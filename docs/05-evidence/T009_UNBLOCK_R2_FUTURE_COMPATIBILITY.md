# T009-UNBLOCK-R2: T-009 FUTURE FILE COMPATIBILITY AUDIT

**Task ID:** `T009-UNBLOCK-R2` (Targeted Git Metadata Exclusion & Validator Reconciliation)  
**Gate:** `G4`  
**Auditor:** Senior Software Engineer, Repository Governance Engineer & Independent QA Engineer  
**Timestamp:** 2026-10-17T08:39:30+07:00  
**Status:** `READ_ONLY_AUDIT_COMPLETE`  

---

## 1. Mục Tiêu & Ranh Giới Kiểm Toán Tiền Khả Thi (Audit Purpose & Boundary)

Theo yêu cầu nghiêm ngặt tại Mục 6 (Phase D) của chỉ thị `T009-UNBLOCK-R2`:
- Thực hiện kiểm toán chỉ đọc (`read-only`) đối với kịch bản [`tools/check_working_tree_consistency.py`](../../tools/check_working_tree_consistency.py) và cấu trúc sổ đăng ký [`docs/05-evidence/EVIDENCE_DELIVERABLE_REGISTER.json`](EVIDENCE_DELIVERABLE_REGISTER.json).
- Mục đích: Đánh giá khả năng tương thích của hệ thống kiểm toán hiện tại đối với các tệp mã nguồn, kiểm thử, cấu hình và tài liệu dự kiến sẽ được tạo ra trong nhiệm vụ sắp tới: **`T-009` (Controlled Spark Environment & Toolchain Bootstrap)**.
- **Ranh giới an toàn tuyệt đối:** AI Agent KHÔNG tự ý mở rộng phạm vi sửa đổi validator trong nhiệm vụ này để cho phép các tệp này trước khi có chỉ thị và quyết định riêng từ Project Lead.

---

## 2. Ma Trận Đánh Giá Tương Thích Các Tệp Dự Kiến Trong T-009

| Hạng Mục Tệp Dự Kiến Trong T-009 | Đường Dẫn / Định Dạng Mẫu | Tương Thích Hiện Tại | Quy Tắc Kiểm Toán Gây Lỗi (Incompatibility Rule) | Đánh Giá Tác Động Tới T-009 |
|---|---|:---:|---|---|
| **Mã nguồn production PySpark** | `src/flight_pipeline/__init__.py`<br>`src/flight_pipeline/core/...` | **KHÔNG TƯƠNG THÍCH** (`INCOMPATIBLE`) | 1. Dòng 484–501: `loc_ok` chỉ cho phép `docs/05-evidence/`, `tools/audit/`, `tools/qa/`. Không có nhánh cho `src/`.<br>2. Dòng 568–585: Mọi tệp trong `src/` sẽ bị xếp vào `unrecognized stray files` và gây `Exit Code 1`. | **Chặn cứng (`BLOCKER`)** khi bắt đầu tạo mã nguồn `src/` tại T-009. |
| **Bộ kiểm thử đơn vị & tích hợp** | `tests/__init__.py`<br>`tests/test_env.py`<br>`tests/test_predicates.py` | **KHÔNG TƯƠNG THÍCH** (`INCOMPATIBLE`) | 1. Dòng 484–501: `loc_ok` không cho phép thư mục `tests/`.<br>2. Dòng 568–585: Mọi tệp trong `tests/` sẽ bị coi là tệp lạ ngoài danh mục. | **Chặn cứng (`BLOCKER`)** khi tạo test suite của T-009. |
| **Quản lý phụ thuộc dự án** | `requirements.txt`<br>`pyproject.toml`<br>`setup.py` | **KHÔNG TƯƠNG THÍCH** (`INCOMPATIBLE`) | 1. Dòng 484–501: `loc_ok` không cho phép tệp cấu hình tại thư mục gốc repository.<br>2. Dòng 58: `.txt` được phép trong bằng chứng nhưng không được phép ở root.<br>3. Dòng 568–585: Tệp tại root ngoài `PACKAGE_MANIFEST.json` bị đánh lỗi stray file. | **Chặn cứng (`BLOCKER`)** khi tạo tệp pin dependencies. |
| **CI Workflow Skeleton** | `.github/workflows/ci.yml` | **KHÔNG TƯƠNG THÍCH** (`INCOMPATIBLE`) | 1. Dòng 556: Bộ lọc chỉ loại trừ `.git/`, KHÔNG loại trừ `.github/`.<br>2. Dòng 58: Phần mở rộng `.yml` không nằm trong `ALLOWED_DELIVERABLE_EXTENSIONS`.<br>3. Dòng 568–585: `.github/workflows/ci.yml` bị báo là stray file. | **Chặn cứng (`BLOCKER`)** khi tạo khung CI. |
| **Tệp Bằng chứng T009** | `docs/05-evidence/T009_*.md`<br>`docs/05-evidence/T009_*.txt` | **TƯƠNG THÍCH HOÀN TOÀN** (`COMPATIBLE`) | Biểu thức `EVIDENCE_FILENAME_RE` (dòng 61–63) đã hỗ trợ đầy đủ tiền tố `T009_` và phần mở rộng `.md`, `.txt`. Task ID `T-009` đã nằm trong `ALLOWED_TASK_GATE_IDS`. | **Không chặn**; lưu bằng chứng thuận lợi. |
| **Nhật ký & Run Manifest Templates** | `conf/logging.conf`<br>`artifacts/runs/...` | **KHÔNG TƯƠNG THÍCH** (`INCOMPATIBLE`) | 1. Thư mục `conf/` hoặc `artifacts/` không được định nghĩa trong `loc_ok`.<br>2. Sẽ bị đánh trượt bởi kiểm tra `unrecognized stray files`. | **Chặn** nếu đặt trong repository mà không có quy chế quản lý riêng. |

---

## 3. Chi Tiết Các Điểm Nghẽn Kỹ Thuật (Technical Incompatibility Details)

### 3.1. Điểm nghẽn 1: Kiểm soát vị trí tệp đăng ký (`loc_ok` tại dòng 484–501)
Hiện tại, `tools/check_working_tree_consistency.py` chỉ cho phép các tệp được đăng ký nằm tại:
- `docs/05-evidence/` (dạng phẳng hoặc thư mục backup lịch sử đã định danh).
- `tools/audit/*.py`, `tools/qa/*.py`.
- Tệp chính `tools/check_working_tree_consistency.py`.

Bất kỳ tệp mới nào nằm trong `src/`, `tests/`, `.github/`, hoặc tại thư mục gốc repository (`requirements.txt`) đều sẽ nhận `loc_ok = False`, dẫn đến việc không thể đăng ký vào `EVIDENCE_DELIVERABLE_REGISTER.json`.

### 3.2. Điểm nghẽn 2: Hạch toán tệp dư thừa trong cây làm việc (dòng 568–585)
Validator yêu cầu:
$$\mathbf{actual\_files} - \mathbf{manifest\_paths} = \mathbf{raw\_data\_files} \cup \mathbf{registry\_self} \cup \mathbf{verified\_deliv\_paths}$$
Nếu một tệp không thể đăng ký vào registry (như `src/` hay `tests/`), nó bắt buộc sẽ rơi vào tập hợp `unrecognized`, làm cho kiểm tra `len(unrecognized) == 0` thất bại và trả về `Exit Code 1`.

### 3.3. Điểm nghẽn 3: Danh mục phần mở rộng cho phép (`ALLOWED_DELIVERABLE_EXTENSIONS`)
Dòng 58:
```python
ALLOWED_DELIVERABLE_EXTENSIONS = {".md", ".csv", ".json", ".py", ".bak", ".txt"}
```
Các tệp cấu hình phổ biến như `.yml` (cho GitHub Actions), `.toml` (cho `pyproject.toml`), `.ini`/`.cfg` (cho pytest hoặc flake8) đều bị từ chối nếu đưa vào diện đăng ký quản trị.

---

## 4. Đề Xuất Phạm Vi Thay Đổi Riêng Cho T-009 (Phải Trình Project Lead Duyệt)

Để triển khai thành công nhiệm vụ `T-009` mà không làm suy giảm tính toàn vẹn của hệ thống quản trị, cần một quyết định kiến trúc (`Architecture Decision`) từ Project Lead phê duyệt gói mở rộng cho `tools/check_working_tree_consistency.py`:

1. **Mở rộng `ALLOWED_DELIVERABLE_EXTENSIONS`:** Bổ sung `.yml`, `.toml`, `.cfg`.
2. **Bổ sung quy tắc vị trí `loc_ok`:**
   - Cho phép các tệp mã nguồn: `dp.startswith("src/flight_pipeline/") and ext == ".py"`.
   - Cho phép các tệp kiểm thử: `dp.startswith("tests/") and ext == ".py"`.
   - Cho phép tệp cấu hình CI: `dp.startswith(".github/workflows/") and ext in (".yml", ".yaml")`.
   - Cho phép tệp phụ thuộc tại root: `dp in ("requirements.txt", "pyproject.toml", "setup.py")`.
3. **Phân loại vai trò Artifact:** Bổ sung các `ALLOWED_ARTIFACT_TYPES` mới: `"PIPELINE_MODULE"`, `"TEST_MODULE"`, `"CI_CONFIG"`, `"DEPENDENCY_SPEC"`.

---

## 5. Kết Luận Kiểm Toán

- Hệ thống kiểm toán sau bản vá `T009-UNBLOCK-R2` đã hoàn toàn hỗ trợ trạng thái Git và tài liệu bằng chứng hiện tại.
- Các tệp dự kiến tạo trong `T-009` (`src/`, `tests/`, `requirements.txt`, `.github/`) sẽ cần một chỉ thị phê duyệt mở rộng validator có kiểm soát khi Project Lead ban hành lệnh khởi động `T-009`.
- **Ranh giới tuân thủ:** AI Agent giữ nguyên hiện trạng, không tự ý sửa đổi trước khi có lệnh.
