"""
KPI calculation and metric validation package for US Flight Performance Analysis.
Conforms to KPI_SPEC.md, DATA_CONTRACT.md, and DECISIONS.md.
"""

from src.flight_pipeline.kpi.catalog import (
    KPI_VERSION,
    QUALITY_VERSION,
    UNIT_STATUS_PROVISIONAL,
    UNIT_STATUS_RESOLVED,
    UNIT_STATUS_ZERO_DENOMINATOR,
    COVERAGE_PARTIAL,
    COVERAGE_VERIFIED_WITH_SCOPE,
    COVERAGE_UNKNOWN,
    MIN_N_CARRIER_YEAR,
    MIN_N_AIRPORT_YEAR,
    MIN_N_ROUTE_YEAR,
    MIN_N_STATUS_SUPPRESSED,
    MIN_N_STATUS_LOW_SAMPLE_CAUTION,
    MIN_N_STATUS_SUFFICIENT,
    MIN_N_STATUS_NOT_APPLICABLE,
    PERCENTILE_APPROX_ACCURACY,
    CORE_KPI_DEFINITIONS,
    KPI_OUTPUT_COLUMNS,
)
from src.flight_pipeline.kpi.aggregators import evaluate_min_n
from src.flight_pipeline.kpi.schema import KPI_OUTPUT_SCHEMA
from src.flight_pipeline.kpi.calculator import KpiCalculator

__all__ = [
    "KPI_VERSION",
    "QUALITY_VERSION",
    "UNIT_STATUS_PROVISIONAL",
    "UNIT_STATUS_RESOLVED",
    "UNIT_STATUS_ZERO_DENOMINATOR",
    "COVERAGE_PARTIAL",
    "COVERAGE_VERIFIED_WITH_SCOPE",
    "COVERAGE_UNKNOWN",
    "MIN_N_CARRIER_YEAR",
    "MIN_N_AIRPORT_YEAR",
    "MIN_N_ROUTE_YEAR",
    "MIN_N_STATUS_SUPPRESSED",
    "MIN_N_STATUS_LOW_SAMPLE_CAUTION",
    "MIN_N_STATUS_SUFFICIENT",
    "MIN_N_STATUS_NOT_APPLICABLE",
    "PERCENTILE_APPROX_ACCURACY",
    "CORE_KPI_DEFINITIONS",
    "KPI_OUTPUT_COLUMNS",
    "KPI_OUTPUT_SCHEMA",
    "KpiCalculator",
    "evaluate_min_n",
]
