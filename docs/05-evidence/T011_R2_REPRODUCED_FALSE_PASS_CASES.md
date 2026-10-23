# T011_R2_REPRODUCED_FALSE_PASS_CASES — Báo cáo Tái lập Phản ví dụ và Lỗi Kỹ thuật Trước khi Khắc phục

**Dự án:** Phân tích Hiệu suất Bay Hoa Kỳ 2016–2024 (US Flight Performance Analysis 2016–2024)  
**Nhiệm vụ:** `T-011 R2 — Targeted Parity Hardening and Evidence Correction`  
**Cổng nội bộ:** `Gate R2-1 — Defect Reproduction and Negative Testing`  
**Tệp kiểm thử tái lập:** [`tests/test_t011_r2_counterexamples.py`](../../tests/test_t011_r2_counterexamples.py)  
**Kết quả thực thi:** `Ran 5 tests in 0.038s OK` — Cả 5 kịch bản phản ví dụ đều xác nhận sự tồn tại của lỗi trên baseline R1.

---

## 1. MỤC TIÊU VÀ NGUYÊN TẮC KIỂM THỬ TÁI LẬP

Trước khi thực hiện bất kỳ sửa đổi nào trên mã nguồn sản xuất, quy trình an toàn bắt buộc tại Gate R2-1 là:
1. Xây dựng các ca kiểm thử tái lập độc lập mô phỏng chính xác các phản ví dụ mà kiểm toán viên độc lập đã phát hiện.
2. Chứng minh cụ thể hành vi lỗi trên mã nguồn tiền nhiệm R1.
3. Ghi nhận chi tiết kết quả thực tế, đường dẫn mã nguồn bị ảnh hưởng và cơ chế gây lỗi.

---

## 2. CHI TIẾT TÁI LẬP 5 PHÁT HIỆN KIỂM TOÁN ĐỘC LẬP

### 2.1. Tái lập R2-F01 — False Authentic BTS Parity via Caller Boolean
- **Ca kiểm thử:** `test_repro_r2_f01_local_file_false_authentic_parity`
- **Cơ chế gây lỗi:**
  - Trong `tools/qa/run_ts018_bts_parity.py` (dòng 87): Khi tìm thấy tệp `bts_transtats_sample.csv`, runner lập tức gán `is_authentic = True`.
  - Trong `src/flight_pipeline/kpi/bts_reconciler.py` (dòng 329): Reconciler chỉ kiểm tra `is_authentic_bts_data` dưới dạng boolean. Nếu boolean này là `True`, reconciler không thực hiện bất kỳ kiểm tra xuất xứ nào mà lập tức phát hành kết luận:
    `TS018_PASS_AUTHENTIC_PARITY_ESTABLISHED`.
- **Bằng chứng tái lập:** Hai tập dữ liệu hoàn toàn do mã kiểm thử tạo cục bộ không có siêu dữ liệu xuất xứ (provenance) vẫn nhận được phán quyết nghiệm thu chính thức `TS018_PASS_AUTHENTIC_PARITY_ESTABLISHED`.
- **Hành vi bắt buộc sửa đổi:** Thiết lập hợp đồng xuất xứ `BtsProvenanceValidator`. Nếu không có hồ sơ xuất xứ chuẩn tắc kèm phê duyệt của Project Lead, hệ thống bắt buộc từ chối và trả về `PENDING/BLOCKED`.

---

### 2.2. Tái lập R2-F02 — Incomplete Seven-Field Validation
- **Ca kiểm thử:** `test_repro_r2_f02_single_measure_passes_when_six_measures_absent`
- **Cơ chế gây lỗi:**
  - Trong `src/flight_pipeline/kpi/bts_reconciler.py` (dòng 269–271): Reconciler dùng `d_rec.get(core_field)` và `b_rec.get(bts_col)`. Khi cột bị thiếu hoàn toàn khỏi bản ghi, cả hai hàm `.get()` đều trả về `None`.
  - Hàm `compare_single_field` phân loại cặp `(None, None)` là `MismatchType.NULL_NULL_AGREEMENT`.
  - Dòng 299: `has_numeric_evidence = (total_exact + total_rounding) > 0`. Điều này cho phép chỉ cần đúng 1 trường số đo có số liệu (ví dụ `ARR_DELAY = 10.0`) là biến `has_numeric_evidence` trở thành `True`.
- **Bằng chứng tái lập:** Bản ghi khuyết 6 trên 7 trường số đo (`DEP_DELAY`, `TAXI_OUT`, `TAXI_IN`, `AIR_TIME`, `ACTUAL_ELAPSED_TIME`, `CRS_ELAPSED_TIME`) vẫn đạt `exact=1` và nhận phán quyết nghiệm thu chính thức `TS018_PASS_AUTHENTIC_PARITY_ESTABLISHED`.
- **Hành vi bắt buộc sửa đổi:** Phân biệt rõ giữa cột vắng mặt trong schema (`SCHEMA_MISSING_COLUMN`) với cột có mặt mang giá trị null. Yêu cầu **tất cả 7 trường số đo CORE** đều phải có quan sát số học độc lập (`numeric_sample_count > 0`).

---

### 2.3. Tái lập R2-F03A — Flight Number Zero Masked by 'or' Syntax
- **Ca kiểm thử:** `test_repro_r2_f03a_flight_number_zero_masked_by_or`
- **Cơ chế gây lỗi:**
  - Trong `extract_composite_key`: Biểu thức `rec.get("OP_CARRIER_FL_NUM") or rec.get("Flight_Number_Reporting_Airline")`.
  - Trong Python, số `0` hoặc `0.0` được đánh giá là Falsy trong ngữ cảnh toán tử `or`.
- **Bằng chứng tái lập:** Khi một bản ghi có `OP_CARRIER_FL_NUM = 0` và alias dự phòng `Flight_Number_Reporting_Airline = 999`, biểu thức `or` đã vô tình bỏ qua giá trị `0` hợp lệ và chọn nhầm `999`.
- **Hành vi bắt buộc sửa đổi:** Thay thế toán tử `or` bằng hàm tra cứu theo sự hiện diện của key và giá trị khác `None` (`is not None`).

---

### 2.4. Tái lập R2-F03B — Blank Date Matches Blank Date
- **Ca kiểm thử:** `test_repro_r2_f03b_blank_date_matches_blank_date`
- **Cơ chế gây lỗi:**
  - Hàm `extract_composite_key` không kiểm tra tính hợp lệ của ngày bay `FL_DATE`. Khi `FL_DATE` là chuỗi rỗng `""`, khóa composite key được tạo với ngày rỗng `("", "AA", 101.0, "DFW", "ORD")`.
- **Bằng chứng tái lập:** Hai bản ghi cùng bị rỗng ngày bay đã ghép cặp thành công (`UNIQUE_MATCH`) và đạt kiểm tra số học.
- **Hành vi bắt buộc sửa đổi:** Kiểm tra định dạng ngày chuẩn ISO `YYYY-MM-DD`. Nếu ngày bị rỗng hoặc sai định dạng, composite key phải bị đánh dấu là không hợp lệ (`None`) và không được phép tham gia so khớp.

---

### 2.5. Tái lập R2-F04 — Stale Lock Governance Invariant (Manual Recovery Required)
- **Ca kiểm thử:** `test_repro_r2_f04_stale_lock_governance_invariant`
- **Cơ chế gây lỗi:**
  - Trong test `test_f08_recovery_and_reconciliation_after_failure` của `test_t011_fault_injection.py`, sau khi phát hiện khóa tồn đọng của tiến trình đã chết (PID dead), test tự động gọi `stale_lock_file.unlink()`.
  - Tuy nhiên, trong mã nguồn chuẩn tắc `src/flight_pipeline/storage/locking.py` (dòng 194–198), khi PID đã chết, hệ thống cố tình ném ra `LockContentionError` với thông điệp:
    `FAIL_CLOSED — MANUAL_RECOVERY_REQUIRED`.
- **Bằng chứng tái lập:** Cơ chế khóa sản xuất kiên quyết từ chối tự động cướp hoặc xóa khóa của tiến trình đã chết nhằm bảo vệ tính toàn vẹn hệ thống tệp và bằng chứng forensic.
- **Hành vi bắt buộc sửa đổi:** Giữ nguyên quy tắc `FAIL_CLOSED — MANUAL_RECOVERY_REQUIRED` trong `locking.py`. Kiểm thử rõ ràng hành vi fail-closed khi có khóa tồn đọng và quy trình can thiệp thủ công (manual intervention lifecycle) của quản trị viên trong sandbox.

---

## 3. KẾT LUẬN GATE R2-1

- **Kết quả:** Toàn bộ 5 phát hiện kiểm toán độc lập đã được tái lập thành công với bằng chứng mã lệnh cụ thể.
- **Tiến độ:** Mở Gate R2-2 để triển khai sửa đổi mã nguồn và nâng cấp công cụ.
