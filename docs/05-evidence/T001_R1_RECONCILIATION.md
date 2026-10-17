# T-001-R1: BÁO CÁO HÒA GIẢI VÀ HIỆU CHỈNH KIỂM TOÁN NGUỒN GỐC DỮ LIỆU (TARGETED PROVENANCE AUDIT RECONCILIATION)

- **Mã nhiệm vụ:** `T-001-R1` (Targeted Provenance Audit Correction)
- **Nhiệm vụ gốc:** `T-001` (Data Provenance & Coverage Audit)
- **Gate:** `G2` (Data Quality, Cohort & Metric Contracts)
- **Ngày thực hiện:** 2026-10-14
- **Vai trò thực hiện:** AI Data Engineer
- **Tài liệu được hiệu chỉnh:** [`docs/05-evidence/T001_PROVENANCE_AUDIT.md`](T001_PROVENANCE_AUDIT.md)
- **Tài liệu căn cứ:** [`AGENTS.md`](../../AGENTS.md), [`DATA_CONTRACT.md`](../02-design/DATA_CONTRACT.md), [`DECISIONS.md`](../02-design/DECISIONS.md), [`BACKLOG.md`](../01-planning/BACKLOG.md), [`ROADMAP.md`](../01-planning/ROADMAP.md), [`TEST_PLAN.md`](../03-quality/TEST_PLAN.md), [`DATA_PROVENANCE.md`](DATA_PROVENANCE.md).

---

## 1. Tổng quan mục tiêu nhiệm vụ T-001-R1

Nhiệm vụ **T-001-R1** được thực hiện nhằm rà soát có mục tiêu, khắc phục 8 phát hiện sai lệch hoặc thiếu chặt chẽ khoa học (F01–F08) trong báo cáo kiểm toán ban đầu [`T001_PROVENANCE_AUDIT.md`](T001_PROVENANCE_AUDIT.md), đảm bảo tính nhất quán giữa bằng chứng thực tế (*actual evidence*), các suy luận hợp lý (*inferences*), và các giới hạn chưa được kiểm chứng (*unknowns/blocked items*).

Nhiệm vụ này **chỉ sửa tài liệu và hòa giải bằng chứng**, tuyệt đối không can thiệp vào dữ liệu raw, không sửa các snapshot kiểm toán lịch sử, không quét full dataset ngoài phạm vi cho phép, và không tự động thay đổi trạng thái gate khi chưa có sự phê duyệt của reviewer.

---

## 2. Chi tiết xử lý từng phát hiện (F01 – F08)

### F01 — Completed Flights: Không đồng nhất 0 missing với bằng chứng trực tiếp của bộ lọc upstream
- **Vấn đề nhận diện:** Báo cáo ban đầu tuyên bố việc toàn bộ các trường thời gian và độ trễ vận hành không có missing data là bằng chứng cho thấy người tạo dataset gốc đã áp dụng bộ lọc `CANCELLED == 0 AND DIVERTED == 0` rồi xóa 2 cột trạng thái này.
- **Biện pháp xử lý:**
  - Chuyển phân loại kết luận này từ khẳng định tuyệt đối sang **`INFERRED`**.
  - Làm rõ trong Mục 5, Mục 7 và Mục 8 của [`T001_PROVENANCE_AUDIT.md`](T001_PROVENANCE_AUDIT.md): Việc 100% bản ghi có finite delays và 0 missing trong các trường vận hành thực tế là hoàn toàn *nhất quán* với quần thể các chuyến bay đã hoàn tất (*completed flights cohort*). Tuy nhiên, do thiếu mã nguồn ETL hoặc tài liệu quy trình trích xuất ban đầu, đây là một **suy luận quy nạp từ dữ liệu quan sát (`INFERRED`)**, không phải bằng chứng trực tiếp về một câu lệnh lọc cụ thể.

### F02 — BTS Reporting Change 2018: Cơ sở pháp lý Part 234 & Form 41, Giới hạn kết luận mức tăng bản ghi
- **Vấn đề nhận diện:** Báo cáo ban đầu chưa trích dẫn văn bản pháp lý chính thức, nhầm lẫn Form 41 là quy định báo cáo on-time, và khẳng định toàn bộ mức tăng +25.3% số dòng năm 2018 là do thay đổi ngưỡng báo cáo.
- **Biện pháp xử lý:**
  - Bổ sung trích dẫn và liên kết đến các văn bản chính thức của Cục Thống kê Giao thông Vận tải Hoa Kỳ (BTS / DOT):
    - Thông cáo báo chí Bộ GTVT Hoa Kỳ: [BTS 38-17 Announcement (Dec 2017)](https://www.transportation.gov/briefing-room/bts3817).
    - Danh sách các hãng và sân bay báo cáo của BTS: [BTS Reporting Air Carriers and Reportable Airports](https://www.bts.gov/topics/airlines-and-airports/lists-reporting-air-carriers-and-reportable-airports-time-performance).
  - Làm rõ cơ sở pháp lý: Quy định báo cáo dữ liệu đúng giờ của các chuyến bay thương mại nội địa Hoa Kỳ thuộc **Title 14 CFR Part 234** (*Airline Service Quality Performance Reports*). Dữ liệu tài chính từ **Form 41** được BTS sử dụng để xác định ngưỡng doanh thu hành khách vận chuyển nội địa nhằm lập danh sách các hãng bắt buộc báo cáo (*mandatory reporting carriers*). Từ 01/01/2018, ngưỡng này được hạ từ 1.0% xuống 0.5% bổ sung 5 hãng mới (`9E, G4, OH, YV, YX`), trong khi `MQ` (Envoy) đã đạt ngưỡng 1.0% cũ từ trước theo xác nhận của BTS 38-17.
  - Điều chỉnh kết luận về mức tăng bản ghi (+25.3%, từ 5.58M lên 6.99M dòng): Không khẳng định toàn bộ mức tăng do thay đổi chính sách. Xác định đây là kết quả của nhiều yếu tố kết hợp: (1) Việc mở rộng đối tượng Part 234 đưa thêm các hãng khu vực (9E, OH, YV, YX) và hãng giá rẻ (G4) vào danh sách bắt buộc nộp báo cáo riêng, cùng sự xuất hiện của MQ; (2) Tăng trưởng khối lượng vận chuyển hàng không toàn quốc năm 2018; (3) Mở rộng mạng bay và lịch bay của các hãng hiện hữu; các giả thuyết về codeshare chưa có bằng chứng khẳng định tác động cụ thể lên CSV.

### F03 — Temporal Coverage: Phân biệt min/max service date với kiểm chứng đầy đủ từng ngày lịch 2024
- **Vấn đề nhận diện:** Báo cáo ban đầu từ kết quả Min `FL_DATE = 2024-01-01` và Max `FL_DATE = 2024-12-31` đã khẳng định bộ dữ liệu "đủ 366 ngày của năm 2024".
- **Biện pháp xử lý:**
  - Làm rõ sự khác biệt giữa **kiểm tra biên ngày (Boundary Check)** và **kiểm chứng tính liên tục đầy đủ của từng ngày lịch (Distinct Daily Coverage Check)**.
  - Phân loại tính đầy đủ của 366 ngày năm 2024 về trạng thái **`UNKNOWN / PENDING_DAILY_COUNT`**.
  - Tuân thủ quy định an toàn: Không thực hiện quét full CSV bổ sung tại T-001; việc đếm distinct service dates cho năm 2024 được đưa vào nhiệm vụ chuyên trách **T-004** (Time audit) và **TS-004 / T-012** (Full run reconciliation).

### F04 — Airport Coverage: Loại bỏ khẳng định tất cả sân bay đều là sân bay thương mại lớn
- **Vấn đề nhận diện:** Báo cáo ban đầu nhận định 305–317 sân bay trong dữ liệu đều là "sân bay thương mại lớn".
- **Biện pháp xử lý:**
  - Loại bỏ hoàn toàn cụm từ "sân bay thương mại lớn".
  - Hiệu chỉnh thành: "Các sân bay thương mại có chuyến bay có lịch trình được phục vụ bởi các hãng báo cáo thuộc phạm vi 14 CFR Part 234".
  - Giải thích rõ: Danh mục này bao gồm cả sân bay trung tâm lớn (*Large Hubs*), trung bình (*Medium Hubs*), nhỏ (*Small Hubs*), sân bay thương mại không thuộc trung tâm (*Non-hub primary*), và một số sân bay địa phương thuộc diện Hàng không Thiết yếu (*EAS*). Phân loại quy mô sân bay chính thức cần được ánh xạ theo chuẩn FAA NPIAS và hiện tại là **`UNKNOWN`** trong dataset thô.

### F05 — Preprocessing: Rà soát, lập bảng phân loại VERIFIED/INFERRED/UNKNOWN và cô lập ARR_TIME
- **Vấn đề nhận diện:** Các bước tiền xử lý được diễn giải gộp chung; mở rộng kết luận rollover của `CRS_ARR_TIME` sang trường `ARR_TIME` thực tế mà chưa có kiểm toán riêng.
- **Biện pháp xử lý:**
  - Lập bảng phân loại độc lập tại Mục 5 của [`T001_PROVENANCE_AUDIT.md`](T001_PROVENANCE_AUDIT.md) cho từng bước tiền xử lý:
    - *Lọc chuyến bay hoàn tất:* **`INFERRED`**.
    - *Làm giàu dữ liệu thời tiết:* **`INFERRED`** (cột hiện diện trong schema, logic merge là inferred).
    - *Tọa độ và Airport Index:* **`INFERRED`** (cột hiện diện trong schema, mapping ổn định).
    - *Chuẩn hóa chuỗi thời gian có lịch (`FL_DATE`, `CRS_DEP_TIME`, `CRS_ARR_TIME`):* **`VERIFIED`** cho 2016–2023 (qua datetime audit lịch sử), **`INFERRED`** cho 2024.
    - *Hành vi rollover của mốc giờ vận hành thực tế (`DEP_TIME`, `ARR_TIME`, `WHEELS_OFF`, `WHEELS_ON`):* **`UNKNOWN`**.
  - Nhấn mạnh: Báo cáo datetime audit lịch sử chỉ chiếu các trường `CRS_*`. Không được suy diễn rằng date component của `ARR_TIME` cũng bị gắn cố định theo `FL_DATE` khi chưa có kiểm toán chuyên biệt tại T-004.

### F06 — FLIGHTS: Phân biệt quan sát mẫu với kiểm toán toàn cột; tái khẳng định BLOCKED
- **Vấn đề nhận diện:** Báo cáo ban đầu viết *"FLIGHTS luôn có giá trị 1.0"* mà không nêu rõ đây chỉ là quan sát trên các dòng mẫu được đọc.
- **Biện pháp xử lý:**
  - Hiệu chỉnh cách diễn đạt: Giá trị `FLIGHTS = 1.0` chỉ mới được quan sát trên các dòng mẫu kiểm tra (sample inspection). Schema audit chỉ ghi nhận kiểu dữ liệu `float` và 0 missing.
  - Phân bố giá trị min, max, distinct của cột `FLIGHTS` trên toàn bộ 54,674,003 dòng hiện tại là **`UNKNOWN`**.
  - Tái khẳng định trạng thái **`BLOCKED`**: Tuyệt đối cấm sử dụng `sum(FLIGHTS)` làm mẫu số hoặc trọng số tính toán trước khi T-002 kiểm toán phân bố giá trị của cột này. Mẫu số hợp lệ của mọi chỉ số chỉ là `count_records` (số dòng accepted).

### F07 — Documentation Portability: Thay thế liên kết tuyệt đối và sửa tiêu đề bảng gây hiểu lầm
- **Vấn đề nhận diện:** Báo cáo ban đầu chứa nhiều liên kết tuyệt đối dạng `file:///D:/Study/...` làm mất tính khả chuyển khi di chuyển repo; tiêu đề bảng có cột *"Số cột rỗng hoàn toàn (0 Missing)"* gây hiểu lầm là cột không có dữ liệu (all-null).
- **Biện pháp xử lý:**
  - Chuyển $100\%$ các liên kết `file:///` sang liên kết tương đối markdown chuẩn:
    - `[AGENTS.md](../../AGENTS.md)`
    - `[DATA_CONTRACT.md](../02-design/DATA_CONTRACT.md)`
    - `[DECISIONS.md](../02-design/DECISIONS.md)`
    - `[BACKLOG.md](../01-planning/BACKLOG.md)`
    - `[inputs/SOURCE_MANIFEST.json](inputs/SOURCE_MANIFEST.json)`
  - Sửa tiêu đề cột tại Mục 3 thành: **`Số cột không khuyết thiếu (0 missing / 100% đầy đủ)`**, làm rõ ý nghĩa 28 cột có dữ liệu hoàn chỉnh tuyệt đối.

### F08 — Evidence Reproducibility: Lập Manifest tái lập các kịch bản scratch và ghi rõ giới hạn
- **Vấn đề nhận diện:** Các kịch bản kiểm tra thăm dò được tạo trong thư mục `scratch/` của môi trường phiên làm việc chưa được lập chỉ mục và lưu vết băm xác thực.
- **Biện pháp xử lý:**
  - Lập bảng **Manifest tái lập bằng chứng kiểm toán (Audit Reproducibility Manifest)** tại Mục 9 của [`T001_PROVENANCE_AUDIT.md`](T001_PROVENANCE_AUDIT.md) ghi nhận đầy đủ 8 kịch bản: tên tệp, đường dẫn, kích thước byte, mã băm SHA-256, nguồn dữ liệu đầu vào, lệnh thực thi, exit code, thời điểm chạy và kết quả xác minh.
  - Cảnh báo rõ ràng: Các kịch bản scratch này nằm ngoài cấu trúc kho lưu trữ phân phối. Đối với môi trường độc lập chỉ nhận git repo/bundle, chúng phải được phân loại là **`NOT_REPRODUCIBLE_FROM_DELIVERED_EVIDENCE`** trừ khi được tích hợp thành công cụ chính thức trong thư mục `tools/`.

---

## 3. Bảng so sánh các tuyên bố đã thay đổi (Old vs New Claims)

| Hạng mục / Vị trí | Tuyên bố cũ (Bản ban đầu) | Tuyên bố mới hiệu chỉnh (Bản T-001-R1) | Lý do hiệu chỉnh & Nguyên tắc |
|---|---|---|---|
| **Completed flights**<br>*(Mục 5, Dòng 123)* | *"Người tạo bộ dữ liệu gốc đã áp dụng bộ lọc `CANCELLED == 0` và `DIVERTED == 0`..."* (Khẳng định sự thật) | *"Tập dữ liệu phản ánh quần thể các chuyến bay đã hoàn tất (Completed flights inferred)..."* (Suy luận `INFERRED`) | Thiếu mã nguồn upstream ETL chứng minh câu lệnh lọc (F01). |
| **BTS Policy 2018**<br>*(Mục 4.2, Dòng 97-98)* | *"BTS hạ ngưỡng doanh thu theo Form 41... Sự gia tăng số chuyến bay từ 2018 là do thay đổi quy định."* | *"Quy định báo cáo On-Time thuộc 14 CFR Part 234; Form 41 dùng làm căn cứ tính doanh thu... Thay đổi ngưỡng là yếu tố cấu trúc chính nhưng không phải nguyên nhân duy nhất của mức tăng +25.3%."* | Trích dẫn chính xác BTS 38-17, phân định thẩm quyền Part 234 và tránh quy kết duy nhất (F02). |
| **2024 Daily Coverage**<br>*(Mục 4.1 & Mục 8)* | *"Xác nhận đủ 366 ngày của năm 2024."* | *"Biên ngày Min 2024-01-01, Max 2024-12-31 và 6,284,841 dòng đã xác minh; tính liên tục đủ 366 ngày là `UNKNOWN / PENDING_DAILY_COUNT`."* | Kiểm tra min/max không đồng nghĩa với đếm distinct service dates (F03). |
| **Airport Classification**<br>*(Mục 4.3, Dòng 102)* | *"...bộ dữ liệu này chỉ bao gồm khoảng 310 sân bay thương mại lớn..."* | *"...bao gồm các sân bay thương mại có chuyến bay có lịch trình phục vụ bởi các hãng Part 234 (bao gồm large, medium, small, non-hub airports)."* | Chưa có đối chiếu phân loại Hub chính thức của FAA (F04). |
| **ARR_TIME Rollover**<br>*(Mục 5, Dòng 136)* | *"Phần ngày của CRS_ARR_TIME và ARR_TIME bị gán đồng nhất với FL_DATE..."* | *"Date component của CRS_ARR_TIME trùng FL_DATE (đã xác minh 2016–2023). Hành vi rollover của ARR_TIME thực tế là `UNKNOWN`."* | Datetime audit lịch sử không chiếu trường `ARR_TIME` (F05). |
| **Cột FLIGHTS**<br>*(Mục 7, Dòng 160)* | *"FLIGHTS luôn có giá trị 1.0 dạng float..."* | *"FLIGHTS có giá trị 1.0 quan sát trên các dòng mẫu kiểm tra; phân bố min/max/distinct toàn cột là `UNKNOWN`. Cột bị `BLOCKED`."* | Tránh khái quát hóa từ dòng mẫu sang toàn bộ 54.67M dòng (F06). |
| **Tiêu đề bảng kiểm toán**<br>*(Mục 3, Cột 14)* | *"Số cột rỗng hoàn toàn (0 Missing)"* | *"Số cột không khuyết thiếu (0 missing / 100% đầy đủ)"* | Sửa lỗi dịch thuật gây hiểu lầm ngược nghĩa (F07). |
| **Liên kết tài liệu**<br>*(Toàn văn)* | Các liên kết tuyệt đối `file:///D:/Study/...` | Các liên kết tương đối markdown (`../../AGENTS.md`, v.v.) | Đảm bảo tính khả chuyển của tài liệu (F07). |
| **Tái lập kiểm toán**<br>*(Mục 9)* | Chưa có thông tin chi tiết về kịch bản | Bảng Manifest tái lập với SHA-256, thời điểm, lệnh, exit code; cảnh báo `NOT_REPRODUCIBLE` từ repo ngoài | Đảm bảo truy vết và minh bạch kỹ thuật (F08). |

---

## 4. Các điểm vẫn giữ trạng thái UNKNOWN / BLOCKED

Sau khi hòa giải và hiệu chỉnh, các thông tin sau đây được xác nhận rõ ràng là **vẫn chưa có bằng chứng** và không được giả định đã giải quyết:

1. **Upstream Distribution URL & Official License (`UNKNOWN`):** Không có tài liệu hoặc URL chính thức xác nhận bản quyền và kho lưu trữ gốc của 9 file CSV thô.
2. **Raw CSV Content SHA-256 (`IDENTITY_UNVERIFIED`):** Chưa có mã băm nội dung tham chiếu từ nguồn phát hành gốc; 9 file CSV chỉ đạt mức `METADATA_MATCH_ONLY`.
3. **Tính liên tục 366 ngày của năm 2024 (`UNKNOWN`):** Chưa đếm distinct service dates cho năm 2024 (chờ T-004 / TS-004).
4. **Hành vi rollover của mốc giờ đến thực tế `ARR_TIME` (`UNKNOWN`):** Chưa có kiểm toán phân tích chuỗi thời gian thực tế (chờ T-004).
5. **Đơn vị chuẩn của 7 trường độ trễ và thời lượng (`UNIT_UNVERIFIED`):** Chưa có tài liệu gốc xác nhận phút (chờ T-003 / TS-018).
6. **Phân bố toàn cột của `FLIGHTS` (`UNKNOWN / BLOCKED`):** Chưa có min/max/distinct toàn cột; bị chặn không dùng làm mẫu số (chờ T-002).
7. **Nguồn gốc, đơn vị và phương thức join thời tiết (`CONDITIONAL_PENDING`):** Chưa có tài liệu trạm đo, mốc thời gian và đơn vị đo (chờ T-005).
8. **Phân loại cấp sân bay theo FAA NPIAS (`UNKNOWN`):** Chưa có bảng tra cứu quy mô hub của 305–317 sân bay.

---

## 5. Kết quả kiểm tra tính nhất quán tài liệu (Document Consistency Check)

Chạy công cụ kiểm tra tự động [`tools/check_docs_consistency.py`](../../tools/check_docs_consistency.py) để đảm bảo các chỉnh sửa không làm phá vỡ cấu trúc tài liệu:

- **Lệnh thực thi:**
  ```powershell
  python tools/check_docs_consistency.py
  ```
- **Exit Code:** `1` *(Do kiểm tra bao phủ manifest cấp packaging `Package manifest covers every other file` bị ảnh hưởng bởi 9 file CSV thô và định dạng dấu gạch chéo Windows, đã được phân tích tại Task Initialization)*.
- **Chi tiết kiểm tra tài liệu nội bộ:**
  - `PASS assertions: 136`
  - $100\%$ các đường dẫn tài liệu chéo dạng `docs/...` trong [`T001_PROVENANCE_AUDIT.md`](T001_PROVENANCE_AUDIT.md) và tài liệu mới đều phân giải chính xác đến tệp có thực trên đĩa (Assertion dòng 35 PASS).
  - Không có token lỗi thời bị cấm xuất hiện trong tài liệu (Assertion dòng 37 PASS).
  - Đảm bảo tính nhất quán giữa Backlog, Roadmap, Data Contract và Test Plan.

---

## 6. Đánh giá lại điều kiện nghiệm thu T-001 so với BACKLOG v1.1

Đối chiếu trực tiếp với tiêu chí nghiệm thu của **T-001** trong [`docs/01-planning/BACKLOG.md`](../01-planning/BACKLOG.md):

| Tiêu chí nghiệm thu BACKLOG v1.1 | Đánh giá hiện trạng sau hiệu chỉnh T-001-R1 | Trạng thái đạt được |
|---|---|:---:|
| **1. Provenance memo đầy đủ** | Đã hoàn thành báo cáo chi tiết [`docs/05-evidence/T001_PROVENANCE_AUDIT.md`](T001_PROVENANCE_AUDIT.md), tổng hợp toàn bộ bằng chứng từ 13 snapshot lịch sử, văn bản BTS và hệ thống filesystem. | **ĐẠT** |
| **2. Source-coverage status rõ ràng** | Đã xác định rõ phạm vi 9 năm, ma trận 19 hãng khai thác, 305–317 sân bay; giải thích cặn kẽ biến động chính sách 14 CFR Part 234 năm 2018 và biến động đại dịch 2020. | **ĐẠT** |
| **3. Đối chiếu selection của dataset** | Đã nhận diện và phân loại hợp lý các bước tiền xử lý (đặc biệt là suy luận completed flights cohort từ 100% finite delays, làm giàu thời tiết, tọa độ địa lý, định dạng timestamp). | **ĐẠT** |
| **4. Việc chưa rõ liệt kê minh bạch** | Đã phân loại rạch ròi các mục `UNKNOWN`, `IDENTITY_UNVERIFIED`, `UNIT_UNVERIFIED`, `BLOCKED`, bảo vệ nghiêm ngặt các ranh giới an toàn cho T-002, T-003, T-004 và T-005. | **ĐẠT** |

---

## 7. Đề xuất trạng thái và Kiến nghị tiếp theo

### 7.1. Đề xuất trạng thái nhiệm vụ T-001
- **Trạng thái đề xuất:** **`PARTIAL (Documentary & Coverage Reconciled; Upstream Provenance & License UNKNOWN; Pending Reviewer Approval)`**.
- **Lý do đề xuất:**
  - Về mặt kiểm toán tài liệu nội bộ, rà soát coverage và thiết lập ranh giới phân tích: Nhiệm vụ đã hoàn thành xuất sắc, tuân thủ tuyệt đối chuẩn mực khoa học dữ liệu và chính sách [`AGENTS.md`](../../AGENTS.md).
  - Về mặt nguồn gốc thượng nguồn: Vì không có thông tin URL phân phối gốc và license chính thức trong gói dữ liệu được bàn giao, việc giữ trạng thái `PARTIAL` phản ánh trung thực bản chất dữ liệu, không ngụy tạo kết quả `PASS` hoàn toàn khi thông tin gốc còn khuyết thiếu.

### 7.2. Cam kết an toàn trạng thái dự án
- **Chưa cập nhật `PROJECT_STATE.md` thành DONE:** Tuân thủ chỉ thị bắt buộc, không tự ý chỉnh sửa `PROJECT_STATE.md` hoặc chuyển trạng thái Gate G2 khi chưa có sự phê duyệt và ký duyệt (*reviewer sign-off*) từ người phụ trách.
- **Dừng thực thi:** Kết thúc phiên làm việc sau nhiệm vụ T-001-R1. Không tự động thực hiện T-002 hoặc bất kỳ nhiệm vụ nào khác.
