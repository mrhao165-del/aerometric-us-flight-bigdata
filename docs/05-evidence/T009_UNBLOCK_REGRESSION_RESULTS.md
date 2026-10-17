# T009-UNBLOCK REGRESSION & RECONCILIATION TEST RESULTS

**Task ID:** `T009-UNBLOCK-R1`  
**Gate:** `G4`  
**Auditor:** Senior Software Engineer, Repository Governance Engineer & Independent QA Engineer  
**Timestamp:** 2026-10-17T08:25:30+07:00  
**Status:** `ALL_REGRESSION_TESTS_PASS`  

---

## 1. Mục Đích & Bộ Công Cụ Kiểm Thử Hồi Quy

Tài liệu này ghi nhận nguyên văn kết quả thực thi các bộ kiểm tra quản trị và kiểm toán tính nhất quán của repository sau khi thực hiện chuẩn hóa bằng chứng phẳng và đăng ký đầy đủ vào sổ đăng ký `EVIDENCE_DELIVERABLE_REGISTER.json`.

Các công cụ bắt buộc:
1. `python tools/check_working_tree_consistency.py`
2. `python tools/qa/verify_t006_contract_consistency.py`

---

## 2. Bảng Tổng Hợp Kết Quả Thực Thi (Execution Summary)

| Kịch bản Kiểm thử | Lệnh Thực thi | Phiên bản Python | Exit Code | Kết quả Assertions | Trạng thái |
|---|---|:---:|:---:|:---:|:---:|
| **Working-Tree Consistency Verifier** | `python tools/check_working_tree_consistency.py` | `Python 3.10.11` | `0` | `385 PASS, 0 FAIL` | **`PASS`** |
| **T-006 Contract Consistency Verifier** | `python tools/qa/verify_t006_contract_consistency.py` | `Python 3.10.11` | `0` | `17 Invariants PASS, 16 Mutations PASS, 0 FAIL` | **`PASS`** |

---

## 3. Nhật Ký Chi Tiết Thực Thi (Detailed Execution Logs)

### 3.1. Nhật ký `tools/check_working_tree_consistency.py`:
```text
Working-Tree PASS assertions: 385; FAIL: 0
ALL WORKING-TREE CHECKS PASSED.
```

### 3.2. Nhật ký `tools/qa/verify_t006_contract_consistency.py`:
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

---

## 4. Đánh Giá Khuyết Tật & Tính Toàn Vẹn Cây Làm Việc

- Không có lỗi gãy liên kết Markdown.
- Không có lỗi thiếu hoặc thừa tệp trong cây làm việc (`unrecognized stray files = 0`).
- Mọi tệp bằng chứng mới tạo đều được kiểm soát mã băm SHA-256 và kích thước byte trong `EVIDENCE_DELIVERABLE_REGISTER.json`.
- Hệ sinh thái kiểm toán đạt trạng thái chuẩn tắc cao nhất.
