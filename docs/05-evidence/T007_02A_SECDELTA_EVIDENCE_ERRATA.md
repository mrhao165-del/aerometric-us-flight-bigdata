# T007-02A-SECURITY-DELTA Governance & Technical Evidence Errata

**Document ID:** `T007_02A_SECDELTA_EVIDENCE_ERRATA.md`  
**Date:** 2026-10-17  
**Task:** `T007-02A-SECURITY-DELTA` (Final Fail-Closed Path Validation & Source Integrity)  
**Parent Task:** `T-007` (Raw CSV Ingestion Pipeline)  
**Parent Gate:** `G4` (`PLANNED / NOT_COMPLETED`)  
**Status:** `OFFICIAL_ERRATA_ISSUED`  
**Engineer:** Senior Governance & Technical Evidence Auditor  

---

## 1. Mục đích và Quy chế Bảo toàn Hồ sơ Lịch sử

Tuân thủ chính sách quản trị repository (`AGENTS.md`), toàn bộ các báo cáo kiểm toán lịch sử và bằng chứng ban đầu (`T007_02A_*.md`, `T007_02A_CLOSURE_*.md`) được giữ nguyên vẹn tính bất biến và không bị ghi đè hay xóa bỏ.

Tài liệu này ban hành các điểm đính chính kỹ thuật chính thức (Official Errata) nhằm làm rõ và chuẩn hóa các thông tin kỹ thuật sau đợt rà soát an ninh `T007-02A-SECURITY-DELTA`.

---

## 2. Bảng Các Điểm Đính chính Kỹ thuật và Quản trị

### 2.1. Đính chính Hành vi `os.lstat` Fail-Open Trước Sửa đổi
- **Nội dung đính chính:** Trong phiên bản mã nguồn trước đợt `T007-02A-SECURITY-DELTA`, phương thức `is_symlink_or_reparse()` đã bắt ngoại lệ `OSError` phát sinh từ `os.lstat` và trả về `False`. Điều này đồng nghĩa với việc nếu một đường dẫn hoặc thư mục cha không thể đọc thuộc tính (do `PermissionError` hoặc `EIO`), hệ thống đã ngộ nhận đường dẫn đó an toàn (fail-open).
- **Hành vi chuẩn hóa mới:** Bản sửa đổi an ninh mới chuyển đổi toàn bộ cơ chế sang **fail-closed**. Mọi lỗi không thể xác định thuộc tính đường dẫn (`PermissionError`, `EIO`, ...) đều kích hoạt ngoại lệ `SourcePathSecurityError`. Chỉ duy nhất trường hợp tệp thực sự không tồn tại (`FileNotFoundError`) mới trả về `False` để phục vụ phân loại `SOURCE_MISSING`.

---

### 2.2. Đính chính Lỗ hổng Kiểm thử Phạm vi Tĩnh (SCOPE-02 Assertions)
- **Nội dung đính chính:** Trong bộ kiểm thử trước đợt sửa đổi này, ca kiểm thử `test_scope_02_validator_contains_no_csv_reader_or_publication_code` chỉ gọi `inspect.getsource()` mà hoàn toàn thiếu các câu lệnh kiểm tra (`assert`). Do đó, tỷ lệ 100% PASS trước đây chưa phản ánh năng lực kiểm chứng phạm vi tĩnh thực tế.
- **Hành vi chuẩn hóa mới:** Bài kiểm thử SCOPE-02 đã được trang bị bộ phân tích cây cú pháp trừu tượng (Python AST) hoàn chỉnh `_check_ast_for_forbidden_ingestion_or_publication()`, đồng thời bổ sung ca kiểm thử đột biến `test_scope_02_mutation_detection_fails_on_forbidden_constructs` để chứng minh bộ kiểm tra bắt giữ thành công 100% các hành vi nhập hoặc gọi hàm bị cấm.

---

### 2.3. Chuẩn hóa Danh xưng API và Cấu trúc Dữ liệu
Nhằm tránh nhầm lẫn trong các tài liệu thiết kế và hồ sơ kiểm toán:
1. **API Ghi nhận Manifest:** Phương thức chính thức trên `RunManifest` là:
   `RunManifest.record_input(path, bytes_count, sha256_hash)`
   (Hàm bao gói trên `SourceValidator` tích hợp vào manifest là `record_into_run_manifest(manifest, batch_result, allow_partial=False)`).
2. **Cấu trúc Dữ liệu Kết quả Kiểm thực:**
   - Cấp bản ghi đơn lẻ: `SourceVerificationResult`.
   - Cấp tập hợp (batch): `BatchVerificationResult` (được bí danh hóa tương thích với `SourceBatchVerificationResult`).

---

### 2.4. Khẳng định Bất biến Danh tính Dữ liệu Nguồn (`OR-08` / `TS-019`)
- **Nội dung đính chính:** Việc module `SourceValidator` tính toán thành công mã băm SHA-256 cục bộ cho các tệp CSV chỉ chứng minh tính toàn vẹn của bản sao tại chỗ (local snapshot integrity).
- **Nguyên tắc bất biến:** Tuyệt đối **không được tuyên bố** rằng mã băm cục bộ chứng minh danh tính nội dung gốc với BTS TranStats hay NOAA. Trạng thái xuất xứ của nguồn thô tiếp tục được duy trì nghiêm ngặt là:
  $$\mathbf{upstream\_identity\_status} = \mathbf{IDENTITY\_UNVERIFIED}$$
  theo đúng quy định tại `OR-08` và quyết định `FP-DEC-014`.

---

### 2.5. Phân định Rõ Ràng Phạm vi Subtask `T007-02B`
- **Nội dung đính chính:** Một số tài liệu diễn giải chưa chính xác gọi T007-02B là "CSV Reader PoC".
- **Phạm vi chuẩn tắc:** Subtask `T007-02B` được định nghĩa chính xác là: **Giai đoạn tính toán mã băm SHA-256 chỉ đọc (read-only streaming hash calculation) trên chín (9) tệp CSV thô thật 15.2 GB** để thiết lập baseline hash được phê duyệt. Subtask này hoàn toàn không phải là CSV Reader PoC hay Spark Ingestion Reader (vốn thuộc về các subtask sau như T007-03..04). Hiện tại, `T007-02B` tiếp tục giữ trạng thái **`LOCKED / PENDING_AUTHORIZATION`**.

---

### 2.6. Giới hạn Kiểm chứng Windows NTFS Junction Point
- **Nội dung đính chính:** Việc kiểm thử phát hiện Junction Point trên Windows (`FILE_ATTRIBUTE_REPARSE_POINT = 0x0400`) chỉ được xác nhận `PASS` khi có bằng chứng thực thi runtime thực tế trên hệ điều hành Windows NTFS hỗ trợ lệnh `mklink /J`. Trên các môi trường không hỗ trợ hoặc thiếu đặc quyền SeCreateSymbolicLinkPrivilege, hệ thống fallback an toàn sang cơ chế mock/lstat kiểm tra bitmask và công bố rõ giới hạn môi trường.
