# T-002: BÁO CÁO TỔNG KẾT ĐÓNG VÀ CHUẨN BỊ NGHIỆM THU CUỐI CÙNG (FINAL CONSISTENCY & ACCEPTANCE PREPARATION)

- **Mã nhiệm vụ:** `T-002-CLOSEOUT` (Final Consistency & Acceptance Preparation)
- **Nhiệm vụ gốc:** `T-002` (Flight Grain & Denominator Audit)
- **Gate:** `G2` (Data Quality, Cohort & Metric Contracts)
- **Ngày thực hiện:** 2026-10-14
- **Vai trò:** Senior Data Engineer & Documentation Auditor
- **Trạng thái đề xuất:** **`AUDIT_COMPLETE / REVIEW_PENDING (Ready for Reviewer Sign-Off)`**
- **Văn bản quy định tuân thủ:** [`AGENTS.md`](../../AGENTS.md), [`DATA_CONTRACT.md`](../02-design/DATA_CONTRACT.md), [`DATA_DICTIONARY.md`](../02-design/DATA_DICTIONARY.md), [`KPI_SPEC.md`](../02-design/KPI_SPEC.md), [`BACKLOG.md`](../01-planning/BACKLOG.md), [`TEST_PLAN.md`](../03-quality/TEST_PLAN.md), [`PROJECT_STATE.md`](../04-execution/PROJECT_STATE.md).

---

## 1. Bảng Kết quả Xử lý Năm Yêu cầu Hiệu chỉnh (C01 — C05 Matrix)

| Mã | Nội dung yêu cầu | Hiện trạng trước Closeout | Kết quả xử lý & Ranh giới khoa học sau Closeout | Trạng thái xác minh |
|:---:|---|---|---|:---:|
| **C01** | **Ranh giới Bằng chứng Cấp hạt Chặng bay** | Gọi "Completed Flight Leg" là `VERIFIED` và xem mỗi dòng là một chuyến bay vật lý riêng biệt. | Phân định rạch ròi 3 tầng bằng chứng: (1) Cấp hạt bản ghi quan sát trong dữ liệu: **`VERIFIED`** (chặng bay thẳng kế hoạch có cặp ORIGIN-DEST và CRS_DEP_TIME); (2) Giả định chuyến bay đã hoàn tất: **`INFERRED`** (do không có missing ở 28 cột vận hành, nhưng thiếu pipeline ETL chứng minh); (3) Sự tương ứng 1-1 với sự kiện vật lý thực tế: **`UNKNOWN`** (do thiếu `TAIL_NUM` và sự hiện diện của cặp trùng YX 3624). | **`VERIFIED_BOUNDARY`** |
| **C02** | **Quản trị Trạng thái Dự án (Project State Governance)** | Tự gán nhãn T-002 là "DONE" hoặc tự chuyển G2 thành PASS khi chưa có Reviewer sign-off. | Cập nhật [`PROJECT_STATE.md`](../04-execution/PROJECT_STATE.md): T-002 mang trạng thái **`AUDIT_COMPLETE / REVIEW_PENDING`**; Gate G2 giữ nguyên **`IN_PROGRESS / NOT_PASSED`**. Tuyệt đối không tự ý nghiệm thu thay quyền của Reviewer. | **`GOVERNANCE_ALIGNED`** |
| **C03** | **Chính xác hóa Nhận định Codeshare** | Viết rằng "hoàn toàn không có trùng lặp trong cùng một hãng", mâu thuẫn với cặp trùng YX 3624. | Làm rõ: Trong dữ liệu có tồn tại **đúng 1 nhóm trùng candidate key thuộc cùng hãng khai thác `OP_CARRIER = YX`** (2018), nhưng là do hoãn giờ sâu sang hôm sau, không phải trùng lặp do codeshare. Việc codeshare có tạo bản ghi thừa dưới mã hãng khác hay không giữ nguyên phân loại **`NOT_DETERMINABLE_FROM_AVAILABLE_FIELDS`**. | **`VERIFIED_STATEMENT`** |
| **C04** | **Tính toán Xác suất Va chạm Băm (Hash Collision)** | Ước lượng xác suất va chạm 64-bit chung chung, có thể gây hiểu nhầm xác suất bằng 0. | Tính toán chi tiết theo 2 cách tiếp cận: (1) Tổng xác suất theo $N_y$ thực tế 9 năm: $\sum P_y \approx \mathbf{9.17 \times 10^{-6}}$ ($0.000917\%$); (2) Giới hạn trên bảo thủ dựa trên năm lớn nhất: $9 \times P_{\max} \approx \mathbf{1.25 \times 10^{-5}}$ ($0.001251\%$). Nêu rõ giả định phân bố đều của BLAKE2b và khẳng định xác suất va chạm **khác 0**, do đó kiểm chứng chuỗi thô độc lập ở Pass 2 là bắt buộc. | **`VERIFIED_ARITHMETIC`** |
| **C05** | **Phạm vi Kiểm thử & Khả năng Tái lập (Test Coverage Scope)** | Đề cập TS-009, TS-012, TS-020 như các test đã thực thi trên pipeline production. | Làm rõ phạm vi kiểm thử theo [`TEST_PLAN.md`](../03-quality/TEST_PLAN.md): Các bài kiểm thử `TS-009` (G2 design / G5 execution), `TS-012` (G5 execution) và `TS-020` (G4 synthetic / G6 full) hiện đang ở trạng thái **thiết kế quy tắc (*SPECIFIED / DESIGN_BASELINE*)**, chưa phải test code chạy production. Các công cụ Python hiện tại là công cụ kiểm toán độc lập (*audit scripts*) phục vụ Gate G2. | **`SPECIFIED_SCOPE_VERIFIED`** |

---

## 2. Vị trí và Nội dung Đã Chỉnh sửa (Audit Diff & Changes Traceability)

1. **[`docs/05-evidence/T002_FLIGHT_GRAIN_AUDIT.md`](T002_FLIGHT_GRAIN_AUDIT.md):**
   - *Mục 4 & 5:* Sửa phân loại cấp hạt: Cấp hạt bản ghi quan sát là `VERIFIED` (*Scheduled Flight Leg Record*); Giả định hoàn tất chuyến bay là `INFERRED`; Tính tương ứng sự kiện vật lý là `UNKNOWN`.
   - *Mục 2.2:* Sửa kết luận `KPI-12` thành đề xuất Reviewer chính thức phê duyệt việc khóa.
2. **[`docs/05-evidence/T002_DUPLICATE_ANALYSIS.md`](T002_DUPLICATE_ANALYSIS.md):**
   - *Mục 2.2:* Chuẩn hóa bảng 4 công thức tỷ lệ duy nhất (Key-to-Row: $99.99999817\%$, Strictly Unique Record: $99.99999634\%$, Duplicate Record: $0.00000366\%$, Duplicate Key: $0.00000183\%$).
   - *Mục 3.1:* Sửa chính xác các trường thời lượng trích xuất từ CSV thô: dòng 6384132 (`ACTUAL_ELAPSED_TIME = 182.0`, `AIR_TIME = 84.0`), dòng 6384133 (`ACTUAL_ELAPSED_TIME = 102.0`, `AIR_TIME = 83.0`).
   - *Mục 4:* Làm rõ nhóm trùng YX 3624 thuộc cùng hãng khai thác; chuyển kết luận codeshare thành `NOT_DETERMINABLE_FROM_AVAILABLE_FIELDS`.
   - *Mục 5:* Làm rõ TS-009, TS-012, TS-020 ở trạng thái `SPECIFIED / DESIGN_BASELINE`.
3. **[`docs/05-evidence/T002_DENOMINATOR_RECOMMENDATION.md`](T002_DENOMINATOR_RECOMMENDATION.md):**
   - *Mục 2.1:* Bổ sung phân định rõ giữa số dòng thô đã kiểm toán ($54,674,003$ dòng) và số dòng `accepted_row_count` thực tế (kết quả runtime sau ingestion tại G4/G5).
   - *Mục 5:* Cập nhật đề xuất Reviewer khóa `KPI-12`.
4. **[`docs/05-evidence/T002_R1_INDEPENDENT_REVIEW.md`](T002_R1_INDEPENDENT_REVIEW.md):**
   - *Mục 3.2:* Cập nhật bảng tính toán xác suất va chạm băm $\sum P_y \approx 9.17 \times 10^{-6}$ và giới hạn trên bảo thủ $1.25 \times 10^{-5}$, nêu rõ các giả định toán học.
5. **[`docs/04-execution/PROJECT_STATE.md`](../04-execution/PROJECT_STATE.md):**
   - Cập nhật dòng T-002: **`AUDIT_COMPLETE / REVIEW_PENDING`**, trích dẫn đầy đủ báo cáo tổng kết cuối cùng, Gate G2 giữ nguyên `IN_PROGRESS / NOT_PASSED`.

---

## 3. Số liệu Kiểm chứng Thống nhất (Consolidated Audit Metrics)

$$\begin{aligned}
\text{Tổng số bản ghi thô (raw\_row\_count):} \quad N &= 54,674,003 \\
\text{Tổng số khóa ứng viên duy nhất (distinct\_candidate\_keys):} \quad K &= 54,674,002 \\
\text{Số khóa bị trùng lặp (duplicate\_keys\_count):} \quad D_{\text{keys}} &= 1 \quad (\text{YX 3624, năm 2018}) \\
\text{Số bản ghi thuộc nhóm khóa trùng (duplicate\_rows\_count):} \quad D_{\text{rows}} &= 2 \\
\text{Số bản ghi có khóa duy nhất tuyệt đối (strictly\_unique\_rows):} \quad U_{\text{rows}} &= 54,674,001 \\
\text{Số giá trị khuyết thiếu trên 6 thành phần khóa (component\_nulls):} \quad &= 0 \\
\text{Tỷ lệ bản ghi có trường FLIGHTS = 1.0:} \quad &= 100.0\% \quad (54,674,003 / 54,674,003)
\end{aligned}$$

---

## 4. Lệnh Thực thi, Exit Code và Kết quả Kiểm thử (Verification Commands)

### 4.1. Kiểm tra tính toàn vẹn không gian làm việc
- **Lệnh thực thi:**
  ```powershell
  python tools/check_working_tree_consistency.py
  ```
- **Exit Code:** `0`
- **Stdout:**
  ```text
  Working-Tree PASS assertions: 88; FAIL: 0
  ALL WORKING-TREE CHECKS PASSED.
  ```
- **Stderr:** *(Trống)*

---

## 5. Danh mục Rủi ro Mở chuyển giao (Open Risks Handover)

| Mã Rủi ro | Nội dung rủi ro | Nhiệm vụ chịu trách nhiệm | Yêu cầu kiểm soát |
|:---:|---|:---:|---|
| **OR-01** | Chưa rõ ý nghĩa cột `FLIGHTS` (100% bằng 1.0, không phải trọng số). | **T-003** (G2) | Khóa `KPI-12`. Dùng `count_records` làm mẫu số thuần tập. |
| **OR-02** | Nguy cơ mất dữ liệu trễ cực đoan nếu naive deduplication. | **T-008** (G4) | Cấm `drop_duplicates` tự động. Giữ nguyên 100% bản ghi thô. Đưa ca YX 3624 vào test fixture TS-009. |
| **OR-03** | Đơn vị 7 trường độ trễ/thời lượng chưa được văn bản gốc xác nhận phút. | **T-003** (G2) | Duy trì nhãn `UNIT_UNVERIFIED` trong metadata; TS-018 phải kiểm chứng trước G2 PASS. |
| **OR-04** | Thiếu cột `CANCELLED` và `DIVERTED`. | **T-003** (G2) | `KPI-11 = NOT_COMPUTABLE`, loại khỏi 8 CORE KPIs. |
| **OR-05** | Tính liên tục 366 ngày của 2024 chưa đếm distinct dates. | **T-004** / **TS-004** | Kiểm toán phân bố ngày chi tiết tại T-004 trước ingestion full. |
| **OR-06** | Rollover mốc giờ thực tế (`ARR_TIME`, `DEP_TIME`) và bản chất cặp trùng YX 3624. | **T-004** (G2) | Cấm tạo trường thời gian đến phái sinh; kiểm toán chi tiết định dạng timestamp vận hành tại T-004. |
| **OR-07** | Dữ liệu thời tiết thiếu trạm đo, mốc thời gian và đơn vị. | **T-005** (G2) | Giữ `CONDITIONAL_PENDING` cho RQ-06 / KPI-10. |
| **OR-08** | Chưa có SHA-256 tham chiếu từ nguồn phát hành gốc. | **T-007** / **TS-019** (G4) | Lập baseline mã băm nội bộ khi khởi tạo ingestion, kiểm tra drift fail-closed. |

---

## 6. Đối chiếu Tiêu chí Nghiệm thu BACKLOG v1.1

- **Tiêu chí nghiệm thu của T-002:**
  > *"Có denominator cohort/record strategy, test grain không dedup tùy tiện"*
- **Kết luận đối chiếu:** **HOÀN THÀNH TOÀN DIỆN (100% ALIGNED)**.
  - Khung hạch toán bản ghi (`raw`, `accepted`, `quarantined`, `rejected`) và mẫu số (`count_records`, `count_metric_valid`, `metric_valid_rate`, xử lý mẫu số 0) đã được chuẩn hóa theo DC-11/12.
  - Cấp hạt bản ghi quan sát chặng bay kế hoạch đã được kiểm toán; chính sách nghiêm cấm deduplicate tùy tiện đã được ban hành và bảo đảm an toàn dữ liệu.

---

## 7. Kết luận Nghiệm thu và Điều kiện Bắt đầu T-003

### 7.1. Kết luận Nghiệm thu T-002
- **Xếp loại kỹ thuật:** **`AUDIT_COMPLETE / READY_FOR_SIGNOFF`**.
- Toàn bộ hồ sơ kiểm toán, đối chiếu trực tiếp dữ liệu thô, hòa giải bằng chứng khoa học và chuẩn hóa số học đã hoàn tất.
- Hồ sơ sẵn sàng để **Reviewer ký duyệt chính thức**.

### 7.2. Các Điều kiện Tiên quyết để Bắt đầu T-003
Nhiệm vụ **T-003** (*Kiểm chứng đơn vị/sign/domain cho 7 trường đo lường và khóa 8 CORE KPIs*) chỉ được bắt đầu khi:
1. Reviewer chính thức phê duyệt biên bản nghiệm thu T-002.
2. Reviewer chấp thuận các quyết định quản trị:
   - Sử dụng `count_records = accepted_row_count(C)` làm mẫu số thuần tập.
   - Ban hành chính sách Zero Arbitrary Deduplication.
   - Khóa chỉ số `KPI-12` (`BLOCKED / REDUNDANT`).
3. Được cấp phép chính thức để khởi tạo task context mới cho T-003.

---

### Cam kết Tuân thủ An toàn
- **TÔI ĐÃ DỪNG LẠI SAU T-002-CLOSEOUT**, không tự ý triển khai mã nguồn hoặc tài liệu của T-003.
- **Gate G2 VẪN GIỮ NGUYÊN TRẠNG THÁI `IN_PROGRESS / NOT_PASSED`**.
