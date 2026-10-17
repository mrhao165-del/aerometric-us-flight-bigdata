# T007_SIGNOFF_EXIT — POST-PUBLICATION RECOVERY VERIFICATION (`BLOCKER-03`)

**Project:** US Flight Performance Analysis 2016–2024  
**Task:** `MASTER-T007-SIGNOFF-EXIT` (`BLOCKER-03` Closure)  
**Target Module:** `src/flight_pipeline/ingestion/coordinator.py` (`71,897` bytes, SHA-256 `2577275651b8f60e23af38725c8d8f01792e969a42ad471e238e320257652d06`)  
**Target Test Suite:** `tests/test_t007_pipeline_integration.py` (`INT-05` & `INT-07`)  

---

## 1. Root Cause Analysis of Pre-Fix `BLOCKER-03`

In commit `0434fe527da1bda5cf7830273921093876692364`, once `SafePublisher.publish()` succeeded (`latest_run_id.txt` switched to `<run_id>` and `data/curated/runs/<run_id>` became live), `IngestionCoordinator.run_ingestion()` prevented overwriting `run_manifest.json` to `FAILED` if a sidecar write failed (`FIX-F05`). However:
1. If the initial atomic write of `run_manifest.json` itself failed immediately after pointer switch (`Case B`), `run_manifest.json` did not exist on disk, and `reconcile_published_run(run_id)` raised `RuntimeError("Cannot reconcile run '<run_id>': manifest file missing...")`, leaving the live run without a recovery path.
2. `reconcile_published_run(run_id)` did not have an explicit fail-closed state (`PipelineState.MANUAL_RECONCILIATION_REQUIRED`) when `run_manifest.json` was corrupted on disk or when any required authoritative sidecar (`source_verification.json`, `anomaly_summary.json`, `forensic_manifest.json`) was missing/corrupted.

---

## 2. Production Fix Implemented in `src/flight_pipeline/ingestion/coordinator.py`

1. **Pre-Publication Authoritative Sidecar Completeness:**
   - Before `SafePublisher.publish()` is invoked, `IngestionCoordinator.run_ingestion()` atomically writes:
     - `data/metadata/<run_id>/source_verification.json` (verified input paths, exact byte sizes, SHA-256 hashes, verification states).
     - `data/quarantine/<run_id>/forensic_manifest.json` (verified `QUARANTINED` and `REJECTED` persistence counts, JSONL and Parquet paths).
     - `data/metadata/<run_id>/anomaly_summary.json` (authoritative `run_id`, `task_id`, `start_time`, `runtime_versions`, `configuration`, `previous_pointer`, `row_accounting`, `per_year_accounting`, `source_scan_results`, `forensic_persistence`, and `anomaly_breakdown`).
2. **Evidence-Backed Missing Manifest Reconstruction (`Case B`) & Receipt Recovery (`Case A`):**
   - `IngestionCoordinator.reconcile_published_run(run_id, fault_injector=None)` first verifies all three authoritative sidecar artifacts (`source_verification.json`, `anomaly_summary.json`, `forensic_manifest.json`), verifies that `source_scan_results` are verifiable and sum to `row_accounting.raw_row_count`, verifies that `row_accounting` is balanced (`DC-11`), verifies forensic Parquet directories (`quarantined_parquet/`, `rejected_parquet/`) against `quarantined_row_count` and `rejected_row_count`, and verifies the immutable published Parquet directory (`data/curated/runs/<run_id>`) against `accepted_row_count` and exact 34-column physical Arrow types (`BLOCKER-02`).
   - In **Case A** (`run_manifest.json` exists with `status="PUBLISHED_RECEIPT_PENDING_RECONCILIATION"` or `"PUBLISHED"`), `reconcile_published_run` validates `run_manifest.json` against the authoritative sidecars, finalizes `status="PUBLISHED"`, and writes `execution_receipt.json`.
   - In **Case B** (`run_manifest.json` is absent on disk because the initial manifest write failed after pointer switch), `reconcile_published_run` reconstructs `run_manifest.json` strictly from the verified authoritative sidecars and the verified published Parquet files (`outputs`), writes `run_manifest.json` (`status="PUBLISHED"`), and writes `execution_receipt.json` with matching `manifest_bytes` and `manifest_sha256`.
   - Zero files inside `data/curated/runs/<run_id>` are ever modified during reconciliation.
3. **Fail-Closed `PipelineState.MANUAL_RECONCILIATION_REQUIRED` Guard:**
   - If `run_manifest.json` exists on disk but is corrupted (invalid JSON, wrong `run_id`, invalid status, or `row_accounting`/`inputs` mismatch against authoritative sidecars), OR if any required sidecar (`source_verification.json`, `anomaly_summary.json`, `forensic_manifest.json`, or forensic/published Parquet directories) is missing, corrupted, or fails `DC-11` / schema verification:
     - `reconcile_published_run(run_id)` fails closed with `success=False, final_state=PipelineState.MANUAL_RECONCILIATION_REQUIRED`.
     - It **never** fabricates `row_accounting`, `inputs`, `outputs`, `run_manifest.json`, or `execution_receipt.json`, and **never** deletes or mutates the live pointer or published Parquet data.

---

## 3. Empirical Fault-Injection & Recovery Matrix (`INT-05` & `INT-07`)

| Scenario ID | Fault / Disk State Injected | `reconcile_published_run` Outcome | Curated Parquet & Pointer Integrity | Verdict |
| :--- | :--- | :--- | :--- | :--- |
| `INT-05` (Case A) | Fault at `POST_POINTER_SIDE_EFFECT` (`run_manifest.json` pending, `execution_receipt.json` missing) | `success=True`, `final_state=PUBLISHED`; `run_manifest.json` finalized to `PUBLISHED` and `execution_receipt.json` created | `latest_run_id.txt` preserved; published Parquet SHA-256 unchanged | **PASS** |
| `INT-07.1` (Case B) | Fault at `POST_POINTER_PRE_MANIFEST_WRITE` (pointer switched, both `run_manifest.json` and `execution_receipt.json` missing) | `success=True`, `final_state=PUBLISHED`; both `run_manifest.json` (`raw=6, accepted=4, quarantined=1, rejected=1, inputs=2, previous_pointer="run_prior_00"`) and `execution_receipt.json` reconstructed from verified sidecars | `latest_run_id.txt == "run_case_b_01"`; published Parquet SHA-256 unchanged | **PASS** |
| `INT-07.2` | Fault at `RECONCILE_PRE_RECEIPT_WRITE` during first `reconcile_published_run` call, followed by second retry | 1st call returns `success=False, final_state=PUBLISHED_RECEIPT_PENDING_RECONCILIATION`; 2nd call returns `success=True, final_state=PUBLISHED` | Published Parquet SHA-256 unchanged | **PASS** |
| `INT-07.3` | Repeated `reconcile_published_run` on an already `PUBLISHED` run | Idempotent (`success=True, final_state=PUBLISHED`); `run_manifest.json` SHA-256 and published Parquet SHA-256 remain 100% identical | Idempotent | **PASS** |
| `INT-07.4` | Corrupted `run_manifest.json` (`{CORRUPTED_NOT_VALID_JSON`) on disk | Fails closed with `success=False, final_state=MANUAL_RECONCILIATION_REQUIRED`; no fake receipt created | Live pointer & published Parquet untouched | **PASS** |
| `INT-07.5` | Missing `run_manifest.json` + missing required sidecar (`anomaly_summary.json` deleted) | Fails closed with `success=False, final_state=MANUAL_RECONCILIATION_REQUIRED`; neither manifest nor receipt fabricated; restoring `anomaly_summary.json` allows clean recovery to `PUBLISHED` | Live pointer & published Parquet untouched | **PASS** |
