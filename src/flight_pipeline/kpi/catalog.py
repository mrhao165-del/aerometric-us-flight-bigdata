"""
Catalog definitions and constants for the 8 CORE KPIs.
Conforms to KPI_SPEC.md, DATA_CONTRACT.md (DC-11, DC-12),
DECISIONS.md (FP-DEC-008, FP-DEC-011, FP-DEC-012, FP-DEC-015, FP-DEC-016),
and Master Execution Prompt T-011.
"""

from dataclasses import dataclass
from typing import Optional, List, Dict, Any


KPI_VERSION: str = "1.0.0"
QUALITY_VERSION: str = "docs-v1.1"

# Unit metadata status under G2-EXC-001 / TS-018
UNIT_STATUS_PROVISIONAL: str = "OFFICIAL_MINUTES_EMPIRICALLY_CONSISTENT_PROVISIONAL"
UNIT_STATUS_RESOLVED: str = "RESOLVED_BY_TS018_APPROVED_OPTION_B"
UNIT_STATUS_ZERO_DENOMINATOR: str = "ZERO_METRIC_DENOMINATOR"
UNIT_STATUS_COUNT_RECORDS: str = "COUNT_RECORDS"

# Source coverage statuses under DC-12
COVERAGE_UNKNOWN: str = "UNKNOWN"
COVERAGE_PARTIAL: str = "PARTIAL"
COVERAGE_VERIFIED_WITH_SCOPE: str = "VERIFIED_WITH_SCOPE"

# Min-N thresholds under FP-DEC-016
MIN_N_CARRIER_YEAR: int = 1000
MIN_N_AIRPORT_YEAR: int = 365
MIN_N_ROUTE_YEAR: int = 100

# Min-N status labels under FP-DEC-016
MIN_N_STATUS_SUPPRESSED: str = "SUPPRESSED"
MIN_N_STATUS_LOW_SAMPLE_CAUTION: str = "LOW_SAMPLE_CAUTION"
MIN_N_STATUS_SUFFICIENT: str = "SUFFICIENT"
MIN_N_STATUS_NOT_APPLICABLE: str = "NOT_APPLICABLE"

# Approved GK-sketch accuracy parameter under FP-DEC-015
PERCENTILE_APPROX_ACCURACY: int = 10000


@dataclass(frozen=True)
class KpiDefinition:
    """Canonical specification for an individual KPI or Submetric."""
    kpi_id: str
    submetric: Optional[str]
    name: str
    target_field: Optional[str]
    calculation_type: str  # 'count', 'rate_gte_15', 'mean_signed', 'mean_positive', 'percentile_50', 'percentile_90'
    description: str


# 8 CORE KPIs and submetrics specification
CORE_KPI_DEFINITIONS: List[KpiDefinition] = [
    KpiDefinition(
        kpi_id="KPI-01",
        submetric=None,
        name="Total accepted records",
        target_field=None,
        calculation_type="count",
        description="Total accepted flight records in cohort (count_records, not sum of FLIGHTS)."
    ),
    KpiDefinition(
        kpi_id="KPI-02",
        submetric=None,
        name="Arrival delay rate >= 15 min",
        target_field="ARR_DELAY",
        calculation_type="rate_gte_15",
        description="Proportion of valid ARR_DELAY >= 15.0 minutes (inclusive)."
    ),
    KpiDefinition(
        kpi_id="KPI-03",
        submetric=None,
        name="Mean signed arrival delay",
        target_field="ARR_DELAY",
        calculation_type="mean_signed",
        description="Arithmetic mean of valid signed ARR_DELAY (negative preserved)."
    ),
    KpiDefinition(
        kpi_id="KPI-04",
        submetric=None,
        name="Departure delay rate >= 15 min",
        target_field="DEP_DELAY",
        calculation_type="rate_gte_15",
        description="Proportion of valid DEP_DELAY >= 15.0 minutes (inclusive)."
    ),
    KpiDefinition(
        kpi_id="KPI-05",
        submetric=None,
        name="Mean signed departure delay",
        target_field="DEP_DELAY",
        calculation_type="mean_signed",
        description="Arithmetic mean of valid signed DEP_DELAY (negative preserved)."
    ),
    KpiDefinition(
        kpi_id="KPI-06",
        submetric="P50",
        name="Median (P50) arrival delay",
        target_field="ARR_DELAY",
        calculation_type="percentile_50",
        description="P50 ARR_DELAY via percentile_approx with accuracy=10000."
    ),
    KpiDefinition(
        kpi_id="KPI-06",
        submetric="P90",
        name="90th percentile (P90) arrival delay",
        target_field="ARR_DELAY",
        calculation_type="percentile_90",
        description="P90 ARR_DELAY via percentile_approx with accuracy=10000."
    ),
    KpiDefinition(
        kpi_id="KPI-07",
        submetric="TAXI_OUT",
        name="Mean taxi-out time",
        target_field="TAXI_OUT",
        calculation_type="mean_positive",
        description="Mean taxi-out time with independent denominator N_valid(TAXI_OUT)."
    ),
    KpiDefinition(
        kpi_id="KPI-07",
        submetric="TAXI_IN",
        name="Mean taxi-in time",
        target_field="TAXI_IN",
        calculation_type="mean_positive",
        description="Mean taxi-in time with independent denominator N_valid(TAXI_IN)."
    ),
    KpiDefinition(
        kpi_id="KPI-08",
        submetric="AIR_TIME",
        name="Mean airborne time",
        target_field="AIR_TIME",
        calculation_type="mean_positive",
        description="Mean air time with independent denominator N_valid(AIR_TIME)."
    ),
    KpiDefinition(
        kpi_id="KPI-08",
        submetric="ACTUAL_ELAPSED_TIME",
        name="Mean actual elapsed time",
        target_field="ACTUAL_ELAPSED_TIME",
        calculation_type="mean_positive",
        description="Mean actual elapsed time with independent denominator N_valid(ACTUAL_ELAPSED_TIME)."
    ),
    KpiDefinition(
        kpi_id="KPI-08",
        submetric="CRS_ELAPSED_TIME",
        name="Mean scheduled elapsed time",
        target_field="CRS_ELAPSED_TIME",
        calculation_type="mean_positive",
        description="Mean scheduled elapsed time with independent denominator N_valid(CRS_ELAPSED_TIME)."
    ),
]

# Canonical 17 output fields in exact order
KPI_OUTPUT_COLUMNS: List[str] = [
    "kpi_id",
    "submetric",
    "run_id",
    "kpi_version",
    "source_year",
    "group_dimensions",
    "filter_definition",
    "count_records",
    "count_metric_valid",
    "excluded_count",
    "metric_valid_rate",
    "source_coverage_status",
    "value",
    "unit_status",
    "min_n_status",
    "quality_version",
    "provenance_reference",
]
