"""
Focused regression tests for T-013 publication order and staging safety.
Verifies the 6 mandatory scenarios from T-013 Master Prompt Section 4:
1. Validation PASS allows controlled publication.
2. Validation FAIL does not change latest pointer.
3. Failure preserves prior published run.
4. Duplicate run ID is rejected.
5. Manifest and receipt remain consistent.
6. Publication failure is not misreported as PASS.

Uses synthetic isolated directories only. Never touches real production directories.
"""

import hashlib
import json
from pathlib import Path
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

import pyarrow as pa
import pyarrow.parquet as pq

from flight_pipeline.kpi.catalog import KPI_OUTPUT_COLUMNS
from flight_pipeline.kpi.runner import KpiProductionRunner, compute_file_sha256


def make_synthetic_kpi_parquet(output_path: Path, is_valid: bool = True) -> None:
    """Helper to generate a synthetic single-row KPI Parquet file."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    schema = pa.schema([
        ("kpi_id", pa.string()),
        ("submetric", pa.string()),
        ("run_id", pa.string()),
        ("kpi_version", pa.string()),
        ("source_year", pa.string()),
        ("group_dimensions", pa.string()),
        ("filter_definition", pa.string()),
        ("count_records", pa.int64()),
        ("count_metric_valid", pa.int64()),
        ("excluded_count", pa.int64()),
        ("metric_valid_rate", pa.float64()),
        ("source_coverage_status", pa.string()),
        ("value", pa.float64()),
        ("unit_status", pa.string()),
        ("min_n_status", pa.string()),
        ("quality_version", pa.string()),
        ("provenance_reference", pa.string()),
    ])

    if is_valid:
        data = {
            "kpi_id": ["KPI-01"],
            "submetric": [None],
            "run_id": ["synthetic_run"],
            "kpi_version": ["1.0.0"],
            "source_year": ["2016"],
            "group_dimensions": ["cohort=all;source_year=2016"],
            "filter_definition": ["accepted_flights"],
            "count_records": [100],
            "count_metric_valid": [100],
            "excluded_count": [0],
            "metric_valid_rate": [1.0],
            "source_coverage_status": ["VERIFIED_WITH_SCOPE"],
            "value": [100.0],
            "unit_status": ["COUNT_RECORDS"],
            "min_n_status": ["NOT_APPLICABLE"],
            "quality_version": ["docs-v1.1"],
            "provenance_reference": ["synthetic"],
        }
    else:
        # Invalid: DC-12 denominator conservation violated (rec=100 != val=50 + exc=0)
        data = {
            "kpi_id": ["KPI-01"],
            "submetric": [None],
            "run_id": ["synthetic_run"],
            "kpi_version": ["1.0.0"],
            "source_year": ["2016"],
            "group_dimensions": ["cohort=all;source_year=2016"],
            "filter_definition": ["accepted_flights"],
            "count_records": [100],
            "count_metric_valid": [50],
            "excluded_count": [0],
            "metric_valid_rate": [0.5],
            "source_coverage_status": ["VERIFIED_WITH_SCOPE"],
            "value": [50.0],
            "unit_status": ["COUNT_RECORDS"],
            "min_n_status": ["NOT_APPLICABLE"],
            "quality_version": ["docs-v1.1"],
            "provenance_reference": ["synthetic_invalid"],
        }

    table = pa.Table.from_pydict(data, schema=schema)
    pq.write_table(table, str(output_path))


class TestT013PublicationOrder(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_root = Path(self.temp_dir.name)
        self.external_audit = self.test_root / "external_audit"
        self.active_runner = None

    def tearDown(self):
        if self.active_runner is not None:
            self.active_runner.close()
        import logging
        logger = logging.getLogger("T013KpiRunner")
        for h in list(logger.handlers):
            h.close()
            logger.removeHandler(h)
        self.temp_dir.cleanup()

    def test_01_validation_pass_allows_controlled_publication(self):
        """Scenario 1: Validation PASS allows atomic promotion and pointer update."""
        runner = KpiProductionRunner(
            run_id="test_run_pass_v1",
            repo_root=self.test_root,
            external_audit_dir=self.external_audit,
        )
        self.active_runner = runner
        staged_file = runner.staging_run_dir / "data" / "year_2016" / "part-0.parquet"
        make_synthetic_kpi_parquet(staged_file, is_valid=True)

        exec_metrics = {"total_output_rows": 1, "years_processed": {}}
        res = runner.publish_and_validate(exec_metrics)

        self.assertIsNotNone(res)
        self.assertTrue(runner.published_run_dir.exists())
        self.assertFalse(runner.staging_run_dir.exists())
        self.assertTrue(runner.latest_pointer_path.exists())
        self.assertEqual(runner.latest_pointer_path.read_text(encoding="utf-8").strip(), "test_run_pass_v1")

    def test_02_validation_fail_does_not_change_latest_pointer(self):
        """Scenario 2: Validation FAIL keeps prior latest pointer unchanged."""
        runner = KpiProductionRunner(
            run_id="test_run_fail_v1",
            repo_root=self.test_root,
            external_audit_dir=self.external_audit,
        )
        self.active_runner = runner
        # Establish prior pointer
        runner.latest_pointer_path.parent.mkdir(parents=True, exist_ok=True)
        runner.latest_pointer_path.write_text("prior_run_v0\n", encoding="utf-8")

        # Create invalid staged data (violates DC-12)
        staged_file = runner.staging_run_dir / "data" / "year_2016" / "part-0.parquet"
        make_synthetic_kpi_parquet(staged_file, is_valid=False)

        exec_metrics = {"total_output_rows": 1, "years_processed": {}}
        with self.assertRaises(AssertionError):
            runner.publish_and_validate(exec_metrics)

        # Pointer must remain prior_run_v0
        self.assertEqual(runner.latest_pointer_path.read_text(encoding="utf-8").strip(), "prior_run_v0")
        # Staging must NOT have been moved to published
        self.assertFalse(runner.published_run_dir.exists())
        self.assertTrue(runner.staging_run_dir.exists())

    def test_03_failure_preserves_prior_published_run(self):
        """Scenario 3: Validation failure preserves prior published run intact."""
        prior_dir = self.test_root / "data" / "kpi" / "runs" / "prior_run_v0"
        prior_file = prior_dir / "data" / "year_2016" / "part-0.parquet"
        make_synthetic_kpi_parquet(prior_file, is_valid=True)
        prior_sha = compute_file_sha256(prior_file)

        runner = KpiProductionRunner(
            run_id="new_run_fail_v2",
            repo_root=self.test_root,
            external_audit_dir=self.external_audit,
        )
        self.active_runner = runner
        staged_file = runner.staging_run_dir / "data" / "year_2016" / "part-0.parquet"
        make_synthetic_kpi_parquet(staged_file, is_valid=False)

        exec_metrics = {"total_output_rows": 1, "years_processed": {}}
        with self.assertRaises(AssertionError):
            runner.publish_and_validate(exec_metrics)

        # Verify prior published run is completely preserved bitwise
        self.assertTrue(prior_file.exists())
        self.assertEqual(compute_file_sha256(prior_file), prior_sha)

    def test_04_duplicate_run_id_is_rejected(self):
        """Scenario 4: Duplicate published run ID is rejected fail-closed without overwrite."""
        runner = KpiProductionRunner(
            run_id="dup_run_v1",
            repo_root=self.test_root,
            external_audit_dir=self.external_audit,
        )
        self.active_runner = runner
        # Create existing published directory
        runner.published_run_dir.mkdir(parents=True, exist_ok=True)
        staged_file = runner.staging_run_dir / "data" / "year_2016" / "part-0.parquet"
        make_synthetic_kpi_parquet(staged_file, is_valid=True)

        exec_metrics = {"total_output_rows": 1, "years_processed": {}}
        with self.assertRaises(RuntimeError) as ctx:
            runner.publish_and_validate(exec_metrics)

        self.assertIn("already exists", str(ctx.exception))

    def test_05_manifest_and_receipt_remain_consistent(self):
        """Scenario 5: Manifest and receipt remain internally and cryptographically consistent."""
        runner = KpiProductionRunner(
            run_id="test_run_manifest_v1",
            repo_root=self.test_root,
            external_audit_dir=self.external_audit,
        )
        self.active_runner = runner
        staged_file = runner.staging_run_dir / "data" / "year_2016" / "part-0.parquet"
        make_synthetic_kpi_parquet(staged_file, is_valid=True)

        exec_metrics = {"total_output_rows": 1, "years_processed": {}}
        runner.publish_and_validate(exec_metrics)

        manifest_path = runner.metadata_run_dir / "run_manifest.json"
        receipt_path = runner.metadata_run_dir / "execution_receipt.json"

        self.assertTrue(manifest_path.exists())
        self.assertTrue(receipt_path.exists())

        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))

        # Verify cryptographic link
        actual_manifest_sha = compute_file_sha256(manifest_path)
        self.assertEqual(receipt["manifest_sha256"], actual_manifest_sha)
        self.assertEqual(receipt["run_id"], manifest["run_id"])
        self.assertEqual(receipt["kpi_rows_emitted"], manifest["output_total_rows"])
        self.assertEqual(receipt["status"], "SUCCESS")

    def test_06_publication_failure_is_not_misreported_as_pass(self):
        """Scenario 6: Publication failure is raised as an error, never returning a PASS verdict."""
        runner = KpiProductionRunner(
            run_id="test_run_fail_reporting_v1",
            repo_root=self.test_root,
            external_audit_dir=self.external_audit,
        )
        self.active_runner = runner
        staged_file = runner.staging_run_dir / "data" / "year_2016" / "part-0.parquet"
        make_synthetic_kpi_parquet(staged_file, is_valid=False)

        exec_metrics = {"total_output_rows": 1, "years_processed": {}}
        did_raise = False
        try:
            runner.publish_and_validate(exec_metrics)
        except Exception:
            did_raise = True

        self.assertTrue(did_raise, "Publication with invalid staging must raise an exception")
        self.assertFalse(runner.published_run_dir.exists())
        self.assertTrue(runner.staging_run_dir.exists(), "Failed staging data must be preserved for diagnosis")


if __name__ == "__main__":
    unittest.main()
