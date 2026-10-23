# TS018_FINAL_R1_FINDINGS_REPRODUCTION.md
# Báo Cáo Tái Hiện Bằng Chứng Forensic Độc Lập Các Phát Hiện F01–F07

**Dự án:** US Flight Performance Analysis 2016–2024  
**Nhiệm vụ:** TS-018 / G5 Final Evidence Integrity Review (R1 Correction)  
**Tác giả:** Principal Big Data Engineer, Independent Forensic Evidence Auditor, Senior PySpark QA Engineer  
**Thời điểm lập:** 2026-10-20  
**Thẩm quyền:** Báo cáo kỹ thuật độc lập; thẩm quyền phê duyệt chính thức thuộc về Project Lead.

---

## 1. MỤC TIÊU VÀ PHẠM VI
Tài liệu này ghi nhận kết quả tái hiện độc lập dựa trên dữ liệu vật lý và mã nguồn đối với toàn bộ 7 phát hiện kiểm toán (F01–F07) được nêu trong chỉ thị `MASTER AGENT PROMPT — TS-018 / G5 FINAL EVIDENCE INTEGRITY CORRECTION`. Mọi kết luận đều được kiểm chứng đối soát trực tiếp với các tệp nguồn thô, tệp tham chiếu BTS TranStats chính thức và mã nguồn thực tế.

---

## 2. BẢNG TỔNG HỢP TRẠNG THÁI TÁI HIỆN VÀ XỬ LÝ (F01–F07)

| Mã phát hiện | Mức độ nghiêm trọng | Trạng thái tái hiện (Reproduction) | Trạng thái xử lý (Correction) | Tồn đọng (Remaining) |
| :--- | :---: | :---: | :---: | :--- |
| **F01** | CRITICAL | **CONFIRMED** | **CORRECTED** | Không có. Đã đối soát đúng 7 trường số CORE đã duyệt. |
| **F02** | HIGH | **CONFIRMED** | **CORRECTED** | Không có. Đã đối soát 3 ví dụ thực tế có trong witness và 2 nguồn. |
| **F03** | HIGH | **CONFIRMED** | **CORRECTED** | Không có. Đã tách 5 hạng mục số học và kiểm chứng IEEE-754 bitwise. |
| **F04** | MEDIUM/HIGH | **CONFIRMED** | **CORRECTED** | Không có. Đã cập nhật bộ 10 negative tests khớp 1-1 với mô tả và code. |
| **F05** | MEDIUM/HIGH | **CONFIRMED** | **CORRECTED** | Không có. Đã chứng minh bằng toán học lý do phân tầng TOPUP toàn bộ âm. |
| **F06** | HIGH GOVERNANCE | **CONFIRMED** | **CORRECTED** | Không có. Đã đính chính G2-EXC-001 là hoãn đối chiếu BTS 7 trường CORE. |
| **F07** | G6 READINESS | **CONFIRMED** | **CORRECTED** | Đo lại đĩa (59.46 GiB), lập ma trận khoảng cách triển khai G6 thực tế. |

---

## 3. CHI TIẾT TÁI HIỆN TỪNG PHÁT HIỆN

### F01 — Danh sách 7 trường đo số cốt lõi TS-018
- **Tái hiện:** Trong báo cáo tổng kết trước đó, danh sách trường được liệt kê nhầm thành: `DEP_DELAY`, `ARR_DELAY`, `CARRIER_DELAY`, `WEATHER_DELAY`, `NAS_DELAY`, `SECURITY_DELAY`, `LATE_AIRCRAFT_DELAY`.
- **Căn cứ sự thật (Ground Truth):**
  - Quyết định `FP-DEC-012` và ngoại lệ `G2-EXC-001` trong `docs/02-design/DECISIONS.md`.
  - Hợp đồng dữ liệu `docs/02-design/DATA_CONTRACT.md` (Mục DC-02, DC-03).
  - Module đối chiếu chuẩn `src/flight_pipeline/kpi/bts_reconciler.py`.
  - Tệp mẫu chứng thực [TS018_201901_MATCHED_SAMPLE_WITNESS.csv](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/docs/05-evidence/TS018_201901_MATCHED_SAMPLE_WITNESS.csv).
- **Danh sách 7 trường số CORE được phê duyệt chính thức:**
  1. `ARR_DELAY`
  2. `DEP_DELAY`
  3. `TAXI_OUT`
  4. `TAXI_IN`
  5. `AIR_TIME`
  6. `ACTUAL_ELAPSED_TIME`
  7. `CRS_ELAPSED_TIME`
- **Kết luận:** Bộ 7 trường trên tệp witness vật lý và công cụ kiểm chứng đã luôn dùng đúng 7 trường CORE này. Sự sai lệch nằm ở văn bản báo cáo và các dự thảo trước đó.

---

### F02 — Ba ví dụ chuyến bay trong báo cáo tổng kết
- **Tái hiện trên tệp BTS ZIP và CSV gốc năm 2019:**
  - Ngày sai được báo cáo trước đó:
    - `2019-01-20 | NK | 314 | IAH | TPA`: BTS và CSV thực tế có `ARR_DELAY = -9.0` (Báo cáo cũ ghi `-16.0`).
    - `2019-01-05 | UA | 753 | SFO | EWR`: BTS và CSV thực tế có `ARR_DELAY = +171.0` (Báo cáo cũ ghi `0.0`).
    - `2019-01-07 | AA | 692 | PHX | HNL`: BTS và CSV thực tế có `ARR_DELAY = -2.0` (Báo cáo cũ ghi `+1186.0`).
    - Cả 3 khóa sai ngày này không nằm trong tập witness 1.500 bản ghi.
  - Ngày chính xác có trong tập witness:
    - `2019-01-10 | NK | 314 | IAH | TPA`: `ARR_DELAY = -6.0`, `DEP_DELAY = -4.0`, `TAXI_OUT = 13.0`, `TAXI_IN = 8.0`, `AIR_TIME = 98.0`, `ACTUAL_ELAPSED_TIME = 119.0`, `CRS_ELAPSED_TIME = 121.0` (Khớp 100% giữa CSV và BTS).
    - `2019-01-31 | UA | 753 | SFO | EWR`: `ARR_DELAY = 0.0`, `DEP_DELAY = 0.0`, `TAXI_OUT = 24.0`, `TAXI_IN = 10.0`, `AIR_TIME = 295.0`, `ACTUAL_ELAPSED_TIME = 329.0`, `CRS_ELAPSED_TIME = 329.0` (Khớp 100% giữa CSV và BTS).
    - `2019-01-21 | AA | 692 | PHX | HNL`: `ARR_DELAY = 1186.0`, `DEP_DELAY = 1191.0`, `TAXI_OUT = 28.0`, `TAXI_IN = 17.0`, `AIR_TIME = 364.0`, `ACTUAL_ELAPSED_TIME = 409.0`, `CRS_ELAPSED_TIME = 414.0` (Khớp 100% giữa CSV và BTS).

---

### F03 — Phân biệt Exact Numeric Equality vs Tolerance
- **Tái hiện:** Trước khi sửa, công cụ `verify_ts018_two_source_sample_witness.py` áp dụng điều kiện `abs(a - b) > 1e-4` và ghi nhận kết quả là `Exact Matches: 10500`, gộp chung các so sánh trong ngưỡng tolerance vào nhóm exact match.
- **Khắc phục:** Đã tách thành 5 phân loại chuẩn mực:
  1. `EXACT_NUMERIC_MATCH`: Khớp tuyệt đối cả về số học và biểu diễn nhị phân IEEE-754 64-bit (`diff == 0.0`).
  2. `TOLERANCE_ONLY_MATCH`: Không bằng nhau tuyệt đối nhưng $0 < |a - b| \le 10^{-4}$.
  3. `NULL_NULL_AGREEMENT`: Cả 2 giá trị đều là null/None hợp lệ.
  4. `MISMATCH`: Sai lệch $> 10^{-4}$ hoặc bất đồng null/giá trị.
  5. `NONFINITE_OR_PARSE_ERROR`: Giá trị NaN, Inf hoặc lỗi chuyển đổi.
- **Kết quả kiểm toán thực tế 10.500 so sánh:**
  - `EXACT_NUMERIC_MATCH`: **10.500**
  - `TOLERANCE_ONLY_MATCH`: **0**
  - `NULL_NULL_AGREEMENT`: **0**
  - `MISMATCH`: **0**
  - `NONFINITE_OR_PARSE_ERROR`: **0**
  - Sai lệch bitwise IEEE-754 signed zero (`+0.0` vs `-0.0`): **0**

---

### F04 — Đồng bộ mã nguồn Negative Tests
- **Tái hiện:** Báo cáo cũ mô tả NEG-W02 là thử sai lệch `+0.00005` (trong khi code thử khóa không tồn tại) và NEG-W06 là thay null thành 0 (trong khi code thay TAXI_OUT 13.0 thành 0.0).
- **Khắc phục:** Đã mở rộng bộ test thành **10 kịch bản độc lập (NEG-W01 đến NEG-W10)** trong [tools/qa/test_ts018_negative_witness_verification.py](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/tools/qa/test_ts018_negative_witness_verification.py). Từng test có mô tả, hành vi đột biến (mutation) và thông báo từ chối (rejection reason) khớp nhau tuyệt đối và đều đạt `PASS` (bị chặn fail-closed với exit code 1).

---

### F05 — Bản chất toán học của phân tầng REMAINDER_TOPUP
- **Tái hiện:** 100/100 chuyến bay trong nhóm `REMAINDER_TOPUP` đều có `ARR_DELAY < 0`. Nếu giả định bốc thăm độc lập từ quần thể có 64,17% âm, xác suất $0.6417^{100} \approx 5.4 \times 10^{-20}$.
- **Chứng minh cơ chế toán học:**
  1. Phân tầng `POSITIVE_DELAY` lấy chỉ tiêu 700 chuyến. Do quần thể dương ít hơn (~180.000 chuyến), điểm băm cắt (hash cutoff) của phân tầng dương bị đẩy xa tới `0x00e05f39ed21...`.
  2. Phân tầng `NEGATIVE_DELAY` lấy chỉ tiêu 500 chuyến (trên quần thể ~358.000 chuyến), điểm băm cắt chỉ ở mức `0x005f1ca983f6...`.
  3. Khi tạo tập phần dư `remainder = population - picked_keys`, toàn bộ các chuyến bay dương có điểm băm $\le \text{0x00e05f39...}$ **đã bị bốc hết vào phân tầng POSITIVE_DELAY**.
  4. Thuật toán sắp xếp `remainder` theo điểm băm tăng dần và lấy 100 phần tử đầu tiên.
  5. 100 phần tử đầu tiên của tập phần dư nằm trong khoảng `[0x005f8998..., 0x00747c6f...]`.
  6. Vì `0x00747c6f... < 0x00e05f39...`, trong khoảng này **về mặt toán học không thể tồn tại bất kỳ chuyến bay dương nào**.
  7. Do đó, 100 bản ghi được chọn chắc chắn 100% chỉ có thể là chuyến bay âm (hoặc chuyến đúng giờ nếu rơi trúng). Đây là hệ quả tất yếu của việc cắt ngưỡng có điều kiện phi đối xứng, hoàn toàn không phải bốc thăm độc lập.
- **Xác minh Seed:** Seed thực tế sử dụng trong adapter và sinh ra 100% điểm băm trong tệp witness là `ts018_bts_jan2019_seed_42` (không phải seed chuỗi ghi nhầm trong báo cáo cũ).

---

### F06 — Đính chính định nghĩa ngoại lệ G2-EXC-001
- **Tái hiện:** Báo cáo cũ mô tả G2-EXC-001 là "Midnight Rollover".
- **Ground Truth:** Theo `DECISIONS.md` (`FP-DEC-012`), `G2-EXC-001` là ngoại lệ kỹ thuật có kiểm soát cho phép **hoãn việc đối chiếu đơn vị đo lường 7 trường số cốt lõi với nguồn BTS TranStats đến Gate G5 (thông qua nhiệm vụ TS-018) trước khi được phép chạy full-run Gate G6**. Ngoại lệ này tiếp tục duy trì trạng thái `ACTIVE` có kiểm soát.

---

### F07 — Khoảng cách vận hành Gate G6 / Task T-012
- **Tái hiện:** Kế hoạch G6 trước đó tham chiếu tập lệnh chưa có `tools/qa/verify_staging_pointer.py`, chưa đo đạc lại đĩa cứng thực tế tại thời điểm chạy và ước tính thời gian 49,5–60 phút là ngoại suy chưa có hệ số an toàn.
- **Khắc phục:**
  - Đo đạc lại dung lượng Drive D: **59,46 GiB** khả dụng ($63.848.439.808$ bytes).
  - Xác nhận phân vùng 2016 Staging hiện hữu (50 tệp) là baseline tham chiếu bất biến của T-010, việc xuất bản phân vùng 2016 trong G6 sẽ tuân thủ quy trình kiểm soát phiên bản riêng.
  - Lập tài liệu phân tích khoảng cách vận hành [G6_T012_FINAL_R1_OPERATIONAL_GAP_REVIEW.md](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/docs/05-evidence/G6_T012_FINAL_R1_OPERATIONAL_GAP_REVIEW.md).
