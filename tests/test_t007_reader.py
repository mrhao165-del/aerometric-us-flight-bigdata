"""
Comprehensive Unit Test Suite for T007-03 Raw CSV Reader, Physical Header Validator,
Independent Logical Record Scanner, and Record Classifier (including FIX-F01, FIX-F02, FIX-F06).

Validates:
1. Valid 34-column CSV parsing and curated schema transformation.
2. Physical 34-column CSV header validation (missing, extra, reordered, duplicate, unknown,
   _corrupt_record in physical header, UTF-8 BOM, UTF-16 BOM, NUL byte).
3. Independent logical record scanning and DC-11 accounting reconciliation (`scan_csv_logical_records`,
   `compute_row_accounting`, `compute_per_year_accounting`), including blank lines and unclosed quotes
   raising `AccountingUnverifiedError` (`ACCOUNTING_UNVERIFIED`).
4. Deterministic content-hash lineage (`_source_year`, `_source_file`, `_record_lineage_id`)
   including disambiguation of exact duplicate rows (e.g., `YX 3624` 2022 pattern).
5. Univocity parser syntax corruption handling (short rows, extra tokens, unclosed quotes -> REJECTED).
6. Real calendar date validation (`2016-02-29` leap year valid, `2016-01-15 00:00:00` normalized,
   `2016-02-30` and `2019-02-29` impossible dates -> QUARANTINED, source year mismatch -> QUARANTINED).
7. Core identity anchor quarantine (`OP_CARRIER`, `ORIGIN`, `DEST`, `OP_CARRIER_FL_NUM`).
8. G3-COND-A compliance: `OP_CARRIER_FL_NUM <= 0` is ACCEPTED with provisional anomaly flag
   `PROVISIONAL_FLIGHT_NUM_NON_POSITIVE_G3_COND_A`.
9. DC-12 metric vs record validity separation (non-numeric delay accepted with flag
   `METRIC_NON_NUMERIC_RAW_TOKEN_DC12`, cast to NULL in curated).
10. FP-DEC-017 compliance: Null weather values (6 columns: O_TEMP..D_WSPD) do NOT reject or quarantine records.
11. FP-DEC-010 compliance: FLIGHTS preserved as float64 without denominator weighting.
"""

from pathlib import Path
import sys
import tempfile
import unittest

SRC_DIR = Path(__file__).resolve().parents[1] / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from pyspark.sql import functions as F
from pyspark.sql.types import DoubleType, LongType

from flight_pipeline.config.spark_config import SparkConfig, get_spark_session, stop_spark_session
from flight_pipeline.ingestion.reader import (
    ANOMALY_FLAGS_COLUMN,
    AccountingUnverifiedError,
    AnomalyReason,
    CsvReadOptions,
    HeaderValidationError,
    IngestionRecordClassifier,
    IngestionTransformer,
    LINEAGE_ID_COLUMN,
    REASON_COLUMN,
    RawCsvReader,
    RecordStatus,
    SOURCE_FILE_COLUMN,
    SOURCE_YEAR_COLUMN,
    STATUS_COLUMN,
    compute_per_year_accounting,
    compute_row_accounting,
    scan_csv_logical_records,
    validate_physical_csv_header,
)
from flight_pipeline.ingestion.schema import (
    CANONICAL_COLUMN_NAMES,
    CANONICAL_COLUMNS_COUNT,
    CORRUPT_RECORD_COLUMN,
)


class TestT007Reader(unittest.TestCase):
    """Test suite for RawCsvReader, header validation, independent accounting, and record classification."""

    @classmethod
    def setUpClass(cls):
        """Initialize isolated local SparkSession."""
        cfg = SparkConfig(app_name="TestT007Reader", master="local[2]", driver_memory="2g", shuffle_partitions=4)
        cls.spark = get_spark_session(cfg)

    @classmethod
    def tearDownClass(cls):
        """Clean up SparkSession."""
        if cls.spark:
            stop_spark_session(cls.spark)

    def _create_synthetic_csv(self, dir_path: Path, rows: list, filename: str = "test_data.csv", header_cols=None) -> Path:
        """Helper to create a CSV with canonical or custom header and specified rows."""
        csv_file = dir_path / filename
        cols = header_cols if header_cols is not None else CANONICAL_COLUMN_NAMES
        header = ",".join(cols)
        lines = [header] + rows
        csv_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return csv_file

    def _make_valid_34_col_row(
        self,
        fl_date: str = "2016-01-01",
        op_carrier: str = "AA",
        fl_num: str = "1234.0",
        origin: str = "JFK",
        dest: str = "LAX",
        dep_delay: str = "10.0",
        arr_delay: str = "-5.0",
        flights: str = "1.0",
        month: str = "1",
        day_of_month: str = "1",
    ) -> str:
        """Generate a valid 34-column CSV line."""
        fields = [
            fl_date,            # FL_DATE
            op_carrier,         # OP_CARRIER
            fl_num,             # OP_CARRIER_FL_NUM
            origin,             # ORIGIN
            dest,               # DEST
            "0800",             # CRS_DEP_TIME
            "0810",             # DEP_TIME
            dep_delay,          # DEP_DELAY
            "15.0",             # TAXI_OUT
            "0825",             # WHEELS_OFF
            "1110",             # WHEELS_ON
            "5.0",              # TAXI_IN
            "1120",             # CRS_ARR_TIME
            "1115",             # ARR_TIME
            arr_delay,          # ARR_DELAY
            360.0,              # CRS_ELAPSED_TIME
            355.0,              # ACTUAL_ELAPSED_TIME
            335.0,              # AIR_TIME
            flights,            # FLIGHTS
            month,              # MONTH
            day_of_month,       # DAY_OF_MONTH
            5,                  # DAY_OF_WEEK
            100,                # ORIGIN_INDEX
            200,                # DEST_INDEX
            15.5,               # O_TEMP
            0.0,                # O_PRCP
            12.0,               # O_WSPD
            22.0,               # D_TEMP
            0.1,                # D_PRCP
            8.0,                # D_WSPD
            40.6413,            # O_LATITUDE
            -73.7781,           # O_LONGITUDE
            33.9416,            # D_LATITUDE
            -118.4085,          # D_LONGITUDE
        ]
        return ",".join(str(f) for f in fields)

    def test_read_valid_34_columns_parses_cleanly(self):
        """RDR-01: Valid 34-column row parses cleanly into 35 fields (34 business + corrupt=None)."""
        with tempfile.TemporaryDirectory() as td:
            row = self._make_valid_34_col_row()
            csv_path = self._create_synthetic_csv(Path(td), [row])

            reader = RawCsvReader(self.spark)
            df = reader.read_raw(csv_path)

            self.assertEqual(len(df.columns), CANONICAL_COLUMNS_COUNT + 1)
            self.assertIn(CORRUPT_RECORD_COLUMN, df.columns)

            records = df.collect()
            self.assertEqual(len(records), 1)
            rec = records[0]

            self.assertEqual(rec["FL_DATE"], "2016-01-01")
            self.assertEqual(rec["OP_CARRIER"], "AA")
            self.assertEqual(rec["OP_CARRIER_FL_NUM"], "1234.0")
            self.assertEqual(rec["DEP_DELAY"], "10.0")
            self.assertEqual(rec["ARR_DELAY"], "-5.0")
            self.assertIsNone(rec[CORRUPT_RECORD_COLUMN])

    def test_short_row_token_mismatch_captured_as_corrupt(self):
        """RDR-02: Short row (< 34 tokens) is captured in _corrupt_record and classified as REJECTED."""
        with tempfile.TemporaryDirectory() as td:
            valid_row = self._make_valid_34_col_row()
            short_row = "2016-01-02,DL,500,ORD,ATL"  # Only 5 tokens
            csv_path = self._create_synthetic_csv(Path(td), [valid_row, short_row])

            scan_res = scan_csv_logical_records(csv_path)
            reader = RawCsvReader(self.spark)
            raw_df = reader.read_raw(csv_path)
            classified_df = IngestionRecordClassifier.classify(raw_df)

            accounting = compute_row_accounting(classified_df, scan_result=scan_res)
            self.assertEqual(accounting.raw_row_count, 2)
            self.assertEqual(accounting.accepted_row_count, 1)
            self.assertEqual(accounting.quarantined_row_count, 0)
            self.assertEqual(accounting.rejected_row_count, 1)
            self.assertTrue(accounting.is_balanced())

            rejected = classified_df.filter(classified_df[STATUS_COLUMN] == RecordStatus.REJECTED.value).collect()
            self.assertEqual(len(rejected), 1)
            self.assertEqual(rejected[0][REASON_COLUMN], AnomalyReason.PARSER_SYNTAX_CORRUPTION.value)

    def test_extra_tokens_captured_as_corrupt(self):
        """RDR-03: Extra tokens (> 34 tokens) captured in _corrupt_record and classified as REJECTED."""
        with tempfile.TemporaryDirectory() as td:
            valid_row = self._make_valid_34_col_row()
            extra_row = self._make_valid_34_col_row() + ",EXTRA_TOKEN_1,EXTRA_TOKEN_2"
            csv_path = self._create_synthetic_csv(Path(td), [valid_row, extra_row])

            scan_res = scan_csv_logical_records(csv_path)
            reader = RawCsvReader(self.spark)
            raw_df = reader.read_raw(csv_path)
            classified_df = IngestionRecordClassifier.classify(raw_df)

            accounting = compute_row_accounting(classified_df, scan_result=scan_res)
            self.assertEqual(accounting.raw_row_count, 2)
            self.assertEqual(accounting.accepted_row_count, 1)
            self.assertEqual(accounting.rejected_row_count, 1)

    def test_dc12_non_numeric_metric_accepted_in_raw_and_null_in_curated(self):
        """RDR-04: Non-numeric metric string is ACCEPTED (DC-12) with flag and cast to NULL in curated schema."""
        with tempfile.TemporaryDirectory() as td:
            row = self._make_valid_34_col_row(dep_delay="CORRUPT_DELAY")
            csv_path = self._create_synthetic_csv(Path(td), [row])

            reader = RawCsvReader(self.spark)
            raw_df = reader.read_raw(csv_path)
            classified_df = IngestionRecordClassifier.classify(raw_df)

            accounting = compute_row_accounting(classified_df, source_path=csv_path)
            self.assertEqual(accounting.raw_row_count, 1)
            self.assertEqual(accounting.accepted_row_count, 1)
            self.assertEqual(accounting.rejected_row_count, 0)

            cls_rec = classified_df.collect()[0]
            self.assertIn("METRIC_NON_NUMERIC_RAW_TOKEN_DC12", cls_rec[ANOMALY_FLAGS_COLUMN])

            curated_df = IngestionTransformer.to_curated(classified_df)
            self.assertEqual(len(curated_df.columns), CANONICAL_COLUMNS_COUNT)
            self.assertEqual(curated_df.schema["DEP_DELAY"].dataType, DoubleType())

            record = curated_df.collect()[0]
            self.assertIsNone(record["DEP_DELAY"])
            self.assertEqual(record["OP_CARRIER"], "AA")

    def test_g3_cond_b_non_positive_flight_num_not_quarantined(self):
        """RDR-05: OP_CARRIER_FL_NUM <= 0 is NOT quarantined per G3-COND-A; remains ACCEPTED with provisional flag."""
        with tempfile.TemporaryDirectory() as td:
            row_zero = self._make_valid_34_col_row(fl_num="0.0")
            row_neg = self._make_valid_34_col_row(fl_num="-100.0")
            csv_path = self._create_synthetic_csv(Path(td), [row_zero, row_neg])

            reader = RawCsvReader(self.spark)
            raw_df = reader.read_raw(csv_path)
            classified_df = IngestionRecordClassifier.classify(raw_df)

            accounting = compute_row_accounting(classified_df, source_path=csv_path)
            self.assertEqual(accounting.raw_row_count, 2)
            self.assertEqual(accounting.accepted_row_count, 2)
            self.assertEqual(accounting.quarantined_row_count, 0)

            rows = classified_df.collect()
            for r in rows:
                self.assertEqual(r[STATUS_COLUMN], RecordStatus.ACCEPTED.value)
                self.assertIn("PROVISIONAL_FLIGHT_NUM_NON_POSITIVE_G3_COND_A", r[ANOMALY_FLAGS_COLUMN])

    def test_malformed_fl_date_quarantined(self):
        """RDR-06: Row with malformed FL_DATE is classified as QUARANTINED."""
        with tempfile.TemporaryDirectory() as td:
            valid_row = self._make_valid_34_col_row()
            bad_date_row = self._make_valid_34_col_row(fl_date="INVALID_DATE_2016")
            csv_path = self._create_synthetic_csv(Path(td), [valid_row, bad_date_row])

            reader = RawCsvReader(self.spark)
            raw_df = reader.read_raw(csv_path)
            classified_df = IngestionRecordClassifier.classify(raw_df)

            accounting = compute_row_accounting(classified_df, source_path=csv_path)
            self.assertEqual(accounting.raw_row_count, 2)
            self.assertEqual(accounting.accepted_row_count, 1)
            self.assertEqual(accounting.quarantined_row_count, 1)
            self.assertEqual(accounting.rejected_row_count, 0)
            self.assertTrue(accounting.is_balanced())

            quarantined = classified_df.filter(classified_df[STATUS_COLUMN] == RecordStatus.QUARANTINED.value).collect()
            self.assertEqual(len(quarantined), 1)
            self.assertEqual(quarantined[0][REASON_COLUMN], AnomalyReason.INVALID_FL_DATE_CORE_ANCHOR.value)

    def test_curated_schema_preserves_canonical_types(self):
        """RDR-07: Curated DataFrame exactly matches canonical 34-column types."""
        with tempfile.TemporaryDirectory() as td:
            row = self._make_valid_34_col_row(fl_num="5432.1", arr_delay="-12.5")
            csv_path = self._create_synthetic_csv(Path(td), [row])

            reader = RawCsvReader(self.spark)
            raw_df = reader.read_raw(csv_path)
            classified_df = IngestionRecordClassifier.classify(raw_df)
            curated_df = IngestionTransformer.to_curated(classified_df)

            self.assertEqual(curated_df.columns, list(CANONICAL_COLUMN_NAMES))

            self.assertEqual(curated_df.schema["OP_CARRIER_FL_NUM"].dataType, DoubleType())
            self.assertEqual(curated_df.schema["FLIGHTS"].dataType, DoubleType())
            self.assertEqual(curated_df.schema["ARR_DELAY"].dataType, DoubleType())
            self.assertEqual(curated_df.schema["MONTH"].dataType, LongType())
            self.assertEqual(curated_df.schema["ORIGIN_INDEX"].dataType, LongType())

            rec = curated_df.collect()[0]
            self.assertEqual(rec["OP_CARRIER_FL_NUM"], 5432.1)
            self.assertEqual(rec["ARR_DELAY"], -12.5)

    def test_quoted_commas_and_embedded_newlines(self):
        """RDR-08: Quoted fields with commas and embedded newlines parse and scan accurately with multi_line=True."""
        with tempfile.TemporaryDirectory() as td:
            opts = CsvReadOptions(multi_line=True)
            reader = RawCsvReader(self.spark, options=opts)

            row1 = self._make_valid_34_col_row(op_carrier='"DELTA, INC"')
            row2 = self._make_valid_34_col_row(op_carrier='"AMERICAN\nAIRLINES"')
            csv_path = self._create_synthetic_csv(Path(td), [row1, row2])

            scan_res = scan_csv_logical_records(csv_path, options=opts, source_year=2016)
            self.assertEqual(scan_res.physical_lines_total, 4)  # 1 header + 1 single-line + 2 physical lines for row2
            self.assertEqual(scan_res.physical_data_lines, 3)
            self.assertEqual(scan_res.logical_data_records, 2)
            self.assertEqual(scan_res.embedded_newline_count, 1)
            self.assertTrue(scan_res.is_verifiable)

            raw_df = reader.read_raw(csv_path, source_year=2016)
            classified_df = IngestionRecordClassifier.classify(raw_df)
            accounting = compute_row_accounting(classified_df, scan_result=scan_res)

            self.assertEqual(accounting.raw_row_count, 2)
            self.assertEqual(accounting.accepted_row_count, 2)

            curated_df = IngestionTransformer.to_curated(classified_df)
            carriers = sorted(r["OP_CARRIER"] for r in curated_df.collect())
            self.assertEqual(carriers, ["AMERICAN\nAIRLINES", "DELTA, INC"])

    def test_null_weather_columns_accepted(self):
        """RDR-09: Absence of weather data (nulls) preserves record as ACCEPTED per FP-DEC-017."""
        with tempfile.TemporaryDirectory() as td:
            fields = [
                "2016-01-01", "AA", "100.0", "JFK", "LAX", "0800", "0810", "10.0", "15.0",
                "0825", "1110", "5.0", "1120", "1115", "-5.0", "360.0", "355.0", "335.0",
                "1.0", "1", "1", "5", "100", "200",
                "", "", "", "", "", "",  # Empty weather fields (6 columns)
                "40.6413", "-73.7781", "33.9416", "-118.4085"
            ]
            row = ",".join(fields)
            csv_path = self._create_synthetic_csv(Path(td), [row])

            reader = RawCsvReader(self.spark)
            raw_df = reader.read_raw(csv_path)
            classified_df = IngestionRecordClassifier.classify(raw_df)
            accounting = compute_row_accounting(classified_df, source_path=csv_path)

            self.assertEqual(accounting.raw_row_count, 1)
            self.assertEqual(accounting.accepted_row_count, 1)

            curated_df = IngestionTransformer.to_curated(classified_df)
            rec = curated_df.collect()[0]
            self.assertIsNone(rec["O_TEMP"])
            self.assertIsNone(rec["O_PRCP"])
            self.assertIsNone(rec["D_TEMP"])

    def test_header_only_csv_handling(self):
        """RDR-10: Header-only CSV file yields 0 rows with balanced accounting (0 = 0 + 0 + 0)."""
        with tempfile.TemporaryDirectory() as td:
            csv_path = self._create_synthetic_csv(Path(td), [])

            scan_res = scan_csv_logical_records(csv_path)
            self.assertEqual(scan_res.logical_data_records, 0)
            self.assertTrue(scan_res.is_verifiable)

            reader = RawCsvReader(self.spark)
            raw_df = reader.read_raw(csv_path)
            classified_df = IngestionRecordClassifier.classify(raw_df)
            accounting = compute_row_accounting(classified_df, scan_result=scan_res)

            self.assertEqual(accounting.raw_row_count, 0)
            self.assertEqual(accounting.accepted_row_count, 0)
            self.assertEqual(accounting.quarantined_row_count, 0)
            self.assertEqual(accounting.rejected_row_count, 0)
            self.assertTrue(accounting.is_balanced())
            self.assertIsNone(accounting.calculate_ingest_acceptance_rate())

    def test_negative_delay_values_preserved(self):
        """RDR-11: Early arrivals/departures with negative signed delays are preserved exactly (KPI-03)."""
        with tempfile.TemporaryDirectory() as td:
            row_early = self._make_valid_34_col_row(dep_delay="-18.0", arr_delay="-45.5")
            csv_path = self._create_synthetic_csv(Path(td), [row_early])

            reader = RawCsvReader(self.spark)
            raw_df = reader.read_raw(csv_path)
            classified_df = IngestionRecordClassifier.classify(raw_df)
            curated_df = IngestionTransformer.to_curated(classified_df)

            rec = curated_df.collect()[0]
            self.assertEqual(rec["DEP_DELAY"], -18.0)
            self.assertEqual(rec["ARR_DELAY"], -45.5)

    def test_fix_f01_physical_header_validation_all_failure_modes(self):
        """RDR-12 (FIX-F01): Physical header validation rejects missing, extra, reordered, duplicate, unknown, and BOM headers."""
        with tempfile.TemporaryDirectory() as td:
            td_path = Path(td)
            valid_row = self._make_valid_34_col_row()
            reader = RawCsvReader(self.spark)

            # 1. Missing column (33 columns)
            csv_missing = self._create_synthetic_csv(
                td_path, [valid_row], "missing.csv", header_cols=list(CANONICAL_COLUMN_NAMES[:-1])
            )
            with self.assertRaises(HeaderValidationError) as ctx1:
                reader.read_raw(csv_missing)
            self.assertIn("expected 34 columns, got 33", str(ctx1.exception))

            # 2. Extra column (35 business columns)
            csv_extra = self._create_synthetic_csv(
                td_path, [valid_row], "extra.csv", header_cols=list(CANONICAL_COLUMN_NAMES) + ["EXTRA_COL"]
            )
            with self.assertRaises(HeaderValidationError) as ctx2:
                reader.read_raw(csv_extra)
            self.assertIn("expected 34 columns, got 35", str(ctx2.exception))

            # 3. Technical _corrupt_record in physical header
            csv_corrupt_hdr = self._create_synthetic_csv(
                td_path, [valid_row], "corrupt_hdr.csv",
                header_cols=list(CANONICAL_COLUMN_NAMES[:-1]) + [CORRUPT_RECORD_COLUMN]
            )
            with self.assertRaises(HeaderValidationError) as ctx3:
                reader.read_raw(csv_corrupt_hdr)
            self.assertIn(CORRUPT_RECORD_COLUMN, str(ctx3.exception))

            # 4. Reordered columns (swap FL_DATE and OP_CARRIER)
            reordered = list(CANONICAL_COLUMN_NAMES)
            reordered[0], reordered[1] = reordered[1], reordered[0]
            csv_reordered = self._create_synthetic_csv(
                td_path, [valid_row], "reordered.csv", header_cols=reordered
            )
            with self.assertRaises(HeaderValidationError) as ctx4:
                reader.read_raw(csv_reordered)
            self.assertIn("order drift", str(ctx4.exception))

            # 5. Duplicate column name
            dup_cols = list(CANONICAL_COLUMN_NAMES)
            dup_cols[1] = "FL_DATE"
            csv_dup = self._create_synthetic_csv(
                td_path, [valid_row], "dup.csv", header_cols=dup_cols
            )
            with self.assertRaises(HeaderValidationError) as ctx5:
                reader.read_raw(csv_dup)
            self.assertIn("Duplicate column names", str(ctx5.exception))

            # 6. Unknown column name replacing a canonical column
            unk_cols = list(CANONICAL_COLUMN_NAMES)
            unk_cols[5] = "UNKNOWN_SCHEDULE_FIELD"
            csv_unk = self._create_synthetic_csv(
                td_path, [valid_row], "unk.csv", header_cols=unk_cols
            )
            with self.assertRaises(HeaderValidationError) as ctx6:
                reader.read_raw(csv_unk)
            self.assertIn("UNKNOWN_SCHEDULE_FIELD", str(ctx6.exception))

            # 7. UTF-8 BOM rejected by default, accepted when allow_utf8_bom=True
            bom_path = td_path / "bom.csv"
            bom_bytes = b"\xef\xbb\xbf" + (",".join(CANONICAL_COLUMN_NAMES) + "\n" + valid_row + "\n").encode("utf-8")
            bom_path.write_bytes(bom_bytes)
            with self.assertRaises(HeaderValidationError) as ctx7:
                validate_physical_csv_header(bom_path, CsvReadOptions(allow_utf8_bom=False))
            self.assertIn("UTF-8 BOM", str(ctx7.exception))

            cols_bom, has_bom = validate_physical_csv_header(bom_path, CsvReadOptions(allow_utf8_bom=True))
            self.assertTrue(has_bom)
            self.assertEqual(cols_bom, list(CANONICAL_COLUMN_NAMES))

            # 8. UTF-16 BOM and NUL byte rejected
            utf16_path = td_path / "utf16.csv"
            utf16_path.write_bytes(b"\xff\xfe" + b"FL_DATE,OP_CARRIER\n")
            with self.assertRaises(HeaderValidationError):
                validate_physical_csv_header(utf16_path)

            nul_path = td_path / "nul.csv"
            nul_path.write_bytes(b"FL_DATE\x00,OP_CARRIER\n")
            with self.assertRaises(HeaderValidationError):
                validate_physical_csv_header(nul_path)

    def test_fix_f06_calendar_dates_and_core_identity_anchors(self):
        """RDR-13 (FIX-F06): Real calendar dates, leap year, timestamp suffix, source year mismatch, and core identity anchors."""
        with tempfile.TemporaryDirectory() as td:
            rows = [
                # 1. Valid leap-year date 2016-02-29 -> ACCEPTED
                self._make_valid_34_col_row(fl_date="2016-02-29", op_carrier="AA", fl_num="101"),
                # 2. Valid timestamp-suffixed date 2016-01-15 00:00:00 with blank MONTH/DAY_OF_MONTH -> ACCEPTED & normalized
                self._make_valid_34_col_row(fl_date="2016-01-15 00:00:00", op_carrier="DL", fl_num="102", month="", day_of_month=""),
                # 3. Impossible date 2016-02-30 -> QUARANTINED (INVALID_FL_DATE_CORE_ANCHOR)
                self._make_valid_34_col_row(fl_date="2016-02-30", op_carrier="UA", fl_num="103"),
                # 4. Non-leap year 2019-02-29 -> QUARANTINED (INVALID_FL_DATE_CORE_ANCHOR)
                self._make_valid_34_col_row(fl_date="2019-02-29", op_carrier="WN", fl_num="104"),
                # 5. Valid calendar date in wrong source year (2017-03-10 in 2016 file) -> QUARANTINED (SOURCE_YEAR_DATE_MISMATCH)
                self._make_valid_34_col_row(fl_date="2017-03-10", op_carrier="B6", fl_num="105"),
                # 6. Missing OP_CARRIER -> QUARANTINED (MISSING_CARRIER_CORE_ANCHOR)
                self._make_valid_34_col_row(fl_date="2016-04-01", op_carrier="", fl_num="106"),
                # 7. Missing ORIGIN -> QUARANTINED (MISSING_AIRPORT_CORE_ANCHOR)
                self._make_valid_34_col_row(fl_date="2016-04-02", op_carrier="AS", fl_num="107", origin=""),
                # 8. Missing DEST -> QUARANTINED (MISSING_AIRPORT_CORE_ANCHOR)
                self._make_valid_34_col_row(fl_date="2016-04-03", op_carrier="AS", fl_num="108", dest=""),
                # 9. Non-numeric OP_CARRIER_FL_NUM -> QUARANTINED (INVALID_FLIGHT_NUM_CORE_ANCHOR)
                self._make_valid_34_col_row(fl_date="2016-04-04", op_carrier="NK", fl_num="BAD_FL_NUM"),
            ]
            csv_path = self._create_synthetic_csv(Path(td), rows)

            scan_res = scan_csv_logical_records(csv_path, source_year=2016)
            reader = RawCsvReader(self.spark)
            raw_df = reader.read_raw(csv_path, source_year=2016, attach_lineage=True)
            classified_df = IngestionRecordClassifier.classify(raw_df)

            accounting = compute_row_accounting(classified_df, scan_result=scan_res)
            self.assertEqual(accounting.raw_row_count, 9)
            self.assertEqual(accounting.accepted_row_count, 2)
            self.assertEqual(accounting.quarantined_row_count, 7)
            self.assertEqual(accounting.rejected_row_count, 0)

            quar_rows = classified_df.filter(F.col(STATUS_COLUMN) == RecordStatus.QUARANTINED.value).collect()
            reasons = [r[REASON_COLUMN] for r in quar_rows]
            self.assertEqual(reasons.count(AnomalyReason.INVALID_FL_DATE_CORE_ANCHOR.value), 2)
            self.assertEqual(reasons.count(AnomalyReason.SOURCE_YEAR_DATE_MISMATCH.value), 1)
            self.assertEqual(reasons.count(AnomalyReason.MISSING_CARRIER_CORE_ANCHOR.value), 1)
            self.assertEqual(reasons.count(AnomalyReason.MISSING_AIRPORT_CORE_ANCHOR.value), 2)
            self.assertEqual(reasons.count(AnomalyReason.INVALID_FLIGHT_NUM_CORE_ANCHOR.value), 1)

            # Verify curated normalization of 2016-01-15 00:00:00 and derived MONTH/DAY_OF_MONTH
            curated_df = IngestionTransformer.to_curated(classified_df)
            dl_rec = curated_df.filter(F.col("OP_CARRIER") == "DL").collect()[0]
            self.assertEqual(dl_rec["FL_DATE"], "2016-01-15")
            self.assertEqual(dl_rec["MONTH"], 1)
            self.assertEqual(dl_rec["DAY_OF_MONTH"], 15)

    def test_fix_f02_unclosed_quote_blank_line_and_accounting_unverified(self):
        """RDR-14 (FIX-F02): Unclosed quotes, blank lines, and tampered classifier counts raise AccountingUnverifiedError."""
        with tempfile.TemporaryDirectory() as td:
            td_path = Path(td)
            valid_row = self._make_valid_34_col_row()

            # 1. Single-line mode unclosed quote is captured as REJECTED by Univocity and reconciles 1-to-1
            unclosed_single = '"2016-01-02,AA,100.0,JFK,LAX'
            csv_unclosed = self._create_synthetic_csv(td_path, [valid_row, unclosed_single], "unclosed.csv")
            scan_u = scan_csv_logical_records(csv_unclosed, CsvReadOptions(multi_line=False))
            self.assertEqual(scan_u.unclosed_quote_count, 1)
            self.assertTrue(scan_u.is_verifiable)

            reader = RawCsvReader(self.spark)
            cls_u = IngestionRecordClassifier.classify(reader.read_raw(csv_unclosed))
            acc_u = compute_row_accounting(cls_u, scan_result=scan_u)
            self.assertEqual(acc_u.raw_row_count, 2)
            self.assertEqual(acc_u.accepted_row_count, 1)
            self.assertEqual(acc_u.rejected_row_count, 1)

            # 2. Multi-line mode unclosed quote reaching EOF is flagged ACCOUNTING_UNVERIFIED
            scan_u_ml = scan_csv_logical_records(csv_unclosed, CsvReadOptions(multi_line=True))
            self.assertFalse(scan_u_ml.is_verifiable)
            with self.assertRaises(AccountingUnverifiedError) as ctx_ml:
                compute_row_accounting(cls_u, scan_result=scan_u_ml)
            self.assertIn("ACCOUNTING_UNVERIFIED", str(ctx_ml.exception))

            # 3. Blank line in CSV is silently skipped by Univocity -> scanner flags ACCOUNTING_UNVERIFIED
            csv_blank = self._create_synthetic_csv(td_path, [valid_row, "", valid_row], "blank.csv")
            scan_blank = scan_csv_logical_records(csv_blank)
            self.assertEqual(scan_blank.blank_lines_count, 1)
            self.assertFalse(scan_blank.is_verifiable)
            with self.assertRaises(AccountingUnverifiedError) as ctx_blk:
                compute_row_accounting(cls_u, scan_result=scan_blank)
            self.assertIn("ACCOUNTING_UNVERIFIED", str(ctx_blk.exception))

            # 4. Tampered/dropped row in classifier DataFrame triggers ACCOUNTING_UNVERIFIED against independent count
            tampered_df = cls_u.limit(1)
            with self.assertRaises(AccountingUnverifiedError) as ctx_tamp:
                compute_row_accounting(tampered_df, independent_raw_count=2)
            self.assertIn("ACCOUNTING_UNVERIFIED", str(ctx_tamp.exception))

    def test_fix_f02_deterministic_lineage_and_duplicate_yx3624_disambiguation(self):
        """RDR-15 (FIX-F02 / TS-020): Deterministic content-hash lineage disambiguates exact duplicate rows (2018-06-21 YX 3624 DEN->XNA & 2022)."""
        with tempfile.TemporaryDirectory() as td:
            dup_row_2018 = self._make_valid_34_col_row(
                fl_date="2018-06-21", op_carrier="YX", fl_num="3624.0", origin="DEN", dest="XNA", month="6", day_of_month="21"
            )
            other_row_2018 = self._make_valid_34_col_row(
                fl_date="2018-06-21", op_carrier="AA", fl_num="100.0", origin="JFK", dest="LAX", month="6", day_of_month="21"
            )
            csv_path = self._create_synthetic_csv(
                Path(td), [dup_row_2018, other_row_2018, dup_row_2018], "flight_2018.csv"
            )

            reader = RawCsvReader(self.spark)
            df1 = reader.read_raw(csv_path, source_year=2018, attach_lineage=True).repartition(1)
            df2 = reader.read_raw(csv_path, source_year=2018, attach_lineage=True).repartition(4)

            ids1 = sorted(r[LINEAGE_ID_COLUMN] for r in df1.collect())
            ids2 = sorted(r[LINEAGE_ID_COLUMN] for r in df2.collect())

            # Lineage IDs must be 3 distinct SHA-256 hex strings and 100% identical across different partition counts
            self.assertEqual(len(ids1), 3)
            self.assertEqual(len(set(ids1)), 3)
            self.assertEqual(ids1, ids2)

    def test_blocker01_quoted_embedded_newline_multimode_and_fail_closed(self):
        """
        RDR-16 (BLOCKER-01): 34-column 2-record CSV where 1 field is quoted with an embedded newline:
        - csv.reader returns 2 logical data records.
        - scan_csv_logical_records(multi_line=True) returns logical_data_records=2, physical_data_lines=3, is_verifiable=True.
        - scan_csv_logical_records(multi_line=False) returns logical_data_records=2 (NEVER 3!), physical_data_lines=3,
          embedded_newline_count=1, is_verifiable=False (ACCOUNTING_UNVERIFIED).
        - RawCsvReader(multi_line=False).read_raw(..., enforce_record_boundaries=True) fails closed.
        - If Spark parses 3 physical lines with multiLine=False, compute_row_accounting fails closed on 2 != 3.
        - Calling compute_row_accounting without an independent source count fails closed.
        """
        import csv as py_csv

        with tempfile.TemporaryDirectory() as td:
            row1 = self._make_valid_34_col_row(op_carrier="AA", fl_num="100.0")
            row2 = self._make_valid_34_col_row(op_carrier='"AMERICAN\nAIRLINES"', fl_num="200.0")
            csv_path = self._create_synthetic_csv(Path(td), [row1, row2], "multiline_2rec.csv")

            # 1. Python csv.reader ground truth: 1 header + 2 logical data records
            with open(csv_path, "r", encoding="utf-8", newline="") as f:
                py_rows = list(py_csv.reader(f))
            self.assertEqual(len(py_rows) - 1, 2)

            # 2. scan_csv_logical_records with multi_line=True
            scan_true = scan_csv_logical_records(csv_path, CsvReadOptions(multi_line=True), source_year=2016)
            self.assertEqual(scan_true.logical_data_records, 2)
            self.assertEqual(scan_true.physical_data_lines, 3)
            self.assertEqual(scan_true.embedded_newline_count, 1)
            self.assertTrue(scan_true.is_verifiable)

            # 3. scan_csv_logical_records with multi_line=False (default contract mode)
            scan_false = scan_csv_logical_records(csv_path, CsvReadOptions(multi_line=False), source_year=2016)
            self.assertEqual(scan_false.logical_data_records, 2)
            self.assertEqual(scan_false.physical_data_lines, 3)
            self.assertEqual(scan_false.embedded_newline_count, 1)
            self.assertFalse(scan_false.is_verifiable)
            self.assertIn("ACCOUNTING_UNVERIFIED", scan_false.unverified_reason or "")

            # 4. RawCsvReader(multi_line=False).read_raw(..., enforce_record_boundaries=True) fails closed
            reader_false = RawCsvReader(self.spark, CsvReadOptions(multi_line=False))
            with self.assertRaises(AccountingUnverifiedError) as ctx_enforced:
                reader_false.read_raw(csv_path, source_year=2016, enforce_record_boundaries=True)
            self.assertIn("ACCOUNTING_UNVERIFIED", str(ctx_enforced.exception))

            # 5. Even if read_raw is called with enforce_record_boundaries=False (so Spark splits into 3 rows),
            # compute_row_accounting fails closed both via scan_false and via independent_raw_count=2
            raw_split_df = reader_false.read_raw(csv_path, source_year=2016, enforce_record_boundaries=False)
            cls_split_df = IngestionRecordClassifier.classify(raw_split_df)
            self.assertEqual(cls_split_df.count(), 3)

            with self.assertRaises(AccountingUnverifiedError) as ctx_scan:
                compute_row_accounting(cls_split_df, scan_result=scan_false)
            self.assertIn("ACCOUNTING_UNVERIFIED", str(ctx_scan.exception))

            with self.assertRaises(AccountingUnverifiedError) as ctx_ind:
                compute_row_accounting(cls_split_df, independent_raw_count=2)
            self.assertIn("ACCOUNTING_UNVERIFIED", str(ctx_ind.exception))

            # 6. Calling compute_row_accounting with NO independent source count fails closed
            with self.assertRaises(AccountingUnverifiedError) as ctx_no_src:
                compute_row_accounting(cls_split_df)
            self.assertIn("ACCOUNTING_UNVERIFIED", str(ctx_no_src.exception))

    def test_blocker01_spark_401_multiline_quoted_escaped_and_eof_no_trailing_newline(self):
        """
        RDR-17 (BLOCKER-01): Real Spark 4.0.1 verification on 34-column synthetic fixtures covering:
        1. Quoted field with embedded newline (multiLine=True) -> 2 logical records, 2 accepted.
        2. Quoted field with escaped quotes (\"\"\") -> exact string preserved, 2 logical records == 2 Spark rows.
        3. EOF without trailing newline -> 2 logical records == 2 Spark rows, is_verifiable=True.
        """
        with tempfile.TemporaryDirectory() as td:
            td_path = Path(td)

            # 1. Quoted field with escaped quotes ("DELTA ""AIR"" LINES")
            row_clean = self._make_valid_34_col_row(op_carrier="AA", fl_num="101.0")
            row_escaped = self._make_valid_34_col_row(op_carrier='"DELTA ""AIR"" LINES"', fl_num="202.0")
            csv_escaped = self._create_synthetic_csv(td_path, [row_clean, row_escaped], "escaped_quotes.csv")

            scan_esc = scan_csv_logical_records(csv_escaped, CsvReadOptions(multi_line=False), source_year=2016)
            self.assertEqual(scan_esc.logical_data_records, 2)
            self.assertEqual(scan_esc.physical_data_lines, 2)
            self.assertTrue(scan_esc.is_verifiable)

            reader_single = RawCsvReader(self.spark, CsvReadOptions(multi_line=False))
            cls_esc = IngestionRecordClassifier.classify(
                reader_single.read_raw(csv_escaped, source_year=2016, scan_result=scan_esc, enforce_record_boundaries=True)
            )
            acc_esc = compute_row_accounting(cls_esc, scan_result=scan_esc)
            self.assertEqual(acc_esc.raw_row_count, 2)
            self.assertEqual(acc_esc.accepted_row_count, 2)
            cur_esc = IngestionTransformer.to_curated(cls_esc)
            carriers = sorted(r["OP_CARRIER"] for r in cur_esc.collect())
            self.assertEqual(carriers, ["AA", 'DELTA "AIR" LINES'])

            # 2. EOF without trailing newline
            eof_path = td_path / "no_trailing_newline.csv"
            header_line = ",".join(CANONICAL_COLUMN_NAMES)
            r1 = self._make_valid_34_col_row(op_carrier="UA", fl_num="301.0")
            r2 = self._make_valid_34_col_row(op_carrier="WN", fl_num="302.0")
            eof_path.write_bytes((header_line + "\n" + r1 + "\n" + r2).encode("utf-8"))

            scan_eof = scan_csv_logical_records(eof_path, CsvReadOptions(multi_line=False), source_year=2016)
            self.assertEqual(scan_eof.physical_lines_total, 3)
            self.assertEqual(scan_eof.physical_data_lines, 2)
            self.assertEqual(scan_eof.logical_data_records, 2)
            self.assertTrue(scan_eof.is_verifiable)

            cls_eof = IngestionRecordClassifier.classify(
                reader_single.read_raw(eof_path, source_year=2016, scan_result=scan_eof, enforce_record_boundaries=True)
            )
            acc_eof = compute_row_accounting(cls_eof, scan_result=scan_eof)
            self.assertEqual(acc_eof.raw_row_count, 2)
            self.assertEqual(acc_eof.accepted_row_count, 2)


if __name__ == "__main__":
    unittest.main()
