# G6 Final Snapshot Validator Counterexample & Vulnerability Audit

**Document ID:** `DOC-G6-SNAP-COUNTER-001`  
**Security / Reliability Classification:** CRITICAL PRODUCTION SAFETY AUDIT  
**Task Reference:** TS-018 / G6 Operational Preflight Safety Correction  
**Evaluator:** Principal Big Data Architect & Independent Forensic QA Auditor  
**Date:** 2026-10-20  
**Status:** AUDITED & REMEDIATED (FAIL-CLOSED VERIFIED)  

---

## 1. Executive Summary & Audit Context

During the Independent Review of the G6 multi-year snapshot validation subsystem (`tools/qa/verify_multiyear_snapshot.py`), three structural vulnerabilities were uncovered in the draft implementation:
1. **S01 — False-PASS on Unverified / Fake Directory Contents:** The validator previously evaluated physical run presence using superficial checks (`physical_dir.is_dir()` and `any(p.is_file())`). It lacked schema and footer inspection for Parquet files, did not enforce the presence or contents of `run_manifest.json`, and was vulnerable to directory path traversal.
2. **S02 — Erroneous Row Accounting & Hardcoding Flaw:** The validator erroneously hardcoded `total_accepted == 54_674_003`. In any production ETL pipeline operating under Data Contract rules DC-11/12, raw row counts undergo quarantine and reject filtering ($raw = accepted + quarantined + rejected$). Enforcing $accepted = 54,674,003$ would illegitimately force quarantine and rejection to zero or falsely reject compliant runs where $accepted < raw$. Furthermore, non-integer types (booleans, floats, strings) and negative numbers were not rejected.
3. **S03 — Path Confinement & Traversal Vulnerability:** Snapshot registry entries referencing parent directories (`../outside`), absolute paths outside the data boundary, or reparse points were not strictly checked against the canonical root `<base_data_dir>/curated/runs/`.

This document records the exact counterexamples used to reproduce these vulnerabilities, demonstrates why each failed open in the prior implementation, and documents the fail-closed invariants that now guarantee zero false passes.

---

## 2. Forensic Reproduction of Counterexamples

### 2.1 Counterexample 1: Fake Parquet & Missing Manifest (Finding S01)
* **Vulnerability Description:** A directory containing a 0-byte file named `part-00000.parquet` or an arbitrary text file with a `.parquet` extension was accepted as a valid production run because only the file extension and directory existence were checked.
* **Failure Mode in Prior Implementation:**
  ```python
  # Old flawed check:
  if not physical_dir.exists() or not physical_dir.is_dir():
      ...
  parquet_files = list(physical_dir.glob("*.parquet"))
  if not parquet_files:  # Passed if ANY file with .parquet existed!
      ...
  ```
* **Reproduction Scenario:**
  1. Created run directory `curated/runs/run_fake_2016`.
  2. Created empty file `curated/runs/run_fake_2016/fake.parquet` (0 bytes, no Thrift metadata).
  3. Omitted `run_manifest.json`.
  4. Old validator output: `VALID` (False-PASS).
* **Remediation Invariant:**
  - Implemented `is_valid_parquet_file(p)` using `pyarrow.parquet.read_metadata(p)`.
  - Verifies Thrift footer metadata, `num_rows >= 0`, `num_columns >= 1`, and magic bytes (`PAR1`) without loading raw row vectors into RAM.
  - Mandates valid published `run_manifest.json` containing matching `run_id`, `year`, and `publication_status == "PUBLISHED"`.

### 2.2 Counterexample 2: Unbalanced Row Accounting & Hardcoded Accepted Constraint (Finding S02)
* **Vulnerability Description:** The prior specification hardcoded the assertion:
  $$\sum_{y=2016}^{2024} accepted_y == 54,674,003$$
  This violates Data Contract DC-11 and DC-12. The canonical BTS raw source contains 54,674,003 records. Under DC-11:
  $$raw = accepted + quarantined + rejected$$
  If even a single flight record is quarantined for data quality anomalies (e.g. negative elapsed time, invalid airport codes), $accepted < raw$. Hardcoding accepted rows to 54,674,003 caused a compliant production run with $quarantined > 0$ to fail, while failing to detect unbalanced row accounting within individual years.
* **Reproduction Scenario:**
  1. Configured 9 valid production runs where Year 2019 had:
     - $raw = 7,422,037$
     - $accepted = 7,420,000$
     - $quarantined = 2,000$
     - $rejected = 37$
     - $raw == accepted + quarantined + rejected$ (Balanced DC-11 accounting).
  2. Total raw across 9 years = 54,674,003; Total accepted = 54,671,966.
  3. Old validator output: `INVALID` (Rejected valid ETL run due to hardcoded accepted sum check).
  4. Conversely, if an entry had $raw = 100, accepted = 100, quarantined = 50, rejected = 10$ ($100 \neq 160$), old code did not check balance.
* **Remediation Invariant:**
  - Enforced per-year conservation: $raw == accepted + quarantined + rejected$.
  - Strictly validated data types: non-negative integers only (`isinstance(v, int) and not isinstance(v, bool) and v >= 0`).
  - Reconciled per-year raw row counts against `CANONICAL_SOURCE_ROW_COUNTS` ($\sum raw = 54,674,003$).
  - Dynamically aggregated accepted row counts without hardcoded equality constraints ($total\_accepted \le 54,674,003$).

### 2.3 Counterexample 3: Path Traversal & Run ID Mismatch (Finding S03)
* **Vulnerability Description:** Registry entries could define `run_dir: "../outside/run_2016"` or point to an absolute directory `/tmp/external_run`. Furthermore, a registry key could specify `"selected_run_id": "run_2016_v1"` while pointing to a directory named `curated/runs/run_2016_v2`.
* **Failure Mode in Prior Implementation:** Paths were resolved via `Path(run_dir).resolve()` without validating that the resolved path remained strictly inside `<base_data_dir>/curated/runs/`.
* **Reproduction Scenario:**
  1. Registry entry set `run_dir: "../outside/runs/run_2016"`.
  2. Old validator checked if `Path(run_dir).exists()`, allowing escape from the curated root.
* **Remediation Invariant:**
  - Resolved `runs_root = (base_data_dir / "curated" / "runs").resolve()`.
  - For each run path, evaluated:
    ```python
    try:
        resolved_dir.relative_to(runs_root)
    except ValueError:
        return SnapshotValidationResult(is_valid=False, status="PATH_TRAVERSAL_DETECTED")
    ```
  - Enforced that `resolved_dir.name == selected_run_id` and verified regex `^[a-zA-Z0-9_\-]+$`.
  - Prohibited duplicate physical directories across distinct years.

---

## 3. Comparative Invariant Matrix

| Security / Integrity Dimension | Prior Validator Behavior | Hardened Production Validator Behavior |
| :--- | :--- | :--- |
| **Directory Confinement** | Unchecked traversal allowed | Strict containment inside `<base_dir>/curated/runs/` |
| **Directory Identity** | Folder name unverified against run_id | Strict equality: `dir.name == selected_run_id` |
| **Directory Content** | Allowed 0-byte or non-parquet files | Requires $\ge 1$ genuine `.parquet` files with Thrift headers |
| **Parquet Integrity** | Extension check only (`*.parquet`) | `pyarrow.parquet.read_metadata()` checks Thrift footer, rows, cols |
| **Manifest Requirement** | Optional or uninspected | Mandatory `run_manifest.json` matching run_id, year, published status |
| **Manifest File Integrity** | Not checked against disk | File size and SHA-256 verified against physical disk files |
| **Accounting Conservation** | Hardcoded `sum(accepted) == 54674003` | Balanced $raw == accepted + quarantined + rejected$ per year |
| **Row Type Safety** | Weak Python typing (accepted bool/str) | Strict integer validation (`int`, non-bool, $\ge 0$) |
| **Annual Raw Inventory** | Missing or partial | Strict match against 9 canonical annual BTS figures ($\sum = 54,674,003$) |
| **Year 2024 Scope (OR-05)** | Not checked | Mandatory `source_coverage_status == 'PARTIAL'` |

---

## 4. Conclusion & Audit Signoff

The hardened implementation in `tools/qa/verify_multiyear_snapshot.py` completely eliminates the failure-open risks exposed in findings S01, S02, and S03. The validator now functions as a strictly fail-closed gate keeper, guaranteeing that any multi-year snapshot accepted for downstream analytical consumption satisfies every structural, mathematical, and cryptographic invariant required by Gate G6.
