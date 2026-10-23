# BÁO CÁO ĐỐI SOÁT VÀ ĐỒNG BỘ AN TOÀN CUỐI CÙNG G5 / G6 (G5 FINAL CLOSEOUT & G6 PRESTART SAFETY ALIGNMENT)

**Dự án:** Phân tích hiệu suất chuyến bay Hoa Kỳ 2016–2024 bằng Apache Spark/PySpark  
**Nhiệm vụ:** `G5-G6-FINAL-ALIGNMENT`  
**Thời điểm lập (UTC):** 2026-10-21T10:00:00Z  
**Cam kết an toàn tuyệt đối:** Zero Spark Production Execution | Zero RAW Mutation | Zero Parquet Baseline Mutation | Zero Pointer Switch | Zero Lock Mutation | Decision D5 remains `NOT_AUTHORIZED`.  
**Phán quyết kỹ thuật & quản trị (Final Verdict):** **`READY_FOR_G5_HUMAN_CLOSEOUT`**

---

## 1. BA VẤN ĐỀ KỸ THUẬT & TÀI LIỆU VÀ PHƯƠNG ÁN KHẮC PHỤC TRIỆT ĐỂ

### 1.1. Vấn đề Task A: Khắc phục lỗi an toàn của Script tiền khởi động (`tools/qa/run_g6_t012_prestart_checks.py`)
Ba khiếm khuyết được phát hiện độc lập trong mã nguồn của bộ chạy kiểm thử trước khởi động đã được xử lý triệt để:
1. **Lỗi nuốt mã lỗi kiểm tra tệp nguồn (Source Integrity Exit Code 0):**
   * *Nguyên nhân cũ:* Bước kiểm tra tệp nguồn CSV 2016 ghi nhận cứng `returncode = 0` ngay cả khi tệp không tồn tại hoặc sai lệch kích thước / mã băm.
   * *Khắc phục:* Viết hàm đánh giá độc lập `evaluate_source_integrity(raw_path)`. Nếu tệp không tồn tại, sai kích thước hoặc sai mã băm SHA-256, ghi nhận chính xác mã lỗi `1` cho bước kiểm tra và đưa vào danh sách lỗi bắt buộc.
2. **Lỗi hàm kết thúc luôn trả về mã 0 (Always Returning Exit Code 0):**
   * *Nguyên nhân cũ:* Hàm `run_checks()` có dòng lệnh kết thúc cứng `return 0` bất kể các kiểm tra con có thất bại hay không.
   * *Khắc phục:* Triển khai cơ chế kiểm soát fail-closed: biến cờ `overall_pass` và danh sách lý do lỗi `failure_reasons`. Nếu bất kỳ kiểm tra bắt buộc nào (tệp nguồn, an toàn khóa, con trỏ xuất bản, dry-run coordinator, chốt chặn quản trị D5, giao diện validator) không đạt mã thoát 0, `run_checks()` bắt buộc trả về mã lỗi `1`.
3. **Lỗi gọi trực tiếp lệnh live coordinator vào thư mục dữ liệu thật:**
   * *Nguyên nhân cũ:* Bước kiểm tra chốt chặn quản trị gọi trực tiếp `coordinator.py` mà không có cờ `--dry-run-preflight`. Mặc dù hiện tại chốt chặn `D5_AUTHORIZED_BY_PROJECT_LEAD = False` ngăn chặn việc chạy, nhưng nếu trong tương lai biến này được bật, việc chạy script kiểm thử sẽ vô tình kích hoạt Spark live ingestion trên dữ liệu thật.
   * *Khắc phục:* **Loại bỏ hoàn toàn lệnh gọi live coordinator vào đường dẫn dữ liệu thật**. Thay thế bằng:
     - Kiểm tra tĩnh mã nguồn (Static Code Inspection): Kiểm tra trực tiếp hằng số `D5_AUTHORIZED_BY_PROJECT_LEAD: bool = False` trong `src/flight_pipeline/ingestion/coordinator.py`.
     - Kiểm thử đơn vị cô lập (Synthetic Unit Test): Thực thi bài test đã có `tests.test_coordinator_preflight_unblock.TestCoordinatorPreflightUnblock.test_09_unauthorized_live_execution_blocked` trong môi trường thư mục tạm hoàn toàn cách ly (`tempfile`).

### 1.2. Vấn đề Task B: Khắc phục các mâu thuẫn trong tài liệu kiến trúc và báo cáo
Ba mâu thuẫn trong tài liệu đã được rà soát và hiệu chỉnh chính xác:
1. **Mâu thuẫn B1 — Loại bỏ mẫu Wildcard không an toàn cho dữ liệu 9 năm:**
   * *Tài liệu hiệu chỉnh:* [`docs/05-evidence/G6_T012_2016_BASELINE_INTEGRATION_DECISION_DRAFT.md`](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/docs/05-evidence/G6_T012_2016_BASELINE_INTEGRATION_DECISION_DRAFT.md) mục 3.3.
   * *Nội dung sửa đổi:* Xóa bỏ khuyến nghị dùng đường dẫn gộp wildcard `spark.read.parquet("curated/runs/run_*/")` vì có thể đọc nhầm nhiều phiên bản lịch sử hoặc các đợt chạy thử nghiệm của cùng một năm. Thay thế bằng quy tắc bắt buộc nạp thông qua danh mục snapshot chính thức [`data/curated/snapshot_registry.json`](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/data/curated/snapshot_registry.json), đảm bảo đúng một đợt chạy được phê chuẩn duy nhất cho mỗi năm khảo sát.
2. **Mâu thuẫn B2 — Phân định rạch ròi Ngoại lệ G2-EXC-001 thuộc về FP-DEC-019 Option B (không phải FP-DEC-020):**
   * *Tài liệu hiệu chỉnh:* [`docs/05-evidence/G6_T012_2016_PRESTART_REPORT.md`](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/docs/05-evidence/G6_T012_2016_PRESTART_REPORT.md) mục 1.
   * *Nội dung sửa đổi:* Làm rõ rằng Ngoại lệ `G2-EXC-001` (về đơn vị tính phút của 7 trường số đo CORE) được giải quyết thông qua việc phê duyệt chính sách đối soát BTS **`FP-DEC-019 Option B`** và chữ ký nghiệm thu TS-018 (Quyết định D3). Quyết định **`FP-DEC-020 Option B`** là quyết định kiến trúc chạy lại năm 2016 của Gate G6, hoàn toàn độc lập và không liên quan đến việc đóng ngoại lệ đơn vị đo của Gate G2.
3. **Mâu thuẫn B3 — Gate G5 không tự động chuyển trạng thái PASS:**
   * *Tài liệu hiệu chỉnh:* [`docs/05-evidence/G6_T012_2016_PRESTART_REPORT.md`](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/docs/05-evidence/G6_T012_2016_PRESTART_REPORT.md) mục 8.
   * *Nội dung sửa đổi:* Xóa bỏ khẳng định rằng việc hoàn tất D1 sẽ "tự động chuyển Gate G5 thành PASS". Làm rõ chuỗi chuyển giao có kiểm soát: Hoàn tất chứng thực người tải D1 là điều kiện tiên quyết cho phép Project Lead thực hiện việc ký duyệt kỹ thuật D3 (TS-018) và ký quyết định đóng cổng D4 (Gate G5). Gate G5 chỉ chính thức PASS khi Project Lead ký quyết định D4.

---

## 2. KẾT QUẢ KIỂM THỬ MỤC TIÊU VÀ MÃ THOÁT THỰC TẾ (TARGETED TEST RESULTS)

### 2.1. Kiểm thử hồi quy an toàn bộ chạy tiền khởi động (`tests/test_prestart_checks_safety.py`)
Đã xây dựng bộ kiểm thử hồi quy độc lập để kiểm chứng các cải tiến an toàn:
* **Lệnh chạy:** `$env:PYTHONPATH="src"; python -m unittest tests/test_prestart_checks_safety.py`
* **Thời gian thực thi:** 5.318s
* **Mã thoát (Exit Code):** `0` (`Ran 3 tests in 5.318s, OK`)
* **Chi tiết các kịch bản kiểm thử:**
  1. `test_01_source_integrity_missing_file_fails`: Khi tệp CSV 2016 bị thiếu, `evaluate_source_integrity` trả về `valid=False`, bước kiểm tra tệp nguồn ghi nhận `Exit Code: 1`, và toàn bộ script trả về mã lỗi `1` (`PRESTART OVERALL VERDICT: FAIL`).
  2. `test_02_source_integrity_size_mismatch_fails`: Khi tệp CSV 2016 có kích thước byte sai lệch, hàm trả về `valid=False` và toàn bộ script trả về mã lỗi `1`.
  3. `test_03_no_live_coordinator_invocation_in_runner`: Phân tích cú pháp AST toàn bộ mã nguồn của `run_g6_t012_prestart_checks.py`, khẳng định 100% không tồn tại bất kỳ lệnh gọi subprocess nào đến `coordinator.py` mà thiếu cờ `--dry-run-preflight`.

### 2.2. Kiểm thử chạy thực tế bộ kiểm tra tiền khởi động cập nhật (`tools/qa/run_g6_t012_prestart_checks.py`)
* **Lệnh chạy:** `python tools/qa/run_g6_t012_prestart_checks.py --allow-resource-hold`
* **Mã thoát (Exit Code):** `0`
* **Kết quả từng bước:**
  * Bước 1 (Git Status): Exit Code `0` (Nhánh `master`, commit `bc4f03fb...`).
  * Bước 2 (Canonical 2016 RAW Inspection): Exit Code `0` (`1,538,427,452` bytes, SHA-256 `4ed92ed7...`, `EXACT_MATCH`).
  * Bước 3 (Workstation Resource Audit): Exit Code `0` (Ổ D: trống 56.83 GiB, RAM khả dụng 4.04 GiB).
  * Bước 4 (Standalone Writer Preflight Safety): Exit Code `0` (`SAFE_TO_PROCEED_TO_LOCK_ACQUISITION`).
  * Bước 5 (Staging Pointer Audit): Exit Code `0` (`UNINITIALIZED_POINTER_ALLOWED`).
  * Bước 6 (Ingestion Coordinator Safe Dry-Run): Exit Code `0` (`[PREFLIGHT PASS] All mandatory safety criteria PASSED. No data written`).
  * Bước 7 (Safe Governance Hold Verification): Exit Code `0` (Kiểm tra tĩnh `D5_AUTHORIZED_BY_PROJECT_LEAD = False` + Unit test mock exit code `0`).
  * Bước 8 (Single-Run Validator Interface): Exit Code `0`.
* **Kết luận:** Toàn bộ 8 bước kiểm tra an toàn đều đạt tiêu chuẩn kỹ thuật nghiêm ngặt.

---

## 3. TRẠNG THÁI QUẢN TRỊ CHÍNH THỨC D1–D4 VÀ ĐỐI SOÁT BTS

### 3.1. Đối soát Chứng thực Nguồn gốc BTS (Quyết định D1)
* **Tệp lưu trữ đối chứng vật lý:** [`data/reference/bts_transtats/original/T_ONTIME_REPORTING_20261019_112232.zip`](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/data/reference/bts_transtats/original/T_ONTIME_REPORTING_20261019_112232.zip)
* **Kích thước byte:** `29,975,383 bytes` (Khớp tuyệt đối mốc kiểm toán).
* **Mã băm SHA-256:** `342de99f65561fb856b524c704f2ad3851f8015f52251668ece346dff1350ae6` (Khớp tuyệt đối mốc kiểm toán).
* **Tuyên bố con người thực tế (Human Downloader Attestation):**  
  Tại phiên làm việc ngày 2026-10-21, Project Lead đã chính thức cung cấp lời xác nhận bằng văn bản:
  > *"tôi đã tải bộ hồ sơ BTS"*
* **Ghi nhận trạng thái:** Tuyên bố con người của Project Lead đã được hợp nhất chính thức vào tài liệu [`docs/05-evidence/G5_D1_BTS_PROVENANCE_ATTESTATION_DRAFT.md`](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/docs/05-evidence/G5_D1_BTS_PROVENANCE_ATTESTATION_DRAFT.md).
* **Trạng thái Quyết định D1:** **`PASS (ATTESTED_BY_PROJECT_LEAD_STATEMENT)`**.

### 3.2. Bảng tổng hợp trạng thái các quyết định D1–D5

| Quyết định | Tên hạng mục | Trạng thái kỹ thuật | Trạng thái quản trị chính thức | Ghi chú & Căn cứ phê duyệt |
| :--- | :--- | :---: | :---: | :--- |
| **D1** | BTS Source Provenance Attestation | `BITWISE_VERIFIED` | **`PASS`** | Đạt đối soát SHA-256 + Lời chứng thực của Project Lead: *"tôi đã tải bộ hồ sơ BTS"*. |
| **D2** | TS-018 BTS Parity Scope (Option B) | `100% BITWISE EXACT` | **`APPROVED_WITH_CONDITIONS`** | Phê duyệt chính thức thành [`FP-DEC-019`](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/docs/02-design/DECISIONS.md) ngày 21/10/2026. Giới hạn 7 trường số đo. |
| **D3** | TS-018 Human Technical Signoff | `10,500/10,500 EXACT` | **`READY_FOR_OFFICIAL_HUMAN_SIGNOFF`** | 100% tiêu chí kỹ thuật đạt, D1 đã có chứng thực nguồn. Chờ Project Lead xác nhận đóng D3. |
| **D4** | Gate G5 Human Gate Signoff | `19/19 EXIT CRITERIA MET` | **`READY_FOR_FINAL_HUMAN_GATE_SIGNOFF`** | Hồ sơ nghiệm thu G5 hoàn tất, chờ Project Lead ký lệnh đóng Gate G5. |
| **G6-ARCH-2016** | Phương án tái nạp 2016 (Option B) | `ARCHITECTURE_APPROVED` | **`APPROVED_BY_PROJECT_LEAD_INSTRUCTION`** | Phê duyệt chính thức thành [`FP-DEC-020`](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/docs/02-design/DECISIONS.md) ngày 21/10/2026. |
| **D5** | Production Execution Authorization | `FAIL_CLOSED_BLOCKED` | **`NOT_AUTHORIZED`** | Nghiêm cấm chạy Spark live; chốt chặn mã nguồn đang khóa 100%. |

---

## 4. TRẠNG THÁI CHÍNH THỨC CỦA CỔNG QUẢN LÝ GATE G5

* **Trạng thái kỹ thuật:** **`19/19 EXIT CRITERIA MET (TECHNICALLY READY)`**.
* **Trạng thái quản trị:** **`READY_FOR_G5_HUMAN_CLOSEOUT`**.
* Toàn bộ các yêu cầu kỹ thuật, tài liệu thiết kế, bài kiểm tra âm tính (negative tests), kiểm tra tính toàn vẹn tệp nguồn và tính xác thực của tệp đối chứng BTS đã hoàn tất đầy đủ.
* Gate G5 đang ở trạng thái sẵn sàng cao nhất để Project Lead thực hiện việc ký nghiệm thu đóng cổng chính thức.

---

## 5. TRẠNG THÁI CỦA QUYẾT ĐỊNH KIẾN TRÚC G6-ARCH-2016

* **Mã đăng ký chính thức:** [`FP-DEC-020`](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/docs/02-design/DECISIONS.md) trong Sổ đăng ký Quyết định (`docs/02-design/DECISIONS.md`).
* **Trạng thái:** **`APPROVED_BY_PROJECT_LEAD_INSTRUCTION`** (Chỉ thị ngày 2026-10-21: *"tôi hoàn toàn đồng ý với ý kiến của bạn"*).
* **Phương án lựa chọn:** **Option B (Unified Production Rerun of 2016)**. Năm 2016 sẽ được nạp như một run sản xuất chuẩn hóa (`run_2016_v1`) tạo đầy đủ `run_manifest.json` và `execution_receipt.json`.
* **Bảo tồn tài sản:** 50 tệp staging Parquet 2016 của T-010 tại `D:\Study\Code\Apache\Flight_Analyzt\staging\` được bảo vệ nguyên vẹn 100% làm bằng chứng lịch sử.
* **Ranh giới:** Quyết định kiến trúc này **tuyệt đối không tương đương với quyền chạy dữ liệu thật D5**.

---

## 6. HÀNH ĐỘNG CON NGƯỜI CHÍNH XÁC CÒN LẠI (REMAINING HUMAN ACTIONS)

Để hoàn tất trọn vẹn Gate G5 và tiến tới Gate G6 / Task T-012, Project Lead chỉ cần thực hiện 3 hành động quản trị tuần tự sau:

1. **Hành động 1 (Ký đóng Gate G5):**  
   Project Lead xác nhận việc đóng chính thức Quyết định D3 (TS-018) và Quyết định D4 (Gate G5).
   *Hành động này sẽ chính thức khép lại Gate G5 với phán quyết `G5 = PASS (CONTROLLED)`, giải quyết dứt điểm Ngoại lệ `G2-EXC-001` sang trạng thái `RESOLVED_BY_OPTION_B`, đóng hợp đồng T-011, và mở khóa cổng quản trị Gate G6.*
2. **Hành động 2 (Chuẩn bị môi trường vận hành):**  
   Người vận hành đóng bớt các ứng dụng nền không cần thiết (trình duyệt web, ứng dụng ngốn RAM) để bảo đảm duy trì dung lượng RAM khả dụng ở mức khuyến nghị $\ge 4.0\text{ GiB}$.
3. **Hành động 3 (Cấp phép Quyết định D5 & Kích hoạt có kiểm duyệt):**  
   Sau khi Gate G6 được mở, Project Lead ban hành Quyết định D5 (Cấp phép nạp dữ liệu sản xuất năm 2016). Kỹ sư sẽ áp dụng bản vá kích hoạt 1 dòng mã nguồn được kiểm duyệt độc lập (`D5_AUTHORIZED_BY_PROJECT_LEAD = True`) để tiến hành mẻ chạy `run_2016_v1`.

---

## 7. KHUYẾN NGHỊ VẬN HÀNH TIẾP CẬN D5 VÀ LÀM RÕ SỐ ĐO RAM LỊCH SỬ

### 7.1. Làm rõ chênh lệch số đo RAM lịch sử (Historical RAM Discrepancy Reconciliation)
* Trong báo cáo trước, có sự khác biệt giữa con số **3.57 GiB** trong nhật ký lệnh thô và con số **3.24 GiB** trong phần tóm tắt báo cáo.
* **Nguyên nhân kỹ thuật:** Đây là sự khác biệt về thời điểm đo đạc thực tế của hệ điều hành Windows:
  - Thời điểm 09:15 UTC (khảo sát sơ bộ bằng lệnh python ngắn): RAM khả dụng đo được là **3.24 GiB** (hệ thống đang sử dụng 79.4%).
  - Thời điểm 09:20 UTC (khi script tự động chạy đo đạc): RAM khả dụng đo được là **3.57 GiB** (hệ thống đang sử dụng 77.3%).
  - Thời điểm 09:54 UTC (phiên đo hiện tại): RAM khả dụng đo được là **4.04 GiB**.
* **Đánh giá quy chuẩn:** Cả 3 số đo lịch sử đều vượt qua ngưỡng cứng tối thiểu của chính sách ($\ge 3.0\text{ GiB}$). Khuyến nghị đóng các ứng dụng nặng để duy trì ổn định $\ge 4.0\text{ GiB}$ trước khi chạy Spark live là hoàn toàn hợp lý và mang tính phòng ngừa rủi ro OOM cao.

### 7.2. Ghi nhận Phiên bản Mã nguồn Git (Working Tree & Commit Versioning)
* **Commit HEAD hiện tại:** `bc4f03fb8ccd6c0b2455af3fcb2b1b98fa39d632` trên nhánh `master`.
* Toàn bộ các thay đổi trong phiên làm việc này chỉ bao gồm:
  1. Bản sửa đổi an toàn cho runner: `tools/qa/run_g6_t012_prestart_checks.py`.
  2. Bộ kiểm thử hồi quy mới: `tests/test_prestart_checks_safety.py`.
  3. Cập nhật tài liệu đối soát và quyết định: `G5_D1_BTS_PROVENANCE_ATTESTATION_DRAFT.md`, `G6_T012_2016_BASELINE_INTEGRATION_DECISION_DRAFT.md`, `G6_T012_2016_PRESTART_REPORT.md`.
  4. Báo cáo đối soát tổng thể: `G5_G6_FINAL_ALIGNMENT_REPORT.md`.

---

## 8. HỒ SƠ LƯU TRỮ VÀ BẰNG CHỨNG KIỂM TOÁN (REVIEW ZIP & MANIFEST)

Gói hồ sơ nghiệm thu kỹ thuật và quản trị Task `G5-G6-FINAL-ALIGNMENT` đã được đóng gói và kiểm toán mã băm:

* **Tệp nén hồ sơ nghiệm thu:**
  * Đường dẫn: [`docs/05-evidence/G5_G6_FINAL_ALIGNMENT_REVIEW.zip`](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/docs/05-evidence/G5_G6_FINAL_ALIGNMENT_REVIEW.zip) *(Bản sao tại gốc repo và thư mục cha)*
* **Tệp kê khai chi tiết (Manifest):**
  * Đường dẫn: [`docs/05-evidence/G5_G6_FINAL_ALIGNMENT_REVIEW_MANIFEST.json`](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/docs/05-evidence/G5_G6_FINAL_ALIGNMENT_REVIEW_MANIFEST.json)

---

## 9. PHÁN QUYẾT CUỐI CÙNG (FINAL VERDICT)

$$\mathbf{VERDICT:}\quad \mathbf{READY\_FOR\_G5\_HUMAN\_CLOSEOUT}$$

*(Toàn bộ các vướng mắc kỹ thuật, an toàn bộ chạy tiền khởi động và mâu thuẫn tài liệu đã được khắc phục 100%; lời chứng thực nguồn BTS của Project Lead đã được hợp nhất; Gate G5 đã hoàn tất toàn bộ điều kiện kỹ thuật và sẵn sàng chờ Project Lead ban hành lệnh đóng cổng chính thức).*
