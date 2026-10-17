# T007-02A Scope & Git Diff Audit Record

**Document ID:** `T007_02A_SCOPE_AND_DIFF_AUDIT.md`  
**Date:** 2026-10-17  
**Task:** `T007-02A` (Source Inventory & Local Hash Verifier Implementation)  
**Parent Gate:** `G4` (`PLANNED / NOT_COMPLETED`)  
**Status:** `AUDITED_AND_VERIFIED`  
**Auditor:** Senior Git Configuration Management & Independent Diff Auditor  

---

## 1. Mục tiêu Kiểm toán Phạm vi

Tài liệu này xác nhận rằng mọi thay đổi trong Subtask `T007-02A` đều nằm nghiêm ngặt trong phạm vi được Project Lead ủy quyền, không sửa đổi bất kỳ tệp dữ liệu thô nào và không làm sai lệch các hợp đồng quản trị đã phê duyệt.

---

## 2. Bảng Kiểm kê Chi tiết Thay đổi Tệp (File Change Audit)

| Đường dẫn Tệp | Loại Thay đổi | Mục đích & Ranh giới |
|---|:---:|---|
| `docs/05-evidence/T007_02A_HANDOFF_ERRATA.md` | `MỚI` | Ban hành đính chính kỹ thuật DOC-F01 (`SOURCE_MANIFEST.json`) và DOC-F02 (`RunManifest.record_input`). |
| `src/flight_pipeline/ingestion/source_validator.py` | `MỚI` | Triển khai module Source Inventory & Streaming SHA-256 Verifier. |
| `src/flight_pipeline/ingestion/__init__.py` | `SỬA` | Bổ sung public exports cho các lớp và hàm của `source_validator.py`. |
| `tests/test_t007_source_validator.py` | `MỚI` | Bộ kiểm thử tổng hợp 21 ca kiểm thử cho module validator. |
| `docs/05-evidence/T007_02A_BASELINE_AND_AUTHORIZATION.md` | `MỚI` | Hồ sơ ghi nhận ủy quyền của Project Lead và baseline entry. |
| `docs/05-evidence/T007_02A_SOURCE_VALIDATOR_DESIGN.md` | `MỚI` | Tài liệu kiến trúc và đặc tả thiết kế module validator. |
| `docs/05-evidence/T007_02A_HASH_AND_INVENTORY_TESTS.md` | `MỚI` | Báo cáo chi tiết các bài kiểm thử tổng hợp băm và inventory. |
| `docs/05-evidence/T007_02A_SOURCE_INTEGRITY_THREAT_MODEL.md` | `MỚI` | Phân tích mô hình đe dọa an toàn hệ thống tệp. |
| `docs/05-evidence/T007_02A_T009_API_COMPATIBILITY.md` | `MỚI` | Đánh giá tính tương thích API giữa T007-02A và T-009. |
| `docs/05-evidence/T007_02A_SCOPE_AND_DIFF_AUDIT.md` | `MỚI` | Bản tài liệu kiểm toán phạm vi và diff này. |
| `docs/05-evidence/T007_02A_FINAL_TEST_MATRIX.md` | `MỚI` | Bảng ma trận kết quả kiểm thử toàn diện của task. |
| `docs/05-evidence/T007_02A_FINAL_VERDICT.md` | `MỚI` | Biên bản kết luận chính thức của Subtask T007-02A. |
| `docs/04-execution/PROJECT_STATE.md` | `SỬA` | Cập nhật snapshot tiến độ thực thi T007-02A có kiểm soát. |
| `docs/05-evidence/EVIDENCE_DELIVERABLE_REGISTER.json` | `SỬA` | Đăng ký các deliverable mới vào hệ thống quản trị. |

---

## 3. Bằng chứng Bất biến Không Sửa đổi (Untouched Invariants)

Kiểm tra đối chiếu xác nhận các nhóm tệp sau **hoàn toàn không bị sửa đổi, truy cập hoặc ghi đè**:
1. **Dữ liệu thô (`data/raw/`):** Không có tệp CSV hoặc directory nào bị chạm đến hoặc thay đổi kích thước/mtime.
2. **SOURCE_MANIFEST (`docs/05-evidence/inputs/SOURCE_MANIFEST.json`):** Giữ nguyên vẹn mã băm và cấu trúc 13 nguồn tài liệu audit.
3. **Mã nguồn Schema T007-01 (`src/flight_pipeline/ingestion/schema.py`):** Giữ nguyên vẹn 100%.
4. **Mã nguồn T-009 (`run_manifest.py`, `publication.py`):** Giữ nguyên vẹn 100%.
5. **Hợp đồng Canonical (`DATA_CONTRACT.md`, `KPI_SPEC.md`, `TEST_PLAN.md`, `DECISIONS.md`, `AGENTS.md`):** Giữ nguyên vẹn 100%.
6. **Không có mã nạp/ghi Parquet:** Tuyệt đối không có code reader Spark, không có code classifier dòng, không có code xuất bản Parquet.
