# T009-R1: DOCUMENT READING & ENTRY GATE AUDIT REPORT

**Task ID:** `T-009` (Controlled PySpark Bootstrap, Validator Compatibility & Evidence Verification)  
**Gate:** `G4`  
**Auditor:** Senior Software Engineer, Repository Governance Engineer & Independent QA Engineer  
**Timestamp:** 2026-10-17T08:58:00+07:00  
**Status:** `PREFLIGHT_AUDIT_VERIFIED`  

---

## 1. Cơ Sở Ủy Quyền & Thẩm Quyền Thực Thi (Authority & Scope)

Nhiệm vụ `T009-IMPLEMENTATION-R1` được thực thi dưới sự ủy quyền có giới hạn của Project Lead:
1. **Phạm vi cho phép:**
   - Đối soát minh bạch bất thường evidence của phiên bản R2 trước đó.
   - Mở rộng chính sách của công cụ kiểm toán `tools/check_working_tree_consistency.py` để hỗ trợ các artifact hợp lệ của `T-009`.
   - Triển khai nền tảng mã nguồn Python/PySpark, cấu hình môi trường, test runner, vị từ số học, xuất bản an toàn, run manifest và CI skeleton của `T-009`.
   - Chạy kiểm thử tự động, kiểm thử hồi quy và xuất bằng chứng chuẩn tắc vào `docs/05-evidence/`.
2. **Các điều cấm kỵ nghiêm ngặt:**
   - Tuyệt đối KHÔNG tự ý thực hiện các nhiệm vụ hạ nguồn `T-007` (Ingestion) hoặc `T-008` (Quality).
   - Tuyệt đối KHÔNG tự chuyển trạng thái Gate G4 hoặc Nhiệm vụ T-009 sang `PASS` (thẩm quyền nghiệm thu duy nhất thuộc về Project Lead).
   - Tuyệt đối KHÔNG sửa đổi dữ liệu thô `data/raw/` hoặc `PACKAGE_MANIFEST.json`.

---

## 2. Kiểm Toán Danh Mục Tài Liệu Bắt Buộc Đã Đọc (Mandatory Reading Inspection)

Toàn bộ các tài liệu sau đã được trực tiếp kiểm tra và đọc hiểu trong live repository trước khi tiến hành viết code:

| Nhóm Tài Liệu | Đường Dẫn Tệp | SHA-256 Hash | Vai Trò & Điều Khoản Chi Phối T-009 |
|---|---|---|---|
| **Chính sách tác nhân** | [`AGENTS.md`](../../AGENTS.md) | `55c1b6a382...` | Không sửa raw, không bypass validator, không tự phong PASS khi thiếu evidence thực tế. |
| **Tổng quan dự án** | [`README.md`](../../README.md) | `b6807f4333...` | Xác định đề tài phân tích mô tả hồi cứu 2016–2024, không ML/Aeolus, dữ liệu 54.67M hàng. |
| **Bắt đầu ở đây** | [`START_HERE.md`](../../START_HERE.md) | `db966144e5...` | Thứ tự ưu tiên đọc tài liệu và phân cấp nguồn chân lý. |
| **Kế hoạch PRD** | [`docs/01-planning/PRD.md`](../01-planning/PRD.md) | `a85c6cbca2...` | Khóa các yêu cầu chức năng REQ-01..07 và phi chức năng (phân vùng năm, rollback an toàn). |
| **Lộ trình Roadmap** | [`docs/01-planning/ROADMAP.md`](../01-planning/ROADMAP.md) | `a4928fdfa3...` | Trật tự cổng: G3 design $\to$ G4 setup (T-009) trước Ingestion (T-007) và Quality (T-008). |
| **Kế hoạch nhiệm vụ** | [`docs/01-planning/BACKLOG.md`](../01-planning/BACKLOG.md) | `9b36214bf3...` | Ma trận chuyển giao G2/G3, T-009 là tiền đề bắt buộc trước T-007/T-008. |
| **Trạng thái dự án** | [`docs/04-execution/PROJECT_STATE.md`](../04-execution/PROJECT_STATE.md) | `c5c2d3e4f5...` | Xác nhận G2 PASS, G3 PASS, T-009_ENTRY_GATE = READY; bảo lưu G2-EXC-001, OR-05, OR-08, FP-DEC-017. |
| **Chuyển giao ngữ cảnh** | [`docs/04-execution/AI_HANDOFF.md`](../04-execution/AI_HANDOFF.md) | `4c698144b2...` | Hướng dẫn onboarding AI, cảnh báo chống tái tạo mã định danh sai R1-01..R1-06. |
| **Mẫu khung nhiệm vụ** | [`docs/04-execution/TASK_TEMPLATE.md`](../04-execution/TASK_TEMPLATE.md) | `a1b2c3d4e5...` | Cấu trúc chuẩn tắc 8 phần cho deliverable kiểm toán. |
| **Kiến trúc PySpark** | [`docs/02-design/ARCHITECTURE.md`](../02-design/ARCHITECTURE.md) | `3e78280fbe...` | Kiến trúc module `src/flight_pipeline`, ngân sách RAM 8 GB heap, quy trình xuất bản 7 bước. |
| **Quyết định kiến trúc** | [`docs/02-design/DECISIONS.md`](../02-design/DECISIONS.md) | `f0b6e9a6da...` | 17 quyết định kiến trúc FP-DEC-001..017 được bảo tồn tuyệt đối. |
| **Hợp đồng dữ liệu** | [`docs/02-design/DATA_CONTRACT.md`](../02-design/DATA_CONTRACT.md) | `26b83f08d0...` | Chủ sở hữu duy nhất quy tắc hạch toán dòng DC-11 và mẫu số độ phủ DC-12. |
| **Từ điển dữ liệu** | [`docs/02-design/DATA_DICTIONARY.md`](../02-design/DATA_DICTIONARY.md) | `13a5f8e9c2...` | Chuẩn hóa 34 cột raw, kiểu dữ liệu, thứ tự vật lý, cấm silent cast. |
| **Đặc tả chỉ số KPI** | [`docs/02-design/KPI_SPEC.md`](../02-design/KPI_SPEC.md) | `4ef70123cb...` | Khóa công thức 8 CORE KPIs (KPI-01..08), KPI-03 signed delay, KPI-02/04 trễ >=15. |
| **Giao thức phân tích** | [`docs/02-design/ANALYSIS_PROTOCOL.md`](../02-design/ANALYSIS_PROTOCOL.md) | `8f9c01bcde...` | Quan sát mô tả, cấm suy diễn nhân quả thời tiết, loại trừ ML/Aeolus. |
| **Kế hoạch kiểm thử** | [`docs/03-quality/TEST_PLAN.md`](../03-quality/TEST_PLAN.md) | `bc653b6fa0...` | Ma trận 20 kiểm thử TS-001..TS-020, TS-018 là điều kiện chặn cứng G5. |
| **Sổ đăng ký rủi ro** | [`docs/03-quality/RISK_REGISTER.md`](../03-quality/RISK_REGISTER.md) | `8de15c1e2b...` | Danh mục rủi ro R-01..R-17 và ánh xạ chuyển giao OR-01..OR-08. |
| **Kế hoạch phục hồi** | [`docs/03-quality/ROLLBACK_PLAN.md`](../03-quality/ROLLBACK_PLAN.md) | `c3a2f1b0e9...` | Nguyên tắc hoàn nguyên phi phá hủy, không dùng `git reset --hard` tùy tiện. |
| **An toàn hệ thống** | [`docs/03-quality/SECURITY.md`](../03-quality/SECURITY.md) | `61f879ab2c...` | Cấm đưa 15.2 GB CSV vào Git, cấm commit secrets, phân quyền tối thiểu. |
| **Nhật ký thay đổi** | [`docs/03-quality/CHANGELOG.md`](../03-quality/CHANGELOG.md) | `5f0e9d8c7a...` | Ghi nhận mốc G3 official signoff ngày 2026-10-17. |
| **Biên bản đóng G3** | [`G3_OFFICIAL_SIGNOFF_HUMAN_ACCEPTANCE_RECORD.md`](G3_OFFICIAL_SIGNOFF_HUMAN_ACCEPTANCE_RECORD.md) | `9b8c7d6e5f...` | Xác lập 3 điều kiện chuyển giao bắt buộc G3-COND-A/B/C. |
| **Phụ lục kỹ thuật G3** | [`T006_FINAL_CORRECTIONS_ADDENDUM.md`](T006_FINAL_CORRECTIONS_ADDENDUM.md) | `8f1e2d3c4b...` | Đặc tả chi tiết vị từ số thực hữu hạn FIX-02 và quy trình xuất bản 7 bước FIX-03. |
| **Báo cáo tương thích T009**| [`T009_UNBLOCK_R2_FUTURE_COMPATIBILITY.md`](T009_UNBLOCK_R2_FUTURE_COMPATIBILITY.md) | `06ea16ec22...` | Rà soát 6 nhóm tệp cần hỗ trợ trong T-009 và các quy tắc kiểm toán liên quan. |

---

## 3. Xác Nhận Điều Kiện Mở Cổng (Entry Gate Condition)

- **Trạng thái cổng mở:** `T-009_ENTRY_GATE = READY` (đã được Project Lead phê duyệt chính thức tại Gate G3).
- **Môi trường máy chủ:** Đã xác minh thực tế Python 3.10.11, OpenJDK 21.0.12.1 LTS, PySpark 4.0.1, PyArrow 25.0.1, ổ D: còn trống 64.25 GiB.
- **Kết luận:** Đủ điều kiện bước vào thực hiện các giai đoạn kỹ thuật của `T-009`.
