# T007 DESIGN IMPLEMENTATION DAG — WORKSTREAM BREAKDOWN, DEPENDENCIES & GATES

**Document ID:** `DOC-T007-DESIGN-07-IMPLEMENTATION-DAG`  
**Task ID:** `T-007` (Raw CSV Ingestion Pipeline)  
**Phase:** `DESIGN ONLY`  
**Gate:** `G4` (`PLANNED / NOT_COMPLETED`)  
**Design Authority:** Senior Big Data Architect & Technical Project Lead  
**Execution Strategy:** Phased Implementation: Synthetic Unit Testing $\to$ 1-Year Smoke Run $\to$ Full 9-Year Ingestion  

---

## 1. IMPLEMENTATION DIRECTED ACYCLIC GRAPH (DAG)

The implementation of Task T-007 is broken down into 6 strictly ordered subtasks (`T007-01` through `T007-06`) designed to prevent circular dependencies and minimize refactoring risk:

```
[Project Lead Design Approval (Checkpoint 1)]
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
  | Validator Module  |   | Single-Writer Lock |
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
[Checkpoint 2: Synthetic Tests PASS Review]
                     |
                     v
  +-------------------------------------+
  |  T007-07: 1-Year Smoke Verification |
  |  (Year 2016 Smoke Execution)        |
  +-------------------------------------+
                     |
                     v
[Checkpoint 3: Full 9-Year Run Approval]
```

---

## 2. DETAILED SUBTASK SPECIFICATIONS

### 2.1. Subtask T007-01: Canonical Schema Definition
- **Objective:** Create the canonical 34-column PySpark schema definitions (`CANONICAL_CSV_SCHEMA` and `CANONICAL_CURATED_SCHEMA`).
- **Target File:** `src/flight_pipeline/ingestion/schema.py`.
- **Dependencies:** None (foundation module).
- **Implementation Steps:**
  1. Define exact 34 `StructField` items matching `DATA_CONTRACT.md` and `T007_DESIGN_SOURCE_SCHEMA_MATRIX.md`.
  2. Implement schema validation utility to compare incoming CSV headers with expected canonical fields.
- **DoD:** Unit test confirms exact 34 column names and physical order.
- **Rollback:** Delete `src/flight_pipeline/ingestion/schema.py`.

### 2.2. Subtask T007-02: Source Validator Module
- **Objective:** Validate physical presence, file size, and streaming SHA-256 hash of raw CSV files.
- **Target File:** `src/flight_pipeline/ingestion/source_validator.py`.
- **Dependencies:** `T007-01`.
- **Implementation Steps:**
  1. Read inventory from `docs/05-evidence/inputs/SOURCE_MANIFEST.json`.
  2. Validate local file sizes and hashes against audited baseline.
  3. Log `OR-08` identity limitation (local SHA-256 does not verify BTS upstream origin).
- **DoD:** Source validator detects missing or truncated CSV files and raises `SourceValidationError`.
- **Rollback:** Delete `src/flight_pipeline/ingestion/source_validator.py`.

### 2.3. Subtask T007-03: CSV Reader & Classification Engine
- **Objective:** Read CSV batches, parse fields, classify rows (`ACCEPTED`, `QUARANTINED`, `REJECTED`), and sanitize data types.
- **Target File:** `src/flight_pipeline/ingestion/reader.py`.
- **Dependencies:** `T007-01`.
- **Implementation Steps:**
  1. Read CSV using `CANONICAL_CSV_SCHEMA` in `PERMISSIVE` mode.
  2. Execute date regex check: `^(?:\d{4}-\d{2}-\d{2}|\d{4}-\d{2}-\d{2} 00:00:00)$`.
  3. Execute core identity anchor checks (carrier, origin, dest).
  4. Enforce `G3-COND-A`: quarantine flight numbers $\le 0$ with `QUARANTINE_INVALID_FL_NUM`.
  5. Format times to 4-character zero-padded strings (`HHmm`).
  6. Compute row counts ($N_{\text{raw}}, N_{\text{acc}}, N_{\text{quar}}, N_{\text{rej}}$) and verify DC-11 conservation.
- **DoD:** Verified against fixtures `FIX-01` to `FIX-11` with 100% classification accuracy.
- **Rollback:** Delete `src/flight_pipeline/ingestion/reader.py`.

### 2.4. Subtask T007-04: Windows Single-Writer Concurrency Lock
- **Objective:** Provide robust, testable single-writer file locking with PID checking and stale lock recovery.
- **Target File:** `src/flight_pipeline/storage/locking.py`.
- **Dependencies:** None.
- **Implementation Steps:**
  1. Implement `PublisherLock` using atomic `os.open(..., O_CREAT | O_EXCL)`.
  2. Implement Windows PID liveness check (`OpenProcess`).
  3. Implement stale lock quarantine to `data/curated/stale_locks/`.
- **DoD:** Passes multi-process contention unit test (`FIX-12`) and stale lock recovery test (`FIX-13`).
- **Rollback:** Delete `src/flight_pipeline/storage/locking.py`.

### 2.5. Subtask T007-05: Ingestion Coordinator Pipeline
- **Objective:** Orchestrate the full ingestion lifecycle: validation, batch read, staging write, pre-publication check, and `SafePublisher` execution.
- **Target File:** `src/flight_pipeline/ingestion/pipeline.py`.
- **Dependencies:** `T007-01`, `T007-02`, `T007-03`, `T007-04`, `SafePublisher`, `RunManifest`.
- **Implementation Steps:**
  1. Initialize `run_id` and acquire `PublisherLock`.
  2. Process years sequentially (`2016` to `2024`).
  3. Write Parquet partitions to `data/staging/{run_id}/year={year}/`.
  4. Record `OR-05` coverage defect for Year 2024 in `RunManifest`.
  5. Verify Parquet magic bytes (`PAR1`) on all output parts.
  6. Call `SafePublisher.publish_run` to promote staging to curated and update pointer.
- **DoD:** Full synthetic pipeline run successfully promotes staging to curated and updates `latest_run_id.txt`.
- **Rollback:** Purge staging, remove incomplete runs from curated, delete `pipeline.py`.

### 2.6. Subtask T007-06: Synthetic Test Suite & Regression
- **Objective:** Implement comprehensive automated unit and integration tests covering all 14 fixtures.
- **Target File:** `tests/test_ingestion_pipeline.py`.
- **Dependencies:** `T007-01` through `T007-05`.
- **Implementation Steps:**
  1. Construct synthetic test fixtures in temporary directories.
  2. Test positive ingest, parse reject, quarantine anchors, invalid metrics, negative delays, and lock contention.
  3. Execute regression tests against existing suite.
- **DoD:** All tests pass with 0 failures, 0 errors.

---

## 3. PROJECT LEAD APPROVAL CHECKPOINTS

The implementation roadmap establishes three mandatory human checkpoints:

1. **Checkpoint 1 (Current Step):** Project Lead review and approval of the T-007 Architectural Design package.
2. **Checkpoint 2:** Project Lead review of synthetic unit test execution results (`T007-06`) prior to touching any real CSV data.
3. **Checkpoint 3:** Project Lead review of a 1-year smoke test (Year 2016) before authorizing the full 9-year 54.7M row ingestion run.

---

## 4. IMPLEMENTATION DAG VERDICT

The phased implementation DAG ensures safe, incremental development with zero regression risk to existing governance records.

**IMPLEMENTATION DAG VERDICT: APPROVED FOR READINESS REVIEW.**
