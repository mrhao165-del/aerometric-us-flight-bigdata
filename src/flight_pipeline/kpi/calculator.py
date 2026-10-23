"""
KpiCalculator engine for computing the 8 CORE KPIs across cohorts and dimensions.
Conforms to KPI_SPEC.md, DATA_CONTRACT.md (DC-11, DC-12),
DECISIONS.md (FP-DEC-008, FP-DEC-011, FP-DEC-012, FP-DEC-015, FP-DEC-016, FP-DEC-017),
and 17-column output contract.
"""

from typing import List, Optional, Dict, Any
from pyspark.sql import DataFrame, Column, SparkSession, functions as F
from pyspark.sql.types import (
    DoubleType,
    LongType,
    StringType,
    ArrayType,
)

try:
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
    from flight_pipeline.kpi.catalog import (
        KPI_VERSION,
        QUALITY_VERSION,
        UNIT_STATUS_PROVISIONAL,
        UNIT_STATUS_RESOLVED,
        UNIT_STATUS_ZERO_DENOMINATOR,
        UNIT_STATUS_COUNT_RECORDS,
        COVERAGE_PARTIAL,
        COVERAGE_VERIFIED_WITH_SCOPE,
        COVERAGE_UNKNOWN,
        CORE_KPI_DEFINITIONS,
        KPI_OUTPUT_COLUMNS,
        PERCENTILE_APPROX_ACCURACY,
    )
    from flight_pipeline.kpi.aggregators import evaluate_min_n
    from flight_pipeline.kpi.schema import KPI_OUTPUT_SCHEMA
except ModuleNotFoundError:
    from src.flight_pipeline.quality.predicates import (
        is_finite_numeric,
        is_valid_arr_delay,
        is_valid_dep_delay,
        is_valid_taxi_out,
        is_valid_taxi_in,
        is_valid_air_time,
        is_valid_actual_elapsed_time,
        is_valid_crs_elapsed_time,
    )
    from src.flight_pipeline.kpi.catalog import (
        KPI_VERSION,
        QUALITY_VERSION,
        UNIT_STATUS_PROVISIONAL,
        UNIT_STATUS_RESOLVED,
        UNIT_STATUS_ZERO_DENOMINATOR,
        UNIT_STATUS_COUNT_RECORDS,
        COVERAGE_PARTIAL,
        COVERAGE_VERIFIED_WITH_SCOPE,
        COVERAGE_UNKNOWN,
        CORE_KPI_DEFINITIONS,
        KPI_OUTPUT_COLUMNS,
        PERCENTILE_APPROX_ACCURACY,
    )
    from src.flight_pipeline.kpi.aggregators import evaluate_min_n
    from src.flight_pipeline.kpi.schema import KPI_OUTPUT_SCHEMA


class KpiCalculator:
    """
    Computes 8 CORE KPIs on accepted flight records.
    Produces standardized 17-field output DataFrames conforming to KPI_SPEC.md.
    """

    def __init__(
        self,
        run_id: str,
        kpi_version: str = KPI_VERSION,
        quality_version: str = QUALITY_VERSION,
    ):
        self.run_id = run_id
        self.kpi_version = kpi_version
        self.quality_version = quality_version

    def compute_kpis_for_cohort(
        self,
        df: DataFrame,
        source_year: str,
        dimension_type: str = "year",
        group_by_cols: Optional[List[str]] = None,
        filter_definition: str = "accepted_flights",
        source_coverage_status: Optional[str] = None,
        provenance_reference: str = "curated_accepted_dataset",
    ) -> DataFrame:
        """
        Compute all 8 CORE KPIs for a specified cohort and dimension.

        Parameters:
        - df: DataFrame of accepted flights (34 canonical columns or synthetic equivalent)
        - source_year: year string, e.g. "2016", "2024"
        - dimension_type: e.g. "year", "carrier-year", "airport-year", "route-year"
        - group_by_cols: list of group columns, e.g. ["OP_CARRIER"], ["ORIGIN"], ["ORIGIN", "DEST"]
        - filter_definition: description of filters applied
        - source_coverage_status: "VERIFIED_WITH_SCOPE", "PARTIAL" (for 2024), or "UNKNOWN"
        - provenance_reference: audit/evidence lineage pointer
        """
        # Enforce OR-05: 2024 source data is strictly PARTIAL coverage regardless of caller parameter
        if str(source_year).strip() == "2024":
            source_coverage_status = COVERAGE_PARTIAL
        elif source_coverage_status is None:
            source_coverage_status = COVERAGE_VERIFIED_WITH_SCOPE

        # Cohort validation: if FL_DATE is present, verify that records match source_year
        if "FL_DATE" in df.columns:
            mismatched_df = df.filter(
                F.col("FL_DATE").isNotNull()
                & (F.substring(F.trim(F.col("FL_DATE")), 1, 4) != str(source_year).strip())
            )
            if mismatched_df.limit(1).count() > 0:
                raise ValueError(
                    f"Cohort integrity violation: DataFrame contains FL_DATE records that do not match source_year='{source_year}'."
                )

        group_cols = group_by_cols or []

        # Build aggregation expressions with coalesce to guarantee non-null counts even on empty cohorts
        agg_exprs = [
            F.count(F.lit(1)).alias("_total_records"),
            # ARR_DELAY
            F.coalesce(F.sum(F.when(is_valid_arr_delay("ARR_DELAY"), 1).otherwise(0)), F.lit(0)).alias("_valid_arr_delay"),
            F.coalesce(
                F.sum(F.when(is_valid_arr_delay("ARR_DELAY") & (F.col("ARR_DELAY").cast(DoubleType()) >= 15.0), 1).otherwise(0)),
                F.lit(0),
            ).alias("_arr_delay_gte_15"),
            F.coalesce(
                F.sum(F.when(is_valid_arr_delay("ARR_DELAY"), F.col("ARR_DELAY").cast(DoubleType())).otherwise(0.0)),
                F.lit(0.0),
            ).alias("_sum_arr_delay"),
            F.percentile_approx(
                F.when(is_valid_arr_delay("ARR_DELAY"), F.col("ARR_DELAY").cast(DoubleType())),
                F.array(F.lit(0.5), F.lit(0.9)),
                F.lit(PERCENTILE_APPROX_ACCURACY),
            ).alias("_percentiles_arr_delay"),
            # DEP_DELAY
            F.coalesce(F.sum(F.when(is_valid_dep_delay("DEP_DELAY"), 1).otherwise(0)), F.lit(0)).alias("_valid_dep_delay"),
            F.coalesce(
                F.sum(F.when(is_valid_dep_delay("DEP_DELAY") & (F.col("DEP_DELAY").cast(DoubleType()) >= 15.0), 1).otherwise(0)),
                F.lit(0),
            ).alias("_dep_delay_gte_15"),
            F.coalesce(
                F.sum(F.when(is_valid_dep_delay("DEP_DELAY"), F.col("DEP_DELAY").cast(DoubleType())).otherwise(0.0)),
                F.lit(0.0),
            ).alias("_sum_dep_delay"),
            # TAXI_OUT & TAXI_IN (KPI-07)
            F.coalesce(F.sum(F.when(is_valid_taxi_out("TAXI_OUT"), 1).otherwise(0)), F.lit(0)).alias("_valid_taxi_out"),
            F.coalesce(
                F.sum(F.when(is_valid_taxi_out("TAXI_OUT"), F.col("TAXI_OUT").cast(DoubleType())).otherwise(0.0)),
                F.lit(0.0),
            ).alias("_sum_taxi_out"),
            F.coalesce(F.sum(F.when(is_valid_taxi_in("TAXI_IN"), 1).otherwise(0)), F.lit(0)).alias("_valid_taxi_in"),
            F.coalesce(
                F.sum(F.when(is_valid_taxi_in("TAXI_IN"), F.col("TAXI_IN").cast(DoubleType())).otherwise(0.0)),
                F.lit(0.0),
            ).alias("_sum_taxi_in"),
            # AIR_TIME, ACTUAL_ELAPSED_TIME, CRS_ELAPSED_TIME (KPI-08)
            F.coalesce(F.sum(F.when(is_valid_air_time("AIR_TIME"), 1).otherwise(0)), F.lit(0)).alias("_valid_air_time"),
            F.coalesce(
                F.sum(F.when(is_valid_air_time("AIR_TIME"), F.col("AIR_TIME").cast(DoubleType())).otherwise(0.0)),
                F.lit(0.0),
            ).alias("_sum_air_time"),
            F.coalesce(
                F.sum(F.when(is_valid_actual_elapsed_time("ACTUAL_ELAPSED_TIME"), 1).otherwise(0)),
                F.lit(0),
            ).alias("_valid_actual_elapsed"),
            F.coalesce(
                F.sum(F.when(is_valid_actual_elapsed_time("ACTUAL_ELAPSED_TIME"), F.col("ACTUAL_ELAPSED_TIME").cast(DoubleType())).otherwise(0.0)),
                F.lit(0.0),
            ).alias("_sum_actual_elapsed"),
            F.coalesce(F.sum(F.when(is_valid_crs_elapsed_time("CRS_ELAPSED_TIME"), 1).otherwise(0)), F.lit(0)).alias("_valid_crs_elapsed"),
            F.coalesce(
                F.sum(F.when(is_valid_crs_elapsed_time("CRS_ELAPSED_TIME"), F.col("CRS_ELAPSED_TIME").cast(DoubleType())).otherwise(0.0)),
                F.lit(0.0),
            ).alias("_sum_crs_elapsed"),
        ]

        if group_cols:
            grouped = df.groupBy(*group_cols).agg(*agg_exprs)
        else:
            grouped = df.agg(*agg_exprs)

        # Build group_dimensions string expression
        if group_cols:
            dim_parts = [F.concat(F.lit(f"{c}="), F.coalesce(F.col(c).cast(StringType()), F.lit("NULL"))) for c in group_cols]
            dim_parts.append(F.lit(f"source_year={source_year}"))
            group_dim_expr = F.concat_ws(";", *dim_parts)
        else:
            group_dim_expr = F.lit(f"cohort=all;source_year={source_year}")

        grouped = grouped.withColumn("_group_dimensions", group_dim_expr)

        # Now build individual KPI rows and union them
        kpi_dfs = []

        # KPI-01: Total accepted records
        kpi_dfs.append(
            self._make_kpi_row(
                grouped,
                kpi_id="KPI-01",
                submetric=None,
                source_year=source_year,
                filter_definition=filter_definition,
                source_coverage_status=source_coverage_status,
                provenance_reference=provenance_reference,
                count_records_col=F.col("_total_records"),
                count_valid_col=F.col("_total_records"),
                value_col=F.col("_total_records").cast(DoubleType()),
                unit_status_val=UNIT_STATUS_COUNT_RECORDS,
                dimension_type=dimension_type,
            )
        )

        # KPI-02: Arrival delay rate >= 15 min
        rate_kpi02 = F.when(
            F.col("_valid_arr_delay") > 0,
            F.col("_arr_delay_gte_15").cast(DoubleType()) / F.col("_valid_arr_delay").cast(DoubleType()),
        ).otherwise(F.lit(None).cast(DoubleType()))
        kpi_dfs.append(
            self._make_kpi_row(
                grouped,
                kpi_id="KPI-02",
                submetric=None,
                source_year=source_year,
                filter_definition=filter_definition,
                source_coverage_status=source_coverage_status,
                provenance_reference=provenance_reference,
                count_records_col=F.col("_total_records"),
                count_valid_col=F.col("_valid_arr_delay"),
                value_col=rate_kpi02,
                unit_status_val=UNIT_STATUS_RESOLVED,
                dimension_type=dimension_type,
            )
        )

        # KPI-03: Mean signed arrival delay
        mean_kpi03 = F.when(
            F.col("_valid_arr_delay") > 0,
            F.col("_sum_arr_delay") / F.col("_valid_arr_delay").cast(DoubleType()),
        ).otherwise(F.lit(None).cast(DoubleType()))
        kpi_dfs.append(
            self._make_kpi_row(
                grouped,
                kpi_id="KPI-03",
                submetric=None,
                source_year=source_year,
                filter_definition=filter_definition,
                source_coverage_status=source_coverage_status,
                provenance_reference=provenance_reference,
                count_records_col=F.col("_total_records"),
                count_valid_col=F.col("_valid_arr_delay"),
                value_col=mean_kpi03,
                unit_status_val=UNIT_STATUS_RESOLVED,
                dimension_type=dimension_type,
            )
        )

        # KPI-04: Departure delay rate >= 15 min
        rate_kpi04 = F.when(
            F.col("_valid_dep_delay") > 0,
            F.col("_dep_delay_gte_15").cast(DoubleType()) / F.col("_valid_dep_delay").cast(DoubleType()),
        ).otherwise(F.lit(None).cast(DoubleType()))
        kpi_dfs.append(
            self._make_kpi_row(
                grouped,
                kpi_id="KPI-04",
                submetric=None,
                source_year=source_year,
                filter_definition=filter_definition,
                source_coverage_status=source_coverage_status,
                provenance_reference=provenance_reference,
                count_records_col=F.col("_total_records"),
                count_valid_col=F.col("_valid_dep_delay"),
                value_col=rate_kpi04,
                unit_status_val=UNIT_STATUS_RESOLVED,
                dimension_type=dimension_type,
            )
        )

        # KPI-05: Mean signed departure delay
        mean_kpi05 = F.when(
            F.col("_valid_dep_delay") > 0,
            F.col("_sum_dep_delay") / F.col("_valid_dep_delay").cast(DoubleType()),
        ).otherwise(F.lit(None).cast(DoubleType()))
        kpi_dfs.append(
            self._make_kpi_row(
                grouped,
                kpi_id="KPI-05",
                submetric=None,
                source_year=source_year,
                filter_definition=filter_definition,
                source_coverage_status=source_coverage_status,
                provenance_reference=provenance_reference,
                count_records_col=F.col("_total_records"),
                count_valid_col=F.col("_valid_dep_delay"),
                value_col=mean_kpi05,
                unit_status_val=UNIT_STATUS_RESOLVED,
                dimension_type=dimension_type,
            )
        )

        # KPI-06: P50 arrival delay
        p50_kpi06 = F.when(
            F.col("_valid_arr_delay") > 0,
            F.col("_percentiles_arr_delay")[0].cast(DoubleType()),
        ).otherwise(F.lit(None).cast(DoubleType()))
        kpi_dfs.append(
            self._make_kpi_row(
                grouped,
                kpi_id="KPI-06",
                submetric="P50",
                source_year=source_year,
                filter_definition=filter_definition,
                source_coverage_status=source_coverage_status,
                provenance_reference=provenance_reference,
                count_records_col=F.col("_total_records"),
                count_valid_col=F.col("_valid_arr_delay"),
                value_col=p50_kpi06,
                unit_status_val=UNIT_STATUS_RESOLVED,
                dimension_type=dimension_type,
            )
        )

        # KPI-06: P90 arrival delay
        p90_kpi06 = F.when(
            F.col("_valid_arr_delay") > 0,
            F.col("_percentiles_arr_delay")[1].cast(DoubleType()),
        ).otherwise(F.lit(None).cast(DoubleType()))
        kpi_dfs.append(
            self._make_kpi_row(
                grouped,
                kpi_id="KPI-06",
                submetric="P90",
                source_year=source_year,
                filter_definition=filter_definition,
                source_coverage_status=source_coverage_status,
                provenance_reference=provenance_reference,
                count_records_col=F.col("_total_records"),
                count_valid_col=F.col("_valid_arr_delay"),
                value_col=p90_kpi06,
                unit_status_val=UNIT_STATUS_RESOLVED,
                dimension_type=dimension_type,
            )
        )

        # KPI-07 Submetric TAXI_OUT
        mean_taxi_out = F.when(
            F.col("_valid_taxi_out") > 0,
            F.col("_sum_taxi_out") / F.col("_valid_taxi_out").cast(DoubleType()),
        ).otherwise(F.lit(None).cast(DoubleType()))
        kpi_dfs.append(
            self._make_kpi_row(
                grouped,
                kpi_id="KPI-07",
                submetric="TAXI_OUT",
                source_year=source_year,
                filter_definition=filter_definition,
                source_coverage_status=source_coverage_status,
                provenance_reference=provenance_reference,
                count_records_col=F.col("_total_records"),
                count_valid_col=F.col("_valid_taxi_out"),
                value_col=mean_taxi_out,
                unit_status_val=UNIT_STATUS_RESOLVED,
                dimension_type=dimension_type,
            )
        )

        # KPI-07 Submetric TAXI_IN
        mean_taxi_in = F.when(
            F.col("_valid_taxi_in") > 0,
            F.col("_sum_taxi_in") / F.col("_valid_taxi_in").cast(DoubleType()),
        ).otherwise(F.lit(None).cast(DoubleType()))
        kpi_dfs.append(
            self._make_kpi_row(
                grouped,
                kpi_id="KPI-07",
                submetric="TAXI_IN",
                source_year=source_year,
                filter_definition=filter_definition,
                source_coverage_status=source_coverage_status,
                provenance_reference=provenance_reference,
                count_records_col=F.col("_total_records"),
                count_valid_col=F.col("_valid_taxi_in"),
                value_col=mean_taxi_in,
                unit_status_val=UNIT_STATUS_RESOLVED,
                dimension_type=dimension_type,
            )
        )

        # KPI-08 Submetric AIR_TIME
        mean_air_time = F.when(
            F.col("_valid_air_time") > 0,
            F.col("_sum_air_time") / F.col("_valid_air_time").cast(DoubleType()),
        ).otherwise(F.lit(None).cast(DoubleType()))
        kpi_dfs.append(
            self._make_kpi_row(
                grouped,
                kpi_id="KPI-08",
                submetric="AIR_TIME",
                source_year=source_year,
                filter_definition=filter_definition,
                source_coverage_status=source_coverage_status,
                provenance_reference=provenance_reference,
                count_records_col=F.col("_total_records"),
                count_valid_col=F.col("_valid_air_time"),
                value_col=mean_air_time,
                unit_status_val=UNIT_STATUS_RESOLVED,
                dimension_type=dimension_type,
            )
        )

        # KPI-08 Submetric ACTUAL_ELAPSED_TIME
        mean_actual_elapsed = F.when(
            F.col("_valid_actual_elapsed") > 0,
            F.col("_sum_actual_elapsed") / F.col("_valid_actual_elapsed").cast(DoubleType()),
        ).otherwise(F.lit(None).cast(DoubleType()))
        kpi_dfs.append(
            self._make_kpi_row(
                grouped,
                kpi_id="KPI-08",
                submetric="ACTUAL_ELAPSED_TIME",
                source_year=source_year,
                filter_definition=filter_definition,
                source_coverage_status=source_coverage_status,
                provenance_reference=provenance_reference,
                count_records_col=F.col("_total_records"),
                count_valid_col=F.col("_valid_actual_elapsed"),
                value_col=mean_actual_elapsed,
                unit_status_val=UNIT_STATUS_RESOLVED,
                dimension_type=dimension_type,
            )
        )

        # KPI-08 Submetric CRS_ELAPSED_TIME
        mean_crs_elapsed = F.when(
            F.col("_valid_crs_elapsed") > 0,
            F.col("_sum_crs_elapsed") / F.col("_valid_crs_elapsed").cast(DoubleType()),
        ).otherwise(F.lit(None).cast(DoubleType()))
        kpi_dfs.append(
            self._make_kpi_row(
                grouped,
                kpi_id="KPI-08",
                submetric="CRS_ELAPSED_TIME",
                source_year=source_year,
                filter_definition=filter_definition,
                source_coverage_status=source_coverage_status,
                provenance_reference=provenance_reference,
                count_records_col=F.col("_total_records"),
                count_valid_col=F.col("_valid_crs_elapsed"),
                value_col=mean_crs_elapsed,
                unit_status_val=UNIT_STATUS_RESOLVED,
                dimension_type=dimension_type,
            )
        )

        # Union all 12 KPI streams
        result_df = kpi_dfs[0]
        for next_df in kpi_dfs[1:]:
            result_df = result_df.unionByName(next_df)

        return result_df.select(*KPI_OUTPUT_COLUMNS)

    def _make_kpi_row(
        self,
        df: DataFrame,
        kpi_id: str,
        submetric: Optional[str],
        source_year: str,
        filter_definition: str,
        source_coverage_status: str,
        provenance_reference: str,
        count_records_col: Column,
        count_valid_col: Column,
        value_col: Column,
        unit_status_val: str,
        dimension_type: str,
    ) -> DataFrame:
        safe_count_records = F.coalesce(count_records_col, F.lit(0))
        safe_count_valid = F.coalesce(count_valid_col, F.lit(0))
        excluded_count_col = safe_count_records - safe_count_valid

        valid_rate_col = F.when(
            safe_count_records > 0,
            safe_count_valid.cast(DoubleType()) / safe_count_records.cast(DoubleType()),
        ).otherwise(F.lit(None).cast(DoubleType()))

        # If metric denominator is 0 and not KPI-01, set unit_status to ZERO_METRIC_DENOMINATOR
        if kpi_id == "KPI-01":
            final_unit_status_col = F.lit(unit_status_val)
        else:
            final_unit_status_col = F.when(
                safe_count_valid == 0,
                F.lit(UNIT_STATUS_ZERO_DENOMINATOR),
            ).otherwise(F.lit(unit_status_val))

        min_n_status_col = evaluate_min_n(safe_count_valid, dimension_type)

        return df.select(
            F.lit(kpi_id).cast(StringType()).alias("kpi_id"),
            F.lit(submetric).cast(StringType()).alias("submetric"),
            F.lit(self.run_id).cast(StringType()).alias("run_id"),
            F.lit(self.kpi_version).cast(StringType()).alias("kpi_version"),
            F.lit(str(source_year)).cast(StringType()).alias("source_year"),
            F.col("_group_dimensions").cast(StringType()).alias("group_dimensions"),
            F.lit(filter_definition).cast(StringType()).alias("filter_definition"),
            safe_count_records.cast(LongType()).alias("count_records"),
            safe_count_valid.cast(LongType()).alias("count_metric_valid"),
            excluded_count_col.cast(LongType()).alias("excluded_count"),
            valid_rate_col.cast(DoubleType()).alias("metric_valid_rate"),
            F.lit(source_coverage_status).cast(StringType()).alias("source_coverage_status"),
            value_col.cast(DoubleType()).alias("value"),
            final_unit_status_col.cast(StringType()).alias("unit_status"),
            min_n_status_col.cast(StringType()).alias("min_n_status"),
            F.lit(self.quality_version).cast(StringType()).alias("quality_version"),
            F.lit(provenance_reference).cast(StringType()).alias("provenance_reference"),
        )
