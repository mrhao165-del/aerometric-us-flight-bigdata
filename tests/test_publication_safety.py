"""
Unit tests for SafePublisher implementing the Windows NTFS 7-step publication order.
Conforms to ARCHITECTURE.md Section 2 and T006_FINAL_CORRECTIONS_ADDENDUM.md Section 4 (FIX-03).
Covers normal promotion, content validation, path confinement, unbalanced accounting rejection, and TS-013 fault injection rollback.
"""

from pathlib import Path
import sys
import tempfile
import unittest

import pyarrow as pa
import pyarrow.parquet as pq

SRC_DIR = Path(__file__).resolve().parents[1] / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from flight_pipeline.storage.publication import SafePublisher
from flight_pipeline.utils.run_manifest import RowAccounting


def write_valid_parquet(target: Path, text: str = "test_payload") -> None:
    """Helper to write a valid small synthetic Parquet file for testing."""
    target.parent.mkdir(parents=True, exist_ok=True)
    table = pa.table({"data": [text]})
    pq.write_table(table, str(target))


class TestPublicationSafety(unittest.TestCase):
    def test_successful_publication_sequence(self):
        """Test complete 7-step safe publication with balanced row accounting and valid Parquet."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            base_dir = Path(tmp_dir)
            publisher = SafePublisher(str(base_dir))

            staging = base_dir / "staging" / "run_001"
            write_valid_parquet(staging / "part-000.parquet", "run_001_data")

            # Balanced accounting: 100 = 95 + 4 + 1
            accounting = RowAccounting(100, 95, 4, 1)

            result = publisher.publish("run_001", staging, accounting)

            self.assertTrue(result.success)
            self.assertEqual(result.status, "PUBLISHED")
            self.assertEqual(result.pointer_value, "run_001")
            self.assertIsNone(result.previous_pointer)
            self.assertEqual(publisher.get_current_pointer(), "run_001")

            # Verify promoted data exists in versioned location
            promoted_file = base_dir / "curated" / "runs" / "run_001" / "part-000.parquet"
            self.assertTrue(promoted_file.is_file())

    def test_unbalanced_accounting_aborts_publication(self):
        """Test Step 2 aborts publication with ACCOUNTING_UNVERIFIED when accounting is unbalanced."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            base_dir = Path(tmp_dir)
            publisher = SafePublisher(str(base_dir))

            # Initial successful publication to establish a pointer
            staging1 = base_dir / "staging" / "run_init"
            write_valid_parquet(staging1 / "data.parquet", "init data")
            publisher.publish("run_init", staging1, RowAccounting(50, 48, 2, 0))
            self.assertEqual(publisher.get_current_pointer(), "run_init")

            # New run with UNBALANCED accounting: 100 != 80 + 5 + 2
            staging2 = base_dir / "staging" / "run_unbalanced"
            write_valid_parquet(staging2 / "data.parquet", "unbalanced data")
            bad_accounting = RowAccounting(100, 80, 5, 2)

            result = publisher.publish("run_unbalanced", staging2, bad_accounting)

            self.assertFalse(result.success)
            self.assertEqual(result.status, "ACCOUNTING_UNVERIFIED")
            self.assertEqual(result.aborted_step, 2)
            # Verify pointer did NOT change (still points to run_init)
            self.assertEqual(publisher.get_current_pointer(), "run_init")

    def test_fault_injection_step5_preserves_previous_pointer_and_staging(self):
        """Test TS-013 fault injection at Step 5 triggers Step 6 non-destructive rollback."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            base_dir = Path(tmp_dir)
            publisher = SafePublisher(str(base_dir))

            # 1. Establish initial good run
            staging1 = base_dir / "staging" / "run_good"
            write_valid_parquet(staging1 / "data.parquet", "good data")
            publisher.publish("run_good", staging1, RowAccounting(10, 10, 0, 0))
            self.assertEqual(publisher.get_current_pointer(), "run_good")

            # 2. Execute new run with forced fault injection at Step 5
            staging2 = base_dir / "staging" / "run_faulty"
            write_valid_parquet(staging2 / "data.parquet", "faulty data")
            good_accounting = RowAccounting(20, 18, 2, 0)

            result = publisher.publish("run_faulty", staging2, good_accounting, fault_injection_step5=True)

            self.assertFalse(result.success)
            self.assertEqual(result.status, "FAILED_POINTER_SWITCH")
            self.assertEqual(result.aborted_step, 5)

            # Assert Step 6 Invariants:
            # - Pointer remains strictly preserved to the previous valid run
            self.assertEqual(publisher.get_current_pointer(), "run_good")
            self.assertEqual(result.previous_pointer, "run_good")
            # - Staging and versioned run remain preserved for audit (no destructive deletion)
            self.assertTrue(staging2.is_dir())
            versioned_faulty = base_dir / "curated" / "runs" / "run_faulty"
            self.assertTrue(versioned_faulty.is_dir())

    def test_version_immutability_rejection(self):
        """Test Step 3 strictly rejects promotion if versioned directory already exists (immutability)."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            base_dir = Path(tmp_dir)
            publisher = SafePublisher(str(base_dir))

            staging = base_dir / "staging" / "run_v1"
            write_valid_parquet(staging / "data.parquet", "v1 original")
            res1 = publisher.publish("run_v1", staging, RowAccounting(10, 10, 0, 0))
            self.assertTrue(res1.success)

            # Attempt to publish again with same run_id but different data
            staging_tamper = base_dir / "staging" / "run_v1_tamper"
            write_valid_parquet(staging_tamper / "data.parquet", "v1 tampered")
            res2 = publisher.publish("run_v1", staging_tamper, RowAccounting(10, 10, 0, 0))

            self.assertFalse(res2.success)
            self.assertEqual(res2.status, "FAILED_VERSION_EXISTS")
            self.assertEqual(res2.aborted_step, 3)

    def test_rejection_of_fake_parquet_content(self):
        """F-02: SafePublisher strictly rejects non-Parquet files masquerading as .parquet."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            base_dir = Path(tmp_dir)
            publisher = SafePublisher(str(base_dir))
            staging = base_dir / "staging" / "run_fake"
            staging.mkdir(parents=True, exist_ok=True)
            (staging / "part-000.parquet").write_text("FAKE PARQUET TEXT CONTENT", encoding="utf-8")
            res = publisher.publish("run_fake", staging, RowAccounting(10, 10, 0, 0))
            self.assertFalse(res.success)
            self.assertEqual(res.status, "FAILED_STAGING_CONTENT_INVALID")

    def test_rejection_of_path_traversal_run_id(self):
        """F-03: SafePublisher strictly rejects path traversal in run_id before writing."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            base_dir = Path(tmp_dir)
            publisher = SafePublisher(str(base_dir))
            staging = base_dir / "staging" / "run_good"
            write_valid_parquet(staging / "data.parquet", "good")

            for bad_id in ("../../outside", "../escaped", "/absolute", "C:\\escape"):
                res = publisher.publish(bad_id, staging, RowAccounting(10, 10, 0, 0))
                self.assertFalse(res.success)
                self.assertEqual(res.status, "FAILED_INVALID_RUN_ID")


if __name__ == "__main__":
    unittest.main()
