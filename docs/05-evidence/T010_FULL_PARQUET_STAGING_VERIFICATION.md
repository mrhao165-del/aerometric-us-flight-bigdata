# T010_FULL_PARQUET_STAGING_VERIFICATION.md — Staging Parquet Output & Readback Verification

**Gate:** G5  
**Task:** T-010 — Bounded Real-Data Smoke & Resource Benchmark  
**Author:** Windows Storage Reliability Engineer & Independent QA Reviewer  
**Execution Timestamp:** 2026-10-18T11:07:20+00:00 (2026-10-18T18:07:20+07:00)  
**Status:** PASS (CONTROLLED)  

---

## 1. Scope & Isolation Architecture

Task T-010 is a bounded smoke and benchmark task under Gate G5. To adhere strictly to repository governance and prevent premature state pollution:
- All output Parquet files were directed exclusively to isolated subdirectories inside `D:\Study\Code\Apache\Flight_Analyzt\staging\`.
- Under NO circumstance was the production pointer `data/curated/latest` updated or switched.
- Staging directories were assigned unique, immutable run IDs based on execution timestamps.

---

## 2. Inventory of Generated Smoke Artifacts

Three isolated staging directories were generated and validated during the execution of Task T-010:

```
D:\Study\Code\Apache\Flight_Analyzt\staging\
├── smoke_2016_micro_20261018_110720\
│   └── part-00000.parquet
├── smoke_2016_jan_20261018_110720\
│   ├── part-00000.parquet
│   └── ... (12 files)
└── smoke_2016_20261018_110720\
    ├── part-00000.parquet
    └── ... (12 files)
```

| Staging Run Directory | Purpose | File Count | Disk Size | Expected Rows | Readback Rows | Row Integrity |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `smoke_2016_micro_20261018_110720` | Phase 3 Micro-Smoke | `1` | `43,446` bytes (42.4 KB) | `1,000` | `1,000` | **MATCH (Exact)** |
| `smoke_2016_jan_20261018_110720` | Phase 4 January Smoke | `12` | `23,124,812` bytes (22.05 MB) | `433,298` | `433,298` | **MATCH (Exact)** |
| `smoke_2016_20261018_110720` | Phase 5 Full-Year Smoke | `12` | `332,018,057` bytes (316.64 MB) | `5,537,987` | `5,537,987` | **MATCH (Exact)** |

---

## 3. Two-Phase Task Attempt Staging Audit (FIX-F04)

All writes were managed by [write_dataframe_parquet_safe](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/src/flight_pipeline/ingestion/coordinator.py#L222-L395).

An audit of the staging directories confirms:
1. **Task Attempt Directory Cleanup:** The internal staging subdirectory `_task_attempts` was completely removed via `shutil.rmtree` upon task completion in all three runs.
2. **Zero Orphan Attempts:** Zero `.parquet.tmp`, `.tmp`, or unpromoted attempt files were left behind.
3. **Partition Deduplication:** Only the winning task attempts returned by Spark to `collect()` on the driver were promoted via atomic `os.replace` into `part-{part_id:05d}.parquet`.

---

## 4. Schema Conformance & Technical Column Leak Audit

Every generated Parquet partition file across all three staging directories was inspected using PyArrow metadata:

### 4.1 Absence of Technical Columns
- `_corrupt_record`: **ABSENT (0 occurrences)**
- `_record_status`: **ABSENT (0 occurrences)**
- `_anomaly_reason`: **ABSENT (0 occurrences)**
- `_anomaly_flags`: **ABSENT (0 occurrences)**
- `_source_year`: **ABSENT (0 occurrences)**
- `_source_file`: **ABSENT (0 occurrences)**
- `_record_lineage_id`: **ABSENT (0 occurrences)**

### 4.2 Exact Canonical Schema Conformance
The physical Arrow schema of the output Parquet files matched [`get_curated_parquet_schema()`](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/src/flight_pipeline/ingestion/schema.py#L182-L245) field-for-field:
- **Columns Count:** Exactly 34 columns.
- **Physical Column Names & Order:** Identical to `CANONICAL_COLUMN_NAMES` (0..33).
- **Physical Types:**
  - `FL_DATE`, `OP_CARRIER`, `ORIGIN`, `DEST`, `CRS_DEP_TIME`, `DEP_TIME`, `WHEELS_OFF`, `WHEELS_ON`, `CRS_ARR_TIME`, `ARR_TIME`: `pa.string()`
  - `DEP_DELAY`, `TAXI_OUT`, `TAXI_IN`, `ARR_DELAY`, `CRS_ELAPSED_TIME`, `ACTUAL_ELAPSED_TIME`, `AIR_TIME`, `FLIGHTS`, `DISTANCE`, `O_TEMP`, `O_PRCP`, `O_WSPD`, `D_TEMP`, `D_PRCP`, `D_WSPD`, `ORIGIN_LATITUDE`, `ORIGIN_LONGITUDE`, `DEST_LATITUDE`, `DEST_LONGITUDE`: `pa.float64()`
  - `MONTH`, `DAY_OF_MONTH`, `DAY_OF_WEEK`, `DEST_AIRPORT_ID`: `pa.int64()`

---

## 5. Verification Conclusion

The Parquet staging files demonstrate 100% row conservation, exact schema compliance, complete isolation from the production pointer, and zero disk contamination.
