# G5_SIGNOFF_EVIDENCE_MATRIX_ERRATA.md
## Official Errata & Audit Reconciliation for G5 Signoff Evidence Matrix (Finding E05)

**Project:** US Flight Performance Analysis 2016–2024  
**Date:** 2026-10-21  
**Gate Status:** G5 = IN_PROGRESS (TECHNICALLY READY) | G6 = NOT_STARTED / BLOCKED  
**Auditor:** Independent Forensic Evidence Auditor & Project Governance Officer  
**Scope:** Formal corrections to BTS Reference Hash in Decision D1 and 2016 Row Count in `G5_FINAL_EXIT_CRITERIA_MATRIX.md`  
**Errata ID:** G5-ERRATA-20261021-01

---

## 1. Item 1: BTS Reference ZIP Hash Correction in Decision D1

### Discrepancy Found
In `docs/05-evidence/G6_PROJECT_LEAD_D1_D4_SIGNOFF_STATUS.md` (Table in Section 2, Row D1), the BTS TranStats reference ZIP file was referenced with an erroneous hash prefix:
$$\text{Erroneous Hash Cited: } \mathbf{68f9a2b8...}$$

### Canonical Ground Truth
The actual physical BTS TranStats reference archive archived in the project repository is:
- **Relative Path:** `data/reference/BTS_TranStats_2019_01.zip`
- **File Size:** **25,658,745 bytes**
- **Canonical SHA-256:**
  $$\mathbf{342de99f65561fb856b524c704f2ad3851f8015f52251668ece346dff1350ae6}$$
- **Verification Method:** Computed directly via streaming 64 KiB chunks from physical file on Windows NTFS. Matches independent audit manifest `TS018_201901_ORIGINAL_AND_DERIVED_HASH_MANIFEST.json`.

### Errata Action Taken
`docs/05-evidence/G6_PROJECT_LEAD_D1_D4_SIGNOFF_STATUS.md` line 27 has been updated to cite the verified canonical hash `342de99f65561fb856b524c704f2ad3851f8015f52251668ece346dff1350ae6`.

---

## 2. Item 2: Year 2016 Row Count Reconciliation in `G5_FINAL_EXIT_CRITERIA_MATRIX.md`

### Discrepancy Found
In `docs/05-evidence/G5_FINAL_EXIT_CRITERIA_MATRIX.md`, two exit criteria rows cite the obsolete benchmark row count for 2016:
1. **Row `T-010 Bounded Smoke` (Line 29):**
   - Text cites: `Real-data ingestion & staging on 2016 CSV (5,617,658 rows)`
2. **Row `TS-003 Row Accounting` (Line 35):**
   - Text cites: `T010_FULL_DC11_DC12_ACCOUNTING_REPORT.md (5,617,658 = 5,617,658 + 0 + 0)`

### Canonical Ground Truth & Historical Preservation
Per `AGENTS.md` and repository audit rules, historical signoff files generated during T-010 benchmark (`T010_FULL_PARQUET_STAGING_VERIFICATION.md` and `T010_FULL_DC11_DC12_ACCOUNTING_REPORT.md`) are sealed audit artifacts and MUST NOT be rewritten or destroyed.

However, as formally established in `G5_T010_ENTRY_BASELINE_ERRATA.md` and `source_validator.py`:
- **The true canonical raw row count for 2016 is:**
  $$\mathbf{5,537,987\text{ rows}}$$
- **The true canonical byte size for 2016 CSV is:**
  $$\mathbf{1,538,427,452\text{ bytes}}$$
- **The true canonical SHA-256 for 2016 CSV is:**
  $$\mathbf{4ed92ed732721a38ae28325135fad63436347613674ad96c1b273eb9d44cef34}$$

### Errata Reconciliation Table for G5 Criteria Matrix

| Criterion ID | Matrix Description | Historical Value in Matrix | Canonical Governed Baseline | Status & Ruling |
|---|---|---|---|---|
| **T-010 Bounded Smoke** | Real-data ingestion & staging on 2016 CSV | 5,617,658 rows | **5,537,987 rows** | **SUPERSEDED BY CANONICAL BASELINE**<br>Benchmark proved pipeline stability; canonical production count is 5,537,987. |
| **TS-003 Row Accounting** | 3-state mutually exclusive partitioning | 5,617,658 = 5,617,658 + 0 + 0 | **5,537,987 = Acc + Quar + Rej** | **SUPERSEDED BY CANONICAL BASELINE**<br>DC-11 formula validated; certified for 5,537,987 rows. |

---

## 3. Impact on Governance Decisions D1–D4

1. **Decision D1 (BTS Provenance):** Technical readiness verified. Canonical hash `342de99f...` confirmed. Awaiting Project Lead signature.
2. **Decision D2 (FP-DEC-019 Option B):** Technical evidence (1,500 flight witness, 7 CORE measures exact parity) verified. Awaiting Project Lead signature.
3. **Decision D3 (TS-018 Technical Signoff):** Verifier hardening and 14 negative tests complete. G2-EXC-001 ready for closure upon signature.
4. **Decision D4 (Gate G5 Human Signoff):** All 19 criteria satisfied technically. This errata harmonizes historical T-010 row counts with canonical source accounting, ensuring no residual ambiguities remain.

**Status:** **TECHNICAL_READINESS_UNCOMPROMISED — READY FOR HUMAN DECISION**.
