"""
T011-R2 Regression Guard Test Suite.
Verifies that all 5 independent auditor findings (R2-F01..F05) fail closed post-remediation:
- R2-F01: Local unverified CSV without approved provenance fails closed to PENDING / unverified.
- R2-F02: Missing CORE measures are flagged as SCHEMA_MISSING_COLUMN and fail parity.
- R2-F03A: Flight number 0.0 is preserved and not masked by falsy evaluation.
- R2-F03B: Blank date fails composite key validation and is isolated as INVALID_KEY.
- R2-F04: Stale lock enforces FAIL_CLOSED — MANUAL_RECOVERY_REQUIRED and requires governed recovery.
"""

import csv
import json
import os
from pathlib import Path
import platform
import shutil
import sys
import tempfile
import unittest

SRC_DIR = Path(__file__).resolve().parents[1] / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))
ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from flight_pipeline.kpi.bts_reconciler import (
    BtsTranStatsReconciler,
    BtsProvenanceMetadata,
    BtsProvenanceValidator,
    CORE_MEASURE_MAPPINGS,
    MismatchType,
    KeyMatchStatus,
)
from flight_pipeline.storage.locking import SingleWriterLock, LockContentionError, LockError


class TestT011R2RegressionGuards(unittest.TestCase):
    """Permanent regression guards for R2 independent auditor findings."""

    def setUp(self):
        self.test_dir = tempfile.TemporaryDirectory(prefix="t011_r2_guard_")
        self.sandbox = Path(self.test_dir.name)

    def tearDown(self):
        try:
            self.test_dir.cleanup()
        except Exception:
            pass

    def test_guard_r2_f01_local_file_without_provenance_fails_closed(self):
        """
        R2-F01 Guard: Proves that caller boolean is_authentic_bts_data=True without
        official Project Lead provenance metadata CANNOT grant TS018_PASS_AUTHENTIC_PARITY_ESTABLISHED.
        """
        reconciler = BtsTranStatsReconciler(tolerance=1e-4)

        local_target = [
            {
                "FL_DATE": "2018-05-10", "OP_CARRIER": "AA", "OP_CARRIER_FL_NUM": 101.0, "ORIGIN": "DFW", "DEST": "ORD",
                "ARR_DELAY": -15.0, "DEP_DELAY": -5.0, "TAXI_OUT": 18.0, "TAXI_IN": 7.0,
                "AIR_TIME": 115.0, "ACTUAL_ELAPSED_TIME": 140.0, "CRS_ELAPSED_TIME": 150.0,
            }
        ]
        local_fake_bts = [
            {
                "FlightDate": "2018-05-10", "Reporting_Airline": "AA", "Flight_Number_Reporting_Airline": 101, "Origin": "DFW", "Dest": "ORD",
                "ArrDelay": -15.0, "DepDelay": -5.0, "TaxiOut": 18.0, "TaxiIn": 7.0,
                "AirTime": 115.0, "ActualElapsedTime": 140.0, "CRSElapsedTime": 150.0,
            }
        ]

        # Passing is_authentic_bts_data=True without approved provenance must FAIL CLOSED
        summary, _ = reconciler.reconcile(local_target, local_fake_bts, provenance_metadata=None, is_authentic_bts_data=True)

        self.assertFalse(summary.source_provenance_verified)
        self.assertNotEqual(summary.reconciliation_verdict, "TS018_PASS_AUTHENTIC_PARITY_ESTABLISHED")
        self.assertEqual(summary.reconciliation_verdict, "SYNTHETIC_RECONCILER_VERIFIED_AUTHENTIC_BTS_PENDING")

    def test_guard_r2_f02_missing_measures_fail_closed(self):
        """
        R2-F02 Guard: Proves that when 6 of the 7 measures are omitted from schema,
        they are detected as SCHEMA_MISSING_COLUMN and fail parity verification.
        """
        reconciler = BtsTranStatsReconciler(tolerance=1e-4)

        target_records = [
            {
                "FL_DATE": "2018-05-10", "OP_CARRIER": "AA", "OP_CARRIER_FL_NUM": 101.0, "ORIGIN": "DFW", "DEST": "ORD",
                "ARR_DELAY": 10.0,
            }
        ]
        bts_records = [
            {
                "FlightDate": "2018-05-10", "Reporting_Airline": "AA", "Flight_Number_Reporting_Airline": 101, "Origin": "DFW", "Dest": "ORD",
                "ArrDelay": 10.0,
            }
        ]

        summary, results = reconciler.reconcile(target_records, bts_records, is_authentic_bts_data=False)

        # Missing measures are flagged as missing_column, NOT null_null_agreement
        taxi_in_stats = summary.field_statistics["TAXI_IN"]
        self.assertEqual(taxi_in_stats["missing_column"], 1)
        self.assertEqual(taxi_in_stats["null_null_agreement"], 0)
        self.assertFalse(summary.schema_valid)
        self.assertFalse(summary.numerical_parity_verified)
        self.assertEqual(summary.reconciliation_verdict, "SYNTHETIC_RECONCILER_FAIL_DISCREPANCIES_DETECTED")

    def test_guard_r2_f03a_flight_number_zero_preserved(self):
        """
        R2-F03A Guard: Proves that numerical zero flight number (0 or 0.0) is preserved as 0.0
        and not masked by secondary aliases.
        """
        reconciler = BtsTranStatsReconciler(tolerance=1e-4)
        rec = {
            "FL_DATE": "2018-05-10",
            "OP_CARRIER": "AA",
            "OP_CARRIER_FL_NUM": 0,
            "Flight_Number_Reporting_Airline": 999,
            "ORIGIN": "DFW",
            "DEST": "ORD",
        }
        k = reconciler.extract_composite_key(rec)
        self.assertEqual(k[2], 0.0, "Flight number zero must be preserved as 0.0")
        self.assertNotEqual(k[2], 999.0, "Flight number zero must not fall back to alias")
        self.assertTrue(k[5], "Composite key with flight number 0.0 must be valid")

    def test_guard_r2_f03b_blank_date_fails_closed(self):
        """
        R2-F03B Guard: Proves that blank/empty FL_DATE fails key validation (k[5] is False)
        and cannot match another blank date.
        """
        reconciler = BtsTranStatsReconciler(tolerance=1e-4)
        target = [{"FL_DATE": "", "OP_CARRIER": "AA", "OP_CARRIER_FL_NUM": 101.0, "ORIGIN": "DFW", "DEST": "ORD", "ARR_DELAY": 0.0}]
        bts = [{"FlightDate": "", "Reporting_Airline": "AA", "Flight_Number_Reporting_Airline": 101, "Origin": "DFW", "Dest": "ORD", "ArrDelay": 0.0}]

        summary, results = reconciler.reconcile(target, bts, is_authentic_bts_data=False)
        self.assertEqual(summary.unique_key_matches, 0)
        self.assertEqual(summary.invalid_key_records, 2)
        self.assertEqual(results[0].key_status, KeyMatchStatus.INVALID_KEY)

    def test_guard_r2_f04_stale_lock_governance_invariant_and_recovery(self):
        """
        R2-F04 Guard: Proves that locking.py enforces FAIL_CLOSED — MANUAL_RECOVERY_REQUIRED on dead PID,
        and governed recovery succeeds via break_stale_lock(force=True).
        """
        lock_dir = self.sandbox / "locks"
        lock_dir.mkdir(parents=True, exist_ok=True)
        stale_lock = lock_dir / "pipeline.lock"

        from flight_pipeline.storage.locking import LockMetadata
        stale_meta = LockMetadata(
            owner_token="old-token",
            run_id="crashed-run",
            pid=999999,
            hostname=platform.node(),
            created_at="2026-01-01T00:00:00Z",
        )
        stale_lock.write_text(stale_meta.to_json(), encoding="utf-8")

        lock = SingleWriterLock(lock_dir=str(lock_dir), run_id="new-run", lock_filename="pipeline.lock")
        with self.assertRaises(LockContentionError) as ctx:
            lock.acquire()

        self.assertIn("FAIL_CLOSED — MANUAL_RECOVERY_REQUIRED", str(ctx.exception))

        # Recovery without force=True fails closed
        with self.assertRaises(LockError):
            lock.break_stale_lock(force=False)

        # Governed recovery with explicit force=True succeeds
        recovered = lock.break_stale_lock(force=True)
        self.assertTrue(recovered)
        self.assertFalse(stale_lock.exists())

        # Governed writer can now acquire cleanly
        lock.acquire()
        self.assertTrue(lock.is_acquired)
        lock.release()


if __name__ == "__main__":
    unittest.main()
