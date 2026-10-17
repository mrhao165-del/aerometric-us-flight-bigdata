# T007_FINAL_REMEDIATION_SOURCE_AND_DIFF_AUDIT — Source File Inventory, Cryptographic Hashes & Diff Audit

**Document ID:** `T007-FINAL-REMEDIATION-SOURCE-DIFF-20261017`  
**Task:** `MASTER-T007-FINAL-REMEDIATION` (`T-007` — Raw CSV Ingestion Pipeline)  
**Parent Gate:** `G4` (`PLANNED / NOT_COMPLETED`)  
**Entry Git Baseline:** `50cf2aac556e0d8e2ce76aeae5d0a911c29afc6b` (`master`)  
**Date:** `2026-10-17`

---

## 1. Scope & Boundary of Source Changes

Per `MASTER-T007-FINAL-REMEDIATION` directives:
- **Zero changes** were made to any `T-009` production or test file (`spark_config.py`, `predicates.py`, `publication.py`, `run_manifest.py`, `logging_config.py`, and their 5 test suites totaling `37` tests).
- **Zero changes** were made to already-accepted `T007-01` (`schema.py`, `22` tests), `T007-02A` (`source_validator.py`, `38` tests), or `T007-04` (`locking.py`, `8` tests).
- **Zero raw CSV files** in `data/raw/tabular/2016..2024/` were modified.
- Targeted production remediation was confined strictly to:
  1. [`src/flight_pipeline/ingestion/reader.py`](../../src/flight_pipeline/ingestion/reader.py) (`FIX-F01`, `FIX-F02`, `FIX-F06`)
  2. [`src/flight_pipeline/ingestion/coordinator.py`](../../src/flight_pipeline/ingestion/coordinator.py) (`FIX-F02`, `FIX-F03`, `FIX-F04`, `FIX-F05`)
  3. [`src/flight_pipeline/ingestion/__init__.py`](../../src/flight_pipeline/ingestion/__init__.py) (exporting new public classes and functions)
  4. [`tests/test_t007_reader.py`](../../tests/test_t007_reader.py) (expanded from `11` to `15` unit tests)
  5. [`tests/test_t007_pipeline_integration.py`](../../tests/test_t007_pipeline_integration.py) (expanded from `7` to `11` integration/fault-injection tests)

---

## 2. Complete Production & Test File Cryptographic Inventory

| File Path | Role / Task | Byte Size | SHA-256 Digest | Modified in Remediation? |
|---|---|---:|---|---:|
| `src/flight_pipeline/__init__.py` | Package root (`T-009`) | `216` | `41becc9dc684ed718be0f2af59899830b36c338956f7b62a8d0186b272ab991c` | No |
| `src/flight_pipeline/config/__init__.py` | Config package (`T-009`) | `222` | `1d6223c8ab4d594cd5051c1ea8945738852b544c089ddc4a64a80a9bf8d84715` | No |
| `src/flight_pipeline/config/spark_config.py` | Spark session factory (`T-009`) | `4,964` | `71e6ae6c70026e3e887fd7a88f0fc44e6ea3994f36480222cb51373dd919cdd4` | No |
| `src/flight_pipeline/quality/__init__.py` | Quality package (`T-009`) | `543` | `66bb045e629cb4088e277f0efffa2025001bf158120121535432b4b3e92f2e0e` | No |
| `src/flight_pipeline/quality/predicates.py` | Numeric predicates (`T-009`) | `3,290` | `b0cb88bf316231229eaba3afd07c34b5f0d65ae9cf240a3ccc6b63de1041f715` | No |
| `src/flight_pipeline/storage/__init__.py` | Storage package (`T-009`) | `174` | `1c6552b05566c7d00c979617cbee78f1817a903d7ee34c36826d09fd01b98195` | No |
| `src/flight_pipeline/storage/publication.py` | 7-step `SafePublisher` (`T-009`) | `17,096` | `86dd8b233e6d8ccaab05a2fd7269d6be3b967b743d56c980e9503c24502b5cbd` | No |
| `src/flight_pipeline/utils/__init__.py` | Utils package (`T-009`) | `267` | `81d522e8d4f5d8d7800b97dae11440fe05eccf418c533f2c2a86e07480534a8f` | No |
| `src/flight_pipeline/utils/logging_config.py` | Structured logging (`T-009`) | `1,236` | `f3229120f70872e56623b55c9ade61f7d3c4ba0fd3e2b3f27f5533b729358e63` | No |
| `src/flight_pipeline/utils/run_manifest.py` | `RunManifest` & `RowAccounting` (`T-009`) | `8,045` | `a50b82ebb8edb56b37d53d36fa32e104522d9a459db5a6eaca34e6650c18a21c` | No |
| `src/flight_pipeline/ingestion/__init__.py` | Ingestion exports (`T-007`) | `4,386` | `cd0683c0340205f0c429e8f3dfe4d597cd73d5679ac9c0338a1d895c32968ed8` | **Yes** |
| `src/flight_pipeline/ingestion/schema.py` | Canonical 34-col schema (`T007-01`) | `10,842` | `4302ff905ef38130b952f962c1aec48ca2df5cba7ca4b1b0696e9b46e772fb92` | No |
| `src/flight_pipeline/ingestion/source_validator.py` | Source validator (`T007-02A`) | `32,991` | `9c0f8da7c8433c98daba28a3ae16a657fe993ee53c0a09579d253fdfd07d8998` | No |
| `src/flight_pipeline/ingestion/reader.py` | CSV reader, header validator, scanner & classifier (`T007-03` / `FIX-F01/02/06`) | `40,558` | `56268bfd2b1339236b62400014c820858447d53b81239aa99c72f535366b1694` | **Yes** |
| `src/flight_pipeline/storage/locking.py` | Win32 single-writer lock (`T007-04`) | `10,675` | `4dd338adf0b9bc18c639d5e3664d6dc15fb61c36763949dde277a5de3c947976` | No |
| `src/flight_pipeline/ingestion/coordinator.py` | Ingestion coordinator, forensic persistence & 2-phase Parquet writer (`T007-05` / `FIX-F02..05`) | `52,716` | `de9c57a77ed6eb828449fef2c04ebf1b0cc4c7c979af398311513fc243eee941` | **Yes** |
| `tests/test_manifest.py` | `T-009` manifest tests (`6`) | `4,736` | `65cc38b29ec2b14c59e92ae4cf5651010e08328b44ca3c478e788a7aba99dd13` | No |
| `tests/test_numeric_predicates.py` | `T-009` predicate tests (`4`) | `5,375` | `72b5306ddd98cea8ff061eb8d6ef2a95049b38c6f7236d92410718e5b1d560b3` | No |
| `tests/test_publication_safety.py` | `T-009` publisher tests (`18`) | `25,802` | `babd4a787f8af54a8b202f619f3efb7f5aa0a061fd6bebb3c1d94c887df9b2dd` | No |
| `tests/test_spark_env.py` | `T-009` Spark env tests (`4`) | `5,597` | `04e48b481429c4fda9760e754ecfe598fecbb48605a9f148a256a40bfb4b2dfd` | No |
| `tests/test_t009_r3_defect_reproductions.py` | `T-009` R3 regression tests (`5`) | `4,409` | `c4c3dda0a2dfc7f3d9490af962e23733bc4ca64f3a5ddeb68d8462e463823807` | No |
| `tests/test_t007_schema.py` | `T007-01` schema tests (`22`) | `16,897` | `8975c52793b3ba4acb5d49562f79b6c83aab3b9363f3ab402e1418f11be2c1f2` | No |
| `tests/test_t007_source_validator.py` | `T007-02A` validator tests (`38`) | `40,759` | `7d0029aec59cf471a5deb266dde084cb98f947ff412983c9c020d2a884f162c9` | No |
| `tests/test_t007_reader.py` | `T007-03` reader & classifier tests (`15`) | `30,937` | `fe74c475e3e0d8e128c67e56e2b549c57d56a6af7c9b94eb743de4efc3d6e138` | **Yes** |
| `tests/test_t007_locking.py` | `T007-04` locking tests (`8`) | `8,041` | `3b35acfe1bcc5e139e94d28fa5673e01d60ad6fc32d8cc8617e0c0a27e8cb3a8` | No |
| `tests/test_t007_pipeline_integration.py` | `T007-05..07` E2E & negative tests (`11`) | `31,106` | `df1c4492a386db14c1b11680889a3c4d68219605a2ae3ec6b93d3973537893c3` | **Yes** |

---

## 3. Summary of Diffs in Modified Production Modules

1. **`src/flight_pipeline/ingestion/reader.py`:**
   - Added `HeaderValidationError`, `AccountingUnverifiedError`, and `SourceScanResult`.
   - Added `validate_physical_csv_header(source_path, options)` enforcing exact 34-column physical header validation (`FIX-F01`).
   - Added `scan_csv_logical_records(source_path, options, source_year)` performing independent `1 MiB` streaming physical line and RFC-4180 logical record counting (`FIX-F02`).
   - Added `RawCsvReader.attach_deterministic_lineage(df, source_path, source_year)` generating partition-independent content-hash `_record_lineage_id` (`FIX-F02`).
   - Upgraded `IngestionRecordClassifier.classify(df)` with real calendar date validation (`try_cast(substring(trim(FL_DATE), 1, 10) AS date)`), source-year vs `FL_DATE` year check, core identity anchors, and pipe-delimited `_anomaly_flags` (`FIX-F06`).
   - Upgraded `IngestionTransformer.to_curated(df)` to normalize `YYYY-MM-DD 00:00:00` -> `YYYY-MM-DD` and derive `MONTH`/`DAY_OF_MONTH` when raw calendar columns are null (`FIX-F06`).
   - Upgraded `compute_row_accounting()` and added `compute_per_year_accounting()` to reconcile independent source scan counts against Spark classifier counts per year and per run (`FIX-F02`).
2. **`src/flight_pipeline/ingestion/coordinator.py`:**
   - Added `PipelineState.PUBLISHED_RECEIPT_PENDING_RECONCILIATION` and `PipelineState.ABORTED_PRESERVED_PREVIOUS` (`FIX-F05`).
   - Added `ForensicPersistenceResult`, `persist_forensic_records()`, and `_parquet_dir_to_jsonl_atomic()` writing full `QUARANTINED` and `REJECTED` records into `data/quarantine/<run_id>/` and verifying readback counts (`FIX-F03`).
   - Upgraded `write_dataframe_parquet_safe()` with two-phase task attempt staging (`_task_attempts`) and added `verify_parquet_directory_integrity()` (`FIX-F04`).
   - Added `write_json_atomic_with_retry()`, separated pre-pointer vs post-pointer failure handling in `run_ingestion()` so `run_manifest.json` is never overwritten to `FAILED` after pointer switch or duplicate `run_id`, and added `reconcile_published_run(run_id)` (`FIX-F05`).
