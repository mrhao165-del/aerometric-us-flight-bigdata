# T010_FULL_BASELINE_AND_PREFLIGHT.md — Preflight Verification and Source Validation (2016 Real Data)

**Gate:** G5  
**Task:** T-010 — Bounded Real-Data Smoke & Resource Benchmark  
**Author:** Independent Big Data QA Auditor & Windows Storage Reliability Engineer  
**Execution Timestamp:** 2026-10-18T11:07:20+00:00 (2026-10-18T18:07:20+07:00)  
**Status:** PASS (CONTROLLED)  

---

## 1. Executive Summary & Authorization

Project Lead directly authorized the execution of Task T-010 under Gate G5 to perform bounded real-data smoke testing and resource benchmarking on the 2016 flight performance dataset.

This document records the preflight source verification conducted on `data/raw/tabular/2016/flight_with_weather_2016.csv` using the production [SourceValidator](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/src/flight_pipeline/ingestion/source_validator.py) and physical CSV header verifier [validate_physical_csv_header](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/src/flight_pipeline/ingestion/reader.py#L143-L190).

---

## 2. Audited Source Baseline vs Physical Inspection

As ratified in [G5_T010_ENTRY_BASELINE_ERRATA.md](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/docs/05-evidence/G5_T010_ENTRY_BASELINE_ERRATA.md), the physical 2016 dataset was independently cross-verified across physical filesystem stats, the G1 audit schema `schema_2016.json`, candidate hash baseline `T007_LOCAL_RAW_SHA256_CANDIDATE.json`, and `AUDITED_SOURCE_INVENTORY[2016]`.

| Attribute | Audited Baseline | Measured Disk Inspection | Verification Status |
| :--- | :--- | :--- | :--- |
| **Survey Year** | `2016` | `2016` | **MATCH** |
| **Relative Path** | `data/raw/tabular/2016/flight_with_weather_2016.csv` | `data/raw/tabular/2016/flight_with_weather_2016.csv` | **MATCH** |
| **File Byte Size** | `1,538,427,452` bytes | `1,538,427,452` bytes | **MATCH (Exact)** |
| **Data Rows Count** | `5,537,987` non-header rows | `5,537,987` non-header rows | **MATCH (Exact)** |
| **Canonical Columns** | `34` columns | `34` columns | **MATCH (Exact)** |
| **File Modification Time** | `1787484809.8685696` | `1787484809.8685696` | **MATCH** |
| **Candidate SHA-256** | `4ed92ed732721a38ae28325135fad63436347613674ad96c1b273eb9d44cef34` | `4ed92ed732721a38ae28325135fad63436347613674ad96c1b273eb9d44cef34` | **MATCH (Streaming)** |
| **Read Permission** | Read-Only Allowed | Granted (`os.access(..., os.R_OK)`) | **PASS** |

---

## 3. Production SourceValidator Execution

Execution of `SourceValidator.verify_source(2016, compute_hash=True)` yielded:

- **Verification State:** `LOCAL_HASH_COMPUTED_UNAPPROVED`
- **Upstream Identity Status:** `IDENTITY_UNVERIFIED` (per OR-08 and TS-019)
- **Approved Golden Hash:** `None` (Preserved as `CANDIDATE_PENDING_HUMAN_ACCEPTANCE`)
- **Is Verified (Golden):** `False`

> [!NOTE]
> Conforming strictly to `AGENTS.md` and repository governance policies, the agent did NOT self-approve or promote the candidate hash into the golden baseline. The upstream identity status remains strictly `IDENTITY_UNVERIFIED` pending BTS/NOAA provenance review.

---

## 4. Physical CSV Header Contract Verification

Execution of `validate_physical_csv_header()` verified the physical CSV header against the canonical 34-column schema:

- **Encoding:** Strict UTF-8 without Byte Order Mark (`BOM: False`).
- **Physical Column Count:** Exactly 34 columns.
- **Physical Column Order:** Exactly matches `CANONICAL_COLUMN_NAMES` (0..33):
  1. `FL_DATE`, 2. `OP_CARRIER`, 3. `OP_CARRIER_FL_NUM`, 4. `ORIGIN`, 5. `DEST`, 6. `CRS_DEP_TIME`, 7. `DEP_TIME`, 8. `DEP_DELAY`, 9. `TAXI_OUT`, 10. `WHEELS_OFF`, 11. `WHEELS_ON`, 12. `TAXI_IN`, 13. `CRS_ARR_TIME`, 14. `ARR_TIME`, 15. `ARR_DELAY`, 16. `CRS_ELAPSED_TIME`, 17. `ACTUAL_ELAPSED_TIME`, 18. `AIR_TIME`, 19. `FLIGHTS`, 20. `MONTH`, 21. `DAY_OF_MONTH`, 22. `DAY_OF_WEEK`, 23. `DISTANCE`, 24. `DEST_AIRPORT_ID`, 25. `O_TEMP`, 26. `O_PRCP`, 27. `O_WSPD`, 28. `D_TEMP`, 29. `D_PRCP`, 30. `D_WSPD`, 31. `ORIGIN_LATITUDE`, 32. `ORIGIN_LONGITUDE`, 33. `DEST_LATITUDE`, 34. `DEST_LONGITUDE`.
- **Parser Schema Separation:** The 35th field `_corrupt_record` is strictly maintained as an internal Spark parser column and was correctly absent from the physical CSV.

---

## 5. Preflight Conclusion

Preflight verification succeeded across all criteria with zero deviations. The 2016 raw source CSV is confirmed physically present, read-accessible, and structurally compliant to proceed with Phase 2 safety verification and Phase 3 micro-smoke execution.
