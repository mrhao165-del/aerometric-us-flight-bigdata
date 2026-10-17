# T009-SEAL-FIX Deliverable Registry Reconciliation Report

## 1. Executive Summary
This document reconciles all deliverable registrations and explains the mathematical evolution of assertion counts resulting from the addition of `T009_FINAL_GOVERNANCE_ERRATA.md`, the 8 `T009_SEAL_FIX_*.md` reports, and the 8 `T009_SEAL_FIX_LOG_*.txt` logs.

---

## 2. Mathematical Assertion Formula
Under `tools/check_working_tree_consistency.py`, total PASS assertions are computed deterministically:

$$\text{Total Assertions} = 111 \text{ (baseline invariants)} + 2 \times N_{\text{registered\_deliverables}}$$

Where each registered deliverable contributes exactly 2 assertion checks:
1. Metadata schema and enum validity.
2. Exact physical byte size and SHA-256 cryptographic verification.

### Evolution Across Iterations
| Iteration Stage | Deliverables ($N$) | Calculated Assertions ($111 + 2N$) | Reported PASS | Context / Key Additions |
| :--- | :---: | :---: | :---: | :--- |
| **T009-R2 Baseline** | 210 | 531 | 531 | Prior to R3 defect reproductions |
| **T009-R3 Final State** | 227 | 565 | 565 | Final R3 dossier |
| **T009-EXIT Final State** | 241 | 593 | 593 | 7 EXIT reports + 7 EXIT logs |
| **T009-SEAL-FIX State** | **258** | **627** | **627** | +1 Final Errata, +8 SEAL_FIX reports, +8 SEAL_FIX logs |

---

## 3. Deliverable Inventory Changes in SEAL-FIX

### 3.1 Updated Deliverables (4 existing files)
1. `src/flight_pipeline/storage/publication.py`: Updated with streaming hash & Step 6 exception handling.
2. `tests/test_publication_safety.py`: Updated with 4 new regression tests (31 tests total).
3. `tools/check_working_tree_consistency.py`: Updated with `--ci-mode` parameter support.
4. `.github/workflows/ci.yml`: Updated to invoke `--ci-mode`.

### 3.2 New Registered Deliverables (17 new files)
1. `docs/05-evidence/T009_FINAL_GOVERNANCE_ERRATA.md` (`ERRATA_REPORT`)
2. `docs/05-evidence/T009_SEAL_FIX_BASELINE_AND_FINDINGS.md` (`AUDIT_REPORT`)
3. `docs/05-evidence/T009_SEAL_FIX_SOURCE_REMEDIATION.md` (`AUDIT_REPORT`)
4. `docs/05-evidence/T009_SEAL_FIX_POINTER_FAILURE_TESTS.md` (`SYNTHETIC_TEST_REPORT`)
5. `docs/05-evidence/T009_SEAL_FIX_STREAMING_HASH_TESTS.md` (`SYNTHETIC_TEST_REPORT`)
6. `docs/05-evidence/T009_SEAL_FIX_CI_READINESS_REVIEW.md` (`AUDIT_REPORT`)
7. `docs/05-evidence/T009_SEAL_FIX_REGISTRY_RECONCILIATION.md` (`AUDIT_REPORT`)
8. `docs/05-evidence/T009_SEAL_FIX_FINAL_TEST_MATRIX.md` (`AUDIT_REPORT`)
9. `docs/05-evidence/T009_SEAL_FIX_FINAL_VERDICT.md` (`AUDIT_REPORT`)
10. `docs/05-evidence/T009_SEAL_FIX_LOG_UNITTESTS.txt` (`SYNTHETIC_TEST_REPORT`)
11. `docs/05-evidence/T009_SEAL_FIX_LOG_SPARK_SMOKE.txt` (`SYNTHETIC_TEST_REPORT`)
12. `docs/05-evidence/T009_SEAL_FIX_LOG_T006_REGRESSION.txt` (`SYNTHETIC_TEST_REPORT`)
13. `docs/05-evidence/T009_SEAL_FIX_LOG_REGISTRY_REGRESSION.txt` (`SYNTHETIC_TEST_REPORT`)
14. `docs/05-evidence/T009_SEAL_FIX_LOG_GIT_EXCLUSION.txt` (`SYNTHETIC_TEST_REPORT`)
15. `docs/05-evidence/T009_SEAL_FIX_LOG_VALIDATOR_EXTENSION.txt` (`SYNTHETIC_TEST_REPORT`)
16. `docs/05-evidence/T009_SEAL_FIX_LOG_CI_CLEAN_CHECKOUT.txt` (`SYNTHETIC_TEST_REPORT`)
17. `docs/05-evidence/T009_SEAL_FIX_LOG_CONSISTENCY.txt` (`SYNTHETIC_TEST_REPORT`)
