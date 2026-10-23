# T008 FULL DC-11 & DC-12 ROW AND METRIC ACCOUNTING REPORT

**Document ID:** `T008_FULL_DC11_DC12_ACCOUNTING_REPORT`  
**Parent Task:** `T-008 — Data Quality, Disjoint Row Accounting & Quarantine Engine`  
**Parent Gate:** `G4`  
**Classification:** `TECHNICAL_AUDIT_AND_ACCOUNTING_VERIFICATION`  
**Date:** 2026-10-18  

---

## 1. PURPOSE & PRINCIPLES

This report verifies the implementation of the three-state disjoint row accounting model (`DC-11`) and the per-submetric validity accounting model (`DC-12`) implemented in `QualityAccountingEngine` and `RowAccounting`/`MetricAccounting`.

### Key Governance Principles:
1. **Independent Verification:** $N_{raw}$ must be observed independently from source file scanning or canonical manifests. It is never tautologically defined as the sum $N_{acc} + N_{quar} + N_{rej}$.
2. **Fail-Closed Balance:** Any discrepancy ($N_{raw} \neq N_{acc} + N_{quar} + N_{rej}$) raises `AccountingBalanceError` and halts publication.
3. **No 4th Accounting State:** Every record is strictly ACCEPTED, QUARANTINED, or REJECTED.
4. **Zero Denominator Robustness:** Denominators with 0 records return `None` (not `0.0` or division-by-zero exceptions).

---

## 2. DC-11 THREE-STATE DISJOINT ROW ACCOUNTING

### 2.1. Mathematical Formula
$$N_{\text{raw}} = N_{\text{accepted}} + N_{\text{quarantined}} + N_{\text{rejected}}$$
$$\text{with } N_{\text{raw}} \ge 0, N_{\text{accepted}} \ge 0, N_{\text{quarantined}} \ge 0, N_{\text{rejected}} \ge 0$$

### 2.2. Acceptance Rate Formula
$$\text{ingest\_acceptance\_rate} = \begin{cases} \frac{N_{\text{accepted}}}{N_{\text{raw}}}, & \text{if } N_{\text{raw}} > 0 \\ \text{None}, & \text{if } N_{\text{raw}} = 0 \end{cases}$$

### 2.3. Verification Implementation
In `QualityAccountingEngine.compute_and_verify_row_accounting()`:
1. Performs a single aggregation pass over `_record_status`.
2. Validates that no unknown status labels exist.
3. Constructs `RowAccounting` with independent ground-truth raw count.
4. Asserts `accounting.is_balanced() == True`, otherwise raises `AccountingBalanceError`.

---

## 3. DC-12 METRIC ACCOUNTING

### 3.1. Mathematical Formula
$$\text{count\_metric\_valid}_M \le \text{count\_records}$$
$$\text{excluded\_count}_M = \text{count\_records} - \text{count\_metric\_valid}_M$$
$$\text{metric\_valid\_rate}_M = \begin{cases} \frac{\text{count\_metric\_valid}_M}{\text{count\_records}}, & \text{if } \text{count\_records} > 0 \\ \text{None}, & \text{if } \text{count\_records} = 0 \end{cases}$$

### 3.2. Seven CORE Measures Monitored
1. `ARR_DELAY`: Arrival delay (minutes, signed finite numeric)
2. `DEP_DELAY`: Departure delay (minutes, signed finite numeric)
3. `TAXI_OUT`: Taxi-out time (minutes, finite numeric $\ge 0.0$)
4. `TAXI_IN`: Taxi-in time (minutes, finite numeric $\ge 0.0$)
5. `AIR_TIME`: Airborne time (minutes, finite numeric $> 0.0$)
6. `ACTUAL_ELAPSED_TIME`: Actual elapsed flight time (minutes, finite numeric $> 0.0$)
7. `CRS_ELAPSED_TIME`: Scheduled elapsed flight time (minutes, finite numeric $> 0.0$)

---

## 4. SYNTHETIC VERIFICATION EVIDENCE

The accounting engine was verified through the following passing tests:
- `test_acct_01_three_state_disjoint_balance_success`: Verified balanced 3-state synthetic cohort.
- `test_acct_02_independent_raw_count_discrepancy_fails_closed`: Verified fail-closed error on discrepancy.
- `test_acct_03_negative_accounting_counts_rejected`: Verified negative counts are rejected.
- `test_acct_04_metric_valid_bound_enforced`: Verified valid metric count cannot exceed total count.
- `test_acct_05_zero_denominator_handled_cleanly`: Verified clean `None` return on zero denominator.
- `test_acct_06_multi_source_reconciliation`: Verified multi-source per-year and aggregate reconciliation.
