# T007_FULL_IMPLEMENTATION_ARCHITECTURE — End-to-End Ingestion Pipeline Design & Implementation

**Document ID:** `T007-FULL-ARCHITECTURE-20261017`  
**Task:** `T-007` (`T007-01` .. `T007-07`)  
**Parent Gate:** `G4` (`PLANNED / NOT_COMPLETED`)  
**Date:** `2026-10-17`

---

## 1. Architectural Overview

The `T-007` Raw CSV Ingestion Pipeline converts raw tabular CSV files (`2016..2024`, 34 canonical columns) into curated, schema-validated Apache Parquet artifacts under single-writer lock protection, strict `DC-11` row accounting, and 7-step Windows NTFS atomic publication (`SafePublisher` from `T-009`).

```
+-------------------------------------------------------------------------+
|                     IngestionCoordinator (T007-05)                      |
|  1. Validate run_id & Acquire SingleWriterLock (T007-04, Win32 PID)     |
|  2. SourceValidator (T007-02A/02B): lstat/reparse check, size & SHA-256 |
|  3. RawCsvReader (T007-03): PERMISSIVE + _corrupt_record + 34 String    |
|  4. IngestionRecordClassifier: ACCEPTED vs QUARANTINED vs REJECTED      |
|  5. compute_row_accounting (DC-11): single-pass agg invariant check     |
|  6. IngestionTransformer: ANSI-safe try_cast + temporal derivation      |
|  7. write_dataframe_parquet_safe: streaming Arrow->Parquet to staging   |
|  8. SafePublisher (T-009): 7-step NTFS atomic publish + pointer switch  |
|  9. RunManifest + ExecutionReceipt: atomic JSON sidecar persistence     |
+-------------------------------------------------------------------------+
```

---

## 2. Module Responsibilities & File Mapping

| Component | Source File | Responsibility |
|---|---|---|
| **Canonical Schema (`T007-01`)** | `src/flight_pipeline/schema.py` | Immutable 34-column canonical contract, defensive `StructType` factories (`get_raw_csv_read_schema`, `get_curated_schema`), 7 CORE measures (`G2-EXC-001`), 15 Weather measures (`FP-DEC-017` `CONDITIONAL_NO_GO`). |
| **Source Validator (`T007-02A/02B`)** | `src/flight_pipeline/ingestion/source_validator.py` | Traversal/symlink/junction (`FILE_ATTRIBUTE_REPARSE_POINT`) defense, 9-year inventory enforcement, streaming 1 MB SHA-256 calculation, 3-state hash status, `OR-08` `IDENTITY_UNVERIFIED`. |
| **CSV Reader & Classifier (`T007-03`)** | `src/flight_pipeline/ingestion/reader.py` | `RawCsvReader` (`mode=PERMISSIVE`, `columnPruning.enabled=false`, `_corrupt_record`), `IngestionRecordClassifier` (`ACCEPTED`, `QUARANTINED`, `REJECTED`), `IngestionTransformer` (`try_cast` to `DoubleType`, `FL_DATE` temporal parsing, `OP_CARRIER_FL_NUM` `.0` normalization), `compute_row_accounting`. |
| **Single-Writer Lock (`T007-04`)** | `src/flight_pipeline/storage/locking.py` | Cross-process exclusive lock (`O_CREAT \| O_EXCL`) at `data/locks/ingestion_writer.lock`, native Win32 `OpenProcess`/`GetExitCodeProcess` liveness check (avoiding Windows `os.kill(pid, 0)` `CTRL_C_EVENT`), stale lock recovery with forensic preservation. |
| **Ingestion Coordinator (`T007-05`)** | `src/flight_pipeline/ingestion/coordinator.py` | Lifecycle state machine (`RUN_STARTED` -> `SOURCE_VERIFICATION` -> `INGESTION_IN_PROGRESS` -> `INGESTION_COMPLETED` -> `STAGING_VERIFIED` -> `PUBLICATION_PENDING` -> `PUBLISHED` / `ABORTED_PRESERVED_PREVIOUS` / `TERMINAL_FAILURE`), `write_dataframe_parquet_safe`, `ExecutionReceipt`, integration with `SafePublisher` and `RunManifest`. |
| **Atomic Publication (`T-009`)** | `src/flight_pipeline/storage/publisher.py` | Reused unchanged (`100%` backward-compatible): 7-step staging verification, `os.replace` directory move, `CURRENT_PUBLISHED_RUN.json` atomic pointer update. |
| **Run Manifest (`T-009`)** | `src/flight_pipeline/metadata/manifest.py` | Reused unchanged: `RowAccounting` (`DC-11` invariant validator) and `RunManifest` serialization. |

---

## 3. Key Engineering Solutions for PySpark 4.0.1 on Windows

1. **Disabling CSV Column Pruning (`spark.sql.csv.parser.columnPruning.enabled=false`):**
   - By default, Spark's Univocity CSV parser prunes unreferenced columns during aggregations (such as `groupBy(_record_status).count()`), which would skip parsing trailing columns and fail to populate `_corrupt_record` on truncated/extra-token lines. `RawCsvReader.read_raw()` temporarily sets `spark.sql.csv.parser.columnPruning.enabled=false` while building the CSV DataFrame plan so all 34 tokens are strictly inspected.
2. **Spark 4.0 ANSI Mode Safe Numeric Casting (`try_cast`):**
   - Spark 4.0 enables `spark.sql.ansi.enabled=true` by default, causing `.cast(DoubleType())` to throw `CAST_INVALID_INPUT` on malformed numeric strings instead of returning `NULL`. `IngestionTransformer.to_curated()` uses `F.expr("try_cast(col AS double)")`, ensuring malformed metric strings safely evaluate to `NULL` inside accepted rows per `DC-12`.
3. **Win32 Process Liveness Inspection (`OpenProcess` vs `os.kill(pid, 0)`):**
   - On Windows, `os.kill(pid, 0)` passes `sig=0` (`CTRL_C_EVENT`) to `GenerateConsoleCtrlEvent`, terminating the console process group (`agy cli`). `is_pid_alive()` in `locking.py` uses `ctypes.WinDLL("kernel32").OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid)` + `GetExitCodeProcess` (`STILL_ACTIVE = 259`) with zero console signals.
4. **Windows `winutils.exe`-Free Distributed Parquet Writer (`write_dataframe_parquet_safe`):**
   - Because local Windows environments without `HADOOP_HOME/bin/winutils.exe` fail on `df.write.parquet()` (`FileNotFoundException`), `write_dataframe_parquet_safe` uses `df.mapInArrow` + `pyarrow.parquet.ParquetWriter` to stream Arrow batches per partition directly to standard Snappy-compressed `.parquet` files in `staging/<run_id>` in O(1) driver memory.
