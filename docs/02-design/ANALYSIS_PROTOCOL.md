# ANALYSIS_PROTOCOL — Giao thức nghiên cứu mô tả

## Thiết kế nghiên cứu
- Loại hình: observational/descriptive, phân tích trên bộ dữ liệu flight-with-weather đã cung cấp.
- Cửa sổ: 2016–2024 bao gồm cả 2024. Không có training/validation/test hoặc sealed holdout vì scope mới không huấn luyện mô hình.
- Đơn vị phân tích sơ bộ: bản ghi nguồn; flight event grain/độ bao phủ chưa được xác nhận, phải mô tả chính xác trong báo cáo.
- Analytic population: **accepted records** theo `DATA_CONTRACT.md` DC-11/12; raw/quarantined/rejected được hạch toán ở source-year và chỉ số hợp lệ theo từng metric. Không khẳng định toàn bộ lịch bay ở Mỹ.
- Outcome: các measures observed như `ARR_DELAY`, `DEP_DELAY`, taxi, elapsed, air time, **cần xác minh đơn vị/domain qua T-003**; date/airport/carrier là dimensions.

## Các bước phân tích
1. Kiểm toán dữ liệu, provenance, schema, số hàng, missing, outliers, category coverage.
2. Khóa cohort definition / numerator / denominator trước khi tính KPI.
3. Aggregate theo năm/tháng và stratify theo hãng/airport/route; luôn công khai `count_records`, `count_metric_valid`, `excluded_count`, `metric_valid_rate` và `source_coverage_status` (xem DATA_CONTRACT DC-11/12), không dùng tên `coverage_rate` không rõ nghĩa.
4. Tạo biểu đồ xu hướng, distributions (trung bình vs median/percentile), kiểm tra sensitivity outliers.
5. Diễn giải giai đoạn 2020 với giới hạn thay đổi cung ứng, không suy diễn nhân quả.
6. Nếu có chứng cứ Weather provenance và unit: exploratory association, stratify season/airport để giảm confounding; **không** gọi là causal effect.
7. Mọi chart/query: lưu `RESULTS_REGISTER` với source audit/run/config/KPI/version.

## Tránh các sai lầm phương pháp
- Không so sánh average của hãng ít chuyến với hãng nhiều chuyến mà không hiển thị N và min-N guard.
- Không dùng record count làm mẫu số 'scheduled flight cancellation rate'.
- Không kiểm tra thời gian qua ngày bằng trừ timestamp nguồn chưa được chứng minh rollover.
- Không dùng missing Weather = zero, không coi một giá trị scalar là bản tin thời tiết phát hành trước chuyến bay.
- Không nạp từ `leakage_audit.md` những điều cấm dùng `DEP_DELAY`/operations cho retrospective: đó là quy tắc **input X của mô hình preflight**, khác với outcome thống kê.

## So sánh và độ không chắc chắn
- Cung cấp N hữu hiệu **riêng từng metric** và phần trăm/tổng/mean; min-N, percentile implementation/tolerance do T-003 khóa, trước đó không công bố ranking. Có thể thêm CI nếu xác định sampling framework phù hợp; không tự gọi confidence interval trên toàn bộ census nguồn là sai số dân số Mỹ.
- Không tiến hành inference toàn quốc cho đến khi có sampling/coverage evidence.
- Chạy phân tích sensitivity: cohort stable carriers/airports across years; outlier policy (keep+flag vs filtered view); weather missingness nếu RQ-06 mở.

## Artifact requirements
Bảng curated + metadata metric; notebooks hoặc SQL trong source control; hình có alt labels/chú thích năm/phạm vi; kiểm chứng qua `TEST_PLAN` và `RESULTS_REGISTER`.
