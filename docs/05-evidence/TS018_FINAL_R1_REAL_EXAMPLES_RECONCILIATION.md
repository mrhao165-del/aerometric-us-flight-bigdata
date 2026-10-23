# TS018_FINAL_R1_REAL_EXAMPLES_RECONCILIATION.md
# Đối Soát Và Chứng Thực Vật Lý Các Ví Dụ Chuyến Bay TS-018

**Dự án:** US Flight Performance Analysis 2016–2024  
**Nhiệm vụ:** TS-018 Final Evidence Integrity Review (R1 Correction)  
**Tác giả:** Senior PySpark QA Engineer & Forensic Evidence Auditor  
**Ngày lập:** 2026-10-20  
**Trạng thái:** Bằng chứng trích xuất trực tiếp bằng máy từ 2 nguồn vật lý.

---

## 1. NGUYÊN NHÂN SAI LỆCH TRONG BÁO CÁO CŨ
Trong báo cáo tổng kết trước đó, 3 ví dụ minh họa chuyến bay bị sai lệch ngày bay và giá trị số so với tệp BTS TranStats. Nguyên nhân được xác định là:
- Người viết báo cáo đã ghi chép nhầm ngày tháng từ một bản nháp phân tích thử nghiệm thay vì sao chép trực tiếp kết quả xuất từ [run_ts018_bts_adapter.py](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/tools/qa/run_ts018_bts_adapter.py) (dòng 593–611) và tệp witness [TS018_201901_MATCHED_SAMPLE_WITNESS.csv](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/docs/05-evidence/TS018_201901_MATCHED_SAMPLE_WITNESS.csv).
- Ba khóa bị ghi nhầm ngày không thuộc tập mẫu 1.500 chuyến bay chứng thực.

---

## 2. ĐỐI SOÁT CHI TIẾT TẠI CẢ HAI NHÓM KHÓA

### Bảng 2.1: Đối soát 3 khóa bị ghi nhầm ngày trong báo cáo cũ

| Khóa chuyến bay | Giá trị báo cáo cũ ghi | Giá trị trích xuất thực tế từ Raw CSV 2019 | Giá trị trích xuất thực tế từ BTS TranStats ZIP | Đánh giá độc lập |
| :--- | :--- | :--- | :--- | :--- |
| `2019-01-20` \| `NK` \| `314` \| `IAH` $\rightarrow$ `TPA` | `ARR_DELAY = -16.0` | `ARR_DELAY = -9.0`<br>`DEP_DELAY = -4.0` | `ARR_DELAY = -9.00`<br>`DEP_DELAY = -4.00` | Cả 2 nguồn thực tế đều khớp nhau (`-9.0`), nhưng báo cáo cũ ghi sai thành `-16.0`. |
| `2019-01-05` \| `UA` \| `753` \| `SFO` $\rightarrow$ `EWR` | `ARR_DELAY = 0.0` | `ARR_DELAY = 171.0`<br>`DEP_DELAY = 194.0` | `ARR_DELAY = 171.00`<br>`DEP_DELAY = 194.00` | Cả 2 nguồn thực tế đều khớp nhau (`171.0`), nhưng báo cáo cũ ghi sai thành `0.0`. |
| `2019-01-07` \| `AA` \| `692` \| `PHX` $\rightarrow$ `HNL` | `ARR_DELAY = 1186.0` | `ARR_DELAY = -2.0`<br>`DEP_DELAY = -3.0` | `ARR_DELAY = -2.00`<br>`DEP_DELAY = -3.00` | Cả 2 nguồn thực tế đều khớp nhau (`-2.0`), nhưng báo cáo cũ ghi sai thành `1186.0`. |

> **Nhận xét quan trọng:** Trên cả 3 khóa sai ngày này, bản thân tệp CSV gốc của đồ án và tệp BTS TranStats gốc **vẫn khớp nhau hoàn toàn** từng trường. Sai lệch chỉ là việc báo cáo văn bản gán nhầm giá trị của ngày này sang ngày khác.

---

### Bảng 2.2: Ba ví dụ chuyến bay chính xác thuộc tập witness 1.500 bản ghi

Các ví dụ dưới đây được trích xuất tự động bằng chương trình từ cả hai nguồn vật lý (`flight_with_weather_2019.csv` và `T_ONTIME_REPORTING_20261019_112232.zip`):

#### Ví dụ 1: Chuyến bay đến sớm (Stratum: `NEGATIVE_DELAY`)
- **Khóa định danh:** `2019-01-10` | Hãng `NK` | Chuyến bay `314` | Tuyến: `IAH` $\rightarrow$ `TPA`
- **Vị trí trong Witness:** Dòng số 2 (Bản ghi mẫu đầu tiên)
- **Điểm băm chọn mẫu:** `000037cf5d495403517fca1f071ea92fc10bc7a90486cd137fedd539b2d561b7`

| Trường đo lường | Giá trị CSV 2019 thô | Giá trị BTS TranStats | Chênh lệch ($\Delta$) | Trạng thái đối soát |
| :--- | :---: | :---: | :---: | :---: |
| `ARR_DELAY` | `-6.0` | `-6.00` | `0.0` | **EXACT_NUMERIC_MATCH** |
| `DEP_DELAY` | `-4.0` | `-4.00` | `0.0` | **EXACT_NUMERIC_MATCH** |
| `TAXI_OUT` | `13.0` | `13.00` | `0.0` | **EXACT_NUMERIC_MATCH** |
| `TAXI_IN` | `8.0` | `8.00` | `0.0` | **EXACT_NUMERIC_MATCH** |
| `AIR_TIME` | `98.0` | `98.00` | `0.0` | **EXACT_NUMERIC_MATCH** |
| `ACTUAL_ELAPSED_TIME` | `119.0` | `119.00` | `0.0` | **EXACT_NUMERIC_MATCH** |
| `CRS_ELAPSED_TIME` | `121.0` | `121.00` | `0.0` | **EXACT_NUMERIC_MATCH** |

---

#### Ví dụ 2: Chuyến bay đúng giờ tuyệt đối (Stratum: `ZERO_DELAY`)
- **Khóa định danh:** `2019-01-31` | Hãng `UA` | Chuyến bay `753` | Tuyến: `SFO` $\rightarrow$ `EWR`
- **Vị trí trong Witness:** Bản ghi thuộc phân tầng đúng giờ
- **Điểm băm chọn mẫu:** Khớp chính xác với hàm băm seed `ts018_bts_jan2019_seed_42`

| Trường đo lường | Giá trị CSV 2019 thô | Giá trị BTS TranStats | Chênh lệch ($\Delta$) | Trạng thái đối soát |
| :--- | :---: | :---: | :---: | :---: |
| `ARR_DELAY` | `0.0` | `0.00` | `0.0` | **EXACT_NUMERIC_MATCH** |
| `DEP_DELAY` | `0.0` | `0.00` | `0.0` | **EXACT_NUMERIC_MATCH** |
| `TAXI_OUT` | `24.0` | `24.00` | `0.0` | **EXACT_NUMERIC_MATCH** |
| `TAXI_IN` | `10.0` | `10.00` | `0.0` | **EXACT_NUMERIC_MATCH** |
| `AIR_TIME` | `295.0` | `295.00` | `0.0` | **EXACT_NUMERIC_MATCH** |
| `ACTUAL_ELAPSED_TIME` | `329.0` | `329.00` | `0.0` | **EXACT_NUMERIC_MATCH** |
| `CRS_ELAPSED_TIME` | `329.0` | `329.00` | `0.0` | **EXACT_NUMERIC_MATCH** |

---

#### Ví dụ 3: Chuyến bay trễ nghiêm trọng (Stratum: `POSITIVE_DELAY`)
- **Khóa định danh:** `2019-01-21` | Hãng `AA` | Chuyến bay `692` | Tuyến: `PHX` $\rightarrow$ `HNL`
- **Vị trí trong Witness:** Bản ghi thuộc phân tầng trễ cao
- **Điểm băm chọn mẫu:** Khớp chính xác với hàm băm seed `ts018_bts_jan2019_seed_42`

| Trường đo lường | Giá trị CSV 2019 thô | Giá trị BTS TranStats | Chênh lệch ($\Delta$) | Trạng thái đối soát |
| :--- | :---: | :---: | :---: | :---: |
| `ARR_DELAY` | `1186.0` | `1186.00` | `0.0` | **EXACT_NUMERIC_MATCH** |
| `DEP_DELAY` | `1191.0` | `1191.00` | `0.0` | **EXACT_NUMERIC_MATCH** |
| `TAXI_OUT` | `28.0` | `28.00` | `0.0` | **EXACT_NUMERIC_MATCH** |
| `TAXI_IN` | `17.0` | `17.00` | `0.0` | **EXACT_NUMERIC_MATCH** |
| `AIR_TIME` | `364.0` | `364.00` | `0.0` | **EXACT_NUMERIC_MATCH** |
| `ACTUAL_ELAPSED_TIME` | `409.0` | `409.00` | `0.0` | **EXACT_NUMERIC_MATCH** |
| `CRS_ELAPSED_TIME` | `414.0` | `414.00` | `0.0` | **EXACT_NUMERIC_MATCH** |

---

## 3. KẾT LUẬN KIỂM CHỨNG
Toàn bộ 3 ví dụ nêu trên đều:
1. Hiện diện đầy đủ trong tệp CSV đồ án thô năm 2019.
2. Hiện diện đầy đủ trong tệp nén BTS TranStats chính thức tháng 1/2019.
3. Hiện diện đầy đủ trong tệp chứng thực 1.500 bản ghi `TS018_201901_MATCHED_SAMPLE_WITNESS.csv`.
4. Có giá trị số khớp tuyệt đối từng bit trên toàn bộ 7 trường số cốt lõi (`diff == 0.0`).
