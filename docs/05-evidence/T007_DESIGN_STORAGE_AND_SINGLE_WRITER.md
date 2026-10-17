# T007 DESIGN STORAGE AND SINGLE WRITER — NTFS CONCURRENCY CONTROL & SAFE PUBLICATION

**Document ID:** `DOC-T007-DESIGN-05-STORAGE-LOCKING`  
**Task ID:** `T-007` (Raw CSV Ingestion Pipeline)  
**Phase:** `DESIGN ONLY`  
**Gate:** `G4` (`PLANNED / NOT_COMPLETED`)  
**Design Authority:** Senior Big Data Architect & Storage Systems Engineer  
**Reference Implementation:** `src/flight_pipeline/storage/publication.py` (`SafePublisher`)  

---

## 1. STORAGE CONCURRENCY PROBLEM STATEMENT ON WINDOWS NTFS

On local Windows developer workstations operating on NTFS filesystems:
1. **Lack of Native POSIX Advisory Locking:** Standard POSIX advisory locking (`fcntl.flock`) is unavailable on Windows. File sharing modes and locks in Windows can cause unpredictable `PermissionError: [WinError 32] The process cannot access the file because it is being used by another process` if file handles remain open.
2. **Multi-Process Race Hazards:** If two ingestion jobs, test runners, or CI agents execute concurrently:
   - They could write to colliding staging paths.
   - They could attempt simultaneous promotions to `data/curated/runs/{run_id}/`.
   - They could produce race conditions when updating the singleton pointer `data/curated/latest_run_id.txt`.
3. **Requirement:** A robust, testable, single-writer operational mechanism that operates natively on Windows, detects dead processes, handles stale locks safely, and integrates seamlessly with `SafePublisher`.

---

## 2. SINGLE-WRITER LOCK SPECIFICATION (`PublisherLock`)

The proposed concurrency enforcement mechanism is implemented via an atomic filesystem lock file:
`data/curated/.publisher.lock`

### 2.1. Lock File Lifecycle & Protocol
```
                                 [Process Starts]
                                        |
                                        v
                            Check .publisher.lock exists?
                                   /         \
                              YES /           \ NO
                                 v             v
                    Read Lock Metadata     Atomic Create (O_CREAT | O_EXCL)
                    (PID, run_id, time)        |
                         |                     v
             Is PID alive on Windows?     [Lock Acquired]
                 /            \                |
            YES /              \ NO            v
               v                v       Execute Ingestion & Publish
        Contention!       Is lock stale?       |
      Raise Error         (age > 2 hours)      v
     (FAIL-FAST)            /        \    Atomic Pointer Update
                       YES /          \ NO     |
                          v            v       v
                   Quarantine Lock   Wait/Abort [Release Lock]
                  & Acquire Anew
```

### 2.2. Atomic Lock File Creation
On Windows NTFS, atomic file creation without race conditions is achieved using the operating system flags:
```python
flags = os.O_CREAT | os.O_EXCL | os.O_WRONLY
fd = os.open(lock_path, flags, 0o644)
```
If another process creates the lock file concurrently, `os.open` raises `FileExistsError` atomically at the filesystem kernel level.

### 2.3. Lock File Payload Structure
The lock file records comprehensive diagnostic metadata in UTF-8 JSON:
```json
{
  "lock_version": "1.0",
  "run_id": "run_20261017_130000_c8f1",
  "pid": 14280,
  "hostname": "DESKTOP-HEIKAPU",
  "acquired_at_utc": "2026-10-17T06:00:00Z",
  "heartbeat_at_utc": "2026-10-17T06:05:00Z",
  "pipeline_task": "T-007"
}
```

### 2.4. Dead Process & Stale Lock Detection on Windows
If `FileExistsError` is encountered, the lock acquirer inspects the existing lock metadata:
1. **Liveness Check on Windows:**
   The acquirer queries the process status via `ctypes.windll.kernel32.OpenProcess`:
   ```python
   import ctypes
   PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
   SYNCHRONIZE = 0x00100000
   
   def is_pid_alive_windows(pid: int) -> bool:
       if pid <= 0:
           return False
       handle = ctypes.windll.kernel32.OpenProcess(
           PROCESS_QUERY_LIMITED_INFORMATION | SYNCHRONIZE, False, pid
       )
       if not handle:
           return False
       ctypes.windll.kernel32.CloseHandle(handle)
       return True
   ```
2. **Stale Lock Timeout:**
   If the PID is confirmed dead (or if the lock timestamp is older than `LOCK_STALE_TIMEOUT_SECONDS = 7200` [2 hours] and the PID cannot be verified):
   - The stale lock is moved to `data/curated/stale_locks/{run_id}_{timestamp}.lock` for forensic analysis.
   - An audit warning is logged.
   - The acquirer retries atomic acquisition.
3. **Active Contention (Fail-Fast):**
   If the PID is alive and active:
   - The process immediately aborts, raising `PublicationContentionError`:
     `"Another ingestion pipeline is currently executing (run_id=..., pid=...). Terminating to prevent storage corruption."`

---

## 3. INTEGRATION WITH `SafePublisher` 7-STEP PUBLICATION

Once ingestion finishes writing to staging, the pipeline transfers execution to T-009's `SafePublisher`:

```
Staging Path: data/staging/{run_id}/
Curated Destination: data/curated/runs/{run_id}/
Pointer File: data/curated/latest_run_id.txt
```

### 3.1. The 7-Step Atomic Publishing Sequence
1. **Step 1 (Preflight Validation):**
   - Confirm staging directory exists and is non-empty.
   - Verify every Parquet file contains valid `PAR1` magic bytes at offset 0 and EOF - 4 (`is_valid_parquet_file`).
   - Confirm destination `data/curated/runs/{run_id}/` does not already exist (immutability rule).
2. **Step 2 (Row Accounting Audit):**
   - Confirm `RunManifest` row balance matches DC-11 ($N_{\text{raw}} = N_{\text{accepted}} + N_{\text{quarantined}} + N_{\text{rejected}}$).
3. **Step 3 (Directory Promotion):**
   - Atomically move/rename `data/staging/{run_id}/` to `data/curated/runs/{run_id}/`.
4. **Step 4 (Part-File Hashes & Manifest Write):**
   - Stream SHA-256 for all curated Parquet part files.
   - Write `data/curated/runs/{run_id}/run_manifest.json`.
5. **Step 5 (Atomic Pointer Switch):**
   - Write new `run_id` to temporary file `data/curated/latest_run_id.txt.tmp`.
   - Flush and sync to disk (`os.fsync`).
   - Replace pointer atomically via `os.replace("latest_run_id.txt.tmp", "latest_run_id.txt")`.
6. **Step 6 (Latest Manifest Copy):**
   - Atomically update `data/curated/LATEST_RUN_MANIFEST.json`.
7. **Step 7 (Lock Release & Cleanup):**
   - Remove `.publisher.lock`.

---

## 4. FORENSIC ARTIFACT PRESERVATION ON FAILURE

If an unhandled exception or crash occurs during CSV parsing or staging:
1. **Pointer Protection:** The pointer `latest_run_id.txt` is **never touched**. Downstream readers continue reading the previous valid, signed-off run without disruption.
2. **Staging Quarantine:** The staging folder `data/staging/{run_id}/` is renamed to `data/staging/{run_id}_FAILED_ABORTED/` and retained for forensic post-mortem investigation.
3. **Lock Release:** In Python, the `PublisherLock` context manager guarantees lock release in its `finally:` block:
   ```python
   with PublisherLock(curated_dir, run_id):
       pipeline.execute()
   ```

---

## 5. STORAGE & LOCKING DESIGN VERDICT

The proposed Windows NTFS single-writer lock and atomic promotion architecture guarantees zero-data-loss, fail-fast concurrency protection, and deterministic recovery.

**STORAGE & LOCKING DESIGN VERDICT: FULLY SPECIFIED & APPROVED.**
