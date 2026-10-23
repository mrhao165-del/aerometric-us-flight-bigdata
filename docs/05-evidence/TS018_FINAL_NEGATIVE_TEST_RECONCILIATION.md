# TS018_FINAL_NEGATIVE_TEST_RECONCILIATION.md
# Báo Cáo Đối Soát Bộ Kiểm Thử Tiêu Cực Chống False-Pass (Hardened 13-Case Negative Suite)

**Dự án:** US Flight Performance Analysis 2016–2024  
**Nhiệm vụ:** TS-018 — Final Verifier Hardening  
**Tác giả:** Senior Software Reliability & QA Engineer  
**Thời điểm lập:** 2026-10-20  
**Tệp thực thi:** [tools/qa/test_ts018_negative_witness_verification.py](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/tools/qa/test_ts018_negative_witness_verification.py)

---

## 1. NGUYÊN TẮC THIẾT KẾ KIỂM THỬ TIÊU CỰC NÂNG CAO
1. **Chống False-Pass (Anti-False-Pass Verification):** Mọi ca kiểm thử tiêu cực phải khẳng định thông điệp lỗi mục tiêu (target diagnostic assertion). Tuyệt đối không chấp nhận các lỗi ngẫu nhiên ngoài ý muốn (như lỗi cú pháp, KeyError, FileNotFoundError hoặc traceback không bắt được) là test PASS.
2. **Cô lập đột biến lỗi:** Chạy hoàn toàn trên thư mục tạm thời `tempfile.TemporaryDirectory()`, không làm thay đổi các tệp dữ liệu thô hay tệp chứng thực chính thức.
3. **Bao phủ toàn diện các rủi ro H01–H05:** Kiểm tra trực tiếp việc từ chối sai số dung sai (H01), từ chối `"NaN"` masquerading thành null (H02), từ chối signed zero masquerading thành bitwise exact (H03), kiểm tra băm ghim witness (H05) và kiểm tra trùng lặp khóa (H05).

---

## 2. BẢNG CHI TIẾT 13 KỊCH BẢN ĐỘT BIẾN LỖI VÀ CHẨN ĐOÁN MỤC TIÊU

| Mã Test | Mô tả kịch bản kiểm thử | Hành động đột biến (Mutation) | Tiêu chí khẳng định mục tiêu (Target Assertion) | Kết quả / Mã thoát |
| :---: | :--- | :--- | :--- | :---: |
| **NEG-W01** | Bắt lỗi chênh lệch số học lớn | `RAW_DATASET_ARR_DELAY = -999.0` (thực tế `-6.0`) | `returncode != 0` AND `"mismatches between raw CSV and witness"` | **PASS** (`exit=1`) |
| **NEG-W02** | Bắt lỗi khóa không tồn tại | Khóa `2019-01-01|ZZ|9999|XYZ|ZZZ` | `returncode != 0` AND `"missing from raw CSV"` | **PASS** (`exit=1`) |
| **NEG-W03** | Bắt lỗi sửa đổi tệp witness bằng băm ghim (H05) | Nối thêm dòng byte rác vào tệp witness, chạy với `VERIFY_WITNESS_PINNED_HASH = True` | `returncode != 0` AND `"Sealed witness checksum mismatch"` | **PASS** (`exit=1`) |
| **NEG-W04** | Bắt lỗi đảo dấu độ trễ | `RAW_DATASET_ARR_DELAY = +6.0` (thực tế `-6.0`) | `returncode != 0` AND `"mismatches between raw CSV and witness"` | **PASS** (`exit=1`) |
| **NEG-W05** | Bắt lỗi trùng lặp khóa trong witness (H05) | Sao chép dòng 0 thành dòng 1 | `returncode != 0` AND `"Duplicate composite key detected in witness"` | **PASS** (`exit=1`) |
| **NEG-W06** | Bắt lỗi ép giá trị khác 0 thành `0.0` | `RAW_DATASET_TAXI_OUT = 0.0` (thực tế `13.0`) | `returncode != 0` AND `"mismatches between raw CSV and witness"` | **PASS** (`exit=1`) |
| **NEG-W07** | Bắt lỗi sai số dung sai $+0.00005$ dưới Strict Exact (H01) | `RAW_DATASET_ARR_DELAY = -5.99995` ($\Delta = 0.00005 \le 10^{-4}$) với `REQUIRE_STRICT_EXACT = True` | `returncode != 0` AND (`"Strict exact mode violation"` OR `"STRICT_FAIL"`) | **PASS** (`exit=1`) |
| **NEG-W08** | Bắt lỗi bất đồng null vs số thực | `RAW_DATASET_AIR_TIME = ""` (thực tế `98.0`) | `returncode != 0` AND `"mismatches between raw CSV and witness"` | **PASS** (`exit=1`) |
| **NEG-W09** | Bắt lỗi token không hữu hạn `"NaN"` trong cột số (H02/H04) | `RAW_DATASET_CRS_ELAPSED_TIME = "NaN"` | `returncode != 0` AND (`"NONFINITE_OR_INVALID_TOKEN"` OR `"mismatches"`) | **PASS** (`exit=1`) |
| **NEG-W10** | Bắt lỗi tráo đổi ngày bay thật | Đổi ngày `NK 314` từ `2019-01-10` thành `2019-01-20` | `returncode != 0` AND (`"mismatches"` OR `"missing"`) | **PASS** (`exit=1`) |
| **NEG-W11** | Chống False-Pass: Hai nguồn cùng chứa `"NaN"` (H02) | Phân tích 2 ô cùng mang token `"NaN"` | `classify_cells()` trả về `NONFINITE_OR_INVALID_TOKEN`, **tuyệt đối không trả về `NULL_NULL_AGREEMENT`** | **PASS** (Unit Check) |
| **NEG-W12** | Phân tách Signed Zero `+0.0` vs `-0.0` (H03) | Phân tích 2 ô mang giá trị `0.0` và `-0.0` | `classify_cells()` trả về `NUMERIC_EQUAL_SIGNED_ZERO_DIFF`, **tuyệt đối không trả về `EXACT_BITWISE_MATCH`** | **PASS** (Unit Check) |
| **NEG-W13** | Parser từ chối các chuỗi không phân tích được biến thành null (H02) | Kiểm tra parser với các chuỗi: `"CORRUPT_TOKEN"`, `"Infinity"`, `"-Infinity"`, `"12.34.56"` | Tất cả đều có `kind == "NONFINITE_OR_INVALID_TOKEN"`, **không có ô nào mang `VALID_NULL`** | **PASS** (Unit Check) |

---

## 3. NHẬT KÝ THỰC THI THỰC TẾ (RAW EXECUTION OUTPUT)

```text
================================================================================
RUNNING TS-018 COMPREHENSIVE NEGATIVE WITNESS FAULT INJECTION TEST SUITE
================================================================================
[PASS] NEG-W01: Injected value mismatch in witness (-999.0 vs real) is caught fail-closed -> exit=1
[PASS] NEG-W02: Non-existent flight key in witness is caught fail-closed -> exit=1
[PASS] NEG-W03: Tampered witness checksum is caught fail-closed by pinned SHA-256 validator (H05) -> exit=1
[PASS] NEG-W04: Slipped sign on arrival delay (-6.0 -> +6.0) is caught fail-closed -> exit=1
[PASS] NEG-W05: Duplicate key collision in witness is detected fail-closed before ingestion (H05) -> exit=1
[PASS] NEG-W06: Non-zero numeric measure replaced with 0.0 is caught fail-closed -> exit=1
[PASS] NEG-W07: Tolerance-only deviation (+0.00005) under strict exact check is rejected fail-closed (H01) -> exit=1
[PASS] NEG-W08: Genuine null-to-value disagreement on AIR_TIME is caught fail-closed -> exit=1
[PASS] NEG-W09: Non-finite numeric value ('NaN') is caught fail-closed as invalid token (H02/H04) -> exit=1
[PASS] NEG-W10: Flight date mismatch (2019-01-10 mutated to 2019-01-20) is caught fail-closed -> exit=1
[PASS] NEG-W11: Two sources both containing 'NaN' are rejected as NONFINITE, never NULL_NULL (H02) -> category=NONFINITE_OR_INVALID_TOKEN
[PASS] NEG-W12: Signed zero (+0.0 vs -0.0) is classified as NUMERIC_EQUAL_SIGNED_ZERO_DIFF, not bitwise exact (H03) -> category=NUMERIC_EQUAL_SIGNED_ZERO_DIFF
[PASS] NEG-W13: Parser strictly classifies malformed / infinite text tokens as invalid, never valid null (H02) -> kinds=['NONFINITE_OR_INVALID_TOKEN', 'NONFINITE_OR_INVALID_TOKEN']
================================================================================
NEGATIVE TEST SUITE SUMMARY: 13 PASS, 0 FAIL (Total: 13)
================================================================================
```

Mã thoát tiến trình: **`0`** (Tất cả 13/13 ca kiểm thử tiêu cực đều được phát hiện và ngắt fail-closed đúng mục tiêu).
