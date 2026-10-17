# T007-02A Hash & Inventory Synthetic Test Suite Execution Record

**Document ID:** `T007_02A_HASH_AND_INVENTORY_TESTS.md`  
**Date:** 2026-10-17  
**Task:** `T007-02A` (Source Inventory & Local Hash Verifier Implementation)  
**Parent Gate:** `G4` (`PLANNED / NOT_COMPLETED`)  
**Status:** `VERIFIED_PASS`  
**Engineer:** Lead Independent QA Reviewer & Test Automation Engineer  

---

## 1. Mục tiêu và Nguyên tắc Kiểm thử Cách ly

Toàn bộ quá trình kiểm thử cho module `source_validator.py` được thiết kế tuân thủ nghiêm ngặt nguyên tắc **cách ly tuyệt đối dữ liệu thô (Strict Raw-Data Isolation)**:
1. **Không truy cập dữ liệu thực:** Mọi bài kiểm thử chạy trên thư mục tạm thời độc lập do hệ điều hành cấp phát (`tempfile.TemporaryDirectory`).
2. **Không đọc byte nào của 9 tệp CSV 15.2 GB:** Không mở luồng đọc, không tính hash, không quét thư mục `data/raw/tabular/`.
3. **Cơ chế Dependency Injection:** Sử dụng tham số `base_dir` và `inventory` tùy biến để tiêm các dữ liệu giả lập (synthetic fixtures) vào `SourceValidator`.

---

## 2. Chi tiết 21 Ca Kiểm thử Tổng hợp (21/21 PASS)

Bộ kiểm thử tại `tests/test_t007_source_validator.py` bao gồm 21 ca kiểm thử chuyên sâu được chia thành 6 nhóm:

### 2.1. Nhóm Kiểm tra Cấu trúc Inventory (INV-01 .. INV-03)
- **`test_inv_01_audited_inventory_entry_count_and_years` (INV-01):**
  - Kiểm tra từ điển `AUDITED_SOURCE_INVENTORY` có chính xác 9 mục tương ứng 9 năm liên tục từ 2016 đến 2024.
  - Kiểm tra mỗi mục có `audited_column_count == 34`.
  - **Kết quả:** `PASS`.
- **`test_inv_02_no_duplicate_years_or_paths` (INV-02):**
  - Kiểm tra không có năm nào bị trùng lặp.
  - Chuẩn hóa đường dẫn dạng chữ thường, kiểm tra tính duy nhất tuyệt đối của 9 đường dẫn tương đối.
  - **Kết quả:** `PASS`.
- **`test_inv_03_expected_row_counts_and_byte_sizes` (INV-03):**
  - Đối chiếu số dòng và số byte từng năm so với metadata G1 được kiểm toán.
  - Tổng số dòng = **54,674,003**; tổng số byte = **15,196,366,173**.
  - **Kết quả:** `PASS`.

---

### 2.2. Nhóm Kiểm tra Băm Streaming SHA-256 (HASH-01 .. HASH-06)
- **`test_hash_01_streaming_sha256_matches_hashlib_reference` (HASH-01):**
  - Tạo tệp CSV giả lập, băm bằng `SourceValidator.compute_file_hash` và so sánh với `hashlib.sha256(content).hexdigest()`.
  - **Kết quả:** `PASS` (mã băm khớp 100%).
- **`test_hash_02_empty_file_hashing` (HASH-02):**
  - Kiểm thử tệp rỗng (0 bytes).
  - Thu được mã băm chuẩn: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`.
  - **Kết quả:** `PASS`.
- **`test_hash_03_file_larger_than_multiple_blocks` (HASH-03):**
  - Tạo tệp nhị phân có kích thước lớn hơn nhiều block (5 block 1 KB + phần dư).
  - Kiểm tra tính toán streaming chính xác qua nhiều vòng lặp `read(chunk_size)`.
  - **Kết quả:** `PASS`.
- **`test_hash_04_streaming_memory_bound_chunk_reads` (HASH-04):**
  - Xác minh cơ chế đọc từng phần (chunk-based read), bộ nhớ RAM không tăng theo kích thước tệp mà bị chặn bởi `chunk_size`.
  - **Kết quả:** `PASS`.
- **`test_hash_05_detect_hash_mismatch` (HASH-05):**
  - Tiêm mã băm giả (`0000...0000`) vào baseline.
  - Ở chế độ thường: nhận trạng thái `HASH_MISMATCH`, `is_verified == False`.
  - Ở chế độ `fail_fast=True`: kích hoạt ngoại lệ `SourceHashMismatchError`.
  - **Kết quả:** `PASS`.
- **`test_hash_06_unapproved_baseline_cannot_conclude_verified` (HASH-06):**
  - Khi chưa cung cấp baseline được duyệt (`approved_baseline_hashes=None`), trạng thái nhận được là `LOCAL_HASH_COMPUTED_UNAPPROVED`.
  - `is_verified == False`, `batch.all_hashes_verified == False`, `batch.has_unapproved_candidate_hashes == True`.
  - **Kết quả:** `PASS` (chứng minh candidate hash không bao giờ bị ngộ nhận thành verified).

---

### 2.3. Nhóm Xử lý Lỗi và Biên An toàn (ERR-01 .. ERR-07)
- **`test_err_01_missing_file` (ERR-01):**
  - Tệp vắng mặt $\implies$ trạng thái `SOURCE_MISSING`; ở chế độ `fail_fast=True` kích hoạt `SourceNotFoundError`.
  - **Kết quả:** `PASS`.
- **`test_err_02_permission_error_fail_closed` (ERR-02):**
  - Lỗi phân quyền đọc tệp $\implies$ kích hoạt `SourcePermissionError` (fail-closed).
  - **Kết quả:** `PASS`.
- **`test_err_03_file_modified_during_hashing` (ERR-03):**
  - Giả lập xung đột kích thước/mtime giữa thời điểm `stat_before` và `stat_after`.
  - Kích hoạt ngoại lệ `SourceChangedDuringReadError`.
  - **Kết quả:** `PASS`.
- **`test_err_04_invalid_path_traversal` (ERR-04):**
  - Kiểm tra đường dẫn chứa `..` hoặc trỏ ra ngoài thư mục gốc $\implies$ kích hoạt `SourcePathSecurityError`.
  - **Kết quả:** `PASS`.
- **`test_err_05_symlink_escape_rejected` (ERR-05):**
  - Kiểm tra symbolic link $\implies$ bị từ chối với `SourcePathSecurityError`.
  - **Kết quả:** `PASS`.
- **`test_err_06_size_mismatch_detected` (ERR-06):**
  - Tệp có kích thước khác kích thước baseline $\implies$ trạng thái `SIZE_MISMATCH`, kích hoạt `SourceSizeMismatchError` trên `fail_fast=True`.
  - **Kết quả:** `PASS`.
- **`test_err_07_corrupt_baseline_format` (ERR-07):**
  - Baseline chứa ký tự không phải hex, chuỗi không đủ 64 ký tự, hoặc năm không thuộc inventory $\implies$ kích hoạt `SourceConfigurationError`.
  - **Kết quả:** `PASS`.

---

### 2.4. Nhóm Tương thích API Sản xuất (API-01)
- **`test_api_01_run_manifest_record_input_compatibility` (API-01):**
  - Tạo instance `RunManifest` (từ T-009).
  - Gọi `validator.record_into_run_manifest()`.
  - Chứng minh gọi đúng phương thức `record_input(path, bytes_count, sha256_hash)` theo `DOC-F02`.
  - Nguồn verified ghi mã hash thật; nguồn chưa verified ghi `"UNVERIFIED"`.
  - **Kết quả:** `PASS`.

---

### 2.5. Nhóm Bất biến Quản trị (GOV-01, GOV-02)
- **`test_gov_01_source_manifest_not_used_as_raw_hash_registry` (GOV-01):**
  - Kiểm tra tuyên bố kỹ thuật trong `SOURCE_MANIFEST.json` khẳng định tệp này không quản lý raw CSV hashes theo `DOC-F01`.
  - **Kết quả:** `PASS`.
- **`test_gov_02_upstream_identity_unverified_invariant` (GOV-02):**
  - Kiểm tra bất biến `OR-08` / `TS-019`: dù mã băm có khớp 100%, thuộc tính `upstream_identity_status` của cả từng tệp và lô kết quả luôn luôn là `"IDENTITY_UNVERIFIED"`.
  - **Kết quả:** `PASS`.

---

### 2.6. Nhóm Ranh giới Phạm vi (SCOPE-01, SCOPE-02)
- **`test_scope_01_synthetic_isolation_no_real_raw_csv_accessed` (SCOPE-01):**
  - Xác nhận đường dẫn `base_dir` trong toàn bộ test nằm trong thư mục tạm hệ thống, không chứa chuỗi `data/raw/tabular`.
  - **Kết quả:** `PASS`.
- **`test_scope_02_validator_contains_no_csv_reader_or_publication_code` (SCOPE-02):**
  - Sử dụng module `inspect` quét mã nguồn `source_validator.py`.
  - Khẳng định không chứa các lệnh đọc CSV Spark (`spark.read.csv`), không chứa xuất bản (`SafePublisher.publish`, `publish_dataset`), không chứa phân loại dòng (`classify_record`, `RowClassifier`).
  - **Kết quả:** `PASS`.

---

## 3. Tổng kết Thực thi

- Lệnh chạy: `python -m unittest tests/test_t007_source_validator.py`
- Exit Code: **0**
- Số ca kiểm thử: **21 ca kiểm thử**
- Kết quả: **21 PASS, 0 FAIL, 0 ERROR**
- Thời gian chạy: **0.123s**
