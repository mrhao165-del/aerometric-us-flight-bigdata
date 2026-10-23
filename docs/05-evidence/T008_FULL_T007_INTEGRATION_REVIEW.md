# T008 FULL T007 INTEGRATION & ARCHITECTURAL REVIEW

**Document ID:** `T008_FULL_T007_INTEGRATION_REVIEW`  
**Parent Task:** `T-008 — Data Quality, Disjoint Row Accounting & Quarantine Engine`  
**Parent Gate:** `G4`  
**Classification:** `ARCHITECTURE_AND_INTEGRATION_AUDIT`  
**Date:** 2026-10-18  

---

## 1. INTEGRATION ARCHITECTURE

The T-008 Data Quality Engine was designed to wrap and extend the validated outputs of T-007 without introducing redundant parsing layers or mutating existing components.

```
+-----------------------------------------------------------------------------------+
|                              TASK T-007 (INGESTION)                                |
|                                                                                   |
|  [Raw CSV File]                                                                   |
|         |                                                                         |
|         v                                                                         |
|  validate_physical_csv_header()  -->  34-column physical header validation        |
|         |                                                                         |
|         v                                                                         |
|  RawCsvReader.read_raw()         -->  35-field parser schema (34 cols + _corrupt) |
|         |                                                                         |
|         v                                                                         |
|  attach_deterministic_lineage()  -->  _source_year, _source_file, _lineage_id     |
|         |                                                                         |
|         v                                                                         |
|  IngestionRecordClassifier       -->  _record_status, _anomaly_reason, _flags    |
+-----------------------------------------------------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
|                           TASK T-008 (QUALITY ENGINE)                             |
|                                                                                   |
|  QualityEngine.evaluate()                                                         |
|         |                                                                         |
|         +---> QualityAccountingEngine.compute_and_verify_row_accounting() (DC-11) |
|         |                                                                         |
|         +---> QualityAccountingEngine.compute_all_core_metrics() (DC-12)           |
|         |                                                                         |
|         +---> ProvisionalPolicyProfiler.profile_flight_number_anomalies()         |
|         |                                                                         |
|         +---> DateCoverageAnalyzer.analyze() (OR-05 / Calendar coverage)           |
|         |                                                                         |
|         +---> QualityEngine.attach_metric_validity_flags()                        |
|                     (is_valid_arr_delay, is_valid_dep_delay, etc.)                |
+-----------------------------------------------------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
|                        DOWNSTREAM TRANSFORMATION & CURATION                       |
|                                                                                   |
|  IngestionTransformer.to_curated()                                                |
|         |                                                                         |
|         +---> Filter ACCEPTED records only                                        |
|         +---> try_cast to curated Parquet schema types (DC-12 null on non-numeric)|
|         +---> Normalize FL_DATE to YYYY-MM-DD                                     |
|         +---> Derive MONTH / DAY_OF_MONTH when raw calendar fields null           |
+-----------------------------------------------------------------------------------+
```

---

## 2. VERIFIED INTEGRATION PROPERTIES

1. **No Redundant Parsers:** T-008 accepts the Spark DataFrame emitted by `RawCsvReader` and does not re-open the raw CSV.
2. **Schema Integrity:** The output of `IngestionTransformer.to_curated()` strictly matches `get_curated_parquet_schema()` in column count (34 columns), names, and types.
3. **Forensic Traceability:** Quarantined and rejected records preserve `_source_year`, `_source_file`, `_record_lineage_id`, `_record_status`, `_anomaly_reason`, and `_anomaly_flags` for complete auditability.
4. **End-to-End Pipeline Test:** Verified by `test_integ_01_end_to_end_quality_pipeline` and `test_integ_02_forensic_output_preserves_anomaly_reasons`.
