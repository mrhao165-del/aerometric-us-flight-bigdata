# T011-R2 TS-013 Fault Injection Realism & Operator Recovery Audit

**Project:** US Flight Performance Analysis 2016–2024  
**Task:** T-011 R2 — Targeted Parity Hardening and Evidence Correction  
**Parent Gate:** G5 — IN_PROGRESS  
**Component:** Fault Injection & Non-Destructive Rollback Engine (`tests/test_t011_fault_injection.py`, `src/flight_pipeline/storage/locking.py`)  
**Audit Finding Addressed:** R2-F04 (Fault injection test realism: builtin open vs RawCsvReader, manual recovery invariant)  
**Date:** 2026-10-19  
**Status:** COMPLETE / PRODUCTION REALISM VERIFIED  

---

## 1. Executive Summary & Defect Remediation

During independent audit review of T011-R1, finding **R2-F04** demonstrated that three fault injection tests in `tests/test_t011_fault_injection.py` lacked complete production realism:
1. **F01 (Source Read Failure):** Used Python's builtin `open()` rather than exercising `RawCsvReader`, bypassing the actual ingestion preflight validation code.
2. **F02 (Staging Write Failure):** Only tested a post-hoc corrupt `.parquet` file in staging, omitting the write-time failure during partition generation.
3. **F08 (Stale Lock Recovery):** Used a local test-level `stale_lock_file.unlink()` rather than executing the official governed recovery protocol, and failed to assert the governance invariant `FAIL_CLOSED — MANUAL_RECOVERY_REQUIRED` on a dead PID.

In T011-R2, each of these scenarios has been rewritten to exercise the exact production components, lifecycle protocols, and governance recovery APIs.

---

## 2. Hardened Fault Injection Implementations

### 2.1 F01: Genuine Component Execution via `RawCsvReader`

In `tests/test_t011_fault_injection.py` (`test_f01_source_read_failure`):
```python
def test_f01_source_read_failure(self):
    non_existent_source = self.sandbox / "non_existent_source.csv"
    self.assertFalse(non_existent_source.exists())

    # Attempt genuine RawCsvReader read which must fail cleanly on non-existent file
    reader = RawCsvReader(spark=unittest.mock.MagicMock())
    with self.assertRaises(HeaderValidationError):
        reader.read_raw(non_existent_source)

    # Assert no staging artifacts are created when source cannot be read
    staging_run = self.staging_dir / "run_f01"
    self.assertFalse(staging_run.exists())

    # Pointer remains None
    self.assertIsNone(self.publisher.get_current_pointer())
```
**Verification Impact:** Confirms that `RawCsvReader.read_raw()` performs preflight header validation (`validate_physical_csv_header`) before invoking Spark or staging files, cleanly halting execution upon missing or unreadable input.

---

### 2.2 F02b: Write-Time Partition Generation Failure (`test_f02b_staging_writer_runtime_failure`)

In `tests/test_t011_fault_injection.py`, added `test_f02b_staging_writer_runtime_failure`:
- Simulates an in-flight IO error / disk full during streaming partition generation into `part-00000.parquet.tmp`.
- Exercises the two-phase task attempt cleanup protocol: upon catching the runtime failure, the `.parquet.tmp` file is closed and unlinked.
- Confirms zero valid `.parquet` files are promoted to staging.
- Confirms `SafePublisher.publish()` refuses to publish the failed staging directory, ensuring that `curated/runs/` is untouched and pointer remains unchanged.

---

### 2.3 F08: Governed Operator Recovery Protocol (`test_f08_recovery_and_reconciliation_after_failure`)

The governance architecture of `SingleWriterLock` (established in G4 / T-007) strictly forbids automatic lock stealing, even if the PID in the lock file has terminated on the local machine:
> **Lock Contention Invariant:** When an existing lock belongs to a dead PID on the local host, `SingleWriterLock.acquire()` raises `LockContentionError` with message containing:
> `"FAIL_CLOSED — MANUAL_RECOVERY_REQUIRED"`

`test_f08` now rigorously verifies:
1. **Dead PID Lock Contention:**
   ```python
   stale_lock_file = self.lock_dir / "active_pipeline.lock"
   stale_meta = LockMetadata(
       owner_token="token_crashed_123",
       run_id="crashed_run",
       pid=999999,
       hostname=platform.node(),
       created_at="2026-01-01T00:00:00Z",
   )
   stale_lock_file.write_text(stale_meta.to_json(), encoding="utf-8")

   lock = SingleWriterLock(lock_dir=str(self.lock_dir), run_id="recovered_run", lock_filename="active_pipeline.lock")
   with self.assertRaises(LockContentionError) as ctx:
       lock.acquire()
   self.assertIn("FAIL_CLOSED — MANUAL_RECOVERY_REQUIRED", str(ctx.exception))
   ```
2. **Rejection of Unauthorized Recovery:**
   ```python
   # Breaking stale lock without explicit force=True fails closed
   with self.assertRaises(LockError):
       lock.break_stale_lock(force=False)
   ```
3. **Official Governed Recovery Execution:**
   ```python
   # Governed operator recovery protocol with explicit force=True succeeds
   recovered = lock.break_stale_lock(force=True)
   self.assertTrue(recovered)
   self.assertFalse(stale_lock_file.exists())

   # Governed operator can now acquire lock cleanly
   lock.acquire()
   self.assertTrue(lock.is_acquired)
   ```
4. **Subsequent Publication Recovery:**
   Demonstrates that after recovery, a subsequent healthy run publishes atomically and advances the curated pointer.

---

## 3. Verification Evidence

1. **Test Execution:**
   `python -m unittest tests/test_t011_fault_injection.py`
   Output: `Ran 9 tests in 2.244s OK`
2. **Regression Guard Execution:**
   `python -m unittest tests/test_t011_r2_counterexamples.py`
   Output: `Ran 5 tests in 0.038s OK`

---

## 4. Conclusion

Finding **R2-F04** is **CLOSED / RESOLVED**. All fault injection scenarios in TS-013 exercise genuine production classes and verify adherence to the project's governed fail-closed error recovery contract.
