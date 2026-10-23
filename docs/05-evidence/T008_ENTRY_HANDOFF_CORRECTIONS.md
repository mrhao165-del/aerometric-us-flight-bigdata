# T008 ENTRY HANDOFF CORRECTIONS & WORKING-TREE RECONCILIATION (DOC-02, DOC-03)

**Document ID:** `T008_ENTRY_HANDOFF_CORRECTIONS`  
**Parent Task:** `T-008 — Data Quality, Disjoint Row Accounting & Quarantine Engine`  
**Parent Gate:** `G4`  
**Classification:** `GOVERNANCE_AND_TECHNICAL_HANDOFF_ERRATA`  
**Date:** 2026-10-18  

---

## 1. PURPOSE & SCOPE

This document provides formal clarifications and handoff errata identified during entry audits for Task T-008, resolving:
- **`DOC-02`:** Working-tree consistency assertion count reconciliation.
- **`DOC-03`:** Manifest boundaries, hash registry separation, storage isolation, provisional quarantine policy constraints, and DataFrame typing contracts.

---

## 2. DOC-02: WORKING-TREE LOG COUNT RECONCILIATION

### 2.1. Phenomenon
The final signoff summary for T-007 referenced 999 assertions, while the raw log `T007_FINAL_SIGNOFF_LOG_QA_VERIFIERS.txt` captured:
```
Working-Tree PASS assertions: 997; FAIL: 0
```
at an intermediate snapshot prior to final deliverable registration.

### 2.2. Root Cause Analysis
The tool `tools/check_working_tree_consistency.py` verifies both static structural invariants (commit signatures, exclusion patterns, git status) and per-deliverable file existence and JSON validity for every entry in `docs/05-evidence/EVIDENCE_DELIVERABLE_REGISTER.json`.
- When 443 deliverables were registered: 997 total assertions were evaluated.
- When `T007_FINAL_SIGNOFF_LOG_QA_VERIFIERS.txt` itself was registered as the 444th deliverable: the checker evaluated 999 assertions (the additional file existence check and its cross-reference).
- Therefore, the assertion count variance was purely a function of the registration sequence. Both runs passed with zero failures (`FAIL: 0`).

### 2.3. T-008 Binding Rule
For Task T-008:
1. Historical log files are immutable and must not be retroactively edited.
2. All new deliverables produced in T-008 shall be systematically registered in `EVIDENCE_DELIVERABLE_REGISTER.json`.
3. The final verification log shall record the exact command, exit code, and exact assertion count reflecting the final deliverable registry.

---

## 3. DOC-03: CRITICAL TECHNICAL & GOVERNANCE HANDOFF CORRECTIONS

### 3.1. Manifest Boundary Separation
- **`docs/05-evidence/inputs/SOURCE_MANIFEST.json` Scope:** This manifest manages repository governance and evidence documents (e.g., G1 schema manifests, contracts, audit summaries). It is **NOT** a raw CSV data catalog or golden hash registry.
- **Candidate Raw Hash Isolation:** The calculated SHA-256 hashes for the 9 raw CSV files are stored exclusively in `docs/05-evidence/T007_LOCAL_RAW_SHA256_CANDIDATE.json` with status `CANDIDATE_PENDING_HUMAN_ACCEPTANCE`.
- **Prohibition:** Agents must **never** inject raw CSV hashes into `docs/05-evidence/inputs/SOURCE_MANIFEST.json` or alter the scope of existing manifests without explicit authority.

### 3.2. Spark Scratch & Storage Safety
- In local Windows environments, PySpark jobs create shuffle and scratch files.
- The scratch directory (`spark.local.dir` or `java.io.tmpdir`) must be located either outside the repository working tree or in designated temporary paths excluded by `.gitignore`.
- Under no circumstance shall Spark temporary files or unversioned test outputs pollute git working tree or be committed.

### 3.3. Provisional Policy Boundary (G3-COND-A)
- In accordance with `G3-COND-A`, the rule regarding `OP_CARRIER_FL_NUM <= 0` remains strictly **`PROVISIONAL`**.
- In the canonical pipeline, records with finite numeric non-positive flight numbers remain **`ACCEPTED`** (with an anomaly flag `PROVISIONAL_FLIGHT_NUM_NON_POSITIVE_G3_COND_A`).
- The T-008 Quality Engine must provide policy profiling, frequency analysis, and impact simulation tools, but **must NOT default to hard quarantine** for non-positive flight numbers.
- Any decision to enact a hard quarantine policy requires real BTS data validation at Gate G5 and formal human signoff.

### 3.4. DataFrame Typing & Pipeline Architecture
- DataFrames produced by `RawCsvReader.read_raw()` contain 34 canonical `StringType` columns plus technical `_corrupt_record` (and lineage columns).
- Downstream quality checks must evaluate both raw string representations (e.g., regex patterns, whitespace, empty tokens) and curated typed representations (`try_cast`).
- Strongly-typed representations are produced via `IngestionTransformer.to_curated()`, preserving `try_cast` semantics where non-numeric values become `NULL` without crashing or dropping valid records (DC-12).
- T-008 Quality Engine operates downstream of T-007 ingestion outputs and does not re-parse raw CSVs or create a redundant parallel reader.
