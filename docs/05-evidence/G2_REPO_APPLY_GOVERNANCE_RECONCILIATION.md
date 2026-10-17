# G2_REPO_APPLY_GOVERNANCE_RECONCILIATION — Báo cáo Đối soát Đồng bộ Tài liệu Quản trị, Quyết định, Rủi ro & Trạng thái Nhiệm vụ Gate G2

- **Mã tài liệu:** `G2-REPO-APPLY-GOV-002`
- **Nhiệm vụ thực thi:** `G2-REPO-APPLY` (*Controlled Governance Update, Evidence Registry Remediation & Final Gate Verification*)
- **Ngày thực hiện:** `2026-10-16`
- **Trạng thái Gate G2 Chính thức:** **`IN_PROGRESS / NOT_PASSED`** *(Readiness: `AWAITING_FINAL_HUMAN_GATE_SIGNOFF`)*
- **Trạng thái Nhiệm vụ `T-006` (Gate G3):** **`NOT_STARTED`**

---

## 1. Tóm tắt Thay đổi Theo Từng Tệp (`File-by-File Change Summary`)

Trong phạm vi được Project Lead phê duyệt tại `G2-REPO-APPLY`, **chính xác 9 tệp hiện hữu** thuộc nhóm tài liệu quản trị sống (`living governance docs`) và công cụ kiểm tra đã được cập nhật có kiểm soát. Toàn bộ 9 tệp đều được sao lưu nguyên bản byte-for-byte trước khi sửa tại thư mục [`G2_REPO_APPLY_BACKUPS/`](G2_REPO_APPLY_BACKUPS/).

| STT | Đường dẫn tệp được sửa | Kích thước `PACKAGE_MANIFEST` v1.1 | Kích thước trước `G2-REPO-APPLY` (`pre_bytes`) | SHA-256 trước `G2-REPO-APPLY` (`pre_sha256`) | Kích thước sau `G2-REPO-APPLY` (`post_bytes`) | SHA-256 sau `G2-REPO-APPLY` (`post_sha256`) | Đường dẫn tệp sao lưu (`backup_path`) |
|:---:|---|---:|---:|---|---:|---|---|
| 1 | [`docs/02-design/DECISIONS.md`](../02-design/DECISIONS.md) | `3,894 B` | `3,894 B` | `046ca0e627266815a1b9c17df49f6676f49c6b7e9aeb18bb6025740a56d8a180` | `18,567 B` | `3c9093aed0c028d15df0b6da001dba6a4ea7bde784b3bd655743f91e4f006ea3` | [`G2_REPO_APPLY_BACKUPS/docs__02-design__DECISIONS.md.pre_g2_repo_apply.bak`](G2_REPO_APPLY_BACKUPS/docs__02-design__DECISIONS.md.pre_g2_repo_apply.bak) |
| 2 | [`docs/04-execution/PROJECT_STATE.md`](../04-execution/PROJECT_STATE.md) | `2,561 B` *(v1.1)* | `6,148 B` *(post-T004)* | `5b803ec172155815b00e9370e3969789d8042c17785e02e5aa06750e1e647269` | `15,387 B` | `2efb4ef49f679a74f05b0742b9c68a0d020e6dfcc643f8a25a2e27264748b547` | [`G2_REPO_APPLY_BACKUPS/docs__04-execution__PROJECT_STATE.md.pre_g2_repo_apply.bak`](G2_REPO_APPLY_BACKUPS/docs__04-execution__PROJECT_STATE.md.pre_g2_repo_apply.bak) |
| 3 | [`docs/04-execution/AI_HANDOFF.md`](../04-execution/AI_HANDOFF.md) | `2,745 B` | `2,745 B` | `7bd3a3b376e13bfda0aed8ed95f1f625fa39cdc0f7ebf31ea5bb9df11df4ca69` | `12,686 B` | `a1151b479c95ccd408de2e2afa4dd4b761e712c0ba13dfacb5d99b17c800d5ff` | [`G2_REPO_APPLY_BACKUPS/docs__04-execution__AI_HANDOFF.md.pre_g2_repo_apply.bak`](G2_REPO_APPLY_BACKUPS/docs__04-execution__AI_HANDOFF.md.pre_g2_repo_apply.bak) |
| 4 | [`docs/04-execution/TASK_TEMPLATE.md`](../04-execution/TASK_TEMPLATE.md) | `1,764 B` | `1,764 B` | `47350b4b253b9ab3192404eceef87b40cbd9061c0093307ae749ed66f4bb8eb7` | `7,623 B` | `3271b673737518db3a46a286d6992a18edf193f58b517ec37ec03a4b5e2f2f26` | [`G2_REPO_APPLY_BACKUPS/docs__04-execution__TASK_TEMPLATE.md.pre_g2_repo_apply.bak`](G2_REPO_APPLY_BACKUPS/docs__04-execution__TASK_TEMPLATE.md.pre_g2_repo_apply.bak) |
| 5 | [`docs/01-planning/BACKLOG.md`](../01-planning/BACKLOG.md) | `5,026 B` | `5,026 B` | `6525a1735338f80c5a4ad1d4260cab1b43646a342799c8fb300f9db9adc787ed` | `9,344 B` | `16c38e9836910e353972fc1329f49f59e2c932b6271297cebf5d95673fed8a87` | [`G2_REPO_APPLY_BACKUPS/docs__01-planning__BACKLOG.md.pre_g2_repo_apply.bak`](G2_REPO_APPLY_BACKUPS/docs__01-planning__BACKLOG.md.pre_g2_repo_apply.bak) |
| 6 | [`docs/02-design/KPI_SPEC.md`](../02-design/KPI_SPEC.md) | `5,845 B` | `5,845 B` | `1972fca2c67288a76984fe1f9953752f77dd65262bee04ff1af942902e4a6dbe` | `8,703 B` | `c189df7a2d0843e7c8153185535bd5dcdef798381396be92b1bd00ffff8cf0ed` | [`G2_REPO_APPLY_BACKUPS/docs__02-design__KPI_SPEC.md.pre_g2_repo_apply.bak`](G2_REPO_APPLY_BACKUPS/docs__02-design__KPI_SPEC.md.pre_g2_repo_apply.bak) |
| 7 | [`docs/03-quality/RISK_REGISTER.md`](../03-quality/RISK_REGISTER.md) | `3,215 B` | `3,215 B` | `745c18d56f60173b6e41e102894bd968570650359a14c38aa1c620dc54cf12df` | `8,457 B` | `a08ee340d66ff5462ab33908a422b660f6ed033af64124f56f122af18c75a2f8` | [`G2_REPO_APPLY_BACKUPS/docs__03-quality__RISK_REGISTER.md.pre_g2_repo_apply.bak`](G2_REPO_APPLY_BACKUPS/docs__03-quality__RISK_REGISTER.md.pre_g2_repo_apply.bak) |
| 8 | [`docs/03-quality/CHANGELOG.md`](../03-quality/CHANGELOG.md) | `2,012 B` | `2,012 B` | `feb443581633193be978be9e587b3dbae8d4afd700dfc231c16fa73b021365f1` | `3,217 B` | `d687e6389e515f9845d0205bcf41496a7f024592a94a34149d9f1f9fbb0eda4e` | [`G2_REPO_APPLY_BACKUPS/docs__03-quality__CHANGELOG.md.pre_g2_repo_apply.bak`](G2_REPO_APPLY_BACKUPS/docs__03-quality__CHANGELOG.md.pre_g2_repo_apply.bak) |
| 9 | [`tools/check_working_tree_consistency.py`](../../tools/check_working_tree_consistency.py) | *(Tạo sau v1.1)* | `8,688 B` | `acdc5911180a4f3672b51a5182d070ed8f72f868665f4ecc4f162c905ebc2a91` | `19,258 B` | `5fe26d6e072982a5c851cda519359ac3d2fa1eddbba5ec9ff19f020014ec8704` | [`G2_REPO_APPLY_BACKUPS/tools__check_working_tree_consistency.py.pre_g2_repo_apply.bak`](G2_REPO_APPLY_BACKUPS/tools__check_working_tree_consistency.py.pre_g2_repo_apply.bak) |

---

## 2. Đối soát Bảng Ánh xạ Quyết định (`Decision ID Mapping: FP-DEC-001..017 & G2-EXC-001`)

| Mã quyết định | Trạng thái trước | Trạng thái chính thức hiện tại | Tóm tắt nội dung đồng bộ hóa trên các tài liệu quản trị |
|---|---|---|---|
| **`FP-DEC-001`** | `USER_CONFIRMED` | **`USER_CONFIRMED`** | Phạm vi phân tích mô tả hiệu suất bay Hoa Kỳ 2016–2024 trên 9 tệp CSV đã kiểm toán (`54,674,003` dòng). |
| **`FP-DEC-002`** | `USER_CONFIRMED_BY_SCOPE` | **`USER_CONFIRMED_BY_SCOPE`** | Ưu tiên lộ trình **8 CORE KPIs** (`KPI-01..KPI-08`) và chất lượng dữ liệu (`KPI-09`); tách biệt hoàn toàn các nhánh tùy chọn/ngoài phạm vi. |
| **`FP-DEC-003`** | `PROPOSED` | **`APPROVED WITH CONDITIONS`** | Cấm ML, dự báo T-2h, phạm vi đơn sân bay ATL, Flight Chain và cấm `torch.load` tệp `.pt` (`TS-010`). |
| **`FP-DEC-004`** | `PROPOSED` | **`APPROVED WITH CONDITIONS`** | Bất biến `data/raw/`, `docs/05-evidence/inputs/`, `SOURCE_MANIFEST.json`, `PACKAGE_MANIFEST.json`; đầu ra bất biến theo `run_id` (`TS-012`, `TS-013`). |
| **`FP-DEC-005`** | `PROPOSED` | **`APPROVED WITH CONDITIONS`** | Định hướng công nghệ PySpark + Parquet. **Bảo lưu rõ ràng:** các thông số runtime/phiên bản Spark-Python-Java/partitioning/benchmark vẫn mở và chuyển giao sang `G3/T-006`, `G4/T-009` và `G5/T-010/TS-014`. |
| **`FP-DEC-006`** | `PROPOSED` | **`APPROVED WITH CONDITIONS`** | Cấm tính KPI hủy chuyến/chuyển hướng do thiếu trường `CANCELLED`, `DIVERTED`; đóng vĩnh viễn `KPI-11 = NOT_COMPUTABLE` (`OR-04`). |
| **`FP-DEC-007`** | `PROPOSED` | **`APPROVED WITH CONDITIONS`** | Quy tắc bảo vệ thời gian an toàn: chỉ dùng giờ-phút + `FL_DATE` + múi giờ IANA lịch sử; cấm suy diễn ngày từ chuỗi timestamp và cấm tự cộng `+24h` (`OR-06`, `TS-003`). |
| **`FP-DEC-008`** | `PROPOSED` | **`APPROVED WITH CONDITIONS`** | Ngưỡng trễ chuẩn BTS `>= 15` phút (`ARR_DEL15`, `DEP_DEL15`) trên mẫu số `count_metric_valid` (`TS-006`, `TS-007`). |
| **`FP-DEC-009`** | `PROPOSED` | **`APPROVED WITH CONDITIONS`** | Tách nhánh thời tiết làm tùy chọn, cấm suy diễn nhân quả; dẫn chiếu sang quyết định đóng có điều kiện `FP-DEC-017`. |
| **`FP-DEC-010`** | `PROPOSED` | **`APPROVED WITH CONDITIONS`** | Cấp hạt *Scheduled Flight Leg Record*; mẫu số chuẩn `count_records` và `count_metric_valid`; cấm dùng `FLIGHTS` làm trọng số (`OR-01`) và cấm deduplicate tùy tiện cặp trùng `YX 3624` (`OR-02`). |
| **`FP-DEC-011`** | `PROPOSED` | **`APPROVED WITH CONDITIONS`** | Hạch toán dòng loại trừ lẫn nhau `DC-11` (`accepted + quarantined + rejected = raw_input_rows`) và tách 4 chỉ số chất lượng `DC-12` (`TS-009`). |
| **`FP-DEC-012`** | `PROPOSED` | **`APPROVED WITH CONDITIONS`** | Khóa hợp đồng 8 CORE KPIs (`KPI-01..08`) kèm ngoại lệ đơn vị đo **`G2-EXC-001`** (`OFFICIAL_MINUTES_EMPIRICALLY_CONSISTENT_PROVISIONAL`, bắt buộc `TS-018` đạt `PASS` tại G5 trước khi chạy G6). |
| **`FP-DEC-013`** | `PROPOSED` | **`APPROVED WITH CONDITIONS`** | Nhánh thời tiết tùy chọn dùng trạng thái có điều kiện (`CONDITIONAL_NO_GO`) để không chặn lộ trình CORE G3–G6. |
| **`FP-DEC-014`** | `PROPOSED` | **`APPROVED WITH CONDITIONS`** | `source_signature` (`size/mtime`) chỉ là `METADATA_MATCH_ONLY`; danh tính nội dung 9 tệp CSV giữ là `IDENTITY_UNVERIFIED` (`OR-08`) và chuyển giao băm SHA-256 sang `G4/T-007` (`TS-019`). |
| **`FP-DEC-015`** | `PROPOSED` *(T-003)* | **`APPROVED WITH CONDITIONS`** | Xấp xỉ phân vị `KPI-06` bằng `percentile_approx(ARR_DELAY, array(0.5, 0.9), 10000)` (`accuracy = 10000`), kiểm chứng qua `TS-008` tại Gate G5 (`T-011`). |
| **`FP-DEC-016`** | `PROPOSED` *(T-003)* | **`APPROVED WITH CONDITIONS`** | Ngưỡng cỡ mẫu tối thiểu `min-N` trên `count_metric_valid`: `carrier-year >= 1000`, `airport-year >= 365`, `route-year >= 100`; gắn cờ `is_low_volume = true` (`LOW_SAMPLE_DO_NOT_RANK`), kiểm chứng qua `TS-008` tại G5 (`T-011`). |
| **`FP-DEC-017`** | `PROPOSED` *(`FP-DEC-PROP-015`)* | **`APPROVED CONDITIONAL_NO_GO`** | Đóng nhánh thời tiết `RQ-06` / `KPI-10` (`EXCLUDED_CONDITIONAL_NO_GO`) và hủy kích hoạt `T-015` trong lộ trình hiện tại; giữ nguyên 6 cột thời tiết trong schema 34 cột (`DC-07`), cấm loại bỏ dòng CORE hợp lệ vì lỗi thời tiết (`DC-11`), và bảo toàn sự thật xuất xứ thời tiết là `UNVERIFIED` (`OR-07`). |
| **`G2-EXC-001`** | `PENDING_HUMAN_SIGNOFF` | **`APPROVED_WITH_CONDITIONS`** | Ngoại lệ hoãn đối chiếu trực tiếp với BTS TranStats cho 7 đơn vị đo số học CORE sang Gate G5 (`TS-018`), kèm điều kiện chặn cứng Gate G6 nếu `TS-018` chưa `PASS`. |

---

## 3. Đối soát Sổ Đăng ký Rủi ro (`Risk Register Mapping: R-01..R-17 & OR-01..OR-08`)

### 3.1. Bảo toàn 17 Rủi ro Gốc (`R-01` đến `R-17`)
Toàn bộ 17 mã rủi ro gốc `R-01` đến `R-17` trong [`RISK_REGISTER.md`](../03-quality/RISK_REGISTER.md) được giữ nguyên định danh để đảm bảo tính tương thích hoàn toàn với [`tools/qa/verify_t004_time_representation.py`](../../tools/qa/verify_t004_time_representation.py) và các tài liệu thiết kế. Cột trạng thái của từng rủi ro đã được cập nhật phản ánh kết quả kiểm toán G2 và các quyết định `FP-DEC-003..017`, `G2-EXC-001`.

### 3.2. Liên kết Tường minh 8 Rủi ro Mở Thực nghiệm (`OR-01` đến `OR-08`)
Mục 2 của [`RISK_REGISTER.md`](../03-quality/RISK_REGISTER.md) ghi nhận đầy đủ bảng theo dõi `OR-01` đến `OR-08`:
- **`OR-01` (`R-02`):** `MITIGATED_VIA_CONTRACT` (`FP-DEC-010`, kiểm tra `TS-009` tại `G4/T-008`).
- **`OR-02` (`R-02`, `R-16`):** `MITIGATED_VIA_CONTRACT` (`FP-DEC-010`, bảo toàn cặp trùng duy nhất `YX 3624`).
- **`OR-03` (`R-04`):** `TRANSFERRED_TO_G5_TS018` (`FP-DEC-012` + `G2-EXC-001`, giữ nhãn `OFFICIAL_MINUTES_EMPIRICALLY_CONSISTENT_PROVISIONAL`, chặn G6 nếu `TS-018` không đạt `PASS`).
- **`OR-04` (`R-01`):** `CLOSED_BY_CONTRACT_EXCLUSION` (`FP-DEC-006`, `KPI-11 = NOT_COMPUTABLE`).
- **`OR-05` (`R-15`):** **`OPEN_QUALITY_DEFECT`** (Năm 2024 chỉ có `335/366` ngày, thiếu trọn 31 ngày Tháng 3/2024; giữ `source_coverage_status = PARTIAL` theo `DC-12`, bảo toàn `provenance_reference`, kiểm tra `TS-004` tại `G4/T-008`).
- **`OR-06` (`R-05`, `R-06`):** `MITIGATED_VIA_SAFE_TIME_CONTRACT` (`FP-DEC-007`, kiểm tra `TS-003` tại `G4/T-007..008`).
- **`OR-07` (`R-04`, `R-07`):** `MITIGATED_BY_SCOPE_EXCLUSION` (`FP-DEC-017 = CONDITIONAL_NO_GO`; giữ sự thật xuất xứ thời tiết `UNVERIFIED` và `TS-011` chưa chạy).
- **`OR-08` (`R-11`):** `TRANSFERRED_TO_G4_TS019` (`FP-DEC-014`; giữ `IDENTITY_UNVERIFIED` tại G2 và băm SHA-256 cục bộ tại `G4/T-007`).

---

## 4. Đối soát Trạng thái Nhiệm vụ (`Task Status Reconciliation: T-001..T-006 & Downstream Tasks`)

| Task ID | Gate | Trạng thái trong `BACKLOG.md` & `PROJECT_STATE.md` | Diễn giải đồng bộ hóa |
|---|---:|---|---|
| **`T-001`** | `G2` | **`PASS` *(Conditional)*** | Hoàn tất kiểm toán xuất xứ (`T001_R2_FINAL_REVIEW.md`); chuyển giao `OR-08` (`TS-019`) sang `G4/T-007`. |
| **`T-002`** | `G2` | **`PASS_WITH_OPEN_RISKS`** | Hoàn tất kiểm toán cấp hạt, `FLIGHTS == 1.0`, cặp trùng `YX 3624` và mẫu số chuẩn (`FP-DEC-010`, `OR-01`, `OR-02`). |
| **`T-003`** | `G2` | **`PASS_WITH_OPEN_RISKS`** | Hoàn tất kiểm toán 8 CORE KPIs, `FIX-14`, phê duyệt `FP-DEC-012`, `FP-DEC-015`, `FP-DEC-016` và ngoại lệ `G2-EXC-001` (`OR-03`, `OR-04`, `TS-008`, `TS-018`). |
| **`T-004`** | `G2` | **`READY_FOR_SIGNOFF_WITH_OPEN_DEFECT`** | Hoàn tất kiểm toán biểu diễn thời gian (`FP-DEC-007`, `OR-06`, `TF-01..09`) và giữ nguyên khuyết tật mở `OR-05 = OPEN_QUALITY_DEFECT` (thiếu 31 ngày Tháng 3/2024). |
| **`T-005`** | `G2` | **`CLOSED_CONDITIONAL_NO_GO`** | Đóng nhánh thời tiết theo quyết định `FP-DEC-017` (`CONDITIONAL_NO_GO`); loại `RQ-06` / `KPI-10` khỏi phạm vi sản xuất hiện tại (`OR-07`). |
| **`T-006`** | `G3` | **`NOT_STARTED`** | Thiết kế kiến trúc PySpark, phiên bản, tài nguyên (`FP-DEC-005`) và xử lý `OR-05` — **bị khóa cho đến khi Project Lead ký nghiệm thu `Gate G2 = PASS`**. |
| **`T-007`..`T-017`** | `G4–G7` | **`NOT_STARTED`** *(Riêng `T-015`: `DEACTIVATED_BY_FP_DEC_017`)* | Cập nhật rõ các nghĩa vụ nhận bàn giao: `T-009` chạy trước `T-007` (`TS-019` SHA-256) và `T-008` (`TS-004` lịch 2024); `T-010` (`TS-014` benchmark); `T-011` (`TS-008` percentile/min-N và **`TS-018` đối chiếu đơn vị BTS bắt buộc trước G6**); `T-015` hủy kích hoạt theo `FP-DEC-017`. |

---

## 5. Xác nhận Bất biến Dữ liệu Thô & Hồ sơ Bằng chứng Lịch sử (`Immutability Attestation`)

Qua kiểm tra tự động bằng [`tools/check_working_tree_consistency.py`](../../tools/check_working_tree_consistency.py):
1. **Không có bất kỳ tệp nào trong `data/raw/` hoặc `docs/05-evidence/inputs/` bị chạm tới hoặc sửa đổi.** Toàn bộ 13 tệp đầu vào trong [`inputs/SOURCE_MANIFEST.json`](inputs/SOURCE_MANIFEST.json) khớp tuyệt đối 100% về kích thước byte và mã băm SHA-256.
2. **Hai tệp manifest gốc [`PACKAGE_MANIFEST.json`](../../PACKAGE_MANIFEST.json) và [`inputs/SOURCE_MANIFEST.json`](inputs/SOURCE_MANIFEST.json) được giữ nguyên bất biến byte-for-byte.**
3. **Toàn bộ các báo cáo bằng chứng lịch sử từ `T-001` đến `T-005`, `G2-FINAL-REVIEW`, `G2-R1`, `G2-SIGNOFF-PREP`, `G2-SIGNOFF-PRECHECK` và `G2-SIGNOFF-HANDOFF-FIX` được bảo toàn nguyên trạng 100%** và được đăng ký mã băm SHA-256 trong [`EVIDENCE_DELIVERABLE_REGISTER.json`](EVIDENCE_DELIVERABLE_REGISTER.json).
