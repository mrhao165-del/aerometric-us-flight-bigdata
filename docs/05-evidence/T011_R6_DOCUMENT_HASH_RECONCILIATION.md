# T011-R6 Canonical Document Hash & Reading Attestation Reconciliation

**Project:** US Flight Performance Analysis 2016–2024  
**Task:** T-011 R6 — Controlled Final Lock Safety Closure  
**Finding Reference:** R6-F03 (Documentation Attestation Discrepancy)  
**Parent Gate:** G5 — `IN_PROGRESS`  
**Authority:** Project Lead only.  

---

## 1. Forensic Root Cause Analysis

During independent review of the `T011_R5_REVIEW_PACKAGE.zip`, the independent auditor detected that Table 1 of `docs/05-evidence/T011_R5_BASELINE_AND_DOCUMENT_AUDIT.md` listed byte counts and SHA-256 hashes that did not match the physical files packaged in the repository.

A forensic audit of repository history reveals:
1. In **T011-R4** (`docs/05-evidence/T011_R4_BASELINE_AND_DOCUMENT_AUDIT.md`), the attestation was computed directly from the live filesystem using an automated disk scanning script. The byte counts and hashes (`README.md` = 3,946 bytes, `DATA_CONTRACT.md` = 7,238 bytes, `KPI_SPEC.md` = 9,949 bytes, `TEST_PLAN.md` = 6,346 bytes) matched the physical files with 100% precision.
2. In **T011-R5**, during the generation of `T011_R5_BASELINE_AND_DOCUMENT_AUDIT.md`, an unverified markdown table was populated with estimated/synthesized numbers rather than freshly executed filesystem measurements. The physical files on disk were never modified to those hallucinated sizes; rather, the report table itself was erroneous.
3. In **T011-R6**, we have implemented automated verification via `scratch/audit_r6_baseline.py` that reads every file byte-for-byte and computes the cryptographic SHA-256 digest directly from the disk.

---

## 2. Side-by-Side Reconciliation Table

The table below compares the erroneous R5 attestation against the authentic R4 baseline and the verified current R6 physical filesystem:

| Document Path | R5 Erroneous Claim | R4 Authentic Record | Current R6 Physical Size | Current R6 Physical SHA-256 | Forensic Status |
| :--- | :---: | :---: | :---: | :---: | :--- |
| `AGENTS.md` | 3,923 | 4,178 | **4,178** | `4b97c977133acff8...` | Preserved from R4 physical baseline |
| `README.md` | 13,833 | 3,946 | **3,946** | `3c5032ea72b4f322...` | Preserved from R4 physical baseline |
| `START_HERE.md` | 13,101 | 2,396 | **2,396** | `7b46e77572cdd89e...` | Preserved from R4 physical baseline |
| `docs/01-planning/PRD.md` | 11,540 | 5,249 | **5,249** | `f0290800a354a94e...` | Preserved from R4 physical baseline |
| `docs/01-planning/ROADMAP.md` | 10,740 | 3,865 | **3,865** | `d46dbb64d73340a2...` | Preserved from R4 physical baseline |
| `docs/01-planning/BACKLOG.md` | 16,357 | 13,563 | **13,664** | `67847fde3ede9798...` | Updated in living governance (13664 vs 13563) |
| `docs/02-design/ARCHITECTURE.md` | 21,056 | 21,056 | **21,056** | `14cf55d044681498...` | Preserved from R4 physical baseline |
| `docs/02-design/ANALYSIS_PROTOCOL.md` | 15,372 | 3,452 | **3,452** | `873fb4bf568b3adf...` | Preserved from R4 physical baseline |
| `docs/02-design/DATA_CONTRACT.md` | 15,312 | 7,238 | **7,238** | `2f831cbd71f177f9...` | Preserved from R4 physical baseline |
| `docs/02-design/DATA_DICTIONARY.md` | 15,108 | 6,081 | **6,081** | `c4e729f40db80371...` | Preserved from R4 physical baseline |
| `docs/02-design/DECISIONS.md` | 21,647 | 21,647 | **21,647** | `bede7f51e95a832b...` | Preserved from R4 physical baseline |
| `docs/02-design/KPI_SPEC.md` | 17,466 | 9,949 | **9,949** | `bf4a663485c6416a...` | Preserved from R4 physical baseline |
| `docs/03-quality/TEST_PLAN.md` | 16,929 | 6,346 | **6,346** | `bc77f3d9d82b75af...` | Preserved from R4 physical baseline |
| `docs/03-quality/RISK_REGISTER.md` | 19,812 | 11,376 | **11,376** | `55c5a46d682cfd5b...` | Preserved from R4 physical baseline |
| `docs/03-quality/ROLLBACK_PLAN.md` | 13,010 | 1,850 | **1,850** | `a27227da7b8db7ff...` | Preserved from R4 physical baseline |
| `docs/04-execution/AI_HANDOFF.md` | 14,845 | 17,329 | **17,329** | `c1d7ae6469570f3d...` | Preserved from R4 physical baseline |

---

## 3. Formal Supersession & Errata Verdict

1. **Formal Supersession:** Table 1 of `T011_R5_BASELINE_AND_DOCUMENT_AUDIT.md` is hereby formally declared superseded and corrected by `T011_R6_BASELINE_AND_DOCUMENT_AUDIT.md` and this document.
2. **Physical Immutability Confirmed:** The underlying canonical documents in `docs/` and repository root were not corrupted or tampered with; their physical integrity is fully preserved.
3. **Living Governance Updates:** Living documents (`PROJECT_STATE.md`, `BACKLOG.md`, `CHANGELOG.md`) have evolved across R4 $\to$ R5 $\to$ R6 as expected by repository governance protocols, and their exact SHA-256 hashes are sealed in `EVIDENCE_DELIVERABLE_REGISTER.json`.
4. **Verification Invariant:** Any auditor can independently reproduce every SHA-256 hash in `T011_R6_BASELINE_AND_DOCUMENT_AUDIT.md` directly against the files in `T011_R6_REVIEW_PACKAGE.zip`.
