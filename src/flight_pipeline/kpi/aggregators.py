"""
PySpark expression builders for KPI aggregations, GK-sketch quantiles, and min-N evaluation.
Conforms to KPI_SPEC.md, DECISIONS.md (FP-DEC-008, FP-DEC-011, FP-DEC-015, FP-DEC-016),
and predicates in quality/predicates.py.
"""

from typing import Union, Optional
from pyspark.sql import Column, functions as F
from pyspark.sql.types import DoubleType, LongType

try:
    from flight_pipeline.quality.predicates import (
        is_valid_arr_delay,
        is_valid_dep_delay,
        is_valid_taxi_out,
        is_valid_taxi_in,
        is_valid_air_time,
        is_valid_actual_elapsed_time,
        is_valid_crs_elapsed_time,
    )
    from flight_pipeline.kpi.catalog import (
        MIN_N_CARRIER_YEAR,
        MIN_N_AIRPORT_YEAR,
        MIN_N_ROUTE_YEAR,
        MIN_N_STATUS_SUPPRESSED,
        MIN_N_STATUS_LOW_SAMPLE_CAUTION,
        MIN_N_STATUS_SUFFICIENT,
        MIN_N_STATUS_NOT_APPLICABLE,
        PERCENTILE_APPROX_ACCURACY,
    )
except ModuleNotFoundError:
    from src.flight_pipeline.quality.predicates import (
        is_valid_arr_delay,
        is_valid_dep_delay,
        is_valid_taxi_out,
        is_valid_taxi_in,
        is_valid_air_time,
        is_valid_actual_elapsed_time,
        is_valid_crs_elapsed_time,
    )
    from src.flight_pipeline.kpi.catalog import (
        MIN_N_CARRIER_YEAR,
        MIN_N_AIRPORT_YEAR,
        MIN_N_ROUTE_YEAR,
        MIN_N_STATUS_SUPPRESSED,
        MIN_N_STATUS_LOW_SAMPLE_CAUTION,
        MIN_N_STATUS_SUFFICIENT,
        MIN_N_STATUS_NOT_APPLICABLE,
        PERCENTILE_APPROX_ACCURACY,
    )


def get_metric_valid_predicate(field_name: Optional[str]) -> Column:
    """Return the canonical metric-valid boolean predicate for a given field."""
    if field_name is None:
        return F.lit(True)
    mapping = {
        "ARR_DELAY": is_valid_arr_delay("ARR_DELAY"),
        "DEP_DELAY": is_valid_dep_delay("DEP_DELAY"),
        "TAXI_OUT": is_valid_taxi_out("TAXI_OUT"),
        "TAXI_IN": is_valid_taxi_in("TAXI_IN"),
        "AIR_TIME": is_valid_air_time("AIR_TIME"),
        "ACTUAL_ELAPSED_TIME": is_valid_actual_elapsed_time("ACTUAL_ELAPSED_TIME"),
        "CRS_ELAPSED_TIME": is_valid_crs_elapsed_time("CRS_ELAPSED_TIME"),
    }
    if field_name not in mapping:
        raise ValueError(f"Unknown metric field for validation predicate: {field_name}")
    return mapping[field_name]


def evaluate_min_n(valid_count_col: Column, dimension_type: str) -> Column:
    """
    Evaluate min-N threshold status on count_metric_valid per FP-DEC-016:
    - carrier-year: min-N = 1000
    - airport-year: min-N = 365
    - route-year: min-N = 100
    Labels:
    - SUPPRESSED: count_metric_valid < min_n
    - LOW_SAMPLE_CAUTION: min_n <= count_metric_valid < 3 * min_n
    - SUFFICIENT: count_metric_valid >= 3 * min_n
    - NOT_APPLICABLE: other grouping dimensions
    """
    dim = dimension_type.lower().strip()
    if dim in ("carrier-year", "carrier_year"):
        min_n = MIN_N_CARRIER_YEAR
    elif dim in (
        "airport-year", "airport_year",
        "origin-year", "origin_year",
        "dest-year", "dest_year",
        "destination-year", "destination_year",
    ):
        min_n = MIN_N_AIRPORT_YEAR
    elif dim in ("route-year", "route_year", "pair-year", "pair_year"):
        min_n = MIN_N_ROUTE_YEAR
    else:
        return F.lit(MIN_N_STATUS_NOT_APPLICABLE)

    safe_count = F.coalesce(valid_count_col, F.lit(0))

    return (
        F.when(safe_count < min_n, F.lit(MIN_N_STATUS_SUPPRESSED))
        .when(safe_count < 3 * min_n, F.lit(MIN_N_STATUS_LOW_SAMPLE_CAUTION))
        .otherwise(F.lit(MIN_N_STATUS_SUFFICIENT))
    )
