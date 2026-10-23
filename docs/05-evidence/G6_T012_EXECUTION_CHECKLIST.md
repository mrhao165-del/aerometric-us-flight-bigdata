# Gate G6 Task T-012 — Execution Checklist
## Operational Verification Checklist for 9-Year Full Ingestion Run

**Project:** US Flight Performance Analysis 2016–2024  
**Date:** 2026-10-20 (Asia/Ho_Chi_Minh)  
**Parent Task:** Task T-012 / Gate G6  
**Parent Gate State:** `G6 — NOT_STARTED / BLOCKED`  
**Status:** **SUPERSEDED / DO_NOT_EXECUTE (Replaced by `G6_T012_FINAL_EXECUTION_CHECKLIST_V2.md`)**  

> [!WARNING]
> **VĂN BẢN ĐÃ HẾT HIỆU LỰC (SUPERSEDED / DO_NOT_EXECUTE):**  
> Bản danh mục sơ khai này chứa các đường dẫn và số liệu cũ (`staging/active/<year>`, `staging/runs/run_...`).  
> Văn bản này được niêm phong lịch sử và thay thế hoàn toàn bởi [`G6_T012_FINAL_EXECUTION_CHECKLIST_V2.md`](./G6_T012_FINAL_EXECUTION_CHECKLIST_V2.md). Tuyệt đối không vận hành theo các đường dẫn trong tài liệu này.  

---

## 1. Phase 0: Pre-Flight Gate Authorization Checklist

Do NOT proceed with any T-012 execution until all items in this section are certified:

- [ ] **CHKL-01: Official Gate G5 Signoff:** Project Lead has signed `G5_HUMAN_SIGNOFF_READINESS_DRAFT.md`, formally marking G5 as `PASS`.
- [ ] **CHKL-02: Exception G2-EXC-001 Resolved:** Project Lead has formally closed `G2-EXC-001`.
- [ ] **CHKL-03: Option B Formally Accepted:** Policy `FP-DEC-PROP-019` is approved as `FP-DEC-019`.
- [ ] **CHKL-04: Working Tree Cleanliness:** `python tools/check_working_tree_consistency.py` exits 0 with 0 FAIL.
- [ ] **CHKL-05: Storage Headroom Check:** Available space on drive `D:` is confirmed $\ge 25\text{ GB}$ (currently 59.47 GB).
- [ ] **CHKL-06: Raw Input Checksums:** All 9 raw CSV digests verified against `SOURCE_MANIFEST.json`.
- [ ] **CHKL-07: Staging 2016 Baseline Protected:** Existing physical 2016 Parquet in `data/staging/` is verified and marked read-only.

---

## 2. Phase 1: In-Flight Annual Batch Execution Checklist

Execute the 9 annual batches sequentially ($2016 \rightarrow 2024$). For each calendar year $Y$:

### Annual Step 1: Pre-Run Locking & Input Check
- [ ] **CHKL-ANN-01:** Acquire `SingleWriterLock(staging/active/<year>)`. Verify no stale lock collision.
- [ ] **CHKL-ANN-02:** Assert raw CSV file existence and checksum for year $Y$.

### Annual Step 2: Ingestion & Quality Partitioning
- [ ] **CHKL-ANN-03:** Read raw CSV via `RawCsvReader` under ANSI mode. Assert all 34 required columns present.
- [ ] **CHKL-ANN-04:** Execute `QualityEngine` rules. Partition into Accepted, Quarantined, and Rejected.
- [ ] **CHKL-ANN-05:** Verify DC-11 row accounting equation:
  $$\text{Raw Rows}(Y) == \text{Accepted}(Y) + \text{Quarantined}(Y) + \text{Rejected}(Y)$$
  *(If equation fails $\implies$ FAIL-CLOSED, halt pipeline immediately).*

### Annual Step 3: Staging & Atomic Publication
- [ ] **CHKL-ANN-06:** Write Snappy Parquet to `staging/runs/run_<year>_<run_id>/`.
- [ ] **CHKL-ANN-07:** Promote run using `SafePublisher` 7-step atomic rename protocol.
- [ ] **CHKL-ANN-08:** Update `staging/active/<year>/latest` pointer.
- [ ] **CHKL-ANN-09:** Generate and hash `run_manifest_<year>.json`.

### Annual Step 4: Cleanup & Checkpoint
- [ ] **CHKL-ANN-10:** Clean up intermediate shuffle files in `tmp_spark/`.
- [ ] **CHKL-ANN-11:** Release `SingleWriterLock` cleanly. Assert zero unlinked lock artifacts.
- [ ] **CHKL-ANN-12:** Record annual checkpoint before proceeding to year $Y+1$.

---

## 3. Phase 2: Year 2024 Special Defect Handling (OR-05)

When processing calendar year 2024:
- [ ] **CHKL-Y24-01:** Confirm presence of 335 operational days.
- [ ] **CHKL-Y24-02:** Confirm total absence of dates `2024-03-01` through `2024-03-31`.
- [ ] **CHKL-Y24-03:** Emit quality metric `source_coverage_status = PARTIAL`.
- [ ] **CHKL-Y24-04:** Assert that ZERO synthetic flights or interpolated records are injected into the 2024 dataset.

---

## 4. Phase 3: Post-Flight Multi-Year Closeout Checklist

Upon completion of all 9 annual runs:
- [ ] **CHKL-POST-01: Multi-Year Accounting Audit:** Compile aggregate DC-11/12 table across all ~54.7M rows. Assert 100% mutual exclusivity and balance.
- [ ] **CHKL-POST-02: Baseline Non-Regression:** Re-verify that 2016 physical Parquet matches baseline fingerprint `b5805fca...`.
- [ ] **CHKL-POST-03: Resource Benchmark Compilation (TS-014):** Compile full-run CPU, RAM, disk, and elapsed time logs.
- [ ] **CHKL-POST-04: Registry Registration:** Register all 9 annual manifests and quality summaries in `EVIDENCE_DELIVERABLE_REGISTER.json`.
- [ ] **CHKL-POST-05: Working Tree Consistency:** Run `tools/check_working_tree_consistency.py` and confirm 0 FAIL.
