"""
Unit tests for SafePublisher implementing the Windows NTFS 7-step publication order.
Conforms to ARCHITECTURE.md Section 2 and T006_FINAL_CORRECTIONS_ADDENDUM.md Section 4 (FIX-03).
Covers normal promotion, content validation, path confinement, unbalanced accounting rejection, and TS-013 fault injection rollback.
"""

from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

import pyarrow as pa
import pyarrow.parquet as pq

SRC_DIR = Path(__file__).resolve().parents[1] / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from flight_pipeline.storage.publication import SafePublisher, is_valid_parquet_file
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

    def test_f05_01_pointer_verification_mismatch_triggers_atomic_rollback(self):
        """F05-01: Step 6 detects pointer mismatch on read-back and rolls back to previous pointer."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            base_dir = Path(tmp_dir)
            publisher = SafePublisher(str(base_dir))

            # Initial valid publication establishes baseline pointer
            staging1 = base_dir / "staging" / "run_001"
            write_valid_parquet(staging1 / "data.parquet", "run_001")
            res1 = publisher.publish("run_001", staging1, RowAccounting(10, 10, 0, 0))
            self.assertTrue(res1.success)
            self.assertEqual(publisher.get_current_pointer(), "run_001")

            # Second publication where Step 6 detects read-back mismatch
            staging2 = base_dir / "staging" / "run_002"
            write_valid_parquet(staging2 / "data.parquet", "run_002")

            call_count = [0]
            real_get = publisher.get_current_pointer

            def mock_get():
                call_count[0] += 1
                # Call 1 is Step 0 (previous_pointer). Call 2 is Step 6 (post-switch verification)
                if call_count[0] == 2:
                    return "unexpected_corrupted_pointer"
                return real_get()

            with patch.object(publisher, "get_current_pointer", side_effect=mock_get):
                res2 = publisher.publish("run_002", staging2, RowAccounting(20, 20, 0, 0))

            self.assertFalse(res2.success)
            self.assertEqual(res2.status, "FAILED_POINTER_VERIFICATION")
            self.assertEqual(res2.aborted_step, 6)
            self.assertEqual(res2.previous_pointer, "run_001")
            # Step 6 rollback returned pointer to run_001
            self.assertEqual(publisher.get_current_pointer(), "run_001")

    def test_f05_02_pointer_verification_rollback_failure_reporting(self):
        """F05-02: Step 6 reports FAILED_POINTER_VERIFICATION_ROLLBACK_ERROR when rollback replacement fails."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            base_dir = Path(tmp_dir)
            publisher = SafePublisher(str(base_dir))

            staging1 = base_dir / "staging" / "run_001"
            write_valid_parquet(staging1 / "data.parquet", "run_001")
            publisher.publish("run_001", staging1, RowAccounting(10, 10, 0, 0))

            staging2 = base_dir / "staging" / "run_002"
            write_valid_parquet(staging2 / "data.parquet", "run_002")

            call_count = [0]
            real_get = publisher.get_current_pointer

            def mock_get():
                call_count[0] += 1
                if call_count[0] == 2:
                    return "unexpected_corrupted_pointer"
                return real_get()

            real_atomic_write = publisher._atomic_write_pointer
            atomic_calls = [0]

            def mock_atomic_write(pval, tmp_prefix=""):
                atomic_calls[0] += 1
                # Call 1 is Step 5 switch. Call 2 is Step 6 rollback attempt
                if atomic_calls[0] == 2:
                    return False  # Simulate NTFS lock failure during rollback
                return real_atomic_write(pval, tmp_prefix)

            with patch.object(publisher, "get_current_pointer", side_effect=mock_get):
                with patch.object(publisher, "_atomic_write_pointer", side_effect=mock_atomic_write):
                    res2 = publisher.publish("run_002", staging2, RowAccounting(20, 20, 0, 0))

            self.assertFalse(res2.success)
            self.assertEqual(res2.status, "FAILED_POINTER_VERIFICATION_ROLLBACK_ERROR")
            self.assertEqual(res2.aborted_step, 6)
            self.assertEqual(res2.previous_pointer, "run_001")

    def test_f05_03_preservation_of_previous_version_and_failure_artifacts(self):
        """F05-03: Non-destructive policy preserves previous version data, staging data, and promoted artifacts on failure."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            base_dir = Path(tmp_dir)
            publisher = SafePublisher(str(base_dir))

            staging1 = base_dir / "staging" / "run_001"
            write_valid_parquet(staging1 / "data.parquet", "version 1 payload")
            res1 = publisher.publish("run_001", staging1, RowAccounting(10, 10, 0, 0))
            self.assertTrue(res1.success)

            prev_run_file = base_dir / "curated" / "runs" / "run_001" / "data.parquet"
            self.assertTrue(prev_run_file.is_file())
            prev_bytes = prev_run_file.read_bytes()

            # Attempt run_002 with fault injection at Step 5
            staging2 = base_dir / "staging" / "run_002"
            write_valid_parquet(staging2 / "data.parquet", "version 2 payload")
            res2 = publisher.publish("run_002", staging2, RowAccounting(20, 20, 0, 0), fault_injection_step5=True)
            self.assertFalse(res2.success)

            # Invariants verification:
            # 1. Previous run files are completely unmodified
            self.assertEqual(prev_run_file.read_bytes(), prev_bytes)
            # 2. Pointer continues to resolve to run_001
            self.assertEqual(publisher.get_current_pointer(), "run_001")
            # 3. Staging directory of failed run is preserved (not purged)
            self.assertTrue(staging2.is_dir())
            self.assertTrue((staging2 / "data.parquet").is_file())
            # 4. Versioned target is preserved for forensic inspection
            versioned2 = base_dir / "curated" / "runs" / "run_002"
            self.assertTrue(versioned2.is_dir())

    def test_f05_04_single_writer_operational_assumption_and_version_collision(self):
        """F05-04: Batch architecture assumes a single writer; concurrent/duplicate version publication is strictly rejected."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            base_dir = Path(tmp_dir)
            publisher = SafePublisher(str(base_dir))

            staging = base_dir / "staging" / "run_batch_01"
            write_valid_parquet(staging / "data.parquet", "batch 1")
            res1 = publisher.publish("run_batch_01", staging, RowAccounting(10, 10, 0, 0))
            self.assertTrue(res1.success)
            self.assertEqual(publisher.get_current_pointer(), "run_batch_01")

            # Duplicate attempt to publish run_batch_01 must fail at Step 3 (immutability)
            staging_dup = base_dir / "staging" / "run_batch_01_concurrent"
            write_valid_parquet(staging_dup / "data.parquet", "duplicate collision payload")
            res_collision = publisher.publish("run_batch_01", staging_dup, RowAccounting(10, 10, 0, 0))

            self.assertFalse(res_collision.success)
            self.assertEqual(res_collision.status, "FAILED_VERSION_EXISTS")
            self.assertEqual(res_collision.aborted_step, 3)
            # Pointer remains on original version
            self.assertEqual(publisher.get_current_pointer(), "run_batch_01")

    def test_parquet_with_valid_magic_bytes_but_corrupted_footer_rejected(self):
        """Verify is_valid_parquet_file and SafePublisher reject files with valid PAR1 magic bytes but corrupt Thrift footers."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            base_dir = Path(tmp_dir)
            publisher = SafePublisher(str(base_dir))

            staging = base_dir / "staging" / "run_corrupt_footer"
            staging.mkdir(parents=True, exist_ok=True)
            corrupt_file = staging / "part-000.parquet"
            # File begins and ends with PAR1, length > 12, but has corrupted Thrift metadata
            corrupt_file.write_bytes(b"PAR1" + b"\x00" * 40 + b"PAR1")

            self.assertFalse(is_valid_parquet_file(corrupt_file))

            res = publisher.publish("run_corrupt_footer", staging, RowAccounting(10, 10, 0, 0))
            self.assertFalse(res.success)
            self.assertEqual(res.status, "FAILED_STAGING_CONTENT_INVALID")
            self.assertEqual(res.aborted_step, 1)

    def test_post_switch_pointer_read_exception_with_previous_pointer(self):
        """FIX-S02: Step 6 pointer read OSError must be caught, rollback to previous pointer, and return error result."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            base_dir = Path(tmp_dir)
            publisher = SafePublisher(str(base_dir))

            staging1 = base_dir / "staging" / "run_prev"
            write_valid_parquet(staging1 / "data.parquet", "prev")
            res1 = publisher.publish("run_prev", staging1, RowAccounting(10, 10, 0, 0))
            self.assertTrue(res1.success)
            self.assertEqual(publisher.get_current_pointer(), "run_prev")

            staging2 = base_dir / "staging" / "run_new"
            write_valid_parquet(staging2 / "data.parquet", "new")

            call_count = [0]
            real_get = publisher.get_current_pointer

            def mock_get(*args, **kwargs):
                call_count[0] += 1
                # Call 1 is Step 0 (read previous). Call 2 is Step 6 (post-switch verification read)
                if call_count[0] == 2:
                    raise OSError("Simulated NTFS access lock on post-switch read")
                return real_get(*args, **kwargs)

            with patch.object(publisher, "get_current_pointer", side_effect=mock_get):
                res2 = publisher.publish("run_new", staging2, RowAccounting(20, 20, 0, 0))

            # Must not crash, must return failed PublicationResult with aborted_step=6
            self.assertFalse(res2.success)
            self.assertIn(res2.status, ("FAILED_POINTER_READ_VERIFICATION", "FAILED_POINTER_VERIFICATION"))
            self.assertEqual(res2.aborted_step, 6)
            self.assertEqual(res2.previous_pointer, "run_prev")
            # Step 6 rollback must have restored pointer to run_prev
            self.assertEqual(publisher.get_current_pointer(), "run_prev")
            # Staging and promoted directory preserved
            self.assertTrue(staging2.is_dir())
            self.assertTrue((base_dir / "curated" / "runs" / "run_new").is_dir())

    def test_post_switch_pointer_read_exception_without_previous_pointer(self):
        """FIX-S02: Step 6 pointer read OSError with previous_pointer=None must rollback cleanly to None."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            base_dir = Path(tmp_dir)
            publisher = SafePublisher(str(base_dir))

            staging = base_dir / "staging" / "run_first"
            write_valid_parquet(staging / "data.parquet", "first")

            call_count = [0]
            real_get = publisher.get_current_pointer

            def mock_get(*args, **kwargs):
                call_count[0] += 1
                if call_count[0] == 2:  # Step 6 read fails on initial run
                    raise OSError("Simulated IO failure on initial pointer read")
                return real_get(*args, **kwargs)

            with patch.object(publisher, "get_current_pointer", side_effect=mock_get):
                res = publisher.publish("run_first", staging, RowAccounting(10, 10, 0, 0))

            self.assertFalse(res.success)
            self.assertIn(res.status, ("FAILED_POINTER_READ_VERIFICATION", "FAILED_POINTER_VERIFICATION"))
            self.assertEqual(res.aborted_step, 6)
            self.assertIsNone(res.previous_pointer)
            self.assertIsNone(publisher.get_current_pointer())

    def test_post_switch_pointer_read_exception_with_rollback_failure(self):
        """FIX-S02: If post-switch read fails AND rollback fails, report FAILED_POINTER_VERIFICATION_ROLLBACK_ERROR."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            base_dir = Path(tmp_dir)
            publisher = SafePublisher(str(base_dir))

            staging1 = base_dir / "staging" / "run_prev"
            write_valid_parquet(staging1 / "data.parquet", "prev")
            publisher.publish("run_prev", staging1, RowAccounting(10, 10, 0, 0))

            staging2 = base_dir / "staging" / "run_new"
            write_valid_parquet(staging2 / "data.parquet", "new")

            call_count = [0]
            real_get = publisher.get_current_pointer

            def mock_get(*args, **kwargs):
                call_count[0] += 1
                if call_count[0] == 2:
                    raise OSError("Simulated post-switch read error")
                return real_get(*args, **kwargs)

            real_atomic_write = publisher._atomic_write_pointer
            atomic_calls = [0]

            def mock_atomic_write(pval, tmp_prefix=""):
                atomic_calls[0] += 1
                if atomic_calls[0] == 2:  # Rollback attempt
                    return False
                return real_atomic_write(pval, tmp_prefix)

            with patch.object(publisher, "get_current_pointer", side_effect=mock_get):
                with patch.object(publisher, "_atomic_write_pointer", side_effect=mock_atomic_write):
                    res2 = publisher.publish("run_new", staging2, RowAccounting(20, 20, 0, 0))

            self.assertFalse(res2.success)
            self.assertEqual(res2.status, "FAILED_POINTER_VERIFICATION_ROLLBACK_ERROR")
            self.assertEqual(res2.aborted_step, 6)

    def test_streaming_sha256_matches_hashlib_and_handles_blocks(self):
        """FIX-S03: Streaming SHA-256 calculation matches hashlib on empty, small, and multi-block files."""
        from hashlib import sha256 as std_sha256
        from flight_pipeline.storage.publication import compute_file_sha256

        with tempfile.TemporaryDirectory() as tmp_dir:
            base = Path(tmp_dir)

            # 1. Empty file
            empty_f = base / "empty.bin"
            empty_f.write_bytes(b"")
            self.assertEqual(compute_file_sha256(empty_f), std_sha256(b"").hexdigest())

            # 2. Small file (< 64KB)
            small_data = b"Hello, Flight Pipeline!" * 100
            small_f = base / "small.bin"
            small_f.write_bytes(small_data)
            self.assertEqual(compute_file_sha256(small_f), std_sha256(small_data).hexdigest())

            # 3. Multi-block file (200KB with 64KB blocks)
            large_data = b"A" * 70000 + b"B" * 70000 + b"C" * 60000
            large_f = base / "large.bin"
            large_f.write_bytes(large_data)
            self.assertEqual(compute_file_sha256(large_f), std_sha256(large_data).hexdigest())

            # 4. Non-existent file raises FileNotFoundError
            with self.assertRaises(FileNotFoundError):
                compute_file_sha256(base / "nonexistent.bin")

    def test_initial_pointer_read_persistent_exception(self):
        """PUB-01: When get_current_pointer raises persistent OSError, publish aborts at step 0 without side effects."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            base = Path(tmp_dir)
            publisher = SafePublisher(str(base))
            staging = base / "staging" / "run_fail"
            write_valid_parquet(staging / "part-0.parquet", "data")

            with patch.object(publisher, "get_current_pointer", side_effect=OSError("Simulated persistent pointer lock")):
                res = publisher.publish("run_fail", staging, RowAccounting(10, 10, 0, 0))

            self.assertFalse(res.success)
            self.assertEqual(res.status, "FAILED_INITIAL_POINTER_READ")
            self.assertEqual(res.aborted_step, 0)
            self.assertIsNone(res.previous_pointer)
            self.assertIn("Initial pointer read failed before publication", res.error_message)
            # Ensure no data was promoted
            self.assertFalse((publisher.runs_root / "run_fail").exists())
            # Ensure pointer was not touched
            self.assertFalse(publisher.pointer_file.exists())

    def test_initial_pointer_read_transient_retry_success(self):
        """PUB-01: Transient OSError on initial read is retried by get_current_pointer and succeeds."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            base = Path(tmp_dir)
            publisher = SafePublisher(str(base))
            publisher.curated_root.mkdir(parents=True, exist_ok=True)
            publisher.pointer_file.write_text("run_existing\n", encoding="utf-8")

            call_count = [0]
            real_read_text = Path.read_text

            def flaky_read_text(*args, **kwargs):
                call_count[0] += 1
                if call_count[0] == 1:
                    raise OSError("Transient file lock on initial read")
                return real_read_text(publisher.pointer_file, *args, **kwargs)

            staging = base / "staging" / "run_new"
            write_valid_parquet(staging / "part-0.parquet", "data")

            with patch("pathlib.Path.read_text", side_effect=flaky_read_text):
                res = publisher.publish("run_new", staging, RowAccounting(10, 10, 0, 0))

            self.assertTrue(res.success)
            self.assertEqual(res.status, "PUBLISHED")
            self.assertEqual(res.previous_pointer, "run_existing")
            self.assertEqual(publisher.get_current_pointer(), "run_new")

    def test_initial_pointer_missing_is_not_treated_as_error(self):
        """PUB-01: When pointer does not exist initially, get_current_pointer returns None and publish proceeds."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            base = Path(tmp_dir)
            publisher = SafePublisher(str(base))
            staging = base / "staging" / "run_first"
            write_valid_parquet(staging / "part-0.parquet", "first_data")

            # Ensure pointer file does not exist
            self.assertFalse(publisher.pointer_file.exists())
            self.assertIsNone(publisher.get_current_pointer())

            res = publisher.publish("run_first", staging, RowAccounting(5, 5, 0, 0))
            self.assertTrue(res.success)
            self.assertEqual(res.status, "PUBLISHED")
            self.assertIsNone(res.previous_pointer)
            self.assertEqual(publisher.get_current_pointer(), "run_first")


if __name__ == "__main__":
    unittest.main()




