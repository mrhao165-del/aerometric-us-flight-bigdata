# DOCS_CONSISTENCY_AUDIT — Báo cáo khắc phục đồng bộ docs-v1.1

**Ngày:** 2026-10-13. **Phạm vi:** Kiểm toán **tài liệu và file đóng gói**, không chạy Spark, không đọc lại raw CSV. Kiểm toán gốc: `docs/00-governance/V1_0_CONSISTENCY_AUDIT.md`.

## Kết quả xử lý 11 phát hiện v1.0

| ID | Kết quả | Bằng chứng sửa / owner |
|---|---|---|
| F-01 | FIXED_IN_DOCS | `ROADMAP.md` G3 design, G4 T-009→T-007→T-008; `BACKLOG.md`, `PROJECT_STATE.md`, `TEST_PLAN.md` đồng bộ |
| F-02 | FIXED_IN_DOCS | `BACKLOG.md` T-003 = review KPI-01..08 (8 CORE), PRD RQ-01..05 vẫn Must |
| F-03 | FIXED_IN_DOCS | `DATA_CONTRACT.md` DC-11/12 định nghĩa raw/accepted/quarantine/reject, per-metric eligibility và `metric_valid_rate`; `KPI_SPEC.md`, `TEST_PLAN.md` TS-017 |
| F-04 | FIXED_IN_DOCS | `BACKLOG.md` T-003 phải xác nhận 7 numeric units/sign/domain; `KPI_SPEC`, `TEST_PLAN` TS-018, G2 requirement |
| F-05 | FIXED_IN_DOCS | Weather T-005/T-015 = CONDITIONAL_PENDING, cần GO hoặc documented CONDITIONAL_NO_GO; không cản CORE G2/G6 |
| F-06 | FIXED_IN_DOCS | `RESULTS_REGISTER` có RES-001..012 bao trùm RQ-01..05 + RQ-06 conditional; register có ma trận toàn chuỗi |
| F-07 | FIXED_IN_DOCS | Raw source size/mtime chỉ metadata, có `METADATA_MATCH_ONLY`/`IDENTITY_UNVERIFIED`; `DATA_PROVENANCE`, TS-019 |
| F-08 | FIXED_IN_DOCS | `DOCUMENT_REGISTER` tách applicability test trước precedence; historical ML rules không áp cho retrospective |
| F-09 | FIXED_IN_DOCS | `AI_HANDOFF.md` trong document owner register, thay HANDOFF.md không tồn tại |
| F-10 | FIXED_IN_DOCS | `README.md` đưa `CHANGELOG.md` về `docs/03-quality/` |
| F-11 | FIXED_IN_DOCS | `ROLLBACK_PLAN.md` dùng TS-013 |

## Các kiểm tra bổ sung so với 11 lỗi

- Q-01 lineage: không mặc định Spark `source_row_number` ổn định, thêm TS-020.
- Q-02 disjoint row quality: DC-11 và fixture accepted/quarantine/rejected + TS-003/017.
- Q-03 P50/P90: method/tolerance vẫn là **quyết định G2 chưa phê duyệt**, TS-008 không gắn PASS giả.
- Q-04 min-N: chưa có ngưỡng được duyệt, không ranking trước T-003.
- Q-05 G1 `PARTIAL` nhưng G2 cho phép read-only audit, gate G3/G4 không được vượt G2.
- Q-06 record count không đồng nhất population flights: `count_records` accepted, source coverage có evidence status.
- Q-07 QA: có script kiểm tra tài liệu `tools/check_docs_consistency.py`; automated tests **không thay** nghiệp vụ review thủ công.
- Q-08 Review bổ sung: KPI-09 được gọi chính xác là mean positive-part trên tất cả records hợp lệ; T-011 kiểm thử đủ 8 CORE KPI tại G5 qua TS-008 synthetic, còn phân tích G6 phải chạy trên dữ liệu đầy đủ.

## Kết quả kiểm chứng và phạm vi tuyên bố

- **DOCS FIXED:** không còn phát hiện F-01..F-11 chưa được xử lý trong authored docs theo checklist trên.
- **STRUCTURE VERIFIED:** 18 file A/B/C; 8 supplementary; task/gate/ID coverage; file paths; 13 source snapshots SHA-256 match; JSON count/column audit; không có production results giả.
- **NO RAW/PIPELINE VERIFICATION:** chưa có 9 raw CSV trong ZIP, chưa chạy Spark, chưa kiểm chứng flight event grain, business representativeness, 7 measure units, source weather join, 2024 full date rollover. Các mục này vẫn là **blockers được trình bày đúng**, không phải lỗi đồng bộ tài liệu đã được chứng minh.
- **Release decision:** `DOCS_CONSISTENCY_PASS` trong phạm vi **static/documentary checks** sau khi script và post-ZIP integrity đều PASS; không phải `G2_PASS`, `DATA_READY`, `PIPELINE_PASS` hay cam kết có thể loại trừ tất cả sai sót chưa biết.

## Cách tự kiểm chứng

```bash
python tools/check_docs_consistency.py
```

Sau khi ZIP được phát hành, kiểm bằng cách giải nén vào thư mục sạch, chạy script trên bản giải nén, so `PACKAGE_MANIFEST.json`, đối chiếu SHA-256 của `docs/05-evidence/inputs/` với `SOURCE_MANIFEST.json`, và chạy `unzip -t`.
