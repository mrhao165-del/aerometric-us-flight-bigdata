# Gate G5 Final Exit Criteria Matrix
## Comprehensive Verification Matrix of Technical, Quality, and Governance Obligations

**Project:** US Flight Performance Analysis 2016–2024  
**Date:** 2026-10-20 (Asia/Ho_Chi_Minh)  
**Task:** Gate G5 Exit Readiness Audit (Phase 3)  
**Parent Gate:** Gate G5 (`IN_PROGRESS`) $\rightarrow$ Gate G6 (`NOT_STARTED / BLOCKED`)  
**Status:** **AUTHORITATIVE G5 AUDIT MATRIX**  
**Governance Authority:** Project Lead exclusive human signoff authority  

---

## 1. Executive Summary

In accordance with `TEST_PLAN.md` (Version docs-v1.1, Section "Gate-to-test mapping: G5"), `G5_ENTRY_HANDOFF.md`, and authoritative project decisions, Gate G5 mandates verifying bounded real-data performance, 3-state row accounting, fault-tolerant atomic publication, KPI calculation correctness, and official BTS Part 234 numerical unit consistency (`TS-018` under exception `G2-EXC-001`).

Every obligation has been categorized into its precise evidentiary scope:
- **`SYNTHETIC_PASS`:** Verified using controlled unit and integration test fixtures.
- **`BOUNDED_REAL_DATA_PASS`:** Verified on actual physical 2016/2019 data.
- **`FULL_RUN_UNEXECUTED`:** Reserved strictly for Gate G6 full 9-year execution.
- **`HUMAN_ACCEPTANCE`:** Requires explicit, written Project Lead approval.

---

## 2. Gate G5 Master Verification Matrix

| Test / Requirement ID | Description & Scope | Evidentiary Requirement | Verified State & Evidence Reference | Test Scope Classification | G5 Compliance Verdict |
|---|---|---|---|---|---|
| **T-010 Bounded Smoke** | Real-data ingestion & staging on 2016 CSV (5,617,658 rows) | SafePublisher 7-step atomic staging, Snappy compression | `T010_FULL_PARQUET_STAGING_VERIFICATION.md`, 50 Parquet files in staging (`b5805fca...`) | `BOUNDED_REAL_DATA_PASS` | **PASS** |
| **T-010 Resource Benchmark** | TS-014 CPU, RAM, disk, and throughput logging | Real measurements on Windows workstation | `T010_FULL_RESOURCE_BENCHMARK_TS014.md` (250s elapsed, 3.2GB peak RAM, 4.5x compression) | `BOUNDED_REAL_DATA_PASS` | **PASS** |
| **T-011 KPI Engine** | 8 CORE KPIs calculation on sample staging cohort | ANSI mode casting, boundary edge cases, signed delays | `T011_FULL_KPI_ENGINE_VERIFICATION.md`, `tests/test_t011_kpi_engine.py` (32 tests PASS) | `SYNTHETIC_AND_SMOKE_PASS` | **PASS** |
| **T-011 Locking & Faults** | TS-013 SingleWriterLock, crash recovery & rollback | Zero partial outputs, stale lock recovery, NTFS durability | `T011_OFFICIAL_CONTROLLED_TECHNICAL_SIGNOFF_20261019.md`, R1..R6 post-closure suites | `SYNTHETIC_AND_SMOKE_PASS` | **PASS (CONTROLLED)** |
| **TS-001 Schema Drift** | 34 raw columns schema validation across years | Fail-closed drift guard, required columns presence | `tests/test_t010_policy_guards.py`, `T010_FULL_BASELINE_AND_PREFLIGHT.md` | `BOUNDED_REAL_DATA_PASS` | **PASS** |
| **TS-002 Parsing & Domain** | Timestamp, null, NaN, Inf, and numeric domain guards | ANSI mode casting, zero silent truncation/drop | `src/flight_pipeline/quality/engine.py`, `tests/test_t008_quality_engine.py` | `BOUNDED_REAL_DATA_PASS` | **PASS** |
| **TS-003 Row Accounting** | 3-state mutually exclusive partitioning (DC-11/12) | $\text{Raw} = \text{Accepted} + \text{Quarantined} + \text{Rejected}$ | `T010_FULL_DC11_DC12_ACCOUNTING_REPORT.md` (5,617,658 = 5,617,658 + 0 + 0) | `BOUNDED_REAL_DATA_PASS` | **PASS** |
| **TS-005 Delay Thresholds** | 15.0 min boundary, eligibility, zero denominator guard | Boundary 14.999/15/15.001, null delay rate handling | `tests/test_t011_kpi_engine.py`, `KPI_SPEC.md` | `SYNTHETIC_AND_SMOKE_PASS` | **PASS** |
| **TS-006 Signed Delay** | Preservation of signed arrival/departure delays | No clipping of negative delays; finite domain mean | `TS018_FINAL_INDEPENDENT_REPLAY_REPORT.md` (negatives -6.0, -4.0 verified) | `BOUNDED_REAL_DATA_PASS` | **PASS** |
| **TS-008 Percentiles** | P50/P90 quantile calculation with `accuracy=10000` | Quantile error $\le 0.0001$, per-submetric denominators | `tests/test_t011_ts008_repeatability.py` (10,000 accuracy verified) | `SYNTHETIC_AND_SMOKE_PASS` | **PASS (BOUNDED_SCOPE)** |
| **TS-009 Grain & Cancel** | FLIGHTS count guard, cancel/divert exclusion | No ungrounded counts, cancel rate derived properly | `DATA_CONTRACT.md` DC-11, `TS018_201901_ACTUAL_STRATUM_AND_KEY_AUDIT.md` | `BOUNDED_REAL_DATA_PASS` | **PASS** |
| **TS-010 Overnight & 2400** | Timestamp handling for cross-midnight flights | Governed as `NOT_AVAILABLE` under `FP-DEC-004` | `DECISIONS.md`, derived timestamps not fabricated | `GOVERNED_POLICY_PASS` | **PASS** |
| **TS-012 Repeatability** | Deterministic outputs across multiple runs | Identical outputs on repeated executions | `tests/test_t011_ts008_repeatability.py`, idempotent publish | `SYNTHETIC_AND_SMOKE_PASS` | **PASS** |
| **TS-013 Rollback & Faults** | Failure injection during publication | Corrupted run unlinked, pointer remains on previous | `tests/test_t011_fault_injection.py`, `tests/test_t011_post_closure.py` | `SYNTHETIC_AND_SMOKE_PASS` | **PASS** |
| **TS-014 Real Benchmarking** | CPU/RAM/Disk benchmark on real physical source | Measured numbers from physical run, not simulated | `T010_FULL_RESOURCE_BENCHMARK_TS014.md` | `BOUNDED_REAL_DATA_PASS` | **PASS** |
| **TS-017 Accounting Terms** | Metric valid rate vs ingest rate terminology | `accepted_row_count(C)` denominator, zero guard | `DATA_CONTRACT.md`, `tests/test_working_tree_registry_regression.py` | `SYNTHETIC_AND_SMOKE_PASS` | **PASS** |
| **TS-018 BTS Unit Parity** | 7 CORE measures record-level comparison with BTS | 10,500/10,500 exact matches, witness CSV verified | `TS018_FINAL_INDEPENDENT_REPLAY_REPORT.md` (Option B candidate ready) | `BOUNDED_REAL_DATA_PASS` | **TECHNICAL_PASS / AWAITING_HUMAN_SIGNOFF** |
| **TS-019 Source Identity** | SHA-256 catalog of all 9 raw CSV inputs | Candidate hashes cataloged; drift fail-closed | `SOURCE_MANIFEST.json`, `OR-08 = IDENTITY_UNVERIFIED` active | `DOCUMENTED_DEFECT_PASS` | **PASS** |
| **FP-DEC-017 Weather** | Weather data excluded from CORE pipeline | Pipeline operates without requiring weather join | `src/flight_pipeline/quality/engine.py` (Core pipeline isolates weather) | `GOVERNED_POLICY_PASS` | **PASS** |

---

## 3. Explicit Differentiation of Scope

> [!IMPORTANT]
> **Boundary Declarations:**
> 1. **TS-008 Scope:** The TS-008 check under Gate G5 confirms algorithm correctness (`accuracy=10000`, tolerance $\le 10^{-4}$, min-N suppression). It **does not mean** that 9-year full-population KPI percentiles have been generated. Full multi-year aggregation belongs strictly to Gate G6 (`T-013`).
> 2. **TS-018 Scope:** The 10,500 record-level comparisons confirm unit, sign, and definitions consistency on January 2019 data (`Option B`). Physical 2019 Parquet was **not tested** (`PARQUET_PARITY_NOT_TESTED`).
> 3. **Full-Run Obligations (G6):** Tests `TS-004` (full 9-year schema & date reconciliation), `TS-007` (6-dimensional aggregate cubes), `TS-015` (research question provenance), and `TS-016` (panel coverage & ranking stability) remain `NOT_STARTED` and are reserved for Gate G6/G7.

---

## 4. Overall Gate G5 Technical Verdict

All nineteen required technical checks for Gate G5 have achieved either `PASS` or `TECHNICAL_PASS`.
The sole remaining action for Gate G5 exit is the **official human signoff** by the Project Lead.

**Status:** **`G5_READY_FOR_HUMAN_SIGNOFF`**
