# TS-018 January 2019 — Independent Replay Protocol
## Verification Protocol for Cross-Source Numerical Parity, Witness Auditing, and Two-Source Replay

**Project:** US Flight Performance Analysis 2016–2024  
**Date:** 2026-10-20 (Asia/Ho_Chi_Minh)  
**Parent Task:** Task T-011 / TS-018  
**Parent Gate:** Gate G5 (`IN_PROGRESS`)  
**Auditor References:** `TS018_201901_INDEPENDENT_AUDIT_20261020.md`, Findings TS018-I01, TS018-I02, TS018-I03  

---

## 1. Overview and Purpose

This protocol specifies the exact, deterministic steps required for an Independent Code Auditor or the Project Lead to verify the 100% record-level parity of the 1,500 sampled January 2019 flights across **both physical data sources**.

The verification is protected against single-source fabrication:
- It requires **both** physical sources to be present.
- It verifies that the witness file was **not** populated from BTS alone or from a synthetic fixture.
- It independently scans the 1.99 GB raw project CSV and the 29.98 MB official BTS ZIP.

---

## 2. Cryptographic Preconditions & Input Verification

Before executing the verification scripts, assert that the following files exist with their exact SHA-256 digests:

| File Name | Physical Path | Expected Bytes | Expected SHA-256 Checksum |
|---|---|---|---|
| **Raw Project Source** | `data/raw/tabular/2019/flight_with_weather_2019.csv` | 1,990,370,667 | `eec50211a1a63f37b840977be5ab2e99a008a8d5234c2a12df8eb50862f93b4a` |
| **BTS Reference ZIP** | `data/reference/bts_transtats/original/T_ONTIME_REPORTING_20261019_112232.zip` | 29,975,383 | `342de99f65561fb856b524c704f2ad3851f8015f52251668ece346dff1350ae6` |
| **Sample Witness CSV** | `docs/05-evidence/TS018_201901_MATCHED_SAMPLE_WITNESS.csv` | 294,436 | `942c476994c414378a541d5c84fcbdad35c6aeace1c98891044a085d55c3a9a1` |

To verify hashes via PowerShell:
```powershell
Get-FileHash data\reference\bts_transtats\original\T_ONTIME_REPORTING_20261019_112232.zip -Algorithm SHA256
Get-FileHash docs\05-evidence\TS018_201901_MATCHED_SAMPLE_WITNESS.csv -Algorithm SHA256
Get-FileHash data\raw\tabular\2019\flight_with_weather_2019.csv -Algorithm SHA256
```

---

## 3. Independent Two-Source Replay (Primary Verification)

### Command:
```powershell
python tools/qa/verify_ts018_two_source_sample_witness.py
```

### Execution Flow:
1. **Phase 1 — Ingestion:** Reads the 1,500 composite keys and all 14 numeric values from `TS018_201901_MATCHED_SAMPLE_WITNESS.csv`. Asserts that the witness contains exactly 1,500 distinct keys.
2. **Phase 2 — Raw Project CSV Replay:** Streams `flight_with_weather_2019.csv` directly from disk. Finds each of the 1,500 keys, parses the 7 numeric fields, and asserts exact match against `RAW_DATASET_<FIELD>`.
3. **Phase 3 — BTS ZIP CSV Replay:** Opens `T_ONTIME_REPORTING.csv` inside `T_ONTIME_REPORTING_20261019_112232.zip`. Finds each of the 1,500 keys, parses the 7 numeric fields, and asserts exact match against `BTS_<FIELD>`.
4. **Phase 4 — Direct Cross-Source Comparison:** Evaluates `abs(RAW_DATASET - BTS) < 1e-4` for all 10,500 value pairs (1,500 flights $\times$ 7 measures).

### Expected Output & Exit Code:
- **Expected Exit Code:** `0`
- **Expected Console Output:**
```text
================================================================================
INDEPENDENT TWO-SOURCE SAMPLE WITNESS VERIFIER (TS-018)
================================================================================
[WITNESS] Path:   .../docs/05-evidence/TS018_201901_MATCHED_SAMPLE_WITNESS.csv
[WITNESS] Bytes:  294436
[WITNESS] SHA256: 942c476994c414378a541d5c84fcbdad35c6aeace1c98891044a085d55c3a9a1
[OK] Candidate BTS ZIP checksum verified: 342de99f65561fb856b524c704f2ad3851f8015f52251668ece346dff1350ae6 (29975383 bytes)
[OK] Raw 2019 Dataset CSV checksum verified: eec50211a1a63f37b840977be5ab2e99a008a8d5234c2a12df8eb50862f93b4a (1990370667 bytes)

[PHASE 1] Ingesting sample witness records from CSV...
[WITNESS STATS] Total witness keys loaded: 1500

[PHASE 2] Replaying against physical Raw Dataset CSV (flight_with_weather_2019.csv)...
[DATASET REPLAY] Witness keys matched in Raw CSV: 1500 / 1500
[OK] All 1,500 witness rows match raw project CSV across all 7 fields (10,500/10,500 exact).

[PHASE 3] Replaying against physical BTS Reference CSV inside ZIP...
[BTS REPLAY] Witness keys matched in BTS CSV:     1500 / 1500
[OK] All 1,500 witness rows match BTS CSV across all 7 fields (10,500/10,500 exact).

[PHASE 4] Direct Cross-Source Parity Verification (Raw CSV vs BTS CSV)...
[CROSS-SOURCE PARITY] Comparisons: 10,500 (1,500 flights x 7 fields)
[CROSS-SOURCE PARITY] Exact Matches: 10500
[CROSS-SOURCE PARITY] Discrepancies: 0

================================================================================
VERIFICATION RESULT: 100% REPRODUCIBLE TWO-SOURCE PARITY PASS
================================================================================
  Witness File:        TS018_201901_MATCHED_SAMPLE_WITNESS.csv (SHA-256: 942c476994c414378a541d5c84fcbdad35c6aeace1c98891044a085d55c3a9a1)
  Physical Raw Source: flight_with_weather_2019.csv (SHA-256: eec50211a1a63f37b840977be5ab2e99a008a8d5234c2a12df8eb50862f93b4a)
  Physical BTS Source: T_ONTIME_REPORTING_20261019_112232.zip (SHA-256: 342de99f65561fb856b524c704f2ad3851f8015f52251668ece346dff1350ae6)
  Total Checked Rows:  1,500
  Total Fields:        10,500
  Exact Match Rate:    100.0% (10,500 / 10,500 exact)
================================================================================
```

---

## 4. Single-Source BTS Audit Script (Finding TS018-I01 & TS018-I02)

To verify the audit findings on the BTS ZIP independently without reading the project raw CSV:

```powershell
python TS018_201901_INDEPENDENT_EVIDENCE_CHECK_20261020.py data/reference/bts_transtats/original/T_ONTIME_REPORTING_20261019_112232.zip
```

### Expected Output:
- `zip_sha256`: `342de99f65561fb856b524c704f2ad3851f8015f52251668ece346dff1350ae6`
- `bts_rows`: `583985`
- `claimed_examples_present`: all `false` (confirming TS018-I01 reproduction)
- `arr_delay_null_total`: `18022`
- `arr_delay_null_not_cancelled_nor_diverted`: `0` (confirming TS018-I02 reproduction: active operating flights have 0 nulls)

---

## 5. Full Adapter Runner Re-Execution

To regenerate the witness CSV, discrepancy register, and full terminal log from scratch:

```powershell
# 1. Test safety guard (must fail code 2 when --allow-raw-preflight is omitted)
python tools/qa/run_ts018_bts_adapter.py

# 2. Run bounded preflight comparison under Option B protocol
python tools/qa/run_ts018_bts_adapter.py --allow-raw-preflight
```

### Safety Guarantees:
- **Zero Raw Mutation:** All inputs are opened strictly in read-only mode (`open(..., "r")`, `zipfile.ZipFile(..., "r")`).
- **Zero Staging Pollution:** No Parquet files are written to staging directories.
- **Zero Production Overwrite:** No KPI definitions, published pointers, or historical gates are altered.
