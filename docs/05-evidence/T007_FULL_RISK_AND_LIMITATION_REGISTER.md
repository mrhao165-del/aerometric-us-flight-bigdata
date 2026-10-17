# T007_FULL_RISK_AND_LIMITATION_REGISTER — Active Risks, Mitigations & Open Governance Items

**Document ID:** `T007-FULL-RISK-REGISTER-20261017`  
**Task:** `T-007` — Raw CSV Ingestion Pipeline  
**Parent Gate:** `G4` (`PLANNED / NOT_COMPLETED`)  
**Date:** `2026-10-17`

---

## 1. Active Governance Risks & Controls

| Risk / Defect ID | Category | Description | Mitigation & Enforcement in `T-007` | Status |
|---|---|---|---|---|
| **OR-05** | Data Coverage (`2024`) | Year `2024` raw CSV covers `335/366` days (`2024-03-01..2024-03-31` missing; `6,348,823` rows). | Tracked as `OPEN_QUALITY_DEFECT` in `AUDITED_SOURCE_INVENTORY[2024]` and emitted in `ExecutionReceipt.or05_coverage_warning` whenever `2024` is ingested. | `OPEN_QUALITY_DEFECT` (Tracked) |
| **OR-08** | Upstream Provenance | No upstream cryptographic signature from BTS/NOAA exists for the 9 historical CSV files. | `SourceValidator` and `ExecutionReceipt` enforce `upstream_identity_status = "IDENTITY_UNVERIFIED"` (`G3-COND-A`). Local SHA-256 (`T007_LOCAL_RAW_SHA256_CANDIDATE.json`) is strictly labeled `LOCAL_HASH_COMPUTED_UNAPPROVED`. | `IDENTITY_UNVERIFIED` (Enforced) |
| **G2-EXC-001** | CORE Units | 7 CORE delay/time measures (`DEP_DELAY`, `ARR_DELAY`, `CRS_ELAPSED_TIME`, `ACTUAL_ELAPSED_TIME`, `AIR_TIME`, `TAXI_IN`, `TAXI_OUT`) carry provisional minute units pending empirical distribution verification on real data. | Marked `PROVISIONAL_MINUTES_PENDING_G5` in `schema.py` and `ExecutionReceipt.core_units_status`. Empirical verification (`TS-018`) is scheduled at Gate `G5` (`T-010`). | `PROVISIONAL_PENDING_G5` |
| **FP-DEC-017** | Weather Branch | 15 Weather columns lack verified upstream unit metadata (Celsius vs Kelvin/Fahrenheit, etc.). | Marked `CONDITIONAL_NO_GO` in `schema.py` and `ExecutionReceipt.weather_status`. Retained as nullable `DoubleType` in curated Parquet without blocking CORE (`AGENTS.md`). | `CONDITIONAL_NO_GO` |
| **WIN-PID-01** | Windows OS Signal Safety | Calling `os.kill(pid, 0)` on Windows sends `CTRL_C_EVENT` (`sig=0`) via `GenerateConsoleCtrlEvent`, terminating console processes (`agy cli`). | Eliminated `os.kill(pid, 0)` on Windows; `is_pid_alive()` in `locking.py` uses Win32 `OpenProcess` + `GetExitCodeProcess` (`STILL_ACTIVE == 259`). Verified by `test_t007_locking.py`. | `RESOLVED / MITIGATED` |
| **WIN-HADOOP-01** | Windows Hadoop Native IO | Local Windows hosts without `winutils.exe` / `hadoop.dll` fail on `df.write.parquet(dir)` and `spark.read.parquet(dir)` directory listing. | Implemented `write_dataframe_parquet_safe` (`mapInArrow` + `pyarrow.parquet.ParquetWriter`) and `read_parquet_safe` (explicit `.parquet` file paths) in `coordinator.py`. | `RESOLVED / MITIGATED` |

---

## 2. Explicit Scope Boundaries Observed in `T-007`

1. **No Raw CSV Modification:** All 9 files in `data/raw/tabular/2016..2024/` remain untouched (`mtime` and byte size identical).
2. **No Premature `G5` / `G6` Execution:** Real 2016 single-year Spark ingestion (`T-010`, Gate `G5`) and real 9-year Spark ingestion (`T-012`, Gate `G6`) were not executed during `T-007`.
3. **No Premature `T-008` Implementation:** `T-008` (KPI Aggregation & Analytical Views) remains `NOT_STARTED`.
