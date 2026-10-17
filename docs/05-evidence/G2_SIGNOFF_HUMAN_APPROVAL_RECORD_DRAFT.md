# G2_SIGNOFF_HUMAN_APPROVAL_RECORD_DRAFT — Dự thảo Biên bản Nghiệm thu và Phê duyệt Đóng Gate G2 Dành cho Project Lead

> **CẢNH BÁO HIỆU LỰC QUẢN TRỊ (GOVERNANCE LEGAL NOTICE):**  
> **TÀI LIỆU NÀY LÀ BẢN DỰ THẢO CHƯA ĐƯỢC KÝ DUYỆT (`UNSIGNED_DRAFT`).**  
> **BẢN DỰ THẢO CHƯA CÓ CHỮ KÝ KHÔNG MANG BẤT KỲ HIỆU LỰC PHÊ DUYỆT NÀO (`UNSIGNED RECORDS CONFER NO APPROVAL`).**  
> Không một ô lựa chọn nào được đánh dấu sẵn. Trạng thái của Gate G2 trong repository vẫn giữ nguyên là **`IN_PROGRESS / NOT_PASSED`**, các quyết định đề xuất vẫn giữ nguyên trạng thái **`PROPOSED`**, và nhiệm vụ **`T-006` (Gate G3) vẫn bị CẤM KHỞI ĐỘNG** cho đến khi Project Lead / Human Reviewer trực tiếp điền lựa chọn và ký xác nhận vào biên bản này.

---

## 1. ĐỊNH DANH DỰ ÁN VÀ CỔNG KIỂM SOÁT (PROJECT & GATE IDENTITY)

| Thuộc tính | Giá trị ghi nhận |
|---|---|
| **Tên dự án** | Phân tích Hiệu suất Chuyến bay Hoa Kỳ 2016–2024 bằng Apache Spark / PySpark (`US Flight Performance Analysis 2016–2024`) |
| **Bản chất nghiên cứu** | Phân tích mô tả hồi cứu dữ liệu lớn quan sát (*Observational / Descriptive Big Data Study*); loại trừ Machine Learning, dự báo T-2h riêng sân bay ATL, và đồ thị chuỗi bay `.pt` |
| **Cổng kiểm soát (Gate)** | **Gate G2 — Data Understanding, Cohort, Measure Units, Safe Time & Weather Usability Contracts** |
| **Mã biên bản** | `G2-SIGNOFF-REC-DRAFT-001` |
| **Phiên bản chuẩn tài liệu** | `docs-v1.1` (Baseline `2026-10-13`, kèm chuỗi bằng chứng kiểm toán `T-001..T-005`, `G2-R1`, `G2-SIGNOFF-PREP` ngày `2026-10-16`) |
| **Trạng thái Gate G2 trước khi ký** | **`IN_PROGRESS / NOT_PASSED`** |
| **Khuyến nghị của Đoàn Kiểm toán Độc lập** | **`READY_WITH_EXPLICIT_CONDITIONS`** |

---

## 2. DANH MỤC TÀI LIỆU THẨM QUYỀN VÀ PHIÊN BẢN BẰNG CHỨNG (AUTHORITATIVE EVIDENCE BASELINE)

Biên bản này căn cứ trực tiếp trên các tài liệu quy phạm và hồ sơ bằng chứng sau đây trong repository:
1. **Tài liệu Quản trị & Hợp đồng Cốt lõi (`docs-v1.1`):**
   - [`AGENTS.md`](../../AGENTS.md), [`README.md`](../../README.md), [`docs/04-execution/PROJECT_STATE.md`](../04-execution/PROJECT_STATE.md), [`docs/04-execution/AI_HANDOFF.md`](../04-execution/AI_HANDOFF.md), [`docs/04-execution/DEPLOYMENT.md`](../04-execution/DEPLOYMENT.md), [`docs/04-execution/TASK_TEMPLATE.md`](../04-execution/TASK_TEMPLATE.md).
   - [`docs/01-planning/ROADMAP.md`](../01-planning/ROADMAP.md), [`docs/01-planning/BACKLOG.md`](../01-planning/BACKLOG.md), [`docs/02-design/DECISIONS.md`](../02-design/DECISIONS.md).
   - [`docs/02-design/DATA_CONTRACT.md`](../02-design/DATA_CONTRACT.md), [`docs/02-design/DATA_DICTIONARY.md`](../02-design/DATA_DICTIONARY.md), [`docs/02-design/KPI_SPEC.md`](../02-design/KPI_SPEC.md), [`docs/02-design/ANALYSIS_PROTOCOL.md`](../02-design/ANALYSIS_PROTOCOL.md).
   - [`docs/03-quality/TEST_PLAN.md`](../03-quality/TEST_PLAN.md), [`docs/03-quality/RISK_REGISTER.md`](../03-quality/RISK_REGISTER.md).
2. **Hồ sơ Bằng chứng Nhiệm vụ Thành phần (`T-001` đến `T-005`):**
   - **T-001:** [`T001_PROVENANCE_AUDIT.md`](T001_PROVENANCE_AUDIT.md), [`T001_R1_RECONCILIATION.md`](T001_R1_RECONCILIATION.md), [`T001_R2_FINAL_REVIEW.md`](T001_R2_FINAL_REVIEW.md).
   - **T-002:** [`T002_FLIGHT_GRAIN_AUDIT.md`](T002_FLIGHT_GRAIN_AUDIT.md), [`T002_DUPLICATE_ANALYSIS.md`](T002_DUPLICATE_ANALYSIS.md), [`T002_DENOMINATOR_RECOMMENDATION.md`](T002_DENOMINATOR_RECOMMENDATION.md), [`T002_R1_INDEPENDENT_REVIEW.md`](T002_R1_INDEPENDENT_REVIEW.md), [`T002_FINAL_ACCEPTANCE_CHECK.md`](T002_FINAL_ACCEPTANCE_CHECK.md).
   - **T-003:** [`T003_UNIT_VERIFICATION.md`](T003_UNIT_VERIFICATION.md), [`T003_KPI_CONTRACT_REVIEW.md`](T003_KPI_CONTRACT_REVIEW.md), [`T003_PERCENTILE_AND_MIN_N_DECISIONS.md`](T003_PERCENTILE_AND_MIN_N_DECISIONS.md), [`T003_TEST_FIXTURE_SPEC.md`](T003_TEST_FIXTURE_SPEC.md), [`T003_FIX14_accounting_fixture.csv`](T003_FIX14_accounting_fixture.csv), [`T003_FIX14_accounting_fixture.json`](T003_FIX14_accounting_fixture.json), [`T003_FINAL_CLOSEOUT_VERIFICATION.md`](T003_FINAL_CLOSEOUT_VERIFICATION.md), [`T003_SIGNOFF_RECORD.md`](T003_SIGNOFF_RECORD.md).
   - **T-004:** [`T004_TIME_REPRESENTATION_AUDIT.md`](T004_TIME_REPRESENTATION_AUDIT.md), [`T004_2024_DATE_COVERAGE_AUDIT.md`](T004_2024_DATE_COVERAGE_AUDIT.md), [`T004_OVERNIGHT_COUNTEREXAMPLES.md`](T004_OVERNIGHT_COUNTEREXAMPLES.md), [`T004_SAFE_FIELDS_DECISION.md`](T004_SAFE_FIELDS_DECISION.md), [`T004_TEST_FIXTURE_SPEC.md`](T004_TEST_FIXTURE_SPEC.md), [`T004_TF09_temporal_fixture.csv`](T004_TF09_temporal_fixture.csv), [`T004_TF09_full_schema_fixture.csv`](T004_TF09_full_schema_fixture.csv), [`T004_TF09_temporal_fixture.json`](T004_TF09_temporal_fixture.json), [`T004_R1_INDEPENDENT_RECONCILIATION.md`](T004_R1_INDEPENDENT_RECONCILIATION.md), [`T004_FINAL_QA_RECONCILIATION.md`](T004_FINAL_QA_RECONCILIATION.md), [`tools/qa/verify_t004_time_representation.py`](../../tools/qa/verify_t004_time_representation.py) (`90/90 PASS`).
   - **T-005:** [`T005_FINAL_AUDIT_RECONCILIATION.md`](T005_FINAL_AUDIT_RECONCILIATION.md), [`T005_EVIDENCE_MATRIX.md`](T005_EVIDENCE_MATRIX.md), [`T005_TS011_TEST_SPEC.md`](T005_TS011_TEST_SPEC.md), [`T005_CONDITIONAL_NO_GO_PROPOSAL.md`](T005_CONDITIONAL_NO_GO_PROPOSAL.md), [`T005_EXECUTION_AND_FILE_MANIFEST.md`](T005_EXECUTION_AND_FILE_MANIFEST.md), [`T005_R2_1_REVIEWER_ADDENDUM.md`](T005_R2_1_REVIEWER_ADDENDUM.md), [`T005_R2_1_EVIDENCE_COMPLETENESS_CHECK.md`](T005_R2_1_EVIDENCE_COMPLETENESS_CHECK.md).
3. **Hồ sơ Rà soát Độc lập & Chuẩn bị Ký duyệt Gate G2:**
   - **G2-R1:** [`G2_R1_CRITICAL_FINDINGS_RECONCILIATION.md`](G2_R1_CRITICAL_FINDINGS_RECONCILIATION.md), [`G2_R1_TEST_AND_ASSERTION_AUDIT.md`](G2_R1_TEST_AND_ASSERTION_AUDIT.md), [`G2_R1_CORRECTED_GATE_READINESS.md`](G2_R1_CORRECTED_GATE_READINESS.md), [`G2_R1_EXECUTION_AND_ARTIFACT_MANIFEST.md`](G2_R1_EXECUTION_AND_ARTIFACT_MANIFEST.md).
   - **G2-SIGNOFF-PREP:** [`G2_SIGNOFF_DECISION_APPROVAL_MATRIX.md`](G2_SIGNOFF_DECISION_APPROVAL_MATRIX.md), [`G2_SIGNOFF_RESIDUAL_RISK_AND_CHANGE_PLAN.md`](G2_SIGNOFF_RESIDUAL_RISK_AND_CHANGE_PLAN.md), [`G2_SIGNOFF_EXECUTION_AND_ARTIFACT_MANIFEST.md`](G2_SIGNOFF_EXECUTION_AND_ARTIFACT_MANIFEST.md).

---

## 3. NGHIỆM THU KẾT QUẢ TỪNG NHIỆM VỤ THÀNH PHẦN (`T-001` ĐẾN `T-005`)

Project Lead đánh dấu chọn **một** phương án cho từng nhiệm vụ:

| Task | Nội dung & Bằng chứng chính | Trạng thái kỹ thuật hiện tại | Phán quyết của Project Lead |
|:---:|---|:---:|---|
| **T-001** | Kiểm toán nguồn gốc 9 CSV (54,674,003 dòng, 34 cột), phạm vi 19 hãng / 305–317 sân bay, phân định `METADATA_MATCH_ONLY` vs `IDENTITY_UNVERIFIED` (`OR-08`), ghi nhận `UPSTREAM_URL_LICENSE_UNKNOWN`. | `PASS (Conditional)` | `[ ] APPROVE_AS_COMPLETE_WITH_CONDITIONS`<br>`[ ] DEFER`<br>`[ ] REJECT / REQUEST_CHANGES` |
| **T-002** | Xác định cấp hạt *Scheduled Flight Leg Record*; chứng minh `FLIGHTS == 1.0` trên 100% dòng (`OR-01`); xác định cặp trùng khóa ứng viên duy nhất `YX 3624` (`2018-06-21 DEN->XNA`, dòng `6,384,132` & `6,384,133`, `OR-02`); cấm dedup tùy tiện (`TS-021`); mẫu số chuẩn `count_records`. | `PASS_WITH_OPEN_RISKS` | `[ ] APPROVE_AS_COMPLETE_WITH_CONDITIONS`<br>`[ ] DEFER`<br>`[ ] REJECT / REQUEST_CHANGES` |
| **T-003** | Khóa hợp đồng 8 CORE KPIs (`KPI-01..08`); xác minh thực nghiệm 7 trường số đo (`OFFICIAL_MINUTES_EMPIRICALLY_CONSISTENT_PROVISIONAL`, `OR-03`); khóa `KPI-11 = NOT_COMPUTABLE` (`OR-04`) & `KPI-12 = BLOCKED`; thiết kế `FIX-01..14` (`133/133 QA PASS`); đệ trình `FP-DEC-015` & `FP-DEC-016`. | `PASS_WITH_OPEN_RISKS` | `[ ] APPROVE_AS_COMPLETE_WITH_CONDITIONS`<br>`[ ] DEFER`<br>`[ ] REJECT / REQUEST_CHANGES` |
| **T-004** | Kiểm toán biểu diễn thời gian; ban hành Ma trận An toàn 4 cấp (`RAW_SOURCE_FIELD` vs `DERIVED_FIELD`), cấm trừ timestamp và cấm cộng `+24h` (`OR-06`); xác lập năm 2024 chỉ có `335/366` ngày (khuyết 31 ngày Tháng 3/2024, `OR-05 = OPEN_QUALITY_DEFECT`); thiết lập fixture `TF-01..09` (`90/90 QA PASS`). | `READY_FOR_SIGNOFF_WITH_OPEN_DEFECT` | `[ ] APPROVE_AS_COMPLETE_WITH_OPEN_DEFECT`<br>`[ ] DEFER`<br>`[ ] REJECT / REQUEST_CHANGES` |
| **T-005** | Kiểm toán 6 trường thời tiết (khuyết 2016: Origin `0.1624%`, Dest `0.1639%`; tổng 9 năm: Origin `0.0246%`, Dest `0.0275%`); chứng minh thiếu mốc giờ quan trắc, thiếu mã trạm và license (`OR-07`); thiết lập đặc tả `TS-011`; đệ trình đề xuất `CONDITIONAL_NO_GO` (`FP-DEC-PROP-015` / `FP-DEC-017`). | `CONDITIONAL_PENDING` | `[ ] APPROVE_CONDITIONAL_NO_GO`<br>`[ ] APPROVE_RESTRICTED_GO`<br>`[ ] DEFER / REQUEST_CHANGES` |

---

## 4. PHÊ DUYỆT CÁC QUYẾT ĐỊNH KIẾN TRÚC (`FP-DEC-003` ĐẾN `FP-DEC-017`)

Project Lead xem xét đánh giá chi tiết tại [`G2_SIGNOFF_DECISION_APPROVAL_MATRIX.md`](G2_SIGNOFF_DECISION_APPROVAL_MATRIX.md) và đánh dấu lựa chọn cho từng nhóm quyết định:

### 4.1. Nhóm Quyết định Khung Phạm vi, An toàn và Hợp đồng Dữ liệu Cốt lõi (`FP-DEC-003, 004, 006, 007, 008, 009, 010, 011, 013, 014`)
- `FP-DEC-003`: Loại trừ ML, ATL-only, Flight Chain `.pt` khỏi CORE; cấm `torch.load`.
- `FP-DEC-004`: Bảo vệ `data/raw/` bất biến (Read-Only); output phân phiên bản theo `run_id`.
- `FP-DEC-006`: Cấm tính KPI canceled/diverted từ 34 cột hiện hữu (`KPI-11 = NOT_COMPUTABLE`).
- `FP-DEC-007`: Cấm tính timeline qua đêm bằng date component của `CRS_ARR_TIME` hoặc cộng `+24h` ngây thơ.
- `FP-DEC-008`: Áp dụng ngưỡng `ARR_DELAY >= 15.0` trên mẫu số hữu hạn cho `KPI-02` (và `DEP_DELAY >= 15.0` cho `KPI-04`).
- `FP-DEC-009` & `FP-DEC-013`: Nhánh thời tiết là `Should/conditional`, cấm suy diễn nhân quả, phán quyết `CONDITIONAL_NO_GO` không làm chặn CORE G2/G6.
- `FP-DEC-010`: Cấm dùng `FLIGHTS` làm trọng số (`KPI-12 = BLOCKED`); mẫu số chuẩn là `count_records(C)`.
- `FP-DEC-011`: Phân biệt `metric_valid_rate` vs `source_coverage_status`; hạch toán 3 trạng thái dòng loại trừ nhau (`DC-11/12`); mẫu số 0 trả về `null` (`ZERO_DENOMINATOR`).
- `FP-DEC-014`: `size/mtime` chỉ cảnh báo drift (`METADATA_MATCH_ONLY`), không chứng minh danh tính nội dung thô (`IDENTITY_UNVERIFIED`).

**Lựa chọn của Project Lead cho Mục 4.1:**
- `[ ] APPROVE ALL (FP-DEC-003, 004, 006, 007, 008, 009, 010, 011, 013, 014)` — Chuyển trạng thái sang `APPROVED` trong `DECISIONS.md`.
- `[ ] APPROVE WITH EXCEPTIONS` — (Ghi rõ mã quyết định giữ lại hoặc yêu cầu sửa tại mục Ghi chú).
- `[ ] REJECT / REQUEST_CHANGES`

### 4.2. Quyết định `FP-DEC-005` — Định hướng Công nghệ PySpark + Parquet
- **Đề xuất:** Giữ trạng thái `PROPOSED` (hoặc `APPROVED_DIRECTION_PENDING_G3_SPEC`) khi đóng Gate G2; giao nhiệm vụ `T-006` (Gate G3) chốt phiên bản Spark/Python/Java, cấu hình tài nguyên và `T-010` (Gate G5) đo benchmark thực tế (`TS-014`).
- `[ ] APPROVE DEFERRAL OF RUNTIME SPEC TO G3 (T-006) & G5 (TS-014)`
- `[ ] REQUIRE FULL ENVIRONMENT SPEC BEFORE G2 CLOSEOUT`

### 4.3. Quyết định `FP-DEC-012` — Khóa 8 CORE KPIs & Chấp nhận Trạng thái Đơn vị Đo Tạm thời (`OR-03`)
- **Đề xuất:** Phê duyệt khóa 8 CORE KPIs (`KPI-01..KPI-08`) và chấp thuận nhãn đơn vị đo `OFFICIAL_MINUTES_EMPIRICALLY_CONSISTENT_PROVISIONAL` cho 7 trường số đo cốt lõi tại Gate G2, với điều kiện bắt buộc xuất cột `unit_status` trong mọi bảng kết quả và thực hiện đối chiếu bản ghi mẫu với dữ liệu BTS TranStats tại Gate G5 (`TS-018`).
- `[ ] APPROVE WITH G5 (TS-018) VERIFICATION CONDITION`
- `[ ] BLOCK G2 UNTIL EXTERNAL BTS TRANSTATS MATCH IS COMPLETED`
- `[ ] REJECT / REQUEST_CHANGES`

### 4.4. Quyết định `FP-DEC-015` — Thuật toán Phân vị P50/P90 (`percentile_approx` GK-Sketch `accuracy = 10000`)
- **Đề xuất:** Phê duyệt sử dụng hàm `percentile_approx(col("ARR_DELAY"), array(lit(0.5), lit(0.9)), accuracy=10000)` cho `KPI-06`, ghi nhận chính thức chặn trên sai số thứ hạng tương đối $\epsilon_{\text{rank}} \le 0.01\%$ (không tuyên bố chặn cứng sai số tuyệt đối theo phút), xuất kèm 5 trường siêu dữ liệu bắt buộc và thực hiện benchmark thực nghiệm tại Gate G5 (`TS-008`).
- `[ ] APPROVE FP-DEC-015 WITH G5 BENCHMARK CONDITION`
- `[ ] DEFER TO G3`
- `[ ] REJECT / REQUEST_CHANGES`

### 4.5. Quyết định `FP-DEC-016` — Chính sách Ngưỡng Cỡ Mẫu Tối thiểu Phân tầng (`min-N = 1000 / 365 / 100`)
- **Đề xuất:** Phê duyệt ngưỡng lọc bảng xếp hạng theo năm: `carrier-year >= 1,000`, `airport-year >= 365`, `route-year >= 100` (vùng cảnh báo `LOW_SAMPLE_CAUTION` từ $[N_{\min}, 3 N_{\min})$, ẩn thứ hạng `SUPPRESSED` khi $< N_{\min}$ nhưng giữ nguyên trong tổng hợp chung), kèm điều kiện bắt buộc gắn cờ `PARTIAL_YEAR_2024_MISSING_MARCH_335_OF_366_DAYS` cho các nhóm năm 2024 (`TS-008`, `TS-016`).
- `[ ] APPROVE FP-DEC-016 WITH 2024 PARTIAL-YEAR DISCLOSURE`
- `[ ] APPROVE WITH MODIFIED THRESHOLDS:` `_____________________________`
- `[ ] DEFER / REJECT`

### 4.6. Quyết định `FP-DEC-PROP-015` (Cấp mã chính thức `FP-DEC-017`) — Phán quyết `CONDITIONAL_NO_GO` cho Nhánh Thời tiết (`RQ-06` / `KPI-10`)
- **Đề xuất:** Phê duyệt ban hành phán quyết `CONDITIONAL_NO_GO` cho `T-005` và `T-015` под mã quyết định chính thức **`FP-DEC-017`**; đóng nhánh câu hỏi tùy chọn `RQ-06` và chỉ số `KPI-10` do thiếu nguồn gốc, bản quyền, mã trạm và mốc giờ quan trắc. Khẳng định đây là quyết định giới hạn phạm vi sử dụng (*scope exclusion*), không xóa 6 cột thời tiết khỏi CSV thô và giữ nguyên hợp đồng Schema 34 cột theo [`DATA_CONTRACT.md DC-07`](../02-design/DATA_CONTRACT.md#L21).
- `[ ] APPROVE CONDITIONAL_NO_GO AS FP-DEC-017 (DESELECT RQ-06 / KPI-10; PRESERVE 34-COLUMN RAW SCHEMA PER DC-07)`
- `[ ] REJECT NO-GO AND KEEP T-005 OPEN FOR EXTERNAL WEATHER RE-INGESTION`
- `[ ] DEFER DECISION`

---

## 5. CHẤP THUẬN QUẢN TRỊ RỦI RO MỞ VÀ ĐIỀU KIỆN RÀNG BUỘC CÁC GATE SAU (`G3–G7`)

Project Lead xác nhận chế độ quản trị đối với các rủi ro mở và khuyết tật dữ liệu chuyển giao sang `G3–G7` (chi tiết tại [`G2_SIGNOFF_RESIDUAL_RISK_AND_CHANGE_PLAN.md`](G2_SIGNOFF_RESIDUAL_RISK_AND_CHANGE_PLAN.md#L68-L80)):

1. **`OR-05` (`OPEN_QUALITY_DEFECT` — Khuyết toàn bộ 31 ngày Tháng 3/2024, năm 2024 chỉ có `335/366` ngày):**
   - `[ ] ACCEPT AS DOCUMENTED OPEN QUALITY DEFECT BOUND TO G3–G7` (Giữ chuẩn lịch 366 ngày cho năm 2024 trong `TS-004`; ghi nhận khuyết 31 ngày trong manifest năm 2024; gắn cờ cảnh báo trên mọi bảng và biểu đồ năm 2024).
   - `[ ] BLOCK PIPELINE UNTIL MARCH 2024 RAW DATA IS EXTERNALLY RECOVERED`
2. **`OR-08` (`METADATA_MATCH_ONLY / IDENTITY_UNVERIFIED` — Chưa có SHA-256 gốc từ BTS cho 9 CSV thô):**
   - `[ ] ACCEPT TRANSFER TO GATE G4 (T-007 / TS-019)` (Bắt buộc tính toán và khóa mã băm SHA-256 nội bộ của 9 CSV thô vào Ingestion Manifest ngay khi khởi tạo pipeline G4; duy trì nhãn `IDENTITY_UNVERIFIED` đối với nguồn ngoài).
   - `[ ] BLOCK G2 UNTIL EXTERNAL CHECKSUMS ARE OBTAINED`
3. **`OR-01, OR-02, OR-03, OR-04, OR-06, OR-07`:**
   - `[ ] ACCEPT POST-G2 MITIGATION & DEFERRAL BINDINGS AS SPECIFIED IN SECTION 2.1 OF G2_SIGNOFF_RESIDUAL_RISK_AND_CHANGE_PLAN.md`
   - `[ ] MODIFY RISK DISPOSITIONS` (Ghi rõ tại mục Ghi chú).

---

## 6. ỦY QUYỀN CẬP NHẬT CÔNG CỤ KIỂM TRA CÂY LÀM VIỆC & TÀI LIỆU ĐIỀU HÀNH

Do [`tools/check_working_tree_consistency.py`](../../tools/check_working_tree_consistency.py) hiện báo `86 PASS, 2 FAIL` vì whitelist tĩnh dòng 139 chỉ nhận diện `T001_..T004_`, Project Lead quyết định về việc thực hiện bản vá kỹ thuật riêng biệt sau khi ký biên bản này:

- `[ ] AUTHORIZE SEPARATE TOOLING & DOCS UPDATE POST-SIGNOFF` — Cho phép:
  1. Cập nhật `tools/check_working_tree_consistency.py` theo cơ chế **Sổ đăng ký Deliverable có Manifest + Kiểm tra Cú pháp Nghiêm ngặt + 6 Negative Regression Tests** đã đặc tả tại Mục 3 của [`G2_SIGNOFF_RESIDUAL_RISK_AND_CHANGE_PLAN.md`](G2_SIGNOFF_RESIDUAL_RISK_AND_CHANGE_PLAN.md).
  2. Cập nhật `docs/02-design/DECISIONS.md`, `docs/01-planning/BACKLOG.md` và `docs/04-execution/PROJECT_STATE.md` theo đúng các lựa chọn đã được tích chọn trong biên bản này.
- `[ ] DO NOT MODIFY CHECKER OR GOVERNANCE DOCS YET`

---

## 7. PHÁN QUYẾT ĐÓNG GATE G2 VÀ ỦY QUYỀN KHỞI ĐỘNG GATE G3 (`TASK T-006`)

Project Lead chọn **một** phán quyết tổng thể cho Gate G2 và nhiệm vụ tiếp theo:

- `[ ] OPTION A — APPROVE GATE G2 WITH EXPLICIT CONDITIONS & AUTHORIZE START OF GATE G3 (TASK T-006)`  
  *(Chuyển trạng thái Gate G2 sang `PASS_WITH_EXPLICIT_CONDITIONS`; cho phép bắt đầu thiết kế kiến trúc, ngân sách tài nguyên và schema đầu ra tại `T-006`; tiếp tục cấm viết code production G4 cho đến khi hoàn thành Gate G3).*
- `[ ] OPTION B — APPROVE GATE G2 DECISIONS ONLY, HOLD TASK T-006 PENDING POST-SIGNOFF DOCS/CHECKER UPDATE VERIFICATION`  
  *(Cho phép cập nhật trạng thái quyết định và sửa công cụ kiểm tra cây làm việc trước; chỉ khởi động `T-006` sau khi xác nhận working-tree checker đạt PASS).*
- `[ ] OPTION C — REJECT / KEEP GATE G2 IN_PROGRESS / NOT_PASSED`  
  *(Yêu cầu thực hiện lại hoặc bổ sung bằng chứng theo chỉ đạo dưới đây; cấm khởi động `T-006`).*

---

## 8. GHI CHÚ CHỈ ĐẠO VÀ CHỮ KÝ XÁC NHẬN CỦA PROJECT LEAD (HUMAN SIGN-OFF BLOCK)

- **Ý kiến chỉ đạo bổ sung / Điều chỉnh của Project Lead:**  
  `____________________________________________________________________________________`  
  `____________________________________________________________________________________`

- **Họ tên / Định danh Người phê duyệt (Project Lead / Technical Reviewer):** `______________________________`
- **Vai trò / Thẩm quyền:** `___________________________________________________________________________`
- **Chữ ký xác nhận:** `_______________________________________________________________________________`
- **Ngày và giờ phê duyệt (YYYY-MM-DD HH:MM TZ):** `___________________________________________________`

---
*Trạng thái hiệu lực hiện tại: **`UNSIGNED_DRAFT — NO APPROVAL CONFERRED`**. Gate G2 hiện vẫn là **`IN_PROGRESS / NOT_PASSED`**.*
