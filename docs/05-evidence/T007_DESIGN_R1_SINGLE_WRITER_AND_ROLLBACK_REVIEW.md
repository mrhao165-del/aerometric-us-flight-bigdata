# T007 DESIGN R1 SINGLE WRITER & ROLLBACK REVIEW — FAIL-CLOSED NTFS LOCKING & FORENSIC SAFETY

**Document ID:** `DOC-T007-DESIGN-R1-06-LOCKING-ROLLBACK`  
**Task ID:** `T-007` (Raw CSV Ingestion Pipeline)  
**Phase:** `DESIGN REMEDIATION (R1)`  
**Gate:** `G4` (`PLANNED / NOT_COMPLETED`)  
**Design Authority:** Storage Reliability Engineer & Systems Architect  
**Governance Baselines:** `ROLLBACK_PLAN.md`, `RISK_REGISTER.md`  

---

## 1. EVALUATION OF SINGLE-WRITER CONCURRENCY ON WINDOWS NTFS

On local Windows developer workstations operating on NTFS filesystems, concurrency control presents distinct operating system challenges:
1. **PID Recycling Hazard:** Windows recycles Process IDs (PIDs) rapidly. A dead pipeline process's PID can be reassigned to an unrelated system process or background service within seconds. Relying solely on `OpenProcess(pid)` liveness without verifying process identity or acquisition tokens creates a severe race hazard.
2. **Access Denied Scenarios:** If another user or elevated service holds a process with the same PID, `OpenProcess` returns `ERROR_ACCESS_DENIED` (5), which does **not** mean the process is dead.
3. **Flawed Automatic Lock Stealing:** The initial T-007 design proposed automatically breaking and quarantining the lock if the file age exceeded 2 hours or if PID checks failed. In a large Big Data ingestion job (e.g. processing 54.7M rows with high I/O wait), a long-running job could easily exceed timeouts, leading to catastrophic concurrent execution and storage corruption!

---

## 2. THE FAIL-CLOSED `PublisherLock` PROTOCOL

To ensure deterministic safety, the single-writer mechanism is re-architected under a strict **Fail-Closed Policy**:

```
                                  [Process Starts]
                                         |
                                         v
                            Attempt Atomic Creation of
                           data/curated/.publisher.lock
                             (O_CREAT | O_EXCL | O_WRONLY)
                                    /          \
                            SUCCESS /            \ FileExistsError
                                   v              v
                           [Lock Acquired]   Read Lock Metadata
                                  |          (run_id, pid, token, time)
                                  v               |
                         Execute Ingestion        v
                                  |         Is PID active & token matches?
                                  v              /          \
                         SafePublisher.publish  /            \
                                  |        YES /              \ NO / UNCERTAIN
                                  v           v                v
                            Release Lock   Active Contention   CANNOT PROVE DEAD!
                           (Unlink file)   Fail-Fast Abort    FAIL-CLOSED ABORT!
                                          (PublicationError) (Requires Operator Review)
```

### 2.1. Lock File Metadata Payload
```json
{
  "lock_version": "1.1",
  "run_id": "run_20261017_150000_f9a2",
  "pid": 18240,
  "hostname": "DESKTOP-HEIKAPU",
  "process_create_time_utc": "2026-10-17T08:00:12Z",
  "lock_acquired_at_utc": "2026-10-17T08:00:15Z",
  "heartbeat_at_utc": "2026-10-17T08:15:00Z",
  "auth_token": "a8f3b2c1d9e4726b",
  "pipeline_task": "T-007"
}
```

### 2.2. Strict Fail-Closed Lock Resolution Rules
1. **Atomic Creation:** Lock acquisition utilizes operating system primitive `os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)`. If the lock file exists, acquisition fails immediately at the kernel level without race windows.
2. **Owner Identity Verification:** The lock holder records `process_create_time_utc` and a unique cryptographic `auth_token` alongside its PID. This completely eliminates the PID recycling hazard.
3. **Prohibition of Automatic Lock Stealing:**
   > [!IMPORTANT]
   > The pipeline **MUST NEVER automatically delete or steal an active lock** merely because a timeout elapsed or `OpenProcess` returned `Access Denied`!
4. **Deterministic Fail-Fast:** If `.publisher.lock` exists and cannot be definitively proven to belong to a terminated, non-recycled process by the same user, the pipeline **halts immediately** with `PublicationContentionError`. An operator must manually inspect the lock file, verify process status, and remove the lock before restarting.

---

## 3. NON-DESTRUCTIVE ROLLBACK & FORENSIC ARTIFACT PRESERVATION

In accordance with `AGENTS.md` and `ROLLBACK_PLAN.md`, all failure handling must be completely non-destructive:

### 3.1. Staging Failure Preservation (No Data Wiping)
If an unhandled exception or DC-11 row mismatch occurs during ingestion:
1. **Pointer Protection:** The pointer `data/curated/latest_run_id.txt` is **never touched**. Downstream readers continue accessing the previous valid run without disruption.
2. **Forensic Quarantine:** The pipeline **does not delete** the staging directory! Deleting staging would destroy the forensic evidence needed to diagnose the failure. Instead, the staging directory is renamed to:
   `data/staging/{run_id}_FAILED_FORENSIC/`
   where engineers can inspect partial parquet parts, corrupt CSV lines, and executor logs.
3. **Lock Release:** In Python, `PublisherLock.__exit__` verifies the `auth_token` matches before unlinking `.publisher.lock`, ensuring a crashed process releases only its own lock.

### 3.2. Git Rollback Command Disambiguation
The initial T-007 design contained an improper `git revert <sha> -m` command. Per Git specification:
- The `-m` (mainline) flag is valid **only for merge commits**. Applying `-m` to a standard linear commit causes `fatal: commit is not a merge`.
- **Correct Non-Destructive Git Rollback:**
  ```bash
  # Standard commit rollback to baseline commit 859ae3874080:
  git revert <commit_sha> --no-edit
  # Or inspect working tree:
  git status --porcelain
  ```

---

## 4. REALISTIC RELIABILITY BOUNDARIES (NO UNSUPPORTED CLAIMS)

Engineering integrity requires acknowledging that no software mechanism can guarantee "absolute zero-data-loss" against sudden power outages, OS kernel panics, or hardware controller failures. The storage architecture implements **defense-in-depth**:
- Staging writes are fully isolated before promotion.
- `shutil.copytree` is followed by 100% byte-by-byte and SHA-256 verification against staging inventory.
- Pointer file updates use atomic replacement (`os.replace`) with filesystem flush (`os.fsync`).
- All failure paths fail-closed rather than risk silent corruption.

---

## 5. SINGLE-WRITER & ROLLBACK REVIEW VERDICT

The single-writer locking and rollback design has been fully re-engineered to be fail-closed, eliminating PID recycling risks and guaranteeing non-destructive forensic artifact preservation.

**LOCKING & ROLLBACK REVIEW VERDICT: FAIL-CLOSED & NON-DESTRUCTIVE.**
