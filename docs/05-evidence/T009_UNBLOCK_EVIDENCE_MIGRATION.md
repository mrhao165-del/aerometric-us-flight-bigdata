# T009-UNBLOCK EVIDENCE MIGRATION & NORMALIZATION REPORT

**Task ID:** `T009-UNBLOCK-R1`  
**Gate:** `G4`  
**Auditor:** Senior Software Engineer, Repository Governance Engineer & Independent QA Engineer  
**Timestamp:** 2026-10-17T08:21:00+07:00  
**Status:** `MIGRATION_COMPLETE / REPOSITORY_STRUCTURE_CANONICAL`  

---

## 1. Mục Đích & Quyết Định Bố Cục Bằng Chứng

Căn cứ phê duyệt của Project Lead tại phiên chỉ thị `T009-UNBLOCK-R1`:
- **Chế độ cấu trúc bằng chứng:** `EVIDENCE_LAYOUT = FLAT_CANONICAL`.
- **Thư mục đích chuẩn:** Trực tiếp dưới `docs/05-evidence/`.
- **Mục tiêu:** Đưa toàn bộ báo cáo và nhật ký của nhiệm vụ `T-009` về quy cách đặt tên phẳng, tương thích hoàn toàn 100% với biểu thức `EVIDENCE_FILENAME_RE` của bộ kiểm toán tính nhất quán cây làm việc `tools/check_working_tree_consistency.py`.

---

## 2. Bảng Đối Chiếu Chuyển Đổi Tệp Bằng Chứng (Migration Mapping Table)

| STT | Đường dẫn Ban đầu (Old Path trong Backup) | Đường dẫn Chuẩn hóa Mới (New Canonical Path) | Vai trò Tài liệu | Điều chỉnh Nội dung / Liên kết |
|:---:|---|---|:---:|---|
| 1 | `T009_ORIGINAL/01_DOCUMENT_READING_AND_AUTHORITY_AUDIT.md` | `docs/05-evidence/T009_DOCUMENT_READING_AND_AUTHORITY_AUDIT.md` | `AUDIT_REPORT` | Cập nhật ghi chú vị trí chuẩn hóa phẳng |
| 2 | `T009_ORIGINAL/02_BASELINE_AND_SCOPE_REPORT.md` | `docs/05-evidence/T009_BASELINE_AND_SCOPE_REPORT.md` | `AUDIT_REPORT` | Cập nhật ghi chú vị trí chuẩn hóa phẳng |
| 3 | `T009_ORIGINAL/08_RISK_AND_DEVIATION_REPORT.md` | `docs/05-evidence/T009_RISK_AND_DEVIATION_REPORT.md` | `AUDIT_REPORT` | Điều chỉnh liên kết tương đối `../03-quality/RISK_REGISTER.md` phù hợp thư mục cha |
| 4 | `T009_ORIGINAL/10_FINAL_T009_REVIEW.md` | `docs/05-evidence/T009_FINAL_REVIEW.md` | `AUDIT_REPORT` | Cập nhật liên kết tương đối giữa 4 báo cáo T-009 phẳng |
| 5 | `T009_ORIGINAL/logs/regression_consistency.log` | `docs/05-evidence/T009_LOG_REGRESSION_CONSISTENCY.txt` | `CODE_AND_REGRESSION_AUDIT` | Chuẩn hóa phần mở rộng `.txt` được validator hỗ trợ |
| 6 | `T009_ORIGINAL/logs/regression_t006.log` | `docs/05-evidence/T009_LOG_REGRESSION_T006.txt` | `CODE_AND_REGRESSION_AUDIT` | Chuẩn hóa phần mở rộng `.txt` được validator hỗ trợ |

---

## 3. Kiểm Tra Liên Kết Tương Đối (Relative Links Verification)

1. **Liên kết sang các thư mục docs khác:**
   - Từ `docs/05-evidence/T009_RISK_AND_DEVIATION_REPORT.md` sang `docs/03-quality/RISK_REGISTER.md`: Sử dụng `../03-quality/RISK_REGISTER.md` (giải quyết chính xác `docs/03-quality/RISK_REGISTER.md`).
2. **Liên kết nội bộ giữa các bằng chứng T-009:**
   - Trong `T009_FINAL_REVIEW.md`, các liên kết đến 3 báo cáo đồng hành sử dụng liên kết tệp cùng cấp: `T009_DOCUMENT_READING_AND_AUTHORITY_AUDIT.md`, `T009_BASELINE_AND_SCOPE_REPORT.md`, `T009_RISK_AND_DEVIATION_REPORT.md`.
3. **Kiểm tra tính hợp lệ đường dẫn:** Toàn bộ đường dẫn tương đối đã được kiểm chứng không phát sinh liên kết gãy.

---

## 4. Thao Tác Di Chuyển Có Kiểm Soát Thư Mục Cũ (Controlled Folder Removal)

- Thư mục ban đầu `docs/05-evidence/T009/` đã được di chuyển an toàn bằng thao tác có kiểm soát ra khỏi không gian làm việc của repository và đưa vào thư mục lưu trữ ngoại vi:  
  `D:\Study\Code\Apache\Flight_Analyzt\T009_UNBLOCK_BACKUP_20261017_081700\T009_MOVED_FROM_REPO\`
- Tuyệt đối không sử dụng lệnh xóa vĩnh viễn mang tính phá hủy (`Remove-Item -Recurse -Force`). Toàn bộ bản gốc được bảo toàn trọn vẹn để đối chiếu lịch sử khi cần thiết.

**Kết luận:** Quá trình chuẩn hóa bằng chứng Phase B hoàn tất 100%, bảo đảm tuân thủ quy tắc hình thức của repository.
