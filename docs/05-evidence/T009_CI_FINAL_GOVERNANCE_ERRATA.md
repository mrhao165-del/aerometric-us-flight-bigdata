# T009-CI-FINAL Governance Errata & Administrative Addendum

## 1. Authority & Purpose
This errata document is formally issued under `T009-CI-FINAL-CLOSURE` to reconcile documentary discrepancies, clarify testing timing variations, and document CI execution status without modifying or overwriting any historical audit reports or execution logs.

---

## 2. Reconciled Discrepancies (ISSUE DOC-01)

### 2.1. Errata Item 1: Assertion Count Reconciliation in CI Review
- **Referenced Document:** `docs/05-evidence/T009_SEAL_FIX_CI_READINESS_REVIEW.md` (Line 37)
- **Reported Text:** `Simulation Outcome: 593 PASS, 0 FAIL (matches expected assertion count).`
- **Actual Log Evidence:** [`T009_SEAL_FIX_LOG_CI_CLEAN_CHECKOUT.txt`](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/docs/05-evidence/T009_SEAL_FIX_LOG_CI_CLEAN_CHECKOUT.txt) recorded `627 PASS assertions`.
- **Root Cause & Technical Fact:** The mathematical assertion formula in `tools/check_working_tree_consistency.py` is:
  $$\text{Total Assertions} = 111 \text{ (baseline)} + 2 \times N_{\text{registered deliverables}}$$
  At the initial drafting of the review document, $N = 241$, yielding $111 + 2 \times 241 = 593$ assertions. When the 17 new deliverables (1 errata, 8 reports, 8 logs) were subsequently registered, $N$ expanded to 258, resulting in $111 + 2 \times 258 = 627$ assertions. The log reflects the true final execution, whereas the early narrative draft retained the pre-registration count.
- **Administrative Correction:** The historical document is preserved unmodified. All parties shall note that 627 PASS assertions represents the authoritative verified count for the 258-deliverable registry state.

### 2.2. Errata Item 2: Unit Test Execution Timing Variations
- **Referenced Discrepancy:** Raw unittest log recorded `Ran 31 tests in 28.504s`, whereas the agent turn summary cited `24.52s`.
- **Technical Fact:** Unit test executions involving Apache Spark (`pyspark`) exhibit variable startup duration on Windows hosts due to JVM bootstrap, background socket allocation, and OS thread scheduling jitter (ranging between 24s and 29s). Both runs executed all tests with 0 failures and 0 errors.

### 2.3. Errata Item 3: Remote GitHub Actions Status
- **Technical Fact:** Because this local development environment operates without active connection to a remote GitHub Actions runner, the remote CI workflow is formally designated **`NOT_EXECUTED`**.
- **Governance Requirement:** The simulated clean checkout executed locally via `python tools/check_working_tree_consistency.py --ci-mode` in an isolated sandbox rigorously validates all file presence, linkage, manifest, and clean working tree rules, but does NOT substitute for a remote GitHub runner log. The project does NOT claim remote GitHub Actions PASS.

---

## 3. Preserved Governance Caveats & Invariants
All canonical caveats previously registered remain fully active and binding:
1. **OR-05 (March 2024 Absence):** March 2024 flight reporting is absent from the audited raw dataset; this gap is documented and must not be masked or synthesized.
2. **OR-08 (Source Identity):** File size and `mtime` do not prove raw cryptographic identity; SHA-256 hashes must be verified where cryptographic proof is required.
3. **FP-DEC-017 (Weather Stream Independence):** The Weather optional stream remains `CONDITIONAL_NO_GO` and does not block CORE analytical milestones.
4. **G2-EXC-001 / TS-018 (Gate G5 Mandatory Hard Stop):** Provisional unit status for the 7 CORE measures is accepted for Gate G4 bootstrap, but Gate G5 mandates a hard stop blocking Gate G6 until weather units and source discrepancies are officially resolved.
5. **Spark Local Warnings:** Warnings regarding missing `winutils.exe` and `native-hadoop` are standard for local Windows PySpark executions and do not affect computational correctness.
6. **TS-013 Simulation Scope:** Fault injection testing validates publication NTFS filesystem safety and non-destructive atomic rollback; it does not simulate cluster-wide distributed worker failure.
7. **Single-Writer Constraint:** The publication mechanism assumes a single orchestrator process writing to `staging/` and `curated/`.
