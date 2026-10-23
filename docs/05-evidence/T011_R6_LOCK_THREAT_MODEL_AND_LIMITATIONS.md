# T011-R6 Lock Threat Model, Enforceable Guarantees & Residual Limitations

**Project:** US Flight Performance Analysis 2016–2024  
**Task:** T-011 R6 — Controlled Final Lock Safety Closure  
**Parent Gate:** G5 — `IN_PROGRESS`  
**Downstream Gate:** G6 — `NOT_STARTED / BLOCKED` (`G2-EXC-001` Hard Stop)  
**Governance Invariant:** Honest Security Boundaries & Fail-Closed Protocols  

---

## 1. Threat Model & Security Boundaries

In accordance with Master Prompt T011-R6 Section 5, we avoid unrealistic claims of universal immunity against arbitrary processes with full filesystem write privileges. We establish explicit, enforceable boundaries:

```
+-----------------------------------------------------------------------------+
|                          PIPELINE LOCK THREAT MODEL                          |
+-----------------------------------------------------------------------------+
|                                                                             |
|  [SCOPE 1: COOPERATIVE PIPELINE WRITERS]                                     |
|  - All compliant pipeline tasks (T-007, T-010, T-011, T-012..T-014).        |
|  - Mechanism: CoordinationLock (kernel byte lock) + Atomic O_CREAT|O_EXCL.  |
|  - Guarantee: 100% Strict Mutual Exclusion & Serialization. No collision.   |
|                                                                             |
|  [SCOPE 2: LOCAL OUT-OF-BAND PROCESSES (DURING ACTIVE ACQUISITION)]          |
|  - Non-cooperative processes attempting file overwrite/deletion on NTFS.    |
|  - Mechanism: OS Held File Descriptor (exclusive share mode).                |
|  - Guarantee: Windows Kernel physically blocks unlink/rename/replace.       |
|                                                                             |
|  [SCOPE 3: OUT-OF-BAND PROCESSES (DURING RELEASE OR RECOVERY)]              |
|  - Rogue external process swapping files while writer is in release/break.  |
|  - Mechanism: Inode identity tracking, atomic rename, forensic quarantine.  |
|  - Guarantee: Replacement files NEVER deleted; multi-actor collisions trigger|
|               explicit FAIL-CLOSED — MANUAL_RECOVERY_REQUIRED.               |
|                                                                             |
|  [OUTSIDE THREAT MODEL / RESIDUAL LIMITATIONS]                              |
|  - Root/Administrator forcefully revoking ACLs, unmounting filesystem,      |
|    or terminating coordination locks out-of-band.                           |
|  - Guarantee: Fail-closed halting; requires operator manual recovery.       |
|                                                                             |
+-----------------------------------------------------------------------------+
```

---

## 2. Enforceable Guarantees

1. **G-01 (Cooperative Exclusivity):** No two compliant pipeline tasks can simultaneously hold the single-writer lock. If writer A holds the lock, writer B receives `LockContentionError`.
2. **G-02 (Replacement Lock Preservation):** Under no circumstances does `acquire()`, `release()`, or `break_stale_lock()` delete an unexpected replacement lock file belonging to another owner.
3. **G-03 (Identity-Aware Cleanup):** On acquisition failure, cleanup verifies the physical file reference (`st_ino, st_dev`). If the canonical path was swapped, the replacement file is left untouched.
4. **G-04 (No Automatic Stealing of Active PIDs):** If a lock file belongs to an active PID, automatic breaking is strictly prohibited.
5. **G-05 (Deterministic Rollback & Quarantine):** In multi-actor collision scenarios, files are quarantined to `.quarantine_<uuid>` to preserve forensic evidence, and execution halts.

---

## 3. Residual Limitations & Administrative Recovery Policy

1. **Limitation L-LOCK-01 (Out-of-Band Path Mutations):**
   - If an uncooperative external process with direct NTFS directory write permissions alters the lock file while a writer is executing release or recovery, the lock authority is declared compromised.
   - **Resolution:** Automatic recovery is disabled. Operator intervention under established writer quiescence is required.
2. **Limitation L-LOCK-02 (Manual Stale Lock Recovery Requires Quiescence):**
   - Breaking a stale lock (`break_stale_lock(force=True)`) requires verified process death (`PidLivenessStatus.PROCESS_DEAD`) on the local host. If the process is alive or status cannot be verified, recovery is refused.
   - **Administrative Prerequisite:** Operator must establish complete writer quiescence before invoking administrative recovery tools.
3. **Limitation L-LOCK-03 (Remote Host Stale Locks):**
   - If a lock file indicates ownership by a different hostname, local liveness cannot be safely determined.
   - **Resolution:** Automatic breaking across hosts is strictly prohibited (`FAIL_CLOSED`).
