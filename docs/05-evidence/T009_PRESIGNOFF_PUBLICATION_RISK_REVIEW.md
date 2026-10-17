# T009-PRESIGNOFF: PUBLICATION SAFETY & CONCURRENCY RISK AUDIT

**Task ID:** `T-009` (Pre-Signoff Publication Audit)  
**Gate:** `G4`  
**Auditor:** Senior Big Data Architect & Systems Safety Engineer  
**Execution Mode:** `READ_ONLY_SOURCE_AUDIT — EVIDENCE_OUTPUT_ONLY`  
**Date:** 2026-10-17  
**Status:** `AUDITED_RISKS_CONTAINED`  

---

## 1. Tổng Quan Kiến Trúc Xuất Bản 7 Bước NTFS

Quy trình xuất bản an toàn triển khai trong lớp [`SafePublisher`](../../src/flight_pipeline/storage/publication.py#L31-L220) tại [`src/flight_pipeline/storage/publication.py`](../../src/flight_pipeline/storage/publication.py) tuân thủ nghiêm ngặt 7 bước đã được phê duyệt trong [`ARCHITECTURE.md`](../02-design/ARCHITECTURE.md) Section 2 và [`T006_FINAL_CORRECTIONS_ADDENDUM.md`](T006_FINAL_CORRECTIONS_ADDENDUM.md) Section 4:

1. **Bước 1: Kiểm tra Thư mục Tạm (Staging Validation):** Xác minh `staging_dir` tồn tại và chứa tệp Parquet.
2. **Bước 2: Xác thực Cân bằng Dòng (Row Accounting Verification):** Kiểm tra $raw = accepted + quarantined + rejected$ (DC-11). Dừng ngay với mã `ACCOUNTING_UNVERIFIED` nếu mất cân bằng.
3. **Bước 3: Thăng cấp Phân bản Bất biến (Versioned Promotion):** Sao chép vào `curated/runs/{run_id}/`. Kiểm tra tuyệt đối tính bất biến: nếu thư mục đích đã tồn tại, từ chối với mã `FAILED_VERSION_EXISTS`.
4. **Bước 4: Hậu kiểm Đọc & Đầy đủ (Completeness Audit):** Kiểm tra số lượng tệp được thăng cấp khớp 100% với tệp staging.
5. **Bước 5: Chuyển dịch Con trỏ Nguyên tử (Atomic Pointer Switch):** Tạo tệp tạm thời `.latest_run_id_{run_id}.tmp` và gọi `os.replace` trên hệ thống tệp NTFS với cơ chế thử lại (exponential backoff).
6. **Bước 6: Hậu kiểm Con trỏ & Hoàn nguyên An toàn (Post-Pointer Verification):** Đọc lại `latest_run_id.txt`. Nếu con trỏ không khớp `run_id`, hoàn nguyên con trỏ về giá trị cũ.
7. **Bước 7: Đóng Đợt Chạy & Lưu Vết (Audit Closure):** Trả về trạng thái `PUBLISHED` và bảo tồn toàn bộ dữ liệu staging cũng như phân bản để phục vụ giám định pháp y.

---

## 2. Phân Tích Chuyên Sâu Các Rủi Ro Kỹ Thuật & Cạnh Tranh (Concurrency Analysis)

### 2.1. Phân tích Rủi ro TOCTOU (Time-Of-Check to Time-Of-Use)
- **Tình huống:** Giữa thời điểm kiểm tra `if versioned_target.exists():` (Dòng 111) và thao tác `shutil.copytree(staging_dir, versioned_target)` (Dòng 122), có tiến trình khác can thiệp tạo thư mục `versioned_target`.
- **Đánh giá kiểm toán:**
  - Trong Python 3.8+, hàm `shutil.copytree` mặc định có tham số `dirs_exist_ok=False`.
  - Nếu `versioned_target` xuất hiện giữa chừng, `shutil.copytree` sẽ ném ngoại lệ `FileExistsError`.
  - Khối lệnh `try ... except Exception as exc:` tại Dòng 123 bắt được ngoại lệ này và hủy bỏ xuất bản với mã `FAILED_PROMOTION`.
  - **Kết luận:** **Không có nguy cơ dữ liệu bị ghi đè hay hỏng hóc.** Tuy nhiên, mã trạng thái trả về là `FAILED_PROMOTION` thay vì `FAILED_VERSION_EXISTS`.

### 2.2. Xử lý Trạng thái Lỗi Sau Thăng cấp & Ràng buộc Thử lại Đợt Chạy (FIND-05)
- **Tình huống:** Nếu một đợt chạy thăng cấp thành công ở Bước 3 nhưng gặp sự cố ở Bước 4 (thiếu tệp) hoặc Bước 5 (khóa tệp con trỏ):
  - Thư mục `curated/runs/{run_id}` đã được tạo ra trên đĩa.
  - Theo chính sách bảo tồn bằng chứng pháp y (forensic preservation), `SafePublisher` **không xóa thư mục này**.
  - Khi đó, nếu người vận hành thử chạy lại pipeline với **cùng một `run_id`**, Bước 3 sẽ phát hiện thư mục đã tồn tại và từ chối với lỗi `FAILED_VERSION_EXISTS`.
- **Khuyến nghị vận hành:** Mọi lần thử lại (retry) bắt buộc phải sử dụng một `run_id` mới (ví dụ gắn thêm timestamp hoặc hậu tố `_retry1`). Đây là hành vi đúng đắn nhằm bảo vệ tính bất biến của lịch sử dữ liệu.

### 2.3. Khả Năng Chống Chịu Sự Cố Tiến Trình Đột Ngột Dừng (Process Crash Resilience)
- **Trường hợp sập nguồn trong Bước 3 (File Copy):**
  - Dữ liệu trong `curated/runs/{run_id}` mới chỉ được chép một phần.
  - Tuy nhiên, tệp `latest_run_id.txt` **chưa hề bị đụng đến** và vẫn trỏ tới phiên bản hợp lệ trước đó.
  - Bất kỳ người dùng hoặc quy trình đọc downstream nào cũng không bao giờ đọc phải dữ liệu dở dang.
- **Trường hợp sập nguồn trong Bước 5 (Pointer Switch):**
  - Thao tác `os.replace` trên Windows NTFS là một thao tác siêu dữ liệu nguyên tử (atomic metadata transaction). Tệp con trỏ chỉ có thể ở trạng thái cũ hoặc trạng thái mới, không bao giờ rơi vào trạng thái rỗng hay chứa nửa chuỗi ký tự.

### 2.4. Tính An Toàn Khi Sao Chép Khác Phân Vùng Ổ Đĩa (Cross-Volume Copy)
- Việc sử dụng `shutil.copytree` đảm bảo khả năng hoạt động an toàn ngay cả khi thư mục `staging` và thư mục `curated` nằm trên các ổ đĩa logic hoặc phân vùng khác nhau (tránh lỗi `EXDEV: Invalid cross-device link` vốn thường gặp khi dùng `os.rename`).

---

## 3. Bảng Phân Định Hiện Trạng Kỹ Thuật (Claims vs Evidence Matrix)

Để đảm bảo tính trung thực tuyệt đối theo chính sách [`AGENTS.md`](../../AGENTS.md), kiểm toán viên phân định rõ ràng giữa các khẳng định lý thuyết và bằng chứng thực tế:

| Khía Cạnh Đánh Giá | Hiện Trạng Mã Nguồn | Hiện Trạng Kiểm Thử | Trạng Thái Bằng Chứng | Đánh Giá Nghiệm Thu |
|---|---|---|---|:---:|
| **Logic 7 bước an toàn** | Đã lập trình đầy đủ | Có test bao phủ | Đã chạy test thành công (`test_successful_publication_sequence`) | **ĐẠT** |
| **Bất biến dòng DC-11** | Đã lập trình đầy đủ | Có test bao phủ | Đã chạy test thành công (`test_unbalanced_accounting_aborts_publication`) | **ĐẠT** |
| **Bất biến phân bản** | Đã lập trình đầy đủ | Có test bao phủ | Đã chạy test thành công (`test_version_immutability_rejection`) | **ĐẠT** |
| **Mô phỏng sự cố TS-013** | Đã lập trình đầy đủ | Có test bao phủ | Đã chạy test thành công (`test_fault_injection_step5_preserves_...`) | **ĐẠT (Simulation)** |
| **Tính nguyên tử NTFS** | Sử dụng `os.replace` | Dựa trên Windows API | Lập luận thiết kế chuẩn kiến trúc Windows NTFS | **ĐẠT** |
| **TS-013 trên 54.7M hàng** | Chưa chạy trên toàn dataset | Chưa đến Gate G5 | Ngoài phạm vi G4 (Chưa kiểm chứng ở quy mô lớn) | **RESERVED FOR G5** |
