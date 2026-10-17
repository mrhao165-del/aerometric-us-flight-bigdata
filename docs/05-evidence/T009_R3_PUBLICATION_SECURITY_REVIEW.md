# T009-R3: PUBLICATION SECURITY & INTEGRITY REVIEW

**Task ID:** `T-009` (Remediation R3)  
**Gate:** `G4`  
**Auditor:** Storage Systems & Security Auditor  
**Execution Mode:** `CONTROLLED TARGETED REMEDIATION`  
**Date:** 2026-10-17  
**Status:** `SECURITY_POSTURE_HARDENED`  

---

## 1. Ma Trận Đánh Giá Các Lớp Phòng Vệ Xuất Bản (Defense-in-Depth Matrix)

Sau đợt sửa đổi R3, lớp [`SafePublisher`](../../src/flight_pipeline/storage/publication.py#L74-L280) thiết lập 5 lớp phòng vệ tuần tự:

| Lớp Phòng Vệ | Cơ Chế Kiểm Soát | Khiếm Khuyết Ngăn Chặn | Trạng Thái Thất Bại |
|---|---|---|:---:|
| **Lớp 0: Path Confinement** | Kiểm tra Regex, cấm ký tự phân cách, xác thực `target.parent == runs_root` | F-03 (Path Traversal, Escape) | `FAILED_INVALID_RUN_ID` |
| **Lớp 1: Staging & Content** | Kiểm tra thư mục, kiểm tra magic bytes `PAR1` đầu/cuối của file Parquet | F-02 (Fake Parquet, Empty) | `FAILED_STAGING_CONTENT_INVALID` |
| **Lớp 2: Row Accounting** | Kiểm tra bất biến DC-11 và số nguyên không âm | F-04 (Negative row counts) | `ACCOUNTING_UNVERIFIED` |
| **Lớp 3: Immutability** | Kiểm tra thư mục đích chưa từng tồn tại | Ghi đè phiên bản lịch sử | `FAILED_VERSION_EXISTS` |
| **Lớp 4: Byte Integrity** | Kiểm tra khớp 100% kích thước byte và SHA-256 giữa staging và promoted | F-02 (Corrupted file copy) | `FAILED_COMPLETENESS` |
| **Lớp 5 & 6: Atomic Pointer** | Cập nhật và rollback con trỏ bằng `os.replace` nguyên tử trên NTFS | F-05 (Partial write, file lock) | `FAILED_POINTER_LOCK` / `FAILED_POINTER_VERIFICATION` |

---

## 2. Giả Định Đơn Tiến Trình Ghi (Single-Writer Operational Restriction)

Kiểm toán viên xác lập rõ ràng:
- `SafePublisher` được thiết kế cho kiến trúc xử lý batch cục bộ (local single-node pipeline) với giả định **Single-Writer** tại một thời điểm.
- Nếu có hai quy trình xuất bản chạy song song với **cùng một `run_id`**, Lớp 3 (`FAILED_VERSION_EXISTS`) và `shutil.copytree(dirs_exist_ok=False)` sẽ từ chối quy trình đến sau, bảo vệ tính toàn vẹn dữ liệu.
- Nếu có hai quy trình xuất bản chạy song song với **hai `run_id` khác nhau**, quy trình nào hoàn tất Bước 5 sau cùng sẽ ghi đè con trỏ `latest_run_id.txt`. Do đó, trong môi trường sản xuất, việc kích hoạt pipeline phải được điều phối tuần tự bởi scheduler hoặc job manager.

---

## 3. Bảo Tồn Dấu Vết Sự Cố (Forensic Evidence Preservation)

- Khi bất kỳ bước nào từ Bước 1 đến Bước 6 thất bại:
  - Thư mục `staging` hoàn toàn được giữ nguyên để phục vụ điều tra lỗi.
  - Thư mục phân bản lỗi (nếu đã tạo ở Bước 3) không bị xóa phá hủy, bảo lưu nguyên trạng vết copy để đối soát.
  - Con trỏ `latest_run_id.txt` được bảo vệ nguyên vẹn trỏ về phiên bản hợp lệ trước đó.
