# T-008 — ENTRY HANDOFF SPECIFICATION (READ-ONLY ARCHITECTURE INTERFACE)

**Project:** US Flight Performance Analysis 2016–2024  
**Upstream Task:** `T-007` — Raw CSV Ingestion Pipeline (`PASS / COMPLETED (CONTROLLED)`)  
**Target Task:** `T-008` — Data Quality, Disjoint Row Accounting & Quarantine Engine  
**Gate:** `G4` (`PLANNED / NOT_COMPLETED`)  
**Document ID:** `T008-ENTRY-HANDOFF-SPEC-01`  
**Date:** 2026-10-18  
**Mode:** `READ-ONLY SPECIFICATION — NO QUALITY ENGINE IMPLEMENTATION AUTHORIZED`  
**Status:** `READY_FOR_PROJECT_LEAD_T008_AUTHORIZATION`

---

## 1. Giới thiệu và Ranh giới Thực thi

Tài liệu này xác định giao diện kiến trúc đầu vào và các ràng buộc pháp lý kỹ thuật dành riêng cho việc chuyển giao từ Nhiệm vụ `T-007` (Raw Ingestion) sang Nhiệm vụ `T-008` (Quality Engine).

> [!CAUTION]
> **Ranh giới Thực thi Nghiêm ngặt:**  
> 1. Tài liệu này là **đặc tả chỉ đọc (read-only specification)**.  
> 2. Tuyệt đối **KHÔNG** bắt đầu triển khai mã nguồn cho `T-008` (Quality Engine).  
> 3. Tuyệt đối **KHÔNG** chạy bất kỳ tác vụ Spark nào trên dữ liệu CSV thật (54.7M dòng) trong giai đoạn này.  
> 4. Trạng thái của Task `T-008` tiếp tục giữ nguyên là **`NOT_STARTED`** cho đến khi có chỉ thị bằng văn bản riêng từ Project Lead.

---

## 2. Đầu vào và Đầu ra Kỹ thuật từ T-007

### 2.1. Đầu vào Nhận từ T-007
Nhiệm vụ `T-008` sẽ tiêu thụ các cấu trúc dữ liệu và thành phần mã nguồn đã được nghiệm thu tại `T-007`:

1. **DataFrame Đã Chuẩn hóa Schema (`RawIngestedDataFrame`):**
   - Do `RawCsvReader.read_raw()` hoặc `IngestionCoordinator.ingest_year()` cung cấp.
   - Tuân thủ chính xác 34 cột theo `CuratedSchema` ([`src/flight_pipeline/ingestion/schema.py`](../../src/flight_pipeline/ingestion/schema.py)).
   - Toàn bộ 34 cột đều có kiểu Arrow/Spark tương thích, `nullable=True`, bảo toàn tên cột chuẩn và thứ tự vật lý.
2. **Cột Định danh Dòng Xác định (`_record_lineage_id`):**
   - Được gắn tự động bởi hàm `attach_deterministic_lineage()`.
   - Cung cấp định danh duy nhất dựa trên băm nội dung và thứ tự xuất hiện, cho phép truy vết mọi bản ghi xuyên suốt qua các tầng phân loại và cách ly.
3. **Kết quả Quét Dòng Logic Độc lập (`CsvScanResult`):**
   - Cung cấp `physical_data_lines`, `logical_data_records`, `embedded_newline_count`, và cờ `is_verifiable` từ `scan_csv_logical_records()`.
   - Đảm bảo mẫu số dòng thô độc lập ($N_{raw}$) để đối soát hạch toán `DC-11`.
4. **Hạ tầng Khóa Đơn ghi và Phục hồi Hậu-pointer:**
   - Sử dụng `SingleWriterLock` ([`src/flight_pipeline/storage/locking.py`](../../src/flight_pipeline/storage/locking.py)) để ngăn chặn xung đột ghi đồng thời.
   - Tái sử dụng cơ chế ghi Parquet hai pha (`_task_attempts` $\to$ `final`) và đối soát thư mục xuất bản.

### 2.2. Đầu ra Kỳ vọng của T-008
Nhiệm vụ `T-008` có trách nhiệm sản sinh các thành phần sau mà không làm thay đổi các bất biến của `T-007`:

1. **Ba Phân vùng Dữ liệu Tách biệt Tuyệt đối (`Disjoint Partitions`):**
   - `accepted`: Các bản ghi chuyến bay hợp lệ phục vụ tính toán KPI ở Gate G5/G6.
   - `quarantined`: Các bản ghi đọc được nhưng vi phạm ràng buộc miền giá trị hợp lệ của chuyến bay cần giữ lại để kiểm toán.
   - `rejected`: Các dòng hỏng cấu trúc không thể nạp thành bản ghi chuyến bay hợp quy.
2. **Báo cáo Hạch toán Dòng `RowAccounting` (`DC-11`):**
   - Xác nhận $N_{raw} = N_{accepted} + N_{quarantined} + N_{rejected}$ mà không có sự chênh lệch (unbalanced).
3. **Báo cáo Mẫu số Hợp đồng `MetricAccounting` (`DC-12`):**
   - Hạch toán tách biệt giữa tính hợp lệ của bản ghi chuyến bay (`count_records`) và tính hợp lệ của từng phép đo (`count_metric_valid`).
4. **Thư mục Lưu trữ Forensic Cách ly:**
   - Dữ liệu `quarantined` được lưu trữ an toàn tại `data/quarantine/<run_id>/` kèm metadata mô tả nguyên nhân vi phạm.

---

## 3. Các Quy tắc Cách ly và Trạng thái Tạm thời (`G3-COND-A`)

### 3.1. Vấn đề `OP_CARRIER_FL_NUM <= 0`
- **Hiện trạng:** Trong thiết kế kiến trúc Gate G3, việc số hiệu chuyến bay `<= 0` được đề xuất sơ bộ đưa vào diện cách ly toàn bộ bản ghi (`whole-record quarantine`).
- **Ràng buộc `G3-COND-A`:** Quyết định này chỉ là **đề xuất sơ bộ**. Không được tự động biến mọi dòng có `OP_CARRIER_FL_NUM <= 0` thành bản ghi cách ly trên dữ liệu thực tế nếu chưa kiểm toán phân bố của chúng.
- **Yêu cầu đối với T-008:** Trong `T-008`, nhóm kỹ sư phải xây dựng công cụ khảo sát phân bố giá trị `OP_CARRIER_FL_NUM` (đặc biệt là giá trị `0` hoặc số âm) để trình Project Lead quyết định xem có đưa vào diện cách ly hay không.

### 3.2. Quy tắc Xử lý Ngày và Định dạng Chuỗi
- **Quy tắc `FP-DEC-007`:**
  - Định dạng chuỗi ngày tháng hợp lệ phải khớp biểu thức chính quy neo chặt: `^(?:\d{4}-\d{2}-\d{2}|\d{4}-\d{2}-\d{2} 00:00:00)$`.
  - Cấm tự động cắt chuỗi hoặc chấp nhận tiền tố lỏng lẻo (`^\d{4}-\d{2}-\d{2}`).
  - Bản ghi có chuỗi ngày không hợp lệ nhưng nạp được cấu trúc sẽ được phân loại vào `quarantined`, không được xếp vào `rejected` (theo bất biến `MUT-10`).

---

## 4. Hợp đồng Dữ liệu DC-11 và DC-12

### 4.1. Hợp đồng DC-11 — Hạch toán Dòng Rời rạc Ba Trạng thái
- Mọi bản ghi dữ liệu thô bắt buộc phải rơi vào đúng **1 trong 3 trạng thái duy nhất**:
  $$\text{accepted} \cap \text{quarantined} = \emptyset, \quad \text{accepted} \cap \text{rejected} = \emptyset, \quad \text{quarantined} \cap \text{rejected} = \emptyset$$
  $$N_{raw} = N_{accepted} + N_{quarantined} + N_{rejected}$$
- Nếu phát hiện số âm, hoặc tổng 3 trạng thái không bằng $N_{raw}$, đường ống phải dừng ngay lập tức ở trạng thái fail-closed (`ACCOUNTING_UNVERIFIED`).

### 4.2. Hợp đồng DC-12 — Phân biệt Record Validity vs. Metric Validity
- **Tính Hợp lệ của Bản ghi (`Record Validity`):**
  - Xác định bản ghi có phải là một chuyến bay có thể phân tích hay không.
  - Phục vụ mẫu số chung: `count_records` (mẫu số cơ sở).
- **Tính Hợp lệ của Phép đo (`Metric Validity`):**
  - Một chuyến bay hợp lệ (`accepted`) có thể có một vài trường đo lường bị thiếu (`null`), NaN hoặc âm ngoài miền cho phép (ví dụ: `TAXI_OUT < 0`).
  - Bản ghi đó **VẪN Ở LẠI TRONG `accepted`** (không bị cách ly cả dòng), nhưng giá trị đo lường đó bị loại khỏi `count_metric_valid` của KPI tương ứng.
  - Nghiêm cấm gộp khái niệm valid rate của một chỉ số với mức độ bao phủ thị trường (coverage rate).

---

## 5. Ma trận Truy vết Kiểm thử (`Test Traceability`)

Nhiệm vụ `T-008` chịu trách nhiệm trực tiếp đáp ứng các chỉ tiêu kỹ thuật trong [`docs/03-quality/TEST_PLAN.md`](../03-quality/TEST_PLAN.md):

| Mã Kiểm thử | Nội dung Kiểm thử Chuẩn tắc | Yêu cầu Kỹ thuật Cụ thể trong T-008 |
| :---: | :--- | :--- |
| **`TS-002`** | Domain Constraints & Source-Year Verification | Kiểm tra giá trị từng trường nằm trong miền cho phép; `YEAR` và thành phần năm trong `FL_DATE` phải trùng với thư mục năm nguồn. |
| **`TS-003`** | Disjoint Three-State Row Accounting Balance | Kiểm chứng thuật toán phân loại rời rạc 3 trạng thái, không thất thoát hoặc nhân đôi dòng ($N_{raw} = N_{acc} + N_{quar} + N_{rej}$). |
| **`TS-004`** | Calendar Date Coverage Early Stage Check | Kiểm tra sớm độ phủ lịch năm 2024 trong stage quality (`335/366` ngày, nhận diện 31 ngày khuyết của Tháng 3/2024 theo `OR-05`). |
| **`TS-017`** | Zero Denominator & Small Cohort Handling | Kiểm chứng xử lý an toàn khi `count_records == 0` hoặc `count_metric_valid == 0`, không gây lỗi chia cho 0 (`ZeroDivisionError`). |

---

## 6. Rủi ro Mở và Ràng buộc Nghiệp vụ Cần Tuân thủ

### 6.1. Khuyết tật Chất lượng Mở `OR-05` (Năm 2024)
- Dữ liệu năm 2024 bị khuyết toàn bộ 31 ngày của Tháng 3/2024 (chỉ có 335/366 ngày). Ngày nhuận `2024-02-29` có `18,642` bản ghi hợp lệ.
- **Ràng buộc:** Trong `T-008`, stage quality phải phát hiện đúng sự vắng mặt này, ghi nhận cờ `source_coverage_status = PARTIAL` theo `DC-12`, tuyệt đối cấm nội suy dữ liệu giả.

### 6.2. Xuất xứ Dữ liệu Thượng nguồn `OR-08` (`IDENTITY_UNVERIFIED`)
- Toàn bộ dữ liệu thô cục bộ tiếp tục giữ nhãn `IDENTITY_UNVERIFIED` / `METADATA_MATCH_ONLY`.
- Mã băm SHA-256 ứng viên tại `T007_LOCAL_RAW_SHA256_CANDIDATE.json` chưa được Project Lead phê duyệt làm golden baseline. Không được tự ý đưa vào kiểm tra hard-fail trong `T-008`.

### 6.3. Ràng buộc Thời tiết `CONDITIONAL_NO_GO` (`FP-DEC-017`)
- 6 cột thời tiết (`O_TEMP`, `O_PRCP`, `O_WSPD`, `D_TEMP`, `D_PRCP`, `D_WSPD`) có mặt trong schema 34 cột nhưng đang ở trạng thái `CONDITIONAL_NO_GO`.
- **CẤM:** Tuyệt đối không được đưa bất kỳ dòng dữ liệu CORE hợp lệ nào vào diện `quarantined` hoặc `rejected` chỉ vì giá trị ở 6 cột thời tiết bị thiếu (`null`), không xác định hoặc không hợp lệ.

---

## 7. Quy tắc Runtime và An toàn Lưu trữ trên Windows NTFS

1. **Cô lập Môi trường Cục bộ:**
   - Sử dụng thư mục tạm Spark cục bộ nằm ngoài workspace kho lưu trữ (`spark.local.dir = D:/Study/Code/Apache/Flight_Analyzt/tmp/spark_local` hoặc thư mục tạm hệ thống hợp chuẩn POSIX/Windows).
2. **Khóa Đơn Ghi (`SingleWriterLock`):**
   - Mọi tiến trình chạy phân loại và xuất bản trong `T-008` phải tạo lock tệp `_lock.json` trước khi ghi, và giải phóng an toàn sau khi kết thúc.
3. **Không Thay đổi Dữ liệu Thô:**
   - Thư mục `data/raw/` là bất biến tuyệt đối (`read-only`). Cấm mọi thao tác ghi, xóa hoặc đổi tên trong `data/raw/`.

---

## 8. Các Hạng mục Cần Project Lead Quyết định Trước Khi Triển khai T-008

Trước khi bắt đầu viết mã nguồn sản xuất cho `T-008`, nhóm kỹ sư đề nghị Project Lead đưa ra quyết định đối với các mục sau:

1. **Quyết định về Chính sách Cách ly `OP_CARRIER_FL_NUM <= 0` (`G3-COND-A`):**
   - Xác nhận có áp dụng cách ly toàn bản ghi đối với chuyến bay có số hiệu `<= 0` hay chỉ gắn cờ cảnh báo chất lượng.
2. **Phê duyệt Golden Baseline SHA-256 (`OR-08` / `T007-02B`):**
   - Quyết định có chính thức thăng cấp tập mã băm trong `T007_LOCAL_RAW_SHA256_CANDIDATE.json` thành golden baseline chính thức trong `SOURCE_MANIFEST.json` hay tiếp tục hoãn sang Gate G5.
3. **Phê chuẩn Lệnh Khởi động `T-008`:**
   - Ban hành prompt ủy quyền triển khai kỹ thuật Nhiệm vụ `T-008`.

---

## 9. Kết luận Handoff

Tầng nạp dữ liệu `T-007` đã được hoàn thành và nghiệm thu ở trạng thái vững chắc nhất, sẵn sàng 100% làm nền tảng cho `T-008`. Mọi hoạt động tiếp theo phải tuân thủ nghiêm ngặt đặc tả này.
