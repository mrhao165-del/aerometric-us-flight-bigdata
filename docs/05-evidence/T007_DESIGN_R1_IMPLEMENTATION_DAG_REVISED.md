# T007 DESIGN R1 IMPLEMENTATION DAG REVISED — SUBTASK SPECIFICATIONS & HUMAN CHECKPOINTS

**Document ID:** `DOC-T007-DESIGN-R1-08-IMPLEMENTATION-DAG`  
**Task ID:** `T-007` (Raw CSV Ingestion Pipeline)  
**Phase:** `DESIGN REMEDIATION (R1)`  
**Gate:** `G4` (`PLANNED / NOT_COMPLETED`)  
**Design Authority:** Technical Project Manager & Lead Data Engineer  
**Execution Strategy:** Bounded Phased Implementation: Synthetic Testing $\to$ 1-Year Smoke Run $\to$ Full 9-Year Ingestion  

---

## 1. REVISED IMPLEMENTATION DAG & HUMAN APPROVAL GATES

The implementation of Task T-007 is structured into 7 distinct, sequential subtasks (`T007-01` through `T007-07`) governed by three mandatory Human Project Lead approval checkpoints:

```
[Project Lead Design Approval (CHECKPOINT 1)]
                     |
                     v
  +-------------------------------------+
  |  T007-01: Canonical Schema Module   |
  |  src/flight_pipeline/ingestion/     |
  |  schema.py                          |
  +-------------------------------------+
                     |
         +-----------+-----------+
         |                       |
         v                       v
  +-------------------+   +--------------------+
  | T007-02: Source   |   | T007-04: Windows   |
  | Inventory & Hash  |   | Single-Writer Lock |
  +-------------------+   +--------------------+
         |                       |
         v                       |
  +-------------------+          |
  | T007-03: Reader & |          |
  | Classification    |          |
  +-------------------+          |
         |                       |
         +-----------+-----------+
                     |
                     v
  +-------------------------------------+
  |  T007-05: Ingestion Coordinator     |
  |  src/flight_pipeline/ingestion/     |
  |  pipeline.py                        |
  +-------------------------------------+
                     |
                     v
  +-------------------------------------+
  |  T007-06: Synthetic Test Suite      |
  |  tests/test_ingestion_pipeline.py   |
  +-------------------------------------+
                     |
                     v
[Project Lead Synthetic Test Approval (CHECKPOINT 2)]
                     |
                     v
  +-------------------------------------+
  |  T007-07: 1-Year Smoke Verification |
  |  (Year 2016 Bounded Real Run)       |
  +-------------------------------------+
                     |
                     v
[Project Lead Full-Run Authorization (CHECKPOINT 3)]
```

---

## 2. DETAILED SUBTASK SPECIFICATIONS

### 2.1. Subtask T007-01: Canonical Schema & Type Casting Module
- **Objective:** Implement `CANONICAL_CSV_SCHEMA` (raw read) and `CANONICAL_CURATED_SCHEMA` (curated write) with safe numeric casting.
- **Files to Create:** `src/flight_pipeline/ingestion/schema.py`.
- **Dependencies:** None.
- **Inputs:** `DATA_CONTRACT.md`, `T007_DESIGN_R1_SOURCE_SCHEMA_CORRECTIONS.md`.
- **Key Implementation Steps:**
  1. Define exact 34 `StructField` items for raw read and curated write.
  2. Implement safe cast helper for `OP_CARRIER_FL_NUM` (float literal `x.0` to integer `x`, flagging fractional decimals).
  3. Implement header and order comparator to detect drift before Spark read.
- **Required Tests:** `TS-001`, `TS-002`.
- **DoD:** Unit tests verify exact 34 column names and physical order on both schemas.
- **Stop Condition:** Any discrepancy in column count or type mapping.
- **Rollback:** Delete `src/flight_pipeline/ingestion/schema.py`.

### 2.2. Subtask T007-02: Source Inventory & Local Hash Verifier
- **Objective:** Validate physical presence of 9 annual CSVs, verify file sizes/mtimes, compute local streaming SHA-256 hashes, and record in Ingestion Manifest.
- **Files to Create:** `src/flight_pipeline/ingestion/source_validator.py`.
- **Dependencies:** `T007-01`.
- **Inputs:** `docs/05-evidence/inputs/data_inventory.md`, raw CSV filesystem paths.
- **Key Implementation Steps:**
  1. Inspect 9 CSV paths: `data/raw/tabular/{year}/flight_with_weather_{year}.csv`.
  2. Verify byte sizes match audited inventory.
  3. Compute streaming SHA-256 (64KB chunks) for local reproducibility (`TS-019`).
  4. Flag `OR-08 = IDENTITY_UNVERIFIED` for upstream BTS origin.
- **Required Tests:** `TS-019`.
- **DoD:** Validator verifies all 9 files, computes hashes, and detects truncated files.
- **Stop Condition:** Missing CSV file or size mismatch against `data_inventory.md`.
- **Rollback:** Delete `src/flight_pipeline/ingestion/source_validator.py`.

### 2.3. Subtask T007-03: CSV Reader & Classification Engine
- **Objective:** Read CSV batches, enforce DC-11 row partition conservation, classify rows (`ACCEPTED`, `QUARANTINED`, `REJECTED`), and sanitize data types.
- **Files to Create:** `src/flight_pipeline/ingestion/reader.py`.
- **Dependencies:** `T007-01`.
- **Inputs:** Raw CSV DataFrames, `DATA_CONTRACT.md` DC-11/12, `G3-COND-A`.
- **Key Implementation Steps:**
  1. Read CSV using `CANONICAL_CSV_SCHEMA` with explicit corrupt record projection to prevent Catalyst column pruning.
  2. Route unparseable lines to `REJECTED`.
  3. Validate core anchors: `FL_DATE` regex `^(?:\d{4}-\d{2}-\d{2}|\d{4}-\d{2}-\d{2} 00:00:00)$`, non-null carrier, non-null airport. Unmatched $\to$ `QUARANTINED`.
  4. Handle `OP_CARRIER_FL_NUM`: flag non-positive values per `G3-COND-A` without hard quarantine.
  5. Format valid times to 4-character strings without date rollover (`FP-DEC-007`).
  6. Compute row counts ($N_{\text{raw}}, N_{\text{acc}}, N_{\text{quar}}, N_{\text{rej}}$) and assert DC-11 balance.
- **Required Tests:** `TS-002`, `TS-003`, `TS-009`, `TS-017`.
- **DoD:** Evaluated against fixtures `FIX-01` to `FIX-11` with 100% classification accuracy.
- **Stop Condition:** `accounting.is_balanced() == False` triggers fail-closed `ACCOUNTING_UNVERIFIED`.
- **Rollback:** Delete `src/flight_pipeline/ingestion/reader.py`.

### 2.4. Subtask T007-04: Windows Single-Writer Concurrency Lock
- **Objective:** Implement fail-closed `PublisherLock` with process creation token, PID liveness check, and non-destructive forensic quarantine.
- **Files to Create:** `src/flight_pipeline/storage/locking.py`.
- **Dependencies:** None.
- **Key Implementation Steps:**
  1. Atomic creation via `os.open(..., O_CREAT | O_EXCL)`.
  2. Record metadata payload: PID, hostname, `process_create_time_utc`, `auth_token`.
  3. Fail-closed: Never steal lock unless owner is definitively proven dead.
  4. Context manager pattern with verified token release in `__exit__`.
- **Required Tests:** `OPR-02` (Contention & fail-closed tests).
- **DoD:** Unit tests verify contention blocking (`FIX-12`) and owner token release.
- **Stop Condition:** Active lock detected during execution.
- **Rollback:** Delete `src/flight_pipeline/storage/locking.py`.

### 2.5. Subtask T007-05: Ingestion Pipeline Coordinator & SafePublisher Adapter
- **Objective:** Orchestrate the complete ingestion lifecycle, manage annual staging, and invoke `SafePublisher.publish()`.
- **Files to Create:** `src/flight_pipeline/ingestion/pipeline.py`.
- **Dependencies:** `T007-01` through `T007-04`, `SafePublisher`, `RunManifest`.
- **Key Implementation Steps:**
  1. Acquire `PublisherLock` under `run_id`.
  2. Process annual batches sequentially into `data/staging/{run_id}/curated/year={year}/*.parquet`.
  3. Archive quarantine and rejected records to `data/staging/{run_id}/evidence/`.
  4. Record `OR-05` defect for Year 2024 in `RunManifest`.
  5. Validate Parquet magic bytes (`PAR1`) on all output parts.
  6. Call `SafePublisher.publish(run_id, staging_dir, accounting)` to promote curated data.
- **Required Tests:** `TS-001`, `TS-003`, `TS-019`, `OPR-04`.
- **DoD:** End-to-end synthetic run promotes data, verifies hashes, and updates pointer.
- **Stop Condition:** Any exception during staging write or publication.
- **Rollback:** Preserve staging as forensic artifact; delete `pipeline.py`.

### 2.6. Subtask T007-06: Synthetic Test Suite & Regression
- **Objective:** Implement comprehensive automated unit and component tests covering all 14 fixtures and publication scenarios.
- **Files to Create:** `tests/test_ingestion_pipeline.py`.
- **Dependencies:** `T007-01` through `T007-05`.
- **DoD:** 100% PASS across all 14 fixtures (`FIX-01`..`14`) and publication scenarios (`PUB-01`..`05`).
- **Stop Condition:** Any test failure or assertion error.
- **Rollback:** Fix defect or revert test modifications.

### 2.7. Subtask T007-07: 1-Year Smoke Verification Execution
- **Objective:** Execute bounded smoke run on Year 2016 raw CSV (5,617,659 rows) to verify real-world throughput, memory bounds (< 4GB driver), and NTFS promotion.
- **Dependencies:** Successful completion of Checkpoint 2.
- **DoD:** Smoke run completes, generates valid RunManifest, and satisfies DC-11 row balance.
- **Stop Condition:** Out of memory, parser exception, or accounting mismatch.
- **Rollback:** Rollback pointer to previous; isolate staging.

---

## 3. HUMAN APPROVAL CHECKPOINTS

1. **Checkpoint 1 (Current Milestone):** Project Lead review and approval of the T-007 Design Remediation R1 package. Unlocks implementation of `T007-01` through `T007-06`.
2. **Checkpoint 2:** Project Lead review of synthetic unit test execution results (`T007-06`) prior to touching any real CSV data. Unlocks `T007-07` (1-Year Smoke Run).
3. **Checkpoint 3:** Project Lead review of 1-Year Smoke Run results (Year 2016) before authorizing full 9-year 54.7M rows execution.

---

## 4. REVISED IMPLEMENTATION DAG VERDICT

The 7-subtask DAG with 3 human checkpoints provides safe, verified, and phased progression with zero risk of premature execution.

**REVISED DAG VERDICT: APPROVED FOR IMPLEMENTATION PLANNING.**
