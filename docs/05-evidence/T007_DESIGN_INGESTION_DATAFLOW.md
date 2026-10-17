# T007 DESIGN INGESTION DATAFLOW — ARCHITECTURE, MEMORY BUDGET & EXECUTION LIFECYCLE

**Document ID:** `DOC-T007-DESIGN-03-DATAFLOW`  
**Task ID:** `T-007` (Raw CSV Ingestion Pipeline)  
**Phase:** `DESIGN ONLY`  
**Gate:** `G4` (`PLANNED / NOT_COMPLETED`)  
**Design Authority:** Senior Big Data Architect & Lead PySpark Data Engineer  
**Reference Implementations:** `src/flight_pipeline/config/spark_config.py`, `src/flight_pipeline/storage/publication.py`, `src/flight_pipeline/utils/run_manifest.py`  

---

## 1. END-TO-END INGESTION DATAFLOW ARCHITECTURE

The canonical ingestion pipeline ingests 9 annual CSV files comprising 54,674,003 raw rows (15.2 GB) into partitioned, immutable Parquet files with zero data loss, strict DC-11 row accounting, and atomic publishing.

```
+---------------------------------------------------------------------------------------------------+
|                                  STAGE 1: PREFLIGHT & VALIDATION                                  |
|  - Check single-writer lock (.publisher.lock)                                                     |
|  - Validate source inventory against SOURCE_MANIFEST.json (file sizes, mtimes, local SHA-256)     |
|  - Record entry gate status and initialize RunManifest (run_id, git_commit, config)               |
+---------------------------------------------------------------------------------------------------+
                                                  |
                                                  v
+---------------------------------------------------------------------------------------------------+
|                                STAGE 2: CONTROLLED CSV PARSE & READ                               |
|  - Apply explicit 34-column CANONICAL_CSV_SCHEMA (StructType)                                     |
|  - Mode: PERMISSIVE with _corrupt_record capture (or strict raw line accounting)                  |
|  - Batch processing: Annual sequential processing (Year 2016 through Year 2024)                   |
|  - Memory bounds: 4GB driver memory, off-heap scratch on local SSD                                |
+---------------------------------------------------------------------------------------------------+
                                                  |
                                                  v
+---------------------------------------------------------------------------------------------------+
|                               STAGE 3: CANONICAL ROW CLASSIFICATION                               |
|  - Structural checks: corrupt CSV parse error -> REJECTED (REJECTED_PARSE_ERROR)                  |
|  - Anchor checks: FL_DATE null/unparseable -> QUARANTINED (QUARANTINE_MALFORMED_DATE)               |
|  - Carrier & Airport checks: null OP_CARRIER, ORIGIN, DEST -> QUARANTINED                         |
|  - Flight number check (G3-COND-A): OP_CARRIER_FL_NUM <= 0 -> QUARANTINED (QUARANTINE_INVALID)    |
|  - Structural & Anchor PASS -> ACCEPTED                                                           |
+---------------------------------------------------------------------------------------------------+
                                                  |
                                                  v
+---------------------------------------------------------------------------------------------------+
|                               STAGE 4: METRIC SANITIZATION & STAGING                              |
|  - Format dates (DateType) and HHmm strings (zero-padded 4-char string, no date rollover)         |
|  - Evaluate finite numeric validity for 7 CORE measures (is_finite_numeric)                       |
|  - Preserve negative signed delays (DEP_DELAY, ARR_DELAY)                                         |
|  - Retain 6 weather columns as nullable (FP-DEC-017 CONDITIONAL_NO_GO)                            |
|  - Write to staging: data/staging/{run_id}/year={year}/*.parquet (Snappy compressed)              |
|  - Write quarantine & rejected rows to data/staging/{run_id}/quarantine/ and /rejected/           |
+---------------------------------------------------------------------------------------------------+
                                                  |
                                                  v
+---------------------------------------------------------------------------------------------------+
|                              STAGE 5: PRE-PUBLICATION AUDIT & VERIFY                              |
|  - Verify DC-11 invariant: raw_rows == accepted_rows + quarantined_rows + rejected_rows           |
|  - Verify Parquet integrity: magic byte check (PAR1) via is_valid_parquet_file                    |
|  - Compute part-file SHA-256 hashes                                                               |
+---------------------------------------------------------------------------------------------------+
                                                  |
                                                  v
+---------------------------------------------------------------------------------------------------+
|                                  STAGE 6: ATOMIC RUN PUBLICATION                                  |
|  - SafePublisher.publish_run: promote staging to data/curated/runs/{run_id}/                      |
|  - Atomically update pointer: data/curated/latest_run_id.txt (via os.replace)                     |
|  - Write RunManifest to run directory and update LATEST_RUN_MANIFEST.json                         |
|  - Release single-writer lock (.publisher.lock)                                                  |
+---------------------------------------------------------------------------------------------------+
```

---

## 2. MEMORY BUDGETING & SPARK EXECUTION ENGINE

### 2.1. Local Windows Execution Constraints
The target environment is a local Windows developer machine operating under the following resource parameters:
- **PySpark Runtime:** Version `4.0.1` on Python `3.10.11` (64-bit Windows 10/11).
- **Physical RAM:** 16 GB to 32 GB available.
- **Spark Execution Memory Allocation:**
  - `spark.driver.memory`: **4g** (strict cap to prevent JVM heap exhaustion and OS page paging).
  - `spark.sql.shuffle.partitions`: **16** (optimized for local CPU core count).
  - `spark.memory.fraction`: **0.6** (leaves 40% for execution buffers, metadata, and JVM garbage collection).
  - `spark.memory.storageFraction`: **0.3** (minimizes caching in memory, favors streaming disk spill).
  - `spark.local.dir`: Dedicated fast scratch directory on local SSD (avoids NTFS fragmentation and `%TEMP%` contention).

### 2.2. Batching Strategy (Year-by-Year Sequential Processing)
Rather than executing a single 54.7M row cross-year `read.csv()` which could trigger driver out-of-memory errors during partition scheduling and metadata aggregation:
1. The pipeline processes data in **annual batches** from `2016` to `2024`.
2. Each annual CSV file (~1.3 GB to ~2.0 GB, ~4.6M to ~7.4M rows) is parsed, classified, and written to its target staging partition: `data/staging/{run_id}/year={year}/`.
3. Intermediate Spark DataFrames are unpersisted immediately after writing the annual batch to staging.
4. Total cumulative row accounting and metric validation counters are accumulated in Python memory (`RowAccounting`, `MetricAccounting`).

---

## 3. SINGLE-SCAN VS. DOUBLE-SCAN TRADE-OFF ANALYSIS

A critical challenge under DC-11 is calculating:
$$\text{raw\_rows} = \text{accepted\_rows} + \text{quarantined\_rows} + \text{rejected\_rows}$$

### 3.1. Trade-off Options
1. **Option A (Double-Scan):**
   - *Scan 1:* Read raw CSV text lines using `spark.read.text()` to get the exact raw line count ($N_{\text{raw}} = N_{\text{lines}} - 1$).
   - *Scan 2:* Read with `CANONICAL_CSV_SCHEMA` and filter into accepted and quarantined sets.
   - *Pros:* 100% exact line count independent of parser behavior.
   - *Cons:* Double I/O scan over 15.2 GB of data (~30.4 GB total disk read).
2. **Option B (Single-Scan with Permissive Error Column):**
   - *Mechanism:* Configure PySpark CSV reader with:
     ```python
     .option("mode", "PERMISSIVE") \
     .option("columnNameOfCorruptRecord", "_corrupt_record")
     ```
   - In a single pass, every row is evaluated:
     - If `_corrupt_record` is not null $\implies$ `REJECTED`.
     - Else if structural anchor check fails $\implies$ `QUARANTINED`.
     - Else $\implies$ `ACCEPTED`.
   - *Pros:* Single I/O pass, highly efficient on local SSD.
   - *Cons:* Requires adding `_corrupt_record` to the parsing schema and dropping it before writing to curated Parquet.
3. **Recommended Canonical Design:**
   - Use **Option B (Single-Scan with `_corrupt_record`)** for high-performance pipeline execution.
   - Supplement with a lightweight raw line-count preflight check during initial source validation (or verify against `SOURCE_MANIFEST.json` audited line counts).
   - If $\text{raw\_rows} \neq \text{accepted} + \text{quarantined} + \text{rejected}$, the pre-publication audit fails immediately with `ACCOUNTING_UNVERIFIED` and blocks publishing.

---

## 4. DATE AND TIME HANDLING SPECIFICATION

1. **Date Parsing (`FL_DATE`):**
   - Format in CSV: `YYYY-MM-DD` or `YYYY-MM-DD 00:00:00`.
   - Validation: Must match anchored regex `^(?:\d{4}-\d{2}-\d{2}|\d{4}-\d{2}-\d{2} 00:00:00)$`.
   - Transformation: Extract standard `DateType` (`YYYY-MM-DD`).
   - If date token cannot be parsed $\implies$ Record quarantined with `QUARANTINE_MALFORMED_DATE`.
2. **Time Handling (`CRS_DEP_TIME`, `DEP_TIME`, `CRS_ARR_TIME`, `ARR_TIME`, `WHEELS_OFF`, `WHEELS_ON`):**
   - Times represent local military time (`HHmm`).
   - Formatting: Must be converted to 4-character zero-padded strings (e.g. numeric `930` $\to$ `"0930"`, `5` $\to$ `"0005"`).
   - **Prohibition on Date Rollover Invention:** Do NOT attempt to construct an arrival timestamp by adding 24 hours to overnight flights based solely on `ARR_TIME < DEP_TIME`. TranStats local times lack time zone identifiers and flight leg date anchors; date-time rollovers must not be invented in raw ingestion.

---

## 5. HANDLING YEAR 2024 SOURCE DEFECT (`OR-05`)

- **Known Defect:** Physical audit established that Year 2024 data completely lacks March 2024 (contains only 335 out of 366 days in leap year 2024).
- **Ingestion Policy:**
  - The pipeline ingests all 5,893,363 available records for 2024 without fabricating data for March 2024.
  - The pipeline automatically computes calendar date coverage for each ingested year.
  - When Year 2024 coverage is computed, the `RunManifest` explicitly flags:
    ```json
    "coverage_defects": [
      {
        "year": 2024,
        "defect_id": "OR-05",
        "status": "OPEN_QUALITY_DEFECT",
        "expected_days": 366,
        "observed_days": 335,
        "missing_ranges": ["2024-03-01 to 2024-03-31"],
        "governance_note": "BTS raw extract permanently lacks March 2024 data."
      }
    ]
    ```

---

## 6. STAGING TO ATOMIC PUBLICATION LIFECYCLE

The promotion from raw CSV to immutable curated storage follows the 7-step sequence governed by `SafePublisher`:

1. **Run Directory Isolation:** Staging writes to `data/staging/{run_id}/year={year}/*.parquet`.
2. **Parquet Integrity Check:** Every output part file is verified via `is_valid_parquet_file(file_path)` (ensuring file size $\ge 12$ bytes and valid `PAR1` magic bytes at offset 0 and EOF - 4).
3. **Audit Closure Check:** Verify that the `RunManifest` row counts balance exactly ($N_{\text{raw}} = N_{\text{accepted}} + N_{\text{quarantined}} + N_{\text{rejected}}$).
4. **Promotion to Curated:** Atomic directory move/rename from `data/staging/{run_id}/` to `data/curated/runs/{run_id}/`.
5. **Atomic Pointer Update:** `data/curated/latest_run_id.txt` is updated atomically using `os.replace` via temporary file `latest_run_id.txt.tmp`.
6. **Manifest Publication:** Write `data/curated/runs/{run_id}/run_manifest.json` and atomically copy to `data/curated/LATEST_RUN_MANIFEST.json`.
7. **Lock Release:** Release `.publisher.lock`.

---

## 7. DATAFLOW DESIGN VERDICT

The ingestion dataflow architecture fully honors all memory, storage, concurrency, and accounting constraints.

**DATAFLOW DESIGN VERDICT: APPROVED FOR T-007 IMPLEMENTATION PLANNING.**
