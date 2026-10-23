# T008 FULL RISK AND LIMITATION REGISTER

**Document ID:** `T008_FULL_RISK_AND_LIMITATION_REGISTER`  
**Parent Task:** `T-008 — Data Quality, Disjoint Row Accounting & Quarantine Engine`  
**Parent Gate:** `G4`  
**Classification:** `GOVERNANCE_RISK_AND_LIMITATION_RECORD`  
**Date:** 2026-10-18  

---

## 1. PRESERVED GOVERNANCE RISKS & CONDITIONS

| ID | Title | Status | Scope & Mitigation | Downstream Obligation |
|:---|:---|:---:|:---|:---|
| **OR-05** | Missing March 2024 Data | `OPEN_QUALITY_DEFECT` | 2024 dataset contains 335 of 366 days. No records fabricated. Labeled `PARTIAL`. | Stage checked in G4 (`T-008`); formal signoff `TS-004` at G6 (`T-012`). |
| **OR-08** | Local Hash Identity Limitation | `IDENTITY_UNVERIFIED` | Local SHA-256 hashes verify integrity against local files, not upstream BTS source identity. | Candidate manifest kept isolated; human review required. |
| **G2-EXC-001** | Provisional Units for 7 Measures | `PROVISIONAL` | Source units for 7 CORE measures remain provisional. Hard stop before G6. | Obligation `TS-018` BTS ground-truth sample reconciliation at Gate G5 (`T-011`). |
| **G3-COND-A** | Flight Number Quarantine Policy | `PROVISIONAL` | `OP_CARRIER_FL_NUM <= 0` is NOT hard-quarantined. Records remain `ACCEPTED` with anomaly flag. | Empirical frequency profiling on real data at G5 (`T-010`/`T-011`) prior to human signoff. |
| **FP-DEC-017** | Weather Column Optionality | `CONDITIONAL_NO_GO` | 6 weather columns optional; null values do NOT quarantine flights. Weather analysis excluded. | Maintained across G4–G7; verified by `test_qual_11`. |
| **CAND-SHA** | Candidate Raw CSV SHA-256 | `PENDING_HUMAN_ACCEPTANCE` | Calculated SHA-256 hashes in `T007_LOCAL_RAW_SHA256_CANDIDATE.json` await formal human signoff. | Cannot be merged into `SOURCE_MANIFEST.json` without authorization. |

---

## 2. TECHNICAL LIMITATIONS OF TASK T-008

1. **Synthetic Execution Only:** In Gate G4, all tests and validations were executed on synthetic test fixtures and unit tests. No PySpark jobs were executed on the full 54,674,003 raw rows.
2. **Real-Data Smoke Deferral:** Full bounded single-year smoke test on real 2016 CSV data is assigned to Task T-010 (Gate G5).
3. **No Self-Signoff:** Gate G4 and Task T-008 remain pending human review.
