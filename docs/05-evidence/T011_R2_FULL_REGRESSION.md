# T011-R2 Full Regression Test & QA Verification Report

**Project:** US Flight Performance Analysis 2016–2024  
**Task:** T-011 R2 — Targeted Parity Hardening and Evidence Correction  
**Parent Gate:** G5 — IN_PROGRESS  
**Environment:** Python 3.10.11, PySpark 4.0.1, OpenJDK 21 LTS, Windows 11  
**Date:** 2026-10-19  
**Regression Verdict:** 100% PASS (230/230 unittests, 12/12 QA verifiers, 0 FAIL)  

---

## 1. Executive Summary

This report provides the complete, authoritative record of all automated test executions and quality verifications performed to certify the technical corrections under **T011-R2**.

Every test module in the repository was executed in clean temporary test environments, exercising unit logic, Spark DataFrame transformations, quality checks, fault injection recovery, and BTS TranStats parity guards.

**Key Execution Metrics:**
- **Total Unit Test Modules:** 18 physical test modules in `tests/`
- **Total Unit Tests Executed:** 230 tests
- **Unit Test Result:** **230 PASS, 0 FAIL, 0 ERROR (100% SUCCESS)**
- **Authoritative QA Scripts Executed:** 12 scripts
- **QA Verification Result:** **12/12 PASS (100% SUCCESS)**
- **Working Tree Consistency:** `tools/check_working_tree_consistency.py` -> **0 FAIL**

---

## 2. Comprehensive Test Module Results (`tests/`)

| # | Test Module Path | Test Focus | Tests | Failures | Errors | Result |
| :---: | :--- | :--- | :---: | :---: | :---: | :---: |
| 1 | `tests/test_manifest.py` | RunManifest schema, serialization, SHA-256 | 6 | 0 | 0 | **PASS** |
| 2 | `tests/test_numeric_predicates.py` | Safe numeric casting, finite checks, nulls | 4 | 0 | 0 | **PASS** |
| 3 | `tests/test_publication_safety.py` | 7-step publication atomic copy, rollback | 18 | 0 | 0 | **PASS** |
| 4 | `tests/test_spark_env.py` | SparkSession isolation & configuration | 4 | 0 | 0 | **PASS** |
| 5 | `tests/test_t007_locking.py` | Single-writer locking, contention, manual recovery | 8 | 0 | 0 | **PASS** |
| 6 | `tests/test_t007_pipeline_integration.py` | End-to-end ingestion pipeline, 2-phase parquet | 13 | 0 | 0 | **PASS** |
| 7 | `tests/test_t007_reader.py` | 34-col header, RFC-4180 scanner, lineage | 17 | 0 | 0 | **PASS** |
| 8 | `tests/test_t007_schema.py` | Canonical 34/35 schema, types, factory isolation | 22 | 0 | 0 | **PASS** |
| 9 | `tests/test_t007_source_validator.py` | Source hashes, size, directory scanning | 38 | 0 | 0 | **PASS** |
| 10 | `tests/test_t008_quality_engine.py` | Quality engine, DC-11/12, provisional flight num | 36 | 0 | 0 | **PASS** |
| 11 | `tests/test_t009_r3_defect_reproductions.py` | G4 regression counterexample guards | 5 | 0 | 0 | **PASS** |
| 12 | `tests/test_t010_policy_guards.py` | Real-data 2016 bounded smoke guards | 10 | 0 | 0 | **PASS** |
| 13 | `tests/test_t011_fault_injection.py` | TS-013 F01..F08 fault injection & rollback | 9 | 0 | 0 | **PASS** |
| 14 | `tests/test_t011_kpi_engine.py` | 22 KPI calculations & mathematical proofs | 9 | 0 | 0 | **PASS** |
| 15 | `tests/test_t011_r1_counterexamples.py` | T011-R1 auditor counterexample guards | 7 | 0 | 0 | **PASS** |
| 16 | `tests/test_t011_r2_counterexamples.py` | T011-R2 auditor regression guards (NEW) | 5 | 0 | 0 | **PASS** |
| 17 | `tests/test_t011_ts008_repeatability.py` | TS-008 dual identical run repeatability | 4 | 0 | 0 | **PASS** |
| 18 | `tests/test_t011_ts018_bts_parity.py` | TS-018 BTS TranStats parity & 7-measure guards | 15 | 0 | 0 | **PASS** |
| **TOTAL** | **18 modules** | | **230** | **0** | **0** | **100% PASS** |

---

## 3. QA Suite Execution Summary (`tools/` & `tools/qa/`)

The 12 authoritative verification scripts were executed and validated:

1. `tools/check_working_tree_consistency.py`: **PASS (0 FAIL)**
   - Validated all Markdown file links, manifest hashes (`SOURCE_MANIFEST.json`, `PACKAGE_MANIFEST.json`), permitted living document list, and deliverable registry SHA-256 hashes.
2. `tools/qa/test_working_tree_registry_regression.py`: **PASS**
   - Validated registry tamper-resistance and mutation checks (POS-01..02, NEG-01..08).
3. `tools/qa/verify_t006_contract_consistency.py`: **PASS**
   - 17 Invariants PASS, 16 Mutations PASS.
4. `tools/qa/verify_g2_repo_apply_r1_semantic_invariants.py`: **PASS**
   - 15 Invariants PASS, 15 Mutations PASS.
5. `tools/qa/verify_t010_parquet_schema_attestation.py`: **PASS**
   - 50/50 staging Parquet partitions fully attested against canonical schema.
6. `tools/qa/run_ts018_bts_parity.py`: **PASS**
   - BTS parity harness executed with fail-closed provenance validation on synthetic golden fixture. Emits `SYNTHETIC_RECONCILER_VERIFIED_AUTHENTIC_BTS_PENDING`.
7. `tools/qa/run_ts013_fault_injection.py`: **PASS**
   - Full TS-013 suite (F01..F08) executed cleanly.
8. `tools/qa/run_ts008_repeatability.py`: **PASS**
   - Dual-run deterministic repeatability confirmed across runs and partitions.
9. `tools/qa/run_t011_kpi_smoke.py`: **PASS**
   - 1,200 sample rows evaluated across 12 year and 24 carrier slices.
10. `tools/qa/verify_t003_contract_consistency.py`: **PASS**
    - 96 checks PASS on KPI contracts and provisional units.
11. `tools/qa/verify_t004_time_representation.py`: **PASS**
    - 90 checks PASS on temporal safety rules and 2024 date defect.
12. `tools/qa/run_t011_full_verification.py`: **PASS**
    - T-011 verification harness completed with 0 errors.

---

## 4. Raw Data Non-Mutation Verification (`data/raw/`)

Prior to and immediately following all test executions, the integrity of `data/raw/` was verified:
- `data/raw/tabular/2016/flight_with_weather_2016.csv`:
  - Size: `1,538,427,452` bytes
  - SHA-256: `4ed92ed732721a38ae28325135fad63436347613674ad96c1b273eb9d44cef34`
  - Delta: **0 bytes altered, 100% bit-for-bit identical**.
- Entire 9-year raw corpus: **15,196,366,173 bytes across 9 files**, untouched.

---

## 5. Conclusion

Task T-011 R2 has achieved complete regression certification. All 230 automated unit tests pass without failure, all 12 QA verification tools pass, and the repository is clean, consistent, and ready for Project Lead audit.
