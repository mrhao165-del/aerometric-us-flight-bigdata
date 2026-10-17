"""
Raw CSV Reader and Ingestion Record Handling module.
Conforms to DATA_CONTRACT.md (DC-11, DC-12), ARCHITECTURE.md, and Gate G3 / T-006 / T-007 specifications.

Governance Invariants:
- DC-11: Three-state disjoint row accounting (N_raw = N_accepted + N_quarantined + N_rejected).
- DC-12: Separation of Ingest Acceptance and Metric Validity. Non-numeric delay does NOT reject or quarantine flight record.
- G3-COND-B: OP_CARRIER_FL_NUM <= 0 must NOT be hard-quarantined.
- FP-DEC-017: Weather columns optional, absence does not reject flight record.
- FP-DEC-010: FLIGHTS column preserved, never fabricated.
- Pure parsing and classification; no unapproved in-place dataset mutations.
"""

from dataclasses import dataclass, field
from enum import Enum
import os
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Tuple, Union

from pyspark.sql import DataFrame, SparkSession, functions as F
from pyspark.sql.types import (
    DoubleType,
    LongType,
    StringType,
    StructField,
    StructType,
)

from flight_pipeline.ingestion.schema import (
    CANONICAL_COLUMN_NAMES,
    CANONICAL_COLUMNS_COUNT,
    CORRUPT_RECORD_COLUMN,
    get_curated_parquet_schema,
    get_raw_parser_schema,
)
from flight_pipeline.utils.run_manifest import RowAccounting


class RecordStatus(str, Enum):
    """Mutually exclusive DC-11 record classification states."""
    ACCEPTED = "ACCEPTED"
    QUARANTINED = "QUARANTINED"
    REJECTED = "REJECTED"


class AnomalyReason(str, Enum):
    """Categorized root-cause reasons for non-accepted records."""
    NONE = "NONE"
    PARSER_SYNTAX_CORRUPTION = "PARSER_SYNTAX_CORRUPTION"
    MALFORMED_FL_DATE = "MALFORMED_FL_DATE"
    MISSING_MANDATORY_IDENTIFIER = "MISSING_MANDATORY_IDENTIFIER"


STATUS_COLUMN: str = "_record_status"
REASON_COLUMN: str = "_anomaly_reason"


@dataclass(frozen=True)
class CsvReadOptions:
    """Configuration options for PySpark DataFrameReader CSV ingestion."""
    header: bool = True
    mode: str = "PERMISSIVE"
    column_name_of_corrupt_record: str = CORRUPT_RECORD_COLUMN
    multi_line: bool = False
    quote: str = '"'
    escape: str = '"'
    empty_value: str = ""
    null_value: str = ""
    ignore_leading_white_space: bool = True
    ignore_trailing_white_space: bool = True
    enforce_schema: bool = True

    def to_spark_options(self) -> Dict[str, str]:
        """Convert options dataclass to PySpark DataFrameReader option dictionary."""
        return {
            "header": str(self.header).lower(),
            "mode": self.mode,
            "columnNameOfCorruptRecord": self.column_name_of_corrupt_record,
            "multiLine": str(self.multi_line).lower(),
            "quote": self.quote,
            "escape": self.escape,
            "emptyValue": self.empty_value,
            "nullValue": self.null_value,
            "ignoreLeadingWhiteSpace": str(self.ignore_leading_white_space).lower(),
            "ignoreTrailingWhiteSpace": str(self.ignore_trailing_white_space).lower(),
            "enforceSchema": str(self.enforce_schema).lower(),
        }


class RawCsvReader:
    """
    Production CSV Reader wrapping PySpark DataFrameReader.
    Enforces canonical 35-field parser schema (34 business columns + technical _corrupt_record).
    """

    def __init__(
        self,
        spark: SparkSession,
        options: Optional[CsvReadOptions] = None,
    ):
        if spark is None:
            raise ValueError("SparkSession cannot be None")
        self.spark = spark
        self.options = options or CsvReadOptions()

    def read_raw(self, source_path: Union[str, Path]) -> DataFrame:
        """
        Read raw CSV file using canonical parser schema.
        
        Args:
            source_path: Path to the raw CSV file on local or distributed filesystem.
            
        Returns:
            DataFrame with 34 business string columns plus technical _corrupt_record.
        """
        path_str = str(source_path)
        # Ensure column pruning is disabled so Univocity parser verifies all tokens
        # across the line and captures token count mismatches into _corrupt_record
        self.spark.conf.set("spark.sql.csv.parser.columnPruning.enabled", "false")
        reader = (
            self.spark.read
            .options(**self.options.to_spark_options())
            .schema(get_raw_parser_schema())
        )
        return reader.csv(path_str)


class IngestionRecordClassifier:
    """
    Classifies raw records into mutually exclusive ACCEPTED, QUARANTINED, and REJECTED states
    conforming to DATA_CONTRACT.md (DC-11 and DC-12).
    """

    @staticmethod
    def classify(df: DataFrame) -> DataFrame:
        """
        Augment DataFrame with `_record_status` and `_anomaly_reason` columns.
        
        Rules:
        1. REJECTED: _corrupt_record IS NOT NULL (Univocity parser syntax error).
        2. QUARANTINED: Mandatory temporal anchor FL_DATE is NULL or does not match YYYY-MM-DD format.
        3. ACCEPTED: All other records meeting structural format.
        
        Note:
        - Non-numeric or missing performance measures (DEP_DELAY, ARR_DELAY, etc.) do NOT
          quarantine or reject the flight record (DC-12).
        - OP_CARRIER_FL_NUM <= 0 is explicitly NOT hard-quarantined per G3-COND-B.
        - Absence of weather data does NOT quarantine or reject flight records per FP-DEC-017.
        """
        corrupt_col = F.col(CORRUPT_RECORD_COLUMN)
        fl_date_col = F.col("FL_DATE")

        # Condition 1: Technical unrecoverable parser corruption
        is_corrupt = corrupt_col.isNotNull()

        # Condition 2: Structural date format violation (mandatory temporal key)
        is_malformed_date = fl_date_col.isNull() | ~fl_date_col.rlike(r"^\d{4}-\d{2}-\d{2}$")

        classified_df = df.withColumn(
            STATUS_COLUMN,
            F.when(is_corrupt, F.lit(RecordStatus.REJECTED.value))
            .when(is_malformed_date, F.lit(RecordStatus.QUARANTINED.value))
            .otherwise(F.lit(RecordStatus.ACCEPTED.value)),
        ).withColumn(
            REASON_COLUMN,
            F.when(is_corrupt, F.lit(AnomalyReason.PARSER_SYNTAX_CORRUPTION.value))
            .when(is_malformed_date, F.lit(AnomalyReason.MALFORMED_FL_DATE.value))
            .otherwise(F.lit(AnomalyReason.NONE.value)),
        )

        return classified_df


class IngestionTransformer:
    """
    Transforms accepted raw StringType records into strongly-typed curated schema
    ready for Parquet serialization.
    """

    @staticmethod
    def to_curated(df: DataFrame, filter_accepted: bool = True) -> DataFrame:
        """
        Cast canonical columns to curated Parquet schema types.
        
        Args:
            df: Classified or raw DataFrame containing canonical columns.
            filter_accepted: If True, filters out REJECTED and QUARANTINED records before casting.
            
        Returns:
            DataFrame matching exact 34 canonical columns and types of CURATED_PARQUET_SCHEMA.
        """
        working_df = df
        if filter_accepted and STATUS_COLUMN in df.columns:
            working_df = working_df.filter(F.col(STATUS_COLUMN) == RecordStatus.ACCEPTED.value)

        curated_schema = get_curated_parquet_schema()
        type_map = {field.name: field.dataType for field in curated_schema.fields}

        select_exprs = []
        for col_name in CANONICAL_COLUMN_NAMES:
            target_type = type_map[col_name]
            if target_type == StringType():
                select_exprs.append(F.col(col_name).cast(StringType()).alias(col_name))
            else:
                # Use try_cast to tolerate malformed strings and return NULL per DC-12
                # (Prevents Spark 4.0 CAST_INVALID_INPUT NumberFormatException)
                select_exprs.append(
                    F.expr(f"try_cast({col_name} AS {target_type.simpleString()})").alias(col_name)
                )

        return working_df.select(select_exprs)


def compute_row_accounting(classified_df: DataFrame) -> RowAccounting:
    """
    Compute DC-11 row accounting from classified DataFrame.
    
    Returns:
        RowAccounting instance verifying N_raw = N_accepted + N_quarantined + N_rejected.
    """
    status_counts_df = (
        classified_df
        .groupBy(STATUS_COLUMN)
        .agg(F.count(F.lit(1)).alias("count"))
    )
    
    status_counts = {row[STATUS_COLUMN]: row["count"] for row in status_counts_df.collect()}

    accepted = status_counts.get(RecordStatus.ACCEPTED.value, 0)
    quarantined = status_counts.get(RecordStatus.QUARANTINED.value, 0)
    rejected = status_counts.get(RecordStatus.REJECTED.value, 0)
    raw_total = accepted + quarantined + rejected

    accounting = RowAccounting(
        raw_row_count=raw_total,
        accepted_row_count=accepted,
        quarantined_row_count=quarantined,
        rejected_row_count=rejected,
    )

    if not accounting.is_balanced():
        raise ValueError(
            f"Row accounting invariant violated: raw ({raw_total}) != "
            f"accepted ({accepted}) + quarantined ({quarantined}) + rejected ({rejected})"
        )

    return accounting
