"""
T-011 R6 Pre-Signoff Addendum Test Suite.
Verifies and prevents:
1. PS-01 (HIGH): Lock release errors must NEVER be silently suppressed (__exit__ and coordinator finally).
2. PS-01: Context manager exception chaining (LockReleaseFailureError chains original pipeline exception).
3. PS-01: Immutable published outputs are preserved when post-publication release fails (non-destructive).
4. PS-01: Coordinator preserves original error and appends release failure diagnostics on pipeline failure.
5. PS-01: Explicit auditable incident files persisted for all release failures.
6. PS-02 (GOVERNANCE): Complete 27-document attestation table verification.
7. PS-03 (BOUNDED LIMITATION): Injected fstat failure leaves incomplete lock, fails closed, and requires manual recovery.
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
import unittest
from unittest.mock import MagicMock, patch

SRC_DIR = Path(__file__).resolve().parents[1] / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))
ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from flight_pipeline.ingestion.coordinator import (
    ExecutionReceipt,
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
    LockContentionError,
    LockError,
    LockMetadata,
    LockOwnerMismatchError,
    LockReleaseFailureError,
    SingleWriterLock,
)
from flight_pipeline.storage.publication import PublicationResult, SafePublisher
from flight_pipeline.utils.run_manifest import RowAccounting, RunManifest


class TestT011R6Presignoff(unittest.TestCase):
    """Pre-signoff addendum regression test suite."""

    # =========================================================================
    # PS-01: LOCK RELEASE SILENT SUPPRESSION & CHAINING TESTS
    # =========================================================================

    def test_ps01_01_normal_release_clean_exit(self):
        """PS-01: Normal context manager exit releases lock cleanly without error."""
        with tempfile.TemporaryDirectory() as td:
            lock_dir = Path(td)
            lock = SingleWriterLock(lock_dir, run_id="run_ps01_norm")
            with lock:
                self.assertTrue(lock.is_acquired)
                self.assertTrue(lock.lock_file_path.exists())

            self.assertFalse(lock.is_acquired)
            self.assertFalse(lock.lock_file_path.exists())
            incidents = list(lock_dir.glob("lock_release_incident_*.json"))
            self.assertEqual(len(incidents), 0)

    def test_ps01_02_owner_mismatch_raises_in_exit(self):
        """PS-01: Owner mismatch during __exit__ must raise LockOwnerMismatchError, not pass silently."""
        with tempfile.TemporaryDirectory() as td:
            lock_dir = Path(td)
            lock = SingleWriterLock(lock_dir, run_id="run_ps01_mismatch")

            with self.assertRaises(LockOwnerMismatchError) as cm:
                with lock:
                    self.assertTrue(lock.is_acquired)
                    # Corrupt lock file with foreign owner token
                    imposter_meta = LockMetadata(
                        owner_token="imposter_token_xyz",
                        run_id="run_ps01_mismatch",
                        pid=os.getpid(),
                        hostname=platform.node(),
                        created_at=datetime.now(timezone.utc).isoformat(),
                    )
                    lock.lock_file_path.write_text(imposter_meta.to_json(), encoding="utf-8")

            self.assertIn("Lock owner mismatch", str(cm.exception))
            # Verify incident file persisted
            incidents = list(lock_dir.glob("lock_release_incident_*.json"))
            self.assertEqual(len(incidents), 1)
            inc_data = json.loads(incidents[0].read_text(encoding="utf-8"))
            self.assertEqual(inc_data["event"], "LOCK_RELEASE_FAILURE")
            self.assertEqual(inc_data["release_error_type"], "LockOwnerMismatchError")
            self.assertEqual(inc_data["recovery_status"], "MANUAL_RECOVERY_REQUIRED")

    def test_ps01_03_permission_io_failure_raises_in_exit(self):
        """PS-01: I/O failure during rename in release must propagate as LockError and persist incident."""
        with tempfile.TemporaryDirectory() as td:
            lock_dir = Path(td)
            lock = SingleWriterLock(lock_dir, run_id="run_ps01_io")

            with patch("os.rename", side_effect=OSError(errno.EACCES, "Permission denied during isolated rename")):
                with self.assertRaises(LockError) as cm:
                    with lock:
                        self.assertTrue(lock.is_acquired)

            self.assertIn("Failed to isolate lock file for deletion", str(cm.exception))
            incidents = list(lock_dir.glob("lock_release_incident_*.json"))
            self.assertEqual(len(incidents), 1)
            inc_data = json.loads(incidents[0].read_text(encoding="utf-8"))
            self.assertEqual(inc_data["release_error_type"], "LockError")

    def test_ps01_04_pipeline_exception_with_release_failure_chains(self):
        """PS-01: Block exception + release failure raises LockReleaseFailureError chained from original exception."""
        with tempfile.TemporaryDirectory() as td:
            lock_dir = Path(td)
            lock = SingleWriterLock(lock_dir, run_id="run_ps01_chain")

            with self.assertRaises(LockReleaseFailureError) as cm:
                with lock:
                    # Corrupt owner token so release will fail
                    imposter_meta = LockMetadata(
                        owner_token="imposter_token_chain",
                        run_id="run_ps01_chain",
                        pid=os.getpid(),
                        hostname=platform.node(),
                        created_at=datetime.now(timezone.utc).isoformat(),
                    )
                    lock.lock_file_path.write_text(imposter_meta.to_json(), encoding="utf-8")
                    # Raise primary pipeline exception
                    raise ValueError("Primary pipeline data verification failed")

            # Verify chaining: __cause__ is the original ValueError
            self.assertIsInstance(cm.exception.__cause__, ValueError)
            self.assertEqual(str(cm.exception.__cause__), "Primary pipeline data verification failed")
            self.assertIn("FAIL_CLOSED — MANUAL_RECOVERY_REQUIRED", str(cm.exception))
            self.assertIn("LockOwnerMismatchError", str(cm.exception))

            # Verify incident file persisted recording both errors
            incidents = list(lock_dir.glob("lock_release_incident_*.json"))
            self.assertEqual(len(incidents), 1)
            inc_data = json.loads(incidents[0].read_text(encoding="utf-8"))
            self.assertEqual(inc_data["release_error_type"], "LockOwnerMismatchError")
            self.assertEqual(inc_data["pipeline_error_type"], "ValueError")
            self.assertEqual(inc_data["pipeline_error_message"], "Primary pipeline data verification failed")

    def test_ps01_05_pipeline_exception_with_normal_release_propagates(self):
        """PS-01: Block exception with normal release propagates original exception unchanged."""
        with tempfile.TemporaryDirectory() as td:
            lock_dir = Path(td)
            lock = SingleWriterLock(lock_dir, run_id="run_ps01_norm_err")

            with self.assertRaises(KeyError) as cm:
                with lock:
                    raise KeyError("missing_required_column")

            self.assertEqual(str(cm.exception), "'missing_required_column'")
            self.assertFalse(lock.is_acquired)
            self.assertFalse(lock.lock_file_path.exists())

    def test_ps01_06_coordinator_already_published_preserves_outputs_on_release_error(self):
        """PS-01: Successful publication preserves outputs (success=True) even when release cleanup fails."""
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source_validator = SourceValidator(base_dir=root)
            coordinator = IngestionCoordinator(
                spark=MagicMock(),
                base_data_dir=root,
                source_validator=source_validator,
            )
            lock_dir = coordinator.lock_dir
            meta_dir = coordinator.metadata_root
            curated_dir = coordinator.curated_root
            runs_dir = curated_dir / "runs"
            quarantine_dir = coordinator.quarantine_root

            run_id = "run_pub_pres_01"
            run_meta = meta_dir / run_id
            run_meta.mkdir(parents=True, exist_ok=True)

            # Mock internal pipeline methods so run_ingestion succeeds through publication
            accounting = RowAccounting(
                raw_row_count=100,
                accepted_row_count=100,
                quarantined_row_count=0,
                rejected_row_count=0,
            )
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

            # Simulate execute_run by patching SingleWriterLock.release to raise LockOwnerMismatchError
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
                to_dict=lambda: {"results": {2016: {"path": "dummy.csv", "actual_byte_size": 100, "computed_sha256": "a" * 64}}},
                results={2016: MagicMock(path="dummy.csv", actual_byte_size=100, computed_sha256="a" * 64)},
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
                 patch("flight_pipeline.ingestion.coordinator.compute_per_year_accounting", return_value=(accounting, {2016: accounting})), \
                 patch("flight_pipeline.ingestion.coordinator.persist_forensic_records", return_value=MagicMock(to_dict=lambda: {"quarantine_dir": str(root / "q")}, quarantine_dir=str(root / "q"))), \
                 patch("flight_pipeline.ingestion.coordinator.verify_parquet_directory_integrity"), \
                 patch.object(coordinator.publisher, "publish", side_effect=mock_publish), \
                 patch("flight_pipeline.ingestion.coordinator.write_dataframe_parquet_safe", side_effect=mock_write_parquet), \
                 patch.object(SingleWriterLock, "release", failing_release):

                outcome = coordinator.run_ingestion(run_id=run_id, years=[2016])

            # CRITICAL VERIFICATION:
            # 1. Publication is preserved!
            self.assertTrue(outcome.success)
            self.assertEqual(outcome.final_state, PipelineState.PUBLISHED)
            self.assertTrue((runs_dir / run_id).exists())
            self.assertTrue((runs_dir / run_id / "part-0.parquet").exists())

            # 2. Release failure is not lost!
            self.assertIsNotNone(outcome.release_error)
            self.assertIn("LockOwnerMismatchError: Simulated post-publication release collision", outcome.release_error)
            self.assertIsNotNone(outcome.release_incident)
            self.assertTrue(outcome.release_incident["publication_preserved"])

            # 3. Governance warning declaring manual recovery required
            has_crit_warn = any("CRITICAL_LOCK_RELEASE_FAILURE" in w for w in outcome.governance_warnings)
            self.assertTrue(has_crit_warn)

            # 4. Incident file persisted on disk
            incidents = list(lock_dir.glob("lock_release_incident_*.json"))
            self.assertGreaterEqual(len(incidents), 1)

    def test_ps01_07_coordinator_pipeline_failure_preserves_original_error(self):
        """PS-01: Ingestion failure retains original error message and appends release failure diagnostic."""
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source_validator = SourceValidator(base_dir=root)
            coordinator = IngestionCoordinator(
                spark=MagicMock(),
                base_data_dir=root,
                source_validator=source_validator,
            )
            lock_dir = coordinator.lock_dir

            run_id = "run_pipe_fail_01"

            def failing_release(self_lock):
                if self_lock._fd is not None:
                    try:
                        os.close(self_lock._fd)
                    except Exception:
                        pass
                    self_lock._fd = None
                raise LockError("Disk IO error during release")

            with patch.object(coordinator, "_verify_target_sources", side_effect=FileNotFoundError("Raw CSV missing for 2016")), \
                 patch.object(SingleWriterLock, "release", failing_release):

                outcome = coordinator.run_ingestion(run_id=run_id, years=[2016])

            self.assertFalse(outcome.success)
            self.assertEqual(outcome.final_state, PipelineState.TERMINAL_FAILURE)
            # Original error preserved
            self.assertIn("Raw CSV missing for 2016", outcome.error_message)
            # Release failure appended
            self.assertIn("[LockReleaseFailure: LockError: Disk IO error during release]", outcome.error_message)
            self.assertIsNotNone(outcome.release_error)
            self.assertIsNotNone(outcome.release_incident)

    def test_ps01_08_reconcile_published_run_records_release_incident(self):
        """PS-01: reconcile_published_run captures release error and persists incident."""
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source_validator = SourceValidator(base_dir=root)
            coordinator = IngestionCoordinator(
                spark=MagicMock(),
                base_data_dir=root,
                source_validator=source_validator,
            )
            lock_dir = coordinator.lock_dir
            meta_dir = coordinator.metadata_root
            curated_dir = coordinator.curated_root
            runs_dir = curated_dir / "runs"
            quarantine_dir = coordinator.quarantine_root

            run_id = "run_reconcile_rel_fail_01"
            # Setup published directory and pointer
            (runs_dir / run_id).mkdir(parents=True, exist_ok=True)
            (curated_dir / "latest_run_id.txt").write_text(run_id, encoding="utf-8")

            # Setup sidecars
            run_meta = meta_dir / run_id
            run_meta.mkdir(parents=True, exist_ok=True)
            run_quarantine = quarantine_dir / run_id
            run_quarantine.mkdir(parents=True, exist_ok=True)

            source_ver_data = {
                "run_id": run_id,
                "all_passed": True,
                "results": {
                    "2016": {"path": "dummy_2016.csv", "actual_byte_size": 100, "computed_sha256": "a" * 64}
                },
            }
            accounting = RowAccounting(
                raw_row_count=100,
                accepted_row_count=100,
                quarantined_row_count=0,
                rejected_row_count=0,
            )
            anom_data = {
                "run_id": run_id,
                "row_accounting": accounting.to_dict(),
                "per_year_accounting": {
                    "2016": accounting.to_dict(),
                },
                "source_scan_results": {
                    "2016": {
                        "is_verifiable": True,
                        "logical_data_records": 100,
                    }
                },
                "anomaly_summary": {},
            }
            forensic_data = {
                "run_id": run_id,
                "quarantine_dir": str(run_quarantine),
                "expected_quarantined_count": 0,
                "persisted_quarantined_count": 0,
                "expected_rejected_count": 0,
                "persisted_rejected_count": 0,
                "verified": True,
            }

            (run_meta / "source_verification.json").write_text(json.dumps(source_ver_data), encoding="utf-8")
            (run_meta / "anomaly_summary.json").write_text(json.dumps(anom_data), encoding="utf-8")
            (run_quarantine / "forensic_manifest.json").write_text(json.dumps(forensic_data), encoding="utf-8")

            def failing_release(self_lock):
                if self_lock._fd is not None:
                    try:
                        os.close(self_lock._fd)
                    except Exception:
                        pass
                    self_lock._fd = None
                raise LockOwnerMismatchError("Reconcile release mismatch simulation")

            with patch("flight_pipeline.ingestion.coordinator.verify_parquet_directory_integrity"), \
                 patch.object(SingleWriterLock, "release", failing_release):
                outcome = coordinator.reconcile_published_run(run_id=run_id)

            self.assertTrue(outcome.success)
            self.assertEqual(outcome.final_state, PipelineState.PUBLISHED)
            self.assertIsNotNone(outcome.release_error)
            self.assertIn("LockOwnerMismatchError: Reconcile release mismatch simulation", outcome.release_error)
            self.assertIsNotNone(outcome.release_incident)
            has_crit_warn = any("CRITICAL_LOCK_RELEASE_FAILURE" in w for w in outcome.governance_warnings)
            self.assertTrue(has_crit_warn)

    # =========================================================================
    # PS-02: COMPLETE 27-DOCUMENT ATTESTATION VERIFICATION
    # =========================================================================

    def test_ps02_all_27_canonical_documents_attested(self):
        """PS-02: All 27 canonical markdown documents exist on disk and are non-empty."""
        repo_root = ROOT_DIR
        expected_docs = [
            "AGENTS.md",
            "README.md",
            "START_HERE.md",
            "docs/00-governance/BUILD_QA_REPORT.md",
            "docs/00-governance/DOCS_CONSISTENCY_AUDIT_v1.1.md",
            "docs/00-governance/DOCUMENT_REGISTER.md",
            "docs/00-governance/V1_0_CONSISTENCY_AUDIT.md",
            "docs/01-planning/BACKLOG.md",
            "docs/01-planning/PRD.md",
            "docs/01-planning/ROADMAP.md",
            "docs/02-design/ANALYSIS_PROTOCOL.md",
            "docs/02-design/API_CONTRACTS.md",
            "docs/02-design/ARCHITECTURE.md",
            "docs/02-design/DATA_CONTRACT.md",
            "docs/02-design/DATA_DICTIONARY.md",
            "docs/02-design/DECISIONS.md",
            "docs/02-design/KPI_SPEC.md",
            "docs/03-quality/CHANGELOG.md",
            "docs/03-quality/G0_G1_REVIEW.md",
            "docs/03-quality/RISK_REGISTER.md",
            "docs/03-quality/ROLLBACK_PLAN.md",
            "docs/03-quality/SECURITY.md",
            "docs/03-quality/TEST_PLAN.md",
            "docs/04-execution/AI_HANDOFF.md",
            "docs/04-execution/DEPLOYMENT.md",
            "docs/04-execution/PROJECT_STATE.md",
            "docs/04-execution/TASK_TEMPLATE.md",
        ]

        self.assertEqual(len(expected_docs), 27)
        for doc_rel in expected_docs:
            p = repo_root / doc_rel
            self.assertTrue(p.exists(), f"Document missing: {doc_rel}")
            self.assertTrue(p.is_file(), f"Document is not a file: {doc_rel}")
            size = p.stat().st_size
            self.assertGreater(size, 0, f"Document is empty: {doc_rel}")

    # =========================================================================
    # PS-03: BOUNDED FSTAT RECOVERY LIMITATION TESTS
    # =========================================================================

    def test_ps03_fstat_failure_leaves_incomplete_lock_fail_closed(self):
        """PS-03: Injected fstat failure leaves 0-byte canonical lock, fails closed, and requires manual recovery."""
        with tempfile.TemporaryDirectory() as td:
            lock_dir = Path(td)
            lock1 = SingleWriterLock(lock_dir, run_id="run_ps03_fstat")

            # Inject OSError into os.fstat during lock acquisition
            with patch("os.fstat", side_effect=OSError(errno.EIO, "Simulated fstat I/O bus error")):
                with self.assertRaises(LockError) as cm:
                    lock1.acquire()

            # Diagnostic declares FAIL_CLOSED — MANUAL_RECOVERY_REQUIRED
            self.assertIn("FAIL_CLOSED — MANUAL_RECOVERY_REQUIRED", str(cm.exception))
            self.assertIn("Failed to stat newly created lock file", str(cm.exception))
            self.assertFalse(lock1.is_acquired)

            # Incomplete 0-byte canonical lock remains on disk
            self.assertTrue(lock1.lock_file_path.exists())
            self.assertEqual(lock1.lock_file_path.stat().st_size, 0)

            # Subsequent writer must fail closed with LockContentionError
            lock2 = SingleWriterLock(lock_dir, run_id="run_ps03_writer2")
            with self.assertRaises(LockContentionError):
                lock2.acquire()

            # Automatic break_stale_lock must refuse to break unparseable 0-byte lock
            with self.assertRaises(LockContentionError) as break_cm:
                lock2.break_stale_lock(force=True)
            self.assertIn("FAIL_CLOSED — MANUAL_RECOVERY_REQUIRED", str(break_cm.exception))
            self.assertIn("unparseable or corrupted lock file", str(break_cm.exception))

            # Controlled manual recovery procedure (PS-03):
            # Operator verifies process quiescence, removes the orphaned 0-byte file
            lock1.lock_file_path.unlink()

            # After manual recovery, subsequent writer acquires successfully
            lock2.acquire()
            self.assertTrue(lock2.is_acquired)
            lock2.release()
            self.assertFalse(lock2.is_acquired)


if __name__ == "__main__":
    unittest.main()
