# G6_POINTER_VERIFICATION_DESIGN_AND_TEST_REPORT.md
# Báo Cáo Thiết Kế Kỹ Thuật và Kết Quả Kiểm Thử Công Cụ Kiểm Tra Con Trỏ Xuất Bản (GAP-01)

**Dự án:** US Flight Performance Analysis 2016–2024  
**Hạng mục kỹ thuật:** GAP-01 — Staging/Curated Publication Pointer Verification  
**Công cụ triển khai:** `tools/qa/verify_staging_pointer.py`  
**Bộ kiểm thử:** `tests/test_verify_staging_pointer.py`  
**Gate quản lý:** Gate G5 = IN_PROGRESS, Gate G6 = NOT_STARTED / BLOCKED  
**Tác giả:** Principal Big Data Engineer, Systems Concurrency Specialist, Independent QA Reviewer  
**Thời điểm lập:** 2026-10-20  

---

## 1. MỤC TIÊU VÀ NGUYÊN TẮC BẢO VỆ DỮ LIỆU

Nhằm khắc phục khoảng cách kiểm toán **GAP-01** (công cụ `verify_staging_pointer.py` chưa từng tồn tại độc lập trong repository), công cụ này được thiết kế và triển khai nhằm phục vụ công tác rà soát trạng thái con trỏ xuất bản trước, trong và sau các phiên thực thi pipeline.

### Nguyên tắc an toàn bất biến (Critical Safety Invariants)
1. **Chế độ chỉ đọc 100% (Strictly Read-Only):**
   - Công cụ tuyệt đối không thực hiện bất kỳ hành vi ghi, sửa, xóa, di chuyển, tạo tệp hoặc thư mục nào trên hệ thống tệp.
   - Không thay đổi timestamp (mtime), kích thước, hoặc quyền truy cập của tệp con trỏ hay tệp dữ liệu.
2. **Không phụ thuộc vào các API không tồn tại:**
   - Không gọi `SingleWriterLock.verify_pointer_integrity()` (phương thức này không tồn tại).
   - Không gọi `SingleWriterLock.is_locked()` (phương thức này không tồn tại).
   - Sử dụng trực tiếp API chính thống `SafePublisher.get_current_pointer()` từ module `flight_pipeline.storage.publication`.
3. **Chống tấn công duyệt đường dẫn (Anti-Path-Traversal):**
   - Mọi giá trị đọc được từ con trỏ đều phải được xác thực thông qua biểu thức chính quy `RUN_ID_REGEX` và hàm `validate_run_id()`.
   - Ngăn chặn ngay lập tức các ký tự nguy hiểm như `..`, `/`, `\`, `:` để không bao giờ thoát ra ngoài thư mục `curated/runs/`.
4. **Phát hiện con trỏ lơ lửng (Dangling Pointer Detection):**
   - Xác minh sự tồn tại vật lý của thư mục đích `curated/runs/{run_id}`.
   - Nếu tệp con trỏ trỏ đến một `run_id` không có thư mục tương ứng, báo lỗi `DANGLING_POINTER_TARGET_MISSING`.
5. **Kiểm tra tính toàn vẹn của tệp Parquet và Manifest:**
   - Quét các tệp `.parquet` và kiểm tra 4 byte ma thuật `b'PAR1'` ở đầu và cuối tệp thông qua `is_valid_parquet_file()`.
   - Nếu có tệp manifest `run_manifest.json`, kiểm tra tính hợp lệ của cấu trúc JSON và so khớp trường `manifest["run_id"]` với giá trị của con trỏ.

---

## 2. KIẾN TRÚC VÀ GIAO DIỆN LẬP TRÌNH (API CONTRACT)

### 2.1. Cấu trúc dữ liệu kết quả (`PointerVerificationResult`)

```python
@dataclass
class PointerVerificationResult:
    success: bool
    status: str
    base_dir: str
    pointer_file: str
    pointer_value: Optional[str] = None
    target_dir: Optional[str] = None
    parquet_files_found: int = 0
    valid_parquet_files: int = 0
    manifest_found: bool = False
    manifest_path: Optional[str] = None
    manifest_run_id: Optional[str] = None
    error_message: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)
```

### 2.2. Bảng mã trạng thái trả về (Status Codes)

| Mã trạng thái | `success` | Ý nghĩa kỹ thuật |
| :--- | :---: | :--- |
| `VALID_POINTER` | `True` | Con trỏ hợp lệ, thư mục đích tồn tại, chứa Parquet hợp lệ và manifest trùng khớp. |
| `UNINITIALIZED_POINTER_ALLOWED` | `True` | Con trỏ chưa khởi tạo nhưng cờ `--allow-uninitialized` được bật (trạng thái ban đầu hợp lệ). |
| `MISSING_POINTER_FILE` | `False` | Tệp con trỏ `latest_run_id.txt` không tồn tại trên đĩa. |
| `POINTER_NOT_A_FILE` | `False` | Đường dẫn con trỏ tồn tại nhưng là thư mục hoặc liên kết hỏng. |
| `POINTER_READ_IO_ERROR` | `False` | Lỗi đọc tệp do sự cố I/O hoặc xung đột khóa NTFS kéo dài quá số lần retry. |
| `EMPTY_POINTER_FILE` | `False` | Tệp con trỏ rỗng hoặc chỉ chứa khoảng trắng. |
| `PATH_TRAVERSAL_DETECTED` | `False` | Giá trị con trỏ chứa ký tự nguy hiểm (`..`, `/`, `\`, `:`). |
| `INVALID_RUN_ID_FORMAT` | `False` | Giá trị con trỏ không khớp biểu thức chính quy chuẩn. |
| `DANGLING_POINTER_TARGET_MISSING` | `False` | Thư mục phiên bản tương ứng với con trỏ không tồn tại trong `curated/runs/`. |
| `TARGET_NOT_A_DIRECTORY` | `False` | Thư mục phiên bản tồn tại nhưng không phải là thư mục hợp lệ. |
| `NO_PARQUET_FILES_FOUND` | `False` | Thư mục phiên bản không chứa bất kỳ tệp dữ liệu `.parquet` nào. |
| `CORRUPT_PARQUET_DETECTED` | `False` | Phát hiện tệp Parquet hỏng header/footer hoặc không thể phân tích metadata. |
| `MISSING_RUN_MANIFEST` | `False` | Thiếu tệp `run_manifest.json` khi được yêu cầu bắt buộc (`require_manifest=True`). |
| `CORRUPT_MANIFEST_FILE` | `False` | Tệp manifest bị hỏng cú pháp JSON. |
| `MANIFEST_RUN_ID_MISMATCH` | `False` | Giá trị `run_id` trong manifest không khớp với giá trị ghi trong tệp con trỏ. |

---

## 3. KẾT QUẢ KIỂM THỬ THỰC TẾ TRÊN BỘ DỮ LIỆU KIỂM ĐỊNH

Bộ kiểm thử `tests/test_verify_staging_pointer.py` bao gồm 12 ca kiểm thử độc lập bao phủ toàn diện:

```
tests/test_verify_staging_pointer.py::TestVerifyStagingPointer::test_positive_valid_pointer_with_manifest_and_parquet ... ok
tests/test_verify_staging_pointer.py::TestVerifyStagingPointer::test_uninitialized_state_allowed ... ok
tests/test_verify_staging_pointer.py::TestVerifyStagingPointer::test_missing_pointer_file_fails_by_default ... ok
tests/test_verify_staging_pointer.py::TestVerifyStagingPointer::test_empty_pointer_file_fails ... ok
tests/test_verify_staging_pointer.py::TestVerifyStagingPointer::test_path_traversal_detection ... ok
tests/test_verify_staging_pointer.py::TestVerifyStagingPointer::test_dangling_pointer_detected ... ok
tests/test_verify_staging_pointer.py::TestVerifyStagingPointer::test_corrupt_parquet_detected ... ok
tests/test_verify_staging_pointer.py::TestVerifyStagingPointer::test_no_parquet_files_found_when_required ... ok
tests/test_verify_staging_pointer.py::TestVerifyStagingPointer::test_missing_required_manifest ... ok
tests/test_verify_staging_pointer.py::TestVerifyStagingPointer::test_corrupt_manifest_json ... ok
tests/test_verify_staging_pointer.py::TestVerifyStagingPointer::test_manifest_run_id_mismatch ... ok
tests/test_verify_staging_pointer.py::TestVerifyStagingPointer::test_verifier_is_strictly_read_only ... ok

----------------------------------------------------------------------
Ran 12 tests in 1.539s

OK
```

### Chi tiết kiểm tra tính bất biến (`test_verifier_is_strictly_read_only`)
Ca kiểm thử ghi nhận chính xác `st_mtime_ns` và `st_size` của tệp con trỏ, tệp Parquet và tệp manifest trước khi chạy kiểm chứng. Sau khi chạy, toàn bộ các chỉ số được đối soát lại và đạt độ trùng khớp $100\%$, chứng minh công cụ hoàn toàn không tạo ra bất kỳ tác dụng phụ (side-effect) nào trên hệ thống tệp.

---

## 4. KẾT LUẬN

Công cụ `tools/qa/verify_staging_pointer.py` đã hoàn tất thiết kế, triển khai và kiểm chứng, giải quyết triệt để khiếm khuyết GAP-01. Công cụ sẵn sàng phục vụ cho Gate G6 để kiểm soát an toàn con trỏ xuất bản của từng năm dữ liệu.
