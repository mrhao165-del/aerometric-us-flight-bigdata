# T011-R3 Gregorian Calendar Date & Composite Key Audit

**Project:** US Flight Performance Analysis 2016–2024  
**Task:** T-011 R3 — Provenance Trust Boundary, Numeric Integrity, Lock Recovery & Evidence Correction  
**Parent Gate:** G5 — IN_PROGRESS  
**Component:** Composite Key Parser (`src/flight_pipeline/kpi/bts_reconciler.py`)  
**Audit Finding Addressed:** R3-F04 (MEDIUM — Regex accepted non-existent calendar dates like Feb 31)  
**Date:** 2026-10-19  
**Status:** COMPLETE / REAL GREGORIAN CALENDAR VALIDATION ENFORCED  

---

## 1. Executive Summary & Defect Remediation

During the independent technical audit of package `T011_R2_REVIEW_PACKAGE.zip`, finding **R3-F04** revealed that composite key extraction in `BtsTranStatsReconciler` relied on a syntactic regex:
```python
ISO_DATE_REGEX = re.compile(r"^(\d{4})-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])$")
```
While this regex prevented arbitrary string tokens, it accepted mathematically impossible calendar dates:
- `2026-02-31` (February never has 31 days)
- `2025-02-29` (2025 is not a leap year)
- `2026-04-31` (April has 30 days)
- `2026-11-31` (November has 30 days)

If malformed records with impossible dates were ingested, they could form invalid composite keys and match identically corrupt records across systems instead of being flagged as `INVALID_KEY`.

In T011-R3, this defect is remediated by integrating real Gregorian calendar semantic validation via Python's standard `datetime.date(year, month, day)`.

---

## 2. Production Source Hardening

In `src/flight_pipeline/kpi/bts_reconciler.py`, `extract_composite_key` now executes:

```python
# 1. Date extraction & strict Gregorian calendar semantic validation
has_date, date_val = cls._lookup_present_key(rec, ["FL_DATE", "FlightDate", "Date"])
fl_date: Optional[str] = None
if has_date:
    date_str = str(date_val).strip()
    m = ISO_DATE_REGEX.match(date_str)
    if m:
        try:
            year, month, day = int(m.group(1)), int(m.group(2)), int(m.group(3))
            # Validate against real Gregorian calendar (e.g., rejects 2026-02-31, 2025-02-29)
            _ = date(year, month, day)
            fl_date = date_str
        except (ValueError, TypeError, OverflowError):
            fl_date = None
```

### Composite Key Validation Invariant

A composite key is defined as:
$$K = (\text{FL\_DATE}, \text{OP\_CARRIER}, \text{OP\_CARRIER\_FL\_NUM}, \text{ORIGIN}, \text{DEST})$$
A record is certified as valid (`is_valid = True`) if and only if all five components are non-null and valid:
1. `fl_date` is a real, valid Gregorian date string in `YYYY-MM-DD` format.
2. `carrier` is a non-empty uppercase string.
3. `fl_num` is a finite float $\in [0.0, +\infty)$. Note: Numerical zero (`0.0` or `"0"`) is explicitly supported and preserved.
4. `origin` is a non-empty uppercase 3-letter IATA code.
5. `dest` is a non-empty uppercase 3-letter IATA code.

---

## 3. Verification Evidence & Counterexample Guards

Permanent regression suite `tests/test_t011_r3_counterexamples.py` (`TestT011R3CompositeKeyDate`) verifies Gregorian calendar enforcement:

1. `test_r3_f04_february_31_rejected`: PASS (`"2026-02-31"` rejected as invalid).
2. `test_r3_f04_non_leap_february_29_rejected`: PASS (`"2025-02-29"` rejected as invalid).
3. `test_r3_f04_leap_february_29_accepted`: PASS (`"2024-02-29"` accepted as valid leap day).
4. `test_r3_f04_april_31_rejected`: PASS (`"2026-04-31"` rejected as invalid).
5. `test_r3_f04_month_13_rejected`: PASS (`"2026-13-01"` rejected as invalid).
6. `test_r3_f04_flight_number_zero_preserved`: PASS (`0.0` preserved as valid float).

---

## 4. Conclusion

Finding **R3-F04** is **RESOLVED / CLOSED**. The reconciler composite key parser enforces true Gregorian calendar validity. Impossible calendar dates fail closed as `INVALID_KEY`.
