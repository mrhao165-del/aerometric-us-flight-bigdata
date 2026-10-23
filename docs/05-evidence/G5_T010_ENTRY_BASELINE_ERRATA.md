# G5-T010-ENTRY-BASELINE-ERRATA: Đính chính Thông số Cơ sở Dữ liệu Nguồn Năm 2016 tại Cổng G5

**Mã tài liệu:** `G5-T010-ERRATA-01`  
**Dự án:** US Flight Performance Analysis 2016–2024  
**Cổng quản trị:** `Gate G5 — Bounded Real Data Smoke, Resource Benchmark & BTS Unit Reconciliation`  
**Nhiệm vụ:** `T-010 — Bounded Real-Data Smoke & Resource Benchmark`  
**Ngày lập:** `2026-10-18`  
**Thẩm quyền ban hành:** `Project Lead Instruction (MASTER-G5-T010 Mandatory Phase 0)`  
**Trạng thái tài liệu:** **`CANONICAL_ERRATA_OFFICIALLY_RATIFIED`**  
**Tham chiếu gốc bị đính chính:** [`docs/05-evidence/G5_ENTRY_HANDOFF.md`](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/docs/05-evidence/G5_ENTRY_HANDOFF.md) Mục 1.1, Mục 2.2, Mục 4

---

## 1. Bối cảnh và Mục đích Đính chính

Trong tài liệu bàn giao [`docs/05-evidence/G5_ENTRY_HANDOFF.md`](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/docs/05-evidence/G5_ENTRY_HANDOFF.md), các thông số định lượng cho tệp dữ liệu nguồn năm 2016 (`data/raw/tabular/2016/flight_with_weather_2016.csv`) đã bị ghi nhầm từ một ngữ cảnh mô phỏng/bản ghi khác thay vì trích xuất từ nguồn thẩm quyền chuẩn tắc của đồ án.

Kiểm toán độc lập theo chỉ thị `MASTER-G5-T010 Phase 0` đã phát hiện sự sai lệch này. Để bảo đảm tính liêm chính documentary integrity, tuân thủ nguyên tắc bất biến bằng chứng (immutable evidence preservation) và ngăn chặn việc các assertion kiểm thử tự động tại Gate G5 sử dụng sai thông số cơ sở, văn bản phụ lục đính chính này xác lập thông số chuẩn tắc 100% đồng thuận giữa các nguồn kiểm toán.

---

## 2. Bảng Đối chiếu Chi tiết Giữa Thông số Sai và Giá trị Chuẩn tắc

| Thuộc tính định lượng | Giá trị sai trong `G5_ENTRY_HANDOFF.md` | Giá trị Chuẩn tắc Thực tế (`Canonical Truth`) | Nguồn Thẩm quyền Xác nhận |
|---|:---:|:---:|---|
| **Năm khảo sát (`Year`)** | 2016 | **2016** | Khớp định danh năm |
| **Đường dẫn tệp nguồn** | `data/raw/tabular/2016/flight_with_weather_2016.csv` | **`data/raw/tabular/2016/flight_with_weather_2016.csv`** | Đường dẫn tương đối chuẩn tắc |
| **Số hàng dữ liệu logic (`Audited Rows`)** | `5,617,658` *(Sai lệch +79,671 dòng)* | **`5,537,987`** | G1 `schema_2016.json`, `AUDITED_SOURCE_INVENTORY[2016]`, `T007_LOCAL_RAW_SHA256_CANDIDATE.json`, đếm thực tế non-header |
| **Kích thước tệp (`File Bytes`)** | `1,556,608,989` bytes *(Sai lệch +18,181,537 bytes)* | **`1,538,427,452`** bytes | G1 `schema_2016.json` (`source_signature.file_size_bytes`), filesystem stat vật lý |
| **Mã băm SHA-256 ứng viên cục bộ** | `632d43e5898b1eb798363a02fa023eec7fa6d38e0ba8f368e7ec8396aa700540` *(Mã băm sai)* | **`4ed92ed732721a38ae28325135fad63436347613674ad96c1b273eb9d44cef34`** | `T007_LOCAL_RAW_SHA256_CANDIDATE.json` (`sources["2016"].sha256_calculated`), streaming hash vật lý |
| **Số lượng cột dữ liệu (`Column Count`)** | 34 | **34** | Khớp canonical schema factory |
| **Phạm vi ngày bay (`Date Range`)** | Không ghi rõ | **`2016-01-01` đến `2016-12-31`** | Đầy đủ 366 ngày (năm nhuận 2016), không khuyết tật coverage như năm 2024 |

---

## 3. Bằng chứng Bốn Nguồn Độc lập Đối chiếu Đồng thuận 100%

Quá trình kiểm chứng tự động tại thời điểm mở Gate G5 xác nhận sự trùng khớp tuyệt đối giữa bốn nguồn thẩm quyền độc lập:

1. **Hồ sơ Kiểm toán G1 (`docs/05-evidence/inputs/schema_2016.json`):**
   - `row_count`: `5,537,987`
   - `source_signature.file_size_bytes`: `1,538,427,452`
   - `column_count`: `34`
2. **Danh mục Kiểm toán Sản xuất (`src/flight_pipeline/ingestion/source_validator.py`):**
   - `AUDITED_SOURCE_INVENTORY[2016].audited_row_count`: `5,537,987`
   - `AUDITED_SOURCE_INVENTORY[2016].audited_byte_size`: `1,538,427,452`
3. **Sổ bộ Băm Ứng viên Cục bộ T-007 (`docs/05-evidence/T007_LOCAL_RAW_SHA256_CANDIDATE.json`):**
   - `sources["2016"].audited_row_count`: `5,537,987`
   - `sources["2016"].file_size`: `1,538,427,452`
   - `sources["2016"].sha256_calculated`: `4ed92ed732721a38ae28325135fad63436347613674ad96c1b273eb9d44cef34`
4. **Hệ thống tệp Thực tế (`data/raw/tabular/2016/flight_with_weather_2016.csv`):**
   - `p.stat().st_size`: `1,538,427,452` bytes.
   - Streaming SHA-256 đọc từng khối 1 MB: `4ed92ed732721a38ae28325135fad63436347613674ad96c1b273eb9d44cef34`.
   - Đếm dòng vật lý loại trừ tiêu đề: chính xác `5,537,987` dòng logic.

---

## 4. Quyết định Quản trị và Hiệu lực Áp dụng cho Nhiệm vụ T-010

1. **Bảo tồn Bằng chứng Lịch sử:** Tài liệu [`G5_ENTRY_HANDOFF.md`](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/docs/05-evidence/G5_ENTRY_HANDOFF.md) được bảo tồn nguyên vẹn byte-for-byte; không sửa đổi hoặc làm giả lịch sử của snapshot đã nghiệm thu.
2. **Quy tắc Kiểm thử Bắt buộc:** Toàn bộ các kiểm thử tiền trạm (Preflight assertions), cân bằng hạch toán dòng DC-11 (`N_raw == N_accepted + N_quarantined + N_rejected`), kiểm chứng Parquet readback và báo cáo tài nguyên TS-014 trong nhiệm vụ `T-010` phải sử dụng **mẫu số và số đếm chuẩn tắc `5,537,987` dòng và `1,538,427,452` bytes**.
3. **Cảnh báo Danh tính Upstream:** Việc mã băm SHA-256 khớp chính xác với candidate hash chỉ chứng minh tính toàn vẹn của bản sao cục bộ so với thời điểm băm T007-02B; danh tính nội dung upstream vẫn tiếp tục giữ nguyên trạng thái quản trị **`OR-08 = IDENTITY_UNVERIFIED`** (`CANDIDATE_PENDING_HUMAN_ACCEPTANCE`).
