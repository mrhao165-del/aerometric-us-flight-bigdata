# T011-R3 Numeric Parsing, Non-Finite & Null Distinction Audit

**Project:** US Flight Performance Analysis 2016–2024  
**Task:** T-011 R3 — Provenance Trust Boundary, Numeric Integrity, Lock Recovery & Evidence Correction  
**Parent Gate:** G5 — IN_PROGRESS  
**Component:** BTS TranStats Reconciler (`src/flight_pipeline/kpi/bts_reconciler.py`)  
**Audit Finding Addressed:** R3-F02 (HIGH — Malformed numerics and non-finites masked as `NULL_NULL_AGREEMENT`)  
**Date:** 2026-10-19  
**Status:** COMPLETE / NUMERIC INTEGRITY ENFORCED  

---

## 1. Executive Summary & Defect Remediation

During the independent technical audit of package `T011_R2_REVIEW_PACKAGE.zip`, finding **R3-F02** identified a numeric masking vulnerability in `src/flight_pipeline/kpi/bts_reconciler.py`:

In R2, numeric conversion was handled by a naive helper:
```python
def safe_float(val):
    try:
        return float(val)
    except (ValueError, TypeError):
        return None
```
When a record contained unparseable text (such as `"invalidXYZ"`, `"CORRUPT"`) or non-finite values (`"NaN"`, `"Infinity"`, `float('nan')`, `float('inf')`), `safe_float()` silently coerced them to `None`. When compared against another record that also had malformed or non-finite text (e.g., `"invalidABC"`), the field comparison logic executed:
```python
if d_val is None and b_val is None:
    return MismatchType.NULL_NULL_AGREEMENT
```
This conflated corrupt, unparseable strings with legitimate missing data (true nulls). If another record in the batch had a single valid number for that measure, the measure satisfied the positive numeric sample condition, and the corrupt records were counted as matching agreement, creating a false parity pass.

In T011-R3, this vulnerability has been eliminated. The reconciler now strictly differentiates between genuine nulls, malformed numbers, and non-finites. Any malformed or non-finite numeric measure produces a `MALFORMED_NUMERIC_ERROR` discrepancy and fails reconciliation.

---

## 2. Formal Classification of Numeric Parse Status

R3 introduces the `NumericParseStatus` enum to classify the exact parse state of every measure:

```python
class NumericParseStatus(str, Enum):
    VALID_FINITE_NUMBER = "VALID_FINITE_NUMBER"
    TRUE_NULL = "TRUE_NULL"
    MALFORMED_NUMBER = "MALFORMED_NUMBER"
    NONFINITE_NUMBER = "NONFINITE_NUMBER"
    SCHEMA_MISSING = "SCHEMA_MISSING"
```

### Approved Null Tokens vs. Malformed Strings

Under project policy (aligned with `DATA_CONTRACT.md` and `DECISIONS.md`), only explicit, approved null tokens are recognized as `TRUE_NULL`:
- Python `None`
- Whitespace-trimmed empty string `""`
- Case-insensitive approved null strings: `"na"`, `"null"`, `"none"`, `"nan_rep_none"`

All other string values are evaluated as potential numbers:
- If string parses to a finite float $\in (-\infty, +\infty)$: `VALID_FINITE_NUMBER`.
- If string parses to `NaN` or `+/-Inf`: `NONFINITE_NUMBER`.
- If string fails float parsing (e.g. `"invalidXYZ"`): `MALFORMED_NUMBER`.

---

## 3. Production Source Implementation

### 3.1 Strict Numeric Parsing (`parse_numeric_measure`)

```python
@classmethod
def parse_numeric_measure(cls, rec: Dict[str, Any], col_name: str) -> Tuple[Optional[float], NumericParseStatus]:
    if col_name not in rec:
        return None, NumericParseStatus.SCHEMA_MISSING
    val = rec[col_name]
    if val is None:
        return None, NumericParseStatus.TRUE_NULL
    if isinstance(val, (int, float)):
        if math.isnan(val) or math.isinf(val):
            return None, NumericParseStatus.NONFINITE_NUMBER
        return float(val), NumericParseStatus.VALID_FINITE_NUMBER
    val_str = str(val).strip()
    if val_str.lower() in APPROVED_NULL_STRINGS:
        return None, NumericParseStatus.TRUE_NULL
    try:
        f = float(val_str)
        if math.isnan(f) or math.isinf(f):
            return None, NumericParseStatus.NONFINITE_NUMBER
        return f, NumericParseStatus.VALID_FINITE_NUMBER
    except (ValueError, TypeError):
        return None, NumericParseStatus.MALFORMED_NUMBER
```

### 3.2 Comparison Logic (`compare_single_field`)

Field comparison strictly evaluates parse statuses:

1. **Both Genuine Nulls:**
   If `d_status == TRUE_NULL` and `b_status == TRUE_NULL`:
   Returns `MismatchType.NULL_NULL_AGREEMENT`.
2. **Malformed or Non-Finite Errors:**
   If either side has status `MALFORMED_NUMBER` or `NONFINITE_NUMBER`:
   Returns `MismatchType.MALFORMED_NUMERIC_ERROR`. This increments `stats["malformed_numeric"]`, marks `all_fields_match = False`, and causes `reconciliation_verdict` to fail closed.
3. **Missingness Mismatch:**
   If one side is `TRUE_NULL` and the other is `VALID_FINITE_NUMBER`:
   Returns `MismatchType.MISSINGNESS_MISMATCH`.
4. **Value & Rounding Comparison:**
   If both sides are `VALID_FINITE_NUMBER`: evaluates absolute difference against tolerance ($10^{-4}$).

---

## 4. Verification Evidence & Counterexample Guards

Permanent regression suite `tests/test_t011_r3_counterexamples.py` (`TestT011R3NumericIntegrity`) verifies all edge cases:

1. `test_r3_f02_malformed_string_vs_malformed_string`: PASS (`"invalidXYZ"` vs `"invalidABC"` yields `MALFORMED_NUMERIC_ERROR`).
2. `test_r3_f02_malformed_string_vs_valid_number`: PASS (`"invalidXYZ"` vs `10.0` yields `MALFORMED_NUMERIC_ERROR`).
3. `test_r3_f02_string_nan_vs_string_nan`: PASS (`"NaN"` vs `"nan"` yields `MALFORMED_NUMERIC_ERROR`, `NONFINITE_NUMBER`).
4. `test_r3_f02_string_inf_vs_string_inf`: PASS (`"Infinity"` vs `"-Inf"` yields `MALFORMED_NUMERIC_ERROR`, `NONFINITE_NUMBER`).
5. `test_r3_f02_float_nan_vs_float_nan`: PASS (`float('nan')` yields `MALFORMED_NUMERIC_ERROR`).
6. `test_r3_f02_approved_null_strings_agree`: PASS (`""`, `"NA"`, `"null"`, `"None"`, `None` pairwise yield `NULL_NULL_AGREEMENT`).
7. `test_r3_f02_null_vs_valid_number`: PASS (`None` vs `10.0` yields `MISSINGNESS_MISMATCH`).

---

## 5. Conclusion

Finding **R3-F02** is **RESOLVED / CLOSED**. Corrupt or malformed strings and non-finite numeric representations can no longer be masked as null agreements. Numeric integrity across all 7 CORE measures is strictly enforced.
