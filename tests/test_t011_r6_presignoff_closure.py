"""
T-011 R6 Pre-Signoff Closure Acceptance & Verification Suite.

Comprehensive independent counterexample and regression tests for:
- PC-F01: Unresolved release failures and crash artifacts block subsequent writers until authorized manual recovery.
- PC-F02: Durable, verified incident file persistence with atomic semantics and zero false-success claims.

All tests run on Windows NTFS and local filesystem invariants without touching data/raw/.
"""

from dataclasses import asdict
from datetime import datetime, timezone
import errno
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import sys
import tempfile
import time
from typing import Dict, Any, Optional
import unittest
from unittest.mock import MagicMock, patch

SRC_DIR = Path(__file__).resolve().parents[1] / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))
ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from flight_pipeline.ingestion.coordinator import (
    IngestionCoordinator,
    PipelineRunOutcome,
    PipelineState,
    write_json_atomic,
    write_json_atomic_with_retry,
)
from flight_pipeline.ingestion.source_validator import (
    BatchVerificationResult,
    SourceEntry,
    SourceValidator,
    UPSTREAM_IDENTITY_STATUS_UNVERIFIED,
)
from flight_pipeline.storage.locking import (
    CoordinationLock,
    DuplicateRunIdError,
    IncidentPersistenceError,
    IncidentPersistenceResult,
    LockContentionError,
    LockError,
    LockMetadata,
    LockOwnerMismatchError,
    LockReleaseFailureError,
    SingleWriterLock,
    UnresolvedRecoveryStateError,
)
from flight_pipeline.storage.publication import PublicationResult, SafePublisher
from flight_pipeline.utils.run_manifest import RowAccounting, RunManifest


class TestT011R6PresignoffClosure(unittest.TestCase):
    """Authoritative test suite for findings PC-F01 and PC-F02."""

    # =========================================================================
    # PC-F01: RELEASE FAILURE RECOVERY BOUNDARY & WRITER ADMISSION
    # =========================================================================

    def test_pcf01_01_normal_acquire_release_new_acquire_succeeds(self):
        """PC-F01 Test 1: Normal acquire, release, and subsequent acquire succeeds cleanly."""
        with tempfile.TemporaryDirectory() as td:
            ld = Path(td)
            lock_a = SingleWriterLock(ld, run_id="run_1_a")
            with lock_a:
                self.assertTrue(lock_a.is_acquired)
                self.assertTrue(lock_a.lock_file_path.exists())

            self.assertFalse(lock_a.is_acquired)
            self.assertFalse(lock_a.lock_file_path.exists())
            self.assertEqual(len(lock_a.get_unresolved_recovery_artifacts()), 0)

            lock_b = SingleWriterLock(ld, run_id="run_1_b")
            with lock_b:
                self.assertTrue(lock_b.is_acquired)
            self.assertFalse(lock_b.is_acquired)

    def test_pcf01_02_staging_unlink_failure_produces_release_incident(self):
        """PC-F01 Test 2: Staging unlink permission failure produces an auditable release incident."""
        with tempfile.TemporaryDirectory() as td:
            ld = Path(td)
            lock = SingleWriterLock(ld, run_id="run_2")
            lock.acquire()

            orig_unlink = Path.unlink
            def fake_unlink(self_path, *args, **kwargs):
                if ".del_" in self_path.name:
                    raise PermissionError("Simulated NTFS access denied on staging deletion")
                return orig_unlink(self_path, *args, **kwargs)

            Path.unlink = fake_unlink
            try:
                with self.assertRaises(LockError) as cm:
                    lock.release()
            finally:
                Path.unlink = orig_unlink

            self.assertIn("Failed to delete isolated lock file", str(cm.exception))
            # Persist incident report
            inc_res = lock.persist_release_incident(release_err=cm.exception)
            self.assertTrue(inc_res.success)
            self.assertTrue(inc_res.verified)
            self.assertTrue(inc_res.incident_file.exists())

            inc_data = json.loads(inc_res.incident_file.read_text(encoding="utf-8"))
            self.assertEqual(inc_data["event"], "LOCK_RELEASE_FAILURE")
            self.assertEqual(inc_data["recovery_status"], "MANUAL_RECOVERY_REQUIRED")

    def test_pcf01_03_new_writer_is_blocked_after_unresolved_staging_failure(self):
        """PC-F01 Test 3: New writer is blocked with UnresolvedRecoveryStateError after staging failure."""
        with tempfile.TemporaryDirectory() as td:
            ld = Path(td)
            lock_a = SingleWriterLock(ld, run_id="run_3_a")
            lock_a.acquire()

            orig_unlink = Path.unlink
            def fake_unlink(self_path, *args, **kwargs):
                if ".del_" in self_path.name:
                    raise PermissionError("Simulated locked file handle")
                return orig_unlink(self_path, *args, **kwargs)

            Path.unlink = fake_unlink
            try:
                with self.assertRaises(LockError):
                    lock_a.release()
            finally:
                Path.unlink = orig_unlink

            # Verify that canonical lock is absent but staging/marker files exist
            self.assertFalse(lock_a.lock_file_path.exists())
            unresolved = lock_a.get_unresolved_recovery_artifacts()
            self.assertGreaterEqual(len(unresolved), 1)

            # New writer Run B calls acquire - MUST FAIL CLOSED
            lock_b = SingleWriterLock(ld, run_id="run_3_b")
            with self.assertRaises(UnresolvedRecoveryStateError) as cm:
                lock_b.acquire()

            self.assertIn("FAIL_CLOSED — MANUAL_RECOVERY_REQUIRED", str(cm.exception))
            self.assertIn("unresolved recovery artifacts detected", str(cm.exception))
            self.assertFalse(lock_b.is_acquired)

    def test_pcf01_04_simulated_process_crash_after_rename_is_detected_and_blocks(self):
        """PC-F01 Test 4: A simulated process crash right after rename is detected and blocks new writer."""
        with tempfile.TemporaryDirectory() as td:
            ld = Path(td)
            # Create orphaned staging file and release marker representing crashed process
            crashed_token = "crashed_owner_token_xyz"
            staging_del = ld / f"..pipeline.lock.del_{crashed_token}"
            staging_del.write_text("{\"owner_token\": \"crashed_owner_token_xyz\"}", encoding="utf-8")
            marker = ld / f"..pipeline.lock.release_in_progress_{crashed_token}"
            marker.write_text("{\"event\": \"RELEASE_IN_PROGRESS\"}", encoding="utf-8")

            # Subsequent writer attempts acquire
            new_writer = SingleWriterLock(ld, run_id="run_4_crashed_recovery")
            with self.assertRaises(UnresolvedRecoveryStateError) as cm:
                new_writer.acquire()

            self.assertIn("FAIL_CLOSED — MANUAL_RECOVERY_REQUIRED", str(cm.exception))
            self.assertFalse(new_writer.is_acquired)

    def test_pcf01_05_no_automatic_cleanup_of_unknown_owner_artifacts(self):
        """PC-F01 Test 5: Acquisition strictly refuses to automatically delete or steal unknown recovery files."""
        with tempfile.TemporaryDirectory() as td:
            ld = Path(td)
            unknown_artifact = ld / "..pipeline.lock.del_unknown_foreign_owner"
            unknown_artifact.write_text("{\"owner_token\": \"unknown_owner\"}", encoding="utf-8")

            writer = SingleWriterLock(ld, run_id="run_5_no_steal")
            with self.assertRaises(UnresolvedRecoveryStateError):
                writer.acquire()

            # Verify unknown artifact was NOT deleted
            self.assertTrue(unknown_artifact.exists(), "Unknown artifact must be preserved intact")

    def test_pcf01_06_authorized_manual_recovery_restores_normal_acquisition(self):
        """PC-F01 Test 6: Authorized operator recovery archives artifacts and restores normal acquisition."""
        with tempfile.TemporaryDirectory() as td:
            ld = Path(td)
            lock_a = SingleWriterLock(ld, run_id="run_6_a")
            lock_a.acquire()

            # Trigger staging failure
            orig_unlink = Path.unlink
            def fake_unlink(self_path, *args, **kwargs):
                if ".del_" in self_path.name:
                    raise PermissionError("NTFS locked handle")
                return orig_unlink(self_path, *args, **kwargs)

            Path.unlink = fake_unlink
            try:
                with self.assertRaises(LockError):
                    lock_a.release()
            finally:
                Path.unlink = orig_unlink

            lock_b = SingleWriterLock(ld, run_id="run_6_b")
            with self.assertRaises(UnresolvedRecoveryStateError):
                lock_b.acquire()

            # Unauthorized recovery rejected
            with self.assertRaises(LockError):
                lock_b.resolve_recovery_state(authorized=False, operator="admin", reason="cleanup")

            # Missing operator or reason rejected
            with self.assertRaises(ValueError):
                lock_b.resolve_recovery_state(authorized=True, operator="", reason="cleanup")
            with self.assertRaises(ValueError):
                lock_b.resolve_recovery_state(authorized=True, operator="admin", reason="")

            # Authorized recovery executed
            rec_res = lock_b.resolve_recovery_state(
                authorized=True,
                operator="lead_operator_01",
                reason="Inspected staging file from run_6_a; confirmed pipeline outputs safe and process dead.",
            )
            self.assertTrue(rec_res["resolved"])
            self.assertGreaterEqual(rec_res["count"], 1)
            self.assertTrue(Path(rec_res["resolution_record_file"]).exists())

            # Now new writer can acquire cleanly!
            lock_b.acquire()
            self.assertTrue(lock_b.is_acquired)
            lock_b.release()
            self.assertFalse(lock_b.is_acquired)

    def test_pcf01_07_two_cooperating_processes_cannot_publish_simultaneously(self):
        """PC-F01 Test 7: Two cooperating processes cannot acquire lock or publish simultaneously."""
        with tempfile.TemporaryDirectory() as td:
            ld = Path(td)
            lock1 = SingleWriterLock(ld, run_id="proc_1")
            lock2 = SingleWriterLock(ld, run_id="proc_2")

            lock1.acquire()
            self.assertTrue(lock1.is_acquired)

            with self.assertRaises(LockContentionError) as cm:
                lock2.acquire()

            self.assertIn("Lock contention", str(cm.exception))
            self.assertFalse(lock2.is_acquired)

            lock1.release()
            lock2.acquire()
            self.assertTrue(lock2.is_acquired)
            lock2.release()

    def test_pcf01_08_previously_published_outputs_and_latest_pointer_remain_unchanged(self):
        """PC-F01 Test 8: Staging failure and recovery never modify published Parquet outputs or latest pointer."""
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            curated_dir = root / "data" / "curated"
            runs_dir = curated_dir / "runs" / "run_pub_08"
            runs_dir.mkdir(parents=True, exist_ok=True)
            dummy_parquet = runs_dir / "part-0000.parquet"
            dummy_parquet.write_text("MOCK_PARQUET_CONTENT_IMMUTABLE", encoding="utf-8")
            orig_parquet_bytes = dummy_parquet.read_bytes()

            ptr_file = curated_dir / "latest_run_id.txt"
            ptr_file.write_text("run_pub_08\n", encoding="utf-8")

            # Run recovery on lock dir
            ld = root / "data" / "staging" / ".locks"
            ld.mkdir(parents=True, exist_ok=True)
            dummy_del = ld / "..pipeline.lock.del_dummy"
            dummy_del.write_text("{\"owner_token\": \"dummy\"}", encoding="utf-8")

            lock = SingleWriterLock(ld, run_id="run_pub_08")
            rec_res = lock.resolve_recovery_state(
                authorized=True,
                operator="operator_auditor",
                reason="Verifying published preservation",
            )
            self.assertTrue(rec_res["resolved"])

            # Verify published output and pointer remain byte-exact identical
            self.assertEqual(dummy_parquet.read_bytes(), orig_parquet_bytes)
            self.assertEqual(ptr_file.read_text(encoding="utf-8").strip(), "run_pub_08")

    def test_pcf01_09_idempotent_repeated_recovery_does_not_destroy_evidence(self):
        """PC-F01 Test 9: Calling manual recovery repeatedly is idempotent and does not corrupt archives."""
        with tempfile.TemporaryDirectory() as td:
            ld = Path(td)
            staging_del = ld / "..pipeline.lock.del_idem"
            staging_del.write_text("{\"token\": \"test_idem\"}", encoding="utf-8")

            lock = SingleWriterLock(ld, run_id="run_idem")
            res1 = lock.resolve_recovery_state(authorized=True, operator="op1", reason="First run")
            self.assertEqual(res1["count"], 1)

            # Second run: zero files remaining, returns cleanly
            res2 = lock.resolve_recovery_state(authorized=True, operator="op1", reason="Second run")
            self.assertTrue(res2["resolved"])
            self.assertEqual(res2["count"], 0)

            # Archive file from first run still exists intact
            archived = Path(res1["archived_artifacts"][0]["archived_path"])
            self.assertTrue(archived.exists())

    def test_pcf01_10_break_stale_lock_staging_failure_blocks_new_writer(self):
        """PC-F01 Test 10: If staging unlink fails during break_stale_lock, new writer is blocked."""
        with tempfile.TemporaryDirectory() as td:
            ld = Path(td)
            # Create a stale lock file with dead PID
            dead_pid = 999999
            stale_meta = LockMetadata(
                owner_token="stale_owner_token",
                run_id="run_stale_10",
                pid=dead_pid,
                hostname=platform.node(),
                created_at=datetime.now(timezone.utc).isoformat(),
            )
            lock_file = ld / ".pipeline.lock"
            lock_file.write_text(stale_meta.to_json(), encoding="utf-8")

            lock = SingleWriterLock(ld, run_id="run_breaker")

            # Force PID liveness to dead
            with patch("flight_pipeline.storage.locking.get_pid_liveness", return_value=SingleWriterLock._read_existing_metadata):
                pass

            orig_unlink = Path.unlink
            def fake_unlink(self_path, *args, **kwargs):
                if ".del_" in self_path.name:
                    raise PermissionError("Locked file handle")
                return orig_unlink(self_path, *args, **kwargs)

            Path.unlink = fake_unlink
            try:
                with patch("flight_pipeline.storage.locking.get_pid_liveness") as mock_live:
                    from flight_pipeline.storage.locking import PidLivenessStatus
                    mock_live.return_value = PidLivenessStatus.PROCESS_DEAD
                    with self.assertRaises(LockError):
                        lock.break_stale_lock(force=True)
            finally:
                Path.unlink = orig_unlink

            # Verify that subsequent writer is blocked!
            writer = SingleWriterLock(ld, run_id="new_run_after_break_fail")
            with self.assertRaises(UnresolvedRecoveryStateError):
                writer.acquire()

    # =========================================================================
    # PC-F02: INCIDENT FILE PERSISTENCE DURABILITY & NO FALSE SUCCESS
    # =========================================================================

    def test_pcf02_01_incident_json_persisted_and_verified_successfully(self):
        """PC-F02 Test 1: Incident JSON is durably persisted and verified on disk."""
        with tempfile.TemporaryDirectory() as td:
            ld = Path(td)
            lock = SingleWriterLock(ld, run_id="run_inc_01")
            res = lock.persist_release_incident(release_err=PermissionError("Simulated unlink failure"))

            self.assertIsInstance(res, IncidentPersistenceResult)
            self.assertTrue(res.success)
            self.assertTrue(res.verified)
            self.assertIsNotNone(res.incident_file)
            self.assertTrue(res.incident_file.exists())
            self.assertGreater(res.bytes_written, 0)
            self.assertIsNone(res.error)

            # Readback validation
            data = json.loads(res.incident_file.read_text(encoding="utf-8"))
            self.assertEqual(data["event"], "LOCK_RELEASE_FAILURE")
            self.assertEqual(data["release_error_type"], "PermissionError")
            self.assertEqual(data["recovery_status"], "MANUAL_RECOVERY_REQUIRED")

    def test_pcf02_02_disk_full_during_incident_write_reports_failure(self):
        """PC-F02 Test 2: Disk full (OSError) during incident write returns success=False without false claims."""
        with tempfile.TemporaryDirectory() as td:
            ld = Path(td)
            lock = SingleWriterLock(ld, run_id="run_inc_02")

            with patch("os.write", side_effect=OSError(errno.ENOSPC, "No space left on device")):
                res = lock.persist_release_incident(release_err=PermissionError("Release failed"))

            self.assertFalse(res.success)
            self.assertFalse(res.verified)
            self.assertIsNone(res.incident_file)
            self.assertIn("No space left on device", res.error)

            # Verify 0 incident files created
            incidents = list(ld.glob("lock_release_incident_*.json"))
            self.assertEqual(len(incidents), 0)

    def test_pcf02_03_permission_denied_during_incident_write_reports_failure(self):
        """PC-F02 Test 3: Permission denied during incident write reports failure truthfully."""
        with tempfile.TemporaryDirectory() as td:
            ld = Path(td)
            lock = SingleWriterLock(ld, run_id="run_inc_03")

            with patch("os.open", side_effect=PermissionError(errno.EACCES, "Access is denied")):
                res = lock.persist_release_incident(release_err=PermissionError("Release failed"))

            self.assertFalse(res.success)
            self.assertFalse(res.verified)
            self.assertIsNone(res.incident_file)
            self.assertIn("Access is denied", res.error)

    def test_pcf02_04_partial_interrupted_json_write_fails_verification(self):
        """PC-F02 Test 4: Short/interrupted write fails durability check."""
        with tempfile.TemporaryDirectory() as td:
            ld = Path(td)
            lock = SingleWriterLock(ld, run_id="run_inc_04")

            # Simulate writing only 5 bytes instead of full payload
            orig_write = os.write
            def short_write(fd, data):
                return 5

            with patch("os.write", side_effect=short_write):
                res = lock.persist_release_incident(release_err=PermissionError("Release failed"))

            self.assertFalse(res.success)
            self.assertFalse(res.verified)
            self.assertIn("Short write", res.error)

    def test_pcf02_05_incident_path_not_created_returns_none_incident_file(self):
        """PC-F02 Test 5: When write fails, incident_file attribute is strictly None."""
        with tempfile.TemporaryDirectory() as td:
            ld = Path(td)
            lock = SingleWriterLock(ld, run_id="run_inc_05")

            with patch("os.replace", side_effect=OSError("Atomic rename failed")):
                res = lock.persist_release_incident(release_err=PermissionError("Release failed"))

            self.assertFalse(res.success)
            self.assertIsNone(res.incident_file)

    def test_pcf02_06_atomic_rename_failure_reports_failure_truthfully(self):
        """PC-F02 Test 6: os.replace failure reports atomic rename error truthfully."""
        with tempfile.TemporaryDirectory() as td:
            ld = Path(td)
            lock = SingleWriterLock(ld, run_id="run_inc_06")

            with patch("os.replace", side_effect=OSError("Target locked on Windows")):
                res = lock.persist_release_incident(release_err=PermissionError("Release failed"))

            self.assertFalse(res.success)
            self.assertIn("Target locked on Windows", res.error)

    def test_pcf02_07_readback_payload_mismatch_fails_verification(self):
        """PC-F02 Test 7: If file content does not match expected payload on readback, verification fails."""
        with tempfile.TemporaryDirectory() as td:
            ld = Path(td)
            lock = SingleWriterLock(ld, run_id="run_inc_07")

            with patch.object(Path, "read_bytes", return_value=b"CORRUPTED_READBACK_BYTES"):
                res = lock.persist_release_incident(release_err=PermissionError("Release failed"))

            self.assertFalse(res.success)
            self.assertIn("Readback verification failed", res.error)

    def test_pcf02_08_pipeline_exception_plus_release_exception_chained(self):
        """PC-F02 Test 8: Context manager preserves pipeline exception as __cause__ with truthful incident status."""
        with tempfile.TemporaryDirectory() as td:
            ld = Path(td)
            lock = SingleWriterLock(ld, run_id="run_inc_08")

            # 8a: Successful incident persistence
            with self.assertRaises(LockReleaseFailureError) as cm:
                with lock:
                    # Corrupt token so release fails
                    lock.lock_file_path.write_text("{\"owner_token\": \"foreign\"}", encoding="utf-8")
                    raise ValueError("Pipeline verification exception")

            self.assertIsInstance(cm.exception.__cause__, ValueError)
            self.assertIn("Incident persisted at", str(cm.exception))
            self.assertIn("FAIL_CLOSED — MANUAL_RECOVERY_REQUIRED", str(cm.exception))

            # 8b: Failed incident persistence in separate directory
            with tempfile.TemporaryDirectory() as td2:
                ld2 = Path(td2)
                lock2 = SingleWriterLock(ld2, run_id="run_inc_08_b")
                with patch("os.replace", side_effect=OSError("Disk write error")):
                    with self.assertRaises(LockReleaseFailureError) as cm2:
                        with lock2:
                            lock2.lock_file_path.write_text("{\"owner_token\": \"foreign\"}", encoding="utf-8")
                            raise TypeError("Original type error in pipeline")

                self.assertIsInstance(cm2.exception.__cause__, TypeError)
                self.assertIn("INCIDENT_PERSISTENCE_FAILED", str(cm2.exception))
                self.assertNotIn("Incident persisted at", str(cm2.exception))

    def test_pcf02_09_published_success_plus_release_exception_preserves_published(self):
        """PC-F02 Test 9: Coordinator preserves success=True when published run encounters release failure."""
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source_validator = SourceValidator(base_dir=root)
            coordinator = IngestionCoordinator(
                spark=MagicMock(),
                base_data_dir=root,
                source_validator=source_validator,
            )
            runs_dir = coordinator.curated_root / "runs"
            run_id = "run_pub_inc_09"
            run_meta = coordinator.metadata_root / run_id
            run_meta.mkdir(parents=True, exist_ok=True)

            accounting = RowAccounting(raw_row_count=100, accepted_row_count=100, quarantined_row_count=0, rejected_row_count=0)
            pub_res = PublicationResult(
                success=True,
                run_id=run_id,
                status="PUBLISHED",
                published_path=str(runs_dir / run_id),
                pointer_value=run_id,
            )

            def mock_write_parquet(df, path, *args, **kwargs):
                path.mkdir(parents=True, exist_ok=True)
                (path / "part-0.parquet").write_text("dummy", encoding="utf-8")
                return (100, ["col1"])

            def mock_publish(*args, **kwargs):
                (runs_dir / run_id).mkdir(parents=True, exist_ok=True)
                (runs_dir / run_id / "part-0.parquet").write_text("dummy_parquet", encoding="utf-8")
                return pub_res

            def failing_release(self_lock):
                if self_lock._fd is not None:
                    try:
                        os.close(self_lock._fd)
                    except Exception:
                        pass
                    self_lock._fd = None
                raise LockOwnerMismatchError("Simulated post-publication release collision")

            mock_df = MagicMock()
            mock_df.filter.return_value.groupBy.return_value.agg.return_value.collect.return_value = []

            mock_src_ver = MagicMock(
                all_passed=True,
                to_dict=lambda: {"results": {2024: {"path": "dummy.csv", "actual_byte_size": 100, "computed_sha256": "a" * 64}}},
                results={2024: MagicMock(path="dummy.csv", actual_byte_size=100, computed_sha256="a" * 64)},
            )
            mock_scan = MagicMock(
                physical_rows=100,
                logical_records=100,
                accepted=100,
                quarantined=0,
                rejected=0,
                anomalies={},
                corrupted_samples=[],
                to_dict=lambda: {"rows": 100},
            )

            coordinator.reader = MagicMock()
            coordinator.reader.read_raw.return_value = MagicMock()

            with patch.object(coordinator, "_verify_target_sources", return_value=mock_src_ver), \
                 patch("flight_pipeline.ingestion.coordinator.scan_csv_logical_records", return_value=mock_scan), \
                 patch("flight_pipeline.ingestion.coordinator.IngestionRecordClassifier.classify", return_value=mock_df), \
                 patch("flight_pipeline.ingestion.coordinator.IngestionTransformer.to_curated", return_value=mock_df), \
                 patch("flight_pipeline.ingestion.coordinator.F.col"), \
                 patch("flight_pipeline.ingestion.coordinator.F.count"), \
                 patch("flight_pipeline.ingestion.coordinator.F.lit"), \
                 patch("flight_pipeline.ingestion.coordinator.compute_per_year_accounting", return_value=(accounting, {2024: accounting})), \
                 patch("flight_pipeline.ingestion.coordinator.persist_forensic_records", return_value=MagicMock(to_dict=lambda: {"quarantine_dir": str(root / "q")}, quarantine_dir=str(root / "q"))), \
                 patch("flight_pipeline.ingestion.coordinator.verify_parquet_directory_integrity"), \
                 patch.object(coordinator.publisher, "publish", side_effect=mock_publish), \
                 patch("flight_pipeline.ingestion.coordinator.write_dataframe_parquet_safe", side_effect=mock_write_parquet), \
                 patch.object(SingleWriterLock, "release", failing_release):

                outcome = coordinator.run_ingestion(run_id=run_id, years=[2024])

            self.assertTrue(outcome.success, "Published run must preserve success=True")
            self.assertEqual(outcome.final_state, PipelineState.PUBLISHED)
            self.assertIsNotNone(outcome.release_error)
            self.assertIsNotNone(outcome.release_incident)
            self.assertTrue(outcome.release_incident["recovery_required"])

    def test_pcf02_10_both_primary_and_secondary_writes_fail_no_false_success(self):
        """PC-F02 Test 10: When both primary and secondary persistence fail, failure is reported truthfully."""
        with tempfile.TemporaryDirectory() as td:
            ld = Path(td)
            sec_dir = ld / "secondary_backup"
            lock = SingleWriterLock(ld, run_id="run_inc_10")

            with patch("os.open", side_effect=OSError("Read-only filesystem")):
                res = lock.persist_release_incident(
                    release_err=PermissionError("Release failed"),
                    secondary_dir=sec_dir,
                )

            self.assertFalse(res.success)
            self.assertFalse(res.verified)
            self.assertIsNone(res.incident_file)
            self.assertIn("Primary persistence failed", res.error)
            self.assertIn("Secondary persistence failed", res.error)


if __name__ == "__main__":
    unittest.main()
