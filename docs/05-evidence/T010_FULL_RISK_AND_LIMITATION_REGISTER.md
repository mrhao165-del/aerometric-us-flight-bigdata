# T010_FULL_RISK_AND_LIMITATION_REGISTER.md — Living Risk & Limitation Register (Gate G5 / T-010)

**Gate:** G5  
**Task:** T-010 — Bounded Real-Data Smoke & Resource Benchmark  
**Author:** Repository Governance Engineer & Risk Auditor  
**Execution Timestamp:** 2026-10-18T11:07:20+00:00 (2026-10-18T18:07:20+07:00)  
**Status:** ACTIVE LIVING REGISTER  

---

## 1. Overview & Context

This register documents the operational risks, workstation resource constraints, and active governance conditions relevant to Gate G5 and Task T-010.

---

## 2. Active Risk Analysis & Post-T010 Status

| Risk ID | Title / Scope | Pre-T010 Status | Post-T010 Status | Empirical Finding & Mitigation |
| :--- | :--- | :--- | :--- | :--- |
| **OR-01** | Workstation Memory Exhaustion during multi-million row processing | `MEDIUM` | `CONTROLLED (LOW)` | Empirical benchmark measured peak driver RSS at `211 MB` and JVM heap at `468 MB` (< 12% of 4 GB budget), providing >8x headroom. |
| **OR-02** | Staging Directory I/O Contention & Disk Spill | `MEDIUM` | `CONTROLLED (LOW)` | Snappy compression achieved `4.63:1` ratio (316 MB output for 1.54 GB CSV); zero disk spills recorded in `tmp_spark`. |
| **OR-05** | Missing March 2024 Retrospective Defect | `OPEN_QUALITY_DEFECT` | `OPEN_QUALITY_DEFECT` | Re-affirmed as an open defect for survey year 2024 (335/366 days). 2016 verified clean (366/366 days observed). |
| **OR-08** | Upstream BTS / NOAA Provenance Identity Status | `IDENTITY_UNVERIFIED` | `IDENTITY_UNVERIFIED` | Candidate hash `4ed92e...` verified locally on snapshot; upstream provenance remains unverified pending human signoff. |
| **G2-EXC-001** | Provisional Units Status for 7 CORE Measures | `PROVISIONAL` | `PROVISIONAL` | Maintained as provisional. Mandatory TS-018 physical unit verification remains a required hard stop at G5 before Gate G6. |
| **FP-DEC-017** | Weather Branch Optionality | `CONDITIONAL_NO_GO` | `CONDITIONAL_NO_GO` | Verified that absence or nulls in weather columns does NOT quarantine flight records. |
| **G3-COND-A** | Flight Number Non-Positive Policy | `PROVISIONAL` | `PROVISIONAL` | In 2016, 0 non-positive flight numbers were detected. Hard quarantine remains blocked in production mode. |

---

## 3. Workstation Hardware Limitations

1. **Local Single-Node Execution (`local[4]`):**
   - Workstation has 8 physical / 16 logical cores and 15.71 GB RAM (with ~4.2 GB available at start).
   - Ingestion of 2016 took 49.22 seconds.
   - The projected duration for the full 9-year dataset (54.67M rows) is ~8.1 minutes, well within reasonable development execution bounds.
2. **Sequential Multi-Year Execution Recommendation:**
   - To avoid Windows NTFS file handle exhaustion and memory pressure, full multi-year ETL in T-011 should process years sequentially or with strict per-year checkpoints rather than opening all 9 large CSVs simultaneously.
3. **Scratch Storage Path:**
   - Scratch directory must remain permanently mapped to `D:\Study\Code\Apache\Flight_Analyzt\tmp_spark\` outside Git tracking.

---

## 4. Governance Gate Hand-off Constraints

1. **T-010 Exit Condition:**
   - Completion of T-010 does NOT authorise starting T-011 (Full Pipeline Execution) or Gate G6.
   - Project Lead human review of `T010_FULL_COMPLETION_REVIEW_PACKAGE.zip` is strictly required before opening T-011.
2. **TS-018 Mandatory Stop:**
   - Gate G5 cannot achieve `PASS` until TS-018 unit verification is performed and formally ratified.
