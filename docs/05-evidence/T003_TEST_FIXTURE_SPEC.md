# T-003: ĐẶC TẢ BỘ DỮ LIỆU KIỂM THỬ TỔNG HỢP VÀ TEST BẢO VỆ CHỈ SỐ (SYNTHETIC TEST FIXTURE SPECIFICATION)

- **Mã nhiệm vụ:** `T-003` (Sub-task 4: Test Fixture Design & Protective Test Spec — Bản cập nhật R1)
- **Gate:** `G2` (Data Quality, Cohort & Metric Contracts)
- **Ngày thực hiện:** 2026-10-14
- **Vai trò:** Senior Big Data Engineer, Statistical Methodology Reviewer & Data Quality Auditor
- **Trạng thái tài liệu:** **`SPECIFIED / DESIGN_BASELINE`** (Thiết kế đặc tả kiểm thử cho G2; chưa chạy test code production)
- **Văn bản tuân thủ:** [`AGENTS.md`](../../AGENTS.md), [`DATA_CONTRACT.md`](../02-design/DATA_CONTRACT.md), [`KPI_SPEC.md`](../02-design/KPI_SPEC.md), [`TEST_PLAN.md`](../03-quality/TEST_PLAN.md) (tiêu chí `TS-002`, `TS-003`, `TS-005`, `TS-006`, `TS-008`, `TS-017`, `TS-018`, `TS-020` và đề xuất `TS-021`).

---

## 1. Mục tiêu và Ranh giới Thiết kế Kiểm thử tại Gate G2

Tại Gate **G2**, trách nhiệm kỹ thuật là thiết kế hoàn chỉnh các kịch bản kiểm thử, định nghĩa các bộ dữ liệu giả lập tổng hợp (*synthetic test fixtures*), xác định kết quả kỳ vọng (*expected outputs*) và đối chiếu với ma trận kiểm thử của [`TEST_PLAN.md`](../03-quality/TEST_PLAN.md).

> [!IMPORTANT]
> **Ranh giới Bắt buộc:** Việc thiết kế và viết đặc tả fixture trên tài liệu **KHÔNG đồng nghĩa với việc test code production đã đạt `PASS`**. Trạng thái kiểm thử tại G2 là **`SPECIFIED / DESIGN_BASELINE`**. Việc thực thi mã nguồn kiểm thử thực tế sẽ diễn ra tại Gate G4 (synthetic runner) và Gate G5 (smoke test trên Spark).

---

## 2. Bảng Danh mục 14 Ca Kiểm thử Tổng hợp (14 Synthetic Test Fixtures)

| Mã Fixture | Tên Kịch bản Kiểm thử | Bộ dữ liệu Đầu vào Giả lập ($D$) | Kết quả Kỳ vọng (Expected Output) | Tiêu chí Bảo vệ Nghiệp vụ | Liên kết TEST_PLAN |
|:---:|---|---|---|---|:---:|
| **FIX-01** | **Negative Delay (Đến sớm)** | `ARR_DELAY = [-25.0, -10.0, -5.0]` ($N=3$) | `KPI-02 = 0.0%`<br>`KPI-03 = -13.3333 phút` | Bảo đảm các chuyến bay đến sớm không bị clip về 0; không được làm méo mó trung bình có dấu. | `TS-005`, `TS-006` |
| **FIX-02** | **Zero Delay (Đúng giờ tuyệt đối)** | `ARR_DELAY = [0.0, 0.0, 0.0]` ($N=3$) | `KPI-02 = 0.0%`<br>`KPI-03 = 0.0 phút`<br>`KPI-06-P50 = 0.0` | Đóng góp $0$ vào tử số tỷ lệ trễ; đóng góp $0$ vào tổng độ trễ; đóng góp $1$ vào mẫu số $N_{\text{valid}}$. | `TS-005`, `TS-006` |
| **FIX-03** | **Boundary 14.999 (Cận dưới ngưỡng trễ)** | `ARR_DELAY = [14.999]` ($N=1$) | `KPI-02 = 0.0%` ($\mathbf{1}[\ge 15.0] == 0$)<br>`KPI-03 = 14.999` | Nghiêm cấm làm tròn lên $15.0$ trước khi so sánh; giá trị $< 15.0$ không được tính là trễ. | `TS-005` |
| **FIX-04** | **Boundary 15.000 (Đúng ngưỡng trễ quy chuẩn)** | `ARR_DELAY = [15.000]` ($N=1$) | `KPI-02 = 100.0%` ($\mathbf{1}[\ge 15.0] == 1$)<br>`KPI-03 = 15.000` | **Bắt buộc bao gồm đúng 15.0** theo định nghĩa BTS On-Time. Toán tử $\ge$ thay vì $>$. | `TS-005` |
| **FIX-05** | **Boundary 15.001 (Cận trên ngưỡng trễ)** | `ARR_DELAY = [15.001]` ($N=1$) | `KPI-02 = 100.0%` ($\mathbf{1}[\ge 15.0] == 1$)<br>`KPI-03 = 15.001` | Trễ vượt ngưỡng quy chuẩn. | `TS-005` |
| **FIX-06** | **Extreme Positive Delay (Trễ cực đoan đa ngày)** | `ARR_DELAY = [10.0, 20.0, 4405.0]` ($N=3$) | `KPI-02 = 66.67%` ($2/3$)<br>`KPI-03 = 1478.33 phút`<br>`KPI-06-P50 = 20.0 phút`<br>`KPI-06-P90 (continuous) = 3528.0 phút`<br>`KPI-06-P90 (discrete approx) = 4405.0 phút` | **Không được winsorize hoặc tự ý cắt bỏ outlier**. Trung bình phản ánh đúng tổng thời gian trễ thực tế; P50 giữ độ trễ trung vị điển hình ($20$ phút). Làm rõ khác biệt giữa phân vị liên tục và phân vị rời rạc xấp xỉ. | `TS-006`, `TS-008` |
| **FIX-07** | **Non-finite Values (Null / NaN / +Inf / -Inf)** | `ARR_DELAY = [10.0, NaN, 20.0, null, Inf, 30.0]` ($N_{\text{raw}}=6$) | `count_records = 6`<br>`count_metric_valid = 3`<br>`excluded_count = 3`<br>`metric_valid_rate = 50.0%`<br>`KPI-02 = 66.67%` ($2/3$ có $\ge 15$)<br>`KPI-03 = 20.0 phút` | Loại trừ an toàn các giá trị không hữu hạn ra khỏi $N_{\text{valid}}$; không biến đổi silent cast thành $0$; hạch toán đầy đủ `excluded_count`. | `TS-002`, `TS-005`, `TS-017` |
| **FIX-08** | **Empty Cohort (Thuần tập rỗng)** | Nhóm lọc không có bản ghi nào ($C = \emptyset$) sau materialized grouping | `count_records = 0`<br>`KPI-01 = 0` (số đếm bản ghi là 0)<br>`count_metric_valid = 0`<br>`metric_valid_rate = null` (`ZERO_DENOMINATOR`)<br>`KPI-02..08 = null` (`ZERO_METRIC_DENOMINATOR`) | Phân định rạch ròi: `KPI-01` là phép đếm bản ghi (kết quả bằng $0$); các tỷ lệ, trung bình và phân vị (`KPI-02..08`) có mẫu số bằng $0$ nên trả về `null`. Không chia cho 0. | `TS-005`, `TS-017` |
| **FIX-09** | **Non-empty Cohort with 100% Invalid Metrics** | $5$ bản ghi accepted, nhưng cả 5 đều có `ARR_DELAY = null` | `count_records = 5`<br>`KPI-01 = 5`<br>`count_metric_valid = 0`<br>`excluded_count = 5`<br>`metric_valid_rate = 0.0%`<br>`KPI-02, 03, 06 = null` (`ZERO_METRIC_DENOMINATOR`) | Thuần tập có 5 bản ghi (`KPI-01 = 5`), nhưng mẫu số hợp lệ $N_{\text{valid}} = 0 \implies$ các chỉ số đo lường trả về `null`. | `TS-005`, `TS-017` |
| **FIX-10** | **Heterogeneous Submetric Nulls (Null không đồng nhất giữa các trường)** | Bản ghi $r_1$: `TAXI_OUT = 15.0`, `TAXI_IN = null`<br>Bản ghi $r_2$: `TAXI_OUT = 20.0`, `TAXI_IN = 8.0`<br>Bản ghi $r_3$: `TAXI_OUT = null`, `TAXI_IN = 10.0` | `KPI-07-TAXI_OUT`:<br>$N_{\text{valid}} = 2$, Trung bình $= 17.5$<br>`KPI-07-TAXI_IN`:<br>$N_{\text{valid}} = 2$, Trung bình $= 9.0$ | **Mẫu số của từng submetric độc lập tuyệt đối**. Không ép $N_{\text{valid}}$ của Taxi-In phải bằng Taxi-Out; không loại bỏ cả hàng nếu chỉ khuyết 1 trường. | `TS-006`, `TS-008` |
| **FIX-11** | **min-N Ranking Suppression & Caution Guard** | Chiều `carrier-year` ($N_{\min}=1000$, $3N_{\min}=3000$):<br>Hãng A: $N=20$, Trễ $0\%$<br>Hãng B: $N=500$, Trễ $5\%$<br>Hãng C: $N=1500$, Trễ $10\%$<br>Hãng D: $N=5000$, Trễ $15\%$ | Hãng A: `rank = null`, `min_n_status = SUPPRESSED`<br>Hãng B: `rank = null`, `min_n_status = SUPPRESSED`<br>Hãng C: `rank = 1`, `min_n_status = LOW_SAMPLE_CAUTION`<br>Hãng D: `rank = 2`, `min_n_status = SUFFICIENT` | **Tuân thủ đúng ngưỡng $N_{\min}=1000$**: Cả Hãng A ($20 < 1000$) và Hãng B ($500 < 1000$) đều bị `SUPPRESSED`. Hãng C ($1500 \in [1000, 3000)$) được xếp hạng 1 kèm cờ cảnh báo `LOW_SAMPLE_CAUTION`. Hãng D xếp hạng 2 chuẩn. | `TS-008` |
| **FIX-12** | **Exact vs Approximate Percentile Verification** | Mảng số học 100 phần tử từ $-10.0$ đến $+89.0$ ($N=100$, step $1.0$) | `P50_exact (continuous) = 39.5`<br>`P90_exact (continuous) = 79.1`<br>`P50_approx (discrete GK) = 39 hoặc 40`<br>`P90_approx (discrete GK) = 79 hoặc 80`<br>Sai số rank: $\le 0.01\%$ | **Sửa mâu thuẫn số học (C02):** Phân vị xấp xỉ Spark trả về giá trị rời rạc trong mẫu ($79$ hoặc $80$). Nếu so với chuẩn nội suy liên tục ($79.1$), độ lệch là $|79 - 79.1| = 0.1$ hoặc $|80 - 79.1| = 0.9$ (chặn trên độ lệch là $\le 0.9$ đơn vị, không phải $\le 0.5$). Nếu so với phân vị rời rạc chuẩn thì sai số là $0.0$. | `TS-008` |
| **FIX-13** | **YX 3624 Pristine Raw & Behavioral Ingestion Protection** | Trích xuất $100\%$ nguyên bản từ CSV 2018 (dòng 6,384,132 & 6,384,133, ngày `2018-06-21`):<br>Dòng A: hoãn $+941$m, `TAXI_OUT=91.0`, `AIR_TIME=84.0`, `TAXI_IN=7.0`<br>Dòng B: hoãn $+4$m, `TAXI_OUT=13.0`, `AIR_TIME=83.0`, `TAXI_IN=6.0` | `count_records = 2` (Cả 2 dòng được nạp đầy đủ)<br>`KPI-02 = 50.0%` ($1/2$ có trễ $\ge 15$m)<br>`KPI-03 = +472.5 phút`<br>Surrogate Row ID: Độc lập | **Bảo vệ chính sách Zero Arbitrary Deduplication**. Giữ nguyên vẹn dữ liệu thô gốc (ngày 21/06/2018). Không tự ý sửa ngày sang 25/06 hay 26/06; không tự chế số liệu taxi. Bản chất vật lý `UNKNOWN`. | `TS-020`, đề xuất `TS-021` |
| **FIX-14** | **Three-State Row Accounting Invariant (TS-003 Baseline)** | 5 dòng dữ liệu đầu vào thô:<br>3 dòng hợp lệ (`accepted`)<br>1 dòng sai cú pháp mã sân bay (`quarantined`, mã lý do `INVALID_IATA_AIRPORT_SYNTAX:ORIGIN_NOT_3_ALPHA`)<br>1 dòng thiếu số lượng cột schema (`rejected`, mã lý do `COLUMN_COUNT_MISMATCH: EXPECTED_34_FOUND_6`) | `raw_row_count = 5`<br>`accepted_row_count = 3`<br>`quarantined_row_count = 1`<br>`rejected_row_count = 1`<br>Bất biến: $5 = 3 + 1 + 1$<br>`ingest_acceptance_rate = 3/5 = 60.0%` | Kiểm chứng bất biến `raw = accepted + quarantined + rejected` theo DC-11 và [`TEST_PLAN.md`](../03-quality/TEST_PLAN.md) dòng 30. Các nhóm group KPI chỉ được tính trên tập 3 dòng accepted. | `TS-003`, `TS-017` |

---

## 3. Đặc tả Chi tiết Fixture FIX-13 (Cặp trùng YX 3624 DEN $\to$ XNA, Năm 2018)

Bản đặc tả này đối chiếu trực tiếp với các dòng thực tế trích xuất từ tệp `data/raw/tabular/2018/flight_with_weather_2018.csv`:

### 3.1. Dữ liệu Nguồn Gốc Tuyệt đối (ORIGINAL_RAW_VALUES)
```json
{
  "fixture_id": "FIX-13",
  "data_provenance": "data/raw/tabular/2018/flight_with_weather_2018.csv",
  "candidate_key": {
    "FL_DATE": "2018-06-21 00:00:00",
    "OP_CARRIER": "YX",
    "OP_CARRIER_FL_NUM": 3624.0,
    "ORIGIN": "DEN",
    "DEST": "XNA",
    "CRS_DEP_TIME": "2018-06-21 20:07:00"
  },
  "raw_records": [
    {
      "source_row_index": 6384132,
      "record_label": "RECORD_A_DEEP_DELAY",
      "FL_DATE": "2018-06-21 00:00:00",
      "CRS_DEP_TIME": "2018-06-21 20:07:00",
      "DEP_TIME": "2018-06-21 10:44:00",
      "DEP_DELAY": 877.0,
      "TAXI_OUT": 91.0,
      "WHEELS_OFF": "2018-06-21 12:15:00",
      "WHEELS_ON": "2018-06-21 14:39:00",
      "TAXI_IN": 7.0,
      "CRS_ARR_TIME": "2018-06-21 23:05:00",
      "ARR_TIME": "2018-06-21 14:46:00",
      "ARR_DELAY": 941.0,
      "CRS_ELAPSED_TIME": 118.0,
      "ACTUAL_ELAPSED_TIME": 182.0,
      "AIR_TIME": 84.0,
      "FLIGHTS": 1.0,
      "arithmetic_identity_check": "91.0 + 84.0 + 7.0 == 182.0 (PASS)",
      "delay_balance_check": "877.0 + (182.0 - 118.0) == 941.0 (PASS)"
    },
    {
      "source_row_index": 6384133,
      "record_label": "RECORD_B_REGULAR_DELAY",
      "FL_DATE": "2018-06-21 00:00:00",
      "CRS_DEP_TIME": "2018-06-21 20:07:00",
      "DEP_TIME": "2018-06-21 20:27:00",
      "DEP_DELAY": 20.0,
      "TAXI_OUT": 13.0,
      "WHEELS_OFF": "2018-06-21 20:40:00",
      "WHEELS_ON": "2018-06-21 23:03:00",
      "TAXI_IN": 6.0,
      "CRS_ARR_TIME": "2018-06-21 23:05:00",
      "ARR_TIME": "2018-06-21 23:09:00",
      "ARR_DELAY": 4.0,
      "CRS_ELAPSED_TIME": 118.0,
      "ACTUAL_ELAPSED_TIME": 102.0,
      "AIR_TIME": 83.0,
      "FLIGHTS": 1.0,
      "arithmetic_identity_check": "13.0 + 83.0 + 6.0 == 102.0 (PASS)",
      "delay_balance_check": "20.0 + (102.0 - 118.0) == 4.0 (PASS)"
    }
  ]
}
```

### 3.2. Ranh giới Nghiệp vụ và Quy tắc Kiểm chứng Bắt buộc
1. **Bảo tồn Dữ liệu Nguyên bản:** Giữ đúng chuỗi timestamp `2018-06-21 10:44:00` và `2018-06-21 14:46:00` như được lưu trong CSV thô. Không được tự ý cộng 24 giờ hay sửa chuỗi ngày thành `2018-06-22` hoặc `2018-06-25`.
2. **Bảo toàn Số học Gốc:** Giữ đúng các trường taxi (`91.0 / 7.0` cho dòng A và `13.0 / 6.0` cho dòng B). Không được thay đổi sang `83.0 / 15.0`.
3. **Mục đích của Fixture FIX-13:**
   - Dùng để bảo vệ hành vi nạp dữ liệu (*ingestion behavioral protection*): pipeline nạp chấp nhận cả 2 bản ghi vào thuần tập `accepted` vì cả hai đều thỏa mãn đầy đủ các quy tắc chất lượng dữ liệu cốt lõi (34 cột hợp lệ, đúng kiểu số, đúng cú pháp sân bay), mà không bị loại bỏ/deduplicate chỉ vì trùng candidate key. **Quy tắc Zero Arbitrary Deduplication tuyệt đối không cho phép bất kỳ bản ghi nào bỏ qua các quy tắc kiểm tra chất lượng cốt lõi (*core quality rules*)**.
   - Kiểm tra bộ sinh khóa đại diện dòng (*surrogate row identifier* theo `TS-020`) tạo ra 2 mã định danh ổn định, phân biệt được 2 dòng này trên các phân vùng Spark.
4. **Ranh giới Khoa học Thực thể Vật lý:**
   - Việc nạp cả 2 bản ghi **không đồng nghĩa với việc khẳng định có 2 máy bay vật lý riêng biệt**. Do schema thiếu trường số hiệu đuôi tàu bay (`TAIL_NUM`), mối quan hệ 1-1 với thực thể vật lý giữ nguyên phân loại **`UNKNOWN`** và bàn giao cho **T-004** rà soát thời gian.

---

## 4. Đặc tả Chi tiết Fixture FIX-14 (Three-State Row Accounting Invariant)

Fixture này phục vụ trực tiếp việc kiểm chứng bài kiểm thử `TS-003` và `TS-017`, đã được lưu trữ thành tệp CSV thực thi tại [`docs/05-evidence/T003_FIX14_accounting_fixture.csv`](T003_FIX14_accounting_fixture.csv) và tệp metadata [`docs/05-evidence/T003_FIX14_accounting_fixture.json`](T003_FIX14_accounting_fixture.json):

### 4.1. Cấu trúc 5 Dòng Vật lý Thô (Raw Physical CSV Lines)
Tệp fixture bao gồm đúng 1 dòng tiêu đề 34 cột theo [`DATA_DICTIONARY.md`](../02-design/DATA_DICTIONARY.md) và 5 dòng dữ liệu vật lý:

```csv
FL_DATE,OP_CARRIER,OP_CARRIER_FL_NUM,ORIGIN,DEST,CRS_DEP_TIME,DEP_TIME,DEP_DELAY,TAXI_OUT,WHEELS_OFF,WHEELS_ON,TAXI_IN,CRS_ARR_TIME,ARR_TIME,ARR_DELAY,CRS_ELAPSED_TIME,ACTUAL_ELAPSED_TIME,AIR_TIME,FLIGHTS,MONTH,DAY_OF_MONTH,DAY_OF_WEEK,ORIGIN_INDEX,DEST_INDEX,O_TEMP,O_PRCP,O_WSPD,D_TEMP,D_PRCP,D_WSPD,O_LATITUDE,O_LONGITUDE,D_LATITUDE,D_LONGITUDE
2018-06-01 00:00:00,AA,1001.0,ORD,DFW,2018-06-01 08:00:00,2018-06-01 08:05:00,5.0,15.0,2018-06-01 08:20:00,2018-06-01 10:20:00,5.0,2018-06-01 10:25:00,2018-06-01 10:25:00,0.0,145.0,140.0,120.0,1.0,6,1,5,10,20,20.0,0.0,10.0,25.0,0.0,8.0,41.97416,-87.90732,32.89595,-97.03720
2018-06-01 00:00:00,DL,2002.0,ATL,LGA,2018-06-01 09:00:00,2018-06-01 08:55:00,-5.0,12.0,2018-06-01 09:07:00,2018-06-01 10:57:00,6.0,2018-06-01 11:15:00,2018-06-01 11:03:00,-12.0,135.0,128.0,110.0,1.0,6,1,5,15,30,22.0,0.0,5.0,21.0,0.0,7.0,33.64044,-84.42694,40.77724,-73.87261
2018-06-01 00:00:00,UA,3003.0,SFO,DEN,2018-06-01 10:00:00,2018-06-01 10:25:00,25.0,18.0,2018-06-01 10:43:00,2018-06-01 13:43:00,7.0,2018-06-01 13:30:00,2018-06-01 13:50:00,20.0,150.0,145.0,120.0,1.0,6,1,5,40,50,18.0,0.0,12.0,24.0,0.0,9.0,37.61900,-122.37484,39.85841,-104.66700
2018-06-01 00:00:00,WN,4004.0,12A,LAX,2018-06-01 11:00:00,2018-06-01 11:10:00,10.0,14.0,2018-06-01 11:24:00,2018-06-01 12:44:00,6.0,2018-06-01 12:30:00,2018-06-01 12:50:00,20.0,90.0,100.0,80.0,1.0,6,1,5,60,70,25.0,0.0,10.0,22.0,0.0,6.0,35.00000,-115.00000,33.94254,-118.40807
2018-06-01 00:00:00,WN,5005.0,BWI,MCO,MALFORMED_TRUNCATED_RECORD
```

### 4.2. Phân loại 3 Trạng thái Hạch toán (Row Accounting Classification)
- **Dòng 2 (Row 1):** `ACCEPTED` — Đầy đủ 34 trường, đúng kiểu số, thỏa mãn đẳng thức số học ($15 + 120 + 5 = 140.0$).
- **Dòng 3 (Row 2):** `ACCEPTED` — Đầy đủ 34 trường, đúng kiểu số, đến sớm $-12.0$m, thỏa mãn đẳng thức ($12 + 110 + 6 = 128.0$).
- **Dòng 4 (Row 3):** `ACCEPTED` — Đầy đủ 34 trường, đúng kiểu số, trễ đến $20.0$m ($\ge 15.0$), thỏa mãn đẳng thức ($18 + 120 + 7 = 145.0$).
- **Dòng 5 (Row 4):** `QUARANTINED` — Parse được đúng 34 trường hợp lệ cú pháp CSV, nhưng trường `ORIGIN = "12A"` vi phạm quy tắc cú pháp mã sân bay IATA 3 chữ cái viết hoa (`^[A-Z]{3}$` theo DC-05). Mã lý do: `INVALID_IATA_AIRPORT_SYNTAX:ORIGIN_NOT_3_ALPHA`.
- **Dòng 6 (Row 5):** `REJECTED` — Bản ghi thiếu số lượng cột bắt buộc (chỉ có 6 trường thay vì 34 trường; lỗi cấu trúc cột không khớp schema, phân biệt với lỗi parser syntax). Mã lý do chuẩn hóa: `COLUMN_COUNT_MISMATCH: EXPECTED_34_FOUND_6`.

### 4.3. Kết quả Hạch toán & Kết quả Kỳ vọng trên Tập Hợp lệ
1. **Kiểm chứng Bất biến DC-11:**
   $$\text{raw\_row\_count (5)} = \text{accepted (3)} + \text{quarantined (1)} + \text{rejected (1)} \quad (\text{PASS})$$
   $$\text{ingest\_acceptance\_rate} = 3 / 5 = 60.0\%$$
2. **Giá trị KPI Tính Độc lập trên Thuần tập 3 Bản ghi Accepted:**
   - `KPI-01` (Total Records): $3$ bản ghi (`count_records = 3`, `count_metric_valid = 3`).
   - `KPI-02` (Arrival Late Rate $\ge 15$m): $1 / 3 \approx 33.3333\%$ (Row 3 có `ARR_DELAY = 20.0`).
   - `KPI-03` (Mean Arrival Delay Signed): $(0.0 - 12.0 + 20.0) / 3 = 8.0 / 3 \approx 2.6667$ phút.
   - `KPI-04` (Departure Late Rate $\ge 15$m): $1 / 3 \approx 33.3333\%$ (Row 3 có `DEP_DELAY = 25.0`).
   - `KPI-05` (Mean Departure Delay Signed): $(5.0 - 5.0 + 25.0) / 3 = 25.0 / 3 \approx 8.3333$ phút.
   - `KPI-06-P50`: Trung vị của `[-12.0, 0.0, 20.0]` là $0.0$ phút.
   - `KPI-06-P90`: Nội suy liên tục: $16.0$ phút; Phân vị rời rạc: $20.0$ phút.
   - `KPI-07-TAXI_OUT`: $(15.0 + 12.0 + 18.0) / 3 = 15.0$ phút.
   - `KPI-07-TAXI_IN`: $(5.0 + 6.0 + 7.0) / 3 = 6.0$ phút.
   - `KPI-08-AIR_TIME`: $(120.0 + 110.0 + 120.0) / 3 = 350.0 / 3 \approx 116.6667$ phút.
   - `KPI-08-ACTUAL_ELAPSED_TIME`: $(140.0 + 128.0 + 145.0) / 3 = 413.0 / 3 \approx 137.6667$ phút.
   - `KPI-08-CRS_ELAPSED_TIME`: $(145.0 + 135.0 + 150.0) / 3 = 430.0 / 3 \approx 143.3333$ phút.

---

## 5. Ma trận Đối chiếu Toàn diện với TEST_PLAN v1.1

| Test ID trong TEST_PLAN | Giai đoạn Thực thi | Mục tiêu Kiểm thử Được Bao phủ bởi Fixtures | Mã Fixture Trực tiếp |
|:---:|:---:|---|:---:|
| **TS-002** | G4 / G5 | Parse kiểu dữ liệu số, xử lý null, NaN, Inf, bảo toàn domain | `FIX-07`, `FIX-10` |
| **TS-003** | G4 / G5 / G6 | Hạch toán 3 trạng thái `raw = accepted + quarantined + rejected` độc lập | `FIX-08`, `FIX-09`, **`FIX-14`** |
| **TS-005** | G2 design / G5 run | Ngưỡng `ARR_DELAY`, eligibility, mẫu số 0, kiểm thử biên $14.999/15.0/15.001$ | `FIX-01`, `FIX-02`, `FIX-03`, `FIX-04`, `FIX-05`, `FIX-07`, `FIX-08`, `FIX-09` |
| **TS-006** | G2 design / G5 run | Signed delay mean (không clip âm), finite domain, submetric nulls độc lập | `FIX-01`, `FIX-02`, `FIX-06`, `FIX-10` |
| **TS-008** | G2 design / G5 run | Phân vị P50/P90, extreme delay, ngưỡng min-N, mẫu số submetric riêng | `FIX-06`, `FIX-10`, `FIX-11`, `FIX-12` |
| **TS-009** | G2 design / G5 / G7 | Bảo vệ `FLIGHTS` (không sum), rào chắn cờ thời tiết optional | Rào chắn ngữ nghĩa `FLIGHTS` |
| **TS-017** | G4 / G5 | Từ vựng hạch toán, mẫu số thuần tập, xử lý mẫu số 0 | `FIX-07`, `FIX-08`, `FIX-09`, **`FIX-14`** |
| **TS-018** | G2 document gate | Kiểm chứng đơn vị đo 7 trường từ quy định chính thức và thực nghiệm | `FIX-01` đến `FIX-07`, `FIX-10` |
| **TS-020** | G4 / G6 | Stable lineage / row identifier trên các phân vùng Spark lặp lại | `FIX-13` |
| **TS-021** *(Proposed)* | G2 design / G4 / G5 | **Duplicate-Preservation & Event-Identity Guard**: Bảo vệ không xóa bản ghi trùng candidate key | **`FIX-13`** |

---

## 6. Kết luận Nghiệm thu B6 sau Vòng R1

- Toàn bộ 14 ca kiểm thử tổng hợp bảo vệ cho 8 CORE KPIs đã được đặc tả hoàn chỉnh và sửa đổi triệt để các sai khác:
  1. `FIX-13` đã phục hồi dữ liệu thô nguyên bản của ca YX 3624 (ngày `2018-06-21`, taxi `91.0/7.0` và `13.0/6.0`), loại bỏ dữ liệu giả mạo.
  2. `FIX-08` phân định đúng `KPI-01 = 0` (phép đếm) và `KPI-02..08 = null` (phép chia mẫu số 0).
  3. `FIX-11` tuân thủ nghiêm ngặt ngưỡng min-N: $N=20$ và $N=500$ đều bị `SUPPRESSED`, $N=1500$ mang cờ `LOW_SAMPLE_CAUTION`.
  4. `FIX-12` phân định rõ phân vị liên tục vs phân vị xấp xỉ rời rạc.
  5. Đã bổ sung `FIX-14` kiểm chứng trọn vẹn bất biến hạch toán 3 trạng thái cho `TS-003`.
  6. Đề xuất mã kiểm thử chuyên biệt `TS-021` bảo vệ chống xóa bản ghi trùng lặp thay vì mở rộng sai phạm vi `TS-009`.
