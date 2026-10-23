# TS-018 BTS External Provenance Attestation (Draft)
## Formal Chain-of-Custody Verification & Operator Download Receipt Attestation

**Project:** US Flight Performance Analysis 2016–2024  
**Date:** 2026-10-20 (Asia/Ho_Chi_Minh)  
**Parent Task:** Task T-011 / TS-018  
**Parent Gate:** Gate G5 (`IN_PROGRESS`)  
**Status:** **PENDING HUMAN ATTESTATION (DRAFT)**  

---

## 1. Principle of External Provenance Governance

Under `AGENTS.md` and repository evidence governance:
1. **No Autonomous Self-Certification:** An AI Agent has no external network presence, physical agency, or institutional identity. An Agent **cannot self-certify** that an archive was acquired from an official government server.
2. **Hash vs Provenance Distinction:** The local SHA-256 digest (`342de99f65561fb856b524c704f2ad3851f8015f52251668ece346dff1350ae6`) proves the immutable integrity of the file on local disk; it **does not by itself prove** institutional origin from the US Bureau of Transportation Statistics.
3. **Requirement for External Attestation:** Full closure of TS-018 requires human operator attestation or documentary receipt certifying the acquisition of the candidate archive.

---

## 2. Current State of Candidate BTS Metadata

The companion metadata file at [`data/reference/bts_transtats/bts_transtats_201901.provenance.json`](../../data/reference/bts_transtats/bts_transtats_201901.provenance.json) was audited and records the following factual parameters:

| Metadata Field | Recorded Value | Governance Status |
|---|---|---|
| **Source Agency** | US Bureau of Transportation Statistics (BTS) | Declared |
| **Table Identifier** | Reporting Carrier On-Time Performance (1987-present) | Declared |
| **Source Period** | January 2019 (`2019-01`) | Verified against data |
| **Source Download URL** | `https://www.transtats.bts.gov/DL_SelectFields.aspx?QO_fu146_anzr=b0-gvzr&gnoyr_VQ=FGJ` | Declared |
| **Archive Filename** | `T_ONTIME_REPORTING_20261019_112232.zip` | Physically verified |
| **Archive Size (Bytes)** | `29,975,383` | Physically verified |
| **Archive SHA-256** | `342de99f65561fb856b524c704f2ad3851f8015f52251668ece346dff1350ae6` | Physically verified |
| **Contained CSV Member** | `T_ONTIME_REPORTING.csv` (217,369,264 bytes uncompressed) | Physically verified |
| **Contained CSV SHA-256** | `dce92e8f602d02ef50f2354789653dd770bc46d948c13a48e3518f2998068bec` | Physically verified |
| **Acquisition Date** | `2026-10-19` | Declared |
| **Acquired By** | `NOT_PROVIDED` | **PENDING_HUMAN_ATTESTATION** |
| **Download Receipt / Proof**| `NOT_PROVIDED` | **PENDING_HUMAN_ATTESTATION** |
| **Operator Identity** | `NOT_PROVIDED` | **PENDING_HUMAN_ATTESTATION** |
| **Project Lead Status** | `PENDING_APPROVAL` | **PENDING_HUMAN_REVIEW** |

---

## 3. Human Operator Attestation Form (To be Completed by Project Lead)

To transition `SOURCE_PROVENANCE_VERIFIED` from `False` to `True` in `BtsTranStatsReconciler`, the Project Lead or acquiring operator must complete the attestation below:

```text
================================================================================
BTS TRANSTATS EXTERNAL ACQUISITION ATTESTATION
================================================================================

I hereby certify that the physical archive:
  Filename:   T_ONTIME_REPORTING_20261019_112232.zip
  SHA-256:    342de99f65561fb856b524c704f2ad3851f8015f52251668ece346dff1350ae6
  Byte Size:  29,975,383 bytes

was acquired directly from the official portal of the United States Bureau of
Transportation Statistics (TranStats, transtats.bts.gov) under the following terms:

1. Acquisition Date & Time:   _________________________________________________
2. Operator / Lead Name:      _________________________________________________
3. Acquisition Mechanism:     [ ] Direct Web Portal (HTTPS Download)
                              [ ] Automated API Script
                              [ ] Other: ______________________________________
4. Table & Year Selected:     Reporting Carrier On-Time Performance (Jan 2019)
5. Fields Selected:           All Part 234 default fields (108 uppercase columns)
6. Supporting Evidence Ref:   [ ] Browser Download History / Log
                              [ ] Transaction Receipt / Screenshot
                              [ ] Local Terminal curl/wget command output
                              [ ] Direct Human Custody Attestation

Attesting Officer Signature:  _________________________________________________
Date of Attestation:          _________________________________________________
================================================================================
```

---

## 4. Current Governance State

Pending execution of the attestation above by the human Project Lead:
- `SOURCE_PROVENANCE_VERIFIED = False`
- `HUMAN_ACCEPTED = False`
- `TS-018 = OPEN (Awaiting Human Attestation & Signoff)`
