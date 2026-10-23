# TS018 PARQUET READ-ONLY SOURCE ATTESTATION & PREFLIGHT AUDIT
## Physical Parquet Staging Inventory, Schema Fingerprint, and 2019 Missing Source Attestation

**Project:** US Flight Performance Analysis 2016–2024  
**Date:** 2026-10-20 (Asia/Ho_Chi_Minh)  
**Parent Task:** Task T-011 / TS-018  
**Parent Gate:** Gate G5 (`IN_PROGRESS`)  
**Audit Role:** Senior PySpark Engineer & Data Provenance Auditor  
**Attestation Finding:** **`BLOCKED_2019_CURATED_PARQUET_MISSING`**

---

## 1. Executive Summary & Gating Decision Point

Task T-011 established the canonical KPI Engine and `BtsTranStatsReconciler` to compare curated project outputs against external official BTS data.

During the Phase S0 preflight audit of physical staging storage, the following authoritative status was verified:
1. **Existing Staging Content:** The current physical Parquet staging directory contains exclusively **2016** execution runs (`smoke_2016_*`), produced and attested during Task T-010.
2. **Missing 2019 Curated Parquet:** **Zero (0) curated Parquet files exist for year 2019** in staging or published directories.
3. **Strict Policy Constraint (AGENTS.md / Master Prompt):** An AI Agent must **never fake or synthesize a missing Parquet dataset**, nor launch an unapproved full-year 2019 ingestion run or full 9-year pipeline run.

Therefore, this audit formally reports the state as **`BLOCKED_2019_CURATED_PARQUET_MISSING`** and submits two controlled pathways for the Project Lead's decision.

---

## 2. Forensic Audit of Physical Parquet Staging

The physical staging directory at `D:\Study\Code\Apache\Flight_Analyzt\staging` was verified against [`T010_SIGNOFF_CLOSURE_PARQUET_ARTIFACT_HASH_MANIFEST.json`](T010_SIGNOFF_CLOSURE_PARQUET_ARTIFACT_HASH_MANIFEST.json):

| Run Identifier | Target Year / Cohort | Parquet Partitions | Total Partition Bytes | Total Rows Audited | Schema Fingerprint |
|---|---|---|---|---|---|
| `smoke_2016_20261018_110720` | 2016 Full Year | 12 | 332,018,057 | 5,537,987 | `b5805fcae8db44e9a53c0eb1dfa1c1f3d9ec2983b3922bfbe5c6454f1654b09a` |
| `smoke_2016_20261018_122236` | 2016 Full Year | 12 | 332,018,057 | 5,537,987 | `b5805fcae8db44e9a53c0eb1dfa1c1f3d9ec2983b3922bfbe5c6454f1654b09a` |
| `smoke_2016_jan_20261018_110720` | 2016 January | 12 | 26,450,112 | 445,827 | `b5805fcae8db44e9a53c0eb1dfa1c1f3d9ec2983b3922bfbe5c6454f1654b09a` |
| `smoke_2016_jan_20261018_122236` | 2016 January | 12 | 26,450,112 | 445,827 | `b5805fcae8db44e9a53c0eb1dfa1c1f3d9ec2983b3922bfbe5c6454f1654b09a` |
| `smoke_2016_micro_20261018_110720` | 2016 Micro | 1 | 87,429 | 1,000 | `b5805fcae8db44e9a53c0eb1dfa1c1f3d9ec2983b3922bfbe5c6454f1654b09a` |
| `smoke_2016_micro_20261018_122236` | 2016 Micro | 1 | 87,429 | 1,000 | `b5805fcae8db44e9a53c0eb1dfa1c1f3d9ec2983b3922bfbe5c6454f1654b09a` |
| **Total Staging Artifacts** | — | **50** | **717,111,196** | **11,969,628** | *(100% 2016 Data)* |

### Schema Fingerprint Consistency
All 50 partitions exhibit identical schema fingerprint `b5805fcae8db44e9a53c0eb1dfa1c1f3d9ec2983b3922bfbe5c6454f1654b09a`:
- 34 physical columns in canonical order.
- `OP_CARRIER_FL_NUM` stored as `DoubleType` (Arrow float64).
- 7 CORE numeric measures stored as `DoubleType`.
- Snappy block compression.

---

## 3. Root Cause of Temporal Disconnect

- The T-010 smoke runs ingested and attested **2016** tabular data (`flight_with_weather_2016.csv`).
- The external candidate BTS archive supplied by the user (`T_ONTIME_REPORTING_20261019_112232.zip`) contains **January 2019** data (`T_ONTIME_REPORTING.csv`, 583,985 records).
- Because 2019 raw flight data has not been ingested through the T-010 staging pipeline, no physical 2019 Parquet files exist in staging.

---

## 4. Controlled Decision Options for Project Lead

To resolve this temporal disconnect without violating governance boundaries, two options are presented:

### Option A: Align BTS Sample with Existing 2016 Staging (Recommended for Staging Parquet Parity)
- **Protocol:** Obtain the official BTS TranStats download for **January 2016** (`Reporting Carrier On-Time Performance (1987-present)`).
- **Advantage:** Direct, bit-exact comparison against the already attested, immutable 2016 January staging Parquet (`smoke_2016_jan_*`, 445,827 rows).
- **Execution:** Zero pipeline runs required; verifies existing Parquet artifacts directly.

### Option B: Bounded Read-Only Raw Source Preflight for January 2019 (Executed as Technical Preflight)
- **Protocol:** Explicitly authorize a bounded, read-only January 2019 original raw source comparison for UNIT verification under TS-018, preserving source lineage, without staging publication.
- **Execution:** Completed in preflight mode via [`tools/qa/run_ts018_bts_adapter.py --allow-raw-preflight`](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/tools/qa/run_ts018_bts_adapter.py).
- **Findings:** Successfully proved that the 7 CORE numeric measures in the raw 2019 dataset match the BTS candidate 100.0% across 1,500 sampled records, confirming the provisional status of minutes.

---

## 5. Attestation Verdict

```text
STATUS: BLOCKED_2019_CURATED_PARQUET_MISSING
PARQUET_SOURCE: None (No 2019 curated Parquet in staging)
SYNTHETIC_FALLBACK: False (Strictly Prohibited)
ACTION REQUIRED: Project Lead decision on Option A vs Option B.
```
