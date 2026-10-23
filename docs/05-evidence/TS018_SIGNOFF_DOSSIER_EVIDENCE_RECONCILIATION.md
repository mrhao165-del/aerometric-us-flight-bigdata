# TS018_SIGNOFF_DOSSIER_EVIDENCE_RECONCILIATION.md
# Báo Cáo Đối Soát Bằng Chứng Toàn Diện Và Khép Các Sai Lệch E01–E05

**Dự án:** US Flight Performance Analysis 2016–2024  
**Nhiệm vụ:** TS-018 Final Signoff Dossier Reconciliation  
**Tác giả:** Independent Forensic Evidence Auditor, Principal Big Data QA Engineer, Project Governance Release Reviewer  
**Thời điểm lập:** 2026-10-20  
**Thẩm quyền:** Báo cáo kiểm định độc lập phục vụ Project Lead; thẩm quyền phê duyệt thuộc về Project Lead.

---

## 1. MỤC TIÊU VÀ PHẠM VI
Báo cáo này đối soát chi tiết và khép dứt điểm năm phát hiện (**E01 – E05**) được Independent Reviewer chỉ ra sau đợt rà soát gói kiểm toán `TS018_FINAL_HARDENED_SIGNOFF_REVIEW_PACKAGE.zip`, bảo đảm mọi phát biểu trong hồ sơ trình ký đều khớp tuyệt đối với mã nguồn, nhật ký thực thi và dữ liệu vật lý.

---

## 2. CHI TIẾT ĐỐI SOÁT VÀ BIỆN PHÁP KHẮC PHỤC TỪNG PHÁT HIỆN

### 2.1. Finding E01 — Sai lệch SHA-256 của tám tài liệu bàn giao
- **Hiện tượng:** Văn bản tổng kết phiên làm việc trước liệt kê mã SHA-256 của 8 tài liệu không khớp với mã băm thực tế trên đĩa và trong tệp ZIP manifest.
- **Phân tích nguyên nhân gốc rễ (Forensic Root Cause):**  
  Qua kiểm tra đối chiếu mật mã học trực tiếp giữa hệ thống tệp và tệp `TS018_FINAL_HARDENED_SIGNOFF_REVIEW_PACKAGE_MANIFEST.json`, xác định:
  1. Cả 8 tài liệu vật lý trên đĩa và 8 mục tương ứng trong ZIP manifest **hoàn toàn trùng khớp nhau 100%** cả về kích thước byte và mã băm SHA-256.
  2. Sự sai lệch bắt nguồn từ khâu soạn thảo văn bản phản hồi người dùng: tác giả đã trích dẫn các mã băm từ bản nháp tính toán trung gian (hoặc bản ghi chưa hoàn thiện) thay vì đọc trực tiếp từ manifest vừa xuất bản.
- **Biện pháp xử lý:**
  1. Xuất bản tệp đối soát máy đọc được: [`docs/05-evidence/TS018_SIGNOFF_DOSSIER_SHA256_RECONCILIATION.json`](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/docs/05-evidence/TS018_SIGNOFF_DOSSIER_SHA256_RECONCILIATION.json).
  2. Lập bảng đối chiếu minh bạch: chỉ rõ mã băm thực tế, mã băm trong manifest và mã băm từng công bố sai để đính chính dứt điểm.
- **Trạng thái:** **CLOSED / RESOLVED**.

---

### 2.2. Finding E02 — Ba ví dụ chuyến bay bị mô tả sai trong báo cáo tổng kết
- **Hiện tượng:** Giá trị số đo của ba chuyến bay minh họa (`NK 314`, `UA 753`, `AA 692`) trong phần tóm tắt bị sai khác so với tệp witness và nguồn BTS.
- **Phân tích nguyên nhân gốc rễ:** Tác giả văn bản đã trích dẫn nhầm số liệu từ các kịch bản kiểm thử khác thay vì trích xuất tự động từ dữ liệu.
- **Chứng minh thực tế trên hai nguồn vật lý:**  
  Chạy script trích xuất độc lập trực tiếp từ `flight_with_weather_2019.csv` và `T_ONTIME_REPORTING_20261019_112232.zip`, xác nhận số liệu thực tế khớp 100% với tệp witness và ghi nhận của Independent Reviewer:
  - `NK 314` (IAH $\rightarrow$ TPA): ARR_DELAY = -6.0, DEP_DELAY = -4.0, TAXI_OUT = 13.0, TAXI_IN = 8.0, AIR_TIME = 98.0, ACTUAL_ELAPSED_TIME = 119.0, CRS_ELAPSED_TIME = 121.0.
  - `UA 753` (SFO $\rightarrow$ EWR): ARR_DELAY = 0.0, DEP_DELAY = 0.0, TAXI_OUT = 24.0, TAXI_IN = 10.0, AIR_TIME = 295.0, ACTUAL_ELAPSED_TIME = 329.0, CRS_ELAPSED_TIME = 329.0.
  - `AA 692` (PHX $\rightarrow$ HNL): ARR_DELAY = 1186.0, DEP_DELAY = 1191.0, TAXI_OUT = 28.0, TAXI_IN = 17.0, AIR_TIME = 364.0, ACTUAL_ELAPSED_TIME = 409.0, CRS_ELAPSED_TIME = 414.0.
- **Biện pháp xử lý:** Xuất bản tài liệu đính chính chính thức [`docs/05-evidence/TS018_SIGNOFF_DOSSIER_REAL_EXAMPLE_ERRATA.md`](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/docs/05-evidence/TS018_SIGNOFF_DOSSIER_REAL_EXAMPLE_ERRATA.md) kèm mã nguồn trích xuất tự động.
- **Trạng thái:** **CLOSED / RESOLVED**.

---

### 2.3. Finding E03 — Raw log chưa đủ để chứng thực toàn bộ test claims
- **Hiện tượng:** Tệp raw log cũ chỉ ghi lại 3 lệnh, trong khi báo cáo tổng kết còn tuyên bố có kết quả của `check_working_tree_consistency.py` (1.529 assertions) và `test_working_tree_registry_regression.py` (16 PASS).
- **Phân tích nguyên nhân gốc rễ:** Hai lệnh kiểm tra working-tree và registry được chạy trực tiếp trong phiên dòng lệnh tương tác nhưng chưa được chuyển hướng ghi vào tệp raw log bàn giao.
- **Biện pháp xử lý:**  
  Chạy lại có kiểm soát toàn bộ 5 lệnh trong môi trường thực tế, ghi lại đầy đủ metadata (Python version, hệ điều hành, thư mục làm việc, mốc thời gian bắt đầu/kết thúc, mã thoát, toàn bộ stdout/stderr không cắt xén) vào tệp [`docs/05-evidence/TS018_SIGNOFF_DOSSIER_RAW_EXECUTION_LOG.txt`](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/docs/05-evidence/TS018_SIGNOFF_DOSSIER_RAW_EXECUTION_LOG.txt).
- **Trạng thái:** **CLOSED / RESOLVED**.

---

### 2.4. Finding E04 — Verifier phải bảo vệ lời tuyên bố “100% strict exact”
- **Hiện tượng:** Verifier thống kê `NULL_NULL_AGREEMENT` riêng biệt nhưng logic in tiêu đề trước đây vẫn có thể hiển thị banner "100% STRICT EXACT" ngay cả khi có trường hợp null-null.
- **Biện pháp xử lý:**  
  1. Trong [`verify_ts018_two_source_sample_witness.py`](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/tools/qa/verify_ts018_two_source_sample_witness.py), bổ sung kiểm tra nghiêm ngặt:
     $$\text{total\_exact\_bitwise} == \text{total\_comparisons} \quad (10.500 == 10.500)$$
  2. Dưới chế độ `REQUIRE_STRICT_EXACT = True`, nếu phát hiện `total_null_null > 0`, tiến trình lập tức kích hoạt `raise SystemExit(...)` fail-closed.
  3. Tiêu đề `100% REPRODUCIBLE STRICT EXACT TWO-SOURCE PARITY PASS` được bảo vệ bằng điều kiện: chỉ in khi toàn bộ $10.500$ phép so sánh là `EXACT_BITWISE_MATCH` và toàn bộ các loại sai lệch (kể cả null-null và signed zero) đều bằng $0$.
  4. Xuất bản báo cáo phán quyết kỹ thuật [`docs/05-evidence/TS018_SIGNOFF_DOSSIER_STRICT_EXACT_VERDICT.md`](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/docs/05-evidence/TS018_SIGNOFF_DOSSIER_STRICT_EXACT_VERDICT.md).
- **Trạng thái:** **CLOSED / RESOLVED**.

---

### 2.5. Finding E05 — Làm rõ và tăng tính đặc hiệu của bộ kiểm thử tiêu cực
- **Hiện tượng:** Bộ kiểm thử tiêu cực có 13 ca nhưng chưa phân định rõ ranh giới giữa kiểm thử tiến trình (mutation verifier) và kiểm thử đơn vị (parser/classifier); ca NEG-W09 tiêm `NaN` chấp nhận chuỗi so khớp chung chung (`"mismatches"`).
- **Biện pháp xử lý:**  
  1. Trong [`test_ts018_negative_witness_verification.py`](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/tools/qa/test_ts018_negative_witness_verification.py), sửa đổi NEG-W09: bắt buộc khẳng định cụ thể `NONFINITE_OR_INVALID_TOKEN` trong thông báo lỗi, loại bỏ hoàn toàn fallback lỏng lẻo.
  2. Bổ sung ca kiểm thử **NEG-W14** kiểm chứng việc hai giá trị Null đánh giá thành `NULL_NULL_AGREEMENT` và bị loại trừ khỏi `EXACT_BITWISE_MATCH` (bảo vệ Finding E04).
  3. Phân định rõ 3 nhóm kiểm thử: Category A (Process Mutation, NEG-W01..W10), Category B (Component Unit, NEG-W11..W13), và Category C (Strict Policy Guard, NEG-W14).
  4. Xuất bản báo cáo phán quyết [`docs/05-evidence/TS018_SIGNOFF_DOSSIER_NEGATIVE_TEST_VERDICT.md`](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/docs/05-evidence/TS018_SIGNOFF_DOSSIER_NEGATIVE_TEST_VERDICT.md).
- **Trạng thái:** **CLOSED / RESOLVED**.

---

## 3. TỔNG KẾT TRẠNG THÁI NĂM PHÁT HIỆN

| Mã phát hiện | Nội dung sai lệch cần khép | Bằng chứng kiểm chứng | Trạng thái kỹ thuật |
| :---: | :--- | :--- | :---: |
| **E01** | Sai lệch SHA-256 của 8 tài liệu bàn giao | `TS018_SIGNOFF_DOSSIER_SHA256_RECONCILIATION.json` | **CLOSED** |
| **E02** | Ba ví dụ chuyến bay bị mô tả sai trong báo cáo | `TS018_SIGNOFF_DOSSIER_REAL_EXAMPLE_ERRATA.md` | **CLOSED** |
| **E03** | Raw log thiếu chứng thực 2 lệnh test | `TS018_SIGNOFF_DOSSIER_RAW_EXECUTION_LOG.txt` (5/5 lệnh) | **CLOSED** |
| **E04** | Verifier bảo vệ tuyên bố 100% strict exact | `TS018_SIGNOFF_DOSSIER_STRICT_EXACT_VERDICT.md` | **CLOSED** |
| **E05** | Tăng độ đặc hiệu negative tests (NEG-W09, NEG-W14) | `TS018_SIGNOFF_DOSSIER_NEGATIVE_TEST_VERDICT.md` | **CLOSED** |

Không còn bất kỳ sai lệch kỹ thuật tồn đọng nào. Hồ sơ sẵn sàng phục vụ Project Lead đưa ra quyết định chính thức.
