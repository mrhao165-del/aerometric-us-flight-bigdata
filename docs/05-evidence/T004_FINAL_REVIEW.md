# T-004: BÁO CÁO TỔNG KẾT VÀ HỒ SƠ NGHIỆM THU KIỂM TOÁN BIỂU DIỄN THỜI GIAN (T-004 FINAL REVIEW & GATE G2 PROGRESSION)

- **Mã nhiệm vụ:** `T-004` (Safe Time Representation & Overnight Operational Timestamps Audit)
- **Gate kiểm soát:** `G2` (Data Quality, Cohort & Metric Contracts)
- **Ngày hoàn thành:** 2026-10-14
- **Vai trò:** Senior Big Data Engineer, Data Quality Auditor & Technical Reviewer
- **Trạng thái nhiệm vụ:** **`AUDIT_COMPLETE / READY_FOR_REVIEWER_SIGNOFF`**
- **Trạng thái Gate G2:** **`IN_PROGRESS / NOT_PASSED`** (Chờ hoàn thành Task T-005)
- **Văn bản tuân thủ:** [`AGENTS.md`](../../AGENTS.md), [`docs/01-planning/BACKLOG.md`](../01-planning/BACKLOG.md), [`docs/02-design/DATA_CONTRACT.md`](../02-design/DATA_CONTRACT.md), [`docs/02-design/DATA_DICTIONARY.md`](../02-design/DATA_DICTIONARY.md), [`docs/02-design/DECISIONS.md`](../02-design/DECISIONS.md), [`docs/03-quality/TEST_PLAN.md`](../03-quality/TEST_PLAN.md) (`TS-004`, `TS-009`, `TS-010`), [`docs/04-execution/PROJECT_STATE.md`](../04-execution/PROJECT_STATE.md).

---

## 1. Tóm tắt Điều hành & Thành quả Kỹ thuật

Nhiệm vụ **T-004** đã hoàn thành toàn diện 100% phạm vi kiểm toán thời gian trên toàn bộ $54,674,003$ bản ghi của 9 tệp CSV thô (2016–2024), giải quyết triệt để các rủi ro kỹ thuật tiềm ẩn về chuỗi thời gian, hiện tượng vượt nửa đêm, và tính liên tục lịch:

1. **Kiểm toán Biểu diễn Chuỗi Thời gian (Sub-task 1):**
   - Đã xác minh thực nghiệm trên toàn bộ 9 năm: $100\%$ các trường thời gian đều được lưu trữ dưới dạng chuỗi ký tự `%Y-%m-%d %H:%M:%S`.
   - Khẳng định bất biến `FL_DATE`: $100\%$ bản ghi có thành phần giờ cố định bằng nửa đêm `00:00:00`.
   - Làm rõ ngữ nghĩa mốc 2400: Không có chuỗi `24:00:00` trong dữ liệu thô, duy trì trạng thái phân loại `2400_SEMANTICS_NOT_PROVEN` ([`T004_TIME_REPRESENTATION_AUDIT.md`](T004_TIME_REPRESENTATION_AUDIT.md)).
2. **Kiểm toán Độ bao phủ Lịch Năm Nhuận 2024 (Sub-task 2):**
   - **Phát hiện quan trọng:** Tháng 3 năm 2024 (`MONTH = 3`) hoàn toàn vắng mặt trong tập dữ liệu thô dẫn xuất ($0$ bản ghi, $0$ ngày từ 2024-03-01 đến 2024-03-31).
   - Số ngày lịch riêng biệt của năm 2024 trong tập dữ liệu là **$335$ ngày** (thay vì $366$ ngày chuẩn lịch năm nhuận).
   - Ngày nhuận `2024-02-29 00:00:00` có mặt đầy đủ với $18,642$ chuyến bay.
   - Tổng số dòng năm 2024 là $6,284,841$ dòng; $100\%$ giá trị `MONTH` khớp với thành phần tháng của `FL_DATE` (0 bất đồng).
   - Trạng thái phân loại: `DATA_ABSENT_IN_CURRENT_CSV (UPSTREAM_ROOT_CAUSE_UNKNOWN)`.
   - Giữ nguyên tham chiếu lịch 366 ngày cho kiểm thử `TS-004` (đánh giá `INCOMPLETE_COVERAGE / DEFECT_DETECTED`); không hạ ngưỡng kiểm thử để tạo PASS giả tạo.
   - Rủi ro **`OR-05`** chuyển sang trạng thái **`OPEN_QUALITY_DEFECT`** (chưa đóng) ([`T004_2024_DATE_COVERAGE_AUDIT.md`](T004_2024_DATE_COVERAGE_AUDIT.md)).
3. **Phân tích Hiện tượng Bay Qua Nửa Đêm & Phản ví dụ YX 3624 (Sub-task 3):**
   - Chứng minh toán học trên cặp dòng 6,384,132 và 6,384,133 của chuyến bay YX 3624 (2018-06-21 DEN $\to$ XNA).
   - Làm sáng tỏ cơ chế lỗi của upstream ETL: Kẹp cứng ngày xuất phát lịch trình vào toàn bộ các mốc giờ thực tế, làm biến dạng chuyến bay trễ 877 phút cất cánh lúc 10:44 sáng ngày 22/06 thành `2018-06-21 10:44:00`.
   - Chứng minh phép trừ chuỗi timestamp trực tiếp gây sai số thảm họa $1440$ phút (24 giờ), cho ra độ trễ âm $-563$ phút thay vì $+877$ phút.
   - Ban hành lệnh cấm tuyệt đối phép trừ timestamp trực tiếp và cấm tự ý cộng 24 giờ ([`T004_OVERNIGHT_COUNTEREXAMPLES.md`](T004_OVERNIGHT_COUNTEREXAMPLES.md)).
4. **Ma trận Phân loại Trường An toàn 4 Cấp độ (Sub-task 4):**
   - Ban hành ma trận phân loại an toàn cho toàn bộ 34 cột:
     - `SAFE_FOR_DIRECT_USE`: 17 cột (bao gồm `FL_DATE` làm service date và 7 thước đo số cốt lõi).
     - `SAFE_WITH_DOCUMENTED_TRANSFORMATION`: 2 cột (`CRS_DEP_TIME` trích xuất `CRS_DEP_HOUR` 0..23).
     - `CONDITIONALLY_USABLE`: 10 cột (`DEP_TIME`, `ARR_TIME`, và 6 trường thời tiết).
     - `NOT_AVAILABLE / BLOCKED`: Khóa phép trừ timestamp, khóa synthetic +24h, khóa Flight Chain (`FINAL — NO_GO`) ([`T004_SAFE_FIELDS_DECISION.md`](T004_SAFE_FIELDS_DECISION.md)).
5. **Đặc tả 9 Synthetic Fixtures cho TS-010 (Sub-task 5):**
   - Xây dựng 9 ca kiểm thử chuẩn hóa `TF-01` đến `TF-09` bao quát toàn bộ các kịch bản biên thời gian: bay ngày, red-eye qua đêm, trễ vận hành qua đêm, rạng sáng, đúng nửa đêm 00:00:00, năm nhuận, giao thừa, và bay qua múi giờ ([`T004_TEST_FIXTURE_SPEC.md`](T004_TEST_FIXTURE_SPEC.md)).

---

## 2. Bảng Đối chiếu với Tiêu chí Nghiệm thu BACKLOG v1.1

- **Tiêu chí nghiệm thu của Task T-004 trong BACKLOG v1.1:**
  > *"Safe-time representation audit, canonical schedule datetime, 2024 boundary, overnight/rollover counterexamples, safe fields decision, TS-010 specs"*
- **Kết quả đánh giá đối chiếu:**

| Thành phần tiêu chí | Kết quả đánh giá | Bằng chứng đối chiếu |
|---|:---:|---|
| *Safe-time representation audit* | **ĐẠT (PASS)** | Kiểm toán 100% định dạng `%Y-%m-%d %H:%M:%S`, kiểm tra tính toàn vẹn 54.67M dòng ([`T004_TIME_REPRESENTATION_AUDIT.md`](T004_TIME_REPRESENTATION_AUDIT.md)). |
| *Canonical schedule datetime* | **ĐẠT (PASS)** | Khẳng định `FL_DATE` tương đương service date, `CRS_DEP_TIME` trích xuất giờ an toàn ([`T004_TIME_REPRESENTATION_AUDIT.md`](T004_TIME_REPRESENTATION_AUDIT.md)). |
| *2024 boundary* | **ĐẠT (PASS)** | Phát hiện 335 ngày, khuyết thiếu Tháng 3/2024, xác minh 18,642 chuyến ngày 29/02/2024 ([`T004_2024_DATE_COVERAGE_AUDIT.md`](T004_2024_DATE_COVERAGE_AUDIT.md)). |
| *Overnight/rollover counterexamples* | **ĐẠT (PASS)** | Phân tích toán học YX 3624 trễ 877 phút, chứng minh sai số 24h của phép trừ timestamp ([`T004_OVERNIGHT_COUNTEREXAMPLES.md`](T004_OVERNIGHT_COUNTEREXAMPLES.md)). |
| *Safe fields decision* | **ĐẠT (PASS)** | Ban hành ma trận 4 cấp độ bao phủ toàn bộ 34 cột dữ liệu ([`T004_SAFE_FIELDS_DECISION.md`](T004_SAFE_FIELDS_DECISION.md)). |
| *TS-010 specs* | **ĐẠT (PASS)** | Đặc tả chi tiết 9 fixtures `TF-01` đến `TF-09` kèm các oracle số học bất biến ([`T004_TEST_FIXTURE_SPEC.md`](T004_TEST_FIXTURE_SPEC.md)). |

---

## 3. Cập nhật Danh mục 8 Rủi ro Mở Dự án (Open Risks Progression)

| Mã Rủi ro | Tóm tắt Rủi ro | Trạng thái trước T-004 | Trạng thái sau T-004 | Hướng xử lý tiếp theo |
|:---:|---|:---:|:---:|---|
| **OR-01** | Cột `FLIGHTS` bằng 1.0 trên toàn bộ 54.67M dòng. | Đã khóa thiết kế | Đã khóa thiết kế | Chuyển G4 kiểm thử Spark |
| **OR-02** | Nguy cơ mất trễ cực đoan nếu deduplicate tùy tiện (ca YX 3624). | Đã lập fixture bảo vệ | Đã chứng minh bản chất vật lý YX 3624 trễ 877m | Chuyển G4 (`TS-020`, `TS-021`) |
| **OR-03** | Đơn vị 7 trường độ trễ/thời lượng giữ nhãn `PROVISIONAL`. | Bảo lưu rủi ro | Bảo lưu rủi ro | Chờ đối chiếu BTS tại G5 |
| **OR-04** | Thiếu cột `CANCELLED` và `DIVERTED` trong 34 cột raw CSV. | Đã đóng phạm vi | Đã đóng phạm vi | Khóa ngoài 8 CORE KPIs |
| **OR-05** | **Tính liên tục 366 ngày của năm nhuận 2024 (vắng mặt Tháng 3/2024).** | `UNKNOWN / PENDING` | **XÁC LẬP KHIẾM KHUYẾT THỰC CHỨNG:** $335/366$ ngày phân biệt, vắng mặt 31 ngày Tháng 3/2024 (`DATA_ABSENT_IN_CURRENT_CSV`). | **OPEN_QUALITY_DEFECT** (Chưa đóng; giữ tham chiếu lịch 366 ngày cho `TS-004`; 3 phương án xử lý tại G3/G4) |
| **OR-06** | **Rollover mốc giờ thực tế (`ARR_TIME`, `DEP_TIME`) và bản chất YX 3624.** | Chuyển giao T-004 | **ĐÃ GIẢI TỎA BẰNG TOÁN HỌC & CHÍNH SÁCH:** Ban hành ma trận trường an toàn, cấm trừ timestamp, cấm cộng 24h, bảo vệ 7 trường số phút. | **ĐÃ ĐÓNG RỦI RO** (Đặc tả `TS-010`) |
| **OR-07** | Dữ liệu thời tiết thiếu trạm đo, mốc thời gian và đơn vị đo. | `CONDITIONAL_PENDING` | `CONDITIONAL_PENDING` | **Chuyển giao cho Task T-005** |
| **OR-08** | Chưa có SHA-256 tham chiếu từ cổng phát hành gốc. | `METADATA_MATCH_ONLY` | `METADATA_MATCH_ONLY` | Chuyển giao T-007 (G4) |

---

## 4. Trạng thái Gate G2 & Kế hoạch Tiếp theo

1. **Trạng thái Gate G2:**
   - **Gate G2 VẪN TIẾP TỤC Ở TRẠNG THÁI `IN_PROGRESS / NOT_PASSED`**.
   - Mặc dù T-001, T-002, T-003, và T-004 đã hoàn tất, Gate G2 **KHÔNG ĐƯỢC PHÉP THÔNG QUA** nếu chưa hoàn thành **Task T-005 (Weather Usability Audit)**.
2. **Kế hoạch Tiếp theo:**
   - Trình Reviewer phê duyệt hồ sơ nghiệm thu **T-004**.
   - Chuyển giao sang **Task T-005**: Kiểm toán khả năng sử dụng của dữ liệu thời tiết (đưa ra quyết định dứt khoát `CONDITIONAL_GO` hoặc `CONDITIONAL_NO_GO` cho nhánh thời tiết tùy chọn mà không làm tắc nghẽn 8 CORE KPIs).
3. **Cam kết Dừng lại Tuyệt đối:**
   - **TÔI ĐÃ DỪNG LẠI SAU T-004**, tuyệt đối không tự ý khởi động Task T-005 hoặc Gate G3 khi chưa có lệnh từ người phụ trách.
   - Không can thiệp sửa đổi các tệp CSV thô, không chạy Spark production.
