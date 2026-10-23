# G6_R05_RECURSIVE_REGRESSION_RESULTS.md
## Positive & Negative Regression Test Execution Report for Finding R05

**Project:** US Flight Performance Analysis 2016–2024  
**Date:** 2026-10-21  
**Gate Status:** G5 = IN_PROGRESS (TECHNICALLY READY) | G6 = NOT_STARTED / BLOCKED  
**Test Suite:** `tests/test_multiyear_snapshot_policy.py`  
**Execution Environment:** Windows 11 Enterprise (NTFS), Python 3.10.11 / 3.11.9, PyArrow 17.0.0, PySpark 4.0.1  
**Total Test Count:** 62 tests (49 historical + 13 new R05/E01/E02/E03 regression tests)  
**Overall Verdict:** **100% PASS (62/62 PASS, 0 FAIL, 0 ERROR)**

---

## 1. Finding R05 Test Matrix

The following targeted unit and integration tests were designed and executed to verify recursive discovery, symlink protection, duplicate filename handling, and physical row count conservation:

| Test ID | Test Method Name | Scenario Description | Expected Status / Code | Actual Result |
|---|---|---|---|---|
| **R05-A** | `test_neg_r05a_unlisted_deep_partition_parquet_fails_closed` | Nested partition directory (`run_2019_v1/nested_partition/unlisted.parquet`) contains Parquet not declared in `RunManifest.outputs`. | `valid=False`<br>`UNLISTED_PHYSICAL_PARQUET_DETECTED` | **PASS** (Fails closed, flags unlisted file) |
| **R05-B** | `test_neg_r05b_manifest_declares_deep_parquet_missing_from_disk_fails_closed` | `RunManifest.outputs` declares deep path `curated/runs/run_2019_v1/deep/sub/missing.parquet`, but file is absent from disk. | `valid=False`<br>`MANIFEST_FILE_NOT_FOUND` | **PASS** (Fails closed, catches missing partition) |
| **R05-C** | `test_pos_r05c_multilevel_partition_hierarchy_passes` | Curated run organized into multi-level partition directories (`year=2019/month=1/part-00000.parquet` and `year=2019/month=2/part-00001.parquet`), both declared with valid bytes/SHA-256. | `valid=True`<br>`VALID_SNAPSHOT_REGISTRY` | **PASS** (Recursively validates both partitions) |
| **R05-D** | `test_pos_r05d_mixed_root_and_deep_parquet_passes` | Curated run contains both a root file (`part-root.parquet`) and a nested subpartition file (`subpartition/part-sub.parquet`), both declared in manifest. | `valid=True`<br>`VALID_SNAPSHOT_REGISTRY` | **PASS** (Discovers and validates mixed files) |
| **R05-E** | `test_neg_r05e_deep_partition_row_count_mismatch_fails_closed` | Nested partition Parquet contains 5 rows on disk, but manifest declares accepted row count = 2. | `valid=False`<br>`PARQUET_PHYSICAL_ROW_COUNT_MISMATCH` | **PASS** (Fails closed on row count disparity) |
| **R05-F** | `test_neg_r05f_symlink_or_reparse_point_in_hierarchy_fails_closed` | Symlink, directory junction, or NTFS reparse point injected into nested partition hierarchy. | `files=None`<br>`UNSAFE_SYMLINK_DETECTED` | **PASS** (Fail-closed symlink detection) |

---

## 2. Additional Regression Tests for E01, E02, and E03

| Test ID | Test Method Name | Scenario Description | Expected Status / Code | Actual Result |
|---|---|---|---|---|
| **E02-A** | `test_pos_e02a_valid_single_annual_run_passes` | `validate_single_annual_run` executed on valid single-year run (2016) with authentic receipt. | `valid=True`<br>`VALID_SINGLE_RUN_ANNUAL_BATCH` | **PASS** (2016 single-run verified) |
| **E02-B** | `test_neg_e02b_single_annual_run_row_mismatch_fails_closed` | 2016 single run injects obsolete typo count 5,617,658 vs canonical 5,537,987. | `valid=False`<br>`CANONICAL_RAW_COUNT_MISMATCH` | **PASS** (Enforces canonical 2016 count) |
| **E02-C** | `test_neg_e02c_single_annual_run_missing_receipt_fails_closed` | `execution_receipt.json` deleted from metadata directory during single-run validation. | `valid=False`<br>`MISSING_EXECUTION_RECEIPT` | **PASS** (Fails closed without receipt) |
| **E02-D** | `test_neg_e02d_single_annual_run_unlisted_deep_parquet_fails_closed` | Unlisted Parquet file injected into nested directory of single-year run. | `valid=False`<br>`UNLISTED_PHYSICAL_PARQUET_DETECTED` | **PASS** (Fails closed on unlisted nested file) |
| **E03-A** | `test_coordinator_cli_help` | `python -m flight_pipeline.ingestion.coordinator --help` invocation. | `SystemExit(0)` | **PASS** (CLI help rendered cleanly) |
| **E03-B** | `test_coordinator_cli_dry_run_preflight` | Production CLI with `--years 2016 --dry-run-preflight`. | Return code `0` | **PASS** (Preflight completes without writing) |
| **E03-C** | `test_coordinator_cli_live_run_blocked_by_d5` | Production CLI with `--years 2016` (no `--dry-run-preflight`). | Return code `1`<br>`[GOVERNANCE HOLD]` | **PASS** (Blocks execution under D5 hold) |

---

## 3. Physical Test Execution Evidence

```
Command: python -m unittest tests/test_multiyear_snapshot_policy.py
Working Directory: D:\Study\Code\Apache\Flight_Analyzt\US_FLIGHT_PERFORMANCE_DOCS_V1
Timestamp: 2026-10-21T13:40:23+07:00
Exit Code: 0

Stdout/Stderr Output:
..............................................................
----------------------------------------------------------------------
Ran 62 tests in 7.891s

OK
================================================================================
INGESTION COORDINATOR PREFLIGHT REPORT (T-012)
================================================================================
Run ID:              run_2016_v1
Target Directory:    D:\Study\Code\Apache\Flight_Analyzt\US_FLIGHT_PERFORMANCE_DOCS_V1\data\curated\runs\run_2016_v1
Survey Years:        [2016]
Base Data Dir:       D:\Study\Code\Apache\Flight_Analyzt\US_FLIGHT_PERFORMANCE_DOCS_V1\data
Lock Directory:      D:\Study\Code\Apache\Flight_Analyzt\US_FLIGHT_PERFORMANCE_DOCS_V1\data\locks
Lock Status:         CLEAN
Dry-Run Mode:        True
--------------------------------------------------------------------------------
Source Files Inventory:
  Year 2016: data\raw\tabular\2016\flight_with_weather_2016.csv [OK]
    Audited Rows:  5,537,987
    Audited Bytes: 1,538,427,452 | Actual Bytes: 1,538,427,452
================================================================================
[PREFLIGHT PASS] Dry-run preflight inspection completed successfully. No data written.

================================================================================
INGESTION COORDINATOR PREFLIGHT REPORT (T-012)
================================================================================
Run ID:              run_2016_v1
Target Directory:    D:\Study\Code\Apache\Flight_Analyzt\US_FLIGHT_PERFORMANCE_DOCS_V1\data\curated\runs\run_2016_v1
Survey Years:        [2016]
Base Data Dir:       D:\Study\Code\Apache\Flight_Analyzt\US_FLIGHT_PERFORMANCE_DOCS_V1\data
Lock Directory:      D:\Study\Code\Apache\Flight_Analyzt\US_FLIGHT_PERFORMANCE_DOCS_V1\data\locks
Lock Status:         CLEAN
Dry-Run Mode:        False
--------------------------------------------------------------------------------
Source Files Inventory:
  Year 2016: data\raw\tabular\2016\flight_with_weather_2016.csv [OK]
    Audited Rows:  5,537,987
    Audited Bytes: 1,538,427,452 | Actual Bytes: 1,538,427,452
================================================================================

[GOVERNANCE HOLD] Live ingestion execution is BLOCKED.
Decision D5 (Gate G6 Annual Ingestion Authorization) has NOT been approved by Project Lead.
Per AGENTS.md, autonomous AI agents cannot authorize production data execution.
Preflight check passed; awaiting explicit human authorization (D5).
```

---

## 4. Conclusion

All 62 tests pass unconditionally. Deep recursive Parquet discovery (R05), single-run validation (E02), and CLI execution guards (E03) are fully proven and regression-tested.
