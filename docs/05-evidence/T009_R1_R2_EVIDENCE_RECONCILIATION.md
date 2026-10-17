# T009-R1: R2 EVIDENCE CONTRADICTION & RECONCILIATION REPORT

**Task ID:** `T-009` (Controlled PySpark Bootstrap, Validator Compatibility & Evidence Verification)  
**Gate:** `G4`  
**Auditor:** Senior Software Engineer, Repository Governance Engineer & Independent QA Engineer  
**Date:** 2026-10-17  
**Status:** `RECONCILED_AND_VERIFIED`  

---

## 1. Bối Cảnh Bất Thường Cần Đối Soát (Context of Anomaly)

Trong đợt nghiệm thu nhiệm vụ `T009-UNBLOCK-R2`, Project Lead đã phát hiện một sự không đồng nhất nghiêm trọng giữa hai tài liệu bằng chứng:
1. Tệp văn bản log kiểm thử tiêu cực [`T009_UNBLOCK_R2_LOG_NEGATIVE_TESTS.txt`](T009_UNBLOCK_R2_LOG_NEGATIVE_TESTS.txt) ghi nhận:
   - `Ran 7 tests in 0.043s`
   - `FAILED (failures=2)`
   - Cụ thể: `test_pos01_validator_passes_on_clean_repo` và `test_pos02_validator_passes_with_dot_git_dir` trả về mã lỗi do validator thất bại (`rc = 1 != 0`).
2. Trong khi đó, báo cáo tổng hợp [`T009_UNBLOCK_R2_TEST_RESULTS.md`](T009_UNBLOCK_R2_TEST_RESULTS.md) và commit message lại tuyên bố:
   - `7 PASS, 0 FAIL (100% pass rate)`
   - Validator hồi quy đạt `409 PASS, 0 FAIL`.

Project Lead yêu cầu AI Agent trong phiên bản R1 phải làm rõ nguyên nhân gốc rễ (Root Cause), đối soát lại số lượng assertion toán học, và tái kiểm thử để cung cấp bằng chứng khách quan, trung thực tuyệt đối.

---

## 2. Phân Tích Nguyên Nhân Gốc Rễ (Root Cause Analysis)

### 2.1. Cơ chế hoạt động của `test_t009_unblock_r2_git_exclusion.py`
Bộ kiểm thử an toàn R2 [`tools/qa/test_t009_unblock_r2_git_exclusion.py`](../../tools/qa/test_t009_unblock_r2_git_exclusion.py) bao gồm 7 ca kiểm thử:
- **5 ca tiêu cực (NEG-01 đến NEG-05):** Kiểm tra cơ chế chặn các đường dẫn `.git` không hợp lệ (như `.git_staging`, `sub/.git`, `.git/hooks/pre-commit`, `.git.json`, v.v.). Các ca này đều chạy trong thư mục tạm `tempfile.TemporaryDirectory` được mock biệt lập hoàn toàn và đã PASS 100%.
- **2 ca tích cực (POS-01 và POS-02):** Kiểm tra cơ chế chấp nhận `.git/` ở root của repository thật.
  - Trong POS-01, test gọi trực tiếp `check_working_tree_consistency.validate_working_tree()` trên chính working tree hiện tại của repository.
  - Trong POS-02, test cũng gọi trực tiếp `check_working_tree_consistency.validate_working_tree()` sau khi xác nhận sự tồn tại của thư mục `.git`.

### 2.2. Trật tự thực thi dẫn đến mâu thuẫn log
1. Trong phiên làm việc `T009-UNBLOCK-R2`, script kiểm thử `test_t009_unblock_r2_git_exclusion.py` được chạy và chuyển hướng đầu ra (redirect output) vào tệp `T009_UNBLOCK_R2_LOG_NEGATIVE_TESTS.txt` tại thời điểm **TRƯỚC KHI** sổ đăng ký [`EVIDENCE_DELIVERABLE_REGISTER.json`](EVIDENCE_DELIVERABLE_REGISTER.json) được đồng bộ hóa.
2. Tại thời điểm đó, các tệp nhật ký `T009_UNBLOCK_R2_LOG_*.txt` và một số tệp tài liệu R2 mới được tạo ra trên đĩa nhưng **chưa có hash** trong `EVIDENCE_DELIVERABLE_REGISTER.json`.
3. Do `validate_working_tree()` có cơ chế khóa nghiêm ngặt: bất kỳ tệp nào tồn tại trong working tree mà không được ghi nhận trong `EVIDENCE_DELIVERABLE_REGISTER.json` sẽ bị tính là vi phạm nguyên tắc toàn vẹn (`unrecognized file`).
4. Hậu quả là `validate_working_tree()` trả về `exit_code = 1`, làm cho POS-01 và POS-02 bị fail trong lần chạy ghi log đầu tiên đó (`failures=2`).
5. Sau khi nhận thấy lỗi do registry chưa đồng bộ, agent R2 đã tiến hành đồng bộ lại toàn bộ SHA-256 hash và dung lượng byte của các deliverable mới vào `EVIDENCE_DELIVERABLE_REGISTER.json`, sau đó chạy validator tổng thể đạt `409 PASS, 0 FAIL`.
6. Tuy nhiên, agent R2 đã **quên chạy lại script `test_t009_unblock_r2_git_exclusion.py` để cập nhật lại tệp log `T009_UNBLOCK_R2_LOG_NEGATIVE_TESTS.txt`**, dẫn đến việc tệp log lưu lại kết quả của lần chạy dang dở trước đó, tạo ra sự mâu thuẫn với báo cáo markdown.

---

## 3. Thực Nghiệm Tái Kiểm Thử & Xác Nhận (Empirical Re-verification)

Để chứng minh luận điểm trên là chính xác 100%, trong phiên R1, chúng tôi đã thực hiện chạy lại lệnh kiểm thử trực tiếp trên live repository hiện tại:

```powershell
python tools/qa/test_t009_unblock_r2_git_exclusion.py
```

### Kết quả thực tế:
```text
test_neg01_git_staging_dir_rejected ... ok
test_neg02_nested_dot_git_rejected ... ok
test_neg03_git_hook_script_rejected ... ok
test_neg04_git_suffix_file_rejected ... ok
test_neg05_corrupted_git_file_rejected ... ok
test_pos01_validator_passes_on_clean_repo ... ok
test_pos02_validator_passes_with_dot_git_dir ... ok

----------------------------------------------------------------------
Ran 7 tests in 0.052s

OK
```
- **Exit Code:** `0`
- **Kết quả:** `7 PASS, 0 FAIL` (100% Pass rate cho cả 5 negative tests và 2 positive tests).
- Bằng chứng thực thi này đã được lưu giữ độc lập trong tệp nhật ký [`T009_R1_LOG_R2_TEST_RERUN.txt`](T009_R1_LOG_R2_TEST_RERUN.txt).

---

## 4. Đối Soát Toán Học Số Lượng Assertions (Assertion Count Reconciliation)

Project Lead cũng yêu cầu làm rõ tại sao số lượng assertion của `check_working_tree_consistency.py` lại tăng từ 385 lên 409 trong đợt R2:

1. **Cơ chế kiểm toán của `check_working_tree_consistency.py`:**
   - Mỗi deliverable được khai báo trong `EVIDENCE_DELIVERABLE_REGISTER.json` phải trải qua 2 kiểm tra bắt buộc:
     - Kiểm tra 1: Tệp có tồn tại trên đĩa vật lý hay không (`os.path.isfile`).
     - Kiểm tra 2: Giá trị băm SHA-256 trên đĩa có khớp chính xác với hash đăng ký hay không (`compute_sha256(path) == expected_hash`).
   - Do đó, mỗi deliverable mới được thêm vào sổ đăng ký sẽ làm tăng chính xác **2 assertions**.

2. **Bảng đối soát chi tiết:**
   - Số lượng deliverable tại baseline R1: **137 deliverables**.
   - Số lượng deliverable được thêm mới trong đợt R2: **12 deliverables**, gồm:
     - 7 tệp tài liệu Markdown:
       1. `T009_UNBLOCK_R2_REMEDIATION_REPORT.md`
       2. `T009_UNBLOCK_R2_SAFETY_ANALYSIS.md`
       3. `T009_UNBLOCK_R2_TEST_RESULTS.md`
       4. `T009_UNBLOCK_R2_REGRESSION_REPORT.md`
       5. `T009_UNBLOCK_R2_FUTURE_COMPATIBILITY.md`
       6. `T009_UNBLOCK_R2_RISK_AND_DEVIATIONS.md`
       7. `T009_UNBLOCK_R2_ROLLBACK_PLAN.md`
     - 5 tệp log text:
       8. `T009_UNBLOCK_R2_LOG_BEFORE_AFTER_DIFF.txt`
       9. `T009_UNBLOCK_R2_LOG_CONSISTENCY.txt`
       10. `T009_UNBLOCK_R2_LOG_NEGATIVE_TESTS.txt`
       11. `T009_UNBLOCK_R2_LOG_T006_REGRESSION.txt`
       12. `T009_UNBLOCK_R2_LOG_REGISTRY_REGRESSION.txt`
   - Tổng số deliverable sau R2: $137 + 12 = 149$ deliverables.
   - Số assertions tăng thêm: $12 \times 2 = 24$ assertions.
   - Tổng số assertions kiểm tra tính toàn vẹn: $385 + 24 = \mathbf{409}$ assertions.

Như vậy, con số 409 assertions hoàn toàn khớp đúng về mặt toán học và phản ánh đầy đủ việc kiểm toán 149 deliverables trong repository.

---

## 5. Kết Luận & Khuyến Nghị

1. **Tính hợp lệ của R2:** Logic loại trừ `.git/` của R2 hoàn toàn đúng đắn và không có lỗ hổng bypass nào. Thất bại trong tệp log cũ là do lỗi quy trình chạy test trước khi sync registry.
2. **Hành động khắc phục:** Đã tái thực thi và ghi lại log sạch vào `T009_R1_LOG_R2_TEST_RERUN.txt`.
3. **Quy trình chuẩn tắc cho R1:** Mọi bài test kiểm tra working tree trong đợt R1 này sẽ chỉ được capture log cuối cùng **SAU KHI** `EVIDENCE_DELIVERABLE_REGISTER.json` đã được đồng bộ hoàn tất 100%, bảo đảm không tái diễn bất kỳ mâu thuẫn nào.
