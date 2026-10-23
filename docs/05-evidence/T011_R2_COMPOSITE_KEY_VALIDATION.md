# T011-R2 Composite Key Validation & Falsy Masking Audit

**Project:** US Flight Performance Analysis 2016–2024  
**Task:** T-011 R2 — Targeted Parity Hardening and Evidence Correction  
**Parent Gate:** G5 — IN_PROGRESS  
**Component:** BTS TranStats Reconciler (`src/flight_pipeline/kpi/bts_reconciler.py`)  
**Audit Finding Addressed:** R2-F03 (Flight number 0.0 masked by 'or' syntax; blank date matching blank date)  
**Date:** 2026-10-19  
**Status:** COMPLETE / COMPOSITE KEY INTEGRITY ENFORCED  

---

## 1. Executive Summary & Defect Remediation

During independent audit review of T011-R1, finding **R2-F03** identified two subtle pythonic evaluation bugs in `extract_composite_key`:
1. **Falsy Masking on Flight Number Zero:** The extraction logic used:
   `fl_num_raw = rec.get("OP_CARRIER_FL_NUM") or rec.get("Flight_Number_Reporting_Airline")`
   In Python, numerical zero (`0` or `0.0`) evaluates to falsy (`bool(0.0) == False`). Consequently, if a flight record legitimately had flight number `0` (which is accepted under `G3-COND-A` with provisional anomaly flag), the `or` expression bypassed it and took whatever secondary alias or default existed, corrupting the key.
2. **Blank Date Matching Blank Date:** The composite key extraction performed no semantic date format verification. An empty string `""` or invalid token on the dataset side matched an empty string `""` on the BTS side, producing a spurious match on invalid records.

In T011-R2, `extract_composite_key` has been re-engineered with explicit non-None existence checks and rigorous format validation.

---

## 2. Hardened Composite Key Architecture

### 2.1 The 5 Canonical Key Components

The composite key consists of 5 fields:
1. `FL_DATE` (Date in `YYYY-MM-DD` format)
2. `OP_CARRIER` (Standard 2-to-3 character airline code)
3. `OP_CARRIER_FL_NUM` (Flight number preserved as numeric float)
4. `ORIGIN` (3-letter IATA airport code)
5. `DEST` (3-letter IATA airport code)

### 2.2 Extraction Implementation (`src/flight_pipeline/kpi/bts_reconciler.py`)

```python
def extract_composite_key(self, record: Dict[str, Any]) -> Tuple[Any, Any, Any, Any, Any, bool]:
    is_valid = True

    # 1. FL_DATE validation
    fl_date_raw = None
    for k in ("FL_DATE", "FlightDate", "fl_date", "flight_date"):
        if k in record and record[k] is not None:
            fl_date_raw = str(record[k]).strip()
            break
    if not fl_date_raw or len(fl_date_raw) < 8 or not ISO_DATE_PATTERN.match(fl_date_raw[:10]):
        is_valid = False
        fl_date = None
    else:
        fl_date = fl_date_raw[:10]

    # 2. OP_CARRIER validation
    carrier_raw = None
    for k in ("OP_CARRIER", "Reporting_Airline", "op_carrier", "reporting_airline", "carrier"):
        if k in record and record[k] is not None:
            carrier_raw = str(record[k]).strip()
            break
    if not carrier_raw:
        is_valid = False
        carrier = None
    else:
        carrier = carrier_raw.upper()

    # 3. OP_CARRIER_FL_NUM validation (explicit non-None check preserves 0.0)
    fl_num_raw = None
    for k in ("OP_CARRIER_FL_NUM", "Flight_Number_Reporting_Airline", "op_carrier_fl_num", "flight_num"):
        if k in record and record[k] is not None:
            fl_num_raw = record[k]
            break
    if fl_num_raw is None:
        is_valid = False
        fl_num = None
    else:
        try:
            fl_num = float(fl_num_raw)
            if fl_num < 0:
                is_valid = False
        except (ValueError, TypeError):
            is_valid = False
            fl_num = None

    # 4. ORIGIN validation
    origin_raw = None
    for k in ("ORIGIN", "Origin", "origin"):
        if k in record and record[k] is not None:
            origin_raw = str(record[k]).strip()
            break
    if not origin_raw:
        is_valid = False
        origin = None
    else:
        origin = origin_raw.upper()

    # 5. DEST validation
    dest_raw = None
    for k in ("DEST", "Dest", "dest"):
        if k in record and record[k] is not None:
            dest_raw = str(record[k]).strip()
            break
    if not dest_raw:
        is_valid = False
        dest = None
    else:
        dest = dest_raw.upper()

    return (fl_date, carrier, fl_num, origin, dest, is_valid)
```

---

## 3. Strict Isolation of Invalid Keys

In `reconcile()`, any record where `not is_valid` is:
1. Immediately recorded as an invalid key: `summary.invalid_key_records += 1`.
2. Appended to `match_results` with status `KeyMatchStatus.INVALID_KEY`.
3. Excluded from `dataset_index` and `bts_index`, making it mathematically impossible for an invalid key to match any other record (even another invalid record with identical blank fields).
4. Sets `summary.numerical_parity_verified = False`, preventing any successful parity determination.

---

## 4. Verification Evidence

1. **Defect Reproduction & Regression Guards (`tests/test_t011_r2_counterexamples.py`):**
   - `test_guard_r2_f03a_flight_number_zero_preserved`: proves that `fl_num = 0` produces `k[2] = 0.0`, is valid (`k[5] = True`), and is never masked by a fallback alias.
   - `test_guard_r2_f03b_blank_date_fails_closed`: proves that empty `FL_DATE` produces `k[5] = False`, increments `summary.invalid_key_records = 2`, and results in `KeyMatchStatus.INVALID_KEY` on both sides.
2. **Dedicated Unit Tests (`tests/test_t011_ts018_bts_parity.py`):**
   - `test_08_invalid_composite_key_detected`: verifies that negative flight numbers fail key validation.
   - `test_15_blank_or_invalid_date_fails_closed`: verifies that empty and malformed dates fail closed.

---

## 5. Conclusion

Finding **R2-F03** is **CLOSED / RESOLVED**. Composite key formation is fully deterministic, respects zero as a legitimate numeric value under `G3-COND-A`, and rejects invalid dates.
