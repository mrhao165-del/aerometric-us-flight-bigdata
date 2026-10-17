# G2_REPO_APPLY_R1_EXECUTION_MANIFEST — Bản kê Khắc phục Ngữ nghĩa, Thẩm tra Mã nguồn & Thực thi Kiểm chứng

**Mã tài liệu:** `G2_REPO_APPLY_R1_EXECUTION_MANIFEST`  
**Nhiệm vụ:** `G2-REPO-APPLY-R1` (Targeted Semantic Regression Repair & Independent Code Verification)  
**Ngày thực hiện:** 2026-10-16  
**Thẩm quyền phê duyệt quyết định:** Project Lead đã phê duyệt chính thức qua chỉ thị nhiệm vụ (`APPROVED_BY_PROJECT_LEAD_INSTRUCTION` / `PROJECT_LEAD_EXPLICIT_INSTRUCTION_IN_TASK_PROMPT`) các quyết định thiết kế Nhóm A–D và ngoại lệ `G2-EXC-001`.  
**Ranh giới kiểm soát cổng:** Project Lead **CHƯA phê duyệt Gate G2 PASS**. Trạng thái Gate G2 chính thức: **`IN_PROGRESS / NOT_PASSED`** (`AWAITING_FINAL_HUMAN_GATE_SIGNOFF`). Trạng thái nhiệm vụ **`T-006 = NOT_STARTED`**.  
**Dữ liệu thô:** Tuyệt đối không đọc/quét lại 54,674,003 dòng hay chạy PySpark production. 9 tệp CSV nguồn và các tệp kiểm toán lịch sử bất biến 100%.

---

## 1. Bản kê Thay đổi Tệp Toàn diện (`Comprehensive File Inventory`)

### 1.1. Tài liệu Sống Được Phép Cập nhật (`Governed Living Documents`)
Tất cả 7 tài liệu sống được cập nhật đều có bản sao lưu v1.1 gốc đối khớp 100% byte và SHA-256 trong `docs/05-evidence/G2_REPO_APPLY_BACKUPS/`:

| Đường dẫn tài liệu | Kích thước v1.1 Gốc | SHA-256 v1.1 Gốc | Kích thước Sau R1 | SHA-256 Sau R1 (`G2-REPO-APPLY-R1`) | Bản sao lưu v1.1 Bảo tồn |
|---|---:|---|---:|---|---|
| [`docs/01-planning/BACKLOG.md`](../01-planning/BACKLOG.md) | 5,026 B | `6525a1735338f80c5a4ad1d4260cab1b43646a342799c8fb300f9db9adc787ed` | 10,556 B | `172760f42ac735e4d34f38c4c8f415f868b3381ffd8dac268ae0b17c2d685b4e` | `docs__01-planning__BACKLOG.md.pre_g2_repo_apply.bak` |
| [`docs/02-design/DECISIONS.md`](../02-design/DECISIONS.md) | 3,894 B | `046ca0e627266815a1b9c17df49f6676f49c6b7e9aeb18bb6025740a56d8a180` | 21,647 B | `bede7f51e95a832bd24dd6ceb51e4eb72a0fb6d9d3efc5a97fc4bc7642d0e66d` | `docs__02-design__DECISIONS.md.pre_g2_repo_apply.bak` |
| [`docs/02-design/KPI_SPEC.md`](../02-design/KPI_SPEC.md) | 5,845 B | `1972fca2c67288a76984fe1f9953752f77dd65262bee04ff1af942902e4a6dbe` | 9,949 B | `bf4a663485c6416a790e1ca1d721f1da808fa9da61dc1e377b52b4ef04121d9c` | `docs__02-design__KPI_SPEC.md.pre_g2_repo_apply.bak` |
| [`docs/03-quality/CHANGELOG.md`](../03-quality/CHANGELOG.md) | 2,012 B | `feb443581633193be978be9e587b3dbae8d4afd700dfc231c16fa73b021365f1` | 4,561 B | `9a45e8fdde45a1b81e2cbc294231c3d18e9375c88179b0f359c1c45956da8cb1` | `docs__03-quality__CHANGELOG.md.pre_g2_repo_apply.bak` |
| [`docs/03-quality/RISK_REGISTER.md`](../03-quality/RISK_REGISTER.md) | 3,215 B | `745c18d56f60173b6e41e102894bd968570650359a14c38aa1c620dc54cf12df` | 11,376 B | `55c5a46d682cfd5b0ec45d9d3f4d65c9adf4f513ad12a8dc0eae88af01fd2d85` | `docs__03-quality__RISK_REGISTER.md.pre_g2_repo_apply.bak` |
| [`docs/04-execution/AI_HANDOFF.md`](../04-execution/AI_HANDOFF.md) | 2,745 B | `7bd3a3b376e13bfda0aed8ed95f1f625fa39cdc0f7ebf31ea5bb9df11df4ca69` | 15,862 B | `004a9c2cd96eb2aa51610bf684fbc3bb1165640d09b3aecf68d598f66d40fde7` | `docs__04-execution__AI_HANDOFF.md.pre_g2_repo_apply.bak` |
| [`docs/04-execution/TASK_TEMPLATE.md`](../04-execution/TASK_TEMPLATE.md) | 1,764 B | `47350b4b253b9ab3192404eceef87b40cbd9061c0093307ae749ed66f4bb8eb7` | 8,445 B | `a0d0ae0059350a653ec17ce5b32400983f18f63687d1ffd43017b2abbb5faf91` | `docs__04-execution__TASK_TEMPLATE.md.pre_g2_repo_apply.bak` |

### 1.2. Snapshot Trạng thái Dự án (`Living Project State`)
| Đường dẫn tài liệu | Kích thước Sau R1 | SHA-256 Sau R1 | Trạng thái Gate G2 | Trạng thái T-006 |
|---|---:|---|:---:|:---:|
| [`docs/04-execution/PROJECT_STATE.md`](../04-execution/PROJECT_STATE.md) | 18,599 B | `11ef2bd24fdc280fa7560547c8ae40a8a3c9a394eabee69edcfd068ac9a40379` | `IN_PROGRESS / NOT_PASSED` | `NOT_STARTED` |

### 1.3. Công cụ & Bộ Kiểm thử Được Nâng cấp / Tạo Mới (`Tools & QA Suites`)
| Đường dẫn tệp | Loại Artifact | Kích thước | SHA-256 | Vai trò & Mục tiêu |
|---|---|---:|---|---|
| [`tools/check_working_tree_consistency.py`](../../tools/check_working_tree_consistency.py) | `QA_SCRIPT` | 21,085 B | `9b98051466113c0faa9da064aa1e9011e28d6d149e87afbe6bf82e17702e61ec` | Tăng cường ghim cứng mã băm manifest, kiểm soát `ALLOWED_GOVERNED_LIVING_DOCS`, `ALLOWED_ARTIFACT_TYPES` và cấm symlink |
| [`tools/qa/test_working_tree_registry_regression.py`](../../tools/qa/test_working_tree_registry_regression.py) | `QA_SCRIPT` | 20,762 B | `b7a28ffaa2aebc873d9fa9379a36d1f50f9f6cbe21dc4eac0c9a10a0c4555a4a` | Bộ kiểm thử hồi quy registry 12 ca (`POS-01..02`, `NEG-01..10`) |
| [`tools/qa/verify_g2_repo_apply_r1_semantic_invariants.py`](../../tools/qa/verify_g2_repo_apply_r1_semantic_invariants.py) | `AUTOMATED_VERIFICATION_SCRIPT` | 25,504 B | `766dd615f289a1722a4909390cc4d7ccea0820510584580ae1c3df3e7777a853` | Kiểm chứng tự động 14 bất biến ngữ nghĩa `R1-01..06` & 8 ca kiểm thử đột biến cô lập `MUT-01..08` |

### 1.4. Báo cáo Bằng chứng Mới Xuất bản thuộc `G2-REPO-APPLY-R1`
| Đường dẫn tệp bằng chứng | Loại Artifact | Kích thước | SHA-256 | Tình trạng Báo cáo Lịch sử |
|---|---|---:|---|---|
| [`docs/05-evidence/G2_REPO_APPLY_R1_SEMANTIC_ERRATA.md`](G2_REPO_APPLY_R1_SEMANTIC_ERRATA.md) | `ERRATA_REPORT` | 13,204 B | `34f1530260aa2c8c08828c4d93ccee0079e808d79bd87c47f17e0f02c832fb17` | Thay thế và vô hiệu hóa các sai lệch ngữ nghĩa trong 5 báo cáo `G2_REPO_APPLY_*.md` cũ (giữ nguyên tệp cũ trên đĩa) |
| [`docs/05-evidence/G2_REPO_APPLY_R1_CODE_AND_REGRESSION_AUDIT.md`](G2_REPO_APPLY_R1_CODE_AND_REGRESSION_AUDIT.md) | `CODE_AND_REGRESSION_AUDIT` | 11,839 B | `9cd87a65f0d48631bc614470c9cb1f3698de28fbe37d48e309558b59e2cc9004` | Báo cáo kiểm toán mã nguồn checker, ranh giới tin cậy, kết quả kiểm thử hồi quy và đột biến |
| [`docs/05-evidence/G2_REPO_APPLY_R1_EXECUTION_MANIFEST.md`](G2_REPO_APPLY_R1_EXECUTION_MANIFEST.md) | `EXECUTION_MANIFEST` | *(Tính sau khi ghi)* | *(Tính sau khi ghi)* | Bản kê thi hành kỹ thuật, đối khớp mã băm và quy trình phục hồi |

---

## 2. Lệnh Kiểm thử Đã Thực thi Thực tế & Exit Codes

Tất cả các lệnh kiểm thử đều được thực thi trực tiếp từ thư mục gốc repository, ghi nhận 100% đạt chuẩn `PASS`:

```powershell
# 1. Kiểm thử tính nhất quán hợp đồng dữ liệu T-003
python tools/qa/verify_t003_contract_consistency.py
# Exit Code: 0 (96 assertions PASS, 0 FAIL)

# 2. Kiểm thử an toàn biểu diễn thời gian và cấu trúc T-004
python tools/qa/verify_t004_time_representation.py
# Exit Code: 0 (90 assertions PASS, 0 FAIL)

# 3. Kiểm thử bất biến ngữ nghĩa R1-01..R1-06 & 8 ca đột biến cô lập
python tools/qa/verify_g2_repo_apply_r1_semantic_invariants.py
# Exit Code: 0 (14 semantic invariants PASS, 8 isolated mutation tests PASS)

# 4. Kiểm thử hồi quy sổ đăng ký tự động
python tools/qa/test_working_tree_registry_regression.py
# Exit Code: 0 (12 regression test cases PASS: POS-01..02, NEG-01..10)

# 5. Kiểm tra toàn diện cây làm việc và đăng ký bằng chứng
python tools/check_working_tree_consistency.py
# Exit Code: 0 (ALL WORKING-TREE CHECKS PASSED, 0 FAIL)
```

---

## 3. Quy trình Phục hồi và Bảo toàn Dữ liệu (`Rollback Procedures`)

1. **Bảo tồn dữ liệu thô:** Thư mục `data/raw/` không bị truy cập ghi, không bị sửa đổi hay xóa bỏ.
2. **Bảo tồn chứng tích lịch sử:** Cả 5 tệp `G2_REPO_APPLY_*.md` trước đó và 9 tệp sao lưu `.pre_g2_repo_apply.bak` được giữ nguyên vẹn 100% từng byte.
3. **Kịch bản phục hồi khẩn cấp:** Nếu cần hoàn tác toàn bộ bước `G2-REPO-APPLY-R1`, thực hiện:
   - Khôi phục 7 tài liệu sống từ `docs/05-evidence/G2_REPO_APPLY_BACKUPS/`.
   - Xóa bỏ các tệp mới `G2_REPO_APPLY_R1_*.md` và `tools/qa/verify_g2_repo_apply_r1_semantic_invariants.py`.
   - Khôi phục `tools/check_working_tree_consistency.py` và `EVIDENCE_DELIVERABLE_REGISTER.json` về trạng thái snapshot trước đó.

---

## 4. Xác nhận Khóa Trạng thái Gate G2 & Bàn giao (`Final Sign-off Status`)

- **Gate G2:** **`IN_PROGRESS / NOT_PASSED`** (`AWAITING_FINAL_HUMAN_GATE_SIGNOFF`).
- **Nhiệm vụ T-006 (Gate G3):** **`NOT_STARTED`** (Bị khóa nghiêm ngặt cho đến khi Project Lead ký nghiệm thu đóng Gate G2).
- **Trạng thái sẵn sàng:** **`READY_FOR_INDEPENDENT_FINAL_REVIEW`**. Toàn bộ sai lệch ngữ nghĩa đã được đính chính triệt để, mã nguồn công cụ và kiểm thử hồi quy đã được thẩm tra độc lập, và kho tài liệu hoàn toàn sẵn sàng cho quyết định phê duyệt cuối cùng của Project Lead.
