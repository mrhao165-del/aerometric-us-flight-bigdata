# G6 Official Governance Decision Mapping & TS-018 Seven Fields Errata

**Document ID:** `DOC-G6-ERRATA-GOV-001`  
**Classification:** PROJECT GOVERNANCE ERRATA & DECISION MAPPING CORRECTION  
**Task Reference:** Finding M05 / Gate G5 Exit & G6 Preflight Readiness  
**Supersedes:** Incorrect mappings in `docs/05-evidence/G6_D1_D5_HUMAN_DECISION_HANDOFF.md`  
**Date:** 2026-10-20  
**Evaluator:** Principal Big Data Architect, Independent Forensic Auditor & Project Governance Officer  
**Status:** OFFICIAL ERRATA ISSUED & RETRACTION RECORDED  

---

## 1. Context and Reason for Errata

In the previous draft of `docs/05-evidence/G6_D1_D5_HUMAN_DECISION_HANDOFF.md`, two significant governance deviations occurred:
1. **D-Decision Mapping Drift:** Decisions D1 through D4 were re-numbered and conflated with other architectural items (e.g. mapping the 2016 baseline architecture choice to D4, and moving TS-018 signoff to D1).
2. **Incorrect TS-018 Measures List:** The document erroneously listed identifier and schedule fields (`CRS_DEP_TIME`, `DEP_TIME`, `CRS_ARR_TIME`, `ARR_TIME`, `DISTANCE`) as the "seven TS-018 fields".

This formal errata document retracts those errors, restores the canonical decision mapping approved by the Project Lead in Gate G5 drafts, and reaffirms the exact 7 CORE measures evaluated under TS-018.

---

## 2. Canonical Governance Decision Mapping (D1–D5 & G6-ARCH-2016)

The authoritative decision numbering established in prior Gate G5 deliverables (`G5_D1_D4_CORRECTED_DRAFT_RECONCILIATION.md`, `G5_D1_D4_HUMAN_SIGNOFF_READINESS.md`) is restored as follows:

| Code | Canonical Decision Title | Scope and Mandate | Authorized Signatory | Current Status |
| :---: | :--- | :--- | :---: | :---: |
| **D1** | **BTS Source Provenance Attestation** | Attests the physical authenticity, lineage, and SHA-256 (`342de99f...`) of the official BTS TranStats January 2019 reference archive (`T_ONTIME_REPORTING_20261019_112232.zip`). | Project Lead | **PENDING_HUMAN_SIGNATURE** |
| **D2** | **FP-DEC-019 Approval (Option B)** | Formally approves Option B candidate intake parity for January 2019, certifying 1:1 numeric match across 1,500 sampled flight records. | Project Lead | **PENDING_HUMAN_SIGNATURE** |
| **D3** | **TS-018 Human Technical Signoff** | Formally accepts the independent audit results of Task TS-018 (witness verification, strict verifier, and 14 negative tests). Upon D3 signature, closes schema exception **G2-EXC-001**. | Project Lead | **PENDING_HUMAN_SIGNATURE** |
| **D4** | **Gate G5 Human Signoff** | Grants formal governance signoff to close Gate G5 (Intake & Lineage Verification). | Project Lead | **PENDING_HUMAN_SIGNATURE** |
| **D5** | **Gate G6 / T-012 Execution Authorization** | Grants formal authorization to initialize Gate G6 and execute the full 9-year production pipeline (T-012) across 54,674,003 records. | Project Lead | **BLOCKED / NOT_AUTHORIZED** |
| **G6-ARCH-2016** | **2016 Baseline Integration Architecture** | **Separate architectural decision** determining whether to re-ingest 2016 under verified schema (Option B, Recommended) or reuse frozen T-010 Parquet (Option A). **Does NOT replace D4.** | Project Lead | **RECOMMEND_OPTION_B** |

---

## 3. Retraction and Correction of the Seven TS-018 Core Measures

The 7 numerical measures evaluated for candidate-to-reference parity under Task TS-018 are strictly the **7 CORE delay and elapsed time measures** defined in `src/flight_pipeline/ingestion/schema.py` (`SEVEN_CORE_MEASURES`):

| Measure # | Canonical Field Name | Audited Meaning | Unit of Measure | Prior Draft Error |
| :---: | :--- | :--- | :---: | :--- |
| **1** | **`ARR_DELAY`** | Arrival delay | Minutes | Retained |
| **2** | **`DEP_DELAY`** | Departure delay | Minutes | Retained |
| **3** | **`TAXI_OUT`** | Taxi-out duration | Minutes | **Restored** (omitted in prior draft) |
| **4** | **`TAXI_IN`** | Taxi-in duration | Minutes | **Restored** (omitted in prior draft) |
| **5** | **`AIR_TIME`** | Airborne flight time | Minutes | **Restored** (omitted in prior draft) |
| **6** | **`ACTUAL_ELAPSED_TIME`** | Actual elapsed flight time | Minutes | **Restored** (omitted in prior draft) |
| **7** | **`CRS_ELAPSED_TIME`** | Scheduled elapsed flight time | Minutes | **Restored** (omitted in prior draft) |

> [!CAUTION]
> Fields such as `CRS_DEP_TIME`, `DEP_TIME`, `CRS_ARR_TIME`, `ARR_TIME`, and `DISTANCE` are flight identifiers, schedule strings, or distance measures. They were part of the 13-field match stratum key or parity candidate check, but are **NOT** the 7 CORE delay/time measures governed by TS-018 and `G2-EXC-001`.

---

## 4. Reaffirmation of Managed Governance Boundaries

1. **OR-08 (Kaggle Upstream Identity Unverified):**  
   Approval of FP-DEC-019 Option B confirms parity for January 2019 against the official BTS reference archive. It **does NOT** validate the upstream Kaggle release pipeline or publisher identity for 2016–2024. `OR-08` remains classified as `IDENTITY_UNVERIFIED`.
2. **OR-05 (2024 Partial Coverage):**  
   March 2024 remains absent from the raw dataset (335/366 days). The 2024 dataset status must strictly declare `source_coverage_status = 'PARTIAL'`. `OR-05` remains an `OPEN_QUALITY_DEFECT`.
3. **FP-DEC-017 (Weather Branch Exclusion):**  
   Weather data remains classified as `CONDITIONAL_NO_GO`. It is strictly excluded from all 8 CORE KPIs.
4. **G2-EXC-001 (Provisional Units Exception):**  
   Remains in state `ACTIVE` until the Project Lead officially signs decision **D3**. Upon D3 signoff, `G2-EXC-001` transitions to `CLOSED`.
5. **PARQUET_PARITY_NOT_TESTED:**  
   Parity has been proven for CSV and BTS reference ZIP. Curated Parquet numeric parity will be proven in Gate G6 following production ingestion.

---

## 5. Conclusion

This errata restores complete consistency across all project documentation. The official D1–D5 semantics and exact 7 TS-018 fields are now locked into the authoritative governance record.
