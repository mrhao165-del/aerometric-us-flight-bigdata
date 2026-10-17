# T007_SIGNOFF_EXIT — FULL REGRESSION RESULTS

**Project:** US Flight Performance Analysis 2016–2024  
**Task:** `MASTER-T007-SIGNOFF-EXIT` (Section 6 Full Regression Execution)  
**Parent Gate:** `G4` (`PLANNED / NOT_COMPLETED`)  
**Execution Date:** 2026-10-17  

---

## 1. Unit & Synthetic Spark Integration Suite (`python -m unittest discover -s tests -p "test_*.py" -v`)

- **Raw Log Artifact:** `docs/05-evidence/T007_SIGNOFF_EXIT_LOG_UNITTEST_SUITE.txt`
- **Total Tests Executed:** `135` (`135 PASS`, `0 FAIL`, `0 ERROR`, `0 SKIP`)
- **Total Execution Duration:** `96.670s`
- **Exit Code:** `0`

| Test Module | Test Count | Pass | Fail | Skip | Scope Covered |
| :--- | ---: | ---: | ---: | ---: | :--- |
| `tests/test_manifest.py` | `7` | `7` | `0` | `0` | `RunManifest`, `RowAccounting`, `MetricAccounting`, `DC-11` / `DC-12` math |
| `tests/test_numeric_predicates.py` | `7` | `7` | `0` | `0` | Canonical metric validity predicates (`is_valid_arr_delay`, `is_valid_dep_delay`, etc.) |
| `tests/test_publication_safety.py` | `7` | `7` | `0` | `0` | `SafePublisher` 7-step atomic promotion, pointer preservation, rollback safety |
| `tests/test_spark_env.py` | `4` | `4` | `0` | `0` | PySpark 4.0.1 session bootstrap, UTC timezone, ANSI disabled, Arrow config |
| `tests/test_t007_locking.py` | `15` | `15` | `0` | `0` | `SingleWriterLock` Windows mutex (`O_CREAT \| O_EXCL`), stale recovery, reentrancy |
| `tests/test_t007_pipeline_integration.py` | `13` | `13` | `0` | `0` | `INT-01..07` & `NEG-01..06` (including `BLOCKER-02` Parquet type contract & `BLOCKER-03` missing manifest recovery + `MANUAL_RECONCILIATION_REQUIRED`) |
| `tests/test_t007_reader.py` | `17` | `17` | `0` | `0` | `RDR-01..17` (including `BLOCKER-01` RFC-4180 vs physical line scanner, `multi_line=False` fail-closed, Spark 4.0.1 escaped quotes & EOF without newline) |
| `tests/test_t007_schema.py` | `26` | `26` | `0` | `0` | `T007-01` 34-column canonical raw/parser/curated schemas, forbidden columns |
| `tests/test_t007_source_validator.py` | `34` | `34` | `0` | `0` | `T007-02` 9-year inventory, streaming SHA-256, TOCTOU, path/symlink/junction security |
| `tests/test_t009_r3_defect_reproductions.py` | `5` | `5` | `0` | `0` | `T-009` `F-01..04` defect regression suite |
| **TOTAL** | **`135`** | **`135`** | **`0`** | **`0`** | **100% Pass Rate (`EXIT_CODE = 0`)** |

---

## 2. Repository Governance & Semantic Invariant Verifiers (`tools/qa/*.py` & `tools/*.py`)

- **Raw Log Artifact:** `docs/05-evidence/T007_SIGNOFF_EXIT_LOG_QA_VERIFIERS.txt`

| Command Executed | Exit Code | Result Summary |
| :--- | ---: | :--- |
| `python tools/qa/verify_t006_contract_consistency.py` | `0` | `17 invariants + 16 mutations PASS, 0 FAIL` (All G3/T-006 contract invariants verified) |
| `python tools/qa/verify_g2_repo_apply_r1_semantic_invariants.py` | `0` | `15 invariants + 14 isolated mutations PASS, 0 FAIL` |
| `python tools/qa/test_t009_r1_validator_extension.py` | `0` | `8 PASS, 0 FAIL` (`BASE-01`, `NEG-01..04`, `POS-01..03`) |
| `python tools/qa/test_t009_unblock_r2_git_exclusion.py` | `0` | `7 PASS, 0 FAIL` (`POS-01..02`, `NEG-01..05`) |
| `python tools/qa/test_working_tree_registry_regression.py` | `0` | `16 PASS, 0 FAIL, 0 SKIP` (`POS-01..02`, `NEG-01..10B`, `MUT-NEG10-01..03`) |
| `python tools/check_working_tree_consistency.py` | `0` | `Working-Tree PASS assertions: 989; FAIL: 0` (All working-tree deliverables registered and hash-verified) |
