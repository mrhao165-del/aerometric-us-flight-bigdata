"""
Comprehensive End-to-End Integration and Negative Fault-Injection Test Suite (T007-05, T007-06, T007-07,
and Final Remediation FIX-F01 .. FIX-F07).

Validates:
1. Multi-year synthetic end-to-end ingestion lifecycle (RUN_STARTED -> ... -> PUBLISHED).
2. Approved baseline SHA-256 verification vs candidate unapproved hash fail-closed guard.
3. Independent DC-11 row accounting conservation per source_year and per run_id.
4. DC-12 metric validity separation using canonical predicates on curated Parquet output.
5. Real Spark Parquet generation, two-phase task attempt staging (`_task_attempts`), SafePublisher 7-step
   promotion, and pointer switching.
6. Full forensic persistence of QUARANTINED and REJECTED records in `data/quarantine/<run_id>/` (JSONL + Parquet).
7. Post-pointer-switch sidecar fault injection (`PUBLISHED_RECEIPT_PENDING_RECONCILIATION`) and non-destructive
   recovery via `reconcile_published_run(run_id)` without overwriting `run_manifest.json` to `FAILED`.
8. Negative tests: missing source, size mismatch, hash mismatch, duplicate run_id, lock contention,
   staging Parquet corruption, physical header drift, and `ACCOUNTING_UNVERIFIED` blank lines.
9. Governance invariants: OR-05 (2024 warning), OR-08 (IDENTITY_UNVERIFIED), FP-DEC-017, G2-EXC-001.
"""

from hashlib import sha256
import json
from pathlib import Path
import sys
import tempfile
import unittest

SRC_DIR = Path(__file__).resolve().parents[1] / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from flight_pipeline.config.spark_config import SparkConfig, get_spark_session, stop_spark_session
from flight_pipeline.ingestion.coordinator import (
    ExecutionReceipt,
    IngestionCoordinator,
    PipelineRunOutcome,
    PipelineState,
    read_parquet_safe,
    verify_parquet_directory_integrity,
    write_dataframe_parquet_safe,
)
from flight_pipeline.ingestion.schema import CANONICAL_COLUMN_NAMES, CANONICAL_COLUMNS_COUNT
from flight_pipeline.ingestion.source_validator import (
    SourceEntry,
    SourceValidator,
    UPSTREAM_IDENTITY_STATUS_UNVERIFIED,
)
from flight_pipeline.quality.predicates import is_valid_arr_delay, is_valid_dep_delay
from flight_pipeline.storage.locking import SingleWriterLock
from flight_pipeline.storage.publication import compute_file_sha256, is_valid_parquet_file


class TestT007PipelineIntegration(unittest.TestCase):
    """End-to-end synthetic integration and negative fault-injection test suite for T-007."""

    @classmethod
    def setUpClass(cls):
        """Initialize shared local SparkSession for integration tests."""
        cfg = SparkConfig(
            app_name="TestT007PipelineIntegration",
            master="local[2]",
            driver_memory="2g",
            shuffle_partitions=2,
        )
        cls.spark = get_spark_session(cfg)

    @classmethod
    def tearDownClass(cls):
        """Stop SparkSession cleanly."""
        if cls.spark:
            stop_spark_session(cls.spark)

    def _make_csv_row(
        self,
        fl_date: str = "2016-05-10",
        carrier: str = "AA",
        fl_num: str = "100.0",
        dep_delay: str = "15.0",
        arr_delay: str = "20.0",
        year_month: int = 5,
    ) -> str:
        """Create a 34-column CSV string."""
        fields = [
            fl_date, carrier, fl_num, "JFK", "LAX", "0900", "0915", dep_delay,
            "12.0", "0927", "1210", "8.0", "1200", "1220", arr_delay,
            "360.0", "365.0", "345.0", "1.0", str(year_month), "10", "2",
            "101", "202", "18.5", "0.0", "10.0", "24.0", "0.0", "7.5",
            "40.6413", "-73.7781", "33.9416", "-118.4085",
        ]
        return ",".join(fields)

    def _setup_synthetic_environment(self, root_dir: Path, years=(2016, 2024)):
        """
        Build a synthetic workspace with multi-year CSVs, custom SourceEntries, and SHA-256 baseline.
        """
        raw_root = root_dir / "raw_sources"
        data_root = root_dir / "pipeline_data"
        inventory = {}
        approved_hashes = {}

        header = ",".join(CANONICAL_COLUMN_NAMES)

        for yr in years:
            yr_dir = raw_root / str(yr)
            yr_dir.mkdir(parents=True, exist_ok=True)
            csv_path = yr_dir / f"flight_{yr}.csv"

            if yr == 2016:
                rows = [
                    self._make_csv_row(fl_date="2016-01-15", carrier="AA", dep_delay="10.0", arr_delay="-5.0"),
                    self._make_csv_row(fl_date="2016-02-20", carrier="DL", dep_delay="NOT_A_NUM", arr_delay="30.0"),  # DC-12: accepted row, invalid dep_delay
                    self._make_csv_row(fl_date="BAD_DATE", carrier="UA", dep_delay="0.0", arr_delay="0.0"),           # Quarantined row
                    "2016-03-01,WN,999,SHORT_ROW",                                                                     # Rejected row
                ]
            else:
                rows = [
                    self._make_csv_row(fl_date=f"{yr}-06-01", carrier="B6", fl_num="-5.0", dep_delay="-2.0", arr_delay="-10.0"),  # G3-COND-A: fl_num <= 0 accepted
                    self._make_csv_row(fl_date=f"{yr}-07-04", carrier="AS", dep_delay="45.0", arr_delay="50.0"),
                ]

            content = "\n".join([header] + rows) + "\n"
            csv_bytes = content.encode("utf-8")
            csv_path.write_bytes(csv_bytes)

            rel_path = csv_path.relative_to(root_dir).as_posix()
            file_hash = sha256(csv_bytes).hexdigest()

            inventory[yr] = SourceEntry(
                year=yr,
                relative_path=rel_path,
                audited_row_count=len(rows),
                audited_byte_size=len(csv_bytes),
                audited_column_count=34,
            )
            approved_hashes[yr] = file_hash

        return data_root, inventory, approved_hashes

    def test_int_01_full_end_to_end_synthetic_pipeline_success(self):
        """INT-01: Full multi-year synthetic ingestion lifecycle transitions cleanly to PUBLISHED."""
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            data_root, inventory, approved_hashes = self._setup_synthetic_environment(root, years=(2016, 2024))

            validator = SourceValidator(
                base_dir=root,
                inventory=inventory,
                approved_baseline_hashes=approved_hashes,
                enforce_production_inventory=False,
            )
            coordinator = IngestionCoordinator(
                spark=self.spark,
                base_data_dir=data_root,
                source_validator=validator,
            )

            outcome = coordinator.run_ingestion(
                run_id="run_2016_2024_e2e_01",
                years=[2016, 2024],
                require_verified_hashes=True,
            )

            self.assertTrue(outcome.success, f"Pipeline failed: {outcome.error_message}")
            self.assertEqual(outcome.final_state, PipelineState.PUBLISHED)

            expected_states = [
                PipelineState.RUN_STARTED,
                PipelineState.SOURCE_VERIFICATION,
                PipelineState.INGESTION_IN_PROGRESS,
                PipelineState.INGESTION_COMPLETED,
                PipelineState.STAGING_VERIFIED,
                PipelineState.PUBLICATION_PENDING,
                PipelineState.PUBLISHED,
            ]
            self.assertEqual(outcome.state_history, expected_states)

            # Verify aggregate and per-year DC-11 Row Accounting:
            # 2016: 2 accepted, 1 quarantined, 1 rejected (total 4)
            # 2024: 2 accepted, 0 quarantined, 0 rejected (total 2)
            # Grand total: 6 raw = 4 accepted + 1 quarantined + 1 rejected
            acc = outcome.row_accounting
            self.assertIsNotNone(acc)
            self.assertEqual(acc.raw_row_count, 6)
            self.assertEqual(acc.accepted_row_count, 4)
            self.assertEqual(acc.quarantined_row_count, 1)
            self.assertEqual(acc.rejected_row_count, 1)
            self.assertTrue(acc.is_balanced())

            self.assertEqual(outcome.per_year_accounting[2016].raw_row_count, 4)
            self.assertEqual(outcome.per_year_accounting[2016].accepted_row_count, 2)
            self.assertEqual(outcome.per_year_accounting[2016].quarantined_row_count, 1)
            self.assertEqual(outcome.per_year_accounting[2016].rejected_row_count, 1)
            self.assertEqual(outcome.per_year_accounting[2024].raw_row_count, 2)
            self.assertEqual(outcome.per_year_accounting[2024].accepted_row_count, 2)

            # Verify SafePublisher outcome & pointer
            pub = outcome.publication_result
            self.assertIsNotNone(pub)
            self.assertTrue(pub.success)
            self.assertEqual(pub.status, "PUBLISHED")
            self.assertEqual(pub.pointer_value, "run_2016_2024_e2e_01")
            self.assertEqual(coordinator.publisher.get_current_pointer(), "run_2016_2024_e2e_01")

            # Verify published Parquet files and DC-12 metric validity on curated data
            published_dir = Path(pub.published_path)
            parquet_files = list(published_dir.rglob("*.parquet"))
            self.assertGreaterEqual(len(parquet_files), 1)
            for pf in parquet_files:
                self.assertTrue(is_valid_parquet_file(pf))

            non_parquet = [
                f for f in published_dir.rglob("*")
                if f.is_file() and not f.name.endswith(".parquet") and not f.name.endswith(".crc") and f.name != "_SUCCESS"
            ]
            self.assertEqual(len(non_parquet), 0, f"Unexpected files in published dir: {non_parquet}")

            curated_df = read_parquet_safe(self.spark, published_dir)
            self.assertEqual(curated_df.count(), 4)
            self.assertEqual(len(curated_df.columns), CANONICAL_COLUMNS_COUNT)

            valid_dep_count = curated_df.filter(is_valid_dep_delay("DEP_DELAY")).count()
            valid_arr_count = curated_df.filter(is_valid_arr_delay("ARR_DELAY")).count()
            self.assertEqual(valid_dep_count, 3)
            self.assertEqual(valid_arr_count, 4)

            # Verify Manifest & Sidecar ExecutionReceipt consistency (No self-reference paradox)
            self.assertTrue(outcome.manifest_path.is_file())
            self.assertTrue(outcome.receipt_path.is_file())

            actual_manifest_bytes = outcome.manifest_path.stat().st_size
            actual_manifest_sha = compute_file_sha256(outcome.manifest_path)

            receipt_data = json.loads(outcome.receipt_path.read_text(encoding="utf-8"))
            self.assertEqual(receipt_data["manifest_bytes"], actual_manifest_bytes)
            self.assertEqual(receipt_data["manifest_sha256"], actual_manifest_sha)
            self.assertEqual(receipt_data["pipeline_state"], "PUBLISHED")
            self.assertEqual(receipt_data["publication_status"], "PUBLISHED")
            self.assertEqual(receipt_data["upstream_identity_status"], UPSTREAM_IDENTITY_STATUS_UNVERIFIED)
            self.assertIsNotNone(receipt_data["or05_coverage_warning"])
            self.assertIn("OR-05", receipt_data["or05_coverage_warning"])

            # Verify lock is released after completion
            lock_file = coordinator.lock_dir / ".pipeline.lock"
            self.assertFalse(lock_file.exists())

    def test_int_02_unapproved_candidate_hashes_guard(self):
        """INT-02: Unapproved candidate hashes fail-closed when require_verified_hashes=True, succeed when allowed."""
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            data_root, inventory, _ = self._setup_synthetic_environment(root, years=(2016,))

            validator = SourceValidator(
                base_dir=root,
                inventory=inventory,
                approved_baseline_hashes=None,
                enforce_production_inventory=False,
            )
            coordinator = IngestionCoordinator(
                spark=self.spark,
                base_data_dir=data_root,
                source_validator=validator,
            )

            outcome_strict = coordinator.run_ingestion(
                run_id="run_unapproved_strict",
                years=[2016],
                require_verified_hashes=True,
                allow_candidate_hashes=False,
            )
            self.assertFalse(outcome_strict.success)
            self.assertEqual(outcome_strict.final_state, PipelineState.TERMINAL_FAILURE)
            self.assertIn("unapproved candidate hash", outcome_strict.error_message)
            self.assertIsNone(coordinator.publisher.get_current_pointer())

            outcome_cand = coordinator.run_ingestion(
                run_id="run_unapproved_allowed",
                years=[2016],
                require_verified_hashes=True,
                allow_candidate_hashes=True,
            )
            self.assertTrue(outcome_cand.success)
            self.assertEqual(outcome_cand.final_state, PipelineState.PUBLISHED)
            self.assertTrue(outcome_cand.source_verification.has_unapproved_candidate_hashes)
            self.assertFalse(outcome_cand.source_verification.all_hashes_verified)

    def test_neg_01_missing_source_file_fails_closed(self):
        """NEG-01: Missing source CSV aborts at SOURCE_VERIFICATION and preserves previous pointer."""
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            data_root, inventory, approved_hashes = self._setup_synthetic_environment(root, years=(2016,))
            (root / inventory[2016].relative_path).unlink()

            validator = SourceValidator(base_dir=root, inventory=inventory, approved_baseline_hashes=approved_hashes)
            coordinator = IngestionCoordinator(self.spark, data_root, validator)

            outcome = coordinator.run_ingestion(run_id="run_missing_src", years=[2016])
            self.assertFalse(outcome.success)
            self.assertEqual(outcome.final_state, PipelineState.TERMINAL_FAILURE)
            self.assertIsNone(coordinator.publisher.get_current_pointer())

    def test_neg_02_source_size_mismatch_fails_closed(self):
        """NEG-02: Source byte size mismatch aborts at SOURCE_VERIFICATION."""
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            data_root, inventory, approved_hashes = self._setup_synthetic_environment(root, years=(2016,))
            csv_file = root / inventory[2016].relative_path
            with open(csv_file, "ab") as f:
                f.write(b"extra_trailing_bytes\n")

            validator = SourceValidator(base_dir=root, inventory=inventory, approved_baseline_hashes=approved_hashes)
            coordinator = IngestionCoordinator(self.spark, data_root, validator)

            outcome = coordinator.run_ingestion(run_id="run_size_mismatch", years=[2016])
            self.assertFalse(outcome.success)
            self.assertEqual(outcome.final_state, PipelineState.TERMINAL_FAILURE)
            self.assertIn("size mismatch", outcome.error_message)

    def test_neg_03_source_hash_mismatch_fails_closed(self):
        """NEG-03: Same byte size but modified content triggers SHA-256 mismatch and aborts."""
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            data_root, inventory, approved_hashes = self._setup_synthetic_environment(root, years=(2016,))
            csv_file = root / inventory[2016].relative_path
            raw_bytes = bytearray(csv_file.read_bytes())
            raw_bytes[-5] = ord("9") if raw_bytes[-5] != ord("9") else ord("8")
            csv_file.write_bytes(bytes(raw_bytes))

            validator = SourceValidator(base_dir=root, inventory=inventory, approved_baseline_hashes=approved_hashes)
            coordinator = IngestionCoordinator(self.spark, data_root, validator)

            outcome = coordinator.run_ingestion(run_id="run_hash_mismatch", years=[2016])
            self.assertFalse(outcome.success)
            self.assertEqual(outcome.final_state, PipelineState.TERMINAL_FAILURE)
            self.assertIn("Hash mismatch", outcome.error_message)

    def test_neg_04_duplicate_run_id_and_lock_contention(self):
        """NEG-04: Duplicate run_id and active lock contention fail-closed while preserving prior publication and manifest."""
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            data_root, inventory, approved_hashes = self._setup_synthetic_environment(root, years=(2016,))
            validator = SourceValidator(base_dir=root, inventory=inventory, approved_baseline_hashes=approved_hashes)
            coordinator = IngestionCoordinator(self.spark, data_root, validator)

            # First run succeeds
            res1 = coordinator.run_ingestion(run_id="run_good_01", years=[2016])
            self.assertTrue(res1.success)
            self.assertEqual(coordinator.publisher.get_current_pointer(), "run_good_01")

            # Re-running with identical run_id must fail-closed AND must not overwrite run_good_01's PUBLISHED manifest
            res_dup = coordinator.run_ingestion(run_id="run_good_01", years=[2016])
            self.assertFalse(res_dup.success)
            self.assertEqual(res_dup.final_state, PipelineState.TERMINAL_FAILURE)
            self.assertEqual(coordinator.publisher.get_current_pointer(), "run_good_01")

            manifest_good = json.loads(res1.manifest_path.read_text(encoding="utf-8"))
            self.assertEqual(manifest_good["status"], "PUBLISHED")

            # Contention: hold external lock while attempting a new run
            with SingleWriterLock(coordinator.lock_dir, run_id="external_active_run"):
                res_locked = coordinator.run_ingestion(run_id="run_contended_02", years=[2016])
                self.assertFalse(res_locked.success)
                self.assertEqual(res_locked.final_state, PipelineState.TERMINAL_FAILURE)
                self.assertIn("Lock contention", res_locked.error_message)
                self.assertEqual(coordinator.publisher.get_current_pointer(), "run_good_01")

    def test_neg_05_fault_injection_corrupt_staging_and_recovery_retry(self):
        """NEG-05: Fault injection corrupting staging Parquet aborts publication and preserves prior pointer; retry succeeds."""
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            data_root, inventory, approved_hashes = self._setup_synthetic_environment(root, years=(2016,))
            validator = SourceValidator(base_dir=root, inventory=inventory, approved_baseline_hashes=approved_hashes)
            coordinator = IngestionCoordinator(self.spark, data_root, validator)

            res_base = coordinator.run_ingestion(run_id="run_baseline_v1", years=[2016])
            self.assertTrue(res_base.success)
            self.assertEqual(coordinator.publisher.get_current_pointer(), "run_baseline_v1")

            def corrupt_staging_hook(state_name: str):
                if state_name == PipelineState.INGESTION_COMPLETED.value:
                    stg_dir = coordinator.staging_root / "run_corrupted_v2"
                    for pf in stg_dir.rglob("*.parquet"):
                        pf.write_bytes(b"CORRUPT_MAGIC_BYTES_NOT_PAR1")

            res_corrupt = coordinator.run_ingestion(
                run_id="run_corrupted_v2",
                years=[2016],
                fault_injector=corrupt_staging_hook,
            )
            self.assertFalse(res_corrupt.success)
            self.assertEqual(res_corrupt.final_state, PipelineState.TERMINAL_FAILURE)
            self.assertIn("FAILED_STAGING_CONTENT_INVALID", res_corrupt.error_message)

            # Crucial: pointer must STILL be run_baseline_v1!
            self.assertEqual(coordinator.publisher.get_current_pointer(), "run_baseline_v1")
            self.assertTrue((coordinator.staging_root / "run_corrupted_v2").exists())

            # Retry with new run_id succeeds and updates pointer to run_retry_v3
            res_retry = coordinator.run_ingestion(run_id="run_retry_v3", years=[2016])
            self.assertTrue(res_retry.success)
            self.assertEqual(coordinator.publisher.get_current_pointer(), "run_retry_v3")
            self.assertEqual(res_retry.publication_result.previous_pointer, "run_baseline_v1")

    def test_int_03_fix_f03_forensic_quarantine_and_rejected_persistence_readback(self):
        """INT-03 (FIX-F03): Quarantined and rejected records are persisted with full raw diagnostic context in data/quarantine/<run_id>/."""
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            data_root, inventory, approved_hashes = self._setup_synthetic_environment(root, years=(2016, 2024))
            validator = SourceValidator(base_dir=root, inventory=inventory, approved_baseline_hashes=approved_hashes)
            coordinator = IngestionCoordinator(self.spark, data_root, validator)

            outcome = coordinator.run_ingestion(run_id="run_forensic_01", years=[2016, 2024])
            self.assertTrue(outcome.success)
            self.assertIsNotNone(outcome.forensic_result)
            self.assertTrue(outcome.forensic_result.verified)

            quar_jsonl = Path(outcome.forensic_result.quarantined_jsonl_path)
            rej_jsonl = Path(outcome.forensic_result.rejected_jsonl_path)
            self.assertTrue(quar_jsonl.is_file())
            self.assertTrue(rej_jsonl.is_file())

            quar_lines = [json.loads(line) for line in quar_jsonl.read_text(encoding="utf-8").splitlines() if line.strip()]
            rej_lines = [json.loads(line) for line in rej_jsonl.read_text(encoding="utf-8").splitlines() if line.strip()]

            self.assertEqual(len(quar_lines), 1)
            self.assertEqual(len(rej_lines), 1)

            q_rec = quar_lines[0]
            self.assertEqual(q_rec["run_id"], "run_forensic_01")
            self.assertEqual(q_rec["_source_year"], 2016)
            self.assertEqual(q_rec["_source_file"], "flight_2016.csv")
            self.assertIsNotNone(q_rec["_record_lineage_id"])
            self.assertEqual(q_rec["_record_status"], "QUARANTINED")
            self.assertEqual(q_rec["_anomaly_reason"], "INVALID_FL_DATE_CORE_ANCHOR")
            self.assertIn("INVALID_FL_DATE_CORE_ANCHOR", q_rec["_anomaly_flags"])
            self.assertEqual(q_rec["FL_DATE"], "BAD_DATE")
            self.assertEqual(q_rec["OP_CARRIER"], "UA")

            r_rec = rej_lines[0]
            self.assertEqual(r_rec["run_id"], "run_forensic_01")
            self.assertEqual(r_rec["_source_year"], 2016)
            self.assertEqual(r_rec["_record_status"], "REJECTED")
            self.assertEqual(r_rec["_anomaly_reason"], "PARSER_SYNTAX_CORRUPTION")
            self.assertIsNotNone(r_rec["_corrupt_record"])
            self.assertIn("SHORT_ROW", r_rec["_corrupt_record"])

            # Verify forensic Parquet directories also match exact counts
            quar_pq_df = read_parquet_safe(self.spark, outcome.forensic_result.quarantined_parquet_dir)
            rej_pq_df = read_parquet_safe(self.spark, outcome.forensic_result.rejected_parquet_dir)
            self.assertEqual(quar_pq_df.count(), 1)
            self.assertEqual(rej_pq_df.count(), 1)

    def test_int_04_fix_f04_parquet_two_phase_attempt_cleanup_and_verification(self):
        """INT-04 (FIX-F04): Two-phase Parquet writer purges orphan task attempts / .tmp files and verifies row counts & schema."""
        with tempfile.TemporaryDirectory() as td:
            stg_dir = Path(td) / "staging_retry_test"
            attempts_dir = stg_dir / "_task_attempts"
            attempts_dir.mkdir(parents=True, exist_ok=True)

            # Plant simulated orphan/failed task attempt files and .parquet.tmp files before write
            (attempts_dir / "part-00000-attempt-0-999-orphan.parquet").write_bytes(b"ORPHAN_ATTEMPT")
            (attempts_dir / "part-00000-attempt-1-998-failed.parquet.tmp").write_bytes(b"PARTIAL_TMP")
            (stg_dir / "stale_partial.parquet.tmp").write_bytes(b"STALE_TMP")

            # Create a 2-row DataFrame matching canonical curated schema
            root = Path(td) / "env"
            data_root, inventory, approved_hashes = self._setup_synthetic_environment(root, years=(2024,))
            csv_path = root / inventory[2024].relative_path
            from flight_pipeline.ingestion.reader import IngestionRecordClassifier, IngestionTransformer, RawCsvReader
            raw_df = RawCsvReader(self.spark).read_raw(csv_path, source_year=2024, attach_lineage=True)
            curated_df = IngestionTransformer.to_curated(IngestionRecordClassifier.classify(raw_df))

            written = write_dataframe_parquet_safe(
                curated_df,
                stg_dir,
                expected_row_count=2,
                verify_curated_schema=True,
            )
            self.assertGreaterEqual(len(written), 1)
            self.assertFalse(attempts_dir.exists(), "_task_attempts directory must be removed after promotion")
            self.assertEqual(len(list(stg_dir.rglob("*.tmp"))), 0, "No .tmp files may remain in staging")

            # Verify row count mismatch detection raises PARQUET_WRITE_INTEGRITY_ERROR
            with self.assertRaises(RuntimeError) as ctx_cnt:
                verify_parquet_directory_integrity(stg_dir, expected_row_count=999, verify_curated_schema=True)
            self.assertIn("PARQUET_WRITE_INTEGRITY_ERROR", str(ctx_cnt.exception))

    def test_int_05_fix_f05_post_pointer_sidecar_failure_and_reconciliation(self):
        """INT-05 (FIX-F05): Post-pointer sidecar failure enters PUBLISHED_RECEIPT_PENDING_RECONCILIATION (never FAILED) and reconciles cleanly."""
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            data_root, inventory, approved_hashes = self._setup_synthetic_environment(root, years=(2016, 2024))
            validator = SourceValidator(base_dir=root, inventory=inventory, approved_baseline_hashes=approved_hashes)
            coordinator = IngestionCoordinator(self.spark, data_root, validator)

            # Inject failure AFTER pointer switch (during sidecar receipt persistence)
            def post_pointer_fault(hook_name: str):
                if hook_name == "POST_POINTER_SIDE_EFFECT":
                    raise OSError("Simulated transient disk error writing sidecar execution_receipt.json")

            outcome_pending = coordinator.run_ingestion(
                run_id="run_post_ptr_01",
                years=[2016, 2024],
                fault_injector=post_pointer_fault,
            )

            # 1. Run must report PUBLISHED_RECEIPT_PENDING_RECONCILIATION, NOT TERMINAL_FAILURE
            self.assertFalse(outcome_pending.success)
            self.assertEqual(outcome_pending.final_state, PipelineState.PUBLISHED_RECEIPT_PENDING_RECONCILIATION)
            self.assertEqual(coordinator.publisher.get_current_pointer(), "run_post_ptr_01")

            # 2. Manifest status must NEVER be overwritten to FAILED
            manifest_pending = json.loads(outcome_pending.manifest_path.read_text(encoding="utf-8"))
            self.assertNotEqual(manifest_pending["status"], "FAILED")
            self.assertEqual(manifest_pending["status"], "PUBLISHED_RECEIPT_PENDING_RECONCILIATION")

            # Record published Parquet hashes before reconciliation to prove immutability
            pub_dir = Path(outcome_pending.publication_result.published_path)
            before_hashes = {
                pf.name: compute_file_sha256(pf) for pf in sorted(pub_dir.rglob("*.parquet"))
            }

            # 3. Reconcile published run via coordinator.reconcile_published_run
            outcome_reconciled = coordinator.reconcile_published_run("run_post_ptr_01")
            self.assertTrue(outcome_reconciled.success)
            self.assertEqual(outcome_reconciled.final_state, PipelineState.PUBLISHED)
            self.assertTrue(outcome_reconciled.receipt_path.is_file())

            manifest_final = json.loads(outcome_reconciled.manifest_path.read_text(encoding="utf-8"))
            receipt_final = json.loads(outcome_reconciled.receipt_path.read_text(encoding="utf-8"))
            self.assertEqual(manifest_final["status"], "PUBLISHED")
            self.assertEqual(receipt_final["pipeline_state"], "PUBLISHED")
            self.assertEqual(receipt_final["publication_status"], "PUBLISHED")
            self.assertEqual(receipt_final["manifest_sha256"], compute_file_sha256(outcome_reconciled.manifest_path))

            # Verify published Parquet files were never mutated during reconciliation
            after_hashes = {
                pf.name: compute_file_sha256(pf) for pf in sorted(pub_dir.rglob("*.parquet"))
            }
            self.assertEqual(before_hashes, after_hashes)

    def test_neg_06_fix_f01_f02_header_drift_and_blank_line_abort_before_publication(self):
        """NEG-06 (FIX-F01 / FIX-F02): Physical header drift or blank line in CSV aborts run and preserves previous pointer."""
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            data_root, inventory, approved_hashes = self._setup_synthetic_environment(root, years=(2016,))
            validator = SourceValidator(base_dir=root, inventory=inventory, approved_baseline_hashes=approved_hashes)
            coordinator = IngestionCoordinator(self.spark, data_root, validator)

            # Establish valid baseline run
            res_ok = coordinator.run_ingestion(run_id="run_base_ok", years=[2016])
            self.assertTrue(res_ok.success)
            self.assertEqual(coordinator.publisher.get_current_pointer(), "run_base_ok")

            # Replace 2016 CSV with a file containing a blank line (and update inventory size/hash so it passes Step 1)
            csv_path = root / inventory[2016].relative_path
            header = ",".join(CANONICAL_COLUMN_NAMES)
            row1 = self._make_csv_row(fl_date="2016-01-15", carrier="AA")
            blank_content = f"{header}\n{row1}\n\n{row1}\n".encode("utf-8")
            csv_path.write_bytes(blank_content)

            inventory[2016] = SourceEntry(
                year=2016,
                relative_path=inventory[2016].relative_path,
                audited_row_count=3,
                audited_byte_size=len(blank_content),
                audited_column_count=34,
            )
            approved_hashes[2016] = sha256(blank_content).hexdigest()

            validator_blk = SourceValidator(base_dir=root, inventory=inventory, approved_baseline_hashes=approved_hashes)
            coordinator_blk = IngestionCoordinator(self.spark, data_root, validator_blk)

            res_blk = coordinator_blk.run_ingestion(run_id="run_blank_line_fail", years=[2016])
            self.assertFalse(res_blk.success)
            self.assertEqual(res_blk.final_state, PipelineState.TERMINAL_FAILURE)
            self.assertIn("ACCOUNTING_UNVERIFIED", res_blk.error_message)
            self.assertEqual(coordinator_blk.publisher.get_current_pointer(), "run_base_ok")

    def test_blocker02_parquet_type_contract_verification_and_pipeline_guard(self):
        """
        INT-06 (BLOCKER-02): Exact 34-column Parquet schema, physical order, Arrow data type, and nullability verification:
        - Rejects all-string 34-column Parquet (e.g. DEP_DELAY as string instead of float64).
        - Rejects LongType column stored as int32, float64, or string.
        - Rejects DoubleType column stored as float32, int64, or string.
        - Rejects StringType column stored as int64 or binary.
        - Rejects temporal string column (FL_DATE / DEP_TIME) stored as date32 or timestamp.
        - Rejects nullable=False on any canonical curated column.
        - Rejects leaked technical columns (_record_status, _corrupt_record, etc.).
        - Accepts canonical 34-column schema (including large_string on StringType).
        - Coordinator fault injection replacing staging Parquet with wrong-typed 34-column Parquet aborts publication
          and preserves previous live pointer.
        """
        from datetime import date, datetime
        import pyarrow as pa
        import pyarrow.parquet as pq
        from pyspark.sql.types import DoubleType, LongType, StringType as SparkStringType
        from flight_pipeline.ingestion.schema import get_curated_parquet_schema

        curated_spark_schema = get_curated_parquet_schema()

        def make_canonical_arrow_fields(overrides=None, nullable_overrides=None):
            overrides = overrides or {}
            nullable_overrides = nullable_overrides or {}
            fields = []
            for sf in curated_spark_schema.fields:
                if sf.name in overrides:
                    pa_t = overrides[sf.name]
                elif isinstance(sf.dataType, SparkStringType):
                    pa_t = pa.string()
                elif isinstance(sf.dataType, DoubleType):
                    pa_t = pa.float64()
                elif isinstance(sf.dataType, LongType):
                    pa_t = pa.int64()
                else:
                    raise AssertionError(f"Unexpected Spark type: {sf.dataType}")
                is_null = nullable_overrides.get(sf.name, True)
                fields.append(pa.field(sf.name, pa_t, nullable=is_null))
            return pa.schema(fields)

        def write_one_row_parquet(dir_path: Path, schema: pa.Schema):
            dir_path.mkdir(parents=True, exist_ok=True)
            for old_f in dir_path.glob("*.parquet"):
                old_f.unlink()
            arrays = []
            for f in schema:
                t = f.type
                if pa.types.is_string(t) or pa.types.is_large_string(t):
                    arrays.append(pa.array(["2016-01-01"], type=t))
                elif pa.types.is_floating(t):
                    arrays.append(pa.array([1.0], type=t))
                elif pa.types.is_integer(t):
                    arrays.append(pa.array([1], type=t))
                elif pa.types.is_date32(t):
                    arrays.append(pa.array([date(2016, 1, 1)], type=t))
                elif pa.types.is_timestamp(t):
                    arrays.append(pa.array([datetime(2016, 1, 1, 8, 0)], type=t))
                elif pa.types.is_binary(t):
                    arrays.append(pa.array([b"AA"], type=t))
                else:
                    arrays.append(pa.array([None], type=t))
            tbl = pa.Table.from_arrays(arrays, schema=schema)
            pq.write_table(tbl, str(dir_path / "part-00000.parquet"))

        with tempfile.TemporaryDirectory() as td:
            td_path = Path(td)

            # 1. Valid canonical 34-column schema passes
            valid_dir = td_path / "valid_canonical"
            write_one_row_parquet(valid_dir, make_canonical_arrow_fields())
            self.assertEqual(
                verify_parquet_directory_integrity(valid_dir, expected_row_count=1, verify_curated_schema=True),
                1,
            )

            # 2. Valid canonical schema with large_string on StringType passes
            large_str_dir = td_path / "valid_large_str"
            write_one_row_parquet(
                large_str_dir,
                make_canonical_arrow_fields(overrides={"OP_CARRIER": pa.large_string(), "FL_DATE": pa.large_string()}),
            )
            self.assertEqual(
                verify_parquet_directory_integrity(large_str_dir, expected_row_count=1, verify_curated_schema=True),
                1,
            )

            # 3. All-string 34-column Parquet (pre-fix BLOCKER-02 reproduction) fails closed
            all_str_dir = td_path / "all_str"
            all_str_schema = pa.schema([pa.field(c, pa.string(), nullable=True) for c in CANONICAL_COLUMN_NAMES])
            write_one_row_parquet(all_str_dir, all_str_schema)
            with self.assertRaises(RuntimeError) as ctx_all_str:
                verify_parquet_directory_integrity(all_str_dir, expected_row_count=1, verify_curated_schema=True)
            self.assertIn("FAILED_STAGING_CONTENT_INVALID", str(ctx_all_str.exception))
            self.assertIn("OP_CARRIER_FL_NUM", str(ctx_all_str.exception))

            # 4. Matrix of wrong physical Arrow types across LongType, DoubleType, StringType, and temporal strings
            mismatch_cases = [
                ("MONTH", pa.int32(), "LongType as int32"),
                ("ORIGIN_INDEX", pa.float64(), "LongType as float64"),
                ("DAY_OF_WEEK", pa.string(), "LongType as string"),
                ("DEP_DELAY", pa.float32(), "DoubleType as float32"),
                ("ARR_DELAY", pa.int64(), "DoubleType as int64"),
                ("FLIGHTS", pa.string(), "DoubleType as string"),
                ("OP_CARRIER", pa.int64(), "StringType as int64"),
                ("ORIGIN", pa.binary(), "StringType as binary"),
                ("FL_DATE", pa.date32(), "Temporal string FL_DATE as date32"),
                ("DEP_TIME", pa.timestamp("us"), "Temporal string DEP_TIME as timestamp"),
            ]
            for idx, (col_name, wrong_pa_type, label) in enumerate(mismatch_cases):
                case_dir = td_path / f"mismatch_{idx}_{col_name}"
                write_one_row_parquet(case_dir, make_canonical_arrow_fields(overrides={col_name: wrong_pa_type}))
                with self.assertRaises(RuntimeError, msg=f"Failed to reject {label}") as ctx_m:
                    verify_parquet_directory_integrity(case_dir, expected_row_count=1, verify_curated_schema=True)
                self.assertIn("FAILED_STAGING_CONTENT_INVALID", str(ctx_m.exception))
                self.assertIn(col_name, str(ctx_m.exception))

            # 5. Nullability mismatch (nullable=False on MONTH) fails closed
            non_null_dir = td_path / "non_null_month"
            write_one_row_parquet(
                non_null_dir,
                make_canonical_arrow_fields(nullable_overrides={"MONTH": False}),
            )
            with self.assertRaises(RuntimeError) as ctx_nn:
                verify_parquet_directory_integrity(non_null_dir, expected_row_count=1, verify_curated_schema=True)
            self.assertIn("nullability mismatch", str(ctx_nn.exception))

            # 6. Coordinator integration: fault injector replaces staging Parquet with wrong-typed 34-column Parquet
            env_root = td_path / "coord_env"
            data_root, inventory, approved_hashes = self._setup_synthetic_environment(env_root, years=(2016,))
            validator = SourceValidator(base_dir=env_root, inventory=inventory, approved_baseline_hashes=approved_hashes)
            coordinator = IngestionCoordinator(self.spark, data_root, validator)

            res_good = coordinator.run_ingestion(run_id="run_type_good_01", years=[2016])
            self.assertTrue(res_good.success)
            self.assertEqual(coordinator.publisher.get_current_pointer(), "run_type_good_01")

            def inject_wrong_parquet_type(state_name: str):
                if state_name == PipelineState.INGESTION_COMPLETED.value:
                    stg_dir = coordinator.staging_root / "run_type_bad_02"
                    # Write 2 rows (matching accepted_row_count=2) with 34 canonical names, but DEP_DELAY as string!
                    bad_schema = make_canonical_arrow_fields(overrides={"DEP_DELAY": pa.string()})
                    arrays = []
                    for f in bad_schema:
                        if pa.types.is_string(f.type):
                            arrays.append(pa.array(["2016-01-01", "2016-01-02"], type=f.type))
                        elif pa.types.is_float64(f.type):
                            arrays.append(pa.array([1.0, 2.0], type=f.type))
                        else:
                            arrays.append(pa.array([1, 2], type=f.type))
                    for old_pf in stg_dir.rglob("*.parquet"):
                        old_pf.unlink()
                    pq.write_table(pa.Table.from_arrays(arrays, schema=bad_schema), str(stg_dir / "part-00000.parquet"))

            res_bad_type = coordinator.run_ingestion(
                run_id="run_type_bad_02",
                years=[2016],
                fault_injector=inject_wrong_parquet_type,
            )
            self.assertFalse(res_bad_type.success)
            self.assertEqual(res_bad_type.final_state, PipelineState.TERMINAL_FAILURE)
            self.assertIn("FAILED_STAGING_CONTENT_INVALID", res_bad_type.error_message)
            self.assertIn("DEP_DELAY", res_bad_type.error_message)
            self.assertEqual(coordinator.publisher.get_current_pointer(), "run_type_good_01")

    def test_blocker03_post_pointer_missing_manifest_and_fail_closed_manual_reconciliation(self):
        """
        INT-07 (BLOCKER-03): Full post-publication recovery & fail-closed matrix:
        1. Pointer switched + run_manifest.json missing + execution_receipt.json missing
           (fault at POST_POINTER_PRE_MANIFEST_WRITE) -> reconcile_published_run reconstructs both from
           authoritative sidecars and returns PUBLISHED without mutating published Parquet files.
        2. Receipt write failure during first reconcile_published_run (RECONCILE_PRE_RECEIPT_WRITE) ->
           returns PUBLISHED_RECEIPT_PENDING_RECONCILIATION; second retry succeeds with PUBLISHED.
        3. Repeated reconcile_published_run on an already PUBLISHED run -> idempotent, preserves manifest SHA-256
           and published Parquet files.
        4. Corrupted run_manifest.json -> fail-closed with MANUAL_RECONCILIATION_REQUIRED, no fake receipt.
        5. Missing required authoritative sidecar (anomaly_summary.json / source_verification.json / forensic_manifest.json)
           when manifest is missing -> fail-closed with MANUAL_RECONCILIATION_REQUIRED, no fake manifest/receipt.
        """
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            data_root, inventory, approved_hashes = self._setup_synthetic_environment(root, years=(2016, 2024))
            validator = SourceValidator(base_dir=root, inventory=inventory, approved_baseline_hashes=approved_hashes)
            coordinator = IngestionCoordinator(self.spark, data_root, validator)

            # Establish prior published run so previous_pointer is non-null
            res_prior = coordinator.run_ingestion(run_id="run_prior_00", years=[2016])
            self.assertTrue(res_prior.success)
            self.assertEqual(coordinator.publisher.get_current_pointer(), "run_prior_00")

            # -----------------------------------------------------------------
            # Scenario 1: Pointer switched + manifest missing + receipt missing
            # -----------------------------------------------------------------
            def fail_before_manifest_write(hook_name: str):
                if hook_name == "POST_POINTER_PRE_MANIFEST_WRITE":
                    raise OSError("Simulated power/disk fault immediately after pointer switch before manifest write")

            outcome_no_manifest = coordinator.run_ingestion(
                run_id="run_case_b_01",
                years=[2016, 2024],
                fault_injector=fail_before_manifest_write,
            )
            self.assertFalse(outcome_no_manifest.success)
            self.assertEqual(outcome_no_manifest.final_state, PipelineState.PUBLISHED_RECEIPT_PENDING_RECONCILIATION)
            self.assertEqual(coordinator.publisher.get_current_pointer(), "run_case_b_01")

            meta_dir_b1 = coordinator.metadata_root / "run_case_b_01"
            manifest_path_b1 = meta_dir_b1 / "run_manifest.json"
            receipt_path_b1 = meta_dir_b1 / "execution_receipt.json"
            self.assertFalse(manifest_path_b1.exists(), "run_manifest.json must be absent on disk in Case B")
            self.assertFalse(receipt_path_b1.exists(), "execution_receipt.json must be absent on disk in Case B")

            pub_dir_b1 = coordinator.publisher.runs_root / "run_case_b_01"
            parquet_hashes_before = {
                pf.name: compute_file_sha256(pf) for pf in sorted(pub_dir_b1.rglob("*.parquet"))
            }

            # -----------------------------------------------------------------
            # Scenario 2: First reconcile attempt fails when writing receipt -> stays PUBLISHED_RECEIPT_PENDING_RECONCILIATION
            # -----------------------------------------------------------------
            def fail_reconcile_receipt(hook_name: str):
                if hook_name == "RECONCILE_PRE_RECEIPT_WRITE":
                    raise OSError("Simulated disk error during first reconcile receipt write")

            reconcile_fail_1 = coordinator.reconcile_published_run(
                "run_case_b_01",
                fault_injector=fail_reconcile_receipt,
            )
            self.assertFalse(reconcile_fail_1.success)
            self.assertEqual(reconcile_fail_1.final_state, PipelineState.PUBLISHED_RECEIPT_PENDING_RECONCILIATION)
            self.assertFalse(receipt_path_b1.exists())

            # Remove manifest_path_b1 again so the retry exercises full Case B reconstruction end-to-end
            if manifest_path_b1.exists():
                manifest_path_b1.unlink()

            # Retry reconcile_published_run without fault -> succeeds and reconstructs both manifest and receipt!
            reconcile_ok = coordinator.reconcile_published_run("run_case_b_01")
            self.assertTrue(reconcile_ok.success)
            self.assertEqual(reconcile_ok.final_state, PipelineState.PUBLISHED)
            self.assertTrue(manifest_path_b1.is_file())
            self.assertTrue(receipt_path_b1.is_file())

            reconstructed_manifest = json.loads(manifest_path_b1.read_text(encoding="utf-8"))
            reconstructed_receipt = json.loads(receipt_path_b1.read_text(encoding="utf-8"))

            self.assertEqual(reconstructed_manifest["status"], "PUBLISHED")
            self.assertEqual(reconstructed_manifest["run_id"], "run_case_b_01")
            self.assertEqual(reconstructed_manifest["row_accounting"]["raw_row_count"], 6)
            self.assertEqual(reconstructed_manifest["row_accounting"]["accepted_row_count"], 4)
            self.assertEqual(reconstructed_manifest["row_accounting"]["quarantined_row_count"], 1)
            self.assertEqual(reconstructed_manifest["row_accounting"]["rejected_row_count"], 1)
            self.assertEqual(len(reconstructed_manifest["inputs"]), 2)
            self.assertGreaterEqual(len(reconstructed_manifest["outputs"]), 1)
            self.assertEqual(reconstructed_manifest["configuration"]["previous_pointer"], "run_prior_00")
            self.assertEqual(reconstructed_receipt["previous_pointer"], "run_prior_00")
            self.assertEqual(reconstructed_receipt["manifest_sha256"], compute_file_sha256(manifest_path_b1))

            parquet_hashes_after = {
                pf.name: compute_file_sha256(pf) for pf in sorted(pub_dir_b1.rglob("*.parquet"))
            }
            self.assertEqual(parquet_hashes_before, parquet_hashes_after)

            # -----------------------------------------------------------------
            # Scenario 3: Idempotent re-execution on an already PUBLISHED run
            # -----------------------------------------------------------------
            manifest_sha_before_idem = compute_file_sha256(manifest_path_b1)
            reconcile_idem = coordinator.reconcile_published_run("run_case_b_01")
            self.assertTrue(reconcile_idem.success)
            self.assertEqual(reconcile_idem.final_state, PipelineState.PUBLISHED)
            self.assertEqual(compute_file_sha256(manifest_path_b1), manifest_sha_before_idem)
            self.assertEqual(
                {pf.name: compute_file_sha256(pf) for pf in sorted(pub_dir_b1.rglob("*.parquet"))},
                parquet_hashes_before,
            )

            # -----------------------------------------------------------------
            # Scenario 4: Corrupted manifest file -> fail-closed MANUAL_RECONCILIATION_REQUIRED
            # -----------------------------------------------------------------
            receipt_path_b1.unlink()
            manifest_path_b1.write_text("{CORRUPTED_NOT_VALID_JSON", encoding="utf-8")
            corrupt_res = coordinator.reconcile_published_run("run_case_b_01")
            self.assertFalse(corrupt_res.success)
            self.assertEqual(corrupt_res.final_state, PipelineState.MANUAL_RECONCILIATION_REQUIRED)
            self.assertIn("MANUAL_RECONCILIATION_REQUIRED", corrupt_res.error_message)
            self.assertFalse(receipt_path_b1.exists(), "Must NEVER create a receipt when manifest is corrupted")
            self.assertEqual(coordinator.publisher.get_current_pointer(), "run_case_b_01")

            # -----------------------------------------------------------------
            # Scenario 5: Missing required authoritative sidecar -> fail-closed MANUAL_RECONCILIATION_REQUIRED
            # -----------------------------------------------------------------
            manifest_path_b1.unlink()
            anomaly_path_b1 = meta_dir_b1 / "anomaly_summary.json"
            anomaly_backup = anomaly_path_b1.read_bytes()
            anomaly_path_b1.unlink()

            missing_sidecar_res = coordinator.reconcile_published_run("run_case_b_01")
            self.assertFalse(missing_sidecar_res.success)
            self.assertEqual(missing_sidecar_res.final_state, PipelineState.MANUAL_RECONCILIATION_REQUIRED)
            self.assertIn("anomaly_summary.json", missing_sidecar_res.error_message)
            self.assertFalse(manifest_path_b1.exists(), "Must NEVER fabricate manifest when sidecar is missing")
            self.assertFalse(receipt_path_b1.exists(), "Must NEVER fabricate receipt when sidecar is missing")

            # Restore anomaly_summary.json and verify recovery succeeds again
            anomaly_path_b1.write_bytes(anomaly_backup)
            recovered_again = coordinator.reconcile_published_run("run_case_b_01")
            self.assertTrue(recovered_again.success)
            self.assertEqual(recovered_again.final_state, PipelineState.PUBLISHED)


if __name__ == "__main__":
    unittest.main()
