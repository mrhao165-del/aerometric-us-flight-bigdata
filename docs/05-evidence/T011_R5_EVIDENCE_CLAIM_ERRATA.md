# T011-R5 Evidence Claim Errata and Historical Reconciliation

**Project:** US Flight Performance Analysis 2016–2024  
**Task:** T-011 R5 — Lock Safety Closure and Evidence Reconciliation  
**Parent Gate:** G5 — `IN_PROGRESS`  
**Finding Reference:** `R5-F03` (Evidence Accuracy and Regression Inventory)  
**Date:** 2026-10-19  

---

## 1. Executive Summary

In accordance with `AGENTS.md` and the Master Execution Prompt for T011-R5, historical evidence reports from earlier gates and remediation cycles are immutable and must not be retroactively modified or rewritten. Instead, this authoritative superseding errata document records all discrepancies identified by the independent technical auditor regarding prior evidence claims, establishes exact physical baselines, and reconciles all claims against verified physical artifacts and raw execution logs.

---

## 2. Reconciled Evidence Discrepancies

### Erratum R5-ERR-01: Physical Test Module Inventory (20 vs 14)
* **Historical Claim (T011-R4 Report):** The R4 regression report claimed the test suite comprised 14 test modules and named several non-existent or generic module names.
* **Physical Reality:** In T011-R4, the physical repository contained exactly **20** `tests/test_*.py` files discovering **288** tests. In T011-R5, with the addition of `tests/test_t011_r5_counterexamples.py`, the repository contains exactly **21** `tests/test_*.py` files discovering **304** tests.
* **Complete Physical Test Module Inventory (21 Modules, 304 Tests):**
  1. `test_manifest.py`: 6 tests
  2. `test_numeric_predicates.py`: 4 tests
  3. `test_publication_safety.py`: 18 tests
  4. `test_spark_env.py`: 4 tests
  5. `test_t007_locking.py`: 8 tests
  6. `test_t007_pipeline_integration.py`: 13 tests
  7. `test_t007_reader.py`: 17 tests
  8. `test_t007_schema.py`: 22 tests
  9. `test_t007_source_validator.py`: 38 tests
  10. `test_t008_quality_engine.py`: 36 tests
  11. `test_t009_r3_defect_reproductions.py`: 5 tests
  12. `test_t010_policy_guards.py`: 10 tests
  13. `test_t011_fault_injection.py`: 9 tests
  14. `test_t011_kpi_engine.py`: 9 tests
  15. `test_t011_r1_counterexamples.py`: 7 tests
  16. `test_t011_r2_counterexamples.py`: 5 tests
  17. `test_t011_r3_counterexamples.py`: 32 tests
  18. `test_t011_r4_counterexamples.py`: 26 tests
  19. `test_t011_r5_counterexamples.py`: 16 tests
  20. `test_t011_ts008_repeatability.py`: 4 tests
  21. `test_t011_ts018_bts_parity.py`: 15 tests
  * **Total Discovered & Passing Tests:** **304**

### Erratum R5-ERR-02: KPI Smoke Runner Scope (Synthetic vs Physical Staging)
* **Historical Claim (T011-R4 Summary):** Verbal summaries loosely referenced the KPI smoke runner without explicitly highlighting data source boundaries.
* **Physical Reality:** `tools/qa/run_t011_kpi_smoke.py` generates an in-memory synthetic Spark DataFrame consisting of exactly 1,200 records across 4 synthetic flights and computes the 8 CORE KPIs. It does NOT read from physical staging or curated Parquet files. Physical Parquet staging remains immutable and governed under Gate G4/T-010.

### Erratum R5-ERR-03: Actual QA Command Inventory
* **Historical Claim (T011-R4 Summary):** The conversational text in the R4 completion handoff listed older Gate G2/G4 QA verifier script names (`verify_g2_clean_room.py`, etc.) rather than the actual scripts executed in `docs/05-evidence/T011_R4_RAW_QA_LOG.txt`.
* **Physical Reality:** The actual raw QA execution log `docs/05-evidence/T011_R4_RAW_QA_LOG.txt` executed exactly the following 12 commands (all exit code 0):
  1. `python tools/qa/verify_t006_contract_consistency.py`
  2. `python tools/qa/verify_g2_repo_apply_r1_semantic_invariants.py`
  3. `python tools/qa/verify_t010_parquet_schema_attestation.py`
  4. `python tools/qa/run_ts018_bts_parity.py`
  5. `python tools/qa/run_t011_kpi_smoke.py`
  6. `python tools/qa/verify_t003_contract_consistency.py`
  7. `python tools/qa/verify_t004_time_representation.py`
  8. `python tools/qa/test_t007_spark_csv_reproduction.py`
  9. `python tools/qa/test_t009_unblock_r2_git_exclusion.py`
  10. `python tools/qa/test_working_tree_registry_regression.py`
  11. `python tools/qa/test_t009_r1_validator_extension.py`
  12. `python tools/check_working_tree_consistency.py`

### Erratum R5-ERR-04: Deliverable Register Physical Count
* **Physical Reality:** `docs/05-evidence/EVIDENCE_DELIVERABLE_REGISTER.json` physically contained 591 registered items at R4 close. In R5, this register is expanded to incorporate all new R5 evidence deliverables and updated hashes.

---

## 3. Strict Boundary Distinctions

To ensure zero ambiguity during technical audits, the following six categories are maintained strictly separate:
1. **Actual Production Source Code:** Physical `.py` files in `src/flight_pipeline/`.
2. **Actual Executed Logs:** Verbatim UTF-8 execution records (`T011_R5_RAW_UNITTEST_LOG.txt`, `T011_R5_RAW_QA_LOG.txt`).
3. **Test Source Coverage:** Physical tests residing in `tests/test_*.py`.
4. **Agent Analytical Reports:** Analytical assessments stored in `docs/05-evidence/`.
5. **Physical Data Validation:** Read-only audits of source CSVs and immutable staging.
6. **Human Signoff:** Official determinations reserved exclusively for the Project Lead.
