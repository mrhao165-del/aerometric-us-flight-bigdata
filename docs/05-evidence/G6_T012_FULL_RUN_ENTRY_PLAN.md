# Gate G6 Task T-012 — Full 9-Year Run Entry Plan
## Sequential Annual Ingestion, Quality Partitioning, and Atomic Staging Protocol (2016–2024)

**Project:** US Flight Performance Analysis 2016–2024  
**Date:** 2026-10-20 (Asia/Ho_Chi_Minh)  
**Parent Task:** Task T-012 / Gate G6  
**Parent Gate State:** `G6 — NOT_STARTED / BLOCKED` (Design & Preparation Only)  
**Execution Condition:** **STRICTLY BLOCKED until Project Lead signs Gate G5 exit**  
**Status:** **AUTHORITATIVE ARCHITECTURAL SPECIFICATION**  

---

## 1. Architectural Scope and Principles

Task `T-012` governs the full multi-year data ingestion and quality staging for all nine survey years (2016 through 2024), representing approximately 54.7 million flight records across 14.15 GB of raw CSV data.

To guarantee zero data loss, avoid Windows filesystem contention, and eliminate memory crashes, T-012 is architected under five fundamental principles:
1. **Sequential Annual Batches:** The 9 years are processed strictly one calendar year at a time ($2016 \rightarrow 2017 \rightarrow \dots \rightarrow 2024$). Processing all 9 years simultaneously is prohibited.
2. **Immutable Baseline Preservation:** The existing, attested 2016 physical staging Parquet (`data/staging/`, fingerprint `b5805fca...`) must remain intact as the validated baseline.
3. **Annual Checkpoint & Fail-Closed Boundary:** Each annual run executes under an independent atomic transaction. If Year $Y$ encounters a schema anomaly or accounting mismatch, the pipeline halts immediately; previously validated years ($2016 \dots Y-1$) remain 100% durable.
4. **DC-11 / DC-12 Strict Accounting:** At every annual boundary, the pipeline must reconcile:
   $$\text{Raw Rows}(Y) = \text{Accepted Rows}(Y) + \text{Quarantined Rows}(Y) + \text{Rejected Rows}(Y)$$
5. **Honest Coverage Disclosure (OR-05 & OR-08):** Year 2024 processes the available 335 days, records `source_coverage_status = PARTIAL`, and strictly prohibits synthetic record fabrication.

---

## 2. Nine-Year Raw Input Inventory

All 9 physical CSV files exist in the repository under `data/raw/tabular/`:

| Calendar Year | Physical Path | Raw File Bytes | Size (GB) | Canonical SHA-256 Digest (`AUDITED_SOURCE_INVENTORY`) |
|---|---|---|---|---|
| **2016** | `data/raw/tabular/2016/flight_with_weather_2016.csv` | 1,538,427,452 | 1.43 GB | `4ed92ed732721a38ae28325135fad63436347613674ad96c1b273eb9d44cef34` (Errata G5-T010) |
| **2017** | `data/raw/tabular/2017/flight_with_weather_2017.csv` | 1,549,837,485 | 1.44 GB | `67b8dbd6678576b1a2229ef2dbeec065e0f64d31d688ab8a2ca59c88d2a656f9` |
| **2018** | `data/raw/tabular/2018/flight_with_weather_2018.csv` | 1,941,406,432 | 1.81 GB | `0398bab8f1b79a5f3bea628b707e18c3af628f37a1daa52de6849fb8bdfc71a3` |
| **2019** | `data/raw/tabular/2019/flight_with_weather_2019.csv` | 1,990,370,667 | 1.85 GB | `eec50211a1a63f37b840977be5ab2e99a008a8d5234c2a12df8eb50862f93b4a` |
| **2020** | `data/raw/tabular/2020/flight_with_weather_2020.csv` | 1,197,858,795 | 1.12 GB | `787981046c9fe0f4884ac207a3d28ea6a7fae98e89535cb9f8a37debb5c7fa5d` |
| **2021** | `data/raw/tabular/2021/flight_with_weather_2021.csv` | 1,600,032,487 | 1.49 GB | `5b7cc4801a6ff5cf432137632209ebd7aecd3d4a0f83e8920e3525116e88defc` |
| **2022** | `data/raw/tabular/2022/flight_with_weather_2022.csv` | 1,782,648,882 | 1.66 GB | `45eb45e801d6eeeb16167306fc69a8449177191cfff29bfb5d22285827f53140` |
| **2023** | `data/raw/tabular/2023/flight_with_weather_2023.csv` | 1,847,433,387 | 1.72 GB | `9c9e20f55d3dd10a127bcdd28680df6547a01a82ad71999b794aff3e1075d7bd` |
| **2024** | `data/raw/tabular/2024/flight_with_weather_2024.csv` | 1,748,350,586 | 1.63 GB | `f938ade95a031088467ab5e75abea2021e541eaf4a4288e564066e100541d5f7` |
| **TOTAL** | All 9 Survey Years | **15,196,366,173** | **14.15 GB** | Pinned in `AUDITED_SOURCE_INVENTORY` |

---

## 3. Sequential Year-by-Year Pipeline Lifecycle

Each annual iteration $Y \in [2016 \dots 2024]$ executes under a strictly bounded 6-stage lifecycle:

```
[Stage 1: Preflight] ──► [Stage 2: Schema Validate] ──► [Stage 3: Quality Engine]
                                                                  │
[Stage 6: Checkpoint] ◄── [Stage 5: Atomic Publish]  ◄── [Stage 4: Safe Staging]
```

1. **Stage 1 — Preflight & Lock Acquisition:**
   - Verify SHA-256 and byte size of `flight_with_weather_<year>.csv`.
   - Acquire exclusive `SingleWriterLock(staging/active/<year>)`.
   - Verify disk headroom on `D:` ($\ge 25\text{ GB}$).
2. **Stage 2 — Schema & Type Validation (TS-001 / TS-002):**
   - Read CSV using `RawCsvReader` in ANSI mode.
   - Assert all 34 required columns exist.
   - Validate timestamp patterns (`YYYY-MM-DD` prefix).
3. **Stage 3 — Quality Engine Partitioning (T-008, DC-11/12):**
   - Execute quality predicate catalog (`is_valid_date`, `is_valid_carrier`, `is_valid_airport`).
   - Partition into Accepted, Quarantined, Rejected.
   - Enforce DC-11 accounting invariant: `raw = accepted + quarantined + rejected`.
4. **Stage 4 — Safe Staging Write:**
   - Write partitioned Parquet to `staging/runs/run_<year>_<run_id>/`.
   - Codec: Snappy compression (`spark.sql.parquet.compression.codec = snappy`).
   - Coalesce partitions to 16 to 32 files per year to prevent small-file overhead.
5. **Stage 5 — Atomic Publication & Manifest Creation:**
   - Publish run directory using `SafePublisher` 7-step atomic rename protocol.
   - Update `staging/active/<year>/latest` pointer.
   - Generate `run_manifest.json` with partition counts, byte sizes, and CRC digests.
6. **Stage 6 — Annual Checkpoint & Lock Release:**
   - Emit audit summary: `quality_summary_<year>.csv`.
   - Safely release `SingleWriterLock`.
   - Clean up temporary Spark shuffle directories in `tmp_spark/`.

---

## 4. Special Handling for Defect OR-05 (Year 2024)

When the pipeline reaches calendar year 2024:
1. **Expect Missing Month:** The pipeline configuration expects `335` days instead of `366`.
2. **Fail-Closed Drift Guard Bypass Prohibition:** The 31 missing days (`2024-03-01` to `2024-03-31`) are recognized as a documented project defect (`OR-05`), **not a random pipeline failure**.
3. **Honest Quality Metric Emission:**
   - `annual_calendar_days_present = 335`
   - `annual_temporal_coverage_rate = 335 / 366 = 91.53%`
   - `source_coverage_status = PARTIAL`
4. **Prohibition of Imputation:** No artificial flights, synthetic delays, or interpolated weather data shall be injected.

---

## 5. Exit Criteria for Task T-012

Task T-012 will be accepted when:
1. All 9 years have published active staging Parquet partitions under `staging/active/<year>/`.
2. All 9 annual run manifests exist and pass checksum validation.
3. Total multi-year DC-11 accounting balances exactly across all ~54.7 million rows.
4. Total execution benchmarks are compiled into the `TS-014` full-run report.
