# RESULTS_REGISTER — Sổ cái kế hoạch và bằng chứng kết quả

**Version:** docs-v1.1. `NO_PRODUCTION_RESULTS`; tất cả dòng CORE bên dưới là **planned slots**, không phải phân tích đã chạy. Bảng audit G1 là baseline để đối chiếu, không được chép thành Spark output. RQ-01..05 đều phải có valid result trước G7.

| RES-ID | RQ / REQ | KPI | Dimension / purpose | Validation | Status |
|---|---|---|---|---|---|
| RES-001 | RQ-01 / REQ-03,05 | KPI-01 | year + counts provenance | TS-003/007/015 | PENDING |
| RES-002 | RQ-01 / REQ-03,05 | KPI-01 | year-month & source coverage notes | TS-007/015 | PENDING |
| RES-003 | RQ-02 / REQ-03,05 | KPI-02/03/06 | arrival year/month, signed+percentiles | TS-005/006/008/015 | PENDING |
| RES-004 | RQ-02 / REQ-03,05 | KPI-04/05 | departure year/month | TS-005/006/015 | PENDING |
| RES-005 | RQ-03 / REQ-03,05 | KPI-02/03/04/05 | carrier-year (N/min-N) | TS-007/016/015 | PENDING |
| RES-006 | RQ-03 / REQ-03,05 | KPI-02/03/04/05 | origin-year + dest-year (separate tables) | TS-007/016/015 | PENDING |
| RES-007 | RQ-03 / REQ-03,05 | KPI-02/03/04/05 | directed route-year | TS-007/016/015 | PENDING |
| RES-008 | RQ-04 / REQ-03,05 | KPI-01/02/03/04/05/06 | 2020 vs surrounding years + composition/sensitivity | TS-016/015 | PENDING |
| RES-009 | RQ-05 / REQ-03,05 | KPI-07 | taxi-out/in distributions or trends, separate N | TS-008/015 | PENDING |
| RES-010 | RQ-05 / REQ-03,05 | KPI-08 | air/actual/crs elapsed, separate N | TS-008/015 | PENDING |
| RES-011 | RQ-02/03 / REQ-03,05 | KPI-06 | P50/P90 with documented quantile method | TS-008/015 | PENDING |
| RES-012 | RQ-06 / REQ-06 | KPI-10 | Weather bins only if T-005/T-015 GO | TS-011/015 | CONDITIONAL_PENDING |

## Bắt buộc điền khi chạy thật
- `RES-ID`, câu hỏi/REQ/KPI version, output table/figure path, run manifest/commit/command/query, filters, cohort definition, field units/status, numerator/denominator, `count_records`, `count_metric_valid`, `excluded_count`, `metric_valid_rate`, `source_coverage_status`, min-N/quantile policy, measured result, validator and test evidence, caveat.
- Kết quả chưa qua kiểm chứng = `PENDING`/`INVALID`, không được `PASS` hoặc điền số liệu G1 vào như đã chạy Spark. Khi Weather `CONDITIONAL_NO_GO` thì RES-012 = `NOT_APPLICABLE` với ADR reference; không ảnh hưởng G6 CORE.
- KPI aggregation full theo 6 dimensions là deliverable T-013; các RES slot là **đầu ra phân tích tiêu biểu** chứ không thay thế nghĩa vụ tạo bảng đầy đủ. RQ-04 có RES-008 riêng.
