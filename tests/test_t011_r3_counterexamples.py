"""
tests/test_t011_r3_counterexamples.py
------------------------------------
Authoritative Regression and Counterexample Test Suite for T-011 R3.
Permanently guards against residual auditor defects R3-F01 through R3-F05:

- R3-F01: Provenance trust boundary, declared SHA-256 preservation, and anti-self-approval.
- R3-F02: Numeric parsing and null distinction (malformed strings and non-finites are discrepancies).
- R3-F03: Lock recovery fail-closed for unparseable, empty, or incomplete lock files.
- R3-F04: Gregorian calendar date validation in composite key extraction.
- R3-F05: Synthetic parity complete matching predicate (0 unmatched, 0 ambiguous, 0 invalid).
"""

import json
from pathlib import Path
import sys
import tempfile
import unittest

SRC_DIR = Path(__file__).resolve().parents[1] / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from flight_pipeline.kpi.bts_reconciler import (
    BtsTranStatsReconciler,
    BtsProvenanceMetadata,
    BtsProvenanceValidator,
    CORE_MEASURE_MAPPINGS,
    MismatchType,
    KeyMatchStatus,
    NumericParseStatus,
)
from flight_pipeline.storage.locking import SingleWriterLock, LockContentionError


class TestT011R3ProvenanceTrustBoundary(unittest.TestCase):
    """Guards for R3-F01: Provenance trust boundary and anti-self-approval."""

    def setUp(self):
        self.reconciler = BtsTranStatsReconciler(tolerance=1e-4)
        self.valid_sha = "a" * 64
        self.valid_dataset = [{
            "FL_DATE": "2018-05-10", "OP_CARRIER": "AA", "OP_CARRIER_FL_NUM": 101.0,
            "ORIGIN": "DFW", "DEST": "ORD",
            "ARR_DELAY": 10.0, "DEP_DELAY": 5.0, "TAXI_OUT": 15.0, "TAXI_IN": 5.0,
            "AIR_TIME": 100.0, "ACTUAL_ELAPSED_TIME": 120.0, "CRS_ELAPSED_TIME": 125.0
        }]
        self.valid_bts = [{
            "FlightDate": "2018-05-10", "Reporting_Airline": "AA", "Flight_Number_Reporting_Airline": 101,
            "Origin": "DFW", "Dest": "ORD",
            "ArrDelay": 10.0, "DepDelay": 5.0, "TaxiOut": 15.0, "TaxiIn": 5.0,
            "AirTime": 100.0, "ActualElapsedTime": 120.0, "CRSElapsedTime": 125.0
        }]

    def test_r3_f01_scenario_01_no_provenance_with_authentic_flag(self):
        """Scenario 1: Caller sets is_authentic_bts_data=True without provenance."""
        summary, _ = self.reconciler.reconcile(
            self.valid_dataset, self.valid_bts,
            provenance_metadata=None,
            is_authentic_bts_data=True
        )
        self.assertFalse(summary.source_provenance_verified)
        self.assertFalse(summary.human_accepted)
        self.assertNotEqual(summary.reconciliation_verdict, "TS018_PASS_AUTHENTIC_PARITY_ESTABLISHED")
        self.assertEqual(summary.reconciliation_verdict, "SYNTHETIC_RECONCILER_VERIFIED_AUTHENTIC_BTS_PENDING")

    def test_r3_f01_scenario_02_not_external_reference(self):
        """Scenario 2: is_external_reference=False must fail provenance."""
        prov = BtsProvenanceMetadata(
            project_lead_approval_status="APPROVED_BY_PROJECT_LEAD",
            approval_record_ref="DECISION_20261019_PL_BTS_SAMPLE",
            is_external_reference=False,
            sha256_hash=self.valid_sha,
        )
        ok, msg = BtsProvenanceValidator.validate_provenance(prov, self.valid_sha)
        self.assertFalse(ok)
        self.assertIn("PROVENANCE_NOT_EXTERNAL", msg)

    def test_r3_f01_scenario_03_empty_sha256(self):
        """Scenario 3: Empty sha256_hash must fail provenance."""
        prov = BtsProvenanceMetadata(
            project_lead_approval_status="APPROVED_BY_PROJECT_LEAD",
            approval_record_ref="DECISION_20261019_PL_BTS_SAMPLE",
            is_external_reference=True,
            sha256_hash="",
        )
        ok, msg = BtsProvenanceValidator.validate_provenance(prov, self.valid_sha)
        self.assertFalse(ok)
        self.assertIn("PROVENANCE_MALFORMED_HASH", msg)

    def test_r3_f01_scenario_04_short_sha256(self):
        """Scenario 4: Non-64 char sha256_hash must fail provenance."""
        prov = BtsProvenanceMetadata(
            project_lead_approval_status="APPROVED_BY_PROJECT_LEAD",
            approval_record_ref="DECISION_20261019_PL_BTS_SAMPLE",
            is_external_reference=True,
            sha256_hash="bad_short_hash",
        )
        ok, msg = BtsProvenanceValidator.validate_provenance(prov, self.valid_sha)
        self.assertFalse(ok)
        self.assertIn("PROVENANCE_MALFORMED_HASH", msg)

    def test_r3_f01_scenario_05_hash_mismatch_with_actual(self):
        """Scenario 5: Declared hash differs from actual file hash."""
        prov = BtsProvenanceMetadata(
            project_lead_approval_status="APPROVED_BY_PROJECT_LEAD",
            approval_record_ref="DECISION_20261019_PL_BTS_SAMPLE",
            is_external_reference=True,
            sha256_hash="b" * 64,
        )
        ok, msg = BtsProvenanceValidator.validate_provenance(prov, self.valid_sha)
        self.assertFalse(ok)
        self.assertIn("PROVENANCE_HASH_MISMATCH", msg)

    def test_r3_f01_scenario_06_unapproved_status_pending(self):
        """Scenario 6: Approval status is PENDING_APPROVAL."""
        prov = BtsProvenanceMetadata(
            project_lead_approval_status="PENDING_APPROVAL",
            approval_record_ref="DECISION_20261019_PL_BTS_SAMPLE",
            is_external_reference=True,
            sha256_hash=self.valid_sha,
        )
        ok, msg = BtsProvenanceValidator.validate_provenance(prov, self.valid_sha)
        self.assertFalse(ok)
        self.assertIn("PROVENANCE_UNAPPROVED", msg)

    def test_r3_f01_scenario_07_unapproved_status_self_approved(self):
        """Scenario 7: Approval status is SELF_APPROVED."""
        prov = BtsProvenanceMetadata(
            project_lead_approval_status="SELF_APPROVED",
            approval_record_ref="DECISION_20261019_PL_BTS_SAMPLE",
            is_external_reference=True,
            sha256_hash=self.valid_sha,
        )
        ok, msg = BtsProvenanceValidator.validate_provenance(prov, self.valid_sha)
        self.assertFalse(ok)
        self.assertIn("PROVENANCE_UNAPPROVED", msg)

    def test_r3_f01_scenario_08_unapproved_status_agent_approved(self):
        """Scenario 8: Approval status is APPROVED_BY_AI_AGENT."""
        prov = BtsProvenanceMetadata(
            project_lead_approval_status="APPROVED_BY_AI_AGENT",
            approval_record_ref="DECISION_20261019_PL_BTS_SAMPLE",
            is_external_reference=True,
            sha256_hash=self.valid_sha,
        )
        ok, msg = BtsProvenanceValidator.validate_provenance(prov, self.valid_sha)
        self.assertFalse(ok)
        self.assertIn("PROVENANCE_UNAPPROVED", msg)

    def test_r3_f01_scenario_09_missing_approval_record_ref_empty(self):
        """Scenario 9: approval_record_ref is empty."""
        prov = BtsProvenanceMetadata(
            project_lead_approval_status="APPROVED_BY_PROJECT_LEAD",
            approval_record_ref="",
            is_external_reference=True,
            sha256_hash=self.valid_sha,
        )
        ok, msg = BtsProvenanceValidator.validate_provenance(prov, self.valid_sha)
        self.assertFalse(ok)
        self.assertIn("PROVENANCE_MISSING_APPROVAL_REF", msg)

    def test_r3_f01_scenario_10_missing_approval_record_ref_whitespace(self):
        """Scenario 10: approval_record_ref is whitespace."""
        prov = BtsProvenanceMetadata(
            project_lead_approval_status="APPROVED_BY_PROJECT_LEAD",
            approval_record_ref="   ",
            is_external_reference=True,
            sha256_hash=self.valid_sha,
        )
        ok, msg = BtsProvenanceValidator.validate_provenance(prov, self.valid_sha)
        self.assertFalse(ok)
        self.assertIn("PROVENANCE_MISSING_APPROVAL_REF", msg)

    def test_r3_f01_scenario_11_candidate_parity_requires_human_signoff(self):
        """Scenario 11: Valid provenance format yields candidate approval pending, NEVER authentic pass."""
        prov = BtsProvenanceMetadata(
            project_lead_approval_status="APPROVED_BY_PROJECT_LEAD",
            approval_record_ref="DECISION_20261019_PL_BTS_SAMPLE",
            is_external_reference=True,
            sha256_hash=self.valid_sha,
        )
        summary, _ = self.reconciler.reconcile(
            self.valid_dataset, self.valid_bts,
            provenance_metadata=prov,
            actual_bts_sha256=self.valid_sha,
            is_authentic_bts_data=True
        )
        self.assertFalse(summary.source_provenance_verified)
        self.assertTrue(summary.companion_metadata_valid)
        self.assertTrue(summary.candidate_checksum_matched)
        self.assertFalse(summary.human_accepted)
        self.assertEqual(summary.reconciliation_verdict, "TS018_CANDIDATE_PARITY_VERIFIED_HUMAN_APPROVAL_PENDING")
        self.assertNotEqual(summary.reconciliation_verdict, "TS018_PASS_AUTHENTIC_PARITY_ESTABLISHED")

    def test_r3_f01_scenario_12_no_hash_overwrite_in_validator(self):
        """Scenario 12: Declared hash is strictly verified against actual without modification."""
        prov = BtsProvenanceMetadata(
            project_lead_approval_status="APPROVED_BY_PROJECT_LEAD",
            approval_record_ref="DECISION_20261019_PL_BTS_SAMPLE",
            is_external_reference=True,
            sha256_hash="c" * 64,
        )
        summary, _ = self.reconciler.reconcile(
            self.valid_dataset, self.valid_bts,
            provenance_metadata=prov,
            actual_bts_sha256="d" * 64,
            is_authentic_bts_data=True
        )
        self.assertFalse(summary.source_provenance_verified)
        self.assertEqual(prov.sha256_hash, "c" * 64)


class TestT011R3NumericIntegrity(unittest.TestCase):
    """Guards for R3-F02: Numeric parsing and null distinction."""

    def setUp(self):
        self.reconciler = BtsTranStatsReconciler(tolerance=1e-4)
        self.base_d = {
            "FL_DATE": "2018-05-10", "OP_CARRIER": "AA", "OP_CARRIER_FL_NUM": 101.0, "ORIGIN": "DFW", "DEST": "ORD",
            "ARR_DELAY": 10.0, "DEP_DELAY": 5.0, "TAXI_OUT": 15.0, "TAXI_IN": 5.0,
            "AIR_TIME": 100.0, "ACTUAL_ELAPSED_TIME": 120.0, "CRS_ELAPSED_TIME": 125.0
        }
        self.base_b = {
            "FlightDate": "2018-05-10", "Reporting_Airline": "AA", "Flight_Number_Reporting_Airline": 101, "Origin": "DFW", "Dest": "ORD",
            "ArrDelay": 10.0, "DepDelay": 5.0, "TaxiOut": 15.0, "TaxiIn": 5.0,
            "AirTime": 100.0, "ActualElapsedTime": 120.0, "CRSElapsedTime": 125.0
        }

    def test_r3_f02_malformed_string_vs_malformed_string(self):
        """Case 1: 'invalidXYZ' vs 'invalidABC' triggers MALFORMED_NUMERIC_ERROR, not NULL_NULL_AGREEMENT."""
        d = dict(self.base_d)
        d["ARR_DELAY"] = "invalidXYZ"
        b = dict(self.base_b)
        b["ArrDelay"] = "invalidABC"

        comp = self.reconciler.compare_single_field("ARR_DELAY", "ArrDelay", d, b)
        self.assertEqual(comp.status, MismatchType.MALFORMED_NUMERIC_ERROR)
        self.assertNotEqual(comp.status, MismatchType.NULL_NULL_AGREEMENT)
        self.assertEqual(comp.dataset_parse_status, NumericParseStatus.MALFORMED_NUMBER)
        self.assertEqual(comp.bts_parse_status, NumericParseStatus.MALFORMED_NUMBER)

    def test_r3_f02_malformed_string_vs_valid_number(self):
        """Case 2: 'invalidXYZ' vs 10.0 triggers MALFORMED_NUMERIC_ERROR."""
        d = dict(self.base_d)
        d["ARR_DELAY"] = "invalidXYZ"
        b = dict(self.base_b)
        b["ArrDelay"] = 10.0

        comp = self.reconciler.compare_single_field("ARR_DELAY", "ArrDelay", d, b)
        self.assertEqual(comp.status, MismatchType.MALFORMED_NUMERIC_ERROR)

    def test_r3_f02_string_nan_vs_string_nan(self):
        """Case 3: 'NaN' vs 'NaN' triggers MALFORMED_NUMERIC_ERROR (non-finite)."""
        d = dict(self.base_d)
        d["ARR_DELAY"] = "NaN"
        b = dict(self.base_b)
        b["ArrDelay"] = "nan"

        comp = self.reconciler.compare_single_field("ARR_DELAY", "ArrDelay", d, b)
        self.assertEqual(comp.status, MismatchType.MALFORMED_NUMERIC_ERROR)
        self.assertEqual(comp.dataset_parse_status, NumericParseStatus.NONFINITE_NUMBER)
        self.assertEqual(comp.bts_parse_status, NumericParseStatus.NONFINITE_NUMBER)

    def test_r3_f02_string_inf_vs_string_inf(self):
        """Case 4: 'Infinity' vs '-Infinity' triggers MALFORMED_NUMERIC_ERROR (non-finite)."""
        d = dict(self.base_d)
        d["ARR_DELAY"] = "Infinity"
        b = dict(self.base_b)
        b["ArrDelay"] = "-Inf"

        comp = self.reconciler.compare_single_field("ARR_DELAY", "ArrDelay", d, b)
        self.assertEqual(comp.status, MismatchType.MALFORMED_NUMERIC_ERROR)
        self.assertEqual(comp.dataset_parse_status, NumericParseStatus.NONFINITE_NUMBER)

    def test_r3_f02_float_nan_vs_float_nan(self):
        """Case 5: float('nan') vs float('nan') triggers MALFORMED_NUMERIC_ERROR."""
        d = dict(self.base_d)
        d["ARR_DELAY"] = float("nan")
        b = dict(self.base_b)
        b["ArrDelay"] = float("nan")

        comp = self.reconciler.compare_single_field("ARR_DELAY", "ArrDelay", d, b)
        self.assertEqual(comp.status, MismatchType.MALFORMED_NUMERIC_ERROR)

    def test_r3_f02_approved_null_strings_agree(self):
        """Case 6: Approved null representations ('', 'NA', 'null', 'None', None) yield NULL_NULL_AGREEMENT."""
        for d_null in ["", "NA", "null", "None", None]:
            for b_null in ["", "NA", "null", "None", None]:
                d = dict(self.base_d)
                d["ARR_DELAY"] = d_null
                b = dict(self.base_b)
                b["ArrDelay"] = b_null
                comp = self.reconciler.compare_single_field("ARR_DELAY", "ArrDelay", d, b)
                self.assertEqual(
                    comp.status,
                    MismatchType.NULL_NULL_AGREEMENT,
                    f"Failed for d={d_null!r}, b={b_null!r}"
                )

    def test_r3_f02_null_vs_valid_number(self):
        """Case 7: Null vs valid number yields MISSINGNESS_MISMATCH."""
        d = dict(self.base_d)
        d["ARR_DELAY"] = None
        b = dict(self.base_b)
        b["ArrDelay"] = 10.0

        comp = self.reconciler.compare_single_field("ARR_DELAY", "ArrDelay", d, b)
        self.assertEqual(comp.status, MismatchType.MISSINGNESS_MISMATCH)


class TestT011R3LockRecovery(unittest.TestCase):
    """Guards for R3-F03: Lock recovery fail-closed on unknown ownership."""

    def test_r3_f03_corrupt_lock_raises_fail_closed(self):
        """Case 1: Corrupted non-JSON lock file must raise LockContentionError and NOT be deleted."""
        with tempfile.TemporaryDirectory() as td:
            tdp = Path(td)
            lock_file = tdp / "active_pipeline.lock"
            lock_file.write_text("CORRUPTED_NON_JSON_METADATA", encoding="utf-8")

            lock = SingleWriterLock(lock_dir=str(tdp), run_id="recovery_writer", lock_filename="active_pipeline.lock")
            with self.assertRaises(LockContentionError) as ctx:
                lock.break_stale_lock(force=True)

            self.assertIn("FAIL_CLOSED — MANUAL_RECOVERY_REQUIRED", str(ctx.exception))
            self.assertTrue(lock_file.exists(), "Corrupt lock file MUST NOT be deleted!")

    def test_r3_f03_empty_lock_raises_fail_closed(self):
        """Case 2: 0-byte empty lock file must raise LockContentionError and NOT be deleted."""
        with tempfile.TemporaryDirectory() as td:
            tdp = Path(td)
            lock_file = tdp / "active_pipeline.lock"
            lock_file.write_text("", encoding="utf-8")

            lock = SingleWriterLock(lock_dir=str(tdp), run_id="recovery_writer", lock_filename="active_pipeline.lock")
            with self.assertRaises(LockContentionError) as ctx:
                lock.break_stale_lock(force=True)

            self.assertIn("FAIL_CLOSED — MANUAL_RECOVERY_REQUIRED", str(ctx.exception))
            self.assertTrue(lock_file.exists(), "Empty lock file MUST NOT be deleted!")

    def test_r3_f03_incomplete_json_lock_raises_fail_closed(self):
        """Case 3: JSON lock file missing required fields must raise LockContentionError."""
        with tempfile.TemporaryDirectory() as td:
            tdp = Path(td)
            lock_file = tdp / "active_pipeline.lock"
            lock_file.write_text(json.dumps({"some_key": "some_value"}), encoding="utf-8")

            lock = SingleWriterLock(lock_dir=str(tdp), run_id="recovery_writer", lock_filename="active_pipeline.lock")
            with self.assertRaises(LockContentionError) as ctx:
                lock.break_stale_lock(force=True)

            self.assertIn("FAIL_CLOSED — MANUAL_RECOVERY_REQUIRED", str(ctx.exception))
            self.assertTrue(lock_file.exists(), "Incomplete lock file MUST NOT be deleted!")


class TestT011R3CompositeKeyDate(unittest.TestCase):
    """Guards for R3-F04: Real Gregorian calendar date validation in composite key."""

    def setUp(self):
        self.reconciler = BtsTranStatsReconciler(tolerance=1e-4)

    def test_r3_f04_february_31_rejected(self):
        """Case 1: 2026-02-31 is impossible calendar date."""
        rec = {"FL_DATE": "2026-02-31", "OP_CARRIER": "AA", "OP_CARRIER_FL_NUM": 100.0, "ORIGIN": "JFK", "DEST": "LAX"}
        k = self.reconciler.extract_composite_key(rec)
        self.assertFalse(k[5], "2026-02-31 must be invalid")

    def test_r3_f04_non_leap_february_29_rejected(self):
        """Case 2: 2025-02-29 is non-leap year impossible date."""
        rec = {"FL_DATE": "2025-02-29", "OP_CARRIER": "AA", "OP_CARRIER_FL_NUM": 100.0, "ORIGIN": "JFK", "DEST": "LAX"}
        k = self.reconciler.extract_composite_key(rec)
        self.assertFalse(k[5], "2025-02-29 must be invalid")

    def test_r3_f04_leap_february_29_accepted(self):
        """Case 3: 2024-02-29 is valid leap day."""
        rec = {"FL_DATE": "2024-02-29", "OP_CARRIER": "AA", "OP_CARRIER_FL_NUM": 100.0, "ORIGIN": "JFK", "DEST": "LAX"}
        k = self.reconciler.extract_composite_key(rec)
        self.assertTrue(k[5], "2024-02-29 must be valid")

    def test_r3_f04_april_31_rejected(self):
        """Case 4: 2026-04-31 has invalid day for April (max 30)."""
        rec = {"FL_DATE": "2026-04-31", "OP_CARRIER": "AA", "OP_CARRIER_FL_NUM": 100.0, "ORIGIN": "JFK", "DEST": "LAX"}
        k = self.reconciler.extract_composite_key(rec)
        self.assertFalse(k[5], "2026-04-31 must be invalid")

    def test_r3_f04_month_13_rejected(self):
        """Case 5: 2026-13-01 has invalid month."""
        rec = {"FL_DATE": "2026-13-01", "OP_CARRIER": "AA", "OP_CARRIER_FL_NUM": 100.0, "ORIGIN": "JFK", "DEST": "LAX"}
        k = self.reconciler.extract_composite_key(rec)
        self.assertFalse(k[5], "2026-13-01 must be invalid")

    def test_r3_f04_flight_number_zero_preserved(self):
        """Case 6: Flight number 0.0 or '0' is preserved as valid float 0.0."""
        rec = {"FL_DATE": "2024-02-29", "OP_CARRIER": "AA", "OP_CARRIER_FL_NUM": 0.0, "ORIGIN": "JFK", "DEST": "LAX"}
        k = self.reconciler.extract_composite_key(rec)
        self.assertTrue(k[5])
        self.assertEqual(k[2], 0.0)


class TestT011R3SyntheticReconcilerPredicate(unittest.TestCase):
    """Guards for R3-F05: Synthetic reconciler complete matching predicate."""

    def setUp(self):
        self.reconciler = BtsTranStatsReconciler(tolerance=1e-4)
        self.match_d = {
            "FL_DATE": "2018-05-10", "OP_CARRIER": "AA", "OP_CARRIER_FL_NUM": 101.0, "ORIGIN": "DFW", "DEST": "ORD",
            "ARR_DELAY": 10.0, "DEP_DELAY": 5.0, "TAXI_OUT": 15.0, "TAXI_IN": 5.0,
            "AIR_TIME": 100.0, "ACTUAL_ELAPSED_TIME": 120.0, "CRS_ELAPSED_TIME": 125.0
        }
        self.match_b = {
            "FlightDate": "2018-05-10", "Reporting_Airline": "AA", "Flight_Number_Reporting_Airline": 101, "Origin": "DFW", "Dest": "ORD",
            "ArrDelay": 10.0, "DepDelay": 5.0, "TaxiOut": 15.0, "TaxiIn": 5.0,
            "AirTime": 100.0, "ActualElapsedTime": 120.0, "CRSElapsedTime": 125.0
        }

    def test_r3_f05_unmatched_dataset_record_prevents_pass(self):
        """Case 1: Unmatched record in dataset prevents synthetic verification pass."""
        extra_d = {
            "FL_DATE": "2018-05-10", "OP_CARRIER": "UA", "OP_CARRIER_FL_NUM": 999.0, "ORIGIN": "ORD", "DEST": "SFO",
            "ARR_DELAY": 0.0, "DEP_DELAY": 0.0, "TAXI_OUT": 10.0, "TAXI_IN": 5.0,
            "AIR_TIME": 200.0, "ACTUAL_ELAPSED_TIME": 215.0, "CRS_ELAPSED_TIME": 220.0
        }
        summary, _ = self.reconciler.reconcile([self.match_d, extra_d], [self.match_b], is_authentic_bts_data=False)
        self.assertFalse(summary.numerical_parity_verified)
        self.assertEqual(summary.reconciliation_verdict, "SYNTHETIC_RECONCILER_PARTIAL_MATCH_UNRESOLVED_RECORDS")
        self.assertNotEqual(summary.reconciliation_verdict, "SYNTHETIC_RECONCILER_VERIFIED_AUTHENTIC_BTS_PENDING")

    def test_r3_f05_unmatched_bts_record_prevents_pass(self):
        """Case 2: Unmatched record in BTS prevents synthetic verification pass."""
        extra_b = {
            "FlightDate": "2018-05-10", "Reporting_Airline": "UA", "Flight_Number_Reporting_Airline": 999, "Origin": "ORD", "Dest": "SFO",
            "ArrDelay": 0.0, "DepDelay": 0.0, "TaxiOut": 10.0, "TaxiIn": 5.0,
            "AirTime": 200.0, "ActualElapsedTime": 215.0, "CRSElapsedTime": 220.0
        }
        summary, _ = self.reconciler.reconcile([self.match_d], [self.match_b, extra_b], is_authentic_bts_data=False)
        self.assertFalse(summary.numerical_parity_verified)
        self.assertEqual(summary.reconciliation_verdict, "SYNTHETIC_RECONCILER_PARTIAL_MATCH_UNRESOLVED_RECORDS")

    def test_r3_f05_ambiguous_duplicate_key_prevents_pass(self):
        """Case 3: Duplicate key (YX 3624 style) prevents synthetic verification pass."""
        second_match_d = {
            "FL_DATE": "2018-05-10", "OP_CARRIER": "DL", "OP_CARRIER_FL_NUM": 202.0, "ORIGIN": "ATL", "DEST": "LGA",
            "ARR_DELAY": 20.0, "DEP_DELAY": 10.0, "TAXI_OUT": 12.0, "TAXI_IN": 8.0,
            "AIR_TIME": 110.0, "ACTUAL_ELAPSED_TIME": 130.0, "CRS_ELAPSED_TIME": 135.0
        }
        second_match_b = {
            "FlightDate": "2018-05-10", "Reporting_Airline": "DL", "Flight_Number_Reporting_Airline": 202, "Origin": "ATL", "Dest": "LGA",
            "ArrDelay": 20.0, "DepDelay": 10.0, "TaxiOut": 12.0, "TaxiIn": 8.0,
            "AirTime": 110.0, "ActualElapsedTime": 130.0, "CRSElapsedTime": 135.0
        }
        dup_d = dict(self.match_d)
        # We have 1 clean match (DL) and 1 ambiguous duplicate pair (AA has 2 records in dataset)
        summary, _ = self.reconciler.reconcile(
            [self.match_d, dup_d, second_match_d],
            [self.match_b, second_match_b],
            is_authentic_bts_data=False
        )
        self.assertFalse(summary.numerical_parity_verified)
        self.assertEqual(summary.unique_key_matches, 1)
        self.assertGreater(summary.ambiguous_duplicate_keys, 0)
        self.assertEqual(summary.reconciliation_verdict, "SYNTHETIC_RECONCILER_PARTIAL_MATCH_UNRESOLVED_RECORDS")

    def test_r3_f05_all_records_matched_emits_verified_pending(self):
        """Case 4: Complete matching across all records with 0 discrepancies emits verified pending."""
        summary, _ = self.reconciler.reconcile([self.match_d], [self.match_b], is_authentic_bts_data=False)
        self.assertTrue(summary.numerical_parity_verified)
        self.assertEqual(summary.reconciliation_verdict, "SYNTHETIC_RECONCILER_VERIFIED_AUTHENTIC_BTS_PENDING")


if __name__ == "__main__":
    unittest.main()
