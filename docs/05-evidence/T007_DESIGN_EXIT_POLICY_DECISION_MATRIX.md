# T007 DESIGN EXIT POLICY DECISION MATRIX — CANONICAL DISPOSITION & G3-COND-A

**Document ID:** `DOC-T007-DESIGN-EXIT-01-POLICY-MATRIX`  
**Task ID:** `T-007` (Raw CSV Ingestion Pipeline)  
**Phase:** `DESIGN RECONCILIATION (R1-EXIT)`  
**Gate:** `G4` (`PLANNED / NOT_COMPLETED`)  
**Design Authority:** Senior Big Data Architect & Canonical Data Contract Auditor  
**Binding Standards:** [`G3_OFFICIAL_SIGNOFF_HUMAN_ACCEPTANCE_RECORD.md`](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/docs/05-evidence/G3_OFFICIAL_SIGNOFF_HUMAN_ACCEPTANCE_RECORD.md) §3.1 (`G3-COND-A`), `DATA_CONTRACT.md` (DC-11, DC-12)  

---

## 1. GOVERNANCE MANDATE: G3-COND-A PROVISIONAL BOUNDARY

In strict accordance with the Human Project Lead's binding acceptance conditions recorded in `G3_OFFICIAL_SIGNOFF_HUMAN_ACCEPTANCE_RECORD.md` §3.1:
1. **Provisional Nature of Record-Level Quarantine:**
   The policy of isolating whole records at ingestion (`record-level quarantine`) is formally a **provisional candidate technical proposal**, NOT an approved hard rule for the whole pipeline.
2. **Prohibition of Automatic Hard Quarantine for Flight Numbers:**
   `OP_CARRIER_FL_NUM <= 0` **must never automatically become a hard quarantine rule** without empirical distribution surveying and data validation on raw data in `G4/T-008`.
3. **Strict DC-11 Tri-State Accounting:**
   The pipeline enforces strictly three mutually exclusive accounting buckets:
   $$N_{\text{raw}} = N_{\text{accepted}} + N_{\text{quarantined}} + N_{\text{rejected}}$$
   **No fourth accounting state exists.** Any pending policy decision maps into these three states with an explicit governance annotation (`POLICY_DECISION_PENDING`).

---

## 2. EXHAUSTIVE DISPOSITION MATRIX FOR CANDIDATE ANCHORS & ANOMALIES

The following matrix provides the definitive disposition for all candidate identity anchors, anomalies, and edge cases, strictly delineating approved rules from provisional proposals:

| Scenario / Token Case | Raw Example | Accounting Disposition (DC-11) | Policy Governance Status | Technical Ingestion Action in T-007 | Required Validation in G4/T-008 |
|---|---|---|---|---|---|
| **1. Invalid / Unparseable `FL_DATE`** | `"2018-02-31"` or `"CORRUPT"` | **`QUARANTINED`** | `APPROVED_CANDIDATE_ANCHOR` | Classified into quarantine dataset (`INVALID_FL_DATE_CORE_ANCHOR`). Record has valid 34-col CSV syntax but cannot be anchored to calendar day. | T-008 confirms full calendar day counts. |
| **2. Missing / Null `FL_DATE`** | `""` or `null` | **`QUARANTINED`** | `APPROVED_CANDIDATE_ANCHOR` | Classified into quarantine dataset (`MISSING_FL_DATE_CORE_ANCHOR`). | T-008 confirms prevalence. |
| **3. Missing / Null `OP_CARRIER`** | `""` or `null` | **`QUARANTINED`** | `APPROVED_CANDIDATE_ANCHOR` | Classified into quarantine dataset (`MISSING_CARRIER_CORE_ANCHOR`). Cannot attribute flight to any reporting carrier. | T-008 confirms carrier distribution. |
| **4. Missing / Null `ORIGIN` or `DEST`** | `""` or `null` or $\neq 3$ chars | **`QUARANTINED`** | `APPROVED_CANDIDATE_ANCHOR` | Classified into quarantine dataset (`MISSING_AIRPORT_CORE_ANCHOR`). Cannot attribute origin/destination airport. | T-008 confirms route topology. |
| **5. Null Flight Number** | `""` or `null` | **`QUARANTINED`** | `PROVISIONAL_PENDING_T008` | Classified into provisional quarantine (`PROVISIONAL_NULL_FL_NUM`). Preserves flight identity boundary pending survey. | T-008 surveys exact frequency across 54.7M rows. |
| **6. Flight Number Equals Zero** | `"0"` or `0.0` | **`ACCEPTED`** (with Flag) | `PROVISIONAL_PENDING_T008` | **NOT quarantined.** Ingested into curated dataset with column flag `fl_num_zero_flag = True`. Counted in `count_records` (KPI-01). | T-008 profiles carrier context to determine if 0 represents charter/ferry. |
| **7. Negative Flight Number** | `"-105"` | **`ACCEPTED`** (with Flag) | `PROVISIONAL_PENDING_T008` | **NOT quarantined.** Ingested into curated dataset with column flag `fl_num_neg_flag = True`. Counted in `count_records` (KPI-01). | T-008 investigates whether negative represents upstream coding anomaly. |
| **8. Fractional Flight Number** | `"1234.5"` | **`ACCEPTED`** (with Flag) | `PROVISIONAL_PENDING_T008` | **NOT silently truncated.** Ingested with `fl_num_fractional_flag = True`. Stored as integer `1234` only if fractional part is `.0`; otherwise flagged. | T-008 surveys if fractional values exist in raw CSVs. |
| **9. Non-Numeric Flight Number** | `"DL102"` | **`QUARANTINED`** | `PROVISIONAL_PENDING_T008` | Cast to integer yields `null`; treated under Null Flight Number policy (`PROVISIONAL_NULL_FL_NUM`). | T-008 checks raw token distribution. |
| **10. Metric Measure Negative Delay** | `DEP_DELAY = -15.0` | **`ACCEPTED`** | `APPROVED_CANONICAL_VALUE` | Fully accepted. Negative delay represents valid early departure. Included in delay metrics. | Verified in G5 (`TS-006`). |
| **11. Metric Measure Invalid / Non-Finite** | `AIR_TIME = -5.0` or `NaN` | **`ACCEPTED`** | `APPROVED_CANONICAL_RULE` | **Record remains ACCEPTED** in `count_records`. Excluded **only** from specific submetric denominator via `is_finite_numeric`. | Verified in G5 (`TS-008`, `TS-018`). |
| **12. Auxiliary Weather Missing** | `O_TEMP = null` | **`ACCEPTED`** | `APPROVED_CANONICAL_RULE` | Fully accepted. Weather is optional (`FP-DEC-017` CONDITIONAL_NO_GO); zero impact on core KPI pipeline. | Verified in G5 (`TS-011`). |
| **13. Malformed Physical Line** | Unclosed quote / corrupted byte stream | **`REJECTED`** | `APPROVED_CANONICAL_RULE` | Classified into `rejected_row_count`. Never enters structured DataFrame. Captured in `rejected/` raw text store. | DC-11 row accounting balance verified. |

---

## 3. OPEN DEPENDENCY MANAGEMENT

1. **Strict Sequencing:** Decisions on whether provisional anomalies (e.g. `OP_CARRIER_FL_NUM <= 0`) should be converted to hard quarantine rules remain formally **`POLICY_DECISION_PENDING`**.
2. **No Premature T-008 Execution:** Task T-007 design implements the flag columns and measurement hooks, but does **NOT** execute data profiling or alter canonical contracts prior to Task T-008.

---

## 4. POLICY DECISION MATRIX VERDICT

The policy matrix strictly enforces `G3-COND-A`, eliminates unauthorized hard quarantine, maintains the three-state DC-11 accounting boundary, and clearly marks pending decisions for T-008 data validation.

**POLICY MATRIX VERDICT: FULLY RECONCILED WITH G3-COND-A.**
