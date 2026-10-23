# G6_PRODUCTION_ENTRY_ACCEPTANCE_MATRIX.md
# Ma Trận Nghiệm Thu Sẵn Sàng Vận Hành Gate G6 (G6 Production Entry Acceptance Matrix)

**Mã tài liệu:** `G6_PRODUCTION_ENTRY_ACCEPTANCE_MATRIX`  
**Dự án:** US Flight Performance Analysis 2016–2024  
**Nhiệm vụ:** T-012 — Nine-Year Ingestion Preflight & Contract Reconciliation  
**Gate quản trị:** Gate G5 = IN_PROGRESS, Gate G6 = NOT_STARTED / BLOCKED  
**Vai trò:** Principal Big Data Architect, PySpark Release Reliability Engineer, Governance Auditor  
**Ngày lập:** 2026-10-20  

---

## 1. MA TRẬN KHẮC PHỤC SÁU PHÁT HIỆN TRỌNG YẾU (FINDINGS C01–C06)

| Mã | Tên phát hiện trọng yếu | Trạng thái kỹ thuật | Bằng chứng kiểm toán & Tài liệu nghiệm thu | Phán quyết độc lập |
| :---: | :--- | :---: | :--- | :---: |
| **G6-C01** | **Annual Row Count Discrepancy**<br>Phân bổ sai số dòng 2017–2024 trong danh mục G6 cũ (2024 ghi 3.63M thay vì 6.28M). | **CLOSED / VERIFIED** | - Quét đọc luồng giới hạn (streaming bounded) 9 CSV thô: tổng 54.674.003 dòng, năm 2024 đúng 6.284.841 dòng.<br>- Khớp 100% `inputs/schema_YYYY.json`, `source_validator.py`, `T004_FINAL_QA_RECONCILIATION.md`.<br>- Tài liệu: [`G6_C01_ANNUAL_ROW_COUNT_RECONCILIATION.md`](./G6_C01_ANNUAL_ROW_COUNT_RECONCILIATION.md), [`G6_T012_CANONICAL_SOURCE_INVENTORY.md`](./G6_T012_CANONICAL_SOURCE_INVENTORY.md).<br>- Test: `tests/test_g6_annual_source_counts.py` (5/5 PASS, có anti-masking test). | **PASS** |
| **G6-C02** | **Wrong Eight CORE KPI Mapping**<br>Checklist G6 mô tả sai các KPI thành OTP-15, Severe Delay, Elapsed Ratio, Cancel Proxy. | **CLOSED / VERIFIED** | - Đính chính toàn diện Section 4 trong `G6_T012_FINAL_EXECUTION_CHECKLIST_V2.md`.<br>- Bác bỏ mọi proxy không hợp đồng; giữ 8 CORE KPI chuẩn: KPI-01 (count), KPI-02 (arr delay rate >=15), KPI-03 (signed arr delay), KPI-04 (dep delay rate >=15), KPI-05 (signed dep delay), KPI-06 (P50/P90 accuracy=10000), KPI-07 (2 submetrics taxi), KPI-08 (3 submetrics elapsed/air).<br>- Tài liệu: [`G6_C02_CANONICAL_EIGHT_KPI_CONTRACT_AUDIT.md`](./G6_C02_CANONICAL_EIGHT_KPI_CONTRACT_AUDIT.md).<br>- Test: `tests/test_g6_kpi_contract_consistency.py` (7/7 PASS). | **PASS** |
| **G6-C03** | **Multi-Year Publication Snapshot**<br>Đọc wildcard `runs/run_*/` gây nguy cơ đọc trùng bản ghi khi chạy lại nhiều phiên bản của cùng một năm. | **CLOSED / VERIFIED** | - Thiết kế kiến trúc Sổ đăng ký snapshot 9 năm `multi_year_dataset_registry.json`.<br>- Khóa 7 quy tắc chặn lỗi Fail-Closed: đủ 9 năm, đúng 1 run_id mỗi năm, đường dẫn vật lý rời nhau, hạch toán đúng 54.67M dòng.<br>- Công cụ: `tools/qa/verify_multiyear_snapshot.py`.<br>- Tài liệu: [`G6_C03_MULTIYEAR_SNAPSHOT_AND_VERSION_POLICY.md`](./G6_C03_MULTIYEAR_SNAPSHOT_AND_VERSION_POLICY.md).<br>- Test: `tests/test_multiyear_snapshot_policy.py` (4/4 PASS, chứng minh re-run không gây duplicate). | **PASS** |
| **G6-C04** | **2016 Baseline Integration**<br>Lựa chọn giữa Thăng hạng T-010 (Option A) vs Chạy lại độc lập (Option B). | **CLOSED / VERIFIED** | - Xác nhận 50/50 tệp Parquet T-010 còn nguyên vẹn trong `D:\Study\Code\Apache\Flight_Analyzt\staging\`.<br>- Đánh giá kỹ thuật: Khuyến nghị Phương án B (Unified Production Re-run) để đồng nhất ExecutionReceipt, RunManifest và tích hợp registry mượt mà, đồng thời bảo vệ 50 tệp T-010 làm đối chứng lịch sử.<br>- Tài liệu: [`G6_C04_2016_BASELINE_OPTION_REVIEW.md`](./G6_C04_2016_BASELINE_OPTION_REVIEW.md).<br>- Chờ Project Lead quyết định chính thức trước D5. | **PASS** |
| **G6-C05** | **Stale Paths & Lock Preflight**<br>Đường dẫn cũ (`staging/active`, `curated/published`) và thiếu lệnh preflight lock độc lập cho Windows CLI. | **CLOSED / VERIFIED** | - Đánh dấu `SUPERSEDED` văn bản v1 cũ (`G6_T012_EXECUTION_CHECKLIST.md`).<br>- Ban hành công cụ CLI độc lập: `tools/qa/check_writer_preflight_safety.py` (quét chỉ đọc, phát hiện liveness PID, recovery marker, trả mã thoát 0/1/2/3/4).<br>- Kiểm thử 6 trạng thái preflight: active, stale, ambiguous, corrupted, recovery markers, clean.<br>- Chuẩn hóa chính sách tài nguyên: Đĩa trống 57.90 GiB (3.13x), Spark scratch trên ổ D, RAM >= 16 GB, JVM Heap 4G.<br>- Tài liệu: [`G6_C05_EXECUTION_PATH_LOCK_RESOURCE_AUDIT.md`](./G6_C05_EXECUTION_PATH_LOCK_RESOURCE_AUDIT.md).<br>- Test: `tests/test_lock_state_vs_pointer_state.py` (6/6 PASS). | **PASS** |
| **G6-C06** | **Evidence Report Integrity**<br>Đối soát mã băm giữa báo cáo, package manifest và working-tree thực tế. | **CLOSED / VERIFIED** | - Trích xuất 787 thành phần từ manifest `G5_SIGNOFF_G6_EXECUTION_CONTRACT_FINAL_REVIEW_MANIFEST.json`.<br>- Xác nhận 782 tệp khớp 100% không đổi, 5 tệp được cập nhật có chủ đích cho G6 readiness.<br>- Lập bảng đối soát máy đọc được: [`G6_C06_EVIDENCE_HASH_RECONCILIATION.json`](./G6_C06_EVIDENCE_HASH_RECONCILIATION.json) (167 KB). | **PASS** |

---

## 2. RANH GIỚI THẨM QUYỀN VÀ TRẠNG THÁI CÁC QUYẾT ĐỊNH CON NGƯỜI (HUMAN DECISIONS)

| Mã quyết định | Tên văn bản quyết định | Phạm vi phê duyệt của con người | Trạng thái hiện tại | Ranh giới thực thi của Agent |
| :---: | :--- | :--- | :---: | :--- |
| **D1** | `G5_D1_BTS_PROVENANCE_ATTESTATION_DRAFT.md` | Xác nhận nguồn gốc tải tệp BTS ZIP từ Cổng TranStats. | `PENDING_HUMAN_SIGNATURE` | Nghiêm cấm Agent tự ý ký duyệt. |
| **D2** | `G5_D2_FP_DEC_019_OPTION_B_APPROVAL_DRAFT.md` | Phê duyệt chính sách FP-DEC-019 Phương án B (chấp thuận đối chiếu 7 trường CSV). | `PENDING_HUMAN_SIGNATURE` | Nghiêm cấm Agent tự ý ký duyệt. |
| **D3** | `G5_D3_TS018_HUMAN_TECHNICAL_SIGNOFF_DRAFT.md` | Nghiệm thu kỹ thuật TS-018 và giải tỏa ngoại lệ G2-EXC-001. | `PENDING_HUMAN_SIGNATURE` | G2-EXC-001 tiếp tục ở trạng thái `ACTIVE` đến khi có chữ ký D3. |
| **D4** | `G5_D4_G5_HUMAN_GATE_SIGNOFF_DRAFT.md` | Chính thức phê chuẩn PASS và đóng Gate G5. | `PENDING_HUMAN_SIGNATURE` | Gate G5 giữ nguyên trạng thái `IN_PROGRESS`. |
| **D5** | Cấp phép vận hành Gate G6 (Full Ingestion T-012) | Cho phép khởi chạy Spark nạp 54.67M dòng dữ liệu 9 năm. | **`NOT_AUTHORIZED`** | **TUYỆT ĐỐI CẤM THỰC THI T-012 KHI CHƯA CÓ D5.** |

---

## 3. DANH MỤC CÁC RỦI RO CÒN LẠI ĐƯỢC QUẢN TRỊ (MANAGED RESIDUAL RISKS)

1. **OR-08 (Kaggle Upstream Provenance):** Không suy diễn danh tính toàn bộ 54.7M dòng Kaggle; kiểm soát bằng snapshot hash nội bộ và đối chiếu phân tầng 1.500 chuyến bay TS-018.
2. **OR-05 (2024 Date Coverage Gap):** Giữ nguyên trạng thái `OPEN_QUALITY_DEFECT`, không nội suy dữ liệu giả cho Tháng 3/2024; gắn nhãn `source_coverage_status = PARTIAL`.
3. **FP-DEC-017 (Weather Branch Exclusion):** Nhánh thời tiết giữ trạng thái `CONDITIONAL_NO_GO`, không đưa vào CORE.
4. **G2-EXC-001 (Provisional Units):** Tiếp tục ở trạng thái `ACTIVE` cho đến khi có chữ ký D3.
5. **PARQUET_PARITY_NOT_TESTED:** Khẳng định đối chiếu TS-018 Option B chỉ áp dụng cho Raw CSV ↔ BTS Reference; chưa bao gồm đối chiếu Parquet 9 năm (sẽ đối chiếu sau T-012).

---

## 4. KẾT LUẬN CUỐI CÙNG

Hồ sơ kỹ thuật đã hoàn tất 100% việc khắc phục các sai lệch C01–C06, đồng bộ hóa tuyệt đối hợp đồng dữ liệu, hợp đồng KPI và kiến trúc xuất bản an toàn.

**Trạng thái đề xuất cho Project Lead:**
$$\mathbf{READY\_FOR\_PROJECT\_LEAD\_G6\_ARCHITECTURE\_AND\_D5\_REVIEW}$$
