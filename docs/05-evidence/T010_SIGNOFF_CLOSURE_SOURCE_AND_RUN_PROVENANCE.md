# T010 SIGNOFF CLOSURE: SOURCE INTEGRITY & REAL-DATA EXECUTION PROVENANCE

**Document ID:** `T010_SIGNOFF_CLOSURE_SOURCE_AND_RUN_PROVENANCE`  
**Parent Task:** `MASTER-T010-SIGNOFF-CLOSURE`  
**Parent Gate:** `G5 — Bounded Real-Data Smoke & Resource Benchmark`  
**Role:** Data Integrity Engineer, Production Reliability Auditor & Independent QA Reviewer  
**Audit Date:** 2026-10-18  

---

## 1. Physical Raw Source Integrity & Immutability Verification

In strict compliance with `AGENTS.md` and `DATA_CONTRACT.md`, physical raw flight data was accessed in **read-only mode**. Zero bytes were modified, overwritten, or created in `data/raw/`.

| File Attribute | Pre-Execution Baseline | Post-Run 1 (Historical) | Post-Run 2 (Closure) | Audit Assessment |
| :--- | :--- | :--- | :--- | :---: |
| **Physical File Path** | `data/raw/tabular/2016/flight_with_weather_2016.csv` | Same | Same | **IDENTICAL** |
| **Physical Byte Size** | `1,538,427,452` bytes | `1,538,427,452` bytes | `1,538,427,452` bytes | **0 BYTES MUTATED** |
| **Filesystem Mtime** | `1787484809.8685696` | `1787484809.8685696` | `1787484809.8685696` | **UNTOUCHED** |
| **Streaming SHA-256** | `4ed92ed732721a38ae28325135fad63436347613674ad96c1b273eb9d44cef34` | Same | Same | **BIT-FOR-BIT IDENTICAL** |
| **Physical Header Columns** | Exactly 34 columns (UTF-8, No BOM) | 34 columns | 34 columns | **MATCH CANONICAL** |
| **Audited Logical Records** | `5,537,987` data rows | `5,537,987` data rows | `5,537,987` data rows | **EXACT MATCH** |
| **Governance Status** | `LOCAL_HASH_COMPUTED_UNAPPROVED` | `LOCAL_HASH_COMPUTED_UNAPPROVED` | `LOCAL_HASH_COMPUTED_UNAPPROVED` | **OR-08 PRESERVED** |
| **Upstream Identity Status**| `IDENTITY_UNVERIFIED` | `IDENTITY_UNVERIFIED` | `IDENTITY_UNVERIFIED` | **OR-08 PRESERVED** |

---

## 2. Multi-Run Execution Provenance Matrix

Pursuant to FIX-02, the repository preserves both the historical baseline execution (Run 1) and the enhanced signoff closure execution (Run 2) with full forensic logs, environment metadata, and execution parameters.

| Execution Dimension | Run 1 (Historical Baseline) | Run 2 (Authoritative Closure Run) | Delta / Remarks |
| :--- | :--- | :--- | :--- |
| **Run Timestamp (UTC)** | `2026-10-18T11:07:20Z` | `2026-10-18T12:22:36Z` | Controlled re-run for closure |
| **Executable Command Line** | `python tools/qa/run_t010_real_data_smoke.py` | `python tools/qa/run_t010_real_data_smoke.py` | Identical entrypoint |
| **Working Directory (CWD)** | `D:\Study\Code\Apache\Flight_Analyzt\US_FLIGHT_PERFORMANCE_DOCS_V1` | `D:\Study\Code\Apache\Flight_Analyzt\US_FLIGHT_PERFORMANCE_DOCS_V1` | Exact repository root |
| **Git Commit Baseline** | `bc4f03fb8ccd6c0b2455af3fcb2b1b98fa39d632` | `bc4f03fb8ccd6c0b2455af3fcb2b1b98fa39d632` | Stable Git HEAD |
| **Raw Execution Log File** | `docs/05-evidence/T010_RUN1_HISTORICAL_REAL_DATA_EXECUTION.txt` | `docs/05-evidence/T010_RUN2_CLOSURE_REAL_DATA_EXECUTION.txt` | Both preserved in full |
| **Log File Size / Lines** | `11,210` bytes / 164 lines | `12,771` bytes / 266 lines | Enhanced with tree RSS & disk preflight |
| **Spark Application ID** | `local-1792322838320` | `local-1792326155314` | Distinct isolated sessions |
| **Runtime Versions** | Python 3.10.11 / PySpark 4.0.1 / Java 21.0.12.1 | Python 3.10.11 / PySpark 4.0.1 / Java 21.0.12.1 | Fully identical toolchain |
| **Free Disk Space at Start** | Unrecorded snapshot | `63.06 GB` (Staging volume `D:\`) | Verified > 30 GB threshold |
| **Phase 0 Entrypoint Guard** | Ran in tests | Enforced at runner entrypoint before CSV read | FIX-04 fully satisfied |
| **January Counting Method** | Spark DataFrame `count()` | Streaming CSV token scanner + Spark verification | FIX-03 fully satisfied |
| **Micro Sampling Method** | Spark `df.limit(1000)` | Deterministic physical sample fixture with SHA-256 | FIX-03 fully satisfied |
| **Micro Sample Hash** | Dynamic limit | `37b8ce77cce667ff161af2ddbc975f20385482b473f8b41ac90a94bee442026b` | Exact reproducible hash |
| **Driver Peak RSS (Python)** | `211.36 MB` | `200.96 MB` | Consistent (<5.2% budget) |
| **Process Tree Peak RSS** | Not sampled | `2,164.64 MB` (Python driver + JVM processes) | True application footprint |
| **Peak JVM Heap Sampled** | `468.60 MB` (snapshot) | `1,055.22 MB` (high-frequency background sampling) | Sampled during active shuffle/write |
| **JVM Heap Maximum** | `4,096.00 MB` | `4,096.00 MB` | > 3.0 GB headroom |
| **Curated Parquet Output** | `332,018,057` bytes (12 files) | `332,018,057` bytes (12 files) | **Exact byte-for-byte determinism** |
| **Parquet Readback Rows** | `5,537,987` rows | `5,537,987` rows | **100% row conservation** |
| **DC-11 Conservation** | $5,537,987 = 5,537,987 + 0 + 0$ | $5,537,987 = 5,537,987 + 0 + 0$ | **Exact balance** |
| **DC-12 7 CORE Metrics** | 100% valid rate | 100% valid rate (independently audited) | Validated in FIX-07 |

---

## 3. Storage Isolation & Zero Publication Leak

1. **Isolation of Staging Artifacts:**
   All Parquet files, metadata receipts, and sample fixtures were generated exclusively inside timestamped directories under `D:\Study\Code\Apache\Flight_Analyzt\staging\`.
2. **Production Pointer Preserved:**
   The canonical production pointer `data/curated/latest` was **NOT created, updated, or altered** in either run.
3. **Repository Cleanliness:**
   Neither the 1.54 GB raw CSV nor the 332 MB Parquet output files were staged into Git or packed into review archives.
