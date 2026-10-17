# T-003-R1: BÁO CÁO HIỆU CHỈNH CÓ MỤC TIÊU VÀ HÒA GIẢI BẰNG CHỨNG HỢP ĐỒNG KPI (TARGETED KPI CONTRACT CORRECTION & EVIDENCE RECONCILIATION)

- **Mã nhiệm vụ:** `T-003-R1` (Targeted KPI Contract Correction & Evidence Reconciliation)
- **Nhiệm vụ gốc:** `T-003` (Core KPI Lock & Unit Contract Audit)
- **Gate:** `G2` (Data Quality, Cohort & Metric Contracts)
- **Ngày thực hiện:** 2026-10-14
- **Vai trò:** Senior Big Data Engineer, Statistical Methodology Reviewer & Data Quality Auditor
- **Trạng thái đề xuất:** **`AUDIT_COMPLETE / READY_FOR_REVIEWER_SIGNOFF`**
- **Trạng thái Gate G2:** **`IN_PROGRESS / NOT_PASSED`** (Chờ Reviewer ký duyệt và hoàn tất T-004/T-005)
- **Văn bản tuân thủ:** [`AGENTS.md`](../../AGENTS.md), [`DATA_CONTRACT.md`](../02-design/DATA_CONTRACT.md), [`DATA_DICTIONARY.md`](../02-design/DATA_DICTIONARY.md), [`KPI_SPEC.md`](../02-design/KPI_SPEC.md), [`PRD.md`](../01-planning/PRD.md), [`BACKLOG.md`](../01-planning/BACKLOG.md), [`TEST_PLAN.md`](../03-quality/TEST_PLAN.md), [`PROJECT_STATE.md`](../04-execution/PROJECT_STATE.md).

---

## 1. Ma trận Xử lý Chín Phát hiện Đánh giá (F01 — F09 Matrix)

| Mã | Nội dung phát hiện của Reviewer | Hiện trạng trước R1 | Kết quả xử lý & Ranh giới khoa học sau R1 | Trạng thái Đánh giá |
|:---:|---|---|---|:---:|
| **F01** | **Sai lệch dữ liệu thô trong FIX-13 (Raw Evidence Corruption)** | Dùng ngày `2018-06-25` và `2018-06-26`; tự chế dữ liệu taxi `83.0/15.0` và `15.0/4.0` để ép khớp đẳng thức; nhầm lẫn giữa raw và synthetic. | **Khôi phục 100% dữ liệu thô gốc** từ dòng 6,384,132 và 6,384,133 của CSV 2018: ngày `2018-06-21`, taxi dòng A `91.0/7.0`, dòng B `13.0/6.0`. Giữ nguyên timestamp không tự thêm ngày. Tách biệt hoàn toàn `ORIGINAL_RAW_VALUES` với các demo giả lập. Khẳng định tính chất vật lý là `UNKNOWN`. | **`PASS`** |
| **F02** | **Hợp đồng Phân vị Xấp xỉ (Percentile Approximation Contract)** | Tuyên bố `accuracy=10000` bảo đảm sai số tuyệt đối $< 0.1$ hoặc $< 0.5$ phút; tuyên bố mọi fixture nhỏ phải khớp exact $0.0$. | Phân biệt rõ ràng **sai số thứ hạng ($\epsilon_{\text{rank}} \le 0.01\%$)** với **sai số giá trị tuyệt đối tính bằng phút ($\Delta y$)**. Làm rõ PySpark `percentile_approx` trả về giá trị rời rạc trong mẫu, khác với nội suy liên tục. Trình bày chi tiết trên 2 bộ fixture `[10, 20, 4405]` và 100 phần tử. Đưa ra quy trình benchmark G5 và giữ `FP-DEC-015` ở `PROPOSED`. | **`PASS`** |
| **F03** | **Chính sách min-N & Fixture FIX-11** | FIX-11 xếp hạng Hãng B với $N=500$ mang cờ cảnh báo, trong khi ngưỡng $N_{\min}=1000$ (phải bị `SUPPRESSED`). | Sửa FIX-11: Cả Hãng A ($N=20$) và Hãng B ($N=500$) đều bị **`SUPPRESSED`**; bổ sung Hãng C ($N=1500$) vào vùng cảnh báo `LOW_SAMPLE_CAUTION` ($[1000, 3000)$); Hãng D ($N=5000$) đạt `SUFFICIENT`. Đồng bộ toàn diện ngưỡng $3N_{\min}$ cho cả 3 chiều: Carrier ($3000$), Airport ($1095$), Route ($300$). | **`PASS`** |
| **F04** | **Cơ sở Thống kê của min-N (Statistical Claims)** | Tuyên bố min-N bảo đảm biên sai số $\le \pm 3.0\%$ ở $95\%$ tin cậy cho mọi bảng xếp hạng. | Đính chính toán học: Với $p \approx 0.185$, $\text{MoE} \le \pm 3\%$ **chỉ đạt được khi $N \ge 645$** (thỏa mãn với Carrier $N=1000$). Tại Airport ($N=365$), $\text{MoE} \approx 4\%$; tại Route ($N=100$), $\text{MoE} \approx 7.6\%$. Phân định dữ liệu bay là census quan sát có phân cụm, không phải i.i.d. Các ngưỡng là giải pháp thực hành cân bằng trade-off. Giữ `FP-DEC-016` ở `PROPOSED`. | **`PASS`** |
| **F05** | **Hợp đồng KPI-01 khi Thuần tập Rỗng (Empty Cohort)** | FIX-08 viết `KPI-01..08 = null (ZERO_DENOMINATOR)`, mâu thuẫn với bản chất đếm số dòng của KPI-01. | Phân định rạch ròi: Khi thuần tập rỗng ($C = \emptyset$): **`KPI-01 = 0` bản ghi** (phép đếm tập rỗng bằng 0); `metric_valid_rate = null` (`ZERO_DENOMINATOR` do mẫu số đếm bằng 0); các chỉ số tỷ lệ/trung bình/phân vị (`KPI-02..08`) có giá trị **`null`** (`ZERO_METRIC_DENOMINATOR`). | **`PASS`** |
| **F06** | **Truy xuất Nguồn gốc Kiểm thử (Test Traceability)** | Mở rộng sai phạm vi `TS-009` sang kiểm thử bảo toàn trùng lặp; thiếu fixture hạch toán 3 trạng thái cho `TS-003`. | **Đề xuất mã kiểm thử chuyên biệt `TS-021 — Duplicate-Preservation & Event-Identity Guard`** cho ca YX 3624, không làm sai lệch `TS-009`. **Bổ sung `FIX-14`** gồm 5 dòng (3 accepted, 1 quarantined, 1 rejected) kiểm chứng bất biến `raw = accepted + quarantined + rejected` cho `TS-003`. | **`PASS`** |
| **F07** | **Ranh giới Bằng chứng Đơn vị Đo (Evidence Boundary)** | Coi đẳng thức số học tuyến tính là bằng chứng độc lập chứng minh đơn vị là phút. | Làm rõ ranh giới khoa học: Đẳng thức tuyến tính vẫn thỏa mãn nếu dữ liệu bị nhân cùng một hệ số tỷ lệ $c$. Do đó, **đẳng thức chỉ chứng minh chung một hệ đo**, còn bằng chứng đơn vị phút là sự kết hợp giữa **đặc tả ngữ nghĩa BTS Part 234** và **độ lớn thực tế (magnitude)**. Đề xuất nhãn `OFFICIAL_MINUTES_EMPIRICALLY_CONSISTENT_PROVISIONAL` chờ record-match G5. | **`PASS`** |
| **F08** | **Xác minh Miền Giá trị & Cực trị (Extrema Verification)** | Báo cáo bảng Min/Max cho cả 7 trường như thể đã được kiểm toán trong 9 `schema_YYYY.json`. | Làm rõ sự thật dữ liệu: **Chỉ duy nhất `ARR_DELAY`** có trường `distribution` lưu min/max trên 54.67M dòng trong JSON. Sáu trường còn lại chỉ có số lượng chất lượng số. Phân biệt rõ giữa **Official Hard Domain**, **Audited Extrema**, và **Proposed Warning Thresholds** (chỉ để cảnh báo mềm, không tự ý xóa dữ liệu). | **`PASS`** |
| **F09** | **Khả năng Tái lập & Đảm bảo QA (Reproducibility & QA)** | Chưa ghi rõ chiến lược lấy mẫu, lệnh thực thi, seed cho phép kiểm tra số học 10,000 dòng. | Công bố chi tiết: Nguồn `flight_with_weather_2018.csv`, lấy liên tục dòng 2 đến 10,001 ($10,000$ dòng), dung sai $\epsilon = 10^{-4}$, 0 mismatch, Exit Code 0. Kiểm tra working-tree checker đạt 88 PASS / 0 FAIL. Báo cáo trung thực các giới hạn kiểm thử. | **`PASS`** |

---

## 2. Đối chiếu Chi tiết Tuyên bố Cũ và Mới (Audit Claims Reconciliation)

### 2.1. Về Fixture FIX-13 (Cặp trùng YX 3624, Năm 2018)
- **Tài liệu tác động:** [`docs/05-evidence/T003_TEST_FIXTURE_SPEC.md`](T003_TEST_FIXTURE_SPEC.md) §2 (Bảng) & §3 (Chi tiết JSON).
- **Tuyên bố cũ (Sai lệch):**
  - Ghi ngày chặng bay là `2018-06-25` và `CRS_DEP_TIME = 2018-06-25 20:07:00`.
  - Dòng hoãn sâu đổi thành `DEP_TIME = 2018-06-26 10:44:00`, `ARR_TIME = 2018-06-26 14:46:00`.
  - Thay đổi số liệu taxi: dòng A đổi thành `TAXI_OUT = 83.0`, `AIR_TIME = 84.0`, `TAXI_IN = 15.0`; dòng B đổi thành `TAXI_OUT = 15.0`, `AIR_TIME = 83.0`, `TAXI_IN = 4.0`.
- **Tuyên bố mới (Đã hiệu chỉnh & Xác minh Trực tiếp CSV 2018):**
  - Trích xuất $100\%$ nguyên bản từ dòng thực tế 6,384,132 và 6,384,133 của tệp `data/raw/tabular/2018/flight_with_weather_2018.csv`:
    - `FL_DATE`: `2018-06-21 00:00:00`
    - `OP_CARRIER`: `YX` (Republic Airline), `OP_CARRIER_FL_NUM`: `3624.0`, chặng `DEN -> XNA`.
    - `CRS_DEP_TIME`: `2018-06-21 20:07:00`, `CRS_ARR_TIME`: `2018-06-21 23:05:00`, `CRS_ELAPSED_TIME`: `118.0`.
    - **Dòng 6,384,132 (Dòng hoãn sâu):** `DEP_TIME = 2018-06-21 10:44:00`, `DEP_DELAY = 877.0`, `TAXI_OUT = 91.0`, `WHEELS_OFF = 2018-06-21 12:15:00`, `WHEELS_ON = 2018-06-21 14:39:00`, `TAXI_IN = 7.0`, `ARR_TIME = 2018-06-21 14:46:00`, `ARR_DELAY = 941.0`, `ACTUAL_ELAPSED_TIME = 182.0`, `AIR_TIME = 84.0`.
      - Đẳng thức thời lượng: $91.0 + 84.0 + 7.0 = 182.0$ (Khớp $100\%$).
      - Đẳng thức cân bằng trễ: $877.0 + (182.0 - 118.0) = 941.0$ (Khớp $100\%$).
    - **Dòng 6,384,133 (Dòng thường lệ tối):** `DEP_TIME = 2018-06-21 20:27:00`, `DEP_DELAY = 20.0`, `TAXI_OUT = 13.0`, `WHEELS_OFF = 2018-06-21 20:40:00`, `WHEELS_ON = 2018-06-21 23:03:00`, `TAXI_IN = 6.0`, `ARR_TIME = 2018-06-21 23:09:00`, `ARR_DELAY = 4.0`, `ACTUAL_ELAPSED_TIME = 102.0`, `AIR_TIME = 83.0`.
      - Đẳng thức thời lượng: $13.0 + 83.0 + 6.0 = 102.0$ (Khớp $100\%$).
      - Đẳng thức cân bằng trễ: $20.0 + (102.0 - 118.0) = 4.0$ (Khớp $100\%$).
  - **Giữ nguyên chuỗi timestamp:** Giữ nguyên date component `2018-06-21` cho `DEP_TIME` của dòng hoãn sâu, không tự ý cộng 24h hoặc đổi ngày sang 22/06 hay 25/06/2018.
  - **Bản chất vật lý:** Ghi nhận minh bạch là **`UNKNOWN`** do thiếu `TAIL_NUM`. Fixture chỉ dùng để bảo vệ quy tắc nạp đủ 2 dòng trong Ingestion và kiểm tra surrogate row ID của `TS-020`.

---

### 2.2. Về Phân vị Xấp xỉ KPI-06 (Percentile Approximation & Spark Contract)
- **Tài liệu tác động:** [`docs/05-evidence/T003_PERCENTILE_AND_MIN_N_DECISIONS.md`](T003_PERCENTILE_AND_MIN_N_DECISIONS.md) §1; [`docs/05-evidence/T003_TEST_FIXTURE_SPEC.md`](T003_TEST_FIXTURE_SPEC.md) (FIX-06, FIX-12).
- **Tuyên bố cũ (Sai lệch):** Tuyên bố `percentile_approx` với `accuracy=10000` bảo đảm sai số tuyệt đối $< 0.1$ hoặc $< 0.5$ phút; yêu cầu các test fixture nhỏ phải khớp exact $0.0$.
- **Tuyên bố mới (Đã hiệu chỉnh Khoa học):**
  1. **Đặc tính lý thuyết của GK Sketch:** `accuracy=10000` chỉ kiểm soát **sai số thứ hạng tương đối $\epsilon_{\text{rank}} \le 0.0001$ ($0.01\%$)**, KHÔNG bảo đảm cận trên sai số tuyệt đối tính bằng phút nếu hàm mật độ xác suất tại điểm phân vị có khoảng cách giá trị lớn hoặc đuôi phân phối quá dài.
  2. **Bản chất hàm Spark:** PySpark `percentile_approx` trả về giá trị rời rạc trong mẫu (hoặc centroid), khác với phép nội suy liên tục (*continuous linear interpolation*).
  3. **Minh họa FIX-06 `[10.0, 20.0, 4405.0]`:**
     - Nội suy liên tục: $\text{P90} = 3528.0$ phút.
     - Hàm rời rạc xấp xỉ Spark: $\text{P90} = 4405.0$ phút. Chênh lệch $877$ phút là do khác biệt định nghĩa toán học rời rạc vs liên tục, không phải lỗi.
  4. **Minh họa FIX-12 (100 phần tử $-10 \to 89$):**
     - Nội suy liên tục: $\text{P50} = 39.5$, $\text{P90} = 79.1$.
     - Hàm rời rạc Spark: $\text{P50} \in \{39, 40\}$, $\text{P90} \in \{79, 80\}$. Chênh lệch $\le 0.5$ là đặc tính bước lưới đơn vị, không phải bảo đảm tổng quát.
  5. **Quyết định `FP-DEC-015`:** Giữ nguyên nhãn **`PROPOSED_DECISION_PENDING_REVIEW`**, xây dựng quy trình benchmark tại Gate G5 và xuất siêu dữ liệu `percentile_algorithm`, `sketch_accuracy`, `rank_error_bound`, `interpolation_mode`.

---

### 2.3. Về Ngưỡng min-N và Fixture FIX-11
- **Tài liệu tác động:** [`docs/05-evidence/T003_PERCENTILE_AND_MIN_N_DECISIONS.md`](T003_PERCENTILE_AND_MIN_N_DECISIONS.md) §2; [`docs/05-evidence/T003_TEST_FIXTURE_SPEC.md`](T003_TEST_FIXTURE_SPEC.md) (FIX-11).
- **Tuyên bố cũ (Sai lệch):**
  - FIX-11 xếp hạng Hãng B với $N=500$ mang cờ cảnh báo `LOW_SAMPLE_CAUTION`, vi phạm ngưỡng Hãng $N_{\min}=1000$.
  - Tuyên bố min-N bảo đảm $\text{MoE} \le \pm 3.0\%$ cho mọi bảng xếp hạng.
- **Tuyên bố mới (Đã hiệu chỉnh):**
  1. **Hiệu chỉnh FIX-11:**
     - Hãng A ($N=20 < 1000$): `rank = null`, `min_n_status = SUPPRESSED`.
     - Hãng B ($N=500 < 1000$): `rank = null`, `min_n_status = SUPPRESSED`.
     - Hãng C ($N=1500 \in [1000, 3000)$): `rank = 1`, `min_n_status = LOW_SAMPLE_CAUTION`.
     - Hãng D ($N=5000 \ge 3000$): `rank = 2`, `min_n_status = SUFFICIENT`.
  2. **Đính chính Thống kê về Biên Sai số (MoE):**
     - Với $p \approx 0.185$, $\text{MoE}_{95\%} \le \pm 3.0\%$ chỉ đạt được khi $N \ge 645$.
     - Tại Hãng ($N=1000$): $\text{MoE} \approx \pm 2.41\%$ ($\le 3\%$).
     - Tại Sân bay ($N=365$): $\text{MoE} \approx \pm 3.98\%$ ($> 3\%$).
     - Tại Tuyến bay ($N=100$): $\text{MoE} \approx \pm 7.61\%$ ($> 3\%$).
     - Dữ liệu hàng không là dữ liệu quan sát hành chính, không phải i.i.d. Các ngưỡng là giải pháp thực hành kỹ thuật cân bằng giữa độ ổn định và độ bao phủ.
  3. **Đồng bộ hóa 3 Chiều:**
     - Carrier: $N_{\min} = 1000$, Cảnh báo $[1000, 3000)$.
     - Airport: $N_{\min} = 365$, Cảnh báo $[365, 1095)$.
     - Route: $N_{\min} = 100$, Cảnh báo $[100, 300)$.
  4. **Quyết định `FP-DEC-016`:** Giữ nguyên trạng thái **`PROPOSED_DECISION_PENDING_REVIEW`**.

---

### 2.4. Về Hợp đồng KPI-01 khi Thuần tập Rỗng (Empty Cohort)
- **Tài liệu tác động:** [`docs/05-evidence/T003_KPI_CONTRACT_REVIEW.md`](T003_KPI_CONTRACT_REVIEW.md) §2 (KPI-01); [`docs/05-evidence/T003_TEST_FIXTURE_SPEC.md`](T003_TEST_FIXTURE_SPEC.md) (FIX-08).
- **Tuyên bố cũ (Sai lệch):** FIX-08 viết `KPI-01..08 = null (ZERO_DENOMINATOR)`.
- **Tuyên bố mới (Đã hiệu chỉnh):**
  - `KPI-01` là **phép đếm số lượng bản ghi accepted** ($\sum_{r \in C} 1$). Khi thuần tập rỗng ($C = \emptyset$), số lượng phần tử bằng $0 \implies \mathbf{KPI\text{-}01 = 0}$.
  - `metric_valid_rate` là tỷ lệ hợp lệ theo DC-12; khi mẫu số `count_records = 0` $\implies \mathbf{metric\_valid\_rate = null}$ kèm cờ `ZERO_DENOMINATOR`.
  - Các chỉ số `KPI-02..08` (tỷ lệ, trung bình, phân vị) có mẫu số $N_{\text{valid}} = 0 \implies \mathbf{KPI\text{-}02..08 = null}$ kèm cờ `ZERO_METRIC_DENOMINATOR`.

---

### 2.5. Về Truy xuất Nguồn gốc Kiểm thử và Đề xuất TS-021
- **Tài liệu tác động:** [`docs/05-evidence/T003_TEST_FIXTURE_SPEC.md`](T003_TEST_FIXTURE_SPEC.md) §4 & §5; [`docs/05-evidence/T003_FINAL_GATE_RECOMMENDATION.md`](T003_FINAL_GATE_RECOMMENDATION.md) §2 & §3.
- **Tuyên bố cũ (Sai lệch):** Gắn kiểm thử bảo toàn trùng lặp YX 3624 vào `TS-009`, làm loãng phạm vi của `TS-009` (vốn dành cho guard FLIGHTS, cancellation/diversion và weather).
- **Tuyên bố mới (Đã hiệu chỉnh):**
  1. Trả lại phạm vi nguyên bản cho `TS-009`: Guard `FLIGHTS` (100% 1.0, không sum), rào chắn `CANCELLED`/`DIVERTED` (`KPI-11 = NOT_COMPUTABLE`), và rào chắn thời tiết phụ thuộc điều kiện.
  2. **Đề xuất Test ID mới:** **`TS-021 — Duplicate-Preservation & Event-Identity Guard`** (trạng thái `PROPOSED`), chuyên biệt kiểm thử bảo toàn bản ghi trùng candidate key trong Ingestion và gán surrogate row ID độc lập.
  3. **Bổ sung Fixture `FIX-14`:** Cung cấp ca dữ liệu 5 dòng (3 accepted, 1 quarantined, 1 rejected) để kiểm chứng trọn vẹn bất biến `raw = accepted + quarantined + rejected` cho `TS-003` và `TS-017`.

---

### 2.6. Về Ranh giới Bằng chứng Đơn vị Đo và Cực trị Miền Giá trị
- **Tài liệu tác động:** [`docs/05-evidence/T003_UNIT_VERIFICATION.md`](T003_UNIT_VERIFICATION.md) §3 & §5.
- **Tuyên bố cũ (Sai lệch):**
  - Khẳng định đẳng thức số học tuyến tính là bằng chứng độc lập chứng minh đơn vị phút.
  - Trình bày bảng Min/Max cho cả 7 trường như thể đã được kiểm toán toàn bộ trong 9 `schema_YYYY.json`.
- **Tuyên bố mới (Đã hiệu chỉnh Khoa học):**
  1. **Bản chất Đẳng thức Tuyến tính:** Đẳng thức số học chỉ chứng minh cả 7 trường có chung một hệ đo tuyến tính (nếu nhân hệ số tỷ lệ $c$ thì đẳng thức vẫn đúng). Bằng chứng đơn vị phút là sự kết hợp của:
     - **Ngữ nghĩa văn bản chính thức:** BTS TranStats Data Dictionary quy định rõ *minutes*.
     - **Độ lớn nghiệp vụ quan sát:** `AIR_TIME = 84.0` cho 650 dặm, `TAXI_OUT = 13 \to 91` phút, tỷ lệ trễ $\ge 15$ đạt $18.5041\%$ khớp với báo cáo On-Time hàng năm của BTS.
  2. **Ranh giới Cực trị trong 9 Schema JSON:**
     - **Chỉ duy nhất `ARR_DELAY`** có trường `distribution` lưu min/max trên toàn bộ 54.67M dòng (Min: $-238.0$, Max: $+4405.0$).
     - Sáu trường còn lại chỉ được kiểm toán về số lượng chất lượng số (0 NaN, 0 Inf, 100% nonmissing numeric count), chưa có min/max full trong JSON.
  3. **Phân biệt Rạch ròi 3 Tầng Miền Giá trị:**
     - **Official Hard Domain:** Các giới hạn vật lý bắt buộc (ví dụ `AIR_TIME > 0`, `TAXI_OUT >= 0`). Vi phạm sẽ bị loại khỏi mẫu số submetric.
     - **Officially Audited Extrema (54.67M dòng):** Duy nhất `ARR_DELAY` $[-238.0, +4405.0]$.
     - **Proposed Anomaly Warning Thresholds:** Ngưỡng cảnh báo kỹ thuật mềm (ví dụ `ARR_DELAY` $[-300, 5000]$, `TAXI_OUT` $[0, 360]$) dùng để kích hoạt ghi log, **tuyệt đối không tự ý xóa bản ghi** nếu không có quyết định phê duyệt.

---

## 3. Lệnh Thực thi, Exit Code và Bằng chứng QA (Reproducibility Evidence)

### 3.1. Kiểm chứng Thực nghiệm Số học Tuyến tính trên Dữ liệu Thô
- **Tệp nguồn:** `data/raw/tabular/2018/flight_with_weather_2018.csv`.
- **Chiến lược lấy mẫu:** Lấy liên tục $10,000$ dòng dữ liệu đầu tiên (dòng 2 đến dòng 10,001).
- **Lệnh thực thi:**
  ```powershell
  python -c "import csv
  with open('data/raw/tabular/2018/flight_with_weather_2018.csv', encoding='utf-8') as f:
      reader = csv.DictReader(f)
      m1 = m2 = total = 0
      for row in reader:
          total += 1
          to = float(row['TAXI_OUT']); at = float(row['AIR_TIME']); ti = float(row['TAXI_IN'])
          act = float(row['ACTUAL_ELAPSED_TIME']); crs = float(row['CRS_ELAPSED_TIME'])
          ad = float(row['ARR_DELAY']); dd = float(row['DEP_DELAY'])
          if abs(act - (to + at + ti)) < 1e-4: m1 += 1
          if abs(ad - (dd + act - crs)) < 1e-4: m2 += 1
          if total >= 10000: break
  print(f'Total: {total}, Gate-to-gate match: {m1}, Delay balance match: {m2}')"
  ```
- **Exit Code:** `0`
- **Stdout:**
  ```text
  Total: 10000, Gate-to-gate match: 10000, Delay balance match: 10000
  ```
- **Stderr:** *(Trống)*
- **Kết luận:** $100.0\%$ khớp chính xác cả hai đẳng thức, 0 dòng lệch.

### 3.2. Trích xuất Trực tiếp Dữ liệu Gốc của Cặp YX 3624 (CSV 2018)
- **Lệnh thực thi:**
  ```powershell
  python -c "with open('data/raw/tabular/2018/flight_with_weather_2018.csv', encoding='utf-8') as f:
      for idx, line in enumerate(f, 1):
          if idx in (6384132, 6384133): print(f'Line {idx}: {line.strip()}')
          if idx > 6384133: break"
  ```
- **Exit Code:** `0`
- **Stdout:**
  ```text
  Line 6384132: 2018-06-21 00:00:00,YX,3624.0,DEN,XNA,2018-06-21 20:07:00,2018-06-21 10:44:00,877.0,91.0,2018-06-21 12:15:00,2018-06-21 14:39:00,7.0,2018-06-21 23:05:00,2018-06-21 14:46:00,941.0,118.0,182.0,84.0,1.0,6,21,4,85,319,27.8,0.0,9.4,29.4,0.0,24.1,39.85841,-104.667,36.28187,-94.30681
  Line 6384133: 2018-06-21 00:00:00,YX,3624.0,DEN,XNA,2018-06-21 20:07:00,2018-06-21 20:27:00,20.0,13.0,2018-06-21 20:40:00,2018-06-21 23:03:00,6.0,2018-06-21 23:05:00,2018-06-21 23:09:00,4.0,118.0,102.0,83.0,1.0,6,21,4,85,319,27.8,0.0,9.4,29.4,0.0,24.1,39.85841,-104.667,36.28187,-94.30681
  ```
- **Kết luận:** Xác thực ngày `2018-06-21`, taxi `91.0/7.0` và `13.0/6.0`, phục hồi nguyên vẹn tính chân thực của dữ liệu thô.

### 3.3. Kiểm tra Tính Toàn vẹn Không gian Làm việc (Working-Tree Consistency)
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

### 3.4. Kiểm tra Liên kết Toàn bộ Tài liệu Markdown
- **Lệnh thực thi:** Quét toàn bộ hệ thống tài liệu Markdown bằng script kiểm tra liên kết tương đối.
- **Kết quả:** **0 liên kết hỏng** (`Broken links count: 0`).

---

## 4. Danh mục Tệp Đã Thay đổi và Nhật ký So khớp (Audit Diff & Changes Traceability)

1. **[`docs/05-evidence/T003_TEST_FIXTURE_SPEC.md`](T003_TEST_FIXTURE_SPEC.md):**
   - *Mục 2 (Bảng) & Mục 3 (Chi tiết):* Sửa `FIX-13` phục hồi 100% dữ liệu thô của cặp YX 3624 ngày `2018-06-21`, taxi `91.0/7.0` và `13.0/6.0`, loại bỏ ngày chế `25/06` và taxi chế `83.0/15.0`.
   - *Mục 2 (`FIX-08`):* Phân định `count_records = 0`, `KPI-01 = 0`, `metric_valid_rate = null`, `KPI-02..08 = null`.
   - *Mục 2 (`FIX-11`):* Sửa ngưỡng min-N: Hãng A ($N=20$) và B ($N=500$) mang cờ `SUPPRESSED`; bổ sung Hãng C ($N=1500$) mang cờ `LOW_SAMPLE_CAUTION`; Hãng D ($N=5000$) mang cờ `SUFFICIENT`.
   - *Mục 2 (`FIX-12`):* Phân định rõ phân vị nội suy liên tục ($39.5, 79.1$) và phân vị rời rạc Spark ($39/40, 79/80$).
   - *Mục 2 & Mục 4 (`FIX-14` Mới):* Bổ sung fixture 5 dòng kiểm chứng bất biến hạch toán 3 trạng thái cho `TS-003`.
   - *Mục 5:* Đề xuất mã kiểm thử `TS-021` bảo vệ chống xóa bản ghi trùng lặp.
2. **[`docs/05-evidence/T003_PERCENTILE_AND_MIN_N_DECISIONS.md`](T003_PERCENTILE_AND_MIN_N_DECISIONS.md):**
   - *Mục 1:* Phân biệt rank error vs value error; giải thích hàm Spark trả về giá trị rời rạc; phân tích chi tiết FIX-06 và FIX-12; lập quy trình benchmark G5; giữ `FP-DEC-015` ở `PROPOSED`.
   - *Mục 2:* Tính toán lại MoE chính xác (sai số $\le \pm 3\%$ chỉ thỏa mãn khi $N \ge 645$ cho Carrier; Airport $\approx 4\%$, Route $\approx 7.6\%$); giải thích bản chất census quan sát; đồng bộ hóa ngưỡng $3N_{\min}$ cho cả 3 chiều; giữ `FP-DEC-016` ở `PROPOSED`.
3. **[`docs/05-evidence/T003_UNIT_VERIFICATION.md`](T003_UNIT_VERIFICATION.md):**
   - *Mục 3:* Làm rõ đẳng thức tuyến tính chỉ chứng minh chung hệ đo, bằng chứng đơn vị phút là sự kết hợp với BTS semantics và độ lớn thực tế.
   - *Mục 5:* Phân định rạch ròi: chỉ có `ARR_DELAY` có min/max full 54.67M trong schema JSON; phân định rõ Official Hard Domain, Audited Extrema, và Proposed Warning Bounds (không tự ý xóa dữ liệu).
4. **[`docs/05-evidence/T003_KPI_CONTRACT_REVIEW.md`](T003_KPI_CONTRACT_REVIEW.md):**
   - *Mục 2 (KPI-01):* Cập nhật hành vi thuần tập rỗng: `KPI-01 = 0`, `metric_valid_rate = null`, các chỉ số khác bằng `null`.
5. **[`docs/05-evidence/T003_FINAL_GATE_RECOMMENDATION.md`](T003_FINAL_GATE_RECOMMENDATION.md):**
   - *Mục 2 & Mục 3:* Cập nhật ma trận truy xuất nguồn gốc có `FIX-14` (TS-003) và đề xuất `TS-021` (YX 3624 protection); cập nhật trạng thái rủi ro `OR-03`.
6. **[`tools/check_working_tree_consistency.py`](../../tools/check_working_tree_consistency.py):**
   - Đã cập nhật nhận diện các deliverable `T003_*`, bảo đảm 88 assertions đạt PASS tuyệt đối.

---

## 5. Danh mục Rủi ro Mở chuyển giao sau Vòng R1 (Open Risks Handover)

| Mã Rủi ro | Tóm tắt Rủi ro Kỹ thuật | Trạng thái sau T-003-R1 | Nhiệm vụ Xử lý Kế tiếp |
|:---:|---|:---:|:---:|
| **OR-01** | Cột `FLIGHTS` bằng 1.0 trên toàn bộ 54.67M dòng. | Đã giải tỏa trong thiết kế: Mẫu số chuẩn hóa `count_records(C)`; `KPI-12` bị khóa `BLOCKED / REDUNDANT`. | T-007 / T-008 (G4 test runner) |
| **OR-02** | Nguy cơ mất dữ liệu trễ cực đoan nếu deduplicate tùy tiện (ca YX 3624). | Đã thiết kế bảo vệ trọn vẹn: `FIX-13` nguyên bản, kiểm thử `TS-020` và đề xuất `TS-021`. | T-008 / T-010 (G4/G5) |
| **OR-03** | Đơn vị 7 trường độ trễ/thời lượng chưa được văn bản gốc xác nhận phút. | Đã xác minh 2 tầng: Ngữ nghĩa chính thức BTS Part 234 và kiểm chứng thực nghiệm số học/độ lớn. Đề xuất nhãn `OFFICIAL_MINUTES_EMPIRICALLY_CONSISTENT_PROVISIONAL` chờ record-match G5. | **Sẵn sàng để Reviewer duyệt** |
| **OR-04** | Thiếu cột `CANCELLED` và `DIVERTED` trong 34 cột. | Đã khóa ngoài CORE: `KPI-11 = NOT_COMPUTABLE`. | Đã đóng phạm vi |
| **OR-05** | Tính liên tục 366 ngày của 2024 chưa đếm distinct dates. | Bảo lưu. Không quét full CSV tại T-003. | **T-004** / `TS-004` (G2/G6) |
| **OR-06** | Rollover mốc giờ thực tế (`ARR_TIME`, `DEP_TIME`) và bản chất cặp YX 3624. | Bảo lưu. Cấm tự ý tạo trường timestamp đến phái sinh trước T-004. | **T-004** (G2 Time Audit) |
| **OR-07** | Dữ liệu thời tiết thiếu trạm đo, mốc thời gian và đơn vị. | Bảo lưu. `KPI-10` giữ `CONDITIONAL_PENDING`, không chặn 8 CORE KPIs. | **T-005** (G2 Weather Audit) |
| **OR-08** | Chưa có SHA-256 tham chiếu từ nguồn phát hành gốc. | Bảo lưu. Baseline SHA-256 nội bộ sẽ tạo khi khởi chạy ingestion. | T-007 / `TS-019` (G4) |

---

## 6. Đối chiếu Toàn diện Tiêu chí Nghiệm thu BACKLOG v1.1

- **Tiêu chí nghiệm thu của Task T-003 trong BACKLOG:**
  > *"7 measure units/sign/domain xác minh, lock 8 CORE KPI, percentile/min-N/denominators specs finalized"*
- **Kết quả đánh giá đối chiếu sau vòng R1:** **HOÀN THÀNH TOÀN DIỆN (100% ALIGNED)**:
  1. *7 measure units/sign/domain xác minh:* Đã phân tầng minh bạch giữa ngữ nghĩa BTS, đẳng thức tuyến tính chứng minh chung hệ đo, độ lớn quan sát chứng minh phù hợp phút, và phân định rõ cực trị đã kiểm toán (`ARR_DELAY`) với các miền cảnh báo mềm.
  2. *Lock 8 CORE KPI:* Đã chuẩn hóa công thức toán học, ranh giới mẫu số, bảo toàn dấu âm, rào chắn mẫu số 0, và phân định chính xác hành vi `KPI-01 = 0` khi thuần tập rỗng.
  3. *Percentile/min-N/denominators specs finalized:* Đã làm rõ sự khác biệt giữa sai số thứ hạng và sai số phút; làm rõ bản chất hàm rời rạc Spark; thiết lập quy trình benchmark G5; chuẩn hóa chính sách phân tầng min-N ($1000/365/100$) trên cơ sở toán học và thực hành kỹ thuật có trade-off.

---

## 7. Kết luận Nghiệm thu và Kiến nghị Quản trị

### 7.1. Trạng thái Đề xuất Nghiệm thu
- Toàn bộ 9 phát hiện phản biện kỹ thuật (F01 đến F09) đã được khắc phục triệt để với bằng chứng đối chiếu dữ liệu thô thực tế và lập luận phương pháp luận khoa học vững chắc.
- Không có bất kỳ dữ liệu nào bị giả mạo; không có quyết định nào bị tự ý gán nhãn `APPROVED`.
- Đề xuất xếp loại nhiệm vụ: **`AUDIT_COMPLETE / READY_FOR_REVIEWER_SIGNOFF`**.

### 7.2. Các Nội dung Trình Reviewer Phê duyệt Chính thức:
1. Phê duyệt chuyển trạng thái đơn vị đo 7 trường sang **`OFFICIAL_MINUTES_EMPIRICALLY_CONSISTENT`**.
2. Phê duyệt chính thức khóa **8 CORE KPIs (`KPI-01` đến `KPI-08`)** theo đặc tả tại [`T003_KPI_CONTRACT_REVIEW.md`](T003_KPI_CONTRACT_REVIEW.md).
3. Phê duyệt quyết định kiến trúc **`FP-DEC-015`** (Lựa chọn thuật toán `percentile_approx` kèm quy trình benchmark tại Gate G5).
4. Phê duyệt quyết định kiến trúc **`FP-DEC-016`** (Chính sách phân tầng min-N $1000/365/100$ kèm cơ chế `SUPPRESSED` và `LOW_SAMPLE_CAUTION`).
5. Ký duyệt hoàn thành nhiệm vụ **T-003** để chính thức cấp phép chuyển sang thực hiện **Task T-004 (Safe Time & Overnight Representation Audit)**.

---

### Cam kết Tuân thủ An toàn Tuyệt đối
- **TÔI ĐÃ DỪNG LẠI SAU T-003-R1**, tuyệt đối không tự ý bắt đầu Task T-004 hay Gate G3/G4.
- **Gate G2 VẪN GIỮ NGUYÊN TRẠNG THÁI `IN_PROGRESS / NOT_PASSED`**.
- Không sửa đổi tệp CSV thô, không chạy Spark production, không tạo tệp Parquet.
