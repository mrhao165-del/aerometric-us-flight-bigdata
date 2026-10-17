# HỒ SƠ NGHIỆM THU KỸ THUẬT NHIỆM VỤ T-003 (T-003 SIGNOFF RECORD)

- **Mã nhiệm vụ:** `T-003` (Core KPI & Unit Contract Audit)
- **Gate kiểm soát:** `G2` (Data Quality, Cohort & Metric Contracts)
- **Ngày nghiệm thu:** 2026-10-14
- **Vai trò thực hiện:** Senior Data Engineer, Data Quality Auditor & Technical Reviewer
- **Kết luận xếp loại nhiệm vụ:** **`PASS_WITH_OPEN_RISKS`** (Trong phạm vi thiết kế hợp đồng dữ liệu và kiểm toán tài liệu)
- **Trạng thái Gate G2:** **`IN_PROGRESS / NOT_PASSED`** (Tiếp tục thực hiện T-004 và T-005 trước khi nghiệm thu Gate)
- **Văn bản tuân thủ:** [`AGENTS.md`](../../AGENTS.md), [`docs/01-planning/BACKLOG.md`](../01-planning/BACKLOG.md), [`docs/02-design/KPI_SPEC.md`](../02-design/KPI_SPEC.md), [`docs/02-design/DATA_CONTRACT.md`](../02-design/DATA_CONTRACT.md), [`docs/02-design/DECISIONS.md`](../02-design/DECISIONS.md), [`docs/03-quality/TEST_PLAN.md`](../03-quality/TEST_PLAN.md), [`docs/04-execution/PROJECT_STATE.md`](../04-execution/PROJECT_STATE.md).

---

## 1. Tuyên bố Nghiệm thu (Sign-off Declaration)

Nhiệm vụ **T-003 (Core KPI & Unit Contract Audit)** chính thức được nghiệm thu đạt trạng thái **`PASS_WITH_OPEN_RISKS`** trong phạm vi thiết kế kỹ thuật, kiểm chuẩn hợp đồng số học và kiểm toán tài liệu.

Toàn bộ 4 vấn đề kỹ thuật phát hiện trong đợt rà soát cuối (F10–F13) đã được giải quyết triệt để và kiểm chứng bằng công cụ tự động:
1. **F10 (Xác thực Cực trị `ARR_DELAY`):** Đã kiểm tra trực tiếp từ 9 tệp siêu dữ liệu `schema_2016.json` đến `schema_2024.json` trong thư mục `inputs/` (ví dụ [`inputs/schema_2016.json`](inputs/schema_2016.json)):
   - Cực tiểu toàn cục (*Overall Min*): **$-238.0$** (năm 2017).
   - Cực đại toàn cục (*Overall Max*): **$+4405.0$** (năm 2023).
   - Dải số cực đoan lạc hậu không có cơ sở kiểm toán đã bị loại bỏ hoàn toàn khỏi toàn bộ hồ sơ bằng chứng.
2. **F11 (Chuẩn hóa Nhãn Đơn vị Đo Canonical):** Đã đồng bộ nhãn đơn vị đo cho toàn bộ 7 thước đo số và 5 KPI tính theo phút về định danh duy nhất:
   - Trạng thái đơn vị đo: **`OFFICIAL_MINUTES_EMPIRICALLY_CONSISTENT_PROVISIONAL`**.
   - `KPI-01`: **`COUNT_INTEGER`**; `KPI-02` và `KPI-04`: **`DIMENSIONLESS_RATIO`**.
   - Tuyệt đối không nâng cấp sớm lên `VERIFIED_AGAINST_UPSTREAM` khi chưa đối chiếu bản ghi với BTS TranStats.
3. **F12 (Phân định Ranh giới Mẫu Thử vs Quần thể Toàn cục):**
   - Phép kiểm toán số học trên $10,000$ dòng CSV 2018 chỉ cung cấp bằng chứng thực nghiệm trên mẫu kiểm tra.
   - Không tuyên bố mẫu $10,000$ dòng đại diện cho toàn bộ $54,674,003$ dòng.
   - Việc quét toàn bộ 54.67 triệu dòng bằng Spark ở G5 chứng minh tính nhất quán số học nội bộ nhưng không thay thế được phép đối chiếu bản ghi upstream BTS. Rủi ro đơn vị đo được giữ ở mức `PROVISIONAL`.
4. **F13 (Bộ Kiểm chuẩn Hợp đồng Tự động & Bảo vệ Quy tắc Chất lượng):**
   - Script [`tools/qa/verify_t003_contract_consistency.py`](../../tools/qa/verify_t003_contract_consistency.py) đã tích hợp đầy đủ các bài kiểm tra F10, F11, F12, F13, đạt **133 PASS / 0 FAIL**.
   - Đặc tả fixture `FIX-13` xác nhận rõ: Quy tắc Zero Arbitrary Deduplication không cho phép bất kỳ bản ghi nào bỏ qua các quy tắc kiểm tra chất lượng dữ liệu cốt lõi (schema, non-null, numeric bounds).

---

## 2. Danh mục 8 Rủi ro Mở Bảo lưu & Chuyển giao (Open Risks Registry)

T-003 nghiệm thu kèm theo việc bảo lưu đầy đủ 8 rủi ro mở sau đây, chuyển giao cho các nhiệm vụ tiếp theo và Gate G5 kiểm chứng bằng Spark:

| Mã Rủi ro | Tóm tắt Nội dung Rủi ro | Trạng thái Chuyển giao | Nhiệm vụ / Gate Tiếp nhận | Phương thức Xử lý & Nghiệm thu |
|:---:|---|:---:|:---:|---|
| **OR-01** | Cột `FLIGHTS` đồng nhất bằng 1.0 trên toàn bộ $54,674,003$ dòng. | Đã khóa thiết kế | T-007 / T-008 / G4 / G5 | Mẫu số chuẩn hóa `count_records(C)`; `KPI-12` bị khóa `BLOCKED / REDUNDANT`. Kiểm chứng trên Spark. |
| **OR-02** | Nguy cơ mất trễ cực đoan nếu deduplicate tùy tiện (ca YX 3624). | Đã lập fixture bảo vệ | T-008 / G4 / G5 (`TS-020`, `TS-021`) | Duy trì chính sách Zero Arbitrary Deduplication; kiểm tra bộ sinh surrogate key không gộp nhầm bản ghi. |
| **OR-03** | Đơn vị 7 trường độ trễ/thời lượng giữ nhãn `PROVISIONAL`. | Bảo lưu rủi ro | G5 / G6 Spark Scan & BTS Match | Chờ đối chiếu mẫu trực tiếp (*bounded record match*) với dữ liệu BTS TranStats nguyên bản tại G5. |
| **OR-04** | Thiếu trường `CANCELLED` và `DIVERTED` trong 34 cột raw CSV. | Đã đóng phạm vi | Đã chốt hợp đồng | `KPI-11` chính thức nằm ngoài 8 CORE KPIs. Không mở rộng schema ngoài 34 cột. |
| **OR-05** | Tính liên tục 366 ngày của năm nhuận 2024 chưa đếm distinct dates. | Bảo lưu | **T-004** / `TS-004` (G2/G6) | Kiểm toán calendar coverage năm 2024 trong T-004. |
| **OR-06** | Rollover mốc giờ thực tế (`ARR_TIME`, `DEP_TIME`) và bản chất YX 3624. | Bảo lưu | **T-004** (G2 Time Audit) | Phân tích trường thời gian an toàn, hiện tượng bay qua nửa đêm và YX 3624 tại T-004. |
| **OR-07** | Dữ liệu thời tiết thiếu trạm đo, mốc thời gian và đơn vị đo. | `CONDITIONAL_PENDING` | **T-005** (G2 Weather Audit) | `KPI-10` giữ `CONDITIONAL_PENDING`, không chặn 8 CORE KPIs. Đưa ra quyết định GO / NO-GO tại T-005. |
| **OR-08** | Chưa có SHA-256 tham chiếu từ cổng phát hành gốc của bên thứ ba. | `METADATA_MATCH_ONLY` | T-007 / `TS-019` (G4) | Lập baseline SHA-256 nội bộ bất biến khi khởi tạo pipeline ingestion tại T-007. |

---

## 3. Trạng thái Quyết định Thiết kế Kiến trúc (ADRs) & Kiểm thử

Các đề xuất kiến trúc và kiểm thử được ghi nhận trong hồ sơ T-003 giữ nguyên trạng thái **`PROPOSED`**, không tự ý nâng cấp thành `APPROVED` trước khi có quyết định phê duyệt chính thức từ người phụ trách:
- **`FP-DEC-015` (Thuật toán Phân vị PySpark):** Trạng thái **`PROPOSED`** (Chuẩn hóa `percentile_approx` với accuracy=10000, rank error $\le 0.01\%$, kiểm chứng thực nghiệm tại Gate G5).
- **`FP-DEC-016` (Chính sách Phân tầng Min-N):** Trạng thái **`PROPOSED`** (Ngưỡng 1000/365/100 bản ghi, gắn nhãn `SUPPRESSED` / `LOW_SAMPLE_CAUTION`).
- **`TS-021` (Bài kiểm thử Duplicate Preservation & Event-Identity Guard):** Trạng thái **`PROPOSED`** (Bổ sung vào bộ test suite của Gate G4).

---

## 4. Hồ sơ Bằng chứng Đã Thiết lập (Evidence Artifacts Registry)

| STT | Tập tin Bằng chứng | Mô tả Nội dung | Trạng thái |
|:---:|---|---|:---:|
| 1 | [`T003_UNIT_VERIFICATION.md`](T003_UNIT_VERIFICATION.md) | Kiểm chứng đơn vị đo 7 trường cốt lõi, quy ước dấu và ranh giới mẫu vs quần thể | **FINAL / SIGNED** |
| 2 | [`T003_KPI_CONTRACT_REVIEW.md`](T003_KPI_CONTRACT_REVIEW.md) | Hợp đồng toán học, ranh giới mẫu số và đặc tả 8 CORE KPIs (`KPI-01`..`KPI-08`) | **FINAL / SIGNED** |
| 3 | [`T003_PERCENTILE_AND_MIN_N_DECISIONS.md`](T003_PERCENTILE_AND_MIN_N_DECISIONS.md) | Phân tích thuật toán phân vị, sai số rank, chi phí Spark và phân tầng min-N | **FINAL / SIGNED** |
| 4 | [`T003_TEST_FIXTURE_SPEC.md`](T003_TEST_FIXTURE_SPEC.md) | Đặc tả 14 fixture kiểm thử đơn vị (`FIX-01` đến `FIX-14`) | **FINAL / SIGNED** |
| 5 | [`T003_FIX14_accounting_fixture.csv`](T003_FIX14_accounting_fixture.csv) | Dữ liệu CSV thực thi cho bài kiểm thử hạch toán 3 trạng thái dòng (5 dòng) | **VERIFIED** |
| 6 | [`T003_FIX14_accounting_fixture.json`](T003_FIX14_accounting_fixture.json) | Oracle siêu dữ liệu và kết quả kỳ vọng độc lập cho FIX-14 | **VERIFIED** |
| 7 | [`T003_FINAL_CLOSEOUT_VERIFICATION.md`](T003_FINAL_CLOSEOUT_VERIFICATION.md) | Báo cáo đối chiếu 9 phát hiện F01–F09 sau vòng CLOSEOUT | **FINAL / SIGNED** |
| 8 | [`T003_FINAL_GATE_RECOMMENDATION.md`](T003_FINAL_GATE_RECOMMENDATION.md) | Báo cáo đối soát tiêu chí nghiệm thu BACKLOG và khuyến nghị chuyển giao | **FINAL / SIGNED** |
| 9 | [`tools/qa/verify_t003_contract_consistency.py`](../../tools/qa/verify_t003_contract_consistency.py) | Script tự động kiểm tra 133 khẳng định nhất quán hợp đồng và số học (133 PASS) | **AUTOMATED QA PASS** |

---

## 5. Kết luận Điều hành & Chuyển giao Nhiệm vụ Kế tiếp

- Nhiệm vụ **T-003** chính thức **HOÀN TẤT VÀ ĐÓNG LẠI** với kết quả `PASS_WITH_OPEN_RISKS`.
- Gate **G2** tiếp tục ở trạng thái **`IN_PROGRESS / NOT_PASSED`**.
- Đủ điều kiện và an toàn để chuyển sang **Task T-004: Safe Time Representation & Overnight Operational Timestamps Audit**.
