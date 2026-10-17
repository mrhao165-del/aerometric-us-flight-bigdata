# T007 DESIGN R1 TEST TRACEABILITY CORRECTIONS — CANONICAL TEST PLAN & RISK ALIGNMENT

**Document ID:** `DOC-T007-DESIGN-R1-07-TEST-TRACEABILITY`  
**Task ID:** `T-007` (Raw CSV Ingestion Pipeline)  
**Phase:** `DESIGN REMEDIATION (R1)`  
**Gate:** `G4` (`PLANNED / NOT_COMPLETED`)  
**Design Authority:** Independent QA Auditor & Big Data Test Engineer  
**Binding Standards:** [`TEST_PLAN.md`](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/docs/03-quality/TEST_PLAN.md), [`RISK_REGISTER.md`](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/docs/03-quality/RISK_REGISTER.md)  

---

## 1. RECTIFICATION OF TEST IDENTIFIERS (`TEST_PLAN.md`)

The initial T-007 design misassigned `TS-009` to atomic pointer publication. Cross-referencing [`TEST_PLAN.md`](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/docs/03-quality/TEST_PLAN.md) establishes the authoritative mapping of all relevant test IDs:

| Canonical Test ID | Canonical Description in `TEST_PLAN.md` | Authoritative Gate Scope | Associated Tasks | Role in Ingestion Pipeline (T-007) |
|---|---|---|---|---|
| **`TS-001`** | **Đủ 9 nguồn và 34 cột mỗi năm** | G4 synthetic / G5 real / G6 full | `REQ-01`, `T-007` | Verifies physical presence of 9 annual CSVs, header names, and exact 34 column order. Fail-closed on drift. |
| **`TS-002`** | **Parse date/numeric, null, NaN, inf, domain & flags** | G4 / G5 | `REQ-02`, `T-007`, `T-008` | Verifies data type parsing, anchored date regex, numeric finite predicates (`is_finite_numeric`), and null handling. |
| **`TS-003`** | **Ba trạng thái row accounting: `raw = accepted + quarantined + rejected`, disjoint** | G4 synthetic / G5 / G6 | `REQ-02/04`, `T-008`, `T-010`, `T-012` | Verifies DC-11 row partition conservation and mutual exclusivity across sets. |
| **`TS-009`** | **Guard FLIGHTS grain, cancel/divert guard, weather optional** | G2 design / G5 / G7 | `REQ-04`, `T-002`, `T-011` | Verifies: (1) `FLIGHTS == 1.0` is constant and not used as weight; (2) no CANCELLED/DIVERTED filters exist; (3) Weather nulls accepted. |
| **`TS-013`** | **Fault injection, rollback pointer, invalid partial output** | **DEFERRED TO G5** | `REQ-07`, `T-011` | Verifies `SafePublisher` Step 5 rollback behavior under injected crashes. (Not claimed as passed in G4). |
| **`TS-014`** | **Resource & Performance benchmark** | **DEFERRED TO G5/G6** | `REQ-07`, `T-006`, `T-010`, `T-012` | End-to-end memory/CPU/disk throughput across 54.7M rows. (Not claimed as passed in G4). |
| **`TS-017`** | **Accounting/coverage glossary + zero denominators** | G4 synthetic / G5 | `REQ-02/04`, `T-002`, `T-003`, `T-008` | Verifies DC-12 rates (`IAR`, `MVR`), zero-denominator handling (`ZERO_DENOMINATOR` rule). |
| **`TS-018`** | **Verify seven CORE measure units/sign/domain từ source** | **DEFERRED TO G5 (MANDATORY BLOCKER FOR G6)** | `REQ-03/05`, `T-003`, `T-011` | Per `G2-EXC-001`, empirical verification against BTS TranStats. If FAIL, blocks G6. |
| **`TS-019`** | **Raw identity và metadata drift** | G4 synthetic / G5 | `REQ-07`, `T-001`, `T-007` | Verifies file sizes/mtimes, computes local streaming SHA-256 for 9 CSVs, maintains `OR-08 = IDENTITY_UNVERIFIED`. |
| **`TS-020`** | **Stable row lineage / row identifier** | G4 / G6 | `REQ-02/07`, `T-007`, `T-012` | Verifies reproducible row traceability across distributed reads; preserves `YX 3624` duplicate candidate key. |

---

## 2. RESTORATION OF CANONICAL RISK IDENTIFIERS (`RISK_REGISTER.md`)

The initial T-007 design erroneously repurposed `OR-01..OR-08` as pipeline operational risks (e.g. labeling OOM as OR-01). To eliminate document drift, the design restores the authoritative definitions from [`RISK_REGISTER.md`](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/docs/03-quality/RISK_REGISTER.md):

### 2.1. Authoritative `OR-01` to `OR-08` Alignment
- **`OR-01` (`Primary: R-09`):** `FLIGHTS == 1.0` constant on all 54.7M rows. Mitigated by `FP-DEC-010`: forbidden as weighting factor; canonical count is `count_records`.
- **`OR-02` (`Primary: R-05, Additional: R-09, R-13`):** Duplicate candidate key pair `YX 3624` (2018-06-21 DEN $\to$ XNA). Mitigated by `DC-10`: preserve both records.
- **`OR-03` (`Primary: R-15`):** 7 CORE measures units provisional. Governed by `G2-EXC-001`: mandatory `TS-018` PASS at G5 blocking G6.
- **`OR-04` (`Primary: R-01, Additional: R-02`):** Absence of `CANCELLED` and `DIVERTED` in raw schema. Governed by `FP-DEC-006`: `KPI-11 = NOT_COMPUTABLE`.
- **`OR-05` (`Primary: R-10`):** Missing March 2024 (335/366 days). Governed as `OPEN_QUALITY_DEFECT`: `source_coverage_status = PARTIAL`.
- **`OR-06` (`Primary: R-03`):** Overnight rollover and local wall-clock times. Governed by `FP-DEC-007`: no naive date rollover or +24h addition.
- **`OR-07` (`Primary: R-04`):** 6 weather columns unverified. Governed by `FP-DEC-017` (`CONDITIONAL_NO_GO`): auxiliary columns preserved, decoupled from CORE.
- **`OR-08` (`Primary: R-16`):** Unverified BTS upstream origin (`METADATA_MATCH_ONLY`). Governed by `FP-DEC-014`: local SHA-256 computed at G4 (`TS-019`), BTS origin remains `IDENTITY_UNVERIFIED`.

### 2.2. Distinct Pipeline Operational Execution Risks (`OPR-`)
To separate project governance risks from physical execution risks, pipeline runtime risks are assigned the prefix **`OPR-`**:
- **`OPR-01` (`Primary: R-06`):** JVM Driver Memory Exhaustion (OOM). Mitigated by annual sequential batching, 4GB driver memory cap, and local SSD scratch directory.
- **`OPR-02`:** Windows NTFS Single-Writer Lock Contention. Mitigated by `PublisherLock` with process creation token and fail-closed abort.
- **`OPR-03`:** CSV Parser Catalyst Column Pruning & Multi-line Drift. Mitigated by explicit corrupt record projection and DC-11 partition balance verification.
- **`OPR-04`:** Promotion & Staging Filesystem Corruption. Mitigated by `SafePublisher` 7-step sequence with `shutil.copytree` and 100% SHA-256 verification.

---

## 3. SYNTHETIC FIXTURE SUITE RE-ALIGNMENT

The 14 synthetic test fixtures (`FIX-01` through `FIX-14`) map cleanly to the corrected test requirements:

| Fixture ID | Target Canonical Tests | Input Condition | Expected Result |
|---|---|---|---|
| `FIX-01` | `TS-001`, `TS-002`, `TS-003` | Valid 34-column CSV rows | 100% `ACCEPTED`, all measures valid. |
| `FIX-02` | `TS-002`, `TS-003` | Corrupt lines (unclosed quotes, bad delimiters) | Lines classified as `REJECTED`, captured in row accounting. |
| `FIX-03` | `TS-002`, `TS-003` | Unparseable date strings | Records classified as `QUARANTINED` (`INVALID_FL_DATE_CORE_ANCHOR`). |
| `FIX-04` | `TS-001`, `TS-003` | Missing core identity (null carrier/airport) | Records classified as `QUARANTINED` (`MISSING_*_CORE_ANCHOR`). |
| `FIX-05` | `TS-002`, `G3-COND-A` | Flight number $\le 0$, float decimal, non-numeric | Flagged with provisional anomaly code; evaluated per `G3-COND-A`. |
| `FIX-06` | `TS-001` | CSV with 33 columns (missing column) | Preflight aborts with `SchemaMismatchError`. |
| `FIX-07` | `TS-001`, `TS-009` | CSV with 35 columns (unexpected extra column) | Preflight aborts with `SchemaMismatchError`. |
| `FIX-08` | `TS-002`, `TS-006` | Negative delays (`DEP_DELAY = -15.0`) | `ACCEPTED`. Negative signed delay preserved exactly. |
| `FIX-09` | `TS-002`, `TS-017` | Metric invalid values (`AIR_TIME = -5.0`, `NaN`) | `ACCEPTED` in `count_records`; excluded only from submetric valid count. |
| `FIX-10` | `TS-009`, `TS-011` | 100% null auxiliary weather columns | `ACCEPTED`. Zero impact on CORE metrics per `FP-DEC-017`. |
| `FIX-11` | `TS-003`, `TS-017` | Empty input file (0 data rows) | Zero denominator handled cleanly per `DC-12`. |
| `FIX-12` | `OPR-02` | Concurrent pipeline invocation | Second process fail-fast aborts with `PublicationContentionError`. |
| `FIX-13` | `OPR-02` | Stale lock with dead owner | Fail-closed inspection prevents automatic lock stealing without proof. |
| `FIX-14` | `TS-013` (Simulation) | Injected failure during pointer switch | Staging preserved as forensic artifact; pointer safely rolled back. |

---

## 4. TEST TRACEABILITY VERDICT

Test identifiers and risk mappings have been 100% restored to their canonical definitions in `TEST_PLAN.md` and `RISK_REGISTER.md`.

**TEST TRACEABILITY VERDICT: FULLY RECONCILED & CANONICALLY TRACEABLE.**
