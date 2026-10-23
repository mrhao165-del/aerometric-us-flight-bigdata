# T008-FINAL-EXIT: Metric Validity ANSI Mode Verification & StringType Safety

**Deliverable ID:** `T008-DELIV-EXIT-01`  
**Task:** `MASTER-T008-FINAL-EXIT`  
**Parent Task:** `T-008 — Data Quality, Disjoint Row Accounting & Quarantine Engine`  
**Gate:** `G4`  
**Timestamp:** `2026-10-18T15:52:00+07:00`  
**Status:** `VERIFIED_PASS`  
**Authority:** `DATA_CONTRACT.md` (DC-11, DC-12), `KPI_SPEC.md`, `G2-EXC-001`, `G3-COND-B`

---

## 1. Executive Summary

During independent QA audit of T-008, a critical edge-case was identified: when the Data Quality Engine (`QualityEngine.evaluate()`) evaluates downstream of `RawCsvReader` on a raw `StringType` DataFrame, evaluating numeric predicates directly against string columns (e.g. `DEP_DELAY="UNKNOWN_DELAY"`) under Spark ANSI mode (`spark.sql.ansi.enabled=true`) could trigger runtime `SparkNumberFormatException: [CAST_INVALID_INPUT] The value 'UNKNOWN_DELAY' of the type STRING cannot be cast to DOUBLE because it is malformed.`

This document records the design, implementation, and rigorous verification of **FIX-01**:
1. Implementation of native `try_cast(DoubleType())` column resolution in `src/flight_pipeline/quality/predicates.py`.
2. Safe evaluation across all 7 CORE measures on both raw `StringType` and curated `DoubleType` inputs.
3. Verification that metric invalidity decrements `count_metric_valid` without quarantining the flight record (DC-12).
4. Preservation of signed negative delays (early arrivals/departures).
5. Comprehensive unit test verification in `test_qual_13_ansi_mode_safe_metric_predicates_on_raw_strings` executed under `spark.sql.ansi.enabled=true`.

---

## 2. Technical Architecture of FIX-01

### 2.1 Native Safe Numeric Resolution
In `src/flight_pipeline/quality/predicates.py`, a dedicated numeric resolver `_resolve_numeric_col` was introduced:

```python
def _resolve_numeric_col(col_or_name: Union[str, Column]) -> Column:
    """
    Helper to convert column name or Column object to a safe double Column.
    Uses try_cast(DoubleType()) to ensure resilience against malformed strings
    and prevents NumberFormatException when spark.sql.ansi.enabled is True.
    """
    c = _resolve_col(col_or_name)
    return c.try_cast(DoubleType())
```

### 2.2 Complete Finite Numeric Predicate
```python
def is_finite_numeric(col_or_name: Union[str, Column]) -> Column:
    """
    Complete finite numeric predicate safe across all Spark versions and Catalyst optimizers.
    Returns True iff the column is NOT NULL, NOT NaN, and NOT +/- Infinity.
    Safely handles both raw StringType and curated DoubleType inputs under Spark ANSI mode.
    """
    c = _resolve_numeric_col(col_or_name)
    return c.isNotNull() & ~F.isnan(c) & ~c.isin(float("inf"), float("-inf"))
```

### 2.3 Strict Domain Boundary Enforcement
For domain-bounded metrics (taxi times $\ge 0.0$, elapsed and air times $> 0.0$), `F.coalesce` wraps the comparison to ensure strict 2-valued boolean Catalyst semantics without null propagation:

```python
def is_valid_taxi_out(col_or_name: Union[str, Column] = "TAXI_OUT") -> Column:
    c = _resolve_numeric_col(col_or_name)
    return is_finite_numeric(c) & F.coalesce(c >= 0.0, F.lit(False))

def is_valid_taxi_in(col_or_name: Union[str, Column] = "TAXI_IN") -> Column:
    c = _resolve_numeric_col(col_or_name)
    return is_finite_numeric(c) & F.coalesce(c >= 0.0, F.lit(False))

def is_valid_air_time(col_or_name: Union[str, Column] = "AIR_TIME") -> Column:
    c = _resolve_numeric_col(col_or_name)
    return is_finite_numeric(c) & F.coalesce(c > 0.0, F.lit(False))

def is_valid_actual_elapsed_time(col_or_name: Union[str, Column] = "ACTUAL_ELAPSED_TIME") -> Column:
    c = _resolve_numeric_col(col_or_name)
    return is_finite_numeric(c) & F.coalesce(c > 0.0, F.lit(False))

def is_valid_crs_elapsed_time(col_or_name: Union[str, Column] = "CRS_ELAPSED_TIME") -> Column:
    c = _resolve_numeric_col(col_or_name)
    return is_finite_numeric(c) & F.coalesce(c > 0.0, F.lit(False))
```

---

## 3. Truth Table Across Input Variations

| Input Value (StringType / DoubleType) | `try_cast(DoubleType())` | `is_finite_numeric` | Domain Check | Predicate Outcome | Action on Flight Record |
|---|---|---|---|---|---|
| `"10.0"` / `10.0` | `10.0` | `True` | N/A | `True` | Accepted, metric valid |
| `"-15.0"` / `-15.0` (Delay) | `-15.0` | `True` | N/A | `True` (Signed delay preserved) | Accepted, metric valid |
| `"-5.0"` (Taxi time) | `-5.0` | `True` | `< 0.0` | `False` | Accepted, metric excluded |
| `"0.0"` (Air time) | `0.0` | `True` | `<= 0.0` | `False` | Accepted, metric excluded |
| `"UNKNOWN_DELAY"` | `NULL` | `False` (`isNotNull` fails) | `False` | `False` | Accepted, metric excluded |
| `"NA"` / `""` / `None` | `NULL` | `False` | `False` | `False` | Accepted, metric excluded |
| `"NaN"` / `float('nan')` | `NaN` or `NULL` | `False` (`~isnan` fails) | `False` | `False` | Accepted, metric excluded |
| `"Infinity"` / `float('inf')` | `+Inf` | `False` (`~isin` fails) | `False` | `False` | Accepted, metric excluded |
| `"-Infinity"` / `float('-inf')` | `-Inf` | `False` (`~isin` fails) | `False` | `False` | Accepted, metric excluded |

---

## 4. Test Verification Evidence

The test `test_qual_13_ansi_mode_safe_metric_predicates_on_raw_strings` in `tests/test_t008_quality_engine.py`:
1. Sets `spark.sql.ansi.enabled = true`.
2. Creates synthetic CSV containing 2 records:
   - Row 1: Valid numeric strings across all 7 CORE measures with negative delays (`dep_delay="-15.0"`, `arr_delay="-20.0"`, `taxi_out="12.0"`, `taxi_in="6.0"`, `air_time="300.0"`, `actual_elapsed="318.0"`, `crs_elapsed="330.0"`).
   - Row 2: Malformed tokens across all measures (`dep_delay="UNKNOWN_DELAY"`, `arr_delay="NA"`, `taxi_out="BAD_NUM"`, `taxi_in="-5.0"`, `air_time="0.0"`, `actual_elapsed="INVALID"`, `crs_elapsed="-10.0"`).
3. Reads data via `RawCsvReader` (yielding raw StringType columns).
4. Invokes `QualityEngine.evaluate(raw_df, independent_raw_count=2)`.
5. Confirms:
   - **No runtime exception or NumberFormatException.**
   - Both records are `ACCEPTED` (`result.accepted_count == 2`, `result.quarantined_count == 0`, `result.rejected_count == 0`).
   - Disjoint row accounting balance strictly verified (`2 == 2 + 0 + 0`).
   - For all 7 CORE measures: `count_records == 2`, `count_metric_valid == 1`, `metric_valid_rate == 0.5`.
   - Output boolean validity columns match ground truth: Row 1 all `True`, Row 2 all `False`.
6. Restores original ANSI configuration in `finally` block.

---

## 5. Verdict

**STATUS: PASS.** FIX-01 is completely verified and provides fail-safe, ANSI-compliant metric evaluation on raw input data.
