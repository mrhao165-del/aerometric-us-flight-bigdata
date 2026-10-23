# TS-018 January 2019 — Actual Stratum and Key Coverage Audit
## Exhaustive Key Accounting, Population Overlap, Duplicate Verification, and Actual Stratum Breakdown

**Project:** US Flight Performance Analysis 2016–2024  
**Date:** 2026-10-20 (Asia/Ho_Chi_Minh)  
**Parent Task:** Task T-011 / TS-018  
**Parent Gate:** Gate G5 (`IN_PROGRESS`)  
**Scope:** Controlled, read-only preflight comparison (`2019_raw_source_vs_BTS_candidate`, Option B)  
**Auditor References:** `TS018_201901_INDEPENDENT_AUDIT_20261020.md`, Finding TS018-I02, Finding TS018-I03  

---

## 1. Physical Source Provenance and Cryptographic Verification

Both physical data sources were verified directly from disk via SHA-256 and byte size before execution:

| Source Role | Physical File Path | File Bytes | SHA-256 Checksum | Invariant / Status |
|---|---|---|---|---|
| **Raw Project Source (2019)** | `data/raw/tabular/2019/flight_with_weather_2019.csv` | 1,990,370,667 | `eec50211a1a63f37b840977be5ab2e99a008a8d5234c2a12df8eb50862f93b4a` | Immutable, read-only |
| **Candidate BTS Reference ZIP** | `data/reference/bts_transtats/original/T_ONTIME_REPORTING_20261019_112232.zip` | 29,975,383 | `342de99f65561fb856b524c704f2ad3851f8015f52251668ece346dff1350ae6` | Immutable, read-only |
| **Contained BTS CSV** | Member `T_ONTIME_REPORTING.csv` inside ZIP | 217,369,264 (uncompressed) | `dce92e8f602d02ef50f2354789653dd770bc46d948c13a48e3518f2998068bec` | CRC32 `0x7d8573c4` verified |

> [!IMPORTANT]
> **Comparison Label:** `2019_raw_source_vs_BTS_candidate`.  
> **Curated Parquet State:** `PARQUET_PARITY_NOT_TESTED`. January 2019 curated Parquet is not present in staging. This evaluation verifies the raw tabular unit consistency against official BTS Part 234 reporting. Physical 2016 Parquet remains available under Option A if curated Parquet output parity is required.

---

## 2. Row Count, Unique Keys, and Duplicate Collision Accounting (TS018-I03)

To ensure no silent deduplication or dictionary overwriting obscures collisions, raw row counts, unique keys, and duplicate occurrences were tracked independently on **both** sides:

### 2.1 Project Raw Dataset Side (`flight_with_weather_2019.csv`)
- **Total Rows in File (Full Year 2019):** `7,161,827`
- **January 2019 Raw Rows:** `559,136`
- **January 2019 Unique Composite Keys:** `559,136`
- **January 2019 Duplicate Composite Keys:** **`0`**
- **Collision / Ambiguity Rate:** **`0.0%`** (every January 2019 row represents a distinct flight composite key).

### 2.2 BTS Candidate Reference Side (`T_ONTIME_REPORTING.csv`)
- **Total Rows in File (January 2019):** `583,985`
- **January 2019 Unique Composite Keys:** `583,985`
- **January 2019 Duplicate Composite Keys:** **`0`**
- **Collision / Ambiguity Rate:** **`0.0%`** (every BTS row represents a distinct flight composite key).

---

## 3. Full Population Overlap & Universe Breakdown

```text
+-------------------------------------------------------------------------------+
|                       BTS Population: 583,985 records                         |
|  +---------------------------------------------+---------------------------+  |
|  |     Matched Keys Cohort: 559,136 records    |  Unmatched: 24,849 recs   |  |
|  |     (100.0% of Project Dataset)             |  - Cancelled: 16,726      |  |
|  |                                             |  - Diverted:   1,296      |  |
|  |                                             |  - Unmatched Active: 6,827|  |
|  +---------------------------------------------+---------------------------+  |
+-------------------------------------------------------------------------------+
```

### Detailed Population Ledger:
1. **Total BTS Records:** `583,985`
2. **Matched Composite Keys:** `559,136`
3. **Dataset Records Unmatched:** **`0`** (Dataset coverage is **100.0%**; every flight in the dataset exists in BTS).
4. **BTS Records Unmatched:** `24,849`:
   - **Cancelled Flights (`CANCELLED == 1.0`):** `16,726` records. Excluded upstream from the project dataset per `DATA_CONTRACT.md` (DC-11: operational flights only).
   - **Diverted Flights (`DIVERTED == 1.0`):** `1,296` records. Excluded upstream per DC-11 due to incomplete terminal arrival segments.
   - **Unmatched Active Operating Flights:** `6,827` records (1.17% of total BTS flights; 1.21% of active BTS flights). These flights operated in the US national airspace but were omitted during upstream compilation of the Kaggle tabular CSV. No causal claim of weather-join drop is made because compilation scripts are external to this repository.

---

## 4. BTS Missing Value (`ARR_DELAY` Null) Root Cause Analysis (TS018-I02)

The independent audit identified that the earlier document claimed "18,022 available null-stratum records in the matched cohort". The programmatic audit of the BTS reference reveals:

| BTS Operational Status | Total Flights | Flights with `ARR_DELAY is None` | Flights with Valid `ARR_DELAY` |
|---|---|---|---|
| **Active Flights (Not Diverted)** | 565,963 | **0** | 565,963 |
| **Cancelled Flights** | 16,726 | **16,726** | 0 |
| **Diverted Flights** | 1,296 | **1,296** | 0 |
| **Total BTS Universe** | **583,985** | **18,022** | **565,963** |

### Key Governance Finding:
1. Every single flight with missing `ARR_DELAY` in BTS January 2019 is **either cancelled or diverted**.
2. **Zero** active operating non-diverted flights have missing `ARR_DELAY`.
3. Because cancelled and diverted flights are excluded from the project raw dataset, the matched operating cohort has **exactly 0 null `ARR_DELAY` records**.
4. The earlier citation of 18,022 null records in the matched cohort was an accounting error transposing BTS-wide cancelled/diverted counts onto the operating dataset.

---

## 5. Actual Strata in Matched Cohort & Deterministic Sampling Audit

### 5.1 Matched Cohort Population Distribution
Within the 559,136 matched operating flights, the true delay distribution is:

| Stratum Name | Definition | Available in Matched Cohort | Percentage of Cohort |
|---|---|---|---|
| `NEGATIVE_DELAY` | `ARR_DELAY < 0.0` (Early arrival) | 358,420 | 64.10% |
| `ZERO_DELAY` | `ARR_DELAY == 0.0` (Exact on-time arrival) | 10,284 | 1.84% |
| `POSITIVE_DELAY` | `ARR_DELAY > 0.0` (Late arrival) | 190,432 | 34.06% |
| `NULL_DELAY` | `ARR_DELAY is None` (Missing arrival delay) | **0** | **0.00%** |
| **Total Matched Cohort** | All operational flights | **559,136** | **100.00%** |

### 5.2 Deterministic Stratified Selection & Top-Up Accounting
Per TS-018 protocol, deterministic sampling was executed using SHA-256 hashing with seed `"ts018_bts_jan2019_seed_42"`:

$$\text{score}(k) = \text{SHA-256}(\text{"ts018\_bts\_jan2019\_seed\_42"} \parallel \text{FL\_DATE} \parallel \text{OP\_CARRIER} \parallel \text{FL\_NUM} \parallel \text{ORIGIN} \parallel \text{DEST})$$

| Stratum Name | Target Quota | Available in Cohort | Selected Count | Selection Mechanism |
|---|---|---|---|---|
| `NEGATIVE_DELAY` | 500 | 358,420 | **500** | Lowest hash score within stratum |
| `ZERO_DELAY` | 200 | 10,284 | **200** | Lowest hash score within stratum |
| `POSITIVE_DELAY` | 700 | 190,432 | **700** | Lowest hash score within stratum |
| `NULL_DELAY` | 100 | 0 | **0** | Shortfall of 100 due to 0 available |
| `REMAINDER_TOPUP` | Shortfall | 557,736 | **100** | Lowest hash score among remaining flights |
| **Total Sample Witness** | **1,500** | **559,136** | **1,500** | Complete determinism, 0 cherry-picking |

---

## 6. Machine-Readable Sample Witness Summary (TS018-I03)

The complete list of 1,500 selected flights, their strata, hash scores, and all 14 numeric values (7 from raw project CSV, 7 from BTS reference CSV) is exported to:
- **File:** [`docs/05-evidence/TS018_201901_MATCHED_SAMPLE_WITNESS.csv`](TS018_201901_MATCHED_SAMPLE_WITNESS.csv)
- **Rows:** 1,500 records (+ 1 header row)
- **Size:** 294,436 bytes
- **SHA-256:** `942c476994c414378a541d5c84fcbdad35c6aeace1c98891044a085d55c3a9a1`
- **Two-Source Replay Status:** Verified via `tools/qa/verify_ts018_two_source_sample_witness.py` (Exit code 0, 10,500/10,500 exact matches).
