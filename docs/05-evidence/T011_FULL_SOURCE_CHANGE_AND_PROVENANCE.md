# T011_FULL_SOURCE_CHANGE_AND_PROVENANCE — BÁO CÁO NGUỒN GỐC VÀ DANH MỤC THAY ĐỔI MÃ NGUỒN T-011

- **Mã nhiệm vụ:** `T-011` (Gate G5: KPI Sample Smoke, BTS Parity, TS-008, TS-013 & Review Packaging)
- **Gate:** `G5` (IN_PROGRESS)
- **Thời điểm kiểm toán:** 2026-10-18T21:05:00+07:00
- **Tiêu chuẩn tuân thủ:** [`AGENTS.md`](../../AGENTS.md), Master Execution Prompt T-011 Mục 4 & Mục 10.
- **Trạng thái:** **VERIFIED**

---

## 1. THÔNG SỐ NỀN TẢNG GIT VÀ RUNTIME

- **Git Branch:** `master`
- **Git Baseline Commit (trước T-011):** `bc4f03fb8ccd6c0b2455af3fcb2b1b98fa39d632`
- **Runtime:** Python 3.10.11, PySpark 4.0.1, OpenJDK 21.0.12.1 LTS
- **Hệ thống tệp:** Windows 10 NTFS (vùng an toàn cục bộ)
- **Dữ liệu thô:** 9 tệp `data/raw/tabular/{year}/flight_with_weather_{year}.csv` (Read-only, 0 bytes modified)
- **Vùng xuất bản sản xuất:** `data/curated/latest` (Unchanged, 0 mutations)

---

## 2. DANH MỤC CÁC TỆP MÃ NGUỒN, KIỂM THỬ VÀ BẰNG CHỨNG MỚI ĐƯỢC TẠO

Toàn bộ các tệp mới tạo nằm chính xác trong phạm vi được ủy quyền của Master Prompt:

### 2.1. Mã nguồn KPI Engine (`src/flight_pipeline/kpi/`)
1. `src/flight_pipeline/kpi/__init__.py`: Đóng gói package exports.
2. `src/flight_pipeline/kpi/catalog.py`: Khai báo 8 CORE KPIs, submetrics, min-N constants, và danh mục 17 cột.
3. `src/flight_pipeline/kpi/schema.py`: PySpark StructType cho bảng kết quả 17 cột chuẩn.
4. `src/flight_pipeline/kpi/aggregators.py`: Vị từ lọc hợp lệ số và hàm đánh giá min-N.
5. `src/flight_pipeline/kpi/calculator.py`: Lớp `KpiCalculator` tính toán 8 CORE KPIs và gom nhóm đa chiều.
6. `src/flight_pipeline/kpi/bts_reconciler.py`: Khung đối soát độc lập TS-018 so sánh 7 trường đo CORE với BTS TranStats.

### 2.2. Bộ Kiểm thử Chuyên sâu Mới (`tests/`)
7. `tests/test_t011_kpi_engine.py`: Unit tests đối soát độc lập với Python Oracle (7 tests PASS).
8. `tests/test_t011_ts008_repeatability.py`: Unit tests cho TS-008 GK-sketch accuracy và TS-012 repeatability (4 tests PASS).
9. `tests/test_t011_fault_injection.py`: Unit tests mô phỏng 8 kịch bản lỗi lưu trữ F01..F08 (8 tests PASS).
10. `tests/test_t011_ts018_bts_parity.py`: Unit tests đối soát 7 trường đo CORE và khóa trùng lặp (5 tests PASS).

### 2.3. Công cụ Kiểm chuẩn QA Mới (`tools/qa/`)
11. `tools/qa/run_t011_kpi_smoke.py`: Runner chạy kiểm chuẩn KPI smoke đa chiều (year, carrier-year).
12. `tools/qa/run_ts018_bts_parity.py`: Runner đối soát TS-018 tạo tệp tóm tắt JSON.

### 2.4. Hồ sơ Bằng chứng và Báo cáo (`docs/05-evidence/`)
13. `docs/05-evidence/T011_FULL_DOC_READING_ATTESTATION.md`: Biên bản đọc toàn bộ 50 tài liệu quy chuẩn (Gate 0A).
14. `docs/05-evidence/T011_FULL_BASELINE_AND_PREFLIGHT.md`: Biên bản kiểm toán baseline môi trường (Gate 0).
15. `docs/05-evidence/T011_FULL_KPI_ENGINE_VERIFICATION.md`: Báo cáo kiểm chuẩn KPI Engine và Oracle parity (Gate 1).
16. `docs/05-evidence/T011_FULL_TS008_AND_REPEATABILITY.md`: Báo cáo kiểm chứng GK-sketch và tính lặp lại (Gate 2).
17. `docs/05-evidence/T011_FULL_FAULT_INJECTION_AND_ROLLBACK.md`: Báo cáo thực nghiệm 8 kịch bản lỗi lưu trữ TS-013 (Gate 3).
18. `docs/05-evidence/T011_FULL_BTS_PARITY_RECONCILIATION.md`: Báo cáo đối soát BTS TranStats TS-018 và hiện trạng G2-EXC-001 (Gate 4).
19. `docs/05-evidence/T011_FULL_CONTRACTUAL_TEST_MATRIX.md`: Ma trận đối chiếu 20 bài kiểm thử hợp đồng.
20. `docs/05-evidence/T011_FULL_TEST_EXECUTION_REPORT.md`: Báo cáo tổng hợp kết quả 205 unittests và QA verifiers.
21. `docs/05-evidence/T011_FULL_RISK_AND_LIMITATION_REGISTER.md`: Sổ đăng ký rủi ro và giới hạn kỹ thuật.
22. `docs/05-evidence/T011_FULL_SOURCE_CHANGE_AND_PROVENANCE.md`: Báo cáo này.
23. `docs/05-evidence/T011_FULL_FINAL_INDEPENDENT_VERDICT.md`: Phán quyết độc lập của Agent cho T-011.
24. `docs/05-evidence/T011_FULL_LOG_UNITTEST_SUITE.txt`: Raw log kết quả chạy 205 unittests.
25. `docs/05-evidence/T011_FULL_LOG_QA_VERIFIERS.txt`: Raw log chạy các QA verifiers.
26. `docs/05-evidence/T011_TS018_BTS_RECONCILIATION_SUMMARY.json`: Tệp tóm tắt kết quả đối soát BTS dạng JSON.
27. `docs/05-evidence/T011_KPI_SAMPLE_SMOKE_METRICS.json`: Tệp dữ liệu metrics mẫu sau khi chạy KPI smoke.

---

## 3. KHẲNG ĐỊNH VỀ TÍNH TOÀN VẸN CỦA DỮ LIỆU VÀ QUẢN TRỊ

1. Tuyệt đối không can thiệp, không sửa đổi dữ liệu thô `data/raw/`.
2. Không ghi đè hoặc làm biến dạng các tài liệu bằng chứng lịch sử của G2, G3, G4, T-007, T-008, T-010.
3. Không tự ý sửa đổi các hợp đồng chuẩn tắc (`DECISIONS.md`, `DATA_CONTRACT.md`, `KPI_SPEC.md`).
4. Toàn bộ các thay đổi đều nằm trong phạm vi ủy quyền của Master Prompt T-011.
