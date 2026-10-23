# T010_FULL_JANUARY_SMOKE_RESULTS.md — Phase 4 Month-Smoke on January 2016 Real Data

**Gate:** G5  
**Task:** T-010 — Bounded Real-Data Smoke & Resource Benchmark  
**Author:** Senior PySpark Data Quality Engineer  
**Execution Timestamp:** 2026-10-18T11:07:20+00:00 (2026-10-18T18:07:20+07:00)  
**Run ID:** `smoke_2016_jan_20261018_110720`  
**Status:** PASS (CONTROLLED)  

---

## 1. Overview & Scope

Phase 4 scaled testing from micro-smoke to a full single calendar month: **January 2016** (`2016-01-01` to `2016-01-31`).

This verified:
1. Scaling to hundreds of thousands of real flight records (`433,298` records).
2. Date coverage evaluation via `DateCoverageAnalyzer` for all 31 days of January.
3. Submetric validity accounting across all 7 CORE measures (DC-12).
4. Multi-partition Parquet writing across 12 partitions with two-phase task staging.
5. PyArrow readback verification of multi-file Parquet dataset.

---

## 2. January 2016 Measured Metrics

| Metric Category | Parameter | Measured Value | Unit / Status |
| :--- | :--- | :--- | :--- |
| **Execution** | Wall-clock Duration | `24.709` | seconds |
| **Memory** | Peak Driver RSS | `125,444,096` (119.63) | bytes (MB) |
| **Row Accounting** | Observed Raw Records ($N_{\text{raw}}$) | `433,298` | rows |
| **Row Accounting** | Accepted Records ($N_{\text{accepted}}$) | `433,298` | rows |
| **Row Accounting** | Quarantined Records ($N_{\text{quarantined}}$) | `0` | rows |
| **Row Accounting** | Rejected Records ($N_{\text{rejected}}$) | `0` | rows |
| **Row Accounting** | DC-11 Accounting Balance | `433,298 = 433,298 + 0 + 0` | **BALANCED (True)** |
| **Row Accounting** | Ingest Acceptance Rate | `1.0000` (100.0%) | percentage |
| **Parquet Staging** | Staging Directory | `D:\Study\Code\Apache\Flight_Analyzt\staging\smoke_2016_jan_20261018_110720` | NTFS directory |
| **Parquet Staging** | Generated Parquet Files | `12` | part-00000..00011.parquet |
| **Parquet Staging** | Total Parquet Bytes on Disk | `23,124,812` (22.05 MB) | bytes (MB) |
| **Parquet Staging** | Readback Rows via PyArrow | `433,298` | rows |
| **Compression** | Snappy Compression Ratio | `~5.1:1` | ratio |

---

## 3. Calendar Date Coverage Analysis (January 2016)

Evaluated via `DateCoverageAnalyzer.analyze()`:
- **Target Year:** `2016` (Leap Year: 366 expected days)
- **Observed Days in January:** Exactly `31` days (`2016-01-01` through `2016-01-31`).
- **Missing Days in January:** `0` missing days within the January date range.
- **Out of Range Dates:** `0` dates outside 2016.
- **Coverage Ratio (Full Year Baseline):** `31 / 366 = 0.0847` (Normal expected for month-smoke slice).
- **March 2024 Defect Check:** `is_march_missing = False` (OR-05 defect not present).

---

## 4. DC-12 Submetric Validity Accounting (7 CORE Measures)

Evaluated on the `433,298` accepted January 2016 records:

| Measure Name | Total Accepted Records | Count Metric Valid | Excluded / Invalid Count | Metric Valid Rate |
| :--- | :--- | :--- | :--- | :--- |
| **ARR_DELAY** | `433,298` | `433,298` | `0` | **100.0%** |
| **DEP_DELAY** | `433,298` | `433,298` | `0` | **100.0%** |
| **TAXI_OUT** | `433,298` | `433,298` | `0` | **100.0%** |
| **TAXI_IN** | `433,298` | `433,298` | `0` | **100.0%** |
| **AIR_TIME** | `433,298` | `433,298` | `0` | **100.0%** |
| **ACTUAL_ELAPSED_TIME** | `433,298` | `433,298` | `0` | **100.0%** |
| **CRS_ELAPSED_TIME** | `433,298` | `433,298` | `0` | **100.0%** |

> [!NOTE]
> All 7 CORE performance measures demonstrated 100% finite numeric validity across January 2016 flights, with zero NaN, Infinity, or unparseable string values.

---

## 5. G3-COND-A Provisional Profiling (January 2016)

- Total Records Profiled: `433,298`
- Non-Positive Flight Numbers (`OP_CARRIER_FL_NUM <= 0`): `0`
- Zero Flight Numbers: `0`
- Negative Flight Numbers: `0`
- Affected Carriers: None (`{}`)
- Simulated Quarantine under Hard Policy: `0`

---

## 6. Phase 4 Conclusion

Month-smoke completed in 24.71 seconds, validating 433,298 records across all 31 days of January 2016 with 100% metric validity, balanced row accounting, and successful Parquet multi-part write and readback.
