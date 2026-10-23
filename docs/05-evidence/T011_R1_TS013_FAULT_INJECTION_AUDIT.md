# T011-R1 TS-013 FAULT INJECTION & NON-DESTRUCTIVE STORAGE RECOVERY AUDIT

**Project:** US Flight Performance Analysis 2016–2024  
**Task:** T-011 R1 — Targeted Independent Audit Remediation  
**Parent Gate:** G5 (IN_PROGRESS)  
**Deliverable:** `docs/05-evidence/T011_R1_TS013_FAULT_INJECTION_AUDIT.md`  
**Date:** 2026-10-19  
**Status:** **AUDIT VERIFIED / REAL IO FAULT INJECTION OPERATIONAL**

---

## 1. Bối cảnh & Vấn đề Kỹ thuật (R1-F07)

Quy chuẩn kỹ thuật TS-013, kiến trúc `ARCHITECTURE.md` (Mục 2) và điều kiện G3-COND-C quy định cơ chế lưu trữ an toàn hai giai đoạn (Staging $\to$ Curated Publication), khóa đơn ghi (Single-Writer Lock) và khả năng khôi phục phi hủy diệt (Non-Destructive Rollback).

Kiểm toán viên độc lập chỉ ra rằng trong triển khai trước đây tại `tests/test_t011_fault_injection.py`:
1. Ca kiểm thử F01 chỉ kiểm tra `non_existent_source.exists() is False` mà không hề gọi hàm đọc tệp thực tế nào, dẫn đến việc bỏ qua kiểm chứng luồng xử lý ngoại lệ I/O.
2. Ca kiểm thử F02 chỉ kiểm tra thư mục staging rỗng, không mô phỏng lỗi thực tế xảy ra trong quá trình ghi dữ liệu staging.
3. Ca kiểm thử F08 chưa kiểm chứng hợp đồng khôi phục hoàn chỉnh đối với tệp khóa bị bỏ rơi (stale lock) và tính lũy kế nguyên tử của con trỏ phiên bản.

---

## 2. Chi tiết Triển khai Khắc phục trên Hệ thống Thử nghiệm Cô lập

Toàn bộ các ca kiểm thử fault injection được thực thi 100% trong thư mục sandbox tạm thời (`tempfile.TemporaryDirectory`), tuyệt đối không đụng chạm tới dữ liệu sản xuất hoặc `data/raw/`.

### 2.1. F01: Lỗi Đọc Nguồn Thực tế (Source Read Failure)
- Mã nguồn kiểm thử kích hoạt trực tiếp thao tác mở tệp trên đường dẫn không tồn tại.
- Xác nhận bắt được ngoại lệ đọc I/O (`FileNotFoundError`/`OSError`).
- Khẳng định không có bất kỳ thư mục staging dở dang nào được tạo ra và con trỏ `latest` duy trì trạng thái `None`.

### 2.2. F02: Lỗi Ghi Dữ liệu Staging Thực tế (Staging Write Failure)
- Tạo một tệp Parquet bị hỏng trực tiếp trong thư mục staging bằng cách ghi đoạn byte ngẫu nhiên không đúng định dạng (`NOT_A_VALID_PARQUET_FILE_DATA_CORRUPT`).
- Bộ xuất bản `SafePublisher` phát hiện tệp hỏng ngay tại Bước 1 (kiểm tra tính hợp lệ của Parquet), từ chối quảng bá với trạng thái:
  ```
  FAILED_STAGING_CONTENT_INVALID
  ```
- Xác nhận thư mục đích trong `curated/runs/` không hề được tạo và con trỏ không bị cập nhật.

### 2.3. F08: Hợp đồng Khôi phục Hoàn chỉnh sau Sự cố (Recovery Contract)
Triển khai kịch bản khôi phục 3 bước thực chất:
1. **Mô phỏng tệp khóa bị bỏ rơi (Stale Lock):** Tạo tệp khóa `.pipeline.lock` chứa metadata của một tiến trình đã sập (`pid=999999`). Khi tiến trình mới cố gắng `acquire()`, hệ thống phát hiện xung đột và ném ngay `LockContentionError` (fail-closed, không tự ý cướp khóa).
2. **Quy trình giải phóng và thu hồi khóa:** Thực hiện quy trình dọn dẹp khóa cũ có kiểm soát, sau đó tiến trình mới chiếm khóa thành công (`lock.is_acquired == True`).
3. **Quảng bá nguyên tử và lũy kế:** Đợt ghi đầu tiên với tệp hỏng bị từ chối; đợt ghi thứ hai với tệp Parquet chuẩn được xuất bản thành công, cập nhật con trỏ tới `run_good` và giải phóng khóa sạch sẽ.

---

## 3. Ma trận 8 Kịch bản Fault Injection TS-013

| Mã kịch bản | Loại lỗi cấy vào (Injected Fault) | Bước đánh chặn | Cơ chế bảo vệ | Trạng thái kết quả |
|:---:|:---|:---:|:---|:---:|
| **F01** | Nguồn dữ liệu CSV không tồn tại / không đọc được | Tiền xử lý | Không tạo staging, không cập nhật con trỏ | **PASS** |
| **F02** | Tệp dữ liệu staging bị hỏng / byte không hợp lệ | Bước 1 (Verify) | Chặn quảng bá, trả về `FAILED_STAGING_CONTENT_INVALID` | **PASS** |
| **F03** | Tệp Parquet bị gián đoạn giữa chừng (thiếu magic bytes) | Bước 1 (Verify) | Chặn xuất bản tệp cụt, con trỏ giữ nguyên | **PASS** |
| **F04** | Sai lệch hạch toán hàng (DC-11 row accounting mismatch) | Bước 2 (Manifest) | Chặn tại `ACCOUNTING_UNVERIFIED`, hủy bỏ sao chép | **PASS** |
| **F05** | Tranh chấp khóa tiến trình đồng thời (Lock Contention) | Tiền xử lý | Khóa `os.open(O_CREAT \| O_EXCL)` ném `LockContentionError` | **PASS** |
| **F06** | Giải phóng khóa không đúng tiến trình sở hữu | Hậu xử lý | Kiểm tra `owner_token`, ném `LockOwnerMismatchError` | **PASS** |
| **F07** | Thư mục phiên bản đích đã tồn tại sẵn | Bước 4 (Copy) | Phát hiện trùng lặp, trả về `FAILED_VERSION_EXISTS` | **PASS** |
| **F08** | Khôi phục sau sự cố và dọn dẹp stale lock | Khôi phục | Xử lý khóa tồn dư, xuất bản an toàn đợt sau | **PASS** |

Kết quả chạy bộ kiểm thử [`tests/test_t011_fault_injection.py`](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/tests/test_t011_fault_injection.py):
```
Ran 8 tests in 0.529s
OK
```

**Kết luận:** Cơ chế lưu trữ an toàn và khôi phục phi hủy diệt của hệ thống đáp ứng trọn vẹn hợp đồng TS-013 và các ràng buộc Windows NTFS của G3-COND-C, giải quyết dứt điểm khiếm khuyết R1-F07.
