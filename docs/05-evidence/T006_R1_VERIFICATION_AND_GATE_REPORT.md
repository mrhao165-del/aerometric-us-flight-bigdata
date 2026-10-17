# T-006-R1 RECONCILIATION REPORT 4: TECHNICAL VERIFICATION & GATE G3 READINESS

**Task ID:** `T-006-R1`  
**Gate:** `G3`  
**Document Nature:** Technical Architecture Verification & Gate Readiness Report (`DESIGN_ONLY`)  
**Project:** US Flight Performance Analysis (2016–2024) using Apache Spark / PySpark  
**Status:** `T006_R1_READY_FOR_HUMAN_REVIEW`  
**Date:** 2026-10-17  
**Supersedes:** `docs/05-evidence/T006_REVIEW_AND_GATE_REPORT.md`

---

## 1. Tóm tắt Điều hành (Executive Summary)

Nhiệm vụ `T-006-R1` được kích hoạt khẩn cấp nhằm khắc phục triệt để các sai lệch ngữ nghĩa và hợp đồng kỹ thuật nghiêm trọng trong hồ sơ thiết kế kiến trúc ban đầu của `T-006` (Gate G3):
1. **Giải tỏa Nghi vấn Baseline (Phase 0):** Đã đối soát toàn diện kích thước và mã băm SHA-256 giữa tệp sao lưu trước T-006 (`T006_BACKUPS/`) và biên bản chính thức `G2_OFFICIAL_SIGNOFF_EXECUTION_MANIFEST.md`. Khẳng định **100% không có mất mát dữ liệu hoặc thoái lui baseline trên đĩa vật lý**. Sự khác biệt số liệu kích thước (`BACKLOG.md = 13,446` vs `10,757`, `PROJECT_STATE.md = 26,527` vs `19,199`) bắt nguồn từ lỗi sao chép văn bản trong câu trả lời hội thoại của Agent ở phiên trước, trong khi tệp thực tế trên đĩa và manifest nghiệm thu hoàn toàn trùng khớp từng byte.
2. **Khôi phục Schema 34 Cột Chuẩn tắc (Phase 1):** Loại bỏ hoàn toàn 9 cột BTS giả định (`CANCELLED`, `DIVERTED`, `CANCELLATION_CODE`, `DISTANCE`, 5 cột BTS delay) và khôi phục đúng 9 cột chuẩn tắc (`MONTH`, `DAY_OF_MONTH`, `DAY_OF_WEEK`, `ORIGIN_INDEX`, `DEST_INDEX`, `O_LATITUDE`, `O_LONGITUDE`, `D_LATITUDE`, `D_LONGITUDE`) theo đúng `DATA_DICTIONARY.md` và 9 tệp `schema_YYYY.json`.
3. **Phục hồi Hợp đồng 8 CORE KPIs (Phase 2):** Khôi phục chính xác công thức toán học và mẫu số hợp lệ theo `KPI_SPEC.md`:
   - `KPI-02`: Arrival Late Rate $\ge 15.0$ (không phải on-time rate).
   - `KPI-03`: Signed Mean Arrival Delay (không phải late rate; bảo toàn độ trễ âm cho các chuyến bay đến sớm).
   - `KPI-04`: Departure Late Rate $\ge 15.0$.
   - `KPI-05`: Signed Mean Departure Delay.
   - `KPI-06`: P50/P90 qua `percentile_approx(ARR_DELAY, [0.5, 0.9], accuracy=10000)` (loại bỏ Mean khỏi KPI-06).
   - `KPI-07` và `KPI-08`: Mẫu số hợp lệ $N_{valid}$ độc lập cho từng submetric taxi và thời lượng.
   - Xóa bỏ hoàn toàn các bộ lọc giả định `CANCELLED = 0.0` và `DIVERTED = 0.0`.
4. **Hạch toán Dòng & An toàn Thời gian (Phase 3):** Tuân thủ `DC-11` ($\mathbf{raw} = \mathbf{accepted} + \mathbf{quarantined} + \mathbf{rejected}$) và `FP-DEC-007` (an toàn thời gian, cấm tự cộng 24h).
5. **Truy vết Kiểm thử (Phase 4):** Chuẩn hóa toàn bộ ma trận `TS-001..TS-020` theo `TEST_PLAN.md` (làm rõ `TS-012` là tính xác định logic chứ không đòi hỏi byte-for-byte Parquet, `TS-013` rollback pointer, `TS-015` mã RES-ID, `TS-016` bảo vệ xếp hạng, `TS-020` định danh dòng phân tán).
6. **Đính chính Rủi ro Kỹ thuật & Tài nguyên (Phase 5):** Chuyển định mức RAM 7–8 GiB sang nhãn `ESTIMATED`; cảnh báo file locking trên Windows NTFS; ghi nhận `source_row_number` là đề xuất thiết kế mang nhãn `OPEN_DESIGN_VERIFICATION`; giữ nguyên `OR-08 = IDENTITY_UNVERIFIED`.
7. **Kiểm thử Hồi quy Tự động (Phase 6):** Xây dựng bộ test chuyên dụng `tools/qa/verify_t006_contract_consistency.py` đạt **12/12 Invariants PASS** và **8/8 Isolated Mutation Tests PASS**.

---

## 2. Bảng Đối soát Tính Toàn vẹn Baseline & Giải quyết Discrepancy (Phase 0)

| Tệp Quản trị Sống | Kích thước Báo cáo Chat G2 | Kích thước Thực tế trên Đĩa Sau G2 | Kích thước Sao lưu Pre-T006 (`T006_BACKUPS/`) | Mã băm SHA-256 G2 Manifest (`G2_OFFICIAL_SIGNOFF`) | Mã băm SHA-256 Pre-T006 Backup | Kết luận Đối soát Kỹ thuật |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| `docs/04-execution/PROJECT_STATE.md` | `26,527` | `19,199` | `19,199` | `32b71aecc221dc19...` | `32b71aecc221dc19...` | **Trùng khớp 100% byte-for-byte; số 26,527 là chat typo** |
| `docs/04-execution/AI_HANDOFF.md` | (không nêu) | `16,494` | `16,494` | `3454d7e5fd05645b...` | `3454d7e5fd05645b...` | **Trùng khớp 100% byte-for-byte** |
| `docs/01-planning/BACKLOG.md` | `13,446` | `10,757` | `10,757` | `aadaa304402c5f82...` | `aadaa304402c5f82...` | **Trùng khớp 100% byte-for-byte; số 13,446 là chat typo** |
| `docs/03-quality/CHANGELOG.md` | `6,104` | `6,104` | `6,104` | `62ab79f10cfeae15...` | `62ab79f10cfeae15...` | **Trùng khớp 100% byte-for-byte** |
| `tools/check_working_tree_consistency.py` | `22,143` | `22,143` | `22,143` | `3a8d897889f4ab60...` | `3a8d897889f4ab60...` | **Trùng khớp 100% byte-for-byte** |
| `tools/qa/verify_g2_repo_apply_r1_semantic_invariants.py` | `32,453` | `32,453` | `32,453` | `f95b0ff8784d9036...` | `f95b0ff8784d9036...` | **Trùng khớp 100% byte-for-byte** |

**Kết luận thẩm định độc lập:** Tuyệt đối không có hiện tượng mất mát dữ liệu hoặc thoái lui phiên bản trên đĩa. Toàn bộ nội dung quản trị Gate G2 PASS đã được bảo toàn nguyên vẹn.

---

## 3. Trạng thái Quản trị Cổng & Nhiệm vụ Hiện hành (Governance State)

Tuân thủ nghiêm ngặt các quy định tại `AGENTS.md` và quyết định của Project Lead:
* **Gate G2:** **`PASS`** (Đã đóng chính thức theo biên bản `G2_OFFICIAL_SIGNOFF_HUMAN_ACCEPTANCE_RECORD.md`).
* **Gate G3:** **`IN_PROGRESS / NOT_PASSED`** (Cổng thiết kế kiến trúc đang thực hiện; tuyệt đối **chưa được nghiệm thu PASS**).
* **Nhiệm vụ T-006:** **`IN_PROGRESS`** (Đã hoàn tất gói thiết kế sửa đổi R1; chuyển sang trạng thái chờ Project Lead xem xét).
* **Nhiệm vụ G4 (`T-009`, `T-007`, `T-008`):** **`NOT_STARTED`** (Tuyệt đối không được khởi động trước khi G3 được phê duyệt chính thức).
* **Ngoại lệ `G2-EXC-001`:** Duy trì trạng thái tạm thời `OFFICIAL_MINUTES_EMPIRICALLY_CONSISTENT_PROVISIONAL` cho 7 trường đo CORE; **bài test `TS-018` tại Gate G5 là chốt chặn bắt buộc (hard stop), nếu FAIL thì chặn toàn bộ Gate G6**.
* **Khuyết tật Lịch 2024 (`OR-05`):** Duy trì `OPEN_QUALITY_DEFECT` (khuyết 31 ngày Tháng 3/2024, chỉ có 335/366 ngày); gắn nhãn `source_coverage_status = PARTIAL`.
* **Nguồn gốc Dữ liệu Thô (`OR-08`):** Duy trì `IDENTITY_UNVERIFIED`.

---

## 4. Kết quả Thực thi Toàn bộ Hệ thống Kiểm thử QA (Verification Test Results)

Hệ thống đã thực thi toàn bộ 6 bộ kiểm thử tự động, tất cả đều đạt kết quả tuyệt đối **Exit Code 0**:

```powershell
# 1. Bộ kiểm thử Hợp đồng Thiết kế T-006-R1 Mới
python tools/qa/verify_t006_contract_consistency.py
# Exit Code: 0 | Kết quả: 12 Invariants PASS, 8 Mutation Tests PASS, 0 FAIL

# 2. Bộ kiểm thử Tính Nhất quán Cây Làm việc & Bằng chứng
python tools/check_working_tree_consistency.py
# Exit Code: 0 | Kết quả: Toàn bộ kiểm tra cấu trúc tài liệu, hash pinned và registry PASS

# 3. Bộ kiểm thử Hồi quy Sổ Đăng ký Bằng chứng
python tools/qa/test_working_tree_regression.py
# Exit Code: 0 | Kết quả: 16 PASS, 0 FAIL, 0 SKIP

# 4. Bộ kiểm thử Bất biến Ngữ nghĩa G2-R1
python tools/qa/verify_g2_repo_apply_r1_semantic_invariants.py
# Exit Code: 0 | Kết quả: 15 Invariants PASS, 14 Mutation Tests PASS

# 5. Bộ kiểm thử Hợp đồng Dữ liệu T-003
python tools/qa/verify_t003_contract_consistency.py
# Exit Code: 0 | Kết quả: 133 PASS, 0 FAIL

# 6. Bộ kiểm thử An toàn Biểu diễn Thời gian T-004
python tools/qa/verify_t004_time_representation.py
# Exit Code: 0 | Kết quả: 90 PASS, 0 FAIL
```

---

## 5. Danh mục Hồ sơ Giao phẩm T-006-R1 (Deliverables Inventory)

1. **[`docs/05-evidence/T006_R1_CANONICAL_SCHEMA_RECONCILIATION.md`](T006_R1_CANONICAL_SCHEMA_RECONCILIATION.md):** Bảng ánh xạ chuẩn tắc đúng 34 cột CSV thô, loại bỏ 9 trường giả định và khôi phục 9 trường chuẩn tắc theo `DATA_DICTIONARY.md`.
2. **[`docs/05-evidence/T006_R1_KPI_AND_TEST_RECONCILIATION.md`](T006_R1_KPI_AND_TEST_RECONCILIATION.md):** Khôi phục chính xác 8 CORE KPIs (`KPI-01..08`), loại bỏ bộ lọc cancel/divert, chuẩn hóa mẫu số độc lập và ma trận kiểm thử `TS-001..TS-020`.
3. **[`docs/05-evidence/T006_R1_ARCHITECTURE_RISK_CORRECTIONS.md`](T006_R1_ARCHITECTURE_RISK_CORRECTIONS.md):** Hiệu chỉnh định mức bộ nhớ (ESTIMATED), ranh giới chứng minh nguồn gốc, phân vùng Parquet, stable lineage (`TS-020`) và xuất bản an toàn trên Windows NTFS.
4. **[`docs/05-evidence/T006_R1_VERIFICATION_AND_GATE_REPORT.md`](T006_R1_VERIFICATION_AND_GATE_REPORT.md):** Báo cáo nghiệm thu kỹ thuật R1 và trạng thái cổng (tài liệu này).
5. **[`docs/05-evidence/T006_R1_EXECUTION_MANIFEST.md`](T006_R1_EXECUTION_MANIFEST.md):** Bản kê khai thực thi, mã băm SHA-256, và snapshot sao lưu khả nghịch.
6. **[`tools/qa/verify_t006_contract_consistency.py`](../../tools/qa/verify_t006_contract_consistency.py):** Bộ kiểm thử hợp đồng thiết kế tự động kèm 8 ca đột biến cô lập.
7. **[`docs/02-design/ARCHITECTURE.md`](../02-design/ARCHITECTURE.md):** Tài liệu kiến trúc sống đã được cập nhật đồng bộ và bổ sung Thông báo Kế thừa & Thay thế Chuẩn tắc (Mục 8).

---

## 6. Đề xuất Nghiệm thu (Final Recommendation)

Agent khuyến nghị trạng thái kỹ thuật chính thức:
$$\mathbf{T006\_R1\_READY\_FOR\_HUMAN\_REVIEW}$$

* **Gate G2:** Tiếp tục duy trì `PASS`.
* **Gate G3:** Tiếp tục duy trì `IN_PROGRESS / NOT_PASSED`.
* **Nhiệm vụ T-006:** Tiếp tục duy trì `IN_PROGRESS` cho đến khi Project Lead hoàn tất xem xét và ký biên bản nghiệm thu chính thức.
* **Nhiệm vụ G4:** Tiếp tục duy trì `NOT_STARTED`.
* **Dừng thực thi:** Dừng mọi thao tác chỉnh sửa mã nguồn hoặc dữ liệu; chờ ý kiến chỉ đạo tiếp theo từ Project Lead.
