# T-002: BÁO CÁO PHÂN TÍCH TRÙNG LẶP VÀ PHẠM VI CODESHARE (DUPLICATE & CODESHARE ANALYSIS)

- **Mã nhiệm vụ:** `T-002` (Duplicate & Codeshare Audit)
- **Gate:** `G2` (Data Quality, Cohort & Metric Contracts)
- **Ngày thực hiện:** 2026-10-14
- **Vai trò:** AI Data Engineer
- **Trạng thái:** **`VERIFIED (Full Population Key Audit Complete; Single Operational Duplicate Identified; Zero Naive Dedup Policy Established)`**
- **Văn bản quy định tuân thủ:** [`AGENTS.md`](../../AGENTS.md), [`DATA_CONTRACT.md`](../02-design/DATA_CONTRACT.md), [`DATA_DICTIONARY.md`](../02-design/DATA_DICTIONARY.md), [`TEST_PLAN.md`](../03-quality/TEST_PLAN.md).

---

## 1. Mục tiêu và Phạm vi kiểm toán

Nhiệm vụ **T-002.2** và **T-002.3** tập trung giải quyết hai bài toán then chốt:
1. **Kiểm toán trùng lặp khóa nghiệp vụ ứng viên:**
   $$\text{Candidate Key} = (\text{FL\_DATE}, \text{OP\_CARRIER}, \text{OP\_CARRIER\_FL\_NUM}, \text{ORIGIN}, \text{DEST}, \text{CRS\_DEP\_TIME})$$
   Đo lường mức độ trùng lặp thực tế trên 54,674,003 dòng và phân tích chi tiết bản chất của mọi nhóm bản ghi bị trùng lặp.
2. **Xác minh phạm vi Codeshare (Codeshare Impact on Duplication):**
   Kiểm tra giả thuyết liệu các chuyến bay hợp tác liên danh thương mại (*codeshare agreements*) có tạo ra các bản ghi trùng lặp trong bộ dữ liệu CSV hay không.
3. **Thiết lập chính sách khử trùng lặp (Deduplication Policy):**
   Đánh giá rủi ro của việc tự động loại bỏ bản ghi (*naive deduplication*) và ban hành quy tắc hạch toán bản ghi cho pipeline xử lý PySpark ở G4/G5.

---

## 2. Kết quả kiểm toán Trùng lặp Khóa 9 năm (2016–2024)

### 2.1. Bảng số liệu kiểm toán tổng hợp

Lệnh thực thi:
```powershell
python tools/audit/audit_candidate_key.py 2016 2017 2018 2019 2020 2021 2022 2023 2024
```
Exit code: `0`. Tổng thời gian quét: $272.5\text{ giây}$. Dữ liệu kết quả được lưu tại [`tools/audit/candidate_key_audit_summary.json`](../../tools/audit/candidate_key_audit_summary.json).

| Năm | Tổng số bản ghi ($N$) | Khóa duy nhất ($K$) | Số khóa trùng lặp | Số bản ghi trùng lặp | Tỷ lệ bản ghi trùng lặp | Phân bố bậc lặp (*Multiplicity*) | Nhóm trùng 100% dòng | Nhóm khác biệt vận hành |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **2016** | 5,537,987 | 5,537,987 | 0 | 0 | 0.000000% | `{1: 5,537,987}` | 0 | 0 |
| **2017** | 5,575,872 | 5,575,872 | 0 | 0 | 0.000000% | `{1: 5,575,872}` | 0 | 0 |
| **2018** | 6,986,842 | 6,986,841 | **1** | **2** | **0.000029%** | `{1: 6,986,840, 2: 1}` | 0 | **1** |
| **2019** | 7,161,827 | 7,161,827 | 0 | 0 | 0.000000% | `{1: 7,161,827}` | 0 | 0 |
| **2020** | 4,312,091 | 4,312,091 | 0 | 0 | 0.000000% | `{1: 4,312,091}` | 0 | 0 |
| **2021** | 5,755,666 | 5,755,666 | 0 | 0 | 0.000000% | `{1: 5,755,666}` | 0 | 0 |
| **2022** | 6,413,416 | 6,413,416 | 0 | 0 | 0.000000% | `{1: 6,413,416}` | 0 | 0 |
| **2023** | 6,645,461 | 6,645,461 | 0 | 0 | 0.000000% | `{1: 6,645,461}` | 0 | 0 |
| **2024** | 6,284,841 | 6,284,841 | 0 | 0 | 0.000000% | `{1: 6,284,841}` | 0 | 0 |
| **TỔNG** | **54,674,003** | **54,674,002** | **1** | **2** | **0.000004%** | — | **0** | **1** |

#### 2.2. Chuẩn hóa Định nghĩa và Công thức Tính các Tỷ lệ Duy nhất (F03 Resolution)

Để tránh nhầm lẫn khái niệm và thống nhất thuật toán, các tỷ lệ liên quan đến tính đơn nhất của khóa được xác định rạch ròi theo 4 công thức:

1. **Tỷ lệ bao phủ khóa duy nhất trên tổng số dòng (Key-to-Row Ratio):**
   $$\text{Key-to-Row Ratio} = \frac{K}{N} = \frac{\text{distinct\_candidate\_keys}}{\text{raw\_row\_count}} = \frac{54,674,002}{54,674,003} \approx \mathbf{99.99999817\%}$$
2. **Tỷ lệ bản ghi có khóa duy nhất tuyệt đối (Strictly Unique Record Rate):**
   $$\text{Strictly Unique Record Rate} = \frac{N - D_{\text{rows}}}{N} = \frac{54,674,001}{54,674,003} \approx \mathbf{99.99999634\%}$$
3. **Tỷ lệ bản ghi thuộc nhóm khóa trùng lặp (Duplicate Record Rate):**
   $$\text{Duplicate Record Rate} = \frac{D_{\text{rows}}}{N} = \frac{2}{54,674,003} \approx \mathbf{0.00000366\%} \quad (3.66 \times 10^{-6}\%)$$
4. **Tỷ lệ khóa bị trùng lặp trên tổng số khóa duy nhất (Duplicate Key Ratio):**
   $$\text{Duplicate Key Ratio} = \frac{D_{\text{keys}}}{K} = \frac{1}{54,674,002} \approx \mathbf{0.00000183\%} \quad (1.83 \times 10^{-6}\%)$$

*Nhận định thực nghiệm:*
- Số nhóm bản ghi trùng lặp 100% tất cả 34 cột (*Exact Full-Row Duplicates*) là **0**. Cả 2 bản ghi có cùng khóa ứng viên đều có sự khác biệt rõ rệt về dữ liệu vận hành thực tế.
- Số bản ghi có năm trong `FL_DATE` không khớp với `source_year` là **0** (`year_mismatch_count = 0`), xác nhận không có hiện tượng giao thoa khóa xuyên năm.

---

## 3. Nghiên cứu trường hợp trùng lặp duy nhất năm 2018 (Case Study — F01 Resolution)

### 3.1. Đối chiếu trực tiếp giá trị trích xuất từ CSV thô

Khóa bị trùng lặp:
$$\text{Key} = (\text{FL\_DATE: } \text{"2018-06-21 00:00:00"}, \text{OP\_CARRIER: } \text{"YX"}, \text{OP\_CARRIER\_FL\_NUM: } \text{"3624.0"}, \text{ORIGIN: } \text{"DEN"}, \text{DEST: } \text{"XNA"}, \text{CRS\_DEP\_TIME: } \text{"2018-06-21 20:07:00"})$$

Đối chiếu trực tiếp từng trường dữ liệu tại hai dòng liên tiếp trong `data/raw/tabular/2018/flight_with_weather_2018.csv`:

| Trường dữ liệu | Dòng 6,384,132 (Dòng hoãn sâu) | Dòng 6,384,133 (Dòng tối thường lệ) | Khác biệt kỹ thuật thực tế |
|---|---|---|:---:|
| `FL_DATE` | `2018-06-21 00:00:00` | `2018-06-21 00:00:00` | Trùng |
| `OP_CARRIER` | `YX` (Republic Airline) | `YX` (Republic Airline) | Trùng |
| `OP_CARRIER_FL_NUM` | `3624.0` | `3624.0` | Trùng |
| `ORIGIN` $\to$ `DEST` | `DEN` $\to$ `XNA` | `DEN` $\to$ `XNA` | Trùng |
| `CRS_DEP_TIME` | `2018-06-21 20:07:00` | `2018-06-21 20:07:00` | Trùng |
| `CRS_ARR_TIME` | `2018-06-21 23:05:00` | `2018-06-21 23:05:00` | Trùng |
| **`DEP_TIME`** | **`2018-06-21 10:44:00`** | **`2018-06-21 20:27:00`** | **Khác 9 giờ 43 phút** |
| **`DEP_DELAY`** | **`877.0`** *(hoãn 14 giờ 37 phút)* | **`20.0`** *(hoãn 20 phút)* | **Khác 857 phút** |
| `TAXI_OUT` | `91.0` | `13.0` | Khác 78 phút |
| `WHEELS_OFF` | `2018-06-21 12:15:00` | `2018-06-21 20:40:00` | Khác 8 giờ 25 phút |
| `WHEELS_ON` | `2018-06-21 14:39:00` | `2018-06-21 23:03:00` | Khác 8 giờ 24 phút |
| `TAXI_IN` | `7.0` | `6.0` | Khác 1 phút |
| **`ARR_TIME`** | **`2018-06-21 14:46:00`** | **`2018-06-21 23:09:00`** | **Khác 8 giờ 23 phút** |
| **`ARR_DELAY`** | **`941.0`** *(đến trễ 15 giờ 41 phút)* | **`4.0`** *(đến trễ 4 phút)* | **Khác 937 phút** |
| `CRS_ELAPSED_TIME` | `118.0` | `118.0` | Trùng (118 phút) |
| `ACTUAL_ELAPSED_TIME` | `182.0` | `102.0` | Khác 80 phút ($91+84+7=182$ vs $13+83+6=102$) |
| `AIR_TIME` | `84.0` | `83.0` | Khác 1 phút (~83-84 phút bay thực tế) |
| `FLIGHTS` | `1.0` | `1.0` | Trùng (hằng số 1.0) |
| `O_TEMP` / `D_TEMP` | `27.8` / `29.4` | `27.8` / `29.4` | Trùng thời tiết |

### 3.2. Đánh giá Khoa học về Bản chất Nghiệp vụ
1. **Những điều đã được chứng minh (`VERIFIED`):**
   - Hai dòng 6384132 và 6384133 trong CSV thô trùng hoàn toàn 6 trường của candidate key.
   - Hai dòng có dữ liệu vận hành hoàn toàn khác biệt; dòng 6384132 có độ trễ khởi hành 877 phút và độ trễ đến 941 phút.
2. **Quan sát số học về thời gian (`INFERRED_ARITHMETIC`):**
   - $20:07 + 877 \text{ phút} = 20:07 + 14\text{h } 37\text{m} = \text{10:44 sáng ngày hôm sau}$.
   - Chuỗi `DEP_TIME` mang giá trị `2018-06-21 10:44:00` thể hiện date component bị cố định theo `FL_DATE` mà không được tăng ngày sang 22/06 (đây là hiện tượng rollover đã được ghi nhận trong thiết kế).
3. **Giới hạn kết luận (`UNKNOWN / NOT_VERIFIED`):**
   - Do bộ dữ liệu 34 cột **không có trường số hiệu máy bay (`TAIL_NUM`)**, số hiệu chặng bay nội bộ hãng hay mã định danh hành trình gốc của DOT, **chưa thể khẳng định chắc chắn** đây là "hai chuyến bay vật lý độc lập" (2 tàu bay khác nhau), hay "cùng một tàu bay bị dời lịch sâu", hay "sai lệch khai báo trong hồ sơ báo cáo gốc".
   - Bản chất sự kiện vật lý được phân loại là **`UNKNOWN`** và bàn giao cho nhiệm vụ **T-004** rà soát thời gian.

### 3.3. Hậu quả nghiêm trọng nếu Khử trùng lặp tự động (Danger of Naive Dedup)
- Nếu áp dụng quy tắc khử trùng lặp tùy tiện (`drop_duplicates(subset=candidate_key)`):
  - Nếu loại bỏ Dòng 6384132: Một sự kiện trễ nghiêm trọng (+941 phút) bị xóa bỏ khỏi dữ liệu, làm giảm giả tạo độ trễ trung bình, bóp méo phân vị P90 và vi phạm quy định chống ẩn giấu dữ liệu cực trị ([AGENTS.md](../../AGENTS.md)).
  - Nếu loại bỏ Dòng 6384133: Một chuyến bay đúng giờ hợp lệ bị loại bỏ, làm mẫu số $N$ bị hụt.
- **Quy tắc bảo vệ dữ liệu:** **Tuyệt đối cấm deduplicate tự động.** Cả 2 bản ghi đều phải được giữ lại trong tập dữ liệu thô.

---

## 4. Xác minh phạm vi Codeshare (T-002.3 — F02 Resolution)

1. **Cấu trúc trường trong dữ liệu:**
   - Tập dữ liệu 34 cột chỉ lưu trữ trường `OP_CARRIER` (Mã hãng khai thác thực tế) và `OP_CARRIER_FL_NUM`.
   - Hoàn toàn **không có cột `MKT_CARRIER`** (Hãng tiếp thị / xuất vé) hay `MKT_CARRIER_FL_NUM`.
2. **Rà soát kết luận về Codeshare:**
   - Báo cáo trước đây nhận định giả thuyết codeshare bị "bác bỏ hoàn toàn bằng thực nghiệm" (`REFUTED_BY_EMPIRICAL_DATA`). Kết luận này **chưa chặt chẽ về phương pháp luận khoa học**.
   - Khóa ứng viên chứa `OP_CARRIER`. Nếu một chuyến bay liên danh được tiếp thị bởi hãng lớn (ví dụ `AA`) nhưng do hãng khu vực (`YX`) khai thác:
     - Nếu upstream đã chuẩn hóa và chỉ trích xuất bản ghi của hãng khai thác (`YX`), ta sẽ không thấy bản ghi nào mang mã `AA`.
     - Nếu có tồn tại bản ghi marketing mang mã `AA` cùng giờ bay, chúng sẽ có `OP_CARRIER` khác nhau (hoặc bị ghi đè), do đó candidate key chứa `OP_CARRIER` sẽ có giá trị khác nhau và không thể phát hiện trùng lặp bằng candidate key này.
   - Cần làm rõ (C03 Resolution): Trong dữ liệu có tồn tại **đúng một nhóm trùng candidate key thuộc cùng hãng khai thác `OP_CARRIER = YX`** (năm 2018). Cặp trùng này khác biệt về mốc giờ vận hành thực tế do hoãn sâu, không phải do trùng lặp dữ liệu codeshare.
   - Ngoại trừ trường hợp đơn lẻ trên, không quan sát thấy hiện tượng trùng lặp khóa mang tính hệ thống nào khác trong cùng hãng khai thác.
   - Việc các chuyến bay liên danh codeshare có bị trích xuất trùng lặp dưới các mã hãng khác nhau (ví dụ một bản ghi tiếp thị mang mã hãng lớn và một bản ghi khai thác mang mã hãng khu vực) hay không là **hoàn toàn không thể xác định được từ các trường hiện có (`NOT_DETERMINABLE_FROM_AVAILABLE_FIELDS`)**, do thiếu trường tiếp thị (`MKT_CARRIER`), số hiệu máy bay (`TAIL_NUM`) hoặc mã định danh hành trình gốc của DOT.
3. **Chính sách:** Không tự ý loại bỏ hay hợp nhất bất kỳ bản ghi nào dựa trên suy luận codeshare.

---

## 5. Chính sách Khử trùng lặp chính thức (Deduplication Policy)

Tuân thủ quy định tại [`DATA_CONTRACT.md`](../02-design/DATA_CONTRACT.md) DC-10:
1. **Chính sách Zero Arbitrary Deduplication:**
   - Toàn bộ 54,674,003 bản ghi đầu vào được giữ nguyên vẹn 100%. Không thực hiện xóa, lọc bỏ hoặc hợp nhất bất kỳ dòng nào vì lý do trùng khóa nghiệp vụ ứng viên.
2. **Quy định hạch toán bản ghi:**
   - Mọi bản ghi hợp lệ đều được hạch toán vào `accepted_row_count`.
   - Pipeline PySpark ở G4/G5 sẽ định danh bản ghi bằng một mã định danh kỹ thuật duy nhất ổn định (`flight_row_id` hoặc partition offset) theo TS-020 thay vì dựa vào khóa ứng viên làm primary key cứng.
3. **Quy tắc thiết kế kiểm thử tại G4/G5 (Test Fixture Design Scope — C05 Resolution):**
   - Các bài kiểm thử `TS-009` (G2 design / G5 execution), `TS-012` (G5 execution) và `TS-020` (G4 synthetic / G6 full) trong [`TEST_PLAN.md`](../03-quality/TEST_PLAN.md) hiện đang ở trạng thái **thiết kế quy tắc (*SPECIFIED / DESIGN_BASELINE*)**, chưa phải test code đã thực thi trên production.
   - Bài kiểm thử `TS-009` và `TS-012` sẽ đưa trường hợp YX 3624 (2018) vào bộ kiểm thử chuẩn (*test fixture*) để bảo đảm pipeline không vô tình loại bỏ các chuyến bay hoãn sâu.
