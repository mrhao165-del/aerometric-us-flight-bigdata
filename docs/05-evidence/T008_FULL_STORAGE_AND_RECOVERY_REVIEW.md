# T008 FULL STORAGE & RECOVERY REVIEW

**Document ID:** `T008_FULL_STORAGE_AND_RECOVERY_REVIEW`  
**Parent Task:** `T-008 — Data Quality, Disjoint Row Accounting & Quarantine Engine`  
**Parent Gate:** `G4`  
**Classification:** `STORAGE_SAFETY_AND_DISASTER_RECOVERY_REVIEW`  
**Date:** 2026-10-18  

---

## 1. STORAGE ARCHITECTURE & ISOLATION

In accordance with Windows NTFS reliability requirements and repository safety policies (`AGENTS.md`), the storage and execution architecture guarantees:
1. **Raw Source Immutability:** The 9 CSV source files in `data/raw/` are opened strictly in read-only mode (`mode="r"`). No write, append, or truncate operations are ever issued to raw directories.
2. **Scratch Isolation:** PySpark local scratch directories (`spark.local.dir`) and Python temporary directories (`tempfile.TemporaryDirectory`) are configured outside the repository or in gitignored scratch paths.
3. **Partition Immutability:** Curated Parquet outputs and forensic quarantine files are written to versioned, immutable run directories (`data/curated/runs/{run_id}/` and `data/forensic/runs/{run_id}/`).
4. **Pointer Switching:** The `latest` pointer is updated atomically only after all accounting balances and manifest signatures pass validation.

---

## 2. CONCURRENCY & RECOVERY MECHANISMS

1. **SingleWriterLock:** NTFS lockfile protocol prevents concurrent conflicting writes to the same run identifier or publication directory.
2. **Crash Recovery & Rollback:**
   - If a failure occurs during quality validation or partition publishing, `SafePublisher` triggers fail-closed cleanup, removing partial staged outputs.
   - The preceding `latest` publication pointer remains untouched.
3. **Verification Evidence:**
   - Verified by T-007 lock and publisher regression tests (`tests/test_t007_locking.py` and `tests/test_t007_publisher.py`).
