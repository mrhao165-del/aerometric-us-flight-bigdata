# T007_FULL_BASELINE_AND_SCOPE — Repository Baseline & Scope Boundary Audit

**Document ID:** `T007_FULL_BASELINE_AND_SCOPE.md`  
**Date:** 2026-10-17  
**Task:** `T-007` — Raw CSV Ingestion Pipeline (End-to-End Implementation)  
**Parent Gate:** `G4` (`PLANNED / NOT_COMPLETED`)  
**Status:** `T007_READY_FOR_HUMAN_SIGNOFF`  
**Author:** Principal Big Data Architect & Repository Governance Auditor  

---

## 1. Repository & Git Entry Baseline

- **Entry Git Branch:** `master`
- **Entry Git Commit HEAD:** `dc96861d7400fa5324774fd19ac9a894e34db510`
- **Working Tree State at Entry:** Clean (`0` uncommitted changes, `0` untracked stray files).
- **Runtime Environment:**
  - **OS:** Windows 10/11 Local (`os.name == 'nt'`)
  - **Python:** `3.10.11`
  - **PySpark:** `4.0.1`
  - **Java:** `21`
  - **Spark Resource Budget (`SparkConfig`):** `local[4]`, Driver Memory `4g`, Memory Overhead `1g`, Shuffle Partitions `16`, Compression `snappy`, Timezone `UTC`.

---

## 2. Approved Governance Baseline

| Gate / Task | Official Status | Authoritative Evidence Reference |
| :--- | :---: | :--- |
| **Gate G2** | `PASS` | `G2_OFFICIAL_SIGNOFF_HUMAN_ACCEPTANCE_RECORD.md` |
| **Gate G3** | `PASS` | `G3_OFFICIAL_SIGNOFF_HUMAN_ACCEPTANCE_RECORD.md` |
| **Task T-006** | `PASS / COMPLETED` | `T006_FINAL_CORRECTIONS_ADDENDUM.md` |
| **Task T-009** | `PASS / COMPLETED` *(Controlled)* | `T009_HUMAN_SIGNOFF_20261017.md` |
| **Subtask T007-01** | `PASS / COMPLETED` *(Controlled)* | `T007_01_HUMAN_SIGNOFF_20261017.md` |
| **Subtask T007-02A** | `READY_FOR_HUMAN_SIGNOFF` | `T007_02A_SECDELTA_FINAL_VERDICT.md` |
| **Task T-007 (Full)** | `T007_READY_FOR_HUMAN_SIGNOFF` | Consolidated in `T007_FULL_*` evidence suite |
| **Task T-008** | `NOT_STARTED` | Quality Engine reserved for subsequent G4 task |
| **Gate G4** | `PLANNED / NOT_COMPLETED` | Awaits T-007 & T-008 completion and human gate signoff |

---

## 3. Canonical Scope Boundary: T-007 (G4) vs. T-010 (G5) & T-012 (G6)

Per the canonical hierarchy of authority (`AGENTS.md` $\rightarrow$ Official Signoffs $\rightarrow$ `BACKLOG.md` / `TEST_PLAN.md`):

1. **T-007 (Gate G4 — Raw CSV Ingestion Pipeline):**
   - Encompasses `T007-01` (Canonical Schema), `T007-02A/B` (Source Inventory & Real Local Streaming SHA-256 Baseline), `T007-03` (Raw CSV Reader & Record Classification), `T007-04` (Windows Single-Writer Locking), `T007-05` (Ingestion Coordinator & Sidecar ExecutionReceipt), `T007-06` (Unit, Integration, and Fault-Injection Testing), and `T007-07` (Bounded Synthetic Multi-Year Integration Smoke).
2. **T-008 (Gate G4 — Data Quality & Validation Engine):**
   - Owns comprehensive statistical profiling, full quality rule evaluation, and quarantine policy finalization. T-007 implements the ingestion boundary and DC-11/DC-12 interfaces without pre-empting T-008.
3. **T-010 (Gate G5 — Real 1-Year Smoke Test & Benchmark):**
   - Earlier design drafts mentioned a 2016 one-year smoke inside T007-07. Reconciling against authoritative `BACKLOG.md`, full Spark ingestion of the 5.54M-row 2016 CSV (`TS-014`) and full-scale fault injection (`TS-013`) are strictly governed under **Task T-010 at Gate G5**.
4. **T-012 (Gate G6 — Full 9-Year Production ETL):**
   - Full 54,674,003-row Spark ingestion is strictly governed under **Task T-012 at Gate G6**, gated behind mandatory `TS-018` unit verification (`G2-EXC-001`).
