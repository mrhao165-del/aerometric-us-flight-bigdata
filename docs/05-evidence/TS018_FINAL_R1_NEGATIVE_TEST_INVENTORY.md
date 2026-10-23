# TS018_FINAL_R1_NEGATIVE_TEST_INVENTORY.md
# Danh Mục Kiểm Thử Tiêu Cực Và Ma Trận Đột Biến Lỗi TS-018

**Dự án:** US Flight Performance Analysis 2016–2024  
**Nhiệm vụ:** TS-018 Final Evidence Integrity Review (R1 Correction)  
**Tác giả:** Senior PySpark QA Engineer, Reliability & Fault Injection Specialist  
**Ngày lập:** 2026-10-20  
**Tệp thực thi:** [tools/qa/test_ts018_negative_witness_verification.py](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/tools/qa/test_ts018_negative_witness_verification.py)

---

## 1. NGUYÊN TẮC THỰC HIỆN KIỂM THỬ TIÊU CỰC
1. **Cô lập tuyệt đối:** Chạy trong thư mục tạm `tempfile.TemporaryDirectory()`, không sửa đổi bất kỳ tệp dữ liệu thô hoặc tệp witness vật lý nào.
2. **Fail-Closed có chủ đích:** Mỗi lỗi tiêm vào (mutation) phải kích hoạt đúng cơ chế phòng vệ chuyên biệt, trả về mã lỗi khác 0 (`exit=1`) và xuất đúng thông điệp lỗi mục tiêu.
3. **Khớp 1-1 giữa mã nguồn và tài liệu:** Tên gọi, mô tả kịch bản, hành động sửa đổi dữ liệu (mutation) và điều kiện khẳng định (assertion) phải đồng nhất tuyệt đối.

---

## 2. BẢNG MA TRẬN 10 KỊCH BẢN ĐỘT BIẾN LỖI (NEGATIVE FAULT INJECTION INVENTORY)

| Mã Test | Tên kịch bản | Hành động đột biến dữ liệu thực tế (Actual Mutation) | Cơ chế kiểm tra mục tiêu | Kết quả / Mã thoát | Thông điệp lỗi ghi nhận |
| :---: | :--- | :--- | :--- | :---: | :--- |
| **NEG-W01** | Giá trị số trong witness bị lệch lớn | Đổi `RAW_DATASET_ARR_DELAY` của dòng 1 từ `-6.0` thành `-999.0` | Đối soát dữ liệu thô CSV | **PASS** (`exit=1`) | `mismatches between raw CSV and witness` |
| **NEG-W02** | Khóa chuyến bay không tồn tại | Đổi khóa định danh thành `2019-01-01|ZZ|9999|XYZ|ZZZ` | Kiểm tra tồn tại khóa trong CSV | **PASS** (`exit=1`) | `missing from raw CSV` |
| **NEG-W03** | Tệp witness bị hỏng cấu trúc byte | Nối thêm dòng byte rác `\nEXTRA_CORRUPT_TRAILING_LINE\n` | Kiểm tra toàn vẹn tệp và băm SHA-256 | **PASS** (`exit=1`) | `checksum mismatch` / `corrupted` |
| **NEG-W04** | Đảo dấu giá trị độ trễ đến | Đổi `ARR_DELAY` của chuyến bay `NK 314` từ `-6.0` thành `+6.0` | Đối soát dấu đại số với nguồn CSV | **PASS** (`exit=1`) | `mismatches between raw CSV and witness` |
| **NEG-W05** | Trùng lặp khóa (Duplicate Key) | Sao chép dòng 0 đè lên dòng 1 (tổng số khóa duy nhất còn 1.499) | Ràng buộc duy nhất 1.500 khóa | **PASS** (`exit=1`) | `Expected exactly 1500 witness records` |
| **NEG-W06** | Giá trị dương bị ép thành 0.0 | Đổi `TAXI_OUT` từ `13.0` thành `0.0` | Đối soát số học với nguồn CSV | **PASS** (`exit=1`) | `mismatches between raw CSV and witness` |
| **NEG-W07** | Bơm sai số nhỏ trong dung sai (+0.00005) | Đổi `ARR_DELAY` từ `-6.0` thành `-5.99995` (chênh lệch $0.00005 \le 10^{-4}$) | Chế độ nghiệm thu nghiêm ngặt `REQUIRE_STRICT_EXACT` | **PASS** (`exit=1`) | `TOL_ONLY` / `Strict exact mode violation` |
| **NEG-W08** | Bất đồng Null vs Giá trị thật | Xóa giá trị `AIR_TIME` thành chuỗi rỗng `""` trong khi BTS là `98.0` | Phát hiện bất đồng giá trị null | **PASS** (`exit=1`) | `mismatches between raw CSV and witness` |
| **NEG-W09** | Bơm ký tự không hữu hạn (`NaN`) | Ghi chuỗi `"NaN"` vào cột `CRS_ELAPSED_TIME` | Kiểm tra giá trị không hữu hạn IEEE-754 | **PASS** (`exit=1`) | `mismatches between raw CSV and witness` |
| **NEG-W10** | Tráo đổi ngày bay của chuyến bay thật | Đổi ngày của `NK 314` từ `2019-01-10` thành `2019-01-20` nhưng giữ nguyên số liệu ngày 10 | Bắt lỗi chênh lệch số liệu thực tế theo ngày | **PASS** (`exit=1`) | `mismatches between raw CSV and witness` |

---

## 3. KẾT QUẢ THỰC THI THỰC TẾ
Lệnh chạy kiểm thử độc lập:
```powershell
python tools/qa/test_ts018_negative_witness_verification.py
```
Nhật ký thực thi tiêu chuẩn (Stdout):
```text
================================================================================
RUNNING TS-018 COMPREHENSIVE NEGATIVE WITNESS FAULT INJECTION TEST SUITE
================================================================================
[PASS] NEG-W01: Injected value mismatch in witness (-999.0 vs real) is caught fail-closed -> exit=1
[PASS] NEG-W02: Non-existent flight key in witness is caught fail-closed -> exit=1
[PASS] NEG-W03: Corrupted witness byte content is rejected fail-closed -> exit=1
[PASS] NEG-W04: Slipped sign on arrival delay (-6.0 -> +6.0) is caught fail-closed -> exit=1
[PASS] NEG-W05: Duplicate key collision in witness (resulting in <1500 distinct keys) is caught -> exit=1
[PASS] NEG-W06: Non-zero numeric measure replaced with 0.0 is caught fail-closed -> exit=1
[PASS] NEG-W07: Tolerance-only deviation (+0.00005) under strict exact check is caught fail-closed -> exit=1
[PASS] NEG-W08: Genuine null-to-value disagreement on AIR_TIME is caught fail-closed -> exit=1
[PASS] NEG-W09: Non-finite numeric value ('NaN') is caught fail-closed -> exit=1
[PASS] NEG-W10: Flight date mismatch (2019-01-10 mutated to 2019-01-20) is caught fail-closed -> exit=1
================================================================================
NEGATIVE TEST SUITE SUMMARY: 10 PASS, 0 FAIL (Total: 10)
================================================================================
```
Mã thoát tiến trình: **`0`** (Tất cả 10/10 kịch bản tiêu cực đều bị chặn đứng thành công).
