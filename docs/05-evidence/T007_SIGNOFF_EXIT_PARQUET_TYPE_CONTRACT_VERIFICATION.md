# T007_SIGNOFF_EXIT — PARQUET TYPE CONTRACT VERIFICATION (`BLOCKER-02`)

**Project:** US Flight Performance Analysis 2016–2024  
**Task:** `MASTER-T007-SIGNOFF-EXIT` (`BLOCKER-02` Closure)  
**Target Module:** `src/flight_pipeline/ingestion/coordinator.py` (`71,897` bytes, SHA-256 `2577275651b8f60e23af38725c8d8f01792e969a42ad471e238e320257652d06`)  
**Target Test Suite:** `tests/test_t007_pipeline_integration.py` (`INT-06: test_blocker02_parquet_type_contract_verification_and_pipeline_guard`)  

---

## 1. Root Cause Analysis of Pre-Fix `BLOCKER-02`

In commit `0434fe527da1bda5cf7830273921093876692364`, `verify_parquet_directory_integrity(..., verify_curated_schema=True)` loaded `expected_curated_schema = get_curated_parquet_schema()` and `arrow_sch = pq_file.schema_arrow`, but only checked:
- absence of leaked technical column names (`forbidden_tech_cols`), and
- `col_names == list(CANONICAL_COLUMN_NAMES)` (`34` column names in order).

It did not compare `arrow_sch.field(i).type` or `arrow_sch.field(i).nullable` against `expected_curated_schema.fields[i]`. Consequently, a Parquet file with the 34 canonical column names where numeric columns (`DEP_DELAY`, `ARR_DELAY`, `FLIGHTS`, `MONTH`, `ORIGIN_INDEX`, etc.) were physically stored as `string` (or `int32`/`float32`) or where temporal string columns (`FL_DATE`, `DEP_TIME`) were physically stored as `date32`/`timestamp` could pass `verify_parquet_directory_integrity`.

---

## 2. Production Fix Implemented in `src/flight_pipeline/ingestion/coordinator.py`

Added `verify_arrow_schema_against_curated(arrow_sch: pa.Schema, source_name: str = "<parquet>") -> None` and integrated it into `verify_parquet_directory_integrity(..., verify_curated_schema=True)` (which runs at the end of `write_dataframe_parquet_safe`, at `STAGING_VERIFIED` prior to `SafePublisher.publish()`, and during `reconcile_published_run()`).

For every `.parquet` file in a curated staging or published directory, `verify_arrow_schema_against_curated` enforces:
1. **Zero Technical Column Leakage:** Rejects any column in `forbidden_tech_cols` (`_corrupt_record`, `_record_status`, `_anomaly_reason`, `_anomaly_flags`, `_source_year`, `_source_file`, `_record_lineage_id`) or any underscore-prefixed column (`col.startswith("_")`).
2. **Exact 34-Column Name & Order Match (`0..33`):** `list(arrow_sch.names) == list(CANONICAL_COLUMN_NAMES)`.
3. **Exact Field-by-Field Physical Arrow Data Type Match against `get_curated_parquet_schema()`:**
   - **8 `StringType` columns** (`FL_DATE`, `OP_CARRIER`, `ORIGIN`, `DEST`, `CRS_DEP_TIME`, `DEP_TIME`, `WHEELS_OFF`, `WHEELS_ON`, `CRS_ARR_TIME`, `ARR_TIME` — wait: 10 `StringType` columns total in `CURATED_PARQUET_SCHEMA`): must satisfy `pa.types.is_string(t) or pa.types.is_large_string(t)`. Physical `date32`, `date64`, `timestamp`, `int*`, `float*`, or `binary` types are strictly rejected.
   - **19 `DoubleType` columns** (`OP_CARRIER_FL_NUM`, `DEP_DELAY`, `TAXI_OUT`, `TAXI_IN`, `ARR_DELAY`, `CRS_ELAPSED_TIME`, `ACTUAL_ELAPSED_TIME`, `AIR_TIME`, `FLIGHTS`, `O_TEMP`, `O_PRCP`, `O_WSPD`, `D_TEMP`, `D_PRCP`, `D_WSPD`, `O_LATITUDE`, `O_LONGITUDE`, `D_LATITUDE`, `D_LONGITUDE`): must satisfy `pa.types.is_float64(t)` (`double`). Physical `float32`, `int64`, `decimal`, or `string` types are strictly rejected.
   - **5 `LongType` columns** (`MONTH`, `DAY_OF_MONTH`, `DAY_OF_WEEK`, `ORIGIN_INDEX`, `DEST_INDEX`): must satisfy `pa.types.is_int64(t)` (`int64`). Physical `int32`, `int16`, `uint64`, `float64`, or `string` types are strictly rejected.
4. **Exact Nullability Match:** Every curated field must satisfy `bool(actual_field.nullable) == bool(expected_field.nullable)` (`True`).

---

## 3. Empirical Verification Matrix (`INT-06` on Real Parquet Files)

| Sub-Case | Parquet Schema Tested | Expected Result | Observed Result | Verdict |
| :--- | :--- | :--- | :--- | :--- |
| `INT-06.1` | Canonical 34-column schema (`10 string`, `19 float64`, `5 int64`, all `nullable=True`) | Accepted (`rows=1`) | Accepted (`rows=1`) | **PASS** |
| `INT-06.2` | Canonical 34-column schema with `large_string` (`large_utf8`) on `OP_CARRIER` & `FL_DATE` | Accepted (`rows=1`) | Accepted (`rows=1`) | **PASS** |
| `INT-06.3` | All 34 canonical column names with `pa.string()` on all 34 columns | Rejected (`FAILED_STAGING_CONTENT_INVALID`) | Raised `RuntimeError: FAILED_STAGING_CONTENT_INVALID: ... field #2 'OP_CARRIER_FL_NUM' physical type mismatch: expected DoubleType (Arrow float64/double), got Arrow type 'string'` | **PASS** |
| `INT-06.4a` | `MONTH` (`LongType`) stored as `pa.int32()` | Rejected (`FAILED_STAGING_CONTENT_INVALID`) | Rejected (`field #19 'MONTH' physical type mismatch`) | **PASS** |
| `INT-06.4b` | `ORIGIN_INDEX` (`LongType`) stored as `pa.float64()` | Rejected (`FAILED_STAGING_CONTENT_INVALID`) | Rejected (`field #22 'ORIGIN_INDEX' physical type mismatch`) | **PASS** |
| `INT-06.4c` | `DAY_OF_WEEK` (`LongType`) stored as `pa.string()` | Rejected (`FAILED_STAGING_CONTENT_INVALID`) | Rejected (`field #21 'DAY_OF_WEEK' physical type mismatch`) | **PASS** |
| `INT-06.4d` | `DEP_DELAY` (`DoubleType`) stored as `pa.float32()` | Rejected (`FAILED_STAGING_CONTENT_INVALID`) | Rejected (`field #7 'DEP_DELAY' physical type mismatch`) | **PASS** |
| `INT-06.4e` | `ARR_DELAY` (`DoubleType`) stored as `pa.int64()` | Rejected (`FAILED_STAGING_CONTENT_INVALID`) | Rejected (`field #14 'ARR_DELAY' physical type mismatch`) | **PASS** |
| `INT-06.4f` | `FLIGHTS` (`DoubleType`) stored as `pa.string()` | Rejected (`FAILED_STAGING_CONTENT_INVALID`) | Rejected (`field #18 'FLIGHTS' physical type mismatch`) | **PASS** |
| `INT-06.4g` | `OP_CARRIER` (`StringType`) stored as `pa.int64()` | Rejected (`FAILED_STAGING_CONTENT_INVALID`) | Rejected (`field #1 'OP_CARRIER' physical type mismatch`) | **PASS** |
| `INT-06.4h` | `ORIGIN` (`StringType`) stored as `pa.binary()` | Rejected (`FAILED_STAGING_CONTENT_INVALID`) | Rejected (`field #3 'ORIGIN' physical type mismatch`) | **PASS** |
| `INT-06.4i` | `FL_DATE` (temporal `StringType`) stored as `pa.date32()` | Rejected (`FAILED_STAGING_CONTENT_INVALID`) | Rejected (`field #0 'FL_DATE' physical type mismatch`) | **PASS** |
| `INT-06.4j` | `DEP_TIME` (HHMM `StringType`) stored as `pa.timestamp('us')` | Rejected (`FAILED_STAGING_CONTENT_INVALID`) | Rejected (`field #6 'DEP_TIME' physical type mismatch`) | **PASS** |
| `INT-06.5` | `MONTH` stored with `nullable=False` | Rejected (`FAILED_STAGING_CONTENT_INVALID`) | Rejected (`field #19 'MONTH' nullability mismatch: expected nullable=True, got nullable=False`) | **PASS** |
| `INT-06.6` | Coordinator fault injection at `INGESTION_COMPLETED` replacing staging Parquet with 34-column Parquet where `DEP_DELAY` is `pa.string()` | `TERMINAL_FAILURE`; publication blocked; `latest_run_id.txt` preserved at `run_type_good_01` | `final_state=TERMINAL_FAILURE`, `latest_run_id.txt == "run_type_good_01"` | **PASS** |
