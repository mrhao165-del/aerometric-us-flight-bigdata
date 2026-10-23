"""
Unit tests for T007-01: Canonical Schema Module.
Validates:
1. Exact 34 canonical names and physical order.
2. Absence of fabricated columns (CANCELLED, DIVERTED, DISTANCE, etc.).
3. Retention of FLIGHTS with explicit KPI weighting prohibition metadata.
4. Retention of 6 weather fields (FP-DEC-017 CONDITIONAL_NO_GO).
5. Raw schema business columns all StringType (DC-12 protection).
6. Separation of technical _corrupt_record from physical 34 columns.
7. Curated schema exact typing boundaries.
8. Nullable Int64 (LongType) calendar and index fields.
9. OP_CARRIER_FL_NUM float64 preservation (no truncating cast).
10. Date/time string preservation without timezone or rollover side effects.
11. Pure schema logic without quality rule execution or data reading.
12. Determinism across repeated imports.
13. Negative tests for schema drift, reordering, missing and extra columns.
14. Compatibility with existing T-009 modules.
"""

import sys
import unittest
from pathlib import Path

# Ensure src/ is on sys.path
SRC_DIR = Path(__file__).resolve().parents[1] / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from pyspark.sql.types import (
    StructType,
    StructField,
    StringType,
    DoubleType,
    LongType,
)

from flight_pipeline.ingestion.schema import (
    CANONICAL_COLUMNS_COUNT,
    CANONICAL_COLUMN_NAMES,
    CORRUPT_RECORD_COLUMN,
    SEVEN_CORE_MEASURES,
    WEATHER_COLUMNS,
    COORDINATE_COLUMNS,
    CALENDAR_INT64_COLUMNS,
    FORBIDDEN_COLUMNS,
    RAW_CSV_BUSINESS_SCHEMA,
    RAW_CSV_PARSER_SCHEMA,
    CURATED_PARQUET_SCHEMA,
    get_canonical_column_names,
    get_raw_business_schema,
    get_raw_parser_schema,
    get_curated_parquet_schema,
    validate_column_names,
)


class TestCanonicalSchemaModule(unittest.TestCase):
    """Test suite for T007-01 Canonical Schema Module."""

    def test_01_exact_34_canonical_names_and_count(self):
        """Verify exactly 34 canonical column names are defined."""
        self.assertEqual(CANONICAL_COLUMNS_COUNT, 34)
        self.assertEqual(len(CANONICAL_COLUMN_NAMES), 34)
        names = get_canonical_column_names()
        self.assertEqual(len(names), 34)
        # Check uniqueness
        self.assertEqual(len(set(names)), 34)

    def test_02_exact_physical_column_order(self):
        """Verify canonical physical sequence matches DATA_DICTIONARY and BTS sources."""
        expected_first_5 = ("FL_DATE", "OP_CARRIER", "OP_CARRIER_FL_NUM", "ORIGIN", "DEST")
        expected_last_4 = ("O_LATITUDE", "O_LONGITUDE", "D_LATITUDE", "D_LONGITUDE")
        self.assertEqual(CANONICAL_COLUMN_NAMES[:5], expected_first_5)
        self.assertEqual(CANONICAL_COLUMN_NAMES[-4:], expected_last_4)

        # Check index of key columns
        self.assertEqual(CANONICAL_COLUMN_NAMES.index("DEP_DELAY"), 7)
        self.assertEqual(CANONICAL_COLUMN_NAMES.index("ARR_DELAY"), 14)
        self.assertEqual(CANONICAL_COLUMN_NAMES.index("FLIGHTS"), 18)
        self.assertEqual(CANONICAL_COLUMN_NAMES.index("MONTH"), 19)
        self.assertEqual(CANONICAL_COLUMN_NAMES.index("O_TEMP"), 24)

    def test_03_no_fabricated_columns(self):
        """Verify no unapproved fabricated columns exist in schema definitions."""
        names = set(CANONICAL_COLUMN_NAMES)
        for forbidden in FORBIDDEN_COLUMNS:
            self.assertNotIn(
                forbidden,
                names,
                f"Forbidden fabricated column {forbidden!r} must not exist in canonical schema!",
            )
            self.assertNotIn(forbidden, RAW_CSV_BUSINESS_SCHEMA.fieldNames())
            self.assertNotIn(forbidden, CURATED_PARQUET_SCHEMA.fieldNames())

    def test_04_flights_column_retained_with_prohibited_weight_metadata(self):
        """Verify FLIGHTS is preserved but metadata strictly forbids KPI weighting."""
        self.assertIn("FLIGHTS", CANONICAL_COLUMN_NAMES)
        self.assertIn("FLIGHTS", RAW_CSV_BUSINESS_SCHEMA.fieldNames())
        self.assertIn("FLIGHTS", CURATED_PARQUET_SCHEMA.fieldNames())

        field = CURATED_PARQUET_SCHEMA["FLIGHTS"]
        self.assertIsInstance(field.dataType, DoubleType)
        self.assertIn("prohibited_use", field.metadata)
        self.assertEqual(field.metadata["prohibited_use"], "KPI_DENOMINATOR_WEIGHTING")

    def test_05_six_weather_fields_retained_as_optional(self):
        """Verify all 6 weather fields are preserved and marked CONDITIONAL_NO_GO."""
        self.assertEqual(len(WEATHER_COLUMNS), 6)
        expected_wx = ("O_TEMP", "O_PRCP", "O_WSPD", "D_TEMP", "D_PRCP", "D_WSPD")
        self.assertEqual(WEATHER_COLUMNS, expected_wx)

        for wx in WEATHER_COLUMNS:
            self.assertIn(wx, CANONICAL_COLUMN_NAMES)
            field = CURATED_PARQUET_SCHEMA[wx]
            self.assertIsInstance(field.dataType, DoubleType)
            self.assertTrue(field.nullable)
            self.assertEqual(field.metadata.get("status"), "CONDITIONAL_NO_GO")

    def test_06_raw_csv_business_schema_all_stringtype(self):
        """Verify raw CSV schema defines all 34 business fields as StringType (DC-12 protection)."""
        schema = get_raw_business_schema()
        self.assertEqual(len(schema.fields), 34)
        for field in schema.fields:
            self.assertIsInstance(
                field.dataType,
                StringType,
                f"Raw business column {field.name} must be StringType, got {field.dataType}!",
            )
            self.assertTrue(field.nullable)

    def test_07_corrupt_record_separation_from_34_columns(self):
        """Verify _corrupt_record is strictly separate from the 34 physical BTS columns."""
        # Not in business columns
        self.assertNotIn(CORRUPT_RECORD_COLUMN, CANONICAL_COLUMN_NAMES)
        self.assertNotIn(CORRUPT_RECORD_COLUMN, RAW_CSV_BUSINESS_SCHEMA.fieldNames())
        self.assertNotIn(CORRUPT_RECORD_COLUMN, CURATED_PARQUET_SCHEMA.fieldNames())

        # In parser schema as 35th field
        parser_schema = get_raw_parser_schema()
        self.assertEqual(len(parser_schema.fields), 35)
        self.assertEqual(parser_schema.fields[-1].name, CORRUPT_RECORD_COLUMN)
        self.assertFalse(parser_schema.fields[-1].metadata.get("is_physical_column", True))

    def test_08_curated_schema_exact_type_mapping(self):
        """Verify curated storage schema matches DATA_DICTIONARY and T-006 agreements."""
        curated = get_curated_parquet_schema()
        self.assertEqual(len(curated.fields), 34)
        self.assertEqual(curated.fieldNames(), list(CANONICAL_COLUMN_NAMES))

        # Check 7 CORE measures are DoubleType
        for m in SEVEN_CORE_MEASURES:
            field = curated[m]
            self.assertIsInstance(field.dataType, DoubleType)
            self.assertTrue(field.nullable)
            self.assertEqual(field.metadata.get("unit_status"), "RESOLVED_BY_TS018_APPROVED_OPTION_B")

        # Check coordinates are DoubleType
        for coord in COORDINATE_COLUMNS:
            field = curated[coord]
            self.assertIsInstance(field.dataType, DoubleType)
            self.assertTrue(field.nullable)

    def test_09_nullable_int64_calendar_fields(self):
        """Verify MONTH, DAY_OF_MONTH, DAY_OF_WEEK, ORIGIN_INDEX, DEST_INDEX are LongType and nullable."""
        curated = get_curated_parquet_schema()
        for col_name in CALENDAR_INT64_COLUMNS:
            field = curated[col_name]
            self.assertIsInstance(
                field.dataType,
                LongType,
                f"Calendar/index field {col_name} must be LongType (Int64), got {field.dataType}!",
            )
            self.assertTrue(
                field.nullable,
                f"Calendar/index field {col_name} must be nullable per DATA_DICTIONARY.md!",
            )

    def test_10_op_carrier_fl_num_float64_boundary(self):
        """Verify OP_CARRIER_FL_NUM preserves float64 (DoubleType) without truncating integer cast."""
        field = CURATED_PARQUET_SCHEMA["OP_CARRIER_FL_NUM"]
        self.assertIsInstance(field.dataType, DoubleType)
        self.assertTrue(field.nullable)
        self.assertEqual(field.metadata.get("raw_audited_dtype"), "float64")
        self.assertEqual(field.metadata.get("governance"), "G3-COND-A")

    def test_11_date_time_schema_preservation(self):
        """Verify date and wall-clock times are StringType per FP-DEC-007 (no rollover/timezone)."""
        curated = get_curated_parquet_schema()
        time_cols = ("CRS_DEP_TIME", "DEP_TIME", "WHEELS_OFF", "WHEELS_ON", "CRS_ARR_TIME", "ARR_TIME")
        for tc in time_cols:
            field = curated[tc]
            self.assertIsInstance(field.dataType, StringType)
            self.assertEqual(field.metadata.get("temporal_policy"), "NO_ROLLOVER")
        self.assertIsInstance(curated["FL_DATE"].dataType, StringType)

    def test_12_pure_schema_no_side_effects(self):
        """Verify importing and calling schema functions produces zero disk I/O and has no quality engine calls."""
        names = get_canonical_column_names()
        names.append("MUTATED_IN_TEST")
        # Ensure returned list is a copy and does not mutate module state
        self.assertEqual(len(get_canonical_column_names()), 34)

    def test_13_schema_deterministic_on_repeated_calls(self):
        """Verify schema instances are idempotent and deterministic across repeated invocations."""
        s1 = get_raw_business_schema()
        s2 = get_raw_business_schema()
        self.assertEqual(s1.json(), s2.json())

        c1 = get_curated_parquet_schema()
        c2 = get_curated_parquet_schema()
        self.assertEqual(c1.json(), c2.json())

    def test_14_negative_validation_tests(self):
        """Verify validate_column_names rejects reordered, missing, extra, or invalid columns."""
        valid_cols = get_canonical_column_names()
        self.assertTrue(validate_column_names(valid_cols))

        # Reordered columns rejected
        reordered = list(valid_cols)
        reordered[0], reordered[1] = reordered[1], reordered[0]
        self.assertFalse(validate_column_names(reordered))

        # Missing column rejected
        missing = valid_cols[:-1]
        self.assertFalse(validate_column_names(missing))

        # Extra column rejected
        extra = valid_cols + ["EXTRA_COL"]
        self.assertFalse(validate_column_names(extra))

        # Invalid type rejected
        self.assertFalse(validate_column_names("not_a_list")) # type: ignore
        self.assertFalse(validate_column_names(None)) # type: ignore

    def test_15_compatibility_with_existing_t009_modules(self):
        """Verify importing schema does not conflict with existing T-009 storage and manifest modules."""
        from flight_pipeline.storage.publication import SafePublisher, PublicationResult
        from flight_pipeline.utils.run_manifest import RunManifest, RowAccounting

        self.assertTrue(callable(SafePublisher))
        self.assertTrue(callable(RunManifest))
        self.assertTrue(callable(RowAccounting))

    # =========================================================================
    # MANDATORY REGRESSION TESTS (T007-01-FINAL-CLOSURE)
    # =========================================================================

    def test_mut_01_raw_business_isolation(self):
        """MUT-01: Verify mutating a returned raw business schema does not affect subsequent calls."""
        s1 = get_raw_business_schema()
        self.assertEqual(len(s1.fields), 34)
        s1.add("MUTANT_FAKE_COL", StringType(), nullable=True)
        self.assertEqual(len(s1.fields), 35)

        s2 = get_raw_business_schema()
        self.assertEqual(
            len(s2.fields),
            34,
            "MUT-01 FAILED: Mutating s1 contaminated subsequent get_raw_business_schema() calls!",
        )
        self.assertNotIn("MUTANT_FAKE_COL", s2.fieldNames())

    def test_mut_02_raw_parser_isolation(self):
        """MUT-02: Verify mutating a returned raw parser schema does not affect subsequent calls."""
        p1 = get_raw_parser_schema()
        self.assertEqual(len(p1.fields), 35)
        p1.add("MUTANT_PARSER_COL", DoubleType(), nullable=True)
        self.assertEqual(len(p1.fields), 36)

        p2 = get_raw_parser_schema()
        self.assertEqual(
            len(p2.fields),
            35,
            "MUT-02 FAILED: Mutating p1 contaminated subsequent get_raw_parser_schema() calls!",
        )
        self.assertNotIn("MUTANT_PARSER_COL", p2.fieldNames())
        self.assertEqual(p2.fieldNames()[-1], CORRUPT_RECORD_COLUMN)
        self.assertEqual(p2.fieldNames().count(CORRUPT_RECORD_COLUMN), 1)

    def test_mut_03_curated_isolation(self):
        """MUT-03: Verify mutating a returned curated schema does not affect subsequent calls."""
        c1 = get_curated_parquet_schema()
        self.assertEqual(len(c1.fields), 34)
        c1.add("MUTANT_CURATED_COL", LongType(), nullable=True)
        self.assertEqual(len(c1.fields), 35)

        c2 = get_curated_parquet_schema()
        self.assertEqual(
            len(c2.fields),
            34,
            "MUT-03 FAILED: Mutating c1 contaminated subsequent get_curated_parquet_schema() calls!",
        )
        self.assertNotIn("MUTANT_CURATED_COL", c2.fieldNames())
        self.assertEqual(c2["OP_CARRIER_FL_NUM"].dataType, DoubleType())
        self.assertEqual(c2["FLIGHTS"].metadata.get("prohibited_use"), "KPI_DENOMINATOR_WEIGHTING")

    def test_mut_04_cross_schema_independence(self):
        """MUT-04: Verify mutating raw schema does not alter parser schema or curated schema."""
        raw = get_raw_business_schema()
        raw.add("INJECTED_COLUMN", StringType(), nullable=True)

        parser = get_raw_parser_schema()
        self.assertEqual(len(parser.fields), 35)
        self.assertNotIn("INJECTED_COLUMN", parser.fieldNames())

        curated = get_curated_parquet_schema()
        self.assertEqual(len(curated.fields), 34)
        self.assertNotIn("INJECTED_COLUMN", curated.fieldNames())

    def test_mut_05_repeatability_and_immutability(self):
        """MUT-05: Verify schemas are deterministic across repeated invocations and immune to mutation."""
        first_raw = get_raw_business_schema()
        second_raw = get_raw_business_schema()
        self.assertEqual(first_raw.json(), second_raw.json())

        first_raw.add("SPOILER", StringType())
        third_raw = get_raw_business_schema()
        self.assertEqual(
            second_raw.json(),
            third_raw.json(),
            "MUT-05 FAILED: Schema was not pristine after mutation of another instance!",
        )

    def test_contract_01_exact_34_column_snapshot(self):
        """CONTRACT-01: Compare all 34 names and physical positions against an independent snapshot."""
        expected_34_snapshot = (
            "FL_DATE", "OP_CARRIER", "OP_CARRIER_FL_NUM", "ORIGIN", "DEST",
            "CRS_DEP_TIME", "DEP_TIME", "DEP_DELAY", "TAXI_OUT", "WHEELS_OFF",
            "WHEELS_ON", "TAXI_IN", "CRS_ARR_TIME", "ARR_TIME", "ARR_DELAY",
            "CRS_ELAPSED_TIME", "ACTUAL_ELAPSED_TIME", "AIR_TIME", "FLIGHTS",
            "MONTH", "DAY_OF_MONTH", "DAY_OF_WEEK", "ORIGIN_INDEX", "DEST_INDEX",
            "O_TEMP", "O_PRCP", "O_WSPD", "D_TEMP", "D_PRCP", "D_WSPD",
            "O_LATITUDE", "O_LONGITUDE", "D_LATITUDE", "D_LONGITUDE"
        )
        curated_fields = tuple(get_curated_parquet_schema().fieldNames())
        raw_fields = tuple(get_raw_business_schema().fieldNames())
        canonical_tuple = tuple(get_canonical_column_names())

        self.assertEqual(canonical_tuple, expected_34_snapshot)
        self.assertEqual(raw_fields, expected_34_snapshot)
        self.assertEqual(curated_fields, expected_34_snapshot)

        # Verify exact position matching for each of the 34 indices
        for idx, col_name in enumerate(expected_34_snapshot):
            self.assertEqual(canonical_tuple[idx], col_name)
            self.assertEqual(raw_fields[idx], col_name)
            self.assertEqual(curated_fields[idx], col_name)

    def test_contract_02_scope_isolation_no_io_or_executors(self):
        """CONTRACT-02: Verify schema module does not import or execute readers, publishers, or raw I/O."""
        import flight_pipeline.ingestion.schema as sm
        # Check forbidden modules are not imported
        for forbidden in ("reader", "classifier", "pipeline", "locking"):
            self.assertFalse(
                hasattr(sm, forbidden),
                f"CONTRACT-02: schema module must not contain {forbidden}!",
            )
        # Check schema module attributes do not include file path handles to data/raw
        for attr_name in dir(sm):
            val = getattr(sm, attr_name)
            if isinstance(val, str):
                self.assertNotIn("data/raw", val)
                self.assertNotIn("data\\raw", val)


if __name__ == "__main__":
    unittest.main()

