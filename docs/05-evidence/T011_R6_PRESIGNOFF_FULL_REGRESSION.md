# T011-R6 PRESIGNOFF FULL REGRESSION TEST MATRIX
## Complete Physical Inventory of 23 Test Modules and 326 Governed Tests

**Project:** US Flight Performance Analysis 2016–2024  
**Task:** T-011 Pre-Signoff Addendum  
**Gate:** G5 — `IN_PROGRESS` (Downstream Gate G6: `NOT_STARTED / BLOCKED` under `G2-EXC-001`)  
**Execution Authority:** AI Implementation Agent  
**Official Acceptance Authority:** Project Lead only.

---

## 1. Regression Test Inventory Overview

Following the implementation of Pre-Signoff Addendum fixes (PS-01, PS-02, PS-03), the project's test suite has expanded to **23 physical test modules** containing **326 independent unit and integration tests**.

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
| 22 | `tests/test_t011_ts008_repeatability.py` | TS-008 exact bit-for-bit KPI calculation repeatability | 4 | PASS |
| 23 | `tests/test_t011_ts018_bts_parity.py` | TS-018 BTS TranStats parity parser & provisional units | 15 | PASS |
| **TOTAL** | **23 Test Modules** | **Full Pipeline, Quality, KPI, Fault & Recovery Matrix** | **326** | **ALL PASS** |

---

## 2. Pre-Signoff Addendum Dedicated Coverage (`tests/test_t011_r6_presignoff.py`)

| Test Case Name | Targeted Finding | Covered Failure Mode / Invariant |
|---|---|---|
| `test_ps01_01_normal_release_clean_exit` | PS-01 | Context manager exit releases lock cleanly without error |
| `test_ps01_02_owner_mismatch_raises_in_exit` | PS-01 | Owner mismatch raises `LockOwnerMismatchError`, persists incident |
| `test_ps01_03_permission_io_failure_raises_in_exit` | PS-01 | Isolated rename I/O failure raises `LockError`, persists incident |
| `test_ps01_04_pipeline_exception_with_release_failure_chains` | PS-01 | Exception in block + release failure chains via `LockReleaseFailureError` from `exc_val` |
| `test_ps01_05_pipeline_exception_with_normal_release_propagates` | PS-01 | Exception in block with normal release propagates original exception unchanged |
| `test_ps01_06_coordinator_already_published_preserves_outputs_on_release_error` | PS-01 / FP-DEC-PROP-018 | Successful publication preserved (`success=True`), release incident persisted |
| `test_ps01_07_coordinator_pipeline_failure_preserves_original_error` | PS-01 | Pipeline failure preserves original error message and appends release diagnostic |
| `test_ps01_08_reconcile_published_run_records_release_incident` | PS-01 | `reconcile_published_run` records release error and persists incident report |
| `test_ps02_all_27_canonical_documents_attested` | PS-02 | Verifies existence, non-emptiness, and SHA-256 for all 27 markdown documents |
| `test_ps03_fstat_failure_leaves_incomplete_lock_fail_closed` | PS-03 | Injected `fstat` failure leaves 0-byte file, fails closed, and requires manual recovery |

---

## 3. Summary of Regression Guarantees

1. **Zero Regressions:** 316 historical unit and integration tests continue to pass 100% without regression.
2. **10 Dedicated Presignoff Tests:** All 10 tests pass deterministically in `< 0.3s`.
3. **Total Coverage:** 326 tests across 23 modules verified.
