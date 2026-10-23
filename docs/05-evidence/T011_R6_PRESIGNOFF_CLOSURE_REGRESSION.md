# T011-R6 PRESIGNOFF CLOSURE FULL REGRESSION TEST MATRIX
## Complete Physical Inventory of 24 Test Modules and 346 Governed Tests

**Project:** US Flight Performance Analysis 2016–2024  
**Task:** T-011 R6 Pre-Signoff Closure  
**Parent Gate:** Gate G5 — `IN_PROGRESS` (Downstream Gate G6: `NOT_STARTED / BLOCKED` under `G2-EXC-001`)  
**Execution Authority:** AI Implementation Agent  
**Official Acceptance Authority:** Project Lead only.

---

## 1. Regression Test Inventory Overview

Following the implementation of Pre-Signoff Closure fixes (PC-F01, PC-F02, and PC-F03), the project's test suite contains **24 physical test modules** containing **346 independent unit and integration tests**.
All 346 tests execute deterministically and achieve **100% PASS (0 FAIL, 0 ERROR)**.

- **Total Test Modules:** 24
- **Total Test Cases:** 346
- **Total Assertions / Checks:** 346 test cases passed
- **Suite Execution Time:** 395.008s
- **Suite Exit Status:** OK

| # | Test Module Name | Primary Gate / Task Scope | Test Cases | Execution Status |
|---|---|---|---|---|
| 1 | `tests/test_manifest.py` | Manifest serialization, SHA-256, runtime detection | 6 | PASS |
| 2 | `tests/test_numeric_predicates.py` | IEEE-754 NaN/Inf, boundary values, DC-12 validation | 4 | PASS |
| 3 | `tests/test_publication_safety.py` | SafePublisher 7-step promotion, atomic pointer switch | 18 | PASS |
| 4 | `tests/test_spark_env.py` | SparkSession lifecycle, UTF-8 environment configuration | 4 | PASS |
| 5 | `tests/test_t007_locking.py` | SingleWriterLock concurrency, tokens, NTFS invariants | 8 | PASS |
| 6 | `tests/test_t007_pipeline_integration.py` | Multi-year pipeline lifecycle, DC-11 accounting, sidecars | 13 | PASS |
| 7 | `tests/test_t007_reader.py` | RawCsvReader line parsing, lineage tracking, boundary guards | 17 | PASS |
| 8 | `tests/test_t007_schema.py` | 34-column canonical schema conformance, Parquet types | 22 | PASS |
| 9 | `tests/test_t007_source_validator.py` | Source inventory, streaming SHA-256, symlink rejection | 38 | PASS |
| 10 | `tests/test_t008_quality_engine.py` | DC-11 3-state classification, forensic quarantine persistence | 36 | PASS |
| 11 | `tests/test_t009_r3_defect_reproductions.py` | T-009 R3 defect regression and boundary verifications | 5 | PASS |
| 12 | `tests/test_t010_policy_guards.py` | G4 stage isolation, read-only guards, unverified hashes | 10 | PASS |
| 13 | `tests/test_t011_fault_injection.py` | TS-013 publication fault injection, rollback, receipts | 9 | PASS |
| 14 | `tests/test_t011_kpi_engine.py` | TS-001..TS-007, TS-009..TS-012 CORE KPI engine logic | 9 | PASS |
| 15 | `tests/test_t011_r1_counterexamples.py` | T-011 R1 counterexample regression suite | 7 | PASS |
| 16 | `tests/test_t011_r2_counterexamples.py` | T-011 R2 counterexample regression suite | 5 | PASS |
| 17 | `tests/test_t011_r3_counterexamples.py` | T-011 R3 provenance boundary, lock recovery, BTS parser | 32 | PASS |
| 18 | `tests/test_t011_r4_counterexamples.py` | T-011 R4 lock safety, SHA-256, coordinator lifecycle | 26 | PASS |
| 19 | `tests/test_t011_r5_counterexamples.py` | T-011 R5 isolated atomic removal, TOCTOU, metadata format | 16 | PASS |
| 20 | `tests/test_t011_r6_counterexamples.py` | T-011 R6 replacement preservation, CoordinationLock serialization | 12 | PASS |
| 21 | `tests/test_t011_r6_presignoff.py` | PS-01 suppression, PS-02 attestation, PS-03 fstat fail-closed | 10 | PASS |
| 22 | `tests/test_t011_r6_presignoff_closure.py` | PC-F01 unresolved artifact exclusion & PC-F02 incident durability | 20 | PASS |
| 23 | `tests/test_t011_ts008_repeatability.py` | TS-008 exact bit-for-bit KPI calculation repeatability | 4 | PASS |
| 24 | `tests/test_t011_ts018_bts_parity.py` | TS-018 BTS TranStats parity parser & provisional units | 15 | PASS |
| **TOTAL** | **24 Test Modules** | **Full Pipeline, Quality, KPI, Fault & Recovery Matrix** | **346** | **ALL PASS** |

---

## 2. Pre-Signoff Closure Dedicated Coverage (`tests/test_t011_r6_presignoff_closure.py`)

| Test Case Name | Targeted Finding | Covered Failure Mode / Invariant |
|---|---|---|
| `test_pcf01_01_stale_del_blocks_subsequent_acquire` | PC-F01 | Presence of `.del_*` blocks new acquire with `UnresolvedRecoveryStateError` |
| `test_pcf01_02_stale_release_in_progress_blocks_acquire` | PC-F01 | Presence of `.release_in_progress_*` marker blocks new acquire |
| `test_pcf01_03_stale_failed_acq_blocks_acquire` | PC-F01 | Presence of `.failed_acq_*` marker blocks new acquire |
| `test_pcf01_04_stale_quarantine_blocks_acquire` | PC-F01 | Presence of `.quarantine_*` artifact blocks new acquire |
| `test_pcf01_05_permission_error_during_unlink_leaves_blocking_artifacts` | PC-F01 | Injected `unlink` `PermissionError` preserves staging/marker, blocks subsequent acquires |
| `test_pcf01_06_clean_release_removes_all_artifacts_allowing_subsequent_acquire` | PC-F01 | Clean release unlinks marker and staging; Run B acquires cleanly |
| `test_pcf01_07_authorized_recovery_resolution_unblocks_acquire` | PC-F01 | `resolve_recovery_state()` archives unresolved artifacts and allows clean acquire |
| `test_pcf01_08_recovery_resolution_records_manifest_and_hashes` | PC-F01 | Recovery resolution creates valid manifest JSON with artifact SHA-256 |
| `test_pcf01_09_recovery_resolution_requires_authorization` | PC-F01 | Unauthorized recovery resolution raises `PermissionError` |
| `test_pcf01_10_concurrent_writers_fail_closed_on_unresolved_recovery` | PC-F01 | Concurrency test: multiple threads fail closed when recovery is unresolved |
| `test_pcf02_01_truthful_incident_persistence_result_success` | PC-F02 | Successful write returns `IncidentPersistenceResult(success=True, verified=True)` |
| `test_pcf02_02_truthful_incident_persistence_result_failure_on_replace_error` | PC-F02 | Injected `replace` failure returns `IncidentPersistenceResult(success=False, verified=False)` |
| `test_pcf02_03_truthful_incident_persistence_result_failure_on_corrupt_readback` | PC-F02 | Corrupted readback triggers `IncidentPersistenceError` / false success rejection |
| `test_pcf02_04_exit_formats_incident_persistence_failure_truthfully` | PC-F02 | Context manager `__exit__` formats `INCIDENT_PERSISTENCE_FAILED` on write error |
| `test_pcf02_05_exit_formats_incident_persistence_success_truthfully` | PC-F02 | Context manager `__exit__` formats `Incident persisted at <path>` on success |
| `test_pcf02_06_coordinator_emits_incident_persistence_failure_truthfully` | PC-F02 | `run_ingestion` coordinator logs `INCIDENT_PERSISTENCE_FAILED` truthfully |
| `test_pcf02_07_coordinator_emits_incident_persistence_success_truthfully` | PC-F02 | `run_ingestion` coordinator logs `Release incident persisted at <path>` on success |
| `test_pcf02_08_reconcile_emits_incident_persistence_failure_truthfully` | PC-F02 | `reconcile_published_run` logs `INCIDENT_PERSISTENCE_FAILED` truthfully |
| `test_pcf02_09_reconcile_emits_incident_persistence_success_truthfully` | PC-F02 | `reconcile_published_run` logs `Release incident persisted at <path>` on success |
| `test_pcf02_10_atomic_incident_persistence_cleans_up_temp_on_error` | PC-F02 | Injected failure cleans up `.tmp` file and leaves no orphaned temporary writes |

---

## 3. Summary of Regression Guarantees

1. **Zero Regressions:** All 326 prior tests continue to pass 100% without modification or regression.
2. **20 Dedicated Pre-Signoff Closure Tests:** All 20 tests pass deterministically in `0.254s`.
3. **Total Coverage:** 346 tests across 24 modules verified.
4. **Authoritative Evidence Log:** Raw log captured in `docs/05-evidence/T011_R6_PRESIGNOFF_CLOSURE_RAW_UNITTEST_LOG.txt`.
