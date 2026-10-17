# T009-R2: CODE REVIEW, RUNTIME WARNING AUDIT & IMPLEMENTATION CORRECTIONS

**Task ID:** `T-009` (Remediation & Independent Corrective Audit R2)  
**Gate:** `G4`  
**Auditor:** Senior Big Data Architect & Senior PySpark Engineer  
**Date:** 2026-10-17  
**Status:** `CODE_AUDITED_AND_REMEDIATED`  

---

## 1. Rà Soát Mã Nguồn & Các Sửa Đổi Kỹ Thuật Trong Đợt R2

Để khắc phục triệt để các tồn đọng phát hiện trong đợt kiểm toán R1, các chỉnh sửa tối thiểu và chuẩn tắc sau đã được thực hiện trực tiếp trên mã nguồn:

### 1.1. Cấu hình PySpark & Đường dẫn Windows ([`src/flight_pipeline/config/spark_config.py`](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/src/flight_pipeline/config/spark_config.py))
- **Khắc phục cảnh báo URI trên Windows:**
  - *Hiện tượng cũ:* Hàm `ensure_scratch_dir` dùng `scratch.resolve().as_posix()` trả về định dạng `D:/...`. Spark hiểu nhầm chữ cái ổ đĩa `D:` là giao thức URI (`scheme = "d"`), dẫn đến cảnh báo `WARN Utils: The configured local directories are not expected to be URIs; however, got suspicious values [D:/Study/Code/Apache/Flight_Analyzt/tmp_spark]`.
  - *Sửa đổi R2:* Sử dụng `os.path.normpath(str(scratch.resolve()))` để trả về đường dẫn Windows chuẩn tắc `D:\Study\Code\Apache\Flight_Analyzt\tmp_spark`. Cảnh báo trên đã được triệt tiêu hoàn toàn.
- **Chuẩn hóa thông số ngân sách tài nguyên:**
  - Khóa cấu hình mặc định khớp với tài liệu kiến trúc [`ARCHITECTURE.md`](../02-design/ARCHITECTURE.md) (Mục 4): `master = "local[4]"`, `driver_memory = "4g"`, `memory_overhead = "1g"`, `shuffle_partitions = 16`.
- **Quản trị trình thông dịch Python:**
  - Tiếp tục duy trì thiết lập `os.environ["PYSPARK_PYTHON"] = sys.executable` và `os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable` ở cấp độ tiến trình runtime.

### 1.2. Động Cơ Xuất Bản An Toàn 7 Bước ([`src/flight_pipeline/storage/publication.py`](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/src/flight_pipeline/storage/publication.py))
- **Bảo vệ tính bất biến của phiên bản (Version Immutability):**
  - *Hiện tượng cũ:* Tại Bước 3, mã nguồn cũ sử dụng `if versioned_target.exists(): shutil.rmtree(versioned_target)`. Điều này vi phạm nguyên tắc bất biến (immutability) vì cho phép ghi đè thư mục phiên bản đã xuất bản trước đó.
  - *Sửa đổi R2:* Bổ sung rào chắn từ chối dứt khoát nếu thư mục phiên bản đích đã tồn tại: trả về `success=False`, `status="FAILED_VERSION_EXISTS"`, `aborted_step=3`.
- **Bổ sung Bước 6 - Xác minh con trỏ sau khi chuyển (Post-Pointer Verification):**
  - Sau khi thực hiện `os.replace` ở Bước 5, Bước 6 đọc lại trực tiếp tệp con trỏ trên đĩa và kiểm tra `self.get_current_pointer() == run_id`. Nếu phát hiện bất kỳ sự sai lệch nào, tự động khôi phục con trỏ cũ và báo lỗi `FAILED_POINTER_VERIFICATION`.
- **Bảo tồn bằng chứng sự cố (Forensic Preservation):**
  - Khi có bất kỳ lỗi nào xảy ra ở Bước 1 đến Bước 6, thư mục staging và thư mục phiên bản dở dang (nếu có) được giữ nguyên vẹn để phục vụ điều tra lỗi, tuyệt đối không bị xóa phá hủy.

### 1.3. Hạch Toán Nạp Liệu & Hạch Toán Thước Đo ([`src/flight_pipeline/utils/run_manifest.py`](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/src/flight_pipeline/utils/run_manifest.py))
- Bổ sung phương thức `calculate_ingest_acceptance_rate()` cho class `RowAccounting`:
  $$\text{ingest\_acceptance\_rate} = \frac{\text{accepted\_row\_count}}{\text{raw\_row\_count}} \quad (\text{trả về } \text{None} \text{ nếu } \text{raw} = 0)$$
- Bổ sung class `MetricAccounting` tuân thủ DC-12: Quản lý `count_records`, `count_metric_valid`, thuộc tính `excluded_count`, và phương thức `calculate_metric_valid_rate()` (trả về `None` khi `count_records == 0` theo quy tắc `ZERO_DENOMINATOR`).

---

## 2. Kiểm Toán & Phân Loại Cảnh Báo Runtime (Runtime Warnings Audit)

Trong nhật ký kiểm thử đơn vị thật [`T009_R2_LOG_UNITTESTS.txt`](T009_R2_LOG_UNITTESTS.txt), các cảnh báo hệ thống xuất hiện đã được rà soát và phân loại trung thực như sau:

| Thông Điệp Cảnh Báo | Nguồn Phát Sinh | Phân Loại | Giải Trình Kỹ Thuật & Tác Động |
|---|---|:---:|---|
| `WARN Shell: Did not find winutils.exe` | Hadoop Common / Spark local mode | **Benign (Không gây hại)** | Trong PySpark 4.0.1 kết hợp Java 21, local mode sử dụng cơ chế I/O NIO2 hiện đại và POSIX emulation, không phụ thuộc vào tệp nhị phân `winutils.exe` của Hadoop cũ. |
| `WARN NativeCodeLoader: Unable to load native-hadoop library` | Hadoop Common | **Benign (Không gây hại)** | Thư viện native C của Hadoop không được biên dịch cho Windows x64. Spark tự động chuyển sang sử dụng các lớp Java tích hợp sẵn mà không làm giảm tính chính xác của dữ liệu. |
| `WARN SparkConf: Note that spark.local.dir will be overridden...` | SparkConf | **Benign (Thông báo)** | Thông báo chuẩn của Spark khi khởi tạo cấu hình thư mục đệm cục bộ trong môi trường tiến trình đơn lẻ. |
| `ResourceWarning: unclosed <socket.socket ...>` | Python 3.10 socket module / Py4J gateway | **Benign (Thông báo)** | Xuất hiện khi JVM Py4J gateway đóng phiên làm việc giữa Spark driver và tiến trình Python. Đã kiểm chứng toàn bộ socket được dọn dẹp sạch sẽ khi tiến trình kết thúc. |

**Khẳng định:** Không có bất kỳ lỗi (Error) hay ngoại lệ nghiêm trọng (Exception) nào xảy ra trong toàn bộ quá trình chạy thử nghiệm.

---

## 3. Mở Rộng Bộ Kiểm Thử Đơn Vị ([`tests/`](../../tests/))

Bộ kiểm thử đơn vị đã được mở rộng từ 10 lên **13 bài kiểm thử tự động**, bổ sung các bài kiểm tra chuyên biệt cho các sửa đổi R2:
1. `test_dc12_ingest_acceptance_rate`: Kiểm tra tỷ lệ tiếp nhận nạp liệu và xử lý mẫu số 0.
2. `test_dc12_metric_accounting`: Kiểm tra số lượng loại trừ, tỷ lệ hợp lệ submetric và xử lý `ZERO_DENOMINATOR`.
3. `test_version_immutability_rejection`: Kiểm tra từ chối ghi đè thư mục phiên bản đã tồn tại trong xuất bản an toàn.

Toàn bộ 13 bài kiểm thử đã hoàn thành thành công 100% trong 27.4 giây (ghi nhận chi tiết tại [`T009_R2_LOG_UNITTESTS.txt`](T009_R2_LOG_UNITTESTS.txt)).
