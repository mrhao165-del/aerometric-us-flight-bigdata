# Bắt đầu ở đây — Bộ hồ sơ đồ án

**Scope:** Phân tích hiệu suất các chuyến bay Hoa Kỳ 2016–2024. **Version:** docs-v1.1 — 2026-10-13.

## Nội dung
- **Nhóm A:** 6 file — yêu cầu, roadmap, kiến trúc, quy tắc AI, backlog và README.
- **Nhóm B:** 6 file — test plan, rủi ro, decisions, changelog, rollback và security.
- **Nhóm C:** 6 file — trạng thái, AI handoff, task template, API conditional, data dictionary và deployment.
- **8 tài liệu chuyên ngành/điều phối:** DATA_CONTRACT, KPI_SPEC, ANALYSIS_PROTOCOL, DATA_PROVENANCE, DATA_QUALITY_REPORT, RESULTS_REGISTER, G0_G1_REVIEW, DOCUMENT_REGISTER.
- **13 báo cáo source nguyên gốc + manifest SHA-256** trong `docs/05-evidence/inputs/`.

## Đọc theo trình tự
1. `docs/03-quality/G0_G1_REVIEW.md` — những gì có bằng chứng và blocker.
2. `docs/02-design/DECISIONS.md` — xác nhận phạm vi mô tả.
3. `docs/01-planning/PRD.md` + `docs/01-planning/ROADMAP.md`.
4. `docs/02-design/DATA_CONTRACT.md` + `KPI_SPEC.md` + `ANALYSIS_PROTOCOL.md`.
5. `AGENTS.md` + `docs/04-execution/PROJECT_STATE.md` + `BACKLOG.md` để bắt đầu giao việc.

## Ngay lúc này
- **G0:** Scope đã xác nhận; docs chính thức về mặt hướng phân tích, một số công nghệ vẫn proposed.
- **G1:** PARTIAL: schema audit đầy đủ, còn thiếu semantic data provenance/flight grain/weather/time rollover.
- **G2:** có đặc tả draft nhưng **chưa duyệt 8 KPI CORE/đơn vị đo**; G3–G7 chưa nghiệm thu thực nghiệm.
- **Không chứa raw CSV/Flight Chain `.pt` hoặc code Spark**. Không coi bộ tài liệu như pipeline đã chạy.

## Phân công AI phù hợp
Dùng `docs/04-execution/TASK_TEMPLATE.md` và giao T-001 trước; yêu cầu audit nhỏ, chỉ đọc, chứng minh provenance/coverage. Sau T-002, T-003 phải kiểm chứng đơn vị và khóa cả KPI-01..08 trước khi G2 PASS. Không giao “viết toàn bộ ETL + chart + thesis trong một lần” khi G2 chưa xong.

## Ghép vào repository hiện có
Nếu dự án đã có `AGENTS.md`, `README.md` hoặc `docs/` với nội dung đang hoạt động, **không ghi đè trực tiếp**. Tạo branch mới, diff nội dung, hợp nhất những quyết định đã được duyệt và cập nhật `PROJECT_STATE.md` theo repo thực tế.
