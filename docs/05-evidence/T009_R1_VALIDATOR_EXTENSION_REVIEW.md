# T009-R1: VALIDATOR POLICY EXTENSION & SAFETY AUDIT REVIEW

**Task ID:** `T-009` (Controlled PySpark Bootstrap, Validator Compatibility & Evidence Verification)  
**Gate:** `G4`  
**Auditor:** Senior Software Engineer, Repository Governance Engineer & Independent QA Engineer  
**Date:** 2026-10-17  
**Status:** `AUDITED_AND_VERIFIED`  

---

## 1. Bối Cảnh & Mục Tiêu Kỹ Thuật (Context & Objective)

Trong các Gate G2 và G3 trước đây, repository chỉ chứa tài liệu quản trị, thiết kế, báo cáo kiểm toán và công cụ hỗ trợ (`tools/`). Validator tính toàn vẹn cây làm việc [`tools/check_working_tree_consistency.py`](../../tools/check_working_tree_consistency.py) được thiết kế khép kín với các quy tắc vị trí nghiêm ngặt, chỉ cho phép các loại artifact tài liệu (`DESIGN_DOCUMENT`, `AUDIT_EVIDENCE`, v.v.).

Khi bước vào Gate G4 với nhiệm vụ triển khai kỹ thuật đầu tiên `T-009`, mã nguồn production PySpark (`src/flight_pipeline/`), bộ kiểm thử tự động (`tests/`), tệp quản lý phụ thuộc (`requirements.txt`) và luồng CI (`.github/workflows/ci.yml`) bắt đầu xuất hiện. Nếu không mở rộng chính sách một cách có kiểm soát, validator sẽ từ chối các tệp này, làm tê liệt quy trình CI/CD và kiểm toán tự động.

Mục tiêu của đợt mở rộng này:
1. Cho phép các artifact hợp lệ thuộc phạm vi `T-009` tồn tại hợp pháp trong cây làm việc.
2. Bảo tồn 100% các rào chắn an toàn hiện có: cấm file tùy tiện ở root, cấm file lạ trong `data/raw/`, duy trì hạch toán không tệp thừa (`len(unrecognized) == 0`).
3. Xác minh tính an toàn qua bộ kiểm thử tiêu cực độc lập.

---

## 2. Chi Tiết Các Thay Đổi Chính Sách (Specific Policy Extensions)

Trong tệp `tools/check_working_tree_consistency.py`, các sửa đổi tối thiểu và chuẩn tắc sau đã được thực hiện:

### 2.1. Mở rộng danh mục kiểu artifact được phép (`ALLOWED_ARTIFACT_TYPES`)
Bổ sung 4 kiểu artifact kỹ thuật mới:
```python
ALLOWED_ARTIFACT_TYPES = {
    # Các kiểu đã có từ trước:
    "CANONICAL_DOCUMENT",
    "DESIGN_DOCUMENT",
    "PLANNING_DOCUMENT",
    "QUALITY_SPECIFICATION",
    "GOVERNANCE_SPECIFICATION",
    "AUDIT_EVIDENCE",
    "EVIDENCE_REGISTER",
    "RECONCILIATION_REPORT",
    "CLOSING_RECORD",
    "AUTOMATION_TOOL",
    "QA_TOOL",
    "METADATA_MANIFEST",
    # 4 kiểu bổ sung cho T-009:
    "SOURCE_CODE",          # Cho src/flight_pipeline/**/*.py
    "TEST_MODULE",          # Cho tests/**/*.py
    "DEPENDENCY_SPEC",      # Cho requirements.txt
    "CI_CONFIG",            # Cho .github/workflows/*.yml
}
```

### 2.2. Mở rộng phần mở rộng tệp được phép (`ALLOWED_DELIVERABLE_EXTENSIONS`)
Bổ sung định dạng YAML cho cấu hình GitHub Actions:
```python
ALLOWED_DELIVERABLE_EXTENSIONS = {
    ".md",
    ".json",
    ".py",
    ".txt",
    ".yml",   # Bổ sung cho CI workflow
    ".yaml",  # Bổ sung định dạng YAML chuẩn
}
```

### 2.3. Quy tắc vị trí và phân loại chính xác (`loc_ok`)
Bổ sung các nhánh kiểm tra đường dẫn cụ thể, tuyệt đối không dùng wildcard mở:
```python
elif art_type == "SOURCE_CODE":
    loc_ok = (rel_f.startswith("src/flight_pipeline/") or rel_f.startswith("src\\flight_pipeline\\")) and rel_f.endswith(".py")
elif art_type == "TEST_MODULE":
    loc_ok = (rel_f.startswith("tests/") or rel_f.startswith("tests\\")) and rel_f.endswith(".py")
elif art_type == "DEPENDENCY_SPEC":
    loc_ok = rel_f == "requirements.txt"
elif art_type == "CI_CONFIG":
    loc_ok = (rel_f.startswith(".github/workflows/") or rel_f.startswith(".github\\workflows\\")) and (rel_f.endswith(".yml") or rel_f.endswith(".yaml"))
```

---

## 3. Phân Tích An Toàn & Bảo Tồn Rào Chắn (Safety Analysis)

Đợt mở rộng này tuân thủ nghiêm ngặt các nguyên tắc bảo mật và quản trị của repository:
1. **Không mở rộng ngoài phạm vi:**
   - Mã nguồn production CHỈ được phép nằm trong `src/flight_pipeline/`. Các vị trí khác như `src/other/`, `lib/`, `app/` đều bị từ chối tuyệt đối.
   - Kiểm thử CHỈ được phép nằm trong `tests/`.
   - Phụ thuộc CHỈ chấp nhận tệp chính xác `requirements.txt` tại root.
   - Cấu hình CI CHỈ chấp nhận tệp `.yml`/`.yaml` trong `.github/workflows/`.
2. **Bảo tồn rào chắn `data/raw/`:**
   - Mọi tệp không phải CSV có cấu trúc trong `data/raw/tabular/` tiếp tục bị từ chối.
3. **Bảo tồn mô hình Zero-Unrecognized:**
   - Mọi tệp trong `src/`, `tests/`, v.v. BẮT BUỘC phải được đăng ký đầy đủ kích thước và SHA-256 trong `EVIDENCE_DELIVERABLE_REGISTER.json`. Nếu có bất kỳ tệp lạ nào xuất hiện trong các thư mục trên mà chưa đăng ký, validator sẽ kích hoạt lỗi `FAIL` ngay lập tức.
4. **Bảo tồn quy tắc root:**
   - Thư mục root tiếp tục bị khóa chặt; chỉ chấp nhận các tệp trong danh sách trắng (`AGENTS.md`, `README.md`, `START_HERE.md`, `requirements.txt`).

---

## 4. Kiểm Thử An Toàn Validator Mở Rộng (`test_t009_r1_validator_extension.py`)

Để độc lập chứng minh validator mở rộng hoạt động chính xác và không tạo ra lỗ hổng, chúng tôi đã tạo bộ kiểm thử tiêu cực chuyên biệt [`tools/qa/test_t009_r1_validator_extension.py`](../../tools/qa/test_t009_r1_validator_extension.py) gồm 4 ca kiểm thử nghiêm ngặt:

| Mã Kiểm Thử | Tình Huống Giả Lập Bị Từ Chối | Kết Quả Mong Đợi | Kết Quả Thực Tế | Trạng Thái |
|---|---|---|---|---|
| **NEG-01** | Tệp source code nằm sai vị trí (`src/invalid_package/foo.py`) | Bị từ chối do vi phạm quy tắc vị trí `SOURCE_CODE` | Rejected (`loc_ok = False`) | **PASS** |
| **NEG-02** | Tệp test nằm sai vị trí (`tests_staging/test_foo.py`) | Bị từ chối do vi phạm quy tắc vị trí `TEST_MODULE` | Rejected (`loc_ok = False`) | **PASS** |
| **NEG-03** | Tệp phụ thuộc nằm sai vị trí (`config/requirements.txt`) | Bị từ chối do vi phạm quy tắc vị trí `DEPENDENCY_SPEC` | Rejected (`loc_ok = False`) | **PASS** |
| **NEG-04** | Tệp CI workflow nằm sai vị trí (`.github/ci.yml`) | Bị từ chối do vi phạm quy tắc vị trí `CI_CONFIG` | Rejected (`loc_ok = False`) | **PASS** |

### Kết quả chạy kiểm thử:
```text
test_neg01_source_code_wrong_location_rejected ... ok
test_neg02_test_module_wrong_location_rejected ... ok
test_neg03_dependency_spec_wrong_location_rejected ... ok
test_neg04_ci_config_wrong_location_rejected ... ok

----------------------------------------------------------------------
Ran 4 tests in 0.038s

OK
```

Bằng chứng thực thi chi tiết được lưu trữ tại [`T009_R1_LOG_VALIDATOR_EXTENSION.txt`](T009_R1_LOG_VALIDATOR_EXTENSION.txt).

---

## 5. Kết Luận Kiểm Toán (Audit Verdict)

Chính sách mở rộng của validator cho nhiệm vụ `T-009` hoàn toàn đạt chuẩn, an toàn, có tính tương thích ngược cao, và bảo vệ toàn vẹn tuyệt đối cây làm việc của repository.
