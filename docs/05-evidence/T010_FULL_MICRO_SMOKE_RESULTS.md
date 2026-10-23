# T010_FULL_MICRO_SMOKE_RESULTS.md — Phase 3 Micro-Smoke on 2016 Real Data (1,000 Records)

**Gate:** G5  
**Task:** T-010 — Bounded Real-Data Smoke & Resource Benchmark  
**Author:** Senior PySpark Data Quality Engineer  
**Execution Timestamp:** 2026-10-18T11:07:20+00:00 (2026-10-18T18:07:20+07:00)  
**Run ID:** `smoke_2016_micro_20261018_110720`  
**Status:** PASS (CONTROLLED)  

---

## 1. Overview & Objectives

Phase 3 micro-smoke executed bounded ingestion, quality validation, curated Parquet serialization, and PyArrow readback verification across the first **1,000 logical records** of the real 2016 dataset (`data/raw/tabular/2016/flight_with_weather_2016.csv`).

The primary objectives were:
1. Verify that `RawCsvReader` and `QualityEngine` execute without regression on physical 2016 CSV data.
2. Verify exact DC-11 3-state disjoint row accounting balance: $N_{\text{raw\_observed}} (1,000) = N_{\text{accepted}} + N_{\text{quarantined}} + N_{\text{rejected}}$.
3. Verify that `write_dataframe_parquet_safe` produces compliant Parquet files in isolated staging without leaking technical columns.
4. Verify PyArrow readback row count matches accepted records.

---

## 2. Micro-Smoke Measured Metrics

| Metric Category | Parameter | Measured Value | Unit / Status |
| :--- | :--- | :--- | :--- |
| **Execution** | Wall-clock Duration | `7.193` | seconds |
| **Memory** | Peak Driver RSS | `115,388,416` (110.04) | bytes (MB) |
| **Row Accounting** | Observed Raw Records | `1,000` | rows |
| **Row Accounting** | Accepted Records ($N_{\text{accepted}}$) | `1,000` | rows |
| **Row Accounting** | Quarantined Records ($N_{\text{quarantined}}$) | `0` | rows |
| **Row Accounting** | Rejected Records ($N_{\text{rejected}}$) | `0` | rows |
| **Row Accounting** | DC-11 Accounting Balance | `1,000 = 1,000 + 0 + 0` | **BALANCED (True)** |
| **Row Accounting** | Ingest Acceptance Rate | `1.0000` (100.0%) | percentage |
| **Parquet Staging** | Staging Directory | `D:\Study\Code\Apache\Flight_Analyzt\staging\smoke_2016_micro_20261018_110720` | NTFS directory |
| **Parquet Staging** | Generated Parquet Files | `1` | part-00000.parquet |
| **Parquet Staging** | Readback Rows via PyArrow | `1,000` | rows |
| **Schema Validation** | Technical Columns Leaked | `0` (`_corrupt_record`, `_record_status` absent) | **VERIFIED** |
| **Schema Validation** | Business Columns | `34` matching curated schema | **VERIFIED** |

---

## 3. G3-COND-A Provisional Profiling (Micro-Sample)

Profiling on the 1,000 records using `ProvisionalPolicyProfiler.profile_flight_number_anomalies`:
- Total Records: `1,000`
- Non-Positive Flight Numbers (`OP_CARRIER_FL_NUM <= 0`): `0` (Rate: `0.0%`)
- Zero Flight Numbers: `0`
- Negative Flight Numbers: `0`
- Simulated Accepted (Canonical Policy): `1,000`
- Simulated Quarantined (Hard Quarantine Policy): `0`

---

## 4. Parquet Output Verification & Readback

The generated Parquet file in `D:\Study\Code\Apache\Flight_Analyzt\staging\smoke_2016_micro_20261018_110720\` was independently inspected via PyArrow:
- **Total Physical Files:** 1 (`part-00000.parquet`)
- **Total Readback Rows:** `1,000` (Matches expected row count `1,000` exactly)
- **Task Attempts Directory:** `_task_attempts` directory was cleaned up with zero leftover attempt or temporary files.
- **Publication Pointer:** Production `latest/` pointer was NOT updated (isolated staging verification only).

---

## 5. Phase 3 Conclusion

Micro-smoke execution completed cleanly in 7.19 seconds with 100% row accounting conservation and schema compliance, confirming pipeline readiness for Phase 4 month-smoke testing.
