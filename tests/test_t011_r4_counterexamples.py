"""
Comprehensive Unit Test Suite for T011-R4 Final Targeted Safety Closure.

Validates the resolutions of auditor findings R4-F01 through R4-F03:
1. R4-F01 Provenance Trust Boundary (>= 9 test cases)
   - Independent verification of candidate checksum matching vs companion format validity vs external source authentication.
   - Prevention of self-verifying hash fallbacks.
   - Invariant: TS018_PASS_AUTHENTIC_PARITY_ESTABLISHED is unreachable by candidate/agent code.
   - Invariant: human_accepted is unconditionally False in automated execution.

2. R4-F02 Invalid PID Fail-Closed Handling (>= 9 test cases)
   - Strict PID type validation in LockMetadata.__post_init__ (rejects bool, str, float, <= 0).
   - PidLivenessStatus classification via get_pid_liveness.
   - Fail-closed behavior on INVALID_PID and PROCESS_STATUS_UNKNOWN in break_stale_lock.

3. R4-F03 Lock Replacement Race Prevention (>= 8 test cases)
   - Double-checked verification immediately prior to unlink in break_stale_lock and release.
   - Pre-unlink hook simulation of concurrent file replacement / deletion.
   - Preservation of replacement locks under all race conditions.
"""

import json
import os
from pathlib import Path
import platform
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
    ReconciliationSummary,
)
from flight_pipeline.storage.locking import (
    DuplicateRunIdError,
    LockContentionError,
    LockError,
    LockMetadata,
    LockOwnerMismatchError,
    PidLivenessStatus,
    SingleWriterLock,
    get_pid_liveness,
    is_pid_alive,
)


class TestT011R4ProvenanceTrustBoundary(unittest.TestCase):
    """Guards for R4-F01: External provenance trust boundary and disaggregated validation."""

    def setUp(self):
        self.reconciler = BtsTranStatsReconciler(tolerance=1e-4)
        self.valid_sha = "a" * 64
        self.valid_dataset = [{
            "FL_DATE": "2018-05-10", "OP_CARRIER": "AA", "OP_CARRIER_FL_NUM": 101.0,
            "ORIGIN": "DFW", "DEST": "ORD", "ARR_DELAY": 10.0, "DEP_DELAY": 5.0,
            "TAXI_OUT": 15.0, "TAXI_IN": 5.0, "AIR_TIME": 100.0,
            "ACTUAL_ELAPSED_TIME": 120.0, "CRS_ELAPSED_TIME": 125.0
        }]
        self.valid_bts = [{
            "FlightDate": "2018-05-10", "Reporting_Airline": "AA",
            "Flight_Number_Reporting_Airline": 101, "Origin": "DFW", "Dest": "ORD",
            "ArrDelay": 10.0, "DepDelay": 5.0, "TaxiOut": 15.0, "TaxiIn": 5.0,
            "AirTime": 100.0, "ActualElapsedTime": 120.0, "CRSElapsedTime": 125.0
        }]

    def test_r4_f01_test_01_missing_actual_bts_sha256_no_fallback(self):
        """Test 1: Missing actual_bts_sha256 (None) does not fall back to comparing declared hash to itself."""
        prov = BtsProvenanceMetadata(
            project_lead_approval_status="APPROVED_BY_PROJECT_LEAD",
            approval_record_ref="DECISION_20261019_PL_BTS_SAMPLE",
            is_external_reference=True,
            sha256_hash=self.valid_sha,
        )
        # Calling validator with None actual hash must return False
        ok, msg = BtsProvenanceValidator.validate_candidate_checksum(prov, None)
        self.assertFalse(ok)
        self.assertIn("PROVENANCE_ACTUAL_CHECKSUM_MISSING", msg)

        # In reconciler, candidate_checksum_matched must be False
        summary, _ = self.reconciler.reconcile(
            self.valid_dataset, self.valid_bts,
            provenance_metadata=prov,
            actual_bts_sha256=None,
            is_authentic_bts_data=True
        )
        self.assertFalse(summary.candidate_checksum_matched)
        self.assertFalse(summary.source_provenance_verified)

    def test_r4_f01_test_02_blank_whitespace_actual_sha_rejected(self):
        """Test 2: Blank or whitespace actual_bts_sha256 is strictly rejected."""
        prov = BtsProvenanceMetadata(
            project_lead_approval_status="APPROVED_BY_PROJECT_LEAD",
            approval_record_ref="DECISION_20261019_PL_BTS_SAMPLE",
            is_external_reference=True,
            sha256_hash=self.valid_sha,
        )
        for bad_actual in ["", "   ", "\t\n"]:
            ok, msg = BtsProvenanceValidator.validate_candidate_checksum(prov, bad_actual)
            self.assertFalse(ok)
            self.assertIn("PROVENANCE_ACTUAL_CHECKSUM_MISSING", msg)

    def test_r4_f01_test_03_invalid_length_actual_sha_rejected(self):
        """Test 3: Malformed lengths (32, 63, 65 chars) in actual checksum are rejected."""
        prov = BtsProvenanceMetadata(
            project_lead_approval_status="APPROVED_BY_PROJECT_LEAD",
            approval_record_ref="DECISION_20261019_PL_BTS_SAMPLE",
            is_external_reference=True,
            sha256_hash=self.valid_sha,
        )
        for bad_len in [32, 63, 65]:
            bad_hash = "f" * bad_len
            ok, msg = BtsProvenanceValidator.validate_candidate_checksum(prov, bad_hash)
            self.assertFalse(ok)
            self.assertIn("PROVENANCE_ACTUAL_CHECKSUM_MALFORMED", msg)

    def test_r4_f01_test_04_companion_format_valid_does_not_authenticate_source(self):
        """Test 4: Valid companion metadata format does NOT set source_provenance_verified = True."""
        prov = BtsProvenanceMetadata(
            project_lead_approval_status="APPROVED_BY_PROJECT_LEAD",
            approval_record_ref="DECISION_20261019_PL_BTS_SAMPLE",
            is_external_reference=True,
            sha256_hash=self.valid_sha,
        )
        fmt_ok, fmt_msg = BtsProvenanceValidator.validate_metadata_format(prov)
        self.assertTrue(fmt_ok, fmt_msg)

        summary, _ = self.reconciler.reconcile(
            self.valid_dataset, self.valid_bts,
            provenance_metadata=prov,
            actual_bts_sha256=self.valid_sha,
            is_authentic_bts_data=True
        )
        self.assertTrue(summary.companion_metadata_valid)
        self.assertFalse(summary.source_provenance_verified,
                         "Candidate companion metadata cannot authenticate external provenance!")

    def test_r4_f01_test_05_candidate_checksum_match_disaggregated(self):
        """Test 5: Matched candidate checksum produces candidate_checksum_matched=True while source_provenance_verified=False."""
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
        self.assertTrue(summary.candidate_checksum_matched)
        self.assertTrue(summary.companion_metadata_valid)
        self.assertFalse(summary.source_provenance_verified)

    def test_r4_f01_test_06_human_accepted_unconditionally_false(self):
        """Test 6: human_accepted is unconditionally False across all automated reconciliation runs."""
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
        self.assertFalse(summary.human_accepted)

    def test_r4_f01_test_07_ts018_pass_authentic_unreachable(self):
        """Test 7: Verdict TS018_PASS_AUTHENTIC_PARITY_ESTABLISHED is strictly unreachable by candidate input."""
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
        self.assertNotEqual(summary.reconciliation_verdict, "TS018_PASS_AUTHENTIC_PARITY_ESTABLISHED")
        self.assertEqual(summary.reconciliation_verdict, "TS018_CANDIDATE_PARITY_VERIFIED_HUMAN_APPROVAL_PENDING")

    def test_r4_f01_test_08_synthetic_reconciler_verdict(self):
        """Test 8: Synthetic fixtures emit SYNTHETIC_RECONCILER_VERIFIED_AUTHENTIC_BTS_PENDING."""
        summary, _ = self.reconciler.reconcile(
            self.valid_dataset, self.valid_bts,
            is_authentic_bts_data=False
        )
        self.assertEqual(summary.reconciliation_verdict, "SYNTHETIC_RECONCILER_VERIFIED_AUTHENTIC_BTS_PENDING")
        self.assertFalse(summary.source_provenance_verified)
        self.assertFalse(summary.candidate_checksum_matched)
        self.assertFalse(summary.companion_metadata_valid)

    def test_r4_f01_test_09_external_candidate_verdict(self):
        """Test 9: External candidate with valid checksum emits TS018_CANDIDATE_PARITY_VERIFIED_HUMAN_APPROVAL_PENDING."""
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
        self.assertEqual(summary.reconciliation_verdict, "TS018_CANDIDATE_PARITY_VERIFIED_HUMAN_APPROVAL_PENDING")


class TestT011R4InvalidPidFailClosed(unittest.TestCase):
    """Guards for R4-F02: Invalid PID fail-closed handling and PidLivenessStatus classification."""

    def test_r4_f02_test_01_string_pid_fails_closed(self):
        """Test 1: String PID ('not-an-integer') is classified as INVALID_PID and fails closed in break_stale_lock."""
        self.assertEqual(get_pid_liveness("not-an-integer"), PidLivenessStatus.INVALID_PID)
        self.assertEqual(get_pid_liveness("12345"), PidLivenessStatus.INVALID_PID)

        with tempfile.TemporaryDirectory() as td:
            tdp = Path(td)
            lock_file = tdp / ".pipeline.lock"
            # Write raw JSON with string PID
            raw_data = {
                "owner_token": "token_1", "run_id": "r1", "pid": "not-an-integer",
                "hostname": platform.node(), "created_at": "2026-01-01T00:00:00Z"
            }
            lock_file.write_text(json.dumps(raw_data), encoding="utf-8")

            lock = SingleWriterLock(tdp, run_id="recovery")
            with self.assertRaises(LockContentionError) as ctx:
                lock.break_stale_lock(force=True)
            self.assertIn("FAIL_CLOSED — MANUAL_RECOVERY_REQUIRED", str(ctx.exception))
            self.assertTrue(lock_file.exists(), "Lock with invalid string PID must not be broken!")

    def test_r4_f02_test_02_negative_pid_fails_closed(self):
        """Test 2: Negative integer PID (-1, -999) is classified as INVALID_PID and fails closed."""
        self.assertEqual(get_pid_liveness(-1), PidLivenessStatus.INVALID_PID)
        self.assertEqual(get_pid_liveness(-999), PidLivenessStatus.INVALID_PID)

        with tempfile.TemporaryDirectory() as td:
            tdp = Path(td)
            lock_file = tdp / ".pipeline.lock"
            raw_data = {
                "owner_token": "token_1", "run_id": "r1", "pid": -1,
                "hostname": platform.node(), "created_at": "2026-01-01T00:00:00Z"
            }
            lock_file.write_text(json.dumps(raw_data), encoding="utf-8")

            lock = SingleWriterLock(tdp, run_id="recovery")
            with self.assertRaises(LockContentionError) as ctx:
                lock.break_stale_lock(force=True)
            self.assertIn("FAIL_CLOSED — MANUAL_RECOVERY_REQUIRED", str(ctx.exception))
            self.assertTrue(lock_file.exists(), "Lock with negative PID must not be broken!")

    def test_r4_f02_test_03_zero_pid_fails_closed(self):
        """Test 3: Zero PID (0) is classified as INVALID_PID and fails closed."""
        self.assertEqual(get_pid_liveness(0), PidLivenessStatus.INVALID_PID)

        with tempfile.TemporaryDirectory() as td:
            tdp = Path(td)
            lock_file = tdp / ".pipeline.lock"
            raw_data = {
                "owner_token": "token_1", "run_id": "r1", "pid": 0,
                "hostname": platform.node(), "created_at": "2026-01-01T00:00:00Z"
            }
            lock_file.write_text(json.dumps(raw_data), encoding="utf-8")

            lock = SingleWriterLock(tdp, run_id="recovery")
            with self.assertRaises(LockContentionError) as ctx:
                lock.break_stale_lock(force=True)
            self.assertIn("FAIL_CLOSED — MANUAL_RECOVERY_REQUIRED", str(ctx.exception))
            self.assertTrue(lock_file.exists(), "Lock with PID 0 must not be broken!")

    def test_r4_f02_test_04_boolean_pid_fails_closed(self):
        """Test 4: Boolean PID (True, False) is classified as INVALID_PID, mitigating Python bool subclassing trap."""
        self.assertEqual(get_pid_liveness(True), PidLivenessStatus.INVALID_PID)
        self.assertEqual(get_pid_liveness(False), PidLivenessStatus.INVALID_PID)

        with tempfile.TemporaryDirectory() as td:
            tdp = Path(td)
            lock_file = tdp / ".pipeline.lock"
            raw_data = {
                "owner_token": "token_1", "run_id": "r1", "pid": True,
                "hostname": platform.node(), "created_at": "2026-01-01T00:00:00Z"
            }
            lock_file.write_text(json.dumps(raw_data), encoding="utf-8")

            lock = SingleWriterLock(tdp, run_id="recovery")
            with self.assertRaises(LockContentionError) as ctx:
                lock.break_stale_lock(force=True)
            self.assertIn("FAIL_CLOSED — MANUAL_RECOVERY_REQUIRED", str(ctx.exception))
            self.assertTrue(lock_file.exists(), "Lock with boolean PID must not be broken!")

    def test_r4_f02_test_05_float_pid_fails_closed(self):
        """Test 5: Float PID (3.14) is classified as INVALID_PID and fails closed."""
        self.assertEqual(get_pid_liveness(3.14), PidLivenessStatus.INVALID_PID)

        with tempfile.TemporaryDirectory() as td:
            tdp = Path(td)
            lock_file = tdp / ".pipeline.lock"
            raw_data = {
                "owner_token": "token_1", "run_id": "r1", "pid": 3.14,
                "hostname": platform.node(), "created_at": "2026-01-01T00:00:00Z"
            }
            lock_file.write_text(json.dumps(raw_data), encoding="utf-8")

            lock = SingleWriterLock(tdp, run_id="recovery")
            with self.assertRaises(LockContentionError) as ctx:
                lock.break_stale_lock(force=True)
            self.assertIn("FAIL_CLOSED — MANUAL_RECOVERY_REQUIRED", str(ctx.exception))
            self.assertTrue(lock_file.exists(), "Lock with float PID must not be broken!")

    def test_r4_f02_test_06_lockmetadata_rejects_bool_pid(self):
        """Test 6: LockMetadata constructor rejects boolean PID (True) with ValueError."""
        with self.assertRaises(ValueError) as ctx:
            LockMetadata(
                owner_token="t", run_id="r", pid=True,
                hostname="h", created_at="2026-01-01T00:00:00Z"
            )
        self.assertIn("Invalid PID", str(ctx.exception))

    def test_r4_f02_test_07_lockmetadata_rejects_string_pid(self):
        """Test 7: LockMetadata constructor rejects string PID ('123') with ValueError."""
        with self.assertRaises(ValueError) as ctx:
            LockMetadata(
                owner_token="t", run_id="r", pid="123",
                hostname="h", created_at="2026-01-01T00:00:00Z"
            )
        self.assertIn("Invalid PID", str(ctx.exception))

    def test_r4_f02_test_08_current_process_alive(self):
        """Test 8: Current process PID is correctly classified as PROCESS_ALIVE."""
        self.assertEqual(get_pid_liveness(os.getpid()), PidLivenessStatus.PROCESS_ALIVE)
        self.assertTrue(is_pid_alive(os.getpid()))

    def test_r4_f02_test_09_dead_pid_dead(self):
        """Test 9: Guaranteed dead PID (99999999) is correctly classified as PROCESS_DEAD."""
        self.assertEqual(get_pid_liveness(99999999), PidLivenessStatus.PROCESS_DEAD)
        self.assertFalse(is_pid_alive(99999999))


class TestT011R4LockReplacementRace(unittest.TestCase):
    """Guards for R4-F03: Lock replacement race prevention and pre-unlink verification."""

    def test_r4_f03_test_01_break_stale_lock_concurrent_deletion(self):
        """Test 1: break_stale_lock handles concurrent external deletion gracefully without crashing."""
        with tempfile.TemporaryDirectory() as td:
            tdp = Path(td)
            dead_pid = 99999999
            meta = LockMetadata(
                owner_token="stale_tok", run_id="stale_run", pid=dead_pid,
                hostname=platform.node(), created_at="2026-01-01T00:00:00Z"
            )
            lock_file = tdp / ".pipeline.lock"
            lock_file.write_text(meta.to_json(), encoding="utf-8")

            lock = SingleWriterLock(tdp, run_id="recovery")

            # Hook unlinks the file right before break_stale_lock calls unlink
            def unlink_concurrently():
                lock_file.unlink(missing_ok=True)

            lock._pre_unlink_hook = unlink_concurrently
            res = lock.break_stale_lock(force=True)
            self.assertTrue(res)
            self.assertFalse(lock_file.exists())

    def test_r4_f03_test_02_break_stale_lock_replaced_by_another_dead_pid(self):
        """Test 2: When lock is replaced by another dead PID during hook, token mismatch fails closed."""
        with tempfile.TemporaryDirectory() as td:
            tdp = Path(td)
            meta1 = LockMetadata(
                owner_token="token_1", run_id="run_1", pid=99999998,
                hostname=platform.node(), created_at="2026-01-01T00:00:00Z"
            )
            meta2 = LockMetadata(
                owner_token="token_2", run_id="run_2", pid=99999999,
                hostname=platform.node(), created_at="2026-01-01T00:00:00Z"
            )
            lock_file = tdp / ".pipeline.lock"
            lock_file.write_text(meta1.to_json(), encoding="utf-8")

            lock = SingleWriterLock(tdp, run_id="recovery")

            def replace_with_meta2():
                lock_file.write_text(meta2.to_json(), encoding="utf-8")

            lock._pre_unlink_hook = replace_with_meta2
            with self.assertRaises(LockContentionError) as ctx:
                lock.break_stale_lock(force=True)
            self.assertIn("Lock file changed concurrently", str(ctx.exception))
            # Verify replacement lock is STILL INTACT on disk!
            self.assertTrue(lock_file.exists())
            self.assertEqual(LockMetadata.from_json(lock_file.read_text("utf-8")).owner_token, "token_2")

    def test_r4_f03_test_03_break_stale_lock_replaced_by_active_pid(self):
        """Test 3: When lock is replaced by active process during hook, fail-closed preserves active lock."""
        with tempfile.TemporaryDirectory() as td:
            tdp = Path(td)
            meta1 = LockMetadata(
                owner_token="token_1", run_id="run_1", pid=99999998,
                hostname=platform.node(), created_at="2026-01-01T00:00:00Z"
            )
            active_meta = LockMetadata(
                owner_token="active_token", run_id="active_run", pid=os.getpid(),
                hostname=platform.node(), created_at="2026-01-01T00:00:00Z"
            )
            lock_file = tdp / ".pipeline.lock"
            lock_file.write_text(meta1.to_json(), encoding="utf-8")

            lock = SingleWriterLock(tdp, run_id="recovery")

            def replace_with_active():
                lock_file.write_text(active_meta.to_json(), encoding="utf-8")

            lock._pre_unlink_hook = replace_with_active
            with self.assertRaises(LockContentionError) as ctx:
                lock.break_stale_lock(force=True)
            self.assertIn("Lock file changed concurrently", str(ctx.exception))
            self.assertTrue(lock_file.exists())
            self.assertEqual(LockMetadata.from_json(lock_file.read_text("utf-8")).owner_token, "active_token")

    def test_r4_f03_test_04_break_stale_lock_replaced_same_pid_diff_token(self):
        """Test 4: Replaced by same PID but different owner token is rejected."""
        with tempfile.TemporaryDirectory() as td:
            tdp = Path(td)
            meta1 = LockMetadata(
                owner_token="token_A", run_id="run_1", pid=99999998,
                hostname=platform.node(), created_at="2026-01-01T00:00:00Z"
            )
            meta2 = LockMetadata(
                owner_token="token_B", run_id="run_1", pid=99999998,
                hostname=platform.node(), created_at="2026-01-01T00:00:00Z"
            )
            lock_file = tdp / ".pipeline.lock"
            lock_file.write_text(meta1.to_json(), encoding="utf-8")

            lock = SingleWriterLock(tdp, run_id="recovery")

            def replace_with_different_token():
                lock_file.write_text(meta2.to_json(), encoding="utf-8")

            lock._pre_unlink_hook = replace_with_different_token
            with self.assertRaises(LockContentionError) as ctx:
                lock.break_stale_lock(force=True)
            self.assertIn("Lock file changed concurrently", str(ctx.exception))
            self.assertTrue(lock_file.exists())

    def test_r4_f03_test_05_break_stale_lock_replaced_corrupt_content(self):
        """Test 5: Lock replaced by corrupt/non-JSON content during hook fails closed."""
        with tempfile.TemporaryDirectory() as td:
            tdp = Path(td)
            meta1 = LockMetadata(
                owner_token="token_1", run_id="run_1", pid=99999998,
                hostname=platform.node(), created_at="2026-01-01T00:00:00Z"
            )
            lock_file = tdp / ".pipeline.lock"
            lock_file.write_text(meta1.to_json(), encoding="utf-8")

            lock = SingleWriterLock(tdp, run_id="recovery")

            def corrupt_concurrently():
                lock_file.write_text("CORRUPTED_IN_FLIGHT", encoding="utf-8")

            lock._pre_unlink_hook = corrupt_concurrently
            with self.assertRaises(LockContentionError) as ctx:
                lock.break_stale_lock(force=True)
            self.assertIn("Lock file became unparseable concurrently", str(ctx.exception))
            self.assertTrue(lock_file.exists())

    def test_r4_f03_test_06_release_replaced_by_different_owner_token(self):
        """Test 6: release() raises LockOwnerMismatchError when lock was replaced prior to unlink."""
        with tempfile.TemporaryDirectory() as td:
            tdp = Path(td)
            writer = SingleWriterLock(tdp, run_id="run_w1")
            writer.acquire()
            self.assertTrue(writer.is_acquired)

            imposter_meta = LockMetadata(
                owner_token="imposter_token", run_id="run_imposter", pid=os.getpid(),
                hostname=platform.node(), created_at="2026-01-01T00:00:00Z"
            )

            def race_replace_lock():
                writer.lock_file_path.write_text(imposter_meta.to_json(), encoding="utf-8")

            writer._pre_unlink_hook = race_replace_lock
            with self.assertRaises(LockOwnerMismatchError) as ctx:
                writer.release()
            self.assertIn("Lock owner mismatch", str(ctx.exception))
            # Verify imposter lock was NOT deleted!
            self.assertTrue(writer.lock_file_path.exists())
            self.assertEqual(
                LockMetadata.from_json(writer.lock_file_path.read_text("utf-8")).owner_token,
                "imposter_token"
            )

    def test_r4_f03_test_07_release_file_deleted_concurrently(self):
        """Test 7: release() exits safely when lock file was already deleted."""
        with tempfile.TemporaryDirectory() as td:
            tdp = Path(td)
            writer = SingleWriterLock(tdp, run_id="run_w1")
            writer.acquire()

            def race_delete():
                writer.lock_file_path.unlink(missing_ok=True)

            writer._pre_unlink_hook = race_delete
            # Even if hook deleted it, recheck handles missing file cleanly
            writer.release()
            self.assertFalse(writer.is_acquired)

    def test_r4_f03_test_08_sequential_acquire_release_cycles(self):
        """Test 8: Normal sequential acquire and release cycles complete cleanly with 0 leaked locks."""
        with tempfile.TemporaryDirectory() as td:
            tdp = Path(td)
            for cycle in range(5):
                lock = SingleWriterLock(tdp, run_id=f"seq_run_{cycle}")
                lock.acquire()
                self.assertTrue(lock.is_acquired)
                self.assertTrue(lock.lock_file_path.exists())
                lock.release()
                self.assertFalse(lock.is_acquired)
                self.assertFalse(lock.lock_file_path.exists())


if __name__ == "__main__":
    unittest.main()
