# G2_SIGNOFF_RESIDUAL_RISK_AND_CHANGE_PLAN — Sổ bộ Rủi ro Chuẩn tắc, Hiệu chỉnh Tồn đọng & Kế hoạch Cập nhật Tài liệu Hậu Ký duyệt

**Document ID:** `G2-SIGNOFF-RRCP-001`  
**Dự án:** Phân tích hiệu suất chuyến bay Hoa Kỳ 2016–2024 bằng Apache Spark / PySpark  
**Gate kiểm soát:** `Gate G2` (Data Understanding, Cohort, Units, Time Safety & Weather Usability Contracts)  
**Phạm vi:** (1) Hiệu chỉnh các điểm tồn đọng sau G2-R1 (Mục A–G), (2) Đối chiếu toàn diện rủi ro `OR-01..OR-08` và `R-01..R-17`, (3) Đặc tả cơ chế đăng ký Artifact có Manifest cho công cụ kiểm tra cây làm việc, và (4) Kế hoạch cập nhật tài liệu điều hành sau khi có chữ ký phê duyệt  
**Trạng thái tài liệu:** `GOVERNANCE_PREPARATION_PACKAGE / PENDING_HUMAN_APPROVAL`  
**Trạng thái Gate G2 hiện hành:** `IN_PROGRESS / NOT_PASSED`  
**Ngày lập:** 2026-10-16  

---

## 1. HIỆU CHỈNH CÁC ĐIỂM TỒN ĐỌNG SAU G2-R1 (RESIDUAL EVIDENCE CORRECTIONS A–G)

Tài liệu này ghi nhận và khóa lại 7 điểm hiệu chỉnh tồn đọng (`Correction A` đến `Correction G`) mà không khởi động lại kiểm toán G2-R1 và không chỉnh sửa đè lên các báo cáo lịch sử:

### 1.1. Correction A — Đính chính Tham chiếu Rủi ro T-001 (`OR-01` vs. Giới hạn URL/License Nguồn)
- **Phát hiện tồn đọng:** Trong bảng tóm tắt Mục 2 (dòng `T-001`) của [`G2_R1_CORRECTED_GATE_READINESS.md`](G2_R1_CORRECTED_GATE_READINESS.md#L27), câu mô tả có ghi chú ngoặc đơn: *"Nhận diện rủi ro thiếu URL/License nguồn gốc (`OR-01` trong phạm vi nghiên cứu học thuật)"*, trong khi ở bảng Mục 4 của chính tài liệu đó đã khôi phục đúng `OR-01` là hằng số `FLIGHTS == 1.0`.
- **Hiệu chỉnh chuẩn tắc:**
  1. **`OR-01` được bảo lưu độc quyền** cho rủi ro: *"Trường `FLIGHTS` mang hằng số `1.0` trên toàn bộ 54,674,003 bản ghi; cấm dùng làm trọng số tính toán; khóa `KPI-12 = BLOCKED`"*.
  2. Giới hạn về việc không xác định được đường dẫn tải xuống (Download URL) và giấy phép phân phối gốc (Upstream License) của bên thứ ba tại [`T001_PROVENANCE_AUDIT.md`](T001_PROVENANCE_AUDIT.md) và [`T001_R2_FINAL_REVIEW.md`](T001_R2_FINAL_REVIEW.md#L88) mang định danh chuẩn là **`UPSTREAM_URL_LICENSE_UNKNOWN`**, gắn với rủi ro dự án **`R-02`** (độ đại diện quần thể) và **`R-14`** (ràng buộc học thuật/nộp bài), **tuyệt đối không gắn mã `OR-01`**.

### 1.2. Correction B — Bảo tồn Nguyên trạng 8 Rủi ro Mở Nhiệm vụ (`OR-01..OR-08`) và Phân biệt với Rủi ro Dự án (`R-01..R-17`)
- Dự án duy trì hai tầng quản trị rủi ro song song nhưng phân biệt rạch ròi:
  - **Tầng Rủi ro Dự án (`R-01` đến `R-17`):** Được định nghĩa tại [`docs/03-quality/RISK_REGISTER.md`](../03-quality/RISK_REGISTER.md), quản lý các nguy cơ xuyên suốt từ G0 đến G7 (kiến trúc, vận hành Spark, bảo mật, nhân sự, tài liệu).
  - **Tầng Rủi ro Mở Nhiệm vụ (`OR-01` đến `OR-08`):** Được khởi tạo tại [`T001_R2_FINAL_REVIEW.md`](T001_R2_FINAL_REVIEW.md#L96-L108) và theo dõi tiến độ bàn giao qua [`T002_FINAL_ACCEPTANCE_CHECK.md`](T002_FINAL_ACCEPTANCE_CHECK.md), [`T003_SIGNOFF_RECORD.md`](T003_SIGNOFF_RECORD.md#L36-L50), [`T004_FINAL_REVIEW.md`](T004_FINAL_REVIEW.md#L62-L74) và [`T005_FINAL_AUDIT_RECONCILIATION.md`](T005_FINAL_AUDIT_RECONCILIATION.md#L88-L90).
- Chi tiết đối chiếu đầy đủ giữa hai hệ thống được trình bày tại **Mục 2** bên dưới.

### 1.3. Correction C — Ghi nhận Giới hạn Lịch sử Phiên bản của Kịch bản Kiểm thử T-004 (`61 PASS` vs. `90 PASS`)
- **Trạng thái số học (`VERIFIED_CURRENT_SCRIPT_EXECUTION`):** Phiên bản hiện hành của [`tools/qa/verify_t004_time_representation.py`](../../tools/qa/verify_t004_time_representation.py) chứa 39 lệnh `check()` trong mã nguồn và khi thực thi đánh giá đúng **90 phép kiểm (`22 + 19 + 9 + 9 + 10 + 4 + 4 + 5 + 8 = 90 PASS, 0 FAIL`, Exit Code `0`)**.
- **Giới hạn truy xuất phiên bản lịch sử (`HISTORICAL_SCRIPT_VERSION_UNAVAILABLE`):** Vì không gian làm việc hiện tại là bản xuất snapshot độc lập (không kèm thư mục lịch sử commit `.git`), phiên bản mã nguồn trung gian từng in ra con số `61 PASS` (được trích dẫn trong văn bản [`T004_FINAL_QA_RECONCILIATION.md`](T004_FINAL_QA_RECONCILIATION.md)) **không còn lưu giữ dưới dạng tệp thực thi riêng biệt trên ổ đĩa**. Do đó:
  - Kết quả `90 PASS, 0 FAIL` được phân loại là **`VERIFIED_REPRODUCIBLE_IN_CURRENT_WORKTREE`**.
  - Con số `61 PASS` được phân loại là **`REPORTED_IN_HISTORICAL_DOC_INTERMEDIATE_VERSION_UNAVAILABLE`**, không suy diễn chi tiết từng dòng mã của bản 61 PASS cũ.

### 1.4. Correction D — Tách biệt Tuyệt đối Kiểm thử QA T-004 với Kiểm định Dữ liệu Thô và Runtime Spark
- Kịch bản [`tools/qa/verify_t004_time_representation.py`](../../tools/qa/verify_t004_time_representation.py) chỉ kiểm tra:
  1. Sự tồn tại và kích thước $>100$ bytes của 11 tệp tài liệu/fixture T-004.
  2. Giá trị `row_count` đã ghi sẵn trong 9 tệp `schema_YYYY.json` và sự xuất hiện của các chuỗi số này trong bảng Markdown.
  3. Sự hiện diện của các chuỗi ký tự chuẩn (như số dòng `6,384,132`, giá trị `13.0 / 83.0 / 6.0 / 102.0`, nhãn `OPEN_QUALITY_DEFECT`) trong báo cáo Markdown.
  4. Cấu trúc cú pháp và đẳng thức số học trên 9 bản ghi giả lập của [`T004_TF09_temporal_fixture.csv`](T004_TF09_temporal_fixture.csv), [`T004_TF09_full_schema_fixture.csv`](T004_TF09_full_schema_fixture.csv) và [`T004_TF09_temporal_fixture.json`](T004_TF09_temporal_fixture.json).
- **Khẳng định ranh giới:** Việc kịch bản này đạt `90 PASS` **KHÔNG phải là kết quả quét lại 54,674,003 dòng CSV thô** và **KHÔNG phải là bằng chứng đã chạy PySpark**.

### 1.5. Correction E — Đối chiếu Trạng thái Hiện thời của `check_working_tree_consistency.py`
- Mọi báo cáo trạng thái phải phản ánh lần chạy trực tiếp trên cây thư mục hiện hành sau khi xuất đầy đủ các tệp.
- Tại thời điểm hoàn tất gói hồ sơ `G2-SIGNOFF-PREP` này, thư mục [`docs/05-evidence/`](./) có tổng cộng **18 tệp bằng chứng mới** nằm ngoài danh sách whitelist tĩnh `T001_..T004_` của [`tools/check_working_tree_consistency.py`](../../tools/check_working_tree_consistency.py#L139):
  - **7 tệp thuộc T-005:** `T005_CONDITIONAL_NO_GO_PROPOSAL.md`, `T005_EVIDENCE_MATRIX.md`, `T005_EXECUTION_AND_FILE_MANIFEST.md`, `T005_FINAL_AUDIT_RECONCILIATION.md`, `T005_R2_1_EVIDENCE_COMPLETENESS_CHECK.md`, `T005_R2_1_REVIEWER_ADDENDUM.md`, `T005_TS011_TEST_SPEC.md`.
  - **3 tệp thuộc G2 (vòng đầu):** `G2_DECISION_AND_BLOCKER_REGISTER.md`, `G2_EXECUTION_EVIDENCE_RECONCILIATION.md`, `G2_FINAL_GATE_READINESS_AUDIT.md`.
  - **4 tệp thuộc G2-R1:** `G2_R1_CORRECTED_GATE_READINESS.md`, `G2_R1_CRITICAL_FINDINGS_RECONCILIATION.md`, `G2_R1_EXECUTION_AND_ARTIFACT_MANIFEST.md`, `G2_R1_TEST_AND_ASSERTION_AUDIT.md`.
  - **4 tệp thuộc G2-SIGNOFF-PREP (gói hiện tại):** `G2_SIGNOFF_DECISION_APPROVAL_MATRIX.md`, `G2_SIGNOFF_RESIDUAL_RISK_AND_CHANGE_PLAN.md`, `G2_SIGNOFF_HUMAN_APPROVAL_RECORD_DRAFT.md`, `G2_SIGNOFF_EXECUTION_AND_ARTIFACT_MANIFEST.md`.
- Kết quả chạy thực tế `python tools/check_working_tree_consistency.py` hiện tại là **`86 PASS, 2 FAIL` (Exit Code `1`)**, trong đó 86/86 quy tắc nội dung và đường dẫn đều PASS, và 2 assertion thất bại hoàn toàn do 18 tệp trên chưa được đăng ký vào bộ lọc của script.

### 1.6. Correction F — Không Dùng Regex Tên Tệp Đơn thuần Làm Cơ chế Phê duyệt Artifact
- Trong báo cáo G2-R1 trước đó, giải pháp đề xuất mới chỉ dừng ở việc mở rộng biểu thức chính quy (regex) tại dòng 139 của `check_working_tree_consistency.py`.
- **Phê bình quản trị:** Một biểu thức regex khớp tên tệp (`T005_...` hay `G2_...`) chỉ kiểm tra được quy ước đặt tên, **không chứng minh được tệp đó là một deliverable đã được đăng ký hợp lệ, không kiểm tra được dung lượng byte hay mã băm SHA-256, và không ngăn được việc tạo tràn lan các tệp nháp không được kiểm soát**.
- Do đó, **Mục 3** của tài liệu này thiết kế một **Đặc tả Cơ chế Đăng ký Artifact Dựa trên Manifest (`Manifest-Backed Deliverable Registry Specification`)** để Project Lead phê duyệt áp dụng cho `T-006` và các nhiệm vụ tiếp theo.

### 1.7. Correction G — Chuẩn hóa Phân loại Rủi ro `OR-07` Khi Phê duyệt Weather `CONDITIONAL_NO_GO`
- Khi Project Lead phê duyệt quyết định `CONDITIONAL_NO_GO` cho nhánh thời tiết (`FP-DEC-PROP-015` / `FP-DEC-017`), rủi ro `OR-07` **không được ghi là "đã khắc phục nguồn dữ liệu"** mà bắt buộc phải ghi nhận trạng thái chính xác là:
  > **`MITIGATED_BY_SCOPE_EXCLUSION (CONDITIONAL_NO_GO — RQ-06 / KPI-10 DESELECTED; UPSTREAM WEATHER PROVENANCE REMAINS UNVERIFIED)`**
- Điều này bảo đảm tính trung thực tuyệt đối: dự án loại bỏ rủi ro bằng cách không sử dụng dữ liệu thời tiết cho phân tích sản xuất, trong khi 6 cột thời tiết trong CSV gốc vẫn giữ nguyên trạng thái `PROVENANCE_UNVERIFIED` theo đúng hợp đồng [`DATA_CONTRACT.md DC-07`](../02-design/DATA_CONTRACT.md#L21).

---

## 2. SỔ BỘ ĐỐI CHIẾU RỦI RO CHUẨN TẮC (`OR-01..OR-08` VÀ `R-01..R-17`)

### 2.1. Bảng Quản trị 8 Rủi ro Mở Nhiệm vụ (`OR-01` đến `OR-08`)

| Mã OR | Định nghĩa gốc bất biến (Canonical Meaning) | Ánh xạ `RISK_REGISTER.md` | Trạng thái hiện tại (Trước khi ký G2) | Trạng thái mục tiêu (Sau khi ký G2) | Điều kiện ràng buộc các Gate sau (`G3–G7`) |
|:---:|---|:---:|---|---|---|
| **`OR-01`** | Trường `FLIGHTS` mang hằng số `1.0` trên toàn bộ 54,674,003 dòng; ngữ nghĩa trọng số không được chứng minh. | `R-09` | `DESIGN_LOCKED_PENDING_G2_SIGNOFF` | `MITIGATED_BY_CONTRACT` (`FP-DEC-010` Approved) | **G4 (`T-007`/`T-008`) & G5 (`TS-009`):** Cấm cộng/nhân trọng số `FLIGHTS`; giữ `KPI-12 = BLOCKED`; kiểm tra bằng unit test. |
| **`OR-02`** | Tồn tại 1 cặp bản ghi trùng khóa nghiệp vụ ứng viên (`YX 3624`, `2018-06-21`, `DEN -> XNA`, dòng `6,384,132` & `6,384,133`) có độ trễ khác biệt lớn (`+877m` vs `+20m`); bản chất thực thể vật lý `UNKNOWN` do thiếu `TAIL_NUM`. | `R-05`, `R-13` | `DESIGN_LOCKED_PENDING_G2_SIGNOFF` | `MITIGATED_BY_PRESERVATION_GUARD` (`DC-10`, `TS-021`) | **G4 (`T-007`/`T-008`) & G5 (`TS-012`, `TS-020`, `TS-021`):** Nghiêm cấm deduplicate tự động trên khóa 6 trường; sử dụng fixture `FIX-13` / `TF-08` để kiểm thử bảo toàn cả 2 dòng. |
| **`OR-03`** | Đơn vị đo của 7 trường số cốt lõi (`ARR_DELAY`, `DEP_DELAY`, `TAXI_OUT`, `TAXI_IN`, `AIR_TIME`, `ACTUAL_ELAPSED_TIME`, `CRS_ELAPSED_TIME`) khớp thực nghiệm với phút nhưng chưa có văn bản gốc của tác giả bộ dữ liệu xác nhận. | `R-15` | `OPEN_PROVISIONAL` (`OFFICIAL_MINUTES_EMPIRICALLY_CONSISTENT_PROVISIONAL`) | `DEFERRED_TO_G5_WITH_CONDITION` (`FP-DEC-012`) | **G5 (`T-011` / `TS-018`) & G7:** Mọi bảng kết quả phải xuất kèm cột `unit_status`; thực hiện đối chiếu mẫu có giới hạn (*bounded record match*) với dữ liệu BTS TranStats tại G5. |
| **`OR-04`** | Bộ dữ liệu 34 cột thiếu hoàn toàn trường `CANCELLED` và `DIVERTED`; 100% bản ghi có `ARR_DELAY` hữu hạn. | `R-01`, `R-02` | `SCOPE_CLOSED_PENDING_G2_SIGNOFF` | `CLOSED_BY_SCOPE_LOCK` (`FP-DEC-006` Approved) | **G4–G7 (`TS-009`):** Khóa vĩnh viễn `KPI-11 = NOT_COMPUTABLE`; công bố rõ quần thể nghiên cứu là các chuyến bay có kết quả vận hành hữu hạn trong tập dữ liệu đã kiểm toán. |
| **`OR-05`** | **Năm nhuận 2024 chỉ có `335/366` ngày phân biệt trong CSV hiện tại; vắng mặt toàn bộ 31 ngày Tháng 3/2024 (`2024-03-01..2024-03-31`, `DATA_ABSENT_IN_CURRENT_CSV`), trong khi ngày nhuận `2024-02-29` có `18,642` bản ghi; nguyên nhân upstream `UNKNOWN`.** | `R-02`, `R-10` | **`OPEN_QUALITY_DEFECT`** | **`ACCEPTED_OPEN_QUALITY_DEFECT_BOUND_TO_G3_G7`** | **G3 (`T-006`), G4 (`T-008`), G6 (`T-012`/`TS-004`, `T-013`/`TS-016`), G7 (`T-016`):** Giữ chuẩn tham chiếu 366 ngày cho năm 2024; ghi nhận `missing_calendar_days = 31` trong manifest năm 2024; gắn cờ `PARTIAL_YEAR_2024_MISSING_MARCH` trên mọi chỉ số và biểu đồ năm 2024. |
| **`OR-06`** | Hiện tượng rollover qua nửa đêm trên các trường chuỗi giờ địa phương (`CRS_ARR_TIME`, `DEP_TIME`, `ARR_TIME`, `WHEELS_OFF`, `WHEELS_ON`) do date component bị gán cứng theo `FL_DATE`. | `R-03` | `RESOLVED_AT_DESIGN_LEVEL_PENDING_SIGNOFF` | `MITIGATED_BY_SAFE_TIME_CONTRACT` (`FP-DEC-007` Approved) | **G4 (`T-007`/`T-008`) & G5 (`TS-010`):** Áp dụng nghiêm ngặt Ma trận An toàn 4 cấp; cấm trừ timestamp trực tiếp; cấm cộng `+24h`; kiểm thử tự động trên 9 kịch bản `TF-01..TF-09`. |
| **`OR-07`** | 6 trường thời tiết (`O_TEMP`, `O_PRCP`, `O_WSPD`, `D_TEMP`, `D_PRCP`, `D_WSPD`) thiếu mã trạm đo, thiếu mốc giờ quan trắc, thiếu chứng từ bản quyền và không rõ thuật toán ghép nối thời gian/không gian. | `R-04` | `CONDITIONAL_PENDING` | **`MITIGATED_BY_SCOPE_EXCLUSION`** (Nếu duyệt `CONDITIONAL_NO_GO` tại `FP-DEC-017`) | **G4–G6 (`DC-07`, `TS-009`, `TS-011`):** Giữ nguyên 34 cột ở schema đọc thô theo `DC-07`; hủy kích hoạt `T-015` (`RQ-06` / `KPI-10`); không đưa lỗi/null thời tiết vào `quarantined_row_count` của CORE. |
| **`OR-08`** | 9 tệp CSV thô hiện chỉ khớp kích thước (`size`) và thời gian sửa đổi (`mtime`) với `schema_YYYY.json` (`METADATA_MATCH_ONLY`), chưa có mã băm SHA-256 tham chiếu từ nguồn phát hành gốc (`IDENTITY_UNVERIFIED`). | `R-16` | `OPEN_METADATA_MATCH_ONLY` | `TRANSFERRED_TO_G4_INGESTION_MANIFEST` (`FP-DEC-014` Approved) | **G4 (`T-009`/`T-007`, `TS-019`) & G5:** Bắt buộc tính toán và khóa mã băm SHA-256 cục bộ của 9 tệp CSV thô vào Ingestion Manifest ngay ở bước khởi tạo; duy trì nhãn `IDENTITY_UNVERIFIED` đối với nguồn gốc bên ngoài. |

### 2.2. Bảng Kiểm tra Toàn vẹn Danh mục Rủi ro Dự án (`R-01` đến `R-17`)
Toàn bộ 17 mã rủi ro chuẩn trong [`docs/03-quality/RISK_REGISTER.md`](../03-quality/RISK_REGISTER.md) được giữ nguyên định nghĩa:
- **Nhóm Rủi ro Dữ liệu & Phương pháp (G2 Trọng tâm):** `R-01` (Cancel/divert), `R-02` (54.7M rows $\ne$ all US flights + thiếu URL/License + khuyết Tháng 3/2024), `R-03` (Overnight/2400), `R-04` (Weather provenance), `R-05` (Drop trùng/thiếu mẫu số), `R-09` (`FLIGHTS` / `OP_CARRIER_FL_NUM`), `R-13` (Cực trị có thật bị cắt ngầm), `R-15` (Đơn vị 7 trường đo), `R-16` (`size/mtime` $\ne$ content hash), `R-17` (Cộng nhầm origin+dest hoặc dùng chung mẫu số submetric).
- **Nhóm Rủi ro Hệ thống, Bảo mật & Quản trị (G3–G7 Trọng tâm):** `R-06` (OOM/spill Spark), `R-07` (Drift tài liệu giữa các phiên AI), `R-08` (Ghi đè raw/lộ đường dẫn), `R-10` (Lệch so sánh năm do 2020 & partial 2024), `R-11` (Nạp `.pt` không tin cậy), `R-12` (KPI không tái lập), `R-14` (Chưa rõ rubric/thời hạn/môi trường).

---

## 3. ĐẶC TẢ KỸ THUẬT CẢI TIẾN CÔNG CỤ KIỂM TRA CÂY LÀM VIỆC (CHECKER REMEDIATION SPECIFICATION)

> **Lưu ý an toàn:** Đây là **Đặc tả Thiết kế Thay đổi Công cụ (Proposed Tooling Change Specification)** trình Project Lead phê duyệt. Không một dòng mã nào trong [`tools/check_working_tree_consistency.py`](../../tools/check_working_tree_consistency.py) hay [`tools/check_docs_consistency.py`](../../tools/check_docs_consistency.py) được sửa đổi trong nhiệm vụ này.

### 3.1. Vấn đề của Cơ chế Hiện tại và Hạn chế của Giải pháp Chỉ Dùng Regex
1. **Hiện trạng dòng 139 của [`tools/check_working_tree_consistency.py`](../../tools/check_working_tree_consistency.py#L139):**
   - Chỉ cho phép các tệp bắt đầu bằng `T001_`, `T002_`, `T003_`, `T004_` trong thư mục `docs/05-evidence/`.
   - Khi dự án tiến sang `T-005`, `G2`, và sắp tới là `T-006` (Gate G3), mọi tệp deliverable hợp lệ đều bị đánh dấu là `unrecognized stray files` (hiện tại gây ra 2 FAIL trên 18 tệp).
2. **Tại sao chỉ dùng Regex tên tệp là chưa đủ an toàn?**
   - Nếu chỉ thay bằng một biểu thức chính quy khớp tiền tố (`T\d{3}_` hay `G\d_`), công cụ sẽ tự động cho qua bất kỳ tệp nháp, tệp rác hoặc tệp giả mạo nào miễn là đặt tên giống quy ước, mà không kiểm tra xem tệp đó có thuộc danh mục bàn giao chính thức hay không, có bị sửa đổi nội dung ngoài ý muốn hay không.

### 3.2. Kiến trúc Đề xuất: Cơ chế Đăng ký Deliverable Dựa trên Manifest Kết hợp Ràng buộc Cú pháp (`Manifest-Backed Deliverable Registry`)
Đề xuất nâng cấp cơ chế kiểm tra working-tree theo mô hình **2 lớp bảo vệ (Two-Layer Verification)** sau khi có phê duyệt của Project Lead:

1. **Lớp 1 — Tệp Đăng ký Bằng chứng Độc lập (`EVIDENCE_DELIVERABLE_REGISTER`):**
   - Duy trì một tệp đăng ký JSON chuyên biệt (hoặc một trường mở rộng được phê duyệt tách biệt khỏi `PACKAGE_MANIFEST.json` v1.1 gốc để bảo toàn 100% mã băm của 47 tệp phát hành ban đầu).
   - Mỗi deliverable hợp lệ từ `T-001` trở đi phải có một bản ghi khai báo tường minh:
     - `path`: Đường dẫn chuẩn POSIX (ví dụ: `docs/05-evidence/T005_FINAL_AUDIT_RECONCILIATION.md`).
     - `task_id` / `gate_id`: Định danh nhiệm vụ/cổng (ví dụ: `T-005`, `G2`).
     - `artifact_role`: Loại tài liệu (`AUDIT_REPORT`, `TEST_FIXTURE_CSV`, `TEST_ORACLE_JSON`, `SIGNOFF_RECORD`, `QA_SCRIPT`).
     - `bytes`: Kích thước tệp chính xác tính bằng byte.
     - `sha256`: Mã băm SHA-256 của tệp tại thời điểm nghiệm thu.
2. **Lớp 2 — Kiểm tra Cú pháp Nghiêm ngặt và Đối khớp Toàn diện trong `check_working_tree_consistency.py`:**
   - Giữ nguyên việc xác thực 47 tệp gốc của `PACKAGE_MANIFEST.json` và 13 tệp gốc của `SOURCE_MANIFEST.json`.
   - Đối với các tệp phát sinh hợp lệ trong working-tree (`extra_files`):
     - Tệp dữ liệu thô: Phải nằm đúng trong `data/raw/tabular/{year}/flight_with_weather_{year}.csv` (đúng 9 tệp từ 2016–2024) và khớp kích thước byte trong `schema_YYYY.json`.
     - Tệp bằng chứng & công cụ nhiệm vụ: **Bắt buộc phải thỏa mãn ĐỒNG THỜI cả hai điều kiện**:
       1. Có mặt trong sổ đăng ký `EVIDENCE_DELIVERABLE_REGISTER` với `bytes` và `sha256` khớp 100% thực tế trên đĩa.
       2. Tuân thủ mẫu đường dẫn và phần mở rộng cho phép:
          - Trong `docs/05-evidence/`: Chỉ cho phép phần mở rộng `.md`, `.csv`, `.json` với tiền tố nhiệm vụ/cổng hợp lệ `^(T00[1-9]|T01[0-7]|G[0-7])(_R\d+(_\d+)?|_SIGNOFF)?_[A-Za-z0-9_]+\.(md|csv|json)$`.
          - Trong `tools/`: Chỉ cho phép các kịch bản kiểm toán/QA đã đăng ký `.py` trong `tools/audit/` và `tools/qa/`.
     - Mọi tệp nằm trên đĩa nhưng không có trong sổ đăng ký, hoặc có trong sổ đăng ký nhưng sai lệch `sha256`/`bytes`, đều bị đánh `FAIL` tức khắc.

### 3.3. Bộ Kịch bản Kiểm thử Hồi quy Âm tính (Negative Regression Test Cases)
Khi Project Lead cho phép cập nhật công cụ kiểm tra ở bước triển khai tiếp theo, bản vá bắt buộc phải vượt qua 6 ca kiểm thử âm tính (Negative Tests) sau đây (đảm bảo công cụ trả về `FAIL` / Exit Code `1` khi gặp các trường hợp này):

| Mã Test | Tình huống giả lập kiểm thử âm tính | Kết quả kỳ vọng của Checker |
|:---:|---|---|
| `NEG-WT-01` | Một tệp có tên đúng cú pháp regex (ví dụ: `T005_UNREGISTERED_DRAFT` đuôi `.md`) xuất hiện trong thư mục bằng chứng nhưng **chưa được khai báo** trong sổ đăng ký manifest. | **Bắt buộc `FAIL`** (`Unregistered file in working-tree`) |
| `NEG-WT-02` | Một tệp đã đăng ký trong manifest bị chỉnh sửa thêm/bớt 1 ký tự làm thay đổi `sha256` hoặc `bytes`. | **Bắt buộc `FAIL`** (`Deliverable hash/size mismatch`) |
| `NEG-WT-03` | Một tệp thực thi hoặc mã nguồn (`.py`, `.sh`, `.exe`, `.bat`, `.pt`, `.parquet`) bị đặt nhầm vào thư mục bằng chứng tài liệu. | **Bắt buộc `FAIL`** (`Disallowed file extension in evidence directory`) |
| `NEG-WT-04` | Một tệp mang tiền tố nhiệm vụ không tồn tại trong `BACKLOG.md` (ví dụ: `T099_` hoặc `G9_`). | **Bắt buộc `FAIL`** (`Invalid task/gate identifier prefix`) |
| `NEG-WT-05` | Một tệp trong `PACKAGE_MANIFEST.json` v1.1 gốc (ví dụ `DECISIONS.md` hoặc `PROJECT_STATE.md`) được cập nhật sau khi ký duyệt nhưng chưa được đưa vào danh sách `governed_living_docs` có kiểm soát phiên bản. | **Bắt buộc `FAIL`** hoặc yêu cầu xác thực chữ ký cập nhật manifest có kiểm soát |
| `NEG-WT-06` | Một tài liệu Markdown chứa đường dẫn văn bản trỏ tới một tệp không tồn tại trên đĩa. | **Bắt buộc `FAIL`** (`Broken documentary path reference`) |

---

## 4. KẾ HOẠCH CẬP NHẬT TÀI LIỆU ĐIỀU HÀNH HẬU KÝ DUYỆT (POST-SIGNOFF DOCUMENT UPDATE PLAN)

Qua rà soát 4 tài liệu điều hành cốt lõi tại `docs/04-execution/`, dưới đây là danh sách các thông tin đã lỗi thời và **văn bản thay thế đề xuất (Proposed Replacement Text)** để áp dụng **SAU KHI** Project Lead ký duyệt đóng Gate G2:

### 4.1. Rà soát [`docs/04-execution/PROJECT_STATE.md`](../04-execution/PROJECT_STATE.md)
- **Các điểm lỗi thời hiện tại:**
  1. Dòng 3: Ngày cập nhật vẫn là `2026-10-13`.
  2. Dòng 9 (Bảng Gate): Cột Evidence của `G2` chưa liệt kê `T-005` và các báo cáo rà soát `G2-R1` / `G2-SIGNOFF`.
  3. Dòng 22 (Hàng `T-004`): Vẫn ghi `61/61 QA checks PASS; 88/88 working-tree checks PASS` và `Gate G2 tiếp tục IN_PROGRESS chờ T-005`.
  4. Bảng `Task execution status` (dòng 17–23): **Chưa có hàng `T-005`**.
  5. Lưu ý kỹ thuật quan trọng: Trong [`tools/check_working_tree_consistency.py`](../../tools/check_working_tree_consistency.py#L128-L129), tệp `PROJECT_STATE.md` đã được cấu hình đặc biệt là `Living project state` (chỉ kiểm tra `exists`, `st_size > 500` và `'T-001' in text`), do đó việc cập nhật `PROJECT_STATE.md` sau khi có phê duyệt của Project Lead sẽ **không** làm hỏng kiểm tra `PACKAGE_MANIFEST.json`.
- **Văn bản thay thế đề xuất (`PROPOSED_POST_SIGNOFF_TEXT — DO NOT APPLY BEFORE HUMAN APPROVAL`):**
  ```markdown
  <!-- PROPOSED_POST_SIGNOFF_TEXT CHO PROJECT_STATE.md (CHỈ ÁP DỤNG SAU KHI PROJECT LEAD KÝ DUYỆT G2) -->
  | G2 | PASS_WITH_EXPLICIT_CONDITIONS (hoặc IN_PROGRESS nếu chưa ký) | T-001 PASS (Conditional); T-002 PASS_WITH_OPEN_RISKS; T-003 PASS_WITH_OPEN_RISKS; T-004 PASS_WITH_OPEN_DEFECT (90/90 QA PASS); T-005 CONDITIONAL_NO_GO (FP-DEC-017); G2-R1 & G2-SIGNOFF package complete | Ràng buộc G3–G7: OR-03 (provisional units -> G5 TS-018), OR-05 (2024 335/366 days missing March -> TS-004/TS-016), OR-08 (raw SHA-256 -> G4 TS-019) |
  
  <!-- Bổ sung hàng T-004 cập nhật và hàng T-005 vào bảng Task execution status: -->
  | **T-004** | **PASS_WITH_OPEN_DEFECT** | `T004_FINAL_QA_RECONCILIATION.md`, `T004_SAFE_FIELDS_DECISION.md`, `T004_2024_DATE_COVERAGE_AUDIT.md`, `T004_OVERNIGHT_COUNTEREXAMPLES.md`, `T004_TF09_temporal_fixture.csv`, `T004_TF09_full_schema_fixture.csv`, `T004_TF09_temporal_fixture.json` | Đối chiếu khớp 54,674,003 dòng; bảo toàn cặp YX 3624 (2018-06-21 DEN->XNA, dòng 6,384,132 & 6,384,133); năm 2024 có 335/366 ngày (thiếu 31 ngày Tháng 3/2024, OR-05 = OPEN_QUALITY_DEFECT); ma trận an toàn thời gian 4 cấp; kịch bản verify_t004_time_representation.py đạt 90/90 PASS (bản lịch sử 61 PASS là snapshot trung gian). |
  | **T-005** | **CONDITIONAL_NO_GO** *(Sau khi duyệt FP-DEC-017)* | `T005_FINAL_AUDIT_RECONCILIATION.md`, `T005_EVIDENCE_MATRIX.md`, `T005_TS011_TEST_SPEC.md`, `T005_CONDITIONAL_NO_GO_PROPOSAL.md`, `T005_R2_1_REVIEWER_ADDENDUM.md` | Hoàn tất kiểm toán 6 trường thời tiết (khuyết 2016: Origin 0.1624%, Dest 0.1639%; tổng 9 năm: Origin 0.0246%, Dest 0.0275%); thiếu timestamp quan trắc, mã trạm và license; hủy chọn RQ-06/KPI-10 (OR-07 = MITIGATED_BY_SCOPE_EXCLUSION); giữ nguyên schema đọc 34 cột theo DC-07; 8 CORE KPIs độc lập 100%. |
  ```

### 4.2. Rà soát [`docs/04-execution/AI_HANDOFF.md`](../04-execution/AI_HANDOFF.md)
- **Các điểm lỗi thời hiện tại:**
  1. Dòng 14–15: Vẫn ghi *"Timestamp representation 2016–2023 processed only; unknown 2400/rollover/2024 full"* và *"Source flight grain, FLIGHTS, canceled/diverted coverage, Weather units/timing/join, numeric units, national representativeness OPEN"*. Thực tế `T-001..T-005` đã kiểm toán xong các mục này và chuyển hóa thành các hợp đồng/rủi ro cụ thể (`OR-01..OR-08`).
  2. Dòng 19: Ghi `G2 DRAFT/NOT_PASSED` mà chưa trỏ tới bộ hồ sơ bằng chứng `T001..T005`, `G2_R1_*` và `G2_SIGNOFF_*`.
  3. Lưu ý kỹ thuật: `AI_HANDOFF.md` nằm trong danh sách kiểm tra hash SHA-256 cứng của `PACKAGE_MANIFEST.json`. Do đó, chỉ được phép cập nhật tệp này khi Project Lead đồng thời phê duyệt cơ chế cập nhật manifest cho `governed_living_docs`.
- **Văn bản thay thế đề xuất (`PROPOSED_POST_SIGNOFF_TEXT — DO NOT APPLY BEFORE HUMAN APPROVAL`):**
  ```markdown
  <!-- PROPOSED_POST_SIGNOFF_TEXT CHO AI_HANDOFF.md MỤC VERIFIED VS UNRESOLVED -->
  ## Verified vs unresolved (Post-G2 Audit Baseline)
  - Source audits 9 năm, 34 columns, 54,674,003 rows; ARR_DELAY >= 15 count = 10,116,916 (~18.5041%). **NOT** Spark runtime execution.
  - Grain & Denominator (T-002): Scheduled Flight Leg Record; `FLIGHTS = 1.0` hằng số trên 100% dòng (`OR-01`, cấm làm trọng số); mẫu số chuẩn là `count_records(C)` trên tập `accepted`; bảo toàn cặp trùng khóa ứng viên duy nhất `YX 3624` (`2018-06-21 DEN->XNA`, dòng 6,384,132 & 6,384,133, `OR-02`, `TS-021`).
  - CORE KPIs & Units (T-003): 8 CORE KPIs (`KPI-01..08`) đã khóa công thức; `KPI-11` (cancel/divert) = `NOT_COMPUTABLE` (`OR-04`); `KPI-12` = `BLOCKED`; 7 trường thời lượng/độ trễ mang nhãn `OFFICIAL_MINUTES_EMPIRICALLY_CONSISTENT_PROVISIONAL` (`OR-03`, đối chiếu BTS tại G5 `TS-018`); P50/P90 dùng `percentile_approx` GK-sketch `accuracy=10000` (`FP-DEC-015`); ngưỡng xếp hạng min-N là `1000 / 365 / 100` (`FP-DEC-016`).
  - Safe Time & 2024 Coverage (T-004): Cấm trừ trực tiếp timestamp và cấm cộng `+24h` (`OR-06`, `FP-DEC-007`); năm 2024 chỉ có `335/366` ngày do khuyết toàn bộ 31 ngày Tháng 3/2024 (`OR-05 = OPEN_QUALITY_DEFECT`, ngày nhuận `2024-02-29` có 18,642 dòng).
  - Weather Usability (T-005): Nhánh tùy chọn `RQ-06` / `KPI-10` được đề xuất/chốt `CONDITIONAL_NO_GO` (`FP-DEC-017`, `OR-07 = MITIGATED_BY_SCOPE_EXCLUSION`); bảo toàn 34 cột raw theo `DC-07`.
  - Raw Content Identity (`OR-08`): Đang ở mức `METADATA_MATCH_ONLY / IDENTITY_UNVERIFIED`; bắt buộc tính SHA-256 nội bộ cho 9 CSV thô tại Gate G4 (`T-007` / `TS-019`).
  ```

### 4.3. Rà soát [`docs/04-execution/DEPLOYMENT.md`](../04-execution/DEPLOYMENT.md)
- **Đánh giá hiện trạng:**
  - Dòng 3 ghi rõ: **`Status: NOT_READY / DOCUMENTATION ONLY.`**
  - **Khẳng định quản trị:** Trạng thái `NOT_READY / DOCUMENTATION ONLY` của `DEPLOYMENT.md` là **HOÀN TOÀN CHÍNH XÁC** tại thời điểm hiện tại và bắt buộc phải giữ nguyên qua cả Gate G2 và Gate G3, vì dự án chưa có mã nguồn PySpark thực thi và chưa có bằng chứng chạy runtime.
- **Bổ sung nhỏ đề xuất trong tương lai (tại Gate G4/G5):**
  - Khi cập nhật ở Gate G4/G5, bổ sung tham chiếu tường minh đến bài kiểm thử `TS-019` (khóa SHA-256 của 9 CSV vào Ingestion Manifest) và kiểm tra lịch 366 ngày vs 335 ngày thực tế của năm 2024 (`OR-05` / `TS-004`).

### 4.4. Rà soát [`docs/04-execution/TASK_TEMPLATE.md`](../04-execution/TASK_TEMPLATE.md)
- **Các điểm thiếu sót hiện tại:**
  - Mục `Deliverables và acceptance` (dòng 23–27) và `Kết quả bắt buộc` (dòng 36–41) chưa quy định rõ quy trình kiểm chứng xuất tệp bằng chứng (*Post-Export Filesystem Verification*) đã được áp dụng từ T-004/T-005/G2.
- **Văn bản bổ sung đề xuất (`PROPOSED_POST_SIGNOFF_TEXT — DO NOT APPLY BEFORE HUMAN APPROVAL`):**
  ```markdown
  <!-- PROPOSED_POST_SIGNOFF_TEXT BỔ SUNG VÀO MỤC KẾT QUẢ BẮT BUỘC CỦA TASK_TEMPLATE.md -->
  - Phân biệt rõ trạng thái kiểm thử: `SPECIFIED / NOT_RUN` (thiết kế trên giấy) vs `EXECUTED_PASS / EXECUTED_FAIL` (có lệnh chạy và exit code thực).
  - Post-Export Verification bắt buộc cho mọi artifact tạo mới:
    1. Kiểm tra tồn tại trên đĩa, dung lượng byte > 0 và đọc lại xác thực UTF-8.
    2. Tính và ghi nhận mã băm SHA-256 của các tệp deliverable vào manifest nhiệm vụ.
    3. Kiểm tra 100% liên kết tương đối Markdown phân giải thành công và không vi phạm quy tắc đường dẫn của `check_working_tree_consistency.py`.
    4. Bảo toàn nguyên vẹn mã rủi ro gốc (`R-01..R-17` và `OR-01..OR-08`), không tự ý gán lại ý nghĩa mã rủi ro.
  ```

---
*Tài liệu này thuộc gói chuẩn bị phê duyệt Gate G2 (`G2-SIGNOFF-PREP`). Không một tệp quản trị hiện hữu nào bị chỉnh sửa.*
