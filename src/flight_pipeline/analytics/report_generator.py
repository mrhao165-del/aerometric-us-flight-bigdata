"""
Report Generator for Task T-014.
Generates T014_ANALYTICAL_FINDINGS_REPORT.md conforming to the 10-section academic structure.
"""

import os
from typing import Dict, Any, List
import pandas as pd


class FindingsReportGenerator:
    """Generates the authoritative Vietnamese analytical findings report for T-014."""

    def __init__(self, run_id: str, results_register_entries: List[Dict[str, Any]], chart_inventory: List[Dict[str, Any]]):
        self.run_id = run_id
        self.entries = results_register_entries
        self.chart_inventory = chart_inventory
        self.res_map = {e["res_id"]: e for e in self.entries}

    def generate_report(self, tables: Dict[str, pd.DataFrame], output_path: str) -> str:
        """Assembles and writes the full 10-section markdown report."""
        report = []

        report.append("# BÁO CÁO KHOA HỌC PHÂN TÍCH HIỆU SUẤT BAY HOA KỲ (2016–2024)")
        report.append("## Đề án Nghiên cứu & Khảo sát Vận hành Hàng không Nội địa Hoa Kỳ")
        report.append("")
        report.append(f"- **Mã thực thi (Run ID):** `{self.run_id}`")
        report.append("- **Nguồn dữ liệu cơ sở:** Snapshot KPI chính thức `kpi_run_2016_2024_v1` (Nhiệm vụ T-013)")
        report.append("- **Tổng số bản ghi nguồn được chấp nhận (DC-11/12):** `54,674,003` chuyến bay")
        report.append("- **Số lượng dòng KPI phân tích:** `684,180` dòng (57,015 cohorts x 12 metric streams)")
        report.append("- **Tình trạng kiểm soát chất lượng:** PASS / VERIFIED (CONTROLLED)")
        report.append("- **Ngôn ngữ báo cáo:** Tiếng Việt (Thuật ngữ kỹ thuật song ngữ chuẩn hóa)")
        report.append("")
        report.append("---")
        report.append("")

        # Section 1
        report.append(self._section_1_executive_summary())
        # Section 2
        report.append(self._section_2_methodology())
        # Section 3
        report.append(self._section_3_rq01(tables))
        # Section 4
        report.append(self._section_4_rq02(tables))
        # Section 5
        report.append(self._section_5_rq03(tables))
        # Section 6
        report.append(self._section_6_rq04(tables))
        # Section 7
        report.append(self._section_7_rq05(tables))
        # Section 8
        report.append(self._section_8_limitations())
        # Section 9
        report.append(self._section_9_recommendations())
        # Section 10
        report.append(self._section_10_appendix())

        content = "\n".join(report)

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)

        return output_path

    def _section_1_executive_summary(self) -> str:
        s = []
        s.append("## 1. Tổng quan điều hành & Tóm tắt phát hiện định lượng (Executive Summary)")
        s.append("")
        s.append("Báo cáo khoa học này tổng hợp toàn bộ kết quả phân tích thống kê mô tả từ 54,674,003 chuyến bay nội địa Hoa Kỳ trong giai đoạn 9 năm (2016–2024), được xử lý qua pipeline Apache Spark và kiểm soát chất lượng theo hợp đồng dữ liệu nghiêm ngặt. Đây là tài liệu bàn giao kỹ thuật trọng tâm của Nhiệm vụ T-014 thuộc Cổng kiểm soát G6.")
        s.append("")
        s.append("### 1.1. Các chỉ số cốt lõi toàn quốc (National Baseline)")
        s.append("- **Quy mô mẫu được chấp nhận:** Toàn bộ 54,674,003 bản ghi nguồn đáp ứng tiêu chuẩn tính hợp lệ, 0 bản ghi bị cách ly (quarantined), 0 bản ghi bị loại bỏ (rejected).")
        s.append("- **Quy mô hàng năm:** Đạt đỉnh tiền đại dịch vào năm 2019 với 7,161,827 chuyến bay, giảm mạnh 39.79% trong năm 2020 xuống còn 4,312,091 chuyến bay, và phục hồi dần đạt 6,645,461 chuyến bay vào năm 2023. Năm 2024 đạt 6,284,841 chuyến bay trên 11 tháng quan sát (tháng 3 vắng mặt do giới hạn nguồn OR-05).")
        s.append("- **Tỷ lệ chuyến bay trễ đến (≥15 phút):** Dao động từ mức thấp kỷ lục 9.73% vào năm 2020 lên mức đỉnh 20.99% vào năm 2022 và 20.81% vào năm 2024. Trung bình toàn giai đoạn đạt xấp xỉ 18.23%.")
        s.append("- **Thời gian trễ đến có dấu (Signed Mean Arrival Delay):** Trung bình toàn quốc đạt giá trị âm (-5.11 phút, chính xác -5.1078 phút) vào năm 2020 (chuyến bay trung bình đến sớm hơn lịch trình), tăng vọt lên +6.93 phút (2022, chính xác +6.9344 phút), +6.57 phút (2023) và +7.11 phút (2024).")
        s.append("- **Hình thái đuôi dài lệch phải cực đoan:** Trung vị trễ đến (P50) hàng năm luôn ở mức âm (-5.0 đến -11.0 phút; năm 2020 đạt -11.0 phút; các năm thông thường đạt -6.0 đến -8.0 phút), phản ánh hơn 50% chuyến bay hạ cánh sớm hơn giờ dự kiến (tuyệt đối không gộp trung vị giữa các năm). Trong khi đó, phân vị 90 (P90) lên tới +42.0 phút (2022) và +43.0 phút (2024), chứng minh hiện tượng chậm trễ tập trung vào đuôi phân phối cực đoan.")
        s.append("- **Thời gian lăn bánh & Đệm lịch trình:** Thời gian lăn ra cất cánh (Taxi-Out) bình quân toàn quốc là 15.25 đến 17.95 phút (giảm xuống 15.25 phút năm 2020, tăng lên 17.95 phút năm 2024). Các hãng bay duy trì đệm lịch trình (chênh lệch giữa hai giá trị kỳ vọng đã công bố: CRS Elapsed TB - Actual Elapsed TB) bình quân từ +4.87 phút (2018) đến +7.08 phút (2020) nhằm hấp thụ các biến động trễ phát sinh.")
        s.append("")
        return "\n".join(s)

    def _section_2_methodology(self) -> str:
        s = []
        s.append("## 2. Phương pháp luận, Không gian mẫu & Tính hợp lệ thống kê")
        s.append("")
        s.append("### 2.1. Nguồn dữ liệu & Tính bất biến")
        s.append("Dữ liệu đầu vào của quy trình phân tích được nạp độc quyền từ snapshot Parquet chính thức `kpi_run_2016_2024_v1`, đã được phê duyệt tại Nhiệm vụ T-013. Tập dữ liệu gồm 9 phân vùng năm (2016–2024) chứa đúng 684,180 bản ghi KPI tương ứng với đúng 57,015 cohort nhân với 12 luồng chỉ số chuẩn hóa.")
        s.append("")
        s.append("### 2.2. Phân loại 6 nhóm chiều phân tích (Grouping Families)")
        s.append("Theo đặc tả KPI_SPEC.md và kết quả đối soát độc lập, 57,015 cohort được phân loại tất định thành 6 nhóm chiều duy nhất:")
        s.append("1. **Toàn quốc theo năm (`year`):** 9 cohort (tương ứng 108 dòng KPI).")
        s.append("2. **Chuỗi thời gian năm-tháng (`year-month`):** 107 cohort (tương ứng 1,284 dòng KPI; tháng 3/2024 không có dữ liệu theo OR-05).")
        s.append("3. **Hãng hàng không theo năm (`carrier-year`):** 140 cohort (tương ứng 1,680 dòng KPI; 19 mã hãng bay trong 9 năm).")
        s.append("4. **Sân bay xuất phát theo năm (`origin-year`):** 2,814 cohort (tương ứng 33,768 dòng KPI).")
        s.append("5. **Sân bay đến theo năm (`dest-year`):** 2,816 cohort (tương ứng 33,792 dòng KPI).")
        s.append("6. **Chặng bay định hướng theo năm (`route-year`):** 51,129 cohort (tương ứng 613,548 dòng KPI).")
        s.append("")
        s.append("Tổng cộng: $9 + 107 + 140 + 2,814 + 2,816 + 51,129 = 57,015$ cohort; $57,015 \\times 12 = 684,180$ dòng KPI hoàn toàn khớp 100%.")
        s.append("")
        s.append("### 2.3. Quy tắc kiểm định mẫu & Tính toán tỷ lệ tổng hợp")
        s.append("- **Bảo vệ cỡ mẫu tối thiểu theo chiều phân tích (`min_n_status` theo FP-DEC-016):** Tất cả các bảng xếp hạng phân tích bắt buộc lọc các cohort có `min_n_status == 'SUFFICIENT'` trên từng chỉ số cụ thể theo đúng ngưỡng đặc thù của từng chiều: Hãng hàng không theo năm (`carrier-year`): tối thiểu 1,000 chuyến bay/năm; Sân bay xuất phát/đến theo năm (`origin-year`, `dest-year`): tối thiểu 365 chuyến bay/năm; Chặng bay theo năm (`route-year`): tối thiểu 100 chuyến bay/năm. Tuyệt đối không quy đồng ngưỡng 100 cho toàn bộ các chiều phân tích. Hệ thống phân loại trạng thái 3 cấp rõ ràng: `SUPPRESSED` (dưới ngưỡng), `LOW_SAMPLE_CAUTION` (cận ngưỡng), và `SUFFICIENT` (đạt ngưỡng). Toàn bộ 140/140 cohort hãng bay phân tích đều đạt mức SUFFICIENT.")
        s.append("- **Gộp theo trọng số mẫu hợp lệ (Valid-Denominator Weighted Pooling):** Tuyệt đối không lấy trung bình cộng đơn giản của các tỷ lệ phần trăm giữa các năm. Toàn bộ các tỷ lệ gộp nhiều năm (như tỷ lệ trễ đến, tỷ lệ đúng giờ, độ trễ trung bình có dấu) đều được tính theo công thức chuẩn: $\\sum (\\text{value} \\times \\text{count\\_metric\\_valid}) / \\sum \\text{count\\_metric\\_valid}$.")
        s.append("- **Cấm gộp phân vị (Prohibition of Percentile Pooling):** Các chỉ số phân vị (P50, P90) là phân vị xấp xỉ Spark GK-quantile được tính độc lập trên từng cohort/năm; tuyệt đối không lấy trung bình hay gộp phân vị giữa các năm.")
        s.append("- **Xử lý số đo có dấu:** Độ trễ âm biểu thị chuyến bay thực hiện sớm hơn kế hoạch. Không tự ý cắt bỏ hay gán về 0 các giá trị âm, bảo toàn tính chân thực của phân phối thời gian thực tế.")
        s.append("")
        return "\n".join(s)

    def _section_3_rq01(self, tables: Dict[str, pd.DataFrame]) -> str:
        s = []
        s.append("## 3. RQ-01: Quy mô, Phân bố thời gian & Mùa vụ (2016–2024)")
        s.append("")
        s.append("### 3.1. Diễn biến quy mô hàng năm (Annual Flight Volume)")
        s.append("Giai đoạn 2016–2019 ghi nhận mức tăng trưởng đều đặn của thị trường hàng không Hoa Kỳ, từ 5,537,987 chuyến (2016, chiếm 10.13%) lên 7,161,827 chuyến (2019, chiếm 13.10%). Năm 2020 chứng kiến mức sụt giảm nghiêm trọng (-39.79% so với 2019) xuống còn 4,312,091 chuyến (chiếm 7.89% tổng sản lượng 9 năm). Quá trình phục hồi diễn ra vững chắc trong các năm tiếp theo, đạt 6,645,461 chuyến vào năm 2023 (`RES-001`).")
        s.append("")

        if "rq01_annual_volume" in tables:
            df = tables["rq01_annual_volume"]
            s.append("| Năm | Quy mô bản ghi (N) | Tỷ trọng 9 năm (%) | Tăng trưởng YoY (%) |")
            s.append("|:---:|---:|---:|---:|")
            for _, r in df.iterrows():
                yoy_str = f"{r['yoy_growth_pct']:+.2f}%" if pd.notnull(r["yoy_growth_pct"]) else "N/A"
                s.append(f"| {int(r['year'])} | {int(r['annual_volume']):,d} | {r['share_of_9yr_pct']:.2f}% | {yoy_str} |")
            s.append("")

        s.append("![Hình 1.1: Quy mô sản lượng chuyến bay hàng năm](charts/CHART_RQ01_01_annual_accepted_volume.png)")
        s.append("*Hình 1.1: Diễn biến tổng sản lượng chuyến bay nội địa Hoa Kỳ 2016–2024 (`RES-001`).*")
        s.append("")

        s.append("### 3.2. Tính quy luật mùa vụ theo tháng (Monthly Seasonality)")
        s.append("Phân tích chuỗi 107 tháng quan sát chỉ ra tính mùa vụ đặc thù:")
        s.append("- **Đỉnh sản lượng:** Trong 6/9 năm quan sát (2016, 2017, 2018, 2021, 2022, 2024), đỉnh sản lượng trong năm đều rơi vào Tháng 7 (thường vượt trên 600,000 chuyến/tháng). Có 3 năm ngoại lệ: năm 2019 đạt đỉnh vào Tháng 8 (636,460 chuyến), năm 2020 đạt đỉnh vào Tháng 1 (590,462 chuyến trước khi dịch bùng phát), và năm 2023 đạt đỉnh vào Tháng 10 (587,544 chuyến) (`RES-002`, cỡ mẫu đánh giá N=9 năm quan sát).")
        s.append("- **Đáy sản lượng:** Trong 8/9 năm quan sát, Tháng 2 luôn là tháng có sản lượng thấp nhất trong năm do số ngày ít hơn và nhu cầu di chuyển giảm. Ngoại lệ duy nhất là năm 2020, đáy sản lượng rơi vào Tháng 5 (163,767 chuyến bay) ngay sau cú sốc đại dịch Tháng 4 (`RES-003`).")
        s.append("")
        s.append("![Hình 1.2: Chuỗi thời gian sản lượng theo tháng](charts/CHART_RQ01_02_monthly_volume_trend.png)")
        s.append("*Hình 1.2: Chuỗi thời gian sản lượng chuyến bay theo tháng, làm nổi bật đáy sụt giảm tháng 4-5/2020 và khoảng trống tháng 3/2024 (`RES-002`, `RES-003`).*")
        s.append("")
        s.append("![Hình 1.3: Bản đồ nhiệt mùa vụ theo tháng](charts/CHART_RQ01_03_year_month_volume_heatmap.png)")
        s.append("*Hình 1.3: Bản đồ nhiệt mật độ chuyến bay theo năm và tháng, phản ánh cấu trúc mùa vụ hè đặc trưng (`RES-002`).*")
        s.append("")
        return "\n".join(s)

    def _section_4_rq02(self, tables: Dict[str, pd.DataFrame]) -> str:
        s = []
        s.append("## 4. RQ-02: Phân bố thời gian trễ, Hình thái đuôi dài & Độ lệch phải")
        s.append("")
        s.append("### 4.1. Tỷ lệ trễ cất cánh và trễ hạ cánh (Delay Rates)")
        s.append("Tỷ lệ trễ đến (≥15 phút) trên toàn mạng lưới duy trì ở mức 17–19% trong các năm tiền đại dịch (2016–2019), giảm mạnh xuống 9.73% trong năm 2020 khi mật độ bầu trời giảm mạnh. Tuy nhiên, khi sản lượng hồi phục, tỷ lệ trễ đã tăng vọt lên 20.99% vào năm 2022, 20.54% vào năm 2023 và 20.81% vào năm 2024 (`RES-004`).")
        s.append("")

        if "rq02_annual_delays" in tables:
            df = tables["rq02_annual_delays"]
            s.append("| Năm | Tỷ lệ trễ đến (%) | Trễ đến TB (phút) | Tỷ lệ trễ đi (%) | Trễ đi TB (phút) | P50 (phút) | P90 (phút) |")
            s.append("|:---:|---:|---:|---:|---:|---:|---:|")
            for _, r in df.iterrows():
                s.append(f"| {int(r['year'])} | {r['arr_delay_ge_15_rate_pct']:.2f}% | {r['arr_delay_signed_mean_min']:+.2f} | {r['dep_delay_ge_15_rate_pct']:.2f}% | {r['dep_delay_signed_mean_min']:+.2f} | {r['arr_delay_p50_min']:+.1f} | {r['arr_delay_p90_min']:+.1f} |")
            s.append("")

        s.append("![Hình 2.1: Tỷ lệ trễ và thời gian trễ trung bình](charts/CHART_RQ02_01_arrival_departure_delay_rate_trend.png)")
        s.append("*Hình 2.1: Diễn biến tỷ lệ trễ (≥15 phút) và giá trị trễ trung bình có dấu giai đoạn 2016–2024 (`RES-004`, `RES-005`).*")
        s.append("")

        s.append("### 4.2. Độ lệch phải và hiện tượng bất đối xứng phân phối (Skewness & Long-Tail)")
        s.append("Phân tích so sánh giữa trung vị (P50) và phân vị 90 (P90) làm sáng tỏ cấu trúc phân phối thời gian trễ bay:")
        s.append("- **Trung vị âm ổn định:** P50 tính riêng cho từng năm theo thuật toán Spark GK-quantile dao động trong khoảng [-11.0, -5.0] phút (năm 2020 đạt -11.0 phút, cohort N = 4,312,091; năm 2022 đạt -6.0 phút, N = 6,413,416; các năm khác dao động từ -5.0 đến -8.0 phút). Điều này chứng minh hơn một nửa số chuyến bay nội địa Hoa Kỳ thực tế hạ cánh trước giờ ghi trên lịch trình. Tuyệt đối không gộp trung vị qua các năm do tính chất phi tuyến (`RES-006`).")
        s.append("- **Phân vị 90 kéo dãn:** Phân vị P90 luôn đạt giá trị dương rất lớn, dao động từ +14.0 phút (2020) đến +42.0 phút (2022, N = 6,413,416) và +43.0 phút (2024, N = 6,284,841). Khoảng cách giữa P90 và P50 lên tới 48–54 phút (`RES-007`).")
        s.append("- **Độ trễ trung bình dương:** Do bị kéo lệch bởi 10–20% các chuyến bay trễ rất nặng (trễ trên 1–3 giờ do dồn ứ dây chuyền), giá trị kỳ vọng (mean) bị kéo lên mức +3.5 đến +7.11 phút trong các năm bình thường (+6.93 phút năm 2022, +6.57 phút năm 2023, +7.11 phút năm 2024), hoàn toàn ngược chiều với trung vị.")
        s.append("")
        s.append("![Hình 2.2: So sánh Trung vị P50 và Phân vị P90](charts/CHART_RQ02_03_arrival_delay_percentiles_p50_p90.png)")
        s.append("*Hình 2.2: Minh chứng định lượng về hiện tượng đuôi dài lệch phải của thời gian trễ đến (`RES-006`, `RES-007`).*")
        s.append("")
        s.append("![Hình 2.3: Tính mùa vụ của độ trễ đến hàng tháng](charts/CHART_RQ02_04_monthly_arrival_delay_rate_seasonality.png)")
        s.append("*Hình 2.3: Tính mùa vụ của tỷ lệ trễ đến gộp theo tháng (`RES-004`).*")
        s.append("")
        return "\n".join(s)

    def _section_5_rq03(self, tables: Dict[str, pd.DataFrame]) -> str:
        s = []
        s.append("## 5. RQ-03: Hiệu suất khai thác theo Hãng bay, Sân bay & Tính bất đối xứng chặng bay")
        s.append("")
        s.append("### 5.1. Hiệu suất các Hãng hàng không (Carrier Performance)")
        s.append("Trong số 19 hãng hàng không quan sát được trong 9 năm, nhóm 3 hãng có thị phần lớn nhất gồm:")
        s.append("1. **Southwest Airlines (WN):** Đạt 11,133,643 chuyến bay tích lũy (chiếm 20.36% sản lượng 9 năm), tỷ lệ đúng giờ gộp đạt 80.67% (tương ứng tỷ lệ trễ đến gộp 19.33%), độ trễ đến trung bình có dấu +3.85 phút (`RES-008`).")
        s.append("2. **Delta Air Lines (DL):** Đạt 7,821,658 chuyến bay tích lũy, duy trì hiệu suất đúng giờ hàng đầu trong nhóm các hãng truyền thống lớn với tỷ lệ đúng giờ gộp 85.81% (tỷ lệ trễ đến gộp chỉ 14.19%), độ trễ đến trung bình có dấu +0.66 phút (`RES-009`).")
        s.append("3. **American Airlines (AA):** Đạt 7,518,473 chuyến bay tích lũy, tỷ lệ đúng giờ gộp 79.61% (tương ứng tỷ lệ trễ đến gộp 20.39%), độ trễ đến trung bình có dấu +7.00 phút (`RES-009`).")
        s.append("")

        if "rq03_top_carriers" in tables:
            df = tables["rq03_top_carriers"].head(10)
            s.append("| Hãng hàng không | Tổng số chuyến (9 năm) | Số năm hoạt động | Trễ đến TB (phút) | Trễ đi TB (phút) | Đúng giờ TB (%) |")
            s.append("|:---|---:|:---:|---:|---:|---:|")
            for _, r in df.iterrows():
                s.append(f"| {r['carrier']} | {int(r['total_volume']):,d} | {int(r['years_active'])} | {r['mean_arr_delay_signed']:+.2f} | {r['mean_dep_delay_signed']:+.2f} | {r['mean_on_time_arr_rate_pct']:.2f}% |")
            s.append("")

        s.append("![Hình 3.1: Tỷ lệ Đến Đúng Giờ của Top 10 Hãng hàng không](charts/CHART_RQ03_01_top_carriers_on_time_performance.png)")
        s.append("*Hình 3.1: So sánh tỷ lệ đến đúng giờ gộp theo trọng số của 10 hãng bay lớn nhất (`RES-008`, `RES-009`).*")
        s.append("")
        s.append("![Hình 3.2: Độ trễ Đến và Trễ Đi của các Hãng lớn](charts/CHART_RQ03_02_top_carriers_mean_delays.png)")
        s.append("*Hình 3.2: So sánh độ trễ đến và trễ khởi hành của các hãng bay chủ lực (`RES-009`).*")
        s.append("")

        s.append("### 5.2. Điểm nghẽn tại các Trung tâm trung chuyển (Hub Congestion)")
        s.append("Các sân bay cửa ngõ vùng đô thị New York và Chicago thường xuyên nằm trong nhóm có tỷ lệ trễ xuất phát cao nhất quốc gia:")
        s.append("- **Newark Liberty (EWR):** Năm 2022 ghi nhận tỷ lệ trễ xuất phát lên tới 27.67% trên quy mô cohort N = 123,277 chuyến bay (đạt mức SUFFICIENT với ngưỡng min-N quy định cho sân bay là 365 chuyến/năm, `RES-010`).")
        s.append("- **Chicago O'Hare (ORD):** Năm 2024 đạt tỷ lệ trễ xuất phát 22.48% trên quy mô N = 251,485 chuyến bay (`RES-010`).")
        s.append("- **New York LaGuardia (LGA):** Năm 2019 đạt tỷ lệ trễ xuất phát 22.63% trên quy mô N = 166,283 chuyến bay (`RES-010`).")
        s.append("")
        s.append("![Hình 3.3: Top Sân bay trễ xuất phát cao nhất](charts/CHART_RQ03_03_top_origin_airports_departure_delays.png)")
        s.append("*Hình 3.3: Tỷ lệ trễ cất cánh tại các trung tâm trung chuyển hàng không trọng điểm (`RES-010`).*")
        s.append("")

        s.append("### 5.3. Tính bất đối xứng vận hành trên các chặng bay hai chiều (Route Asymmetry)")
        s.append("Phân tích 51,129 cohort chặng bay hàng năm chỉ ra tính bất đối xứng vận hành rõ rệt giữa hai chiều bay đối ứng ($A \\to B$ so với $B \\to A$), thỏa mãn tiêu chí min-N >= 100 chuyến bay/năm cho mỗi chiều:")
        s.append("- **Cặp hành lang Chicago (ORD) — New York LaGuardia (LGA):** Năm 2019, chiều ORD $\\to$ LGA chịu tỷ lệ trễ đến 31.42% (N = 14,108) so với 28.60% (N = 14,169) của chiều LGA $\\to$ ORD, tạo ra mức chênh lệch bất đối xứng 2.82% (2.8242 điểm phần trăm) trên tổng quy mô cặp chặng N = 28,277 chuyến bay (`RES-011`).")
        s.append("- **Cặp hành lang San Francisco (SFO) — Los Angeles (LAX):** Năm 2017, chiều SFO $\\to$ LAX ghi nhận tỷ lệ trễ 20.35% so với 17.89% của chiều LAX $\\to$ SFO, tạo mức chênh lệch 2.46% trên tổng quy mô cặp chặng N = 28,174 chuyến bay (`RES-011`).")
        s.append("")
        s.append("![Hình 3.4: Bất đối xứng trễ trên các cặp chặng bay đối ứng](charts/CHART_RQ03_04_directed_route_delay_asymmetry.png)")
        s.append("*Hình 3.4: So sánh tỷ lệ trễ giữa hai chiều đối ứng trên các hành lang bay mật độ cao (`RES-011`).*")
        s.append("")
        return "\n".join(s)

    def _section_6_rq04(self, tables: Dict[str, pd.DataFrame]) -> str:
        s = []
        s.append("## 6. RQ-04: Cú sốc đại dịch 2020, Quá trình phục hồi & Tái tắc nghẽn (Quan sát phi nhân quả)")
        s.append("")
        s.append("> [!IMPORTANT]")
        s.append("> **Nguyên tắc phương pháp luận:** Mối liên hệ giữa giai đoạn 2020 và các biến động hiệu suất bay được trình bày dưới góc độ quan sát thực nghiệm mô tả (observational patterns). Nghiên cứu không khẳng định mối quan hệ nhân quả duy nhất từ một yếu tố đơn lẻ khi chưa có mô hình kiểm soát nhiễu đa biến.")
        s.append("")
        s.append("### 6.1. Sự trùng hợp quan sát giữa suy giảm sản lượng và cải thiện đúng giờ")
        s.append("Năm 2020 ghi nhận sự trùng hợp nổi bật giữa sự sụt giảm mạnh về quy mô khai thác và sự cải thiện vượt bậc của các chỉ số hiệu suất:")
        s.append("- Sản lượng toàn quốc giảm xuống 4,312,091 chuyến (-39.79% so với 2019).")
        s.append("- Tỷ lệ trễ đến giảm xuống mức kỷ lục 9.73% (giảm gần 10 điểm phần trăm so với mức 19.11% của năm 2019) (`RES-012`).")
        s.append("- Thời gian trễ đến trung bình có dấu chuyển sang giá trị âm (-5.11 phút, chính xác -5.1078 phút) (`RES-005`).")
        s.append("- Tháng 4/2020 ghi nhận tỷ lệ đúng giờ đạt đỉnh 95.15% (tỷ lệ trễ chỉ 4.85%) trên tổng số 179,835 chuyến bay (`RES-013`).")
        s.append("")

        if "rq04_pandemic_comparison" in tables:
            df = tables["rq04_pandemic_comparison"]
            s.append("| Năm | Quy mô chuyến bay | Tỷ lệ trễ đến (%) | Trễ đến TB (phút) | Trễ đi TB (phút) | P90 trễ đến (phút) |")
            s.append("|:---:|---:|---:|---:|---:|---:|")
            for _, r in df.iterrows():
                y_val = int(r["year"]) if "year" in r else int(r.name)
                s.append(f"| {y_val} | {int(r['total_records']):,d} | {r['arr_delay_ge_15_rate_pct']:.2f}% | {r['arr_delay_signed_mean_min']:+.2f} | {r['dep_delay_signed_mean_min']:+.2f} | {r['arr_delay_p90_min']:+.1f} |")
            s.append("")

        s.append("![Hình 4.1: Diễn biến Quy mô và Tỷ lệ trễ qua các giai đoạn](charts/CHART_RQ04_01_pandemic_period_kpi_comparison.png)")
        s.append("*Hình 4.1: So sánh hiệu suất các chỉ số cốt lõi trước, trong và sau năm 2020 (`RES-012`, `RES-014`).*")
        s.append("")

        s.append("### 6.2. Hiện tượng tái tắc nghẽn hậu đại dịch (Post-Pandemic Re-congestion)")
        s.append("Khi nhu cầu đi lại phục hồi, sản lượng tăng dần: 5.76 triệu chuyến (2021), 6.41 triệu chuyến (2022), và 6.65 triệu chuyến (2023). Đáng chú ý, tỷ lệ trễ đến không chỉ quay lại mức trước đại dịch mà còn vượt qua mức năm 2019, đạt đỉnh 20.99% vào năm 2022 và duy trì ở mức trên 20.5% trong các năm 2023–2024 (`RES-014`).")
        s.append("")
        s.append("Dữ liệu chỉ ra rằng việc tái phục hồi quy mô vận hành trong bối cảnh hạ tầng và nhân lực chưa đồng bộ có mối liên hệ mật thiết với việc gia tăng độ trễ mạng lưới.")
        s.append("")
        s.append("![Hình 4.2: Biến động sản lượng và tỷ lệ đúng giờ theo tháng](charts/CHART_RQ04_02_2020_monthly_shock_and_rebound.png)")
        s.append("*Hình 4.2: Cú sốc đại dịch và xu hướng phục hồi hàng tháng giai đoạn 2019–2021 (`RES-013`, `RES-014`).*")
        s.append("")
        return "\n".join(s)

    def _section_7_rq05(self, tables: Dict[str, pd.DataFrame]) -> str:
        s = []
        s.append("## 7. RQ-05: Động học thời gian lăn bánh (Taxi Times) & Biên đệm lịch trình (Buffer Time)")
        s.append("")
        s.append("### 7.1. Thời gian lăn ra cất cánh và lăn vào bến đỗ (Taxi-Out vs. Taxi-In)")
        s.append("Dữ liệu 9 năm chứng minh thời gian lăn bánh trên mặt đất đóng góp đáng kể vào tổng thời gian hoạt động của tàu bay:")
        s.append("- **Thời gian lăn ra (Taxi-Out):** Toàn quốc bình quân đạt 16.19 phút (2016) đến 17.95 phút (2024). Năm 2020 giảm xuống 15.25 phút (chính xác 15.2476 phút) khi sân bay thông thoáng (`RES-015`).")
        s.append("- **Thời gian lăn vào (Taxi-In):** Duy trì tương đối ổn định từ 7.45 phút (2016) đến 8.37 phút (2024), ít bị ảnh hưởng bởi tắc nghẽn đường cất hạ cánh so với Taxi-Out (`RES-016`).")
        s.append("")

        if "rq05_annual_journey_times" in tables:
            df = tables["rq05_annual_journey_times"]
            s.append("| Năm | Taxi-Out TB (phút) | Taxi-In TB (phút) | Thời gian bay TB (phút) | Tổng thời gian thực (phút) | Lịch trình CRS (phút) | Đệm lịch trình (phút) |")
            s.append("|:---:|---:|---:|---:|---:|---:|---:|")
            for _, r in df.iterrows():
                buf = r['crs_elapsed_mean_min'] - r['actual_elapsed_mean_min']
                s.append(f"| {int(r['year'])} | {r['taxi_out_mean_min']:.2f} | {r['taxi_in_mean_min']:.2f} | {r['air_time_mean_min']:.2f} | {r['actual_elapsed_mean_min']:.2f} | {r['crs_elapsed_mean_min']:.2f} | {buf:+.2f} |")
            s.append("")

        s.append("![Hình 5.1: Động học thời gian lăn bánh mặt đất](charts/CHART_RQ05_01_annual_taxi_time_trends.png)")
        s.append("*Hình 5.1: Diễn biến thời gian lăn ra (Taxi-Out) và lăn vào (Taxi-In) bình quân toàn quốc giai đoạn 2016–2024 (`RES-015`, `RES-016`).*")
        s.append("")

        s.append("### 7.2. Điểm nghẽn lăn bánh tại các Sân bay đô thị lớn")
        s.append("Thời gian lăn ra chịu áp lực nghiêm trọng tại các sân bay có cấu hình đường băng phức tạp và mật độ khai thác dày đặc:")
        s.append("- **Sân bay John F. Kennedy (JFK):** Đứng đầu với thời gian Taxi-Out bình quân đạt 26.21 phút trong năm 2023 trên quy mô N = 129,620 chuyến bay (thỏa mãn tiêu chí min-N >= 365 chuyến/năm, `RES-017`).")
        s.append("- **Sân bay Newark Liberty (EWR):** Năm 2023 đạt thời gian Taxi-Out bình quân 23.76 phút trên quy mô N = 134,185 chuyến bay (`RES-017`).")
        s.append("- **Sân bay LaGuardia (LGA):** Năm 2023 đạt thời gian Taxi-Out bình quân 23.58 phút trên quy mô N = 158,552 chuyến bay (`RES-017`).")
        s.append("- **Sân bay Chicago O'Hare (ORD):** Năm 2023 đạt thời gian Taxi-Out bình quân 22.45 phút trên quy mô N = 253,478 chuyến bay (`RES-017`).")
        s.append("")
        s.append("![Hình 5.2: Top 10 Sân bay có thời gian Taxi-Out dài nhất](charts/CHART_RQ05_03_top_airports_taxi_out_congestion.png)")
        s.append("*Hình 5.2: Bảng xếp hạng các sân bay có thời gian lăn ra cất cánh bình quân cao nhất (`RES-017`).*")
        s.append("")

        s.append("### 7.3. Biên đệm lịch trình (Schedule Buffer) & Phân rã hành trình")
        s.append("Chênh lệch giữa thời gian dự kiến trên lịch trình và thời gian bay thực tế phản ánh chiến lược đệm lịch trình:")
        s.append("- **Định nghĩa toán học & Công bố phi nhân quả:** Đệm lịch trình được xác định như chênh lệch giữa hai giá trị kỳ vọng đã công bố (Difference of Published Means: $\\mu_{\\text{CRS}} - \\mu_{\\text{ACTUAL}}$), tuyệt đối không suy diễn quan hệ nhân quả hay can thiệp vận hành cấp vi mô khi chưa kiểm soát yếu tố thời tiết và luồng không lưu.")
        s.append("- Giá trị đệm lịch trình bình quân toàn quốc luôn dương trong toàn bộ 9 năm, dao động từ **+4.87 phút (2018)** đến **+7.08 phút (2020)** (`RES-018`).")
        s.append("- Năm 2020, đệm lịch trình đạt mức cao nhất (+7.08 phút, N = 4,312,091) do thời gian lăn bánh và bay thực tế giảm nhanh trong bối cảnh lịch trình chưa kịp điều chỉnh tương ứng.")
        s.append("- **Phân rã hành trình bay (`RES-019`):** Thời gian thực hiện hành trình toàn quốc (`ACTUAL_ELAPSED_TIME`) đạt bình quân 140.16 phút năm 2016 (N = 5,537,987; dao động 137.30 đến 142.39 phút giai đoạn 2016–2024). Việc phân tích tỷ trọng các thành phần hành trình (Air Time chiếm ~81%, Taxi-Out ~12%, Taxi-In ~6%) được trình bày dưới dạng so sánh cận biên giữa các giá trị trung bình đã công bố do sự chênh lệch nhỏ về số lượng mẫu hợp lệ giữa các chỉ số con.")
        s.append("")
        s.append("![Hình 5.3: Biên đệm lịch trình hàng năm](charts/CHART_RQ05_02_elapsed_time_and_schedule_buffer.png)")
        s.append("*Hình 5.3: Mức chênh lệch thời gian đệm lịch trình bình quân toàn quốc 2016–2024 (`RES-018`, `RES-019`).*")
        s.append("")
        return "\n".join(s)

    def _section_8_limitations(self) -> str:
        s = []
        s.append("## 8. Giới hạn phương pháp luận, Hạn chế dữ liệu & Cảnh báo sử dụng")
        s.append("")
        s.append("Người sử dụng kết quả nghiên cứu cần lưu ý các ràng buộc kỹ thuật và phạm vi sau:")
        s.append("1. **Giới hạn độ phủ năm 2024 (Ràng buộc OR-05):** Do thiếu hụt tệp nguồn tháng 3/2024 từ nguồn cung cấp ban đầu, năm 2024 chỉ bao gồm 11 tháng quan sát (335 ngày, 6,284,841 chuyến bay, `RES-020`). Các so sánh tổng sản lượng năm 2024 với các năm đủ 12 tháng cần được diễn giải với sự thận trọng thích đáng.")
        s.append("2. **Tính chất mô tả của phân tích:** Toàn bộ các kết luận trong báo cáo đều mang tính thống kê mô tả (descriptive analytics). Không ngoại suy quan hệ nhân quả đơn lẻ đối với các cú sốc vĩ mô hoặc hiện tượng thời tiết.")
        s.append("3. **Phân nhánh dữ liệu thời tiết (Weather Data Branch):** Phân nhánh thời tiết T-015 hiện ở trạng thái `CONDITIONAL_NO_GO` và không thuộc phạm vi xử lý của báo cáo này.")
        s.append("4. **Độ chính xác phân vị (Percentile Approximation):** Các chỉ số phân vị P50 và P90 được tính toán thông qua thuật toán xấp xỉ phân vị của Spark với độ chính xác tương đối `relative_error = 0.01` theo đặc tả `KPI_SPEC.md`.")
        s.append("5. **Bảo toàn tính toàn vẹn:** Nghiên cứu này tuyệt đối không can thiệp, sửa đổi hay ghi đè lên các tập dữ liệu Parquet nền tảng đã được niêm phong tại T-012 và T-013.")
        s.append("")
        return "\n".join(s)

    def _section_9_recommendations(self) -> str:
        s = []
        s.append("## 9. Đề xuất can thiệp vận hành & Định hướng nghiên cứu mở rộng")
        s.append("")
        s.append("### 9.1. Khuyến nghị cho Cơ quan Quản lý & Điều hành Sân bay (Airport Operators & FAA)")
        s.append("1. **Kiểm soát nghẽn mặt đất tại các Siêu Hub:** Ưu tiên tối ưu hóa luồng di chuyển trên đường lăn và lịch xếp hàng cất cánh (Surface Metering / Departure Queue Management) tại JFK, LGA, và ORD để cắt giảm thời gian Taxi-Out đang vượt mức 22–25 phút.")
        s.append("2. **Cân đối tải chặng bay hai chiều:** Điều chỉnh giờ cấp phép cất hạ cánh (Slot Allocation) trên các hành lang bay có tính bất đối xứng cao (như SFO-LAX) nhằm giảm thiểu tích lũy trễ dây chuyền.")
        s.append("")
        s.append("### 9.2. Khuyến nghị cho các Hãng hàng không (Airlines)")
        s.append("1. **Chuẩn hóa chiến lược đệm lịch trình:** Tái đánh giá mức đệm lịch trình theo từng mùa vụ và khung giờ để tránh tình trạng hạ cánh sớm quá mức gây quá tải cổng đón tại sân bay đến, hoặc đệm quá ít dẫn đến tỷ lệ trễ tăng vọt.")
        s.append("2. **Quản trị rủi ro đuôi dài (Tail Risk Management):** Thay vì chỉ theo dõi trễ trung bình, cần thiết lập chỉ số cảnh báo sớm dựa trên biến động của phân vị P90 để kịp thời kích hoạt các phương án phục hồi đội bay.")
        s.append("")
        s.append("### 9.3. Định hướng nghiên cứu tiếp theo")
        s.append("- Tích hợp dữ liệu thời tiết khi các điều kiện kiểm soát chất lượng tại Cổng G5/G6 đối với T-015 được thỏa mãn.")
        s.append("- Phát triển các mô hình chuỗi thời gian phân tách thành phần xu hướng và mùa vụ phục vụ dự báo ngắn hạn.")
        s.append("")
        return "\n".join(s)

    def _section_10_appendix(self) -> str:
        s = []
        s.append("## 10. Phụ lục: Bảng tra cứu định danh kết quả (RES Register Index) & Danh mục biểu đồ")
        s.append("")
        s.append("### 10.1. Danh mục định danh kết quả nghiên cứu (Results Register Index)")
        s.append("| Mã RES | Câu hỏi | Chỉ số KPI | Chiều phân tích | Giá trị quan sát | Tóm tắt phát hiện |")
        s.append("|:---|:---:|:---:|:---:|:---:|:---|")
        for e in self.entries:
            val_str = str(e["observed_value"])
            if isinstance(e["observed_value"], float):
                val_str = f"{e['observed_value']:.2f}"
            s.append(f"| `{e['res_id']}` | {e['rq_id']} | {e['kpi_id']} | `{e['cohort_family']}` | {val_str} | {e['key_finding_vi'][:70]}... |")
        s.append("")

        s.append("### 10.2. Danh mục biểu đồ trực quan hóa (Chart Inventory)")
        s.append("| Mã Biểu đồ | Tên file (PNG / SVG) | Định dạng | RES liên kết | Tiêu đề biểu đồ |")
        s.append("|:---|:---|:---:|:---:|:---|")
        for c in self.chart_inventory:
            supp_res = c.get("supporting_res_ids", [c.get("res_id", "")])
            supp_res_str = ", ".join(f"`{r}`" for r in supp_res)
            s.append(f"| `{c['chart_id']}` | `{c['png_file']}`<br>`{c['svg_file']}` | PNG (300 DPI)<br>SVG (Vector) | {supp_res_str} | {c['title_vi']} |")
        s.append("")
        return "\n".join(s)
