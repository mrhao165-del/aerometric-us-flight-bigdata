# T009-SEAL-FIX Baseline & Audit Findings Report

## 1. Executive Summary & Audit Context
- **Task ID:** `T009-SEAL-CORRECTION`
- **Gate:** `G4` (Status: `PLANNED / NOT_COMPLETED`)
- **Execution Mode:** `TARGETED FIX — FAILING TESTS FIRST — NO UNRELATED REFACTORING`
- **Auditor:** Senior PySpark Engineer, Storage Safety Auditor, CI Engineer & Repository Governance Auditor
- **Audit Target:** Independent evaluation of `T009_FINAL_SEAL_PACKAGE.zip` and repository state at commit `ec361f16a8bc045291af95fe5694a95bc08fa46f`.

---

## 2. Identified Blockers & Findings

### Finding FIX-S01: Registry Omission of Final Governance Errata
- **Finding:** The file `T009_FINAL_GOVERNANCE_ERRATA.md` was packaged into `T009_FINAL_SEAL_PACKAGE.zip` under `docs/05-evidence/`, but was not committed to the live Git repository or registered in `EVIDENCE_DELIVERABLE_REGISTER.json`.
- **Root Cause:** To avoid leaving an uncommitted dirty working tree, the errata was generated into the external artifact directory and included in the external ZIP, leaving the live registry at 241 deliverables.
- **Remediation Mandate:** Bring `T009_FINAL_GOVERNANCE_ERRATA.md` directly into `docs/05-evidence/`, refine its content per FIX-S05, register it with exact byte size and SHA-256, and freeze the repository.

### Finding FIX-S02: Post-Switch Pointer Read Exception
- **Finding:** In `src/flight_pipeline/storage/publication.py`, if `get_current_pointer()` raises an `OSError` (e.g. transient NTFS file lock by an anti-virus scanner) at Step 6, `publish()` crashes with an unhandled exception after Step 5 has already modified the pointer file.
- **Root Cause:** Step 6 called `self.get_current_pointer()` without an exception handler or retry mechanism.
- **Remediation Mandate:** Implement retry/backoff in `get_current_pointer()`, wrap Step 6 read-back in `try-except OSError`, execute atomic rollback upon read error, verify rollback success, and return structured `PublicationResult` with clear error status (`FAILED_POINTER_READ_VERIFICATION` or `FAILED_POINTER_VERIFICATION_ROLLBACK_ERROR`).

### Finding FIX-S03: Non-Streaming SHA-256 RAM Hazard
- **Finding:** Lines 224 and 286 of `publication.py` computed hashes via `sha256(f.read_bytes()).hexdigest()`, loading entire Parquet partitions into memory.
- **Remediation Mandate:** Implement `compute_file_sha256()` with 64KB streaming chunks.

### Finding FIX-S04: GitHub Actions CI Incompatibility on Clean Checkout
- **Finding:** `.github/workflows/ci.yml` executed `tools/check_working_tree_consistency.py`, which required exactly 9 raw CSV files (`len(raw_data_files) == 9`). Because 15GB of raw CSVs are excluded from Git, clean checkouts on CI runners fail.
- **Remediation Mandate:** Add `--ci-mode` to `check_working_tree_consistency.py` enforcing that raw data is excluded from Git tracking, and update `ci.yml`.

### Finding FIX-S05: Governance Errata Precision
- **Finding:** Refine governance statements regarding OR-05 (March 2024 missing in audit data), OR-08 (local hash $\ne$ BTS identity), FP-DEC-017 (Weather CONDITIONAL_NO_GO), TS-018 G5 hard stop, Spark warnings, and TS-013 unit simulation boundary.
