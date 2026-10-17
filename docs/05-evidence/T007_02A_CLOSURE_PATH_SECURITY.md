# T007-02A Final Closure Filesystem Path Security & Reparse Point Audit

**Document ID:** `T007_02A_CLOSURE_PATH_SECURITY.md`  
**Date:** 2026-10-17  
**Task:** `T007-02A-FINAL-CLOSURE` (Fail-Closed Source Integrity Correction)  
**Parent Task:** `T-007` (Raw CSV Ingestion Pipeline)  
**Parent Gate:** `G4` (`PLANNED / NOT_COMPLETED`)  
**Status:** `AUDITED_AND_VERIFIED`  
**Engineer:** Senior Python Data Engineer & Filesystem Security Auditor  

---

## 1. Mô hình Đe dọa Hệ thống Tệp (Filesystem Threat Model)

Trong môi trường thực thi phân tích dữ liệu, các nguồn dữ liệu đầu vào phải được cô lập tuyệt đối trong ranh giới thư mục được chỉ định (`base_dir`). Các nguy cơ bảo mật hệ thống tệp bao gồm:

1. **Path Traversal (`..` escape):** Sử dụng các thành phần đường dẫn tương đối để vượt ra ngoài `base_dir`.
2. **Symlink Escape tại Tệp Lá:** Tệp đích cuối cùng là một liên kết tượng trưng trỏ tới một tệp nhạy cảm bên ngoài hoặc tệp không được kiểm soát.
3. **Symlink Thư mục Trung gian (Intermediate Directory Symlink):** Bản thân tệp lá là tệp thông thường, nhưng một hoặc nhiều thư mục cha nằm giữa `base_dir` và tệp lá là symlink trỏ ra bên ngoài.
4. **NTFS Junction Point / Reparse Point Bypass trên Windows:** Sử dụng Directory Junction (`mklink /J`) trên hệ điều hành Windows để đánh lừa các hàm kiểm tra symlink tiêu chuẩn của Python.

---

## 2. Phân tích Kỹ thuật: Python Standard Library vs Windows NTFS Junctions

### 2.1. Giới hạn của `Path.is_symlink()` và `os.path.islink()` trên Windows
Trên Windows NTFS, một Directory Junction được tạo ra thông qua cơ chế Reparse Point của hệ điều hành (`IO_REPARSE_TAG_MOUNT_POINT`). Trong phiên bản Python 3.10:
- `pathlib.Path.is_symlink()` và `os.path.islink()` chỉ kiểm tra cờ tượng trưng POSIX hoặc symlink mềm của Windows (`IO_REPARSE_TAG_SYMLINK`).
- Khi một thư mục được tạo bằng lệnh `mklink /J` (Junction Point), cả hai hàm trên đều trả về `False`.
- Nếu chỉ dựa vào `is_symlink()`, hệ thống sẽ coi Junction Point là một thư mục bình thường, tạo ra lỗ hổng bỏ sót nghiêm trọng (fail-open vulnerability).

### 2.2. Giải pháp Phát hiện Triệt để Reparse Point
Để vô hiệu hóa hoàn toàn nguy cơ này, hàm bảo mật cấp thấp `is_symlink_or_reparse(p)` được triển khai trong `source_validator.py`:

```python
def is_symlink_or_reparse(p: Path) -> bool:
    """Detect symlinks on all OSes, plus Windows NTFS junction / reparse points."""
    try:
        if p.is_symlink() or os.path.islink(str(p)):
            return True
        if sys.platform == "win32":
            st = os.lstat(str(p))
            reparse_bit = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x0400)
            if hasattr(st, "st_file_attributes") and (st.st_file_attributes & reparse_bit):
                return True
    except (OSError, ValueError):
        return True  # Fail-closed upon inspection error
    return False
```

Nguyên tắc fail-closed: Nếu lệnh `os.lstat` gặp lỗi cấp quyền hoặc I/O trong quá trình kiểm tra, hàm lập tức trả về `True` (xem như không an toàn).

---

## 3. Thuật toán Duyệt Cây Thư mục Tổ tiên (Ancestor Traversal Algorithm)

Hàm `validate_path_safety(target_path, base_dir)` được nâng cấp từ kiểm tra một điểm (single-point check) thành kiểm tra chuỗi tổ tiên đầy đủ:

```
[base_dir]
   │
   ├── [ancestor_1]       <-- is_symlink_or_reparse() check
   │      │
   │      └── [ancestor_2] <-- is_symlink_or_reparse() check
   │             │
   │             └── [target_file.csv] <-- is_symlink_or_reparse() check
```

Thuật toán thực hiện các bước sau:
1. **Kiểm tra Traversal Tương đối:** Kiểm tra toàn bộ các phần tử trong `target_path.parts`. Nếu xuất hiện `".."`, ném ngay `SourcePathSecurityError`.
2. **Kiểm tra Symlink / Junction trên Đường dẫn Ban đầu:**
   - Kiểm tra tệp đích: `is_symlink_or_reparse(target_path)`.
   - Duyệt ngược toàn bộ chuỗi thư mục cha: `curr = target_path.parent` cho đến khi chạm tới `base_dir`. Bất kỳ thành phần nào là symlink hoặc junction point đều kích hoạt `SourcePathSecurityError`.
3. **Phân giải và Kiểm tra Ranh giới Sandbox:**
   - Phân giải đường dẫn thực tế: `resolved_target = target_path.resolve()`.
   - Xác minh `resolved_target` nằm trong `resolved_base = base_dir.resolve()` bằng `resolved_target.relative_to(resolved_base)`.
4. **Kiểm tra Chuỗi Thư mục Cha Đã Phân giải:**
   - Duyệt ngược lại từ `resolved_target.parent` tới `resolved_base` để bảo đảm không có liên kết ngầm nào được thiết lập sau phân giải.

---

## 4. Bằng chứng Kiểm thử Tự động (Unit Test Evidence)

Hai bài kiểm thử đặc thù đã được bổ sung trong `tests/test_t007_source_validator.py` và chứng minh tính hiệu quả 100%:

### 4.1. Kiểm thử Symlink Thư mục Trung gian (`test_closure_fix_a03_intermediate_directory_symlink_rejected`)
- Thiết lập một cấu trúc cây thư mục trong đó thư mục cha trung gian `real_sub/` được symlink sang `link_sub/`. Tệp CSV con nằm bên trong thư mục liên kết.
- Kết quả kiểm thử: `validate_path_safety` phát hiện thành phần thư mục trung gian và ném `SourcePathSecurityError("Intermediate directory component is a symlink or reparse point: ...")`.

### 4.2. Kiểm thử Windows NTFS Junction Point (`test_closure_fix_a03_windows_junction_rejected`)
- Trên Windows, sử dụng lệnh shell `mklink /J` để tạo một Junction Point trỏ tới một thư mục bên ngoài.
- Kết quả kiểm thử:
  - `path.is_symlink()` trả về `False` (minh chứng lỗi chuẩn của Python).
  - `is_symlink_or_reparse()` phát hiện cờ `FILE_ATTRIBUTE_REPARSE_POINT (0x0400)` và trả về `True`.
  - `validate_path_safety` chặn đứng hoàn toàn và ném `SourcePathSecurityError`.

Kết luận: Hệ thống tệp được bảo vệ đa tầng, fail-closed và hoàn toàn tương thích trên cả môi trường POSIX lẫn Windows NTFS.
