# T003_FINAL_ACCEPTANCE_RECONCILIATION — Hồ sơ Đối chiếu Nghiệm thu Cuối cùng và Kiểm chứng Độc lập

**Nhiệm vụ:** T-003 — Core KPI Lock & Unit Contract Audit (Vòng Đối chiếu Thẩm định Độc lập — Final Acceptance Reconciliation)  
**Dự án:** Phân tích hiệu suất chuyến bay Hoa Kỳ giai đoạn 2016–2024 (Big Data Descriptive Study, Apache Spark)  
**Phiên bản tài liệu:** docs-v1.1  
**Ngày thực hiện:** 2026-10-14  
**Vai trò:** Independent Technical Reviewer & Data Contract QA Engineer  
**Trạng thái đề xuất nhiệm vụ:** `READY_FOR_SIGNOFF` (Đã giải quyết 100% blocker A01–A06, kiểm chứng tự động đạt 87 PASS / 0 FAIL)  
**Trạng thái Gate G2:** `IN_PROGRESS / NOT_PASSED` (Bảo lưu nghiêm ngặt, chờ hoàn tất T-004 và T-005)  

---

## 1. Bối cảnh và Mục tiêu Thực hiện

Báo cáo nghiệm thu vòng trước của Task T-003 ([`T003_FINAL_CLOSEOUT_VERIFICATION.md`](T003_FINAL_CLOSEOUT_VERIFICATION.md)) đã phát sinh các lỗi kỹ thuật nghiêm trọng liên quan đến:
1. Sai lệch ánh xạ định danh 8 CORE KPIs so với văn bản gốc có thẩm quyền [`KPI_SPEC.md`](../02-design/KPI_SPEC.md) v1.1.
2. Số liệu mô tả bằng văn bản trong bảng tổng kết FIX-14 không khớp với tệp CSV thực thi ([`T003_FIX14_accounting_fixture.csv`](T003_FIX14_accounting_fixture.csv)) và tệp JSON ([`T003_FIX14_accounting_fixture.json`](T003_FIX14_accounting_fixture.json)).
3. Sai lệch truy vết kiểm thử giữa `TS-009`, `TS-010`, `TS-005` và đề xuất `TS-021` so với [`TEST_PLAN.md`](../03-quality/TEST_PLAN.md).
4. Cam kết quá mức về sai số tuyệt đối của thuật toán phân vị PySpark mà chưa chạy kiểm chứng trên cluster.
5. Chưa phân biệt rạch ròi giữa lỗi cấu trúc cột schema (column count mismatch) và lỗi cú pháp parser CSV.
6. Ngộ nhận kết quả 88 PASS của working-tree consistency checker là bằng chứng tính đúng của công thức KPI.

Nhiệm vụ này tiến hành đối chiếu độc lập, khắc phục toàn bộ các sai sót đã xác định, chuẩn hóa hồ sơ kỹ thuật và xây dựng công cụ kiểm chứng tự động chuyên dụng để ngăn ngừa tái diễn. Nhiệm vụ **KHÔNG** triển khai lại toàn bộ T-003 và **KHÔNG** bắt đầu Task T-004.

---

## 2. Ma trận Xử lý và Đối chiếu Chi tiết A01–A06

| Mã | Hạng mục Yêu cầu | Tồn tại Đã Phát hiện | Giải pháp và Hành động Kỹ thuật Đã Thực hiện | Trạng thái |
|---|---|---|---|:---:|
| **A01** | **Sai ánh xạ KPI (KPI Mapping Error)** | Báo cáo gán nhầm KPI-02 thành đúng giờ, KPI-03 thành trễ đến, KPI-04 thành trễ đến TB, KPI-05 thành P50 đến, KPI-06 thành chỉ P90 đến, KPI-07 thành trễ đi, KPI-08 thành trễ đi TB. | Khôi phục 100% định nghĩa chuẩn theo [`KPI_SPEC.md`](../02-design/KPI_SPEC.md) v1.1: KPI-01 (Accepted count), KPI-02 (ARR_DELAY $\ge 15$ rate), KPI-03 (Signed mean ARR_DELAY), KPI-04 (DEP_DELAY $\ge 15$ rate), KPI-05 (Signed mean DEP_DELAY), KPI-06 (P50 & P90 ARR_DELAY), KPI-07 (Mean TAXI_OUT & TAXI_IN), KPI-08 (Mean AIR, ACTUAL, CRS Elapsed). | **RESOLVED** |
| **A02** | **FIX-14 Báo cáo không khớp CSV/JSON** | Báo cáo mô tả số liệu ảo `ARR_DELAY = [5, 22, 16]` và `DEP_DELAY = [-2, 18, 0]`, tính toán các giá trị KPI sai lệch hoàn toàn với dữ liệu tệp CSV. | Đọc trực tiếp tệp CSV bằng `csv.reader`, xác nhận giá trị gốc: `ARR_DELAY = [0.0, -12.0, 20.0]`, `DEP_DELAY = [5.0, -5.0, 25.0]`. Tính toán lại toàn bộ 8 CORE KPIs bằng code Python độc lập, khớp chính xác 13 mục oracle trong JSON metadata. Sửa toàn bộ mô tả sai trong báo cáo. | **RESOLVED** |
| **A03** | **Sửa TEST_PLAN Traceability** | Báo cáo mô tả sai `TS-009` thành bài kiểm tra temporal boundary / midnight rollover và gán cho `FIX-04/05`. | Khôi phục định nghĩa gốc trong [`TEST_PLAN.md`](../03-quality/TEST_PLAN.md): `TS-009` là rào chắn `FLIGHTS` (không sum) và cờ thời tiết tùy chọn; `TS-010` là bài kiểm tra temporal boundary / 2400 semantics; `FIX-04/05` là fixture kiểm thử biên trễ 15 phút thuộc `TS-005`; `FIX-13` gắn với đề xuất `TS-021`. | **RESOLVED** |
| **A04** | **Sửa Điều kiện Percentile Gate G5** | Cam kết sai số tuyệt đối $\le 0.5$m hay $\le 1.0$m phổ quát chỉ dựa vào `accuracy=10000`; nhầm lẫn discrete vs continuous. | Bãi bỏ cam kết sai số tuyệt đối phổ quát. Phân định hệ quy chiếu đa tầng: (1) Continuous Type-7, (2) Exact Discrete, (3) Spark approximate, (4) Rank error $\le 0.01\%$, (5) Measured value error chỉ là kết quả quan sát trên dataset cụ thể. Kết quả Spark ở G2 giữ `PENDING_G5_VALIDATION`. Duy trì `FP-DEC-015` ở `PROPOSED`. | **RESOLVED** |
| **A05** | **Phân biệt Lỗi CSV và Lỗi Schema** | Dòng thứ 5 của FIX-14 bị gọi là "lỗi parser CSV syntax" gây hiểu nhầm. | Chuẩn hóa lý do: `COLUMN_COUNT_MISMATCH: EXPECTED_34_FOUND_6`. Phân tích rõ hành vi của ingestion parser (Spark `PERMISSIVE` vs `DROPMALFORMED` vs `FAILFAST`), yêu cầu kiểm tra số lượng cột trước/trong nạp. Trạng thái: `DESIGN_SPECIFIED`. | **RESOLVED** |
| **A06** | **Kiểm tra Quản trị và QA Tooling** | Ngộ nhận kết quả 88 PASS của working-tree checker là bằng chứng KPI tính đúng; nguy cơ tự duyệt ADR. | Khẳng định `check_working_tree_consistency.py` chỉ kiểm tra tính toàn vẹn tệp và manifest. Xây dựng công cụ kiểm toán độc lập `tools/qa/verify_t003_contract_consistency.py` để tính toán lại toàn bộ oracle số học. Bảo lưu `FP-DEC-015/016` và `TS-021` ở `PROPOSED`. Gate G2 giữ `IN_PROGRESS / NOT_PASSED`. | **RESOLVED** |

---

## 3. Chi tiết các Lỗi Đã Sửa và Vị trí Thay đổi trong Hồ sơ

### 3.1. Phục hồi Ánh xạ Chuẩn 8 CORE KPIs (A01)
Các sai lệch về mã định danh KPI đã được sửa đổi triệt để trên toàn bộ các tài liệu kỹ thuật:
- **`docs/05-evidence/T003_FINAL_CLOSEOUT_VERIFICATION.md`:**
  - Mục 5.1 (Bảng FIX-12): Chuyển Median từ `KPI-05` về đúng `KPI-06-P50`; chuyển P90 về đúng `KPI-06-P90`.
  - Mục 5.2 (Bảng FIX-14): Thay thế bảng ánh xạ sai bằng bảng chuẩn xác 100% theo [`KPI_SPEC.md`](../02-design/KPI_SPEC.md) v1.1.
  - Mục 3 (Item 4): Ghi nhận việc loại bỏ sự nhầm lẫn giữa tỷ lệ đúng giờ và tỷ lệ trễ đến.

### 3.2. Sửa Mô tả FIX-14 và Đối chiếu Khớp 100% với CSV/JSON (A02)
- **Tệp dữ liệu vật lý ([`T003_FIX14_accounting_fixture.csv`](T003_FIX14_accounting_fixture.csv)):**
  - Giữ nguyên bản 5 dòng dữ liệu vật lý đã tạo (không sửa vì dữ liệu đã đúng chuẩn 34 cột).
  - 3 dòng accepted có giá trị chính xác:
    - Line 2 (Row 1): `ARR_DELAY = 0.0`, `DEP_DELAY = 5.0`, `TAXI_OUT = 15.0`, `TAXI_IN = 5.0`, `AIR_TIME = 120.0`, `ACTUAL_ELAPSED = 140.0`, `CRS_ELAPSED = 145.0`.
    - Line 3 (Row 2): `ARR_DELAY = -12.0`, `DEP_DELAY = -5.0`, `TAXI_OUT = 12.0`, `TAXI_IN = 6.0`, `AIR_TIME = 110.0`, `ACTUAL_ELAPSED = 128.0`, `CRS_ELAPSED = 135.0`.
    - Line 4 (Row 3): `ARR_DELAY = 20.0`, `DEP_DELAY = 25.0`, `TAXI_OUT = 18.0`, `TAXI_IN = 7.0`, `AIR_TIME = 120.0`, `ACTUAL_ELAPSED = 145.0`, `CRS_ELAPSED = 150.0`.
- **Tệp metadata ([`T003_FIX14_accounting_fixture.json`](T003_FIX14_accounting_fixture.json)):**
  - Cập nhật dòng 45: Chuẩn hóa lý do phân loại hàng 5 thành `"reason": "COLUMN_COUNT_MISMATCH: EXPECTED_34_FOUND_6"`.
- **Báo cáo Closeout ([`T003_FINAL_CLOSEOUT_VERIFICATION.md`](T003_FINAL_CLOSEOUT_VERIFICATION.md)):**
  - Sửa lại toàn bộ mô tả văn bản trong Mục 5.2, xóa bỏ các số liệu ảo `[5, 22, 16]` và `[-2, 18, 0]`.

### 3.3. Sửa Truy vết TEST_PLAN (A03)
- **[`T003_FINAL_CLOSEOUT_VERIFICATION.md`](T003_FINAL_CLOSEOUT_VERIFICATION.md) (Mục 8):**
  - Khôi phục `TS-009`: Rào chắn bảo vệ `FLIGHTS` (không sum, không tự suy ra số chuyến bay hoàn thành khi chưa có grain vật lý) và cờ thời tiết tùy chọn.
  - Ghi nhận `TS-010`: Bài kiểm thử temporal boundary, timezone, overnight rollover và 2400 semantics thuộc phạm vi Task T-004.
  - Phân bổ `FIX-04` và `FIX-05` (kiểm thử biên trễ 15 phút) về đúng ca kiểm thử `TS-005` (ARR_DELAY threshold boundaries).
  - Gán `FIX-13` (bảo lưu cặp trùng YX 3624) cho đề xuất ca kiểm thử mới `TS-021` (`Duplicate-Preservation & Event-Identity Guard`).
- **[`T003_TEST_FIXTURE_SPEC.md`](T003_TEST_FIXTURE_SPEC.md):**
  - Cập nhật bảng tổng hợp Section 2 và ma trận Section 5 phản ánh đúng phân bổ test trên.

### 3.4. Chuẩn hóa Hợp đồng Phân vị và Điều kiện G5 (A04)
- **[`T003_PERCENTILE_AND_MIN_N_DECISIONS.md`](T003_PERCENTILE_AND_MIN_N_DECISIONS.md) (§1.3 & §1.4):**
  - Sửa mâu thuẫn số học FIX-12: Với $N=100$ phân bố đều từ $-10$ đến $89$, P90 liên tục Type 7 là $79.1$, PySpark discrete là $80.0 \implies |80.0 - 79.1| = 0.9$ phút (chặn bởi $\le 0.9$ phút so với mốc liên tục hoặc $\le 1.0$ đơn vị bước lưới; sai số so với discrete exact là $0.0$ phút).
  - Bổ sung cảnh báo phương pháp luận: Độ lệch $\le 0.9$ phút là kết quả đo lường quan sát (*measured value error*) trên tập dữ liệu cụ thể này, **không phải là cam kết sai số tuyệt đối $\le 1.0$ phút cho mọi dataset bất kỳ**.
  - Thiết lập hệ quy chiếu 5 thành phần (Continuous Type-7, Exact Discrete, Spark approx, Rank error $\le 0.01\%$, Measured value error).
  - Trạng thái Spark output ở G2 được ấn định là **`PENDING_G5_VALIDATION`**.
  - Quyết định kiến trúc `FP-DEC-015` tiếp tục duy trì ở trạng thái **`PROPOSED`**.

### 3.5. Chuẩn hóa Phân loại Lỗi Schema FIX-14 Hàng 5 (A05)
- **Chuẩn hóa nhãn mã lý do:**  
  `COLUMN_COUNT_MISMATCH: EXPECTED_34_FOUND_6`
- **Phân định kỹ thuật:**
  - Hàng thứ 5 trong FIX-14 (`2018-06-01 00:00:00,WN,5005.0,BWI,MCO,MALFORMED_TRUNCATED_RECORD`) là một dòng CSV có 6 trường phân tách dấu phẩy hợp lệ về mặt cú pháp ký tự, nhưng vi phạm quy cách số lượng cột bắt buộc (34 cột).
  - Phân biệt với lỗi parser syntax (như unclosed quotes, invalid escape character).
  - Trong thiết kế Ingestion (Task T-007 / T-008): Phải có cơ chế kiểm tra `field_count` trước khi map vào schema, hoặc cấu hình Spark CSV parser phù hợp (`DROPMALFORMED` / `PERMISSIVE` kèm kiểm tra cột `_corrupt_record`) để hạch toán chính xác bản ghi này vào phân loại `rejected`.
  - Trạng thái kiểm thử ở G2: **`DESIGN_SPECIFIED`** (chưa tuyên bố Spark production test PASS).

### 3.6. Quản trị và Công cụ Kiểm toán Tự động (A06)
- Đăng ký công cụ kiểm toán độc lập: [`tools/qa/verify_t003_contract_consistency.py`](../../tools/qa/verify_t003_contract_consistency.py).
- Cập nhật [`tools/check_working_tree_consistency.py`](../../tools/check_working_tree_consistency.py) để nhận diện hợp lệ thư mục `tools/qa/`.
- Xác nhận lại trạng thái:
  - `FP-DEC-015`: `PROPOSED`
  - `FP-DEC-016`: `PROPOSED`
  - `TS-021`: `PROPOSED`
  - `Gate G2`: `IN_PROGRESS / NOT_PASSED`

---

## 4. Bảng Số liệu KPI Đúng và Đối chiếu Độc lập trên FIX-14

Quá trình kiểm chứng tự động đã đọc trực tiếp tệp [`docs/05-evidence/T003_FIX14_accounting_fixture.csv`](T003_FIX14_accounting_fixture.csv) bằng thư viện chuẩn `csv.reader` của Python và tính toán lại toàn bộ 8 CORE KPIs độc lập trên thuần tập 3 bản ghi accepted:

$$\text{Tập dữ liệu trễ đến: } \text{ARR\_DELAY} = [0.0, -12.0, 20.0]$$
$$\text{Tập dữ liệu trễ đi: } \text{DEP\_DELAY} = [5.0, -5.0, 25.0]$$

| Mã KPI | Tên chỉ số theo KPI_SPEC v1.1 | Công thức toán học độc lập | Giá trị Tính toán lại (Recalculated Oracle) | Giá trị trong JSON Metadata | Trạng thái Đối chiếu |
|---|---|---|:---:|:---:|:---:|
| **`KPI-01`** | Tổng bản ghi accepted | $\text{count\_records}(C)$ | **3** | `3` | **MATCH (EXACT)** |
| **`KPI-02`** | Tỷ lệ trễ đến $\ge 15$ phút | $\sum \mathbf{1}[\text{ARR\_DELAY} \ge 15] / N$ | **1/3** ($\approx 0.333333333$) | `0.3333333333333333` | **MATCH ($< 10^{-9}$)** |
| **`KPI-03`** | Trễ đến trung bình có dấu | $\sum \text{ARR\_DELAY} / N = (0 - 12 + 20) / 3$ | **8/3** ($\approx 2.666666667$ min) | `2.6666666666666665` | **MATCH ($< 10^{-9}$)** |
| **`KPI-04`** | Tỷ lệ trễ đi $\ge 15$ phút | $\sum \mathbf{1}[\text{DEP\_DELAY} \ge 15] / N$ | **1/3** ($\approx 0.333333333$) | `0.3333333333333333` | **MATCH ($< 10^{-9}$)** |
| **`KPI-05`** | Trễ đi trung bình có dấu | $\sum \text{DEP\_DELAY} / N = (5 - 5 + 25) / 3$ | **25/3** ($\approx 8.333333333$ min) | `8.333333333333334` | **MATCH ($< 10^{-9}$)** |
| **`KPI-06-P50`** | Trung vị trễ đến (P50) | Median của $\{-12.0, 0.0, 20.0\}$ | **0.0 min** | `0.0` | **MATCH (EXACT)** |
| **`KPI-06-P90_cont`** | Phân vị 90 trễ đến (Type 7 liên tục) | $0.0 + 0.8 \times (20.0 - 0.0)$ | **16.0 min** | `16.0` | **MATCH (EXACT)** |
| **`KPI-06-P90_disc`** | Phân vị 90 trễ đến (Rời rạc mẫu) | Thống kê thứ tự mẫu (Order statistic $y_3$) | **20.0 min** | `20.0` | **MATCH (EXACT)** |
| **`KPI-07-TAXI_OUT`** | Taxi-out trung bình | $(15.0 + 12.0 + 18.0) / 3 = 45 / 3$ | **15.0 min** | `15.0` | **MATCH (EXACT)** |
| **`KPI-07-TAXI_IN`** | Taxi-in trung bình | $(5.0 + 6.0 + 7.0) / 3 = 18 / 3$ | **6.0 min** | `6.0` | **MATCH (EXACT)** |
| **`KPI-08-AIR_TIME`** | Thời gian bay trung bình | $(120.0 + 110.0 + 120.0) / 3 = 350 / 3$ | **350/3** ($\approx 116.6666667$ min) | `116.66666666666667` | **MATCH ($< 10^{-9}$)** |
| **`KPI-08-ACTUAL`** | Thời gian hành trình thực tế TB | $(140.0 + 128.0 + 145.0) / 3 = 413 / 3$ | **413/3** ($\approx 137.6666667$ min) | `137.66666666666666` | **MATCH ($< 10^{-9}$)** |
| **`KPI-08-CRS`** | Thời gian hành trình dự kiến TB | $(145.0 + 135.0 + 150.0) / 3 = 430 / 3$ | **430/3** ($\approx 143.3333333$ min) | `143.33333333333334` | **MATCH ($< 10^{-9}$)** |

*Kết luận đối chiếu số học:* **13/13 mục oracle khớp tuyệt đối với dữ liệu CSV thô.**

---

## 5. Kết quả Kiểm định QA Độc lập (Automated Verification Execution)

### 5.1. Thực thi Công cụ Kiểm chứng Hợp đồng và Oracles (`verify_t003_contract_consistency.py`)

Lệnh thực thi:
```powershell
PS D:\Study\Code\Apache\Flight_Analyzt\US_FLIGHT_PERFORMANCE_DOCS_V1> $env:PYTHONIOENCODING="utf-8"; python tools/qa/verify_t003_contract_consistency.py
```

Kết quả đầu ra thực tế (stdout):
```
================================================================================
T-003 INDEPENDENT CONTRACT CONSISTENCY & ARITHMETIC ORACLE VERIFICATION
================================================================================
[PASS] FIX-14 CSV file exists
[PASS] FIX-14 CSV header has exactly 34 columns
[PASS] FIX-14 CSV has exactly 5 data rows
[PASS] FIX-14 data row 1 has 34 columns
[PASS] FIX-14 data row 2 has 34 columns
[PASS] FIX-14 data row 3 has 34 columns
[PASS] FIX-14 data row 4 has 34 columns
[PASS] FIX-14 data row 5 has exactly 6 columns (column count mismatch)
[PASS] FIX-14 row 4 has ORIGIN='12A' (quarantine trigger)
[PASS] FIX-14 JSON metadata file exists
[PASS] Accounting raw_row_count == 5
[PASS] Accounting accepted_row_count == 3
[PASS] Accounting quarantined_row_count == 1
[PASS] Accounting rejected_row_count == 1
[PASS] Accounting invariant holds: 5 = 3 + 1 + 1
[PASS] Ingest acceptance rate is exactly 60.0% (3/5)
[PASS] Standardized rejection reason contains COLUMN_COUNT_MISMATCH: EXPECTED_34_FOUND_6
[PASS] Accepted ARR_DELAY values are [0.0, -12.0, 20.0]
[PASS] Accepted DEP_DELAY values are [5.0, -5.0, 25.0]
[PASS] Recalculated KPI-01 == 3
[PASS] Recalculated KPI-02 == 1/3 (~33.3333%)
[PASS] Recalculated KPI-03 == 8/3 (~2.6667 min)
[PASS] Recalculated KPI-04 == 1/3 (~33.3333%)
[PASS] Recalculated KPI-05 == 25/3 (~8.3333 min)
[PASS] Recalculated KPI-06 P50 == 0.0 min
[PASS] Recalculated KPI-06 P90 continuous == 16.0 min
[PASS] Recalculated KPI-06 P90 discrete == 20.0 min
[PASS] Recalculated KPI-07 Taxi-Out == 15.0 min
[PASS] Recalculated KPI-07 Taxi-In == 6.0 min
[PASS] Recalculated KPI-08 Air Time == 350/3 min
[PASS] Recalculated KPI-08 Actual Elapsed Time == 413/3 min
[PASS] Recalculated KPI-08 CRS Elapsed Time == 430/3 min
[PASS] JSON KPI-01 matches recalculated oracle
[PASS] JSON KPI-02 matches recalculated oracle
[PASS] JSON KPI-03 matches recalculated oracle
[PASS] JSON KPI-04 matches recalculated oracle
[PASS] JSON KPI-05 matches recalculated oracle
[PASS] JSON KPI-06-P50 matches recalculated oracle
[PASS] JSON KPI-06-P90_continuous matches recalculated oracle
[PASS] JSON KPI-06-P90_discrete matches recalculated oracle
[PASS] JSON KPI-07-TAXI_OUT matches recalculated oracle
[PASS] JSON KPI-07-TAXI_IN matches recalculated oracle
[PASS] JSON KPI-08-AIR_TIME matches recalculated oracle
[PASS] JSON KPI-08-ACTUAL_ELAPSED_TIME matches recalculated oracle
[PASS] JSON KPI-08-CRS_ELAPSED_TIME matches recalculated oracle
[PASS] T003_TEST_FIXTURE_SPEC.md exists
[PASS] All 14 fixtures (FIX-01..FIX-14) present in TEST_FIXTURE_SPEC
[PASS] No erroneous pattern in T003_FINAL_CLOSEOUT_VERIFICATION.md: KPI-02 wrongly mapped as on-time rate
[PASS] No erroneous pattern in T003_FINAL_CLOSEOUT_VERIFICATION.md: KPI-03 wrongly mapped as arrival late rate
[PASS] No erroneous pattern in T003_FINAL_CLOSEOUT_VERIFICATION.md: KPI-04 wrongly mapped as arrival average delay
[PASS] No erroneous pattern in T003_FINAL_CLOSEOUT_VERIFICATION.md: KPI-05 wrongly mapped as arrival median delay
[PASS] No erroneous pattern in T003_FINAL_CLOSEOUT_VERIFICATION.md: KPI-07 wrongly mapped as departure late rate
[PASS] No erroneous pattern in T003_FINAL_CLOSEOUT_VERIFICATION.md: KPI-08 wrongly mapped as departure average delay
[PASS] No erroneous pattern in T003_FINAL_CLOSEOUT_VERIFICATION.md: Hallucinated ARR_DELAY=[5, 22, 16] found
[PASS] No erroneous pattern in T003_FINAL_CLOSEOUT_VERIFICATION.md: Hallucinated DEP_DELAY=[-2, 18, 0] found
[PASS] No erroneous pattern in T003_FINAL_GATE_RECOMMENDATION.md: KPI-02 wrongly mapped as on-time rate
[PASS] No erroneous pattern in T003_FINAL_GATE_RECOMMENDATION.md: KPI-03 wrongly mapped as arrival late rate
[PASS] No erroneous pattern in T003_FINAL_GATE_RECOMMENDATION.md: KPI-04 wrongly mapped as arrival average delay
[PASS] No erroneous pattern in T003_FINAL_GATE_RECOMMENDATION.md: KPI-05 wrongly mapped as arrival median delay
[PASS] No erroneous pattern in T003_FINAL_GATE_RECOMMENDATION.md: KPI-07 wrongly mapped as departure late rate
[PASS] No erroneous pattern in T003_FINAL_GATE_RECOMMENDATION.md: KPI-08 wrongly mapped as departure average delay
[PASS] No erroneous pattern in T003_FINAL_GATE_RECOMMENDATION.md: Hallucinated ARR_DELAY=[5, 22, 16] found
[PASS] No erroneous pattern in T003_FINAL_GATE_RECOMMENDATION.md: Hallucinated DEP_DELAY=[-2, 18, 0] found
[PASS] No erroneous pattern in T003_TEST_FIXTURE_SPEC.md: KPI-02 wrongly mapped as on-time rate
[PASS] No erroneous pattern in T003_TEST_FIXTURE_SPEC.md: KPI-03 wrongly mapped as arrival late rate
[PASS] No erroneous pattern in T003_TEST_FIXTURE_SPEC.md: KPI-04 wrongly mapped as arrival average delay
[PASS] No erroneous pattern in T003_TEST_FIXTURE_SPEC.md: KPI-05 wrongly mapped as arrival median delay
[PASS] No erroneous pattern in T003_TEST_FIXTURE_SPEC.md: KPI-07 wrongly mapped as departure late rate
[PASS] No erroneous pattern in T003_TEST_FIXTURE_SPEC.md: KPI-08 wrongly mapped as departure average delay
[PASS] No erroneous pattern in T003_TEST_FIXTURE_SPEC.md: Hallucinated ARR_DELAY=[5, 22, 16] found
[PASS] No erroneous pattern in T003_TEST_FIXTURE_SPEC.md: Hallucinated DEP_DELAY=[-2, 18, 0] found
[PASS] No erroneous pattern in T003_PERCENTILE_AND_MIN_N_DECISIONS.md: KPI-02 wrongly mapped as on-time rate
[PASS] No erroneous pattern in T003_PERCENTILE_AND_MIN_N_DECISIONS.md: KPI-03 wrongly mapped as arrival late rate
[PASS] No erroneous pattern in T003_PERCENTILE_AND_MIN_N_DECISIONS.md: KPI-04 wrongly mapped as arrival average delay
[PASS] No erroneous pattern in T003_PERCENTILE_AND_MIN_N_DECISIONS.md: KPI-05 wrongly mapped as arrival median delay
[PASS] No erroneous pattern in T003_PERCENTILE_AND_MIN_N_DECISIONS.md: KPI-07 wrongly mapped as departure late rate
[PASS] No erroneous pattern in T003_PERCENTILE_AND_MIN_N_DECISIONS.md: KPI-08 wrongly mapped as departure average delay
[PASS] No erroneous pattern in T003_PERCENTILE_AND_MIN_N_DECISIONS.md: Hallucinated ARR_DELAY=[5, 22, 16] found
[PASS] No erroneous pattern in T003_PERCENTILE_AND_MIN_N_DECISIONS.md: Hallucinated DEP_DELAY=[-2, 18, 0] found
[PASS] No wrongful temporal mapping of TS-009 in T003_FINAL_CLOSEOUT_VERIFICATION.md
[PASS] No wrongful temporal mapping of TS-009 in T003_FINAL_GATE_RECOMMENDATION.md
[PASS] No wrongful temporal mapping of TS-009 in T003_TEST_FIXTURE_SPEC.md
[PASS] No wrongful temporal mapping of TS-009 in T003_PERCENTILE_AND_MIN_N_DECISIONS.md
[PASS] PROJECT_STATE.md exists
[PASS] Gate G2 is NOT passed in PROJECT_STATE.md
[PASS] Gate G2 is NOT overclaimed as PASS
[PASS] FP-DEC-015 and FP-DEC-016 are NOT claimed as APPROVED (retained as PROPOSED)
================================================================================
VERIFICATION SUMMARY: 87 PASS, 0 FAIL
================================================================================

ALL CONTRACT CONSISTENCY & ARITHMETIC ORACLE CHECKS PASSED.
```
- **Stderr:** *(Hoàn toàn trống)*
- **Mã thoát (Exit Code):** `0`

### 5.2. Thực thi Công cụ Kiểm chứng Working-Tree (`check_working_tree_consistency.py`)
```powershell
PS D:\Study\Code\Apache\Flight_Analyzt\US_FLIGHT_PERFORMANCE_DOCS_V1> python tools/check_working_tree_consistency.py
Working-Tree PASS assertions: 88; FAIL: 0
ALL WORKING-TREE CHECKS PASSED.
```
- **Mã thoát (Exit Code):** `0`

---

## 6. Danh mục Tệp được Tạo mới và Hiệu chỉnh

1. [`docs/05-evidence/T003_FINAL_ACCEPTANCE_RECONCILIATION.md`](T003_FINAL_ACCEPTANCE_RECONCILIATION.md) *(Tạo mới)*: Báo cáo đối chiếu kỹ thuật độc lập toàn diện giải quyết triệt để A01–A06.
2. [`tools/qa/verify_t003_contract_consistency.py`](../../tools/qa/verify_t003_contract_consistency.py) *(Tạo mới)*: Script kiểm toán tự động độc lập kiểm tra cấu trúc FIX-14, tính toán lại oracle số học và rà soát ngữ nghĩa báo cáo.
3. [`docs/05-evidence/T003_FIX14_accounting_fixture.json`](T003_FIX14_accounting_fixture.json) *(Hiệu chỉnh)*: Chuẩn hóa mã lý do hàng 5 thành `COLUMN_COUNT_MISMATCH: EXPECTED_34_FOUND_6`.
4. [`docs/05-evidence/T003_TEST_FIXTURE_SPEC.md`](T003_TEST_FIXTURE_SPEC.md) *(Hiệu chỉnh)*: Chuẩn hóa mã lý do hàng 5 FIX-14 và làm rõ ánh xạ test catalog.
5. [`docs/05-evidence/T003_PERCENTILE_AND_MIN_N_DECISIONS.md`](T003_PERCENTILE_AND_MIN_N_DECISIONS.md) *(Hiệu chỉnh)*: Sửa giải thích FIX-12 ($|80-79.1|=0.9$ min), bổ sung cảnh báo không cam kết sai số tuyệt đối phổ quát, quy định trạng thái `PENDING_G5_VALIDATION`.
6. [`docs/05-evidence/T003_FINAL_CLOSEOUT_VERIFICATION.md`](T003_FINAL_CLOSEOUT_VERIFICATION.md) *(Hiệu chỉnh)*: Phục hồi ánh xạ chuẩn 8 CORE KPIs, số liệu CSV thực thi, và ranh giới test catalog.
7. [`tools/check_working_tree_consistency.py`](../../tools/check_working_tree_consistency.py) *(Hiệu chỉnh)*: Bổ sung nhận diện hợp lệ thư mục `tools/qa/`.
8. [`docs/04-execution/PROJECT_STATE.md`](../04-execution/PROJECT_STATE.md) *(Hiệu chỉnh)*: Cập nhật dẫn chiếu đến báo cáo đối chiếu cuối cùng `T003_FINAL_ACCEPTANCE_RECONCILIATION.md`.

---

## 7. Danh mục 8 Rủi ro Chưa giải quyết Bàn giao (OR-01 đến OR-08)

Toàn bộ 8 rủi ro mở tiếp tục được bảo lưu và chuyển giao có kiểm soát:

1. **OR-01:** Nguồn gốc upstream và mã băm raw CSV chưa đối chiếu trực tiếp với cổng BTS. *(Chuyển giao G4/G5/G7)*.
2. **OR-02:** Giới hạn đại diện và độ bao phủ do thay đổi quy định BTS Part 234 năm 2018. *(Chuyển giao T-013/T-014 tại G6/G7)*.
3. **OR-03:** Cặp trùng khóa kinh doanh YX 3624 (2018), bản chất vật lý `UNKNOWN`, cấm xóa dữ liệu, áp dụng test `TS-021`. *(Chuyển giao T-004 và G5)*.
4. **OR-04:** Thiếu `TAIL_NUM` trong schema 34 cột; xác nhận out-of-scope cho phân tích mô tả CORE. *(Đã kiểm soát)*.
5. **OR-05:** Tình trạng đơn vị đo mang tính tạm thời (`PROVISIONAL`) do schema JSON v1.1 chỉ lưu min/max toàn cục cho `ARR_DELAY`. Quét kiểm chứng toàn bộ 54.67M dòng tại Gate G5/G6. *(Chuyển giao G5/G6)*.
6. **OR-06:** Rủi ro phân tích thời gian, rollover nửa đêm và 2400 semantics. *(Chuyển giao ngay cho **Task T-004**)*.
7. **OR-07:** Sai khác bản chất giữa thuật toán phân vị PySpark (discrete) và nội suy liên tục (continuous Type 7). Áp dụng benchmark bắt buộc tại G5 (TS-008). *(Chuyển giao G5)*.
8. **OR-08:** Tính khả thi và phân giải dữ liệu thời tiết. Áp dụng nhánh tùy chọn `CONDITIONAL_PENDING / CONDITIONAL_NO_GO`. *(Chuyển giao cho **Task T-005**)*.

---

## 8. Tình trạng Sign-off và Quyết định Cần Reviewer Phê chuẩn

Để hoàn tất thủ tục bàn giao chính thức Task T-003, Project Lead và Technical Reviewer cần xem xét ký duyệt:
1. **Phê duyệt Hợp đồng 8 CORE KPIs:** Khóa định nghĩa toán học, ranh giới mẫu số thuần tập $\text{count\_records}(C)$, và xử lý mẫu số 0 của `KPI-01` đến `KPI-08`.
2. **Phê duyệt Đơn vị đo:** Chấp thuận nhãn `OFFICIAL_MINUTES_EMPIRICALLY_CONSISTENT_PROVISIONAL` cho 7 thước đo số.
3. **Ghi nhận 2 Quyết định Kiến trúc Bổ sung (PROPOSED):**
   - `FP-DEC-015`: Lựa chọn PySpark `percentile_approx(accuracy=10000)` với trạng thái `PENDING_G5_VALIDATION`.
   - `FP-DEC-016`: Chính sách ngưỡng cỡ mẫu tối thiểu đa tầng ($1000/365/100$) kèm cơ chế cảnh báo.
4. **Ghi nhận Ca kiểm thử Đề xuất (PROPOSED):**
   - `TS-021`: Duplicate-Preservation & Event-Identity Guard (bảo vệ không xóa cặp YX 3624 trong FIX-13).
5. **Chấp thuận Bàn giao Danh mục 8 Rủi ro Mở (`OR-01` đến `OR-08`).**

---

## 9. Kết luận và Kiến nghị Hành động Kế tiếp

### 9.1. Đề xuất Trạng thái
Toàn bộ các lỗi kỹ thuật và mâu thuẫn số liệu đã được khắc phục triệt để. Phép tính oracle đã được kiểm chứng tự động bằng script độc lập đạt 100% assertions. Đội ngũ kỹ thuật trân trọng đề xuất trạng thái:
$$\mathbf{T\text{-}003: READY\_FOR\_SIGNOFF}$$

### 9.2. Nguyên tắc Dừng và Ranh giới Gate G2
> [!IMPORTANT]
> **1. Gate G2 vẫn giữ trạng thái `IN_PROGRESS / NOT_PASSED`:** Gate G2 chỉ có thể được xem xét nghiệm thu sau khi hoàn thành Task T-004 (Time representation & safe datetime parsing) và Task T-005 (Weather conditional branch).  
> **2. DỪNG LẠI TẠI ĐÂY:** AI Agent tuân thủ nghiêm ngặt quy định tại `AGENTS.md`, **DỪNG LẠI SAU TASK NÀY**, tuyệt đối **KHÔNG TỰ ĐỘNG THỰC HIỆN TASK T-004** khi chưa có chỉ thị chính thức từ User / Project Lead.
