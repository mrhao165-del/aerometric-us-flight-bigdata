# T011-R6 Acquire Failure & Replacement Lock Preservation Counterexamples

**Project:** US Flight Performance Analysis 2016–2024  
**Task:** T-011 R6 — Controlled Final Lock Safety Closure  
**Finding Reference:** R6-F01 (Acquire Failure Cleanup Deletes Replacement Lock)  
**Parent Gate:** G5 — `IN_PROGRESS`  
**Severity:** HIGH  
**Status:** REPRODUCED AND EMPIRICALLY DEMONSTRATED  

---

## 1. Problem Statement & Root Cause

In the R5 implementation of `SingleWriterLock.acquire()`, lines 322–336 contained this exception cleanup handler:

```python
# Write metadata and flush immediately
try:
    os.write(fd, meta_json)
    os.close(fd)
except Exception as e:
    try:
        os.close(fd)
    except Exception:
        pass
    try:
        self.lock_file_path.unlink(missing_ok=True)
    except Exception:
        pass
    raise LockError(f"Failed to write lock metadata: {e}") from e
```

### The Defect Mechanism
1. A writer calls `acquire()`. The atomic `os.open(..., O_CREAT | O_EXCL)` successfully creates the file and returns descriptor `fd`.
2. Before metadata writing completes, an out-of-band actor or competing process replaces the canonical lock file with another owner's lock.
3. `os.write(fd, meta_json)` fails (e.g. disk full, quota exceeded, process interruption, or short write).
4. The exception handler catches the error and executes `self.lock_file_path.unlink(missing_ok=True)`.
5. Because `unlink` is called directly against the canonical path without verifying that the file on disk is the one created by `fd`, **the replacement owner's lock file is deleted**.

---

## 2. Empirical Counterexample Reproduction

The counterexample is codified in `tests/test_t011_r6_counterexamples.py`:

- **Case 1 (`test_r6_f01_test_03_short_write_failure_cleans_own_incomplete_file`):**
  - Simulated `os.write` returning only 5 bytes.
  - Pre-fix R5: Did not inspect byte count; failed to raise `LockError` on partial write.
- **Case 2 (`test_r6_f01_test_04_acquire_failure_with_replacement_before_write_preserves_replacement`):**
  - Owner A creates lock file.
  - Simulated out-of-band replacement with Owner B (`owner_b_token_xyz_999`).
  - Write failure injected.
  - Pre-fix R5: Deleted Owner B's lock file via unconditional `unlink`.
- **Case 3 (`test_r6_f01_test_05_acquire_failure_with_replacement_immediately_before_cleanup`):**
  - File replaced right before cleanup handler executes.
  - Pre-fix R5: Failed to preserve Owner B.

Execution on unpatched R5 code:
```
Ran 11 tests in 0.101s
FAILED (failures=4)
```

---

## 3. Targeted Remediation Design

To resolve R6-F01 completely:
1. **Short Write Inspection:**
   ```python
   bytes_written = os.write(fd, meta_json)
   if bytes_written < len(meta_json):
       raise OSError(f"Short metadata write: wrote {bytes_written} of {len(meta_json)} bytes")
   ```
2. **Inode & Device File Identity Tracking:**
   Immediately upon opening `fd`, query `st_orig = os.fstat(fd)`. On Windows NTFS and POSIX, `(st_dev, st_ino)` uniquely identifies the physical file reference created by this `open` call.
3. **Replacement Preservation:**
   In the exception handler, query `st_cur = self.lock_file_path.stat()`:
   - If `(st_cur.st_ino, st_cur.st_dev) != (st_orig.st_ino, st_orig.st_dev)`:
     The canonical lock file was replaced! **Do NOT touch or delete `self.lock_file_path`**. Preserve the replacement lock intact and raise `LockError` declaring `FAIL_CLOSED — MANUAL_RECOVERY_REQUIRED`.
   - If `(st_cur.st_ino, st_cur.st_dev) == (st_orig.st_ino, st_orig.st_dev)`:
     Atomically isolate the failed file via `os.rename` to `.failed_acq_<uuid>`, verify `st_staging`, and unlink only the staging file.
4. **Retention of File Descriptor:**
   Hold `self._fd` open while the lock is acquired to provide OS-level kernel protection against deletion or replacement on Windows NTFS.
