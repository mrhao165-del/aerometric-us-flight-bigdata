# T007 DESIGN EXIT CHECKPOINT SCOPE — GOVERNANCE BOUNDARIES & T007-01 ACCEPTANCE CRITERIA

**Document ID:** `DOC-T007-DESIGN-EXIT-05-CHECKPOINTS`  
**Task ID:** `T-007` (Raw CSV Ingestion Pipeline)  
**Phase:** `DESIGN RECONCILIATION (R1-EXIT)`  
**Gate:** `G4` (`PLANNED / NOT_COMPLETED`)  
**Design Authority:** Technical Project Manager & Governance Engineer  
**Binding Standards:** `ROADMAP.md`, `BACKLOG.md`, `AGENTS.md`  

---

## 1. GOVERNANCE BOUNDARY & CHECKPOINT DELINEATION

To eliminate ambiguity regarding engineering authorization, this document formally separates the **Design Closure Milestone** from the **Phased Implementation Authorizations**:

```
[CURRENT STEP: T007 Design Review Package Submitted]
                     |
                     v
+---------------------------------------------------------------------------------------------------+
| CHECKPOINT 1: Design Phase Signoff (Project Lead Approval)                                        |
|   - Formally reviews and approves T007 Design Review (R1-EXIT).                                    |
|   - Confirms that design blockers (G3-COND-A, SafePublisher API, DC-11 accounting) are closed.     |
|   - DOES NOT automatically authorize bulk implementation of all subtasks!                         |
+---------------------------------------------------------------------------------------------------+
                                                  |
                                                  v
+---------------------------------------------------------------------------------------------------+
| PROPOSED CHECKPOINT 1A: Authorization of Subtask T007-01 ONLY                                     |
|   - Strictly bounded authorization to implement ONLY the Canonical Schema Module.                 |
|   - Target: src/flight_pipeline/ingestion/schema.py.                                              |
|   - Explicitly PROHIBITS: reader, pipeline, locking, or touching real CSV datasets.               |
+---------------------------------------------------------------------------------------------------+
                                                  |
                                                  v
+---------------------------------------------------------------------------------------------------+
| CHECKPOINT 2: Synthetic Verification Review (Project Lead Approval)                               |
|   - Evaluates synthetic test suite execution results (T007-06).                                    |
|   - Confirms all 14 fixtures (FIX-01..14) and 5 publication fixtures (PUB-01..05) PASS.            |
|   - Authorizes execution of 1-Year Smoke Verification (T007-07) on Year 2016 CSV.                 |
+---------------------------------------------------------------------------------------------------+
                                                  |
                                                  v
+---------------------------------------------------------------------------------------------------+
| CHECKPOINT 3: Smoke Test Review & Full-Run Authorization (Project Lead Approval)                  |
|   - Evaluates 1-Year Smoke Run results, RunManifest, and DC-11 row accounting on real data.        |
|   - Confirms memory ceiling (< 4GB driver), partition throughput, and publication pointer.        |
|   - Formally authorizes full 9-year 54.7M rows ingestion execution.                               |
+---------------------------------------------------------------------------------------------------+
```

---

## 2. SUBTASK T007-01 MEASURABLE ACCEPTANCE CRITERIA

When authorized under **Checkpoint 1A**, Subtask **`T007-01`** (*Canonical Schema Module*) must satisfy exactly 9 measurable acceptance criteria before any downstream subtask may begin:

1. **Exact 34 Canonical Columns:** Must define all 34 canonical column names in the exact physical order audited across all 9 annual CSV files (2016–2024).
2. **Layer Schema Separation:** Must cleanly distinguish between the raw CSV parsing schema (`CANONICAL_CSV_SCHEMA` in Bronze) and the curated Parquet storage schema (`CANONICAL_CURATED_SCHEMA` in Silver).
3. **`FLIGHTS` Constant Preservation:** Must define `FLIGHTS` as `DoubleType` (strictly constant 1.0) and enforce the contract rule that `sum(FLIGHTS)` is forbidden as a KPI denominator (`FP-DEC-010`).
4. **Zero Fabricated Columns:** Must not contain `CANCELLED`, `DIVERTED`, `DISTANCE`, or delay breakdown categories.
5. **Strict Nullable Semantics:** Must mark calendar fields (`MONTH`, `DAY_OF_MONTH`, `DAY_OF_WEEK`, `ORIGIN_INDEX`, `DEST_INDEX`) and time fields as nullable, matching `DATA_DICTIONARY.md`.
6. **Safe Numeric Casting:** Must implement float-to-integer casting that converts `x.0` to `x` without silently dropping fractional decimals (e.g. `1234.5` must raise an anomaly flag, not truncate to `1234`).
7. **No Extraneous Policies:** Must not introduce unauthorized quality, quarantine, or filtering policies.
8. **Synthetic Unit Test Verification:** Must achieve 100% `PASS` on isolated synthetic schema tests verifying column names, types, order, and casting rules.
9. **Zero Real Data Mutation:** Must not open, read, or process the 54,674,003 raw CSV rows.

---

## 3. CHECKPOINT SCOPE VERDICT

The checkpoint governance framework provides unambiguous, phased authorization gates, preventing unauthorized scope expansion while defining strict, measurable acceptance criteria for Subtask `T007-01`.

**CHECKPOINT SCOPE VERDICT: FULLY GOVERNED & READY FOR HUMAN REVIEW.**
