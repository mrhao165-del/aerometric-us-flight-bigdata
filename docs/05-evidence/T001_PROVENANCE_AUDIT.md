# T-001: BÁO CÁO KIỂM TOÁN NGUỒN GỐC VÀ ĐỘ BAO PHỦ DỮ LIỆU (DATA PROVENANCE & COVERAGE AUDIT)

- **Mã nhiệm vụ:** `T-001` (Bản cập nhật rà soát: `T-001-R1`)
- **Gate:** `G2` (Data Quality, Cohort & Metric Contracts)
- **Ngày thực hiện:** 2026-10-14
- **Vai trò thực hiện:** AI Data Engineer
- **Trạng thái nhiệm vụ đề xuất:** `PARTIAL (Documentary & Coverage Reconciled; Upstream Provenance & License UNKNOWN; Pending Reviewer Approval)`
- **Văn bản quy định tuân thủ:** [`AGENTS.md`](../../AGENTS.md), [`DATA_CONTRACT.md`](../02-design/DATA_CONTRACT.md), [`DECISIONS.md`](../02-design/DECISIONS.md), [`BACKLOG.md`](../01-planning/BACKLOG.md), [`ROADMAP.md`](../01-planning/ROADMAP.md).

---

## 1. Mục tiêu và phạm vi kiểm toán

Nhiệm vụ **T-001** là bước khởi đầu bắt buộc của Gate **G2**, nhằm:
1. Xác minh nguồn gốc ban đầu, tài liệu phân phối, URL và giấy phép sử dụng (*license*) của bộ dữ liệu Tabular 2016–2024.
2. Kiểm tra tính toàn vẹn của 9 tệp dữ liệu CSV thô trên đĩa đối chiếu với các bằng chứng kiểm toán lịch sử ([`data_inventory.md`](inputs/data_inventory.md), 9 tệp `schema_YYYY.json`).
3. Xác định quần thể chuyến bay quan sát (*observed flight population*), các bước tiền xử lý đã áp dụng trước khi phát hành CSV, và phạm vi các hãng hàng không, sân bay, năm.
4. Đánh giá tính đại diện của bộ dữ liệu đối với toàn bộ hoạt động hàng không Hoa Kỳ.
5. Phân định rõ ràng giữa xác minh bằng siêu dữ liệu (*metadata verification*) và xác minh bằng mã băm nội dung (*content hash verification*).
6. Nhận diện các điểm mù thông tin (*information gaps*) ảnh hưởng trực tiếp đến nhiệm vụ **T-002** (Grain & Denominators) và **T-003** (Đơn vị đo & 8 CORE KPIs).

---

## 2. Nguồn tài liệu và bằng chứng tham chiếu

Kiểm toán được thực hiện dựa trên các nguồn tài liệu nguyên gốc tại thư mục [`docs/05-evidence/inputs/`](inputs/):
- **[`SOURCE_MANIFEST.json`](inputs/SOURCE_MANIFEST.json):** Xác thực 13 tệp snapshot kiểm toán bằng giá trị băm SHA-256 bất biến.
- **[`data_inventory.md`](inputs/data_inventory.md):** Bản kê kích thước tệp, đường dẫn và phát hiện 9 CSV Tabular cùng 27 tệp `.pt` Flight Chain (được kiểm toán ngày 23/08/2026).
- **9 tệp `schema_2016.json` đến `schema_2024.json`:** Kết quả kiểm toán cấu trúc schema v0.1.0 (do `pandas_chunked` quét với chunk 250,000 dòng ngày 23/08/2026).
- **[`canonical_schema_v1(1).md`](<inputs/canonical_schema_v1(1).md>):** Đặc tả 34 trường dữ liệu canonical v1.
- **[`canonical_schedule_datetime_representation_audit.md`](inputs/canonical_schedule_datetime_representation_audit.md):** Kiểm toán biểu diễn thời gian trên 48,389,162 dòng dữ liệu giai đoạn 2016–2023 (ngày 26/08/2026).
- **[`leakage_audit.md`](inputs/leakage_audit.md):** Kiểm toán thông tin phục vụ mô hình dự báo T-2h của đề tài Aeolus lịch sử (ngày 23/08/2026 và addendum 26/08/2026).
- **Tài liệu quy định và thống kê chính thức của chính phủ Hoa Kỳ:**
  - *US Department of Transportation / Bureau of Transportation Statistics (BTS) Press Release BTS 38-17:* [BTS 38-17 Announcement](https://www.transportation.gov/briefing-room/bts3817).
  - *BTS Reporting Air Carriers & Reportable Airports:* [BTS Reporting Lists](https://www.bts.gov/topics/airlines-and-airports/lists-reporting-air-carriers-and-reportable-airports-time-performance).
  - *Code of Federal Regulations (CFR):* Title 14 CFR Part 234 (*Airline Service Quality Performance Reports*).

---

## 3. Bảng kiểm toán nguồn dữ liệu theo từng năm (2016–2024)

Dưới đây là bảng tổng hợp đối chiếu trực tiếp giữa hệ thống tệp trên đĩa cứng và các báo cáo kiểm toán lịch sử:

| Năm | Đường dẫn tệp CSV | Kích thước đĩa (bytes) | Kích thước trong JSON/Inventory | Khớp kích thước | Modified Time trên đĩa (UTC) | Modified Time trong JSON (UTC) | Khớp mtime | Số dòng (`row_count`) | Số hãng (`OP_CARRIER`) | Sân bay đi / đến (`ORIGIN` / `DEST`) | Phân bố `ARR_DELAY` (Min / Mean / Max) | Trễ đến $\ge 15$ phút (Số lượng / Tỷ lệ) | Số cột không khuyết thiếu (0 missing / 100% đầy đủ) | Số cột có Missing (Weather) |
|:---:|---|---:|---:|:---:|---|---|:---:|---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **2016** | `data/raw/tabular/2016/flight_with_weather_2016.csv` | 1,538,427,452 | 1,538,427,452 | **ĐÚNG** | 2026-08-23 11:33:29.868570 | 2026-08-23 11:33:29.868570 | **ĐÚNG** | 5,537,987 | 12 | 308 / 308 | -152.0 / +3.5194 / 2142.0 | 964,216 (17.41%) | 28 / 34 | 6 / 34 (O: 8,995; D: 9,079) |
| **2017** | `data/raw/tabular/2017/flight_with_weather_2017.csv` | 1,549,837,485 | 1,549,837,485 | **ĐÚNG** | 2026-08-23 11:34:01.257975 | 2026-08-23 11:34:01.257975 | **ĐÚNG** | 5,575,872 | 12 | 312 / 312 | -238.0 / +4.3219 / 2189.0 | 1,028,626 (18.45%) | 28 / 34 | 6 / 34 (O: 980; D: 1,154) |
| **2018** | `data/raw/tabular/2018/flight_with_weather_2018.csv` | 1,941,406,432 | 1,941,406,432 | **ĐÚNG** | 2026-08-23 11:34:33.177224 | 2026-08-23 11:34:33.177224 | **ĐÚNG** | 6,986,842 | 18 | 316 / 316 | -117.0 / +4.9980 / 2692.0 | 1,333,849 (19.09%) | 28 / 34 | 6 / 34 (O: 541; D: 722) |
| **2019** | `data/raw/tabular/2019/flight_with_weather_2019.csv` | 1,990,370,667 | 1,990,370,667 | **ĐÚNG** | 2026-08-23 11:36:57.859942 | 2026-08-23 11:36:57.859942 | **ĐÚNG** | 7,161,827 | 17 | 316 / 316 | -99.0 / +5.3787 / 2695.0 | 1,368,348 (19.11%) | 28 / 34 | 6 / 34 (O: 557; D: 768) |
| **2020** | `data/raw/tabular/2020/flight_with_weather_2020.csv` | 1,197,858,795 | 1,197,858,795 | **ĐÚNG** | 2026-08-23 11:36:18.106841 | 2026-08-23 11:36:18.106841 | **ĐÚNG** | 4,312,091 | 17 | 316 / 316 | -139.0 / -5.1078 / 3864.0 | 419,429 (9.73%) | 28 / 34 | 6 / 34 (O: 408; D: 451) |
| **2021** | `data/raw/tabular/2021/flight_with_weather_2021.csv` | 1,600,032,487 | 1,600,032,487 | **ĐÚNG** | 2026-08-23 11:37:00.664679 | 2026-08-23 11:37:00.664679 | **ĐÚNG** | 5,755,666 | 17 | 316 / 317 | -107.0 / +2.9494 / 3089.0 | 983,228 (17.08%) | 28 / 34 | 6 / 34 (O: 439; D: 593) |
| **2022** | `data/raw/tabular/2022/flight_with_weather_2022.csv` | 1,782,648,882 | 1,782,648,882 | **ĐÚNG** | 2026-08-23 11:37:18.113783 | 2026-08-23 11:37:18.113783 | **ĐÚNG** | 6,413,416 | 17 | 316 / 316 | -100.0 / +6.9344 / 3423.0 | 1,346,386 (20.99%) | 28 / 34 | 6 / 34 (O: 494; D: 667) |
| **2023** | `data/raw/tabular/2023/flight_with_weather_2023.csv` | 1,847,433,387 | 1,847,433,387 | **ĐÚNG** | 2026-08-23 11:39:27.768559 | 2026-08-23 11:39:27.768559 | **ĐÚNG** | 6,645,461 | 15 | 309 / 309 | -119.0 / +6.5690 / 4405.0 | 1,365,190 (20.54%) | 28 / 34 | 6 / 34 (O: 547; D: 862) |
| **2024** | `data/raw/tabular/2024/flight_with_weather_2024.csv` | 1,748,350,586 | 1,748,350,586 | **ĐÚNG** | 2026-08-23 11:39:32.792665 | 2026-08-23 11:39:32.792665 | **ĐÚNG** | 6,284,841 | 15 | 305 / 306 | -126.0 / +7.1081 / 3803.0 | 1,307,644 (20.81%) | 28 / 34 | 6 / 34 (O: 513; D: 750) |
| **Tổng** | **9 tệp CSV** | **15,196,366,173** | **15,196,366,173** | **100% KHỚP** | — | — | **100% KHỚP** | **54,674,003** | **19 distinct** | — | — | **10,116,916 (18.5041%)** | **28/34 (100% full)** | **O: 13,474; D: 15,046** |

---

## 4. Phân tích độ bao phủ (Coverage) và giới hạn tính đại diện

### 4.1. Độ bao phủ thời gian (Temporal Coverage)
- **Phạm vi biên ngày (Boundary Check):**
  - Giai đoạn 2016–2023: Đã được kiểm toán chi tiết qua [`canonical_schedule_datetime_representation_audit.md`](inputs/canonical_schedule_datetime_representation_audit.md) trên 48,389,162 dòng, xác nhận chuỗi `FL_DATE` đều parse theo `%Y-%m-%d 00:00:00` và bao quát từ ngày 01/01 đến 31/12 của mỗi năm.
  - Năm 2024: Đã kiểm tra biên chuỗi thời gian, ghi nhận:
    - Min `FL_DATE`: `2024-01-01 00:00:00`
    - Max `FL_DATE`: `2024-12-31 00:00:00`
    - Tổng số dòng đọc được: `6,284,841` dòng (khớp chính xác với `schema_2024.json`).
- **Phân định giới hạn bằng chứng (F03 Correction):**
  - Việc kiểm tra giá trị Min/Max và tổng số dòng **chưa chứng minh tính liên tục đầy đủ của từng ngày** (chưa đếm số ngày distinct trong 366 ngày của năm nhuận 2024).
  - Do đó, tuyên bố *"đủ 366 ngày của năm 2024"* được phân loại là **`UNKNOWN / PENDING_DAILY_COUNT`**.
  - Theo nguyên tắc an toàn, không chạy quét full CSV bổ sung tại T-001; việc kiểm chứng tính liên tục của từng ngày lịch sẽ được thực hiện tại nhiệm vụ **T-004** (Time audit) hoặc **TS-004 / T-012** (Reconciliation).

### 4.2. Độ bao phủ hãng hàng không (Airline Coverage) & Quy định BTS Part 234
Kiểm toán trích xuất toàn bộ 54.67 triệu bản ghi đã xác định được chính xác **19 mã hãng hàng không (`OP_CARRIER`)** xuất hiện trong 9 năm:

#### Ma trận hiện diện của các hãng qua từng năm:
```text
Carrier  Tên hãng hàng không         2016 2017 2018 2019 2020 2021 2022 2023 2024  Phân loại & Biến động vận hành
---------------------------------------------------------------------------------------------------------------------
AA       American Airlines             Y    Y    Y    Y    Y    Y    Y    Y    Y   Xuyên suốt 9 năm (Mainline Network)
AS       Alaska Airlines               Y    Y    Y    Y    Y    Y    Y    Y    Y   Xuyên suốt 9 năm (Mainline Network)
B6       JetBlue Airways               Y    Y    Y    Y    Y    Y    Y    Y    Y   Xuyên suốt 9 năm (Mainline Low-Cost)
DL       Delta Air Lines               Y    Y    Y    Y    Y    Y    Y    Y    Y   Xuyên suốt 9 năm (Mainline Network)
F9       Frontier Airlines             Y    Y    Y    Y    Y    Y    Y    Y    Y   Xuyên suốt 9 năm (Ultra Low-Cost)
HA       Hawaiian Airlines             Y    Y    Y    Y    Y    Y    Y    Y    Y   Xuyên suốt 9 năm (Mainline / Niche)
NK       Spirit Airlines               Y    Y    Y    Y    Y    Y    Y    Y    Y   Xuyên suốt 9 năm (Ultra Low-Cost)
OO       SkyWest Airlines              Y    Y    Y    Y    Y    Y    Y    Y    Y   Xuyên suốt 9 năm (Major Regional)
UA       United Airlines               Y    Y    Y    Y    Y    Y    Y    Y    Y   Xuyên suốt 9 năm (Mainline Network)
WN       Southwest Airlines            Y    Y    Y    Y    Y    Y    Y    Y    Y   Xuyên suốt 9 năm (Major Low-Cost)
---------------------------------------------------------------------------------------------------------------------
9E       Endeavor Air                  .    .    Y    Y    Y    Y    Y    Y    Y   Bắt đầu báo cáo từ 2018 (Regional)
G4       Allegiant Air                 .    .    Y    Y    Y    Y    Y    Y    Y   Bắt đầu báo cáo từ 2018 (Ultra Low-Cost)
MQ       Envoy Air                     .    .    Y    Y    Y    Y    Y    Y    Y   Bắt đầu báo cáo từ 2018 (Regional)
OH       PSA Airlines                  .    .    Y    Y    Y    Y    Y    Y    Y   Bắt đầu báo cáo từ 2018 (Regional)
YX       Republic Airways              .    .    Y    Y    Y    Y    Y    Y    Y   Bắt đầu báo cáo từ 2018 (Regional)
---------------------------------------------------------------------------------------------------------------------
VX       Virgin America                Y    Y    Y    .    .    .    .    .    .   Biến mất sau 2018 (Sáp nhập vào AS)
EV       ExpressJet Airlines           Y    Y    Y    Y    Y    .    .    .    .   Biến mất sau 2020 (Ngừng bay sau tác động COVID-19)
QX       Horizon Air                   .    .    .    .    .    Y    Y    .    .   Chỉ xuất hiện trong 2 năm 2021–2022 (Regional)
YV       Mesa Airlines                 .    .    Y    Y    Y    Y    Y    .    .   Xuất hiện từ 2018–2022, ngừng xuất hiện từ 2023
```

#### Quy định pháp lý và Phân tích biến động 2018 (R2-01 Correction):
- **Cơ sở pháp lý & Quy định báo cáo:**
  - Quy định báo cáo dữ liệu đúng giờ của các chuyến bay thương mại nội địa Hoa Kỳ được điều chỉnh bởi **Title 14 CFR Part 234** (*Airline Service Quality Performance Reports*). Dữ liệu tài chính từ **Form 41** được BTS sử dụng làm căn cứ tính doanh thu hành khách vận chuyển nội địa có lịch trình (*domestic scheduled passenger revenue*) để xác định danh sách các hãng bắt buộc báo cáo (*mandatory reporting carriers*).
  - Theo thông cáo báo chí của Bộ Giao thông Vận tải Hoa Kỳ ([BTS 38-17](https://www.transportation.gov/briefing-room/bts3817)), có hiệu lực từ ngày **01/01/2018**, ngưỡng doanh thu bắt buộc báo cáo theo 14 CFR Part 234 đã được hạ từ **1.0% xuống còn 0.5%** tổng doanh thu vận chuyển hành khách nội địa toàn ngành.
- **Yếu tố đã xác minh (Verified Structural Evidence):**
  - **Bổ sung các hãng mới vào báo cáo:** Theo thông cáo BTS 38-17, quy định hạ ngưỡng 0.5% đã bổ sung trực tiếp 5 hãng hàng không khu vực và giá rẻ mới (`9E`, `G4`, `OH`, `YV`, `YX`) vào danh sách bắt buộc nộp báo cáo On-Time riêng rẽ từ năm 2018. Hãng `MQ` (Envoy Air) thực tế đã đạt và nộp báo cáo theo ngưỡng 1.0% cũ từ trước đó (*"Envoy Air already reported under the 1.0 percent threshold"*). Do đó, không phải toàn bộ 6 hãng mới xuất hiện trong dataset 2018 đều do việc hạ ngưỡng 0.5%.
  - **Giả thuyết chuyển dịch báo cáo Codeshare (Codeshare Reporting Hypothesis):** Trước năm 2018, các chuyến bay do hãng khu vực vận hành dưới thỏa thuận hợp tác thương hiệu / codeshare với các hãng lớn (như Delta Connection do Endeavor/SkyWest bay, American Eagle do Envoy/PSA bay, United Express) có thể chỉ do hãng tiếp thị lớn báo cáo hoặc không được tách riêng theo hãng khai thác trong một số trích xuất dữ liệu. Quy định 2018 yêu cầu các hãng vận hành đạt ngưỡng 0.5% phải nộp dữ liệu độc lập dưới mã hãng khai thác (`OP_CARRIER`) của chính họ. Tuy nhiên, **chưa có kiểm chứng mã nguồn trích xuất thượng nguồn để khẳng định quy định codeshare này trực tiếp tạo ra sự thay đổi cụ thể nào trong tập CSV được bàn giao**; nhận định này được xếp loại là giả thuyết chưa kiểm chứng (`HYPOTHESIS_UNVERIFIED`).
  - **Phạm vi sân bay báo cáo (Reportable Airports Scope):** Part 234 quy định các hãng báo cáo phải nộp dữ liệu cho tất cả các sân bay mà họ khai thác chuyến bay có lịch trình. Sự xuất hiện của các hãng khu vực mới đưa thêm một số sân bay nhỏ/khu vực vào dữ liệu, giải thích số lượng sân bay xuất hiện tăng từ 312 (2017) lên 316 (2018).
- **Yếu tố giả thuyết chưa được lượng hóa (Unquantified Hypotheses):**
  - Số lượng bản ghi năm 2018 tăng từ 5,575,872 (2017) lên 6,986,842 (2018), tương đương tăng **+25.3% (+1.41 triệu bản ghi)**.
  - Sự gia tăng này là kết quả tổng hợp của cả yếu tố thay đổi cấu trúc báo cáo (đã xác minh) lẫn các yếu tố thị trường như tăng trưởng lưu lượng hành khách toàn quốc và điều chỉnh tần suất/mạng bay của các hãng hiện hữu (các giả thuyết kinh tế chưa được đối chiếu định lượng ngoài nguồn).
  - **Không tự ý gán tỷ lệ phần trăm đóng góp** cho từng nguyên nhân khi chưa có phân rã định lượng cụ thể theo từng nhóm hãng (sẽ được phân tích tại T-013).

### 4.3. Độ bao phủ sân bay (Airport Coverage & F04 Resolution)
- Số lượng sân bay xuất phát (`ORIGIN`) dao động từ **305 đến 316 sân bay** mỗi năm; sân bay đến (`DEST`) dao động từ **305 đến 317 sân bay**.
- **Hiệu chỉnh phân loại sân bay (F04 Correction):**
  - **Loại bỏ khẳng định** cho rằng *"tất cả các sân bay trong dữ liệu đều là sân bay thương mại lớn"*.
  - Theo 14 CFR Part 234 và quy định BTS, danh sách sân bay báo cáo (*reportable airports*) bao gồm các sân bay đón nhận chuyến bay của các hãng báo cáo, bao gồm các sân bay trung tâm lớn (*Large Hubs*), trung bình (*Medium Hubs*), nhỏ (*Small Hubs*), và các sân bay thương mại không thuộc trung tâm (*Non-hub primary / commercial service airports*), thậm chí một số sân bay địa phương được phục vụ theo chương trình Hàng không Thiết yếu (*Essential Air Service - EAS*).
  - Do chưa thực hiện ánh xạ với bảng phân loại cảng hàng không chính thức của FAA (NPIAS / Hub classification), bộ dữ liệu chỉ được mô tả chính xác là: **"Các sân bay thương mại có chuyến bay có lịch trình được phục vụ bởi các hãng báo cáo thuộc phạm vi Part 234"**.

### 4.4. Giới hạn tính đại diện (Representativeness Limitations)
> [!CAUTION]
> **Bộ dữ liệu 54.67 triệu dòng KHÔNG đại diện cho toàn bộ các chuyến bay tại Hoa Kỳ (All US Flights).**

Các giới hạn đại diện bắt buộc phải công bố trong mọi báo cáo và ấn phẩm:
1. **Chỉ bao gồm chuyến bay nội địa chở khách có lịch trình của các hãng báo cáo (Part 234 Reporting Carriers Only):** Không bao gồm các hãng hàng không nhỏ (dưới ngưỡng 0.5% doanh thu sau 2018 hoặc dưới 1.0% trước 2018), chuyến bay quốc tế, chuyến bay thuê chuyến (*charter*), hàng hóa chuyên dụng (*cargo* như FedEx, UPS), quân sự (*military*), hay hàng không chung (*general aviation*).
2. **Thành phần hãng thay đổi cấu trúc qua các năm:** Không thể so sánh trực tiếp tổng số chuyến bay năm 2016 với năm 2018 mà không chuẩn hóa hoặc phân tích riêng cohort các hãng ổn định xuyên suốt (*10 stable carriers: AA, AS, B6, DL, F9, HA, NK, OO, UA, WN*).
3. **Biến động bất thường năm 2020:** Số dòng giảm còn 4.31 triệu (-39.8% so với 2019) do đại dịch COVID-19 làm sụt giảm nhu cầu đi lại; các hãng cắt giảm chuyến bay và dồn tải vào các tuyến bay trục chính, dẫn đến tỷ lệ trễ đến $\ge 15$ phút giảm xuống mức thấp kỷ lục (9.73%) và độ trễ trung bình mang dấu âm (-5.11 phút).

---

## 5. Rà soát và Phân loại các bước tiền xử lý (Preprocessing Review — F01 & F05)

Dưới đây là bảng phân loại nghiêm ngặt các bước tiền xử lý đã nhận diện từ dữ liệu đối chiếu với bằng chứng hiện hữu:

| Bước tiền xử lý nhận diện | Trạng thái phân loại | Căn cứ bằng chứng hiện có | Giới hạn kết luận & Hiệu chỉnh bắt buộc (F01 & F05) |
|---|:---:|---|---|
| **1. Lọc dữ liệu chuyến bay hoàn tất (Completed Flights Filter)** | **`INFERRED`** | Kiểm toán missing values trên 54,674,003 dòng xác nhận toàn bộ 28 cột vận hành (`ARR_DELAY`, `DEP_DELAY`, `TAXI_OUT`, `TAXI_IN`, `AIR_TIME`, `ACTUAL_ELAPSED_TIME`, `ARR_TIME`, `DEP_TIME`,...) có **0 giá trị missing** và **$100\%$ finite**. Không có cột `CANCELLED` và `DIVERTED`. | **F01 Correction:** Không được coi việc thiếu missing data là bằng chứng trực tiếp cho bộ lọc `CANCELLED == 0 AND DIVERTED == 0`. Tình trạng 100% finite delays là nhất quán với cohort các chuyến bay đã hoàn tất, nhưng không có pipeline script gốc chứng minh việc lọc. Do đó, kết luận này giữ mức **`INFERRED`**. |
| **2. Bổ sung dữ liệu thời tiết (Weather Enrichment)** | **`INFERRED`** | 6 cột thời tiết (`O_TEMP`, `O_PRCP`, `O_WSPD`, `D_TEMP`, `D_PRCP`, `D_WSPD`) hiện diện trong schema. [`leakage_audit.md`](inputs/leakage_audit.md) dòng 25 ghi nhận: *"The official paper identifies Meteostat hourly measurements..."*. Tỷ lệ khuyết thiếu thấp (0.0246% nơi đi, 0.0275% nơi đến). | Sự hiện diện của các cột thời tiết là `VERIFIED_IN_SCHEMA`, nhưng phương pháp làm giàu dữ liệu (join thời gian, trạm đo, logic fill) hoàn toàn thiếu siêu dữ liệu, do đó toàn bộ quy trình merge được phân loại là **`INFERRED`**. |
| **3. Bổ sung tọa độ và mã Index sân bay** | **`INFERRED`** | Cột tọa độ (`O_LATITUDE`, `O_LONGITUDE`, `D_LATITUDE`, `D_LONGITUDE`) khớp vị trí sân bay. `ORIGIN_INDEX` và `DEST_INDEX` có mapping ổn định theo `artifacts/manifests/airport_index_mapping_audit.json` được trích trong `leakage_audit.md`. | Sự hiện diện của các cột là `VERIFIED_IN_SCHEMA`. Việc chúng được tính toán và bổ sung trong bước tiền xử lý upstream là **`INFERRED`**. |
| **4. Biểu diễn chuỗi thời gian có lịch (`FL_DATE`, `CRS_DEP_TIME`, `CRS_ARR_TIME`) và quy trình chuẩn hóa ETL** | **Định dạng quan sát: `VERIFIED` (2016–2023) / `UNKNOWN` (toàn bộ 2024); Quy trình ETL: `INFERRED`** | [`canonical_schedule_datetime_representation_audit.md`](inputs/canonical_schedule_datetime_representation_audit.md) đã quét 48,389,162 dòng (2016–2023), xác nhận $100\%$ là chuỗi timestamp, date component của `CRS_ARR_TIME` trùng với `FL_DATE` bất kể chuyến bay qua đêm (*rollover issue*). Đối với năm 2024, mẫu nhỏ hiển thị chuỗi dạng timestamp-like (`YYYY-MM-DD 00:00:00`), nhưng do chưa có kiểm toán quét toàn diện toàn bộ 366 ngày của 2024, tính đồng nhất của định dạng được phân loại là **`UNKNOWN`** và chính thức chuyển giao cho T-004 kiểm chứng. | **R2-02 Correction:** Phân biệt rõ giữa *định dạng chuỗi timestamp đã quan sát trong lưu trữ* (đã được kiểm chứng qua datetime audit 2016–2023) với *lịch sử quy trình biến đổi ETL upstream* (chỉ là suy luận `INFERRED`, không có mã nguồn ETL hay tài liệu upstream chứng minh). Giữ nguyên giới hạn rollover: cấm dùng phép trừ timestamp naive để suy luận thời gian xuyên đêm. |
| **5. Biểu diễn thời gian vận hành thực tế (`DEP_TIME`, `ARR_TIME`, `WHEELS_OFF`, `WHEELS_ON`)** | **`UNKNOWN`** | Các trường này lưu dưới dạng chuỗi timestamp trong schema audit. | **F05 Correction:** Báo cáo kiểm toán datetime lịch sử chỉ chiếu các trường giờ có lịch (`CRS_*`). **Không được mở rộng kết luận rollover của `CRS_ARR_TIME` sang trường `ARR_TIME` thực tế** khi chưa có kiểm toán riêng. Hành vi rollover của `ARR_TIME` là **`UNKNOWN`** cho đến nhiệm vụ T-004. |

---

## 6. Phân định xác minh Metadata vs Xác minh Content Hash

Tuân thủ quy định tại [`DATA_CONTRACT.md`](../02-design/DATA_CONTRACT.md) và quyết định [`FP-DEC-014`](../02-design/DECISIONS.md):

- **Xác minh Siêu dữ liệu (`source_signature`):**
  - Kích thước byte và thời gian sửa đổi (mtime) của 9 tệp CSV trên đĩa cứng khớp chính xác $100\%$ với các giá trị được ghi lại trong 9 tệp `schema_YYYY.json` từ đợt kiểm toán ngày 23/08/2026.
  - Trạng thái phân loại: **`METADATA_MATCH_ONLY`**.
- **Xác minh Mã băm nội dung (`content hash`):**
  - Trong gói tài liệu `docs-v1.1`, tệp [`SOURCE_MANIFEST.json`](inputs/SOURCE_MANIFEST.json) chỉ cung cấp mã băm SHA-256 cho 13 tài liệu snapshot kiểm toán; **hoàn toàn không có mã băm SHA-256 tham chiếu của 9 tệp CSV thô** từ nguồn phát hành gốc.
  - Việc kiểm tra kích thước byte và mtime chỉ loại trừ việc sửa đổi tệp ngoài ý muốn trên cùng filesystem, không chứng minh tính đồng nhất nội dung so với nguồn công bố gốc nếu tệp được tạo từ môi trường khác.
  - Trạng thái phân loại: **`IDENTITY_UNVERIFIED`**.

---

## 7. Các điểm chưa rõ và tác động đến T-002, T-003

| Mục chưa có bằng chứng | Trạng thái | Tác động đến KPI / Nghiên cứu | Hành động tại T-002 và T-003 |
|---|:---:|---|---|
| **Đơn vị đo của 7 trường số** (`ARR_DELAY`, `DEP_DELAY`, `TAXI_OUT`, `TAXI_IN`, `AIR_TIME`, `ACTUAL_ELAPSED_TIME`, `CRS_ELAPSED_TIME`) | `UNIT_UNVERIFIED` | Nguy cơ gán sai đơn vị (mặc dù quy ước thông dụng của BTS là phút, nhưng chưa có tài liệu gốc kiểm chứng). | **T-003:** Bắt buộc duy trì nhãn `unit_status = UNIT_UNVERIFIED` trong mọi bảng tổng hợp cho đến khi có ADR phê duyệt hoặc bằng chứng nguồn gốc. Khóa G2 nếu chưa có quyết định rõ ràng. |
| **Ý nghĩa và cấp hạt của cột `FLIGHTS` (F06 Correction)** | `BLOCKED` | `FLIGHTS` lưu dạng `float64` với 0 missing. Giá trị `1.0` chỉ mới được quan sát trên các dòng mẫu kiểm tra (sample inspection), **chưa xác minh min/max/distinct trên toàn bộ 54.67 triệu dòng**. | **T-002:** Cấm dùng `sum(FLIGHTS)` làm mẫu số tính toán. Mẫu số hợp lệ chỉ là `count_records` (số dòng accepted). Chặn `KPI-12`. T-002 sẽ kiểm toán phân bố giá trị của cột này. |
| **Cột `CANCELLED` và `DIVERTED`** | `NOT_COMPUTABLE` | Không thể tính toán tỷ lệ hủy chuyến hay chuyển hướng bay. | **T-003:** Đánh dấu `KPI-11 = NOT_COMPUTABLE`, loại hẳn khỏi phạm vi 8 CORE KPIs. |
| **Nguồn gốc và phương thức join dữ liệu thời tiết** | `CONDITIONAL_PENDING` | Không rõ đơn vị nhiệt độ (°C hay °F), mưa, gió; không rõ mốc thời gian trích xuất thời tiết dẫn đến nguy cơ sai lệch lớn khi phân tích. | **T-005 / G2:** Giữ trạng thái `CONDITIONAL_PENDING` cho RQ-06 và KPI-10. Nếu không tìm được tài liệu nguồn, phải ban hành quyết định `CONDITIONAL_NO_GO` mà không làm chặn tiến độ của CORE KPIs. |
| **Định danh sự kiện chuyến bay (Flight Grain & Keys)** | `UNKNOWN` | Chưa rõ khóa nghiệp vụ duy nhất (business key). Trùng lặp hoàn toàn dòng (full-row duplicate) bằng 0 theo schema audit, nhưng chưa kiểm chứng trùng lặp chuyến bay theo logic nghiệp vụ. | **T-002:** Xác định chính sách hạch toán bản ghi (`accepted_row_count`), kiểm tra tính đơn nhất của khóa nghiệp vụ, cấm tự động loại bỏ bản ghi trùng lặp khi chưa có quy tắc phê duyệt. |
| **Cơ chế Rollover thời gian qua nửa đêm** | `BLOCKED_FOR_DERIVATION` | `CRS_ARR_TIME` bị cố định ngày theo `FL_DATE`. Không thể tính thời gian hành trình bằng phép trừ timestamp đơn thuần. Trường `ARR_TIME` thực tế chưa rõ hành vi rollover. | **T-004:** Cấm tạo trường thời gian đến phái sinh; sử dụng trực tiếp các trường thời lượng có sẵn (`CRS_ELAPSED_TIME`, `ACTUAL_ELAPSED_TIME`) sau khi kiểm chứng domain. |

---

## 8. Bảng phân loại mức độ bằng chứng (Evidence Classification)

| Nội dung / Tuyên bố | Mức độ xác minh | Căn cứ bằng chứng |
|---|:---:|---|
| Sự tồn tại, đường dẫn, dung lượng 9 CSV Tabular | **`VERIFIED`** | Kiểm tra trực tiếp filesystem, khớp 100% [`data_inventory.md`](inputs/data_inventory.md) và 9 `schema_YYYY.json`. |
| Tổng số dòng quan sát: 54,674,003 dòng | **`VERIFIED`** | Báo cáo kiểm toán 9 schema JSON v0.1.0 và kiểm toán trực tiếp dòng năm 2024. |
| Danh mục 34 cột dữ liệu đồng nhất 9 năm | **`VERIFIED`** | 9/9 tệp schema JSON đánh dấu `column_count: 34`, `is_complete: true`. |
| 19 mã hãng hàng không và ma trận hiện diện | **`VERIFIED`** | Quét trực tiếp cột `OP_CARRIER` trên toàn bộ 54.67 triệu dòng. |
| Khoảng thời gian biên: 2016-01-01 đến 2024-12-31 | **`VERIFIED`** | Kiểm toán datetime 2016–2023 và quét min/max `FL_DATE` năm 2024. |
| Tính liên tục đủ 366 ngày của năm 2024 | **`UNKNOWN`** | Chỉ mới kiểm tra min/max date boundary và line count; chưa đếm distinct service dates. |
| Tập dữ liệu phản ánh quần thể chuyến bay đã hoàn tất | **`INFERRED`** | Căn cứ vào 0 giá trị missing và 100% finite delays của tất cả các trường vận hành (F01). |
| Dữ liệu xuất phát từ BTS Form 41 / Part 234 và Meteostat | **`INFERRED`** | Đối chiếu cấu trúc trường, biến động hãng hàng không Part 234 năm 2018 và trích dẫn trong `leakage_audit.md` (F02). |
| Phân loại sân bay (Hub status / Size) | **`UNKNOWN`** | Chỉ xác định 305–317 sân bay thương mại có chuyến bay báo cáo; chưa ánh xạ FAA Hub size (F04). |
| Giấy phép sử dụng (*license*) và URL phân phối chính thức | **`UNKNOWN`** | Không có thông tin URL hay tệp license trong mã nguồn hoặc gói tài liệu được giao. |
| Tính toàn vẹn nội dung raw CSV qua SHA-256 | **`UNKNOWN`** | `SOURCE_MANIFEST.json` không chứa mã băm tham chiếu cho 9 file CSV thô (`IDENTITY_UNVERIFIED`). |
| Đơn vị chuẩn của các trường đo lường độ trễ và thời gian | **`UNKNOWN`** | Chưa có tài liệu thượng nguồn xác nhận chính thức (`UNIT_UNVERIFIED`). |
| Đại diện cho toàn bộ các chuyến bay của nước Mỹ | **`BLOCKED`** | Đã chứng minh tập dữ liệu có sự thiên lệch chọn lọc (chỉ hãng báo cáo Part 234, chỉ chuyến hoàn tất, chỉ ~310 sân bay). |

---

## 9. Manifest tái lập bằng chứng kiểm toán (Audit Reproducibility Manifest — F08)

Toàn bộ các phép kiểm toán thăm dò đã thực hiện trong nhiệm vụ T-001 được ghi nhận đầy đủ siêu dữ liệu kỹ thuật dưới đây:

| Kịch bản kiểm toán | Đường dẫn lưu trữ | Kích thước (bytes) | SHA-256 Hash | Nguồn dữ liệu đầu vào | Lệnh thực thi | Exit Code | Thời điểm chạy | Kết quả chính & Bằng chứng |
|---|---|---:|---|---|---|:---:|---|---|
| `audit_extract.py` | `scratch/audit_extract.py` | 1,419 | `a84794f3a9c762d3710b5fbafec52450b970e5ae0a911aac966739d6284f4ddc` | 9 schema JSON + stat của 9 CSV thô | `python scratch/audit_extract.py` | `0` | 2026-10-14 00:54:57 | Kích thước và mtime khớp 100% giữa đĩa và JSON audit cũ. |
| `sample_rows.py` | `scratch/sample_rows.py` | 527 | `3411e6a7e54254eb6310a429fd466c95937ba0d027f363746f78fdfe3e82b6da` | `data/raw/tabular/2016/flight_with_weather_2016.csv` (2 dòng đầu) | `python scratch/sample_rows.py` | `0` | 2026-10-14 00:55:07 | Xác nhận header 34 cột và định dạng dữ liệu mẫu năm 2016. |
| `sample_2024.py` | `scratch/sample_2024.py` | 502 | `14d432c364fd77b6ab23cf35776c791124a385c6237bfd3ee3b43628076e4119` | `data/raw/tabular/2024/flight_with_weather_2024.csv` (2 dòng đầu) | `python scratch/sample_2024.py` | `0` | 2026-10-14 00:55:22 | Xác nhận header 34 cột và định dạng dữ liệu mẫu năm 2024. |
| `check_missing.py` | `scratch/check_missing.py` | 664 | `d9503cda101d3af52cd36e6573cfc6c0f84d333f9717df7574ae9624415e346b` | `docs/05-evidence/inputs/schema_2016.json` | `python scratch/check_missing.py` | `1` | 2026-10-14 00:55:49 | Lỗi cú pháp so sánh kiểu dict; được thay thế bởi `check_all_missing.py`. |
| `check_all_missing.py` | `scratch/check_all_missing.py` | 645 | `24ee9b9ee71eb5c55fd50522158fc3497709c0d5a8e90ffe5e42d8c2bd9aece8` | 9 schema JSON | `python scratch/check_all_missing.py` | `0` | 2026-10-14 00:56:03 | 28/34 cột không thiếu dữ liệu; 6 cột thời tiết thiếu 13,474 (O) và 15,046 (D). |
| `test_carriers_2016.py` | `scratch/test_carriers_2016.py` | 609 | `35f78581da92c5fdc7a7f6b5a034c9766afafd728e48f3d5f7200fe009930052` | `data/raw/tabular/2016/flight_with_weather_2016.csv` | `python scratch/test_carriers_2016.py` | `0` | 2026-10-14 00:56:56 | Benchmark quét streaming (3.48s); trích xuất 12 hãng của năm 2016. |
| `extract_all_carriers.py` | `scratch/extract_all_carriers.py` | 1,137 | `00525a6bbfff24de3789c843354cb3ddcddc1f7c6cb3f986632f6f47d2da715e` | 9 CSV thô (2016..2024) | `python scratch/extract_all_carriers.py` | `0` | 2026-10-14 00:57:19 | Quét 54.67M dòng (34.45s); lập ma trận 19 hãng hàng không. |
| `check_2024_date.py` | `scratch/check_2024_date.py` | 649 | `43f29927fe8f1397aab84a6dac5cb2b4b18b1844d06be0ef03b8a39bec0ea57a` | `data/raw/tabular/2024/flight_with_weather_2024.csv` | `python scratch/check_2024_date.py` | `0` | 2026-10-14 00:58:17 | Quét 6,284,841 dòng; Min FL_DATE 2024-01-01, Max FL_DATE 2024-12-31. |

*Ghi chú về tính khả chuyển:* Các kịch bản trên được tạo và lưu trữ tại thư mục scratch của phiên làm việc. Đối với môi trường độc lập chỉ nhận mã nguồn của repository, các kịch bản scratch này phải được coi là `NOT_REPRODUCIBLE_FROM_DELIVERED_EVIDENCE` trừ khi được nhúng trực tiếp mã nguồn trong báo cáo kiểm toán hoặc lưu thành công cụ chính thức trong `tools/`.

---

## 10. Đề xuất cập nhật tài liệu và Trạng thái nghiệm thu

### 10.1. Đề xuất cập nhật tài liệu quản trị (Cần Reviewer phê duyệt)
1. **[`docs/05-evidence/DATA_PROVENANCE.md`](DATA_PROVENANCE.md):**
   - Bổ sung ma trận 19 hãng hàng không và trích dẫn quy định 14 CFR Part 234 / BTS 38-17.
   - Ghi nhận trạng thái: Dataset suy luận là các chuyến bay hoàn tất (*completed flights inferred*).
   - Cập nhật trạng thái xác minh: `METADATA_MATCH_ONLY`, `IDENTITY_UNVERIFIED`.
2. **[`docs/04-execution/PROJECT_STATE.md`](../04-execution/PROJECT_STATE.md):**
   - **TẠM THỜI CHƯA CẬP NHẬT THÀNH DONE.** Giữ nguyên trạng thái `TODO / PENDING_REVIEW` cho nhiệm vụ `T-001` cho đến khi có sự phê duyệt chính thức từ reviewer.

### 10.2. Kết luận nghiệm thu T-001
- Nhiệm vụ T-001 đề xuất xếp loại **`PARTIAL (Documentary & Coverage Reconciled; Upstream License & URL UNKNOWN)`**.
- Báo cáo đã phân định rạch ròi giữa các sự kiện đã kiểm chứng (*verified facts*), suy luận hợp lý (*inferences*), và các điểm mù thông tin (*unknowns/blocked*).
- Toàn bộ các phát hiện F01–F08 đã được xử lý triệt để, đảm bảo tính trung thực khoa học tuyệt đối cho đồ án.
