# T-005 R2: ĐẶC TẢ KIỂM CHUẨN KỸ THUẬT VÀ KHẾ ƯỚC DỮ LIỆU TS-011
## (T-005 R2 TS-011 TEST SPECIFICATION: WEATHER DATA GUARDS & ISOLATION CONTRACT)

- **Mã kiểm thử:** `TS-011` (Weather Units, Join, Missing, Stratification & CORE Isolation)
- **Gate kiểm soát:** `Gate G2` (Thiết kế & Khế ước) $\to$ Thực thi tại `Gate G4 / G5 / G6`
- **Nhiệm vụ liên quan:** [`T-005`](../01-planning/BACKLOG.md), T-015
- **Yêu cầu kỹ thuật:** `REQ-06` (Weather Stratified Analysis), `REQ-04` (Core Metric Integrity)
- **Văn bản tuân thủ:** [`docs/02-design/DATA_CONTRACT.md`](../02-design/DATA_CONTRACT.md) ([`DC-07`](../02-design/DATA_CONTRACT.md#L21), [`DC-11`](../02-design/DATA_CONTRACT.md#L26-L34), [`DC-12`](../02-design/DATA_CONTRACT.md#L35-L45)), [`docs/02-design/KPI_SPEC.md`](../02-design/KPI_SPEC.md) (KPI-10), [`docs/03-quality/TEST_PLAN.md`](../03-quality/TEST_PLAN.md) (`TS-011`), [`docs/02-design/DECISIONS.md`](../02-design/DECISIONS.md) ([`FP-DEC-009`](../02-design/DECISIONS.md#L15), [`FP-DEC-013`](../02-design/DECISIONS.md#L19)).
- **Trạng thái thực thi hiện thời:** **`SPECIFIED / NOT_RUN`** (Đặc tả thiết kế kiểm chuẩn; chưa thực thi trên Spark production).

---

## 1. NGUYÊN TẮC CỐT LÕI VỀ CÁCH LY KHẾ ƯỚC DÒNG (DC-11 / DC-12 ISOLATION PRINCIPLE)

Mọi kịch bản kiểm thử trong đặc tả `TS-011` phải tuân thủ nghiêm ngặt **Quy tắc Bất biến về Kế toán Hàng**:
1. **Bảo vệ Tuyệt đối Quần thể Chuyến bay Cốt lõi (CORE Record Protection):**
   Một bản ghi dữ liệu có các trường vận hành chuyến bay hợp lệ (`FL_DATE`, `ORIGIN`, `DEST`, `DEP_DELAY`, `ARR_DELAY`) **bắt buộc phải được phân loại là `accepted_row_count`** ở tầng nạp dữ liệu cấp năm.
2. **Không Quarantine Lây nhiễm (No Contagious Quarantine):**
   Bất kỳ lỗi, dị thường, khuyết thiếu, hoặc nghi ngờ rò rỉ nào xuất phát từ 6 trường thời tiết (`O_TEMP`, `O_PRCP`, `O_WSPD`, `D_TEMP`, `D_PRCP`, `D_WSPD`) **CHỈ ĐƯỢC PHÉP tác động tới mẫu số của chỉ số thời tiết KPI-10** (`excluded_count += 1`, `metric_valid_rate` giảm). Tuyệt đối **KHÔNG ĐƯỢC** chuyển bản ghi chuyến bay sang `quarantined_row_count` hoặc `rejected_row_count`.
3. **Phân biệt Quan sát Hồi cứu vs Rò rỉ Dự báo:**
   Đối với bài toán phân tích mô tả hồi cứu (retrospective descriptive study), việc dữ liệu thời tiết ghi nhận tại thời điểm sau giờ khởi hành không tự động cấu thành lỗi rò rỉ thông tin (*prediction leakage*); tuy nhiên, nếu không chứng minh được mốc giờ quan trắc tương ứng với thời gian chuyến bay diễn ra, dữ liệu đó bị loại khỏi phân tích tương quan thời gian.

---

## 2. CHI TIẾT MƯỜI HAI KỊCH BẢN KIỂM CHUẨN GIẢ LẬP (SC-01 ĐẾN SC-12)

### Kịch bản SC-01: Unknown Units Guard (Rào chắn Đơn vị Chưa được Chứng thực)
*   **Mục đích & Rủi ro Kiểm tra:** Ngăn chặn việc xuất bản biểu đồ hoặc bảng thống kê có gắn nhãn đơn vị ($^\circ\text{C}$, $\text{mm}$, $\text{km/h}$) khi chưa có datasheet thẩm quyền (`R-15`).
*   **Dữ liệu Giả lập Đầu vào (Synthetic Input):** Bản ghi chuyến bay hợp lệ kèm `O_TEMP = 25.0`, metadata cột mang cờ `unit_status = UNIT_EMPIRICALLY_PLAUSIBLE_PROVISIONAL`.
*   **Hành vi Xử lý Kỳ vọng:** Hệ thống hiển thị cờ cảnh báo `provisional`; trục biểu đồ không ghi đơn vị khẳng định; gán nhãn `UNIT_UNVERIFIED`.
*   **Tác động Kế toán Dòng CORE (DC-11):** Bản ghi là `accepted` ($100\%$).
*   **Tác động Chỉ số Thời tiết (DC-12):** `count_records += 1`, `count_metric_valid += 1` (nếu phân tích không phụ thuộc đơn vị tuyệt đối).
*   **Phân loại Thất bại Kỳ vọng:** `WARN_PROVISIONAL_UNIT`.
*   **Trạng thái Thực thi:** **`SPECIFIED / NOT_RUN`**.
*   **Điều kiện Đạt PASS Tương lai:** Báo cáo đầu ra không chứa đơn vị chưa chứng thực hoặc hiển thị đúng disclaimer.

---

### Kịch bản SC-02: Missing Provider Identity (Rào chắn Nguồn gốc Không xác định)
*   **Mục đích & Rủi ro Kiểm tra:** Ngăn chặn việc khẳng định dữ liệu đến từ một nhà cung cấp chính thức khi thiếu hợp đồng hoặc API key (`OR-07`).
*   **Dữ liệu Giả lập Đầu vào:** Schema cấu hình thiếu URL endpoint hoặc chữ ký mã nguồn từ Meteostat/NOAA.
*   **Hành vi Xử lý Kỳ vọng:** Hệ thống gắn nhãn xuất xứ `PROVENANCE_UNVERIFIED`; từ chối tạo báo cáo gán tên nhà cung cấp chính thức.
*   **Tác động Kế toán Dòng CORE (DC-11):** Không ảnh hưởng (`accepted_row_count` giữ nguyên).
*   **Tác động Chỉ số Thời tiết (DC-12):** Chặn xuất bản bảng tổng hợp cấp nhà cung cấp.
*   **Phân loại Thất bại Kỳ vọng:** `PROVENANCE_METADATA_ABSENT`.
*   **Trạng thái Thực thi:** **`SPECIFIED / NOT_RUN`**.
*   **Điều kiện Đạt PASS Tương lai:** Hệ thống phát hiện thiếu metadata nguồn và tự động áp dụng cờ bảo vệ.

---

### Kịch bản SC-03: Null vs Valid Zero Distinction (Phân định Số 0 Hợp lệ vs Mất Dữ liệu)
*   **Mục đích & Rủi ro Kiểm tra:** Ngăn chặn lỗi điền số 0 vào giá trị null (`DC-07`), phân biệt giữa trời không mưa (`PRCP = 0.0`) và trạm đo bị hỏng (`PRCP = null`).
*   **Dữ liệu Giả lập Đầu vào:** 
    - Bản ghi A: `O_PRCP = 0.0` (thực tế không mưa).
    - Bản ghi B: `O_PRCP = null` (trạm mất tín hiệu).
*   **Hành vi Xử lý Kỳ vọng:** Bản ghi A được tính vào mẫu số hợp lệ của lượng mưa; Bản ghi B giữ nguyên `null`, không được fill `0.0`.
*   **Tác động Kế toán Dòng CORE (DC-11):** Cả Bản ghi A và Bản ghi B đều là `accepted` trong quần thể bay.
*   **Tác động Chỉ số Thời tiết (DC-12):** 
    - Bản ghi A: `count_metric_valid += 1`.
    - Bản ghi B: `excluded_count += 1`, ghi nhận lý do `NULL_WEATHER_VALUE`.
*   **Phân loại Thất bại Kỳ vọng:** Fail nếu hệ thống tự động `fillna(0.0)`.
*   **Trạng thái Thực thi:** **`SPECIFIED / NOT_RUN`**.
*   **Điều kiện Đạt PASS Tương lai:** Tỷ lệ null trước và sau biến đổi giữ nguyên bất biến.

---

### Kịch bản SC-04: Future Observation Leakage Guard (Rào chắn Rò rỉ Thời gian Tương lai)
*   **Mục đích & Rủi ro Kiểm tra:** Ngăn chặn việc gán dữ liệu thời tiết quan trắc sau khi chuyến bay đã kết thúc vào phân tích điều kiện khởi hành.
*   **Dữ liệu Giả lập Đầu vào:** Bản ghi có `WHEELS_ON = 2018-06-21 14:00:00`, nhưng trường thời tiết mang mốc quan trắc `2018-06-21 18:00:00`.
*   **Hành vi Xử lý Kỳ vọng:** Hệ thống phát hiện mốc thời tiết lệch sau giờ bay; gắn cờ `TEMPORAL_LEAKAGE_DETECTED`.
*   **Tác động Kế toán Dòng CORE (DC-11):** **BẢN GHI VẪN LÀ ACCEPTED TRONG CORE**. Tuyệt đối không đưa vào quarantine dòng máy bay.
*   **Tác động Chỉ số Thời tiết (DC-12):** Loại bản ghi khỏi phân tích điều kiện thời tiết khởi hành (`excluded_count += 1`).
*   **Phân loại Thất bại Kỳ vọng:** `EXCLUDED_FROM_WEATHER_COHORT`.
*   **Trạng thái Thực thi:** **`SPECIFIED / NOT_RUN`**.
*   **Điều kiện Đạt PASS Tương lai:** Bản ghi vẫn có mặt trong KPI-01..08 nhưng bị loại khỏi KPI-10.

---

### Kịch bản SC-05: Missing Join Timestamp Guard (Rào chắn Thiếu Mốc giờ Quan trắc)
*   **Mục đích & Rủi ro Kiểm tra:** Ngăn chặn phân tích tương quan thời gian mịn khi dữ liệu thiếu hoàn toàn trường mốc giờ đo đạc thực tế (`OR-07`).
*   **Dữ liệu Giả lập Đầu vào:** Toàn bộ bảng dữ liệu không có trường `OBSERVATION_TIME`.
*   **Hành vi Xử lý Kỳ vọng:** Hệ thống chặn các truy vấn phân nhóm theo khoảng thời gian dưới 24 giờ (`hourly correlation blocked`).
*   **Tác động Kế toán Dòng CORE (DC-11):** Toàn bộ hàng bay accepted giữ nguyên.
*   **Tác động Chỉ số Thời tiết (DC-12):** Chỉ cho phép phân nhóm ở cấp độ ngày/tháng/mùa; chặn phân tích theo giờ khởi hành thực tế.
*   **Phân loại Thất bại Kỳ vọng:** `GRANULAR_TEMPORAL_JOIN_UNSUPPORTED`.
*   **Trạng thái Thực thi:** **`SPECIFIED / NOT_RUN`**.
*   **Điều kiện Đạt PASS Tương lai:** Hệ thống từ chối thực thi các phép tính tương quan giờ mịn.

---

### Kịch bản SC-06: Timezone & DST Ambiguity Guard (Rào chắn Bất đồng Múi giờ và Giờ Mùa hè)
*   **Mục đích & Rủi ro Kiểm tra:** Ngăn chặn việc so khớp ngây thơ giữa chuỗi giờ địa phương không có múi giờ và dữ liệu thời tiết lưu theo chuẩn UTC.
*   **Dữ liệu Giả lập Đầu vào:** Chuyến bay cất cánh tại ORD lúc `14:00 CDT` (UTC-5), đối chiếu với bản ghi khí tượng Meteostat lưu theo UTC.
*   **Hành vi Xử lý Kỳ vọng:** Nếu pipeline không có bảng ánh xạ IANA timezone để đổi `14:00 CDT` thành `19:00 UTC`, hệ thống phải dừng lệnh join.
*   **Tác động Kế toán Dòng CORE (DC-11):** Bản ghi bay accepted không bị ảnh hưởng.
*   **Tác động Chỉ số Thời tiết (DC-12):** Gắn nhãn `TIMEZONE_OFFSET_AMBIGUOUS`, chặn phân tích trễ theo giờ.
*   **Phân loại Thất bại Kỳ vọng:** `FAIL_CLOSED_ON_TIMEZONE_MISMATCH`.
*   **Trạng thái Thực thi:** **`SPECIFIED / NOT_RUN`**.
*   **Điều kiện Đạt PASS Tương lai:** Phát hiện lỗi trôi lệch múi giờ trong kiểm thử giả lập.

---

### Kịch bản SC-07: Station Distance Threshold Guard (Rào chắn Khoảng cách Trạm đo Sân bay)
*   **Mục đích & Rủi ro Kiểm tra:** Ngăn chặn việc gán thời tiết của một trạm cách xa tâm sân bay hàng trăm km cho chuyến bay tại sân bay địa phương.
*   **Dữ liệu Giả lập Đầu vào:** Chuyến bay tại sân bay nhỏ, trạm thời tiết gần nhất có khoảng cách tính theo đường trắc địa là $150\text{ km}$ (vượt ngưỡng giả định $100\text{ km}$).
*   **Hành vi Xử lý Kỳ vọng:** Hệ thống gắn cờ `SPATIAL_DISTANCE_EXCEEDED`; loại bỏ giá trị thời tiết của bản ghi này.
*   **Tác động Kế toán Dòng CORE (DC-11):** Bản ghi bay vẫn là `accepted`.
*   **Tác động Chỉ số Thời tiết (DC-12):** Trường thời tiết bị coi là không hợp lệ đối với sân bay đó (`excluded_count += 1`).
*   **Phân loại Thất bại Kỳ vọng:** `EXCLUDED_DUE_TO_SPATIAL_THRESHOLD`.
*   **Trạng thái Thực thi:** **`SPECIFIED / NOT_RUN`** *(Ngưỡng 100km là giả lập thiết kế, chưa phải ngưỡng sản xuất)*.
*   **Điều kiện Đạt PASS Tương lai:** Dữ liệu trạm quá xa bị loại bỏ thành công.

---

### Kịch bản SC-08: Row Multiplication on Join Guard (Rào chắn Nhân đôi Dòng do Join)
*   **Mục đích & Rủi ro Kiểm tra:** Ngăn chặn lỗi kỹ thuật trong câu lệnh join thời tiết làm phát sinh bản ghi trùng, làm sai lệch tổng số chuyến bay (`count_records`) của dự án.
*   **Dữ liệu Giả lập Đầu vào:** Một chuyến bay khớp với 2 bản ghi thời tiết quan trắc khác nhau trong cùng một khung giờ.
*   **Hành vi Xử lý Kỳ vọng:** Pipeline join phải sử dụng cơ chế gom nhóm hoặc lọc chính xác 1 bản ghi duy nhất; nếu phát hiện số dòng sau join $>$ số dòng trước join, **lệnh nạp thời tiết phải fail-closed ngay lập tức**.
*   **Tác động Kế toán Dòng CORE (DC-11):** **BẢO VỆ TUYỆT ĐỐI**: Không để lỗi join thời tiết làm tăng `raw_row_count` hay `accepted_row_count` của tập chuyến bay cốt lõi.
*   **Tác động Chỉ số Thời tiết (DC-12):** Dừng tiến trình nạp thời tiết; ghi log lỗi `ROW_MULTIPLICATION_DETECTED`.
*   **Phân loại Thất bại Kỳ vọng:** `FATAL_JOIN_CARDINALITY_ERROR`.
*   **Trạng thái Thực thi:** **`SPECIFIED / NOT_RUN`**.
*   **Điều kiện Đạt PASS Tương lai:** Số dòng trước và sau join thời tiết bảo toàn tuyệt đối bằng nhau.

---

### Kịch bản SC-09: Annual Unit & Distribution Inconsistency (Rào chắn Trôi dạt Phân bố Đa năm)
*   **Mục đích & Rủi ro Kiểm tra:** Ngăn chặn việc tổng hợp dữ liệu qua các năm nếu một năm bị thay đổi thang đo hoặc cách mã hóa.
*   **Dữ liệu Giả lập Đầu vào:** Năm 2016 lưu tốc độ gió theo km/h (phân bố trần 92.5), năm giả định 2025 lưu theo m/s (phân bố trần 25.0).
*   **Hành vi Xử lý Kỳ vọng:** Kiểm tra phân bố thống kê tự động phát hiện trôi dạt phân vị; cảnh báo `DISTRIBUTION_DRIFT`.
*   **Tác động Kế toán Dòng CORE (DC-11):** Luồng CORE không bị ảnh hưởng.
*   **Tác động Chỉ số Thời tiết (DC-12):** Chặn lệnh gộp đa năm của chỉ số thời tiết.
*   **Phân loại Thất bại Kỳ vọng:** `CROSS_YEAR_DISTRIBUTION_MISMATCH`.
*   **Trạng thái Thực thi:** **`SPECIFIED / NOT_RUN`**.
*   **Điều kiện Đạt PASS Tương lai:** Phát hiện sự thay đổi phân bố đơn vị trong kiểm chuẩn.

---

### Kịch bản SC-10: Missing March 2024 Impact Guard (Rào chắn Khiếm khuyết Mất Tháng 3/2024)
*   **Mục đích & Rủi ro Kiểm tra:** Đảm bảo hệ thống nhận diện đúng khiếm khuyết thiếu 31 ngày Tháng 3/2024 (`OR-05`), không nội suy thời tiết giả mạo cho các ngày vắng mặt.
*   **Dữ liệu Giả lập Đầu vào:** Truy vấn chuỗi thời gian thời tiết liên tục từ 01/01/2024 đến 31/12/2024.
*   **Hành vi Xử lý Kỳ vọng:** Hệ thống phát hiện Tháng 3 có 0 bản ghi; gắn nhãn `OR-05: OPEN_QUALITY_DEFECT`; từ chối tính tổng tích lũy thời tiết cả năm 2024 nếu không có chú thích cửa sổ tháng.
*   **Tác động Kế toán Dòng CORE (DC-11):** Giữ nguyên số dòng thực tế 2024 ($6,284,841$).
*   **Tác động Chỉ số Thời tiết (DC-12):** Gắn nhãn `PARTIAL_YEAR_WEATHER`.
*   **Phân loại Thất bại Kỳ vọng:** `INCOMPLETE_CALENDAR_COVERAGE_DETECTED`.
*   **Trạng thái Thực thi:** **`SPECIFIED / NOT_RUN`**.
*   **Điều kiện Đạt PASS Tương lai:** Hệ thống phát hiện chính xác lỗ hổng 31 ngày Tháng 3/2024.

---

### Kịch bản SC-11: Unverified License Governance Guard (Rào chắn Pháp lý Bản quyền)
*   **Mục đích & Rủi ro Kiểm tra:** Ngăn chặn việc xuất bản hoặc phân phối lại tập dữ liệu có chứa thông tin thời tiết khi chưa có văn bản cấp phép hợp lệ (`OR-07`).
*   **Dữ liệu Giả lập Đầu vào:** Lệnh xuất bản gói artifact ra môi trường công cộng.
*   **Hành vi Xử lý Kỳ vọng:** Hệ thống kiểm tra tệp `LICENSE` và trường bản quyền; chặn xuất bản nếu cờ bản quyền thời tiết mang nhãn `UNKNOWN`.
*   **Tác động Kế toán Dòng CORE (DC-11):** Báo cáo chuyến bay nội bộ không bị ảnh hưởng.
*   **Tác động Chỉ số Thời tiết (DC-12):** Tách riêng các trường thời tiết khỏi tệp phân phối công khai.
*   **Phân loại Thất bại Kỳ vọng:** `REDISTRIBUTION_LICENSE_UNVERIFIED`.
*   **Trạng thái Thực thi:** **`SPECIFIED / NOT_RUN`**.
*   **Điều kiện Đạt PASS Tương lai:** Cơ chế phân quyền ngăn chặn rò rỉ dữ liệu chưa rõ bản quyền.

---

### Kịch bản SC-12: CORE Analytics Complete Isolation (Rào chắn Cách ly Tuyệt đối Luồng CORE)
*   **Mục đích & Rủi ro Kiểm tra:** Chứng minh bất biến tối cao: Việc kích hoạt `CONDITIONAL_NO_GO` hoặc loại bỏ toàn bộ 6 cột thời tiết **không gây ra bất kỳ lỗi hoặc sai lệch nào cho 8 CORE KPIs** (`KPI-01..08`).
*   **Dữ liệu Giả lập Đầu vào:** Xóa bỏ hoàn toàn 6 cột `O_TEMP..D_WSPD` (drop columns) khỏi DataFrame đầu vào.
*   **Hành vi Xử lý Kỳ vọng:** Pipeline tính toán 8 CORE KPIs chạy thành công $100\%$, cho ra các giá trị tử số, mẫu số, tỷ lệ trễ, thời gian lăn bánh và thời gian bay chính xác tuyệt đối như khi có cột thời tiết.
*   **Tác động Kế toán Dòng CORE (DC-11):** `raw_row_count = accepted_row_count + quarantined_row_count + rejected_row_count` được bảo toàn nguyên vẹn $100\%$.
*   **Tác động Chỉ số Thời tiết (DC-12):** Chỉ số KPI-10 chuyển trạng thái `SHELVED / DESELECTED`.
*   **Phân loại Thất bại Kỳ vọng:** **HOÀN TOÀN KHÔNG CÓ LỖI (ZERO ERROR ON CORE)**.
*   **Trạng thái Thực thi:** **`SPECIFIED / NOT_RUN`**.
*   **Điều kiện Đạt PASS Tương lai:** Tính độc lập của luồng CORE được chứng minh trong kiểm thử tích hợp tại Gate G4/G5.

---

## 3. TỔNG HỢP MA TRẬN RANH GIỚI KIỂM THỬ TS-011

```mermaid
flowchart TD
    subgraph Raw_Input["Tập Dữ liệu Đầu vào (Raw CSV 34 Cột)"]
        Flight_Cols["28 Cột Vận hành Chuyến bay (Core)"]
        Weather_Cols["6 Cột Thời tiết (Optional)"]
    end
    subgraph Ingestion_Gate["Tầng Kiểm soát Nạp Dữ liệu (DC-11)"]
        Core_Check{"Dữ liệu Core Hợp lệ?"}
        Weather_Check{"Thời tiết Lỗi / Thiếu / Lệch?"}
    end
    subgraph Accounting["Hạch toán Kế toán Dòng"]
        Accepted["Accepted Rows (Quần thể Bay Cốt lõi)"]
        Quarantine["Quarantined Rows (Lỗi Core Nghiêm trọng)"]
    end
    subgraph Metric_Calc["Tính toán Chỉ số (DC-12)"]
        Core_KPIs["8 CORE KPIs (KPI-01..08): 100% HOẠT ĐỘNG"]
        Weather_KPI["KPI-10 (Thời tiết): EXCLUDED_COUNT += 1"]
    end

    Flight_Cols --> Core_Check
    Weather_Cols --> Weather_Check
    Core_Check -->|Hợp lệ| Accepted
    Core_Check -->|Lỗi Core| Quarantine
    Weather_Check -->|Lỗi Thời tiết (SC-01..SC-11)| Weather_KPI
    Accepted --> Core_KPIs
    Accepted --> Weather_KPI
```

*   **Tuyên bố Nghiêm ngặt:** Đặc tả này là thiết kế kiểm chuẩn bất biến cho Gate G4/G5. Không một lập trình viên hay agent nào được phép thay đổi quy tắc cách ly này để làm lây nhiễm lỗi thời tiết vào quần thể chuyến bay accepted của dự án.
