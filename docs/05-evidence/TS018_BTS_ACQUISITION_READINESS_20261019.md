# TS018 BTS ACQUISITION READINESS & SOURCE SPECIFICATION
## Readiness Assessment, Field Mapping, Intake Checklist & Provenance Guard for TS-018

**Project:** US Flight Performance Analysis 2016–2024  
**Date:** 2026-10-19 (Asia/Ho_Chi_Minh)  
**Parent Gate:** Gate G5 (`IN_PROGRESS`)  
**Parent Task:** Task T-011  
**Test Spec Reference:** `TS-018` (BTS TranStats Sample Parity & Record-Level Unit Verification)  
**Governing Exception:** `G2-EXC-001` (`ACTIVE`)  
**Overall TS-018 Status:** `OPEN (BLOCKING_G5_EXIT)` / `PENDING_EXTERNAL_SOURCE_DELIVERY`  
**Hard Stop:** `Gate G5 = IN_PROGRESS`; `Gate G6 = NOT_STARTED / BLOCKED`

---

## 1. Executive Summary & Authoritative Gating Status

Under approved exception **`G2-EXC-001`** and design decisions **`FP-DEC-012`**, direct BTS TranStats record-level verification for the 7 CORE numeric measures was deferred from Gate G2 to **Gate G5 (`TS-018`)**.

Following the human Project Lead's official controlled signoff of Task T-011's technical implementation on 2026-10-19 ([`T011_OFFICIAL_CONTROLLED_TECHNICAL_SIGNOFF_20261019.md`](T011_OFFICIAL_CONTROLLED_TECHNICAL_SIGNOFF_20261019.md)), Task T-011's status is disaggregated into:
1. `T-011 TECHNICAL_IMPLEMENTATION = PASS / SIGNED_OFF (CONTROLLED)`
2. `T-011 TS-018 EXTERNAL ACCEPTANCE CONDITION = OPEN (BLOCKING_G5_EXIT)`
3. `T-011 FULL_CONTRACT_CLOSEOUT = PENDING_TS018`

> [!CRITICAL]
> **No autonomous Agent can self-certify authentic BTS provenance.**
> A synthetic test harness exit code `0` or a locally authored JSON companion stating `APPROVED_BY_PROJECT_LEAD` does NOT constitute authentic external BTS source verification.
> **Status:** `PENDING_EXTERNAL_SOURCE_DELIVERY`. Gate G5 remains `IN_PROGRESS` and Gate G6 remains strictly `NOT_STARTED / BLOCKED`.

---

## 2. Official BTS Source Specification

The official, authentic data source required to satisfy TS-018 is:
- **Agency:** Bureau of Transportation Statistics (BTS), United States Department of Transportation (US DOT).
- **Portal:** TranStats Data Center.
- **Table Name:** **Reporting Carrier On-Time Performance (1987–present)**  
  *(CAUTION: Do NOT use "Marketing Carrier On-Time Performance (Beginning January 2018)", which has different carrier definitions and aggregation logic).*
- **Official Download URL:**  
  [`https://www.transtats.bts.gov/DL_SelectFields.aspx?QO_fu146_anzr=b0-gvzr&gnoyr_VQ=FGJ`](https://www.transtats.bts.gov/DL_SelectFields.aspx?QO_fu146_anzr=b0-gvzr&gnoyr_VQ=FGJ)
- **Official Data Field Dictionary:**  
  [`https://www.transtats.bts.gov/Fields.asp?gnoyr_VQ=FGJ`](https://www.transtats.bts.gov/Fields.asp?gnoyr_VQ=FGJ)
- **Official Table Profile:**  
  [`https://www.transtats.bts.gov/TableInfo.asp?QO_fu146_anzr=b0-gvzr&gnoyr_VQ=FGJ`](https://www.transtats.bts.gov/TableInfo.asp?QO_fu146_anzr=b0-gvzr&gnoyr_VQ=FGJ)

---

## 3. Seven Canonical CORE Measures: Official-to-Canonical Mapping

Every one of the 7 CORE numeric measures must be extracted from the official BTS download and compared record-for-record against the project's curated dataset:

| # | Canonical Dataset Column | Official BTS Column Name | Official US DOT / 14 CFR Part 234 Definition | Unit & Convention |
|---|---|---|---|---|
| 1 | `ARR_DELAY` | `ArrDelay` | Difference in minutes between scheduled and actual arrival time. Early arrivals show negative numbers. | Minutes (`float64`), signed |
| 2 | `DEP_DELAY` | `DepDelay` | Difference in minutes between scheduled and actual departure time. Early departures show negative numbers. | Minutes (`float64`), signed |
| 3 | `TAXI_OUT` | `TaxiOut` | Taxi Out time in minutes (wheels-off minus gate-out). | Minutes (`float64`), non-negative |
| 4 | `TAXI_IN` | `TaxiIn` | Taxi In time in minutes (gate-in minus wheels-on). | Minutes (`float64`), non-negative |
| 5 | `AIR_TIME` | `AirTime` | Airborne flight time in minutes (wheels-on minus wheels-off). | Minutes (`float64`), non-negative |
| 6 | `ACTUAL_ELAPSED_TIME` | `ActualElapsedTime` | Elapsed flight time in minutes (gate-to-gate total). | Minutes (`float64`), non-negative |
| 7 | `CRS_ELAPSED_TIME` | `CRSElapsedTime` | Computerized Reservations System scheduled elapsed time in minutes. | Minutes (`float64`), non-negative |

---

## 4. Composite Business Matching Keys

To match rows unambiguously between the official BTS export and the project dataset, the 5 composite keys are defined:

| Key # | Canonical Field | Official BTS Column | Matching Semantics & Transformation Requirements |
|---|---|---|---|
| 1 | `FL_DATE` | `FlightDate` (or `FL_DATE`) | ISO Date `YYYY-MM-DD`. BTS raw export typically uses `M/D/YYYY 12:00:00 AM` (e.g. `1/1/2019 12:00:00 AM`); parser must normalize to ISO format before key matching. |
| 2 | `OP_CARRIER` | `Reporting_Airline` (or `OP_CARRIER`) | 2-character IATA airline code (e.g., `AA`, `DL`, `UA`, `WN`, `YX`). String match. |
| 3 | `OP_CARRIER_FL_NUM` | `Flight_Number_Reporting_Airline` (or `OP_CARRIER_FL_NUM`) | Numerical flight number. Must preserve float-to-int normalization (e.g., `101.0` $\leftrightarrow$ `101`) and preserve flight number `0` / `0.0` under G3-COND-A. |
| 4 | `ORIGIN` | `Origin` (or `ORIGIN`) | 3-letter IATA origin airport code (e.g., `DFW`, `ATL`, `ORD`). Uppercase string. |
| 5 | `DEST` | `Dest` (or `DEST`) | 3-letter IATA destination airport code (e.g., `ORD`, `LGA`, `SFO`). Uppercase string. |

---

## 5. Candidate File Inventory on Local Disk

During the Phase S0 baseline audit, an external download archive was discovered on disk:
- **Location:** `data/reference/bts_transtats/original/T_ONTIME_REPORTING_20261019_112232.zip`
- **File Size:** 29,975,383 bytes
- **Streaming SHA-256:** `342de99f65561fb856b524c704f2ad3851f8015f52251668ece346dff1350ae6`
- **Contained File:** `T_ONTIME_REPORTING.csv` (217,369,264 bytes uncompressed, 109 columns, covering January 2019).
- **Candidate Downloads in User Folder:**
  - `C:\Users\Heikapu\Downloads\T_ONTIME_REPORTING_20261019_104600.zip` (4,692,909 bytes; contains 2026 data, out of project scope).
  - `C:\Users\Heikapu\Downloads\T_ONTIME_REPORTING_20261019_105733.zip` (29,692,560 bytes; contains 2026 data, out of project scope).

### Audit Verdict on Candidate File
While `T_ONTIME_REPORTING_20261019_112232.zip` covers January 2019 (within the 2016–2024 project scope), it currently has:
1. `source_provenance_verified = False`: No download transaction receipt, IP, operator attestation, or URL log exists in `docs/05-evidence/`.
2. `companion_metadata_valid = False`: No companion metadata (`.provenance.json`) has been generated or approved.
3. `human_accepted = False`: The human Project Lead has not reviewed or signed off on this candidate archive.

Therefore, this archive is classified as **`CANDIDATE_UNVERIFIED_PENDING_HUMAN_INTAKE`**.

---

## 6. Governed Evidence Intake Checklist for TS-018

Before TS-018 can be evaluated for formal human acceptance, the following 7 deliverables must be completed by an authorized operator:

- [ ] **Checklist Item 1 — Download Transaction Receipt (`TS018_BTS_SOURCE_ACQUISITION_RECORD.md`):**  
  Document the exact browser download session, table name, date filters, exact URL accessed, acquisition timestamp with timezone, operator identity, and original filename.
- [ ] **Checklist Item 2 — Hash & File Registry (`TS018_BTS_ORIGINAL_FILE_HASHES.json`):**  
  Compute streaming SHA-256 and byte sizes of both the original ZIP and extracted CSV. Store read-only in `data/reference/bts_transtats/`.
- [ ] **Checklist Item 3 — Sample Selection Protocol (`TS018_BTS_SAMPLE_SELECTION_PROTOCOL.md`):**  
  Define a bounded reference cohort (e.g., January 2016 or January 2019) present in both the local project dataset and the BTS export. Document sample size ($N \ge 1,000$), duplicate key handling, and coverage of signed negatives, zeros, and positive delays.
- [ ] **Checklist Item 4 — Provenance Companion Metadata (`bts_transtats_sample.provenance.json`):**  
  Create metadata conforming to `BtsProvenanceMetadata` in `src/flight_pipeline/kpi/bts_reconciler.py`. Maintain `project_lead_approval_status = "PENDING_APPROVAL"`.
- [ ] **Checklist Item 5 — Execution of Parity Runner:**  
  Run `python tools/qa/run_ts018_bts_parity.py` against the authentic sample. Capture full CLI stdout/stderr log in `docs/05-evidence/`.
- [ ] **Checklist Item 6 — Discrepancy & Parity Analysis (`TS018_BTS_CANDIDATE_PARITY_REPORT.md`):**  
  Independently verify 0 key mismatches, 0 duplicate collisions, and exact / rounding match rates across all 7 CORE measures.
- [ ] **Checklist Item 7 — Submission of Human Approval Request (`TS018_BTS_HUMAN_APPROVAL_REQUEST.md`):**  
  Submit the complete evidence package to the Project Lead. Only explicit human acceptance can transition TS-018 to `PASS`.

---

## 7. Intentional Trust-Boundary Safeguards in `BtsTranStatsReconciler`

The codebase contains deliberate architectural safeguards that enforce governance boundaries:
```python
# From src/flight_pipeline/kpi/bts_reconciler.py:
# Locally self-asserted companion metadata files CANNOT self-verify external provenance
source_provenance_verified = False  # Trust boundary: requires external human verification
human_accepted = False              # Exclusive authority: Project Lead
```
These flags prevent autonomous AI agents or local test scripts from manufacturing a `TS018_PASS_AUTHENTIC_PARITY_ESTABLISHED` verdict.

---

## 8. Summary of Active Gate Constraints

| Boundary | Status | Implication |
|---|---|---|
| **TS-018 Parity** | `OPEN (BLOCKING_G5_EXIT)` | Gate G5 cannot be closed |
| **G2-EXC-001** | `ACTIVE` | Numeric units remain provisional |
| **Gate G5** | `IN_PROGRESS` | Full pipeline execution prohibited |
| **Gate G6** | `NOT_STARTED / BLOCKED` | 9-year batch execution blocked |
