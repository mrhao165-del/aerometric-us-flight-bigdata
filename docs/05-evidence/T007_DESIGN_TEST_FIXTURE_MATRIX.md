# T007 DESIGN TEST FIXTURE MATRIX — SYNTHETIC FIXTURES & CONTRACT TRACEABILITY

**Document ID:** `DOC-T007-DESIGN-06-TEST-MATRIX`  
**Task ID:** `T-007` (Raw CSV Ingestion Pipeline)  
**Phase:** `DESIGN ONLY`  
**Gate:** `G4` (`PLANNED / NOT_COMPLETED`)  
**Design Authority:** Independent QA Auditor & Big Data Test Engineer  
**Traceability Baselines:** `TEST_PLAN.md` (TS-001, TS-009, TS-019), `DATA_CONTRACT.md` (DC-11, DC-12), `G2-EXC-001`, `G3-COND-A/B/C`, `FP-DEC-017`  

---

## 1. CONTRACT REQUIREMENTS TRACEABILITY MATRIX

The testing strategy for T-007 maps directly to project-level requirements, data contracts, and governance conditions:

| Req / Test ID | Description | Binding Standard / Authority | Target Fixture(s) | Verification Strategy | Implementation Task |
|---|---|---|---|---|---|
| **REQ-SCHEMA-34** | Strict 34-column schema, headers, and types | `TS-001`, `DATA_CONTRACT.md` §3 | `FIX-01`, `FIX-06`, `FIX-07` | Schema assertion, fail-fast on mismatch | `T007-01`, `T007-06` |
| **REQ-DC11-CONS** | Partition conservation: $N_{\text{raw}} = N_{\text{acc}} + N_{\text{quar}} + N_{\text{rej}}$ | `DATA_CONTRACT.md` DC-11 | `FIX-01` through `FIX-05` | Exact integer equation assert | `T007-03`, `T007-05` |
| **REQ-DC11-EXCL** | Mutually exclusive row classification | `DATA_CONTRACT.md` DC-11 | `FIX-01` through `FIX-05` | Disjoint set intersection check | `T007-03` |
| **REQ-DC12-MVR** | Metric validity independent of record acceptance | `DATA_CONTRACT.md` DC-12 | `FIX-08`, `FIX-09`, `FIX-10` | Non-finite / negative metric audit | `T007-03` |
| **REQ-NEG-DELAY** | Negative delay preservation (early flights) | `KPI_SPEC.md` §2.1 | `FIX-08` | Preserves negative signed double | `T007-03` |
| **REQ-G3-COND-A** | Quarantine non-positive flight numbers | `G3-COND-A` (Provisional Rule) | `FIX-05` | Routes `FL_NUM <= 0` to quarantine | `T007-03` |
| **REQ-DEC-017** | Weather nullable, independent of CORE KPI | `FP-DEC-017` (CONDITIONAL_NO_GO) | `FIX-10` | Weather nulls accepted without drop | `T007-03` |
| **REQ-SINGLE-WR** | Single-writer concurrency lock & fail-fast | `OR-02`, Storage Safety | `FIX-12`, `FIX-13` | Multi-process lock contention test | `T007-04` |
| **REQ-TS-009** | Atomic publication & pointer integrity | `TS-009`, `SafePublisher` | `FIX-14` | Verify `PAR1` bytes, pointer update | `T007-05` |
| **REQ-OR-05** | Year 2024 missing March 2024 tracking | `OR-05` (OPEN_QUALITY_DEFECT) | Real 2024 Source / Manifest | `RunManifest` coverage flag | `T007-05` |

---

## 2. SYNTHETIC TEST FIXTURE SUITE SPECIFICATION

To test the ingestion pipeline safely without scanning 54.7M rows during development, a comprehensive synthetic test suite of 14 fixtures (`FIX-01` through `FIX-14`) is specified:

| Fixture ID | Fixture Purpose | Description of Data Inputs | Expected Pipeline Outcome |
|---|---|---|---|
| **`FIX-01`** | **Golden Positive Baseline** | 100 rows of valid 34-column CSV data covering multiple carriers, airports, and valid dates. | 100 `ACCEPTED`, 0 `QUARANTINED`, 0 `REJECTED`. All 7 measures valid. |
| **`FIX-02`** | **Malformed Syntax Lines** | 10 valid rows + 5 corrupt lines (unclosed quotes, mismatched commas, unescaped newlines). | 10 `ACCEPTED`, 0 `QUARANTINED`, 5 `REJECTED` (`REJECTED_PARSE_ERROR`). |
| **`FIX-03`** | **Malformed Date Strings** | 10 rows with unparseable dates: `"2020-02-31"`, `"INVALID"`, `""`, `"0000-00-00"`. | 0 `ACCEPTED`, 10 `QUARANTINED` (`QUARANTINE_MALFORMED_DATE`), 0 `REJECTED`. |
| **`FIX-04`** | **Missing Structural Anchors** | 10 rows with missing identity: null `OP_CARRIER`, null `ORIGIN`, or null `DEST`. | 0 `ACCEPTED`, 10 `QUARANTINED` (`QUARANTINE_NULL_*`), 0 `REJECTED`. |
| **`FIX-05`** | **Invalid Flight Numbers** | 10 rows with `OP_CARRIER_FL_NUM` as `0`, `-123`, `null`, or `"UNKNOWN"`. | 0 `ACCEPTED`, 10 `QUARANTINED` (`QUARANTINE_INVALID_FL_NUM` per `G3-COND-A`). |
| **`FIX-06`** | **Missing Structural Column** | CSV containing only 33 columns (omits `ORIGIN`). | Job immediately aborts with `SchemaMismatchError`. No staging written. |
| **`FIX-07`** | **Unexpected Extra Column** | CSV containing 35 columns (unexpected extra `DISTANCE` column appended). | Job immediately aborts with `SchemaMismatchError`. |
| **`FIX-08`** | **Negative Signed Delays** | 20 rows with early departures/arrivals: `DEP_DELAY = -15.0`, `ARR_DELAY = -30.0`. | 20 `ACCEPTED`. Delay values preserved exactly as negative doubles. |
| **`FIX-09`** | **Metric Invalid Values** | 20 rows where `AIR_TIME = -5.0`, `TAXI_OUT = NaN`, `DEP_DELAY = Inf`. | 20 `ACCEPTED` records. Single metric invalid flags set. Records in `count_records`. |
| **`FIX-10`** | **Null Auxiliary Weather** | 20 rows with 100% null values in all 6 weather fields (`O_TEMP`, `D_WSPD`, etc.). | 20 `ACCEPTED`. Core metrics unaffected. Complies with `FP-DEC-017`. |
| **`FIX-11`** | **Empty Input File** | CSV containing only the 34-column header line, 0 data rows. | 0 `ACCEPTED`, 0 `QUARANTINED`, 0 `REJECTED`. IAR returns `ZERO_DENOMINATOR`. |
| **`FIX-12`** | **Single-Writer Contention** | Two concurrent pipeline processes attempting to execute simultaneously. | First acquires lock. Second fails immediately with `PublicationContentionError`. |
| **`FIX-13`** | **Stale Lock Recovery** | `.publisher.lock` exists with PID of a dead process and stale timestamp (> 2h). | Lock quarantined to `stale_locks/`. New process acquires lock successfully. |
| **`FIX-14`** | **Publication Failure Recovery**| Simulated disk failure during staging write before pointer switch. | Staging retained with `_FAILED` marker. `latest_run_id.txt` completely untouched. |

---

## 3. DEFERRED OBLIGATIONS & FUTURE GATE BOUNDARIES

In accordance with `AGENTS.md` and official G2/G3 signoffs, the following testing obligations are explicitly recognized as deferred and must **NOT** be claimed as passed during T-007 design:

1. **`TS-018` (CORE Measures Physical Units & BTS Alignment):**
   - Per `G2-EXC-001`, full empirical verification of the 7 numerical measures against official BTS distributions remains provisional. Full verification is an absolute gate blocker for Gate **G5** prior to Gate **G6**.
2. **`TS-013` (Full-Scale Fault Injection Suite):**
   - Full cluster and filesystem fault injection across 54.7M rows is formally assigned to Gate **G5**.
3. **`TS-014` (Resource & Performance Benchmarks):**
   - End-to-end multi-core throughput and disk I/O benchmarks for full 54.7M rows will be executed during Gate **G4 / G5**.

---

## 4. TEST MATRIX DESIGN VERDICT

The test fixture matrix provides complete positive, negative, and edge-case coverage for T-007 implementation while strictly respecting deferred testing boundaries.

**TEST MATRIX VERDICT: FULLY TRACEABLE & APPROVED.**
