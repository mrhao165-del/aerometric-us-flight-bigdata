"""
Data Quality and Validation Package (T-008).
Conforms to DATA_CONTRACT.md (DC-11, DC-12), ARCHITECTURE.md, and Gate G3 / G4 specifications.
"""

from flight_pipeline.quality.predicates import (
    is_finite_numeric,
    is_valid_arr_delay,
    is_valid_dep_delay,
    is_valid_taxi_out,
    is_valid_taxi_in,
    is_valid_air_time,
    is_valid_actual_elapsed_time,
    is_valid_crs_elapsed_time,
)
from flight_pipeline.quality.catalog import (
    QualityRule,
    QualityRuleCatalog,
    RuleSeverity,
    RuleScope,
    RuleConsequence,
    RULE_SYNTAX_CORRUPT,
    RULE_DATE_CORE_ANCHOR,
    RULE_DATE_YEAR_MISMATCH,
    RULE_CARRIER_CORE_ANCHOR,
    RULE_AIRPORT_CORE_ANCHOR,
    RULE_FLIGHT_NUM_CORE_ANCHOR,
    RULE_FLIGHT_NUM_NON_POSITIVE_PROVISIONAL,
    RULE_WEATHER_MISSING,
    RULE_ARR_DELAY_VALID,
    RULE_DEP_DELAY_VALID,
    RULE_TAXI_OUT_VALID,
    RULE_TAXI_IN_VALID,
    RULE_AIR_TIME_VALID,
    RULE_ACTUAL_ELAPSED_TIME_VALID,
    RULE_CRS_ELAPSED_TIME_VALID,
    RULE_CALENDAR_COVERAGE,
    RULE_ROW_ACCOUNTING_BALANCE,
    RULE_METRIC_BOUND_ACCOUNTING,
)
from flight_pipeline.quality.policy import (
    PolicyViolationError,
    QualityPolicyConfig,
    assert_production_policy_compliance,
    ProvisionalPolicyProfile,
    ProvisionalPolicyProfiler,
)
from flight_pipeline.quality.coverage import (
    CoverageReport,
    DateCoverageAnalyzer,
)
from flight_pipeline.quality.accounting import (
    AccountingBalanceError,
    QualityAccountingEngine,
)
from flight_pipeline.quality.engine import (
    QualityEngine,
    QualityValidationResult,
)

__all__ = [
    # Numeric Predicates
    "is_finite_numeric",
    "is_valid_arr_delay",
    "is_valid_dep_delay",
    "is_valid_taxi_out",
    "is_valid_taxi_in",
    "is_valid_air_time",
    "is_valid_actual_elapsed_time",
    "is_valid_crs_elapsed_time",
    # Quality Rules & Catalog
    "QualityRule",
    "QualityRuleCatalog",
    "RuleSeverity",
    "RuleScope",
    "RuleConsequence",
    "RULE_SYNTAX_CORRUPT",
    "RULE_DATE_CORE_ANCHOR",
    "RULE_DATE_YEAR_MISMATCH",
    "RULE_CARRIER_CORE_ANCHOR",
    "RULE_AIRPORT_CORE_ANCHOR",
    "RULE_FLIGHT_NUM_CORE_ANCHOR",
    "RULE_FLIGHT_NUM_NON_POSITIVE_PROVISIONAL",
    "RULE_WEATHER_MISSING",
    "RULE_ARR_DELAY_VALID",
    "RULE_DEP_DELAY_VALID",
    "RULE_TAXI_OUT_VALID",
    "RULE_TAXI_IN_VALID",
    "RULE_AIR_TIME_VALID",
    "RULE_ACTUAL_ELAPSED_TIME_VALID",
    "RULE_CRS_ELAPSED_TIME_VALID",
    "RULE_CALENDAR_COVERAGE",
    "RULE_ROW_ACCOUNTING_BALANCE",
    "RULE_METRIC_BOUND_ACCOUNTING",
    # Policy
    "PolicyViolationError",
    "QualityPolicyConfig",
    "assert_production_policy_compliance",
    "ProvisionalPolicyProfile",
    "ProvisionalPolicyProfiler",
    # Coverage
    "CoverageReport",
    "DateCoverageAnalyzer",
    # Accounting
    "AccountingBalanceError",
    "QualityAccountingEngine",
    # Engine
    "QualityEngine",
    "QualityValidationResult",
]
