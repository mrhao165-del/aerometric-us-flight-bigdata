# T007 EXIT DELTA - RUNMANIFEST LIFECYCLE & SAFE PUBLICATION STATE MACHINE

**Document ID:** `DOC-T007-EXIT-DELTA-04-STATE-MACHINE`  
**Task ID:** `T-007` (Raw CSV Ingestion Pipeline)  
**Gate:** `G4` (`PLANNED / NOT_COMPLETED`)  
**Design Authority:** Storage Systems Engineer & Repository Governance Reviewer  
**Binding Implementation:** `src/flight_pipeline/storage/publication.py`, `src/flight_pipeline/utils/run_manifest.py`  

---

## 1. RUNMANIFEST LIFECYCLE STATE MACHINE

To resolve **BLOCKER STORAGE-01**, T-007 formally aligns the pipeline execution lifecycle with the production implementation of `RunManifest` and `SafePublisher`.

```
  [State 0: RUN_STARTED]
          │
          ▼ (Spark distributed ingestion executed)
  [State 1: INGESTION_COMPLETED]
          │
          ▼ (Parquet files, magic bytes, and schemas validated)
  [State 2: STAGING_VERIFIED]
          │
          ▼ (DC-11 accounting balance checked: raw == acc + quar + rej)
  [State 3: PUBLICATION_PENDING]
          │
          ├──────────────────────────┐
          │ (SafePublisher.publish)  │ (Accounting or Staging Failure)
          ▼                          ▼
  [State 4: PUBLISHED]      [State 5: TERMINAL_FAILURE]
  (Pointer atomically       - ACCOUNTING_UNVERIFIED
   switched to run_id;      - FAILED_STAGING_CONTENT_INVALID
   receipt written)         - FAILED_COMPLETENESS
                            - FAILED_POINTER_SWITCH
```

### 1.1. State Transition Matrix

| State Name | Trigger Event | Mandatory Verifications | Manifest Status Value | Success Flag |
| :--- | :--- | :--- | :--- | :---: |
| **`RUN_STARTED`** | Job initialization | Generate unique `run_id`, detect host runtime versions | `"IN_PROGRESS"` | `None` |
| **`INGESTION_COMPLETED`** | Raw CSVs read & written to staging | Staging directory exists, non-empty, Parquet files generated | `"IN_PROGRESS"` | `None` |
| **`STAGING_VERIFIED`** | Pre-publication audit | Magic bytes `PAR1`, schema 34 cols, file inventory hashed | `"IN_PROGRESS"` | `None` |
| **`PUBLICATION_PENDING`** | Pre-promotion check | `RowAccounting.is_balanced()` is `True` | `"IN_PROGRESS"` | `None` |
| **`PUBLISHED`** | `SafePublisher` returns `status="PUBLISHED"` | Step 4 byte verification PASS, Step 5 pointer switched | `"PUBLISHED"` | `True` |
| **`TERMINAL_FAILURE`** | Any step aborts | Error recorded with traceback, non-destructive rollback | Failure Status | `False` |

---

## 2. PRODUCTION API RECONCILIATION

### 2.1. Strict Status Value Alignment
- Live production `SafePublisher.publish()` returns a `PublicationResult` object with:
  ```python
  PublicationResult(
      success=True,
      status="PUBLISHED",           # NEVER "SUCCESS"
      run_id=run_id,
      published_path=".../curated/runs/{run_id}",
      pointer_value=run_id,
      previous_pointer=previous_pointer,
      aborted_step=None
  )
  ```
- Design rule: `RunManifest.close(status="PUBLISHED")` is called **ONLY AFTER** `SafePublisher.publish()` returns `success=True`.
- It is strictly prohibited to record terminal success before the publication result is verified!

### 2.2. Semantics of `PublicationResult.published_path`
- If publication fails at Step 5 (`FAILED_POINTER_SWITCH` or `FAILED_POINTER_LOCK`) or Step 6 (`FAILED_POINTER_VERIFICATION`), the promoted versioned directory under `curated/runs/{run_id}` has already been copied by Step 3.
- In accordance with production source, `PublicationResult.published_path` **retains the string path of the promoted directory** for forensic analysis; the pointer file remains at `previous_pointer`. The directory is NOT deleted, ensuring non-destructive safety.

---

## 3. RESOLUTION OF MANIFEST SELF-REFERENCE: THE EXTERNAL RECEIPT

### 3.1. The Self-Reference Problem
If `RunManifest` attempts to include its own file path, byte size, and SHA-256 in `manifest.outputs`:
1. `manifest.to_bytes()` is serialized and hashed.
2. If `manifest.record_output("manifest.json", size, sha)` is called, it mutates `manifest.outputs`.
3. The mutation alters the byte content of `manifest.json`.
4. The previously calculated SHA-256 becomes invalid!
5. Re-serializing changes the hash again, creating an infinite mathematical loop.

### 3.2. The Canonical Architecture: Execution Receipt
T-007 solves this by establishing a strict boundary:
1. **`manifest.json` Role:** Captures data outputs and diagnostic logs only:
   - `accepted/` Parquet files
   - `quarantined/` Parquet files
   - `rejected/` CSV/Parquet files
   - Row accounting metrics (DC-11/12)
   - Environment and runtime versions
2. **`manifest.json` Finalization:**
   ```python
   # Finalize and persist manifest
   manifest.close(status=pub_result.status)
   manifest_sha = manifest.save(versioned_dir / "manifest.json")
   ```
3. **`_execution_receipt.json` Role:**
   An immutable sidecar execution receipt is written to `curated/runs/{run_id}/_execution_receipt.json`:
   ```json
   {
     "run_id": "20261017_T007_001",
     "task_id": "T-007",
     "publication_status": "PUBLISHED",
     "manifest_file": "manifest.json",
     "manifest_bytes": 4512,
     "manifest_sha256": "3a8b...7f",
     "published_path": "D:/Study/.../curated/runs/20261017_T007_001",
     "pointer_value": "20261017_T007_001",
     "previous_pointer": null,
     "published_at_utc": "2026-10-17T09:00:00Z"
   }
   ```
4. **Receipt Ownership & Verification:**
   - Generated by the pipeline runner immediately following Step 7.
   - Verified by independent QA auditors and downstream tasks (e.g., T-008, G5).
   - Manifest bytes remain 100% immutable and cryptographically verifiable.
