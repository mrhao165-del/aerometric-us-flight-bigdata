# T011-R5 Windows Process Concurrency Tests

**Project:** US Flight Performance Analysis 2016–2024  
**Task:** T-011 R5 — Lock Safety Closure and Evidence Reconciliation  
**Parent Gate:** G5 — `IN_PROGRESS`  
**Governing Standard:** Windows NTFS File Sharing, Process Liveness, and Locking Invariants  
**Date:** 2026-10-19  

---

## 1. Concurrency Test Matrix

The following real OS-level inter-process and filesystem concurrency scenarios are tested in `tests/test_t011_r5_counterexamples.py`:

| Test ID | Test Method Name | Execution Mechanism | Expected Outcome | Verification Status |
| :--- | :--- | :--- | :--- | :---: |
| **PC-01** | `test_r5_f01_test_01_release_late_replacement_preserves_new_lock` | Injected replacement right at the unlink execution step in `release()` | `LockOwnerMismatchError` raised; replacement lock remains intact on disk | **PASS** |
| **PC-02** | `test_r5_f01_test_02_break_stale_lock_late_replacement_preserves_new_lock` | Injected replacement right at the unlink execution step in `break_stale_lock()` | `LockContentionError` raised; active replacement lock remains intact on disk | **PASS** |
| **PC-03** | `test_r5_f01_test_03_normal_acquire_release_no_contention` | Sequential acquire and release across 5 iterations | All acquire/release cycles clean; 0 leaked lock files | **PASS** |
| **PC-04** | `test_r5_f01_test_04_two_real_competing_worker_processes` | Two real OS child processes spawned via `subprocess.Popen` contending for same lock | Exactly one process gets exit 0; competing process gets exit 2 (`LockContentionError`) | **PASS** |
| **PC-05** | `test_r5_f01_test_05_release_while_second_process_requests_acquisition` | Main process holds lock; background worker polls; main releases | Background worker successfully acquires lock once released | **PASS** |
| **PC-06** | `test_r5_f01_test_06_corrupted_metadata_fail_closed` | Lock file populated with invalid/corrupted non-JSON string | Fail-closed (`LockContentionError` with `MANUAL_RECOVERY_REQUIRED`); file preserved | **PASS** |
| **PC-07** | `test_r5_f01_test_07_invalid_pid_and_unknown_liveness_fail_closed` | PID with non-positive integer (0, -10) | Fail-closed (`LockContentionError` with `MANUAL_RECOVERY_REQUIRED`); file preserved | **PASS** |
| **PC-08** | `test_r5_f01_test_08_replaced_lock_concurrently_recreated_after_move` | Atomic rename moves old lock to staging; competitor creates new lock at canonical path | Staging unlinked cleanly; competitor's new lock at canonical path completely intact | **PASS** |

---

## 2. Multi-Process Execution Validation

Test `PC-04` was specifically executed with real Python processes on Windows NTFS:
- Process 1 (PID A) acquires lock and holds it for 1.0 second.
- Process 2 (PID B) attempts acquisition while lock is held:
  - Fails closed immediately with `LockContentionError` (exit code 2).
- Process 1 finishes work, releases lock cleanly (exit code 0).
- Exit code distribution is exactly `[0, 2]`. No deadlock, no race condition, no corrupted lock files.
