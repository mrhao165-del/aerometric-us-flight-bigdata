# Gate G6 Task T-012 — Risk, Fault Injection & Rollback Plan
## Fail-Closed Contingency Procedures, Crash Recovery, and Atomic Rollback Protocols

**Project:** US Flight Performance Analysis 2016–2024  
**Date:** 2026-10-20 (Asia/Ho_Chi_Minh)  
**Parent Task:** Task T-012 / Gate G6  
**Parent Gate State:** `G6 — NOT_STARTED / BLOCKED`  
**Status:** **AUTHORITATIVE ROLLBACK SPECIFICATION**  

---

## 1. Principles of Rollback & Fault Containment

The multi-year pipeline for Task T-012 is designed to withstand ungraceful process termination, disk saturation, and corrupted input without cascading failures:
1. **Raw Immutability:** Raw CSV files in `data/raw/tabular/` are opened exclusively in read-only mode (`"r"`, `"rb"`). No pipeline operation possesses write authority over raw data.
2. **Annual Isolation:** Because each calendar year runs in an independent atomic batch, a failure during Year $Y$ has **zero effect** on already validated and published years ($2016 \dots Y-1$).
3. **Atomic Pointer Promotion:** Unfinished staging Parquet resides in an unpromoted directory (`staging/runs/run_<year>_<id>/`). The production pointer `staging/active/<year>/latest` is updated **only after** all partitions, manifests, and accounting balances have been verified.
4. **NTFS Crash Recovery:** In the event of a sudden OS crash or power termination, `SingleWriterLock` utilizes atomic marker files and tombstone resolution (`.del_*` / `.release_in_progress_*`) verified under T-011 R6 post-closure.

---

## 2. Failure Scenarios & Targeted Contingency Procedures

### Scenario 1: Disk Space Depletion During Ingestion
- **Trigger:** Free storage on drive `D:` drops below the safety threshold of `10.0 GB`.
- **System Response:** The preflight disk monitor trips fail-closed, aborting the active annual run before writing begins.
- **Rollback Action:**
  1. Purge all scratch files in `D:/Study/Code/Apache/Flight_Analyzt/tmp_spark/`.
  2. Unlink the partial run directory in `staging/runs/`.
  3. The `latest` pointer of the active year remains pointed to the prior validated state.
  4. Previously completed annual batches are completely preserved.

---

### Scenario 2: Ungraceful Process Termination / Power Loss Mid-Year
- **Trigger:** JVM crash, OutOfMemoryError, or machine power cycle during partition write.
- **System State upon Restart:**
  - `SingleWriterLock` will detect an abandoned lock file or a pending release marker.
  - A partially written Parquet directory exists in `staging/runs/`.
- **Recovery & Rollback Protocol:**
  1. Invoke `SingleWriterLock.resolve_recovery_state()` to clean abandoned markers and re-establish writer admission guard.
  2. Verify that `staging/active/<year>/latest` still points to the previous valid run (or remains unset if Year 1).
  3. Purge the orphan directory in `staging/runs/run_<year>_<id>/`.
  4. Re-initiate the annual batch for year $Y$ cleanly.

---

### Scenario 3: DC-11 / DC-12 Row Accounting Imbalance
- **Trigger:**
  $$\text{Raw Rows}(Y) \ne \text{Accepted Rows}(Y) + \text{Quarantined Rows}(Y) + \text{Rejected Rows}(Y)$$
- **System Response:** The Quality Engine halts immediately with `DC11_ACCOUNTING_VIOLATION`.
- **Rollback Action:**
  1. `SafePublisher` strictly aborts before pointer update.
  2. The run is quarantined under `staging/quarantine/accounting_mismatch_<year>_<id>/`.
  3. An incident diagnostic log is emitted.
  4. No corrupted data enters active staging.

---

### Scenario 4: Driver JVM OutOfMemoryError
- **Trigger:** Heap pressure during wide shuffle aggregation on high-volume years (e.g. 2018 or 2019, ~7.2M rows).
- **Contingency Action:**
  1. Clean JVM cache via `spark.catalog.clearCache()`.
  2. Increase shuffle partition count from `16` to `32` (`spark.sql.shuffle.partitions = 32`), reducing per-task partition size to ~10 MB.
  3. Rerun the annual batch with isolated memory headroom.

---

## 3. Rollback Target Verification Matrix

| Target State | Scope of Rollback | Procedure | Verification Command |
|---|---|---|---|
| **Single-Year Rollback** | Specific calendar year $Y$ | Revert `staging/active/<year>/latest` to previous `run_manifest.json` | `python tools/qa/verify_staging_pointer.py --year <Y>` |
| **Complete T-012 Rollback** | All G6 generated staging data | Remove G6 generated run directories; preserve 2016 baseline | Verify fingerprint `b5805fca...` on `data/staging/` |
| **Lock System Rollback** | Recovery of lock contention | Execute `resolve_recovery_state()` with authorized token | `python -c "from flight_pipeline.storage.locking import SingleWriterLock; ..."` |
