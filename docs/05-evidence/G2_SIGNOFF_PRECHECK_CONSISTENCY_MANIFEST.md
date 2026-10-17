# G2-SIGNOFF-HANDOFF-FIX — EXECUTION AND ARTIFACT MANIFEST (`G2_SIGNOFF_PRECHECK_CONSISTENCY_MANIFEST.md`)

**Document ID:** `G2-SIGNOFF-PRECHECK-MAN-002`  
**Task ID:** `G2-SIGNOFF-HANDOFF-FIX`  
**Role:** Senior Big Data Evidence Quality Auditor & Independent Governance Reviewer  
**Scope:** Corrected source inventory, executed commands, file changes, verification status, SHA-256 of the errata report, link validation, known checker failures, and reproducibility limitations (`design/documentation only`)  
**Reconciliation Verdict:** **`DOCUMENTATION_RECONCILED`**  
**Current Gate Status:** **`Gate G2 = IN_PROGRESS / NOT_PASSED`**  
**Current `T-006` Status:** **`T-006 = NOT_STARTED`**

---

## 1. AUTHORITATIVE INPUT SOURCE INVENTORY (CORRECTED & VERIFIED)

All 13 mandatory authoritative inputs for `G2-SIGNOFF-HANDOFF-FIX` were read directly from the repository and cross-checked against the canonical fact lock (read-only):

| # | Authoritative File Path | Exact Verified Scope & Status in Source of Truth | Modification Status |
| :---: | :--- | :--- | :--- |
| 1 | [`AGENTS.md`](../../AGENTS.md) | Policy v1.1: `DC-11/12` row accounting & coverage rules, requirement to verify 7 CORE measure units before G2 PASS, Weather optional (`CONDITIONAL_PENDING` or `CONDITIONAL_NO_GO`) non-blocking policy, prohibition on fabricating full-scan/Spark execution | Unmodified |
| 2 | [`docs/02-design/DECISIONS.md`](../02-design/DECISIONS.md) | Contains **14 decisions (`FP-DEC-001` through `FP-DEC-014`)**:<br>- `FP-DEC-001`: Descriptive 2016–2024 scope (`USER_CONFIRMED`)<br>- `FP-DEC-002`: Retrospective use of 2024 (`USER_CONFIRMED_BY_SCOPE`)<br>- `FP-DEC-003`: Exclude ML / ATL-only / Flight Chain `.pt` from CORE (`PROPOSED_IMPLEMENTATION`)<br>- `FP-DEC-004`: Raw data immutable, versioned output by `run_id` (`PROPOSED_CONTROL`)<br>- `FP-DEC-005`: PySpark + Parquet for main processing (`PROPOSED`)<br>- `FP-DEC-006`: Prohibit canceled/diverted KPIs from 34 fields (`PROPOSED_GUARD`)<br>- `FP-DEC-007`: Safe temporal representation guard (`PROPOSED_GUARD`)<br>- `FP-DEC-008`: `ARR_DELAY >= 15` threshold on finite denominator (`PROPOSED_KPI`)<br>- `FP-DEC-009`: Conditional Weather expansion, no causal claims (`PROPOSED`)<br>- `FP-DEC-010`: Prohibit `FLIGHTS` as weight; `accepted` row-based denominator (`PROPOSED_GUARD`)<br>- `FP-DEC-011`: Distinguish `metric_valid_rate` vs `source_coverage_status`, mutually exclusive `accepted`/`quarantined`/`rejected` (`PROPOSED_CONTROL`)<br>- `FP-DEC-012`: **8 CORE KPIs** and verification of **7 CORE measure units/sign/domain** before G2 (`PROPOSED_REQUIREMENT`)<br>- `FP-DEC-013`: Weather is `Should/conditional` (`GO` or `CONDITIONAL_NO_GO`), does not block CORE G2/G6 (`PROPOSED_CONTROL`)<br>- `FP-DEC-014`: Metadata `size/mtime` warns of drift only, not raw content identity (`PROPOSED_CONTROL`) | Unmodified |
| 3 | [`docs/02-design/KPI_SPEC.md`](../02-design/KPI_SPEC.md) | Defines `KPI-01..12`:<br>- **`KPI-01..08` = `CORE`** (`CORE_DRAFT`, serving `RQ-01..05`)<br>- **`KPI-09` = `OPTIONAL`** (`OPTIONAL_DRAFT`, mean positive arrival delay per valid record)<br>- **`KPI-10` = `CONDITIONAL / WEATHER`** (`CONDITIONAL_PENDING`, serving `RQ-06`)<br>- **`KPI-11` = `NOT_COMPUTABLE`** (Cancel/divert rate)<br>- **`KPI-12` = `BLOCKED`** (`FLIGHTS` sum/weight)<br>- Requires `source_coverage_status`, `unit_status`, `min_n_status`, and `provenance_reference` on every KPI output row | Unmodified |
| 4 | [`docs/02-design/DATA_CONTRACT.md`](../02-design/DATA_CONTRACT.md) | Defines `DC-01..DC-10` (`DC-02` = time strings/overnight prohibition before T-004; `DC-03` = `ARR_DELAY`/`DEP_DELAY`; `DC-04` = 5 duration fields `TAXI_OUT`, `TAXI_IN`, `AIR_TIME`, `ACTUAL_ELAPSED_TIME`, `CRS_ELAPSED_TIME`; `DC-07` = 6 Weather fields; `DC-08` = `MONTH`/`DAY_OF_MONTH`/`DAY_OF_WEEK`), `DC-11` (disjoint 3-state row accounting), and `DC-12` (`source_coverage_status = UNKNOWN/PARTIAL/VERIFIED_WITH_SCOPE` + provenance) | Unmodified |
| 5 | [`docs/04-execution/PROJECT_STATE.md`](../04-execution/PROJECT_STATE.md) | Snapshot v1.1: `Gate G2 = IN_PROGRESS / NOT_PASSED`; `T-001 = PASS (Conditional)`, `T-002 = PASS_WITH_OPEN_RISKS`, `T-003 = PASS_WITH_OPEN_RISKS`, `T-004 = READY_FOR_SIGNOFF_WITH_OPEN_DEFECT`, `T-005 = CONDITIONAL_PENDING`, `G3 / T-006 = PLANNED / NOT_STARTED` | Unmodified |
| 6 | [`docs/03-quality/TEST_PLAN.md`](../03-quality/TEST_PLAN.md) | Defines **20 test specifications (`TS-001` through `TS-020`)**, including `TS-008` (P50/P90, min-N, per-submetric denominators), `TS-011` (Weather `GO` or `CONDITIONAL_NO_GO`), `TS-014` (resource benchmark), `TS-017` (accounting/coverage glossary), and `TS-018` (verify 7 CORE measure units/sign/domain from source before G2 or G2 `BLOCKED`) | Unmodified |
| 7 | [`docs/05-evidence/T003_PERCENTILE_AND_MIN_N_DECISIONS.md`](T003_PERCENTILE_AND_MIN_N_DECISIONS.md) | Proposes **`FP-DEC-015`** (PySpark `percentile_approx` GK-sketch `accuracy = 10000` for `KPI-06`, $\epsilon_{\text{rank}} \le 0.01\%$) and **`FP-DEC-016`** (tiered `min-N` ranking thresholds: **`carrier-year >= 1,000`**, **`airport-year >= 365`**, **`route-year >= 100`**), both at status `PROPOSED_DECISION_PENDING_REVIEW` | Unmodified |
| 8 | [`docs/05-evidence/T005_CONDITIONAL_NO_GO_PROPOSAL.md`](T005_CONDITIONAL_NO_GO_PROPOSAL.md) | Proposes **`FP-DEC-PROP-015`** (`CONDITIONAL_NO_GO` for optional Weather analysis `RQ-06` / `KPI-10`), at status `PROPOSAL_PENDING_REVIEW` (with **`FP-DEC-017`** reserved as canonical ID only after authorized human approval) | Unmodified |
| 9 | [`docs/05-evidence/G2_R1_CORRECTED_GATE_READINESS.md`](G2_R1_CORRECTED_GATE_READINESS.md) | Latest G2 technical readiness review; official verdict is **`READY_WITH_EXPLICIT_CONDITIONS`** while `Gate G2` remains `IN_PROGRESS / NOT_PASSED` | Unmodified |
| 10 | [`docs/05-evidence/G2_SIGNOFF_DECISION_APPROVAL_MATRIX.md`](G2_SIGNOFF_DECISION_APPROVAL_MATRIX.md) | Decision-by-decision governance matrix for `FP-DEC-001..016` and `FP-DEC-PROP-015` (proposed canonical ID `FP-DEC-017`) | Unmodified |
| 11 | [`docs/05-evidence/G2_SIGNOFF_HUMAN_APPROVAL_RECORD_DRAFT.md`](G2_SIGNOFF_HUMAN_APPROVAL_RECORD_DRAFT.md) | Unsigned human approval record draft (`UNSIGNED_DRAFT — NO APPROVAL CONFERRED`) | Unmodified |
| 12 | [`docs/05-evidence/G2_SIGNOFF_FINAL_PRECHECK_ADDENDUM.md`](G2_SIGNOFF_FINAL_PRECHECK_ADDENDUM.md) | Precheck addendum (`CHECK-01..05`), refined by [`G2_SIGNOFF_PRECHECK_CONSISTENCY_ERRATA.md`](G2_SIGNOFF_PRECHECK_CONSISTENCY_ERRATA.md) regarding `G2-EXC-001` historical audit scope and `DC-12` `provenance_reference` preservation | Unmodified |
| 13 | [`docs/05-evidence/G2_SIGNOFF_FINAL_PRECHECK_MANIFEST.md`](G2_SIGNOFF_FINAL_PRECHECK_MANIFEST.md) | Previous precheck manifest audited and corrected via [`G2_SIGNOFF_PRECHECK_CONSISTENCY_ERRATA.md`](G2_SIGNOFF_PRECHECK_CONSISTENCY_ERRATA.md) (`B-01..B-07`) without overwriting the historical file | Unmodified |

---

## 2. COMMANDS ACTUALLY EXECUTED & VERIFICATION RESULTS

No raw CSV files (`data/raw/tabular/{year}/flight_with_weather_{year}.csv`) were scanned and no Spark jobs were executed in this task. The following commands were actually executed in the workspace:

| # | Command Executed | Purpose | Exit Code | Verification Status & Honest Output Summary |
| :---: | :--- | :--- | :---: | :--- |
| 1 | `python -c "import hashlib, os; p='docs/05-evidence/G2_SIGNOFF_PRECHECK_CONSISTENCY_ERRATA.md'; b=open(p,'rb').read(); print(p, len(b), hashlib.sha256(b).hexdigest())"` | Compute exact byte size and SHA-256 of `G2_SIGNOFF_PRECHECK_CONSISTENCY_ERRATA.md` | `0` | **`PASS`** — `37,570 bytes`, SHA-256: `71ea3bfaa85f88428dd662f099b8ca4e4b430fbefdb0de262541b50ce4429d7a` |
| 2 | `python tools/qa/verify_t004_time_representation.py` | Independently verify T-004 time representation assertions, 9-year `schema_YYYY.json` row counts (`54,674,003`), and `TF-01..09` fixtures | `0` | **`PASS`** — `VERIFICATION SUMMARY: 90 PASS, 0 FAIL` (`ALL 90 T-004 FINAL QA CHECKS PASSED`) |
| 3 | `python tools/check_working_tree_consistency.py` | Independently run repository working-tree and Markdown link consistency checker | `1` | **`86 PASS, 2 FAIL` (Known Checker Failure Retained Honestly):**<br>- All 86 structural, manifest hash, `docs/...` path, and relative Markdown link checks **`PASS`** (`All relative markdown links resolve correctly`).<br>- **2 FAIL assertions:** `No unrecognized stray files in working-tree` and `All extra working-tree files cleanly accounted for` fail because line 139 of [`tools/check_working_tree_consistency.py`](../../tools/check_working_tree_consistency.py#L139) hardcodes a whitelist for `T001_..T004_` only, flagging the **22 post-T004 evidence files** (`7 T005_ + 3 G2_ + 4 G2_R1_ + 4 G2_SIGNOFF_ + 2 G2_SIGNOFF_FINAL_PRECHECK_ + 2 G2_SIGNOFF_PRECHECK_CONSISTENCY_`). |
| 4 | Post-export UTF-8 readback and relative link validation script | Verify both new `G2_SIGNOFF_PRECHECK_CONSISTENCY_*` files are valid UTF-8, non-empty, and all relative Markdown links resolve on disk | `0` | **`PASS`** — `2 files verified, 0 broken links` |

---

## 3. FILE CHANGES & GENERATED OUTPUT ARTIFACTS

### 3.1. Unauthorized Modification Check
- **Modified existing tracked or untracked files:** **`0`** (`None`).
- Raw data (`data/raw/`), audit inputs (`docs/05-evidence/inputs/`), manifests (`SOURCE_MANIFEST.json`, `PACKAGE_MANIFEST.json`), governance documents (`AGENTS.md`, `DECISIONS.md`, `KPI_SPEC.md`, `DATA_CONTRACT.md`, `PROJECT_STATE.md`, `TEST_PLAN.md`, `RISK_REGISTER.md`), and all prior evidence reports (`T001_..T005_`, `G2_*`, `G2_R1_*`, `G2_SIGNOFF_*`) remain **100% untouched**.

### 3.2. New Markdown Files Created (`docs/05-evidence/`)

| Exact Output Path | Role / Description | File Size (Bytes) | SHA-256 Checksum | UTF-8 & Link Validation |
| :--- | :--- | :---: | :--- | :---: |
| [`docs/05-evidence/G2_SIGNOFF_PRECHECK_CONSISTENCY_ERRATA.md`](G2_SIGNOFF_PRECHECK_CONSISTENCY_ERRATA.md) | Cross-document consistency errata resolving `A-01..A-05`, `B-01..B-07`, `G2-EXC-001` (`C`), `DC-12` `provenance_reference` (`D`), and reported vs verified executions (`E`) | `37,570` | `71ea3bfaa85f88428dd662f099b8ca4e4b430fbefdb0de262541b50ce4429d7a` | `PASS` (`0` broken links) |
| [`docs/05-evidence/G2_SIGNOFF_PRECHECK_CONSISTENCY_MANIFEST.md`](G2_SIGNOFF_PRECHECK_CONSISTENCY_MANIFEST.md) | This execution and artifact manifest (self-hash omitted inside the file to avoid circular hashing; reported externally in console output) | *(See console output)* | *(Self-hash omitted)* | `PASS` (`0` broken links) |

---

## 4. KNOWN CHECKER FAILURES & REPRODUCIBILITY LIMITATIONS

1. **Known Working-Tree Checker Failure (`tools/check_working_tree_consistency.py`, Exit Code `1`, `86 PASS, 2 FAIL`):**
   - As documented in Section 2, [`tools/check_working_tree_consistency.py`](../../tools/check_working_tree_consistency.py#L139-L176) fails on 2 inventory assertions because its static prefix tuple `("T001_", "T002_", "T003_", "T004_")` does not include `T005_` or `G2_` deliverables. Because modifying existing scripts is strictly prohibited before human sign-off, this failure is retained and reported transparently.
2. **Historical Audit vs. Live Full-Dataset Execution (`Reproducibility Limitation`):**
   - Full-dataset metrics (`54,674,003` total rows across 9 CSVs, `10,116,916` rows with `ARR_DELAY >= 15`, 2024 date coverage `335/366` days missing March 2024, `YX 3624` physical row numbers `6,384,132` and `6,384,133`, and Weather null counts) are **cited from historical `schema_YYYY.json` and `T-001..T-005` audit artifacts**. They were **not** re-computed via a live 54.67M-row raw CSV scan or Spark job during `G2-SIGNOFF-HANDOFF-FIX`.
   - The `T-003` QA assertion count (`133/133 PASS`) is **reported in `T-003` closeout documentation** ([`T003_FINAL_CLOSEOUT_VERIFICATION.md`](T003_FINAL_CLOSEOUT_VERIFICATION.md)), whereas the `T-004` QA assertion count (`90/90 PASS`) was **independently reproduced in this session** by executing `python tools/qa/verify_t004_time_representation.py` (Exit Code `0`).
3. **Gate & Task Lock:**
   - `Gate G2` remains **`IN_PROGRESS / NOT_PASSED`**.
   - `T-006` remains **`NOT_STARTED`**.
   - All proposed decisions (`FP-DEC-003..016`, `FP-DEC-PROP-015`, and exception `G2-EXC-001`) remain **unapproved** pending human sign-off.
