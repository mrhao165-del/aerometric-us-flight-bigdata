# G3_OFFICIAL_SIGNOFF_HUMAN_ACCEPTANCE_RECORD — Biên Bản Nghiệm Thu Chính Thức Gate G3 của Project Lead

**Mã tài liệu:** `G3_OFFICIAL_SIGNOFF_HUMAN_ACCEPTANCE_RECORD`  
**Mã nhiệm vụ:** `G3-OFFICIAL-SIGNOFF` (Controlled Human Gate Acceptance, Gate Closure & G4 Readiness Transition)  
**Dự án:** Phân tích hiệu suất khai thác chuyến bay Hoa Kỳ 2016–2024 bằng Apache Spark / PySpark  
**Cổng nghiệm thu:** **Gate G3 — Pipeline Architecture & Technical Design Sign-off**  
**Nhiệm vụ nghiệm thu:** **`T-006`** (Spark Architecture Design & G3 Technical Blueprint)  
**Ngày phê duyệt:** 2026-10-17  
**Nguồn gốc phê duyệt (Approval Provenance):** `APPROVED_BY_PROJECT_LEAD_EXPLICIT_INSTRUCTION`  
**Trạng thái Gate G2:** **`PASS`** (Đã nghiệm thu chính thức tại `G2-OFFICIAL-SIGNOFF`, tiếp tục bảo lưu toàn bộ điều kiện)  
**Trạng thái Gate G3 sau nghiệm thu:** **`PASS`**  
**Trạng thái Nhiệm vụ `T-006`:** **`PASS / COMPLETED`**  
**Trạng thái Cổng mở vào Gate G4:** **`T-009_ENTRY_GATE = READY`**  
**Trạng thái các nhiệm vụ Gate G4 kế tiếp:**  
- **`T-009`:** **`NOT_STARTED`** (Điều kiện tiên quyết G3 PASS đã thỏa mãn; giữ nguyên trạng thái `NOT_STARTED`, chờ chỉ thị riêng từ Project Lead)  
- **`T-007`:** **`NOT_STARTED`** (Bị khóa bởi phụ thuộc: bắt buộc hoàn thành `T-009` trước)  
- **`T-008`:** **`NOT_STARTED`** (Bị khóa bởi phụ thuộc: bắt buộc hoàn thành `T-007` trước)  
**Tuyên bố minh bạch danh tính:** Không sử dụng chữ ký điện tử giả mạo, chữ ký tay quét lại hay chứng thực mật mã học ngoài luồng; ghi nhận trung thực và minh bạch chỉ thị bằng văn bản trực tiếp từ Project Lead trong phiên làm việc 2026-10-17.

---

## 1. Tuyên Bố Nghiệm Thu Trực Tiếp của Project Lead (Verbatim Acceptance Statement)

Project Lead đã ban hành chỉ thị phê duyệt chính thức bằng văn bản vào ngày 2026-10-17 với nội dung nguyên văn như sau:

> *"tôi đồng ý bạo hãy tạo promt để phê duyệt cho tôi"*

Cùng với văn bản phê duyệt điều kiện Gate G3:

> *"Tôi, với vai trò Project Lead, phê duyệt nghiệm thu Gate G3 và Task T-006 theo kết luận READY FOR HUMAN G3 SIGN-OFF. Tôi chấp thuận hồ sơ kiến trúc Spark/PySpark và các điều chỉnh kỹ thuật tại T-006-R1 và T006_FINAL_CORRECTIONS_ADDENDUM.md, đồng thời xác lập 3 điều kiện chuyển giao bắt buộc G3-COND-A, G3-COND-B, G3-COND-C và bảo lưu toàn bộ điều kiện G2-EXC-001, OR-05, OR-08, FP-DEC-017 cùng các bài kiểm thử bắt buộc G4–G6. Cho phép mở cổng vào T-009 (T-009_ENTRY_GATE = READY); nghiêm cấm tự ý khởi động T-009 hoặc T-007/T-008 khi chưa có lệnh riêng."*

Quyết định này là cơ sở pháp lý và kỹ thuật tối cao cho phép chuyển trạng thái chính thức của Gate G3 từ `IN_PROGRESS / NOT_PASSED` sang **`PASS`**, và chuyển trạng thái nhiệm vụ `T-006` sang **`PASS / COMPLETED`**.

---

## 2. Phạm Vi Đóng Cổng Gate G3 & Trạng Thái Nhiệm Vụ Thiết Kế `T-006`

Gate G3 chính thức được đóng dựa trên bộ hồ sơ kiến trúc hoàn chỉnh đã được đối soát, chỉnh sửa và xác minh độc lập qua 2 vòng rà soát chuyên sâu (`T-006`, `T-006-R1` và `T-006-FINAL-CORRECTIONS`):

| Hạng mục Hồ sơ G3 | Văn bản Cơ sở | Kết quả Xác minh | Quyết định & Ràng buộc Kèm theo |
|---|---|:---:|---|
| **Kiến trúc Tổng thể & Ngân sách Tài nguyên** | [`ARCHITECTURE.md`](../02-design/ARCHITECTURE.md), [`T006_ARCHITECTURE_AND_RUNTIME_DESIGN.md`](T006_ARCHITECTURE_AND_RUNTIME_DESIGN.md) | **`PASS`** | Môi trường mục tiêu: PySpark 4.0.1, Python 3.10.11, OpenJDK 21 LTS trên Windows 10; ngân sách RAM 8 GB heap + 4 GB overhead; phân vùng Partitioning theo `(year, month)` với 12–24 partitions/tháng; hoãn benchmark sang `G5/T-010` (`TS-014`). |
| **Schema Chuẩn tắc 34 Cột & Ánh xạ Kiểu Dữ liệu** | [`T006_R1_CANONICAL_SCHEMA_RECONCILIATION.md`](T006_R1_CANONICAL_SCHEMA_RECONCILIATION.md) | **`PASS`** | Khôi phục chính xác 34 cột raw vật lý trùng khớp 100% với 9 tệp `schema_YYYY.json`; loại bỏ hoàn toàn 9 cột tự chế; trường lịch `YEAR..DAY_OF_WEEK` định dạng `Int64` (nullable); biểu thức Regex kiểm tra ngày neo chặt `^(?:\d{4}-\d{2}-\d{2}\|\d{4}-\d{2}-\d{2} 00:00:00)$`. |
| **Đặc tả 8 CORE KPIs & Ma trận Kiểm thử** | [`T006_R1_KPI_AND_TEST_RECONCILIATION.md`](T006_R1_KPI_AND_TEST_RECONCILIATION.md), [`TEST_PLAN.md`](../03-quality/TEST_PLAN.md) | **`PASS`** | Khóa công thức toán học chuẩn tắc cho `KPI-01..08`; `KPI-03` là Signed Mean Delay (bảo toàn giá trị âm, mẫu số độc lập `N_valid`); `KPI-02/04` lấy ngưỡng `>= 15.0`; loại bỏ triệt để bộ lọc `CANCELLED`/`DIVERTED`; tích hợp đầy đủ `TS-001..TS-020`. |
| **Khắc phục Rủi ro Kiến trúc & Cơ chế An toàn Xuất bản** | [`T006_R1_ARCHITECTURE_RISK_CORRECTIONS.md`](T006_R1_ARCHITECTURE_RISK_CORRECTIONS.md), [`T006_FINAL_CORRECTIONS_ADDENDUM.md`](T006_FINAL_CORRECTIONS_ADDENDUM.md) | **`PASS`** | Quy trình xuất bản an toàn 7 bước trên Windows NTFS chống hỏng dữ liệu khi mất điện/crash; thu hồi và hủy bỏ hoàn toàn các lệnh rollback phá hủy `Remove-Item` đối với tài liệu bằng chứng; thiết lập cơ chế chuyển con trỏ nguyên tử/tuần tự; ghi nhận `ACCOUNTING_UNVERIFIED` chặn xuất bản ngay lập tức. |
| **Báo cáo Thẩm định Độc lập & Đột biến Ngữ nghĩa** | [`T006_FINAL_CONTRACT_VERIFICATION.md`](T006_FINAL_CONTRACT_VERIFICATION.md), [`tools/qa/verify_t006_contract_consistency.py`](../../tools/qa/verify_t006_contract_consistency.py) | **`PASS`** | Đạt **17/17 Invariants PASS** và **16/16 Isolated Mutation Tests PASS** (gồm 8 đột biến cấu trúc và 8 đột biến an toàn triển khai `MUT-09..MUT-16`). |

---

## 3. Ba Điều Kiện Chuyển Giao Bắt Buộc của Gate G3 (`G3-COND-A`, `G3-COND-B`, `G3-COND-C`)

Project Lead phê duyệt Gate G3 kèm 3 điều kiện chuyển giao bắt buộc, yêu cầu các nhiệm vụ hạ tầng và chất lượng tại Gate G4 và Gate G5 phải kiểm chứng thực tế trước khi áp dụng:

### 3.1. `G3-COND-A` — Chính sách Cách ly Bản ghi Không Phê duyệt Cứng (`Record-level Quarantine Policy is PROVISIONAL`)
1. **Bản chất chính sách:** Chính sách cách ly toàn bộ dòng bản ghi (`record-level quarantine`) ở tầng nạp hiện chỉ là **đề xuất kỹ thuật sơ bộ của Gate G3**, chưa được phê duyệt thành quy tắc cứng bắt buộc cho toàn bộ pipeline.
2. **Bảo vệ định danh chuyến bay:** Ràng buộc `OP_CARRIER_FL_NUM <= 0` **tuyệt đối không được tự động trở thành quy tắc cách ly cứng toàn bộ dòng** khi chưa thực hiện khảo sát và kiểm chứng thực nghiệm trên dữ liệu thô tại `G4/T-008`.
3. **Bảo toàn nguyên tắc phân định `DC-11 / DC-12`:**
   - Chỉ có các vi phạm mỏ neo bản ghi cốt lõi (*Core Record-level Anchor Violations*: `INVALID_FL_DATE_CORE_ANCHOR`, `MISSING_CARRIER_CORE_ANCHOR`, `MISSING_AIRPORT_CORE_ANCHOR`, `INVALID_FLIGHT_NUM_CORE_ANCHOR`) mới đưa dòng vào `quarantined_row_count`.
   - Các trường hợp vi phạm tính hợp lệ của số đo chuyên biệt (*Metric-Level Invalidity*, e.g., `TAXI_OUT < 0.0`, `TAXI_IN < 0.0`, `AIR_TIME <= 0.0`) **vẫn phải được phân loại là `accepted_row_count`**, vẫn được tính vào mẫu số của `KPI-01` (`count_records`) và chỉ bị loại khỏi mẫu số hợp lệ `count_metric_valid` của chính số đo đó.

### 3.2. `G3-COND-B` — Ngữ nghĩa Số học Spark Đòi hỏi Kiểm thử Runtime Thực tế (`Spark Numeric Semantics Require Real Runtime Tests`)
1. **Vị thế vị từ số học:** Vị từ kiểm tra số hữu hạn `is_finite_numeric(c)`:
   $$\text{is\_finite\_numeric}(c) \iff c\text{.isNotNull()} \land \neg\text{isnan}(c) \land \neg c\text{.isin}(+\infty, -\infty)$$
   là một **thiết kế ứng viên (candidate design)** được duyệt về mặt lý thuyết trong `T006_FINAL_CORRECTIONS_ADDENDUM.md`.
2. **Nghĩa vụ kiểm thử tại `G4/T-009`:** Bắt buộc phải được kiểm chứng thực nghiệm bằng các DataFrame tổng hợp nhỏ (*small synthetic DataFrames*) ngay tại nhiệm vụ thiết lập hạ tầng `G4/T-009` trên đúng môi trường thực thi (PySpark 4.0.1, OpenJDK 21 LTS, Python 3.10.11 trên Windows 10) để bảo đảm không xảy ra ngoại lệ kiểu dữ liệu hay lỗi thực thi.
3. **Nghiệm thu toàn diện tại `G5/T-011`:** Toàn bộ vị từ số học cho cả 7 trường số đo CORE sẽ được nghiệm thu chính thức trong bài kiểm thử **`TS-008`** tại Gate G5.

### 3.3. `G3-COND-C` — Cơ chế Xuất bản An toàn trên Windows Phải Được Chứng Minh Thực Tế (`Windows-Safe Publication Must Be Demonstrated`)
1. **Bảo vệ hệ thống tệp Windows NTFS:** Quy trình xuất bản phân tầng 7 bước (Staged Parquet Publication: `Stage` $\to$ `Audit Row Accounting` $\to$ `Promote Data` $\to$ `Audit Promoted Data` $\to$ `Sequential/Atomic Pointer Switch` $\to$ `Verify Health` $\to$ `Rollback Readiness`) phải được chứng minh hoạt động an toàn và không xung đột khóa tệp (*file locking*) trên hệ điều hành Windows tại `G4/T-009`.
2. **Kiểm thử tiêm lỗi tại `G5/T-011`:** Bắt buộc thực hiện bài kiểm thử tiêm lỗi **`TS-013`** tại Gate G5 (`T-011`) để mô phỏng tình huống ngắt nguồn, crash tiến trình hoặc lỗi I/O bất ngờ, chứng minh rằng con trỏ xuất bản không bao giờ trỏ vào thư mục Parquet hỏng hoặc chưa hoàn tất, và dữ liệu gốc không bị ảnh hưởng.

---

## 4. Các Nghĩa Vụ Bắt Buộc Được Tiếp Tục Bảo Lưu từ Gate G2

Việc phê duyệt Gate G3 tiếp tục duy trì hiệu lực tối cao và nguyên vẹn của toàn bộ các cam kết quản trị đã xác lập tại Gate G2:

1. **Ngoại lệ đơn vị đo `G2-EXC-001` (Điều kiện chặn G6):**
   - Đúng 7 trường số đo nguồn CORE (`ARR_DELAY`, `DEP_DELAY`, `TAXI_OUT`, `TAXI_IN`, `AIR_TIME`, `ACTUAL_ELAPSED_TIME`, `CRS_ELAPSED_TIME`; không gồm `ELAPSED_DIFF`) tiếp tục mang nhãn trạng thái:
     `OFFICIAL_MINUTES_EMPIRICALLY_CONSISTENT_PROVISIONAL`
   - Tuyệt đối cấm tuyên bố các đơn vị này đã `VERIFIED` khi chưa có kết quả đối chiếu BTS TranStats.
   - Bài kiểm thử **`TS-018` BẮT BUỘC PHẢI ĐẠT `PASS`** tại Gate G5 (`T-011`). Nếu `TS-018` không đạt `PASS`, toàn bộ pipeline sẽ bị **CHẶN (`BLOCKED`)**: cấm chạy full-run 9 năm tại Gate G6 (`T-012`) và cấm xuất bản bất kỳ kết quả KPI nào.
2. **Khuyết tật độ phủ lịch năm 2024 `OR-05 = OPEN_QUALITY_DEFECT`:**
   - Năm 2024 chỉ có `335/366` ngày (thiếu 31 ngày Tháng 3/2024, ngày nhuận `2024-02-29` có `18,642` bản ghi); duy trì `source_coverage_status = PARTIAL`.
   - Bắt buộc kiểm tra sớm lịch ở stage quality `G4/T-008` và nghiệm thu chính thức bài kiểm thử `TS-004` ở `G6/T-012`.
3. **Danh tính tệp CSV nguồn `OR-08 = IDENTITY_UNVERIFIED`:**
   - Kích thước và mtime chỉ chứng minh tính đồng nhất metadata (`METADATA_MATCH_ONLY`).
   - Bắt buộc tính mã băm SHA-256 cục bộ cho 9 tệp CSV nguồn tại `G4/T-007` (`TS-019`).
4. **Phán quyết thời tiết `FP-DEC-017` (`CONDITIONAL_NO_GO`):**
   - Loại trừ `RQ-06`/`KPI-10` khỏi sản xuất.
   - Giữ nguyên 6 cột thời tiết `O_TEMP..D_WSPD` trong schema 34 cột; cấm loại bỏ dòng CORE hợp lệ vì thiếu thời tiết; duy trì nghĩa vụ kiểm thử tuân thủ `TS-011`.
5. **Các cam kết kiến trúc đã khóa:**
   - Khóa hợp đồng 8 CORE KPIs (`KPI-01..08`, `FP-DEC-012`).
   - Phân vị `percentile_approx` với `accuracy=10000` cho `KPI-06` (`FP-DEC-015`).
   - Ngưỡng `min-N` (`1000/365/100`) trên `count_metric_valid` (`FP-DEC-016`).
   - Bảo toàn cặp bản ghi `YX 3624` và bảo đảm định danh dòng ổn định (`TS-020`, `FP-DEC-010`).
   - Chấp nhận các giới hạn không chặn `L-01` và `L-02`.

---

## 5. Ranh Giới Chuyển Tiếp Cổng & Điều Kiện Mở Cổng Vào Gate G4

1. **Gate G2:** **`PASS`** (Đã đóng thành công ngày 2026-10-16).
2. **Gate G3:** **`PASS`** (Chính thức đóng thành công ngày 2026-10-17 theo biên bản này).
3. **Nhiệm vụ `T-006`:** **`PASS / COMPLETED`** (Đạt toàn diện các tiêu chuẩn thiết kế kiến trúc).
4. **Trạng thái Cổng mở `T-009_ENTRY_GATE`:** **`READY`** (Toàn bộ điều kiện tiên quyết về mặt thiết kế kiến trúc để khởi động Gate G4 đã hoàn tất đầy đủ).
5. **Trình tự thực thi Gate G4 bắt buộc:**
   $$\mathbf{T\text{-}009} \text{ (Khởi tạo Hạ tầng \& Toolchain)} \longrightarrow \mathbf{T\text{-}007} \text{ (Ingestion Đọc-chỉ \& SHA-256)} \longrightarrow \mathbf{T\text{-}008} \text{ (Quality \& Row Accounting)}$$
   - Tuyệt đối cấm đảo lộn thứ tự: không được thực hiện `T-007` hay `T-008` trước khi hoàn tất `T-009`.
6. **Lệnh dừng bắt buộc (`Strict Hold Assertion`):**
   - Mặc dù cổng vào Gate G4 đã ở trạng thái `READY`, nhưng **nhiệm vụ `T-009` (cũng như `T-007` và `T-008`) giữ nguyên trạng thái `NOT_STARTED`**.
   - Trong phạm vi phiên làm việc này, Agent **tuyệt đối không tự ý khởi động `T-009`**, không viết mã nguồn Spark hay chạy script ingestion nào.
   - Agent phải dừng lại, báo cáo kết quả đóng Gate G3 và chờ chỉ thị giao nhiệm vụ tiếp theo từ Project Lead.
