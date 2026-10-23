# G4-SIGNOFF-TEST-EVIDENCE-ERRATA: Reconciliation of Repository Test Modules

**Mã tài liệu:** `G4-ERRATA-TEST-01`  
**Dự án:** US Flight Performance Analysis 2016–2024  
**Nhiệm vụ:** `Gate G4 Official Signoff & Verification Audit`  
**Ngày lập:** `2026-10-18`  
**Trạng thái:** `OFFICIALLY_RECONCILED`  
**Tham chiếu gốc:** [`T008_FINAL_EXIT_FULL_TEST_RESULTS.md`](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/docs/05-evidence/T008_FINAL_EXIT_FULL_TEST_RESULTS.md), [`T008_FINAL_EXIT_LOG_UNITTEST_SUITE.txt`](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/docs/05-evidence/T008_FINAL_EXIT_LOG_UNITTEST_SUITE.txt)

---

## 1. Mục đích và Phạm vi Đính chính

Trong tài liệu [`T008_FINAL_EXIT_FULL_TEST_RESULTS.md`](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/docs/05-evidence/T008_FINAL_EXIT_FULL_TEST_RESULTS.md) Mục 2, bảng phân bổ kết quả kiểm thử toàn repository đã ghi nhận đúng tuyệt đối tổng số lượng kiểm thử thực tế là **171 tests PASS**, hoàn toàn khớp với log thực thi `Ran 171 tests in 123.808s - OK` tại [`T008_FINAL_EXIT_LOG_UNITTEST_SUITE.txt`](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/docs/05-evidence/T008_FINAL_EXIT_LOG_UNITTEST_SUITE.txt).

Tuy nhiên, trong bảng biểu Mục 2 của tài liệu trên, một số tên tệp kiểm thử đã được trình bày dưới dạng tên chức năng/bí danh gộp thay vì đường dẫn tệp vật lý độc lập (ví dụ: gộp `test_manifest.py`, `test_numeric_predicates.py`, `test_t009_r3_defect_reproductions.py` thành `test_t009_run_manifest.py`; gọi `test_publication_safety.py` là `test_t009_windows_safe_publisher.py`; gọi `test_t007_pipeline_integration.py` là `test_t007_coordinator.py`).

Tài liệu phụ lục đính chính này thực hiện đối chiếu chi tiết 1-1 giữa bảng phân bổ chức năng và **11 tệp kiểm thử vật lý thực tế** trong thư mục `tests/`, bảo đảm tính minh bạch, chính xác tuyệt đối và toàn vẹn của bằng chứng nghiệm thu Gate G4 mà không sửa đổi lịch sử log thô đã niêm phong.

---

## 2. Bảng Đối chiếu Chi tiết 11 Test Modules Thực tế

Lệnh khám phá kiểm thử `python -m unittest discover tests` tự động nạp và thực thi chính xác **11 tệp module kiểm thử vật lý** trong thư mục `tests/`:

| STT | Tên Tệp Kiểm thử Vật lý (`Physical Test File`) | Nhiệm vụ Gốc | Số Tests Thực tế | Thời gian / Trạng thái | Bí danh Gộp trong Báo cáo Cũ |
|:---:|---|:---:|:---:|:---:|---|
| 1 | [`tests/test_manifest.py`](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/tests/test_manifest.py) | `T-009` | **6** | PASS | Gộp trong `test_t009_run_manifest.py` |
| 2 | [`tests/test_numeric_predicates.py`](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/tests/test_numeric_predicates.py) | `T-009` | **4** | PASS | Gộp trong `test_t009_run_manifest.py` |
| 3 | [`tests/test_publication_safety.py`](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/tests/test_publication_safety.py) | `T-009` | **18** | PASS | Ghi là `test_t009_windows_safe_publisher.py` |
| 4 | [`tests/test_spark_env.py`](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/tests/test_spark_env.py) | `T-009` | **4** | PASS | Ghi là `test_t009_spark_init.py` |
| 5 | [`tests/test_t007_locking.py`](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/tests/test_t007_locking.py) | `T-007` | **8** | PASS | Ghi là `test_t007_locking.py` |
| 6 | [`tests/test_t007_pipeline_integration.py`](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/tests/test_t007_pipeline_integration.py) | `T-007` | **13** | PASS | Ghi là `test_t007_coordinator.py` |
| 7 | [`tests/test_t007_reader.py`](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/tests/test_t007_reader.py) | `T-007` | **17** | PASS | Ghi là `test_t007_reader.py` |
| 8 | [`tests/test_t007_schema.py`](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/tests/test_t007_schema.py) | `T-007` | **22** | PASS | Ghi là `test_t007_schema.py` (26 tests do gộp 4 test fixture) |
| 9 | [`tests/test_t007_source_validator.py`](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/tests/test_t007_source_validator.py) | `T-007` | **38** | PASS | Ghi là `test_t007_source_validator.py` |
| 10 | [`tests/test_t008_quality_engine.py`](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/tests/test_t008_quality_engine.py) | `T-008` | **36** | PASS | Ghi là `test_t008_quality_engine.py` |
| 11 | [`tests/test_t009_r3_defect_reproductions.py`](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/tests/test_t009_r3_defect_reproductions.py) | `T-009` | **5** | PASS | Gộp trong `test_t009_run_manifest.py` |
| **TỔNG** | **Toàn bộ 11 modules kiểm thử vật lý** | **G4** | **171** | **100% PASS** | **Khớp chính xác 171 tests trong raw log** |

---

## 3. Phân bổ Số lượng Test Theo Nhiệm vụ Thành phần của Gate G4

1. **Nhiệm vụ `T-009` (Hạ tầng PySpark, Publisher, Manifest):**
   - `test_manifest.py` (6) + `test_numeric_predicates.py` (4) + `test_publication_safety.py` (18) + `test_spark_env.py` (4) + `test_t009_r3_defect_reproductions.py` (5) = **37 tests PASS**.
2. **Nhiệm vụ `T-007` (Ingestion Pipeline, Schema, Reader, Coordinator, Locking):**
   - `test_t007_locking.py` (8) + `test_t007_pipeline_integration.py` (13) + `test_t007_reader.py` (17) + `test_t007_schema.py` (22) + `test_t007_source_validator.py` (38) = **98 tests PASS**.
3. **Nhiệm vụ `T-008` (Data Quality, Accounting, Coverage, Policy):**
   - `test_t008_quality_engine.py` = **36 tests PASS**.

**Tổng cộng:** $37 + 98 + 36 = 171$ unit & integration tests PASS.

---

## 4. Kết luận Quản trị

Phụ lục đính chính này xác nhận rằng:
- Không có bất kỳ test giả mạo hoặc test case nào bị thiếu.
- Cả 11 tệp module kiểm thử đều tồn tại thực tế trên hệ thống tệp và được thực thi đầy đủ.
- Tổng số lượng 171 tests đã đạt trạng thái `OK` và hoàn toàn bảo toàn nguyên vẹn tính nhất quán documentary integrity của đồ án.
