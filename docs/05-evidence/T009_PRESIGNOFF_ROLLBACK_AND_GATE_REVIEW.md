# T009-PRESIGNOFF: ROLLBACK SAFETY & GATE READINESS REVIEW

**Task ID:** `T-009` (Pre-Signoff Rollback & Gate Review)  
**Gate:** `G4`  
**Auditor:** Technical Project Manager & Governance Auditor  
**Execution Mode:** `READ_ONLY_SOURCE_AUDIT — EVIDENCE_OUTPUT_ONLY`  
**Date:** 2026-10-17  
**Status:** `GATE_READINESS_REVIEWED`  

---

## 1. Kiểm Toán Tính Chuẩn Xác Của Cú Pháp Git Revert (FIND-01)

### 1.1. Phân Tích Cú Pháp Trong Phụ Lục R2
Trong tài liệu [`T009_R2_ROLLBACK_SAFETY_ADDENDUM.md`](T009_R2_ROLLBACK_SAFETY_ADDENDUM.md) Mục 2.2, tài liệu đã đề xuất:
```powershell
git revert --no-commit cda19fb..HEAD
```

### 1.2. Phát Hiện Khiếm Khuyết Ngữ Nghĩa Dải Commit Của Git
- **Nguyên lý của Git:** Trong cú pháp dải phiên bản `A..B`, Git định nghĩa tập hợp các commit là: *các commit có thể chạm tới từ B nhưng KHÔNG thể chạm tới từ A*. Điều này đồng nghĩa với việc **commit A bị loại trừ khỏi dải**.
- **Hậu quả thực tế:**
  - Dải `cda19fb..HEAD` (với HEAD là commit `2ec5bf2`) **chỉ bao gồm commit `2ec5bf2` (R2)** và **loại trừ commit `cda19fb` (R1)**!
  - Nếu thực thi lệnh này, Git chỉ hoàn nguyên các tệp của đợt R2, trong khi toàn bộ mã nguồn và tệp bằng chứng của đợt R1 (`cda19fb`) vẫn còn nguyên trên cây làm việc, không thể đưa repository quay về baseline `be1b81e`!

### 1.3. Lệnh Chuẩn Tắc Thay Thế
Để hoàn nguyên triệt để toàn bộ các commit của nhiệm vụ T-009 (bao gồm cả R1 và R2) để quay về mốc chuẩn `be1b81e`, lệnh bắt buộc phải là:
```powershell
# Cú pháp chuẩn xác 1: Sử dụng mốc baseline be1b81e làm điểm cận dưới
git revert --no-commit be1b81e..HEAD
git commit -m "revert(t009): cleanly roll back all T-009 changes to baseline be1b81e"

# Hoặc cú pháp chuẩn xác 2: Sử dụng toán tử commit cha của R1 (cda19fb^)
git revert --no-commit cda19fb^..HEAD
```

---

## 2. Kiểm Toán Các Thao Tác Xóa File Trong Kế Hoạch Hoàn Nguyên Lịch Sử

Kiểm toán viên xác nhận quyết định thu hồi tại R2 đối với các lệnh phá hủy trong `T009_R1_ROLLBACK_PLAN.md`:
- Các lệnh `Remove-Item -Recurse -Force src/flight_pipeline`, `tests/`, `.github/workflows`, `requirements.txt`, và `docs/05-evidence/T009_R1_*` **chính thức bị cấm và vô hiệu hóa**.
- Quy trình hoàn nguyên bắt buộc phải sử dụng Git revert hoặc cách ly nhánh (`git checkout -b rollback-branch be1b81e`), tuyệt đối không xóa bằng chứng lịch sử.
- Chỉ các tệp đệm tạm bên ngoài repository (`D:\Study\Code\Apache\Flight_Analyzt\tmp_spark\`) mới được phép dọn dẹp vật lý.

---

## 3. Phân Định Trạng Thái Công Việc & Ranh Giới Gate G4

Để ngăn ngừa việc nghiệm thu vượt cấp hoặc nhầm lẫn tiến độ, kiểm toán viên xác lập ranh giới rõ ràng:

| Hạng Mục | Trạng Thái Thực Tế Hiện Tại | Thẩm Quyền Quyết Định | Ranh Giới & Ràng Buộc |
|---|:---:|:---:|---|
| **Nhiệm vụ T-009** | `TECHNICAL_IMPLEMENTATION_COMPLETED` | Project Lead (Human) | Đã hoàn thành mã nguồn, unit test và kiểm toán; chờ ký duyệt chính thức. |
| **Nhiệm vụ T-007 (Ingestion)** | `NOT_STARTED` | Chưa kích hoạt | Bắt buộc phải hoàn tất nghiệm thu T-009 mới được bắt đầu. |
| **Nhiệm vụ T-008 (Quality Engine)**| `NOT_STARTED` | Chưa kích hoạt | Phụ thuộc vào T-007; chưa được phép triển khai. |
| **Gate G4** | `PLANNED / NOT_COMPLETED` | Project Lead (Human) | G4 chỉ đạt khi cả T-009, T-007, và T-008 hoàn thành và có signoff đầy đủ. |

---

## 4. Bảo Lưu Các Ngoại Lệ & Quyết Định Quản Trị Cốt Lõi

Toàn bộ các quyết định và ngoại lệ nền tảng tiếp tục được bảo lưu nguyên vẹn:
1. **G2-EXC-001 / OR-05 / OR-08:** Bảo tồn trạng thái của 9 CSV thô, bảo lưu việc không lập chỉ số hủy/chuyển hướng do thiếu trường, bảo lưu giới hạn mẫu.
2. **FP-DEC-017:** Không suy diễn ngày đến từ thành phần ngày của `CRS_ARR_TIME`; không tự ý cộng 24h để sửa rollover khi chưa có căn cứ.
3. **G3-COND-A/B/C:** Bảo lưu đơn vị đo lường 7 thước đo (phút), ranh giới miền số thực hữu hạn, và cấu trúc thư mục xuất bản.
4. **TS-018 tại G5:** Kiểm tra độ chính xác thống kê và số học trên 54.7 triệu hàng được bảo lưu thực hiện tại Gate G5, không được tự ý công bố hoàn thành tại G4.
