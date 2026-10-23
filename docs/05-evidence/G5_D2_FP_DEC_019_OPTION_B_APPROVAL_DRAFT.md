# G5_D2_FP_DEC_019_OPTION_B_APPROVAL_DRAFT.md
# Quyết Định Phê Duyệt Chính Sách FP-DEC-019 / Phương Án B (Quyết Định D2 — Approved Record)

**Dự án:** US Flight Performance Analysis 2016–2024  
**Hạng mục quản trị:** Quyết định độc lập D2 — FP-DEC-019 Option B Approval  
**Cổng quản lý:** Gate G5 — IN_PROGRESS  
**Trạng thái hiện tại:** **APPROVED_WITH_CONDITIONS**  
**Nguồn ủy quyền:** `APPROVED_BY_PROJECT_LEAD_INSTRUCTION` (Chỉ thị tường minh ngày 2026-10-21: *"tôi hoàn toàn đồng ý với ý kiến của bạn"*)  
**Tác giả ghi nhận:** Project Governance Officer & Principal Big Data Engineer  
**Thời điểm phê duyệt:** 2026-10-21  

---

## 1. BỐI CẢNH VÀ CƠ SỞ KỸ THUẬT

1. Theo quy định tại `DATA_CONTRACT.md` và `TEST_PLAN.md` (TS-018), dự án yêu cầu kiểm chứng đối soát tính trung thực của dữ liệu bay so với nguồn công bố chính thức của BTS TranStats.
2. Tại Gate G5, chỉ có dữ liệu năm 2016 được chạy thử nghiệm và đóng gói Parquet theo giới hạn của Task T-010. Dữ liệu năm 2019 chưa được chuyển đổi sang Parquet Staging nhằm tuân thủ tuyệt đối quy tắc phân kỳ của dự án (T-012 thuộc Gate G6 mới xử lý toàn bộ 2016–2024).
3. Do đó, đề xuất chính sách **FP-DEC-019 / Phương án B (Option B)** được khởi tạo:
   - Sử dụng phép so sánh trực tiếp giữa tệp dữ liệu thô **`data/raw/tabular/2019/flight_with_weather_2019.csv`** (tháng 1/2019) và tệp dữ liệu chính thống **`BTS TranStats T_ONTIME_REPORTING.csv`** (tháng 1/2019) làm bằng chứng đơn vị kỹ thuật (unit verification) cho nhiệm vụ TS-018.
   - Giới hạn phép kiểm tra trong phạm vi chính xác **7 trường số đo hiệu suất CORE**: `ARR_DELAY`, `DEP_DELAY`, `TAXI_OUT`, `TAXI_IN`, `AIR_TIME`, `ACTUAL_ELAPSED_TIME`, `CRS_ELAPSED_TIME`.

---

## 2. ĐẶC TÍNH MẪU VÀ KẾT QUẢ KIỂM CHỨNG THỰC NGHIỆM

> [!NOTE]
> **Đặc tính lấy mẫu:** Tập mẫu witness gồm 1.500 chuyến bay được thiết lập theo phương thức **lấy mẫu phân tầng theo hạn ngạch có kiểm soát (controlled quota-stratified sampling)** trên 17 hãng hàng không của tháng 1/2019 theo seed xác định `ts018_bts_jan2019_seed_42`. Đây là mẫu kiểm toán đơn vị có kiểm soát (controlled audit sample), **tuyệt đối không gán tính đại diện ngẫu nhiên độc lập phân phối đồng nhất (i.i.d.)** chưa được chứng minh toán học cho toàn bộ 583.985 chuyến bay của tháng hay toàn bộ 9 năm.

Quá trình kiểm chứng hai nguồn vật lý độc lập trên mẫu phân tầng ngẫu nhiên 1.500 chuyến bay đã đạt kết quả:

| Chỉ số kiểm tra | Kết quả thực tế | Tiêu chuẩn nghiệm thu | Đánh giá |
| :--- | :---: | :---: | :---: |
| **Số khóa chuyến bay phân tầng hạn ngạch** | `1,500` khóa | 1.500 khóa | `PASS` |
| **Khóa trùng lặp trong tệp mẫu witness** | `0` | 0 | `PASS` |
| **Khóa trùng lặp trong nguồn RAW CSV 2019** | `0` | 0 | `PASS` |
| **Khóa trùng lặp trong nguồn BTS CSV 2019** | `0` | 0 | `PASS` |
| **Tổng số giá trị trường số đối soát** | `10,500` ($1,500 \times 7$) | 10.500 | `PASS` |
| **Trùng khớp số học tuyệt đối (Bitwise Exact IEEE-754)** | `10,500 / 10,500` | $100\%$ | `PASS` |
| **Trường hợp chênh lệch trong dung sai (Tolerance-only)** | `0` | 0 | `PASS` |
| **Trường hợp sai lệch giá trị (Mismatches)** | `0` | 0 | `PASS` |
| **Kiểm thử tiêu cực phát hiện sai lệch (Negative tests)** | `14 / 14` PASS fail-closed | 100% fail-closed | `PASS` |

---

## 3. CÁC ĐIỀU KIỆN RÀNG BUỘC VÀ RANH GIỚI BẢO LƯU

Quyết định này chỉ có giá trị pháp lý trong phạm vi được định nghĩa nghiêm ngặt sau:

1. **Ranh giới `PARQUET_PARITY_NOT_TESTED`:**
   - Phép kiểm chứng này chỉ chứng minh độ trung thực của tệp CSV thô 2019 so với BTS.
   - Phép kiểm chứng **chưa và không kiểm tra** tính chẵn lẻ của tệp Parquet 2019 (vì Parquet 2019 chưa được sinh ra tại G5).
2. **Không suy rộng ra toàn bộ giai đoạn 2016–2024:**
   - Sự trùng khớp tuyệt đối của tháng 1/2019 là bằng chứng thực nghiệm mạnh mẽ cho tháng 1/2019, nhưng **không cấu thành chứng nhận toàn bộ 9 năm trên Kaggle đều có chuỗi bàn giao chính thức từ BTS** (Rủi ro `OR-08` tiếp tục được bảo lưu).
3. **Giới hạn 7 trường CORE:**
   - Không chứng nhận các trường dữ liệu thời tiết (Weather tiếp tục duy trì trạng thái `CONDITIONAL_NO_GO` theo FP-DEC-017).

---

## 4. QUYẾT ĐỊNH CỦA PROJECT LEAD (ĐÃ GHI NHẬN CHÍNH THỨC)

> [!NOTE]
> Hành động phê duyệt được ghi nhận chính thức theo cơ chế ủy quyền chỉ thị tường minh (`APPROVED_BY_PROJECT_LEAD_INSTRUCTION`) trong phiên làm việc ngày 2026-10-21. Không tạo lập chữ ký số hay chữ ký tay nhân tạo.

Project Lead dự án US Flight Performance Analysis 2016–2024:
1. **CHÍNH THỨC CHẤP THUẬN** chính sách **FP-DEC-019 / Phương Án B (Option B)** với các điều kiện và ranh giới bảo lưu đã nêu tại Mục 3.
2. Cho phép sử dụng kết quả đối soát RAW CSV 2019 $\leftrightarrow$ BTS January 2019 làm căn cứ kỹ thuật đầy đủ để xem xét nghiệm thu nhiệm vụ TS-018.

- **Hình thức phê chuẩn:** `APPROVED_BY_PROJECT_LEAD_INSTRUCTION`
- **Nội dung chỉ thị:** *"tôi hoàn toàn đồng ý với ý kiến của bạn"*
- **Ngày phê duyệt:** 2026-10-21
- **Trạng thái quyết định D2:** **`APPROVED_WITH_CONDITIONS`** (Đăng ký chính thức `FP-DEC-019` tại `DECISIONS.md`)
