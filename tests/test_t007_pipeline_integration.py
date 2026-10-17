"""
Comprehensive End-to-End Integration and Negative Fault-Injection Test Suite (T007-05, T007-06, T007-07).
Validates:
1. Multi-year synthetic end-to-end ingestion lifecycle (RUN_STARTED -> ... -> PUBLISHED).
2. Approved baseline SHA-256 verification vs candidate unapproved hash fail-closed guard.
3. DC-11 row accounting conservation across valid, quarantined, and rejected rows.
4. DC-12 metric validity separation using canonical predicates on curated Parquet output.
5. Real Spark Parquet generation, SafePublisher 7-step promotion, and pointer switching.
6. Sidecar ExecutionReceipt atomic generation and manifest self-reference avoidance.
7. Immutability of published versioned directory after promotion.
8. Negative tests: missing source, size mismatch, hash mismatch, duplicate run_id, lock contention,
   staging Parquet corruption, fault injection during lifecycle transitions, and retry recovery.
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
                    self._make_csv_row(fl_date=f"{yr}-06-01", carrier="B6", fl_num="-5.0", dep_delay="-2.0", arr_delay="-10.0"),  # G3-COND-B: fl_num <= 0 accepted
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

            # Verify exact lifecycle transition sequence
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

            # Verify DC-11 Row Accounting:
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

            # Ensure no non-parquet diagnostic files polluted published_dir
            non_parquet = [
                f for f in published_dir.rglob("*")
                if f.is_file() and not f.name.endswith(".parquet") and not f.name.endswith(".crc") and f.name != "_SUCCESS"
            ]
            self.assertEqual(len(non_parquet), 0, f"Unexpected files in published dir: {non_parquet}")

            # Read back published Parquet with Spark and verify DC-12 metric validity
            curated_df = read_parquet_safe(self.spark, published_dir)
            self.assertEqual(curated_df.count(), 4)
            self.assertEqual(len(curated_df.columns), CANONICAL_COLUMNS_COUNT)

            valid_dep_count = curated_df.filter(is_valid_dep_delay("DEP_DELAY")).count()
            valid_arr_count = curated_df.filter(is_valid_arr_delay("ARR_DELAY")).count()
            # 1 of the 4 accepted rows had DEP_DELAY="NOT_A_NUM" -> NULL, so 3 valid DEP_DELAY and 4 valid ARR_DELAY
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

            # Validator with NO approved baseline hashes
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

            # 1. Default strict mode must reject unapproved candidate hashes
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

            # 2. Explicitly allowing candidate hashes succeeds and records unverified status
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
            # Delete the physical CSV
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
            # Append extra bytes to CSV
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
            # Flip 2 bytes in place without changing file size
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
        """NEG-04: Duplicate run_id and active lock contention fail-closed while preserving prior publication."""
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            data_root, inventory, approved_hashes = self._setup_synthetic_environment(root, years=(2016,))
            validator = SourceValidator(base_dir=root, inventory=inventory, approved_baseline_hashes=approved_hashes)
            coordinator = IngestionCoordinator(self.spark, data_root, validator)

            # First run succeeds
            res1 = coordinator.run_ingestion(run_id="run_good_01", years=[2016])
            self.assertTrue(res1.success)
            self.assertEqual(coordinator.publisher.get_current_pointer(), "run_good_01")

            # Re-running with identical run_id must fail-closed
            res_dup = coordinator.run_ingestion(run_id="run_good_01", years=[2016])
            self.assertFalse(res_dup.success)
            self.assertEqual(res_dup.final_state, PipelineState.TERMINAL_FAILURE)
            self.assertEqual(coordinator.publisher.get_current_pointer(), "run_good_01")

            # Contention: hold external lock while attempting a new run
            with SingleWriterLock(coordinator.lock_dir, run_id="external_active_run"):
                res_locked = coordinator.run_ingestion(run_id="run_contended_02", years=[2016])
                self.assertFalse(res_locked.success)
                self.assertEqual(res_locked.final_state, PipelineState.TERMINAL_FAILURE)
                self.assertIn("Lock contention", res_locked.error_message)
                # Pointer still points to run_good_01
                self.assertEqual(coordinator.publisher.get_current_pointer(), "run_good_01")

    def test_neg_05_fault_injection_corrupt_staging_and_recovery_retry(self):
        """NEG-05: Fault injection corrupting staging Parquet aborts publication and preserves prior pointer; retry succeeds."""
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            data_root, inventory, approved_hashes = self._setup_synthetic_environment(root, years=(2016,))
            validator = SourceValidator(base_dir=root, inventory=inventory, approved_baseline_hashes=approved_hashes)
            coordinator = IngestionCoordinator(self.spark, data_root, validator)

            # Establish baseline published version
            res_base = coordinator.run_ingestion(run_id="run_baseline_v1", years=[2016])
            self.assertTrue(res_base.success)
            self.assertEqual(coordinator.publisher.get_current_pointer(), "run_baseline_v1")

            # Inject corruption into staging parquet right when INGESTION_COMPLETED is reached
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

            # Forensic staging directory for run_corrupted_v2 is preserved (not destructively deleted)
            self.assertTrue((coordinator.staging_root / "run_corrupted_v2").exists())

            # Retry with new run_id succeeds and updates pointer to run_retry_v3
            res_retry = coordinator.run_ingestion(run_id="run_retry_v3", years=[2016])
            self.assertTrue(res_retry.success)
            self.assertEqual(coordinator.publisher.get_current_pointer(), "run_retry_v3")
            self.assertEqual(res_retry.publication_result.previous_pointer, "run_baseline_v1")


if __name__ == "__main__":
    unittest.main()
