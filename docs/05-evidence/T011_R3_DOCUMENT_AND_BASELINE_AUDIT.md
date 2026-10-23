# T011-R3 — Document and Baseline Audit Report

**Date:** 2026-10-19T14:05:00+07:00  
**Task:** T-011 R3 — Provenance Trust Boundary, Numeric Integrity, Lock Recovery & Evidence Correction  
**Parent Gate:** Gate G5 — `IN_PROGRESS`  
**Downstream Gate:** Gate G6 — `NOT_STARTED / BLOCKED`  
**Execution Mode:** Autonomous Implementation under Master Execution Prompt T011-R3 with Mandatory Internal Safety Gates  
**Approval Authority:** Project Lead (Exclusive Human Signoff Authority)  
**Status:** `GATE_R3_0_COMPLETE — PROCEED_TO_GATE_R3_1`

---

## 1. Executive Summary & Authoritative Baseline

In accordance with Section 2 of **MASTER EXECUTION PROMPT — T011-R3**, this audit establishes the complete, verified, read-only baseline of repository governance documents, technical design contracts, production source code, and test suites prior to executing any code modifications.

### 1.1. Physical Environment & Git Baseline
- **Repository Root:** `D:\Study\Code\Apache\Flight_Analyzt\US_FLIGHT_PERFORMANCE_DOCS_V1`
- **Operating System:** Windows 11 (NTFS Local Filesystem, win32 API process liveness)
- **Git Commit Baseline:** `bc4f03fb8ccd6c0b2455af3fcb2b1b98fa39d632`
- **Runtime Environment:**
  - Python: `3.10.11` (64-bit)
  - Java: OpenJDK `21.0.12.1` LTS
  - Apache Spark / PySpark: `4.0.1` (local cluster mode `local[4]`, shuffle partitions: `16`)
  - Arrow / Parquet: `pyarrow 19.0.1` (Snappy compression, strict footer Thrift verification)

### 1.2. Uncompromised Canonical Invariants
- **Raw Data Immutability:** 9 CSV files (`data/raw/tabular/{year}/flight_with_weather_{year}.csv` for years 2016–2024, `54,674,003` records, `15,196,366,173` bytes) remain strictly read-only and 100% immutable (0 bytes altered).
- **Provisional Unit Status (`G2-EXC-001`):** The 7 CORE measures (`ARR_DELAY`, `DEP_DELAY`, `TAXI_OUT`, `TAXI_IN`, `AIR_TIME`, `ACTUAL_ELAPSED_TIME`, `CRS_ELAPSED_TIME`) retain provisional status `OFFICIAL_MINUTES_EMPIRICALLY_CONSISTENT_PROVISIONAL`.
- **Authentic BTS Parity (`TS-018`):** Remains strictly `PENDING_EXTERNAL_BTS_SOURCE_DELIVERY`. No AI-generated metadata, self-issued approval token, local checksum, or runner flag can confer authentic acceptance.
- **Downstream Gate Hard Stop:** Gate G6 remains strictly `NOT_STARTED / BLOCKED` until authentic BTS parity is verified under genuine Project Lead signoff.
- **Historic Package Preservation:** Previous review archives `T011_REVIEW_PACKAGE.zip`, `T011_R1_REVIEW_PACKAGE.zip`, and `T011_R2_REVIEW_PACKAGE.zip` are preserved unmodified.

---

## 2. Mandatory Documentation Reading & Contract Reconciliation

All 27 project governance and planning Markdown documents have been read in their entirety (100% line coverage). The exact physical attributes and key requirements are recorded below:

| # | Document Path | Bytes | Lines | SHA-256 Checksum | Reading Coverage & Key Architectural Requirements |
|---|---|---|---|---|---|
| 1 | `AGENTS.md` | 4,178 | 35 | `4b97c977133acff8e3ad2ecba3c062de00cefda79316b7c6eaa0b33d5c0165d1` | 100% — Prohibits editing raw data, fabricating Spark execution, or inferring causality. Strict adherence to DC-11/12 and G2-EXC-001. |
| 2 | `README.md` | 3,946 | 39 | `3c5032ea72b4f3221cf30b703a846265b514d3e6cec8d2e3c4a973acddf32837` | 100% — Project overview: 2016–2024 descriptive study; defines structure, environment, and review procedures. |
| 3 | `START_HERE.md` | 2,396 | 29 | `7b46e77572cdd89ed6717cfd9d8c9139eb2fec5647af7ecbda1fd035c561cda0` | 100% — Quickstart guide; outlines doc hierarchy, gate prerequisites, and read-first policy. |
| 4 | `docs/00-governance/BUILD_QA_REPORT.md` | 2,063 | 21 | `583229e19bd7346ef2857013691d25bae8090882a24c7f1fb69641f7bb32e3f4` | 100% — QA verification report on repository build scripts and environment hygiene. |
| 5 | `docs/00-governance/DOCS_CONSISTENCY_AUDIT_v1.1.md` | 4,179 | 45 | `878184396cb1160a419de1fe251334b8e800aa2796a1e7455b7a37c5986d40ca` | 100% — Docs audit report affirming consistency across 18 core docs and cross-links. |
| 6 | `docs/00-governance/DOCUMENT_REGISTER.md` | 5,376 | 40 | `996754a0cd3b19fd50a386b41ec0b2854180b9c24468bb9e4900f4e1af271f28` | 100% — Authoritative register of all repository documentation deliverables and owners. |
| 7 | `docs/00-governance/V1_0_CONSISTENCY_AUDIT.md` | 16,126 | 123 | `6fe4b6fcfc56a6dbcb79b66764c19c4ef9cb05a6b4ab89d9607547d381ee1f36` | 100% — Comprehensive v1.0 documentation reconciliation audit report. |
| 8 | `docs/01-planning/BACKLOG.md` | 13,568 | 45 | `4c5252971324326d7753fc85ce2930b2b317acebeda70204009faf7accadc464` | 100% — Authoritative task inventory: T-001..T-017; defines completion criteria and downstream obligations. |
| 9 | `docs/01-planning/PRD.md` | 5,249 | 58 | `f0290800a354a94e1adb6424e9942caa83ec215bde03a795bfe91ece2ab10414` | 100% — Research questions RQ-01..RQ-06; defines IN/OUT scope; descriptive study 2016–2024. |
| 10 | `docs/01-planning/ROADMAP.md` | 3,865 | 24 | `d46dbb64d73340a22830db66ba617ae256e000c44db294375fc30e6cbd6e9c72` | 100% — Gates G0..G7 exit criteria and sequential gate dependency rules. |
| 11 | `docs/02-design/ANALYSIS_PROTOCOL.md` | 3,452 | 32 | `873fb4bf568b3adf5b96bbe0612b5f918e9caa072be4d819c6b8b1742c3b6925` | 100% — Statistical and descriptive analysis protocol; causality prohibitions; stratification rules. |
| 12 | `docs/02-design/API_CONTRACTS.md` | 769 | 7 | `ba9ae2838372add9208737572a7986774c3f96e5c0c3d6253c1d5b0f7fdaaf8b` | 100% — API contract specifications for pipeline programmatic interfaces. |
| 13 | `docs/02-design/ARCHITECTURE.md` | 21,056 | 238 | `14cf55d04468149886bec7d6102228240f98bdb07305b7282073bd71608fa6a6` | 100% — High-level PySpark architecture: SafePublisher, coordinator, partitioning, memory budgets. |
| 14 | `docs/02-design/DATA_CONTRACT.md` | 7,238 | 49 | `2f831cbd71f177f9cf18ec101be781f2a5a372ea2b3395aef6fe9bde1a04d6f4` | 100% — Sole owner of DC-11 row accounting and DC-12 metric validity metadata definitions. |
| 15 | `docs/02-design/DATA_DICTIONARY.md` | 6,081 | 54 | `c4e729f40db803719f7f66fef92225a703db6a15a5de4a3d4cece095fb5f9642` | 100% — 34 canonical column definitions, physical data types, nullability, and BTS mappings. |
| 16 | `docs/02-design/DECISIONS.md` | 21,647 | 51 | `bede7f51e95a832bd24dd6ceb51e4eb72a0fb6d9d3efc5a97fc4bc7642d0e66d` | 100% — FP-DEC-001..017 registry, G2-EXC-001 exception record, and living decision governance. |
| 17 | `docs/02-design/KPI_SPEC.md` | 9,949 | 41 | `bf4a663485c6416a790e1ca1d721f1da808fa9da61dc1e377b52b4ef04121d9c` | 100% — Mathematical specifications of KPI-01..08 (CORE) and 17-column standard schema. |
| 18 | `docs/03-quality/CHANGELOG.md` | 24,097 | 50 | `64861fc69062dd1247950a9a94fdf0d8297001d6399c901a19680e7677f0494a` | 100% — Historical changelog tracking all architectural decisions, fixes, and gate progressions. |
| 19 | `docs/03-quality/G0_G1_REVIEW.md` | 3,926 | 39 | `ca325a846bc6890d25c0b03d7e521bdbde15faa7de6fe59b8c6e4972587bf731` | 100% — Independent audit review of Gate G0 baseline and G1 structural data inventory. |
| 20 | `docs/03-quality/RISK_REGISTER.md` | 11,376 | 47 | `55c5a46d682cfd5b0ec45d9d3f4d65c9adf4f513ad12a8dc0eae88af01fd2d85` | 100% — R-01..R-17 canonical risks; maps open risks OR-01..OR-08 to primary mitigations. |
| 21 | `docs/03-quality/ROLLBACK_PLAN.md` | 1,850 | 27 | `a27227da7b8db7ff619b962dd80acf03009410b58052e7f9eaf0fd8f1f4860b2` | 100% — Rollback procedures, single-writer pointer reverting, and staging isolation. |
| 22 | `docs/03-quality/SECURITY.md` | 1,748 | 14 | `24d4696701ec3c03774fbee9313fc1959a5e22ac4311e81cf7b8e4af008b91c8` | 100% — Strict prohibition on `.pt` / `torch.load` and malicious code execution guards. |
| 23 | `docs/03-quality/TEST_PLAN.md` | 6,346 | 46 | `bc77f3d9d82b75af5ad2407b1523a7e010e1429bdba984bf22c7a869a2f9efde` | 100% — TS-001..TS-020 verification matrix; maps tests to required gates and acceptance conditions. |
| 24 | `docs/04-execution/AI_HANDOFF.md` | 17,329 | 86 | `c1d7ae6469570f3da4f36df7a92ada07f594159753781b3e8b05ceb5bd6a06bb` | 100% — Comprehensive AI handoff protocol; establishes source-of-truth hierarchy and errata. |
| 25 | `docs/04-execution/DEPLOYMENT.md` | 1,923 | 19 | `21a408adc186637e21b45abafb721f933778260a69f25f5ca9465090a328209c` | 100% — Operational deployment guidelines and runtime environment setup instructions. |
| 26 | `docs/04-execution/PROJECT_STATE.md` | 40,148 | 90 | `9b64fc6eb628c91a16264f8aff6f648bd561b2cf46b04f1d90de2781d5ca8b6d` | 100% — Authoritative living project state snapshot; gates, tasks, and historical test tracking. |
| 27 | `docs/04-execution/TASK_TEMPLATE.md` | 8,445 | 73 | `a0d0ae0059350a653ec17ce5b32400983f18f63687d1ffd43017b2abbb5faf91` | 100% — Canonical task report template required for all evidence documentation deliverables. |

---

## 3. Production Code & Test Suite Baseline Audit

The relevant production modules and test suites have been inspected in detail:

| File Path | Bytes | Lines | SHA-256 Checksum | Target Defect & Code Audit Findings |
|---|---|---|---|---|
| `src/flight_pipeline/kpi/bts_reconciler.py` | 21,817 | 539 | `78f149b587dac45441c4fd2074d1568fd3c1cfb648c7c812b87eec3e71a56dfe` | **R3-F01, R3-F02, R3-F04, R3-F05**: Validates `metadata.sha256_hash` against itself; converts malformed numerics to `None` causing false `NULL_NULL_AGREEMENT`; uses calendar-unaware regex for dates; emits synthetic PASS when records remain unmatched. |
| `tools/qa/run_ts018_bts_parity.py` | 12,268 | 259 | `c0f89290361cc7c5a8f1fcccfa9771895e26488067625c16999fd72a680e5e07` | **R3-F01**: Line 124 explicitly overwrites declared SHA-256 with computed SHA-256 (`provenance_meta.sha256_hash = bts_sha256`), bypassing cryptographic checksum validation. |
| `src/flight_pipeline/storage/locking.py` | 10,675 | 301 | `4dd338adf0b9bc18c639d5e3664d6dc15fb61c36763949dde277a5de3c947976` | **R3-F03**: Line 268 unlinks lock file when metadata is unparseable (`if existing_meta is None: self.lock_file_path.unlink()`), risking deletion of an active unknown-owner lock. |
| `src/flight_pipeline/storage/publication.py` | 17,096 | 416 | `86dd8b233e6d8ccaab05a2fd7269d6be3b967b743d56c980e9503c24502b5cbd` | Verified compliant with 7-step safe publication, NTFS atomic replacement, and row accounting verification. |
| `tests/test_t011_ts018_bts_parity.py` | 13,852 | 259 | `0ac7b47de2b6837f257ee2a0b8f9f71489a727d999a97a860ea2817729a90028` | Unit tests for TS-018: Test 14C passes fake metadata with string `"APPROVED_BY_PROJECT_LEAD"` and asserts authentic PASS. |
| `tests/test_t011_r2_counterexamples.py` | 7,879 | 185 | `25de5e7dd506acb77b6f9b8dc596c59d07be8b7b67c8fddc485aa50d0134a386` | Permanent regression guards for R2-F01..F05; will be supplemented by R3 regression guards. |
| `tests/test_t011_fault_injection.py` | 15,207 | 328 | `8b6fd73a494ec6443c2983e368dff57ff5f78e86c2109c8658de7a2fd4df7d7a` | Sandbox fault injection F01..F08; F08 tests stale lock recovery. |

---

## 4. Technical Analysis of Independent Auditor Findings (R3-F01..F06)

1. **R3-F01 (False Authentic BTS PASS Through Self-Approved Metadata):**
   - *Mechanisms:* `run_ts018_bts_parity.py` loads companion provenance and overwrites `provenance_meta.sha256_hash = bts_sha256`. Then `reconciler.reconcile()` validates `provenance_metadata.sha256_hash` against itself. A local CSV with a fabricated companion JSON claiming `project_lead_approval_status = "APPROVED_BY_PROJECT_LEAD"` can fool the system into returning `TS018_PASS_AUTHENTIC_PARITY_ESTABLISHED`.
   - *Remediation Plan:* Separate physical file presence, checksum matching, external BTS provenance, and human signoff. Never overwrite pre-existing declared hashes. Explicitly prevent self-signed local metadata from conferring authenticity. If no external Project Lead signed record exists, return candidate evidence for review while keeping TS-018 official status `PENDING`.

2. **R3-F02 (Malformed Numerics Masked as Null-Null Agreement):**
   - *Mechanisms:* `_to_float()` returns `None` for any unparseable string (e.g. `"invalidXYZ"`), NaN, or Infinity. When both dataset and BTS contain malformed strings, `compare_single_field` sees `d_val is None and b_val is None` and returns `MismatchType.NULL_NULL_AGREEMENT`. If another row has valid numbers, `numeric_sample_count > 0` and overall parity passes.
   - *Remediation Plan:* Introduce a strongly typed enum `NumericParseStatus` (`VALID_FINITE_NUMBER`, `TRUE_NULL`, `MALFORMED_NUMBER`, `NONFINITE_NUMBER`, `SCHEMA_MISSING`). Only approved null representations (`None`, `""`, `"NA"`, `"null"`, `"NULL"`) evaluate to `TRUE_NULL`. Malformed strings or non-finites create discrepancies (`MismatchType.VALUE_MISMATCH` or `MALFORMED_NUMERIC_ERROR`), preventing false pass.

3. **R3-F03 (Unknown-Owner Lock Deletion on force=True):**
   - *Mechanisms:* `break_stale_lock(force=True)` in `locking.py` checks `if existing_meta is None: self.lock_file_path.unlink()`. If a lock file is empty, partially written, or corrupted, it deletes it. This violates fail-closed safety because an active lock whose header cannot be parsed might be deleted.
   - *Remediation Plan:* Unparseable or corrupt lock files must fail closed (`FAIL_CLOSED — MANUAL_RECOVERY_REQUIRED`). Automatic unlinking is prohibited even with `force=True`. Only locks with parseable metadata proving a dead PID on the local host can be safely cleared under governed operator force.

4. **R3-F04 (Calendar-Unaware Date Validation):**
   - *Mechanisms:* `ISO_DATE_REGEX = re.compile(r"^\d{4}-(?:0[1-9]|1[0-2])-(?:0[1-9]|[12]\d|3[01])$")` accepts impossible calendar dates like `2026-02-31`, `2025-02-29`, and `2026-04-31`.
   - *Remediation Plan:* Validate calendar dates using `datetime.date(year, month, day)` after regex verification, cleanly rejecting impossible dates while accepting real leap days (`2024-02-29`).

5. **R3-F05 (Synthetic Verification Inconsistency with Unmatched Records):**
   - *Mechanisms:* `reconcile()` checked `matched_parity_ok = not has_mismatch and summary.unique_key_matches > 0 and all_seven_measures_have_numeric`. If 1 record matched, but another candidate record was unmatched, `matched_parity_ok` was True, causing `summary.reconciliation_verdict = "SYNTHETIC_RECONCILER_VERIFIED_AUTHENTIC_BTS_PENDING"` while `numerical_parity_verified` was False.
   - *Remediation Plan:* Full reconciliation success requires zero unmatched records (`unmatched_dataset_records == 0` and `unmatched_bts_records == 0`), zero invalid keys, zero ambiguous duplicates, and zero mismatches. Incomplete synthetic matching must emit `PARTIAL`, `FAIL`, or `BLOCKED`.

6. **R3-F06 (Evidence Claim Reconciliations):**
   - *Mechanisms:* Reconcile discrepancy in reported assertion counts (1,240 vs 1,241) and clarify the exact scope of cryptographic provenance claims.
   - *Remediation Plan:* Track and assert exact test and verifier counts across all modules and issue precise supersession errata.

---

## 5. Gate R3-0 Completion Attestation

The documentation and baseline audit is complete. No production code has been modified during this gate. All mandatory source files and planning documents have been cataloged and reconciled.

**Execution Authority:** Antigravity AI Implementation Agent  
**Next Gate:** Gate R3-1 (Reproduce Counterexamples)
