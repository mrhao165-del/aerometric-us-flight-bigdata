# G6 Human Governance & Decision Signoff Dossier (D1–D5)

**Document ID:** `DOC-G6-GOV-HANDOFF-001`  
**Classification:** PROJECT GOVERNANCE & FORMAL HUMAN HANDOFF  
**Current Gate:** Gate G5 = IN_PROGRESS / TECHNICALLY READY  
**Target Gate:** Gate G6 = NOT_STARTED / BLOCKED (Awaiting D5 Approval)  
**Evaluator:** Principal Big Data Architect, Independent Auditor & Project Governance Reviewer  
**Date:** 2026-10-20  
**Overall Readiness Verdict:** `TECHNICALLY_READY_AWAITING_PROJECT_LEAD_APPROVAL`  

---

## 1. Mục đích và Giới hạn Thẩm quyền Tuyệt đối

Theo điều lệ quản trị nghiêm ngặt tại `AGENTS.md` và `DECISIONS.md`:
1. AI Agent **tuyệt đối không được tự ý phê duyệt** các quyết định chiến lược cấp dự án (D1–D5).
2. AI Agent **không được tự chuyển trạng thái Gate G5 thành PASS** hoặc **tự ý mở Gate G6**.
3. AI Agent **không được tự ý thực thi pipeline T-012 full-run** trên 54,7 triệu hàng khi chưa có lệnh ủy quyền chính thức từ Project Lead.
4. Hồ sơ này được thiết lập như một văn kiện bàn giao kỹ thuật hoàn chỉnh (Controlled Technical Signoff Dossier), đệ trình Project Lead các bằng chứng thực nghiệm để đưa ra quyết định độc lập.

---

## 2. Ma trận Quyết định Quản trị (Decisions D1–D5)

| Mã Quyết định | Nội dung Quyết định | Trạng thái Kỹ thuật | Trạng thái Quản trị | Thẩm quyền Ký duyệt |
| :---: | :--- | :---: | :---: | :---: |
| **D1** | Nghiệm thu chính thức TS-018 & Đóng Gate G5 | **TECHNICALLY_READY** | **PENDING_HUMAN_SIGNATURE** | Project Lead |
| **D2** | Phê duyệt Quyết định Kiến trúc FP-DEC-019 (BTS Intake & Parity) | **TECHNICALLY_READY** | **PENDING_HUMAN_SIGNATURE** | Project Lead |
| **D3** | Đóng Ngoại lệ Schema G2-EXC-001 | **CONDITIONS_MET** | **ACTIVE (Awaiting Signoff)** | Project Lead |
| **D4** | Lựa chọn Kiến trúc Tích hợp Baseline 2016 (Option A vs Option B) | **RECOMMEND_OPTION_B** | **PENDING_DECISION** | Project Lead |
| **D5** | Cấp phép Thực thi Full-Run T-012 (Gia nhập Gate G6) | **PREFLIGHT_PASS** | **BLOCKED (Not Authorized)** | Project Lead |

---

## 3. Chi tiết Bằng chứng Kỹ thuật Từng Quyết định

### 3.1 Quyết định D1: Nghiệm thu TS-018 & Đóng Gate G5
* **Cơ sở Bằng chứng:**
  - Đối chiếu vật lý 2 nguồn thực tế: 1.500/1.500 chuyến bay chứng từ chọn ngẫu nhiên từ file CSV thô 2019 khớp 100% với tệp nén chính thức từ Cục Thống kê Giao thông vận tải Hoa Kỳ (BTS TranStats ZIP `T_ONTIME_REPORTING_20261019_112232.zip`).
  - 10.500/10.500 giá trị thuộc 7 trường KPI cốt lõi khớp số học chính xác tuyệt đối (`CRS_DEP_TIME`, `DEP_TIME`, `DEP_DELAY`, `CRS_ARR_TIME`, `ARR_TIME`, `ARR_DELAY`, `DISTANCE`).
  - Bộ kiểm định nghiêm ngặt `verify_bts_parity_strict.py` vượt qua toàn bộ 14 bài kiểm thử tiêu cực chống giả mạo chứng từ.
* **Đề xuất:** Phê duyệt nghiệm thu TS-018 và đóng Gate G5.

### 3.2 Quyết định D2: Phê duyệt FP-DEC-019
* **Cơ sở Bằng chứng:** Hồ sơ kỹ thuật chứng minh tính xác thực nguồn gốc dữ liệu BTS TranStats, loại bỏ sự phụ thuộc không thể kiểm chứng vào Kaggle (OR-08).
* **Đề xuất:** Phê duyệt FP-DEC-019 với điều kiện ghi nhận đầy đủ rủi ro nguồn gốc Kaggle.

### 3.3 Quyết định D3: Đóng Ngoại lệ Schema G2-EXC-001
* **Cơ sở Bằng chứng:** Bằng chứng vật lý TS-018 đã chứng minh 7 trường KPI cốt lõi có đơn vị đo lường và định dạng chuẩn (phút, dặm, giờ địa phương HHMM). Mọi điều kiện tiên quyết của G2-EXC-001 đã được thỏa mãn về mặt kỹ thuật.
* **Đề xuất:** Ký đóng G2-EXC-001 đồng thời với D1.

### 3.4 Quyết định D4: Khuyến nghị Kiến trúc Baseline 2016 (Option B vs Option A)
* **Phân tích Hai Phương án:**
  - **Option A (Tái sử dụng Artifact Parquet T-010 Đã Đóng Băng):** Sử dụng trực tiếp 50 tệp Parquet của năm 2016 tạo ra từ Task T-010. Tiết kiệm tài nguyên tính toán nhưng tạo ra sự không đồng nhất về lineage vì T-010 được chạy trên cấu hình staging cũ và chưa trải qua quy trình xuất bản `SafePublisher` của G6.
  - **Option B (Khuyến nghị — Tái Nhập Toàn diện Dưới Schema Đã Xác minh):** Thực thi ingestion năm 2016 song song với các năm 2017–2024 trong T-012 bằng pipeline chuẩn hóa thống nhất. Đảm bảo toàn bộ 9 năm có chung cấu trúc metadata, định dạng Parquet, partition scheme, và manifest layout.
* **Khuyến nghị Chính thức:** **LỰA CHỌN OPTION B**. Lưu trữ 50 tệp Parquet T-010 làm đối chứng chuẩn (Benchmark Golden Baseline) để so sánh đối soát 1:1 sau khi hoàn thành T-012.

### 3.5 Quyết định D5: Cấp phép Thực thi Full-Run T-012 (Gia nhập Gate G6)
* **Cơ sở Bằng chứng:**
  - Bộ tiền kiểm an toàn (`check_writer_preflight_safety.py`) đạt 9/9 PASS.
  - Bộ kiểm tra snapshot 9 năm (`verify_multiyear_snapshot.py`) đạt 20/20 PASS.
  - Đã khắc phục triệt để các lỗ hổng S01, S02, S03, S04.
* **Tình trạng:** **HIỆN TẠI ĐANG BỊ KHÓA (BLOCKED)**. AI Agent dừng mọi hoạt động ghi dữ liệu production, sẵn sàng chờ quyết định của Project Lead.

---

## 4. Các Giới hạn Quản trị Tiếp tục Được Duy trì Nghiêm ngặt

Trong suốt quá trình bàn giao và vận hành Gate G6, các ranh giới sau đây bắt buộc phải được duy trì:
1. **OR-08 (Kaggle Provenance Unverified):** Dữ liệu Kaggle không được coi là chân lý gốc; chỉ có BTS TranStats là nguồn tham chiếu chuẩn mực.
2. **OR-05 (2024 Partial Coverage):** Năm 2024 thiếu dữ liệu tháng 3. Validator bắt buộc phải gắn nhãn `source_coverage_status == 'PARTIAL'`. Không được gọi tổng số hàng là tổng chuyến bay thực tế của Hoa Kỳ.
3. **FP-DEC-017 (Weather CONDITIONAL_NO_GO):** Nhánh dữ liệu thời tiết tiếp tục bị loại trừ hoàn toàn khỏi 8 CORE KPI. Tuyệt đối không để thời tiết ảnh hưởng đến pipeline CORE.
4. **PARQUET_PARITY_NOT_TESTED:** Tính tương đương số học trên Parquet thực tế sẽ chỉ được kiểm chứng sau khi hoàn thành ghi production dataset trong T-012; hiện tại mới chỉ kiểm chứng trên CSV gốc và BTS.

---

## 5. Kết luận Bàn giao

Hệ thống đã đạt trạng thái **TECHNICALLY READY**. AI Agent trân trọng chuyển giao toàn bộ hồ sơ cho Project Lead để thực hiện các quyết định quản trị D1–D5.
