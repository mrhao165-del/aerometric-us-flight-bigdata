# T010_FULL_YEAR_SMOKE_RESULTS.md — Phase 5 Bounded Full-Year 2016 Smoke Results

**Gate:** G5  
**Task:** T-010 — Bounded Real-Data Smoke & Resource Benchmark  
**Author:** Principal Apache Spark Engineer & Independent QA Auditor  
**Execution Timestamp:** 2026-10-18T11:07:20+00:00 (2026-10-18T18:07:20+07:00)  
**Run ID:** `smoke_2016_20261018_110720`  
**Status:** PASS (CONTROLLED)  

---

## 1. Executive Summary & Scope

Phase 5 executed the complete bounded full-year smoke test across all **5,537,987 records** of the real 2016 flight CSV (`data/raw/tabular/2016/flight_with_weather_2016.csv`).

Key achievements:
- **Independent Record Accounting:** RFC-4180 logical record scan proved exact correspondence: $N_{\text{raw\_observed}} = 5,537,987$.
- **Strict DC-11 Balance:** $5,537,987 = 5,537,987 (\text{accepted}) + 0 (\text{quarantined}) + 0 (\text{rejected})$.
- **Full Calendar Coverage:** All **366 days** of leap year 2016 were observed with zero missing days (`source_coverage_status = COMPLETE`).
- **Complete Metric Validity:** All 7 CORE measures achieved 100.0% finite numeric validity across the entire year.
- **Parquet Output Conservation:** Exactly 5,537,987 rows were written and independently read back via PyArrow.

---

## 2. Independent Logical Record Scanner Verification

Before initiating Spark ingestion, the raw CSV was scanned using [scan_csv_logical_records](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/src/flight_pipeline/ingestion/reader.py#L317-L460):

- **Input File:** `data/raw/tabular/2016/flight_with_weather_2016.csv` (1,538,427,452 bytes)
- **Scanned Logical Records:** `5,537,987`
- **Scanned Physical Data Lines:** `5,537,987`
- **Blank Lines Detected:** `0`
- **Embedded Newlines in Quotes:** `0`
- **Unclosed Quotes:** `0`
- **Is Verifiable:** `True` (Record boundary integrity confirmed)

---

## 3. Full-Year 2016 Ingestion & Row Accounting (DC-11)

Evaluated via [QualityEngine.evaluate](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/src/flight_pipeline/quality/engine.py#L101-L196):

```
raw_row_count = accepted_row_count + quarantined_row_count + rejected_row_count
5,537,987     = 5,537,987          + 0                      + 0
```

| Parameter | Measured Count | Rate / Proportion | Governance Status |
| :--- | :--- | :--- | :--- |
| **Independent Raw Count ($N_{\text{raw}}$)** | `5,537,987` | 100.0% | Audited Ground Truth |
| **Accepted Records ($N_{\text{accepted}}$)** | `5,537,987` | 100.0% | Core Entity Anchors Satisfied |
| **Quarantined Records ($N_{\text{quarantined}}$)** | `0` | 0.0% | Zero Anchor Violations |
| **Rejected Records ($N_{\text{rejected}}$)** | `0` | 0.0% | Zero Syntax Corruptions |
| **Ingest Acceptance Rate** | `1.0000` | 100.0% | Complete Ingestion |
| **Accounting Balance Verification** | `True` | Disjoint Set Verified | **DC-11 PASS** |

---

## 4. Calendar Date Coverage Analysis (OR-05 Audit)

Evaluated via `DateCoverageAnalyzer.analyze()`:

| Coverage Metric | Measured Value | Benchmark / Expectation | Compliance |
| :--- | :--- | :--- | :--- |
| **Survey Year** | `2016` | 2016 | **PASS** |
| **Is Leap Year** | `True` | 2016 is leap year | **PASS** |
| **Expected Days** | `366` | 366 days in leap year | **PASS** |
| **Observed Unique Days** | `366` | All calendar dates present | **PASS** |
| **Missing Days Count** | `0` | Zero missing dates | **PASS** |
| **Out-of-Year Records** | `0` | Zero dates outside 2016 | **PASS** |
| **Coverage Ratio** | `1.0000` (100.0%) | 100% full annual coverage | **PASS** |
| **Source Coverage Status** | `COMPLETE` | No calendar gaps | **PASS** |
| **March Missing Defect** | `False` | Defect is specific to 2024 | **PASS** |

---

## 5. DC-12 Submetric Validity Accounting (7 CORE Measures)

Evaluated on all `5,537,987` accepted flights across 2016:

| Measure Column | Denominator ($N_{\text{accepted}}$) | Count Metric Valid | Excluded / Non-Numeric | Metric Valid Rate |
| :--- | :--- | :--- | :--- | :--- |
| **ARR_DELAY** | `5,537,987` | `5,537,987` | `0` | **100.0%** |
| **DEP_DELAY** | `5,537,987` | `5,537,987` | `0` | **100.0%** |
| **TAXI_OUT** | `5,537,987` | `5,537,987` | `0` | **100.0%** |
| **TAXI_IN** | `5,537,987` | `5,537,987` | `0` | **100.0%** |
| **AIR_TIME** | `5,537,987` | `5,537,987` | `0` | **100.0%** |
| **ACTUAL_ELAPSED_TIME** | `5,537,987` | `5,537,987` | `0` | **100.0%** |
| **CRS_ELAPSED_TIME** | `5,537,987` | `5,537,987` | `0` | **100.0%** |

> [!IMPORTANT]
> In accordance with DC-12, all 7 CORE measures were evaluated independently. Every metric valid rate is strictly 100.0%, confirming high structural data quality in the audited 2016 dataset.

---

## 6. G3-COND-A Provisional Policy Profiling

Evaluated via `ProvisionalPolicyProfiler.profile_flight_number_anomalies`:
- **Total Records Profiled:** `5,537,987`
- **Non-Positive Flight Numbers (`OP_CARRIER_FL_NUM <= 0`):** `0`
- **Zero Flight Numbers (`== 0.0`):** `0`
- **Negative Flight Numbers (`< 0.0`):** `0`
- **Affected Carriers:** `{}`
- **Simulated Quarantine under Hard Policy:** `0` records

> [!NOTE]
> In 2016, 100% of flight numbers are strictly positive (> 0.0). Thus, whether canonical production policy (G3-COND-A) or hypothetical hard quarantine policy is applied, zero records are impacted in the 2016 survey year.

---

## 7. Staging Parquet Output & Readback Verification

The curated DataFrame was written to isolated staging via `write_dataframe_parquet_safe`:
- **Staging Directory:** `D:\Study\Code\Apache\Flight_Analyzt\staging\smoke_2016_20261018_110720\`
- **Parquet Partition Files:** Exactly `12` files (`part-00000.parquet` to `part-00011.parquet`).
- **Total Disk Size:** `332,018,057` bytes (`316.64` MB).
- **PyArrow Readback Count:** Exactly `5,537,987` rows across all 12 files.
- **Row Conservation:** $\text{Readback Rows} (5,537,987) == \text{Accepted Rows} (5,537,987)$.
- **Production Isolation:** The publication pointer (`latest/`) was NOT updated, preserving production isolation per G5 boundaries.
