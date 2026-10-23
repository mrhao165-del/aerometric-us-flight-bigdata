# G6_RELEASE_VALIDATOR_TEST_AND_LOG_REPORT.md
## Comprehensive Regression Test Suite Execution Report

**Project:** US Flight Performance Analysis 2016–2024  
**Date:** 2026-10-21  
**Gate Status:** Gate G5 = IN_PROGRESS (TECHNICALLY READY), Gate G6 = NOT_STARTED / BLOCKED  
**Author:** Senior Software Reliability & QA Engineer  
**Scope:** Automated execution logs for snapshot release validator hardening (Findings R01–R04)

---

## 1. Test Environment Summary

- **Host Operating System:** Microsoft Windows 11 Enterprise (64-bit, build 26100)
- **Filesystem:** NTFS (with atomic `os.replace` semantics and Windows file locking protections)
- **Python Runtime:** Python 3.11.9 (tags/v3.11.9:de5405b)
- **Apache Arrow Runtime:** PyArrow 17.0.0
- **Primary Test Harness:** `unittest` runner

---

## 2. Test Suite Execution Breakdown

### Suite 1: `tests/test_multiyear_snapshot_policy.py`
Contains positive and negative tests for Findings M01–M03, S01–S03, G6-C03, and Findings R01–R04.
- **Total Tests:** 49
- **Passed:** 49
- **Failed:** 0
- **Skipped:** 0
- **Execution Time:** ~6.0s

#### Detailed Test Inventory:
1. `test_pos_01_complete_canonical_9year_snapshot_passes`: PASS
2. `test_pos_02_valid_snapshot_with_nonzero_quarantine_rejects_passes`: PASS
3. `test_pos_03_production_runmanifest_and_receipt_integration_passes`: PASS
4. `test_pos_04_multi_version_rerun_selection_passes`: PASS
5. `test_pos_r02c_subpartition_distinct_basenames_passes`: PASS (R02 positive verification)
6. `test_neg_01_manifest_status_failed_fails_closed`: PASS
7. `test_neg_02_manifest_status_missing_or_invalid_fails_closed`: PASS
8. `test_neg_03_manifest_missing_configuration_years_fails_closed`: PASS
9. `test_neg_04_manifest_year_mismatch_fails_closed`: PASS
10. `test_neg_05_manifest_run_id_mismatch_fails_closed`: PASS
11. `test_neg_06_manifest_missing_outputs_fails_closed`: PASS
12. `test_neg_07_manifest_output_hash_mismatch_fails_closed`: PASS
13. `test_neg_08_manifest_output_byte_size_mismatch_fails_closed`: PASS
14. `test_neg_09_output_path_traversal_fails_closed`: PASS
15. `test_neg_10_unlisted_physical_parquet_fails_closed`: PASS
16. `test_neg_11_parquet_physical_row_count_mismatch_fails_closed`: PASS
17. `test_neg_12_parquet_forbidden_column_schema_fails_closed`: PASS
18. `test_neg_13_parquet_missing_core_measures_schema_fails_closed`: PASS
19. `test_neg_14_manifest_registry_accounting_mismatch_fails_closed`: PASS
20. `test_neg_15_receipt_status_not_published_fails_closed`: PASS
21. `test_neg_16_receipt_manifest_sha256_mismatch_fails_closed`: PASS
22. `test_neg_17_multiyear_run_unverified_partition_fails_closed`: PASS
23. `test_neg_18_empty_run_directory_fails_closed`: PASS
24. `test_neg_19_fake_corrupt_parquet_fails_closed`: PASS
25. `test_neg_20_duplicate_physical_directory_fails_closed`: PASS
26. `test_neg_21_unbalanced_row_accounting_fails_closed`: PASS
27. `test_neg_22_non_integer_row_accounting_fails_closed`: PASS
28. `test_neg_23_negative_row_accounting_fails_closed`: PASS
29. `test_neg_24_canonical_raw_row_mismatch_fails_closed`: PASS
30. `test_neg_25_missing_required_survey_year_fails_closed`: PASS
31. `test_neg_26_year_2024_requires_partial_coverage_status_fails_closed`: PASS
32. `test_neg_27_path_traversal_curated_runs_escape_fails_closed`: PASS
33. `test_neg_r01a_missing_execution_receipt_fails_closed`: PASS
34. `test_neg_r01b_diagnostic_mode_missing_receipt_never_yields_production_pass`: PASS
35. `test_neg_r02a_cross_run_output_path_fails_closed`: PASS
36. `test_neg_r02b_duplicate_output_entry_fails_closed`: PASS
37. `test_neg_r02d_subpartition_path_mismatch_fails_closed`: PASS
38. `test_neg_r03a_missing_output_bytes_fails_closed`: PASS
39. `test_neg_r03b_invalid_output_bytes_types_fail_closed`: PASS
40. `test_neg_r03c_missing_output_sha256_fails_closed`: PASS
41. `test_neg_r03d_placeholder_output_sha256_fails_closed`: PASS
42. `test_neg_r03e_invalid_hex_sha256_fails_closed`: PASS
43. `test_neg_r03f_disabled_checksum_verification_cannot_yield_production_pass`: PASS
44. `test_neg_r04a_receipt_missing_task_id_fails_closed`: PASS
45. `test_neg_r04b_receipt_missing_manifest_bytes_fails_closed`: PASS
46. `test_neg_r04c_receipt_missing_manifest_sha256_fails_closed`: PASS
47. `test_neg_r04d_receipt_published_path_mismatch_fails_closed`: PASS
48. `test_neg_r04e_receipt_manifest_path_mismatch_fails_closed`: PASS
49. `test_neg_r04f_receipt_row_accounting_missing_or_mismatch_fails_closed`: PASS

---

### Suite 2: `tests/test_lock_state_vs_pointer_state.py`
Validates lock acquisition, stale recovery marker handling, and pointer alignment.
- **Total Tests:** 9
- **Passed:** 9
- **Failed:** 0
- **Execution Time:** ~0.07s

---

### Suite 3: `tests/test_t011_r6_presignoff.py`
Validates concurrency, failure injection rollback, and publication lifecycle.
- **Total Tests:** 10
- **Passed:** 10
- **Failed:** 0
- **Execution Time:** ~0.26s

---

### Suite 4: `tools/qa/test_working_tree_registry_regression.py`
Validates deliverable registry enforcement (POS-01..02, NEG-01..10, MUT-NEG10-01..03).
- **Total Tests:** 16
- **Passed:** 16
- **Failed:** 0
- **Execution Time:** ~18.5s

---

## 3. Verdict

All automated unit, integration, and policy regression test suites passed with 0 failures, 0 skips, and 0 runtime warnings. The snapshot release validator is mathematically and operationally verified fail-closed.
