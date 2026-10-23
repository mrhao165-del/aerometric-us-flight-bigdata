# T011-R1 REPRODUCED COUNTEREXAMPLES AND FLAW AUDIT

**Project:** US Flight Performance Analysis 2016–2024  
**Task:** T-011 R1 — Targeted Independent Audit Remediation  
**Parent Gate:** G5 (IN_PROGRESS)  
**Deliverable:** `docs/05-evidence/T011_R1_REPRODUCED_COUNTEREXAMPLES.md`  
**Execution Date:** 2026-10-19  
**Status:** **GATE R1-1 PASS / COUNTEREXAMPLES VERIFIED**

---

## 1. Mục đích & Phạm vi Kiểm thử

Gate R1-1 yêu cầu xây dựng bộ kiểm thử hồi quy độc lập trước khi tiến hành chỉnh sửa mã nguồn nhằm tái hiện đầy đủ và khách quan 7 lỗ hổng/khiếm khuyết (R1-F01 đến R1-F07) đã được kiểm toán viên độc lập chỉ ra.

Tập tin kiểm thử phản chứng: [`tests/test_t011_r1_counterexamples.py`](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/tests/test_t011_r1_counterexamples.py).

Kết quả chạy kiểm thử xác minh:
```
Ran 7 tests in 53.455s
OK
```

---

## 2. Chi tiết 7 Khiếm khuyết Được Tái hiện (R1-F01 .. R1-F07)

### R1-F01: BTS Parity Harness Stub & Unconditional Zero Exit Code
- **Vị trí:** [`tools/qa/run_ts018_bts_parity.py`](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/tools/qa/run_ts018_bts_parity.py#L43-L49)
- **Hành vi khiếm khuyết:**
  1. Khi phát hiện tập tin tại các đường dẫn tiềm năng, harness gán `dataset_records = []` và `bts_records = []` mà không hề đọc dữ liệu thực, không kiểm tra schema hay xác minh digest SHA-256 đối soát.
  2. Hàm `run_ts018_reconciliation()` kết thúc vô điều kiện với `return 0` ngay cả khi dữ liệu không xác thực hoặc phát hiện sai lệch.
- **Chứng cứ phản chứng:** Test `test_reproduce_r1_f01_bts_harness_stub_exit_zero` khẳng định mã nguồn hiện hành chứa việc gán mảng rỗng và thoát zero vô điều kiện.

### R1-F02: BTS Reconciler False Pass on Nulls & Unmatched Records
- **Vị trí:** [`src/flight_pipeline/kpi/bts_reconciler.py`](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/src/flight_pipeline/kpi/bts_reconciler.py#L285-L291)
- **Hành vi khiếm khuyết:**
  1. Điều kiện trả về `TS018_PASS_AUTHENTIC_PARITY_ESTABLISHED` chỉ kiểm tra `not has_mismatch and summary.unique_key_matches > 0`. Nếu có 1 bản ghi khớp nhưng toàn bộ 7 độ đo là NULL (`null_null_agreement`) và có hàng nghìn bản ghi không khớp (`unmatched_dataset_records > 0`, `unmatched_bts_records > 0`), reconciler vẫn tuyên bố PASS.
  2. Bỏ qua các bản ghi trùng lặp khóa (`ambiguous_duplicate_keys > 0`).
  3. `extract_composite_key` âm thầm ép kiểu `float(flight_num)` lỗi thành `0.0`, che giấu lỗi khóa composite.
- **Chứng cứ phản chứng:** Test `test_reproduce_r1_f02_bts_reconciler_false_pass_on_unmatched_and_nulls` đã chứng minh với 1 bản ghi all-NULL và 2 bản ghi unmatched, kết quả trả về vẫn là `TS018_PASS_AUTHENTIC_PARITY_ESTABLISHED`.

### R1-F03: GK-Sketch Tolerance & Finite Sample Discretization
- **Vị trí:** [`tests/test_t011_ts008_repeatability.py`](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/tests/test_t011_ts008_repeatability.py#L132-L135)
- **Hành vi khiếm khuyết:**
  1. Assert kiểm tra sai số rank cho phép tolerance `0.015` (1.5%), lỏng hơn 150 lần so với chuẩn mực kỹ thuật `accuracy=10000` ($\epsilon \le 1/10000 = 0.0001 = 0.01\%$).
  2. Cỡ mẫu thử nghiệm $N = 5000$ có bước rời rạc tối thiểu $1/N = 0.0002 > 0.0001$, khiến việc kiểm chứng toán học sai số $\le 0.0001$ trên mẫu rời rạc là không khả thi.
- **Chứng cứ phản chứng:** Test `test_reproduce_r1_f03_ts008_loose_tolerance_and_insufficient_sample` khẳng định ngưỡng `0.015` và bước rời rạc $1/5000 = 0.0002 > 0.0001$.

### R1-F04: Empty Cohort Produces SQL NULL Counts & Wrong Unit Status
- **Vị trí:** [`src/flight_pipeline/kpi/calculator.py`](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/src/flight_pipeline/kpi/calculator.py#L130-L167)
- **Hành vi khiếm khuyết:**
  1. Khi DataFrame cohort rỗng (0 dòng), hàm `df.agg(*agg_exprs)` của PySpark sinh ra dòng chứa giá trị SQL NULL cho toàn bộ các biểu thức `F.sum(...)`.
  2. Dẫn đến `count_metric_valid` bị NULL, `excluded_count = 0 - NULL = NULL`.
  3. Biểu thức điều kiện `count_valid_col == 0` trở thành `NULL == 0` (đánh giá NULL trong logic tam trị), khiến `unit_status` không chuyển thành `ZERO_METRIC_DENOMINATOR` mà giữ nguyên `PROVISIONAL`.
- **Chứng cứ phản chứng:** Test `test_reproduce_r1_f04_empty_cohort_null_counts` xác nhận trên DataFrame rỗng, `count_metric_valid` và `excluded_count` là `None`, và `unit_status` không phải là `ZERO_METRIC_DENOMINATOR`.

### R1-F05: Gap in Dimension Boundary Thresholds & Naming Coverage
- **Vị trí:** [`src/flight_pipeline/kpi/aggregators.py`](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/src/flight_pipeline/kpi/aggregators.py#L86-L90)
- **Hành vi khiếm khuyết:**
  1. `evaluate_min_n` chỉ hỗ trợ `("airport-year", "airport_year", "origin-year", "dest-year")`, trả về `NOT_APPLICABLE` nếu truyền `destination-year` hoặc `destination_year`.
  2. Thiếu kiểm thử biên toàn diện cho airport-year ($N \in \{364, 365, 1094, 1095\}$) và route-year ($N \in \{99, 100, 299, 300\}$).
  3. Khi cột đếm chứa giá trị NULL, logic `valid_count_col < min_n` bị NULL và rơi vào nhánh `.otherwise(SUFFICIENT)`.
- **Chứng cứ phản chứng:** Test `test_reproduce_r1_f05_dimension_thresholds_gap` khẳng định `destination-year` bị coi là `NOT_APPLICABLE` và NULL count bị gắn nhãn sai thành `SUFFICIENT`.

### R1-F06: Missing Cohort Year Integrity & OR-05 Bypass
- **Vị trí:** [`src/flight_pipeline/kpi/calculator.py`](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/src/flight_pipeline/kpi/calculator.py#L90-L96)
- **Hành vi khiếm khuyết:**
  1. Người gọi có thể truyền `source_coverage_status="VERIFIED_WITH_SCOPE"` cho năm 2024, vi phạm quy định chuẩn tắc OR-05 (2024 bắt buộc phải là `PARTIAL`).
  2. Hàm `compute_kpis_for_cohort` không kiểm tra tính nhất quán giữa cột `FL_DATE` và tham số `source_year`, chấp nhận dữ liệu năm khác mà không cảnh báo.
  3. Sử dụng `cast(DoubleType())` thay vì `try_cast` an toàn ANSI.
- **Chứng cứ phản chứng:** Test `test_reproduce_r1_f06_source_year_and_or05_bypass` cho thấy năm 2024 nhận `VERIFIED_WITH_SCOPE` thành công và chuyến bay 2017 được tính toán dưới `source_year="2016"`.

### R1-F07: Fault Injection Mocks Real Storage IO
- **Vị trí:** [`tests/test_t011_fault_injection.py`](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/tests/test_t011_fault_injection.py#L71-L85)
- **Hành vi khiếm khuyết:**
  1. Kịch bản F01 chỉ kiểm tra tập tin không tồn tại và thư mục staging không tồn tại, không hề kích hoạt đọc pipeline thật.
  2. Kịch bản F02 chỉ kiểm tra thư mục staging rỗng, không mô phỏng lỗi gián đoạn ghi staging.
  3. Kịch bản F08 chưa kiểm tra việc khôi phục và đối soát dữ liệu dở dang.
- **Chứng cứ phản chứng:** Test `test_reproduce_r1_f07_fault_injection_mock_bypass` khẳng định kịch bản kiểm thử F01 không gọi đến bất kỳ hàm đọc nào.

---

## 3. Kết luận Gate R1-1

Toàn bộ 7 khiếm khuyết đã được tái hiện và ghi nhận đầy đủ, tạo tiền đề để chuyển sang **Gate R1-2: Triển khai Chỉnh sửa Mã nguồn Mục tiêu**.
