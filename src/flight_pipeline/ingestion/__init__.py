"""
Ingestion package for US Flight Performance Analysis (2016-2024).
Provides canonical schema definitions, field mappings, and typing boundaries.
"""

from flight_pipeline.ingestion.schema import (
    CANONICAL_COLUMNS_COUNT,
    CANONICAL_COLUMN_NAMES,
    CORRUPT_RECORD_COLUMN,
    SEVEN_CORE_MEASURES,
    WEATHER_COLUMNS,
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

__all__ = [
    "CANONICAL_COLUMNS_COUNT",
    "CANONICAL_COLUMN_NAMES",
    "CORRUPT_RECORD_COLUMN",
    "SEVEN_CORE_MEASURES",
    "WEATHER_COLUMNS",
    "FORBIDDEN_COLUMNS",
    "RAW_CSV_BUSINESS_SCHEMA",
    "RAW_CSV_PARSER_SCHEMA",
    "CURATED_PARQUET_SCHEMA",
    "get_canonical_column_names",
    "get_raw_business_schema",
    "get_raw_parser_schema",
    "get_curated_parquet_schema",
    "validate_column_names",
]
