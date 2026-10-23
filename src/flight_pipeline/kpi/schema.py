"""
PySpark schema definition for standardized 17-field KPI output tables.
Conforms to KPI_SPEC.md, DATA_CONTRACT.md (DC-11, DC-12), and Master Prompt Section 6.2.
"""

from pyspark.sql.types import (
    StructType,
    StructField,
    StringType,
    LongType,
    DoubleType,
)


KPI_OUTPUT_SCHEMA = StructType([
    StructField("kpi_id", StringType(), False),
    StructField("submetric", StringType(), True),
    StructField("run_id", StringType(), False),
    StructField("kpi_version", StringType(), False),
    StructField("source_year", StringType(), False),
    StructField("group_dimensions", StringType(), False),
    StructField("filter_definition", StringType(), False),
    StructField("count_records", LongType(), False),
    StructField("count_metric_valid", LongType(), False),
    StructField("excluded_count", LongType(), False),
    StructField("metric_valid_rate", DoubleType(), True),
    StructField("source_coverage_status", StringType(), False),
    StructField("value", DoubleType(), True),
    StructField("unit_status", StringType(), False),
    StructField("min_n_status", StringType(), False),
    StructField("quality_version", StringType(), False),
    StructField("provenance_reference", StringType(), False),
])
