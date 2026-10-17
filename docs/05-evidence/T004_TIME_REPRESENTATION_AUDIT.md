# T-004: BÁO CÁO KIỂM TOÁN BIỂU DIỄN THỜI GIAN VÀ CHUỖI TIMESTAMP TRONG TẬP DỮ LIỆU THÔ (TIME REPRESENTATION AUDIT)

- **Mã nhiệm vụ:** `T-004` (Sub-task 1: Raw Timestamp Representation & Syntactic Audit)
- **Gate kiểm soát:** `G2` (Data Quality, Cohort & Metric Contracts)
- **Ngày thực hiện:** 2026-10-14
- **Vai trò:** Senior Data Engineer, Big Data Quality Auditor & Technical Reviewer
- **Trạng thái:** **`AUDIT_COMPLETE`**
- **Văn bản tuân thủ:** [`AGENTS.md`](../../AGENTS.md), [`docs/01-planning/BACKLOG.md`](../01-planning/BACKLOG.md), [`docs/02-design/DATA_CONTRACT.md`](../02-design/DATA_CONTRACT.md), [`docs/02-design/DATA_DICTIONARY.md`](../02-design/DATA_DICTIONARY.md), [`docs/02-design/DECISIONS.md`](../02-design/DECISIONS.md), [`docs/03-quality/TEST_PLAN.md`](../03-quality/TEST_PLAN.md) (`TS-009`, `TS-010`).

---

## 1. Mục tiêu & Bối cảnh Kiểm toán

Trong thiết kế hệ thống Big Data phân tích chuyến bay, biểu diễn thời gian là một trong những thành phần dễ gây sai lệch nhất (*temporal representation hazards*). Dữ liệu gốc của Cục Thống kê Vận tải Hoa Kỳ (BTS TranStats) lưu trữ các mốc thời gian dưới dạng số nguyên `HHMM` (ví dụ `0900` cho 9:00 sáng, `2359` cho 11:59 đêm, và `2400` cho nửa đêm).

Tuy nhiên, tập dữ liệu thực tế của dự án bao gồm 9 tệp CSV dẫn xuất `flight_with_weather_YYYY.csv` (2016–2024) với tổng cộng $54,674,003$ bản ghi, đã qua một giai đoạn tiền xử lý ETL của bên thứ ba (*upstream derivative ETL*).

Mục tiêu của báo cáo này là:
1. Xác minh định dạng biểu diễn thực tế của 7 trường thời gian trong toàn bộ 9 tệp CSV thô.
2. Kiểm tra tính hợp lệ cú pháp, tỷ lệ khuyết thiếu và tính phân bổ của các trường thời gian.
3. Làm rõ sự khác biệt giữa biểu diễn thời gian trong CSV thô và ngữ nghĩa BTS gốc.

---

## 2. Danh mục 7 Trường Thời gian trong Schema 34 Cột

Theo [`DATA_DICTIONARY.md`](../02-design/DATA_DICTIONARY.md), tập dữ liệu chứa 7 trường biểu diễn thời gian:

| STT | Tên trường | Định nghĩa nghiệp vụ BTS | Ý nghĩa trong nghiên cứu |
|:---:|---|---|---|
| 1 | `FL_DATE` | Flight Date (Ngày vận hành theo lịch trình của chuyến bay) | Khóa phân vùng ngày và mốc dịch vụ cơ sở (*service calendar date*). |
| 2 | `CRS_DEP_TIME` | Computer Reservation System Scheduled Departure Time | Mốc giờ dự kiến khởi hành theo công bố của hãng. |
| 3 | `DEP_TIME` | Actual Departure Time (Gate departure) | Mốc giờ máy bay thực tế rời cổng xuất phát. |
| 4 | `WHEELS_OFF` | Wheels Off Time (Takeoff time) | Mốc giờ bánh máy bay thực tế rời đường băng cất cánh. |
| 5 | `WHEELS_ON` | Wheels On Time (Touchdown time) | Mốc giờ bánh máy bay thực tế chạm đường băng hạ cánh. |
| 6 | `CRS_ARR_TIME` | CRS Scheduled Arrival Time | Mốc giờ dự kiến hạ cánh / cập cổng tại điểm đến. |
| 7 | `ARR_TIME` | Actual Arrival Time (Gate arrival) | Mốc giờ máy bay thực tế cập cổng tại sân bay đích. |

---

## 3. Kết quả Kiểm toán Biểu diễn Thực tế trên Dữ liệu Thô (Empirical Audit Findings)

### 3.1. Định dạng Chuỗi Thực tế (Physical Storage Format)
Khác với giả định ban đầu về số nguyên `HHMM`, kết quả kiểm tra trực tiếp trên cả 9 tệp CSV từ 2016 đến 2024 xác nhận:
- **100% các trường thời gian đều được lưu trữ dưới dạng chuỗi ký tự timestamp:**
  $$\text{Định dạng: } \texttt{YYYY-MM-DD HH:MM:SS}$$
  (Ví dụ: `2016-01-01 09:00:00`, `2018-06-21 20:07:00`, `2024-01-01 12:52:00`).
- Không có trường thời gian nào ở dạng số thực hay số nguyên `HHMM` (như `900.0` hay `2007`).
- Chuỗi thời gian sử dụng dấu cách phân cách giữa ngày và giờ, và dấu hai chấm phân cách giờ, phút, giây (`%Y-%m-%d %H:%M:%S`).

### 3.2. Kiểm toán Trường `FL_DATE` (Service Date Invariant)
- **100% giá trị của `FL_DATE`** trên toàn bộ $54,674,003$ bản ghi đều có thành phần giờ-phút-giây cố định bằng nửa đêm:
  $$\texttt{FL\_DATE} = \texttt{YYYY-MM-DD 00:00:00}$$
- Không có bất kỳ dòng nào có thành phần giờ khác `00:00:00` (*zero non-midnight values*).
- Không có giá trị `null`, rỗng, hoặc định dạng không hợp lệ.
- **Hệ quả kiến trúc:** Trường `FL_DATE` tương đương một cách đơn ánh (*deterministically equivalent*) với ngày lịch dịch vụ (*service calendar date*). Khi nạp vào Spark, trường này được trích xuất an toàn thành kiểu `DateType` (`to_date(FL_DATE)`).

### 3.3. Kiểm toán Thành phần Ngày của `CRS_DEP_TIME` và `CRS_ARR_TIME`
Kiểm toán độc lập trên $48,389,162$ bản ghi (giai đoạn 2016–2023) từ hồ sơ `canonical_schedule_datetime_representation_audit.md` và kiểm tra đối chứng năm 2024 chỉ ra quy luật nhất quán của upstream ETL:
1. **Thành phần ngày của `CRS_DEP_TIME` luôn bằng `FL_DATE` (100%):**
   - Không có trường hợp nào `CRS_DEP_TIME` mang ngày hôm trước hoặc ngày hôm sau của `FL_DATE`.
2. **Thành phần ngày của `CRS_ARR_TIME` CŨNG LUÔN BẰNG `FL_DATE` (100%):**
   - Kể cả với các chuyến bay dự kiến bay qua nửa đêm (ví dụ cất cánh lúc 22:25 và hạ cánh lúc 00:30 sáng hôm sau), upstream ETL vẫn gán thành phần ngày của `CRS_ARR_TIME` bằng đúng ngày của `FL_DATE`!
   - Ví dụ quan sát được:
     `FL_DATE = 2016-06-01 00:00:00`
     `CRS_DEP_TIME = 2016-06-01 22:25:00`
     `CRS_ARR_TIME = 2016-06-01 00:00:00`
   - **Hệ quả nghiêm trọng:** Thành phần ngày của `CRS_ARR_TIME` **KHÔNG PHẢI LÀ NGÀY ĐẾN THEO LỊCH TRÌNH THỰC TẾ**. Upstream ETL đã kẹp cứng ngày xuất phát vào cả mốc đến.

### 3.4. Kiểm toán Thành phần Ngày của Các Mốc Hoạt động Thực tế (`DEP_TIME`, `ARR_TIME`, `WHEELS_OFF`, `WHEELS_ON`)
- Tương tự như lịch trình, upstream ETL đã gắn chuỗi ngày của `FL_DATE` vào toàn bộ các mốc thời gian hoạt động thực tế.
- Khi một chuyến bay bị trễ nghiêm trọng và thực tế cất cánh hoặc hạ cánh vào ngày hôm sau (hoặc hôm sau nữa), chuỗi timestamp lưu trữ trong CSV vẫn giữ nguyên ngày `FL_DATE` ban đầu!
- Phản ví dụ điển hình: Chuyến bay `YX 3624` ngày 2018-06-21 cất cánh lúc 10:44 sáng ngày 22/06/2018 (trễ 877 phút), nhưng trong CSV được lưu là `2018-06-21 10:44:00`!

---

## 4. Kiểm toán Ngữ nghĩa 24:00 & Mốc Nửa đêm (2400 Semantics Audit)

Trong quy định của BTS TranStats:
- `2400` đại diện cho mốc nửa đêm kết thúc ngày vận hành.
- `0000` đại diện cho mốc nửa đêm bắt đầu ngày vận hành mới.

Kết quả kiểm toán trên dữ liệu thô:
1. **Khởi hành lúc đúng nửa đêm (`00:00:00`):**
   - Trên toàn bộ 48.38 triệu dòng (2016–2023), số lượng chuyến bay có `CRS_DEP_TIME` đúng `00:00:00` là **$0$ chuyến** (100% các chuyến bay trong khung giờ 00 đều có phút $> 0$, ví dụ 00:05, 00:15).
2. **Hạ cánh lúc đúng nửa đêm (`00:00:00`):**
   - Xuất hiện một số lượng nhỏ các bản ghi có `CRS_ARR_TIME` đúng `00:00:00` (15 ca năm 2016, 89 ca năm 2018, 93 ca năm 2019, 21 ca năm 2020, 7 ca năm 2021, 4 ca năm 2022, 1 ca năm 2023).
   - Tất cả các trường hợp này đều được gán chuỗi `YYYY-MM-DD 00:00:00` với ngày bằng `FL_DATE`.
3. **Kết luận về ngữ nghĩa 2400:**
   - Trong dữ liệu thô không tồn tại chuỗi `24:00:00`. Upstream ETL đã chuyển đổi hoặc không lưu mốc 2400.
   - Trạng thái kỹ thuật: **`2400_SEMANTICS_NOT_PROVEN`** (Không thể khôi phục được sự phân biệt giữa 2400 và 0000 từ chuỗi timestamp dẫn xuất).

---

## 5. Kết luận & Cảnh báo An toàn Thời gian (Temporal Safety Directives)

1. **Tuyệt đối cấm trừ chuỗi timestamp trực tiếp:**
   - Việc tính toán `CRS_ARR_TIME - CRS_DEP_TIME` hoặc `ARR_TIME - DEP_TIME` bằng các hàm chênh lệch timestamp tiêu chuẩn (như `datediff`, `unix_timestamp`, hoặc phép trừ SQL) sẽ dẫn đến kết quả sai lệch nghiêm trọng:
     - Cho ra giá trị âm (ví dụ $-22$ giờ cho chuyến bay đêm).
     - Cho ra độ trễ âm hàng trăm phút khi chuyến bay trễ lăn qua ngày hôm sau.
2. **Sử dụng các trường thời lượng số chính thức:**
   - Toàn bộ các phép đo độ trễ và thời lượng bay **BẮT BUỘC PHẢI DÙNG CÁC TRƯỜNG SỐ CỐT LÕI**: `ARR_DELAY`, `DEP_DELAY`, `ACTUAL_ELAPSED_TIME`, `CRS_ELAPSED_TIME`, `AIR_TIME`, `TAXI_OUT`, `TAXI_IN`.
   - Các trường này đã được kiểm chứng số học khớp 100% trong T-003.
3. **Phân loại trường an toàn:**
   - Bàn giao kết quả kiểm toán làm đầu vào cho ma trận phân loại an toàn trong [`T004_SAFE_FIELDS_DECISION.md`](T004_SAFE_FIELDS_DECISION.md).
