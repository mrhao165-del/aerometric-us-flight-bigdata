# T011-R6 PRESIGNOFF CLOSURE FP-DEC-PROP-018 REVIEW
## Proposed Human Governance Policy: Treatment of Post-Publication Lock Release Incidents

**Project:** US Flight Performance Analysis 2016–2024  
**Task:** T-011 R6 Pre-Signoff Closure  
**Parent Gate:** G5 (IN_PROGRESS)  
**Proposed Policy ID:** `FP-DEC-PROP-018`  
**Current Status:** `PROPOSED` (Awaiting Project Lead Explicit Human Signoff)  
**Date:** 2026-10-19  
**Submission Authority:** Senior PySpark Reliability & Governance Engineer

---

## 1. Context & Motivation

During autonomous pipeline execution, a critical architectural edge case occurs when:
1. `IngestionCoordinator` successfully executes data ingestion, validation, row accounting, and staging.
2. `SafePublisher` successfully executes the 7-step atomic publication protocol:
   - Parquet directory promoted to `data/curated/runs/<run_id>/`.
   - `latest_run_id.txt` atomically switched to point to `<run_id>`.
   - Execution receipt and manifest finalized.
3. However, in the `finally:` block of `IngestionCoordinator.run_ingestion()`, calling `SingleWriterLock.release()` raises an OS exception (e.g., Windows NTFS file locking conflict, sharing violation WinError 32 on `.pipeline.lock.del_*`, or disk failure).

Prior to this review, the system lacked a formalized human governance decision on how to classify the run outcome, whether to permit downstream reads, and how to govern subsequent write admissions.

---

## 2. Eight Core Dimensions of Proposed Decision FP-DEC-PROP-018

### 2.1. The Proposed State Transition
- **Pipeline Execution State:** Transitions normally through `INGESTION_COMPLETED -> STAGING_VERIFIED -> PUBLISHED`.
- **Post-Publication Incident Trigger:** When `release()` raises an exception in `finally:`, the execution outcome records state `PUBLISHED` but flags `recovery_required=True` and status `MANUAL_RECOVERY_REQUIRED`.
- **Target State Machine:**
  ```
  [PUBLISHED]
       │
       ▼ (Release cleanup fails)
  [PUBLISHED_WITH_RECOVERY_REQUIRED]
       │
       ▼ (Operator executes resolve_recovery_state)
  [CLEARED / READY_FOR_NEXT_WRITER]
  ```

### 2.2. Validity & Readability of Published Outputs
- **Policy:** **PUBLISHED OUTPUTS REMAIN 100% VALID AND READABLE.**
- **Rationale:** The Parquet payload was verified, staged, promoted, and pointed to before the lock release cleanup was attempted. The release cleanup failure is purely a concurrency management artifact, not a data corruption event. Rolling back valid data would introduce unnecessary downtime and risk data loss.

### 2.3. Representation of `PipelineRunOutcome.success`
- **Policy:** **`PipelineRunOutcome.success` REMAINS `True`.**
- **Rationale:** The data transformation and publication mission succeeded. Altering `success=False` would cause automated orchestrators or CI to assume data ingestion failed, potentially triggering redundant or destructive retries.
- **Diagnostic Separation:** The failure is isolated to `outcome.release_error`, `outcome.release_incident`, and `outcome.governance_warnings`.

### 2.4. Representation of `RECOVERY_REQUIRED` Status
- Inside `PipelineRunOutcome.release_incident`:
  ```json
  {
    "incident_persisted": true,
    "incident_file": "path/to/lock_release_incident_...json",
    "recovery_required": true,
    "recovery_state": "MANUAL_RECOVERY_REQUIRED",
    "release_error": "LockError: Failed to delete isolated lock file...",
    "publication_preserved": true
  }
  ```
- In `PipelineRunOutcome.governance_warnings`:
  `CRITICAL_LOCK_RELEASE_FAILURE: Lock release failed (...). Incident persisted at (...). FAIL_CLOSED — MANUAL_RECOVERY_REQUIRED`

### 2.5. Mechanism That Blocks Subsequent Writers
- **Gating Enforcement:** `SingleWriterLock.acquire()` enforces a fail-closed boundary by scanning `lock_dir` for unresolved artifacts:
  - Staging files matching `*{lock_filename}*.del_*`
  - Failed acquisition files matching `*{lock_filename}*.failed_acq_*`
  - Quarantined files matching `*{lock_filename}*.quarantine_*`
  - Release markers matching `*{lock_filename}*.release_in_progress_*`
- If ANY of these files exist, `acquire()` raises `UnresolvedRecoveryStateError` (`FAIL_CLOSED — MANUAL_RECOVERY_REQUIRED`).
- Any new writer (including cooperating pipeline runs or scheduled batch jobs) is strictly prevented from acquiring the lock until the recovery state is cleared.

### 2.6. Verification of Durable Incident Evidence
- `SingleWriterLock.persist_release_incident()` implements atomic tempfile replacement, hardware flush (`os.fsync`), and exact byte readback verification.
- An incident is marked `incident_persisted=True` ONLY after the destination file is verified on disk.
- If persistence fails, the status is emitted as `INCIDENT_PERSISTENCE_FAILED`, preserving transparency.

### 2.7. Clearing the Incident (Authorized Operator Procedure)
- Automatic clearing is strictly prohibited to avoid race conditions and evidence destruction.
- Clearing requires an authorized operator calling `SingleWriterLock.resolve_recovery_state(authorized=True, operator=..., reason=...)`.
- The method safely moves unresolved artifacts to `recovery_archive/` with SHA-256 hashes and generates `recovery_resolution_<id>.json`.

### 2.8. Residual Risks & Mitigations
| Residual Risk | Severity | Mitigation in Proposed Policy |
|:---|:---:|:---|
| Operator clears recovery while another process is running | Medium | `resolve_recovery_state` runs under `CoordinationLock`; Step 1 of playbook mandates checking process liveness. |
| Disk failure prevents both primary and secondary incident persistence | Low | Emits explicit `INCIDENT_PERSISTENCE_FAILED` in exception message and logs; staging `.del_*` remains on disk blocking new writers. |
| Read traffic accesses newly published Parquet while lock is unresolved | Low | Acceptable by design; published Parquet files are immutable and verified before pointer switch. |

---

## 3. Human Signoff Submission

> [!IMPORTANT]
> This policy proposal is submitted for human technical review. It remains in status `PROPOSED` until the **Project Lead** explicitly approves and signs off. No autonomous agent has modified `DECISIONS.md` or approved this proposal.
