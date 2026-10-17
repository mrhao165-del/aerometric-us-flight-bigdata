# T009-PRESIGNOFF: AUTOMATED TEST COVERAGE & VERIFICATION MATRIX

**Task ID:** `T-009` (Pre-Signoff Test Audit)  
**Gate:** `G4`  
**Auditor:** Software Testing & Independent QA Auditor  
**Execution Mode:** `READ_ONLY_SOURCE_AUDIT — EVIDENCE_OUTPUT_ONLY`  
**Date:** 2026-10-17  
**Status:** `ALL_TESTS_VERIFIED_PASS`  

---

## 1. Ma Trận Bao Phủ 13 Bài Kiểm Thử Đơn Vị Tự Động (Unit Test Coverage)

Toàn bộ 13 bài kiểm thử đơn vị trong thư mục `tests/` đã được kiểm toán đối chiếu chi tiết giữa mã kiểm thử, mục tiêu thiết kế và hợp đồng chuẩn tắc:

| STT | Tệp Kiểm Thử | Tên Hàm Kiểm Thử Chuẩn Xác | Ràng Buộc Hợp Đồng / Kiến Trúc | Cơ Chế Kiểm Tra Cụ Thể | Kết Quả Thực Tế |
|:---:|---|---|---|---|:---:|
| 1 | [`tests/test_manifest.py`](../../tests/test_manifest.py#L40-L48) | `test_dc12_ingest_acceptance_rate` | DATA_CONTRACT.md (DC-12) | Tính $accepted / raw$; kiểm tra trường hợp mẫu số 0 trả về `None` (`ZERO_DENOMINATOR`). | **PASS** |
| 2 | [`tests/test_manifest.py`](../../tests/test_manifest.py#L49-L60) | `test_dc12_metric_accounting` | DATA_CONTRACT.md (DC-12) | Hạch toán theo từng chỉ số, tính `excluded_count` và `metric_valid_rate`; bảo vệ mẫu số 0. | **PASS** |
| 3 | [`tests/test_manifest.py`](../../tests/test_manifest.py#L20-L39) | `test_row_accounting_balance_invariant` | DATA_CONTRACT.md (DC-11) | Kiểm tra tính cân bằng ba trạng thái rời nhau: $raw = accepted + quarantined + rejected$. | **PASS** |
| 4 | [`tests/test_manifest.py`](../../tests/test_manifest.py#L61-L90) | `test_run_manifest_lifecycle_and_hashing` | ARCHITECTURE.md Section 4 | Vòng đời RunManifest, ghi vết input/output, tạo JSON và tính toán mã băm SHA-256. | **PASS** |
| 5 | [`tests/test_numeric_predicates.py`](../../tests/test_numeric_predicates.py#L61-L79) | `test_delay_predicates_preserve_signed_negative` | FP-DEC-004, KPI-02..05 | Khẳng định độ trễ âm (`-25.0`, `-10.0`) là hợp lệ để phản ánh bay sớm. | **PASS** |
| 6 | [`tests/test_numeric_predicates.py`](../../tests/test_numeric_predicates.py#L101-L125) | `test_duration_predicates_require_strictly_positive` | G3-COND-B, KPI-08 | Khẳng định thời gian bay `AIR_TIME` và elapsed time bắt buộc $> 0.0$; loại trừ giá trị 0.0. | **PASS** |
| 7 | [`tests/test_numeric_predicates.py`](../../tests/test_numeric_predicates.py#L38-L60) | `test_is_finite_numeric_matrix` | T006 FIX-02 (Addendum Sec 3) | Bảng chân lý: loại trừ `None`, `NaN`, $+\infty$, $-\infty$; chấp nhận số thực hữu hạn. | **PASS** |
| 8 | [`tests/test_numeric_predicates.py`](../../tests/test_numeric_predicates.py#L80-L100) | `test_taxi_predicates_require_non_negative` | KPI-07 (Sub 7a, 7b) | Khẳng định thời gian lăn bánh `TAXI_OUT`, `TAXI_IN` bắt buộc $\ge 0.0$; chấp nhận giá trị 0.0. | **PASS** |
| 9 | [`tests/test_publication_safety.py`](../../tests/test_publication_safety.py#L74-L107) | `test_fault_injection_step5_preserves_previous_pointer_and_staging` | TS-013 Simulation, FIX-03 | Bơm lỗi tại Bước 5; khẳng định con trỏ cũ và staging không bị xóa mất dấu vết. | **PASS** |
| 10 | [`tests/test_publication_safety.py`](../../tests/test_publication_safety.py#L21-L46) | `test_successful_publication_sequence` | ARCHITECTURE.md Section 2 | Chu trình xuất bản an toàn 7 bước, thăng cấp phân bản và trỏ `latest_run_id.txt`. | **PASS** |
| 11 | [`tests/test_publication_safety.py`](../../tests/test_publication_safety.py#L47-L73) | `test_unbalanced_accounting_aborts_publication` | TS-003 Simulation, DC-11 | Ngắt xuất bản tại Bước 2 khi vi phạm bất biến dòng (`ACCOUNTING_UNVERIFIED`). | **PASS** |
| 12 | [`tests/test_publication_safety.py`](../../tests/test_publication_safety.py#L108-L134) | `test_version_immutability_rejection` | FIX-03 Immutability Guard | Từ chối thăng cấp khi thư mục phân bản đã tồn tại (`FAILED_VERSION_EXISTS`). | **PASS** |
| 13 | [`tests/test_spark_env.py`](../../tests/test_spark_env.py#L18-L36) | `test_spark_session_creation_and_config` | ARCHITECTURE.md Section 3 | Khởi tạo SparkSession với cấu hình tối ưu, kiểm tra RDD sum và DataFrame count. | **PASS** |

---

## 2. Phân Định Ranh Giới Kiểm Thử Đơn Vị vs Kiểm Thử Vận Hành TEST_PLAN.md

Kiểm toán viên nhấn mạnh nguyên tắc phân định cấp độ kiểm thử:
- Các bài kiểm thử đơn vị trên là các **mô phỏng cục bộ (local unit simulations)** nhằm chứng minh tính đúng đắn của thuật toán trước khi vận hành pipeline sản xuất.
- **Tuyệt đối không đánh đồng** các unit test này với các mã kiểm thử vận hành toàn diện quy định trong [`TEST_PLAN.md`](../03-quality/TEST_PLAN.md):
  - `TS-009` (Ingestion schema enforcement): Thuộc phạm vi nghiệm thu nhiệm vụ T-007 tại Gate G4.
  - `TS-013` (Fault injection & recovery at scale): Thuộc phạm vi kiểm thử tích hợp trên toàn bộ dữ liệu tại Gate G5.
  - `TS-014` (Pipeline execution idempotency): Thuộc phạm vi chạy kép (dual-run) kiểm tra tính lũy đẳng tại Gate G5/G6.
  - `TS-018` (Statistical & numerical accuracy at 54.7M rows): Đã được hoãn lại (deferred) có bảo lưu sang Gate G5 theo phê duyệt G2/G3.

---

## 3. Tổng Hợp Kết Quả 4 Bộ Kiểm Thử Hồi Quy QA Cấp Hệ Thống

Ngoài 13 unit tests, 4 bộ công cụ kiểm toán QA độc lập đã được thực thi và xác nhận:

| Bộ Kiểm Thử Hồi Quy | Đường Dẫn Script | Số Lượng Ca Kiểm Thử | Kết Quả Đo Lường |
|---|---|:---:|:---:|
| **Validator Extension Security** | [`tools/qa/test_t009_r1_validator_extension.py`](../../tools/qa/test_t009_r1_validator_extension.py) | 8 tests (4 Pos, 4 Neg) | **8 PASS, 0 FAIL** |
| **Git Exclusion Verification** | [`tools/qa/test_t009_unblock_r2_git_exclusion.py`](../../tools/qa/test_t009_unblock_r2_git_exclusion.py) | 7 tests (2 Pos, 5 Neg) | **7 PASS, 0 FAIL** |
| **Deliverable Registry Regression**| [`tools/qa/test_working_tree_registry_regression.py`](../../tools/qa/test_working_tree_registry_regression.py) | 16 tests (2 Pos, 14 Neg/Mut) | **16 PASS, 0 FAIL** |
| **T-006 Semantic Contract Verifier**| [`tools/qa/verify_t006_contract_consistency.py`](../../tools/qa/verify_t006_contract_consistency.py) | 17 Invariants, 16 Mutations | **33 PASS, 0 FAIL** |

---

## 4. Chứng Minh Bất Biến Toán Học Của Công Cụ Kiểm Toán Cây Làm Việc

Công thức xác định tổng số khẳng định trong [`tools/check_working_tree_consistency.py`](../../tools/check_working_tree_consistency.py):
$$	ext{Total Assertions} = 	ext{Baseline Checks (111)} + 2 	imes 	ext{Registered Deliverables (N)}$$
- Mỗi deliverable hợp lệ được cộng chính xác 2 assertions: (1) khẳng định tệp vật lý tồn tại (`df.is_file()`), và (2) khẳng định kích thước byte và mã băm SHA-256 khớp tuyệt đối với sổ bộ (`meta_ok`).
- Trạng thái kiểm chứng sau R2: $111 + 2 	imes 203 = 517$ assertions (100% PASS).
