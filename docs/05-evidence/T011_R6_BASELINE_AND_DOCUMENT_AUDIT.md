# T011-R6 Baseline & Document Reading Attestation

**Project:** US Flight Performance Analysis 2016–2024  
**Task:** T-011 R6 — Controlled Final Lock Safety Closure  
**Parent Gate:** G5 — `IN_PROGRESS`  
**Downstream Gate:** G6 — `NOT_STARTED / BLOCKED` (`G2-EXC-001` Hard Stop)  
**Audit Timestamp:** 2026-10-19T10:43:25.998245+00:00  
**Host Platform:** Windows 10 (AMD64), Python 3.10.11  
**Git Baseline Commit:** `bc4f03fb8ccd6c0b2455af3fcb2b1b98fa39d632` (branch: `master`)  
**Previous Package:** `T011_R5_REVIEW_PACKAGE.zip` (SHA-256: `2037e02ba46a6d511de51f1fc7031e8df4f77b5224bb6ed404686720ac0732bd`)  
**Authority:** Project Lead is the exclusive human signoff authority.

---

## 1. Documentation Reading Attestation

Pursuant to `AGENTS.md` and Master Execution Prompt T011-R6, the Implementation Agent has conducted a complete, physically verified reading and hash audit of all canonical project planning, architecture, governance, testing, quality, and execution Markdown documents. Every byte count and SHA-256 digest in this table has been freshly calculated directly from the physical filesystem at the start of iteration R6:

> [!NOTE]
> The byte counts and SHA-256 digests in this table record the authoritative baseline snapshot at the start of task T-011 R6. Living documents (`docs/01-planning/BACKLOG.md`, `docs/04-execution/PROJECT_STATE.md`, `docs/03-quality/CHANGELOG.md`) evolve as part of task execution and governance reporting; their live post-remediation digests are sealed in `EVIDENCE_DELIVERABLE_REGISTER.json` under `governed_living_docs`. All static canonical documents remain permanently identical to this baseline.

| Relative Document Path | Exact Byte Size | SHA-256 Digest | Applicable Governance Mapping |
| :--- | :---: | :---: | :--- |
| `AGENTS.md` | 4,178 | `4b97c977133acff8e3ad2ecba3c062de00cefda79316b7c6eaa0b33d5c0165d1` | Agent Execution Policy, Gate Constraints, DoD |
| `README.md` | 3,946 | `3c5032ea72b4f3221cf30b703a846265b514d3e6cec8d2e3c4a973acddf32837` | Repository Orientation, Data Overview |
| `START_HERE.md` | 2,396 | `7b46e77572cdd89ed6717cfd9d8c9139eb2fec5647af7ecbda1fd035c561cda0` | Developer & Auditor Guide |
| `docs/01-planning/PRD.md` | 5,249 | `f0290800a354a94e1adb6424e9942caa83ec215bde03a795bfe91ece2ab10414` | Product Scope, 8 CORE KPIs, Non-goals |
| `docs/01-planning/ROADMAP.md` | 3,865 | `d46dbb64d73340a22830db66ba617ae256e000c44db294375fc30e6cbd6e9c72` | Gate Milestones (G1..G7), Hard Stops |
| `docs/01-planning/BACKLOG.md` | 13,664 | `67847fde3ede97980701a221173a350d7c66fb89412cfe9145c7ab0ba550584e` | Task Definitions, Acceptance Criteria |
| `docs/02-design/ARCHITECTURE.md` | 21,056 | `14cf55d04468149886bec7d6102228240f98bdb07305b7282073bd71608fa6a6` | 10-Step Architecture, Windows NTFS Safe Publication |
| `docs/02-design/ANALYSIS_PROTOCOL.md` | 3,452 | `873fb4bf568b3adf5b96bbe0612b5f918e9caa072be4d819c6b8b1742c3b6925` | Statistical Aggregations, min-N Rules |
| `docs/02-design/DATA_CONTRACT.md` | 7,238 | `2f831cbd71f177f9cf18ec101be781f2a5a372ea2b3395aef6fe9bde1a04d6f4` | DC-01..DC-12 Rules, 34 Raw Columns, Disjoint Cohorts |
| `docs/02-design/DATA_DICTIONARY.md` | 6,081 | `c4e729f40db803719f7f66fef92225a703db6a15a5de4a3d4cece095fb5f9642` | Field Definitions, Nullability, Types |
| `docs/02-design/DECISIONS.md` | 21,647 | `bede7f51e95a832bd24dd6ceb51e4eb72a0fb6d9d3efc5a97fc4bc7642d0e66d` | FP-DEC-001..017, G2-EXC-001, Storage Locks |
| `docs/02-design/KPI_SPEC.md` | 9,949 | `bf4a663485c6416a790e1ca1d721f1da808fa9da61dc1e377b52b4ef04121d9c` | KPI-01..08 Formulas, Metric Denominators |
| `docs/03-quality/TEST_PLAN.md` | 6,346 | `bc77f3d9d82b75af5ad2407b1523a7e010e1429bdba984bf22c7a869a2f9efde` | TS-001..TS-020 Specifications, TS-018 Gate G5 Stop |
| `docs/03-quality/RISK_REGISTER.md` | 11,376 | `55c5a46d682cfd5b0ec45d9d3f4d65c9adf4f513ad12a8dc0eae88af01fd2d85` | R-01..R-17 Risks, OR-05 (March 2024), OR-08 |
| `docs/03-quality/CHANGELOG.md` | 32,022 | `8984216af21d18c38b2d352edacd7007af871bbe800212325dbbd429f8fd86ca` | Living Version Audit Trail |
| `docs/04-execution/PROJECT_STATE.md` | 40,426 | `dfcaff5d18723a5de8557334b37a7acd99ca22f476bb7532297eb314e94d781c` | Gate Statuses, Active Governance Decisions |
| `docs/03-quality/ROLLBACK_PLAN.md` | 1,850 | `a27227da7b8db7ff619b962dd80acf03009410b58052e7f9eaf0fd8f1f4860b2` | Non-destructive Rollback Order, Pointer Safety |
| `docs/04-execution/AI_HANDOFF.md` | 17,329 | `c1d7ae6469570f3da4f36df7a92ada07f594159753781b3e8b05ceb5bd6a06bb` | Handoff Standards, Packaging Instructions |
| `docs/04-execution/TASK_TEMPLATE.md` | 8,445 | `a0d0ae0059350a653ec17ce5b32400983f18f63687d1ffd43017b2abbb5faf91` | Standardized Task Structure & Evidence Invariants |

---

## 2. Invariant Baseline Code Hashes

The physical source code and test files inspected prior to R6 technical modifications:

| Relative File Path | Exact Byte Size | SHA-256 Digest | Role in R6 Remediation |
| :--- | :---: | :---: | :--- |
| `src/flight_pipeline/storage/locking.py` | 23,573 | `2affc597868063dab47b3faa0ac65490349552fb48328956ead21d97a1e78f6d` | SingleWriterLock & CoordinationLock implementation |
| `src/flight_pipeline/storage/publication.py` | 17,096 | `86dd8b233e6d8ccaab05a2fd7269d6be3b967b743d56c980e9503c24502b5cbd` | SafePublisher 7-step publication |
| `src/flight_pipeline/kpi/bts_reconciler.py` | 33,921 | `ee2b343bb1292352b8d8212fe454194b64db1c57c1f6131bd978915f9f337bd2` | BtsTranStatsReconciler & SHA-256 validator |
| `tools/qa/run_ts018_bts_parity.py` | 12,482 | `a483f4f2af59b4522c9943385805aa7de011a31e0d43c6bcb088b4ff7a7f63bd` | TS-018 parity test runner |
| `tests/test_t007_locking.py` | 8,041 | `3b35acfe1bcc5e139e94d28fa5673e01d60ad6fc32d8cc8617e0c0a27e8cb3a8` | T-007 core locking test suite |
| `tests/test_t011_fault_injection.py` | 15,207 | `8b6fd73a494ec6443c2983e368dff57ff5f78e86c2109c8658de7a2fd4df7d7a` | T-011 fault injection & rollback suite |
| `tests/test_t011_r4_counterexamples.py` | 25,737 | `d9f64856e6444341632c5e08a972765959e6591ecd74219c3cf0a7700ff169b7` | T011-R4 counterexamples |
| `tests/test_t011_r5_counterexamples.py` | 20,994 | `57b13d65bf96622d88a33a2d6e6892d848f2097c4535b973ea734db50e9cb329` | T011-R5 counterexamples |

---

## 3. Governance Status & Hard Constraints Attestation

1. **Gate G5 State:** `IN_PROGRESS`. T-011 technical implementation and safety closures are submitted for independent audit review. T-011 is NOT officially signed off.
2. **Gate G6 State:** `NOT_STARTED / BLOCKED`. Strictly blocked under `G2-EXC-001` hard stop requiring authentic BTS parity (`TS-018`) human signoff by Project Lead.
3. **TS-018 Authentic BTS Parity:** `PENDING`. No candidate reference dataset has been approved by the Project Lead; candidate CSV evaluation strictly yields `CANDIDATE_PARITY_VERIFIED_HUMAN_APPROVAL_PENDING` (human_accepted=False).
4. **Raw Data Immutability:** Exactly 0 bytes of `data/raw/` have been or will be altered (54,674,003 rows across 9 years = 15,196,366,173 bytes).
5. **Approved T-010 Staging:** Completely preserved, read-only, and untouched.
6. **No Architectural Redesign:** Approved G2–G4 architecture and 8 CORE KPI definitions remain 100% stable.
7. **Signoff Authority:** Exclusive authority resides with the Project Lead. The Agent issues technical verdicts only (`R6_SAFE_WITH_DECLARED_MANUAL_RECOVERY_LIMITATIONS` or `R6_READY_FOR_INDEPENDENT_TECHNICAL_REVIEW`).
