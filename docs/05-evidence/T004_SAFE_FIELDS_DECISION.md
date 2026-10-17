# T-004: QUYẾT ĐỊNH PHÂN LOẠI TRƯỜNG THỜI GIAN VÀ CHỈ SỐ AN TOÀN (SAFE FIELDS & TEMPORAL USABILITY DECISION MATRIX)

- **Mã nhiệm vụ:** `T-004` (Sub-task 4: Safe Fields Classification & Architectural Decision)
- **Gate kiểm soát:** `G2` (Data Quality, Cohort & Metric Contracts)
- **Ngày ban hành:** 2026-10-14
- **Vai trò:** Senior Big Data Engineer, Data Architect & Quality Auditor
- **Trạng thái:** **`PROPOSED_FOR_REVIEWER_SIGNOFF`**
- **Văn bản tuân thủ:** [`AGENTS.md`](../../AGENTS.md), [`docs/01-planning/BACKLOG.md`](../01-planning/BACKLOG.md), [`docs/02-design/DATA_CONTRACT.md`](../02-design/DATA_CONTRACT.md), [`docs/02-design/DATA_DICTIONARY.md`](../02-design/DATA_DICTIONARY.md), [`docs/02-design/KPI_SPEC.md`](../02-design/KPI_SPEC.md), [`docs/02-design/DECISIONS.md`](../02-design/DECISIONS.md).

---

## 1. Mục đích & Nguyên tắc Quản trị Thời gian

Dựa trên kết quả kiểm toán từ [`T004_TIME_REPRESENTATION_AUDIT.md`](T004_TIME_REPRESENTATION_AUDIT.md) và [`T004_OVERNIGHT_COUNTEREXAMPLES.md`](T004_OVERNIGHT_COUNTEREXAMPLES.md), dự án ban hành ma trận phân loại an toàn cho toàn bộ các trường thời gian trong schema 34 cột.

Nguyên tắc quản trị cốt lõi:
1. **Bảo vệ tính toàn vẹn ngữ nghĩa:** Phân biệt rạch ròi giữa ngày lịch dịch vụ (*service date*), giờ đồng hồ địa phương (*local clock time*), và mốc thời gian vật lý toàn cục (*absolute timestamp*).
2. **Ngăn ngừa biến dạng số học:** Chặn đứng mọi nỗ lực trừ chuỗi timestamp trực tiếp hoặc tự ý cộng 24 giờ để "sửa" hiện tượng qua nửa đêm.
3. **Phân tầng mức độ an toàn:** Mọi trường dữ liệu và chỉ số phái sinh phải thuộc về một trong 4 cấp độ kiểm soát nghiêm ngặt.

---

## 2. Ma trận Phân loại An toàn 4 Cấp độ (4-Tier Usability Decision Matrix)

```text
+--------------------------------------------------------------------------------+
| TẦNG 1: SAFE_FOR_DIRECT_USE (Sử dụng trực tiếp không rủi ro)                   |
|   FL_DATE (service date), MONTH, DAY_OF_MONTH, DAY_OF_WEEK, 7 Thước đo số phút  |
+--------------------------------------------------------------------------------+
                                       |
+--------------------------------------------------------------------------------+
| TẦNG 2: SAFE_WITH_DOCUMENTED_TRANSFORMATION (Biến đổi an toàn có tài liệu hóa) |
|   CRS_DEP_TIME -> CRS_DEP_HOUR (0..23), time-of-day buckets (Morning/Evening)   |
+--------------------------------------------------------------------------------+
                                       |
+--------------------------------------------------------------------------------+
| TẦNG 3: CONDITIONALLY_USABLE (Sử dụng có điều kiện & cảnh báo)                  |
|   DEP_TIME, ARR_TIME, WHEELS_OFF, WHEELS_ON -> Chỉ phân tích giờ nội bộ sân bay  |
+--------------------------------------------------------------------------------+
                                       |
+--------------------------------------------------------------------------------+
| TẦNG 4: NOT_AVAILABLE / BLOCKED (Bị cấm hoặc không khả thi trong schema 34 cột)|
|   Timestamp trừ trực tiếp, Absolute Arrival Datetime (+24h), Flight Chain      |
+--------------------------------------------------------------------------------+
```

---

## 3. Đặc tả Chi tiết Từng Cấp độ An toàn

### 3.1. Cấp độ 1: `SAFE_FOR_DIRECT_USE` (An toàn cho Sử dụng Trực tiếp)

Các trường thuộc nhóm này đã được kiểm chứng độc lập về tính nguyên vẹn số học và ngữ nghĩa, được phép nạp trực tiếp vào các phép tính KPI, nhóm phân tích (*group-by*), và tổng hợp phân vị:

| Tên trường | Kiểu dữ liệu PySpark | Mục đích sử dụng an toàn & Ánh xạ KPI | Ranh giới & Điều kiện lưu ý |
|---|:---:|---|---|
| `FL_DATE` | `DateType` | Khóa phân vùng ngày, trục thời gian chính; xác định thuần tập accepted cho **`KPI-01`** ($\text{count\_records}(C)$). | Trích xuất bằng `to_date(FL_DATE)`. Được hiểu là **Ngày Dịch vụ Lịch trình (*Scheduled Service Date*)**, không khẳng định là ngày đến nơi. |
| `MONTH` | `IntegerType` | Phân tích xu hướng theo mùa (*seasonal trend*), nhóm theo quý. | Cần lưu ý Tháng 3/2024 có $0$ bản ghi ([`T004_2024_DATE_COVERAGE_AUDIT.md`](T004_2024_DATE_COVERAGE_AUDIT.md)). |
| `DAY_OF_MONTH` | `IntegerType` | Phân tích biến thiên theo ngày trong tháng ($1..31$). | Phân tích phân bố nội tháng. |
| `DAY_OF_WEEK` | `IntegerType` | Phân tích chu kỳ tuần ($1..7$, $1 = \text{Thứ Hai}$). | Đo lường hiệu suất ngày thường vs cuối tuần. |
| `ARR_DELAY` | `DoubleType` | Thước đo cốt lõi cho **`KPI-02`** (Tỷ lệ trễ đến $\ge 15$), **`KPI-03`** (Trễ đến trung bình có dấu), và **`KPI-06`** (P50/P90 trễ đến). | Giữ nguyên dấu âm ($< 0$ là đến sớm). Đơn vị phút. |
| `DEP_DELAY` | `DoubleType` | Thước đo cốt lõi cho **`KPI-04`** (Tỷ lệ trễ đi $\ge 15$), và **`KPI-05`** (Trễ đi trung bình có dấu). | Giữ nguyên dấu âm ($< 0$ là khởi hành sớm). Đơn vị phút. |
| `TAXI_OUT` | `DoubleType` | Thước đo thời gian lăn cất cánh cho **`KPI-07`**. | Đơn vị phút, $\text{TAXI\_OUT} \ge 0.0$. |
| `TAXI_IN` | `DoubleType` | Thước đo thời gian lăn cập cổng cho **`KPI-07`**. | Đơn vị phút, $\text{TAXI\_IN} \ge 0.0$. |
| `AIR_TIME` | `DoubleType` | Thước đo thời gian bay trên không cho **`KPI-08`**. | Đơn vị phút, bắt buộc $\text{AIR\_TIME} > 0.0$. |
| `ACTUAL_ELAPSED_TIME` | `DoubleType` | Tổng thời gian hành trình thực tế cho **`KPI-08`**. | Đơn vị phút, $\text{ACTUAL} \equiv \text{TAXI\_OUT} + \text{AIR} + \text{TAXI\_IN}$. |
| `CRS_ELAPSED_TIME` | `DoubleType` | Thời gian hành trình kế hoạch cho **`KPI-08`**. | Đơn vị phút, công bố từ lịch trình của hãng. |


---

### 3.2. Cấp độ 2: `SAFE_WITH_DOCUMENTED_TRANSFORMATION` (An toàn Qua Biến đổi Chuẩn hóa)

Các trường thuộc nhóm này không được dùng nguyên trạng toàn phần (chuỗi datetime đầy đủ), nhưng được phép trích xuất các đặc trưng giờ/phút theo các biểu thức chuẩn hóa đã kiểm thử:

| Trường nguồn | Trường phái sinh | Biểu thức PySpark chuẩn hóa | Phạm vi áp dụng & Mục đích |
|---|---|---|---|
| `CRS_DEP_TIME` | `CRS_DEP_HOUR` | `hour(to_timestamp(col("CRS_DEP_TIME")))` | Trích xuất giờ kế hoạch khởi hành ($0..23$). Dùng phân tích hiệu suất theo khung giờ khởi hành trong ngày. Giờ mang ngữ nghĩa giờ địa phương sân bay đi (*local departure time*). |
| `CRS_DEP_TIME` | `DEP_TIME_OF_DAY` | Phân đoạn theo giờ:<br>- `06..11`: Sáng (*Morning*)<br>- `12..17`: Chiều (*Afternoon*)<br>- `18..23`: Tối (*Evening*)<br>- `00..05`: Đêm (*Night*) | Phân cụm mô tả hoạt động vận hành để so sánh độ trễ giữa các khung giờ trong ngày. |
| `CRS_DEP_TIME` | `CRS_DEP_MINUTE` | `minute(to_timestamp(col("CRS_DEP_TIME")))` | Phân tích hành vi xếp lịch theo phút (ví dụ gom lịch vào phút :00, :15, :30, :45). |

> [!CAUTION]
> **Hạn chế Nghiêm ngặt:**
> - Tuyệt đối không trích xuất ngày từ `CRS_ARR_TIME` để làm trục thời gian đến.
> - Thành phần ngày của `CRS_ARR_TIME` bị upstream ETL kẹp cố định bằng `FL_DATE`.

---

### 3.3. Cấp độ 3: `CONDITIONALLY_USABLE` (Sử dụng Có Điều kiện & Cảnh báo)

Bao gồm các trường thời gian vận hành thực tế: `DEP_TIME`, `ARR_TIME`, `WHEELS_OFF`, `WHEELS_ON`.

- **Điều kiện được phép sử dụng:**
  1. Chỉ được trích xuất thành phần giờ (`hour(...)`) để phân tích phân bổ mật độ cất/hạ cánh thực tế tại từng sân bay cụ thể (ví dụ: giờ cao điểm hạ cánh thực tế tại sân bay ORD).
  2. Phải kèm theo nhãn cảnh báo: `"LOCAL_CLOCK_HOUR_ONLY (NO_ABSOLUTE_ORDERING)"`.
- **Hành vi BỊ CẤM đối với nhóm này:**
  1. Cấm dùng để sắp xếp thứ tự thời gian toàn cục giữa các sân bay thuộc múi giờ khác nhau (ví dụ: so sánh mốc 14:00 tại JFK với 12:00 tại LAX mà không có timezone offset).
  2. Cấm dùng trong các phép trừ giữa các cột với nhau để tính toán độ trễ hoặc thời lượng.

---

### 3.4. Cấp độ 4: `NOT_AVAILABLE / BLOCKED` (Bị Khóa Hoàn toàn Ngoài Phạm vi)

Các tính năng và trường hợp sau đây bị khóa vĩnh viễn trong phạm vi đồ án:

1. **Phép trừ chuỗi Timestamp trực tiếp (*Direct Timestamp Subtraction*):**
   - Trạng thái: **`BLOCKED / FORBIDDEN`**.
   - Lý do: Gây ra sai số đến 1440 phút (24 giờ) hoặc cho ra độ trễ âm vô lý như đã chứng minh ở phản ví dụ YX 3624.
2. **Tự động cộng 24 giờ để tạo mốc đến thực tế (*Synthetic +24h Datetime*):**
   - Trạng thái: **`BLOCKED / REJECTED`**.
   - Lý do: Quy tắc chắp vá ngây thơ (*naive heuristic*) không chứng minh được chuyến bay trễ 1 ngày hay nhiều ngày, không xử lý được chênh lệch múi giờ.
3. **Chuỗi chuyến bay máy bay quay vòng (*Aircraft Flight Chain Reconstruction*):**
   - Trạng thái: **`FINAL — NO_GO`**.
   - Lý do: Schema 34 cột thiếu trường số hiệu đuôi tàu bay (`TAIL_NUM`), không có mã chuyến bay duy nhất, và thiếu múi giờ IANA.
4. **Chỉ số Hủy chuyến và Chuyển hướng (`KPI-11: CANCELLATION_DIVERSION_RATE`):**
   - Trạng thái: **`BLOCKED / NOT_COMPUTABLE`**.
   - Lý do: Schema 34 cột hoàn toàn thiếu hai cột `CANCELLED` và `DIVERTED`. `KPI-11` chính thức nằm ngoài 8 CORE KPIs.

---

## 4. Bảng Tra cứu Tổng hợp 34 Cột theo Nhãn An toàn

| Phân loại | Số lượng cột | Danh sách các cột trong Schema 34 cột |
|---|:---:|---|
| **`SAFE_FOR_DIRECT_USE`** | **17 cột** | `FL_DATE`, `OP_CARRIER`, `OP_CARRIER_FL_NUM`, `ORIGIN`, `DEST`, `MONTH`, `DAY_OF_MONTH`, `DAY_OF_WEEK`, `ORIGIN_INDEX`, `DEST_INDEX`, `ARR_DELAY`, `DEP_DELAY`, `TAXI_OUT`, `TAXI_IN`, `AIR_TIME`, `ACTUAL_ELAPSED_TIME`, `CRS_ELAPSED_TIME`. |
| **`SAFE_WITH_DOCUMENTED_TRANSFORMATION`** | **2 cột** | `CRS_DEP_TIME` (cho `CRS_DEP_HOUR`), `CRS_ARR_TIME` (cho `CRS_ARR_HOUR` với cảnh báo giờ địa phương). |
| **`CONDITIONALLY_USABLE`** | **10 cột** | `DEP_TIME`, `ARR_TIME`, `WHEELS_OFF`, `WHEELS_ON` (chỉ dùng local hour); 6 trường thời tiết (`O_TEMP`, `O_PRCP`, `O_WSPD`, `D_TEMP`, `D_PRCP`, `D_WSPD` — chuyển giao T-005). |
| **`STATIC_COORDINATES`** | **4 cột** | `O_LATITUDE`, `O_LONGITUDE`, `D_LATITUDE`, `D_LONGITUDE` (Tọa độ địa lý cố định, an toàn cho hiển thị bản đồ). |
| **`REDUNDANT_BLOCKED`** | **1 cột** | `FLIGHTS` (100% bằng 1.0, cấm làm mẫu số; `KPI-12` bị khóa). |
| **Tổng cộng** | **34 cột** | Phân loại toàn diện 100% schema |

---

## 5. Kết luận Điều hành

Quyết định phân loại này cung cấp ranh giới kỹ thuật bất biến (*immutable technical boundary*) cho toàn bộ giai đoạn thiết kế kiến trúc (G3) và viết mã pipeline nạp dữ liệu (G4). Mọi đoạn mã vi phạm quy tắc an toàn thời gian trên sẽ bị bộ kiểm thử chặn đứng.
