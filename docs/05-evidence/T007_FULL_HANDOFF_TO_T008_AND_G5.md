# T007_FULL_HANDOFF_TO_T008_AND_G5 — Handoff Specification for T-008 (G4) & T-010 (G5)

**Document ID:** `T007-FULL-HANDOFF-20261017`  
**Task:** `T-007` — Raw CSV Ingestion Pipeline  
**Parent Gate:** `G4` (`PLANNED / NOT_COMPLETED`)  
**Date:** `2026-10-17`

---

## 1. Handoff to Project Lead (Human Signoff for `T-007`)

To complete human signoff for `T-007`:
1. Review `docs/05-evidence/T007_FULL_FINAL_INDEPENDENT_REVIEW.md` and `docs/05-evidence/T007_LOCAL_RAW_SHA256_CANDIDATE.json`.
2. Upon Project Lead approval:
   - `T-007` transitions from `T007_READY_FOR_HUMAN_SIGNOFF` to `PASS` (Human Signed-Off).
   - The 9 candidate SHA-256 hashes in `docs/05-evidence/T007_LOCAL_RAW_SHA256_CANDIDATE.json` can be passed as `approved_baseline_hashes` into `SourceValidator` so production runs achieve `LOCAL_HASH_VERIFIED` while preserving `upstream_identity_status = "IDENTITY_UNVERIFIED"` (`OR-08`).

---

## 2. Handoff to `T-008` (KPI Aggregation & Analytical Views at Gate `G4`)

Downstream `T-008` modules should consume curated Parquet data exclusively via the atomic pointer protocol established in `T-009` and `T-007`:
1. **Resolving Active Published Run:**
   - Use `SafePublisher(base_data_dir).get_current_pointer()` to read `data/curated/CURRENT_PUBLISHED_RUN.json` and resolve `data/curated/runs/<run_id>/`.
2. **Reading Curated Parquet on Windows:**
   - Use `read_parquet_safe(spark, published_run_dir)` from `flight_pipeline.ingestion.coordinator` (which conforms to `get_curated_schema()` across all 34 columns).
3. **Applying Canonical Quality Predicates (`DC-12`):**
   - Because `T-007` accepts valid-key rows with `NULL` metrics (`DC-12`), `T-008` KPI aggregations must filter metric-specific denominators using `flight_pipeline.quality.predicates` (`is_valid_dep_delay`, `is_valid_arr_delay`, `is_valid_air_time`, `is_valid_distance`, `is_valid_taxi_times`) and never emit a generic `coverage_rate`.
4. **Honoring `OR-05`, `FP-DEC-017`, and `G2-EXC-001`:**
   - Year `2024` annual/YoY aggregations must carry the `OR-05` partial-year annotation (`335/366` days; March missing).
   - Weather branch remains `CONDITIONAL_NO_GO` (`FP-DEC-017`).
   - 7 CORE delay/time measures remain labeled with provisional minute units (`G2-EXC-001`) until `T-010` (`G5`) completes `TS-018`.

---

## 3. Handoff to `T-010` (2016 Single-Year Smoke Execution at Gate `G5`)

Once Gate `G4` (`T-009`, `T-007`, `T-008`) receives Human Gate Signoff:
- `T-010` will invoke `IngestionCoordinator.run_ingestion(run_id=..., years=[2016], require_verified_hashes=True)` against `data/raw/tabular/2016/flight_with_weather_2016.csv` (`5,548,445` rows, `1,538,427,452` bytes, SHA-256 `4ed92ed732721a38ae28325135fad63436347613674ad96c1b273eb9d44cef34`) and execute `TS-018` empirical unit verification to close `G2-EXC-001`.
