"""
Quality Policy Configuration and Provisional Policy Profiling (T-008).
Conforms to DATA_CONTRACT.md, ARCHITECTURE.md, and Gate G3 / G4 governance decisions (G3-COND-A, FP-DEC-017).
"""

from dataclasses import dataclass, asdict, field
from typing import Any, Dict, List, Optional
from pyspark.sql import DataFrame, functions as F


class PolicyViolationError(ValueError):
    """Raised when an unapproved or disallowed quality policy configuration is attempted."""


@dataclass(frozen=True)
class QualityPolicyConfig:
    """
    Configuration controlling quality validation behavior and governance invariants.
    
    RUNTIME EXECUTION GUARDS (Canonical Production Invariants):
    - quarantine_non_positive_flight_num (default False): Under G3-COND-A, non-positive flight numbers
      (OP_CARRIER_FL_NUM <= 0) must remain ACCEPTED with an anomaly flag. Escalating to hard quarantine
      is strictly provisional pending real BTS data validation at Gate G5.
    - allow_weather_nulls (default True): Under FP-DEC-017 (CONDITIONAL_NO_GO), weather column nulls or
      absence must never quarantine or reject valid CORE flights.
    - strict_record_accounting (default True): Enforces DC-11 3-state disjoint row accounting balance.
    - strict_metric_accounting (default True): Enforces DC-12 metric valid bound and zero-denominator safety.
    
    SIMULATION PARAMETER:
    - allow_unapproved_policies (default False): Safety gate required to run offline what-if policy
      simulations (e.g. simulating the volume impact of hard quarantining non-positive flight numbers).
      Must NEVER be enabled in canonical production execution.
    """
    # Runtime execution guards
    quarantine_non_positive_flight_num: bool = False
    allow_weather_nulls: bool = True
    strict_record_accounting: bool = True
    strict_metric_accounting: bool = True
    
    # Simulation safety gate
    allow_unapproved_policies: bool = False

    def __post_init__(self):
        self.validate()

    def validate(self) -> None:
        """Validate configuration against canonical governance invariants."""
        if self.quarantine_non_positive_flight_num and not self.allow_unapproved_policies:
            raise PolicyViolationError(
                "GOVERNANCE_VIOLATION: Hard quarantine for OP_CARRIER_FL_NUM <= 0 is strictly "
                "PROVISIONAL under G3-COND-A. Escalation to hard quarantine requires explicit human "
                "signoff after real BTS data validation at Gate G5. Set allow_unapproved_policies=True "
                "only for offline impact simulations."
            )
        if not self.allow_weather_nulls and not self.allow_unapproved_policies:
            raise PolicyViolationError(
                "GOVERNANCE_VIOLATION: Disallowing weather nulls violates FP-DEC-017 (CONDITIONAL_NO_GO). "
                "Weather absence must not quarantine or reject valid CORE flights."
            )

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return asdict(self)


def assert_production_policy_compliance(policy: QualityPolicyConfig) -> None:
    """
    Production Safety Hard Guard (G3-COND-A, FP-DEC-017).
    Enforces that canonical production and bounded real-data smoke execution strictly
    reject simulation parameters and unapproved policy deviations at the entrypoint.
    
    Invariants Enforced:
    1. allow_unapproved_policies == False: Simulation mode strictly rejected in production.
    2. quarantine_non_positive_flight_num == False: Under G3-COND-A, non-positive flight numbers
       remain ACCEPTED with anomaly flag, never whole-record quarantined in production.
    3. allow_weather_nulls == True: Under FP-DEC-017 (CONDITIONAL_NO_GO), weather absence
       must never quarantine or reject valid flight events.
    4. strict_record_accounting == True: Enforces DC-11 3-state disjoint row accounting.
    5. strict_metric_accounting == True: Enforces DC-12 metric valid bound and zero-denominator safety.
    """
    if policy.allow_unapproved_policies:
        raise PolicyViolationError(
            "PRODUCTION_GUARD_VIOLATION: allow_unapproved_policies=True is strictly prohibited in "
            "canonical production and real-data execution. It is reserved solely for offline simulations."
        )
    if policy.quarantine_non_positive_flight_num:
        raise PolicyViolationError(
            "PRODUCTION_GUARD_VIOLATION: Hard quarantine for OP_CARRIER_FL_NUM <= 0 is prohibited "
            "under G3-COND-A in production mode."
        )
    if not policy.allow_weather_nulls:
        raise PolicyViolationError(
            "PRODUCTION_GUARD_VIOLATION: Disallowing weather nulls violates FP-DEC-017."
        )
    if not policy.strict_record_accounting:
        raise PolicyViolationError(
            "PRODUCTION_GUARD_VIOLATION: strict_record_accounting must be True under DC-11."
        )
    if not policy.strict_metric_accounting:
        raise PolicyViolationError(
            "PRODUCTION_GUARD_VIOLATION: strict_metric_accounting must be True under DC-12."
        )


@dataclass(frozen=True)
class ProvisionalPolicyProfile:
    """
    Results of profiling provisional rules (e.g., OP_CARRIER_FL_NUM <= 0 under G3-COND-A).
    Captures exact frequency, carrier breakdown, and simulated policy impacts.
    """
    total_records: int
    non_positive_count: int
    non_positive_rate: Optional[float]
    zero_count: int
    negative_count: int
    affected_carriers: Dict[str, int]
    simulated_accepted_under_canonical_policy: int
    simulated_quarantined_under_hard_policy: int
    governance_status: str = "PROVISIONAL_POLICY_PENDING_REAL_DATA_VALIDATION"

    def to_dict(self) -> Dict[str, Any]:
        """Convert profile to dictionary."""
        return asdict(self)


class ProvisionalPolicyProfiler:
    """
    Analyzer and simulation engine for provisional data quality rules.
    Allows measuring policy impact without mutating production records or breaching G3-COND-A.
    """

    @staticmethod
    def profile_flight_number_anomalies(df: DataFrame) -> ProvisionalPolicyProfile:
        """
        Profile the distribution and impact of non-positive flight numbers (G3-COND-A).
        Evaluates on input DataFrame without mutating original columns.
        """
        fl_num_col = "OP_CARRIER_FL_NUM"
        carrier_col = "OP_CARRIER"
        
        if fl_num_col not in df.columns:
            raise ValueError(f"DataFrame missing required column: {fl_num_col}")
        
        # Cast to numeric safely
        fl_num_double = F.expr(f"try_cast(trim({fl_num_col}) AS double)")
        is_finite_num = fl_num_double.isNotNull() & ~F.isnan(fl_num_double) & ~fl_num_double.isin(float("inf"), float("-inf"))
        
        is_zero = is_finite_num & (fl_num_double == 0.0)
        is_negative = is_finite_num & (fl_num_double < 0.0)
        is_non_positive = is_zero | is_negative

        # Aggregate counts in a single pass
        agg_row = df.select(
            F.count(F.lit(1)).alias("total_records"),
            F.sum(F.when(is_non_positive, 1).otherwise(0)).alias("non_positive_count"),
            F.sum(F.when(is_zero, 1).otherwise(0)).alias("zero_count"),
            F.sum(F.when(is_negative, 1).otherwise(0)).alias("negative_count"),
        ).collect()[0]

        total = int(agg_row["total_records"] or 0)
        non_pos = int(agg_row["non_positive_count"] or 0)
        zeros = int(agg_row["zero_count"] or 0)
        negs = int(agg_row["negative_count"] or 0)
        
        rate = (non_pos / total) if total > 0 else None

        # Carrier breakdown for non-positive flights
        carrier_counts: Dict[str, int] = {}
        if non_pos > 0 and carrier_col in df.columns:
            carrier_rows = (
                df.filter(is_non_positive)
                .groupBy(carrier_col)
                .agg(F.count(F.lit(1)).alias("cnt"))
                .collect()
            )
            for r in carrier_rows:
                c_key = str(r[carrier_col]) if r[carrier_col] is not None else "<NULL>"
                carrier_counts[c_key] = int(r["cnt"])

        # Under canonical G3-COND-A policy: non-positive flight numbers are ACCEPTED (flagged only)
        # Under alternative hard policy: they would be moved to QUARANTINED
        return ProvisionalPolicyProfile(
            total_records=total,
            non_positive_count=non_pos,
            non_positive_rate=rate,
            zero_count=zeros,
            negative_count=negs,
            affected_carriers=carrier_counts,
            simulated_accepted_under_canonical_policy=total,
            simulated_quarantined_under_hard_policy=non_pos,
            governance_status="PROVISIONAL_POLICY_PENDING_REAL_DATA_VALIDATION",
        )
