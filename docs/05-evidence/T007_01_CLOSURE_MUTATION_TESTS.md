# T007-01 CLOSURE MUTATION & ISOLATION REGRESSION TEST REPORT

**Document ID:** `DOC-T007-01-CLOSURE-02-MUTATION-TESTS`  
**Task ID:** `T007-01-FINAL-CLOSURE`  
**Parent Gate:** `G4` (`PLANNED / NOT_COMPLETED`)  
**Test Suite:** `tests/test_t007_schema.py`  
**Auditor:** Senior PySpark QA Engineer & Data Contract Auditor  
**Date:** 2026-10-17  

---

## 1. Test-Driven Defect Reproduction (Failing Tests First)

Prior to applying any source remediation in `schema.py`, 7 new regression tests were authored in `tests/test_t007_schema.py`:
- 5 Mutation Isolation tests (`MUT-01` through `MUT-05`)
- 2 Scope and Contract tests (`CONTRACT-01` and `CONTRACT-02`)

Executing the test suite against the unpatched implementation resulted in **4 distinct assertion failures**, confirming the presence of shared mutable state:

```text
======================================================================
FAIL: test_mut_01_raw_business_isolation (tests.test_t007_schema.TestCanonicalSchemaModule)
AssertionError: 35 != 34 : MUT-01 FAILED: Mutating s1 contaminated subsequent get_raw_business_schema() calls!

======================================================================
FAIL: test_mut_02_raw_parser_isolation (tests.test_t007_schema.TestCanonicalSchemaModule)
AssertionError: 36 != 35 : MUT-02 FAILED: Mutating p1 contaminated subsequent get_raw_parser_schema() calls!

======================================================================
FAIL: test_mut_03_curated_isolation (tests.test_t007_schema.TestCanonicalSchemaModule)
AssertionError: 35 != 34 : MUT-03 FAILED: Mutating c1 contaminated subsequent get_curated_parquet_schema() calls!

======================================================================
FAIL: test_mut_04_cross_schema_independence (tests.test_t007_schema.TestCanonicalSchemaModule)
AssertionError: 36 != 35

----------------------------------------------------------------------
Ran 22 tests in 0.009s
FAILED (failures=4)
```

---

## 2. Regression Test Specifications & Post-Fix Results

After applying the Schema Factory pattern in `src/flight_pipeline/ingestion/schema.py`, all 22 tests in `tests/test_t007_schema.py` passed with 100% success.

### 2.1. Mutation Test Details

| Test Case | Identifier | Test Logic | Post-Fix Result |
| :--- | :--- | :--- | :---: |
| **Raw Business Isolation** | `MUT-01` | Calls `s1 = get_raw_business_schema()`, executes `s1.add("MUTANT_COL", StringType())`, then retrieves `s2 = get_raw_business_schema()`. Verifies `len(s2.fields) == 34` and `"MUTANT_COL" not in s2.names`. | **PASS** |
| **Raw Parser Isolation** | `MUT-02` | Calls `p1 = get_raw_parser_schema()`, executes `p1.add("CORRUPT_MUTANT", DoubleType())`, then retrieves `p2 = get_raw_parser_schema()`. Verifies `len(p2.fields) == 35` and `_corrupt_record` is strictly the last field. | **PASS** |
| **Curated Storage Isolation** | `MUT-03` | Calls `c1 = get_curated_parquet_schema()`, executes `c1.add("EXTRA_COL", LongType())`, then retrieves `c2 = get_curated_parquet_schema()`. Verifies `len(c2.fields) == 34`, types match canonical spec, and metadata is unaffected. | **PASS** |
| **Cross-Schema Independence** | `MUT-04` | Mutates a raw business schema instance. Verifies that `get_raw_parser_schema()` still has exactly 35 fields and `get_curated_parquet_schema()` still has exactly 34 fields. | **PASS** |
| **Repeatability & Immutability** | `MUT-05` | Generates multiple schema instances across repeated calls. Verifies JSON serialization identity (`s1.json() == s2.json()`), mutates an instance, and verifies subsequent instances reproduce the canonical JSON. | **PASS** |

### 2.2. Contract & Scope Test Details

| Test Case | Identifier | Test Logic | Result |
| :--- | :--- | :--- | :---: |
| **Exact 34-Column Snapshot** | `CONTRACT-01` | Compares the exact names and positions of all 34 fields against an independent hardcoded tuple `EXPECTED_PHYSICAL_COLUMNS`. Verifies count (34), set equality, and exact sequence. | **PASS** |
| **Scope & Module Isolation** | `CONTRACT-02` | Audits module namespace to verify zero imports or references to `csv`, `reader`, `classifier`, `publication`, `os.remove`, or file I/O operations. Confirms pure schema boundary. | **PASS** |

---

## 3. Targeted Test Execution Summary

```text
python -m unittest tests/test_t007_schema.py
......................
----------------------------------------------------------------------
Ran 22 tests in 0.011s

OK
```

All 22 tests passed in 0.011s with 0 errors, 0 failures, and 0 skips.
The verified defect of shared mutable schema state is permanently eliminated.
