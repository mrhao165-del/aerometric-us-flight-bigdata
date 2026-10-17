# T007-02 ENTRY PREPARATION & READ-ONLY SOURCE AUDIT HANDOFF

**Document ID:** `DOC-T007-02-ENTRY-PREPARATION`  
**Task ID:** `T007-02` (Source Inventory & Local Hash Verifier)  
**Parent Gate:** `G4` (`PLANNED / NOT_COMPLETED`)  
**Status:** **`READ-ONLY PREPARATION — SUBTASK LOCKED PENDING AUTHORIZATION`**  
**Author:** Senior Big Data Architect & Storage Safety Auditor  
**Date:** 2026-10-17  

---

## 1. Executive Summary & Entry Prerequisites

This document establishes the technical, architectural, and governance specifications for **Subtask `T007-02` (Source Inventory & Local Hash Verifier)** prior to any code implementation or raw data access.

### 1.1. Governance Prerequisites Checklist
- [x] **Gate G2:** Formally signed off (`PASS`) under [`G2_OFFICIAL_SIGNOFF_HUMAN_ACCEPTANCE_RECORD.md`](G2_OFFICIAL_SIGNOFF_HUMAN_ACCEPTANCE_RECORD.md).
- [x] **Gate G3:** Formally signed off (`PASS`) under [`G3_OFFICIAL_SIGNOFF_HUMAN_ACCEPTANCE_RECORD.md`](G3_OFFICIAL_SIGNOFF_HUMAN_ACCEPTANCE_RECORD.md).
- [x] **Task T-006:** Completed (`PASS / COMPLETED`) with PySpark architectural specifications approved.
- [x] **Task T-009:** Completed (`PASS / COMPLETED` controlled) under [`T009_HUMAN_SIGNOFF_20261017.md`](T009_HUMAN_SIGNOFF_20261017.md).
- [x] **Subtask T007-01:** Formally signed off (`PASS / COMPLETED` controlled) under [`T007_01_HUMAN_SIGNOFF_20261017.md`](T007_01_HUMAN_SIGNOFF_20261017.md).
- [ ] **Subtask T007-02 Authorization:** **LOCKED**. Awaits explicit instruction and authorization from the Human Project Lead.
- [ ] **Gate G4 Status:** Strictly **`PLANNED / NOT_COMPLETED`**.

---

## 2. Audited Raw CSV Inventory Baseline

The pipeline ingests data across the 2016–2024 retrospective period from exactly nine (9) annual CSV files stored in `data/raw/tabular/`:

| Year | Canonical Relative Path | Audited Row Count | Audited Byte Size | Audited Column Count |
| :---: | :--- | :---: | :---: | :---: |
| **2016** | `data/raw/tabular/2016/flight_with_weather_2016.csv` | 5,617,658 | 1,563,303,803 | 34 |
| **2017** | `data/raw/tabular/2017/flight_with_weather_2017.csv` | 5,674,621 | 1,577,414,136 | 34 |
| **2018** | `data/raw/tabular/2018/flight_with_weather_2018.csv` | 7,213,446 | 2,005,622,763 | 34 |
| **2019** | `data/raw/tabular/2019/flight_with_weather_2019.csv` | 7,422,037 | 2,060,544,985 | 34 |
| **2020** | `data/raw/tabular/2020/flight_with_weather_2020.csv` | 4,688,354 | 1,303,942,668 | 34 |
| **2021** | `data/raw/tabular/2021/flight_with_weather_2021.csv` | 5,992,543 | 1,666,039,833 | 34 |
| **2022** | `data/raw/tabular/2022/flight_with_weather_2022.csv` | 6,703,047 | 1,863,280,094 | 34 |
| **2023** | `data/raw/tabular/2023/flight_with_weather_2023.csv` | 6,787,093 | 1,885,823,248 | 34 |
| **2024** | `data/raw/tabular/2024/flight_with_weather_2024.csv` | 4,575,204 | 1,270,394,643 | 34 |
| **TOTAL** | **9 Files** | **54,674,003** | **15,196,366,173** | **34** |

*Note: The metadata above is derived from the G1 audit baseline (`docs/05-evidence/inputs/data_inventory.md` and 9 `schema_YYYY.json` files). It reflects the audited snapshot and must not be altered.*

---

## 3. Local Hash Verification Strategy & Governance Invariants

### 3.1. Role of `SOURCE_MANIFEST.json` vs. Raw CSV Hashes
- **Critical Clarification:** The thirteen (13) `SOURCE_MANIFEST.json` files in the repository tree govern the integrity of repository documentation, inputs, and audit fixtures under `docs/05-evidence/inputs/`. They do **NOT** contain or manage golden SHA-256 hashes for the 15.2 GB raw CSV tabular files.
- Modifying `SOURCE_MANIFEST.json` to inject raw CSV hashes is strictly forbidden and would break repository consistency checks (`tools/check_working_tree_consistency.py`).

### 3.2. Bootstrapping Local Content Hashes (`TS-019` & `OR-08`)
- Under `FP-DEC-014`, file size and modification timestamps (`size/mtime`) do not prove raw content identity or detect silent bit-rot.
- Under `OR-08` (`IDENTITY_UNVERIFIED` / `METADATA_MATCH_ONLY`), computing the local SHA-256 of the 9 CSV files establishes the **immutable baseline of the locally audited snapshot**.
- **Non-Negotiable Governance Invariant:** Computing local SHA-256 does **NOT** prove that the CSV files originated authentically from upstream BTS TranStats servers or that NOAA weather data was joined properly upstream. The status of raw data origin remains strictly `IDENTITY_UNVERIFIED`. Local hashes serve exclusively to detect local modification, corruption, or environmental drift across pipeline executions.

### 3.3. Memory-Safe Streaming Architecture
- To prevent Out-Of-Memory (OOM) failures or memory pressure on local execution environments, file hashing must be performed using a streaming block-by-block reader:
  - Buffer size: 64 KB (`65,536` bytes) or 1 MB (`1,048,576` bytes).
  - Python memory overhead: strictly $O(1)$ memory consumption ($< 2$ MB RAM) regardless of file size (even for the 2.06 GB 2019 CSV).
  - Algorithm: Standard NIST `hashlib.sha256()`.

---

## 4. Subtask T007-02 Module Specifications (`source_validator.py`)

When authorized by the Project Lead, the implementation of `T007-02` will adhere to the following contract:

### 4.1. Functional Responsibilities
1. **File Inventory Verification:** Verify that all 9 annual CSV files exist at their expected relative paths.
2. **Size Verification:** Check that the physical file size on disk matches the audited baseline (exact byte count).
3. **Local Hash Computation & Verification (`TS-019`):** Compute streaming SHA-256 hashes, compare against previously recorded local snapshot baseline, and record them into the pipeline execution manifest (`RunManifest.add_input()`).
4. **Fail-Closed Policy:** Any anomaly must trigger an immediate, non-ignorable exception halting pipeline execution:
   - File missing $\implies$ raise `FileNotFoundError` (exit code $\neq 0$).
   - Byte size mismatch $\implies$ raise `SourceIntegrityError` (exit code $\neq 0$).
   - Hash mismatch $\implies$ raise `SourceIntegrityError` (exit code $\neq 0$).
   - Read permission denied $\implies$ raise `PermissionError` (exit code $\neq 0$).

### 4.2. Testing Boundaries & Synthetic Isolation
- All automated unit tests for `T007-02` (`tests/test_t007_source_validator.py`) must execute exclusively on **small synthetic dummy CSV files** created in isolated temporary directories (`tempfile.TemporaryDirectory`).
- Unit tests must **NEVER** read, hash, or touch the 15.2 GB real dataset in `data/raw/tabular/`.
- Full-scale hashing of the 15.2 GB dataset is reserved for the smoke/pipeline execution phase under explicit human authorization.

---

## 5. Required Project Lead Authorizations for T007-02 Execution

Before Subtask `T007-02` can proceed from `LOCKED` to `IN_PROGRESS`, the following authorizations are required:
1. **Authorization to Implement Module:** Permission to author `src/flight_pipeline/ingestion/source_validator.py` and `tests/test_t007_source_validator.py`.
2. **Authorization for Read-Only Raw Access:** Permission to grant the Python process read-only streaming access to `data/raw/tabular/` to perform the one-time baseline SHA-256 calculation.
3. **Approval of Local Baseline Snapshot Manifest:** Acceptance of the generated local SHA-256 inventory as the frozen reference for `TS-019`.

---

## 6. Strict Prohibitions (Preserved Invariants)

- **DO NOT** author `source_validator.py` at this time.
- **DO NOT** execute SHA-256 calculation on the 15.2 GB real dataset at this time.
- **DO NOT** modify `SOURCE_MANIFEST.json` or `data/raw/` in any way.
- **DO NOT** unlock `T007-02` or mark it as started until explicit instruction is issued.
- **DO NOT** mark Task `T-007` overall or Gate `G4` as complete.
