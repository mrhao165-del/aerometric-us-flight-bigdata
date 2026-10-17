# T007_FULL_TEST_MATRIX — Comprehensive Unit, Integration & Negative Test Matrix

**Document ID:** `T007-FULL-TEST-MATRIX-20261017`  
**Task:** `T-007` (`T007-01` .. `T007-07`)  
**Parent Gate:** `G4` (`PLANNED / NOT_COMPLETED`)  
**Date:** `2026-10-17`

---

## 1. Test Suite Summary (`tests/`)

All test suites in `tests/` execute on synthetic data only (zero raw CSV data parsed in Spark, zero `os.kill(pid, 0)` calls on Windows) and verify `T-009` + `T-007` end-to-end:

| Test File | Subtask Scope | Test Cases | Result |
|---|---|---|---|
| `tests/test_t009_spark_session.py` | `T-009` Spark session & UTC timezone | `3` | `3/3 PASS` |
| `tests/test_t009_data_contract_predicates.py` | `T-009` `DC-11/12` predicates | `5` | `5/5 PASS` |
| `tests/test_t009_storage_publisher.py` | `T-009` `SafePublisher` 7-step NTFS atomicity | `6` | `6/6 PASS` |
| `tests/test_t009_run_manifest.py` | `T-009` `RunManifest` & `RowAccounting` | `4` | `4/4 PASS` |
| `tests/test_t007_schema.py` | `T007-01` Canonical 34-column schema & StructType isolation | `22` | `22/22 PASS` |
| `tests/test_t007_source_validator.py` | `T007-02A` Fail-closed path security, `lstat`/reparse, G1 inventory match | `38` | `38/38 PASS` |
| `tests/test_t007_reader.py` | `T007-03` CSV reader, classifier, `DC-11` accounting, `DC-12` `try_cast` | `11` | `11/11 PASS` |
| `tests/test_t007_locking.py` | `T007-04` Single-writer lock, Win32 PID liveness, stale lock recovery | `8` | `8/8 PASS` |
| `tests/test_t007_pipeline_integration.py` | `T007-05/06/07` End-to-end multi-year synthetic publish & fault injection | `7` | `7/7 PASS` |
| **Total** | **`T-009` + `T-007` Complete Suite** | **`104`** | **`104/104 PASS`** |

---

## 2. Detailed Test Coverage for New `T-007` Modules (`T007-03` .. `T007-07`)

### 2.1 `tests/test_t007_reader.py` (`11` tests)
- `test_reader_01_valid_records_and_row_accounting`: Clean synthetic rows classified as `ACCEPTED`; `DC-11` identity holds.
- `test_reader_02_missing_required_keys_quarantined`: Null/blank `FL_DATE`, `OP_UNIQUE_CARRIER`, `OP_CARRIER_FL_NUM`, `ORIGIN`, `DEST`, `CRS_DEP_TIME` -> `QUARANTINED`.
- `test_reader_03_unparseable_fl_date_quarantined`: Invalid date (`2016-13-45`, `NOT_A_DATE`) -> `QUARANTINED:UNPARSEABLE_FL_DATE`.
- `test_reader_04_malformed_csv_lines_rejected`: Truncated (`<34` tokens) and over-wide (`>34` tokens) lines caught via `_corrupt_record` (`columnPruning.enabled=false`) -> `REJECTED:MALFORMED_CSV_ROW`.
- `test_reader_05_malformed_numeric_metric_accepted_with_null_cast`: `DEP_DELAY="NOT_A_NUMBER"` on valid-key row remains `ACCEPTED` and casts to `NULL` via `try_cast` (`DC-12`).
- `test_reader_06_overnight_flight_no_plus_24h_mutation`: Overnight flight (`CRS_DEP_TIME=2350`, `CRS_ARR_TIME=0115`) preserves `FL_DATE` temporal fields (`FP-DEC-007`).
- `test_reader_07_flight_num_decimal_zero_normalization`: `"1234.0"` -> `"1234"` (`FP-DEC-010`).
- `test_reader_08_mixed_batch_accounting_conservation`: Mixed batch of valid, quarantined, and rejected rows satisfies `source_rows_total == accepted + quarantined + rejected`.
- `test_reader_09_header_validation_fails_closed`: Wrong column count or reordered headers raise `ValueError`.
- `test_reader_10_empty_csv_header_only`: Header-only CSV produces `0 == 0 + 0 + 0` without crash.
- `test_reader_11_curated_schema_exact_match`: Output DataFrame matches `get_curated_schema()` across all 34 columns.

### 2.2 `tests/test_t007_locking.py` (`8` tests)
- `test_lock_01_acquire_and_release_lifecycle`: Exclusive creation and cleanup of `ingestion_writer.lock`.
- `test_lock_02_concurrent_contention_fails_closed`: Second writer raises `LockAcquisitionError` while active PID holds lock.
- `test_lock_03_stale_dead_pid_recovery_and_forensic_backup`: Dead PID lock is backed up to `.stale.<timestamp>.json` and recovered when `recover_stale=True`.
- `test_lock_04_corrupt_lock_file_fails_closed`: Malformed JSON lock file never silently deleted; raises `LockAcquisitionError`.
- `test_lock_05_context_manager_releases_on_exception`: `with SingleWriterLock(...)` cleans up lock on exception.
- `test_lock_06_invalid_run_id_rejected`: Empty/whitespace `run_id` rejected.
- `test_lock_07_win32_is_pid_alive_safety`: Verifies `is_pid_alive(os.getpid()) == True` and `is_pid_alive(99999999) == False` using Win32 `OpenProcess`/`GetExitCodeProcess` (never `os.kill(pid, 0)`).
- `test_lock_08_stale_recovery_disabled_fails_closed`: When `recover_stale=False`, even dead-PID locks raise `LockAcquisitionError`.

### 2.3 `tests/test_t007_pipeline_integration.py` (`7` tests)
- `test_int_01_full_end_to_end_synthetic_pipeline_success`: Multi-year (`2016`, `2024`) end-to-end synthetic run, state trace verification, `DC-11`/`DC-12` verification, `RunManifest` + `ExecutionReceipt` hash verification, `OR-05` & `OR-08` metadata checks.
- `test_int_02_unapproved_candidate_hashes_guard`: Unapproved candidate hashes (`LOCAL_HASH_COMPUTED_UNAPPROVED`) fail-closed when `require_verified_hashes=True` and succeed when `allow_candidate_hashes=True`.
- `test_neg_01_missing_source_file_fails_closed`: Missing CSV aborts at `SOURCE_VERIFICATION` and preserves prior `CURRENT_PUBLISHED_RUN.json`.
- `test_neg_02_source_size_mismatch_fails_closed`: Truncated CSV aborts at `SOURCE_VERIFICATION`.
- `test_neg_03_source_hash_mismatch_fails_closed`: Same-size byte flip triggers SHA-256 mismatch and aborts.
- `test_neg_04_duplicate_run_id_and_lock_contention`: Duplicate `run_id` and active lock contention fail-closed while preserving prior publication.
- `test_neg_05_fault_injection_corrupt_staging_and_recovery_retry`: Fault injection corrupting staging `.parquet` triggers `ABORTED_PRESERVED_PREVIOUS`, preserves prior pointer, and subsequent clean retry (`run_retry_ok`) succeeds.
