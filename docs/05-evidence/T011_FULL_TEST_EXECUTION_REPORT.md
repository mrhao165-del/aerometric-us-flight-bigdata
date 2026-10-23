# T011_FULL_TEST_EXECUTION_REPORT — BÁO CÁO TỔNG HỢP KẾT QUẢ THỰC THI KIỂM THỬ VÀ QA VERIFIERS

- **Mã nhiệm vụ:** `T-011` (Gate G5: KPI Sample Smoke, BTS Parity, TS-008, TS-013 & Review Packaging)
- **Gate:** `G5` (IN_PROGRESS)
- **Thời điểm kiểm toán:** 2026-10-18T21:04:30+07:00
- **Tiêu chuẩn tuân thủ:** [`AGENTS.md`](../../AGENTS.md), Master Execution Prompt T-011 Mục 10.1.
- **Trạng thái:** **ALL UNITTESTS & VERIFIERS PASS (205/205 Tests OK)**

---

## 1. BẢNG TỔNG HỢP CÁC LỆNH KIỂM THỬ ĐÃ THỰC THI

| STT | Lệnh thực thi chính xác | Thư mục làm việc | Thời gian thực thi | Mã thoát (Exit Code) | Số lượng test / Khẳng định | Kết quả | Tệp log bằng chứng |
|:---:|---|---|---:|:---:|:---:|:---:|---|
| 1 | `python -m unittest discover -s tests -p "test_*.py"` | Repo root | 337.34s | `0` | **205 tests** | **205 PASS, 0 FAIL** | `T011_FULL_LOG_UNITTEST_SUITE.txt` |
| 2 | `python tools/qa/verify_g2_repo_apply_r1_semantic_invariants.py` | Repo root | 2.12s | `0` | 15 invariants + 15 mutations | **30 PASS, 0 FAIL** | `T011_FULL_LOG_QA_VERIFIERS.txt` |
| 3 | `python tools/qa/verify_t006_contract_consistency.py` | Repo root | 2.35s | `0` | 17 invariants + 16 mutations | **33 PASS, 0 FAIL** | `T011_FULL_LOG_QA_VERIFIERS.txt` |
| 4 | `python tools/qa/verify_t010_parquet_schema_attestation.py` | Repo root | 1.84s | `0` | 50 physical parquet files | **50/50 ATTESTED, 0 FAIL** | `T011_FULL_LOG_QA_VERIFIERS.txt` |
| 5 | `python tools/qa/run_ts018_bts_parity.py` | Repo root | 0.45s | `0` | 7 core measures parity check | **PASS (Technical Level)** | `T011_TS018_BTS_RECONCILIATION_SUMMARY.json` |
| 6 | `python tools/qa/run_t011_kpi_smoke.py` | Repo root | 41.20s | `0` | Multi-dimensional KPI smoke | **PASS (12 year + 24 carrier)** | `T011_KPI_SAMPLE_SMOKE_METRICS.json` |

---

## 2. CHI TIẾT CÁC TEST SUITE MỚI THUỘC T-011

Trong phạm vi T-011, 4 bộ kiểm thử chuyên sâu mới (tổng cộng 24 tests mới) đã được bổ sung và tích hợp vào kho lưu trữ:

### 2.1. `tests/test_t011_kpi_engine.py` (7 tests — 100% PASS)
- `test_01_synthetic_oracle_parity_clean_data`: Đối soát 12 lát cắt KPI với Python Oracle.
- `test_02_negative_delays_preserved_in_signed_means`: Bảo toàn dấu âm trong mean signed ARR_DELAY và DEP_DELAY.
- `test_03_exact_15_minute_boundary`: Kiểm chứng điểm biên trễ đúng $15.0$ phút.
- `test_04_zero_metric_denominator_safety`: Trả về SQL NULL và `ZERO_METRIC_DENOMINATOR` khi mẫu số bằng 0.
- `test_05_independent_denominators_kpi07_and_kpi08`: Mẫu số hoàn toàn độc lập giữa các submetrics taxi và elapsed.
- `test_06_min_n_threshold_boundaries`: Kiểm tra chính xác các điểm biên min-N cho carrier-year, airport-year, route-year.
- `test_07_year_2024_partial_coverage_metadata`: Gán nhãn `PARTIAL` cho năm 2024.

### 2.2. `tests/test_t011_ts008_repeatability.py` (4 tests — 100% PASS)
- `test_01_gk_sketch_rank_error_on_skewed_distribution`: Đo sai số thứ hạng phân vị trên 5,000 điểm dữ liệu lệch đuôi nặng.
- `test_02_ts012_deterministic_repeatability`: Tính lặp lại tất định 100% giữa nhiều lượt chạy.
- `test_03_tied_values_and_extreme_outliers`: Xử lý giá trị trùng lặp (50 bản ghi 15.0 min) và cực trị (+4,405.0 min).
- `test_04_null_and_nan_inf_exclusion_from_quantiles`: Cách ly các giá trị không hữu hạn.

### 2.3. `tests/test_t011_fault_injection.py` (8 tests — 100% PASS)
- Kiểm chứng 8 kịch bản lỗi lưu trữ F01..F08 trong sandbox cô lập.
- Chứng minh cơ chế khóa Win32 atomic và rollback phi phá hủy phục hồi nguyên vẹn con trỏ xuất bản.

### 2.4. `tests/test_t011_ts018_bts_parity.py` (5 tests — 100% PASS)
- `test_01_exact_match_all_seven_measures`: Khớp hoàn hảo 7 trường đo CORE trên khóa composite.
- `test_02_scale_mismatch_detection`: Phát hiện sai lệch hệ đo theo tỷ lệ (giây vs phút).
- `test_03_sign_mismatch_detection`: Phát hiện sai lệch dấu độ trễ.
- `test_04_missingness_mismatch_and_null_agreement`: Phân biệt thỏa hiệp null-null với thiếu dữ liệu một phía.
- `test_05_ambiguous_duplicate_key_detection`: Phát hiện và gắn nhãn khóa trùng lặp mơ hồ.

---

## 3. KẾT LUẬN THỰC THI KIỂM THỬ

Toàn bộ **205/205 unittests** của kho lưu trữ và các bộ kiểm chuẩn QA verifiers đều đạt kết quả **PASS 100%**, không có bất kỳ lỗi hồi quy hay cảnh báo rủi ro kỹ thuật nào.
