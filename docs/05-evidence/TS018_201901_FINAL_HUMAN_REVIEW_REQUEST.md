# TS018 CANDIDATE INTAKE & PARITY — FINAL HUMAN REVIEW REQUEST
## Formal Submission of Technical Evidence & Controlled Decision Options to Project Lead

**Project:** US Flight Performance Analysis 2016–2024  
**Date:** 2026-10-20 (Asia/Ho_Chi_Minh)  
**Parent Gate:** Gate G5 (`IN_PROGRESS`)  
**Parent Task:** Task T-011 / TS-018  
**Governing Authority:** Project Lead (Exclusive Human Signoff Authority)  
**Submitted By:** Principal Big Data Engineer & Independent Data Lineage Auditor  
**Candidate Evaluation Result:** `NUMERICAL_PARITY_VERIFIED = True` (0 Discrepancies)  
**Formal Gating Verdict:** **`BLOCKED_2019_CURATED_PARQUET_MISSING`**  
**Gate Status:** **Gate G5 remains `IN_PROGRESS`** | **Gate G6 remains `NOT_STARTED / BLOCKED`**

---

## 1. Submission Purpose

Under approved exception **`G2-EXC-001`**, design decision **`FP-DEC-018`**, and the controlled signoff of Task T-011 ([`T011_OFFICIAL_CONTROLLED_TECHNICAL_SIGNOFF_20261019.md`](T011_OFFICIAL_CONTROLLED_TECHNICAL_SIGNOFF_20261019.md)), this dossier formally submits the candidate intake, forensic verification, and record-level numeric parity results for TS-018 to the Project Lead for human review and policy decision.

---

## 2. Preserved Authoritative Baseline

The implementation agent has maintained all authoritative project baselines without modification:
- **Gate G2:** `PASS`.
- **Gate G3:** `PASS`.
- **Gate G4:** `PASS (CONTROLLED)`.
- **Task T-010:** `PASS / COMPLETED (CONTROLLED)`.
- **Policy FP-DEC-018:** `APPROVED_WITH_CONDITIONS`.
- **Task T-011 Technical Implementation:** `PASS / SIGNED_OFF (CONTROLLED)`.
- **Task T-011 Full Contract Closeout:** `PENDING_TS018`.
- **Specification TS-018:** `OPEN (BLOCKING_G5_EXIT)`.
- **Exception G2-EXC-001:** `ACTIVE`.
- **Gate G5:** `IN_PROGRESS`.
- **Gate G6:** `NOT_STARTED / BLOCKED`.
- **Seven CORE Measures Unit Status:** `OFFICIAL_MINUTES_EMPIRICALLY_CONSISTENT_PROVISIONAL`.
- **Raw Data Invariants:** Exactly `15,196,366,173` bytes across 108 CSVs (2016–2024); delta: `0 bytes` (100% untouched).
- **Staging Parquet Invariants:** Exactly 50 Parquet files from T-010 (2016 runs) preserved with schema fingerprint `b5805fcae8db44e9a53c0eb1dfa1c1f3d9ec2983b3922bfbe5c6454f1654b09a`.
- **Production Latest Pointer:** Intact, untouched.

---

## 3. Summary of Technical Evidence Produced

| Deliverable Artifact | Description & Forensic Status | Gating Value |
|---|---|---|
| [`TS018_201901_SOURCE_INTAKE_AND_PROVENANCE.md`](TS018_201901_SOURCE_INTAKE_AND_PROVENANCE.md) | Physical file inspection, ZIP SHA-256 (`342de99f...`), uncompressed CSV SHA-256 (`dce92e...`), 108 columns, 583,985 rows. | Forensics Verified; Provenance Unauthenticated (`False`) |
| [`TS018_201901_ORIGINAL_AND_DERIVED_HASH_MANIFEST.json`](TS018_201901_ORIGINAL_AND_DERIVED_HASH_MANIFEST.json) | Governed manifest registering reference ZIP and provenance companion. | Whitelist Inventory Registered |
| [`TS018_201901_REFERENCE_POLICY_ERRATA.md`](TS018_201901_REFERENCE_POLICY_ERRATA.md) | Narrow erratum correcting column count claim (109 $\rightarrow$ 108) and documenting `.gitignore` / checker hardening. | Policy Hardening Recorded |
| [`TS018_201901_PARQUET_READONLY_SOURCE_ATTESTATION.md`](TS018_201901_PARQUET_READONLY_SOURCE_ATTESTATION.md) | Staging inventory confirming exclusively 2016 Parquet and reporting missing 2019 curated Parquet. | `BLOCKED_2019_CURATED_PARQUET_MISSING` |
| [`TS018_201901_KEY_COVERAGE_AND_SAMPLE_PROTOCOL.md`](TS018_201901_KEY_COVERAGE_AND_SAMPLE_PROTOCOL.md) | Population overlap (559,136 matched keys, 100.0% coverage of dataset) and stratified sample protocol ($N=1,500$). | Deterministic Protocol Documented |
| [`TS018_201901_SEVEN_FIELD_PARITY_REPORT.md`](TS018_201901_SEVEN_FIELD_PARITY_REPORT.md) | Record-level reconciliation of 10,500 field comparisons using `BtsTranStatsReconciler`: 0 mismatches, 0 rounding diffs. | `NUMERICAL_PARITY_VERIFIED = True` |
| [`TS018_201901_DISCREPANCY_REGISTER.csv`](TS018_201901_DISCREPANCY_REGISTER.csv) | Machine-readable log of field-level discrepancies: 0 discrepancy rows. | Clean Discrepancy Register |
| [`TS018_201901_RAW_RUN_LOG.txt`](TS018_201901_RAW_RUN_LOG.txt) | Complete CLI stdout/stderr logs, timestamps, environment, and exit codes. | Full Reproducibility Trail |

---

## 4. Separation of Governance States

```text
================================================================================
GOVERNANCE & PROVENANCE EVALUATION MATRIX
================================================================================
  1. FILE_PRESENT:                 TRUE  (ZIP and CSV forensically verified)
  2. SCHEMA_VALID:                  TRUE  (108 uppercase columns, all 7 measures & 5 keys present)
  3. COMPANION_METADATA_VALID:      FALSE (PENDING_APPROVAL in companion JSON)
  4. CANDIDATE_CHECKSUM_MATCHED:    TRUE  (342de99f... matched)
  5. SOURCE_PROVENANCE_VERIFIED:    FALSE (Requires external human authentication)
  6. NUMERICAL_PARITY_VERIFIED:     TRUE  (10,500 / 10,500 comparisons exact, 0 discrepancies)
  7. HUMAN_ACCEPTED:                FALSE (Exclusive authority of Project Lead)
================================================================================
VERDICT: SYNTHETIC_RECONCILER_VERIFIED_AUTHENTIC_BTS_PENDING
GATE G5: IN_PROGRESS
GATE G6: NOT_STARTED / BLOCKED (under G2-EXC-001)
================================================================================
```

---

## 5. Explicit Decisions Requested from Project Lead

The Project Lead is respectfully requested to review the dossier and render decisions on the following three points:

### Decision Point 1: Controlled Resolution of the Missing Curated 2019 Parquet
The physical staging directory contains only 2016 Parquet runs. Please select one of the following two approved pathways:
- **Option A:** Authorize acquiring the official BTS **January 2016** download archive to execute a bit-exact record-level reconciliation directly against the already attested, immutable 2016 staging Parquet (`smoke_2016_jan_*`).
- **Option B:** Formally accept the completed bounded read-only January 2019 raw source comparison ([`TS018_201901_SEVEN_FIELD_PARITY_REPORT.md`](TS018_201901_SEVEN_FIELD_PARITY_REPORT.md)) as satisfying the unit verification requirement of TS-018 without requiring staging publication.

### Decision Point 2: Independent Authentication of External BTS Provenance
Review the external acquisition receipt, download URL session, and operator identity for candidate archive `T_ONTIME_REPORTING_20261019_112232.zip`. If verified authentic:
- Transition `bts_transtats_201901.provenance.json` from `PENDING_APPROVAL` to `APPROVED_BY_PROJECT_LEAD`.

### Decision Point 3: Formal Gate Signoff
If Decision Points 1 and 2 are satisfied:
- Authorize the formal closure of **TS-018** (`PASS`).
- Authorize the full contract closeout of **Task T-011** (`FULL_CONTRACT_CLOSEOUT = PASS`).
- Authorize the resolution of exception **`G2-EXC-001`** (`RESOLVED`).
- Authorize the transition of **Gate G5** from `IN_PROGRESS` to `PASS`.

Until the Project Lead explicitly signs off on these items, all gating guards remain actively enforced.
