# T011-R6 PRESIGNOFF CLOSURE REPRODUCTIONS REPORT
## Deterministic Reproductions of PC-F01 (Writer Admission on Unresolved State) and PC-F02 (False Incident Persistence Success)

**Project:** US Flight Performance Analysis 2016–2024  
**Task:** T-011 R6 Pre-Signoff Closure  
**Parent Gate:** G5 (IN_PROGRESS)  
**Date:** 2026-10-19  
**Technical Role:** Independent Reliability & Concurrency Reviewer

---

## 1. Executive Summary

Prior to applying corrective remediation in production code, both residual defects reported by the independent technical auditor were reproduced deterministically on the Windows NTFS environment using isolated test harness scripts.

| Defect ID | Severity | Root Cause Subsystem | Unmitigated Failure Mode | Remediated Behavior |
|:---:|:---:|:---|:---|:---|
| **PC-F01** | BLOCKER | `SingleWriterLock.acquire()` & `release()` | When staging unlink fails in `release()`, canonical path `.pipeline.lock` is absent; subsequent writer acquires lock without operator recovery. | `acquire()` detects unresolved `.del_*`, `.failed_acq_*`, `.quarantine_*`, and release markers, raising `UnresolvedRecoveryStateError` (`FAIL_CLOSED — MANUAL_RECOVERY_REQUIRED`). |
| **PC-F02** | BLOCKER | `SingleWriterLock.persist_release_incident()` | `persist_release_incident()` caught all write exceptions and returned a `Path`, causing `__exit__` and `coordinator.py` to falsely claim `Incident persisted` when 0 incident files were written. | Atomic staging write, fsync, and readback verification; returns typed `IncidentPersistenceResult`; emits `INCIDENT_PERSISTENCE_FAILED` when write fails; zero false-success claims. |

---

## 2. Reproduction of PC-F01: Writer Admission on Unresolved State

### 2.1. Defect Description & Mechanism
In `SingleWriterLock`:
1. Run A calls `acquire()`. Canonical lock file `.pipeline.lock` is created.
2. In `release()`, atomic isolated removal moves `.pipeline.lock` to a temporary staging file `.{lock_filename}.del_{uuid}` via `os.rename`.
3. Canonical lock path `.pipeline.lock` is now absent on disk.
4. When `staging_del.unlink()` encounters an OS permission or locked handle error (`PermissionError` / `OSError`), `release()` raises `LockError`.
5. The orphaned staging file remains on disk in `lock_dir`.
6. Run B calls `acquire()`. `SingleWriterLock.acquire()` only checked `if self.lock_file_path.exists():`. Because `.pipeline.lock` was absent, Run B acquired the canonical lock without detecting the active unrecovered incident!

### 2.2. Isolated Reproduction Script & Output
```python
import tempfile, sys, os
from pathlib import Path
from flight_pipeline.storage.locking import SingleWriterLock

with tempfile.TemporaryDirectory() as td:
    ld = Path(td)
    lock_a = SingleWriterLock(ld, run_id='run_a')
    lock_a.acquire()

    # Simulate locked handle on Windows NTFS during staging deletion
    orig_unlink = Path.unlink
    def fake_unlink(self_path, *a, **kw):
        if 'del_' in self_path.name:
            raise PermissionError("Simulated locked file handle on unlink")
        return orig_unlink(self_path, *a, **kw)

    Path.unlink = fake_unlink
    try:
        lock_a.release()
    except Exception as e:
        print("Run A release raised:", type(e).__name__)
    finally:
        Path.unlink = orig_unlink

    # Run B calls acquire without manual recovery
    lock_b = SingleWriterLock(ld, run_id='run_b')
    acquired_b = False
    try:
        lock_b.acquire()
        acquired_b = lock_b.is_acquired
        lock_b.release()
    except Exception as e:
        print("Run B acquire raised:", type(e).__name__, e)

    print("PC-F01 DEFECT REPRODUCED (Run B acquired without recovery):", acquired_b)
```

**Observed Reproduction Output (Pre-Remediation):**
```
Run A release raised: LockError
All files in lock_dir after failed release: ['..pipeline.lock.del_336ec4b958f8467ebf063a000c9d8d3b', '.pipeline.lock.coord']
Canonical lock exists: False
Staging del files count: 1
DEFECT REPRODUCED PC-F01 (Run B acquired without recovery): True
```

### 2.3. Remediated Output (Post-Remediation)
Following the implementation of `get_unresolved_recovery_artifacts()`, durable release markers, and admission gating in `acquire()`:
```
Run A release raised: LockError
Run B blocked successfully as expected: Cannot acquire lock: unresolved recovery artifacts detected in lock directory: ['..pipeline.lock.del_8b687d0e3fc44862ac2a90cf915167f0', '..pipeline.lock.release_in_progress_56d71db2-2d61-4c98-b4b5-c6b4cf0c5d7f']. Incomplete lock release, crash during removal, or quarantined collision state requires authorized operator recovery before new writers may acquire the lock. FAIL_CLOSED — MANUAL_RECOVERY_REQUIRED
PC-F01 VERIFIED BLOCKED: True
Recovery result: True archived count: 2
Run B acquire succeeded after authorized recovery: True
```

---

## 3. Reproduction of PC-F02: Incident File Persistence False Success

### 3.1. Defect Description & Mechanism
In `SingleWriterLock.persist_release_incident()`:
```python
# PRE-REMEDIATION CODE:
try:
    self.lock_dir.mkdir(parents=True, exist_ok=True)
    incident_file.write_text(json.dumps(payload, indent=2), encoding="utf-8")
except Exception:
    pass
return incident_file
```
When `write_text()` failed due to disk exhaustion (`ENOSPC`), permission error (`EACCES`), or invalid directory:
1. The exception was caught by `except Exception: pass`.
2. The function nevertheless returned `incident_file` as a `Path` object.
3. Callers in `__exit__` and `coordinator.py` assumed `incident_file` was written and output messages claiming `Incident persisted at <path>`.
4. However, `incident_file.exists()` was `False`, and 0 incident files existed on disk.

### 3.2. Isolated Reproduction Script & Output
```python
import tempfile, os, sys
from pathlib import Path
from flight_pipeline.storage.locking import SingleWriterLock

with tempfile.TemporaryDirectory() as td:
    ld = Path(td)
    lock = SingleWriterLock(ld, run_id='run_test')

    # Simulate write failure in persist_release_incident
    orig_write = Path.write_text
    def fake_write(self, *args, **kwargs):
        raise OSError("Simulated disk full during incident logging")

    Path.write_text = fake_write
    try:
        inc_path = lock.persist_release_incident(release_err=PermissionError("Access denied"))
    finally:
        Path.write_text = orig_write

    print("Returned incident path:", inc_path)
    print("Returned incident path exists on disk:", inc_path.exists())
    actual_incident_files = list(ld.glob("*incident*"))
    print("Actual incident files count:", len(actual_incident_files))

    # Check __exit__ message
    lock._is_acquired = True
    lock.release = lambda: (_ for _ in ()).throw(PermissionError("Unlink failed"))
    exit_msg = ""
    try:
        lock.__exit__(Exception, Exception("pipeline failure"), None)
    except Exception as e:
        exit_msg = str(e)
    print("Exit message contains Incident persisted:", "Incident persisted" in exit_msg)
    print("DEFECT REPRODUCED PC-F02 (False success claims):", (not inc_path.exists()) and ("Incident persisted" in exit_msg))
```

**Observed Reproduction Output (Pre-Remediation):**
```
Returned incident path: C:\Users\...\lock_release_incident_bdb76379_fe6e8dff12fa.json
Returned incident path exists on disk: False
Actual incident files count: 0
Exit message contains Incident persisted: True
DEFECT REPRODUCED PC-F02 (False success claims): True
```

### 3.3. Remediated Output (Post-Remediation)
Following the implementation of `IncidentPersistenceResult`, atomic tempfile replacement, fsync, and readback verification:
```
Normal persist: True True True
Failed persist success: False
Failed persist verified: False
Failed persist incident_file: None
Failed persist error: Primary persistence failed (OSError: Simulated disk full / atomic rename failure)
Exit message with write failure: Lock release failed after block exception (PermissionError: Unlink failed). INCIDENT_PERSISTENCE_FAILED (Primary persistence failed (OSError: Simulated disk full / atomic rename failure)). FAIL_CLOSED — MANUAL_RECOVERY_REQUIRED
Contains false Incident persisted claim: False
Contains INCIDENT_PERSISTENCE_FAILED: True
```

---

## 4. Verification Conclusion

Both defects PC-F01 and PC-F02 have been eliminated. Subsequent writers are strictly fail-closed whenever unresolved recovery artifacts exist, and incident persistence failure is reported truthfully without false-success claims.
