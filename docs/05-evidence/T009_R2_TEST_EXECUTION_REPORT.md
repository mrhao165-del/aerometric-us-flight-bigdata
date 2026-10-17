# T009-R2: AUTOMATED UNIT TEST EXECUTION & AUDIT REPORT

**Task ID:** `T-009` (Remediation & Independent Corrective Audit R2)  
**Gate:** `G4`  
**Auditor:** Software Testing & QA Engineer  
**Date:** 2026-10-17  
**Status:** `ALL_13_UNIT_TESTS_PASSED`  

---

## 1. Tổng Quan Thực Thi Kiểm Thử Đơn Vị Tự Động (Execution Overview)

Bộ kiểm thử đơn vị tự động đã được thực thi độc lập và toàn diện bằng bộ chạy kiểm thử `unittest` chuẩn của Python:

```powershell
python -m unittest discover -s tests -v
```

- **Mã thoát (Exit Code):** `0`
- **Tổng số bài kiểm thử thực thi:** `13 / 13 (100% PASS)`
- **Thời gian chạy thực tế:** `27.437 giây`
- **Thất bại (Failures):** `0`
- **Lỗi (Errors):** `0`
- **Tệp nhật ký thực thi nguyên bản:** [`T009_R2_LOG_UNITTESTS.txt`](T009_R2_LOG_UNITTESTS.txt)

---

## 2. Ma Trận 13 Bài Kiểm Thử Đơn Vị Chi Tiết (Unit Test Execution Matrix)

Bảng dưới đây ghi nhận chính xác 100% tên hàm kiểm thử thực tế và kết quả đo lường từ raw log:

| STT | Mô-đun Kiểm Thử | Tên Hàm Kiểm Thử Chuẩn Xác | Mục Tiêu & Cơ Chế Kiểm Tra | Kết Quả Thực Tế |
|:---:|---|---|---|:---:|
| 1 | [`test_manifest.py`](../../tests/test_manifest.py) | `test_dc12_ingest_acceptance_rate` | Tỷ lệ tiếp nhận nạp liệu $accepted / raw$ và quy tắc `ZERO_DENOMINATOR` trả về `None` khi $raw = 0$. | **PASS** |
| 2 | [`test_manifest.py`](../../tests/test_manifest.py) | `test_dc12_metric_accounting` | Hạch toán thước đo DC-12, `excluded_count`, `metric_valid_rate` và quy tắc `ZERO_DENOMINATOR`. | **PASS** |
| 3 | [`test_manifest.py`](../../tests/test_manifest.py) | `test_row_accounting_balance_invariant` | Bất biến DC-11: $raw = accepted + quarantined + rejected$ (ba trạng thái rời nhau). | **PASS** |
| 4 | [`test_manifest.py`](../../tests/test_manifest.py) | `test_run_manifest_lifecycle_and_hashing` | Vòng đời RunManifest, tự động dò môi trường, băm SHA-256 và tuần tự hóa JSON chuẩn tắc. | **PASS** |
| 5 | [`test_numeric_predicates.py`](../../tests/test_numeric_predicates.py) | `test_delay_predicates_preserve_signed_negative` | Bảo tồn số âm phản ánh chuyến bay đến/đi sớm cho `ARR_DELAY` và `DEP_DELAY` (FP-DEC-004, KPI-03). | **PASS** |
| 6 | [`test_numeric_predicates.py`](../../tests/test_numeric_predicates.py) | `test_duration_predicates_require_strictly_positive` | Ràng buộc thời gian bay thực tế và dự kiến `CRS_ELAPSED_TIME` bắt buộc $> 0$. | **PASS** |
| 7 | [`test_numeric_predicates.py`](../../tests/test_numeric_predicates.py) | `test_is_finite_numeric_matrix` | Bảng chân lý vị từ FIX-02: loại bỏ `None`, `NaN`, $+\infty$, $-\infty$, và chấp nhận số thực hữu hạn. | **PASS** |
| 8 | [`test_numeric_predicates.py`](../../tests/test_numeric_predicates.py) | `test_taxi_predicates_require_non_negative` | Ràng buộc thời gian lăn bánh `TAXI_OUT` và `TAXI_IN` bắt buộc $\ge 0$. | **PASS** |
| 9 | [`test_publication_safety.py`](../../tests/test_publication_safety.py) | `test_fault_injection_step5_preserves_previous_pointer_and_staging` | Mô phỏng sự cố TS-013: Bơm lỗi tại Bước 5, bảo tồn con trỏ cũ và không xóa bằng chứng staging. | **PASS** |
| 10 | [`test_publication_safety.py`](../../tests/test_publication_safety.py) | `test_successful_publication_sequence` | Xuất bản an toàn 7 bước NTFS, kiểm tra dữ liệu đích nguyên vẹn và con trỏ chuyển chính xác. | **PASS** |
| 11 | [`test_publication_safety.py`](../../tests/test_publication_safety.py) | `test_unbalanced_accounting_aborts_publication` | Chặn xuất bản ngay tại Bước 2 khi vi phạm bất biến dòng DC-11 (`ACCOUNTING_UNVERIFIED`). | **PASS** |
| 12 | [`test_publication_safety.py`](../../tests/test_publication_safety.py) | `test_version_immutability_rejection` | Từ chối ghi đè thư mục phiên bản đã tồn tại (`FAILED_VERSION_EXISTS`), bảo vệ tính bất biến. | **PASS** |
| 13 | [`test_spark_env.py`](../../tests/test_spark_env.py) | `test_spark_session_creation_and_config` | Khởi tạo SparkSession local, kiểm tra tham số cấu hình, tính toán phân tán RDD filter & count. | **PASS** |

---

## 3. Kiểm Thử Khói Khởi Tạo Spark ([`test_spark_env.py`](../../tests/test_spark_env.py))

Lệnh chạy độc lập: `python -m unittest tests.test_spark_env -v`
- Kết quả: `Ran 1 test in 10.824s ... OK (Exit Code 0)`.
- Cấu hình SparkSession đã xác nhận:
  - `spark.master`: `local[2]` (trong test) / `local[4]` (trong config mặc định)
  - `spark.sql.shuffle.partitions`: `4` (trong test) / `16` (trong config mặc định)
  - Phép tính phân tán: RDD sum `range(100) == 4950`, DataFrame count `2`.
  - Tệp nhật ký đầy đủ: [`T009_R2_LOG_SPARK_SMOKE.txt`](T009_R2_LOG_SPARK_SMOKE.txt).

---

## 4. Ghi Nhận Trung Thực Các Cảnh Báo Hệ Thống

Toàn bộ các cảnh báo ghi nhận trong quá trình thực thi:
1. `WARN Shell: Did not find winutils.exe`: Hadoop shell warning trên Windows; PySpark 4.0.1 vận hành bằng NIO2 không phụ thuộc vào `winutils.exe`.
2. `WARN NativeCodeLoader`: Thư viện native C của Hadoop không có trên Windows; Spark sử dụng bytecode Java thuần túy.
3. `ResourceWarning: unclosed socket`: Py4J gateway socket notification của Python 3.10; không làm rò rỉ bộ nhớ hay tài nguyên.

---

## 5. Kết Luận Kiểm Thử Đơn Vị (Test Verdict)

Toàn bộ 13 bài kiểm thử đơn vị tự động đã được thực thi thực tế, đạt kết quả **100% PASS (0 FAIL, 0 ERROR)**, hoàn toàn trung thực và đồng bộ với tệp nhật ký nguyên bản.
