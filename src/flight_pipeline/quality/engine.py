"""
Unified Data Quality Engine for US Flight Performance Analysis (T-008).
Conforms to DATA_CONTRACT.md (DC-11, DC-12), ARCHITECTURE.md, T006_FINAL_CORRECTIONS_ADDENDUM.md,
and Gate G3 / G4 governance decisions (G3-COND-A, FP-DEC-007, FP-DEC-010, FP-DEC-017).
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple, Union
from pyspark.sql import DataFrame, functions as F

from flight_pipeline.ingestion.reader import (
    RecordStatus,
    AnomalyReason,
    STATUS_COLUMN,
    REASON_COLUMN,
    ANOMALY_FLAGS_COLUMN,
    IngestionRecordClassifier,
)
from flight_pipeline.quality.accounting import QualityAccountingEngine, AccountingBalanceError
from flight_pipeline.quality.catalog import QualityRuleCatalog
from flight_pipeline.quality.coverage import DateCoverageAnalyzer, CoverageReport
from flight_pipeline.quality.policy import (
    QualityPolicyConfig,
    ProvisionalPolicyProfile,
    ProvisionalPolicyProfiler,
)
from flight_pipeline.quality.predicates import (
    is_valid_arr_delay,
    is_valid_dep_delay,
    is_valid_taxi_out,
    is_valid_taxi_in,
    is_valid_air_time,
    is_valid_actual_elapsed_time,
    is_valid_crs_elapsed_time,
)
from flight_pipeline.utils.run_manifest import RowAccounting, MetricAccounting


@dataclass(frozen=True)
class QualityValidationResult:
    """
    Comprehensive results of Data Quality Engine execution.
    Encapsulates DC-11 row accounting, DC-12 metric accounting, calendar coverage,
    and provisional policy profiling.
    """
    row_accounting: RowAccounting
    metric_accounting: Dict[str, MetricAccounting]
    coverage_report: Optional[CoverageReport] = None
    provisional_policy_profile: Optional[ProvisionalPolicyProfile] = None
    accepted_count: int = 0
    quarantined_count: int = 0
    rejected_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary for manifest serialization."""
        return {
            "row_accounting": self.row_accounting.to_dict(),
            "metric_accounting": {k: v.to_dict() for k, v in self.metric_accounting.items()},
            "coverage_report": self.coverage_report.to_dict() if self.coverage_report else None,
            "provisional_policy_profile": (
                self.provisional_policy_profile.to_dict() if self.provisional_policy_profile else None
            ),
            "accepted_count": self.accepted_count,
            "quarantined_count": self.quarantined_count,
            "rejected_count": self.rejected_count,
        }


class QualityEngine:
    """
    Production Data Quality Engine operating downstream of RawCsvReader.
    Evaluates:
    1. DC-11 3-state disjoint row accounting balance against independent raw source count.
    2. DC-12 submetric validity on accepted records across all 7 CORE measures.
    3. G3-COND-A provisional flight number policy analysis without unauthorized hard quarantine.
    4. OR-05 calendar date coverage and missing day detection.
    5. Clean separation between Record Validity and Metric Validity.
    """

    def __init__(self, policy: Optional[QualityPolicyConfig] = None):
        self.policy = policy or QualityPolicyConfig()

    @staticmethod
    def attach_metric_validity_flags(df: DataFrame) -> DataFrame:
        """
        Augment DataFrame with 7 boolean metric validity columns per DC-12.
        Does NOT drop or quarantine records with invalid metrics.
        """
        return (
            df.withColumn("is_valid_arr_delay", is_valid_arr_delay("ARR_DELAY"))
            .withColumn("is_valid_dep_delay", is_valid_dep_delay("DEP_DELAY"))
            .withColumn("is_valid_taxi_out", is_valid_taxi_out("TAXI_OUT"))
            .withColumn("is_valid_taxi_in", is_valid_taxi_in("TAXI_IN"))
            .withColumn("is_valid_air_time", is_valid_air_time("AIR_TIME"))
            .withColumn("is_valid_actual_elapsed_time", is_valid_actual_elapsed_time("ACTUAL_ELAPSED_TIME"))
            .withColumn("is_valid_crs_elapsed_time", is_valid_crs_elapsed_time("CRS_ELAPSED_TIME"))
        )

    def evaluate(
        self,
        df: DataFrame,
        independent_raw_count: int,
        source_year: Optional[int] = None,
        analyze_coverage: bool = True,
        profile_provisional_policy: bool = True,
    ) -> Tuple[DataFrame, QualityValidationResult]:
        """
        Run complete data quality validation on an ingested DataFrame.
        
        Args:
            df: Ingested DataFrame (raw or already classified).
            independent_raw_count: Independent record count observed from source file/manifest.
            source_year: Target survey year for calendar coverage analysis.
            analyze_coverage: If True and source_year is provided, evaluates calendar date coverage.
            profile_provisional_policy: If True, profiles G3-COND-A flight number anomalies.
            
        Returns:
            Tuple of (augmented_df, QualityValidationResult).
        """
        # 1. Ensure record classification is applied
        if STATUS_COLUMN not in df.columns:
            working_df = IngestionRecordClassifier.classify(df)
        else:
            working_df = df

        # 1b. Offline policy simulation: if quarantine_non_positive_flight_num is activated
        # (Only permitted when allow_unapproved_policies=True per G3-COND-A)
        if self.policy.quarantine_non_positive_flight_num:
            fl_num_col = "OP_CARRIER_FL_NUM"
            if fl_num_col in working_df.columns:
                fl_num_d = F.expr(f"try_cast(trim({fl_num_col}) AS double)")
                is_non_pos = (
                    fl_num_d.isNotNull()
                    & ~F.isnan(fl_num_d)
                    & ~fl_num_d.isin(float("inf"), float("-inf"))
                    & (fl_num_d <= 0.0)
                )
                working_df = (
                    working_df.withColumn(
                        REASON_COLUMN,
                        F.when(
                            (F.col(STATUS_COLUMN) == RecordStatus.ACCEPTED.value) & is_non_pos,
                            F.lit("PROVISIONAL_FLIGHT_NUM_NON_POSITIVE"),
                        ).otherwise(F.col(REASON_COLUMN)),
                    )
                    .withColumn(
                        STATUS_COLUMN,
                        F.when(
                            (F.col(STATUS_COLUMN) == RecordStatus.ACCEPTED.value) & is_non_pos,
                            F.lit(RecordStatus.QUARANTINED.value),
                        ).otherwise(F.col(STATUS_COLUMN)),
                    )
                )

        # 2. Compute and verify DC-11 row accounting balance
        row_acct = QualityAccountingEngine.compute_and_verify_row_accounting(
            working_df,
            independent_raw_count=independent_raw_count,
            status_col=STATUS_COLUMN,
        )

        # 3. Filter accepted records for metric evaluation
        accepted_df = working_df.filter(F.col(STATUS_COLUMN) == RecordStatus.ACCEPTED.value)

        # 4. Compute DC-12 metric accounting for 7 CORE measures
        metric_accts = QualityAccountingEngine.compute_all_core_metrics(accepted_df)

        # 5. Date coverage analysis (OR-05)
        cov_report: Optional[CoverageReport] = None
        if analyze_coverage and source_year is not None and "FL_DATE" in working_df.columns:
            cov_report = DateCoverageAnalyzer.analyze(
                accepted_df,
                target_year=source_year,
                date_col="FL_DATE",
            )

        # 6. Provisional policy profiling (G3-COND-A)
        prof_profile: Optional[ProvisionalPolicyProfile] = None
        if profile_provisional_policy and "OP_CARRIER_FL_NUM" in working_df.columns:
            prof_profile = ProvisionalPolicyProfiler.profile_flight_number_anomalies(accepted_df)

        # 7. Attach metric validity columns to output DataFrame
        augmented_df = self.attach_metric_validity_flags(working_df)

        result = QualityValidationResult(
            row_accounting=row_acct,
            metric_accounting=metric_accts,
            coverage_report=cov_report,
            provisional_policy_profile=prof_profile,
            accepted_count=row_acct.accepted_row_count,
            quarantined_count=row_acct.quarantined_row_count,
            rejected_count=row_acct.rejected_row_count,
        )

        return augmented_df, result
