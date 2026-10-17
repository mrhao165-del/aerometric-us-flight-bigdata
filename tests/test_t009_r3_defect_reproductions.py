"""
Pre-fix defect reproduction tests for T009-R3 (F-01 through F-05).
These tests reflect the required behavior per canonical contracts and verify remediation.
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

from flight_pipeline.utils.run_manifest import RunManifest, RowAccounting, MetricAccounting
from flight_pipeline.storage.publication import SafePublisher


class TestT009R3DefectReproductions(unittest.TestCase):
    def test_f01_manifest_save_sha256_matches_disk_bytes(self):
        """F-01: Returned sha256 from RunManifest.save() must match exact disk bytes."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            out_file = Path(tmp_dir) / "manifest.json"
            manifest = RunManifest(run_id="run_f01_test", task_id="T-009")
            returned_sha = manifest.save(str(out_file))
            disk_sha = sha256(out_file.read_bytes()).hexdigest()
            self.assertEqual(
                returned_sha,
                disk_sha,
                f"F-01 Defect: returned {returned_sha} != disk {disk_sha}",
            )

    def test_f02_publication_rejects_fake_parquet_content(self):
        """F-02: SafePublisher must reject non-Parquet files masquerading as .parquet."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            base_dir = Path(tmp_dir)
            publisher = SafePublisher(str(base_dir))
            staging = base_dir / "staging" / "run_f02"
            staging.mkdir(parents=True, exist_ok=True)
            # Text file disguised as parquet
            (staging / "part-000.parquet").write_text("NOT A REAL PARQUET FILE", encoding="utf-8")
            accounting = RowAccounting(10, 10, 0, 0)

            result = publisher.publish("run_f02", staging, accounting)
            self.assertFalse(result.success, "F-02 Defect: Fake parquet was erroneously accepted")
            self.assertEqual(result.status, "FAILED_STAGING_CONTENT_INVALID")

    def test_f03_run_id_path_traversal_strictly_rejected(self):
        """F-03: SafePublisher must strictly reject path traversal in run_id before writing."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            base_dir = Path(tmp_dir)
            publisher = SafePublisher(str(base_dir))
            staging = base_dir / "staging" / "run_f03"
            staging.mkdir(parents=True, exist_ok=True)
            (staging / "data.txt").write_text("data", encoding="utf-8")
            accounting = RowAccounting(10, 10, 0, 0)

            payloads = [
                "../../escaped",
                "../outside",
                "/root/escape",
                "C:\\escape",
                "run/sub",
                "run\\sub",
                "",
                "   ",
            ]
            for bad_id in payloads:
                result = publisher.publish(bad_id, staging, accounting)
                self.assertFalse(
                    result.success,
                    f"F-03 Defect: Malicious run_id {bad_id!r} was not rejected",
                )
                self.assertEqual(result.status, "FAILED_INVALID_RUN_ID")
                if bad_id.strip() and not bad_id.startswith(("/", "\\", "C:")):
                    self.assertFalse(
                        (publisher.runs_root / bad_id).exists(),
                        f"Directory was created: {bad_id}",
                    )

    def test_f04_dc11_rejects_negative_counts(self):
        """F-04: RowAccounting must reject negative counts and not declare balanced."""
        try:
            bad_row = RowAccounting(-1, -1, 0, 0)
            self.assertFalse(bad_row.is_balanced(), "F-04 Defect: Negative row count declared balanced")
        except (ValueError, TypeError):
            pass

    def test_f04_dc12_rejects_valid_exceeding_records(self):
        """F-04: MetricAccounting must reject count_metric_valid > count_records."""
        try:
            bad_metric = MetricAccounting("ARR_DELAY", count_records=100, count_metric_valid=120)
            rate = bad_metric.calculate_metric_valid_rate()
            self.assertIsNone(rate, f"F-04 Defect: Rate {rate} exceeds 1.0 without rejection")
        except (ValueError, TypeError):
            pass


if __name__ == "__main__":
    unittest.main()
