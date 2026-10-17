# T007-02A Handoff Errata — Technical Specification Corrections

**Document ID:** `T007_02A_HANDOFF_ERRATA.md`  
**Date:** 2026-10-17  
**Parent Task:** `T-007` (Raw CSV Ingestion Pipeline)  
**Subtask:** `T007-02A` (Source Inventory & Local Hash Verifier Implementation)  
**Status:** `OFFICIALLY_RECORDED`  
**Auditor / Engineer:** Senior Python Data Engineer & Data Provenance Auditor  

---

## 1. Mục đích và Phạm vi

Tài liệu này ghi nhận chính thức hai điểm hiệu chỉnh kỹ thuật (errata) đã được phát hiện trong quá trình kiểm toán độc lập các tài liệu chuyển giao thiết kế T-007 và chuẩn bị triển khai Subtask `T007-02A`.

Việc ban hành phụ lục đính chính này bảo đảm việc triển khai mã nguồn module `src/flight_pipeline/ingestion/source_validator.py` và bộ kiểm thử `tests/test_t007_source_validator.py` hoàn toàn ăn khớp với hiện trạng thực tế của codebase, loại bỏ các ngộ nhận kỹ thuật trước khi lập mã.

---

## 2. Danh mục Chi tiết Các Điểm Đính chính

### 2.1. DOC-F01 — Phạm vi và Ranh giới của `SOURCE_MANIFEST.json`

- **Mô tả sai lệch trong giả định ban đầu:** Một số phác thảo thiết kế sơ bộ ngộ nhận tệp `docs/05-evidence/inputs/SOURCE_MANIFEST.json` chứa mã băm chuẩn (golden SHA-256 checksums) của 9 tệp CSV dữ liệu thô hàng không (`data/raw/tabular/{year}/flight_with_weather_{year}.csv`).
- **Hiện trạng thực tế đã kiểm toán:**
  - Tệp `docs/05-evidence/inputs/SOURCE_MANIFEST.json` được thiết lập tại Gate G1 (ngày 2026-10-13) nhằm quản lý 13 tài liệu kiểm toán đầu vào (bao gồm 4 tệp markdown kiểm toán và 9 tệp `schema_YYYY.json`).
  - Dòng 3 của tệp ghi rõ tuyên bố pháp lý kỹ thuật:
    > `"statement": "SHA-256 verifies snapshots of user-provided audit documents; NOT raw CSV files."`
- **Quy tắc bắt buộc đối với Source Validator:**
  - Tuyệt đối **không** được lập trình module `source_validator.py` đọc tệp `SOURCE_MANIFEST.json` như một bảng đăng ký mã băm của 9 tệp CSV thô.
  - Mã băm của 9 tệp CSV thô cục bộ chưa từng được tính toán hay phê duyệt ở G1–G3. Việc tính candidate SHA-256 baseline cho 9 tệp CSV thô được phân tách nghiêm ngặt sang Subtask `T007-02B` (yêu cầu lệnh ủy quyền riêng từ Project Lead con người).
  - Source Validator trong `T007-02A` chỉ hỗ trợ nạp cấu hình baseline mã băm thông qua cơ chế Dependency Injection (tham số `approved_baseline_hashes: Optional[Dict[int, str]] = None`). Khi tham số này bằng `None` hoặc vắng mặt năm kiểm tra, trạng thái băm phải giữ ở mức `LOCAL_HASH_COMPUTED_UNAPPROVED` hoặc `BASELINE_PENDING_APPROVAL`, cấm tự động nâng lên `LOCAL_HASH_VERIFIED`.

---

### 2.2. DOC-F02 — Chữ ký API Thực tế của `RunManifest` (T-009)

- **Mô tả sai lệch trong giả định ban đầu:** Một số tài liệu ghi chú thiết kế đề cập phương thức tích hợp `RunManifest.add_input(...)` để ghi nhận nguồn dữ liệu đầu vào.
- **Hiện trạng thực tế trong mã nguồn T-009:**
  - Kiểm tra trực tiếp tệp `src/flight_pipeline/utils/run_manifest.py` (dòng 155–161) xác nhận chữ ký chính thức của phương thức là:
    ```python
    def record_input(self, path: str, bytes_count: int, sha256_hash: Optional[str] = None) -> None:
        """Record an audited input source file."""
        self.inputs.append({
            "path": path,
            "bytes": bytes_count,
            "sha256": sha256_hash or "UNVERIFIED",
        })
    ```
  - Trong toàn bộ codebase hoàn toàn **không tồn tại** phương thức `RunManifest.add_input()`.
- **Quy tắc bắt buộc đối với Source Validator:**
  - Mọi adapter, helper hoặc lời gọi tích hợp từ `source_validator.py` sang `RunManifest` phải gọi đúng phương thức `record_input(path, bytes_count, sha256_hash)`.
  - Giá trị truyền vào `sha256_hash` chỉ được xem là verified khi đã đối chiếu khớp với baseline được phê duyệt (`LOCAL_HASH_VERIFIED`). Trường hợp candidate hash chưa được phê duyệt (`LOCAL_HASH_COMPUTED_UNAPPROVED`), giá trị có thể truyền `None` (để `RunManifest` ghi nhận `"UNVERIFIED"`) hoặc truyền candidate hash kèm ghi chú rõ trong metadata kết quả rằng candidate hash đang chờ phê duyệt.

---

## 3. Kết luận và Ranh giới Thực thi

- Bản phụ lục đính chính `T007_02A_HANDOFF_ERRATA.md` này có hiệu lực tức thì cho toàn bộ quá trình phát triển Subtask `T007-02A`.
- Các tài liệu lịch sử trước đây không bị ghi đè để bảo tồn tính toàn vẹn của chuỗi kiểm toán; phụ lục này đóng vai trò hướng dẫn kỹ thuật có quyền lực cao nhất đối với module `source_validator.py`.
