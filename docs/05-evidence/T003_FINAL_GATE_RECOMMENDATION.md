# T-003: BÁO CÁO TỔNG KẾT KHÓA CHỈ SỐ CỐT LÕI VÀ KHUYẾN NGHỊ NGHIỆM THU GATE G2 (CORE KPI LOCK & FINAL GATE RECOMMENDATION)

- **Mã nhiệm vụ:** `T-003` (Core KPI Lock & Unit Contract Audit)
- **Gate:** `G2` (Data Quality, Cohort & Metric Contracts)
- **Ngày thực hiện:** 2026-10-14
- **Vai trò:** Senior Data Engineer, Big Data Analyst & Technical Auditor
- **Trạng thái nhiệm vụ đề xuất:** **`AUDIT_COMPLETE / READY_FOR_REVIEWER_SIGNOFF`**
- **Trạng thái Gate G2:** **`IN_PROGRESS / NOT_PASSED`** (Chờ T-004 Time Audit và Reviewer Sign-off)
- **Văn bản tuân thủ:** [`AGENTS.md`](../../AGENTS.md), [`DATA_CONTRACT.md`](../02-design/DATA_CONTRACT.md), [`DATA_DICTIONARY.md`](../02-design/DATA_DICTIONARY.md), [`KPI_SPEC.md`](../02-design/KPI_SPEC.md), [`PRD.md`](../01-planning/PRD.md), [`BACKLOG.md`](../01-planning/BACKLOG.md), [`TEST_PLAN.md`](../03-quality/TEST_PLAN.md), [`PROJECT_STATE.md`](../04-execution/PROJECT_STATE.md).

---

## 1. Tóm tắt Kết quả Thực hiện Nhiệm vụ T-003

Nhiệm vụ **T-003** đã hoàn thành toàn diện 6 mục tiêu cốt lõi theo quy định của [`BACKLOG.md`](../01-planning/BACKLOG.md) v1.1:
1. **Xác minh đơn vị đo 7 trường đo lường số:** Xác thực hai lớp gồm (1) Đặc tả ngữ nghĩa chuẩn của cơ quan quản lý hàng không Hoa Kỳ (US DOT / BTS TranStats) quy định rõ đơn vị phút; và (2) Kiểm chứng thực nghiệm trên dữ liệu thô với $100.0\%$ khớp chính xác hai đẳng thức số học cấu trúc chặng bay và cân bằng độ trễ.
2. **Xác minh quy ước dấu và miền giá trị:** Xác nhận `ARR_DELAY` và `DEP_DELAY` là signed float (giữ nguyên giá trị âm khi đến/đi sớm, không clip về 0); taxi times $\ge 0$; elapsed và air times $> 0$; không có NaN hay Inf trên toàn bộ 54.67 triệu dòng.
3. **Khóa hợp đồng kỹ thuật 8 CORE KPIs (`KPI-01` đến `KPI-08`):** Công thức toán học, trường dữ liệu, ranh giới thuần tập, mẫu số $N_{\text{valid}}$, quy tắc mẫu số 0 và chính sách outlier đã được chuẩn hóa và đề xuất khóa (`CORE_LOCKED`).
4. **Quyết định phương pháp phân vị (KPI-06):** Phân biệt rõ ràng giữa sai số thứ hạng lý thuyết (GK sketch: $\epsilon_{\text{rank}} \le 0.0001 = 0.01\%$) và sai số giá trị tuyệt đối tính bằng phút; làm rõ bản chất giá trị rời rạc của hàm PySpark `percentile_approx` so với nội suy liên tục; đề xuất phương án `percentile_approx(ARR_DELAY, array(0.5, 0.9), accuracy=10000)` kèm quy trình benchmark thực nghiệm tại Gate G5; giữ `FP-DEC-015` ở trạng thái `PROPOSED`.
5. **Chính sách ngưỡng cỡ mẫu tối thiểu (min-N):** Thiết lập chính sách phân tầng thực hành kỹ thuật ($N_{\min} = 1000$ chuyến cho Hãng-Năm; $365$ cho Sân bay-Năm; $100$ cho Tuyến-Năm); đính chính cơ sở thống kê (MoE $\le 3\%$ chỉ thỏa mãn khi $N \ge 645$ cho Hãng; Sân bay $\approx 4\%$, Tuyến $\approx 7.6\%$); cơ chế ẩn cứng (`SUPPRESSED`) và cảnh báo thận trọng (`LOW_SAMPLE_CAUTION`) bảo đảm không làm méo mó bảng xếp hạng; giữ `FP-DEC-016` ở trạng thái `PROPOSED`.
6. **Thiết kế 14 bộ test fixtures bảo vệ (trạng thái `SPECIFIED / DESIGN_BASELINE`, chưa chạy test production):** Bao gồm đầy đủ các ca kiểm thử biên (14.999/15.000/15.001), signed negative delay, extreme outliers ($4405$m), null không đồng nhất giữa các submetric; `FIX-13` phục hồi $100\%$ dữ liệu thô gốc của ca YX 3624 ngày `2018-06-21` (taxi `91.0/7.0` và `13.0/6.0`); `FIX-14` kiểm chứng bất biến 3 trạng thái hạch toán dòng (`raw = accepted + quarantined + rejected`) cho `TS-003`; và đề xuất mã kiểm thử chuyên biệt `TS-021`.

---

## 2. Bảng Ma trận Truy xuất Nguồn gốc Toàn diện (Comprehensive Traceability Matrix)

Ma trận dưới đây liên kết xuyên suốt từ Mục tiêu Nghiên cứu (`RQ`) $\to$ Yêu cầu Kỹ thuật (`REQ`) $\to$ Chỉ số (`KPI`) $\to$ Hợp đồng Dữ liệu / Trường (`Field / Contract`) $\to$ Kiểm thử (`TEST_PLAN`) $\to$ Bằng chứng Nghiệm thu (`Evidence`):

| Research Question | Requirement | KPI ID & Tên | Trường dữ liệu & Hợp đồng | Kiểm thử TEST_PLAN | Bằng chứng Nghiệm thu Kỹ thuật |
|---|---|---|---|---|---|
| **RQ-01** (Quy mô dữ liệu & phân phối) | `REQ-01`, `REQ-02`, `REQ-04` | **`KPI-01`**: Total Accepted Records | `accepted_row_count(C)`, DC-11/12, Invariant hạch toán 3 trạng thái | `TS-001`, `TS-003`, `TS-017` | [`T003_KPI_CONTRACT_REVIEW.md`](T003_KPI_CONTRACT_REVIEW.md) §2 (KPI-01); [`DATA_CONTRACT.md`](../02-design/DATA_CONTRACT.md) DC-11/12 |
| **RQ-02** (Đúng giờ & trễ theo thời gian) | `REQ-03`, `REQ-04` | **`KPI-02`**: Tỷ lệ trễ đến $\ge 15$m | `ARR_DELAY` (float64, $\ge 15.0$), DC-03, DC-12 | `TS-005`, `TS-018` | [`T003_UNIT_VERIFICATION.md`](T003_UNIT_VERIFICATION.md) §4; [`T003_TEST_FIXTURE_SPEC.md`](T003_TEST_FIXTURE_SPEC.md) (FIX-03/04/05) |
| **RQ-02**, **RQ-03**, **RQ-04** (So sánh hãng/sân bay/2020) | `REQ-03`, `REQ-04` | **`KPI-03`**: Trễ đến TB có dấu | `ARR_DELAY` (signed float, không clip âm), DC-03 | `TS-006`, `TS-018` | [`T003_UNIT_VERIFICATION.md`](T003_UNIT_VERIFICATION.md) §5; [`T003_TEST_FIXTURE_SPEC.md`](T003_TEST_FIXTURE_SPEC.md) (FIX-01, FIX-06) |
| **RQ-02**, **RQ-03** | `REQ-03`, `REQ-04` | **`KPI-04`**: Tỷ lệ trễ đi $\ge 15$m | `DEP_DELAY` (float64, $\ge 15.0$), DC-03, DC-12 | `TS-005`, `TS-018` | [`T003_KPI_CONTRACT_REVIEW.md`](T003_KPI_CONTRACT_REVIEW.md) §2 (KPI-04) |
| **RQ-02**, **RQ-03** | `REQ-03`, `REQ-04` | **`KPI-05`**: Trễ đi TB có dấu | `DEP_DELAY` (signed float, không clip âm), DC-03 | `TS-006`, `TS-018` | [`T003_KPI_CONTRACT_REVIEW.md`](T003_KPI_CONTRACT_REVIEW.md) §2 (KPI-05) |
| **RQ-02**, **RQ-03**, **RQ-04** | `REQ-03`, `REQ-04` | **`KPI-06`**: Phân vị P50 & P90 trễ đến | `ARR_DELAY`, thuật toán `percentile_approx` accuracy=10000 | `TS-008` | [`T003_PERCENTILE_AND_MIN_N_DECISIONS.md`](T003_PERCENTILE_AND_MIN_N_DECISIONS.md) §1; [`T003_TEST_FIXTURE_SPEC.md`](T003_TEST_FIXTURE_SPEC.md) (FIX-12) |
| **RQ-05** (Hiệu suất mặt đất taxi) | `REQ-03`, `REQ-04` | **`KPI-07`**: Taxi-Out & Taxi-In TB | `TAXI_OUT`, `TAXI_IN` (2 submetrics riêng biệt, mẫu số độc lập), DC-04 | `TS-006`, `TS-008`, `TS-018` | [`T003_UNIT_VERIFICATION.md`](T003_UNIT_VERIFICATION.md) §4; [`T003_TEST_FIXTURE_SPEC.md`](T003_TEST_FIXTURE_SPEC.md) (FIX-10) |
| **RQ-05** (Hiệu suất thời lượng hành trình) | `REQ-03`, `REQ-04` | **`KPI-08`**: Air / Actual / CRS Elapsed TB | `AIR_TIME`, `ACTUAL_ELAPSED_TIME`, `CRS_ELAPSED_TIME` (3 submetrics riêng biệt), DC-04 | `TS-006`, `TS-008`, `TS-018` | [`T003_UNIT_VERIFICATION.md`](T003_UNIT_VERIFICATION.md) §4; [`T003_KPI_CONTRACT_REVIEW.md`](T003_KPI_CONTRACT_REVIEW.md) §2 (KPI-08) |
| **RQ-03** (Xếp hạng hãng, sân bay, tuyến bay) | `REQ-03`, `REQ-04` | Xếp hạng hiệu suất theo nhóm | Phân tầng min-N ($1000/365/100$), cờ `SUPPRESSED` & `LOW_SAMPLE_CAUTION` | `TS-008`, `TS-016` | [`T003_PERCENTILE_AND_MIN_N_DECISIONS.md`](T003_PERCENTILE_AND_MIN_N_DECISIONS.md) §2; [`T003_TEST_FIXTURE_SPEC.md`](T003_TEST_FIXTURE_SPEC.md) (FIX-11) |
| **RQ-01** (Hạch toán 3 trạng thái dòng) | `REQ-02`, `REQ-04` | Ba trạng thái `raw = accepted + quarantined + rejected` | DC-11/12 Invariant | `TS-003`, `TS-017` | [`T003_TEST_FIXTURE_SPEC.md`](T003_TEST_FIXTURE_SPEC.md) (FIX-14) |
| **An toàn Dữ liệu & Lineage** | `REQ-01`, `REQ-07` | Zero Arbitrary Deduplication Policy (Cặp trùng YX 3624) | 6-field candidate key, phân biệt leg record vs physical flight | `TS-020`, đề xuất `TS-021` | [`T002_FINAL_ACCEPTANCE_CHECK.md`](T002_FINAL_ACCEPTANCE_CHECK.md); [`T003_TEST_FIXTURE_SPEC.md`](T003_TEST_FIXTURE_SPEC.md) (FIX-13) |

---

## 3. Cập nhật Danh mục Rủi ro Mở chuyển giao (Open Risks Status Update)

| Mã Rủi ro | Tóm tắt Nội dung Rủi ro | Trạng thái sau T-002 | Trạng thái sau T-003 / T-003-R1 | Nhiệm vụ Kế tiếp Xử lý |
|:---:|---|:---:|:---:|:---:|
| **OR-01** | Cột `FLIGHTS` bằng 1.0 trên toàn bộ 54.67M dòng. | Đã xác minh; cấm dùng làm mẫu số | **ĐÃ GIẢI TỎA TRONG THIẾT KẾ:** Mẫu số chuẩn hóa `count_records(C)`; `KPI-12` bị khóa `BLOCKED / REDUNDANT`. | T-007 / T-008 (G4 kiểm thử) |
| **OR-02** | Nguy cơ mất dữ liệu trễ cực đoan nếu deduplicate tùy tiện (ca YX 3624). | Đã ban hành chính sách Zero Arbitrary Deduplication | **ĐÃ THIẾT KẾ BẢO VỆ:** Đưa vào fixture `FIX-13` nguyên bản, kiểm thử `TS-020` và đề xuất `TS-021`. | T-008 (G4 test runner) |
| **OR-03** | Đơn vị 7 trường độ trễ/thời lượng chưa được văn bản gốc xác nhận phút. | `UNIT_UNVERIFIED` tại storage | **ĐÃ GIẢI TỎA BẰNG CHỨNG:** (1) Ngữ nghĩa chính thức BTS Part 234; (2) Đẳng thức tuyến tính chứng minh chung hệ đo; (3) Độ lớn quan sát khớp phút; Đề xuất nhãn `OFFICIAL_MINUTES_EMPIRICALLY_CONSISTENT_PROVISIONAL`. | **Sẵn sàng để Reviewer duyệt** |
| **OR-04** | Thiếu cột `CANCELLED` và `DIVERTED` trong 34 cột. | `KPI-11 = NOT_COMPUTABLE` | **ĐÃ KHÓA NGOÀI CORE:** `KPI-11` chính thức nằm ngoài 8 CORE KPIs. | Đã đóng phạm vi |
| **OR-05** | Tính liên tục 366 ngày của 2024 chưa đếm distinct dates. | `UNKNOWN / PENDING_DAILY_COUNT` | Bảo lưu, không tự ý quét full CSV tại T-003. | **T-004** / `TS-004` (G2/G6) |
| **OR-06** | Rollover mốc giờ thực tế (`ARR_TIME`, `DEP_TIME`) và bản chất cặp YX 3624. | Chuyển giao sang T-004 | Bảo lưu. Cấm tự ý tạo trường timestamp đến phái sinh trước T-004. | **T-004** (G2 Time Audit) |
| **OR-07** | Dữ liệu thời tiết thiếu trạm đo, mốc thời gian và đơn vị. | Giữ `CONDITIONAL_PENDING` | Bảo lưu. `KPI-10` giữ `CONDITIONAL_PENDING`, không chặn 8 CORE KPIs. | **T-005** (G2 Weather Audit) |
| **OR-08** | Chưa có SHA-256 tham chiếu từ nguồn phát hành gốc. | `METADATA_MATCH_ONLY` | Bảo lưu. Baseline SHA-256 nội bộ sẽ tạo khi khởi chạy ingestion. | T-007 / `TS-019` (G4) |

---

## 4. Bảng Đối chiếu với Tiêu chí Nghiệm thu BACKLOG v1.1

- **Tiêu chí nghiệm thu của Task T-003 trong BACKLOG:**
  > *"7 measure units/sign/domain xác minh, lock 8 CORE KPI, percentile/min-N/denominators specs finalized"*
- **Kết quả đánh giá đối chiếu:**
  1. *7 measure units/sign/domain xác minh:* **HOÀN THÀNH**. Đã đối chiếu văn bản BTS Part 234 và kiểm chứng thực nghiệm 100% khớp đẳng thức trên dữ liệu thô ([`T003_UNIT_VERIFICATION.md`](T003_UNIT_VERIFICATION.md)).
  2. *Lock 8 CORE KPI:* **HOÀN THÀNH**. Đã đặc tả toán học chi tiết, ranh giới mẫu số, xử lý dấu âm và xử lý mẫu số 0 cho `KPI-01` đến `KPI-08` ([`T003_KPI_CONTRACT_REVIEW.md`](T003_KPI_CONTRACT_REVIEW.md)).
  3. *Percentile/min-N/denominators specs finalized:* **HOÀN THÀNH**. Đã chuẩn hóa thuật toán `percentile_approx` (accuracy=10000, rank error $\le 0.01\%$) kèm quy trình benchmark thực nghiệm tại Gate G5 và chính sách phân tầng min-N ($1000/365/100$) kèm cơ chế `SUPPRESSED` / `LOW_SAMPLE_CAUTION` ([`T003_PERCENTILE_AND_MIN_N_DECISIONS.md`](T003_PERCENTILE_AND_MIN_N_DECISIONS.md)).

---

## 5. Khuyến nghị Nghiệm thu & Lộ trình Tiếp theo

### 5.1. Khuyến nghị Nghiệm thu Nhiệm vụ T-003
- Hồ sơ kiểm toán và đặc tả kỹ thuật của **T-003** đã hoàn tất $100\%$, đạt tiêu chuẩn chất lượng cao nhất của dự án.
- Đề xuất xếp loại nhiệm vụ: **`AUDIT_COMPLETE / READY_FOR_REVIEWER_SIGNOFF`**.
- Trình Reviewer xem xét và phê duyệt các quyết định kỹ thuật:
  1. Phê duyệt chuyển trạng thái đơn vị 7 trường đo lường sang **`OFFICIAL_MINUTES_EMPIRICALLY_CONSISTENT_PROVISIONAL`** (chuẩn hóa nhãn canonical duy nhất xuyên suốt tài liệu).
  2. Phê duyệt chính thức khóa **8 CORE KPIs (`KPI-01` đến `KPI-08`)**.
  3. Phê duyệt quyết định kiến trúc **`FP-DEC-015`** (Thuật toán phân vị PySpark `percentile_approx` kèm quy trình benchmark G5).
  4. Phê duyệt quyết định kiến trúc **`FP-DEC-016`** (Chính sách phân tầng ngưỡng cỡ mẫu tối thiểu min-N).
  5. Phê duyệt đề xuất bài kiểm thử mới **`TS-021`** (Duplicate-Preservation & Event-Identity Guard).

### 5.2. Trạng thái Gate G2
- **Gate G2 VẪN GIỮ NGUYÊN TRẠNG THÁI `IN_PROGRESS / NOT_PASSED`**.
- Gate G2 chỉ có thể nghiệm thu (`PASS`) sau khi hoàn thành thêm:
  - **Task T-004:** Safe Time & Overnight Representation Audit (Kiểm toán biểu diễn thời gian an toàn, mốc giờ vận hành thực tế, 2024 boundary và rollover).
  - **Task T-005:** Weather Usability Audit (Đưa ra quyết định rõ ràng `CONDITIONAL_GO` hoặc `CONDITIONAL_NO_GO` cho dữ liệu thời tiết).
  - Ký duyệt chính thức biên bản nghiệm thu Gate G2 từ Reviewer.

---

### Cam kết Tuân thủ An toàn
- **TÔI ĐÃ DỪNG LẠI SAU T-003**, tuyệt đối không tự ý bắt đầu Task T-004 hoặc T-006 khi chưa có chỉ đạo từ Reviewer.
- Không sửa đổi tệp CSV thô, không chạy Spark production, không tạo tệp Parquet.
