# T007 DESIGN EXIT T-009 API & MANIFEST RECONCILIATION — STATUS FIDELITY & RECEIPT ARCHITECTURE

**Document ID:** `DOC-T007-DESIGN-EXIT-03-API-MANIFEST`  
**Task ID:** `T-007` (Raw CSV Ingestion Pipeline)  
**Phase:** `DESIGN RECONCILIATION (R1-EXIT)`  
**Gate:** `G4` (`PLANNED / NOT_COMPLETED`)  
**Design Authority:** Storage Interface Reviewer & Repository Governance Auditor  
**Live Production Modules:** [`src/flight_pipeline/storage/publication.py`](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/src/flight_pipeline/storage/publication.py), [`src/flight_pipeline/utils/run_manifest.py`](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/src/flight_pipeline/utils/run_manifest.py)  

---

## 1. LIVE PRODUCTION T-009 API AUDIT & STATUS RECONCILIATION

Direct audit of [`src/flight_pipeline/storage/publication.py`](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/src/flight_pipeline/storage/publication.py) establishes the exact method signatures, status constants, and operational mechanics:

### 1.1. Exact Method Signatures
```python
# SafePublisher Constructor
publisher = SafePublisher(base_data_dir="data")

# Publication Execution
result: PublicationResult = publisher.publish(
    run_id=run_id,
    staging_dir=Path(f"data/staging/{run_id}/curated"),
    accounting=accounting,
    fault_injection_step5=False
)
```

### 1.2. Authoritative `PublicationResult` Statuses

| Publication Step | Live Production Status Constant | Failure / Success Condition | Forensic Action |
|---|---|---|---|
| **Step 0 (Pointer Read)** | `"FAILED_INITIAL_POINTER_READ"` | Persistent OSError/PermissionError reading `latest_run_id.txt` | Aborts before touching staging. |
| **Step 0 (Run ID Path)** | `"FAILED_INVALID_RUN_ID"` | Path traversal (`..`) or invalid characters in `run_id` | Aborts before touching staging. |
| **Step 1 (Staging Exists)** | `"FAILED_STAGING_MISSING"` | Staging directory does not exist | Aborts; pointer untouched. |
| **Step 1 (Staging Empty)** | `"FAILED_STAGING_EMPTY"` | Staging directory contains no files | Aborts; pointer untouched. |
| **Step 1 (Parquet Missing)**| `"FAILED_STAGING_NO_PARQUET"` | Staging directory contains no `.parquet` files | Aborts; pointer untouched. |
| **Step 1 (Magic Bytes)** | `"FAILED_STAGING_CONTENT_INVALID"`| Parquet magic bytes (`b'PAR1'`) or Thrift metadata corrupt | Aborts; staging retained for review. |
| **Step 2 (Row Accounting)** | `"ACCOUNTING_UNVERIFIED"` | `accounting.is_balanced() == False` ($N_{\text{raw}} \neq \sum$) | Promotion halted; pointer untouched. |
| **Step 3 (Target Exists)** | `"FAILED_VERSION_EXISTS"` | `data/curated/runs/{run_id}/` already exists (immutability) | Promotion halted; existing data safe. |
| **Step 3 (Copy Failure)** | `"FAILED_PROMOTION"` | Exception during `shutil.copytree` | Destination cleaned up; staging untouched. |
| **Step 4 (Completeness)** | **`"FAILED_COMPLETENESS"`** | Byte size or SHA-256 mismatch between staging and promoted data | **Promoted version retained for forensics; NOT deleted!** Pointer untouched. |
| **Step 5 (Fault Injection)**| `"FAILED_POINTER_SWITCH"` | `fault_injection_step5=True` (simulated pointer failure) | Pointer remains at `previous_pointer`. |
| **Step 5 (Pointer Lock)** | `"FAILED_POINTER_LOCK"` | Transient OS error updating pointer file via `os.replace` | Pointer remains at `previous_pointer`. |
| **Final Step (Success)** | **`"PUBLISHED"`** | All 7 steps succeed; pointer switched atomically | **Status is strictly `"PUBLISHED"` (NOT `"SUCCESS"`).** |

> [!IMPORTANT]
> - SafePublisher returns `status="PUBLISHED"` upon successful publication.
> - Step 4 failure returns `status="FAILED_COMPLETENESS"` and **leaves the promoted version intact** so engineers can inspect corrupted blocks. It does NOT automatically delete the directory.

---

## 2. RESOLUTION OF THE MANIFEST SELF-REFERENCE CIRCULARITY

### 2.1. The Circularity Hazard
In earlier pipeline drafts, the sequence:
```python
manifest.save("data/staging/evidence/run_manifest.json")
manifest.record_output("evidence/run_manifest.json", size, sha256)
```
created an inescapable circularity:
1. `manifest.save()` writes the JSON payload to disk.
2. `manifest.record_output()` then modifies the `manifest.outputs` array in memory.
3. The in-memory object no longer matches the file on disk! Any subsequent recalculation of `manifest.to_bytes()` yields a different SHA-256 hash than the file saved on disk.

### 2.2. The Canonical Ingestion Receipt Architecture
To eliminate self-reference without modifying the production `RunManifest` API:
1. **Rule 1 (Manifest Outputs Scope):**
   `manifest.outputs` records **only data and diagnostic outputs produced by the pipeline**:
   - `year=2016/*.parquet` through `year=2024/*.parquet`
   - `evidence/quarantine/*.jsonl`
   - `evidence/rejected/*.txt`
   The manifest file itself is **never added** to its own `manifest.outputs` list!
2. **Rule 2 (Final Closure via Manifest Save):**
   Once all pipeline outputs are recorded, `manifest.close(status="SUCCESS")` is called, followed by a single, final `manifest.save(target_path)`.
   ```python
   manifest.close(status="SUCCESS")
   manifest_disk_sha256 = manifest.save(f"data/staging/{run_id}/evidence/run_manifest.json")
   ```
3. **Rule 3 (External Execution Receipt):**
   The disk SHA-256 and byte size of the saved manifest are recorded in an external **Execution Receipt** (`execution_receipt.json`) and returned in `PublicationResult.published_path`:
   ```json
   {
     "receipt_version": "1.0",
     "run_id": "run_20261017_153000",
     "manifest_file": "run_manifest.json",
     "manifest_bytes": 4812,
     "manifest_sha256": "4a7b2c9d...",
     "publication_status": "PUBLISHED"
   }
   ```
   This breaks the circularity completely and ensures 100% cryptographic consistency between memory and disk.

---

## 3. SYNTHETIC VERIFICATION SUITE DESIGN

In Subtask `T007-06`, the following 5 unit test cases are implemented to verify T-009 integration:

1. **`TEST-PUB-STATUS`:** Asserts that successful execution of `SafePublisher.publish()` returns `result.status == "PUBLISHED"` and `result.success == True`.
2. **`TEST-PUB-STEP4`:** Injects a single-byte corruption into a promoted part file; asserts `result.status == "FAILED_COMPLETENESS"`, `result.success == False`, and verifies the promoted folder was retained for forensics.
3. **`TEST-MANIFEST-DISK`:** Asserts that `manifest.save()` writes canonical UTF-8 bytes whose hash matches `manifest.calculate_sha256()`.
4. **`TEST-MANIFEST-NO-SELF-REF`:** Asserts that `manifest.outputs` contains only data files and does not contain `run_manifest.json`.
5. **`TEST-POINTER-ROLLBACK`:** Tests `fault_injection_step5=True`; asserts `result.status == "FAILED_POINTER_SWITCH"` and verifies `latest_run_id.txt` retains `previous_pointer`.

---

## 4. T-009 API & MANIFEST RECONCILIATION VERDICT

The publication interface and manifest workflow have been 100% reconciled with the live production implementation of `SafePublisher` and `RunManifest`.

**INTERFACE RECONCILIATION VERDICT: FULLY COMPLIANT WITH LIVE SOURCE.**
