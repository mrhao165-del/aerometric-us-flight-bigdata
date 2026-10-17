# Kiểm toán chéo bộ hồ sơ US Flight Performance — docs-v1.0

**Ngày rà soát:** 2026-10-13  
**Đối tượng:** `US_FLIGHT_PERFORMANCE_DOCS_A_B_C_v1.0.zip` (45 thành phần), 18 tài liệu A/B/C, 8 tài liệu chuyên môn/điều phối, các hồ sơ gốc và manifests.  
**Phạm vi:** rà soát **nội dung/tài liệu**, không chạy Spark, không truy cập 9 CSV raw cỡ lớn, không xác nhận dữ liệu đầu nguồn ngoài những kiểm toán đã đính kèm. **Không chỉnh sửa ZIP v1.0**.

## 1. Phán quyết

**Chưa đạt trạng thái `DOCS_CONSISTENCY_PASS`.** ZIP và các số tổng hợp thống kê không hỏng; các quy tắc phân tích mô tả chính nhìn chung đồng hướng. Tuy nhiên vẫn tồn tại xung đột giữa timeline và phân công task, một khác biệt về số KPI lõi, nhiều điểm chưa đủ đặc tả để AI thực hiện nhất quán, và 3 tham chiếu văn bản sai. Cần bản vá tài liệu có kiểm chứng (`docs-v1.1`) trước khi giao tự động những gate triển khai mã nguồn.

### Kiểm tra tự động thực sự đã chạy

| Kiểm tra | Kết quả | Giới hạn |
|---|---|---|
| Mở ZIP, `ZipFile.testzip()` | PASS: 45 thành phần, không có CRC error | Chỉ integrity của gói |
| So sánh ZIP với file đang có trong thư mục đã đóng gói | PASS: các bytes tương đồng | Không xác thực logic |
| `PACKAGE_MANIFEST.json`: 44 file được ghi nhận, đối chiếu bytes/SHA256 | PASS: 44/44 | Manifest không tự kiểm tra cross-document semantics |
| 9 `schema_YYYY.json` | PASS parse, `is_complete=true`, 34 columns đúng thứ tự | Không đọc lại CSV raw |
| Tổng 9 `row_count` | 54.674.003 (PASS) | Số hàng trong dataset, chưa được chứng minh là tổng số chuyến tại Mỹ |
| Tổng 9 `arr_delay.gte_15.count` | 10.116.916 (PASS) | Audit-derived, không phải KPI Spark mới |
| Tỷ lệ audit `ARR_DELAY>=15` | 18,5040703897% (PASS) | Chỉ khi cùng định nghĩa/audit cohort |
| Mean có trọng số của `ARR_DELAY` | 4,4770985216 (PASS) | Đơn vị cần được xác minh theo nguồn |
| Missing theo cột thời tiết | O_*: 13.474 mỗi cột; D_*: 15.046 mỗi cột (PASS) | Không chứng minh weather unit, valid time/join |
| Tham chiếu file MD hiện hữu | Có lỗi trong docs soạn mới | Các tham chiếu đến repo Aeolus lịch sử nằm **trong source evidence** không tính lỗi gói mới |

## 2. Phát hiện bắt buộc sửa trước G3/G4

### F-01 — HIGH — Backlog đặt bước viết code vào G3 nhưng Roadmap xem G3 là giai đoạn thiết kế

- **Nguồn:** `docs/01-planning/ROADMAP.md` (G3: *kiến trúc/ETL plan và bộ kiểm thử*, exit review fixtures/schema/command dự kiến; G4: *cấu hình dự án...*, repo/CI đã chạy); `docs/01-planning/BACKLOG.md` (T-007 *viết ingestion + tests* và T-008 *viết quality/quarantine* thuộc **G3**, trong khi T-009 setup tests/lint/CI thuộc **G4**); `PROJECT_STATE.md` giữ cùng phân giai đoạn.
- **Vì sao xung đột:** Nếu Agent tuân Roadmap, G3 chưa triển khai pipeline; nếu tuân Backlog, G3 phải hoàn thành code và tests trước khi G4 thiết lập project/test runner. G3–G4 không còn gate rạch ròi.
- **Khắc phục:** Giữ G3 cho phê duyệt kiến trúc/fixtures/contracts, đưa thiết lập môi trường và CI skeleton sang đầu G4, sau đó T-007/T-008 triển khai trong G4 (đổi dependency IDs nếu cần); G5 mới smoke. Cập nhật đồng thời `ROADMAP`, `BACKLOG`, `PROJECT_STATE`, `TEST_PLAN`.

### F-02 — HIGH — “Khóa 5 KPI lõi” không khớp catalog 8 KPI `CORE_DRAFT`

- **Nguồn:** `BACKLOG.md` T-003: “Khóa **5 KPI lõi**”; `KPI_SPEC.md`: KPI-01 đến KPI-08 đều `CORE_DRAFT`; `PRD.md` đánh dấu RQ-01 đến RQ-05 bắt buộc, cần chỉ số taxi/elapsed ở KPI-07/08.
- **Hệ quả:** Một Agent có thể chọn KPI-01..05 và cho T-003 PASS, bỏ lỡ KPI-06/07/08 và đầu ra RQ-05; Agent khác hiểu phải duyệt cả 8. Không thể nghiệm thu thống nhất.
- **Khắc phục:** Hoặc quy định chính xác danh sách **5 KPI minimal** (và chuyển các KPI không thuộc đó sang giai đoạn có tên, ưu tiên rõ), hoặc sửa T-003 thành “review/khóa toàn bộ CORE KPI-01..08”. Tôi khuyên giải pháp thứ hai nếu RQ-05 vẫn Must.

### F-03 — HIGH — `coverage_rate` và số hàng bị loại thiếu một định nghĩa duy nhất

- **Nguồn:** `KPI_SPEC.md` yêu cầu các output phải có `count_records`, `count_metric_valid`, `excluded_count`, `coverage_rate`, nhưng chỉ định nghĩa `N_rows` và `N_valid(field)`; `DATA_CONTRACT.md` định nghĩa `raw_rows = accepted + quarantined + rejected`; `ANALYSIS_PROTOCOL.md` đòi công khai `n` và coverage.
- **Vì sao nguy hiểm:** `coverage_rate` có thể bị hiểu là tỷ lệ còn lại từ raw, tỷ lệ field valid trong accepted, hoặc tỷ lệ thị trường Mỹ được bao phủ. Ba đại lượng hoàn toàn khác nhau. `excluded_count` cũng chưa nói so với raw, accepted hay metric valid; `accepted`, `quarantined`, `rejected` chưa được định nghĩa mutually exclusive.
- **Khắc phục:** Tạo glossary ngay trong `DATA_CONTRACT` và chuẩn hóa output theo `raw_row_count`, `accepted_row_count`, `quarantined_row_count`, `rejected_row_count`, `metric_eligible_count`, `metric_excluded_count`, `metric_valid_rate=metric_eligible_count/accepted_row_count` (khi mẫu số >0). Dùng nhãn riêng `source_coverage_status` cho độ bao phủ ngoài dataset (chưa xác minh), **không** gắn tên `coverage_rate` chung chung. Viết fixture các trạng thái, null/invalid và nhóm mẫu số 0 vào TEST_PLAN. Giá trị nào chưa chuẩn y thì giữ PROPOSED.

### F-04 — MEDIUM-HIGH — Quy tắc qua G2 và các blocker về đơn vị chưa được nối rõ với task/test

- **Nguồn:** `ROADMAP.md` yêu cầu có bằng chứng về **đơn vị, denominator, coverage, date policy** của KPI bắt buộc trước G2 PASS; `DATA_DICTIONARY.md` nói đơn vị của delay/taxi/elapsed chưa được xác minh tại nguồn; `BACKLOG.md` T-001/002/003 không ghi tường minh nhiệm vụ xác nhận đơn vị các measure bắt buộc; T-005 chỉ dành cho Weather.
- **Hệ quả:** Có thể tuyên bố “T-003 DONE” sau khi thống nhất công thức mặc dù đơn vị/minutes còn mở, rồi vẫn không đủ tiêu chí G2. Cần phân biệt policy cho KPI dùng `ARR_DELAY`/`DEP_DELAY` sẵn có và các KPI thời lượng RQ-05.
- **Khắc phục:** Thêm nhiệm vụ/acceptance về units/sign conventions cho `ARR_DELAY`, `DEP_DELAY`, `TAXI_IN`, `TAXI_OUT`, `AIR_TIME`, `CRS_ELAPSED_TIME`, `ACTUAL_ELAPSED_TIME`. G2 PASS chỉ nếu các metric Must còn lại có evidence hoặc được chính thức hạ scope bằng ADR.

### F-05 — MEDIUM — Task Weather optional bị đánh `BLOCKED` trong Gate G6 mà không có quy tắc miễn trừ gate

- **Nguồn:** `BACKLOG.md` T-015 G6 = `BLOCKED`; `PRD.md` REQ-06 Should/conditional; `ROADMAP.md` nói weather là nhánh tùy chọn và không cản CORE; `G0_G1_REVIEW.md` cho phép NO-GO Weather.
- **Hệ quả:** Một Agent có thể coi G6 thất bại vì còn task `BLOCKED`; Agent khác cho phép PASS mà không có quy tắc nghiệm thu rõ.
- **Khắc phục:** Định nghĩa `CONDITIONAL_NO_GO/NOT_APPLICABLE` và chỉ cho G6 PASS khi CORE task/test PASS, Weather có GO + evidence hoặc NO-GO decision documented. Không ghi “BLOCKED” như task bắt buộc chưa làm, hoặc phân nhóm optional riêng.

### F-06 — MEDIUM — `RESULTS_REGISTER` chưa bao phủ các đầu ra Must của PRD

- **Nguồn:** `PRD.md` RQ-01..RQ-05 là Must; `RESULTS_REGISTER.md` chỉ có RES-001(RQ01), RES-002(RQ02), RES-003(RQ03 carrier-year), RES-004(RQ05), RES-005(RQ06 conditional); **không có RES cho RQ-04 (2020)**, và chưa có kế hoạch result rows cho `DEP_DELAY` KPI-04/05, monthly, airport-year và route-year dù `KPI_SPEC.md` yêu cầu.
- **Phân loại:** Thiếu traceability/coverage của bản mẫu đăng ký, không phải sai lệch số liệu.
- **Khắc phục:** Thêm `RES-006` trở đi làm *planned slots* cho tất cả RQ bắt buộc/aggregation must; liên kết `RQ → REQ → KPI → T → TS → RES`. Giữ `NOT_RUN`, tuyệt đối không tự thêm kết quả.

### F-07 — MEDIUM — Data signature so khớp `mtime` chưa phân biệt provenance và kiểm tra identity

- **Nguồn:** `DATA_CONTRACT.md` yêu cầu đối chiếu path/size/mtime với `source_signature` trong JSON; `DATA_PROVENANCE.md` xác nhận không có raw SHA-256.
- **Hệ quả:** Copy raw file sang máy khác có thể đổi mtime dù nội dung giữ nguyên; cũng có thể khác nội dung nhưng giữ size/mtime. Nếu viết fail-fast theo literal requirement sẽ gây false FAIL hoặc tin nhầm file.
- **Khắc phục:** `size + mtime` chỉ là kiểm tra metadata/thông tin cảnh báo; raw content checksum là bằng chứng identity mạnh hơn khi thu thập được. Định nghĩa cách xử lý khi mtime đổi: không tự sửa source audit; chuyển `IDENTITY_UNVERIFIED` cho đến khi có checksum/verification phù hợp.

### F-08 — MEDIUM — Quy tắc phân xử “evidence cũ trước decision mới” cần bước xét tính áp dụng

- **Nguồn:** `DOCUMENT_REGISTER.md` xếp các source historical audit trên quyết định/PRD; `data_inventory.md` lại có holdout 2024 và ML core; `DECISIONS.md`/`ANALYSIS_PROTOCOL.md` rõ ràng bỏ holdout cho phân tích mô tả.
- **Thực tế:** Tài liệu mới đã *nói đúng* rằng Aeolus lịch sử không chi phối dự án hiện tại, nên **chưa có xung đột scope đang tồn tại**.
- **Rủi ro:** Agent thực hiện thuật toán precedence máy móc sẽ tưởng evidence mô tả “2024 sealed” có quyền phủ quyết scope analysis-first đã được user xác nhận.
- **Khắc phục:** Bổ sung bước `context/applicability test`: lịch sử ML chỉ là evidence về tình trạng pipeline cũ; chính sách mới được quyết định tại `FP-DEC-001/002`. Phân xử dựa trên facts từ audit, không áp dụng policy ML ngoài phạm vi.

## 3. Lỗi tham chiếu cụ thể phải sửa

### F-09 — LOW — Tên file bàn giao không tồn tại

`docs/00-governance/DOCUMENT_REGISTER.md`, mục thứ tự nguồn sự thật, tham chiếu `HANDOFF.md` nhưng file thật là `docs/04-execution/AI_HANDOFF.md`. Đổi thành tên/path chính xác.

### F-10 — LOW — Vị trí CHANGELOG sai trong README

`README.md`, mục cấu trúc, mô tả `CHANGELOG` trong `docs/04-execution/`; file thật nằm ở `docs/03-quality/CHANGELOG.md`. Sửa một vị trí, tránh để Agent tìm nhầm.

### F-11 — LOW — Sai tiền tố ID bài test rollback

`docs/03-quality/ROLLBACK_PLAN.md`, mục diễn tập, viết `TEST-013 logs` nhưng catalog dùng `TS-013` (`TEST_PLAN.md`, fault injection/rollback). Sửa thành `TS-013`.

**Lưu ý ngoại lệ:** `canonical_schedule_datetime_representation_audit.md` trong `docs/05-evidence/inputs/` tham chiếu tới vài file `docs/dataset_audit/` không có trong ZIP. Đây là tham chiếu đến **repository Aeolus lịch sử** từ một bản snapshot nguồn bất biến; **không nên sửa nguồn** và **không coi là lỗi tham chiếu của tài liệu mới**. Nếu cần phụ lục, có thể lập một mapping nguồn tham chiếu ngoài gói.

## 4. Các điểm cần quy chuẩn hóa để giao việc cho AI (không phải mâu thuẫn đã được chứng minh)

- **Q-01:** `source_row_number` trên Spark distributed không mặc nhiên ổn định với cách đọc lại file khác số partitions. Thiết kế ID/offset hoặc surrogate-key, chứng minh determinism trước khi dùng làm ID truy vết.
- **Q-02:** Bảng quality flags và ba nhóm `accepted/quarantined/rejected` phải được thiết kế disjoint (xem F-03). Không loại những record có thời tiết missing khỏi các KPI delay khi quy tắc metric không yêu cầu Weather.
- **Q-03:** `KPI-06` percentile exact/approx và tolerance chưa khóa. Đây là hạng mục T-003, không được đánh PASS trước đó.
- **Q-04:** Min-N và policy ranking chưa khóa; test cần phản ánh suppression/caution ở mẫu ít.
- **Q-05:** G2/G3 có thể tiến hành dựa trên G1 structural **PARTIAL**; phải ghi rõ các blocker nào chặn đúng metric nào, không chặn vô lý toàn bộ analysis nhưng cũng không cho qua điều kiện dữ liệu chưa hợp lệ.
- **Q-06:** Tách `KPI row-volume` (raw/accepted) và `flight event count` (đợi T-002). Không lén suy ra số chuyến của toàn quốc từ records.
- **Q-07:** `BUILD_QA_REPORT.md` ghi PASS cho **file count, parse và hash**, không có nghĩa PASS cho kiểm toán tham chiếu/logic. Nên bổ sung automated docs lint và matrix completeness ở bản sau.

## 5. Những mục phù hợp, không được báo lỗi nhầm

- Dùng 2024 để phân tích mô tả và không dùng 2024 làm ML holdout **không mâu thuẫn** với snapshot Aeolus, vì khác nhiệm vụ và đã có `FP-DEC-001/002`.
- Cấm `DEP_DELAY` làm predictor T-2h trong audit cũ **không mâu thuẫn** với dùng `DEP_DELAY` để phân tích hồi cứu hiệu suất.
- `FL_DATE`/schedule có bằng chứng chi tiết 2016–2023; 2024 cần xác nhận thêm và `2400_SEMANTICS_NOT_PROVEN` đã được tôn trọng trong docs mới.
- Thiếu `CANCELLED`/`DIVERTED` đã được thống nhất NO-GO cho tỷ lệ hủy/chuyển hướng từ 34 cột hiện có.
- Kết quả JSON được nhận diện là *audit-source baseline*, không giả là Spark production output; scope chỉ gồm 9 CSV, không tự dùng `.pt`.
- Các phép tổng row/late, weighted mean, weather missing đối chiếu khớp JSON; không thấy số thống kê mâu thuẫn nội bộ ở các mục đã kiểm.

## 6. Thứ tự sửa và kiểm chứng đề xuất

1. **Patch-A (bắt buộc trước AI coding):** F-01, F-02, F-03, F-04, F-05. Cùng sửa `ROADMAP`, `BACKLOG`, `PROJECT_STATE`, `KPI_SPEC`, `DATA_CONTRACT`, `TEST_PLAN`, và các phần liên quan trong `PRD/DECISIONS` nếu scope bị thay đổi.
2. **Patch-B (truy vết):** F-06, F-07, F-08; bổ sung traceability matrix RQ→REQ→KPI→TASK→TEST→RESULT, clarifications về source signature / evidence applicability.
3. **Patch-C (tham chiếu):** F-09, F-10, F-11; chạy kiểm tra liên kết/tên/path của tất cả MD mới, bỏ qua tham chiếu tới repo Aeolus bên trong nguồn immutable.
4. **QA release:** Verify mọi tài liệu mới đã cập nhật đồng bộ, manifest mới, CHANGELOG, review gate criteria, giữ snapshot gốc và ghi version `docs-v1.1`. Không thay đổi bất kỳ file trong `docs/05-evidence/inputs/`.

**Tiêu chí `DOCS_CONSISTENCY_PASS` đề xuất:** 0 lỗi HIGH/MEDIUM chưa xử lý ảnh hưởng code; 0 path tham chiếu mới sai; một định nghĩa duy nhất cho mọi KPI/coverage; đồng bộ gate–task–test–result; status/provenance chính xác; kiểm tra ZIP và manifest PASS; các blocker thực tế vẫn hiển thị, không xóa bằng cách đổi nhãn thành PASS.

## 7. Kết luận cuối

Bộ hồ sơ v1.0 **đạt tính toàn vẹn tệp và nhất quán số liệu cơ bản**, nhưng **chưa đạt tính đồng bộ quy trình cho AI Agent**. Nên sửa có kiểm chứng lên v1.1 trước khi khởi động T-006 đến G5. Các audit read-only T-001, T-002 và việc làm rõ đơn vị/coverage có thể chuẩn bị dựa trên tài liệu hiện tại, với trạng thái PENDING/PROPOSED rõ ràng.
