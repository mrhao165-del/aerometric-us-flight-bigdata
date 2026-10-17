# DOCUMENT_REGISTER — Quản trị tài liệu, áp dụng nguồn & truy vết

**Version:** docs-v1.1 (2026-10-13). Phạm vi: đồ án Big Data **phân tích mô tả** hiệu suất bay tại Hoa Kỳ 2016–2024, không phải Aeolus ATL prediction. 18 file A/B/C + 8 tài liệu miền/quản trị + BUILD_QA_REPORT/START_HERE/manifests + snapshot nguồn bất biến.

## Hai bước phân xử — tránh áp sai policy lịch sử
1. **Applicability test:** câu nào là fact được kiểm toán, câu nào là quyết định quy trình; xác định dataset (raw vs processed vs ATL subset), thời gian, và nhiệm vụ (retrospective vs pre-flight ML) của nguồn. Giữ factual evidence của audit, nhưng **không lấy chính sách ML cũ** (`2024 sealed`, `T-2h`, `drop actual operations`) làm rule của đồ án mới.
2. **Sau khi xác định cùng phạm vi áp dụng:** (a) user/rubric thực được cung cấp cho scope; (b) evidence facts từ source snapshots; (c) `DECISIONS.md` ADR đã được duyệt, `PRD.md` scope; (d) owners: `DATA_CONTRACT.md` row/validity, `KPI_SPEC.md` metric, `ANALYSIS_PROTOCOL.md` claims, `ARCHITECTURE.md` design, `TEST_PLAN.md` verification, `ROADMAP.md` gate; (e) `BACKLOG.md` task, `PROJECT_STATE.md` progress, `AI_HANDOFF.md` summary. Khi có xung đột **cùng scope**, ghi BLOCKED/ADR, không tự chọn nội dung tiện lợi.

## Owners (mỗi ý một nơi chính thức)
| Group | Files | Owner of |
|---|---|---|
| A | `README.md`, `AGENTS.md`, `docs/01-planning/PRD.md`, `docs/01-planning/ROADMAP.md`, `docs/01-planning/BACKLOG.md`, `docs/02-design/ARCHITECTURE.md` | Hướng dẫn, rules AI, scope RQ/REQ, gates, task, system design |
| B | `docs/03-quality/TEST_PLAN.md`, `docs/03-quality/RISK_REGISTER.md`, `docs/02-design/DECISIONS.md`, `docs/03-quality/CHANGELOG.md`, `docs/03-quality/ROLLBACK_PLAN.md`, `docs/03-quality/SECURITY.md` | Tests, risks, decisions, changes, recovery, security |
| C | `docs/04-execution/PROJECT_STATE.md`, `docs/04-execution/AI_HANDOFF.md`, `docs/04-execution/TASK_TEMPLATE.md`, `docs/02-design/API_CONTRACTS.md`, `docs/02-design/DATA_DICTIONARY.md`, `docs/04-execution/DEPLOYMENT.md` | Actual gate state, agent transfer, task contract, optional API, raw schema, deployment |
| Supplementary (8) | `docs/02-design/DATA_CONTRACT.md`, `docs/02-design/KPI_SPEC.md`, `docs/02-design/ANALYSIS_PROTOCOL.md`, `docs/05-evidence/DATA_PROVENANCE.md`, `docs/05-evidence/DATA_QUALITY_REPORT.md`, `docs/05-evidence/RESULTS_REGISTER.md`, `docs/03-quality/G0_G1_REVIEW.md`, `docs/00-governance/DOCUMENT_REGISTER.md` | Accounting, KPIs, method, provenance, source facts, results, G0–G1 audit, doc precedence |

`docs/00-governance/BUILD_QA_REPORT.md`, `docs/00-governance/V1_0_CONSISTENCY_AUDIT.md` và `docs/00-governance/DOCS_CONSISTENCY_AUDIT_v1.1.md` là **hồ sơ QA của chính bộ tài liệu**, không nằm trong 8 supplementary. `START_HERE.md` là trang điều hướng.

## ID standards
- `RQ-01..06` (RQ-06 conditional); `REQ-01..08` (REQ-06 conditional, REQ-08 Could); `FP-DEC-001..`; `DC-01..12`; `KPI-01..12`; `T-001..017`; `TS-001..020`; `R-01..`; `RES-001..012`.
- Task IDs giữ nguyên so với v1.0 để không phá liên kết; **thứ tự phụ thuộc T-009 trước T-007/T-008** theo gate G4.
- States: `USER_CONFIRMED`, `PROPOSED`, `VERIFIED_SOURCE`, `NOT_RUN`, `TODO`, `PARTIAL`, `BLOCKED`, `CONDITIONAL_PENDING`, `CONDITIONAL_NO_GO`, `NOT_APPLICABLE`, `PASS` khi có evidence. `CONDITIONAL_NO_GO` không phải thực thi PASS, phải có quyết định/hồ sơ lý do.
- Evidence snapshots: `docs/05-evidence/inputs/` (13 file MD/JSON nguyên bytes) + `SOURCE_MANIFEST.json`; hash source ở đây **không** là SHA256 raw CSV.

## Ma trận RQ → REQ → KPI → Task → Test → Result (expected, chưa nghiệm thu)
| RQ | REQ | KPI | Tasks chính | Tests thiết yếu | Planned RES |
|---|---|---|---|---|---|
| RQ-01 | REQ-01/02/03/04/05/07 | KPI-01 | T-001/002/003/007/008/010/012/013/014 | TS-001/003/004/007/015/017 | RES-001/002 |
| RQ-02 | REQ-03/04/05/07 | KPI-02/03/04/05/06 | T-003/011/013/014 | TS-005/006/008/015/017/018 | RES-003/004/011 |
| RQ-03 | REQ-03/04/05 | KPI-02/03/04/05/06 | T-001/002/003/013/014 | TS-007/008/015/016 | RES-005/006/007/011 |
| RQ-04 | REQ-03/04/05 | KPI-01/02/03/04/05/06 | T-001/013/014 | TS-007/015/016 | RES-008 |
| RQ-05 | REQ-03/04/05 | KPI-07/08 | T-003/011/013/014 | TS-006/008/015/018 | RES-009/010 |
| RQ-06 (optional) | REQ-06 | KPI-10 | T-005/015 | TS-011 | RES-012 (GO hoặc N/A với ADR) |

REQ-08 dashboard/API = `COULD/NOT_APPLICABLE` theo PRD/API_CONTRACTS, không được đẩy vào gate CORE. REQ-07 reproducibility là yêu cầu ngang xuyên suốt, kiểm TS-012/013/014/019/020. `T-016/017` và TS-015 áp dụng tất cả RQ CORE.

## Trình tự sửa
- Sửa owner document rồi đối chiếu ma trận downstream (REQ/KPI/T/TS/RES), cập nhật ADR nếu scope hoặc công thức đổi, ghi CHANGELOG.
- Không sửa `docs/05-evidence/inputs/` hoặc hash source cũ; không sửa nguồn lịch sử để làm mâu thuẫn biến mất.
- Cập nhật `PROJECT_STATE.md` bằng evidence thực tế, không nâng trạng thái gate chỉ vì đã chỉnh tài liệu. Chạy QA report/checklist và kiểm tra manifest khi phát hành ZIP.
