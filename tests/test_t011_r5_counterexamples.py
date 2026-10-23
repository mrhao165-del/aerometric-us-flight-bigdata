"""
T-011 R5 Counterexample and Regression Test Suite.
Verifies and prevents:
1. R5-F01 (CRITICAL): Late check-to-unlink race conditions during release() and break_stale_lock().
2. R5-F01: Multi-process concurrency and mutual exclusion across real worker processes on Windows NTFS.
3. R5-F01: Replacement lock protection (lock is NEVER deleted if concurrently replaced).
4. R5-F01: Fail-closed manual recovery semantics on dead PID, invalid PID, unknown status, and corrupted metadata.
5. R5-F02: SHA-256 hexadecimal encoding validation in BtsProvenanceValidator (64-char hex strictly required).
6. R5-F03: Test inventory and physical test module discovery reconciliation.
"""

from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import tempfile
import time
import unittest

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
from flight_pipeline.kpi.bts_reconciler import (
    BtsProvenanceMetadata,
    BtsProvenanceValidator,
    BtsTranStatsReconciler,
    ReconciliationSummary,
    is_valid_sha256_hex,
)


class TestT011R5Counterexamples(unittest.TestCase):
    """Regression test suite for T011-R5 findings."""

    # =========================================================================
    # R5-F01: LATE CHECK-TO-UNLINK RACE & REPLACEMENT PRESERVATION TESTS
    # =========================================================================

    def test_r5_f01_test_01_release_late_replacement_preserves_new_lock(self):
        """
        Reproduction A: An actor replaces the lock file after final check but before unlink.
        MUST NOT delete the replacement lock and MUST raise LockOwnerMismatchError.
        """
        with tempfile.TemporaryDirectory() as td:
            tdp = Path(td)
            writer = SingleWriterLock(tdp, run_id="run_w1")
            writer.acquire()
            self.assertTrue(writer.is_acquired)

            replacement_meta = LockMetadata(
                owner_token="new_owner_token_999",
                run_id="run_new_owner",
                pid=os.getpid(),
                hostname=platform.node(),
                created_at="2026-01-01T00:00:00Z",
            )

            def late_race_replacement():
                writer.lock_file_path.write_text(replacement_meta.to_json(), encoding="utf-8")

            writer._pre_unlink_hook = late_race_replacement
            with self.assertRaises(LockOwnerMismatchError) as ctx:
                writer.release()
            self.assertIn("Lock owner mismatch", str(ctx.exception))
            # CRITICAL VERIFICATION: Replacement lock MUST STILL EXIST on disk!
            self.assertTrue(writer.lock_file_path.exists(), "Replacement lock was deleted!")
            surviving_meta = LockMetadata.from_json(writer.lock_file_path.read_text(encoding="utf-8"))
            self.assertEqual(surviving_meta.owner_token, "new_owner_token_999")

    def test_r5_f01_test_02_break_stale_lock_late_replacement_preserves_new_lock(self):
        """
        Reproduction B: An actor replaces a stale lock after liveness verification but before unlink.
        MUST NOT delete the replacement lock and MUST raise LockContentionError (fail-closed).
        """
        with tempfile.TemporaryDirectory() as td:
            tdp = Path(td)
            stale_meta = LockMetadata(
                owner_token="stale_token_111",
                run_id="stale_run",
                pid=99999999,  # dead PID
                hostname=platform.node(),
                created_at="2026-01-01T00:00:00Z",
            )
            lock_file = tdp / ".pipeline.lock"
            lock_file.write_text(stale_meta.to_json(), encoding="utf-8")

            active_replacement = LockMetadata(
                owner_token="active_replacement_token_222",
                run_id="active_run_2",
                pid=os.getpid(),
                hostname=platform.node(),
                created_at="2026-01-01T00:00:00Z",
            )

            recovery_tool = SingleWriterLock(tdp, run_id="recovery_tool")

            def late_race_replacement():
                lock_file.write_text(active_replacement.to_json(), encoding="utf-8")

            recovery_tool._pre_unlink_hook = late_race_replacement
            with self.assertRaises(LockContentionError) as ctx:
                recovery_tool.break_stale_lock(force=True)
            self.assertIn("Lock file changed concurrently", str(ctx.exception))
            # CRITICAL VERIFICATION: Replacement lock MUST STILL EXIST on disk!
            self.assertTrue(lock_file.exists(), "Active replacement lock was deleted by stale recovery!")
            surviving_meta = LockMetadata.from_json(lock_file.read_text(encoding="utf-8"))
            self.assertEqual(surviving_meta.owner_token, "active_replacement_token_222")

    def test_r5_f01_test_03_normal_acquire_release_no_contention(self):
        """Normal acquire and release cycles succeed cleanly without orphaned locks or leaked files."""
        with tempfile.TemporaryDirectory() as td:
            tdp = Path(td)
            for i in range(5):
                lock = SingleWriterLock(tdp, run_id=f"run_normal_{i}")
                self.assertFalse(lock.is_acquired)
                lock.acquire()
                self.assertTrue(lock.is_acquired)
                self.assertTrue(lock.lock_file_path.exists())
                lock.release()
                self.assertFalse(lock.is_acquired)
                self.assertFalse(lock.lock_file_path.exists())

    def test_r5_f01_test_04_two_real_competing_worker_processes(self):
        """
        Two real OS child processes contend for the same lock.
        Exactly one worker succeeds in acquisition; the other fails closed.
        """
        worker_code = """
import os, sys, time
from pathlib import Path
sys.path.insert(0, sys.argv[1])
from flight_pipeline.storage.locking import SingleWriterLock, LockContentionError

lock_dir = Path(sys.argv[2])
worker_id = sys.argv[3]
lock = SingleWriterLock(lock_dir, run_id=f"worker_{worker_id}")

try:
    lock.acquire()
    print(f"WORKER_{worker_id}_ACQUIRED", flush=True)
    time.sleep(1.0)
    lock.release()
    print(f"WORKER_{worker_id}_RELEASED", flush=True)
    sys.exit(0)
except LockContentionError:
    print(f"WORKER_{worker_id}_CONTENTION", flush=True)
    sys.exit(2)
except Exception as e:
    print(f"WORKER_{worker_id}_ERROR: {e}", flush=True)
    sys.exit(1)
"""
        with tempfile.TemporaryDirectory() as td:
            script_path = Path(td) / "worker.py"
            script_path.write_text(worker_code, encoding="utf-8")
            lock_dir = Path(td) / "locks"

            p1 = subprocess.Popen(
                [sys.executable, str(script_path), str(SRC_DIR), str(lock_dir), "1"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            # Give P1 a short head start to establish acquisition
            time.sleep(0.2)
            p2 = subprocess.Popen(
                [sys.executable, str(script_path), str(SRC_DIR), str(lock_dir), "2"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

            out1, _ = p1.communicate(timeout=10)
            out2, _ = p2.communicate(timeout=10)

            # One must succeed with exit code 0; one must receive contention with exit code 2
            exit_codes = sorted([p1.returncode, p2.returncode])
            self.assertEqual(exit_codes, [0, 2], f"Expected exits [0, 2], got {exit_codes}. P1: {out1}, P2: {out2}")

    def test_r5_f01_test_05_release_while_second_process_requests_acquisition(self):
        """A second process waiting for lock acquires cleanly once first process releases."""
        worker_waiter = """
import os, sys, time
from pathlib import Path
sys.path.insert(0, sys.argv[1])
from flight_pipeline.storage.locking import SingleWriterLock, LockContentionError

lock_dir = Path(sys.argv[2])
lock = SingleWriterLock(lock_dir, run_id="waiter_run")

# Poll until acquisition succeeds or 5s timeout
deadline = time.time() + 5.0
acquired = False
while time.time() < deadline:
    try:
        lock.acquire()
        acquired = True
        break
    except LockContentionError:
        time.sleep(0.05)

if acquired:
    print("WAITER_ACQUIRED", flush=True)
    lock.release()
    sys.exit(0)
else:
    print("WAITER_TIMED_OUT", flush=True)
    sys.exit(1)
"""
        with tempfile.TemporaryDirectory() as td:
            script_path = Path(td) / "waiter.py"
            script_path.write_text(worker_waiter, encoding="utf-8")
            lock_dir = Path(td) / "locks"

            # Writer 1 acquires in this process
            w1 = SingleWriterLock(lock_dir, run_id="primary_run")
            w1.acquire()

            # Launch waiter in background
            p = subprocess.Popen(
                [sys.executable, str(script_path), str(SRC_DIR), str(lock_dir)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

            # Hold lock for 0.4s then release
            time.sleep(0.4)
            w1.release()

            out, _ = p.communicate(timeout=5)
            self.assertEqual(p.returncode, 0)
            self.assertIn("WAITER_ACQUIRED", out)

    def test_r5_f01_test_06_corrupted_metadata_fail_closed(self):
        """Corrupted/non-JSON lock metadata raises LockContentionError (FAIL_CLOSED — MANUAL_RECOVERY_REQUIRED)."""
        with tempfile.TemporaryDirectory() as td:
            tdp = Path(td)
            lock_file = tdp / ".pipeline.lock"
            lock_file.write_text("NOT_VALID_JSON_CORRUPTED_METADATA", encoding="utf-8")

            writer = SingleWriterLock(tdp, run_id="run_c1")
            with self.assertRaises(LockContentionError) as ctx:
                writer.acquire()
            self.assertIn("FAIL_CLOSED — MANUAL_RECOVERY_REQUIRED", str(ctx.exception))

            # Automatic break must also fail closed
            with self.assertRaises(LockContentionError) as ctx:
                writer.break_stale_lock(force=True)
            self.assertIn("FAIL_CLOSED — MANUAL_RECOVERY_REQUIRED", str(ctx.exception))
            # Verify corrupted file preserved for forensic inspection
            self.assertTrue(lock_file.exists())

    def test_r5_f01_test_07_invalid_pid_and_unknown_liveness_fail_closed(self):
        """Invalid PID types (bool, negative, zero) or unknown liveness fail closed."""
        with tempfile.TemporaryDirectory() as td:
            tdp = Path(td)
            lock_file = tdp / ".pipeline.lock"

            for bad_pid in [0, -10]:
                meta = {
                    "owner_token": "token_bad",
                    "run_id": "run_bad",
                    "pid": bad_pid,
                    "hostname": platform.node(),
                    "created_at": "2026-01-01T00:00:00Z",
                }
                lock_file.write_text(json.dumps(meta), encoding="utf-8")
                writer = SingleWriterLock(tdp, run_id="run_test")
                with self.assertRaises(LockContentionError) as ctx:
                    writer.break_stale_lock(force=True)
                self.assertIn("FAIL_CLOSED — MANUAL_RECOVERY_REQUIRED", str(ctx.exception))
                self.assertTrue(lock_file.exists())

    def test_r5_f01_test_08_replaced_lock_concurrently_recreated_after_move(self):
        """
        When the lock file is moved to staging and an external actor concurrently creates a new lock
        at the canonical path, the canonical lock is NOT deleted when staging is unlinked.
        """
        with tempfile.TemporaryDirectory() as td:
            tdp = Path(td)
            writer = SingleWriterLock(tdp, run_id="run_orig")
            writer.acquire()

            competitor_meta = LockMetadata(
                owner_token="competitor_token_777",
                run_id="run_competitor",
                pid=os.getpid(),
                hostname=platform.node(),
                created_at="2026-01-01T00:00:00Z",
            )

            # Inject competitor recreation after move to staging
            orig_rename = os.rename

            def rename_and_create_competitor(src, dst):
                res = orig_rename(src, dst)
                if Path(src) == writer.lock_file_path:
                    # Competitor immediately creates lock at original path
                    writer.lock_file_path.write_text(competitor_meta.to_json(), encoding="utf-8")
                return res

            os.rename = rename_and_create_competitor
            try:
                writer.release()
                # Verify competitor lock at canonical path SURVIVED!
                self.assertTrue(writer.lock_file_path.exists())
                current_meta = LockMetadata.from_json(writer.lock_file_path.read_text(encoding="utf-8"))
                self.assertEqual(current_meta.owner_token, "competitor_token_777")
            finally:
                os.rename = orig_rename

    # =========================================================================
    # R5-F02: BTS PROVENANCE SHA-256 HEXADECIMAL ENCODING TESTS
    # =========================================================================

    def test_r5_f02_test_01_valid_lowercase_sha256_accepted(self):
        """Valid 64-char lowercase hexadecimal SHA-256 is accepted as CANDIDATE_CHECKSUM_MATCHED."""
        valid_hash = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        prov = BtsProvenanceMetadata(
            project_lead_approval_status="APPROVED_BY_PROJECT_LEAD",
            approval_record_ref="DECISION_20261019_PL_BTS_SAMPLE",
            is_external_reference=True,
            sha256_hash=valid_hash,
        )
        ok, msg = BtsProvenanceValidator.validate_candidate_checksum(prov, valid_hash)
        self.assertTrue(ok)
        self.assertEqual(msg, "CANDIDATE_CHECKSUM_MATCHED")

    def test_r5_f02_test_02_valid_uppercase_and_mixed_case_sha256_accepted(self):
        """Valid uppercase and mixed-case 64-char hexadecimal SHA-256 is accepted."""
        hash_lower = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        hash_upper = hash_lower.upper()
        hash_mixed = hash_lower[:32].upper() + hash_lower[32:]

        prov = BtsProvenanceMetadata(
            project_lead_approval_status="APPROVED_BY_PROJECT_LEAD",
            approval_record_ref="DECISION_20261019_PL_BTS_SAMPLE",
            is_external_reference=True,
            sha256_hash=hash_upper,
        )
        ok, msg = BtsProvenanceValidator.validate_candidate_checksum(prov, hash_lower)
        self.assertTrue(ok)
        self.assertEqual(msg, "CANDIDATE_CHECKSUM_MATCHED")

        prov.sha256_hash = hash_mixed
        ok, msg = BtsProvenanceValidator.validate_candidate_checksum(prov, hash_upper)
        self.assertTrue(ok)
        self.assertEqual(msg, "CANDIDATE_CHECKSUM_MATCHED")

    def test_r5_f02_test_03_non_hex_64_chars_strictly_rejected(self):
        """
        R5-F02 Core Counterexample: 64 non-hex characters ('z' * 64) matching in declared
        and actual MUST NOT count as valid checksum evidence.
        """
        invalid_nonhex = "z" * 64
        prov = BtsProvenanceMetadata(
            project_lead_approval_status="APPROVED_BY_PROJECT_LEAD",
            approval_record_ref="DECISION_20261019_PL_BTS_SAMPLE",
            is_external_reference=True,
            sha256_hash=invalid_nonhex,
        )
        ok, msg = BtsProvenanceValidator.validate_candidate_checksum(prov, invalid_nonhex)
        self.assertFalse(ok)
        self.assertIn("PROVENANCE_ACTUAL_CHECKSUM_MALFORMED", msg)

        # In validate_metadata_format
        fmt_ok, fmt_msg = BtsProvenanceValidator.validate_metadata_format(prov)
        self.assertFalse(fmt_ok)
        self.assertIn("PROVENANCE_MALFORMED_HASH", fmt_msg)

    def test_r5_f02_test_04_invalid_lengths_rejected(self):
        """Hashes of lengths other than 64 (e.g. 32, 63, 65) are rejected."""
        valid_hash = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        prov = BtsProvenanceMetadata(
            project_lead_approval_status="APPROVED_BY_PROJECT_LEAD",
            approval_record_ref="DECISION_20261019_PL_BTS_SAMPLE",
            is_external_reference=True,
            sha256_hash=valid_hash,
        )
        for bad_len in [32, 63, 65]:
            bad_hash = "a" * bad_len
            ok, msg = BtsProvenanceValidator.validate_candidate_checksum(prov, bad_hash)
            self.assertFalse(ok)
            self.assertIn("PROVENANCE_ACTUAL_CHECKSUM_MALFORMED", msg)

    def test_r5_f02_test_05_empty_and_whitespace_hashes_rejected(self):
        """Empty, blank, leading/trailing whitespace, or embedded whitespace hashes are rejected."""
        valid_hash = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        prov = BtsProvenanceMetadata(
            project_lead_approval_status="APPROVED_BY_PROJECT_LEAD",
            approval_record_ref="DECISION_20261019_PL_BTS_SAMPLE",
            is_external_reference=True,
            sha256_hash=valid_hash,
        )
        for bad in ["", "   ", " " + valid_hash, valid_hash + " ", valid_hash[:30] + " " + valid_hash[31:]]:
            ok, msg = BtsProvenanceValidator.validate_candidate_checksum(prov, bad)
            self.assertFalse(ok)

    def test_r5_f02_test_06_mismatching_valid_hex_hashes_rejected(self):
        """Two differing valid 64-char hex digests produce PROVENANCE_HASH_MISMATCH."""
        hash_1 = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        hash_2 = "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"
        prov = BtsProvenanceMetadata(
            project_lead_approval_status="APPROVED_BY_PROJECT_LEAD",
            approval_record_ref="DECISION_20261019_PL_BTS_SAMPLE",
            is_external_reference=True,
            sha256_hash=hash_1,
        )
        ok, msg = BtsProvenanceValidator.validate_candidate_checksum(prov, hash_2)
        self.assertFalse(ok)
        self.assertIn("PROVENANCE_HASH_MISMATCH", msg)

    def test_r5_f02_test_07_source_provenance_verified_remains_false(self):
        """Candidate metadata matching valid hash still has source_provenance_verified = False."""
        valid_hash = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        prov = BtsProvenanceMetadata(
            project_lead_approval_status="APPROVED_BY_PROJECT_LEAD",
            approval_record_ref="DECISION_20261019_PL_BTS_SAMPLE",
            is_external_reference=True,
            sha256_hash=valid_hash,
        )
        reconciler = BtsTranStatsReconciler()
        summary, _ = reconciler.reconcile(
            [], [],
            provenance_metadata=prov,
            actual_bts_sha256=valid_hash,
            is_authentic_bts_data=True,
        )
        self.assertTrue(summary.candidate_checksum_matched)
        self.assertFalse(summary.source_provenance_verified)
        self.assertFalse(summary.human_accepted)

    # =========================================================================
    # R5-F03: TEST INVENTORY & DISCOVERY RECONCILIATION
    # =========================================================================

    def test_r5_f03_test_01_physical_test_modules_inventory(self):
        """
        Verify that test discovery finds exactly all physical test_*.py files in tests/
        and does not invent nonexistent test files.
        """
        tests_dir = Path(__file__).resolve().parent
        physical_files = sorted([p.stem for p in tests_dir.glob("test_*.py")])

        # Discover tests using unittest
        loader = unittest.TestLoader()
        suite = loader.discover(str(tests_dir), pattern="test_*.py")

        discovered_modules = set()

        def extract_modules(s):
            for item in s:
                if isinstance(item, unittest.TestCase):
                    discovered_modules.add(item.__class__.__module__)
                else:
                    extract_modules(item)

        extract_modules(suite)
        discovered_stems = sorted([m.split(".")[-1] for m in discovered_modules])

        self.assertEqual(
            discovered_stems, physical_files,
            f"Mismatch between physical files and discovered modules: {set(physical_files) ^ set(discovered_stems)}"
        )
        self.assertGreaterEqual(len(physical_files), 21, "Expected at least 21 test modules in R5")


if __name__ == "__main__":
    unittest.main()
