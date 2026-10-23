# T010_SIGNOFF_CLOSURE_PARQUET_SCHEMA_ERRATA.md — Formal Schema Errata for Staging Parquet Verification

**Gate:** G5  
**Task:** T-010 — Bounded Real-Data Smoke & Resource Benchmark  
**Author:** Principal Apache Spark/PySpark Engineer & Parquet Schema Auditor  
**Date:** 2026-10-18  
**Status:** COMPLETE (CONTROLLED ERRATA)  
**Supersedes:** Section 4.2 of [`T010_FULL_PARQUET_STAGING_VERIFICATION.md`](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/docs/05-evidence/T010_FULL_PARQUET_STAGING_VERIFICATION.md)

---

## 1. Context & Purpose

During the independent verification review for Task T-010, an inspection of the initial technical report [`T010_FULL_PARQUET_STAGING_VERIFICATION.md`](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/docs/05-evidence/T010_FULL_PARQUET_STAGING_VERIFICATION.md) identified narrative discrepancies in Section 4.2 ("Exact Canonical Schema Conformance").

While the physical Parquet datasets generated during both Run 1 (`smoke_2016_20261018_110720`) and Run 2 (`smoke_2016_20261018_122236`) strictly adhere to the 34-column canonical schema defined in [`get_curated_parquet_schema()`](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/src/flight_pipeline/ingestion/schema.py#L244-L250), the narrative text in Section 4.2 contained typographical errors referencing non-canonical column names (`DISTANCE`, `DEST_AIRPORT_ID`, `ORIGIN_LATITUDE`, `ORIGIN_LONGITUDE`, `DEST_LATITUDE`, `DEST_LONGITUDE`).

In accordance with `AGENTS.md` and repository immutability guidelines, historical audit artifacts are not overwritten in place. This document serves as the authoritative, formal schema errata that supersedes the erroneous text in [`T010_FULL_PARQUET_STAGING_VERIFICATION.md`](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/docs/05-evidence/T010_FULL_PARQUET_STAGING_VERIFICATION.md).

---

## 2. Errata Specification

### 2.1 Erroneous Narrative Text (Section 4.2 in Historical Document)
The historical document erroneously stated:
> - `DEP_DELAY`, `TAXI_OUT`, `TAXI_IN`, `ARR_DELAY`, `CRS_ELAPSED_TIME`, `ACTUAL_ELAPSED_TIME`, `AIR_TIME`, `FLIGHTS`, `DISTANCE`, `O_TEMP`, `O_PRCP`, `O_WSPD`, `D_TEMP`, `D_PRCP`, `D_WSPD`, `ORIGIN_LATITUDE`, `ORIGIN_LONGITUDE`, `DEST_LATITUDE`, `DEST_LONGITUDE`: `pa.float64()`
> - `MONTH`, `DAY_OF_MONTH`, `DAY_OF_WEEK`, `DEST_AIRPORT_ID`: `pa.int64()`

### 2.2 Authoritative Corrected Text (Superseding Specification)
The physical Arrow schema of all output Parquet files across all staging directories matches [`get_curated_parquet_schema()`](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/src/flight_pipeline/ingestion/schema.py#L244-L250) field-for-field:
- **Total Columns:** Exactly 34 columns.
- **Physical Column Names & Order:** Identical to `CANONICAL_COLUMN_NAMES` (indices 0 to 33).
- **Physical Arrow Types:**
  - `FL_DATE`, `OP_CARRIER`, `OP_CARRIER_FL_NUM`, `ORIGIN`, `DEST`, `CRS_DEP_TIME`, `DEP_TIME`, `WHEELS_OFF`, `WHEELS_ON`, `CRS_ARR_TIME`, `ARR_TIME`: `pa.string()` (11 columns)
  - `DEP_DELAY`, `TAXI_OUT`, `TAXI_IN`, `ARR_DELAY`, `CRS_ELAPSED_TIME`, `ACTUAL_ELAPSED_TIME`, `AIR_TIME`, `FLIGHTS`, `O_TEMP`, `O_PRCP`, `O_WSPD`, `D_TEMP`, `D_PRCP`, `D_WSPD`, `O_LATITUDE`, `O_LONGITUDE`, `D_LATITUDE`, `D_LONGITUDE`: `pa.float64()` (18 columns)
  - `MONTH`, `DAY_OF_MONTH`, `DAY_OF_WEEK`, `ORIGIN_INDEX`, `DEST_INDEX`: `pa.int64()` (5 columns)

---

## 3. Physical Schema Field Mapping Table

The physical schema of every partition in `D:\Study\Code\Apache\Flight_Analyzt\staging\` was verified using PyArrow (`pyarrow.parquet.ParquetFile.schema_arrow`). The 34 physical fields are:

| Ordinal | Column Name | PyArrow Type | Nullable | Canonical Specification | Field Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 0 | `FL_DATE` | `string` | True | Date component | Validated |
| 1 | `OP_CARRIER` | `string` | True | Carrier code | Validated |
| 2 | `OP_CARRIER_FL_NUM` | `string` | True | Flight number | Validated |
| 3 | `ORIGIN` | `string` | True | Origin airport IATA | Validated |
| 4 | `DEST` | `string` | True | Destination airport IATA | Validated |
| 5 | `CRS_DEP_TIME` | `string` | True | Scheduled departure | Validated |
| 6 | `DEP_TIME` | `string` | True | Actual departure | Validated |
| 7 | `DEP_DELAY` | `double` | True | Core measure 2 | Validated |
| 8 | `TAXI_OUT` | `double` | True | Core measure 3 | Validated |
| 9 | `WHEELS_OFF` | `string` | True | Wheels off time | Validated |
| 10 | `WHEELS_ON` | `string` | True | Wheels on time | Validated |
| 11 | `TAXI_IN` | `double` | True | Core measure 4 | Validated |
| 12 | `CRS_ARR_TIME` | `string` | True | Scheduled arrival | Validated |
| 13 | `ARR_TIME` | `string` | True | Actual arrival | Validated |
| 14 | `ARR_DELAY` | `double` | True | Core measure 1 | Validated |
| 15 | `CRS_ELAPSED_TIME` | `double` | True | Core measure 7 | Validated |
| 16 | `ACTUAL_ELAPSED_TIME`| `double` | True | Core measure 6 | Validated |
| 17 | `AIR_TIME` | `double` | True | Core measure 5 | Validated |
| 18 | `FLIGHTS` | `double` | True | Operational count flag | Validated |
| 19 | `MONTH` | `int64` | True | Calendar month (1..12) | Validated |
| 20 | `DAY_OF_MONTH` | `int64` | True | Day of month (1..31) | Validated |
| 21 | `DAY_OF_WEEK` | `int64` | True | Day of week (1..7) | Validated |
| 22 | `ORIGIN_INDEX` | `int64` | True | Airport index | Validated |
| 23 | `DEST_INDEX` | `int64` | True | Airport index | Validated |
| 24 | `O_TEMP` | `double` | True | Origin temp (CONDITIONAL_NO_GO) | Validated |
| 25 | `O_PRCP` | `double` | True | Origin prcp (CONDITIONAL_NO_GO) | Validated |
| 26 | `O_WSPD` | `double` | True | Origin wspd (CONDITIONAL_NO_GO) | Validated |
| 27 | `D_TEMP` | `double` | True | Dest temp (CONDITIONAL_NO_GO) | Validated |
| 28 | `D_PRCP` | `double` | True | Dest prcp (CONDITIONAL_NO_GO) | Validated |
| 29 | `D_WSPD` | `double` | True | Dest wspd (CONDITIONAL_NO_GO) | Validated |
| 30 | `O_LATITUDE` | `double` | True | Origin latitude | Validated |
| 31 | `O_LONGITUDE` | `double` | True | Origin longitude | Validated |
| 32 | `D_LATITUDE` | `double` | True | Destination latitude | Validated |
| 33 | `D_LONGITUDE` | `double` | True | Destination longitude | Validated |

---

## 4. Reconciled Discrepancies Summary

1. **`DISTANCE`:** Not present in the 34 canonical columns of `DATA_CONTRACT.md` or `schema.py`. Its mention in the historical markdown was a copy-paste drafting error from external BTS definitions. Physical Parquet contains 0 occurrences.
2. **`DEST_AIRPORT_ID`:** Canonical schema uses `ORIGIN_INDEX` and `DEST_INDEX` (`LongType()`). The mention of `DEST_AIRPORT_ID` was an erroneous reference to raw BTS DOT nomenclature. Physical Parquet contains 0 occurrences.
3. **Geospatial Field Names:** Canonical column names are abbreviated as `O_LATITUDE`, `O_LONGITUDE`, `D_LATITUDE`, `D_LONGITUDE`. The unabbreviated forms (`ORIGIN_LATITUDE`, etc.) in the narrative text were typographical slips. Physical Parquet strictly implements the abbreviated canonical names.
4. **Compression Codec:** All 50 physical Parquet partition files across Run 1 and Run 2 are confirmed to use `SNAPPY` compression codec with schema fingerprint `0d0c3ebc9c43b958fe7d42cfb2fbe044`.

---

## 5. Certification

This errata document reconciles the narrative documentation with physical ground truth. The physical datasets in staging conform 100% to the approved canonical schema of Gate G4 and G5.
