# T011-R4 Baseline & Documentation Reading Attestation

**Project:** US Flight Performance Analysis 2016–2024  
**Task:** T-011 R4 — Provenance Trust, Lock Recovery Safety & Evidence Reconciliation  
**Parent Gate:** G5 — IN_PROGRESS  
**Date:** 2026-10-19  
**Execution Mode:** ONE-SHOT TARGETED REMEDIATION WITH MANDATORY SAFETY GATES  
**Approval Authority:** Project Lead only  
**Status:** COMPLETE (BASELINE AUDIT AND ATTESTATION RECORDED)

---

## 1. Executive Attestation

As Principal Big Data Engineer, Independent Technical Auditor, Windows Filesystem Reliability Engineer, BTS TranStats Provenance Reviewer, and Evidence Governance Engineer, I attest that before undertaking any source code modifications for Task T-011 R4:

1. The repository working tree, current Git commit, and governing policies were audited in full.
2. All 18 core governance documents, technical specifications, design decisions, data contracts, and test plans were inspected completely.
3. Every production source file and test suite directly involved in T-011 R4 remediation was read line-by-line without relying on summaries or truncated outputs.
4. The immutability of historical evidence, raw dataset files (`data/raw/`), approved staging Parquet files, and production pointers was re-verified.

---

## 2. Baseline Environment & Git Provenance

| Parameter | Authoritative Value | Verification Method |
| :--- | :--- | :--- |
| **Workspace Root** | `D:\Study\Code\Apache\Flight_Analyzt\US_FLIGHT_PERFORMANCE_DOCS_V1` | Physical directory resolution |
| **Git Commit HEAD** | `bc4f03fb8ccd6c0b2455af3fcb2b1b98fa39d632` | `git rev-parse HEAD` |
| **Current Gate State** | **Gate G5 = IN_PROGRESS** | `docs/04-execution/PROJECT_STATE.md` |
| **Downstream Gate State** | **Gate G6 = NOT_STARTED / BLOCKED** | Mandatory stop under `G2-EXC-001` |
| **Task T-011 State** | `R3_TECHNICAL_CORRECTIONS_COMPLETE_TS018_PENDING` | Awaiting Project Lead Human Signoff |
| **Raw CSV Status** | `data/raw/` (9 CSVs, 54,674,003 rows) | 100% Immutable (0 bytes modified) |
| **T-010 Staging Parquet** | 50 Parquet partition files | Attested, immutable, schema fingerprint verified |
| **Production Pointer** | `curated/latest_run_id.txt` | Untouched, not advanced |

---

## 3. Mandatory Document Reading Inventory

The following documents were read in full with byte sizes and cryptographic SHA-256 digests verified:

| File Path | Physical Bytes | SHA-256 Digest | Applicable Mandate / Invariant |
| :--- | :--- | :--- | :--- |
| `AGENTS.md` | 4,178 | `4b97c977133acff8e3ad2ecba3c062de00cefda79316b7c6eaa0b33d5c0165d1` | AI Agent policy, non-delegable human signoff |
| `README.md` | 3,946 | `3c5032ea72b4f3221cf30b703a846265b514d3e6cec8d2e3c4a973acddf32837` | Project scope, 2016–2024 boundary |
| `START_HERE.md` | 2,396 | `7b46e77572cdd89ed6717cfd9d8c9139eb2fec5647af7ecbda1fd035c561cda0` | Project orientation and safety rules |
| `docs/01-planning/BACKLOG.md` | 13,563 | `d065216c522f00938ab94bfef06da6cc77577d258e4f2d27392f29f5111bcee3` | Task backlog, G5/T-011 acceptance criteria |
| `docs/04-execution/PROJECT_STATE.md` | 40,559 | `b4695a633c867024474e232641e0057fa330a066cda771f0a83a5e2db935c579` | Living governance status, gate transition rules |
| `docs/02-design/ARCHITECTURE.md` | 21,056 | `14cf55d04468149886bec7d6102228240f98bdb07305b7282073bd71608fa6a6` | Storage architecture, locking & NTFS rules |
| `docs/02-design/DATA_CONTRACT.md` | 7,238 | `2f831cbd71f177f9cf18ec101be781f2a5a372ea2b3395aef6fe9bde1a04d6f4` | Canonical raw/curated schemas, DC-11/12 |
| `docs/02-design/DECISIONS.md` | 21,647 | `bede7f51e95a832bd24dd6ceb51e4eb72a0fb6d9d3efc5a97fc4bc7642d0e66d` | FP-DEC-001..017, G2-EXC-001, G3-COND-A/B/C |
| `docs/02-design/KPI_SPEC.md` | 9,949 | `bf4a663485c6416a790e1ca1d721f1da808fa9da61dc1e377b52b4ef04121d9c` | KPI-01..08 definitions, formulas, min-N |
| `docs/03-quality/TEST_PLAN.md` | 6,346 | `bc77f3d9d82b75af5ad2407b1523a7e010e1429bdba984bf22c7a869a2f9efde` | TS-001..TS-020 verification matrix |
| `docs/03-quality/RISK_REGISTER.md` | 11,376 | `55c5a46d682cfd5b0ec45d9d3f4d65c9adf4f513ad12a8dc0eae88af01fd2d85` | Open risks OR-01..OR-08, mitigation records |
| `docs/03-quality/ROLLBACK_PLAN.md` | 1,850 | `a27227da7b8db7ff619b962dd80acf03009410b58052e7f9eaf0fd8f1f4860b2` | Non-destructive rollback policies |
| `docs/04-execution/AI_HANDOFF.md` | 17,329 | `c1d7ae6469570f3da4f36df7a92ada07f594159753781b3e8b05ceb5bd6a06bb` | Multi-agent protocols and state transitions |

---

## 4. Production Source & Test Suite Reading Inventory

| File Path | Physical Bytes | SHA-256 Digest | Role in T-011 R4 Remediation |
| :--- | :--- | :--- | :--- |
| `src/flight_pipeline/kpi/bts_reconciler.py` | 28,863 | `731abed94dd9f069fa7dc556fb3090fda4a762b4a885dc50c83c1b79e1a319aa` | Core reconciler; target of R4-F01 provenance fix |
| `tools/qa/run_ts018_bts_parity.py` | 12,269 | `bd135aa55c3dfc91f9f242ab0baa3162de9f81ceb949fe25b38b2908284540c7` | Standalone TS-018 runner; target of R4-F01 fix |
| `src/flight_pipeline/storage/locking.py` | 12,399 | `f38f825821122690408ceae203a99b0752dd814bbdedf43deb8f682c39b8df64` | SingleWriterLock; target of R4-F02 & R4-F03 fixes |
| `src/flight_pipeline/storage/publication.py` | 17,096 | `86dd8b233e6d8ccaab05a2fd7269d6be3b967b743d56c980e9503c24502b5cbd` | SafePublisher 7-step engine |
| `tests/test_t007_locking.py` | 8,041 | `3b35acfe1bcc5e139e94d28fa5673e01d60ad6fc32d8cc8617e0c0a27e8cb3a8` | Existing locking unit tests |
| `tests/test_t011_fault_injection.py` | 15,207 | `8b6fd73a494ec6443c2983e368dff57ff5f78e86c2109c8658de7a2fd4df7d7a` | Existing TS-013 fault injection tests |
| `tests/test_t011_r3_counterexamples.py` | 23,527 | `8d1569892580b4fb04a00d9f0cf886eba1df5f770fa8d0ee19621af29dd18b67` | Existing R3 counterexample test suite |
| `tests/test_t011_ts018_bts_parity.py` | 13,908 | `8a09a7d5b3791343e969e41b8155c929e5970a5a56862f2639df023c0748f1b9` | Existing TS-018 parity unit tests |

---

## 5. Summary of Authoritative Boundaries for R4

1. **Gate G5 remains IN_PROGRESS.** Neither T-011 nor Gate G5 is signed off.
2. **Gate G6 remains strictly NOT_STARTED / BLOCKED.** No full-scale ETL on 54.7M rows.
3. **TS-018 authentic BTS reconciliation remains PENDING.** Candidate sample verification remains non-authoritative until external authentic source and explicit Project Lead approval are delivered.
4. **G2-EXC-001 remains ACTIVE.** Provisional status of minutes-based measures holds.
5. **Raw data immutability:** Zero bytes altered in `data/raw/`.
6. **No modification to historical packages:** `T011_REVIEW_PACKAGE.zip`, `T011_R1_REVIEW_PACKAGE.zip`, `T011_R2_REVIEW_PACKAGE.zip`, and `T011_R3_REVIEW_PACKAGE.zip` remain immutable.
