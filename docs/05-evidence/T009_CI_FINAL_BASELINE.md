# T009-CI-FINAL Baseline & Safety Audit Report

## 1. Executive Summary
- **Task ID:** `T009-CI-FINAL-CLOSURE`
- **Gate:** Gate G4 (`PLANNED / NOT_COMPLETED`)
- **Authority Mode:** `MINIMAL_TARGETED_FIX + INDEPENDENT VERIFICATION`
- **Starting Git Baseline:** Commit [`7f8c088e161022bb918dbdb3e9bc853f6e533ccd`](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1) on branch `master`
- **Working Tree Integrity:** Confirmed clean before any changes.

---

## 2. Mandatory Document Inspection
Before initiating source edits, direct inspection was conducted across canonical governance and design specifications:
1. `AGENTS.md` (docs-v1.1): Strict prohibition against modifying `data/raw/`, falsifying Spark runs or row counts, self-approving gates, and overwriting historical logs.
2. `docs/02-design/ARCHITECTURE.md` (v1.1): Section 2 NTFS-safe publication order; Section 3 PySpark 3.5.x environment budget.
3. `docs/02-design/DATA_CONTRACT.md`: Canonical 34 columns, row accounting invariants (DC-11/12).
4. `docs/03-quality/TEST_PLAN.md`: Authoritative TS-001 through TS-020 verification matrix.
5. `G2` and `G3` Official Human Signoff Records: Gate G2 and G3 confirmed approved and immutable.
6. All `T009_SEAL_FIX_*` evidence reports and errata.

---

## 3. Discovered Defects Requiring Remediation

### 3.1. ISSUE CI-01 — Windows Scratch Path on Linux
- **Location:** [`src/flight_pipeline/config/spark_config.py`](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/src/flight_pipeline/config/spark_config.py)
- **Defect:** `SparkConfig.scratch_dir` hardcoded to `"D:/Study/Code/Apache/Flight_Analyzt/tmp_spark/"`. On POSIX systems (Linux/macOS), `pathlib.Path("D:/...")` has no drive letter and is parsed as a relative path with the first directory component named `D:`. When `ensure_scratch_dir()` creates directories, a stray folder `D:` is generated inside the active repository working tree. Furthermore, the fallback used `os.environ.get("TEMP", ".")`, which falls back to `"."` (current directory) on Linux where `TEMP` is not typically defined.
- **Risk:** Contaminates clean Git checkouts in CI pipelines and violates clean working-tree invariants.

### 3.2. ISSUE PUB-01 — Initial Pointer Read Exception Handling
- **Location:** [`src/flight_pipeline/storage/publication.py`](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/src/flight_pipeline/storage/publication.py)
- **Defect:** Prior to Step 0, `publish()` calls `previous_pointer = self.get_current_pointer()`. While `get_current_pointer()` retries transient errors, persistent I/O errors or file-lock issues raise an unhandled `OSError`. This would crash the calling pipeline with an unhandled exception before publication validation begins.
- **Risk:** Uncontrolled pipeline crash and absence of structured failure reporting.

### 3.3. ISSUE DOC-01 — Evidence Consistency Variances
- **Discrepancy 1:** `T009_SEAL_FIX_CI_READINESS_REVIEW.md` line 37 cited 593 PASS assertions from an early draft, whereas the actual execution log recorded 627 PASS assertions following registry deliverable expansion ($111 + 2 \times 258 = 627$).
- **Discrepancy 2:** Unittest execution time varied between raw log (`28.504s`) and agent summary (`24.522s`) due to non-deterministic JVM startup jitter.
- **Discrepancy 3:** Distinction between local clean-checkout simulation (`--ci-mode`) and remote GitHub Actions runners must be formally stated as `NOT_EXECUTED` for remote runners.

---

## 4. Execution Plan
1. Write failing regression tests replicating CI-01 and PUB-01.
2. Apply minimal targeted remediation to `spark_config.py` and `publication.py`.
3. Verify test pass across all unit test modules (37 tests).
4. Run full regression test suite (Spark smoke, contract consistency, deliverable registry, Git exclusion, validator extension).
5. Perform strict clean-checkout simulation executing unit tests *before* consistency checker to verify zero filesystem pollution.
6. Issue formal governance errata and reconcile deliverable register.
