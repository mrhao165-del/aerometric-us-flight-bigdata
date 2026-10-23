"""
tests/test_lock_state_vs_pointer_state.py

Dedicated regression suite for Finding P02 and Finding G6-C05:
Proves the strict architectural decoupling of POINTER_STATE from WRITER_LOCK_STATE.
Tests all 6 operational preflight states (clean, active, stale, ambiguous, corrupted, unresolved recovery).

Governance Invariants Verified:
1. An uninitialized pointer (missing latest_run_id.txt) DOES NOT imply the workspace is safe for a new writer.
2. If an active lock exists (.pipeline.lock held by a live PID), starting a new writer is strictly forbidden (FAIL-CLOSED).
3. If an unresolved recovery artifact (.del_*, .recovery_required*) exists, SingleWriterLock.acquire()
   strictly raises UnresolvedRecoveryStateError (FAIL-CLOSED).
4. Process liveness distinguishes PROCESS_ALIVE, PROCESS_DEAD, and PROCESS_STATUS_UNKNOWN.
   Ambiguous or unverified liveness strictly results in FAIL-CLOSED.
5. Detecting PROCESS_DEAD does NOT authorize automatic lock deletion or bypass of governed manual recovery.
"""

import json
import os
from pathlib import Path
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

ROOT_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT_DIR / "src"
TOOLS_DIR = ROOT_DIR / "tools" / "qa"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

from flight_pipeline.storage.locking import (
    LockContentionError,
    LockMetadata,
    PidLivenessStatus,
    SingleWriterLock,
    UnresolvedRecoveryStateError,
    get_pid_liveness,
)
from verify_staging_pointer import verify_staging_pointer
from check_writer_preflight_safety import evaluate_writer_safety_policy


class TestLockStateVsPointerStateRegression(unittest.TestCase):
    def test_01_negative_uninitialized_pointer_with_active_lock_is_not_safe(self):
        """
        NEGATIVE REGRESSION (P02 / G6-C05):
        When pointer is uninitialized, verify_staging_pointer() returns UNINITIALIZED_POINTER_ALLOWED.
        HOWEVER, because an active writer lock exists, the preflight check MUST NOT declare SAFE_TO_START_WRITER.
        """
        with tempfile.TemporaryDirectory() as tmp_dir:
            base_dir = Path(tmp_dir)
            lock_dir = base_dir / "locks"
            lock_dir.mkdir(parents=True, exist_ok=True)

            # 1. Pointer file is completely absent (uninitialized)
            pointer_res = verify_staging_pointer(base_dir, allow_uninitialized=True)
            self.assertTrue(pointer_res.success)
            self.assertEqual(pointer_res.status, "UNINITIALIZED_POINTER_ALLOWED")

            # 2. Simulate active lock held by current process PID
            lock = SingleWriterLock(lock_dir, run_id="active_writer_run")
            lock.acquire()
            try:
                # 3. Dual-gate evaluation MUST reject writer admission
                report = evaluate_writer_safety_policy(base_dir, run_id="probe_writer_run")

                self.assertFalse(report.safe_to_start_writer, "Must NOT be safe to start writer when lock is active!")
                self.assertEqual(report.exit_code, 1)
                self.assertEqual(report.lock_state, "ACTIVE_WRITER_LOCK_HELD")
                self.assertEqual(report.pointer_status, "UNINITIALIZED_POINTER_ALLOWED")
                self.assertEqual(report.active_pid, os.getpid())
                self.assertEqual(report.liveness_status, "PROCESS_ALIVE")
            finally:
                lock.release()

    def test_02_negative_unresolved_recovery_marker_blocks_writer_admission(self):
        """
        NEGATIVE REGRESSION:
        When an unrecovered marker (.recovery_required*) or deletion marker (.del_*) exists,
        evaluate_writer_safety_policy() MUST return FAIL-CLOSED (exit code 2).
        """
        with tempfile.TemporaryDirectory() as tmp_dir:
            base_dir = Path(tmp_dir)
            lock_dir = base_dir / "locks"
            lock_dir.mkdir(parents=True, exist_ok=True)

            marker = lock_dir / ".pipeline.lock.recovery_required_run_crashed_12345"
            marker.write_text("CRASH_DURING_PUBLICATION", encoding="utf-8")

            report = evaluate_writer_safety_policy(base_dir, run_id="probe_writer_run")
            self.assertFalse(report.safe_to_start_writer)
            self.assertEqual(report.exit_code, 2)
            self.assertEqual(report.lock_state, "UNRESOLVED_RECOVERY_ARTIFACTS_DETECTED")
            self.assertEqual(report.recovery_artifacts_count, 1)

            # And SingleWriterLock.acquire() MUST raise UnresolvedRecoveryStateError
            lock = SingleWriterLock(lock_dir, run_id="probe_writer_run")
            with self.assertRaises(UnresolvedRecoveryStateError):
                lock.acquire()

    def test_03_negative_stale_lock_dead_pid_does_not_auto_delete(self):
        """
        STALE LOCK INTEGRITY:
        When a lock file contains a dead PID (e.g. 999999), SingleWriterLock MUST NOT
        silently delete it. Preflight evaluator returns exit code 1.
        """
        with tempfile.TemporaryDirectory() as tmp_dir:
            base_dir = Path(tmp_dir)
            lock_dir = base_dir / "locks"
            lock_dir.mkdir(parents=True, exist_ok=True)

            dead_pid = 999999
            with patch("check_writer_preflight_safety.get_pid_liveness", return_value=PidLivenessStatus.PROCESS_DEAD):
                meta = LockMetadata(
                    owner_token="owner-dead-probe",
                    run_id="stale_run",
                    pid=dead_pid,
                    hostname="test-node",
                    created_at="2026-10-19T00:00:00Z",
                )
                lock_file = lock_dir / ".pipeline.lock"
                lock_file.write_text(meta.to_json(), encoding="utf-8")

                report = evaluate_writer_safety_policy(base_dir, run_id="probe_writer_run")
                self.assertFalse(report.safe_to_start_writer)
                self.assertEqual(report.exit_code, 1)
                self.assertEqual(report.lock_state, "STALE_LOCK_MANUAL_RECOVERY_REQUIRED")
                self.assertEqual(report.liveness_status, "PROCESS_DEAD")

                # Lock file must remain untouched
                self.assertTrue(lock_file.exists())

    def test_04_negative_corrupt_lock_metadata_fails_closed(self):
        """
        CORRUPTED LOCK METADATA:
        When .pipeline.lock exists but is corrupted/truncated, preflight check returns exit code 3.
        """
        with tempfile.TemporaryDirectory() as tmp_dir:
            base_dir = Path(tmp_dir)
            lock_dir = base_dir / "locks"
            lock_dir.mkdir(parents=True, exist_ok=True)

            lock_file = lock_dir / ".pipeline.lock"
            lock_file.write_text("{CORRUPT_JSON", encoding="utf-8")

            report = evaluate_writer_safety_policy(base_dir, run_id="probe_writer_run")
            self.assertFalse(report.safe_to_start_writer)
            self.assertEqual(report.exit_code, 3)
            self.assertTrue(report.lock_state.startswith("CORRUPT_LOCK_METADATA_FAIL_CLOSED"))

    def test_05_negative_ambiguous_liveness_fails_closed(self):
        """
        AMBIGUOUS LIVENESS:
        When get_pid_liveness returns PROCESS_STATUS_UNKNOWN, preflight check returns exit code 3.
        """
        with tempfile.TemporaryDirectory() as tmp_dir:
            base_dir = Path(tmp_dir)
            lock_dir = base_dir / "locks"
            lock_dir.mkdir(parents=True, exist_ok=True)

            with patch("check_writer_preflight_safety.get_pid_liveness", return_value=PidLivenessStatus.PROCESS_STATUS_UNKNOWN):
                meta = LockMetadata(
                    owner_token="owner-ambig-probe",
                    run_id="ambiguous_run",
                    pid=12345,
                    hostname="test-node",
                    created_at="2026-10-19T00:00:00Z",
                )
                (lock_dir / ".pipeline.lock").write_text(meta.to_json(), encoding="utf-8")

                report = evaluate_writer_safety_policy(base_dir, run_id="probe_writer_run")
                self.assertFalse(report.safe_to_start_writer)
                self.assertEqual(report.exit_code, 3)
                self.assertEqual(report.lock_state, "AMBIGUOUS_LOCK_LIVENESS_FAIL_CLOSED")

    def test_06_positive_clean_workspace_safe_for_lock_acquisition(self):
        """
        POSITIVE VERIFICATION:
        When pointer is valid (or cleanly uninitialized) and lock directory has no active lock
        and no recovery artifacts, evaluate_writer_safety_policy() reports exit code 0.
        """
        with tempfile.TemporaryDirectory() as tmp_dir:
            base_dir = Path(tmp_dir)
            lock_dir = base_dir / "locks"
            lock_dir.mkdir(parents=True, exist_ok=True)

            report = evaluate_writer_safety_policy(base_dir, run_id="probe_writer_run")
            self.assertTrue(report.safe_to_start_writer)
            self.assertEqual(report.exit_code, 0)
            self.assertEqual(report.lock_state, "CLEAN")
            self.assertEqual(report.recovery_artifacts_count, 0)
            self.assertEqual(report.summary_verdict, "SAFE_TO_PROCEED_TO_LOCK_ACQUISITION")
            self.assertTrue(report.storage_root_matched)

    def test_07_storage_root_mismatch_blocks_writer_admission(self):
        """
        FINDING S04 REGRESSION:
        When expected_storage_root differs from evaluated base_dir (e.g. CLI path drift),
        evaluate_writer_safety_policy() MUST fail-closed with exit code 4.
        """
        with tempfile.TemporaryDirectory() as tmp_dir1, tempfile.TemporaryDirectory() as tmp_dir2:
            base_dir = Path(tmp_dir1)
            planned_root = Path(tmp_dir2)
            (base_dir / "locks").mkdir(parents=True, exist_ok=True)

            report = evaluate_writer_safety_policy(
                base_dir,
                run_id="probe_writer_run",
                expected_storage_root=planned_root,
            )
            self.assertFalse(report.safe_to_start_writer)
            self.assertEqual(report.exit_code, 4)
            self.assertFalse(report.storage_root_matched)
            self.assertTrue(report.summary_verdict.startswith("BLOCKED_STORAGE_ROOT_MISMATCH"))

    def test_08_pointer_corruption_fails_closed(self):
        """
        POINTER CORRUPTION REGRESSION:
        When latest_run_id.txt points to a non-existent directory or has traversal characters,
        evaluate_writer_safety_policy() MUST fail-closed with exit code 4.
        """
        with tempfile.TemporaryDirectory() as tmp_dir:
            base_dir = Path(tmp_dir)
            curated_dir = base_dir / "curated"
            curated_dir.mkdir(parents=True, exist_ok=True)
            (base_dir / "locks").mkdir(parents=True, exist_ok=True)

            pointer_file = curated_dir / "latest_run_id.txt"
            pointer_file.write_text("run_dangling_non_existent\n", encoding="utf-8")

            report = evaluate_writer_safety_policy(base_dir, run_id="probe_writer_run")
            self.assertFalse(report.safe_to_start_writer)
            self.assertEqual(report.exit_code, 4)
            self.assertEqual(report.pointer_status, "DANGLING_POINTER_TARGET_MISSING")
            self.assertTrue(report.summary_verdict.startswith("BLOCKED_POINTER_VERIFICATION_FAILED"))

    def test_09_unified_tools_integration_consistency(self):
        """
        FINDING S04 INTEGRATION:
        Verifies that verify_staging_pointer and check_writer_preflight_safety
        inspect identical resolved absolute paths for the base data directory.
        """
        with tempfile.TemporaryDirectory() as tmp_dir:
            base_dir = Path(tmp_dir).resolve()
            (base_dir / "locks").mkdir(parents=True, exist_ok=True)

            ptr_res = verify_staging_pointer(base_dir, allow_uninitialized=True)
            safety_res = evaluate_writer_safety_policy(base_dir)

            self.assertEqual(Path(ptr_res.base_dir).resolve(), Path(safety_res.base_data_dir).resolve())
            self.assertEqual(Path(ptr_res.pointer_file).resolve(), Path(safety_res.pointer_file).resolve())
            self.assertTrue(safety_res.storage_root_matched)


if __name__ == "__main__":
    unittest.main()
