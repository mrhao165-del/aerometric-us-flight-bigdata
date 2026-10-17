# G2_REPO_APPLY_FINAL_GATE_READINESS — Báo cáo Đánh giá Sẵn sàng Kỹ thuật Cuối cùng của Gate G2 Sau Khi Áp dụng Quyết định Phê duyệt

- **Mã tài liệu:** `G2-REPO-APPLY-RDY-004`
- **Nhiệm vụ thực thi:** `G2-REPO-APPLY` (*Controlled Governance Update, Evidence Registry Remediation & Final Gate Verification*)
- **Ngày thực hiện:** `2026-10-16`
- **Trạng thái Gate G2 Chính thức:** **`IN_PROGRESS / NOT_PASSED`** *(Readiness Annotation: `AWAITING_FINAL_HUMAN_GATE_SIGNOFF`)*
- **Trạng thái Nhiệm vụ `T-006` (Gate G3):** **`NOT_STARTED`**
- **Khuyến nghị Kỹ thuật Cuối cùng Trình Project Lead:** **`READY_FOR_FINAL_HUMAN_GATE_SIGNOFF`**

---

## 1. Ma trận Kiểm chứng Tiêu chí Đóng Gate G2 Sau Khi Đồng bộ Quyết định (`Post-Apply G2 Exit Criteria Matrix`)

| Mã tiêu chí | Nội dung tiêu chí đóng Gate G2 (theo [`ROADMAP.md`](../01-planning/ROADMAP.md), [`BACKLOG.md`](../01-planning/BACKLOG.md) & `AGENTS.md`) | Trạng thái trước `G2-REPO-APPLY` | Trạng thái sau `G2-REPO-APPLY` | Bằng chứng & Quyết định Phê duyệt của Project Lead |
|---|---|---|---|---|
| **G2-EC-01** | **Kiểm toán xuất xứ dữ liệu (`T-001`):** Xác minh nguồn gốc 9 tệp CSV, ánh xạ cột, ranh giới `source_signature` (`size/mtime` $\neq$ SHA-256) | `PASS (Conditional)` | **`SATISFIED_WITH_APPROVED_G4_TRANSFER`** | [`T001_R2_FINAL_REVIEW.md`](T001_R2_FINAL_REVIEW.md); `FP-DEC-014` (`APPROVED WITH CONDITIONS`); `OR-08` (`METADATA_MATCH_ONLY / IDENTITY_UNVERIFIED`) chuyển giao chính thức sang `G4/T-007` (`TS-019` local SHA-256). |
| **G2-EC-02** | **Kiểm toán cấp hạt & trùng lặp (`T-002`):** Xác minh cấp hạt dòng, cột `FLIGHTS == 1.0`, cặp trùng `YX 3624`, khóa mẫu số chuẩn | `PASS_WITH_OPEN_RISKS` | **`SATISFIED`** | [`T002_FINAL_ACCEPTANCE_CHECK.md`](T002_FINAL_ACCEPTANCE_CHECK.md); `FP-DEC-010` (`APPROVED WITH CONDITIONS`); `OR-01` & `OR-02` được khóa hợp đồng (`count_records`, cấm dùng `FLIGHTS` làm trọng số, cấm deduplicate tùy tiện `YX 3624`). |
| **G2-EC-03** | **Khóa công thức 8 CORE KPIs, hạch toán `DC-11/12`, `percentile_approx`, `min-N` & đơn vị đo (`T-003`)** | `PASS_WITH_OPEN_RISKS` *(Đợi phê duyệt `G2-EXC-001`, `FP-DEC-015..016`)* | **`SATISFIED_UNDER_G2_EXC_001`** | [`T003_SIGNOFF_RECORD.md`](T003_SIGNOFF_RECORD.md); Project Lead đã phê duyệt `FP-DEC-006`, `FP-DEC-008`, `FP-DEC-011`, `FP-DEC-012`, `FP-DEC-015` (`accuracy=10000`), `FP-DEC-016` (`min-N = 1000/365/100`) và ngoại lệ **`G2-EXC-001`** (`OR-03` giữ nhãn `OFFICIAL_MINUTES_EMPIRICALLY_CONSISTENT_PROVISIONAL`, bắt buộc `TS-018` đạt `PASS` tại G5 trước khi chạy G6). |
| **G2-EC-04** | **Kiểm toán biểu diễn thời gian & phủ lịch 2024 (`T-004`):** Xác định các trường thời gian an toàn, phản ví dụ qua đêm, và ghi nhận khuyết tật lịch 2024 | `READY_FOR_SIGNOFF_WITH_OPEN_DEFECT` | **`SATISFIED_WITH_TRACKED_DEFECT_OR05`** | [`T004_FINAL_QA_RECONCILIATION.md`](T004_FINAL_QA_RECONCILIATION.md); `FP-DEC-007` (`APPROVED WITH CONDITIONS`, `OR-06`); `OR-05` giữ nguyên trạng thái trung thực **`OPEN_QUALITY_DEFECT`** (`335/366` ngày năm 2024, thiếu 31 ngày Tháng 3/2024, `source_coverage_status = PARTIAL`) và chuyển giao kiểm định tự động sang `G4/T-008` (`TS-004`). |
| **G2-EC-05** | **Quyết định nhánh thời tiết tùy chọn (`T-005`):** Đánh giá khả năng sử dụng 6 cột thời tiết cho `RQ-06` / `KPI-10` | `CONDITIONAL_PENDING` | **`SATISFIED_CONDITIONAL_NO_GO`** | [`T005_FINAL_AUDIT_RECONCILIATION.md`](T005_FINAL_AUDIT_RECONCILIATION.md), [`T005_CONDITIONAL_NO_GO_PROPOSAL.md`](T005_CONDITIONAL_NO_GO_PROPOSAL.md); Project Lead đã phê duyệt **`FP-DEC-017` (`CONDITIONAL_NO_GO`)**, chuyển `T-005` sang `CLOSED_CONDITIONAL_NO_GO`, đóng `RQ-06`/`KPI-10` và hủy kích hoạt `T-015` mà không chặn lộ trình CORE. |
| **G2-EC-06** | **Đồng bộ hóa tài liệu quản trị & sổ đăng ký quyết định/rủi ro** | `PENDING_REPO_APPLY` | **`SATISFIED`** | Đã đồng bộ hóa [`DECISIONS.md`](../02-design/DECISIONS.md), [`PROJECT_STATE.md`](../04-execution/PROJECT_STATE.md), [`AI_HANDOFF.md`](../04-execution/AI_HANDOFF.md), [`TASK_TEMPLATE.md`](../04-execution/TASK_TEMPLATE.md), [`BACKLOG.md`](../01-planning/BACKLOG.md), [`KPI_SPEC.md`](../02-design/KPI_SPEC.md), [`RISK_REGISTER.md`](../03-quality/RISK_REGISTER.md) và [`CHANGELOG.md`](../03-quality/CHANGELOG.md) kèm bản sao lưu byte-for-byte tại [`G2_REPO_APPLY_BACKUPS/`](G2_REPO_APPLY_BACKUPS/). |
| **G2-EC-07** | **Toàn bộ bộ kiểm thử tự động & kiểm tra working-tree đạt `Exit Code 0`** | `FAIL` (`check_working_tree_consistency.py` báo `86 PASS, 2 FAIL`) | **`SATISFIED` (`0 FAIL` trên cả 4 bộ kiểm thử)** | `verify_t003_contract_consistency.py` (`96 PASS, 0 FAIL`), `verify_t004_time_representation.py` (`90 PASS, 0 FAIL`), `check_working_tree_consistency.py` (`0 FAIL`), `test_working_tree_registry_regression.py` (`10 PASS, 0 FAIL`). |
| **G2-EC-08** | **Chữ ký nghiệm thu đóng Gate G2 cuối cùng của Project Lead (`Final Human Gate Sign-off`)** | `NOT_PROVIDED` | **`AWAITING_FINAL_HUMAN_GATE_SIGNOFF`** | Project Lead đã phê duyệt các quyết định thiết kế Nhóm A–D và `G2-EXC-001`, nhưng theo đúng chỉ thị `G2-REPO-APPLY`, quyền ký đóng cổng `Gate G2 = PASS` thuộc bước phê duyệt cuối cùng của Con người sau khi xem xét gói kết quả này. |

---

## 2. Tổng hợp Các Nghĩa vụ Kỹ thuật Bắt buộc Chuyển giao Sang Gate G3, G4, G5 & G6 (`Downstream Gate Obligations`)

Để đảm bảo không một rủi ro mở hoặc điều kiện phê duyệt nào bị bỏ sót khi chuyển sang các cổng tiếp theo, bảng dưới đây khóa chặt các nghĩa vụ bắt buộc:

| Gate đích | Nhiệm vụ đích | Mã bài kiểm thử / Quyết định | Nội dung nghĩa vụ kỹ thuật bắt buộc | Điều kiện chặn cổng (`Gate Stop Condition`) |
|---|---|---|---|:---:|
| **Gate G3** | `T-006` | `FP-DEC-005`, `OR-05` | Chốt phiên bản Spark/Python/Java, cấu hình bộ nhớ driver/executor, chiến lược phân vùng Parquet theo `YEAR`, schema bảng tổng hợp đầu ra và thiết kế kiểm tra độ phủ lịch 2024 (`source_coverage_status = PARTIAL`, bảo toàn `provenance_reference`). | Chặn mở Gate G4 nếu chưa hoàn tất thiết kế `T-006`. |
| **Gate G4** | `T-009` $\to$ `T-007` | `TS-019`, `FP-DEC-014`, `OR-08` | **Tuân thủ thứ tự `T-009` (bootstrap) trước `T-007` (ingestion).** Tại `T-007`, bắt buộc tính và ghi nhận mã băm SHA-256 cục bộ cho toàn bộ 9 tệp CSV nguồn (`2016.csv`..`2024.csv`) vào manifest thực thi. | Chặn đóng `T-007` / Gate G4 nếu thiếu SHA-256 cục bộ của 9 tệp CSV. |
| **Gate G4** | `T-008` | `TS-003`, `TS-004`, `TS-009`, `OR-01`, `OR-02`, `OR-05`, `OR-06` | Thực thi kiểm định hạch toán dòng `DC-11/12` (`TS-009`), bảo vệ thời gian qua đêm (`TS-003`), bảo toàn cặp trùng `YX 3624` (`OR-02`), bất biến `FLIGHTS == 1.0` (`OR-01`), và phát hiện tự động 31 ngày khuyết Tháng 3/2024 (`TS-004`, `OR-05`). Không loại bỏ dòng CORE hợp lệ vì lỗi cột thời tiết (`FP-DEC-017`). | Chặn đóng `T-008` / Gate G4 nếu bất kỳ bài kiểm thử `TS-003`, `TS-004`, `TS-009` nào thất bại. |
| **Gate G5** | `T-010` | `TS-014`, `FP-DEC-005` | Chạy smoke-run 1 năm dữ liệu thật, đo đạc và ghi nhận thời gian chạy, dung lượng Parquet, số phân vùng và mức tiêu thụ tài nguyên thực tế (`TS-014`). | Chặn đóng `T-010` nếu chưa có số liệu benchmark thực nghiệm. |
| **Gate G5** | `T-011` | **`TS-008`**, **`TS-018` (`G2-EXC-001`)** | 1. Thực thi **`TS-008`**: kiểm chứng độ chính xác `percentile_approx(..., 10000)` so với phân vị chính xác trên mẫu 1 năm và kiểm chứng cờ `is_low_volume` theo ngưỡng `min-N = 1000 / 365 / 100` (`FP-DEC-015`, `FP-DEC-016`).<br>2. Thực thi **`TS-018` (`G2-EXC-001`, `OR-03`)**: đối chiếu mẫu bản ghi trực tiếp với tệp gốc BTS TranStats để xác nhận đơn vị phút chính thức cho 7 trường đo CORE. | **ĐIỀU KIỆN CHẶN CỨNG (`HARD GATE STOP`):** Nếu `TS-018` hoặc `TS-008` chưa đạt `PASS` tại G5, **chặn hoàn toàn việc chạy full-run 9 năm tại Gate G6 (`T-012..T-014`)**. |
| **Gate G6** | `T-012`..`T-014` *(Hủy `T-015`)* | `FP-DEC-017` | Chỉ chạy sau khi Gate G5 (bao gồm `TS-018`) đạt `PASS`. Nhiệm vụ `T-015` (Weather `KPI-10`) giữ trạng thái hủy kích hoạt (`DEACTIVATED_BY_FP_DEC_017`). | Chặn xuất bản báo cáo G7 nếu thiếu kết quả G6 hợp lệ. |

---

## 3. Xác nhận Trạng thái Quản trị & Khuyến nghị Kỹ thuật Cuối cùng (`Final Technical Readiness Recommendation`)

1. **Xác nhận trạng thái Gate G2:** **`IN_PROGRESS / NOT_PASSED`** (với chú thích sẵn sàng: **`AWAITING_FINAL_HUMAN_GATE_SIGNOFF`**).
2. **Xác nhận trạng thái Nhiệm vụ `T-006`:** **`NOT_STARTED`**.
3. **Đánh giá kỹ thuật độc lập:**
   - Toàn bộ các quyết định thiết kế được Project Lead phê duyệt (`G2-EXC-001`, Nhóm A `FP-DEC-003..014`, Nhóm B `FP-DEC-015..016`, Nhóm C `FP-DEC-017`, Nhóm D `OR-01..OR-08`) đã được áp dụng chính xác, đầy đủ và trung thực vào hệ thống tài liệu quản trị.
   - Công cụ kiểm tra tính nhất quán working-tree ([`tools/check_working_tree_consistency.py`](../../tools/check_working_tree_consistency.py)) đã được khắc phục triệt để bằng sổ đăng ký bằng chứng có kiểm tra mật mã học ([`EVIDENCE_DELIVERABLE_REGISTER.json`](EVIDENCE_DELIVERABLE_REGISTER.json)) và vượt qua toàn bộ 10 kịch bản kiểm thử hồi quy âm/dương ([`tools/qa/test_working_tree_registry_regression.py`](../../tools/qa/test_working_tree_registry_regression.py)).
   - Cả 4 bộ kiểm thử tự động của dự án đều đạt **`Exit Code 0` (`0 FAIL`)**.
4. **Khuyến nghị trình Project Lead:**
   > **`READY_FOR_FINAL_HUMAN_GATE_SIGNOFF`** — Kho tài liệu và bằng chứng của dự án đã hoàn toàn nhất quán, minh bạch, có khả năng hoàn nguyên 100% và sẵn sàng để Project Lead ký nghiệm thu đóng **Gate G2 (`PASS`)** và cho phép khởi động **Gate G3 (`T-006`)**.
