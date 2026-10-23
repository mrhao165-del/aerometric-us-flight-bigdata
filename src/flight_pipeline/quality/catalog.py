"""
Data Quality Rule Catalog and Rule Metadata Definitions (T-008).
Conforms to DATA_CONTRACT.md (DC-11, DC-12), ARCHITECTURE.md, T006_FINAL_CORRECTIONS_ADDENDUM.md,
and Gate G3 / G4 governance decisions (G3-COND-A, FP-DEC-007, FP-DEC-010, FP-DEC-017).
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Sequence


class RuleSeverity(str, Enum):
    """Severity level of a quality rule violation."""
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"


class RuleScope(str, Enum):
    """Scope of evaluation for the quality rule."""
    RECORD = "RECORD"      # Evaluated per individual record (DC-11 disposition)
    METRIC = "METRIC"      # Evaluated per submetric on accepted records (DC-12)
    DATASET = "DATASET"    # Evaluated across the dataset/cohort (coverage, accounting)


class RuleConsequence(str, Enum):
    """Consequence of rule violation on record or metric disposition."""
    REJECT = "REJECT"                    # DC-11 REJECTED (unrecoverable syntax corruption)
    QUARANTINE = "QUARANTINE"            # DC-11 QUARANTINED (core entity anchor failure)
    METRIC_INVALID = "METRIC_INVALID"    # DC-12 Metric invalidity (record remains ACCEPTED)
    FLAG_ONLY = "FLAG_ONLY"              # Informational or provisional flag (record remains ACCEPTED)


@dataclass(frozen=True)
class QualityRule:
    """
    Formal specification of a data quality rule.
    Provides complete traceability to canonical contracts, authorities, and test cases.
    """
    rule_id: str
    name: str
    scope: RuleScope
    severity: RuleSeverity
    consequence: RuleConsequence
    authority: str
    description: str
    approval_status: str = "APPROVED"
    is_provisional: bool = False
    target_columns: Sequence[str] = field(default_factory=tuple)


# Canonical Rule Definitions
RULE_SYNTAX_CORRUPT = QualityRule(
    rule_id="QR-REC-01",
    name="SYNTAX_PARSER_CORRUPTION",
    scope=RuleScope.RECORD,
    severity=RuleSeverity.ERROR,
    consequence=RuleConsequence.REJECT,
    authority="DC-11 / FIX-F06 / Univocity parser",
    description="Record has unrecoverable CSV parser syntax errors (token count mismatch, unclosed quotes).",
    approval_status="APPROVED",
    is_provisional=False,
    target_columns=("_corrupt_record",),
)

RULE_DATE_CORE_ANCHOR = QualityRule(
    rule_id="QR-REC-02",
    name="INVALID_FL_DATE_CORE_ANCHOR",
    scope=RuleScope.RECORD,
    severity=RuleSeverity.ERROR,
    consequence=RuleConsequence.QUARANTINE,
    authority="FP-DEC-007 / FIX-F06 / T006 Addendum Sec 6.3",
    description="FL_DATE is null, empty, fails anchored regex (YYYY-MM-DD), or fails real calendar date parsing.",
    approval_status="APPROVED",
    is_provisional=False,
    target_columns=("FL_DATE",),
)

RULE_DATE_YEAR_MISMATCH = QualityRule(
    rule_id="QR-REC-03",
    name="SOURCE_YEAR_DATE_MISMATCH",
    scope=RuleScope.RECORD,
    severity=RuleSeverity.ERROR,
    consequence=RuleConsequence.QUARANTINE,
    authority="FIX-F06 / TS-002",
    description="Year component of FL_DATE does not match source file year (_source_year).",
    approval_status="APPROVED",
    is_provisional=False,
    target_columns=("FL_DATE", "_source_year"),
)

RULE_CARRIER_CORE_ANCHOR = QualityRule(
    rule_id="QR-REC-04",
    name="MISSING_CARRIER_CORE_ANCHOR",
    scope=RuleScope.RECORD,
    severity=RuleSeverity.ERROR,
    consequence=RuleConsequence.QUARANTINE,
    authority="FIX-F06 / T006 Addendum Sec 2.1",
    description="Operating carrier code (OP_CARRIER) is null, blank, or missing.",
    approval_status="APPROVED",
    is_provisional=False,
    target_columns=("OP_CARRIER",),
)

RULE_AIRPORT_CORE_ANCHOR = QualityRule(
    rule_id="QR-REC-05",
    name="MISSING_AIRPORT_CORE_ANCHOR",
    scope=RuleScope.RECORD,
    severity=RuleSeverity.ERROR,
    consequence=RuleConsequence.QUARANTINE,
    authority="FIX-F06 / T006 Addendum Sec 2.1",
    description="Origin airport (ORIGIN) or Destination airport (DEST) is null, blank, or missing.",
    approval_status="APPROVED",
    is_provisional=False,
    target_columns=("ORIGIN", "DEST"),
)

RULE_FLIGHT_NUM_CORE_ANCHOR = QualityRule(
    rule_id="QR-REC-06",
    name="INVALID_FLIGHT_NUM_CORE_ANCHOR",
    scope=RuleScope.RECORD,
    severity=RuleSeverity.ERROR,
    consequence=RuleConsequence.QUARANTINE,
    authority="FIX-F06 / T006 Addendum Sec 2.1",
    description="OP_CARRIER_FL_NUM is null, blank, non-numeric, or non-finite (+/- Inf, NaN).",
    approval_status="APPROVED",
    is_provisional=False,
    target_columns=("OP_CARRIER_FL_NUM",),
)

RULE_FLIGHT_NUM_NON_POSITIVE_PROVISIONAL = QualityRule(
    rule_id="QR-REC-07",
    name="PROVISIONAL_FLIGHT_NUM_NON_POSITIVE",
    scope=RuleScope.RECORD,
    severity=RuleSeverity.WARNING,
    consequence=RuleConsequence.FLAG_ONLY,
    authority="G3-COND-A / T006 Addendum Sec 2.1",
    description="OP_CARRIER_FL_NUM <= 0 (finite numeric). Record remains ACCEPTED; hard quarantine is provisional.",
    approval_status="PROVISIONAL_POLICY_PENDING_REAL_DATA_VALIDATION",
    is_provisional=True,
    target_columns=("OP_CARRIER_FL_NUM",),
)

RULE_WEATHER_MISSING = QualityRule(
    rule_id="QR-REC-08",
    name="WEATHER_DATA_ABSENCE_ALLOWED",
    scope=RuleScope.RECORD,
    severity=RuleSeverity.INFO,
    consequence=RuleConsequence.FLAG_ONLY,
    authority="FP-DEC-017 / DC-07 / CONDITIONAL_NO_GO",
    description="Weather columns are missing or null. Record remains ACCEPTED; does not quarantine flight.",
    approval_status="APPROVED",
    is_provisional=False,
    target_columns=("O_TEMP", "O_PRCP", "O_WSPD", "D_TEMP", "D_PRCP", "D_WSPD"),
)

# 7 CORE Metric Rules (DC-12)
RULE_ARR_DELAY_VALID = QualityRule(
    rule_id="QR-MET-01",
    name="VALID_ARR_DELAY_METRIC",
    scope=RuleScope.METRIC,
    severity=RuleSeverity.INFO,
    consequence=RuleConsequence.METRIC_INVALID,
    authority="G2-EXC-001 / DC-12 / KPI-02, KPI-03, KPI-06",
    description="Arrival delay must be finite numeric (preserves signed negative values).",
    approval_status="APPROVED",
    is_provisional=False,
    target_columns=("ARR_DELAY",),
)

RULE_DEP_DELAY_VALID = QualityRule(
    rule_id="QR-MET-02",
    name="VALID_DEP_DELAY_METRIC",
    scope=RuleScope.METRIC,
    severity=RuleSeverity.INFO,
    consequence=RuleConsequence.METRIC_INVALID,
    authority="G2-EXC-001 / DC-12 / KPI-04, KPI-05",
    description="Departure delay must be finite numeric (preserves signed negative values).",
    approval_status="APPROVED",
    is_provisional=False,
    target_columns=("DEP_DELAY",),
)

RULE_TAXI_OUT_VALID = QualityRule(
    rule_id="QR-MET-03",
    name="VALID_TAXI_OUT_METRIC",
    scope=RuleScope.METRIC,
    severity=RuleSeverity.INFO,
    consequence=RuleConsequence.METRIC_INVALID,
    authority="DC-12 / KPI-07 Sub 7a",
    description="Taxi-out time must be finite numeric and non-negative (>= 0.0).",
    approval_status="APPROVED",
    is_provisional=False,
    target_columns=("TAXI_OUT",),
)

RULE_TAXI_IN_VALID = QualityRule(
    rule_id="QR-MET-04",
    name="VALID_TAXI_IN_METRIC",
    scope=RuleScope.METRIC,
    severity=RuleSeverity.INFO,
    consequence=RuleConsequence.METRIC_INVALID,
    authority="DC-12 / KPI-07 Sub 7b",
    description="Taxi-in time must be finite numeric and non-negative (>= 0.0).",
    approval_status="APPROVED",
    is_provisional=False,
    target_columns=("TAXI_IN",),
)

RULE_AIR_TIME_VALID = QualityRule(
    rule_id="QR-MET-05",
    name="VALID_AIR_TIME_METRIC",
    scope=RuleScope.METRIC,
    severity=RuleSeverity.INFO,
    consequence=RuleConsequence.METRIC_INVALID,
    authority="DC-12 / KPI-08 Sub 8a",
    description="Air time must be finite numeric and strictly positive (> 0.0).",
    approval_status="APPROVED",
    is_provisional=False,
    target_columns=("AIR_TIME",),
)

RULE_ACTUAL_ELAPSED_TIME_VALID = QualityRule(
    rule_id="QR-MET-06",
    name="VALID_ACTUAL_ELAPSED_TIME_METRIC",
    scope=RuleScope.METRIC,
    severity=RuleSeverity.INFO,
    consequence=RuleConsequence.METRIC_INVALID,
    authority="DC-12 / KPI-08 Sub 8b",
    description="Actual elapsed time must be finite numeric and strictly positive (> 0.0).",
    approval_status="APPROVED",
    is_provisional=False,
    target_columns=("ACTUAL_ELAPSED_TIME",),
)

RULE_CRS_ELAPSED_TIME_VALID = QualityRule(
    rule_id="QR-MET-07",
    name="VALID_CRS_ELAPSED_TIME_METRIC",
    scope=RuleScope.METRIC,
    severity=RuleSeverity.INFO,
    consequence=RuleConsequence.METRIC_INVALID,
    authority="DC-12 / KPI-08 Sub 8c",
    description="CRS scheduled elapsed time must be finite numeric and strictly positive (> 0.0).",
    approval_status="APPROVED",
    is_provisional=False,
    target_columns=("CRS_ELAPSED_TIME",),
)

# Dataset & Accounting Rules
RULE_CALENDAR_COVERAGE = QualityRule(
    rule_id="QR-DAT-01",
    name="CALENDAR_DATE_COVERAGE",
    scope=RuleScope.DATASET,
    severity=RuleSeverity.WARNING,
    consequence=RuleConsequence.FLAG_ONLY,
    authority="OR-05 / FP-DEC-002 / TS-004",
    description="Evaluates daily calendar coverage (365/366 expected days; detects missing March 2024).",
    approval_status="APPROVED",
    is_provisional=False,
    target_columns=("FL_DATE",),
)

RULE_ROW_ACCOUNTING_BALANCE = QualityRule(
    rule_id="QR-DAT-02",
    name="DISJOINT_ROW_ACCOUNTING_BALANCE",
    scope=RuleScope.DATASET,
    severity=RuleSeverity.ERROR,
    consequence=RuleConsequence.REJECT,
    authority="DC-11 / FIX-F02 / TS-003",
    description="Mandatory disjoint accounting balance: N_raw == N_accepted + N_quarantined + N_rejected.",
    approval_status="APPROVED",
    is_provisional=False,
    target_columns=("_record_status",),
)

RULE_METRIC_BOUND_ACCOUNTING = QualityRule(
    rule_id="QR-DAT-03",
    name="METRIC_COUNT_BOUND_ACCOUNTING",
    scope=RuleScope.DATASET,
    severity=RuleSeverity.ERROR,
    consequence=RuleConsequence.REJECT,
    authority="DC-12 / TS-003",
    description="For every metric: count_metric_valid <= count_records; zero denominator handled cleanly.",
    approval_status="APPROVED",
    is_provisional=False,
    target_columns=(),
)


class QualityRuleCatalog:
    """Registry and query interface for all data quality rules in the pipeline."""

    _ALL_RULES: Sequence[QualityRule] = (
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

    @classmethod
    def get_all_rules(cls) -> Sequence[QualityRule]:
        """Return all registered quality rules."""
        return cls._ALL_RULES

    @classmethod
    def get_rule_by_id(cls, rule_id: str) -> Optional[QualityRule]:
        """Look up a rule by rule_id."""
        for r in cls._ALL_RULES:
            if r.rule_id == rule_id:
                return r
        return None

    @classmethod
    def get_rules_by_scope(cls, scope: RuleScope) -> List[QualityRule]:
        """Filter rules by scope."""
        return [r for r in cls._ALL_RULES if r.scope == scope]

    @classmethod
    def get_provisional_rules(cls) -> List[QualityRule]:
        """Return all rules flagged as provisional."""
        return [r for r in cls._ALL_RULES if r.is_provisional]
