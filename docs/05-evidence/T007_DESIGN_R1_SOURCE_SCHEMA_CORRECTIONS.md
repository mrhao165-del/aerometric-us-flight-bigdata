# T007 DESIGN R1 SOURCE SCHEMA CORRECTIONS — EXACT 34-COLUMN FIDELITY & DATA TYPE PARSING

**Document ID:** `DOC-T007-DESIGN-R1-02-SCHEMA-CORRECTIONS`  
**Task ID:** `T-007` (Raw CSV Ingestion Pipeline)  
**Phase:** `DESIGN REMEDIATION (R1)`  
**Gate:** `G4` (`PLANNED / NOT_COMPLETED`)  
**Design Authority:** Lead PySpark Data Engineer & Data Contract Auditor  
**Binding Standards:** `DATA_CONTRACT.md`, `DATA_DICTIONARY.md`, `FP-DEC-007`, `FP-DEC-010`, `FP-DEC-017`, `G2-EXC-001`  

---

## 1. CANONICAL 34-COLUMN PHYSICAL MAPPING & SEPARATION OF LAYERS

To ensure absolute fidelity to raw data and prevent subtle semantic corruption during ingestion, the design establishes a strict architectural separation between the **Raw CSV Parsing Schema** (`Bronze Layer`) and the **Curated Parquet Storage Schema** (`Silver Layer`):

```
+------------------------------------+          +------------------------------------+
|       RAW CSV PARSING SCHEMA       |          |      CURATED PARQUET SCHEMA        |
|  - All 34 columns physically mapped|          |  - All 34 columns stored in Parquet|
|  - String/Double raw tokens        |  ----->  |  - Parsed DateType & IntegerType   |
|  - No data dropping or invention   |          |  - Nullable semantics preserved    |
|  - _corrupt_record for syntax traps|          |  - Zero next-day/timezone rollover |
+------------------------------------+          +------------------------------------+
```

### 1.1. Exact 34-Column Physical Schema Specification

| # | Column Name | Raw CSV Type | Curated Target Type | Nullable | Canonical Semantics & Parsing Rules |
|---|---|---|---|---|---|
| 0 | `FL_DATE` | String (`YYYY-MM-DD` or `YYYY-MM-DD 00:00:00`) | `DateType` | False (Anchor) | Flight date. Verified by regex: `^(?:\d{4}-\d{2}-\d{2}\|\d{4}-\d{2}-\d{2} 00:00:00)$`. (Note: in Markdown tables the pipe is escaped as `\|`, representing regex alternation `|`). If unparseable $\to$ provisional quarantine. |
| 1 | `OP_CARRIER` | String | `StringType` | False (Anchor) | 2–3 letter IATA carrier code. If null/empty $\to$ quarantine (`MISSING_CARRIER_CORE_ANCHOR`). |
| 2 | `OP_CARRIER_FL_NUM` | String/Double (e.g. `1234` or `1234.0`) | `IntegerType` | True (Provisional) | Flight number. **Safe Numeric Cast Rule:** If raw is float `x.0`, cast to integer `x`. If raw has non-zero fractional part (`x.5`) or non-numeric tokens $\to$ parse anomaly flag. Governed by `G3-COND-A`. |
| 3 | `ORIGIN` | String | `StringType` | False (Anchor) | 3-letter IATA origin airport code. If null/empty $\to$ quarantine (`MISSING_AIRPORT_CORE_ANCHOR`). |
| 4 | `DEST` | String | `StringType` | False (Anchor) | 3-letter IATA destination airport code. If null/empty $\to$ quarantine (`MISSING_AIRPORT_CORE_ANCHOR`). |
| 5 | `CRS_DEP_TIME` | String/Numeric | `StringType` | True | Scheduled departure time (`HHmm`). Raw string preserved. No date rollover calculated (`FP-DEC-007`). |
| 6 | `DEP_TIME` | String/Numeric | `StringType` | True | Actual departure time (`HHmm`). Raw string preserved. |
| 7 | `DEP_DELAY` | Numeric (Double) | `DoubleType` | True | **CORE MEASURE 1**. Signed departure delay in minutes. **Negative values preserved** as valid early departures. Units: `OFFICIAL_MINUTES_EMPIRICALLY_CONSISTENT_PROVISIONAL` (`G2-EXC-001`). |
| 8 | `TAXI_OUT` | Numeric (Double) | `DoubleType` | True | **CORE MEASURE 2**. Taxi-out duration in minutes. Units: provisional. |
| 9 | `WHEELS_OFF` | String/Numeric | `StringType` | True | Wheels-off time (`HHmm`). |
| 10 | `WHEELS_ON` | String/Numeric | `StringType` | True | Wheels-on time (`HHmm`). |
| 11 | `TAXI_IN` | Numeric (Double) | `DoubleType` | True | **CORE MEASURE 3**. Taxi-in duration in minutes. Units: provisional. |
| 12 | `CRS_ARR_TIME` | String/Numeric | `StringType` | True | Scheduled arrival time (`HHmm`). |
| 13 | `ARR_TIME` | String/Numeric | `StringType` | True | Actual arrival time (`HHmm`). |
| 14 | `ARR_DELAY` | Numeric (Double) | `DoubleType` | True | **CORE MEASURE 4**. Signed arrival delay in minutes. **Negative values preserved** as valid early arrivals. Units: provisional. |
| 15 | `CRS_ELAPSED_TIME`| Numeric (Double) | `DoubleType` | True | **CORE MEASURE 5**. Scheduled elapsed duration in minutes. Units: provisional. |
| 16 | `ACTUAL_ELAPSED_TIME`| Numeric (Double) | `DoubleType` | True | **CORE MEASURE 6**. Actual elapsed duration in minutes. Units: provisional. |
| 17 | `AIR_TIME` | Numeric (Double) | `DoubleType` | True | **CORE MEASURE 7**. Airborne duration in minutes. Units: provisional. |
| 18 | `FLIGHTS` | Numeric (Double) | `DoubleType` | False | Strictly constant `1.0` in all audited rows. Per `FP-DEC-010`: **Forbidden to use sum(FLIGHTS) as KPI denominator**. Canonical count is `count_records`. |
| 19 | `MONTH` | Numeric (Int64 in raw) | `IntegerType` | True | Calendar month (1–12). Nullable per `DATA_DICTIONARY.md`. |
| 20 | `DAY_OF_MONTH` | Numeric (Int64 in raw) | `IntegerType` | True | Day of month (1–31). Nullable. |
| 21 | `DAY_OF_WEEK` | Numeric (Int64 in raw) | `IntegerType` | True | Day of week (1–7). Nullable. |
| 22 | `ORIGIN_INDEX` | Numeric (Int64 in raw) | `IntegerType` | True | Origin airport index. Nullable. |
| 23 | `DEST_INDEX` | Numeric (Int64 in raw) | `IntegerType` | True | Destination airport index. Nullable. |
| 24 | `O_TEMP` | Numeric (Double) | `DoubleType` | True | Origin temperature. `FP-DEC-017` CONDITIONAL_NO_GO. Preserved in Parquet; nullable; independent of CORE KPI pipeline. |
| 25 | `O_PRCP` | Numeric (Double) | `DoubleType` | True | Origin precipitation. `FP-DEC-017` CONDITIONAL_NO_GO. Preserved in Parquet; nullable. |
| 26 | `O_WSPD` | Numeric (Double) | `DoubleType` | True | Origin wind speed. `FP-DEC-017` CONDITIONAL_NO_GO. Preserved in Parquet; nullable. |
| 27 | `D_TEMP` | Numeric (Double) | `DoubleType` | True | Destination temperature. `FP-DEC-017` CONDITIONAL_NO_GO. Preserved in Parquet; nullable. |
| 28 | `D_PRCP` | Numeric (Double) | `DoubleType` | True | Destination precipitation. `FP-DEC-017` CONDITIONAL_NO_GO. Preserved in Parquet; nullable. |
| 29 | `D_WSPD` | Numeric (Double) | `DoubleType` | True | Destination wind speed. `FP-DEC-017` CONDITIONAL_NO_GO. Preserved in Parquet; nullable. |
| 30 | `O_LATITUDE` | Numeric (Double) | `DoubleType` | True | Origin latitude coordinate. Preserved; nullable. |
| 31 | `O_LONGITUDE` | Numeric (Double) | `DoubleType` | True | Origin longitude coordinate. Preserved; nullable. |
| 32 | `D_LATITUDE` | Numeric (Double) | `DoubleType` | True | Destination latitude coordinate. Preserved; nullable. |
| 33 | `D_LONGITUDE` | Numeric (Double) | `DoubleType` | True | Destination longitude coordinate. Preserved; nullable. |

---

## 2. SPECIAL FIELD PARSING RULES & BOUNDARIES

### 2.1. Safe Numeric Casting for `OP_CARRIER_FL_NUM`
In the raw CSV files, `OP_CARRIER_FL_NUM` is frequently represented as float literals (e.g. `1234.0`) or string digits (`"1234"`). Direct cast to integer via naive truncating casts could produce unexpected behavior:
1. **Rule 1 (Valid Integer / Float Representation):** If the token is numeric and has zero fractional component (e.g. `1234.0` or `1234`), it is cast to integer `1234`.
2. **Rule 2 (Non-Zero Fraction Anomaly):** If a flight number token contains a non-zero fractional component (e.g. `1234.5`), it indicates token corruption and must be flagged as a parse anomaly rather than silently truncated to `1234`.
3. **Rule 3 (Non-Numeric Tokens):** If the token contains alphabetic characters (e.g. `"DL123"`), standard integer cast returns `null`, triggering anchor validation.

### 2.2. Prohibition on Date Rollover & Timezone Fabrication (`FP-DEC-007`)
1. **Raw Time Representation:** Scheduled and actual times (`CRS_DEP_TIME`, `DEP_TIME`, `CRS_ARR_TIME`, `ARR_TIME`) represent local wall-clock times in `HHmm` format without timezone offsets.
2. **Strict Ingestion Rule:** The ingestion pipeline **MUST NOT** attempt to construct composite timestamps (e.g. `YYYY-MM-DD HH:mm:ss`) or invent next-day calendar rollovers for overnight flights (e.g. adding +24h when `ARR_TIME < DEP_TIME`). Per `FP-DEC-007` and `T-004` temporal audit, all derived timestamp calculations are formally deferred or classified as `NOT_AVAILABLE` in the Bronze/Silver core pipeline.
3. **Zero-Padding Format:** Time values that parse as integers (e.g. `930`) are converted to standard 4-character strings (`"0930"`) only where verified by synthetic unit tests. Raw string representations are preserved without truncating trailing zeros.

### 2.3. Provisional Status of 7 CORE Measures (`G2-EXC-001`)
The physical units of the 7 numerical measures (`ARR_DELAY`, `DEP_DELAY`, `TAXI_OUT`, `TAXI_IN`, `AIR_TIME`, `ACTUAL_ELAPSED_TIME`, `CRS_ELAPSED_TIME`) remain strictly:
$$\text{Unit Status} = \mathbf{OFFICIAL\_MINUTES\_EMPIRICALLY\_CONSISTENT\_PROVISIONAL}$$
It is strictly forbidden to claim that these units are `VERIFIED` during T-007 design or implementation. Full physical validation against official BTS documentation is an explicit gate blocker for Gate **G5** (`TS-018`) before Gate **G6**.

---

## 3. ABSENT COLUMNS REAFFIRMATION

The canonical source dataset contains exactly 34 columns. The following columns **DO NOT EXIST** in the raw CSV files and must never be referenced or fabricated:
1. `CANCELLED`: Does not exist. No flight cancellation filter may be applied!
2. `DIVERTED`: Does not exist. No diversion filter may be applied!
3. `CANCELLATION_CODE`: Does not exist.
4. `DISTANCE` / `DISTANCE_GROUP`: Does not exist.
5. Delay breakdown columns (`CARRIER_DELAY`, `WEATHER_DELAY`, `NAS_DELAY`, `SECURITY_DELAY`, `LATE_AIRCRAFT_DELAY`): Do not exist.

---

## 4. SCHEMA CORRECTIONS VERDICT

The 34-column schema specifications have been fully corrected and aligned with canonical contracts, safe numeric casting rules, and governance exceptions.

**SCHEMA CORRECTIONS VERDICT: CANONICALLY ALIGNED & APPROVED.**
