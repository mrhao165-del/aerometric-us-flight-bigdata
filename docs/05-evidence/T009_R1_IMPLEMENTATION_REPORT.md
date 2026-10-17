# T009-R1: TECHNICAL IMPLEMENTATION & ARCHITECTURAL CONFORMANCE REPORT

**Task ID:** `T-009` (Controlled PySpark Bootstrap, Validator Compatibility & Evidence Verification)  
**Gate:** `G4`  
**Engineer:** Senior Big Data Software Architect & Senior PySpark Engineer  
**Date:** 2026-10-17  
**Status:** `IMPLEMENTATION_COMPLETED`  

---

## 1. Tổng Quan Triển Khai Kỹ Thuật (Implementation Overview)

Nhiệm vụ `T-009` chịu trách nhiệm thiết lập nền tảng hạ tầng kỹ thuật (runtime infrastructure, execution safety, configuration management, automated testing) phục vụ cho toàn bộ các giai đoạn xử lý dữ liệu tiếp theo của dự án phân tích hiệu suất chuyến bay Hoa Kỳ 2016–2024.

Mọi module mã nguồn được phát triển tuân thủ nghiêm ngặt theo các tài liệu thiết kế chuẩn tắc:
- [`ARCHITECTURE.md`](../02-design/ARCHITECTURE.md)
- [`DECISIONS.md`](../02-design/DECISIONS.md) (17 quyết định kiến trúc FP-DEC-001..017)
- [`DATA_CONTRACT.md`](../02-design/DATA_CONTRACT.md) (DC-11, DC-12)
- [`T006_FINAL_CORRECTIONS_ADDENDUM.md`](T006_FINAL_CORRECTIONS_ADDENDUM.md) (Đặc tả FIX-02 và FIX-03)
- [`TEST_PLAN.md`](../03-quality/TEST_PLAN.md) (TS-009, TS-013, TS-014, TS-018)

---

## 2. Chi Tiết Các Module Thành Phần Đã Triển Khai (Implemented Modules)

### 2.1. Cấu hình SparkSession & Quản lý Tài nguyên (`src/flight_pipeline/config/spark_config.py`)
- **Factory function:** `get_spark_session(app_name="US_Flight_Performance_Analysis", memory_fraction=0.8, master="local[*]")`
- **Các thuộc tính kỹ thuật cốt lõi:**
  - **Memory Budget (FP-DEC-013):** Cấp phát 8 GB JVM heap (`spark.driver.memory = "8g"`), cấu hình giới hạn kích thước kết quả phân tích (`spark.driver.maxResultSize = "4g"`).
  - **Off-heap & Overhead:** Bật off-heap memory (`spark.memory.offHeap.enabled = "true"`, `spark.memory.offHeap.size = "2g"`).
  - **Phân vùng xáo trộn (Shuffle Partitions):** Cấu hình `spark.sql.shuffle.partitions = "16"` phù hợp với 16 vCPU cục bộ của máy trạm.
  - **Cơ chế Parquet & PyArrow:** Bật bộ tối ưu Vectorized Parquet Reader (`spark.sql.parquet.enableVectorizedReader = "true"`), kích hoạt PyArrow enabled (`spark.sql.execution.arrow.pyspark.enabled = "true"`).
  - **Thư mục tạm an toàn (Scratch Directory):** Thiết lập `spark.local.dir = "D:/Study/Code/Apache/Flight_Analyzt/tmp_spark"` để cách ly toàn bộ I/O tạm thời ra khỏi repository root, tránh ô nhiễm ổ đĩa hệ thống.
  - **Process-Level Python Isolation:** Cấu hình tự động `os.environ["PYSPARK_PYTHON"] = sys.executable` và `os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable` ngay trong phiên làm việc của tiến trình, bảo đảm PySpark driver và worker sử dụng chính xác môi trường Python ảo hiện tại mà không làm thay đổi biến môi trường toàn cục của Windows.

### 2.2. Vị Từ Kiểm Tra Số Thực & 7 Thước Đo CORE (`src/flight_pipeline/quality/predicates.py`)
Tuân thủ tuyệt đối đặc tả sửa lỗi kỹ thuật FIX-02 trong [`T006_FINAL_CORRECTIONS_ADDENDUM.md`](T006_FINAL_CORRECTIONS_ADDENDUM.md) và quyết định FP-DEC-002:
- **`is_finite_numeric(col_or_name)`:**
  Xây dựng biểu thức PySpark cột loại bỏ triệt để 4 trạng thái không hợp lệ:
  $$\text{Valid} \iff (\text{col IS NOT NULL}) \land (\text{NOT isNaN(col)}) \land (\text{col} \neq +\infty) \land (\text{col} \neq -\infty)$$
  Sử dụng trực tiếp `col_expr.isNotNull() & (~isnan(col_expr)) & (col_expr != float("inf")) & (col_expr != float("-inf"))`.
- **7 Thước Đo Số Học CORE (Core Continuous Metrics):**
  1. `is_valid_arr_delay(col_name="ARR_DELAY")`: Chấp nhận số thực hữu hạn (kể cả số âm phản ánh chuyến bay đến sớm theo FP-DEC-004 và KPI-03).
  2. `is_valid_dep_delay(col_name="DEP_DELAY")`: Chấp nhận số thực hữu hạn (kể cả số âm phản ánh khởi hành sớm theo FP-DEC-004).
  3. `is_valid_taxi_out(col_name="TAXI_OUT")`: Bắt buộc số thực hữu hạn và $\ge 0$.
  4. `is_valid_taxi_in(col_name="TAXI_IN")`: Bắt buộc số thực hữu hạn và $\ge 0$.
  5. `is_valid_air_time(col_name="AIR_TIME")`: Bắt buộc số thực hữu hạn và $\ge 0$.
  6. `is_valid_actual_elapsed_time(col_name="ACTUAL_ELAPSED_TIME")`: Bắt buộc số thực hữu hạn và $\ge 0$.
  7. `is_valid_crs_elapsed_time(col_name="CRS_ELAPSED_TIME")`: Bắt buộc số thực hữu hạn và $> 0$ (thời gian dự kiến không thể bằng 0 hoặc âm).

### 2.3. Hạch Toán Toàn Vẹn Dòng & Manifest Quản Trị (`src/flight_pipeline/utils/run_manifest.py`)
Tuân thủ nguyên tắc DC-11 và DC-12 trong [`DATA_CONTRACT.md`](../02-design/DATA_CONTRACT.md):
- **Model `RowAccounting`:**
  - Quản lý 4 chỉ số cơ bản: `total_input_rows`, `accepted_rows`, `quarantined_rows`, `rejected_rows`.
  - Phương thức `is_balanced()` kiểm tra nghiêm ngặt bất biến toán học:
    $$\text{accepted\_rows} + \text{quarantined\_rows} + \text{rejected\_rows} \equiv \text{total\_input\_rows}$$
  - Phương thức `calculate_valid_rate()` tính toán tỷ lệ hợp lệ thực sự trên tập được xem xét ($\frac{\text{accepted}}{\text{accepted} + \text{quarantined}}$), không nhầm lẫn với độ bao phủ thị trường (DC-12).
- **Model `RunManifest`:**
  - Tự động thu thập thông tin môi trường thực thi: OS platform, Python version, PySpark version, OpenJDK version, Git commit SHA, hostname, run ID dạng UUID4, timestamp UTC.
  - Tích hợp tính toán giá trị băm SHA-256 cho các artifact sinh ra.
  - Hỗ trợ xuất và nhập manifest dưới định dạng JSON có thụt lề chuẩn tắc.

### 2.4. Động Cơ Xuất Bản An Toàn Windows NTFS 7 Bước (`src/flight_pipeline/storage/publication.py`)
Hiện thực hóa đầy đủ quy trình 7 bước chống rách dữ liệu (FIX-03 và TS-013) được thiết kế đặc thù cho hệ thống tệp Windows NTFS:
1. **Bước 1 (Staging Isolation):** Dữ liệu được ghi vào thư mục staging độc lập có timestamp và UUID (`_stage_<run_id>`).
2. **Bước 2 (Integrity Verification):** Kiểm tra tính toàn vẹn của dữ liệu staging (kiểm tra không rỗng, kiểm tra row accounting `is_balanced() == True`). Nếu phát hiện mất cân bằng, ném ngoại lệ hủy bỏ ngay lập tức.
3. **Bước 3 (Fault Injection Hook):** Điểm can thiệp mô phỏng sự cố phục vụ bài kiểm thử TS-013 (`fault_trigger_stage == "pre_promote"`).
4. **Bước 4 (Prepare Version Directory):** Tạo thư mục đích phiên bản cụ thể (`versions/run_<timestamp>`).
5. **Bước 5 (Atomic / Safe Move):** Di chuyển thư mục staging sang thư mục phiên bản bằng `shutil.move` với cơ chế retry xử lý file-locking của Windows Defender / OS.
6. **Bước 6 (Pointer Switch / Manifest Update):** Cập nhật con trỏ `latest` (thông qua manifest hoặc tệp liên kết có ghi đè an toàn).
7. **Bước 7 (Cleanup / Rollback):** Tự động dọn dẹp thư mục staging. Nếu xảy ra bất kỳ lỗi nào ở bất kỳ bước nào, khối `finally`/`except` tự động kích hoạt dọn dẹp staging và khôi phục trạng thái an toàn.

### 2.5. Cấu Hình Ghi Nhật Ký Chuẩn Hóa (`src/flight_pipeline/utils/logging_config.py`)
- Cấu hình logging chuẩn format: `[timestamp] [level] [name]: message`.
- Tách luồng ghi log độc lập ra Console (stdout) và tệp log vật lý trong thư mục chỉ định.

### 2.6. Quản Lý Phụ Thuộc & CI Skeleton
- **`requirements.txt`:** Khóa cứng phiên bản phụ thuộc chính thức:
  - `pyspark==4.0.1`
  - `pyarrow==25.0.1`
  - `pandas==2.3.3`
- **`.github/workflows/ci.yml`:** Khung CI GitHub Actions thiết lập ma trận kiểm thử tự động, cài đặt JDK 21, Python 3.10, chạy toàn bộ unit tests và công cụ kiểm toán repository consistency.

---

## 3. Ranh Giới Chức Năng & Tuân Thủ Điều Kiện Cấm (Scope Boundaries)

Đợt triển khai này tuân thủ tuyệt đối các ranh giới do Project Lead và tài liệu `AGENTS.md` đề ra:
- **KHÔNG triển khai Ingestion Pipeline (T-007):** Không có logic đọc và phân tích 9 tệp CSV thô trong `data/raw/tabular/`. Thư mục thô được giữ nguyên vẹn 100%.
- **KHÔNG triển khai Data Quality Execution (T-008):** Không chạy các tác vụ phân loại, cách ly hay làm sạch dữ liệu quy mô lớn.
- **KHÔNG triển khai KPI Aggregation (T-010..013):** Chỉ triển khai vị từ logic ở mức biểu thức cột PySpark, chưa thực hiện tính toán KPI trên dữ liệu thực.
- Toàn bộ các mã nguồn chỉ phục vụ mục đích dựng khung nền tảng, cơ chế an toàn và chuẩn bị cho các gate kế tiếp.
