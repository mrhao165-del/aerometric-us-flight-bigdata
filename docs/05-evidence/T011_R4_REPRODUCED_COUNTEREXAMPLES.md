# T011-R4 Reproduced Counterexamples & Vulnerability Evidence

**Project:** US Flight Performance Analysis 2016–2024  
**Task:** T-011 R4 — Provenance Trust, Lock Recovery Safety & Evidence Reconciliation  
**Parent Gate:** G5 — IN_PROGRESS  
**Component:** Reconciliation Engine (`src/flight_pipeline/kpi/bts_reconciler.py`) & Locking Engine (`src/flight_pipeline/storage/locking.py`)  
**Status:** ALL 3 RESIDUAL DEFECTS (R4-F01, R4-F02, R4-F03) FULLY REPRODUCED AND EMPIRICALLY CONFIRMED

---

## 1. Executive Summary

Prior to applying any source fixes in T-011 R4, an isolated empirical test harness (`scratch/reproduce_r4_defects.py`) was executed against the pre-fix codebase.
All 3 residual defects independently discovered by the technical auditor were reproduced with 100% fidelity:

1. **R4-F01 (CRITICAL): Provenance Self-Verification & Checksum Self-Comparison**
   - A self-authored companion JSON claiming `APPROVED_BY_PROJECT_LEAD` and matching a local candidate CSV's SHA-256 caused `BtsProvenanceValidator` and `reconciler.reconcile()` to award `source_provenance_verified = True`.
   - When `actual_bts_sha256=None`, the fallback compared `provenance.sha256_hash` with itself (`check_sha = actual_bts_sha256 or (provenance_metadata.sha256_hash...)`), creating a tautological self-match.

2. **R4-F02 (HIGH): Invalid PID Authorizing Lock Deletion**
   - Calling `SingleWriterLock.break_stale_lock(force=True)` on a lock containing a truthy but invalid PID (`"not-an-integer"`, `-1`, `3.1`, `True`) caused `is_pid_alive()` to return `False`.
   - The pre-fix recovery method treated `is_pid_alive() == False` as proof of process termination, deleting the lock file instead of failing closed with `FAIL_CLOSED — MANUAL_RECOVERY_REQUIRED`.

3. **R4-F03 (HIGH): Lock Replacement Race Condition (TOC/TOU)**
   - In `break_stale_lock()`, replacing the lock file immediately after the final metadata check resulted in deleting the newly created, active writer's lock.
   - In `release()`, replacing the lock file immediately after `_read_existing_metadata()` resulted in the releasing instance deleting another writer's lock.

---

## 2. Empirical Reproduction Outcomes

### 2.1. R4-F01 — Provenance Self-Verification Log
```text
--- [REPRODUCING R4-F01] Provenance Self-Verification ---
R4-F01 Reproduction 1A: BtsProvenanceValidator.validate_provenance -> prov_ok=True, prov_msg='PROVENANCE_METADATA_FORMAT_VERIFIED'
R4-F01 Reproduction 1B: summary.source_provenance_verified = True (DEFECT: accepted self-authored provenance as True!)
R4-F01 Reproduction 1C: summary.reconciliation_verdict = TS018_CANDIDATE_PARITY_VERIFIED_HUMAN_APPROVAL_PENDING
R4-F01 Reproduction 1D: When actual_bts_sha256 is None, summary.source_provenance_verified = True (DEFECT: compared hash with itself!)
```

### 2.2. R4-F02 — Invalid PID Deletion Log
```text
--- [REPRODUCING R4-F02] Invalid PID Authorizing Lock Deletion ---
R4-F02 Reproduction: PID='not-an-integer' (str) -> break_stale_lock returned True, file exists after break: False (DEFECT: deleted lock with invalid PID!)
R4-F02 Reproduction: PID=-1 (int) -> break_stale_lock returned True, file exists after break: False (DEFECT: deleted lock with invalid PID!)
R4-F02 Reproduction: PID=3.1 (float) -> break_stale_lock returned True, file exists after break: False (DEFECT: deleted lock with invalid PID!)
R4-F02 Reproduction: PID=True (bool) -> break_stale_lock returned True, file exists after break: False (DEFECT: deleted lock with invalid PID!)
R4-F02 Expected Exception: PID=0 -> LockContentionError: Cannot break incomplete lock file .pipeline.lock: missing required metadata fields. FAIL_CLOSED — MANUAL_RECOVERY_REQUIRED
```

### 2.3. R4-F03 — Lock Replacement Race Log
```text
--- [REPRODUCING R4-F03] Lock Replacement Race Condition ---
R4-F03 Reproduction 3A: After racy break_stale_lock, does new active writer lock exist? False (DEFECT: new lock was deleted!)
R4-F03 Reproduction 3B: After racy release, does writer 2 lock exist? False (DEFECT: writer 2 lock was deleted!)
```

---

## 3. Defect Analysis & Targeted Remediation Blueprint

### R4-F01 Remediation Blueprint:
1. Disaggregate metadata-structure validity, checksum integrity, and external acquisition authentication into separate indicators.
2. Local metadata can only establish `companion_metadata_valid` and `candidate_checksum_matched`.
3. `source_provenance_verified` remains strictly `False` until independent Project Lead acquisition verification is delivered.
4. Remove the fallback comparing `provenance.sha256_hash` to itself; strictly require `actual_bts_sha256` to be a non-empty 64-char string.
5. Official `TS018_PASS_AUTHENTIC_PARITY_ESTABLISHED` remains completely unreachable through agent-controlled candidate files.

### R4-F02 Remediation Blueprint:
1. Enforce strict type validation in `LockMetadata`: `pid` must be an `int`, `not isinstance(pid, bool)`, and `pid > 0`.
2. Define explicit `PidLivenessStatus` Enum: `PROCESS_ALIVE`, `PROCESS_DEAD`, `INVALID_PID`, `PROCESS_STATUS_UNKNOWN`.
3. In `break_stale_lock()`, any status other than `PROCESS_DEAD` on the local host must fail closed with `FAIL_CLOSED — MANUAL_RECOVERY_REQUIRED`.
4. `force=True` must never bypass PID type or liveness validation.

### R4-F03 Remediation Blueprint:
1. Re-verify the lock file's owner token immediately prior to unlink in both `break_stale_lock()` and `release()`.
2. If the lock was replaced or its owner token does not match the expected instance/stale token, abort unlinking and fail closed.
3. Explicitly document that unprivileged filesystem deletion on Windows NTFS / POSIX is not a native atomic compare-and-swap, requiring operator quiescence for manual recovery.
