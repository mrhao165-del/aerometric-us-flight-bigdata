# T007-02A Final Test Matrix & Comprehensive Verification Record

**Document ID:** `T007_02A_FINAL_TEST_MATRIX.md`  
**Date:** 2026-10-17  
**Task:** `T007-02A` (Source Inventory & Local Hash Verifier Implementation)  
**Parent Task:** `T-007` (Raw CSV Ingestion Pipeline)  
**Status:** `ALL_TESTS_PASS`  
**Engineer:** Lead Big Data QA Engineer & Verification Auditor  

---

## 1. Tổng quan Kết quả Thực thi

Toàn bộ các chu trình kiểm thử, bao gồm unit tests, mutation tests, contract consistency checks, semantic invariant verifiers, và deliverable registry regression tests đều đạt kết quả xuất sắc: **100% PASS, 0 FAIL, 0 ERROR**.

---

## 2. Bảng Ma trận Kiểm thử Tổng thể

| STT | Bộ Kiểm thử / Công cụ | Lệnh Thực thi | Exit Code | Số Lượng Ca / Assertions | Kết quả | Thời gian |
|:---:|---|---|:---:|:---:|:---:|:---:|
| **1** | **Targeted Unit Tests** (`test_t007_source_validator.py`) | `python -m unittest tests/test_t007_source_validator.py` | `0` | 21 tests | **`21 PASS / 0 FAIL`** | 0.123s |
| **2** | **Full Repository Unittest Suite** | `python -m unittest discover tests` | `0` | 80 tests | **`80 PASS / 0 FAIL`** | 24.206s |
| **3** | **T-006 Contract Consistency Verifier** | `python tools/qa/verify_t006_contract_consistency.py` | `0` | 17 Invariants + 16 Mutations | **`33 PASS / 0 FAIL`** | ~1.5s |
| **4** | **G2 Semantic Invariant Verifier** | `python tools/qa/verify_g2_repo_apply_r1_semantic_invariants.py` | `0` | 15 Invariants + 14 Mutations | **`29 PASS / 0 FAIL`** | ~1.2s |
| **5** | **Deliverable Registry Regression Suite** | `python tools/qa/test_working_tree_registry_regression.py` | `0` | 16 Tests (POS-01..02, NEG-01..10, MUT) | **`16 PASS / 0 FAIL`** | ~1.8s |
| **6** | **Working Tree Consistency Checker** | `python tools/check_working_tree_consistency.py` | `0` | 843+ Assertions | **`PASS / 0 FAIL`** | ~4.5s |

---

## 3. Bảng Phân bổ Chi tiết 21 Ca Kiểm thử Mục tiêu (`T007-02A`)

| Mã Kiểm thử | Tên Test Case trong `test_t007_source_validator.py` | Nhóm Chức năng | Trạng thái |
|---|---|---|:---:|
| `INV-01` | `test_inv_01_audited_inventory_entry_count_and_years` | Inventory Baseline | `PASS` |
| `INV-02` | `test_inv_02_no_duplicate_years_or_paths` | Inventory Baseline | `PASS` |
| `INV-03` | `test_inv_03_expected_row_counts_and_byte_sizes` | Inventory Baseline | `PASS` |
| `HASH-01` | `test_hash_01_streaming_sha256_matches_hashlib_reference` | Streaming SHA-256 | `PASS` |
| `HASH-02` | `test_hash_02_empty_file_hashing` | Streaming SHA-256 | `PASS` |
| `HASH-03` | `test_hash_03_file_larger_than_multiple_blocks` | Streaming SHA-256 | `PASS` |
| `HASH-04` | `test_hash_04_streaming_memory_bound_chunk_reads` | Streaming SHA-256 | `PASS` |
| `HASH-05` | `test_hash_05_detect_hash_mismatch` | Streaming SHA-256 | `PASS` |
| `HASH-06` | `test_hash_06_unapproved_baseline_cannot_conclude_verified` | Streaming SHA-256 | `PASS` |
| `ERR-01` | `test_err_01_missing_file` | Lỗi & Ranh giới An toàn | `PASS` |
| `ERR-02` | `test_err_02_permission_error_fail_closed` | Lỗi & Ranh giới An toàn | `PASS` |
| `ERR-03` | `test_err_03_file_modified_during_hashing` | Lỗi & Ranh giới An toàn | `PASS` |
| `ERR-04` | `test_err_04_invalid_path_traversal` | Lỗi & Ranh giới An toàn | `PASS` |
| `ERR-05` | `test_err_05_symlink_escape_rejected` | Lỗi & Ranh giới An toàn | `PASS` |
| `ERR-06` | `test_err_06_size_mismatch_detected` | Lỗi & Ranh giới An toàn | `PASS` |
| `ERR-07` | `test_err_07_corrupt_baseline_format` | Lỗi & Ranh giới An toàn | `PASS` |
| `API-01` | `test_api_01_run_manifest_record_input_compatibility` | Tích hợp T-009 | `PASS` |
| `GOV-01` | `test_gov_01_source_manifest_not_used_as_raw_hash_registry` | Bất biến Quản trị | `PASS` |
| `GOV-02` | `test_gov_02_upstream_identity_unverified_invariant` | Bất biến Quản trị | `PASS` |
| `SCOPE-01` | `test_scope_01_synthetic_isolation_no_real_raw_csv_accessed` | Ranh giới Phạm vi | `PASS` |
| `SCOPE-02` | `test_scope_02_validator_contains_no_csv_reader_or_publication_code` | Ranh giới Phạm vi | `PASS` |
