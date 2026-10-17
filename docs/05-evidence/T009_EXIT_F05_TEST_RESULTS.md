# T009-R3-EXIT Defect F-05 Test Results & Safety Verification Report

## 1. Background & Scope of Defect F-05
Defect F-05 was identified during the independent source audit of the safe publication engine (`src/flight_pipeline/storage/publication.py`). While `SafePublisher` implemented the 7-step publication order, dedicated test cases were required to rigorously verify:
1. Step 6 post-switch pointer verification mismatch and subsequent atomic rollback.
2. Status reporting when an NTFS lock or OS failure prevents the rollback replacement from completing (`FAILED_POINTER_VERIFICATION_ROLLBACK_ERROR`).
3. Non-destructive policy ensuring that failed publication attempts never delete previous valid runs, staging artifacts, or promoted runs.
4. Concurrency boundary: Explicit documentation and verification of the single-writer operational assumption.

---

## 2. Test Suite Implementation (`tests/test_publication_safety.py`)

### 2.1 Test F05-01: Post-Pointer Read-Back Mismatch & Atomic Rollback
- **Test Method:** `test_f05_01_pointer_verification_mismatch_triggers_atomic_rollback`
- **Scenario:** Initial run `run_001` is published. A second run `run_002` is staged and promoted. During Step 5, pointer switch appears to succeed, but in Step 6, the immediate read-back of `latest_run_id.txt` detects an unexpected or corrupted value.
- **Verification Assertions:**
  - `result.success == False`
  - `result.status == "FAILED_POINTER_VERIFICATION"`
  - `result.aborted_step == 6`
  - `result.previous_pointer == "run_001"`
  - `publisher.get_current_pointer() == "run_001"` (atomic rollback restores previous valid run)
- **Status:** PASS.

### 2.2 Test F05-02: Rollback Replacement Failure Diagnostic Reporting
- **Test Method:** `test_f05_02_pointer_verification_rollback_failure_reporting`
- **Scenario:** Post-switch verification detects a pointer mismatch, and the subsequent atomic rollback write (`_atomic_write_pointer`) also fails due to an NTFS file lock or OS error.
- **Verification Assertions:**
  - `result.success == False`
  - `result.status == "FAILED_POINTER_VERIFICATION_ROLLBACK_ERROR"`
  - `result.aborted_step == 6`
  - `result.previous_pointer == "run_001"`
- **Status:** PASS.

### 2.3 Test F05-03: Non-Destructive Preservation of Artifacts
- **Test Method:** `test_f05_03_preservation_of_previous_version_and_failure_artifacts`
- **Scenario:** A failure occurs during the publication sequence (e.g. at Step 5 or Step 6).
- **Verification Assertions:**
  - Previous published version in `curated/runs/run_001/` remains byte-for-byte identical (unmodified, uncorrupted).
  - Pointer remains pointing to `run_001`.
  - Staging directory `staging/run_002/` is preserved intact for engineering triage and retry.
  - Promoted directory `curated/runs/run_002/` is retained for forensic audit.
- **Status:** PASS.

### 2.4 Test F05-04: Single-Writer Operational Assumption & Version Collision
- **Test Method:** `test_f05_04_single_writer_operational_assumption_and_version_collision`
- **Scenario:** The batch pipeline operates under a strict single-writer operational assumption. If two processes attempt to publish under the identical `run_id`, Step 3 detects that the target directory exists and rejects the promotion.
- **Verification Assertions:**
  - First run `run_batch_01` succeeds and publishes cleanly.
  - Second concurrent attempt with same `run_id` is rejected with `status == "FAILED_VERSION_EXISTS"`.
  - `aborted_step == 3`.
  - Pointer and existing data remain strictly unmodified.
- **Status:** PASS.

---

## 3. Execution Summary
- All 4 F-05 test cases were integrated into `tests/test_publication_safety.py`.
- Suite execution: 11 tests in 0.455s (incorporating baseline publication, F-02, F-03, F-04, and all F-05 variants).
- **Outcome:** 11 PASS, 0 FAIL, 0 ERROR.
