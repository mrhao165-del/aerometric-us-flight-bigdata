# T-004: BÁO CÁO PHÂN TÍCH HIỆN TƯỢNG BAY QUA NỬA ĐÊM VÀ PHẢN VÍ DỤ KINH ĐIỂN YX 3624 (OVERNIGHT FLIGHTS & MIDNIGHT ROLLOVER COUNTEREXAMPLES)

- **Mã nhiệm vụ:** `T-004` (Sub-task 3: Overnight Operations, Rollover & YX 3624 Analysis)
- **Gate kiểm soát:** `G2` (Data Quality, Cohort & Metric Contracts)
- **Ngày thực hiện:** 2026-10-14
- **Vai trò:** Senior Data Engineer, Big Data Quality Auditor & Technical Reviewer
- **Trạng thái:** **`AUDIT_COMPLETE / MATHEMATICALLY_PROVEN`**
- **Văn bản tuân thủ:** [`AGENTS.md`](../../AGENTS.md), [`docs/01-planning/BACKLOG.md`](../01-planning/BACKLOG.md), [`docs/02-design/DATA_CONTRACT.md`](../02-design/DATA_CONTRACT.md), [`docs/02-design/DECISIONS.md`](../02-design/DECISIONS.md), [`docs/03-quality/TEST_PLAN.md`](../03-quality/TEST_PLAN.md) (`TS-010`, `TS-020`, `TS-021`).

---

## 1. Bối cảnh & Mục tiêu Nghiên cứu

Trong kỹ thuật xử lý dữ liệu hàng không, hiện tượng chuyến bay vượt qua mốc nửa đêm (*midnight rollover*) xảy ra ở hai kịch bản chính:
1. **Bay đêm theo kế hoạch (*Scheduled Overnight / Red-Eye Flights*):** Chuyến bay được lên lịch cất cánh vào đêm muộn hôm trước và hạ cánh vào sáng sớm ngày hôm sau (ví dụ: các chuyến bay xuyên lục địa bờ Tây sang bờ Đông như LAX $\to$ JFK, SEA $\to$ MIA).
2. **Bay đêm do trễ chuyến vận hành (*Operational Delay Rollover*):** Chuyến bay ban đầu được lên kế hoạch trong ngày, nhưng do thời tiết hoặc kỹ thuật bị trễ nghiêm trọng và chỉ có thể cất cánh/hạ cánh sau nửa đêm sang ngày hôm sau.

Hồ sơ này mổ xẻ cơ chế lưu trữ chuỗi thời gian của upstream ETL, phân tích phản ví dụ kinh điển **`YX 3624`**, và chứng minh bằng toán học tại sao việc trừ trực tiếp các chuỗi timestamp sẽ dẫn đến sai số thảm họa.

---

## 2. Phân tích Chi tiết Phản ví dụ Kinh điển YX 3624 (2018-06-21 DEN $\to$ XNA)

Trong tệp dữ liệu thô `data/raw/tabular/2018/flight_with_weather_2018.csv`, tại các dòng vật lý **6,384,132** và **6,384,133**, tồn tại một cặp bản ghi trùng khóa 6 trường (`FL_DATE`, `OP_CARRIER`, `OP_CARRIER_FL_NUM`, `ORIGIN`, `DEST`, `CRS_DEP_TIME`).

### 2.1. Bảng Trích xuất Nguyên bản 34 Cột của Cặp Dòng YX 3624:

| Thuộc tính / Cột dữ liệu | Bản ghi A (Dòng vật lý 6,384,132) | Bản ghi B (Dòng vật lý 6,384,133) | Chênh lệch Số học ($A - B$) |
|---|:---:|:---:|:---:|
| `FL_DATE` | `2018-06-21 00:00:00` | `2018-06-21 00:00:00` | $0$ (Cùng ngày dịch vụ) |
| `OP_CARRIER` | `YX` (Republic Airways) | `YX` (Republic Airways) | Giống nhau |
| `OP_CARRIER_FL_NUM` | `3624.0` | `3624.0` | Giống nhau |
| `ORIGIN` / `DEST` | `DEN` $\to$ `XNA` | `DEN` $\to$ `XNA` | Tuyến Denver $\to$ Arkansas |
| `CRS_DEP_TIME` | `2018-06-21 20:07:00` | `2018-06-21 20:07:00` | $0$ (Cùng giờ dự kiến 20:07) |
| `CRS_ARR_TIME` | `2018-06-21 23:05:00` | `2018-06-21 23:05:00` | $0$ (Cùng giờ dự kiến 23:05) |
| `CRS_ELAPSED_TIME` | `118.0` phút | `118.0` phút | $0$ (Kế hoạch: 1h58m) |
| **`DEP_TIME`** | **`2018-06-21 10:44:00`** | **`2018-06-21 20:27:00`** | **Chuỗi giờ lệch nhau** |
| **`ARR_TIME`** | **`2018-06-21 14:46:00`** | **`2018-06-21 23:09:00`** | **Chuỗi giờ lệch nhau** |
| **`DEP_DELAY`** | **`+877.0` phút** | **`+20.0` phút** | **$+857.0$ phút (14h 17m)** |
| **`ARR_DELAY`** | **`+941.0` phút** | **`+4.0` phút** | **$+937.0$ phút (15h 37m)** |
| `TAXI_OUT` | `91.0` phút | `13.0` phút | $+78.0$ phút (Kẹt sân DEN) |
| `AIR_TIME` | `84.0` phút | `83.0` phút | $+1.0$ phút |
| `TAXI_IN` | `7.0` phút | `6.0` phút | $+1.0$ phút |
| `ACTUAL_ELAPSED_TIME` | `182.0` phút | `102.0` phút | $+80.0$ phút |

---

### 2.2. Kiểm chứng Tính Nhất quán Số học Nội tại của Từng Bản ghi

#### Đối với Bản ghi B (Dòng 6,384,133 — Chuyến bay Vận hành Bình thường):
1. **Kiểm tra khởi hành:**
   - Dự kiến: $20:07$. Thực tế: $20:27$.
   - $\text{DEP\_TIME} - \text{CRS\_DEP\_TIME} = 20\text{ phút} = \text{DEP\_DELAY}$ ($+20.0$).
2. **Kiểm tra thời gian hành trình thực tế:**
   - $\text{TAXI\_OUT} + \text{AIR\_TIME} + \text{TAXI\_IN} = 13.0 + 83.0 + 6.0 = 102.0\text{ phút} \equiv \text{ACTUAL\_ELAPSED\_TIME}$ ($102.0$).
3. **Kiểm tra đến nơi:**
   - Dự kiến: $23:05$. Thực tế: $23:09$.
   - $\text{ARR\_TIME} - \text{CRS\_ARR\_TIME} = 4\text{ phút} = \text{ARR\_DELAY}$ ($+4.0$).
4. **Kiểm tra cân bằng độ trễ:**
   - $\text{DEP\_DELAY} + (\text{ACTUAL} - \text{CRS}) = 20.0 + (102.0 - 118.0) = 20.0 - 16.0 = 4.0 \equiv \text{ARR\_DELAY}$ ($+4.0$).
$\implies$ **Bản ghi B là một chuyến bay đúng lịch trình thông thường vào tối ngày 21/06/2018 (chỉ trễ 20 phút do lăn cất cánh).**

---

#### Đối với Bản ghi A (Dòng 6,384,132 — Chuyến bay Trễ Cực đoan Lăn qua Ngày Hôm sau):
1. **Kiểm tra thời gian hành trình thực tế:**
   - $\text{TAXI\_OUT} + \text{AIR\_TIME} + \text{TAXI\_IN} = 91.0 + 84.0 + 7.0 = 182.0\text{ phút} \equiv \text{ACTUAL\_ELAPSED\_TIME}$ ($182.0$).
2. **Kiểm tra cân bằng độ trễ:**
   - $\text{DEP\_DELAY} + (\text{ACTUAL} - \text{CRS}) = 877.0 + (182.0 - 118.0) = 877.0 + 64.0 = 941.0 \equiv \text{ARR\_DELAY}$ ($+941.0$).
   - Số học hoàn toàn khớp chính xác tuyệt đối $100.0\%$.

---

### 2.3. Phân định Ranh giới Khoa học về Bản chất Dữ liệu YX 3624 (F02 Scientific Classification)

Dự án phân định minh bạch ba tầng chứng cứ đối với cặp bản ghi YX 3624:

1. **Tầng VERIFIED (Bằng chứng Thực nghiệm Trực tiếp từ CSV thô):**
   - Tồn tại hai dòng vật lý riêng biệt tại vị trí 6,384,132 và 6,384,133 trong tệp `flight_with_weather_2018.csv`.
   - Cả hai dòng đều có 34 cột số liệu hợp lệ, thỏa mãn $100\%$ các đẳng thức số học nội tại của BTS.
   - Bản ghi A có $\text{DEP\_DELAY} = +877.0$ phút và $\text{ARR\_DELAY} = +941.0$ phút.
   - Chuỗi timestamp lưu trữ tại Bản ghi A ghi nhận `DEP_TIME = "2018-06-21 10:44:00"`.
   - Phép trừ chuỗi timestamp trực tiếp giữa `DEP_TIME` và `CRS_DEP_TIME` trên Bản ghi A cho ra giá trị âm $-563$ phút, sai lệch đúng $\mathbf{1440\text{ phút}}$ ($24$ giờ) so với giá trị chính thức $\text{DEP\_DELAY} = +877.0$ phút.

2. **Tầng INFERRED (Giả thuyết Suy luận Thời gian):**
   - Về mặt thời gian vận hành: Nếu độ trễ chính thức là $+877.0$ phút ($14$ giờ $37$ phút), mốc cất cánh vật lý tương ứng phải là **10:44 sáng ngày hôm sau (22/06/2018)** ($20:07 + 14\text{h }37\text{m}$).
   - Do đó, thành phần ngày `2018-06-21` trong chuỗi timestamp của Bản ghi A được suy luận là hệ quả của việc kẹp ngày dịch vụ (`FL_DATE`) vào giờ thực tế khi bảng dữ liệu dẫn xuất được tạo lập.
   - **Lưu ý khoa học:** Đây là suy luận dựa trên sự nhất quán giữa độ trễ và giờ đồng hồ, không phải là phát biểu về toàn bộ 54.67 triệu dòng.

3. **Tầng UNKNOWN (Ranh giới Giới hạn Khoa học):**
   - **Mã nguồn Upstream ETL:** Đồ án không sở hữu mã nguồn ETL gốc của bên thứ ba, do đó nguyên nhân kỹ thuật cụ thể tạo ra chuỗi ngày này được phân loại là **`UPSTREAM_CODE_UNKNOWN`**.
   - **Bản chất Thực thể Vật lý:** Do schema 34 cột không chứa số hiệu đuôi tàu bay (`TAIL_NUM`), không có chứng thực độc lập để khẳng định Bản ghi A và Bản ghi B là hai chuyến bay vật lý riêng biệt, một chuyến bay bị dời lịch (*rescheduled leg*), hay là lỗi truyền trùng bản ghi (*dual-transmission*). Trạng thái thực thể vật lý là **`PHYSICAL_EVENT_IDENTITY_UNKNOWN`**.
   - Không được tự ý ngoại suy rằng toàn bộ 7 trường thời gian của 54.67 triệu dòng đều bị date-clamping; chỉ kết luận trên các trường hợp đã được kiểm chứng thực tế.


---

## 3. Hệ quả Nguy hại của Phép Trừ Timestamp Trực tiếp (Timestamp Subtraction Hazard)

Nếu một kỹ sư dữ liệu hoặc mô hình phân tích tự ý lấy chuỗi `DEP_TIME` trừ đi `CRS_DEP_TIME` bằng phép tính thời gian:
$$\Delta t = \texttt{to\_timestamp("2018-06-21 10:44:00")} - \texttt{to\_timestamp("2018-06-21 20:07:00")}$$
Kết quả thu được sẽ là:
$$\Delta t = -9\text{ giờ } 23\text{ phút} = \mathbf{-563\text{ phút}}!$$

- Phép tính cho ra kết luận rằng: *Máy bay đã khởi hành sớm 563 phút (hơn 9 tiếng đồng hồ trước giờ lịch trình)!*
- Trong khi thực tế vật lý: **Máy bay bị hoãn tới 877 phút (hơn 14 tiếng đồng hồ và bay vào ngày hôm sau)!**
- **Sai số tuyệt đối lên tới:** $877 - (-563) = \mathbf{1440\text{ phút}} = \text{đúng 24 giờ}$!

---

## 4. Tình huống Chuyến bay Đêm theo Kế hoạch (Scheduled Red-Eye Flights)

Hiện tượng sai lệch này không chỉ xảy ra với chuyến bay trễ như YX 3624, mà xảy ra trên hàng trăm nghìn chuyến bay đêm theo kế hoạch:
- Ví dụ chuyến bay: `FL_DATE = 2018-07-01 00:00:00`, Tuyến San Francisco (`SFO`) $\to$ New York (`JFK`):
  - `CRS_DEP_TIME`: `2018-07-01 22:30:00` (10:30 đêm bờ Tây)
  - `CRS_ARR_TIME`: `2018-07-01 06:45:00` (6:45 sáng bờ Đông)
  - `CRS_ELAPSED_TIME`: $315.0$ phút ($5$ giờ $15$ phút).
- Nếu trừ trực tiếp `CRS_ARR_TIME - CRS_DEP_TIME`:
  $$06:45 - 22:30 = \mathbf{-15\text{ giờ } 45\text{ phút}} = -945\text{ phút}!$$
- Một chuyến bay bay mất 5 tiếng 15 phút bị tính toán thành thời gian bay âm 15 tiếng 45 phút nếu dựa vào thành phần ngày của `CRS_ARR_TIME`.

---

## 5. Các Chỉ thị An toàn Bắt buộc (Mandatory Engineering Directives)

Từ các bằng chứng thực nghiệm trên, đồ án ban hành các quy định kỹ thuật nghiêm ngặt:

1. **CẤM TUYỆT ĐỐI trừ trực tiếp hai chuỗi timestamp để tính độ trễ hoặc thời lượng bay.**
2. **CẤM TUYỆT ĐỐI suy diễn ngày hạ cánh thực tế chỉ từ thành phần ngày của `CRS_ARR_TIME` hoặc `ARR_TIME`.**
3. **CẤM TỰ Ý CỘNG 24 GIỜ ĐỂ "VÁ" DỮ LIỆU (No Blind +24h Fix):**
   - Việc thấy thời gian âm rồi tự động cộng 24 giờ là một kỹ thuật ngây thơ (*naive heuristic*) cực kỳ nguy hiểm, vì chuyến bay có thể trễ qua nhiều ngày, hoặc sự chênh lệch có thể do chênh lệch múi giờ giữa bờ Tây và bờ Đông Hoa Kỳ (chênh lệch từ 3 đến 5 múi giờ).
4. **BẮT BUỘC SỬ DỤNG 7 TRƯỜNG ĐO LƯỜNG SỐ CỐT LÕI:**
   - Mọi phân tích về độ trễ, thời gian lăn, thời gian bay phải sử dụng trực tiếp các cột số nguyên bản:
     `ARR_DELAY`, `DEP_DELAY`, `ACTUAL_ELAPSED_TIME`, `CRS_ELAPSED_TIME`, `AIR_TIME`, `TAXI_OUT`, `TAXI_IN`.
   - Các trường này đã được kiểm chứng số học độc lập trong T-003 là phản ánh chính xác 100% thời lượng và độ trễ thực tế.
