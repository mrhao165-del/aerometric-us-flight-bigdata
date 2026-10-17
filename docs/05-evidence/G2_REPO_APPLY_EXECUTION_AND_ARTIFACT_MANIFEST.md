# G2_REPO_APPLY_EXECUTION_AND_ARTIFACT_MANIFEST — Nhật ký Thực thi, Bảng Kê Kích thước/SHA-256 & Xác nhận Toàn vẹn Manifest Gate G2

- **Mã tài liệu:** `G2-REPO-APPLY-MAN-005`
- **Nhiệm vụ thực thi:** `G2-REPO-APPLY` (*Controlled Governance Update, Evidence Registry Remediation & Final Gate Verification*)
- **Ngày thực hiện:** `2026-10-16`
- **Trạng thái Gate G2 Chính thức:** **`IN_PROGRESS / NOT_PASSED`** *(Readiness Annotation: `AWAITING_FINAL_HUMAN_GATE_SIGNOFF`)*
- **Trạng thái Nhiệm vụ `T-006` (Gate G3):** **`NOT_STARTED`**

---

## 1. Snapshot Môi trường Thực thi (`Environment Snapshot`)

| Thông số môi trường | Giá trị ghi nhận thực tế |
|---|---|
| **Hệ điều hành (`OS`)** | Windows (`win32`, PowerShell) |
| **Thư mục làm việc (`Repo Root`)** | `D:\Study\Code\Apache\Flight_Analyzt\US_FLIGHT_PERFORMANCE_DOCS_V1` |
| **Trạng thái kho Git (`.git`)** | **Không khởi tạo (`.git exists = False`)** — Quản lý phiên bản và hoàn nguyên thông qua [`PACKAGE_MANIFEST.json`](../../PACKAGE_MANIFEST.json), [`inputs/SOURCE_MANIFEST.json`](inputs/SOURCE_MANIFEST.json), [`EVIDENCE_DELIVERABLE_REGISTER.json`](EVIDENCE_DELIVERABLE_REGISTER.json) và thư mục sao lưu nguyên bản [`G2_REPO_APPLY_BACKUPS/`](G2_REPO_APPLY_BACKUPS/). |
| **Phiên bản Python** | `Python 3.10.11` |
| **Thực thi PySpark / Quét CSV thô** | **Không thực thi (`NOT_RUN`)** — Đây là nhiệm vụ đồng bộ hóa quản trị, khắc phục công cụ kiểm tra và xác minh cổng tài liệu/QA. |

---

## 2. Nhật ký Lệnh Thực thi & Mã Thoát (`Commands Executed & Exit Codes`)

### 2.1. Kiểm tra Baseline Trước Khi Thay đổi (`Phase 0 Preflight Baseline`)
| STT | Lệnh thực thi | Exit Code | Kết quả ghi nhận |
|:---:|---|---:|---|
| 1 | `python tools/qa/verify_t003_contract_consistency.py` | `0` | `96 PASS, 0 FAIL` |
| 2 | `python tools/qa/verify_t004_time_representation.py` | `0` | `90 PASS, 0 FAIL` |
| 3 | `python tools/check_working_tree_consistency.py` *(phiên bản cũ trước khi khắc phục)* | `1` | `86 PASS, 2 FAIL` (Lỗi do 22 tệp bằng chứng hợp lệ sau `T-004` chưa có trong tập mã hóa cứng `allowed_evidence_files`). |

### 2.2. Kiểm tra Xác minh Toàn diện Sau Khi Áp dụng & Khắc phục (`Phase 4 Post-Apply Verification`)
| STT | Lệnh thực thi | Exit Code | Kết quả ghi nhận |
|:---:|---|---:|---|
| 1 | `python tools/qa/verify_t003_contract_consistency.py` | **`0`** | **`96 PASS, 0 FAIL`** (`ALL 96 T-003 CLOSEOUT CHECKS PASSED`) |
| 2 | `python tools/qa/verify_t004_time_representation.py` | **`0`** | **`90 PASS, 0 FAIL`** (`ALL 90 T-004 FINAL QA CHECKS PASSED`) |
| 3 | `python tools/check_working_tree_consistency.py` | **`0`** | **`255 PASS, 0 FAIL`** (`ALL WORKING-TREE CHECKS PASSED`) |
| 4 | `python tools/qa/test_working_tree_registry_regression.py` | **`0`** | **`10 PASS, 0 FAIL`** (`POS-01..POS-02` và `NEG-01..NEG-08` đạt 100% trên kho tạm cô lập) |

---

## 3. Bảng Kê Đầy đủ 9 Tệp Hiện Hữu Được Cập nhật (`Modified Existing Files`)

| STT | Đường dẫn tệp (`Relative Path`) | `pre_bytes` | `pre_sha256` | `post_bytes` | `post_sha256` | Tệp sao lưu nguyên bản (`Backup Path`) |
|:---:|---|---:|---|---:|---|---|
| 1 | [`docs/02-design/DECISIONS.md`](../02-design/DECISIONS.md) | `3,894` | `046ca0e627266815a1b9c17df49f6676f49c6b7e9aeb18bb6025740a56d8a180` | `18,567` | `3c9093aed0c028d15df0b6da001dba6a4ea7bde784b3bd655743f91e4f006ea3` | [`G2_REPO_APPLY_BACKUPS/docs__02-design__DECISIONS.md.pre_g2_repo_apply.bak`](G2_REPO_APPLY_BACKUPS/docs__02-design__DECISIONS.md.pre_g2_repo_apply.bak) |
| 2 | [`docs/04-execution/PROJECT_STATE.md`](../04-execution/PROJECT_STATE.md) | `6,148` | `5b803ec172155815b00e9370e3969789d8042c17785e02e5aa06750e1e647269` | `15,387` | `2efb4ef49f679a74f05b0742b9c68a0d020e6dfcc643f8a25a2e27264748b547` | [`G2_REPO_APPLY_BACKUPS/docs__04-execution__PROJECT_STATE.md.pre_g2_repo_apply.bak`](G2_REPO_APPLY_BACKUPS/docs__04-execution__PROJECT_STATE.md.pre_g2_repo_apply.bak) |
| 3 | [`docs/04-execution/AI_HANDOFF.md`](../04-execution/AI_HANDOFF.md) | `2,745` | `7bd3a3b376e13bfda0aed8ed95f1f625fa39cdc0f7ebf31ea5bb9df11df4ca69` | `12,686` | `a1151b479c95ccd408de2e2afa4dd4b761e712c0ba13dfacb5d99b17c800d5ff` | [`G2_REPO_APPLY_BACKUPS/docs__04-execution__AI_HANDOFF.md.pre_g2_repo_apply.bak`](G2_REPO_APPLY_BACKUPS/docs__04-execution__AI_HANDOFF.md.pre_g2_repo_apply.bak) |
| 4 | [`docs/04-execution/TASK_TEMPLATE.md`](../04-execution/TASK_TEMPLATE.md) | `1,764` | `47350b4b253b9ab3192404eceef87b40cbd9061c0093307ae749ed66f4bb8eb7` | `7,623` | `3271b673737518db3a46a286d6992a18edf193f58b517ec37ec03a4b5e2f2f26` | [`G2_REPO_APPLY_BACKUPS/docs__04-execution__TASK_TEMPLATE.md.pre_g2_repo_apply.bak`](G2_REPO_APPLY_BACKUPS/docs__04-execution__TASK_TEMPLATE.md.pre_g2_repo_apply.bak) |
| 5 | [`docs/01-planning/BACKLOG.md`](../01-planning/BACKLOG.md) | `5,026` | `6525a1735338f80c5a4ad1d4260cab1b43646a342799c8fb300f9db9adc787ed` | `9,344` | `16c38e9836910e353972fc1329f49f59e2c932b6271297cebf5d95673fed8a87` | [`G2_REPO_APPLY_BACKUPS/docs__01-planning__BACKLOG.md.pre_g2_repo_apply.bak`](G2_REPO_APPLY_BACKUPS/docs__01-planning__BACKLOG.md.pre_g2_repo_apply.bak) |
| 6 | [`docs/02-design/KPI_SPEC.md`](../02-design/KPI_SPEC.md) | `5,845` | `1972fca2c67288a76984fe1f9953752f77dd65262bee04ff1af942902e4a6dbe` | `8,703` | `c189df7a2d0843e7c8153185535bd5dcdef798381396be92b1bd00ffff8cf0ed` | [`G2_REPO_APPLY_BACKUPS/docs__02-design__KPI_SPEC.md.pre_g2_repo_apply.bak`](G2_REPO_APPLY_BACKUPS/docs__02-design__KPI_SPEC.md.pre_g2_repo_apply.bak) |
| 7 | [`docs/03-quality/RISK_REGISTER.md`](../03-quality/RISK_REGISTER.md) | `3,215` | `745c18d56f60173b6e41e102894bd968570650359a14c38aa1c620dc54cf12df` | `8,457` | `a08ee340d66ff5462ab33908a422b660f6ed033af64124f56f122af18c75a2f8` | [`G2_REPO_APPLY_BACKUPS/docs__03-quality__RISK_REGISTER.md.pre_g2_repo_apply.bak`](G2_REPO_APPLY_BACKUPS/docs__03-quality__RISK_REGISTER.md.pre_g2_repo_apply.bak) |
| 8 | [`docs/03-quality/CHANGELOG.md`](../03-quality/CHANGELOG.md) | `2,012` | `feb443581633193be978be9e587b3dbae8d4afd700dfc231c16fa73b021365f1` | `3,217` | `d687e6389e515f9845d0205bcf41496a7f024592a94a34149d9f1f9fbb0eda4e` | [`G2_REPO_APPLY_BACKUPS/docs__03-quality__CHANGELOG.md.pre_g2_repo_apply.bak`](G2_REPO_APPLY_BACKUPS/docs__03-quality__CHANGELOG.md.pre_g2_repo_apply.bak) |
| 9 | [`tools/check_working_tree_consistency.py`](../../tools/check_working_tree_consistency.py) | `8,688` | `acdc5911180a4f3672b51a5182d070ed8f72f868665f4ecc4f162c905ebc2a91` | `19,258` | `5fe26d6e072982a5c851cda519359ac3d2fa1eddbba5ec9ff19f020014ec8704` | [`G2_REPO_APPLY_BACKUPS/tools__check_working_tree_consistency.py.pre_g2_repo_apply.bak`](G2_REPO_APPLY_BACKUPS/tools__check_working_tree_consistency.py.pre_g2_repo_apply.bak) |

---

## 4. Bảng Kê Toàn bộ 16 Tệp Tạo Mới Trong `G2-REPO-APPLY` (`Newly Created Files`)

| STT | Đường dẫn tệp tạo mới (`Relative Path`) | Phân loại (`Category`) | Kích thước (`bytes`) | Mã băm `SHA-256` |
|:---:|---|---|---:|---|
| 1 | [`docs/05-evidence/G2_REPO_APPLY_HUMAN_APPROVAL_RECORD.md`](G2_REPO_APPLY_HUMAN_APPROVAL_RECORD.md) | `GOVERNANCE_PACKAGE` | `20,364` | `987b8889a6984c1abb95dfe80a4798e0c8019c6bd58527f8678ddbfb69fe55fc` |
| 2 | [`docs/05-evidence/G2_REPO_APPLY_GOVERNANCE_RECONCILIATION.md`](G2_REPO_APPLY_GOVERNANCE_RECONCILIATION.md) | `GOVERNANCE_PACKAGE` | `15,417` | `535cdb1f7d0cd3daa11e69401c850616531352cdd1b6295c15a7e27b36c664cc` |
| 3 | [`docs/05-evidence/G2_REPO_APPLY_CHECKER_AND_REGRESSION_REPORT.md`](G2_REPO_APPLY_CHECKER_AND_REGRESSION_REPORT.md) | `GOVERNANCE_PACKAGE` | `11,579` | `6ad3181f5393a27c7e2a7596a65541983061ac740f3331337c825bf663463e15` |
| 4 | [`docs/05-evidence/G2_REPO_APPLY_FINAL_GATE_READINESS.md`](G2_REPO_APPLY_FINAL_GATE_READINESS.md) | `GOVERNANCE_PACKAGE` | `10,676` | `4c31a7ca7ae58d5af5e28c530b908d7406b19878cbacabcafdb6b9f179a7a6ff` |
| 5 | [`docs/05-evidence/G2_REPO_APPLY_EXECUTION_AND_ARTIFACT_MANIFEST.md`](G2_REPO_APPLY_EXECUTION_AND_ARTIFACT_MANIFEST.md) | `governance_package` | *(Xem mục đăng ký trong `EVIDENCE_DELIVERABLE_REGISTER.json`)* | *(Tránh tự tham chiếu vòng tròn SHA-256; mã băm chính xác của tệp này được lưu và kiểm tra tự động trong `EVIDENCE_DELIVERABLE_REGISTER.json`)* |
| 6 | [`docs/05-evidence/EVIDENCE_DELIVERABLE_REGISTER.json`](EVIDENCE_DELIVERABLE_REGISTER.json) | `deliverable_registry` | *(Sổ đăng ký trung tâm)* | *(Được xác thực cấu trúc và đối chiếu với toàn bộ working-tree bởi `tools/check_working_tree_consistency.py`)* |
| 7 | [`tools/qa/test_working_tree_registry_regression.py`](../../tools/qa/test_working_tree_registry_regression.py) | `qa_script` | `16,150` | `68efd15ca851aff545ef6e613a7704d7ba34a105b5ad3059bc856daf6dc1f0e3` |
| 8 | [`docs/05-evidence/G2_REPO_APPLY_BACKUPS/docs__01-planning__BACKLOG.md.pre_g2_repo_apply.bak`](G2_REPO_APPLY_BACKUPS/docs__01-planning__BACKLOG.md.pre_g2_repo_apply.bak) | `pre_change_backup` | `5,026` | `6525a1735338f80c5a4ad1d4260cab1b43646a342799c8fb300f9db9adc787ed` |
| 9 | [`docs/05-evidence/G2_REPO_APPLY_BACKUPS/docs__02-design__DECISIONS.md.pre_g2_repo_apply.bak`](G2_REPO_APPLY_BACKUPS/docs__02-design__DECISIONS.md.pre_g2_repo_apply.bak) | `pre_change_backup` | `3,894` | `046ca0e627266815a1b9c17df49f6676f49c6b7e9aeb18bb6025740a56d8a180` |
| 10 | [`docs/05-evidence/G2_REPO_APPLY_BACKUPS/docs__02-design__KPI_SPEC.md.pre_g2_repo_apply.bak`](G2_REPO_APPLY_BACKUPS/docs__02-design__KPI_SPEC.md.pre_g2_repo_apply.bak) | `pre_change_backup` | `5,845` | `1972fca2c67288a76984fe1f9953752f77dd65262bee04ff1af942902e4a6dbe` |
| 11 | [`docs/05-evidence/G2_REPO_APPLY_BACKUPS/docs__03-quality__CHANGELOG.md.pre_g2_repo_apply.bak`](G2_REPO_APPLY_BACKUPS/docs__03-quality__CHANGELOG.md.pre_g2_repo_apply.bak) | `pre_change_backup` | `2,012` | `feb443581633193be978be9e587b3dbae8d4afd700dfc231c16fa73b021365f1` |
| 12 | [`docs/05-evidence/G2_REPO_APPLY_BACKUPS/docs__03-quality__RISK_REGISTER.md.pre_g2_repo_apply.bak`](G2_REPO_APPLY_BACKUPS/docs__03-quality__RISK_REGISTER.md.pre_g2_repo_apply.bak) | `pre_change_backup` | `3,215` | `745c18d56f60173b6e41e102894bd968570650359a14c38aa1c620dc54cf12df` |
| 13 | [`docs/05-evidence/G2_REPO_APPLY_BACKUPS/docs__04-execution__AI_HANDOFF.md.pre_g2_repo_apply.bak`](G2_REPO_APPLY_BACKUPS/docs__04-execution__AI_HANDOFF.md.pre_g2_repo_apply.bak) | `pre_change_backup` | `2,745` | `7bd3a3b376e13bfda0aed8ed95f1f625fa39cdc0f7ebf31ea5bb9df11df4ca69` |
| 14 | [`docs/05-evidence/G2_REPO_APPLY_BACKUPS/docs__04-execution__PROJECT_STATE.md.pre_g2_repo_apply.bak`](G2_REPO_APPLY_BACKUPS/docs__04-execution__PROJECT_STATE.md.pre_g2_repo_apply.bak) | `pre_change_backup` | `6,148` | `5b803ec172155815b00e9370e3969789d8042c17785e02e5aa06750e1e647269` |
| 15 | [`docs/05-evidence/G2_REPO_APPLY_BACKUPS/docs__04-execution__TASK_TEMPLATE.md.pre_g2_repo_apply.bak`](G2_REPO_APPLY_BACKUPS/docs__04-execution__TASK_TEMPLATE.md.pre_g2_repo_apply.bak) | `pre_change_backup` | `1,764` | `47350b4b253b9ab3192404eceef87b40cbd9061c0093307ae749ed66f4bb8eb7` |
| 16 | [`docs/05-evidence/G2_REPO_APPLY_BACKUPS/tools__check_working_tree_consistency.py.pre_g2_repo_apply.bak`](G2_REPO_APPLY_BACKUPS/tools__check_working_tree_consistency.py.pre_g2_repo_apply.bak) | `pre_change_backup` | `8,688` | `acdc5911180a4f3672b51a5182d070ed8f72f868665f4ecc4f162c905ebc2a91` |

---

## 5. Xác minh Tính Bất biến của `SOURCE_MANIFEST.json` & `PACKAGE_MANIFEST.json`

| Tệp Manifest Bất biến | Kích thước (`bytes`) | Mã băm `SHA-256` | Trạng thái kiểm định |
|---|---:|---|---:|
| [`PACKAGE_MANIFEST.json`](../../PACKAGE_MANIFEST.json) | `8,354` | `7c457207a6fefd2a45ad56a4c8ee8e3fb6194b8462f6ee24985f4e9534d61df1` | **`UNCHANGED_VERIFIED`** |
| [`docs/05-evidence/inputs/SOURCE_MANIFEST.json`](inputs/SOURCE_MANIFEST.json) | `2,479` | `5e11e619790e475260b19c70630d8faef9a902c9d55d2ca641320163c87447fc` | **`UNCHANGED_VERIFIED`** |

---

## 6. Quy trình Hoàn nguyên Tức thì (`Deterministic Rollback Procedure`)

Nếu cần hoàn nguyên kho tài liệu về trạng thái ngay trước `G2-REPO-APPLY`:
1. Sao chép đè 9 tệp `.pre_g2_repo_apply.bak` từ [`docs/05-evidence/G2_REPO_APPLY_BACKUPS/`](G2_REPO_APPLY_BACKUPS/) về đúng đường dẫn gốc tương ứng và kiểm tra lại mã băm SHA-256 khớp với cột `pre_sha256` ở Bảng 3.
2. Xóa 5 tệp `docs/05-evidence/G2_REPO_APPLY_*.md`, tệp [`docs/05-evidence/EVIDENCE_DELIVERABLE_REGISTER.json`](EVIDENCE_DELIVERABLE_REGISTER.json), kịch bản [`tools/qa/test_working_tree_registry_regression.py`](../../tools/qa/test_working_tree_registry_regression.py) và thư mục [`docs/05-evidence/G2_REPO_APPLY_BACKUPS/`](G2_REPO_APPLY_BACKUPS/).
