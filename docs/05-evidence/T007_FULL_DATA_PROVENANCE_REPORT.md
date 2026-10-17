# T007_FULL_DATA_PROVENANCE_REPORT — Data Provenance, Manifest & Sidecar Receipt Audit

**Document ID:** `T007-FULL-PROVENANCE-20261017`  
**Task:** `T-007` (`T007-02B`, `T007-05`)  
**Parent Gate:** `G4` (`PLANNED / NOT_COMPLETED`)  
**Date:** `2026-10-17`

---

## 1. Provenance Chain Architecture (`G3-COND-A` & `OR-08`)

Every ingestion run executed by `IngestionCoordinator` produces a cryptographically linked, tamper-evident metadata bundle in `data/metadata/<run_id>/`:

1. **`source_verification.json`:**
   - Captures the full `BatchVerificationResult` from `SourceValidator`, including per-year path, expected vs. actual byte size, computed streaming SHA-256, `hash_status` (`LOCAL_HASH_VERIFIED` or `LOCAL_HASH_COMPUTED_UNAPPROVED`), and `upstream_identity_status = "IDENTITY_UNVERIFIED"`.
2. **`anomaly_summary.json`:**
   - Captures the exact `DC-11` row accounting breakdown (`source_rows_total`, `accepted_rows`, `quarantined_rows`, `rejected_rows`) plus the grouped counts of every `(status, reason)` pair (`MISSING_FL_DATE`, `UNPARSEABLE_FL_DATE`, `MALFORMED_CSV_ROW`, etc.).
3. **`run_manifest.json` (`RunManifest` from `T-009`):**
   - Records `run_id`, `task_id`, `timestamp_utc`, `git_commit`, `row_accounting`, `inputs` (each input CSV's path, byte size, and SHA-256 hash), `outputs` (each published Parquet file's path, byte size, and SHA-256 hash), and `configuration`.
4. **`execution_receipt.json` (`ExecutionReceipt` sidecar from `T007-05`):**
   - Written atomically **after** `run_manifest.json` is closed on disk.
   - Records `manifest_path`, `manifest_bytes`, and `manifest_sha256` (avoiding the self-referential hash paradox of embedding a file's SHA-256 inside itself).
   - Records `pipeline_state`, `state_history`, `publication_status`, `published_path`, `previous_published_run_id`, `upstream_identity_status`, `weather_status`, `core_units_status`, `or05_coverage_warning`, and `governance_warnings`.

---

## 2. Explicit Separation of Local Snapshot Hash vs Upstream Identity (`OR-08`)

Per `AGENTS.md`, `DECISIONS.md` (`OR-08`), and `G3-COND-A`:
- Local SHA-256 hashes computed in `docs/05-evidence/T007_LOCAL_RAW_SHA256_CANDIDATE.json` prove **local byte-stream snapshot consistency** across runs on this repository's raw files (`15,196,366,173` bytes across `2016..2024`).
- They do **not** prove upstream BTS/NOAA cryptographic authenticity.
- Therefore, both `T007_LOCAL_RAW_SHA256_CANDIDATE.json` and every `ExecutionReceipt` explicitly set:
  - `upstream_identity_status = "IDENTITY_UNVERIFIED"`
  - `candidate_status = "LOCAL_HASH_COMPUTED_UNAPPROVED"` (until Project Lead promotes the candidate baseline to approved status).
