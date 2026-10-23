# G6_T012_2016_CANONICAL_EXECUTION_RUNBOOK.md
## Canonical Operational Runbook for Year 2016 Production Ingestion (T-012)

**Project:** US Flight Performance Analysis 2016–2024  
**Date:** 2026-10-21  
**Gate Status:** G5 = IN_PROGRESS (TECHNICALLY READY) | G6 = NOT_STARTED / BLOCKED  
**Author:** Principal Big Data Engineer & PySpark Production Release Engineer  
**Supersedes:** Obsolete row references and legacy commands in `G6_T012_FIRST_YEAR_EXECUTION_READINESS.md`  
**Governance Guard:** **D5 (Gate G6 Annual Ingestion Authorization) = NOT_AUTHORIZED / PENDING PROJECT LEAD SIGNATURE**

---

## 1. Canonical Source File Identity & Row Accounting (Finding E01)

Per `DATA_CONTRACT.md`, `source_validator.py`, and `G5_T010_ENTRY_BASELINE_ERRATA.md`, the canonical baseline for survey year 2016 is strictly defined as follows:

| Metric | Canonical Value | Obsolete/Typo Value (Superseded) | Verification Method |
|---|---|---|---|
| **Survey Year** | `2016` | `2016` | Static Invariant |
| **Source Relative Path** | `data/raw/tabular/2016/flight_with_weather_2016.csv` | Same | Physical Path on Disk |
| **Physical File Size** | **1,538,427,452 bytes** | Same | `os.stat().st_size` |
| **Canonical RAW Rows** | **5,537,987 rows** | ~~5,617,658 rows~~ (Typo) | `SourceValidator` & T-010 Errata |
| **Canonical SHA-256** | `4ed92ed732721a38ae28325135fad63436347613674ad96c1b273eb9d44cef34` | Same | Streaming SHA-256 |
| **Upstream Identity Status** | `IDENTITY_UNVERIFIED` (OR-08) | Same | `DECISIONS.md` |
| **Source Coverage Status** | `VERIFIED_WITH_SCOPE` | Same | BTS TranStats Scope |

> [!IMPORTANT]
> **DC-11 Balanced Accounting Requirement:**
> Post-ETL accounting must satisfy:
> $$\text{Raw Rows } (5,537,987) = \text{Accepted Rows } + \text{Quarantined Rows } + \text{Rejected Rows}$$
> Ingestion must NOT assume $\text{Accepted} = \text{Raw}$ prior to execution. Any discrepancy triggers fail-closed abort.

---

## 2. Storage Roots, Lock Paths & Recovery Architecture (Finding E04)

All operations must resolve strictly against a single, coherent `--base-data-dir` (default: `data`):

| Component | Physical Path Relative to Workspace | Governed Role |
|---|---|---|
| **Base Data Dir** | `data/` | Root container for pipeline storage |
| **Raw Storage** | `data/raw/tabular/2016/flight_with_weather_2016.csv` | Immutable, read-only source data |
| **Lock Directory** | `data/locks/` | Single-writer concurrency control |
| **Production Lock File** | `data/locks/.pipeline.lock` | Active write mutex managed by `SingleWriterLock` |
| **Staging Root** | `data/staging/{run_id}/` | Ephemeral scratch directory for PySpark writes |
| **Curated Runs Root** | `data/curated/runs/{run_id}/` | Published immutable Parquet datasets |
| **Active Pointer File** | `data/curated/latest_run_id.txt` | Atomic pointer to certified active run (`SafePublisher`) |
| **Metadata Root** | `data/metadata/{run_id}/` | Audit sidecars (`run_manifest.json`, `execution_receipt.json`) |

### Two-Phase Commit & Recovery Sequence
1. **Phase 1 (Staging & Validation — Steps 1–4):** PySpark writes Parquet partitions to `data/staging/{run_id}/`. Parquet Thrift metadata, column schemas, and DC-11 row accounting are strictly validated. If any error occurs, staging directory is wiped cleanly. No pointer or catalog state is altered.
2. **Phase 2 (Atomic Publication & Commit — Steps 5–7):** `SafePublisher` atomically moves staging to `data/curated/runs/{run_id}/` and updates `data/curated/latest_run_id.txt`. Once Step 5 succeeds, the commit is irreversible. Any subsequent failure (e.g. metadata write) triggers recovery reconciliation (`reconcile_published_run`) rather than destructive rollback.

---

## 3. Resource & Environmental Preflight Policy (Section 8)

| Metric | Measured Workstation Value | Runbook Legacy Threshold | Status / Assessment |
|---|---|---|---|
| **Free Disk Space** | **57.83 GiB** | 60 GiB | `UNAPPROVED_RESOURCE_THRESHOLD` |
| **Available RAM** | **3.27 GiB** | 8 GiB | `UNAPPROVED_RESOURCE_THRESHOLD` (Meets 3.0 GiB min operational threshold) |
| **Total System RAM** | **15.71 GiB (16.87 GB)** | N/A | Physical System Hardware |
| **Python Runtime** | Python 3.10.11 / 3.11.9 | Python 3.10+ | Satisfied |
| **PySpark Engine** | PySpark 4.0.1 | PySpark 3.4+ | Satisfied |
| **Java JDK Runtime** | OpenJDK 21.0.12.1 (Vector Inc) | OpenJDK 17/21 | Satisfied |
| **Operating System** | Windows 11 Enterprise (NTFS) | Windows NTFS | Satisfied |

> [!WARNING]
> The historical runbook stated arbitrary thresholds (60 GiB disk / 8 GiB RAM) without formal benchmark justification. A single annual batch (2016) generates ~1.5 GB compressed Parquet and requires ~3.2 GB peak RAM. However, per governance policy, AI agents cannot unilaterally lower thresholds. The threshold is classified as `UNAPPROVED_RESOURCE_THRESHOLD` and submitted to Project Lead for formal approval under Decision D5.

---

## 4. Production Execution Procedures (Finding E03)

### Step 1: Pre-Execution Writer Safety Check
Verify that no stale lock, dangling pointer, or uncommitted staging directory exists:
```powershell
python tools/qa/check_writer_preflight_safety.py --base-dir data
```
*Expected Output:* `SAFE_TO_PROCEED_TO_LOCK_ACQUISITION` (Exit Code: 0)

### Step 2: Ingestion Coordinator Dry-Run Preflight (Safe, Non-Writing)
Validate run parameters, source inventory, row counts, and lock status without initializing PySpark or writing data:
```powershell
python -m flight_pipeline.ingestion.coordinator --years 2016 --run-id run_2016_v1 --base-dir data --dry-run-preflight
```
*Expected Output:*
```
[PREFLIGHT PASS] Preflight safety inspection completed successfully. All mandatory safety criteria PASSED. No data written.
```
(Exit Code: 0)

### Step 3: Production Ingestion Execution (REQUIRES DECISION D5)
> [!CAUTION]
> **DO NOT EXECUTE WITHOUT EXPLICIT WRITTEN AUTHORIZATION FROM PROJECT LEAD (DECISION D5).**
> Live execution without `--dry-run-preflight` will encounter the autonomous governance hold:
```powershell
python -m flight_pipeline.ingestion.coordinator --years 2016 --run-id run_2016_v1 --base-data-dir data
```

---

## 5. Post-Execution Single-Run Verification (Finding E02)

Following successful completion of the annual batch, verification MUST be performed using the dedicated single-run verifier rather than the multi-year snapshot registry:

```powershell
python tools/qa/verify_multiyear_snapshot.py --single-run-year 2016 --run-id run_2016_v1 --base-dir data
```

### Verification Invariants Evaluated
1. **Recursive Parquet Discovery (R05):** All files discovered via `discover_physical_parquet_files()`.
2. **Manifest Outputs Verification:** Full relative path, byte size, and SHA-256 match 1:1 against disk.
3. **Canonical Row Count Accounting:** RAW row count strictly matches 5,537,987; accepted rows match physical Parquet rows.
4. **Schema Compliance:** Contains all 7 CORE measures and zero forbidden columns.
5. **Execution Receipt Strictness:** `execution_receipt.json` matches `run_manifest.json` cryptographic hash.

*Expected Output upon certified completion:*
```
[SINGLE-RUN PASS] Year 2016 run run_2016_v1 successfully validated.
Status: VALID_SINGLE_RUN_ANNUAL_BATCH
```
(Exit Code: 0)
