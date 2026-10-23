# T011-R6 PRESIGNOFF CLOSURE RECOVERY PROTOCOL
## Operator Manual Recovery Playbook & Fail-Closed Writer Admission Boundary

**Project:** US Flight Performance Analysis 2016–2024  
**Task:** T-011 R6 Pre-Signoff Closure  
**Parent Gate:** G5 (IN_PROGRESS)  
**Date:** 2026-10-19  
**Technical Role:** Windows NTFS Concurrency Specialist & Storage Reliability Engineer

---

## 1. Concurrency Architecture & Threat Boundary

In high-concurrency and mission-critical distributed Big Data ingestion, single-writer exclusivity is enforced at the storage boundary. The T-011 architecture implements a multi-layered defense-in-depth model:

1. **Kernel / OS Coordination Lock (`CoordinationLock`):** Serializes all administrative operations (`acquire`, `release`, `break_stale_lock`, `resolve_recovery_state`) via blocking byte-range locks (`msvcrt.locking(LK_LOCK)` on Windows NTFS; `fcntl.flock(LOCK_EX)` on POSIX).
2. **Atomic Inode Creation (`O_CREAT | O_EXCL`):** Ensures atomic creation of `.pipeline.lock` with cryptographic owner tokens.
3. **OS-Authoritative Held Lock:** Open file descriptor `_fd` is retained throughout the active run, preventing external deletion (Windows WinError 32 `ERROR_SHARING_VIOLATION`) or truncation.
4. **Fail-Closed Writer Admission Gating (PC-F01):** Before creating a new writer lock, `acquire()` inspects `lock_dir` for unresolved staging deletions (`.del_*`), failed acquisitions (`.failed_acq_*`), quarantine files (`.quarantine_*`), or active release markers (`.release_in_progress_*`). If any such artifacts exist, acquisition is strictly denied with `UnresolvedRecoveryStateError` (`FAIL_CLOSED — MANUAL_RECOVERY_REQUIRED`).
5. **Durable Release Marker:** Established atomically prior to renaming `.pipeline.lock` to `.del_<uuid>` and cleared only after successful unlink. If an unhandled exception or process termination occurs during release, the marker and staging file remain, permanently blocking subsequent writers until an operator intervenes.

---

## 2. Why Automated Cleanup of Unknown Artifacts is Prohibited

A naive implementation might attempt to automatically delete leftover `.del_*` or `.failed_acq_*` files during `acquire()`. This is **strictly prohibited** by repository policy and concurrency safety for three fundamental reasons:

1. **Active Writer Race:** If process A is actively releasing or breaking a lock in a slow or heavily loaded I/O environment, an aggressive process B deleting `.del_*` files could destroy active state or corrupt file descriptors.
2. **Forensic Evidence Destruction:** Incomplete releases often indicate hardware I/O degradation, OS file locking conflicts, or out-of-band tampering. Deleting evidence destroys forensic audit trails.
3. **Inode Ambiguity:** On Windows NTFS, file deletion is deferred if any process retains an open handle. Deleting by path without verifying file identity risks deleting a newly created replacement file.

Therefore, unknown or orphaned recovery artifacts must remain undisturbed until an authorized human operator performs controlled investigation and recovery.

---

## 3. Specification of `resolve_recovery_state()`

The programmatic API for authorized manual recovery is implemented on `SingleWriterLock`:

```python
def resolve_recovery_state(
    self,
    authorized: bool = False,
    operator: str = "",
    reason: str = "",
    archive_dir: Optional[Path] = None,
) -> Dict[str, Any]:
```

### Safety Properties:
1. **Explicit Authorization Gate:** Requires `authorized=True`. Calling without this flag raises `LockError`.
2. **Identity & Justification Audit:** Requires non-empty `operator` and `reason` strings.
3. **CoordinationLock Serialization:** Executes under `with self._coord_lock:` to prevent concurrent acquisition or release during recovery.
4. **Forensic Archival (Non-Destructive):** Moves unresolved artifacts to `recovery_archive/` with unique resolution IDs and computes physical size and SHA-256 for each artifact.
5. **Audit Record Generation:** Generates `recovery_resolution_<resolution_id>.json` containing full provenance.
6. **Idempotency:** Calling `resolve_recovery_state()` repeatedly when 0 unresolved artifacts remain succeeds cleanly without altering existing archived records.

---

## 4. Controlled 5-Step Operator Manual Playbook

When an automated pipeline execution halts with:
`UnresolvedRecoveryStateError: Cannot acquire lock: unresolved recovery artifacts detected in lock directory ... FAIL_CLOSED — MANUAL_RECOVERY_REQUIRED`

The authorized systems operator must follow this 5-step playbook:

### Step 1: Verify Process Liveness
Check whether the prior pipeline process is still running:
```powershell
Get-Process -Name "python*" | Select-Object Id, ProcessName, StartTime, CPU
```
Verify that no background PySpark coordinator or executor is actively holding handles in `data/staging/` or `data/curated/`.

### Step 2: Inspect Lock Directory Contents
Examine the artifacts present in `data/staging/.locks`:
```powershell
Get-ChildItem -Path "data/staging/.locks" -Force
```
Identify the active blocking files (e.g., `..pipeline.lock.del_*`, `..pipeline.lock.release_in_progress_*`, `lock_release_incident_*.json`).

### Step 3: Verify Integrity of Published Data
Check if the pipeline run completed publication prior to the release failure:
- Inspect `data/curated/latest_run_id.txt` for the current pointer value.
- Verify that `data/curated/runs/<run_id>/` contains intact, valid Parquet files.
- Inspect `data/metadata/<run_id>/anomaly_summary.json` and `execution_receipt.json`.
- **CRITICAL RULE:** If publication succeeded (`latest_run_id.txt` points to `<run_id>`), DO NOT roll back or modify the curated Parquet files. The publication is valid and immutable.

### Step 4: Execute Authorized Operator Recovery
Run the recovery command via Python:
```python
from flight_pipeline.storage.locking import SingleWriterLock
from pathlib import Path

lock = SingleWriterLock(Path("data/staging/.locks"), run_id="operator_recovery")
result = lock.resolve_recovery_state(
    authorized=True,
    operator="Operator_Name",
    reason="Inspected Run <run_id>. Verified publication intact and prior process dead.",
)
print("Recovery completed:", result)
```

### Step 5: Verify Clear Admission State
Re-verify that no unresolved artifacts remain and test acquisition:
```python
artifacts = lock.get_unresolved_recovery_artifacts()
assert len(artifacts) == 0, f"Unresolved artifacts remain: {artifacts}"
print("Admission gate restored: Normal pipeline execution may resume.")
```
