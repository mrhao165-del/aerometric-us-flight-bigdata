# T007-01 UNIT TEST EXECUTION & AUDIT REPORT

**Document ID:** `DOC-T007-01-04-TEST-RESULTS`  
**Task ID:** `T007-01` (Canonical Schema Module)  
**Parent Gate:** `G4` (`PLANNED / NOT_COMPLETED`)  
**Test Suite:** [`tests/test_t007_schema.py`](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/tests/test_t007_schema.py)  
**Test Framework:** Python Standard Library `unittest`  
**Host Platform:** Windows (Python 3.10.11 64-bit)  

---

## 1. T007-01 UNIT TEST SUITE RESULTS (15 / 15 PASS)

| Test ID | Test Method Name | Validated Invariant / Boundary | Result | Execution Time |
| :---: | :--- | :--- | :---: | :---: |
| **T-01** | `test_01_exact_34_canonical_names_and_count` | Exactly 34 unique canonical column names | **PASS** | < 1 ms |
| **T-02** | `test_02_exact_physical_column_order` | Exact physical sequence matching `DATA_DICTIONARY.md` | **PASS** | < 1 ms |
| **T-03** | `test_03_no_fabricated_columns` | Absence of `CANCELLED`, `DIVERTED`, `DISTANCE`, etc. | **PASS** | < 1 ms |
| **T-04** | `test_04_flights_column_retained_with_prohibited_weight_metadata` | `FLIGHTS` retained; KPI denominator weighting prohibited | **PASS** | < 1 ms |
| **T-05** | `test_05_six_weather_fields_retained_as_optional` | 6 weather columns retained with `CONDITIONAL_NO_GO` | **PASS** | < 1 ms |
| **T-06** | `test_06_raw_csv_business_schema_all_stringtype` | All 34 business fields are `StringType` in raw schema | **PASS** | < 1 ms |
| **T-07** | `test_07_corrupt_record_separation_from_34_columns` | Technical `_corrupt_record` separated from 34 physical cols | **PASS** | < 1 ms |
| **T-08** | `test_08_curated_schema_exact_type_mapping` | Strongly-typed curated Parquet schema with provisional units | **PASS** | < 1 ms |
| **T-09** | `test_09_nullable_int64_calendar_fields` | `MONTH`, `DAY_OF_MONTH`, etc. are nullable `LongType` | **PASS** | < 1 ms |
| **T-10** | `test_10_op_carrier_fl_num_float64_boundary` | `OP_CARRIER_FL_NUM` preserves `DoubleType` (float64) | **PASS** | < 1 ms |
| **T-11** | `test_11_date_time_schema_preservation` | Date/time strings preserved; no rollover/timezone side effects | **PASS** | < 1 ms |
| **T-12** | `test_12_pure_schema_no_side_effects` | Pure schema logic; immutable return copies; no data I/O | **PASS** | < 1 ms |
| **T-13** | `test_13_schema_deterministic_on_repeated_calls` | Idempotent, deterministic JSON schemas on repeated calls | **PASS** | < 1 ms |
| **T-14** | `test_14_negative_validation_tests` | Rejection of reordered, missing, extra, or malformed columns | **PASS** | < 1 ms |
| **T-15** | `test_15_compatibility_with_existing_t009_modules` | Clean imports alongside existing `SafePublisher` & `RunManifest` | **PASS** | < 1 ms |

**T007-01 Suite Summary:** **15 PASS, 0 FAIL, 0 SKIP (Total Time: 0.009s)**

---

## 2. REPOSITORY-WIDE UNIT TEST REGRESSION SUITE (52 / 52 PASS)

All existing repository unit tests were executed in full alongside the new schema tests:
- `tests/test_numeric_predicates.py`: 6 tests PASS
- `tests/test_publication_safety.py`: 20 tests PASS
- `tests/test_manifest.py`: 4 tests PASS
- `tests/test_t009_r3_defect_reproductions.py`: 3 tests PASS
- `tests/test_spark_env.py`: 4 tests PASS
- `tests/test_t007_schema.py`: 15 tests PASS

**Grand Total:** **52 PASS, 0 FAIL, 0 SKIP (Total Time: 24.109s)**  
**Regression Impact:** **ZERO regressions detected across existing T-009 codebase.**
