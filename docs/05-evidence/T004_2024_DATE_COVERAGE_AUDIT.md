# T-004: BÁO CÁO KIỂM TOÁN ĐỘ BAO PHỦ LỊCH NĂM NHUẬN 2024 (2024 DATE COVERAGE & CALENDAR CONTINUITY AUDIT)

- **Mã nhiệm vụ:** `T-004` (Sub-task 2: 2024 Calendar Coverage & Leap Year Verification)
- **Gate kiểm soát:** `G2` (Data Quality, Cohort & Metric Contracts)
- **Ngày thực hiện:** 2026-10-14
- **Vai trò:** Senior Data Engineer, Big Data Quality Auditor & Technical Reviewer
- **Trạng thái:** **`AUDIT_COMPLETE / CRITICAL_DEFECT_DISCOVERED`**
- **Văn bản tuân thủ:** [`AGENTS.md`](../../AGENTS.md), [`docs/01-planning/BACKLOG.md`](../01-planning/BACKLOG.md), [`docs/02-design/DATA_CONTRACT.md`](../02-design/DATA_CONTRACT.md), [`docs/03-quality/TEST_PLAN.md`](../03-quality/TEST_PLAN.md) (`TS-004`), [`docs/05-evidence/inputs/schema_2024.json`](inputs/schema_2024.json).

---

## 1. Mục tiêu & Phương pháp Kiểm toán

Trong các giai đoạn trước (T-001 đến T-003), rủi ro **`OR-05`** được bảo lưu ở trạng thái:
> *"Tính liên tục 366 ngày của năm nhuận 2024 chưa đếm distinct dates (UNKNOWN / PENDING_DAILY_COUNT); cấm tự ý quét full CSV tại T-003."*

Khi bước vào nhiệm vụ **T-004**, việc kiểm toán trực tiếp trên tệp `data/raw/tabular/2024/flight_with_weather_2024.csv` được kích hoạt theo đúng phạm vi kỹ thuật nhằm giải quyết dứt điểm:
1. Xác định số ngày lịch phân biệt (*distinct calendar service dates*) trong năm 2024.
2. Kiểm tra tính liên tục của các tháng trong năm (1 đến 12).
3. Kiểm chứng sự tồn tại của ngày nhuận **`2024-02-29`** và khối lượng dữ liệu tương ứng.
4. Đánh giá tác động đến việc phân tích mô tả chuỗi thời gian, tính toán xu hướng theo quý/tháng, và nghiệm thu tiêu chí `TS-004`.

Phương pháp thực thi: Sử dụng script Python đọc luồng có giới hạn bộ nhớ (*bounded streaming reader*), quét tuần tự $6,284,841$ dòng dữ liệu vật lý của năm 2024 mà không nạp toàn bộ tệp vào RAM.

---

## 2. Phát hiện Chấn động: Sự Vắng mặt Hoàn toàn của Tháng 3/2024 (Month 3 Missing Defect)

> [!WARNING]
> **PHÁT HIỆN KIỂM TOÁN QUAN TRỌNG NHẤT VỀ ĐỘ BAO PHỦ DỮ LIỆU NĂM 2024:**
> Trong tệp dữ liệu thô `flight_with_weather_2024.csv`, **THÁNG 3 NĂM 2024 (`MONTH = 3`, tức toàn bộ tháng 3/2024) HOÀN TOÀN KHÔNG TỒN TẠI TRONG TẬP DỮ LIỆU**.
> Toàn bộ 31 ngày của tháng 3/2024 (từ `2024-03-01` đến `2024-03-31`) có số lượng bản ghi bằng **$0$**.

### Bảng Phân bổ Bản ghi theo Tháng Thực tế trong Năm 2024:
Tổng số dòng vật lý: $6,284,841$ dòng dữ liệu (khớp $100\%$ với `finite_count` trong [`inputs/schema_2024.json`](inputs/schema_2024.json)).

| Tháng (`MONTH`) | Tên tháng | Trạng thái hiện diện | Số lượng bản ghi quan sát thực tế | Tỷ lệ trong năm 2024 | Ghi chú kiểm toán |
|:---:|---|:---:|---:|---:|---|
| **1** | Tháng 1 / 2024 | Có mặt | $517,544$ | $8.23\%$ | Đủ 31 ngày (`2024-01-01` đến `2024-01-31`) |
| **2** | Tháng 2 / 2024 | Có mặt | $507,200$ | $8.07\%$ | Đủ 29 ngày (Năm nhuận, có ngày `2024-02-29`) |
| **3** | **Tháng 3 / 2024** | **HOÀN TOÀN VẮNG MẶT** | **$0$** | **$0.00\%$** | **DATA_ABSENT_IN_CURRENT_CSV (UPSTREAM_ROOT_CAUSE_UNKNOWN)** |
| **4** | Tháng 4 / 2024 | Có mặt | $568,475$ | $9.05\%$ | Đủ 30 ngày (`2024-04-01` đến `2024-04-30`) |
| **5** | Tháng 5 / 2024 | Có mặt | $590,760$ | $9.40\%$ | Đủ 31 ngày (`2024-05-01` đến `2024-05-31`) |
| **6** | Tháng 6 / 2024 | Có mặt | $591,680$ | $9.41\%$ | Đủ 30 ngày (`2024-06-01` đến `2024-06-30`) |
| **7** | Tháng 7 / 2024 | Có mặt | $603,904$ | $9.61\%$ | Đủ 31 ngày (`2024-07-01` đến `2024-07-31`) |
| **8** | Tháng 8 / 2024 | Có mặt | $596,131$ | $9.49\%$ | Đủ 31 ngày (`2024-08-01` đến `2024-08-31`) |
| **9** | Tháng 9 / 2024 | Có mặt | $571,224$ | $9.09\%$ | Đủ 30 ngày (`2024-09-01` đến `2024-09-30`) |
| **10** | Tháng 10 / 2024 | Có mặt | $600,193$ | $9.55\%$ | Đủ 31 ngày (`2024-10-01` đến `2024-10-31`) |
| **11** | Tháng 11 / 2024 | Có mặt | $563,296$ | $8.96\%$ | Đủ 30 ngày (`2024-11-01` đến `2024-11-30`) |
| **12** | Tháng 12 / 2024 | Có mặt | $574,434$ | $9.14\%$ | Đủ 31 ngày (`2024-12-01` đến `2024-12-31`) |
| **Tổng** | **11 tháng hiện diện** | **Thiếu Tháng 3** | **$6,284,841$** | **$100.00\%$** | Khớp chính xác tổng số hàng kiểm toán |

---

## 3. Kiểm chứng Số ngày Lịch Riêng biệt (Distinct Calendar Days)

### 3.1. Ranh giới Khoa học về Chuẩn Lịch vs Dữ liệu Thực tế
- **Chuẩn Lịch Thiên văn Tham chiếu (*Astronomical Calendar Reference*):** Năm 2024 là năm nhuận (*Leap Year*), bắt buộc phải có chuẩn tham chiếu là **$366$ ngày**. Tuyệt đối không thay đổi chuẩn tham chiếu này thành 335 ngày để gượng ép trạng thái PASS.
- **Hiện trạng Dữ liệu Quan sát Thực tế (*Observed Empirical State*):**
  - Số ngày lịch quan sát được: $\mathbf{335\text{ ngày}}$.
  - Số ngày thiếu: $\mathbf{31\text{ ngày}}$ (từ `2024-03-01` đến `2024-03-31`).
  - Trạng thái bao phủ lịch: **`INCOMPLETE_COVERAGE / PARTIAL_YEAR`**.
- Đối chiếu chéo giữa cột `MONTH` và tháng trích xuất từ `FL_DATE`: **100% khớp (0 mismatch)** trên $6,284,841$ dòng. Cả hai trường đều hoàn toàn vắng mặt Tháng 3.

### 3.2. Kiểm chứng Ngày Nhuận 29/02/2024
- Tìm kiếm cụ thể ngày `2024-02-29 00:00:00`: **ĐÃ XÁC MINH HIỆN DIỆN**.
- Số lượng bản ghi quan sát được vào đúng ngày `2024-02-29`:
  $$\mathbf{18,642\text{ chuyến bay}}.$$
- **Ranh giới Bằng chứng Nguồn gốc (F01/F02 Boundary):**
  - Dữ liệu thô thực tế có chứa ngày 29/02/2024 (`DATA_PRESENT_FOR_LEAP_DAY`).
  - Dữ liệu thô thực tế không chứa tháng 3/2024 (`DATA_ABSENT_IN_CURRENT_CSV`).
  - Do đồ án không sở hữu mã nguồn ETL của bên thứ ba, nguyên nhân kỹ thuật gốc của việc khuyết thiếu tháng 3 được phân loại chính xác là **`UPSTREAM_ROOT_CAUSE_UNKNOWN`**. Tuyệt đối không tự ý khẳng định kịch bản upstream cụ thể khi chưa có bằng chứng nguồn trực tiếp.

### 3.3. Đối chiếu Đối chứng với 8 Năm Còn lại (2016–2023)
Kiểm tra đối chứng độc lập trên 8 năm còn lại bằng script quét luồng trực tiếp từng ngày:
- Năm 2016 (Nhuận): Đủ $366$ ngày phân biệt ($0$ ngày thiếu, $5,537,987$ dòng).
- Năm 2017: Đủ $365$ ngày phân biệt ($0$ ngày thiếu, $5,575,872$ dòng).
- Năm 2018: Đủ $365$ ngày phân biệt ($0$ ngày thiếu, $6,986,842$ dòng).
- Năm 2019: Đủ $365$ ngày phân biệt ($0$ ngày thiếu, $7,161,827$ dòng).
- Năm 2020 (Nhuận): Đủ $366$ ngày phân biệt ($0$ ngày thiếu, $4,312,091$ dòng).
- Năm 2021: Đủ $365$ ngày phân biệt ($0$ ngày thiếu, $5,755,666$ dòng).
- Năm 2022: Đủ $365$ ngày phân biệt ($0$ ngày thiếu, $6,413,416$ dòng).
- Năm 2023: Đủ $365$ ngày phân biệt ($0$ ngày thiếu, $6,645,461$ dòng).
- Năm 2024 (Nhuận): **Chỉ có $335$ ngày phân biệt** ($31$ ngày thiếu của Tháng 3, $6,284,841$ dòng).

Hiện tượng khuyết thiếu nguyên tháng **CHỈ XẢY RA DUY NHẤT TẠI NĂM 2024**. Toàn bộ 8 năm (2016–2023) đều có độ bao phủ lịch đạt $100\%$ tính liên tục.

---

## 4. Tác động Phân tích & Đề xuất Phương án Xử lý (Impact & Treatment Protocol)

### 4.1. Tác động Trực tiếp đến Các Chỉ số và Biểu đồ
1. **Chỉ số Sản lượng `KPI-01` (Accepted Record Count):**
   - Sản lượng năm 2024 quan sát được là $6,284,841$ bản ghi, bị thiếu hụt nhân tạo xấp xỉ $\approx 8.3\%$ sản lượng cả năm.
   - Tuyệt đối không so sánh trực tiếp tổng số chuyến bay năm 2024 với các năm đủ khác mà không kèm nhãn cảnh báo.
2. **Tổng hợp Quý 1 (Q1 Aggregations):**
   - Q1/2024 thực tế chỉ gồm Tháng 1 + Tháng 2. Mọi bảng biểu và KPI tính cho Q1/2024 bắt buộc phải gắn nhãn: `Q1_2024_PARTIAL (Missing March)`.
3. **Phân tích Xu hướng Chuỗi Thời gian & Mùa vụ (Seasonal Trends):**
   - Điểm dữ liệu Tháng 3/2024 bắt buộc phải hiển thị khoảng trống (*gap*) hoặc nhãn `N/A`.
   - **CẤM TUYỆT ĐỐI ĐIỀN SỐ 0 HOẶC TỰ Ý NỘI SUY:** Việc điền 0 sẽ làm biến dạng các chỉ số thống kê, trong khi việc tự ý nội suy số chuyến bay vi phạm nguyên tắc bảo toàn dữ liệu nguồn của `AGENTS.md`.

### 4.2. Khuyến nghị Ba Phương án Xử lý Kỹ thuật (2024 Treatment Options)
- **Phương án 1 (Bổ sung Nguồn Dữ liệu Chuẩn — Recommended for Production Expansion):**
  - Trích xuất bổ sung tệp dữ liệu Tháng 3/2024 trực tiếp từ hệ thống BTS TranStats (Title 14 CFR Part 234).
  - Yêu cầu: Kiểm tra nghiêm ngặt tính tương thích schema 34 cột, định dạng chuỗi timestamp và kiểm tra trôi dạt nguồn (*provenance verification*).
- **Phương án 2 (Bảo toàn Hiện trạng & Gắn nhãn Nghiên cứu — Baseline Analytic Policy):**
  - Giữ nguyên bộ dữ liệu thô hiện hành.
  - Phân loại năm 2024 trong toàn bộ báo cáo phân tích là **`PARTIAL_YEAR`** (11 tháng).
  - Mọi đồ thị và bảng số liệu 2024 phải mang chú thích bắt buộc (*mandatory footnote*).
- **Phương án 3 (So sánh Đối chiếu trên Cửa sổ Tháng Chung — Common-Month Windowing):**
  - Khi thực hiện các phân tích so sánh giữa các năm (YoY comparison), chỉ so sánh trên tập hợp 11 tháng chung (`[1, 2, 4, 5, 6, 7, 8, 9, 10, 11, 12]`, loại trừ Tháng 3 trên tất cả các năm) để đảm bảo tính chuẩn hóa thống kê.

### 4.3. Định vị Tiêu chí Kiểm thử `TS-004` (Calendar Continuity Check)
- Giữ nguyên chuẩn tham chiếu của `TS-004` trong [`TEST_PLAN.md`](../03-quality/TEST_PLAN.md):
  - Tiêu chí `TS-004` kiểm tra tính toàn vẹn lịch trình cả năm.
  - Đối với năm 2024: Đánh giá là **`FAIL_FULL_YEAR_COVERAGE / DEFECT_DETECTED`** (với kết quả cụ thể: `observed=335`, `missing=31`, `coverage_status=INCOMPLETE`).
  - Tuyệt đối không thay đổi tiêu chí kiểm thử để che giấu khiếm khuyết dữ liệu.

---

## 5. Cập nhật Rủi ro OR-05 (Open Quality Defect)

- **Phân định rạch ròi:**
  - Sự không chắc chắn về số lượng ngày (*uncertainty about day count*) đã được **GIẢI TỎA BẰNG THỰC CHỨNG KIỂM TOÁN** (xác định chính xác 335 ngày, khuyết thiếu Tháng 3, 29/02 có 18,642 chuyến).
  - Tuy nhiên, **KHIẾM KHUYẾT CHẤT LƯỢNG DỮ LIỆU THỰC TẾ (DATA QUALITY DEFECT) VẪN CÒN TỒN TẠI** do thiếu 31 ngày của Tháng 3.
- Do đó, rủi ro **`OR-05`** **TUYỆT ĐỐI KHÔNG ĐƯỢC ĐÓNG**.
- Cập nhật phân loại trạng thái của **`OR-05`**:
  - Trạng thái kỹ thuật: **`OPEN_QUALITY_DEFECT`** (Khiếm khuyết chất lượng mở: Thiếu Tháng 3/2024, độ bao phủ 335/366 ngày).
  $$\mathbf{OR\text{-}05: OPEN\_QUALITY\_DEFECT\ (Incomplete\ 2024\ Coverage,\ Missing\ March)}$$
- Rủi ro này được bảo lưu chuyển giao cho Gate G6 để áp dụng phương án xử lý đã chọn (Phương án 2 hoặc Phương án 3).

