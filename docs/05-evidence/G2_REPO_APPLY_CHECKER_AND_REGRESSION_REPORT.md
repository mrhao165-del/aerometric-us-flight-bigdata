# G2_REPO_APPLY_CHECKER_AND_REGRESSION_REPORT — Báo cáo Khắc phục Công cụ Kiểm tra Working-Tree, Sổ Đăng ký Bằng chứng & Kiểm thử Hồi quy Âm/Dương

- **Mã tài liệu:** `G2-REPO-APPLY-CHK-003`
- **Nhiệm vụ thực thi:** `G2-REPO-APPLY` (*Controlled Governance Update, Evidence Registry Remediation & Final Gate Verification*)
- **Ngày thực hiện:** `2026-10-16`
- **Công cụ được nâng cấp:** [`tools/check_working_tree_consistency.py`](../../tools/check_working_tree_consistency.py)
- **Sổ đăng ký bằng chứng:** [`EVIDENCE_DELIVERABLE_REGISTER.json`](EVIDENCE_DELIVERABLE_REGISTER.json)
- **Bộ kiểm thử hồi quy:** [`tools/qa/test_working_tree_registry_regression.py`](../../tools/qa/test_working_tree_registry_regression.py)
- **Trạng thái Gate G2 Chính thức:** **`IN_PROGRESS / NOT_PASSED`** *(Readiness: `AWAITING_FINAL_HUMAN_GATE_SIGNOFF`)*

---

## 1. Phân tích Nguyên nhân Gốc rễ Lỗi Trước Khi Khắc phục (`Root Cause of Prior 86 PASS, 2 FAIL`)

Trước khi thực hiện `G2-REPO-APPLY`, khi chạy lệnh `python tools/check_working_tree_consistency.py` ở Phase 0, công cụ trả về **Exit Code `1` (`86 PASS, 2 FAIL`)** với 2 lỗi:
1. `[FAIL] No unrecognized stray files in working-tree`
2. `[FAIL] All extra working-tree files cleanly accounted for`

**Nguyên nhân gốc rễ (`Root Cause`):**
- Phiên bản cũ của [`tools/check_working_tree_consistency.py`](../../tools/check_working_tree_consistency.py) (bản sao lưu tại [`G2_REPO_APPLY_BACKUPS/tools__check_working_tree_consistency.py.pre_g2_repo_apply.bak`](G2_REPO_APPLY_BACKUPS/tools__check_working_tree_consistency.py.pre_g2_repo_apply.bak)) sử dụng một tập hợp tĩnh `allowed_evidence_files` được mã hóa cứng (`hardcoded set`) chỉ bao gồm các tệp bằng chứng từ `T-001` đến `T-004`.
- Khi các nhiệm vụ hợp lệ sau `T-004` (`T-005 R2`, `T-005 R2.1`, `G2-FINAL-REVIEW`, `G2-R1`, `G2-SIGNOFF-PREP`, `G2-SIGNOFF-PRECHECK`, `G2-SIGNOFF-HANDOFF-FIX`) xuất bản 22 tệp bằng chứng Markdown vào thư mục `docs/05-evidence/`, tập mã hóa cứng không nhận diện được các tệp này và đánh dấu nhầm là tệp rác (`stray files`).
- Ngoài ra, phiên bản cũ kiểm tra cứng cả 47 tệp trong [`PACKAGE_MANIFEST.json`](../../PACKAGE_MANIFEST.json) (chỉ trừ duy nhất `PROJECT_STATE.md`), dẫn tới việc nếu cập nhật các tài liệu quản trị sống được phê duyệt (`DECISIONS.md`, `BACKLOG.md`, `KPI_SPEC.md`, `RISK_REGISTER.md`, `AI_HANDOFF.md`, `TASK_TEMPLATE.md`, `CHANGELOG.md`) mà không sửa [`PACKAGE_MANIFEST.json`](../../PACKAGE_MANIFEST.json) thì cần có một cơ chế đối chiếu bản sao lưu tiền cập nhật (`pre-change backup`) đối với [`PACKAGE_MANIFEST.json`](../../PACKAGE_MANIFEST.json) và xác thực mã băm SHA-256 của bản hiện hành.

---

## 2. Thiết kế Cơ chế Xác thực Dựa trên Sổ Đăng ký Bằng chứng (`Deliverable Registry Architecture`)

Theo đúng yêu cầu của Project Lead tại Mục 5 (`Phase 3 — Working-Tree Consistency Checker Remediation`), chúng tôi **tuyệt đối không** dùng bộ lọc ký tự đại diện mù (`blind wildcard/glob ignore`) và **không** vô hiệu hóa kiểm tra đối với tệp lạ. Thay vào đó, công cụ [`tools/check_working_tree_consistency.py`](../../tools/check_working_tree_consistency.py) được nâng cấp để đọc sổ đăng ký có cấu trúc [`EVIDENCE_DELIVERABLE_REGISTER.json`](EVIDENCE_DELIVERABLE_REGISTER.json).

### 2.1. Cấu trúc Schema của `EVIDENCE_DELIVERABLE_REGISTER.json`
Sổ đăng ký [`EVIDENCE_DELIVERABLE_REGISTER.json`](EVIDENCE_DELIVERABLE_REGISTER.json) gồm hai khối kiểm soát mật mã học:
1. **`governed_living_docs`**:
   - Ghi nhận 7 tài liệu quản trị sống thuộc [`PACKAGE_MANIFEST.json`](../../PACKAGE_MANIFEST.json) được phép cập nhật có kiểm soát trong `G2-REPO-APPLY` (`DECISIONS.md`, `AI_HANDOFF.md`, `TASK_TEMPLATE.md`, `BACKLOG.md`, `KPI_SPEC.md`, `RISK_REGISTER.md`, `CHANGELOG.md`).
   - Với mỗi tệp, công cụ kiểm tra đồng thời **hai chiều**:
     - **Chiều bảo toàn lịch sử (`Baseline Backup Verification`):** Tệp sao lưu `backup_path` trong `docs/05-evidence/G2_REPO_APPLY_BACKUPS/` phải tồn tại và có kích thước byte + mã băm SHA-256 **khớp tuyệt đối 100%** với `original_v1_1_bytes` và `original_v1_1_sha256` trong [`PACKAGE_MANIFEST.json`](../../PACKAGE_MANIFEST.json) v1.1.
     - **Chiều toàn vẹn hiện hành (`Current State Verification`):** Tệp hiện hành trên đĩa phải khớp tuyệt đối 100% với `current_bytes` và `current_sha256` đã đăng ký.
   - Toàn bộ 39 tệp tĩnh còn lại trong [`PACKAGE_MANIFEST.json`](../../PACKAGE_MANIFEST.json) (không kể `PROJECT_STATE.md` và 7 tệp `governed_living_docs`) tiếp tục được kiểm tra khớp trực tiếp byte-for-byte với [`PACKAGE_MANIFEST.json`](../../PACKAGE_MANIFEST.json).
2. **`registered_deliverables`**:
   - Danh sách tường minh từng tệp bằng chứng, dữ liệu kiểm thử, bản sao lưu và kịch bản QA ngoài [`PACKAGE_MANIFEST.json`](../../PACKAGE_MANIFEST.json) và [`inputs/SOURCE_MANIFEST.json`](inputs/SOURCE_MANIFEST.json).
   - Mỗi mục bắt buộc có đủ 6 trường:
     - `path`: Đường dẫn tương đối chuẩn hóa POSIX.
     - `task_id`: Mã nhiệm vụ hợp lệ (`T-001`, `T-002`, `T-003`, `T-004`, `T-005`, `G2-FINAL-REVIEW`, `G2-R1`, `G2-SIGNOFF-PREP`, `G2-SIGNOFF-PRECHECK`, `G2-SIGNOFF-HANDOFF-FIX`, `G2-REPO-APPLY`).
     - `artifact_type`: Phân loại hợp lệ (`AUDIT_REPORT`, `TEST_FIXTURE`, `QA_SCRIPT`, `AUDIT_SCRIPT`, `GOVERNANCE_PACKAGE`, `PRE_CHANGE_BACKUP`).
     - `bytes`: Kích thước byte chính xác (`> 0`).
     - `sha256`: Mã băm SHA-256 gồm 64 ký tự hex viết thường.
     - `authorization_ref`: Chuỗi tham chiếu thẩm quyền phê duyệt hợp lệ (`non-empty string`).

### 2.2. Các Luật Chặn Bảo mật & Toàn vẹn trong `tools/check_working_tree_consistency.py`
1. **Chặn leo thang đường dẫn (`Path Traversal Prevention`):** Mọi đường dẫn bắt đầu bằng `/`, `\`, chứa `..`, hoặc nằm ngoài `docs/05-evidence/` và `tools/` đều bị đánh dấu `[FAIL]` ngay lập tức.
2. **Chặn phần mở rộng nguy hiểm/ngoài phạm vi:** Chỉ cho phép các phần mở rộng `.md`, `.json`, `.csv`, `.py`, `.bak`, `.txt`. Các tệp `.pt`, `.parquet`, `.pkl`, `.exe`, `.tmp`, `.bak2`, v.v. bị từ chối.
3. **Chặn mục đăng ký trùng lặp (`Duplicate Path Detection`)** và **chặn mục đăng ký ma (`Missing Registered File Detection`)**.
4. **Kiểm tra khớp kích thước byte và SHA-256 (`Cryptographic Hash & Size Match`)** trên toàn bộ tệp đã đăng ký.
5. **Chặn tệp lạ chưa đăng ký (`Unregistered Stray File Rejection`):** Mọi tệp xuất hiện trong working-tree mà không thuộc [`PACKAGE_MANIFEST.json`](../../PACKAGE_MANIFEST.json), [`inputs/SOURCE_MANIFEST.json`](inputs/SOURCE_MANIFEST.json), hoặc [`EVIDENCE_DELIVERABLE_REGISTER.json`](EVIDENCE_DELIVERABLE_REGISTER.json) đều làm công cụ trả về `Exit Code 1`.

---

## 3. Ma trận Kiểm thử Hồi quy Tự động (`POS-01..02` & `NEG-01..08`)

Bộ kiểm thử tự động [`tools/qa/test_working_tree_registry_regression.py`](../../tools/qa/test_working_tree_registry_regression.py) tạo môi trường sao chép cô lập trong thư mục tạm (`tempfile.mkdtemp`) — **không bao giờ chạm vào kho mã nguồn thật** — và thực thi **10 kịch bản kiểm thử bắt buộc**:

| Mã kịch bản | Loại kiểm thử | Mô tả tình huống mô phỏng trên kho mã nguồn tạm (`Isolated Temp Fixture`) | Kỳ vọng kết quả Checker | Kết quả thực tế |
|---|---:|---|---:|---:|
| **`POS-01`** | Dương tính (`Positive`) | Đăng ký thêm một tệp bằng chứng mới hợp lệ (`T005_SYNTHETIC_POS01_CHECK.md`) với đúng kích thước và SHA-256 | `0 FAIL` (`Accepted`) | **`PASS`** |
| **`POS-02`** | Dương tính (`Positive`) | Toàn bộ 13 tệp bất biến trong [`inputs/SOURCE_MANIFEST.json`](inputs/SOURCE_MANIFEST.json), 47 tệp gốc trong [`PACKAGE_MANIFEST.json`](../../PACKAGE_MANIFEST.json) (cùng 7 bản sao lưu đối chứng) và 75 tệp đã đăng ký được xác thực thành công | `0 FAIL` (`255 PASS`) | **`PASS`** |
| **`NEG-01`** | Âm tính (`Negative`) | Tạo thêm một tệp lạ chưa đăng ký (`UNREGISTERED_STRAY_NOTE.md`) trong `docs/05-evidence/` | `FAIL` (Từ chối tệp lạ) | **`PASS`** |
| **`NEG-02`** | Âm tính (`Negative`) | Tạo tệp có tiền tố hợp lệ (`T005_UNREGISTERED_LOOKALIKE.md`) nhưng không đăng ký trong `EVIDENCE_DELIVERABLE_REGISTER.json` | `FAIL` (Từ chối tệp chưa đăng ký) | **`PASS`** |
| **`NEG-03`** | Âm tính (`Negative`) | Sửa đổi nội dung của một tệp đã đăng ký (`T005_FINAL_AUDIT_RECONCILIATION.md`) gây lệch mã băm SHA-256 | `FAIL` (Lệch SHA-256) | **`PASS`** |
| **`NEG-04`** | Âm tính (`Negative`) | Xóa một tệp đã đăng ký khỏi đĩa hoặc làm sai lệch trường `bytes` trong sổ đăng ký | `FAIL` (Thiếu tệp / lệch byte size) | **`PASS`** |
| **`NEG-05`** | Âm tính (`Negative`) | Làm hỏng cú pháp JSON của sổ đăng ký hoặc chèn mục đăng ký trùng lặp đường dẫn (`duplicate path`) | `FAIL` (Lỗi JSON / trùng lặp) | **`PASS`** |
| **`NEG-06`** | Âm tính (`Negative`) | Chèn đường dẫn leo thang thư mục (`../outside_secret.md`) vào sổ đăng ký | `FAIL` (Chặn path traversal) | **`PASS`** |
| **`NEG-07`** | Âm tính (`Negative`) | Đăng ký tệp có phần mở rộng bị cấm (`.pt`) hoặc mã nhiệm vụ giả mạo (`T-999`) | `FAIL` (Chặn `.pt` và `T-999`) | **`PASS`** |
| **`NEG-08`** | Âm tính (`Negative`) | Sửa đổi trái phép tệp bất biến (`docs/05-evidence/inputs/data_inventory.md`) thuộc [`inputs/SOURCE_MANIFEST.json`](inputs/SOURCE_MANIFEST.json) hoặc tệp `README.md` thuộc [`PACKAGE_MANIFEST.json`](../../PACKAGE_MANIFEST.json) | `FAIL` (Không thể qua mặt manifest gốc) | **`PASS`** |

---

## 4. Kết quả Thực thi Lệnh Kiểm tra & Số lượng Assertion (`Execution Results`)

| Lệnh thực thi | Exit Code | Tổng kết Assertion | Ghi chú xác minh |
|---|---:|---|---|
| `python tools/qa/verify_t003_contract_consistency.py` | **`0`** | **`96 PASS, 0 FAIL`** | Đạt 100% kiểm tra hợp đồng KPI, `FIX-14`, biên cực trị và trạng thái cổng G2. |
| `python tools/qa/verify_t004_time_representation.py` | **`0`** | **`90 PASS, 0 FAIL`** | Đạt 100% kiểm tra biểu diễn thời gian, `TF-01..09`, `OR-05` và trạng thái cổng G2. |
| `python tools/check_working_tree_consistency.py` | **`0`** | **`255 PASS, 0 FAIL`** | Đạt 100% kiểm tra cấu trúc tài liệu, liên kết Markdown, 13 tệp `SOURCE_MANIFEST.json`, 47 tệp `PACKAGE_MANIFEST.json` (gồm 7 `governed_living_docs`) và 75 tệp đã đăng ký trong `EVIDENCE_DELIVERABLE_REGISTER.json`. |
| `python tools/qa/test_working_tree_registry_regression.py` | **`0`** | **`10 PASS, 0 FAIL`** | Đạt 100% trên cả 2 kịch bản dương tính (`POS-01..02`) và 8 kịch bản âm tính (`NEG-01..08`). |
