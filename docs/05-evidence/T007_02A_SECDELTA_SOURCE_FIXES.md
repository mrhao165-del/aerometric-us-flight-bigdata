# T007-02A-SECURITY-DELTA Source Code Remediation Audit

**Document ID:** `T007_02A_SECDELTA_SOURCE_FIXES.md`  
**Date:** 2026-10-17  
**Task:** `T007-02A-SECURITY-DELTA` (Final Fail-Closed Path Validation & Source Integrity)  
**Parent Task:** `T-007` (Raw CSV Ingestion Pipeline)  
**Parent Gate:** `G4` (`PLANNED / NOT_COMPLETED`)  
**Status:** `AUDITED_AND_REMEDIATED`  
**Engineer:** Senior Python Filesystem Security Engineer, Data Integrity Auditor & Independent QA Engineer  

---

## 1. Mục tiêu và Phạm vi Khắc phục (Remediation Scope)

Đợt bổ sung an ninh `T007-02A-SECURITY-DELTA` được thực hiện theo phương thức **`MINIMAL TARGETED FIX — FAILING TESTS FIRST`** nhằm giải quyết dứt điểm các điểm yếu biên giới filesystem và khuyết tật kiểm thử còn lại trong module `src/flight_pipeline/ingestion/source_validator.py` và `tests/test_t007_source_validator.py`.

Ranh giới tuân thủ nghiêm ngặt:
- Không sửa đổi hay ghi đè mã nguồn T-009 (`publication.py`, `run_manifest.py`).
- Không sửa đổi Canonical Schema Module T007-01 (`schema.py`).
- Tuyệt đối không đọc, quét hay truy cập 15.2 GB của 9 tệp CSV thô thật trong `data/raw/tabular/`.
- Không tự ý mở Subtask `T007-02B` hay các subtask `T007-03..07`.
- Không tự ý nghiệm thu Gate G4 (`G4` tiếp tục giữ nguyên `PLANNED / NOT_COMPLETED`).

---

## 2. Chi tiết Kỹ thuật Khắc phục 3 Khuyết tật An ninh

### 2.1. FIX-SEC01 — Chuyển đổi Cơ chế Kiểm tra Thuộc tính `os.lstat` Sang Fail-Closed Tuyệt đối

- **Khuyết tật trước sửa đổi:**
  Trong hàm `is_symlink_or_reparse(path_obj)`, khối `try...except (OSError, ValueError): pass` đã bắt nuốt toàn bộ các ngoại lệ `OSError` (bao gồm `PermissionError`, `EIO`, disk read error) và tiếp tục thực hiện `return False`. Hành vi này vi phạm nguyên tắc an toàn fail-closed: khi hệ điều hành từ chối quyền truy cập hoặc phát sinh lỗi đọc thuộc tính của một thành phần đường dẫn, hệ thống lại ngộ nhận đường dẫn đó "không phải symlink/junction" và cho phép tiếp tục xử lý. Đồng thời, việc dùng `curr.exists()` trên chuỗi tổ tiên đã bỏ qua kiểm tra khi thư mục cha bị chặn quyền.
- **Biện pháp khắc phục triệt để:**
  1. Tái cấu trúc hàm `is_symlink_or_reparse(path_obj)`:
     - Ngoại lệ `FileNotFoundError` được bóc tách riêng: chỉ khi tệp thực sự không tồn tại trên filesystem thì hàm mới trả về `False` (đảm bảo không làm hỏng logic phát hiện tệp thiếu `SOURCE_MISSING`).
     - Bất kỳ ngoại lệ truy cập hoặc I/O nào khác (`PermissionError`, `OSError(errno.EIO, ...)`, `ValueError`) đều ngay lập tức kích hoạt `SourcePathSecurityError` kèm thông điệp chi tiết, chặn đứng việc ngộ nhận an toàn.
  2. Nâng cấp `validate_path_safety()`:
     - Loại bỏ việc bọc kiểm tra bằng `curr.exists()`. Mọi thành phần tổ tiên (`curr = path_obj.parent` và `curr_res = resolved_path.parent`) đều được chuyển trực tiếp qua `is_symlink_or_reparse()`. Nếu một thư mục cha trung gian bị cấm truy cập hoặc phát sinh lỗi I/O, `SourcePathSecurityError` lập tức được kích hoạt.
     - Bảo toàn việc kiểm tra symlink/reparse point tại tệp lá và toàn bộ chuỗi tổ tiên trước và sau khi resolve.
     - Bảo toàn việc đối soát containment trong `base_dir`.

---

### 2.2. FIX-SEC02 — Khôi phục Kiểm thử Phạm vi Tĩnh Bằng Phân tích AST Thực thụ

- **Khuyết tật trước sửa đổi:**
  Phương thức kiểm thử `test_scope_02_validator_contains_no_csv_reader_or_publication_code` trong `tests/test_t007_source_validator.py` chỉ thực hiện nạp mã nguồn qua `inspect.getsource(sv_module)` và gán vào biến nhưng hoàn toàn không chứa bất kỳ lệnh `assert` nào. Bài kiểm thử luôn `PASS` giả tạo mà không kiểm tra gì.
- **Biện pháp khắc phục triệt để:**
  1. Xây dựng hàm kiểm định cây cú pháp trừu tượng `_check_ast_for_forbidden_ingestion_or_publication(source_code: str) -> list[str]`:
     - Duyệt đệ quy toàn bộ nút AST (`ast.walk`).
     - Kiểm tra nút `Import` và `ImportFrom`: cấm triệt để các module `pyspark`, `pandas`, `csv`, và cấm nhập từ gói `flight_pipeline.publication`.
     - Kiểm tra nút `Call`: cấm các lệnh gọi trực tiếp hoặc thuộc tính liên quan tới nạp dữ liệu hay xuất bản: `SafePublisher()`, `publish_atomic()`, `classify_records()`, `quarantine_records()`, và `.read.csv()`.
  2. Cập nhật `test_scope_02_validator_contains_no_csv_reader_or_publication_code` với assertion thực sự:
     `self.assertEqual(violations, [])`.
  3. Bổ sung bài kiểm thử đột biến âm tính `test_scope_02_mutation_detection_fails_on_forbidden_constructs`:
     Chứng minh rằng khi đưa đoạn mã đột biến chứa `import csv`, `from flight_pipeline.publication import SafePublisher`, `SafePublisher()`, `spark.read.csv()`, `classify_records()` vào, hàm kiểm định phát hiện tối thiểu 4 vi phạm và ném cờ bắt giữ chính xác.

---

### 2.3. FIX-SEC03 — Bóc tách và Xử lý Có Cấu trúc Lỗi I/O Metadata Trong `verify_source`

- **Khuyết tật trước sửa đổi:**
  Trong `verify_source()`, việc lấy kích thước tệp qua `os.path.getsize(path_obj)` chỉ bọc `PermissionError`. Nếu phát sinh `OSError` khác (như lỗi sector đĩa `errno.EIO`), ngoại lệ không được bắt và làm sập tiến trình ngay cả khi cấu hình `fail_fast=False`. Ngoài ra, việc dùng `path_obj.exists()` trước đó có nguy cơ bắt nuốt `OSError` và ngụy tạo thành `SOURCE_MISSING`.
- **Biện pháp khắc phục triệt để:**
  1. Hợp nhất việc kiểm tra metadata và kích thước tệp vào một lệnh gọi `os.stat(path_obj)` duy nhất có cấu trúc phân tầng rõ ràng:
     - `FileNotFoundError`: Trả về `VerificationState.SOURCE_MISSING` (hoặc ném `SourceNotFoundError` nếu `fail_fast=True`).
     - `PermissionError`: Trả về `VerificationState.SOURCE_READ_ERROR` (hoặc ném `SourcePermissionError` nếu `fail_fast=True`).
     - `OSError` khác (ví dụ `EIO`): Trả về `VerificationState.SOURCE_READ_ERROR` kèm thông điệp rõ ràng `I/O error reading metadata for ...` (hoặc ném `SourceIntegrityError` nếu `fail_fast=True`).
  2. Kiểm tra tệp thông thường qua `stat.S_ISREG(st_mode)`: Nếu là thư mục hoặc thiết bị đặc biệt, trả về `SOURCE_READ_ERROR` (hoặc `SourceIntegrityError` nếu `fail_fast=True`).
  3. Lấy kích thước byte trực tiếp từ `st.st_size`, loại bỏ hoàn toàn lệnh gọi thừa `os.path.getsize()`.
  4. Xác lập ma trận batch: Bất kỳ nguồn nào gặp lỗi I/O metadata đều ép `all_present=False`, `all_sizes_match=False`, `all_hashes_verified=False`.

---

## 3. Đối chiếu Tính Nhất quán và Ranh giới Thực thi

- **Kiểm thử đơn vị:** 37/37 tests PASS trong `tests/test_t007_source_validator.py`.
- **Kiểm thử toàn diện repo:** 96/96 tests PASS trong `python -m unittest discover tests`.
- **T-009 & T007-01:** Bảo toàn nguyên vẹn mã nguồn và mã băm SHA-256 đã phê duyệt.
- **Dữ liệu thô:** 100% kiểm thử chạy trên fixture tổng hợp trong thư mục tạm, không chạm 9 CSV thật.
