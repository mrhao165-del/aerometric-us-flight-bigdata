# T-006-R1 RECONCILIATION REPORT 1: CANONICAL RAW SCHEMA SPECIFICATION

**Task ID:** `T-006-R1`  
**Gate:** `G3`  
**Document Nature:** Authoritative Canonical Schema Reconciliation & Architectural Fix (`DESIGN_ONLY`)  
**Project:** US Flight Performance Analysis (2016–2024) using Apache Spark / PySpark  
**Status:** `PROPOSED_FOR_PROJECT_LEAD_REVIEW`  
**Date:** 2026-10-17  
**Supersedes:** `docs/05-evidence/T006_SCHEMA_QUALITY_AND_LINEAGE_DESIGN.md` (Mục 2 & Bảng ánh xạ 34 cột)

---

## 1. Bối cảnh & Mục tiêu Đính chính (Context & Objectives)

Trong chu kỳ soát xét thiết kế Gate G3 đợt 1 (`T-006`), hồ sơ thiết kế `T006_SCHEMA_QUALITY_AND_LINEAGE_DESIGN.md` đã xuất hiện **sai lệch cấu trúc nghiêm trọng**:
1. Tự ý đưa vào **9 trường BTS không tồn tại** trong tập dữ liệu CSV thực tế 34 cột (`CANCELLED`, `DIVERTED`, `CANCELLATION_CODE`, `DISTANCE`, `CARRIER_DELAY`, `WEATHER_DELAY`, `NAS_DELAY`, `SECURITY_DELAY`, `LATE_AIRCRAFT_DELAY`).
2. Đồng thời **bỏ sót 9 trường chuẩn tắc thực tế** có mặt trong cả 9 năm audit (`MONTH`, `DAY_OF_MONTH`, `DAY_OF_WEEK`, `ORIGIN_INDEX`, `DEST_INDEX`, `O_LATITUDE`, `O_LONGITUDE`, `D_LATITUDE`, `D_LONGITUDE`).
3. Dẫn tới các thiết kế lọc hạ tầng sai lầm (ví dụ: lọc `CANCELLED = 0.0 AND DIVERTED = 0.0` trong khi hai cột này không hề tồn tại trong raw CSV).

Hồ sơ này khôi phục và chuẩn hóa bảng ánh xạ schema nguồn PySpark dựa trên **hai nguồn căn cứ pháp lý duy nhất**:
- [`docs/02-design/DATA_DICTIONARY.md`](../02-design/DATA_DICTIONARY.md) (Phiên bản chuẩn docs-v1.1).
- 9 tệp siêu dữ liệu kiểm toán gốc: `docs/05-evidence/inputs/schema_2016.json` đến `schema_2024.json`.

---

## 2. Bảng Đối chiếu Sai lệch Schema (Schema Deviation & Errata Matrix)

### 2.1. Danh sách 9 Trường Bị Loại bỏ (Fabricated Fields Removed)

Các trường sau **hoàn toàn không có trong 34 cột thô** của 9 năm CSV (2016–2024) và bị loại bỏ triệt để khỏi thiết kế nạp dữ liệu:

| STT | Trường Tự ý Đưa vào (Sai lệch T-006) | Nguồn gốc Sai sót | Tác hại Kỹ thuật nếu Triển khai | Biện pháp Khắc phục Chuẩn tắc |
| :---: | :--- | :--- | :--- | :--- |
| 1 | `CANCELLED` | Thói quen BTS chuẩn | Spark ném lỗi `AnalysisException: Column 'CANCELLED' does not exist` | Loại bỏ khỏi raw schema; tuân thủ `FP-DEC-006` (`KPI-11 = NOT_COMPUTABLE`) |
| 2 | `DIVERTED` | Thói quen BTS chuẩn | Spark ném lỗi thiếu cột khi dựng `StructType` CSV reader | Loại bỏ khỏi raw schema; không lọc diverted trong CORE |
| 3 | `CANCELLATION_CODE` | Thói quen BTS chuẩn | Đọc nhầm dữ liệu sang null hoặc gây lệch vị trí cột | Loại bỏ khỏi raw schema |
| 4 | `DISTANCE` | Thói quen BTS chuẩn | Gây lỗi tính toán phân loại khoảng cách đường bay | Loại bỏ khỏi raw schema; các đường bay dùng mã `ORIGIN-DEST` |
| 5 | `CARRIER_DELAY` | Báo cáo delay BTS | Gây hiểu nhầm phân rã trễ đã có sẵn trong raw | Loại bỏ khỏi raw schema; ngoài phạm vi CORE |
| 6 | `WEATHER_DELAY` | Báo cáo delay BTS | Nhầm lẫn với 6 cột đo thời tiết liên kết | Loại bỏ khỏi raw schema; ngoài phạm vi CORE |
| 7 | `NAS_DELAY` | Báo cáo delay BTS | Gây hiểu nhầm có phân tích hệ thống kiểm soát bay | Loại bỏ khỏi raw schema; ngoài phạm vi CORE |
| 8 | `SECURITY_DELAY` | Báo cáo delay BTS | Không tồn tại trong dữ liệu thực tế | Loại bỏ khỏi raw schema; ngoài phạm vi CORE |
| 9 | `LATE_AIRCRAFT_DELAY`| Báo cáo delay BTS | Không tồn tại trong dữ liệu thực tế | Loại bỏ khỏi raw schema; ngoài phạm vi CORE |

### 2.2. Danh sách 9 Trường Chuẩn tắc Được Khôi phục (Canonical Fields Restored)

9 trường sau hiện diện thực tế trong 100% 9 tệp audit `schema_YYYY.json` và `DATA_DICTIONARY.md`:

| STT | Tên cột Chuẩn tắc | Thứ tự Thực tế (Index) | Kiểu Thô Audit (`observed_dtypes`) | Kiểu PySpark Thiết kế | Nhóm Nghiệp vụ & Ý nghĩa |
| :---: | :--- | :---: | :---: | :---: | :--- |
| 1 | `MONTH` | 20 | `integer` | `IntegerType` | Tháng phục vụ chuyến bay (1..12); đối chiếu chéo với `FL_DATE`. |
| 2 | `DAY_OF_MONTH` | 21 | `integer` | `IntegerType` | Ngày trong tháng (1..31); đối chiếu chéo với `FL_DATE`. |
| 3 | `DAY_OF_WEEK` | 22 | `integer` | `IntegerType` | Thứ trong tuần (1..7); đối chiếu hệ thống đánh số tại G4. |
| 4 | `ORIGIN_INDEX` | 23 | `integer` | `IntegerType` | Chỉ số định danh số của sân bay khởi hành (`cardinality: 308` năm 2016). |
| 5 | `DEST_INDEX` | 24 | `integer` | `IntegerType` | Chỉ số định danh số của sân bay điểm đến (`cardinality: 308` năm 2016). |
| 6 | `O_LATITUDE` | 31 | `float` | `DoubleType` | Vĩ độ địa lý sân bay đi (tọa độ WGS84). |
| 7 | `O_LONGITUDE` | 32 | `float` | `DoubleType` | Kinh độ địa lý sân bay đi (tọa độ WGS84). |
| 8 | `D_LATITUDE` | 33 | `float` | `DoubleType` | Vĩ độ địa lý sân bay đến (tọa độ WGS84). |
| 9 | `D_LONGITUDE` | 34 | `float` | `DoubleType` | Kinh độ địa lý sân bay đến (tọa độ WGS84). |

---

## 3. Bảng Ánh xạ Toàn diện 34 Cột Chuẩn tắc Sang PySpark (Canonical 34-Column Spec)

Dưới đây là bảng ánh xạ chuẩn tắc, bất biến, khớp 100% về tên, thứ tự và kiểu dữ liệu với 9 tệp `schema_YYYY.json`:

| Index | Tên Cột Chuẩn tắc | Observed Dtype | PySpark Raw Type | Target Curated Type | Null Policy | Quy tắc Ép kiểu & Kiểm tra Cú pháp (Parsing & Cast Policy) | Downstream KPI / Nhánh áp dụng | Ghi chú Ràng buộc Nghiệp vụ |
| :---: | :--- | :---: | :---: | :---: | :---: | :--- | :---: | :--- |
| 1 | `FL_DATE` | string | `StringType` | `DateType` | `NOT_NULL` | Parse chuỗi; hỗ trợ định dạng `yyyy-MM-dd` và timestamp-like `"yyyy-MM-dd 00:00:00"`; nếu parse thất bại $\implies$ `REJECTED` | KPI-01..08 | Khóa lịch duy nhất được kiểm toán; bảo lưu chuỗi thô nếu parse lỗi. |
| 2 | `OP_CARRIER` | string | `StringType` | `StringType` | `NOT_NULL` | Chuỗi mã IATA hãng (2 ký tự); nếu null/rỗng $\implies$ `REJECTED` | KPI-01..06 | Chiều phân tích Hãng hàng không (Carrier dimension). |
| 3 | `OP_CARRIER_FL_NUM` | float | `DoubleType` | `IntegerType` | `NOT_NULL` | Đọc dạng số (do audit ghi nhận `float`), ép kiểu số nguyên dương; nếu null/âm/0 $\implies$ `QUARANTINED` | KPI-01..08 | Số hiệu chuyến bay; không dùng làm single business key. |
| 4 | `ORIGIN` | string | `StringType` | `StringType` | `NOT_NULL` | Chuỗi 3 ký tự mã sân bay đi; nếu null $\implies$ `REJECTED` | KPI-01..07 | Chiều phân tích Sân bay Khởi hành (Origin dimension). |
| 5 | `DEST` | string | `StringType` | `StringType` | `NOT_NULL` | Chuỗi 3 ký tự mã sân bay đến; nếu null $\implies$ `REJECTED` | KPI-01..07 | Chiều phân tích Sân bay Đến (Destination dimension). |
| 6 | `CRS_DEP_TIME` | string | `StringType` | `StringType` | `NOT_NULL` | Chuỗi giờ dự kiến (hỗ trợ `HHmm` hoặc `"yyyy-MM-dd HH:mm:ss"`); cấm parse timestamp tuyệt đối | KPI-01..08 | Giờ khởi hành kế hoạch; tuân thủ an toàn thời gian `FP-DEC-007`. |
| 7 | `DEP_TIME` | string | `StringType` | `StringType` | `NULLABLE` | Chuỗi giờ khởi hành thực tế; giữ nguyên biểu diễn chuỗi, hỗ trợ mốc `2400` | KPI-04, 05 | Cấm tự động trừ timestamp; cấm cộng 24h (`FP-DEC-007`). |
| 8 | `DEP_DELAY` | float | `DoubleType` | `DoubleType` | `NULLABLE` | Số thực biểu diễn phút trễ khởi hành (signed); giữ giá trị âm cho đi sớm | KPI-04, 05 | **`G2-EXC-001`**: Đơn vị mang nhãn `PROVISIONAL`, chặn G6 nếu `TS-018` FAIL ở G5. |
| 9 | `TAXI_OUT` | float | `DoubleType` | `DoubleType` | `NULLABLE` | Số thực thời gian lăn ra; giá trị `< 0` $\implies$ `QUARANTINED` | KPI-07 (Sub 7a) | **`G2-EXC-001`**: Đơn vị mang nhãn `PROVISIONAL`. Mẫu số tính độc lập với KPI khác. |
| 10 | `WHEELS_OFF` | string | `StringType` | `StringType` | `NULLABLE` | Chuỗi thời điểm cất cánh; giữ nguyên biểu diễn gốc | Audit / Lineage | Lưu ý cross-midnight và múi giờ. |
| 11 | `WHEELS_ON` | string | `StringType` | `StringType` | `NULLABLE` | Chuỗi thời điểm chạm đất; giữ nguyên biểu diễn gốc | Audit / Lineage | Lưu ý cross-midnight và múi giờ. |
| 12 | `TAXI_IN` | float | `DoubleType` | `DoubleType` | `NULLABLE` | Số thực thời gian lăn vào; giá trị `< 0` $\implies$ `QUARANTINED` | KPI-07 (Sub 7b) | **`G2-EXC-001`**: Đơn vị mang nhãn `PROVISIONAL`. Mẫu số tính độc lập với TAXI_OUT. |
| 13 | `CRS_ARR_TIME` | string | `StringType` | `StringType` | `NOT_NULL` | Chuỗi giờ đến dự kiến theo lịch | KPI-01..08 | **Date component không chứng minh ngày đến thực** (`DATA_DICTIONARY.md`). |
| 14 | `ARR_TIME` | string | `StringType` | `StringType` | `NULLABLE` | Chuỗi giờ đến thực tế; giữ nguyên mốc `2400` | KPI-02, 03, 06 | Overnight flights có `ARR_TIME < DEP_TIME` cấm tự cộng 24h. |
| 15 | `ARR_DELAY` | float | `DoubleType` | `DoubleType` | `NULLABLE` | Số thực phút trễ đến (signed); giữ giá trị âm cho đến sớm | KPI-02, 03, 06 | **`G2-EXC-001`**: Đơn vị mang nhãn `PROVISIONAL`. Ngưỡng trễ `>= 15.0` (`FP-DEC-008`). |
| 16 | `CRS_ELAPSED_TIME` | float | `DoubleType` | `DoubleType` | `NULLABLE` | Thời lượng hành trình dự kiến; `<= 0` $\implies$ `QUARANTINED` | KPI-08 (Sub 8c) | **`G2-EXC-001`**: Đơn vị mang nhãn `PROVISIONAL`. |
| 17 | `ACTUAL_ELAPSED_TIME`| float | `DoubleType` | `DoubleType` | `NULLABLE` | Thời lượng hành trình thực tế; `<= 0` $\implies$ `QUARANTINED` | KPI-08 (Sub 8b) | **`G2-EXC-001`**: Đơn vị mang nhãn `PROVISIONAL`. |
| 18 | `AIR_TIME` | float | `DoubleType` | `DoubleType` | `NULLABLE` | Thời gian thực bay trên không; `<= 0` $\implies$ `QUARANTINED` | KPI-08 (Sub 8a) | **`G2-EXC-001`**: Đơn vị mang nhãn `PROVISIONAL`. Mẫu số tính độc lập. |
| 19 | `FLIGHTS` | float | `DoubleType` | `DoubleType` | `NOT_NULL` | Chỉ số chuyến bay dạng float (`1.0` trong 100% audit); không dùng làm trọng số | Mẫu số (`FP-DEC-010`) | Mẫu số accepted là `count_records`, tuyệt đối không dùng `sum(FLIGHTS)`. |
| 20 | `MONTH` | integer | `IntegerType` | `IntegerType` | `NOT_NULL` | Giá trị tháng (1..12); đối chiếu chéo với `month(FL_DATE)` | KPI-01..08 Grouping | **Cột vật lý thực tế trong raw**, không phải cột chỉ sinh sau nạp. |
| 21 | `DAY_OF_MONTH` | integer | `IntegerType` | `IntegerType` | `NOT_NULL` | Giá trị ngày trong tháng (1..31); đối chiếu với `dayofmonth(FL_DATE)` | Lịch & Temporal | Kiểm tra tính nhất quán lịch với `FL_DATE`. |
| 22 | `DAY_OF_WEEK` | integer | `IntegerType` | `IntegerType` | `NOT_NULL` | Thứ trong tuần (1..7); kiểm tra hệ thống đánh số | Lịch & Temporal | Hệ quy chiếu (Chủ nhật=1 hay Thứ hai=1) sẽ xác minh tại G4. |
| 23 | `ORIGIN_INDEX` | integer | `IntegerType` | `IntegerType` | `NULLABLE` | Chỉ số định danh số của sân bay đi | Phân loại / Grouping | Cardinality 308 (năm 2016); không xem là biến liên tục. |
| 24 | `DEST_INDEX` | integer | `IntegerType` | `IntegerType` | `NULLABLE` | Chỉ số định danh số của sân bay đến | Phân loại / Grouping | Cardinality 308 (năm 2016); không xem là biến liên tục. |
| 25 | `O_TEMP` | float | `DoubleType` | `DoubleType` | `NULLABLE` | Nhiệt độ tại sân bay đi; giữ nguyên giá trị thô | Weather Ingest | **Loại khỏi CORE theo `FP-DEC-017`**; thiếu giá trị KHÔNG làm reject CORE. |
| 26 | `O_PRCP` | float | `DoubleType` | `DoubleType` | `NULLABLE` | Lượng mưa tại sân bay đi; giữ nguyên giá trị thô | Weather Ingest | **Loại khỏi CORE theo `FP-DEC-017`**; thiếu giá trị KHÔNG làm reject CORE. |
| 27 | `O_WSPD` | float | `DoubleType` | `DoubleType` | `NULLABLE` | Tốc độ gió tại sân bay đi; giữ nguyên giá trị thô | Weather Ingest | **Loại khỏi CORE theo `FP-DEC-017`**; thiếu giá trị KHÔNG làm reject CORE. |
| 28 | `D_TEMP` | float | `DoubleType` | `DoubleType` | `NULLABLE` | Nhiệt độ tại sân bay đến; giữ nguyên giá trị thô | Weather Ingest | **Loại khỏi CORE theo `FP-DEC-017`**; thiếu giá trị KHÔNG làm reject CORE. |
| 29 | `D_PRCP` | float | `DoubleType` | `DoubleType` | `NULLABLE` | Lượng mưa tại sân bay đến; giữ nguyên giá trị thô | Weather Ingest | **Loại khỏi CORE theo `FP-DEC-017`**; thiếu giá trị KHÔNG làm reject CORE. |
| 30 | `D_WSPD` | float | `DoubleType` | `DoubleType` | `NULLABLE` | Tốc độ gió tại sân bay đến; giữ nguyên giá trị thô | Weather Ingest | **Loại khỏi CORE theo `FP-DEC-017`**; thiếu giá trị KHÔNG làm reject CORE. |
| 31 | `O_LATITUDE` | float | `DoubleType` | `DoubleType` | `NULLABLE` | Tọa độ vĩ độ sân bay đi; giá trị ngoài `[-90, 90]` $\implies$ `QUARANTINED` | Không gian / Route | Dữ liệu tọa độ không gian hỗ trợ trực quan hóa đường bay. |
| 32 | `O_LONGITUDE` | float | `DoubleType` | `DoubleType` | `NULLABLE` | Tọa độ kinh độ sân bay đi; giá trị ngoài `[-180, 180]` $\implies$ `QUARANTINED`| Không gian / Route | Dữ liệu tọa độ không gian hỗ trợ trực quan hóa đường bay. |
| 33 | `D_LATITUDE` | float | `DoubleType` | `DoubleType` | `NULLABLE` | Tọa độ vĩ độ sân bay đến; giá trị ngoài `[-90, 90]` $\implies$ `QUARANTINED` | Không gian / Route | Dữ liệu tọa độ không gian hỗ trợ trực quan hóa đường bay. |
| 34 | `D_LONGITUDE` | float | `DoubleType` | `DoubleType` | `NULLABLE` | Tọa độ kinh độ sân bay đến; giá trị ngoài `[-180, 180]` $\implies$ `QUARANTINED`| Không gian / Route | Dữ liệu tọa độ không gian hỗ trợ trực quan hóa đường bay. |

---

## 4. Xử lý Các Trường Dẫn xuất vs. Trường Vật lý (Derived vs. Physical Fields)

1. **`YEAR` và `QUARTER` là các trường DẪN XUẤT (`DERIVED`), không phải trường vật lý thô:**
   - Trong CSV thô không có cột mang tên `YEAR` hay `QUARTER`.
   - `YEAR` được trích xuất từ `year(to_date(FL_DATE, ...))` trong quá trình Ingestion và dùng làm Partition Column cho tầng Curated Parquet.
   - `QUARTER` được trích xuất từ `quarter(...)` phục vụ tổng hợp phân tích theo quý.
2. **`MONTH` là TRƯỜNG VẬT LÝ THỰC TẾ (`PHYSICAL RAW COLUMN`):**
   - Cột `MONTH` nằm ở vị trí số 20 trong tệp CSV gốc (kiểu `Int64 nullable`).
   - Trong quá trình nạp dữ liệu tại Gate G4/T-007, pipeline bắt buộc phải đối chiếu chéo:
     $$\mathbf{MONTH}_{\text{physical}} == \text{month}(\mathbf{FL\_DATE})$$
     Nếu có sự bất đồng (ví dụ: `FL_DATE` thuộc tháng 6 nhưng `MONTH == 7`), bản ghi sẽ được chuyển vào diện `QUARANTINED` với mã lỗi `CALENDAR_MONTH_DISCREPANCY`.

---

## 5. Xử lý Định dạng Chuỗi Thời gian Đã Được Kiểm toán (Audited Temporal String Handling)

Theo bằng chứng kiểm toán tại `T004_2024_DATE_COVERAGE_AUDIT.md` và `schema_2016.json`:
- Các tệp CSV từ 2016 đến 2023 có chứa biểu diễn chuỗi thời gian dạng:
  - `FL_DATE`: `"2016-06-01 00:00:00"` (chứa đuôi timestamp `00:00:00`).
  - `CRS_DEP_TIME`: `"2016-06-01 22:25:00"` (chứa cả thành phần ngày và giây).
- **Quy tắc Thiết kế Ingestion Parser:**
  - Parser không được giả định ngây thơ rằng chuỗi `FL_DATE` luôn là `yyyy-MM-dd` có đúng 10 ký tự.
  - Sử dụng biểu thức parse linh hoạt (hoặc regex trích xuất `^\d{4}-\d{2}-\d{2}`) để lấy đúng phần ngày `yyyy-MM-dd`.
  - Nếu bản ghi có cấu trúc chuỗi đọc được và chuyển đổi thành công sang ngày hợp lệ $\implies$ bản ghi được `ACCEPTED`. Tuyệt đối không phân loại nhầm thành lỗi parse CSV cấp thấp (`REJECTED`) chỉ vì chuỗi có kèm đuôi `00:00:00`.
  - Trong trường hợp trích xuất thất bại hoàn toàn (chuỗi hỏng cú pháp), giá trị chuỗi gốc phải được bảo tồn trong cột `raw_error_payload` để phục vụ đối soát.

---

## 6. Kết luận & Chốt chặn Tuân thủ (Compliance Sign-off)

- **Số lượng cột:** Đúng **34 cột duy nhất**.
- **Tên cột:** Khớp 100% với `DATA_DICTIONARY.md` và 9 tệp `schema_YYYY.json`.
- **Thứ tự cột:** Giữ đúng thứ tự vật lý từ 1 đến 34.
- **Loại trừ trường giả định:** 9 trường giả định (`CANCELLED`, `DIVERTED`, `CANCELLATION_CODE`, `DISTANCE`, 5 cột BTS delay) đã bị xóa bỏ hoàn toàn.
- **Ràng buộc Thời tiết:** 6 cột thời tiết được bảo tồn trong raw ingest và loại bỏ khỏi 8 CORE KPIs theo đúng `FP-DEC-017`.
