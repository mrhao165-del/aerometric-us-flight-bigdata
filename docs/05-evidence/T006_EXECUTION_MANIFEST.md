# T-006 DELIVERABLE E: EXECUTION & ARTIFACT MANIFEST

**Task ID:** `T-006`  
**Gate:** `G3`  
**Execution Type:** Big Data Architecture Design, Runtime Budgeting, QA Guard Transition & Governance Verification  
**Authorizing Context:** Project Lead direct instruction to kickoff Gate G3 / Task T-006 following G2-OFFICIAL-SIGNOFF  
**Execution Timestamp:** 2026-10-17T02:35:00+07:00  
**Overall Verdict:** `T006_DESIGN_READY_FOR_HUMAN_REVIEW`  

---

## 1. Mục đích & Thẩm quyền Thực thi

Bản kê khai này lưu trữ bằng chứng kiểm toán độc lập về toàn bộ các thao tác kỹ thuật, các tệp tài liệu được tạo mới và cập nhật, các bản sao lưu khả nghịch, và kết quả kiểm thử thực tế của nhiệm vụ `T-006` (Gate G3).

---

## 2. Bảng Kê Khai Toàn bộ Tệp Tin Được Tạo mới & Sửa đổi

### 2.1. Các Deliverables Thiết kế Kiến trúc Mới Được Tạo (`docs/05-evidence/`)

| STT | Đường dẫn Tệp | Phân loại Artifact | Kích thước (bytes) | SHA-256 Checksum | Mục đích & Nội dung cốt lõi |
| :---: | :--- | :---: | :---: | :---: | :--- |
| 1 | `docs/05-evidence/T006_ARCHITECTURE_AND_RUNTIME_DESIGN.md` | `AUDIT_REPORT` | 16,991 | `c81ec84953238630ee270d77d2bbe0b2b5842304eda1baa95cd2d8c0c273bc5b` | Deliverable A: Sơ đồ kiến trúc, luồng dữ liệu, runtime PySpark 4.0 / Java 21, ngân sách bộ nhớ, Parquet layout. |
| 2 | `docs/05-evidence/T006_SCHEMA_QUALITY_AND_LINEAGE_DESIGN.md` | `AUDIT_REPORT` | 17,276 | `325dba248d7c1f94302881ba22868a4a97afdf05a465f9198fd2bb9cbae70a16` | Deliverable B: Ánh xạ chuẩn tắc 34 cột raw, schema Curated, 3 trạng thái dòng (DC-11), an toàn thời gian, TS-020. |
| 3 | `docs/05-evidence/T006_KPI_AND_TEST_BLUEPRINT.md` | `AUDIT_REPORT` | 21,409 | `5258fac980e207ca6b5fb0ed1d6699f0062d21335d043c736651f6ed1d089345` | Deliverable C: Bản vẽ kỹ thuật 8 CORE KPIs (KPI-01..08), ngưỡng trễ <15/>=15, min-N, phân vị, ma trận TS-001..020. |
| 4 | `docs/05-evidence/T006_REVIEW_AND_GATE_REPORT.md` | `AUDIT_REPORT` | 10,884 | `de0c281969e2b7c1ac1bc784cc469c1c310543ea02829ace8790b9ed7d3e96c5` | Deliverable D: Báo cáo đánh giá mức độ sẵn sàng, checklist 21 tiêu chí, câu hỏi mở, rủi ro, khuyến nghị nghiệm thu. |
| 5 | `docs/05-evidence/T006_EXECUTION_MANIFEST.md` | `EXECUTION_MANIFEST` | *(Đăng ký trong sổ deliverables)* | *(Tự tham chiếu theo L-01)* | Deliverable E: Bảng kê khai chi tiết các tệp, kích thước, SHA-256, logs test và bằng chứng sao lưu khả nghịch. |

### 2.2. Các Tài liệu Quản trị Sống Được Cập nhật

| STT | Đường dẫn Tệp | Kích thước (bytes) | SHA-256 Checksum | Nội dung Cập nhật Chính |
| :---: | :--- | :---: | :---: | :--- |
| 1 | `docs/04-execution/PROJECT_STATE.md` | 19,473 | `e66d58238062d7b7a0499ef477ef6fe2a1e66fd6fa22c5e5ea38b357013dce96` | Chuyển T-006 = `IN_PROGRESS`, Gate G3 = `IN_PROGRESS / NOT_PASSED`, cập nhật Section 1, Section 2 và Section 5.2. |
| 2 | `docs/04-execution/AI_HANDOFF.md` | 16,712 | `7ba93e1184d15290dfbf6d280dad66ee3444516d9a7d2ba339c46500775b8277` | Cập nhật Mục 1: Gate G2 = `PASS`, Gate G3 = `IN_PROGRESS / NOT_PASSED`, T-006 = `IN_PROGRESS`, Downstream G4 = `NOT_STARTED`. |
| 3 | `docs/01-planning/BACKLOG.md` | 10,876 | `061b99283a795a73a5a90b3a41effd7198598de5f54cc44940149fc3a5ad8cdb` | Cập nhật trạng thái T-006 từ `TODO` sang `IN_PROGRESS`, các task G4 giữ nguyên `TODO`. |
| 4 | `docs/03-quality/CHANGELOG.md` | 7,373 | `22bc76598dffab5e65f26955515f904cd998ba3033a587c5905248b37f9771bc` | Thêm bản ghi phiên bản `docs-v1.1-g3-t006-kickoff` ghi nhận thiết kế kiến trúc và khởi động Gate G3. |
| 5 | `docs/02-design/ARCHITECTURE.md` | 17,479 | `a301611b01e7cee43d7dc27869d9628bcae79016d29dc1505e40ef5a7dfec587` | Nâng cấp toàn diện tài liệu thiết kế hệ thống sống: Mermaid pipeline, bảng luồng dữ liệu, runtime, ngân sách RAM, Parquet. |

### 2.3. Các Công cụ QA Được Nâng cấp

| STT | Đường dẫn Tệp | Kích thước (bytes) | SHA-256 Checksum | Cơ chế Bảo vệ Được Nâng cấp |
| :---: | :--- | :---: | :---: | :--- |
| 1 | `tools/check_working_tree_consistency.py` | 22,423 | `b8988b5e3b8802d7f145f94c0ff190171e7c424f3503fab8cdcaefe0d9fd90fd` | Hỗ trợ regex `T006_BACKUP_FILENAME_RE`, cho phép thư mục `T006_BACKUPS/`, thêm `ARCHITECTURE.md` vào `ALLOWED_GOVERNED_LIVING_DOCS`. |
| 2 | `tools/qa/verify_g2_repo_apply_r1_semantic_invariants.py` | 36,842 | `827eaccf41c93e8677ae207321fdb8687bc97003b9de4e2f8412ee956108c436` | Nâng cấp INV-12 xác thực có kiểm soát T-006 = `IN_PROGRESS`, cấm G3 = `PASS`, cấm khởi động sớm T-007..009; mở rộng đột biến `MUT-06A..C`. |

### 2.4. Danh mục Snapshot Sao lưu Khả nghịch (`docs/05-evidence/T006_BACKUPS/`)

| STT | Đường dẫn Snapshot | Kích thước (bytes) | SHA-256 Checksum | Tệp Nguồn Được Bảo vệ |
| :---: | :--- | :---: | :---: | :--- |
| 1 | `docs/05-evidence/T006_BACKUPS/docs__01-planning__BACKLOG.md.pre_t006.bak` | 10,757 | `aadaa304402c5f82fd015fbbfe0ad308ea43ceb3dafdb714116552f549a08a29` | `docs/01-planning/BACKLOG.md` |
| 2 | `docs/05-evidence/T006_BACKUPS/docs__02-design__ARCHITECTURE.md.pre_t006.bak` | 4,261 | `1f9d5ee4773fa62575813dbad60b6a77d4d63f3fab9dbb588b0e97dd4b6258e4` | `docs/02-design/ARCHITECTURE.md` (Khớp 100% v1.1) |
| 3 | `docs/05-evidence/T006_BACKUPS/docs__03-quality__CHANGELOG.md.pre_t006.bak` | 6,104 | `62ab79f10cfeae153622a25e75a99a734c088a2b8cc23a5501e51bbe07b89b26` | `docs/03-quality/CHANGELOG.md` |
| 4 | `docs/05-evidence/T006_BACKUPS/docs__04-execution__AI_HANDOFF.md.pre_t006.bak` | 16,494 | `3454d7e5fd05645b5aa5ad1a39eac2b9f85ecdffd8a5cf36a1255ad775502b88` | `docs/04-execution/AI_HANDOFF.md` |
| 5 | `docs/05-evidence/T006_BACKUPS/docs__04-execution__PROJECT_STATE.md.pre_t006.bak` | 19,199 | `32b71aecc221dc1991c5d518758257360e0f3c5616b2d82e93196dac0007a3d8` | `docs/04-execution/PROJECT_STATE.md` |
| 6 | `docs/05-evidence/T006_BACKUPS/docs__05-evidence__EVIDENCE_DELIVERABLE_REGISTER.json.pre_t006.bak` | 39,762 | `a759af2fa7d0ea5641e7090b2956f8160c5691a36ac8277634cfccd4e75f6e2a` | `docs/05-evidence/EVIDENCE_DELIVERABLE_REGISTER.json` |
| 7 | `docs/05-evidence/T006_BACKUPS/tools__check_working_tree_consistency.py.pre_t006.bak` | 22,143 | `3a8d897889f4ab6049cc1a081338792cb9c6399bdc3fb6c153ec711692f75387` | `tools/check_working_tree_consistency.py` |
| 8 | `docs/05-evidence/T006_BACKUPS/tools__qa__verify_g2_repo_apply_r1_semantic_invariants.py.pre_t006.bak` | 32,453 | `f95b0ff8784d90366266c80f5e6db2a1802f658f951b5c7af59376dc7e2a75c9` | `tools/qa/verify_g2_repo_apply_r1_semantic_invariants.py` |

---

## 3. Khảo sát & Quan trắc Môi trường Thực thi (Environment Observations)

* **Hệ điều hành:** Windows-10-10.0.19045-SP0 (AMD64)
* **Python Runtime:** Python 3.10.11 (tags/v3.10.11:7d4cc5a, Apr 5 2023)
* **Cores:** 8 physical cores, 16 logical cores
* **RAM:** 15.71 GiB tổng thể, khả dụng: ~5.72 GiB (Cấp phát tối đa cho Spark: 6–8 GiB)
* **Storage:**
  * Drive C:\: 154.9 GiB tổng, 27.2 GiB trống
  * **Drive D:\ (Project Drive):** 300.0 GiB tổng, **64.3 GiB trống**
* **Java:** OpenJDK 21.0.12.1 LTS (Eclipse Adoptium Temurin 64-bit)
* **Installed Packages:** PySpark `4.0.1`, PyArrow `25.0.1`, pandas `2.3.3`
* **Raw CSV Data:** 9 tệp CSV (2016–2024), tổng kích thước chính xác: **15,196,366,173 bytes** (~14.15 GiB), Read-Only.

---

## 4. Kết quả Thực thi Kiểm thử Tự động (Automated Verification Logs)

1. **`python tools/qa/verify_g2_repo_apply_r1_semantic_invariants.py`:**
   * **Exit Code:** `0`
   * **Invariants:** 15/15 PASS
   * **Mutations:** 14/14 PASS (bao gồm `MUT-05A..D` kiểm tra G2/G3 và `MUT-06A..C` kiểm tra ngăn chặn khởi động sớm T-006, T-009, T-007)
2. **`python tools/qa/verify_t003_contract_consistency.py`:**
   * **Exit Code:** `0`
   * **Kết quả:** 133/133 PASS
3. **`python tools/qa/verify_t004_time_representation.py`:**
   * **Exit Code:** `0`
   * **Kết quả:** 90/90 PASS
4. **`python tools/qa/test_working_tree_registry_regression.py`:**
   * **Exit Code:** `0`
   * **Kết quả:** 16/16 PASS (POS-01..02, NEG-01..10, MUT-NEG10-01..03)
5. **`python tools/check_working_tree_consistency.py`:**
   * **Exit Code:** `0`
   * **Kết quả:** PASS tuyệt đối, 0 FAIL

---

## 5. Trạng thái Quản trị Chuẩn tắc Sau Thực thi

* **Gate G2:** **`PASS`** (Phê duyệt chính thức bởi Project Lead ngày 2026-10-16)
* **Gate G3:** **`IN_PROGRESS / NOT_PASSED`** (Đang triển khai thiết kế; `G3 != PASS`)
* **Task T-006:** **`IN_PROGRESS`** (Đã hoàn thiện gói hồ sơ thiết kế A..E để trình duyệt)
* **Downstream Tasks (T-009, T-007, T-008):** **`NOT_STARTED` / `TODO`**
* **Downstream Gates (G4, G5, G6, G7):** **`PLANNED / NOT_STARTED`**

---

## 6. Tuyên bố Dừng Nghiêm ngặt (Strict Stop Statement)

Toàn bộ phạm vi công việc của Gate G3 / Nhiệm vụ `T-006` đã hoàn thành và sẵn sàng cho việc nghiệm thu của Project Lead.

Theo đúng quy định của `AGENTS.md`:
* **Hệ thống dừng mọi thao tác tiếp theo.**
* **TUYỆT ĐỐI KHÔNG tự ý khởi động Gate G4, không chạy Task T-009, T-007, T-008.**
* **TUYỆT ĐỐI KHÔNG tự ý tuyên bố Gate G3 đạt PASS.**
* **Chờ chỉ thị phê duyệt nghiệm thu từ Project Lead.**
