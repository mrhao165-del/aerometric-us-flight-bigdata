# T007-02A Final Closure Source Code Audit & Defect Remediation Record

**Document ID:** `T007_02A_CLOSURE_SOURCE_REVIEW.md`  
**Date:** 2026-10-17  
**Task:** `T007-02A-FINAL-CLOSURE` (Fail-Closed Source Integrity Correction)  
**Parent Task:** `T-007` (Raw CSV Ingestion Pipeline)  
**Parent Gate:** `G4` (`PLANNED / NOT_COMPLETED`)  
**Status:** `AUDITED_AND_REMEDIATED`  
**Engineer:** Senior Python Data Engineer, Filesystem Security Auditor & Independent QA Reviewer  

---

## 1. Mục tiêu và Bối cảnh Kiểm toán

Trong quá trình thẩm định độc lập gói bàn giao `T007_02A_REVIEW_PACKAGE.zip`, chuyên gia kiểm toán đã phát hiện bốn (4) điểm khuyết tật an toàn hệ thống tệp và ngữ nghĩa fail-closed trong module `src/flight_pipeline/ingestion/source_validator.py`.

Nhiệm vụ `T007-02A-FINAL-CLOSURE` được kích hoạt theo phương thức **`STRICT TARGETED FIX — FAILING TESTS FIRST`** nhằm khắc phục triệt để 4 lỗi này mà không làm xáo trộn kiến trúc, không sửa đổi T-009 hay canonical schema T007-01, và tuyệt đối không truy cập 9 tệp CSV thô thật.

---

## 2. Bảng Phân tích và Khắc phục 4 Điểm Khuyết tật

### 2.1. FIX-A01 — Khuyết tật False-Positive Khi Inventory Rỗng
- **Hiện tượng lỗi:** Gọi `SourceValidator(inventory={}).verify_all_sources(compute_hash=True)` trả về:
  `all_present=True`, `all_sizes_match=True`, `all_hashes_verified=True`, `results={}`.
  Đây là lỗi ngụy biện chân lý rỗng (vacuous truth), dẫn tới nguy cơ hệ thống chứng nhận "đã xác minh toàn bộ dữ liệu" trong khi không có tệp nào được kiểm tra.
- **Biện pháp khắc phục:**
  1. `SourceValidator.__init__` lập tức kích hoạt `SourceConfigurationError("Configured inventory cannot be empty")` nếu tham số `inventory` truyền vào là từ điển rỗng `{}`.
  2. Bổ sung tham số bảo vệ tính toàn vẹn sản xuất `enforce_production_inventory: bool = False`. Khi cờ này bật, hệ thống kiểm tra bắt buộc inventory phải có đầy đủ 9 năm liên tục 2016–2024; mọi tập con 1–8 nguồn đều bị từ chối fail-closed.
  3. Phương thức `verify_all_sources()` bổ sung chốt chặn an toàn: nếu `len(self.inventory) == 0`, trả về toàn bộ cờ `False` (`all_present=False`, `all_sizes_match=False`, `all_hashes_verified=False`).

---

### 2.2. FIX-A02 — Khuyết tật Bỏ sót Cờ Batch Fail-Closed Khi Gặp Lỗi Đọc/Cấu trúc
- **Hiện tượng lỗi:** Một nguồn trong inventory trỏ tới thư mục thay vì tệp regular file, trả về `SOURCE_READ_ERROR` ở cấp bản ghi, nhưng cờ tổng hợp của batch vẫn giữ `all_present=True` và `all_sizes_match=True`.
- **Biện pháp khắc phục:**
  - Thiết kế lại máy trạng thái tổng hợp batch trong `verify_all_sources()`:
    - `all_present`: Chỉ `True` khi **toàn bộ** tệp trong inventory tồn tại dưới dạng regular file hợp lệ. Nếu có bất kỳ tệp nào rơi vào `SOURCE_MISSING`, `SOURCE_READ_ERROR`, hoặc `SOURCE_CHANGED_DURING_READ`, `all_present` lập tức chuyển thành `False`.
    - `all_sizes_match`: Chỉ `True` khi `all_present` là `True` và **toàn bộ** tệp có `actual_byte_size == expected_byte_size`.
    - `all_hashes_verified`: Chỉ `True` khi `compute_hash=True`, `all_present=True`, `all_sizes_match=True`, và **100% tệp** đạt trạng thái `LOCAL_HASH_VERIFIED`.

---

### 2.3. FIX-A03 — Khuyết tật Bỏ sót Symlink Thư mục Trung gian và NTFS Junction Point
- **Hiện tượng lỗi:**
  1. `validate_path_safety()` chỉ kiểm tra symlink trên tệp lá cuối cùng (`target_path.is_symlink()`), không kiểm tra các thư mục cha trung gian. Một symlink thư mục nằm trong `base_dir` trỏ sang thư mục khác vẫn được chấp nhận.
  2. Trên Windows NTFS, lệnh `mklink /J` tạo junction/reparse point không được hàm `islink()` hay `is_symlink()` phát hiện (trả về `False`).
- **Biện pháp khắc phục:**
  1. Xây dựng hàm kiểm tra toàn diện `is_symlink_or_reparse(path_obj)`: kết hợp `path.is_symlink()`, `os.path.islink()`, và cờ hệ thống `os.lstat(path).st_file_attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT (0x0400)`.
  2. Duyệt đệ quy toàn bộ chuỗi cây thư mục tổ tiên (`curr = path_obj.parent`) từ tệp lá ngược lên `base_dir` và từ tệp đã resolve ngược lên `base_dir`, bảo đảm **không có bất kỳ thành phần trung gian nào** là symlink hoặc NTFS junction.

---

### 2.4. FIX-A04 — Ranh giới Thất bại Khi Tích hợp Với `RunManifest`
- **Hiện tượng lỗi:** Phương thức `record_into_run_manifest()` vô điều kiện ghi các tệp bị lỗi (`SOURCE_READ_ERROR`, `SOURCE_MISSING`) vào `manifest.inputs` với `bytes=0, sha256="UNVERIFIED"`, khiến downstream ngộ nhận nguồn đã hoàn tất nạp.
- **Biện pháp khắc phục:**
  1. Thiết lập cơ chế mặc định fail-closed: `record_into_run_manifest(manifest, batch, allow_partial=False)`. Nếu batch chứa bất kỳ tệp lỗi nào, ném ngay `SourceIntegrityError` và từ chối ghi vào manifest.
  2. Khi chế độ `allow_partial=True` được cấu hình tường minh, phương thức chỉ ghi các nguồn đã vượt qua kiểm tra cấu trúc hợp lệ (`SOURCE_PRESENT_METADATA_MATCH`, `LOCAL_HASH_COMPUTED_UNAPPROVED`, `LOCAL_HASH_VERIFIED`), hoàn toàn loại bỏ nguồn lỗi khỏi `manifest.inputs` và trả về báo cáo chi tiết các nguồn bị từ chối (`rejected_details`).
