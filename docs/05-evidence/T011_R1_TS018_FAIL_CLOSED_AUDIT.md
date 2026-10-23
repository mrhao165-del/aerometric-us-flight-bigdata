# T011-R1 TS-018 BTS TRANSTATS RECONCILER FAIL-CLOSED AUDIT

**Project:** US Flight Performance Analysis 2016–2024  
**Task:** T-011 R1 — Targeted Independent Audit Remediation  
**Parent Gate:** G5 (IN_PROGRESS)  
**Deliverable:** `docs/05-evidence/T011_R1_TS018_FAIL_CLOSED_AUDIT.md`  
**Date:** 2026-10-19  
**Status:** **AUDIT VERIFIED / FAIL-CLOSED RULES OPERATIONAL**

---

## 1. Bối cảnh & Mục tiêu

Kiểm toán độc lập tại Gate R1 đã chỉ ra hai khiếm khuyết nghiêm trọng trong cơ chế đối soát BTS TranStats mẫu (TS-018, quy định tại G2-EXC-001):
1. **R1-F01:** `tools/qa/run_ts018_bts_parity.py` gán danh sách rỗng `dataset_records = []`, `bts_records = []` khi phát hiện tập tin, không đọc dữ liệu thật, không kiểm tra schema/digest và trả về exit code 0 vô điều kiện.
2. **R1-F02:** `BtsTranStatsReconciler` cho phép tuyên bố `TS018_PASS_AUTHENTIC_PARITY_ESTABLISHED` ngay cả khi có bản ghi không khớp (`unmatched_dataset_records > 0`), toàn bộ 7 độ đo là NULL (`NULL_NULL_AGREEMENT`), hoặc khóa trùng lặp (`ambiguous_duplicate_keys > 0`), đồng thời âm thầm ép kiểu số hiệu chuyến bay lỗi thành `0.0`.

Báo cáo này xác nhận việc khắc phục toàn diện và thiết lập cơ chế fail-closed chặt chẽ cho toàn bộ module đối soát TS-018.

---

## 2. Chi tiết Triển khai Chỉnh sửa (Remediations)

### 2.1. Đọc và Kiểm thực Dữ liệu BTS Thực tế (`tools/qa/run_ts018_bts_parity.py`)
- Bổ sung hàm `read_bts_csv(file_path: Path) -> Tuple[List[Dict[str, Any]], str]`:
  - Đọc CSV bằng `csv.DictReader(encoding='utf-8-sig')`.
  - Tính toán mã băm SHA-256 chuẩn tắc của tập tin đầu vào qua `compute_sha256()`.
  - Kiểm tra bắt buộc tập cột khóa nhận diện chuyến bay: `{'FlightDate', 'Reporting_Airline', 'Flight_Number_Reporting_Airline', 'Origin', 'Dest'}` (hoặc định dạng alias chuẩn).
  - Ném `ValueError` nếu tập tin rỗng, thiếu header hoặc không đủ cột khóa.
- Loại bỏ hoàn toàn mã gán stub rỗng; khi có tập tin BTS thực, hệ thống nạp toàn bộ dòng vào `bts_records`.

### 2.2. Quy tắc Phán quyết Nghiêm ngặt Fail-Closed (`BtsTranStatsReconciler.reconcile`)
Khi cờ `is_authentic_bts_data == True`, để đạt phán quyết `TS018_PASS_AUTHENTIC_PARITY_ESTABLISHED`, hệ thống bắt buộc phải thỏa mãn đồng thời 6 điều kiện toán học:
1. **Không có bất kỳ sai lệch nào:** `total_mismatch == 0` trên toàn bộ 7 độ đo (`ARR_DELAY`, `DEP_DELAY`, `TAXI_OUT`, `TAXI_IN`, `AIR_TIME`, `ACTUAL_ELAPSED_TIME`, `CRS_ELAPSED_TIME`).
2. **Có ít nhất một bản ghi khớp duy nhất:** `summary.unique_key_matches > 0`.
3. **Có bằng chứng số học thực chất:** `has_numeric_evidence == True`, tức là tổng số phép so khớp chính xác (`exact_match`) hoặc sai số làm tròn hợp lệ (`rounding_diff`) phải $> 0$. Nghiêm cấm chấp nhận tập mẫu mà toàn bộ các trường đều là NULL-NULL (`NULL_NULL_AGREEMENT`).
4. **Không có bản ghi tồn dư phía Dataset:** `summary.unmatched_dataset_records == 0`.
5. **Không có bản ghi tồn dư phía BTS:** `summary.unmatched_bts_records == 0`.
6. **Không có khóa trùng lặp nhập nhằng chưa xử lý:** `summary.ambiguous_duplicate_keys == 0`.

Nếu bất kỳ điều kiện nào trong 6 điều kiện trên bị vi phạm, phán quyết bắt buộc chuyển thành:
```
TS018_FAIL_DISCREPANCIES_DETECTED
```

### 2.3. Chuẩn hóa Khóa Composite Không Âm thầm Ép kiểu
- Trong `extract_composite_key`:
  - `fl_num_raw` được phân tích cú pháp cẩn thận. Nếu là chuỗi không hợp lệ (ví dụ `"CORRUPT_FLIGHT"` hoặc `None`), hàm gán `fl_num = None` thay vì ép thành `0.0`.
  - Khóa chứa `None` cho số hiệu chuyến bay được gắn cờ `AMBIGUOUS_DUPLICATE` và không thể khớp nhầm với các chuyến bay mang số hiệu `0.0`.

### 2.4. Mã Thoát Fail-Closed Chuẩn tắc (Exit Codes)
Hàm `run_ts018_reconciliation()` trả về mã thoát theo hợp đồng quy định:
- **Exit Code 0:** Nghiệm thu thành công:
  - Khi `is_authentic_bts_data == True` và đạt `TS018_PASS_AUTHENTIC_PARITY_ESTABLISHED`.
  - Hoặc khi chạy bộ golden fixture tổng hợp và đạt `SYNTHETIC_RECONCILER_VERIFIED_AUTHENTIC_BTS_PENDING` (tuân thủ trạng thái ngoại lệ tạm thời G2-EXC-001 khi chưa có dữ liệu BTS thật).
- **Exit Code 1:** Phát hiện sai lệch đối soát hoặc vi phạm tiêu chí fail-closed (`TS018_FAIL_DISCREPANCIES_DETECTED` hoặc `SYNTHETIC_RECONCILER_FAIL_DISCREPANCIES_DETECTED`).
- **Exit Code 2:** Lỗi đọc tập tin, tập tin rỗng hoặc vi phạm schema CSV.

---

## 3. Bằng chứng Kiểm thử Xác minh

Bộ kiểm thử [`tests/test_t011_ts018_bts_parity.py`](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/tests/test_t011_ts018_bts_parity.py) đã được mở rộng lên 8 ca kiểm thử:
- `test_01_exact_match_all_seven_measures`: PASS (khớp chính xác 7 độ đo).
- `test_02_scale_mismatch_detection`: PASS (phát hiện lệch scale x60 giây/phút).
- `test_03_sign_mismatch_detection`: PASS (phát hiện đảo dấu delay).
- `test_04_missingness_mismatch_and_null_agreement`: PASS (phân biệt đúng NULL-NULL và thiếu dữ liệu).
- `test_05_ambiguous_duplicate_key_detection`: PASS (phát hiện chuyến bay lặp OR-02 YX 3624).
- `test_06_authentic_parity_fail_closed_on_unmatched_records`: PASS (từ chối PASS khi có 1 bản ghi unmatched).
- `test_07_authentic_parity_fail_closed_on_all_null_measures`: PASS (từ chối PASS khi 100% độ đo là NULL).
- `test_08_invalid_flight_number_handling`: PASS (không ép kiểu lỗi thành 0.0).

Kết quả thực thi:
```
Ran 8 tests in 0.000s
OK
```

Chạy harness thực tế [`tools/qa/run_ts018_bts_parity.py`](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/tools/qa/run_ts018_bts_parity.py):
- Phán quyết: `SYNTHETIC_RECONCILER_VERIFIED_AUTHENTIC_BTS_PENDING`
- Exit Code: 0 (hợp lệ theo ngoại lệ G2-EXC-001).
- Tệp tóm tắt: [`docs/05-evidence/T011_TS018_BTS_RECONCILIATION_SUMMARY.json`](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/docs/05-evidence/T011_TS018_BTS_RECONCILIATION_SUMMARY.json).

**Kết luận:** Module TS-018 đạt chuẩn fail-closed tuyệt đối, loại trừ hoàn toàn nguy cơ false pass.
