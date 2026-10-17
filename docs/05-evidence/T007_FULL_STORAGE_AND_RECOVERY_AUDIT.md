# T007_FULL_STORAGE_AND_RECOVERY_AUDIT — Windows NTFS Single-Writer Locking, Atomic Publish & Recovery Audit

**Document ID:** `T007-FULL-STORAGE-RECOVERY-20261017`  
**Task:** `T-007` (`T007-04`, `T007-05`, `T007-07`)  
**Parent Gate:** `G4` (`PLANNED / NOT_COMPLETED`)  
**Date:** `2026-10-17`

---

## 1. Windows `os.kill(pid, 0)` Root-Cause Analysis & Permanent Fix

### 1.1 Why `agy cli` Was Previously Interrupted During `test_t007_locking.py`
- On POSIX operating systems, `os.kill(pid, 0)` performs a kernel permission/existence check without delivering a signal.
- On Windows (`os.name == "nt"`), signal `0` is `signal.CTRL_C_EVENT` (`0`). Python's CPython implementation of `os.kill(pid, 0)` on Windows first calls `GenerateConsoleCtrlEvent(CTRL_C_EVENT, pid)`. When `pid` belongs to the current console process group (or `pid == os.getpid()`), Windows broadcasts a `CTRL_C_EVENT` (`SIGINT`) to every process attached to the console — including the parent `agy cli` process!
- **Permanent Fix in `src/flight_pipeline/storage/locking.py`:**
  `is_pid_alive(pid)` uses native Win32 kernel APIs via `ctypes.WinDLL("kernel32", use_last_error=True)`:
  1. `OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION=0x1000, False, pid)`
  2. `GetExitCodeProcess(handle, byref(exit_code))` -> alive iff `exit_code == STILL_ACTIVE (259)` (or `ERROR_ACCESS_DENIED (5)` if owned by another Windows security principal).
  3. `CloseHandle(handle)` in `finally`.
- **Verification:** `python -m unittest -v tests/test_t007_locking.py` executes `8/8` tests in `0.151s` with zero console signals and zero CLI interruption.

---

## 2. Single-Writer Lock Protocol (`SingleWriterLock`)

- **Lock Path:** `data/locks/ingestion_writer.lock`
- **Atomic Creation:** `os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)` guarantees OS-level mutual exclusion across concurrent processes.
- **Lock Payload (`LockMetadata`):** `run_id`, `pid`, `hostname`, `acquired_at_utc`, `python_executable`.
- **Stale Lock Recovery:**
  - If `ingestion_writer.lock` exists and contains valid JSON whose `pid` is confirmed dead (`is_pid_alive(pid) == False`), and `recover_stale=True`:
    1. Moves the stale lock file to `ingestion_writer.lock.stale.<timestamp_ms>.<pid>.json` for forensic audit (`G3-COND-C`).
    2. Retries atomic acquisition (`O_CREAT | O_EXCL`).
  - If the lock file is corrupt/non-JSON, `SingleWriterLock` fails closed (`LockAcquisitionError`) without deleting forensic evidence.

---

## 3. Atomic Publication & Fault Recovery (`SafePublisher` + `IngestionCoordinator`)

1. **Isolation of Diagnostic Artifacts:**
   - Diagnostic JSON files (`source_verification.json`, `anomaly_summary.json`, `run_manifest.json`, `execution_receipt.json`) are written exclusively under `data/metadata/<run_id>/`.
   - `data/staging/<run_id>/` contains only valid `.parquet` files written by `write_dataframe_parquet_safe`, ensuring `SafePublisher` Step 2 (`_verify_staging`) never encounters non-Parquet files in staging.
2. **Preservation of Prior Pointer on Failure (`ABORTED_PRESERVED_PREVIOUS`):**
   - Verified in `test_neg_05_fault_injection_corrupt_staging_and_recovery_retry`:
     - Run 1 (`run_initial_good`) publishes cleanly; `CURRENT_PUBLISHED_RUN.json` points to `run_initial_good`.
     - Run 2 (`run_corrupt_stage`) injects corruption into the staged `.parquet` file at `STAGING_VERIFIED`. `SafePublisher` detects invalid Parquet magic bytes (`PAR1`) before pointer switch, transitions to `ABORTED_PRESERVED_PREVIOUS`, and keeps `CURRENT_PUBLISHED_RUN.json` pointing to `run_initial_good`.
     - Run 3 (`run_retry_ok`) executes cleanly and advances `CURRENT_PUBLISHED_RUN.json` to `run_retry_ok`, while `data/curated/runs/run_initial_good` remains immutable on disk.
