# T011_FULL_BTS_PARITY_RECONCILIATION — BÁO CÁO THỰC THI KHUNG ĐỐI SOÁT TS-018 BTS TRANSTATS VÀ HIỆN TRẠNG NGOẠI LỆ G2-EXC-001

- **Mã nhiệm vụ:** `T-011` (Gate G5: KPI Sample Smoke, BTS Parity, TS-008, TS-013 & Review Packaging)
- **Gate:** `G5` (IN_PROGRESS)
- **Thời điểm kiểm toán:** 2026-10-18T20:56:30+07:00
- **Tiêu chuẩn tuân thủ:** [`AGENTS.md`](../../AGENTS.md), [`TEST_PLAN.md`](../03-quality/TEST_PLAN.md) (TS-018), [`G2_OFFICIAL_SIGNOFF_HUMAN_ACCEPTANCE_RECORD.md`](G2_OFFICIAL_SIGNOFF_HUMAN_ACCEPTANCE_RECORD.md) (G2-EXC-001), [`DECISIONS.md`](../02-design/DECISIONS.md) (FP-DEC-012, OR-03).
- **Trạng thái Gate 4:** **PASS (Reconciliation Harness Verified; Authentic BTS Parity Classified as BLOCKED_BEFORE_G6)**

---

## 1. BỐI CẢNH VÀ NGHĨA VỤ PHÁP LÝ CỦA NGOẠI LỆ G2-EXC-001

1. **Trạng thái Hiện hành của 7 Trường Đo Cốt lõi (CORE Measures):**
   - 7 trường số đo gốc: `ARR_DELAY`, `DEP_DELAY`, `TAXI_OUT`, `TAXI_IN`, `AIR_TIME`, `ACTUAL_ELAPSED_TIME`, `CRS_ELAPSED_TIME`.
   - Trạng thái pháp lý chuẩn tắc: **`OFFICIAL_MINUTES_EMPIRICALLY_CONSISTENT_PROVISIONAL`** (`OR-03`, rủi ro chính `R-15`).
   - Tuyệt đối **không được gán nhãn `VERIFIED`** cho đơn vị phút khi chưa có đối soát thực tế từng bản ghi với cổng BTS TranStats.
2. **Điều kiện Tiên quyết Chặn Gate G6 (Mandatory Hard Blocker):**
   - Theo Ngoại lệ `G2-EXC-001` được phê duyệt tại `FP-DEC-012`, bài kiểm thử `TS-018` **bắt buộc phải đạt `PASS` tại Gate G5** trước khi được phép mở pipeline xử lý toàn diện 9 năm tại Gate G6 (`T-012`) hoặc xuất bản kết quả cuối cùng.
   - Nếu `TS-018` chưa PASS hoặc bị chặn $\implies$ **TOÀN BỘ PIPELINE SẢN XUẤT GATE G6 BỊ KHÓA HOÀN TOÀN**.

---

## 2. KẾT QUẢ RÀ SOÁT TÀI NGUYÊN NGUỒN BTS TRONG KHO LƯU TRỮ

Kiểm toán độc lập đã quét toàn diện hệ thống thư mục (`docs/05-evidence/inputs/`, `data/`, v.v.):
- **Hiện trạng:** Kho lưu trữ hiện tại **CHƯA CÓ bất kỳ tệp dữ liệu mẫu nào được tải về từ cổng thông tin BTS TranStats chính thức** (On-Time Marketing Carrier hoặc Reporting Carrier On-Time Performance).
- **Tuân thủ Chính sách Chống Giả mạo (`AGENTS.md`):**
  - Cấm tự dùng dữ liệu giả lập tổng hợp (synthetic) để tuyên bố `TS-018 PASS`.
  - Cấm tự tải dữ liệu mạng không được kiểm soát mà chưa có sự phê duyệt provenance từ Project Lead.
  - Phân định rõ ràng: **Khung công cụ đối soát (Reconciler Engine) đã hoàn thành và đạt kiểm chuẩn thuật toán 100%**, nhưng **phép đối soát dữ liệu thực tế (Authentic BTS Parity) được phân loại trung thực là `PENDING_EXTERNAL_BTS_SOURCE / BLOCKED_BEFORE_G6`**.

---

## 3. THIẾT KẾ KHUNG CÔNG CỤ ĐỐI SOÁT (`src/flight_pipeline/kpi/bts_reconciler.py`)

Khung công cụ `BtsTranStatsReconciler` được xây dựng với các cơ chế kiểm chuẩn cấp cao:
1. **Khóa đối chiếu kết hợp (Composite Key):**
   - `(FL_DATE, OP_CARRIER, OP_CARRIER_FL_NUM, ORIGIN, DEST)`.
   - Chuẩn hóa định dạng ngày `YYYY-MM-DD`, mã hãng hàng không (IATA/DOT 2 ký tự), số hiệu chuyến bay (DoubleType/float), và mã sân bay 3 ký tự.
2. **Cơ chế phát hiện và xử lý trùng lặp / mơ hồ (Duplicate & Ambiguity Handling):**
   - Quét độc lập trên cả hai phía (dataset và BTS).
   - Nếu một khóa xuất hiện nhiều hơn 1 lần trên một trong hai phía (chẳng hạn cặp chuyến bay trùng khóa duy nhất `YX 3624` theo `OR-02`), reconciler **tuyệt đối không tự ý lấy bản ghi đầu tiên**, mà phân loại thành **`AMBIGUOUS_DUPLICATE`** và loại khỏi tập so sánh 1-1.
3. **Phân loại sai lệch chi tiết (Mismatch Categorization):**
   - `EXACT_MATCH`: Khớp tuyệt đối sai số $\Delta = 0.0$.
   - `ROUNDING_DIFF`: Sai lệch nằm trong dung sai số thực $|\Delta| \le 10^{-4}$.
   - `SCALE_DIFF`: Phát hiện sai lệch hệ đo theo tỷ lệ (ví dụ: lệch hệ số 60 giữa giây và phút).
   - `SIGN_MISMATCH`: Sai lệch dấu (một bên âm, một bên dương).
   - `MISSINGNESS_MISMATCH`: Một bên có giá trị, bên kia là null.
   - `NULL_NULL_AGREEMENT`: Cả hai bên đều null (ghi nhận độc lập, **không đánh đồng với việc xác minh đơn vị số**).
   - `VALUE_MISMATCH`: Giá trị số khác biệt không giải thích được.

---

## 4. KẾT QUẢ KIỂM CHUẨN THỰC THI (SYNTHETIC FIXTURE AUDIT)

Công cụ kiểm chuẩn QA `tools/qa/run_ts018_bts_parity.py` và bộ kiểm thử `tests/test_t011_ts018_bts_parity.py` (5 tests PASS) đã chứng minh độ chính xác thuật toán:
- **Tổng số bản ghi đối chiếu mẫu:** 5 bản ghi dataset, 4 bản ghi BTS fixture.
- **Khớp 1-1 duy nhất (Unique Key Matches):** 3 cặp bản ghi.
- **Khóa trùng lặp mơ hồ (Ambiguous Duplicate Keys):** 1 cặp bản ghi (`YX 3624`) được cách ly chính xác.
- **Tỷ lệ khớp 7 trường đo CORE trên các cặp duy nhất:**
  - `ARR_DELAY`: 3/3 EXACT_MATCH (100.0%)
  - `DEP_DELAY`: 3/3 EXACT_MATCH (100.0%)
  - `TAXI_OUT`: 3/3 EXACT_MATCH (100.0%)
  - `TAXI_IN`: 3/3 EXACT_MATCH (100.0%)
  - `AIR_TIME`: 3/3 EXACT_MATCH (100.0%)
  - `ACTUAL_ELAPSED_TIME`: 3/3 EXACT_MATCH (100.0%)
  - `CRS_ELAPSED_TIME`: 3/3 EXACT_MATCH (100.0%)
- **Phán quyết kết xuất tệp JSON:** `docs/05-evidence/T011_TS018_BTS_RECONCILIATION_SUMMARY.json`:
  `reconciliation_verdict = "SYNTHETIC_RECONCILER_VERIFIED_AUTHENTIC_BTS_PENDING"`.

---

## 5. TÁC ĐỘNG QUẢN TRỊ ĐỐI VỚI G2-EXC-001 VÀ GATE G6

1. **Trạng thái Đơn vị Đo 7 Trường CORE:**
   - Tiếp tục duy trì trạng thái: **`OFFICIAL_MINUTES_EMPIRICALLY_CONSISTENT_PROVISIONAL`**.
   - Cấm chuyển sang `VERIFIED`.
2. **Khóa Chặn Gate G6:**
   - Gate G6 tiếp tục duy trì trạng thái **`BLOCKED / NOT_STARTED`**.
   - Pipeline không được phép chạy full 9 năm cho đến khi Project Lead cung cấp tệp dữ liệu mẫu BTS chính thức và xác thực thành công qua runner `tools/qa/run_ts018_bts_parity.py`.
3. **Yêu cầu Bàn giao Dữ liệu Đối với Project Lead:**
   Để gỡ bỏ điểm chặn TS-018, Project Lead cần tải và cung cấp tệp CSV mẫu từ cổng BTS TranStats chính thức:
   - URL: `https://www.transtats.bts.gov/DL_SelectFields.aspx?QO_fu146_anzr=&gnoyr_VQ=FGJ`
   - Bảng: *Reporting Carrier On-Time Performance (1987-present)*.
   - Các trường cần xuất: `FlightDate`, `Reporting_Airline`, `Flight_Number_Reporting_Airline`, `Origin`, `Dest`, `ArrDelay`, `DepDelay`, `TaxiOut`, `TaxiIn`, `AirTime`, `ActualElapsedTime`, `CRSElapsedTime`.
   - Vị trí khuyến nghị đặt tệp: `docs/05-evidence/inputs/bts_transtats_sample.csv`.

---

## 6. KẾT LUẬN GATE 4

- Khung đối soát kỹ thuật `BtsTranStatsReconciler` và script runner độc lập `run_ts018_bts_parity.py` đã hoàn thành 100%, sẵn sàng thực thi ngay khi có dữ liệu thật.
- Báo cáo và tệp tóm tắt JSON phản ánh trung thực hiện trạng không có dữ liệu thật bên ngoài, tuân thủ tuyệt đối quy định liêm chính học thuật.
- **GATE 4 ĐẠT KIỂM CHUẨN KỸ THUẬT (PASS AT TECHNICAL LEVEL), ĐỒNG THỜI BẢO LƯU ĐIỂM CHẶN TS-018 TRƯỚC GATE G6.**
