# T-004: ĐẶC TẢ BỘ DỮ LIỆU KIỂM THỬ THỜI GIAN AN TOÀN VÀ VƯỢT NỬA ĐÊM (TEST FIXTURE SPECIFICATION FOR TS-010)

- **Mã nhiệm vụ:** `T-004` (Sub-task 5: Synthetic Test Fixtures for TS-010)
- **Gate kiểm soát:** `G2` (Data Quality, Cohort & Metric Contracts)
- **Ngày ban hành:** 2026-10-14
- **Vai trò:** Senior Big Data QA Engineer & Statistical Reviewer
- **Trạng thái:** **`FIXTURE_SPEC_FINALIZED`**
- **Văn bản tuân thủ:** [`AGENTS.md`](../../AGENTS.md), [`docs/02-design/DATA_CONTRACT.md`](../02-design/DATA_CONTRACT.md), [`docs/02-design/DATA_DICTIONARY.md`](../02-design/DATA_DICTIONARY.md), [`docs/03-quality/TEST_PLAN.md`](../03-quality/TEST_PLAN.md) (`TS-010`), [`docs/05-evidence/T004_SAFE_FIELDS_DECISION.md`](T004_SAFE_FIELDS_DECISION.md).

---

## 1. Mục tiêu & Phạm vi của Bộ Fixture TS-010

Bộ kiểm thử **`TS-010` (Safe Time Representation & Overnight Operational Timestamps Guard)** được thiết kế nhằm bảo vệ hệ thống ingestion và pipeline tính toán KPI của Apache Spark chống lại các lỗi thời gian nghiêm trọng:
1. Đảm bảo pipeline không bao giờ thực hiện phép trừ chuỗi timestamp trực tiếp giữa các cột thời gian.
2. Đảm bảo pipeline nhận diện chính xác các trường hợp bay đêm theo lịch (*scheduled red-eye*), hoãn bay qua nửa đêm (*operational rollover*), và bay qua nhiều múi giờ.
3. Đảm bảo không xảy ra hiện tượng ngoại lệ parser tại các mốc biên (giao thừa, năm nhuận, đúng nửa đêm 00:00:00).

### Phân định Rõ ràng Hai Định dạng Tệp Dữ liệu Kiểm thử Thực thi:
- **`T004_TF09_temporal_fixture.csv` (18 cột — `TEMPORAL_TEST_PROJECTION`):** Tập trung chuyên sâu vào các trường thời gian, trích xuất giờ `CRS_DEP_HOUR`, độ trễ, thời lượng phút và phân loại ma trận trường an toàn. Phù hợp cho unit test nhẹ và kiểm tra nhanh các bất biến thời gian.
- **`T004_TF09_full_schema_fixture.csv` (34 cột — `FULL_SCHEMA_INGESTION_FIXTURE`):** Đúng đầy đủ 34 cột theo schema chuẩn của 9 năm CSV thô (1 header + 9 data rows, 0 comment lines). Phù hợp cho kiểm thử nạp dữ liệu (*ingestion pipeline test*) trên Spark.
- **`T004_TF09_temporal_fixture.json` (Metadata Oracle):** Chứa metadata đầy đủ, phân loại ma trận 4 cấp, định danh múi giờ chuẩn IANA, cờ DST, và các khẳng định toán học bất biến tự động.

---

## 2. Bảng Tổng hợp 9 Kịch bản Kiểm thử Thời gian (TF-01 đến TF-09)

| Mã Fixture | Tên Kịch bản Nghiệp vụ | Tuyến bay & Hãng | Đặc điểm Thời gian Cốt lõi & Múi giờ Lịch sử | Khẳng định Kiểm chuẩn Kỳ vọng (*Expected Oracle Assertion*) |
|:---:|---|:---:|---|---|
| **`TF-01`** | Same-day Standard Daytime Flight | AA 101 (ORD $\to$ DFW) | Khởi hành 08:00, hạ cánh 10:25 cùng ngày; `America/Chicago` (CDT, UTC-5); $\Delta\text{TZ} = 0$h | Khớp thời gian ban ngày chuẩn; $\text{ARR\_DELAY} = 0.0$; $\text{ACTUAL} = \text{TAXI\_OUT} + \text{AIR} + \text{TAXI\_IN}$. |
| **`TF-02`** | Scheduled Overnight Flight (Red-Eye) | UA 202 (LAX $\to$ JFK) | Kế hoạch 23:00 $\to$ 07:15 sáng hôm sau; Date kẹp `FL_DATE`; PDT (UTC-7) $\to$ EDT (UTC-4); $\Delta\text{TZ} = +3$h | Chặn đứng phép trừ timestamp; $\text{CRS\_ELAPSED} = 315.0$ phút; trích xuất `CRS_DEP_HOUR = 23`. |
| **`TF-03`** | Operational Overnight Delay | DL 303 (ATL $\to$ LGA) | Kế hoạch 21:00 $\to$ 23:30; Thực tế hoãn cất cánh lúc 01:30 sáng hôm sau; `America/New_York` (EDT, UTC-4); $\Delta\text{TZ} = 0$h | Chặn đứng tính trễ âm; $\text{DEP\_DELAY} = +270.0$; không trừ trực tiếp $01:30 - 21:00$. |
| **`TF-04`** | Early Morning Departure | WN 404 (BWI $\to$ MCO) | Kế hoạch và thực tế cất cánh lúc 01:15 sáng; `America/New_York` (EDT, UTC-4); $\Delta\text{TZ} = 0$h | Trích xuất an toàn `CRS_DEP_HOUR = 1`; gán nhãn khung giờ `Night / Early Morning` ($00..05$). |
| **`TF-05`** | Midnight Departure Boundary | B6 505 (BOS $\to$ FLL) | Khởi hành đúng mốc nửa đêm `00:00:00`; `America/New_York` (EDT, UTC-4); $\Delta\text{TZ} = 0$h | Kiểm tra xử lý biên; $\text{hour}(00:00:00) == 0$; không phát sinh lỗi chia cho 0 hay parser fail. |
| **`TF-06`** | Leap Year & Timezone Flight | WN 606 (LAS $\to$ PHX) | Ngày nhuận `2024-02-29`; PST (UTC-8) $\to$ MST (UTC-7, PHX không đổi DST, lệch $+1$h); Cất cánh 13:58, hạ cánh 16:18 | Parser ngày nhuận hợp lệ; thời lượng UTC và đồng hồ địa phương chuẩn hóa khớp $80.0$ min; $\text{ARR\_DELAY} = -2.0$. |
| **`TF-07`** | Year-End Rollover & Timezone Flight | AS 707 (SEA $\to$ ANC) | `FL_DATE = 2023-12-31`; PST (UTC-8) $\to$ AKST (UTC-9, lệch $-1$h); Cất cánh 23:50, hạ cánh 02:15 rạng sáng 01/01 | Phân vùng theo năm giữ 2023; thời lượng UTC và đồng hồ địa phương chuẩn hóa khớp $205.0$ min; $\text{ARR\_DELAY} = 0.0$. |
| **`TF-08`** | Heavy Delay Overnight (Dựa trên YX 3624) | YX 3624 (DEN $\to$ XNA) | Trễ cực đoan $+877.0$ phút; cất cánh 10:44 sáng hôm sau; MDT (UTC-6) $\to$ CDT (UTC-5, lệch $+1$h) | Giữ nguyên bản ghi làm Counterexample; $\text{ARR\_DELAY} = +941.0$; cân bằng trễ $877 + (182 - 118) = 941$. |
| **`TF-09`** | Transcontinental Timezone Crossing | UA 909 (SFO $\to$ BOS) | Bay qua 3 múi giờ mùa hè; PDT (UTC-7) $\to$ EDT (UTC-4, lệch $+3$h); Đồng hồ lệch 8.5h nhưng thời gian bay thực 5.5h | Không suy thời lượng từ hiệu đồng hồ địa phương; $\text{CRS\_ELAPSED} = 330.0$ phút ($5.5$h). |

---

## 3. Đặc tả Chi tiết Giá trị Dữ liệu 34 Cột cho Từng Fixture

```csv
FL_DATE,OP_CARRIER,OP_CARRIER_FL_NUM,ORIGIN,DEST,CRS_DEP_TIME,DEP_TIME,DEP_DELAY,TAXI_OUT,WHEELS_OFF,WHEELS_ON,TAXI_IN,CRS_ARR_TIME,ARR_TIME,ARR_DELAY,CRS_ELAPSED_TIME,ACTUAL_ELAPSED_TIME,AIR_TIME,FLIGHTS,MONTH,DAY_OF_MONTH,DAY_OF_WEEK,ORIGIN_INDEX,DEST_INDEX,O_TEMP,O_PRCP,O_WSPD,D_TEMP,D_PRCP,D_WSPD,O_LATITUDE,O_LONGITUDE,D_LATITUDE,D_LONGITUDE
# TF-01: Same-day Standard Daytime Flight (ORD -> DFW)
2018-06-01 00:00:00,AA,101.0,ORD,DFW,2018-06-01 08:00:00,2018-06-01 08:05:00,5.0,15.0,2018-06-01 08:20:00,2018-06-01 10:20:00,5.0,2018-06-01 10:25:00,2018-06-01 10:25:00,0.0,145.0,140.0,120.0,1.0,6,1,5,10,20,20.0,0.0,10.0,25.0,0.0,8.0,41.97416,-87.90732,32.89595,-97.03720
# TF-02: Scheduled Overnight Flight (LAX -> JFK, Red-Eye)
2018-06-01 00:00:00,UA,202.0,LAX,JFK,2018-06-01 23:00:00,2018-06-01 23:02:00,2.0,18.0,2018-06-01 23:20:00,2018-06-01 07:05:00,10.0,2018-06-01 07:15:00,2018-06-01 07:15:00,0.0,315.0,313.0,285.0,1.0,6,1,5,30,40,18.0,0.0,5.0,16.0,0.0,7.0,33.94254,-118.40807,40.64131,-73.77814
# TF-03: Operational Overnight Delay (ATL -> LGA, Delayed 270m to next morning)
2018-06-01 00:00:00,DL,303.0,ATL,LGA,2018-06-01 21:00:00,2018-06-01 01:30:00,270.0,20.0,2018-06-01 01:50:00,2018-06-01 03:50:00,10.0,2018-06-01 23:30:00,2018-06-01 04:00:00,270.0,150.0,150.0,120.0,1.0,6,1,5,50,60,22.0,0.0,8.0,19.0,0.0,6.0,33.64044,-84.42694,40.77724,-73.87261
# TF-04: Early Morning Departure (BWI -> MCO, 01:15 AM)
2018-06-01 00:00:00,WN,404.0,BWI,MCO,2018-06-01 01:15:00,2018-06-01 01:10:00,-5.0,12.0,2018-06-01 01:22:00,2018-06-01 03:22:00,8.0,2018-06-01 03:35:00,2018-06-01 03:30:00,-5.0,140.0,140.0,120.0,1.0,6,1,5,70,80,17.0,0.0,4.0,24.0,0.0,5.0,39.17540,-76.66820,28.43116,-81.30808
# TF-05: Midnight Departure Boundary (BOS -> FLL, 00:00:00)
2018-06-01 00:00:00,B6,505.0,BOS,FLL,2018-06-01 00:00:00,2018-06-01 00:02:00,2.0,15.0,2018-06-01 00:17:00,2018-06-01 03:17:00,8.0,2018-06-01 03:25:00,2018-06-01 03:25:00,0.0,205.0,203.0,180.0,1.0,6,1,5,90,100,15.0,0.0,6.0,26.0,0.0,7.0,42.36561,-71.00956,26.07421,-80.15060
# TF-06: Leap Year Boundary & Timezone Flight (LAS -> PHX, 2024-02-29, PST UTC-8 -> MST UTC-7, +1h TZ)
2024-02-29 00:00:00,WN,606.0,LAS,PHX,2024-02-29 14:00:00,2024-02-29 13:58:00,-2.0,14.0,2024-02-29 14:12:00,2024-02-29 16:12:00,6.0,2024-02-29 16:20:00,2024-02-29 16:18:00,-2.0,80.0,80.0,60.0,1.0,2,29,4,110,120,18.0,0.0,9.0,21.0,0.0,8.0,36.08400,-115.15374,33.43727,-112.00779
# TF-07: Year-End Rollover & Timezone Flight (SEA -> ANC, 2023-12-31 -> 2024-01-01, PST UTC-8 -> AKST UTC-9, -1h TZ)
2023-12-31 00:00:00,AS,707.0,SEA,ANC,2023-12-31 23:45:00,2023-12-31 23:50:00,5.0,16.0,2024-01-01 00:06:00,2024-01-01 02:06:00,9.0,2023-12-31 02:15:00,2024-01-01 02:15:00,0.0,210.0,205.0,180.0,1.0,12,31,7,130,140,5.0,0.0,12.0,-2.0,0.0,15.0,47.45025,-122.30882,61.17589,-149.99008
# TF-08: Heavy Delay Overnight Rollover (YX 3624 Row A, Delayed 877m to next day)
2018-06-21 00:00:00,YX,3624.0,DEN,XNA,2018-06-21 20:07:00,2018-06-21 10:44:00,877.0,91.0,2018-06-21 12:15:00,2018-06-21 14:39:00,7.0,2018-06-21 23:05:00,2018-06-21 14:46:00,941.0,118.0,182.0,84.0,1.0,6,21,4,150,160,24.0,0.0,7.0,26.0,0.0,5.0,39.85841,-104.66700,36.28186,-94.30681
# TF-09: Transcontinental Timezone Crossing (SFO -> BOS, 3 timezones)
2018-06-01 00:00:00,UA,909.0,SFO,BOS,2018-06-01 08:00:00,2018-06-01 08:00:00,0.0,20.0,2018-06-01 08:20:00,2018-06-01 16:20:00,10.0,2018-06-01 16:30:00,2018-06-01 16:30:00,0.0,330.0,330.0,300.0,1.0,6,1,5,170,180,16.0,0.0,10.0,20.0,0.0,8.0,37.61900,-122.37484,42.36561,-71.00956

```

---

## 4. Các Quy tắc Kiểm chuẩn Bắt buộc cho TS-010 (Oracles & Assertions)

Mọi pipeline ETL nạp dữ liệu và kiểm thử chất lượng phải thỏa mãn các khẳng định toán học sau:

1. **Khẳng định Đơn vị Đo & Cân bằng Độ trễ:**
   $$\forall \text{ record: } \text{ARR\_DELAY} \equiv \text{DEP\_DELAY} + (\text{ACTUAL\_ELAPSED\_TIME} - \text{CRS\_ELAPSED\_TIME})$$
   (Thỏa mãn trên toàn bộ 9 fixtures, bao gồm `TF-03` trễ 270 phút và `TF-08` trễ 877 phút).
2. **Khẳng định Phân rã Thời gian Cổng-đến-Cổng:**
   $$\forall \text{ record: } \text{ACTUAL\_ELAPSED\_TIME} \equiv \text{TAXI\_OUT} + \text{AIR\_TIME} + \text{TAXI\_IN}$$
   (Thỏa mãn trên toàn bộ 9 fixtures).
3. **Khẳng định Khóa Phân vùng Ngày Lịch:**
   $$\text{to\_date}(\texttt{FL\_DATE}) \text{ phải trích xuất chính xác ngày dịch vụ mà không đổi theo giờ trễ}.$$
   (Ví dụ: `TF-08` trễ sang sáng ngày 22/06 nhưng khóa phân vùng vẫn là `2018-06-21`).
4. **Khẳng định Trích xuất Giờ An toàn:**
   $$\text{hour}(\texttt{CRS\_DEP\_TIME}) \in [0, 23]$$
   (Không bị lỗi tại `TF-05` với mốc `00:00:00` $\implies \text{hour} = 0$).
5. **Khẳng định Cấm Phép Trừ Timestamp Trực tiếp:**
   Bộ kiểm thử tự động sẽ ném ngoại lệ nếu phát hiện biểu thức dạng:
   $$\texttt{unix\_timestamp(CRS\_ARR\_TIME) - unix\_timestamp(CRS\_DEP\_TIME)}$$
   hoặc bất kỳ hàm nào cố tình tính thời lượng bằng hiệu hai timestamp này.
