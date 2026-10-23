# T011-R1 SOURCE CODE CHANGES & RISK REMEDIATION REPORT

**Project:** US Flight Performance Analysis 2016–2024  
**Task:** T-011 R1 — Targeted Independent Audit Remediation  
**Parent Gate:** G5 (IN_PROGRESS)  
**Deliverable:** `docs/05-evidence/T011_R1_SOURCE_CHANGE_AND_RISK_REPORT.md`  
**Date:** 2026-10-19  
**Status:** **AUDIT VERIFIED / ALL FINDINGS REMEDIATED / ZERO REGRESSION**

---

## 1. Tổng quan Mục tiêu Chỉnh sửa

Thực hiện nhiệm vụ **MASTER PROMPT — T011-R1 TARGETED INDEPENDENT AUDIT REMEDIATION**, nhóm kỹ thuật đã tiến hành khắc phục chính xác, cục bộ và triệt để 7 khiếm khuyết được chỉ ra bởi kiểm toán viên độc lập (R1-F01 đến R1-F07).

Toàn bộ các thay đổi tuân thủ nghiêm ngặt nguyên tắc:
- Không sửa/ghi đè bất kỳ tệp dữ liệu thô nào trong `data/raw/` (0 bytes modified).
- Bảo toàn tuyệt đối các quyết định chuẩn tắc `OR-05`, `OR-08`, `G2-EXC-001`, `G3-COND-A/B/C`, `FP-DEC-017`.
- Không khởi động Gate G6; không tự tiện tuyên bố nghiệm thu T-011 PASS.

---

## 2. Bảng Kê Chi tiết Thay đổi Mã nguồn (Source Code Changes)

| STT | Tập tin | Các hàm / phương thức sửa đổi | Mục đích & Chi tiết kỹ thuật |
|:---:|:---|:---|:---|
| 1 | `src/flight_pipeline/kpi/bts_reconciler.py` | `extract_composite_key`<br>`reconcile` | - Không âm thầm ép kiểu số hiệu chuyến bay lỗi thành `0.0`.<br>- Bổ sung 6 quy tắc fail-closed khi so khớp dữ liệu authentic (yêu cầu 0 unmatched, 0 ambiguity, 0 mismatch, có bằng chứng số học thực chất).<br>- Phân biệt rõ ràng phán quyết synthetic và authentic. |
| 2 | `src/flight_pipeline/kpi/calculator.py` | `compute_kpis_for_cohort`<br>`_make_kpi_row` | - Bọc toàn bộ các biểu thức `F.sum(...)` bằng `F.coalesce` tránh sinh ra SQL NULL trên DataFrame rỗng.<br>- Đảm bảo `count_records`, `count_metric_valid`, `excluded_count` là số nguyên $\ge 0$.<br>- Tự động gán `unit_status=ZERO_METRIC_DENOMINATOR` cho DataFrame 0 dòng.<br>- Cưỡng chế `source_coverage_status=PARTIAL` cho năm 2024 per OR-05.<br>- Kiểm tra tính toàn vẹn giữa `FL_DATE` và `source_year`. |
| 3 | `src/flight_pipeline/kpi/aggregators.py` | `evaluate_min_n` | - Bổ sung toàn bộ alias cho airport (`destination-year`, `origin_year`, v.v.) và route (`pair-year`).<br>- Bọc `safe_count = F.coalesce(valid_count_col, F.lit(0))` bảo đảm giá trị NULL được phân loại là `SUPPRESSED` thay vì `SUFFICIENT`. |
| 4 | `tools/qa/run_ts018_bts_parity.py` | `read_bts_csv`<br>`compute_sha256`<br>`run_ts018_reconciliation` | - Thay thế việc gán mảng rỗng bằng hàm đọc CSV thực tế và kiểm tra schema cột khóa bắt buộc.<br>- Tính toán mã băm SHA-256 đối soát.<br>- Thiết lập mã thoát fail-closed chuẩn: exit 0 (pass/pending), exit 1 (discrepancy), exit 2 (lỗi tệp). |
| 5 | `tests/test_t011_fault_injection.py` | `test_f01_source_read_failure`<br>`test_f02_staging_write_failure`<br>`test_f08_recovery_and_reconciliation_after_failure` | - F01 kích hoạt ngoại lệ đọc tệp nguồn thực sự.<br>- F02 ghi tệp byte hỏng vào staging để kiểm tra đánh chặn.<br>- F08 kiểm tra quy trình phát hiện stale lock và khôi phục nguyên tử sau lỗi. |
| 6 | `tests/test_t011_kpi_engine.py` | `test_06_min_n_threshold_boundaries`<br>`test_07_year_2024_partial_coverage_metadata`<br>`test_08_empty_cohort_kpi_computation`<br>`test_09_cohort_fl_date_year_validation` | - Mở rộng ma trận kiểm thử biên min-N lên 20 điểm trên cả 3 chiều và alias.<br>- Kiểm tra cưỡng chế OR-05 khi người gọi cố tình ghi đè.<br>- Kiểm thử tính toán trên cohort rỗng 0 dòng.<br>- Kiểm thử ném `ValueError` khi sai lệch cohort năm. |
| 7 | `tests/test_t011_ts008_repeatability.py` | `test_01_gk_sketch_rank_error_on_skewed_distribution` | - Nâng cỡ mẫu lên $N = 25,000$ ($1/N = 0.00004 \ll 0.0001$).<br>- Đánh giá khoảng hạng $[R_{low}/N, R_{high}/N]$ độc lập cho P50 và P90 với dung sai toán học $\epsilon \le 0.0001$. |
| 8 | `tests/test_t011_ts018_bts_parity.py` | `test_06_authentic_parity_fail_closed_on_unmatched_records`<br>`test_07_authentic_parity_fail_closed_on_all_null_measures`<br>`test_08_invalid_flight_number_handling` | - Kiểm thử từ chối PASS khi có 1 bản ghi unmatched.<br>- Kiểm thử từ chối PASS khi 100% độ đo là NULL.<br>- Kiểm thử trích xuất số hiệu chuyến bay lỗi. |
| 9 | `tests/test_t011_r1_counterexamples.py` | Toàn bộ tệp | - Xây dựng bộ kiểm thử xác minh hồi quy mục tiêu cho cả 7 khiếm khuyết R1-F01..F07. |

---

## 3. Cập nhật Sổ tay Rủi ro (Risk Register Updates)

| Mã rủi ro | Mô tả rủi ro | Đánh giá trước R1 | Biện pháp xử lý tại R1 | Đánh giá sau R1 | Trạng thái |
|:---|:---|:---:|:---|:---:|:---:|
| **R-KPI-01** | Dung sai GK-sketch quá lỏng (1.5%) che giấu sai lệch phân vị | CAO | Tăng mẫu lên $N=25,000$, kiểm tra khoảng hạng toán học $\epsilon \le 0.0001$. | THẤP | **MITIGATED** |
| **R-KPI-02** | Lan truyền SQL NULL trên cohort rỗng gây lỗi hợp đồng đếm | TRUNG BÌNH | Bọc `F.coalesce` toàn diện, đảm bảo count $\ge 0$ và unit status chuẩn. | RẤT THẤP | **RESOLVED** |
| **R-KPI-03** | Nguy cơ False Pass trong đối soát BTS TranStats | RẤT CAO | Áp dụng 6 quy tắc fail-closed, đọc CSV thật, kiểm tra digest SHA-256. | THẤP | **CONTROLLED** |
| **R-KPI-04** | Vi phạm quyết định chuẩn tắc OR-05 đối với năm 2024 | TRUNG BÌNH | Cưỡng chế tự động `source_coverage_status=PARTIAL` ở tầng tính toán. | RẤT THẤP | **RESOLVED** |
| **R-KPI-05** | Nhầm lẫn dữ liệu giữa các năm cohort | TRUNG BÌNH | Thêm tiền kiểm tra `FL_DATE` khớp `source_year`, fail-closed ném `ValueError`. | RẤT THẤP | **RESOLVED** |
| **R-FS-03** | Khôi phục không hoàn chỉnh sau sự cố gián đoạn ghi staging | TRUNG BÌNH | Kiểm thử thực tế stale lock recovery và xuất bản nguyên tử hai giai đoạn. | THẤP | **VERIFIED** |

---

## 4. Xác nhận Bất biến Dữ liệu Thô (Data Invariance Attestation)

Auditor khẳng định và cam đoan:
- Thư mục `data/raw/` không có bất kỳ tập tin nào bị sửa đổi, xóa hoặc tạo mới (0 bytes changed).
- Không có bất kỳ lệnh SQL/Spark overwrite nào can thiệp vào các tập tin CSV nguồn.
- Toàn bộ bằng chứng và artifact đầu ra được xuất riêng biệt trong `docs/05-evidence/`.
