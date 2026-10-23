# T008 FULL SYNTHETIC TEST MATRIX & REQUIREMENT TRACEABILITY

**Document ID:** `T008_FULL_SYNTHETIC_TEST_MATRIX`  
**Parent Task:** `T-008 — Data Quality, Disjoint Row Accounting & Quarantine Engine`  
**Parent Gate:** `G4`  
**Classification:** `TEST_TRACEABILITY_AND_VERIFICATION_MATRIX`  
**Date:** 2026-10-18  

---

## 1. TEST SUITE OVERVIEW

- **Test Suite Module:** [`tests/test_t008_quality_engine.py`](../../tests/test_t008_quality_engine.py)
- **Total Tests:** 29 unit and integration tests
- **Execution Time:** ~29.7 seconds
- **Pass Rate:** 100% (29 passed, 0 failed, 0 skipped)
- **Environment:** Local Windows, PySpark 3.5.x, Java 17, Python 3.10

---

## 2. REQUIREMENT TO TEST MAPPING

### Group 1: QUALITY (Record & Metric Integrity)
| Test ID | Method Name | Requirement / Invariant Tested | Status |
|:---|:---|:---|:---:|
| `QUAL-01` | `test_qual_01_valid_record_identity_accepted` | Valid core identity anchors -> `ACCEPTED` | **PASS** |
| `QUAL-02` | `test_qual_02_missing_core_carrier_quarantined` | Missing `OP_CARRIER` -> `QUARANTINED` | **PASS** |
| `QUAL-03` | `test_qual_03_missing_core_airport_quarantined` | Missing `ORIGIN`/`DEST` -> `QUARANTINED` | **PASS** |
| `QUAL-04` | `test_qual_04_invalid_flight_number_quarantined` | Non-numeric/null flight number -> `QUARANTINED` | **PASS** |
| `QUAL-05` | `test_qual_05_provisional_flight_num_non_positive_accepted_and_flagged` | G3-COND-A: `FL_NUM <= 0` accepted + provisional flag | **PASS** |
| `QUAL-06` | `test_qual_06_calendar_date_validation_leap_year` | Real calendar dates: Feb 29 valid, Feb 30 quarantined | **PASS** |
| `QUAL-07` | `test_qual_07_source_year_mismatch_quarantined` | FL_DATE year != `_source_year` -> `QUARANTINED` | **PASS** |
| `QUAL-08` | `test_qual_08_metric_invalidity_preserves_accepted_record` | DC-12 non-numeric delay preserves accepted record | **PASS** |
| `QUAL-09` | `test_qual_09_signed_negative_delay_preserved` | Signed negative delays preserved as valid metrics | **PASS** |
| `QUAL-10` | `test_qual_10_duration_metrics_domain_boundaries` | Duration domains: taxi >= 0, air_time > 0, elapsed > 0 | **PASS** |
| `QUAL-11` | `test_qual_11_weather_absence_allowed` | FP-DEC-017: Null weather does not quarantine flight | **PASS** |
| `QUAL-12` | `test_qual_12_duplicate_records_preserved` | Exact duplicate records (YX 3624) preserved with unique lineage | **PASS** |

### Group 2: ACCOUNTING (DC-11 & DC-12)
| Test ID | Method Name | Requirement / Invariant Tested | Status |
|:---|:---|:---|:---:|
| `ACCT-01` | `test_acct_01_three_state_disjoint_balance_success` | DC-11: $N_{raw} = N_{acc} + N_{quar} + N_{rej}$ balanced | **PASS** |
| `ACCT-02` | `test_acct_02_independent_raw_count_discrepancy_fails_closed` | Discrepancy with independent count raises error | **PASS** |
| `ACCT-03` | `test_acct_03_negative_accounting_counts_rejected` | Negative accounting counts raise ValueError | **PASS** |
| `ACCT-04` | `test_acct_04_metric_valid_bound_enforced` | DC-12: valid metric count cannot exceed total records | **PASS** |
| `ACCT-05` | `test_acct_05_zero_denominator_handled_cleanly` | Zero denominator returns None without div/0 error | **PASS** |
| `ACCT-06` | `test_acct_06_multi_source_reconciliation` | Multi-source per-year and aggregate reconciliation | **PASS** |

### Group 3: COVERAGE (DateCoverageAnalyzer & OR-05)
| Test ID | Method Name | Requirement / Invariant Tested | Status |
|:---|:---|:---|:---:|
| `COV-01` | `test_cov_01_complete_normal_year` | 365 days normal year (2017) -> `COMPLETE` | **PASS** |
| `COV-02` | `test_cov_02_complete_leap_year` | 366 days leap year (2016) -> `COMPLETE` | **PASS** |
| `COV-03` | `test_cov_03_or05_missing_march_2024_defect_detected` | OR-05: 335 observed days, 31 missing March days -> `PARTIAL` | **PASS** |
| `COV-04` | `test_cov_04_missing_feb_29_and_out_of_year_dates` | Detects missing Feb 29 in leap year and out-of-year dates | **PASS** |

### Group 4: POLICY (G3-COND-A & Safety)
| Test ID | Method Name | Requirement / Invariant Tested | Status |
|:---|:---|:---|:---:|
| `POL-01` | `test_pol_01_default_policy_conforms_to_g3_cond_a` | Default config adheres to provisional G3-COND-A | **PASS** |
| `POL-02` | `test_pol_02_enabling_hard_quarantine_without_override_raises_error` | Enabling hard quarantine without override raises error | **PASS** |
| `POL-03` | `test_pol_03_disallowing_weather_nulls_raises_error` | Disallowing weather nulls without override raises error | **PASS** |
| `POL-04` | `test_pol_04_provisional_policy_profiling_simulation` | Profiler measures frequencies and simulates policies | **PASS** |

### Group 5: INTEGRATION (End-to-End Pipeline & Forensics)
| Test ID | Method Name | Requirement / Invariant Tested | Status |
|:---|:---|:---|:---:|
| `INT-01` | `test_integ_01_end_to_end_quality_pipeline` | RawCsvReader -> QualityEngine -> IngestionTransformer | **PASS** |
| `INT-02` | `test_integ_02_forensic_output_preserves_anomaly_reasons` | Quarantined records preserve anomaly reasons and flags | **PASS** |
| `INT-03` | `test_integ_03_quality_rule_catalog_traceability` | Rule catalog completeness and attribute integrity | **PASS** |
