# API_CONTRACTS — Chưa kích hoạt

**Status: NOT_APPLICABLE** vì mục tiêu hiện tại là pipeline phân tích, các bảng tổng hợp và báo cáo, không có yêu cầu làm backend API.

Không có endpoint nào được triển khai hoặc bảo đảm tồn tại. Nếu dashboard/API được phê duyệt bằng ADR, trước khi coding phải xác định: auth, endpoint/version, shape của dữ liệu, aggregation key, pagination/filter, metric version, provenance `run_id`, rounding policy, empty state, cache policy và contract tests.

**Nguyên tắc:** API không được tự tính lại KPI khác với `KPI_SPEC.md`, không gọi bảng năm 2016–2024 là toàn bộ thị trường, không để lộ raw data không cần thiết.
