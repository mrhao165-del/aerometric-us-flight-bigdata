# T011-R2 Evidence Claim & Test Inventory Reconciliation Audit

**Project:** US Flight Performance Analysis 2016–2024  
**Task:** T-011 R2 — Targeted Parity Hardening and Evidence Correction  
**Parent Gate:** G5 — IN_PROGRESS  
**Component:** Evidence & Test Suite Governance  
**Audit Finding Addressed:** R2-F05 (Test module inventory, F06 description, and evidence claim discrepancies)  
**Date:** 2026-10-19  
**Status:** COMPLETE / 100% RECONCILED  

---

## 1. Executive Summary & Defect Remediation

During independent audit review of T011-R1, finding **R2-F05** identified discrepancies in evidence documentation:
1. **F06 Description Confusion:** Certain textual references loosely described test scenario F06 in terms of annual data ranges (e.g. 2017–2024), whereas the actual canonical definition of F06 in TS-013 is **"Pointer switch failure and non-destructive rollback"** (`test_f06_pointer_switch_failure_and_non_destructive_rollback`), which validates atomic pointer rollback to a prior valid run when a pointer switch failure is injected at Step 5.
2. **Test Module Inventory Ambiguity:** Prior reports cited "17 test modules" without clarifying whether `tools/qa/test_working_tree_registry_regression.py` was part of the standard `tests/` directory or an auxiliary QA script.

In T011-R2, all test module inventories, directory structures, and evidence claims have been comprehensively audited and reconciled.

---

## 2. Canonical Test Suite Inventory (tests/ Directory)

As of T011-R2, the repository contains exactly **18 test modules** inside the `tests/` directory, encompassing **230 unit tests**:

| # | Test Module Name | Gate Origin | Purpose | Test Count |
| :---: | :--- | :---: | :--- | :---: |
| 1 | `tests/test_manifest.py` | G4 | Run manifest & metadata serialization | 6 |
| 2 | `tests/test_numeric_predicates.py` | G4 | Safe numeric casting & null handling | 4 |
| 3 | `tests/test_publication_safety.py` | G4 | 7-step publication & rollback safety | 18 |
| 4 | `tests/test_spark_env.py` | G4 | SparkSession isolation & configuration | 4 |
| 5 | `tests/test_t007_locking.py` | G4 | Single-writer locking & manual recovery | 8 |
| 6 | `tests/test_t007_pipeline_integration.py` | G4 | End-to-end ingestion pipeline integration | 13 |
| 7 | `tests/test_t007_reader.py` | G4 | CSV parsing, 34-column header, logical scanner | 17 |
| 8 | `tests/test_t007_schema.py` | G4 | Schema contracts, 34/35 column definitions | 22 |
| 9 | `tests/test_t007_source_validator.py` | G4 | Source hash, size, and metadata verification | 38 |
| 10 | `tests/test_t008_quality_engine.py` | G4 | Quality engine, partition isolation, DC-11/12 | 36 |
| 11 | `tests/test_t009_r3_defect_reproductions.py` | G4 | G4 regression reproduction tests | 5 |
| 12 | `tests/test_t010_policy_guards.py` | G5 | Real-data 2016 bounded smoke guards | 10 |
| 13 | `tests/test_t011_fault_injection.py` | G5 | TS-013 F01..F08 fault injection suite | 9 |
| 14 | `tests/test_t011_kpi_engine.py` | G5 | 22 KPI calculations & mathematical proofs | 9 |
| 15 | `tests/test_t011_r1_counterexamples.py` | G5 | T011-R1 auditor counterexamples | 7 |
| 16 | `tests/test_t011_r2_counterexamples.py` | G5 | T011-R2 auditor regression guards (NEW) | 5 |
| 17 | `tests/test_t011_ts008_repeatability.py` | G5 | TS-008 dual identical run repeatability | 4 |
| 18 | `tests/test_t011_ts018_bts_parity.py` | G5 | TS-018 BTS TranStats parity & 7-measure guards | 15 |
| **TOTAL** | **18 modules** | | **All passing (100% OK)** | **230** |

---

## 3. Auxiliary QA Tools Inventory (`tools/qa/`)

The `tools/qa/` directory contains specialized governance and verification tools that are run as part of the authoritative QA suite, not standard unit discovery:

1. `tools/qa/test_working_tree_registry_regression.py`: verifies that all tracked files match hashes registered in `EVIDENCE_DELIVERABLE_REGISTER.json`.
2. `tools/qa/run_ts008_repeatability.py`: executes TS-008 repeatability verification across dual runs.
3. `tools/qa/run_ts013_fault_injection.py`: runs the full TS-013 fault injection harness.
4. `tools/qa/run_ts018_bts_parity.py`: runs TS-018 BTS TranStats reconciliation with companion provenance checking.
5. `tools/qa/run_t011_full_verification.py`: coordinator harness for T-011 verification deliverables.

---

## 4. Clarification of Fault Injection F06

To eliminate any residual ambiguity from prior reports:
- **Identifier:** `F06` (`test_f06_pointer_switch_failure_and_non_destructive_rollback`)
- **Domain:** Storage publication and transactional atomicity (`src/flight_pipeline/storage/publication.py`).
- **Mechanism:** Injects a simulated exception during Step 5 of the 7-step publication protocol (the atomic pointer switch).
- **Verified Behavior:**
  1. The target publication run (`run_b`) is cleanly aborted (`FAILED_POINTER_SWITCH`, Step 5).
  2. The active dataset pointer remains pointing to the prior valid published run (`run_a`).
  3. The prior published data files in `curated/runs/run_a` remain intact, parseable, and uncorrupted.
  4. Non-destructive rollback leaves no orphaned active pointers or corrupted symlinks/targets.

---

## 5. Conclusion

Finding **R2-F05** is **CLOSED / RESOLVED**. All test counts, module locations, and failure injection descriptions are fully aligned with the production code and evidence documentation.
