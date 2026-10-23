# T008-FINAL-EXIT: Calendar Coverage Specificity & OR-05 Disambiguation

**Deliverable ID:** `T008-DELIV-EXIT-02`  
**Task:** `MASTER-T008-FINAL-EXIT`  
**Parent Task:** `T-008 — Data Quality, Disjoint Row Accounting & Quarantine Engine`  
**Gate:** `G4`  
**Timestamp:** `2026-10-18T15:52:00+07:00`  
**Status:** `VERIFIED_PASS`  
**Authority:** `OR-05`, `FP-DEC-002`, `DATA_CONTRACT.md` (DC-12), `TEST_PLAN.md` (`TS-004`)

---

## 1. Executive Summary

In the initial implementation of `DateCoverageAnalyzer`, the check for the 2024 March anomaly was evaluated via `all(m in missing_dates for m in march_days)`. If an empty cohort (`observed_days == 0`) was analyzed, `missing_dates` contained all 366 days of 2024, causing the analyzer to erroneously set `has_march_2024_defect = True`. Furthermore, there was no formal distinction between a dataset where March was simply among multiple missing months versus the exact canonical OR-05 pattern (335 observed days, exactly the 31 days of March missing).

This document records the resolution of **FIX-02**:
1. Preventing empty or all-missing cohorts from triggering false-positive OR-05 defect flags.
2. Formally disambiguating `is_march_missing` from `is_exact_or05_pattern`.
3. Updating `CoverageReport` dataclass to expose both diagnostic attributes.
4. Implementing a complete test matrix covering 5 distinct calendar coverage conditions.

---

## 2. Technical Architecture of FIX-02

### 2.1 Extended `CoverageReport` Dataclass
In `src/flight_pipeline/quality/coverage.py`, `CoverageReport` was updated to include:

```python
@dataclass(frozen=True)
class CoverageReport:
    year: int
    is_leap: bool
    expected_days: int
    observed_days: int
    missing_days_count: int
    missing_dates: List[str]
    out_of_year_count: int
    out_of_year_dates: List[str]
    source_coverage_status: str  # "COMPLETE" or "PARTIAL"
    coverage_ratio: Optional[float]
    has_march_2024_defect: bool
    is_march_missing: bool = False
    is_exact_or05_pattern: bool = False
```

### 2.2 Disambiguated Evaluation Logic in `analyze()`
```python
        # Check for OR-05 specific pattern: 2024 missing all 31 days of March.
        # Disambiguate March missing vs exact OR-05 pattern (335 observed days, exactly 31 days of March missing).
        # An empty cohort (observed_count == 0) must NOT trigger the OR-05 defect flag.
        has_march_2024_defect = False
        is_march_missing = False
        is_exact_or05_pattern = False
        if target_year == 2024 and observed_count > 0:
            march_days = [f"2024-03-{d:02d}" for d in range(1, 32)]
            is_march_missing = all(m in missing_dates for m in march_days)
            has_march_2024_defect = is_march_missing
            is_exact_or05_pattern = (observed_count == 335 and missing_count == 31 and is_march_missing)
```

---

## 3. Disambiguation Matrix & Test Verification

| Scenario | Test Method | Observed Days | Missing Days | `has_march_2024_defect` | `is_march_missing` | `is_exact_or05_pattern` | Status |
|---|---|:---:|:---:|:---:|:---:|:---:|:---:|
| **Empty 2024 Cohort** | `test_cov_05` | `0` | `366` | **`False`** (No false-positive) | `False` | `False` | `PARTIAL` |
| **Exact OR-05 Pattern** | `test_cov_03` | `335` | `31` | **`True`** | **`True`** | **`True`** | `PARTIAL` |
| **March + April Missing** | `test_cov_06` | `305` | `61` | **`True`** | **`True`** | **`False`** | `PARTIAL` |
| **Non-March Missing (Jan)** | `test_cov_07` | `356` | `10` | **`False`** | `False` | `False` | `PARTIAL` |
| **Complete 2024 (Leap)** | `test_cov_08` | `366` | `0` | **`False`** | `False` | `False` | `COMPLETE` |

---

## 4. Test Verification Evidence

All 5 scenarios were executed against PySpark in `tests/test_t008_quality_engine.py`:
- `test_cov_03_or05_missing_march_2024_defect_detected`: PASS
- `test_cov_05_empty_2024_cohort_does_not_flag_or05_defect`: PASS
- `test_cov_06_march_plus_other_months_missing_not_exact_or05_pattern`: PASS
- `test_cov_07_non_march_days_missing_does_not_flag_or05`: PASS
- `test_cov_08_complete_2024_does_not_flag_or05`: PASS

---

## 5. Verdict

**STATUS: PASS.** FIX-02 eliminates false-positive anomaly detection on empty cohorts and provides precise diagnostic separation between general March absence and the exact 335-day OR-05 defect pattern.
