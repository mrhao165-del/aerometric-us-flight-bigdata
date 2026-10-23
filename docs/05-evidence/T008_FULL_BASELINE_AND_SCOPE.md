# T008 FULL BASELINE AND SCOPE SPECIFICATION

**Document ID:** `T008_FULL_BASELINE_AND_SCOPE`  
**Parent Task:** `T-008 — Data Quality, Disjoint Row Accounting & Quarantine Engine`  
**Parent Gate:** `G4`  
**Execution Mode:** Full Technical Implementation, Automated Verification, Final Human Signoff Readiness  
**Target Status:** `T008_READY_FOR_HUMAN_SIGNOFF`  
**Date:** 2026-10-18  

---

## 1. MISSION AND GOVERNANCE BASELINE

### 1.1. Executive Mission
Under the direct authorization of the Human Project Lead, this mission executes the complete technical implementation and synthetic verification of **Task T-008**:
- Construction of the production Data Quality Engine operating downstream of T-007 ingestion.
- Enforcement of `DC-11` three-state disjoint row accounting ($N_{raw} = N_{acc} + N_{quar} + N_{rej}$) verified against independent ground truth.
- Enforcement of `DC-12` metric validity vs record validity separation on all 7 CORE measures.
- Compliance with `G3-COND-A`: retention of `OP_CARRIER_FL_NUM <= 0` as provisional, non-quarantined, with impact profiling.
- Compliance with `OR-05` and `FP-DEC-002`: calendar date coverage analyzer detecting the missing 31 days of March 2024.
- Compliance with `FP-DEC-017`: weather absence permitted without quarantine of valid CORE flights.
- Complete documentation reconciliation of `DOC-01` (9-year source inventory), `DOC-02` (working-tree assertion counts), and `DOC-03` (handoff errata).

### 1.2. Baseline Commit & Governance State
- **Git Commit Baseline:** `bc4f03fb8ccd6c0b2455af3fcb2b1b98fa39d632` (after T-007 signoff recording).
- **Gate G2:** `PASS` (Human Signoff recorded, `G2-EXC-001` preserved requiring `TS-018` at G5).
- **Gate G3:** `PASS` (Human Signoff recorded, `G3-COND-A/B/C` preserved).
- **Task T-006:** `PASS / COMPLETED`.
- **Task T-009:** `PASS (Controlled)`.
- **Task T-007:** `PASS / COMPLETED — CONTROLLED` (Ingestion pipeline completed on synthetic fixtures).
- **Task T-008:** In transition to `T008_READY_FOR_HUMAN_SIGNOFF`.
- **Gate G4:** Remains `PLANNED / NOT_COMPLETED` pending formal human review of T-008.
- **Gates G5 / G6:** `NOT_STARTED`.

---

## 2. STRICT INVARIANTS & BOUNDARIES

1. **No Self-Signoff:** The Agent does not declare `T-008 PASS` or `G4 PASS`. All evidence is prepared for Human Project Lead review.
2. **Immutable Raw Data:** Zero modifications to `data/raw/` CSV files or historical audit JSON/MD manifests.
3. **Synthetic Execution Only:** In G4, all PySpark tests run on bounded synthetic fixtures. No Spark jobs are executed against the 54.7M real dataset.
4. **Provisional Policy Protection (G3-COND-A):** Non-positive flight numbers (`OP_CARRIER_FL_NUM <= 0`) are NOT hard-quarantined in default policy.
5. **Weather Optionality (FP-DEC-017):** The 6 weather columns are not required for flight record acceptance.
6. **Candidate Hashes Isolated:** Candidate raw CSV SHA-256 hashes remain strictly isolated in `T007_LOCAL_RAW_SHA256_CANDIDATE.json` with status `CANDIDATE_PENDING_HUMAN_ACCEPTANCE`.
