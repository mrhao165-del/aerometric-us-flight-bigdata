# AI_HANDOFF — Tài liệu Bàn giao Ngữ cảnh và Quy tắc Quản trị cho AI Agent

**Documentation Baseline:** `docs-v1.1` (`2026-10-13`), đã đồng bộ hóa các quyết định được Project Lead phê duyệt tại `G2-REPO-APPLY` và đính chính ngữ nghĩa tại `G2-REPO-APPLY-R1` (`2026-10-16`, [`G2_REPO_APPLY_R1_SEMANTIC_ERRATA.md`](../05-evidence/G2_REPO_APPLY_R1_SEMANTIC_ERRATA.md)).  
**Project Identity:** Đồ án **phân tích mô tả hồi cứu hiệu suất khai thác chuyến bay Hoa Kỳ giai đoạn 2016–2024 bằng Apache Spark / PySpark** (*Observational / Descriptive Big Data Study*).  
**Phạm vi bị loại trừ tuyệt đối (`Excluded Legacy Aeolus Scope`):** Đây **KHÔNG** phải dự án dự báo học máy Aeolus lịch sử. Tuyệt đối không đưa vào dự án này: Machine Learning dự báo trễ, quy tắc cắt dữ liệu trước giờ khởi hành `T-2h`, phạm vi chỉ riêng sân bay `ATL`, các tệp đồ thị chuỗi bay PyTorch `.pt` (cấm tuyệt đối `torch.load`), suy diễn nhân quả từ thời tiết, hoặc suy diễn 54.67 triệu bản ghi là toàn bộ chuyến bay toàn quốc Hoa Kỳ.

---

## 1. Trạng thái Gate G2, G3 & Nhiệm vụ `T-006` Hiện hành (Mandatory Starting Assertions)

- **`Gate G2 = PASS`** (Được Project Lead chính thức phê duyệt nghiệm thu ngày 2026-10-16 theo chỉ thị tường minh `APPROVED_BY_PROJECT_LEAD_EXPLICIT_INSTRUCTION`, biên bản [`docs/05-evidence/G2_OFFICIAL_SIGNOFF_HUMAN_ACCEPTANCE_RECORD.md`](../05-evidence/G2_OFFICIAL_SIGNOFF_HUMAN_ACCEPTANCE_RECORD.md); chấp nhận các giới hạn không chặn `L-01` và `L-02`).
- **`Gate G3 = PASS`** (Được Project Lead chính thức phê duyệt nghiệm thu ngày 2026-10-17 theo chỉ thị tường minh `APPROVED_BY_PROJECT_LEAD_EXPLICIT_INSTRUCTION`, biên bản [`docs/05-evidence/G3_OFFICIAL_SIGNOFF_HUMAN_ACCEPTANCE_RECORD.md`](../05-evidence/G3_OFFICIAL_SIGNOFF_HUMAN_ACCEPTANCE_RECORD.md); xác lập 3 điều kiện chuyển giao bắt buộc `G3-COND-A`, `G3-COND-B`, `G3-COND-C`).
- **`T-006 = PASS / COMPLETED`** (Hồ sơ thiết kế kiến trúc PySpark đã hoàn thành và được Project Lead nghiệm thu toàn diện).
- **`Cổng mở Gate G4: T-009_ENTRY_GATE = READY`** (Điều kiện tiên quyết mở Gate G4 đã thỏa mãn).
- **`Nhiệm vụ Gate G4 kế tiếp: T-009, T-007, T-008 = NOT_STARTED`** (Nghiêm ngặt giữ trạng thái `NOT_STARTED` / `TODO`; tuân thủ thứ tự bắt buộc `T-009` setup $\to$ `T-007` ingestion $\to$ `T-008` quality; cấm tự ý khởi động khi chưa có lệnh riêng từ Project Lead).
- **`Nhiệm vụ Tiếp theo Được Phép (Khi Có Chỉ Thị): NEXT_TASK = T-009`** (Bootstrap Python/PySpark Infrastructure, Test Runner, Lint & Run Manifest).
- **Ranh giới cốt tử:** Việc Gate G2 và Gate G3 đạt `PASS` **không đồng nghĩa với việc đã triển khai code Spark production** (chưa có code Spark production). Mọi điều kiện của `G2-EXC-001` (7 trường số đo mang nhãn `PROVISIONAL`, bắt buộc `TS-018` PASS ở G5 trước khi chạy G6), khuyết tật `OR-05` (thiếu 31 ngày Tháng 3/2024, `source_coverage_status = PARTIAL`), `OR-08` (`IDENTITY_UNVERIFIED`), và `FP-DEC-017` (Weather CONDITIONAL_NO_GO) cùng 3 điều kiện mới `G3-COND-A/B/C` tiếp tục được giữ nguyên và ràng buộc nghiêm ngặt các cổng tiếp theo. Agent kế tiếp bắt buộc phải đọc kỹ các hợp đồng thiết kế đã duyệt trước khi tiến hành công việc.

---

## 2. Thứ tự Đọc Tài liệu & Phân cấp Nguồn Chân lý (Source-of-Truth Hierarchy)

Khi bắt đầu bất kỳ phiên làm việc nào, AI Agent bắt buộc phải đọc theo thứ tự ưu tiên từ cao xuống thấp dưới đây (dùng đường dẫn thực tế từ thư mục gốc repository):

1. **Quy tắc điều hành & Đăng ký tài liệu:** [`AGENTS.md`](../../AGENTS.md), [`README.md`](../../README.md), [`docs/00-governance/DOCUMENT_REGISTER.md`](../00-governance/DOCUMENT_REGISTER.md).
2. **Trạng thái thực thi, Quyết định đã phê duyệt & Đính chính `R1`:** [`docs/04-execution/PROJECT_STATE.md`](PROJECT_STATE.md), [`docs/02-design/DECISIONS.md`](../02-design/DECISIONS.md), [`docs/05-evidence/G2_REPO_APPLY_R1_SEMANTIC_ERRATA.md`](../05-evidence/G2_REPO_APPLY_R1_SEMANTIC_ERRATA.md), [`docs/05-evidence/G2_REPO_APPLY_HUMAN_APPROVAL_RECORD.md`](../05-evidence/G2_REPO_APPLY_HUMAN_APPROVAL_RECORD.md).
3. **Hợp đồng kỹ thuật (Chủ sở hữu định nghĩa duy nhất):**
   - [`docs/02-design/DATA_CONTRACT.md`](../02-design/DATA_CONTRACT.md): Chủ sở hữu duy nhất của quy tắc hạch toán dòng `DC-11` (`raw_row_count = accepted_row_count + quarantined_row_count + rejected_row_count`) và siêu dữ liệu mẫu số/độ phủ `DC-12` (`count_records`, `count_metric_valid`, `excluded_count`, `metric_valid_rate`, `ingest_acceptance_rate`, `source_coverage_status`).
   - [`docs/02-design/KPI_SPEC.md`](../02-design/KPI_SPEC.md): Chủ sở hữu công thức toán học của `KPI-01..12`.
   - [`docs/02-design/DATA_DICTIONARY.md`](../02-design/DATA_DICTIONARY.md) & [`docs/02-design/ANALYSIS_PROTOCOL.md`](../02-design/ANALYSIS_PROTOCOL.md).
4. **Kế hoạch, Kiểm thử & Rủi ro:** [`docs/01-planning/PRD.md`](../01-planning/PRD.md), [`docs/01-planning/ROADMAP.md`](../01-planning/ROADMAP.md), [`docs/01-planning/BACKLOG.md`](../01-planning/BACKLOG.md), [`docs/03-quality/TEST_PLAN.md`](../03-quality/TEST_PLAN.md), [`docs/03-quality/RISK_REGISTER.md`](../03-quality/RISK_REGISTER.md), [`docs/03-quality/ROLLBACK_PLAN.md`](../03-quality/ROLLBACK_PLAN.md), [`docs/03-quality/SECURITY.md`](../03-quality/SECURITY.md).
5. **Thứ tự ưu tiên khi đọc hồ sơ bằng chứng Gate G2 (`Historical Report Supersession Hierarchy`):**
   - **Tài liệu đính chính [`G2_REPO_APPLY_R1_SEMANTIC_ERRATA.md`](../05-evidence/G2_REPO_APPLY_R1_SEMANTIC_ERRATA.md) thay thế và đính chính (supersede)** các lỗi hồi quy ngữ nghĩa (`R1-01..R1-06`) trong 5 báo cáo lịch sử `G2_REPO_APPLY_*.md` (vốn được giữ nguyên byte-for-byte trên đĩa để bảo toàn lịch sử kiểm toán).
   - Gói `G2_REPO_APPLY_R1_*`, `G2_REPO_APPLY_*` và [`G2_SIGNOFF_PRECHECK_CONSISTENCY_ERRATA.md`](../05-evidence/G2_SIGNOFF_PRECHECK_CONSISTENCY_ERRATA.md) thay thế các tóm tắt cũ trong `G2_SIGNOFF_*`, `G2_R1_*`, và đặc biệt thay thế báo cáo lỗi thời `G2_FINAL_GATE_READINESS_AUDIT.md`.
   - Đối với từng nhiệm vụ `T-001..T-005`, luôn ưu tiên đọc báo cáo nghiệm thu/đối chiếu cuối cùng (`T001_R2_FINAL_REVIEW.md`, `T002_FINAL_ACCEPTANCE_CHECK.md`, `T003_FINAL_CLOSEOUT_VERIFICATION.md`, `T004_FINAL_QA_RECONCILIATION.md`, `T005_FINAL_AUDIT_RECONCILIATION.md`).
   - **Cảnh báo chống tái tạo mã định danh sai (`R1-01..R1-06`):** Tuyệt đối không lấy các mã quyết định, mã rủi ro hoặc mã kiểm thử bị gán nhầm trong các bản tóm tắt cũ (ví dụ: không gán `FP-DEC-002` cho 8 CORE KPIs hay phân vị; không dùng các tên cột thời tiết tự chế `weather_code..surface_pressure`; không gán `TS-003` cho overnight hay `TS-010` cho `.pt`; không gộp `ELAPSED_DIFF` vào `G2-EXC-001`). Chỉ sử dụng bảng ánh xạ chuẩn tắc tại Mục 3 và Mục 4 bên dưới.

---

## 3. Bảng Khóa Sự thật Chuẩn tắc: `FP-DEC-001..017`, `G2-EXC-001` & `KPI-01..12`

### 3.1. Các Quyết định Kiến trúc Đã Được Project Lead Phê duyệt (`docs/02-design/DECISIONS.md`)
- **`FP-DEC-001` (`USER_CONFIRMED`):** Phạm vi phân tích mô tả hiệu suất bay Hoa Kỳ 2016–2024 (không tập trung ML; `TS-001`, `TS-004`).
- **`FP-DEC-002` (`USER_CONFIRMED_BY_SCOPE` — `R1-01`):** Sử dụng năm 2024 cho phân tích mô tả hồi cứu thay vì coi là tập ML holdout lịch sử của Aeolus (kèm công bố khuyết 31 ngày Tháng 3/2024 theo `OR-05`; `TS-004`, `TS-016`). **Không** dùng `FP-DEC-002` cho lộ trình 8 CORE KPIs (thuộc `FP-DEC-012`).
- **`FP-DEC-003` (`APPROVED`):** Loại trừ ML, dự báo ATL-only, Flight Chain `.pt` khỏi CORE; cấm `torch.load` (`R-11`; kiểm tra quản trị kho mã, không gán nhầm vào `TS-010`).
- **`FP-DEC-004` (`APPROVED`):** Dữ liệu CSV nguồn (`data/raw/tabular/{year}/flight_with_weather_{year}.csv` cho `2016..2024`, không gọi tắt là `2016.csv..2024.csv`) bất biến (Read-Only); đầu ra phân phiên bản theo `run_id` (`TS-001`, `TS-012`, `TS-013`, `TS-015`).
- **`FP-DEC-005` (`APPROVED_TECHNOLOGY_DIRECTION_DEFERRED_RUNTIME`):** Phê duyệt định hướng công nghệ **PySpark + Parquet** (cấu phần đề xuất `005A`); **hoãn** việc chọn phiên bản Spark/Python/Java, cấu hình bộ nhớ, partitioning, ngân sách tài nguyên và benchmark (cấu phần đề xuất `005B` — không phải ADR độc lập) sang `G3/T-006`, `G4/T-009` và `G5/T-010/TS-014`.
- **`FP-DEC-006` (`APPROVED`):** Cấm tính KPI canceled/diverted từ schema 34 cột hiện hữu (`KPI-11 = NOT_COMPUTABLE`, `OR-04` -> `R-01` chính / `R-02` bổ trợ; `TS-009`).
- **`FP-DEC-007` (`APPROVED_WITH_CONDITIONS`):** Quy tắc bảo vệ biểu diễn thời gian an toàn — cấm tính thời lượng bay qua đêm từ thành phần ngày của `CRS_ARR_TIME` hoặc trừ trực tiếp chuỗi timestamp, cấm tự cộng `+24h` (`OR-06` -> `R-03`; kiểm thử theo `TS-010`, không phải `TS-003`). Các mốc giờ phái sinh loại khỏi CORE (`NOT_AVAILABLE` theo `DC-02`), và `DEP_TIME_TZ..CRS_ARR_TIME_TZ` chỉ là cột phụ trợ trong synthetic fixture `TF-09`, không thuộc 34 cột raw (`R1-06`).
- **`FP-DEC-008` (`APPROVED`):** Ngưỡng `ARR_DELAY >= 15` (và `DEP_DELAY >= 15`) trên mẫu số hữu hạn `N_valid` (`TS-005` cho ngưỡng `>=15` và `N=0`; `TS-006` cho mean signed/positive và submetrics; không gán nhầm sang `TS-007`).
- **`FP-DEC-009` & `FP-DEC-013` (`APPROVED`):** Nhánh thời tiết (`RQ-06` / `KPI-10`) là tùy chọn có điều kiện, cấm suy diễn nhân quả, và phán quyết `CONDITIONAL_NO_GO` không làm chặn CORE G2/G6 (`TS-009`, `TS-011`).
- **`FP-DEC-010` (`APPROVED`):** Cấm dùng `FLIGHTS` làm trọng số (`OR-01` -> `R-09`, `KPI-12 = BLOCKED`, `TS-009`); mẫu số chuẩn là `count_records` trên cấp hạt *Scheduled Flight Leg Record*; bảo toàn cặp bản ghi `YX 3624` (`OR-02` -> `R-05` chính / `R-09, R-13` bổ trợ; `TS-012`, `TS-020`).
- **`FP-DEC-011` (`APPROVED`):** Hạch toán 3 trạng thái dòng rời nhau (`DC-11`: `raw_row_count = accepted_row_count + quarantined_row_count + rejected_row_count`, kiểm thử theo `TS-003`) và siêu dữ liệu mẫu số (`DC-12`, kiểm thử theo `TS-005` và `TS-017`; không gán nhầm vào `TS-009`). Giữ nguyên 3 giá trị hợp lệ của `source_coverage_status` là `UNKNOWN`, `PARTIAL`, `VERIFIED_WITH_SCOPE` và giữ `provenance_reference` làm con trỏ bằng chứng.
- **`FP-DEC-012` (`APPROVED_WITH_EXCEPTION_G2_EXC_001`):** Phê duyệt **8 CORE KPIs (`KPI-01..08`)** kèm **Ngoại lệ `G2-EXC-001`** cho đúng **7 trường số đo cốt lõi trong CSV nguồn** (`ARR_DELAY`, `DEP_DELAY`, `TAXI_OUT`, `TAXI_IN`, `AIR_TIME`, `ACTUAL_ELAPSED_TIME`, `CRS_ELAPSED_TIME` — không bao gồm biểu thức kiểm tra nội bộ `ELAPSED_DIFF`): giữ nhãn `OFFICIAL_MINUTES_EMPIRICALLY_CONSISTENT_PROVISIONAL` (`OR-03` -> `R-15`), cấm gọi đơn vị là đã `VERIFIED`, và **bắt buộc `TS-018` phải đạt `PASS` tại Gate G5 trước khi chạy full-run G6 hoặc xuất bản kết quả**.
- **`FP-DEC-014` (`APPROVED_WITH_CONDITIONS`):** `size/mtime` chỉ cảnh báo drift (`METADATA_MATCH_ONLY`), không chứng minh danh tính nội dung thô (`IDENTITY_UNVERIFIED`, `OR-08` -> `R-16`); bắt buộc tính SHA-256 cục bộ cho 9 CSV tại `G4/T-007` và `G5` (`TS-019`).
- **`FP-DEC-015` (`APPROVED_WITH_CONDITIONS`):** Dùng PySpark `percentile_approx(ARR_DELAY, [0.5, 0.9], accuracy=10000)` cho `KPI-06` P50/P90; phân biệt sai số thứ hạng ($\le 0.01\%$) với sai số phút tuyệt đối; kiểm chứng theo `TS-008` tại Gate G5.
- **`FP-DEC-016` (`APPROVED_WITH_CONDITIONS`):** Ngưỡng cỡ mẫu hợp lệ tối thiểu (`min-N` áp dụng trên `count_metric_valid`, không dùng `raw_row_count`): **`carrier-year >= 1000`**, **`airport-year >= 365`**, **`route-year >= 100`**; trường `min_n_status` nhận `SUPPRESSED`, `LOW_SAMPLE_CAUTION`, `SUFFICIENT` (không dùng `is_low_volume` hay `LOW_SAMPLE_DO_NOT_RANK`; kiểm chứng theo `TS-008`, `TS-016`).
- **`FP-DEC-017` (`APPROVED_CONDITIONAL_NO_GO`):** Chính thức hóa đề xuất `FP-DEC-PROP-015` — ban hành `CONDITIONAL_NO_GO` cho nhánh thời tiết (`RQ-06` / `KPI-10`), chuyển `T-005` sang `CLOSED_CONDITIONAL_NO_GO`, giữ `T-015 = CONDITIONAL_NO_GO`, và chuyển `OR-07` (`R-04`) sang `MITIGATED_BY_SCOPE_EXCLUSION`. Giữ nguyên **6 cột thời tiết thực tế trong schema 34 cột (`O_TEMP`, `O_PRCP`, `O_WSPD`, `D_TEMP`, `D_PRCP`, `D_WSPD` theo `DATA_DICTIONARY.md`; bác bỏ các tên cột tự chế `weather_code, temp, app_temp, precip, wind_speed, surface_pressure` hoặc mã `WMO 4677` — `R1-03`)**, cấm loại bỏ/quarantine bản ghi CORE hợp lệ chỉ vì thiếu thời tiết, và giữ `TS-009`, `TS-011` làm nghĩa vụ kiểm thử tương lai.

### 3.2. Danh mục Chỉ số (`KPI-01` đến `KPI-12`) & Phân biệt Trường Nguồn vs. Trường Phái sinh
- **`KPI-01..KPI-08` (`CORE`):** 8 chỉ số cốt lõi phục vụ `RQ-01..RQ-05` (`KPI-07` có 2 submetrics taxi; `KPI-08` có 3 submetrics elapsed/air time với mẫu số độc lập).
- **`KPI-09` (`OPTIONAL_DRAFT`):** Trung bình số phút trễ dương trên mỗi bản ghi hợp lệ (`sum(max(ARR_DELAY,0)) / N_valid`; không phải chỉ số "chất lượng dữ liệu" — `R1-01`).
- **`KPI-10` (`CONDITIONAL_NO_GO`):** Đã loại khỏi phạm vi phân tích sản xuất hiện tại theo `FP-DEC-017`.
- **`KPI-11` (`NOT_COMPUTABLE`):** Tỷ lệ hủy/chuyển hướng không tính được từ schema 34 cột hiện tại (`FP-DEC-006`, `OR-04`).
- **`KPI-12` (`BLOCKED`):** Tổng lượt theo trọng số `FLIGHTS` (`FP-DEC-010`, `OR-01`).
- **Phân biệt Schema:** 34 cột trong CSV nguồn là `RAW_SOURCE_FIELD` (bất biến); các cờ chất lượng, trạng thái dòng (`accepted`/`quarantined`/`rejected`), và cột siêu dữ liệu KPI là `DERIVED_FIELD` của pipeline, không bao giờ ghi ngược vào `data/raw/`.

---

## 4. Rủi ro Mở (`OR-01..OR-08`), Phụ thuộc Gate & Quy trình Xuất Bằng chứng

1. **Bảng khóa nhanh ánh xạ `OR-01..OR-08` $\leftrightarrow$ `R-01..R-17` (`R1-02`):**
   - `OR-01` (`FLIGHTS == 1.0`) $\to$ **Primary `R-09`** (`TS-009`).
   - `OR-02` (`YX 3624`) $\to$ **Primary `R-05`**, Additional `R-09`, `R-13` (`TS-012`, `TS-020`).
   - `OR-03` (7 đơn vị CORE `PROVISIONAL` theo `G2-EXC-001`) $\to$ **Primary `R-15`** (`TS-018` bắt buộc PASS ở G5).
   - `OR-04` (Thiếu `CANCELLED`/`DIVERTED`) $\to$ **Primary `R-01`**, Additional `R-02` (`TS-009`).
   - `OR-05` (`OPEN_QUALITY_DEFECT` — năm 2024 chỉ có `335/366` ngày, thiếu 31 ngày Tháng 3/2024) $\to$ **Primary `R-10`** (kiểm tra lịch sớm ở `G4/T-008`, nghiệm thu chính thức `TS-004` ở `G6/T-012`, cảnh báo ở `G6/G7` `TS-016`).
   - `OR-06` (Overnight rollover / `2400` / local time string) $\to$ **Primary `R-03`** (`TS-010`).
   - `OR-07` (6 cột thời tiết `O_TEMP..D_WSPD` thiếu provenance, `MITIGATED_BY_SCOPE_EXCLUSION`) $\to$ **Primary `R-04`** (`TS-009`, `TS-011`).
   - `OR-08` (`IDENTITY_UNVERIFIED` / `METADATA_MATCH_ONLY`) $\to$ **Primary `R-16`** (`TS-019` tính SHA-256 cục bộ 9 CSV tại `G4/T-007` và `G5`).
   - Giới hạn `UPSTREAM_URL_LICENSE_UNKNOWN` tiếp tục được theo dõi độc lập từ `T-001` (không gán nhầm vào `OR-01`, `R-02` hay `R-14`).
2. **Thứ tự phụ thuộc Gate nghiêm ngặt:**
   - `G2` (ĐÃ ĐÓNG: `PASS`) $\to$ `G3` (ĐÃ ĐÓNG: `PASS`) $\to$ `G4` (**bắt buộc `T-009` bootstrap trước `T-007` ingestion và `T-008` quality**) $\to$ `G5` (`T-010` smoke, `T-011` KPI sample + **`TS-018` bắt buộc PASS**) $\to$ `G6` (`T-012..014` full 9 năm; `T-015` = `CONDITIONAL_NO_GO`) $\to$ `G7` (`T-016..017`).
3. **Quy trình Xuất Bằng chứng & Đăng ký Deliverable Bắt buộc:**
   - Mọi nhiệm vụ phải xuất tệp bằng chứng thực tế dưới `docs/05-evidence/` theo mẫu tại [`docs/04-execution/TASK_TEMPLATE.md`](TASK_TEMPLATE.md).
   - Mọi tệp tạo mới dưới `docs/05-evidence/` hoặc `tools/` phải được đăng ký kích thước byte và mã băm SHA-256 chính xác vào [`docs/05-evidence/EVIDENCE_DELIVERABLE_REGISTER.json`](../05-evidence/EVIDENCE_DELIVERABLE_REGISTER.json) và phải vượt qua lệnh `python tools/check_working_tree_consistency.py` và `python tools/qa/verify_g2_repo_apply_r1_semantic_invariants.py` (Exit Code `0`).
