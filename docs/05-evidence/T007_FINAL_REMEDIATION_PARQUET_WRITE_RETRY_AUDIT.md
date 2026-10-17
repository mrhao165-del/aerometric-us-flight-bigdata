# T007_FINAL_REMEDIATION_PARQUET_WRITE_RETRY_AUDIT — Two-Phase Task Attempt Staging & Readback Verification Audit (`FIX-F04`)

**Document ID:** `T007-FINAL-REMEDIATION-PARQUET-RETRY-20261017`  
**Task:** `MASTER-T007-FINAL-REMEDIATION` (`T-007` — Raw CSV Ingestion Pipeline)  
**Parent Gate:** `G4` (`PLANNED / NOT_COMPLETED`)  
**Date:** `2026-10-17`

---

## 1. Executive Summary

This report documents the remediation of **`FIX-F04` (Parquet Write Integrity, Executor Retry Safety & Independent Readback Verification)** in `write_dataframe_parquet_safe()` and `verify_parquet_directory_integrity()` within [`src/flight_pipeline/ingestion/coordinator.py`](../../src/flight_pipeline/ingestion/coordinator.py).

---

## 2. Root-Cause Finding Closed

Previously, `write_dataframe_parquet_safe()` wrote partition files directly into `staging_dir / f"part-{part_id:05d}-{uid}.parquet"` inside `df.mapInArrow()`. Under that design:
1. If a Spark task failed mid-partition or was retried/speculated by the executor, an incomplete or duplicate `part-{part_id:05d}-{uid1}.parquet` file could remain in `staging_dir` alongside the retry's `part-{part_id:05d}-{uid2}.parquet`.
2. Because `SafePublisher` promotes all `.parquet` files in `staging_dir`, orphan or duplicate task-attempt files would cause silent row duplication or corrupt file promotion unless explicitly isolated and verified.

---

## 3. Two-Phase Task Attempt Staging Protocol (`write_dataframe_parquet_safe`)

`write_dataframe_parquet_safe(df, staging_dir, compression="snappy", expected_row_count=None, verify_curated_schema=False)` now implements a deterministic two-phase commit protocol:

### Phase 1 — Isolated Task-Attempt Writing (`staging_dir / "_task_attempts"`)
1. **Pre-Write Cleanup:** Removes any pre-existing `_task_attempts/` directory, `.parquet`, or `.tmp` files in `staging_dir`.
2. **Task Attempt Context Identification:** Inside `_write_partition_arrow(batch_iter)`, inspects `TaskContext.get()` for:
   - `part_id = ctx.partitionId()`
   - `attempt_num = ctx.attemptNumber()`
   - `task_attempt_id = ctx.taskAttemptId()`
3. **Temporary `.parquet.tmp` Streaming Write:**
   - Streams Arrow record batches to `_task_attempts / f"part-{part_id:05d}-attempt-{attempt_num}-{task_attempt_id}-{uid}.parquet.tmp"`.
   - Only after all batches in the partition are written and `writer.close()` completes does the task atomically rename `.parquet.tmp` -> `.parquet` inside `_task_attempts`.
   - If any exception occurs mid-partition, `writer.close()` is called and both `.parquet.tmp` and `.parquet` for that failed attempt are immediately unlinked in the `except` handler before re-raising.

### Phase 2 — Driver Promotion of Winning Attempts & `_task_attempts` Purge
1. **Winning Attempt Selection:** On the driver after `df.mapInArrow(...).collect()`, results are indexed by `part_id` (selecting the winning `task_attempt_id` returned by Spark's DAGScheduler).
2. **Atomic Promotion to Canonical Partition Name:** For each winning partition with `rows_written > 0`, the winning attempt file is promoted via `os.replace` to `staging_dir / f"part-{part_id:05d}.parquet"`.
3. **Complete Purge of `_task_attempts`:** `shutil.rmtree(staging_dir / "_task_attempts")` runs in both normal flow and `finally`, guaranteeing that any orphan file from a failed or speculative attempt inside `_task_attempts` is permanently removed before `staging_dir` is inspected or published.

---

## 4. Independent Post-Write Readback & Schema Verification (`verify_parquet_directory_integrity`)

Immediately after promotion (and again at `PipelineState.STAGING_VERIFIED`), `verify_parquet_directory_integrity()` verifies:
1. **Zero Leftover Temporary Artifacts:** Confirms zero `*.tmp` / `*.parquet.tmp` files and no `_task_attempts` directory exist in `parquet_dir`.
2. **Magic Byte & Footer Parseability:** Calls `is_valid_parquet_file(pf)` (`PAR1` header/footer + Thrift metadata) on every `.parquet` file.
3. **Row Count Conservation:** Sums `pq.ParquetFile(pf).metadata.num_rows` across all `.parquet` files (`readback_rows`) and enforces:
   - `readback_rows == driver_written_rows`
   - `readback_rows == expected_row_count` (`accounting.accepted_row_count`)
   - Raises `RuntimeError("PARQUET_WRITE_INTEGRITY_ERROR: ...")` on any discrepancy.
4. **Curated Schema & Technical Column Isolation (`verify_curated_schema=True`):**
   - Verifies that every `.parquet` file has the exact `34` canonical columns (`CANONICAL_COLUMN_NAMES`) in canonical order and that zero technical columns (`_corrupt_record`, `_record_status`, `_anomaly_reason`, `_anomaly_flags`, `_source_year`, `_source_file`, `_record_lineage_id`) leaked into curated Parquet.
