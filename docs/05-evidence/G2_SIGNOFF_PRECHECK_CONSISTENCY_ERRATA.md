# G2-SIGNOFF-HANDOFF-FIX — BÁO CÁO ĐÍNH CHÍNH NHẤT QUÁN LIÊN TÀI LIỆU (`G2_SIGNOFF_PRECHECK_CONSISTENCY_ERRATA.md`)

**Document ID:** `G2-SIGNOFF-PRECHECK-ERRATA-001`  
**Task ID:** `G2-SIGNOFF-HANDOFF-FIX`  
**Dự án:** Phân tích hiệu suất chuyến bay Hoa Kỳ 2016–2024 bằng Apache Spark / PySpark  
**Vai trò:** Senior Big Data Evidence Quality Auditor & Independent Governance Reviewer  
**Phạm vi:** Đính chính các sai lệch mã quyết định (`FP-DEC-###`), phạm vi `KPI-01..12`, ngưỡng `min-N`, thông tin kiểm kê trong [`G2_SIGNOFF_FINAL_PRECHECK_MANIFEST.md`](G2_SIGNOFF_FINAL_PRECHECK_MANIFEST.md), điểm tinh chỉnh tại [`G2_SIGNOFF_FINAL_PRECHECK_ADDENDUM.md`](G2_SIGNOFF_FINAL_PRECHECK_ADDENDUM.md) và phản hồi bàn giao của Agent ở bước `G2-SIGNOFF-PRECHECK` (`design/documentation only`)  
**Trạng thái Gate G2 hiện hành:** **`IN_PROGRESS / NOT_PASSED`**  
**Trạng thái Nhiệm vụ `T-006` hiện hành:** **`NOT_STARTED`**  
**Kết luận Đối chiếu:** **`DOCUMENTATION_RECONCILED`**  
**Ngày lập:** 2026-10-16

---

## 1. TÓM TẮT ĐIỀU HÀNH (EXECUTIVE SUMMARY)

Trong bước `G2-SIGNOFF-PRECHECK` trước đó, mặc dù tệp phụ lục [`G2_SIGNOFF_FINAL_PRECHECK_ADDENDUM.md`](G2_SIGNOFF_FINAL_PRECHECK_ADDENDUM.md) đã sử dụng đúng các mã quyết định `FP-DEC-015`, `FP-DEC-016` và `FP-DEC-PROP-015` (cùng ngưỡng `min-N = 1,000 / 365 / 100`), **tệp manifest [`G2_SIGNOFF_FINAL_PRECHECK_MANIFEST.md`](G2_SIGNOFF_FINAL_PRECHECK_MANIFEST.md)** và **phản hồi bàn giao (final response) của Agent** lại phát sinh sự trượt mã định danh nghiêm trọng (*identifier drift*) và sai lệch thông tin kiểm kê so với các văn bản gốc [`DECISIONS.md`](../02-design/DECISIONS.md), [`KPI_SPEC.md`](../02-design/KPI_SPEC.md), [`DATA_CONTRACT.md`](../02-design/DATA_CONTRACT.md), [`T003_PERCENTILE_AND_MIN_N_DECISIONS.md`](T003_PERCENTILE_AND_MIN_N_DECISIONS.md), [`T005_CONDITIONAL_NO_GO_PROPOSAL.md`](T005_CONDITIONAL_NO_GO_PROPOSAL.md) và [`G2_R1_CORRECTED_GATE_READINESS.md`](G2_R1_CORRECTED_GATE_READINESS.md).

Báo cáo đính chính (`Errata`) này thực hiện:
1. **Bác bỏ và hủy bỏ hiệu lực tham chiếu** của mọi mệnh đề sai lệch trong phản hồi bàn giao trước đó của Agent và trong [`G2_SIGNOFF_FINAL_PRECHECK_MANIFEST.md`](G2_SIGNOFF_FINAL_PRECHECK_MANIFEST.md) mà **không ghi đè lịch sử tệp cũ**.
2. **Khóa chặt bảng ánh xạ chuẩn tắc (`Mandatory Fact Lock`)** đối với toàn bộ hệ thống mã quyết định `FP-DEC-001..016`, `FP-DEC-PROP-015` (và mã dự kiến `FP-DEC-017` sau khi được phê duyệt), danh mục `KPI-01..12` và ngưỡng `min-N` (`1,000 / 365 / 100`).
3. **Tinh chỉnh ranh giới bằng chứng cho `G2-EXC-001` và `DC-12` (`CHECK-01`, `CHECK-02`):** Không tuyên bố nhiệm vụ hiện tại đã tự quét lại 54,674,003 dòng dữ liệu thô (chỉ đối chiếu từ báo cáo kiểm toán lịch sử); đồng thời bảo vệ trường `provenance_reference` như một con trỏ bằng chứng nguồn gốc — không ghi đè mã lý do khuyết Tháng 3/2024 lên `provenance_reference`.
4. **Giữ nguyên trạng thái trung thực của các công cụ kiểm tra và cổng kiểm soát:** `Gate G2 = IN_PROGRESS / NOT_PASSED`, `T-006 = NOT_STARTED`, không một quyết định `PROPOSED` nào được tự động duyệt.

---

## 2. BẢNG KHÓA SỰ THẬT CHUẨN TẮC (CANONICAL FACT LOCK)

Đối chiếu trực tiếp từ [`docs/02-design/DECISIONS.md`](../02-design/DECISIONS.md), [`docs/02-design/KPI_SPEC.md`](../02-design/KPI_SPEC.md), [`docs/02-design/DATA_CONTRACT.md`](../02-design/DATA_CONTRACT.md), [`docs/05-evidence/T003_PERCENTILE_AND_MIN_N_DECISIONS.md`](T003_PERCENTILE_AND_MIN_N_DECISIONS.md) và [`docs/05-evidence/T005_CONDITIONAL_NO_GO_PROPOSAL.md`](T005_CONDITIONAL_NO_GO_PROPOSAL.md), dưới đây là bảng ánh xạ chuẩn tắc duy nhất có hiệu lực:

### 2.1. Ánh xạ Chuẩn tắc Các Quyết định Kiến trúc (`FP-DEC-###`)

| Mã Quyết định | Nội dung Chuẩn tắc theo Tài liệu Thẩm quyền | Trạng thái Hiện tại trong Nguồn Gốc | Nguồn Thẩm quyền Chính thức |
| :--- | :--- | :--- | :--- |
| **`FP-DEC-001`** | Đồ án **phân tích hiệu suất chuyến bay Mỹ 2016–2024** (mô tả), không tập trung ML | `USER_CONFIRMED` | [`DECISIONS.md` dòng 7](../02-design/DECISIONS.md#L7) |
| **`FP-DEC-002`** | Dùng cả năm **2024** cho phân tích mô tả hồi cứu, không gọi là sealed ML holdout của đề tài cũ | `USER_CONFIRMED_BY_SCOPE` | [`DECISIONS.md` dòng 8](../02-design/DECISIONS.md#L8) |
| **`FP-DEC-003`** | **Machine Learning, ATL-only, Flight Chain `.pt`, Flight Network** nằm ngoài CORE (không đọc `.pt`) | `PROPOSED_IMPLEMENTATION` | [`DECISIONS.md` dòng 9](../02-design/DECISIONS.md#L9) |
| **`FP-DEC-004`** | **Raw data immutable** + đầu ra phân phiên bản theo `run_id` (kế thừa tinh thần D013 lịch sử) | `PROPOSED_CONTROL` | [`DECISIONS.md` dòng 10](../02-design/DECISIONS.md#L10) |
| **`FP-DEC-005`** | Dùng **PySpark + Parquet** cho xử lý chính *(nhãn `005A`/`005B` chỉ là nhãn tách cấu phần đề xuất để trình duyệt, không phải ADR độc lập đã được phê duyệt)* | `PROPOSED` | [`DECISIONS.md` dòng 11](../02-design/DECISIONS.md#L11) |
| **`FP-DEC-006`** | Cấm lập KPI canceled/diverted từ 34 trường hiện có | `PROPOSED_GUARD` | [`DECISIONS.md` dòng 12](../02-design/DECISIONS.md#L12) |
| **`FP-DEC-007`** | Không tính timeline qua đêm bằng `CRS_ARR_TIME` date component (safe temporal representation guard) | `PROPOSED_GUARD` | [`DECISIONS.md` dòng 13](../02-design/DECISIONS.md#L13) |
| **`FP-DEC-008`** | Dùng ngưỡng `ARR_DELAY >= 15` cho KPI trễ đến có mẫu số hữu hạn | `PROPOSED_KPI` | [`DECISIONS.md` dòng 14](../02-design/DECISIONS.md#L14) |
| **`FP-DEC-009`** | Weather chỉ mở rộng có điều kiện, không kết luận nguyên nhân (block `RQ-06` trước `T-005`) | `PROPOSED` | [`DECISIONS.md` dòng 15](../02-design/DECISIONS.md#L15) |
| **`FP-DEC-010`** | Không dùng `FLIGHTS` làm trọng số trước xác minh grain; mẫu số báo `accepted` row-based (`count_records`) | `PROPOSED_GUARD` | [`DECISIONS.md` dòng 16](../02-design/DECISIONS.md#L16) |
| **`FP-DEC-011`** | Chính thức phân biệt `metric_valid_rate` với `source_coverage_status`; các tập row `accepted`/`quarantined`/`rejected` loại trừ lẫn nhau (`DC-11/12`) | `PROPOSED_CONTROL` | [`DECISIONS.md` dòng 17](../02-design/DECISIONS.md#L17) |
| **`FP-DEC-012`** | Có **8 CORE KPI** và phải xác minh đơn vị/dấu/miền của **7 measures cốt lõi** trước G2 (`T-003` + `TS-018`) | `PROPOSED_REQUIREMENT` | [`DECISIONS.md` dòng 18](../02-design/DECISIONS.md#L18) |
| **`FP-DEC-013`** | Weather là `Should/conditional`: explicit `GO` hoặc `CONDITIONAL_NO_GO`, không chặn G2/G6 CORE | `PROPOSED_CONTROL` | [`DECISIONS.md` dòng 19](../02-design/DECISIONS.md#L19) |
| **`FP-DEC-014`** | Metadata `size/mtime` chỉ cảnh báo drift, không chứng minh raw content identity (`IDENTITY_UNVERIFIED` khi chưa rõ) | `PROPOSED_CONTROL` | [`DECISIONS.md` dòng 20](../02-design/DECISIONS.md#L20) |
| **`FP-DEC-015`** | Đề xuất phương pháp tính phân vị xấp xỉ cho `KPI-06`: PySpark `percentile_approx` (GK-sketch, `accuracy = 10000`, chặn sai số thứ hạng tương đối $\epsilon_{\text{rank}} \le 0.01\%$) | `PROPOSED_DECISION_PENDING_REVIEW` *(chưa phê duyệt)* | [`T003_PERCENTILE_AND_MIN_N_DECISIONS.md` dòng 60–84, 141](T003_PERCENTILE_AND_MIN_N_DECISIONS.md#L60-L84) |
| **`FP-DEC-016`** | Đề xuất chính sách ngưỡng cỡ mẫu tối thiểu (`min-N`) cho bảng xếp hạng:<br>- `carrier-year >= 1,000`<br>- `airport-year >= 365`<br>- `route-year >= 100` | `PROPOSED_DECISION_PENDING_REVIEW` *(chưa phê duyệt)* | [`T003_PERCENTILE_AND_MIN_N_DECISIONS.md` dòng 115–136, 141](T003_PERCENTILE_AND_MIN_N_DECISIONS.md#L115-L136) |
| **`FP-DEC-PROP-015`** | Đề xuất ban hành phán quyết `CONDITIONAL_NO_GO` cho nhánh phân tích thời tiết tùy chọn (`RQ-06` / `KPI-10`) | `PROPOSAL_PENDING_REVIEW` *(chưa phê duyệt)* | [`T005_CONDITIONAL_NO_GO_PROPOSAL.md` dòng 9–15](T005_CONDITIONAL_NO_GO_PROPOSAL.md#L9-L15) |
| **`FP-DEC-017`** | Mã định danh chính thức dự kiến (reserved/proposed canonical ID) chỉ được cấp cho quyết định `CONDITIONAL_NO_GO` của Weather (`FP-DEC-PROP-015`) **sau khi có phê duyệt hợp lệ của Human Reviewer** để tránh trùng mã `FP-DEC-015` với `T-003` | `RESERVED_PENDING_HUMAN_APPROVAL` *(chưa tồn tại trong `DECISIONS.md`)* | [`G2_SIGNOFF_DECISION_APPROVAL_MATRIX.md` dòng 18–21, 49](G2_SIGNOFF_DECISION_APPROVAL_MATRIX.md#L18-L21) |

### 2.2. Ánh xạ Chuẩn tắc Danh mục Chỉ số (`KPI-01` đến `KPI-12`)

Theo [`docs/02-design/KPI_SPEC.md`](../02-design/KPI_SPEC.md#L3-L25) (dòng 3 và bảng dòng 12–25):

| Nhóm / Mã KPI | Tên chỉ số | Phân loại Chuẩn tắc | Trạng thái trong `KPI_SPEC.md` | Câu hỏi Nghiên cứu |
| :--- | :--- | :--- | :--- | :--- |
| **`KPI-01..KPI-08`** | **8 Chỉ số Cốt lõi (CORE KPIs):**<br>- `KPI-01`: Tổng bản ghi accepted (`count_records(C)`)<br>- `KPI-02`: Tỷ lệ trễ đến `ARR_DELAY >= 15`<br>- `KPI-03`: Trễ đến trung bình có dấu (`mean signed ARR_DELAY`)<br>- `KPI-04`: Tỷ lệ trễ đi `DEP_DELAY >= 15`<br>- `KPI-05`: Trễ đi trung bình có dấu (`mean signed DEP_DELAY`)<br>- `KPI-06`: Phân vị `P50 / P90` độ trễ đến (`ARR_DELAY`)<br>- `KPI-07`: Taxi-out và Taxi-in trung bình (2 submetrics độc lập)<br>- `KPI-08`: Air / Actual / CRS Elapsed Time trung bình (3 submetrics độc lập) | **`CORE`** (8 CORE KPIs) | `CORE_DRAFT` | `RQ-01..RQ-05` |
| **`KPI-09`** | Trung bình số phút trễ dương trên mỗi bản ghi hợp lệ (`sum(max(ARR_DELAY,0)) / N_valid`) | **`OPTIONAL`** | `OPTIONAL_DRAFT` | `RQ-02` |
| **`KPI-10`** | Độ trễ phân tầng theo điều kiện thời tiết (*Weather-conditioned delay*) | **`CONDITIONAL / WEATHER`** | `CONDITIONAL_PENDING` | `RQ-06` |
| **`KPI-11`** | Tỷ lệ hủy chuyến / chuyển hướng (*Cancel/divert rate*) | **`NOT_COMPUTABLE`** | `NOT_COMPUTABLE` | Ngoài CORE |
| **`KPI-12`** | Tổng lượt theo cột `FLIGHTS` | **`BLOCKED`** | `BLOCKED` | Ngoài CORE |

---

## 3. KIỂM TOÁN CHI TIẾT CÁC PHÁT HIỆN SAI LỆCH & BẢNG ĐỐI CHIẾU HỒI QUY (CROSS-DOCUMENT REGRESSION MATRIX)

### 3.1. Hạng mục A — Bác bỏ Sai lệch Mã Quyết định & Ngưỡng `min-N` trong Phản hồi Bàn giao Trước đó của Agent (`Agent Final Response`)

Tại Mục 4 (*"Các quyết định cần Human Reviewer phê duyệt để đóng Gate G2"*) của phản hồi bàn giao cuối phiên `G2-SIGNOFF-PRECHECK`, Agent đã tóm tắt sai hoàn toàn hệ thống mã `FP-DEC-###` và con số ngưỡng `min-N`. Các tuyên bố đó **bị bác bỏ hoàn toàn (EXPLICITLY REJECTED)** theo bảng dưới đây:

| STT | Tuyên bố sai trong Phản hồi Bàn giao Trước đó của Agent | Nguồn Gốc Bị Vi phạm | Sự thật Chuẩn tắc sau Đính chính (`DOCUMENTATION_RECONCILED`) |
| :---: | :--- | :--- | :--- |
| **A-01** | Gán `FP-DEC-002` cho *"Phê duyệt phép tính phân vị chính xác + `approx_percentile` có kiểm soát sai số"* | [`DECISIONS.md` dòng 8](../02-design/DECISIONS.md#L8)<br>[`T003_PERCENTILE_AND_MIN_N_DECISIONS.md` dòng 60](T003_PERCENTILE_AND_MIN_N_DECISIONS.md#L60) | **BÁC BỎ.** `FP-DEC-002` là quyết định phạm vi: *"Dùng cả 2024 cho phân tích mô tả, không gọi là sealed ML holdout của đề tài cũ"* (trạng thái `USER_CONFIRMED_BY_SCOPE`). Đề xuất thuật toán phân vị xấp xỉ cho `KPI-06` mang mã **`FP-DEC-015`** (`PROPOSED_DECISION_PENDING_REVIEW`). |
| **A-02** | Gán `FP-DEC-003` cho *"Phê duyệt ngưỡng cỡ mẫu tối thiểu `min_n` (`100` / `30` / `1,000`) và nhãn `LOW_SAMPLE` / `SUPPRESSED`"* | [`DECISIONS.md` dòng 9](../02-design/DECISIONS.md#L9)<br>[`T003_PERCENTILE_AND_MIN_N_DECISIONS.md` dòng 119–136](T003_PERCENTILE_AND_MIN_N_DECISIONS.md#L119-L136) | **BÁC BỎ KÉP (Sai cả mã quyết định lẫn con số ngưỡng):**<br>1. `FP-DEC-003` là quyết định loại trừ *"Machine Learning, ATL-only, Flight Chain `.pt`, Flight Network nằm ngoài CORE"* (`PROPOSED_IMPLEMENTATION`).<br>2. Chính sách ngưỡng cỡ mẫu tối thiểu (`min-N`) mang mã **`FP-DEC-016`** (`PROPOSED_DECISION_PENDING_REVIEW`).<br>3. Bộ ngưỡng chuẩn của `FP-DEC-016` là **`carrier-year >= 1,000`**, **`airport-year >= 365`**, **`route-year >= 100`** (với ngưỡng cảnh báo $3 \times N_{\min}$ là `3,000 / 1,095 / 300` và 3 trạng thái `SUPPRESSED`, `LOW_SAMPLE_CAUTION`, `SUFFICIENT`), **tuyệt đối không có ngưỡng `30`**. |
| **A-03** | Gán `FP-DEC-004` cho *"(`T-005` Weather Scope): Phê duyệt `CONDITIONAL_NO_GO` cho nhánh tùy chọn `RQ-06 / KPI-10`"* | [`DECISIONS.md` dòng 10, 15, 19](../02-design/DECISIONS.md#L10)<br>[`T005_CONDITIONAL_NO_GO_PROPOSAL.md` dòng 9](T005_CONDITIONAL_NO_GO_PROPOSAL.md#L9) | **BÁC BỎ.** `FP-DEC-004` là quyết định *"Raw immutable + output version theo run"* (`PROPOSED_CONTROL`). Các quy định khung về Weather trong `DECISIONS.md` là **`FP-DEC-009`** và **`FP-DEC-013`**, còn đề xuất ban hành `CONDITIONAL_NO_GO` của `T-005` mang mã đề xuất **`FP-DEC-PROP-015`** (dự kiến cấp mã chính thức **`FP-DEC-017`** chỉ sau khi được Human Reviewer phê duyệt). |
| **A-04** | Gán `FP-DEC-006` cho *"(`DC-12` / `OR-05`): Phê duyệt giữ nguyên `source_coverage_status = 'PARTIAL'` cho năm 2024"* | [`DECISIONS.md` dòng 12, 17](../02-design/DECISIONS.md#L12) | **BÁC BỎ.** `FP-DEC-006` là quyết định *"Cấm canceled/diverted KPI từ 34 trường hiện có"* (`PROPOSED_GUARD`). Quyết định phân biệt `metric_valid_rate` với `source_coverage_status` theo `DC-11/12` mang mã **`FP-DEC-011`**, và chính sách ngưỡng xếp hạng kèm cảnh báo năm 2024 mang mã **`FP-DEC-016`** (kết hợp quản trị khuyết tật mở **`OR-05`**). |
| **A-05** | Gán `FP-DEC-008` cho *"Phê duyệt loại trừ hoàn toàn bài toán dự báo `T-2h`, `ATL`, Machine Learning và Flight Chain"* | [`DECISIONS.md` dòng 9, 14](../02-design/DECISIONS.md#L9) | **BÁC BỎ.** `FP-DEC-008` là quyết định *"Dùng ngưỡng `ARR_DELAY >= 15` cho KPI trễ đến có mẫu số hữu hạn"* (`PROPOSED_KPI`). Việc loại trừ ML, ATL-only và Flight Chain `.pt` thuộc về **`FP-DEC-003`** (và phần cấm áp dụng quy tắc dự báo lịch sử `T-2h/ATL` được nêu tại `DECISIONS.md` mục Phân loại quyết định cũ dòng 22–23 cùng `AGENTS.md` dòng 9). |

---

### 3.2. Hạng mục B — Kiểm toán và Đính chính Các Sai lệch trong [`G2_SIGNOFF_FINAL_PRECHECK_MANIFEST.md`](G2_SIGNOFF_FINAL_PRECHECK_MANIFEST.md)

Rà soát từng dòng trong [`docs/05-evidence/G2_SIGNOFF_FINAL_PRECHECK_MANIFEST.md`](G2_SIGNOFF_FINAL_PRECHECK_MANIFEST.md) phát hiện **7 lỗi mô tả kiểm kê (Inventory & Citation Regressions)** cần đính chính chính thức:

| Mã Lỗi | Vị trí trong `G2_SIGNOFF_FINAL_PRECHECK_MANIFEST.md` | Nội dung ghi sai trong Manifest cũ | Nội dung Đính chính Chuẩn xác theo Nguồn Gốc |
| :---: | :--- | :--- | :--- |
| **B-01** | Mục 1.1, Dòng 21 ([`DECISIONS.md`](../02-design/DECISIONS.md)) | *"Baseline status of `FP-DEC-001` through `FP-DEC-008` (`FP-DEC-001` = `APPROVED`; `FP-DEC-002..008` = `PROPOSED`)"* | [`docs/02-design/DECISIONS.md`](../02-design/DECISIONS.md#L7-L20) chứa **14 quyết định (`FP-DEC-001` đến `FP-DEC-014`)**, trong đó: `FP-DEC-001` = **`USER_CONFIRMED`**, `FP-DEC-002` = **`USER_CONFIRMED_BY_SCOPE`**, và `FP-DEC-003` đến `FP-DEC-014` mang các trạng thái **`PROPOSED_*`** (`PROPOSED_IMPLEMENTATION`, `PROPOSED_CONTROL`, `PROPOSED`, `PROPOSED_GUARD`, `PROPOSED_KPI`, `PROPOSED_REQUIREMENT`). Không có quyết định nào mang chuỗi trạng thái `APPROVED` trong tệp gốc. |
| **B-02** | Mục 1.1, Dòng 22 ([`DATA_CONTRACT.md`](../02-design/DATA_CONTRACT.md)) | *"`DC-12` strict taxonomy (`source_coverage_status = UNKNOWN/PARTIAL/VERIFIED_WITH_SCOPE`), `DC-04` overnight rollover prohibition, `DC-08` units verification requirement"* | Trong [`docs/02-design/DATA_CONTRACT.md`](../02-design/DATA_CONTRACT.md#L16-L22):<br>- Quy tắc giữ nguyên text thời gian và không dựng overnight/zone timestamp trước T-004 là **`DC-02`** (dòng 16).<br>- Quy tắc về đơn vị và miền giá trị của 5 trường thời lượng (`TAXI_OUT`, `TAXI_IN`, `AIR_TIME`, `ACTUAL_ELAPSED_TIME`, `CRS_ELAPSED_TIME`) là **`DC-04`** (dòng 18), kết hợp với **`DC-03`** cho `ARR_DELAY`/`DEP_DELAY` (dòng 17).<br>- Còn **`DC-08`** (dòng 22) là quy tắc kiểm chứng `MONTH`, `DAY_OF_MONTH`, `DAY_OF_WEEK` so với service date. |
| **B-03** | Mục 1.1, Dòng 23 ([`KPI_SPEC.md`](../02-design/KPI_SPEC.md)) | *"Mandatory KPI summary columns (`source_coverage_status`, `provenance_reference`, `unit_status`), `KPI-01..09` CORE vs `KPI-10` Optional Weather rules"* | Trong [`docs/02-design/KPI_SPEC.md`](../02-design/KPI_SPEC.md#L3-L25):<br>- Chỉ có **8 CORE KPIs là `KPI-01..KPI-08`** (`CORE_DRAFT`).<br>- **`KPI-09`** là **`OPTIONAL_DRAFT`** (Trung bình số phút trễ dương trên mỗi bản ghi hợp lệ), **không thuộc CORE**.<br>- **`KPI-10`** là **`CONDITIONAL_PENDING`** (Weather-conditioned delay).<br>- **`KPI-11`** là **`NOT_COMPUTABLE`** và **`KPI-12`** là **`BLOCKED`**. |
| **B-04** | Mục 1.1, Dòng 24 ([`DATA_DICTIONARY.md`](../02-design/DATA_DICTIONARY.md)) & Dòng 27 ([`TEST_PLAN.md`](../03-quality/TEST_PLAN.md)) | Dòng 24: *"26-column dictionary..."*<br>Dòng 27: *"`TS-001` through `TS-018` test specifications..."* | - [`docs/02-design/DATA_DICTIONARY.md`](../02-design/DATA_DICTIONARY.md) đặc tả đầy đủ **34 cột (34-column schema)** được gom nhóm trong 26 dòng của bảng tóm tắt, kèm dòng cảnh báo `unit_status = UNVERIFIED` ở dòng 5.<br>- [`docs/03-quality/TEST_PLAN.md`](../03-quality/TEST_PLAN.md#L7-L26) đặc tả **20 bài kiểm thử từ `TS-001` đến `TS-020`** (không phải chỉ đến `TS-018`). |
| **B-05** | Mục 1.2, Dòng 42 ([`G2_R1_CORRECTED_GATE_READINESS.md`](G2_R1_CORRECTED_GATE_READINESS.md)) | *"Latest G2 technical readiness review (`READY_FOR_HUMAN_SIGNOFF`)"* | Phán quyết thẩm định chính thức ghi tại dòng 9 và dòng 119 của [`G2_R1_CORRECTED_GATE_READINESS.md`](G2_R1_CORRECTED_GATE_READINESS.md#L9) là **`READY_WITH_EXPLICIT_CONDITIONS`** (không phải `READY_FOR_HUMAN_SIGNOFF`). |
| **B-06** | Mục 1.2, Dòng 46 ([`T003_PERCENTILE_AND_MIN_N_DECISIONS.md`](T003_PERCENTILE_AND_MIN_N_DECISIONS.md)) | *"Verified `FP-DEC-002` and `FP-DEC-003` technical records"* | [`T003_PERCENTILE_AND_MIN_N_DECISIONS.md`](T003_PERCENTILE_AND_MIN_N_DECISIONS.md#L60-L141) là tài liệu đề xuất kỹ thuật cho **`FP-DEC-015`** (Thuật toán phân vị P50/P90 cho `KPI-06`) và **`FP-DEC-016`** (Chính sách ngưỡng cỡ mẫu tối thiểu `min-N = 1,000 / 365 / 100`), **không phải** `FP-DEC-002` và `FP-DEC-003`. |
| **B-07** | Mục 1.2, Dòng 48 ([`T005_CONDITIONAL_NO_GO_PROPOSAL.md`](T005_CONDITIONAL_NO_GO_PROPOSAL.md)) | *"Verified `FP-DEC-004 = CONDITIONAL_NO_GO` and `T-005 = CONDITIONAL_PENDING`"* | [`T005_CONDITIONAL_NO_GO_PROPOSAL.md`](T005_CONDITIONAL_NO_GO_PROPOSAL.md#L9-L15) đệ trình đề xuất **`FP-DEC-PROP-015`** (*Disposition of Optional Weather Analysis RQ-06 / KPI-10* với trạng thái `PROPOSAL_PENDING_REVIEW`), dự kiến mang mã chính thức **`FP-DEC-017`** nếu được duyệt, **không phải** `FP-DEC-004`. Ngoài ra, dòng 54 của Manifest ghi `data/raw/*.parquet` trong khi định dạng dữ liệu thô thực tế theo [`DATA_CONTRACT.md`](../02-design/DATA_CONTRACT.md#L6) là 9 tệp CSV (`data/raw/tabular/{year}/flight_with_weather_{year}.csv`). |

---

### 3.3. Hạng mục C — Kiểm chứng và Tinh chỉnh `G2-EXC-001` Đối chiếu với Yêu cầu Đóng Gate G2 Thực tế

Đối chiếu Mục 2.2 (`CHECK-02`) của [`G2_SIGNOFF_FINAL_PRECHECK_ADDENDUM.md`](G2_SIGNOFF_FINAL_PRECHECK_ADDENDUM.md#L65-L87) với [`AGENTS.md`](../../AGENTS.md#L13), [`DATA_CONTRACT.md`](../02-design/DATA_CONTRACT.md#L17-L18), [`KPI_SPEC.md`](../02-design/KPI_SPEC.md#L28) và [`TEST_PLAN.md`](../03-quality/TEST_PLAN.md#L24), báo cáo này khóa chặt **4 sự phân biệt bắt buộc** đối với ngoại lệ đơn vị đo `G2-EXC-001`:

1. **Đơn vị phút nhất quán thực nghiệm tạm thời (`Empirically Consistent Provisional Minute Units`):**
   - Nhãn `OFFICIAL_MINUTES_EMPIRICALLY_CONSISTENT_PROVISIONAL` phản ánh việc các báo cáo kiểm toán lịch sử của `T-003` ([`T003_UNIT_VERIFICATION.md`](T003_UNIT_VERIFICATION.md)) và `T-004` ([`T004_FINAL_QA_RECONCILIATION.md`](T004_FINAL_QA_RECONCILIATION.md)) đã ghi nhận sự khớp nhau về mặt đại số giữa 7 cột số đo (`ARR_DELAY`, `DEP_DELAY`, `TAXI_OUT`, `TAXI_IN`, `AIR_TIME`, `ACTUAL_ELAPSED_TIME`, `CRS_ELAPSED_TIME`) và khoảng cách giờ lịch trình.
   - **Tuyên bố trung thực về phạm vi thực thi (`No Fabricated Full-Scan Claim`):** Tuân thủ [`AGENTS.md` dòng 13](../../AGENTS.md#L13) (*"Không giả mạo việc đã đọc 54,7 triệu hàng hoặc đã chạy Spark nếu chỉ đọc metadata audit"*), các nhiệm vụ chuẩn bị quản trị `G2-R1`, `G2-SIGNOFF-PREP`, `G2-SIGNOFF-PRECHECK` và `G2-SIGNOFF-HANDOFF-FIX` **không tự chạy lại lệnh quét 54,674,003 dòng CSV thô**, mà chỉ tổng hợp số liệu từ 9 tệp `schema_YYYY.json`, các báo cáo kiểm toán `T-001..T-005` đã lưu trữ, và chạy bộ kiểm thử [`tools/qa/verify_t004_time_representation.py`](../../tools/qa/verify_t004_time_representation.py) trên bộ 9 dòng fixture `TF-01..TF-09`.
2. **Ngữ nghĩa trường chuẩn của US DOT / BTS (`Official BTS Field Semantics`):**
   - Theo quy định pháp lý 14 CFR Part 234 và tài liệu BTS On-Time Performance, các trường cùng tên của BTS được định nghĩa theo đơn vị **phút (minutes)**.
3. **Biến đổi chưa xác minh của bên thứ ba đóng gói lại dữ liệu (`Unverified Transformations by Third-Party Data Repackager` — `OR-03`):**
   - Do bộ dữ liệu `flight_with_weather_{year}.csv` là sản phẩm đóng gói lại của bên thứ ba (đã ghép nối thêm thời tiết và chuẩn hóa lại chuỗi thời gian) mà không kèm theo codebook/script gốc hay bản đối chiếu trực tiếp với tệp tải từ BTS TranStats, hiện **chưa có bằng chứng độc lập xác thực 100%** rằng bên thứ ba không thực hiện phép biến đổi nào làm thay đổi đơn vị/miền giá trị gốc của BTS.
4. **Yêu cầu bắt buộc phải có Phê duyệt của Con người (`Mandatory Human Approval for G2-EXC-001`):**
   - Vì [`KPI_SPEC.md` dòng 28](../02-design/KPI_SPEC.md#L28) và [`TEST_PLAN.md` dòng 24 (`TS-018`)](../03-quality/TEST_PLAN.md#L24) yêu cầu xác minh đơn vị của 7 trường đo trước khi Gate G2 PASS (*"Citation/source/protocol cho cả 7 trường hoặc G2 BLOCKED"*), việc hoãn bước đối chiếu bản ghi thực tế với BTS TranStats (`OR-03` / `TS-018`) sang Gate G5 **bắt buộc phải được Project Lead phê duyệt thành một ngoại lệ có điều kiện (`G2-EXC-001`)**.
   - Cho đến khi Project Lead ký duyệt `G2-EXC-001`, ngoại lệ này vẫn ở trạng thái **`PENDING_HUMAN_APPROVAL`**, và mọi đầu ra KPI bị cấm gắn nhãn `'minutes'` như một sự thật đã kiểm chứng tuyệt đối.

---

### 3.4. Hạng mục D — Bảo toàn Tuyệt đối Taxonomy `DC-12` và Vai trò Con trỏ Bằng chứng của `provenance_reference`

Đối chiếu Mục 2.1 (`CHECK-01`) của [`G2_SIGNOFF_FINAL_PRECHECK_ADDENDUM.md`](G2_SIGNOFF_FINAL_PRECHECK_ADDENDUM.md#L46-L62) với [`DATA_CONTRACT.md` dòng 42 (`DC-12`)](../02-design/DATA_CONTRACT.md#L42) và [`KPI_SPEC.md` dòng 8](../02-design/KPI_SPEC.md#L8):

1. **Giữ nguyên 100% tập giá trị hợp lệ của `source_coverage_status` theo `DC-12`:**
   - Trường `source_coverage_status` chỉ nhận một trong 3 giá trị: **`UNKNOWN`**, **`PARTIAL`**, hoặc **`VERIFIED_WITH_SCOPE`**.
   - Đối với mọi bảng báo cáo toàn năm 2024 hoặc tổng hợp đa năm bao gồm năm 2024, giá trị của `source_coverage_status` bắt buộc giữ nguyên là **`PARTIAL`**.
2. **Đính chính quan trọng về trường `provenance_reference` (`Do Not Overwrite Provenance Pointer with Reason Code`):**
   - Tại [`G2_SIGNOFF_FINAL_PRECHECK_ADDENDUM.md`](G2_SIGNOFF_FINAL_PRECHECK_ADDENDUM.md#L60-L61), văn bản trước đó đã gợi ý ghi chuỗi lý do `"OR05_2024_MISSING_MARCH_335_OF_366_DAYS"` trực tiếp vào trường `provenance_reference`.
   - **Đính chính chuẩn hóa:** Trong [`KPI_SPEC.md` dòng 8](../02-design/KPI_SPEC.md#L8), `provenance_reference` là **con trỏ tham chiếu bằng chứng nguồn gốc dữ liệu / manifest kiểm toán** (ví dụ: trỏ tới manifest năm nguồn, `T004_2024_DATE_COVERAGE_AUDIT.md`, hoặc `run_id` manifest). **Tuyệt đối không ghi đè một mã lý do khuyết dữ liệu (`reason code`) đè lên con trỏ bằng chứng nguồn gốc `provenance_reference`**.
   - Thay vào đó:
     - Giữ `source_coverage_status = 'PARTIAL'` theo đúng `DC-12`.
     - Giữ `provenance_reference` làm con trỏ tham chiếu tới hồ sơ bằng chứng/manifest nguồn (nơi tài liệu hóa việc năm 2024 có `335/366` ngày và vắng mặt 31 ngày dịch vụ Tháng 3/2024 theo `OR-05`).
     - Nếu cần một trường mã hóa máy đọc riêng biệt cho lý do bao phủ một phần, **đề xuất (propose)** Project Lead xem xét cho phép bổ sung một trường siêu dữ liệu độc lập (ví dụ: `source_coverage_notes` hoặc `coverage_defect_code = "OR05_2024_MISSING_MARCH_335_OF_366_DAYS"`) trong thiết kế schema đầu ra ở Gate G3 (`T-006`) mà không làm hỏng `source_coverage_status` hay `provenance_reference`.

---

### 3.5. Hạng mục E — Phân biệt Kết quả Đã Báo cáo (`Reported`) và Kết quả Tự Kiểm chứng Độc lập (`Independently Verified`)

Tuân thủ [`AGENTS.md` dòng 13, 20, 27](../../AGENTS.md#L13-L27), bảng dưới đây phân định rạch ròi giữa các kết quả được kế thừa từ báo cáo trước và các lệnh thực tế được chạy kiểm chứng trong phiên làm việc này:

| Hạng mục / Công cụ Kiểm tra | Phân loại Bằng chứng | Lệnh thực thi trong nhiệm vụ hiện tại | Exit Code | Kết quả thực tế & Giới hạn tái lập |
| :--- | :---: | :--- | :---: | :--- |
| **Thống kê tổng hợp 9 năm (`54,674,003` dòng, `ARR_DELAY >= 15` = `10,116,916`, năm 2024 có `335/366` ngày, thống kê null thời tiết)** | `REPORTED_IN_HISTORICAL_AUDITS` *(khớp với 9 tệp `schema_YYYY.json` và báo cáo `T-001..T-005`)* | Không chạy lại full-scan trên 9 tệp CSV thô (~15.2 GB) trong nhiệm vụ này | `N/A` | Số liệu được đối chiếu chéo từ 9 tệp `docs/05-evidence/inputs/schema_2016.json` đến `docs/05-evidence/inputs/schema_2024.json` và các báo cáo kiểm toán `T-001..T-005`. Không giả mạo đã chạy Spark hay quét lại toàn bộ CSV thô trong bước này. |
| **Bộ kiểm thử QA T-003 (`133/133 PASS` trên `FIX-01..14`)** | `REPORTED_IN_T003_EVIDENCE` | Không có script chạy độc lập trong `tools/qa/` (chỉ có tệp fixture [`T003_FIX14_accounting_fixture.csv`](T003_FIX14_accounting_fixture.csv) và `.json`) | `N/A` | Được ghi nhận tại [`PROJECT_STATE.md` dòng 21](../04-execution/PROJECT_STATE.md#L21) và [`T003_FINAL_CLOSEOUT_VERIFICATION.md`](T003_FINAL_CLOSEOUT_VERIFICATION.md); chưa chạy lại bằng runner tự động trong phiên này. |
| **Bộ kiểm thử QA T-004 ([`tools/qa/verify_t004_time_representation.py`](../../tools/qa/verify_t004_time_representation.py))** | **`INDEPENDENTLY_VERIFIED_IN_CURRENT_TASK`** | `python tools/qa/verify_t004_time_representation.py` | **`0`** | **`90 PASS, 0 FAIL`** (`OVERALL STATUS: PASS`). Kiểm tra sự tồn tại của các tệp T-004, tổng số dòng trong 9 tệp `schema_YYYY.json` (`54,674,003`), và 9 dòng fixture `TF-01..09`. |
| **Công cụ kiểm tra cây làm việc ([`tools/check_working_tree_consistency.py`](../../tools/check_working_tree_consistency.py))** | **`INDEPENDENTLY_VERIFIED_IN_CURRENT_TASK` (Đang có `2 FAIL` thật)** | `python tools/check_working_tree_consistency.py` | **`1`** | **`Working-Tree PASS assertions: 86; FAIL: 2`**.<br>- Toàn bộ 86 kiểm tra về cấu trúc thư mục, mã băm `SOURCE_MANIFEST.json`, `PACKAGE_MANIFEST.json`, các đường dẫn `docs/...` và liên kết Markdown tương đối đều **`PASS`**.<br>- **2 mục `FAIL` thực tế (không được phép tuyên bố là đã sửa):** Do bộ lọc tĩnh tại dòng 139 của [`tools/check_working_tree_consistency.py`](../../tools/check_working_tree_consistency.py#L139) chỉ cho phép các tệp `T001_..T004_`, nên **22 tệp bằng chứng tạo ra từ `T-005` đến `G2-SIGNOFF-HANDOFF-FIX`** bị đánh dấu là `unrecognized stray files`. |

---

## 4. CÁC ĐỘ KHÔNG CHẮC CHẮN CÒN LẠI (REMAINING UNCERTAINTY)

1. **Trạng thái các quyết định thiết kế (`FP-DEC-003..016`, `FP-DEC-PROP-015`):** Toàn bộ vẫn đang ở trạng thái **`PROPOSED` / `PENDING_REVIEW`**. Nhãn `FP-DEC-005A` và `FP-DEC-005B` chỉ là nhãn phân tách cấu phần đề xuất để thuận tiện cho việc ra quyết định của Project Lead, không phải là các ADR độc lập đã được phê duyệt. Mã `FP-DEC-017` chỉ là mã dự kiến dành riêng cho quyết định thời tiết sau khi có phê duyệt của Project Lead.
2. **Khoảng trống xác minh đơn vị đo 7 trường CORE (`OR-03` / `G2-EXC-001`):** Đơn vị đo của 7 trường số học cốt lõi vẫn giữ nhãn tạm thời `OFFICIAL_MINUTES_EMPIRICALLY_CONSISTENT_PROVISIONAL` cho đến khi Project Lead phê duyệt ngoại lệ `G2-EXC-001` và nhóm thực hiện hoàn tất kiểm thử đối chiếu mẫu BTS TranStats (`TS-018`) tại Gate G5.
3. **Khiếm khuyết lịch năm 2024 (`OR-05`):** Năm 2024 trong bộ CSV hiện tại chỉ có `335/366` ngày (vắng mặt toàn bộ 31 ngày dịch vụ Tháng 3/2024), giữ trạng thái `OPEN_QUALITY_DEFECT` và `source_coverage_status = 'PARTIAL'`.
4. **Danh tính nội dung dữ liệu thô (`OR-08`) và URL/License nguồn đóng gói:** 9 tệp CSV thô hiện chỉ khớp `size/mtime` với `schema_YYYY.json` (`METADATA_MATCH_ONLY` / `IDENTITY_UNVERIFIED`), và đường dẫn tải xuống/giấy phép của bản đóng gói bên thứ ba vẫn là `UPSTREAM_URL_LICENSE_UNKNOWN`.
5. **Trạng thái Exit Code `1` của `tools/check_working_tree_consistency.py`:** Sẽ tiếp tục báo `86 PASS, 2 FAIL` cho đến khi Project Lead phê duyệt cho phép cập nhật danh sách tệp hợp lệ trong script sau khi ký đóng Gate G2.

---

## 5. KẾT LUẬN SẴN SÀNG KÝ DUYỆT & CÁC QUYẾT ĐỊNH BẮT BUỘC CỦA CON NGƯỜI (SIGN-OFF READINESS & REQUIRED HUMAN APPROVALS)

### 5.1. Kết luận Đối chiếu Tài liệu
- **Trạng thái nghiệm thu nhiệm vụ `G2-SIGNOFF-HANDOFF-FIX`:** **`DOCUMENTATION_RECONCILED`**.
- **Trạng thái gói hồ sơ trình ký Gate G2:** **`READY_FOR_HUMAN_REVIEW` (`READY_WITH_EXPLICIT_CONDITIONS`)**.
- **Trạng thái Gate G2 hiện tại:** **`IN_PROGRESS / NOT_PASSED`**.
- **Trạng thái Nhiệm vụ `T-006` (Gate G3):** **`NOT_STARTED`**.

### 5.2. Danh mục Chính xác Các Quyết định Cần Project Lead / Human Reviewer Phê duyệt
Project Lead thực hiện xem xét và tích chọn trực tiếp trên dự thảo chưa ký [`G2_SIGNOFF_HUMAN_APPROVAL_RECORD_DRAFT.md`](G2_SIGNOFF_HUMAN_APPROVAL_RECORD_DRAFT.md) (kèm theo hiệu chỉnh tại [`G2_SIGNOFF_FINAL_PRECHECK_ADDENDUM.md`](G2_SIGNOFF_FINAL_PRECHECK_ADDENDUM.md) và bản đính chính chuẩn tắc này) đối với các hạng mục sau:

1. **Duy trì 2 quyết định phạm vi đã xác nhận ở G0:**
   - **`FP-DEC-001`** (`USER_CONFIRMED`): Phạm vi đồ án phân tích hiệu suất chuyến bay Hoa Kỳ 2016–2024 (mô tả).
   - **`FP-DEC-002`** (`USER_CONFIRMED_BY_SCOPE`): Sử dụng năm 2024 cho phân tích mô tả hồi cứu (kèm công bố khuyết Tháng 3/2024 theo `OR-05`).
2. **Xem xét phê duyệt nhóm quyết định kiểm soát, an toàn và hợp đồng trong [`DECISIONS.md`](../02-design/DECISIONS.md):**
   - **`FP-DEC-003`**: Loại trừ Machine Learning, ATL-only, Flight Chain `.pt` và Flight Network khỏi CORE (`PROPOSED_IMPLEMENTATION`).
   - **`FP-DEC-004`**: Dữ liệu thô bất biến (`raw immutable`) và đầu ra phân phiên bản theo `run_id` (`PROPOSED_CONTROL`).
   - **`FP-DEC-005`**: Định hướng công nghệ PySpark + Parquet cho xử lý chính (`PROPOSED` — trong đó Project Lead có thể chọn duyệt định hướng công nghệ theo nhãn đề xuất `005A` tại G2 và hoãn thông số phiên bản/tài nguyên/benchmark theo nhãn đề xuất `005B` sang `T-006` ở G3, `T-009` ở G4 và `TS-014` ở G5).
   - **`FP-DEC-006`**: Cấm tính KPI canceled/diverted từ 34 trường hiện có; giữ `KPI-11 = NOT_COMPUTABLE` (`PROPOSED_GUARD`).
   - **`FP-DEC-007`**: Cấm tính timeline qua đêm bằng date component của `CRS_ARR_TIME` hoặc tự cộng `+24h` (`PROPOSED_GUARD`, phân tách rõ 3 tầng: `VERIFIED` quan sát lưu trữ, `UNKNOWN` mã nguồn ETL upstream, và `PROPOSED_GUARD` quy tắc phòng vệ).
   - **`FP-DEC-008`**: Dùng ngưỡng `ARR_DELAY >= 15` cho KPI trễ đến trên mẫu số hữu hạn (`PROPOSED_KPI`).
   - **`FP-DEC-009` & `FP-DEC-013`**: Nhánh thời tiết (`RQ-06` / `KPI-10`) là `Should/conditional`, cấm suy diễn nhân quả, phán quyết `CONDITIONAL_NO_GO` không chặn CORE G2/G6 (`PROPOSED` / `PROPOSED_CONTROL`).
   - **`FP-DEC-010`**: Cấm dùng `FLIGHTS` làm trọng số (`KPI-12 = BLOCKED`); mẫu số chuẩn là `count_records` (`PROPOSED_GUARD`).
   - **`FP-DEC-011`**: Phân biệt `metric_valid_rate` với `source_coverage_status`; hạch toán 3 trạng thái dòng `accepted`/`quarantined`/`rejected` loại trừ lẫn nhau theo `DC-11/12` (`PROPOSED_CONTROL`).
   - **`FP-DEC-012` & Ngoại lệ `G2-EXC-001`**: Khóa **8 CORE KPIs (`KPI-01..KPI-08`)** (giữ `KPI-09 = OPTIONAL`, `KPI-10 = CONDITIONAL / WEATHER`, `KPI-11 = NOT_COMPUTABLE`, `KPI-12 = BLOCKED`) và quyết định việc cấp **Ngoại lệ `G2-EXC-001`** cho phép dùng nhãn đơn vị đo tạm thời `OFFICIAL_MINUTES_EMPIRICALLY_CONSISTENT_PROVISIONAL` cho **7 trường đo cốt lõi** qua G2, kèm điều kiện bắt buộc đối chiếu BTS TranStats (`TS-018`) tại Gate G5 và cấm xuất bản nhãn `'minutes'` như sự thật đã xác minh trước khi vượt qua `TS-018`.
   - **`FP-DEC-014`**: `source_signature` (`size/mtime`) chỉ cảnh báo drift (`METADATA_MATCH_ONLY`), không chứng minh danh tính nội dung thô (`IDENTITY_UNVERIFIED`) (`PROPOSED_CONTROL`).
3. **Xem xét phê duyệt 3 đề xuất kỹ thuật mới từ `T-003` và `T-005` (hiện đang ở trạng thái `PROPOSED` / chưa được duyệt):**
   - **`FP-DEC-015`**: Phương pháp tính phân vị xấp xỉ cho `KPI-06` bằng PySpark `percentile_approx` (GK-sketch, `accuracy = 10000`, $\epsilon_{\text{rank}} \le 0.01\%$, kiểm chuẩn thực nghiệm ở Gate G5 `TS-008`).
   - **`FP-DEC-016`**: Chính sách ngưỡng cỡ mẫu tối thiểu (`min-N`) cho bảng xếp hạng: **`carrier-year >= 1,000`**, **`airport-year >= 365`**, **`route-year >= 100`** (kèm giữ nguyên `source_coverage_status = 'PARTIAL'` theo `DC-12` cho các báo cáo năm 2024 thiếu Tháng 3 mà không ghi đè mã lý do lên con trỏ `provenance_reference`).
   - **`FP-DEC-PROP-015`** *(dự kiến cấp mã chính thức **`FP-DEC-017`** chỉ sau khi được phê duyệt)*: Ban hành phán quyết `CONDITIONAL_NO_GO` cho nhánh phân tích thời tiết tùy chọn (`RQ-06` / `KPI-10`).
4. **Phê duyệt chế độ quản trị rủi ro mở (`OR-01..OR-08`), ủy quyền cập nhật `tools/check_working_tree_consistency.py` sau ký duyệt, và phán quyết đóng Gate G2 / mở khóa `T-006`.**

---
*Báo cáo đính chính này được lưu trữ độc lập tại `docs/05-evidence/G2_SIGNOFF_PRECHECK_CONSISTENCY_ERRATA.md`. Gate G2 tiếp tục giữ trạng thái `IN_PROGRESS / NOT_PASSED` và `T-006` giữ trạng thái `NOT_STARTED`.*
