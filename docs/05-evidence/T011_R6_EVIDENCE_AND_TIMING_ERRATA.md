# T011-R6 Evidence, Timing & Documentation Supersession Errata

**Project:** US Flight Performance Analysis 2016–2024  
**Task:** T-011 R6 — Controlled Final Lock Safety Closure  
**Finding References:** R6-F03 (Documentation Reading Attestation), R6-F04 (Per-Module Timing Claims)  
**Parent Gate:** G5 — `IN_PROGRESS`  
**Downstream Gate:** G6 — `NOT_STARTED / BLOCKED` (`G2-EXC-001` Hard Stop)  
**Authority:** Project Lead only.  

---

## 1. Executive Summary

This formal errata document reconciles two evidence-governance findings identified during independent review of `T011_R5_REVIEW_PACKAGE.zip`:
1. **R6-F03 (Document Attestation Hashes):** Table 1 of `T011_R5_BASELINE_AND_DOCUMENT_AUDIT.md` erroneously listed estimated/synthesized byte counts and SHA-256 hashes instead of freshly calculated filesystem values.
2. **R6-F04 (Per-Module Timing Claims):** Table 1 of `T011_R5_FULL_REGRESSION.md` assigned specific decimal seconds to individual test modules, whereas standard `unittest discover` reports only the aggregate runtime (`Ran 304 tests in 391.831s: OK`), resulting in unverified breakdown claims.

---

## 2. Errata Item 1: Documentation Reading Attestation Hashes (R6-F03)

### Discrepancy Identified
In `T011_R5_BASELINE_AND_DOCUMENT_AUDIT.md`, 12 canonical documents were reported with inaccurate byte sizes and hashes (e.g. `README.md` was claimed as 13,833 bytes instead of physical 3,946 bytes; `DATA_CONTRACT.md` as 15,312 bytes instead of 7,238 bytes).

### Root Cause
In T011-R5, an unverified markdown table template was populated without executing a physical disk scanning script. The physical repository files were never altered; the error was entirely typographical and evidentiary within the R5 report.

### Formal Resolution
- Table 1 of `T011_R5_BASELINE_AND_DOCUMENT_AUDIT.md` is hereby **FORMALLY SUPERSEDED**.
- Authoritative physical hashes are documented in [`docs/05-evidence/T011_R6_BASELINE_AND_DOCUMENT_AUDIT.md`](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/docs/05-evidence/T011_R6_BASELINE_AND_DOCUMENT_AUDIT.md) and [`docs/05-evidence/T011_R6_DOCUMENT_HASH_RECONCILIATION.md`](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/docs/05-evidence/T011_R6_DOCUMENT_HASH_RECONCILIATION.md).
- Automated regression guard `test_r6_f03_baseline_document_hashes_match_physical_files` in `tests/test_t011_r6_counterexamples.py` mathematically guarantees that every attested hash in R6 matches disk 100%.

---

## 3. Errata Item 2: Unittest Timing Disaggregation (R6-F04)

### Discrepancy Identified
In `T011_R5_FULL_REGRESSION.md`, individual module runtimes (e.g. `test_t007_pipeline_integration.py: 62.450s`, `test_t011_ts008_repeatability.py: 72.100s`) were presented without an underlying instrumented per-module log. The aggregate duration of `391.831s` was authentic, but the individual rows were unverified estimations.

### Formal Resolution
- Table 1 of `T011_R5_FULL_REGRESSION.md` is hereby **FORMALLY SUPERSEDED**.
- In T011-R6, two distinct, authentic execution streams are established and separately documented:
  1. **Official Aggregate Discover Run:** Standard `python -m unittest discover -s tests -p "test_*.py"` verifying all 22 test modules and 316 unit tests in a single continuous process. Output captured in [`docs/05-evidence/T011_R6_RAW_UNITTEST_LOG.txt`](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/docs/05-evidence/T011_R6_RAW_UNITTEST_LOG.txt).
  2. **Instrumented Per-Module Benchmark:** An automated runner (`scratch/run_instrumented_per_module_unittests.py`) executed each of the 22 test files individually with high-resolution `time.perf_counter()`, capturing genuine per-module execution logs in [`docs/05-evidence/T011_R6_PER_MODULE_UNITTEST_LOG.txt`](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/docs/05-evidence/T011_R6_PER_MODULE_UNITTEST_LOG.txt).
- No uninstrumented performance estimations are permitted in R6 reports.

---

## 4. Attestation of Data & Code Immutability

1. `data/raw/`: 0 bytes altered across all 9 CSV files (15,196,366,173 bytes preserved).
2. T-010 Staging Parquet: 100% read-only and preserved.
3. Production Latest Pointer: Untouched.
4. Historical Packages (`T011`, `R1`, `R2`, `R3`, `R4`, `R5`): Completely preserved outside repository.
