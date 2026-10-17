# T007_FINAL_REMEDIATION_CLASSIFICATION_AND_FORENSIC_REVIEW — Classification Policy, Calendar Date Validation & Forensic Persistence Audit (`FIX-F03` & `FIX-F06`)

**Document ID:** `T007-FINAL-REMEDIATION-CLASSIFICATION-FORENSIC-20261017`  
**Task:** `MASTER-T007-FINAL-REMEDIATION` (`T-007` — Raw CSV Ingestion Pipeline)  
**Parent Gate:** `G4` (`PLANNED / NOT_COMPLETED`)  
**Date:** `2026-10-17`

---

## 1. Executive Summary

This report documents the remediation of **`FIX-F06` (Record Classification, Real Calendar Date Validation & Core Identity Anchors)** in [`src/flight_pipeline/ingestion/reader.py`](../../src/flight_pipeline/ingestion/reader.py) and **`FIX-F03` (Full Forensic Persistence of `QUARANTINED` and `REJECTED` Records)** in [`src/flight_pipeline/ingestion/coordinator.py`](../../src/flight_pipeline/ingestion/coordinator.py).

---

## 2. `FIX-F06` — Disjoint 3-State Classification & Real Calendar Date Policy

### 2.1 Strict Separation of `REJECTED`, `QUARANTINED`, and `ACCEPTED` (`DC-11` / `DC-12`)
`IngestionRecordClassifier.classify(df)` enforces mutually exclusive record states per `DATA_CONTRACT.md` (`DC-11`, `DC-12`), `T006_FINAL_CORRECTIONS_ADDENDUM.md` Section 2.1, and `G3-COND-A`:

| State (`_record_status`) | Trigger Condition | Primary `_anomaly_reason` | Curated Disposition |
|---|---|---|---|
| **`REJECTED`** | `_corrupt_record IS NOT NULL` (Univocity parser syntax failure: `<34` tokens, `>34` tokens, or unclosed quote) | `PARSER_SYNTAX_CORRUPTION` | Excluded from curated Parquet; persisted in `data/quarantine/<run_id>/rejected_*` |
| **`QUARANTINED`** | Syntax-valid row failing `FL_DATE` anchored regex or real calendar date parse (`2016-02-30`, `2019-02-29`) | `INVALID_FL_DATE_CORE_ANCHOR` | Excluded from curated Parquet; persisted in `data/quarantine/<run_id>/quarantined_*` |
| **`QUARANTINED`** | `year(parsed_fl_date) != _source_year` when `_source_year` is present | `SOURCE_YEAR_DATE_MISMATCH` | Excluded from curated Parquet; persisted in `data/quarantine/<run_id>/quarantined_*` |
| **`QUARANTINED`** | `OP_CARRIER` is null or blank | `MISSING_CARRIER_CORE_ANCHOR` | Excluded from curated Parquet; persisted in `data/quarantine/<run_id>/quarantined_*` |
| **`QUARANTINED`** | `ORIGIN` or `DEST` is null or blank | `MISSING_AIRPORT_CORE_ANCHOR` | Excluded from curated Parquet; persisted in `data/quarantine/<run_id>/quarantined_*` |
| **`QUARANTINED`** | `OP_CARRIER_FL_NUM` is null, blank, or non-numeric (`try_cast` is `NULL`/`NaN`/`Inf`) | `INVALID_FLIGHT_NUM_CORE_ANCHOR` | Excluded from curated Parquet; persisted in `data/quarantine/<run_id>/quarantined_*` |
| **`ACCEPTED`** | All core identity anchors valid | `NONE` | Promoted to curated Parquet (`34` columns) |

### 2.2 Real Calendar Date Validation (`FP-DEC-007` & `T006` Addendum Section 6.3)
- Previously, `FL_DATE` was checked only with a regex (`^\d{4}-\d{2}-\d{2}`), which allowed impossible calendar dates such as `2016-02-30` or non-leap `2019-02-29`.
- `IngestionRecordClassifier.classify()` now validates `FL_DATE` using:
  1. Anchored regex: `r"^(?:\d{4}-\d{2}-\d{2}|\d{4}-\d{2}-\d{2} 00:00:00)$"`
  2. Real calendar date parsing: `F.expr("try_cast(substring(trim(FL_DATE), 1, 10) AS date)") IS NOT NULL`
  3. Source-year consistency: `F.year(parsed_cal_date) == F.col("_source_year")`
- Verified behaviors:
  - `2016-02-29` (leap year) -> `ACCEPTED`
  - `2016-01-15 00:00:00` -> `ACCEPTED` and normalized to `"2016-01-15"` in `IngestionTransformer.to_curated()`, with `MONTH` and `DAY_OF_MONTH` derived via `F.coalesce(raw_month, F.month(parsed_cal_date))` when raw calendar fields are null.
  - `2016-02-30` and `2019-02-29` -> `QUARANTINED` (`INVALID_FL_DATE_CORE_ANCHOR`).

### 2.3 Preservation of `G3-COND-A`, `DC-12`, and `FP-DEC-017`
- **`G3-COND-A` (`OP_CARRIER_FL_NUM <= 0`):** Numeric flight numbers `<= 0` (e.g. `0.0`, `-5.0`) are **NOT** quarantined in `T-007`; they remain `ACCEPTED` and carry `_anomaly_flags = "PROVISIONAL_FLIGHT_NUM_NON_POSITIVE_G3_COND_A"` for `T-008` inspection.
- **`DC-12` (Metric vs Record Validity):** Non-numeric strings in any of the 7 CORE measures (`ARR_DELAY`, `DEP_DELAY`, `TAXI_OUT`, `TAXI_IN`, `AIR_TIME`, `ACTUAL_ELAPSED_TIME`, `CRS_ELAPSED_TIME`) remain `ACCEPTED`, carry `_anomaly_flags = "METRIC_NON_NUMERIC_RAW_TOKEN_DC12"`, and cast safely to `NULL` via `try_cast` in `IngestionTransformer.to_curated()`.
- **`FP-DEC-017` (Weather Optional):** Null or missing values in the 6 weather columns (`O_TEMP`, `O_PRCP`, `O_WSPD`, `D_TEMP`, `D_PRCP`, `D_WSPD`) never reject or quarantine a flight record.

---

## 3. `FIX-F03` — Forensic Persistence of `QUARANTINED` and `REJECTED` Records

### 3.1 Root-Cause Finding Closed
Previously, `IngestionCoordinator` only wrote aggregate counts in `anomaly_summary.json` and filtered out `QUARANTINED` and `REJECTED` records before writing curated Parquet, discarding the individual anomalous rows needed for `T-008` forensic inspection.

### 3.2 Forensic Storage Architecture (`persist_forensic_records`)
`persist_forensic_records(classified_df, run_id, quarantine_root, accounting)` in [`src/flight_pipeline/ingestion/coordinator.py`](../../src/flight_pipeline/ingestion/coordinator.py) writes all non-accepted records to `data/quarantine/<run_id>/` (strictly outside `data/staging/` and `data/curated/`):
- **Artifacts Written:**
  - `data/quarantine/<run_id>/quarantined_records.jsonl`
  - `data/quarantine/<run_id>/rejected_records.jsonl`
  - `data/quarantine/<run_id>/quarantined_parquet/part-*.parquet`
  - `data/quarantine/<run_id>/rejected_parquet/part-*.parquet`
  - `data/quarantine/<run_id>/forensic_manifest.json`
- **Columns Preserved per Forensic Record:**
  - `run_id`, `_source_year`, `_source_file`, `_record_lineage_id`
  - `_record_status` (`QUARANTINED` or `REJECTED`), `_anomaly_reason`, `_anomaly_flags`
  - `_corrupt_record` (raw unparsed line for syntax-corrupt rows)
  - All `34` canonical raw string columns (`FL_DATE` .. `D_LONGITUDE`) prior to numeric casting.
- **Fail-Closed Readback Verification:**
  - Independently reads back both the Parquet metadata and the JSONL line counts and verifies:
    - `persisted_quarantined_count == accounting.quarantined_row_count`
    - `persisted_rejected_count == accounting.rejected_row_count`
  - Raises `RuntimeError("FORENSIC_PERSISTENCE_FAILED: ...")` and aborts before publication if any count mismatches. Forensic directories are never deleted on failure.
