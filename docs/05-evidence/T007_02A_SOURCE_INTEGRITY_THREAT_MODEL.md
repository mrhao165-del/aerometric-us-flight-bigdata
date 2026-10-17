# T007-02A Source Integrity Threat Model & Filesystem Security Analysis

**Document ID:** `T007_02A_SOURCE_INTEGRITY_THREAT_MODEL.md`  
**Date:** 2026-10-17  
**Task:** `T007-02A` (Source Inventory & Local Hash Verifier Implementation)  
**Parent Gate:** `G4` (`PLANNED / NOT_COMPLETED`)  
**Status:** `AUDITED_AND_VERIFIED`  
**Engineer:** Lead Big Data Security Engineer & Filesystem Auditor  

---

## 1. Giới thiệu và Mục tiêu

Tài liệu này phân tích mô hình đe dọa (Threat Model) đối với quá trình nạp và xác minh 9 tệp dữ liệu CSV thô (tổng quy mô 15.2 GB) trên môi trường phát triển cục bộ Windows NTFS và môi trường CI Linux POSIX.

---

## 2. Bảng Phân loại Mối đe dọa và Cơ chế Phòng thủ

| Mã Mối đe dọa | Mô tả Mối đe dọa (Threat Description) | Mức độ Rủi ro | Cơ chế Phòng thủ trong `source_validator.py` | Kiểm thử Chứng minh |
|---|---|:---:|---|:---:|
| **TM-01** | **Xung đột sửa đổi khi đang đọc (TOCTOU / Concurrent Modification):** Tệp bị tiến trình khác ghi đè hoặc cắt tỉa trong khi thuật toán băm streaming đang tính toán. | `CAO` | Thực hiện kiểm tra kép `stat_before` và `stat_after` (kiểm tra cả `st_size` và `st_mtime`). Nếu phát hiện lệch, ném `SourceChangedDuringReadError` (fail-closed). | `ERR-03` |
| **TM-02** | **Tấn công duyệt thư mục (Path Traversal):** Sử dụng các thành phần `..` để thoát khỏi thư mục dữ liệu quy định và đọc các tệp nhạy cảm trong hệ thống. | `CRITICAL` | Hàm `validate_path_safety` bóc tách từng thành phần đường dẫn, lập tức từ chối mọi chuỗi chứa `..` với `SourcePathSecurityError`. | `ERR-04` |
| **TM-03** | **Tấn công liên kết biểu trưng (Symlink / Reparse Point Escape):** Tạo liên kết symlink hoặc junction point trên Windows/POSIX trỏ tới tệp bên ngoài hoặc tệp giả mạo. | `CAO` | Kiểm tra cả `path.is_symlink()` và `os.path.islink()` trước và sau khi resolve. Mọi liên kết symlink đều bị chặn với `SourcePathSecurityError`. | `ERR-05` |
| **TM-04** | **Cạn kiệt bộ nhớ hệ thống (Out-Of-Memory DoS):** Đọc toàn bộ tệp CSV 2.06 GB (năm 2019) vào bộ nhớ RAM bằng các hàm như `read_bytes()`. | `CAO` | Bắt buộc sử dụng luồng đọc theo khối cố định `DEFAULT_HASH_CHUNK_SIZE = 1,048,576` bytes (1 MiB). Bộ nhớ RAM bị chặn ở mức $O(1)$ (< 2 MB). | `HASH-03`, `HASH-04` |
| **TM-05** | **Ngộ nhận mã băm ứng viên thành mã băm kiểm chứng (False Verification):** Tính được SHA-256 của tệp nhưng chưa có baseline phê duyệt đối chiếu, hệ thống tự động đánh dấu tệp là `VERIFIED`. | `CRITICAL` | Phân tách nghiêm ngặt trạng thái: nếu không có baseline approved, kết quả nhận `LOCAL_HASH_COMPUTED_UNAPPROVED` với `is_verified = False`. Chỉ khi khớp baseline được duyệt mới nhận `LOCAL_HASH_VERIFIED`. | `HASH-05`, `HASH-06` |
| **TM-06** | **Tuyên bố sai lệch xuất xứ nguồn BTS (Upstream Provenance Spoofing):** Đồng hóa việc tính mã băm cục bộ với việc xác nhận dữ liệu chuẩn tắc từ BTS TranStats. | `CRITICAL` | Cố định thuộc tính `upstream_identity_status = "IDENTITY_UNVERIFIED"` theo hợp đồng `OR-08` và `TS-019` trên 100% kết quả kiểm tra. | `GOV-02` |
| **TM-07** | **Lỗi phân quyền hoặc I/O bị bỏ qua (Silent Permission Failure):** Hệ điều hành từ chối quyền đọc nhưng validator bỏ qua hoặc trả về kết quả rỗng. | `TRUNG BÌNH` | Bắt giữ mọi ngoại lệ `PermissionError` và `OSError`, ném ra `SourcePermissionError` hoặc ghi nhận `SOURCE_READ_ERROR` (fail-closed). | `ERR-02` |
| **TM-08** | **Ngộ nhận `SOURCE_MANIFEST.json` thành raw hash registry:** Đọc tệp kê khai tài liệu audit để tìm mã băm của dữ liệu CSV thô. | `CAO` | Tuân thủ đính chính `DOC-F01`: Validator không dùng tệp này làm cơ sở kiểm tra mã băm CSV thô. | `GOV-01` |

---

## 3. Đánh giá Ranh giới Thực thi (Residual Risk & Invariants)

- **Giới hạn kiểm tra TOCTOU:** Cơ chế stat trước/sau phát hiện hầu hết các trường hợp thay đổi kích thước hoặc mtime, tuy nhiên không tuyên bố loại bỏ 100% mọi race condition ở cấp hạt microsecond trên các hệ thống file phân tán đặc thù. Do đó, quy trình pipeline khuyến nghị chỉ một writer được phép can thiệp tại một thời điểm (phù hợp với giới hạn `L-T009-02`).
- **Bảo toàn dữ liệu thô:** Trong toàn bộ quá trình xác thực, quyền truy cập hệ thống tệp là **READ-ONLY**; tuyệt đối không có thao tác mở tệp ở chế độ ghi (`w`, `wb`, `a`, `w+`), không tạo tệp tạm trong thư mục raw, và không thay đổi bất kỳ thuộc tính nào của dữ liệu gốc.
