# ROADMAP — Cổng triển khai và điều kiện chuyển giai đoạn

**Version:** docs-v1.1; thiết kế, không phải bằng chứng đã chạy Spark. `G0=DESIGN_BASELINE`; `G1=PARTIAL`; các G2–G7 chưa PASS. Một gate chỉ được `PASS` bằng bằng chứng và reviewer, không tự suy từ việc file Markdown đã có.

| Gate | Mục tiêu | Công việc/backlog | Exit criteria (tất cả bắt buộc trong phạm vi CORE) |
|---|---|---|---|
| G0 | Khóa hướng analysis-first | FP-DEC-001/002 và PRD | Phạm vi 2016–2024 mô tả đã được người dùng xác nhận; rubric nếu chưa có phải tiếp tục đánh dấu OPEN |
| G1 | Nắm nguồn dữ liệu và audit cấu trúc | 9 `schema_YYYY.json`, canonical, quality review | Structural evidence đã có; `PARTIAL` về semantic provenance/units/grain/time/weather, không coi raw production-ready |
| G2 | Khóa cohort, đơn vị, chỉ số và protocol | T-001..T-005 | T-001/002/003 có bằng chứng; đủ nguồn/đơn vị/sign và domain cho KPI-01..08; formula/denominator/percentile/min-N/cross-year coverage được duyệt; time-dependent derivation chỉ GO khi T-004 có evidence hoặc chính thức loại khỏi CORE; T-005 GO hoặc documented CONDITIONAL_NO_GO |
| G3 | Thiết kế pipeline, environment plan, test fixtures và recovery | T-006, ARCHITECTURE, TEST_PLAN | Architecture/dataflow/output schema/fixtures/commands dự kiến/rollback/resource plan được review; **chưa yêu cầu code ingestion** |
| G4 | Khởi tạo repo + viết ingestion/quality và kiểm thử ban đầu | **T-009 → T-007 → T-008** | Runtime/test runner/CI khởi tạo hoạt động; ingestion và QA synthetic tests chạy thật; không ghi raw; xác nhận lệnh chạy/commit (không tự coi setup docs là PASS) |
| G5 | Chạy smoke một năm/giới hạn và đối chiếu KPI | T-010 → T-011 | Reconciliation raw/accepted/quarantine/reject, **KPI-01..08 synthetic/smoke** (gồm submetric và percentile) theo TS-008, idempotence/fault rollback, benchmark, logs; chưa coi sample là full-run |
| G6 | Full processing 9 năm và phân tích | T-012 → T-013 → T-014; T-015 optional | 9 year manifests, quality & CORE KPI reconciled, RQ-01..05 có kết quả có bằng chứng, đặc biệt 2024; T-015 phải ghi GO+validated hoặc CONDITIONAL_NO_GO (không chặn G6) |
| G7 | Báo cáo, kiểm toán cuối và bàn giao | T-016 → T-017 | Mọi claim có RES-ID/source run/test, reproducibility & security checks, các giới hạn và rubric OPEN được nêu rõ |

## Quy tắc phụ thuộc
- G2 có thể chạy **kiểm toán bổ sung read-only** khi G1 còn `PARTIAL` nhờ bằng chứng cấu trúc. Không được giả G1 `PASS` hoặc đi tiếp vào code dùng KPI chưa khóa.
- G3 design cần G2 CORE được review. G4 code cần G3 design acceptance và G2 CORE. G5 cần G4; G6 cần G5; G7 cần G6.
- T-004 xử lý thời gian qua nửa đêm **không phải điều kiện để tính lại** các cột độ trễ/thời lượng có sẵn nếu đơn vị & domain của chúng đã qua G2; không suy ra timestamp đến từ `CRS_ARR_TIME`.
- T-005/T-015 weather là nhánh `Should/conditional`; nếu không có bằng chứng phải có quyết định `CONDITIONAL_NO_GO`, không tự mở Weather và không làm G2/G6 BLOCKED.
- Tình trạng G0 `DESIGN_BASELINE` không đồng nghĩa toàn bộ rubric hay công nghệ đã được giảng viên duyệt.

## Bằng chứng để chuyển gate
Ghi gate, trạng thái, task IDs, test IDs và số PASS/FAIL/SKIP, run manifest, source provenance, KPI version, git commit, người review, unresolved blockers/conditional NO-GO. `BLOCKED`/`NOT_RUN` không phải `PASS`. Giá trị chưa có evidence giữ nguyên `PENDING`.
