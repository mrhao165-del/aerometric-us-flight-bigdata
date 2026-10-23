"""
Update governance documents for T-014 V4 Signoff Blocker Correction.
Updates PROJECT_STATE.md, CHANGELOG.md, BACKLOG.md, and AI_HANDOFF.md with UTF-8 encoding.
"""

import os
import sys

def update_project_state():
    p = "docs/04-execution/PROJECT_STATE.md"
    with open(p, "r", encoding="utf-8") as f:
        text = f.read()

    # 1. Update line 3 (Updated header)
    old_updated_prefix = "**Updated:** 2026-10-22 (Nghiệm thu Đóng Kỹ thuật Cuối cùng V3 Nhiệm vụ T-014:"
    new_updated = (
        "**Updated:** 2026-10-22 (Nghiệm thu Khắc phục Toàn bộ Điểm nghẽn Kiểm toán Cuối cùng V4 Nhiệm vụ T-014 "
        "[T014_SIGNOFF_BLOCKERS_RESOLVED_READY_FOR_HUMAN_SIGNOFF]: Giải quyết triệt để 4 điểm nghẽn Blockers A, B, C, D; "
        "Blocker A: ma trận kiểm chứng ngữ nghĩa biểu đồ 5/5 TRUE, 16/16 biểu đồ xác thực động; Blocker B: đối soát "
        "chuẩn xác năm 2019 và bổ sung cột year tường minh cho tuyến bay đối ứng ORD <-> LGA 31.42% vs 28.60%, chênh lệch "
        "2.82%, tổng mẫu 28,277; Blocker C: thu thập nhật ký kiểm thử thô thực tế đầy đủ từ pytest và QA independent "
        "audit tại T014_AUTHENTIC_TEST_AND_AUDIT_LOG.txt; Blocker D: đối soát và đính chính mã băm vật lý gói niêm phong "
        "V3 [4,219,816 bytes, SHA-256 2e522cddb01333836c10f091fb5ad7abc0cc36b77c250a2f27cd16b1b40bfc7c, CRC-32 e07cc024, "
        "65 files]; xuất bản t014_analysis_2016_2024_v4 tại data/analytics/runs/; con trỏ data/analytics/latest_run_id.txt "
        "trỏ t014_analysis_2016_2024_v4; 29/29 unit tests PASS [kèm 12 negative tests]; 91/91 QA audit checks PASS; "
        "gói niêm phong V4 T014_FINAL_REVIEW.zip [4,182,327 bytes, SHA-256 8dbdbb23e42c35b5463f28328761bf7019fce79f83a48e780dc9a0f026a798f0, "
        "CRC-32 1f4055f9, 70 files]; Gate G6 tiếp tục IN_PROGRESS [T012_T013_SIGNED_OFF, "
        "T014_SIGNOFF_BLOCKERS_RESOLVED_READY_FOR_HUMAN_SIGNOFF]; Quyết định D5 fail-closed NOT_AUTHORIZED; T-014 sẵn sàng "
        "cho Project Lead phê duyệt nghiệm thu chính thức)."
    )

    lines = text.splitlines()
    for i, line in enumerate(lines):
        if line.startswith(old_updated_prefix):
            lines[i] = new_updated
            break

    text = "\n".join(lines)

    # 2. Update Bản chất tài liệu
    text = text.replace(
        "hoàn tất đóng kiểm toán kỹ thuật cuối cùng T-014 V3 (t014_analysis_2016_2024_v3, con trỏ analytics latest trỏ t014_analysis_2016_2024_v3)",
        "hoàn tất khắc phục điểm nghẽn kiểm toán cuối cùng T-014 V4 (t014_analysis_2016_2024_v4, con trỏ analytics latest trỏ t014_analysis_2016_2024_v4)"
    )

    # 3. Update summary header G6 status
    text = text.replace(
        "Gate G6 = IN_PROGRESS (T012_T013_SIGNED_OFF, T014_FINAL_READY_FOR_HUMAN_SIGNOFF)",
        "Gate G6 = IN_PROGRESS (T012_T013_SIGNED_OFF, T014_SIGNOFF_BLOCKERS_RESOLVED_READY_FOR_HUMAN_SIGNOFF)"
    )

    # 4. Update Table 1 G6 row
    old_g6_row = "| G6 | IN_PROGRESS (T012_T013_SIGNED_OFF, T014_FINAL_READY_FOR_HUMAN_SIGNOFF) |"
    new_g6_row = "| G6 | IN_PROGRESS (T012_T013_SIGNED_OFF, T014_SIGNOFF_BLOCKERS_RESOLVED_READY_FOR_HUMAN_SIGNOFF) |"
    text = text.replace(old_g6_row, new_g6_row)

    # 5. Update Table 2 T-014 row
    old_t014_row_part = "| **T-014 (Phân tích Mô tả, Trực quan hóa & Tổng hợp Khoa học 2016–2024)** | **T014_FINAL_READY_FOR_HUMAN_SIGNOFF** |"
    new_t014_row_part = "| **T-014 (Phân tích Mô tả, Trực quan hóa & Tổng hợp Khoa học 2016–2024)** | **T014_SIGNOFF_BLOCKERS_RESOLVED_READY_FOR_HUMAN_SIGNOFF** |"
    text = text.replace(old_t014_row_part, new_t014_row_part)

    # 6. Correct Section 5 item 8 V3 hash and add item 9
    old_item_8_hash = "T014_FINAL_REVIEW.zip (4,218,758 bytes, SHA-256 aba67279e0cea0f185f3777de791b9435aa49a588213f53240f057515fef5244, 65 files)"
    corrected_item_8_hash = "T014_FINAL_REVIEW.zip (4,219,816 bytes, SHA-256 2e522cddb01333836c10f091fb5ad7abc0cc36b77c250a2f27cd16b1b40bfc7c, CRC-32 e07cc024, 65 member files; superseding earlier draft transcription discrepancy aba67279e0...)"
    text = text.replace(old_item_8_hash, corrected_item_8_hash)

    # Add item 9 before Section 6
    item_9_text = (
        "\n9. **Nhiệm vụ T-014 (Gate G6) — Hoàn tất Khắc phục Toàn bộ Điểm nghẽn Kiểm toán Cuối cùng V4 (T014_SIGNOFF_BLOCKERS_RESOLVED_READY_FOR_HUMAN_SIGNOFF):** "
        "Đã giải quyết dứt điểm 4 điểm nghẽn kỹ thuật (Blockers A, B, C, D) từ bản V3 theo chỉ thị độc lập: "
        "(1) **Blocker A (Semantic Checks):** Khắc phục lỗi so sánh chuỗi định danh biểu đồ; 5/5 kiểm tra ngữ nghĩa đạt TRUE (16/16 biểu đồ xác thực động, liên kết RES/KPI/bảng tham chiếu/nhóm chiều hợp lệ, cơ chế fail-closed chặt chẽ). "
        "(2) **Blocker B (Route Analysis Year & Rates):** Phép biến đổi tuyến đối ứng xác định chuẩn xác cho Năm 2019; bổ sung cột year: 2019 tường minh vào bảng rq03_directed_routes (cả CSV và Parquet). Đối soát chuẩn xác cặp tuyến Chicago — New York (ORD <-> LGA): chiều ORD->LGA trễ 31.4219% (14,108 chuyến), chiều LGA->ORD trễ 28.5976% (14,169 chuyến), chênh lệch 2.8242% (làm tròn 2.82%), tổng sản lượng 28,277 chuyến bay. Đã đồng bộ 100% số liệu trên Báo cáo, Sổ đăng ký kết quả (RES-011) và biểu đồ CHART_RQ03_04. "
        "(3) **Blocker C (Authentic Test Evidence):** Thu thập nhật ký thực thi thực tế thô từ lệnh shell pytest (29/29 tests PASS) và kịch bản kiểm toán QA độc lập (91/91 checks PASS), ghi nhận đầy đủ lệnh shell, môi trường, thời lượng, stdout, stderr, Exit Code 0 tại T014_AUTHENTIC_TEST_AND_AUDIT_LOG.txt. "
        "(4) **Blocker D (Documentary Hash Reconciliation):** Đối soát và đính chính các tham chiếu mã băm tài liệu lịch sử V3 [4,219,816 bytes, SHA-256 2e522cddb01333836c10f091fb5ad7abc0cc36b77c250a2f27cd16b1b40bfc7c, CRC-32 e07cc024, 65 member files], đồng thời xác lập thông số niêm phong V4 mới nhất. "
        "Xuất bản run chính thức t014_analysis_2016_2024_v4 tại data/analytics/runs/ và cập nhật con trỏ data/analytics/latest_run_id.txt trỏ t014_analysis_2016_2024_v4. "
        "Bộ tài liệu niêm phong nghiệm thu V4 được đóng gói tại D:\\Flight_Audit_Exports\\T014_FULL_ANALYTICS\\signoff_blocker_closeout\\: "
        "T014_FINAL_REVIEW.zip (4,182,327 bytes, SHA-256 8dbdbb23e42c35b5463f28328761bf7019fce79f83a48e780dc9a0f026a798f0, CRC-32 1f4055f9, 70 member files); "
        "7 tài liệu bàn giao bắt buộc: T014_SIGNOFF_BLOCKER_CORRECTION_REPORT.md, T014_CORRECTED_CHART_SEMANTIC_VERIFICATION.json, T014_ROUTE_YEAR_NUMERICAL_RECONCILIATION.json, T014_AUTHENTIC_TEST_AND_AUDIT_LOG.txt, T014_BLOCKER_FIX_CHANGES.patch, T014_FINAL_REVIEW.zip, T014_FINAL_REVIEW_MANIFEST.json. "
        "Kiểm thử: 29/29 tests PASS (tests/test_t014_analytics_comprehensive.py bao gồm 12 negative tests) và 91/91 checks PASS (tools/qa/run_t014_independent_audit.py). "
        "Quyết định D5 duy trì fail-closed NOT_AUTHORIZED. Cổng Gate G6 duy trì trạng thái IN_PROGRESS (T012_T013_SIGNED_OFF, T014_SIGNOFF_BLOCKERS_RESOLVED_READY_FOR_HUMAN_SIGNOFF). Sẵn sàng cho Project Lead xem xét và ban hành quyết định nghiệm thu chính thức T-014."
    )

    if "## 6. Runtime Fields to Populate Only When True" in text and "9. **Nhiệm vụ T-014 (Gate G6) — Hoàn tất Khắc phục Toàn bộ Điểm nghẽn Kiểm toán Cuối cùng V4" not in text:
        text = text.replace(
            "\n## 6. Runtime Fields to Populate Only When True",
            item_9_text + "\n\n## 6. Runtime Fields to Populate Only When True"
        )

    with open(p, "w", encoding="utf-8") as f:
        f.write(text)
    print("Updated PROJECT_STATE.md")


def update_changelog():
    p = "docs/03-quality/CHANGELOG.md"
    with open(p, "r", encoding="utf-8") as f:
        text = f.read()

    # 1. Correct V3 hash citation
    text = text.replace(
        "T014_FINAL_REVIEW.zip [4,218,758 bytes, SHA-256 aba67279e0..., 65 member files]",
        "T014_FINAL_REVIEW.zip [4,219,816 bytes, SHA-256 2e522cddb01333836c10f091fb5ad7abc0cc36b77c250a2f27cd16b1b40bfc7c, CRC-32 e07cc024, 65 member files; superseding earlier draft transcription discrepancy aba67279e0...]"
    )

    # 2. Add V4 entry at top of CHANGELOG
    v4_entry = (
        "## docs-v1.1-g6-t014-signoff-blocker-closeout-v4 — 2026-10-22 (controlled completion of Task T014-FINAL-SIGNOFF-BLOCKER-CORRECTION: "
        "resolution of all 4 signoff blockers A..D, dynamic semantic chart traceability 5/5 TRUE, explicit year 2019 route asymmetry table and report reconciliation, "
        "authentic raw execution logs from pytest and QA audit in T014_AUTHENTIC_TEST_AND_AUDIT_LOG.txt, historical V3 hash reconciliation, "
        "publication of versioned run t014_analysis_2016_2024_v4, sealed review package T014_FINAL_REVIEW.zip [4,182,327 bytes, "
        "SHA-256 8dbdbb23e42c35b5463f28328761bf7019fce79f83a48e780dc9a0f026a798f0, CRC-32 1f4055f9, 70 member files], 29/29 unit tests PASS "
        "including 12 negative tests, 91/91 QA audit checks PASS; T-014 verdict T014_SIGNOFF_BLOCKERS_RESOLVED_READY_FOR_HUMAN_SIGNOFF)\n"
        "- 2026-10-22 | docs-v1.1-g6-t014-signoff-blocker-closeout-v4 | PROJECT_STATE.md, BACKLOG.md, AI_HANDOFF.md, CHANGELOG.md, "
        "src/flight_pipeline/analytics/*, tests/test_t014_analytics_comprehensive.py, tools/qa/run_t014_independent_audit.py, "
        "tools/qa/capture_authentic_test_log.py, data/analytics/runs/t014_analysis_2016_2024_v4/*, "
        "D:\\Flight_Audit_Exports\\T014_FULL_ANALYTICS\\signoff_blocker_closeout\\* | Controlled technical completion of Task "
        "T014-FINAL-SIGNOFF-BLOCKER-CORRECTION under Gate G6: (1) Preserved immutable upstream KPI run kpi_run_2016_2024_v1 (684,180 records, "
        "54,674,003 source flight records accepted) and historic v1/v2/v3 analytical artifacts; (2) Blocker A resolved: implemented exact full ID "
        "chart mapping and dynamic derivation of semantic_alignment_verified, confirmed 5/5 semantic checks evaluate to TRUE, verified all 16 "
        "figures have valid RES links, cohort families, and table references with fail-closed enforcement; (3) Blocker B resolved: confirmed "
        "authoritative directed route transformation executes on Year 2019, added explicit year: 2019 column to rq03_directed_routes (CSV & Parquet), "
        "reconciled ORD <-> LGA route pair at ORD->LGA 31.4219% (N=14,108) vs LGA->ORD 28.5976% (N=14,169), diff 2.8242%, total volume 28,277, "
        "min-N SUFFICIENT (>=100), and updated Results Register (RES-011), narrative report Section 5.3, and figure CHART_RQ03_04; "
        "(4) Blocker C resolved: captured authentic raw shell execution output from pytest (29 tests PASS, 9.75s) and independent QA audit "
        "(91 checks PASS) in T014_AUTHENTIC_TEST_AND_AUDIT_LOG.txt; (5) Blocker D resolved: documented authentic physical values of sealed V3 archive "
        "(4,219,816 bytes, SHA-256 2e522cddb01333836c10f091fb5ad7abc0cc36b77c250a2f27cd16b1b40bfc7c, CRC-32 e07cc024, 65 member files) "
        "superseding draft transcription discrepancies; (6) Published versioned run t014_analysis_2016_2024_v4 at data/analytics/runs/ and updated "
        "analytics latest pointer; (7) Assembled external sealed review package T014_FINAL_REVIEW.zip (70 member files, 4,182,327 bytes, "
        "SHA-256 8dbdbb23e42c35b5463f28328761bf7019fce79f83a48e780dc9a0f026a798f0, CRC-32 1f4055f9) and 7 mandatory deliverables at "
        "D:\\Flight_Audit_Exports\\T014_FULL_ANALYTICS\\signoff_blocker_closeout\\; (8) 29/29 unit tests PASS (including 12 negative tests) and "
        "91/91 QA audit checks PASS; (9) Task T-014 verdict T014_SIGNOFF_BLOCKERS_RESOLVED_READY_FOR_HUMAN_SIGNOFF; Gate G6 remains IN_PROGRESS; "
        "D5 remains NOT_AUTHORIZED | data_rebuild=NO (analytical aggregation only; raw, curated, and KPI runs untouched) | "
        "test_t014_analytics_comprehensive.py (29 PASS), run_t014_independent_audit.py (91 PASS) | Full technical blocker resolution and verification "
        "by Senior Data Analytics Engineer & Independent Quality Reviewer awaiting Project Lead human signoff\n\n"
    )

    if "## docs-v1.1-g6-t014-signoff-blocker-closeout-v4" not in text:
        marker = "## docs-v1.1-g6-t014-final-evidence-closeout-v3"
        text = text.replace(marker, v4_entry + marker)

    with open(p, "w", encoding="utf-8") as f:
        f.write(text)
    print("Updated CHANGELOG.md")


def update_backlog():
    p = "docs/01-planning/BACKLOG.md"
    with open(p, "r", encoding="utf-8") as f:
        text = f.read()

    # 1. Update line 3 summary
    text = text.replace(
        "Gate G6 chuyển sang `IN_PROGRESS (T012_T013_SIGNED_OFF, T014_PENDING)`",
        "Gate G6 chuyển sang `IN_PROGRESS (T012_T013_SIGNED_OFF, T014_SIGNOFF_BLOCKERS_RESOLVED_READY_FOR_HUMAN_SIGNOFF)`"
    )

    # 2. Update T-014 row in Backlog table
    old_row = "| T-014 | G6 | Biểu đồ, so sánh 2020 (và cảnh báo năm 2024 khuyết Tháng 3 theo OR-05) và trả lời RQ-01..05 | T-013 | Đóng kiểm toán kỹ thuật V3 hoàn tất (T014_FINAL_READY_FOR_HUMAN_SIGNOFF: 12 bảng, 16 biểu đồ, 20 RES-IDs động với mẫu số cohort cụ thể, ma trận ngữ nghĩa biểu đồ, 8 negative tests fail-closed, báo cáo 10 phần tiếng Việt, gói niêm phong T014_FINAL_REVIEW.zip, 23/23 unit tests PASS, 67/67 QA audit checks PASS) | T014_FINAL_READY_FOR_HUMAN_SIGNOFF |"
    new_row = "| T-014 | G6 | Biểu đồ, so sánh 2020 (và cảnh báo năm 2024 khuyết Tháng 3 theo OR-05) và trả lời RQ-01..05 | T-013 | Khắc phục toàn bộ 4 điểm nghẽn kiểm toán V4 hoàn tất (T014_SIGNOFF_BLOCKERS_RESOLVED_READY_FOR_HUMAN_SIGNOFF: 12 bảng, 16 biểu đồ, 20 RES-IDs, 5/5 semantic checks True, 2019 route analysis 31.42% vs 28.60% diff 2.82%, N=28,277, nhật ký test thô thực tế T014_AUTHENTIC_TEST_AND_AUDIT_LOG.txt, gói niêm phong V4 T014_FINAL_REVIEW.zip [70 members], 29/29 unit tests PASS kèm 12 negative tests, 91/91 QA audit checks PASS) | T014_SIGNOFF_BLOCKERS_RESOLVED_READY_FOR_HUMAN_SIGNOFF |"
    text = text.replace(old_row, new_row)

    # 3. Update obligation table row
    text = text.replace(
        "`T-014 READY_FOR_HUMAN_SIGNOFF` (12 bảng, 16 biểu đồ, 20 RES-IDs, báo cáo 10 phần)",
        "`T-014 T014_SIGNOFF_BLOCKERS_RESOLVED_READY_FOR_HUMAN_SIGNOFF` (12 bảng, 16 biểu đồ, 20 RES-IDs, 5/5 semantic True, 2019 route, 29 tests PASS, 91 checks PASS)"
    )

    with open(p, "w", encoding="utf-8") as f:
        f.write(text)
    print("Updated BACKLOG.md")


def update_ai_handoff():
    p = "docs/04-execution/AI_HANDOFF.md"
    with open(p, "r", encoding="utf-8") as f:
        text = f.read()

    old_g6_status = "- **Gate G6 = IN_PROGRESS (T012_T013_SIGNED_OFF, T014_FINAL_READY_FOR_HUMAN_SIGNOFF)**"
    new_g6_status = "- **Gate G6 = IN_PROGRESS (T012_T013_SIGNED_OFF, T014_SIGNOFF_BLOCKERS_RESOLVED_READY_FOR_HUMAN_SIGNOFF)**"
    text = text.replace(old_g6_status, new_g6_status)

    with open(p, "w", encoding="utf-8") as f:
        f.write(text)
    print("Updated AI_HANDOFF.md")


if __name__ == "__main__":
    update_project_state()
    update_changelog()
    update_backlog()
    update_ai_handoff()
    print("All governance documents successfully updated.")
