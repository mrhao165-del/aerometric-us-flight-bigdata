# T011 POST-CLOSURE FULL REGRESSION TEST MATRIX
## Complete Physical Inventory of 25 Test Modules and 364 Governed Tests

**Project:** US Flight Performance Analysis 2016–2024  
**Task:** T011-R6-POST-CLOSURE  
**Parent Gate:** Gate G5 — `IN_PROGRESS` (Downstream Gate G6: `NOT_STARTED / BLOCKED` under `G2-EXC-001`)  
**Execution Authority:** AI Implementation Agent  
**Official Acceptance Authority:** Project Lead only.

---

## 1. Regression Test Inventory Overview

Following the implementation of Post-Closure fixes (C1, C2, and C3), the project's test suite contains **25 physical test modules** containing **364 independent unit and integration tests**.
All 364 tests execute deterministically and achieve **100% PASS (0 FAIL, 0 ERROR)**.

- **Total Test Modules:** 25
- **Total Test Cases:** 364
- **Suite Execution Time:** 384.634s
- **Suite Result:** 364 PASS / 0 FAIL / 0 ERROR / 0 SKIP
- **Raw Execution Log:** `docs/05-evidence/T011_POST_CLOSURE_RAW_UNITTEST_LOG.txt` (120,634 bytes)

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
| 15 | `tests/test_t011_post_closure.py` | C1 recovery transaction hold/audit & C2 truthful diagnostics | 18 | PASS |
| 16 | `tests/test_t011_r1_counterexamples.py` | T-011 R1 counterexample regression suite | 7 | PASS |
| 17 | `tests/test_t011_r2_counterexamples.py` | T-011 R2 counterexample regression suite | 5 | PASS |
| 18 | `tests/test_t011_r3_counterexamples.py` | T-011 R3 provenance boundary, lock recovery, BTS parser | 32 | PASS |
| 19 | `tests/test_t011_r4_counterexamples.py` | T-011 R4 lock safety, SHA-256, coordinator lifecycle | 26 | PASS |
| 20 | `tests/test_t011_r5_counterexamples.py` | T-011 R5 isolated atomic removal, TOCTOU, metadata format | 16 | PASS |
| 21 | `tests/test_t011_r6_counterexamples.py` | T-011 R6 replacement preservation, CoordinationLock serialization | 12 | PASS |
| 22 | `tests/test_t011_r6_presignoff.py` | PS-01 suppression, PS-02 attestation, PS-03 fstat fail-closed | 10 | PASS |
| 23 | `tests/test_t011_r6_presignoff_closure.py` | PC-F01 staging unlink exclusion & PC-F02 incident durability | 20 | PASS |
| 24 | `tests/test_t011_ts008_repeatability.py` | TS-008 exact bit-for-bit KPI calculation repeatability | 4 | PASS |
| 25 | `tests/test_t011_ts018_bts_parity.py` | TS-018 BTS TranStats parity parser & provisional units | 15 | PASS |
| **TOTAL** | **25 Test Modules** | **Full Pipeline, Quality, KPI, Fault & Recovery Matrix** | **364** | **ALL PASS** |

---

## 2. Dedicated Post-Closure Coverage (`tests/test_t011_post_closure.py`)

All test function names below are directly enumerated from `tests/test_t011_post_closure.py` via Python reflection:

| Physical Method Name | Targeted Finding | Covered Failure Mode / Invariant | Result |
|---|---|---|---|
| `test_c1_01_recovery_record_cannot_be_created` | C1 | Permission error on resolution record preserves hold marker; blocks new writer | PASS |
| `test_c1_02_recovery_record_write_interrupted` | C1 | Short write on resolution record fails closed; blocks writer | PASS |
| `test_c1_03_recovery_record_fsync_fails` | C1 | `os.fsync` error fails closed; blocks writer | PASS |
| `test_c1_04_recovery_record_readback_mismatch` | C1 | Corrupted byte readback fails verification; blocks writer | PASS |
| `test_c1_05_partial_artifact_archival_fails` | C1 | Failure during artifact rename preserves hold marker; blocks writer | PASS |
| `test_c1_06_retry_after_partially_completed_recovery` | C1 | Retry after partial failure successfully recovers remaining artifacts and commits | PASS |
| `test_c1_07_new_writer_denied_until_verified_recovery_commit` | C1 | New writer denied acquisition while hold marker exists | PASS |
| `test_c1_08_successful_verified_recovery_permits_next_writer` | C1 | Full clean recovery lifecycle commits resolution and permits next writer | PASS |
| `test_c1_09_two_cooperative_processes_remain_mutually_exclusive` | C1 | CoordinationLock serializes recovery and writer acquisition | PASS |
| `test_c1_10_recovery_requires_explicit_authorization_and_operator` | C1 | Unauthorized or empty operator calls strictly rejected without disk writes | PASS |
| `test_c2_01_normal_exit_clean_release_no_incident` | C2 | Normal context exit releases lock cleanly with 0 incident files | PASS |
| `test_c2_02_normal_exit_release_fail_persist_success` | C2 | Normal exit + release failure + successful persist surfaces incident path | PASS |
| `test_c2_03_normal_exit_release_fail_persist_fail_surfaces_diagnostic` | C2 | Normal exit + release failure + persist failure surfaces `INCIDENT_PERSISTENCE_FAILED` | PASS |
| `test_c2_04_normal_exit_owner_mismatch_raises_lock_owner_release_failure` | C2 | Owner mismatch raises hybrid `LockOwnerReleaseFailureError` (matches both types) | PASS |
| `test_c2_05_block_exception_release_fail_persist_success` | C2 | Block exception + release failure + successful persist chains from block exception | PASS |
| `test_c2_06_block_exception_release_fail_persist_fail` | C2 | Block exception + release failure + persist failure surfaces `INCIDENT_PERSISTENCE_FAILED` | PASS |
| `test_c2_07_block_exception_normal_release_propagates_original` | C2 | Block exception + normal release propagates original exception unchanged | PASS |
| `test_c2_08_atomic_persistence_temp_files_cleaned_up` | C2 | Failed atomic incident persistence leaves no stray `.tmp_*` files behind | PASS |
