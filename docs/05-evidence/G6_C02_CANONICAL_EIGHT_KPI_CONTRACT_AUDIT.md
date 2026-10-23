# G6_C02_CANONICAL_EIGHT_KPI_CONTRACT_AUDIT.md
# Kiểm Toán Hợp Đồng 8 CORE KPI Chuẩn Hóa và Đính Chính Danh Mục Vận Hành G6

**Mã tài liệu:** `G6_C02_CANONICAL_EIGHT_KPI_CONTRACT_AUDIT`  
**Dự án:** US Flight Performance Analysis 2016–2024  
**Nhiệm vụ:** T-012 / T-013 — Nine-Year Pipeline Ingestion & KPI Calculation  
**Gate quản trị:** Gate G5 = IN_PROGRESS, Gate G6 = NOT_STARTED / BLOCKED  
**Vai trò:** Principal Big Data Architect, Senior PySpark Engineer, Independent Quality Auditor  
**Ngày lập:** 2026-10-20  

---

## 1. PHÁT HIỆN KIỂM TOÁN VÀ ĐÍNH CHÍNH DANH MỤC G6 (G6-C02 FINDING & ERRATA)

### 1.1. Hiện trạng sai lệch trong tài liệu kế hoạch G6 trước đây:
Trong tài liệu [`G6_T012_FINAL_EXECUTION_CHECKLIST_V2.md`](./G6_T012_FINAL_EXECUTION_CHECKLIST_V2.md) (bản sơ khai trước đính chính), Phần 4 đã liệt kê sai lệch nghiêm trọng danh mục 8 CORE KPI:
- Đã ghi: KPI-01 là "OTP-15 Rate", KPI-04 là "Severe Delay Rate $\ge 60$", KPI-07 là "Elapsed Time Ratio", KPI-08 là "Flight Volume & Cancellation Proxy".

### 1.2. Đính chính chính thức (Official Governance Errata):
1. **Bác bỏ hoàn toàn các chỉ số ngoài hợp đồng:**
   - **Severe Delay Rate $\ge 60$:** Không thuộc phạm vi 8 CORE KPI đã duyệt.
   - **Elapsed Time Ratio (Actual / Scheduled):** Không nằm trong hợp đồng thiết kế của `FP-DEC-012`.
   - **Cancellation Proxy:** Schema 34 cột hiện tại không có cờ hủy hay chuyển hướng (`CANCELLED`, `DIVERTED`); theo quyết định `FP-DEC-006` và rủi ro `OR-04`, tỷ lệ hủy được phân loại là **`NOT_COMPUTABLE`**, tuyệt đối không tự chế proxy.
   - **Flight Volume qua `FLIGHTS`:** Bị chặn bởi `FP-DEC-010` và `OR-01` do trường `FLIGHTS` luôn bằng $1.0$ mà không rõ ngữ nghĩa phân bổ trọng số.
2. **Khẳng định tính toàn vẹn của mã nguồn sản xuất:**
   - Kiểm tra mã nguồn thực tế tại `src/flight_pipeline/kpi/catalog.py` và `src/flight_pipeline/kpi/calculator.py` xác nhận: **Mã nguồn động cơ KPI hoàn toàn tuân thủ 100% hợp đồng `KPI_SPEC.md` và các quyết định `FP-DEC-008`, `FP-DEC-011`, `FP-DEC-012`, `FP-DEC-015`, `FP-DEC-016`**.
   - Không phát sinh lỗi `KPI_ENGINE_CONTRACT_MISMATCH`. Lỗi chỉ nằm ở tài liệu checklist và đã được sửa chữa dứt điểm tại Section 4 của `G6_T012_FINAL_EXECUTION_CHECKLIST_V2.md`.

---

## 2. MA TRẬN ĐỐI CHIẾU 8 CORE KPI THEO HỢP ĐỒNG THẨM QUYỀN

| Mã KPI | Tên chỉ số chính thức | Định nghĩa toán học trong Cohort $C$ | Mẫu số $N_{\text{valid}}$ | Submetrics | Quyết định liên quan |
| :---: | :--- | :--- | :--- | :---: | :---: |
| **KPI-01** | Tổng bản ghi accepted | $\text{count\_records}(C)$ | Toàn bộ bản ghi accepted trong cohort $C$ | Không | `FP-DEC-010`, `FP-DEC-012` |
| **KPI-02** | Tỷ lệ trễ đến $\ge 15$ phút | $\frac{\sum_{\text{valid}} 1[\text{ARR\_DELAY} \ge 15.0]}{N_{\text{valid}}(\text{ARR\_DELAY}, C)}$ | $N_{\text{valid}}(\text{ARR\_DELAY}, C)$ | Không | `FP-DEC-008`, `TS-005` |
| **KPI-03** | Trễ đến trung bình có dấu | $\frac{\sum_{\text{valid}} \text{ARR\_DELAY}}{N_{\text{valid}}(\text{ARR\_DELAY}, C)}$ | $N_{\text{valid}}(\text{ARR\_DELAY}, C)$ | Không (Giữ nguyên dấu âm chuyến đến sớm) | `FP-DEC-012`, `TS-006` |
| **KPI-04** | Tỷ lệ trễ đi $\ge 15$ phút | $\frac{\sum_{\text{valid}} 1[\text{DEP\_DELAY} \ge 15.0]}{N_{\text{valid}}(\text{DEP\_DELAY}, C)}$ | $N_{\text{valid}}(\text{DEP\_DELAY}, C)$ | Không | `FP-DEC-008`, `TS-005` |
| **KPI-05** | Trễ đi trung bình có dấu | $\frac{\sum_{\text{valid}} \text{DEP\_DELAY}}{N_{\text{valid}}(\text{DEP\_DELAY}, C)}$ | $N_{\text{valid}}(\text{DEP\_DELAY}, C)$ | Không (Giữ nguyên dấu âm chuyến cất cánh sớm) | `FP-DEC-012`, `TS-006` |
| **KPI-06** | Phân vị P50 và P90 độ trễ đến | GK-Sketch `percentile_approx(ARR_DELAY, [0.5, 0.9], accuracy=10000)` | $N_{\text{valid}}(\text{ARR\_DELAY}, C)$ | **2 submetrics:** `P50` và `P90` | `FP-DEC-015`, `TS-008` |
| **KPI-07** | Thời gian lăn bánh trung bình | $\text{avg}(\text{TAXI\_OUT})$ và $\text{avg}(\text{TAXI\_IN})$ | Từng trường riêng biệt: $N_{\text{valid}}(\text{TAXI\_OUT})$, $N_{\text{valid}}(\text{TAXI\_IN})$ | **2 submetrics:** `TAXI_OUT` và `TAXI_IN` | `FP-DEC-012`, `TS-006` |
| **KPI-08** | Thời gian bay và hành trình TB | $\text{avg}(\text{AIR\_TIME})$, $\text{avg}(\text{ACTUAL\_ELAPSED})$, $\text{avg}(\text{CRS\_ELAPSED})$ | Từng trường riêng biệt: $N_{\text{valid}}(\text{AIR})$, $N_{\text{valid}}(\text{ACTUAL})$, $N_{\text{valid}}(\text{CRS})$ | **3 submetrics:** `AIR_TIME`, `ACTUAL_ELAPSED_TIME`, `CRS_ELAPSED_TIME` | `FP-DEC-012`, `TS-006` |

---

## 3. CÁC QUY TẮC BẢO TOÀN VÀ XỬ LÝ BIÊN (BOUNDARY CONDITIONS)

1. **Xử lý mẫu số bằng 0 ($N_{\text{valid}} = 0$):**
   - Theo quyết định `FP-DEC-011`, khi một cohort không có bản ghi nào thỏa mãn điều kiện hợp lệ ($N_{\text{valid}} = 0$), giá trị tính toán `value` trả về là **`null`**, đồng thời gắn cờ `unit_status = "ZERO_METRIC_DENOMINATOR"`.
   - Tuyệt đối cấm gán giá trị $0.0$ khi mẫu số bằng 0 để tránh sai lệch phân tích.
2. **Bảo tồn độ trễ có dấu (Negative Signed Delays):**
   - Các giá trị âm (chuyến bay hạ cánh hoặc cất cánh sớm hơn lịch trình, ví dụ $\text{ARR\_DELAY} = -12.0$) bắt buộc phải được bảo toàn nguyên vẹn trong tính toán mean (KPI-03, KPI-05) và phân vị (KPI-06).
   - Tuyệt đối không thay thế giá trị âm bằng $0$ trong 8 CORE KPI (việc lấy $\max(\text{delay}, 0)$ chỉ thuộc chỉ số phụ tùy chọn KPI-09).
3. **Phân vị xấp xỉ `KPI-06`:**
   - Thuật toán GK-Sketch bắt buộc dùng tham số độ chính xác `accuracy = 10000`, bảo đảm giới hạn sai số thứ hạng $\epsilon_{\text{rank}} \le 0.01\%$.
4. **Chính sách ngưỡng cỡ mẫu tối thiểu `min-N` (FP-DEC-016):**
   - Phân cấp trạng thái xếp hạng:
     * `SUPPRESSED`: Khi $N_{\text{valid}} < \text{threshold}$ (`carrier-year < 1000`, `airport-year < 365`, `route-year < 100`).
     * `LOW_SAMPLE_CAUTION`: Khi $\text{threshold} \le N_{\text{valid}} < 3 \times \text{threshold}$.
     * `SUFFICIENT`: Khi $N_{\text{valid}} \ge 3 \times \text{threshold}$.
5. **Cấu trúc 17 cột canonical theo DC-11 / DC-12:**
   - Mọi bản ghi kết quả KPI đều phải xuất bản đủ 17 cột:
     `kpi_id`, `submetric`, `run_id`, `kpi_version`, `source_year`, `group_dimensions`, `filter_definition`, `count_records`, `count_metric_valid`, `excluded_count`, `metric_valid_rate`, `source_coverage_status`, `value`, `unit_status`, `min_n_status`, `quality_version`, `provenance_reference`.

---

## 4. KẾT LUẬN NGHIỆM THU

Hợp đồng 8 CORE KPI đã được xác lập hoàn chỉnh và khóa chặt giữa `KPI_SPEC.md`, `src/flight_pipeline/kpi/catalog.py`, `src/flight_pipeline/kpi/calculator.py`, và các tài liệu vận hành G6. Động cơ sẵn sàng cho giai đoạn tính toán KPI T-013 sau khi T-012 hoàn tất.
