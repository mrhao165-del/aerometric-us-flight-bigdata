# T007_FINAL_REMEDIATION_PUBLICATION_RECEIPT_RECOVERY_AUDIT — Pointer Commit Boundary & Sidecar Receipt Reconciliation Audit (`FIX-F05`)

**Document ID:** `T007-FINAL-REMEDIATION-PUBLICATION-RECOVERY-20261017`  
**Task:** `MASTER-T007-FINAL-REMEDIATION` (`T-007` — Raw CSV Ingestion Pipeline)  
**Parent Gate:** `G4` (`PLANNED / NOT_COMPLETED`)  
**Date:** `2026-10-17`

---

## 1. Executive Summary

This report documents the remediation of **`FIX-F05` (Publication Pointer Commit Boundary, Manifest Protection & Post-Pointer Sidecar Receipt Reconciliation)** in [`src/flight_pipeline/ingestion/coordinator.py`](../../src/flight_pipeline/ingestion/coordinator.py).

---

## 2. Root-Cause Finding Closed

Previously, `IngestionCoordinator.run_ingestion()` wrapped the entire pipeline inside a single `try ... except Exception:` block that unconditionally executed `manifest.close(status="FAILED")` and returned `PipelineState.TERMINAL_FAILURE`.
- If `self.publisher.publish()` succeeded—meaning `data/curated/runs/<run_id>` was promoted and the active pointer (`data/curated/latest_run_id.txt`) was already switched to `<run_id>`—and a transient error occurred moments later while writing `execution_receipt.json`, the `except` handler would overwrite `run_manifest.json` to `status="FAILED"`.
- Similarly, if a caller accidentally re-invoked `run_ingestion()` with an already-published `run_id`, the `except` handler could overwrite the existing published run's `run_manifest.json` to `FAILED`.

---

## 3. Remediated Commit Boundary & State Machine (`FIX-F05`)

### 3.1 Strict Separation of Pre-Pointer vs Post-Pointer Failures
`IngestionCoordinator.run_ingestion()` tracks two explicit guards:
1. `is_duplicate_run_id`: Set to `True` if `data/curated/runs/<run_id>`, `data/staging/<run_id>`, or `data/metadata/<run_id>/run_manifest.json` already exists at `RUN_STARTED`.
   - When `is_duplicate_run_id` is `True`, the `except` block transitions to `PipelineState.TERMINAL_FAILURE` **without touching or overwriting** the existing `run_manifest.json` on disk.
2. `pointer_switched`: Set to `True` immediately after `self.publisher.publish()` returns `pub_result.success and pub_result.status == "PUBLISHED"`.
   - **Pre-Pointer Failure (`pointer_switched == False`):** The active pointer `data/curated/latest_run_id.txt` was not switched to `run_id` (any prior published run remains intact). The coordinator safely closes `run_manifest.json` with `status="FAILED"` and returns `PipelineState.TERMINAL_FAILURE`.
   - **Post-Pointer Sidecar Failure (`pointer_switched == True`):** The active pointer `data/curated/latest_run_id.txt` already points to `run_id` and `data/curated/runs/<run_id>` is live and immutable.
     - Both `run_manifest.json` (`status="PUBLISHED"`) and `execution_receipt.json` are written using `write_json_atomic_with_retry(..., max_retries=3)`.
     - If a post-pointer sidecar error still occurs (tested via `fault_injector("POST_POINTER_SIDE_EFFECT")`), the coordinator **NEVER** sets `manifest.status = "FAILED"`. Instead, it records `manifest.status = "PUBLISHED_RECEIPT_PENDING_RECONCILIATION"` and returns `PipelineState.PUBLISHED_RECEIPT_PENDING_RECONCILIATION`.

### 3.2 Non-Destructive Sidecar Recovery (`reconcile_published_run`)
`IngestionCoordinator.reconcile_published_run(run_id)` provides deterministic recovery for any run in `PUBLISHED_RECEIPT_PENDING_RECONCILIATION`:
1. Acquires `SingleWriterLock`.
2. Verifies that `data/curated/runs/<run_id>` exists and that `self.publisher.get_current_pointer() == run_id`.
3. Reads `data/metadata/<run_id>/run_manifest.json` and verifies `RowAccounting` balance (`DC-11`).
4. Calls `verify_parquet_directory_integrity(published_dir, expected_row_count=accounting.accepted_row_count, verify_curated_schema=True)` without modifying any file inside `data/curated/runs/<run_id>`.
5. Recomputes the output Parquet file inventory (`path`, `bytes`, `sha256`), atomically writes `run_manifest.json` with `status="PUBLISHED"`, computes `manifest_bytes` and `manifest_sha256`, and atomically writes `execution_receipt.json` with `pipeline_state="PUBLISHED"` and `publication_status="PUBLISHED"`.
6. Verified in `test_int_05_fix_f05_post_pointer_sidecar_failure_and_reconciliation`: Parquet file SHA-256 digests inside `data/curated/runs/run_post_ptr_01` are `100%` identical before and after reconciliation.
