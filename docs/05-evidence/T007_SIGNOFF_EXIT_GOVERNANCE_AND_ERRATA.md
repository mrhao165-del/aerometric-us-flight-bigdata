# T007_SIGNOFF_EXIT — GOVERNANCE AND ERRATA RECONCILIATION

**Project:** US Flight Performance Analysis 2016–2024  
**Task:** `MASTER-T007-SIGNOFF-EXIT` (Section 5 Governance & Documentation Reconciliation)  
**Parent Gate:** `G4` (`PLANNED / NOT_COMPLETED`)  
**Audit Date:** 2026-10-17  

---

## 1. Purpose

This document provides the single authoritative governance and errata reconciliation for `T-007` prior to Human Signoff, resolving all documentary/terminology questions raised during independent review and aligning every `T-007` production module and test suite with `DATA_CONTRACT.md`, `DATA_DICTIONARY.md`, `DECISIONS.md`, `TEST_PLAN.md`, `G2_FINAL_CLOSEOUT_SIGN_OFF_PACKAGE.md`, and `G3_FINAL_SIGN_OFF_PACKAGE.md`.

---

## 2. Explicit Technical & Documentary Clarifications (Section 5.1)

### 2.1 Physical CSV Header Contract: Strictly 34 Columns (`FL_DATE` .. `D_LONGITUDE`)
- **Authoritative Rule (`DC-01` / `T007-01`):** Every raw annual CSV file (`flight_data_2016.csv` .. `flight_data_2024.csv`) has exactly **34 physical business columns** in canonical order (`0: FL_DATE` through `33: D_LONGITUDE`).
- **Correction of Legacy Reference:** Any historical mention of "21 or 22 columns" in early exploratory notes is superseded and invalid. `validate_physical_csv_header()` in `src/flight_pipeline/ingestion/reader.py` strictly enforces `CANONICAL_COLUMNS_COUNT == 34` and exact column ordering before Spark reads any file. The 35th field (`_corrupt_record`) exists only in `RAW_CSV_PARSER_SCHEMA` as Spark Univocity's `PERMISSIVE` parser side-channel and is forbidden in physical CSV headers (`RDR-12`).

### 2.2 Forbidden Column `DISTANCE` & Actual `_anomaly_flags` Contract
- **No `DISTANCE` Column in Schema:** Per `DC-02` and `src/flight_pipeline/ingestion/schema.py` (`FORBIDDEN_COLUMNS`), `DISTANCE`, `CANCELLED`, `DIVERTED`, `TAIL_NUM`, and cause-delay columns do **not** exist in the 34-column raw dataset or curated Parquet schema. No production code or active `T-007` documentation claims a `DISTANCE` column or a `DISTANCE <= 0` flag.
- **Exact `_anomaly_flags` Implementation in `src/flight_pipeline/ingestion/reader.py`:**
  - `_anomaly_flags` is a pipe-delimited (`|`) `StringType` technical column attached during `IngestionRecordClassifier.classify()` (persisted in forensic quarantine/rejected outputs and stripped before curated Parquet publication).
  - The exact implemented flag tokens are:
    1. `PARSER_SYNTAX_CORRUPTION` (malformed CSV syntax captured in `_corrupt_record` -> `REJECTED`).
    2. `INVALID_FL_DATE_CORE_ANCHOR` (missing/impossible calendar date -> `QUARANTINED`).
    3. `SOURCE_YEAR_DATE_MISMATCH` (`YEAR(FL_DATE) != _source_year` -> `QUARANTINED`).
    4. `MISSING_CARRIER_CORE_ANCHOR` (null/blank `OP_CARRIER` -> `QUARANTINED`).
    5. `MISSING_AIRPORT_CORE_ANCHOR` (null/blank `ORIGIN` or `DEST` -> `QUARANTINED`).
    6. `INVALID_FLIGHT_NUM_CORE_ANCHOR` (null/blank or non-numeric `OP_CARRIER_FL_NUM` -> `QUARANTINED`).
    7. `PROVISIONAL_FLIGHT_NUM_NON_POSITIVE_G3_COND_A` (`OP_CARRIER_FL_NUM <= 0` -> remains `ACCEPTED` per `G3-COND-A` with provisional flag for `T-008` audit).
    8. `METRIC_NON_NUMERIC_RAW_TOKEN_DC12` (non-empty, non-numeric raw string in a numeric measure column -> remains `ACCEPTED` per `DC-12`; measure casts to `NULL` in curated Parquet).

### 2.3 `_record_lineage_id`: Deterministic Content + Occurrence-Rank Hash (Not Physical Line Number)
- **Implementation (`attach_deterministic_lineage` in `src/flight_pipeline/ingestion/reader.py`):**
  - `_record_lineage_id` is **not** a physical file line number (`_source_row_number`). Spark distributed CSV partitions do not expose a partition-invariant physical line counter without single-threaded indexing.
  - Instead, `attach_deterministic_lineage` computes a 64-character SHA-256 content hash over `_source_year`, `_source_file`, all 34 raw column tokens (`<NULL>` sentinel for nulls), and `_corrupt_record`, then orders deterministically within identical-content groups to assign `dup_occurrence_rank = row_number() OVER (PARTITION BY _source_year, _source_file, _raw_content_sha256 ORDER BY _raw_content_sha256)` and hashes `(_source_year, _source_file, _raw_content_sha256, dup_occurrence_rank)` into `_record_lineage_id`.
  - Verified in `RDR-15` to produce 3 distinct, 100% identical SHA-256 lineage IDs across `repartition(1)` and `repartition(4)` on duplicate records.

### 2.4 `TS-020` Scope Split (`T-007` Synthetic Verification vs `G5/G6` Real CSV Verification)
- **Verified in `T-007` (`RDR-15` in `tests/test_t007_reader.py`):** Partition-independent duplicate disambiguation (`attach_deterministic_lineage`) is verified on synthetic 34-column fixtures modeling the exact duplicate key pattern (`2018-06-21, YX, 3624.0, DEN -> XNA` and `2022-05-05, YX, 3624.0`).
- **Deferred to `G5/G6` Real Data Execution:** Verification of the real duplicate record pair at physical lines `6,384,132` and `6,384,133` in `data/raw/flight_data_2018.csv` (`2018-06-21, YX, 3624, DEN -> XNA`) and full 9-year duplicate accounting (`54,727,629` rows) belongs to `G5` (Single-Year Smoke & Real Data Reconciliation) and `G6` (Full 9-Year Execution), because `T-007` is strictly authorized for synthetic Spark execution only (`0` real CSV rows read by Spark in `G4`).

### 2.5 `G3-COND-A` Provisional Record-Level Quarantine Policy
- **Status (`PROVISIONAL_PENDING_T008_AUDIT`):** The record-level quarantine rules in `IngestionRecordClassifier` (`INVALID_FL_DATE_CORE_ANCHOR`, `SOURCE_YEAR_DATE_MISMATCH`, `MISSING_CARRIER_CORE_ANCHOR`, `MISSING_AIRPORT_CORE_ANCHOR`, `INVALID_FLIGHT_NUM_CORE_ANCHOR`, while keeping `OP_CARRIER_FL_NUM <= 0` as `ACCEPTED` with `PROVISIONAL_FLIGHT_NUM_NON_POSITIVE_G3_COND_A`) remain governed by `G3-COND-A` and await empirical confirmation in `T-008` (`Data Quality Audit & Anomaly Quarantine`).

---

## 3. Preservation of Mandatory Project Governance Invariants (Section 5.2)

| Invariant ID | Canonical Status | Enforcement in `T-007` Code & Evidence |
| :--- | :--- | :--- |
| **`OR-05`** | `OPEN_QUALITY_DEFECT` | Year 2024 has partial temporal coverage (`335/366` days; March 2024 missing). Automatically emitted in `PipelineRunOutcome.governance_warnings` and `ExecutionReceipt.or05_coverage_warning` whenever `2024` is in `target_years`. |
| **`OR-08` / `TS-019`** | `IDENTITY_UNVERIFIED` (`METADATA_MATCH_ONLY`) | `UPSTREAM_IDENTITY_STATUS_UNVERIFIED = "IDENTITY_UNVERIFIED"`. Local SHA-256 verification proves local snapshot integrity only and never claims upstream BTS/DOT provenance. |
| **`G2-EXC-001`** | `OFFICIAL_MINUTES_EMPIRICALLY_CONSISTENT_PROVISIONAL` | Recorded as `core_units_status = "G2-EXC-001_PROVISIONAL"` in `RunManifest` and `ExecutionReceipt` pending `G5` `TS-018` empirical check. |
| **`FP-DEC-017`** | `CONDITIONAL_NO_GO` (Weather optional) | Null values in the 6 weather columns (`O_TEMP..D_WSPD`) never reject or quarantine flight records (`RDR-09`). |
| **Candidate Raw SHA-256 Manifest** | `CANDIDATE_PENDING_HUMAN_ACCEPTANCE` | `docs/05-evidence/T007_LOCAL_RAW_SHA256_CANDIDATE.json` remains unapproved until explicit Project Lead signoff; `SourceValidator` defaults to `approved_baseline_hashes=None` (`LOCAL_HASH_COMPUTED_UNAPPROVED`). |
