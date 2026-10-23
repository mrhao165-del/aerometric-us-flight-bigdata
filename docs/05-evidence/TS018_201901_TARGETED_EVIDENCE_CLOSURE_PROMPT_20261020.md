# ANTIGRAVITY MASTER PROMPT — TS-018 JAN 2019 TARGETED EVIDENCE CORRECTION

**Role:** Independent Big Data Auditor + Spark/PySpark QA Engineer + Evidence Custodian.
**Scope:** Evidence correctness, reproducible sampling and provenance only. **Not a new G5/G6 implementation or blanket refactor.**

## 0. Baseline and invariants
Read `AGENTS.md`, `docs/03-quality/TEST_PLAN.md`, `docs/02-design/DATA_CONTRACT.md`, `docs/02-design/DECISIONS.md`, `docs/04-execution/PROJECT_STATE.md`, TS-018 evidence, and `tools/qa/run_ts018_bts_adapter.py`, `src/flight_pipeline/kpi/bts_reconciler.py`.

Baseline candidate `TS018_201901_CANDIDATE_REVIEW_PACKAGE.zip` (SHA-256 `a752d26ba61e95171dd27abd7c383c3e422409b82e7603c05c549848e5904f3c`), and external BTS ZIP in `data/reference/bts_transtats/original/T_ONTIME_REPORTING_20261019_112232.zip` (SHA-256 `342de99f65561fb856b524c704f2ad3851f8015f52251668ece346dff1350ae6`).

Read independent audit `TS018_201901_INDEPENDENT_AUDIT_20261020.md` and rerun accompanying `TS018_201901_INDEPENDENT_EVIDENCE_CHECK_20261020.py` on the exact BTS ZIP. Baseline-reproduce all three findings **before changes**.

Do not touch raw 9-year inputs, original BTS ZIP, accepted staging Parquet, KPI specifications or publication pointers. Git-ignore all reference binaries. No 2019 Parquet ingestion. No G6 execution. Do not edit historical signed documentation in place.

## 1. TS018-I01 HIGH — Unsupported record examples
Inspect three claims in `TS018_201901_SEVEN_FIELD_PARITY_REPORT.md`:
- `2019-01-01 | DL | 1142 | ATL | LGA`
- `2019-01-12 | AA | 2401 | DFW | ORD`
- `2019-01-20 | WN | 582 | DEN | PHX`

Independently scan the official physical BTS CSV; log present/missing per full composite key. These keys were absent in independent replay. Produce a **superseding errata**; replace examples only with records produced programmatically from authentic matched inputs. Never invent flight IDs or numbers. If any value is unavailable, print unavailable instead of filling it.

## 2. TS018-I02 MEDIUM/HIGH — False stratum representation
Compare actual code with `TS018_201901_KEY_COVERAGE_AND_SAMPLE_PROTOCOL.md`.

Calculate exact, independently logged counts for 4 strata **in matched project cohort**, not whole BTS universe: negative ARR_DELAY, zero, positive and ARR_DELAY null. Report actual selected counts and distinct top-up count. Do not call top-up flights “null cases” or “high-delay edge cases” unless code explicitly selects them on that criterion.

Check BTS null `ARR_DELAY` by CANCELLED/DIVERTED flags: independent reference found 18,022 nulls, all 16,726 canceled or 1,296 diverted, zero other null. Explain why source reports 18,022 in a matched cohort (if it really does). No unproven weather-join attribution for 6,827 unmatched active flights.

## 3. TS018-I03 MEDIUM — Provide verifiable sample receipt
Rerun bounded raw preflight with explicit flag. Guard against synthetic fallback, wrong year and missing raw source; print physical source paths and SHA-256 for both BTS and project 2019 raw CSV. Report **raw row counts, unique keys and duplicate counts separately** on BOTH sides; a dict silently overwriting duplicates is prohibited for conclusive reporting. Flag ambiguous keys and stop on invalid/malformed numerics before claiming seven-field parity.

Produce a compact `TS018_201901_MATCHED_SAMPLE_WITNESS.csv` or Parquet containing **exactly 1,500 selected composite keys**, seven values on BOTH sources, stratum, SHA-256 sample selection score/seed, and mismatch/null statuses. Derive it exclusively by reading the immutable physical files, never by typing sample entries. Export sample receipt SHA-256 and bounded aggregate discrepancy register. Protect against witness being populated from BTS alone by an independent verification script reading BOTH physical source inputs and comparing each row.

Keep the comparison name precise: `2019_raw_source_vs_BTS_candidate`, **not** curated Parquet parity. If formal protocol requires Parquet, record `PARQUET_PARITY_NOT_TESTED` and provide the 2016 Parquet alignment option rather than altering rules.

## 4. Provenance, governance, testing
Preserve `SOURCE_PROVENANCE_VERIFIED=False`, `HUMAN_ACCEPTED=False`, TS-018 OPEN, `G2-EXC-001` ACTIVE, G5 IN_PROGRESS, G6 BLOCKED. You cannot grant external source authenticity or accept Option B without the Project Lead.

Request explicit human source-acquisition attestation with honest download URL, table, period, local file SHA-256, timestamp and operator receipt state. Do not invent session IDs or download receipts. Source can remain provenance-pending if not proven.

Run on Windows actual code tests including source mismatch, nonexistent report examples, correct sample strata, duplicate keys, malformed numeric, negative delays, nulls, and synthetic fallback prohibition. Capture machine-generated exact commands, exit codes and raw logs. Only report tests actually executed.

## 5. Handoff, stop criteria and deliverables
Create **new** evidence under `docs/05-evidence/`:
- `TS018_201901_EVIDENCE_CORRECTION_ERRATA.md`
- `TS018_201901_ACTUAL_STRATUM_AND_KEY_AUDIT.md`
- `TS018_201901_MATCHED_SAMPLE_WITNESS.csv`
- `TS018_201901_INDEPENDENT_REPLAY_PROTOCOL.md`
- `TS018_201901_RAW_CLOSURE_LOG.txt`
- `TS018_201901_CORRECTED_CANDIDATE_READINESS.md`
- an independent two-source replay script and SHA-256 manifest with exact code version

Export `TS018_201901_EVIDENCE_CLOSURE_REVIEW_PACKAGE.zip` + a full byte/SHA-256 manifest **outside the repository**. Do not bundle 15GB project raw or rewrite historical signed artifacts; note where those originals reside for reviewer. If source files are missing, STOP with `BLOCKED_SOURCE_NOT_AVAILABLE` and export factual diagnostics.

**No autonomous TS-018 PASS, no human signoff impersonation, no resolve of G2-EXC-001, no G5 PASS and no G6 start.** Submit corrected evidence to Independent Reviewer and Project Lead to choose Option A or Option B.
