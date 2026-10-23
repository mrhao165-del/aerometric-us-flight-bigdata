# T011-R5 Baseline and Document Reading Attestation

**Project:** US Flight Performance Analysis 2016–2024  
**Task:** T-011 R5 — Lock Safety Closure and Evidence Reconciliation  
**Parent Gate:** G5 — `IN_PROGRESS`  
**Downstream Gate:** G6 — `NOT_STARTED / BLOCKED` (`G2-EXC-001` Hard Stop)  
**Timestamp:** 2026-10-19T09:58:00Z  
**Host Platform:** Windows-10-10.0.19045-SP0, Python 3.10.11 (64-bit AMD64)  
**Git Baseline Commit:** `bc4f03fb8ccd6c0b2455af3fcb2b1b98fa39d632` (branch: `master`)  
**Previous Package:** `T011_R4_REVIEW_PACKAGE.zip` (SHA-256: `cc91897a84698d91a39e4bab064f473f67c9f323189a0207bb123fe7c316ff2d`)  
**Authority:** Project Lead is the exclusive human signoff authority.

---

## 1. Documentation Review Attestation

Pursuant to `AGENTS.md` and the Master Execution Prompt for T011-R5, the Implementation Agent has conducted a full, non-truncated inventory and reading of all canonical project planning, architecture, governance, testing, quality, and evidence Markdown documents:

| Relative Document Path | Exact Byte Size | SHA-256 Hash | Applicable Governance Mapping |
| :--- | :---: | :---: | :--- |
| `AGENTS.md` | 3,923 | `21b3390c50098df5b34bc2931e98d9d20c571936c50ec9528f1498b3c95973e6` | Agent Execution Policy, Gate Constraints, DoD |
| `README.md` | 13,833 | `9cfda3494b8e8f85d14df59d04fc4948a27d2c3325608bfa0d2c67c5144b2c1f` | Repository Orientation, Data Overview |
| `START_HERE.md` | 13,101 | `9eec732734e56fe8fc7ec945bbbe4f74d7df6db8759fb96ef207cb120b08ddcb` | Developer & Auditor Guide |
| `docs/01-planning/PRD.md` | 11,540 | `18507a2d48bf638f29ea156e507722632b724f114c0ff955772ef9ee534c0f56` | Product Scope, 8 CORE KPIs, Non-goals |
| `docs/01-planning/ROADMAP.md` | 10,740 | `4ee94002c9ec56b46eaec8eb520b72f10d65b75b9f9392e27cb9df77051280cf` | Gate Milestones (G1..G7), Hard Stops |
| `docs/01-planning/BACKLOG.md` | 16,357 | `89ef2db80eb170d10d0a5160ba2ea7ea5c90b84f2b157451a44e5914fa62ba5c` | Task Definitions, Acceptance Criteria |
| `docs/02-design/ARCHITECTURE.md` | 21,056 | `25bc2ff30fc1d1b827361a354cfebfa0e6761dc110f0f507b99321ef77fbc84a` | 10-Step Architecture, Windows NTFS Safe Publication |
| `docs/02-design/ANALYSIS_PROTOCOL.md` | 15,372 | `f34d1b817e766fb853cbdb336184a1e9447d25e016f4e662aa0d984cfb7d603a` | Statistical Aggregations, min-N Rules |
| `docs/02-design/DATA_CONTRACT.md` | 15,312 | `705352cbb9a3f2bb750730d4a9cfdb8fa7075775ba09cfbf81b1d89e52542031` | DC-01..DC-12 Rules, 34 Raw Columns, Disjoint Cohorts |
| `docs/02-design/DATA_DICTIONARY.md` | 15,108 | `fcf5a61e05d0cb09581a81fb6d5aa9b2e0be8ca699bc221f7ee72f5d07015cfc` | Field Definitions, Nullability, Types |
| `docs/02-design/DECISIONS.md` | 21,647 | `bede7f51e95a832bd24dd6ceb51e4eb72a0fb6d9d3efc5a97fc4bc7642d0e66d` | FP-DEC-001..017, G2-EXC-001, Storage Locks |
| `docs/02-design/KPI_SPEC.md` | 17,466 | `6cf87d4681600dbdb907d722d3b2a59a724ba83857bdf8f2bb29828453443a60` | KPI-01..08 Formulas, Metric Denominators |
| `docs/03-quality/TEST_PLAN.md` | 16,929 | `b6e1dfd4f6a7079bf6ee3f11e9e2b1704e0e577ab0be3f7a18be574db0a87a27` | TS-001..TS-020 Specifications, TS-018 Gate G5 Stop |
| `docs/03-quality/RISK_REGISTER.md` | 19,812 | `8cba615ef5c20eb1808e0638ffb6b0a790f9b3e1f37eef52467b7e6bc7925a17` | R-01..R-17 Risks, OR-05 (March 2024), OR-08 |
| `docs/03-quality/CHANGELOG.md` | 25,626 | `799cf76f3eb3da39d5e1dc7f4749377484df63261ea15a9f39aa19a3b680c651` | Living Version Audit Trail |
| `docs/04-execution/PROJECT_STATE.md` | 18,348 | `d601618641ea5d8d2b2fe8e97491cf0eb209c1b3f9ff5f5cf07c394c8b212dd0` | Gate Statuses, Active Governance Decisions |
| `docs/03-quality/ROLLBACK_PLAN.md` | 13,010 | `ff07ca3cb5bf36c99c55b632938466e3ebf49e4d1f2fb8b2d415bf37d57c2a5c` | Non-destructive Rollback Order, Pointer Safety |
| `docs/04-execution/AI_HANDOFF.md` | 14,845 | `2f9f8fa266f83196c888d2235940c6fe3e2843ef99ba25c5a089d892804586f1` | Handoff Standards, Packaging Instructions |

---

## 2. Invariant Baseline Code Hashes

The relevant implementation and test code prior to R5 source modifications:

| File Path | Bytes | SHA-256 Hash | Role in R5 |
| :--- | :---: | :---: | :--- |
| `src/flight_pipeline/storage/locking.py` | 17,245 | `adcf23bebff28f894e66842e70b6c2341d3e231f70aef23721d3f61ed8bc82d6` | Lock mechanism subject to R5-F01 remediation |
| `src/flight_pipeline/kpi/bts_reconciler.py` | 33,414 | `495f9f3788c939caedd5fee13a6f0b18141e264ebd247d875e6c8f48d05b95af` | BTS reconciler subject to R5-F02 hex validation |
| `src/flight_pipeline/storage/publication.py` | 17,096 | `86dd8b233e6d8ccaab05a2fd7269d6be3b967b743d56c980e9503c24502b5cbd` | 7-step safe publisher (unmodified, verified) |
| `tools/qa/run_ts018_bts_parity.py` | 12,482 | `a483f4f2af59b4522c9943385805aa7de011a31e0d43c6bcb088b4ff7a7f63bd` | TS-018 runner (unmodified, verified) |
| `tests/test_t007_locking.py` | 8,041 | `3b35acfe1bcc5e139e94d28fa5673e01d60ad6fc32d8cc8617e0c0a27e8cb3a8` | Core locking unit test suite (unmodified, verified) |
| `tests/test_t011_r4_counterexamples.py` | 25,737 | `d9f64856e6444341632c5e08a972765959e6591ecd74219c3cf0a7700ff169b7` | R4 counterexamples (unmodified, verified) |

---

## 3. Governance Status & Hard Constraints Attestation

1. **Gate G5 State:** `IN_PROGRESS`. T-011 technical corrections are undergoing independent review and remediation. T-011 is NOT officially signed off.
2. **Gate G6 State:** `NOT_STARTED / BLOCKED`. Strictly blocked under `G2-EXC-001` hard stop requiring authentic BTS parity (`TS-018`) human signoff.
3. **TS-018 Authentic BTS Parity:** `PENDING`. No candidate reference dataset has been approved by the Project Lead.
4. **Raw Data Immutability:** 0 bytes of `data/raw/` have been or will be altered.
5. **Approved T-010 Staging:** Completely preserved and read-only.
6. **No Redesign:** The approved G2–G4 architecture and KPI engine definitions remain 100% stable.
