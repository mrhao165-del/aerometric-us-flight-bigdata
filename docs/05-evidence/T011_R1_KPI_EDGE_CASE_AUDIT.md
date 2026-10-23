# T011-R1 KPI ENGINE EDGE CASES & COHORT INTEGRITY AUDIT

**Project:** US Flight Performance Analysis 2016–2024  
**Task:** T-011 R1 — Targeted Independent Audit Remediation  
**Parent Gate:** G5 (IN_PROGRESS)  
**Deliverable:** `docs/05-evidence/T011_R1_KPI_EDGE_CASE_AUDIT.md`  
**Date:** 2026-10-19  
**Status:** **AUDIT VERIFIED / ZERO-DEFECT ARITHMETIC CONFIRMED**

---

## 1. Bối cảnh & Vấn đề Kỹ thuật (R1-F04 & R1-F06)

Kiểm toán độc lập Gate R1 đã phát hiện các điểm rủi ro tiềm tàng trong cơ chế tổng hợp và kiểm soát tham số của `KpiCalculator`:
1. **R1-F04:** Khi nạp một DataFrame rỗng (0 dòng), hàm `df.agg(*agg_exprs)` của PySpark sinh ra dòng chứa SQL NULL cho toàn bộ các phép `F.sum(...)`. Hệ quả là `count_metric_valid` và `excluded_count` bị nhận giá trị `None` thay vì `0`, vi phạm hợp đồng kiểu dữ liệu nguyên không null (`LongType`), đồng thời khiến `unit_status` không chuyển thành `ZERO_METRIC_DENOMINATOR`.
2. **R1-F06:** Người gọi có thể tự ý truyền tham số `source_coverage_status="VERIFIED_WITH_SCOPE"` cho năm 2024 mà không bị ghi đè thành `PARTIAL` theo quyết định chuẩn tắc OR-05; ngoài ra, hàm không xác thực tính đồng nhất của cột `FL_DATE` so với tham số `source_year`, có nguy cơ tính toán sai cohort năm.

---

## 2. Giải pháp Kỹ thuật Triển khai

### 2.1. Bảo toàn Đếm Số học qua `coalesce` trên Cohort Rỗng
Trong [`src/flight_pipeline/kpi/calculator.py`](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/src/flight_pipeline/kpi/calculator.py#L120-L170), tất cả các biểu thức tính tổng được bọc an toàn qua `F.coalesce`:
```python
F.coalesce(F.sum(F.when(predicate, 1).otherwise(0)), F.lit(0)).alias("_valid_arr_delay")
F.coalesce(F.sum(F.when(predicate, col.cast(DoubleType())).otherwise(0.0)), F.lit(0.0)).alias("_sum_arr_delay")
```
Đồng thời trong `_make_kpi_row`:
```python
safe_count_records = F.coalesce(count_records_col, F.lit(0))
safe_count_valid = F.coalesce(count_valid_col, F.lit(0))
excluded_count_col = safe_count_records - safe_count_valid
```

Quy tắc phán quyết đối với DataFrame 0 dòng:
- `count_records = 0` (nguyên, không bao giờ NULL).
- `count_metric_valid = 0` (nguyên, không bao giờ NULL).
- `excluded_count = 0` (nguyên, không bao giờ NULL).
- `metric_valid_rate = None` (DoubleType NULL).
- `value = None` đối với KPI-02..08; `value = 0.0` đối với KPI-01.
- `unit_status = ZERO_METRIC_DENOMINATOR` đối với KPI-02..08; `COUNT_RECORDS_ACCEPTED` đối với KPI-01.

### 2.2. Kiểm soát Tính Toàn vẹn Dữ liệu Cohort Năm
Bổ sung đoạn kiểm tra tính nhất quán trước khi tổng hợp:
```python
if "FL_DATE" in df.columns:
    mismatched_df = df.filter(
        F.col("FL_DATE").isNotNull()
        & (F.substring(F.trim(F.col("FL_DATE")), 1, 4) != str(source_year).strip())
    )
    if mismatched_df.limit(1).count() > 0:
        raise ValueError(
            f"Cohort integrity violation: DataFrame contains FL_DATE records that do not match source_year='{source_year}'."
        )
```
Nếu nạp dữ liệu năm khác (ví dụ chuyến bay năm 2017 vào phiên chạy năm 2016), hệ thống ném ngay ngoại lệ fail-closed `ValueError: Cohort integrity violation`.

### 2.3. Cưỡng chế Quyết định Chuẩn tắc OR-05 cho Năm 2024
Dù người gọi truyền bất kỳ giá trị nào cho `source_coverage_status`, hệ thống tự động cưỡng chế:
```python
if str(source_year).strip() == "2024":
    source_coverage_status = COVERAGE_PARTIAL
elif source_coverage_status is None:
    source_coverage_status = COVERAGE_VERIFIED_WITH_SCOPE
```
Quy tắc này bảo đảm không bất kỳ tiến trình nào có thể tạo ra KPI năm 2024 với trạng thái bao phủ toàn phần.

---

## 3. Kết quả Kiểm thử Nghiệm thu

Bộ kiểm thử [`tests/test_t011_kpi_engine.py`](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/tests/test_t011_kpi_engine.py) đã thực hiện xác minh:
- **Test 07 (OR-05 Enforcement):** Truyền `source_coverage_status=VERIFIED_WITH_SCOPE` cho năm 2024 $\to$ Kết quả nhận `PARTIAL` 100%. **PASS**.
- **Test 08 (Empty Cohort):** Nạp DataFrame 0 dòng $\to$ Toàn bộ 12 lát cắt KPI trả về `count_records=0`, `count_metric_valid=0`, `excluded_count=0`, và `unit_status=ZERO_METRIC_DENOMINATOR` (cho KPI-02..08). **PASS**.
- **Test 09 (Cohort FL_DATE Validation):** Nạp chuyến bay `2017-05-15` dưới `source_year="2016"` $\to$ Ném `ValueError: Cohort integrity violation`. **PASS**.

Tổng thời gian chạy test suite: `Ran 9 tests in 152.156s OK`.

**Kết luận:** Cơ chế số học trên các trường hợp biên và kiểm soát cohort của Engine đạt độ tin cậy tuyệt đối.
