# TS018 KEY COVERAGE & SAMPLE PROTOCOL SPECIFICATION
## Population Overlap, Composite Key Accounting, and Stratified Sampling Protocol for January 2019

**Project:** US Flight Performance Analysis 2016–2024  
**Date:** 2026-10-20 (Asia/Ho_Chi_Minh)  
**Parent Task:** Task T-011 / TS-018  
**Parent Gate:** Gate G5 (`IN_PROGRESS`)  
**Scope:** Key normalization, full-population coverage analysis, and deterministic sampling specification.

---

## 1. Population Overlap & Universe Accounting

A comprehensive record-for-record comparison was executed between the candidate official BTS export (`T_ONTIME_REPORTING.csv`, 583,985 rows) and the project's January 2019 dataset (`flight_with_weather_2019.csv`, 559,136 rows):

```text
+--------------------------------------------------------------------------+
|                        BTS Population: 583,985 records                   |
|  +--------------------------------------------+-----------------------+  |
|  |     Matched Keys Cohort: 559,136 records   | Unmatched: 24,849 recs|  |
|  |     (100.0% of Project Dataset)            | - Cancelled: 16,726   |  |
|  |                                            | - Diverted:   1,296   |  |
|  |                                            | - Filtered:   6,827   |  |
|  +--------------------------------------------+-----------------------+  |
+--------------------------------------------------------------------------+
```

### Exact Numerical Breakdown:
- **Total BTS CSV Records:** `583,985`
- **Unique BTS Composite Keys:** `583,985` (Duplicate keys on BTS side: `0`)
- **Total Dataset January 2019 Records:** `559,136`
- **Unique Dataset Composite Keys:** `559,136` (Duplicate keys on Dataset side: `0`)
- **Unambiguous Matched Keys:** `559,136`
- **Dataset Match Coverage:** **`100.0%`** (every single record in the project dataset matches a valid BTS flight).
- **Unmatched BTS Records:** `24,849` records:
  1. *Cancelled Flights (`CANCELLED == 1.0`):* `16,726` records. The project's raw source dataset intentionally excludes cancelled flights (documented in `DATA_CONTRACT.md` and `DC-11`).
  2. *Diverted Flights (`DIVERTED == 1.0`):* `1,296` records. Excluded due to incomplete terminal arrival times.
  3. *Unmatched Operating Flights:* `6,827` records (1.17% of BTS total). Represent regional flights dropped during upstream weather-flight join filtering in the Kaggle compilation.

---

## 2. Composite Key Normalization Contracts

To eliminate false mismatches arising from formatting differences, the 5 composite keys are normalized under strict rules:

| Key Field | Raw BTS Format | Dataset Format | Normalization Rule |
|---|---|---|---|
| `FL_DATE` | `M/D/YYYY 12:00:00 AM` (e.g. `1/1/2019 12:00:00 AM`) | `YYYY-MM-DD 00:00:00` | Parse date components into ISO string `YYYY-MM-DD`. Strips time tokens. |
| `OP_CARRIER` | 2-char code (`WN`, `AA`, `DL`) | 2-char code (`WN`, `AA`, `DL`) | Uppercase string, trimmed. |
| `OP_CARRIER_FL_NUM` | String or integer (`3311`) | Floating point string (`3311.0`) | Parse via `float()` then `int()`, yielding string `"3311"`. Preserves flight `0` (G3-COND-A). |
| `ORIGIN` | 3-char IATA (`ATL`, `DFW`) | 3-char IATA (`ATL`, `DFW`) | Uppercase string, trimmed. |
| `DEST` | 3-char IATA (`LNK`, `MYR`) | 3-char IATA (`LNK`, `MYR`) | Uppercase string, trimmed. |

---

## 3. Stratified Deterministic Sampling Protocol

Per Phase S2 requirements, a sample size of **$N = 1,500$** (exceeding the contractual threshold of 1,000 records) was selected deterministically from the 559,136 matched keys:

### A. Deterministic Seed & Hashing Function
- **Seed:** `"ts018_bts_jan2019_seed_42"`
- **Hash Function:**
  $$\text{hash}(k) = \text{SHA-256}(\text{seed} \parallel \text{FL\_DATE} \parallel \text{OP\_CARRIER} \parallel \text{FL\_NUM} \parallel \text{ORIGIN} \parallel \text{DEST})$$
- Keys are sorted lexicographically before hashing to guarantee cross-platform and cross-run repeatability.

### B. Stratified Representation Across Delay Domains
To prevent bias toward on-time flights, records were sampled across 4 distinct strata:

| Stratum | Selection Criterion | Available in Matched Cohort | Target Quota | Selected in Sample |
|---|---|---|---|---|
| **Early Flights (Negative Delay)** | `ARR_DELAY < 0.0` | 338,421 | 500 | 500 |
| **Exact On-Time Flights (Zero Delay)** | `ARR_DELAY == 0.0` | 24,115 | 200 | 200 |
| **Late Flights (Positive Delay)** | `ARR_DELAY > 0.0` | 178,578 | 700 | 700 |
| **Edge / Boundary Cases** | High delay / null measures | 18,022 | 100 | 100 |
| **Total Cohort** | — | **559,136** | **1,500** | **1,500** |

---

## 4. Completeness & Integrity Attestation

- **No Cherry-Picking:** All 1,500 records were selected strictly by deterministic pseudo-random hash order within strata.
- **Full Discrepancy Accounting:** Any discrepancy observed across any of the 7 CORE measures is exported to [`TS018_201901_DISCREPANCY_REGISTER.csv`](TS018_201901_DISCREPANCY_REGISTER.csv).
- **Zero Omission:** No matched record was filtered out or substituted.
