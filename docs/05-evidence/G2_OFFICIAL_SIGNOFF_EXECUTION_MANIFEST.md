# G2_OFFICIAL_SIGNOFF_EXECUTION_MANIFEST — Bản Kê Thực Thi & Đối Soát Bằng Chứng Nghiệm Thu Gate G2

**Mã tài liệu:** `G2_OFFICIAL_SIGNOFF_EXECUTION_MANIFEST`  
**Mã nhiệm vụ:** `G2-OFFICIAL-SIGNOFF` (Controlled Human Gate Acceptance & Authorized State Transition)  
**Dự án:** Phân tích hiệu suất khai thác chuyến bay Hoa Kỳ 2016–2024 bằng Apache Spark / PySpark  
**Ngày thực hiện:** 2026-10-16  
**Thẩm quyền quyết định:** Quyết định phê duyệt bằng văn bản tường minh từ Project Lead ngày 2026-10-16 (`APPROVED_BY_PROJECT_LEAD_EXPLICIT_INSTRUCTION`), ghi nhận tại biên bản [`docs/05-evidence/G2_OFFICIAL_SIGNOFF_HUMAN_ACCEPTANCE_RECORD.md`](G2_OFFICIAL_SIGNOFF_HUMAN_ACCEPTANCE_RECORD.md).  
**Trạng thái Cổng chính thức:**  
- **Gate G2:** **`PASS`** (Đã đóng thành công).  
- **Gate G3:** **`PLANNED / NOT_PASSED`** (Cổng kế tiếp).  
- **Nhiệm vụ T-006:** **`NOT_STARTED`** (Điều kiện mở cổng **`T-006_ENTRY_GATE = SATISFIED`**).

---

## 1. Bảng Đối Soát Trạng Thái & Mã Băm Các Tài Liệu Quản Trị Sống Được Chỉnh Sửa

| STT | Đường dẫn Tài liệu Quản trị Sống | Kích thước Trước (`bytes`) | Mã băm SHA-256 Trước | Kích thước Sau (`bytes`) | Mã băm SHA-256 Sau | Tệp Sao Lưu Phục Hồi Trước Nhiệm Vụ |
|:---:|---|---:|---|---:|---|---|
| 1 | [`docs/04-execution/PROJECT_STATE.md`](../04-execution/PROJECT_STATE.md) | `18,599` | `11ef2bd24fdc280fa7560547c8ae40a8a3c9a394eabee69edcfd068ac9a40379` | `19,199` | `32b71aecc221dc1991c5d518758257360e0f3c5616b2d82e93196dac0007a3d8` | [`docs/05-evidence/G2_OFFICIAL_SIGNOFF_BACKUPS/docs__04-execution__PROJECT_STATE.md.pre_g2_official_signoff.bak`](G2_OFFICIAL_SIGNOFF_BACKUPS/docs__04-execution__PROJECT_STATE.md.pre_g2_official_signoff.bak) |
| 2 | [`docs/04-execution/AI_HANDOFF.md`](../04-execution/AI_HANDOFF.md) | `15,862` | `004a9c2cd96eb2aa51610bf684fbc3bb1165640d09b3aecf68d598f66d40fde7` | `16,494` | `3454d7e5fd05645b5aa5ad1a39eac2b9f85ecdffd8a5cf36a1255ad775502b88` | [`docs/05-evidence/G2_OFFICIAL_SIGNOFF_BACKUPS/docs__04-execution__AI_HANDOFF.md.pre_g2_official_signoff.bak`](G2_OFFICIAL_SIGNOFF_BACKUPS/docs__04-execution__AI_HANDOFF.md.pre_g2_official_signoff.bak) |
| 3 | [`docs/01-planning/BACKLOG.md`](../01-planning/BACKLOG.md) | `10,556` | `172760f42ac735e4d34f38c4c8f415f868b3381ffd8dac268ae0b17c2d685b4e` | `10,757` | `aadaa304402c5f82fd015fbbfe0ad308ea43ceb3dafdb714116552f549a08a29` | [`docs/05-evidence/G2_OFFICIAL_SIGNOFF_BACKUPS/docs__01-planning__BACKLOG.md.pre_g2_official_signoff.bak`](G2_OFFICIAL_SIGNOFF_BACKUPS/docs__01-planning__BACKLOG.md.pre_g2_official_signoff.bak) |
| 4 | [`docs/03-quality/CHANGELOG.md`](../03-quality/CHANGELOG.md) | `4,561` | `9a45e8fdde45a1b81e2cbc294231c3d18e9375c88179b0f359c1c45956da8cb1` | `6,104` | `62ab79f10cfeae153622a25e75a99a734c088a2b8cc23a5501e51bbe07b89b26` | [`docs/05-evidence/G2_OFFICIAL_SIGNOFF_BACKUPS/docs__03-quality__CHANGELOG.md.pre_g2_official_signoff.bak`](G2_OFFICIAL_SIGNOFF_BACKUPS/docs__03-quality__CHANGELOG.md.pre_g2_official_signoff.bak) |

---

## 2. Bảng Đối Soát Trạng Thái & Mã Băm Các Công Cụ Kiểm Tra Được Cập Nhật

| STT | Đường dẫn Công cụ / Bài Kiểm tra | Kích thước Trước (`bytes`) | Mã băm SHA-256 Trước | Kích thước Sau (`bytes`) | Mã băm SHA-256 Sau | Tệp Sao Lưu Phục Hồi Trước Nhiệm Vụ |
|:---:|---|---:|---|---:|---|---|
| 1 | [`tools/check_working_tree_consistency.py`](../../tools/check_working_tree_consistency.py) | `21,387` | `66f19c321b2164a916f2c41d1879e4af9996386dee0d12c40b6ec9c626dc52c1` | `22,143` | `3a8d897889f4ab6049cc1a081338792cb9c6399bdc3fb6c153ec711692f75387` | [`docs/05-evidence/G2_OFFICIAL_SIGNOFF_BACKUPS/tools__check_working_tree_consistency.py.pre_g2_official_signoff.bak`](G2_OFFICIAL_SIGNOFF_BACKUPS/tools__check_working_tree_consistency.py.pre_g2_official_signoff.bak) |
| 2 | [`tools/qa/verify_g2_repo_apply_r1_semantic_invariants.py`](../../tools/qa/verify_g2_repo_apply_r1_semantic_invariants.py) | `27,960` | `272f3ce963e31641551beffeaaf8dac11585ba48f74006a53f4ec231cd3f5f17` | `32,453` | `f95b0ff8784d90366266c80f5e6db2a1802f658f951b5c7af59376dc7e2a75c9` | [`docs/05-evidence/G2_OFFICIAL_SIGNOFF_BACKUPS/tools__qa__verify_g2_repo_apply_r1_semantic_invariants.py.pre_g2_official_signoff.bak`](G2_OFFICIAL_SIGNOFF_BACKUPS/tools__qa__verify_g2_repo_apply_r1_semantic_invariants.py.pre_g2_official_signoff.bak) |
| 3 | [`tools/qa/verify_t003_contract_consistency.py`](../../tools/qa/verify_t003_contract_consistency.py) | `20,788` | `b23f5710ce7c158803b16d5dc2f7244c4cc922d694869295c2c7494fde091820` | `21,527` | `e91286556d0eefe25a35a554f32bcc4cd507eb4dae0e08b7befe8e7f9183c833` | [`docs/05-evidence/G2_OFFICIAL_SIGNOFF_BACKUPS/tools__qa__verify_t003_contract_consistency.py.pre_g2_official_signoff.bak`](G2_OFFICIAL_SIGNOFF_BACKUPS/tools__qa__verify_t003_contract_consistency.py.pre_g2_official_signoff.bak) |
| 4 | [`tools/qa/verify_t004_time_representation.py`](../../tools/qa/verify_t004_time_representation.py) | `13,970` | `5adadd4d59302fac102afa13259d86b92e8c12069b1f6ceb1b80877aa85e6c4c` | `14,311` | `7712d1758c0e0459bd6335099b78051b76fae120bf45f413ec3b7507343092bf` | [`docs/05-evidence/G2_OFFICIAL_SIGNOFF_BACKUPS/tools__qa__verify_t004_time_representation.py.pre_g2_official_signoff.bak`](G2_OFFICIAL_SIGNOFF_BACKUPS/tools__qa__verify_t004_time_representation.py.pre_g2_official_signoff.bak) |

---

## 3. Bảng Kê Các Tệp Bằng Chứng Giao Phẩm Mới Tạo Lập

| STT | Đường dẫn Tệp Bằng Chứng Mới | Phân loại (`Artifact Type`) | Kích thước (`bytes`) | Mã băm `SHA-256` |
|:---:|---|---|---:|---|
| 1 | [`docs/05-evidence/G2_OFFICIAL_SIGNOFF_HUMAN_ACCEPTANCE_RECORD.md`](G2_OFFICIAL_SIGNOFF_HUMAN_ACCEPTANCE_RECORD.md) | `GOVERNANCE_PACKAGE` | `12,478` | `42c6131345069eac540337b6ca9cc0359219a051a8199f35fc29e158d58b95fc` |
| 2 | [`docs/05-evidence/G2_OFFICIAL_SIGNOFF_STATE_TRANSITION_REPORT.md`](G2_OFFICIAL_SIGNOFF_STATE_TRANSITION_REPORT.md) | `GOVERNANCE_PACKAGE` | `11,820` | `c7e85ce66b98c5fe3c0310c2d97a28fd816ad07c0dcac76c831d7fab764cc9bf` |
| 3 | [`docs/05-evidence/G2_OFFICIAL_SIGNOFF_EXECUTION_MANIFEST.md`](G2_OFFICIAL_SIGNOFF_EXECUTION_MANIFEST.md) | `EXECUTION_MANIFEST` | *(Đăng ký trong sổ deliverables)* | *(Tài liệu này)* |
| 4 | [`docs/05-evidence/G2_OFFICIAL_SIGNOFF_BACKUPS/docs__01-planning__BACKLOG.md.pre_g2_official_signoff.bak`](G2_OFFICIAL_SIGNOFF_BACKUPS/docs__01-planning__BACKLOG.md.pre_g2_official_signoff.bak) | `PRE_CHANGE_BACKUP` | `10,556` | `172760f42ac735e4d34f38c4c8f415f868b3381ffd8dac268ae0b17c2d685b4e` |
| 5 | [`docs/05-evidence/G2_OFFICIAL_SIGNOFF_BACKUPS/docs__03-quality__CHANGELOG.md.pre_g2_official_signoff.bak`](G2_OFFICIAL_SIGNOFF_BACKUPS/docs__03-quality__CHANGELOG.md.pre_g2_official_signoff.bak) | `PRE_CHANGE_BACKUP` | `4,561` | `9a45e8fdde45a1b81e2cbc294231c3d18e9375c88179b0f359c1c45956da8cb1` |
| 6 | [`docs/05-evidence/G2_OFFICIAL_SIGNOFF_BACKUPS/docs__04-execution__AI_HANDOFF.md.pre_g2_official_signoff.bak`](G2_OFFICIAL_SIGNOFF_BACKUPS/docs__04-execution__AI_HANDOFF.md.pre_g2_official_signoff.bak) | `PRE_CHANGE_BACKUP` | `15,862` | `004a9c2cd96eb2aa51610bf684fbc3bb1165640d09b3aecf68d598f66d40fde7` |
| 7 | [`docs/05-evidence/G2_OFFICIAL_SIGNOFF_BACKUPS/docs__04-execution__PROJECT_STATE.md.pre_g2_official_signoff.bak`](G2_OFFICIAL_SIGNOFF_BACKUPS/docs__04-execution__PROJECT_STATE.md.pre_g2_official_signoff.bak) | `PRE_CHANGE_BACKUP` | `18,599` | `11ef2bd24fdc280fa7560547c8ae40a8a3c9a394eabee69edcfd068ac9a40379` |
| 8 | [`docs/05-evidence/G2_OFFICIAL_SIGNOFF_BACKUPS/docs__05-evidence__EVIDENCE_DELIVERABLE_REGISTER.json.pre_g2_official_signoff.bak`](G2_OFFICIAL_SIGNOFF_BACKUPS/docs__05-evidence__EVIDENCE_DELIVERABLE_REGISTER.json.pre_g2_official_signoff.bak) | `PRE_CHANGE_BACKUP` | `34,394` | `9f926deee35d1e60cc797473166553af91ca2b50790ecb4d11bf268ceabaa131` |
| 9 | [`docs/05-evidence/G2_OFFICIAL_SIGNOFF_BACKUPS/tools__check_working_tree_consistency.py.pre_g2_official_signoff.bak`](G2_OFFICIAL_SIGNOFF_BACKUPS/tools__check_working_tree_consistency.py.pre_g2_official_signoff.bak) | `PRE_CHANGE_BACKUP` | `21,387` | `66f19c321b2164a916f2c41d1879e4af9996386dee0d12c40b6ec9c626dc52c1` |
| 10 | [`docs/05-evidence/G2_OFFICIAL_SIGNOFF_BACKUPS/tools__qa__verify_g2_repo_apply_r1_semantic_invariants.py.pre_g2_official_signoff.bak`](G2_OFFICIAL_SIGNOFF_BACKUPS/tools__qa__verify_g2_repo_apply_r1_semantic_invariants.py.pre_g2_official_signoff.bak) | `PRE_CHANGE_BACKUP` | `27,960` | `272f3ce963e31641551beffeaaf8dac11585ba48f74006a53f4ec231cd3f5f17` |
| 11 | [`docs/05-evidence/G2_OFFICIAL_SIGNOFF_BACKUPS/tools__qa__verify_t003_contract_consistency.py.pre_g2_official_signoff.bak`](G2_OFFICIAL_SIGNOFF_BACKUPS/tools__qa__verify_t003_contract_consistency.py.pre_g2_official_signoff.bak) | `PRE_CHANGE_BACKUP` | `20,788` | `b23f5710ce7c158803b16d5dc2f7244c4cc922d694869295c2c7494fde091820` |
| 12 | [`docs/05-evidence/G2_OFFICIAL_SIGNOFF_BACKUPS/tools__qa__verify_t004_time_representation.py.pre_g2_official_signoff.bak`](G2_OFFICIAL_SIGNOFF_BACKUPS/tools__qa__verify_t004_time_representation.py.pre_g2_official_signoff.bak) | `PRE_CHANGE_BACKUP` | `13,970` | `5adadd4d59302fac102afa13259d86b92e8c12069b1f6ceb1b80877aa85e6c4c` |

---

## 4. Kiểm Định Tính Bất Biến Của Manifest Lịch Sử

| Tệp Manifest Lịch Sử Bất Biến | Kích thước Yêu cầu (`bytes`) | Mã băm SHA-256 Ghim cứng | Trạng thái Thực tế |
|---|---:|---|:---:|
| [`PACKAGE_MANIFEST.json`](../../PACKAGE_MANIFEST.json) | `8,354` | `7c457207a6fefd2a45ad56a4c8ee8e3fb6194b8462f6ee24985f4e9534d61df1` | **`UNCHANGED_VERIFIED`** |
| [`docs/05-evidence/inputs/SOURCE_MANIFEST.json`](inputs/SOURCE_MANIFEST.json) | `2,479` | `5e11e619790e475260b19c70630d8faef9a902c9d55d2ca641320163c87447fc` | **`UNCHANGED_VERIFIED`** |

---

## 5. Kết Quả Thực Thi Toàn Bộ 5 Bộ Kiểm Thử Chuẩn Tắc

```powershell
# 1. Kiểm thử tính nhất quán hợp đồng dữ liệu T-003
python tools/qa/verify_t003_contract_consistency.py
# Exit Code: 0 | Kết quả: 133 PASS, 0 FAIL

# 2. Kiểm thử an toàn biểu diễn thời gian và cấu trúc T-004
python tools/qa/verify_t004_time_representation.py
# Exit Code: 0 | Kết quả: 90 PASS, 0 FAIL

# 3. Kiểm thử bất biến ngữ nghĩa chốt chặn G2 PASS & 12 ca đột biến cô lập
python tools/qa/verify_g2_repo_apply_r1_semantic_invariants.py
# Exit Code: 0 | Kết quả: 15 Invariants PASS, 12 Mutation Tests PASS (MUT-01..09, gồm MUT-05A..D)

# 4. Kiểm thử hồi quy sổ đăng ký tự động
python tools/qa/test_working_tree_registry_regression.py
# Exit Code: 0 | Kết quả: 16 PASS, 0 FAIL, 0 SKIP (POS-01..02, NEG-01..10B, MUT-NEG10-01..03)

# 5. Kiểm tra toàn diện tính nhất quán cây làm việc
python tools/check_working_tree_consistency.py
# Exit Code: 0 | Kết quả: 281 PASS assertions, 0 FAIL
```

---

## 6. Trạng Thái Khóa Quản Trị & Bàn Giao

- **Gate G2:** **`PASS`** (Chính thức được nghiệm thu theo chỉ thị của Project Lead).
- **Gate G3:** **`PLANNED / NOT_PASSED`** (Cổng kế tiếp).
- **Nhiệm vụ T-006:** **`NOT_STARTED`** (Điều kiện mở cổng **`T-006_ENTRY_GATE = SATISFIED`**).
- **Giới hạn chấp nhận:** `L-01` (export manifest self-hash) và `L-02` (rollback registry reconciliation) được ghi nhận đầy đủ.
- **Ràng buộc downstream:** `G2-EXC-001` (7 trường số đo mang nhãn `PROVISIONAL`, bắt buộc `TS-018` PASS ở G5 trước khi chạy G6), `OR-05` (thiếu Tháng 3/2024, `source_coverage_status = PARTIAL`), `OR-08` (`IDENTITY_UNVERIFIED`), `FP-DEC-017` (Weather CONDITIONAL_NO_GO), và các bài test bắt buộc G3–G6 tiếp tục ràng buộc nghiêm ngặt các cổng tiếp theo.
- **Dừng thực thi:** Tuyệt đối không khởi động `T-006` trong nhiệm vụ này.
