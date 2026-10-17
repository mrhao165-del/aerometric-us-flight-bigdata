# T009-R2: WINDOWS NTFS PUBLICATION SAFETY & ATOMICITY AUDIT

**Task ID:** `T-009` (Remediation & Independent Corrective Audit R2)  
**Gate:** `G4`  
**Auditor:** Senior Big Data Architect & Storage Systems Engineer  
**Date:** 2026-10-17  
**Status:** `PUBLICATION_SAFETY_VERIFIED`  

---

## 1. Tổng Quan Kiến Trúc Động Cơ Xuất Bản An Toàn 7 Bước

Module [`src/flight_pipeline/storage/publication.py`](../../src/flight_pipeline/storage/publication.py) hiện thực hóa đầy đủ quy trình xuất bản an toàn 7 bước theo đặc tả FIX-03 trong [`T006_FINAL_CORRECTIONS_ADDENDUM.md`](T006_FINAL_CORRECTIONS_ADDENDUM.md) và [`ARCHITECTURE.md`](../02-design/ARCHITECTURE.md), được tối ưu hóa đặc thù cho các đặc tính I/O của hệ thống tệp Windows NTFS:

```
[Staging Data]
      │
      ▼ (Bước 1: Kiểm tra Staging tồn tại & không rỗng)
[Staging Verified]
      │
      ▼ (Bước 2: Xác minh hạch toán dòng DC-11: raw = acc + quar + rej)
[Accounting Verified] ──(Unbalanced)──► [HỦY BỎ: ACCOUNTING_UNVERIFIED] (Bảo tồn Staging)
      │
      ▼ (Bước 3: Promote sang thư mục versioned bất biến runs/{run_id}/)
[Versioned Target] ────(Đã tồn tại)───► [HỦY BỎ: FAILED_VERSION_EXISTS] (Không ghi đè)
      │
      ▼ (Bước 4: Kiểm toán tính toàn vẹn và số lượng tệp sau promotion)
[Completeness Verified]
      │
      ▼ (Bước 5: Chuyển con trỏ nguyên tử qua tệp đệm .tmp và os.replace)
[Pointer Switched] ────(Lỗi / TS-013)──► [HỦY BỎ: Rollback con trỏ cũ] (Bảo tồn Staging)
      │
      ▼ (Bước 6: Hậu kiểm con trỏ: đọc lại disk và so khớp run_id)
[Pointer Verified] ────(Không khớp)────► [HỦY BỎ: Rollback con trỏ cũ]
      │
      ▼ (Bước 7: Đóng phiên thành công, cập nhật RunManifest, hoàn tất)
[PUBLISHED]
```

---

## 2. Đánh Giá Ngữ Nghĩa I/O Trên Hệ Thống Tệp Windows NTFS

### 2.1. Phân biệt giữa `shutil.move` và `os.replace`
- **Hạn chế của `shutil.move` trên Windows:** Khi di chuyển thư mục hoặc tệp giữa các điểm gắn kết hoặc khi đích đã tồn tại, `shutil.move` trên Windows không bảo đảm tính nguyên tử (atomic), có thể rơi vào trạng thái sao chép dở dang nếu xảy ra mất điện hoặc bị can thiệp bởi tiến trình khác.
- **Tính nguyên tử của `os.replace` đối với tệp con trỏ:**
  - Trong Step 5, việc cập nhật con trỏ `latest_run_id.txt` được thực hiện bằng cách ghi nội dung mới vào một tệp tạm cùng thư mục (`.latest_run_id_{run_id}.tmp`), sau đó thực hiện lệnh gọi hệ thống:
    ```python
    os.replace(tmp_pointer, self.pointer_file)
    ```
  - Trên Windows NTFS, `os.replace` gọi trực tiếp Win32 API `MoveFileExW` với cờ `MOVEFILE_REPLACE_EXISTING`. Do hai tệp nằm trên cùng một volume NTFS, thao tác này được nhân hệ điều hành thực hiện như một atomic pointer switch cấp độ bảng Master File Table (MFT), loại trừ 100% khả năng người đọc nhìn thấy tệp con trỏ bị rách (torn read).

### 2.2. Kiểm soát hiện tượng khóa tệp tạm thời (File Locking Mitigation)
- Trên Windows 10, các tiến trình dịch vụ nền như Windows Defender (Antivirus Scanner) hoặc Windows Search Indexer thường xuyên mở handle khóa tạm thời trên các tệp mới sinh ra.
- Module `publication.py` đã tích hợp vòng lặp thử lại có kiểm soát (retry loop tối đa 5 lần) kết hợp thời gian chờ tăng dần (`0.05 * (attempt + 1)` giây). Điều này giúp hệ thống vượt qua các trạng thái khóa tạm thời một cách mượt mà và an toàn.

### 2.3. Rào chắn bất biến (Version Immutability Guard)
- Một thư mục phiên bản đã được xuất bản (`curated/runs/{run_id}/`) được định nghĩa là dữ liệu lịch sử chuẩn tắc và bất biến.
- Trong Bước 3, nếu phát hiện thư mục `versioned_target` đã tồn tại, hệ thống từ chối ngay lập tức (`FAILED_VERSION_EXISTS`), tuyệt đối không dùng `shutil.rmtree` để xóa hoặc ghi đè lên dữ liệu đã xuất bản.

### 2.4. Bảo tồn chứng cứ sự cố (Forensic Evidence Preservation)
- Khi phát hiện mất cân bằng dòng ở Bước 2, lỗi sao chép ở Bước 3, lỗi tệp ở Bước 4 hoặc lỗi khóa con trỏ ở Bước 5:
  - Thư mục staging được giữ nguyên vẹn để phục vụ thanh tra chất lượng dữ liệu.
  - Con trỏ `latest_run_id.txt` giữ nguyên giá trị phiên bản hợp lệ gần nhất (hoặc được hoàn nguyên về giá trị cũ nếu có sự cố tại Bước 6).
  - Không có bất kỳ dữ liệu lỗi hoặc dở dang nào bị lộ ra cho các ứng dụng phân tích phía sau.

---

## 3. Kết Quả Thực Nghiệm Kiểm Thử Đơn Vị ([`test_publication_safety.py`](../../tests/test_publication_safety.py))

Đã kiểm chứng thực nghiệm 4 kịch bản an toàn cốt lõi:
1. **Happy Path (`test_successful_publication_sequence`):** Xuất bản thành công 7 bước, con trỏ cập nhật chính xác, thư mục phiên bản đầy đủ dữ liệu. $\implies$ **PASS**.
2. **Unbalanced Accounting Rejection (`test_unbalanced_accounting_aborts_publication`):** Dữ liệu staging vi phạm DC-11 ($100 \neq 80 + 5 + 2$) bị chặn ngay tại Bước 2 với trạng thái `ACCOUNTING_UNVERIFIED`. Con trỏ phiên bản cũ được giữ nguyên. $\implies$ **PASS**.
3. **TS-013 Fault Injection Simulation (`test_fault_injection_step5_preserves_previous_pointer_and_staging`):** Kích hoạt hook bơm lỗi tại Bước 5. Con trỏ cũ được bảo tồn, thư mục staging và thư mục versioned lỗi được giữ nguyên trạng để điều tra. $\implies$ **PASS**.
4. **Version Immutability Rejection (`test_version_immutability_rejection`):** Xuất bản lại trùng `run_id` bị chặn tại Bước 3 với trạng thái `FAILED_VERSION_EXISTS`, dữ liệu gốc không bị can thiệp. $\implies$ **PASS**.

---

## 4. Ranh Giới Nhiệm Vụ & Nghĩa Vụ Chuyển Tiếp

- **Trong T-009:** Đã hoàn thành xây dựng và kiểm thử đơn vị độc lập động cơ xuất bản an toàn 7 bước, chứng minh cơ chế atomicity và rollback trên Windows NTFS.
- **Tại Gate G5 / Nhiệm vụ T-011:** Toàn bộ pipeline nạp liệu và biến đổi dữ liệu thực tế bắt buộc phải gọi `SafePublisher` để công bố các phân vùng Parquet và thực hiện kiểm thử vận hành TS-013 trên môi trường chạy thực.
