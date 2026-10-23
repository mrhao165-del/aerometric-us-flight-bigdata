# T011-R5 Source Change and Risk Analysis Report

**Project:** US Flight Performance Analysis 2016–2024  
**Task:** T-011 R5 — Lock Safety Closure and Evidence Reconciliation  
**Parent Gate:** G5 — `IN_PROGRESS`  
**Date:** 2026-10-19  

---

## 1. Summary of Source Code Modifications

The modifications in T011-R5 are strictly bounded to two production files and one new test suite:

### 1. `src/flight_pipeline/storage/locking.py`
- **`CoordinationLock` Implementation:**
  - Added OS-level kernel byte locking across processes: `msvcrt.locking(LK_LOCK)` on Windows NTFS and `fcntl.flock(LOCK_EX)` on POSIX.
  - Coupled with in-process `threading.RLock()` for thread-safe reentrancy within the same Python process.
- **`SingleWriterLock` Updates:**
  - Integrated `CoordinationLock` covering the critical sections of `acquire()`, `release()`, and `break_stale_lock()`.
  - Replaced vulnerable direct `Path.unlink()` path deletions in `release()` and `break_stale_lock()` with the **Atomic Isolated File Removal Protocol** (`os.rename` to private `.del_<uuid>` staging, post-move token/PID re-verification, restore/quarantine on mismatch).
  - Explicitly differentiated between unparseable concurrent lock modifications and token/PID mismatches to preserve fail-closed forensic error messages.

### 2. `src/flight_pipeline/kpi/bts_reconciler.py`
- **Strict SHA-256 Hexadecimal Validation:**
  - Added `SHA256_HEX_REGEX = re.compile(r"^[0-9a-fA-F]{64}$")` and `is_valid_sha256_hex(val: Any) -> bool`.
  - Enforced strict 64-character hexadecimal digest validation in both `validate_metadata_format` and `validate_candidate_checksum`.
  - Prohibited non-hex strings (`"z" * 64`) and whitespace from being accepted as matching candidate hashes.

### 3. `tests/test_t011_r5_counterexamples.py`
- Created dedicated test suite with **16** independent regression tests verifying the late-unlink race prevention, multi-process coordination, replacement lock survival, strict hex validation, and physical module inventory.

---

## 2. Invariant & Governance Preservation

1. **Raw Data Immutability:** 0 bytes of raw CSV data in `data/raw/` have been accessed or modified.
2. **Physical Parquet Staging:** Approved T-010 physical Parquet staging remains immutable and untouched.
3. **Core Contracts:** DC-11/DC-12 row accounting, G3-COND-A/B/C safety constraints, and 8 CORE KPI specifications remain completely intact.
4. **Provisional Unit Status:** The 7 CORE continuous measures retain `unit_status = "OFFICIAL_MINUTES_EMPIRICALLY_CONSISTENT_PROVISIONAL"`.
5. **Gate G6 Hard Stop:** Gate G6 remains strictly `NOT_STARTED / BLOCKED` under `G2-EXC-001`.

---

## 3. Risk Assessment Matrix

| Risk ID | Description | Pre-Mitigation Level | Post-Mitigation Level | Mitigation Applied |
| :--- | :--- | :---: | :---: | :--- |
| **R-LOCK-RACE** | Late race replacement between check and unlink deleting new owner's lock | HIGH | NEGLIGIBLE | OS-level `CoordinationLock` + atomic rename-and-verify protocol completely prevents deletion of replacement locks |
| **R-HEX-SPOOF** | Acceptance of non-hex strings as matching SHA-256 hashes | MEDIUM | NEGLIGIBLE | Regex-enforced 64-char hexadecimal validation (`[0-9a-fA-F]{64}`) with whitespace rejection |
| **R-EVID-DISC** | Inconsistent test module counts or scope claims in agent reports | LOW | NEGLIGIBLE | Authoritative superseding errata and exact physical repository inventory reconciliation |
| **R-DEADLOCK** | Deadlock in coordination lock during abrupt worker termination | MEDIUM | NEGLIGIBLE | Windows kernel automatically releases MSVCRT byte locks upon process termination; tested and confirmed |
