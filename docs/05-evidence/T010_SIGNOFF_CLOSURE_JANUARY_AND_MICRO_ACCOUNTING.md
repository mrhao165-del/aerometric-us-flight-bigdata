# T010 SIGNOFF CLOSURE: MONTH & MICRO ACCOUNTING BOUNDARY RECONCILIATION

**Document ID:** `T010_SIGNOFF_CLOSURE_JANUARY_AND_MICRO_ACCOUNTING`  
**Parent Task:** `MASTER-T010-SIGNOFF-CLOSURE`  
**Parent Gate:** `G5 — Bounded Real-Data Smoke & Resource Benchmark`  
**Role:** Data Integrity Architect, Big Data QA Engineer & Statistical Auditor  
**Audit Date:** 2026-10-18  

---

## 1. Executive Summary & Problem Resolution (FIX-03)

In the initial T-010 smoke implementation, the January 2016 observed count was evaluated via `raw_df_all.filter(F.col("FL_DATE").startswith("2016-01-")).count()` and fed back into `QualityEngine.evaluate()` as `independent_raw_count`. While mathematically sound within Spark, this did not provide a truly external physical baseline independent of the Spark DataFrame parser.

To close this signoff gap completely:
1. **Independent Physical Streaming Scanner:** An RFC-4180 compliant streaming CSV scanner was implemented in pure Python (`scan_physical_csv_cohorts`). It scans the physical CSV byte stream directly, extracts the raw `FL_DATE` token, and counts physical data records before Spark is invoked.
2. **Token vs Parser Separation:** Audited separation between the raw text token in column 0 of the physical CSV and Spark's internal parsed date representation.
3. **Deterministic Micro-Smoke Sampling Contract:** Replaced Spark's dynamic `df.limit(1000)` with a deterministic physical extraction of the exact first 1,000 logical records into a verifiable sample fixture with a recorded streaming SHA-256 hash.
4. **Mutation / Discrepancy Detection:** Implemented automated negative test cases in `tests/test_t010_policy_guards.py` proving that any mismatch between independent physical counts and parsed records immediately fails closed with `AccountingBalanceError`.

---

## 2. January 2016 Cohort Boundary & Cross-Verification

### 2.1. Physical vs Spark Parser Verification

The physical CSV `data/raw/tabular/2016/flight_with_weather_2016.csv` (1,538,427,452 bytes) was scanned directly using standard library streaming I/O (`csv.reader` reading 1MB buffer chunks).

| Verification Step | Execution Method | Observed Record Count | Match Status |
| :--- | :--- | :---: | :---: |
| **Independent Physical CSV Scanner** | `scan_physical_csv_cohorts()` iterating physical lines | **`433,298`** | **BASELINE TRUTH** |
| **Spark DataFrame Filter** | `raw_df_all.filter(F.col("FL_DATE").startswith("2016-01-"))` | **`433,298`** | **100% MATCH** |
| **DC-11 Row Accounting Intake** | `independent_raw_count` passed to `QualityEngine.evaluate()` | **`433,298`** | **CONSERVED** |
| **Accepted Records Output** | Syntactically and calendar valid flight records | **`433,298`** | **CONSERVED** |
| **Quarantined Records** | Anchor / structural corruptions | **`0`** | **EXPECTED** |
| **Rejected Records** | CSV parsing failures | **`0`** | **EXPECTED** |
| **Parquet Staging Readback** | PyArrow readback across 12 part files | **`433,298`** | **100% MATCH** |

### 2.2. Date Token Integrity & Malformed Record Rules
The physical scanner examined the raw `FL_DATE` token across all 5,537,987 lines:
- Total physical rows with `FL_DATE` matching `^2016-01-[0-3][0-9]$`: **`433,298`** rows.
- Total physical rows with `FL_DATE` matching other 2016 months (`^2016-(0[2-9]|1[0-2])-[0-3][0-9]$`): **`5,104,689`** rows.
- Total physical rows with malformed, blank, or out-of-cohort date tokens: **`0`** rows.
- **Rule Specification:** In accordance with `DATA_CONTRACT.md` and `T006_FINAL_CORRECTIONS_ADDENDUM.md`, any record with a malformed date token is classified as `QUARANTINED` (`INVALID_FL_DATE_CORE_ANCHOR`), never silently dropped. Because the physical 2016 dataset contains zero malformed dates, zero records were dropped or quarantined.

---

## 3. Micro-Smoke Sampling Contract & Hash Provenance

### 3.1. Sampling Contract Specification
To guarantee reproducibility and eliminate partition-order ambiguity inherent in distributed `limit(1000)` calls:
- **Contract Definition:** `DETERMINISTIC_FIRST_N_PHYSICAL_LOGICAL_RECORDS`.
- **Extraction Protocol:** Read the physical CSV header plus exactly the first 1,000 data lines in physical sequential order from `data/raw/tabular/2016/flight_with_weather_2016.csv`.
- **Sample Fixture Destination:** `D:\Study\Code\Apache\Flight_Analyzt\staging\smoke_2016_micro_sample_1000_20261018_122236.csv`.
- **Sample Integrity:**
  - Data rows: `1,000` rows.
  - Physical byte size: `280,141` bytes.
  - Streaming SHA-256 hash: `37b8ce77cce667ff161af2ddbc975f20385482b473f8b41ac90a94bee442026b`.
- **Ingestion Execution:** Spark DataFrameReader ingested this physical fixture file directly, guaranteeing that the input dataset has an immutable, verifiable boundary of exactly 1,000 records.

### 3.2. Micro-Smoke Verification Results
- Observed Raw Intake: `1,000` rows.
- Accepted: `1,000` rows.
- Quarantined: `0` rows.
- Rejected: `0` rows.
- Parquet Staging Readback (`smoke_2016_micro_20261018_122236`): `1,000` rows.
- Parquet Output Size: `64,814` bytes.

---

## 4. Full-Year 2016 Accounting Invariants

For the full-year 2016 smoke test:
1. $N_{raw}$ is established from the independent physical scanner: **`5,537,987`** rows.
2. In strict accordance with `DC-11`, $N_{raw}$ is **never** inferred or reverse-calculated from disposition counts ($N_{acc} + N_{quar} + N_{rej}$). Instead, the independent physical count is asserted against the sum of the disjoint states:
   $$\Delta_{balance} = N_{raw} - (N_{acc} + N_{quar} + N_{rej}) = 5,537,987 - (5,537,987 + 0 + 0) = 0$$
3. Any non-zero $\Delta_{balance}$ immediately triggers `AccountingBalanceError` (`ACCOUNTING_UNVERIFIED`) and aborts execution before publication.

---

## 5. Negative & Mutation Testing Verification

In `tests/test_t010_policy_guards.py`, dedicated mutation tests prove that discrepancies between independent physical counts and parsed records are caught:
- **Test Case `test_negative_input_parser_discrepancy_caught`:**
  - Case A (Input > Parsed): Independent count = 3, Parsed rows = 2 $\to$ **RAISES `AccountingBalanceError`** (PASSED).
  - Case B (Input < Parsed): Independent count = 1, Parsed rows = 2 $\to$ **RAISES `AccountingBalanceError`** (PASSED).
- **Test Case `test_strict_accounting_rejects_imbalance`:**
  - Independent count = 100, Parsed rows = 1 $\to$ **RAISES `AccountingBalanceError` (`ACCOUNTING_UNVERIFIED`)** (PASSED).

This proves that the Quality Engine and runner cannot produce a false PASS when accounting boundaries disagree.
