# TS-018 Final Independent Replay Report
## Two-Source Physical Parity Verification, Per-Field Exact Numeric Equality, and Example Attestation

**Project:** US Flight Performance Analysis 2016–2024  
**Date:** 2026-10-20 (Asia/Ho_Chi_Minh)  
**Parent Task:** Task T-011 / TS-018  
**Parent Gate:** Gate G5 (`IN_PROGRESS`)  
**Scope:** Controlled, read-only preflight comparison (`2019_raw_source_vs_BTS_candidate`, Option B)  
**Status:** **AUTHORITATIVE REPLAY REPORT**  

---

## 1. Executive Summary & Verification Verdict

The independent two-source replay verifier [`verify_ts018_two_source_sample_witness.py`](../../tools/qa/verify_ts018_two_source_sample_witness.py) was executed directly against **both physical sources** and the machine-readable sample witness [`TS018_201901_MATCHED_SAMPLE_WITNESS.csv`](TS018_201901_MATCHED_SAMPLE_WITNESS.csv).

```text
================================================================================
FINAL REPLAY VERIFICATION LEDGER
================================================================================
Total Selected Flight Keys:            1,500 distinct composite keys
Keys Verified in Raw Project CSV:      1,500 / 1,500 (100.0%)
Keys Verified in BTS TranStats ZIP:    1,500 / 1,500 (100.0%)
Many-to-Many Key Collisions:           0
Non-Finite Values (NaN / Infinity):    0
Total Record-Level Field Comparisons:  10,500 (1,500 flights x 7 fields)
Exact Bitwise Numeric Equality:        10,500 / 10,500 (100.0%, diff == 0.0)
Tolerance-Only Matches (diff <= 1e-4): 0
Null / Missing Disagreements:          0
Numerical Mismatches:                  0
Final Replay Verdict:                  100% REPRODUCIBLE TWO-SOURCE PARITY PASS
================================================================================
```

---

## 2. Physical Artifact Cryptographic Attestation

Prior to verification, the digests and physical sizes of all relevant artifacts were verified:

| Artifact Role | Physical File Path | File Bytes | SHA-256 Checksum | Invariant Status |
|---|---|---|---|---|
| **Raw Project Source (2019)** | `data/raw/tabular/2019/flight_with_weather_2019.csv` | 1,990,370,667 | `eec50211a1a63f37b840977be5ab2e99a008a8d5234c2a12df8eb50862f93b4a` | Immutable, read-only |
| **Candidate BTS Reference ZIP** | `data/reference/bts_transtats/original/T_ONTIME_REPORTING_20261019_112232.zip` | 29,975,383 | `342de99f65561fb856b524c704f2ad3851f8015f52251668ece346dff1350ae6` | Immutable, read-only |
| **Contained BTS CSV** | Member `T_ONTIME_REPORTING.csv` inside ZIP | 217,369,264 (uncompressed) | `dce92e8f602d02ef50f2354789653dd770bc46d948c13a48e3518f2998068bec` | CRC32 `0x7d8573c4` verified |
| **Sample Witness CSV** | `docs/05-evidence/TS018_201901_MATCHED_SAMPLE_WITNESS.csv` | 294,436 | `942c476994c414378a541d5c84fcbdad35c6aeace1c98891044a085d55c3a9a1` | Immutable witness record |

> [!IMPORTANT]
> **Comparison Scope & Boundaries:**
> - Comparison Label: `2019_raw_source_vs_BTS_candidate` (Option B).
> - Curated Parquet State: `PARQUET_PARITY_NOT_TESTED`. This verification evaluates numerical unit consistency between the project raw dataset and official BTS Part 234 reporting. Physical 2016 Parquet (50 files, SNAPPY, fingerprint `b5805fcae8db...`) is present in staging and remains available under Option A if curated Parquet output parity is required.

---

## 3. Per-Field Exact Numeric Equality Breakdown

To avoid obscuring rounding approximations behind an aggregate tolerance, each of the seven CORE numeric measures was evaluated for **exact bitwise equality** ($\text{diff} == 0.0$) versus **tolerance match** ($\text{diff} \le 10^{-4}$):

| Measure Field | Meaning | Exact Bitwise Equality | Tolerance Only | Null-Null Agreement | Mismatch Count | Total Comparisons |
|---|---|---|---|---|---|---|
| `ARR_DELAY` | Arrival delay (minutes, signed) | **1,500** | 0 | 0 | 0 | 1,500 |
| `DEP_DELAY` | Departure delay (minutes, signed) | **1,500** | 0 | 0 | 0 | 1,500 |
| `TAXI_OUT` | Taxi-out duration (minutes) | **1,500** | 0 | 0 | 0 | 1,500 |
| `TAXI_IN` | Taxi-in duration (minutes) | **1,500** | 0 | 0 | 0 | 1,500 |
| `AIR_TIME` | Airborne duration (minutes) | **1,500** | 0 | 0 | 0 | 1,500 |
| `ACTUAL_ELAPSED_TIME` | Door-to-door elapsed time (minutes) | **1,500** | 0 | 0 | 0 | 1,500 |
| `CRS_ELAPSED_TIME` | Scheduled elapsed time (minutes) | **1,500** | 0 | 0 | 0 | 1,500 |
| **TOTALS** | All 7 CORE Measures | **10,500** | **0** | **0** | **0** | **10,500** |

### Key Forensic Findings:
1. **Zero Tolerance-Only Matches:** In every single one of the 10,500 comparisons, the raw project CSV value and the BTS value are **bit-for-bit identical**. No rounding divergence ($10^{-4}$) was utilized or required.
2. **Preservation of Negative Delay Signs:** Negative arrival and departure delays are preserved in both sources (e.g. `-6.0`, `-4.0`). No premature floor clipping (`max(0, delay)`) occurs in raw staging or intake.
3. **No Zero Substitution for Nulls:** Zero delay (`0.0`) is rigorously distinguished from missing values. (In the matched operating cohort, available nulls equal 0 because cancelled/diverted flights are excluded per DC-11).
4. **Finite Values Guaranteed:** Zero `NaN`, `+Infinity`, `-Infinity`, or unparseable tokens were encountered in the sample cohort.

---

## 4. Re-Verification of Corrected Real-Data Examples

The three programmatically verified flight examples introduced in [`TS018_201901_EVIDENCE_CORRECTION_ERRATA.md`](TS018_201901_EVIDENCE_CORRECTION_ERRATA.md) were re-queried directly from the raw physical CSV and the physical BTS ZIP:

### Authentic Record 1 — Early Arrival (Negative Delay Stratum)
- **Composite Key:** `2019-01-10` | `NK` | `314` | `IAH` $\rightarrow$ `TPA`
- **Stratum:** `NEGATIVE_DELAY` | **Selection Score:** `15ebfd7d7eeff5be4cead2ec8574c93f0b2f3d5386f874836696ef2c6e61f93f`
- `ARR_DELAY`: Raw Dataset = `-6.0`, BTS = `-6.00` $\rightarrow$ **EXACT MATCH** (diff = 0.0)
- `DEP_DELAY`: Raw Dataset = `-4.0`, BTS = `-4.00` $\rightarrow$ **EXACT MATCH** (diff = 0.0)
- `TAXI_OUT`: Raw Dataset = `13.0`, BTS = `13.00` $\rightarrow$ **EXACT MATCH** (diff = 0.0)
- `TAXI_IN`: Raw Dataset = `8.0`, BTS = `8.00` $\rightarrow$ **EXACT MATCH** (diff = 0.0)
- `AIR_TIME`: Raw Dataset = `98.0`, BTS = `98.00` $\rightarrow$ **EXACT MATCH** (diff = 0.0)
- `ACTUAL_ELAPSED_TIME`: Raw Dataset = `119.0`, BTS = `119.00` $\rightarrow$ **EXACT MATCH** (diff = 0.0)
- `CRS_ELAPSED_TIME`: Raw Dataset = `121.0`, BTS = `121.00` $\rightarrow$ **EXACT MATCH** (diff = 0.0)

### Authentic Record 2 — Exact On-Time Arrival (Zero Delay Stratum)
- **Composite Key:** `2019-01-31` | `UA` | `753` | `SFO` $\rightarrow$ `EWR`
- **Stratum:** `ZERO_DELAY` | **Selection Score:** `0cf6df084473857bb643193e16440db9fe71fa6e0a9b83b3e648c6b54134812a`
- `ARR_DELAY`: Raw Dataset = `0.0`, BTS = `0.00` $\rightarrow$ **EXACT MATCH** (diff = 0.0)
- `DEP_DELAY`: Raw Dataset = `0.0`, BTS = `0.00` $\rightarrow$ **EXACT MATCH** (diff = 0.0)
- `TAXI_OUT`: Raw Dataset = `24.0`, BTS = `24.00` $\rightarrow$ **EXACT MATCH** (diff = 0.0)
- `TAXI_IN`: Raw Dataset = `10.0`, BTS = `10.00` $\rightarrow$ **EXACT MATCH** (diff = 0.0)
- `AIR_TIME`: Raw Dataset = `295.0`, BTS = `295.00` $\rightarrow$ **EXACT MATCH** (diff = 0.0)
- `ACTUAL_ELAPSED_TIME`: Raw Dataset = `329.0`, BTS = `329.00` $\rightarrow$ **EXACT MATCH** (diff = 0.0)
- `CRS_ELAPSED_TIME`: Raw Dataset = `329.0`, BTS = `329.00` $\rightarrow$ **EXACT MATCH** (diff = 0.0)

### Authentic Record 3 — Substantial Delay (Positive Delay Stratum)
- **Composite Key:** `2019-01-21` | `AA` | `692` | `PHX` $\rightarrow$ `HNL`
- **Stratum:** `POSITIVE_DELAY` | **Selection Score:** `763ef9081ae2b4c8ad0678eb8c6c59600e1cfeb5b7965aa30164bc9ba3e945c7`
- `ARR_DELAY`: Raw Dataset = `+1186.0`, BTS = `+1186.00` $\rightarrow$ **EXACT MATCH** (diff = 0.0)
- `DEP_DELAY`: Raw Dataset = `+1191.0`, BTS = `+1191.00` $\rightarrow$ **EXACT MATCH** (diff = 0.0)
- `TAXI_OUT`: Raw Dataset = `28.0`, BTS = `28.00` $\rightarrow$ **EXACT MATCH** (diff = 0.0)
- `TAXI_IN`: Raw Dataset = `17.0`, BTS = `17.00` $\rightarrow$ **EXACT MATCH** (diff = 0.0)
- `AIR_TIME`: Raw Dataset = `364.0`, BTS = `364.00` $\rightarrow$ **EXACT MATCH** (diff = 0.0)
- `ACTUAL_ELAPSED_TIME`: Raw Dataset = `409.0`, BTS = `409.00` $\rightarrow$ **EXACT MATCH** (diff = 0.0)
- `CRS_ELAPSED_TIME`: Raw Dataset = `414.0`, BTS = `414.00` $\rightarrow$ **EXACT MATCH** (diff = 0.0)

---

## 5. Execution Command and Replay Log

The independent replay script was executed with the following result:
```powershell
python tools/qa/verify_ts018_two_source_sample_witness.py
# Exit code: 0
# Comparisons: 10,500
# Discrepancies: 0
```
Full stdout log is persisted in [TS018_201901_RAW_CLOSURE_LOG.txt](TS018_201901_RAW_CLOSURE_LOG.txt).
