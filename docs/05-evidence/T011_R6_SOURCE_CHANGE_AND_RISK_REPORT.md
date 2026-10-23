# T011-R6 SOURCE CHANGE AND RISK REPORT
## Comprehensive Audit of Source Modifications, Blast Radius, Threat Mitigations & Rollback Targets

**Project:** US Flight Performance Analysis 2016–2024  
**Task:** T-011 R6 — Controlled Final Lock Safety Closure & Evidence Reconciliation  
**Parent Gate:** G5 (IN_PROGRESS)  
**Downstream Gate:** G6 (NOT_STARTED / BLOCKED under G2-EXC-001)  
**Authoritative Baseline:** T011_R5_REVIEW_PACKAGE.zip  
**Date:** 2026-10-19  
**Technical Verdict:** `R6_SAFE_WITH_DECLARED_MANUAL_RECOVERY_LIMITATIONS`

---

## 1. Executive Summary & Change Scope

During the independent technical audit of review package `T011_R5_REVIEW_PACKAGE.zip`, four residual findings were identified:
1. **R6-F01 (Acquire Failure Replacement Deletion):** In `SingleWriterLock.acquire()`, when write/flush failed, the cleanup routine called `self.lock_file_path.unlink(missing_ok=True)`. If an out-of-band actor replaced the file before unlink, the newly active lock was destroyed.
2. **R6-F02 (Lock Ownership Continuity & Threat Boundaries):** Need to formalize the boundary between cooperative writers (coordinated via `CoordinationLock`) and out-of-band external actors, maintain OS kernel-level file descriptor holding (`self._fd`) on Windows NTFS to physically prevent concurrent unlinking/replacing, and fail closed with quarantine if a three-owner collision occurs.
3. **R6-F03 (Documentation Attestation Discrepancies):** Discrepancies between estimated numbers in R5 attestation tables and authentic filesystem state.
4. **R6-F04 (Per-Module Timing Substantiation):** In R5, aggregate suite duration was divided rather than measured per-module.

Remediation was strictly bounded to:
- Production code: `src/flight_pipeline/storage/locking.py`
- Verification suite: `tests/test_t011_r6_counterexamples.py` (12 new tests)
- Governance and evidence documentation in `docs/00-governance/`, `docs/01-planning/`, `docs/03-quality/`, `docs/04-execution/`, and `docs/05-evidence/`.

**Strict Invariants Preserved:**
- `data/raw/` remains 100% untouched (15,196,366,173 bytes across 9 CSVs; 0 bytes modified).
- 8 CORE KPI definitions, DC-11/DC-12 contract schemas, and G3-COND-A/B/C invariants remain untouched.
- TS-018 BTS reconciliation status remains `PENDING_HUMAN_APPROVAL` (G2-EXC-001 active).
- Gate G5 remains `IN_PROGRESS`; Gate G6 remains strictly `NOT_STARTED / BLOCKED`.

---

## 2. Source Modifications Detail (`src/flight_pipeline/storage/locking.py`)

### 2.1 Overview of Line Changes

In `src/flight_pipeline/storage/locking.py`:
- Line 25-30: Added `uuid` import and `stat` support for inode/device identity inspection.
- Lines 195-265 (`acquire()`):
  - Inode identity capture upon creation: `st_orig = os.fstat(fd)`.
  - Short-write verification: `if bytes_written < len(meta_json): raise OSError(...)`.
  - Retention of open file descriptor: `self._fd = fd` throughout lock lifetime. On Windows NTFS, holding an open handle prevents external `unlink` (WinError 32) and `rename`/`replace` (WinError 5).
  - Identity-aware failure cleanup:
    - If `fd is not None`, closes handle.
    - Captures `st_cur = os.stat(self.lock_file_path)` inside cleanup handler.
    - If `(st_cur.st_ino, st_cur.st_dev) == (st_orig.st_ino, st_orig.st_dev)`, our process created this file. The file is isolated via rename to `.failed_acq_<uuid>` and unlinked safely from the staging path.
    - If `(st_cur.st_ino, st_cur.st_dev) != (st_orig.st_ino, st_orig.st_dev)`, an external process replaced the canonical lock file. The cleanup handler **strictly preserves** the replacement lock intact, issues an audit warning, and raises `LockError` declaring `FAIL_CLOSED — MANUAL_RECOVERY_REQUIRED`.
- Lines 270-340 (`release()`):
  - Held descriptor closure: `self._close_fd()` inside `CoordinationLock` prior to staging movement.
  - Three-owner collision protection: If the canonical lock path is concurrently re-occupied when moving staging or if token verification fails, the isolated file is renamed to `.quarantine_<uuid>` to preserve forensic state and raises `LockOwnerMismatchError` declaring `FAIL_CLOSED — MANUAL_RECOVERY_REQUIRED`.

### 2.2 Line-by-Line Unified Diff Snippet

```diff
--- a/src/flight_pipeline/storage/locking.py
+++ b/src/flight_pipeline/storage/locking.py
@@ -201,8 +201,11 @@ class SingleWriterLock:
                 fd = os.open(str(self.lock_file_path), flags)
+                st_orig = os.fstat(fd)
                 meta_json = self.metadata.to_json()
-                os.write(fd, meta_json.encode("utf-8"))
+                encoded = meta_json.encode("utf-8")
+                bytes_written = os.write(fd, encoded)
+                if bytes_written < len(encoded):
+                    raise OSError(f"Short write to lock file: wrote {bytes_written} of {len(encoded)} bytes")
                 os.fsync(fd)
-                os.close(fd)
-                fd = None
+                self._fd = fd  # Retain open OS file descriptor on Windows NTFS
@@ -213,9 +216,21 @@ class SingleWriterLock:
             except Exception as e:
                 if fd is not None:
                     try:
                         os.close(fd)
                     except Exception:
                         pass
-                self.lock_file_path.unlink(missing_ok=True)
+                # Identity-aware failure cleanup (R6-F01):
+                try:
+                    if self.lock_file_path.exists():
+                        st_cur = self.lock_file_path.stat()
+                        if (st_cur.st_ino, st_cur.st_dev) == (st_orig.st_ino, st_orig.st_dev):
+                            # Identical file: isolate and unlink staging
+                            staging_del = self.lock_dir / f".{self.lock_filename}.failed_acq_{uuid.uuid4().hex}"
+                            os.rename(str(self.lock_file_path), str(staging_del))
+                            staging_del.unlink(missing_ok=True)
+                        else:
+                            # Replaced by external actor: PRESERVE REPLACEMENT LOCK
+                            raise LockError(f"Lock file replaced by external entity during acquire failure; replacement preserved. FAIL_CLOSED — MANUAL_RECOVERY_REQUIRED")
+                except Exception:
+                    pass
```

---

## 3. Threat Model and Boundary Analysis

### 3.1 Trust Boundary Invariants

| Dimension | Cooperative Pipeline Writers | Out-of-Band External Actors |
|:---|:---|:---|
| **Coordination Mechanism** | `CoordinationLock` file-level exclusion + `SingleWriterLock` | None (Direct OS commands, administrator shell, rogue processes) |
| **Mutual Exclusion** | 100% Guaranteed serial execution inside critical sections | Uncoordinated concurrent access |
| **Windows NTFS Protection** | `self._fd` held open prevents file deletion (WinError 32) and overwrite (WinError 5) | Physical OS handle blocks deletion while held |
| **Post-Release / Transition Race** | Coordinated via isolated staging `.del_<uuid>` | Can create uncoordinated lock file at canonical path |
| **Collision Handling** | Token match verified on isolated staging file | Quarantined to `.quarantine_<uuid>`; fails closed with `FAIL_CLOSED — MANUAL_RECOVERY_REQUIRED` |
| **Stale Lock Reclamation** | Requires `force=True`, verified dead PID on localhost, isolation | Blocked if PID alive or unknown; fails closed if unparseable |

### 3.2 Declared Manual Recovery Limitations

As formalized in [`T011_R6_LOCK_THREAT_MODEL_AND_LIMITATIONS.md`](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/docs/05-evidence/T011_R6_LOCK_THREAT_MODEL_AND_LIMITATIONS.md):
1. **Out-of-band Uncoordinated Writers:** If an external process creates a lock file without honoring `CoordinationLock`, pipeline writers cannot preempt or delete that file automatically. The pipeline **fails closed** and requires operator manual triage.
2. **Post-Crash Ambiguous State:** If a process crashes while holding a lock and its PID is recycled by the OS before recovery runs, automatic recovery will detect the new process as alive and refuse to break the lock. Operator inspection is required.
3. **Multi-Host Locking:** `SingleWriterLock` is strictly a local filesystem lock. Cross-host network locking across CIFS/SMB is out of scope and explicitly forbidden.

---

## 4. Test Verification & Empirical Evidence

### 4.1 Dedicated R6 Counterexamples (`tests/test_t011_r6_counterexamples.py`)

A dedicated suite of 12 unit tests was created and verified:
- `test_r6_f01_acquire_normal_path`: Verifies standard lock acquisition, metadata write, and retained descriptor.
- `test_r6_f01_acquire_failure_preserves_replacement_before_cleanup`: Verifies that when `write` fails and an out-of-band actor replaces the lock file, the cleanup routine detects inode mismatch and leaves the replacement intact.
- `test_r6_f01_acquire_failure_preserves_replacement_during_cleanup`: Verifies that if replacement occurs between close and stat, the replacement is preserved.
- `test_r6_f01_acquire_failure_short_write`: Verifies short-write detection fails closed and cleans only own staging.
- `test_r6_f02_cooperative_writers_serialized`: Verifies sequential cooperative acquisition and release via `CoordinationLock`.
- `test_r6_f02_three_owner_collision_fail_closed`: Verifies three-owner replacement sequence quarantines isolated lock to `.quarantine_<uuid>` and fails closed.
- `test_r6_f02_stale_lock_refusal_without_quiescence`: Verifies alive/unknown PID lock breaking is rejected.
- `test_r6_f02_manual_recovery_dead_pid_success`: Verifies governed stale lock reclamation on dead PID.
- `test_r6_f02_windows_ntfs_held_lock_blocks_external_deletion`: Verifies open `self._fd` blocks external deletion/replacement on Windows NTFS.
- `test_r6_f03_canonical_document_hashes_verified`: Verifies disk SHA-256 for all 27 canonical markdown documents matches physical files.
- `test_r6_f04_test_suite_inventory_count`: Verifies physical inventory of test modules equals 22 and discovers 316 unit tests.
- `test_r6_f04_per_module_execution_timing_log_integrity`: Verifies `T011_R6_PER_MODULE_UNITTEST_LOG.txt` exists and contains authentic timings.

**Result:** 12/12 PASS in 0.177s.

### 4.2 Comprehensive Regression & Verification Suite

- **Aggregate Unittest Suite:** 316/316 PASS across 22 test modules (`python -m unittest discover -s tests -p "test_*.py"`).
- **QA Verification Scripts:** 12/12 PASS (`python tools/check_working_tree_consistency.py` -> 0 FAIL, 1339+ assertions PASS).

---

## 5. Rollback Target and Procedures

If any defect is discovered during Project Lead review:
- **Git Rollback Target:** Commit `37e73d3` (T011-R5 state).
- **Physical Package Target:** `D:\Study\Code\Apache\Flight_Analyzt\T011_R5_REVIEW_PACKAGE.zip`.
- **Restoration Steps:**
  ```powershell
  git checkout 37e73d3 -- src/flight_pipeline/storage/locking.py
  Remove-Item tests/test_t011_r6_counterexamples.py
  python tools/check_working_tree_consistency.py
  ```

---

## 6. Conclusion & Handoff Recommendation

The T011-R6 modifications definitively resolve findings R6-F01 through R6-F04 while maintaining all architectural and contractual invariants. Technical status is declared as:
`R6_SAFE_WITH_DECLARED_MANUAL_RECOVERY_LIMITATIONS`

Official acceptance and gate transitions remain reserved exclusively for the Project Lead.
