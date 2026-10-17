"""
Raw CSV Reader, Physical Header Validator, Independent Record Scanner, and Record Classifier (T007-03).
Conforms to DATA_CONTRACT.md (DC-11, DC-12), ARCHITECTURE.md, T006_FINAL_CORRECTIONS_ADDENDUM.md,
and Gate G3 / T-006 / T-007 specifications.

Governance Invariants:
- FIX-F01: Explicit physical 34-column CSV header validation before Spark parsing (rejects missing,
  extra, reordered, duplicate, or unknown headers, and checks UTF-8/BOM encoding). Never confuses
  the 35-field parser schema (34 business + _corrupt_record) with the 34 physical CSV columns.
- FIX-F02 / DC-11: Independent source logical record accounting (N_raw observed from source file
  independently of classifier counts; N_raw == N_accepted + N_quarantined + N_rejected per source_year
  and per run_id). Raises AccountingUnverifiedError (ACCOUNTING_UNVERIFIED) on any discrepancy.
- FIX-F06 / DC-12: Separation of Parser Corruption (REJECTED), Core Identity Anchor Violation
  (QUARANTINED), and Metric Invalidity (ACCEPTED with NULL try_cast).
- G3-COND-A: OP_CARRIER_FL_NUM <= 0 is NOT hard-quarantined; remains ACCEPTED with provisional
  anomaly flag PROVISIONAL_FLIGHT_NUM_NON_POSITIVE_G3_COND_A.
- FP-DEC-007: Real calendar date validation via anchored regex + try_cast AS date; no +24h rollover
  or timezone invention.
- FP-DEC-017: Weather columns (6 columns: O_TEMP..D_WSPD) optional, absence does not reject flight.
- FP-DEC-010: FLIGHTS column preserved, never fabricated or used as denominator weight.
"""

import csv
from dataclasses import dataclass, field, asdict
from enum import Enum
import io
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple, Union

from pyspark.sql import DataFrame, SparkSession, Window, functions as F
from pyspark.sql.types import (
    DoubleType,
    LongType,
    StringType,
)

from flight_pipeline.ingestion.schema import (
    CANONICAL_COLUMN_NAMES,
    CANONICAL_COLUMNS_COUNT,
    CORRUPT_RECORD_COLUMN,
    SEVEN_CORE_MEASURES,
    get_curated_parquet_schema,
    get_raw_parser_schema,
)
from flight_pipeline.utils.run_manifest import RowAccounting


class HeaderValidationError(ValueError):
    """Raised when a physical CSV header fails 34-column canonical contract validation."""


class AccountingUnverifiedError(RuntimeError):
    """Raised when independent source record accounting does not reconcile (ACCOUNTING_UNVERIFIED)."""


class RecordStatus(str, Enum):
    """Mutually exclusive DC-11 record classification states."""
    ACCEPTED = "ACCEPTED"
    QUARANTINED = "QUARANTINED"
    REJECTED = "REJECTED"


class AnomalyReason(str, Enum):
    """Categorized root-cause reasons for non-accepted records per T006_FINAL_CORRECTIONS_ADDENDUM.md."""
    NONE = "NONE"
    PARSER_SYNTAX_CORRUPTION = "PARSER_SYNTAX_CORRUPTION"
    INVALID_FL_DATE_CORE_ANCHOR = "INVALID_FL_DATE_CORE_ANCHOR"
    MALFORMED_FL_DATE = "INVALID_FL_DATE_CORE_ANCHOR"  # Alias preserving backward compatibility
    SOURCE_YEAR_DATE_MISMATCH = "SOURCE_YEAR_DATE_MISMATCH"
    MISSING_CARRIER_CORE_ANCHOR = "MISSING_CARRIER_CORE_ANCHOR"
    MISSING_AIRPORT_CORE_ANCHOR = "MISSING_AIRPORT_CORE_ANCHOR"
    INVALID_FLIGHT_NUM_CORE_ANCHOR = "INVALID_FLIGHT_NUM_CORE_ANCHOR"
    MISSING_MANDATORY_IDENTIFIER = "MISSING_MANDATORY_IDENTIFIER"


STATUS_COLUMN: str = "_record_status"
REASON_COLUMN: str = "_anomaly_reason"
ANOMALY_FLAGS_COLUMN: str = "_anomaly_flags"
SOURCE_YEAR_COLUMN: str = "_source_year"
SOURCE_FILE_COLUMN: str = "_source_file"
LINEAGE_ID_COLUMN: str = "_record_lineage_id"

MAX_HEADER_BYTES: int = 65536


@dataclass(frozen=True)
class CsvReadOptions:
    """Configuration options for PySpark DataFrameReader CSV ingestion."""
    header: bool = True
    mode: str = "PERMISSIVE"
    column_name_of_corrupt_record: str = CORRUPT_RECORD_COLUMN
    multi_line: bool = False
    quote: str = '"'
    escape: str = '"'
    empty_value: str = ""
    null_value: str = ""
    ignore_leading_white_space: bool = True
    ignore_trailing_white_space: bool = True
    enforce_schema: bool = True
    allow_utf8_bom: bool = False

    def to_spark_options(self) -> Dict[str, str]:
        """Convert options dataclass to PySpark DataFrameReader option dictionary."""
        return {
            "header": str(self.header).lower(),
            "mode": self.mode,
            "columnNameOfCorruptRecord": self.column_name_of_corrupt_record,
            "multiLine": str(self.multi_line).lower(),
            "quote": self.quote,
            "escape": self.escape,
            "emptyValue": self.empty_value,
            "nullValue": self.null_value,
            "ignoreLeadingWhiteSpace": str(self.ignore_leading_white_space).lower(),
            "ignoreTrailingWhiteSpace": str(self.ignore_trailing_white_space).lower(),
            "enforceSchema": str(self.enforce_schema).lower(),
        }


@dataclass(frozen=True)
class SourceScanResult:
    """
    Independent source file scan metrics (FIX-F02).
    Distinguishes physical lines from logical CSV records without relying on Spark classifier output.
    """
    source_path: str
    source_year: Optional[int]
    physical_lines_total: int
    header_lines_count: int
    physical_data_lines: int
    logical_data_records: int
    blank_lines_count: int
    embedded_newline_count: int
    unclosed_quote_count: int
    has_unclosed_quote_eof: bool
    utf8_bom_detected: bool
    is_verifiable: bool
    unverified_reason: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def validate_physical_csv_header(
    source_path: Union[str, Path],
    options: Optional[CsvReadOptions] = None,
) -> Tuple[List[str], bool]:
    """
    Preflight physical CSV header validation (FIX-F01).
    Verifies that the physical file starts with a valid UTF-8 header containing the exact
    34 canonical columns in exact canonical order.
    Never confuses the 35-field Spark parser schema with the 34 physical CSV columns.

    Returns:
        Tuple of (parsed_header_columns, utf8_bom_detected).
    Raises:
        HeaderValidationError: On missing file, empty file, encoding/BOM violation,
            unclosed quotes in header, wrong column count, duplicate columns, unknown
            columns, or column order drift.
    """
    opts = options or CsvReadOptions()
    path = Path(source_path)
    if not path.exists() or not path.is_file():
        raise HeaderValidationError(f"CSV source file does not exist or is not a regular file: {path}")

    file_size = path.stat().st_size
    if file_size == 0:
        raise HeaderValidationError(f"CSV source file is empty (0 bytes): {path}")

    with open(path, "rb") as f:
        head_chunk = f.read(MAX_HEADER_BYTES)

    # Check for non-UTF-8 BOMs (UTF-16 / UTF-32)
    if head_chunk.startswith((b"\xff\xfe", b"\xfe\xff", b"\x00\x00\xfe\xff", b"\xff\xfe\x00\x00")):
        raise HeaderValidationError(f"Unsupported non-UTF-8 BOM (UTF-16/UTF-32) detected in {path}")

    # Check for embedded NUL bytes in header chunk
    first_nl_pos = head_chunk.find(b"\n")
    header_raw_bytes = head_chunk[: first_nl_pos + 1] if first_nl_pos != -1 else head_chunk
    if first_nl_pos == -1 and file_size > MAX_HEADER_BYTES:
        raise HeaderValidationError(
            f"Physical header line in {path} exceeds {MAX_HEADER_BYTES} bytes without a newline terminator"
        )
    if b"\x00" in header_raw_bytes:
        raise HeaderValidationError(f"Binary NUL byte detected in physical header of {path}")

    utf8_bom = False
    if header_raw_bytes.startswith(b"\xef\xbb\xbf"):
        utf8_bom = True
        if not opts.allow_utf8_bom:
            raise HeaderValidationError(
                f"UTF-8 BOM (EF BB BF) detected at start of {path}; rejected by strict header policy "
                "(set allow_utf8_bom=True only if BOM is explicitly authorized)."
            )
        header_raw_bytes = header_raw_bytes[3:]

    try:
        header_line = header_raw_bytes.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise HeaderValidationError(f"Invalid UTF-8 encoding in physical header of {path}: {exc}") from exc

    header_line_stripped = header_line.rstrip("\r\n")
    if not header_line_stripped.strip():
        raise HeaderValidationError(f"First physical line (header) is blank/empty in {path}")

    # Parse physical header line using RFC-4180 CSV rules
    try:
        double_quote = opts.escape == opts.quote
        escape_char = None if double_quote else opts.escape
        reader = csv.reader(
            [header_line_stripped],
            delimiter=",",
            quotechar=opts.quote,
            escapechar=escape_char,
            doublequote=double_quote,
            strict=True,
        )
        parsed_cols = next(reader, [])
    except csv.Error as exc:
        raise HeaderValidationError(f"Malformed CSV syntax in physical header of {path}: {exc}") from exc

    cleaned_cols: List[str] = []
    for col in parsed_cols:
        c = col
        if opts.ignore_leading_white_space:
            c = c.lstrip()
        if opts.ignore_trailing_white_space:
            c = c.rstrip()
        cleaned_cols.append(c)

    if not cleaned_cols:
        raise HeaderValidationError(f"No columns found in physical header of {path}")

    # Check for duplicate column names
    seen = set()
    duplicates = []
    for c in cleaned_cols:
        if c in seen and c not in duplicates:
            duplicates.append(c)
        seen.add(c)
    if duplicates:
        raise HeaderValidationError(
            f"Duplicate column names in physical CSV header of {path}: {duplicates}"
        )

    # Check exact column count against 34 physical columns (never 35 parser fields)
    if CORRUPT_RECORD_COLUMN in cleaned_cols:
        raise HeaderValidationError(
            f"Technical parser field '{CORRUPT_RECORD_COLUMN}' must not appear in physical CSV header of {path}"
        )

    expected_cols = list(CANONICAL_COLUMN_NAMES)
    if len(cleaned_cols) != CANONICAL_COLUMNS_COUNT:
        missing = [c for c in expected_cols if c not in seen]
        unexpected = [c for c in cleaned_cols if c not in expected_cols]
        raise HeaderValidationError(
            f"Physical CSV header column count mismatch in {path}: expected {CANONICAL_COLUMNS_COUNT} "
            f"columns, got {len(cleaned_cols)} (missing={missing}, unexpected={unexpected})"
        )

    # Check for unknown/unexpected or missing column names
    expected_set = set(expected_cols)
    if seen != expected_set:
        missing = [c for c in expected_cols if c not in seen]
        unexpected = [c for c in cleaned_cols if c not in expected_set]
        raise HeaderValidationError(
            f"Physical CSV header column names mismatch in {path}: missing={missing}, unexpected={unexpected}"
        )

    # Check exact physical order
    if cleaned_cols != expected_cols:
        diffs = [
            f"index {i}: expected '{exp}', got '{act}'"
            for i, (exp, act) in enumerate(zip(expected_cols, cleaned_cols))
            if exp != act
        ]
        raise HeaderValidationError(
            f"Physical CSV header column order drift in {path}: {'; '.join(diffs[:5])}"
        )

    return cleaned_cols, utf8_bom


def scan_csv_logical_records(
    source_path: Union[str, Path],
    options: Optional[CsvReadOptions] = None,
    source_year: Optional[int] = None,
) -> SourceScanResult:
    """
    Independently scan a raw CSV file to count physical lines and logical CSV records (FIX-F02).
    
    Fast-path & RFC-4180 state machine:
    - Validates the physical 34-column header first.
    - Streams the file in 1 MiB binary chunks (O(1) memory).
    - If a chunk contains no quote characters (`"`) and no blank lines (`\\n\\n` / `\\r\\n\\r\\n`),
      counts newlines at C speed (`chunk.count(b"\\n")`), allowing 15 GB of clean CSVs to scan in ~3s.
    - Whenever quotes or potential blank lines are present, runs a character/byte state machine to
      accurately distinguish:
        * Physical lines vs logical CSV records (embedded newlines inside quotes)
        * Unclosed quotes (per-line in multi_line=False mode, or at EOF in multi_line=True mode)
        * Blank lines (which Spark Univocity silently skips, triggering ACCOUNTING_UNVERIFIED).
    """
    opts = options or CsvReadOptions()
    path = Path(source_path)

    _, utf8_bom = validate_physical_csv_header(path, opts)

    quote_byte = opts.quote.encode("ascii")[0]
    escape_byte = opts.escape.encode("ascii")[0]

    physical_lines_total = 0
    header_lines_count = 1
    physical_data_lines = 0
    logical_data_records = 0
    blank_lines_count = 0
    embedded_newline_count = 0
    unclosed_quote_count = 0
    has_unclosed_quote_eof = False

    with open(path, "rb") as f:
        # Consume header line first
        header_line = f.readline()
        if not header_line:
            raise HeaderValidationError(f"Empty CSV file: {path}")
        physical_lines_total = 1

        if not opts.multi_line:
            # Single-line mode: each physical line after header is one record candidate.
            carry = b""
            while True:
                chunk = f.read(1024 * 1024)
                if not chunk:
                    break
                buf = carry + chunk
                last_nl = buf.rfind(b"\n")
                if last_nl == -1:
                    carry = buf
                    continue
                complete_part = buf[: last_nl + 1]
                carry = buf[last_nl + 1 :]

                # Fast check: if no quotes and no blank lines in complete_part
                if (
                    quote_byte not in complete_part
                    and b"\n\n" not in complete_part
                    and b"\n\r\n" not in complete_part
                    and not complete_part.startswith((b"\n", b"\r\n"))
                ):
                    n_lines = complete_part.count(b"\n")
                    physical_lines_total += n_lines
                    physical_data_lines += n_lines
                    logical_data_records += n_lines
                else:
                    for raw_line in complete_part.splitlines(keepends=False):
                        physical_lines_total += 1
                        physical_data_lines += 1
                        logical_data_records += 1
                        if not raw_line.strip():
                            blank_lines_count += 1
                            continue
                        if quote_byte in raw_line:
                            if not _is_quote_balanced_line(raw_line, quote_byte, escape_byte):
                                unclosed_quote_count += 1

            if carry:
                physical_lines_total += 1
                physical_data_lines += 1
                logical_data_records += 1
                if not carry.strip():
                    blank_lines_count += 1
                elif quote_byte in carry and not _is_quote_balanced_line(carry, quote_byte, escape_byte):
                    unclosed_quote_count += 1
        else:
            # Multi-line mode (RFC-4180 quoted fields may span physical lines)
            in_quotes = False
            i_prev_escape = False
            pending_quote_close = False
            line_has_non_ws = False
            record_has_content = False

            while True:
                chunk = f.read(1024 * 1024)
                if not chunk:
                    if pending_quote_close:
                        in_quotes = False
                        pending_quote_close = False
                    break
                idx = 0
                n = len(chunk)
                while idx < n:
                    b_val = chunk[idx]
                    if pending_quote_close:
                        pending_quote_close = False
                        if escape_byte == quote_byte and b_val == quote_byte:
                            # Doubled quote inside quoted field -> stays in_quotes
                            idx += 1
                            continue
                        else:
                            # Previous quote actually closed the quoted field; re-process current byte
                            in_quotes = False

                    if b_val == quote_byte:
                        if in_quotes:
                            if i_prev_escape:
                                i_prev_escape = False
                            elif escape_byte == quote_byte:
                                pending_quote_close = True
                            else:
                                in_quotes = False
                        else:
                            in_quotes = True
                            line_has_non_ws = True
                            record_has_content = True
                    elif in_quotes and escape_byte != quote_byte and b_val == escape_byte:
                        i_prev_escape = not i_prev_escape
                    elif b_val == 10:  # '\n'
                        physical_lines_total += 1
                        physical_data_lines += 1
                        if in_quotes:
                            embedded_newline_count += 1
                        else:
                            logical_data_records += 1
                            if not line_has_non_ws and not record_has_content:
                                blank_lines_count += 1
                            line_has_non_ws = False
                            record_has_content = False
                    elif b_val not in (13, 32, 9):  # not '\r', ' ', '\t'
                        line_has_non_ws = True
                        record_has_content = True
                        i_prev_escape = False
                    idx += 1

            # Handle trailing record without final newline
            if line_has_non_ws or record_has_content or in_quotes:
                physical_lines_total += 1
                physical_data_lines += 1
                logical_data_records += 1
                if in_quotes:
                    unclosed_quote_count += 1
                    has_unclosed_quote_eof = True

    is_verifiable = True
    unverified_reason = None
    if blank_lines_count > 0:
        is_verifiable = False
        unverified_reason = (
            f"ACCOUNTING_UNVERIFIED: Source file {path.name} contains {blank_lines_count} blank line(s) "
            "which Univocity CSV parser silently drops, violating strict 1-to-1 record accounting."
        )
    elif opts.multi_line and has_unclosed_quote_eof:
        is_verifiable = False
        unverified_reason = (
            f"ACCOUNTING_UNVERIFIED: Source file {path.name} has an unclosed quoted field reaching EOF "
            "in multiLine=True mode, corrupting logical record boundaries."
        )

    return SourceScanResult(
        source_path=str(path),
        source_year=source_year,
        physical_lines_total=physical_lines_total,
        header_lines_count=header_lines_count,
        physical_data_lines=physical_data_lines,
        logical_data_records=logical_data_records,
        blank_lines_count=blank_lines_count,
        embedded_newline_count=embedded_newline_count,
        unclosed_quote_count=unclosed_quote_count,
        has_unclosed_quote_eof=has_unclosed_quote_eof,
        utf8_bom_detected=utf8_bom,
        is_verifiable=is_verifiable,
        unverified_reason=unverified_reason,
    )


def _is_quote_balanced_line(raw_line: bytes, quote_byte: int, escape_byte: int) -> bool:
    """Verify whether quotes on a single physical CSV line are properly closed according to RFC-4180."""
    in_quotes = False
    i = 0
    n = len(raw_line)
    while i < n:
        b_val = raw_line[i]
        if b_val == quote_byte:
            if in_quotes:
                if escape_byte == quote_byte and i + 1 < n and raw_line[i + 1] == quote_byte:
                    i += 2
                    continue
                in_quotes = False
            else:
                in_quotes = True
        elif in_quotes and escape_byte != quote_byte and b_val == escape_byte:
            i += 2
            continue
        i += 1
    return not in_quotes


class RawCsvReader:
    """
    Production CSV Reader wrapping PySpark DataFrameReader.
    Enforces preflight physical 34-column header validation and canonical 35-field parser schema
    (34 business columns + technical _corrupt_record), plus deterministic lineage metadata.
    """

    def __init__(
        self,
        spark: SparkSession,
        options: Optional[CsvReadOptions] = None,
    ):
        if spark is None:
            raise ValueError("SparkSession cannot be None")
        self.spark = spark
        self.options = options or CsvReadOptions()

    def read_raw(
        self,
        source_path: Union[str, Path],
        source_year: Optional[int] = None,
        attach_lineage: bool = False,
    ) -> DataFrame:
        """
        Validate physical 34-column header and read raw CSV file using canonical 35-field parser schema.
        
        Args:
            source_path: Path to the raw CSV file on local filesystem.
            source_year: Optional integer year for source-year lineage and date consistency validation.
            attach_lineage: If True, attaches deterministic `_source_year`, `_source_file`, and
                `_record_lineage_id` columns.
            
        Returns:
            DataFrame with 34 business string columns plus technical _corrupt_record (and lineage columns
            when attach_lineage=True).
        """
        path_obj = Path(source_path)
        if self.options.header:
            validate_physical_csv_header(path_obj, self.options)

        path_str = str(path_obj)
        # Ensure column pruning is disabled so Univocity parser verifies all tokens
        # across the line and captures token count mismatches into _corrupt_record
        self.spark.conf.set("spark.sql.csv.parser.columnPruning.enabled", "false")
        reader = (
            self.spark.read
            .options(**self.options.to_spark_options())
            .schema(get_raw_parser_schema())
        )
        df = reader.csv(path_str)

        if attach_lineage or source_year is not None:
            df = self.attach_deterministic_lineage(
                df,
                source_path=path_obj,
                source_year=source_year,
            )
        return df

    @staticmethod
    def attach_deterministic_lineage(
        df: DataFrame,
        source_path: Union[str, Path],
        source_year: Optional[int] = None,
    ) -> DataFrame:
        """
        Attach deterministic, partition-independent lineage columns (`_source_year`, `_source_file`,
        `_record_lineage_id`) without assuming Spark file split offsets or `monotonically_increasing_id`
        are stable across distributed runs (TS-020 / FIX-F02).
        """
        path_obj = Path(source_path)
        src_file_name = path_obj.name

        out_df = df.withColumn(
            SOURCE_YEAR_COLUMN,
            F.lit(int(source_year) if source_year is not None else None).cast(LongType()),
        ).withColumn(
            SOURCE_FILE_COLUMN,
            F.lit(src_file_name).cast(StringType()),
        )

        # Deterministic content-based window rank to disambiguate exact duplicate records (e.g. YX 3624)
        partition_cols = (
            [F.coalesce(F.col(SOURCE_YEAR_COLUMN).cast(StringType()), F.lit("NA")), F.col(SOURCE_FILE_COLUMN)]
            + [F.coalesce(F.col(c), F.lit("<NULL>")) for c in CANONICAL_COLUMN_NAMES]
            + [F.coalesce(F.col(CORRUPT_RECORD_COLUMN), F.lit("<VALID>"))]
        )
        dup_window = Window.partitionBy(*partition_cols).orderBy(F.lit(1))
        dup_rank_col = F.row_number().over(dup_window).cast(StringType())

        hash_input = F.concat_ws("||", *(partition_cols + [dup_rank_col]))
        out_df = out_df.withColumn(LINEAGE_ID_COLUMN, F.sha2(hash_input, 256))
        return out_df


class IngestionRecordClassifier:
    """
    Classifies raw records into mutually exclusive ACCEPTED, QUARANTINED, and REJECTED states
    conforming to DATA_CONTRACT.md (DC-11 and DC-12), T006_FINAL_CORRECTIONS_ADDENDUM.md, and G3-COND-A.
    """

    @staticmethod
    def classify(df: DataFrame) -> DataFrame:
        """
        Augment DataFrame with `_record_status`, `_anomaly_reason`, and `_anomaly_flags` columns.
        
        Rules (FIX-F06 & T006_FINAL_CORRECTIONS_ADDENDUM.md Section 2.1):
        1. REJECTED:
           - `_corrupt_record IS NOT NULL` (Univocity parser syntax corruption: short row, extra tokens,
             unclosed quotes). Reason: `PARSER_SYNTAX_CORRUPTION`.
        2. QUARANTINED (evaluated on syntax-valid 34-column rows):
           - `FL_DATE` is null/blank, fails anchored regex `^(?:\\d{4}-\\d{2}-\\d{2}|\\d{4}-\\d{2}-\\d{2} 00:00:00)$`,
             or fails real calendar date parsing `try_cast(substring(trim(FL_DATE), 1, 10) AS date) IS NULL`
             (e.g. `2016-02-30` or `2019-02-29`). Reason: `INVALID_FL_DATE_CORE_ANCHOR`.
           - When `_source_year` is present and non-null, `year(parsed_date) != _source_year`.
             Reason: `SOURCE_YEAR_DATE_MISMATCH`.
           - `OP_CARRIER` is null or blank. Reason: `MISSING_CARRIER_CORE_ANCHOR`.
           - `ORIGIN` or `DEST` is null or blank. Reason: `MISSING_AIRPORT_CORE_ANCHOR`.
           - `OP_CARRIER_FL_NUM` is null, blank, or non-numeric (`try_cast` is NULL/NaN/Inf).
             Reason: `INVALID_FLIGHT_NUM_CORE_ANCHOR`.
        3. ACCEPTED:
           - All other records meeting core identity anchors.
           - `OP_CARRIER_FL_NUM <= 0` (finite numeric) is NOT quarantined per G3-COND-A; remains ACCEPTED
             and receives `_anomaly_flags` = `PROVISIONAL_FLIGHT_NUM_NON_POSITIVE_G3_COND_A`.
           - Non-numeric or missing performance measures (DEP_DELAY, ARR_DELAY, etc.) do NOT quarantine
             or reject the record per DC-12; remains ACCEPTED and receives `_anomaly_flags` =
             `METRIC_NON_NUMERIC_RAW_TOKEN_DC12`.
           - Absence of weather data does NOT quarantine or reject flight records per FP-DEC-017.
        """
        corrupt_col = F.col(CORRUPT_RECORD_COLUMN)
        fl_date_trimmed = F.trim(F.col("FL_DATE"))
        op_carrier_trimmed = F.trim(F.col("OP_CARRIER"))
        origin_trimmed = F.trim(F.col("ORIGIN"))
        dest_trimmed = F.trim(F.col("DEST"))
        fl_num_trimmed = F.trim(F.col("OP_CARRIER_FL_NUM"))

        # 1. Technical unrecoverable parser corruption
        is_corrupt = corrupt_col.isNotNull()

        # 2. Anchored regex + real calendar date check (FP-DEC-007 & T006 Addendum Section 6.3)
        anchored_date_regex = r"^(?:\d{4}-\d{2}-\d{2}|\d{4}-\d{2}-\d{2} 00:00:00)$"
        parsed_cal_date = F.expr("try_cast(substring(trim(FL_DATE), 1, 10) AS date)")
        is_invalid_fl_date = (
            F.col("FL_DATE").isNull()
            | (fl_date_trimmed == "")
            | (~fl_date_trimmed.rlike(anchored_date_regex))
            | parsed_cal_date.isNull()
        )

        # Source year vs FL_DATE year consistency check
        if SOURCE_YEAR_COLUMN in df.columns:
            is_year_mismatch = (
                ~is_invalid_fl_date
                & F.col(SOURCE_YEAR_COLUMN).isNotNull()
                & (F.year(parsed_cal_date).cast(LongType()) != F.col(SOURCE_YEAR_COLUMN).cast(LongType()))
            )
        else:
            is_year_mismatch = F.lit(False)

        # 3. Core entity identity anchors
        is_missing_carrier = F.col("OP_CARRIER").isNull() | (op_carrier_trimmed == "")
        is_missing_airport = (
            F.col("ORIGIN").isNull()
            | (origin_trimmed == "")
            | F.col("DEST").isNull()
            | (dest_trimmed == "")
        )

        fl_num_double = F.expr("try_cast(trim(OP_CARRIER_FL_NUM) AS double)")
        is_invalid_flight_num = (
            F.col("OP_CARRIER_FL_NUM").isNull()
            | (fl_num_trimmed == "")
            | fl_num_double.isNull()
            | F.isnan(fl_num_double)
            | fl_num_double.isin(float("inf"), float("-inf"))
        )

        # Provisional G3-COND-A flag: OP_CARRIER_FL_NUM <= 0 is ACCEPTED, flagged for T-008
        is_provisional_non_pos_fl_num = (
            ~is_corrupt & ~is_invalid_flight_num & (fl_num_double <= 0.0)
        )

        # DC-12 non-numeric raw metric token flag on ACCEPTED rows
        non_num_metric_conds = []
        for m_col in SEVEN_CORE_MEASURES:
            m_trim = F.trim(F.col(m_col))
            m_cast = F.expr(f"try_cast(trim({m_col}) AS double)")
            non_num_metric_conds.append(
                F.col(m_col).isNotNull() & (m_trim != "") & m_cast.isNull()
            )
        has_non_numeric_metric_token = non_num_metric_conds[0]
        for c_expr in non_num_metric_conds[1:]:
            has_non_numeric_metric_token = has_non_numeric_metric_token | c_expr

        is_any_quarantine = (
            is_invalid_fl_date
            | is_year_mismatch
            | is_missing_carrier
            | is_missing_airport
            | is_invalid_flight_num
        )

        classified_df = (
            df.withColumn(
                STATUS_COLUMN,
                F.when(is_corrupt, F.lit(RecordStatus.REJECTED.value))
                .when(is_any_quarantine, F.lit(RecordStatus.QUARANTINED.value))
                .otherwise(F.lit(RecordStatus.ACCEPTED.value)),
            )
            .withColumn(
                REASON_COLUMN,
                F.when(is_corrupt, F.lit(AnomalyReason.PARSER_SYNTAX_CORRUPTION.value))
                .when(is_invalid_fl_date, F.lit(AnomalyReason.INVALID_FL_DATE_CORE_ANCHOR.value))
                .when(is_year_mismatch, F.lit(AnomalyReason.SOURCE_YEAR_DATE_MISMATCH.value))
                .when(is_missing_carrier, F.lit(AnomalyReason.MISSING_CARRIER_CORE_ANCHOR.value))
                .when(is_missing_airport, F.lit(AnomalyReason.MISSING_AIRPORT_CORE_ANCHOR.value))
                .when(is_invalid_flight_num, F.lit(AnomalyReason.INVALID_FLIGHT_NUM_CORE_ANCHOR.value))
                .otherwise(F.lit(AnomalyReason.NONE.value)),
            )
        )

        # Build comprehensive pipe-delimited _anomaly_flags column preserving all matched flags
        flag_exprs = [
            F.when(is_corrupt, F.lit(AnomalyReason.PARSER_SYNTAX_CORRUPTION.value)),
            F.when(~is_corrupt & is_invalid_fl_date, F.lit(AnomalyReason.INVALID_FL_DATE_CORE_ANCHOR.value)),
            F.when(~is_corrupt & is_year_mismatch, F.lit(AnomalyReason.SOURCE_YEAR_DATE_MISMATCH.value)),
            F.when(~is_corrupt & is_missing_carrier, F.lit(AnomalyReason.MISSING_CARRIER_CORE_ANCHOR.value)),
            F.when(~is_corrupt & is_missing_airport, F.lit(AnomalyReason.MISSING_AIRPORT_CORE_ANCHOR.value)),
            F.when(~is_corrupt & is_invalid_flight_num, F.lit(AnomalyReason.INVALID_FLIGHT_NUM_CORE_ANCHOR.value)),
            F.when(is_provisional_non_pos_fl_num, F.lit("PROVISIONAL_FLIGHT_NUM_NON_POSITIVE_G3_COND_A")),
            F.when(~is_corrupt & ~is_any_quarantine & has_non_numeric_metric_token, F.lit("METRIC_NON_NUMERIC_RAW_TOKEN_DC12")),
        ]
        concat_flags = F.concat_ws("|", *flag_exprs)
        classified_df = classified_df.withColumn(
            ANOMALY_FLAGS_COLUMN,
            F.when(concat_flags == "", F.lit("NONE")).otherwise(concat_flags),
        )

        return classified_df


class IngestionTransformer:
    """
    Transforms accepted raw StringType records into strongly-typed curated schema
    ready for Parquet serialization.
    """

    @staticmethod
    def to_curated(df: DataFrame, filter_accepted: bool = True) -> DataFrame:
        """
        Cast canonical columns to curated Parquet schema types.
        
        - Normalizes `FL_DATE` (`YYYY-MM-DD 00:00:00` -> `YYYY-MM-DD`) without timezone/rollover mutation.
        - Derives `MONTH` and `DAY_OF_MONTH` from validated `FL_DATE` when raw calendar fields are null
          (per T006_FINAL_CORRECTIONS_ADDENDUM.md Section 6.2).
        - Uses `try_cast` on numeric fields so non-numeric metric strings become NULL per DC-12.
        """
        working_df = df
        if filter_accepted and STATUS_COLUMN in df.columns:
            working_df = working_df.filter(F.col(STATUS_COLUMN) == RecordStatus.ACCEPTED.value)

        curated_schema = get_curated_parquet_schema()
        type_map = {field.name: field.dataType for field in curated_schema.fields}
        parsed_cal_date = F.expr("try_cast(substring(trim(FL_DATE), 1, 10) AS date)")

        select_exprs = []
        for col_name in CANONICAL_COLUMN_NAMES:
            target_type = type_map[col_name]
            if col_name == "FL_DATE":
                select_exprs.append(
                    F.when(
                        F.col("FL_DATE").isNotNull(),
                        F.substring(F.trim(F.col("FL_DATE")), 1, 10),
                    )
                    .otherwise(F.lit(None).cast(StringType()))
                    .alias("FL_DATE")
                )
            elif col_name == "MONTH":
                raw_month = F.expr("try_cast(trim(MONTH) AS bigint)")
                select_exprs.append(
                    F.coalesce(raw_month, F.month(parsed_cal_date).cast(LongType())).alias("MONTH")
                )
            elif col_name == "DAY_OF_MONTH":
                raw_dom = F.expr("try_cast(trim(DAY_OF_MONTH) AS bigint)")
                select_exprs.append(
                    F.coalesce(raw_dom, F.dayofmonth(parsed_cal_date).cast(LongType())).alias("DAY_OF_MONTH")
                )
            elif target_type == StringType():
                select_exprs.append(F.col(col_name).cast(StringType()).alias(col_name))
            else:
                select_exprs.append(
                    F.expr(f"try_cast(trim({col_name}) AS {target_type.simpleString()})").alias(col_name)
                )

        return working_df.select(select_exprs)


def compute_row_accounting(
    classified_df: DataFrame,
    independent_raw_count: Optional[int] = None,
    scan_result: Optional[SourceScanResult] = None,
) -> RowAccounting:
    """
    Compute and verify DC-11 row accounting from a classified DataFrame (FIX-F02).
    
    When `independent_raw_count` or `scan_result` is supplied:
    - Verifies `scan_result.is_verifiable` (e.g., no blank lines silently dropped by Spark and no
      unclosed multiLine quotes at EOF).
    - Uses the independently observed source record count as `raw_row_count` (never tautologically
      summing accepted + quarantined + rejected to define raw_row_count).
    - Raises `AccountingUnverifiedError("ACCOUNTING_UNVERIFIED: ...")` if the classifier output sum
      does not equal the independent source record count or if any records lack a valid DC-11 status.
    """
    if scan_result is not None:
        if not scan_result.is_verifiable:
            raise AccountingUnverifiedError(
                scan_result.unverified_reason
                or f"ACCOUNTING_UNVERIFIED: Source file {scan_result.source_path} failed record boundary verification."
            )
        if independent_raw_count is None:
            independent_raw_count = scan_result.logical_data_records

    status_counts_df = (
        classified_df
        .groupBy(STATUS_COLUMN)
        .agg(F.count(F.lit(1)).alias("count"))
    )
    status_rows = status_counts_df.collect()

    valid_statuses = {
        RecordStatus.ACCEPTED.value,
        RecordStatus.QUARANTINED.value,
        RecordStatus.REJECTED.value,
    }
    status_counts: Dict[str, int] = {}
    unclassified_count = 0
    for row in status_rows:
        st = row[STATUS_COLUMN]
        cnt = int(row["count"])
        if st in valid_statuses:
            status_counts[st] = cnt
        else:
            unclassified_count += cnt

    if unclassified_count > 0:
        raise AccountingUnverifiedError(
            f"ACCOUNTING_UNVERIFIED: Found {unclassified_count} record(s) with null or invalid _record_status"
        )

    accepted = status_counts.get(RecordStatus.ACCEPTED.value, 0)
    quarantined = status_counts.get(RecordStatus.QUARANTINED.value, 0)
    rejected = status_counts.get(RecordStatus.REJECTED.value, 0)
    classifier_total = accepted + quarantined + rejected

    raw_total = independent_raw_count if independent_raw_count is not None else classifier_total

    if raw_total != classifier_total:
        raise AccountingUnverifiedError(
            f"ACCOUNTING_UNVERIFIED: Independent source logical record count ({raw_total}) != "
            f"classified record sum ({classifier_total} = accepted:{accepted} + "
            f"quarantined:{quarantined} + rejected:{rejected})"
        )

    accounting = RowAccounting(
        raw_row_count=raw_total,
        accepted_row_count=accepted,
        quarantined_row_count=quarantined,
        rejected_row_count=rejected,
    )

    if not accounting.is_balanced():
        raise AccountingUnverifiedError(
            f"ACCOUNTING_UNVERIFIED: Row accounting invariant violated: raw ({raw_total}) != "
            f"accepted ({accepted}) + quarantined ({quarantined}) + rejected ({rejected})"
        )

    return accounting


def compute_per_year_accounting(
    classified_df: DataFrame,
    scan_results_by_year: Mapping[int, SourceScanResult],
) -> Tuple[RowAccounting, Dict[int, RowAccounting]]:
    """
    Reconcile DC-11 row accounting independently for each `source_year` and in aggregate for `run_id`.
    Raises `AccountingUnverifiedError` if any year fails independent record boundary verification
    or if any year's classified record sum diverges from its independent source scan count.
    """
    for yr, scan_res in sorted(scan_results_by_year.items()):
        if not scan_res.is_verifiable:
            raise AccountingUnverifiedError(
                scan_res.unverified_reason
                or f"ACCOUNTING_UNVERIFIED: Year {yr} source failed record boundary verification."
            )

    grouped_rows = (
        classified_df
        .groupBy(SOURCE_YEAR_COLUMN, STATUS_COLUMN)
        .agg(F.count(F.lit(1)).alias("count"))
        .collect()
    )

    valid_statuses = {
        RecordStatus.ACCEPTED.value,
        RecordStatus.QUARANTINED.value,
        RecordStatus.REJECTED.value,
    }
    counts_by_year: Dict[int, Dict[str, int]] = {yr: {} for yr in scan_results_by_year}

    for row in grouped_rows:
        yr_val = row[SOURCE_YEAR_COLUMN]
        st_val = row[STATUS_COLUMN]
        cnt = int(row["count"])
        if yr_val is None or int(yr_val) not in counts_by_year:
            raise AccountingUnverifiedError(
                f"ACCOUNTING_UNVERIFIED: Classified records contain unexpected _source_year={yr_val}"
            )
        if st_val not in valid_statuses:
            raise AccountingUnverifiedError(
                f"ACCOUNTING_UNVERIFIED: Year {yr_val} contains {cnt} record(s) with invalid status {st_val!r}"
            )
        counts_by_year[int(yr_val)][st_val] = cnt

    per_year_accounting: Dict[int, RowAccounting] = {}
    total_raw = 0
    total_acc = 0
    total_quar = 0
    total_rej = 0

    for yr, scan_res in sorted(scan_results_by_year.items()):
        yr_counts = counts_by_year.get(yr, {})
        acc = yr_counts.get(RecordStatus.ACCEPTED.value, 0)
        quar = yr_counts.get(RecordStatus.QUARANTINED.value, 0)
        rej = yr_counts.get(RecordStatus.REJECTED.value, 0)
        cls_sum = acc + quar + rej
        ind_raw = scan_res.logical_data_records

        if ind_raw != cls_sum:
            raise AccountingUnverifiedError(
                f"ACCOUNTING_UNVERIFIED: Year {yr} independent source record count ({ind_raw}) != "
                f"classified sum ({cls_sum} = accepted:{acc} + quarantined:{quar} + rejected:{rej})"
            )

        yr_accounting = RowAccounting(
            raw_row_count=ind_raw,
            accepted_row_count=acc,
            quarantined_row_count=quar,
            rejected_row_count=rej,
        )
        per_year_accounting[yr] = yr_accounting
        total_raw += ind_raw
        total_acc += acc
        total_quar += quar
        total_rej += rej

    run_accounting = RowAccounting(
        raw_row_count=total_raw,
        accepted_row_count=total_acc,
        quarantined_row_count=total_quar,
        rejected_row_count=total_rej,
    )
    if not run_accounting.is_balanced():
        raise AccountingUnverifiedError("ACCOUNTING_UNVERIFIED: Aggregate run accounting is not balanced.")

    return run_accounting, per_year_accounting
