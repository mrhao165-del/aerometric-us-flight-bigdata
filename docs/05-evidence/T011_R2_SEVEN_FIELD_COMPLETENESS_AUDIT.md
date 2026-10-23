# T011-R2 Seven-Field Completeness & Schema Missing Column Audit

**Project:** US Flight Performance Analysis 2016–2024  
**Task:** T-011 R2 — Targeted Parity Hardening and Evidence Correction  
**Parent Gate:** G5 — IN_PROGRESS  
**Component:** BTS TranStats Reconciler (`src/flight_pipeline/kpi/bts_reconciler.py`)  
**Audit Finding Addressed:** R2-F02 (Single numeric measure satisfying global condition when 6 measures are absent)  
**Date:** 2026-10-19  
**Status:** COMPLETE / ZERO-TOLERANCE SCHEMA CONTRACT ENFORCED  

---

## 1. Executive Summary & Defect Remediation

During independent audit review of T011-R1, finding **R2-F02** discovered that if 6 of the 7 CORE measures were completely absent from the dataset or BTS records, `BtsTranStatsReconciler` evaluated `d_rec.get(col)` as `None` and `b_rec.get(col)` as `None`. It categorized these absent columns as `MismatchType.NULL_NULL_AGREEMENT`.

Consequently, if even a single measure (e.g. `ARR_DELAY`) matched with a single numeric value, the global condition `(exact + rounding) > 0` and `mismatch == 0` was satisfied, improperly awarding parity across all 7 measures.

In T011-R2, this schema omission vulnerability has been completely resolved:
1. **Explicit Schema Column Verification:** `compare_single_field` checks whether the required columns are present in the record dictionaries (`dataset_field in dataset_record` and `bts_field in bts_record`). If either is missing, it explicitly returns `MismatchType.SCHEMA_MISSING_COLUMN`.
2. **Mandatory Non-Zero Numeric Observations:** Every single one of the 7 CORE measures must have `numeric_sample_count > 0` to be eligible for official parity. If any measure has 0 numeric observations (even if null agreement is 100%), parity fails closed.

---

## 2. Core Measure Field Mapping Specification

The 7 canonical CORE measures audited under TS-018 are:

| Metric Index | Canonical Pipeline Field | BTS TranStats Column Name | Metric Physical Role | Tolerance |
| :---: | :--- | :--- | :--- | :---: |
| 1 | `ARR_DELAY` | `ArrDelay` | Arrival delay in minutes | 1e-4 |
| 2 | `DEP_DELAY` | `DepDelay` | Departure delay in minutes | 1e-4 |
| 3 | `TAXI_OUT` | `TaxiOut` | Taxi out duration in minutes | 1e-4 |
| 4 | `TAXI_IN` | `TaxiIn` | Taxi in duration in minutes | 1e-4 |
| 5 | `AIR_TIME` | `AirTime` | Airborne duration in minutes | 1e-4 |
| 6 | `ACTUAL_ELAPSED_TIME` | `ActualElapsedTime` | Gate-to-gate elapsed time | 1e-4 |
| 7 | `CRS_ELAPSED_TIME` | `CRSElapsedTime` | Scheduled elapsed time | 1e-4 |

---

## 3. Strict Classification & Completeness Rules

### 3.1 Field Status Resolution Hierarchy

In `compare_single_field(dataset_field, bts_field, dataset_record, bts_record)`:
1. **Missing Column Check:** If `dataset_field not in dataset_record` or `bts_field not in bts_record`:
   - Returns `MismatchType.SCHEMA_MISSING_COLUMN`.
   - Increments `missing_column` counter and `mismatch` counter.
   - Sets `summary.schema_valid = False` and `all_fields_match = False`.
2. **Null-Null Agreement:** If both fields are physically present in the record dictionaries but have `None` or empty string values:
   - Returns `MismatchType.NULL_NULL_AGREEMENT`.
   - Increments `null_null_agreement`.
   - Does NOT increment `numeric_sample_count`.
3. **One-Sided Null:** If one side is numeric and the other is `None`:
   - Returns `MismatchType.ONE_NULL_ONE_VALUE`.
   - Increments `mismatch`.
4. **Numeric Comparison:** If both sides are parseable numbers:
   - Evaluates `abs(d_val - b_val) <= tolerance`.
   - If exact difference is zero: `MismatchType.EXACT_MATCH`, increments `exact_match` and `numeric_sample_count`.
   - If difference within tolerance: `MismatchType.ROUNDING_DIFF`, increments `rounding_diff` and `numeric_sample_count`.
   - If difference > tolerance: `MismatchType.VALUE_MISMATCH`, increments `mismatch`.

### 3.2 Global Parity Prerequisite: All 7 Measures Must Have Numeric Data

In `reconcile()`:
```python
measures_with_zero_numeric = [
    f_name for f_name, stats in summary.field_statistics.items()
    if stats["numeric_sample_count"] == 0
]
all_seven_measures_have_numeric = len(measures_with_zero_numeric) == 0

summary.schema_valid = (total_missing_col == 0) and (summary.total_dataset_records > 0) and (summary.total_bts_records > 0)

matched_parity_ok = bool(
    not has_mismatch
    and summary.unique_key_matches > 0
    and all_seven_measures_have_numeric
)
```

If `all_seven_measures_have_numeric is False`, `matched_parity_ok` is strictly `False`, blocking any authentic or synthetic parity verdict.

---

## 4. Comprehensive Unit Test Evidence

In `tests/test_t011_ts018_bts_parity.py`, 15 targeted tests rigorously verify the seven-field completeness contract:

| Test Name | Scenario Tested | Expected & Verified Outcome |
| :--- | :--- | :--- |
| `test_01_exact_match_all_seven_measures` | All 7 measures have identical float values | 7 exact matches, numeric_sample_count=1 each, `reconciliation_verdict=SYNTHETIC_RECONCILER_VERIFIED_AUTHENTIC_BTS_PENDING` |
| `test_02_rounding_difference_within_tolerance` | Small diff (1e-5 <= 1e-4) | `ROUNDING_DIFF` recorded, parity passes |
| `test_03_value_mismatch_exceeds_tolerance` | Diff (0.1 > 1e-4) on `ARR_DELAY` | `VALUE_MISMATCH`, parity fails closed |
| `test_04_one_null_one_value_detected` | `TAXI_IN` is 7.0 in dataset, `None` in BTS | `ONE_NULL_ONE_VALUE`, parity fails closed |
| `test_05_both_null_agreement_detected` | Both sides have `None` for `TAXI_OUT` | `NULL_NULL_AGREEMENT`, numeric_sample_count=0 for TAXI_OUT -> fails 7-measure completeness |
| `test_06_unmatched_records_detected` | Dataset has extra unmapped row | `UNMATCHED_IN_DATASET`, parity fails |
| `test_07_ambiguous_duplicate_keys_detected` | Two identical flights in BTS | `AMBIGUOUS_DUPLICATE`, parity fails |
| `test_08_invalid_composite_key_detected` | Negative flight number (-1) | `INVALID_KEY`, parity fails |
| `test_10_missing_column_on_one_side_detected` | `CRS_ELAPSED_TIME` omitted from dataset dict | `SCHEMA_MISSING_COLUMN`, `schema_valid=False`, fails closed |
| `test_11_all_measures_null_fails_numeric_requirement` | All 7 measures are None on both sides | `NULL_NULL_AGREEMENT` for all 7, but `numeric_sample_count=0` -> fails completeness |
| `test_12_single_measure_scale_mismatch_detected` | `AIR_TIME` in seconds (6900) vs minutes (115) | `VALUE_MISMATCH`, fails closed |
| `test_13_sign_inversion_detected` | `DEP_DELAY` is -5.0 vs +5.0 | `VALUE_MISMATCH`, fails closed |

---

## 5. Conclusion

Finding **R2-F02** is **CLOSED / RESOLVED**. Missing columns are never mistaken for null agreement, and parity across all 7 CORE measures requires affirmative numerical verification on every measure without exception.
