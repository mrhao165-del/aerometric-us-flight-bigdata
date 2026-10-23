"""
tests/test_verify_staging_pointer.py

Unit and negative test suite for tools/qa/verify_staging_pointer.py.
Conforms to ARCHITECTURE.md, T006_FINAL_CORRECTIONS_ADDENDUM.md, and Gate G6 Operational Standards.

Covers:
- Positive verification of valid pointer, published Parquet files, and run_manifest.json.
- Detection of uninitialized state with allow_uninitialized.
- Fail-closed detection of:
  * Missing pointer file
  * Empty pointer file
  * Path traversal attempts in pointer (.., absolute paths, separators)
  * Dangling pointer (target directory missing)
  * Target containing corrupted Parquet file
  * Target containing no Parquet files
  * Missing required manifest
  * Corrupted manifest JSON
  * Manifest run_id mismatch with pointer
- Immutability check ensuring the verifier strictly never modifies files or directories.
"""

import json
from pathlib import Path
import sys
import tempfile
import time
import unittest

import pyarrow as pa
import pyarrow.parquet as pq

ROOT_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT_DIR / "src"
TOOLS_DIR = ROOT_DIR / "tools" / "qa"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

from verify_staging_pointer import verify_staging_pointer, PointerVerificationResult


def write_dummy_parquet(target: Path, text: str = "valid_parquet_payload") -> None:
    """Helper to write a valid small Parquet file."""
    target.parent.mkdir(parents=True, exist_ok=True)
    table = pa.table({"col1": [text]})
    pq.write_table(table, str(target))


class TestVerifyStagingPointer(unittest.TestCase):
    def test_positive_valid_pointer_with_manifest_and_parquet(self):
        """Positive: Pointer points to valid run directory with Parquet data and matching manifest."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            base_dir = Path(tmp_dir)
            curated_root = base_dir / "curated"
            runs_root = curated_root / "runs"
            run_id = "run_20261020_001"
            run_dir = runs_root / run_id
            run_dir.mkdir(parents=True, exist_ok=True)

            # Write pointer file
            pointer_file = curated_root / "latest_run_id.txt"
            pointer_file.write_text(run_id + "\n", encoding="utf-8")

            # Write valid Parquet file
            write_dummy_parquet(run_dir / "part-000.parquet", "test_content")

            # Write matching manifest
            manifest_file = run_dir / "run_manifest.json"
            manifest_data = {
                "run_id": run_id,
                "task_id": "T-012",
                "status": "SUCCESS",
                "row_accounting": {"raw_row_count": 100, "accepted_row_count": 100},
            }
            manifest_file.write_text(json.dumps(manifest_data), encoding="utf-8")

            res = verify_staging_pointer(base_dir, require_manifest=True, require_parquet=True)

            self.assertTrue(res.success)
            self.assertEqual(res.status, "VALID_POINTER")
            self.assertEqual(res.pointer_value, run_id)
            self.assertEqual(res.target_dir, str(run_dir.resolve()))
            self.assertEqual(res.parquet_files_found, 1)
            self.assertEqual(res.valid_parquet_files, 1)
            self.assertTrue(res.manifest_found)
            self.assertEqual(res.manifest_run_id, run_id)
            self.assertIsNone(res.error_message)

    def test_uninitialized_state_allowed(self):
        """Positive: Pointer missing but allow_uninitialized=True succeeds cleanly."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            base_dir = Path(tmp_dir)
            res = verify_staging_pointer(base_dir, allow_uninitialized=True)
            self.assertTrue(res.success)
            self.assertEqual(res.status, "UNINITIALIZED_POINTER_ALLOWED")

    def test_missing_pointer_file_fails_by_default(self):
        """Negative: Missing pointer file fails when allow_uninitialized=False."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            base_dir = Path(tmp_dir)
            res = verify_staging_pointer(base_dir, allow_uninitialized=False)
            self.assertFalse(res.success)
            self.assertEqual(res.status, "MISSING_POINTER_FILE")
            self.assertIn("does not exist", res.error_message)

    def test_empty_pointer_file_fails(self):
        """Negative: Empty pointer file fails fail-closed."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            base_dir = Path(tmp_dir)
            pointer_file = base_dir / "curated" / "latest_run_id.txt"
            pointer_file.parent.mkdir(parents=True, exist_ok=True)
            pointer_file.write_text("   \n\t  ", encoding="utf-8")

            res = verify_staging_pointer(base_dir)
            self.assertFalse(res.success)
            self.assertEqual(res.status, "EMPTY_POINTER_FILE")

    def test_path_traversal_detection(self):
        """Negative: Path traversal in pointer is strictly rejected."""
        traversal_payloads = [
            "../../outside",
            "..\\outside",
            "/absolute/root",
            "run_001/subdir",
            "run_001\\subdir",
            "C:\\escaped",
        ]
        for bad_id in traversal_payloads:
            with tempfile.TemporaryDirectory() as tmp_dir:
                base_dir = Path(tmp_dir)
                pointer_file = base_dir / "curated" / "latest_run_id.txt"
                pointer_file.parent.mkdir(parents=True, exist_ok=True)
                pointer_file.write_text(bad_id, encoding="utf-8")

                res = verify_staging_pointer(base_dir)
                self.assertFalse(res.success)
                self.assertIn(res.status, ("PATH_TRAVERSAL_DETECTED", "INVALID_RUN_ID_FORMAT"))

    def test_dangling_pointer_detected(self):
        """Negative: Pointer points to a run_id whose directory does not exist."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            base_dir = Path(tmp_dir)
            pointer_file = base_dir / "curated" / "latest_run_id.txt"
            pointer_file.parent.mkdir(parents=True, exist_ok=True)
            pointer_file.write_text("run_dangling_ghost_999\n", encoding="utf-8")

            res = verify_staging_pointer(base_dir)
            self.assertFalse(res.success)
            self.assertEqual(res.status, "DANGLING_POINTER_TARGET_MISSING")
            self.assertIn("Dangling pointer detected", res.error_message)

    def test_corrupt_parquet_detected(self):
        """Negative: Corrupt Parquet file in target run directory is detected."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            base_dir = Path(tmp_dir)
            run_id = "run_corrupt_pq"
            run_dir = base_dir / "curated" / "runs" / run_id
            run_dir.mkdir(parents=True, exist_ok=True)
            pointer_file = base_dir / "curated" / "latest_run_id.txt"
            pointer_file.write_text(run_id, encoding="utf-8")

            # Write fake Parquet file
            fake_pq = run_dir / "bad.parquet"
            fake_pq.write_text("NOT A REAL PARQUET FILE CONTENT", encoding="utf-8")

            res = verify_staging_pointer(base_dir, require_parquet=True)
            self.assertFalse(res.success)
            self.assertEqual(res.status, "CORRUPT_PARQUET_DETECTED")

    def test_no_parquet_files_found_when_required(self):
        """Negative: Target directory exists but has no Parquet files."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            base_dir = Path(tmp_dir)
            run_id = "run_empty_dir"
            run_dir = base_dir / "curated" / "runs" / run_id
            run_dir.mkdir(parents=True, exist_ok=True)
            pointer_file = base_dir / "curated" / "latest_run_id.txt"
            pointer_file.write_text(run_id, encoding="utf-8")

            res = verify_staging_pointer(base_dir, require_parquet=True)
            self.assertFalse(res.success)
            self.assertEqual(res.status, "NO_PARQUET_FILES_FOUND")

    def test_missing_required_manifest(self):
        """Negative: Missing manifest fails when require_manifest=True."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            base_dir = Path(tmp_dir)
            run_id = "run_no_manifest"
            run_dir = base_dir / "curated" / "runs" / run_id
            write_dummy_parquet(run_dir / "data.parquet")
            pointer_file = base_dir / "curated" / "latest_run_id.txt"
            pointer_file.write_text(run_id, encoding="utf-8")

            res = verify_staging_pointer(base_dir, require_manifest=True)
            self.assertFalse(res.success)
            self.assertEqual(res.status, "MISSING_RUN_MANIFEST")

    def test_corrupt_manifest_json(self):
        """Negative: Malformed JSON in manifest file is detected."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            base_dir = Path(tmp_dir)
            run_id = "run_corrupt_manifest"
            run_dir = base_dir / "curated" / "runs" / run_id
            write_dummy_parquet(run_dir / "data.parquet")
            pointer_file = base_dir / "curated" / "latest_run_id.txt"
            pointer_file.write_text(run_id, encoding="utf-8")

            (run_dir / "run_manifest.json").write_text("{CORRUPT JSON NOT VALID", encoding="utf-8")

            res = verify_staging_pointer(base_dir, require_manifest=False)
            self.assertFalse(res.success)
            self.assertEqual(res.status, "CORRUPT_MANIFEST_FILE")

    def test_manifest_run_id_mismatch(self):
        """Negative: Manifest run_id differs from pointer run_id."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            base_dir = Path(tmp_dir)
            run_id = "run_alpha"
            run_dir = base_dir / "curated" / "runs" / run_id
            write_dummy_parquet(run_dir / "data.parquet")
            pointer_file = base_dir / "curated" / "latest_run_id.txt"
            pointer_file.write_text(run_id, encoding="utf-8")

            (run_dir / "run_manifest.json").write_text(
                json.dumps({"run_id": "run_beta_mismatched"}), encoding="utf-8"
            )

            res = verify_staging_pointer(base_dir, require_manifest=False)
            self.assertFalse(res.success)
            self.assertEqual(res.status, "MANIFEST_RUN_ID_MISMATCH")

    def test_verifier_is_strictly_read_only(self):
        """Invariant: Verifier must not modify, touch, or alter any disk file or directory."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            base_dir = Path(tmp_dir)
            run_id = "run_readonly_test"
            run_dir = base_dir / "curated" / "runs" / run_id
            pq_file = run_dir / "data.parquet"
            write_dummy_parquet(pq_file)
            manifest_file = run_dir / "run_manifest.json"
            manifest_file.write_text(json.dumps({"run_id": run_id}), encoding="utf-8")
            pointer_file = base_dir / "curated" / "latest_run_id.txt"
            pointer_file.write_text(run_id, encoding="utf-8")

            # Record stats before
            pointer_stat_before = pointer_file.stat()
            pq_stat_before = pq_file.stat()
            manifest_stat_before = manifest_file.stat()

            time.sleep(0.01)
            res = verify_staging_pointer(base_dir, require_manifest=True, require_parquet=True)
            self.assertTrue(res.success)

            # Record stats after
            pointer_stat_after = pointer_file.stat()
            pq_stat_after = pq_file.stat()
            manifest_stat_after = manifest_file.stat()

            self.assertEqual(pointer_stat_before.st_mtime_ns, pointer_stat_after.st_mtime_ns)
            self.assertEqual(pointer_stat_before.st_size, pointer_stat_after.st_size)
            self.assertEqual(pq_stat_before.st_mtime_ns, pq_stat_after.st_mtime_ns)
            self.assertEqual(pq_stat_before.st_size, pq_stat_after.st_size)
            self.assertEqual(manifest_stat_before.st_mtime_ns, manifest_stat_after.st_mtime_ns)
            self.assertEqual(manifest_stat_before.st_size, manifest_stat_after.st_size)

    def test_positive_valid_pointer_with_coordinator_metadata_manifest(self):
        """Positive: Pointer resolves manifest located at base_dir / metadata / {run_id} / run_manifest.json."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            base_dir = Path(tmp_dir)
            curated_root = base_dir / "curated"
            runs_root = curated_root / "runs"
            run_id = "run_coord_001"
            run_dir = runs_root / run_id
            run_dir.mkdir(parents=True, exist_ok=True)

            pointer_file = curated_root / "latest_run_id.txt"
            pointer_file.write_text(run_id + "\n", encoding="utf-8")
            write_dummy_parquet(run_dir / "part-000.parquet", "data")

            # Place manifest in IngestionCoordinator metadata root: base_dir / metadata / run_id
            meta_dir = base_dir / "metadata" / run_id
            meta_dir.mkdir(parents=True, exist_ok=True)
            manifest_file = meta_dir / "run_manifest.json"
            manifest_file.write_text(
                json.dumps({"run_id": run_id, "status": "SUCCESS"}), encoding="utf-8"
            )

            res = verify_staging_pointer(base_dir, require_manifest=True, require_parquet=True)
            self.assertTrue(res.success)
            self.assertEqual(res.status, "VALID_POINTER")
            self.assertTrue(res.manifest_found)
            self.assertEqual(res.manifest_run_id, run_id)
            self.assertEqual(res.manifest_path, str(manifest_file))


if __name__ == "__main__":
    unittest.main()
