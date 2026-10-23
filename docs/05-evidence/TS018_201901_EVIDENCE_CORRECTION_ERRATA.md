# TS-018 January 2019 — Evidence Correction Errata
## Formal Superseding Errata for Unsupported Record Examples & Stratum Representation

**Project:** US Flight Performance Analysis 2016–2024  
**Date:** 2026-10-20 (Asia/Ho_Chi_Minh)  
**Parent Task:** Task T-011 / TS-018  
**Parent Gate:** Gate G5 (`IN_PROGRESS`)  
**Status:** **AUTHORITATIVE ERRATA RECORD**  
**Auditor Reference:** `TS018_201901_INDEPENDENT_AUDIT_20261020.md`  

---

## 1. Executive Summary & Policy Invariant

In accordance with `AGENTS.md` and repository evidence governance policies:
1. **Non-Destructive Errata:** Earlier evidence documents (`TS018_201901_SEVEN_FIELD_PARITY_REPORT.md` and `TS018_201901_KEY_COVERAGE_AND_SAMPLE_PROTOCOL.md`) are **not deleted or rewritten in-place**.
2. **Definitive Supersession:** This document explicitly identifies, explains the root causes of, and formally **supersedes** two defects identified during the independent review:
   - **Finding TS018-I01 (HIGH):** Unsupported illustrative flight examples in the seven-field parity report.
   - **Finding TS018-I02 (MEDIUM/HIGH):** Inaccurate stratum representation and misattributed null counts in the sampling protocol.
3. **Machine-Readable Witness:** Full cross-source reproducibility is established via [`TS018_201901_MATCHED_SAMPLE_WITNESS.csv`](TS018_201901_MATCHED_SAMPLE_WITNESS.csv) (1,500 rows, SHA-256 `942c476994c414378a541d5c84fcbdad35c6aeace1c98891044a085d55c3a9a1`), independently replayed by `tools/qa/verify_ts018_two_source_sample_witness.py` (10,500 / 10,500 exact matches).

---

## 2. Supersession of Finding TS018-I01: Narrative Record Examples

### 2.1 Obsolete / Defective Claims
Section 4 of `docs/05-evidence/TS018_201901_SEVEN_FIELD_PARITY_REPORT.md` cited three flights as real comparison examples:
- Record 1: `2019-01-01` | `DL` | `1142` | `ATL` $\rightarrow$ `LGA`
- Record 2: `2019-01-12` | `AA` | `2401` | `DFW` $\rightarrow$ `ORD`
- Record 3: `2019-01-20` | `WN` | `582` | `DEN` $\rightarrow$ `PHX`

### 2.2 Independent Reproduction & Root Cause
- **Reproduction:** An independent scan using `TS018_201901_INDEPENDENT_EVIDENCE_CHECK_20261020.py` against the authentic physical BTS ZIP (`T_ONTIME_REPORTING_20261019_112232.zip`, SHA-256 `342de99f65561fb856b524c704f2ad3851f8015f52251668ece346dff1350ae6`) yielded `false` for all three keys.
- **Root Cause:** The earlier author drafted these three records as narrative template examples without automated verification against the physical BTS CSV export. While 1,500 flights were algorithmically sampled, the narrative text cited non-existent keys.

### 2.3 Superseding Programmatically Verified Examples
The three obsolete records are hereby **fully superseded and replaced** with the following programmatically extracted records, verified in **both** physical sources (`flight_with_weather_2019.csv` and `T_ONTIME_REPORTING.csv` inside ZIP):

#### Authentic Record 1 — Early Arrival (Negative Delay Stratum)
- **Composite Key:** `2019-01-10` | `NK` | `314` | `IAH` $\rightarrow$ `TPA`
- **Stratum:** `NEGATIVE_DELAY`
- **Selection Score:** `15ebfd7d7eeff5be4cead2ec8574c93f0b2f3d5386f874836696ef2c6e61f93f`
- **Numerical Parity (Raw Dataset vs BTS Candidate):**
  - `ARR_DELAY`: Raw Dataset = `-6.0`, BTS = `-6.0` $\rightarrow$ **EXACT MATCH**
  - `DEP_DELAY`: Raw Dataset = `-4.0`, BTS = `-4.0` $\rightarrow$ **EXACT MATCH**
  - `TAXI_OUT`: Raw Dataset = `13.0`, BTS = `13.0` $\rightarrow$ **EXACT MATCH**
  - `TAXI_IN`: Raw Dataset = `8.0`, BTS = `8.0` $\rightarrow$ **EXACT MATCH**
  - `AIR_TIME`: Raw Dataset = `98.0`, BTS = `98.0` $\rightarrow$ **EXACT MATCH**
  - `ACTUAL_ELAPSED_TIME`: Raw Dataset = `119.0`, BTS = `119.0` $\rightarrow$ **EXACT MATCH**
  - `CRS_ELAPSED_TIME`: Raw Dataset = `121.0`, BTS = `121.0` $\rightarrow$ **EXACT MATCH**

#### Authentic Record 2 — Exact On-Time Arrival (Zero Delay Stratum)
- **Composite Key:** `2019-01-31` | `UA` | `753` | `SFO` $\rightarrow$ `EWR`
- **Stratum:** `ZERO_DELAY`
- **Selection Score:** `0cf6df084473857bb643193e16440db9fe71fa6e0a9b83b3e648c6b54134812a`
- **Numerical Parity (Raw Dataset vs BTS Candidate):**
  - `ARR_DELAY`: Raw Dataset = `0.0`, BTS = `0.0` $\rightarrow$ **EXACT MATCH**
  - `DEP_DELAY`: Raw Dataset = `0.0`, BTS = `0.0` $\rightarrow$ **EXACT MATCH**
  - `TAXI_OUT`: Raw Dataset = `24.0`, BTS = `24.0` $\rightarrow$ **EXACT MATCH**
  - `TAXI_IN`: Raw Dataset = `10.0`, BTS = `10.0` $\rightarrow$ **EXACT MATCH**
  - `AIR_TIME`: Raw Dataset = `295.0`, BTS = `295.0` $\rightarrow$ **EXACT MATCH**
  - `ACTUAL_ELAPSED_TIME`: Raw Dataset = `329.0`, BTS = `329.0` $\rightarrow$ **EXACT MATCH**
  - `CRS_ELAPSED_TIME`: Raw Dataset = `329.0`, BTS = `329.0` $\rightarrow$ **EXACT MATCH**

#### Authentic Record 3 — Substantial Delay (Positive Delay Stratum)
- **Composite Key:** `2019-01-21` | `AA` | `692` | `PHX` $\rightarrow$ `HNL`
- **Stratum:** `POSITIVE_DELAY`
- **Selection Score:** `763ef9081ae2b4c8ad0678eb8c6c59600e1cfeb5b7965aa30164bc9ba3e945c7`
- **Numerical Parity (Raw Dataset vs BTS Candidate):**
  - `ARR_DELAY`: Raw Dataset = `+1186.0`, BTS = `+1186.0` $\rightarrow$ **EXACT MATCH**
  - `DEP_DELAY`: Raw Dataset = `+1191.0`, BTS = `+1191.0` $\rightarrow$ **EXACT MATCH**
  - `TAXI_OUT`: Raw Dataset = `28.0`, BTS = `28.0` $\rightarrow$ **EXACT MATCH**
  - `TAXI_IN`: Raw Dataset = `17.0`, BTS = `17.0` $\rightarrow$ **EXACT MATCH**
  - `AIR_TIME`: Raw Dataset = `364.0`, BTS = `364.0` $\rightarrow$ **EXACT MATCH**
  - `ACTUAL_ELAPSED_TIME`: Raw Dataset = `409.0`, BTS = `409.0` $\rightarrow$ **EXACT MATCH**
  - `CRS_ELAPSED_TIME`: Raw Dataset = `414.0`, BTS = `414.0` $\rightarrow$ **EXACT MATCH**

---

## 3. Supersession of Finding TS018-I02: Sampling Strata & Null Accounting

### 3.1 Obsolete / Defective Claims
Section 3.B of `docs/05-evidence/TS018_201901_KEY_COVERAGE_AND_SAMPLE_PROTOCOL.md` reported:
- Negative delay: 338,421 available $\rightarrow$ 500 selected.
- Zero delay: 24,115 available $\rightarrow$ 200 selected.
- Positive delay: 178,578 available $\rightarrow$ 700 selected.
- Edge / Boundary Cases: "18,022 available null stratum" $\rightarrow$ 100 selected.

### 3.2 Independent Reproduction & Root Cause
- **Reproduction:** An independent scan confirmed that in the authentic BTS export, there are indeed 18,022 flights with missing `ARR_DELAY`. However, **all 18,022** are cancelled (`CANCELLED == 1.0`: 16,726) or diverted (`DIVERTED == 1.0`: 1,296). Active operating flights have **zero** missing `ARR_DELAY` values.
- In the project dataset (`flight_with_weather_2019.csv`), cancelled and diverted flights are excluded upstream per `DATA_CONTRACT.md` (DC-11). Therefore, within the 559,136 matched operating cohort, **zero records have null `ARR_DELAY`**!
- **Root Cause:** The earlier author mistakenly copied the BTS-side 18,022 null count into the matched cohort table. When the runner attempted to select 100 null-delay records, it encountered 0 available records and deterministically filled the 100-record shortfall from the remainder of matched flights. The report falsely labeled these 100 top-up flights as "Edge / Boundary Cases from 18,022 stratum".

### 3.3 Superseding Actual Strata & Selection Accounting
The sampling table is hereby **fully superseded and replaced** with the following audited figures:

| Stratum Name | Selection Rule | Available in Matched Cohort | Target Quota | Selected in Sample | Status / Note |
|---|---|---|---|---|---|
| `NEGATIVE_DELAY` | `ARR_DELAY < 0.0` | 358,420 | 500 | 500 | Fully fulfilled |
| `ZERO_DELAY` | `ARR_DELAY == 0.0` | 10,284 | 200 | 200 | Fully fulfilled |
| `POSITIVE_DELAY` | `ARR_DELAY > 0.0` | 190,432 | 700 | 700 | Fully fulfilled |
| `NULL_DELAY` | `ARR_DELAY is None` | **0** | 100 | **0** | Zero available in operating cohort |
| `REMAINDER_TOPUP` | Deterministic hash over remaining cohort | 557,736 | 0 | **100** | Explicit shortfall top-up |
| **Total Cohort** | — | **559,136** | **1,500** | **1,500** | Exactly 1,500 records |

### 3.4 Governance of Unmatched Active Flights (6,827 Records)
In the BTS CSV, 565,963 active non-diverted operating flights exist. The project January 2019 raw dataset contains 559,136 flights.
The difference of **6,827 flights** (1.21% of active BTS flights) is factually recorded as:
> *Active operating flights present in official BTS Part 234 reporting but absent from the Kaggle compiled raw dataset. Because the Kaggle compilation scripts are not part of this repository, no unproven causal attribution (such as weather-join drops) is asserted.*

---

## 4. Summary of Superseding Artifacts

| Defect Finding | Obsolete Section | Superseding Document / Artifact | Audit Hash / Reference |
|---|---|---|---|
| **TS018-I01** | `TS018_201901_SEVEN_FIELD_PARITY_REPORT.md` §4 | `TS018_201901_EVIDENCE_CORRECTION_ERRATA.md` §2 & `TS018_201901_MATCHED_SAMPLE_WITNESS.csv` | SHA-256 `942c476994c414378a541d5c84fcbdad35c6aeace1c98891044a085d55c3a9a1` |
| **TS018-I02** | `TS018_201901_KEY_COVERAGE_AND_SAMPLE_PROTOCOL.md` §3.B | `TS018_201901_EVIDENCE_CORRECTION_ERRATA.md` §3 & `TS018_201901_ACTUAL_STRATUM_AND_KEY_AUDIT.md` | Audited cohort counts (358,420 / 10,284 / 190,432 / 0 / 100) |
| **TS018-I03** | Lack of machine-readable sample witness | `TS018_201901_MATCHED_SAMPLE_WITNESS.csv` & `tools/qa/verify_ts018_two_source_sample_witness.py` | 1,500 rows, 10,500/10,500 verified across both physical sources |
