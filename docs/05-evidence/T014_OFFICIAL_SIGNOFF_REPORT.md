# BÁO CÁO NGHIỆM THU CHÍNH THỨC CÓ KIỂM SOÁT NHIỆM VỤ T-014 (OFFICIAL CONTROLLED SIGNOFF REPORT)

**Dự án:** Phân tích hiệu suất khai thác chuyến bay nội địa Hoa Kỳ 2016–2024 (US Flight Performance Analysis)  
**Nhiệm vụ:** T-014 — Quy trình Phân tích Mô tả, Trực quan hóa & Tổng hợp Khoa học 9 Năm (Descriptive Analytical Workflows, Visualization & Scientific Synthesis)  
**Cổng kiểm soát:** Cổng G6 (Trạng thái hiện tại: `IN_PROGRESS — READY_FOR_FINAL_HUMAN_REVIEW`)  
**Thẩm quyền phê duyệt:** Project Lead (Chỉ thị phê duyệt trực tiếp `OFFICIAL PROJECT LEAD SIGNOFF — T014 CONTROLLED ACCEPTANCE & FINAL EVIDENCE ERRATUM`)  
**Vai trò thực hiện:** Project Governance Officer, Scientific Evidence Maintainer & Release Documentation Reviewer  
**Thời điểm lập:** 2026-10-22  
**Quyết định chính thức:** **`T-014 = PASS / COMPLETED (CONTROLLED)`**  

---

## 1. CĂN CỨ VÀ QUYẾT ĐỊNH PHÊ DUYỆT CỦA PROJECT LEAD (HUMAN AUTHORIZATION)

Căn cứ chỉ thị phê duyệt chính thức được Project Lead gửi trực tiếp:
> *"By personally submitting this instruction, I, the Project Lead, authorize controlled acceptance of Task T-014, conditional on correcting the identified non-production documentation inconsistencies and confirming no unresolved material analytical blocker. Target official status: `T-014 = PASS / COMPLETED (CONTROLLED)`. This approval applies only to T-014. Gate G6 must remain IN_PROGRESS until its own final acceptance requirements and Project Lead authorization are satisfied."*

Project Governance Officer chính thức ghi nhận quyết định phê duyệt có kiểm soát đối với Nhiệm vụ T-014 với trạng thái pháp lý dự án:
$$\mathbf{T\text{-}014 = PASS\ /\ COMPLETED\ (CONTROLLED)}$$

**Điều kiện bắt buộc đi kèm:** Phê duyệt này gắn liền với bản đính chính bổ sung bất biến [`T014_FINAL_EVIDENCE_ERRATUM.md`](T014_FINAL_EVIDENCE_ERRATUM.md) và xác nhận không còn bất kỳ điểm nghẽn phân tích trọng yếu nào tồn đọng. Phê duyệt này chỉ áp dụng riêng cho Nhiệm vụ T-014; Cổng G6 tiếp tục duy trì trạng thái `IN_PROGRESS` chờ văn bản nghiệm thu cổng riêng biệt.

---

## 2. NGUYÊN TẮC BẢO TOÀN DỮ LIỆU SẢN XUẤT VÀ CHÂN LÝ CƠ SỞ (RELEASE BASELINE)

Toàn bộ các thực thể sản xuất và bản phát hành đã được niêm phong kỹ thuật được bảo toàn tuyệt đối, không tính toán lại, không chỉnh sửa:

1. **Bản chụp KPI đầu vào thượng nguồn:**
   - Mã định danh: [`kpi_run_2016_2024_v1`](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/data/kpi/runs/kpi_run_2016_2024_v1)
   - Quy mô: **54,674,003** bản ghi chuyến bay hợp lệ chấp nhận qua kiểm toán chất lượng G5/T-012.
   - Bản ghi KPI: **684,180** hàng KPI chuẩn tắc qua 6 chiều tổng hợp (9 tệp Parquet, 11,879,782 bytes).
   - Cohorts phân tích: **57,015** cohorts.
   - Chỉ số: Đủ **8 chỉ số CORE KPIs** chuẩn tắc (`KPI-01..08`).
2. **Bản chạy phân tích sản xuất chính thức:**
   - Mã định danh: [`t014_analysis_2016_2024_v4`](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/data/analytics/runs/t014_analysis_2016_2024_v4)
   - Bảng phân tích: Đúng **12 bảng Parquet + 12 bảng CSV** đối ứng giải quyết 5 câu hỏi nghiên cứu RQ-01 đến RQ-05.
   - Đồ thị trực quan: Đúng **16 đồ thị khoa học (32 tệp gồm 16 PNG 300 DPI + 16 SVG vector)**.
   - Sổ đăng ký kết quả: Đúng **20 mục kết quả khoa học** (`RES-001` đến `RES-020`) với mẫu số phân tích cụ thể từng cohort.
   - Báo cáo khoa học: [`T014_ANALYTICAL_FINDINGS_REPORT.md`](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/data/analytics/runs/t014_analysis_2016_2024_v4/T014_ANALYTICAL_FINDINGS_REPORT.md) gồm 10 phần chi tiết bằng tiếng Việt.
   - Con trỏ điều hướng: [`data/analytics/latest_run_id.txt`](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/data/analytics/latest_run_id.txt) trỏ chính xác `t014_analysis_2016_2024_v4`.
3. **Các gói lưu trữ đã niêm phong và được kiểm chứng độc lập:**
   - **Gói kiểm toán V4:** `T014_FINAL_REVIEW.zip` (Kích thước: **4,182,327 bytes**; SHA-256: `8dbdbb23e42c35b5e04e5c836634d6cb0e374da7d22f9708f8a12237ea1ffce4`; CRC-32: `1f4055f9`; 70/70 thành phần kiểm toán khớp 100% manifest).
   - **Gói phụ lục nghiệm thu:** `T014_V4_SIGNOFF_ADDENDUM.zip` (Kích thước: **36,085 bytes**; SHA-256: `6a2415b28425796e8548bd7c6accdf466b4fa70ca5bb8bc199f746a573c58818`; CRC-32: `f68efbc2`; 5/5 thành phần kiểm toán khớp 100% manifest).
   - Các bản chạy phân tích lịch sử v1, v2, v3 duy trì chỉ đọc bất biến.

---

## 3. KIỂM CHỨNG CÁC ĐIỀU KIỆN NGHIỆM THU CÓ KIỂM SOÁT (ACCEPTANCE VERIFICATION)

Trước khi xác lập quyết định nghiệm thu, 8 điều kiện tiên quyết đã được kiểm tra độc lập và thỏa mãn toàn bộ:

| STT | Điều kiện kiểm tra có kiểm soát | Kết quả kiểm chứng thực tế | Đánh giá |
|:---:|:---|:---|:---:|
| 1 | Bản chạy vật lý v4 tồn tại nguyên vẹn | Thư mục `data/analytics/runs/t014_analysis_2016_2024_v4/` hiện hữu, đầy đủ 12 bảng, 16 biểu đồ, manifest và báo cáo | **PASS** |
| 2 | Con trỏ công bố chọn chính xác v4 | Tệp `data/analytics/latest_run_id.txt` chứa chuỗi `t014_analysis_2016_2024_v4` | **PASS** |
| 3 | Xác thực mã băm mật mã học hai gói ZIP | Cả 2 gói ZIP (`T014_FINAL_REVIEW.zip` và `T014_V4_SIGNOFF_ADDENDUM.zip`) trùng khớp 100% SHA-256 và CRC-32 | **PASS** |
| 4 | Bảng phân tích v4 không bị sửa đổi | 12 bảng Parquet và CSV trong v4 giữ nguyên mã băm xác thực, không bị ghi đè | **PASS** |
| 5 | Bản đính chính chỉ tác động văn bản/mô tả | Toàn bộ 7 nội dung hiệu chỉnh A..G chỉ đính chính mô tả, phân loại và trích dẫn, 0 thay đổi toán học | **PASS** |
| 6 | Tài liệu kiểm thử và an toàn phát hành đầy đủ | Ghi nhận đầy đủ 33/33 unit tests PASS (gồm 4 tests an toàn phát hành) và 91/91 QA audit checks PASS | **PASS** |
| 7 | Ghi nhận đầy đủ các giới hạn nghiên cứu | Bảo lưu OR-05, OR-08, FP-DEC-017, TS-018 Option B và nguyên tắc phi nhân quả | **PASS** |
| 8 | Chỉ thị phê duyệt của Project Lead xác thực | Project Lead đã trực tiếp gửi chỉ thị phê duyệt tường minh trong phiên làm việc | **PASS** |

---

## 4. TỔNG HỢP NỘI DUNG ĐÍNH CHÍNH BẰNG CHỨNG (ERRATUM SUMMARY: CORRECTIONS A — G)

Chi tiết đầy đủ được ban hành tại [`T014_FINAL_EVIDENCE_ERRATUM.md`](T014_FINAL_EVIDENCE_ERRATUM.md):

1. **Hiệu chỉnh A (Số lượng liên kết bằng chứng):** Xác lập con số vật lý chuẩn xác từ tệp JSON có thẩm quyền: **24 EXACT_EVIDENCE + 3 THEMATIC_CONTEXTUAL = 27 mối liên kết RES** trên 16 biểu đồ (sửa lại con số 22+3=25 trong văn bản thuyết minh trước).
2. **Hiệu chỉnh B (Đáy sản lượng tháng 2020):** Khẳng định đáy sản lượng thấp nhất tuyệt đối trong chuỗi 107 tháng là **Tháng 05/2020 (163,767 chuyến bay)**, không phải Tháng 04/2020 (179,835 chuyến bay). Mục RES-003 bảo lưu tính chính xác như quan sát về cú sốc giảm đột ngột ban đầu của đại dịch.
3. **Hiệu chỉnh C (Tỷ lệ trễ đến 2020):** Khẳng định tỷ lệ trễ đến toàn quốc năm 2020 trong bảng sản xuất là **`9.73%` (`9.726812%`)**, sửa chữa các viện dẫn nhầm thành 11.75%.
4. **Hiệu chỉnh D (Sản lượng chuyến bay 2019):** Khẳng định sản lượng chuyến bay được chấp nhận năm 2019 là **`7,161,827`** chuyến bay, loại bỏ con số viện dẫn nhầm 7,162,267.
5. **Hiệu chỉnh E (Trung bình thời gian hành trình 2020):** Khẳng định thời gian dự kiến trung bình là `138.47 phút`, thời gian thực tế trung bình là `131.39 phút`, chênh lệch trung bình biên là `+7.08 phút`. Nghiêm cấm suy diễn hiệu số này thành chiến lược đệm lịch trình có chủ đích ở cấp độ từng chuyến bay.
6. **Hiệu chỉnh F (Ngữ nghĩa toán học KPI-03 & KPI-05):** Khẳng định KPI-03 và KPI-05 là trung bình có dấu (signed means) trên toàn bộ chuyến bay hợp lệ (bao gồm cả giá trị âm khi bay sớm), không bị giới hạn riêng cho các chuyến bay trễ dương hay trễ >=15 phút.
7. **Hiệu chỉnh G (Chuẩn mực phân loại bằng chứng):** Bảo lưu 3 liên kết ngữ cảnh chủ đề (`THEMATIC_CONTEXTUAL`) phản ánh trung thực nguồn dữ liệu bảng phân tích (`rq02_monthly_delays.parquet` và `rq03_top_carriers.parquet`), không gán nhãn lại thành chính xác chỉ để làm đẹp số liệu.

---

## 5. MA TRẬN TRẠNG THÁI QUẢN TRỊ DỰ ÁN CHÍNH THỨC (GOVERNANCE STATE MATRIX)

Sau khi hoàn tất thủ tục phê duyệt có kiểm soát, trạng thái quản trị toàn dự án được xác lập:

| Thành phần Quản trị | Trạng thái Chính thức | Căn cứ Pháp lý & Ghi chú |
|:---|:---:|:---|
| **Nhiệm vụ T-012** | **`PASS / COMPLETED (CONTROLLED)`** | Quyết định phê duyệt của Project Lead ngày 2026-10-21 (54,674,003 bản ghi, 117 Parquet). |
| **Nhiệm vụ T-013** | **`PASS / COMPLETED (CONTROLLED)`** | Quyết định phê duyệt của Project Lead ngày 2026-10-22 (684,180 hàng KPI, 84 luồng math PASS). |
| **Nhiệm vụ T-014** | **`PASS / COMPLETED (CONTROLLED)`** | **Quyết định phê duyệt có kiểm soát của Project Lead ngày 2026-10-22 kèm bản đính chính bằng chứng.** |
| **Quyết định D5** | **`NOT_AUTHORIZED / FAIL-CLOSED`** | **Duy trì đóng chặt fail-closed; không cấp phép mở rộng phân tích.** |
| **Nhiệm vụ T-015 (Weather)** | **`CONDITIONAL_NO_GO`** | Tuân thủ chính sách FP-DEC-017; không cản trở đóng Cổng G6. |
| **Cổng Gate G6** | **`IN_PROGRESS — READY_FOR_FINAL_HUMAN_REVIEW`** | **Duy trì `IN_PROGRESS`; sẵn sàng cho Project Lead thẩm tra và ký duyệt đóng cổng.** |
| **Cổng Gate G7** | **`NOT_STARTED`** | Chưa kích hoạt; chỉ mở sau khi Cổng G6 đóng thành công. |

---

## 6. CÁC GIỚI HẠN DỮ LIỆU VÀ CẢNH BÁO BẮT BUỘC (RESIDUAL LIMITATIONS & DISCLAIMERS)

Toàn bộ các tài liệu công bố và tổng kết tiếp tục bảo lưu nghiêm ngặt các giới hạn:
1. **Giới hạn OR-05 (Tháng 03/2024 khuyết thiếu):** Toàn bộ Tháng 03/2024 không có dữ liệu nguồn gốc từ upstream; năm 2024 chỉ có 335/366 ngày quan sát và được đánh nhãn bắt buộc `source_coverage_status = PARTIAL`.
2. **Giới hạn OR-08 (Nguồn gốc Kaggle):** Nguồn gốc tải lên ban đầu từ Kaggle không thể xác minh danh tính điện tử; chấp nhận có kiểm soát trên cơ sở đối soát bitwise TS-018 Option B đối với 10,500 điểm dữ liệu đối chiếu BTS.
3. **Chính sách FP-DEC-017 (Loại trừ Thời tiết):** Dữ liệu thời tiết không thuộc phạm vi CORE; không phát hành chỉ số tương quan thời tiết trong gói sản phẩm chính.
4. **Phạm vi TS-018 Option B:** Đối chiếu số học nghiêm ngặt được thực hiện có giới hạn trên tháng 01/2019.
5. **Cảnh báo phi nhân quả (Non-causality Disclaimer):** Đây thuần túy là đề tài phân tích dữ liệu lớn mô tả hồi cứu (Observational / Descriptive Big Data Study). Các xu hướng sụt giảm năm 2020, giãn nở hành trình hay chênh lệch tuyến bay phản ánh sự biến thiên thống kê quan sát được, không khẳng định mối quan hệ nhân quả. Sự chênh lệch giữa các trung bình biên không đồng nhất với ước lượng cặp trên từng chuyến bay đơn lẻ.

---

## 7. DANH MỤC THÀNH PHẦN HỒ SƠ NGHIỆM THU NIÊM PHONG (DELIVERABLES INVENTORY)

Hồ sơ nghiệm thu chính thức được niêm phong tại thư mục:  
[`D:\Flight_Audit_Exports\T014_FULL_ANALYTICS\official_signoff\`](file:///D:/Flight_Audit_Exports/T014_FULL_ANALYTICS/official_signoff/)

1. [`T014_OFFICIAL_SIGNOFF_REPORT.md`](T014_OFFICIAL_SIGNOFF_REPORT.md) (Báo cáo nghiệm thu có kiểm soát chính thức — văn bản này).
2. [`T014_OFFICIAL_SIGNOFF_SUMMARY.json`](T014_OFFICIAL_SIGNOFF_SUMMARY.json) (Bản tổng hợp dữ liệu máy đọc được về phê duyệt nghiệm thu).
3. [`T014_FINAL_EVIDENCE_ERRATUM.md`](T014_FINAL_EVIDENCE_ERRATUM.md) (Bản đính chính bằng chứng phân tích và phân loại ngữ nghĩa cuối cùng).
4. [`T014_OFFICIAL_SIGNOFF_REVIEW.zip`](T014_OFFICIAL_SIGNOFF_REVIEW.zip) (Gói nén niêm phong toàn bộ 3 tài liệu nghiệm thu nêu trên).
5. [`T014_OFFICIAL_SIGNOFF_REVIEW_MANIFEST.json`](T014_OFFICIAL_SIGNOFF_REVIEW_MANIFEST.json) (Bản kê băm mật mã học SHA-256 và CRC-32 của gói niêm phong).

---

## 8. KẾT LUẬN & BÀN GIAO (FINAL VERDICT)

Toàn bộ các yêu cầu nghiệm thu có kiểm soát của Project Lead đối với Nhiệm vụ T-014 đã hoàn tất đầy đủ, chính xác và minh bạch 100%.

**KẾT LUẬN CHÍNH THỨC:**  
$$\mathbf{T014\_OFFICIAL\_SIGNOFF\_COMPLETED\_CONTROLLED}$$

- Nhiệm vụ T-014 chính thức chuyển sang: **`PASS / COMPLETED (CONTROLLED)`**.
- Cổng Gate G6 chuyển sang: **`IN_PROGRESS — READY_FOR_FINAL_HUMAN_REVIEW`**.
- Dừng mọi hoạt động thực thi kỹ thuật. Chờ quyết định nghiệm thu Cổng G6 tiếp theo từ Project Lead.
