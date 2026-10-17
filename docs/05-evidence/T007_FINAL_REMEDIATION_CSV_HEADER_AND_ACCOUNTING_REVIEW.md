# T007_FINAL_REMEDIATION_CSV_HEADER_AND_ACCOUNTING_REVIEW — Physical Header Validation & Independent Logical Accounting Audit (`FIX-F01` & `FIX-F02`)

**Document ID:** `T007-FINAL-REMEDIATION-HEADER-ACCOUNTING-20261017`  
**Task:** `MASTER-T007-FINAL-REMEDIATION` (`T-007` — Raw CSV Ingestion Pipeline)  
**Parent Gate:** `G4` (`PLANNED / NOT_COMPLETED`)  
**Date:** `2026-10-17`

---

## 1. Executive Summary

This report documents the design, implementation, and verification of **`FIX-F01` (Physical CSV Header Validation)** and **`FIX-F02` (Independent `DC-11` Logical Record Accounting & Deterministic Lineage)** in [`src/flight_pipeline/ingestion/reader.py`](../../src/flight_pipeline/ingestion/reader.py) and [`src/flight_pipeline/ingestion/coordinator.py`](../../src/flight_pipeline/ingestion/coordinator.py).

---

## 2. `FIX-F01` — Physical CSV Header Validation (`validate_physical_csv_header`)

### 2.1 Root-Cause Finding Closed
Previously, `RawCsvReader.read_raw()` relied solely on PySpark's `.schema(get_raw_parser_schema())` with `header=True`. In PySpark's Univocity CSV reader, supplying an explicit `StructType` overrides physical header inspection—meaning a CSV file with missing, extra, reordered, duplicate, or unknown header column names could be ingested positionally without raising a header contract error.

### 2.2 Remediation Implementation
`validate_physical_csv_header(source_path, options)` in [`src/flight_pipeline/ingestion/reader.py`](../../src/flight_pipeline/ingestion/reader.py) executes as a mandatory preflight step before Spark opens the CSV:
1. **File Existence & Non-Empty Check:** Fails closed with `HeaderValidationError` if the file is missing, not a regular file, or `0` bytes.
2. **Binary Encoding & BOM Inspection:**
   - Rejects non-UTF-8 BOMs (`UTF-16 LE/BE`, `UTF-32 LE/BE`: `FF FE`, `FE FF`, `00 00 FE FF`, `FF FE 00 00`).
   - Rejects binary `NUL` (`\x00`) bytes in the header line.
   - Rejects `UTF-8 BOM` (`EF BB BF`) by default (`allow_utf8_bom=False`), stripping it only when `CsvReadOptions(allow_utf8_bom=True)` is explicitly configured.
   - Decodes the physical header line with strict UTF-8 (`UnicodeDecodeError` -> `HeaderValidationError`).
3. **Strict RFC-4180 Header Token Parsing:**
   - Parses the physical header line via Python's `csv.reader(..., strict=True)`.
   - Applies whitespace trimming consistent with `CsvReadOptions`.
4. **34-Column Canonical Contract vs 35-Field Parser Schema Boundary:**
   - Explicitly rejects any physical header containing the technical parser column `_corrupt_record` (`CORRUPT_RECORD_COLUMN`).
   - Rejects duplicate column names (`Duplicate column names in physical CSV header`).
   - Verifies exact column count == `34` (`CANONICAL_COLUMNS_COUNT`), reporting missing and unexpected columns on mismatch.
   - Verifies exact column name set and exact positional order against `CANONICAL_COLUMN_NAMES` (`FL_DATE` at index `0` through `D_LONGITUDE` at index `33`).

---

## 3. `FIX-F02` — Independent Logical Record Accounting & Deterministic Lineage

### 3.1 Root-Cause Finding Closed
Previously, `compute_row_accounting(classified_df)` derived `raw_row_count` by summing the classifier output (`accepted + quarantined + rejected`). That made `raw == accepted + quarantined + rejected` a tautology of the post-parse DataFrame rather than an independent verification against the raw source file.

### 3.2 Independent Source Scanner (`scan_csv_logical_records`)
`scan_csv_logical_records(source_path, options, source_year)` in [`src/flight_pipeline/ingestion/reader.py`](../../src/flight_pipeline/ingestion/reader.py) scans the raw CSV file in `1 MiB` streaming chunks (`O(1)` memory) independently of Spark and returns a `SourceScanResult` recording:
- `physical_lines_total`: Total physical newline-delimited lines including header.
- `header_lines_count`: `1` (validated physical header).
- `physical_data_lines`: Physical lines after the header.
- `logical_data_records`: Independently counted logical CSV data records.
- `blank_lines_count`: Count of blank/whitespace-only data lines.
- `embedded_newline_count`: Count of newlines inside balanced RFC-4180 quoted fields when `multi_line=True`.
- `unclosed_quote_count` and `has_unclosed_quote_eof`: Quote syntax anomalies.
- `is_verifiable` & `unverified_reason`:
  - If `blank_lines_count > 0`, Univocity silently skips blank lines during parsing, causing `spark_rows < logical_data_records`. `scan_csv_logical_records` sets `is_verifiable = False` (`ACCOUNTING_UNVERIFIED`).
  - If `multi_line=True` and `has_unclosed_quote_eof=True`, logical record boundaries are corrupted at EOF and `is_verifiable = False` (`ACCOUNTING_UNVERIFIED`).

### 3.3 Per-Year and Per-Run Reconciliation (`compute_row_accounting` & `compute_per_year_accounting`)
- `compute_row_accounting(classified_df, independent_raw_count, scan_result)` and `compute_per_year_accounting(classified_df, scan_results_by_year)` reconcile the independent `SourceScanResult.logical_data_records` against Spark's classified `accepted + quarantined + rejected` counts **both per `source_year` and in aggregate for `run_id`**.
- Any discrepancy raises `AccountingUnverifiedError("ACCOUNTING_UNVERIFIED: ...")`, immediately aborting ingestion before staging promotion or publication.

### 3.4 Deterministic Partition-Independent Lineage (`attach_deterministic_lineage`)
- `RawCsvReader.attach_deterministic_lineage(df, source_path, source_year)` attaches:
  - `_source_year` (`LongType`)
  - `_source_file` (`StringType` basename)
  - `_record_lineage_id` (`StringType` SHA-256 hex digest)
- Instead of relying on `monotonically_increasing_id()` or unstable Spark split offsets, `_record_lineage_id` hashes `(_source_year, _source_file, all 34 raw canonical column strings, _corrupt_record, within-identical-content occurrence rank)`, guaranteeing deterministic, partition-independent lineage IDs that disambiguate exact duplicate records such as the `2022` `YX 3624` pair (`TS-020`).
