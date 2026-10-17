# G2_REPO_APPLY_HUMAN_APPROVAL_RECORD — Hồ sơ Phê duyệt Chính thức của Project Lead cho Các Quyết định Thiết kế & Quản trị Gate G2

- **Mã hồ sơ:** `G2-REPO-APPLY-HAR-001`
- **Nhiệm vụ thực thi:** `G2-REPO-APPLY` (*Controlled Governance Update, Evidence Registry Remediation & Final Gate Verification*)
- **Ngày ghi nhận phê duyệt:** `2026-10-16`
- **Thẩm quyền phê duyệt (Approval Authority):** **Project Lead (Human Governance Authority)** — Phê duyệt tường minh trong chỉ thị nhiệm vụ `G2-REPO-APPLY`.
- **Trạng thái Hồ sơ Phê duyệt Quyết định:** **`SIGNED_BY_PROJECT_LEAD_INSTRUCTION` (`APPROVED_WITH_CONDITIONS`)**
- **Trạng thái Gate G2 Chính thức:** **`IN_PROGRESS / NOT_PASSED`** *(Readiness: `AWAITING_FINAL_HUMAN_GATE_SIGNOFF`)*
- **Trạng thái Nhiệm vụ `T-006` (Gate G3):** **`NOT_STARTED`**

---

## 1. Phân định Thẩm quyền & Ranh giới Phê duyệt (`Critical Governance Distinction`)

Theo chỉ thị nhiệm vụ `G2-REPO-APPLY` của Project Lead:
1. **Đã được phê duyệt bởi Con người (`APPROVED`):**
   - Ngoại lệ quản trị có điều kiện **`G2-EXC-001`** đối với bằng chứng đơn vị đo của 7 trường số đo CORE (`OR-03`).
   - Toàn bộ các quyết định thiết kế **Nhóm A (`FP-DEC-003` đến `FP-DEC-014`)**.
   - Hai quyết định tham số thống kê & ngưỡng cỡ mẫu tối thiểu **Nhóm B (`FP-DEC-015`, `FP-DEC-016`)**.
   - Quyết định nhánh thời tiết tùy chọn **Nhóm C (`FP-DEC-017` — `CONDITIONAL_NO_GO`)**, chuyển đổi từ đề xuất `FP-DEC-PROP-015`.
   - Phương án xử lý, giảm thiểu và chuyển giao có kiểm soát **Nhóm D (`OR-01` đến `OR-08`)** cùng quyền nâng cấp công cụ kiểm tra tính nhất quán working-tree ([`tools/check_working_tree_consistency.py`](../../tools/check_working_tree_consistency.py)) và sổ đăng ký bằng chứng ([`EVIDENCE_DELIVERABLE_REGISTER.json`](EVIDENCE_DELIVERABLE_REGISTER.json)).
2. **Chưa được phê duyệt (`NOT_APPROVED_YET`):**
   - **Nghiệm thu đóng cổng `Gate G2 = PASS` cuối cùng CHƯA được cấp.**
   - Gate G2 bắt buộc giữ nguyên trạng thái **`IN_PROGRESS / NOT_PASSED`** (với nhãn sẵn sàng kỹ thuật `AWAITING_FINAL_HUMAN_GATE_SIGNOFF`) cho đến khi Project Lead kiểm tra gói kết quả của `G2-REPO-APPLY` và ra quyết định đóng cổng độc lập.
   - Nhiệm vụ **`T-006`** thuộc Gate G3 giữ nguyên trạng thái **`NOT_STARTED`**.

---

## 2. Hồ sơ Ngoại lệ Quản trị Có Điều kiện `G2-EXC-001` (`Unit Evidence Exception`)

| Thuộc tính | Nội dung được Project Lead phê duyệt |
|---|---|
| **Mã ngoại lệ** | **`G2-EXC-001`** |
| **Tên ngoại lệ** | *Provisional Acceptance of 7 Numeric CORE Measure Units Pending G5 BTS Cross-Check (`TS-018`)* |
| **Trạng thái** | **`APPROVED_WITH_CONDITIONS`** |
| **7 Trường áp dụng** | `ARR_DELAY`, `DEP_DELAY`, `TAXI_OUT`, `TAXI_IN`, `AIR_TIME`, `ACTUAL_ELAPSED_TIME`, `CRS_ELAPSED_TIME` (cùng cột dẫn xuất phụ trợ `ELAPSED_DIFF`) |
| **Trạng thái bằng chứng hiện tại** | **`OFFICIAL_MINUTES_EMPIRICALLY_CONSISTENT_PROVISIONAL`** (Chứng minh thực nghiệm qua đẳng thức đại số `ACTUAL_ELAPSED_TIME = TAXI_OUT + AIR_TIME + TAXI_IN` khớp 100% trên 9 năm dữ liệu tại [`T003_UNIT_VERIFICATION.md`](T003_UNIT_VERIFICATION.md) và quy ước tài liệu BTS On-Time; chưa có bản đối chiếu từng dòng với tệp gốc tải trực tiếp từ BTS TranStats do môi trường cách ly mạng). |
| **Quyết định của Project Lead** | Chấp thuận cho phép khóa hợp đồng 8 CORE KPIs (`FP-DEC-012`) tại Gate G2 mà không ngụy tạo trạng thái `VERIFIED` tuyệt đối cho 7 đơn vị đo trên. |
| **Điều kiện ràng buộc bắt buộc (Mandatory Conditions)** | 1. Giữ nguyên nhãn **`OFFICIAL_MINUTES_EMPIRICALLY_CONSISTENT_PROVISIONAL`** trong [`KPI_SPEC.md`](../02-design/KPI_SPEC.md), [`DECISIONS.md`](../02-design/DECISIONS.md), [`PROJECT_STATE.md`](../04-execution/PROJECT_STATE.md) và [`RISK_REGISTER.md`](../03-quality/RISK_REGISTER.md) (`OR-03`).<br>2. Bắt buộc thực thi bài kiểm thử đối chiếu mẫu bản ghi trực tiếp với BTS TranStats (**`TS-018`**) tại **Gate G5 (`T-011`)**.<br>3. **Điều kiện chặn cứng (Hard Gate Stop):** Nếu `TS-018` không đạt `PASS` tại Gate G5, **chặn hoàn toàn việc chạy full-run 9 năm tại Gate G6 (`T-012..T-014`) và cấm xuất bản các KPI phụ thuộc đơn vị phút**. |

---

## 3. Bảng Phê duyệt Quyết định Nhóm A (`FP-DEC-003` đến `FP-DEC-014`)

*Ghi chú: `FP-DEC-001` (`USER_CONFIRMED`) và `FP-DEC-002` (`USER_CONFIRMED_BY_SCOPE`) đã được xác nhận từ baseline G0 và được bảo toàn nguyên vẹn.*

| Decision ID | Trạng thái trước `G2-REPO-APPLY` | Trạng thái sau `G2-REPO-APPLY` | Nội dung phê duyệt & Điều kiện ràng buộc thực thi | Tài liệu áp dụng |
|---|---|---|---|---|
| **`FP-DEC-003`** | `PROPOSED` | **`APPROVED WITH CONDITIONS`** | Loại trừ hoàn toàn Machine Learning, dự báo T-2h, phạm vi đơn sân bay ATL, Flight Chain (`FLIGHT_CHAIN.md`) và cấm nạp tệp `.pt` qua `torch.load`. Điều kiện: Kiểm tra tuân thủ qua [`SECURITY.md`](../03-quality/SECURITY.md) và `TS-010`. | [`DECISIONS.md`](../02-design/DECISIONS.md), [`BACKLOG.md`](../01-planning/BACKLOG.md) |
| **`FP-DEC-004`** | `PROPOSED` | **`APPROVED WITH CONDITIONS`** | Bất biến dữ liệu thô (`data/raw/`), bất biến bằng chứng đầu vào (`docs/05-evidence/inputs/`) và nguyên tắc `immutable run_id` (chỉ cập nhật con trỏ `latest` sau khi pass kiểm định). Điều kiện: Kiểm chứng qua `TS-012`, `TS-013`. | [`DECISIONS.md`](../02-design/DECISIONS.md), [`DATA_CONTRACT.md`](../02-design/DATA_CONTRACT.md) |
| **`FP-DEC-005`** | `PROPOSED` | **`APPROVED WITH CONDITIONS`** | Phê duyệt định hướng công nghệ **Apache Spark / PySpark + Parquet** cho mô tả 9 năm (`54,674,003` dòng). **Bảo lưu bắt buộc:** Không tuyên bố đã khóa phiên bản Spark/Python/Java, cấu hình driver/executor memory, partition count hay kết quả benchmark runtime tại G2; toàn bộ thông số này chuyển giao sang `G3/T-006` (thiết kế), `G4/T-009` (bootstrap) và `G5/T-010/TS-014` (benchmark 1 năm). | [`DECISIONS.md`](../02-design/DECISIONS.md), [`ARCHITECTURE.md`](../02-design/ARCHITECTURE.md), [`BACKLOG.md`](../01-planning/BACKLOG.md) |
| **`FP-DEC-006`** | `PROPOSED` | **`APPROVED WITH CONDITIONS`** | Cấm tính toán hoặc suy diễn tỷ lệ hủy chuyến (`CANCELLED`) và chuyển hướng (`DIVERTED`) do vắng mặt trường dữ liệu trong schema 34 cột; đóng vĩnh viễn `KPI-11 = NOT_COMPUTABLE` (`OR-04 = CLOSED_BY_CONTRACT_EXCLUSION`). | [`DECISIONS.md`](../02-design/DECISIONS.md), [`KPI_SPEC.md`](../02-design/KPI_SPEC.md), [`RISK_REGISTER.md`](../03-quality/RISK_REGISTER.md) |
| **`FP-DEC-007`** | `PROPOSED` | **`APPROVED WITH CONDITIONS`** | Phê duyệt quy tắc bảo vệ biểu diễn thời gian: chỉ dùng thành phần giờ-phút kết hợp `FL_DATE` và múi giờ IANA lịch sử (`DEP_TIME_TZ`, `ARR_TIME_TZ`, `CRS_DEP_TIME_TZ`, `CRS_ARR_TIME_TZ`); **cấm** dùng thành phần ngày của `DEP_TIME`/`ARR_TIME`/`CRS_ARR_TIME` làm ngày thực tế của sự kiện và **cấm** tự động cộng `+24h` (`OR-06`). Kiểm chứng qua `TS-003` và fixture [`T004_TF09_temporal_fixture.json`](T004_TF09_temporal_fixture.json). | [`DECISIONS.md`](../02-design/DECISIONS.md), [`DATA_CONTRACT.md`](../02-design/DATA_CONTRACT.md), [`T004_SAFE_FIELDS_DECISION.md`](T004_SAFE_FIELDS_DECISION.md) |
| **`FP-DEC-008`** | `PROPOSED` | **`APPROVED WITH CONDITIONS`** | Phê duyệt ngưỡng trễ chuẩn BTS `>= 15` phút (`ARR_DEL15 = (ARR_DELAY >= 15)`, `DEP_DEL15 = (DEP_DELAY >= 15)`). Mẫu số chỉ tính trên `count_metric_valid` tương ứng (`TS-006`, `TS-007`). | [`DECISIONS.md`](../02-design/DECISIONS.md), [`KPI_SPEC.md`](../02-design/KPI_SPEC.md) |
| **`FP-DEC-009`** | `PROPOSED` | **`APPROVED WITH CONDITIONS`** | Phân tách nhánh thời tiết làm nhánh tùy chọn (`OPTIONAL`), cấm suy diễn nhân quả từ tương quan thời tiết và không chặn CORE KPIs. Kết hợp với quyết định thực thi cụ thể tại **`FP-DEC-017` (`CONDITIONAL_NO_GO`)**. | [`DECISIONS.md`](../02-design/DECISIONS.md), [`KPI_SPEC.md`](../02-design/KPI_SPEC.md) |
| **`FP-DEC-010`** | `PROPOSED` | **`APPROVED WITH CONDITIONS`** | Cấp hạt chuẩn của dataset là *Scheduled Flight Leg Record*; mẫu số chuẩn là `count_records` (tổng dòng sau kiểm định) và `count_metric_valid` (tổng dòng hợp lệ có trường đo khác null). **Cấm** dùng `SUM(FLIGHTS)` làm trọng số và **cấm** deduplicate tùy tiện cặp trùng khóa ứng viên duy nhất `YX 3624` (`2018-06-21 DEN->XNA`, `OR-01`, `OR-02`). | [`DECISIONS.md`](../02-design/DECISIONS.md), [`KPI_SPEC.md`](../02-design/KPI_SPEC.md), [`T002_DENOMINATOR_RECOMMENDATION.md`](T002_DENOMINATOR_RECOMMENDATION.md) |
| **`FP-DEC-011`** | `PROPOSED` | **`APPROVED WITH CONDITIONS`** | Khóa quy tắc hạch toán dòng loại trừ lẫn nhau `DC-11` (`raw_input_rows = accepted_rows + quarantined_rows + rejected_rows`) và tách bạch 4 chỉ số chất lượng `DC-12` (`row_parse_rate`, `metric_valid_rate_<metric>`, `temporal_date_coverage`, `source_coverage_status`). Cấm dùng thuật ngữ mơ hồ `coverage_rate`. Kiểm chứng qua `TS-009` và [`T003_FIX14_accounting_fixture.json`](T003_FIX14_accounting_fixture.json). | [`DECISIONS.md`](../02-design/DECISIONS.md), [`DATA_CONTRACT.md`](../02-design/DATA_CONTRACT.md), [`KPI_SPEC.md`](../02-design/KPI_SPEC.md) |
| **`FP-DEC-012`** | `PROPOSED` | **`APPROVED WITH CONDITIONS`** | Khóa hợp đồng 8 CORE KPIs (`KPI-01` đến `KPI-08`) cho thiết kế G3 và triển khai G4–G6 theo ngoại lệ đơn vị đo **`G2-EXC-001`** (`OFFICIAL_MINUTES_EMPIRICALLY_CONSISTENT_PROVISIONAL`, bắt buộc `TS-018` đạt `PASS` tại G5 trước khi chạy G6). | [`DECISIONS.md`](../02-design/DECISIONS.md), [`KPI_SPEC.md`](../02-design/KPI_SPEC.md), [`T003_SIGNOFF_RECORD.md`](T003_SIGNOFF_RECORD.md) |
| **`FP-DEC-013`** | `PROPOSED` | **`APPROVED WITH CONDITIONS`** | Quy tắc quản trị cổng đối với nhánh thời tiết tùy chọn: cho phép sử dụng trạng thái có điều kiện (`CONDITIONAL_NO_GO` theo `FP-DEC-017`) để không chặn lộ trình CORE G3–G6. | [`DECISIONS.md`](../02-design/DECISIONS.md), [`BACKLOG.md`](../01-planning/BACKLOG.md) |
| **`FP-DEC-014`** | `PROPOSED` | **`APPROVED WITH CONDITIONS`** | Khẳng định `source_signature` (`size_bytes`, `mtime_epoch`) chỉ là kiểm tra siêu dữ liệu nhanh, **không** chứng minh danh tính nội dung tệp thô (`METADATA_MATCH_ONLY / IDENTITY_UNVERIFIED`, `OR-08`). Bắt buộc băm SHA-256 cục bộ cho 9 tệp CSV tại Gate G4 (`T-007` / `TS-019`). | [`DECISIONS.md`](../02-design/DECISIONS.md), [`RISK_REGISTER.md`](../03-quality/RISK_REGISTER.md) |

---

## 4. Bảng Phê duyệt Quyết định Nhóm B (`FP-DEC-015` & `FP-DEC-016` — Tham số Thống kê `KPI-06` & Ngưỡng `min-N`)

| Decision ID | Trạng thái trước `G2-REPO-APPLY` | Trạng thái sau `G2-REPO-APPLY` | Thông số kỹ thuật được phê duyệt | Điều kiện kiểm thử bắt buộc tại Gate G5 |
|---|---|---|---|---|
| **`FP-DEC-015`** | `PROPOSED` (trong [`T003_PERCENTILE_AND_MIN_N_DECISIONS.md`](T003_PERCENTILE_AND_MIN_N_DECISIONS.md)) | **`APPROVED WITH CONDITIONS`** | Sử dụng hàm xấp xỉ phân vị phân tán của Spark SQL **`percentile_approx(ARR_DELAY, array(0.5, 0.9), 10000)`** (`accuracy = 10000`, sai số thứ hạng tương đối lý thuyết $\le 0.01\%$) cho `KPI-06` (`P50` và `P90` của `ARR_DELAY` trên tập `count_metric_valid(ARR_DELAY)`). | Thực thi **`TS-008`** tại Gate G5 (`T-011`): đối chiếu kết quả `percentile_approx(..., 10000)` với phân vị chính xác (`exact percentile`) trên tập mẫu 1 năm và kiểm tra tính tất định (`determinism`) giữa các lần chạy. |
| **`FP-DEC-016`** | `PROPOSED` (trong [`T003_PERCENTILE_AND_MIN_N_DECISIONS.md`](T003_PERCENTILE_AND_MIN_N_DECISIONS.md)) | **`APPROVED WITH CONDITIONS`** | Áp dụng bộ ngưỡng cỡ mẫu tối thiểu **`min-N`** tính trên **`count_metric_valid`** cho các bảng xếp hạng và phân vị:<br>- **`carrier-year >= 1,000`** (`KPI-04`, `KPI-06`)<br>- **`airport-year >= 365`** (`KPI-05`, `KPI-06`)<br>- **`route-year >= 100`** (`KPI-06` mở rộng theo chặng)<br>Các nhóm có `0 < count_metric_valid < min_N` **không bị xóa khỏi bảng xuất**, nhưng bắt buộc gắn cờ `is_low_volume = true` (`LOW_SAMPLE_DO_NOT_RANK`) và loại khỏi bảng xếp hạng Top-K chính thức. | Thực thi **`TS-008`** tại Gate G5 (`T-011`): kiểm chứng cờ `is_low_volume` và quy tắc loại trừ khỏi Top-K trên các nhóm biên (`N = 999, 1000`, `N = 364, 365`, `N = 99, 100`). |

*Ghi chú bảo toàn bằng chứng lịch sử:* Tệp [`T003_PERCENTILE_AND_MIN_N_DECISIONS.md`](T003_PERCENTILE_AND_MIN_N_DECISIONS.md) được giữ nguyên không chỉnh sửa để bảo toàn dấu vết đề xuất ban đầu của `T-003` và tương thích với kịch bản kiểm thử [`tools/qa/verify_t003_contract_consistency.py`](../../tools/qa/verify_t003_contract_consistency.py). Quyết định phê duyệt chính thức được ghi nhận tại [`DECISIONS.md`](../02-design/DECISIONS.md) và [`KPI_SPEC.md`](../02-design/KPI_SPEC.md).

---

## 5. Phê duyệt Quyết định Nhóm C (`FP-DEC-017` — Nhánh Thời tiết `CONDITIONAL_NO_GO`)

| Thuộc tính | Nội dung được Project Lead phê duyệt |
|---|---|
| **Mã quyết định chính thức** | **`FP-DEC-017`** (Chuyển đổi từ mã đề xuất `FP-DEC-PROP-015` trong [`T005_CONDITIONAL_NO_GO_PROPOSAL.md`](T005_CONDITIONAL_NO_GO_PROPOSAL.md)) |
| **Trạng thái phê duyệt** | **`APPROVED CONDITIONAL_NO_GO`** |
| **Trạng thái nhiệm vụ `T-005`** | **`CLOSED_CONDITIONAL_NO_GO`** |
| **Trạng thái `RQ-06` & `KPI-10`** | **`EXCLUDED_CONDITIONAL_NO_GO`** (Loại khỏi phạm vi phân tích và xuất bản của lộ trình sản xuất hiện tại) |
| **Trạng thái nhiệm vụ `T-015` (Gate G6)** | **Hủy kích hoạt (`DEACTIVATED_BY_FP_DEC_017`)** trong lộ trình sản xuất hiện tại |
| **5 Quy tắc Thực thi Bắt buộc** | 1. **Không loại bỏ cột ở tầng đọc thô (`DC-07`):** Vẫn đọc đủ 34 cột chuẩn từ CSV, giữ nguyên 6 cột thời tiết (`weather_code`, `temp`, `app_temp`, `precip`, `wind_speed`, `surface_pressure`) dưới dạng cột thụ động.<br>2. **Không ảnh hưởng hạch toán dòng CORE (`DC-11`):** Tuyệt đối **cấm** đưa bản ghi hợp lệ về mặt CORE vào `quarantined_rows` hoặc `rejected_rows` chỉ vì các trường thời tiết bị `null`, ngoài miền giá trị hoặc chưa xác minh xuất xứ.<br>3. **Đóng nhánh phân tích `KPI-10`:** Không tính toán và không xuất bản `KPI-10` trong pipeline G4–G6 hiện tại.<br>4. **Bảo toàn sự thật kiểm toán (`OR-07`):** Giữ nguyên trạng thái xuất xứ upstream của 6 trường thời tiết là `UNVERIFIED` (mã `WMO 4677` và đơn vị `°C`, `mm`, `km/h`, `hPa` vẫn là `EMPIRICALLY_CONSISTENT_NOT_PROVEN`), và giữ `TS-011` ở trạng thái `DEFINED_NOT_EXECUTED` (chưa thực thi).<br>5. **Điều kiện mở lại trong tương lai (`Re-activation Criteria`):** Chỉ được mở lại qua một ADR mới nếu xác minh được nguồn cấp dữ liệu thời tiết, quy tắc ghép nối không-thời gian và thực thi thành công `TS-011`. |

---

## 6. Phê duyệt Quyết định Nhóm D (`OR-01` đến `OR-08` & Cải tiến Công cụ Kiểm tra Working-Tree)

### 6.1. Bảng Phê duyệt Chuyển giao & Giảm thiểu Rủi ro Mở (`OR-01` đến `OR-08`)

| Mã rủi ro | Liên kết `R-xx` | Trạng thái sau `G2-REPO-APPLY` | Quyết định xử lý & Cổng/Bài kiểm thử nhận bàn giao |
|---|---|---|---|
| **`OR-01`** | `R-02` | **`MITIGATED_VIA_CONTRACT`** | Cột `FLIGHTS == 1.0` hằng số trên toàn bộ `54,674,003` dòng; khóa hợp đồng `FP-DEC-010` dùng `count_records` / `count_metric_valid` và kiểm tra bất biến `FLIGHTS` tại Gate G4 (`T-008` / `TS-009`). |
| **`OR-02`** | `R-02`, `R-16` | **`MITIGATED_VIA_CONTRACT`** | Bảo toàn cả 2 bản ghi của cặp trùng khóa ứng viên duy nhất `YX 3624` (`2018-06-21 DEN->XNA`, dòng `6,384,132` & `6,384,133`); cấm deduplicate tùy tiện (`FP-DEC-010`, kiểm tra tại `G4/T-008`). |
| **`OR-03`** | `R-04` | **`TRANSFERRED_TO_G5_TS018`** *(kèm `G2-EXC-001`)* | Giữ nhãn `OFFICIAL_MINUTES_EMPIRICALLY_CONSISTENT_PROVISIONAL` cho 7 trường đo CORE; bắt buộc thực thi `TS-018` tại Gate G5 (`T-011`) và chặn Gate G6 nếu `TS-018` chưa `PASS`. |
| **`OR-04`** | `R-01` | **`CLOSED_BY_CONTRACT_EXCLUSION`** | Đóng vĩnh viễn `KPI-11` (`NOT_COMPUTABLE`) do thiếu trường `CANCELLED` và `DIVERTED` (`FP-DEC-006`). |
| **`OR-05`** | `R-15` | **`OPEN_QUALITY_DEFECT`** *(Chuyển giao thiết kế/kiểm định sang `G3/G4`)* | **Không ngụy tạo đã sửa dữ liệu.** Năm 2024 chỉ có `335/366` ngày (khuyết toàn bộ 31 ngày Tháng 3/2024; ngày nhuận `2024-02-29` có `18,642` dòng). Giữ `source_coverage_status = PARTIAL` theo `DC-12`, bảo toàn `provenance_reference`, và bắt buộc thực thi kiểm tra phủ lịch `TS-004` tại Gate G4 (`T-008`). |
| **`OR-06`** | `R-05`, `R-06` | **`MITIGATED_VIA_SAFE_TIME_CONTRACT`** | Áp dụng quy tắc `FP-DEC-007` (cấm trừ trực tiếp hai chuỗi timestamp, cấm tự cộng `+24h`, chỉ dùng giờ-phút + `FL_DATE` + múi giờ IANA lịch sử); kiểm thử runtime qua `TS-003` tại Gate G4 (`T-007`, `T-008`). |
| **`OR-07`** | `R-04`, `R-07` | **`MITIGATED_BY_SCOPE_EXCLUSION`** | Áp dụng `FP-DEC-017` (`CONDITIONAL_NO_GO`): loại `RQ-06` / `KPI-10` khỏi phạm vi sản xuất hiện tại; giữ nguyên sự thật xuất xứ thời tiết là `UNVERIFIED` và `TS-011` chưa chạy. |
| **`OR-08`** | `R-11` | **`TRANSFERRED_TO_G4_TS019`** *(Giữ `IDENTITY_UNVERIFIED`)* | `source_signature` (`size/mtime`) chỉ là `METADATA_MATCH_ONLY`; danh tính nội dung 9 tệp CSV thô giữ nguyên là `IDENTITY_UNVERIFIED` tại G2 và bắt buộc tính SHA-256 cục bộ tại Gate G4 (`T-007` / `TS-019`). |

### 6.2. Phê duyệt Cải tiến Công cụ Kiểm tra Working-Tree (`Checker Remediation Authorization`)
- Project Lead đã phê duyệt việc nâng cấp [`tools/check_working_tree_consistency.py`](../../tools/check_working_tree_consistency.py) để khắc phục lỗi `86 PASS, 2 FAIL` (do danh sách tệp cho phép bị mã hóa cứng chỉ đến hết `T-004`), thay thế bằng cơ chế xác thực dựa trên sổ đăng ký bằng chứng có kiểm tra kích thước byte và băm SHA-256 ([`EVIDENCE_DELIVERABLE_REGISTER.json`](EVIDENCE_DELIVERABLE_REGISTER.json)), đồng thời giữ nguyên hai manifest bất biến [`PACKAGE_MANIFEST.json`](../../PACKAGE_MANIFEST.json) và [`inputs/SOURCE_MANIFEST.json`](inputs/SOURCE_MANIFEST.json) cùng bộ kiểm thử hồi quy âm/dương tự động ([`tools/qa/test_working_tree_registry_regression.py`](../../tools/qa/test_working_tree_registry_regression.py)).

---

## 7. Xác nhận Trạng thái Cổng Hiện tại (`Final Gate Status Attestation`)

- **Gate G2 Official Status:** **`IN_PROGRESS / NOT_PASSED`**
- **Gate G2 Readiness Annotation:** **`AWAITING_FINAL_HUMAN_GATE_SIGNOFF`**
- **Task `T-006` Status:** **`NOT_STARTED`**
- **Khuyến nghị kỹ thuật trình Project Lead:** **`READY_FOR_FINAL_HUMAN_GATE_SIGNOFF`** (Chi tiết kiểm chứng tại [`G2_REPO_APPLY_FINAL_GATE_READINESS.md`](G2_REPO_APPLY_FINAL_GATE_READINESS.md)).
