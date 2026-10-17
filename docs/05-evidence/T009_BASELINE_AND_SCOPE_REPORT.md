# T-009 BASELINE, SCOPE & MANDATORY STOP BLOCKER REPORT

**Task ID:** `T-009`  
**Gate:** `G4`  
**Auditor:** Senior Big Data Software Architect & Lead Governance Engineer  
**Timestamp:** 2026-10-17T08:02:00+07:00  
**Normalized Placement:** `docs/05-evidence/T009_BASELINE_AND_SCOPE_REPORT.md` (Flat Canonical Layout per Project Lead T009-UNBLOCK-R1 Directive)  
**Status:** `BLOCKED — MANDATORY STOP TRIGGERED (MISSING GIT BASELINE)`  

---

## 1. Tóm Tắt Tình Trạng Kích Hoạt Lệnh Dừng (Executive Summary)

Theo ủy quyền thực thi nhiệm vụ `T-009` từ Project Lead:
```text
TASK_TO_IMPLEMENT = T-009
TEST_RUNNER = unittest
DEPENDENCY_INSTALLATION = NOT_AUTHORIZED
GIT_MODE = REQUIRE_EXISTING_VERIFIED_BASELINE
SPARK_SCRATCH = D:/Study/Code/Apache/Flight_Analyzt/tmp_spark/
GATE_PASS_AUTHORITY = PROJECT_LEAD_ONLY
NEXT_TASK_EXECUTION = PROHIBITED
EVIDENCE_ROOT = docs/05-evidence/T009/
```

Và các điều kiện ràng buộc tối cao tại Mục 0 và Mục 2 của lệnh:
> *"Nếu repository không có Git baseline, phải STOP trước khi sửa code và yêu cầu Project Lead quyết định. Không tự chuyển sang chế độ non-Git."*  
> *"Nếu GIT_MODE = REQUIRE_EXISTING_VERIFIED_BASELINE mà chưa có Git baseline, xuất báo cáo blocker vào docs/05-evidence/T009/ và STOP."*  
> *"Một ngoại lệ non-Git chỉ được phép khi Project Lead ban hành quyết định riêng, ghi rõ phạm vi, phương án backup và cách xác minh rollback."*

Qua kiểm tra trực tiếp và khách quan trên filesystem của Live Repository:
1. **Kiểm tra thư mục `.git`:** Lệnh `Test-Path .git` trả về **`False`**. Lệnh `Test-Path ..\.git` trả về **`False`**.
2. **Hiện trạng Git:** Repository hiện tại **HOÀN TOÀN CHƯA ĐƯỢC KHỞI TẠO GIT (`NO_GIT_REPOSITORY`)**.
3. **Hành động tuân thủ:** AI Agent **LẬP TỨC KÍCH HOẠT ĐIỀU KIỆN DỪNG (`MANDATORY STOP`)**, tuyệt đối **KHÔNG** tạo mới hay sửa đổi bất kỳ tệp mã nguồn nào trong `src/` hoặc `tests/`, không tự động chuyển sang chế độ non-Git, và xuất báo cáo Blocker này vào bằng chứng T-009 để trình Project Lead quyết định.

---

## 2. Ma Trận Môi Trường & Hạ Tầng Đo Lường Thực Tế (Measured Environment Matrix)

| Thành phần | Đường dẫn / Phiên bản quan sát thực tế | Trạng thái kỹ thuật | Đánh giá tính tương thích với T-009 |
|---|---|:---:|---|
| **Repository Root** | `D:\Study\Code\Apache\Flight_Analyzt\US_FLIGHT_PERFORMANCE_DOCS_V1` | `EXISTS` | Đúng workspace được chỉ định. |
| **Git Baseline** | `.git` (Không tồn tại trước khi chạy T009-UNBLOCK-R1) | **`MISSING (BLOCKER)`** | **Vi phạm điều kiện `GIT_MODE = REQUIRE_EXISTING_VERIFIED_BASELINE`.** |
| **Python Runtime** | `3.10.11 (tags/v3.10.11:7d4cc5a, Apr 5 2023, 00:38:17)` tại `C:\Users\Heikapu\AppData\Local\Programs\Python\Python310\python.exe` | `VERIFIED` | Tương thích hoàn hảo với PySpark 4.0.1 và PyArrow 25.0.1. |
| **Java Runtime** | `OpenJDK 21.0.12.1 LTS` (Eclipse Adoptium Temurin 64-bit) tại `C:\Program Files\Eclipse Adoptium\jdk-21.0.12.101-hotspot` | `VERIFIED` | `JAVA_HOME` hợp lệ; Spark 4.0.1 hỗ trợ chính thức Java 21 LTS. |
| **PySpark** | `4.0.1` | `VERIFIED` | Đã cài đặt trong Python 3.10 global site-packages. |
| **PyArrow** | `25.0.1` | `VERIFIED` | Hỗ trợ tối ưu hóa Spark Arrow serialization. |
| **Pandas** | `2.3.3` | `VERIFIED` | Sẵn sàng cho conversion nhỏ khi kiểm thử. |
| **Test Runner** | `unittest` (Standard Library) | `VERIFIED` | `python -m unittest discover -s tests` khả dụng 100%, zero-dependency. |
| **Công cụ Lint** | `flake8`, `black`, `ruff`, `pytest` | `NOT_INSTALLED` | Chưa cài đặt; không được tự cài khi chưa có phê duyệt. |
| **Hệ thống tệp & Staging** | Phân vùng `D:` có **64.26 GiB** khả dụng; Phân vùng `C:` có **26.59 GiB** | `VERIFIED` | Scratch path `D:/Study/Code/Apache/Flight_Analyzt/tmp_spark/` an toàn, tránh đầy ổ C. |
| **Biến môi trường PySpark** | `PYSPARK_PYTHON` & `PYSPARK_DRIVER_PYTHON` trỏ sai đường dẫn ảo `D:\Study\Code\Apache\ApacheSpark\.venv\Scripts\python.exe` (không tồn tại) | `KNOWN_DEFECT (RESOLVED IN CODE DESIGN)` | Đã kiểm chứng giải pháp inject `sys.executable` trong process scope của Spark session factory, không sửa registry Windows. |

---

## 3. Xác Minh Trạng Thái Quản Trị Dự Án Hiện Hành

Kiểm tra đối chiếu trực tiếp giữa các tài liệu quản trị sống:
- `docs/04-execution/PROJECT_STATE.md`:
  - `G0 = DESIGN_BASELINE`
  - `G1 = PARTIAL`
  - `G2 = PASS` (Phê duyệt chính thức ngày 2026-10-16, `G2_OFFICIAL_SIGNOFF_HUMAN_ACCEPTANCE_RECORD.md`)
  - `G3 = PASS` (Phê duyệt chính thức ngày 2026-10-17, `G3_OFFICIAL_SIGNOFF_HUMAN_ACCEPTANCE_RECORD.md`)
  - `T-006 = PASS / COMPLETED`
  - `T-009_ENTRY_GATE = READY`
  - `G4 (T-009, T-007, T-008) = NOT_STARTED`
  - `G5, G6, G7 = NOT_STARTED`
- `docs/01-planning/BACKLOG.md`:
  - `T-009 = TODO`
  - `T-007 = TODO` (Bị khóa bởi T-009)
  - `T-008 = TODO` (Bị khóa bởi T-007)

**Kết luận:** Trạng thái thực tế trên đĩa hoàn toàn khớp với hợp đồng quản trị. Cổng mở vào T-009 đã `READY`, nhưng việc triển khai mã nguồn bị chặn bởi điều kiện thiếu Git baseline.

---

## 4. Hiện Trạng Cấu Trúc Mã Nguồn & Thư Mục

1. **`src/`:** Chưa tồn tại (`Test-Path src` $\implies$ `False`). Chưa có bất kỳ dòng code pipeline nào.
2. **`tests/`:** Chưa tồn tại (`Test-Path tests` $\implies$ `False`).
3. **`tools/`:** Tồn tại đầy đủ 11 kịch bản kiểm tra chất lượng và kiểm toán cây làm việc (đạt 363/363 PASS assertions trên `check_working_tree_consistency.py` và 17/17 + 16/16 PASS trên `verify_t006_contract_consistency.py`).
4. **`data/raw/tabular/{year}/flight_with_weather_{year}.csv`:** 9 tệp CSV nguồn tồn tại đầy đủ, kích thước 15.196.366.173 bytes (14,15 GiB), 54.674.003 hàng, tuyệt đối nguyên vẹn và bất biến.

---

## 5. Ranh Giới Phạm Vi Nhiệm Vụ T-009 (Scope Boundary)

### 5.1. Những việc thuộc phạm vi T-009 (Sẽ thực thi ngay khi Project Lead gỡ Blocker):
1. Thiết lập gói Python chuẩn:
   ```text
   src/
     flight_pipeline/
       __init__.py
       config/
         __init__.py
         spark_config.py
       utils/
         __init__.py
         spark_session.py
         manifest.py
       quality/
         __init__.py
         predicates.py
       storage/
         __init__.py
         publication.py
   tests/
     __init__.py
     test_environment.py
     test_predicates.py
     test_publication.py
     test_manifest.py
   ```
2. Khởi tạo `SparkSession` với cấu hình an toàn cho Windows 10, Java 21, PySpark 4.0.1:
   - Tự động override `os.environ["PYSPARK_PYTHON"] = sys.executable` và `os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable`.
   - Cấu hình scratch `spark.local.dir` trỏ về `D:/Study/Code/Apache/Flight_Analyzt/tmp_spark/`.
   - Đảm bảo driver khởi tạo và dừng sạch sẽ không để lại rác bộ nhớ hay tiến trình zombie.
3. Hiện thực hóa vị từ số học hữu hạn đầy đủ `is_finite_numeric` (G3-COND-B):
   - Xử lý triệt để 7 ca biên: `null`, `NaN`, `+inf`, `-inf`, `0.0`, số âm hữu hạn, số dương hữu hạn.
   - Bảo toàn delay âm và phân định rõ ràng giữa Record Validity và Metric Validity.
4. Hiện thực hóa cơ chế xuất bản an toàn 7 bước trên Windows NTFS (G3-COND-C):
   - Sử dụng cơ chế pointer file nguyên tử qua `os.replace`.
   - Đảm bảo khi gặp lỗi (fault injection), con trỏ hợp lệ cũ không bị hỏng và không để lộ dữ liệu bán phần.
5. Xây dựng khung `RunManifest` và logging theo dõi lần chạy.
6. Cấu hình CI skeleton và thực thi toàn bộ test qua `python -m unittest discover -s tests`.

### 5.2. Những việc TUYỆT ĐỐI BỊ CẤM trong T-009:
- Cấm đọc nạp dữ liệu thật 9 năm từ `data/raw/` (thuộc T-007).
- Cấm thực hiện phân loại hạch toán 3 trạng thái trên toàn bộ dữ liệu (thuộc T-008).
- Cấm tính toán 8 CORE KPIs trên dữ liệu thật (thuộc Gate G5/G6).
- Cấm xây dựng mô hình dự báo ML, mạng đồ thị chuyến bay, hoặc nạp file `.pt`.
- Cấm tính toán chỉ số thời tiết hoặc vẽ biểu đồ thời tiết (bảo lưu `FP-DEC-017` CONDITIONAL_NO_GO).
- Cấm chỉnh sửa công thức KPI hoặc các hợp đồng dữ liệu DC-01..12.

---

## 6. Đề Xuất Giải Quyết Blocker Để Trình Project Lead

Để gỡ bỏ trạng thái `BLOCKED` và bắt đầu triển khai code T-009, kính đề nghị Project Lead lựa chọn một trong hai phương án sau:

### Phương án 1 (Khuyến nghị chuẩn mực): Project Lead thiết lập Git Baseline
Project Lead mở terminal tại thư mục dự án và thực hiện:
```powershell
cd D:\Study\Code\Apache\Flight_Analyzt\US_FLIGHT_PERFORMANCE_DOCS_V1
git init
git add .
git commit -m "feat: baseline repository snapshot at Gate G3 PASS (T-009 entry readiness)"
```
Sau khi hoàn tất lệnh trên, AI Agent sẽ xác nhận Git baseline hợp lệ và tiến hành triển khai mã nguồn T-009 ngay lập tức theo đúng `GIT_MODE = REQUIRE_EXISTING_VERIFIED_BASELINE`.

### Phương án 2: Project Lead ban hành Quyết định Ngoại lệ Non-Git (Non-Git Exception Directive)
Nếu Project Lead muốn tiếp tục triển khai mà chưa cần Git, Project Lead ban hành chỉ thị chính thức bằng văn bản cho phép:
- Chuyển `GIT_MODE = NON_GIT_WITH_VERIFIED_BACKUPS`.
- Áp dụng cơ chế tạo snapshot sao lưu `.bak` toàn diện trước khi sửa đổi bất kỳ tệp tài liệu quản trị nào (`BACKLOG.md`, `PROJECT_STATE.md`, `CHANGELOG.md`).
- Lưu trữ mọi tệp mã nguồn mới tạo vào bảng kê hash có chữ ký xác thực.
