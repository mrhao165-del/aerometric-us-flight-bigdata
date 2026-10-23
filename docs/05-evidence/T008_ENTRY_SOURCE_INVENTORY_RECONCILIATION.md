# T008 ENTRY SOURCE INVENTORY RECONCILIATION (DOC-01)

**Document ID:** `T008_ENTRY_SOURCE_INVENTORY_RECONCILIATION`  
**Parent Task:** `T-008 — Data Quality, Disjoint Row Accounting & Quarantine Engine`  
**Parent Gate:** `G4`  
**Supersession Scope:** Formally supersedes the erroneous per-year table in `docs/05-evidence/T007_FINAL_SIGNOFF_DOCUMENTATION_ERRATA.md` Section 3 without mutating sealed historical documents.  
**Classification:** `CANONICAL_INVENTORY_RECONCILIATION — RATIFIED_AGREEMENT`  
**Date:** 2026-10-18  

---

## 1. EXECUTIVE SUMMARY & INVESTIGATION OUTCOME

An independent audit identified a discrepancy between the per-year row counts and byte sizes presented in the documentation errata `docs/05-evidence/T007_FINAL_SIGNOFF_DOCUMENTATION_ERRATA.md` and the values embedded in:
1. Production code `AUDITED_SOURCE_INVENTORY` in [`src/flight_pipeline/ingestion/source_validator.py`](../../src/flight_pipeline/ingestion/source_validator.py)
2. Candidate hash manifest [`docs/05-evidence/T007_LOCAL_RAW_SHA256_CANDIDATE.json`](./T007_LOCAL_RAW_SHA256_CANDIDATE.json)

Both tables summed identically to:
- **Total Rows:** `54,674,003`
- **Total Bytes:** `15,196,366,173`

Because both sums match to the exact integer, total-only aggregate checks did not detect the per-year distribution mismatch.

### Root Cause Analysis
During the preparation of `T007_FINAL_SIGNOFF_DOCUMENTATION_ERRATA.md`, an obsolete pre-ingestion planning estimate table (originally drafted in `docs/05-evidence/T007_02_ENTRY_PREPARATION.md`) was accidentally copied into the documentation errata report instead of copying the canonical audited manifest numbers.

### Definitive Canonical Audit
An audit against the original Gate G1 schema manifests [`docs/05-evidence/inputs/schema_2016.json`](./inputs/schema_2016.json) through [`docs/05-evidence/inputs/schema_2024.json`](./inputs/schema_2024.json) proves conclusively:
- **Canonical G1 schema manifests match `AUDITED_SOURCE_INVENTORY` 100% across all 9 years.**
- **Canonical G1 schema manifests match `T007_LOCAL_RAW_SHA256_CANDIDATE.json` 100% across all 9 years.**
- **Unit test `test_inv_04_inventory_matches_g1_canonical_schema_manifests` in `tests/test_t007_source_validator.py` passes with zero discrepancies.**

**Conclusion:** The production code and candidate manifest are completely sound, verified, and in 100% alignment with G1 canonical evidence. There is **NO production code defect** and **NO canonical contract conflict**. This document formally supersedes the obsolete errata table and establishes the canonical per-year ground truth.

---

## 2. NINE-YEAR RECONCILIATION MATRIX

The table below reconciles all four representations for each of the 9 survey years (2016–2024):

| Year | Canonical G1 Schema Manifest (`schema_2016.json`..`schema_2024.json`) | Production `AUDITED_SOURCE_INVENTORY` (`source_validator.py`) | Candidate Manifest (`T007_LOCAL_RAW_SHA256_CANDIDATE.json`) | Obsolete Errata Table (`T007_FINAL_SIGNOFF_DOCUMENTATION_ERRATA.md`) | Reconciliation Status |
|:---:|:---|:---|:---|:---|:---:|
| **2016** | **Rows:** 5,537,987<br>**Bytes:** 1,538,427,452 | **Rows:** 5,537,987<br>**Bytes:** 1,538,427,452 | **Rows:** 5,537,987<br>**Bytes:** 1,538,427,452 | Rows: 5,617,658 (+79,671)<br>Bytes: 1,563,975,417 (+25,547,965) | **G1 MATCH (100%)** |
| **2017** | **Rows:** 5,575,872<br>**Bytes:** 1,549,837,485 | **Rows:** 5,575,872<br>**Bytes:** 1,549,837,485 | **Rows:** 5,575,872<br>**Bytes:** 1,549,837,485 | Rows: 5,674,621 (+98,749)<br>Bytes: 1,577,440,782 (+27,603,297) | **G1 MATCH (100%)** |
| **2018** | **Rows:** 6,986,842<br>**Bytes:** 1,941,406,432 | **Rows:** 6,986,842<br>**Bytes:** 1,941,406,432 | **Rows:** 6,986,842<br>**Bytes:** 1,941,406,432 | Rows: 7,213,446 (+226,604)<br>Bytes: 2,004,500,642 (+63,094,210) | **G1 MATCH (100%)** |
| **2019** | **Rows:** 7,161,827<br>**Bytes:** 1,990,370,667 | **Rows:** 7,161,827<br>**Bytes:** 1,990,370,667 | **Rows:** 7,161,827<br>**Bytes:** 1,990,370,667 | Rows: 7,422,037 (+260,210)<br>Bytes: 2,062,711,819 (+72,341,152) | **G1 MATCH (100%)** |
| **2020** | **Rows:** 4,312,091<br>**Bytes:** 1,197,858,795 | **Rows:** 4,312,091<br>**Bytes:** 1,197,858,795 | **Rows:** 4,312,091<br>**Bytes:** 1,197,858,795 | Rows: 4,688,354 (+376,263)<br>Bytes: 1,302,488,407 (+104,629,612) | **G1 MATCH (100%)** |
| **2021** | **Rows:** 5,755,666<br>**Bytes:** 1,600,032,487 | **Rows:** 5,755,666<br>**Bytes:** 1,600,032,487 | **Rows:** 5,755,666<br>**Bytes:** 1,600,032,487 | Rows: 5,992,674 (+237,008)<br>Bytes: 1,666,039,837 (+66,007,350) | **G1 MATCH (100%)** |
| **2022** | **Rows:** 6,413,416<br>**Bytes:** 1,782,648,882 | **Rows:** 6,413,416<br>**Bytes:** 1,782,648,882 | **Rows:** 6,413,416<br>**Bytes:** 1,782,648,882 | Rows: 6,701,551 (+288,135)<br>Bytes: 1,862,804,785 (+80,155,903) | **G1 MATCH (100%)** |
| **2023** | **Rows:** 6,645,461<br>**Bytes:** 1,847,433,387 | **Rows:** 6,645,461<br>**Bytes:** 1,847,433,387 | **Rows:** 6,645,461<br>**Bytes:** 1,847,433,387 | Rows: 6,731,374 (+85,913)<br>Bytes: 1,886,130,467 (+38,697,080) | **G1 MATCH (100%)** |
| **2024** | **Rows:** 6,284,841<br>**Bytes:** 1,748,350,586 | **Rows:** 6,284,841<br>**Bytes:** 1,748,350,586 | **Rows:** 6,284,841<br>**Bytes:** 1,748,350,586 | Rows: 4,632,288 (-1,652,553)<br>Bytes: 1,270,274,017 (-478,076,569) | **G1 MATCH (100%)** |
| **TOTAL** | **Rows:** 54,674,003<br>**Bytes:** 15,196,366,173 | **Rows:** 54,674,003<br>**Bytes:** 15,196,366,173 | **Rows:** 54,674,003<br>**Bytes:** 15,196,366,173 | **Rows:** 54,674,003 (Net diff: 0)<br>**Bytes:** 15,196,366,173 (Net diff: 0) | **100% EQUIVALENT** |

---

## 3. FORMAL RATIFICATION & GOVERNANCE STATUS

1. **Ratified Canonical Baseline:** The canonical per-year row counts and byte sizes for the 9-year dataset are those specified in the G1 schema manifests and `AUDITED_SOURCE_INVENTORY`:
   - 2016: 5,537,987 rows | 1,538,427,452 bytes
   - 2017: 5,575,872 rows | 1,549,837,485 bytes
   - 2018: 6,986,842 rows | 1,941,406,432 bytes
   - 2019: 7,161,827 rows | 1,990,370,667 bytes
   - 2020: 4,312,091 rows | 1,197,858,795 bytes
   - 2021: 5,755,666 rows | 1,600,032,487 bytes
   - 2022: 6,413,416 rows | 1,782,648,882 bytes
   - 2023: 6,645,461 rows | 1,847,433,387 bytes
   - 2024: 6,284,841 rows | 1,748,350,586 bytes
   - Total: 54,674,003 rows | 15,196,366,173 bytes
2. **Preservation of Sealed Records:** In accordance with repository policies (`AGENTS.md`), historical audit documents (`T007_FINAL_SIGNOFF_DOCUMENTATION_ERRATA.md`) remain immutable; this document serves as the binding supersession record.
3. **Preservation of Governance Invariants:**
   - `OR-08 = IDENTITY_UNVERIFIED`: The local SHA-256 hashes and file size checks prove integrity against the local audited files, not upstream BTS identity.
   - Candidate SHA-256 hashes remain `PENDING_HUMAN_ACCEPTANCE`.
   - Raw CSV files in `data/raw/` remain strictly untouched and unread during synthetic development.
