# T-005 R2: NHẬT KÝ THỰC THI VÀ MANIFEST HỒ SƠ PHÁT SINH
## (T-005 R2 EXECUTION LOG, ARTIFACT HASHES & REPRODUCIBILITY MANIFEST)

- **Mã tài liệu:** `T-005-R2-MANIFEST` (Execution Evidence & File Audit Manifest)
- **Gate kiểm soát:** `Gate G2` (Data Quality & Cohort Contracts)
- **Ngày lập:** 2026-10-16
- **Tác giả:** Senior Big Data Engineer & Evidence Documentation Specialist
- **Trạng thái tài liệu:** **`VERIFIED_IN_SESSION`**
- **Văn bản liên kết:** [`T005_FINAL_AUDIT_RECONCILIATION.md`](T005_FINAL_AUDIT_RECONCILIATION.md), [`T005_EVIDENCE_MATRIX.md`](T005_EVIDENCE_MATRIX.md), [`T005_TS011_TEST_SPEC.md`](T005_TS011_TEST_SPEC.md), [`T005_CONDITIONAL_NO_GO_PROPOSAL.md`](T005_CONDITIONAL_NO_GO_PROPOSAL.md).

---

## 1. THÔNG TIN MÔI TRƯỜNG VÀ VỊ TRÍ KHO LƯU TRỮ (REPOSITORY BASELINE)

- **Đường dẫn Kho lưu trữ (Sanitized Location):** `[WORKSPACE_ROOT]/US_FLIGHT_PERFORMANCE_DOCS_V1`  
  *(Đường dẫn cục bộ thực tế: `D:\Study\Code\Apache\Flight_Analyzt\US_FLIGHT_PERFORMANCE_DOCS_V1`)*
- **Hệ điều hành Thực thi:** Windows 11 (64-bit), PowerShell / Python 3.12 runtime.
- **Trạng thái Git Branch / Commit Hash:** **`NOT_AVAILABLE (STANDALONE_SNAPSHOT)`**  
  *Ghi chú kiểm toán:* Thư mục làm việc là bản snapshot phân phối/export tĩnh, không chứa thư mục `.git` cục bộ. Mọi tuyên bố về commit hash cụ thể đều không thể xác minh trên cây làm việc hiện tại.
- **Phiên bản Bộ Tài liệu Quy chuẩn:** `docs-v1.1` (Bất biến).

---

## 2. DANH MỤC TÀI LIỆU ĐẦU VÀO ĐÃ ĐỐI CHIẾU (INPUT DOCUMENTS INVENTORY)

| Đường dẫn Tệp Tài liệu Đầu vào | Phiên bản / Ngày Snapshot | Trạng thái Toàn vẹn / Hash Check | Vai trò Tham chiếu trong T-005 R2 |
|---|:---:|:---:|---|
| [`AGENTS.md`](../../AGENTS.md) | docs-v1.1 | Khớp SHA-256 trong manifest | Chính sách bảo mật và an toàn cho AI Agent |
| [`README.md`](../../README.md) | docs-v1.1 | Khớp SHA-256 trong manifest | Mục tiêu và phạm vi phân tích mô tả 2016–2024 |
| [`docs/04-execution/PROJECT_STATE.md`](../04-execution/PROJECT_STATE.md) | 2026-10-14 | Văn bản hiện hành | Trạng thái Gate G2 và lịch sử các task T-001..T-004 |
| [`docs/01-planning/BACKLOG.md`](../01-planning/BACKLOG.md) | docs-v1.1 | Văn bản hiện hành | Tiêu chí chấp nhận (DoD) của T-005 |
| [`docs/01-planning/ROADMAP.md`](../01-planning/ROADMAP.md) | docs-v1.1 | Văn bản hiện hành | Lộ trình các cổng G0–G7 |
| [`docs/02-design/DECISIONS.md`](../02-design/DECISIONS.md) | docs-v1.1 | Văn bản hiện hành | Quyết định FP-DEC-009, FP-DEC-013, FP-DEC-014 |
| [`docs/02-design/DATA_CONTRACT.md`](../02-design/DATA_CONTRACT.md) | docs-v1.1 | Văn bản hiện hành | Khế ước dữ liệu DC-07, DC-11, DC-12 |
| [`docs/02-design/DATA_DICTIONARY.md`](../02-design/DATA_DICTIONARY.md) | docs-v1.1 | Văn bản hiện hành | Khóa 6 cột thời tiết ở trạng thái BLOCKED |
| [`docs/02-design/KPI_SPEC.md`](../02-design/KPI_SPEC.md) | docs-v1.1 | Văn bản hiện hành | Danh mục 8 CORE KPIs và KPI-10 |
| [`docs/02-design/ANALYSIS_PROTOCOL.md`](../02-design/ANALYSIS_PROTOCOL.md) | docs-v1.1 | Văn bản hiện hành | Quy tắc cấm suy diễn nhân quả từ tương quan |
| [`docs/03-quality/TEST_PLAN.md`](../03-quality/TEST_PLAN.md) | docs-v1.1 | Văn bản hiện hành | Đặc tả kiểm thử TS-004, TS-010, TS-011 |
| [`docs/03-quality/RISK_REGISTER.md`](../03-quality/RISK_REGISTER.md) | docs-v1.1 | Văn bản hiện hành | Danh mục rủi ro R-04, OR-05, OR-07, OR-08 |
| [`docs/05-evidence/T001_R2_FINAL_REVIEW.md`](T001_R2_FINAL_REVIEW.md) | 2026-10-14 | Văn bản hiện hành | Bằng chứng nguồn gốc và phân loại METADATA_MATCH_ONLY |
| [`docs/05-evidence/T004_FINAL_QA_RECONCILIATION.md`](T004_FINAL_QA_RECONCILIATION.md) | 2026-10-14 | Văn bản hiện hành | Báo cáo QA thời gian và hòa giải 61 vs 90 PASS |
| 9 tệp [`schema_YYYY.json`](inputs/) (2016–2024) | 2026-08-23 | Khớp hash SOURCE_MANIFEST | Thống kê số dòng thô và số lượng khuyết thiếu 34 cột |

---

## 3. NHẬT KÝ LỆNH THỰC THI VÀ MÃ THOÁT THỰC TẾ (EXECUTED COMMANDS LOG)

Toàn bộ các lệnh kiểm thử và kiểm toán đã được thực thi thực tế trong môi trường máy chủ:

| STT | Lệnh Thực thi Chính xác (Exact CommandLine) | Phạm vi & Mục đích Thực thi | Mã Thoát (Exit Code) | Tóm tắt Kết quả Thực tế (Output Summary) | Bằng chứng Tham chiếu |
|:---:|---|---|:---:|---|:---:|
| **CMD-01** | `python tools/check_working_tree_consistency.py` | Kiểm toán tính toàn vẹn của toàn bộ 47 tệp manifest và cấu trúc thư mục repo. | **`0`** | `Working-Tree PASS assertions: 88; FAIL: 0. ALL WORKING-TREE CHECKS PASSED.` | Console log trực tiếp |
| **CMD-02** | `python tools/qa/verify_t004_time_representation.py` | Kiểm toán độc lập 11 artifact kiểm chuẩn thời gian T-004, đối chiếu 9 năm và ma trận an toàn. | **`0`** | `VERIFICATION SUMMARY: 90 PASS, 0 FAIL. ALL 90 T-004 FINAL QA CHECKS PASSED.` | Console log trực tiếp |
| **CMD-03** | Python script kiểm toán khuyết thiếu đa năm trên 9 `schema_YYYY.json` | Đọc và trích xuất số lượng null chính xác của 6 cột thời tiết từ 2016 đến 2024. | **`0`** | Xác nhận: Tổng dòng $54,674,003$; null nơi đi: $13,474$ dòng ($0.0246\%$); null nơi đến: $15,046$ dòng ($0.0275\%$). Bằng nhau tuyệt đối theo bộ 3 ở mức biên. | Bảng Mục 4 trong T005_FINAL_AUDIT |
| **CMD-04** | Python scratch script `check_weather_sample.py` | Quét luồng giới hạn bộ nhớ $100,000$ dòng đầu năm 2016 để tìm min/max các cột thời tiết. | **`0`** | `O_TEMP`: min = -28.3, max = 45.6; `O_PRCP`: min = 0.0, max = 253.7; `O_WSPD`: min = 0.0, max = 92.5. | `scratch/check_weather_sample.py` |
| **CMD-05** | Python scratch script `inspect_temp_extremes.py` | Truy vết dòng vật lý cụ thể chứa cực trị thời tiết tại các sân bay thực tế năm 2016. | **`0`** | Row 46610 (MSP, -25.6), Row 50169 (MSP, -28.3), Row 55086 (LAS, +41.7). | `scratch/inspect_temp_extremes.py` |
| **CMD-06** | Python scratch script `check_yx3624_weather.py` (Nhiệm vụ nền `task-112`) | Đọc chính xác 2 dòng vật lý 6,384,132 và 6,384,133 của chuyến bay YX 3624 trong tệp 2018 (1.94 GB). | **`0`** | Xác nhận: Cả 2 dòng (cất cánh cách nhau gần 10 tiếng thực tế) có giá trị thời tiết y hệt nhau: `O_TEMP=27.8, O_PRCP=0.0, O_WSPD=9.4, D_TEMP=29.4, D_PRCP=0.0, D_WSPD=24.1`. | Log `task-112.log` |
| **CMD-07** | Python script tính toán mã băm SHA-256 các tệp phát sinh T-005 R2 | Đo đạc dung lượng byte và tính hash SHA-256 cho 4 tệp báo cáo markdown vừa tạo. | **`0`** | Trả về độ dài byte và chuỗi hash hex 64 ký tự của từng tệp (chi tiết tại Mục 5). | Console log trực tiếp |

---

## 4. HẠCH TOÁN KỊCH BẢN TẠM THỜI VÀ GIỚI HẠN LƯU TRỮ (SCRATCH SCRIPTS ACCOUNTING)

Trong quá trình điều tra kỹ thuật, 4 kịch bản Python đã được tạo ra trong thư mục scratch của phiên làm việc (`C:\Users\Heikapu\.gemini\antigravity-cli\brain\c4a94221-adc9-4c34-ab69-1c88a5fd6082\scratch\`):
1. `sample_weather.py` (533 bytes): Đọc 20 dòng mẫu từ `flight_with_weather_2016.csv`.
2. `check_weather_sample.py` (773 bytes): Quét min/max trên mẫu $100,000$ dòng.
3. `inspect_temp_extremes.py` (682 bytes): In chi tiết các dòng chứa nhiệt độ cực đoan tại MSP và LAS.
4. `check_yx3624_weather.py` (621 bytes): Đọc chính xác các trường thời tiết của cặp YX 3624 tại dòng 6,384,132 và 6,384,133.

**Tuyên bố Giới hạn Lưu trữ (Persistence Limitation):**  
Các tệp kịch bản scratch này nằm bên ngoài thư mục repository và gắn liền với phiên làm việc của Agent. Bằng chứng sinh ra từ các tệp này được phân loại chính xác là **`REPORTED_IN_LOCAL_SESSION_SCRATCH_ONLY`**. Để phục vụ tái lập độc lập trong tương lai mà không phụ thuộc vào bộ nhớ agent, các kết luận cốt lõi đã được ghi lại bằng văn bản trong hồ sơ T-005 R2.

---

## 5. MANIFEST TỆP PHÁT SINH VÀ MÃ BĂM SHA-256 (GENERATED FILES MANIFEST)

Dưới đây là danh mục chính xác các tệp báo cáo kiểm chuẩn mới được tạo lập trong nhiệm vụ T-005 R2 tại thư mục `docs/05-evidence/`:

| Tên Tệp Báo cáo Phát sinh | Đường dẫn Tuyệt đối trong Hệ thống | Dung lượng (Bytes) | Mã băm SHA-256 (Content Hash Digest) | Trạng thái Kiểm tra Sau khi Ghi |
|---|---|:---:|---|:---:|
| **`T005_FINAL_AUDIT_RECONCILIATION.md`** | `docs/05-evidence/T005_FINAL_AUDIT_RECONCILIATION.md` | $19,047$ bytes | `0ae421b54fc0dab37a0fc7385010461f404112b3ff5e5b620bda0918431f18ed` | **PASS (Đọc lại OK, UTF-8 hợp lệ)** |
| **`T005_EVIDENCE_MATRIX.md`** | `docs/05-evidence/T005_EVIDENCE_MATRIX.md` | $13,414$ bytes | `658bedfd7610912d145fe701aeb9dc7b602abab9f0252bb0d1baad246169c134` | **PASS (Đọc lại OK, UTF-8 hợp lệ)** |
| **`T005_TS011_TEST_SPEC.md`** | `docs/05-evidence/T005_TS011_TEST_SPEC.md` | $19,136$ bytes | `b93c4b388999a70d0a830ee000fdf2bd1661c410c53026a6bd93556bf17d4886` | **PASS (Đọc lại OK, UTF-8 hợp lệ)** |
| **`T005_CONDITIONAL_NO_GO_PROPOSAL.md`** | `docs/05-evidence/T005_CONDITIONAL_NO_GO_PROPOSAL.md` | $14,007$ bytes | `92c58405625a65cfb14d27cabac0dfcbe4823087d6e8a1fb5b7fe45f31698707` | **PASS (Đọc lại OK, UTF-8 hợp lệ)** |
| **`T005_EXECUTION_AND_FILE_MANIFEST.md`** | `docs/05-evidence/T005_EXECUTION_AND_FILE_MANIFEST.md` | *(Tệp hiện tại)* | *[Không tính self-hash để tránh nghịch lý đệ quy]* | **PASS (Đã hoàn thiện)** |

*Ghi chú kỹ thuật:* Tuân thủ nghiêm ngặt quy định không tạo mã băm tự thân (*self-hash*), tệp manifest này không tự băm chính nó.

---

## 6. CÁC TỆP KHÔNG THỂ XÁC MINH HOẶC THIẾU HỤT TỪ NGUỒN (UNVERIFIABLE EVIDENCE)

Trong suốt quá trình kiểm toán, các tệp và thông tin sau đây được ghi nhận chính thức là **hoàn toàn vắng bóng trong kho lưu trữ**:
1. **Mã nguồn tiền xử lý ETL của bên thứ ba:** Không có script Python/SQL chứng minh thuật toán join thời tiết và cách xử lý múi giờ (`UNKNOWN`).
2. **Tệp Giấy phép Bản quyền Thời tiết:** Không có tệp `LICENSE_WEATHER` hoặc điều khoản phân phối lại của Meteostat (`UNKNOWN`).
3. **Mã băm SHA-256 của 9 tệp raw CSV:** Kho lưu trữ không có SHA-256 baseline từ cổng phát hành gốc của BTS TranStats (`IDENTITY_UNVERIFIED`).
4. **Dữ liệu chuyến bay Tháng 3/2024:** 31 ngày của Tháng 3/2024 hoàn toàn khuyết thiếu ($0$ bản ghi, `OR-05: OPEN_QUALITY_DEFECT`).

---

## 7. KẾT LUẬN VÀ TUYÊN BỐ DỪNG LẠI (FINAL DECLARATION)

- Toàn bộ hồ sơ kiểm toán **T-005 R2** đã hoàn tất việc tạo lập và đối soát 5 tệp bằng chứng tự thân, bảo đảm tính minh bạch khoa học cao nhất.
- Không có bất kỳ lệnh sửa đổi trái phép nào được thực hiện trên mã nguồn sản xuất, tài liệu quản trị hay dữ liệu thô.
- Đề xuất phán quyết kỹ thuật **`CONDITIONAL_NO_GO`** đã sẵn sàng chờ Người phụ trách Dự án (Project Lead) xem xét ký duyệt.
