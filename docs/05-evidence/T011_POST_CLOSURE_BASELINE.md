# T011 POST-CLOSURE AUTHORITATIVE BASELINE & DEFECT RECONCILIATION

**Project:** US Flight Performance Analysis 2016–2024  
**Task:** T011-R6-POST-CLOSURE  
**Parent Gate:** Gate G5 — `IN_PROGRESS` (Downstream Gate G6: `NOT_STARTED / BLOCKED` under `G2-EXC-001`)  
**Previous Package Baseline:** `T011_R6_PRESIGNOFF_CLOSURE_REVIEW_PACKAGE.zip` (SHA-256: `104870d5ac626467f4a314c397a890e742c698b8a2b94da443e7266355736615`)  
**Role:** Principal Reliability Engineer, Windows NTFS Concurrency Engineer, Independent QA & Evidence Auditor  
**Authority:** Project Lead is the exclusive authority for official Gate and Task signoff.

---

## 1. Authoritative Baseline Status & Invariant Preservation

| Component | Status | Governing Invariant / Policy |
|---|---|---|
| Gate G2 | PASS | Core schema, dictionary, nullable int64, regex, UTC timestamp |
| Gate G3 | PASS | 7 provisional unit statuses, KPI specs, test plan, architecture |
| Gate G4 | PASS (CONTROLLED) | Staging Parquet created; immutable raw CSV boundary (15,196,366,173 bytes preserved) |
| Task T-010 | PASS / COMPLETED (CONTROLLED) | 50 Parquet files verified; zero mutation on raw source CSVs |
| Task T-011 | PENDING HUMAN SIGNOFF | Controlled implementation and lock safety closure awaiting Project Lead acceptance |
| Gate G5 | IN_PROGRESS | Authoritative KPI engine & parity validation |
| Gate G6 | NOT_STARTED / BLOCKED | Mandatory hard stop under `G2-EXC-001` (full 54.7M flight dataset run strictly prohibited) |
| TS-018 BTS Parity | PENDING | Authentic BTS TranStats parity pending authorized download |
| Exception `G2-EXC-001` | ACTIVE | 7 CORE numeric measures provisionally expressed in minutes |
| Defect `OR-05` | OPEN_QUALITY_DEFECT | Controlled staging discrepancy tracked |
| Defect `OR-08` | IDENTITY_UNVERIFIED | Size/mtime source signature trust boundary |
| Weather `FP-DEC-017` | CONDITIONAL_NO_GO | Weather enrichment pipeline decoupled and blocked from gating CORE |
| Proposed Decision `FP-DEC-PROP-018` | PROPOSED | Separation of publication immutability (`success=True`) from local lock recovery |

---

## 2. Git Baseline and Exact Source Hashes (Pre-Remediation)

- **Git Commit:** `bc4f03fb8ccd6c0b2455af3fcb2b1b98fa39d632`
- **Git Date:** `Sun Oct 18 14:35:06 2026 +0700`
- **Git Subject:** `docs(t007): record official human signoff, documentation errata, and T008 handoff`

### Pre-Remediation Source Hashes:
- `src/flight_pipeline/storage/locking.py`: 43,699 bytes | SHA-256: `6fe0fb8ea92c906660161427f71587d60f54ddde9db1450259b34208a0fc40e8`
- `tests/test_t011_r6_counterexamples.py`: 20,034 bytes | SHA-256: `138c2089f2a0375a0df47a469a918a385f0efcba4da70059aa7538c8c7cfd85a`
- `tests/test_t011_r6_presignoff_closure.py`: 28,645 bytes | SHA-256: `41dc738d22791443eb3ba13ce60752495bb391b15c99e19c018a360a02d84793`

---

## 3. Targeted Findings & Independent Reproduction Summary

### Finding C1: Recovery audit failure incorrectly clears writer admission guard (HIGH)
- **Defect Description:** In `SingleWriterLock.resolve_recovery_state()`, blocking artifacts were moved into `recovery_archive/` before writing the resolution record (`recovery_resolution_<id>.json`). When writing the resolution record failed with an `OSError`, an exception was raised, but no unresolved artifacts remained in `lock_dir`, allowing a subsequent writer to acquire the lock without a committed recovery audit record.
- **Deterministic Reproduction:**
  ```text
  === REPRODUCING FINDING C1 ===
  Initial acquisition blocked: True
  Recovery raised expected OSError: Disk failure during recovery audit write
  Remaining unresolved artifacts: 0
  Archived artifacts: 2
  Recovery audit records: 0
  Next writer admitted: True
  FINDING C1 REPRODUCED: True
  ```

### Finding C2: Incident persistence failure diagnostic missing from normal context exit (MEDIUM)
- **Defect Description:** In `SingleWriterLock.__exit__()`, when the `with` block completed normally (`exc_val is None`), but `release()` failed and incident persistence also failed, `__exit__` raised `rel_err` directly without surfacing the computed `INCIDENT_PERSISTENCE_FAILED` diagnostic.
- **Deterministic Reproduction:**
  ```text
  === REPRODUCING FINDING C2 ===
  Caught exception type: LockError
  Exception message: Injected unlink PermissionError during release
  Contains INCIDENT_PERSISTENCE_FAILED: False
  FINDING C2 REPRODUCED: True
  ```

### Finding C3: Regression report lists incorrect test names (MEDIUM — EVIDENCE TRACEABILITY)
- **Defect Description:** In `docs/05-evidence/T011_R6_PRESIGNOFF_CLOSURE_REGRESSION.md`, the 20 test names listed in Section 2 did not match the physical function names implemented in `tests/test_t011_r6_presignoff_closure.py`.
- **Deterministic Reproduction:**
  ```text
  === REPRODUCING FINDING C3 ===
  Report lists wrong name: True
  Module has actual name: True
  Module lacks reported name: True
  FINDING C3 REPRODUCED: True
  ```
