"""
Visualization Generator for Task T-014.
Produces publication-quality Matplotlib figures covering RQ-01 through RQ-05.
"""

import os
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import seaborn as sns
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional

# Style and typography configuration
plt.rcParams["font.sans-serif"] = ["DejaVu Sans", "Arial", "Helvetica"]
plt.rcParams["axes.edgecolor"] = "#cccccc"
plt.rcParams["axes.linewidth"] = 0.8
plt.rcParams["grid.color"] = "#e5e5e5"
plt.rcParams["grid.linestyle"] = "--"
plt.rcParams["grid.alpha"] = 0.7


class KPIVisualizer:
    """Generates standardized, reproducible publication figures."""

    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        self.chart_inventory: List[Dict[str, Any]] = []

    def _save_figure(
        self,
        fig: plt.Figure,
        chart_id: str,
        title: str,
        res_id: str,
        supporting_res_ids: Optional[List[str]] = None,
        rq_id: Optional[str] = None,
        kpi_id: Optional[str] = None,
        cohort_family: Optional[str] = None,
        table_reference: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Saves figure in both PNG (300 DPI) and SVG formats, recording inventory metadata."""
        png_path = os.path.join(self.output_dir, f"{chart_id}.png")
        svg_path = os.path.join(self.output_dir, f"{chart_id}.svg")

        fig.savefig(png_path, dpi=300, bbox_inches="tight")
        fig.savefig(svg_path, format="svg", bbox_inches="tight")
        plt.close(fig)

        meta = {
            "chart_id": chart_id,
            "title_vi": title,
            "res_id": res_id,
            "supporting_res_ids": supporting_res_ids or [res_id],
            "rq_id": rq_id,
            "kpi_id": kpi_id,
            "cohort_family": cohort_family,
            "table_reference": table_reference,
            "png_file": f"{chart_id}.png",
            "svg_file": f"{chart_id}.svg",
            "png_bytes": os.path.getsize(png_path),
            "svg_bytes": os.path.getsize(svg_path),
        }
        self.chart_inventory.append(meta)
        return meta

    # -------------------------------------------------------------------------
    # RQ-01: Volume & Temporal Distribution
    # -------------------------------------------------------------------------
    def plot_rq01_01_annual_volume(self, df_annual: pd.DataFrame) -> Dict[str, Any]:
        fig, ax = plt.subplots(figsize=(10, 5.5))
        years = df_annual["year"]
        vols_m = df_annual["annual_volume"] / 1e6

        colors = ["#2b5c8f" if y != 2024 else "#e67e22" for y in years]
        bars = ax.bar(years, vols_m, color=colors, width=0.65, zorder=3)

        ax.grid(axis="y", zorder=0)
        ax.set_title("Quy mô Dữ liệu Quan sát Hàng năm (2016–2024)", fontsize=13, fontweight="bold", pad=15)
        ax.set_xlabel("Năm Quan sát", fontsize=11, labelpad=10)
        ax.set_ylabel("Số lượng Bản ghi Chặng bay (Triệu lượt)", fontsize=11, labelpad=10)
        ax.set_ylim(0, 8.5)

        for bar, y, vol in zip(bars, years, df_annual["annual_volume"]):
            h = bar.get_height()
            label = f"{vol/1e6:.2f}M"
            if y == 2024:
                label += "\n(PARTIAL)"
            ax.annotate(
                label,
                xy=(bar.get_x() + bar.get_width() / 2, h),
                xytext=(0, 4),
                textcoords="offset points",
                ha="center",
                va="bottom",
                fontsize=9,
                fontweight="bold" if y in (2019, 2020, 2024) else "normal",
            )

        ax.text(
            0.02,
            0.92,
            "Nguồn: T-013 kpi_run_2016_2024_v1 [RES-001, RES-020]\nLưu ý: Năm 2024 khuyết toàn bộ Tháng 3 (335 ngày, OR-05, coverage PARTIAL).",
            transform=ax.transAxes,
            fontsize=8.5,
            bbox=dict(boxstyle="round,pad=0.4", facecolor="#f8f9fa", edgecolor="#cccccc"),
        )
        return self._save_figure(
            fig,
            "CHART_RQ01_01_annual_accepted_volume",
            "Quy mô Dữ liệu Quan sát Hàng năm (2016–2024)",
            "RES-001",
            supporting_res_ids=["RES-001", "RES-020"],
            rq_id="RQ-01",
            kpi_id="KPI-01",
            cohort_family="year",
            table_reference="rq01_annual_volume.parquet",
        )

    def plot_rq01_02_monthly_volume_trend(self, df_monthly: pd.DataFrame) -> Dict[str, Any]:
        fig, ax = plt.subplots(figsize=(12, 5.5))

        # Re-index to ensure March 2024 is visible as gap
        all_months = []
        for y in range(2016, 2025):
            for m in range(1, 13):
                all_months.append(f"{y}-{m:02d}")

        df_full = pd.DataFrame({"year_month": all_months})
        df_full = df_full.merge(df_monthly, on="year_month", how="left")

        x = np.arange(len(df_full))
        y_vals = df_full["monthly_volume"] / 1e3

        ax.plot(x, y_vals, color="#2b5c8f", linewidth=1.8, marker="o", markersize=3, zorder=3, label="Sản lượng hàng tháng")

        # Mark 2020 drop
        apr_2020_idx = all_months.index("2020-04")
        ax.annotate(
            "Đáy đại dịch (T4/2020):\n180K chuyến",
            xy=(apr_2020_idx, y_vals.iloc[apr_2020_idx]),
            xytext=(apr_2020_idx + 3, 300),
            arrowprops=dict(facecolor="#e74c3c", shrink=0.05, width=1, headwidth=5),
            fontsize=8.5,
            color="#c0392b",
            fontweight="bold",
        )

        # Mark missing 2024-03
        mar_2024_idx = all_months.index("2024-03")
        ax.axvline(mar_2024_idx, color="#d35400", linestyle="--", linewidth=1.2, zorder=2)
        ax.annotate(
            "Khuyết T3/2024 (OR-05)",
            xy=(mar_2024_idx, 50),
            xytext=(mar_2024_idx - 15, 100),
            arrowprops=dict(facecolor="#d35400", shrink=0.05, width=1, headwidth=5),
            fontsize=8.5,
            color="#d35400",
            fontweight="bold",
        )

        ax.grid(True, zorder=0)
        ax.set_title("Chuỗi Thời gian Lưu lượng Chặng bay Quan sát Hàng tháng (2016–2024)", fontsize=13, fontweight="bold", pad=15)
        ax.set_ylabel("Số lượng Bản ghi (Nghìn lượt)", fontsize=11)
        ax.set_xlabel("Năm và Tháng", fontsize=11)

        # Year tick marks
        year_ticks = [i for i, ym in enumerate(all_months) if ym.endswith("-01")]
        year_labels = [ym.split("-")[0] for ym in all_months if ym.endswith("-01")]
        ax.set_xticks(year_ticks)
        ax.set_xticklabels(year_labels)

        ax.text(
            0.02,
            0.08,
            "Nguồn: T-013 KPI-01 [RES-002, RES-003]. Đỉnh tháng 7 xuất hiện trong 6/9 năm (2016-2018, 2021-2022, 2024); tháng 3/2024 được giữ trống (OR-05).",
            transform=ax.transAxes,
            fontsize=8.5,
            bbox=dict(boxstyle="round,pad=0.4", facecolor="#f8f9fa", edgecolor="#cccccc"),
        )
        return self._save_figure(
            fig,
            "CHART_RQ01_02_monthly_volume_trend",
            "Chuỗi Thời gian Lưu lượng Chặng bay Hàng tháng (2016–2024)",
            "RES-002",
            supporting_res_ids=["RES-002", "RES-003"],
            rq_id="RQ-01",
            kpi_id="KPI-01",
            cohort_family="year-month",
            table_reference="rq01_monthly_volume.parquet",
        )

    def plot_rq01_03_year_month_heatmap(self, df_monthly: pd.DataFrame) -> Dict[str, Any]:
        fig, ax = plt.subplots(figsize=(11, 6))

        # Pivot Year x Month
        grid = np.full((9, 12), np.nan)
        years = list(range(2016, 2025))
        for _, row in df_monthly.iterrows():
            y_idx = years.index(int(row["year"]))
            m_idx = int(row["month"]) - 1
            grid[y_idx, m_idx] = row["monthly_volume"] / 1e3

        sns.heatmap(
            grid,
            annot=True,
            fmt=".0f",
            cmap="YlGnBu",
            cbar_kws={"label": "Nghìn bản ghi"},
            xticklabels=[f"T{m}" for m in range(1, 13)],
            yticklabels=years,
            ax=ax,
            mask=np.isnan(grid),
            linewidths=0.5,
            linecolor="white",
        )

        # Highlight missing 2024-03
        ax.add_patch(plt.Rectangle((2, 8), 1, 1, fill=True, facecolor="#ffcccc", hatch="//", edgecolor="#d9534f"))
        ax.text(2.5, 8.5, "MISSING\n(OR-05)", ha="center", va="center", fontsize=7.5, color="#c0392b", fontweight="bold")

        ax.set_title("Bản Đồ Nhiệt Mật Độ Sản Lượng Chuyến Bay theo Tháng & Năm (2016–2024)", fontsize=13, fontweight="bold", pad=15)
        ax.set_xlabel("Tháng trong Năm", fontsize=11)
        ax.set_ylabel("Năm Quan sát", fontsize=11)
        return self._save_figure(
            fig,
            "CHART_RQ01_03_year_month_volume_heatmap",
            "Bản Đồ Nhiệt Phân Bố Sản Lượng theo Tháng & Năm",
            "RES-002",
            supporting_res_ids=["RES-002", "RES-003"],
            rq_id="RQ-01",
            kpi_id="KPI-01",
            cohort_family="year-month",
            table_reference="rq01_monthly_volume.parquet",
        )

    # -------------------------------------------------------------------------
    # RQ-02: Delay Distributions, Means & Percentiles
    # -------------------------------------------------------------------------
    def plot_rq02_01_delay_rates(self, df_annual_delay: pd.DataFrame) -> Dict[str, Any]:
        fig, ax = plt.subplots(figsize=(10, 5.5))
        years = df_annual_delay["year"]

        ax.plot(years, df_annual_delay["arr_delay_ge_15_rate_pct"], marker="o", color="#c0392b", linewidth=2.2, label="Tỷ lệ Trễ Đến (ARR_DELAY >= 15m)")
        ax.plot(years, df_annual_delay["dep_delay_ge_15_rate_pct"], marker="s", color="#2980b9", linewidth=2.0, linestyle="--", label="Tỷ lệ Trễ Khởi hành (DEP_DELAY >= 15m)")

        ax.grid(True, zorder=0)
        ax.set_title("Tỷ Lệ Chuyến Bay Chậm Trễ Hàng Năm (2016–2024, Ngưỡng >= 15 Phút)", fontsize=13, fontweight="bold", pad=15)
        ax.set_xlabel("Năm Quan sát", fontsize=11)
        ax.set_ylabel("Tỷ lệ Trễ (%)", fontsize=11)
        ax.set_ylim(5, 25)
        ax.yaxis.set_major_formatter(ticker.PercentFormatter(decimals=0))

        for _, row in df_annual_delay.iterrows():
            ax.annotate(f"{row['arr_delay_ge_15_rate_pct']:.1f}%", (row["year"], row["arr_delay_ge_15_rate_pct"]), textcoords="offset points", xytext=(0, 5), ha="center", fontsize=8.5, color="#c0392b", fontweight="bold")
            ax.annotate(f"{row['dep_delay_ge_15_rate_pct']:.1f}%", (row["year"], row["dep_delay_ge_15_rate_pct"]), textcoords="offset points", xytext=(0, -12), ha="center", fontsize=8.5, color="#2980b9")

        ax.legend(loc="upper left", frameon=True)
        ax.text(
            0.02,
            0.15,
            "Nguồn: T-013 KPI-02 & KPI-04 [RES-004, RES-014]. Ngưỡng trễ >= 15 phút. Năm 2020 đạt mức thấp kỷ lục (9.73%), tái tắc nghẽn năm 2022 (20.99%).",
            transform=ax.transAxes,
            fontsize=8.5,
            bbox=dict(boxstyle="round,pad=0.4", facecolor="#f8f9fa", edgecolor="#cccccc"),
        )
        return self._save_figure(
            fig,
            "CHART_RQ02_01_arrival_departure_delay_rate_trend",
            "Tỷ Lệ Chuyến Bay Chậm Trễ Hàng Năm (2016–2024)",
            "RES-004",
            supporting_res_ids=["RES-004", "RES-014"],
            rq_id="RQ-02",
            kpi_id="KPI-02, KPI-04",
            cohort_family="year",
            table_reference="rq02_annual_delays.parquet",
        )

    def plot_rq02_02_signed_means(self, df_annual_delay: pd.DataFrame) -> Dict[str, Any]:
        fig, ax = plt.subplots(figsize=(10, 5.5))
        years = df_annual_delay["year"]

        ax.plot(years, df_annual_delay["arr_delay_signed_mean_min"], marker="o", color="#c0392b", linewidth=2.2, label="Độ Trễ Đến Trung Bình Có Dấu (ARR_DELAY, phút)")
        ax.plot(years, df_annual_delay["dep_delay_signed_mean_min"], marker="s", color="#2980b9", linewidth=2.0, linestyle="--", label="Độ Trễ Khởi Hành Trung Bình Có Dấu (DEP_DELAY, phút)")
        ax.axhline(0, color="#888888", linestyle="-", linewidth=0.8)

        ax.grid(True, zorder=0)
        ax.set_title("Độ Trễ Trung Bình Có Dấu Toàn Quốc Hàng Năm (2016–2024)", fontsize=13, fontweight="bold", pad=15)
        ax.set_xlabel("Năm Quan sát", fontsize=11)
        ax.set_ylabel("Số Phút Trễ Trung Bình (Phút)", fontsize=11)
        ax.set_ylim(-7, 16)  # Expanded y-limits to accommodate -5.11m comfortably

        for _, row in df_annual_delay.iterrows():
            ax.annotate(f"{row['arr_delay_signed_mean_min']:.1f}", (row["year"], row["arr_delay_signed_mean_min"]), textcoords="offset points", xytext=(0, 6 if row['arr_delay_signed_mean_min']>=0 else -14), ha="center", fontsize=8.5, color="#c0392b", fontweight="bold")
            ax.annotate(f"{row['dep_delay_signed_mean_min']:.1f}", (row["year"], row["dep_delay_signed_mean_min"]), textcoords="offset points", xytext=(0, 6), ha="center", fontsize=8.5, color="#2980b9")

        ax.legend(loc="upper left", frameon=True)
        ax.text(
            0.02,
            0.65,
            "Nguồn: T-013 KPI-03 & KPI-05 [RES-005].\nGiá trị âm năm 2020 (-5.11 phút) phản ánh trung bình các chuyến bay đến sớm hơn lịch trình; tăng mạnh lên +6.93m (2022) và +7.11m (2024).",
            transform=ax.transAxes,
            fontsize=8.5,
            bbox=dict(boxstyle="round,pad=0.4", facecolor="#f8f9fa", edgecolor="#cccccc"),
        )
        return self._save_figure(
            fig,
            "CHART_RQ02_02_signed_mean_arrival_departure_delays",
            "Độ Trễ Trung Bình Có Dấu Hàng năm (2016–2024)",
            "RES-005",
            supporting_res_ids=["RES-005"],
            rq_id="RQ-02",
            kpi_id="KPI-03, KPI-05",
            cohort_family="year",
            table_reference="rq02_annual_delays.parquet",
        )

    def plot_rq02_03_percentiles(self, df_annual_delay: pd.DataFrame) -> Dict[str, Any]:
        fig, ax = plt.subplots(figsize=(10, 5.5))
        years = df_annual_delay["year"]

        ax.plot(years, df_annual_delay["arr_delay_p90_min"], marker="D", color="#8e44ad", linewidth=2.2, label="Phân vị 90 (P90, trễ nặng)")
        ax.plot(years, df_annual_delay["arr_delay_p50_min"], marker="o", color="#27ae60", linewidth=2.0, linestyle="--", label="Trung vị (P50, điển hình)")
        ax.axhline(0, color="#888888", linestyle=":", linewidth=0.8)

        ax.grid(True, zorder=0)
        ax.set_title("Tính Bất Đối Xứng Phân Phối Trễ: Trung Vị (P50) vs Phân Vị 90 (P90) Đến", fontsize=13, fontweight="bold", pad=15)
        ax.set_xlabel("Năm Quan sát", fontsize=11)
        ax.set_ylabel("Số Phút Trễ (Phút)", fontsize=11)
        ax.set_ylim(-15, 50)  # Expanded y-limits to display P50 (-11.0m) and P90 (+42.0m) cleanly

        for _, row in df_annual_delay.iterrows():
            ax.annotate(f"{row['arr_delay_p90_min']:.0f}m", (row["year"], row["arr_delay_p90_min"]), textcoords="offset points", xytext=(0, 5), ha="center", fontsize=8.5, color="#8e44ad", fontweight="bold")
            ax.annotate(f"{row['arr_delay_p50_min']:.0f}m", (row["year"], row["arr_delay_p50_min"]), textcoords="offset points", xytext=(0, -13), ha="center", fontsize=8.5, color="#27ae60", fontweight="bold")

        ax.legend(loc="center right", frameon=True)
        ax.text(
            0.02,
            0.75,
            "Nguồn: T-013 KPI-06 [RES-006, RES-007].\nP50 luôn âm (-5 đến -11 phút, năm 2020: -11.0m) cho thấy >50% chuyến bay đến sớm;\ngánh nặng trễ tập trung cao độ ở phân vị trên (P90 từ +14.0m năm 2020 đến +42.0m năm 2022 và +43.0m năm 2024).",
            transform=ax.transAxes,
            fontsize=8.5,
            bbox=dict(boxstyle="round,pad=0.4", facecolor="#f8f9fa", edgecolor="#cccccc"),
        )
        return self._save_figure(
            fig,
            "CHART_RQ02_03_arrival_delay_percentiles_p50_p90",
            "Tính Bất Đối Xứng Phân Phối Trễ: P50 vs P90 Đến",
            "RES-006",
            supporting_res_ids=["RES-006", "RES-007"],
            rq_id="RQ-02",
            kpi_id="KPI-06",
            cohort_family="year",
            table_reference="rq02_annual_delays.parquet",
        )

    def plot_rq02_04_monthly_seasonality(self, df_monthly_input: pd.DataFrame) -> Dict[str, Any]:
        fig, ax = plt.subplots(figsize=(10, 5))
        # Support either precomputed pooled table or monthly delay table with volume weighting
        if "pooled_arr_delay_rate_pct" in df_monthly_input.columns:
            monthly_rates = df_monthly_input["pooled_arr_delay_rate_pct"].values
        elif "flight_volume" in df_monthly_input.columns and "arr_delay_ge_15_rate_pct" in df_monthly_input.columns:
            # Weighted average across observed years
            w_num = (df_monthly_input["arr_delay_ge_15_rate_pct"] * df_monthly_input["flight_volume"]).groupby(df_monthly_input["month"]).sum()
            w_den = df_monthly_input["flight_volume"].groupby(df_monthly_input["month"]).sum()
            monthly_rates = (w_num / w_den).values
        else:
            monthly_rates = df_monthly_input.groupby("month")["arr_delay_ge_15_rate_pct"].mean().values

        months = [f"T{m}" for m in range(1, 13)]
        bars = ax.bar(months, monthly_rates, color="#34495e", width=0.6, zorder=3)

        # Highlight summer surge (June-July)
        bars[5].set_color("#e74c3c")  # June
        bars[6].set_color("#e74c3c")  # July

        ax.grid(axis="y", zorder=0)
        ax.set_title("Tính Mùa Vụ Của Tỷ Lệ Trễ Đến Hàng Tháng (Gộp Trọng Số 2016–2024)", fontsize=13, fontweight="bold", pad=15)
        ax.set_xlabel("Tháng trong Năm", fontsize=11)
        ax.set_ylabel("Tỷ lệ Trễ Đến Gộp (>=15 phút, %)", fontsize=11)
        ax.set_ylim(0, 26)
        ax.yaxis.set_major_formatter(ticker.PercentFormatter(decimals=0))

        for i, val in enumerate(monthly_rates):
            ax.annotate(f"{val:.1f}%", (i, val), textcoords="offset points", xytext=(0, 4), ha="center", fontsize=8.5)

        ax.text(
            0.02,
            0.88,
            "Nguồn: T-013 KPI-02 [RES-004]. Tỷ lệ gộp có trọng số mẫu hợp lệ (valid-denominator weighted rate).\nMùa hè (T6-T7) và mùa đông (T12) ghi nhận tỷ lệ trễ đến cao nhất.",
            transform=ax.transAxes,
            fontsize=8.5,
            bbox=dict(boxstyle="round,pad=0.4", facecolor="#f8f9fa", edgecolor="#cccccc"),
        )
        return self._save_figure(
            fig,
            "CHART_RQ02_04_monthly_arrival_delay_rate_seasonality",
            "Tính Mùa vụ Tỷ lệ Trễ Đến (2016–2024)",
            "RES-004",
            supporting_res_ids=["RES-004"],
            rq_id="RQ-02",
            kpi_id="KPI-02",
            cohort_family="year-month",
            table_reference="rq02_monthly_delays.parquet",
        )

    # -------------------------------------------------------------------------
    # RQ-03: Carriers, Airports & Directed Routes
    # -------------------------------------------------------------------------
    def plot_rq03_01_top_carriers_punctuality(self, df_top_carriers: pd.DataFrame) -> Dict[str, Any]:
        fig, ax = plt.subplots(figsize=(10, 6))
        carriers = df_top_carriers["carrier"]
        rates = df_top_carriers["mean_on_time_arr_rate_pct"]

        y_pos = np.arange(len(carriers))
        bars = ax.barh(y_pos, rates, color="#2980b9", height=0.6, zorder=3)
        ax.set_yticks(y_pos)
        ax.set_yticklabels([f"{c} (N={v/1e6:.2f}M)" for c, v in zip(carriers, df_top_carriers["total_volume"])])
        ax.invert_yaxis()  # Top carrier at top

        ax.grid(axis="x", zorder=0)
        ax.set_title("Tỷ lệ Đến Đúng Giờ Gộp theo Trọng số của Top 10 Hãng Hàng không (2016–2024)", fontsize=13, fontweight="bold", pad=15)
        ax.set_xlabel("Tỷ lệ Đến Đúng Giờ (<15 phút trễ, %)", fontsize=11)
        ax.set_xlim(65, 95)
        ax.xaxis.set_major_formatter(ticker.PercentFormatter(decimals=0))

        for bar, val in zip(bars, rates):
            w = bar.get_width()
            ax.annotate(f"{val:.1f}%", xy=(w, bar.get_y() + bar.get_height() / 2), xytext=(5, 0), textcoords="offset points", ha="left", va="center", fontsize=9, fontweight="bold")

        ax.text(
            0.02,
            0.05,
            "Nguồn: T-013 KPI-01 & KPI-02 [RES-008, RES-009]. Tỷ lệ gộp có trọng số mẫu hợp lệ. WN dẫn đầu sản lượng (11.13M, đúng giờ 80.67%); DL đạt tỷ lệ đúng giờ cao nhất (85.81%, N=7.82M).",
            transform=ax.transAxes,
            fontsize=8.5,
            bbox=dict(boxstyle="round,pad=0.4", facecolor="#f8f9fa", edgecolor="#cccccc"),
        )
        return self._save_figure(
            fig,
            "CHART_RQ03_01_top_carriers_on_time_performance",
            "Tỷ lệ Đến Đúng Giờ Top 10 Hãng Hàng không (2016–2024)",
            "RES-008",
            supporting_res_ids=["RES-008", "RES-009"],
            rq_id="RQ-03",
            kpi_id="KPI-01, KPI-02",
            cohort_family="carrier-year",
            table_reference="rq03_top_carriers.parquet",
        )

    def plot_rq03_02_top_carriers_mean_delays(self, df_top_carriers: pd.DataFrame) -> Dict[str, Any]:
        fig, ax = plt.subplots(figsize=(10, 5.5))
        top_8 = df_top_carriers.head(8)
        carriers = top_8["carrier"]
        arr_delay = top_8["mean_arr_delay_signed"]
        dep_delay = top_8["mean_dep_delay_signed"]

        x = np.arange(len(carriers))
        w = 0.35

        ax.bar(x - w / 2, arr_delay, width=w, color="#c0392b", label="Trễ Đến Trung bình (ARR_DELAY, phút)", zorder=3)
        ax.bar(x + w / 2, dep_delay, width=w, color="#2980b9", label="Trễ Khởi hành Trung bình (DEP_DELAY, phút)", zorder=3)

        ax.set_xticks(x)
        ax.set_xticklabels([f"{c}\n({v/1e6:.1f}M)" for c, v in zip(carriers, top_8["total_volume"])])
        ax.grid(axis="y", zorder=0)

        ax.set_title("Độ Trễ Trung Bình Có Dấu (Đến vs Khởi Hành) theo Hãng Hàng Không", fontsize=13, fontweight="bold", pad=15)
        ax.set_ylabel("Số Phút Trễ Trung Bình (Phút)", fontsize=11)
        ax.legend(loc="upper right")

        ax.text(
            0.02,
            0.88,
            "Nguồn: T-013 KPI-03 & KPI-05 [RES-008, RES-009]. Trễ trung bình có dấu tính theo trọng số mẫu hợp lệ (DL: trễ đến TB +0.66m; WN: +3.85m; AA: +7.00m).",
            transform=ax.transAxes,
            fontsize=8.5,
            bbox=dict(boxstyle="round,pad=0.4", facecolor="#f8f9fa", edgecolor="#cccccc"),
        )
        return self._save_figure(
            fig,
            "CHART_RQ03_02_top_carriers_mean_delays",
            "Độ Trễ Trung Bình theo Hãng Hàng Không (2016–2024)",
            "RES-009",
            supporting_res_ids=["RES-008", "RES-009"],
            rq_id="RQ-03",
            kpi_id="KPI-03, KPI-05",
            cohort_family="carrier-year",
            table_reference="rq03_top_carriers.parquet",
        )

    def plot_rq03_03_top_origin_airports(self, df_origin: pd.DataFrame) -> Dict[str, Any]:
        fig, ax = plt.subplots(figsize=(10, 6))
        # Top 10 by departure delay rate in recent normal year (2023)
        sub = df_origin[df_origin["year"] == 2023].sort_values("dep_delay_ge_15_rate_pct", ascending=False).head(10)

        airports = sub["origin_airport"]
        rates = sub["dep_delay_ge_15_rate_pct"]

        y_pos = np.arange(len(airports))
        bars = ax.barh(y_pos, rates, color="#d35400", height=0.6, zorder=3)
        ax.set_yticks(y_pos)
        ax.set_yticklabels([f"{apt} (N={v:,})" for apt, v in zip(airports, sub["volume"])])
        ax.invert_yaxis()

        ax.grid(axis="x", zorder=0)
        ax.set_title("Top 10 Sân Bay Có Tỷ Lệ Trễ Khởi Hành Cao Nhất (Năm 2023, N >= 365)", fontsize=13, fontweight="bold", pad=15)
        ax.set_xlabel("Tỷ lệ Trễ Khởi hành (>=15 phút, %)", fontsize=11)
        ax.set_xlim(15, 32)
        ax.xaxis.set_major_formatter(ticker.PercentFormatter(decimals=0))

        for bar, val in zip(bars, rates):
            w = bar.get_width()
            ax.annotate(f"{val:.1f}%", xy=(w, bar.get_y() + bar.get_height() / 2), xytext=(5, 0), textcoords="offset points", ha="left", va="center", fontsize=9, fontweight="bold")

        ax.text(
            0.02,
            0.05,
            "Nguồn: T-013 KPI-04 [RES-010]. Top sân bay xuất phát trễ cao nhất (EWR đạt 27.67% năm 2022, LGA 22.63% năm 2019, ORD 22.48% năm 2024; lọc SUFFICIENT N >= 365).",
            transform=ax.transAxes,
            fontsize=8.5,
            bbox=dict(boxstyle="round,pad=0.4", facecolor="#f8f9fa", edgecolor="#cccccc"),
        )
        return self._save_figure(
            fig,
            "CHART_RQ03_03_top_origin_airports_departure_delays",
            "Top 10 Sân Bay Tỷ Lệ Trễ Khởi Hành Cao Nhất (2023)",
            "RES-010",
            supporting_res_ids=["RES-010"],
            rq_id="RQ-03",
            kpi_id="KPI-04",
            cohort_family="origin-year",
            table_reference="rq03_origin_airports.parquet",
        )

    def plot_rq03_04_directed_routes(self, df_routes: pd.DataFrame) -> Dict[str, Any]:
        fig, ax = plt.subplots(figsize=(11, 5.5))
        top_5 = df_routes.head(5)
        x = np.arange(len(top_5))
        w = 0.35

        fwd_rates = top_5["arr_delay_rate_fwd_pct"]
        ret_rates = top_5["arr_delay_rate_ret_pct"]

        ax.bar(x - w / 2, fwd_rates, width=w, color="#16a085", label="Chiều đi (Forward)", zorder=3)
        ax.bar(x + w / 2, ret_rates, width=w, color="#d35400", label="Chiều về (Return)", zorder=3)

        ax.set_xticks(x)
        labels = [f"{r['route_fwd']}\nvs {r['route_ret']}" for _, r in top_5.iterrows()]
        ax.set_xticklabels(labels, fontsize=9)
        ax.grid(axis="y", zorder=0)

        ax.set_title("Tính Bất Đối Xứng Tỷ Lệ Trễ Đến Giữa Hai Chiều của Tuyến Bay (Năm 2019)", fontsize=13, fontweight="bold", pad=15)
        ax.set_ylabel("Tỷ lệ Trễ Đến >= 15 phút (%)", fontsize=11)
        ax.yaxis.set_major_formatter(ticker.PercentFormatter(decimals=0))
        ax.legend(loc="upper right")

        for i, (_, row) in enumerate(top_5.iterrows()):
            ax.annotate(f"{row['arr_delay_rate_fwd_pct']:.1f}%", (i - w / 2, row['arr_delay_rate_fwd_pct']), textcoords="offset points", xytext=(0, 3), ha="center", fontsize=8)
            ax.annotate(f"{row['arr_delay_rate_ret_pct']:.1f}%", (i + w / 2, row['arr_delay_rate_ret_pct']), textcoords="offset points", xytext=(0, 3), ha="center", fontsize=8)

        ax.text(
            0.02,
            0.88,
            "Nguồn: T-013 KPI-02 & KPI-03 [RES-011]. Min-N >= 100 chuyến mỗi chiều. Năm 2019: LGA <-> ORD chênh lệch 2.82% (ORD->LGA 31.42% vs LGA->ORD 28.60%, N=28,277); LAX <-> SFO chênh lệch 2.46%, N=28,174.",
            transform=ax.transAxes,
            fontsize=8.5,
            bbox=dict(boxstyle="round,pad=0.4", facecolor="#f8f9fa", edgecolor="#cccccc"),
        )
        return self._save_figure(
            fig,
            "CHART_RQ03_04_directed_route_delay_asymmetry",
            "Tính Bất Đối Xứng Tỷ Lệ Trễ Tuyến Bay Có Hướng",
            "RES-011",
            supporting_res_ids=["RES-011"],
            rq_id="RQ-03",
            kpi_id="KPI-02, KPI-03",
            cohort_family="route-year",
            table_reference="rq03_directed_routes.parquet",
        )

    # -------------------------------------------------------------------------
    # RQ-04: Pandemic Shock (2019-2021)
    # -------------------------------------------------------------------------
    def plot_rq04_01_pandemic_comparison(self, df_pandemic: pd.DataFrame) -> Dict[str, Any]:
        fig, axes = plt.subplots(1, 4, figsize=(14, 4.5))

        years = ["2019", "2020", "2021"]
        colors = ["#2b5c8f", "#e74c3c", "#27ae60"]

        # Panel 1: Volume
        vols = [df_pandemic.loc[int(y), "total_records"] / 1e6 for y in years]
        axes[0].bar(years, vols, color=colors, width=0.6, zorder=3)
        axes[0].set_title("Lưu lượng (Triệu lượt)", fontsize=10, fontweight="bold")
        axes[0].set_ylabel("Triệu chuyến bay")
        axes[0].grid(axis="y", zorder=0)
        for i, v in enumerate(vols):
            axes[0].annotate(f"{v:.2f}M", (i, v), textcoords="offset points", xytext=(0, 3), ha="center", fontsize=8.5, fontweight="bold")

        # Panel 2: Delay rate
        rates = [df_pandemic.loc[int(y), "arr_delay_ge_15_rate_pct"] for y in years]
        axes[1].bar(years, rates, color=colors, width=0.6, zorder=3)
        axes[1].set_title("Tỷ lệ Trễ Đến (%)", fontsize=10, fontweight="bold")
        axes[1].grid(axis="y", zorder=0)
        axes[1].yaxis.set_major_formatter(ticker.PercentFormatter(decimals=0))
        for i, r in enumerate(rates):
            axes[1].annotate(f"{r:.1f}%", (i, r), textcoords="offset points", xytext=(0, 3), ha="center", fontsize=8.5, fontweight="bold")

        # Panel 3: Signed mean delay
        means = [df_pandemic.loc[int(y), "arr_delay_signed_mean_min"] for y in years]
        axes[2].bar(years, means, color=colors, width=0.6, zorder=3)
        axes[2].axhline(0, color="#888888", linestyle="-", linewidth=0.8)
        axes[2].set_title("Trễ Đến TB (Phút)", fontsize=10, fontweight="bold")
        axes[2].grid(axis="y", zorder=0)
        for i, m in enumerate(means):
            axes[2].annotate(f"{m:.2f}m", (i, m), textcoords="offset points", xytext=(0, 3 if m>=0 else -12), ha="center", fontsize=8.5, fontweight="bold")

        # Panel 4: Taxi out mean
        taxi = [df_pandemic.loc[int(y), "taxi_out_mean_min"] for y in years]
        axes[3].bar(years, taxi, color=colors, width=0.6, zorder=3)
        axes[3].set_title("Taxi-Out TB (Phút)", fontsize=10, fontweight="bold")
        axes[3].grid(axis="y", zorder=0)
        for i, t in enumerate(taxi):
            axes[3].annotate(f"{t:.1f}m", (i, t), textcoords="offset points", xytext=(0, 3), ha="center", fontsize=8.5, fontweight="bold")

        fig.suptitle("So sánh Các Chỉ Số Hiệu Suất Cốt Lõi: Trước, Trong và Sau Năm 2020", fontsize=12, fontweight="bold", y=1.03)
        plt.tight_layout()
        return self._save_figure(
            fig,
            "CHART_RQ04_01_pandemic_period_kpi_comparison",
            "So sánh Các Chỉ Số Hiệu Suất Giai đoạn 2019–2021",
            "RES-012",
            supporting_res_ids=["RES-012", "RES-014"],
            rq_id="RQ-04",
            kpi_id="KPI-01, KPI-02",
            cohort_family="year",
            table_reference="rq04_pandemic_comparison.parquet",
        )

    def plot_rq04_02_pandemic_monthly(self, df_monthly: pd.DataFrame) -> Dict[str, Any]:
        fig, ax1 = plt.subplots(figsize=(11, 5))
        sub = df_monthly[df_monthly["year"].isin([2019, 2020, 2021])].sort_values("year_month").reset_index(drop=True)

        x = np.arange(len(sub))
        vol_col = "flight_volume" if "flight_volume" in sub.columns else "monthly_volume"
        ax1.bar(x, sub[vol_col] / 1e3, color="#bdc3c7", alpha=0.7, width=0.6, zorder=2, label="Lưu lượng (nghìn lượt)")
        ax1.set_ylabel("Lưu lượng (Nghìn bản ghi)", color="#7f8c8d", fontsize=10)
        ax1.set_ylim(0, 750)

        ax2 = ax1.twinx()
        # On time rate = 100 - arr_delay_rate
        on_time = 100.0 - sub["arr_delay_ge_15_rate_pct"]
        ax2.plot(x, on_time, color="#27ae60", marker="o", linewidth=2.0, zorder=3, label="Tỷ lệ Đến Đúng Giờ (%)")
        ax2.set_ylabel("Tỷ lệ Đến Đúng Giờ (%)", color="#27ae60", fontsize=10)
        ax2.set_ylim(60, 100)
        ax2.yaxis.set_major_formatter(ticker.PercentFormatter(decimals=0))

        ax1.set_xticks(x[::2])
        ax1.set_xticklabels(sub["year_month"].iloc[::2], rotation=45, ha="right", fontsize=8.5)
        ax1.grid(axis="x", zorder=0)

        # Annotate April 2020
        idx_apr = sub[sub["year_month"] == "2020-04"].index[0]
        ax1.annotate(
            "T4/2020:\n180K lượt\nĐúng giờ: 95.1%",
            xy=(idx_apr, 180),
            xytext=(idx_apr + 1, 350),
            arrowprops=dict(facecolor="#c0392b", shrink=0.05, width=1, headwidth=5),
            fontsize=8.5,
            fontweight="bold",
            color="#c0392b",
        )

        ax1.set_title("Cú Sốc Đại Dịch và Xu Hướng Phục Hồi Hàng Tháng (2019–2021)", fontsize=13, fontweight="bold", pad=15)
        return self._save_figure(
            fig,
            "CHART_RQ04_02_2020_monthly_shock_and_rebound",
            "Cú Sốc Đại Dịch và Xu Hướng Phục Hồi (2019–2021)",
            "RES-013",
            supporting_res_ids=["RES-003", "RES-013"],
            rq_id="RQ-04",
            kpi_id="KPI-01, KPI-02",
            cohort_family="year-month",
            table_reference="rq02_monthly_delays.parquet",
        )

    # -------------------------------------------------------------------------
    # RQ-05: Taxi & Journey Times
    # -------------------------------------------------------------------------
    def plot_rq05_01_annual_taxi(self, df_taxi: pd.DataFrame) -> Dict[str, Any]:
        fig, ax = plt.subplots(figsize=(10, 5))
        years = df_taxi["year"]

        ax.plot(years, df_taxi["taxi_out_mean_min"], marker="s", color="#e67e22", linewidth=2.2, label="Taxi-Out Trung bình (KPI-07, khởi hành -> cất cánh)")
        ax.plot(years, df_taxi["taxi_in_mean_min"], marker="o", color="#16a085", linewidth=2.0, linestyle="--", label="Taxi-In Trung bình (KPI-07, hạ cánh -> cập cổng)")

        ax.grid(True, zorder=0)
        ax.set_title("Thời Gian Lăn Bánh (Taxi Time) Bình Quân Toàn Quốc Hàng Năm", fontsize=13, fontweight="bold", pad=15)
        ax.set_xlabel("Năm Quan sát", fontsize=11)
        ax.set_ylabel("Thời gian (Phút)", fontsize=11)
        ax.set_ylim(5, 22)

        for _, row in df_taxi.iterrows():
            ax.annotate(f"{row['taxi_out_mean_min']:.1f}m", (row["year"], row["taxi_out_mean_min"]), textcoords="offset points", xytext=(0, 5), ha="center", fontsize=8.5, color="#d35400", fontweight="bold")
            ax.annotate(f"{row['taxi_in_mean_min']:.1f}m", (row["year"], row["taxi_in_mean_min"]), textcoords="offset points", xytext=(0, -12), ha="center", fontsize=8.5, color="#16a085")

        ax.legend(loc="center right")
        ax.text(
            0.02,
            0.12,
            "Nguồn: T-013 KPI-07 [RES-015, RES-016]. Taxi-out giảm xuống 15.25 phút và Taxi-in giảm xuống 7.15 phút năm 2020 do mật độ sân bay giảm; Taxi-out tăng lên 17.95m năm 2024.",
            transform=ax.transAxes,
            fontsize=8.5,
            bbox=dict(boxstyle="round,pad=0.4", facecolor="#f8f9fa", edgecolor="#cccccc"),
        )
        return self._save_figure(
            fig,
            "CHART_RQ05_01_annual_taxi_time_trends",
            "Xu Hướng Thời Gian Lăn (Taxi Time) Hàng Năm (2016–2024)",
            "RES-015",
            supporting_res_ids=["RES-015", "RES-016"],
            rq_id="RQ-05",
            kpi_id="KPI-07",
            cohort_family="year",
            table_reference="rq05_annual_journey_times.parquet",
        )

    def plot_rq05_02_elapsed_times(self, df_taxi: pd.DataFrame) -> Dict[str, Any]:
        fig, ax = plt.subplots(figsize=(10, 5.5))
        years = df_taxi["year"]

        ax.plot(years, df_taxi["crs_elapsed_mean_min"], marker="^", color="#2c3e50", linewidth=2.0, linestyle=":", label="Thời gian Hành trình Lịch trình (CRS_ELAPSED, phút)")
        ax.plot(years, df_taxi["actual_elapsed_mean_min"], marker="s", color="#2980b9", linewidth=2.2, label="Thời gian Hành trình Thực tế (ACTUAL_ELAPSED, phút)")
        ax.plot(years, df_taxi["air_time_mean_min"], marker="o", color="#27ae60", linewidth=1.8, linestyle="--", label="Thời gian Bay Trên Không (AIR_TIME, phút)")

        # Fill schedule buffer
        ax.fill_between(years, df_taxi["actual_elapsed_mean_min"], df_taxi["crs_elapsed_mean_min"], color="#bdc3c7", alpha=0.4, label="Đệm Lịch trình (Schedule Buffer)")

        ax.grid(True, zorder=0)
        ax.set_title("Thời Gian Hành Trình và Đệm Lịch Trình (Schedule Padding) Hàng Năm", fontsize=13, fontweight="bold", pad=15)
        ax.set_xlabel("Năm Quan sát", fontsize=11)
        ax.set_ylabel("Thời gian (Phút)", fontsize=11)
        ax.set_ylim(100, 160)

        ax.legend(loc="upper right")
        ax.text(
            0.02,
            0.12,
            "Nguồn: T-013 KPI-08 [RES-018, RES-019].\nChênh lệch giữa hai giá trị trung bình đã công bố (Difference of Published Means: CRS Elapsed TB - Actual Elapsed TB) dao động từ +4.87 đến +7.08m, không cấu thành chứng minh nhân quả về chiến lược đệm lịch trình.",
            transform=ax.transAxes,
            fontsize=8.5,
            bbox=dict(boxstyle="round,pad=0.4", facecolor="#f8f9fa", edgecolor="#cccccc"),
        )
        return self._save_figure(
            fig,
            "CHART_RQ05_02_elapsed_time_and_schedule_buffer",
            "Thời Gian Hành Trình và Đệm Lịch Trình (2016–2024)",
            "RES-018",
            supporting_res_ids=["RES-018", "RES-019"],
            rq_id="RQ-05",
            kpi_id="KPI-08",
            cohort_family="year",
            table_reference="rq05_annual_journey_times.parquet",
        )

    def plot_rq05_03_airport_taxi_congestion(self, df_airport_taxi: pd.DataFrame) -> Dict[str, Any]:
        fig, ax = plt.subplots(figsize=(10, 5.5))
        airports = df_airport_taxi["origin_airport"]
        taxi_out = df_airport_taxi["taxi_out_mean_min"]

        y_pos = np.arange(len(airports))
        bars = ax.barh(y_pos, taxi_out, color="#d35400", height=0.6, zorder=3)
        ax.set_yticks(y_pos)
        ax.set_yticklabels([f"{apt} (N={v:,})" for apt, v in zip(airports, df_airport_taxi["volume"])])
        ax.invert_yaxis()

        ax.grid(axis="x", zorder=0)
        ax.set_title("Top 10 Sân Bay Có Thời Gian Taxi-Out Dài Nhất (Năm 2023, N >= 365)", fontsize=13, fontweight="bold", pad=15)
        ax.set_xlabel("Thời gian Taxi-Out Trung bình (Phút)", fontsize=11)
        ax.set_xlim(15, 30)

        for bar, val in zip(bars, taxi_out):
            w = bar.get_width()
            ax.annotate(f"{val:.1f}m", xy=(w, bar.get_y() + bar.get_height() / 2), xytext=(5, 0), textcoords="offset points", ha="left", va="center", fontsize=9, fontweight="bold")

        ax.text(
            0.02,
            0.05,
            "Nguồn: T-013 KPI-07 [RES-017]. JFK dẫn đầu Taxi-Out bình quân năm 2023 với 26.21 phút (N=129,620); EWR 23.76m, LGA 23.58m, ORD 22.45m; lọc SUFFICIENT N >= 365.",
            transform=ax.transAxes,
            fontsize=8.5,
            bbox=dict(boxstyle="round,pad=0.4", facecolor="#f8f9fa", edgecolor="#cccccc"),
        )
        return self._save_figure(
            fig,
            "CHART_RQ05_03_top_airports_taxi_out_congestion",
            "Top 10 Sân Bay Taxi-Out Dài Nhất (2023)",
            "RES-017",
            supporting_res_ids=["RES-017"],
            rq_id="RQ-05",
            kpi_id="KPI-07",
            cohort_family="origin-year",
            table_reference="rq05_airport_taxi.parquet",
        )

    def generate_all_charts(self, tables: Dict[str, pd.DataFrame]) -> List[Dict[str, Any]]:
        """Generates all 16 publication figures covering RQ-01 through RQ-05."""
        self.plot_rq01_01_annual_volume(tables["rq01_annual_volume"])
        self.plot_rq01_02_monthly_volume_trend(tables["rq01_monthly_volume"])
        self.plot_rq01_03_year_month_heatmap(tables["rq01_monthly_volume"])
        self.plot_rq02_01_delay_rates(tables["rq02_annual_delays"])
        self.plot_rq02_02_signed_means(tables["rq02_annual_delays"])
        self.plot_rq02_03_percentiles(tables["rq02_annual_delays"])
        self.plot_rq02_04_monthly_seasonality(tables.get("rq02_monthly_pooled_seasonality", tables["rq02_monthly_delays"]))
        self.plot_rq03_01_top_carriers_punctuality(tables["rq03_top_carriers"])
        self.plot_rq03_02_top_carriers_mean_delays(tables["rq03_top_carriers"])
        self.plot_rq03_03_top_origin_airports(tables["rq03_origin_airports"])
        self.plot_rq03_04_directed_routes(tables["rq03_directed_routes"])
        self.plot_rq04_01_pandemic_comparison(tables["rq04_pandemic_comparison"])
        self.plot_rq04_02_pandemic_monthly(tables["rq02_monthly_delays"])
        self.plot_rq05_01_annual_taxi(tables["rq05_annual_journey_times"])
        self.plot_rq05_02_elapsed_times(tables["rq05_annual_journey_times"])
        self.plot_rq05_03_airport_taxi_congestion(tables["rq05_airport_taxi"])
        return self.chart_inventory
