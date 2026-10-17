# T007-01 CONTRACT TRACEABILITY MATRIX

**Document ID:** `DOC-T007-01-03-TRACEABILITY`  
**Task ID:** `T007-01` (Canonical Schema Module)  
**Parent Gate:** `G4` (`PLANNED / NOT_COMPLETED`)  
**Design Authority:** Data Contract Auditor & Repository Governance Reviewer  

---

## 1. COMPREHENSIVE CONTRACT TRACEABILITY MATRIX

| Item ID | Governance Anchor | Contract Requirement | Schema Implementation In `schema.py` | Compliance Verification |
| :---: | :--- | :--- | :--- | :---: |
| **TR-01** | `DATA_DICTIONARY.md` | Exact 34 canonical columns; physical order 0..33 | `CANONICAL_COLUMN_NAMES` tuple matches exact names and sequence. | **100% PASS** (`test_01`, `test_02`) |
| **TR-02** | `DATA_DICTIONARY.md` | Zero unapproved fabricated columns (`CANCELLED`, `DIVERTED`, `DISTANCE`) | `FORBIDDEN_COLUMNS` strictly excluded from all schemas. | **100% PASS** (`test_03`) |
| **TR-03** | `DATA_DICTIONARY.md` | `OP_CARRIER_FL_NUM` raw audited dtype `float64` | `CURATED_PARQUET_SCHEMA["OP_CARRIER_FL_NUM"]` is `DoubleType` (float64). | **100% PASS** (`test_10`) |
| **TR-04** | `DATA_DICTIONARY.md` | `MONTH`, `DAY_OF_MONTH`, `DAY_OF_WEEK` are nullable Int64 | Defined as `LongType(nullable=True)`. | **100% PASS** (`test_09`) |
| **TR-05** | `DATA_CONTRACT.md` (DC-11) | Tri-state disjoint accounting (`raw = accepted + quarantined + rejected`) | Separates 34 business columns from technical `_corrupt_record`. | **100% PASS** (`test_07`) |
| **TR-06** | `DATA_CONTRACT.md` (DC-12) | Record Validity $\ne$ Metric Validity; non-numeric delay does not discard flight | `RAW_CSV_BUSINESS_SCHEMA` uses `StringType` for all 34 fields. | **100% PASS** (`test_06`) |
| **TR-07** | `FP-DEC-007` | Strict prohibition of date rollover deduction or timezone invention | Local time fields defined as `StringType`; metadata `NO_ROLLOVER`. | **100% PASS** (`test_11`) |
| **TR-08** | `FP-DEC-010` | `FLIGHTS` strictly prohibited as KPI denominator weight | Field metadata `prohibited_use="KPI_DENOMINATOR_WEIGHTING"`. | **100% PASS** (`test_04`) |
| **TR-09** | `FP-DEC-017` | Weather fields classified as `APPROVED_CONDITIONAL_NO_GO` | 6 weather columns defined with `metadata={"status": "CONDITIONAL_NO_GO"}`. | **100% PASS** (`test_05`) |
| **TR-10** | `G2-EXC-001` | 7 continuous CORE measures physical units provisional | Field metadata explicitly marks `G2-EXC-001_PROVISIONAL`. | **100% PASS** (`test_08`) |
| **TR-11** | `G3-COND-A` | Non-positive flight number (`FL_NUM <= 0`) is provisional anomaly | `DoubleType(nullable=True)` avoids premature rejection at schema layer. | **100% PASS** (`test_10`) |
| **TR-12** | `ROADMAP.md` (G4) | Pure schema logic without ingestion side effects | Pure schema module: zero disk reads, zero Spark job submissions. | **100% PASS** (`test_12`, `test_14`) |

---

## 2. AUDIT SUMMARY
Every canonical constraint from `DATA_DICTIONARY.md`, `DATA_CONTRACT.md`, `DECISIONS.md`, and Gate G2/G3 signoff agreements has direct 1-to-1 implementation traceability in `schema.py` and is fully verified by automated unit tests in `test_t007_schema.py`.
