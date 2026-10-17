# G2_FINAL_FIX_TEST_AND_EXECUTION_MANIFEST — Bản Kê Thực Thi Kỹ Thuật, Đối Khớp Mã Băm & Thẩm Tra Bộ Kiểm Thử

**Mã tài liệu:** `G2_FINAL_FIX_TEST_AND_EXECUTION_MANIFEST`  
**Nhiệm vụ:** `G2-FINAL-FIX` (Targeted Corrections, Regression Verification & Final Human Sign-off Preparation)  
**Ngày thực hiện:** 2026-10-16  
**Thẩm quyền quyết định:** Project Lead đã phê duyệt chính thức qua chỉ thị nhiệm vụ các quyết định thiết kế Nhóm A–D và ngoại lệ `G2-EXC-001`.  
**Ranh giới kiểm soát cổng:** Project Lead **CHƯA phê duyệt Gate G2 PASS**. Trạng thái Gate G2 chính thức: **`IN_PROGRESS / NOT_PASSED`** (`AWAITING_FINAL_HUMAN_GATE_SIGNOFF`). Trạng thái nhiệm vụ **`T-006 = NOT_STARTED`**.  
**Dữ liệu thô:** Tuyệt đối không đọc/quét lại 54,674,003 dòng CSV thô, không chạy Spark production. 9 tệp CSV nguồn và các manifest lịch sử bất biến 100%.

---

## 1. Bản Kê Thay Đổi Tệp & Đối Khớp Mã Băm Trước / Sau Sửa Đổi (`Pre/Post Cryptographic Hash Ledger`)

### 1.1. Các Tệp Mã Nguồn & Công Cụ Được Sửa Đổi
| Đường dẫn tệp | Kích thước Trước (Bytes) | SHA-256 Trước | Kích thước Sau (Bytes) | SHA-256 Sau | Vị trí Bản sao lưu Phục hồi |
|---|---:|---|---:|---|---|
| [`tools/check_working_tree_consistency.py`](../../tools/check_working_tree_consistency.py) | 21,085 | `9b98051466113c0faa9da064aa1e9011e28d6d149e87afbe6bf82e17702e61ec` | 21,203 | `04bf0ce9c2354c46fbe47b74ea71fbba3b2a2491fa1a26d7f950669c5e7b57b9` | `docs/05-evidence/G2_FINAL_FIX_BACKUPS/tools__check_working_tree_consistency.py.pre_g2_final_fix.bak` |
| [`tools/qa/test_working_tree_registry_regression.py`](../../tools/qa/test_working_tree_registry_regression.py) | 20,762 | `b7a28ffaa2aebc873d9fa9379a36d1f50f9f6cbe21dc4eac0c9a10a0c4555a4a` | 25,541 | `5ae18c1e405a3064619d8544e45d94715ea011535a298be0408544d6735c3453` | `docs/05-evidence/G2_FINAL_FIX_BACKUPS/tools__qa__test_working_tree_registry_regression.py.pre_g2_final_fix.bak` |
| [`tools/qa/verify_g2_repo_apply_r1_semantic_invariants.py`](../../tools/qa/verify_g2_repo_apply_r1_semantic_invariants.py) | 25,504 | `766dd615f289a1722a4909390cc4d7ccea0820510584580ae1c3df3e7777a853` | 28,095 | `2f8fc0e6f1f462ebae61e6462725e1732e7f41f2249cf4516ff8363ba15b0aa2` | `docs/05-evidence/G2_FINAL_FIX_BACKUPS/tools__qa__verify_g2_repo_apply_r1_semantic_invariants.py.pre_g2_final_fix.bak` |

### 1.2. Các Báo Cáo Bằng Chứng Mới Được Tạo Lập
| Đường dẫn báo cáo bằng chứng | Loại Artifact | Kích thước (Bytes) | Mã Băm SHA-256 | Vai trò & Mục đích Nghiệm thu |
|---|---|---:|---|---|
| [`docs/05-evidence/G2_FINAL_FIX_CORRECTION_AND_SCOPE_REPORT.md`](G2_FINAL_FIX_CORRECTION_AND_SCOPE_REPORT.md) | `ERRATA_REPORT` | 17,193 | `3904ef7933d08e898dd0e9e3f0c9d1d4933eaf71e8a228355effdc576aaa27cb` | Báo cáo xử lý các phát hiện C-01..C-05, đính chính ngữ nghĩa TS-020 và 3 cấp độ phục hồi |
| [`docs/05-evidence/G2_FINAL_FIX_TEST_AND_EXECUTION_MANIFEST.md`](G2_FINAL_FIX_TEST_AND_EXECUTION_MANIFEST.md) | `EXECUTION_MANIFEST` | *(Tính toán tự động)* | *(Tính toán tự động)* | Bản kê thực thi kỹ thuật, đối khớp mã băm và kết quả chạy 5 bộ kiểm thử |
| [`docs/05-evidence/G2_FINAL_FIX_FINAL_GATE_RECOMMENDATION.md`](G2_FINAL_FIX_FINAL_GATE_RECOMMENDATION.md) | `GOVERNANCE_PACKAGE` | 11,583 | `a3a569d80b9f801d37fb4465133688f1d6aa17069f332cba02d3222f7d2369b7` | Khuyến nghị nghiệm thu Gate G2 cuối cùng gửi Project Lead |

### 1.3. Bất Biến Tuyệt Đối của Bản Kê Gốc & Dữ Liệu Nguồn
- **`PACKAGE_MANIFEST.json`:** `8,354 bytes`, SHA-256: `7c457207a6fefd2a45ad56a4c8ee8e3fb6194b8462f6ee24985f4e9534d61df1` (**Bất biến 100%**).
- **`docs/05-evidence/inputs/SOURCE_MANIFEST.json`:** `2,479 bytes`, SHA-256: `5e11e619790e475260b19c70630d8faef9a902c9d55d2ca641320163c87447fc` (**Bất biến 100%**).
- **9 tệp CSV nguồn (`data/raw/tabular/{year}/flight_with_weather_{year}.csv`):** Giữ nguyên vẹn, không truy cập ghi.

---

## 2. Kết Quả Thực Thi Thực Tế Của 5 Lệnh Kiểm Chứng Kỹ Thuật

Tất cả 5 bộ kiểm thử tự động đều được chạy thực tế từ thư mục gốc của repository (`D:\Study\Code\Apache\Flight_Analyzt\US_FLIGHT_PERFORMANCE_DOCS_V1`), sử dụng Python 3.10:

```powershell
# 1. Kiểm thử tính nhất quán hợp đồng dữ liệu T-003
python tools/qa/verify_t003_contract_consistency.py
# Kết quả: 133 PASS, 0 FAIL, 0 SKIP (Exit Code: 0)

# 2. Kiểm thử an toàn biểu diễn thời gian và cấu trúc T-004
python tools/qa/verify_t004_time_representation.py
# Kết quả: 90 PASS, 0 FAIL, 0 SKIP (Exit Code: 0)

# 3. Kiểm thử bất biến ngữ nghĩa và đột biến cô lập
python tools/qa/verify_g2_repo_apply_r1_semantic_invariants.py
# Kết quả: 15 semantic invariants PASS, 9 isolated mutations PASS, 0 FAIL, 0 SKIP (Exit Code: 0)

# 4. Kiểm thử hồi quy sổ đăng ký tự động (đã nâng cấp NEG-10A/B & mutations)
python tools/qa/test_working_tree_registry_regression.py
# Kết quả: 16 PASS, 0 FAIL, 0 SKIP (Exit Code: 0)

# 5. Kiểm tra toàn diện cây làm việc và đăng ký bằng chứng
python tools/check_working_tree_consistency.py
# Kết quả: ALL WORKING-TREE CHECKS PASSED, 0 FAIL (Exit Code: 0)
```

---

## 3. Xác Nhận Kiểm Tra Liên Kết Markdown & Mã Hóa UTF-8

- **Mã hóa:** Tất cả các tệp tài liệu và mã nguồn mới được lưu theo chuẩn UTF-8 không BOM.
- **Tính toàn vẹn liên kết Markdown:** Toàn bộ liên kết tương đối nội bộ giữa các tài liệu trong `docs/` đều được kiểm tra tính hợp lệ bằng công cụ kiểm tra cây làm việc `tools/check_working_tree_consistency.py`, đảm bảo không có bất kỳ liên kết hỏng (broken link) nào.

---

## 4. Trạng Thái Cổng và Bàn Giao

- **Gate G2:** **`IN_PROGRESS / NOT_PASSED`** (`AWAITING_FINAL_HUMAN_GATE_SIGNOFF`).
- **Nhiệm vụ T-006 (Gate G3):** **`NOT_STARTED`** (Bị khóa nghiêm ngặt; chờ Project Lead ra quyết định ký duyệt đóng Gate G2).
- **Trạng thái sẵn sàng:** **`READY_FOR_FINAL_HUMAN_G2_SIGNOFF`**.
