# BUILD_QA_REPORT — Kiểm tra hồ sơ docs-v1.1

**Ngày:** 2026-10-13; phạm vi duy nhất là **tài liệu đã soạn và source audits đính kèm**. Không chạy Spark, không đọc CSV raw; mọi `PASS` dưới đây là PASS cho kiểm tra file/logic static được mô tả, không phải nghiệm thu G2..G7.

## Vòng 1: Đối chiếu nguồn và cấu trúc
- Kiểm tra 9/9 JSON parse hợp lệ, `is_complete=true`, 34 cột nhất quán; tổng 54.674.003 records và 10.116.916 source rows với `ARR_DELAY >= 15`.
- Đối chiếu 13 file nguồn immutable bằng SHA-256 `SOURCE_MANIFEST.json`; không giả đây là raw SHA-256.
- Kiểm kê 18 file A/B/C và 8 supplementary, file điều phối/QA và script.

## Vòng 2: Consistency giữa tài liệu
- Kiểm tra gate–task dependencies không tạo vòng lặp; G3 chỉ design và T-009 trước T-007/T-008 trong G4.
- Kiểm tra KPI-01..08 CORE, 7 trường cần xác nhận đơn vị trước G2; DC-11/12 mẫu số & zero denominator; KPI-09 mean positive-part không nhầm thành mean có điều kiện, và TS-008 đã có cả G5 synthetic/G6 full.
- Kiểm tra all RQ-01..06 / result slots, TS catalog, bộ policy Weather conditional và phân xử evidence Aeolus lịch sử.
- Kiểm tra đường dẫn `docs/...`, `AI_HANDOFF.md`, `CHANGELOG.md`, `TS-013`.

## Vòng 3: ZIP/package release
- Chạy `tools/check_docs_consistency.py` **trên bản ZIP đã giải nén** và `zipfile.testzip()` CRC.
- Đối chiếu toàn bộ các file trong `PACKAGE_MANIFEST.json` theo SHA-256/size; kiểm tra danh sách ZIP chính xác bằng manifest, không thừa file và không thiếu source.
- Ghi kết quả thực tế ở kiểm toán/phản hồi khi phát hành. Script chỉ chứng minh consistency có thể kiểm được, không chứng minh semantic provenance còn OPEN.

**Evidence:** `docs/00-governance/DOCS_CONSISTENCY_AUDIT_v1.1.md`, `tools/check_docs_consistency.py`, `PACKAGE_MANIFEST.json`, `docs/05-evidence/inputs/SOURCE_MANIFEST.json`.
