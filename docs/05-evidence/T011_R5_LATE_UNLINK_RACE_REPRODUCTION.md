# T011-R5 Late Unlink Race Reproduction and Analysis

**Project:** US Flight Performance Analysis 2016–2024  
**Task:** T-011 R5 — Lock Safety Closure and Evidence Reconciliation  
**Parent Gate:** G5 — `IN_PROGRESS`  
**Finding Reference:** `R5-F01` (CRITICAL: Final Check-to-Unlink Race in `SingleWriterLock`)  
**Date:** 2026-10-19  

---

## 1. Description of the Vulnerability

In T011-R4, `SingleWriterLock` implemented double-checked metadata verification immediately before calling `Path.unlink()`:
```python
# R4 implementation snippet:
recheck_meta = self._read_existing_metadata()
if recheck_meta is None:
    ...
if recheck_meta.owner_token != self.owner_token:
    raise LockOwnerMismatchError(...)

try:
    self.lock_file_path.unlink()
except OSError as e:
    ...
```

While this defended against races occurring prior to the final metadata read, it remained vulnerable to a Time-of-Check to Time-of-Use (TOCTOU) race condition in the window **between** the final metadata read and the invocation of `self.lock_file_path.unlink()`.

Because `Path.unlink()` takes a path string and deletes whatever physical file happens to be at that path at the exact millisecond of the OS syscall, any replacement file created by another process during that interval was unconditionally unlinked.

---

## 2. Reproduction Counterexamples

The independent technical auditor reproduced this defect in two isolated counterexamples:

### Reproduction A: `release()` Late Replacement
1. Writer 1 acquires `.pipeline.lock` with `owner_token = "token_w1"`.
2. Writer 1 initiates `release()`.
3. Writer 1 reads metadata, passes validation (`owner_token == "token_w1"`).
4. An external or concurrent actor unlinks `.pipeline.lock` and creates a new lock file with `owner_token = "new_owner_token_999"` before Writer 1 calls `unlink()`.
5. Writer 1 calls `self.lock_file_path.unlink()`.
6. **Observed Failure:**
   - `release()` returned normally without error (`is_acquired = False`).
   - The new owner's lock was destroyed on disk (`self.lock_file_path.exists() == False`).

### Reproduction B: `break_stale_lock()` Late Replacement
1. Stale lock exists on disk with dead PID `99999999`.
2. Recovery tool calls `break_stale_lock(force=True)`.
3. Recovery tool reads metadata, validates PID as dead, and verifies final metadata.
4. Another actor creates a new lock with active PID and `owner_token = "active_replacement_token_222"`.
5. Recovery tool calls `self.lock_file_path.unlink()`.
6. **Observed Failure:**
   - `break_stale_lock(force=True)` returned `True`.
   - The active new process's lock was destroyed on disk.

---

## 3. Pre-Fix Verification Evidence

Executing the unpatched R4 code with an injected late hook directly confirmed the auditor's findings:
```text
R5-F01 Reproduction A: lock.release() completed without error!
Did the replacement lock survive? False

R5-F01 Reproduction B: break_stale_lock() returned: True
Did the replacement lock survive? False
```

---

## 4. Root Cause and Systemic Flaw

1. **Non-Atomic Path Deletion:** Standard user-space filesystems (NTFS, POSIX) do not offer an atomic `unlink_if_owner_token_matches(path, token)` primitive. Path unlinking is unconditional.
2. **Unquiesced Autonomous Breaking:** Calling `break_stale_lock()` in a system where other writers might concurrently contend or recover without OS-level critical section serialization is inherently susceptible to TOCTOU races.
3. **Absence of Coordinated Inter-Process Critical Section:** While lock acquisition used atomic file creation (`O_CREAT | O_EXCL`), the removal phase lacked a coordinated OS-level synchronization boundary.
