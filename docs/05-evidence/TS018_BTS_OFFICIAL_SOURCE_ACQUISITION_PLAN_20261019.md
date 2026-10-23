# TS-018 — Official BTS TranStats Source Acquisition and 7-Measure Parity Plan

**Project:** US Flight Performance Analysis 2016–2024  
**Gate:** G5 (`IN_PROGRESS`)  
**Status:** `SOURCE_ACQUISITION_REQUIRED`; authentic reference has **not** been downloaded or approved by this handoff.  
**Hard stop:** `G2-EXC-001 ACTIVE`, `G6 NOT_STARTED / BLOCKED`.

## 1. Exact official source and why it matters

**Bureau of Transportation Statistics (BTS), TranStats, Reporting Carrier On-Time Performance (1987–present)** — rather than the separate *Marketing Carrier On-Time Performance (Beginning January 2018)* dataset.

- Official download page: https://www.transtats.bts.gov/DL_SelectFields.aspx?QO_fu146_anzr=b0-gvzr&gnoyr_VQ=FGJ
- Official field dictionary: https://www.transtats.bts.gov/Fields.asp?gnoyr_VQ=FGJ
- Official table profile: https://www.transtats.bts.gov/TableInfo.asp?QO_fu146_anzr=b0-gvzr&gnoyr_VQ=FGJ

The agency describes this table as monthly, non-stop domestic reporting-carrier flight records with delay, taxi and elapsed-time fields. **The page being official does not by itself authenticate a local candidate CSV**.

## 2. Official-to-canonical mapping: all 7 required fields

| Canonical raw dataset field | Official BTS Reporting Carrier column | Official data dictionary meaning |
|---|---|---|
| `ARR_DELAY` | `ArrDelay` | Scheduled vs actual arrival delay, signed minutes; early arrival negative |
| `DEP_DELAY` | `DepDelay` | Scheduled vs actual departure delay, signed minutes; early departure negative |
| `TAXI_OUT` | `TaxiOut` | Taxi-out time, minutes |
| `TAXI_IN` | `TaxiIn` | Taxi-in time, minutes |
| `AIR_TIME` | `AirTime` | Flight time, minutes |
| `ACTUAL_ELAPSED_TIME` | `ActualElapsedTime` | Actual elapsed flight time, minutes |
| `CRS_ELAPSED_TIME` | `CRSElapsedTime` | Scheduled elapsed flight time, minutes |

Download with composite matching keys: `FlightDate`, `Reporting_Airline`, `Flight_Number_Reporting_Airline`, `Origin`, `Dest` (or verified aliases `FL_DATE`, `OP_CARRIER`, `OP_CARRIER_FL_NUM`, `ORIGIN`, `DEST` if genuinely present). Prefer include useful context such as `Year`, `Month`, `Cancelled`, `Diverted` for understanding null patterns without changing the seven CORE measures or inventing canceled/diverted KPI support.

## 3. Data acquisition — controlled steps

1. With a human operator/browser, go to the official download page **Reporting Carrier**; choose a **bounded** month/year within 2016–2024 **already present in the local raw dataset**. Suggested initial period: January 2016 (subject to local cohort verification). Do not use missing March 2024 as a pass-producing control sample.
2. Select the five composite-key columns and seven measure columns. Export the original BTS file/ZIP without altering the bytes. Record exact table identifier, filter period, selected fields, complete source URL as actually accessed, local acquisition timestamp with timezone, downloaded filename, source webpage or browser export evidence, and user/operator identity.
3. Calculate SHA-256 and size of original downloaded file (including ZIP if applicable). Preserve original bytes read-only in a non-production `data/reference/` location or approved evidence input directory, respecting Git ignore/secrets/size policies. Extract a working CSV without replacing the original source. Record its SHA-256 and size separately.
4. Choose a *deterministic, declared* reference cohort that has corresponding project source rows; write method/seed and duplicate-key handling. Avoid optimizing the sample for success. Cover realistic negative signed delays, zeros, positive delays and documented missingness across seven measures, without demanding impossible values.
5. Create a source-acquisition evidence record and candidate `BtsProvenanceMetadata` companion (schema in `src/flight_pipeline/kpi/bts_reconciler.py`). Never make a local companion alone the proof of source authenticity. `project_lead_approval_status` stays `PENDING_APPROVAL` until explicit separately recorded human source review.
6. Run physical-source/parity prechecks with `tools/qa/run_ts018_bts_parity.py`; inspect the code's actual expected path `data/reference/bts_transtats_sample.csv` or `docs/05-evidence/inputs/bts_transtats_sample.csv`. Before running, inspect code and backed-up outputs: it writes `docs/05-evidence/T011_TS018_BTS_RECONCILIATION_SUMMARY.json`. Safeguard historical summary as needed.
7. Independently examine key matches, duplicates, invalid keys, missing columns, numeric null/NaN/malformed values, sign and scale discrepancies, and **all seven** field statistics. Distinguish 0 exit code on synthetic harness from genuinely approved TS-018; **never** treat `SYNTHETIC_RECONCILER_VERIFIED_AUTHENTIC_BTS_PENDING` or `TS018_CANDIDATE_PARITY_VERIFIED_HUMAN_APPROVAL_PENDING` as official PASS.
8. Present a **separate** source-acquisition approval submission and independent numerical parity review to Project Lead. Only an explicit later human acceptance with valid external provenance can close TS-018 and change `G2-EXC-001`; until then keep `G5 IN_PROGRESS`, `G6 BLOCKED`.

## 4. Gating subtlety in current implementation

The current `BtsTranStatsReconciler.reconcile()` deliberately sets `summary.source_provenance_verified = False` and `summary.human_accepted = False` for locally declared companions, even if checksum and numerical comparison match. This is an *intentional trust-boundary safeguard*, not something to bypass by writing `true` to JSON or injecting booleans. A genuine BTS source-acquisition process and a separate Project Lead signoff must be recorded without manufacturing `TS018_PASS_AUTHENTIC_PARITY_ESTABLISHED`.

## 5. Deliverables expected from TS-018 acquisition stage

- `TS018_BTS_SOURCE_ACQUISITION_RECORD.md` — actual official download transaction, not invented.
- `TS018_BTS_ORIGINAL_FILE_HASHES.json` — ZIP/CSV filenames, sizes, independently computed SHA-256.
- `TS018_BTS_SAMPLE_SELECTION_PROTOCOL.md` — cohort matching method, sample count and exclusions.
- `TS018_BTS_SCHEMA_AND_PROVENANCE_REVIEW.md` — distinct source and companion metadata states.
- `TS018_BTS_CANDIDATE_PARITY_REPORT.md` — genuine comparison, all 7 fields and abnormal/mismatched records.
- `TS018_BTS_HUMAN_APPROVAL_REQUEST.md` — review-only; no auto approval.
- Raw command/output logs, timestamped environment, negative cases, immutable audit register, export package and manifest.

## 6. Current blocker

No genuine BTS CSV, official original export ZIP, or independent acquisition transaction is included in the existing T-011 Post-Closure review package. **Authentic parity cannot be completed from these documents alone.** If the official portal cannot be accessed automatically, an operator should export and provide the actual file. Do not substitute data copied from the existing project dataset, synthetic fixture or a source-attributed-but-unverifiable local CSV.
