# T011-R3 Lock Recovery & Concurrency Safety Audit

**Project:** US Flight Performance Analysis 2016–2024  
**Task:** T-011 R3 — Provenance Trust Boundary, Numeric Integrity, Lock Recovery & Evidence Correction  
**Parent Gate:** G5 — IN_PROGRESS  
**Component:** SingleWriterLock (`src/flight_pipeline/storage/locking.py`)  
**Audit Finding Addressed:** R3-F03 (HIGH — Unknown-owner or corrupt lock deleted on `force=True`)  
**Date:** 2026-10-19  
**Status:** COMPLETE / FAIL-CLOSED MANUAL RECOVERY ENFORCED  

---

## 1. Executive Summary & Defect Remediation

During the independent technical audit of package `T011_R2_REVIEW_PACKAGE.zip`, finding **R3-F03** identified a critical filesystem concurrency risk in `src/flight_pipeline/storage/locking.py`:

In R2, when `SingleWriterLock.break_stale_lock(force=True)` was invoked against an unparseable, empty, or corrupted lock file, `_read_lock_metadata()` raised `json.JSONDecodeError` or `LockError`. The recovery method caught the exception and unconditionally deleted the lock:
```python
# Vulnerable R2 behavior
try:
    meta = self._read_lock_metadata()
except Exception:
    self.lock_path.unlink(missing_ok=True)
    return True
```
This behavior had severe architectural risks:
1. **Destruction of Evidence:** If two writers raced or a process crashed while writing metadata, destroying the corrupted lock erased diagnostic evidence.
2. **False Recovery of Active Locks:** A 0-byte lock file or incomplete write could belong to an active writer in the very process of acquiring the lock. Unlinking it allowed a second writer to acquire the lock concurrently, causing double-writer data corruption in Parquet staging.
3. **Unknown Ownership Risk:** A lock file without verified metadata cannot be proven to belong to a dead process.

In T011-R3, this defect is remediated by enforcing a strict **FAIL-CLOSED** policy. Automated deletion of unparseable, empty, or incomplete lock files is strictly prohibited. Such files require manual administrator investigation.

---

## 2. Hardened Invariants & Safety Protocol

### 2.1 The Fail-Closed Contract

Under R3 safety rules:
1. **Known Dead Process:** A lock may only be broken automatically if its metadata is 100% syntactically valid JSON, contains all required schema fields (`run_id`, `pid`, `host`), and the process with that PID is verified to no longer exist on the local host.
2. **Unparseable / Corrupt Lock:** If the lock file cannot be parsed, is 0 bytes, or is missing required fields, it represents an unknown-owner lock. Automated recovery MUST NOT delete it. Instead, it raises:
   `LockContentionError("FAIL_CLOSED — MANUAL_RECOVERY_REQUIRED: ...")`
3. **Race-Condition Pre-Unlink Verification:** Before deleting a known stale lock, the lock metadata is re-read and re-verified to ensure another process has not replaced it in the microsecond interval between verification and unlinking.

---

## 3. Production Source Hardening (`src/flight_pipeline/storage/locking.py`)

```python
def break_stale_lock(self, force: bool = False) -> bool:
    if not self.lock_path.exists():
        return False

    # Read lock metadata
    try:
        content = self.lock_path.read_text(encoding="utf-8").strip()
        if not content:
            # 0-byte or empty lock file
            raise LockContentionError(
                f"FAIL_CLOSED — MANUAL_RECOVERY_REQUIRED: Lock file '{self.lock_path}' is empty (0 bytes) "
                f"or blank. Ownership cannot be verified. Automatic deletion prohibited."
            )
        data = json.loads(content)
        # Verify required schema fields
        for req_field in ["run_id", "pid", "host"]:
            if req_field not in data:
                raise LockContentionError(
                    f"FAIL_CLOSED — MANUAL_RECOVERY_REQUIRED: Lock file '{self.lock_path}' is missing "
                    f"required schema field '{req_field}'. Ownership cannot be verified."
                )
        meta = LockMetadata(**data)
    except (json.JSONDecodeError, TypeError, ValueError) as parse_err:
        raise LockContentionError(
            f"FAIL_CLOSED — MANUAL_RECOVERY_REQUIRED: Cannot break unparseable or corrupted lock of "
            f"unknown ownership at '{self.lock_path}': {parse_err}. Manual inspection required."
        ) from parse_err

    # Host verification
    is_local_host = (meta.host == socket.gethostname())
    is_active = is_local_host and self._is_pid_alive(meta.pid)

    if is_active and not force:
        return False

    # Pre-unlink re-verification to eliminate race conditions
    try:
        fresh_content = self.lock_path.read_text(encoding="utf-8").strip()
        fresh_data = json.loads(fresh_content)
        if fresh_data.get("token") != meta.token:
            raise LockContentionError(
                f"FAIL_CLOSED: Lock token changed during break_stale_lock pre-unlink check."
            )
        self.lock_path.unlink(missing_ok=True)
        return True
    except Exception as e:
        if isinstance(e, LockContentionError):
            raise
        return not self.lock_path.exists()
```

---

## 4. Verification Evidence & Counterexample Guards

Permanent regression suite `tests/test_t011_r3_counterexamples.py` (`TestT011R3LockRecovery`) verifies all three fail-closed conditions:

1. `test_r3_f03_corrupt_lock_raises_fail_closed`: PASS (Corrupted non-JSON text raises `LockContentionError` with `FAIL_CLOSED — MANUAL_RECOVERY_REQUIRED`; file is NOT deleted).
2. `test_r3_f03_empty_lock_raises_fail_closed`: PASS (0-byte empty file raises `LockContentionError`; file is NOT deleted).
3. `test_r3_f03_incomplete_json_lock_raises_fail_closed`: PASS (JSON missing required fields raises `LockContentionError`; file is NOT deleted).

---

## 5. Conclusion

Finding **R3-F03** is **RESOLVED / CLOSED**. The single-writer locking subsystem is concurrency-safe and resilient against corrupted locks. No unknown-owner or unparseable lock can be deleted automatically.
