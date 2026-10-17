# T009-CI-FINAL Test Results & Verification Matrix

## 1. Test Suite Summary
All test suites were executed on live project assets. Zero failures, zero errors, and zero regressions were observed.

| # | Test Suite | Scope & Module | Assertions / Cases | Result | Duration | Evidence Log |
|---|---|---|:---:|:---:|:---:|---|
| 1 | **Unit Test Suite** | Full discover `tests/test_*.py` | 37 tests | **37 PASS / 0 FAIL** | 28.1s | [`T009_CI_FINAL_LOG_UNITTESTS.txt`](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/docs/05-evidence/T009_CI_FINAL_LOG_UNITTESTS.txt) |
| 2 | **Spark Session Smoke** | `tests.test_spark_env.TestSparkEnv` | 1 session smoke | **1 PASS / 0 FAIL** | 11.1s | [`T009_CI_FINAL_LOG_SPARK_SMOKE.txt`](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/docs/05-evidence/T009_CI_FINAL_LOG_SPARK_SMOKE.txt) |
| 3 | **Contract Consistency** | `verify_t006_contract_consistency.py` | 17 Invariants + 16 Mutations | **33 PASS / 0 FAIL** | < 1s | [`T009_CI_FINAL_LOG_T006_REGRESSION.txt`](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/docs/05-evidence/T009_CI_FINAL_LOG_T006_REGRESSION.txt) |
| 4 | **Deliverable Registry** | `test_working_tree_registry_regression.py` | POS-01..02, NEG-01..10, MUT-01..03 | **16 PASS / 0 FAIL** | 11.5s | [`T009_CI_FINAL_LOG_REGISTRY_REGRESSION.txt`](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/docs/05-evidence/T009_CI_FINAL_LOG_REGISTRY_REGRESSION.txt) |
| 5 | **Git Exclusion Rules** | `test_git_exclusion_rules.py` | POS-01..02, NEG-01..05 | **7 PASS / 0 FAIL** | 5.2s | [`T009_CI_FINAL_LOG_GIT_EXCLUSION.txt`](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/docs/05-evidence/T009_CI_FINAL_LOG_GIT_EXCLUSION.txt) |
| 6 | **Validator Extension** | `test_validator_extension.py` | BASE-01, NEG-01..04, POS-01..03 | **8 PASS / 0 FAIL** | 5.8s | [`T009_CI_FINAL_LOG_VALIDATOR_EXTENSION.txt`](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/docs/05-evidence/T009_CI_FINAL_LOG_VALIDATOR_EXTENSION.txt) |
| 7 | **CI Clean Checkout** | `check_working_tree_consistency.py --ci-mode` | Full documentary & deliverable check | **655 PASS / 0 FAIL** | 1.9s | [`T009_CI_FINAL_LOG_CI_CLEAN_CHECKOUT.txt`](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/docs/05-evidence/T009_CI_FINAL_LOG_CI_CLEAN_CHECKOUT.txt) |
| 8 | **Local Consistency** | `check_working_tree_consistency.py` | Full working tree check (9 CSVs, 272 deliverables) | **655 PASS / 0 FAIL** | 1.2s | [`T009_CI_FINAL_LOG_CONSISTENCY.txt`](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/docs/05-evidence/T009_CI_FINAL_LOG_CONSISTENCY.txt) |

---

## 2. Unit Test Breakdown (37 Tests)
- `tests/test_manifest.py`: 6 tests (manifest serialization, schema pinning, run hash validation)
- `tests/test_numeric_predicates.py`: 7 tests (finite number checks, NaN/Inf handling for 7 CORE measures)
- `tests/test_publication_safety.py`: 18 tests (7-step publication order, row accounting, atomic replacement, rollback, streaming SHA-256, initial pointer read trapping)
- `tests/test_spark_env.py`: 4 tests (SparkSession creation, POSIX scratch compliance, Windows scratch compliance, safe fallback)
- `tests/test_t009_r3_defect_reproductions.py`: 2 tests (F-01 and F-02 regression guards)
