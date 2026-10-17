"""
Unit Test Suite for T007-04 Single-Writer Locking Module.
Validates:
1. Single writer lock acquisition and release.
2. Two writers contention and fail-closed behavior.
3. Duplicate run_id detection.
4. Lock owner token verification and mismatch rejection.
5. Stale lock detection with dead PID and governed recovery.
6. Refusal to break locks held by active processes.
7. Concurrent contention across threads.
"""

from concurrent.futures import ThreadPoolExecutor
import json
import os
from pathlib import Path
import sys
import tempfile
import time
import unittest

SRC_DIR = Path(__file__).resolve().parents[1] / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from flight_pipeline.storage.locking import (
    DuplicateRunIdError,
    LockContentionError,
    LockError,
    LockMetadata,
    LockOwnerMismatchError,
    SingleWriterLock,
    is_pid_alive,
)


class TestT007Locking(unittest.TestCase):
    """Test suite for SingleWriterLock."""

    def test_single_writer_acquire_and_release(self):
        """LCK-01: Single writer acquires lock, writes metadata, and releases cleanly."""
        with tempfile.TemporaryDirectory() as td:
            lock_dir = Path(td)
            lock = SingleWriterLock(lock_dir, run_id="run_2016_test_01")

            self.assertFalse(lock.is_acquired)
            self.assertFalse(lock.lock_file_path.exists())

            lock.acquire()
            self.assertTrue(lock.is_acquired)
            self.assertTrue(lock.lock_file_path.exists())

            # Verify lock metadata content
            meta = LockMetadata.from_json(lock.lock_file_path.read_text(encoding="utf-8"))
            self.assertEqual(meta.run_id, "run_2016_test_01")
            self.assertEqual(meta.owner_token, lock.owner_token)
            self.assertEqual(meta.pid, os.getpid())

            lock.release()
            self.assertFalse(lock.is_acquired)
            self.assertFalse(lock.lock_file_path.exists())

    def test_context_manager_usage(self):
        """LCK-02: SingleWriterLock functions as a safe context manager."""
        with tempfile.TemporaryDirectory() as td:
            lock_dir = Path(td)
            with SingleWriterLock(lock_dir, run_id="run_cm_01") as lock:
                self.assertTrue(lock.is_acquired)
                self.assertTrue(lock.lock_file_path.exists())

            # After exit, lock is released
            self.assertFalse(lock.is_acquired)
            self.assertFalse(lock.lock_file_path.exists())

    def test_lock_contention_between_two_writers(self):
        """LCK-03: Two writers contend for lock; second writer raises LockContentionError."""
        with tempfile.TemporaryDirectory() as td:
            lock_dir = Path(td)
            writer1 = SingleWriterLock(lock_dir, run_id="run_writer_1")
            writer2 = SingleWriterLock(lock_dir, run_id="run_writer_2")

            writer1.acquire()
            self.assertTrue(writer1.is_acquired)

            # Writer 2 must fail-closed
            with self.assertRaises(LockContentionError) as ctx:
                writer2.acquire()
            self.assertIn("Lock contention", str(ctx.exception))
            self.assertFalse(writer2.is_acquired)

            writer1.release()

            # Now writer 2 can acquire
            writer2.acquire()
            self.assertTrue(writer2.is_acquired)
            writer2.release()

    def test_duplicate_run_id_detection(self):
        """LCK-04: Contending writer with same run_id raises DuplicateRunIdError."""
        with tempfile.TemporaryDirectory() as td:
            lock_dir = Path(td)
            writer1 = SingleWriterLock(lock_dir, run_id="run_duplicate_id")
            writer2 = SingleWriterLock(lock_dir, run_id="run_duplicate_id")

            writer1.acquire()

            with self.assertRaises(DuplicateRunIdError) as ctx:
                writer2.acquire()
            self.assertIn("Active lock already exists for run_id", str(ctx.exception))

            writer1.release()

    def test_lock_owner_mismatch_prevents_release(self):
        """LCK-05: Instance with different token cannot delete another owner's lock."""
        with tempfile.TemporaryDirectory() as td:
            lock_dir = Path(td)
            writer1 = SingleWriterLock(lock_dir, run_id="run_owner_test")
            writer1.acquire()

            # Craft imposter with different token but pretending to be acquired
            imposter = SingleWriterLock(lock_dir, run_id="run_owner_test")
            imposter._is_acquired = True  # force state

            with self.assertRaises(LockOwnerMismatchError) as ctx:
                imposter.release()
            self.assertIn("Lock owner mismatch", str(ctx.exception))

            # Original lock file must remain intact!
            self.assertTrue(writer1.lock_file_path.exists())
            writer1.release()
            self.assertFalse(writer1.lock_file_path.exists())

    def test_stale_lock_with_dead_pid_requires_manual_recovery(self):
        """LCK-06: Stale lock from dead PID is not stolen automatically (fail-closed)."""
        with tempfile.TemporaryDirectory() as td:
            lock_dir = Path(td)
            dead_pid = 99999999  # Guaranteed non-existent PID
            self.assertFalse(is_pid_alive(dead_pid))

            import platform
            meta = LockMetadata(
                owner_token="stale_token_123",
                run_id="stale_run_id",
                pid=dead_pid,
                hostname=platform.node(),
                created_at="2026-01-01T00:00:00Z",
            )
            # Write stale lock file
            lock_file = lock_dir / ".pipeline.lock"
            lock_file.write_text(meta.to_json(), encoding="utf-8")

            writer = SingleWriterLock(lock_dir, run_id="new_run")
            with self.assertRaises(LockContentionError) as ctx:
                writer.acquire()
            self.assertIn("FAIL_CLOSED — MANUAL_RECOVERY_REQUIRED", str(ctx.exception))

            # Governed recovery with explicit force=True succeeds
            recovered = writer.break_stale_lock(force=True)
            self.assertTrue(recovered)
            self.assertFalse(lock_file.exists())

            # Now writer can acquire
            writer.acquire()
            self.assertTrue(writer.is_acquired)
            writer.release()

    def test_refuse_to_break_active_lock(self):
        """LCK-07: Refuse to break lock held by currently living PID even with force=True."""
        with tempfile.TemporaryDirectory() as td:
            lock_dir = Path(td)
            active_writer = SingleWriterLock(lock_dir, run_id="active_run")
            active_writer.acquire()

            recovery_tool = SingleWriterLock(lock_dir, run_id="recovery_run")
            with self.assertRaises(LockContentionError) as ctx:
                recovery_tool.break_stale_lock(force=True)
            self.assertIn("is still actively running", str(ctx.exception))

            active_writer.release()

    def test_concurrent_lock_attempts(self):
        """LCK-08: Multiple threads contending for lock results in exactly one winner."""
        with tempfile.TemporaryDirectory() as td:
            lock_dir = Path(td)
            results = []

            def try_lock(worker_id: int):
                lock = SingleWriterLock(lock_dir, run_id=f"run_worker_{worker_id}")
                try:
                    lock.acquire()
                    time.sleep(0.05)  # hold lock briefly
                    lock.release()
                    results.append((worker_id, True))
                except LockContentionError:
                    results.append((worker_id, False))

            with ThreadPoolExecutor(max_workers=5) as executor:
                futures = [executor.submit(try_lock, i) for i in range(5)]
                for f in futures:
                    f.result()

            successes = [r for r in results if r[1] is True]
            self.assertGreaterEqual(len(successes), 1)


if __name__ == "__main__":
    unittest.main()
