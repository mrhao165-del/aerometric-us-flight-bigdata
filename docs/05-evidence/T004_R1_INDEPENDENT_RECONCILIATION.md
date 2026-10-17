# T-004-R1: BÁO CÁO ĐỐI CHIẾU KHOA HỌC & HIỆU CHỈNH KIỂM TOÁN BIỂU DIỄN THỜI GIAN ĐỘC LẬP
## (INDEPENDENT EVIDENCE RECONCILIATION & TEMPORAL AUDIT DEFECT REMEDIATION)

- **Mã nhiệm vụ:** `T-004-R1` (Targeted Temporal Audit Correction & Scientific Reconciliation)
- **Gate kiểm soát:** `G2` (Data Quality, Cohort & Metric Contracts)
- **Ngày lập:** 2026-10-14
- **Vai trò:** Senior Big Data Engineer, Data Quality Auditor, Temporal Data Specialist & Independent Reviewer
- **Trạng thái nhiệm vụ:** **`READY_FOR_SIGNOFF_WITH_OPEN_DEFECT`**
- **Trạng thái Gate G2:** **`IN_PROGRESS / NOT_PASSED`** (Chờ hoàn thành Task T-005)
- **Văn bản tuân thủ:** [`AGENTS.md`](../../AGENTS.md), [`docs/01-planning/BACKLOG.md`](../01-planning/BACKLOG.md), [`docs/02-design/DATA_CONTRACT.md`](../02-design/DATA_CONTRACT.md), [`docs/02-design/DATA_DICTIONARY.md`](../02-design/DATA_DICTIONARY.md), [`docs/02-design/DECISIONS.md`](../02-design/DECISIONS.md), [`docs/02-design/KPI_SPEC.md`](../02-design/KPI_SPEC.md), [`docs/03-quality/TEST_PLAN.md`](../03-quality/TEST_PLAN.md) (`TS-004`, `TS-009`, `TS-010`), [`docs/03-quality/RISK_REGISTER.md`](../03-quality/RISK_REGISTER.md), [`docs/04-execution/PROJECT_STATE.md`](../04-execution/PROJECT_STATE.md).

---

## 1. Tóm tắt Điều hành & Phán quyết Độc lập (Executive Summary & Independent Verdict)

Nhiệm vụ **T-004-R1** được thực hiện nhằm xử lý dứt điểm 7 điểm bất đồng kỹ thuật (**`F01` đến `F07`**) đã được reviewer chỉ ra sau vòng kiểm toán ban đầu của Task T-004. Báo cáo này xác lập các bằng chứng thực nghiệm độc lập, chuẩn hóa các ranh giới suy diễn, sửa đổi các ánh xạ KPI, đồng thời cung cấp hai tệp dữ liệu kiểm thử thực thi độc lập (`CSV` và `JSON`) cho bộ kiểm chuẩn `TS-010`.

### Phán quyết Độc lập
1. **Nhiệm vụ T-004:** **`READY_FOR_SIGNOFF_WITH_OPEN_DEFECT`**.
   - Toàn bộ các phát hiện F01–F07 đã được xử lý triệt để, có bằng chứng đối chiếu và script kiểm tra tự động đạt $100\%$ PASS.
   - Rủi ro **`OR-05`** (vắng mặt Tháng 3/2024) được xác lập là **`OPEN_QUALITY_DEFECT`** (chưa đóng) với 3 phương án xử lý rõ ràng cho G3/G4.
   - Ma trận phân loại trường an toàn 34 cột bảo vệ tuyệt đối 8 CORE KPIs, cấm hoàn toàn phép trừ chuỗi timestamp trực tiếp và cấm tự ý cộng 24h.
2. **Gate G2:** Tiếp tục duy trì trạng thái **`IN_PROGRESS / NOT_PASSED`**.
   - Tuyệt đối không mở Gate G2 trước khi hoàn thành **Task T-005 (Weather Usability Audit)**.

---

## 2. F01 — Nguyên nhân gốc & Phân loại Độ bao phủ Lịch Năm Nhuận 2024

### 2.1 Hiện trạng Thực chứng
Thực hiện quét luồng giới hạn bộ nhớ (*bounded streaming audit*) trên toàn bộ $6,284,841$ dòng của tệp `flight_with_weather_2024.csv` (thời gian quét: 20.28 giây), kết quả thực chứng xác nhận:
- **Số ngày dịch vụ riêng biệt quan sát được:** Đúng **$335$ ngày**.
- **Tham chiếu lịch chuẩn năm nhuận 2024:** Đúng **$366$ ngày**.
- **Khoảng trống khuyết thiếu:** Vắng mặt toàn bộ **31 ngày của Tháng 3 năm 2024** (`2024-03-01` đến `2024-03-31`).
- **Phân bổ tháng:** Cột `MONTH` chỉ nhận 11 giá trị ($1, 2, 4, 5, 6, 7, 8, 9, 10, 11, 12$); giá trị `MONTH = 3` có đúng $0$ bản ghi.
- **Tính nhất quán giữa cột MONTH và FL_DATE:** Đúng $100\%$ (chính xác $0$ bản ghi bất đồng trên $6,284,841$ dòng).
- **Ngày nhuận 2024-02-29:** Có mặt đầy đủ trong dữ liệu với đúng $18,642$ chuyến bay.

### 2.2 Phân loại Kỹ thuật & Ranh giới Suy diễn
- **Trạng thái phân loại:** **`DATA_ABSENT_IN_CURRENT_CSV (UPSTREAM_ROOT_CAUSE_UNKNOWN)`**.
- **Ranh giới:** Nhóm nghiên cứu chỉ sở hữu sản phẩm dẫn xuất CSV từ nguồn lưu trữ bên ngoài, không sở hữu mã nguồn ETL upstream trích xuất dữ liệu từ Cục Thống kê Giao thông Vận tải Hoa Kỳ (BTS). Do đó, **tuyệt đối không kết luận hoặc suy đoán rằng "script ETL upstream bị lỗi lọc tháng 3"**, mà chỉ ghi nhận sự vắng mặt thực tế của dữ liệu trong tệp CSV hiện hữu.

### 2.3 Nguyên tắc Đánh giá Kiểm thử TS-004 & Rủi ro OR-05
- **Kiểm thử TS-004:** Giữ nguyên tham chiếu lịch đầy đủ $366$ ngày; năm 2024 được đánh giá là **`INCOMPLETE_COVERAGE / DEFECT_DETECTED`**. Tuyệt đối **không hạ ngưỡng kiểm thử xuống 335 ngày** để tạo kết quả PASS giả mạo.
- **Rủi ro OR-05:** Trong [`docs/03-quality/RISK_REGISTER.md`](../03-quality/RISK_REGISTER.md) và hồ sơ T-004, OR-05 được xác lập ở trạng thái **`OPEN_QUALITY_DEFECT`** (chưa đóng).
- **3 Phương án Xử lý Kỹ thuật cho G3/G4:**
  1. *Phương án A (Data Supplementation):* Bổ sung dữ liệu Tháng 3/2024 từ nguồn BTS On-Time chính thống nếu được cấp quyền cập nhật kho dữ liệu thô.
  2. *Phương án B (Explicit Partial-Year Marking):* Giữ nguyên dữ liệu thô, gắn nhãn rõ ràng năm 2024 là "partial year (11 months)" trong mọi biểu đồ xu hướng dài hạn 2016–2024 để tránh thiên lệch mùa vụ (*seasonal bias*).
  3. *Phương án C (Common-Month Windowing):* Trong các bài phân tích so sánh liên năm (Year-over-Year), thiết lập cửa sổ phân tích loại trừ Tháng 3 ở tất cả 9 năm (hoặc chỉ so sánh theo từng tháng tương ứng).

---

## 3. F02 — Ranh giới Bằng chứng Hiện tượng Bay Qua Nửa Đêm & Bản chất YX 3624

### 3.1 Bằng chứng Toán học & Dòng Vật lý
Tại tệp dữ liệu `flight_with_weather_2018.csv`, cặp dòng vật lý **6,384,132** và **6,384,133** thuộc chuyến bay YX 3624 (chặng Denver DEN $\to$ Northwest Arkansas XNA, ngày kế hoạch `2018-06-21`):

| Trường dữ liệu | Dòng 6,384,132 (Row A) | Dòng 6,384,133 (Row B) | Nhận xét đối chiếu |
|---|:---:|:---:|---|
| `FL_DATE` | `2018-06-21 00:00:00` | `2018-06-21 00:00:00` | Cùng ngày dịch vụ theo lịch trình |
| `CRS_DEP_TIME` | `2018-06-21 20:07:00` | `2018-06-21 20:07:00` | Cùng giờ cất cánh kế hoạch (20:07 tối) |
| `DEP_TIME` | `2018-06-21 10:44:00` | `2018-06-21 20:27:00` | Row A: 10:44 (sáng); Row B: 20:27 (tối) |
| `DEP_DELAY` | **`+877.0` phút** | **`+20.0` phút** | Row A trễ 14.6 giờ; Row B trễ 20 phút |
| `ARR_DELAY` | **`+941.0` phút** | **`+4.0` phút** | Row A trễ 15.7 giờ; Row B trễ 4 phút |
| `CRS_ELAPSED_TIME` | `118.0` phút | `118.0` phút | Thời gian bay kế hoạch chuẩn |
| `ACTUAL_ELAPSED_TIME` | `182.0` phút | `102.0` phút | Row A: thời gian thực 182 phút |
| `TAXI_OUT` / `AIR` / `TAXI_IN` | `91.0` / `84.0` / `7.0` | `13.0` / `83.0` / `6.0` | Row A: $91 + 84 + 7 = 182.0$; Row B: $13 + 83 + 6 = 102.0$ (khớp $100\%$ thực chứng) |

### 3.2 Phân định 3 Cấp độ Ranh giới Bằng chứng (Section 2.3)
1. **Cấp độ `VERIFIED` (Bằng chứng Số học Được Xác minh):**
   - Số phút độ trễ `DEP_DELAY = +877.0` và `ARR_DELAY = +941.0` được lưu độc lập dưới dạng số thực `float64`.
   - Đẳng thức phân rã thời lượng hoàn toàn chính xác: $\text{ACTUAL\_ELAPSED} = 91 + 84 + 7 = 182.0$ phút.
   - Đẳng thức cân bằng độ trễ thỏa mãn hoàn hảo:
     $$\text{ARR\_DELAY} = \text{DEP\_DELAY} + (\text{ACTUAL\_ELAPSED} - \text{CRS\_ELAPSED}) = 877.0 + (182.0 - 118.0) = 941.0 \text{ phút}$$
   - Phép trừ chuỗi timestamp trực tiếp gây ra sai số nghiêm trọng:
     $$\texttt{DEP\_TIME} - \texttt{CRS\_DEP\_TIME} = 10:44 - 20:07 = -563 \text{ phút} \neq +877.0 \text{ phút}$$
     Chênh lệch đúng bằng $877 - (-563) = 1440 \text{ phút}$ (đúng 24 giờ).
2. **Cấp độ `INFERRED` (Suy diễn Hợp lý nhưng Chưa Có Chứng từ Hãng):**
   - Chuyến bay ở Row A nhiều khả năng đã bị hoãn qua đêm sang sáng ngày hôm sau (`2018-06-22`), cất cánh lúc 10:44 sáng (tức sau giờ kế hoạch 20:07 tối hôm trước là 14 giờ 37 phút = 877 phút).
   - Quy trình tạo dữ liệu của bên thứ ba đã kẹp ngày lịch trình `2018-06-21` vào chuỗi giờ thực tế thay vì sử dụng ngày thực tế `2018-06-22`.
3. **Cấp độ `UNKNOWN` (Bất khả Tri trong Phạm vi Dữ liệu Hiện hữu):**
   - Không thể biết mã nguồn script ETL upstream đã xử lý như thế nào (`UPSTREAM_CODE_UNKNOWN`).
   - Do tập dữ liệu 34 cột **hoàn toàn thiếu trường số hiệu đuôi tàu bay (`TAIL_NUM`)**, không thể khẳng định chắc chắn Row A và Row B là cùng một tàu bay vật lý hay hai tàu bay khác nhau (`PHYSICAL_ENTITY_IDENTITY_UNKNOWN`).

### 3.3 Lệnh Cấm Tuyệt đối trong Thiết kế Pipeline
- **CẤM TUYỆT ĐỐI** mọi phép trừ chuỗi timestamp hoặc `unix_timestamp(ARR_TIME) - unix_timestamp(DEP_TIME)`.
- **CẤM TUYỆT ĐỐI** thuật toán tự động cộng $24$ giờ khi phát hiện hiệu thời gian âm (vì sẽ phá hủy các trường hợp chuyến bay qua múi giờ hoặc trễ nhiều ngày).
- **QUY ĐỊNH BẮT BUỘC:** Mọi tính toán thời lượng và độ trễ phải sử dụng trực tiếp 7 trường số phút thực nghiệm.

---

## 4. F03 — Hiệu chỉnh Ánh xạ Chỉ số An toàn (KPI Safe Field Mapping)

Ma trận phân loại trường an toàn 4 cấp độ tại [`docs/05-evidence/T004_SAFE_FIELDS_DECISION.md`](T004_SAFE_FIELDS_DECISION.md) đã được hiệu chỉnh chính xác để ánh xạ đúng với 8 CORE KPIs đã ban hành trong [`docs/02-design/KPI_SPEC.md`](../02-design/KPI_SPEC.md):

| Nhóm Cột & Cấp độ An toàn | Danh sách Cột Dữ liệu (34 cột) | Vai trò Kỹ thuật & Ánh xạ CORE KPI |
|---|---|---|
| **Tier 1: `SAFE_FOR_DIRECT_USE`** (17 cột) | `FL_DATE`, `OP_CARRIER`, `OP_CARRIER_FL_NUM`, `ORIGIN`, `DEST`, `MONTH`, `DAY_OF_MONTH`, `DAY_OF_WEEK`, `ORIGIN_INDEX`, `DEST_INDEX`, `O_LATITUDE`, `O_LONGITUDE`, `D_LATITUDE`, `D_LONGITUDE`, `DEP_DELAY`, `ARR_DELAY`, `TAXI_OUT`, `TAXI_IN`, `CRS_ELAPSED_TIME`, `ACTUAL_ELAPSED_TIME`, `AIR_TIME` | - `FL_DATE` $\to$ Khóa phân vùng ngày dịch vụ & mẫu số **`KPI-01`**.<br>- `ARR_DELAY` $\to$ Tỷ lệ trễ đến **`KPI-02`**, Trung bình trễ đến **`KPI-03`**, Phân vị P50/P90 **`KPI-06`**.<br>- `DEP_DELAY` $\to$ Tỷ lệ trễ đi **`KPI-04`**, Trung bình trễ đi **`KPI-05`**.<br>- `TAXI_OUT`, `TAXI_IN` $\to$ Thời gian lăn bánh **`KPI-07`**.<br>- `CRS_ELAPSED_TIME`, `ACTUAL_ELAPSED_TIME`, `AIR_TIME` $\to$ Phân tích thời gian bay **`KPI-08`**. |
| **Tier 2: `SAFE_WITH_DOCUMENTED_TRANSFORMATION`** (2 cột) | `CRS_DEP_TIME`, `CRS_ARR_TIME` | - Trích xuất an toàn `CRS_DEP_HOUR = hour(CRS_DEP_TIME)` ($0..23$) để phân tích khung giờ.<br>- Cấm trừ hai mốc này để tính thời lượng; cấm sử dụng để phân vùng ngày. |
| **Tier 3: `CONDITIONALLY_USABLE`** (10 cột) | `DEP_TIME`, `ARR_TIME`, `WHEELS_OFF`, `WHEELS_ON`, và 6 trường thời tiết (`O_TEMP`, `O_PRCP`, `O_WSPD`, `D_TEMP`, `D_PRCP`, `D_WSPD`) | - Các mốc giờ vận hành chỉ dùng cho mục đích kiểm toán hiển thị chuỗi giờ địa phương, không dùng cho số học thời gian.<br>- 6 trường thời tiết phụ thuộc vào kết quả Task T-005. |
| **Tier 4: `NOT_AVAILABLE / BLOCKED`** (5 hạng mục) | - Cột `FLIGHTS` (bằng 1.0 cố định)<br>- Cột `CANCELLED` & `DIVERTED` (vắng mặt)<br>- Phép trừ trực tiếp timestamp<br>- Tự ý cộng 24h (*synthetic +24h*)<br>- Mô hình hóa chuỗi chuyến bay (*Flight Chain*) | - Khóa tuyệt đối ngoài 8 CORE KPIs.<br>- Flight Chain duy trì phán quyết **`FINAL — NO_GO`** do thiếu `TAIL_NUM` và tính toàn vẹn chuyến bay bị gián đoạn. |

---

## 5. F04 — Hiệu chỉnh Số học Fixture Múi giờ & Trôi Đồng hồ (Timezone Alignment)

Trong bộ đặc tả kiểm thử `TS-010` ([`docs/05-evidence/T004_TEST_FIXTURE_SPEC.md`](T004_TEST_FIXTURE_SPEC.md)), hai ca kiểm thử bay qua múi giờ **`TF-06`** và **`TF-07`** đã được tính toán lại chính xác giữa giờ đồng hồ địa phương (*local clock time*) và thời gian trôi thực tế (*UTC elapsed time*):

### 5.1 Kịch bản TF-06: Chuyến bay Ngày Nhuận & Múi giờ (LAS $\to$ PHX)
- **Tuyến bay & Ngày:** WN 606 (Las Vegas LAS $\to$ Phoenix PHX), ngày `2024-02-29`.
- **Múi giờ:** Las Vegas thuộc PST (UTC-8); Phoenix thuộc MST (UTC-7 quanh năm không đổi DST). Độ lệch: **$+1.0$ giờ** (+60 phút).
- **Mốc giờ địa phương:**
  - Khởi hành thực tế: `2024-02-29 13:58:00` (tương đương `21:58:00 UTC`).
  - Hạ cánh thực tế: `2024-02-29 16:18:00` (tương đương `23:18:00 UTC`).
- **Thời lượng bay thực tế:**
  - Hiệu số theo UTC: $23:18 - 21:58 = \mathbf{80.0 \text{ phút}}$ ($1$ giờ $20$ phút).
  - Hiệu số đồng hồ địa phương: $16:18 - 13:58 = 140.0 \text{ phút}$.
  - Chuẩn hóa theo múi giờ: $140.0 \text{ phút} - 60.0 \text{ phút (TZ)} = \mathbf{80.0 \text{ phút}}$.
- **Các trường kiểm chuẩn:** `CRS_ELAPSED_TIME = 80.0`, `ACTUAL_ELAPSED_TIME = 80.0`, `AIR_TIME = 60.0`, `TAXI_OUT = 14.0`, `TAXI_IN = 6.0`.
  - Phân rã thời gian: $14.0 + 60.0 + 6.0 = 80.0$ (chính xác $100\%$).
  - Độ trễ: $\text{DEP\_DELAY} = -2.0$, $\text{ARR\_DELAY} = -2.0$. Cân bằng: $-2 + (80 - 80) = -2.0$.

### 5.2 Kịch bản TF-07: Chuyến bay Giao thừa & Múi giờ (SEA $\to$ ANC)
- **Tuyến bay & Ngày:** AS 707 (Seattle SEA $\to$ Anchorage ANC), ngày dịch vụ `2023-12-31`.
- **Múi giờ:** Seattle thuộc PST (UTC-8); Anchorage thuộc AKST (UTC-9). Độ lệch: **$-1.0$ giờ** (-60 phút).
- **Mốc giờ địa phương:**
  - Khởi hành kế hoạch: `2023-12-31 23:45:00` (tương đương `2024-01-01 07:45:00 UTC`).
  - Khởi hành thực tế: `2023-12-31 23:50:00` (tương đương `2024-01-01 07:50:00 UTC`).
  - Hạ cánh thực tế: `2024-01-01 02:15:00` (tương đương `2024-01-01 11:15:00 UTC`).
- **Thời lượng bay thực tế:**
  - Hiệu số theo UTC: $11:15 - 07:50 = \mathbf{205.0 \text{ phút}}$ ($3$ giờ $25$ phút).
  - Hiệu số đồng hồ địa phương: $02:15 - 23:50 = 2 \text{ giờ } 25 \text{ phút} = 145.0 \text{ phút}$.
  - Chuẩn hóa theo múi giờ: $145.0 \text{ phút} + 60.0 \text{ phút (TZ)} = \mathbf{205.0 \text{ phút}}$.
- **Các trường kiểm chuẩn:** `CRS_ELAPSED_TIME = 210.0`, `ACTUAL_ELAPSED_TIME = 205.0`, `AIR_TIME = 180.0`, `TAXI_OUT = 16.0`, `TAXI_IN = 9.0`.
  - Phân rã thời gian: $16.0 + 180.0 + 9.0 = 205.0$ (chính xác $100\%$).
  - Độ trễ: $\text{DEP\_DELAY} = +5.0$, $\text{ARR\_DELAY} = 0.0$. Cân bằng: $5 + (205 - 210) = 0.0$.
  - Khóa phân vùng ngày dịch vụ: Giữ nguyên `FL_DATE = 2023-12-31 00:00:00` (thuộc năm 2023).

---

## 6. F05 — Tách biệt Rõ ràng Danh mục Kiểm thử TS-009 vs TS-010 vs TS-004

Để tránh nhầm lẫn giữa các phạm vi kiểm chuẩn tại Gate G2, G4 và G6, ranh giới giữa các mã kiểm thử được quy định thống nhất như sau:

| Mã Kiểm chuẩn | Tên Kiểm chuẩn | Gate Kiểm soát | Đối tượng Bảo vệ | Hành vi Kiểm tra & Oracle |
|:---:|---|:---:|---|---|
| **`TS-009`** | Scope & Guard Tests | Gate G2 & G4 | - Cột `FLIGHTS = 1.0`<br>- Thiếu `CANCELLED` & `DIVERTED`<br>- Weather optional guards | Kiểm tra pipeline không dùng `FLIGHTS` làm mẫu số; chặn việc tạo KPI tỷ lệ hủy chuyến; đảm bảo nhánh thời tiết cách ly hoàn toàn với 8 CORE KPIs. |
| **`TS-010`** | Safe Time & Overnight Guard Tests | Gate G2 & G4 | - Khung giờ `CRS_DEP_HOUR`<br>- Hiện tượng bay qua nửa đêm<br>- Bay qua múi giờ<br>- Cấm trừ chuỗi timestamp | Sử dụng bộ 9 synthetic fixtures `TF-01` đến `TF-09` để kiểm tra parser không văng lỗi tại mốc 2400/00:00:00; xác nhận pipeline không dùng phép trừ timestamp trực tiếp. |
| **`TS-004`** | Calendar Continuity Test | Gate G6 | - Độ bao phủ lịch đầy đủ của từng năm (365/366 ngày) | Đối chiếu số ngày phân biệt với lịch thiên văn; gắn cờ phát hiện khiếm khuyết `INCOMPLETE_COVERAGE / DEFECT_DETECTED` cho năm 2024. |

---

## 7. F06 — Bảng Đối chiếu Đánh số Rủi ro Mở (Risk Register Crosswalk)

Do báo cáo hòa giải trước đó ([`T003_FINAL_ACCEPTANCE_RECONCILIATION.md`](T003_FINAL_ACCEPTANCE_RECONCILIATION.md)) đã tạm thời đánh số cục bộ một số rủi ro, bảng dưới đây chuẩn hóa ánh xạ đối chiếu về danh mục chuẩn tắc của [`docs/03-quality/RISK_REGISTER.md`](../03-quality/RISK_REGISTER.md):

| Mã Rủi ro Chuẩn tắc | Mã Tạm thời trong T-003 Recon | Tóm tắt Bản chất Rủi ro | Trạng thái Sau T-004-R1 | Hướng Xử lý Tiếp theo |
|:---:|:---:|---|:---:|---|
| **`OR-01`** | `OR-01` | Cột `FLIGHTS` bằng 1.0 cố định trên toàn bộ 54.67M dòng | Đã khóa thiết kế | Chuyển G4 kiểm thử Spark (`TS-009`) |
| **`OR-02`** | `OR-02` | Rủi ro mất trễ cực đoan nếu deduplicate tùy tiện (ca YX 3624) | Đã khóa thiết kế | Bảo vệ bằng `TS-020` và `TS-021` |
| **`OR-03`** | `OR-03` | Đơn vị 7 trường độ trễ/thời lượng giữ nhãn `PROVISIONAL` | Bảo lưu rủi ro | Chờ đối chiếu BTS On-Time tại G5 |
| **`OR-04`** | `OR-04` | Thiếu cột `CANCELLED` và `DIVERTED` trong 34 cột raw CSV | Đã đóng phạm vi | Khóa ngoài 8 CORE KPIs |
| **`OR-05`** | `OR-07` | **Tính liên tục lịch năm nhuận 2024 (vắng mặt Tháng 3/2024)** | **`OPEN_QUALITY_DEFECT`** (Chưa đóng) | Xử lý tại G3/G4 theo 3 phương án (A, B, C) |
| **`OR-06`** | `OR-08` | Rollover mốc giờ thực tế (`ARR_TIME`, `DEP_TIME`) | Đã giải tỏa bằng chính sách & ma trận an toàn | Bảo vệ bằng 9 fixtures `TS-010` (`TF-01..TF-09`) |
| **`OR-07`** | `OR-05` | Dữ liệu thời tiết thiếu trạm đo, mốc thời gian và đơn vị đo | `CONDITIONAL_PENDING` | **Chuyển giao cho Task T-005** |
| **`OR-08`** | `OR-06` | Chưa có SHA-256 tham chiếu từ cổng phát hành gốc | `METADATA_MATCH_ONLY` | Chuyển giao Task T-007 (G4) |

---

## 8. F07 — Khả năng Tái lập & Giới hạn Thời gian Kiểm toán Bounded (Audit Performance)

Để đảm bảo tính trung thực khoa học theo yêu cầu của `AGENTS.md` (không giả mạo việc nạp toàn bộ dataset vào bộ nhớ máy ảo), toàn bộ quá trình kiểm toán thực chứng được thực thi thông qua các công cụ đọc luồng giới hạn dung lượng bộ nhớ (*bounded-memory chunked streaming*):

1. **Kiểm toán Chi tiết Năm 2024 (`task-1003`):**
   - **Tệp nguồn:** `data/raw/tabular/flight_with_weather_2024.csv` ($6,284,841$ dòng).
   - **Thời gian thực thi:** Đúng **$20.28$ giây**.
   - **Mức tiêu thụ bộ nhớ:** Cố định dưới 50 MB RAM (đọc từng khối 250,000 dòng).
   - **Kết quả:** Xác định chính xác $335$ ngày riêng biệt, Tháng 3 có $0$ dòng, 0 bất đồng tháng.
2. **Kiểm toán Toàn diện 8 Năm Trước 2016–2023 (`task-1007`):**
   - **Tệp nguồn:** 8 tệp CSV từ 2016 đến 2023 ($48,389,162$ dòng).
   - **Thời gian thực thi:** Đúng **$125.20$ giây** ($2.08$ phút).
   - **Mức tiêu thụ bộ nhớ:** Cố định dưới 50 MB RAM.
   - **Kết quả:** Khẳng định $100\%$ cả 8 năm đều đạt độ bao phủ lịch trọn vẹn $365$ hoặc $366$ ngày (chi tiết tại Mục 9).

---

## 9. Bảng Tổng hợp Độ bao phủ Lịch 9 Năm (2016–2024 Multi-Year Coverage Table)

Dưới đây là bảng tổng hợp kết quả kiểm chứng thực nghiệm tính liên tục lịch trên toàn bộ 9 tệp dữ liệu thô:

| Năm | Tổng Số Dòng Quan sát | Năm Nhuận? | Số Ngày Lịch Chuẩn | Số Ngày Quan sát Được | Số Ngày Khuyết Thiếu | Tỷ lệ Bao phủ Ngày | Đánh giá Tính Liên tục Lịch |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **2016** | $5,537,987$ | Có | $366$ | **$366$** | $0$ | $100.0\%$ | **FULL_COVERAGE (PASS)** |
| **2017** | $5,575,872$ | Không | $365$ | **$365$** | $0$ | $100.0\%$ | **FULL_COVERAGE (PASS)** |
| **2018** | $6,986,842$ | Không | $365$ | **$365$** | $0$ | $100.0\%$ | **FULL_COVERAGE (PASS)** |
| **2019** | $7,161,827$ | Không | $365$ | **$365$** | $0$ | $100.0\%$ | **FULL_COVERAGE (PASS)** |
| **2020** | $4,312,091$ | Có | $366$ | **$366$** | $0$ | $100.0\%$ | **FULL_COVERAGE (PASS)** |
| **2021** | $5,755,666$ | Không | $365$ | **$365$** | $0$ | $100.0\%$ | **FULL_COVERAGE (PASS)** |
| **2022** | $6,413,416$ | Không | $365$ | **$365$** | $0$ | $100.0\%$ | **FULL_COVERAGE (PASS)** |
| **2023** | $6,645,461$ | Không | $365$ | **$365$** | $0$ | $100.0\%$ | **FULL_COVERAGE (PASS)** |
| **2024** | $6,284,841$ | Có | $366$ | **$335$** | **$31$ (Tháng 3)** | **$91.53\%$** | **INCOMPLETE_COVERAGE (DEFECT)** |
| **TỔNG** | **$54,674,003$** | — | **$3,288$** | **$3,257$** | **$31$** | **$99.06\%$** | **DEFECT_LOCALIZED_TO_2024** |

> **Kết luận Khoa học:** Khiếm khuyết khuyết thiếu 31 ngày hoàn toàn cục bộ tại năm 2024. Toàn bộ 8 năm từ 2016 đến 2023 đều đạt độ bao phủ lịch $100\%$, không có bất kỳ khoảng trống ngày nào.

---

## 10. Đặc tả Bộ Fixture Thực thi Độc lập (TF-01 đến TF-09)

Để phục vụ kiểm thử tự động trong CI/CD và pipeline Apache Spark, ba tệp artifact kiểm chuẩn đã được ban hành độc lập tại thư mục `docs/05-evidence/`:

1. **Tệp CSV Chiếu Thời gian (18 cột — `TEMPORAL_TEST_PROJECTION`):** [`docs/05-evidence/T004_TF09_temporal_fixture.csv`](T004_TF09_temporal_fixture.csv)
   - Đúng **10 dòng vật lý** (1 header + 9 dòng dữ liệu `TF-01` đến `TF-09`).
   - Không chứa bất kỳ dòng chú thích nào bắt đầu bằng `#`.
   - Cung cấp đầy đủ 18 cột nghiệp vụ phục vụ kiểm chuẩn an toàn thời gian và trích xuất giờ `CRS_DEP_HOUR`.
2. **Tệp CSV Toàn Schema Ingestion (34 cột — `FULL_SCHEMA_INGESTION_FIXTURE`):** [`docs/05-evidence/T004_TF09_full_schema_fixture.csv`](T004_TF09_full_schema_fixture.csv)
   - Đúng **10 dòng vật lý** (1 header + 9 dòng dữ liệu `TF-01` đến `TF-09`).
   - Đúng chuẩn 34 cột dữ liệu tương thích hoàn hảo với schema nguồn của 9 năm thô, phục vụ kiểm thử nạp dữ liệu Spark.
3. **Tệp JSON Oracle Khẳng định Kiểm chuẩn:** [`docs/05-evidence/T004_TF09_temporal_fixture.json`](T004_TF09_temporal_fixture.json)
   - Chứa metadata đầy đủ, phân loại an toàn theo ma trận 4 cấp độ, mã IANA chuẩn (`America/Chicago`, `America/New_York`, `America/Los_Angeles`, `America/Phoenix`, `America/Denver`, `America/Anchorage`), cờ DST, và độ lệch múi giờ (*timezone offset*).
   - Chứa các khẳng định kiểm chuẩn toán học tự động (`expected_oracle_assertions`) về cân bằng độ trễ, phân rã thời gian cổng-đến-cổng, và cấm phép trừ chuỗi timestamp.

---

## 11. Tác động tới các Task Hạ nguồn (Downstream Impact Analysis)

1. **Đối với Task T-005 (Weather Usability Audit):**
   - Không bị ảnh hưởng tiêu cực bởi việc khuyết thiếu Tháng 3/2024 vì T-005 kiểm toán tính khả dụng và tính đồng bộ không gian/thời gian của 6 trường thời tiết. T-005 có toàn quyền đưa ra phán quyết `CONDITIONAL_GO` hoặc `CONDITIONAL_NO_GO`.
2. **Đối với Task T-006 (Architecture & Ingestion Design):**
   - Thiết kế ingestion phải sử dụng `to_date(FL_DATE)` làm partition key ngày dịch vụ, cấm trích xuất ngày từ `CRS_ARR_TIME` hoặc `ARR_TIME`.
   - Pipeline phải áp dụng parser an toàn cho `CRS_DEP_TIME` để trích xuất `CRS_DEP_HOUR`.
3. **Đối với Task T-007 & T-008 (Production Implementation & Core Analytics):**
   - Toàn bộ các công thức tính 8 CORE KPIs sử dụng trực tiếp các trường số thực phút (`DEP_DELAY`, `ARR_DELAY`, `TAXI_OUT`, `TAXI_IN`, `CRS_ELAPSED_TIME`, `ACTUAL_ELAPSED_TIME`, `AIR_TIME`).
   - Cấm hoàn toàn mọi phép trừ timestamp trong mã Spark production.
4. **Đối với Gate G2 Progression:**
   - Gate G2 được bảo toàn nguyên vẹn tính nghiêm ngặt: việc hoàn thành T-004-R1 giúp giải tỏa toàn bộ các nghi vấn về biểu diễn thời gian, nhưng **vẫn giữ Gate G2 ở trạng thái `IN_PROGRESS`** cho đến khi T-005 kết luận.

---

## 12. Bằng chứng Kiểm thử QA & Tính Nhất quán Cây Làm việc

Toàn bộ hệ thống kiểm tra tự động đã được thực thi và xác nhận:

1. **Script Kiểm tra Biểu diễn Thời gian T-004-R1:**
   - Lệnh thực thi: `python tools/qa/verify_t004_time_representation.py`
   - Kết quả: **PASS $100\%$** (toàn bộ 32 khẳng định kiểm tra đều đạt, bao gồm kiểm tra cấu trúc CSV 10 dòng, JSON oracle, các khẳng định múi giờ TF-06/TF-07, và phân định Section 2.3).
2. **Script Kiểm tra Tính Nhất quán Repository:**
   - Lệnh thực thi: `python tools/check_working_tree_consistency.py`
   - Kết quả: **PASS $100\%$** (88/88 khẳng định đạt, 0 lỗi, không có tệp thừa, PACKAGE_MANIFEST v1.1 bất biến).

---

## 13. Khuyến nghị Nghiệm thu & Cam kết Dừng lại Tuyệt đối

### Khuyến nghị Kỹ thuật
- Kính trình Reviewer phê duyệt hồ sơ nghiệm thu **Task T-004** với trạng thái **`READY_FOR_SIGNOFF_WITH_OPEN_DEFECT`** (bảo lưu rủi ro chất lượng mở `OR-05` cho Gate G3/G4).
- Duy trì Gate G2 ở trạng thái **`IN_PROGRESS / NOT_PASSED`**.
- Đề xuất nhiệm vụ tiếp theo: **Triển khai Task T-005 (Kiểm toán Khả năng Sử dụng Dữ liệu Thời tiết)**.

### Cam kết Dừng lại Tuyệt đối
- Nhóm kỹ sư **DỪNG LẠI HOÀN TOÀN TẠI ĐÂY**, không tự ý triển khai Task T-005 khi chưa có lệnh từ người phụ trách.
- Tuyệt đối không can thiệp, chỉnh sửa hay ghi đè vào 9 tệp dữ liệu thô tại `data/raw/tabular/`.
- Tuyệt đối không can thiệp vào các tệp manifest bất biến đã phát hành.
