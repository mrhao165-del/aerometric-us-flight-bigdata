"""
Canonical Schema Module for US Flight Performance Analysis (2016-2024).
Conforms to DATA_CONTRACT.md, DATA_DICTIONARY.md, and Gate G3 / T-006 agreements.

Pure schema definitions only:
- Exact 34 canonical raw business columns.
- StringType raw parsing schema boundary (prevents metric corruption from triggering record rejection).
- Technical _corrupt_record field (35th field in parser schema, separate from physical 34 columns).
- Curated strongly-typed storage schema preserving float64 OP_CARRIER_FL_NUM and nullable Int64 calendar fields.
- Strictly NO reader execution, classifier logic, or filesystem side effects.
"""

from typing import List, Tuple
from pyspark.sql.types import (
    StructType,
    StructField,
    StringType,
    DoubleType,
    LongType,
)

# -----------------------------------------------------------------------------
# 1. CANONICAL CONSTANTS & BOUNDARIES
# -----------------------------------------------------------------------------

CANONICAL_COLUMNS_COUNT: int = 34

CANONICAL_COLUMN_NAMES: Tuple[str, ...] = (
    "FL_DATE",
    "OP_CARRIER",
    "OP_CARRIER_FL_NUM",
    "ORIGIN",
    "DEST",
    "CRS_DEP_TIME",
    "DEP_TIME",
    "DEP_DELAY",
    "TAXI_OUT",
    "WHEELS_OFF",
    "WHEELS_ON",
    "TAXI_IN",
    "CRS_ARR_TIME",
    "ARR_TIME",
    "ARR_DELAY",
    "CRS_ELAPSED_TIME",
    "ACTUAL_ELAPSED_TIME",
    "AIR_TIME",
    "FLIGHTS",
    "MONTH",
    "DAY_OF_MONTH",
    "DAY_OF_WEEK",
    "ORIGIN_INDEX",
    "DEST_INDEX",
    "O_TEMP",
    "O_PRCP",
    "O_WSPD",
    "D_TEMP",
    "D_PRCP",
    "D_WSPD",
    "O_LATITUDE",
    "O_LONGITUDE",
    "D_LATITUDE",
    "D_LONGITUDE",
)

CORRUPT_RECORD_COLUMN: str = "_corrupt_record"

SEVEN_CORE_MEASURES: Tuple[str, ...] = (
    "ARR_DELAY",
    "DEP_DELAY",
    "TAXI_OUT",
    "TAXI_IN",
    "AIR_TIME",
    "ACTUAL_ELAPSED_TIME",
    "CRS_ELAPSED_TIME",
)

WEATHER_COLUMNS: Tuple[str, ...] = (
    "O_TEMP",
    "O_PRCP",
    "O_WSPD",
    "D_TEMP",
    "D_PRCP",
    "D_WSPD",
)

COORDINATE_COLUMNS: Tuple[str, ...] = (
    "O_LATITUDE",
    "O_LONGITUDE",
    "D_LATITUDE",
    "D_LONGITUDE",
)

CALENDAR_INT64_COLUMNS: Tuple[str, ...] = (
    "MONTH",
    "DAY_OF_MONTH",
    "DAY_OF_WEEK",
    "ORIGIN_INDEX",
    "DEST_INDEX",
)

FORBIDDEN_COLUMNS: Tuple[str, ...] = (
    "CANCELLED",
    "DIVERTED",
    "CANCELLATION_CODE",
    "DISTANCE",
    "DISTANCE_GROUP",
    "CARRIER_DELAY",
    "WEATHER_DELAY",
    "NAS_DELAY",
    "SECURITY_DELAY",
    "LATE_AIRCRAFT_DELAY",
)


# -----------------------------------------------------------------------------
# 2. RAW CSV PARSING SCHEMAS (BRONZE LAYER BOUNDARY - FACTORY IMPLEMENTATION)
# -----------------------------------------------------------------------------
# Raw ingestion parses all 34 business columns as StringType to prevent
# field-level cast anomalies (e.g. non-numeric delay strings) from triggering
# parser-level record rejection (_corrupt_record != null), protecting DC-12.


def _create_raw_business_fields() -> List[StructField]:
    """Factory creating isolated StructField instances for 34 business columns."""
    return [
        StructField(col_name, StringType(), nullable=True)
        for col_name in CANONICAL_COLUMN_NAMES
    ]


def _create_corrupt_record_field() -> StructField:
    """Factory creating isolated technical _corrupt_record field."""
    return StructField(
        CORRUPT_RECORD_COLUMN,
        StringType(),
        nullable=True,
        metadata={
            "description": "Internal technical field for PySpark Univocity parser corrupt lines",
            "is_physical_column": False,
        },
    )


# -----------------------------------------------------------------------------
# 3. CURATED STORAGE SCHEMA (SILVER LAYER BOUNDARY - FACTORY IMPLEMENTATION)
# -----------------------------------------------------------------------------
# Curated Parquet schema reflects the canonical DATA_DICTIONARY and T-006 decisions:
# - OP_CARRIER_FL_NUM: DoubleType (preserving float64 audited dtype without truncating cast)
# - FLIGHTS: DoubleType (strictly prohibited from KPI denominator weighting per FP-DEC-010)
# - MONTH, DAY_OF_MONTH, DAY_OF_WEEK: LongType (Int64 nullable)
# - 7 CORE measures: DoubleType (units: provisional under G2-EXC-001 / TS-018)
# - Weather: DoubleType (optional, conditional no-go under FP-DEC-017)
# - Date/Time strings: StringType (no rollover or timezone invention per FP-DEC-007)


def _create_curated_fields() -> List[StructField]:
    """Factory creating isolated StructField instances for 34 curated columns."""
    return [
        # Core Identifiers and Date/Time (Strings preserved per FP-DEC-007)
        StructField("FL_DATE", StringType(), nullable=True, metadata={"anchor": "FLIGHT_DATE"}),
        StructField("OP_CARRIER", StringType(), nullable=True, metadata={"anchor": "CARRIER"}),
        StructField(
            "OP_CARRIER_FL_NUM",
            DoubleType(),
            nullable=True,
            metadata={"raw_audited_dtype": "float64", "governance": "G3-COND-A"},
        ),
        StructField("ORIGIN", StringType(), nullable=True, metadata={"anchor": "ORIGIN_AIRPORT"}),
        StructField("DEST", StringType(), nullable=True, metadata={"anchor": "DEST_AIRPORT"}),
        StructField("CRS_DEP_TIME", StringType(), nullable=True, metadata={"temporal_policy": "NO_ROLLOVER"}),
        StructField("DEP_TIME", StringType(), nullable=True, metadata={"temporal_policy": "NO_ROLLOVER"}),

        # Performance Measures (Continuous Doubles, Resolved Units via TS-018 Option B)
        StructField("DEP_DELAY", DoubleType(), nullable=True, metadata={"unit_status": "RESOLVED_BY_TS018_APPROVED_OPTION_B"}),
        StructField("TAXI_OUT", DoubleType(), nullable=True, metadata={"unit_status": "RESOLVED_BY_TS018_APPROVED_OPTION_B"}),
        StructField("WHEELS_OFF", StringType(), nullable=True, metadata={"temporal_policy": "NO_ROLLOVER"}),
        StructField("WHEELS_ON", StringType(), nullable=True, metadata={"temporal_policy": "NO_ROLLOVER"}),
        StructField("TAXI_IN", DoubleType(), nullable=True, metadata={"unit_status": "RESOLVED_BY_TS018_APPROVED_OPTION_B"}),
        StructField("CRS_ARR_TIME", StringType(), nullable=True, metadata={"temporal_policy": "NO_ROLLOVER"}),
        StructField("ARR_TIME", StringType(), nullable=True, metadata={"temporal_policy": "NO_ROLLOVER"}),
        StructField("ARR_DELAY", DoubleType(), nullable=True, metadata={"unit_status": "RESOLVED_BY_TS018_APPROVED_OPTION_B"}),
        StructField("CRS_ELAPSED_TIME", DoubleType(), nullable=True, metadata={"unit_status": "RESOLVED_BY_TS018_APPROVED_OPTION_B"}),
        StructField("ACTUAL_ELAPSED_TIME", DoubleType(), nullable=True, metadata={"unit_status": "RESOLVED_BY_TS018_APPROVED_OPTION_B"}),
        StructField("AIR_TIME", DoubleType(), nullable=True, metadata={"unit_status": "RESOLVED_BY_TS018_APPROVED_OPTION_B"}),

        # Operational Count Flag (Preserved raw float64, prohibited as KPI weight)
        StructField(
            "FLIGHTS",
            DoubleType(),
            nullable=True,
            metadata={"raw_audited_dtype": "float64", "prohibited_use": "KPI_DENOMINATOR_WEIGHTING"},
        ),

        # Calendar and Index Fields (Int64 Nullable)
        StructField("MONTH", LongType(), nullable=True),
        StructField("DAY_OF_MONTH", LongType(), nullable=True),
        StructField("DAY_OF_WEEK", LongType(), nullable=True),
        StructField("ORIGIN_INDEX", LongType(), nullable=True),
        StructField("DEST_INDEX", LongType(), nullable=True),

        # Weather Fields (FP-DEC-017 CONDITIONAL_NO_GO, preserved as nullable DoubleType)
        StructField("O_TEMP", DoubleType(), nullable=True, metadata={"status": "CONDITIONAL_NO_GO"}),
        StructField("O_PRCP", DoubleType(), nullable=True, metadata={"status": "CONDITIONAL_NO_GO"}),
        StructField("O_WSPD", DoubleType(), nullable=True, metadata={"status": "CONDITIONAL_NO_GO"}),
        StructField("D_TEMP", DoubleType(), nullable=True, metadata={"status": "CONDITIONAL_NO_GO"}),
        StructField("D_PRCP", DoubleType(), nullable=True, metadata={"status": "CONDITIONAL_NO_GO"}),
        StructField("D_WSPD", DoubleType(), nullable=True, metadata={"status": "CONDITIONAL_NO_GO"}),

        # Geospatial Coordinates (Continuous DoubleType)
        StructField("O_LATITUDE", DoubleType(), nullable=True),
        StructField("O_LONGITUDE", DoubleType(), nullable=True),
        StructField("D_LATITUDE", DoubleType(), nullable=True),
        StructField("D_LONGITUDE", DoubleType(), nullable=True),
    ]


# -----------------------------------------------------------------------------
# 4. ACCESSOR & VALIDATION FUNCTIONS (SCHEMA FACTORIES & PURE LOGIC)
# -----------------------------------------------------------------------------

def get_canonical_column_names() -> List[str]:
    """Return a copy of the canonical 34 column names in physical order."""
    return list(CANONICAL_COLUMN_NAMES)


def get_raw_business_schema() -> StructType:
    """
    Construct and return a fresh, isolated 34-column StringType schema for raw CSV data.
    Each invocation generates newly instantiated StructField objects to prevent mutable
    in-place mutations from contaminating subsequent calls.
    """
    return StructType(_create_raw_business_fields())


def get_raw_parser_schema() -> StructType:
    """
    Construct and return a fresh, isolated 35-field PySpark DataFrameReader schema
    including _corrupt_record as the 35th field.
    Note: The 35th field is internal technical, not a physical column of BTS sources.
    """
    return StructType(_create_raw_business_fields() + [_create_corrupt_record_field()])


def get_curated_parquet_schema() -> StructType:
    """
    Construct and return a fresh, isolated 34-column strongly-typed curated storage schema.
    Each invocation generates newly instantiated StructField objects to ensure schema immutability.
    """
    return StructType(_create_curated_fields())


# -----------------------------------------------------------------------------
# 5. MODULE-LEVEL CONSTANTS (BACKWARDS COMPATIBILITY)
# -----------------------------------------------------------------------------
# Provided for backwards compatibility with existing callers importing constants directly.
# Getters above do NOT reference these constants, preventing mutations to constants
# from leaking into getter outputs.

RAW_CSV_BUSINESS_SCHEMA: StructType = get_raw_business_schema()
RAW_CSV_PARSER_SCHEMA: StructType = get_raw_parser_schema()
CURATED_PARQUET_SCHEMA: StructType = get_curated_parquet_schema()


def validate_column_names(column_names: List[str]) -> bool:
    """
    Validate whether a list of column names matches the 34 canonical columns
    in exact count, names, and physical order.
    """
    if not isinstance(column_names, (list, tuple)):
        return False
    return list(column_names) == list(CANONICAL_COLUMN_NAMES)
