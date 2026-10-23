# TS-018 January 2019 — Corrected Candidate Readiness Dossier
## Targeted Evidence Closure, Two-Source Replay Attestation, and Gate Governance State

**Project:** US Flight Performance Analysis 2016–2024  
**Date:** 2026-10-20 (Asia/Ho_Chi_Minh)  
**Parent Task:** Task T-011 / TS-018  
**Parent Gate:** Gate G5 (`IN_PROGRESS`)  
**Auditor References:** `TS018_201901_INDEPENDENT_AUDIT_20261020.md`, Findings TS018-I01, TS018-I02, TS018-I03  
**Status:** **AWAITING PROJECT LEAD & INDEPENDENT REVIEWER EVALUATION**  

---

## 1. Executive Summary

This dossier documents the targeted closure of the three evidence findings identified in the independent review of TS-018 candidate results (`TS018_201901_INDEPENDENT_AUDIT_20261020.md`):

1. **TS018-I01 (HIGH — Unsupported record examples) CLOSED:**
   - Obsolete narrative examples (`DL 1142 ATL->LGA`, `AA 2401 DFW->ORD`, `WN 582 DEN->PHX`) were reproduced as absent from the physical BTS file and formally superseded via [`TS018_201901_EVIDENCE_CORRECTION_ERRATA.md`](TS018_201901_EVIDENCE_CORRECTION_ERRATA.md).
   - Replaced strictly with 3 programmatically verified authentic flight records present in both physical sources (`NK 314 IAH->TPA`, `UA 753 SFO->EWR`, `AA 692 PHX->HNL`), with all 7 numeric fields matching exactly.

2. **TS018-I02 (MEDIUM/HIGH — False stratum representation) CLOSED:**
   - Investigated and documented the true population distribution: within the 559,136 matched operating flights, there are **0 records with null `ARR_DELAY`** because cancelled (`CANCELLED == 1.0`, 16,726) and diverted (`DIVERTED == 1.0`, 1,296) flights are excluded upstream per `DATA_CONTRACT.md` (DC-11).
   - Reported exact strata counts in [`TS018_201901_ACTUAL_STRATUM_AND_KEY_AUDIT.md`](TS018_201901_ACTUAL_STRATUM_AND_KEY_AUDIT.md): 358,420 negative delay (500 sampled), 10,284 zero delay (200 sampled), 190,432 positive delay (700 sampled), 0 null delay (0 sampled), and 100 remainder top-up flights.
   - Categorized the 6,827 unmatched active BTS flights factually without unproven causal claims of weather filtering.

3. **TS018-I03 (MEDIUM — Lack of machine-readable witness & duplicate protection) CLOSED:**
   - Both physical sources verified via SHA-256 and byte sizes before execution.
   - Raw row counts, unique keys, and duplicate occurrences tracked independently: 0 duplicate keys on project dataset side, 0 duplicate keys on BTS side.
   - Exported [`TS018_201901_MATCHED_SAMPLE_WITNESS.csv`](TS018_201901_MATCHED_SAMPLE_WITNESS.csv) containing all 1,500 sampled flight keys, strata, SHA-256 selection scores, and all 14 paired numeric values.
   - Authored and verified independent replay script [`tools/qa/verify_ts018_two_source_sample_witness.py`](../../tools/qa/verify_ts018_two_source_sample_witness.py), confirming 10,500 / 10,500 exact matches against both physical sources directly.

---

## 2. Separation of Governance States

Per `AGENTS.md` and `docs/02-design/DECISIONS.md`, candidate technical verification is strictly decoupled from provenance approval and human acceptance:

```text
================================================================================
GOVERNANCE STATE LEDGER (TS-018 / Gate G5)
================================================================================
1. FILE_PRESENT:              True   (Candidate BTS ZIP physically verified)
2. SCHEMA_VALID:              True   (108 uppercase TranStats fields validated)
3. COMPANION_METADATA_VALID:  False  (External acquisition receipt pending human attestation)
4. CANDIDATE_CHECKSUM_MATCHED:True   (SHA-256 342de99f... matched)
5. SOURCE_PROVENANCE_VERIFIED:False  (Requires Project Lead External Authentication)
6. NUMERICAL_PARITY_VERIFIED: True   (10,500/10,500 exact comparisons verified across two sources)
7. HUMAN_ACCEPTED:            False  (EXCLUSIVE AUTHORITY: Project Lead)
================================================================================
```

---

## 3. Comparison Mode & Limitation Disclosure

- **Comparison Label:** `2019_raw_source_vs_BTS_candidate` (Option B protocol).
- **Curated Parquet State:** `PARQUET_PARITY_NOT_TESTED`. Physical curated Parquet for 2019 is not present in staging. This comparison confirms numerical unit consistency between the project raw dataset and official BTS Part 234 definitions.
- **Physical Parquet Option (Option A):** Physical 2016 Parquet (50 files, SNAPPY compressed, fingerprint `b5805fcae8db...`) is present in staging. If the Project Lead or Auditor requires curated Parquet output parity rather than raw input parity, official BTS January 2016 data should be acquired under Option A.

---

## 4. Unchanged Project Baselines

The following governance statuses remain active and are **not altered**:
- **Gate G2, Gate G3, Gate G4:** `PASS`
- **T-010:** `PASS / COMPLETED (CONTROLLED)`
- **T-011 Technical Implementation:** `PASS / SIGNED_OFF (CONTROLLED)`
- **T-011 Full Contract Closeout:** `PENDING_TS018`
- **TS-018:** `OPEN` (Candidate verified, awaiting human signoff)
- **G2-EXC-001:** `ACTIVE` (Blocks Gate G6 entry)
- **Gate G5:** `IN_PROGRESS`
- **Gate G6:** `NOT_STARTED / BLOCKED`
- **OR-05 (March 2024 Missingness):** `OPEN_QUALITY_DEFECT`
- **OR-08 (Source Identity):** `IDENTITY_UNVERIFIED`
- **Weather FP-DEC-017:** `CONDITIONAL_NO_GO`

---

## 5. Summary of Candidate Closure Artifacts

| Deliverable Path | Artifact Type | Bytes | SHA-256 Checksum |
|---|---|---|---|
| `docs/05-evidence/TS018_201901_EVIDENCE_CORRECTION_ERRATA.md` | `AUDIT_REPORT` | 6,554 | `85e82f50d03dd5d6ec1ca495f50ba1e84ca3b57351658b73ce96f12fe0a09e1e` |
| `docs/05-evidence/TS018_201901_ACTUAL_STRATUM_AND_KEY_AUDIT.md` | `AUDIT_REPORT` | 6,858 | `a1f0a1c1d81de8fa5c56c24b611e3895e691efdf307b22fcefc88a101b9a957a` |
| `docs/05-evidence/TS018_201901_MATCHED_SAMPLE_WITNESS.csv` | `RECEIPT_RECORD` | 294,436 | `942c476994c414378a541d5c84fcbdad35c6aeace1c98891044a085d55c3a9a1` |
| `docs/05-evidence/TS018_201901_INDEPENDENT_REPLAY_PROTOCOL.md` | `AUDIT_REPORT` | 6,664 | `3c09b8543f055a4eecf130b4ec7cbaef186c67d163ae37d1d4d3ce4c8d451eb8` |
| `docs/05-evidence/TS018_201901_CORRECTED_CANDIDATE_READINESS.md` | `AUDIT_REPORT` | — | *(This document)* |
| `docs/05-evidence/TS018_201901_RAW_CLOSURE_LOG.txt` | `EXECUTION_LOG` | — | *(Generated upon suite completion)* |
| `tools/qa/verify_ts018_two_source_sample_witness.py` | `QA_VERIFIER_TOOL` | 7,651 | `3f03b5df520ae1e7bb2830f5ec811ee361bcfaea373972235941c96765da74e4` |
| `tools/qa/TS018_201901_INDEPENDENT_EVIDENCE_CHECK_20261020.py` | `QA_VERIFIER_TOOL` | 2,948 | `7c7cf5cefd62bc5a8f4c2eef00c7e2f5c786a512e09ff7b63fbb974c0a527fae` |
| `docs/05-evidence/TS018_201901_INDEPENDENT_AUDIT_20261020.md` | `AUDIT_REPORT` | 6,674 | `94a97ee89b91bdf1d5cf65c401eeeb98f86ba93bc8ee242a77e804f3db6a2a07` |
| `docs/05-evidence/TS018_201901_INDEPENDENT_EVIDENCE_RESULT_20261020.json` | `AUDIT_REPORT` | 660 | `01217e29bb12852233f57ce79c4a8cf68aa5c5555d4ee7132a9cbf446b5a32ec` |
| `docs/05-evidence/TS018_201901_TARGETED_EVIDENCE_CLOSURE_PROMPT_20261020.md` | `GOVERNANCE_PACKAGE` | 5,962 | `a90c50d757d5982e5b88c42247f12e87369324d5ba7b2e88a38148b59d997233` |

---

## 6. Decision Request to Project Lead

With the technical evidence corrected and independently verifiable:
1. **Decision on Option A vs Option B:**
   - **Option B (Recommended for proportional unit verification):** Project Lead authorizes the 2019 raw source vs BTS comparison (10,500/10,500 exact) as fulfilling the numeric unit verification of TS-018, with the formal caveat `PARQUET_PARITY_NOT_TESTED`.
   - **Option A:** Project Lead directs acquisition of official BTS January 2016 reference data to test against existing physical 2016 staging Parquet.
2. **External Provenance Attestation:** Project Lead provides external download receipt/attestation to transition `SOURCE_PROVENANCE_VERIFIED` to `True`.
3. **Formal TS-018 Signoff:** Only upon Project Lead's explicit approval may TS-018 transition from `OPEN` to `PASS`. Gate G5 remains `IN_PROGRESS`.
