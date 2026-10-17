# T009_SIGNOFF_AUTHORIZATION_RECORD — Biên bản Ghi nhận Phê duyệt Nghiệm thu T-009 của Project Lead

**Mã tài liệu:** `T009-SIGNOFF-AUTH-REC-20261017`  
**Dự án:** US Flight Performance Analysis 2016–2024 using Apache Spark / PySpark  
**Nhiệm vụ:** `T-009` (Python/PySpark Infrastructure, SafePublisher, Test Runner & Manifest Baseline)  
**Gate chủ quản:** `G4`  
**Chế độ thực thi:** `AUTHORIZED_HUMAN_DECISION_RECORDING_AND_CONTROLLED_REPOSITORY_UPDATE`  
**Ngày quyết định phê duyệt (Decision Date):** `2026-10-17`  
**Thời điểm Agent ghi nhận (System Recording Timestamp):** `2026-10-17T12:42:00+07:00`  
**Cơ quan có thẩm quyền phê duyệt (Approving Authority):** Project Lead (Human)  
**Chủ thể ghi nhận (Recording Actor):** AI Coding Assistant (Antigravity) — Chỉ ghi nhận quyết định có thẩm quyền, không tự phê duyệt  
**Trạng thái chứng thực (Authentication Status):** `HUMAN_APPROVAL_RECEIVED — FORMAL_AUTHENTICATION_PENDING` (Ghi nhận chỉ thị phê duyệt trực tiếp của Project Lead; không giả mạo chữ ký tay vật lý hay chứng thư số khi chưa có thủ tục PKI)

---

## 1. Căn cứ và Bằng chứng Phê duyệt Trực tiếp của Project Lead

Trong phiên đối thoại làm việc trực tiếp, Human Project Lead đã đưa ra chỉ thị tường minh bằng văn bản:

> **"tôi duyệt bạn hãy tạo promt để thực hiện việc tiếp theo"**

### 1.1. Ngữ cảnh phê duyệt
Chỉ thị trên là phản hồi trực tiếp đối với đề xuất nghiệm thu chính thức của gói hoàn tất T-009:
- Đề xuất trạng thái: **`TASK_T009 = PASS` có kiểm soát (`acceptance_mode = CONTROLLED`)**.
- Bảo lưu 5 giới hạn kỹ thuật không chặn (`L-T009-01` đến `L-T009-05`).
- Bảo lưu toàn bộ các điều kiện và ngoại lệ quản trị (`G2-EXC-001`, `OR-05`, `OR-08`, `FP-DEC-017`, `G3-COND-A/B/C`).
- Git HEAD được đánh giá: [`2a7eb160d8e198354586427ccfd9060ad3ec613f`](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1)
- Gói đánh giá niêm phong: `T009_CI_TEST_CLOSURE_PACKAGE.zip` (SHA-256: `62c5292316b8aa3e5d7c25b7f7a2857e1090eceb247d5d19706256791f23d344`, 89 tệp).

### 1.2. Tính hợp lệ của quyết định
Đây là quyết định phê duyệt hợp lệ của con người có thẩm quyền cao nhất trong dự án (Human Project Lead). AI Agent đóng vai trò thư ký quản trị kho mã (Configuration Management & Repository Governance Agent), không tự ban hành phán quyết và không tự phê duyệt.

---

## 2. Ranh giới Quyền hạn và Phạm vi Hiệu lực của Quyết định

| Hạng mục | Trạng thái sau phê duyệt | Ranh giới & Giới hạn thẩm quyền |
|---|:---:|---|
| **Nhiệm vụ T-009** | **`PASS`** *(Controlled)* | Đã hoàn thành toàn bộ yêu cầu kỹ thuật nền tảng PySpark, SafePublisher Windows NTFS atomic, test suite 37 tests PASS, 4 spark env tests PASS, bộ kiểm chuẩn hợp đồng T-006 17 invariants + 16 mutations PASS. |
| **Nhiệm vụ T-007** | **`NOT_STARTED (DESIGN AUTHORIZED)`** | **Được phép chuẩn bị nghiên cứu và thiết kế**. Tuyệt đối **CẤM** tự ý viết mã nguồn thực thi (`src/flight_pipeline/ingestion.py`), nạp CSV hay thay đổi dữ liệu trước khi có prompt/chỉ thị riêng. |
| **Nhiệm vụ T-008** | **`NOT_STARTED`** | Nghiêm ngặt giữ nguyên trạng thái chưa bắt đầu. |
| **Gate G4** | **`PLANNED / NOT_COMPLETED`** | **CHƯA ĐÓNG**. Gate G4 chỉ được nghiệm thu sau khi cả `T-007` và `T-008` hoàn thành và được kiểm toán đầy đủ. |
| **Gate G5 & G6** | **`NOT_STARTED / NOT_SIGNED_OFF`** | Toàn bộ nghĩa vụ chạy PySpark trên dữ liệu thật và đối chiếu BTS giữ nguyên ở Gate G5/G6. |
| **Gate G2 & G3** | **`PASS`** *(Immutable)* | Giữ nguyên trạng thái phê duyệt lịch sử, không thay đổi. |

---

## 3. Danh mục 5 Giới hạn Kỹ thuật Không chặn Được Chấp thuận (`L-T009-01..05`)

Human Project Lead chấp thuận nghiệm thu T-009 đồng thời bảo lưu 5 giới hạn kỹ thuật đã được công bố minh bạch:

1. **`L-T009-01` — Linux Runtime Execution Boundary (`POSIX_FULL_SUITE_NOT_EXECUTED`):**
   - Bài test kiểm tra script bootstrap (`tests/test_spark_env.py`) đã được sửa và tách biệt trên POSIX (`test_spark_script_invocable_posix`).
   - Môi trường cục bộ Windows đã thực thi thành công 100% test suite.
   - Chưa có lượt thực thi toàn diện PySpark pipeline trên hạ tầng GitHub Actions Linux / POSIX remote thực tế. Giới hạn này được chấp nhận và sẽ theo dõi qua CI workflow.
2. **`L-T009-02` — SafePublisher Single-Writer Operational Constraint:**
   - Cơ chế xuất bản nguyên tử Windows NTFS qua `SafePublisher` được thiết kế an toàn cho một tiến trình ghi độc lập (Single-Writer).
   - Nhiệm vụ `T-007` và các pipeline tiếp theo phải bảo đảm điều phối tiến trình (process coordination/concurrency control) trước khi tích hợp vào pipeline sản xuất.
3. **`L-T009-03` — Parquet Validation Boundary:**
   - Cơ chế kiểm thử hợp lệ Parquet tại T-009 xác minh magic bytes (`PAR1`), cấu trúc Thrift footer metadata và đối chiếu SHA-256 bản sao.
   - Cơ chế này không thay thế việc kiểm chứng nghiệp vụ dữ liệu trên 54.7 triệu hàng. Việc kiểm chứng hợp đồng dữ liệu thuộc trách nhiệm của `T-007` và `T-008`.
4. **`L-T009-04` — Benign Windows Local Spark Warnings:**
   - Các cảnh báo cục bộ trên Windows (`winutils.exe`, `NativeCodeLoader`, `SparkConf`, Py4J `ResourceWarning`) xuất hiện trong log do đặc thù môi trường Windows nhưng không làm thất bại các bài kiểm thử.
   - Không tuyên bố tuyệt đối không có cảnh báo tài nguyên; runtime Spark đáp ứng đầy đủ tiêu chí chấp nhận của T-009.
5. **`L-T009-05` — Full-scale Testing Obligations Deferred to G5/G6:**
   - Các bài kiểm thử quy mô lớn toàn bộ dataset, tiêm lỗi hỏng đĩa đầy đủ `TS-013`, đo đạc tài nguyên `TS-014` và đối chiếu dữ liệu gốc BTS `TS-018` tiếp tục được phân định đúng các Gate G5 và G6.

---

## 4. Bảo lưu Toàn diện các Ràng buộc Quản trị Bất biến

Biên bản này tái khẳng định hiệu lực tối thượng của các điều kiện quản trị dự án:

1. **`G2-EXC-001` & `TS-018` (Mandatory Hard Stop at Gate G5):**
   - Đơn vị đo của đúng **7 trường số đo liên tục CORE** (`ARR_DELAY`, `DEP_DELAY`, `TAXI_OUT`, `TAXI_IN`, `AIR_TIME`, `ACTUAL_ELAPSED_TIME`, `CRS_ELAPSED_TIME`; không gồm `ELAPSED_DIFF`) tiếp tục mang nhãn **`OFFICIAL_MINUTES_EMPIRICALLY_CONSISTENT_PROVISIONAL`**.
   - Bắt buộc kiểm thử `TS-018` đối chiếu trực tiếp mẫu số liệu BTS TranStats phải đạt `PASS` tại Gate G5 trước khi mở Gate G6. Nếu `TS-018` thất bại, toàn bộ Gate G6 bị CHẶN (`BLOCKED`).
2. **`OR-05 = OPEN_QUALITY_DEFECT`:**
   - Dữ liệu năm 2024 khuyết toàn bộ 31 ngày Tháng 3/2024 (chỉ có `335/366` ngày).
   - Cấm bịa đặt dữ liệu bù đắp, cấm nội suy âm thầm, cấm gọi 2024 là đủ 366 ngày.
3. **`OR-08 = IDENTITY_UNVERIFIED`:**
   - Mã băm SHA-256 của 9 file CSV thô chỉ chứng minh tính toàn vẹn so với snapshot đã kiểm toán (`METADATA_MATCH_ONLY`), không tự chứng minh nguồn gốc ban đầu từ BTS.
4. **`FP-DEC-017` (Weather CONDITIONAL_NO_GO):**
   - Nhánh thời tiết giữ nguyên trạng thái `CONDITIONAL_NO_GO`, 6 cột thời tiết giữ nguyên trong raw schema 34 cột (`DC-07`), không suy diễn nhân quả thời tiết đối với độ trễ.
5. **`G3-COND-A/B/C`:**
   - `G3-COND-A`: Chính sách quarantine là đề xuất sơ bộ, không tự tiện quarantine bản ghi hợp lệ.
   - `G3-COND-B`: Vị từ số học hữu hạn (`is_finite_numeric`) tiếp tục được kiểm chứng ở các bước tiếp theo.
   - `G3-COND-C`: Xuất bản an toàn Windows NTFS và kiểm thử tiêm lỗi `TS-013` thuộc Gate G5.

---

## 5. Kết luận & Phê chuẩn Lưu trữ

1. Quyết định phê duyệt của Project Lead đối với **Nhiệm vụ `T-009`** chính thức có hiệu lực kể từ ngày **2026-10-17**.
2. Hồ sơ này được lưu trữ vĩnh viễn tại [`docs/05-evidence/T009_SIGNOFF_AUTHORIZATION_RECORD.md`](T009_SIGNOFF_AUTHORIZATION_RECORD.md) và đăng ký vào [`docs/05-evidence/EVIDENCE_DELIVERABLE_REGISTER.json`](EVIDENCE_DELIVERABLE_REGISTER.json).
3. Kho mã sẵn sàng bước vào giai đoạn chuẩn bị thiết kế cho Nhiệm vụ `T-007` theo đúng quy trình kiểm soát thay đổi.
