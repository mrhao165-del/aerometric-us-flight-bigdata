# T-009 RISK, DEVIATION AND STRUCTURAL CONFLICT REPORT

**Task ID:** `T-009`  
**Gate:** `G4`  
**Auditor:** Senior Big Data Software Architect & Lead Governance Engineer  
**Timestamp:** 2026-10-17T08:03:00+07:00  
**Normalized Placement:** `docs/05-evidence/T009_RISK_AND_DEVIATION_REPORT.md` (Flat Canonical Layout per Project Lead T009-UNBLOCK-R1 Directive)  
**Status:** `ACTIVE_RISKS_CATALOGED / STRUCTURAL_CONFLICT_DISCLOSED`  

---

## 1. Trạng Thái Các Rủi Ro Vận Hành & Dự Án Mở (Active Open Risks)

Toàn bộ các rủi ro vận hành `OR-01..OR-08` tiếp tục được theo dõi chặt chẽ và đối chiếu chuẩn tắc theo [`docs/03-quality/RISK_REGISTER.md`](../03-quality/RISK_REGISTER.md):

| Mã Rủi Ro | Mã Dự Án | Trạng Thái Quản Trị | Bản Chất & Tác Động Tới Nhiệm Vụ T-009 | Chiến Lược Giảm Thiểu / Ràng Buộc |
|:---:|:---:|:---:|---|---|
| **`OR-01`** | **`R-09`** | `MITIGATED_BY_CONTRACT` | `FLIGHTS == 1.0` trên 100% dòng dữ liệu; không phản ánh số lần hủy hay gộp chuyến. | Tuân thủ `FP-DEC-010`: Cấm dùng `FLIGHTS` làm trọng số; mọi chỉ số dùng mẫu số bản ghi `count_records`. |
| **`OR-02`** | **`R-05`** (`R-09`, `R-13`) | `PRESERVED_AS_AUDITED` | Cặp bản ghi `YX 3624` (2018-06-21, DEN->XNA, dòng 6.384.132 & 6.384.133) trùng candidate key. | Tuyệt đối cấm deduplicate tùy tiện; thiết kế định danh dòng ổn định `TS-020` ở T-007. |
| **`OR-03`** | **`R-15`** | `PROVISIONAL_EXCEPTION` | Đơn vị 7 trường đo CORE mang nhãn `OFFICIAL_MINUTES_EMPIRICALLY_CONSISTENT_PROVISIONAL` theo ngoại lệ **`G2-EXC-001`**. | Bắt buộc bài kiểm thử **`TS-018` PHẢI PASS ở Gate G5/T-011** trước khi chạy G6; nếu FAIL sẽ chặn toàn bộ pipeline. |
| **`OR-04`** | **`R-01`** (`R-02`) | `CLOSED_OUT_OF_SCOPE` | CSV thô 34 cột không có trường `CANCELLED` hoặc `DIVERTED`. | Khóa phạm vi: Cấm tính tỷ lệ hủy/chuyển hướng (`KPI-11 = NOT_COMPUTABLE`, `TS-009`). |
| **`OR-05`** | **`R-10`** | `OPEN_QUALITY_DEFECT` | Dữ liệu năm 2024 chỉ có **335 / 366 ngày** (khuyết hoàn toàn 31 ngày Tháng 3/2024). | Gán nhãn `source_coverage_status = PARTIAL` (`DC-12`); cấm tự tạo bản ghi 0 chuyến bay; nghiệm thu `TS-004` ở G6. |
| **`OR-06`** | **`R-03`** | `MITIGATED_BY_CONTRACT` | Chuyến bay qua đêm có `ARR_TIME < DEP_TIME`; mốc 24:00; múi giờ địa phương. | Tuân thủ `FP-DEC-007`: Cấm trừ chuỗi timestamp, cấm tự động cộng 24h (`TS-010`); dùng trường thời lượng có sẵn của BTS. |
| **`OR-07`** | **`R-04`** | `MITIGATED_BY_SCOPE_EXCLUSION` | Đơn vị, join và provenance của 6 cột thời tiết thô chưa được chứng thực. | Đã phê duyệt `FP-DEC-017` (`CONDITIONAL_NO_GO`); loại bỏ `RQ-06`/`KPI-10`; giữ nguyên 6 cột thời tiết thô trong schema; cấm quarantine dòng CORE vì thiếu thời tiết. |
| **`OR-08`** | **`R-16`** | `IDENTITY_UNVERIFIED` | Danh tính tệp CSV nguồn 14.15 GiB chỉ mới đối khớp metadata (`METADATA_MATCH_ONLY`). | Chuyển giao sang `G4/T-007` (`TS-019`) để tính mã băm SHA-256 cục bộ cho cả 9 tệp CSV nguồn. |

---

## 2. Phát Hiện Xung Đột Cấu Trúc Kiểm Toán Cây Làm Việc (Working-Tree Validator Conflict)

Trong quá trình preflight và rà soát các công cụ kiểm toán hiện hành, AI Agent đã phát hiện một xung đột cấu trúc quan trọng giữa **Đề xuất đóng gói của Prompt T-009** và **Bộ kiểm tra tính nhất quán đã được phê duyệt (`tools/check_working_tree_consistency.py`)**:

### Chi tiết xung đột kỹ thuật:
1. **Yêu cầu trong Prompt T-009:**
   - Yêu cầu thiết lập thư mục gốc bằng chứng riêng biệt: `EVIDENCE_ROOT = docs/05-evidence/T009/`.
   - Yêu cầu xuất toàn bộ báo cáo vào thư mục con này (ví dụ: `01_DOCUMENT_READING_AND_AUTHORITY_AUDIT.md`, `02_BASELINE_AND_SCOPE_REPORT.md`,...).
2. **Quy tắc cứng trong `tools/check_working_tree_consistency.py`:**
   - Tại dòng 495:
     ```python
     elif dp.startswith("docs/05-evidence/") and "/" not in dp[len("docs/05-evidence/"):]:
         loc_ok = bool(EVIDENCE_FILENAME_RE.match(fname))
     ```
   - Script hiện hành chỉ chấp nhận các tệp bằng chứng nằm **trực tiếp** dưới thư mục `docs/05-evidence/` và khớp biểu thức chính quy `EVIDENCE_FILENAME_RE = re.compile(r"^(?:T0(?:0[1-9]|1[0-7])|G[0-7])_[A-Za-z0-9_.\-]+\.(?:md|csv|json|txt)$")`.
   - Các thư mục con duy nhất được phép trong `docs/05-evidence/` là các thư mục sao lưu (`G2_REPO_APPLY_BACKUPS/`, `G2_FINAL_FIX_BACKUPS/`, `G2_OFFICIAL_SIGNOFF_BACKUPS/`, `T006_BACKUPS/`, `T006_R1_BACKUPS/`).
   - Mọi tệp tạo trong `docs/05-evidence/T009/` sẽ bị bộ kiểm tra coi là **`unrecognized stray file`** (Mục 14, dòng 583), làm script trả về **Exit Code 1 (FAIL)**!
3. **Quy định giải quyết xung đột tại Mục 6 của Prompt T-009:**
   > *"Nếu có xung đột giữa schema registry và cách đóng gói evidence đề xuất, ưu tiên schema đang được phê duyệt hoặc STOP để xin quyết định."*

### Đề xuất xử lý trình Project Lead:
- **Lựa chọn A (Khuyến nghị để tương thích 100% validator hiện tại — Đã được Project Lead chọn trong T009-UNBLOCK-R1):** Sử dụng quy ước đặt tên phẳng truyền thống trực tiếp dưới `docs/05-evidence/`:
  - `T009_DOCUMENT_READING_AND_AUTHORITY_AUDIT.md` (nằm trực tiếp tại `docs/05-evidence/`)
  - `T009_BASELINE_AND_SCOPE_REPORT.md` (nằm trực tiếp tại `docs/05-evidence/`)
  - `T009_RISK_AND_DEVIATION_REPORT.md` (nằm trực tiếp tại `docs/05-evidence/`)
  - `T009_FINAL_REVIEW.md` (nằm trực tiếp tại `docs/05-evidence/`)
  - ... (khớp biểu thức `T009_*.md` và đăng ký được vào `EVIDENCE_DELIVERABLE_REGISTER.json`).
- **Lựa chọn B:** Project Lead ban hành chỉ thị cập nhật `tools/check_working_tree_consistency.py` để bổ sung quy tắc cho phép thư mục con `docs/05-evidence/T009/` và đăng ký trong registry schema v1.1.

---

## 3. Khuyết Tật Môi Trường Đã Được Khắc Phục Trong Thiết Kế (Known Environment Defect)

- **Hiện tượng:** Biến môi trường hệ thống `PYSPARK_PYTHON` và `PYSPARK_DRIVER_PYTHON` trỏ vào một đường dẫn không tồn tại: `D:\Study\Code\Apache\ApacheSpark\.venv\Scripts\python.exe`.
- **Hậu quả:** Khi Spark khởi tạo tiến trình worker Python, JVM sẽ ném ngoại lệ:
  `java.io.IOException: Cannot run program "D:\Study\Code\Apache\ApacheSpark\.venv\Scripts\python.exe": CreateProcess error=2, The system cannot find the file specified`.
- **Giải pháp thiết kế:**
  Trong module `flight_pipeline.utils.spark_session`, tiến trình sẽ tự động gán đè:
  ```python
  import os, sys
  os.environ["PYSPARK_PYTHON"] = sys.executable
  os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable
  ```
  Giải pháp này đã được kiểm nghiệm thực tế và hoàn toàn thành công mà không cần can thiệp sửa đổi biến môi trường vĩnh viễn của Windows.

---

## 4. Tuyên Bố Độ Lệch & Tình Trạng Dừng (Deviation & Stop Statement)

- **Không có độ lệch tự ý:** AI Agent không tự ý điều chỉnh phạm vi, không tự ý sửa code, không tạo code trong trạng thái thiếu Git.
- **Tuân thủ điều kiện dừng tối cao:** Dừng triển khai mã nguồn ngay tại ranh giới tiền kiểm toán theo lệnh chỉ thị `GIT_MODE = REQUIRE_EXISTING_VERIFIED_BASELINE`.
