# BÁO CÁO KHOA HỌC PHÂN TÍCH HIỆU SUẤT BAY HOA KỲ (2016–2024)
## Đề án Nghiên cứu & Khảo sát Vận hành Hàng không Nội địa Hoa Kỳ

- **Mã thực thi (Run ID):** `t014_analysis_2016_2024_v4`
- **Nguồn dữ liệu cơ sở:** Snapshot KPI chính thức `kpi_run_2016_2024_v1` (Nhiệm vụ T-013)
- **Tổng số bản ghi nguồn được chấp nhận (DC-11/12):** `54,674,003` chuyến bay
- **Số lượng dòng KPI phân tích:** `684,180` dòng (57,015 cohorts x 12 metric streams)
- **Tình trạng kiểm soát chất lượng:** PASS / VERIFIED (CONTROLLED)
- **Ngôn ngữ báo cáo:** Tiếng Việt (Thuật ngữ kỹ thuật song ngữ chuẩn hóa)

---

## 1. Tổng quan điều hành & Tóm tắt phát hiện định lượng (Executive Summary)

Báo cáo khoa học này tổng hợp toàn bộ kết quả phân tích thống kê mô tả từ 54,674,003 chuyến bay nội địa Hoa Kỳ trong giai đoạn 9 năm (2016–2024), được xử lý qua pipeline Apache Spark và kiểm soát chất lượng theo hợp đồng dữ liệu nghiêm ngặt. Đây là tài liệu bàn giao kỹ thuật trọng tâm của Nhiệm vụ T-014 thuộc Cổng kiểm soát G6.

### 1.1. Các chỉ số cốt lõi toàn quốc (National Baseline)
- **Quy mô mẫu được chấp nhận:** Toàn bộ 54,674,003 bản ghi nguồn đáp ứng tiêu chuẩn tính hợp lệ, 0 bản ghi bị cách ly (quarantined), 0 bản ghi bị loại bỏ (rejected).
- **Quy mô hàng năm:** Đạt đỉnh tiền đại dịch vào năm 2019 với 7,161,827 chuyến bay, giảm mạnh 39.79% trong năm 2020 xuống còn 4,312,091 chuyến bay, và phục hồi dần đạt 6,645,461 chuyến bay vào năm 2023. Năm 2024 đạt 6,284,841 chuyến bay trên 11 tháng quan sát (tháng 3 vắng mặt do giới hạn nguồn OR-05).
- **Tỷ lệ chuyến bay trễ đến (≥15 phút):** Dao động từ mức thấp kỷ lục 9.73% vào năm 2020 lên mức đỉnh 20.99% vào năm 2022 và 20.81% vào năm 2024. Trung bình toàn giai đoạn đạt xấp xỉ 18.23%.
- **Thời gian trễ đến có dấu (Signed Mean Arrival Delay):** Trung bình toàn quốc đạt giá trị âm (-5.11 phút, chính xác -5.1078 phút) vào năm 2020 (chuyến bay trung bình đến sớm hơn lịch trình), tăng vọt lên +6.93 phút (2022, chính xác +6.9344 phút), +6.57 phút (2023) và +7.11 phút (2024).
- **Hình thái đuôi dài lệch phải cực đoan:** Trung vị trễ đến (P50) hàng năm luôn ở mức âm (-5.0 đến -11.0 phút; năm 2020 đạt -11.0 phút; các năm thông thường đạt -6.0 đến -8.0 phút), phản ánh hơn 50% chuyến bay hạ cánh sớm hơn giờ dự kiến (tuyệt đối không gộp trung vị giữa các năm). Trong khi đó, phân vị 90 (P90) lên tới +42.0 phút (2022) và +43.0 phút (2024), chứng minh hiện tượng chậm trễ tập trung vào đuôi phân phối cực đoan.
- **Thời gian lăn bánh & Đệm lịch trình:** Thời gian lăn ra cất cánh (Taxi-Out) bình quân toàn quốc là 15.25 đến 17.95 phút (giảm xuống 15.25 phút năm 2020, tăng lên 17.95 phút năm 2024). Các hãng bay duy trì đệm lịch trình (chênh lệch giữa hai giá trị kỳ vọng đã công bố: CRS Elapsed TB - Actual Elapsed TB) bình quân từ +4.87 phút (2018) đến +7.08 phút (2020) nhằm hấp thụ các biến động trễ phát sinh.

## 2. Phương pháp luận, Không gian mẫu & Tính hợp lệ thống kê

### 2.1. Nguồn dữ liệu & Tính bất biến
Dữ liệu đầu vào của quy trình phân tích được nạp độc quyền từ snapshot Parquet chính thức `kpi_run_2016_2024_v1`, đã được phê duyệt tại Nhiệm vụ T-013. Tập dữ liệu gồm 9 phân vùng năm (2016–2024) chứa đúng 684,180 bản ghi KPI tương ứng với đúng 57,015 cohort nhân với 12 luồng chỉ số chuẩn hóa.

### 2.2. Phân loại 6 nhóm chiều phân tích (Grouping Families)
Theo đặc tả KPI_SPEC.md và kết quả đối soát độc lập, 57,015 cohort được phân loại tất định thành 6 nhóm chiều duy nhất:
1. **Toàn quốc theo năm (`year`):** 9 cohort (tương ứng 108 dòng KPI).
2. **Chuỗi thời gian năm-tháng (`year-month`):** 107 cohort (tương ứng 1,284 dòng KPI; tháng 3/2024 không có dữ liệu theo OR-05).
3. **Hãng hàng không theo năm (`carrier-year`):** 140 cohort (tương ứng 1,680 dòng KPI; 19 mã hãng bay trong 9 năm).
4. **Sân bay xuất phát theo năm (`origin-year`):** 2,814 cohort (tương ứng 33,768 dòng KPI).
5. **Sân bay đến theo năm (`dest-year`):** 2,816 cohort (tương ứng 33,792 dòng KPI).
6. **Chặng bay định hướng theo năm (`route-year`):** 51,129 cohort (tương ứng 613,548 dòng KPI).

Tổng cộng: $9 + 107 + 140 + 2,814 + 2,816 + 51,129 = 57,015$ cohort; $57,015 \times 12 = 684,180$ dòng KPI hoàn toàn khớp 100%.

### 2.3. Quy tắc kiểm định mẫu & Tính toán tỷ lệ tổng hợp
- **Bảo vệ cỡ mẫu tối thiểu theo chiều phân tích (`min_n_status` theo FP-DEC-016):** Tất cả các bảng xếp hạng phân tích bắt buộc lọc các cohort có `min_n_status == 'SUFFICIENT'` trên từng chỉ số cụ thể theo đúng ngưỡng đặc thù của từng chiều: Hãng hàng không theo năm (`carrier-year`): tối thiểu 1,000 chuyến bay/năm; Sân bay xuất phát/đến theo năm (`origin-year`, `dest-year`): tối thiểu 365 chuyến bay/năm; Chặng bay theo năm (`route-year`): tối thiểu 100 chuyến bay/năm. Tuyệt đối không quy đồng ngưỡng 100 cho toàn bộ các chiều phân tích. Hệ thống phân loại trạng thái 3 cấp rõ ràng: `SUPPRESSED` (dưới ngưỡng), `LOW_SAMPLE_CAUTION` (cận ngưỡng), và `SUFFICIENT` (đạt ngưỡng). Toàn bộ 140/140 cohort hãng bay phân tích đều đạt mức SUFFICIENT.
- **Gộp theo trọng số mẫu hợp lệ (Valid-Denominator Weighted Pooling):** Tuyệt đối không lấy trung bình cộng đơn giản của các tỷ lệ phần trăm giữa các năm. Toàn bộ các tỷ lệ gộp nhiều năm (như tỷ lệ trễ đến, tỷ lệ đúng giờ, độ trễ trung bình có dấu) đều được tính theo công thức chuẩn: $\sum (\text{value} \times \text{count\_metric\_valid}) / \sum \text{count\_metric\_valid}$.
- **Cấm gộp phân vị (Prohibition of Percentile Pooling):** Các chỉ số phân vị (P50, P90) là phân vị xấp xỉ Spark GK-quantile được tính độc lập trên từng cohort/năm; tuyệt đối không lấy trung bình hay gộp phân vị giữa các năm.
- **Xử lý số đo có dấu:** Độ trễ âm biểu thị chuyến bay thực hiện sớm hơn kế hoạch. Không tự ý cắt bỏ hay gán về 0 các giá trị âm, bảo toàn tính chân thực của phân phối thời gian thực tế.

## 3. RQ-01: Quy mô, Phân bố thời gian & Mùa vụ (2016–2024)

### 3.1. Diễn biến quy mô hàng năm (Annual Flight Volume)
Giai đoạn 2016–2019 ghi nhận mức tăng trưởng đều đặn của thị trường hàng không Hoa Kỳ, từ 5,537,987 chuyến (2016, chiếm 10.13%) lên 7,161,827 chuyến (2019, chiếm 13.10%). Năm 2020 chứng kiến mức sụt giảm nghiêm trọng (-39.79% so với 2019) xuống còn 4,312,091 chuyến (chiếm 7.89% tổng sản lượng 9 năm). Quá trình phục hồi diễn ra vững chắc trong các năm tiếp theo, đạt 6,645,461 chuyến vào năm 2023 (`RES-001`).

| Năm | Quy mô bản ghi (N) | Tỷ trọng 9 năm (%) | Tăng trưởng YoY (%) |
|:---:|---:|---:|---:|
| 2016 | 5,537,987 | 10.13% | N/A |
| 2017 | 5,575,872 | 10.20% | +0.68% |
| 2018 | 6,986,842 | 12.78% | +25.30% |
| 2019 | 7,161,827 | 13.10% | +2.50% |
| 2020 | 4,312,091 | 7.89% | -39.79% |
| 2021 | 5,755,666 | 10.53% | +33.48% |
| 2022 | 6,413,416 | 11.73% | +11.43% |
| 2023 | 6,645,461 | 12.15% | +3.62% |
| 2024 | 6,284,841 | 11.50% | -5.43% |

![Hình 1.1: Quy mô sản lượng chuyến bay hàng năm](charts/CHART_RQ01_01_annual_accepted_volume.png)
*Hình 1.1: Diễn biến tổng sản lượng chuyến bay nội địa Hoa Kỳ 2016–2024 (`RES-001`).*

### 3.2. Tính quy luật mùa vụ theo tháng (Monthly Seasonality)
Phân tích chuỗi 107 tháng quan sát chỉ ra tính mùa vụ đặc thù:
- **Đỉnh sản lượng:** Trong 6/9 năm quan sát (2016, 2017, 2018, 2021, 2022, 2024), đỉnh sản lượng trong năm đều rơi vào Tháng 7 (thường vượt trên 600,000 chuyến/tháng). Có 3 năm ngoại lệ: năm 2019 đạt đỉnh vào Tháng 8 (636,460 chuyến), năm 2020 đạt đỉnh vào Tháng 1 (590,462 chuyến trước khi dịch bùng phát), và năm 2023 đạt đỉnh vào Tháng 10 (587,544 chuyến) (`RES-002`, cỡ mẫu đánh giá N=9 năm quan sát).
- **Đáy sản lượng:** Trong 8/9 năm quan sát, Tháng 2 luôn là tháng có sản lượng thấp nhất trong năm do số ngày ít hơn và nhu cầu di chuyển giảm. Ngoại lệ duy nhất là năm 2020, đáy sản lượng rơi vào Tháng 5 (163,767 chuyến bay) ngay sau cú sốc đại dịch Tháng 4 (`RES-003`).

![Hình 1.2: Chuỗi thời gian sản lượng theo tháng](charts/CHART_RQ01_02_monthly_volume_trend.png)
*Hình 1.2: Chuỗi thời gian sản lượng chuyến bay theo tháng, làm nổi bật đáy sụt giảm tháng 4-5/2020 và khoảng trống tháng 3/2024 (`RES-002`, `RES-003`).*

![Hình 1.3: Bản đồ nhiệt mùa vụ theo tháng](charts/CHART_RQ01_03_year_month_volume_heatmap.png)
*Hình 1.3: Bản đồ nhiệt mật độ chuyến bay theo năm và tháng, phản ánh cấu trúc mùa vụ hè đặc trưng (`RES-002`).*

## 4. RQ-02: Phân bố thời gian trễ, Hình thái đuôi dài & Độ lệch phải

### 4.1. Tỷ lệ trễ cất cánh và trễ hạ cánh (Delay Rates)
Tỷ lệ trễ đến (≥15 phút) trên toàn mạng lưới duy trì ở mức 17–19% trong các năm tiền đại dịch (2016–2019), giảm mạnh xuống 9.73% trong năm 2020 khi mật độ bầu trời giảm mạnh. Tuy nhiên, khi sản lượng hồi phục, tỷ lệ trễ đã tăng vọt lên 20.99% vào năm 2022, 20.54% vào năm 2023 và 20.81% vào năm 2024 (`RES-004`).

| Năm | Tỷ lệ trễ đến (%) | Trễ đến TB (phút) | Tỷ lệ trễ đi (%) | Trễ đi TB (phút) | P50 (phút) | P90 (phút) |
|:---:|---:|---:|---:|---:|---:|---:|
| 2016 | 17.41% | +3.52 | 17.12% | +8.87 | -6.0 | +32.0 |
| 2017 | 18.45% | +4.32 | 18.08% | +9.66 | -6.0 | +35.0 |
| 2018 | 19.09% | +5.00 | 18.33% | +9.87 | -6.0 | +37.0 |
| 2019 | 19.11% | +5.38 | 18.63% | +10.85 | -6.0 | +39.0 |
| 2020 | 9.73% | -5.11 | 9.00% | +1.97 | -11.0 | +14.0 |
| 2021 | 17.08% | +2.95 | 17.27% | +9.28 | -7.0 | +32.0 |
| 2022 | 20.99% | +6.93 | 21.25% | +12.50 | -5.0 | +42.0 |
| 2023 | 20.54% | +6.57 | 20.47% | +12.19 | -6.0 | +41.0 |
| 2024 | 20.81% | +7.11 | 20.59% | +12.59 | -6.0 | +43.0 |

![Hình 2.1: Tỷ lệ trễ và thời gian trễ trung bình](charts/CHART_RQ02_01_arrival_departure_delay_rate_trend.png)
*Hình 2.1: Diễn biến tỷ lệ trễ (≥15 phút) và giá trị trễ trung bình có dấu giai đoạn 2016–2024 (`RES-004`, `RES-005`).*

### 4.2. Độ lệch phải và hiện tượng bất đối xứng phân phối (Skewness & Long-Tail)
Phân tích so sánh giữa trung vị (P50) và phân vị 90 (P90) làm sáng tỏ cấu trúc phân phối thời gian trễ bay:
- **Trung vị âm ổn định:** P50 tính riêng cho từng năm theo thuật toán Spark GK-quantile dao động trong khoảng [-11.0, -5.0] phút (năm 2020 đạt -11.0 phút, cohort N = 4,312,091; năm 2022 đạt -6.0 phút, N = 6,413,416; các năm khác dao động từ -5.0 đến -8.0 phút). Điều này chứng minh hơn một nửa số chuyến bay nội địa Hoa Kỳ thực tế hạ cánh trước giờ ghi trên lịch trình. Tuyệt đối không gộp trung vị qua các năm do tính chất phi tuyến (`RES-006`).
- **Phân vị 90 kéo dãn:** Phân vị P90 luôn đạt giá trị dương rất lớn, dao động từ +14.0 phút (2020) đến +42.0 phút (2022, N = 6,413,416) và +43.0 phút (2024, N = 6,284,841). Khoảng cách giữa P90 và P50 lên tới 48–54 phút (`RES-007`).
- **Độ trễ trung bình dương:** Do bị kéo lệch bởi 10–20% các chuyến bay trễ rất nặng (trễ trên 1–3 giờ do dồn ứ dây chuyền), giá trị kỳ vọng (mean) bị kéo lên mức +3.5 đến +7.11 phút trong các năm bình thường (+6.93 phút năm 2022, +6.57 phút năm 2023, +7.11 phút năm 2024), hoàn toàn ngược chiều với trung vị.

![Hình 2.2: So sánh Trung vị P50 và Phân vị P90](charts/CHART_RQ02_03_arrival_delay_percentiles_p50_p90.png)
*Hình 2.2: Minh chứng định lượng về hiện tượng đuôi dài lệch phải của thời gian trễ đến (`RES-006`, `RES-007`).*

![Hình 2.3: Tính mùa vụ của độ trễ đến hàng tháng](charts/CHART_RQ02_04_monthly_arrival_delay_rate_seasonality.png)
*Hình 2.3: Tính mùa vụ của tỷ lệ trễ đến gộp theo tháng (`RES-004`).*

## 5. RQ-03: Hiệu suất khai thác theo Hãng bay, Sân bay & Tính bất đối xứng chặng bay

### 5.1. Hiệu suất các Hãng hàng không (Carrier Performance)
Trong số 19 hãng hàng không quan sát được trong 9 năm, nhóm 3 hãng có thị phần lớn nhất gồm:
1. **Southwest Airlines (WN):** Đạt 11,133,643 chuyến bay tích lũy (chiếm 20.36% sản lượng 9 năm), tỷ lệ đúng giờ gộp đạt 80.67% (tương ứng tỷ lệ trễ đến gộp 19.33%), độ trễ đến trung bình có dấu +3.85 phút (`RES-008`).
2. **Delta Air Lines (DL):** Đạt 7,821,658 chuyến bay tích lũy, duy trì hiệu suất đúng giờ hàng đầu trong nhóm các hãng truyền thống lớn với tỷ lệ đúng giờ gộp 85.81% (tỷ lệ trễ đến gộp chỉ 14.19%), độ trễ đến trung bình có dấu +0.66 phút (`RES-009`).
3. **American Airlines (AA):** Đạt 7,518,473 chuyến bay tích lũy, tỷ lệ đúng giờ gộp 79.61% (tương ứng tỷ lệ trễ đến gộp 20.39%), độ trễ đến trung bình có dấu +7.00 phút (`RES-009`).

| Hãng hàng không | Tổng số chuyến (9 năm) | Số năm hoạt động | Trễ đến TB (phút) | Trễ đi TB (phút) | Đúng giờ TB (%) |
|:---|---:|:---:|---:|---:|---:|
| WN | 11,133,643 | 9 | +3.85 | +10.56 | 80.67% |
| DL | 7,821,658 | 9 | +0.66 | +8.07 | 85.81% |
| AA | 7,518,473 | 9 | +7.00 | +12.24 | 79.61% |
| OO | 6,044,308 | 9 | +5.11 | +9.55 | 83.09% |
| UA | 5,083,571 | 9 | +4.35 | +10.81 | 81.35% |
| B6 | 2,236,608 | 9 | +11.34 | +16.89 | 73.61% |
| YX | 1,995,607 | 7 | +0.26 | +5.42 | 84.27% |
| AS | 1,859,574 | 9 | +0.87 | +4.00 | 82.40% |
| MQ | 1,747,132 | 7 | +4.04 | +7.30 | 81.64% |
| NK | 1,696,082 | 9 | +7.54 | +12.61 | 78.10% |

![Hình 3.1: Tỷ lệ Đến Đúng Giờ của Top 10 Hãng hàng không](charts/CHART_RQ03_01_top_carriers_on_time_performance.png)
*Hình 3.1: So sánh tỷ lệ đến đúng giờ gộp theo trọng số của 10 hãng bay lớn nhất (`RES-008`, `RES-009`).*

![Hình 3.2: Độ trễ Đến và Trễ Đi của các Hãng lớn](charts/CHART_RQ03_02_top_carriers_mean_delays.png)
*Hình 3.2: So sánh độ trễ đến và trễ khởi hành của các hãng bay chủ lực (`RES-009`).*

### 5.2. Điểm nghẽn tại các Trung tâm trung chuyển (Hub Congestion)
Các sân bay cửa ngõ vùng đô thị New York và Chicago thường xuyên nằm trong nhóm có tỷ lệ trễ xuất phát cao nhất quốc gia:
- **Newark Liberty (EWR):** Năm 2022 ghi nhận tỷ lệ trễ xuất phát lên tới 27.67% trên quy mô cohort N = 123,277 chuyến bay (đạt mức SUFFICIENT với ngưỡng min-N quy định cho sân bay là 365 chuyến/năm, `RES-010`).
- **Chicago O'Hare (ORD):** Năm 2024 đạt tỷ lệ trễ xuất phát 22.48% trên quy mô N = 251,485 chuyến bay (`RES-010`).
- **New York LaGuardia (LGA):** Năm 2019 đạt tỷ lệ trễ xuất phát 22.63% trên quy mô N = 166,283 chuyến bay (`RES-010`).

![Hình 3.3: Top Sân bay trễ xuất phát cao nhất](charts/CHART_RQ03_03_top_origin_airports_departure_delays.png)
*Hình 3.3: Tỷ lệ trễ cất cánh tại các trung tâm trung chuyển hàng không trọng điểm (`RES-010`).*

### 5.3. Tính bất đối xứng vận hành trên các chặng bay hai chiều (Route Asymmetry)
Phân tích 51,129 cohort chặng bay hàng năm chỉ ra tính bất đối xứng vận hành rõ rệt giữa hai chiều bay đối ứng ($A \to B$ so với $B \to A$), thỏa mãn tiêu chí min-N >= 100 chuyến bay/năm cho mỗi chiều:
- **Cặp hành lang Chicago (ORD) — New York LaGuardia (LGA):** Năm 2019, chiều ORD $\to$ LGA chịu tỷ lệ trễ đến 31.42% (N = 14,108) so với 28.60% (N = 14,169) của chiều LGA $\to$ ORD, tạo ra mức chênh lệch bất đối xứng 2.82% (2.8242 điểm phần trăm) trên tổng quy mô cặp chặng N = 28,277 chuyến bay (`RES-011`).
- **Cặp hành lang San Francisco (SFO) — Los Angeles (LAX):** Năm 2017, chiều SFO $\to$ LAX ghi nhận tỷ lệ trễ 20.35% so với 17.89% của chiều LAX $\to$ SFO, tạo mức chênh lệch 2.46% trên tổng quy mô cặp chặng N = 28,174 chuyến bay (`RES-011`).

![Hình 3.4: Bất đối xứng trễ trên các cặp chặng bay đối ứng](charts/CHART_RQ03_04_directed_route_delay_asymmetry.png)
*Hình 3.4: So sánh tỷ lệ trễ giữa hai chiều đối ứng trên các hành lang bay mật độ cao (`RES-011`).*

## 6. RQ-04: Cú sốc đại dịch 2020, Quá trình phục hồi & Tái tắc nghẽn (Quan sát phi nhân quả)

> [!IMPORTANT]
> **Nguyên tắc phương pháp luận:** Mối liên hệ giữa giai đoạn 2020 và các biến động hiệu suất bay được trình bày dưới góc độ quan sát thực nghiệm mô tả (observational patterns). Nghiên cứu không khẳng định mối quan hệ nhân quả duy nhất từ một yếu tố đơn lẻ khi chưa có mô hình kiểm soát nhiễu đa biến.

### 6.1. Sự trùng hợp quan sát giữa suy giảm sản lượng và cải thiện đúng giờ
Năm 2020 ghi nhận sự trùng hợp nổi bật giữa sự sụt giảm mạnh về quy mô khai thác và sự cải thiện vượt bậc của các chỉ số hiệu suất:
- Sản lượng toàn quốc giảm xuống 4,312,091 chuyến (-39.79% so với 2019).
- Tỷ lệ trễ đến giảm xuống mức kỷ lục 9.73% (giảm gần 10 điểm phần trăm so với mức 19.11% của năm 2019) (`RES-012`).
- Thời gian trễ đến trung bình có dấu chuyển sang giá trị âm (-5.11 phút, chính xác -5.1078 phút) (`RES-005`).
- Tháng 4/2020 ghi nhận tỷ lệ đúng giờ đạt đỉnh 95.15% (tỷ lệ trễ chỉ 4.85%) trên tổng số 179,835 chuyến bay (`RES-013`).

| Năm | Quy mô chuyến bay | Tỷ lệ trễ đến (%) | Trễ đến TB (phút) | Trễ đi TB (phút) | P90 trễ đến (phút) |
|:---:|---:|---:|---:|---:|---:|
| 2019 | 7,161,827 | 19.11% | +5.38 | +10.85 | +39.0 |
| 2020 | 4,312,091 | 9.73% | -5.11 | +1.97 | +14.0 |
| 2021 | 5,755,666 | 17.08% | +2.95 | +9.28 | +32.0 |

![Hình 4.1: Diễn biến Quy mô và Tỷ lệ trễ qua các giai đoạn](charts/CHART_RQ04_01_pandemic_period_kpi_comparison.png)
*Hình 4.1: So sánh hiệu suất các chỉ số cốt lõi trước, trong và sau năm 2020 (`RES-012`, `RES-014`).*

### 6.2. Hiện tượng tái tắc nghẽn hậu đại dịch (Post-Pandemic Re-congestion)
Khi nhu cầu đi lại phục hồi, sản lượng tăng dần: 5.76 triệu chuyến (2021), 6.41 triệu chuyến (2022), và 6.65 triệu chuyến (2023). Đáng chú ý, tỷ lệ trễ đến không chỉ quay lại mức trước đại dịch mà còn vượt qua mức năm 2019, đạt đỉnh 20.99% vào năm 2022 và duy trì ở mức trên 20.5% trong các năm 2023–2024 (`RES-014`).

Dữ liệu chỉ ra rằng việc tái phục hồi quy mô vận hành trong bối cảnh hạ tầng và nhân lực chưa đồng bộ có mối liên hệ mật thiết với việc gia tăng độ trễ mạng lưới.

![Hình 4.2: Biến động sản lượng và tỷ lệ đúng giờ theo tháng](charts/CHART_RQ04_02_2020_monthly_shock_and_rebound.png)
*Hình 4.2: Cú sốc đại dịch và xu hướng phục hồi hàng tháng giai đoạn 2019–2021 (`RES-013`, `RES-014`).*

## 7. RQ-05: Động học thời gian lăn bánh (Taxi Times) & Biên đệm lịch trình (Buffer Time)

### 7.1. Thời gian lăn ra cất cánh và lăn vào bến đỗ (Taxi-Out vs. Taxi-In)
Dữ liệu 9 năm chứng minh thời gian lăn bánh trên mặt đất đóng góp đáng kể vào tổng thời gian hoạt động của tàu bay:
- **Thời gian lăn ra (Taxi-Out):** Toàn quốc bình quân đạt 16.19 phút (2016) đến 17.95 phút (2024). Năm 2020 giảm xuống 15.25 phút (chính xác 15.2476 phút) khi sân bay thông thoáng (`RES-015`).
- **Thời gian lăn vào (Taxi-In):** Duy trì tương đối ổn định từ 7.45 phút (2016) đến 8.37 phút (2024), ít bị ảnh hưởng bởi tắc nghẽn đường cất hạ cánh so với Taxi-Out (`RES-016`).

| Năm | Taxi-Out TB (phút) | Taxi-In TB (phút) | Thời gian bay TB (phút) | Tổng thời gian thực (phút) | Lịch trình CRS (phút) | Đệm lịch trình (phút) |
|:---:|---:|---:|---:|---:|---:|---:|
| 2016 | 16.19 | 7.45 | 116.53 | 140.16 | 145.51 | +5.35 |
| 2017 | 16.77 | 7.50 | 117.52 | 141.80 | 147.13 | +5.34 |
| 2018 | 17.45 | 7.61 | 111.70 | 136.75 | 141.62 | +4.87 |
| 2019 | 17.42 | 7.75 | 111.82 | 136.98 | 142.45 | +5.47 |
| 2020 | 15.25 | 6.82 | 109.33 | 131.39 | 138.47 | +7.08 |
| 2021 | 16.00 | 7.65 | 113.65 | 137.30 | 143.63 | +6.33 |
| 2022 | 16.88 | 7.90 | 113.15 | 137.92 | 143.49 | +5.57 |
| 2023 | 17.44 | 8.10 | 115.00 | 140.54 | 146.16 | +5.62 |
| 2024 | 17.95 | 8.37 | 114.98 | 141.30 | 146.78 | +5.48 |

![Hình 5.1: Động học thời gian lăn bánh mặt đất](charts/CHART_RQ05_01_annual_taxi_time_trends.png)
*Hình 5.1: Diễn biến thời gian lăn ra (Taxi-Out) và lăn vào (Taxi-In) bình quân toàn quốc giai đoạn 2016–2024 (`RES-015`, `RES-016`).*

### 7.2. Điểm nghẽn lăn bánh tại các Sân bay đô thị lớn
Thời gian lăn ra chịu áp lực nghiêm trọng tại các sân bay có cấu hình đường băng phức tạp và mật độ khai thác dày đặc:
- **Sân bay John F. Kennedy (JFK):** Đứng đầu với thời gian Taxi-Out bình quân đạt 26.21 phút trong năm 2023 trên quy mô N = 129,620 chuyến bay (thỏa mãn tiêu chí min-N >= 365 chuyến/năm, `RES-017`).
- **Sân bay Newark Liberty (EWR):** Năm 2023 đạt thời gian Taxi-Out bình quân 23.76 phút trên quy mô N = 134,185 chuyến bay (`RES-017`).
- **Sân bay LaGuardia (LGA):** Năm 2023 đạt thời gian Taxi-Out bình quân 23.58 phút trên quy mô N = 158,552 chuyến bay (`RES-017`).
- **Sân bay Chicago O'Hare (ORD):** Năm 2023 đạt thời gian Taxi-Out bình quân 22.45 phút trên quy mô N = 253,478 chuyến bay (`RES-017`).

![Hình 5.2: Top 10 Sân bay có thời gian Taxi-Out dài nhất](charts/CHART_RQ05_03_top_airports_taxi_out_congestion.png)
*Hình 5.2: Bảng xếp hạng các sân bay có thời gian lăn ra cất cánh bình quân cao nhất (`RES-017`).*

### 7.3. Biên đệm lịch trình (Schedule Buffer) & Phân rã hành trình
Chênh lệch giữa thời gian dự kiến trên lịch trình và thời gian bay thực tế phản ánh chiến lược đệm lịch trình:
- **Định nghĩa toán học & Công bố phi nhân quả:** Đệm lịch trình được xác định như chênh lệch giữa hai giá trị kỳ vọng đã công bố (Difference of Published Means: $\mu_{\text{CRS}} - \mu_{\text{ACTUAL}}$), tuyệt đối không suy diễn quan hệ nhân quả hay can thiệp vận hành cấp vi mô khi chưa kiểm soát yếu tố thời tiết và luồng không lưu.
- Giá trị đệm lịch trình bình quân toàn quốc luôn dương trong toàn bộ 9 năm, dao động từ **+4.87 phút (2018)** đến **+7.08 phút (2020)** (`RES-018`).
- Năm 2020, đệm lịch trình đạt mức cao nhất (+7.08 phút, N = 4,312,091) do thời gian lăn bánh và bay thực tế giảm nhanh trong bối cảnh lịch trình chưa kịp điều chỉnh tương ứng.
- **Phân rã hành trình bay (`RES-019`):** Thời gian thực hiện hành trình toàn quốc (`ACTUAL_ELAPSED_TIME`) đạt bình quân 140.16 phút năm 2016 (N = 5,537,987; dao động 137.30 đến 142.39 phút giai đoạn 2016–2024). Việc phân tích tỷ trọng các thành phần hành trình (Air Time chiếm ~81%, Taxi-Out ~12%, Taxi-In ~6%) được trình bày dưới dạng so sánh cận biên giữa các giá trị trung bình đã công bố do sự chênh lệch nhỏ về số lượng mẫu hợp lệ giữa các chỉ số con.

![Hình 5.3: Biên đệm lịch trình hàng năm](charts/CHART_RQ05_02_elapsed_time_and_schedule_buffer.png)
*Hình 5.3: Mức chênh lệch thời gian đệm lịch trình bình quân toàn quốc 2016–2024 (`RES-018`, `RES-019`).*

## 8. Giới hạn phương pháp luận, Hạn chế dữ liệu & Cảnh báo sử dụng

Người sử dụng kết quả nghiên cứu cần lưu ý các ràng buộc kỹ thuật và phạm vi sau:
1. **Giới hạn độ phủ năm 2024 (Ràng buộc OR-05):** Do thiếu hụt tệp nguồn tháng 3/2024 từ nguồn cung cấp ban đầu, năm 2024 chỉ bao gồm 11 tháng quan sát (335 ngày, 6,284,841 chuyến bay, `RES-020`). Các so sánh tổng sản lượng năm 2024 với các năm đủ 12 tháng cần được diễn giải với sự thận trọng thích đáng.
2. **Tính chất mô tả của phân tích:** Toàn bộ các kết luận trong báo cáo đều mang tính thống kê mô tả (descriptive analytics). Không ngoại suy quan hệ nhân quả đơn lẻ đối với các cú sốc vĩ mô hoặc hiện tượng thời tiết.
3. **Phân nhánh dữ liệu thời tiết (Weather Data Branch):** Phân nhánh thời tiết T-015 hiện ở trạng thái `CONDITIONAL_NO_GO` và không thuộc phạm vi xử lý của báo cáo này.
4. **Độ chính xác phân vị (Percentile Approximation):** Các chỉ số phân vị P50 và P90 được tính toán thông qua thuật toán xấp xỉ phân vị của Spark với độ chính xác tương đối `relative_error = 0.01` theo đặc tả `KPI_SPEC.md`.
5. **Bảo toàn tính toàn vẹn:** Nghiên cứu này tuyệt đối không can thiệp, sửa đổi hay ghi đè lên các tập dữ liệu Parquet nền tảng đã được niêm phong tại T-012 và T-013.

## 9. Đề xuất can thiệp vận hành & Định hướng nghiên cứu mở rộng

### 9.1. Khuyến nghị cho Cơ quan Quản lý & Điều hành Sân bay (Airport Operators & FAA)
1. **Kiểm soát nghẽn mặt đất tại các Siêu Hub:** Ưu tiên tối ưu hóa luồng di chuyển trên đường lăn và lịch xếp hàng cất cánh (Surface Metering / Departure Queue Management) tại JFK, LGA, và ORD để cắt giảm thời gian Taxi-Out đang vượt mức 22–25 phút.
2. **Cân đối tải chặng bay hai chiều:** Điều chỉnh giờ cấp phép cất hạ cánh (Slot Allocation) trên các hành lang bay có tính bất đối xứng cao (như SFO-LAX) nhằm giảm thiểu tích lũy trễ dây chuyền.

### 9.2. Khuyến nghị cho các Hãng hàng không (Airlines)
1. **Chuẩn hóa chiến lược đệm lịch trình:** Tái đánh giá mức đệm lịch trình theo từng mùa vụ và khung giờ để tránh tình trạng hạ cánh sớm quá mức gây quá tải cổng đón tại sân bay đến, hoặc đệm quá ít dẫn đến tỷ lệ trễ tăng vọt.
2. **Quản trị rủi ro đuôi dài (Tail Risk Management):** Thay vì chỉ theo dõi trễ trung bình, cần thiết lập chỉ số cảnh báo sớm dựa trên biến động của phân vị P90 để kịp thời kích hoạt các phương án phục hồi đội bay.

### 9.3. Định hướng nghiên cứu tiếp theo
- Tích hợp dữ liệu thời tiết khi các điều kiện kiểm soát chất lượng tại Cổng G5/G6 đối với T-015 được thỏa mãn.
- Phát triển các mô hình chuỗi thời gian phân tách thành phần xu hướng và mùa vụ phục vụ dự báo ngắn hạn.

## 10. Phụ lục: Bảng tra cứu định danh kết quả (RES Register Index) & Danh mục biểu đồ

### 10.1. Danh mục định danh kết quả nghiên cứu (Results Register Index)
| Mã RES | Câu hỏi | Chỉ số KPI | Chiều phân tích | Giá trị quan sát | Tóm tắt phát hiện |
|:---|:---:|:---:|:---:|:---:|:---|
| `RES-001` | RQ-01 | KPI-01 | `year` | 54674003 | Tổng sản lượng quan sát 9 năm (2016-2024) đạt 54,674,003 chuyến bay; đ... |
| `RES-002` | RQ-01 | KPI-01 | `year-month` | 6 | Trong đúng 6/9 năm quan sát (2016-2018, 2021-2022, 2024), đỉnh sản lượ... |
| `RES-003` | RQ-01 | KPI-01 | `year-month` | 179835 | Tháng 4/2020 ghi nhận sản lượng giảm sâu còn 179,835 chuyến và tháng 5... |
| `RES-004` | RQ-02 | KPI-02 | `year` | 20.99 | Tỷ lệ trễ đến (>=15m) đạt đỉnh 20.99% năm 2022 trên 6,413,416 chuyến b... |
| `RES-005` | RQ-02 | KPI-03 | `year` | -5.11 | Độ trễ đến trung bình có dấu âm duy nhất vào năm 2020 (-5.11 phút, chí... |
| `RES-006` | RQ-02 | KPI-06 | `year` | -11.00 | Trung vị trễ đến (P50) đạt mức âm sâu kỷ lục vào năm 2020 (-11.0 phút ... |
| `RES-007` | RQ-02 | KPI-06 | `year` | 42.00 | Phân vị P90 kéo dãn lên tới +42 phút vào năm 2022 trên 6,413,416 chuyế... |
| `RES-008` | RQ-03 | KPI-01 | `carrier-year` | 11133643 | Southwest Airlines (WN) là hãng có sản lượng lớn nhất với 11,133,643 c... |
| `RES-009` | RQ-03 | KPI-02 | `carrier-year` | 14.19 | Delta Air Lines (DL, N=7,821,658) đạt hiệu suất đúng giờ hàng đầu tron... |
| `RES-010` | RQ-03 | KPI-04 | `origin-year` | 27.67 | Sân bay Newark Liberty (EWR) ghi nhận tỷ lệ trễ cất cánh (>=15m) đạt đ... |
| `RES-011` | RQ-03 | KPI-02 | `route-year` | 2.82 | Năm 2019, cặp tuyến đối đầu Chicago - New York (ORD <-> LGA) ghi nhận ... |
| `RES-012` | RQ-04 | KPI-01 | `year` | -39.79 | Năm 2020 ghi nhận sụt giảm sản lượng 39.79% so với 2019, đồng thời tỷ ... |
| `RES-013` | RQ-04 | KPI-02 | `year-month` | 95.15 | Tháng 4/2020 đạt tỷ lệ đúng giờ kỷ lục 95.15% (tỷ lệ trễ chỉ 4.85%) tr... |
| `RES-014` | RQ-04 | KPI-02 | `year` | 20.99 | Giai đoạn 2022-2024 chứng kiến hiện tượng tái tắc nghẽn khi tỷ lệ trễ ... |
| `RES-015` | RQ-05 | KPI-07 | `year` | 15.25 | Thời gian lăn ra cất cánh (Taxi-Out) bình quân năm 2020 giảm xuống 15.... |
| `RES-016` | RQ-05 | KPI-07 | `year` | 6.82 | Thời gian lăn vào bến đỗ (Taxi-In) bình quân toàn quốc năm 2020 giảm x... |
| `RES-017` | RQ-05 | KPI-07 | `origin-year` | 26.21 | Sân bay JFK dẫn đầu quốc gia về thời gian Taxi-Out bình quân năm 2023 ... |
| `RES-018` | RQ-05 | KPI-08 | `year` | 7.08 | Chênh lệch giữa hai giá trị trung bình đã công bố (CRS Elapsed TB - Ac... |
| `RES-019` | RQ-05 | KPI-08 | `year` | 140.16 | Thời gian hành trình thực tế trung bình (KPI-08 Actual Elapsed Time) n... |
| `RES-020` | RQ-01 | KPI-01 | `year` | 335 | Năm 2024 có đúng 11 tháng quan sát (335 ngày, khuyết tháng 3 theo OR-0... |

### 10.2. Danh mục biểu đồ trực quan hóa (Chart Inventory)
| Mã Biểu đồ | Tên file (PNG / SVG) | Định dạng | RES liên kết | Tiêu đề biểu đồ |
|:---|:---|:---:|:---:|:---|
| `CHART_RQ01_01_annual_accepted_volume` | `CHART_RQ01_01_annual_accepted_volume.png`<br>`CHART_RQ01_01_annual_accepted_volume.svg` | PNG (300 DPI)<br>SVG (Vector) | `RES-001`, `RES-020` | Quy mô Dữ liệu Quan sát Hàng năm (2016–2024) |
| `CHART_RQ01_02_monthly_volume_trend` | `CHART_RQ01_02_monthly_volume_trend.png`<br>`CHART_RQ01_02_monthly_volume_trend.svg` | PNG (300 DPI)<br>SVG (Vector) | `RES-002`, `RES-003` | Chuỗi Thời gian Lưu lượng Chặng bay Hàng tháng (2016–2024) |
| `CHART_RQ01_03_year_month_volume_heatmap` | `CHART_RQ01_03_year_month_volume_heatmap.png`<br>`CHART_RQ01_03_year_month_volume_heatmap.svg` | PNG (300 DPI)<br>SVG (Vector) | `RES-002`, `RES-003` | Bản Đồ Nhiệt Phân Bố Sản Lượng theo Tháng & Năm |
| `CHART_RQ02_01_arrival_departure_delay_rate_trend` | `CHART_RQ02_01_arrival_departure_delay_rate_trend.png`<br>`CHART_RQ02_01_arrival_departure_delay_rate_trend.svg` | PNG (300 DPI)<br>SVG (Vector) | `RES-004`, `RES-014` | Tỷ Lệ Chuyến Bay Chậm Trễ Hàng Năm (2016–2024) |
| `CHART_RQ02_02_signed_mean_arrival_departure_delays` | `CHART_RQ02_02_signed_mean_arrival_departure_delays.png`<br>`CHART_RQ02_02_signed_mean_arrival_departure_delays.svg` | PNG (300 DPI)<br>SVG (Vector) | `RES-005` | Độ Trễ Trung Bình Có Dấu Hàng năm (2016–2024) |
| `CHART_RQ02_03_arrival_delay_percentiles_p50_p90` | `CHART_RQ02_03_arrival_delay_percentiles_p50_p90.png`<br>`CHART_RQ02_03_arrival_delay_percentiles_p50_p90.svg` | PNG (300 DPI)<br>SVG (Vector) | `RES-006`, `RES-007` | Tính Bất Đối Xứng Phân Phối Trễ: P50 vs P90 Đến |
| `CHART_RQ02_04_monthly_arrival_delay_rate_seasonality` | `CHART_RQ02_04_monthly_arrival_delay_rate_seasonality.png`<br>`CHART_RQ02_04_monthly_arrival_delay_rate_seasonality.svg` | PNG (300 DPI)<br>SVG (Vector) | `RES-004` | Tính Mùa vụ Tỷ lệ Trễ Đến (2016–2024) |
| `CHART_RQ03_01_top_carriers_on_time_performance` | `CHART_RQ03_01_top_carriers_on_time_performance.png`<br>`CHART_RQ03_01_top_carriers_on_time_performance.svg` | PNG (300 DPI)<br>SVG (Vector) | `RES-008`, `RES-009` | Tỷ lệ Đến Đúng Giờ Top 10 Hãng Hàng không (2016–2024) |
| `CHART_RQ03_02_top_carriers_mean_delays` | `CHART_RQ03_02_top_carriers_mean_delays.png`<br>`CHART_RQ03_02_top_carriers_mean_delays.svg` | PNG (300 DPI)<br>SVG (Vector) | `RES-008`, `RES-009` | Độ Trễ Trung Bình theo Hãng Hàng Không (2016–2024) |
| `CHART_RQ03_03_top_origin_airports_departure_delays` | `CHART_RQ03_03_top_origin_airports_departure_delays.png`<br>`CHART_RQ03_03_top_origin_airports_departure_delays.svg` | PNG (300 DPI)<br>SVG (Vector) | `RES-010` | Top 10 Sân Bay Tỷ Lệ Trễ Khởi Hành Cao Nhất (2023) |
| `CHART_RQ03_04_directed_route_delay_asymmetry` | `CHART_RQ03_04_directed_route_delay_asymmetry.png`<br>`CHART_RQ03_04_directed_route_delay_asymmetry.svg` | PNG (300 DPI)<br>SVG (Vector) | `RES-011` | Tính Bất Đối Xứng Tỷ Lệ Trễ Tuyến Bay Có Hướng |
| `CHART_RQ04_01_pandemic_period_kpi_comparison` | `CHART_RQ04_01_pandemic_period_kpi_comparison.png`<br>`CHART_RQ04_01_pandemic_period_kpi_comparison.svg` | PNG (300 DPI)<br>SVG (Vector) | `RES-012`, `RES-014` | So sánh Các Chỉ Số Hiệu Suất Giai đoạn 2019–2021 |
| `CHART_RQ04_02_2020_monthly_shock_and_rebound` | `CHART_RQ04_02_2020_monthly_shock_and_rebound.png`<br>`CHART_RQ04_02_2020_monthly_shock_and_rebound.svg` | PNG (300 DPI)<br>SVG (Vector) | `RES-003`, `RES-013` | Cú Sốc Đại Dịch và Xu Hướng Phục Hồi (2019–2021) |
| `CHART_RQ05_01_annual_taxi_time_trends` | `CHART_RQ05_01_annual_taxi_time_trends.png`<br>`CHART_RQ05_01_annual_taxi_time_trends.svg` | PNG (300 DPI)<br>SVG (Vector) | `RES-015`, `RES-016` | Xu Hướng Thời Gian Lăn (Taxi Time) Hàng Năm (2016–2024) |
| `CHART_RQ05_02_elapsed_time_and_schedule_buffer` | `CHART_RQ05_02_elapsed_time_and_schedule_buffer.png`<br>`CHART_RQ05_02_elapsed_time_and_schedule_buffer.svg` | PNG (300 DPI)<br>SVG (Vector) | `RES-018`, `RES-019` | Thời Gian Hành Trình và Đệm Lịch Trình (2016–2024) |
| `CHART_RQ05_03_top_airports_taxi_out_congestion` | `CHART_RQ05_03_top_airports_taxi_out_congestion.png`<br>`CHART_RQ05_03_top_airports_taxi_out_congestion.svg` | PNG (300 DPI)<br>SVG (Vector) | `RES-017` | Top 10 Sân Bay Taxi-Out Dài Nhất (2023) |
