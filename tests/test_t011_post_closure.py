#!/usr/bin/env python3
"""
tests/test_t011_post_closure.py

T011 Post-Closure Comprehensive Safety & Evidence Suite.
Addresses findings C1 and C2:
- C1: SingleWriterLock recovery transaction safety, durable hold marker,
      fail-closed admission block on audit record failure, retry/idempotency,
      and verified audit commit before writer admission.
- C2: SingleWriterLock __exit__ truthful diagnostics surfacing INCIDENT_PERSISTENCE_FAILED
      on normal context exit with release failure, exception chaining, owner mismatch preservation,
      and zero false persistence claims.
"""

import errno
import json
import os
import platform
import tempfile
import unittest
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from unittest.mock import MagicMock, patch

from flight_pipeline.storage.locking import (
    CoordinationLock,
    IncidentPersistenceError,
    IncidentPersistenceResult,
    LockContentionError,
    LockError,
    LockMetadata,
    LockOwnerMismatchError,
    LockOwnerReleaseFailureError,
    LockReleaseFailureError,
    SingleWriterLock,
    UnresolvedRecoveryStateError,
)


class TestT011PostClosure(unittest.TestCase):
    """Post-closure regression and verification suite for findings C1 and C2."""

    # =========================================================================
    # FINDING C1: RECOVERY TRANSACTION INTEGRITY & DURABLE HOLD MECHANISM
    # =========================================================================

    def test_c1_01_recovery_record_cannot_be_created(self):
        """C1 Test 1: Permission error creating resolution record keeps hold marker and blocks writer."""
        with tempfile.TemporaryDirectory() as td:
            ld = Path(td)
            staging_del = ld / ".pipeline.lock.del_test_01"
            staging_del.write_text("{\"owner_token\": \"t1\"}", encoding="utf-8")

            lock1 = SingleWriterLock(ld, run_id="run_c1_01")
            archive_dir = ld / "recovery_archive"

            orig_open = os.open
            def fake_open(path, flags, *args, **kwargs):
                if "recovery_resolution_" in str(path):
                    raise PermissionError("Access denied creating recovery resolution record")
                return orig_open(path, flags, *args, **kwargs)

            with patch("os.open", side_effect=fake_open):
                with self.assertRaises(LockError) as cm:
                    lock1.resolve_recovery_state(
                        authorized=True,
                        operator="sec_ops",
                        reason="Test permission error on resolution record",
                        archive_dir=archive_dir,
                    )

            self.assertIn("Failed to commit recovery resolution audit record", str(cm.exception))
            self.assertIn("Admission guard preserved", str(cm.exception))

            # Verify writer 2 is strictly blocked
            lock2 = SingleWriterLock(ld, run_id="run_c1_01_writer2")
            with self.assertRaises(UnresolvedRecoveryStateError) as cm2:
                lock2.acquire()
            self.assertIn("unresolved recovery artifacts detected", str(cm2.exception))
            self.assertFalse(lock2.is_acquired)

    def test_c1_02_recovery_record_write_interrupted(self):
        """C1 Test 2: Short write during resolution record persistence fails closed and blocks writer."""
        with tempfile.TemporaryDirectory() as td:
            ld = Path(td)
            staging_del = ld / ".pipeline.lock.del_test_02"
            staging_del.write_text("{\"owner_token\": \"t2\"}", encoding="utf-8")

            lock1 = SingleWriterLock(ld, run_id="run_c1_02")
            archive_dir = ld / "recovery_archive"

            orig_write = os.write
            def short_write(fd, data):
                # Write only 3 bytes instead of full payload
                return 3

            with patch("os.write", side_effect=short_write):
                with self.assertRaises(LockError) as cm:
                    lock1.resolve_recovery_state(
                        authorized=True,
                        operator="sec_ops",
                        reason="Test short write on resolution record",
                        archive_dir=archive_dir,
                    )

            self.assertIn("Short write on recovery resolution", str(cm.exception))

            # Verify writer 2 is blocked
            lock2 = SingleWriterLock(ld, run_id="run_c1_02_writer2")
            with self.assertRaises(UnresolvedRecoveryStateError):
                lock2.acquire()

    def test_c1_03_recovery_record_fsync_fails(self):
        """C1 Test 3: fsync failure during resolution record persistence fails closed and blocks writer."""
        with tempfile.TemporaryDirectory() as td:
            ld = Path(td)
            staging_del = ld / ".pipeline.lock.del_test_03"
            staging_del.write_text("{\"owner_token\": \"t3\"}", encoding="utf-8")

            lock1 = SingleWriterLock(ld, run_id="run_c1_03")
            archive_dir = ld / "recovery_archive"

            orig_fsync = os.fsync
            call_count = 0
            def failing_fsync(fd):
                nonlocal call_count
                call_count += 1
                # First fsync is for hold marker (succeeds), second is for resolution record (fails)
                if call_count >= 2:
                    raise OSError(errno.EIO, "I/O error during fsync of resolution record")
                return orig_fsync(fd)

            with patch("os.fsync", side_effect=failing_fsync):
                with self.assertRaises(LockError) as cm:
                    lock1.resolve_recovery_state(
                        authorized=True,
                        operator="sec_ops",
                        reason="Test fsync failure",
                        archive_dir=archive_dir,
                    )

            self.assertIn("I/O error during fsync", str(cm.exception))

            # Verify writer 2 is blocked
            lock2 = SingleWriterLock(ld, run_id="run_c1_03_writer2")
            with self.assertRaises(UnresolvedRecoveryStateError):
                lock2.acquire()

    def test_c1_04_recovery_record_readback_mismatch(self):
        """C1 Test 4: Corrupted readback of resolution record fails verification and blocks writer."""
        with tempfile.TemporaryDirectory() as td:
            ld = Path(td)
            staging_del = ld / ".pipeline.lock.del_test_04"
            staging_del.write_text("{\"owner_token\": \"t4\"}", encoding="utf-8")

            lock1 = SingleWriterLock(ld, run_id="run_c1_04")
            archive_dir = ld / "recovery_archive"

            orig_read_bytes = Path.read_bytes
            def corrupt_read_bytes(self_path, *args, **kwargs):
                if "recovery_resolution_" in str(self_path):
                    return b"{\"corrupted_json\": true}"
                return orig_read_bytes(self_path, *args, **kwargs)

            with patch("pathlib.Path.read_bytes", autospec=True, side_effect=corrupt_read_bytes):
                with self.assertRaises(LockError) as cm:
                    lock1.resolve_recovery_state(
                        authorized=True,
                        operator="sec_ops",
                        reason="Test readback mismatch",
                        archive_dir=archive_dir,
                    )

            self.assertIn("Corrupted recovery resolution readback", str(cm.exception))

            # Verify writer 2 is blocked
            lock2 = SingleWriterLock(ld, run_id="run_c1_04_writer2")
            with self.assertRaises(UnresolvedRecoveryStateError):
                lock2.acquire()

    def test_c1_05_partial_artifact_archival_fails(self):
        """C1 Test 5: If renaming an artifact to archive fails, hold marker remains and blocks writer."""
        with tempfile.TemporaryDirectory() as td:
            ld = Path(td)
            art1 = ld / ".pipeline.lock.del_art1"
            art2 = ld / ".pipeline.lock.del_art2"
            art1.write_text("{\"owner\": \"art1\"}", encoding="utf-8")
            art2.write_text("{\"owner\": \"art2\"}", encoding="utf-8")

            lock1 = SingleWriterLock(ld, run_id="run_c1_05")
            archive_dir = ld / "recovery_archive"

            orig_replace = os.replace
            replace_calls = 0
            def partial_replace(src, dst):
                nonlocal replace_calls
                replace_calls += 1
                # Replace 1: hold marker tmp -> hold marker (succeeds)
                # Replace 2: art1 -> archive (succeeds)
                # Replace 3: art2 -> archive (fails)
                if replace_calls == 3:
                    raise OSError("Injected filesystem error moving art2")
                return orig_replace(src, dst)

            with patch("os.replace", side_effect=partial_replace):
                with self.assertRaises(LockError) as cm:
                    lock1.resolve_recovery_state(
                        authorized=True,
                        operator="sec_ops",
                        reason="Test partial archival failure",
                        archive_dir=archive_dir,
                    )

            self.assertIn("Failed to archive recovery artifact", str(cm.exception))
            self.assertIn("Recovery hold marker preserved", str(cm.exception))

            # Verify writer 2 is blocked
            lock2 = SingleWriterLock(ld, run_id="run_c1_05_writer2")
            with self.assertRaises(UnresolvedRecoveryStateError):
                lock2.acquire()

    def test_c1_06_retry_after_partially_completed_recovery(self):
        """C1 Test 6: Retry after partial failure successfully recovers remaining artifacts and admits writer."""
        with tempfile.TemporaryDirectory() as td:
            ld = Path(td)
            staging_del = ld / ".pipeline.lock.del_retry"
            staging_del.write_text("{\"owner_token\": \"t_retry\"}", encoding="utf-8")

            lock1 = SingleWriterLock(ld, run_id="run_c1_06")
            archive_dir = ld / "recovery_archive"

            # Inject failure on first run
            orig_open = os.open
            fail_open = True
            def conditionally_failing_open(path, flags, *args, **kwargs):
                if fail_open and "recovery_resolution_" in str(path):
                    raise OSError("Temporary I/O glitch")
                return orig_open(path, flags, *args, **kwargs)

            with patch("os.open", side_effect=conditionally_failing_open):
                with self.assertRaises(LockError):
                    lock1.resolve_recovery_state(
                        authorized=True,
                        operator="ops_retry",
                        reason="First attempt fails",
                        archive_dir=archive_dir,
                    )

            # Writer is blocked after failed attempt
            lock2 = SingleWriterLock(ld, run_id="run_c1_06_writer2")
            with self.assertRaises(UnresolvedRecoveryStateError):
                lock2.acquire()

            # Second attempt (retry without failure)
            fail_open = False
            with patch("os.open", side_effect=conditionally_failing_open):
                res = lock1.resolve_recovery_state(
                    authorized=True,
                    operator="ops_retry",
                    reason="Second attempt succeeds",
                    archive_dir=archive_dir,
                )

            self.assertTrue(res["resolved"])
            self.assertGreater(res["count"], 0)
            self.assertTrue(Path(res["resolution_record_file"]).exists())

            # Now writer 2 acquires cleanly!
            lock2.acquire()
            self.assertTrue(lock2.is_acquired)
            lock2.release()
            self.assertFalse(lock2.is_acquired)

    def test_c1_07_new_writer_denied_until_verified_recovery_commit(self):
        """C1 Test 7: New writer is denied acquisition while recovery hold is in place."""
        with tempfile.TemporaryDirectory() as td:
            ld = Path(td)
            # Create a hold file directly
            hold_file = ld / ".pipeline.lock.recovery_in_progress_manual"
            hold_file.write_text("{\"event\": \"RECOVERY_IN_PROGRESS\"}", encoding="utf-8")

            writer = SingleWriterLock(ld, run_id="writer_denied")
            with self.assertRaises(UnresolvedRecoveryStateError) as cm:
                writer.acquire()
            self.assertIn("recovery_in_progress_manual", str(cm.exception))

    def test_c1_08_successful_verified_recovery_permits_next_writer(self):
        """C1 Test 8: End-to-end verified recovery cleanly commits resolution record and permits next writer."""
        with tempfile.TemporaryDirectory() as td:
            ld = Path(td)
            staging_del = ld / ".pipeline.lock.del_clean"
            staging_del.write_text("{\"owner_token\": \"token_clean\"}", encoding="utf-8")

            lock1 = SingleWriterLock(ld, run_id="run_c1_08_recoverer")
            res = lock1.resolve_recovery_state(
                authorized=True,
                operator="lead_operator",
                reason="Routine recovery of clean staging failure",
            )

            self.assertTrue(res["resolved"])
            self.assertEqual(res["count"], 1)
            res_file = Path(res["resolution_record_file"])
            self.assertTrue(res_file.exists())

            # Check JSON audit record structure
            data = json.loads(res_file.read_text(encoding="utf-8"))
            self.assertEqual(data["operator"], "lead_operator")
            self.assertEqual(data["reason"], "Routine recovery of clean staging failure")
            self.assertEqual(len(data["archived_artifacts"]), 1)
            self.assertIn("del_clean", data["archived_artifacts"][0]["original_path"])

            # Verify writer 2 acquires cleanly
            lock2 = SingleWriterLock(ld, run_id="run_c1_08_admitted_writer")
            lock2.acquire()
            self.assertTrue(lock2.is_acquired)
            lock2.release()
            self.assertFalse(lock2.is_acquired)

    def test_c1_09_two_cooperative_processes_remain_mutually_exclusive(self):
        """C1 Test 9: CoordinationLock serializes recovery and concurrent acquisition."""
        with tempfile.TemporaryDirectory() as td:
            ld = Path(td)
            lock1 = SingleWriterLock(ld, run_id="writer_mutex_1")
            lock2 = SingleWriterLock(ld, run_id="writer_mutex_2")

            lock1.acquire()
            self.assertTrue(lock1.is_acquired)

            with self.assertRaises(LockContentionError):
                lock2.acquire()

            lock1.release()
            self.assertFalse(lock1.is_acquired)

            lock2.acquire()
            self.assertTrue(lock2.is_acquired)
            lock2.release()

    def test_c1_10_recovery_requires_explicit_authorization_and_operator(self):
        """C1 Test 10: resolve_recovery_state rejects unauthorized or empty operator calls."""
        with tempfile.TemporaryDirectory() as td:
            ld = Path(td)
            lock = SingleWriterLock(ld, run_id="test_auth")

            # Unauthorized
            with self.assertRaises(LockError) as cm1:
                lock.resolve_recovery_state(authorized=False, operator="ops", reason="fix")
            self.assertIn("authorized=True", str(cm1.exception))

            # Empty operator
            with self.assertRaises(ValueError) as cm2:
                lock.resolve_recovery_state(authorized=True, operator="", reason="fix")
            self.assertIn("non-empty operator", str(cm2.exception))

            # Empty reason
            with self.assertRaises(ValueError) as cm3:
                lock.resolve_recovery_state(authorized=True, operator="ops", reason="   ")
            self.assertIn("non-empty justification reason", str(cm3.exception))

    # =========================================================================
    # FINDING C2: CONTEXT EXIT TRUTHFUL INCIDENT DIAGNOSTICS & CHAINING
    # =========================================================================

    def test_c2_01_normal_exit_clean_release_no_incident(self):
        """C2 Test 1: Normal context manager exit releases cleanly with 0 incident reports."""
        with tempfile.TemporaryDirectory() as td:
            ld = Path(td)
            lock = SingleWriterLock(ld, run_id="run_c2_01")
            with lock:
                self.assertTrue(lock.is_acquired)

            self.assertFalse(lock.is_acquired)
            incidents = list(ld.glob("lock_release_incident_*.json"))
            self.assertEqual(len(incidents), 0)

    def test_c2_02_normal_exit_release_fail_persist_success(self):
        """C2 Test 2: Normal exit with release failure and successful incident persistence surfaces path."""
        with tempfile.TemporaryDirectory() as td:
            ld = Path(td)
            lock = SingleWriterLock(ld, run_id="run_c2_02")

            def failing_release():
                raise LockError("Injected unlink PermissionError during release")

            with patch.object(lock, "release", side_effect=failing_release):
                with self.assertRaises(LockReleaseFailureError) as cm:
                    with lock:
                        pass

            self.assertIn("Incident persisted at", str(cm.exception))
            self.assertIn("Injected unlink PermissionError", str(cm.exception))
            self.assertIn("FAIL_CLOSED — MANUAL_RECOVERY_REQUIRED", str(cm.exception))
            self.assertIsInstance(cm.exception.__cause__, LockError)

            # Cleanup open fd
            if getattr(lock, "_fd", None):
                try:
                    os.close(lock._fd)
                except Exception:
                    pass
                lock._fd = None

    def test_c2_03_normal_exit_release_fail_persist_fail_surfaces_diagnostic(self):
        """C2 Test 3: Normal exit with release failure and persistence failure surfaces INCIDENT_PERSISTENCE_FAILED."""
        with tempfile.TemporaryDirectory() as td:
            ld = Path(td)
            lock = SingleWriterLock(ld, run_id="run_c2_03")

            def failing_release():
                raise LockError("Injected release network drop")

            def failing_persist(*args, **kwargs):
                return IncidentPersistenceResult(
                    success=False,
                    incident_file=None,
                    bytes_written=0,
                    verified=False,
                    error="Primary storage read-only",
                )

            with patch.object(lock, "release", side_effect=failing_release):
                with patch.object(lock, "persist_release_incident", side_effect=failing_persist):
                    with self.assertRaises(LockReleaseFailureError) as cm:
                        with lock:
                            pass

            self.assertIn("INCIDENT_PERSISTENCE_FAILED", str(cm.exception))
            self.assertIn("Primary storage read-only", str(cm.exception))
            self.assertNotIn("Incident persisted at", str(cm.exception))
            self.assertIsInstance(cm.exception.__cause__, LockError)

            # Cleanup open fd
            if getattr(lock, "_fd", None):
                try:
                    os.close(lock._fd)
                except Exception:
                    pass
                lock._fd = None

    def test_c2_04_normal_exit_owner_mismatch_raises_lock_owner_release_failure(self):
        """C2 Test 4: Normal exit with owner mismatch raises LockOwnerReleaseFailureError matching both types."""
        with tempfile.TemporaryDirectory() as td:
            ld = Path(td)
            lock = SingleWriterLock(ld, run_id="run_c2_04")
            with self.assertRaises(LockOwnerMismatchError) as cm_mismatch:
                with lock:
                    imposter = LockMetadata(
                        owner_token="imposter_token_c2_04",
                        run_id="run_c2_04",
                        pid=os.getpid(),
                        hostname=platform.node(),
                        created_at=datetime.now(timezone.utc).isoformat(),
                    )
                    lock.lock_file_path.write_text(imposter.to_json(), encoding="utf-8")

            # Must satisfy both LockOwnerMismatchError and LockReleaseFailureError
            self.assertIsInstance(cm_mismatch.exception, LockOwnerMismatchError)
            self.assertIsInstance(cm_mismatch.exception, LockReleaseFailureError)
            self.assertIsInstance(cm_mismatch.exception, LockError)
            self.assertIn("Lock owner mismatch", str(cm_mismatch.exception))
            self.assertIn("Incident persisted at", str(cm_mismatch.exception))

            # Must satisfy both LockOwnerMismatchError and LockReleaseFailureError
            self.assertIsInstance(cm_mismatch.exception, LockOwnerMismatchError)
            self.assertIsInstance(cm_mismatch.exception, LockReleaseFailureError)
            self.assertIsInstance(cm_mismatch.exception, LockError)
            self.assertIn("Lock owner mismatch", str(cm_mismatch.exception))
            self.assertIn("Incident persisted at", str(cm_mismatch.exception))

    def test_c2_05_block_exception_release_fail_persist_success(self):
        """C2 Test 5: Block exception + release failure + successful persist chains from block exception."""
        with tempfile.TemporaryDirectory() as td:
            ld = Path(td)
            lock = SingleWriterLock(ld, run_id="run_c2_05")

            def failing_release():
                raise LockError("Release failed after pipeline error")

            with patch.object(lock, "release", side_effect=failing_release):
                with self.assertRaises(LockReleaseFailureError) as cm:
                    with lock:
                        raise ValueError("Simulated pipeline failure")

            self.assertIsInstance(cm.exception.__cause__, ValueError)
            self.assertIn("Simulated pipeline failure", str(cm.exception.__cause__))
            self.assertIn("Incident persisted at", str(cm.exception))
            self.assertIn("Release failed after pipeline error", str(cm.exception))

            if getattr(lock, "_fd", None):
                try:
                    os.close(lock._fd)
                except Exception:
                    pass
                lock._fd = None

    def test_c2_06_block_exception_release_fail_persist_fail(self):
        """C2 Test 6: Block exception + release failure + persist failure chains and surfaces INCIDENT_PERSISTENCE_FAILED."""
        with tempfile.TemporaryDirectory() as td:
            ld = Path(td)
            lock = SingleWriterLock(ld, run_id="run_c2_06")

            def failing_release():
                raise LockError("Release failed after pipeline error")

            def failing_persist(*args, **kwargs):
                return IncidentPersistenceResult(
                    success=False,
                    incident_file=None,
                    bytes_written=0,
                    verified=False,
                    error="Storage full during incident write",
                )

            with patch.object(lock, "release", side_effect=failing_release):
                with patch.object(lock, "persist_release_incident", side_effect=failing_persist):
                    with self.assertRaises(LockReleaseFailureError) as cm:
                        with lock:
                            raise KeyError("Simulated column missing in pipeline")

            self.assertIsInstance(cm.exception.__cause__, KeyError)
            self.assertIn("INCIDENT_PERSISTENCE_FAILED", str(cm.exception))
            self.assertIn("Storage full during incident write", str(cm.exception))

            if getattr(lock, "_fd", None):
                try:
                    os.close(lock._fd)
                except Exception:
                    pass
                lock._fd = None

    def test_c2_07_block_exception_normal_release_propagates_original(self):
        """C2 Test 7: Block exception with clean normal release propagates original exception unchanged."""
        with tempfile.TemporaryDirectory() as td:
            ld = Path(td)
            lock = SingleWriterLock(ld, run_id="run_c2_07")

            with self.assertRaises(RuntimeError) as cm:
                with lock:
                    raise RuntimeError("Normal pipeline runtime failure")

            self.assertEqual(str(cm.exception), "Normal pipeline runtime failure")
            self.assertFalse(lock.is_acquired)

    def test_c2_08_atomic_persistence_temp_files_cleaned_up(self):
        """C2 Test 8: Failed atomic incident persistence leaves no stray .tmp files behind."""
        with tempfile.TemporaryDirectory() as td:
            ld = Path(td)
            lock = SingleWriterLock(ld, run_id="run_c2_08")

            with patch("os.replace", side_effect=OSError("Atomic rename failed on Windows")):
                res = lock.persist_release_incident(release_err=LockError("Release failure"))

            self.assertFalse(res.success)
            self.assertFalse(res.verified)

            # Check for any .tmp files
            tmp_files = list(ld.glob(".tmp_*"))
            self.assertEqual(len(tmp_files), 0, f"Found stray temporary files: {tmp_files}")


if __name__ == "__main__":
    unittest.main()
