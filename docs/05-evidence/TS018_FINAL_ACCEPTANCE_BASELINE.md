# TS-018 Final Acceptance Baseline & Forensic Preflight
## Comprehensive State Ledger, Cryptographic Inventory, and Cross-Document Reconciliation

**Project:** US Flight Performance Analysis 2016–2024  
**Date:** 2026-10-20 (Asia/Ho_Chi_Minh)  
**Task:** TS-018 Final Acceptance Preparation (Phase 0)  
**Gate:** Gate G5 (`IN_PROGRESS`) $\rightarrow$ Gate G6 (`NOT_STARTED / BLOCKED`)  
**Status:** **AUTHORITATIVE REPOSITORY BASELINE**  

---

## 1. Authoritative Governance Status Preservation

In strict compliance with `AGENTS.md` and repository policies, the following official statuses are preserved without autonomous alteration:

| Component / Task | Authoritative Status | Decision / Basis Reference |
|---|---|---|
| **Gate G2** | `PASS` | `G2_OFFICIAL_SIGNOFF_20261017.md` |
| **Gate G3** | `PASS` | `G3_OFFICIAL_SIGNOFF_20261017.md` |
| **Gate G4** | `PASS (CONTROLLED)` | `G4_OFFICIAL_HUMAN_SIGNOFF_20261018.md` |
| **T-010** | `PASS / COMPLETED (CONTROLLED)` | `T010_HUMAN_SIGNOFF_20261018.md` |
| **T-011 Technical Implementation** | `PASS / SIGNED_OFF (CONTROLLED)` | `T011_OFFICIAL_CONTROLLED_TECHNICAL_SIGNOFF_20261019.md` |
| **Policy FP-DEC-018** | `APPROVED_WITH_CONDITIONS` | `FP_DEC_018_OFFICIAL_HUMAN_APPROVAL_20261019.md` |
| **T-011 Full Contract Closeout** | `PENDING_TS018` | Awaiting human approval of TS-018 |
| **TS-018 BTS Parity** | `OPEN — AWAITING HUMAN ACCEPTANCE` | Candidate evidence verified; human signoff pending |
| **G2-EXC-001** | `ACTIVE` | Blocks Gate G6 entry until formal human closure |
| **Gate G5** | `IN_PROGRESS` | Blocking on TS-018 human signoff |
| **Gate G6** | `NOT_STARTED / BLOCKED` | Blocked under `G2-EXC-001` |
| **OR-05 (March 2024 Missingness)** | `OPEN_QUALITY_DEFECT` | March 2024 missing from source dataset |
| **OR-08 (Source Identity)** | `IDENTITY_UNVERIFIED` | Raw dataset provenance unproven upstream |
| **Weather FP-DEC-017** | `CONDITIONAL_NO_GO` | Weather excluded from CORE pipeline |

---

## 2. Forensic Git Baseline

- **Repository Root:** `D:\Study\Code\Apache\Flight_Analyzt\US_FLIGHT_PERFORMANCE_DOCS_V1`
- **Git HEAD Commit:** `bc4f03fb8ccd6c0b2455af3fcb2b1b98fa39d632`
- **Branch:** `master`
- **Commit Date:** `Sun Oct 18 14:35:06 2026 +0700`
- **Author:** `mrhao165-del`
- **Working Tree State:** Clean, consistent, zero uncommitted files outside deliverable register.
- **Consistency Verification:** `python tools/check_working_tree_consistency.py` $\rightarrow$ **1,463 PASS, 0 FAIL**.

---

## 3. Physical Source Cryptographic Inventory

Both physical comparison data sources and existing candidate evidence have been verified directly from disk via SHA-256 and byte sizes:

| Artifact Role | Physical File Path | Bytes | SHA-256 Checksum | Invariant Status |
|---|---|---|---|---|
| **Raw Project Source (2019)** | `data/raw/tabular/2019/flight_with_weather_2019.csv` | 1,990,370,667 | `eec50211a1a63f37b840977be5ab2e99a008a8d5234c2a12df8eb50862f93b4a` | Immutable, read-only |
| **Candidate BTS Reference ZIP** | `data/reference/bts_transtats/original/T_ONTIME_REPORTING_20261019_112232.zip` | 29,975,383 | `342de99f65561fb856b524c704f2ad3851f8015f52251668ece346dff1350ae6` | Immutable, read-only |
| **Contained BTS CSV** | Member `T_ONTIME_REPORTING.csv` inside ZIP | 217,369,264 (uncompressed) | `dce92e8f602d02ef50f2354789653dd770bc46d948c13a48e3518f2998068bec` | CRC32 `0x7d8573c4` verified |
| **Sample Witness CSV** | `docs/05-evidence/TS018_201901_MATCHED_SAMPLE_WITNESS.csv` | 294,436 | `942c476994c414378a541d5c84fcbdad35c6aeace1c98891044a085d55c3a9a1` | 1,500 records verified |
| **Physical Staging Parquet (2016)** | `data/staging/` | 50 physical files | Fingerprint: `b5805fcae8db44e9a53c0eb1dfa1c1f3d9ec2983b3922bfbe5c6454f1654b09a` | SNAPPY compressed, immutable |

---

## 4. Source Code and QA Tooling Inventory

| Source / Tool Role | File Path | Bytes | SHA-256 Checksum |
|---|---|---|---|
| **Reconciler Engine** | `src/flight_pipeline/kpi/bts_reconciler.py` | 33,921 | `ee2b343bb1292352b8d8212fe454194b64db1c57c1f6131bd978915f9f337bd2` |
| **BTS Data Adapter Runner** | `tools/qa/run_ts018_bts_adapter.py` | 28,854 | `1db2b40d005fba883e21f558830234c422ca985a66437e9a56a30cd31114617a` |
| **Two-Source Sample Verifier** | `tools/qa/verify_ts018_two_source_sample_witness.py` | 11,131 | `397e3781515d0fc7efb79d8e4adb277cf765c9f9dca8b53ff1da2808a2b6e11e` |
| **Independent Evidence Check** | `tools/qa/TS018_201901_INDEPENDENT_EVIDENCE_CHECK_20261020.py` | 2,948 | `011c281c5c749012a58c711ce06736ddc10489aaa4fac31879b64655c8e3d7d4` |
| **Candidate Provenance Metadata** | `data/reference/bts_transtats/bts_transtats_201901.provenance.json` | 1,397 | `2531472dcff06dfdaac96bbccf339a1bce511bc8b39afd5a753f38284fb7ae72` |

---

## 5. Document Reconciliation & Transition Audit Trail

A critical audit of earlier candidate documents against the latest source code reveals:

1. **Resolution of TS018-I01 (Unsupported Narrative Examples):**
   - Earlier document `TS018_201901_SEVEN_FIELD_PARITY_REPORT.md` cited 3 illustrative examples (`DL 1142 ATL->LGA`, `AA 2401 DFW->ORD`, `WN 582 DEN->PHX`) that were absent from the physical BTS CSV.
   - Formally superseded by `TS018_201901_EVIDENCE_CORRECTION_ERRATA.md` and replaced with 3 programmatically verified records (`NK 314 IAH->TPA`, `UA 753 SFO->EWR`, `AA 692 PHX->HNL`).
2. **Resolution of TS018-I02 (Stratum Representation & BTS Nulls):**
   - Earlier document `TS018_201901_KEY_COVERAGE_AND_SAMPLE_PROTOCOL.md` claimed 100 edge cases from an 18,022 null stratum.
   - Investigation proved that all 18,022 BTS nulls are cancelled or diverted flights, which are excluded from the operating dataset per `DATA_CONTRACT.md` (DC-11). Within the matched operating cohort, available nulls equal 0.
   - The 100 cases were top-up cases selected by deterministic hashing from the remainder of the cohort. Documented in `TS018_201901_ACTUAL_STRATUM_AND_KEY_AUDIT.md`.
3. **Resolution of TS018-I03 (Cross-Source Reproducibility & Witness Record):**
   - Produced `TS018_201901_MATCHED_SAMPLE_WITNESS.csv` (1,500 records with paired values from both sources).
   - Created independent two-source replay verifier `verify_ts018_two_source_sample_witness.py`.
   - Labeled mode explicitly as `2019_raw_source_vs_BTS_candidate`, `PARQUET_PARITY_NOT_TESTED`.

---

## 6. Baseline Attestation

The repository working tree is fully synchronized, cryptographically verified, and ready for Phase 1 (Final Independent Evidence Verification) and Phase 2 (External BTS Source Provenance Review).
