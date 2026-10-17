"""
Unit tests for RunManifest and RowAccounting models.
Conforms to DATA_CONTRACT.md (DC-11/12) and ARCHITECTURE.md specifications.
"""

import json
import sys
import tempfile
import unittest
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parents[1] / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from flight_pipeline.utils.run_manifest import RunManifest, RowAccounting


class TestRunManifest(unittest.TestCase):
    def test_row_accounting_balance_invariant(self):
        """Test DC-11 three-state disjoint row accounting balance check."""
        # Balanced case: raw = accepted + quarantined + rejected
        acc_valid = RowAccounting(
            raw_row_count=1000,
            accepted_row_count=980,
            quarantined_row_count=15,
            rejected_row_count=5,
        )
        self.assertTrue(acc_valid.is_balanced())

        # Unbalanced case: sum != raw
        acc_invalid = RowAccounting(
            raw_row_count=1000,
            accepted_row_count=950,
            quarantined_row_count=10,
            rejected_row_count=5,
        )
        self.assertFalse(acc_invalid.is_balanced())

    def test_run_manifest_lifecycle_and_hashing(self):
        """Test RunManifest creation, input/output tracking, close, and SHA-256 computation."""
        manifest = RunManifest(run_id="run_20261017_test", task_id="T-009")
        self.assertEqual(manifest.status, "IN_PROGRESS")
        self.assertIn("python", manifest.runtime_versions)

        # Record inputs and outputs
        manifest.record_input("data/raw/tabular/2016/flight_with_weather_2016.csv", 1000000)
        manifest.record_output("data/curated/runs/run_20261017_test/", 500000)

        # Attach balanced accounting
        manifest.row_accounting = RowAccounting(500, 490, 8, 2)
        manifest.close(status="SUCCESS")

        self.assertEqual(manifest.status, "SUCCESS")
        self.assertIsNotNone(manifest.end_time)

        # Test JSON serialization and save
        with tempfile.TemporaryDirectory() as tmp_dir:
            out_file = Path(tmp_dir) / "manifest.json"
            computed_sha = manifest.save(str(out_file))

            self.assertTrue(out_file.is_file())
            content = out_file.read_text(encoding="utf-8")
            data = json.loads(content)
            self.assertEqual(data["run_id"], "run_20261017_test")
            self.assertTrue(data["row_accounting"]["is_balanced"])
            self.assertEqual(len(computed_sha), 64)


if __name__ == "__main__":
    unittest.main()
