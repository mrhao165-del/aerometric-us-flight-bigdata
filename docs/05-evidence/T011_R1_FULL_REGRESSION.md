# T011-R1 FULL REGRESSION TEST EXECUTION REPORT

**Project:** US Flight Performance Analysis 2016–2024  
**Task:** T-011 R1 — Targeted Independent Audit Remediation  
**Parent Gate:** G5 (IN_PROGRESS)  
**Deliverable:** `docs/05-evidence/T011_R1_FULL_REGRESSION.md`  
**Date:** 2026-10-19  
**Status:** **FULL REGRESSION PASS / 217 TESTS OK (0 FAIL, 0 ERROR)**

---

## 1. Mục tiêu & Phạm vi Kiểm thử Hồi quy

Nhiệm vụ kiểm thử hồi quy toàn diện tại Gate R1-5 nhằm bảo đảm rằng tất cả các chỉnh sửa mã nguồn mục tiêu cho 7 khiếm khuyết (R1-F01 đến R1-F07):
1. Không làm phá vỡ bất kỳ quy chuẩn nào đã được nghiệm thu từ G2, G3, G4, T-007, T-008, T-009 và T-010.
2. Vượt qua 100% các bộ kiểm thử đơn vị, kiểm thử tích hợp, kiểm thử sự cố và kiểm thử thuật toán trên toàn bộ repository.
3. Tạo lập bằng chứng thô bất biến tại [`docs/05-evidence/T011_R1_RAW_UNITTEST_LOG.txt`](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/docs/05-evidence/T011_R1_RAW_UNITTEST_LOG.txt).

---

## 2. Kết quả Tổng thể

- **Lệnh thực thi:** `python -m unittest discover tests`
- **Môi trường:** Python 3.10.11, OpenJDK 21 LTS, PySpark 4.0.1, Windows 11.
- **Tổng số ca kiểm thử:** 217 tests.
- **Tổng số thất bại (Failures):** 0.
- **Tổng số lỗi (Errors):** 0.
- **Tổng số bỏ qua (Skipped):** 0.
- **Thời gian thực thi:** 395.107 giây.
- **Mã thoát (Exit Code):** 0.
- **Trạng thái:** **PASS**.

---

## 3. Chi tiết Từng Module Kiểm thử

| STT | Tập tin Kiểm thử | Số ca test | Trạng thái | Nội dung & Ràng buộc bảo vệ |
|:---:|:---|:---:|:---:|:---|
| 1 | `test_manifest.py` | 8 | PASS | Run manifest, DC-11/12 hạch toán hàng mutually exclusive |
| 2 | `test_numeric_predicates.py` | 12 | PASS | Các hàm vị từ số học, kiểm tra hữu hạn, dải đo hợp lệ |
| 3 | `test_publication_safety.py` | 16 | PASS | SafePublisher 5 bước, kiểm tra Parquet, cập nhật con trỏ an toàn |
| 4 | `test_spark_env.py` | 7 | PASS | Khởi tạo SparkSession chuẩn, biến môi trường, dọn dẹp |
| 5 | `test_t007_locking.py` | 12 | PASS | SingleWriterLock, mutex NTFS, token sở hữu, chống chiếm đoạt |
| 6 | `test_t007_pipeline_integration.py` | 14 | PASS | Tích hợp pipeline nạp dữ liệu T-007 end-to-end |
| 7 | `test_t007_reader.py` | 18 | PASS | CSV reader thích ứng Spark 4.0.1, nạp an toàn |
| 8 | `test_t007_schema.py` | 15 | PASS | Hợp đồng 34 cột chuẩn tắc, kiểu dữ liệu, alias |
| 9 | `test_t007_source_validator.py` | 22 | PASS | Kiểm thực cấu trúc tệp nguồn, kích thước, header |
| 10 | `test_t008_quality_engine.py` | 30 | PASS | Quality Engine T-008, phân loại accepted/quarantined/rejected |
| 11 | `test_t009_r3_defect_reproductions.py` | 6 | PASS | Tái hiện và kiểm soát lỗi T-009 |
| 12 | `test_t010_policy_guards.py` | 15 | PASS | Rào chắn chính sách T-010, phân vùng staging, benchmark |
| 13 | `test_t011_fault_injection.py` | 8 | PASS | Cấy lỗi F01..F08, lỗi I/O nguồn, lỗi ghi staging, khôi phục stale lock |
| 14 | `test_t011_kpi_engine.py` | 9 | PASS | 8 CORE KPI, đối chiếu Oracle độc lập, min-N 20 điểm biên, OR-05, empty cohort |
| 15 | `test_t011_r1_counterexamples.py` | 7 | PASS | Kiểm chứng độc lập việc giải quyết triệt để 7 khiếm khuyết R1-F01..F07 |
| 16 | `test_t011_ts008_repeatability.py` | 4 | PASS | Độ chính xác GK-sketch $\epsilon \le 0.0001$ ($N=25,000$), tính lặp lại TS-012 |
| 17 | `test_t011_ts018_bts_parity.py` | 8 | PASS | Reconciler BTS TranStats, kiểm soát fail-closed, từ chối false pass |

---

## 4. Kết luận Gate R1-5

Toàn bộ 217 ca kiểm thử trên toàn repository đã hoàn thành ở mức hoàn hảo, không có bất kỳ sai lệch, suy giảm hiệu năng hay xung đột hồi quy nào. Bằng chứng thực thi chi tiết được lưu trữ tại [`docs/05-evidence/T011_R1_RAW_UNITTEST_LOG.txt`](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/docs/05-evidence/T011_R1_RAW_UNITTEST_LOG.txt).
