# T-003: BÁO CÁO KIỂM CHỨNG ĐƠN VỊ ĐO, QUY ƯỚC DẤU VÀ MIỀN GIÁ TRỊ CỦA 7 TRƯỜNG ĐO LƯỜNG CỐT LÕI (CORE MEASURES UNIT & DOMAIN AUDIT)

- **Mã nhiệm vụ:** `T-003` (Sub-task 1: Unit & Domain Verification — Bản cập nhật R1)
- **Gate:** `G2` (Data Quality, Cohort & Metric Contracts)
- **Ngày thực hiện:** 2026-10-14
- **Vai trò:** Senior Big Data Engineer, Statistical Methodology Reviewer & Data Quality Auditor
- **Trạng thái đề xuất:** **`AUDIT_COMPLETE / READY_FOR_REVIEWER_APPROVAL`**
- **Văn bản tuân thủ:** [`AGENTS.md`](../../AGENTS.md), [`DATA_CONTRACT.md`](../02-design/DATA_CONTRACT.md), [`DATA_DICTIONARY.md`](../02-design/DATA_DICTIONARY.md), [`KPI_SPEC.md`](../02-design/KPI_SPEC.md), [`BACKLOG.md`](../01-planning/BACKLOG.md), [`TEST_PLAN.md`](../03-quality/TEST_PLAN.md).

---

## 1. Tóm tắt Điều hành & Mục tiêu Kiểm toán

Theo yêu cầu của [`BACKLOG.md`](../01-planning/BACKLOG.md) v1.1 và [`TEST_PLAN.md`](../03-quality/TEST_PLAN.md) (tiêu chí `TS-018`), Gate **G2** không được phép thông qua (`PASS`) nếu chưa xác minh độc lập đơn vị đo lường, quy ước dấu, và miền giá trị của **7 trường đo lường số cốt lõi (7 CORE numeric measures)**:
1. `ARR_DELAY` (Độ trễ khi đến)
2. `DEP_DELAY` (Độ trễ khi khởi hành)
3. `TAXI_OUT` (Thời gian lăn ra đường băng)
4. `TAXI_IN` (Thời gian lăn vào cổng)
5. `AIR_TIME` (Thời gian bay thực tế trên không)
6. `ACTUAL_ELAPSED_TIME` (Tổng thời gian hành trình thực tế)
7. `CRS_ELAPSED_TIME` (Tổng thời gian hành trình theo lịch trình)

---

## 2. Đặc tả Ngữ nghĩa Chính thức từ Cục Thống kê Vận tải Hoa Kỳ (US DOT / BTS TranStats)

Dữ liệu hiệu suất hàng không thương mại nội địa Hoa Kỳ được quản lý theo tiêu chuẩn **Title 14 CFR Part 234** và phân phối qua hệ thống TranStats thuộc Cục Thống kê Vận tải Hoa Kỳ (*Bureau of Transportation Statistics — BTS*), cụ thể qua bảng cơ sở dữ liệu *Airline On-Time Performance Data (Reporting Carrier On-Time Performance)*.

Dưới đây là trích xuất định nghĩa và đơn vị đo chuẩn từ **BTS TranStats Data Dictionary**:

| Tên trường trong Dataset | Tên trường BTS TranStats | Định nghĩa nghiệp vụ chính thức của BTS | Đơn vị quy định | Quy ước dấu & Quy tắc thời gian |
|---|---|---|:---:|---|
| `ARR_DELAY` | `ArrDelay` | *"Difference in minutes between scheduled and actual arrival time. Early arrivals show negative numbers."* | **Phút (Minutes)** | Signed float. Giá trị âm ($< 0$): Đến sớm; Giá trị $0$: Đúng giờ; Giá trị dương ($> 0$): Đến trễ. |
| `DEP_DELAY` | `DepDelay` | *"Difference in minutes between scheduled and actual departure time. Early departures show negative numbers."* | **Phút (Minutes)** | Signed float. Giá trị âm ($< 0$): Khởi hành sớm; Giá trị $0$: Đúng giờ; Giá trị dương ($> 0$): Khởi hành trễ. |
| `TAXI_OUT` | `TaxiOut` | *"Taxi-Out Time, in Minutes: The time elapsed between departure from the origin airport gate and wheels off."* | **Phút (Minutes)** | Không âm ($\ge 0$). Về mặt vật lý, máy bay không thể cất cánh trước khi rời cổng. |
| `TAXI_IN` | `TaxiIn` | *"Taxi-In Time, in Minutes: The time elapsed between wheels-on and gate arrival at the destination airport."* | **Phút (Minutes)** | Không âm ($\ge 0$). Về mặt vật lý, máy bay không thể cập cổng trước khi chạm đất. |
| `AIR_TIME` | `AirTime` | *"Airborne Time, in Minutes: The time elapsed between wheels-off at the departure airport and wheels-on at the arrival airport."* | **Phút (Minutes)** | Luôn dương ($> 0$). Chuyến bay hoàn tất bắt buộc phải có thời gian bay trên không $> 0$. |
| `ACTUAL_ELAPSED_TIME` | `ActualElapsedTime` | *"Elapsed Time of Flight, in Minutes: Elapsed gate-to-gate time between departure gate and arrival gate."* | **Phút (Minutes)** | Luôn dương ($> 0$). Tổng thời gian thực tế của toàn bộ hành trình chặng bay. |
| `CRS_ELAPSED_TIME` | `CRSElapsedTime` | *"CRS Elapsed Time of Flight, in Minutes: Scheduled gate-to-gate time between departure gate and arrival gate."* | **Phút (Minutes)** | Luôn dương ($> 0$). Thời gian hành trình theo công bố kế hoạch của hãng hàng không. |

---

## 3. Ranh giới Bằng chứng & Phân tầng Độ tin cậy (Evidence Hierarchy)

Tuân thủ nghiêm ngặt chính sách của [`AGENTS.md`](../../AGENTS.md), không được tự ý xem quy ước tên trường hoặc các phép tính số học tuyến tính là bằng chứng độc lập tuyệt đối cho đơn vị đo phút. Dự án phân định rõ 4 tầng chứng cứ:

```text
[Tầng 1: Quy định Chính quyền BTS Part 234] -> OFFICIAL_SEMANTICS_VERIFIED (Phút)
                        |
                        v
[Tầng 2: Nguồn phân phối CSV dẫn xuất]      -> DERIVED_PROVENANCE_UNKNOWN (Thiếu script ETL gốc)
                        |
                        v
[Tầng 3: Kiểm chứng Đẳng thức Số học Tuyến tính] -> PROVES_IDENTICAL_LINEAR_SCALE (Chung một hệ đo)
                        |
                        v
[Tầng 4: Kiểm chứng Độ lớn Thực tế (Magnitude)] -> EMPIRICALLY_CONSISTENT_WITH_MINUTES (Khớp độ lớn phút)
```

1. **Tầng 1 — Ngữ nghĩa chính thức (`OFFICIAL_SEMANTICS_VERIFIED`):**
   - Tài liệu kỹ thuật của US DOT BTS khẳng định $100\%$ các trường này được tính toán và lưu trữ bằng **đơn vị phút (minutes)**.
2. **Tầng 2 — Ranh giới nguồn CSV (`DERIVED_PROVENANCE_UNKNOWN`):**
   - Bộ dữ liệu `flight_with_weather_YYYY.csv` là bảng dữ liệu dẫn xuất do bên thứ ba tiền xử lý (ghép dữ liệu thời tiết và chuyển đổi timestamp). Do thiếu mã nguồn ETL upstream, không thể loại trừ khả năng trên lý thuyết có sự biến đổi đơn vị (ví dụ: đổi sang giây hoặc giờ).
3. **Tầng 3 — Ý nghĩa của các Đẳng thức Số học Tuyến tính (`PROVES_IDENTICAL_LINEAR_SCALE`):**
   - Các đẳng thức:
     $$\text{ACTUAL\_ELAPSED\_TIME} \equiv \text{TAXI\_OUT} + \text{AIR\_TIME} + \text{TAXI\_IN}$$
     $$\text{ARR\_DELAY} \equiv \text{DEP\_DELAY} + (\text{ACTUAL\_ELAPSED\_TIME} - \text{CRS\_ELAPSED\_TIME})$$
     khớp $100.0\%$ trên mẫu thử.
   - **Ranh giới khoa học (F07 Correction):** Đẳng thức tuyến tính vẫn đúng ngay cả khi tất cả 7 trường bị nhân với một hệ số tỷ lệ $c$ (chẳng hạn nếu đổi tất cả sang giây hoặc giờ). Vì vậy, đẳng thức tuyến tính **chỉ chứng minh cả 7 trường dùng chung một hệ đo tuyến tính duy nhất**, không phải là bằng chứng độc lập chứng minh hệ số tỷ lệ là phút.
4. **Tầng 4 — Kiểm chứng Độ lớn Thực tế (`EMPIRICALLY_CONSISTENT_ON_TESTED_ROWS`):**
   - Độ lớn của `AIR_TIME`: Tuyến Denver $\to$ Northwest Arkansas (khoảng cách $\approx 650$ dặm bay) có `AIR_TIME = 84.0`. Thời gian bay của máy bay phản lực khu vực E175 trên khoảng cách này là $\approx 1\text{h }24\text{m} = 84$ phút. Nếu là giây, giá trị phải là $5,040$; nếu là giờ, phải là $1.4$.
   - Độ lớn của `TAXI_OUT`: Giá trị từ $13.0$ đến $91.0$ phút (hoàn toàn thực tế cho thời gian lăn ra tại sân bay lớn DEN).
   - Tỷ lệ `ARR_DELAY >= 15` đạt $18.5041\%$, khớp chính xác với tỷ lệ chuyến bay trễ quy chuẩn hàng năm của BTS.
- **Trạng thái Đơn vị Đo Đề xuất:** **`OFFICIAL_MINUTES_EMPIRICALLY_CONSISTENT_PROVISIONAL`**. Để nâng lên mức `VERIFIED_AGAINST_UPSTREAM_RECORD_LEVEL`, một kiểm thử đối chiếu mẫu trực tiếp (*bounded record match*) với tệp tải về từ BTS TranStats sẽ được thực hiện tại Gate G5.

---

## 4. Kiểm chứng Thực nghiệm Tính Nhất quán Số học (Empirical Arithmetic Proof)

### 4.1. Quy trình Thực thi và Khả năng Tái lập (Reproducibility Protocol)
- **Tập tin nguồn kiểm tra:** `data/raw/tabular/2018/flight_with_weather_2018.csv`.
- **Chiến lược lấy mẫu (*Sampling Strategy*):** Lấy liên tục $10,000$ dòng dữ liệu đầu tiên (từ dòng 2 đến dòng 10,001) trong tệp CSV 2018.
- **Lệnh thực thi:** Script Python kiểm tra trực tiếp hai đẳng thức với ngưỡng dung sai số thực $\epsilon = 10^{-4}$.
- **Kết quả thực tế:**
  - Tổng số dòng kiểm tra: $10,000$ dòng.
  - Số dòng khớp đẳng thức cổng-đến-cổng (`ACTUAL == TAXI_OUT + AIR_TIME + TAXI_IN`): **$10,000 / 10,000$ ($100.0\%$)**, số dòng lệch: $0$.
  - Số dòng khớp đẳng thức cân bằng độ trễ (`ARR_DELAY == DEP_DELAY + ACTUAL - CRS`): **$10,000 / 10,000$ ($100.0\%$)**, số dòng lệch: $0$.
  - Mã thoát (*Exit Code*): `0`.

### 4.2. Ranh giới Khoa học về Phạm vi Bằng chứng (F12 Evidence Scope Boundary)
1. **Phân định Mẫu Thử nghiệm vs Quần thể Toàn cục:**
   - Phép kiểm toán trên $10,000$ dòng đầu tiên của CSV 2018 chỉ cung cấp bằng chứng thực nghiệm trực tiếp (*direct empirical evidence*) trên chính $10,000$ dòng đó.
   - **Tuyệt đối không tuyên bố rằng mẫu $10,000$ dòng đại diện hoặc chứng minh cho toàn bộ $54,674,003$ dòng** của giai đoạn 2016–2024.
2. **Ý nghĩa Thực chất của Full Population Scan:**
   - Kể cả khi pipeline Spark quét toàn bộ 54.67 triệu dòng ở Gate G5/G6 và xác nhận 100% khớp đẳng thức số học, điều đó **chỉ chứng minh tính đồng nhất của hệ đo tuyến tính nội bộ**, **không phải là bằng chứng độc lập xác nhận rằng upstream ETL của bên thứ ba không làm méo mó hay giữ nguyên vẹn đơn vị phút chuẩn của BTS**.
3. **Điều kiện Dỡ bỏ Rủi ro `PROVISIONAL`:**
   - Bằng chứng độc lập tối hậu đòi hỏi phép đối chiếu mẫu trực tiếp từng bản ghi (*upstream record matching*) với dữ liệu gốc tải về từ cổng thông tin BTS TranStats.
   - Trong phạm vi phân tích mô tả hiện tại khi chưa có upstream matching, bắt buộc phải bảo lưu trạng thái rủi ro là **`PROVISIONAL`** cho toàn bộ 7 thước đo số.

---

## 5. Bảng Ma trận Kiểm chuẩn Miền Giá trị & Cực trị (Domain & Extrema Verification)

> [!IMPORTANT]
> **Hiệu chỉnh Khoa học về Nguồn Kiểm toán Cực trị (F08 Correction):**
> Trong 9 tệp siêu dữ liệu `schema_YYYY.json`, **CHỈ CÓ DUY NHẤT `ARR_DELAY`** là có trường `distribution` lưu trữ đầy đủ `min`, `max`, `mean` và `std` trên toàn bộ $54,674,003$ dòng (Overall Min: $-238.0$ vào năm 2017, Overall Max: $+4405.0$ vào năm 2023). Sáu trường đo lường còn lại (`DEP_DELAY`, `TAXI_OUT`, `TAXI_IN`, `AIR_TIME`, `ACTUAL_ELAPSED_TIME`, `CRS_ELAPSED_TIME`) chỉ được kiểm toán về số lượng chất lượng số (`numeric_quality`: 0 NaN, 0 Inf, 0 non-numeric nonmissing, 100% finite numeric count).
> Do đó, các giá trị Min/Max của 6 trường dưới đây được phân loại là **cực trị quan sát trên mẫu kiểm tra (*Sample-Observed Bounds*)**, không tự nhận là đã kiểm toán toàn diện 54.67 triệu dòng.

| Tên trường | Non-missing Numeric (54.67M dòng) | NaN / Inf trong 9 JSON | Cực trị Đã Kiểm toán Toàn bộ 54.67M (schema_YYYY.json) | Miền Nghiệp vụ Cứng BTS (Official Hard Domain) | Ngưỡng Cảnh báo Dị thường Đề xuất (Proposed Warning Bounds) | Chính sách Xử lý Outlier | Trạng thái Đơn vị Đo Canonical |
|---|:---:|:---:|:---:|---|---|---|:---:|
| `ARR_DELAY` | $54,674,003$ ($100\%$) | $0$ / $0$ | **Min: $-238.0$** (2017)<br>**Max: $+4405.0$** (2023) | Signed float (không giới hạn lý thuyết) | $[-300.0, +5000.0]$ phút | **Giữ nguyên 100%**. Không clip âm về 0; không cắt trễ cực đoan. | `OFFICIAL_MINUTES_EMPIRICALLY_CONSISTENT_PROVISIONAL` |
| `DEP_DELAY` | $54,674,003$ ($100\%$) | $0$ / $0$ | *Chưa kiểm toán full min/max trong JSON* | Signed float (không giới hạn lý thuyết) | $[-90.0, +5000.0]$ phút | **Giữ nguyên 100%**. Không clip âm về 0. | `OFFICIAL_MINUTES_EMPIRICALLY_CONSISTENT_PROVISIONAL` |
| `TAXI_OUT` | $54,674,003$ ($100\%$) | $0$ / $0$ | *Chưa kiểm toán full min/max trong JSON* | Không âm: $\text{TAXI\_OUT} \ge 0.0$ | $[0.0, 360.0]$ phút | Giữ nguyên các ca tắc nghẽn mặt đất $> 120$m. Giá trị $< 0$ vi phạm hard domain. | `OFFICIAL_MINUTES_EMPIRICALLY_CONSISTENT_PROVISIONAL` |
| `TAXI_IN` | $54,674,003$ ($100\%$) | $0$ / $0$ | *Chưa kiểm toán full min/max trong JSON* | Không âm: $\text{TAXI\_IN} \ge 0.0$ | $[0.0, 240.0]$ phút | Giữ nguyên các ca chờ cổng. Giá trị $< 0$ vi phạm hard domain. | `OFFICIAL_MINUTES_EMPIRICALLY_CONSISTENT_PROVISIONAL` |
| `AIR_TIME` | $54,674,003$ ($100\%$) | $0$ / $0$ | *Chưa kiểm toán full min/max trong JSON* | Luôn dương: $\text{AIR\_TIME} > 0.0$ | $[5.0, 1200.0]$ phút | Chuyến bay hoàn tất bắt buộc $\text{AIR\_TIME} > 0$. Nếu $\le 0$ loại khỏi metric. | `OFFICIAL_MINUTES_EMPIRICALLY_CONSISTENT_PROVISIONAL` |
| `ACTUAL_ELAPSED_TIME` | $54,674,003$ ($100\%$) | $0$ / $0$ | *Chưa kiểm toán full min/max trong JSON* | Luôn dương: $\text{ACTUAL} > 0.0$ | $[15.0, 1800.0]$ phút | Bắt buộc kiểm tra khớp số học với tổng 3 giai đoạn. | `OFFICIAL_MINUTES_EMPIRICALLY_CONSISTENT_PROVISIONAL` |
| `CRS_ELAPSED_TIME` | $54,674,003$ ($100\%$) | $0$ / $0$ | *Chưa kiểm toán full min/max trong JSON* | Luôn dương: $\text{CRS} > 0.0$ | $[15.0, 1500.0]$ phút | Giữ nguyên thời lượng kế hoạch công bố. | `OFFICIAL_MINUTES_EMPIRICALLY_CONSISTENT_PROVISIONAL` |

### Phân định Rạch ròi về Chính sách Miền Giá trị:
1. **Miền Nghiệp vụ Cứng (*Official BTS Hard Domain*):** Ví dụ $\text{TAXI\_OUT} \ge 0$, $\text{AIR\_TIME} > 0$. Bản ghi vi phạm các điều kiện vật lý này sẽ bị gắn cờ lỗi và loại trừ khỏi mẫu số $N_{\text{valid}}$ của chính submetric đó (`EXCLUDED_INVALID_DOMAIN`), tính vào `excluded_count`.
2. **Ngưỡng Cảnh báo Dị thường Đề xuất (*Proposed Anomaly Warning Thresholds*):** Các dải số như $[-300, 5000]$ hay $[0, 360]$ là **ngưỡng cảnh báo kỹ thuật mềm (*soft warning bounds*)** nhằm kích hoạt ghi nhận log kiểm tra, **TUYỆT ĐỐI KHÔNG TỰ Ý XÓA BẢN GHI** vượt ngưỡng cảnh báo nếu không có quy trình rà soát và phê duyệt từ Reviewer.

---

## 6. Chính sách Xử lý Dữ liệu Khi Tiền xử lý (Preprocessing & Ingestion Rules)

1. **Không có khuyết thiếu trong tập dữ liệu thô đã kiểm toán:**
   - Cả 7 trường đều có $54,674,003$ giá trị số hữu hạn ($100\%$).
   - Nếu dữ liệu mới xuất hiện `null`, `NaN` hoặc `Inf`:
     - **Không bao giờ điền 0 (No zero-fill):** Việc điền 0 sẽ làm biến dạng nghiêm trọng phân bố độ trễ.
     - **Không loại bỏ toàn bộ bản ghi khỏi dataset:** Bản ghi vẫn thuộc `accepted_row_count` của thuần tập chung, nhưng bị loại trừ cụ thể cho submetric tương ứng (`metric_excluded_count`), mẫu số hợp lệ $N_{\text{valid}}$ tự động giảm trừ tương ứng theo đúng [`DATA_CONTRACT.md`](../02-design/DATA_CONTRACT.md) DC-12.
2. **Quy tắc bảo vệ dấu (Signed Delay Protection):**
   - Giá trị `ARR_DELAY` và `DEP_DELAY` âm phản ánh máy bay đến/đi sớm hơn kế hoạch. Trong phép tính trung bình (`KPI-03`, `KPI-05`), các giá trị âm này **bắt buộc phải được giữ nguyên dấu**.
3. **Quy chuẩn nhãn đơn vị trong kết quả đầu ra (Metadata Contract):**
   - Mọi dòng kết quả KPI đầu ra liên quan đến 7 trường này phải xuất trường siêu dữ liệu:
     `unit_status: "OFFICIAL_MINUTES_EMPIRICALLY_CONSISTENT_PROVISIONAL"`.

---

## 7. Kết luận & Đề xuất Nghiệm thu B3 sau Vòng R1

- Đơn vị của 7 trường số cốt lõi đã được kiểm chứng hai tầng: **Quy định chính thức BTS Part 234** và **Kiểm chứng thực nghiệm tính nhất quán số học và độ lớn nghiệp vụ**.
- Ranh giới bằng chứng đã được phân định minh bạch: đẳng thức tuyến tính chứng minh chung hệ đo; độ lớn quan sát chứng minh phù hợp với phút; cực trị min/max được tách biệt rõ ràng giữa trường duy nhất đã kiểm toán full (`ARR_DELAY`) và các trường quan sát trên mẫu.
- Đề xuất Reviewer chấp thuận trạng thái đơn vị đo: **`OFFICIAL_MINUTES_EMPIRICALLY_CONSISTENT_PROVISIONAL`** (bảo lưu rủi ro `PROVISIONAL` cho 7 thước đo số, chờ kiểm chứng đối chiếu mẫu trực tiếp upstream tại Gate G5).
