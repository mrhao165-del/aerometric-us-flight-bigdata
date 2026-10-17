# T009-R1: GOVERNANCE & ARCHITECTURAL REGRESSION AUDIT REPORT

**Task ID:** `T-009` (Controlled PySpark Bootstrap, Validator Compatibility & Evidence Verification)  
**Gate:** `G4`  
**Auditor:** Independent QA Engineer & Repository Governance Engineer  
**Date:** 2026-10-17  
**Status:** `ZERO_REGRESSIONS_VERIFIED`  

---

## 1. Mục Tiêu Kiểm Toán Hồi Quy (Regression Audit Objective)

Trong quá trình triển khai `T-009`, nhiều tệp mã nguồn mới (`src/`), tệp kiểm thử (`tests/`), cấu hình (`requirements.txt`, `.github/`) và các sửa đổi mở rộng chính sách trong `tools/check_working_tree_consistency.py` đã được đưa vào repository.

Mục tiêu của đợt kiểm toán hồi quy là bảo đảm:
1. Không làm suy thoái (regression) bất kỳ quy tắc quản trị nào đã được thiết lập từ Gate G2 và G3.
2. Bộ kiểm chuẩn hợp đồng dữ liệu T-006 (`verify_t006_contract_consistency.py`) tiếp tục vượt qua 100%.
3. Bộ kiểm chuẩn tính toàn vẹn sổ đăng ký (`test_working_tree_regression.py`) tiếp tục vượt qua 100%.
4. Logic loại trừ `.git/` của đợt R2 (`test_t009_unblock_r2_git_exclusion.py`) tiếp tục vượt qua 100%.
5. Bộ kiểm thử mở rộng validator mới (`test_t009_r1_validator_extension.py`) hoạt động chuẩn xác.
6. Cây làm việc đạt chuẩn 100% khi chạy kiểm tra toàn diện với `check_working_tree_consistency.py`.

---

## 2. Tổng Hợp Kết Quả Các Bộ Kiểm Chuẩn Hồi Quy (Regression Suites Summary)

| STT | Bộ Kiểm Chuẩn Hồi Quy | Mục Tiêu Kiểm Tra | Kết Quả Thực Tế | Trạng Thái |
|:---:|---|---|---|:---:|
| **1** | [`verify_t006_contract_consistency.py`](../../tools/qa/verify_t006_contract_consistency.py) | 17 Bất biến thiết kế G2/G3 + 16 Ca đột biến tiêu cực (Negative Mutations) | 17 PASS, 16 PASS, 0 FAIL | **PASS** |
| **2** | [`test_working_tree_registry_regression.py`](../../tools/qa/test_working_tree_registry_regression.py) | 16 Ca kiểm thử tính toàn vẹn của cơ chế băm và cấu trúc sổ đăng ký | 16 PASS, 0 FAIL | **PASS** |
| **3** | [`test_t009_unblock_r2_git_exclusion.py`](../../tools/qa/test_t009_unblock_r2_git_exclusion.py) | 5 Ca tiêu cực chặn đường dẫn `.git` sai + 2 Ca tích cực kiểm tra root `.git/` | 7 PASS, 0 FAIL | **PASS** |
| **4** | [`test_t009_r1_validator_extension.py`](../../tools/qa/test_t009_r1_validator_extension.py) | 4 Ca tiêu cực kiểm tra chặn các tệp mã nguồn/test/CI sai quy cách | 4 PASS, 0 FAIL | **PASS** |
| **5** | [`check_working_tree_consistency.py`](../../tools/check_working_tree_consistency.py) | Kiểm toán toàn bộ tệp trong cây làm việc, khóa chặt root và `data/raw/` | Toàn bộ tệp hợp lệ, 0 tệp lạ | **PASS** |

---

## 3. Chi Tiết Thực Thi Từng Bộ Kiểm Chuẩn

### 3.1. Hồi quy Hợp đồng Dữ liệu T-006 (`verify_t006_contract_consistency.py`)
- Lệnh chạy: `python tools/qa/verify_t006_contract_consistency.py`
- Kết quả:
  - 17 Invariants verified: Tất cả các quy tắc cấu trúc schema, kiểu dữ liệu, thứ tự cột, và định nghĩa 8 CORE KPI đều nhất quán 100%.
  - 16 Negative Mutations verified: Các đột biến giả lập vi phạm schema đều bị phát hiện và ngăn chặn thành công.
  - Tệp log lưu tại [`T009_R1_LOG_T006_REGRESSION.txt`](T009_R1_LOG_T006_REGRESSION.txt).

### 3.2. Hồi quy Sổ Đăng Ký Working Tree (`test_working_tree_registry_regression.py`)
- Lệnh chạy: `python tools/qa/test_working_tree_registry_regression.py`
- Kết quả:
  - `Ran 16 tests in 0.082s`
  - `OK` (16 PASS, 0 FAIL).
  - Tệp log lưu tại [`T009_R1_LOG_REGISTRY_REGRESSION.txt`](T009_R1_LOG_REGISTRY_REGRESSION.txt).

### 3.3. Tái Kiểm Tra Độc Lập An Toàn Loại Trừ Git R2 (`test_t009_unblock_r2_git_exclusion.py`)
- Lệnh chạy: `python tools/qa/test_t009_unblock_r2_git_exclusion.py`
- Kết quả:
  - `Ran 7 tests in 0.052s`
  - `OK` (7 PASS, 0 FAIL).
  - Tệp log lưu tại [`T009_R1_LOG_R2_TEST_RERUN.txt`](T009_R1_LOG_R2_TEST_RERUN.txt).

### 3.4. Kiểm Thử Mở Rộng Validator T-009 (`test_t009_r1_validator_extension.py`)
- Lệnh chạy: `python tools/qa/test_t009_r1_validator_extension.py`
- Kết quả:
  - `Ran 4 tests in 0.038s`
  - `OK` (4 PASS, 0 FAIL).
  - Tệp log lưu tại [`T009_R1_LOG_VALIDATOR_EXTENSION.txt`](T009_R1_LOG_VALIDATOR_EXTENSION.txt).

### 3.5. Kiểm Toán Toàn Vẹn Cây Làm Việc (`check_working_tree_consistency.py`)
- Lệnh chạy: `python tools/check_working_tree_consistency.py`
- Kết quả:
  - Tất cả các tệp khai báo trong `EVIDENCE_DELIVERABLE_REGISTER.json` đều tồn tại và khớp chính xác giá trị băm SHA-256.
  - Không có tệp lạ nào (`unrecognized`) tồn tại trong repository.
  - Tệp log lưu tại [`T009_R1_LOG_CONSISTENCY.txt`](T009_R1_LOG_CONSISTENCY.txt).

---

## 4. Kết Luận Kiểm Toán Hồi Quy (Regression Verdict)

Repository hoàn toàn ổn định, không có bất kỳ sự suy thoái kỹ thuật hoặc vi phạm quản trị nào. Hệ thống đạt trạng thái sẵn sàng cao nhất cho việc xem xét nghiệm thu kỹ thuật.
