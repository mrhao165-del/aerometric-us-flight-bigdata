"""
KPI Analytics Transformations for Task T-014.
Transforms indexed KPI data into clean, reproducible analytical result tables.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Tuple


class KPIAnalyticsTransformer:
    """Produces standardized analytical result tables conforming to research questions."""

    def __init__(self, kpi_df: pd.DataFrame):
        self.df = kpi_df

    # -------------------------------------------------------------------------
    # RQ-01: Volume & Temporal Coverage
    # -------------------------------------------------------------------------
    def get_rq01_annual_volume_table(self) -> pd.DataFrame:
        """Annual accepted record volume, shares, and YoY growth (2016-2024)."""
        sub = self.df[(self.df["group_family"] == "year") & (self.df["kpi_id"] == "KPI-01")].copy()
        sub = sub.sort_values("entity_year").reset_index(drop=True)

        total_9yr = sub["value"].sum()
        sub["annual_volume"] = sub["value"].astype(int)
        sub["share_of_9yr_pct"] = (sub["annual_volume"] / total_9yr) * 100.0
        sub["yoy_growth_pct"] = sub["annual_volume"].pct_change() * 100.0

        cols = [
            "entity_year",
            "annual_volume",
            "share_of_9yr_pct",
            "yoy_growth_pct",
            "source_coverage_status",
            "count_records",
            "count_metric_valid",
        ]
        out = sub[cols].rename(columns={"entity_year": "year"})
        return out

    def get_rq01_monthly_volume_table(self) -> pd.DataFrame:
        """Monthly accepted record volume across 107 observed months."""
        sub = self.df[(self.df["group_family"] == "year-month") & (self.df["kpi_id"] == "KPI-01")].copy()
        sub = sub.sort_values("entity_year_month").reset_index(drop=True)

        sub["monthly_volume"] = sub["value"].astype(int)
        cols = [
            "entity_year",
            "entity_month",
            "entity_year_month",
            "monthly_volume",
            "source_coverage_status",
            "count_records",
        ]
        out = sub[cols].rename(
            columns={
                "entity_year": "year",
                "entity_month": "month",
                "entity_year_month": "year_month",
            }
        )
        return out

    # -------------------------------------------------------------------------
    # RQ-02: Arrival & Departure Delay Patterns
    # -------------------------------------------------------------------------
    def get_rq02_annual_delay_performance_table(self) -> pd.DataFrame:
        """Annual rates, signed means, and P50/P90 percentiles (2016-2024)."""
        sub = self.df[self.df["group_family"] == "year"].copy()

        pivot_val = sub.pivot(index="entity_year", columns=["kpi_id", "submetric"], values="value")
        pivot_records = sub.pivot(index="entity_year", columns=["kpi_id", "submetric"], values="count_records")

        records_col = pivot_records[("KPI-01", None)]

        records = []
        for year in sorted(sub["entity_year"].unique()):
            row = {
                "year": int(year),
                "total_records": int(records_col.loc[year]),
                "arr_delay_ge_15_rate_pct": float(pivot_val.loc[year, ("KPI-02", None)] * 100.0),
                "arr_delay_signed_mean_min": float(pivot_val.loc[year, ("KPI-03", None)]),
                "dep_delay_ge_15_rate_pct": float(pivot_val.loc[year, ("KPI-04", None)] * 100.0),
                "dep_delay_signed_mean_min": float(pivot_val.loc[year, ("KPI-05", None)]),
                "arr_delay_p50_min": float(pivot_val.loc[year, ("KPI-06", "P50")]),
                "arr_delay_p90_min": float(pivot_val.loc[year, ("KPI-06", "P90")]),
            }
            records.append(row)

        return pd.DataFrame(records)

    def get_rq02_monthly_delay_performance_table(self) -> pd.DataFrame:
        """Monthly delay rates and signed means across 107 observed months."""
        sub = self.df[self.df["group_family"] == "year-month"].copy()

        pivot_val = sub.pivot(index="entity_year_month", columns=["kpi_id", "submetric"], values="value")
        pivot_cov = sub.pivot(index="entity_year_month", columns=["kpi_id", "submetric"], values="source_coverage_status")

        records = []
        for ym in sorted(sub["entity_year_month"].dropna().unique()):
            row = {
                "year_month": ym,
                "year": int(ym.split("-")[0]),
                "month": int(ym.split("-")[1]),
                "flight_volume": int(pivot_val.loc[ym, ("KPI-01", None)]),
                "arr_delay_ge_15_rate_pct": float(pivot_val.loc[ym, ("KPI-02", None)] * 100.0),
                "arr_delay_signed_mean_min": float(pivot_val.loc[ym, ("KPI-03", None)]),
                "dep_delay_ge_15_rate_pct": float(pivot_val.loc[ym, ("KPI-04", None)] * 100.0),
                "dep_delay_signed_mean_min": float(pivot_val.loc[ym, ("KPI-05", None)]),
                "source_coverage_status": str(pivot_cov.loc[ym, ("KPI-01", None)]),
            }
            records.append(row)

        return pd.DataFrame(records)

    # -------------------------------------------------------------------------
    # RQ-03: Carrier, Airport & Directed Route Differences
    # -------------------------------------------------------------------------
    def get_rq03_carrier_performance_table(self) -> pd.DataFrame:
        """Carrier-year performance metrics for all 140 carrier cohorts."""
        sub = self.df[self.df["group_family"] == "carrier-year"].copy()

        pivot_val = sub.pivot(index=["entity_carrier", "entity_year"], columns=["kpi_id", "submetric"], values="value")
        pivot_status = sub.pivot(index=["entity_carrier", "entity_year"], columns=["kpi_id", "submetric"], values="min_n_status")
        pivot_valid = sub.pivot(index=["entity_carrier", "entity_year"], columns=["kpi_id", "submetric"], values="count_metric_valid")

        records = []
        for carrier, year in pivot_val.index:
            records.append({
                "carrier": carrier,
                "year": int(year),
                "volume": int(pivot_val.loc[(carrier, year), ("KPI-01", None)]),
                "count_metric_valid_arr_delay": int(pivot_valid.loc[(carrier, year), ("KPI-02", None)]),
                "arr_delay_ge_15_rate_pct": float(pivot_val.loc[(carrier, year), ("KPI-02", None)] * 100.0),
                "on_time_arr_rate_pct": float((1.0 - pivot_val.loc[(carrier, year), ("KPI-02", None)]) * 100.0),
                "arr_delay_signed_mean_min": float(pivot_val.loc[(carrier, year), ("KPI-03", None)]),
                "dep_delay_ge_15_rate_pct": float(pivot_val.loc[(carrier, year), ("KPI-04", None)] * 100.0),
                "dep_delay_signed_mean_min": float(pivot_val.loc[(carrier, year), ("KPI-05", None)]),
                "taxi_out_mean_min": float(pivot_val.loc[(carrier, year), ("KPI-07", "TAXI_OUT")]),
                "min_n_status": str(pivot_status.loc[(carrier, year), ("KPI-01", None)]),
            })

        out = pd.DataFrame(records).sort_values(["year", "volume"], ascending=[True, False]).reset_index(drop=True)
        return out

    def get_rq03_top_carriers_summary(self, top_n: int = 10) -> pd.DataFrame:
        """
        Top carriers aggregated across the 9-year dataset by total observed volume.
        Uses valid-denominator weighting for all pooled delay rates and signed means.
        """
        sub = self.df[self.df["group_family"] == "carrier-year"].copy()

        # 1. Total volume & active years from KPI-01
        vol_sub = sub[(sub["kpi_id"] == "KPI-01") & (sub["submetric"].isna())]
        carrier_vol = vol_sub.groupby("entity_carrier").agg(
            total_volume=("value", "sum"),
            years_active=("entity_year", "nunique"),
        )

        # 2. Weighted Arr Delay Rate from KPI-02
        kpi02 = sub[(sub["kpi_id"] == "KPI-02") & (sub["submetric"].isna())].copy()
        kpi02["weighted_val"] = kpi02["value"] * kpi02["count_metric_valid"]
        kpi02_agg = kpi02.groupby("entity_carrier").agg(
            sum_weighted=("weighted_val", "sum"),
            sum_valid=("count_metric_valid", "sum"),
        )
        kpi02_agg["pooled_arr_delay_rate"] = kpi02_agg["sum_weighted"] / kpi02_agg["sum_valid"]
        kpi02_agg["mean_on_time_arr_rate_pct"] = (1.0 - kpi02_agg["pooled_arr_delay_rate"]) * 100.0
        kpi02_agg["pooled_arr_delay_rate_pct"] = kpi02_agg["pooled_arr_delay_rate"] * 100.0

        # 3. Weighted Arr Delay Signed Mean from KPI-03
        kpi03 = sub[(sub["kpi_id"] == "KPI-03") & (sub["submetric"].isna())].copy()
        kpi03["weighted_val"] = kpi03["value"] * kpi03["count_metric_valid"]
        kpi03_agg = kpi03.groupby("entity_carrier").agg(
            sum_weighted=("weighted_val", "sum"),
            sum_valid=("count_metric_valid", "sum"),
        )
        kpi03_agg["mean_arr_delay_signed"] = kpi03_agg["sum_weighted"] / kpi03_agg["sum_valid"]

        # 4. Weighted Dep Delay Rate from KPI-04
        kpi04 = sub[(sub["kpi_id"] == "KPI-04") & (sub["submetric"].isna())].copy()
        kpi04["weighted_val"] = kpi04["value"] * kpi04["count_metric_valid"]
        kpi04_agg = kpi04.groupby("entity_carrier").agg(
            sum_weighted=("weighted_val", "sum"),
            sum_valid=("count_metric_valid", "sum"),
        )
        kpi04_agg["pooled_dep_delay_rate_pct"] = (kpi04_agg["sum_weighted"] / kpi04_agg["sum_valid"]) * 100.0

        # 5. Weighted Dep Delay Signed Mean from KPI-05
        kpi05 = sub[(sub["kpi_id"] == "KPI-05") & (sub["submetric"].isna())].copy()
        kpi05["weighted_val"] = kpi05["value"] * kpi05["count_metric_valid"]
        kpi05_agg = kpi05.groupby("entity_carrier").agg(
            sum_weighted=("weighted_val", "sum"),
            sum_valid=("count_metric_valid", "sum"),
        )
        kpi05_agg["mean_dep_delay_signed"] = kpi05_agg["sum_weighted"] / kpi05_agg["sum_valid"]

        # 6. Weighted Taxi-Out from KPI-07 TAXI_OUT
        kpi07 = sub[(sub["kpi_id"] == "KPI-07") & (sub["submetric"] == "TAXI_OUT")].copy()
        kpi07["weighted_val"] = kpi07["value"] * kpi07["count_metric_valid"]
        kpi07_agg = kpi07.groupby("entity_carrier").agg(
            sum_weighted=("weighted_val", "sum"),
            sum_valid=("count_metric_valid", "sum"),
        )
        kpi07_agg["mean_taxi_out"] = kpi07_agg["sum_weighted"] / kpi07_agg["sum_valid"]

        # Combine all carrier metrics
        combined = carrier_vol.join([
            kpi02_agg[["mean_on_time_arr_rate_pct", "pooled_arr_delay_rate_pct"]],
            kpi03_agg[["mean_arr_delay_signed"]],
            kpi04_agg[["pooled_dep_delay_rate_pct"]],
            kpi05_agg[["mean_dep_delay_signed"]],
            kpi07_agg[["mean_taxi_out"]],
        ]).reset_index().rename(columns={"entity_carrier": "carrier"})

        combined["total_volume"] = combined["total_volume"].astype(int)
        combined["years_active"] = combined["years_active"].astype(int)

        # Sort by total volume descending and take top_n
        top = combined.sort_values("total_volume", ascending=False).head(top_n).reset_index(drop=True)
        return top

    def get_rq02_monthly_pooled_seasonality_table(self) -> pd.DataFrame:
        """
        Pooled monthly delay rates and volumes across all 9 observed years (12 calendar months).
        Uses valid-denominator weighting: sum(rate * count_valid) / sum(count_valid).
        """
        sub = self.df[self.df["group_family"] == "year-month"].copy()

        # Volume per month across years
        vol_sub = sub[(sub["kpi_id"] == "KPI-01") & (sub["submetric"].isna())]
        m_vol = vol_sub.groupby("entity_month")["value"].sum().astype(int)

        # Delay rate per month across years
        kpi02 = sub[(sub["kpi_id"] == "KPI-02") & (sub["submetric"].isna())].copy()
        kpi02["weighted_val"] = kpi02["value"] * kpi02["count_metric_valid"]
        kpi02_agg = kpi02.groupby("entity_month").agg(
            sum_weighted=("weighted_val", "sum"),
            sum_valid=("count_metric_valid", "sum"),
        )
        kpi02_agg["pooled_arr_delay_rate_pct"] = (kpi02_agg["sum_weighted"] / kpi02_agg["sum_valid"]) * 100.0

        # Signed mean arr delay
        kpi03 = sub[(sub["kpi_id"] == "KPI-03") & (sub["submetric"].isna())].copy()
        kpi03["weighted_val"] = kpi03["value"] * kpi03["count_metric_valid"]
        kpi03_agg = kpi03.groupby("entity_month").agg(
            sum_weighted=("weighted_val", "sum"),
            sum_valid=("count_metric_valid", "sum"),
        )
        kpi03_agg["pooled_arr_delay_signed_mean_min"] = kpi03_agg["sum_weighted"] / kpi03_agg["sum_valid"]

        out = pd.DataFrame({
            "month": list(range(1, 13)),
            "month_label": [f"T{m}" for m in range(1, 13)],
            "pooled_volume": [int(m_vol.get(m, 0)) for m in range(1, 13)],
            "pooled_arr_delay_rate_pct": [float(kpi02_agg.loc[m, "pooled_arr_delay_rate_pct"]) if m in kpi02_agg.index else 0.0 for m in range(1, 13)],
            "pooled_arr_delay_signed_mean_min": [float(kpi03_agg.loc[m, "pooled_arr_delay_signed_mean_min"]) if m in kpi03_agg.index else 0.0 for m in range(1, 13)],
        })
        return out

    def get_rq03_origin_airport_performance_table(self, min_sample: int = 365) -> pd.DataFrame:
        """Origin airport annual performance for eligible hubs (min-N >= 365 and SUFFICIENT status)."""
        sub = self.df[self.df["group_family"] == "origin-year"].copy()

        pivot_val = sub.pivot(index=["entity_origin", "entity_year"], columns=["kpi_id", "submetric"], values="value")
        pivot_status = sub.pivot(index=["entity_origin", "entity_year"], columns=["kpi_id", "submetric"], values="min_n_status")

        records = []
        for origin, year in pivot_val.index:
            vol = int(pivot_val.loc[(origin, year), ("KPI-01", None)])
            status_kpi01 = str(pivot_status.loc[(origin, year), ("KPI-01", None)])
            status_kpi04 = str(pivot_status.loc[(origin, year), ("KPI-04", None)])
            status_kpi05 = str(pivot_status.loc[(origin, year), ("KPI-05", None)])
            status_kpi07 = str(pivot_status.loc[(origin, year), ("KPI-07", "TAXI_OUT")])

            if (
                status_kpi01 == "SUFFICIENT"
                and status_kpi04 == "SUFFICIENT"
                and status_kpi05 == "SUFFICIENT"
                and status_kpi07 == "SUFFICIENT"
                and vol >= min_sample
            ):
                records.append({
                    "origin_airport": origin,
                    "year": int(year),
                    "volume": vol,
                    "dep_delay_ge_15_rate_pct": float(pivot_val.loc[(origin, year), ("KPI-04", None)] * 100.0),
                    "dep_delay_signed_mean_min": float(pivot_val.loc[(origin, year), ("KPI-05", None)]),
                    "taxi_out_mean_min": float(pivot_val.loc[(origin, year), ("KPI-07", "TAXI_OUT")]),
                    "min_n_status": status_kpi01,
                })

        out = pd.DataFrame(records).sort_values(["year", "volume"], ascending=[True, False]).reset_index(drop=True)
        return out

    def get_rq03_dest_airport_performance_table(self, min_sample: int = 365) -> pd.DataFrame:
        """Destination airport annual performance for eligible hubs (min-N >= 365 and SUFFICIENT status)."""
        sub = self.df[self.df["group_family"] == "dest-year"].copy()

        pivot_val = sub.pivot(index=["entity_dest", "entity_year"], columns=["kpi_id", "submetric"], values="value")
        pivot_status = sub.pivot(index=["entity_dest", "entity_year"], columns=["kpi_id", "submetric"], values="min_n_status")

        records = []
        for dest, year in pivot_val.index:
            vol = int(pivot_val.loc[(dest, year), ("KPI-01", None)])
            status_kpi01 = str(pivot_status.loc[(dest, year), ("KPI-01", None)])
            status_kpi02 = str(pivot_status.loc[(dest, year), ("KPI-02", None)])
            status_kpi03 = str(pivot_status.loc[(dest, year), ("KPI-03", None)])
            status_kpi07 = str(pivot_status.loc[(dest, year), ("KPI-07", "TAXI_IN")])

            if (
                status_kpi01 == "SUFFICIENT"
                and status_kpi02 == "SUFFICIENT"
                and status_kpi03 == "SUFFICIENT"
                and status_kpi07 == "SUFFICIENT"
                and vol >= min_sample
            ):
                records.append({
                    "dest_airport": dest,
                    "year": int(year),
                    "volume": vol,
                    "arr_delay_ge_15_rate_pct": float(pivot_val.loc[(dest, year), ("KPI-02", None)] * 100.0),
                    "arr_delay_signed_mean_min": float(pivot_val.loc[(dest, year), ("KPI-03", None)]),
                    "taxi_in_mean_min": float(pivot_val.loc[(dest, year), ("KPI-07", "TAXI_IN")]),
                    "min_n_status": status_kpi01,
                })

        out = pd.DataFrame(records).sort_values(["year", "volume"], ascending=[True, False]).reset_index(drop=True)
        return out

    def get_rq03_directed_route_asymmetry_table(self, year: int = 2019, top_n_pairs: int = 10) -> pd.DataFrame:
        """Asymmetric comparison of bidirectional directed routes (A->B vs. B->A) for top pairs."""
        sub = self.df[(self.df["group_family"] == "route-year") & (self.df["entity_year"] == year)].copy()

        pivot_val = sub.pivot(index=["entity_origin", "entity_dest"], columns=["kpi_id", "submetric"], values="value")
        pivot_status = sub.pivot(index=["entity_origin", "entity_dest"], columns=["kpi_id", "submetric"], values="min_n_status")

        pairs_processed = set()
        records = []

        for orig, dest in pivot_val.index:
            if (dest, orig) in pivot_val.index:
                pair_key = tuple(sorted([orig, dest]))
                if pair_key in pairs_processed:
                    continue
                pairs_processed.add(pair_key)

                # Forward
                fwd_vol = int(pivot_val.loc[(orig, dest), ("KPI-01", None)])
                fwd_arr_rate = float(pivot_val.loc[(orig, dest), ("KPI-02", None)] * 100.0)
                fwd_arr_mean = float(pivot_val.loc[(orig, dest), ("KPI-03", None)])
                fwd_status_kpi01 = str(pivot_status.loc[(orig, dest), ("KPI-01", None)])
                fwd_status_kpi02 = str(pivot_status.loc[(orig, dest), ("KPI-02", None)])
                fwd_status_kpi03 = str(pivot_status.loc[(orig, dest), ("KPI-03", None)])

                # Return
                ret_vol = int(pivot_val.loc[(dest, orig), ("KPI-01", None)])
                ret_arr_rate = float(pivot_val.loc[(dest, orig), ("KPI-02", None)] * 100.0)
                ret_arr_mean = float(pivot_val.loc[(dest, orig), ("KPI-03", None)])
                ret_status_kpi01 = str(pivot_status.loc[(dest, orig), ("KPI-01", None)])
                ret_status_kpi02 = str(pivot_status.loc[(dest, orig), ("KPI-02", None)])
                ret_status_kpi03 = str(pivot_status.loc[(dest, orig), ("KPI-03", None)])

                if (
                    fwd_status_kpi01 == "SUFFICIENT"
                    and fwd_status_kpi02 == "SUFFICIENT"
                    and fwd_status_kpi03 == "SUFFICIENT"
                    and ret_status_kpi01 == "SUFFICIENT"
                    and ret_status_kpi02 == "SUFFICIENT"
                    and ret_status_kpi03 == "SUFFICIENT"
                ):
                    records.append({
                        "year": year,
                        "city_pair": f"{pair_key[0]} <-> {pair_key[1]}",
                        "route_fwd": f"{orig} -> {dest}",
                        "volume_fwd": fwd_vol,
                        "arr_delay_rate_fwd_pct": fwd_arr_rate,
                        "arr_delay_mean_fwd_min": fwd_arr_mean,
                        "route_ret": f"{dest} -> {orig}",
                        "volume_ret": ret_vol,
                        "arr_delay_rate_ret_pct": ret_arr_rate,
                        "arr_delay_mean_ret_min": ret_arr_mean,
                        "delay_rate_diff_pct": abs(fwd_arr_rate - ret_arr_rate),
                        "mean_delay_diff_min": abs(fwd_arr_mean - ret_arr_mean),
                        "total_pair_volume": fwd_vol + ret_vol,
                    })

        out = pd.DataFrame(records).sort_values("total_pair_volume", ascending=False).head(top_n_pairs).reset_index(drop=True)
        return out

    # -------------------------------------------------------------------------
    # RQ-04: Pandemic Shock & Structural Shift (2019 - 2021)
    # -------------------------------------------------------------------------
    def get_rq04_pandemic_comparison_table(self) -> pd.DataFrame:
        """Side-by-side comparison of 2019, 2020, and 2021 across all core measures."""
        annual_df = self.get_rq02_annual_delay_performance_table()
        taxi_df = self.get_rq05_annual_journey_times_table()

        merged = pd.merge(
            annual_df,
            taxi_df[[
                "year",
                "taxi_out_mean_min",
                "taxi_in_mean_min",
                "air_time_mean_min",
                "actual_elapsed_mean_min",
                "crs_elapsed_mean_min",
            ]],
            on="year",
        )
        pandemic_sub = merged[merged["year"].isin([2019, 2020, 2021])].copy()
        # Preserve year both as an explicit column for CSV serialization and as DataFrame index
        pandemic_sub = pandemic_sub.set_index("year", drop=False)
        return pandemic_sub

    # -------------------------------------------------------------------------
    # RQ-05: Taxi & Journey Time Performance
    # -------------------------------------------------------------------------
    def get_rq05_annual_journey_times_table(self) -> pd.DataFrame:
        """Annual mean taxi and elapsed times (2016-2024)."""
        sub = self.df[self.df["group_family"] == "year"].copy()

        pivot_val = sub.pivot(index="entity_year", columns=["kpi_id", "submetric"], values="value")

        records = []
        for year in sorted(sub["entity_year"].unique()):
            taxi_out = float(pivot_val.loc[year, ("KPI-07", "TAXI_OUT")])
            taxi_in = float(pivot_val.loc[year, ("KPI-07", "TAXI_IN")])
            air_time = float(pivot_val.loc[year, ("KPI-08", "AIR_TIME")])
            actual_elapsed = float(pivot_val.loc[year, ("KPI-08", "ACTUAL_ELAPSED_TIME")])
            crs_elapsed = float(pivot_val.loc[year, ("KPI-08", "CRS_ELAPSED_TIME")])
            schedule_buffer = crs_elapsed - actual_elapsed

            records.append({
                "year": int(year),
                "taxi_out_mean_min": taxi_out,
                "taxi_in_mean_min": taxi_in,
                "air_time_mean_min": air_time,
                "actual_elapsed_mean_min": actual_elapsed,
                "crs_elapsed_mean_min": crs_elapsed,
                "schedule_buffer_mean_min": schedule_buffer,
            })

        return pd.DataFrame(records)

    def get_rq05_airport_taxi_congestion_table(self, year: int = 2023, top_n: int = 10) -> pd.DataFrame:
        """Top airports with highest taxi-out congestion for a given benchmark year."""
        sub = self.df[(self.df["group_family"] == "origin-year") & (self.df["entity_year"] == year)].copy()

        pivot_val = sub.pivot(index="entity_origin", columns=["kpi_id", "submetric"], values="value")
        pivot_status = sub.pivot(index="entity_origin", columns=["kpi_id", "submetric"], values="min_n_status")

        records = []
        for origin in pivot_val.index:
            vol = int(pivot_val.loc[origin, ("KPI-01", None)])
            status_kpi01 = str(pivot_status.loc[origin, ("KPI-01", None)])
            status_kpi07 = str(pivot_status.loc[origin, ("KPI-07", "TAXI_OUT")])
            if status_kpi01 == "SUFFICIENT" and status_kpi07 == "SUFFICIENT" and vol >= 365:
                records.append({
                    "origin_airport": origin,
                    "year": int(year),
                    "volume": vol,
                    "taxi_out_mean_min": float(pivot_val.loc[origin, ("KPI-07", "TAXI_OUT")]),
                })

        out = pd.DataFrame(records).sort_values("taxi_out_mean_min", ascending=False).head(top_n).reset_index(drop=True)
        return out
