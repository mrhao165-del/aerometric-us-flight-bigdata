"""
Standalone QA runner for TS-018 BTS TranStats Parity Verification (G2-EXC-001).
Conforms to Master Execution Prompt T-011 and T011-R2 remediation requirements.
Executes reconciler with strict provenance validation and fail-closed 7-field verification.
Generates canonical machine-readable JSON summary separating the 5 governance states:
1. FILE_PRESENT
2. SCHEMA_VALID
3. SOURCE_PROVENANCE_VERIFIED
4. NUMERICAL_PARITY_VERIFIED
5. HUMAN_ACCEPTED
"""

import csv
import hashlib
import json
import os
from pathlib import Path
import sys
from typing import List, Dict, Any, Tuple, Optional

SRC_DIR = Path(__file__).resolve().parents[2] / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))
ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from flight_pipeline.kpi.bts_reconciler import (
    BtsTranStatsReconciler,
    BtsProvenanceMetadata,
    BtsProvenanceValidator,
    CORE_MEASURE_MAPPINGS,
)


def compute_sha256(file_path: Path) -> str:
    """Compute streaming SHA-256 checksum of a file."""
    h = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def read_bts_csv(file_path: Path) -> Tuple[List[Dict[str, Any]], str]:
    """
    Read and validate an external BTS TranStats CSV reference file.
    Returns parsed records and SHA-256 digest.
    Raises ValueError on schema or formatting violation.
    """
    digest = compute_sha256(file_path)
    records: List[Dict[str, Any]] = []

    with open(file_path, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            raise ValueError(f"Empty or headerless CSV file: {file_path}")

        field_set = set(reader.fieldnames)
        required_key_cols = {"FlightDate", "Reporting_Airline", "Flight_Number_Reporting_Airline", "Origin", "Dest"}
        alt_key_cols = {"FL_DATE", "OP_CARRIER", "OP_CARRIER_FL_NUM", "ORIGIN", "DEST"}

        if not (required_key_cols.issubset(field_set) or alt_key_cols.issubset(field_set)):
            raise ValueError(f"Missing required BTS key columns in {file_path}. Header: {reader.fieldnames}")

        for row in reader:
            records.append(dict(row))

    return records, digest


def load_companion_provenance(csv_path: Path) -> Optional[BtsProvenanceMetadata]:
    """
    Attempt to load approved provenance metadata companion file.
    Follows pattern: {name}.provenance.json in the same directory.
    """
    prov_path = csv_path.with_name(f"{csv_path.stem}.provenance.json")
    if not prov_path.is_file():
        # Also check directory-level provenance manifest
        dir_prov = csv_path.parent / "BTS_PROVENANCE_MANIFEST.json"
        if dir_prov.is_file():
            prov_path = dir_prov
        else:
            return None

    try:
        data = json.loads(prov_path.read_text(encoding="utf-8"))
        return BtsProvenanceMetadata(**data)
    except Exception as e:
        print(f"[WARN] Failed to parse provenance metadata at {prov_path}: {e}")
        return None


def run_ts018_reconciliation() -> int:
    print("=" * 80)
    print("RUNNING TS-018 BTS TRANSTATS SAMPLE PARITY & RECONCILIATION AUDIT (R4)")
    print("=" * 80)

    # 1. Search for authentic BTS TranStats reference files in repository
    bts_search_paths = [
        ROOT_DIR / "docs" / "05-evidence" / "inputs" / "bts_transtats_sample.csv",
        ROOT_DIR / "data" / "reference" / "bts_transtats_sample.csv",
        ROOT_DIR / "data" / "raw" / "bts_sample.csv",
    ]

    candidate_bts_file = None
    for p in bts_search_paths:
        if p.exists() and p.is_file() and p.stat().st_size > 0:
            candidate_bts_file = p
            break

    reconciler = BtsTranStatsReconciler(tolerance=1e-4)
    provenance_meta: Optional[BtsProvenanceMetadata] = None

    if candidate_bts_file is not None:
        print(f"[INFO] Discovered external BTS reference candidate file: {candidate_bts_file}")
        try:
            bts_records, bts_sha256 = read_bts_csv(candidate_bts_file)
            print(f"[INFO] Parsed {len(bts_records)} records from {candidate_bts_file} (SHA-256: {bts_sha256})")

            # Check provenance metadata companion (R2-F01, R3-F01 guard)
            provenance_meta = load_companion_provenance(candidate_bts_file)
            if provenance_meta is not None:
                print(f"[PROVENANCE] Loaded companion provenance metadata: declared_hash='{provenance_meta.sha256_hash}', approval_status='{provenance_meta.project_lead_approval_status}'")
            else:
                print(f"[PROVENANCE] Candidate file found but NO companion provenance metadata. Status: PROVENANCE_UNVERIFIED.")

            # Load dataset candidate sample
            dataset_candidate_path = ROOT_DIR / "docs" / "05-evidence" / "inputs" / "dataset_candidate_sample.csv"
            if dataset_candidate_path.exists() and dataset_candidate_path.stat().st_size > 0:
                with open(dataset_candidate_path, "r", encoding="utf-8-sig") as f:
                    dataset_records = list(csv.DictReader(f))
            else:
                dataset_records = []

        except Exception as e:
            print(f"[ERROR] Failed to read or parse candidate BTS reference file: {e}")
            return 2
    else:
        print("[AUDIT] No candidate external BTS TranStats sample CSV found in repository.")
        print("[AUDIT] Executing algorithmic reconciliation verification on synthetic golden fixtures...")

        # Controlled golden fixture covering all 7 CORE measures and edge cases
        dataset_records = [
            {
                "FL_DATE": "2018-05-10", "OP_CARRIER": "AA", "OP_CARRIER_FL_NUM": 101.0, "ORIGIN": "DFW", "DEST": "ORD",
                "ARR_DELAY": -15.0, "DEP_DELAY": -5.0, "TAXI_OUT": 18.0, "TAXI_IN": 7.0,
                "AIR_TIME": 115.0, "ACTUAL_ELAPSED_TIME": 140.0, "CRS_ELAPSED_TIME": 150.0,
            },
            {
                "FL_DATE": "2018-05-10", "OP_CARRIER": "DL", "OP_CARRIER_FL_NUM": 202.0, "ORIGIN": "ATL", "DEST": "LGA",
                "ARR_DELAY": 45.0, "DEP_DELAY": 50.0, "TAXI_OUT": 25.0, "TAXI_IN": 10.0,
                "AIR_TIME": 105.0, "ACTUAL_ELAPSED_TIME": 140.0, "CRS_ELAPSED_TIME": 135.0,
            },
            {
                "FL_DATE": "2018-05-10", "OP_CARRIER": "UA", "OP_CARRIER_FL_NUM": 303.0, "ORIGIN": "DEN", "DEST": "SFO",
                "ARR_DELAY": 0.0, "DEP_DELAY": 0.0, "TAXI_OUT": 15.0, "TAXI_IN": 8.0,
                "AIR_TIME": 130.0, "ACTUAL_ELAPSED_TIME": 153.0, "CRS_ELAPSED_TIME": 153.0,
            },
            # Edge case: Flight with 0.0 flight number (R2-F03)
            {
                "FL_DATE": "2018-05-10", "OP_CARRIER": "WN", "OP_CARRIER_FL_NUM": 0.0, "ORIGIN": "MDW", "DEST": "BWI",
                "ARR_DELAY": 5.0, "DEP_DELAY": 2.0, "TAXI_OUT": 12.0, "TAXI_IN": 6.0,
                "AIR_TIME": 90.0, "ACTUAL_ELAPSED_TIME": 108.0, "CRS_ELAPSED_TIME": 105.0,
            },
            # Single YX 3624 flight (matches BTS fixture)
            {
                "FL_DATE": "2018-05-10", "OP_CARRIER": "YX", "OP_CARRIER_FL_NUM": 3624.0, "ORIGIN": "LGA", "DEST": "BOS",
                "ARR_DELAY": 10.0, "DEP_DELAY": 5.0, "TAXI_OUT": 15.0, "TAXI_IN": 5.0,
                "AIR_TIME": 45.0, "ACTUAL_ELAPSED_TIME": 65.0, "CRS_ELAPSED_TIME": 60.0,
            },
        ]

        bts_records = [
            {
                "FlightDate": "2018-05-10", "Reporting_Airline": "AA", "Flight_Number_Reporting_Airline": 101, "Origin": "DFW", "Dest": "ORD",
                "ArrDelay": -15.0, "DepDelay": -5.0, "TaxiOut": 18.0, "TaxiIn": 7.0,
                "AirTime": 115.0, "ActualElapsedTime": 140.0, "CRSElapsedTime": 150.0,
            },
            {
                "FlightDate": "2018-05-10", "Reporting_Airline": "DL", "Flight_Number_Reporting_Airline": 202, "Origin": "ATL", "Dest": "LGA",
                "ArrDelay": 45.0, "DepDelay": 50.0, "TaxiOut": 25.0, "TaxiIn": 10.0,
                "AirTime": 105.0, "ActualElapsedTime": 140.0, "CRSElapsedTime": 135.0,
            },
            {
                "FlightDate": "2018-05-10", "Reporting_Airline": "UA", "Flight_Number_Reporting_Airline": 303, "Origin": "DEN", "Dest": "SFO",
                "ArrDelay": 0.0, "DepDelay": 0.0, "TaxiOut": 15.0, "TaxiIn": 8.0,
                "AirTime": 130.0, "ActualElapsedTime": 153.0, "CRSElapsedTime": 153.0,
            },
            {
                "FlightDate": "2018-05-10", "Reporting_Airline": "WN", "Flight_Number_Reporting_Airline": 0, "Origin": "MDW", "Dest": "BWI",
                "ArrDelay": 5.0, "DepDelay": 2.0, "TaxiOut": 12.0, "TaxiIn": 6.0,
                "AirTime": 90.0, "ActualElapsedTime": 108.0, "CRSElapsedTime": 105.0,
            },
            {
                "FlightDate": "2018-05-10", "Reporting_Airline": "YX", "Flight_Number_Reporting_Airline": 3624, "Origin": "LGA", "Dest": "BOS",
                "ArrDelay": 10.0, "DepDelay": 5.0, "TaxiOut": 15.0, "TaxiIn": 5.0,
                "AirTime": 45.0, "ActualElapsedTime": 65.0, "CRSElapsedTime": 60.0,
            },
        ]

    # Reconcile with provenance gating
    actual_sha = bts_sha256 if candidate_bts_file is not None else None
    summary, results = reconciler.reconcile(
        dataset_records,
        bts_records,
        provenance_metadata=provenance_meta,
        actual_bts_sha256=actual_sha,
        is_authentic_bts_data=(provenance_meta is not None and candidate_bts_file is not None),
    )

    print(f"[SUMMARY] Total Dataset Records: {summary.total_dataset_records}")
    print(f"[SUMMARY] Total BTS Records: {summary.total_bts_records}")
    print(f"[SUMMARY] Unique Key Matches: {summary.unique_key_matches}")
    print(f"[SUMMARY] Ambiguous Duplicate Keys: {summary.ambiguous_duplicate_keys}")
    print(f"[SUMMARY] Invalid Key Records: {summary.invalid_key_records}")
    print(f"[SUMMARY] Unmatched Dataset Records: {summary.unmatched_dataset_records}")
    print(f"[SUMMARY] Unmatched BTS Records: {summary.unmatched_bts_records}")
    print("=" * 40)
    print("SEPARATION OF GOVERNANCE STATES (R4-F01):")
    print(f"  1. FILE_PRESENT:                 {summary.file_present}")
    print(f"  2. SCHEMA_VALID:                  {summary.schema_valid}")
    print(f"  3. COMPANION_METADATA_VALID:      {summary.companion_metadata_valid}")
    print(f"  4. CANDIDATE_CHECKSUM_MATCHED:    {summary.candidate_checksum_matched}")
    print(f"  5. SOURCE_PROVENANCE_VERIFIED:    {summary.source_provenance_verified} (CANNOT_SELF_VERIFY_LOCAL_CLAIMS)")
    print(f"  6. NUMERICAL_PARITY_VERIFIED:     {summary.numerical_parity_verified}")
    print(f"  7. HUMAN_ACCEPTED:                {summary.human_accepted} (EXCLUSIVE: Project Lead)")
    print("=" * 40)
    print(f"[SUMMARY] Reconciliation Verdict: {summary.reconciliation_verdict}")

    for f_name, stats in summary.field_statistics.items():
        print(f"  Field {f_name:20s}: exact={stats['exact_match']}, round={stats['rounding_diff']}, numeric_samples={stats['numeric_sample_count']}, null_null={stats['null_null_agreement']}, mismatch={stats['mismatch']}, missing_col={stats['missing_column']}, malformed={stats['malformed_numeric']}")

    # Output machine-readable JSON summary
    out_json = ROOT_DIR / "docs" / "05-evidence" / "T011_TS018_BTS_RECONCILIATION_SUMMARY.json"
    out_json.parent.mkdir(parents=True, exist_ok=True)
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(summary.to_dict(), f, indent=2)

    print(f"[ARTIFACT] Machine-readable summary written to: {out_json}")
    print("=" * 80)

    # Fail-closed exit code semantics:
    # Exit 0: Authentic parity established OR synthetic validation passed with authentic source pending
    #         OR candidate external BTS evidence verified numerically, awaiting human signoff.
    # Exit 1: Discrepancies, mismatches, or false-pass conditions detected.
    if summary.reconciliation_verdict in (
        "TS018_PASS_AUTHENTIC_PARITY_ESTABLISHED",
        "SYNTHETIC_RECONCILER_VERIFIED_AUTHENTIC_BTS_PENDING",
        "TS018_CANDIDATE_PARITY_VERIFIED_HUMAN_APPROVAL_PENDING",
    ):
        return 0
    else:
        print(f"[FAIL-CLOSED] Reconciliation failed with verdict: {summary.reconciliation_verdict}")
        return 1


if __name__ == "__main__":
    sys.exit(run_ts018_reconciliation())
