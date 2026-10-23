# T011_FULL_KPI_ENGINE_VERIFICATION — BÁO CÁO KIỂM CHUẨN ENGINE 8 CORE KPIS VÀ ĐỐI SOÁT TOÁN HỌC ĐỘC LẬP

- **Mã nhiệm vụ:** `T-011` (Gate G5: KPI Sample Smoke, BTS Parity, TS-008, TS-013 & Review Packaging)
- **Gate:** `G5` (IN_PROGRESS)
- **Thời điểm kiểm toán:** 2026-10-18T20:48:30+07:00
- **Tiêu chuẩn tuân thủ:** [`AGENTS.md`](../../AGENTS.md), [`KPI_SPEC.md`](../02-design/KPI_SPEC.md), [`DATA_CONTRACT.md`](../02-design/DATA_CONTRACT.md) (DC-11, DC-12), [`DECISIONS.md`](../02-design/DECISIONS.md) (FP-DEC-008, FP-DEC-011, FP-DEC-012, FP-DEC-015, FP-DEC-016, FP-DEC-017).
- **Trạng thái Gate 1:** **PASS (KPI Engine Verified & Oracle Parity 100%)**

---

## 1. TỔNG QUAN TRIỂN KHAI PACKAGE `src/flight_pipeline/kpi/`

Package mới `src/flight_pipeline/kpi/` đã được thiết kế và triển khai hoàn thiện theo kiến trúc mô-đun chuẩn tắc:
- `catalog.py`: Khai báo 8 CORE KPIs (`KPI-01..08`), 12 lát cắt submetrics chuẩn, các hằng số min-N (1000/365/100), độ chính xác GK-sketch (accuracy=10000), và danh mục 17 trường output.
- `schema.py`: Đặc tả PySpark `StructType` cho 17 cột chuẩn của bảng KPI.
- `aggregators.py`: Vị từ lọc giá trị hợp lệ số an toàn Spark ANSI mode, hàm đánh giá min-N và các biểu thức phân vị.
- `calculator.py`: Lớp `KpiCalculator` thực hiện gom nhóm đa chiều (`year`, `carrier-year`, `airport-year`, `route-year`), áp dụng các bộ lọc, hạch toán mẫu số độc lập và xuất bản bảng kết quả.
- `__init__.py`: Đóng gói các giao diện công khai an toàn.

---

## 2. MA TRẬN 8 CORE KPIS VÀ CÔNG THỨC NGHIỆP VỤ CHUẨN TẮC

| Mã KPI | Tên chỉ số & Submetric | Trường dữ liệu mục tiêu | Quy tắc tính & Mẫu số hợp lệ | Ràng buộc nghiệp vụ bắt buộc |
|:---:|---|:---:|---|---|
| **KPI-01** | Total accepted flight records | Không (Record count) | `count_records(C)` | Dùng số lượng bản ghi accepted; **cấm dùng `sum(FLIGHTS)`** (`FP-DEC-010`). |
| **KPI-02** | Arrival delay rate >= 15 min | `ARR_DELAY` | `count(ARR_DELAY >= 15.0) / N_valid(ARR_DELAY)` | Lấy điểm biên đúng $15.0$ phút (`FP-DEC-008`); loại trừ null/NaN/Inf. |
| **KPI-03** | Mean signed arrival delay | `ARR_DELAY` | `sum(ARR_DELAY) / N_valid(ARR_DELAY)` | **Bảo toàn dấu âm** của các chuyến bay đến sớm (`FP-DEC-008`); cấm gán âm về 0. |
| **KPI-04** | Departure delay rate >= 15 min | `DEP_DELAY` | `count(DEP_DELAY >= 15.0) / N_valid(DEP_DELAY)` | Lấy điểm biên đúng $15.0$ phút (`FP-DEC-008`); loại trừ null/NaN/Inf. |
| **KPI-05** | Mean signed departure delay | `DEP_DELAY` | `sum(DEP_DELAY) / N_valid(DEP_DELAY)` | **Bảo toàn dấu âm** của các chuyến bay khởi hành sớm; cấm gán âm về 0. |
| **KPI-06** | P50 (Median) arrival delay | `ARR_DELAY` | `percentile_approx(ARR_DELAY, [0.5], 10000)` | Thuật toán GK-sketch trên cohort metric-valid (`FP-DEC-015`). |
| **KPI-06** | P90 arrival delay | `ARR_DELAY` | `percentile_approx(ARR_DELAY, [0.9], 10000)` | Thuật toán GK-sketch trên cohort metric-valid (`FP-DEC-015`). |
| **KPI-07** | Submetric `TAXI_OUT` mean | `TAXI_OUT` | `sum(TAXI_OUT) / N_valid(TAXI_OUT)` | Mẫu số độc lập $N_{\text{valid}}(\text{TAXI\_OUT})$, miền $\ge 0.0$ (`DC-12`). |
| **KPI-07** | Submetric `TAXI_IN` mean | `TAXI_IN` | `sum(TAXI_IN) / N_valid(TAXI_IN)` | Mẫu số độc lập $N_{\text{valid}}(\text{TAXI\_IN})$, miền $\ge 0.0$ (`DC-12`). |
| **KPI-08** | Submetric `AIR_TIME` mean | `AIR_TIME` | `sum(AIR_TIME) / N_valid(AIR_TIME)` | Mẫu số độc lập $N_{\text{valid}}(\text{AIR\_TIME})$, miền $> 0.0$ (`DC-12`). |
| **KPI-08** | Submetric `ACTUAL_ELAPSED_TIME` | `ACTUAL_ELAPSED_TIME` | `sum(ACTUAL) / N_valid(ACTUAL)` | Mẫu số độc lập $N_{\text{valid}}(\text{ACTUAL\_ELAPSED\_TIME})$, miền $> 0.0$. |
| **KPI-08** | Submetric `CRS_ELAPSED_TIME` | `CRS_ELAPSED_TIME` | `sum(CRS) / N_valid(CRS)` | Mẫu số độc lập $N_{\text{valid}}(\text{CRS\_ELAPSED\_TIME})$, miền $> 0.0$. |

---

## 3. THẨM ĐỊNH HỢP ĐỒNG 17 TRƯỜNG ĐẦU RA (17-FIELD OUTPUT CONTRACT)

Bảng kết quả của `KpiCalculator` đã được kiểm chứng xuất bản chính xác **17 trường dữ liệu chuẩn** theo đúng thứ tự:
1. `kpi_id` (string, e.g. "KPI-01")
2. `submetric` (string, e.g. "TAXI_OUT", "P50", hoặc null)
3. `run_id` (string, e.g. "test_run_t011")
4. `kpi_version` (string, e.g. "1.0.0")
5. `source_year` (string, e.g. "2016", "2024")
6. `group_dimensions` (string, e.g. "cohort=all;source_year=2016" hoặc "OP_CARRIER=AA;source_year=2016")
7. `filter_definition` (string, e.g. "accepted_flights")
8. `count_records` (long, tổng số bản ghi trong nhóm)
9. `count_metric_valid` (long, số bản ghi có metric hợp lệ cho chính KPI/submetric đó)
10. `excluded_count` (long, `count_records - count_metric_valid` theo DC-12)
11. `metric_valid_rate` (double, `count_metric_valid / count_records` nếu `count_records > 0`, ngược lại null)
12. `source_coverage_status` (string, "VERIFIED_WITH_SCOPE" hoặc "PARTIAL" cho năm 2024 theo OR-05)
13. `value` (double, giá trị chỉ số tính toán được, hoặc null khi mẫu số bằng 0)
14. `unit_status` (string, "OFFICIAL_MINUTES_EMPIRICALLY_CONSISTENT_PROVISIONAL", "COUNT_RECORDS", hoặc "ZERO_METRIC_DENOMINATOR")
15. `min_n_status` (string, "SUPPRESSED", "LOW_SAMPLE_CAUTION", "SUFFICIENT", hoặc "NOT_APPLICABLE")
16. `quality_version` (string, "docs-v1.1")
17. `provenance_reference` (string, con trỏ bằng chứng truy xuất nguồn gốc)

---

## 4. KẾT QUẢ ĐỐI SOÁT TOÁN HỌC VỚI INDEPENDENT PYTHON ORACLE

Một bộ kiểm chuẩn độc lập thuần túy viết bằng Python (`_compute_python_oracle`) hoàn toàn tách biệt khỏi PySpark đã được xây dựng trong `tests/test_t011_kpi_engine.py`. Kết quả đối soát 7 trường hợp kiểm thử tự động:

1. **`test_01_synthetic_oracle_parity_clean_data` [PASS]:**
   - Đối chiếu 12 dòng KPI trên tập dữ liệu tổng hợp chứa đầy đủ các trường hợp: đến sớm, đúng 15.0, trễ nặng, trễ sát biên (14.9), và thời tiết null.
   - Sai lệch số học giữa PySpark Engine và Python Oracle: **$\Delta = 0.00000$ (Khớp chính xác 100%)**.
   - Hạch toán dòng: `count_records == count_metric_valid + excluded_count` trên 100% các dòng.
2. **`test_02_negative_delays_preserved_in_signed_means` [PASS]:**
   - Dữ liệu đến sớm `ARR_DELAY = -30.0` và trễ `+10.0` $\implies$ Signed Mean = `-10.0`.
   - Khởi hành sớm `DEP_DELAY = -10.0` và đúng giờ `0.0` $\implies$ Signed Mean = `-5.0`.
   - Khẳng định: Dấu âm không bị biến mất, không bị đổi thành 0.
3. **`test_03_exact_15_minute_boundary` [PASS]:**
   - Chuyến bay có độ trễ `14.999` không được tính vào trễ $\ge 15$.
   - Chuyến bay có độ trễ `15.000` được tính vào trễ $\ge 15$.
   - Tỷ lệ ra đúng $1 / 2 = 0.50000$.
4. **`test_04_zero_metric_denominator_safety` [PASS]:**
   - Khi nhóm không có bất kỳ bản ghi nào có metric hợp lệ (`count_metric_valid == 0`):
     - `value = None` (SQL NULL), loại trừ hoàn toàn `ZeroDivisionError`.
     - `unit_status = "ZERO_METRIC_DENOMINATOR"`.
     - Cấm trả về $0.0$ giả mạo.
5. **`test_05_independent_denominators_kpi07_and_kpi08` [PASS]:**
   - Bản ghi khuyết `TAXI_IN` nhưng có `TAXI_OUT` vẫn được tính vào trung bình `TAXI_OUT` với mẫu số $N=1$.
   - Tương tự cho `AIR_TIME` ($N=1$), `ACTUAL_ELAPSED_TIME` ($N=1$), và `CRS_ELAPSED_TIME` ($N=2$).
   - Mẫu số hoàn toàn độc lập giữa các submetrics (`DC-12`).
6. **`test_06_min_n_threshold_boundaries` [PASS]:**
   - Carrier-year ($N=1000$): $999 \to$ `SUPPRESSED`, $1000 \to$ `LOW_SAMPLE_CAUTION`, $2999 \to$ `LOW_SAMPLE_CAUTION`, $3000 \to$ `SUFFICIENT`.
   - Airport-year ($N=365$): $364 \to$ `SUPPRESSED`, $365 \to$ `LOW_SAMPLE_CAUTION`, $1094 \to$ `LOW_SAMPLE_CAUTION`, $1095 \to$ `SUFFICIENT`.
   - Route-year ($N=100$): $99 \to$ `SUPPRESSED`, $100 \to$ `LOW_SAMPLE_CAUTION`, $299 \to$ `LOW_SAMPLE_CAUTION`, $300 \to$ `SUFFICIENT`.
7. **`test_07_year_2024_partial_coverage_metadata` [PASS]:**
   - Năm 2024 tự động gán nhãn `source_coverage_status = PARTIAL` (`OR-05`).

---

## 5. KẾT LUẬN GATE 1

- Module KPI Engine triển khai đầy đủ 8 CORE KPIs theo hợp đồng thiết kế.
- Bảng kết quả tuân thủ nghiêm ngặt cấu trúc 17 trường chuẩn.
- Đạt 100% đối soát toán học với Python Oracle độc lập; không có lỗi chia cho 0, không làm mất delay âm, không sai lệch mẫu số.
- Không có bất kỳ thay đổi nào vào dữ liệu thô `data/raw/` hoặc con trỏ xuất bản `data/curated/latest`.
- **GATE 1 CHÍNH THỨC ĐẠT (PASS) — Cho phép chuyển sang Phase 2 (TS-008, TS-012 & Contractual Tests).**
