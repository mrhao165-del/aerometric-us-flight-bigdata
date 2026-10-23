# T011-R6 PRESIGNOFF CLOSURE INCIDENT DURABILITY AUDIT
## Atomic Persistence, Readback Verification & Truthful Diagnostic Reporting

**Project:** US Flight Performance Analysis 2016–2024  
**Task:** T-011 R6 Pre-Signoff Closure  
**Parent Gate:** G5 (IN_PROGRESS)  
**Date:** 2026-10-19  
**Technical Role:** Evidence Governance & Filesystem Reliability Engineer

---

## 1. Defect Analysis & Threat Model (PC-F02)

In mission-critical data governance, evidence of system failures must be recorded with equal or greater durability than standard data outputs. The independent review identified that `SingleWriterLock.persist_release_incident()` had a critical false-success reporting flaw:
- It caught all exceptions raised by `Path.write_text()` via `except Exception: pass`.
- It returned the target `Path` object regardless of whether the write succeeded or failed.
- Downstream callers in `SingleWriterLock.__exit__` and `coordinator.py` inspected the return value and formatted error messages declaring: `Incident persisted at <path>`.
- In cases of disk exhaustion (`ENOSPC`), permission errors (`EACCES`), or directory read-only states, no file existed on disk, creating a deceptive audit trail.

---

## 2. Remediated Architecture & Atomic Durability Protocol

To guarantee that incident persistence claims are strictly truthful and resilient to filesystem failures, `persist_release_incident()` was redesigned to adhere to a 6-step atomic durability protocol:

```
[Incident Event]
      │
      ▼
1. Prepare JSON Payload (UUID, timestamp, tokens, stack traces, host, pid)
      │
      ▼
2. Open Temp Staging File (`.lock_release_incident_<token>_<id>.tmp_<rand>`)
      │  Flags: os.O_CREAT | os.O_WRONLY | os.O_TRUNC | os.O_BINARY, mode 0o600
      ▼
3. Write Full Buffer & Detect Short Writes (`bytes_written < len(content)`)
      │
      ▼
4. Hardware Sync (`os.fsync(fd)`) & Close Descriptor
      │
      ▼
5. Atomic Inode Replacement (`os.replace(tmp, dest)`)
      │
      ▼
6. Full Readback Verification (`dest.read_bytes() == content` & `json.loads`)
      │
      ├───────────────────────────────┬───────────────────────────────┐
      │ (Verification Succeeded)      │ (Any Step Failed)             │
      ▼                               ▼                               ▼
Return IncidentPersistenceResult(   Attempt Secondary Backup        Return IncidentPersistenceResult(
  success=True,                       (if secondary_dir provided)     success=False,
  incident_file=dest,                                                 incident_file=None,
  bytes_written=N,                                                    verified=False,
  verified=True,                                                      error="Primary persistence failed (...)"
  error=None                                                        )
)
```

---

## 3. Specification of `IncidentPersistenceResult`

The function returns an explicit typed dataclass rather than an ambiguous path:

```python
@dataclass
class IncidentPersistenceResult:
    """Result of attempting to persist an auditable lock release incident (PC-F02)."""
    success: bool
    incident_file: Optional[Path] = None
    bytes_written: int = 0
    verified: bool = False
    error: Optional[str] = None
    secondary_incident_file: Optional[Path] = None
```

### Invariant Rules:
1. `incident_file` is strictly `None` when `success=False` or `verified=False`.
2. `verified` is `True` ONLY after the destination file has been re-read from disk and confirmed to match the exact byte payload and incident UUID.
3. If primary persistence fails, secondary persistence (e.g., in a backup or system directory) is attempted if configured.
4. If all persistence attempts fail, `error` contains detailed diagnostic information and `success=False`.

---

## 4. Truthful Diagnostic Emission in `__exit__` and `coordinator.py`

### 4.1. `SingleWriterLock.__exit__`
```python
if rel_err is not None:
    inc_res = self.persist_release_incident(release_err=rel_err, pipeline_err=exc_val)
    if inc_res.success and inc_res.verified:
        incident_diag = f"Incident persisted at {inc_res.incident_file}"
    else:
        incident_diag = f"INCIDENT_PERSISTENCE_FAILED ({inc_res.error})"

    if exc_val is None:
        raise rel_err
    else:
        raise LockReleaseFailureError(
            f"Lock release failed after block exception ({type(rel_err).__name__}: {rel_err}). "
            f"{incident_diag}. FAIL_CLOSED — MANUAL_RECOVERY_REQUIRED"
        ) from exc_val
```
**Guarantee:** If persistence fails, the exception message states `INCIDENT_PERSISTENCE_FAILED (<error>)`. It is physically impossible for the message to claim `Incident persisted`.

### 4.2. `IngestionCoordinator` (`coordinator.py`)
In `coordinator.py`, `PipelineRunOutcome` records the exact persistence state:
```python
incident_info = {
    "incident_persisted": inc_res.success and inc_res.verified,
    "incident_file": str(inc_res.incident_file) if inc_res.incident_file else None,
    "incident_persistence_error": inc_res.error,
    "run_id": run_id,
    "release_error": rel_diag,
    "publication_preserved": outcome.success if outcome else False,
    "recovery_required": True,
    "recovery_state": "MANUAL_RECOVERY_REQUIRED",
    "timestamp": datetime.now(timezone.utc).isoformat(),
}
```
If persistence fails:
- `outcome.release_incident["incident_persisted"] == False`
- `outcome.release_incident["incident_file"] is None`
- `outcome.release_incident["incident_persistence_error"] == inc_res.error`
- `outcome.governance_warnings` appends `INCIDENT_PERSISTENCE_FAILED: ...`

---

## 5. Non-Destructive Publication Invariant Preserved

Even when lock release fails or incident persistence fails:
- If `IngestionCoordinator` has already committed outputs (`PublicationResult.success == True` and `latest_run_id.txt` points to `run_id`), `outcome.success` remains `True`.
- The committed Parquet files in `data/curated/runs/<run_id>/` are immutable and valid.
- The pipeline does **not** roll back or invalidate successful data merely because the post-publication release cleanup encountered an I/O error.
- Instead, the incident is flagged for manual operator recovery (`FAIL_CLOSED — MANUAL_RECOVERY_REQUIRED`).
