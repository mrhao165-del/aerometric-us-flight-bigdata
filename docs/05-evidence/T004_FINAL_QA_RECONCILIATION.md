# T-004: BÁO CÁO ĐỐI CHIẾU CHẤT LƯỢNG NGUỒN VÀ NGHIỆM THU KỸ THUẬT CUỐI CÙNG
## (T-004 FINAL QA: SOURCE COUNT RECONCILIATION & TEMPORAL EVIDENCE SIGN-OFF)

- **Mã nhiệm vụ:** `T-004-FINAL-QA` (Source Count Reconciliation, Fixture Integrity & Temporal Evidence Sign-Off)
- **Gate kiểm soát:** `G2` (Data Quality, Cohort & Metric Contracts)
- **Ngày lập:** 2026-10-14
- **Vai trò:** Independent Data Quality Auditor & Technical Reviewer
- **Trạng thái nhiệm vụ:** **`READY_FOR_SIGNOFF_WITH_OPEN_DEFECT`**
- **Trạng thái Gate G2:** **`IN_PROGRESS / NOT_PASSED`** (Chờ hoàn thành Task T-005)
- **Văn bản tuân thủ:** [`AGENTS.md`](../../AGENTS.md), [`docs/01-planning/BACKLOG.md`](../01-planning/BACKLOG.md), [`docs/02-design/DATA_CONTRACT.md`](../02-design/DATA_CONTRACT.md), [`docs/02-design/DATA_DICTIONARY.md`](../02-design/DATA_DICTIONARY.md), [`docs/02-design/DECISIONS.md`](../02-design/DECISIONS.md), [`docs/02-design/KPI_SPEC.md`](../02-design/KPI_SPEC.md), [`docs/03-quality/TEST_PLAN.md`](../03-quality/TEST_PLAN.md) (`TS-004`, `TS-009`, `TS-010`), [`docs/03-quality/RISK_REGISTER.md`](../03-quality/RISK_REGISTER.md), [`docs/04-execution/PROJECT_STATE.md`](../04-execution/PROJECT_STATE.md).

---

## 1. Ma trận Xử lý Bốn Yêu cầu Kiểm toán Bắt buộc (QA-01 đến QA-04)

| Mã Yêu cầu | Tên Yêu cầu Kỹ thuật | Trọng tâm Đánh giá & Ranh giới Kiểm toán | Biện pháp Sửa đổi & Kết quả Đạt được | Đánh giá |
|:---:|---|---|---|:---:|
| **QA-01** | **Reconcile Annual Row Counts** | Bảng số dòng trong T004_R1 cũ sai lệch so với schema audit gốc (dù tổng vẫn đúng 54.67M). | - Đọc trực tiếp `row_count` từ 9 tệp `schema_YYYY.json` và đếm dòng vật lý trực tiếp trên 9 CSV thô.<br>- Sửa toàn bộ bảng 9 năm trong mọi tài liệu T-004 theo đúng dữ liệu nguồn.<br>- Bổ sung hàm kiểm tra tự động đối chiếu từng năm trong script QA. | **PASS** |
| **QA-02** | **Preserve Original YX 3624 Records** | Bản ghi B trong T004_R1 cũ bị sửa thành TAXI_OUT=20, AIR=77, TAXI_IN=5 thay vì 13, 83, 6. | - Khôi phục nguyên bản các trường của Bản ghi B: `TAXI_OUT = 13.0`, `AIR_TIME = 83.0`, `TAXI_IN = 6.0`, `ACTUAL = 102.0`.<br>- Khẳng định phân định 3 cấp độ: `VERIFIED`, `INFERRED`, `UNKNOWN`.<br>- Không tự ý deduplicate; khóa phân loại `PHYSICAL_ENTITY_IDENTITY_UNKNOWN`. | **PASS** |
| **QA-03** | **Fixture & Timezone Contract** | Phân định schema 18 cột vs 34 cột; chuẩn hóa múi giờ lịch sử theo IANA ZoneInfo & DST. | - Ban hành 2 tệp CSV riêng: `T004_TF09_temporal_fixture.csv` (18 cột — `TEMPORAL_TEST_PROJECTION`) và `T004_TF09_full_schema_fixture.csv` (34 cột — `FULL_SCHEMA_INGESTION_FIXTURE`).<br>- Chuẩn hóa múi giờ theo IANA (`America/Chicago`, `America/New_York`, `America/Los_Angeles`, `America/Phoenix`, `America/Denver`, `America/Anchorage`) và phân biệt rõ DST (CDT/EDT/PDT/MDT) vào mùa hè vs Standard Time (PST/MST/AKST) vào mùa đông.<br>- Giữ nguyên hai bất biến số học trên cả 9 fixtures; giữ TF-08 làm counterexample. | **PASS** |
| **QA-04** | **Reproducible QA and Evidence Boundaries** | Xung đột số lượng assertion (32 vs 59); ranh giới kiểm tra working-tree; rủi ro OR-05. | - Đồng bộ số lượng assertion thực tế trong log kiểm thử.<br>- Mô tả chính xác phạm vi kiểm tra của `check_working_tree_consistency.py` (cấu trúc tài liệu, hash manifest, phân loại tệp).<br>- Giữ trạng thái `CONTENT_INTEGRITY_NOT_PROVEN` cho raw CSV do thiếu SHA-256 baseline.<br>- Giữ `OR-05` là `OPEN_QUALITY_DEFECT` và Gate G2 là `IN_PROGRESS / NOT_PASSED`. | **PASS** |

---

## 2. Bảng Đối chiếu Số dòng Chín Năm với Nguồn Dữ liệu Thẩm quyền (QA-01)

### 2.1. Nguồn Dữ liệu Đối chiếu Độc lập
1. **Nguồn Metadata Thẩm quyền Lịch sử:** Đọc trực tiếp trường `row_count` trong từng tệp [`schema_YYYY.json`](inputs/schema_2016.json) tại `docs/05-evidence/inputs/`.
2. **Nguồn Dữ liệu Thô Thực tế trên Ổ đĩa:** Đếm số dòng vật lý thực tế bằng script đọc byte nhị phân Python trên từng tệp `data/raw/tabular/<YYYY>/flight_with_weather_<YYYY>.csv` (nhiệm vụ nền `task-1110`).

### 2.2. Bảng Đối chiếu Từng Năm (2016–2024)

| Năm | Đường dẫn Tệp Raw CSV | Số Dòng Vật lý (Physical Lines) | Header Lines | Số Dòng Dữ liệu Thực tế (Data Rows) | `row_count` trong `schema_YYYY.json` | Khớp Tuyệt đối? | Đánh giá Trạng thái Dữ liệu |
|:---:|---|:---:|:---:|:---:|:---:|:---:|:---:|
| **2016** | `data/raw/tabular/2016/flight_with_weather_2016.csv` | $5,537,988$ | $1$ | **$5,537,987$** | **$5,537,987$** | **KHỚP 100%** | **FULL_YEAR (366 days)** |
| **2017** | `data/raw/tabular/2017/flight_with_weather_2017.csv` | $5,575,873$ | $1$ | **$5,575,872$** | **$5,575,872$** | **KHỚP 100%** | **FULL_YEAR (365 days)** |
| **2018** | `data/raw/tabular/2018/flight_with_weather_2018.csv` | $6,986,843$ | $1$ | **$6,986,842$** | **$6,986,842$** | **KHỚP 100%** | **FULL_YEAR (365 days)** |
| **2019** | `data/raw/tabular/2019/flight_with_weather_2019.csv` | $7,161,828$ | $1$ | **$7,161,827$** | **$7,161,827$** | **KHỚP 100%** | **FULL_YEAR (365 days)** |
| **2020** | `data/raw/tabular/2020/flight_with_weather_2020.csv` | $4,312,092$ | $1$ | **$4,312,091$** | **$4,312,091$** | **KHỚP 100%** | **FULL_YEAR (366 days)** |
| **2021** | `data/raw/tabular/2021/flight_with_weather_2021.csv` | $5,755,667$ | $1$ | **$5,755,666$** | **$5,755,666$** | **KHỚP 100%** | **FULL_YEAR (365 days)** |
| **2022** | `data/raw/tabular/2022/flight_with_weather_2022.csv` | $6,413,417$ | $1$ | **$6,413,416$** | **$6,413,416$** | **KHỚP 100%** | **FULL_YEAR (365 days)** |
| **2023** | `data/raw/tabular/2023/flight_with_weather_2023.csv` | $6,645,462$ | $1$ | **$6,645,461$** | **$6,645,461$** | **KHỚP 100%** | **FULL_YEAR (365 days)** |
| **2024** | `data/raw/tabular/2024/flight_with_weather_2024.csv` | $6,284,842$ | $1$ | **$6,284,841$** | **$6,284,841$** | **KHỚP 100%** | **PARTIAL_YEAR (335 days, Missing March)** |
| **TỔNG** | **9 tệp CSV thô** | **$54,674,012$** | **$9$** | **$54,674,003$** | **$54,674,003$** | **KHỚP 100%** | **MATCHED_ALL_YEARS** |

> **Nguyên nhân sai lệch cũ:** Bảng số dòng cũ trong bản nháp T004_R1 phát sinh do lỗi sao chép nhầm phân bổ dòng trung gian, tuy nhiên tổng số dòng vẫn bằng 54,674,003. Việc năm 2018 có đúng **$6,986,842$ bản ghi** hoàn toàn tương thích và chứng thực cho sự tồn tại của cặp bản ghi YX 3624 tại dòng vật lý **6,384,132** và **6,384,133** ($6,384,133 < 6,986,843$).
> Bảng trên đã được đồng bộ hóa và khóa bất biến vào toàn bộ tài liệu kiểm chuẩn.

---

## 3. Bảng So sánh và Bảo tồn Nguyên bản Bản ghi YX 3624 (QA-02)

Đối chiếu trực tiếp giữa các tài liệu kiểm toán [`T002_DUPLICATE_ANALYSIS.md`](T002_DUPLICATE_ANALYSIS.md), [`T004_OVERNIGHT_COUNTEREXAMPLES.md`](T004_OVERNIGHT_COUNTEREXAMPLES.md) và hai dòng vật lý trong `data/raw/tabular/2018/flight_with_weather_2018.csv`:

| Thuộc tính | Bản ghi A (Dòng vật lý 6,384,132) | Bản ghi B Thực tế trong Raw CSV (Dòng vật lý 6,384,133) | Giá trị Sai sót trong Draft R1 Cũ | Trạng thái Hiệu chỉnh & Bằng chứng Khôi phục |
|---|:---:|:---:|:---:|---|
| `FL_DATE` | `2018-06-21 00:00:00` | `2018-06-21 00:00:00` | `2018-06-21 00:00:00` | Khớp $100\%$ |
| `OP_CARRIER` / `FL_NUM` | `YX` / `3624.0` | `YX` / `3624.0` | `YX` / `3624.0` | Khớp $100\%$ |
| `ORIGIN` $\to$ `DEST` | `DEN` $\to$ `XNA` | `DEN` $\to$ `XNA` | `DEN` $\to$ `XNA` | Khớp $100\%$ |
| `CRS_DEP_TIME` | `2018-06-21 20:07:00` | `2018-06-21 20:07:00` | `2018-06-21 20:07:00` | Khớp $100\%$ |
| `CRS_ARR_TIME` | `2018-06-21 23:05:00` | `2018-06-21 23:05:00` | `2018-06-21 23:05:00` | Khớp $100\%$ |
| `DEP_TIME` | `2018-06-21 10:44:00` | `2018-06-21 20:27:00` | `2018-06-21 20:27:00` | Khớp $100\%$ |
| `DEP_DELAY` | **`+877.0`** | **`+20.0`** | `+20.0` | Khớp $100\%$ |
| `ARR_TIME` | `2018-06-21 14:46:00` | `2018-06-21 23:09:00` | `2018-06-21 23:09:00` | Khớp $100\%$ |
| `ARR_DELAY` | **`+941.0`** | **`+4.0`** | `+4.0` | Khớp $100\%$ |
| **`TAXI_OUT`** | **`91.0`** | **`13.0`** | `20.0` (SAI) | **ĐÃ KHÔI PHỤC: `13.0`** |
| **`AIR_TIME`** | **`84.0`** | **`83.0`** | `77.0` (SAI) | **ĐÃ KHÔI PHỤC: `83.0`** |
| **`TAXI_IN`** | **`7.0`** | **`6.0`** | `5.0` (SAI) | **ĐÃ KHÔI PHỤC: `6.0`** |
| `CRS_ELAPSED_TIME` | `118.0` | `118.0` | `118.0` | Khớp $100\%$ |
| `ACTUAL_ELAPSED_TIME` | `182.0` | `102.0` | `102.0` | $13.0 + 83.0 + 6.0 = \mathbf{102.0}$ |
| **Kiểm tra Phân rã** | $91 + 84 + 7 = 182.0$ | $13 + 83 + 6 = 102.0$ | $20 + 77 + 5 = 102.0$ | Khôi phục chính xác số liệu thô |
| **Cân bằng Độ trễ** | $877 + (182 - 118) = 941$ | $20 + (102 - 118) = 4$ | $20 + (102 - 118) = 4$ | Cả hai bản ghi đều thỏa mãn cân bằng |

### Phân định Ranh giới Bằng chứng (Section 2.3 Boundary):
1. **`VERIFIED`:** Bản ghi A trễ 877 phút cất cánh 10:44, đến trễ 941 phút lúc 14:46; Bản ghi B trễ 20 phút cất cánh 20:27, đến trễ 4 phút lúc 23:09. Cả hai bản ghi đều thỏa mãn tuyệt đối đẳng thức phân rã thời gian và đẳng thức cân bằng trễ.
2. **`INFERRED`:** Bản ghi A là chuyến bay bị hoãn sâu sang sáng hôm sau (ngày 22/06/2018), quy trình upstream đã kẹp cứng ngày lịch trình `2018-06-21` vào chuỗi giờ thực tế.
3. **`UNKNOWN`:** Do thiếu `TAIL_NUM`, phân loại chính xác là **`PHYSICAL_ENTITY_IDENTITY_UNKNOWN`** (không biết cùng hay khác máy bay vật lý) và **`UPSTREAM_CODE_UNKNOWN`** (không biết logic ETL của bên thứ ba). **CẤM DEDUPLICATE TÙY TIỆN**.

---

## 4. Kết quả Kiểm tra 9 Fixtures & Phân định Schema (QA-03)

### 4.1. Phân định Hai Định dạng Fixture CSV:
1. **`T004_TF09_temporal_fixture.csv` (18 cột — `TEMPORAL_TEST_PROJECTION`):**
   - Header: `fixture_id,case_description,expected_classification,FL_DATE,CRS_DEP_TIME,DEP_TIME,CRS_ARR_TIME,ARR_TIME,DEP_DELAY,ARR_DELAY,TAXI_OUT,TAXI_IN,CRS_ELAPSED_TIME,ACTUAL_ELAPSED_TIME,AIR_TIME,ORIGIN,DEST,notes`
   - Số dòng vật lý: Đúng **10 dòng** (1 header + 9 data rows). Không có comment `#`.
   - Mục đích: Kiểm thử độc lập các hàm xử lý thời gian, trích xuất giờ `CRS_DEP_HOUR`, và các ma trận phân loại an toàn.
2. **`T004_TF09_full_schema_fixture.csv` (34 cột — `FULL_SCHEMA_INGESTION_FIXTURE`):**
   - Header: Đúng đầy đủ 34 cột raw CSV chuẩn.
   - Số dòng vật lý: Đúng **10 dòng** (1 header + 9 data rows). Không có comment `#`.
   - Mục đích: Kiểm thử toàn diện đường ống nạp dữ liệu (*ingestion pipeline test*) trên Apache Spark.

### 4.2. Kiểm chứng Hai Bất biến Số học trên Cả 9 Fixtures:

| Mã Fixture | Tuyến bay | Invariant 1: Cân bằng Độ trễ ($\text{ARR} \equiv \text{DEP} + [\text{ACT} - \text{CRS}]$) | Invariant 2: Phân rã Thời lượng ($\text{ACT} \equiv \text{TAXI\_OUT} + \text{AIR} + \text{TAXI\_IN}$) | Kết quả Đánh giá |
|:---:|---|---|---|:---:|
| **`TF-01`** | ORD $\to$ DFW | $0.0 \equiv 5.0 + (140.0 - 145.0) = 0.0$ | $140.0 \equiv 15.0 + 120.0 + 5.0 = 140.0$ | **PASS** |
| **`TF-02`** | LAX $\to$ JFK | $0.0 \equiv 2.0 + (313.0 - 315.0) = 0.0$ | $313.0 \equiv 18.0 + 285.0 + 10.0 = 313.0$ | **PASS** |
| **`TF-03`** | ATL $\to$ LGA | $270.0 \equiv 270.0 + (150.0 - 150.0) = 270.0$ | $150.0 \equiv 20.0 + 120.0 + 10.0 = 150.0$ | **PASS** |
| **`TF-04`** | BWI $\to$ MCO | $-5.0 \equiv -5.0 + (140.0 - 140.0) = -5.0$ | $140.0 \equiv 12.0 + 120.0 + 8.0 = 140.0$ | **PASS** |
| **`TF-05`** | BOS $\to$ FLL | $0.0 \equiv 2.0 + (203.0 - 205.0) = 0.0$ | $203.0 \equiv 15.0 + 180.0 + 8.0 = 203.0$ | **PASS** |
| **`TF-06`** | LAS $\to$ PHX | $-2.0 \equiv -2.0 + (80.0 - 80.0) = -2.0$ | $80.0 \equiv 14.0 + 60.0 + 6.0 = 80.0$ | **PASS** |
| **`TF-07`** | SEA $\to$ ANC | $0.0 \equiv 5.0 + (205.0 - 210.0) = 0.0$ | $205.0 \equiv 16.0 + 180.0 + 9.0 = 205.0$ | **PASS** |
| **`TF-08`** | DEN $\to$ XNA | $941.0 \equiv 877.0 + (182.0 - 118.0) = 941.0$ | $182.0 \equiv 91.0 + 84.0 + 7.0 = 182.0$ | **PASS** |
| **`TF-09`** | SFO $\to$ BOS | $0.0 \equiv 0.0 + (330.0 - 330.0) = 0.0$ | $330.0 \equiv 20.0 + 300.0 + 10.0 = 330.0$ | **PASS** |

---

## 5. Metadata Múi giờ Đã Chuẩn hóa theo IANA & Trạng thái DST Lịch sử (QA-03)

Toàn bộ các nhãn múi giờ đã được kiểm chứng bằng thư viện chuẩn `zoneinfo` theo đúng ngày lịch trình của chuyến bay:

| Mã Fixture | Ngày Chuyến bay | Sân bay Đi $\to$ Đến | IANA Origin TZ | IANA Dest TZ | Múi giờ Lịch sử Đi | Múi giờ Lịch sử Đến | Trạng thái DST | Độ lệch Múi giờ ($\Delta\text{TZ}$) |
|:---:|:---:|:---:|---|---|:---:|:---:|:---:|:---:|
| **`TF-01`** | 2018-06-01 | ORD $\to$ DFW | `America/Chicago` | `America/Chicago` | **CDT (UTC-5)** | **CDT (UTC-5)** | Đang áp dụng DST | **$0$h** |
| **`TF-02`** | 2018-06-01 | LAX $\to$ JFK | `America/Los_Angeles` | `America/New_York` | **PDT (UTC-7)** | **EDT (UTC-4)** | Đang áp dụng DST | **$+3$h** |
| **`TF-03`** | 2018-06-01 | ATL $\to$ LGA | `America/New_York` | `America/New_York` | **EDT (UTC-4)** | **EDT (UTC-4)** | Đang áp dụng DST | **$0$h** |
| **`TF-04`** | 2018-06-01 | BWI $\to$ MCO | `America/New_York` | `America/New_York` | **EDT (UTC-4)** | **EDT (UTC-4)** | Đang áp dụng DST | **$0$h** |
| **`TF-05`** | 2018-06-01 | BOS $\to$ FLL | `America/New_York` | `America/New_York` | **EDT (UTC-4)** | **EDT (UTC-4)** | Đang áp dụng DST | **$0$h** |
| **`TF-06`** | 2024-02-29 | LAS $\to$ PHX | `America/Los_Angeles` | `America/Phoenix` | **PST (UTC-8)** | **MST (UTC-7)** | Giờ Tiêu chuẩn (Không DST) | **$+1$h** |
| **`TF-07`** | 2023-12-31 | SEA $\to$ ANC | `America/Los_Angeles` | `America/Anchorage` | **PST (UTC-8)** | **AKST (UTC-9)** | Giờ Tiêu chuẩn (Không DST) | **$-1$h** |
| **`TF-08`** | 2018-06-21 | DEN $\to$ XNA | `America/Denver` | `America/Chicago` | **MDT (UTC-6)** | **CDT (UTC-5)** | Đang áp dụng DST | **$+1$h** |
| **`TF-09`** | 2018-06-01 | SFO $\to$ BOS | `America/Los_Angeles` | `America/New_York` | **PDT (UTC-7)** | **EDT (UTC-4)** | Đang áp dụng DST | **$+3$h** |

*Ghi chú quan trọng về TF-08:* Bản ghi TF-08 (YX 3624) được giữ nguyên vẹn chuỗi thời gian địa phương (`CRS_DEP_TIME = 20:07`, `DEP_TIME = 10:44`) gắn với `FL_DATE = 2018-06-21` như một **counterexample** kinh điển chứng minh sự thất bại của phép trừ timestamp trực tiếp. Không tự ý sửa đổi chuỗi timestamp sang ngày 22/06 để bảo đảm tính trung thực của dữ liệu nguồn.

---

## 6. Kết quả Kiểm tra Script & Log Thực thi Tự động (QA-04)

### 6.1. Chi tiết Script Kiểm tra Thời gian và Hợp đồng Kỹ thuật:
- **Tệp script:** [`tools/qa/verify_t004_time_representation.py`](../../tools/qa/verify_t004_time_representation.py)
- **Lệnh thực thi:** `python tools/qa/verify_t004_time_representation.py`
- **Mã thoát (Exit Code):** `0`
- **Kết quả Assertion:** **`61 PASS, 0 FAIL`**
- **Nội dung kiểm tra:**
  1. Kiểm tra sự tồn tại và tính không rỗng của 11 artifact kiểm chuẩn.
  2. Đối chiếu từng năm của 9 tệp `schema_YYYY.json` với số liệu thẩm quyền (9 PASS).
  3. Kiểm tra tổng số dòng schema bằng $54,674,003$.
  4. Kiểm tra sự hiện diện của số dòng từng năm trong bảng của `T004_R1_INDEPENDENT_RECONCILIATION.md` (9 PASS).
  5. Kiểm tra giá trị thực tế của cặp bản ghi YX 3624 (13.0, 83.0, 6.0, 102.0) và phân định 3 cấp độ Section 2.3.
  6. Kiểm tra cấu trúc 10 dòng, không comment `#`, và đúng 18 cột của `T004_TF09_temporal_fixture.csv`.
  7. Kiểm tra cấu trúc 10 dòng, không comment `#`, và đúng 34 cột của `T004_TF09_full_schema_fixture.csv`.
  8. Kiểm tra tính hợp lệ của JSON oracle và hai bất biến số học trên cả 9 fixtures.
  9. Kiểm tra định danh múi giờ chuẩn IANA và cờ DST lịch sử.
  10. Kiểm tra danh mục rủi ro chuẩn `OR-01`..`OR-08` trong `RISK_REGISTER.md`.
  11. Kiểm tra trạng thái Gate G2 `IN_PROGRESS / NOT_PASSED` và rủi ro `OR-05: OPEN_QUALITY_DEFECT`.

### 6.2. Chi tiết Script Kiểm tra Tính Nhất quán Repository:
- **Tệp script:** [`tools/check_working_tree_consistency.py`](../../tools/check_working_tree_consistency.py)
- **Lệnh thực thi:** `python tools/check_working_tree_consistency.py`
- **Mã thoát (Exit Code):** `0`
- **Kết quả Assertion:** **`88 PASS, 0 FAIL`**
- **Ranh giới Kiểm tra Cần Ghi nhận Rõ ràng:**
  - `check_working_tree_consistency.py` kiểm tra:
    + Cấu trúc 18 tài liệu A/B/C + 8 tài liệu bổ trợ.
    + Tính toàn vẹn của tất cả các liên kết markdown và đường dẫn tương đối.
    + Không có từ khóa lỗi thời (cũ: HANDOFF, khóa 5 KPI...).
    + Khế ước dữ liệu, thứ tự 12 KPI, tính chu trình DAG của nhiệm vụ.
    + Tính bất biến của `SOURCE_MANIFEST.json` và `PACKAGE_MANIFEST.json` v1.1.
    + Phân loại tệp: Đúng 9 tệp raw CSV (kiểm tra đường dẫn/tên tệp), các deliverable hợp lệ thuộc `T001_`..`T004_`, và không có tệp thừa.
  - **Giới hạn Bằng chứng:** Việc script xác nhận `len(raw_data_files) == 9` **KHÔNG CHỨNG MINH NỘI DUNG RAW CSV ĐÃ ĐƯỢC XÁC MINH HASH** (vì kho dữ liệu chưa có SHA-256 baseline từ BTS gốc). Rủi ro này tiếp tục được ghi nhận chính xác là **`CONTENT_INTEGRITY_NOT_PROVEN / METADATA_MATCH_ONLY`** (`OR-08`).

---

## 7. Danh sách File Thay đổi & Tổng hợp Thay đổi (File Changes Summary)

1. **`docs/05-evidence/T004_FINAL_QA_RECONCILIATION.md` (Tạo mới):** Báo cáo đối chiếu và nghiệm thu kỹ thuật cuối cùng cho T-004.
2. **`docs/05-evidence/T004_TF09_full_schema_fixture.csv` (Tạo mới):** Tệp fixture thực thi chuẩn đầy đủ 34 cột cho nạp dữ liệu Spark (10 dòng, 0 comment `#`).
3. **`docs/05-evidence/T004_TF09_temporal_fixture.json` (Cập nhật):** Bổ sung định danh IANA (`America/...`), cờ DST, và ghi chú phân định projection 18 cột vs 34 cột.
4. **`docs/05-evidence/T004_TEST_FIXTURE_SPEC.md` (Cập nhật):** Bổ sung phân định rõ ràng giữa tệp projection 18 cột và tệp full schema 34 cột; chuẩn hóa bảng múi giờ IANA.
5. **`docs/05-evidence/T004_R1_INDEPENDENT_RECONCILIATION.md` (Cập nhật):**
   - Khôi phục nguyên bản các trường của Bản ghi B YX 3624 (`TAXI_OUT = 13.0`, `AIR = 83.0`, `TAXI_IN = 6.0`).
   - Sửa bảng Section 9 theo đúng số dòng thẩm quyền của 9 năm (2016: 5,537,987 ... 2024: 6,284,841).
   - Bổ sung tham chiếu tới tệp `T004_TF09_full_schema_fixture.csv`.
   - Cập nhật số lượng assertion trong Section 12.
6. **`tools/qa/verify_t004_time_representation.py` (Cập nhật):** Mở rộng kiểm tra toàn diện QA-01..QA-04 (61 assertions PASS).
7. **`docs/04-execution/PROJECT_STATE.md` (Cập nhật):** Bổ sung liên kết tới `T004_FINAL_QA_RECONCILIATION.md` và `T004_TF09_full_schema_fixture.csv`.

---

## 8. Các Rủi ro Chưa Giải quyết (Unresolved Risks Progression)

1. **`OR-01` (Cột FLIGHTS bằng 1.0 cố định):** Đã khóa thiết kế ngoài KPI; chờ chuyển G4 kiểm thử Spark (`TS-009`).
2. **`OR-02` (Deduplicate tùy tiện làm mất trễ cực đoan):** Đã lập counterexample YX 3624 và cấm dedup; bảo vệ bằng `TS-020`, `TS-021`.
3. **`OR-03` (Đơn vị 7 trường độ trễ/thời lượng giữ nhãn PROVISIONAL):** Bảo lưu rủi ro; chờ đối chiếu nguồn BTS On-Time tại G5.
4. **`OR-04` (Thiếu CANCELLED & DIVERTED):** Đã đóng phạm vi ngoài 8 CORE KPIs.
5. **`OR-05` (Tính liên tục năm 2024 khuyết thiếu Tháng 3 — 335/366 ngày):** Tiếp tục duy trì trạng thái **`OPEN_QUALITY_DEFECT`** (chưa đóng). Có 3 phương án xử lý chuyển giao cho G3/G4 (A: Bổ sung BTS, B: Gắn nhãn Partial Year, C: Common-month windowing).
6. **`OR-06` (Rollover mốc giờ thực tế ARR_TIME, DEP_TIME):** Đã giải tỏa triệt để bằng chính sách cấm trừ timestamp, cấm cộng 24h, và ban hành ma trận an toàn cùng bộ fixture `TS-010`.
7. **`OR-07` (Dữ liệu thời tiết thiếu trạm đo, mốc giờ và đơn vị):** Trạng thái `CONDITIONAL_PENDING`; **chuyển giao cho Task T-005**.
8. **`OR-08` (Chưa có baseline SHA-256 từ BTS gốc):** Trạng thái `METADATA_MATCH_ONLY / CONTENT_INTEGRITY_NOT_PROVEN`; chuyển giao T-007 (G4).

---

## 9. Bảng Đối chiếu Tiêu chí Nghiệm thu BACKLOG T-004

- **Tiêu chí trong BACKLOG v1.1:**
  > *"Safe-time representation audit, canonical schedule datetime, 2024 boundary, overnight/rollover counterexamples, safe fields decision, TS-010 specs"*

| Thành phần Tiêu chí | Bằng chứng Đối chiếu Hoàn tất | Đánh giá |
|---|---|:---:|
| *Safe-time representation audit* | Kiểm toán 100% định dạng `%Y-%m-%d %H:%M:%S` trên 54.67M dòng ([`T004_TIME_REPRESENTATION_AUDIT.md`](T004_TIME_REPRESENTATION_AUDIT.md)). | **ĐẠT (PASS)** |
| *Canonical schedule datetime* | Khẳng định `FL_DATE` là ngày dịch vụ, `CRS_DEP_TIME` trích xuất `CRS_DEP_HOUR` ([`T004_TIME_REPRESENTATION_AUDIT.md`](T004_TIME_REPRESENTATION_AUDIT.md)). | **ĐẠT (PASS)** |
| *2024 boundary* | Xác định 335 ngày, khuyết thiếu Tháng 3/2024, ngày nhuận 29/02 có 18,642 chuyến; OR-05 mở ([`T004_2024_DATE_COVERAGE_AUDIT.md`](T004_2024_DATE_COVERAGE_AUDIT.md)). | **ĐẠT (PASS)** |
| *Overnight/rollover counterexamples* | Khôi phục nguyên bản số liệu dòng 6,384,132 & 6,384,133 (YX 3624), phân định 3 cấp độ Section 2.3 ([`T004_OVERNIGHT_COUNTEREXAMPLES.md`](T004_OVERNIGHT_COUNTEREXAMPLES.md)). | **ĐẠT (PASS)** |
| *Safe fields decision* | Ban hành ma trận an toàn 4 cấp độ bao phủ 34 cột và ánh xạ chuẩn với 8 CORE KPIs ([`T004_SAFE_FIELDS_DECISION.md`](T004_SAFE_FIELDS_DECISION.md)). | **ĐẠT (PASS)** |
| *TS-010 specs* | Ban hành đầy đủ bộ 3 tệp fixture (`T004_TF09_temporal_fixture.csv`, `T004_TF09_full_schema_fixture.csv`, `T004_TF09_temporal_fixture.json`) ([`T004_TEST_FIXTURE_SPEC.md`](T004_TEST_FIXTURE_SPEC.md)). | **ĐẠT (PASS)** |

---

## 10. Kết luận Nghiệm thu & Cam kết Dừng lại Tuyệt đối

### Kết luận Nghiệm thu
Hồ sơ kiểm toán **Task T-004** đã giải quyết triệt để toàn bộ các mâu thuẫn kỹ thuật được reviewer chỉ ra trong QA-01 đến QA-04. Số liệu từng năm đã được đối chiếu khớp $100\%$ với schema audit và dữ liệu thô trên ổ đĩa. Dữ liệu phản ví dụ YX 3624 đã được khôi phục nguyên bản. Hai tệp fixture thực thi (18 cột và 34 cột) cùng metadata oracle đã hoàn thiện. Toàn bộ 61 phép kiểm tra QA tự động và 88 phép kiểm tra repository đều đạt PASS.

Do đó, Task T-004 đạt điều kiện nghiệm thu kỹ thuật ở trạng thái:
$$\mathbf{READY\_FOR\_SIGNOFF\_WITH\_OPEN\_DEFECT}$$
(với rủi ro mở chất lượng dữ liệu `OR-05` được bảo lưu chuyển giao cho Gate G3/G4).

### Cam kết Dừng lại Tuyệt đối
1. **DỪNG LẠI HOÀN TOÀN TẠI ĐÂY**, tuyệt đối không tự ý khởi động **Task T-005**.
2. **Gate G2 TIẾP TỤC DUY TRÌ TRẠNG THÁI `IN_PROGRESS / NOT_PASSED`** theo đúng quy định của `AGENTS.md`.
3. Không sửa đổi, can thiệp hay ghi đè vào 9 tệp dữ liệu thô tại `data/raw/tabular/`.
4. Không sửa đổi các tệp manifest phát hành bất biến.
