# T012 Final Targeted Preflight Correction — Evidence & Technical Audit Report

**Document ID:** `T012_FINAL_PREFLIGHT_CORRECTION`  
**Date:** 2026-10-21  
**Project:** US Flight Performance Analysis 2016–2024  
**Task:** T012-MINIMAL-UNBLOCK Final Preflight Remediation  
**Status:** `READY_FOR_HUMAN_SIGNOFF_PREPARATION`  
**Authority:** Project Lead  

---

## 1. Executive Summary & Governance State

Following independent technical review of the `T012_MINIMAL_UNBLOCK_REVIEW.zip` package, two preflight-specific defects were reproduced:
1. **Defect 1 (Incorrect PID Enum Members):** CLI preflight checked `PidLivenessStatus.ALIVE` and `PidLivenessStatus.DEAD` rather than `PROCESS_ALIVE` and `PROCESS_DEAD`, raising an unhandled `AttributeError` that was caught and misclassified as `CORRUPT_LOCK_METADATA`.
2. **Defect 2 (Empty Pointer False-PASS):** CLI preflight did not record an error when an existing pointer file was empty or whitespace-only, resulting in a false `PREFLIGHT PASS` (exit code 0).

Both defects have been remediated with minimal, targeted changes strictly confined to:
- `src/flight_pipeline/ingestion/coordinator.py`
- `tests/test_coordinator_preflight_unblock.py`

### Current Governance State (Strictly Maintained)
| Governance Entity | Status | Description / Authority Boundary |
|---|---|---|
| **Gate G5** | `IN_PROGRESS` | Technical artifacts closed; Human signoff pending |
| **Gate G6** | `BLOCKED` | Awaiting G5 closure, D1–D4, and G6-ARCH-2016 |
| **Task T-012** | `NOT_STARTED` | Ingestion pipeline not initiated |
| **Decision D1** | `PENDING` | BTS Source Provenance Attestation (Human Signoff) |
| **Decision D2** | `PENDING` | FP-DEC-019 Option B Formal Approval (Human Signoff) |
| **Decision D3** | `PENDING` | TS-018 Technical Parity Human Acceptance |
| **Decision D4** | `PENDING` | Gate G5 Human Gate Signoff |
| **Decision D5** | `NOT_AUTHORIZED` | Production Execution Authorization strictly held |
| **G6-ARCH-2016** | `PENDING` | Architecture selection for 2016 baseline integration |

**CRITICAL INVARIANT:** No production Spark execution was run; no RAW source CSVs were touched; no T-010 staging Parquet baseline files were modified; no locks or pointers were modified.

---

## 2. Defect 1: Incorrect PID Enum Members

### 2.1 Root Cause Analysis
In `src/flight_pipeline/storage/locking.py`, the process-liveness enumeration is defined as:
```python
class PidLivenessStatus(str, Enum):
    PROCESS_ALIVE = "PROCESS_ALIVE"
    PROCESS_DEAD = "PROCESS_DEAD"
    INVALID_PID = "INVALID_PID"
    PROCESS_STATUS_UNKNOWN = "PROCESS_STATUS_UNKNOWN"
```
In `src/flight_pipeline/ingestion/coordinator.py` (preflight section), the code attempted to access:
```python
if liveness == PidLivenessStatus.ALIVE:
    ...
elif liveness == PidLivenessStatus.DEAD:
    ...
```
Because `PidLivenessStatus` does not define `ALIVE` or `DEAD`, an `AttributeError` was raised. The enclosing generic `except Exception as exc:` caught the `AttributeError` and classified valid active locks as:
`CORRUPT_LOCK_METADATA ('PidLivenessStatus' object has no attribute 'ALIVE')`.
While this blocked execution (fail-closed), the diagnostic classification was incorrect and masked process liveness.

### 2.2 Applied Remediation
1. **Enum Alignment:** Replaced invalid attributes with `PidLivenessStatus.PROCESS_ALIVE`, `PidLivenessStatus.PROCESS_DEAD`, `PidLivenessStatus.INVALID_PID`, and `PidLivenessStatus.PROCESS_STATUS_UNKNOWN`.
2. **Decoupled Metadata Parsing from Liveness:** Separated JSON metadata parsing from PID evaluation so that genuine parse errors (`json.JSONDecodeError`, schema invalidity) yield `CORRUPT_LOCK_METADATA`, while liveness outcomes yield distinct, accurate diagnostics:
   - `PROCESS_ALIVE` $\rightarrow$ `ACTIVE_WRITER_RUNNING`
   - `PROCESS_DEAD` $\rightarrow$ `STALE_LOCK_DEAD_PID`
   - `INVALID_PID` $\rightarrow$ `INVALID_PID`
   - `PROCESS_STATUS_UNKNOWN` $\rightarrow$ `AMBIGUOUS_LOCK`
3. **Fail-Closed Guarantee:** Every branch where a lock file exists appends an entry to `preflight_errors` and blocks preflight (exit code 1).

---

## 3. Defect 2: Empty Pointer False-PASS

### 3.1 Root Cause Analysis
In `coordinator.py`, pointer inspection checked:
```python
if pointer_file.is_file():
    ptr_val = pointer_file.read_text(encoding="utf-8").strip()
    if ptr_val:
        ... # validation and dangling checks
    else:
        pointer_status_str = "EMPTY_POINTER"
```
When `ptr_val` was empty string `""` or whitespace, `pointer_status_str` was set to `"EMPTY_POINTER"`, but **no error was added to `preflight_errors`**. As a consequence, preflight reported `PREFLIGHT PASS` (exit code 0). In contrast, `tools/qa/verify_staging_pointer.py` correctly treated `EMPTY_POINTER_FILE` as a fatal failure.

### 3.2 Applied Remediation
Aligned pointer inspection semantics with established project verification rules:
1. **Distinguish Absent vs Empty Pointer:**
   - **Absent pointer (`not pointer_file.exists()`):** Permitted as valid uninitialized state (`UNINITIALIZED`). Preflight may pass in dry-run mode if all other criteria pass.
   - **Existing empty / whitespace-only pointer:** Classified as `EMPTY_POINTER_FILE`. Appends to `preflight_errors` with `"Empty or whitespace-only pointer file detected at <path>"` and fails preflight (exit code 1).
2. **File Type Enforcement:** If pointer exists but is not a regular file (e.g. a directory), it is classified as `POINTER_NOT_A_FILE` and fails preflight.
3. **Anti-Traversal & Dangling Check Preservation:** Preserved `validate_run_id` checks (preventing path traversal and format corruption $\rightarrow$ `CORRUPT_POINTER`) and target directory existence checks ($\rightarrow$ `DANGLING_POINTER`).

---

## 4. Assessment of FP-DEC-018 Lock Release Incident Handling

The previous review package introduced structured incident logging in `coordinator.py` for post-publication lock release failures. This was audited against `FP-DEC-018`:
- **FP-DEC-018 Principle:** If Parquet data was successfully published and verified, but the subsequent lock release fails, the publication remains valid and readable. The run outcome records `success=True` with `recovery_required=True`, and all future coordinating writer processes remain strictly blocked (`FAIL_CLOSED`) until manual recovery is completed.
- **Audit Finding:**
  - `coordinator.py` safely calls `lock.persist_release_incident(release_err, pipeline_err)`.
  - Durability and readback verification are performed by `SingleWriterLock`.
  - Unresolved recovery markers (`.recovery_required*`, `.del_*`, `.quarantine_*`, `.failed_acq_*`) are inspected during preflight via `lock_obj.get_unresolved_recovery_artifacts()` and glob inspection.
  - If any marker is present, preflight fails immediately with `BLOCKED_UNRESOLVED_RECOVERY`.
- **Conclusion:** The lock release incident handling in `coordinator.py` is fully compliant with FP-DEC-018. No changes to this logic were needed, and it remains intact.

---

## 5. Verification & Test Evidence

### 5.1 Test Suite Results (`tests/test_coordinator_preflight_unblock.py`)
Executed command:
```powershell
cmd /c "set PYTHONPATH=src && python -m unittest -v tests/test_coordinator_preflight_unblock.py"
```
**Outcome:** `16/16 PASSED` (0.197s), Exit Code 0.

| Test Scenario | Scenario Name | Verified Assertion | Result |
|---|---|---|---|
| `test_01` | Valid preflight synthetic | Exit code 0, PREFLIGHT PASS | **PASS** |
| `test_02` | Missing RAW source | Exit code 1, `FAIL (MISSING)` | **PASS** |
| `test_03` | Byte-size mismatch | Exit code 1, `FAIL (SIZE_MISMATCH)` | **PASS** |
| `test_04` | SHA-256 mismatch | Exit code 1, `FAIL (HASH_MISMATCH)` | **PASS** |
| `test_05` | Active writer lock blocked | Exit code 1, `ACTIVE_WRITER_RUNNING`, NO `CORRUPT_LOCK_METADATA` | **PASS** |
| `test_05b` | Stale dead PID writer lock | Exit code 1, `STALE_LOCK_DEAD_PID`, NO `CORRUPT_LOCK_METADATA` | **PASS** |
| `test_05c` | Genuinely corrupt lock metadata | Exit code 1, `CORRUPT_LOCK_METADATA` | **PASS** |
| `test_05d` | Ambiguous / Invalid PID lock | Exit code 1, `AMBIGUOUS_LOCK` and `INVALID_PID` | **PASS** |
| `test_06` | Unresolved recovery / Dangling pointer | Exit code 1, `BLOCKED_UNRESOLVED_RECOVERY` and `DANGLING_POINTER` | **PASS** |
| `test_06b` | Empty / Whitespace pointer fails | Exit code 1, `EMPTY_POINTER_FILE`, `[PREFLIGHT FAIL]` | **PASS** |
| `test_06c` | Absent pointer uninitialized passes | Exit code 0, `UNINITIALIZED`, `[PREFLIGHT PASS]` | **PASS** |
| `test_06d` | Path traversal pointer fails | Exit code 1, `CORRUPT_POINTER`, `[PREFLIGHT FAIL]` | **PASS** |
| `test_07` | Duplicate run_id blocked | Exit code 1, duplicate run detected | **PASS** |
| `test_08` | Invalid year / run_id traversal | Exit code 1, traversal blocked | **PASS** |
| `test_09` | Unauthorized live execution hold | Exit code 1, `[GOVERNANCE HOLD]`, no data written | **PASS** |
| `test_10` | CLI path resolution aliases | Exit code 0 for `--base-dir` and `--base-data-dir` | **PASS** |

### 5.2 Companion Pointer and Lock Tests
- `tests/test_lock_state_vs_pointer_state.py`: 12/12 PASSED
- `tests/test_verify_staging_pointer.py`: 10/10 PASSED

### 5.3 CLI Real-Data Dry-Run Smoke Test
Executed command:
```powershell
$env:PYTHONPATH = "src"; python src/flight_pipeline/ingestion/coordinator.py --years 2016 --run-id run_preflight_dry_check_01 --dry-run-preflight
```
Output:
- Target Directory: `.../data/curated/runs/run_preflight_dry_check_01`
- Survey Years: `[2016]`
- Lock Status: `CLEAN`
- Pointer Status: `UNINITIALIZED`
- Source Status: `[OK]` | Audited Rows: `5,537,987` | Actual Bytes: `1,538,427,452`
- SHA-256 Status: `VERIFIED_MATCH (4ed92ed732721a38...)`
- Verdict: `[PREFLIGHT PASS] Preflight safety inspection completed successfully. All mandatory safety criteria PASSED. No data written.`
- Exit Code: **0**

### 5.4 Live Execution Governance Hold Verification
Executed command:
```powershell
$env:PYTHONPATH = "src"; python src/flight_pipeline/ingestion/coordinator.py --years 2016 --run-id run_preflight_dry_check_02
```
Output:
- `[PREFLIGHT PASS] Preflight safety inspection completed successfully.`
- `[GOVERNANCE HOLD] Live ingestion execution is BLOCKED.`
- `Decision D5 (Gate G6 Annual Ingestion Authorization) has NOT been approved by Project Lead.`
- `Status: PENDING_D5`
- Exit Code: **1**
- Absolute confirmation: No staging or curated directories created; no Spark session executed.

---

## 6. Review Package Deliverables

1. **Patch:** `docs/05-evidence/T012_FINAL_PREFLIGHT_CORRECTION.patch`
2. **Execution Test Log:** `docs/05-evidence/T012_FINAL_PREFLIGHT_CORRECTION_TEST_LOG.txt`
3. **Review Archive:** `T012_FINAL_PREFLIGHT_CORRECTION_REVIEW.zip` (located in project root and mirrored in `docs/05-evidence/`)
4. **Manifest:** `T012_FINAL_PREFLIGHT_CORRECTION_REVIEW_MANIFEST.json`

---

## 7. Recommended Human Action

The preflight defects are completely resolved. The codebase is fail-closed, verified by regression tests, and fully prepared for Project Lead human review.

**Recommended Decision:** Accept technical remediation and proceed with human review of Decisions D1–D4 towards closing Gate G5. Maintain Decision D5 as `NOT_AUTHORIZED`.
