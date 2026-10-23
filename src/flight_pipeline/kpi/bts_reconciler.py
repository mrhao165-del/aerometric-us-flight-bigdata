"""
BTS TranStats Sample Parity & Reconciliation Engine for TS-018 (G2-EXC-001).
Compares the 7 CORE numeric measures between candidate dataset records and official BTS records.
Handles composite key matching, duplicate detection, ambiguity classification, and numeric tolerances.
Hardened under Master Prompt T011-R3:
- Strict provenance trust boundary separating 5 governance states; no self-approved authentic pass.
- Typed numeric parser distinguishing TRUE_NULL, VALID_FINITE_NUMBER, MALFORMED_NUMBER, and NONFINITE_NUMBER.
- Calendar-aware ISO date validation preventing impossible dates (e.g., Feb 31, non-leap leap days).
- Comprehensive reconciliation success predicate requiring zero unmatched records, zero duplicates, zero invalid keys.
"""

from dataclasses import dataclass, field, asdict
from datetime import date
from enum import Enum
import math
import re
from typing import List, Dict, Any, Optional, Tuple, Set


# The 7 canonical CORE numeric measures and their BTS equivalent column names
CORE_MEASURE_MAPPINGS: Dict[str, str] = {
    "ARR_DELAY": "ArrDelay",
    "DEP_DELAY": "DepDelay",
    "TAXI_OUT": "TaxiOut",
    "TAXI_IN": "TaxiIn",
    "AIR_TIME": "AirTime",
    "ACTUAL_ELAPSED_TIME": "ActualElapsedTime",
    "CRS_ELAPSED_TIME": "CRSElapsedTime",
}

ISO_DATE_REGEX = re.compile(r"^(\d{4})-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])$")
SHA256_HEX_REGEX = re.compile(r"^[0-9a-fA-F]{64}$")


def is_valid_sha256_hex(val: Any) -> bool:
    """Validate that val is a string of exactly 64 hexadecimal characters with no whitespace."""
    if not val or not isinstance(val, str):
        return False
    if val != val.strip():
        return False
    return bool(SHA256_HEX_REGEX.match(val))


# Approved explicit null representations under project null policy
APPROVED_NULL_STRINGS: Set[str] = {"", "na", "null", "none", "nan_rep_none"}


class NumericParseStatus(str, Enum):
    VALID_FINITE_NUMBER = "VALID_FINITE_NUMBER"
    TRUE_NULL = "TRUE_NULL"
    MALFORMED_NUMBER = "MALFORMED_NUMBER"
    NONFINITE_NUMBER = "NONFINITE_NUMBER"
    SCHEMA_MISSING = "SCHEMA_MISSING"


class MismatchType(str, Enum):
    EXACT_MATCH = "EXACT_MATCH"
    ROUNDING_DIFF = "ROUNDING_DIFF"
    SCALE_DIFF = "SCALE_DIFF"
    MISSINGNESS_MISMATCH = "MISSINGNESS_MISMATCH"
    SIGN_MISMATCH = "SIGN_MISMATCH"
    VALUE_MISMATCH = "VALUE_MISMATCH"
    MALFORMED_NUMERIC_ERROR = "MALFORMED_NUMERIC_ERROR"
    NULL_NULL_AGREEMENT = "NULL_NULL_AGREEMENT"
    SCHEMA_MISSING_COLUMN = "SCHEMA_MISSING_COLUMN"


class KeyMatchStatus(str, Enum):
    UNIQUE_MATCH = "UNIQUE_MATCH"
    AMBIGUOUS_DUPLICATE = "AMBIGUOUS_DUPLICATE"
    INVALID_KEY = "INVALID_KEY"
    UNMATCHED_IN_DATASET = "UNMATCHED_IN_DATASET"
    UNMATCHED_IN_BTS = "UNMATCHED_IN_BTS"


@dataclass
class BtsProvenanceMetadata:
    """Provenance and custody metadata for external BTS reference candidate."""
    source_agency: str = "US Bureau of Transportation Statistics"
    table_identifier: str = "Reporting Carrier On-Time Performance (1987-present)"
    source_period: str = ""
    export_fields: List[str] = field(default_factory=list)
    sha256_hash: str = ""
    acquisition_date: str = ""
    acquired_by: str = ""
    chain_of_custody_ref: str = ""
    project_lead_approval_status: str = "PENDING_APPROVAL"  # Must be "APPROVED_BY_PROJECT_LEAD"
    approval_record_ref: str = ""
    is_external_reference: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class BtsProvenanceValidator:
    """
    Validates provenance for external BTS reference candidate data.
    Enforces that file presence or local SHA-256 alone does NOT confer authenticity.
    Requires official project lead approval and verified acquisition metadata.
    A local metadata file or API boolean alone cannot substitute for genuine human signoff.

    Hardened under R4-F01:
    - Strictly disaggregates metadata format validity, candidate checksum matching,
      and independent external provenance authentication.
    - Prohibits self-tautology fallbacks when actual_bts_sha256 is absent.
    - Self-authored companion JSON claiming 'APPROVED_BY_PROJECT_LEAD' cannot self-authenticate
      external BTS provenance; external provenance verification requires independent authority.
    """
    REQUIRED_APPROVAL_STATUS = "APPROVED_BY_PROJECT_LEAD"

    @classmethod
    def validate_metadata_format(
        cls,
        provenance: Optional[BtsProvenanceMetadata],
    ) -> Tuple[bool, str]:
        """Validate structure and completeness of candidate provenance metadata."""
        if provenance is None:
            return False, "PROVENANCE_MISSING: No provenance metadata record provided."

        if not provenance.is_external_reference:
            return False, "PROVENANCE_NOT_EXTERNAL: Reference file is not certified as an external source."

        if not provenance.sha256_hash or not is_valid_sha256_hex(provenance.sha256_hash):
            return False, "PROVENANCE_MALFORMED_HASH: Expected SHA-256 hash is missing or not a valid 64-character hexadecimal digest."

        if not provenance.approval_record_ref or not provenance.approval_record_ref.strip():
            return False, "PROVENANCE_MISSING_APPROVAL_REF: No official approval record reference provided."

        if provenance.project_lead_approval_status != cls.REQUIRED_APPROVAL_STATUS:
            return False, (
                f"PROVENANCE_UNAPPROVED: Project Lead approval status is '{provenance.project_lead_approval_status}', "
                f"required '{cls.REQUIRED_APPROVAL_STATUS}'."
            )

        return True, "PROVENANCE_METADATA_FORMAT_VERIFIED"

    @classmethod
    def validate_candidate_checksum(
        cls,
        provenance: Optional[BtsProvenanceMetadata],
        actual_sha256: Optional[str],
    ) -> Tuple[bool, str]:
        """
        Validate physical file SHA-256 against declared provenance hash.
        Strictly requires actual_sha256; no self-comparison fallback permitted (R4-F01).
        Enforces strict 64-character hexadecimal encoding (R5-F02).
        """
        if provenance is None:
            return False, "PROVENANCE_MISSING: No provenance metadata record provided."

        if not actual_sha256 or not isinstance(actual_sha256, str) or not actual_sha256.strip():
            return False, (
                "PROVENANCE_ACTUAL_CHECKSUM_MISSING: Actual physical file SHA-256 is required; "
                "self-comparison fallback is prohibited."
            )

        if not is_valid_sha256_hex(actual_sha256):
            return False, (
                "PROVENANCE_ACTUAL_CHECKSUM_MALFORMED: Actual physical file SHA-256 must be exactly 64 hexadecimal characters."
            )

        if not provenance.sha256_hash or not is_valid_sha256_hex(provenance.sha256_hash):
            return False, "PROVENANCE_MALFORMED_HASH: Declared SHA-256 hash is missing or not a valid 64-character hexadecimal digest."

        if provenance.sha256_hash.strip().lower() != actual_sha256.strip().lower():
            return False, (
                f"PROVENANCE_HASH_MISMATCH: Declared {provenance.sha256_hash} != Actual {actual_sha256}."
            )

        return True, "CANDIDATE_CHECKSUM_MATCHED"

    @classmethod
    def validate_provenance(
        cls,
        provenance: Optional[BtsProvenanceMetadata],
        actual_sha256: Optional[str],
    ) -> Tuple[bool, str]:
        """
        Validates metadata structure and checksum consistency for a candidate BTS file.
        R4-F01: Strictly rejects missing actual_sha256 and prevents self-matching.
        """
        fmt_ok, fmt_msg = cls.validate_metadata_format(provenance)
        if not fmt_ok:
            return False, fmt_msg

        chk_ok, chk_msg = cls.validate_candidate_checksum(provenance, actual_sha256)
        if not chk_ok:
            return False, chk_msg

        return True, "PROVENANCE_METADATA_FORMAT_AND_CHECKSUM_VERIFIED"


@dataclass
class FieldComparison:
    field_name: str
    bts_field_name: str
    dataset_val: Optional[float]
    bts_val: Optional[float]
    status: MismatchType
    abs_diff: Optional[float]
    dataset_parse_status: NumericParseStatus = NumericParseStatus.VALID_FINITE_NUMBER
    bts_parse_status: NumericParseStatus = NumericParseStatus.VALID_FINITE_NUMBER


@dataclass
class MatchedRecordResult:
    composite_key: Tuple[Any, ...]
    key_status: KeyMatchStatus
    field_comparisons: Dict[str, FieldComparison] = field(default_factory=dict)
    all_fields_match: bool = False


@dataclass
class ReconciliationSummary:
    total_dataset_records: int = 0
    total_bts_records: int = 0
    unique_key_matches: int = 0
    ambiguous_duplicate_keys: int = 0
    invalid_key_records: int = 0
    unmatched_dataset_records: int = 0
    unmatched_bts_records: int = 0
    field_statistics: Dict[str, Dict[str, int]] = field(default_factory=dict)

    # Disaggregated governance states (R2-F01, R3-F01, R4-F01)
    file_present: bool = False
    schema_valid: bool = False
    companion_metadata_valid: bool = False
    candidate_checksum_matched: bool = False
    source_provenance_verified: bool = False
    numerical_parity_verified: bool = False
    human_accepted: bool = False

    is_authentic_bts_data: bool = False
    reconciliation_verdict: str = "PENDING_OFFICIAL_BTS_SOURCE"
    notes: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class BtsTranStatsReconciler:
    """
    Independent reconciliation harness for TS-018.
    Compares 7 CORE numeric measures between dataset records and BTS TranStats records.
    """

    def __init__(self, tolerance: float = 1e-4):
        self.tolerance = tolerance

    @staticmethod
    def _lookup_present_key(rec: Dict[str, Any], candidate_keys: List[str]) -> Tuple[bool, Any]:
        """
        Lookup first key from candidate_keys that is physically present in rec and not None.
        Returns (present, value).
        """
        for k in candidate_keys:
            if k in rec and rec[k] is not None:
                return True, rec[k]
        return False, None

    @classmethod
    def extract_composite_key(
        cls, rec: Dict[str, Any]
    ) -> Tuple[Optional[str], Optional[str], Optional[float], Optional[str], Optional[str], bool]:
        """
        Extract canonical composite key: (FL_DATE, OP_CARRIER, OP_CARRIER_FL_NUM, ORIGIN, DEST, is_valid).
        Safely normalizes date, carrier, and flight number.
        Preserves numerical zero (0.0) without masking (G3-COND-A).
        Validates real calendar dates (R3-F04) preventing impossible calendar dates.
        """
        # 1. Date extraction & calendar validation (R3-F04)
        has_date, date_val = cls._lookup_present_key(rec, ["FL_DATE", "FlightDate"])
        fl_date: Optional[str] = None
        if has_date:
            date_str = str(date_val).strip()
            m = ISO_DATE_REGEX.match(date_str)
            if m:
                year, month, day = int(m.group(1)), int(m.group(2)), int(m.group(3))
                try:
                    # Validate against real Gregorian calendar (e.g., rejects 2026-02-31, 2025-02-29)
                    _ = date(year, month, day)
                    fl_date = date_str
                except (ValueError, TypeError, OverflowError):
                    fl_date = None

        # 2. Carrier extraction
        has_carrier, carrier_val = cls._lookup_present_key(rec, ["OP_CARRIER", "Reporting_Airline", "Carrier"])
        carrier: Optional[str] = None
        if has_carrier:
            c_str = str(carrier_val).strip()
            if c_str:
                carrier = c_str.upper()

        # 3. Flight number extraction (preserves 0 and 0.0)
        has_fl_num, fl_num_val = cls._lookup_present_key(rec, ["OP_CARRIER_FL_NUM", "Flight_Number_Reporting_Airline", "FlightNum"])
        fl_num: Optional[float] = None
        if has_fl_num:
            raw_s = str(fl_num_val).strip()
            if raw_s != "":
                try:
                    f = float(fl_num_val)
                    if not (math.isnan(f) or math.isinf(f)):
                        fl_num = f
                except (ValueError, TypeError):
                    fl_num = None

        # 4. Origin & Destination extraction
        has_origin, origin_val = cls._lookup_present_key(rec, ["ORIGIN", "Origin"])
        origin: Optional[str] = None
        if has_origin:
            o_str = str(origin_val).strip()
            if o_str:
                origin = o_str.upper()

        has_dest, dest_val = cls._lookup_present_key(rec, ["DEST", "Dest"])
        dest: Optional[str] = None
        if has_dest:
            d_str = str(dest_val).strip()
            if d_str:
                dest = d_str.upper()

        is_valid = bool(
            fl_date is not None
            and carrier is not None
            and fl_num is not None
            and origin is not None
            and dest is not None
        )

        return (fl_date, carrier, fl_num, origin, dest, is_valid)

    @classmethod
    def parse_numeric_measure(cls, val: Any) -> Tuple[NumericParseStatus, Optional[float]]:
        """
        Typed numeric measure parser conforming to R3-F02 requirements.
        Explicitly distinguishes VALID_FINITE_NUMBER, TRUE_NULL, MALFORMED_NUMBER, and NONFINITE_NUMBER.
        """
        if val is None:
            return NumericParseStatus.TRUE_NULL, None

        # Handle string inputs
        if isinstance(val, str):
            clean_s = val.strip()
            if clean_s.lower() in APPROVED_NULL_STRINGS:
                return NumericParseStatus.TRUE_NULL, None
            # Check explicit non-finite string tokens
            if clean_s.lower() in ("nan", "+nan", "-nan", "inf", "+inf", "-inf", "infinity", "+infinity", "-infinity"):
                return NumericParseStatus.NONFINITE_NUMBER, None
            try:
                f = float(clean_s)
                if math.isnan(f) or math.isinf(f):
                    return NumericParseStatus.NONFINITE_NUMBER, None
                return NumericParseStatus.VALID_FINITE_NUMBER, f
            except (ValueError, TypeError):
                return NumericParseStatus.MALFORMED_NUMBER, None

        # Handle numeric types (int, float, Decimal, etc.)
        if isinstance(val, (int, float)):
            if math.isnan(val) or math.isinf(val):
                return NumericParseStatus.NONFINITE_NUMBER, None
            return NumericParseStatus.VALID_FINITE_NUMBER, float(val)

        # Fallback for unexpected types
        try:
            f = float(val)
            if math.isnan(f) or math.isinf(f):
                return NumericParseStatus.NONFINITE_NUMBER, None
            return NumericParseStatus.VALID_FINITE_NUMBER, f
        except (ValueError, TypeError):
            return NumericParseStatus.MALFORMED_NUMBER, None

    def compare_single_field(
        self,
        field_name: str,
        bts_field_name: str,
        rec_dataset: Dict[str, Any],
        rec_bts: Dict[str, Any],
    ) -> FieldComparison:
        """
        Compare a single numeric measure between dataset and BTS.
        Strictly prevents malformed numbers or non-finites from becoming NULL_NULL_AGREEMENT (R3-F02).
        """
        has_d = field_name in rec_dataset
        has_b = (bts_field_name in rec_bts) or (field_name in rec_bts)

        # Missing column on one or both sides
        if not has_d or not has_b:
            d_st, d_v = (self.parse_numeric_measure(rec_dataset.get(field_name)) if has_d else (NumericParseStatus.SCHEMA_MISSING, None))
            b_st, b_v = (self.parse_numeric_measure(rec_bts.get(bts_field_name, rec_bts.get(field_name))) if has_b else (NumericParseStatus.SCHEMA_MISSING, None))
            return FieldComparison(
                field_name=field_name,
                bts_field_name=bts_field_name,
                dataset_val=d_v,
                bts_val=b_v,
                status=MismatchType.SCHEMA_MISSING_COLUMN,
                abs_diff=None,
                dataset_parse_status=d_st,
                bts_parse_status=b_st,
            )

        d_raw = rec_dataset[field_name]
        b_raw = rec_bts.get(bts_field_name, rec_bts.get(field_name))

        d_status, d_val = self.parse_numeric_measure(d_raw)
        b_status, b_val = self.parse_numeric_measure(b_raw)

        # Check for malformed or nonfinite values on either side (R3-F02 guard)
        if d_status in (NumericParseStatus.MALFORMED_NUMBER, NumericParseStatus.NONFINITE_NUMBER) or \
           b_status in (NumericParseStatus.MALFORMED_NUMBER, NumericParseStatus.NONFINITE_NUMBER):
            return FieldComparison(
                field_name=field_name,
                bts_field_name=bts_field_name,
                dataset_val=d_val,
                bts_val=b_val,
                status=MismatchType.MALFORMED_NUMERIC_ERROR,
                abs_diff=None,
                dataset_parse_status=d_status,
                bts_parse_status=b_status,
            )

        # Both present columns contain approved true nulls -> valid null-null agreement
        if d_status == NumericParseStatus.TRUE_NULL and b_status == NumericParseStatus.TRUE_NULL:
            return FieldComparison(
                field_name=field_name,
                bts_field_name=bts_field_name,
                dataset_val=None,
                bts_val=None,
                status=MismatchType.NULL_NULL_AGREEMENT,
                abs_diff=0.0,
                dataset_parse_status=d_status,
                bts_parse_status=b_status,
            )

        # One true null, other valid number -> missingness mismatch
        if d_status == NumericParseStatus.TRUE_NULL or b_status == NumericParseStatus.TRUE_NULL:
            return FieldComparison(
                field_name=field_name,
                bts_field_name=bts_field_name,
                dataset_val=d_val,
                bts_val=b_val,
                status=MismatchType.MISSINGNESS_MISMATCH,
                abs_diff=None,
                dataset_parse_status=d_status,
                bts_parse_status=b_status,
            )

        # Both are VALID_FINITE_NUMBER
        assert d_val is not None and b_val is not None
        diff = abs(d_val - b_val)

        # Exact match
        if diff == 0.0:
            status = MismatchType.EXACT_MATCH
        # Within floating-point tolerance
        elif diff <= self.tolerance:
            status = MismatchType.ROUNDING_DIFF
        # Sign mismatch (one positive, one negative)
        elif (d_val > 0 and b_val < 0) or (d_val < 0 and b_val > 0):
            status = MismatchType.SIGN_MISMATCH
        # Scale mismatch (e.g., factor of 60 between seconds and minutes)
        elif math.isclose(d_val * 60.0, b_val, rel_tol=1e-3) or math.isclose(d_val, b_val * 60.0, rel_tol=1e-3):
            status = MismatchType.SCALE_DIFF
        else:
            status = MismatchType.VALUE_MISMATCH

        return FieldComparison(
            field_name=field_name,
            bts_field_name=bts_field_name,
            dataset_val=d_val,
            bts_val=b_val,
            status=status,
            abs_diff=diff,
            dataset_parse_status=d_status,
            bts_parse_status=b_status,
        )

    def reconcile(
        self,
        dataset_records: List[Dict[str, Any]],
        bts_records: List[Dict[str, Any]],
        provenance_metadata: Optional[BtsProvenanceMetadata] = None,
        actual_bts_sha256: Optional[str] = None,
        is_authentic_bts_data: bool = False,
    ) -> Tuple[ReconciliationSummary, List[MatchedRecordResult]]:
        """
        Execute reconciliation between dataset and BTS records.
        Strictly enforces 7-field completeness, robust composite keys, and provenance gating.
        """
        summary = ReconciliationSummary(
            total_dataset_records=len(dataset_records),
            total_bts_records=len(bts_records),
            file_present=len(bts_records) > 0,
        )

        for core_field in CORE_MEASURE_MAPPINGS.keys():
            summary.field_statistics[core_field] = {
                "exact_match": 0,
                "rounding_diff": 0,
                "null_null_agreement": 0,
                "mismatch": 0,
                "missing_column": 0,
                "malformed_numeric": 0,
                "numeric_sample_count": 0,
            }

        # Validate candidate provenance (R4-F01: disaggregate format, checksum, and external trust)
        # Strictly require actual_bts_sha256; no self-comparison fallback permitted!
        if actual_bts_sha256 and isinstance(actual_bts_sha256, str) and len(actual_bts_sha256.strip()) == 64:
            check_sha: Optional[str] = actual_bts_sha256.strip().lower()
        else:
            check_sha = None

        if provenance_metadata is not None:
            fmt_ok, fmt_msg = BtsProvenanceValidator.validate_metadata_format(provenance_metadata)
            chk_ok, chk_msg = BtsProvenanceValidator.validate_candidate_checksum(provenance_metadata, check_sha)

            summary.companion_metadata_valid = fmt_ok
            summary.candidate_checksum_matched = chk_ok

            # R4-F01 Trust Invariant: A local companion JSON claiming "APPROVED_BY_PROJECT_LEAD"
            # and matching a candidate file hash does NOT constitute independent BTS provenance!
            # Independent source authentication cannot be self-issued by local JSON.
            # Therefore, source_provenance_verified remains False for local candidate files.
            summary.source_provenance_verified = False

            if not fmt_ok:
                summary.notes.append(f"Provenance metadata format invalid: {fmt_msg}")
            if not chk_ok:
                summary.notes.append(f"Candidate checksum validation failed: {chk_msg}")
            if fmt_ok and chk_ok:
                summary.notes.append(
                    "Candidate metadata format and local file checksum verified. "
                    "Independent external-source provenance remains UNVERIFIED_PENDING_HUMAN_ACQUISITION_REVIEW."
                )
        else:
            summary.companion_metadata_valid = False
            summary.candidate_checksum_matched = False
            summary.source_provenance_verified = False
            if is_authentic_bts_data:
                summary.notes.append("Caller specified is_authentic_bts_data=True without approved provenance: REJECTED.")

        # Human acceptance is NEVER granted by automated code or local JSON
        # It remains strictly False until Project Lead executes official Human Signoff
        summary.human_accepted = False
        summary.is_authentic_bts_data = False

        # Index dataset records by composite key
        dataset_index: Dict[Tuple, List[Dict[str, Any]]] = {}
        match_results: List[MatchedRecordResult] = []

        for r in dataset_records:
            k = self.extract_composite_key(r)
            if not k[5]:  # invalid composite key
                summary.invalid_key_records += 1
                match_results.append(
                    MatchedRecordResult(composite_key=k[:5], key_status=KeyMatchStatus.INVALID_KEY)
                )
            else:
                dataset_index.setdefault(k[:5], []).append(r)

        # Index BTS records by composite key
        bts_index: Dict[Tuple, List[Dict[str, Any]]] = {}
        for r in bts_records:
            k = self.extract_composite_key(r)
            if not k[5]:
                summary.invalid_key_records += 1
                match_results.append(
                    MatchedRecordResult(composite_key=k[:5], key_status=KeyMatchStatus.INVALID_KEY)
                )
            else:
                bts_index.setdefault(k[:5], []).append(r)

        # Deterministically sort keys for reproducible result ordering
        all_keys = sorted(set(dataset_index.keys()).union(set(bts_index.keys())), key=lambda x: tuple(str(e) for e in x))

        for k in all_keys:
            d_list = dataset_index.get(k, [])
            b_list = bts_index.get(k, [])

            if d_list and not b_list:
                summary.unmatched_dataset_records += len(d_list)
                if len(d_list) > 1:
                    summary.ambiguous_duplicate_keys += (len(d_list) - 1)
                match_results.append(
                    MatchedRecordResult(composite_key=k, key_status=KeyMatchStatus.UNMATCHED_IN_BTS)
                )
                continue

            if b_list and not d_list:
                summary.unmatched_bts_records += len(b_list)
                if len(b_list) > 1:
                    summary.ambiguous_duplicate_keys += (len(b_list) - 1)
                match_results.append(
                    MatchedRecordResult(composite_key=k, key_status=KeyMatchStatus.UNMATCHED_IN_DATASET)
                )
                continue

            # Key present on both sides
            if len(d_list) > 1 or len(b_list) > 1:
                # Ambiguous duplicate key (e.g. YX 3624 duplicate pair)
                summary.ambiguous_duplicate_keys += max(len(d_list), len(b_list))
                match_results.append(
                    MatchedRecordResult(composite_key=k, key_status=KeyMatchStatus.AMBIGUOUS_DUPLICATE)
                )
                continue

            # Unique 1-to-1 match
            summary.unique_key_matches += 1
            d_rec = d_list[0]
            b_rec = b_list[0]

            field_comps = {}
            all_match = True

            for core_field, bts_col in CORE_MEASURE_MAPPINGS.items():
                comp = self.compare_single_field(core_field, bts_col, d_rec, b_rec)
                field_comps[core_field] = comp

                stats = summary.field_statistics[core_field]
                if comp.status == MismatchType.EXACT_MATCH:
                    stats["exact_match"] += 1
                    stats["numeric_sample_count"] += 1
                elif comp.status == MismatchType.ROUNDING_DIFF:
                    stats["rounding_diff"] += 1
                    stats["numeric_sample_count"] += 1
                elif comp.status == MismatchType.NULL_NULL_AGREEMENT:
                    stats["null_null_agreement"] += 1
                elif comp.status == MismatchType.SCHEMA_MISSING_COLUMN:
                    stats["missing_column"] += 1
                    stats["mismatch"] += 1
                    all_match = False
                elif comp.status == MismatchType.MALFORMED_NUMERIC_ERROR:
                    stats["malformed_numeric"] += 1
                    stats["mismatch"] += 1
                    all_match = False
                else:
                    stats["mismatch"] += 1
                    all_match = False

            match_results.append(
                MatchedRecordResult(
                    composite_key=k,
                    key_status=KeyMatchStatus.UNIQUE_MATCH,
                    field_comparisons=field_comps,
                    all_fields_match=all_match,
                )
            )

        total_exact = sum(stats["exact_match"] for stats in summary.field_statistics.values())
        total_rounding = sum(stats["rounding_diff"] for stats in summary.field_statistics.values())
        total_mismatch = sum(stats["mismatch"] for stats in summary.field_statistics.values())
        total_missing_col = sum(stats["missing_column"] for stats in summary.field_statistics.values())
        total_malformed = sum(stats["malformed_numeric"] for stats in summary.field_statistics.values())

        has_mismatch = (total_mismatch > 0) or (total_missing_col > 0) or (total_malformed > 0)
        has_unmatched = (summary.unmatched_dataset_records > 0) or (summary.unmatched_bts_records > 0)
        has_ambiguity = summary.ambiguous_duplicate_keys > 0
        has_invalid_keys = summary.invalid_key_records > 0

        # R2-F02: All 7 CORE measures MUST have at least one valid finite numeric observation!
        measures_with_zero_numeric = [
            f_name for f_name, stats in summary.field_statistics.items()
            if stats["numeric_sample_count"] == 0
        ]
        all_seven_measures_have_numeric = len(measures_with_zero_numeric) == 0

        # Check schema validity: no missing columns across the 7 measures
        summary.schema_valid = (total_missing_col == 0) and (summary.total_dataset_records > 0) and (summary.total_bts_records > 0)

        # Full reconciliation success predicate (R3-F05):
        # Requires zero mismatches, positive numeric samples for all 7 measures,
        # zero unmatched records on either side, zero ambiguous duplicates, and zero invalid keys.
        summary.numerical_parity_verified = bool(
            not has_mismatch
            and summary.unique_key_matches > 0
            and all_seven_measures_have_numeric
            and not has_unmatched
            and not has_ambiguity
            and not has_invalid_keys
        )

        # Determine overall verdict (R3-F01, R3-F05, R4-F01)
        is_external_evaluation = is_authentic_bts_data or (provenance_metadata is not None)

        if is_external_evaluation:
            # External BTS reference evaluation (Candidate or Authentic TS-018)
            if summary.numerical_parity_verified:
                # Even with verified numerical parity and valid companion metadata format,
                # authentic acceptance requires Project Lead Human Signoff and certified external source
                if summary.human_accepted and summary.source_provenance_verified:
                    summary.reconciliation_verdict = "TS018_PASS_AUTHENTIC_PARITY_ESTABLISHED"
                    summary.notes.append(
                        "Authentic BTS TranStats parity verified across all 7 CORE measures with zero discrepancies "
                        "under official Project Lead human signoff."
                    )
                elif provenance_metadata is not None and summary.companion_metadata_valid:
                    summary.reconciliation_verdict = "TS018_CANDIDATE_PARITY_VERIFIED_HUMAN_APPROVAL_PENDING"
                    summary.notes.append(
                        "Candidate external BTS reference achieved complete 7-measure numerical parity with zero discrepancies. "
                        "External source provenance authentication and official TS-018 acceptance remain PENDING until Project Lead reviews acquisition evidence and executes human signoff."
                    )
                else:
                    summary.reconciliation_verdict = "SYNTHETIC_RECONCILER_VERIFIED_AUTHENTIC_BTS_PENDING"
                    summary.notes.append(
                        "Reconciler validated numerical parity with zero discrepancies, but candidate provenance metadata is missing or unapproved; "
                        "official TS-018 parity remains PENDING_EXTERNAL_BTS_SOURCE_DELIVERY."
                    )
            else:
                summary.reconciliation_verdict = "TS018_FAIL_DISCREPANCIES_DETECTED"
                summary.notes.append(
                    f"External BTS reconciliation failed: mismatch={total_mismatch}, "
                    f"missing_columns={total_missing_col}, "
                    f"malformed_numerics={total_malformed}, "
                    f"unmatched_dataset={summary.unmatched_dataset_records}, "
                    f"unmatched_bts={summary.unmatched_bts_records}, "
                    f"ambiguous_keys={summary.ambiguous_duplicate_keys}, "
                    f"invalid_keys={summary.invalid_key_records}, "
                    f"measures_with_zero_numeric={measures_with_zero_numeric}"
                )
        else:
            # Pure synthetic fixture evaluation (offline unit/integration testing)
            if summary.numerical_parity_verified:
                summary.reconciliation_verdict = "SYNTHETIC_RECONCILER_VERIFIED_AUTHENTIC_BTS_PENDING"
                summary.notes.append(
                    "Synthetic golden fixtures validated reconciler algorithm across all 7 CORE measures with 0 discrepancies; "
                    "authentic BTS reference remains PENDING_EXTERNAL_BTS_SOURCE_DELIVERY."
                )
            elif summary.unique_key_matches > 0 and not has_mismatch and (has_unmatched or has_ambiguity or has_invalid_keys):
                summary.reconciliation_verdict = "SYNTHETIC_RECONCILER_PARTIAL_MATCH_UNRESOLVED_RECORDS"
                summary.notes.append(
                    f"Partial match achieved ({summary.unique_key_matches} matches), but unresolved records remain: "
                    f"unmatched_dataset={summary.unmatched_dataset_records}, "
                    f"unmatched_bts={summary.unmatched_bts_records}, "
                    f"ambiguous={summary.ambiguous_duplicate_keys}, "
                    f"invalid_keys={summary.invalid_key_records}."
                )
            else:
                summary.reconciliation_verdict = "SYNTHETIC_RECONCILER_FAIL_DISCREPANCIES_DETECTED"
                if not all_seven_measures_have_numeric:
                    summary.notes.append(
                        f"Reconciliation incomplete: {len(measures_with_zero_numeric)}/7 measures have 0 numeric observations: {measures_with_zero_numeric}"
                    )
                if has_mismatch:
                    summary.notes.append(f"Mismatches detected: mismatch={total_mismatch}, missing_columns={total_missing_col}, malformed_numerics={total_malformed}")
                if has_unmatched or has_ambiguity or has_invalid_keys:
                    summary.notes.append(
                        f"Key errors: unmatched_dataset={summary.unmatched_dataset_records}, "
                        f"unmatched_bts={summary.unmatched_bts_records}, "
                        f"ambiguous={summary.ambiguous_duplicate_keys}, invalid_keys={summary.invalid_key_records}"
                    )

        return summary, match_results
