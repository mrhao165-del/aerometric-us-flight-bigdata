# T-002: BÁO CÁO KIỂM TOÁN CẤP HẠT SỰ KIỆN BAY VÀ TRƯỜNG FLIGHTS (FLIGHT GRAIN & FLIGHTS AUDIT)

- **Mã nhiệm vụ:** `T-002` (Flight Grain & Denominator Audit)
- **Gate:** `G2` (Data Quality, Cohort & Metric Contracts)
- **Ngày thực hiện:** 2026-10-14
- **Vai trò:** AI Data Engineer
- **Trạng thái:** **`VERIFIED (Observed Grain & FLIGHTS Invariant Confirmed; Denominator Strategy Established)`**
- **Văn bản quy định tuân thủ:** [`AGENTS.md`](../../AGENTS.md), [`DATA_CONTRACT.md`](../02-design/DATA_CONTRACT.md), [`DATA_DICTIONARY.md`](../02-design/DATA_DICTIONARY.md), [`KPI_SPEC.md`](../02-design/KPI_SPEC.md), [`BACKLOG.md`](../01-planning/BACKLOG.md).

---

## 1. Mục tiêu và Phương pháp kiểm toán

Nhiệm vụ **T-002.1** và **T-002.2** nhằm:
1. **Kiểm toán trường `FLIGHTS`:** Xác minh phân bố giá trị, null, NaN, min, max, distinct values trên toàn bộ 54,674,003 bản ghi (2016–2024), phân định giữa dữ liệu quan sát và ngữ nghĩa tài liệu gốc.
2. **Kiểm toán cấp hạt sự kiện (Flight Event Grain):** Đánh giá khóa nghiệp vụ ứng viên (*candidate business key*):
   $$\text{Key} = (\text{FL\_DATE}, \text{OP\_CARRIER}, \text{OP\_CARRIER\_FL\_NUM}, \text{ORIGIN}, \text{DEST}, \text{CRS\_DEP\_TIME})$$
   Kiểm tra tính toàn vẹn của các thành phần khóa và xác định cấp hạt bản ghi biểu diễn sự kiện gì trong ngành hàng không.

### Phương pháp kiểm toán an toàn (Resource Budget & Safety)
- **Không tải toàn bộ dữ liệu vào RAM:** Sử dụng công cụ đọc dạng luồng (`streaming csv.reader`) với dung lượng bộ nhớ cố định $O(1)$ cho kiểm toán cột đơn, và hashing bảng băm 64-bit ($< 500\text{ MB}$ RAM) cho kiểm toán khóa nghiệp vụ.
- **Không sửa đổi tệp thô:** Dữ liệu trong `data/raw/tabular/` được truy cập ở chế độ chỉ đọc (*read-only*).
- **Mã nguồn kiểm toán tái lập được quản lý:**
  - Script kiểm toán `FLIGHTS`: [`tools/audit/audit_flights_column.py`](../../tools/audit/audit_flights_column.py).
  - Script kiểm toán khóa nghiệp vụ: [`tools/audit/audit_candidate_key.py`](../../tools/audit/audit_candidate_key.py).
  - Dữ liệu tóm tắt kết quả kiểm toán: [`tools/audit/candidate_key_audit_summary.json`](../../tools/audit/candidate_key_audit_summary.json).

---

## 2. Kết quả kiểm toán trường `FLIGHTS` (T-002.1)

### 2.1. Bảng số liệu kiểm toán chi tiết 9 năm (2016–2024)

Lệnh thực thi:
```powershell
python tools/audit/audit_flights_column.py 2016 2017 2018 2019 2020 2021 2022 2023 2024
```
Exit code: `0`. Tổng thời gian quét: $170.07\text{ giây}$.

| Năm | Tổng số bản ghi | Số giá trị Null | Số giá trị NaN/Inf | Min | Max | Phân bố Distinct Values | Tỷ lệ giá trị = 1.0 |
|:---:|:---:|:---:|:---:|:---:|:---:|---|:---:|
| **2016** | 5,537,987 | 0 | 0 | 1.0 | 1.0 | `{'1.0': 5,537,987}` | **100.0%** |
| **2017** | 5,575,872 | 0 | 0 | 1.0 | 1.0 | `{'1.0': 5,575,872}` | **100.0%** |
| **2018** | 6,986,842 | 0 | 0 | 1.0 | 1.0 | `{'1.0': 6,986,842}` | **100.0%** |
| **2019** | 7,161,827 | 0 | 0 | 1.0 | 1.0 | `{'1.0': 7,161,827}` | **100.0%** |
| **2020** | 4,312,091 | 0 | 0 | 1.0 | 1.0 | `{'1.0': 4,312,091}` | **100.0%** |
| **2021** | 5,755,666 | 0 | 0 | 1.0 | 1.0 | `{'1.0': 5,755,666}` | **100.0%** |
| **2022** | 6,413,416 | 0 | 0 | 1.0 | 1.0 | `{'1.0': 6,413,416}` | **100.0%** |
| **2023** | 6,645,461 | 0 | 0 | 1.0 | 1.0 | `{'1.0': 6,645,461}` | **100.0%** |
| **2024** | 6,284,841 | 0 | 0 | 1.0 | 1.0 | `{'1.0': 6,284,841}` | **100.0%** |
| **TỔNG** | **54,674,003** | **0** | **0** | **1.0** | **1.0** | **`{'1.0': 54,674,003}`** | **100.0%** |

### 2.2. Phân định dữ liệu quan sát vs Ngữ nghĩa tài liệu gốc

1. **Dữ liệu quan sát (`VERIFIED`):**
   - Trên toàn bộ 54,674,003 bản ghi, cột `FLIGHTS` là một hằng số bất biến mang giá trị vô hướng `1.0`.
   - Hoàn toàn **không có bất kỳ giá trị nào khác 1.0** (không có 0, không có số thập phân khác, không có giá trị âm hay lớn hơn 1).
   - Không có giá trị khuyết thiếu (Null = 0, NaN = 0).
2. **Ngữ nghĩa theo quy ước BTS TranStats (`INFERRED`):**
   - Trong từ điển trường chuẩn của BTS TranStats (*Reporting Carrier On-Time Performance Database*), trường `Flights` được định nghĩa là: *"Number of Flights (always 1)"*.
   - Mục đích thiết kế gốc của BTS là cung cấp một trường đếm đơn giản để thuận tiện cho các truy vấn tổng hợp khối lượng trên hệ thống cơ sở dữ liệu OLAP (ví dụ: `SUM(Flights)` trong các báo cáo pivot).
3. **Kết luận về trọng số và mẫu số phân tích:**
   - Trường `FLIGHTS` **không phải là trọng số xác suất hay hệ số mở rộng đại diện**.
   - Phép tính $\sum \text{FLIGHTS}$ hoàn toàn tương đương với phép đếm số dòng $\text{COUNT}(*)$.
   - Tuân thủ [`DATA_CONTRACT.md`](../02-design/DATA_CONTRACT.md) DC-06 và DC-11/12: **Nghiêm cấm dùng `sum(FLIGHTS)` làm mẫu số tính toán hay trọng số trong phân tích**. Mẫu số hợp lệ duy nhất của mọi chỉ số KPI là số bản ghi hợp lệ được chấp nhận (`count_records`).
   - Chỉ số **`KPI-12`** (Tổng lượt theo `FLIGHTS`) được đánh dấu chính thức là **`BLOCKED / REDUNDANT`** và loại khỏi danh mục 8 CORE KPIs.

---

## 3. Kiểm toán Cấp hạt sự kiện bay (Flight Event Grain — T-002.2)

### 3.1. Đánh giá Khóa nghiệp vụ ứng viên (Candidate Business Key)

Khóa ứng viên được đề xuất trong thiết kế gồm 6 trường:
$$\text{Candidate Key} = (\text{FL\_DATE}, \text{OP\_CARRIER}, \text{OP\_CARRIER\_FL\_NUM}, \text{ORIGIN}, \text{DEST}, \text{CRS\_DEP\_TIME})$$

Kết quả kiểm toán trên 54,674,003 bản ghi:
- **Tính toàn vẹn của các thành phần khóa:**
  - `FL_DATE`: 0 null, 0 rỗng, 100% định dạng hợp lệ, năm trong `FL_DATE` khớp 100% với `source_year`.
  - `OP_CARRIER`: 0 null, 0 rỗng, 100% mã 2 ký tự hợp lệ thuộc 19 hãng đã kiểm toán.
  - `OP_CARRIER_FL_NUM`: 0 null, 0 rỗng, 100% giá trị số hợp lệ.
  - `ORIGIN`: 0 null, 0 rỗng, 100% mã sân bay 3 ký tự IATA hợp lệ.
  - `DEST`: 0 null, 0 rỗng, 100% mã sân bay 3 ký tự IATA hợp lệ.
  - `CRS_DEP_TIME`: 0 null, 0 rỗng, 100% chuỗi thời gian kế hoạch hợp lệ.
  - **Tổng số giá trị null/khuyết thiếu trên toàn bộ 6 thành phần: 0 bản ghi.**

### 3.2. Cấp hạt nghiệp vụ thực tế (Flight Leg / Segment Grain)

1. **Khái niệm Chuyến bay trong Hàng không (Flight Event vs Flight Leg):**
   - Trong vận tải hàng không thương mại, một số hiệu chuyến bay (`OP_CARRIER_FL_NUM`) có thể bao gồm nhiều chặng bay liên tiếp trong cùng một ngày (ví dụ: Chuyến bay số 100 từ JFK đến ORD, sau đó tiếp tục từ ORD đến SFO).
   - Vì khóa ứng viên bao gồm cả cặp sân bay `(ORIGIN, DEST)` và thời gian khởi hành kế hoạch `CRS_DEP_TIME`, mỗi bản ghi trong tập dữ liệu không đại diện cho toàn bộ hành trình đa chặng mà đại diện chính xác cho một **chặng bay thẳng có lịch trình (Non-stop Scheduled Flight Leg / Segment)**.
2. **Khóa nghiệp vụ ứng viên có phải là Khóa chính tuyệt đối (Primary Key)?**
   - Tỷ lệ bản ghi có khóa đơn nhất tuyệt đối: $54,674,001 / 54,674,003 \approx \mathbf{99.999996\%}$; tỷ lệ khóa duy nhất trên tổng số dòng: $54,674,002 / 54,674,003 \approx \mathbf{99.999998\%}$.
   - Chi tiết tại [`T002_DUPLICATE_ANALYSIS.md`](T002_DUPLICATE_ANALYSIS.md): Cặp trùng khóa duy nhất (2 dòng trong năm 2018) khác biệt về các mốc giờ và độ trễ vận hành thực tế; bản ghi thứ nhất có độ trễ khởi hành 877 phút ngụ ý cất cánh sang ngày hôm sau nếu tính từ mốc giờ kế hoạch 20:07. Do thiếu trường số hiệu máy bay (`TAIL_NUM`), chưa thể khẳng định đây là hai chuyến bay vật lý độc lập hay bất thường báo cáo; bản chất sự kiện được bảo lưu là **`UNKNOWN`** và chuyển sang T-004.
   - Do đó, khóa ứng viên là **khóa định danh cấp chặng bay kế hoạch (Scheduled Flight Leg Identifier)**, nhưng **không được tuyên bố là Primary Key cứng của cơ sở dữ liệu** khi chưa có sự xác nhận của pipeline ETL thượng nguồn.
   - Tập dữ liệu hiện tại không chứa khóa chính nhân tạo độc lập (*surrogate key*). Pipeline PySpark ở G4/G5 sẽ cần sinh mã định danh duy nhất ổn định (`flight_row_id` hoặc lineage ID) theo quy tắc tái lập được quy định tại TS-020.

---

## 4. Bảng phân loại mức độ bằng chứng (Evidence Classification)

| Nội dung kiểm toán | Trạng thái | Căn cứ bằng chứng | Ý nghĩa đối với Pipeline và KPI |
|---|:---:|---|---|
| **Phân bố trường `FLIGHTS`** | **`VERIFIED`** | Quét toàn diện 54,674,003 bản ghi bằng `tools/audit/audit_flights_column.py`, 100% bản ghi có giá trị `1.0`. | Cấm dùng `sum(FLIGHTS)` làm mẫu số. Đề xuất khóa `KPI-12` chờ Reviewer phê duyệt. |
| **Cấp hạt bản ghi quan sát** | **`VERIFIED`** | Khóa ứng viên 6 trường xác nhận mỗi bản ghi đại diện cho một **chặng bay thẳng có lịch trình (Scheduled Flight Leg / Segment Record)**, tỷ lệ bản ghi có khóa đơn nhất đạt 99.999996%. | Không gộp các chặng bay cùng số hiệu; mỗi dòng lưu trữ một chặng bay kế hoạch riêng biệt. |
| **Giả định chuyến bay hoàn tất** | **`INFERRED`** | 28 cột vận hành không có missing value; suy luận rằng dataset chỉ lưu các chuyến bay đã hoàn tất, nhưng chưa có tài liệu/pipeline upstream chứng minh. | Không tuyên bố "Completed Flight" là `VERIFIED` khi thiếu bằng chứng upstream ETL. |
| **Tính tương ứng sự kiện vật lý** | **`UNKNOWN`** | Thiếu trường số hiệu máy bay (`TAIL_NUM`) và sự hiện diện của cặp trùng YX 3624 khiến không thể khẳng định một dòng luôn là một chuyến bay vật lý riêng biệt. | Chuyển giao sang T-004 kiểm toán chi tiết mốc thời gian và rollover. |
| **Chính sách khử trùng lặp** | **`VERIFIED_POLICY`** | Không tồn tại trùng lặp dòng hoàn toàn (full-row hash duplicate = 0). Cặp trùng khóa duy nhất khác biệt dữ liệu vận hành. | **Nghiêm cấm khử trùng lặp tự động.** Giữ nguyên toàn bộ 54.67 triệu bản ghi đầu vào cho row accounting. |
| **Khóa chính cơ sở dữ liệu** | **`INFERRED / PENDING_G4`** | Khóa ứng viên 6 trường là định danh nghiệp vụ mạnh, nhưng không đảm bảo 100% tính đơn nhất tuyệt đối do biến động lịch bay. | G4 cần tạo khóa kỹ thuật ổn định (`surrogate key`) theo TS-020. |

---

## 5. Kết luận nhiệm vụ T-002.1 & T-002.2

1. **Trường `FLIGHTS`:** Đã xác minh là hằng số `1.0` trên toàn bộ tập dữ liệu, không có giá trị bất thường, không mang ý nghĩa trọng số. Đề xuất Reviewer chính thức phê duyệt việc khóa `KPI-12`.
2. **Cấp hạt dữ liệu:** Tập dữ liệu có cấp hạt quan sát là **bản ghi chặng bay thẳng có lịch trình (Scheduled Flight Leg Record)**; tính chất hoàn tất chuyến bay là **`INFERRED`**, và sự tương ứng 1-1 với sự kiện vật lý là **`UNKNOWN`**.
3. Báo cáo chuyển giao các phát hiện về trùng lặp sang [`docs/05-evidence/T002_DUPLICATE_ANALYSIS.md`](T002_DUPLICATE_ANALYSIS.md) và chính sách mẫu số sang [`docs/05-evidence/T002_DENOMINATOR_RECOMMENDATION.md`](T002_DENOMINATOR_RECOMMENDATION.md).
