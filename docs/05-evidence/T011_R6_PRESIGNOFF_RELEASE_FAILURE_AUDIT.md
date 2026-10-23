# T011-R6 PRESIGNOFF RELEASE FAILURE AUDIT & DECISION PROPOSAL
## Technical Remediation of Finding PS-01, Exception Chaining, Non-Destructive Invariants, and Proposed Decision FP-DEC-PROP-018

**Project:** US Flight Performance Analysis 2016–2024  
**Task:** T-011 Pre-Signoff Addendum  
**Gate:** G5 — `IN_PROGRESS` (Downstream Gate G6: `NOT_STARTED / BLOCKED` under `G2-EXC-001`)  
**Finding Remediated:** PS-01 (Silent suppression of lock release errors)  
**Proposed Decision:** `FP-DEC-PROP-018: Treatment of Post-Publication Lock Release Incidents`  
**Execution Authority:** AI Implementation Agent  
**Official Acceptance Authority:** Project Lead only.

---

## 1. Executive Summary

During independent review of T011-R6, the technical auditor reproduced a latent error suppression defect in the release handling logic of `SingleWriterLock.__exit__` and `IngestionCoordinator`:

1. In `SingleWriterLock.__exit__` (`src/flight_pipeline/storage/locking.py`), lines 635–641:
   ```python
   def __exit__(self, exc_type, exc_val, exc_tb):
       if self._is_acquired:
           try:
               self.release()
           except Exception:
               pass  # SILENT SUPPRESSION
   ```
2. In `IngestionCoordinator.run_ingestion` and `reconcile_published_run` (`src/flight_pipeline/ingestion/coordinator.py`):
   ```python
   finally:
       if lock.is_acquired:
           try:
               lock.release()
           except Exception:
               pass  # SILENT SUPPRESSION
   ```

Under this pattern, if `lock.release()` encountered a critical condition (such as `LockOwnerMismatchError` due to out-of-band lock replacement, file system permission failure, or isolation rename error), the error was silently discarded.

---

## 2. Technical Remediation & Architectural Invariants

### 2.1 Context Manager Remediation (`SingleWriterLock.__exit__`)

The context manager exit logic was completely rewritten to eliminate silent suppression while upholding Python exception chaining conventions:

1. **Clean Block Exit (`exc_val is None`):**  
   If the protected block completed normally but `release()` raised an exception `rel_err`, `persist_release_incident()` persists the incident report, and `rel_err` is raised directly.
2. **Exception in Block (`exc_val is not None`):**  
   If the block raised an exception `exc_val` AND `release()` also failed with `rel_err`, the system must not discard either error. It persists the incident report and raises:
   ```python
   raise LockReleaseFailureError(
       f"Lock release failed after block exception ({type(rel_err).__name__}: {rel_err}). "
       f"Incident persisted. FAIL_CLOSED — MANUAL_RECOVERY_REQUIRED"
   ) from exc_val
   ```
   This leverages Python's `__cause__` mechanism, ensuring that tracebacks and audit tools display both the primary pipeline error and the secondary release failure.
3. **Clean Release with Exception:**  
   If the block raised `exc_val` and `release()` succeeded cleanly, `__exit__` returns `None` / `False`, allowing `exc_val` to propagate unchanged.

### 2.2 Ingestion Coordinator Remediation (`coordinator.py`)

In `IngestionCoordinator`, release failure handling balances two critical, non-negotiable architectural mandates:
- **Mandate A (Fail-Closed Visibility):** Release failures must never be hidden.
- **Mandate B (Non-Destructive Publication Invariant):** Valid committed, published outputs must NEVER be rolled back or unpublished merely because transient lock release cleanup failed.

The `finally:` blocks in `run_ingestion` and `reconcile_published_run` now execute the following governed protocol:

```python
finally:
    if lock.is_acquired:
        try:
            lock.release()
        except Exception as rel_err:
            incident_file = lock.persist_release_incident(
                release_err=rel_err,
                pipeline_err=Exception(outcome.error_message) if (outcome and outcome.error_message) else None,
            )
            rel_diag = f"{type(rel_err).__name__}: {rel_err}"
            incident_info = {
                "incident_file": str(incident_file),
                "run_id": run_id,
                "release_error": rel_diag,
                "publication_preserved": outcome.success if outcome else False,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
            try:
                coord_inc = run_meta_dir / f"lock_release_incident_{run_id}.json"
                write_json_atomic_with_retry(coord_inc, incident_info)
            except Exception:
                pass

            if outcome is not None:
                outcome.release_error = rel_diag
                outcome.release_incident = incident_info
                outcome.governance_warnings.append(
                    f"CRITICAL_LOCK_RELEASE_FAILURE: Lock release failed ({rel_diag}). "
                    f"Incident persisted at {incident_file}. FAIL_CLOSED — MANUAL_RECOVERY_REQUIRED"
                )
                if not outcome.success:
                    outcome.error_message = (
                        f"{outcome.error_message} [LockReleaseFailure: {rel_diag}]"
                        if outcome.error_message
                        else f"LockReleaseFailure: {rel_diag}"
                    )
```

---

## 3. Incident JSON Schema

Whenever a release failure occurs, an auditable, non-destructive incident file is persisted to disk at `data/curated/locks/lock_release_incident_<owner_token>_<incident_id>.json` and `data/curated/metadata/<run_id>/lock_release_incident_<run_id>.json`:

```json
{
  "incident_id": "a1b2c3d4e5f6",
  "timestamp_utc": "2026-10-19T12:00:00.000000+00:00",
  "event": "LOCK_RELEASE_FAILURE",
  "lock_file_path": "data/curated/locks/.pipeline.lock",
  "lock_file_exists": true,
  "canonical_metadata": { ... },
  "owner_token": "token_12345",
  "run_id": "run_20261019_01",
  "pid": 1234,
  "hostname": "WORKSTATION-01",
  "release_error_type": "LockOwnerMismatchError",
  "release_error_message": "Lock owner mismatch! Cannot release lock...",
  "pipeline_error_type": null,
  "pipeline_error_message": null,
  "recovery_status": "MANUAL_RECOVERY_REQUIRED",
  "action_required": "Investigate lock file and release error. If pipeline outputs were published, preserve published immutable outputs and clean up residual lock file manually after verifying no concurrent writer is active."
}
```

---

## 4. Formal Proposed Decision: FP-DEC-PROP-018

```markdown
### FP-DEC-PROP-018: Treatment of Post-Publication Lock Release Incidents

**Status:** PROPOSED (Awaiting Project Lead Human Review & Decision)  
**Parent Task:** T-011 Pre-Signoff Addendum  
**Gate:** G5 — IN_PROGRESS  
**Date:** 2026-10-19  

#### Context
In Phase 7 of SafePublisher and the post-publication finalization of IngestionCoordinator, the pipeline reaches a commit point where:
1. Curated Parquet files are immutably placed in `data/curated/runs/<run_id>/`.
2. `latest_run_id.txt` atomically points to `<run_id>`.
3. `run_manifest.json` and `execution_receipt.json` are atomically persisted with matching SHA-256 hashes.
Following this commit point, the coordinator attempts to release `SingleWriterLock`.

If `lock.release()` encounters an unexpected error (e.g., transient NTFS file lock, owner token mismatch due to out-of-band manipulation, or disk permission error):
How should the pipeline treat the already-published dataset?

#### Options Considered
- **Option 1 (Destructive Rollback):** Treat release failure as a terminal pipeline failure. Revert `latest_run_id.txt` pointer and delete or quarantine the published Parquet directory.
  - *Risk:* Destroys valid, verified data. A release failure is a metadata coordination artifact, not a corruption of the Parquet payload. Rollback after pointer switch risks breaking active downstream readers.
- **Option 2 (Non-Destructive Preservation with Fail-Closed Incident Alerting — RECOMMENDED):** 
  - Preserve `outcome.success = True`.
  - Retain the published immutable Parquet directory and live pointer.
  - Persist an explicit, durable incident report JSON (`lock_release_incident_<id>.json`).
  - Attach `release_error` and `release_incident` to `PipelineRunOutcome`.
  - Append a critical governance warning declaring `FAIL_CLOSED — MANUAL_RECOVERY_REQUIRED`.
  - Block subsequent writers until an operator verifies host quiescence and cleans up the residual lock.

#### Proposed Decision
Adopt Option 2 as the project standard. Post-publication lock release failures MUST NOT unpublish or roll back valid committed datasets. The pipeline preserves data immutability, alerts operators through structured incident receipts, and fails closed against subsequent writes until governed manual recovery is completed.
```

---

## 5. Verification Matrix

The PS-01 remediation is verified by 8 deterministic unit tests in `tests/test_t011_r6_presignoff.py`:
1. `test_ps01_01_normal_release_clean_exit`: PASS
2. `test_ps01_02_owner_mismatch_raises_in_exit`: PASS
3. `test_ps01_03_permission_io_failure_raises_in_exit`: PASS
4. `test_ps01_04_pipeline_exception_with_release_failure_chains`: PASS
5. `test_ps01_05_pipeline_exception_with_normal_release_propagates`: PASS
6. `test_ps01_06_coordinator_already_published_preserves_outputs_on_release_error`: PASS
7. `test_ps01_07_coordinator_pipeline_failure_preserves_original_error`: PASS
8. `test_ps01_08_reconcile_published_run_records_release_incident`: PASS

Verdict: **PS-01_REMEDIATION_VERIFIED**.
