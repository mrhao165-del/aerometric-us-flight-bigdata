# G6_T012_FIRST_BATCH_PRESTART_DECISION_MATRIX.md
## Master Decision Matrix & Prestart Gate Checklist for First Annual Batch (T-012)

**Project:** US Flight Performance Analysis 2016–2024  
**Date:** 2026-10-21  
**Gate Status:** G5 = IN_PROGRESS (TECHNICALLY READY) | G6 = NOT_STARTED / BLOCKED  
**Author:** Project Governance Release Reviewer & Principal Big Data Architect  
**Purpose:** Formal submission of Decision Register D1–D5, Architectural Choice G6-ARCH-2016, and Resource Policy to Project Lead for official signoff.

---

## 1. Master Decision Matrix (D1–D5)

| Decision ID | Governed Domain | Technical Baseline & Evidence Ready | Current State | Action Required from Project Lead |
|---|---|---|---|---|
| **D1** | **BTS Source Provenance** | `T_ONTIME_REPORTING_20261019_112232.zip` verified (**29,975,383 bytes**, SHA-256 `342de99f...`; supersedes 25,658,745 typo). Intake manifest sealed. | `AWAITING_DECISION` | Sign formal attestation of BTS reference data acquisition. |
| **D2** | **FP-DEC-019 / Option B** | Option B technical verification complete: RAW CSV vs BTS Jan 2019 exact 7-field parity on 1,500 flights. `PARQUET_PARITY_NOT_TESTED` preserved. | `PROPOSED / PENDING` | Formally approve Option B scope and ratify FP-DEC-019. |
| **D3** | **TS-018 Technical Signoff** | Strict verifier hardened, 14 negative tests pass, 100% exact numeric match, residual risks documented. | `HUMAN_SIGNOFF_PENDING` | Execute formal technical signoff closing G2-EXC-001 as `RESOLVED_BY_OPTION_B`. |
| **D4** | **Gate G5 Gate Signoff** | All 19 G5 exit criteria satisfied technically. Evidence matrix errata published (`G5-ERRATA-20261021-01`). | `IN_PROGRESS (TECHNICALLY READY)` | Execute formal gate signoff transitioning Gate G5 to `PASS (CONTROLLED)`. |
| **G6-ARCH-2016** | **2016 Catalog Architecture** | Option B recommended: Preserve 50 T-010 files as historical benchmark; run clean versioned production batch `run_2016_v1` into `data/curated/runs/`. | `RECOMMENDED_OPTION_B` | Formally select Option B (clean production rerun) over Option A (promote T-010). |
| **D5** | **G6 Annual Ingestion Authorization** | Coordinator CLI hardened with `--dry-run-preflight`. Invariant tests passing. Governed hold active. | `NOT_AUTHORIZED / BLOCKED` | Authorize commencement of live PySpark execution for Year 2016. |

---

## 2. Resource Policy & Threshold Decision

| Metric | Measured Physical Value | Legacy Runbook Threshold | Recommended Governed Threshold | Governance Status |
|---|---|---|---|---|
| **Free Disk Space** | **58.95 GiB (63.30 GB)** | 60 GiB | **25 GiB** (Provides 16x margin over ~1.5 GB annual Parquet) | `UNAPPROVED_RESOURCE_THRESHOLD` (Awaiting D5 Approval) |
| **Available RAM** | **2.69 GiB (2.89 GB)** | 8 GiB | **4.0 GiB** (Single-year 2016 peak benchmark is 3.2 GB) | `UNAPPROVED_RESOURCE_THRESHOLD` (Awaiting D5 Approval) |
| **Total Physical RAM** | **15.71 GiB (16.87 GB)** | N/A | Hardware constraint | Satisfied |

> [!IMPORTANT]
> The technical team recommends Project Lead formally approve the calibrated resource thresholds (25 GiB disk / 4 GiB available RAM) as part of Decision D5, replacing the uncalibrated historical estimates.

---

## 3. Prestart Conditions Verification Checklist

All technical prerequisites for commencing Year 2016 execution are evaluated below:

- [x] **CANONICAL_SOURCE_VERIFIED:** `data/raw/tabular/2016/flight_with_weather_2016.csv` verified on disk (1,538,427,452 bytes, 5,537,987 rows, SHA-256 `4ed92ed7...`).
- [x] **RECURSIVE_DISCOVERY_PROVEN (R05):** `discover_physical_parquet_files()` passes deep partition hierarchy, symlink guard, and row conservation tests (62/62 tests PASS).
- [x] **SINGLE_RUN_VERIFIER_READY (E02):** `validate_single_annual_run` implemented and unit tested without faking 9-year snapshots.
- [x] **CLI_RUNNER_VALIDATED (E03):** `flight_pipeline.ingestion.coordinator` production CLI with `--dry-run-preflight` verified (Exit 0).
- [x] **LOCK_ROOT_ALIGNED (E04):** `data/locks/.pipeline.lock` confirmed as production mutex path. Preflight safety tool passes.
- [x] **BTS_HASH_CORRECTED (E05):** Canonical BTS hash `342de99f...` cited in governance register.
- [x] **ERRATA_PUBLISHED (E05):** `G5_SIGNOFF_EVIDENCE_MATRIX_ERRATA.md` issued for 2016 row counts in historical matrices.
- [ ] **HUMAN_D1_SIGNED:** Pending Project Lead signature.
- [ ] **HUMAN_D2_SIGNED:** Pending Project Lead signature.
- [ ] **HUMAN_D3_SIGNED:** Pending Project Lead signature.
- [ ] **HUMAN_D4_SIGNED:** Pending Project Lead signature.
- [ ] **HUMAN_ARCH_2016_RATIFIED:** Pending Project Lead signature.
- [ ] **HUMAN_D5_SIGNED:** Pending Project Lead signature.

---

## 4. Governance Signoff Recommendation & Stop Order

1. **Recommendation:** The technical team recommends Project Lead execute Decisions **D1, D2, D3, D4**, and ratify **G6-ARCH-2016 Option B**.
2. **Post-Signoff Action:** Following approval of D1–D4, Project Lead may review workstation resource allocations and execute Decision **D5** to authorize the first annual production batch (Year 2016).
3. **MANDATORY STOP ORDER:**
   **Per `AGENTS.md`, AI AGENTS MUST NOT SELF-APPROVE DECISIONS D1–D5 OR EXECUTE T-012. WORK IS COMPLETE AND TRANSFERRED TO HUMAN GOVERNANCE.**
