# G2_SIGNOFF_EXECUTION_AND_ARTIFACT_MANIFEST — Bảng Kê Hồ sơ Chuẩn bị Phê duyệt Quản trị & Bằng chứng Thực thi Gate G2

**Document ID:** `G2-SIGNOFF-MANIF-001`  
**Dự án:** Phân tích hiệu suất chuyến bay Hoa Kỳ 2016–2024 bằng Apache Spark / PySpark  
**Gate kiểm soát:** `Gate G2` (Data Understanding, Cohort, Units, Time Safety & Weather Usability Contracts)  
**Phạm vi:** Bảng kê chính thức các tệp tạo mới trong gói `G2-SIGNOFF-PREP`, mã băm SHA-256, dung lượng byte, danh mục tài liệu nguồn tham chiếu, nhật ký thực thi kiểm chứng và các giới hạn bằng chứng  
**Trạng thái tài liệu:** `GOVERNANCE_PREPARATION_PACKAGE / PENDING_HUMAN_APPROVAL`  
**Trạng thái Gate G2 hiện hành:** `IN_PROGRESS / NOT_PASSED`  
**Ngày lập:** 2026-10-16  

---

## 1. BẢNG KÊ CÁC TỆP TẠO MỚI TRONG GÓI `G2-SIGNOFF-PREP` (GENERATED ARTIFACTS REGISTRY)

Bốn tệp tài liệu Markdown dưới đây được tạo mới hoàn toàn trong thư mục [`docs/05-evidence/`](./) (không ghi đè bất kỳ tệp lịch sử hay tệp quản trị nào). Bảng dưới đây ghi nhận chính xác dung lượng byte và mã băm mật mã học SHA-256 của 3 báo cáo nội dung (tệp manifest thứ 4 không tự băm chính nó):

| STT | Tên tệp artifact | Đường dẫn tương đối từ Root | Dung lượng (Bytes) | Mã băm SHA-256 | Vai trò trong gói phê duyệt G2 |
|:---:|---|---|:---:|---|---|
| 1 | [`G2_SIGNOFF_DECISION_APPROVAL_MATRIX.md`](G2_SIGNOFF_DECISION_APPROVAL_MATRIX.md) | `docs/05-evidence/G2_SIGNOFF_DECISION_APPROVAL_MATRIX.md` | `48,247` | `37a15fdc0bb369d8d159a459540713baf6da860cdbf03a446ba758e4710b9774` | Đánh giá chi tiết 17 quyết định (`FP-DEC-001..016` & `FP-DEC-PROP-015` $\to$ `FP-DEC-017`). |
| 2 | [`G2_SIGNOFF_RESIDUAL_RISK_AND_CHANGE_PLAN.md`](G2_SIGNOFF_RESIDUAL_RISK_AND_CHANGE_PLAN.md) | `docs/05-evidence/G2_SIGNOFF_RESIDUAL_RISK_AND_CHANGE_PLAN.md` | `31,363` | `884457a7476d9d7dd756e74c181043d4c014bddaf93cd8e35f184c7174968e38` | Hiệu chỉnh 7 điểm tồn đọng (A–G), ánh xạ rủi ro `OR-01..08` $\leftrightarrow$ `R-01..17`, đặc tả nâng cấp checker có manifest và kế hoạch cập nhật tài liệu hậu ký duyệt. |
| 3 | [`G2_SIGNOFF_HUMAN_APPROVAL_RECORD_DRAFT.md`](G2_SIGNOFF_HUMAN_APPROVAL_RECORD_DRAFT.md) | `docs/05-evidence/G2_SIGNOFF_HUMAN_APPROVAL_RECORD_DRAFT.md` | `19,305` | `46555fd65f32e963f82d3a2a010d0dde22a7ca5c3f2418a451ba2cee402b505c` | Dự thảo biên bản phê duyệt dành cho Project Lead (để trống hoàn toàn các ô chọn và chữ ký). |
| 4 | [`G2_SIGNOFF_EXECUTION_AND_ARTIFACT_MANIFEST.md`](G2_SIGNOFF_EXECUTION_AND_ARTIFACT_MANIFEST.md) | `docs/05-evidence/G2_SIGNOFF_EXECUTION_AND_ARTIFACT_MANIFEST.md` | *(Self)* | *(Manifest file — not self-hashed)* | Bảng kê nguồn tham chiếu, nhật ký thực thi kiểm chứng và giới hạn bằng chứng của gói `G2-SIGNOFF-PREP`. |

---

## 2. DANH MỤC TÀI LIỆU NGUỒN THẨM QUYỀN ĐÃ ĐỌC VÀ ĐỐI CHIẾU (SOURCE REFERENCES)

Toàn bộ gói hồ sơ `G2-SIGNOFF-PREP` được xây dựng từ việc đọc trực tiếp các phiên bản hiện hành trên hệ thống tệp của repository:

1. **Tài liệu Quản trị, Kế hoạch & Hợp đồng (`docs-v1.1`):**
   - [`AGENTS.md`](../../AGENTS.md) & [`README.md`](../../README.md)
   - [`docs/04-execution/PROJECT_STATE.md`](../04-execution/PROJECT_STATE.md)
   - [`docs/04-execution/AI_HANDOFF.md`](../04-execution/AI_HANDOFF.md)
   - [`docs/04-execution/DEPLOYMENT.md`](../04-execution/DEPLOYMENT.md)
   - [`docs/04-execution/TASK_TEMPLATE.md`](../04-execution/TASK_TEMPLATE.md)
   - [`docs/01-planning/ROADMAP.md`](../01-planning/ROADMAP.md) & [`docs/01-planning/BACKLOG.md`](../01-planning/BACKLOG.md)
   - [`docs/02-design/DECISIONS.md`](../02-design/DECISIONS.md)
   - [`docs/02-design/DATA_CONTRACT.md`](../02-design/DATA_CONTRACT.md), [`docs/02-design/DATA_DICTIONARY.md`](../02-design/DATA_DICTIONARY.md), [`docs/02-design/KPI_SPEC.md`](../02-design/KPI_SPEC.md), [`docs/02-design/ANALYSIS_PROTOCOL.md`](../02-design/ANALYSIS_PROTOCOL.md)
   - [`docs/03-quality/TEST_PLAN.md`](../03-quality/TEST_PLAN.md) & [`docs/03-quality/RISK_REGISTER.md`](../03-quality/RISK_REGISTER.md)
2. **Hồ sơ Bằng chứng Nhiệm vụ (`T-001` đến `T-005`) và Rà soát `G2-R1`:**
   - **T-001:** [`T001_PROVENANCE_AUDIT.md`](T001_PROVENANCE_AUDIT.md), [`T001_R1_RECONCILIATION.md`](T001_R1_RECONCILIATION.md), [`T001_R2_FINAL_REVIEW.md`](T001_R2_FINAL_REVIEW.md).
   - **T-002:** [`T002_FLIGHT_GRAIN_AUDIT.md`](T002_FLIGHT_GRAIN_AUDIT.md), [`T002_DUPLICATE_ANALYSIS.md`](T002_DUPLICATE_ANALYSIS.md), [`T002_DENOMINATOR_RECOMMENDATION.md`](T002_DENOMINATOR_RECOMMENDATION.md), [`T002_R1_INDEPENDENT_REVIEW.md`](T002_R1_INDEPENDENT_REVIEW.md), [`T002_FINAL_ACCEPTANCE_CHECK.md`](T002_FINAL_ACCEPTANCE_CHECK.md).
   - **T-003:** [`T003_UNIT_VERIFICATION.md`](T003_UNIT_VERIFICATION.md), [`T003_KPI_CONTRACT_REVIEW.md`](T003_KPI_CONTRACT_REVIEW.md), [`T003_PERCENTILE_AND_MIN_N_DECISIONS.md`](T003_PERCENTILE_AND_MIN_N_DECISIONS.md), [`T003_TEST_FIXTURE_SPEC.md`](T003_TEST_FIXTURE_SPEC.md), [`T003_FIX14_accounting_fixture.csv`](T003_FIX14_accounting_fixture.csv), [`T003_FIX14_accounting_fixture.json`](T003_FIX14_accounting_fixture.json), [`T003_FINAL_CLOSEOUT_VERIFICATION.md`](T003_FINAL_CLOSEOUT_VERIFICATION.md), [`T003_SIGNOFF_RECORD.md`](T003_SIGNOFF_RECORD.md).
   - **T-004:** [`T004_TIME_REPRESENTATION_AUDIT.md`](T004_TIME_REPRESENTATION_AUDIT.md), [`T004_2024_DATE_COVERAGE_AUDIT.md`](T004_2024_DATE_COVERAGE_AUDIT.md), [`T004_OVERNIGHT_COUNTEREXAMPLES.md`](T004_OVERNIGHT_COUNTEREXAMPLES.md), [`T004_SAFE_FIELDS_DECISION.md`](T004_SAFE_FIELDS_DECISION.md), [`T004_TEST_FIXTURE_SPEC.md`](T004_TEST_FIXTURE_SPEC.md), [`T004_TF09_temporal_fixture.csv`](T004_TF09_temporal_fixture.csv), [`T004_TF09_full_schema_fixture.csv`](T004_TF09_full_schema_fixture.csv), [`T004_TF09_temporal_fixture.json`](T004_TF09_temporal_fixture.json), [`T004_FINAL_REVIEW.md`](T004_FINAL_REVIEW.md), [`T004_R1_INDEPENDENT_RECONCILIATION.md`](T004_R1_INDEPENDENT_RECONCILIATION.md), [`T004_FINAL_QA_RECONCILIATION.md`](T004_FINAL_QA_RECONCILIATION.md).
   - **T-005:** [`T005_FINAL_AUDIT_RECONCILIATION.md`](T005_FINAL_AUDIT_RECONCILIATION.md), [`T005_EVIDENCE_MATRIX.md`](T005_EVIDENCE_MATRIX.md), [`T005_TS011_TEST_SPEC.md`](T005_TS011_TEST_SPEC.md), [`T005_CONDITIONAL_NO_GO_PROPOSAL.md`](T005_CONDITIONAL_NO_GO_PROPOSAL.md), [`T005_EXECUTION_AND_FILE_MANIFEST.md`](T005_EXECUTION_AND_FILE_MANIFEST.md), [`T005_R2_1_REVIEWER_ADDENDUM.md`](T005_R2_1_REVIEWER_ADDENDUM.md), [`T005_R2_1_EVIDENCE_COMPLETENESS_CHECK.md`](T005_R2_1_EVIDENCE_COMPLETENESS_CHECK.md).
   - **G2-R1:** [`G2_R1_CRITICAL_FINDINGS_RECONCILIATION.md`](G2_R1_CRITICAL_FINDINGS_RECONCILIATION.md), [`G2_R1_TEST_AND_ASSERTION_AUDIT.md`](G2_R1_TEST_AND_ASSERTION_AUDIT.md), [`G2_R1_CORRECTED_GATE_READINESS.md`](G2_R1_CORRECTED_GATE_READINESS.md), [`G2_R1_EXECUTION_AND_ARTIFACT_MANIFEST.md`](G2_R1_EXECUTION_AND_ARTIFACT_MANIFEST.md).

---

## 3. NHẬT KÝ THỰC THI KIỂM CHỨNG HỆ THỐNG TỆP (EXECUTION & VERIFICATION LOG)

| STT | Hành động / Lệnh kiểm chứng | Thư mục làm việc (`Cwd`) | Exit Code | Kết quả thực tế ghi nhận |
|:---:|---|---|:---:|---|
| 1 | Kiểm tra tồn tại, đọc lại UTF-8, đo kích thước byte và tính SHA-256 của 4 tệp `G2_SIGNOFF_*` | `D:\Study\Code\Apache\Flight_Analyzt\US_FLIGHT_PERFORMANCE_DOCS_V1` | `0` | **PASS**: Cả 4 tệp tồn tại trên đĩa, dung lượng $>0$, UTF-8 hợp lệ 100%. |
| 2 | Kiểm tra phân giải toàn bộ liên kết tương đối Markdown trong 4 tệp `G2_SIGNOFF_*` | `D:\Study\Code\Apache\Flight_Analyzt\US_FLIGHT_PERFORMANCE_DOCS_V1` | `0` | **PASS**: `0` liên kết hỏng; toàn bộ đường dẫn `docs/...` đều trỏ tới tệp có thật trên đĩa. |
| 3 | `python tools/qa/verify_t004_time_representation.py` | `D:\Study\Code\Apache\Flight_Analyzt\US_FLIGHT_PERFORMANCE_DOCS_V1` | `0` | **`90 PASS, 0 FAIL`** (`VERIFIED_REPRODUCIBLE_IN_CURRENT_WORKTREE`). |
| 4 | `python tools/check_working_tree_consistency.py` *(chạy sau khi tạo đủ 4 tệp `G2_SIGNOFF_*`)* | `D:\Study\Code\Apache\Flight_Analyzt\US_FLIGHT_PERFORMANCE_DOCS_V1` | `1` | **`86 PASS, 2 FAIL`** (`FAILED_WITH_EXPLAINED_CAUSE` — xem chi tiết Mục 3.1 bên dưới). |

### 3.1. Chi tiết Kết quả Hiện thời của `tools/check_working_tree_consistency.py`
Khi chạy trực tiếp trên cây thư mục hiện hành (sau khi xuất đủ 4 tệp `G2_SIGNOFF_*`), kịch bản trả về:
- **86/86 assertion về cấu trúc tài liệu, liên kết Markdown, đường dẫn `docs/...`, manifest phát hành `PACKAGE_MANIFEST.json` (47 tệp), `SOURCE_MANIFEST.json` (13 tệp), và 9 tệp CSV thô:** **ĐỀU ĐẠT (`86 PASS`)**.
- **2 assertion báo `FAIL`:**
  1. `FAIL: No unrecognized stray files in working-tree`
  2. `FAIL: All extra working-tree files cleanly accounted for`
- **Tập hợp chính xác 18 tệp nằm trong thông báo `unrecognized` hiện tại:**
  - `7` tệp `T005_*`: `T005_CONDITIONAL_NO_GO_PROPOSAL.md`, `T005_EVIDENCE_MATRIX.md`, `T005_EXECUTION_AND_FILE_MANIFEST.md`, `T005_FINAL_AUDIT_RECONCILIATION.md`, `T005_R2_1_EVIDENCE_COMPLETENESS_CHECK.md`, `T005_R2_1_REVIEWER_ADDENDUM.md`, `T005_TS011_TEST_SPEC.md`.
  - `3` tệp `G2_*` (vòng đầu): `G2_DECISION_AND_BLOCKER_REGISTER.md`, `G2_EXECUTION_EVIDENCE_RECONCILIATION.md`, `G2_FINAL_GATE_READINESS_AUDIT.md`.
  - `4` tệp `G2_R1_*`: `G2_R1_CORRECTED_GATE_READINESS.md`, `G2_R1_CRITICAL_FINDINGS_RECONCILIATION.md`, `G2_R1_EXECUTION_AND_ARTIFACT_MANIFEST.md`, `G2_R1_TEST_AND_ASSERTION_AUDIT.md`.
  - `4` tệp `G2_SIGNOFF_*` (gói hiện tại): `G2_SIGNOFF_DECISION_APPROVAL_MATRIX.md`, `G2_SIGNOFF_RESIDUAL_RISK_AND_CHANGE_PLAN.md`, `G2_SIGNOFF_HUMAN_APPROVAL_RECORD_DRAFT.md`, `G2_SIGNOFF_EXECUTION_AND_ARTIFACT_MANIFEST.md`.
- **Cam kết trung thực:** Không che giấu lỗi, không tự ý chỉnh sửa `tools/check_working_tree_consistency.py` và không tuyên bố trước rằng bản vá tương lai sẽ mặc nhiên PASS trước khi được Project Lead cho phép triển khai và chạy kiểm thử thực tế.

---

## 4. GIỚI HẠN BẰNG CHỨNG VÀ TUÂN THỦ HỢP ĐỒNG AN TOÀN (EVIDENCE & SAFETY BOUNDARIES)

1. **Không có tệp hiện hữu nào bị sửa đổi:** Toàn bộ dữ liệu thô (`data/raw/`), mã nguồn/công cụ (`tools/`), manifest gốc (`PACKAGE_MANIFEST.json`, `SOURCE_MANIFEST.json`), tài liệu quản trị (`AGENTS.md`, `DECISIONS.md`, `PROJECT_STATE.md`, `BACKLOG.md`, `ROADMAP.md`, `DATA_CONTRACT.md`, `KPI_SPEC.md`, `TEST_PLAN.md`, `RISK_REGISTER.md`) và các báo cáo bằng chứng trước đó đều giữ nguyên 100% từng byte.
2. **Không có hiệu lực phê duyệt tự động:** Gói tài liệu `G2-SIGNOFF-PREP` chỉ là hồ sơ chuẩn bị trình duyệt (`PENDING_APPROVAL`). Gate G2 vẫn ở trạng thái **`IN_PROGRESS / NOT_PASSED`**.
3. **Trạng thái triển khai Runtime:** [`docs/04-execution/DEPLOYMENT.md`](../04-execution/DEPLOYMENT.md) vẫn giữ nguyên trạng thái **`NOT_READY / DOCUMENTATION ONLY`**. Chưa có pipeline PySpark nào được viết hoặc chạy.
4. **Điểm dừng bắt buộc (`STOP CONDITION`):** Nhiệm vụ `T-006` (Gate G3) tuyệt đối không được khởi động cho đến khi Project Lead ký xác nhận vào biên bản phê duyệt.
