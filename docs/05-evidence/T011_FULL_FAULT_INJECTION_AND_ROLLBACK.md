# T011_FULL_FAULT_INJECTION_AND_ROLLBACK — BÁO CÁO THỰC NGHIỆM BƠM LỖI TS-013 VÀ PHỤC HỒI PHI PHÁ HỦY

- **Mã nhiệm vụ:** `T-011` (Gate G5: KPI Sample Smoke, BTS Parity, TS-008, TS-013 & Review Packaging)
- **Gate:** `G5` (IN_PROGRESS)
- **Thời điểm kiểm toán:** 2026-10-18T20:53:30+07:00
- **Tiêu chuẩn tuân thủ:** [`AGENTS.md`](../../AGENTS.md), [`ARCHITECTURE.md`](../02-design/ARCHITECTURE.md) Section 2, [`ROLLBACK_PLAN.md`](../03-quality/ROLLBACK_PLAN.md), [`TEST_PLAN.md`](../03-quality/TEST_PLAN.md) (TS-013), G3-COND-C.
- **Trạng thái Gate 3:** **PASS (All 8 Fault Scenarios Intercepted & Non-Destructive Rollback Verified)**

---

## 1. NGUYÊN TẮC AN TOÀN VÀ CƠ CHẾ CÔ LẬP SANDBOX

Toàn bộ các phép thử bơm lỗi chủ đích (fault injection) và mô phỏng sự cố được thực hiện **100% trong môi trường sandbox tạm thời cô lập**:
- Sử dụng fixture `tempfile.TemporaryDirectory(prefix="ts013_sandbox_")` độc lập.
- **Tuyệt đối không can thiệp, không ghi đè, không xóa bất kỳ byte nào** trong thư mục dữ liệu thô `data/raw/` hoặc các tệp Parquet staging/curated đã được nghiệm thu của T-010.
- Con trỏ xuất bản chính thức của kho lưu trữ hoàn toàn được bảo vệ bất biến.

---

## 2. MA TRẬN 8 KỊCH BẢN BƠM LỖI (F01..F08) VÀ KẾT QUẢ KIỂM CHỨNG

| Kịch bản | Tên kịch bản & Điểm bơm lỗi | Cơ chế xử lý an toàn của hệ thống | Kết quả quan sát | Trạng thái |
|:---:|---|---|---|:---:|
| **F01** | *Source read failure* (Đường dẫn nguồn không tồn tại hoặc lỗi đọc) | Pipeline hủy bỏ ngay lập tức, không tạo thư mục staging dở dang, không cập nhật con trỏ. | Con trỏ vẫn giữ nguyên `None` (hoặc con trỏ cũ); không có tệp rác. | **PASS** |
| **F02** | *Staging write failure* (Lỗi I/O khi ghi staging, thư mục rỗng) | `SafePublisher` phát hiện thư mục staging không có tệp nào $\implies$ Trả về `FAILED_STAGING_EMPTY`, dừng trước khi thăng cấp. | Thư mục curated runs không bị tạo dở dang; con trỏ không đổi. | **PASS** |
| **F03** | *Interrupted Parquet write* (Tệp Parquet bị cắt cụt giữa chừng do mất điện/đầy đĩa) | Step 1 validation (`is_valid_parquet_file`) quét magic bytes và metadata Thrift $\implies$ Phát hiện tệp hỏng, trả về `FAILED_STAGING_CONTENT_INVALID`. | Hủy bỏ tại Step 1; không chuyển dữ liệu hỏng sang curated; con trỏ không đổi. | **PASS** |
| **F04** | *Manifest accounting mismatch* (Mất cân bằng hạch toán dòng DC-11) | Step 2 balance check: So sánh `raw != accepted + quarantined + rejected` $\implies$ Phát hiện sai lệch (960 != 1000), trả về `ACCOUNTING_UNVERIFIED`. | Hủy bỏ tại Step 2; không thăng cấp dữ liệu mất cân bằng; con trỏ không đổi. | **PASS** |
| **F05** | *Single-writer lock contention* (Tranh chấp ghi đồng thời) | `SingleWriterLock` sử dụng Win32 atomic file creation (`O_CREAT \| O_EXCL`) $\implies$ Tiến trình thứ hai bị ném ngoại lệ `LockContentionError`. | Tiến trình 2 dừng an toàn (fail-closed); tiến trình 1 hoàn tất và giải phóng khóa sạch sẽ. | **PASS** |
| **F06** | *Pointer switching failure & rollback* (Lỗi khi cập nhật con trỏ `latest_run_id`) | Step 5 giả lập lỗi chuyển con trỏ $\implies$ Step 6 kích hoạt phục hồi phi phá hủy (non-destructive rollback), khôi phục con trỏ về bản chạy hợp lệ trước đó (`run_a`). | Bản chạy cũ `run_a` vẫn nguyên vẹn 100% và đọc được; con trỏ an toàn trỏ về `run_a`; trả về `FAILED_POINTER_SWITCH`. | **PASS** |
| **F07** | *Partial publication detection* (Thư mục đích đã tồn tại hoặc tệp bị xung đột) | Step 3 kiểm tra đường dẫn đích $\implies$ Phát hiện thư mục phiên bản đã tồn tại, trả về `FAILED_VERSION_EXISTS`. | Ngăn chặn ghi đè đan xen phá hủy dữ liệu trước đó. | **PASS** |
| **F08** | *Recovery & reconciliation* (Tự phục hồi sau phiên chạy lỗi) | Sau phiên chạy `run_bad` bị từ chối, phiên chạy hợp lệ tiếp theo `run_good` được thực thi $\implies$ Xuất bản thành công. | Con trỏ chuyển an toàn sang `run_good`; hệ thống tự chữa lành hoàn toàn. | **PASS** |

---

## 3. BẰNG CHỨNG PHỤC HỒI PHI PHÁ HỦY (NON-DESTRUCTIVE ROLLBACK EVIDENCE)

Trong kịch bản F06:
1. Bản chạy `run_a` ban đầu xuất bản thành công:
   - Tệp Parquet: `runs/run_a/part-00000.parquet` (kích thước 1,027 bytes, băm SHA-256 xác thực).
   - Con trỏ `latest_run_id.txt` chứa: `run_a`.
2. Bản chạy `run_b` bơm lỗi cưỡng bức tại Step 5 (`fault_injection_step5=True`):
   - Quá trình cập nhật con trỏ bị gián đoạn.
   - Cơ chế rollback tại Step 6 tự động khôi phục con trỏ về giá trị trước đó (`run_a`).
   - Tệp `runs/run_a/part-00000.parquet` **vẫn nguyên vẹn 100%, đọc được bình thường, không suy giảm dữ liệu**.
   - Kết quả xuất bản của `run_b` ghi nhận `success=False`, `aborted_step=5`, trạng thái `FAILED_POINTER_SWITCH`.
   - Khẳng định: **Không có lệnh xóa phá hủy (zero destructive delete), không có con trỏ treo (no dangling pointer)**.

---

## 4. KẾT LUẬN GATE 3

- Toàn bộ 8/8 kịch bản lỗi lưu trữ bắt buộc (F01..F08) của bài kiểm thử `TS-013` đã được kiểm chứng tự động và đạt 100% PASS trong sandbox cô lập.
- Cơ chế khóa tiến trình `SingleWriterLock` và xuất bản 7 bước `SafePublisher` đáp ứng hoàn hảo tiêu chuẩn an toàn hệ thống tệp Windows NTFS theo điều kiện `G3-COND-C`.
- Không có bất kỳ thay đổi nào ngoài phạm vi sandbox.
- **GATE 3 CHÍNH THỨC ĐẠT (PASS) — Cho phép chuyển sang Phase 4 (TS-018 BTS TranStats Reconciliation).**
