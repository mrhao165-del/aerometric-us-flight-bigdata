# T011-R1 MIN-N THRESHOLDS & DIMENSION COVERAGE AUDIT

**Project:** US Flight Performance Analysis 2016–2024  
**Task:** T-011 R1 — Targeted Independent Audit Remediation  
**Parent Gate:** G5 (IN_PROGRESS)  
**Deliverable:** `docs/05-evidence/T011_R1_MIN_N_AND_COVERAGE_AUDIT.md`  
**Date:** 2026-10-19  
**Status:** **AUDIT VERIFIED / EXHAUSTIVE BOUNDARY MATRIX PASS**

---

## 1. Bối cảnh & Vấn đề Kỹ thuật (R1-F05)

Quyết định chuẩn tắc FP-DEC-016 và đặc tả `KPI_SPEC.md` quy định ngưỡng cỡ mẫu tối thiểu (min-N thresholds) trên số lượng bản ghi hợp lệ của chỉ số (`count_metric_valid`) để gắn nhãn độ tin cậy thống kê cho các chiều phân tích.

Kiểm toán viên độc lập chỉ ra rằng:
1. `evaluate_min_n` trong `src/flight_pipeline/kpi/aggregators.py` chỉ đối khớp cứng với một số tên chiều hạn chế (`"airport-year"`, `"origin-year"`, `"dest-year"`), trả về sai lệch `NOT_APPLICABLE` đối với các alias hợp lệ như `"destination-year"`, `"destination_year"`, `"dest_year"`.
2. Kiểm thử đơn vị tại G5 chỉ kiểm tra 4 giá trị của chiều `carrier-year`, bỏ sót hoàn toàn việc kiểm tra biên thực tế của `airport-year` (365 / 1095) và `route-year` (100 / 300).
3. Khi cột số đếm nhận giá trị NULL, logic SQL `valid_count_col < min_n` bị đánh giá là NULL và rơi vào nhánh mặc định `.otherwise(SUFFICIENT)`, dẫn đến việc gắn nhãn sai nghiêm trọng một tập dữ liệu rỗng thành "đủ mẫu".

---

## 2. Quy tắc Ngưỡng Chuẩn tắc FP-DEC-016

| Chiều phân tích (`dimension_type`) | Ngưỡng cơ sở ($min\_N$) | Ngưỡng đủ mẫu ($3 \times min\_N$) | Quy tắc phân loại trạng thái |
|:---|:---:|:---:|:---|
| **Carrier-Year** | 1,000 | 3,000 | $N < 1000 \to \text{SUPPRESSED}$<br>$1000 \le N < 3000 \to \text{LOW\_SAMPLE\_CAUTION}$<br>$N \ge 3000 \to \text{SUFFICIENT}$ |
| **Airport-Year**<br>(bao gồm origin/destination) | 365 | 1,095 | $N < 365 \to \text{SUPPRESSED}$<br>$365 \le N < 1095 \to \text{LOW\_SAMPLE\_CAUTION}$<br>$N \ge 1095 \to \text{SUFFICIENT}$ |
| **Route-Year**<br>(cặp tuyến bay có hướng) | 100 | 300 | $N < 100 \to \text{SUPPRESSED}$<br>$100 \le N < 300 \to \text{LOW\_SAMPLE\_CAUTION}$<br>$N \ge 300 \to \text{SUFFICIENT}$ |
| **Các chiều khác** (ví dụ `year`) | Không áp dụng | Không áp dụng | Luôn trả về `NOT_APPLICABLE` |

---

## 3. Triển khai Chỉnh sửa Mã nguồn

Trong [`src/flight_pipeline/kpi/aggregators.py`](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/src/flight_pipeline/kpi/aggregators.py#L71-L98):
1. **Mở rộng tập alias đầy đủ:**
   - Airport: `("airport-year", "airport_year", "origin-year", "origin_year", "dest-year", "dest_year", "destination-year", "destination_year")`.
   - Route: `("route-year", "route_year", "pair-year", "pair_year")`.
2. **Bảo vệ chống giá trị NULL:**
   ```python
   safe_count = F.coalesce(valid_count_col, F.lit(0))
   return (
       F.when(safe_count < min_n, F.lit(MIN_N_STATUS_SUPPRESSED))
       .when(safe_count < 3 * min_n, F.lit(MIN_N_STATUS_LOW_SAMPLE_CAUTION))
       .otherwise(F.lit(MIN_N_STATUS_SUFFICIENT))
   )
   ```
   Nếu `valid_count_col` là NULL (ví dụ do DataFrame rỗng hoặc phép tổng hợp lỗi), giá trị được quy đổi về 0 và gắn nhãn chính xác là `SUPPRESSED`.

---

## 4. Ma trận Kiểm thử Biên Toàn diện (Exhaustive Boundary Matrix)

Đã triển khai trong [`tests/test_t011_kpi_engine.py`](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/tests/test_t011_kpi_engine.py#L407-L445) với 20 ca kiểm thử biên độc lập:

| STT | Giá trị đếm ($N$) | Chiều (`dimension_type`) | Trạng thái kỳ vọng | Kết quả thực tế | Phán quyết |
|:---:|:---:|:---|:---|:---|:---:|
| 1 | 999 | `carrier-year` | `SUPPRESSED` | `SUPPRESSED` | PASS |
| 2 | 1000 | `carrier-year` | `LOW_SAMPLE_CAUTION` | `LOW_SAMPLE_CAUTION` | PASS |
| 3 | 2999 | `carrier-year` | `LOW_SAMPLE_CAUTION` | `LOW_SAMPLE_CAUTION` | PASS |
| 4 | 3000 | `carrier-year` | `SUFFICIENT` | `SUFFICIENT` | PASS |
| 5 | 364 | `airport-year` | `SUPPRESSED` | `SUPPRESSED` | PASS |
| 6 | 365 | `airport-year` | `LOW_SAMPLE_CAUTION` | `LOW_SAMPLE_CAUTION` | PASS |
| 7 | 1094 | `airport-year` | `LOW_SAMPLE_CAUTION` | `LOW_SAMPLE_CAUTION` | PASS |
| 8 | 1095 | `airport-year` | `SUFFICIENT` | `SUFFICIENT` | PASS |
| 9 | 364 | `destination-year` | `SUPPRESSED` | `SUPPRESSED` | PASS |
| 10 | 365 | `destination-year` | `LOW_SAMPLE_CAUTION` | `LOW_SAMPLE_CAUTION` | PASS |
| 11 | 1095 | `origin-year` | `SUFFICIENT` | `SUFFICIENT` | PASS |
| 12 | 1095 | `dest_year` | `SUFFICIENT` | `SUFFICIENT` | PASS |
| 13 | 99 | `route-year` | `SUPPRESSED` | `SUPPRESSED` | PASS |
| 14 | 100 | `route-year` | `LOW_SAMPLE_CAUTION` | `LOW_SAMPLE_CAUTION` | PASS |
| 15 | 299 | `route-year` | `LOW_SAMPLE_CAUTION` | `LOW_SAMPLE_CAUTION` | PASS |
| 16 | 300 | `route-year` | `SUFFICIENT` | `SUFFICIENT` | PASS |
| 17 | 300 | `pair_year` | `SUFFICIENT` | `SUFFICIENT` | PASS |
| 18 | `None` (NULL) | `carrier-year` | `SUPPRESSED` | `SUPPRESSED` | PASS |
| 19 | `None` (NULL) | `airport-year` | `SUPPRESSED` | `SUPPRESSED` | PASS |
| 20 | 500 | `year` | `NOT_APPLICABLE` | `NOT_APPLICABLE` | PASS |

**Kết luận:** Toàn bộ 20 điểm kiểm thử biên trên cả ba chiều và alias đều đạt kết quả chính xác 100%, giải quyết dứt điểm khiếm khuyết R1-F05.
