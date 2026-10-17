# T007 DESIGN EXIT DATE/TIME FINAL RULES — CANONICAL TEMPORAL SPECIFICATION

**Document ID:** `DOC-T007-DESIGN-EXIT-04-DATE-TIME`  
**Task ID:** `T-007` (Raw CSV Ingestion Pipeline)  
**Phase:** `DESIGN RECONCILIATION (R1-EXIT)`  
**Gate:** `G4` (`PLANNED / NOT_COMPLETED`)  
**Design Authority:** Lead PySpark Data Engineer & Data Contract Auditor  
**Binding Standards:** `DATA_CONTRACT.md`, `DATA_DICTIONARY.md`, `FP-DEC-007`, `G2-EXC-001`, `TEST_PLAN.md` (`TS-002`, `TS-010`, `TS-018`)  

---

## 1. `FL_DATE` CANONICAL SPECIFICATION & UNAMBIGUOUS REGEX

To eliminate Markdown table delimiter escaping confusion (where `|` had to be escaped as `\|`), the canonical regular expression for `FL_DATE` validation is formally declared in standalone syntax:

### 1.1. Authoritative Regex Specification
```regex
^(?:\d{4}-\d{2}-\d{2}|\d{4}-\d{2}-\d{2} 00:00:00)$
```

### 1.2. Regex Validation Rules
1. **Permitted Patterns:**
   - Standard ISO-8601 calendar date: `YYYY-MM-DD` (e.g. `2016-01-01`).
   - TranStats midnight-timestamped string: `YYYY-MM-DD 00:00:00` (e.g. `2016-01-01 00:00:00`).
2. **Target Curated Type:**
   Extracted to PySpark `DateType` (`YYYY-MM-DD`).
3. **Synthetic Test Vectors:**

| Test Vector String | Category | Expected Validation Result | Technical Disposition |
|---|---|---|---|
| `"2016-01-01"` | Positive | **VALID** | Extracted as Date `2016-01-01` |
| `"2024-02-29"` | Positive | **VALID** (Leap Day) | Extracted as Date `2024-02-29` |
| `"2019-12-31 00:00:00"` | Positive | **VALID** (Midnight Timestamp) | Extracted as Date `2019-12-31` |
| `"2018-02-31"` | Negative | **INVALID** (Calendar Day Out of Domain) | Quarantined (`INVALID_FL_DATE_CORE_ANCHOR`) |
| `"01/01/2016"` | Negative | **INVALID** (Slash Format) | Quarantined (`INVALID_FL_DATE_CORE_ANCHOR`) |
| `"2016-1-1"` | Negative | **INVALID** (Unpadded Month/Day) | Quarantined (`INVALID_FL_DATE_CORE_ANCHOR`) |
| `"2024-03-15 12:30:00"`| Negative | **INVALID** (Non-Midnight Timestamp) | Quarantined (`INVALID_FL_DATE_CORE_ANCHOR`) |
| `""` or `null` | Negative | **INVALID** (Empty / Null Anchor) | Quarantined (`MISSING_FL_DATE_CORE_ANCHOR`) |

---

## 2. TIME FIELDS & WALL-CLOCK CONSTRAINTS (`FP-DEC-007`)

The 6 time columns (`CRS_DEP_TIME`, `DEP_TIME`, `CRS_ARR_TIME`, `ARR_TIME`, `WHEELS_OFF`, `WHEELS_ON`) represent local wall-clock times in official BTS TranStats notation:

### 2.1. Strictly Enforced Constraints
1. **NO TIMEZONE FABRICATION:**
   TranStats extracts do not provide timezone offsets or local time zone identifiers. The pipeline **must not invent timezone conversions** or UTC offsets.
2. **NO OVERNIGHT ROLLOVER INFERENCE:**
   Under `FP-DEC-007`, the pipeline **must never add +24 hours** to arrival times or shift calendar dates when `ARR_TIME < DEP_TIME`. TranStats does not provide flight leg arrival dates; inferring next-day arrival causes severe distortion in red-eye flights.
3. **Controlled Zero-Padding Rule:**
   - **DO NOT blindly zero-pad strings.** If a raw token already contains non-integer characters or timestamps, blind padding corrupts data.
   - Raw string tokens are preserved in the Bronze staging layer.
   - Conversion to 4-character `HHmm` is applied **strictly to verified integer numeric tokens** (e.g. integer `930` $\to$ `"0930"`, `5` $\to$ `"0005"`, `0` $\to$ `"0000"`). If the raw token is float `930.0`, the fractional `.0` is stripped before padding to `"0930"`.
4. **Storage Nullability:**
   All 6 time columns are stored in Curated Parquet as **`StringType` (nullable = True)**.

---

## 3. CALENDAR FIELDS & NULLABLE SEMANTICS

In accordance with `DATA_DICTIONARY.md`:
- `MONTH`: Calendar month (1–12), `IntegerType`, **nullable = True**.
- `DAY_OF_MONTH`: Day of month (1–31), `IntegerType`, **nullable = True**.
- `DAY_OF_WEEK`: Day of week (1–7, 1=Monday per BTS standard), `IntegerType`, **nullable = True**.
- `ORIGIN_INDEX`, `DEST_INDEX`: Integer indexes, `IntegerType`, **nullable = True**.

---

## 4. PROVISIONAL STATUS OF 7 CORE MEASURES (`G2-EXC-001`)

The units of the 7 numerical measures (`ARR_DELAY`, `DEP_DELAY`, `TAXI_OUT`, `TAXI_IN`, `AIR_TIME`, `ACTUAL_ELAPSED_TIME`, `CRS_ELAPSED_TIME`) remain strictly provisional:
$$\text{Unit Status} = \mathbf{OFFICIAL\_MINUTES\_EMPIRICALLY\_CONSISTENT\_PROVISIONAL}$$
1. Delay values are valid signed doubles: **negative delays are preserved exactly** (early departures/arrivals).
2. Physical units must **NOT** be declared `VERIFIED` until test **`TS-018`** achieves `PASS` at Gate **G5** before Gate **G6**.

---

## 5. DATE/TIME SPECIFICATION VERDICT

The date and time specification provides an unambiguous single source of truth, eliminates Markdown escaping risks, and strictly enforces `FP-DEC-007` and `G2-EXC-001`.

**DATE/TIME RULES VERDICT: FULLY SPECIFIED & CANONICALLY TRACEABLE.**
