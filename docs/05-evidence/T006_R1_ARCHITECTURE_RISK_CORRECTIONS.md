# T-006-R1 RECONCILIATION REPORT 3: ARCHITECTURE & RESOURCE RISK CORRECTIONS

**Task ID:** `T-006-R1`  
**Gate:** `G3`  
**Document Nature:** Technical Architecture, Resource Budget & Risk Assessment Reconciliation (`DESIGN_ONLY`)  
**Project:** US Flight Performance Analysis (2016–2024) using Apache Spark / PySpark  
**Status:** `PROPOSED_FOR_PROJECT_LEAD_REVIEW`  
**Date:** 2026-10-17  
**Supersedes:** `docs/05-evidence/T006_ARCHITECTURE_AND_RUNTIME_DESIGN.md` (Mục 3, Mục 4, Mục 5 & Mục 6)

---

## 1. Mục tiêu & Ranh giới Kỹ thuật (Authority & Objectives)

Hồ sơ này rà soát độc lập và đính chính các tuyên bố kỹ thuật chưa được kiểm chứng, các giả định quá mức lạc quan về tài nguyên, và các rủi ro hệ điều hành Windows trong gói thiết kế kiến trúc ban đầu của `T-006`:
1. Ranh giới chứng minh nguồn gốc dữ liệu thô và trạng thái `OR-08` (`IDENTITY_UNVERIFIED`).
2. Định mức ngân sách bộ nhớ thực tế trên máy trạm 15.71 GiB RAM (loại bỏ nhãn `MEASURED_SAFE` khi chưa đo đạc).
3. Ranh giới kỹ thuật phân vùng Parquet và kích thước tệp.
4. Ranh giới giải pháp định danh dòng ổn định (`TS-020`) và tính phân tán của Apache Spark.
5. Cơ chế xuất bản dữ liệu an toàn trên hệ thống tệp Windows NTFS (cảnh báo file locking).
6. Kế hoạch kiểm chứng tương thích bộ công nghệ PySpark 4.0.1 / Java 21 / Python 3.10 tại G4/T-009.

---

## 2. Ranh giới Chứng minh Nguồn gốc Dữ liệu Thô (Raw Data Provenance & OR-08)

### 2.1. Thực trạng Kiểm toán & Giới hạn của `SOURCE_MANIFEST.json`
- `docs/05-evidence/inputs/SOURCE_MANIFEST.json` (kích thước `2,479` bytes, SHA-256 `5e11e6...`) chứng nhận tính toàn vẹn của **các tệp evidence và metadata audit** được đăng ký trong manifest.
- **Tuyên bố cần đính chính:** Manifest này **không chứng minh danh tính từng byte (byte identity)** của 9 tệp CSV thô (`data/raw/tabular/{year}/flight_with_weather_{year}.csv`) so với cơ sở dữ liệu gốc của Cục Thống kê Vận tải Hoa Kỳ (BTS TranStats).
- **Rủi ro `OR-08` (`IDENTITY_UNVERIFIED` / `METADATA_MATCH_ONLY`):**
  - Sự trùng khớp về kích thước tệp (`bytes`) và thời gian sửa đổi (`mtime`) trong `source_signature` chỉ chứng minh tệp CSV cục bộ không bị sửa đổi kể từ thời điểm chạy audit ban đầu.
  - Sự trùng khớp này **không tương đương với việc nội dung đã được xác minh bằng mã băm SHA-256 đối chiếu với BTS**.
  - Việc tính toán mã băm SHA-256 cục bộ của 9 tệp CSV tại Gate G4/T-007 (`TS-019`) đóng vai trò là **mốc đối soát nội bộ bất biến (local baseline)**, không tự động biến dữ liệu thành "BTS-verified".
  - Giữ nguyên trạng thái rủi ro `OR-08 = IDENTITY_UNVERIFIED` cho đến khi có bằng chứng đối soát độc lập.

---

## 3. Định mức Ngân sách Tài nguyên & Bộ nhớ Thực tế (Resource Budget Reconciliation)

### 3.1. Phân tích Hiện trạng Máy trạm Thực thi
Theo kết quả đo lường phần cứng thực tế tại thời điểm kiểm toán T-006:
* **Tổng RAM vật lý:** 15.71 GiB (~16 GB).
* **RAM khả dụng thực tế:** Dao động từ **5.72 GiB đến 6.5 GiB** (do hệ điều hành Windows 10 và các tiến trình nền chiếm dụng ~9.5–10 GiB).
* **Ổ đĩa D:\:** Khả dụng **64.3 GiB** (đủ cho không gian staging và shuffle spill).

### 3.2. Đính chính Nhãn Cấp phát Tài nguyên
1. **Loại bỏ nhãn `MEASURED_SAFE` cho cấu hình 7–8 GiB:**
   - Việc tuyên bố cấp phát `spark.driver.memory = 7g - 8g` là "MEASURED_SAFE" trên máy chỉ còn trống ~6 GiB khả dụng là một **sai lệch nghiêm trọng**, có nguy cơ đẩy hệ điều hành vào trạng thái cạn kiệt RAM vật lý (*hard paging / thrashing*).
   - Mọi thông số cấp phát bộ nhớ tại G3 bắt buộc phải phân loại là **`ESTIMATED` (Ước tính thiết kế)**, tuyệt đối không gắn nhãn `MEASURED_SAFE` khi chưa có dữ liệu benchmark thực tế.
2. **Phân tách các thành phần tiêu thụ bộ nhớ:**
   Cần phân biệt rõ ràng 5 thành phần cạnh tranh RAM:
   - **Spark Driver Heap (`spark.driver.memory`):** Vùng nhớ JVM quản lý DAG, Catalyst optimizer, và metadata phân vùng.
   - **Spark Off-Heap / Overhead (`spark.driver.memoryOverhead`):** Tối thiểu 10% (512 MB – 1 GiB) cho native allocations của JVM, Netty buffers, và Arrow memory.
   - **Tiến trình Python Worker:** Khi PySpark thực thi UDF hoặc Arrow serialization, các tiến trình `python.exe` chạy độc lập ngoài JVM và tiêu thụ RAM của hệ điều hành.
   - **Bộ đệm Hệ điều hành (OS Buffer Cache):** Windows cần bộ nhớ đệm trang (*page cache*) để tăng tốc đọc ghi tệp CSV và Parquet.
   - **Ổ đĩa Shuffle / Spill (`spark.local.dir`):** Nằm trên Drive D:\ (tránh ghi vào ổ C:\ hệ thống).
3. **Cấu hình Đề xuất Thận trọng tại G4/G5:**
   - **Chế độ Smoke / Single-Year:** `spark.driver.memory = 3g - 4g`, `memoryOverhead = 1g`, số luồng `local[4]`.
   - **Chế độ Full-Run (nếu chạy toàn bộ):** `spark.driver.memory = 5g - 6g`, `memoryOverhead = 1g - 1.5g`, số luồng `local[6]`.
4. **Loại bỏ Cam kết Triệt tiêu OOM của Chiến lược Batching theo Năm:**
   - Thiết kế "Year-by-Year Ingestion Batching" (nạp tuần tự từng năm) giúp giảm mạnh footprint bộ nhớ so với nạp 9 năm cùng lúc.
   - **Tuy nhiên, không thể đảm bảo triệt tiêu 100% rủi ro OOM**: Các phép toán phân vị phức tạp (`percentile_approx`), việc thu thập kết quả lớn (`collect()`), hoặc hiện tượng lệch dữ liệu (*data skew*) tại các sân bay lớn (ATL, ORD) vẫn có thể gây bùng nổ bộ nhớ.
   - Mọi tuyên bố về RAM cực đại (ví dụ: "đỉnh RAM < 2 GiB/năm" hoặc "full-run RAM chỉ 600 MB - 1.2 GiB") là các giả định chưa được chứng minh, bắt buộc phải đo đạc thực nghiệm bằng bài test `TS-014` tại Gate G5.

---

## 4. Ranh giới Thiết kế Tầng Lưu trữ Chuẩn hóa Parquet (Curated Parquet Layout)

### 4.1. Phân biệt Ba Khái niệm Phân vùng (Partitioning Distinction)
Hồ sơ thiết kế cần phân định rạch ròi 3 khái niệm thường bị nhầm lẫn:
1. **Thư mục phân vùng logic (Hive-style partition directory):** Thư mục theo năm trên đĩa (`year=2016/` đến `year=2024/`, gồm đúng 9 thư mục).
2. **Phân vùng thực thi trong bộ nhớ (Spark execution partitions / RDD partitions):** Số lượng khối dữ liệu được xử lý song song trong bộ nhớ (quy định bởi `spark.sql.shuffle.partitions` hoặc kích thước khối đọc CSV `spark.sql.files.maxPartitionBytes`, thường là 16 đến 64 partitions).
3. **Số lượng tệp vật lý Parquet trên đĩa (Physical Parquet file count):** Số tệp `.snappy.parquet` thực tế được ghi ra trong mỗi thư mục năm.

### 4.2. Tính chất Ước lượng của Kích thước Tệp
- Kích thước ước tính `250 MB - 350 MB` mỗi năm sau nén Snappy chỉ là **dự báo lý thuyết** dựa trên tỷ lệ nén thông thường của dữ liệu dạng bảng.
- Kích thước thực tế phụ thuộc vào tính lặp lại của dữ liệu (cardinality của chuỗi IATA) và kích thước khối mã hóa từ điển (*dictionary encoding*).
- Kiểm chứng thực tế tỷ lệ nén và số lượng tệp sẽ được nghiệm thu tại `TS-014` (Gate G5/G6).

### 4.3. Quản lý Phiên bản Đầu ra theo `run_id` (Idempotent Publication)
- Mọi lần ghi dữ liệu trung gian bắt buộc ghi vào đường dẫn có gắn định danh lần chạy duy nhất: `data/staging/{run_id}/`.
- **Quy tắc bảo vệ dữ liệu:** Tuyệt đối không ghi đè trực tiếp (*silent overwrite*) lên tập dữ liệu curated hiện hành. Việc thăng cấp dữ liệu chỉ diễn ra sau khi toàn bộ hạch toán dòng `DC-11` được thẩm định thành công.

---

## 5. Ranh giới Kỹ thuật Định danh Dòng Ổn định (Stable Lineage — TS-020)

### 5.1. Bản chất Kỹ thuật & Giới hạn của Apache Spark
1. **`source_row_number` là trường ĐỀ XUẤT THIẾT KẾ, không phải hàm có sẵn của Spark CSV Reader:**
   - Spark CSV Reader mặc định đọc song song theo byte-split và không duy trì chỉ số dòng vật lý liên tục xuyên suốt các partition.
   - Hàm `monotonically_increasing_id()` tạo ra định danh phụ thuộc vào Partition ID (31 bit cao), sẽ thay đổi nếu số partition hoặc cấu hình đọc thay đổi giữa các lần chạy $\implies$ Không tái lập.
2. **Phương án Khả thi cho G4/T-007:**
   - *Phương án A:* Ingestion tuần tự từng năm với cấu hình đọc đơn luồng hoặc chỉ định `maxPartitionBytes` lớn hơn kích thước tệp năm để sinh chỉ số dòng vật lý xác định.
   - *Phương án B:* Kết hợp `source_year` + `hash64(all_34_columns)` + bộ đếm phân biệt cho các dòng trùng lặp hoàn toàn.
3. **Phân loại Trạng thái Pháp lý:**
   - Định danh dòng ổn định bắt buộc giữ nhãn **`OPEN_DESIGN_VERIFICATION`**.
   - Phương án cụ thể sẽ được thí nghiệm và kiểm chứng độc lập tại Gate G4 (`T-007`) và Gate G5 (`T-010`, `T-011`) theo bài kiểm tra `TS-020`.
4. **Bảo tồn Phản ví dụ Cặp Chuyến bay `YX 3624`:**
   - Hai bản ghi chuyến bay `YX 3624` ngày `2018-06-21` (`DEN -> XNA`, dòng 6.384.132 và 6.384.133 trong `schema_2018.json`) trùng toàn bộ khóa nghiệp vụ nhưng là 2 bản ghi vật lý riêng biệt đã được kiểm toán.
   - Bất kỳ giải pháp lineage nào cũng phải bảo tồn trọn vẹn cả 2 bản ghi, tuyệt đối cấm deduplicate làm mất dữ liệu.

---

## 6. Cơ chế Xuất bản Dữ liệu & Cảnh báo File-Locking trên Windows NTFS

### 6.1. Hạn chế của Windows NTFS đối với Thao tác Rename
- Trên hệ điều hành Linux/POSIX, lệnh đổi tên thư mục (`rename`) là nguyên tử (*atomic*).
- **Trên Windows NTFS:** Thao tác đổi tên thư mục có thể thất bại với lỗi `AccessDeniedException` hoặc `SharingViolation` nếu có bất kỳ tiến trình nào (Spark file reader, JVM thread, Windows Search Indexer, hoặc phần mềm diệt virus) đang giữ file handle mở trên các tệp Parquet trong thư mục đó.
- Do đó, kiến trúc **không được hứa hẹn cơ chế "universal atomic directory rename"** mà phải thiết kế cơ chế xuất bản an toàn:
  1. Ghi dữ liệu vào thư mục staging độc lập: `data/staging/{run_id}/curated/`.
  2. Xác thực cân bằng hạch toán dòng: `raw == accepted + quarantined + rejected`.
  3. Cập nhật con trỏ phiên bản xuất bản chính thức (`latest_run_id` trong manifest).
  4. Nếu thao tác rename thư mục đích phát sinh file locking, hệ thống kích hoạt cơ chế retry có backoff hoặc ghi nhận cảnh báo để Project Lead can thiệp, không để xảy ra tình trạng mất dữ liệu hoặc dữ liệu bán phần.
  5. **Bảo tồn dấu vết lỗi:** Tuyệt đối không tự động xóa dấu vết của các lần chạy thất bại; mọi artifacts của lần chạy lỗi phải được lưu trữ để phục vụ kiểm toán nguyên nhân gốc rễ (*root-cause audit*).

---

## 7. Đánh giá Môi trường Runtime & Kế hoạch Thử nghiệm G4/T-009

### 7.1. Bộ Công nghệ Mục tiêu (Candidate Stack)
Dựa trên hiện trạng phần mềm đã cài đặt trên máy chủ:
- **PySpark:** `4.0.1`
- **Java:** OpenJDK `21.0.12.1 LTS` (Eclipse Adoptium)
- **Python:** `3.10.11` (64-bit)
- **PyArrow:** `25.0.1`

### 7.2. Ranh giới Chấp nhận & Kế hoạch Bootstrap Smoke-test
- **Nguyên tắc an toàn:** Tuyệt đối không tự ý cài đặt thêm phần mềm, hạ phiên bản hay thay đổi biến môi trường hệ thống trong giai đoạn thiết kế G3.
- **Kế hoạch Kiểm chứng Tương thích tại G4 / Task `T-009`:**
  - Nhiệm vụ `T-009` bắt buộc phải thực thi trước `T-007` và `T-008`.
  - `T-009` sẽ chạy một bài kiểm thử bootstrap tối thiểu (`TS-014` bootstrap smoke):
    1. Khởi tạo `SparkSession` local.
    2. Đọc và ghi một tập dữ liệu giả lập nhỏ (synthetic DataFrame) ra tệp Parquet trên ổ đĩa D:\.
    3. Kiểm tra khả năng tương thích của PySpark 4.0 với Java 21 (xử lý các cờ JVM `--add-opens` nếu có cảnh báo reflection).
    4. Xác nhận sự hiện diện và hoạt động của tiện ích Windows native (`winutils.exe` / `hadoop.dll`) nếu môi trường yêu cầu.
  - **Phân định rõ ràng:** Việc cài đặt thư viện thành công (import package thành công trong Python) **không đồng nghĩa với việc runtime tương thích 100% trong quá trình xử lý dữ liệu lớn**. Mọi kết luận tương thích chỉ được xác nhận sau khi `T-009` hoàn thành có bằng chứng lệnh và log thực thi.

---

## 8. Kết luận & Chốt chặn Tuân thủ (Compliance Sign-off)

1. **Minh bạch Nguồn gốc:** Xác nhận `SOURCE_MANIFEST.json` attests bằng chứng đăng ký, dữ liệu thô giữ trạng thái `IDENTITY_UNVERIFIED` (`OR-08`).
2. **Kỷ luật Bộ nhớ:** Đưa toàn bộ định mức cấp phát RAM về nhãn `ESTIMATED`; yêu cầu kiểm nghiệm thực tế `TS-014` tại Gate G5.
3. **An toàn Hệ thống:** Cảnh báo file locking trên Windows NTFS và chuẩn hóa quy trình xuất bản an toàn có kiểm tra cân bằng hạch toán.
4. **Bảo tồn Lineage:** Giữ trạng thái `OPEN_DESIGN_VERIFICATION` cho định danh dòng ổn định và bảo toàn phản ví dụ `YX 3624`.
