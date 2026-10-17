# T009-UNBLOCK-R2: COMPREHENSIVE REGRESSION & VERIFICATION TEST RESULTS

**Task ID:** `T009-UNBLOCK-R2` (Targeted Git Metadata Exclusion & Validator Reconciliation)  
**Gate:** `G4`  
**Auditor:** Senior Software Engineer, Repository Governance Engineer & Independent QA Engineer  
**Timestamp:** 2026-10-17T08:41:00+07:00  
**Status:** `ALL_TESTS_PASS`  

---

## 1. Mục Tiêu & Tổng Thể Các Bộ Kiểm Thử (Verification Overview)

Tài liệu này ghi nhận nguyên văn toàn bộ các kết quả kiểm thử bắt buộc cho nhiệm vụ `T009-UNBLOCK-R2`:
1. Kiểm tra tái hiện lỗi trước khi sửa đổi (Pre-remediation failure check).
2. Kiểm tra bất biến khế ước Gate G3 / T-006 (T-006 contract consistency & mutation suite).
3. Kiểm tra kiểm chứng hai chiều dương tính / âm tính (Positive & Negative verification suite).
4. Kiểm tra cây làm việc sau khi sửa đổi (Post-remediation consistency check).

---

## 2. Bảng Tổng Hợp Kết Quả Thực Thi (Execution Summary)

| STT | Bộ Kiểm Thử (`Test Suite`) | Lệnh Thực Thi | Phiên Bản Python | Exit Code | Kết Quả Thực Tế | Trạng Thái |
|:---:|---|---|:---:|:---:|:---:|:---:|
| **1** | **Pre-Remediation Working-Tree Verifier** | `python tools/check_working_tree_consistency.py` | `Python 3.10.11` | `1` | `383 PASS, 2 FAIL`<br>(227 tệp `.git/` bị nhận diện là stray files) | **`REPRODUCED`** |
| **2** | **T-006 Contract Consistency Verifier** | `python tools/qa/verify_t006_contract_consistency.py` | `Python 3.10.11` | `0` | `17 Invariants PASS`<br>`16 Mutations PASS, 0 FAIL` | **`PASS`** |
| **3** | **Dedicated Positive & Negative Suite** | `python tools/qa/test_t009_unblock_r2_git_exclusion.py` | `Python 3.10.11` | `0` | `2 Positive PASS`<br>`5 Negative/Tamper PASS, 0 FAIL` | **`PASS`** |
| **4** | **Post-Remediation Working-Tree Verifier** | `python tools/check_working_tree_consistency.py` | `Python 3.10.11` | `0` | `385 PASS, 0 FAIL`<br>(Toàn bộ 137 deliverables và cây làm việc hợp lệ) | **`PASS`** |

---

## 3. Nhật Ký Chi Tiết Từng Bộ Kiểm Thử (Detailed Execution Logs)

### 3.1. Nhật ký Kiểm thử Bất biến T-006 (`verify_t006_contract_consistency.py`):
```text
================================================================================
RUNNING T-006 CONTRACT CONSISTENCY & IMPLEMENTATION-SAFETY VERIFIER
================================================================================
[PASS] Case 1: All 34 raw columns match canonical names and physical order.
[PASS] Case 2: All 9 fabricated columns removed; 9 restored canonical columns verified.
[PASS] Case 3: Physical order and audited raw dtypes agree with schema_YYYY.json evidence.
[PASS] Case 4: KPI-01..08 IDs, submetrics, and formulas agree with KPI_SPEC.md.
[PASS] Case 5: KPI-03 verified as Signed Mean ARR_DELAY (negative delay preserved, not late rate).
[PASS] Case 6: KPI-02/04 verified as Late Rate >= 15.0 (boundary 15.0 included, not on-time rate).
[PASS] Case 7: Metric-valid denominators N_valid independent across submetrics; ZERO_METRIC_DENOMINATOR enforced.
[PASS] Case 8: No CANCELLED or DIVERTED references in CORE filters.
[PASS] Case 9: TS-012/013/015/016/020 match authoritative TEST_PLAN.md specifications.
[PASS] Case 10: G2-EXC-001 verified as provisional unit status with G5 TS-018 mandatory hard stop blocking G6.
[PASS] Case 11: Gate G2 confirmed PASS; Gate G3 confirmed PASS with human acceptance record; T-006 confirmed PASS / COMPLETED.
[PASS] Case 12: Downstream G4 tasks (T-009, T-007, T-008) verified NOT_STARTED.
[PASS] Case 13: DC-11/12 row accounting and Record vs Metric Validity verified (metric invalidity does not quarantine flight).
[PASS] Case 14: Complete finite numeric predicate verified with explicit NaN and Inf handling for all 7 CORE measures.
[PASS] Case 15: Safe 7-step Windows NTFS publication order and TS-013 fault injection verified.
[PASS] Case 16: Raw schema boundary verified (nullable Int64 calendar fields, anchored date regex, no unapproved NOT_NULL).
[PASS] Case 17: Safe non-destructive rollback policy verified (destructive Remove-Item commands superseded and revoked).
[PASS] Mutation Suite: 16 isolated mutation tests successfully detected and rejected.
================================================================================
VERIFICATION SUMMARY: 17 INVARIANTS PASS, 16 MUTATIONS PASS, 0 FAIL
================================================================================
ALL T-006 CONTRACT CONSISTENCY & IMPLEMENTATION-SAFETY CHECKS PASSED.
```

### 3.2. Nhật ký Bộ Kiểm thử Dương tính & Âm tính (`test_t009_unblock_r2_git_exclusion.py`):
```text
================================================================================
RUNNING T009-UNBLOCK-R2 GIT EXCLUSION POSITIVE & NEGATIVE VERIFICATION SUITE
================================================================================
[PASS] POS-01: Isolated repo with root `.git/` metadata is cleanly accepted with 0 errors
[PASS] POS-02: Markdown file inside root `.git/` is ignored by active docs checks and accounting
[PASS] NEG-01: Unrecognized stray file at repository root is strictly rejected
[PASS] NEG-02: Unrecognized stray file in docs/ subfolder is strictly rejected
[PASS] NEG-03: Unrecognized stray Python script in tools/ subfolder is strictly rejected
[PASS] NEG-04: Nested `.git/` outside repository root is NOT ignored and strictly rejected
[PASS] NEG-05: Tampered deliverable with SHA-256/size mismatch is strictly detected and rejected
================================================================================
VERIFICATION SUMMARY: 7 PASS, 0 FAIL
================================================================================
ALL T009-UNBLOCK-R2 POSITIVE & NEGATIVE CHECKS PASSED.
```

### 3.3. Nhật ký Kiểm tra Tính nhất quán Cây làm việc Sau sửa đổi:
```text
Working-Tree PASS assertions: 385; FAIL: 0
ALL WORKING-TREE CHECKS PASSED.
```

---

## 4. Đánh Giá Chất Lượng & Tính Toàn Vẹn Cây Làm Việc

1. **Hiệu quả của bộ lọc:** Toàn bộ siêu dữ liệu `.git/` ở root được bỏ qua chính xác, không còn gây nghẽn hạch toán cây làm việc.
2. **Khả năng phát hiện tệp lạ:** Các ca kiểm thử âm tính chứng minh validator vẫn phát hiện và chặn đứng 100% các tệp lạ đưa vào ở mọi cấp thư mục.
3. **Tính toàn vẹn mã băm:** Mọi tệp bằng chứng và kịch bản trong `docs/05-evidence/` và `tools/` đều trùng khớp byte-for-byte và SHA-256 với sổ đăng ký quản trị.
