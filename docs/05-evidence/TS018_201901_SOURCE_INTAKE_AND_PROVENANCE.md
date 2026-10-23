# TS018 SOURCE INTAKE & PROVENANCE REPORT — BTS JANUARY 2019
## Candidate Source Verification, Forensic Hashes, and Trust Boundary Attestation

**Project:** US Flight Performance Analysis 2016–2024  
**Date:** 2026-10-20 (Asia/Ho_Chi_Minh)  
**Parent Gate:** Gate G5 (`IN_PROGRESS`)  
**Parent Task:** Task T-011  
**Test Spec:** `TS-018` (BTS TranStats Sample Parity & Record-Level Unit Verification)  
**Governing Policy:** `FP-DEC-012`, `FP-DEC-018`, `G2-EXC-001`  
**Candidate Intake Classification:** `CANDIDATE_UNVERIFIED_PENDING_HUMAN_AUTHENTICATION`  
**Overall Provenance Status:** `SOURCE_PROVENANCE_VERIFIED = False` | `HUMAN_ACCEPTED = False`

---

## 1. Executive Summary & Gating Status

Under approved exception **`G2-EXC-001`**, record-level unit verification against external official BTS TranStats data was deferred to Gate G5 (`TS-018`). This report documents the physical source intake, streaming forensic hash verification, and provenance attestation of the January 2019 reference archive supplied to the repository.

> [!CRITICAL]
> **Trust Boundary Invariant (R4-F01 / FP-DEC-018):**
> Presence of a candidate archive on disk, matching SHA-256 checksums, and algorithmic test execution DO NOT constitute authentic external BTS provenance.
> No autonomous AI Agent can self-certify external data provenance. Provenance authentication belongs exclusively to the human Project Lead.
> Current Gating Status: **Gate G5 remains `IN_PROGRESS`**; **Gate G6 remains `NOT_STARTED / BLOCKED`**.

---

## 2. Physical File & Cryptographic Forensics

The reference archive was verified in place at its designated path without modification or timestamp alteration:

| Forensic Attribute | Verified Value | Compliance / Attestation |
|---|---|---|
| **Relative Path** | `data/reference/bts_transtats/original/T_ONTIME_REPORTING_20261019_112232.zip` | Within strictly allowed reference subtree |
| **Physical File Size** | `29,975,383` bytes | Exact byte match with expected size |
| **ZIP Streaming SHA-256** | `342de99f65561fb856b524c704f2ad3851f8015f52251668ece346dff1350ae6` | 100% cryptographic match with pre-intake digest |
| **ZIP Header CRC-32** | `0x7d8573c4` | Valid ZIP container CRC |
| **Archive Integrity Test** | `zipfile.testzip() == None` | 0 corrupted bytes, 0 header defects |
| **Internal Member Name** | `T_ONTIME_REPORTING.csv` | Exactly 1 member file |
| **Uncompressed Size** | `217,369,264` bytes | Verified via streaming decompressor |
| **Compressed Size** | `29,975,241` bytes | Deflate compression ratio ~7.25x |
| **CSV Streaming SHA-256** | `dce92e8f602d02ef50f2354789653dd770bc46d948c13a48e3518f2998068bec` | Cryptographic signature of uncompressed CSV |

---

## 3. Streaming CSV Header & Metric Completeness

The uncompressed CSV member `T_ONTIME_REPORTING.csv` was inspected via a streaming text reader. The physical CSV header contains **108 columns** (all uppercase):

### A. Five Composite Matching Keys (All Present, Uppercase)
1. `FL_DATE` (Column index 5) — Raw format `M/D/YYYY 12:00:00 AM` (e.g. `1/1/2019 12:00:00 AM`)
2. `OP_CARRIER` (Column index 8) — 2-character IATA airline code (e.g. `WN`, `AA`, `DL`)
3. `OP_CARRIER_FL_NUM` (Column index 10) — Flight number (e.g. `3311`, `5109`)
4. `ORIGIN` (Column index 14) — 3-letter IATA origin airport code (e.g. `ATL`, `DFW`)
5. `DEST` (Column index 23) — 3-letter IATA destination airport code (e.g. `LNK`, `MYR`)

### B. Seven Required CORE Numeric Measures (All Present, Uppercase)
1. `ARR_DELAY` (Column index 41) — Signed arrival delay (minutes)
2. `DEP_DELAY` (Column index 31) — Signed departure delay (minutes)
3. `TAXI_OUT` (Column index 36) — Non-negative taxi-out time (minutes)
4. `TAXI_IN` (Column index 39) — Non-negative taxi-in time (minutes)
5. `AIR_TIME` (Column index 51) — Non-negative airborne time (minutes)
6. `ACTUAL_ELAPSED_TIME` (Column index 50) — Non-negative total gate-to-gate time (minutes)
7. `CRS_ELAPSED_TIME` (Column index 49) — Non-negative scheduled elapsed time (minutes)

### C. Operational Status Indicators
- `CANCELLED` (Column index 46): `16,726` cancelled flights (2.86%)
- `DIVERTED` (Column index 48): `1,296` diverted flights (0.22%)
- `CANCELLATION_CODE` (Column index 47): Reason codes (A=Carrier, B=Weather, C=NAS, D=Security)

---

## 4. Population & Temporal Accounting

A full-month linear streaming scan of all 583,985 records confirmed:
- **Total Physical Records:** `583,985` rows (excluding 1-line header).
- **Date Boundary:** Covers exactly 31 days from `2019-01-01` to `2019-01-31` (100% of January 2019).
- **Duplicate Composite Keys:** `0` duplicate collisions observed across the entire 583,985-row universe.
- **Active Reporting Airlines:** `17` distinct operating carriers. Top carriers:
  1. `WN` (Southwest Airlines): 111,312 flights
  2. `AA` (American Airlines): 77,017 flights
  3. `DL` (Delta Air Lines): 73,836 flights
  4. `OO` (SkyWest Airlines): 64,926 flights
  5. `UA` (United Airlines): 46,915 flights

---

## 5. Provenance Companion Metadata & Trust Separation

In accordance with `BtsProvenanceValidator` and `FP-DEC-018`:
- Candidate metadata file authored: [`data/reference/bts_transtats/bts_transtats_201901.provenance.json`](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/data/reference/bts_transtats/bts_transtats_201901.provenance.json)
- Provenance Attributes:
  - `source_agency`: `"US Bureau of Transportation Statistics"`
  - `table_identifier`: `"Reporting Carrier On-Time Performance (1987-present)"`
  - `source_period`: `"2019-01"`
  - `acquired_by`: `"NOT_PROVIDED"` (Honest disclosure: operator metadata not bundled with ZIP)
  - `download_transaction_receipt`: `"NOT_PROVIDED"`
  - `operator_identity`: `"NOT_PROVIDED"`
  - `project_lead_approval_status`: `"PENDING_APPROVAL"`
  - `approval_record_ref`: `"PENDING_HUMAN_REVIEW"`
  - `is_external_reference`: `True`

```text
========================================
SEPARATION OF GOVERNANCE STATES:
  1. FILE_PRESENT:              True
  2. SCHEMA_VALID:               True (108 uppercase columns verified)
  3. COMPANION_METADATA_VALID:   False (PENDING_APPROVAL)
  4. CANDIDATE_CHECKSUM_MATCHED: True (342de99f... matched)
  5. SOURCE_PROVENANCE_VERIFIED: False (Requires Project Lead External Authentication)
  6. NUMERICAL_PARITY_VERIFIED:  True
  7. HUMAN_ACCEPTED:             False (EXCLUSIVE: Project Lead)
========================================
```

**Conclusion:** The archive is forensically valid and structurally complete, but awaits independent human authentication of its external acquisition chain before TS-018 can be formally closed.
