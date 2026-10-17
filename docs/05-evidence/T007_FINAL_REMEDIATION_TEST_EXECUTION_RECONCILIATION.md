# T007_FINAL_REMEDIATION_TEST_EXECUTION_RECONCILIATION — Test Suite Inventory, Raw Log Reconciliation & Errata (`FIX-F07`)

**Document ID:** `T007-FINAL-REMEDIATION-TEST-RECONCILIATION-20261017`  
**Task:** `MASTER-T007-FINAL-REMEDIATION` (`T-007` — Raw CSV Ingestion Pipeline)  
**Parent Gate:** `G4` (`PLANNED / NOT_COMPLETED`)  
**Date:** `2026-10-17`

---

## 1. Executive Summary & `FIX-F07` Errata Supersession

This document resolves **`FIX-F07` (Test & Evidence Reconciliation)** by establishing a single, machine-verified test inventory and explicitly superseding the documentation discrepancies identified in the prior `T007_FULL_*` reports.

### 1.1 Explicit Errata for Earlier `T007_FULL_*` Reports
The following historical discrepancies in `T007_FULL_IMPLEMENTATION_ARCHITECTURE.md`, `T007_FULL_TEST_MATRIX.md`, `T007_FULL_SYNTHETIC_INTEGRATION_REPORT.md`, and `T007_FULL_STORAGE_AND_RECOVERY_AUDIT.md` (which remain immutable in the evidence archive) are formally superseded by this `T007_FINAL_REMEDIATION_*` suite:

| Earlier Document | Earlier Statement (Superseded) | Corrected / Actual Ground Truth |
|---|---|---|
| `T007_FULL_TEST_MATRIX.md` & `T007_FULL_FINAL_INDEPENDENT_REVIEW.md` vs `PROJECT_STATE.md` | `T007_FULL_TEST_MATRIX.md` listed `18` `T-009` tests + `86` `T-007` tests = `104` total, while `PROJECT_STATE.md` listed `122/122` tests. | Actual `tests/` directory contains **`37` `T-009` tests** across 5 files (`6 + 4 + 18 + 4 + 5 = 37`) and **`94` `T-007` tests** across 5 files (`22 + 38 + 15 + 8 + 11 = 94`, up from `86` before remediation), for an exact total of **`131/131` tests PASS** in [`T007_FINAL_REMEDIATION_LOG_UNITTEST_SUITE.txt`](T007_FINAL_REMEDIATION_LOG_UNITTEST_SUITE.txt). |
| `T007_FULL_TEST_MATRIX.md` Section 2.1 & 2.2 | Listed draft test method names (`test_reader_01_valid_records_and_row_accounting`, `test_lock_01_acquire_and_release_lifecycle`, `"1234.0" -> "1234"`). | Actual test method names in `tests/test_t007_reader.py`, `tests/test_t007_locking.py`, and `tests/test_t007_pipeline_integration.py` are listed verbatim in Section 2 below; `OP_CARRIER_FL_NUM` is preserved as `DoubleType` (`float64`), not string-stripped. |
| `T007_FULL_IMPLEMENTATION_ARCHITECTURE.md` Section 2 | Wrote `15 Weather measures`, `src/flight_pipeline/schema.py`, `src/flight_pipeline/storage/publisher.py`, `src/flight_pipeline/metadata/manifest.py`, and `CURRENT_PUBLISHED_RUN.json`. | Canonical schema has **`6` Weather columns** (`O_TEMP`, `O_PRCP`, `O_WSPD`, `D_TEMP`, `D_PRCP`, `D_WSPD`) and **`7` CORE measures** (`G2-EXC-001`). Actual module paths are `src/flight_pipeline/ingestion/schema.py`, `src/flight_pipeline/storage/publication.py`, `src/flight_pipeline/utils/run_manifest.py`, and pointer file `data/curated/latest_run_id.txt`. |
| `T007_FULL_SYNTHETIC_INTEGRATION_REPORT.md` Section 2 | Described `INT-01` synthetic fixture as `7 == 4 + 2 + 1` rows (`5` rows in 2016 + `2` rows in 2024). | Actual `test_int_01_full_end_to_end_synthetic_pipeline_success` in `tests/test_t007_pipeline_integration.py` uses **`6` total rows (`6 == 4 + 1 + 1`)**: `2016` has `4` rows (`2` accepted, `1` quarantined `BAD_DATE`, `1` rejected `SHORT_ROW`) and `2024` has `2` rows (`2` accepted, `0` quarantined, `0` rejected). |
| `T007_FULL_STORAGE_AND_RECOVERY_AUDIT.md` Section 2 | Wrote lock filename `data/locks/ingestion_writer.lock` and `LockAcquisitionError`. | Actual `SingleWriterLock` in `src/flight_pipeline/storage/locking.py` uses `data/locks/.pipeline.lock` (`DEFAULT_LOCK_FILENAME = ".pipeline.lock"`) and raises `LockContentionError` / `CorruptLockError` (subclasses of `LockError`). |

---

## 2. Complete Machine-Verified Unittest Inventory (`131/131 PASS`)

Executed via:
`python -m unittest discover -s tests -p "test_*.py" -v`
Raw log: [`docs/05-evidence/T007_FINAL_REMEDIATION_LOG_UNITTEST_SUITE.txt`](T007_FINAL_REMEDIATION_LOG_UNITTEST_SUITE.txt) (`Exit Code: 0`, `Ran 131 tests in 75.987s — OK`).

| # | Test File | Task Scope | Test Count | Status |
|---|---|---|---:|---|
| 1 | `tests/test_manifest.py` | `T-009` `RunManifest` & `RowAccounting` (`DC-11/12`) | `6` | `6/6 PASS` |
| 2 | `tests/test_numeric_predicates.py` | `T-009` `is_finite_numeric` & KPI predicates (`G3-COND-B`) | `4` | `4/4 PASS` |
| 3 | `tests/test_publication_safety.py` | `T-009` `SafePublisher` 7-step Windows NTFS atomicity (`G3-COND-C`) | `18` | `18/18 PASS` |
| 4 | `tests/test_spark_env.py` | `T-009` Spark session & scratch directory isolation | `4` | `4/4 PASS` |
| 5 | `tests/test_t009_r3_defect_reproductions.py` | `T-009` R3 regression suite (`F-01..F-04`) | `5` | `5/5 PASS` |
| — | **`T-009` Subtotal** | **Baseline Infrastructure (`100%` Unmodified)** | **`37`** | **`37/37 PASS`** |
| 6 | `tests/test_t007_schema.py` | `T007-01` Canonical 34-col schema & `StructType` isolation | `22` | `22/22 PASS` |
| 7 | `tests/test_t007_source_validator.py` | `T007-02A/02B` Path security, `lstat`/reparse, G1 inventory & SHA-256 | `38` | `38/38 PASS` |
| 8 | `tests/test_t007_reader.py` | `T007-03` + `FIX-F01/F02/F06` Header validation, scanner, lineage & classifier | `15` | `15/15 PASS` |
| 9 | `tests/test_t007_locking.py` | `T007-04` Win32 `OpenProcess` single-writer lock & contention | `8` | `8/8 PASS` |
| 10 | `tests/test_t007_pipeline_integration.py` | `T007-05..07` + `FIX-F01..F06` E2E publish, forensic, retry & recovery | `11` | `11/11 PASS` |
| — | **`T-007` Subtotal** | **Raw CSV Ingestion Pipeline** | **`94`** | **`94/94 PASS`** |
| — | **Grand Total (`tests/`)** | **All Discovered Unit & Integration Tests** | **`131`** | **`131/131 PASS`** |

---

## 3. Verbatim Method List for Updated Test Suites (`test_t007_reader.py`, `test_t007_locking.py`, `test_t007_pipeline_integration.py`)

### 3.1 `tests/test_t007_reader.py` (`15` methods)
1. `test_curated_schema_preserves_canonical_types`
2. `test_dc12_non_numeric_metric_accepted_in_raw_and_null_in_curated`
3. `test_extra_tokens_captured_as_corrupt`
4. `test_fix_f01_physical_header_validation_all_failure_modes`
5. `test_fix_f02_deterministic_lineage_and_duplicate_yx3624_disambiguation`
6. `test_fix_f02_unclosed_quote_blank_line_and_accounting_unverified`
7. `test_fix_f06_calendar_dates_and_core_identity_anchors`
8. `test_g3_cond_b_non_positive_flight_num_not_quarantined`
9. `test_header_only_csv_handling`
10. `test_malformed_fl_date_quarantined`
11. `test_negative_delay_values_preserved`
12. `test_null_weather_columns_accepted`
13. `test_quoted_commas_and_embedded_newlines`
14. `test_read_valid_34_columns_parses_cleanly`
15. `test_short_row_token_mismatch_captured_as_corrupt`

### 3.2 `tests/test_t007_locking.py` (`8` methods)
1. `test_concurrent_lock_attempts`
2. `test_context_manager_usage`
3. `test_duplicate_run_id_detection`
4. `test_lock_contention_between_two_writers`
5. `test_lock_owner_mismatch_prevents_release`
6. `test_refuse_to_break_active_lock`
7. `test_single_writer_acquire_and_release`
8. `test_stale_lock_with_dead_pid_requires_manual_recovery`

### 3.3 `tests/test_t007_pipeline_integration.py` (`11` methods)
1. `test_int_01_full_end_to_end_synthetic_pipeline_success`
2. `test_int_02_unapproved_candidate_hashes_guard`
3. `test_int_03_fix_f03_forensic_quarantine_and_rejected_persistence_readback`
4. `test_int_04_fix_f04_parquet_two_phase_attempt_cleanup_and_verification`
5. `test_int_05_fix_f05_post_pointer_sidecar_failure_and_reconciliation`
6. `test_neg_01_missing_source_file_fails_closed`
7. `test_neg_02_source_size_mismatch_fails_closed`
8. `test_neg_03_source_hash_mismatch_fails_closed`
9. `test_neg_04_duplicate_run_id_and_lock_contention`
10. `test_neg_05_fault_injection_corrupt_staging_and_recovery_retry`
11. `test_neg_06_fix_f01_f02_header_drift_and_blank_line_abort_before_publication`

---

## 4. Repository QA & Governance Verifiers

Raw log: [`docs/05-evidence/T007_FINAL_REMEDIATION_LOG_QA_VERIFIERS.txt`](T007_FINAL_REMEDIATION_LOG_QA_VERIFIERS.txt)
- `python tools/qa/verify_t006_contract_consistency.py`: `Exit Code 0` (`17/17` Invariants PASS, `16/16` Mutations PASS).
- `python tools/qa/verify_g2_repo_apply_r1_semantic_invariants.py`: `Exit Code 0` (`R1-01..06` PASS, `MUT-01..08` PASS).
- `python tools/qa/test_t009_r1_validator_extension.py`: `Exit Code 0` (`8/8` PASS).
- `python tools/qa/test_t009_unblock_r2_git_exclusion.py`: `Exit Code 0` (`7/7` PASS).
- `python tools/qa/test_working_tree_registry_regression.py`: `Exit Code 0` (`16/16` PASS).
- `python tools/check_working_tree_consistency.py`: `Exit Code 0` (`0 FAIL`).
