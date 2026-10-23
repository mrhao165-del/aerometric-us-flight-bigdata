# TS-018 Option B Formal Decision Dossier (Draft)
## Proposed Human Acceptance Policy for Raw Source Numerical Unit Verification

**Project:** US Flight Performance Analysis 2016–2024  
**Date:** 2026-10-20 (Asia/Ho_Chi_Minh)  
**Parent Task:** Task T-011 / TS-018  
**Parent Gate:** Gate G5 (`IN_PROGRESS`)  
**Proposed Policy ID:** `FP-DEC-PROP-019` (Option B Protocol)  
**Authority:** **PROJECT LEAD EXCLUSIVE HUMAN SIGNOFF (DRAFT ONLY)**  

---

## 1. Context and Objective

Under Gate G5, requirement TS-018 mandates verifying that the seven CORE numerical measures in the project dataset conform to official Bureau of Transportation Statistics (BTS) Part 234 reporting definitions, particularly regarding units of measure (minutes vs seconds), signed delay preservation (negative delay for early arrival/departure), and elapsed time validity.

Because physical staging Parquet currently exists only for 2016 (50 files, SNAPPY compressed, fingerprint `b5805fcae8db...`), and physical ingestion of 2019 Parquet is prohibited under G5/G6 boundaries, an operational choice was proposed between:
- **Option A:** Acquire official BTS January 2016 data and compare against attested physical 2016 staging Parquet.
- **Option B (Proposed Candidate):** Compare the authentic January 2019 BTS export against the immutable January 2019 raw project dataset (`flight_with_weather_2019.csv`).

This document provides the formal proposal and risk boundaries for the Project Lead's decision regarding **Option B**.

---

## 2. Technical Evidence Base

The candidate Option B evaluation was executed under strict, verifiable protocols:
1. **Physical File Verification:**
   - Raw project source: `flight_with_weather_2019.csv` (1,990,370,667 bytes, SHA-256 `eec50211a1a63f37b840977be5ab2e99a008a8d5234c2a12df8eb50862f93b4a`).
   - BTS reference export: `T_ONTIME_REPORTING_20261019_112232.zip` (29,975,383 bytes, SHA-256 `342de99f65561fb856b524c704f2ad3851f8015f52251668ece346dff1350ae6`).
2. **Exhaustive Population Overlap:**
   - Total January 2019 raw project flights: `559,136` (0 duplicate keys).
   - Total January 2019 BTS flights: `583,985` (0 duplicate keys).
   - Matched composite keys: `559,136` (**100.0%** of project dataset matches valid BTS flights).
3. **Deterministic Sample Parity:**
   - $N = 1,500$ records stratified across negative, zero, positive delays, and remainder top-up.
   - Total record-level comparisons: $1,500 \times 7 = \mathbf{10,500}$ comparisons.
   - **Exact bitwise equality:** $\mathbf{10,500 / 10,500}$ (**100.0%**, diff = 0.0 minutes).
   - Zero tolerance matches required, zero mismatches, zero null disagreements.
4. **Machine-Readable Witness & Replay:**
   - Exported to [`TS018_201901_MATCHED_SAMPLE_WITNESS.csv`](TS018_201901_MATCHED_SAMPLE_WITNESS.csv) (SHA-256 `942c476994c414378a541d5c84fcbdad35c6aeace1c98891044a085d55c3a9a1`).
   - Independently replayed and confirmed by [`verify_ts018_two_source_sample_witness.py`](../../tools/qa/verify_ts018_two_source_sample_witness.py).

---

## 3. Scope of Acceptance under Option B

If approved by the Project Lead, Option B establishes the following technical conclusions:
1. **Unit of Measure Attestation:** All 7 CORE numerical measures in the project tabular dataset are expressed in **minutes**. No seconds-to-minutes scale distortion ($60\times$) or hours distortion exists.
2. **Signed Delay Invariant:** Arrival and departure delays strictly preserve signed negative values for early flights (e.g. `-6.0`, `-4.0`). No premature zero-clipping or absolute-value transformations occur.
3. **Elapsed Time Invariant:** `TAXI_OUT`, `TAXI_IN`, `AIR_TIME`, `ACTUAL_ELAPSED_TIME`, and `CRS_ELAPSED_TIME` strictly conform to Part 234 definitions.

---

## 4. Mandatory Explicit Limitations & Residual Risks

> [!WARNING]
> **Governed Limitations of Option B:**
> 1. **`PARQUET_PARITY_NOT_TESTED`:** Option B verifies raw tabular input parity, **not curated Parquet output parity**. Parquet schema conformance and Spark transformation correctness remain guaranteed separately by T-010 and T-011 unit/smoke tests, but physical 2019 Parquet files have not been generated or compared.
> 2. **No Upstream Provenance Proof (`OR-08`):** Record-level parity with BTS January 2019 proves that the project's 2019 data originates from BTS Part 234. However, it **does not prove** upstream chain-of-custody for all 9 years (2016–2024). Residual risk `OR-08` (`IDENTITY_UNVERIFIED`) remains active.
> 3. **Unmatched Operating Flights (6,827 Records):** In the BTS population, 6,827 active operating flights are absent from the Kaggle 2019 dataset. This population delta is documented factually without asserting unproven causal claims of weather-join filtering.
> 4. **Option A Availability:** If an independent auditor or external stakeholder requires verification directly on curated Parquet, Option A remains available as a non-breaking alternative.

---

## 5. Decision Request to Project Lead

Please review the evidence and select the authoritative project decision:

```text
[ ] CHOICE 1: APPROVE_WITH_CONDITIONS (Option B Accepted)
    Accept 2019 raw source vs BTS parity (10,500/10,500 exact) as satisfying TS-018 unit verification.
    Record PARQUET_PARITY_NOT_TESTED as an explicit technical limitation.
    Maintain OR-05 and OR-08 active.
    Permit transition of TS-018 to PASS upon external provenance attestation.

[ ] CHOICE 2: HOLD (Direct Option A Execution)
    Direct acquisition of official BTS January 2016 sample.
    Require comparison directly against 2016 staging Parquet before TS-018 signoff.

[ ] CHOICE 3: REJECT
    Reject Option B evidence. Specify required technical remediation.
```

---

## 6. Signoff Area (Project Lead Only)

- **Decision:** `________________________________________________`
- **Authorized Project Lead Name:** `________________________________`
- **Date:** `____________________`
- **Signature / Token:** `________________________________________`
