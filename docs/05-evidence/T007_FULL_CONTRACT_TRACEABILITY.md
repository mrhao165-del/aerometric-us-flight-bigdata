# T007_FULL_CONTRACT_TRACEABILITY — Requirements & Governance Traceability Matrix

**Document ID:** `T007-FULL-TRACEABILITY-20261017`  
**Task:** `T-007` — Raw CSV Ingestion Pipeline  
**Parent Gate:** `G4` (`PLANNED / NOT_COMPLETED`)  
**Date:** `2026-10-17`

---

## 1. Data Contract (`DATA_CONTRACT.md`) & Decision (`DECISIONS.md`) Traceability

| Contract / Decision ID | Rule Summary | Implementation Location | Verification Test(s) | Status |
|---|---|---|---|---|
| **DC-01 / DC-02** | 34 canonical columns (`2016..2024`), exact order & casing; header validation | `schema.py` (`CANONICAL_COLUMNS`), `reader.py` (`validate_header`) | `test_t007_schema.py`, `test_reader_09_header_validation_fails_closed` | VERIFIED |
| **DC-03 / DC-04** | Primary business key (`FL_DATE`, `OP_UNIQUE_CARRIER`, `OP_CARRIER_FL_NUM`, `ORIGIN`, `DEST`, `CRS_DEP_TIME`); missing/invalid key -> `QUARANTINED` | `reader.py` (`IngestionRecordClassifier.classify`) | `test_reader_02_missing_required_keys_quarantined`, `test_reader_03_unparseable_fl_date_quarantined` | VERIFIED |
| **DC-05 / FP-DEC-007** | Temporal integrity: derive `year`, `month`, `day_of_month`, `day_of_week` (`1=Mon..7=Sun`) strictly from `FL_DATE`. Never add `+24h` to arrival time or infer arrival date from `CRS_ARR_TIME`. | `reader.py` (`IngestionTransformer.to_curated`, lines 302–336) | `test_reader_06_overnight_flight_no_plus_24h_mutation` | VERIFIED |
| **DC-06 / FP-DEC-010** | Normalize `OP_CARRIER_FL_NUM` trailing `.0` (`"1234.0"` -> `"1234"`) while preserving alphanumeric identifiers | `reader.py` (`_normalize_flight_num_expr`, line 258) | `test_reader_07_flight_num_decimal_zero_normalization` | VERIFIED |
| **DC-11** | Row accounting invariant: `source_rows_total == accepted_rows + quarantined_rows + rejected_rows`; mutually exclusive statuses | `reader.py` (`compute_row_accounting`), `manifest.py` (`RowAccounting.validate_invariant`) | `test_reader_01`, `test_reader_08`, `test_int_01_multi_year_end_to_end_publish_and_accounting` | VERIFIED |
| **DC-12** | Malformed numeric metrics (`DEP_DELAY="bad_num"`) on valid-key rows do NOT quarantine the row; row is `ACCEPTED` and metric is cast to `NULL` via `try_cast`. No generic `coverage_rate`. | `reader.py` (`IngestionRecordClassifier.classify`, `IngestionTransformer.to_curated`) | `test_reader_05_malformed_numeric_metric_accepted_with_null_cast` | VERIFIED |
| **G2-EXC-001** | 7 CORE delay/time measures carry provisional minute units (`PROVISIONAL_MINUTES_PENDING_G5`) pending G5 `TS-018` verification | `schema.py` (`CORE_PROVISIONAL_MINUTE_MEASURES`), `coordinator.py` (`ExecutionReceipt`) | `test_t007_schema.py`, `test_int_01` | VERIFIED |
| **FP-DEC-017** | 15 Weather columns are `CONDITIONAL_NO_GO` and optional for CORE; retained as nullable `DoubleType` without blocking CORE | `schema.py` (`WEATHER_MEASURE_COLUMNS`), `coordinator.py` (`ExecutionReceipt`) | `test_t007_schema.py`, `test_int_01` | VERIFIED |
| **OR-05** | Year 2024 partial coverage (`335/366` days; March 2024 missing) tracked as `OPEN_QUALITY_DEFECT` | `source_validator.py` (`AUDITED_SOURCE_INVENTORY[2024]`), `coordinator.py` (`governance_warnings`) | `test_t007_source_validator.py`, `test_int_01` | VERIFIED |
| **OR-08 / G3-COND-A** | Raw CSV upstream identity is `IDENTITY_UNVERIFIED`; local SHA-256 proves snapshot consistency only | `source_validator.py` (`UPSTREAM_IDENTITY_STATUS_UNVERIFIED`), `coordinator.py` (`ExecutionReceipt`) | `test_t007_source_validator.py`, `test_int_01`, `test_int_02` | VERIFIED |
| **G3-COND-B** | 7-step Windows NTFS atomic publish & pointer switching (`CURRENT_PUBLISHED_RUN.json`) | `publisher.py` (`SafePublisher`), `coordinator.py` (`IngestionCoordinator`) | `test_t009_storage_publisher.py`, `test_int_01`, `test_neg_05`, `test_neg_06` | VERIFIED |
| **G3-COND-C** | Single-writer lock (`data/locks/ingestion_writer.lock`) with stale PID detection & forensic preservation | `locking.py` (`SingleWriterLock`, `is_pid_alive`) | `test_t007_locking.py`, `test_neg_04_duplicate_run_id_and_lock_contention` | VERIFIED |
