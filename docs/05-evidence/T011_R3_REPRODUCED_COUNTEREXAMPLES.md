# T011-R3 — Reproduced Counterexamples Report

**Date:** 2026-10-19T14:06:00+07:00  
**Task:** T-011 R3 — Provenance Trust Boundary, Numeric Integrity, Lock Recovery & Evidence Correction  
**Parent Gate:** Gate G5 — `IN_PROGRESS`  
**Execution Phase:** Gate R3-1 — Defect Reproduction  
**Status:** `GATE_R3_1_COMPLETE — ALL_6_DEFECTS_REPRODUCED`

---

## 1. Executive Summary

This report documents the empirical reproduction of the 6 residual defects discovered by the independent technical auditor in the T011-R2 release. All counterexamples were executed directly against the unmodified R2 codebase (`src/flight_pipeline/kpi/bts_reconciler.py`, `tools/qa/run_ts018_bts_parity.py`, `src/flight_pipeline/storage/locking.py`) in an isolated sandbox.

Every defect was confirmed to produce unsafe behavior or false-pass results in the R2 baseline prior to remediation.

---

## 2. Empirical Defect Reproduction Results

### 2.1. R3-F01 — False Authentic BTS PASS Through Self-Approved Metadata (CRITICAL)
- **Vulnerability:** In `tools/qa/run_ts018_bts_parity.py`, line 124 executed `provenance_meta.sha256_hash = bts_sha256`, unconditionally overwriting any declared expected SHA-256 with the file's actual checksum. Then `bts_reconciler.py` validated the provenance hash against itself. Furthermore, an untrusted JSON file containing `project_lead_approval_status = "APPROVED_BY_PROJECT_LEAD"` was accepted as authentic proof of Project Lead approval.
- **Empirical Counterexample:**
  - File: `bts_sample.csv` with matching records across all 7 CORE measures.
  - Companion: `bts_sample.provenance.json` with `project_lead_approval_status = "APPROVED_BY_PROJECT_LEAD"`, `approval_record_ref = "DRAFT_FAKE_APPROVAL_NOT_REAL"`, `sha256_hash = "THIS_IS_INTENTIONALLY_A_BAD_SHA256"`.
- **Observed R2 Output:**
  ```text
  R2 Observed Verdict: TS018_PASS_AUTHENTIC_PARITY_ESTABLISHED
  R2 Observed source_provenance_verified: True
  R2 Observed human_accepted: False
  Exit Code: 0
  ```
- **Auditor Confirmation:** A locally fabricated CSV + JSON with a declared bad SHA-256 successfully obtained `TS018_PASS_AUTHENTIC_PARITY_ESTABLISHED`, completely bypassing the human signoff requirement.

---

### 2.2. R3-F02 — Malformed Numerics Masked as Null-Null Agreement (HIGH)
- **Vulnerability:** In `bts_reconciler.py`, `_to_float()` returned `None` for unparseable strings (e.g. `"invalidXYZ"`). When both sides contained malformed values, `compare_single_field()` saw `d_val is None and b_val is None` and assigned `MismatchType.NULL_NULL_AGREEMENT`. If a separate record had valid numbers, `numeric_sample_count > 0` and overall parity passed.
- **Empirical Counterexample:**
  - Record 1: `dataset.ARR_DELAY = "invalidXYZ"`, `BTS.ArrDelay = "invalidABC"`.
  - Record 2: Valid numbers across all 7 CORE fields.
- **Observed R2 Output:**
  ```text
  R2 Observed comparison status for invalidXYZ vs invalidABC: NULL_NULL_AGREEMENT
  R2 Observed ARR_DELAY null_null_agreement count: 1
  R2 Observed ARR_DELAY numeric_sample_count: 1
  R2 Observed overall verdict: SYNTHETIC_RECONCILER_VERIFIED_AUTHENTIC_BTS_PENDING
  ```
- **Auditor Confirmation:** Corrupt data strings were converted to legitimate null-null agreements, hiding data corruption behind successful parity.

---

### 2.3. R3-F03 — Unknown-Owner Lock Must Not Be Deleted (HIGH)
- **Vulnerability:** In `locking.py`, `break_stale_lock(force=True)` contained:
  ```python
  existing_meta = self._read_existing_metadata()
  if existing_meta is None:
      self.lock_file_path.unlink()
      return True
  ```
  If a lock file was corrupted, empty, or contained non-JSON data, `break_stale_lock(force=True)` unlinked it immediately, risking removal of an active lock belonging to another process.
- **Empirical Counterexample:**
  - Lock file: `.pipeline.lock` containing `"CORRUPTED_NON_JSON_METADATA"`.
  - Action: `lock.break_stale_lock(force=True)`.
- **Observed R2 Output:**
  ```text
  R2 Observed break_stale_lock(force=True) on unparseable lock: deleted=True, file_exists=False
  ```
- **Auditor Confirmation:** An active lock of unknown ownership was deleted without verifying PID liveness or host identity.

---

### 2.4. R3-F04 — Real Calendar Date Validation (MEDIUM)
- **Vulnerability:** In `bts_reconciler.py`, `ISO_DATE_REGEX = re.compile(r"^\d{4}-(?:0[1-9]|1[0-2])-(?:0[1-9]|[12]\d|3[01])$")` checked only digit patterns. It accepted calendar-impossible dates such as February 31st or leap days in non-leap years.
- **Empirical Counterexample:**
  - Input: `FL_DATE = "2026-02-31"`.
- **Observed R2 Output:**
  ```text
  R2 Observed key for '2026-02-31': fl_date=2026-02-31, is_valid=True
  ```
- **Auditor Confirmation:** Non-existent calendar dates passed composite key validation.

---

### 2.5. R3-F05 — Synthetic Verification Must Reject Unmatched Records (MEDIUM)
- **Vulnerability:** In `bts_reconciler.py`, `matched_parity_ok` checked only that matched records had no discrepancies and positive numeric counts. It did not require `unmatched_dataset_records == 0`. Consequently, `summary.reconciliation_verdict` was set to `SYNTHETIC_RECONCILER_VERIFIED_AUTHENTIC_BTS_PENDING` while `summary.numerical_parity_verified` was `False`.
- **Empirical Counterexample:**
  - Record 1: Perfectly matched across all 7 CORE measures.
  - Record 2: Present in dataset, absent from BTS reference.
- **Observed R2 Output:**
  ```text
  R2 Observed unique_key_matches: 1
  R2 Observed unmatched_dataset_records: 1
  R2 Observed numerical_parity_verified: False
  R2 Observed reconciliation_verdict: SYNTHETIC_RECONCILER_VERIFIED_AUTHENTIC_BTS_PENDING
  ```
- **Auditor Confirmation:** Reconciler reported synthetic verification success despite unmapped records, creating an internally contradictory summary.

---

### 2.6. R3-F06 — Evidence Claim Reconciliations (MEDIUM)
- **Discrepancy:** The R2 raw QA log reported 1,240 assertions, while the agent's textual response reported 1,241 assertions (due to re-running the consistency check at the end of the script). Additionally, `T011_R2_BTS_PROVENANCE_GUARD_AUDIT.md` made claims about cryptographic verification that were not enforced by executable source code (since line 124 in `run_ts018_bts_parity.py` overwrote the hash).
- **Remediation Plan:** Align exact assertions across logs, tools, and textual summaries; issue formal supersession errata in `T011_R3_EVIDENCE_CLAIM_ERRATA.md`.

---

## 3. Summary of Reproduction Exit State

| Defect ID | Description | Severity | R2 Baseline Status | Target R3 State |
|---|---|---|---|---|
| **R3-F01** | False authentic BTS PASS via self-approved metadata | CRITICAL | VULNERABLE (False PASS) | FAIL CLOSED (PENDING) |
| **R3-F02** | Malformed numerics masked as null-null agreement | HIGH | VULNERABLE (False PASS) | FAIL CLOSED (DISCREPANCY) |
| **R3-F03** | Unknown-owner lock deleted on force=True | HIGH | VULNERABLE (Unsafe Deletion) | FAIL CLOSED (MANUAL_RECOVERY) |
| **R3-F04** | Calendar-unaware date validation | MEDIUM | VULNERABLE (Invalid Date Accepted) | FAIL CLOSED (INVALID_KEY) |
| **R3-F05** | Synthetic verification emitted with unmatched records | MEDIUM | VULNERABLE (Inconsistent Verdict) | FAIL CLOSED (PARTIAL/FAIL) |
| **R3-F06** | Evidence claim discrepancies | MEDIUM | DISCREPANCY IDENTIFIED | RECONCILED & SEALED |

Gate R3-1 is successfully completed. All counterexamples are verified and reproducible.
