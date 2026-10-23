"""
Quality Accounting Engine for Disjoint Row Accounting (DC-11) and Metric Accounting (DC-12).
Conforms to DATA_CONTRACT.md, ARCHITECTURE.md, and Gate G3 / G4 governance decisions.
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Mapping, Optional, Sequence, Union
from pyspark.sql import DataFrame, functions as F

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


class AccountingBalanceError(RuntimeError):
    """Raised when DC-11 or DC-12 accounting invariants fail validation."""


class QualityAccountingEngine:
    """
    Engine implementing strict three-state disjoint row accounting (DC-11)
    and metric valid/invalid accounting (DC-12).
    """

    @staticmethod
    def verify_row_accounting(accounting: RowAccounting) -> None:
        """
        Verify that a RowAccounting instance satisfies DC-11 invariants:
        - Non-negative counts for all states.
        - Exact balance: raw == accepted + quarantined + rejected.
        Raises AccountingBalanceError on any discrepancy.
        """
        if not accounting.is_balanced():
            raise AccountingBalanceError(
                f"ACCOUNTING_UNVERIFIED: Row accounting balance failed DC-11. "
                f"raw={accounting.raw_row_count} != accepted={accounting.accepted_row_count} + "
                f"quarantined={accounting.quarantined_row_count} + rejected={accounting.rejected_row_count} "
                f"(sum={accounting.accepted_row_count + accounting.quarantined_row_count + accounting.rejected_row_count})"
            )

    @classmethod
    def compute_and_verify_row_accounting(
        cls,
        classified_df: DataFrame,
        independent_raw_count: int,
        status_col: str = "_record_status",
    ) -> RowAccounting:
        """
        Compute row accounting counts from a classified DataFrame and strictly verify against
        an independent ground-truth raw record count.
        
        Args:
            classified_df: DataFrame containing the status classification column.
            independent_raw_count: Independent record count observed from source file/manifest.
            status_col: Name of the status column (default "_record_status").
            
        Returns:
            Verified RowAccounting instance.
            
        Raises:
            AccountingBalanceError: If independent count is non-positive or sum does not match.
        """
        if independent_raw_count is None:
            raise AccountingBalanceError("ACCOUNTING_UNVERIFIED: independent_raw_count must not be None.")
        if independent_raw_count < 0:
            raise AccountingBalanceError(
                f"ACCOUNTING_UNVERIFIED: independent_raw_count cannot be negative: {independent_raw_count}"
            )
        if status_col not in classified_df.columns:
            raise AccountingBalanceError(f"DataFrame missing status column: {status_col}")

        # Compute status counts in a single pass aggregation
        counts_df = classified_df.groupBy(status_col).agg(F.count(F.lit(1)).alias("cnt")).collect()
        status_map: Dict[str, int] = {r[status_col]: int(r["cnt"]) for r in counts_df if r[status_col] is not None}

        accepted = status_map.get("ACCEPTED", 0)
        quarantined = status_map.get("QUARANTINED", 0)
        rejected = status_map.get("REJECTED", 0)
        
        # Check for unexpected statuses (violating three-state disjointness)
        total_observed = sum(status_map.values())
        valid_three_state_sum = accepted + quarantined + rejected
        if total_observed != valid_three_state_sum:
            unknown_keys = set(status_map.keys()) - {"ACCEPTED", "QUARANTINED", "REJECTED"}
            raise AccountingBalanceError(
                f"ACCOUNTING_UNVERIFIED: Unknown classification states detected: {unknown_keys}. "
                f"DC-11 strictly requires exactly three disjoint states."
            )

        accounting = RowAccounting(
            raw_row_count=independent_raw_count,
            accepted_row_count=accepted,
            quarantined_row_count=quarantined,
            rejected_row_count=rejected,
        )

        cls.verify_row_accounting(accounting)
        return accounting

    @staticmethod
    def compute_metric_accounting(
        df: DataFrame,
        metric_name: str,
        valid_condition: F.Column,
    ) -> MetricAccounting:
        """
        Compute DC-12 metric accounting on a DataFrame:
        - Evaluates count_records (total records in the cohort)
        - Evaluates count_metric_valid (records satisfying valid_condition)
        - Enforces count_metric_valid <= count_records
        - Handles zero-denominator cleanly without division by zero
        """
        agg_row = df.select(
            F.count(F.lit(1)).alias("count_records"),
            F.sum(F.when(valid_condition, 1).otherwise(0)).alias("count_metric_valid"),
        ).collect()[0]

        total = int(agg_row["count_records"] or 0)
        valid = int(agg_row["count_metric_valid"] or 0)

        return MetricAccounting(
            metric_name=metric_name,
            count_records=total,
            count_metric_valid=valid,
        )

    @classmethod
    def compute_all_core_metrics(cls, accepted_df: DataFrame) -> Dict[str, MetricAccounting]:
        """
        Compute metric accounting for all 7 CORE measures on accepted flight records (DC-12).
        Uses predicates from `flight_pipeline.quality.predicates` ensuring complete protection
        against null, NaN, and +/- Inf, while preserving signed negative delays.
        """
        # Predicate mapping for 7 CORE measures
        metric_predicates = {
            "ARR_DELAY": is_valid_arr_delay("ARR_DELAY"),
            "DEP_DELAY": is_valid_dep_delay("DEP_DELAY"),
            "TAXI_OUT": is_valid_taxi_out("TAXI_OUT"),
            "TAXI_IN": is_valid_taxi_in("TAXI_IN"),
            "AIR_TIME": is_valid_air_time("AIR_TIME"),
            "ACTUAL_ELAPSED_TIME": is_valid_actual_elapsed_time("ACTUAL_ELAPSED_TIME"),
            "CRS_ELAPSED_TIME": is_valid_crs_elapsed_time("CRS_ELAPSED_TIME"),
        }

        # Single aggregation pass for all 7 measures
        select_exprs = [F.count(F.lit(1)).alias("total_records")]
        for m_name, pred in metric_predicates.items():
            select_exprs.append(
                F.sum(F.when(pred, 1).otherwise(0)).alias(f"valid_{m_name}")
            )

        agg_row = accepted_df.select(select_exprs).collect()[0]
        total_records = int(agg_row["total_records"] or 0)

        results: Dict[str, MetricAccounting] = {}
        for m_name in metric_predicates:
            valid_cnt = int(agg_row[f"valid_{m_name}"] or 0)
            results[m_name] = MetricAccounting(
                metric_name=m_name,
                count_records=total_records,
                count_metric_valid=valid_cnt,
            )
        return results

    @classmethod
    def reconcile_multi_source_accounting(
        cls,
        accountings_by_source: Mapping[str, RowAccounting],
        expected_total_raw: int,
    ) -> RowAccounting:
        """
        Aggregate and reconcile multiple per-source RowAccounting instances.
        Verifies individual balances and aggregate balance against expected total.
        """
        total_raw = 0
        total_acc = 0
        total_quar = 0
        total_rej = 0

        for src_name, acct in accountings_by_source.items():
            cls.verify_row_accounting(acct)
            total_raw += acct.raw_row_count
            total_acc += acct.accepted_row_count
            total_quar += acct.quarantined_row_count
            total_rej += acct.rejected_row_count

        if total_raw != expected_total_raw:
            raise AccountingBalanceError(
                f"ACCOUNTING_UNVERIFIED: Multi-source total raw ({total_raw}) does not match "
                f"expected total raw ({expected_total_raw})."
            )

        aggregate = RowAccounting(
            raw_row_count=total_raw,
            accepted_row_count=total_acc,
            quarantined_row_count=total_quar,
            rejected_row_count=total_rej,
        )
        cls.verify_row_accounting(aggregate)
        return aggregate
