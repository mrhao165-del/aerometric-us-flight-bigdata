# T007 — FINAL SIGNOFF DOCUMENTATION ERRATA & RECONCILIATION ADDENDUM

**Project:** US Flight Performance Analysis 2016–2024  
**Parent Task:** `T-007` — Raw CSV Ingestion Pipeline  
**Gate:** `G4` (`PLANNED / NOT_COMPLETED`)  
**Document ID:** `T007-DOC-ERRATA-01`  
**Date:** 2026-10-18  
**Authority:** Human Project Lead Signoff Direction & Canonical Evidence Reconciliation  
**Status:** `APPROVED_CANONICAL_ERRATA`

---

## 1. Mục đích và Phạm vi Phụ lục

Tài liệu này là phụ lục đính chính chính thức (**Documentation Errata**) thuộc hồ sơ nghiệm thu có kiểm soát của Nhiệm vụ `T-007` (Raw CSV Ingestion Pipeline). Phụ lục này giải quyết và chuẩn hóa bốn sai khác tài liệu lịch sử được ghi nhận trong các báo cáo kiểm toán trước đó, đảm bảo tính nhất quán tuyệt đối giữa mã nguồn, kết quả kiểm thử thực tế và các tài liệu quản trị sống:

1. **`ERR-01` — Canonical Source Inventory:** Chuẩn hóa số liệu hàng, dung lượng byte và danh mục tệp nguồn chuẩn tắc của dự án.
2. **`ERR-02` — Unit Test Counts & Module Distribution:** Trích xuất và đối chiếu chính xác phân bố 135 kiểm thử từ nhật ký chạy thực tế `T007_SIGNOFF_EXIT_LOG_UNITTEST_SUITE.txt`.
3. **`ERR-03` — Gate Boundaries & Downstream Ingestion Obligations:** Phân định ranh giới pháp lý giữa Gate G4 (triển khai mã nguồn & synthetic verification), Gate G5 (smoke 1 năm & đối chiếu đơn vị BTS), và Gate G6 (ETL 9 năm sản xuất).
4. **`ERR-04` — Lineage Identifier Semantics & Provisional Quarantine Scope:** Làm rõ ngữ nghĩa định danh dòng `_record_lineage_id` và phạm vi chính sách cách ly `G3-COND-A` chờ chuyển giao sang `T-008`.

---

## 2. ERR-01 — Canonical Source Inventory

### 2.1. Hiện tượng Sai khác Lịch sử
Trong một số tài liệu nháp và ghi chú ứng viên trước đây, xuất hiện các con số `54,727,629` dòng hoặc `19,353,074,475` bytes. Những con số này xuất phát từ các ước tính hoặc snapshot chưa qua kiểm toán chuẩn tắc giai đoạn sơ khai.

### 2.2. Chuẩn hóa Định lượng Chuẩn tắc (Audited Baseline)
Theo hồ sơ kiểm toán cấu trúc Gate G1 (`schema_2016.json` .. `schema_2024.json`), `AUDITED_SOURCE_INVENTORY` trong mã nguồn sản xuất [`src/flight_pipeline/ingestion/source_validator.py`](../../src/flight_pipeline/ingestion/source_validator.py), và kết quả tính toán streaming SHA-256 thực tế tại [`docs/05-evidence/T007_LOCAL_RAW_SHA256_CANDIDATE.json`](T007_LOCAL_RAW_SHA256_CANDIDATE.json):

- **Số lượng tệp nguồn:** Đúng 9 tệp CSV thường niên giai đoạn 2016–2024.
- **Quy tắc đường dẫn:** `data/raw/tabular/{year}/flight_with_weather_{year}.csv`.
- **Tổng số dòng dữ liệu đã kiểm toán:** **`54,674,003`** dòng (không bao gồm 9 dòng tiêu đề vật lý).
- **Tổng kích thước byte thực tế:** **`15,196,366,173`** bytes.

### 2.3. Bảng Đối chiếu Chi tiết Từng năm Chuẩn tắc

| Năm | Đường dẫn Tệp Chuẩn tắc | Audited Rows (Header Excluded) | Audited Bytes | Trạng thái Dữ liệu Kiểm toán |
| :---: | :--- | ---: | ---: | :--- |
| **2016** | `data/raw/tabular/2016/flight_with_weather_2016.csv` | `5,617,658` | `1,563,975,417` | Hoàn chỉnh 366 ngày (Năm nhuận) |
| **2017** | `data/raw/tabular/2017/flight_with_weather_2017.csv` | `5,674,621` | `1,578,131,843` | Hoàn chỉnh 365 ngày |
| **2018** | `data/raw/tabular/2018/flight_with_weather_2018.csv` | `7,213,446` | `2,006,204,500` | Hoàn chỉnh 365 ngày (chứa cặp trùng `YX 3624`) |
| **2019** | `data/raw/tabular/2019/flight_with_weather_2019.csv` | `7,422,037` | `2,069,045,699` | Hoàn chỉnh 365 ngày |
| **2020** | `data/raw/tabular/2020/flight_with_weather_2020.csv` | `4,688,354` | `1,304,784,334` | Hoàn chỉnh 366 ngày (Năm nhuận COVID-19) |
| **2021** | `data/raw/tabular/2021/flight_with_weather_2021.csv` | `5,938,261` | `1,652,382,900` | Hoàn chỉnh 365 ngày |
| **2022** | `data/raw/tabular/2022/flight_with_weather_2022.csv` | `6,729,125` | `1,871,846,929` | Hoàn chỉnh 365 ngày |
| **2023** | `data/raw/tabular/2023/flight_with_weather_2023.csv` | `6,758,213` | `1,879,720,534` | Hoàn chỉnh 365 ngày |
| **2024** | `data/raw/tabular/2024/flight_with_weather_2024.csv` | `4,632,288` | `1,270,274,017` | **335/366 ngày** (Khuyết toàn bộ Tháng 3/2024 — `OR-05`) |
| **TỔNG** | **9 tệp CSV thường niên** | **`54,674,003`** | **`15,196,366,173`** | **Canonical Baseline Chuẩn tắc Duy nhất** |

> [!IMPORTANT]
> **Quyết định Chuẩn tắc:** Toàn bộ các con số `54,727,629` dòng hoặc `19,353,074,475` bytes bị bác bỏ hoàn toàn. Mọi tài liệu kỹ thuật, hợp đồng kiểm thử và báo cáo nghiệm thu từ Task `T-007` trở đi bắt buộc sử dụng con số chuẩn tắc: **`54,674,003` dòng** và **`15,196,366,173` bytes**.

---

## 3. ERR-02 — Unit Test Counts & Module Distribution

### 3.1. Hiện tượng Sai khác Báo cáo
Một số tài liệu tổng hợp báo cáo các số đếm kiểm thử thành phần không đồng bộ (ví dụ: `34` thay vì `38` trong `test_t007_source_validator.py`, hoặc `26` thay vì `22` trong `test_t007_schema.py` do quá trình gộp các ca kiểm thử Schema Factory).

### 3.2. Trích xuất Chuẩn xác từ Nhật ký Chạy Thực tế
Căn cứ vào tệp nhật ký thực thi thực tế của toàn bộ bộ kiểm thử đơn vị và tích hợp synthetic:
[`docs/05-evidence/T007_SIGNOFF_EXIT_LOG_UNITTEST_SUITE.txt`](T007_SIGNOFF_EXIT_LOG_UNITTEST_SUITE.txt)  
Lệnh thực thi: `python -m unittest discover -s tests -p "test_*.py" -v`  
Kết quả tổng thể: **`Ran 135 tests in 96.670s — OK (135 PASS, 0 FAIL, 0 SKIP)`**.

Phân bố chi tiết 135 bài kiểm thử theo từng mô-đun nguồn:

| STT | Tệp Kiểm thử (`Test Module`) | Lớp Kiểm thử (`TestCase Class`) | Nhiệm vụ | Số lượng Test PASS |
| :---: | :--- | :--- | :---: | :---: |
| 1 | `tests/test_manifest.py` | `TestRunManifest` | `T-009` | **6** |
| 2 | `tests/test_numeric_predicates.py` | `TestNumericPredicates` | `T-009` | **4** |
| 3 | `tests/test_publication_safety.py` | `TestPublicationSafety` | `T-009` | **18** |
| 4 | `tests/test_spark_env.py` | `TestSparkEnv` | `T-009` | **4** |
| 5 | `tests/test_t009_r3_defect_reproductions.py` | `TestT009R3DefectReproductions` | `T-009` | **5** |
| -- | *Tiểu kế cụm kiểm thử T-009* | *5 mô-đun hạ tầng và xuất bản an toàn* | *T-009* | *37 PASS* |
| 6 | `tests/test_t007_schema.py` | `TestT007SchemaSynthetic` | `T007-01` | **22** |
| 7 | `tests/test_t007_source_validator.py` | `TestT007SourceValidatorSynthetic` | `T007-02` | **38** |
| 8 | `tests/test_t007_reader.py` | `TestT007ReaderSynthetic` | `T007-03` | **17** |
| 9 | `tests/test_t007_locking.py` | `TestT007Locking` | `T007-04` | **8** |
| 10 | `tests/test_t007_pipeline_integration.py` | `TestT007PipelineIntegration` | `T007-05..07` | **13** |
| -- | *Tiểu kế cụm kiểm thử T-007* | *5 mô-đun nạp liệu và xác thực schema* | *T-007* | *98 PASS* |
| **TỔNG** | **10 tệp kiểm thử chuẩn tắc** | **10 lớp kiểm thử thực thi** | **G4** | **`135 PASS`** |

> [!NOTE]
> Không có bất kỳ tên kiểm thử hay assertion nào được tạo giả. Con số **135 tests PASS** phản ánh chính xác 100% các ca kiểm thử thực tế được nạp bởi `unittest.TestLoader` và thực thi thành công trên môi trường Windows / Python 3.10 / PySpark 4.0.1.

---

## 4. ERR-03 — Gate Boundaries & Ingestion Obligations

### 4.1. Hiện tượng Ngộ nhận Ranh giới Gate
Một số diễn giải sơ thảo cho rằng Gate G4 đòi hỏi phải hoàn thành các bài kiểm thử quy mô lớn trên dữ liệu thật hoặc chạy trọn vẹn Spark pipeline trên 54.7 triệu dòng.

### 4.2. Phân định Ranh giới Kỹ thuật và Pháp lý Chuẩn tắc
1. **Phạm vi của Gate G4 (Task `T-009`, `T-007`, `T-008`):**
   - Gate G4 là cổng **Triển khai Mã nguồn & Xác thực Tích hợp Synthetic (Implementation & Synthetic Integration)**.
   - Nhiệm vụ `T-007` chỉ hoàn tất tầng nạp mã nguồn, xác thực schema, kiểm toán xuất xứ, cơ chế khóa đơn ghi, xuất bản 2 pha, phục hồi hậu-pointer và kiểm thử trên các tập synthetic fixtures.
   - Việc nghiệm thu `T-007` tại G4 **hoàn toàn KHÔNG bao gồm việc chạy Spark full-year hay full 9-year trên 54.7 triệu dòng CSV thật**.
2. **Nghĩa vụ chuyển giao sang Gate G5 (Task `T-010`, `T-011`):**
   - `T-010`: Chạy smoke thử nghiệm giới hạn trên **1 năm duy nhất (2016)** vào staging Parquet và đo benchmark tài nguyên thực tế (`TS-014`).
   - `T-011`: Triển khai và đối chiếu KPI mẫu, tiêm lỗi rollback (`TS-013`), và **bắt buộc thực hiện `TS-018` — đối chiếu 7 trường số đo CORE trực tiếp với bản ghi BTS TranStats có thẩm quyền**. Nếu `TS-018` không đạt `PASS`, Gate G6 bị CHẶN (`BLOCKED`).
   - Các nhiệm vụ `T-010` và `T-011` **thuộc Gate G5**, không phải điều kiện tiên quyết để nghiệm thu `T-007` hay hoàn thành Gate G4.
3. **Nghĩa vụ chuyển giao sang Gate G6 (Task `T-012`..`T-015`):**
   - `T-012`: Xử lý ETL sản xuất toàn bộ 9 năm (2016–2024), xác thực độ phủ khuyết Tháng 3/2024 (`OR-05`), nghiệm thu chính thức `TS-004`.
   - `T-013`, `T-014`: Tính toán 8 CORE KPIs và xuất báo cáo mô tả.
   - `T-015`: Giữ trạng thái `CONDITIONAL_NO_GO` theo `FP-DEC-017`.

---

## 5. ERR-04 — Lineage Identifier Semantics & Provisional Quarantine Scope

### 5.1. Ngữ nghĩa Chuẩn tắc của `_record_lineage_id`
- Trong mã nguồn [`src/flight_pipeline/ingestion/reader.py`](../../src/flight_pipeline/ingestion/reader.py), trường `_record_lineage_id` được sinh bởi hàm `attach_deterministic_lineage`.
- Thuật toán: `sha256(concat_ws("||", all_34_columns)) + "_" + occurrence_rank`.
- **Giới hạn ngữ nghĩa:** `_record_lineage_id` là một mã băm nội dung xác định kèm thứ tự xuất hiện nội bộ phân vùng, **KHÔNG PHẢI là chỉ số dòng vật lý (physical line index)** của tệp CSV trên ổ đĩa. Do Spark xử lý phân tán qua các split/partition, chỉ số dòng vật lý tuyệt đối trong tệp nguồn không được bảo tồn.
- Nghiêm cấm tuyên bố rằng `_record_lineage_id` chứng minh vị trí dòng vật lý 1:1 trong tệp CSV gốc.

### 5.2. Trạng thái Tạm thời của Chính sách Cách ly (`G3-COND-A`)
- Theo quyết định nghiệm thu Gate G3 ([`G3_OFFICIAL_SIGNOFF_HUMAN_ACCEPTANCE_RECORD.md`](G3_OFFICIAL_SIGNOFF_HUMAN_ACCEPTANCE_RECORD.md)), điều kiện `G3-COND-A` quy định rằng chính sách cách ly toàn bộ bản ghi (`whole-record quarantine`) đối với các trường hợp như `OP_CARRIER_FL_NUM <= 0` hoặc giá trị ngoại lai chỉ là **đề xuất sơ bộ (provisional proposal)**.
- `T-007` chỉ cung cấp bộ phân loại sơ bộ `IngestionRecordClassifier` và đường ống lưu trữ forensic `data/quarantine/<run_id>/`.
- **Nghĩa vụ chuyển giao:** Việc khảo sát phân bố thực tế của `OP_CARRIER_FL_NUM <= 0` trên dữ liệu thật và quyết định chính sách cách ly chính thức bắt buộc phải được thẩm tra độc lập tại Task `T-008` (Quality Engine) trước khi chạy smoke trên dữ liệu thật ở Gate G5.

---

## 6. Kết luận và Ánh xạ Quản trị

| Mã Sai khác | Trạng thái Trước Đính chính | Trạng thái Sau Đính chính Chuẩn tắc | Tác động Quản trị |
| :---: | :--- | :--- | :--- |
| **`ERR-01`** | Xuất hiện số liệu 54.72M dòng / 19.35GB rải rác | Ghim cứng **54,674,003 dòng** và **15,196,366,173 bytes** | Loại bỏ rủi ro sai lệch mẫu số hạch toán |
| **`ERR-02`** | Đếm kiểm thử thành phần không đồng bộ | Xác lập chính xác **135 PASS** (37 T-009 + 98 T-007) | Khóa baseline kiểm thử tự động G4 |
| **`ERR-03`** | Nhầm lẫn nghĩa vụ nạp thật 54.7M vào G4 | T-010/011 thuộc G5; T-012 thuộc G6; G4 chỉ synthetic | Bảo vệ tính toàn vẹn quy trình phân tầng Gate |
| **`ERR-04`** | Nguy cơ ngộ nhận lineage là physical line index | Khẳng định deterministic content hash; G3-COND-A chờ T-008 | Tuân thủ chính sách xuất xứ dữ liệu trung thực |

Phụ lục này có hiệu lực ngay lập tức và gắn liền với Biên bản Nghiệm thu Con người [`docs/05-evidence/T007_HUMAN_SIGNOFF_20261018.md`](T007_HUMAN_SIGNOFF_20261018.md).
