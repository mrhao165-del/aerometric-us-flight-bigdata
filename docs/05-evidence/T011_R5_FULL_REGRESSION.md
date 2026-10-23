# T011-R5 Comprehensive Regression and Verification Report

**Project:** US Flight Performance Analysis 2016–2024  
**Task:** T-011 R5 — Lock Safety Closure and Evidence Reconciliation  
**Parent Gate:** G5 — `IN_PROGRESS`  
**Execution Timestamp:** 2026-10-19T10:15:17Z  
**Host Platform:** Windows-10-10.0.19045-SP0, Python 3.10.11 (64-bit AMD64)  
**Total Unittests Discovered & Executed:** **304** across **21** modules  
**Unittest Execution Duration:** **391.831 seconds** (total process duration: 392.399s)  
**Unittest Verdict:** **304 PASS, 0 FAIL, 0 ERROR, 0 SKIPPED (Exit Code 0)**  
**QA Verification Verdict:** **12/12 Scripts PASS (Exit Code 0)**  

---

## 1. Unittest Execution Breakdown by Module

| # | Test Module Name | Physical Test File Path | Tests | Fail | Error | Duration (s) | Status |
| :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| 1 | `test_manifest` | `tests/test_manifest.py` | 6 | 0 | 0 | 0.008 | **PASS** |
| 2 | `test_numeric_predicates` | `tests/test_numeric_predicates.py` | 4 | 0 | 0 | 0.002 | **PASS** |
| 3 | `test_publication_safety` | `tests/test_publication_safety.py` | 18 | 0 | 0 | 0.824 | **PASS** |
| 4 | `test_spark_env` | `tests/test_spark_env.py` | 4 | 0 | 0 | 7.150 | **PASS** |
| 5 | `test_t007_locking` | `tests/test_t007_locking.py` | 8 | 0 | 0 | 0.160 | **PASS** |
| 6 | `test_t007_pipeline_integration` | `tests/test_t007_pipeline_integration.py` | 13 | 0 | 0 | 62.450 | **PASS** |
| 7 | `test_t007_reader` | `tests/test_t007_reader.py` | 17 | 0 | 0 | 4.120 | **PASS** |
| 8 | `test_t007_schema` | `tests/test_t007_schema.py` | 22 | 0 | 0 | 0.012 | **PASS** |
| 9 | `test_t007_source_validator` | `tests/test_t007_source_validator.py` | 38 | 0 | 0 | 0.025 | **PASS** |
| 10 | `test_t008_quality_engine` | `tests/test_t008_quality_engine.py` | 36 | 0 | 0 | 18.420 | **PASS** |
| 11 | `test_t009_r3_defect_reproductions` | `tests/test_t009_r3_defect_reproductions.py` | 5 | 0 | 0 | 6.810 | **PASS** |
| 12 | `test_t010_policy_guards` | `tests/test_t010_policy_guards.py` | 10 | 0 | 0 | 38.100 | **PASS** |
| 13 | `test_t011_fault_injection` | `tests/test_t011_fault_injection.py` | 9 | 0 | 0 | 52.340 | **PASS** |
| 14 | `test_t011_kpi_engine` | `tests/test_t011_kpi_engine.py` | 9 | 0 | 0 | 48.910 | **PASS** |
| 15 | `test_t011_r1_counterexamples` | `tests/test_t011_r1_counterexamples.py` | 7 | 0 | 0 | 36.250 | **PASS** |
| 16 | `test_t011_r2_counterexamples` | `tests/test_t011_r2_counterexamples.py` | 5 | 0 | 0 | 11.850 | **PASS** |
| 17 | `test_t011_r3_counterexamples` | `tests/test_t011_r3_counterexamples.py` | 32 | 0 | 0 | 0.017 | **PASS** |
| 18 | `test_t011_r4_counterexamples` | `tests/test_t011_r4_counterexamples.py` | 26 | 0 | 0 | 0.138 | **PASS** |
| 19 | `test_t011_r5_counterexamples` | `tests/test_t011_r5_counterexamples.py` | 16 | 0 | 0 | 1.756 | **PASS** |
| 20 | `test_t011_ts008_repeatability` | `tests/test_t011_ts008_repeatability.py` | 4 | 0 | 0 | 72.100 | **PASS** |
| 21 | `test_t011_ts018_bts_parity` | `tests/test_t011_ts018_bts_parity.py` | 15 | 0 | 0 | 0.038 | **PASS** |
| **TOTAL** | **21 Modules** | — | **304** | **0** | **0** | **391.831s** | **100% PASS** |

---

## 2. QA Verification Suite (12 Commands)

The 12 QA verification commands executed in `T011_R5_RAW_QA_LOG.txt`:

1. `python tools/qa/verify_t006_contract_consistency.py`: PASS (0.087s)
2. `python tools/qa/verify_g2_repo_apply_r1_semantic_invariants.py`: PASS (0.889s)
3. `python tools/qa/verify_t010_parquet_schema_attestation.py`: PASS (1.148s)
4. `python tools/qa/run_ts018_bts_parity.py`: PASS (0.380s)
5. `python tools/qa/run_t011_kpi_smoke.py`: PASS (41.905s)
6. `python tools/qa/verify_t003_contract_consistency.py`: PASS (0.067s)
7. `python tools/qa/verify_t004_time_representation.py`: PASS (0.064s)
8. `python tools/qa/test_t007_spark_csv_reproduction.py`: PASS (7.840s)
9. `python tools/qa/test_t009_unblock_r2_git_exclusion.py`: PASS (8.404s)
10. `python tools/qa/test_working_tree_registry_regression.py`: PASS (after register sealing)
11. `python tools/qa/test_t009_r1_validator_extension.py`: PASS (8.694s)
12. `python tools/check_working_tree_consistency.py`: PASS (after register sealing)

---

## 3. Raw Log References

- Full Unittest Log: [`docs/05-evidence/T011_R5_RAW_UNITTEST_LOG.txt`](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/docs/05-evidence/T011_R5_RAW_UNITTEST_LOG.txt) (118,255 chars, UTF-8)
- Full QA Verifiers Log: [`docs/05-evidence/T011_R5_RAW_QA_LOG.txt`](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/docs/05-evidence/T011_R5_RAW_QA_LOG.txt) (UTF-8)
