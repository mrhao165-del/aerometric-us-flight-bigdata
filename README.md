# Phân tích hiệu suất chuyến bay Hoa Kỳ 2016–2024

**Hồ sơ điều phối đồ án Big Data — bản docs-v1.1 (`2026-10-13`)**. Trọng tâm là **phân tích mô tả và so sánh hiệu suất hoạt động bay**, không phải mô hình dự báo.

## Điểm khởi đầu đã có bằng chứng
- 9 CSV Tabular, 34 trường/năm; báo cáo schema audit `0.1.0` thống kê tổng cộng **54,674,003 hàng** (chưa đồng nghĩa tổng chuyến bay thương mại của Hoa Kỳ).
- Có dữ liệu ngày, hãng khai thác, sân bay đi/đến, thời gian kế hoạch/thực tế, độ trễ, taxi, thời gian bay và sáu cột thời tiết.
- Không có cột `CANCELLED` hoặc `DIVERTED`. **Không tính tỷ lệ hủy/chuyển hướng** nếu chưa lấy nguồn dữ liệu khác có mẫu số đủ.
- Năm 2024 nằm trong phạm vi phân tích mô tả; chính sách ML holdout của Aeolus trước đây không điều khiển đồ án mới (xem `docs/02-design/DECISIONS.md`).
- Hiện **chưa có mã nguồn pipeline mới** trong gói này. Các lệnh PySpark, CI, dashboard và môi trường chạy là công việc triển khai về sau, không được ghi là đã vận hành.

## Bắt đầu từ đâu
1. Đọc `AGENTS.md`, `docs/00-governance/DOCUMENT_REGISTER.md`, `docs/04-execution/PROJECT_STATE.md`.
2. Đọc `docs/03-quality/G0_G1_REVIEW.md` và `docs/02-design/DECISIONS.md` trước khi dùng số liệu.
3. Khi triển khai pipeline, thực hiện `docs/01-planning/ROADMAP.md` và `docs/01-planning/BACKLOG.md`; G3 chỉ thiết kế, G4 khởi tạo T-009 trước khi viết ingestion T-007/quality T-008; ghi bằng chứng mỗi gate.
4. Công thức thống kê lấy từ `docs/02-design/KPI_SPEC.md`; hợp đồng hàng/mẫu số lấy từ `docs/02-design/DATA_CONTRACT.md` (DC-11/12); không đổi định nghĩa tùy ý. G2 chưa nghiệm thu 8 KPI CORE hoặc đơn vị đo.

## Cấu trúc
- Root: `README.md`, `AGENTS.md`.
- `docs/00-governance/`: danh mục, versioning và nguồn sự thật.
- `docs/01-planning/`: PRD, Roadmap, Backlog.
- `docs/02-design/`: Architecture, Data Dictionary, Data Contract, KPI, protocol, decisions, API (chưa kích hoạt).
- `docs/03-quality/`: test, risk, security, rollback, báo cáo rà soát G0–G1.
- `docs/04-execution/`: trạng thái, AI handoff, task template, deployment (chưa kích hoạt).
- `docs/03-quality/CHANGELOG.md`: lịch sử chỉnh sửa hồ sơ.
- `docs/05-evidence/`: báo cáo nguồn được sao chép nguyên dạng, provenance, dữ liệu kiểm toán, kết quả.

## Quy ước trạng thái
- `VERIFIED`: có bằng chứng trong tệp được cung cấp và trích nguồn rõ ràng.
- `USER_CONFIRMED`: người thực hiện đã chốt trực tiếp (phạm vi analysis-first).
- `PROPOSED`: giải pháp thiết kế đề nghị; chưa có bằng chứng vận hành/phê duyệt của giảng viên.
- `BLOCKED`: không được dùng để kết luận cho đến khi xử lý.
- `CONDITIONAL_PENDING` / `CONDITIONAL_NO_GO`: hạng mục không bắt buộc đang chờ GO/NO-GO / đã có quyết định không làm; không ngăn nghiệm thu CORE khi được documented.
- `NOT_APPLICABLE`: chưa cần (ví dụ backend API nếu không làm website).

## Tái lập (chưa triển khai)
Dữ liệu gốc không đóng gói vào ZIP. Khi có code phải công bố phiên bản Spark/Python, lệnh chạy, dataset hashes/manifest, seed nếu liên quan, pipeline version, KPI version và bằng chứng test. Không tuyên bố có kết quả Spark chỉ từ các báo cáo audit Pandas hiện có.

> Các tài liệu là đặc tả và hướng dẫn; không thay thế việc đọc dữ liệu lớn, chạy pipeline thực và kiểm chứng. Nếu tài liệu mâu thuẫn, dừng và theo thứ tự nguồn sự thật tại `DOCUMENT_REGISTER.md`.
