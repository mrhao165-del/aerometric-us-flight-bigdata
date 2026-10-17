# T007_SIGNOFF_EXIT — CSV LOGICAL RECORD VERIFICATION (`BLOCKER-01`)

**Project:** US Flight Performance Analysis 2016–2024  
**Task:** `MASTER-T007-SIGNOFF-EXIT` (`BLOCKER-01` Closure)  
**Target Module:** `src/flight_pipeline/ingestion/reader.py` (`44,077` bytes, SHA-256 `2f3df94170d954d9fde299590cc1b7d4928cf24737b794f159c5fbf101a88067`)  
**Target Test Suite:** `tests/test_t007_reader.py` (`RDR-08`, `RDR-14`, `RDR-16`, `RDR-17`)  

---

## 1. Root Cause Analysis of Pre-Fix `BLOCKER-01`

1. In commit `0434fe527da1bda5cf7830273921093876692364`, `scan_csv_logical_records(csv_path, options=CsvReadOptions(multi_line=False))` branched into a line-by-line loop when `not opts.multi_line`, incrementing `logical_data_records += 1` for every physical line after the header without tracking RFC-4180 quote state across line breaks.
2. Consequently, on a 34-column CSV with 1 header line and 2 RFC-4180 logical records where 1 field contained a quoted embedded newline (`"AMERICAN\nAIRLINES"`):
   - Python `csv.reader`: `2` logical data records.
   - Pre-fix `scan_csv_logical_records(multi_line=True)`: `2` logical data records, `3` physical data lines.
   - Pre-fix `scan_csv_logical_records(multi_line=False)`: `3` logical data records, `3` physical data lines, `embedded_newline_count=0`, `is_verifiable=True`.
   - Because Spark's CSV reader with `multiLine=False` also split the 2 logical records into 3 physical rows (`1 ACCEPTED + 2 REJECTED`), pre-fix `compute_row_accounting` compared `3 == 3` and falsely reported `is_balanced() == True` instead of raising `AccountingUnverifiedError` (`ACCOUNTING_UNVERIFIED`).
3. Furthermore, `compute_row_accounting(classified_df)` previously contained a fallback `raw_total = ... else classifier_total` when called without `scan_result` or `independent_raw_count`, violating `DC-11` independent source accounting.

---

## 2. Production Fix Implemented in `src/flight_pipeline/ingestion/reader.py`

1. **Unified Physical + RFC-4180 Logical Record Scanner (`scan_csv_logical_records`):**
   - Regardless of `opts.multi_line`, `scan_csv_logical_records` now executes a single streaming byte/character state machine that simultaneously measures:
     - `physical_lines_total` and `physical_data_lines` (physical line breaks `\n`, `\r\n`, `\r`, plus trailing line without newline at EOF).
     - `logical_data_records` (RFC-4180 quote-aware logical record count).
     - `embedded_newline_count` (line breaks occurring while `in_quotes == True` on lines that do not have an unescaped quote mismatch).
     - `unclosed_quote_count` and `has_unclosed_quote_eof`.
     - `blank_lines_count`.
2. **Fail-Closed Contract Enforcement When `multi_line=False`:**
   - When `opts.multi_line` is `False` (default contract mode) and the source CSV contains quoted embedded newlines (`embedded_newline_count > 0` or `physical_data_lines != logical_data_records` without unclosed quote syntax errors), `scan_csv_logical_records` returns:
     - `logical_data_records = 2` (true RFC-4180 logical record count, never `3`),
     - `physical_data_lines = 3`,
     - `embedded_newline_count = 1`,
     - `is_verifiable = False`,
     - `unverified_reason = "ACCOUNTING_UNVERIFIED: Source CSV '...' contains 1 embedded newline(s) inside quoted fields (logical_data_records=2 != physical_data_lines=3), which cannot be parsed safely with multiLine=False"`.
   - `RawCsvReader.read_raw(..., enforce_record_boundaries=True)` (used by `IngestionCoordinator.run_ingestion`) immediately raises `AccountingUnverifiedError` before classification or publication.
   - Even if `read_raw` is invoked with `enforce_record_boundaries=False`, `compute_row_accounting` checks `scan_result.is_verifiable` and `scan_result.logical_data_records != classifier_total` (`2 != 3`) and raises `AccountingUnverifiedError`.
3. **Elimination of Tautological Accounting Fallback:**
   - `compute_row_accounting` no longer falls back to `classifier_total`. Calling `compute_row_accounting(classified_df)` without `scan_result`, `source_path`, or `independent_raw_count` immediately raises `AccountingUnverifiedError("ACCOUNTING_UNVERIFIED: Independent source record count (scan_result, source_path, or independent_raw_count) is required...")`.

---

## 3. Empirical Verification Matrix (Python `csv.reader` vs `scan_csv_logical_records` vs Real Spark 4.0.1)

| Test ID | Synthetic 34-Column Fixture Scenario | `csv.reader` Data Records | `scan_csv_logical_records` (`logical` / `physical` / `verifiable`) | Spark 4.0.1 Parser Output & Accounting Result | Verdict |
| :--- | :--- | ---: | :--- | :--- | :--- |
| `RDR-16` (Case 1) | 2 logical records, record #2 has `"AMERICAN\nAIRLINES"`, `multi_line=False` | `2` | `logical=2`, `physical=3`, `embedded_nl=1`, `verifiable=False` | `read_raw(enforce_record_boundaries=True)` & `compute_row_accounting` both raise `AccountingUnverifiedError` (`2 != 3` blocked fail-closed) | **PASS** |
| `RDR-16` (Case 2) | Same 2-record embedded-newline fixture, `multi_line=True` | `2` | `logical=2`, `physical=3`, `embedded_nl=1`, `verifiable=True` | Spark parses `2` records (`2 ACCEPTED`); `raw=2 == accepted=2` balanced | **PASS** |
| `RDR-16` (Case 3) | `compute_row_accounting(classified_df)` called without independent count | N/A | N/A | Raises `AccountingUnverifiedError` (`ACCOUNTING_UNVERIFIED`) | **PASS** |
| `RDR-17` (Case 1) | 2 logical records, record #2 has escaped quotes `"DELTA ""AIR"" LINES"` | `2` | `logical=2`, `physical=2`, `verifiable=True` | Spark parses `2` records (`2 ACCEPTED`), curated `OP_CARRIER == 'DELTA "AIR" LINES'` | **PASS** |
| `RDR-17` (Case 2) | 2 logical records, EOF without trailing newline | `2` | `logical=2`, `physical=2`, `verifiable=True` | Spark parses `2` records (`2 ACCEPTED`); `raw=2 == accepted=2` balanced | **PASS** |
| `RDR-14` (Case 1) | Unclosed quote in single-line mode (`multi_line=False`) | N/A (malformed) | `logical=2`, `physical=2`, `unclosed_quote=1`, `verifiable=True` | Spark captures malformed line in `_corrupt_record` (`1 ACCEPTED + 1 REJECTED = 2`) | **PASS** |
| `RDR-14` (Case 2) | Unclosed quote reaching EOF in `multi_line=True` mode | N/A (malformed) | `has_unclosed_quote_eof=True`, `verifiable=False` | Raises `AccountingUnverifiedError` (`ACCOUNTING_UNVERIFIED`) | **PASS** |
| `RDR-14` (Case 3) | Blank line between data records | `2` non-empty | `blank_lines_count=1`, `verifiable=False` | Raises `AccountingUnverifiedError` (`ACCOUNTING_UNVERIFIED`) | **PASS** |
