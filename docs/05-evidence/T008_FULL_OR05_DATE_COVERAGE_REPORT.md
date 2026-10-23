# T008 FULL OR-05 DATE COVERAGE & ANOMALY REPORT

**Document ID:** `T008_FULL_OR05_DATE_COVERAGE_REPORT`  
**Parent Task:** `T-008 — Data Quality, Disjoint Row Accounting & Quarantine Engine`  
**Parent Gate:** `G4`  
**Classification:** `QUALITY_DEFECT_ANALYSIS_AND_STAGE_VERIFICATION`  
**Date:** 2026-10-18  

---

## 1. OR-05 DEFECT SPECIFICATION

**Defect ID:** `OR-05`  
**Status:** `OPEN_QUALITY_DEFECT`  
**Description:** In the audited 2016–2024 dataset, the 2024 raw CSV (`flight_with_weather_2024.csv`) completely lacks all 31 calendar days of March 2024 (`2024-03-01` through `2024-03-31`). As a result, the 2024 dataset covers only `335` of `366` expected calendar days.

### Non-Negotiable Governance Rules:
- **No Data Fabrication:** Under no circumstance shall synthetic records, blank rows, or interpolated flights be generated to "fill" the missing March days.
- **Coverage Status:** The 2024 dataset must be formally assigned `source_coverage_status = "PARTIAL"`.
- **Early-Stage Validation vs Final Acceptance:**
  - In Gate G4 (`T-008`): Date coverage algorithms and OR-05 defect detection are implemented and verified on synthetic fixtures.
  - In Gate G6 (`T-012`): Test `TS-004` will be officially evaluated and signed off on the full real dataset.

---

## 2. DATE COVERAGE ANALYZER IMPLEMENTATION

The `DateCoverageAnalyzer` implemented in `flight_pipeline.quality.coverage`:
1. Calculates canonical calendar days for any target year using `calendar.isleap(year)`:
   - Leap years (2016, 2020, 2024): `366` expected days (including February 29).
   - Normal years (2017, 2018, 2019, 2021, 2022, 2023): `365` expected days.
2. Extracts clean `YYYY-MM-DD` strings from `FL_DATE`.
3. Computes:
   - `observed_days`: Distinct valid calendar days in the cohort.
   - `missing_days_count` & `missing_dates`: Specific calendar days absent from the dataset.
   - `out_of_year_count` & `out_of_year_dates`: Dates belonging to a different calendar year.
   - `coverage_ratio`: `observed_days / expected_days`.
   - `has_march_2024_defect`: Boolean flag indicating whether all 31 days of March 2024 are missing.

---

## 3. SYNTHETIC VERIFICATION RESULTS

The analyzer was validated across 4 comprehensive tests:
- `test_cov_01_complete_normal_year`: Evaluated 365 days of 2017. Result: `COMPLETE`, 0 missing, coverage 1.0.
- `test_cov_02_complete_leap_year`: Evaluated 366 days of 2016 (including Feb 29). Result: `COMPLETE`, 0 missing, coverage 1.0.
- `test_cov_03_or05_missing_march_2024_defect_detected`: Evaluated 2024 synthetic fixture with 335 observed days and missing March. Result: `PARTIAL`, 31 missing days, `has_march_2024_defect = True`, coverage ratio `0.9153`.
- `test_cov_04_missing_feb_29_and_out_of_year_dates`: Evaluated 2020 leap year without Feb 29 plus out-of-year dates. Result: correctly flagged `2020-02-29` as missing and `2019-12-31` as out-of-year.
