# T011-R3 Source Change & Risk Report

**Project:** US Flight Performance Analysis 2016–2024  
**Task:** T-011 R3 — Provenance Trust Boundary, Numeric Integrity, Lock Recovery & Evidence Correction  
**Parent Gate:** G5 — IN_PROGRESS  
**Component:** Source Audit & Risk Register  
**Date:** 2026-10-19  
**Status:** COMPLETE / ZERO-REGRESSION ASSESSED  

---

## 1. Executive Summary

This report documents all source code modifications executed during the **T-011 R3** remediation cycle. All edits were strictly targeted to resolve findings R3-F01 through R3-F06 without redesigning the accepted G2–G4 architecture, altering raw ingestion contracts, or compromising repository governance.

---

## 2. Inventory of Source Changes

### 2.1 Production Pipeline Modules

#### 1. `src/flight_pipeline/kpi/bts_reconciler.py`
- **Rationale:** Eliminate hash overwrite vulnerabilities, prevent malformed numerics from masking as null agreement, enforce Gregorian calendar validation, enforce the complete matching predicate, and strictly separate candidate parity from official human signoff.
- **Specific Changes:**
  - Added `NumericParseStatus` enum (`VALID_FINITE_NUMBER`, `TRUE_NULL`, `MALFORMED_NUMBER`, `NONFINITE_NUMBER`, `SCHEMA_MISSING`).
  - Added `APPROVED_NULL_STRINGS = {"", "na", "null", "none", "nan_rep_none"}`.
  - Added `MismatchType.MALFORMED_NUMERIC_ERROR`.
  - Implemented `parse_numeric_measure()` to classify parse states and reject non-finites / malformed strings.
  - Hardened `compare_single_field()` so `NULL_NULL_AGREEMENT` requires both sides to be `TRUE_NULL`. Malformed strings produce `MALFORMED_NUMERIC_ERROR`.
  - Hardened `extract_composite_key()` using `datetime.date(year, month, day)` to reject impossible Gregorian calendar dates (e.g. Feb 31, leap day in non-leap year).
  - Enforced complete matching predicate in `reconcile()`: `numerical_parity_verified` requires 0 unmatched records, 0 ambiguous keys, 0 invalid keys, 0 field mismatches, and positive numeric samples across all 7 measures.
  - Implemented `TS018_CANDIDATE_PARITY_VERIFIED_HUMAN_APPROVAL_PENDING` verdict when format and parity pass.
  - Hardcoded `summary.human_accepted = False` for all automated execution.

#### 2. `src/flight_pipeline/storage/locking.py`
- **Rationale:** Prevent unconditional deletion of unparseable, empty, or unknown-owner lock files during recovery.
- **Specific Changes:**
  - Updated `break_stale_lock(force=True)` to inspect lock file content and verify required schema fields (`run_id`, `pid`, `host`).
  - If lock file is 0 bytes, empty, malformed, or missing required fields, it raises `LockContentionError` with `FAIL_CLOSED — MANUAL_RECOVERY_REQUIRED` and refuses to delete the file.
  - Added pre-unlink token re-verification to eliminate check-then-unlink race conditions.

### 2.2 QA Harness Modules

#### 3. `tools/qa/run_ts018_bts_parity.py`
- **Rationale:** Eliminate self-attestation hash overwrite and pass independent cryptographic hashes.
- **Specific Changes:**
  - Removed `prov_meta.sha256_hash = bts_sha256` statement.
  - Passed `actual_bts_sha256` directly to `reconciler.reconcile()`.
  - Updated exit code handling to recognize `TS018_CANDIDATE_PARITY_VERIFIED_HUMAN_APPROVAL_PENDING` as a valid candidate state while logging that official signoff is pending.

### 2.3 Test Suite Modules

#### 4. `tests/test_t011_ts018_bts_parity.py`
- Updated mock provenance hashes to valid 64-character hex strings (`"a" * 64`).
- Updated Test 14C to assert candidate approval pending verdict and `human_accepted=False`.
- Updated test assertions for all-null and unmatched records to align with hardened fail-closed verdicts.

#### 5. `tests/test_t011_r1_counterexamples.py`
- Added valid 64-character `sha256_hash` to mock approved provenance in `test_verified_r1_f02`.

#### 6. `tests/test_t011_r3_counterexamples.py` (NEW)
- Created 32 permanent regression tests covering R3-F01 through R3-F05.

---

## 3. Risk Assessment Matrix

| Risk ID | Description | Severity | Likelihood | Mitigation / Status in R3 |
| :--- | :--- | :---: | :---: | :--- |
| **RSK-R3-01** | Raw CSV data modification | CRITICAL | ZERO | Zero bytes modified; verified via SHA-256 manifests. |
| **RSK-R3-02** | Staging schema regression | HIGH | ZERO | 34-column canonical raw schema untouched. |
| **RSK-R3-03** | Premature Gate G6 execution | CRITICAL | ZERO | G6 strictly marked `NOT_STARTED / BLOCKED`. |
| **RSK-R3-04** | False authentic BTS parity claim | HIGH | ZERO | `human_accepted` hardcoded to `False`; verdict gated as `PENDING`. |
| **RSK-R3-05** | Filesystem lock race condition | MEDIUM | VERY LOW | Pre-unlink token re-check eliminates race window. |
| **RSK-R3-06** | Corrupted lock file deletion | HIGH | ZERO | Fail-closed policy raises `LockContentionError` without unlinking. |
| **RSK-R3-07** | Non-existent calendar date match | LOW | ZERO | Real Gregorian calendar check (`datetime.date`) enforces validity. |

---

## 4. Operational Invariant Verification

- **Raw Data Immutability:** All 9 CSV source files in `data/raw/` have unmodified byte sizes and SHA-256 signatures matching the original project baseline.
- **Gate Boundaries:** Parent Gate G5 remains `IN_PROGRESS`. Gate G6 is strictly `NOT_STARTED / BLOCKED`.
- **Provisional Status:** `G2-EXC-001` remains active; unit designations are provisional.
- **Defect Records:** `OR-05` (missing March 2024) and `OR-08` (unverified identity) remain active in the risk register.

---

## 5. Conclusion

All source modifications in T011-R3 are targeted, minimal, and fully covered by regression guards. Zero regressions were introduced into previously accepted G2–G4 or T-010 components.
