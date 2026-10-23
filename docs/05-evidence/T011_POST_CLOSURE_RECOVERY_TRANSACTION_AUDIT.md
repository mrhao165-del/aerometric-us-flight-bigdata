# T011 POST-CLOSURE RECOVERY TRANSACTION AUDIT
## Durable Hold Mechanism, Fail-Closed Admission Guards & Resolution Verification

**Project:** US Flight Performance Analysis 2016–2024  
**Task:** T011-R6-POST-CLOSURE  
**Parent Gate:** Gate G5 — `IN_PROGRESS` (Downstream Gate G6: `NOT_STARTED / BLOCKED` under `G2-EXC-001`)  
**Scope:** Remediation and Verification of Finding C1  
**Authority:** Project Lead only.

---

## 1. Finding C1 Root Cause & Architectural Risk

Under the prior implementation of `SingleWriterLock.resolve_recovery_state()`, the recovery routine performed:
1. Enumeration of unresolved recovery artifacts (`unresolved = self.get_unresolved_recovery_artifacts()`).
2. Immediate relocation of all detected artifacts into `target_archive` using `os.replace`.
3. Subsequent serialization of the resolution audit record (`res_file.write_text(...)`).

### The Architectural Failure Mode:
If step 3 encountered an unhandled I/O error, disk full (`ENOSPC`), permission failure (`EACCES`), process crash, or power interruption:
- All blocking artifacts (`.del_*`, `.release_in_progress_*`, `.quarantine_*`) had already been removed from `lock_dir`.
- No resolution audit record was committed to `recovery_archive/`.
- The method raised an exception to the operator, but the lock directory was left completely clean.
- A subsequent writer calling `lock.acquire()` observed 0 unresolved recovery artifacts, 0 active lock files, and acquired writer admission without any audit trail of the prior failure or human resolution.

This constituted a **High-Severity Recovery Transaction Blocker**.

---

## 2. Hardened 4-Phase Recovery Transaction Protocol

To guarantee strict transactional durability and prevent premature writer admission, `resolve_recovery_state()` implements a hardened 4-phase protocol executing entirely inside the OS-level `CoordinationLock` critical section:

### Phase 1: Durable Recovery Intent & Hold Establishment (Pre-Relocation)
Before moving any existing artifact, the method establishes a durable hold marker:
- **File Name:** `.{lock_filename}.recovery_in_progress_{resolution_id}`
- **Pattern Matching:** Included in `SingleWriterLock.get_unresolved_recovery_artifacts()` via `*{prefix_pattern}*.recovery_in_progress_*`.
- **Atomic Creation:** Written to a temporary file (`.tmp_...`) using `os.open` with `O_CREAT | O_WRONLY | O_EXCL | O_BINARY`, written with `os.write`, flushed with `os.fsync`, and atomically promoted via `os.replace`.
- **Content:** JSON metadata recording `resolution_id`, `operator`, `reason`, `unresolved_artifacts`, `timestamp`, and `pid`.
- **Guaranteed Invariant:** If the process terminates, crashes, or raises an error at any point after Phase 1, the hold marker remains in `lock_dir`, ensuring any future `acquire()` fails closed with `UnresolvedRecoveryStateError`.

### Phase 2: Forensic Archival of Unresolved Artifacts
For each artifact identified in Phase 1 (strictly excluding the hold marker):
- Captures physical byte size and streaming SHA-256 digest.
- Atomically renames to `target_archive / f"archived_{art.name}_{resolution_id}"`.
- Records archival metadata.
- If archival of any artifact fails, raises `LockError` while preserving the Phase 1 hold marker on disk.

### Phase 3: Resolution Audit Record Commitment & Readback Verification
The audit resolution record is durably committed:
- **Payload:** Structured JSON containing `resolution_id`, UTC timestamp, operator ID, justification reason, directory paths, resolved count, and full artifact metadata array (paths, sizes, SHA-256).
- **Atomic Persistence:** Written to `.tmp_...` in `target_archive` with `O_BINARY`, flushed with `os.fsync`, and atomically replaced to `recovery_resolution_{resolution_id}.json`.
- **Readback Verification:** Directly reads back the written bytes from disk and asserts an exact byte-for-byte match with `record_bytes`.
- **Failure Defense:** If write, fsync, atomic replace, or readback verification fails:
  - Cleans up the partial `.tmp` file.
  - Atomically renames the hold marker to permanent `.{lock_filename}.recovery_required_{resolution_id}`.
  - Raises `LockError(f"Failed to commit recovery resolution audit record: ... Admission guard preserved ... FAIL_CLOSED — MANUAL_RECOVERY_REQUIRED")`.

### Phase 4: Verified Hold Removal
Only after Phase 3 completes with full byte-level readback verification:
- Removes the temporary hold marker via `hold_file.unlink()`.
- If unlinking fails with an OS-level error, raises `LockError` preserving the file, so admission remains blocked until operator intervention.
- Returns the verified resolution summary dictionary.

---

## 3. Concurrency, Serialization & Idempotency Guarantees

1. **Coordination Lock Serialization:** All operations in `resolve_recovery_state()` execute within `with self._coord_lock:`, ensuring complete mutual exclusion with concurrent `acquire()`, `release()`, and `break_stale_lock()` attempts across processes on the same host.
2. **Idempotency on Clean State:** If `get_unresolved_recovery_artifacts()` returns an empty list, the method returns `{"resolved": True, "count": 0}` immediately without writing any files or mutating the filesystem.
3. **Retry Capability After Failure:** If a recovery operation fails at Phase 2 or Phase 3, the hold marker (or renamed `recovery_required` marker) remains in `lock_dir`. On subsequent invocation of `resolve_recovery_state()`, the new transaction detects the marker as an unresolved artifact, moves it into `target_archive`, and successfully commits a new verified resolution record.

---

## 4. Verification Evidence Matrix (10 Dedicated Negative & Positive Tests)

All 10 test cases are implemented in [`tests/test_t011_post_closure.py`](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/tests/test_t011_post_closure.py) and verified under Windows NTFS:

| Test Identifier | Failure Mode / Invariant Evaluated | Expected Behavior | Result |
|---|---|---|---|
| `test_c1_01_recovery_record_cannot_be_created` | Permission error creating resolution record | Preserves hold marker; writer 2 blocked with `UnresolvedRecoveryStateError` | PASS |
| `test_c1_02_recovery_record_write_interrupted` | Short write on resolution record | Raises `LockError`; hold marker preserved; writer 2 blocked | PASS |
| `test_c1_03_recovery_record_fsync_fails` | `os.fsync` failure on resolution record | Raises `LockError`; hold marker preserved; writer 2 blocked | PASS |
| `test_c1_04_recovery_record_readback_mismatch` | Corrupted byte readback on resolution record | Rejects unverified record; hold marker preserved; writer 2 blocked | PASS |
| `test_c1_05_partial_artifact_archival_fails` | `os.replace` failure during artifact archival | Preserves hold marker; writer 2 blocked | PASS |
| `test_c1_06_retry_after_partially_completed_recovery` | Retry following earlier failed resolution | Archives remaining hold/artifact, commits resolution, admits writer | PASS |
| `test_c1_07_new_writer_denied_until_verified_recovery_commit` | Writer attempts acquire while hold marker exists | Denied immediately with `UnresolvedRecoveryStateError` | PASS |
| `test_c1_08_successful_verified_recovery_permits_next_writer` | Full clean recovery lifecycle | Resolution JSON committed; hold unlinked; writer 2 acquires | PASS |
| `test_c1_09_two_cooperative_processes_remain_mutually_exclusive` | Mutual exclusion between concurrent processes | Serialized under `CoordinationLock`; lock contention enforced | PASS |
| `test_c1_10_recovery_requires_explicit_authorization_and_operator` | Missing authorization, empty operator, empty reason | Strictly rejected with `LockError`/`ValueError` without disk writes | PASS |
