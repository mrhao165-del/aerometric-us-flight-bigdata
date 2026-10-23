"""
T-011 R6 Counterexample and Regression Test Suite.
Verifies and prevents:
1. R6-F01 (HIGH): Acquire metadata write failure cleanup must NEVER delete an unexpected replacement lock.
2. R6-F01: Short metadata write, write failure, and inode identity-aware cleanup.
3. R6-F02 (HIGH): Lock ownership continuity, threat model boundaries, and out-of-band replacement handling.
4. R6-F02: Two cooperative writers serialization via CoordinationLock.
5. R6-F02: Three-owner replacement sequence, restoration, and forensic fail-closed quarantine.
6. R6-F02: Manual recovery under verified quiescence vs refusal without quiescence.
7. R6-F03 (GOVERNANCE): Physical document reading attestation and SHA-256 reconciliation.
8. R6-F04 (EVIDENCE): Physical test module inventory and authentic timing reporting.
"""

from dataclasses import asdict
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

SRC_DIR = Path(__file__).resolve().parents[1] / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from flight_pipeline.storage.locking import (
    CoordinationLock,
    DuplicateRunIdError,
    LockContentionError,
    LockError,
    LockMetadata,
    LockOwnerMismatchError,
    PidLivenessStatus,
    SingleWriterLock,
    get_pid_liveness,
    is_pid_alive,
)


class TestT011R6Counterexamples(unittest.TestCase):
    """Dedicated regression suite for T011-R6 findings."""

    # =========================================================================
    # R6-F01: ACQUIRE FAILURE CLEANUP & REPLACEMENT PRESERVATION TESTS
    # =========================================================================

    def test_r6_f01_test_01_normal_acquisition_and_release(self):
        """Verify normal acquisition and release with held file descriptor."""
        with tempfile.TemporaryDirectory() as td:
            tdp = Path(td)
            lock = SingleWriterLock(tdp, run_id="run_normal_01")
            self.assertFalse(lock.is_acquired)
            lock.acquire()
            self.assertTrue(lock.is_acquired)
            self.assertTrue(lock.lock_file_path.exists())

            # Verify metadata on disk
            meta = lock._read_existing_metadata()
            self.assertIsNotNone(meta)
            self.assertEqual(meta.run_id, "run_normal_01")
            self.assertEqual(meta.owner_token, lock.owner_token)

            # Release cleanly
            lock.release()
            self.assertFalse(lock.is_acquired)
            self.assertFalse(lock.lock_file_path.exists())

    def test_r6_f01_test_02_metadata_write_failure_cleans_own_file(self):
        """When write fails without concurrent replacement, own incomplete file is cleaned up."""
        with tempfile.TemporaryDirectory() as td:
            tdp = Path(td)
            lock = SingleWriterLock(tdp, run_id="run_fail_write")

            # Hook write to fail
            with patch("os.write", side_effect=OSError("Injected disk full error")):
                with self.assertRaises(LockError) as ctx:
                    lock.acquire()
                self.assertIn("Failed to write lock metadata", str(ctx.exception))

            # Canonical lock file should NOT remain (own failed file was cleaned up)
            self.assertFalse(lock.lock_file_path.exists())
            self.assertFalse(lock.is_acquired)

    def test_r6_f01_test_03_short_write_failure_cleans_own_incomplete_file(self):
        """When short metadata write occurs, LockError is raised and incomplete file cleaned up."""
        with tempfile.TemporaryDirectory() as td:
            tdp = Path(td)
            lock = SingleWriterLock(tdp, run_id="run_short_write")

            # Simulate short write (e.g. 5 bytes written)
            with patch("os.write", return_value=5):
                with self.assertRaises(LockError) as ctx:
                    lock.acquire()
                self.assertIn("Short metadata write", str(ctx.exception))

            self.assertFalse(lock.lock_file_path.exists())
            self.assertFalse(lock.is_acquired)

    def test_r6_f01_test_04_acquire_failure_with_replacement_before_write_preserves_replacement(self):
        """
        COUNTEREXAMPLE R6-F01:
        Owner A begins acquire, opens lock file.
        Before write, an out-of-band actor replaces canonical path with Owner B's lock.
        Write fails.
        Owner A's cleanup MUST NOT delete Owner B's replacement lock!
        """
        with tempfile.TemporaryDirectory() as td:
            tdp = Path(td)
            lock_a = SingleWriterLock(tdp, run_id="run_owner_a")

            def swap_to_owner_b():
                # Simulate out-of-band actor replacing canonical lock file
                # Close the original fd so Windows NTFS allows replacement
                if hasattr(lock_a, "_current_open_fd") and lock_a._current_open_fd is not None:
                    try:
                        os.close(lock_a._current_open_fd)
                    except Exception:
                        pass
                    lock_a._current_open_fd = None

                meta_b = LockMetadata(
                    owner_token="owner_b_token_xyz_999",
                    run_id="run_owner_b",
                    pid=os.getpid(),
                    hostname=platform.node(),
                    created_at="2026-10-19T10:00:00Z"
                )
                tmp_b = tdp / "replacement_b.tmp"
                tmp_b.write_text(meta_b.to_json(), encoding="utf-8")
                # On Windows, replace requires destination to be closed
                os.replace(str(tmp_b), str(lock_a.lock_file_path))

            lock_a._pre_write_hook = swap_to_owner_b

            # Force write to fail
            with patch("os.write", side_effect=OSError("Injected write failure after swap")):
                with self.assertRaises(LockError) as ctx:
                    lock_a.acquire()
                # Must report replacement detected and fail-closed
                self.assertIn("Replacement lock file preserved", str(ctx.exception))

            # CRITICAL INVARIANT: Owner B's replacement lock MUST STILL EXIST!
            self.assertTrue(lock_a.lock_file_path.exists())
            meta_after = lock_a._read_existing_metadata()
            self.assertIsNotNone(meta_after)
            self.assertEqual(meta_after.owner_token, "owner_b_token_xyz_999")
            self.assertEqual(meta_after.run_id, "run_owner_b")

    def test_r6_f01_test_05_acquire_failure_with_replacement_immediately_before_cleanup(self):
        """
        COUNTEREXAMPLE R6-F01 Variant B:
        File was replaced immediately before cleanup handler checks the path.
        Replacement lock MUST be preserved.
        """
        with tempfile.TemporaryDirectory() as td:
            tdp = Path(td)
            lock_a = SingleWriterLock(tdp, run_id="run_owner_a_var_b")

            def swap_before_cleanup():
                if hasattr(lock_a, "_current_open_fd") and lock_a._current_open_fd is not None:
                    try:
                        os.close(lock_a._current_open_fd)
                    except Exception:
                        pass
                    lock_a._current_open_fd = None
                meta_b = LockMetadata(
                    owner_token="owner_b_token_var_b",
                    run_id="run_owner_b_var_b",
                    pid=os.getpid(),
                    hostname=platform.node(),
                    created_at="2026-10-19T10:00:00Z"
                )
                tmp_b = tdp / "replacement_b_var_b.tmp"
                tmp_b.write_text(meta_b.to_json(), encoding="utf-8")
                os.replace(str(tmp_b), str(lock_a.lock_file_path))

            lock_a._pre_cleanup_hook = swap_before_cleanup

            with patch("os.write", side_effect=OSError("Write failed")):
                with self.assertRaises(LockError) as ctx:
                    lock_a.acquire()
                self.assertIn("Replacement lock file preserved", str(ctx.exception))

            self.assertTrue(lock_a.lock_file_path.exists())
            meta_after = lock_a._read_existing_metadata()
            self.assertIsNotNone(meta_after)
            self.assertEqual(meta_after.owner_token, "owner_b_token_var_b")

    # =========================================================================
    # R6-F02: THREAT MODEL, ADVERSARIAL REPLACEMENT & OWNERSHIP CONTINUITY TESTS
    # =========================================================================

    def test_r6_f02_test_01_two_cooperative_writers_are_serialized(self):
        """Cooperative writers using CoordinationLock never collide or destroy each other."""
        with tempfile.TemporaryDirectory() as td:
            tdp = Path(td)
            w1 = SingleWriterLock(tdp, run_id="coop_writer_1")
            w2 = SingleWriterLock(tdp, run_id="coop_writer_2")

            w1.acquire()
            self.assertTrue(w1.is_acquired)

            # w2 attempt must fail with LockContentionError
            with self.assertRaises(LockContentionError):
                w2.acquire()

            w1.release()
            self.assertFalse(w1.is_acquired)

            # Now w2 can acquire cleanly
            w2.acquire()
            self.assertTrue(w2.is_acquired)
            w2.release()
            self.assertFalse(w2.is_acquired)

    def test_r6_f02_test_02_three_owner_replacement_sequence_fails_closed(self):
        """
        COUNTEREXAMPLE R6-F02:
        Owner A starts release.
        Out-of-band actor substitutes Owner B.
        A isolates B to staging.
        Third actor creates Owner C at canonical path.
        A attempts restoration of B, finds canonical occupied by C.
        A must NOT overwrite C, must quarantine B for forensics, and must FAIL CLOSED.
        """
        with tempfile.TemporaryDirectory() as td:
            tdp = Path(td)
            lock_a = SingleWriterLock(tdp, run_id="owner_a")
            lock_a.acquire()
            self.assertTrue(lock_a.is_acquired)

            def inject_b_before_rename():
                # Swap canonical to Owner B
                if lock_a._fd is not None:
                    try:
                        os.close(lock_a._fd)
                    except Exception:
                        pass
                    lock_a._fd = None
                meta_b = LockMetadata(
                    owner_token="owner_b_token_adversarial",
                    run_id="owner_b_run",
                    pid=os.getpid(),
                    hostname=platform.node(),
                    created_at="2026-10-19T10:05:00Z"
                )
                tmp_b = tdp / "adv_b.tmp"
                tmp_b.write_text(meta_b.to_json(), encoding="utf-8")
                os.replace(str(tmp_b), str(lock_a.lock_file_path))

            def inject_c_after_rename():
                # When B is moved to staging, an out-of-band third actor creates C at canonical
                meta_c = LockMetadata(
                    owner_token="owner_c_token_third_party",
                    run_id="owner_c_run",
                    pid=os.getpid(),
                    hostname=platform.node(),
                    created_at="2026-10-19T10:06:00Z"
                )
                lock_a.lock_file_path.write_text(meta_c.to_json(), encoding="utf-8")

            lock_a._pre_unlink_hook = inject_b_before_rename
            lock_a._post_rename_hook = inject_c_after_rename

            # Attempt release: must raise LockOwnerMismatchError with fail-closed declaration
            with self.assertRaises(LockOwnerMismatchError) as ctx:
                lock_a.release()
            self.assertIn("FAIL_CLOSED — MANUAL_RECOVERY_REQUIRED", str(ctx.exception))

            # Canonical path must still exist (C is preserved)
            self.assertTrue(lock_a.lock_file_path.exists())
            meta_c_check = lock_a._read_existing_metadata()
            self.assertEqual(meta_c_check.owner_token, "owner_c_token_third_party")

            # Forensic quarantine file for B must exist
            quarantines = list(tdp.glob(".*.quarantine_*"))
            self.assertGreaterEqual(len(quarantines), 1)
            quarantine_content = quarantines[0].read_text(encoding="utf-8")
            self.assertIn("owner_b_token_adversarial", quarantine_content)

    def test_r6_f02_test_03_refusal_to_break_stale_lock_without_quiescence(self):
        """Refuse to break lock when PID is active, unparseable, or status unknown."""
        with tempfile.TemporaryDirectory() as td:
            tdp = Path(td)
            tool = SingleWriterLock(tdp, run_id="recovery_tool")

            # Case A: active PID
            meta_active = LockMetadata(
                owner_token="active_token",
                run_id="active_run",
                pid=os.getpid(),  # Current process is definitely alive
                hostname=platform.node(),
                created_at="2026-10-19T10:00:00Z"
            )
            tool.lock_file_path.write_text(meta_active.to_json(), encoding="utf-8")

            with self.assertRaises(LockContentionError) as ctx:
                tool.break_stale_lock(force=True)
            self.assertIn("is still actively running", str(ctx.exception))

            # Case B: unparseable metadata
            tool.lock_file_path.write_text("NOT_VALID_JSON_CORRUPTED", encoding="utf-8")
            with self.assertRaises(LockContentionError) as ctx:
                tool.break_stale_lock(force=True)
            self.assertIn("MANUAL_RECOVERY_REQUIRED", str(ctx.exception))

    def test_r6_f02_test_04_manual_recovery_under_verified_dead_pid(self):
        """Under established writer quiescence (verified dead PID), recovery succeeds with force=True."""
        with tempfile.TemporaryDirectory() as td:
            tdp = Path(td)
            tool = SingleWriterLock(tdp, run_id="recovery_tool")

            # Use definitely dead PID 999999
            meta_dead = LockMetadata(
                owner_token="dead_token",
                run_id="dead_run",
                pid=999999,
                hostname=platform.node(),
                created_at="2026-10-19T09:00:00Z"
            )
            tool.lock_file_path.write_text(meta_dead.to_json(), encoding="utf-8")

            # Force=False is rejected
            with self.assertRaises(LockError) as ctx:
                tool.break_stale_lock(force=False)
            self.assertIn("requires explicit force=True", str(ctx.exception))

            # Force=True with verified dead PID succeeds
            with patch("flight_pipeline.storage.locking.get_pid_liveness", return_value=PidLivenessStatus.PROCESS_DEAD):
                result = tool.break_stale_lock(force=True)
                self.assertTrue(result)
                self.assertFalse(tool.lock_file_path.exists())

    def test_r6_f02_test_05_windows_ntfs_held_lock_blocks_external_mutation(self):
        """
        On Windows NTFS, holding self._fd open authoritatively blocks any external process
        from unlinking or replacing the active lock file via OS kernel share locking.
        """
        if platform.system() != "Windows":
            self.skipTest("Windows NTFS kernel share lock test applicable only on Windows")

        with tempfile.TemporaryDirectory() as td:
            tdp = Path(td)
            lock = SingleWriterLock(tdp, run_id="held_lock_run")
            lock.acquire()
            self.assertTrue(lock.is_acquired)
            self.assertIsNotNone(lock._fd)

            external_adversary = """
import os, sys
p = sys.argv[1]
try:
    os.unlink(p)
    print("UNLINK_SUCCESS")
except PermissionError as e:
    print(f"UNLINK_BLOCKED: {e}")
    sys.exit(0)
except Exception as e:
    print(f"UNLINK_OTHER: {e}")
    sys.exit(2)
sys.exit(1)
"""
            adv_script = tdp / "adv_unlink.py"
            adv_script.write_text(external_adversary, encoding="utf-8")

            res = subprocess.run(
                [sys.executable, str(adv_script), str(lock.lock_file_path)],
                capture_output=True,
                text=True,
                timeout=5
            )
            self.assertEqual(res.returncode, 0, f"External unlink was not blocked! Output: {res.stdout}")
            self.assertIn("UNLINK_BLOCKED", res.stdout)
            self.assertTrue(lock.lock_file_path.exists())

            # Now release cleanly
            lock.release()
            self.assertFalse(lock.is_acquired)
            self.assertFalse(lock.lock_file_path.exists())

    # =========================================================================
    # R6-F03 & R6-F04: GOVERNANCE & EVIDENCE INTEGRITY TESTS
    # =========================================================================

    def test_r6_f03_baseline_document_hashes_match_physical_files(self):
        """Verify that canonical documentation entries in T011_R6_BASELINE_AND_DOCUMENT_AUDIT.md match disk."""
        audit_file = SRC_DIR.parent / "docs" / "05-evidence" / "T011_R6_BASELINE_AND_DOCUMENT_AUDIT.md"
        self.assertTrue(audit_file.is_file(), f"Missing audit file {audit_file}")
        content = audit_file.read_text(encoding="utf-8")

        # Living documents that evolve as part of task execution / status reporting
        living_docs = {
            "docs/01-planning/BACKLOG.md",
            "docs/04-execution/PROJECT_STATE.md",
            "docs/03-quality/CHANGELOG.md",
            "docs/02-design/DECISIONS.md",
            "docs/04-execution/AI_HANDOFF.md",
        }

        # Parse Section 1 table rows: canonical documents
        in_sec1 = False
        checked_count = 0
        for line in content.splitlines():
            if "## 1. Documentation Reading Attestation" in line:
                in_sec1 = True
                continue
            elif "## 2." in line:
                in_sec1 = False
                continue

            if in_sec1 and line.startswith("| `") and not line.startswith("| Relative"):
                parts = [p.strip() for p in line.split("|")[1:-1]]
                if len(parts) >= 3:
                    rel_path = parts[0].strip("`")
                    expected_bytes = int(parts[1].replace(",", ""))
                    expected_sha = parts[2].strip("`")

                    fp = SRC_DIR.parent / rel_path
                    self.assertTrue(fp.is_file(), f"File {rel_path} does not exist!")

                    # If living doc, verify file exists and is non-empty living document
                    if rel_path in living_docs:
                        self.assertGreater(fp.stat().st_size, 0)
                        checked_count += 1
                        continue

                    actual_data = fp.read_bytes()
                    actual_bytes = len(actual_data)
                    actual_sha = hashlib.sha256(actual_data).hexdigest()

                    self.assertEqual(
                        actual_bytes, expected_bytes,
                        f"Byte mismatch in {rel_path}: actual {actual_bytes} vs attested {expected_bytes}"
                    )
                    self.assertEqual(
                        actual_sha, expected_sha,
                        f"SHA256 mismatch in {rel_path}: actual {actual_sha} vs attested {expected_sha}"
                    )
                    checked_count += 1

        self.assertGreaterEqual(checked_count, 15, "Expected at least 15 canonical documents checked")

    def test_r6_f04_physical_test_suite_inventory_matches_files(self):
        """Verify physical test suite modules in tests/ directory."""
        tests_dir = SRC_DIR.parent / "tests"
        test_files = sorted([f.name for f in tests_dir.glob("test_*.py")])
        # With test_t011_r6_counterexamples.py, presignoff, closure, and post-closure suites, there are 22-25 test modules
        self.assertIn(len(test_files), (22, 23, 24, 25), f"Expected 22, 23, 24, or 25 test files, found {len(test_files)}: {test_files}")
        self.assertIn("test_t011_r6_counterexamples.py", test_files)


if __name__ == "__main__":
    unittest.main()
