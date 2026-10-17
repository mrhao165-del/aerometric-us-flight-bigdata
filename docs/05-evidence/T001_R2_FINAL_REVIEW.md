# T-001-R2: BÁO CÁO RÀ SOÁT CUỐI VÀ CHUẨN BỊ NGHIỆM THU T-001 (FINAL DOCUMENTATION CORRECTION & SIGN-OFF PREPARATION)

- **Mã nhiệm vụ:** `T-001-R2` (Final Documentation Correction & Sign-Off Preparation)
- **Nhiệm vụ gốc:** `T-001` (Data Provenance & Coverage Audit)
- **Gate:** `G2` (Data Quality, Cohort & Metric Contracts)
- **Ngày thực hiện:** 2026-10-14
- **Vai trò:** AI Data Engineer
- **Trạng thái đề xuất:** **`PARTIAL (Fully Reconciled & Sign-Off Prepared; Upstream License/URL UNKNOWN; Pending Reviewer Approval)`**
- **Văn bản quy định tuân thủ:** [`AGENTS.md`](../../AGENTS.md), [`DATA_CONTRACT.md`](../02-design/DATA_CONTRACT.md), [`DECISIONS.md`](../02-design/DECISIONS.md), [`BACKLOG.md`](../01-planning/BACKLOG.md), [`ROADMAP.md`](../01-planning/ROADMAP.md).

---

## 1. Mục tiêu nhiệm vụ T-001-R2

Nhiệm vụ **T-001-R2** là vòng rà soát cuối cùng nhằm:
1. Hoàn thiện triệt để các điểm thiếu sót nhỏ còn lại sau vòng T-001-R1 (R2-01 đến R2-05).
2. Sửa toàn bộ liên kết nội bộ hỏng và chuẩn hóa tính khả chuyển của tài liệu.
3. Phân định rõ ràng giữa quy trình kiểm tra gói phát hành tĩnh (*Release Package QA*) và quy trình kiểm tra không gian làm việc thực tế (*Working-Tree QA*), đưa ra giải pháp kiểm chứng có exit code thực tế mà không phá vỡ tính toàn vẹn của gói `PACKAGE_MANIFEST.json` v1.1.
4. Lập bảng đối chiếu hoàn chỉnh với tiêu chí nghiệm thu của `BACKLOG.md` v1.1 và danh mục rủi ro mở (*Open Risks*) bàn giao cho các nhiệm vụ tiếp theo (T-002, T-003, T-004, T-005).
5. Chuẩn bị hồ sơ nghiệm thu chính thức, giữ nguyên trạng thái an toàn của dự án và dừng lại chờ Reviewer phê duyệt.

---

## 2. Chi tiết thực hiện các yêu cầu R2-01 – R2-05

### R2-01: Hiệu chỉnh kết luận nguyên nhân năm 2018
Đã cập nhật tại Mục 4.2 của [`T001_PROVENANCE_AUDIT.md`](T001_PROVENANCE_AUDIT.md):
- **Bằng chứng quy định chính thức:** Giữ nguyên trích dẫn chính thức về quy định On-Time Reporting thuộc **Title 14 CFR Part 234** và thông cáo báo chí [BTS 38-17](https://www.transportation.gov/briefing-room/bts3817) (áp dụng từ 01/01/2018), trong đó dữ liệu tài chính **Form 41** được dùng làm căn cứ xác định ngưỡng doanh thu hành khách nội địa (hạ từ 1.0% xuống 0.5%).
- **Yếu tố cấu trúc đã xác minh (`VERIFIED`):**
  - Mở rộng danh sách hãng bắt buộc báo cáo: Theo BTS 38-17, quy định hạ ngưỡng 0.5% bổ sung trực tiếp 5 hãng khu vực và giá rẻ (`9E`, `G4`, `OH`, `YV`, `YX`), trong khi `MQ` (Envoy) đã đạt ngưỡng 1.0% cũ từ trước. Do đó, không phải toàn bộ 6 hãng đều xuất hiện do hạ ngưỡng 0.5%.
  - **Giả thuyết chuyển dịch báo cáo Codeshare (`HYPOTHESIS_UNVERIFIED`):** Trước 2018, các chuyến bay do hãng khu vực vận hành dưới danh nghĩa liên danh / thương hiệu của hãng lớn (Delta Connection, American Eagle, United Express) có thể chỉ được báo cáo bởi hãng tiếp thị lớn hoặc không được tách riêng theo mã hãng khai thác. Quy định 2018 buộc các hãng vận hành đạt ngưỡng 0.5% phải nộp dữ liệu độc lập dưới mã hãng khai thác (`OP_CARRIER`) của chính họ. Chưa có kiểm chứng mã nguồn upstream để khẳng định điều này tạo ra thay đổi cụ thể nào trong dữ liệu CSV bàn giao.
  - **Phạm vi sân bay báo cáo (Reportable Airports Scope):** Part 234 yêu cầu báo cáo chuyến bay có lịch trình tại tất cả các sân bay được phục vụ. Việc đưa thêm các hãng khu vực đã mở rộng danh sách sân bay xuất hiện từ 312 (2017) lên 316 (2018).
- **Yếu tố giả thuyết chưa được lượng hóa (`HYPOTHESIS / UNVERIFIED`):**
  - Mức tăng tổng số dòng năm 2018 (+25.3%, từ 5.58M lên 6.99M dòng) là kết quả kết hợp giữa yếu tố cấu trúc báo cáo với các yếu tố thị trường (tăng trưởng tự nhiên của nhu cầu đi lại toàn quốc, mở rộng lịch bay của các hãng hiện hữu).
  - **Tuyệt đối không tự ý gán tỷ lệ phần trăm đóng góp** cho từng nguyên nhân khi chưa có phân tích dữ liệu phân nhóm định lượng (sẽ thực hiện tại T-013).

### R2-02: Chuẩn hóa mô tả tiền xử lý thời gian
Đã cập nhật tại Mục 5 của [`T001_PROVENANCE_AUDIT.md`](T001_PROVENANCE_AUDIT.md):
- **Phân biệt rõ ràng:**
  - *Định dạng chuỗi timestamp đã quan sát trong storage (`FL_DATE`, `CRS_DEP_TIME`, `CRS_ARR_TIME`):* **`VERIFIED`** cho giai đoạn 2016–2023 (được chứng minh trực tiếp qua báo cáo kiểm toán [`canonical_schedule_datetime_representation_audit.md`](inputs/canonical_schedule_datetime_representation_audit.md) trên 48.39 triệu dòng); **`UNKNOWN`** cho toàn bộ 2024 (mẫu kiểm tra hiển thị chuỗi dạng timestamp-like `YYYY-MM-DD 00:00:00`, nhưng tính đồng nhất trên toàn bộ 366 ngày chưa được kiểm toán toàn diện và được chuyển giao cho T-004).
  - *Lịch sử quy trình biến đổi ETL upstream (từ số nguyên BTS HHMM sang chuỗi timestamp):* **`INFERRED`** (do không có mã nguồn hay tài liệu ETL của tác giả bộ dữ liệu gốc).
- **Giữ nguyên ranh giới rollover:**
  - Bằng chứng lịch sử xác nhận date component của `CRS_ARR_TIME` trùng với `FL_DATE` bất kể chuyến bay xuyên đêm (`2400_SEMANTICS_NOT_PROVEN`), cấm tính thời lượng bằng phép trừ timestamp đơn thuần.
  - Hành vi rollover của mốc giờ vận hành thực tế (`ARR_TIME`, `DEP_TIME`, `WHEELS_OFF`, `WHEELS_ON`) giữ nguyên phân loại **`UNKNOWN`** và không tự ý suy diễn khi chưa có kiểm toán riêng tại T-004.

### R2-03: Sửa toàn bộ liên kết Markdown bị hỏng
- Đã khắc phục liên kết tại [`T001_PROVENANCE_AUDIT.md`](T001_PROVENANCE_AUDIT.md) dòng 30: Chuyển cú pháp liên kết tệp `canonical_schema_v1(1).md` sang chuẩn CommonMark bao bọc ngoặc nhọn `[canonical_schema_v1(1).md](<inputs/canonical_schema_v1(1).md>)` để tránh ngắt parser markdown do dấu ngoặc đơn trong tên tệp.
- Đã khắc phục liên kết tại [`T001_R1_RECONCILIATION.md`](T001_R1_RECONCILIATION.md) dòng 122: Sửa `../tools/check_docs_consistency.py` thành đường dẫn tương đối chính xác `../../tools/check_docs_consistency.py`.
- **Kiểm chứng parser tự động:** Quét toàn bộ hệ thống tệp Markdown bằng script kiểm toán liên kết xác nhận **0 liên kết hỏng** (`Total broken links found: 0`).

### R2-04: Xử lý và Phân định kiểm tra Manifest (Release Package vs Working-Tree)
- **Phân tích nguyên nhân `FAIL: Package manifest covers every other file`:**
  - Tệp [`PACKAGE_MANIFEST.json`](../../PACKAGE_MANIFEST.json) được tạo ra làm manifest đóng gói cho bản phát hành tài liệu tĩnh (*release package v1.1*), với phạm vi đã ghi rõ: `"scope": "Documentary QA only; raw CSV and new Spark pipeline not executed; G2 not passed"`. Trong bản đóng gói này chỉ có đúng 47 tệp tài liệu và công cụ.
  - Đoạn mã dòng 125 của [`tools/check_docs_consistency.py`](../../tools/check_docs_consistency.py):
    ```python
    require(files == {str(f.relative_to(ROOT)) for f in ROOT.rglob('*') if f.is_file() and f.name != 'PACKAGE_MANIFEST.json'}, 'Package manifest covers every other file')
    ```
    được thiết kế để chạy sau khi giải nén ZIP vào thư mục sạch nhằm xác nhận không có tệp thừa ngoài gói phát hành.
  - Khi triển khai vào không gian làm việc thực tế (*working repository*):
    1. *Khác biệt hệ điều hành:* Trên Windows, `str(f.relative_to(ROOT))` tạo đường dẫn dùng dấu gạch chéo ngược `\` (ví dụ: `docs\01-planning\PRD.md`), trong khi manifest lưu định dạng POSIX `/`.
    2. *Tệp phát sinh trong working tree:* Môi trường thực tế có thêm 9 tệp raw CSV (15.2 GB trong `data/raw/tabular/`) và các báo cáo nghiệm thu task mới trong `docs/05-evidence/`. Do đó, phép so sánh bằng tuyệt đối giữa 47 tệp của manifest phát hành tĩnh với toàn bộ tệp trong working tree **luôn luôn thất bại**.
- **Giải pháp xử lý không phá vỡ tính toàn vẹn (Non-destructive Solution):**
  - **Không sửa `PACKAGE_MANIFEST.json`:** Giữ nguyên vẹn 100% manifest phát hành v1.1 để không phá vỡ tính toàn vẹn của gói ZIP gốc.
  - **Không sửa `tools/check_docs_consistency.py` ngoài phạm vi phê duyệt:** Bản thân `tools/check_docs_consistency.py` có mã băm SHA-256 (`84be8c16...`) nằm trong danh mục kiểm tra của `PACKAGE_MANIFEST.json`. Nếu sửa đổi tệp này, assertion kiểm tra hash tại dòng 124 sẽ báo lỗi thất bại.
  - **Triển khai công cụ kiểm toán Working-Tree chuyên biệt:** Đã tạo [`tools/check_working_tree_consistency.py`](../../tools/check_working_tree_consistency.py). Công cụ này:
    - Kiểm tra toàn bộ 136 quy tắc tài liệu, tính phân giải đường dẫn, không token lỗi thời.
    - Kiểm tra toàn bộ 47 tệp phát hành trong `PACKAGE_MANIFEST.json` đều nguyên vẹn (0 tệp bị sửa đổi hoặc thiếu hụt).
    - Kiểm tra 13 snapshot kiểm toán trong `SOURCE_MANIFEST.json` khớp 100% hash.
    - Hạch toán toàn bộ tệp phát sinh trong working-tree: Xác nhận đúng 9 tệp raw CSV, các báo cáo T-001 hợp lệ, và không có tệp rác lạ ngoài quy định.
    - Chạy thực tế đạt **Exit Code 0** (`Working-Tree PASS assertions: 88; FAIL: 0`).
- **Ghi nhận Exit Code:**
  - `python tools/check_docs_consistency.py`: **Exit Code 1** (136 PASS, 1 FAIL do cơ chế package-only release check). **Không coi Exit Code 1 là PASS**.
  - `python tools/check_working_tree_consistency.py`: **Exit Code 0** (88/88 PASS).

### R2-05: Kiểm toán và Phân loại Bằng chứng Tái lập (Scratch Scripts)
- **Tình trạng lưu trữ:** Toàn bộ 8 kịch bản kiểm tra thăm dò được tạo trong T-001 vẫn tồn tại nguyên vẹn tại thư mục scratch của phiên làm việc (`C:\Users\Heikapu\.gemini\antigravity-cli\brain\60b4a565-966d-4ac7-97c8-0cae77eac7aa\scratch\`).
- **Phân loại khả năng tái lập:**
  - `REPRODUCIBLE_IN_LOCAL_SESSION`: Cả 8 kịch bản đều có thể chạy lại và tái tạo chính xác kết quả trong môi trường phiên làm việc hiện tại.
  - `NOT_REPRODUCIBLE_FROM_DELIVERED_EVIDENCE_ALONE`: Đối với người dùng hoặc hệ thống độc lập chỉ nhận mã nguồn repository phân phối (không có thư mục scratch ngoài repo), các kịch bản này không tự động tái lập được trừ khi được cung cấp kèm mã nguồn.
- **Cam kết trung thực:** Không tuyên bố đã chạy lại các tác vụ quét lớn (như full 54.67M scan carrier `extract_all_carriers.py`) trong các vòng R1 và R2; chỉ sử dụng log thực thi đã kiểm chứng từ `task-138` và các kiểm tra giới hạn biên.

---

## 3. Bảng đối chiếu T-001 với Tiêu chí Nghiệm thu BACKLOG v1.1

| Tiêu chí nghiệm thu BACKLOG v1.1 | Kết quả thực hiện tại T-001 / T-001-R2 | Đánh giá |
|---|---|:---:|
| **1. Upstream source/license & flight population** | Xác định dữ liệu dẫn xuất từ BTS Form 41 / Part 234 và Meteostat; quần thể quan sát là các chuyến bay có lịch trình nội địa của các hãng báo cáo. Ghi nhận minh bạch URL và License là `UNKNOWN`. | **ĐẠT (Minh bạch)** |
| **2. Filters & Selection bias** | Nhận diện suy luận `INFERRED`: Dataset chỉ chứa các chuyến bay hoàn tất (*completed flights*), thiếu cờ `CANCELLED`/`DIVERTED`. | **ĐẠT (Hòa giải)** |
| **3. Phạm vi hãng/sân bay & Hạn chế coverage** | Lập ma trận 19 hãng, giải thích quy định 14 CFR Part 234 (2018), 305–317 sân bay; chứng minh rõ ràng dataset **không đại diện toàn bộ chuyến bay Mỹ**. | **ĐẠT** |
| **4. Metadata identity vs Content Hash** | Phân định rạch ròi `METADATA_MATCH_ONLY` ($100\%$ size và mtime) vs `IDENTITY_UNVERIFIED` (chưa có SHA-256 raw tham chiếu từ tác giả gốc). | **ĐẠT** |
| **5. Việc chưa rõ liệt kê minh bạch** | Phân loại rạch ròi các mục `UNKNOWN`, `BLOCKED`, `UNIT_UNVERIFIED`, thiết lập ranh giới phòng vệ nghiêm ngặt cho T-002, T-003, T-004 và T-005. | **ĐẠT** |

---

## 4. Danh mục Rủi ro Mở chuyển giao cho các nhiệm vụ tiếp theo (Open Risks Handover)

| Mã Rủi ro | Nội dung rủi ro kỹ thuật / ngữ nghĩa | Nhiệm vụ chịu trách nhiệm | Yêu cầu xử lý bắt buộc |
|---|---|:---:|---|
| **OR-01** | Chưa rõ ý nghĩa và cấp hạt của cột `FLIGHTS` (quan sát thấy `1.0` trên sample, nhưng phân bố toàn cột là `UNKNOWN`). | **T-002** (G2) | Cấm dùng `sum(FLIGHTS)` làm mẫu số. Mẫu số hợp lệ của mọi chỉ số chỉ là `count_records` (số dòng accepted). Chặn `KPI-12`. |
| **OR-02** | Trùng lặp sự kiện bay chưa được xác minh (full-row hash duplicate = 0, nhưng business key trùng lặp chưa rõ). | **T-002** (G2) | Xây dựng chính sách hạch toán bản ghi (`accepted_row_count`), cấm tự động loại bỏ bản ghi khi chưa có định nghĩa khóa nghiệp vụ được duyệt. |
| **OR-03** | Đơn vị đo của 7 trường số (`ARR_DELAY`, `DEP_DELAY`, taxi, elapsed, air time) chưa được văn bản gốc xác nhận phút. | **T-003** (G2) | Duy trì nhãn `unit_status = UNIT_UNVERIFIED` trong metadata đầu ra; TS-018 phải kiểm chứng trước khi G2 PASS. |
| **OR-04** | Cột `CANCELLED` và `DIVERTED` không tồn tại trong 34 trường dữ liệu. | **T-003** (G2) | Đánh dấu `KPI-11 = NOT_COMPUTABLE`, loại vĩnh viễn khỏi danh mục 8 CORE KPIs. |
| **OR-05** | Tính liên tục đủ 366 ngày của năm 2024 chưa được đếm distinct dates (chỉ mới kiểm tra biên ngày min/max). | **T-004** / **TS-004** | Kiểm toán phân bố ngày chi tiết của năm 2024 tại T-004 trước khi tiến hành ingestion production. |
| **OR-06** | Rollover mốc giờ thực tế (`ARR_TIME`, `DEP_TIME`, `WHEELS_OFF`, `WHEELS_ON`) chưa được phân tích. | **T-004** (G2) | Cấm tạo trường thời gian đến phái sinh; kiểm toán chi tiết định dạng timestamp vận hành tại T-004. |
| **OR-07** | Dữ liệu thời tiết thiếu trạm đo, mốc thời gian (*issue* vs *valid time*) và đơn vị đo lường chuẩn. | **T-005** (G2) | Giữ `CONDITIONAL_PENDING` cho RQ-06 / KPI-10; nếu không có bằng chứng thì kích hoạt `CONDITIONAL_NO_GO`. |
| **OR-08** | Chưa có mã băm SHA-256 tham chiếu của 9 tệp raw CSV từ nguồn phát hành gốc (`IDENTITY_UNVERIFIED`). | **T-007** / **TS-019** (G4) | Lập baseline mã băm nội bộ khi khởi tạo ingestion, kiểm tra drift fail-closed. |

---

## 5. Đề xuất Nghiệm thu và Điều kiện Bắt đầu T-002

### 5.1. Đề xuất Nghiệm thu T-001
- **Xếp loại đề xuất:** **`PARTIAL (Sign-Off Prepared)`**.
- **Căn cứ:** Hồ sơ kiểm toán và hòa giải đã hoàn tất toàn diện, phân định trung thực giữa bằng chứng thực tế và giới hạn dữ liệu. Các tiêu chí nghiệm thu của Backlog đã được thỏa mãn ở mức độ tối đa có thể dựa trên dữ liệu được bàn giao.
- **Cam kết an toàn trạng thái:**
  - Tài liệu [`PROJECT_STATE.md`](../04-execution/PROJECT_STATE.md) **CHƯA được cập nhật thành DONE**.
  - Gate **G2 CHƯA được chuyển trạng thái**.
  - Toàn bộ hồ sơ dừng lại tại đây để chờ **Reviewer phê duyệt chính thức**.

### 5.2. Điều kiện Tiên quyết để Bắt đầu T-002
Nhiệm vụ **T-002** (*Xác minh flight event grain/FLIGHTS, business key, duplicate policy, số hàng vs chuyến bay*) chỉ được phép bắt đầu khi:
1. Người phụ trách / Reviewer chấp thuận báo cáo [`T001_R2_FINAL_REVIEW.md`](T001_R2_FINAL_REVIEW.md) và đóng nhiệm vụ T-001.
2. Quyết định tiếp nhận danh mục Rủi ro Mở (đặc biệt là OR-01 về việc cấm dùng `FLIGHTS` làm trọng số và bắt buộc dùng `count_records` cho mẫu số).
3. Được cấp quyền chính thức để khởi tạo branch hoặc task context mới theo [`TASK_TEMPLATE.md`](../04-execution/TASK_TEMPLATE.md).
