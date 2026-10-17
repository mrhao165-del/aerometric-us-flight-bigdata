# T009-UNBLOCK-R2: VERDICT & REGRESSION RESULTS ERRATA REPORT

**Task ID:** `T009-UNBLOCK-R2` (Targeted Git Metadata Exclusion & Validator Reconciliation)  
**Gate:** `G4`  
**Auditor:** Senior Software Engineer, Repository Governance Engineer & Independent QA Engineer  
**Timestamp:** 2026-10-17T08:40:00+07:00  
**Status:** `ERRATA_PUBLISHED_AND_RECONCILED`  

---

## 1. Lý Do Ban Hành & Nguyên Tắc Bảo Tồn Lịch Sử (Rationale & Immutability)

Tài liệu này được ban hành theo yêu cầu tại Mục 7 (Phase E) của chỉ thị `T009-UNBLOCK-R2`, nhằm:
1. Đính chính và hòa giải minh bạch sự khác biệt kỹ thuật giữa các tài liệu báo cáo của nhiệm vụ `T009-UNBLOCK-R1`.
2. **Nguyên tắc bảo tồn lịch sử bất biến:** Tuyệt đối không xóa, không ghi đè, và không làm biến đổi nội dung lịch sử của [`T009_UNBLOCK_FINAL_VERDICT.md`](T009_UNBLOCK_FINAL_VERDICT.md) và [`T009_UNBLOCK_REGRESSION_RESULTS.md`](T009_UNBLOCK_REGRESSION_RESULTS.md).
3. Thiết lập chuỗi niên biểu rõ ràng thể hiện chính xác trạng thái thực thi tại từng thời điểm.

---

## 2. Đối Chiếu Các Điểm Bất Đồng Giữa Các Báo Cáo Trong T009-UNBLOCK-R1

Trong quá trình thực thi nhiệm vụ `T009-UNBLOCK-R1` (ngày 2026-10-17), đã xuất hiện sự không đồng nhất về mặt trạng thái giữa các văn bản lưu trữ và báo cáo phản hồi:

| Văn Bản / Báo Cáo | Trạng Thái Ghi Nhận | Thời Điểm Lập | Bối Cảnh & Thực Tế Kỹ Thuật |
|---|:---:|:---:|---|
| **[`T009_UNBLOCK_REGRESSION_RESULTS.md`](T009_UNBLOCK_REGRESSION_RESULTS.md)** | `ALL_REGRESSION_TESTS_PASS`<br>(385 PASS, 0 FAIL) | 2026-10-17T08:25:30 | **Kết quả thực thi TRƯỚC khi khởi tạo Git (Phase C).** Chưa phản ánh kết quả chạy lại sau khi `git init` tạo ra thư mục `.git/`. |
| **[`T009_UNBLOCK_FINAL_VERDICT.md`](T009_UNBLOCK_FINAL_VERDICT.md)** | `PRECONDITIONS_READY_FOR_T009_IMPLEMENTATION` | 2026-10-17T08:26:00 | **Được soạn thảo dựa trên kết quả kiểm tra trước Git.** Chưa tích hợp sự cố `Exit Code 1` phát sinh từ việc validator quét các tệp `.git/`. |
| **Báo cáo kết thúc phiên gửi Project Lead** | `READY_WITH_OPEN_CONDITIONS` | 2026-10-17T08:29:30 | **Phản ánh trung thực trạng thái SAU khi khởi tạo Git (Phase D/E).** Ghi nhận Git baseline đã hoàn tất nhưng validator trả về Exit Code 1 do thiếu bộ lọc loại trừ `.git/`. |

---

## 3. Trình Tự Thời Gian & Diễn Biến Kỹ Thuật Chi Tiết (Chronological Sequence)

```text
2026-10-17T08:17:00 -> [Phase A] Tạo backup an toàn ngoại vi tại T009_UNBLOCK_BACKUP_20261017_081700/
2026-10-17T08:20:00 -> [Phase B] Di chuyển thư mục T009/, tạo 6 deliverables phẳng chuẩn tắc
2026-10-17T08:23:00 -> [Phase C] Cập nhật registry; chạy check_working_tree_consistency.py
                        ==> KẾT QUẢ: 385 PASS, 0 FAIL (Exit Code 0). Ghi nhận vào báo cáo.
2026-10-17T08:24:58 -> [Phase D] Chạy `git init`, stage 186 files, tạo baseline commit 5d2ce38
2026-10-17T08:26:00 -> [Phase E] Chạy lại check_working_tree_consistency.py trong repo đã có Git
                        ==> SỰ CỐ: 383 PASS, 2 FAIL (Exit Code 1) do 227 tệp .git/ bị coi là tệp lạ.
2026-10-17T08:27:00 -> [Tuân thủ an toàn] Không tự ý sửa validator, giữ nguyên code, tạo commit 5d70035
2026-10-17T08:29:30 -> [Báo cáo Project Lead] Đề xuất phán quyết READY_WITH_OPEN_CONDITIONS
2026-10-17T08:33:00 -> [T009-UNBLOCK-R2] Project Lead phê duyệt sửa validator loại trừ .git/ ở root
2026-10-17T08:37:00 -> [Remediation] Áp dụng bộ lọc `f.relative_to(root).parts[0] != ".git"`
2026-10-17T08:41:00 -> [Hồi quy sau sửa đổi] Chạy lại kiểm thử: 100% PASS (Exit Code 0).
```

---

## 4. Bảng Đối Soát Trạng Thái Kỹ Thuật Chuẩn Tắc Hiện Hành (Current Reconciled State)

Sau khi hoàn tất khắc phục kỹ thuật tại `T009-UNBLOCK-R2`:

1. **Working-Tree Consistency Verifier:**
   - **Trước khắc phục (Post-Git R1):** `Exit Code 1` (383 PASS, 2 FAIL).
   - **Sau khắc phục (Post-Remediation R2):** **`Exit Code 0`** (385 PASS, 0 FAIL).
2. **T-006 Contract Consistency Verifier:**
   - Duy trì ổn định tuyệt đối: **`Exit Code 0`** (17 Invariants PASS, 16 Mutations PASS, 0 FAIL).
3. **Bộ kiểm thử dương tính / âm tính:**
   - Chứng minh loại trừ chính xác `.git/` ở root và phát hiện 100% các tệp lạ đưa vào thử nghiệm.
4. **Trạng thái phán quyết kỹ thuật hiện hành:**
   - Điều kiện mở duy nhất của Gate G4 đối với công cụ kiểm toán đã được xử lý triệt để.
   - Toàn bộ các tiền đề kỹ thuật, Git baseline và tài liệu quản trị đã sẵn sàng cho bước tiếp theo.
