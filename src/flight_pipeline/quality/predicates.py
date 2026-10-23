"""
Numeric validation predicates for PySpark DataFrames.
Conforms to ARCHITECTURE.md, T006_FINAL_CORRECTIONS_ADDENDUM.md Section 3 (FIX-02),
and DC-12 submetric validity specifications.
Guarantees complete protection against NULL, NaN, +Infinity, and -Infinity values.
Safely handles both raw StringType and curated DoubleType inputs under Spark ANSI mode.
"""

from typing import Union
from pyspark.sql import Column, functions as F
from pyspark.sql.types import DoubleType


def _resolve_col(col_or_name: Union[str, Column]) -> Column:
    """Helper to convert column name string to Column object if needed."""
    if isinstance(col_or_name, str):
        return F.col(col_or_name)
    return col_or_name


def _resolve_numeric_col(col_or_name: Union[str, Column]) -> Column:
    """
    Helper to convert column name or Column object to a safe double Column.
    Uses try_cast(DoubleType()) to ensure resilience against malformed strings
    and prevents NumberFormatException when spark.sql.ansi.enabled is True.
    """
    c = _resolve_col(col_or_name)
    return c.try_cast(DoubleType())


def is_finite_numeric(col_or_name: Union[str, Column]) -> Column:
    """
    Complete finite numeric predicate safe across all Spark versions and Catalyst optimizers.
    Returns True iff the column is NOT NULL, NOT NaN, and NOT +/- Infinity.
    Safely handles both raw StringType and curated DoubleType inputs under Spark ANSI mode.
    
    Formula from T006_FINAL_CORRECTIONS_ADDENDUM.md:
    c.isNotNull() & ~F.isnan(c) & ~c.isin(float('inf'), float('-inf'))
    """
    c = _resolve_numeric_col(col_or_name)
    return c.isNotNull() & ~F.isnan(c) & ~c.isin(float("inf"), float("-inf"))


def is_valid_arr_delay(col_or_name: Union[str, Column] = "ARR_DELAY") -> Column:
    """
    Metric validity predicate for ARR_DELAY (KPI-02, KPI-03, KPI-06).
    Preserves negative signed delay values (early arrivals); strictly excludes null, NaN, and +/- Inf.
    """
    return is_finite_numeric(col_or_name)


def is_valid_dep_delay(col_or_name: Union[str, Column] = "DEP_DELAY") -> Column:
    """
    Metric validity predicate for DEP_DELAY (KPI-04, KPI-05).
    Preserves negative signed delay values (early departures); strictly excludes null, NaN, and +/- Inf.
    """
    return is_finite_numeric(col_or_name)


def is_valid_taxi_out(col_or_name: Union[str, Column] = "TAXI_OUT") -> Column:
    """
    Metric validity predicate for TAXI_OUT (KPI-07 Sub 7a).
    Domain requirement: finite numeric and non-negative (TAXI_OUT >= 0.0).
    """
    c = _resolve_numeric_col(col_or_name)
    return is_finite_numeric(c) & F.coalesce(c >= 0.0, F.lit(False))


def is_valid_taxi_in(col_or_name: Union[str, Column] = "TAXI_IN") -> Column:
    """
    Metric validity predicate for TAXI_IN (KPI-07 Sub 7b).
    Domain requirement: finite numeric and non-negative (TAXI_IN >= 0.0).
    """
    c = _resolve_numeric_col(col_or_name)
    return is_finite_numeric(c) & F.coalesce(c >= 0.0, F.lit(False))


def is_valid_air_time(col_or_name: Union[str, Column] = "AIR_TIME") -> Column:
    """
    Metric validity predicate for AIR_TIME (KPI-08 Sub 8a).
    Domain requirement: finite numeric and strictly positive (AIR_TIME > 0.0).
    """
    c = _resolve_numeric_col(col_or_name)
    return is_finite_numeric(c) & F.coalesce(c > 0.0, F.lit(False))


def is_valid_actual_elapsed_time(col_or_name: Union[str, Column] = "ACTUAL_ELAPSED_TIME") -> Column:
    """
    Metric validity predicate for ACTUAL_ELAPSED_TIME (KPI-08 Sub 8b).
    Domain requirement: finite numeric and strictly positive (ACTUAL_ELAPSED_TIME > 0.0).
    """
    c = _resolve_numeric_col(col_or_name)
    return is_finite_numeric(c) & F.coalesce(c > 0.0, F.lit(False))


def is_valid_crs_elapsed_time(col_or_name: Union[str, Column] = "CRS_ELAPSED_TIME") -> Column:
    """
    Metric validity predicate for CRS_ELAPSED_TIME (KPI-08 Sub 8c).
    Domain requirement: finite numeric and strictly positive (CRS_ELAPSED_TIME > 0.0).
    """
    c = _resolve_numeric_col(col_or_name)
    return is_finite_numeric(c) & F.coalesce(c > 0.0, F.lit(False))
