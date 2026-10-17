# T009-SEAL-FIX Final Test Execution Matrix

## 1. Executive Summary
This document provides the definitive verification matrix for Task T-009 seal fix remediation, detailing execution parameters, exit codes, and assertion volumes across all test frameworks.

---

## 2. Comprehensive Test Execution Suite

| Suite ID | Target / Test File | Scope / Invariants Verified | Executed Command | Results | Exit Code | Verified Evidence Log |
| :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| **UNIT-01** | `tests/` (all discovery) | 31 tests: Manifest, DC-11/12, finite numerics, SafePublisher normal, F-01..F-05, pointer read exception (3 variants), streaming SHA-256 | `python -m unittest discover tests -v` | **31 PASS**<br>0 FAIL<br>0 SKIP | 0 | `T009_SEAL_FIX_LOG_UNITTESTS.txt` |
| **SMOKE-01** | `tests.test_spark_env.TestSparkEnv` | SparkSession initialization, local directory config, catalog metadata access | `python -m unittest tests.test_spark_env.TestSparkEnv -v` | **1 PASS**<br>0 FAIL<br>0 SKIP | 0 | `T009_SEAL_FIX_LOG_SPARK_SMOKE.txt` |
| **T006-REG** | `tools/qa/verify_t006_contract_consistency.py` | 17 data contract invariants & 16 isolated mutation test cases | `python tools/qa/verify_t006_contract_consistency.py` | **17 PASS (Inv)**<br>**16 PASS (Mut)**<br>0 FAIL | 0 | `T009_SEAL_FIX_LOG_T006_REGRESSION.txt` |
| **REG-01** | `tools/qa/test_working_tree_registry_regression.py` | Working-tree deliverable registry regression (POS-01..02, NEG-01..10, MUT-01..03) | `python tools/qa/test_working_tree_registry_regression.py` | **16 PASS**<br>0 FAIL<br>0 SKIP | 0 | `T009_SEAL_FIX_LOG_REGISTRY_REGRESSION.txt` |
| **GIT-01** | `tools/qa/test_t009_unblock_r2_git_exclusion.py` | Git `.git/` root metadata exclusion positive & negative tests | `python tools/qa/test_t009_unblock_r2_git_exclusion.py` | **7 PASS**<br>0 FAIL | 0 | `T009_SEAL_FIX_LOG_GIT_EXCLUSION.txt` |
| **VAL-01** | `tools/qa/test_t009_r1_validator_extension.py` | Validator policy extension for PySpark pipeline files | `python tools/qa/test_t009_r1_validator_extension.py` | **8 PASS**<br>0 FAIL | 0 | `T009_SEAL_FIX_LOG_VALIDATOR_EXTENSION.txt` |
| **CI-01** | `tools/check_working_tree_consistency.py --ci-mode` | Clean-checkout CI mode (enforces 0 raw CSVs committed to Git) | `python tools/check_working_tree_consistency.py --ci-mode` | **627 PASS**<br>0 FAIL<br>0 SKIP | 0 | `T009_SEAL_FIX_LOG_CI_CLEAN_CHECKOUT.txt` |
| **CONS-01** | `tools/check_working_tree_consistency.py` | Full local audit consistency (enforces exactly 9 raw CSVs present on disk) | `python tools/check_working_tree_consistency.py` | **627 PASS**<br>0 FAIL<br>0 SKIP | 0 | `T009_SEAL_FIX_LOG_CONSISTENCY.txt` |

---

## 3. Total Verification Volume
- **Total Assertions Across Suites:** $31 + 1 + 33 + 16 + 7 + 8 + 627 + 627 = 1350\text{ assertion checkpoints verified}$.
- **Failures / Errors:** `0`.
- **Skipped Tests:** `0`.
