# BIÊN BẢN NGHIỆM THU CHÍNH THỨC NHIỆM VỤ T-008 (PROJECT LEAD OFFICIAL SIGNOFF)

**Mã biên bản:** `T008-SIGNOFF-20261018`  
**Dự án:** US Flight Performance Analysis 2016–2024  
**Nhiệm vụ:** `T-008 — Data Quality, Disjoint Row Accounting & Quarantine Engine`  
**Cổng quản trị:** `Gate G4`  
**Ngày nghiệm thu:** `2026-10-18`  
**Thẩm quyền phê duyệt:** `Project Lead` (qua chỉ thị trực tiếp `APPROVED_BY_PROJECT_LEAD_EXPLICIT_INSTRUCTION`)  
**Trạng thái phê duyệt:** **`PASS / COMPLETED (CONTROLLED)`**  
**Hình thức kiểm toán:** Independent QA & Governance Audit Record  

---

## 1. Quyết định Nghiệm thu Chính thức

Căn cứ kết quả rà soát độc lập và gói hồ sơ kỹ thuật `MASTER-T008-FINAL-EXIT`, Project Lead chính thức phê duyệt nghiệm thu:

> **NHIỆM VỤ T-008 = PASS / COMPLETED (CONTROLLED)**

### 1.1 Phạm vi Nghiệm thu
1. **Triển khai Production Code (`src/flight_pipeline/quality/`):**
   - [`predicates.py`](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/src/flight_pipeline/quality/predicates.py): Vị từ số học an toàn tuyệt đối dưới Spark ANSI mode (`spark.sql.ansi.enabled=true`) thông qua `try_cast(DoubleType())`, bảo vệ hoàn toàn khỏi `SparkNumberFormatException` khi gặp chuỗi lỗi (`"UNKNOWN_DELAY"`), bảo toàn số trễ âm (chuyến bay sớm), áp dụng `F.coalesce` cho biên domain thời gian.
   - [`accounting.py`](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/src/flight_pipeline/quality/accounting.py): Động cơ hạch toán dòng 3 trạng thái rời nhau tuyệt đối (`DC-11`: `N_raw == N_accepted + N_quarantined + N_rejected`), kiểm toán đối chiếu với số đếm độc lập từ file nguồn, hạch toán metric `count_metric_valid <= count_records` (`DC-12`), xử lý mẫu số 0 an toàn.
   - [`catalog.py`](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/src/flight_pipeline/quality/catalog.py): Danh mục 18 quy tắc chất lượng chuẩn tắc với đầy đủ thuộc tính `rule_id`, `scope`, `severity`, `consequence`, `authority`, phân định rõ `RECORD`, `METRIC`, `DATASET`.
   - [`coverage.py`](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/src/flight_pipeline/quality/coverage.py): Bộ phân tích độ phủ lịch hàng năm, phân định rành mạch giữa vắng mặt Tháng 3/2024 (`is_march_missing`) và mẫu hình chuẩn tắc chính xác 335 ngày của OR-05 (`is_exact_or05_pattern`), chống dương tính giả trên cohort trống.
   - [`policy.py`](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/src/flight_pipeline/quality/policy.py): Cấu hình chính sách chất lượng với ranh giới thép giữa **Runtime Execution Guards** (bất biến sản xuất: `quarantine_non_positive_flight_num=False`, `allow_weather_nulls=True`, `strict_record_accounting=True`, `strict_metric_accounting=True`) và **Simulation Parameter** (`allow_unapproved_policies=False`).
   - [`engine.py`](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/src/flight_pipeline/quality/engine.py): Cổng điều phối chất lượng thống nhất `QualityEngine.evaluate()`, gắn cờ metric validity không làm rơi dòng, hỗ trợ mô phỏng tái phân loại an toàn khi có cờ ủy quyền.
2. **Kiểm chứng Tích hợp Thực nghiệm (Synthetic Verification):**
   - Đạt **36/36 tests PASS** trong [`tests/test_t008_quality_engine.py`](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/tests/test_t008_quality_engine.py) (thời gian chạy: 37.26 giây).
   - Toàn bộ test suite repository đạt **171/171 tests PASS** (thời gian chạy: 123.81 giây).
3. **Bộ Artifact Kiểm toán Được Niêm phong:**
   - Lưu trữ tại: `D:/Study/Code/Apache/Flight_Analyzt/T008_FINAL_SIGNOFF_REVIEW_PACKAGE.zip` (1,715,263 bytes, SHA-256: `4fb7c5e276e1416dbb8906e78c681804aeb46b30defe974062a4ae78c6282e5a`, 523 tệp).
   - Manifest: `D:/Study/Code/Apache/Flight_Analyzt/T008_FINAL_SIGNOFF_REVIEW_PACKAGE_MANIFEST.json`.

---

## 2. Ranh giới Nghiệm thu và Cảnh báo Chống Giả mạo (Anti-Hallucination Boundaries)

Theo chính sách bắt buộc tại `AGENTS.md`:
1. **Phạm vi nghiệm thu là mã nguồn production và kiểm thử synthetic.** Nghiệm thu này **KHÔNG PHẢI** là xác nhận đã chạy Spark trên 54,674,003 dòng dữ liệu thật của 9 năm.
2. Dữ liệu gốc trong `data/raw/` được bảo tồn nguyên vẹn 100%, không bị sửa đổi hay ghi đè.
3. Các mã băm SHA-256 ứng viên cho 9 tệp CSV nguồn giữ trạng thái **`CANDIDATE_PENDING_HUMAN_ACCEPTANCE`** (`OR-08 = IDENTITY_UNVERIFIED`).

---

## 3. Các Điều kiện và Nghĩa vụ Chuyển giao Bắt buộc Được Bảo lưu

| Mã điều kiện / Rủi ro | Nội dung quản trị bắt buộc | Cổng / Nhiệm vụ đích | Trạng thái bảo lưu |
|---|---|---|:---:|
| **`OR-05`** | Năm 2024 khuyết 31 ngày Tháng 3/2024 (`335/366` ngày). Giữ `source_coverage_status = PARTIAL`. Cấm tự chế dòng bù khuyết. | G6 / `T-012` (`TS-004`) | **`OPEN_QUALITY_DEFECT`** |
| **`OR-08`** | 9 tệp CSV nguồn chỉ khớp metadata size/line, nội dung SHA-256 chưa đối chiếu upstream. | G4/G5 / `TS-019` | **`IDENTITY_UNVERIFIED`** |
| **`G2-EXC-001`** | 7 trường số đo CORE giữ nhãn `OFFICIAL_MINUTES_EMPIRICALLY_CONSISTENT_PROVISIONAL`. Bắt buộc đối chiếu mẫu BTS TranStats đạt PASS tại G5 (`TS-018`); nếu FAIL chặn toàn bộ G6. | G5 / `T-011` (`TS-018`) | **`PROVISIONAL_EXCEPTION_ACTIVE`** |
| **`G3-COND-A`** | Chính sách hard quarantine cho `OP_CARRIER_FL_NUM <= 0` là đề xuất sơ bộ. Trong production, các bản ghi này tiếp tục là `ACCEPTED` kèm cờ cảnh báo. Bắt buộc rào cứng preflight trước `T-010`. | G5 / `T-010`, `T-011` | **`PROVISIONAL_POLICY_PENDING_REAL_DATA`** |
| **`FP-DEC-017`** | Thời tiết mang trạng thái `CONDITIONAL_NO_GO`. Vắng mặt dữ liệu thời tiết không được phép quarantine hay reject chuyến bay CORE. | G5–G7 / `T-010..T-015` | **`APPROVED_CONDITIONAL_NO_GO`** |

---

## 4. Rào chắn Sản xuất Bắt buộc Trước Gate G5 (`T-010`)

Trước khi thực thi smoke run trên dữ liệu thật năm 2016 tại `T-010`:
1. Cấm kích hoạt `allow_unapproved_policies=True` trong cấu hình pipeline sản xuất.
2. Cấm kích hoạt `quarantine_non_positive_flight_num=True` trong cấu hình pipeline sản xuất.
3. Cấm xuất bản bất kỳ DataFrame nào từ chế độ mô phỏng (`allow_unapproved_policies=True`) thành output sản xuất.
4. Mọi vi phạm phải kích hoạt cơ chế `fail-closed` ngay lập tức, chặn không cập nhật con trỏ xuất bản.
5. Kiểm chứng các rào chắn này qua regression tests tại preflight của Gate G5.

---

## 5. Kết luận

Nhiệm vụ **T-008** chính thức hoàn tất với trạng thái **`PASS / COMPLETED (CONTROLLED)`**. Dự án đủ điều kiện đóng Gate G4 và bàn giao sang công tác chuẩn bị Gate G5.
