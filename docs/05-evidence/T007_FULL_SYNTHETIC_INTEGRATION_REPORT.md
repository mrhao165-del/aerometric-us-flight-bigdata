# T007_FULL_SYNTHETIC_INTEGRATION_REPORT — Multi-Year Synthetic Execution & Fault-Injection Report

**Document ID:** `T007-FULL-SYNTHETIC-INTEGRATION-20261017`  
**Task:** `T-007` (`T007-05`, `T007-06`, `T007-07`)  
**Parent Gate:** `G4` (`PLANNED / NOT_COMPLETED`)  
**Date:** `2026-10-17`

---

## 1. Purpose & Scope Boundary

Per `AGENTS.md` and `MASTER-T007` governance rules:
- Full-year Spark ingestion on the real 2016 CSV (`5,548,445` rows) is reserved for `T-010` at Gate `G5`.
- Full 9-year Spark ingestion (`54,674,003` rows) is reserved for `T-012` at Gate `G6`.
- `T-007` at Gate `G4` validates the complete ingestion pipeline using multi-year synthetic CSV datasets (`2016` and `2024`) through real PySpark 4.0.1 execution, real Parquet staging writes, real `SafePublisher` 7-step atomic publication, and real `RunManifest` + `ExecutionReceipt` sidecar generation.

---

## 2. Multi-Year Synthetic Integration Scenario (`INT-01`)

### 2.1 Synthetic Dataset Composition (`2016` + `2024`)
- **Year `2016` synthetic CSV (`5` rows total):**
  1. Valid standard flight (`2016-01-15`, `AA`, `"100.0"` -> normalized to `"100"`, `JFK` -> `LAX`) -> `ACCEPTED`
  2. Valid overnight flight (`2016-06-30`, `DL`, `"205"`, `SFO` -> `JFK`, `CRS_DEP_TIME=2345`, `CRS_ARR_TIME=0815`) -> `ACCEPTED` (no `+24h` rollover mutation per `FP-DEC-007`)
  3. Valid key with malformed numeric metric (`DEP_DELAY="NOT_A_NUM"`) -> `ACCEPTED` with `DEP_DELAY=NULL` (`DC-12`)
  4. Missing required key (`ORIGIN=""`) -> `QUARANTINED:MISSING_ORIGIN`
  5. Malformed CSV line (`only,three,tokens`) -> `REJECTED:MALFORMED_CSV_ROW`
- **Year `2024` synthetic CSV (`2` rows total):**
  1. Valid standard flight (`2024-02-10`, `WN`, `"900.0"` -> `"900"`, `DAL` -> `HOU`) -> `ACCEPTED`
  2. Unparseable `FL_DATE` (`2024-99-99`) -> `QUARANTINED:UNPARSEABLE_FL_DATE`

### 2.2 Verified `DC-11` Row Accounting & `DC-12` Metric Validity
- `source_rows_total`: `7`
- `accepted_rows`: `4`
- `quarantined_rows`: `2` (`MISSING_ORIGIN: 1`, `UNPARSEABLE_FL_DATE: 1`)
- `rejected_rows`: `1` (`MALFORMED_CSV_ROW: 1`)
- Conservation Identity (`DC-11`): `7 == 4 + 2 + 1` (`PASS`)
- Curated Parquet Row Count: `4` rows across `34` canonical columns
- `DC-12` Valid Metric Counts on Curated Data:
  - `is_valid_dep_delay("DEP_DELAY")`: `3` of `4` rows (`"NOT_A_NUM"` safely cast to `NULL`)
  - `is_valid_arr_delay("ARR_DELAY")`: `4` of `4` rows

### 2.3 Verified State Machine Trace & Sidecar Receipt
- State Trace:
  `RUN_STARTED -> SOURCE_VERIFICATION -> INGESTION_IN_PROGRESS -> INGESTION_COMPLETED -> STAGING_VERIFIED -> PUBLICATION_PENDING -> PUBLISHED`
- `ExecutionReceipt` (`data/metadata/<run_id>/execution_receipt.json`):
  - Records exact `manifest_bytes` and `manifest_sha256` of `run_manifest.json` after `run_manifest.json` is closed on disk, eliminating any self-referential hash paradox.
  - Records `upstream_identity_status = "IDENTITY_UNVERIFIED"` (`OR-08`) and `or05_coverage_warning` when `2024` is included (`OR-05`).
