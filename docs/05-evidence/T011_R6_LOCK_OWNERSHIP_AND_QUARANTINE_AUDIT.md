# T011-R6 Lock Ownership Continuity & Quarantine Behavior Audit

**Project:** US Flight Performance Analysis 2016–2024  
**Task:** T-011 R6 — Controlled Final Lock Safety Closure  
**Finding Reference:** R6-F02 (Quarantine Is Not Equivalent to Ownership Preservation)  
**Parent Gate:** G5 — `IN_PROGRESS`  
**Severity:** HIGH  
**Status:** AUDITED, FORMALIZED, AND BOUNDED  

---

## 1. Problem Analysis: The Three-Owner Anomaly

The independent auditor identified the following scenario in R5:
1. Owner A acquires the lock and subsequently begins `release()`.
2. A non-cooperative out-of-band actor replaces the lock file at the canonical path with Owner B's lock file.
3. Owner A executes atomic rename: `os.rename(canonical, staging_del)`. Owner B's lock file is moved to staging.
4. Yet another out-of-band actor creates Owner C's lock file at the canonical path.
5. Owner A reads staging metadata, finds `staging_meta.owner_token != self.owner_token` (token belongs to B).
6. Owner A attempts to restore B's lock to the canonical path, but finds the canonical path occupied by C (`self.lock_file_path.exists()` is True).
7. In R5, Owner A moved B's file from staging to quarantine (`.quarantine_<uuid>`).

### The Implication
While Owner B's file content was preserved on disk in the quarantine directory, **Owner B lost its authoritative canonical lock file**. If Owner B believed it held an active lock, its canonical position was displaced by C.

---

## 2. Threat Model Boundaries & Enforceable Guarantees

In accordance with Master Prompt T011-R6 Section 5, we do not claim impossible user-space protection against arbitrary processes with full write/delete permissions. We explicitly define the boundaries:

### Scope 1: Cooperative Writers (Fully Enforced & Guaranteed)
- **Definition:** All compliant pipeline processes that utilize `SingleWriterLock` and respect the project protocol.
- **Enforcement Mechanism:**
  - All cooperative writers MUST acquire the OS-level `CoordinationLock` (`.pipeline.lock.coord`) using `msvcrt.locking(LK_LOCK)` on Windows NTFS / `fcntl.flock(LOCK_EX)` on POSIX before performing any acquire, release, or recovery operation.
  - While Owner A is releasing its lock inside `CoordinationLock`, no cooperative writer can acquire the lock or create a replacement file.
  - Therefore, **the three-owner replacement sequence is physically impossible among cooperative writers**.

### Scope 2: Out-of-Band Actors (Bounded & Fail-Closed)
- **Definition:** External tools, scripts, or OS users that directly modify, overwrite, or delete files in the lock directory without acquiring `CoordinationLock`.
- **Enforcement Mechanism:**
  - **OS-Authoritative Held Lock:** During active acquisition, `SingleWriterLock` retains the open file descriptor (`self._fd`). On Windows NTFS, open file handles without `FILE_SHARE_DELETE` physically block deletion, renaming, or replacement by any external process (WinError 5 / WinError 32).
  - **Fail-Closed on Competing Replacement:** If an out-of-band actor somehow replaces the file during release or recovery:
    - If the canonical path is re-occupied by another actor, the system strictly halts publication, refuses to silently drop or overwrite locks, preserves forensic quarantine records, and raises `LockOwnerMismatchError` declaring `FAIL_CLOSED — MANUAL_RECOVERY_REQUIRED`.
    - Manual administrative recovery under verified writer quiescence is strictly mandated before any new run may proceed.

---

## 3. Mandatory Audit Verdict

1. **Quarantine Role:** Quarantine is a **forensic preservation mechanism for compromised lock state**, NOT a substitute for active lock ownership.
2. **Explicit Fail-Closed Policy:** Whenever quarantine occurs due to concurrent canonical re-occupation, the operation is an explicit failure requiring operator intervention. It is never treated as a successful release.
3. **Quiescence Prerequisite:** Automatic stale-lock breaking remains strictly prohibited on active or ambiguous PIDs.
