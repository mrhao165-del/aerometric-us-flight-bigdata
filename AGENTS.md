# AGENTS.md — Chính sách cho AI Agent

**Scope:** toàn repository đồ án phân tích hiệu suất bay Hoa Kỳ 2016–2024. Phiên bản docs-v1.1; ưu tiên cao với AI Agent nhưng không thay thế quyền truy cập filesystem và kiểm soát Git thực tế.

## Trước mọi task
1. Đọc `README.md`, `docs/04-execution/PROJECT_STATE.md`, `docs/01-planning/BACKLOG.md` và quyết định liên quan trong `docs/02-design/DECISIONS.md`.
2. Đọc đúng `DATA_CONTRACT.md`, `KPI_SPEC.md`, `TEST_PLAN.md` khi xử lý dữ liệu/KPI. Nếu file không có, báo blocker; không tự chế quy tắc.
3. Ghi rõ input, output, file được phép sửa, các bằng chứng hiện hữu, các giả định chưa chứng minh; trình bày plan thay đổi nhỏ.
4. Không dùng các yêu cầu dự báo T-2h/ATL của Aeolus lịch sử làm quy tắc cho đồ án mô tả; xem `ANALYSIS_PROTOCOL.md`.

## Những điều cấm
- **Không sửa/ghi đè `data/raw/`, nguồn JSON/MD audit, bản gốc ở `docs/05-evidence/inputs/`.**
- Không giả mạo việc đã đọc 54,7 triệu hàng hoặc đã chạy Spark nếu chỉ đọc metadata audit.
- Không gọi row count là “tổng chuyến bay thực tế của Mỹ”; chỉ gọi “số hàng trong dataset đã audit”. Không lập KPI canceled/diverted vì thiếu trường.
- Không suy ra nguyên nhân từ tương quan thời tiết; không chốt đơn vị Celsius/mm/kmh khi chưa xác minh nguồn.
- Không suy ra ngày đến thực tế chỉ từ date component của `CRS_ARR_TIME`; không tự động cộng 24h để “sửa” rollover.
- Không tự nạp `.pt` qua `torch.load` không có chứng thực; Flight Chain và ML đều **ngoài phạm vi chính**.
- Không xóa dữ liệu, force push, reset hard trên branch có thay đổi chưa backup, chạy SQL/Spark overwrite vào dữ liệu gốc, hay thay đổi định nghĩa KPI mà chưa có decision review.
- Không đưa secrets, dữ liệu thô cỡ lớn hoặc generated outputs vào Git.
- Không nói `PASS` khi không có output lệnh, manifest hoặc test phù hợp.

## Quy trình bắt buộc
- Một task / một branch hoặc commit theo phạm vi; lấy trạng thái Git và chỉ sửa file được yêu cầu.
- Đối với pipeline: test unit trên dữ liệu giả lập → smoke một phần dữ liệu thật → đối chiếu năm → full run; ghi rõ giới hạn sample.
- Artifact đầu ra là immutable/run-id; chỉ cập nhật con trỏ `latest` sau khi xác minh thành công.
- Nếu phát hiện bất đồng giữa sources, tạo issue/tài liệu decision với trạng thái `BLOCKED` thay vì im lặng sửa số liệu.
- Kết thúc: liệt kê thay đổi, lệnh chạy và exit code, kết quả pass/fail/skip, vấn đề tồn đọng, tác động KPI, commit, rollback target và đề nghị nhiệm vụ kế.
- Chỉ cập nhật `PROJECT_STATE.md` sau khi có bằng chứng; không sửa các phần historical audit.
- Tuân DC-11/12: `accepted`, `quarantined`, `rejected` mutually exclusive; không viết `coverage_rate` chung chung hoặc nhầm metric valid rate với mức bao phủ thị trường.
- G2 phải được review và đủ bằng chứng units cho 7 measures trước khi lập code production CORE; G3 thiết kế, G4 **T-009 setup trước T-007/008**.
- Với Weather optional: dùng `CONDITIONAL_PENDING` hoặc `CONDITIONAL_NO_GO` có quyết định; không chặn các gate CORE chỉ vì nhánh optional chưa GO.
- `source_signature` size/mtime không chứng minh raw content identity; không tự biến đổi mtime mismatch thành chắc chắn file lỗi hay metadata match thành hash verified.

## Định nghĩa hoàn thành (DoD)
Task đạt khi acceptance criteria trong `docs/01-planning/BACKLOG.md` được kiểm chứng, kiểm thử bắt buộc hoàn tất, rủi ro mới được cập nhật và không có sai khác không giải thích. Task chỉ biên soạn tài liệu có thể nghiệm thu mà không cần full pipeline nhưng phải mang nhãn `design/documentation only`.
