# T007-01 CANONICAL SCHEMA IMPLEMENTATION SPECIFICATION

**Document ID:** `DOC-T007-01-02-SCHEMA-SPEC`  
**Task ID:** `T007-01` (Canonical Schema Module)  
**Parent Gate:** `G4` (`PLANNED / NOT_COMPLETED`)  
**Source Module:** [`src/flight_pipeline/ingestion/schema.py`](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/src/flight_pipeline/ingestion/schema.py)  
**Design Authority:** Senior PySpark Schema Engineer  

---

## 1. ARCHITECTURAL OVERVIEW

The canonical schema implementation in `src/flight_pipeline/ingestion/schema.py` establishes a robust, two-layer boundary that prevents data loss, preserves raw tokens, and guarantees contract compliance:

```
+─────────────────────────────────────────────────────────────────────────────+
| LAYER 1: Raw CSV Ingestion Boundary (Bronze Layer)                          |
| - 34 Canonical business columns defined strictly as `StringType`            |
| - Preserves unparsed text representations without loss or premature cast    |
| - Technical `_corrupt_record: StringType` added as 35th field               |
| - Prevents non-numeric metric strings from triggering record rejection       |
+─────────────────────────────────────────────────────────────────────────────+
                                       │
                                       ▼ (Safe Typed Transformation)
+─────────────────────────────────────────────────────────────────────────────+
| LAYER 2: Curated Parquet Storage Schema (Silver Layer)                      |
| - 34 Canonical columns strongly typed according to DATA_DICTIONARY.md       |
| - OP_CARRIER_FL_NUM: DoubleType (preserving float64 audited representation)  |
| - FLIGHTS: DoubleType (metadata explicitly prohibits KPI denominator weight)|
| - MONTH, DAY_OF_MONTH, DAY_OF_WEEK: LongType (Int64 nullable)               |
| - 7 CORE measures: DoubleType (provisional units under G2-EXC-001)           |
| - Weather: DoubleType (optional, conditional no-go under FP-DEC-017)        |
| - Local Times & Date: StringType (no rollover or timezone per FP-DEC-007)   |
+─────────────────────────────────────────────────────────────────────────────+
```

---

## 2. PHYSICAL SCHEMA MAPPING TABLE (34 CANONICAL COLUMNS)

| Index | Column Name | Raw Parse Type | Curated Storage Type | Nullable | Canonical Category & Governance Metadata |
| :---: | :--- | :--- | :--- | :---: | :--- |
| **0** | `FL_DATE` | `StringType` | `StringType` | `True` | Core Anchor (`anchor="FLIGHT_DATE"`); date string `YYYY-MM-DD`. |
| **1** | `OP_CARRIER` | `StringType` | `StringType` | `True` | Core Anchor (`anchor="CARRIER"`); 2-3 letter IATA code. |
| **2** | `OP_CARRIER_FL_NUM` | `StringType` | `DoubleType` | `True` | Flight number; raw audited dtype `float64`; G3-COND-A boundary. |
| **3** | `ORIGIN` | `StringType` | `StringType` | `True` | Core Anchor (`anchor="ORIGIN_AIRPORT"`); 3-letter IATA code. |
| **4** | `DEST` | `StringType` | `StringType` | `True` | Core Anchor (`anchor="DEST_AIRPORT"`); 3-letter IATA code. |
| **5** | `CRS_DEP_TIME` | `StringType` | `StringType` | `True` | Scheduled departure time (`HHmm`); `temporal_policy="NO_ROLLOVER"`. |
| **6** | `DEP_TIME` | `StringType` | `StringType` | `True` | Actual departure time (`HHmm`); `temporal_policy="NO_ROLLOVER"`. |
| **7** | `DEP_DELAY` | `StringType` | `DoubleType` | `True` | **CORE MEASURE 1**. Signed departure delay (`G2-EXC-001_PROVISIONAL`). |
| **8** | `TAXI_OUT` | `StringType` | `DoubleType` | `True` | **CORE MEASURE 2**. Taxi-out duration (`G2-EXC-001_PROVISIONAL`). |
| **9** | `WHEELS_OFF` | `StringType` | `StringType` | `True` | Wheels-off time (`HHmm`); `temporal_policy="NO_ROLLOVER"`. |
| **10** | `WHEELS_ON` | `StringType` | `StringType` | `True` | Wheels-on time (`HHmm`); `temporal_policy="NO_ROLLOVER"`. |
| **11** | `TAXI_IN` | `StringType` | `DoubleType` | `True` | **CORE MEASURE 3**. Taxi-in duration (`G2-EXC-001_PROVISIONAL`). |
| **12** | `CRS_ARR_TIME` | `StringType` | `StringType` | `True` | Scheduled arrival time (`HHmm`); `temporal_policy="NO_ROLLOVER"`. |
| **13** | `ARR_TIME` | `StringType` | `StringType` | `True` | Actual arrival time (`HHmm`); `temporal_policy="NO_ROLLOVER"`. |
| **14** | `ARR_DELAY` | `StringType` | `DoubleType` | `True` | **CORE MEASURE 4**. Signed arrival delay (`G2-EXC-001_PROVISIONAL`). |
| **15** | `CRS_ELAPSED_TIME` | `StringType` | `DoubleType` | `True` | **CORE MEASURE 5**. Scheduled elapsed time (`G2-EXC-001_PROVISIONAL`). |
| **16** | `ACTUAL_ELAPSED_TIME` | `StringType` | `DoubleType` | `True` | **CORE MEASURE 6**. Actual elapsed time (`G2-EXC-001_PROVISIONAL`). |
| **17** | `AIR_TIME` | `StringType` | `DoubleType` | `True` | **CORE MEASURE 7**. Airborne duration (`G2-EXC-001_PROVISIONAL`). |
| **18** | `FLIGHTS` | `StringType` | `DoubleType` | `True` | Preserved float64; metadata `prohibited_use="KPI_DENOMINATOR_WEIGHTING"`. |
| **19** | `MONTH` | `StringType` | `LongType` | `True` | Calendar month (1-12); Int64 nullable. |
| **20** | `DAY_OF_MONTH` | `StringType` | `LongType` | `True` | Day of month (1-31); Int64 nullable. |
| **21** | `DAY_OF_WEEK` | `StringType` | `LongType` | `True` | Day of week (1-7); Int64 nullable. |
| **22** | `ORIGIN_INDEX` | `StringType` | `LongType` | `True` | Origin airport index; Int64 nullable. |
| **23** | `DEST_INDEX` | `StringType` | `LongType` | `True` | Destination airport index; Int64 nullable. |
| **24** | `O_TEMP` | `StringType` | `DoubleType` | `True` | Origin temperature; `status="CONDITIONAL_NO_GO"` (FP-DEC-017). |
| **25** | `O_PRCP` | `StringType` | `DoubleType` | `True` | Origin precipitation; `status="CONDITIONAL_NO_GO"` (FP-DEC-017). |
| **26** | `O_WSPD` | `StringType` | `DoubleType` | `True` | Origin wind speed; `status="CONDITIONAL_NO_GO"` (FP-DEC-017). |
| **27** | `D_TEMP` | `StringType` | `DoubleType` | `True` | Destination temperature; `status="CONDITIONAL_NO_GO"` (FP-DEC-017). |
| **28** | `D_PRCP` | `StringType` | `DoubleType` | `True` | Destination precipitation; `status="CONDITIONAL_NO_GO"` (FP-DEC-017). |
| **29** | `D_WSPD` | `StringType` | `DoubleType` | `True` | Destination wind speed; `status="CONDITIONAL_NO_GO"` (FP-DEC-017). |
| **30** | `O_LATITUDE` | `StringType` | `DoubleType` | `True` | Origin latitude coordinate. |
| **31** | `O_LONGITUDE` | `StringType` | `DoubleType` | `True` | Origin longitude coordinate. |
| **32** | `D_LATITUDE` | `StringType` | `DoubleType` | `True` | Destination latitude coordinate. |
| **33** | `D_LONGITUDE` | `StringType` | `DoubleType` | `True` | Destination longitude coordinate. |

---

## 3. ACCESSOR FUNCTIONS & CONTRACT INTERFACES

Module `schema.py` provides deterministic, immutable accessors:
1. `get_canonical_column_names() -> List[str]`: Returns a copy of the canonical 34 column names.
2. `get_raw_business_schema() -> StructType`: Returns the 34-field `StringType` schema for business data validation.
3. `get_raw_parser_schema() -> StructType`: Returns the 35-field PySpark parser schema including `_corrupt_record`.
4. `get_curated_parquet_schema() -> StructType`: Returns the strongly-typed 34-column Parquet storage schema.
5. `validate_column_names(column_names: List[str]) -> bool`: Pure logical predicate verifying that an incoming column header sequence matches the canonical sequence with zero drift.
