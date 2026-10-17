# T009-R3-EXIT Evidence Registry & Assertion Count Errata

## 1. Scope & Purpose
This errata document reconciles assertion counts, explains deliverable evolution across Task T-009 iterations (R1, R2, R3, EXIT), and formally corrects drafting ambiguities while strictly preserving raw historical logs as immutable evidence.

---

## 2. Assertion Count Mathematical Formula
In `tools/check_working_tree_consistency.py`, the total PASS assertions reported during repository verification follow a strictly deterministic formula:

$$\text{Total Assertions} = \text{Baseline Invariants} + 2 \times N_{\text{registered\_deliverables}}$$

Where:
- $\text{Baseline Invariants} = 111$: Fundamental checks covering raw data existence, manifest schemas, document cross-references, Git exclusion, and directory structure.
- Each registered deliverable $dp \in \text{EVIDENCE\_DELIVERABLE\_REGISTER.json}$ undergoes exactly 2 checks:
  1. Format and required metadata fields validation (`dp`).
  2. Physical file existence, exact byte size, and SHA-256 integrity verification (`dp`).

### Historical Progression Across T-009 Iterations
| Iteration Stage | Registered Deliverables ($N$) | Calculated Assertions ($111 + 2N$) | Reported PASS Count | Context / Notes |
| :--- | :---: | :---: | :---: | :--- |
| **T009-R2 Baseline** | 210 | 531 | 531 | Prior to R3 defect reproduction tests and reports |
| **T009-R3 Draft State** | 219 | 549 | 549 | Intermediate state before registering all 17 R3 deliverables |
| **T009-R3 Final State** | 227 | 565 | 565 | Final registered state with R3 tests, logs, and reports |
| **T009-R3-EXIT Final State** | 241 | 593 | 593 | Complete exit state including 7 EXIT reports + 7 EXIT logs |

---

## 3. Explicit Operational Assumptions & Boundary Clarifications
1. **Single-Writer Operational Assumption:** The storage publication engine assumes batch-mode execution orchestrated sequentially by the pipeline coordinator. Concurrent execution attempting duplicate `run_id` publications is prevented by immutable version directories (`FAILED_VERSION_EXISTS`), but distributed locks are out of scope for G4 and deferred to production orchestration.
2. **Raw Log Immutability:** Historical log files (such as `T009_R3_LOG_REGISTRY_REGRESSION.txt`) remain unchanged in `docs/05-evidence/` to maintain strict audit trail integrity. The explanation and verified clean status are formally recorded in `T009_EXIT_REGISTRY_FAILURE_RECONCILIATION.md` and `T009_EXIT_LOG_REGISTRY_REGRESSION.txt`.
