# T011-R2 Source Change & Risk Assessment Report

**Project:** US Flight Performance Analysis 2016–2024  
**Task:** T-011 R2 — Targeted Parity Hardening and Evidence Correction  
**Parent Gate:** G5 — IN_PROGRESS  
**Date:** 2026-10-19  
**Review Scope:** T011-R1 Auditor Findings Remediation (R2-F01..F05)  
**Status:** COMPLETE / READY FOR HUMAN AUDIT  

---

## 1. Executive Summary

This report documents all source code modifications, test suite expansions, risk evaluations, and invariant verifications executed under **T011-R2**.

In accordance with `AGENTS.md`, `PROJECT_STATE.md`, and the **MASTER PROMPT — T011-R2**, all technical corrections were targeted directly at the 5 findings raised by the independent auditor on T011-R1. No accepted architecture from G2–G4 was redesigned, no raw data in `data/raw/` was modified (0 bytes altered), Gate G6 remains strictly `NOT_STARTED / BLOCKED`, and Task T-011 is submitted for human technical signoff under status `READY_FOR_HUMAN_TECHNICAL_REVIEW (T011_R2_TECHNICAL_CORRECTIONS_COMPLETE_TS018_PENDING)`.

---

## 2. Inventory of Source Code Modifications

### 2.1 `src/flight_pipeline/kpi/bts_reconciler.py`
- **Component:** BTS TranStats Reconciler & Provenance Guard
- **Remediations Applied:**
  1. **Cryptographic Provenance Guard (`BtsProvenanceMetadata`, `BtsProvenanceValidator`):** Implemented strict fail-closed metadata validation. A caller boolean `is_authentic_bts_data=True` alone CANNOT grant authentic parity without a verified `BtsProvenanceMetadata` object signed with `project_lead_approval_status = "APPROVED_BY_PROJECT_LEAD"` and `is_external_reference = True`.
  2. **Formal 5 Governance States:** Explicitly separated and recorded:
     - `file_present`: candidate CSV exists on disk.
     - `schema_valid`: all 7 CORE measures mapped without missing columns.
     - `source_provenance_verified`: external provenance approved by Project Lead.
     - `numerical_parity_verified`: mathematical agreement within tolerance.
     - `human_accepted`: official Project Lead signoff.
  3. **Hardened Composite Key Parsing (`extract_composite_key`):**
     - Replaced falsy `or` syntax with explicit `is not None` lookup, preserving flight number `0` and `0.0` as valid under `G3-COND-A`.
     - Added strict ISO date pattern validation (`YYYY-MM-DD`), preventing empty or malformed dates from matching.
     - Added strict string formatting for carrier, origin, destination.
     - Returns 6-tuple `(fl_date, carrier, fl_num, origin, dest, is_valid)`.
  4. **Immediate Invalid Key Isolation:** Records with `not is_valid` are isolated immediately during indexing, recorded in `invalid_key_records`, marked as `KeyMatchStatus.INVALID_KEY`, and excluded from matching.
  5. **Schema Missing Column Detection:** Added `MismatchType.SCHEMA_MISSING_COLUMN`. If any of the 7 measures is absent from the input record dictionary, it is flagged as a missing column rather than silently coalesced into `NULL_NULL_AGREEMENT`.
  6. **7-Measure Completeness Requirement:** Enforced that all 7 CORE measures must have `numeric_sample_count > 0` for official parity eligibility.

### 2.2 `tools/qa/run_ts018_bts_parity.py`
- **Component:** TS-018 QA Verification Harness
- **Remediations Applied:**
  1. Added `load_companion_provenance()` looking for companion metadata (`{file}.provenance.json` or `BTS_PROVENANCE_MANIFEST.json`).
  2. When executed on the local synthetic sample `data/raw/bts_transtats_sample.csv`, it discovers no external Project Lead approval manifest, logs `PROVENANCE_UNVERIFIED`, and sets `provenance_meta = None, is_authentic_bts_data = False`.
  3. Outputs verdict `SYNTHETIC_RECONCILER_VERIFIED_AUTHENTIC_BTS_PENDING` (Exit 0 for QA test passing, while preventing false authentic parity claim).

### 2.3 `tests/test_t011_fault_injection.py`
- **Component:** TS-013 Fault Injection Test Suite
- **Remediations Applied:**
  1. **F01 Realism:** Rewrote `test_f01_source_read_failure` to invoke `RawCsvReader.read_raw()`, verifying that missing inputs raise `HeaderValidationError` without touching staging or publisher pointer.
  2. **F02b Write-Time Failure:** Added `test_f02b_staging_writer_runtime_failure` demonstrating that mid-stream IO/disk full failure during staging partition generation triggers two-phase `.tmp` cleanup and blocks publication.
  3. **F08 Governed Recovery:** Rewrote `test_f08_recovery_and_reconciliation_after_failure` to assert `LockContentionError("FAIL_CLOSED — MANUAL_RECOVERY_REQUIRED")` on dead PID, verify that `break_stale_lock(force=False)` is rejected, and execute the official operator recovery protocol via `break_stale_lock(force=True)`.

### 2.4 `tests/test_t011_ts018_bts_parity.py`
- **Component:** TS-018 Unit Test Suite
- **Remediations Applied:**
  1. Expanded test count from 8 to 15 tests.
  2. Added test coverage for: missing columns on one side (`test_10`), all measures null failing numeric completeness (`test_11`), scale mismatch (`test_12`), sign inversion (`test_13`), provenance gating (`test_14`), and blank/invalid date failing closed (`test_15`).

### 2.5 `tests/test_t011_r2_counterexamples.py`
- **Component:** T011-R2 Regression Guard Suite (NEW)
- **Remediations Applied:**
  1. Implemented 5 permanent regression guards testing the exact failure modes identified in findings R2-F01..F05, verifying that all 5 fail closed post-remediation.

---

## 3. Risk Assessment & Invariant Tracking

| Invariant / Risk | Target Gate / Task | Governance Status in T011-R2 |
| :--- | :---: | :--- |
| **`G2-EXC-001` (Provisional Units)** | G5 / TS-018 | **ACTIVE & PROVISIONAL.** 7 CORE measures verified on synthetic golden fixture; authentic external BTS parity remains `PENDING_EXTERNAL_BTS_SOURCE_DELIVERY`. |
| **Gate G6 Hard Blocker** | G6 / T-012 | **STRICTLY BLOCKED.** G6 full ETL processing is permanently blocked until TS-018 authentic BTS parity is signed off by Project Lead. |
| **`OR-05` (March 2024 Missing, 335/366 days)** | G6 / T-012 | **PRESERVED.** Handled via cohort detection; `source_coverage_status = PARTIAL` override maintained in KPI engine. |
| **`OR-08` (Raw Source Identity Unverified)** | G2 / G5 | **PRESERVED.** SHA-256 local baseline recorded; external upstream identity remains unverified. |
| **`FP-DEC-017` (Weather CONDITIONAL_NO_GO)** | G2–G7 | **PRESERVED.** 6 weather columns remain in schema as nullable; no weather KPIs computed; no flights quarantined for null weather. |
| **Raw Data Immutability (`data/raw/`)** | Repository-wide | **VERIFIED.** Pre/post byte count, file timestamps, and hashes 100% identical. 0 bytes altered. |
| **Windows NTFS Safety (`G3-COND-C`)** | Publication | **VERIFIED.** Atomic copy + pointer update + non-destructive rollback tested under TS-013. |

---

## 4. Conclusion

All source code changes in T011-R2 are targeted, minimal, fully tested, and zero-regression. All open project risks and governance blockers are strictly enforced.
