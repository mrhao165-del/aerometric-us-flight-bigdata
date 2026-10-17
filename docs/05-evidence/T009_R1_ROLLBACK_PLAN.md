# T009-R1: NON-DESTRUCTIVE ROLLBACK PROCEDURE & TARGET AUDIT

**Task ID:** `T-009` (Controlled PySpark Bootstrap, Validator Compatibility & Evidence Verification)  
**Gate:** `G4`  
**Engineer:** Repository Governance Engineer & QA Engineer  
**Date:** 2026-10-17  
**Status:** `READY_FOR_EXECUTION_IF_REVERT_MANDATED`  

---

## 1. Mục Tiêu & Nguyên Tắc Hoàn Nguyên (Rollback Principles)

Theo quy định tại [`AGENTS.md`](../../AGENTS.md) và [`ROLLBACK_PLAN.md`](../03-quality/ROLLBACK_PLAN.md):
1. **Bảo tồn lịch sử (Non-destructive):** Tuyệt đối không sử dụng `git reset --hard` tùy tiện nếu có nguy cơ xóa nhầm các bằng chứng kiểm toán trước đó.
2. **Khôi phục chính xác (Target Precision):** Nếu Project Lead yêu cầu hoàn nguyên phiên bản T009-R1, hệ thống phải trở về trạng thái sạch sẽ tại commit chuẩn tắc trước khi thực hiện nhiệm vụ này.
3. **Cách ly hoàn toàn:** Dọn dẹp toàn bộ mã nguồn mới mà không ảnh hưởng đến bất kỳ tệp dữ liệu thô hoặc tài liệu thiết kế G2/G3 nào.

---

## 2. Điểm Hoàn Nguyên Chuẩn Tắc (Rollback Baseline Target)

- **Baseline Commit SHA:** `be1b81e676dde78767c05a0cd2420ec171ba960f`
- **Branch:** `master`
- **Thông điệp commit:** `fix(governance): exclude root .git metadata from working tree validator` (Hoàn thành T009-UNBLOCK-R2).
- **Trạng thái baseline:**
  - Validator: Đạt chuẩn (409 assertions).
  - T-006 Consistency: Đạt chuẩn (17 invariants, 16 mutations).
  - Registry: Hoàn toàn đồng bộ với 149 deliverables.

---

## 3. Quy Trình Hoàn Nguyên Từng Bước (Step-by-Step Rollback Execution)

Nếu có lệnh rollback chính thức từ Project Lead, quy trình sau sẽ được thực thi:

### Bước 1: Xóa các tệp mã nguồn và kiểm thử mới của T-009
Xóa bỏ hoàn toàn các thư mục và tệp kỹ thuật được sinh ra trong T-009:
```powershell
Remove-Item -Recurse -Force src/flight_pipeline
Remove-Item -Recurse -Force tests
Remove-Item -Recurse -Force .github/workflows
Remove-Item -Force requirements.txt
Remove-Item -Force tools/qa/test_t009_r1_validator_extension.py
```

### Bước 2: Xóa các tệp bằng chứng và nhật ký của T-009 R1
Xóa các tệp deliverable mang tiền tố `T009_R1_*` trong `docs/05-evidence/`:
```powershell
Remove-Item -Force docs/05-evidence/T009_R1_*
```

### Bước 3: Hoàn nguyên công cụ validator và sổ đăng ký bằng chứng
Khôi phục hai tệp quản trị về trạng thái tại commit `be1b81e676dde78767c05a0cd2420ec171ba960f`:
```powershell
git checkout be1b81e676dde78767c05a0cd2420ec171ba960f -- tools/check_working_tree_consistency.py
git checkout be1b81e676dde78767c05a0cd2420ec171ba960f -- docs/05-evidence/EVIDENCE_DELIVERABLE_REGISTER.json
```

### Bước 4: Dọn dẹp thư mục tạm ngoài tree
Xóa toàn bộ các tệp đệm, log tạm của PySpark trong thư mục ngoài repository:
```powershell
Remove-Item -Recurse -Force D:/Study/Code/Apache/Flight_Analyzt/tmp_spark/*
```

### Bước 5: Kiểm định lại tính toàn vẹn cây làm việc sau hoàn nguyên
Chạy lại công cụ kiểm toán để bảo đảm repository trở về trạng thái sạch 100%:
```powershell
python tools/check_working_tree_consistency.py
```
- Kết quả kỳ vọng: `Validation PASSED: 409 assertions passed, 0 failed`.

---

## 4. Đánh Giá Khả Năng Thực Thi (Rollback Readiness Verdict)

Kế hoạch hoàn nguyên đã được chuẩn bị đầy đủ và có thể thực thi tức thì một cách an toàn mà không làm mất mát bất kỳ dữ liệu nào.
