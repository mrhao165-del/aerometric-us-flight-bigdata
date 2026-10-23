"""
tests/test_coordinator_preflight_unblock.py

Targeted test suite verifying fail-closed CLI preflight and operational unblock
for Task T012-MINIMAL-UNBLOCK (Scope D).

Covers all 10 mandatory test scenarios:
1. Valid preflight using synthetic approved source metadata (PASS).
2. Missing RAW source (FAIL).
3. Byte-size mismatch (FAIL).
4. SHA-256 mismatch where approved baseline is present (FAIL).
5. Active writer lock (BLOCKED).
6. Unsafe pointer or unresolved recovery state (BLOCKED).
7. Duplicate run_id (BLOCKED).
8. Invalid survey year or run_id (BLOCKED).
9. Unauthorized live execution returns nonzero without starting ingestion (BLOCKED).
10. CLI root/path resolution matches SourceValidator and production storage configuration (PASS).
"""

import hashlib
import io
import json
import os
from contextlib import redirect_stdout, redirect_stderr
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from typing import Dict
from unittest.mock import patch

SRC_DIR = Path(__file__).resolve().parents[1] / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from flight_pipeline.ingestion.coordinator import main as coordinator_main
from flight_pipeline.ingestion.source_validator import SourceEntry
from flight_pipeline.storage.locking import LockMetadata, PidLivenessStatus


class TestCoordinatorPreflightUnblock(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name).resolve()
        self.data_dir = self.root / "data"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Setup synthetic 2016 CSV
        self.raw_dir = self.data_dir / "raw" / "tabular" / "2016"
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.csv_path = self.raw_dir / "flight_with_weather_2016.csv"

        # Create known synthetic content
        self.csv_content = b"YEAR,QUARTER,MONTH,DAY_OF_MONTH,FL_DATE\n2016,1,1,1,2016-01-01\n"
        self.csv_bytes = len(self.csv_content)
        self.csv_sha256 = hashlib.sha256(self.csv_content).hexdigest()
        self.csv_path.write_bytes(self.csv_content)

        self.synthetic_inventory: Dict[int, SourceEntry] = {
            2016: SourceEntry(
                year=2016,
                relative_path="data/raw/tabular/2016/flight_with_weather_2016.csv",
                audited_row_count=1,
                audited_byte_size=self.csv_bytes,
                audited_column_count=34,
            )
        }
        self.synthetic_approved_hashes: Dict[int, str] = {
            2016: self.csv_sha256,
        }

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_01_valid_preflight_synthetic_approved(self):
        """Scenario 1: Valid preflight using synthetic approved source metadata exits 0."""
        code = coordinator_main(
            argv=[
                "--years", "2016",
                "--run-id", "run_synthetic_v1",
                "--dry-run-preflight",
                "--base-data-dir", str(self.data_dir),
            ],
            approved_baseline_hashes=self.synthetic_approved_hashes,
            custom_inventory=self.synthetic_inventory,
        )
        self.assertEqual(code, 0)

    def test_02_missing_raw_source_fails(self):
        """Scenario 2: Missing RAW source fails preflight with exit code 1."""
        self.csv_path.unlink()
        code = coordinator_main(
            argv=[
                "--years", "2016",
                "--run-id", "run_synthetic_v1",
                "--dry-run-preflight",
                "--base-data-dir", str(self.data_dir),
            ],
            approved_baseline_hashes=self.synthetic_approved_hashes,
            custom_inventory=self.synthetic_inventory,
        )
        self.assertEqual(code, 1)

    def test_03_byte_size_mismatch_fails(self):
        """Scenario 3: Byte-size mismatch fails preflight with exit code 1."""
        # Append extra byte to cause size mismatch
        self.csv_path.write_bytes(self.csv_content + b"\n")
        code = coordinator_main(
            argv=[
                "--years", "2016",
                "--run-id", "run_synthetic_v1",
                "--dry-run-preflight",
                "--base-data-dir", str(self.data_dir),
            ],
            approved_baseline_hashes=self.synthetic_approved_hashes,
            custom_inventory=self.synthetic_inventory,
        )
        self.assertEqual(code, 1)

    def test_04_sha256_mismatch_with_approved_baseline_fails(self):
        """Scenario 4: Same size but SHA-256 mismatch with approved baseline fails preflight."""
        # Mutate last byte keeping exact same byte size
        mutated_content = self.csv_content[:-1] + b"X"
        self.csv_path.write_bytes(mutated_content)
        self.assertEqual(len(mutated_content), self.csv_bytes)
        self.assertNotEqual(hashlib.sha256(mutated_content).hexdigest(), self.csv_sha256)

        code = coordinator_main(
            argv=[
                "--years", "2016",
                "--run-id", "run_synthetic_v1",
                "--dry-run-preflight",
                "--base-data-dir", str(self.data_dir),
            ],
            approved_baseline_hashes=self.synthetic_approved_hashes,
            custom_inventory=self.synthetic_inventory,
        )
        self.assertEqual(code, 1)

    def test_05_active_writer_lock_blocked(self):
        """Scenario 5: Active writer lock held blocks preflight with exit code 1 and accurate status."""
        lock_dir = self.data_dir / "locks"
        lock_dir.mkdir(parents=True, exist_ok=True)
        lock_file = lock_dir / ".pipeline.lock"

        # Write lock metadata with current process PID (active alive process)
        meta = LockMetadata(
            owner_token="tok_test_active_123",
            run_id="run_competing_writer",
            pid=os.getpid(),
            hostname="test_host",
            created_at="2026-10-21T00:00:00Z",
        )
        lock_file.write_text(meta.to_json(), encoding="utf-8")

        buf_out = io.StringIO()
        with redirect_stdout(buf_out):
            code = coordinator_main(
                argv=[
                    "--years", "2016",
                    "--run-id", "run_synthetic_v1",
                    "--dry-run-preflight",
                    "--base-data-dir", str(self.data_dir),
                ],
                approved_baseline_hashes=self.synthetic_approved_hashes,
                custom_inventory=self.synthetic_inventory,
            )
        output = buf_out.getvalue()
        self.assertEqual(code, 1)
        self.assertIn("ACTIVE_WRITER_RUNNING", output)
        self.assertIn("Active writer lock held by PID", output)
        self.assertNotIn("CORRUPT_LOCK_METADATA", output)

    def test_05b_stale_dead_pid_writer_lock_blocked(self):
        """Scenario 5B: Stale writer lock held by dead PID is classified as STALE_LOCK_DEAD_PID."""
        lock_dir = self.data_dir / "locks"
        lock_dir.mkdir(parents=True, exist_ok=True)
        lock_file = lock_dir / ".pipeline.lock"

        meta = LockMetadata(
            owner_token="tok_test_dead_456",
            run_id="run_dead_writer",
            pid=99999999,
            hostname="test_host",
            created_at="2026-10-21T00:00:00Z",
        )
        lock_file.write_text(meta.to_json(), encoding="utf-8")

        buf_out = io.StringIO()
        with patch("flight_pipeline.ingestion.coordinator.get_pid_liveness", return_value=PidLivenessStatus.PROCESS_DEAD):
            with redirect_stdout(buf_out):
                code = coordinator_main(
                    argv=[
                        "--years", "2016",
                        "--run-id", "run_synthetic_v1",
                        "--dry-run-preflight",
                        "--base-data-dir", str(self.data_dir),
                    ],
                    approved_baseline_hashes=self.synthetic_approved_hashes,
                    custom_inventory=self.synthetic_inventory,
                )
        output = buf_out.getvalue()
        self.assertEqual(code, 1)
        self.assertIn("STALE_LOCK_DEAD_PID", output)
        self.assertIn("Stale writer lock detected from dead PID", output)
        self.assertNotIn("CORRUPT_LOCK_METADATA", output)

    def test_05c_corrupt_lock_metadata_blocked(self):
        """Scenario 5C: Corrupt lock metadata file is correctly classified as CORRUPT_LOCK_METADATA."""
        lock_dir = self.data_dir / "locks"
        lock_dir.mkdir(parents=True, exist_ok=True)
        lock_file = lock_dir / ".pipeline.lock"
        lock_file.write_text("{this is not valid json content...", encoding="utf-8")

        buf_out = io.StringIO()
        with redirect_stdout(buf_out):
            code = coordinator_main(
                argv=[
                    "--years", "2016",
                    "--run-id", "run_synthetic_v1",
                    "--dry-run-preflight",
                    "--base-data-dir", str(self.data_dir),
                ],
                approved_baseline_hashes=self.synthetic_approved_hashes,
                custom_inventory=self.synthetic_inventory,
            )
        output = buf_out.getvalue()
        self.assertEqual(code, 1)
        self.assertIn("CORRUPT_LOCK_METADATA", output)
        self.assertNotIn("ACTIVE_WRITER_RUNNING", output)
        self.assertNotIn("STALE_LOCK_DEAD_PID", output)

    def test_05d_ambiguous_and_invalid_pid_lock_blocked(self):
        """Scenario 5D: Ambiguous and invalid PID states are classified as AMBIGUOUS_LOCK and INVALID_PID."""
        lock_dir = self.data_dir / "locks"
        lock_dir.mkdir(parents=True, exist_ok=True)
        lock_file = lock_dir / ".pipeline.lock"

        meta = LockMetadata(
            owner_token="tok_test_ambig_789",
            run_id="run_ambig_writer",
            pid=12345,
            hostname="test_host",
            created_at="2026-10-21T00:00:00Z",
        )
        lock_file.write_text(meta.to_json(), encoding="utf-8")

        # Subcase 1: PROCESS_STATUS_UNKNOWN
        buf_out = io.StringIO()
        with patch("flight_pipeline.ingestion.coordinator.get_pid_liveness", return_value=PidLivenessStatus.PROCESS_STATUS_UNKNOWN):
            with redirect_stdout(buf_out):
                code = coordinator_main(
                    argv=[
                        "--years", "2016",
                        "--run-id", "run_synthetic_v1",
                        "--dry-run-preflight",
                        "--base-data-dir", str(self.data_dir),
                    ],
                    approved_baseline_hashes=self.synthetic_approved_hashes,
                    custom_inventory=self.synthetic_inventory,
                )
        output = buf_out.getvalue()
        self.assertEqual(code, 1)
        self.assertIn("AMBIGUOUS_LOCK", output)

        # Subcase 2: INVALID_PID
        buf_out2 = io.StringIO()
        with patch("flight_pipeline.ingestion.coordinator.get_pid_liveness", return_value=PidLivenessStatus.INVALID_PID):
            with redirect_stdout(buf_out2):
                code2 = coordinator_main(
                    argv=[
                        "--years", "2016",
                        "--run-id", "run_synthetic_v1",
                        "--dry-run-preflight",
                        "--base-data-dir", str(self.data_dir),
                    ],
                    approved_baseline_hashes=self.synthetic_approved_hashes,
                    custom_inventory=self.synthetic_inventory,
                )
        output2 = buf_out2.getvalue()
        self.assertEqual(code2, 1)
        self.assertIn("INVALID_PID", output2)

    def test_06_unsafe_pointer_or_recovery_marker_blocked(self):
        """Scenario 6: Unresolved recovery state (.del_*) or dangling pointer blocks preflight."""
        # Subcase 6A: Recovery marker present in locks dir
        lock_dir = self.data_dir / "locks"
        lock_dir.mkdir(parents=True, exist_ok=True)
        recovery_marker = lock_dir / ".recovery_required_run_failed"
        recovery_marker.write_text("recovery needed", encoding="utf-8")

        buf_out = io.StringIO()
        with redirect_stdout(buf_out):
            code = coordinator_main(
                argv=[
                    "--years", "2016",
                    "--run-id", "run_synthetic_v1",
                    "--dry-run-preflight",
                    "--base-data-dir", str(self.data_dir),
                ],
                approved_baseline_hashes=self.synthetic_approved_hashes,
                custom_inventory=self.synthetic_inventory,
            )
        output = buf_out.getvalue()
        self.assertEqual(code, 1)
        self.assertIn("BLOCKED_UNRESOLVED_RECOVERY", output)

        # Cleanup marker and test Subcase 6B: Dangling pointer
        recovery_marker.unlink()
        curated_dir = self.data_dir / "curated"
        curated_dir.mkdir(parents=True, exist_ok=True)
        pointer_file = curated_dir / "latest_run_id.txt"
        pointer_file.write_text("run_non_existent_target\n", encoding="utf-8")

        buf_out2 = io.StringIO()
        with redirect_stdout(buf_out2):
            code = coordinator_main(
                argv=[
                    "--years", "2016",
                    "--run-id", "run_synthetic_v1",
                    "--dry-run-preflight",
                    "--base-data-dir", str(self.data_dir),
                ],
                approved_baseline_hashes=self.synthetic_approved_hashes,
                custom_inventory=self.synthetic_inventory,
            )
        output2 = buf_out2.getvalue()
        self.assertEqual(code, 1)
        self.assertIn("DANGLING_POINTER", output2)

    def test_06b_empty_or_whitespace_pointer_fails_preflight(self):
        """Scenario 6B: Existing empty or whitespace-only pointer causes preflight FAIL and nonzero exit."""
        curated_dir = self.data_dir / "curated"
        curated_dir.mkdir(parents=True, exist_ok=True)
        pointer_file = curated_dir / "latest_run_id.txt"

        # Case 1: Empty string (0 bytes)
        pointer_file.write_text("", encoding="utf-8")
        buf_out = io.StringIO()
        with redirect_stdout(buf_out):
            code = coordinator_main(
                argv=[
                    "--years", "2016",
                    "--run-id", "run_synthetic_v1",
                    "--dry-run-preflight",
                    "--base-data-dir", str(self.data_dir),
                ],
                approved_baseline_hashes=self.synthetic_approved_hashes,
                custom_inventory=self.synthetic_inventory,
            )
        output = buf_out.getvalue()
        self.assertEqual(code, 1)
        self.assertIn("EMPTY_POINTER_FILE", output)
        self.assertIn("Empty or whitespace-only pointer file detected", output)
        self.assertIn("[PREFLIGHT FAIL]", output)

        # Case 2: Whitespace only (spaces, newlines, tabs)
        pointer_file.write_text("   \n\t  \r\n", encoding="utf-8")
        buf_out2 = io.StringIO()
        with redirect_stdout(buf_out2):
            code2 = coordinator_main(
                argv=[
                    "--years", "2016",
                    "--run-id", "run_synthetic_v1",
                    "--dry-run-preflight",
                    "--base-data-dir", str(self.data_dir),
                ],
                approved_baseline_hashes=self.synthetic_approved_hashes,
                custom_inventory=self.synthetic_inventory,
            )
        output2 = buf_out2.getvalue()
        self.assertEqual(code2, 1)
        self.assertIn("EMPTY_POINTER_FILE", output2)
        self.assertIn("Empty or whitespace-only pointer file detected", output2)
        self.assertIn("[PREFLIGHT FAIL]", output2)

    def test_06c_absent_pointer_uninitialized_passes_preflight(self):
        """Scenario 6C: Absent latest_run_id.txt pointer is valid UNINITIALIZED state and passes preflight."""
        curated_dir = self.data_dir / "curated"
        curated_dir.mkdir(parents=True, exist_ok=True)
        pointer_file = curated_dir / "latest_run_id.txt"
        if pointer_file.exists():
            pointer_file.unlink()

        buf_out = io.StringIO()
        with redirect_stdout(buf_out):
            code = coordinator_main(
                argv=[
                    "--years", "2016",
                    "--run-id", "run_synthetic_v1",
                    "--dry-run-preflight",
                    "--base-data-dir", str(self.data_dir),
                ],
                approved_baseline_hashes=self.synthetic_approved_hashes,
                custom_inventory=self.synthetic_inventory,
            )
        output = buf_out.getvalue()
        self.assertEqual(code, 0)
        self.assertIn("UNINITIALIZED", output)
        self.assertIn("[PREFLIGHT PASS]", output)

    def test_06d_path_traversal_pointer_fails_preflight(self):
        """Scenario 6D: Pointer file with path traversal fails preflight with CORRUPT_POINTER."""
        curated_dir = self.data_dir / "curated"
        curated_dir.mkdir(parents=True, exist_ok=True)
        pointer_file = curated_dir / "latest_run_id.txt"
        pointer_file.write_text("../../etc/passwd\n", encoding="utf-8")

        buf_out = io.StringIO()
        with redirect_stdout(buf_out):
            code = coordinator_main(
                argv=[
                    "--years", "2016",
                    "--run-id", "run_synthetic_v1",
                    "--dry-run-preflight",
                    "--base-data-dir", str(self.data_dir),
                ],
                approved_baseline_hashes=self.synthetic_approved_hashes,
                custom_inventory=self.synthetic_inventory,
            )
        output = buf_out.getvalue()
        self.assertEqual(code, 1)
        self.assertIn("CORRUPT_POINTER", output)
        self.assertIn("[PREFLIGHT FAIL]", output)

    def test_07_duplicate_run_id_blocked(self):
        """Scenario 7: Duplicate run_id (already existing curated or staging run) blocks preflight."""
        # Create pre-existing curated run
        existing_run = self.data_dir / "curated" / "runs" / "run_synthetic_v1"
        existing_run.mkdir(parents=True, exist_ok=True)

        code = coordinator_main(
            argv=[
                "--years", "2016",
                "--run-id", "run_synthetic_v1",
                "--dry-run-preflight",
                "--base-data-dir", str(self.data_dir),
            ],
            approved_baseline_hashes=self.synthetic_approved_hashes,
            custom_inventory=self.synthetic_inventory,
        )
        self.assertEqual(code, 1)

    def test_08_invalid_survey_year_or_run_id_blocked(self):
        """Scenario 8: Invalid survey year or directory-traversal run_id blocks preflight."""
        # Invalid year
        code_yr = coordinator_main(
            argv=[
                "--years", "1999",
                "--run-id", "run_synthetic_v1",
                "--dry-run-preflight",
                "--base-data-dir", str(self.data_dir),
            ],
            approved_baseline_hashes=self.synthetic_approved_hashes,
            custom_inventory=self.synthetic_inventory,
        )
        self.assertEqual(code_yr, 1)

        # Path traversal run_id
        code_run = coordinator_main(
            argv=[
                "--years", "2016",
                "--run-id", "../escape_run",
                "--dry-run-preflight",
                "--base-data-dir", str(self.data_dir),
            ],
            approved_baseline_hashes=self.synthetic_approved_hashes,
            custom_inventory=self.synthetic_inventory,
        )
        self.assertEqual(code_run, 1)

    def test_09_unauthorized_live_execution_blocked(self):
        """Scenario 9: Unauthorized live execution without D5 returns 1 under governance hold without writing data."""
        code = coordinator_main(
            argv=[
                "--years", "2016",
                "--run-id", "run_synthetic_v1",
                "--base-data-dir", str(self.data_dir),
            ],
            approved_baseline_hashes=self.synthetic_approved_hashes,
            custom_inventory=self.synthetic_inventory,
        )
        self.assertEqual(code, 1)

        # Verify absolutely no staging or curated outputs were created
        self.assertFalse((self.data_dir / "staging" / "run_synthetic_v1").exists())
        self.assertFalse((self.data_dir / "curated" / "runs" / "run_synthetic_v1").exists())

    def test_10_cli_root_path_resolution_matches_storage_configuration(self):
        """Scenario 10: CLI --base-dir alias and path resolution correctly handles data/ root without data/data/raw."""
        # Both --base-data-dir and --base-dir aliases must work
        code1 = coordinator_main(
            argv=[
                "--years", "2016",
                "--run-id", "run_synthetic_alias1",
                "--dry-run-preflight",
                "--base-data-dir", str(self.data_dir),
            ],
            approved_baseline_hashes=self.synthetic_approved_hashes,
            custom_inventory=self.synthetic_inventory,
        )
        self.assertEqual(code1, 0)

        code2 = coordinator_main(
            argv=[
                "--years", "2016",
                "--run-id", "run_synthetic_alias2",
                "--dry-run-preflight",
                "--base-dir", str(self.data_dir),
            ],
            approved_baseline_hashes=self.synthetic_approved_hashes,
            custom_inventory=self.synthetic_inventory,
        )
        self.assertEqual(code2, 0)

    def test_11_live_ingestion_rejects_allow_candidate_hashes(self):
        """Scenario 11: Live ingestion invocation with --allow-candidate-hashes is strictly blocked under governance hold."""
        code = coordinator_main(
            argv=[
                "--years", "2016",
                "--run-id", "run_synthetic_live_cand",
                "--allow-candidate-hashes",
                "--base-data-dir", str(self.data_dir),
            ],
            approved_baseline_hashes=self.synthetic_approved_hashes,
            custom_inventory=self.synthetic_inventory,
        )
        self.assertEqual(code, 1)
        self.assertFalse((self.data_dir / "staging" / "run_synthetic_live_cand").exists())
        self.assertFalse((self.data_dir / "curated" / "runs" / "run_synthetic_live_cand").exists())

    def test_12_schema_contract_authoritative_fingerprint(self):
        """Scenario 12: Canonical schema factory produces deterministic authoritative fingerprint b5805fca..."""
        from flight_pipeline.ingestion.schema import get_curated_parquet_schema
        schema = get_curated_parquet_schema()
        spark_to_arrow = {"StringType()": "string", "DoubleType()": "double", "LongType()": "int64"}
        canonical_fields = [[f.name, spark_to_arrow[str(f.dataType)]] for f in schema.fields]
        payload = json.dumps(canonical_fields)
        fp = hashlib.sha256(payload.encode("utf-8")).hexdigest()
        self.assertEqual(fp, "b5805fcae8db44e9a53c0eb1dfa1c1f3d9ec2983b3922bfbe5c6454f1654b09a")

    def test_13_all_published_parquet_schema_compatibility(self):
        """Scenario 13: All physical Parquet partition files across 2016-2024 match canonical fingerprint."""
        import pyarrow.parquet as pq
        curated_root = Path("data/curated/runs")
        if not curated_root.exists():
            self.skipTest("Curated runs root not present")
        
        expected_fp = "b5805fcae8db44e9a53c0eb1dfa1c1f3d9ec2983b3922bfbe5c6454f1654b09a"
        checked_count = 0
        for yr in range(2016, 2025):
            yr_dir = curated_root / f"run_{yr}_v1"
            if not yr_dir.is_dir():
                continue
            for pf in yr_dir.glob("*.parquet"):
                checked_count += 1
                arrow_schema = pq.ParquetFile(str(pf)).schema_arrow
                fields = [[f.name, str(f.type)] for f in arrow_schema]
                fp = hashlib.sha256(json.dumps(fields).encode("utf-8")).hexdigest()
                self.assertEqual(fp, expected_fp, f"Fingerprint mismatch in {pf}")

        self.assertGreaterEqual(checked_count, 117, "Expected at least 117 Parquet partition files to be checked")


if __name__ == "__main__":
    unittest.main()
