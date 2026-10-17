# T-003: BÁO CÁO RÀ SOÁT VÀ KHÓA ĐẶC TẢ 8 CHỈ SỐ CỐT LÕI (CORE KPI CONTRACT REVIEW & LOCKING SPECIFICATION)

- **Mã nhiệm vụ:** `T-003` (Sub-task 2: KPI Contract Review & Core Lock)
- **Gate:** `G2` (Data Quality, Cohort & Metric Contracts)
- **Ngày thực hiện:** 2026-10-14
- **Vai trò:** Senior Data Engineer, Big Data Analyst & Technical Auditor
- **Trạng thái đề xuất:** **`CORE_LOCKED (Ready for Reviewer Sign-Off)`**
- **Văn bản tuân thủ:** [`AGENTS.md`](../../AGENTS.md), [`DATA_CONTRACT.md`](../02-design/DATA_CONTRACT.md), [`DATA_DICTIONARY.md`](../02-design/DATA_DICTIONARY.md), [`KPI_SPEC.md`](../02-design/KPI_SPEC.md), [`PRD.md`](../01-planning/PRD.md), [`TEST_PLAN.md`](../03-quality/TEST_PLAN.md).

---

## 1. Mục tiêu và Nguyên tắc Khóa Chỉ số (KPI Locking Principles)

Nhiệm vụ **T-003** có trách nhiệm rà soát chi tiết, hoàn thiện và khóa kỹ thuật cho toàn bộ **8 chỉ số cốt lõi (KPI-01 đến KPI-08)** nhằm phục vụ 5 câu hỏi nghiên cứu bắt buộc (`RQ-01` đến `RQ-05`) theo [`PRD.md`](../01-planning/PRD.md).

### 7 Nguyên tắc Bắt buộc Không thể Thay đổi:
1. **Ngưỡng trễ quy chuẩn bao gồm đúng 15 phút:** Cả `KPI-02` (trễ đến) và `KPI-04` (trễ đi) đều áp dụng toán tử lớn hơn hoặc bằng $\ge 15.0$ (tức là $\mathbf{1}[\text{DELAY} \ge 15.0]$), bao gồm chính xác giá trị $15.0$ phút theo chuẩn BTS.
2. **Bảo toàn dấu trung bình (Signed Mean Preservation):** Cả `KPI-03` và `KPI-05` tuyệt đối **không được cắt (clip)** các giá trị âm về $0$. Các chuyến bay đến sớm hoặc đi sớm phải giữ nguyên dấu âm để phản ánh đúng mức độ bù trừ thời gian vận hành.
3. **Mẫu số độc lập cho từng submetric của KPI-07:** `KPI-07` bao gồm 2 submetric riêng biệt (`TAXI_OUT` và `TAXI_IN`). Mỗi submetric có mẫu số hợp lệ $N_{\text{valid}}$ riêng, không được gộp hoặc ép buộc bằng nhau.
4. **Mẫu số độc lập cho từng submetric của KPI-08:** `KPI-08` bao gồm 3 submetric riêng biệt (`AIR_TIME`, `ACTUAL_ELAPSED_TIME`, `CRS_ELAPSED_TIME`). Mỗi submetric có mẫu số hợp lệ $N_{\text{valid}}$ riêng biệt.
5. **Chỉ số không thể tính toán (KPI-11 = NOT_COMPUTABLE):** Bộ dữ liệu 34 cột hoàn toàn thiếu trường `CANCELLED` và `DIVERTED`. Do đó, `KPI-11` (Tỷ lệ hủy/chuyển hướng) được khóa ở trạng thái **`NOT_COMPUTABLE`**, nằm ngoài 8 CORE KPIs.
6. **Chỉ số bị chặn và dư thừa (KPI-12 = BLOCKED / REDUNDANT):** Cột `FLIGHTS` bằng $1.0$ trên toàn bộ $54,674,003$ dòng ($100\%$). Tuyệt đối cấm dùng `sum(FLIGHTS)` làm mẫu số. `KPI-12` bị khóa ở trạng thái **`BLOCKED / REDUNDANT`**, nằm ngoài 8 CORE KPIs.
7. **Chỉ số thời tiết phụ thuộc điều kiện (KPI-10 = CONDITIONAL_PENDING):** Thuộc `RQ-06`, giữ nguyên trạng thái phụ thuộc quyết định tại Gate G2 / Task `T-005`.

---

## 2. Đặc tả Chi tiết 8 Chỉ số Cốt lõi (KPI-01 đến KPI-08)

### KPI-01: Tổng số Bản ghi Hợp lệ trong Thuần tập (Total Accepted Cohort Records)
- **ID & Tên:** `KPI-01` — Total Accepted Cohort Records
- **Câu hỏi nghiên cứu liên quan:** `RQ-01` (Quy mô dữ liệu quan sát và phân phối theo thời gian).
- **Công thức toán học:**
  $$\text{KPI-01}(C) = \sum_{r \in C} 1 = \text{accepted\_row\_count}(C)$$
- **Trường dữ liệu đầu vào:** Toàn bộ bản ghi thuộc thuần tập $C$ sau bộ lọc nhóm (`source_year`, `MONTH`, `OP_CARRIER`, `ORIGIN`, `DEST`).
- **Thuần tập / Filter:** Tập hợp các bản ghi đã được chấp nhận (`accepted`) tại tầng Ingestion, thỏa mãn điều kiện phân nhóm công khai.
- **Tử số & Mẫu số:**
  - Tử số: $\sum_{r \in C} 1$ (số đếm bản ghi).
  - Mẫu số: Bản thân thuần tập $C$.
  - Theo [`DATA_CONTRACT.md`](../02-design/DATA_CONTRACT.md) DC-12: `count_records(C) = accepted_row_count(C)`, `count_metric_valid = count_records(C)`, `excluded_count = 0`, `metric_valid_rate = 1.0` (khi $N > 0$).
- **Đơn vị kết quả & Unit Status:** Đơn vị: `records` (số nguyên không âm); `unit_status: "COUNT_INTEGER"`.
- **Xử lý Null/NaN/Inf:** Không có (bản ghi đã accepted thì luôn đếm được).
- **Hành vi khi Thuần tập Rỗng (Empty Cohort Behavior):**
  - Đối với nhóm rỗng được biểu diễn tường minh (*explicitly materialized group* từ dimensional master):
    - **Giá trị `KPI-01` bằng $0$ bản ghi** (`KPI-01 = 0`, vì đây là phép đếm số lượng phần tử của tập hợp rỗng $\sum_{r \in \emptyset} 1 = 0$).
    - `count_metric_valid = 0`.
    - `metric_valid_rate = null` kèm cờ `ZERO_DENOMINATOR` (do mẫu số `count_records = 0` theo DC-12).
    - Các chỉ số tỷ lệ, trung bình và phân vị (`KPI-02..08`) có giá trị bằng `null` kèm cờ `ZERO_METRIC_DENOMINATOR`.
  - Đối với câu truy vấn `groupBy` thông thường trong Spark SQL: Nếu thuần tập không tồn tại bất kỳ dòng nào, Spark không tạo dòng cho nhóm đó.
- **Điều kiện Đủ Dữ liệu (min-N):** Không áp dụng cho tổng volume bản ghi (luôn báo cáo số đếm thực).
- **Test ID & Tiêu chí Nghiệm thu:** `TS-003`, `TS-017` (Khớp đúng số dòng accepted, hạch toán bảo toàn).
- **Trạng thái Đề xuất:** **`CORE_LOCKED`**.

---

### KPI-02: Tỷ lệ Chậm Đến $\ge 15$ Phút (On-Time Arrival: Late Rate $\ge 15$ min)
- **ID & Tên:** `KPI-02` — Arrival Late Rate ($\ge 15$ minutes)
- **Câu hỏi nghiên cứu liên quan:** `RQ-02`, `RQ-03`, `RQ-04` (Hiệu suất đúng giờ theo thời gian, hãng, sân bay, năm 2020).
- **Công thức toán học:**
  $$\text{KPI-02}(C) = \frac{\sum_{r \in C, \text{valid}(r.\text{ARR\_DELAY})} \mathbf{1}[r.\text{ARR\_DELAY} \ge 15.0]}{N_{\text{valid}}(\text{ARR\_DELAY}, C)}$$
- **Trường dữ liệu đầu vào:** `ARR_DELAY` (float64).
- **Thuần tập / Filter:** Bản ghi accepted trong $C$ có `ARR_DELAY` là số thực hữu hạn (`isfinite`).
- **Tử số & Mẫu số:**
  - Tử số: Số bản ghi hợp lệ trong $C$ có $\text{ARR\_DELAY} \ge 15.0$ (bao gồm chính xác $15.0$).
  - Mẫu số: $N_{\text{valid}}(\text{ARR\_DELAY}, C)$ = `count_metric_valid(ARR_DELAY, C)`.
- **Đơn vị kết quả & Unit Status:** Đơn vị: Tỷ lệ không thứ nguyên $\in [0.0, 1.0]$ (hoặc hiển thị dưới dạng $\% \in [0.0\%, 100.0\%]$); `unit_status: "DIMENSIONLESS_RATIO"`.
- **Quy tắc Signed Values:** Giá trị âm ($< 15.0$) đóng góp $0$ vào tử số, nhưng đóng góp $1$ vào mẫu số $N_{\text{valid}}$.
- **Xử lý Null/NaN/Inf:** Bản ghi có `ARR_DELAY` không hữu hạn bị loại khỏi cả tử số và mẫu số, tính vào `excluded_count`.
- **Chính sách Outlier:** Giữ nguyên toàn bộ các ca trễ cực đoan $> 1000$ phút (vì $\ge 15.0$ luôn bằng $1$).
- **Xử lý Mẫu số 0:** Nếu $N_{\text{valid}} == 0 \implies$ kết quả là `null` kèm cờ `ZERO_METRIC_DENOMINATOR` (không xuất $0\%$).
- **Điều kiện Đủ Dữ liệu (min-N):** Tuân thủ chính sách min-N của T-003 (Carrier $\ge 1000$, Airport $\ge 365$, Route $\ge 100$). Nhỏ hơn ngưỡng sẽ bị gán cờ `SUPPRESSED` khi xếp hạng.
- **Test ID & Tiêu chí Nghiệm thu:** `TS-005` (Kiểm thử biên $14.999$, $15.000$, $15.001$, xử lý null và mẫu số $0$).
- **Trạng thái Đề xuất:** **`CORE_LOCKED`**.

---

### KPI-03: Độ Trễ Đến Trung bình Có Dấu (Mean Arrival Delay — Signed)
- **ID & Tên:** `KPI-03` — Mean Arrival Delay (Signed)
- **Câu hỏi nghiên cứu liên quan:** `RQ-02`, `RQ-03`, `RQ-04`.
- **Công thức toán học:**
  $$\text{KPI-03}(C) = \frac{\sum_{r \in C, \text{valid}(r.\text{ARR\_DELAY})} r.\text{ARR\_DELAY}}{N_{\text{valid}}(\text{ARR\_DELAY}, C)}$$
- **Trường dữ liệu đầu vào:** `ARR_DELAY` (float64).
- **Tử số & Mẫu số:**
  - Tử số: Tổng đại số có dấu của `ARR_DELAY` trên các bản ghi hợp lệ.
  - Mẫu số: $N_{\text{valid}}(\text{ARR\_DELAY}, C)$.
- **Đơn vị kết quả & Unit Status:** Đơn vị: Phút (Minutes); `unit_status: "OFFICIAL_MINUTES_EMPIRICALLY_CONSISTENT_PROVISIONAL"`.
- **Quy tắc Signed Values:** **TUYỆT ĐỐI KHÔNG CLIP VỀ 0**. Giá trị âm (ví dụ $-15.0$) được cộng đại số trực tiếp, phản ánh mức độ đến sớm.
- **Chính sách Outlier:** Giữ nguyên các giá trị trễ lớn (không tự ý cắt ngắn). Độ nhạy đối với outlier được đánh giá bổ sung qua `KPI-06` (P50/P90).
- **Xử lý Mẫu số 0:** Nếu $N_{\text{valid}} == 0 \implies$ kết quả là `null` kèm cờ `ZERO_METRIC_DENOMINATOR`.
- **Test ID & Tiêu chí Nghiệm thu:** `TS-006` (Bảo toàn dấu âm, trung bình số học chính xác, không tràn số).
- **Trạng thái Đề xuất:** **`CORE_LOCKED`**.

---

### KPI-04: Tỷ lệ Chậm Khởi hành $\ge 15$ Phút (On-Time Departure: Late Rate $\ge 15$ min)
- **ID & Tên:** `KPI-04` — Departure Late Rate ($\ge 15$ minutes)
- **Câu hỏi nghiên cứu liên quan:** `RQ-02`, `RQ-03`, `RQ-04`.
- **Công thức toán học:**
  $$\text{KPI-04}(C) = \frac{\sum_{r \in C, \text{valid}(r.\text{DEP\_DELAY})} \mathbf{1}[r.\text{DEP\_DELAY} \ge 15.0]}{N_{\text{valid}}(\text{DEP\_DELAY}, C)}$$
- **Trường dữ liệu đầu vào:** `DEP_DELAY` (float64).
- **Tử số & Mẫu số:**
  - Tử số: Số bản ghi hợp lệ trong $C$ có $\text{DEP\_DELAY} \ge 15.0$ (bao gồm đúng $15.0$).
  - Mẫu số: $N_{\text{valid}}(\text{DEP\_DELAY}, C)$.
- **Đơn vị kết quả & Unit Status:** Đơn vị: Tỷ lệ không thứ nguyên $\in [0.0, 1.0]$; `unit_status: "DIMENSIONLESS_RATIO"`.
- **Quy tắc Signed Values:** Khởi hành sớm ($< 15.0$) đóng góp $0$ vào tử số, $1$ vào mẫu số.
- **Xử lý Mẫu số 0:** Nếu $N_{\text{valid}} == 0 \implies$ `null` kèm `ZERO_METRIC_DENOMINATOR`.
- **Test ID & Tiêu chí Nghiệm thu:** `TS-005`.
- **Trạng thái Đề xuất:** **`CORE_LOCKED`**.

---

### KPI-05: Độ Trễ Khởi hành Trung bình Có Dấu (Mean Departure Delay — Signed)
- **ID & Tên:** `KPI-05` — Mean Departure Delay (Signed)
- **Câu hỏi nghiên cứu liên quan:** `RQ-02`, `RQ-03`, `RQ-04`.
- **Công thức toán học:**
  $$\text{KPI-05}(C) = \frac{\sum_{r \in C, \text{valid}(r.\text{DEP\_DELAY})} r.\text{DEP\_DELAY}}{N_{\text{valid}}(\text{DEP\_DELAY}, C)}$$
- **Trường dữ liệu đầu vào:** `DEP_DELAY` (float64).
- **Tử số & Mẫu số:**
  - Tử số: Tổng đại số có dấu của `DEP_DELAY`.
  - Mẫu số: $N_{\text{valid}}(\text{DEP\_DELAY}, C)$.
- **Đơn vị kết quả & Unit Status:** Đơn vị: Phút (Minutes); `unit_status: "OFFICIAL_MINUTES_EMPIRICALLY_CONSISTENT_PROVISIONAL"`.
- **Quy tắc Signed Values:** Không clip giá trị âm; giữ nguyên độ trễ khởi hành thực tế.
- **Xử lý Mẫu số 0:** Nếu $N_{\text{valid}} == 0 \implies$ `null` kèm `ZERO_METRIC_DENOMINATOR`.
- **Test ID & Tiêu chí Nghiệm thu:** `TS-006`.
- **Trạng thái Đề xuất:** **`CORE_LOCKED`**.

---

### KPI-06: Phân vị Độ Trễ Đến (Arrival Delay Quantiles: P50 Median & P90 Tail)
- **ID & Tên:** `KPI-06` — Arrival Delay Percentiles (P50 & P90)
- **Câu hỏi nghiên cứu liên quan:** `RQ-02`, `RQ-03`, `RQ-04` (Khắc phục hạn chế nhạy cảm với outlier của trung bình số học).
- **Công thức toán học:**
  - `KPI-06-P50`: $\text{Quantile}_{0.50}(\{r.\text{ARR\_DELAY} \mid r \in C, \text{valid}(r.\text{ARR\_DELAY})\})$ (Trung vị).
  - `KPI-06-P90`: $\text{Quantile}_{0.90}(\{r.\text{ARR\_DELAY} \mid r \in C, \text{valid}(r.\text{ARR\_DELAY})\})$ (Đuôi phân phối trễ nặng).
- **Trường dữ liệu đầu vào:** `ARR_DELAY` (float64).
- **Mẫu số thuần tập:** $N_{\text{valid}}(\text{ARR\_DELAY}, C)$.
- **Đơn vị kết quả & Unit Status:** Đơn vị: Phút (Minutes); `unit_status: "OFFICIAL_MINUTES_EMPIRICALLY_CONSISTENT_PROVISIONAL"`.
- **Phương pháp tính toán (Xem chi tiết tại T003_PERCENTILE_AND_MIN_N_DECISIONS.md):**
  - Trong PySpark quy mô lớn (G5/G6): Áp dụng `percentile_approx(ARR_DELAY, array(0.5, 0.9), accuracy=10000)`.
  - Trong Unit/Synthetic test fixtures (G2/G4): Tính phân vị chính xác (`linear interpolation` Type 7 hoặc thống kê thứ tự rời rạc exact).
  - Ràng buộc sai số thuật toán: Chặn trên sai số thứ hạng lý thuyết $\epsilon_{\text{rank}} \le 1/\text{accuracy} = 0.01\%$; kết quả Spark ở G2 giữ trạng thái `PENDING_G5_VALIDATION`. Không cam kết sai số tuyệt đối $\le 0.5$m hay $\le 1.0$m phổ quát trên mọi phân phối.
- **Xử lý Mẫu số 0:** Nếu $N_{\text{valid}} == 0 \implies$ `null` kèm `ZERO_METRIC_DENOMINATOR`.
- **Test ID & Tiêu chí Nghiệm thu:** `TS-008` (Đối chiếu thuật toán quantile, kiểm tra dung sai xấp xỉ).
- **Trạng thái Đề xuất:** **`CORE_LOCKED`**.

---

### KPI-07: Hiệu suất Thời gian Lăn Bánh (Taxi Performance: Taxi-Out & Taxi-In)
- **ID & Tên:** `KPI-07` — Taxi Times Performance (2 Submetrics độc lập)
- **Câu hỏi nghiên cứu liên quan:** `RQ-05` (Thời gian trên mặt đất tại sân bay đi và sân bay đến).
- **Hai Submetrics Độc lập Bắt buộc:**
  1. `KPI-07-TAXI_OUT`: Thời gian lăn ra trung bình tại sân bay khởi hành:
     $$\text{KPI-07-TAXI\_OUT}(C) = \frac{\sum_{r \in C, \text{valid}(r.\text{TAXI\_OUT})} r.\text{TAXI\_OUT}}{N_{\text{valid}}(\text{TAXI\_OUT}, C)}$$
  2. `KPI-07-TAXI_IN`: Thời gian lăn vào trung bình tại sân bay đến:
     $$\text{KPI-07-TAXI\_IN}(C) = \frac{\sum_{r \in C, \text{valid}(r.\text{TAXI\_IN})} r.\text{TAXI\_IN}}{N_{\text{valid}}(\text{TAXI\_IN}, C)}$$
- **Trường dữ liệu đầu vào:** `TAXI_OUT` (float64) và `TAXI_IN` (float64).
- **Quy tắc Mẫu số Riêng biệt:** $N_{\text{valid}}(\text{TAXI\_OUT}, C)$ và $N_{\text{valid}}(\text{TAXI\_IN}, C)$ được tính **hoàn toàn độc lập**. Nếu một bản ghi có `TAXI_OUT` hợp lệ nhưng `TAXI_IN` bị lỗi/khuyết thiếu, bản ghi đó vẫn đóng góp vào submetric taxi-out mà không ảnh hưởng đến taxi-in.
- **Đơn vị kết quả & Unit Status:** Đơn vị: Phút (Minutes); `unit_status: "OFFICIAL_MINUTES_EMPIRICALLY_CONSISTENT_PROVISIONAL"`.
- **Miền hợp lệ:** $\text{TAXI\_OUT} \ge 0$, $\text{TAXI\_IN} \ge 0$.
- **Xử lý Mẫu số 0:** Từng submetric độc lập: nếu $N_{\text{valid}} == 0 \implies$ `null` kèm `ZERO_METRIC_DENOMINATOR`.
- **Test ID & Tiêu chí Nghiệm thu:** `TS-006`, `TS-008` (Mẫu số submetric phân ly, không copy chéo mẫu số).
- **Trạng thái Đề xuất:** **`CORE_LOCKED`**.

---

### KPI-08: Hiệu suất Thời lượng Hành trình & Thời gian Bay (Journey Duration & Air Time Performance)
- **ID & Tên:** `KPI-08` — Journey & Air Duration Performance (3 Submetrics độc lập)
- **Câu hỏi nghiên cứu liên quan:** `RQ-05` (Hiệu suất vận hành trên không và tổng thời lượng hành trình).
- **Ba Submetrics Độc lập Bắt buộc:**
  1. `KPI-08-AIR_TIME`: Thời gian bay trên không trung bình:
     $$\text{KPI-08-AIR\_TIME}(C) = \frac{\sum_{r \in C, \text{valid}(r.\text{AIR\_TIME})} r.\text{AIR\_TIME}}{N_{\text{valid}}(\text{AIR\_TIME}, C)}$$
  2. `KPI-08-ACTUAL_ELAPSED_TIME`: Tổng thời gian hành trình thực tế trung bình:
     $$\text{KPI-08-ACTUAL\_ELAPSED\_TIME}(C) = \frac{\sum_{r \in C, \text{valid}(r.\text{ACTUAL\_ELAPSED\_TIME})} r.\text{ACTUAL\_ELAPSED\_TIME}}{N_{\text{valid}}(\text{ACTUAL\_ELAPSED\_TIME}, C)}$$
  3. `KPI-08-CRS_ELAPSED_TIME`: Tổng thời gian hành trình lịch trình trung bình:
     $$\text{KPI-08-CRS\_ELAPSED\_TIME}(C) = \frac{\sum_{r \in C, \text{valid}(r.\text{CRS\_ELAPSED\_TIME})} r.\text{CRS\_ELAPSED\_TIME}}{N_{\text{valid}}(\text{CRS\_ELAPSED\_TIME}, C)}$$
- **Trường dữ liệu đầu vào:** `AIR_TIME` (float64), `ACTUAL_ELAPSED_TIME` (float64), `CRS_ELAPSED_TIME` (float64).
- **Quy tắc Mẫu số Riêng biệt:** Mỗi submetric tính trên mẫu số hợp lệ riêng biệt $N_{\text{valid}}(m, C)$.
- **Đơn vị kết quả & Unit Status:** Đơn vị: Phút (Minutes); `unit_status: "OFFICIAL_MINUTES_EMPIRICALLY_CONSISTENT_PROVISIONAL"`.
- **Miền hợp lệ:** Cả 3 trường đều bắt buộc $> 0$.
- **Xử lý Mẫu số 0:** Từng submetric độc lập: nếu $N_{\text{valid}} == 0 \implies$ `null` kèm `ZERO_METRIC_DENOMINATOR`.
- **Test ID & Tiêu chí Nghiệm thu:** `TS-006`, `TS-008`.
- **Trạng thái Đề xuất:** **`CORE_LOCKED`**.

---

## 3. Tổng hợp Bảng Danh mục Chỉ số Dự án (Project KPI Catalog Summary)

| KPI ID | Tên Chỉ số | Submetrics | Loại Chỉ số | RQ Phục vụ | Trạng thái Kỹ thuật | Trạng thái Đề xuất Khóa |
|---|---|:---:|:---:|:---:|:---:|:---:|
| **KPI-01** | Total Accepted Records | 1 | CORE | RQ-01 | Hoàn thiện | **`CORE_LOCKED`** |
| **KPI-02** | Arrival Late Rate ($\ge 15$m) | 1 | CORE | RQ-02/03/04 | Hoàn thiện | **`CORE_LOCKED`** |
| **KPI-03** | Mean Arrival Delay (Signed) | 1 | CORE | RQ-02/03/04 | Hoàn thiện | **`CORE_LOCKED`** |
| **KPI-04** | Departure Late Rate ($\ge 15$m) | 1 | CORE | RQ-02/03/04 | Hoàn thiện | **`CORE_LOCKED`** |
| **KPI-05** | Mean Departure Delay (Signed) | 1 | CORE | RQ-02/03/04 | Hoàn thiện | **`CORE_LOCKED`** |
| **KPI-06** | Arrival Delay P50 & P90 | 2 (P50, P90) | CORE | RQ-02/03/04 | Hoàn thiện | **`CORE_LOCKED`** |
| **KPI-07** | Mean Taxi Times | 2 (Out, In) | CORE | RQ-05 | Hoàn thiện | **`CORE_LOCKED`** |
| **KPI-08** | Mean Flight & Journey Duration | 3 (Air, Actual, CRS) | CORE | RQ-05 | Hoàn thiện | **`CORE_LOCKED`** |
| *KPI-09* | Mean Positive Delay per valid record | 1 | OPTIONAL | RQ-02 | Bản nháp tùy chọn | `OPTIONAL_DRAFT` |
| *KPI-10* | Weather-Conditioned Delay | Phụ thuộc bins | CONDITIONAL | RQ-06 | Đang chờ G2/T-005 | `CONDITIONAL_PENDING` |
| *KPI-11* | Flight Cancellation/Divert Rate | — | NGOÀI CORE | — | Thiếu cột cờ | **`NOT_COMPUTABLE`** |
| *KPI-12* | Total Flights via `FLIGHTS` | — | NGOÀI CORE | — | Cột không đổi (1.0) | **`BLOCKED / REDUNDANT`** |

---

## 4. Kết luận Nghiệm thu B4

- Toàn bộ 8 CORE KPIs đã được đặc tả toán học chi tiết, ranh giới mẫu số rạch ròi, xử lý giá trị âm và xử lý mẫu số 0 nghiêm ngặt theo đúng [`DATA_CONTRACT.md`](../02-design/DATA_CONTRACT.md) DC-11/12.
- Các yêu cầu không thay đổi công thức, giữ `KPI-11` là `NOT_COMPUTABLE`, giữ `KPI-12` là `BLOCKED / REDUNDANT`, giữ `KPI-10` là `CONDITIONAL_PENDING` đã được tuân thủ 100%.
- Hồ sơ sẵn sàng để **Reviewer ký duyệt khóa chính thức 8 CORE KPIs**.
