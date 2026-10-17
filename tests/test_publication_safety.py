"""
Unit tests for SafePublisher implementing the Windows NTFS 7-step publication order.
Conforms to ARCHITECTURE.md Section 2 and T006_FINAL_CORRECTIONS_ADDENDUM.md Section 4 (FIX-03).
Covers normal promotion, unbalanced accounting rejection, and TS-013 fault injection rollback.
"""

import sys
import tempfile
import unittest
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parents[1] / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from flight_pipeline.storage.publication import SafePublisher
from flight_pipeline.utils.run_manifest import RowAccounting


class TestPublicationSafety(unittest.TestCase):
    def test_successful_publication_sequence(self):
        """Test complete 7-step safe publication with balanced row accounting."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            base_dir = Path(tmp_dir)
            publisher = SafePublisher(str(base_dir))

            # Create mock staging data
            staging = base_dir / "staging" / "run_001"
            staging.mkdir(parents=True, exist_ok=True)
            (staging / "part-000.parquet").write_text("dummy parquet content", encoding="utf-8")

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
            staging1.mkdir(parents=True, exist_ok=True)
            (staging1 / "data.parquet").write_text("init data", encoding="utf-8")
            publisher.publish("run_init", staging1, RowAccounting(50, 48, 2, 0))
            self.assertEqual(publisher.get_current_pointer(), "run_init")

            # New run with UNBALANCED accounting: 100 != 80 + 5 + 2
            staging2 = base_dir / "staging" / "run_unbalanced"
            staging2.mkdir(parents=True, exist_ok=True)
            (staging2 / "data.parquet").write_text("unbalanced data", encoding="utf-8")
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
            staging1.mkdir(parents=True, exist_ok=True)
            (staging1 / "data.parquet").write_text("good data", encoding="utf-8")
            publisher.publish("run_good", staging1, RowAccounting(10, 10, 0, 0))
            self.assertEqual(publisher.get_current_pointer(), "run_good")

            # 2. Execute new run with forced fault injection at Step 5
            staging2 = base_dir / "staging" / "run_faulty"
            staging2.mkdir(parents=True, exist_ok=True)
            (staging2 / "data.parquet").write_text("faulty data", encoding="utf-8")
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


if __name__ == "__main__":
    unittest.main()
