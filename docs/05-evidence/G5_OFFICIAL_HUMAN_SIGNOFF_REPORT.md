# Báo cáo Nghiệm thu Chính thức Gate G5 bởi Project Lead (Official Human Signoff Report)

**Document ID:** `G5_OFFICIAL_HUMAN_SIGNOFF_REPORT`  
**Date:** 2026-10-21  
**Project:** US Flight Performance Analysis 2016–2024  
**Task:** `OFFICIAL-G5-HUMAN-SIGNOFF`  
**Roles:** Project Governance Officer, Independent Technical Reviewer, Senior Big Data Engineering Advisor  
**Human Authority:** Project Lead  
**Final Governance Verdict:** **`G5_PASS_CONTROLLED`**

---

## 1. Căn cứ Pháp lý & Chỉ thị Ủy quyền Tường minh của Project Lead (Human Authorization Basis)

Vào ngày 2026-10-21, Project Lead — người có thẩm quyền phê duyệt cao nhất của dự án — đã ban hành chỉ thị phê duyệt chính thức bằng văn bản thông qua prompt điều hành `MASTER PROMPT — OFFICIAL G5 HUMAN SIGNOFF & CONTROLLED CLOSEOUT`:

> **D3 — APPROVED:** "Tôi approve the official controlled technical signoff of TS-018, based on the previously reviewed evidence of 1,500 matched flight keys and 10,500 exact numeric comparisons across seven CORE fields, within the scope of FP-DEC-019 Option B."
>
> **D4 — APPROVED:** "Tôi approve closing Gate G5 as PASS (CONTROLLED), provided D1, D2, D3 and all 19 G5 exit criteria are validly satisfied."
>
> **Chứng thực Người tải (Downloader Attestation cho D1):** "Tôi cũng xác nhận một cách tường minh rằng **tôi là người tải bộ dữ liệu BTS**. Tuyên bố này là sự chứng thực của người tải (downloader attestation), không phải tuyên bố rằng BTS đã ký số tệp ZIP."
>
> **Ranh giới Cấm tuyệt đối:** "**TÔI KHÔNG CẤP PHÉP D5 HOẶC CHẠY INGESTION SẢN XUẤT (I DO NOT AUTHORIZE D5 OR PRODUCTION INGESTION).**"

Chỉ thị trên thỏa mãn đầy đủ các điều kiện tiên quyết bị phong tỏa trước đây đối với Decision D1, D3, D4 và hoàn thành toàn bộ chuỗi nghiệm thu nhân sự của Gate G5.

---

## 2. Bảng Trạng thái Chung quyết D1–D4 (Final States)

| Quyết định | Nội dung / Phạm vi | Trạng thái Trước khi Duyệt | Trạng thái Chung quyết | Căn cứ Phê duyệt / Bằng chứng |
| :---: | :--- | :---: | :---: | :--- |
| **D1** | **BTS Source Provenance Attestation** | `PENDING_HUMAN_SOURCE_ATTESTATION` | **`PASS (CONTROLLED)`** | Project Lead xác nhận tường minh *"tôi là người tải bộ dữ liệu BTS"*; xác thực vật lý tệp `T_ONTIME_REPORTING_20261019_112232.zip` (29.975.383 bytes, SHA-256 `342de99f65561fb856b524c704f2ad3851f8015f52251668ece346dff1350ae6`, ZIP testzip CRC `PASS`). |
| **D2** | **FP-DEC-019 Option B Formal Policy** | `APPROVED_WITH_CONDITIONS` | **`APPROVED_WITH_CONDITIONS`** | Phê duyệt áp dụng đối soát RAW CSV 2019 và BTS TranStats tháng 1/2019 cho 7 trường số đo CORE làm căn cứ nghiệm thu TS-018. |
| **D3** | **TS-018 BTS Parity Human Technical Signoff** | `CONDITIONALLY_ACCEPTED_PENDING_PREREQUISITES` | **`PASS (CONTROLLED)`** | Project Lead phê duyệt chỉ thị D3; đối soát 1.500 khóa bay, 10.500/10.500 giá trị bitwise exact trên 7 trường CORE; 14/14 negative tests PASS; giải quyết ngoại lệ `G2-EXC-001`. |
| **D4** | **Gate G5 Human Gate Signoff** | `IN_PROGRESS / HUMAN_SIGNOFF_PENDING` | **`APPROVED`** | Project Lead phê duyệt chỉ thị D4; toàn bộ 19/19 tiêu chí kỹ thuật Gate G5 đạt chuẩn; chính thức đóng Gate G5 đạt `PASS (CONTROLLED)`. |

---

## 3. Trạng thái Chung quyết của TS-018 và Ngoại lệ `G2-EXC-001`

- **Nhiệm vụ `TS-018`:** **`PASS (CONTROLLED)`**
  - Căn cứ theo chính sách `FP-DEC-019 Option B`, đối soát thực nghiệm giữa tệp nguồn `data/raw/tabular/2019/flight_with_weather_2019.csv` (tháng 1/2019) và tệp đối chiếu chính thức `data/reference/bts_transtats/original/T_ONTIME_REPORTING_20261019_112232.zip` trên 1.500 bản ghi phân tầng (stratified sample) đạt:
    - `1.500 / 1.500` khóa nghiệp vụ khớp chính xác (`100.0%`).
    - `10.500 / 10.500` điểm đo số học trên 7 trường CORE (`ARR_DELAY`, `DEP_DELAY`, `TAXI_OUT`, `TAXI_IN`, `AIR_TIME`, `ACTUAL_ELAPSED_TIME`, `CRS_ELAPSED_TIME`) khớp bitwise exact (`delta = 0.000000`, sai số `0.0%`).
    - `14 / 14` negative mutation counterexamples đạt kết quả phát hiện lỗi `PASS` (tỷ lệ fail-closed `100.0%`).
- **Ngoại lệ `G2-EXC-001`:** **`RESOLVED_BY_TS018_APPROVED_OPTION_B`**
  - Chuyển trạng thái từ `ACTIVE` sang `RESOLVED_BY_TS018_APPROVED_OPTION_B`.
  - Đơn vị đo phút của 7 trường số đo cốt lõi đã được kiểm chứng thực nghiệm tính nhất quán với nguồn dữ liệu quốc gia BTS TranStats trong phạm vi phân tích mô tả.
- **Hợp đồng Nhiệm vụ `T-011`:** **`PASS / COMPLETED (FULL_CONTRACT_CLOSED)`**
  - Toàn bộ các cấu phần kỹ thuật (8 CORE KPIs, 17 cột hợp đồng, GK sketch TS-008, TS-012/013, SingleWriterLock) và điều kiện đối soát TS-018 đã hoàn tất và đóng hợp đồng.

---

## 4. Phán quyết Quản trị Chung cuộc Gate G5 (Final Governance Verdict)

**Phán quyết:** **`G5_PASS_CONTROLLED`**

- **Gate G5:** Đã chuyển trạng thái từ `IN_PROGRESS` sang **`PASS (CONTROLLED)`**.
- Toàn bộ **19/19 tiêu chí exit criteria của Gate G5** đã được đối chiếu, thẩm tra và thỏa mãn đầy đủ (xem chi tiết tại [`docs/05-evidence/G5_D4_G5_HUMAN_GATE_SIGNOFF_DRAFT.md`](G5_D4_G5_HUMAN_GATE_SIGNOFF_DRAFT.md)).
- **Gate G6:** Chuyển trạng thái từ `NOT_STARTED / BLOCKED` sang **`READY_FOR_PREPARATION / BLOCKED_ON_D5`**.
- Quyết định kiến trúc `G6-ARCH-2016 Option B` (`FP-DEC-020`) được duy trì có hiệu lực để định hướng việc thực thi sản xuất năm 2016 khi có lệnh.

---

## 5. Ranh giới Giới hạn Còn tồn tại Được Bảo lưu Nghiêm ngặt (Explicit Residual Limitations)

Việc nghiệm thu Gate G5 `PASS (CONTROLLED)` không xóa bỏ mà tiếp tục ràng buộc nghiêm ngặt các rủi ro và giới hạn đã được công bố:

1. **`PARQUET_PARITY_NOT_TESTED`:** Đối soát TS-018 được thực hiện trực tiếp giữa RAW CSV 2019 và BTS reference ZIP; chưa kiểm thử parity trực tiếp trên các tệp Parquet sản xuất.
2. **`OR-05` (Khuyết tật Dữ liệu Tháng 3/2024):** Bộ dữ liệu năm 2024 chỉ có `335/366` ngày (thiếu toàn bộ 31 ngày của Tháng 3/2024); siêu dữ liệu bắt buộc ghi nhận `source_coverage_status = PARTIAL`.
3. **`OR-08` (Nguồn gốc Thượng nguồn Kaggle):** Nguồn gốc tải lên thượng nguồn Kaggle chưa được kiểm chứng danh tính số (`IDENTITY_UNVERIFIED`); nhận diện nội dung dựa trên SHA-256 cục bộ của 9 tệp CSV thô.
4. **`FP-DEC-017` (Loại trừ Thời tiết khỏi CORE):** Nhánh thời tiết giữ phán quyết `CONDITIONAL_NO_GO`, không tham gia vào các chỉ số CORE và không được suy diễn tương quan/nhân quả.
5. **Giới hạn Mẫu TS-018:** Bằng chứng đối soát đơn vị đo dựa trên tháng 1/2019 và không chứng minh sự đồng nhất nội dung của toàn bộ 54,67 triệu dòng trong 9 năm.

---

## 6. Danh mục Hồ sơ & Mã nguồn Được Cập nhật (Files Updated)

1. [`docs/05-evidence/G5_D1_BTS_PROVENANCE_ATTESTATION_DRAFT.md`](G5_D1_BTS_PROVENANCE_ATTESTATION_DRAFT.md): Cập nhật phán quyết D1 thành `PASS (CONTROLLED)` ghi nhận chứng thực người tải của Project Lead.
2. [`docs/05-evidence/G5_D3_TS018_HUMAN_TECHNICAL_SIGNOFF_DRAFT.md`](G5_D3_TS018_HUMAN_TECHNICAL_SIGNOFF_DRAFT.md): Cập nhật phán quyết D3 thành `PASS (CONTROLLED)`, `TS-018 = PASS (CONTROLLED)`, `G2-EXC-001 = RESOLVED_BY_TS018_APPROVED_OPTION_B`, `T-011 FULL_CONTRACT_CLOSEOUT = PASS (CONTROLLED)`.
3. [`docs/05-evidence/G5_D4_G5_HUMAN_GATE_SIGNOFF_DRAFT.md`](G5_D4_G5_HUMAN_GATE_SIGNOFF_DRAFT.md): Cập nhật phán quyết D4 thành `PASS (CONTROLLED)`, Gate G5 = `PASS (CONTROLLED)`, Gate G6 = `READY_FOR_PREPARATION / BLOCKED_ON_D5`.
4. [`docs/02-design/DECISIONS.md`](../02-design/DECISIONS.md): Ghi nhận giải quyết ngoại lệ `G2-EXC-001 = RESOLVED_BY_TS018_APPROVED_OPTION_B`.
5. [`docs/04-execution/PROJECT_STATE.md`](../04-execution/PROJECT_STATE.md): Cập nhật bảng Gate (G5 = `PASS`, G6 = `READY_FOR_PREPARATION / BLOCKED_ON_D5`), T-011 = `PASS / COMPLETED (FULL_CONTRACT_CLOSED)`.
6. [`docs/04-execution/AI_HANDOFF.md`](../04-execution/AI_HANDOFF.md): Đồng bộ hóa trạng thái Gate G5, Gate G6 và giải quyết G2-EXC-001.
7. [`docs/01-planning/BACKLOG.md`](../01-planning/BACKLOG.md): Đồng bộ hóa trạng thái T-011, Gate G5 exit criteria, và TS-018.
8. [`docs/03-quality/CHANGELOG.md`](../03-quality/CHANGELOG.md): Bổ sung bản ghi thay đổi chính thức `docs-v1.1-g5-official-human-signoff`.
9. [`docs/05-evidence/G5_OFFICIAL_HUMAN_SIGNOFF_REPORT.md`](G5_OFFICIAL_HUMAN_SIGNOFF_REPORT.md): Báo cáo nghiệm thu chung cuộc này.

---

## 7. Xác nhận Ranh giới Điều hành: D5 Giữ NOT_AUTHORIZED & Zero Spark Ingestion

Xác nhận kiểm toán độc lập về ranh giới an toàn:
- **Decision D5:** Giữ nghiêm ngặt trạng thái **`NOT_AUTHORIZED`**.
- **Chốt chặn Mã nguồn (`src/flight_pipeline/ingestion/coordinator.py`):**
  - Biến cờ bảo vệ: `D5_AUTHORIZED_BY_PROJECT_LEAD = False` giữ nguyên bất biến.
  - Chốt chặn fail-closed hoạt động tuyệt đối: Mọi nỗ lực thực thi nạp sản xuất không có ủy quyền đều bị chặn ngay tại tiền điều kiện.
- **Thực thi Spark Sản xuất:** **Hoàn toàn KHÔNG (ZERO production Spark execution).**
  - Không có byte dữ liệu sản xuất nào được ghi vào đĩa.
  - Không có bất kỳ thay đổi nào tác động lên 9 tệp RAW CSV (15.196.366.173 bytes) hoặc 50 tệp Parquet staging T-010.

---

## 8. Các Hành động Bắt buộc Kế tiếp Trước khi Thực thi Sản xuất T-012

Để có thể bắt đầu nạp sản xuất năm 2016 theo `G6-ARCH-2016 Option B` khi Project Lead cho phép:
1. **Dọn dẹp Bộ nhớ RAM Trạm làm việc:** Người vận hành máy trạm cần giải phóng RAM khả dụng đạt tối thiểu $\ge 4.0\text{ GiB}$ (kiểm tra tài nguyên bộ nhớ khả dụng trước khi kích hoạt JVM Spark).
2. **Quyết định Ủy quyền D5 của Project Lead:** Project Lead ban hành quyết định chính thức ủy quyền thực thi sản xuất (`Decision D5 = AUTHORIZED`).
3. **Kích hoạt Chốt chặn Coordinator (Controlled 1-line patch):** Sau khi có quyết định D5, áp dụng bản vá kiểm soát 1 dòng duy nhất trong `src/flight_pipeline/ingestion/coordinator.py`:
   ```python
   # Chuyển từ:
   D5_AUTHORIZED_BY_PROJECT_LEAD: bool = False
   # Sang:
   D5_AUTHORIZED_BY_PROJECT_LEAD: bool = True
   ```
4. **Khởi động Nạp Sản xuất Năm Đầu tiên (2016):** Thực thi `IngestionCoordinator` cho năm 2016, kiểm tra tính toàn vẹn `run_manifest.json` và `execution_receipt.json` trước khi cấp phép cho các năm tiếp theo (2017–2024).
