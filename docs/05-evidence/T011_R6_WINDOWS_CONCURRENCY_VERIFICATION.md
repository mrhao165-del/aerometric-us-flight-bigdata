# T011-R6 Windows Concurrency & Adversarial Process Verification

**Project:** US Flight Performance Analysis 2016–2024  
**Task:** T-011 R6 — Controlled Final Lock Safety Closure  
**Host Platform:** Windows 10 Pro (64-bit AMD64), NTFS Filesystem  
**Parent Gate:** G5 — `IN_PROGRESS`  
**Status:** PASS (0 FAIL)  

---

## 1. Scope & Verification Objective

This document records the empirical verification of multi-process concurrency, mutual exclusion, and adversarial out-of-band interference resilience on Windows NTFS:
1. **OS Kernel Byte Locking (`CoordinationLock`):** Verifies that `msvcrt.locking(msvcrt.LK_LOCK)` serializes concurrent processes competing for `.pipeline.lock.coord`.
2. **Mutual Exclusion Across Real OS Processes:** Verifies that when two distinct Python processes contend for `SingleWriterLock`, exactly one process succeeds and the other receives `LockContentionError` (exit code 2).
3. **OS-Authoritative Held Lock:** Verifies that while `SingleWriterLock` is acquired on Windows NTFS, holding `self._fd` open physically blocks external out-of-band processes from unlinking or replacing the active lock file (`PermissionError: [WinError 32] / [WinError 5]`).
4. **Clean Release & Handoff:** Verifies that a waiting background worker process successfully acquires the lock once the primary process executes `release()`.

---

## 2. Test Execution & Observed Results

The test suite executed is part of `tests/test_t011_r6_counterexamples.py` and `tests/test_t011_r5_counterexamples.py`:

```
================================================================================
TEST EXECUTION MATRIX: WINDOWS NTFS CONCURRENCY & ADVERSARIAL MUTATION
================================================================================
1. test_r6_f02_test_01_two_cooperative_writers_are_serialized:
   - Action: W1 acquires lock; W2 attempts acquisition concurrently.
   - Outcome: W2 immediately raises LockContentionError. W1 releases. W2 acquires cleanly.
   - Verdict: PASS

2. test_r6_f02_test_05_windows_ntfs_held_lock_blocks_external_mutation:
   - Action: Primary process acquires lock, holding OS file descriptor.
   - Adversary: Spawns external Python child process attempting os.unlink(lock_path).
   - Outcome: External process blocked by Windows OS kernel (PermissionError: WinError 32). Lock file preserved intact.
   - Verdict: PASS

3. test_r5_f01_test_04_two_real_competing_worker_processes:
   - Action: Spawns two independent OS child processes with P1 given 0.2s head start.
   - Outcome: P1 exits 0 (ACQUIRED -> RELEASED); P2 exits 2 (CONTENTION).
   - Exit codes verified: [0, 2].
   - Verdict: PASS

4. test_r5_f01_test_05_release_while_second_process_requests_acquisition:
   - Action: Primary holds lock for 0.4s while background worker polls.
   - Outcome: Background worker detects busy state, waits, acquires immediately upon release.
   - Verdict: PASS
================================================================================
VERIFICATION SUMMARY: 4/4 CONCURRENCY TESTS PASS (0 FAIL)
================================================================================
```

---

## 3. Platform Specifics & NTFS Invariants

1. **Share Mode Invariant:** Under Windows NTFS, `os.open(..., O_CREAT | O_EXCL | O_RDWR)` creates a file handle with exclusive write/delete access. Any attempt by another process to delete or overwrite the file fails with `WinError 32` ("The process cannot access the file because it is being used by another process") or `WinError 5` ("Access is denied").
2. **Crash Resilience:** If a process crashes or is killed by the OS, the Windows kernel automatically closes all open file handles, releasing kernel locks and permitting governed operator recovery.
3. **No Unsafe Stealing:** Active process PIDs are never stolen. If a PID is dead, recovery strictly mandates `force=True` and established writer quiescence.
