# G2_OFFICIAL_SIGNOFF_HUMAN_ACCEPTANCE_RECORD — Biên Bản Nghiệm Thu Chính Thức Gate G2 của Project Lead

**Mã tài liệu:** `G2_OFFICIAL_SIGNOFF_HUMAN_ACCEPTANCE_RECORD`  
**Mã nhiệm vụ:** `G2-OFFICIAL-SIGNOFF` (Controlled Human Gate Acceptance & Authorized State Transition)  
**Dự án:** Phân tích hiệu suất khai thác chuyến bay Hoa Kỳ 2016–2024 bằng Apache Spark / PySpark  
**Cổng nghiệm thu:** **Gate G2 — Data Audit, Grain, Units, Temporal Safety & Contracts Sign-off**  
**Ngày phê duyệt:** 2026-10-16  
**Nguồn gốc phê duyệt (Approval Provenance):** `APPROVED_BY_PROJECT_LEAD_EXPLICIT_INSTRUCTION`  
**Trạng thái Gate G2 sau nghiệm thu:** **`PASS`**  
**Trạng thái Gate G3 kế tiếp:** **`PLANNED / NOT_PASSED`**  
**Trạng thái Nhiệm vụ `T-006`:** **`NOT_STARTED`** (Điều kiện mở cổng Gate G3 cho `T-006` đã thỏa mãn; `T-006` sẵn sàng bắt đầu khi có chỉ thị riêng)  
**Tuyên bố minh bạch danh tính:** Không sử dụng chữ ký điện tử giả mạo, chữ ký tay quét lại hay chứng thực mật mã học ngoài luồng; ghi nhận trung thực và minh bạch chỉ thị bằng văn bản trực tiếp từ Project Lead trong phiên làm việc 2026-10-16.

---

## 1. Tuyên Bố Nghiệm Thu Trực Tiếp của Project Lead (Verbatim Acceptance Statement)

Project Lead đã ban hành quyết định phê duyệt chính thức bằng văn bản vào ngày 2026-10-16 với nội dung nguyên văn như sau:

> *"Tôi, với vai trò Project Lead, phê duyệt nghiệm thu Gate G2 theo kết luận READY FOR HUMAN G2 SIGN-OFF. Tôi chấp nhận giới hạn không chặn L-01 (export manifest self-hash) và L-02 (rollback registry cần đối soát), đồng thời giữ nguyên tất cả điều kiện G2-EXC-001, OR-05, OR-08, FP-DEC-017 và các test bắt buộc G3–G6."*

Quyết định này là cơ sở pháp lý và kỹ thuật tối cao cho phép chuyển trạng thái chính thức của Gate G2 từ `IN_PROGRESS / NOT_PASSED` sang **`PASS`**.

---

## 2. Phạm Vi Đóng Cổng Gate G2 & Trạng Thái Các Nhiệm Vụ Thành Phần (`T-001` đến `T-005`)

Gate G2 chính thức được đóng với toàn bộ 5 nhiệm vụ kiểm toán nền tảng đạt kết quả nghiệm thu có điều kiện theo đúng hồ sơ bằng chứng:

| Nhiệm vụ (`Task`) | Trọng tâm Kiểm toán | Trạng thái Nghiệm thu | Báo cáo Nghiệm thu Cuối cùng | Quyết định & Rủi ro Kèm theo |
|---|---|:---:|---|---|
| **`T-001`** | Nguồn dữ liệu, giấy phép, cấp độ bao phủ, metadata identity | **`PASS (Conditional)`** | [`T001_R2_FINAL_REVIEW.md`](T001_R2_FINAL_REVIEW.md) | `OR-08` (`IDENTITY_UNVERIFIED` $\to$ Primary `R-16`); chuyển giao sang G4/G5 (`T-007` / `TS-019`) để tính SHA-256 cục bộ cho 9 CSV nguồn. |
| **`T-002`** | Cấp hạt chuyến bay (*Scheduled Flight Leg Record*), trường `FLIGHTS`, cặp bản ghi `YX 3624` | **`PASS_WITH_OPEN_RISKS`** | [`T002_FINAL_ACCEPTANCE_CHECK.md`](T002_FINAL_ACCEPTANCE_CHECK.md) | `FP-DEC-010` (mẫu số `count_records`, cấm dùng `FLIGHTS` làm trọng số, `OR-01` $\to$ Primary `R-09`); cấm deduplicate tùy tiện cặp `YX 3624` (`OR-02` $\to$ Primary `R-05`, Additional `R-09/13`, `TS-012`, `TS-020`). |
| **`T-003`** | Đơn vị đo 7 trường số CORE, khóa 8 CORE KPIs, phân vị `percentile_approx` và ngưỡng `min-N` | **`PASS_WITH_OPEN_RISKS`** | [`T003_SIGNOFF_RECORD.md`](T003_SIGNOFF_RECORD.md) | `FP-DEC-012` kèm ngoại lệ **`G2-EXC-001`** (7 trường số đo CORE mang nhãn `PROVISIONAL`, bắt buộc `TS-018` PASS ở G5); `FP-DEC-015` (`accuracy=10000`); `FP-DEC-016` (`min-N = 1000/365/100`). |
| **`T-004`** | An toàn biểu diễn thời gian, cấm tự cộng `+24h`, khuyết tật độ phủ lịch 2024 | **`READY_FOR_SIGNOFF_WITH_OPEN_DEFECT`** | [`T004_FINAL_QA_RECONCILIATION.md`](T004_FINAL_QA_RECONCILIATION.md) | `FP-DEC-007` (bảo vệ chuỗi thời gian, `TS-010`); ghi nhận khuyết tật **`OR-05 = OPEN_QUALITY_DEFECT`** (năm 2024 chỉ có `335/366` ngày, thiếu 31 ngày Tháng 3/2024, `source_coverage_status = PARTIAL`). |
| **`T-005`** | Kiểm toán nhánh thời tiết, schema 6 cột thực tế `O_TEMP..D_WSPD` | **`CLOSED_CONDITIONAL_NO_GO`** | [`T005_FINAL_AUDIT_RECONCILIATION.md`](T005_FINAL_AUDIT_RECONCILIATION.md) | **`FP-DEC-017`** (`CONDITIONAL_NO_GO` loại `RQ-06`/`KPI-10` khỏi sản xuất); giữ nguyên 6 cột thời tiết, cấm loại bỏ dòng CORE hợp lệ vì thiếu thời tiết (`OR-07` $\to$ Primary `R-04`, `TS-011`). |

---

## 3. Các Quyết Định Thiết Kế Được Bảo Lưu Toàn Vẹn (`FP-DEC-001..017`)

Tất cả các quyết định thiết kế đã được phê duyệt trong chuỗi `G2-REPO-APPLY` và `G2-REPO-APPLY-R1` tiếp tục có hiệu lực đầy đủ, không bị thay đổi, điều chỉnh hay hủy bỏ:

- **`FP-DEC-001`:** Phạm vi nghiên cứu mô tả hồi cứu 2016–2024 (`USER_CONFIRMED`).
- **`FP-DEC-002`:** Sử dụng năm 2024 cho phân tích mô tả hồi cứu (`USER_CONFIRMED_BY_SCOPE`).
- **`FP-DEC-003`:** Loại trừ hoàn toàn ML, dự báo ATL-only, mô hình đồ thị PyTorch `.pt` khỏi CORE (`APPROVED`).
- **`FP-DEC-004`:** Dữ liệu nguồn `data/raw/` là bất biến (Read-Only) (`APPROVED`).
- **`FP-DEC-005`:** Phê duyệt định hướng PySpark + Parquet, hoãn runtime sang `G3/T-006` và `G4/T-009` (`APPROVED_TECHNOLOGY_DIRECTION_DEFERRED_RUNTIME`).
- **`FP-DEC-006`:** Cấm tính KPI hủy/chuyển hướng từ 34 cột hiện tại (`KPI-11 = NOT_COMPUTABLE`, `APPROVED`).
- **`FP-DEC-007`:** Quy tắc bảo vệ thời gian an toàn, cấm trừ trực tiếp chuỗi timestamp, cấm cộng `+24h` (`APPROVED_WITH_CONDITIONS`).
- **`FP-DEC-008`:** Ngưỡng trễ `>= 15` phút trên mẫu số hợp lệ (`APPROVED`).
- **`FP-DEC-009` & `FP-DEC-013`:** Thời tiết là nhánh tùy chọn, cấm suy diễn nhân quả (`APPROVED`).
- **`FP-DEC-010`:** Cấm dùng `FLIGHTS` làm trọng số, bảo toàn cặp bản ghi `YX 3624` (`APPROVED`).
- **`FP-DEC-011`:** Hạch toán 3 trạng thái dòng `DC-11` rời nhau (`accepted`, `quarantined`, `rejected`) (`APPROVED`).
- **`FP-DEC-012`:** Khóa hợp đồng 8 CORE KPIs (`KPI-01..08`) kèm ngoại lệ **`G2-EXC-001`** (`APPROVED_WITH_EXCEPTION_G2_EXC_001`).
- **`FP-DEC-014`:** Metadata `size/mtime` không chứng minh nội dung thô (`APPROVED_WITH_CONDITIONS`).
- **`FP-DEC-015`:** Phân vị `percentile_approx` với `accuracy=10000` cho `KPI-06` (`APPROVED_WITH_CONDITIONS`).
- **`FP-DEC-016`:** Ngưỡng `min-N` (`1000/365/100`) trên `count_metric_valid` (`APPROVED_WITH_CONDITIONS`).
- **`FP-DEC-017`:** Phán quyết `CONDITIONAL_NO_GO` cho nhánh thời tiết (`APPROVED_CONDITIONAL_NO_GO`).

---

## 4. Điều Kiện Bắt Buộc Của Ngoại Lệ Đơn Vị Đo `G2-EXC-001`

1. **Danh mục 7 trường số đo áp dụng:** Đúng 7 trường số đo nguồn CORE gồm:
   - `ARR_DELAY`
   - `DEP_DELAY`
   - `TAXI_OUT`
   - `TAXI_IN`
   - `AIR_TIME`
   - `ACTUAL_ELAPSED_TIME`
   - `CRS_ELAPSED_TIME`
   *(Tuyệt đối không bao gồm biểu thức kiểm tra nội bộ `ELAPSED_DIFF`)*.
2. **Nhãn trạng thái đơn vị đo:** Duy trì trạng thái:
   `OFFICIAL_MINUTES_EMPIRICALLY_CONSISTENT_PROVISIONAL`
   *(Tuyệt đối cấm tuyên bố các đơn vị này đã `VERIFIED` khi chưa thực hiện đối chiếu nguồn)*.
3. **Điều kiện chặn bắt buộc tại Gate G5 (Mandatory Hard-Stop at G5):**
   - Bài kiểm thử **`TS-018`** (đối chiếu trực tiếp mẫu bản ghi với BTS TranStats) **BẮT BUỘC PHẢI ĐẠT `PASS`** tại Gate G5 (`T-011`).
   - Nếu `TS-018` không đạt `PASS`, toàn bộ pipeline sẽ bị **CHẶN (`BLOCKED`)**: không được phép thực thi full-run 9 năm tại Gate G6 (`T-012`) và không được phép xuất bản bất kỳ kết quả KPI phụ thuộc đơn vị phút nào.
   - Việc Gate G2 đạt `PASS` **tuyệt đối không miễn trừ** nghĩa vụ thực hiện bài kiểm thử `TS-018`.

---

## 5. Rủi Ro Tồn Đọng (`Residual Risks`) & Các Giới Hạn Đã Được Project Lead Chấp Nhận

### 5.1. Rủi ro Chất lượng Dữ liệu Được Giữ Nguyên
1. **`OR-05 = OPEN_QUALITY_DEFECT` (Thiếu Tháng 3/2024):**
   - Năm 2024 chỉ có `335/366` ngày (thiếu trọn vẹn 31 ngày Tháng 3/2024).
   - Duy trì `source_coverage_status = PARTIAL` cho các chỉ số liên quan đến năm 2024. Cấm tự tạo bản ghi giả mạo hoặc coi những ngày thiếu là có 0 chuyến bay.
   - Bắt buộc kiểm tra sớm lịch ở `G4/T-008` và nghiệm thu chính thức `TS-004` ở `G6/T-012`.
2. **`OR-08 = IDENTITY_UNVERIFIED` (Danh tính CSV nguồn chưa kiểm chứng):**
   - Việc đối khớp kích thước và thời gian sửa đổi (`size/mtime`) chỉ chứng minh tính đồng nhất metadata, không chứng minh tính toàn vẹn nội dung thô so với upstream BTS.
   - Bắt buộc tính mã băm SHA-256 cục bộ cho 9 tệp CSV nguồn tại `G4/T-007` (`TS-019`).
3. **Thời tiết `FP-DEC-017` (`CONDITIONAL_NO_GO`):**
   - Loại trừ `RQ-06`/`KPI-10` khỏi sản xuất. Không được phép quarantine bản ghi CORE hợp lệ chỉ vì thiếu 6 trường thời tiết `O_TEMP..D_WSPD`.

### 5.2. Các Giới Hạn Không Chặn Đã Được Project Lead Chấp Thuận
1. **`L-01` (Export manifest self-hash inconsistency):** Tệp `EXPORT_MANIFEST.json` trong gói ZIP đánh giá độc lập trước đây chứa sự không nhất quán về mã băm tự thân. Project Lead đã chấp nhận đây là giới hạn tài liệu không chặn tiến trình nghiệm thu.
2. **`L-02` (Rollback registry requires reconciliation across historical states):** Việc phục hồi các tệp do sổ đăng ký kiểm soát đòi hỏi đối soát đồng bộ và không thể thực thi tự động qua các trạng thái lịch sử (đặc biệt khi repository không sử dụng Git). Project Lead đã chấp nhận và phê duyệt phụ lục phục hồi phân tầng [`docs/05-evidence/G2_FINAL_CLOSEOUT_ROLLBACK_ERRATA.md`](G2_FINAL_CLOSEOUT_ROLLBACK_ERRATA.md).

---

## 6. Danh Mục Nghĩa Vụ Kiểm Thử Bắt Buộc Khi Mở Cổng `G3–G6`

Việc đóng Gate G2 chuyển giao nguyên vẹn các nghĩa vụ kiểm thử sau đây sang các cổng tiếp theo:
1. **`TS-003`:** Kiểm chứng hạch toán dòng rời nhau (`raw = accepted + quarantined + rejected`) tại `G4/T-008`.
2. **`TS-004`:** Nghiệm thu chính thức độ phủ lịch nguồn và xử lý khuyết tật Tháng 3/2024 tại `G6/T-012`.
3. **`TS-008`:** Kiểm chứng phân vị `percentile_approx` (`accuracy=10000`) và ngưỡng `min-N` (`1000/365/100`) tại `G5/T-011` và `G6/T-013`.
4. **`TS-010`:** Kiểm chứng quy tắc an toàn biểu diễn thời gian và cấm cộng `+24h` tại `G4/T-008`.
5. **`TS-011`:** Kiểm chứng tuân thủ miễn trừ biểu đồ thời tiết theo `FP-DEC-017` tại `G5/G6`.
6. **`TS-014`:** Đo đạc benchmark hiệu năng và tài nguyên thực tế tại `G5/T-010`.
7. **`TS-018`:** Đối chiếu mẫu 7 trường đo số CORE trực tiếp với BTS TranStats (điều kiện chặn G6) tại `G5/T-011`.
8. **`TS-019`:** Thiết lập baseline SHA-256 cục bộ cho 9 CSV nguồn tại `G4/T-007`.
9. **`TS-020`:** Bảo đảm định danh dòng ổn định (*Stable lineage / row identifier*) tại `G4/T-007` và `G6/T-012`.

---

## 7. Kết Luận Khóa Quản Trị & Ranh Giới Chuyển Tiếp Cổng

1. **Gate G2:** **`PASS`** (Được phê duyệt chính thức theo biên bản này).
2. **Gate G3:** **`PLANNED / NOT_PASSED`** (Chưa được nghiệm thu; thiết kế kiến trúc PySpark chưa triển khai).
3. **Nhiệm vụ `T-006`:** **`NOT_STARTED`** (Điều kiện mở cổng Gate G3 cho `T-006` đã thỏa mãn; tuy nhiên `T-006` **chưa được phép khởi động** trong phạm vi nhiệm vụ này. Agent phải dừng lại và chờ chỉ thị riêng từ Project Lead).
4. **Bảo toàn dữ liệu:** Không có bất kỳ dòng dữ liệu thô `data/raw/` nào bị sửa đổi. Không có lệnh Spark nào được thực thi.
