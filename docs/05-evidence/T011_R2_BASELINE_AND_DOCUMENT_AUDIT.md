# T011_R2_BASELINE_AND_DOCUMENT_AUDIT — Biên bản Kiểm toán Tài liệu Chuẩn tắc và Baseline T011-R2

**Dự án:** Phân tích Hiệu suất Bay Hoa Kỳ 2016–2024 (US Flight Performance Analysis 2016–2024)  
**Nhiệm vụ:** `T-011 R2 — Targeted Parity Hardening and Evidence Correction`  
**Cổng quản trị cha:** `Gate G5 (IN_PROGRESS)` | **Cổng hạ nguồn:** `Gate G6 (NOT_STARTED / BLOCKED)`  
**Thời điểm kiểm toán:** `2026-10-19T12:55:00+07:00`  
**Thẩm quyền thực thi:** Master Prompt T011-R2 do Project Lead trực tiếp ban hành  
**Trạng thái cổng nội bộ Gate R2-0:** **`PASS`**

---

## 1. THÔNG SỐ VÀ TRẠNG THÁI BASELINE GIT

| Thông số | Giá trị thực tế ghi nhận | Ghi chú kiểm toán |
|---|---|---|
| **Git Baseline Commit (HEAD)** | `bc4f03fb8ccd6c0b2455af3fcb2b1b98fa39d632` | Trùng khớp baseline chuẩn tắc |
| **Git Active Branch** | `master` | Nhánh làm việc chính thức |
| **Gói kiểm toán tiền nhiệm** | `T011_R1_REVIEW_PACKAGE.zip` | Kích thước: `1,985,883 bytes`, SHA-256: `b8062442e5a9dba99103063a9f57440009edf5206e75e379c38059225efdcaec` |
| **Gói T011 gốc** | `T011_REVIEW_PACKAGE.zip` | Kích thước: `192,978 bytes` (bảo toàn nguyên vẹn, không ghi đè) |
| **Bảo vệ dữ liệu thô (`data/raw/`)** | `15,196,366,173 bytes` trên 9 tệp CSV | 0 byte bị thay đổi, mtime nguyên vẹn |

---

## 2. XÁC THỰC CÁC CHUẨN TẮC VÀ ĐIỀU KIỆN QUẢN TRỊ HIỆN HÀNH

Theo chỉ thị Master Prompt T011-R2, toàn bộ các quyết định và trạng thái chuẩn tắc sau được duy trì nguyên vẹn:
1. **Các Gate đã nghiệm thu chính thức:**
   - Gate G2 = `PASS` (theo [`G2_OFFICIAL_SIGNOFF_HUMAN_ACCEPTANCE_RECORD.md`](G2_OFFICIAL_SIGNOFF_HUMAN_ACCEPTANCE_RECORD.md))
   - Gate G3 = `PASS` (theo [`G3_OFFICIAL_SIGNOFF_HUMAN_ACCEPTANCE_RECORD.md`](G3_OFFICIAL_SIGNOFF_HUMAN_ACCEPTANCE_RECORD.md))
   - Gate G4 = `PASS (CONTROLLED)` (theo [`G4_OFFICIAL_HUMAN_SIGNOFF_20261018.md`](G4_OFFICIAL_HUMAN_SIGNOFF_20261018.md))
   - Task T-009 = `PASS (Controlled)`
   - Task T-007 = `PASS / COMPLETED (CONTROLLED)` (theo [`T007_HUMAN_SIGNOFF_20261018.md`](T007_HUMAN_SIGNOFF_20261018.md))
   - Task T-008 = `PASS / COMPLETED (CONTROLLED)` (theo [`T008_HUMAN_SIGNOFF_20261018.md`](T008_HUMAN_SIGNOFF_20261018.md))
   - Task T-010 = `PASS / COMPLETED (CONTROLLED)` (theo [`T010_HUMAN_SIGNOFF_20261018.md`](T010_HUMAN_SIGNOFF_20261018.md))
2. **Trạng thái cổng và nhiệm vụ đang thực hiện:**
   - Gate G5 = `IN_PROGRESS`
   - Task T-011 = `R2_TECHNICAL_CORRECTIONS_IN_PROGRESS` (chưa nghiệm thu chính thức)
   - Gate G6 = `NOT_STARTED / BLOCKED` (tiếp tục bị chặn cứng cho đến khi hoàn tất đối chiếu BTS thực tế)
3. **Các điều kiện ràng buộc đặc biệt:**
   - **`G2-EXC-001`:** Đơn vị 7 trường số đo CORE (`ARR_DELAY`, `DEP_DELAY`, `TAXI_OUT`, `TAXI_IN`, `AIR_TIME`, `ACTUAL_ELAPSED_TIME`, `CRS_ELAPSED_TIME`) giữ nhãn `PROVISIONAL`; bắt buộc `TS-018` đạt đối chiếu thực tế trước khi mở G6.
   - **`OR-05`:** Khuyết tật chất lượng mở năm 2024 (`OPEN_QUALITY_DEFECT`, chỉ có `335/366` ngày, vắng mặt 31 ngày Tháng 3/2024); `source_coverage_status = PARTIAL`.
   - **`OR-08`:** Candidate SHA-256 cho 9 CSV thô giữ `CANDIDATE_PENDING_HUMAN_ACCEPTANCE` (`IDENTITY_UNVERIFIED`).
   - **`FP-DEC-017`:** Thời tiết giữ nguyên trạng thái `CONDITIONAL_NO_GO`, không chặn luồng CORE.
   - **`G3-COND-A/B/C`:** Giữ nguyên các rào chắn sản xuất (không tự động whole-record quarantine chuyến bay số không dương, vị từ số học runtime, xuất bản an toàn NTFS).

---

## 3. BẢNG KIỂM TOÁN TÀI LIỆU CHUẨN TẮC TOÀN DIỆN (READING ATTESTATION)

Toàn bộ các tài liệu cốt lõi đã được đọc và kiểm chứng không tóm tắt, không cắt xén:

| STT | Đường dẫn tài liệu | Kích thước (bytes) | SHA-256 Digest | Trạng thái đọc | Ràng buộc quản trị liên quan |
|---|---|:---:|---|:---:|---|
| 1 | `README.md` | 13,293 | `5cf438ef9bcf278149eb0cb1e6a188be96d744f4d2f1f50a86b9789178be884a` | READ_VERIFIED | Khung dự án Big Data mô tả 2016–2024 |
| 2 | `AGENTS.md` | 3,923 | `dc0835f11eb77583769c0dfb6c6b3e6484e03df03289069d7ca194a282f6e520` | READ_VERIFIED | Quy tắc ứng xử AI: bất biến raw, fail-closed |
| 3 | `START_HERE.md` | 5,556 | `3d51787c93e43343a411546747b0e1215bb1c586144e5d440ad81ec01804f8fc` | READ_VERIFIED | Hướng dẫn khởi động và cây thư mục |
| 4 | `PACKAGE_MANIFEST.json` | 8,354 | `7c457207a6fefd2a45ad56a4c8ee8e3fb6194b8462f6ee24985f4e9534d61df1` | READ_VERIFIED | Manifest ghim cứng 47 file gốc docs-v1.1 |
| 5 | `docs/00-governance/DOCUMENT_REGISTER.md` | 8,024 | `3ecf349c25da73d42125f448c5e62fba2df894981e4b9d5cbf239f67a29e4b7b` | READ_VERIFIED | Sổ đăng ký vai trò tài liệu quản trị |
| 6 | `docs/01-planning/PRD.md` | 18,179 | `a5fbc406981cfef14b434c442438ea2f65a127a3c7ddaeec6d8fbfe6e2730da1` | READ_VERIFIED | Yêu cầu sản phẩm, RQ-01..05 và câu hỏi nghiên cứu |
| 7 | `docs/01-planning/ROADMAP.md` | 9,879 | `915e7f12e84c98f99335a14d5fb5aa0a911eb35777dfa8baef350c26ae776369` | READ_VERIFIED | Lộ trình các cổng Gate G0 đến G7 |
| 8 | `docs/01-planning/BACKLOG.md` | 13,411 | `fc29cb5743b177d6118b760a95786f4a25b169871587a840e69a03975ba524a8` | READ_VERIFIED | Tiêu chí hoàn thành (DoD) T-011 và các task |
| 9 | `docs/02-design/ARCHITECTURE.md` | 32,580 | `4ee163c431411261cb404746654a938c426210fec603e8cbb62c72b22ecf707f` | READ_VERIFIED | Thiết kế PySpark, SafePublisher và 2-phase writer |
| 10 | `docs/02-design/API_CONTRACTS.md` | 10,757 | `8ca2e5eeebf2f5349e5d4cb05ca006e86481977a455a2cbe7c390632d43d1a49` | READ_VERIFIED | Hợp đồng giao diện pipeline và CLI |
| 11 | `docs/02-design/DATA_CONTRACT.md` | 16,845 | `27fcab33ba16aa5a3ba25be692bcfdbe68469be408aa43034b0713b6e828453d` | READ_VERIFIED | DC-01..12: schema 34 cột, disjoint row accounting |
| 12 | `docs/02-design/DATA_DICTIONARY.md` | 16,368 | `efbfe6ba2c5f111dd954845a7201c7fb391fb1779cf107a688a24558eec131ce` | READ_VERIFIED | Từ điển dữ liệu 34 cột thô và 17 cột KPI |
| 13 | `docs/02-design/DECISIONS.md` | 21,647 | `bede7f51e95a832bd24dd6ceb51e4eb72a0fb6d9d3efc5a97fc4bc7642d0e66d` | READ_VERIFIED | Quyết định đã duyệt: FP-DEC-001..017, G2-EXC-001 |
| 14 | `docs/02-design/KPI_SPEC.md` | 9,949 | `bf4a663485c6416a790e1ca1d721f1da808fa9da61dc1e377b52b4ef04121d9c` | READ_VERIFIED | Đặc tả 8 CORE KPIs, công thức, mẫu số độc lập |
| 15 | `docs/02-design/ANALYSIS_PROTOCOL.md` | 14,082 | `cbdb9fe79203923c6f05e3a893cb6fb0f507e155bc8b981d3ea74720619e0777` | READ_VERIFIED | Giao thức phân tích hồi cứu mô tả |
| 16 | `docs/03-quality/TEST_PLAN.md` | 24,930 | `f28a381190bc93c3ccb467ec7e8f52281eb0aa84d1a43a8aa9f7d4a6f272c72b` | READ_VERIFIED | Kế hoạch kiểm thử TS-001..TS-020 |
| 17 | `docs/03-quality/RISK_REGISTER.md` | 11,376 | `55c5a46d682cfd5b0ec45d9d3f4d65c9adf4f513ad12a8dc0eae88af01fd2d85` | READ_VERIFIED | Sổ theo dõi rủi ro R-01..R-17 và OR-01..08 |
| 18 | `docs/03-quality/CHANGELOG.md` | 21,877 | `dbd5a0dbe13049b4d88e7b30c1e5509971a81dc2ee6f505e60882ef9ff827aa5` | READ_VERIFIED | Lịch sử thay đổi hệ thống và quản trị |
| 19 | `docs/03-quality/ROLLBACK_PLAN.md` | 8,973 | `0f0e0ca97d3cf26e4fb4b8f59d57a2c07090289fc542ba831e5f8f8c2b535d88` | READ_VERIFIED | Kế hoạch thu hồi không phá hủy trên Windows |
| 20 | `docs/03-quality/SECURITY.md` | 9,842 | `00155b1f9b3ec7025805561a355653b49704e9c70423c4a9a0891d120d58aa89` | READ_VERIFIED | Chính sách an toàn dữ liệu, chống rò rỉ secret |
| 21 | `docs/04-execution/PROJECT_STATE.md` | 39,423 | `b16cbb63e46c7504eb2023cb236ea2462e249495ca9b5d3a5ca1ae8e13e2f5f1` | READ_VERIFIED | Snapshot quản trị chính thức của toàn repository |
| 22 | `docs/04-execution/AI_HANDOFF.md` | 6,559 | `1cb5da70d3810ae11be98236d8d5df1fbaea1b5853bca51aa427be5d8525b410` | READ_VERIFIED | Giao thức chuyển giao giữa các agent AI |
| 23 | `docs/04-execution/TASK_TEMPLATE.md` | 3,923 | `810620bb5c382ea4ca170f3f22c83ff1c841369b0fa6dbf9b7c844111fe1e901` | READ_VERIFIED | Mẫu báo cáo nhiệm vụ chuẩn tắc |
| 24 | `docs/04-execution/DEPLOYMENT.md` | 9,788 | `668ba43e59549f7e7da2e783227eb5ebc8397a6e11467f37478d5236b3346d0e` | READ_VERIFIED | Đặc tả môi trường triển khai local PySpark |
| 25 | `docs/05-evidence/EVIDENCE_DELIVERABLE_REGISTER.json` | 219,303 | `032e5ce6c98679d40b4904bf77f1e63a32501a3575971dfa92e106d8a39e80e3` | READ_VERIFIED | Sổ đăng ký toàn bộ bằng chứng và mã băm SHA-256 |
| 26 | `docs/05-evidence/T011_R1_TS018_FAIL_CLOSED_AUDIT.md` | 13,858 | `d03a111a4cf4d5fc7d23d8c47ddf8aa8ec2f99f36f3ea83fb8b1fb3a7593c617` | READ_VERIFIED | Báo cáo R1 TS-018 tiền nhiệm |
| 27 | `docs/05-evidence/T011_R1_TS008_ACCURACY_RECONCILIATION.md` | 12,284 | `26b3ad3361110e527d4948a47427d14cbef6fb9e9fdb609f80cc29424e75618b` | READ_VERIFIED | Báo cáo R1 TS-008 Greenwald-Khanna tiền nhiệm |
| 28 | `docs/05-evidence/T011_R1_KPI_EDGE_CASE_AUDIT.md` | 12,886 | `2467ca67fe7e6c46927a7ff59828d15a5fef109b0270a6c25603ca5bb83c38fa` | READ_VERIFIED | Báo cáo R1 KPI edge case tiền nhiệm |
| 29 | `docs/05-evidence/T011_R1_MIN_N_AND_COVERAGE_AUDIT.md` | 12,504 | `7a177fe715e7144ee6bb6b3bbd2c1c911765c92c9f5636034177d9c0e5a6f2ea` | READ_VERIFIED | Báo cáo R1 min-N aliases tiền nhiệm |
| 30 | `docs/05-evidence/T011_R1_TS013_FAULT_INJECTION_AUDIT.md` | 14,089 | `84cb06450ccbe92f7ea89410313cb67d5eb45eaae021f196c34279b94ee095a5` | READ_VERIFIED | Báo cáo R1 TS-013 fault injection tiền nhiệm |

---

## 4. TỔNG HỢP 5 PHÁT HIỆN KIỂM TOÁN ĐỘC LẬP R2 CẦN KHẮC PHỤC

Kiểm toán viên độc lập sau khi xem xét gói nén `T011_R1_REVIEW_PACKAGE.zip` đã xác nhận 5 vấn đề kỹ thuật còn tồn đọng:

1. **R2-F01 — FALSE AUTHENTIC BTS PARITY:**
   - Script runner `tools/qa/run_ts018_bts_parity.py` phát hiện tệp có tên `bts_transtats_sample.csv` thì tự động gán `is_authentic = True` mà không qua xác minh xuất xứ (provenance validation).
   - Kiểm toán viên đã tái lập thành công: tạo 2 file CSV cục bộ với số liệu trùng khớp nhưng không có xuất xứ BTS thực tế, script vẫn trả về `TS018_PASS_AUTHENTIC_PARITY_ESTABLISHED`.
   - **Yêu cầu:** Phân tách rành mạch 5 trạng thái độc lập (`FILE_PRESENT`, `SCHEMA_VALID`, `SOURCE_PROVENANCE_VERIFIED`, `NUMERICAL_PARITY_VERIFIED`, `HUMAN_ACCEPTED`). Yêu cầu bản ghi siêu dữ liệu xuất xứ được phê duyệt bởi Project Lead; nếu thiếu thì trả về `PENDING/BLOCKED`.

2. **R2-F02 — INCOMPLETE SEVEN-FIELD VALIDATION:**
   - Mã nguồn xác định `has_numeric_evidence = (total_exact + total_rounding) > 0`, cho phép chỉ cần 1 trường số đo có giá trị khớp là thỏa mãn điều kiện toàn cục, trong khi 6 trường số đo còn lại hoàn toàn vắng mặt hoặc toàn null.
   - Hàm `rec.get()` âm thầm chuyển cột bị thiếu thành `None`, dẫn đến `NULL_NULL_AGREEMENT` giả mạo.
   - **Yêu cầu:** Xác minh rõ ràng sự tồn tại của cả 7 cột số đo trên cả hai phía. Phân biệt cột vắng mặt (`SCHEMA_MISSING_COLUMN`) với cột có mặt chứa null. Yêu cầu **mọi trường trong 7 trường số đo CORE** đều phải có quan sát số học độc lập (`numeric_sample_count > 0`) mới đủ điều kiện nghiệm thu chẵn lẻ chính thức.

3. **R2-F03 — COMPOSITE KEY VALIDATION:**
   - Sử dụng cú pháp `or` trong Python (`rec.get("OP_CARRIER_FL_NUM") or ...`) khiến số hiệu chuyến bay bằng `0` hoặc `0.0` bị coi là Falsy và bị bỏ rơi hoặc rơi vào alias khác.
   - Ngày bay rỗng (`""`) bị ghép cặp thành công giữa hai bản ghi cùng thiếu ngày.
   - Thiếu kiểm tra định dạng chuẩn ISO `YYYY-MM-DD` cho ngày bay, độ rỗng của hãng bay/sân bay.
   - **Yêu cầu:** Tra cứu alias dựa trên sự hiện diện của key và giá trị khác `None`. Bảo toàn số học `0` và `0.0`. Khóa composite key lỗi/rỗng không được phép tham gia so khớp.

4. **R2-F04 — FAULT INJECTION EVIDENCE REALISM:**
   - Kịch bản `F01` dùng hàm `open()` tích hợp của Python thay vì gọi giao diện nạp dữ liệu chính thức (`RawCsvReader` / `IngestionCoordinator`).
   - Kịch bản `F02` chỉ tiêm byte hỏng sau khi ghi chứ không kiểm thử lỗi trong quá trình ghi staging.
   - Kịch bản `F08` tự ý xóa khóa `stale_lock_file.unlink()` mà không tuân thủ giao thức `FAIL_CLOSED — MANUAL_RECOVERY_REQUIRED` của `locking.py`.
   - **Yêu cầu:** Nâng cấp F01, F02, F08 phản ánh đúng giao diện sản xuất và hợp đồng thu hồi khóa.

5. **R2-F05 — EVIDENCE AND REPORT ACCURACY:**
   - Báo cáo F06 nhầm lẫn giữa lỗi chuyển con trỏ (pointer switch failure) với lỗi nhả khóa sai chủ sở hữu (wrong-owner lock release).
   - Danh sách phân rã test modules trong báo cáo hồi quy chưa chuẩn hóa đúng 17 file module vật lý trong `tests/`.
   - **Yêu cầu:** Lập biên bản đính chính R2, ghi nhận chính xác 17 test modules và 217 unit tests thực tế.

---

## 5. KẾT LUẬN GATE R2-0

- **Điều kiện mở Gate R2-1:** ĐÃ THỎA MÃN.
- Toàn bộ tài liệu, cam kết an toàn, danh sách 5 phát hiện kiểm toán độc lập đã được làm rõ và đối chiếu đầy đủ.
- Tiến hành thực thi Gate R2-1: Lập bộ test tái lập các phản ví dụ R2-F01..F05.
