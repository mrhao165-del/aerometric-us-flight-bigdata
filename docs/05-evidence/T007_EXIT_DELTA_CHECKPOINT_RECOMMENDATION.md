# T007 EXIT DELTA - CHECKPOINT SCOPE & GOVERNANCE RECOMMENDATION

**Document ID:** `DOC-T007-EXIT-DELTA-05-CHECKPOINTS`  
**Task ID:** `T-007` (Raw CSV Ingestion Pipeline)  
**Gate:** `G4` (`PLANNED / NOT_COMPLETED`)  
**Design Authority:** Technical Project Manager & Governance Auditor  
**Binding Standards:** `ROADMAP.md`, `BACKLOG.md`, `AGENTS.md`  

---

## 1. DUAL-CHECKPOINT GOVERNANCE FRAMEWORK

To ensure maximum risk containment and prevent unauthorized scope escalation, the engineering pathway for Task T-007 is structured into two distinct, sequential governance checkpoints:

```
[Current Status: T-007 Design Complete & Empirical Proof Verified]
                                │
                                ▼
+─────────────────────────────────────────────────────────────────────────────+
| CHECKPOINT 1: Full Design Signoff (Project Lead Authority)                  |
| - Approves closure of design phase for Task T-007.                          |
| - Confirms resolution of all four blockers (CSV-01, CSV-02, CSV-03,         |
|   STORAGE-01) backed by reproducible empirical proof.                       |
| - DOES NOT authorize full pipeline implementation or data ingestion!        |
+─────────────────────────────────────────────────────────────────────────────+
                                │
                                ▼ (Optional Phased Authorization)
+─────────────────────────────────────────────────────────────────────────────+
| PROPOSED CHECKPOINT 1A: Isolated Schema Module Authorization (T007-01 ONLY) |
| - Allows implementation of ONLY the static Schema Module:                   |
|   `src/flight_pipeline/ingestion/schema.py`.                                |
| - Strictly isolated from file readers, storage writers, and datasets.       |
| - Governed by 9 measurable acceptance criteria.                             |
| - PROHIBITS reader, pipeline coordinator, locking, and real CSV ingestion!  |
+─────────────────────────────────────────────────────────────────────────────+
```

---

## 2. CHECKPOINT 1 — FULL DESIGN APPROVAL CONDITIONS

The Project Lead is recommended to grant **CHECKPOINT 1 DESIGN APPROVAL** upon verifying that the design meets the following four closure conditions:

1. **Empirical CSV Parser Verification (CSV-01):**
   - PySpark 4.0.1 parser behavior empirically proven by [`tools/qa/test_t007_spark_csv_reproduction.py`](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/tools/qa/test_t007_spark_csv_reproduction.py).
   - Catalyst column pruning risk eliminated via the Two-Action / Cache Materialization pattern.
   - StringType raw schema proven to protect DC-12 record-level acceptance against metric cast errors.
2. **Canonical Classification & Quarantine Alignment (CSV-02):**
   - Complete 11-situation decision matrix fully defined in [`T007_EXIT_DELTA_CLASSIFICATION_DECISION.md`](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/docs/05-evidence/T007_EXIT_DELTA_CLASSIFICATION_DECISION.md).
   - G3-COND-A preserved: non-positive flight numbers (`FL_NUM <= 0`) are tagged as anomalies, not hard-quarantined.
   - DC-11 mutual exclusivity and completeness mathematically proven.
3. **Robust Record Accounting & Fail-Closed Guardrails (CSV-03):**
   - Dual-accounting architecture (Physical Lines vs Logical Records) established in [`T007_EXIT_DELTA_RECORD_ACCOUNTING.md`](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/docs/05-evidence/T007_EXIT_DELTA_RECORD_ACCOUNTING.md).
   - Fail-closed behavior on accounting imbalance (`ACCOUNTING_UNVERIFIED`).
4. **Storage & Manifest Production Consistency (STORAGE-01):**
   - Lifecycle state machine fully aligned with live `SafePublisher` (`status="PUBLISHED"`) and `RunManifest`.
   - Manifest self-reference loop broken via external `_execution_receipt.json`.

---

## 3. PROPOSED CHECKPOINT 1A — SUBTASK T007-01 CRITERIA

If the Project Lead approves Checkpoint 1, the Lead may optionally authorize **Checkpoint 1A** to implement Subtask `T007-01` (Canonical Schema Module).

### 3.1. Strict Negative Scope Boundaries (What T007-01 Cannot Do)
Subtask `T007-01` is strictly restricted to defining data structures. It is **EXPLICITLY PROHIBITED** from:
- Writing or invoking CSV reader routines (`reader.py`).
- Writing classification or quarantine logic (`classifier.py`).
- Writing pipeline execution coordinators (`pipeline.py`).
- Writing file locking or publication coordinators (`locking.py`).
- Opening, reading, or processing any of the 9 raw CSV files (`data/raw/`).
- Generating Parquet outputs.

### 3.2. Nine Measurable Acceptance Criteria for T007-01
Implementation of `T007-01` shall be verified against:
1. **34 Canonical Columns:** Exactly 34 columns in exact canonical name and physical sequence matching `DATA_DICTIONARY.md`.
2. **Dual Schema Specialization:** Formally defines both `RAW_CSV_SCHEMA` (all business fields as `StringType` plus `_corrupt_record`) and `CURATED_PARQUET_SCHEMA` (strongly typed with strict nullable boundaries).
3. **No Fabricated Columns:** Zero fabricated `CANCELLED` or `DIVERTED` columns.
4. **Preservation of `FLIGHTS`:** Present in schema but marked with an explicit metadata constraint prohibiting its use as a KPI denominator weight.
5. **Exact Numeric Datatypes:** Integral columns typed as `IntegerType` / `LongType`; decimal delay/time measures typed as `DoubleType` (no truncation of decimals).
6. **No Unapproved Quality Policies:** Schema definitions contain no unapproved drop-null or filter side effects.
7. **Complete Unit Test Coverage:** 100% test pass on synthetic schema validation fixtures (`tests/test_t007_schema.py`).
8. **Isolated Synthetic Verification:** All unit tests run against mock/synthetic dictionaries in memory.
9. **Zero Raw Data Access:** Zero disk I/O against `data/raw/`.

---

## 4. FORMAL GOVERNANCE STATEMENT

> [!IMPORTANT]
> The Agent does **NOT** self-authorize Checkpoint 1 or Checkpoint 1A. Implementation of Subtask `T007-01` remains strictly **BLOCKED** until the Project Lead explicitly issues a signoff directive. Task `T-008` remains strictly `NOT_STARTED` and Gate `G4` remains `PLANNED / NOT_COMPLETED`.
