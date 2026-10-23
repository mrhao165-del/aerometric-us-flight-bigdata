# TS-018 January 2019 — Independent Evidence Audit
**Review date:** 2026-10-20 (Asia/Ho_Chi_Minh)  
**Verdict:** **HOLD TS-018 HUMAN SIGNOFF — TARGETED EVIDENCE CORRECTION**  
**Scope:** Submitted candidate ZIP/manifest, contained source and evidence, and independently supplied BTS January 2019 ZIP. No project 2019 RAW CSV or actual Parquet bytes were supplied in this review; therefore no independent replay of the 10,500 cross-source comparisons is claimed.

## 1. Verified package integrity
- ZIP: `TS018_201901_CANDIDATE_REVIEW_PACKAGE.zip`, 2,451,874 bytes, SHA-256 `a752d26ba61e95171dd27abd7c383c3e422409b82e7603c05c549848e5904f3c`.
- 712/712 member bytes and SHA-256 match the manifest. Archive CRC `testzip()` passed; no duplicate, missing, or extra names.
- BTS external archive independently present at `T_ONTIME_REPORTING_20261019_112232.zip`: SHA-256 `342de99f65561fb856b524c704f2ad3851f8015f52251668ece346dff1350ae6`; 583,985 rows, 31 January 2019 days.
- Compared with T011 controlled signoff package: 13 files added, 3 changed, 0 deleted. The main reconciliation engine source remained unchanged; newly added `tools/qa/run_ts018_bts_adapter.py` executed raw-mode comparisons per Windows log.

## 2. Independent critical evidence finding TS018-I01 (HIGH)
The document `docs/05-evidence/TS018_201901_SEVEN_FIELD_PARITY_REPORT.md` labels the following **three records as real matched comparison examples**, with seven exact values each:
- `2019-01-01 | DL | 1142 | ATL | LGA`
- `2019-01-12 | AA | 2401 | DFW | ORD`
- `2019-01-20 | WN | 582 | DEN | PHX`

An independent full scan of the exact January 2019 external BTS ZIP using date + carrier + flight number + origin + destination returned **none of these composite keys**. The numerical values cited for these records therefore cannot be attributed to this BTS file as reported. This invalidates those example entries and lowers the trustworthiness of the narrative. It **does not by itself refute** the reported 1,500-record algorithmic parity because neither full cohort nor raw dataset was included.

**Required closure:** Issue non-destructive evidence errata; delete/supersede unsupported examples, automatically export verified sample keys and both sources' seven values, and verify every illustrative record against the physical BTS source. Never silently replace a historical signed document.

## 3. Sampling evidence finding TS018-I02 (MEDIUM/HIGH)
`docs/05-evidence/TS018_201901_KEY_COVERAGE_AND_SAMPLE_PROTOCOL.md` reports 100 sampled `Edge / Boundary Cases` from an available 18,022 `high delay / null` stratum. Actual runner selects its `other_sample` only when dataset `ARR_DELAY is None`; it does **not select high-delay flights as a separate edge stratum**. When the stratum is undersized, the code fills the remainder from other matched flights but **does not record actual per-stratum counts**.

Independent BTS file scan: **18,022** January 2019 flights have missing `ARR_DELAY`; each is cancelled (16,726) or diverted (1,296), and **zero** active non-diverted flights have missing `ARR_DELAY`. The Agent asserts that these statuses are excluded from the project's matched dataset. Thus the claim of 100 null-stratum records cannot be substantiated from the disclosed algorithm and coverage policy; 18,022 appears to be BTS-side null count, not an available raw dataset null stratum.

**Required closure:** Produce actual per-stratum counts from the runnable cohort; report top-up sample separately; if zero null records exist, show `null_stratum=0` and cover missingness with a distinct BTS-only controlled test (not falsely marked as matched parity). Retain full deterministic selection evidence and real sample hashes.

## 4. Insufficient cross-source reproducibility TS018-I03 (MEDIUM)
The runner prints aggregate counts and a 0-row discrepancy CSV but **does not export the list of 1,500 selected flight keys and corresponding paired numeric values**. The submitted bundle omits the user's large raw 2019 CSV and physical BTS ZIP (the ZIP was independently available separately to this reviewer). Therefore the reported `10,500 / 10,500 exact` remains **agent-log-supported, not independently replayed**. The raw runner also overwrites duplicate dataset keys into a `dict` without reporting raw row counts or duplicate collisions, so `559,136 indexed unique keys` alone is insufficient to prove zero original duplicates.

**Required closure:** Save a compact 1,500-row machine-readable witness with source values, seed, stratum/selection reason and exact composite keys; separate raw input file SHA-256/bytes, raw row count and duplicates; provide independent verifier that **reads both authoritative inputs** (not a hand-authored or BTS-copied witness). For count of unmatched active flights (6,827), distinguish proven category from *hypothesized weather-join filtering* unless source lineage supports causation.

## 5. Gate and source trust
- Proven: physical BTS candidate checksum, ZIP/CRC/schema and January 2019 coverage, referenced evidence package integrity.
- Agent-reported, not reproduced here: 559,136 paired matching keys and 10,500 exact field matches against project raw CSV.
- Agent has reported no January 2019 curated Parquet; bounded `--allow-raw-preflight` uses **raw CSV**, not Parquet, irrespective of any `curated_parquet_dir` found later. Its label must never imply curated parity.
- SOURCE_PROVENANCE_VERIFIED `False`; companion acquired_by / download receipt / operator ID unavailable. Request documented human attestation before approved provenance.
- FP-DEC-018 remains APPROVED_WITH_CONDITIONS, T011 technical signoff remains CONTROLLED; TS-018 OPEN, G2-EXC-001 ACTIVE, G5 IN_PROGRESS, G6 NOT_STARTED/BLOCKED.

## 6. Recommendation
**Do not sign TS-018, resolve G2-EXC-001, or advance G5 yet.** Fix three evidence issues through one narrow read-only rerun, then independent verification. **Option B** (2019 original raw vs BTS, no publication) is a proportionate *candidate* to satisfy the *raw source numeric unit verification* subrequirement, but **only if** Project Lead explicitly approves this limitation after corrected proof; it cannot establish curated Parquet parity. Option A (2016 BTS vs attested 2016 Parquet) is stronger if formal G5 contract requires physical output parity. Review `TEST_PLAN.md` and `G2-EXC-001` wording before choosing; do not imply this audit pre-authorizes either option.

**Independent reproduction:** `TS018_201901_INDEPENDENT_EVIDENCE_CHECK_20261020.py` + output JSON; accepts the authentic BTS original ZIP, performs a full read-only scan and confirms the three invalid examples and the null-status accounting.
