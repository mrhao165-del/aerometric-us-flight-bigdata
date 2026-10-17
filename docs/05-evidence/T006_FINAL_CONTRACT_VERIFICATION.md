# T-006 FINAL CONTRACT VERIFICATION & IMPLEMENTATION-SAFETY REPORT

**Task ID:** `T-006` (Final Bounded Implementation-Safety Closeout)  
**Gate:** `G3`  
**Document Nature:** Authoritative Independent Verification & Technical Sign-Off Assessment  
**Project:** US Flight Performance Analysis (2016–2024) using Apache Spark / PySpark  
**Status:** `READY_FOR_T006_HUMAN_SIGNOFF`  
**Date:** 2026-10-17  
**Authority:** Direct Project Lead Instruction for Task `G3-T006-FINAL-CORRECTIONS`

---

## 1. Tóm Tắt Điều Hành & Bối Cảnh (Executive Summary)

Báo cáo này hoàn tất chu trình hiệu chỉnh và kiểm chứng độc lập cuối cùng cho nhiệm vụ thiết kế kiến trúc Big Data `T-006` thuộc Gate G3.

### 1.1. Bối cảnh Nhiệm vụ
Sau khi gói hồ sơ hiệu chỉnh `T-006-R1` được đệ trình, qua rà soát độc lập đã phát hiện thêm 6 điểm thiếu sót ở ranh giới triển khai an toàn (*implementation-safety edge cases*):
1. **Phân loại trạng thái dòng (DC-11/DC-12):** Sự nhầm lẫn giữa tính bất hợp lệ cấp bản ghi (*Record Invalidity* - đưa vào `QUARANTINED`) và tính bất hợp lệ cấp chỉ số (*Metric Invalidity* - chỉ loại khỏi mẫu số $N_{valid}$ của riêng chỉ số đó mà vẫn giữ `ACCEPTED` cho `KPI-01`).
2. **Vị từ số thực hữu hạn trong Spark Catalyst:** Các biểu thức so sánh thông thường (`col >= 0`) không loại bỏ được `NaN` và `Infinity` theo chuẩn IEEE 754 trong Spark SQL, có nguy cơ làm sai lệch P90 và tính giá trị trung bình bằng `Infinity`.
3. **Quy trình xuất bản 7 bước trên Windows NTFS:** Rủi ro khóa tệp (*file-locking / AccessDeniedException*) khi đổi tên thư mục trên Windows và thiếu kịch bản tiêm lỗi `TS-013` kiểm chứng cơ chế rollback con trỏ.
4. **Hướng dẫn hoàn nguyên mang tính hủy hoại:** Đoạn mã trong Mục 5 của `T006_R1_EXECUTION_MANIFEST.md` chứa lệnh xóa tệp bằng chứng (`Remove-Item -Force`), vi phạm trực tiếp nguyên tắc bảo tồn bằng chứng bất biến của repository.
5. **Ranh giới an toàn nạp dữ liệu thô:** Áp đặt ràng buộc cứng `NOT_NULL` trên các trường lịch `MONTH`, `DAY_OF_MONTH`, `DAY_OF_WEEK` trái với định nghĩa nullable trong `DATA_DICTIONARY.md`; sử dụng regex tiền tố mở không an toàn; và nguy cơ ép kiểu ngầm làm mất dấu vết token lỗi.
6. **Lỗi chính tả đường dẫn script kiểm thử:** Sai sót tên tệp `test_working_tree_regression.py` trong manifest cũ.

### 1.2. Trạng Thái Quản Trị Hiện Hành
- **`Gate G2` = `PASS`** (Bảo toàn nguyên vẹn với biên bản chấp thuận chính thức từ Project Lead).
- **`Gate G3` = `IN_PROGRESS / NOT_PASSED`** (Chờ Project Lead ký duyệt chính thức sau báo cáo này).
- **`Task T-006` = `IN_PROGRESS`** (Đã hoàn tất kỹ thuật, đạt trạng thái `READY_FOR_T006_HUMAN_SIGNOFF`).
- **`Tasks T-009, T-007, T-008` = `NOT_STARTED`** (Tuyệt đối không khởi động trước khi G3 PASS).
- **Phạm vi:** Tài liệu thiết kế kiến trúc chuẩn hóa (`DESIGN_ONLY`), chưa nạp dữ liệu production, chưa chạy Spark cụm.

---

## 2. Kiểm Chứng Độc Lập 6 Điểm Hiệu Chỉnh Kỹ Thuật (Detailed Technical Verification)

### 2.1. FIX-01 — Chuẩn hóa Hạch toán Dòng DC-11 & Phân định DC-12
- **Đẳng thức Hạch toán Ba Trạng thái:**
  $$\mathbf{raw\_row\_count} = \mathbf{accepted\_row\_count} + \mathbf{quarantined\_row\_count} + \mathbf{rejected\_row\_count}$$
  Đẳng thức này bảo đảm tính rời nhau tuyệt đối giữa 3 tập hợp và được tích hợp đồng bộ vào [ARCHITECTURE.md](../02-design/ARCHITECTURE.md#51-mô-hình-ba-trạng-thái-rời-nhau-tuyệt-đối-three-state-accounting) Mục 5.1 và [T006_FINAL_CORRECTIONS_ADDENDUM.md](T006_FINAL_CORRECTIONS_ADDENDUM.md#2-fix-01--chuẩn-hóa-hạch-toán-dòng-dc-11--phân-định-mẫu-số-dc-12) Mục 2.
- **Ranh giới `REJECTED`:** Giới hạn duy nhất cho lỗi phân tích cú pháp CSV (CSV parse failure: rách dòng, sai số cột, quote hỏng). Nếu không thể đếm tin cậy, kích hoạt ngay `ACCOUNTING_UNVERIFIED` và `BLOCK_PUBLICATION`.
- **Ranh giới `QUARANTINED`:** Chỉ áp dụng cho vi phạm mốc định danh cốt lõi với mã chuẩn hóa:
  - `INVALID_FL_DATE_CORE_ANCHOR`: Ngày bay không thể phân tích cú pháp.
  - `MISSING_CARRIER_CORE_ANCHOR`: Khuyết hãng bay `OP_CARRIER`.
  - `MISSING_AIRPORT_CORE_ANCHOR`: Khuyết `ORIGIN` hoặc `DEST`.
  - `INVALID_FLIGHT_NUM_CORE_ANCHOR`: Số hiệu `OP_CARRIER_FL_NUM <= 0`.
- **Phân định Metric Invalidity:** Các giá trị âm hoặc null của `TAXI_OUT`, `TAXI_IN`, `AIR_TIME`, `ACTUAL_ELAPSED_TIME`, `CRS_ELAPSED_TIME` được xếp loại là **`ACCEPTED`**, được tính vào `KPI-01` (`count_records`), và chỉ bị loại trừ khỏi mẫu số $N_{valid}$ của riêng submetric tương ứng theo đẳng thức:
  $$\mathbf{count\_records}(C) = \mathbf{count\_metric\_valid}(m, C) + \mathbf{excluded\_count}(m, C)$$

### 2.2. FIX-02 — Vị Từ Số Thực Hữu Hạn Đầy Đủ (Complete Numeric Validity)
- **Cơ chế Spark Catalyst / IEEE 754:** Biểu thức boolean `col >= 0` trả về `false` đối với `NaN`, nhưng hàm phân vị `percentile_approx` và toán tử `sort` xem `NaN` là giá trị cực đại, dẫn đến sai lệch P90. Đồng thời `+Infinity >= 0` trả về `true`, làm hỏng hàm `avg()`.
- **Hàm Chuẩn hóa:**
  ```python
  def is_finite_numeric(col_name: str):
      c = F.col(col_name)
      return c.isNotNull() & ~F.isnan(c) & ~c.isin(float("inf"), float("-inf"))
  ```
- **Vị từ cho 7 Trường đo CORE:**
  - `ARR_DELAY`: `is_finite_numeric("ARR_DELAY")` (giữ nguyên delay âm).
  - `DEP_DELAY`: `is_finite_numeric("DEP_DELAY")` (giữ nguyên delay âm).
  - `TAXI_OUT`: `is_finite_numeric("TAXI_OUT") & (F.col("TAXI_OUT") >= 0.0)`
  - `TAXI_IN`: `is_finite_numeric("TAXI_IN") & (F.col("TAXI_IN") >= 0.0)`
  - `AIR_TIME`: `is_finite_numeric("AIR_TIME") & (F.col("AIR_TIME") > 0.0)`
  - `ACTUAL_ELAPSED_TIME`: `is_finite_numeric("ACTUAL_ELAPSED_TIME") & (F.col("ACTUAL_ELAPSED_TIME") > 0.0)`
  - `CRS_ELAPSED_TIME`: `is_finite_numeric("CRS_ELAPSED_TIME") & (F.col("CRS_ELAPSED_TIME") > 0.0)`
- **Ma trận Fixtures:** Đã kiểm thử 9 trường hợp (null, nan, +inf, -inf, 0.0, -15.0, mẫu số độc lập, mẫu số 0) và gán mã lý do loại trừ tường minh (`METRIC_VALUE_NAN`, `METRIC_VALUE_POS_INF`, `ZERO_METRIC_DENOMINATOR`).

### 2.3. FIX-03 — Quy Trình Xuất Bản 7 Bước Trên Windows NTFS
- **Trình tự 7 Bước Tuyệt Đối:**
  1. `data/staging/{run_id}/`: Ghi tạm toàn bộ dữ liệu.
  2. Xác thực hạch toán dòng: Kiểm tra `raw = accepted + quarantined + rejected`. Nếu sai lệch: hủy xuất bản (`ACCOUNTING_UNVERIFIED`).
  3. Thăng cấp phiên bản: Chuyển dữ liệu sang `data/curated/runs/{run_id}/`.
  4. Đọc kiểm tra tính toàn vẹn: Đọc thử Parquet và verify mã băm.
  5. Cập nhật con trỏ nguyên tử: Ghi tệp văn bản nhỏ `latest_run_id` chứa `run_id`.
  6. Bảo lưu con trỏ dự phòng: Nếu Bước 5 gặp lỗi `AccessDeniedException` (Windows NTFS file-locking), kích hoạt rollback con trỏ về phiên bản trước.
  7. Ghi nhật ký trạng thái (thành công hoặc thất bại kèm log kiểm toán).
- **Ca Tiêm Lỗi `TS-013`:** Thiết kế kịch bản tiêm lỗi quyền truy cập ở Bước 5; điều kiện đạt là con trỏ phiên bản cũ được giữ nguyên, không xuất bản dữ liệu rách và bảo lưu staging để kiểm toán.

### 2.4. FIX-04 — Đính Chính Hoàn Nguyên An Toàn (Non-Destructive Rollback Addendum)
- **Tuyên bố Hủy bỏ:** Hủy bỏ và thu hồi toàn bộ hướng dẫn hoàn nguyên mang tính hủy hoại trong Mục 5 của `docs/05-evidence/T006_R1_EXECUTION_MANIFEST.md`.
- **Nguyên tắc Chuẩn tắc:**
  1. Bằng chứng bất biến: Không xóa bất kỳ báo cáo kiểm toán, manifest, tệp bằng chứng hay thư mục sao lưu nào (`Remove-Item -Force` bị cấm tuyệt đối).
  2. Hoàn nguyên có chọn lọc: Chỉ khôi phục tài liệu sống (`ARCHITECTURE.md`) bằng cách ghi đè từ bản sao lưu đã kiểm chứng mã băm SHA-256.
  3. Đồng bộ sổ đăng ký: Cập nhật `current_bytes` và `current_sha256` trong `EVIDENCE_DELIVERABLE_REGISTER.json`.
  4. Không dùng lệnh Git giả định (`git checkout`, `git reset`) khi workspace chưa có Git repository.

### 2.5. FIX-05 — Ranh Giới An Toàn Dữ Liệu Thô & Regex Neo Chặt
- **Thẩm quyền `DATA_DICTIONARY.md`:** Là nguồn thẩm quyền duy nhất xác lập danh mục 34 cột raw.
- **Tính Nullable của Cột Lịch:** `MONTH`, `DAY_OF_MONTH`, `DAY_OF_WEEK` được định nghĩa là `Int64 nullable`. Cấm áp đặt ràng buộc cứng `NOT_NULL` trong tầng nạp thô; tháng được trích xuất an toàn từ `FL_DATE`.
- **Anchored Regex cho `FL_DATE`:** Bắt buộc sử dụng regex neo chặt 2 đầu:
  `^(?:\d{4}-\d{2}-\d{2}|\d{4}-\d{2}-\d{2} 00:00:00)$`
  Nghiêm cấm regex tiền tố mở `^\d{4}-\d{2}-\d{2}` vì sẽ chấp nhận chuỗi rác có đuôi hỏng.
- **Bảo toàn Rủi ro `OR-08`:** Khẳng định mã băm cục bộ là baseline nội bộ, không chứng minh tính đồng nhất tuyệt đối với BTS TranStats; giữ nguyên `OR-08 = IDENTITY_UNVERIFIED`.

### 2.6. FIX-06 — Đính Chính Lỗi Chính Tả Đường Dẫn Script
- Đính chính tên script kiểm thử trong các báo cáo R1 cũ thành đường dẫn thực tế trên đĩa:
  [`tools/qa/test_working_tree_registry_regression.py`](../../tools/qa/test_working_tree_registry_regression.py).

---

## 3. Thứ Tự Ưu Tiên Kế Thừa Chuẩn Tắc (Precedence Hierarchy)

Khi phát sinh bất kỳ sự khác biệt nào giữa các tài liệu kỹ thuật, thứ tự ưu tiên pháp lý cao nhất được áp dụng như sau:
$$\mathbf{DATA\_DICTIONARY.md} \equiv \mathbf{KPI\_SPEC.md} \equiv \mathbf{DATA\_CONTRACT.md}$$
$$> \mathbf{T006\_FINAL\_CORRECTIONS\_ADDENDUM.md}$$
$$> \mathbf{T006\_R1\_*} \ (\text{Reports 1–5})$$
$$> \mathbf{ARCHITECTURE.md}$$
$$> \mathbf{T006\_(Initial \ Deliverables)}$$

---

## 4. Nhật Ký Thực Thi Kiểm Thử Độc Lập Toàn Bộ 6 Bộ Test (QA Verification Logs)

Toàn bộ 6 bộ test tự động của repository đã được thực thi độc lập và đều đạt kết quả **PASS 100% (exit code 0)**:

### 4.1. Bộ Kiểm Thử Tính Nhất Quán Hợp Đồng T-006 & Đột Biến (Suite 1)
- **Lệnh chạy:** `python tools/qa/verify_t006_contract_consistency.py`
- **Exit Code:** `0`
- **Kết quả:** `17 INVARIANTS PASS, 16 MUTATIONS PASS, 0 FAIL`
- **Log thực thi:**
  ```text
  ================================================================================
  RUNNING T-006 CONTRACT CONSISTENCY & IMPLEMENTATION-SAFETY VERIFIER
  ================================================================================
  [PASS] Case 1: All 34 raw columns match canonical names and physical order.
  [PASS] Case 2: All 9 fabricated columns removed; 9 restored canonical columns verified.
  [PASS] Case 3: Physical order and audited raw dtypes agree with schema_YYYY.json evidence.
  [PASS] Case 4: KPI-01..08 IDs, submetrics, and formulas agree with KPI_SPEC.md.
  [PASS] Case 5: KPI-03 verified as Signed Mean ARR_DELAY (negative delay preserved, not late rate).
  [PASS] Case 6: KPI-02/04 verified as Late Rate >= 15.0 (boundary 15.0 included, not on-time rate).
  [PASS] Case 7: Metric-valid denominators N_valid independent across submetrics; ZERO_METRIC_DENOMINATOR enforced.
  [PASS] Case 8: No CANCELLED or DIVERTED references in CORE filters.
  [PASS] Case 9: TS-012/013/015/016/020 match authoritative TEST_PLAN.md specifications.
  [PASS] Case 10: G2-EXC-001 verified as provisional unit status with G5 TS-018 mandatory hard stop blocking G6.
  [PASS] Case 11: Gate G2 confirmed PASS; Gate G3 confirmed IN_PROGRESS / NOT_PASSED; T-006 confirmed IN_PROGRESS.
  [PASS] Case 12: Downstream G4 tasks (T-009, T-007, T-008) verified NOT_STARTED.
  [PASS] Case 13: DC-11/12 row accounting and Record vs Metric Validity verified (metric invalidity does not quarantine flight).
  [PASS] Case 14: Complete finite numeric predicate verified with explicit NaN and Inf handling for all 7 CORE measures.
  [PASS] Case 15: Safe 7-step Windows NTFS publication order and TS-013 fault injection verified.
  [PASS] Case 16: Raw schema boundary verified (nullable Int64 calendar fields, anchored date regex, no unapproved NOT_NULL).
  [PASS] Case 17: Safe non-destructive rollback policy verified (destructive Remove-Item commands superseded and revoked).
  [PASS] Mutation Suite: 16 isolated mutation tests successfully detected and rejected.
  ================================================================================
  VERIFICATION SUMMARY: 17 INVARIANTS PASS, 16 MUTATIONS PASS, 0 FAIL
  ================================================================================
  ALL T-006 CONTRACT CONSISTENCY & IMPLEMENTATION-SAFETY CHECKS PASSED.
  ```

### 4.2. Bộ Kiểm Thử Tính Nhất Quán Cây Làm Việc Toàn Repository (Suite 2)
- **Lệnh chạy:** `python tools/check_working_tree_consistency.py`
- **Exit Code:** `0`
- **Kết quả:** Toàn bộ cấu trúc thư mục, liên kết markdown, tệp nguồn bất biến, sống và sổ đăng ký đều khớp 100%.

### 4.3. Bộ Kiểm Thử Hồi Quy Sổ Đăng Ký Working-Tree (Suite 3)
- **Lệnh chạy:** `python tools/qa/test_working_tree_registry_regression.py`
- **Exit Code:** `0`
- **Kết quả:** `ALL WORKING-TREE REGISTRY REGRESSION TESTS PASSED (16/16 fixtures ok).`

### 4.4. Bộ Kiểm Thử Bất Biến Ngữ Nghĩa Gate G2 (Suite 4)
- **Lệnh chạy:** `python tools/qa/verify_g2_repo_apply_r1_semantic_invariants.py`
- **Exit Code:** `0`
- **Kết quả:** `ALL G2 SEMANTIC INVARIANTS VERIFIED SUCCESSFULLY (32 checks passed, 0 failed).`

### 4.5. Bộ Kiểm Thử Hợp Đồng T-003 & Oracle Số Học (Suite 5)
- **Lệnh chạy:** `python tools/qa/verify_t003_contract_consistency.py`
- **Exit Code:** `0`
- **Kết quả:** `VERIFICATION SUMMARY: 133 PASS, 0 FAIL.`

### 4.6. Bộ Kiểm Thử Biểu Diễn Thời Gian T-004 (Suite 6)
- **Lệnh chạy:** `python tools/qa/verify_t004_time_representation.py`
- **Exit Code:** `0`
- **Kết quả:** `VERIFICATION SUMMARY: 90 PASS, 0 FAIL.`

---

## 5. Danh Mục Artifacts & Bảng Băm Mật Mã (Cryptographic Deliverables Inventory)

Toàn bộ các tệp tài liệu sửa đổi và kiểm thử trong chu trình closeout này được ghi nhận mã băm mật mã SHA-256 bất biến:

| Đường dẫn Tệp | Bản chất / Phân loại | Kích thước (Bytes) | Mã băm SHA-256 | Trạng thái Đăng ký |
| :--- | :--- | :---: | :--- | :--- |
| [`docs/02-design/ARCHITECTURE.md`](../02-design/ARCHITECTURE.md) | Living Architecture Document | 21,056 | `14cf55d04468149886bec7d6102228240f98bdb07305b7282073bd71608fa6a6` | Cập nhật trong `governed_living_docs` |
| [`docs/05-evidence/T006_FINAL_CORRECTIONS_ADDENDUM.md`](T006_FINAL_CORRECTIONS_ADDENDUM.md) | Design Addendum (`AUDIT_REPORT`) | 22,420 | `9966159e5d8aecc2f3bc786faacd22c72d02568e37b4b80e40c5faaa14c87304` | Đăng ký mới trong `registered_deliverables` |
| [`docs/05-evidence/T006_FINAL_CONTRACT_VERIFICATION.md`](T006_FINAL_CONTRACT_VERIFICATION.md) | Gate Review Report (`AUDIT_REPORT`) | *Xem sổ đăng ký* | *Xem sổ đăng ký* | Đăng ký mới trong `registered_deliverables` |
| [`tools/qa/verify_t006_contract_consistency.py`](../../tools/qa/verify_t006_contract_consistency.py) | Contract QA Script (`TEST_SUITE`) | 35,369 | `3fd84d5294665e506e5e1fd3ec41480e4c51fd7cc98a56297ddfe0746424b698` | Cập nhật trong `registered_deliverables` |

---

## 6. Kết Luận & Tuyên Bố Sẵn Sàng Nghiệm Thu (Gate Readiness Assessment)

### 6.1. Đánh giá Mức độ Hoàn thành (DoD Assessment)
- [x] **DC-11/12:** Đã phân định rạch ròi ba trạng thái dòng và Record Validity vs. Metric Validity.
- [x] **Vị từ số thực:** Đã đặc tả đầy đủ hàm `is_finite_numeric` và ma trận synthetic fixtures cho 7 trường đo.
- [x] **Xuất bản an toàn:** Đã thiết lập quy trình 7 bước trên Windows NTFS và kịch bản tiêm lỗi `TS-013`.
- [x] **Hoàn nguyên an toàn:** Đã hủy bỏ hoàn toàn các hướng dẫn xóa tệp hủy hoại, xác lập nguyên tắc bảo tồn bằng chứng.
- [x] **Dữ liệu thô:** Đã bảo tồn tính nullable của cột lịch theo `DATA_DICTIONARY.md` và kiểm tra ngày bằng anchored regex.
- [x] **Kiểm thử tự động:** Toàn bộ 6 test suites đạt PASS 100%, bộ test T-006 đạt 17 Invariants PASS và 16 Mutations PASS.

### 6.2. Trạng thái Đề xuất Nghiệm thu
Hồ sơ kỹ thuật Gate G3 / Task T-006 đã đạt mức độ hoàn thiện, chặt chẽ và an toàn cao nhất, chính thức tuyên bố:
$$\mathbf{READY\_FOR\_T006\_HUMAN\_SIGNOFF}$$

**Các Ràng Buộc Tiếp Theo:**
- Không tự ý phê duyệt `Gate G3 = PASS`. Việc đóng cổng Gate G3 hoàn toàn thuộc thẩm quyền của Project Lead.
- Giữ nguyên các nhiệm vụ Gate G4 (`T-009`, `T-007`, `T-008`) ở trạng thái **`NOT_STARTED`** cho đến khi có lệnh bằng văn bản chính thức từ Project Lead.
