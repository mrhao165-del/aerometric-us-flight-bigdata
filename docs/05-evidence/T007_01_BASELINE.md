# T007-01 BASELINE & AUTHORIZATION AUDIT

**Document ID:** `DOC-T007-01-01-BASELINE`  
**Task ID:** `T007-01` (Canonical Schema Module)  
**Parent Gate:** `G4` (`PLANNED / NOT_COMPLETED`)  
**Authorization Reference:** Project Lead Explicit Checkpoint 1A Instruction (2026-10-17)  
**Execution Mode:** `STRICT LIMITED IMPLEMENTATION + SYNTHETIC TESTS ONLY`  
**Design Authority:** Senior PySpark Schema Engineer & Data Contract Auditor  

---

## 1. ENTRY VERIFICATION & AUTHORIZATION PROVENANCE

### 1.1. Project Lead Authorization
The human Project Lead explicitly authorized the commencement of Subtask `T007-01` (Checkpoint 1A) via direct prompt instruction.
- **Authorized Scope:**
  1. Creation of `src/flight_pipeline/ingestion/__init__.py`.
  2. Creation of `src/flight_pipeline/ingestion/schema.py`.
  3. Creation of unit test suite `tests/test_t007_schema.py`.
  4. Authoring required evidence deliverables and updating `EVIDENCE_DELIVERABLE_REGISTER.json`.
- **Explicit Non-Authorizations:**
  - Full Checkpoint 1 design signoff is **NOT** pre-approved.
  - Subtasks `T007-02` through `T007-07` remain strictly **NOT AUTHORIZED**.
  - Task `T-008` remains strictly **NOT_STARTED**.
  - Gate `G4` remains strictly **PLANNED / NOT_COMPLETED**.

### 1.2. Baseline Verification
- **Baseline Git HEAD:** [`98220d5c1532f84de0f6748388fa15d4dcee35c8`](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1)
- **Pre-execution Working Tree:** 100% clean (`git status --porcelain` empty).
- **Pre-execution Consistency:** 791 / 791 PASS assertions verified.

---

## 2. BINDING CANONICAL STANDARDS

Subtask `T007-01` strictly implements schemas governed by the authoritative repository contracts:
1. **`DATA_DICTIONARY.md`:** Authoritative source for exact 34 column names, physical ordering, and audited data types.
2. **`DATA_CONTRACT.md` (DC-11/12):** Mutual exclusivity of record states (`raw = accepted + quarantined + rejected`) and independence of record validity from metric validity.
3. **`DECISIONS.md`:**
   - `FP-DEC-007`: Strict preservation of raw date and local wall-clock time strings; prohibition of composite timestamp creation, date rollover deduction, or timezone invention.
   - `FP-DEC-010`: Prohibition of `sum(FLIGHTS)` as a KPI denominator weight; record count is canonical grain.
   - `FP-DEC-017`: Weather fields classified as `APPROVED_CONDITIONAL_NO_GO`, preserved as nullable double measures independent of CORE KPI pipeline.
4. **`G2-EXC-001`:** Physical units of 7 continuous CORE measures remain `OFFICIAL_MINUTES_EMPIRICALLY_CONSISTENT_PROVISIONAL`, subject to mandatory verification at Gate G5 (`TS-018`).
5. **`G3-COND-A`:** Safe boundary for `OP_CARRIER_FL_NUM <= 0` (provisional anomaly tag, not hard quarantine).

---

## 3. STRICT NEGATIVE BOUNDARIES

To ensure zero risk of accidental pipeline activation or dataset contamination, `T007-01` operates under strict architectural constraints:
- **NO CSV Reader Execution:** No calls to `spark.read.csv()` against real data.
- **NO Dataset Access:** Zero file handles opened against `data/raw/`.
- **NO File Locking Logic:** No concurrency or locking modules.
- **NO Storage Side Effects:** No Parquet datasets generated; zero writes to `curated/` or `staging/`.
- **NO Orchestration Logic:** No invocation of `SafePublisher` or `RunManifest` write workflows.
