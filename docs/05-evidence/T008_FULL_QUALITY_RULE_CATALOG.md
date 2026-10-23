# T008 FULL QUALITY RULE CATALOG & TRACEABILITY MATRIX

**Document ID:** `T008_FULL_QUALITY_RULE_CATALOG`  
**Parent Task:** `T-008 — Data Quality, Disjoint Row Accounting & Quarantine Engine`  
**Parent Gate:** `G4`  
**Classification:** `TECHNICAL_SPECIFICATION_AND_TRACEABILITY_MATRIX`  
**Date:** 2026-10-18  

---

## 1. PURPOSE & ARCHITECTURE

This catalog formally defines all data quality rules implemented in `flight_pipeline.quality.catalog`. Every rule provides complete end-to-end traceability to canonical project contracts, governance authorities, architectural specifications, and synthetic test cases.

---

## 2. FORMAL RULE CATALOG

| Rule ID | Rule Name | Scope | Severity | Consequence | Authority | Approval Status | Target Columns | Test Case |
|:---|:---|:---:|:---:|:---:|:---|:---:|:---|:---|
| **QR-REC-01** | `SYNTAX_PARSER_CORRUPTION` | RECORD | ERROR | REJECT | DC-11 / FIX-F06 | APPROVED | `_corrupt_record` | `test_acct_01` |
| **QR-REC-02** | `INVALID_FL_DATE_CORE_ANCHOR` | RECORD | ERROR | QUARANTINE | FP-DEC-007 / FIX-F06 | APPROVED | `FL_DATE` | `test_qual_06` |
| **QR-REC-03** | `SOURCE_YEAR_DATE_MISMATCH` | RECORD | ERROR | QUARANTINE | FIX-F06 / TS-002 | APPROVED | `FL_DATE`, `_source_year` | `test_qual_07` |
| **QR-REC-04** | `MISSING_CARRIER_CORE_ANCHOR` | RECORD | ERROR | QUARANTINE | FIX-F06 / T006 Addendum | APPROVED | `OP_CARRIER` | `test_qual_02` |
| **QR-REC-05** | `MISSING_AIRPORT_CORE_ANCHOR` | RECORD | ERROR | QUARANTINE | FIX-F06 / T006 Addendum | APPROVED | `ORIGIN`, `DEST` | `test_qual_03` |
| **QR-REC-06** | `INVALID_FLIGHT_NUM_CORE_ANCHOR` | RECORD | ERROR | QUARANTINE | FIX-F06 / T006 Addendum | APPROVED | `OP_CARRIER_FL_NUM` | `test_qual_04` |
| **QR-REC-07** | `PROVISIONAL_FLIGHT_NUM_NON_POSITIVE` | RECORD | WARNING | FLAG_ONLY | G3-COND-A / T006 Addendum | **PROVISIONAL** | `OP_CARRIER_FL_NUM` | `test_qual_05`, `test_pol_04` |
| **QR-REC-08** | `WEATHER_DATA_ABSENCE_ALLOWED` | RECORD | INFO | FLAG_ONLY | FP-DEC-017 / DC-07 | APPROVED | `O_TEMP`..`D_WSPD` | `test_qual_11` |
| **QR-MET-01** | `VALID_ARR_DELAY_METRIC` | METRIC | INFO | METRIC_INVALID | G2-EXC-001 / DC-12 | APPROVED | `ARR_DELAY` | `test_qual_09` |
| **QR-MET-02** | `VALID_DEP_DELAY_METRIC` | METRIC | INFO | METRIC_INVALID | G2-EXC-001 / DC-12 | APPROVED | `DEP_DELAY` | `test_qual_08`, `test_qual_09` |
| **QR-MET-03** | `VALID_TAXI_OUT_METRIC` | METRIC | INFO | METRIC_INVALID | DC-12 / KPI-07 | APPROVED | `TAXI_OUT` | `test_qual_10` |
| **QR-MET-04** | `VALID_TAXI_IN_METRIC` | METRIC | INFO | METRIC_INVALID | DC-12 / KPI-07 | APPROVED | `TAXI_IN` | `test_qual_10` |
| **QR-MET-05** | `VALID_AIR_TIME_METRIC` | METRIC | INFO | METRIC_INVALID | DC-12 / KPI-08 | APPROVED | `AIR_TIME` | `test_qual_10` |
| **QR-MET-06** | `VALID_ACTUAL_ELAPSED_TIME_METRIC` | METRIC | INFO | METRIC_INVALID | DC-12 / KPI-08 | APPROVED | `ACTUAL_ELAPSED_TIME` | `test_qual_10` |
| **QR-MET-07** | `VALID_CRS_ELAPSED_TIME_METRIC` | METRIC | INFO | METRIC_INVALID | DC-12 / KPI-08 | APPROVED | `CRS_ELAPSED_TIME` | `test_qual_10` |
| **QR-DAT-01** | `CALENDAR_DATE_COVERAGE` | DATASET | WARNING | FLAG_ONLY | OR-05 / FP-DEC-002 | APPROVED | `FL_DATE` | `test_cov_01`..`04` |
| **QR-DAT-02** | `DISJOINT_ROW_ACCOUNTING_BALANCE` | DATASET | ERROR | REJECT | DC-11 / FIX-F02 | APPROVED | `_record_status` | `test_acct_01`..`03` |
| **QR-DAT-03** | `METRIC_COUNT_BOUND_ACCOUNTING` | DATASET | ERROR | REJECT | DC-12 / TS-003 | APPROVED | All 7 CORE metrics | `test_acct_04`..`05` |

---

## 3. PROVISIONAL RULE BOUNDARY (QR-REC-07)
- **Status:** `PROVISIONAL_POLICY_PENDING_REAL_DATA_VALIDATION`.
- **Behavior:** In canonical production configuration, `OP_CARRIER_FL_NUM <= 0` does **NOT** quarantine or reject records. Records remain `ACCEPTED` and receive the flag `PROVISIONAL_FLIGHT_NUM_NON_POSITIVE_G3_COND_A`.
- **Protection:** Attempting to configure hard quarantine without explicit override raises `PolicyViolationError`. Full resolution is deferred to Gate G5 real data BTS validation.
