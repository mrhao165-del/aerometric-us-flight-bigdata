# Gate G5 Residual Risk, Caveats, and Conditions Ledger
## Authoritative Accounting of Open Defects, Operational Limitations, and Governance Boundaries

**Project:** US Flight Performance Analysis 2016–2024  
**Date:** 2026-10-20 (Asia/Ho_Chi_Minh)  
**Task:** Gate G5 Exit Readiness Audit (Phase 3)  
**Parent Gate:** Gate G5 (`IN_PROGRESS`) $\rightarrow$ Gate G6 (`NOT_STARTED / BLOCKED`)  
**Status:** **AUTHORITATIVE RISK LEDGER**  

---

## 1. Executive Summary

This document formalizes all active residual risks, known quality defects, technical limitations, and operational boundaries that must be preserved and carried forward into Gate G6. No automated agent is permitted to silently resolve or downplay these risks.

---

## 2. Active Risk & Defect Inventory

| Defect / Risk Identifier | Classification | Description & Provenance | Governance Handling & Impact on Gate G6 | Authorized Signoff Authority |
|---|---|---|---|---|
| **`G2-EXC-001`** | `ACTIVE_GATE_BLOCKER` | Exception permitted G3/G4 progression while TS-018 remained pending. | **Strictly blocks Gate G6 execution.** Cannot be resolved autonomously. Requires Project Lead approval of TS-018 and Gate G5. | Project Lead only |
| **`OR-05`** | `OPEN_QUALITY_DEFECT` | March 2024 is completely missing from `flight_with_weather_2024.csv` (335/366 days present, 91.5% coverage). | **Must be reported transparently.** T-012 full-run must process available 2024 data honestly; zero synthetic flights may be fabricated. | Project Lead / Final Audit |
| **`OR-08`** | `IDENTITY_UNVERIFIED` | Raw 9-year CSV files originate from secondary Kaggle compilation; institutional chain-of-custody unproven. | **Remains active across all gates.** Record-level BTS parity on Jan 2019 establishes unit validity but does not prove upstream lineage for 2016–2024. | Project Lead / Final Audit |
| **`Option B Boundary`** | `TECHNICAL_LIMITATION` | BTS parity was verified on raw CSV (`flight_with_weather_2019.csv`), not curated Parquet (`PARQUET_PARITY_NOT_TESTED`). | **Documented limitation.** Parquet transformation correctness is verified separately by T-010/T-011. Option A (2016 Parquet parity) remains available as alternative. | Project Lead / Reviewer |
| **`Unmatched 6,827 Flights`** | `EMPIRICAL_DELTA` | 6,827 active operating flights present in BTS Part 234 Jan 2019 are absent from the Kaggle 2019 CSV. | **Factual disclosure.** Recorded as secondary compilation filtering; no unproven causal attribution (such as weather-join drops) is asserted. | Data Quality Auditor |
| **`FP-DEC-017 Weather`** | `CONDITIONAL_NO_GO` | Weather columns lack standardized unit provenance and complete temporal-spatial coverage. | **Weather excluded from CORE pipeline.** Core 8 KPIs operate strictly on flight mechanics. 34 weather columns retained in Parquet schema as nullable. | Project Lead |
| **`Windows Local Capacity`** | `RESOURCE_CONSTRAINT` | Windows local workstation with limited RAM (4GB driver budget) and SSD disk budget. | **Mandates sequential year-by-year execution.** T-012 cannot run all 9 years simultaneously; requires checkpoints and disk monitoring. | PySpark Architect |

---

## 3. Detailed Forensic Risk Profiles

### 3.1 Defect OR-05: Missing March 2024 Data
- **Factual Evidence:** A full temporal scan of `flight_with_weather_2024.csv` confirms that dates from `2024-03-01` to `2024-03-31` are completely absent. All other 11 months have complete daily representation.
- **Mandatory Policy for Gate G6 (`T-012`):**
  1. The pipeline must ingest the 335 available days of 2024 without throwing a fatal crash.
  2. The quality reporting must record `source_coverage_status = PARTIAL` and disclose the 31-day gap.
  3. **Zero synthetic flight generation:** It is strictly prohibited to interpolate, synthesize, or substitute mock records for March 2024.
  4. Multi-year trend analyses (`T-014`, RQ-01..05) must include explicit visual caveats regarding 2024 seasonal comparisons.

### 3.2 Limitation OR-08: Secondary Upstream Lineage
- **Factual Evidence:** Physical SHA-256 checksums are pinned for all 9 raw CSV files (`SOURCE_MANIFEST.json`). However, because these files were acquired from a public secondary compilation on Kaggle, the exact extraction scripts and intermediate filters used to generate them from raw BTS/NOAA feeds are external to this repository.
- **Mandatory Policy:**
  1. Record-level numeric parity with BTS Part 234 on January 2019 confirms that the numeric fields and column semantics are authentic BTS measures.
  2. It does not certify that no records were filtered out upstream (as evidenced by the 6,827 unmatched active flights).
  3. The limitation must be formally disclosed in all academic, technical, and governance deliverables.

### 3.3 Option B Protocol: `PARQUET_PARITY_NOT_TESTED`
- **Factual Evidence:** Option B evaluated 10,500 comparisons between raw CSV input and authentic BTS reference ZIP. No curated Parquet exists for 2019 in staging.
- **Mandatory Policy:**
  1. This limitation is explicitly acknowledged in the formal Option B decision proposal (`FP-DEC-PROP-019`).
  2. The Project Lead must explicitly approve Option B with this condition.
  3. If formal stakeholder requirements demand physical Parquet output comparison, Option A (BTS January 2016 vs 2016 staging Parquet) must be executed.

---

## 4. Operational Invariants for Gate G6

Prior to commencing full-run execution (`T-012`):
1. **Explicit Project Lead Directive:** `G2-EXC-001` must be formally closed, and `G5` must be transitioned to `PASS` by human signature.
2. **Sequential Execution Guard:** Processing must execute one calendar year at a time, checking DC-11/12 reconciliation at each annual boundary.
3. **Immutable 2016 Baseline:** The existing physical 2016 staging Parquet (`data/staging/`) must not be overwritten or corrupted.
