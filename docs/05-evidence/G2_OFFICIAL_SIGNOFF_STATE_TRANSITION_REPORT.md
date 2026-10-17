# G2_OFFICIAL_SIGNOFF_STATE_TRANSITION_REPORT — Báo Cáo Chuyển Trạng Thái Quản Trị & Nghiệm Thu Chính Thức Gate G2

**Mã tài liệu:** `G2_OFFICIAL_SIGNOFF_STATE_TRANSITION_REPORT`  
**Mã nhiệm vụ:** `G2-OFFICIAL-SIGNOFF` (Controlled Human Gate Acceptance & Authorized State Transition)  
**Dự án:** Phân tích hiệu suất khai thác chuyến bay Hoa Kỳ 2016–2024 bằng Apache Spark / PySpark  
**Ngày lập:** 2026-10-16  
**Thẩm quyền phê duyệt:** Project Lead đã ban hành quyết định phê duyệt bằng văn bản tường minh ngày 2026-10-16 (`APPROVED_BY_PROJECT_LEAD_EXPLICIT_INSTRUCTION`), ghi nhận tại biên bản [`docs/05-evidence/G2_OFFICIAL_SIGNOFF_HUMAN_ACCEPTANCE_RECORD.md`](G2_OFFICIAL_SIGNOFF_HUMAN_ACCEPTANCE_RECORD.md).  
**Trạng thái Gate G2 trước nhiệm vụ:** **`IN_PROGRESS / NOT_PASSED`** (Chú thích mức độ sẵn sàng: **`AWAITING_FINAL_HUMAN_GATE_SIGNOFF`**).  
**Trạng thái Gate G2 sau nhiệm vụ:** **`PASS`** (Chính thức được nghiệm thu và có hiệu lực trên toàn bộ kho lưu trữ).  
**Trạng thái Gate G3 kế tiếp:** **`PLANNED / NOT_PASSED`**.  
**Trạng thái Nhiệm vụ `T-006`:** **`NOT_STARTED`** (Điều kiện mở cổng Gate G3 cho `T-006` đã thỏa mãn: **`T-006_ENTRY_GATE = SATISFIED`**).

---

## 1. Căn Cứ Pháp Lý & Quyết Định Nghiệm Thu của Project Lead

Căn cứ theo chỉ thị trực tiếp từ Project Lead ngày 2026-10-16:
> *"Tôi, với vai trò Project Lead, phê duyệt nghiệm thu Gate G2 theo kết luận READY FOR HUMAN G2 SIGN-OFF. Tôi chấp nhận giới hạn không chặn L-01 (export manifest self-hash) và L-02 (rollback registry cần đối soát), đồng thời giữ nguyên tất cả điều kiện G2-EXC-001, OR-05, OR-08, FP-DEC-017 và các test bắt buộc G3–G6."*

Nhiệm vụ `G2-OFFICIAL-SIGNOFF` đã thực hiện chuyển dịch trạng thái quản trị có kiểm soát (controlled state transition) từ `IN_PROGRESS / NOT_PASSED` sang `PASS` trên các tài liệu quản trị sống, đồng thời cập nhật các chốt chặn kiểm thử tự động (guarded test assertions) để phản ánh tính hợp thức của biên bản nghiệm thu người dùng.

---

## 2. Danh Mục Các Tài Liệu Quản Trị Sống Được Cập Nhật

Để phản ánh chính xác trạng thái chuyển tiếp cổng mà không làm xáo trộn các tài liệu không liên quan, chỉ có 4 tài liệu quản trị sống mục tiêu được chỉnh sửa:

1. [`docs/04-execution/PROJECT_STATE.md`](../04-execution/PROJECT_STATE.md):
   - Cập nhật Gate G2: chuyển chính thức sang **`PASS`**.
   - Ghi nhận ngày nghiệm thu: `2026-10-16`, căn cứ phê duyệt: `APPROVED_BY_PROJECT_LEAD_EXPLICIT_INSTRUCTION` trỏ đến [`G2_OFFICIAL_SIGNOFF_HUMAN_ACCEPTANCE_RECORD.md`](G2_OFFICIAL_SIGNOFF_HUMAN_ACCEPTANCE_RECORD.md).
   - Ghi nhận điều kiện mở cổng cho nhiệm vụ kế tiếp: **`T-006_ENTRY_GATE = SATISFIED`**.
   - Giữ nguyên nhiệm vụ `T-006 = NOT_STARTED`.
   - Cập nhật mục *Trình tự Công việc Tiếp theo* ghi nhận Gate G2 đã đóng thành công và Gate G3 sẵn sàng khởi động khi có lệnh riêng.
2. [`docs/04-execution/AI_HANDOFF.md`](../04-execution/AI_HANDOFF.md):
   - Mục 1: Khẳng định Gate G2 = `PASS`, Gate G3 = `PLANNED / NOT_PASSED`, `T-006 = NOT_STARTED`.
   - Nhấn mạnh ranh giới cốt tử: Việc Gate G2 đạt `PASS` không thay thế việc triển khai mã Spark (chưa có mã Spark ingestion/quality). Mọi điều kiện của `G2-EXC-001`, `OR-05`, `OR-08`, `FP-DEC-017` tiếp tục ràng buộc các cổng tiếp theo.
   - Mục 4: Cập nhật thứ tự chuỗi Gate phụ thuộc (`G2` ĐÃ ĐÓNG: `PASS` $\to$ `G3` thiết kế $\to$ `G4` $\to$ `G5` $\to$ `G6` $\to$ `G7`).
3. [`docs/01-planning/BACKLOG.md`](../01-planning/BACKLOG.md):
   - Cập nhật dòng trạng thái phiên bản: Ghi nhận Gate G2 đã đạt `PASS` chính thức ngày 2026-10-16.
   - Cập nhật phụ thuộc của `T-006`: `G2 PASS (T-001..T-005)`, trạng thái `TODO` (`NOT_STARTED`).
4. [`docs/03-quality/CHANGELOG.md`](../03-quality/CHANGELOG.md):
   - Thêm bản ghi phát hành: `docs-v1.1-g2-official-signoff — 2026-10-16 (formal Project Lead acceptance of Gate G2 & authorized state transition)`.

---

## 3. Cơ Chế Chốt Chặn Kiểm Tra Có Điều Kiện (`Guarded Transition Checks`)

Thay vì xóa bỏ các quy tắc bảo vệ đã ngăn chặn Agent tự ý tuyên bố G2 PASS, hệ thống kiểm thử đã được nâng cấp thành **quy tắc kiểm tra phân tầng 2 tình huống (Two-Situation Guarded Rule)**:

### 3.1. Đặc tả Quy tắc Kiểm chứng Phân tầng
- **Tình huống A (Không có biên bản nghiệm thu hợp lệ của Project Lead):**
  - Trạng thái Gate G2 trong `PROJECT_STATE.md` bắt buộc **KHÔNG ĐƯỢC LÀ `PASS`** (phải là `IN_PROGRESS / NOT_PASSED` hoặc `DRAFT / NOT_PASSED`).
  - Bất kỳ nỗ lực nào tự ý ghi `PASS` sẽ lập tức bị bắt lỗi và trả về `FAIL` trong các bài kiểm thử.
- **Tình huống B (Tồn tại biên bản nghiệm thu hợp lệ của Project Lead):**
  - Trạng thái Gate G2 được phép là `PASS` khi và chỉ khi:
    1. Tệp bằng chứng nghiệm thu tồn tại tại đúng đường dẫn: `docs/05-evidence/G2_OFFICIAL_SIGNOFF_HUMAN_ACCEPTANCE_RECORD.md`.
    2. Chứa nguồn gốc phê duyệt chuẩn tắc: `APPROVED_BY_PROJECT_LEAD_EXPLICIT_INSTRUCTION`.
    3. Phạm vi phê duyệt xác nhận đúng Gate G2.
    4. Bảo lưu đầy đủ các điều kiện ràng buộc bắt buộc: `G2-EXC-001`, `OR-05`, `OR-08`, `FP-DEC-017`, `L-01`, `L-02`, và nghĩa vụ `TS-018`.
    5. Tài liệu sống `PROJECT_STATE.md` trỏ trực tiếp đến biên bản nghiệm thu và ghi nhận nguồn gốc phê duyệt.
    6. Các tài liệu quản trị sống (`AI_HANDOFF.md`, `BACKLOG.md`) đồng thuận trạng thái `PASS`.
    7. Nhiệm vụ `T-006` vẫn được bảo vệ ở trạng thái `NOT_STARTED` và Gate G3 không bị tuyên bố `PASS` trái phép.

### 3.2. Cập nhật Trên Các Bộ Kiểm Thử
1. [`tools/check_working_tree_consistency.py`](../../tools/check_working_tree_consistency.py):
   - Bổ sung kiểm tra có điều kiện: Khi `PROJECT_STATE.md` ghi nhận `| G2 | PASS |`, công cụ bắt buộc phải tìm thấy và xác thực tệp `G2_OFFICIAL_SIGNOFF_HUMAN_ACCEPTANCE_RECORD.md` chứa `APPROVED_BY_PROJECT_LEAD_EXPLICIT_INSTRUCTION`.
   - Bổ sung `G2-OFFICIAL-SIGNOFF` vào `ALLOWED_TASK_GATE_IDS`.
   - Bổ sung quy tắc nhận diện thư mục sao lưu phục hồi `docs/05-evidence/G2_OFFICIAL_SIGNOFF_BACKUPS/`.
2. [`tools/qa/verify_g2_repo_apply_r1_semantic_invariants.py`](../../tools/qa/verify_g2_repo_apply_r1_semantic_invariants.py):
   - Nâng cấp **`INV-12`** thành kiểm tra chốt chặn có điều kiện (*Guarded G2 Gate Acceptance & T-006 Locked*).
   - Mở rộng bộ kiểm thử đột biến cô lập:
     - **`MUT-05A`**: Chứng minh hệ thống bắt lỗi và từ chối khi G2 là `PASS` nhưng thiếu tệp biên bản nghiệm thu.
     - **`MUT-05B`**: Chứng minh hệ thống bắt lỗi khi nguồn gốc phê duyệt bị thay đổi hoặc giả mạo.
     - **`MUT-05C`**: Chứng minh hệ thống bắt lỗi khi biên bản nghiệm thu bỏ sót điều kiện ngoại lệ `G2-EXC-001`.
     - **`MUT-05D`**: Chứng minh hệ thống bắt lỗi khi Gate G3 bị tuyên bố `PASS` trái phép.
     - **`MUT-06`**: Chứng minh hệ thống bắt lỗi khi `T-006` bị khởi động sớm (`IN_PROGRESS`).
3. [`tools/qa/verify_t003_contract_consistency.py`](../../tools/qa/verify_t003_contract_consistency.py):
   - Cập nhật mục 7: Kiểm tra G2 là `PASS` khi có biên bản nghiệm thu và có liên kết bằng chứng hợp lệ, hoặc từ chối `PASS` nếu không có biên bản.
4. [`tools/qa/verify_t004_time_representation.py`](../../tools/qa/verify_t004_time_representation.py):
   - Cập nhật mục quản trị: Xác thực G2 là `PASS` trong `PROJECT_STATE.md` khi tồn tại biên bản nghiệm thu chính thức.

---

## 4. Bảo Lưu Toàn Bộ Điều Kiện & Nghĩa Vụ Downstream

Quyết định nghiệm thu Gate G2 `PASS` của Project Lead gắn liền với việc bảo lưu nguyên vẹn các điều kiện và rủi ro:

1. **`G2-EXC-001` (Ngoại lệ đơn vị đo CORE):**
   - 7 trường số đo nguồn CORE (`ARR_DELAY`, `DEP_DELAY`, `TAXI_OUT`, `TAXI_IN`, `AIR_TIME`, `ACTUAL_ELAPSED_TIME`, `CRS_ELAPSED_TIME`) duy trì nhãn `OFFICIAL_MINUTES_EMPIRICALLY_CONSISTENT_PROVISIONAL`.
   - **`TS-018` BẮT BUỘC ĐẠT `PASS`** tại Gate G5 (`T-011`) qua đối chiếu trực tiếp BTS TranStats. Nếu không đạt `PASS`, toàn bộ pipeline sẽ bị chặn (`BLOCKED`), không được chạy full-run G6 và không được công bố kết quả phụ thuộc đơn vị phút.
2. **`OR-05` (Khuyết tật chất lượng độ phủ lịch 2024):**
   - Vắng mặt toàn bộ 31 ngày Tháng 3/2024 (`335/366` ngày). Duy trì `source_coverage_status = PARTIAL` cho các báo cáo liên quan năm 2024. Bắt buộc kiểm tra sớm ở `G4/T-008` và nghiệm thu chính thức `TS-004` ở `G6/T-012`.
3. **`OR-08` (Danh tính dữ liệu thô chưa kiểm chứng):**
   - Metadata `size/mtime` chỉ là `METADATA_MATCH_ONLY`. Bắt buộc tính mã băm SHA-256 cục bộ cho 9 CSV tại `G4/T-007` (`TS-019`).
4. **`FP-DEC-017` (Weather CONDITIONAL_NO_GO):**
   - Nhánh thời tiết `RQ-06`/`KPI-10` bị loại khỏi phạm vi sản xuất hiện tại; giữ nguyên 6 cột thời tiết thô; cấm loại bỏ dòng CORE hợp lệ vì thiếu thời tiết.
5. **Giới hạn không chặn `L-01` & `L-02`:**
   - Tiếp tục được công bố minh bạch và ghi nhận là đã được Project Lead chấp thuận.

---

## 5. Kết Quả Kiểm Định Kỹ Thuật Thực Tế

Toàn bộ 5 bộ kiểm thử chuẩn tắc đã được thực thi từ thư mục gốc repository với kết quả đạt 100% chuẩn `PASS`:

| Bộ Kiểm thử (`Verification Suite`) | Tập lệnh Thực thi | Mã Thoát | Kết quả Chi tiết |
|---|---|:---:|---|
| **Suite 1: T-003 Contract Consistency** | `python tools/qa/verify_t003_contract_consistency.py` | `0` | **133 PASS**, 0 FAIL |
| **Suite 2: T-004 Time Representation** | `python tools/qa/verify_t004_time_representation.py` | `0` | **90 PASS**, 0 FAIL |
| **Suite 3: Semantic Invariants & Mutations** | `python tools/qa/verify_g2_repo_apply_r1_semantic_invariants.py` | `0` | **15 Invariants PASS, 12 Mutations PASS**, 0 FAIL |
| **Suite 4: Registry Regression Suite** | `python tools/qa/test_working_tree_registry_regression.py` | `0` | **16 PASS**, 0 FAIL, 0 SKIP |
| **Suite 5: Working-Tree Consistency Checker** | `python tools/check_working_tree_consistency.py` | `0` | **281 PASS assertions**, 0 FAIL *(Sau khi đăng ký sổ deliverables)* |

---

## 6. Kết Luận & Bàn Giao

Nhiệm vụ `G2-OFFICIAL-SIGNOFF` đã hoàn thành trọn vẹn việc ghi nhận quyết định phê duyệt của Project Lead và chuyển dịch trạng thái quản trị an toàn:

- **Gate G2:** **`PASS`**
- **Gate G3:** **`PLANNED / NOT_PASSED`**
- **Nhiệm vụ `T-006`:** **`NOT_STARTED`**
- **Điều kiện mở cổng `T-006`:** **`T-006_ENTRY_GATE = SATISFIED`**

Nhiệm vụ dừng thực thi tại đây. Toàn bộ hệ thống sẵn sàng cho nhiệm vụ mở Gate G3 và khởi động `T-006` theo chỉ thị tiếp theo của Project Lead.
