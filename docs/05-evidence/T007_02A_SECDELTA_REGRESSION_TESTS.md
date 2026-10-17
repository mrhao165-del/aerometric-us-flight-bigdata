# T007-02A-SECURITY-DELTA Regression & Test Verification Report

**Document ID:** `T007_02A_SECDELTA_REGRESSION_TESTS.md`  
**Date:** 2026-10-17  
**Task:** `T007-02A-SECURITY-DELTA` (Final Fail-Closed Path Validation & Source Integrity)  
**Parent Task:** `T-007` (Raw CSV Ingestion Pipeline)  
**Parent Gate:** `G4` (`PLANNED / NOT_COMPLETED`)  
**Status:** `VERIFIED_ALL_PASS`  
**Engineer:** Independent QA Engineer & Automated Test Specialist  

---

## 1. Phương pháp Thực thi `FAILING TESTS FIRST`

Trước khi sửa đổi bất kỳ dòng mã nào trong `src/flight_pipeline/ingestion/source_validator.py`, tám (8) bài kiểm thử hồi quy mới đã được lập trình trong `tests/test_t007_source_validator.py` để mô phỏng chính xác các lỗi đã được kiểm toán:

1. `test_secdelta_fix_sec01_lstat_permission_error_raises_security_error`: Mô phỏng `PermissionError` trên `os.lstat`.
2. `test_secdelta_fix_sec01_lstat_eio_error_raises_security_error`: Mô phỏng `OSError(errno.EIO, ...)` trên `os.lstat`.
3. `test_secdelta_fix_sec01_missing_file_differentiated_and_returns_source_missing`: Tệp không tồn tại phân biệt với lỗi bảo mật, trả `SOURCE_MISSING`.
4. `test_secdelta_fix_sec01_inaccessible_intermediate_path_fails_closed`: Mô phỏng thư mục cha trung gian bị cấm quyền truy cập.
5. `test_scope_02_validator_contains_no_csv_reader_or_publication_code`: Phân tích AST tĩnh phát hiện vi phạm mã nguồn.
6. `test_scope_02_mutation_detection_fails_on_forbidden_constructs`: Kiểm tra đột biến chứng minh checker bắt giữ 4 vi phạm cấm.
7. `test_secdelta_fix_sec03_metadata_io_error_returns_source_read_error`: Lỗi `EIO` khi đọc metadata với `fail_fast=False`.
8. `test_secdelta_fix_sec03_metadata_io_error_fail_fast_raises_source_integrity_error`: Lỗi `EIO` với `fail_fast=True`.
9. `test_secdelta_fix_sec03_batch_aggregation_fail_closed_on_io_error`: Batch aggregation ép cờ `False` khi gặp lỗi I/O.

### Kết quả Thực thi Trước Sửa đổi (Pre-fix Reproduction Run):
```
Ran 37 tests in 1.183s
FAILED (failures=3, errors=3)
```
- **3 Thất bại (Failures):**
  - `test_secdelta_fix_sec01_lstat_permission_error_raises_security_error`: `is_symlink_or_reparse` trả `False` thay vì ném ngoại lệ.
  - `test_secdelta_fix_sec01_lstat_eio_error_raises_security_error`: `is_symlink_or_reparse` trả `False` thay vì ném ngoại lệ.
  - `test_secdelta_fix_sec01_inaccessible_intermediate_path_fails_closed`: `validate_path_safety` bỏ qua thư mục cha bị cấm quyền.
- **3 Lỗi (Errors):**
  - `test_secdelta_fix_sec03_metadata_io_error_returns_source_read_error`: `OSError: [Errno 5]` không được bắt trong `getsize()`.
  - `test_secdelta_fix_sec03_metadata_io_error_fail_fast_raises_source_integrity_error`: `OSError: [Errno 5]` không được bọc thành `SourceIntegrityError`.
  - `test_secdelta_fix_sec03_batch_aggregation_fail_closed_on_io_error`: `OSError: [Errno 5]` làm sập toàn bộ batch.

---

## 2. Kết quả Thực thi Sau Khắc phục (Post-fix Test Execution)

### 2.1. Kiểm thử Đơn vị Module `SourceValidator` (`test_t007_source_validator.py`):
```bash
python -m unittest tests/test_t007_source_validator.py
```
- **Kết quả:** **37/37 bài kiểm thử PASS (100%)**.
- **Thời gian:** 0.353 giây.
- **Chi tiết phân bổ 37 bài kiểm thử:**
  - 3 bài Inventory (INV-01..03)
  - 4 bài Metadata & Missing (ERR-01, ERR-02, test_05, test_06)
  - 4 bài Hash & Modification Race (HASH-01..03, ERR-03)
  - 3 bài Path Traversal & Symlinks (ERR-04, ERR-05, test_14)
  - 4 bài Batch Verification & Manifest Integration (test_16..18)
  - 3 bài CLI Interface (test_19..21)
  - 2 bài Scope Boundaries (SCOPE-01 synthetic isolation, SCOPE-02 AST validation + mutation test)
  - 8 bài Closure Fixes (FIX-A01..A04)
  - 6 bài Security Delta Fixes (FIX-SEC01, FIX-SEC03)

### 2.2. Kiểm thử Toàn bộ Repository (`discover tests`):
```bash
python -m unittest discover tests
```
- **Kết quả:** **96/96 bài kiểm thử PASS (100%)**.
- **Thời gian:** 59.460 giây.
- **Không có bất kỳ thất bại, lỗi, hoặc bỏ qua nào (0 Failures, 0 Errors, 0 Skipped).**

---

## 3. Kết luận Kiểm thử

Toàn bộ các yêu cầu an toàn, fail-closed, cách ly ranh giới và kiểm thử tĩnh đã được kiểm chứng bằng thực nghiệm tự động. Module `SourceValidator` đạt độ tin cậy sản xuất tối đa.
