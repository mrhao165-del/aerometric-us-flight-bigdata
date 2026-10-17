# T009-R2: NON-DESTRUCTIVE ROLLBACK POLICY & SAFETY ADDENDUM

**Task ID:** `T-009` (Remediation & Independent Corrective Audit R2)  
**Gate:** `G4`  
**Auditor:** Senior Big Data Architect & Repository Governance Engineer  
**Date:** 2026-10-17  
**Status:** `DESTRUCTIVE_INSTRUCTIONS_REVOKED_AND_SUPERSEDED`  

---

## 1. Tuyên Bố Thu Hồi Hướng Dẫn Hoàn Nguyên Phá Hủy Trong R1 (Revocation Notice)

Trong tài liệu [`T009_R1_ROLLBACK_PLAN.md`](T009_R1_ROLLBACK_PLAN.md) (Mục 3), tác giả đã đề xuất các lệnh PowerShell có tính chất phá hủy (destructive):
```powershell
# CÁC LỆNH SAU ĐÃ BỊ THU HỒI HIỆU LỰC HOÀN TOÀN:
Remove-Item -Recurse -Force src/flight_pipeline
Remove-Item -Recurse -Force tests
Remove-Item -Recurse -Force .github/workflows
Remove-Item -Force requirements.txt
Remove-Item -Force docs/05-evidence/T009_R1_*
```

**ĐÁNH GIÁ NGUY CƠ:**
- Việc sử dụng `Remove-Item -Force` làm mất vĩnh viễn dấu vết lịch sử (forensic audit trail) của các tệp bằng chứng R1, vi phạm nghiêm trọng chính sách quản trị tại [`AGENTS.md`](../../AGENTS.md) và tài liệu chuẩn tắc [`ROLLBACK_PLAN.md`](../03-quality/ROLLBACK_PLAN.md) ("*Bảo tồn lịch sử (Non-destructive): Tuyệt đối không xóa dữ liệu, force push, reset hard...*").
- **QUYẾT ĐỊNH:** Toàn bộ các hướng dẫn xóa tệp bằng lệnh `Remove-Item` trong `T009_R1_ROLLBACK_PLAN.md` chính thức bị **THU HỒI VÀ VÔ HIỆU HÓA HOÀN TOÀN**. Tài liệu lịch sử `T009_R1_ROLLBACK_PLAN.md` được giữ lại nguyên trạng làm bằng chứng kiểm toán quá khứ, nhưng quy trình kỹ thuật được thay thế bằng phụ lục chuẩn tắc này.

---

## 2. Quy Trình Hoàn Nguyên Chuẩn Tắc Bằng Git & Bản Sao Lưu (Non-Destructive Rollback Procedure)

Nếu Project Lead ra chỉ thị hoàn nguyên các thay đổi của nhiệm vụ T-009, quy trình an toàn sau đây bắt buộc phải được áp dụng:

### 2.1. Điểm hoàn nguyên chuẩn tắc (Rollback Baseline Target)
- **Commit SHA:** `be1b81e676dde78767c05a0cd2420ec171ba960f`
- **Branch:** `master`
- **Thông điệp baseline:** `fix(governance): exclude root .git metadata from working tree validator` (Kết thúc T009-UNBLOCK-R2).

### 2.2. Phương thức 1: Hoàn nguyên bảo tồn lịch sử qua Git Revert (Khuyến nghị cao nhất)
Sử dụng `git revert` để tạo một commit đảo ngược mới, bảo đảm lịch sử commit không bị viết lại (non-destructive history):
```powershell
# Tạo commit hoàn nguyên không phá hủy lịch sử
git revert --no-commit cda19fb..HEAD
git commit -m "revert(t009): cleanly roll back T-009 code changes to baseline be1b81e"
```

### 2.3. Phương thức 2: Cách ly sang nhánh kiểm toán (Branch Isolation)
Nếu cần đưa repository về trạng thái sạch tại baseline mà không can thiệp vào branch hiện tại:
```powershell
# Tạo nhánh mới từ commit baseline để làm việc độc lập
git checkout -b rollback-to-be1b81e be1b81e676dde78767c05a0cd2420ec171ba960f
```

### 2.4. Dọn dẹp an toàn các thư mục tạm ngoài tree
Chỉ dọn dẹp các tệp bộ nhớ đệm tạm thời nằm bên ngoài repository:
```powershell
# Xóa tệp rác tạm của PySpark trong thư mục đệm ngoài repository
if (Test-Path D:\Study\Code\Apache\Flight_Analyzt\tmp_spark) {
    Remove-Item -Recurse -Force D:\Study\Code\Apache\Flight_Analyzt\tmp_spark\*
}
```

### 2.5. Hậu kiểm sau hoàn nguyên (Post-Rollback Verification)
Chạy công cụ kiểm toán để bảo đảm repository trở về trạng thái toàn vẹn tại baseline:
```powershell
python tools/check_working_tree_consistency.py
```
- Kết quả mong đợi: `Working-Tree PASS assertions: 409; FAIL: 0`.

---

## 3. Kết Luận (Safety Verdict)

Quy trình hoàn nguyên phi phá hủy bằng Git bảo vệ 100% tính toàn vẹn của dữ liệu thô, các tệp bằng chứng lịch sử và cấu trúc repository, triệt tiêu mọi rủi ro mất mát dữ liệu do các lệnh shell xóa cưỡng bức gây ra.
