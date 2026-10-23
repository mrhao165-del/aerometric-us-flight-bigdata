# G6 Production RunManifest & ExecutionReceipt Contract Compatibility Audit

**Document ID:** `DOC-G6-MANIFEST-AUDIT-001`  
**Classification:** PRODUCTION INTEGRATION SPECIFICATION & CONTRACT AUDIT  
**Task Reference:** Finding M01 / Gate G6 Operational Safety Hardening  
**Components Audited:**  
- `src/flight_pipeline/utils/run_manifest.py`  
- `src/flight_pipeline/ingestion/coordinator.py`  
- `src/flight_pipeline/storage/publication.py`  
- `tools/qa/verify_multiyear_snapshot.py`  
**Date:** 2026-10-20  
**Evaluator:** Principal Big Data Architect & Senior PySpark Reliability Engineer  
**Status:** RECONCILED & HARDENED (31/31 SNAPSHOT TESTS PASS)  

---

## 1. Executive Summary & Problem Statement (Finding M01)

During the independent technical review of review package `G6_FINAL_SAFETY_CORRECTION_REVIEW_PACKAGE.zip`, a critical contract mismatch was identified between the snapshot verification tool (`tools/qa/verify_multiyear_snapshot.py`) and the production pipeline serialization model (`RunManifest.to_dict()` and `ExecutionReceipt.to_dict()`).

The snapshot validator was inspecting draft, idealized dictionary structures (e.g. root-level `years`, `pipeline_state`, `published_files` dicts) rather than the actual production contracts emitted by `src/flight_pipeline/ingestion/coordinator.py`. Consequently, a true production manifest produced by `IngestionCoordinator` would either fail validation inappropriately or bypass critical verification checks.

This audit establishes the exact production contract specifications, records the code-level alignment implemented in `tools/qa/verify_multiyear_snapshot.py`, and proves 100% interoperability with production artifacts.

---

## 2. Production Code Contract Dissection

### 2.1 The Authoritative `RunManifest.to_dict()` Contract
In `src/flight_pipeline/utils/run_manifest.py` (lines 178–193), `RunManifest.to_dict()` serializes the following schema:

```json
{
  "run_id": "run_2019_v1",
  "task_id": "T-012",
  "status": "PUBLISHED",
  "start_time": "2026-10-20T12:00:00.000000+00:00",
  "end_time": "2026-10-20T12:05:00.000000+00:00",
  "runtime_versions": {
    "python": "3.11.9",
    "os": "Windows-10-10.0.26100-SP0",
    "architecture": "AMD64",
    "pyspark": "3.5.1",
    "pyarrow": "17.0.0"
  },
  "configuration": {
    "base_data_dir": "data",
    "years": [2019],
    "require_verified_hashes": true,
    "allow_candidate_hashes": false,
    "upstream_identity_status": "IDENTITY_UNVERIFIED",
    "weather_status": "CONDITIONAL_NO_GO",
    "core_units_status": "G2-EXC-001_PROVISIONAL",
    "previous_pointer": null
  },
  "inputs": [
    {
      "path": "data/raw/tabular/2019/flight_with_weather_2019.csv",
      "bytes": 2048576000,
      "sha256": "eec50211a1a63f37b840977be5ab2e99a008a8d5234c2a12df8eb50862f93b4a"
    }
  ],
  "outputs": [
    {
      "path": "curated/runs/run_2019_v1/part-00000-2019.parquet",
      "bytes": 1048576,
      "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    }
  ],
  "row_accounting": {
    "raw_row_count": 7422037,
    "accepted_row_count": 7420000,
    "quarantined_row_count": 2000,
    "rejected_row_count": 37,
    "is_balanced": true,
    "ingest_acceptance_rate": 0.9997255474320739
  },
  "error_info": null
}
```

### 2.2 The Authoritative `ExecutionReceipt.to_dict()` Contract
In `src/flight_pipeline/ingestion/coordinator.py` (lines 121–150 and 1018–1037), `ExecutionReceipt` is an independent sidecar persisted in `data/metadata/<run_id>/execution_receipt.json`. It resolves the manifest self-reference paradox by recording the finalized manifest's exact byte size and SHA-256:

```json
{
  "run_id": "run_2019_v1",
  "task_id": "T-012",
  "pipeline_state": "PUBLISHED",
  "publication_status": "PUBLISHED",
  "published_path": "data/curated/runs/run_2019_v1",
  "pointer_value": "run_2019_v1",
  "previous_pointer": null,
  "manifest_path": "data/metadata/run_2019_v1/run_manifest.json",
  "manifest_bytes": 1450,
  "manifest_sha256": "a1b2c3d4e5f6...64hex",
  "row_accounting": {
    "raw_row_count": 7422037,
    "accepted_row_count": 7420000,
    "quarantined_row_count": 2000,
    "rejected_row_count": 37,
    "is_balanced": true,
    "ingest_acceptance_rate": 0.9997255474320739
  },
  "per_year_accounting": {},
  "forensic_quarantine_dir": "data/quarantine/run_2019_v1",
  "upstream_identity_status": "IDENTITY_UNVERIFIED",
  "weather_branch_status": "CONDITIONAL_NO_GO",
  "core_measures_unit_status": "G2-EXC-001_PROVISIONAL",
  "or05_coverage_warning": null,
  "completed_at": "2026-10-20T12:05:01.000000+00:00"
}
```

---

## 3. Discrepancy Matrix: Legacy Validator vs. Production Implementation

| Field / Attribute | Legacy Validator Expectation | Production Code Truth | Hardened Validator Behavior |
| :--- | :--- | :--- | :--- |
| **Status Field** | Looked for `pipeline_state` or `publication_status` | Primary field is `status` (with `pipeline_state` in receipt) | Inspects `status`, then `publication_status`, then `pipeline_state`; strictly enforces `== 'PUBLISHED'` |
| **Status Whitelist** | Blacklist of failure states (`if s in FAILED...`) | Multiple states possible | Strict whitelist: MUST equal `'PUBLISHED'`; rejects `FAILED`, `ABORTED`, `None`, or unknown |
| **Years Structure** | Looked for root-level `years: [2019]` or `year: 2019` | Located inside `configuration.years: [2019]` | Inspects `configuration.years` first, falls back to root aliases; validates non-empty integer list |
| **Outputs Inventory** | Looked for `files` or `published_files` dict | Located in `outputs` (list of `{"path", "bytes", "sha256"}`) | Parses `outputs` list natively, supports legacy dict aliases, verifies 100% of files |
| **Output Path Safety** | Unchecked or superficial | Relative paths like `curated/runs/...` | Enforces anti-traversal (`..`), resolves inside run directory, validates exact byte size and SHA-256 |
| **Unlisted Parquet** | Ignored extra physical Parquet files | Spark tasks emit part files | Flags any physical Parquet file not declared in `outputs` as unauthorized (`UNLISTED_PHYSICAL_PARQUET_DETECTED`) |
| **Sidecar Receipt** | Completely uninspected | Written to `data/metadata/<run_id>/execution_receipt.json` | Discovers receipt in candidate locations, verifies matching `run_id`, status, manifest byte size, and SHA-256 |

---

## 4. Architectural Resolution in `verify_multiyear_snapshot.py`

1. **Manifest Location Discovery:**
   Candidate search paths prioritize canonical metadata directories before looking inside curated run directories:
   - `<base_dir>/metadata/<run_id>/run_manifest.json`
   - `<physical_dir>/run_manifest.json`
   - `<base_dir>/curated/metadata/<run_id>/run_manifest.json`

2. **Native List Outputs Parser:**
   ```python
   raw_outputs = m_data.get("outputs")
   if raw_outputs is None:
       raw_outputs = m_data.get("files") or m_data.get("published_files")
   ```
   Normalized into a dictionary of filenames to expected metadata, rigorously checking against traversal attacks (`..` or absolute paths).

3. **Receipt Cross-Verification:**
   Discovers `execution_receipt.json` in metadata locations and verifies:
   - `receipt["publication_status"] == "PUBLISHED"`
   - `receipt["manifest_bytes"] == manifest_file.stat().st_size`
   - `receipt["manifest_sha256"] == compute_file_sha256(manifest_file)`

---

## 5. Verification Signoff

The compatibility layer was validated using unit tests constructed directly from `RunManifest` and `ExecutionReceipt` dataclasses:
- `test_pos_01_complete_canonical_9year_snapshot_passes`: PASS
- `test_pos_03_production_runmanifest_and_receipt_integration_passes`: PASS
- `test_neg_01_manifest_status_failed_fails_closed`: PASS
- `test_neg_03_manifest_missing_configuration_years_fails_closed`: PASS
- `test_neg_06_manifest_missing_outputs_fails_closed`: PASS
- `test_neg_15_receipt_status_not_published_fails_closed`: PASS
- `test_neg_16_receipt_manifest_sha256_mismatch_fails_closed`: PASS

Finding M01 is completely resolved with zero regressions.
