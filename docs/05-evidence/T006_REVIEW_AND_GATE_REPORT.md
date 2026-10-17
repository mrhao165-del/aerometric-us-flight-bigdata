# T-006 DELIVERABLE D: TECHNICAL REVIEW & GATE READINESS REPORT

**Task ID:** `T-006`  
**Gate:** `G3`  
**Document Nature:** Technical Architecture Evaluation & Governance Recommendation (`REVIEW_ONLY`)  
**Project:** US Flight Performance Analysis (2016–2024) using Apache Spark / PySpark  
**Status:** `PROPOSED_FOR_PROJECT_LEAD_REVIEW`  
**Date:** 2026-10-17  

---

## 1. Mục đích Báo cáo & Bối cảnh Thẩm định

Báo cáo này tổng hợp kết quả thẩm định kỹ thuật độc lập đối với toàn bộ gói tài liệu thiết kế kiến trúc thuộc Gate G3 / Nhiệm vụ `T-006`, bao gồm:
* Deliverable A: Thiết kế Kiến trúc & Runtime PySpark (`T006_ARCHITECTURE_AND_RUNTIME_DESIGN.md`)
* Deliverable B: Ánh xạ 34 Cột Schema, Chất lượng & Lineage (`T006_SCHEMA_QUALITY_AND_LINEAGE_DESIGN.md`)
* Deliverable C: Bản vẽ Kỹ thuật 8 CORE KPIs & Ma trận Kiểm thử (`T006_KPI_AND_TEST_BLUEPRINT.md`)
* Deliverable E: Bảng Kê khai Thực thi & Bằng chứng Mã hóa (`T006_EXECUTION_MANIFEST.md`)
* Tài liệu Thiết kế Hệ thống Cập nhật: [`docs/02-design/ARCHITECTURE.md`](../02-design/ARCHITECTURE.md)

Nhiệm vụ này là **nhiệm vụ thiết kế tài liệu và lập kế hoạch kỹ thuật**, tuyệt đối **KHÔNG** viết mã nguồn nạp dữ liệu sản xuất (thuộc G4/T-007), không chạy Spark sản xuất trên 54.67M dòng (thuộc G6), và không tự ý chuyển Gate G3 sang trạng thái `PASS`.

---

## 2. Bảng Đánh giá Mức độ Đáp ứng Tiêu chí Chấp nhận (Acceptance Checklist)

Dưới đây là bảng đối chiếu 21 tiêu chí chất lượng nghiêm ngặt của Gate G3 / Task T-006:

| STT | Tiêu chí Kiểm định Chất lượng | Bằng chứng Đáp ứng & Tài liệu Tham chiếu | Kết quả Thẩm định |
| :---: | :--- | :--- | :---: |
| 1 | Gate G2 đạt `PASS` có bằng chứng con người hợp lệ | Biên bản [`G2_OFFICIAL_SIGNOFF_HUMAN_ACCEPTANCE_RECORD.md`](G2_OFFICIAL_SIGNOFF_HUMAN_ACCEPTANCE_RECORD.md) (SHA-256: `42c61313...`) | **PASS** |
| 2 | Nhiệm vụ T-006 được khởi động có kiểm soát | Chuyển `T-006 = IN_PROGRESS`, Gate `G3 = IN_PROGRESS / NOT_PASSED` trong `PROJECT_STATE.md`, `AI_HANDOFF.md`, `BACKLOG.md` | **PASS** |
| 3 | QA guards nhận diện đúng trạng thái G3 | Nâng cấp INV-12 trong `verify_g2_repo_apply_r1_semantic_invariants.py`, mở rộng đột biến `MUT-06A..C` chặn khởi động trái phép | **PASS** |
| 4 | Sơ đồ kiến trúc và luồng dữ liệu rõ ràng | Sơ đồ Mermaid End-to-End Pipeline & bảng luồng dữ liệu chi tiết trong Deliverable A & `ARCHITECTURE.md` | **PASS** |
| 5 | Stack Spark/Python/Java có phân tích tương thích | Khảo sát thực tế máy trạm: Python 3.10.11 + OpenJDK 21 LTS + PySpark 4.0.1; chuẩn bị fallback PySpark 3.5.3 + JDK 17 | **PASS** |
| 6 | Có bảng ngân sách tài nguyên thực tế | Bảng cấp phát bộ nhớ (Driver 6g, Overhead 1-2g, Shuffle 32-64, Scratch D:\) trong Deliverable A, không giả định 100% RAM | **PASS** |
| 7 | Ánh xạ chính xác toàn bộ 34 cột raw CSV | Bảng ánh xạ chuẩn tắc 34 cột kèm Null Policy, Cast Policy và Downstream Rule trong Deliverable B | **PASS** |
| 8 | Bảo toàn hạch toán dòng DC-11 & siêu dữ liệu DC-12 | Phương trình $\mathbf{raw = accepted + quarantined + rejected}$ và siêu dữ liệu $N_{valid}$ được tích hợp đầy đủ trong Deliverable B & C | **PASS** |
| 9 | Stable Lineage có phương án và ranh giới rõ ràng | Phân tích lỗi Spark offset; đề xuất physical record ordinal; bảo tồn cặp `YX 3624`; gắn nhãn `OPEN_DESIGN_VERIFICATION` (TS-020) | **PASS** |
| 10 | Bảo vệ biểu diễn thời gian an toàn (FP-DEC-007) | Cấm trừ chuỗi timestamp; cấm cộng +24h qua đêm; giữ nguyên 2400; loại bỏ timestamp phái sinh khỏi CORE trong Deliverable B | **PASS** |
| 11 | Xử lý đúng độ phủ lịch năm 2024 (OR-05) | Xác nhận 335/366 ngày khuyết Tháng 3; cấm nội suy dữ liệu giả định; gắn nhãn `source_coverage_status = PARTIAL` | **PASS** |
| 12 | Nhánh Weather không làm hỏng dữ liệu CORE | Tuân thủ `FP-DEC-017` (`CONDITIONAL_NO_GO`); giữ 6 cột raw; cấm quarantine dòng CORE vì thiếu thời tiết | **PASS** |
| 13 | 8 CORE KPIs có bản vẽ kỹ thuật đầy đủ | Đặc tả chi tiết 14 mục cho từng KPI (`KPI-01..08`) dựa trên nguồn duy nhất `KPI_SPEC.md` trong Deliverable C | **PASS** |
| 14 | Có cấu trúc layout lưu trữ Parquet và phân vùng | Phân tích lựa chọn phân vùng `YEAR` (9 partitions); cấu trúc thư mục staging/curated/quarantine/aggregates trong Deliverable A | **PASS** |
| 15 | Ma trận truy vết kiểm thử Gate G4–G7 chính xác | Ánh xạ chi tiết 20 bài kiểm thử `TS-001..TS-020` kèm phân định trạng thái `SYNTHETIC_PLANNED`, `SMOKE_PLANNED`, `FULL_RUN_PLANNED` | **PASS** |
| 16 | Điều kiện ngoại lệ `G2-EXC-001` giữ nguyên vẹn | Giữ nguyên nhãn `PROVISIONAL` cho 7 trường số đo CORE; thiết lập `TS-018` tại Gate G5 làm điều kiện chặn bắt buộc cho Gate G6 | **PASS** |
| 17 | Không viết mã nguồn nạp dữ liệu sản xuất | Tuyệt đối tuân thủ ranh giới G3: chỉ lập tài liệu thiết kế kiến trúc, không sinh mã code Spark nạp dữ liệu tại T-006 | **PASS** |
| 18 | Không chạy Spark full-run trên 54.67M dòng | Dữ liệu thô 14.15 GiB được giữ nguyên vẹn ở chế độ Read-Only; không có tiến trình Spark quét dữ liệu thô nào được thực thi | **PASS** |
| 19 | Hệ thống kiểm tra QA làm việc ổn định, 0 lỗi | Cả 5 bộ kiểm tra quản trị (`verify_t003`, `verify_t004`, `semantic_invariants`, `cwtc`, `registry_regression`) đạt `PASS` tuyệt đối | **PASS** |
| 20 | Có đầy đủ bằng chứng và phương án khôi phục | Lưu trữ 8 tệp sao lưu preflight tại `docs/05-evidence/T006_BACKUPS/`; đăng ký mã hóa trong `EVIDENCE_DELIVERABLE_REGISTER.json` | **PASS** |
| 21 | Các quyết định kỹ thuật chưa chốt gắn PROPOSED | Toàn bộ các đề xuất về runtime, phân vùng và lineage đều gắn nhãn `PROPOSED_FOR_PROJECT_LEAD_REVIEW` | **PASS** |

---

## 3. Các Câu hỏi Kiến trúc Mở & Rủi ro Kỹ thuật Cần Theo dõi

1. **Khả năng tương thích của PySpark 4.0.1 trên Windows 10:**
   * *Thực trạng:* Máy trạm đã cài sẵn PySpark 4.0.1 và OpenJDK 21 LTS. Về lý thuyết, Spark 4.0 hỗ trợ tốt Java 21 và môi trường đơn máy. Tuy nhiên, trên Windows, các thư viện Hadoop nhị phân native (`winutils.exe` / `hadoop.dll`) đôi khi có thể phát sinh cảnh báo quyền truy cập đường dẫn tệp tạm thời.
   * *Giải pháp đề xuất:* Tiến hành bài kiểm tra smoke test `TS-014` ngay tại bước khởi tạo Gate G4 (`T-009`). Nếu phát sinh lỗi không tương thích nhị phân, lập tức kích hoạt phương án dự phòng chuyển sang `PySpark 3.5.3` + `OpenJDK 17 LTS`.
2. **Cơ chế Hiện thực hóa Độc lập của Stable Lineage (`TS-020`):**
   * *Thực trạng:* Cặp chuyến bay `YX 3624` (2018-06-21) có toàn bộ business keys giống hệt nhau nhưng là hai dòng vật lý phân biệt. Việc tạo ra `source_row_number` ổn định tuyệt đối trong môi trường đọc phân tán của Spark đòi hỏi kỹ thuật indexer theo thứ tự tệp nguồn.
   * *Giải pháp đề xuất:* Giữ nguyên phân loại **`OPEN_DESIGN_VERIFICATION`**. Thử nghiệm giải pháp đánh số thứ tự dòng vật lý đơn tệp (*single-file partition ordinal*) tại Gate G4/T-007 và Gate G5/T-010 trước khi áp dụng trên quy mô lớn.
3. **Hiệu năng Thực tế của Thuật toán `percentile_approx` (`FP-DEC-015`):**
   * *Thực trạng:* Quyết định đã duyệt yêu cầu tham số `accuracy=10000` cho phép tính P50 và P90 của `ARR_DELAY` (`KPI-06`). Mức accuracy này đòi hỏi vùng đệm bộ nhớ lớn hơn thông thường (`accuracy=1000`).
   * *Giải pháp đề xuất:* Đo đạc mức tiêu hao bộ nhớ và thời gian thực thi của `percentile_approx` trên tập mẫu tại Gate G5 (`T-011` / `TS-008`) để chứng minh tính khả thi trước khi chạy full-run 54.67M dòng.

---

## 4. Các Quyết định Kỹ thuật Trình Duyệt Project Lead

Kính trình Project Lead xem xét và phê duyệt các điểm thiết kế kiến trúc sau đây trước khi triển khai Gate G4:
1. **Phê chuẩn Lựa chọn Runtime Chính:** Cho phép sử dụng cấu hình chính **`Python 3.10` + `OpenJDK 21 LTS` + `PySpark 4.0.1` + `PyArrow 25.0.1`**, với cơ chế dự phòng tự động chuyển sang `PySpark 3.5.3` + `OpenJDK 17` nếu bài test khởi tạo môi trường `TS-014` tại `G4/T-009` phát hiện lỗi nhị phân native.
2. **Phê chuẩn Chiến lược Xử lý Tuần tự Từng Năm (Year-by-Year Batching):** Phê chuẩn kiến trúc nạp dữ liệu độc lập theo từng năm nguồn tại tầng Ingestion và lưu trữ Parquet theo phân vùng `year` (9 partitions), bảo đảm đỉnh tiêu thụ bộ nhớ RAM luôn dưới 6 GiB.
3. **Phê chuẩn Kế hoạch Thực hiện Gate G4 theo Trình tự Chuẩn:** Xác nhận thứ tự triển khai bắt buộc của Gate G4 là:
   $$\mathbf{T\text{-}009}\ (\text{Setup môi trường \& test runner}) \longrightarrow \mathbf{T\text{-}007}\ (\text{Ingestion \& local SHA-256}) \longrightarrow \mathbf{T\text{-}008}\ (\text{Quality, hạch toán dòng \& kiểm tra lịch 2024})$$

---

## 5. Khuyến nghị Nghiệm thu Kỹ thuật (Technical Recommendation)

Toàn bộ gói hồ sơ kỹ thuật của Nhiệm vụ `T-006` đã hoàn tất với chất lượng cao nhất, thỏa mãn 100% các tiêu chí chấp nhận, không phát sinh bất kỳ mâu thuẫn hay hành vi vượt quyền nào.

$$\mathbf{TECHNICAL\ RECOMMENDATION:}\quad \mathbf{T006\_DESIGN\_READY\_FOR\_HUMAN\_REVIEW}$$

* **Lưu ý Pháp lý Quản trị:** Báo cáo này **KHÔNG** tự ý tuyên bố nhiệm vụ T-006 đạt `PASS` và **KHÔNG** tuyên bố Gate G3 đạt `PASS`. Toàn bộ trạng thái quản trị của repository được giữ ở mức:
  * **Gate G2:** `PASS`
  * **Gate G3:** `IN_PROGRESS / NOT_PASSED`
  * **Task T-006:** `IN_PROGRESS`
  * **T-006 Implementation Package:** Sẵn sàng chờ Project Lead phê duyệt nghiệm thu chính thức.
  * **Downstream Tasks (T-009, T-007, T-008):** `NOT_STARTED` / `TODO` (Nghiêm ngặt dừng và chờ chỉ thị tiếp theo).
