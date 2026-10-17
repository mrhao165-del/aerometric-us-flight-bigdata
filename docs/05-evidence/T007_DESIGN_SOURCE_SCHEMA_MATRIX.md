# T007 DESIGN SOURCE SCHEMA MATRIX — EXACT 34-COLUMN CANONICAL MAPPING

**Document ID:** `DOC-T007-DESIGN-02-SCHEMA-MATRIX`  
**Task ID:** `T-007` (Raw CSV Ingestion Pipeline)  
**Phase:** `DESIGN ONLY`  
**Gate:** `G4` (`PLANNED / NOT_COMPLETED`)  
**Design Authority:** Senior Big Data Architect & Lead PySpark Data Engineer  
**Canonical Compliance:** `DATA_CONTRACT.md`, `DATA_DICTIONARY.md`, `KPI_SPEC.md`, `FP-DEC-010`, `FP-DEC-017`  

---

## 1. RAW SOURCE INVENTORY & PHYSICAL VALIDATION

The US Flight Performance Analysis repository processes 9 annual CSV files located at:
`data/raw/tabular/{year}/flight_with_weather_{year}.csv` for years `2016` through `2024`.

### 1.1. Physical Source Inventory Table
Physical audit confirms the following exact file sizes and record counts across all 9 years:

| Year | File Relative Path | Audited File Size (Bytes) | Audited Raw Rows (including Header) | Header Column Count |
|---|---|---|---|---|
| **2016** | `data/raw/tabular/2016/flight_with_weather_2016.csv` | 1,563,086,178 | 5,617,659 | 34 |
| **2017** | `data/raw/tabular/2017/flight_with_weather_2017.csv` | 1,580,248,321 | 5,674,622 | 34 |
| **2018** | `data/raw/tabular/2018/flight_with_weather_2018.csv` | 1,585,027,330 | 5,689,512 | 34 |
| **2019** | `data/raw/tabular/2019/flight_with_weather_2019.csv` | 2,058,954,682 | 7,422,038 | 34 |
| **2020** | `data/raw/tabular/2020/flight_with_weather_2020.csv` | 1,323,178,829 | 4,688,355 | 34 |
| **2021** | `data/raw/tabular/2021/flight_with_weather_2021.csv` | 1,675,199,445 | 5,983,494 | 34 |
| **2022** | `data/raw/tabular/2022/flight_with_weather_2022.csv` | 1,895,301,578 | 6,767,316 | 34 |
| **2023** | `data/raw/tabular/2023/flight_with_weather_2023.csv` | 1,948,019,165 | 6,937,652 | 34 |
| **2024** | `data/raw/tabular/2024/flight_with_weather_2024.csv` | 1,567,350,645 | 5,893,364 | 34 |
| **TOTAL**| **9 Annual Files** | **15,196,366,173 bytes** | **54,674,012 lines (54,674,003 data rows)** | **34 identical** |

> [!IMPORTANT]
> Physical header verification across all 9 annual CSV files proves that the column names and column order are **100% identical** across the entire 2016–2024 dataset. There is zero column name drift, zero column reordering, and zero column insertion across all 9 years.

---

## 2. CANONICAL 34-COLUMN SCHEMA SPECIFICATION MATRIX

The following table provides the exhaustive canonical mapping from raw CSV tokens to PySpark `StructField` types, nullability rules, parsing semantics, and governance constraints:

| # | Column Name | Raw CSV Type | Target PySpark Type | Nullable | Primary Semantics & Ingestion Constraints |
|---|---|---|---|---|---|
| 0 | `FL_DATE` | String (`YYYY-MM-DD` or `YYYY-MM-DD 00:00:00`) | `DateType` | False (Core Anchor) | Flight date. Must match anchored regex `^(?:\d{4}-\d{2}-\d{2}\|\d{4}-\d{2}-\d{2} 00:00:00)$`. If null or unparseable $\to$ QUARANTINE (`QUARANTINE_MALFORMED_DATE`). |
| 1 | `OP_CARRIER` | String (2-3 chars) | `StringType` | False (Core Anchor) | Reporting operating carrier IATA code (e.g. `AA`, `DL`, `WN`). If null or empty $\to$ QUARANTINE (`QUARANTINE_NULL_CARRIER`). |
| 2 | `OP_CARRIER_FL_NUM` | Numeric/String (e.g. `1234` or `1234.0`) | `IntegerType` | False (Provisional) | Operating flight number. Cast safely from double/string to integer. `G3-COND-A` rule: If null, 0, or negative $\to$ QUARANTINE (`QUARANTINE_INVALID_FL_NUM`). |
| 3 | `ORIGIN` | String (3 chars) | `StringType` | False (Core Anchor) | Origin airport 3-letter IATA code. If null or empty $\to$ QUARANTINE (`QUARANTINE_NULL_ORIGIN_DEST`). |
| 4 | `DEST` | String (3 chars) | `StringType` | False (Core Anchor) | Destination airport 3-letter IATA code. If null or empty $\to$ QUARANTINE (`QUARANTINE_NULL_ORIGIN_DEST`). |
| 5 | `CRS_DEP_TIME` | Numeric/String (e.g. `930`, `0930`, `930.0`) | `StringType` | True | Scheduled departure time formatted as 4-character string `HHmm`. Left-pad with zeros if numeric. Never construct rollover dates. |
| 6 | `DEP_TIME` | Numeric/String (e.g. `928`, `0928`, `928.0`) | `StringType` | True | Actual departure time formatted as 4-character string `HHmm`. Left-pad with zeros. |
| 7 | `DEP_DELAY` | Numeric (Float/Double) | `DoubleType` | True | Departure delay in minutes. **CORE MEASURE 1**. Valid signed double. **Negative delays are valid early departures** and must be preserved! |
| 8 | `TAXI_OUT` | Numeric (Float/Double) | `DoubleType` | True | Taxi-out duration in minutes. **CORE MEASURE 2**. Finite double $\ge 0.0$. Negative values are metric-invalid but do not quarantine record. |
| 9 | `WHEELS_OFF` | Numeric/String | `StringType` | True | Wheels-off time formatted as 4-character string `HHmm`. |
| 10 | `WHEELS_ON` | Numeric/String | `StringType` | True | Wheels-on time formatted as 4-character string `HHmm`. |
| 11 | `TAXI_IN` | Numeric (Float/Double) | `DoubleType` | True | Taxi-in duration in minutes. **CORE MEASURE 3**. Finite double $\ge 0.0$. |
| 12 | `CRS_ARR_TIME` | Numeric/String | `StringType` | True | Scheduled arrival time formatted as 4-character string `HHmm`. |
| 13 | `ARR_TIME` | Numeric/String | `StringType` | True | Actual arrival time formatted as 4-character string `HHmm`. |
| 14 | `ARR_DELAY` | Numeric (Float/Double) | `DoubleType` | True | Arrival delay in minutes. **CORE MEASURE 4**. Valid signed double. Negative delays are valid early arrivals! |
| 15 | `CRS_ELAPSED_TIME` | Numeric (Float/Double) | `DoubleType` | True | Scheduled elapsed time in minutes. **CORE MEASURE 5**. Finite double $> 0.0$. |
| 16 | `ACTUAL_ELAPSED_TIME` | Numeric (Float/Double) | `DoubleType` | True | Actual elapsed time in minutes. **CORE MEASURE 6**. Finite double $> 0.0$. |
| 17 | `AIR_TIME` | Numeric (Float/Double) | `DoubleType` | True | Airborne time in minutes. **CORE MEASURE 7**. Finite double $> 0.0$. |
| 18 | `FLIGHTS` | Numeric (strictly `1.0`) | `DoubleType` | False | Canonical row indicator. Per `FP-DEC-010`: **Strictly constant 1.0**. Forbidden to use as weighting factor or aggregation multiplier. |
| 19 | `MONTH` | Integer (1–12) | `IntegerType` | True | Calendar month extracted from `FL_DATE` or raw column. |
| 20 | `DAY_OF_MONTH` | Integer (1–31) | `IntegerType` | True | Day of month. |
| 21 | `DAY_OF_WEEK` | Integer (1–7) | `IntegerType` | True | Day of week (1=Monday per BTS standard). |
| 22 | `ORIGIN_INDEX` | Integer | `IntegerType` | True | Integer index of origin airport. |
| 23 | `DEST_INDEX` | Integer | `IntegerType` | True | Integer index of destination airport. |
| 24 | `O_TEMP` | Numeric (Float/Double) | `DoubleType` | True | Origin temperature. `FP-DEC-017` CONDITIONAL_NO_GO. Preserved in Parquet; nullable; independent of CORE KPI pipeline. |
| 25 | `O_PRCP` | Numeric (Float/Double) | `DoubleType` | True | Origin precipitation. `FP-DEC-017` CONDITIONAL_NO_GO. Preserved in Parquet; nullable. |
| 26 | `O_WSPD` | Numeric (Float/Double) | `DoubleType` | True | Origin wind speed. `FP-DEC-017` CONDITIONAL_NO_GO. Preserved in Parquet; nullable. |
| 27 | `D_TEMP` | Numeric (Float/Double) | `DoubleType` | True | Destination temperature. `FP-DEC-017` CONDITIONAL_NO_GO. Preserved in Parquet; nullable. |
| 28 | `D_PRCP` | Numeric (Float/Double) | `DoubleType` | True | Destination precipitation. `FP-DEC-017` CONDITIONAL_NO_GO. Preserved in Parquet; nullable. |
| 29 | `D_WSPD` | Numeric (Float/Double) | `DoubleType` | True | Destination wind speed. `FP-DEC-017` CONDITIONAL_NO_GO. Preserved in Parquet; nullable. |
| 30 | `O_LATITUDE` | Numeric (Float/Double) | `DoubleType` | True | Origin latitude coordinate. Preserved in Parquet; nullable. |
| 31 | `O_LONGITUDE` | Numeric (Float/Double) | `DoubleType` | True | Origin longitude coordinate. Preserved in Parquet; nullable. |
| 32 | `D_LATITUDE` | Numeric (Float/Double) | `DoubleType` | True | Destination latitude coordinate. Preserved in Parquet; nullable. |
| 33 | `D_LONGITUDE` | Numeric (Float/Double) | `DoubleType` | True | Destination longitude coordinate. Preserved in Parquet; nullable. |

---

## 3. ABSENT COLUMNS INAUDITED AS CANONICAL ABSENCES

The following columns, commonly found in certain BTS TranStats raw extracts, **DO NOT EXIST** in the audited 2016–2024 source dataset and must **NEVER** be referenced, filtered, or fabricated by the ingestion pipeline:

1. `CANCELLED`: Does not exist. No flight cancellation filter may be applied!
2. `DIVERTED`: Does not exist. No diversion filter may be applied!
3. `CANCELLATION_CODE`: Does not exist.
4. `DISTANCE` / `DISTANCE_GROUP`: Does not exist.
5. Delay breakdown categories (`CARRIER_DELAY`, `WEATHER_DELAY`, `NAS_DELAY`, `SECURITY_DELAY`, `LATE_AIRCRAFT_DELAY`): Do not exist.
6. `TAXI_DIFF` / `DEP_DELAY_GROUP` / `ARR_DELAY_GROUP`: Do not exist.

> [!WARNING]
> Attempting to filter out rows where `CANCELLED == 1` or `DIVERTED == 1` will fail-fast with a column resolution error or silently corrupt row accounting. Ingestion acceptance must rely solely on structural validity and the core identity anchors (`FL_DATE`, `OP_CARRIER`, `ORIGIN`, `DEST`, `OP_CARRIER_FL_NUM`).

---

## 4. CANONICAL PYSPARK STRUCTTYPE DEFINITION

The production-ready PySpark schema definition proposed for implementation in `src/flight_pipeline/ingestion/schema.py` is specified as follows:

```python
from pyspark.sql.types import (
    StructType,
    StructField,
    StringType,
    IntegerType,
    DoubleType,
    DateType,
)

CANONICAL_RAW_COLUMN_COUNT = 34

CANONICAL_CSV_SCHEMA = StructType([
    StructField("FL_DATE", StringType(), False),            # Raw token parsed to DateType in classification
    StructField("OP_CARRIER", StringType(), False),
    StructField("OP_CARRIER_FL_NUM", DoubleType(), True),   # Raw numeric in CSV (may parse as float, e.g. 1234.0)
    StructField("ORIGIN", StringType(), False),
    StructField("DEST", StringType(), False),
    StructField("CRS_DEP_TIME", StringType(), True),
    StructField("DEP_TIME", StringType(), True),
    StructField("DEP_DELAY", DoubleType(), True),
    StructField("TAXI_OUT", DoubleType(), True),
    StructField("WHEELS_OFF", StringType(), True),
    StructField("WHEELS_ON", StringType(), True),
    StructField("TAXI_IN", DoubleType(), True),
    StructField("CRS_ARR_TIME", StringType(), True),
    StructField("ARR_TIME", StringType(), True),
    StructField("ARR_DELAY", DoubleType(), True),
    StructField("CRS_ELAPSED_TIME", DoubleType(), True),
    StructField("ACTUAL_ELAPSED_TIME", DoubleType(), True),
    StructField("AIR_TIME", DoubleType(), True),
    StructField("FLIGHTS", DoubleType(), False),
    StructField("MONTH", IntegerType(), True),
    StructField("DAY_OF_MONTH", IntegerType(), True),
    StructField("DAY_OF_WEEK", IntegerType(), True),
    StructField("ORIGIN_INDEX", IntegerType(), True),
    StructField("DEST_INDEX", IntegerType(), True),
    StructField("O_TEMP", DoubleType(), True),
    StructField("O_PRCP", DoubleType(), True),
    StructField("O_WSPD", DoubleType(), True),
    StructField("D_TEMP", DoubleType(), True),
    StructField("D_PRCP", DoubleType(), True),
    StructField("D_WSPD", DoubleType(), True),
    StructField("O_LATITUDE", DoubleType(), True),
    StructField("O_LONGITUDE", DoubleType(), True),
    StructField("D_LATITUDE", DoubleType(), True),
    StructField("D_LONGITUDE", DoubleType(), True),
])

CANONICAL_CURATED_SCHEMA = StructType([
    StructField("FL_DATE", DateType(), False),
    StructField("OP_CARRIER", StringType(), False),
    StructField("OP_CARRIER_FL_NUM", IntegerType(), False),
    StructField("ORIGIN", StringType(), False),
    StructField("DEST", StringType(), False),
    StructField("CRS_DEP_TIME", StringType(), True),
    StructField("DEP_TIME", StringType(), True),
    StructField("DEP_DELAY", DoubleType(), True),
    StructField("TAXI_OUT", DoubleType(), True),
    StructField("WHEELS_OFF", StringType(), True),
    StructField("WHEELS_ON", StringType(), True),
    StructField("TAXI_IN", DoubleType(), True),
    StructField("CRS_ARR_TIME", StringType(), True),
    StructField("ARR_TIME", StringType(), True),
    StructField("ARR_DELAY", DoubleType(), True),
    StructField("CRS_ELAPSED_TIME", DoubleType(), True),
    StructField("ACTUAL_ELAPSED_TIME", DoubleType(), True),
    StructField("AIR_TIME", DoubleType(), True),
    StructField("FLIGHTS", DoubleType(), False),
    StructField("MONTH", IntegerType(), True),
    StructField("DAY_OF_MONTH", IntegerType(), True),
    StructField("DAY_OF_WEEK", IntegerType(), True),
    StructField("ORIGIN_INDEX", IntegerType(), True),
    StructField("DEST_INDEX", IntegerType(), True),
    StructField("O_TEMP", DoubleType(), True),
    StructField("O_PRCP", DoubleType(), True),
    StructField("O_WSPD", DoubleType(), True),
    StructField("D_TEMP", DoubleType(), True),
    StructField("D_PRCP", DoubleType(), True),
    StructField("D_WSPD", DoubleType(), True),
    StructField("O_LATITUDE", DoubleType(), True),
    StructField("O_LONGITUDE", DoubleType(), True),
    StructField("D_LATITUDE", DoubleType(), True),
    StructField("D_LONGITUDE", DoubleType(), True),
])
```

---

## 5. DESIGN REVIEW FINDINGS & VERDICT

1. The exact 34 columns are physically verified across all 9 annual raw CSV files.
2. The PySpark schema aligns 100% with `DATA_CONTRACT.md` and `DATA_DICTIONARY.md`.
3. Nullability policies cleanly decouple record acceptance from single-metric validity.
4. Auxiliary weather columns are strictly preserved in Parquet storage but decoupled from CORE KPI processing per `FP-DEC-017`.

**SCHEMA MATRIX VERDICT: COMPLETE & CANONICALLY COMPLIANT.**
