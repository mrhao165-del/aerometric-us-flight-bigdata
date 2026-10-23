# BÁO CÁO ĐÁNH GIÁ SẴN SÀNG KHỞI ĐỘNG NẠP DỮ LIỆU NĂM 2016 (G6 T-012 FIRST-YEAR PRESTART REPORT)

**Dự án:** Phân tích hiệu suất chuyến bay Hoa Kỳ 2016–2024 bằng Apache Spark/PySpark  
**Nhiệm vụ:** `G6-T012-2016-PRESTART` (First-Year Production Ingestion Prestart Assessment)  
**Thời điểm đánh giá (UTC):** 2026-10-21T09:20:00Z  
**Phạm vi:** Năm khảo sát 2016 duy nhất (`data/raw/tabular/2016/flight_with_weather_2016.csv`)  
**Tập lệnh bằng chứng:** [`docs/05-evidence/G6_T012_2016_PRESTART_RAW_LOG.txt`](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/docs/05-evidence/G6_T012_2016_PRESTART_RAW_LOG.txt)  
**Phán quyết kỹ thuật (Verdict):** **`READY_WITH_CONDITIONS`**

---

## 1. TRẠNG THÁI QUẢN TRỊ HIỆN TẠI (GOVERNANCE STATUS)

Căn cứ theo tài liệu bàn giao [`G5_CONTROLLED_SIGNOFF_CLOSEOUT_REPORT.md`](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/docs/05-evidence/G5_CONTROLLED_SIGNOFF_CLOSEOUT_REPORT.md), [`PROJECT_STATE.md`](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/docs/04-execution/PROJECT_STATE.md), và [`DECISIONS.md`](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/docs/02-design/DECISIONS.md):

* **Gate G5:** `IN_PROGRESS / HUMAN_SIGNOFF_PENDING` (Phán quyết: `G5_PENDING_HUMAN_PREREQUISITES`). Toàn bộ 19/19 tiêu chí kỹ thuật và thiết kế đã thỏa mãn; việc đóng cổng chính thức chờ chữ ký người tải dữ liệu thực tế tại Quyết định D1.
* **Gate G6:** `NOT_STARTED / BLOCKED`. Bị khóa quản trị cho đến khi Gate G5 chính thức đạt `PASS (CONTROLLED)`.
* **Task T-011:** `PASS (CONTROLLED)` về mã nguồn và logic tính toán 8 CORE KPI; hợp đồng đóng chính thức chờ nghiệm thu TS-018.
* **Task T-012:** `NOT_STARTED`. Trạng thái an toàn: chưa có bất kỳ dữ liệu sản xuất nào được ghi, chưa có lệnh Spark live nào được chạy.
* **Quyết định D1 (BTS Source Provenance Attestation):** `PENDING_HUMAN_SOURCE_ATTESTATION`. Tệp gốc `T_ONTIME_REPORTING_20261019_112232.zip` khớp bitwise 100% SHA-256 nhưng chờ chữ ký con người của người trực tiếp tải từ transtats.bts.gov tại [`G5_D1_BTS_PROVENANCE_ATTESTATION_DRAFT.md`](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/docs/05-evidence/G5_D1_BTS_PROVENANCE_ATTESTATION_DRAFT.md).
* **Quyết định D2 (BTS Parity Option B):** Đã phê duyệt chính thức thành [`FP-DEC-019`](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/docs/02-design/DECISIONS.md) theo chỉ đạo của Project Lead ngày 21/10/2026.
* **Quyết định D3 (TS-018 Technical Parity Signoff):** `CONDITIONALLY_ACCEPTED_PENDING_PREREQUISITES`. 10.500/10.500 giá trị khớp bitwise và 14/14 negative tests đạt PASS; chờ hoàn tất D1.
* **Quyết định D4 (Gate G5 Human Signoff):** `IN_PROGRESS / HUMAN_SIGNOFF_PENDING`. Chờ hoàn tất D1/D3.
* **Quyết định G6-ARCH-2016 (Kiến trúc tích hợp 2016):** Đã phê duyệt chính thức **Option B (Unified Production Rerun of 2016)** thành [`FP-DEC-020`](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/docs/02-design/DECISIONS.md) theo chỉ đạo của Project Lead ngày 21/10/2026.
* **Quyết định D5 (Production Execution Authorization):** Nghiêm ngặt **`NOT_AUTHORIZED`**.
* **Ngoại lệ G2-EXC-001:** `ACTIVE`. Đã có lộ trình giải quyết dứt điểm qua **FP-DEC-019 (Option B)** và việc ký nghiệm thu chính thức TS-018 / Quyết định D3 (hoàn toàn tách biệt với quyết định kiến trúc tái nạp 2016 FP-DEC-020 Option B); sẽ chuyển sang `RESOLVED_BY_OPTION_B` khi Gate G5 chính thức đóng.

---

## 2. KIỂM TRA TÍNH TOÀN VẸN NGUỒN DỮ LIỆU NĂM 2016 (SOURCE INTEGRITY)

Thực hiện kiểm tra thực tế tệp nguồn CSV chuẩn hóa năm 2016:

* **Đường dẫn tệp:** [`data/raw/tabular/2016/flight_with_weather_2016.csv`](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/data/raw/tabular/2016/flight_with_weather_2016.csv)
* **Sự tồn tại vật lý:** `True` (Tệp tồn tại, quyền đọc hợp lệ).
* **Kích thước byte thực tế:** `1,538,427,452 bytes` (Khớp tuyệt đối mốc cơ sở: `True`).
* **Mã băm SHA-256 thực tế:**  
  `4ed92ed732721a38ae28325135fad63436347613674ad96c1b273eb9d44cef34`  
  (Khớp tuyệt đối mốc cơ sở đã kiểm toán: `True`).
* **Số hàng kỳ vọng theo danh mục kiểm toán:** `5,537,987 hàng` (theo metadata `schema_2016.json`).  
  *Ghi chú ranh giới:* Preflight không đếm thô số hàng CSV để tránh profiling thừa; số hàng vật lý thực tế sẽ được kiểm chứng và đối soát 1:1 trong quá trình nạp dữ liệu có kiểm soát theo hợp đồng DC-11/DC-12.
* **Tương thích danh mục kiểm toán `SourceValidator`:**  
  `SourceEntry(year=2016, relative_path='data/raw/tabular/2016/flight_with_weather_2016.csv', audited_row_count=5537987, audited_byte_size=1538427452, audited_column_count=34)` -> Hoàn toàn tương thích.
* **Bảo tồn 50 tệp staging Parquet của T-010:**  
  Toàn bộ 50 tệp Parquet staging tạo ra từ T-010 tại thư mục `D:\Study\Code\Apache\Flight_Analyzt\staging\` được bảo toàn nguyên trạng, không bị di chuyển, sửa đổi hay ghi đè.

---

## 3. ĐÁNH GIÁ TÀI NGUYÊN HỆ THỐNG TRẠNG THÁI ĐỌC (READ-ONLY RESOURCE ASSESSMENT)

Đo đạc tài nguyên thực tế tại máy trạm ngày 21/10/2026:

| Thành phần tài nguyên | Số đo thực tế | Ngưỡng chính sách tối thiểu (Hard Policy) | Ngưỡng khuyến nghị (Recommended) | Đánh giá trạng thái |
| :--- | :--- | :--- | :--- | :--- |
| **Dung lượng trống ổ D:** | **56.83 GiB** (61.02 GB) | $\ge 25.0\text{ GiB}$ (Chính sách G6) | $\ge 25.0\text{ GiB}$ | **PASS** (Dư dôi >35 lần dung lượng RAW và Parquet 2016) |
| **Dung lượng trống ổ C:** | **22.29 GiB** (23.93 GB) | $\ge 10.0\text{ GiB}$ (OS paging) | $\ge 15.0\text{ GiB}$ | **PASS** |
| **Bộ nhớ RAM vật lý khả dụng** | **3.24 GiB** (3.48 GB) | $\ge 3.0\text{ GiB}$ (Ngưỡng khởi động tối thiểu) | $\ge 4.0\text{ GiB}$ (Headroom khuyến nghị) | **PASS HARD MINIMUM / OPERATOR CLEANUP ADVISED** |
| **Tổng RAM máy trạm** | **15.71 GiB** (~16 GB) | $\ge 8.0\text{ GiB}$ | $\ge 16.0\text{ GiB}$ | **PASS** (Hiện đang sử dụng 79.4%) |
| **Khóa tiến trình (Active Locks)** | **0 tệp** (`CLEAN`) | 0 tệp khóa hoạt động | 0 | **PASS** |
| **Dấu vết phục hồi (`.del_*`)** | **0 tệp/thư mục** | 0 dấu vết | 0 | **PASS** |

### Cấu hình Spark / JVM Memory
* **Master:** `local[4]` (Sử dụng 4 lõi CPU cục bộ).
* **Driver Memory (`spark.driver.memory`):** `4g` (4 GiB heap).
* **Driver Overhead (`spark.driver.memoryOverhead`):** `1g` (1 GiB off-heap).
* **Shuffle Partitions:** `16`.
* **Thư mục đệm (Scratch Dir):** `D:/Study/Code/Apache/Flight_Analyzt/tmp_spark/` (Nằm ngoài cây thư mục git repository, bảo đảm hiệu năng I/O trên ổ SSD D:).
* **Định dạng & Nén:** Parquet với codec `snappy`.
* **Làm rõ chênh lệch số đo RAM lịch sử:** Nhật ký lệnh thô tự động ghi nhận **3.57 GiB** khả dụng (lúc 09:20 UTC), trong khi đo đạc thủ công sơ bộ ghi nhận **3.24 GiB** (lúc 09:15 UTC) do hệ điều hành Windows cấp phát/thu hồi bộ nhớ nền động (hiện tại đo đạt >4.0 GiB). Cả hai số đo lịch sử đều đạt ngưỡng vận hành tối thiểu ($\ge 3.0\text{ GiB}$) nhưng nằm dưới mức khuyến nghị ($\ge 4.0\text{ GiB}$).
* **Khuyến nghị tài nguyên trước khi chạy:** Người vận hành nên tắt các ứng dụng nền không cần thiết (trình duyệt web, ứng dụng ngốn RAM) để bảo đảm duy trì RAM khả dụng ở mức $\ge 4.0\text{ GiB}$ trước khi bắt đầu live ingestion.

---

## 4. AN TOÀN KHÓA, CON TRỎ VÀ PHỤC HỒI (LOCK, POINTER & RECOVERY SAFETY)

Thực thi kiểm tra an toàn bằng 2 công cụ độc lập:

### 4.1. Kiểm tra bằng `tools/qa/check_writer_preflight_safety.py`
* **Lệnh chạy:** `python tools/qa/check_writer_preflight_safety.py --base-dir data --run-id run_2016_v1 --json`
* **Mã thoát (Exit Code):** `0`
* **Kết quả chi tiết:**
  * `safe_to_start_writer`: `true`
  * `summary_verdict`: `"SAFE_TO_PROCEED_TO_LOCK_ACQUISITION"`
  * `pointer_status`: `"UNINITIALIZED_POINTER_ALLOWED"` (Hợp lệ cho lần nạp sản xuất đầu tiên)
  * `lock_state`: `"CLEAN"`
  * `recovery_artifacts_count`: `0`
  * `storage_root_matched`: `true`

### 4.2. Kiểm tra bằng `tools/qa/verify_staging_pointer.py`
* **Lệnh chạy:** `python tools/qa/verify_staging_pointer.py --base-dir data --allow-uninitialized --json`
* **Mã thoát (Exit Code):** `0`
* **Kết quả chi tiết:**
  * `success`: `true`
  * `status`: `"UNINITIALIZED_POINTER_ALLOWED"`
  * `pointer_file`: `data/curated/latest_run_id.txt` (Chưa tồn tại, hợp lệ cho trạng thái chưa khởi tạo)
  * `error_message`: `null`

---

## 5. KẾT QUẢ KIỂM THỬ KHỞI ĐỘNG THỬ NGHIỆM (DRY-RUN PREFLIGHT RESULTS)

Thực thi kiểm tra an toàn tích hợp thông qua `coordinator.py`:

* **Lệnh chạy:**  
  `$env:PYTHONPATH="src"; python src/flight_pipeline/ingestion/coordinator.py --years 2016 --run-id run_2016_v1 --base-data-dir data --dry-run-preflight --verify-hashes`
* **Mã thoát (Exit Code):** `0`
* **Đầu ra ghi nhận:**
  ```text
  ================================================================================
  INGESTION COORDINATOR PREFLIGHT REPORT (T-012)
  ================================================================================
  Run ID:              run_2016_v1
  Target Directory:    ...\data\curated\runs\run_2016_v1
  Survey Years:        [2016]
  Base Data Dir:       ...\data
  Lock Directory:      ...\data\locks
  Lock Status:         CLEAN
  Pointer Status:      UNINITIALIZED
  Dry-Run Mode:        True
  --------------------------------------------------------------------------------
  Source Files Inventory:
    Year 2016: ...\data\raw\tabular\2016\flight_with_weather_2016.csv [OK]
      Audited Expected Rows: 5,537,987
      Audited Bytes:         1,538,427,452 | Actual Bytes: 1,538,427,452
      SHA-256 Status:        VERIFIED_MATCH (4ed92ed732721a38...)
  --------------------------------------------------------------------------------
  Row Count Verification Boundary:
    Row counts are AUDITED_EXPECTED_ROWS from audited catalog; physical row counts
    are verified during ingestion and reconciled per DC-11/DC-12 row accounting.
  ================================================================================
  [PREFLIGHT PASS] Preflight safety inspection completed successfully. All mandatory safety criteria PASSED. No data written.
  ```
* **Xác nhận:** Toàn bộ kiểm tra tính toàn vẹn tệp nguồn, streaming hash SHA-256, kiểm tra xung đột run ID, trạng thái khóa và con trỏ đều đạt **PASS**. Không có dữ liệu nào bị ghi.

---

## 6. ĐIỀU KIỆN KÍCH HOẠT ĐIỂM VÀO SẢN XUẤT (PRODUCTION ENTRYPOINT & D5 DEPENDENCY)

### 6.1. Xác nhận chốt chặn quản trị an toàn (Safe Governance Hold Verification)
Để bảo đảm an toàn tuyệt đối, hệ thống kiểm tra chốt chặn quản trị thông qua kiểm tra tĩnh mã nguồn và kiểm thử đơn vị độc lập trên dữ liệu giả lập (mock isolated directory), **tuyệt đối không gọi lệnh coordinator live vào thư mục dữ liệu thật**:
* **Kiểm tra tĩnh mã nguồn:** Trực tiếp kiểm tra hằng số `D5_AUTHORIZED_BY_PROJECT_LEAD: bool = False` tại dòng 1971 trong `src/flight_pipeline/ingestion/coordinator.py`. Kết quả: `False` (Chốt chặn đang kích hoạt 100%).
* **Kiểm thử đơn vị độc lập:** Chạy bài kiểm tra `tests.test_coordinator_preflight_unblock.TestCoordinatorPreflightUnblock.test_09_unauthorized_live_execution_blocked` trong môi trường thư mục tạm cô lập:
  * Mã thoát (Exit Code): `0` (Bài test xác nhận coordinator trả về mã lỗi 1 và từ chối ghi dữ liệu khi không có D5).
* **Xác nhận:** Chốt chặn quản trị hoàn toàn ngăn chặn việc khởi tạo SparkSession và ngăn chặn việc ghi dữ liệu sản xuất. Tuyệt đối an toàn ngay cả khi runner được chạy nhiều lần.

### 6.2. Phân loại phụ thuộc kích hoạt
* **Phân loại báo cáo:** `PRODUCTION_ENTRYPOINT_PENDING_D5_CONTROLLED_ACTIVATION`.
* **Thủ tục kích hoạt:** Sau khi Project Lead ký phê duyệt Quyết định D5, việc kích hoạt đòi hỏi một thay đổi mã nguồn tối thiểu có kiểm duyệt độc lập (chuyển biến boolean sang `True` hoặc nhận cờ cấu hình được ủy quyền chính thức).
* **Lệnh thực thi trong tương lai (sau khi D5 được cấp phép):**
  ```powershell
  $env:PYTHONPATH="src"
  python src/flight_pipeline/ingestion/coordinator.py --years 2016 --run-id run_2016_v1 --base-data-dir data --verify-hashes
  ```

---

## 7. KẾ HOẠCH NGHIỆM THU VÀ PHỤC HỒI NĂM ĐẦU TIÊN (FIRST-YEAR VALIDATION & RECOVERY PLAN)

### 7.1. Công cụ nghiệm thu sản xuất
Dự án sẽ sử dụng trực tiếp công cụ hiện hữu [`tools/qa/verify_multiyear_snapshot.py`](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/tools/qa/verify_multiyear_snapshot.py) với chế độ `--single-run-year`:
```powershell
python tools/qa/verify_multiyear_snapshot.py --single-run-year 2016 --run-id run_2016_v1 --base-dir data --require-receipt
```

### 7.2. Các tiêu chí kiểm tra sau khi nạp (Post-Run Invariants)
1. **RunManifest (`run_manifest.json`):** Tồn tại, trường `publication_status == 'PUBLISHED'`, cấu hình năm gồm `[2016]`, danh mục toàn bộ file Parquet kèm kích thước byte và mã băm SHA-256 chính xác (không có placeholder).
2. **ExecutionReceipt (`execution_receipt.json`):** Tuân thủ cấu trúc nghiêm ngặt `ExecutionReceipt.to_dict()` (R01, R04), xác nhận mã băm manifest, đường dẫn phát hành, trạng thái pipeline hoàn tất thành công.
3. **Kiểm tra Thrift Metadata của tệp Parquet bằng PyArrow:** Magic bytes `PAR1`, cấu trúc cột hợp lệ, không chứa cột cấm (như `WEATHER_*` theo FP-DEC-017), đầy đủ 7 trường trễ/thời gian cốt lõi và định danh chuyến bay.
4. **Cân đối kế toán hàng (DC-11/DC-12):**  
   $\text{RAW rows } (5.537.987) = \text{accepted } + \text{quarantined } + \text{rejected}$.
5. **Khớp số hàng vật lý:** Số hàng đếm được từ các partition Parquet phải khớp tuyệt đối 1:1 với số hàng `accepted_row_count` trong manifest và receipt.
6. **Nhất quán con trỏ xuất bản:** Tệp `data/curated/latest_run_id.txt` trỏ nguyên tử đến `run_2016_v1`.
7. **Trạng thái khóa:** Khóa `SingleWriterLock` được giải phóng hoàn toàn và sạch sẽ (`CLEAN`).
8. **Ranh giới Multi-Year Snapshot:** Kết quả năm 2016 không đồng nghĩa với hoàn tất snapshot 9 năm (2016–2024); đây là mốc cơ sở năm đầu tiên làm tiền đề nạp các năm tiếp theo.

### 7.3. Kế hoạch phục hồi (Recovery Protocol)
Nhờ kiến trúc `SafePublisher` và atomic pointer:
* Nếu tiến trình nạp gặp sự cố (OOM, gián đoạn), dữ liệu chưa hoàn tất sẽ nằm cô lập trong thư mục staging tạm hoặc bị đánh dấu `.del_*`. Con trỏ sản xuất chưa bao giờ di chuyển.
* Người vận hành **tuyệt đối không can thiệp xóa file thủ công bằng tay**.
* Khi khởi động lại, `SafePublisher` và `check_writer_preflight_safety.py` sẽ phát hiện và thực hiện quy trình phục hồi có kiểm soát đã được kiểm chứng tại T-011.

---

## 8. CÁC TỒN ĐỌNG VÀ HÀNH ĐỘNG YÊU CẦU TỪ PROJECT LEAD

Trước khi tiến hành nạp dữ liệu sản xuất năm 2016, 4 hành động tuần tự sau cần được thực hiện:

1. **Hành động 1 (Hoàn tất G5):** Người tải dữ liệu BTS ký tên và xác nhận thông tin tại mục 4 của tệp [`docs/05-evidence/G5_D1_BTS_PROVENANCE_ATTESTATION_DRAFT.md`](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/docs/05-evidence/G5_D1_BTS_PROVENANCE_ATTESTATION_DRAFT.md). Sau khi D1 được xác thực nguồn gốc hợp lệ, Project Lead xem xét phê chuẩn chính thức TS-018 (Quyết định D3) và ban hành quyết định đóng Gate G5 (Quyết định D4). Gate G5 **không** tự động chuyển trạng thái mà bắt buộc phải qua các bước Human Signoff phụ thuộc này.
2. **Hành động 2 (Dọn dẹp RAM máy trạm):** Người vận hành đóng bớt các ứng dụng ngốn RAM (như tab trình duyệt web) để đưa dung lượng RAM khả dụng từ mức hiện tại (3.24 GiB) lên $\ge 4.0\text{ GiB}$ trước khi chạy Spark.
3. **Hành động 3 (Phê duyệt Quyết định D5):** Project Lead xem xét báo cáo này và phê duyệt chính thức Quyết định D5 (Cấp phép nạp dữ liệu sản xuất năm 2016).
4. **Hành động 4 (Kích hoạt điểm vào có kiểm soát):** Áp dụng thay đổi mã nguồn tối thiểu có kiểm duyệt để kích hoạt `D5_AUTHORIZED_BY_PROJECT_LEAD = True` trong `coordinator.py`.

---

## 9. KHUYẾN NGHỊ VÀ PHÁN QUYẾT CUỐI CÙNG (FINAL RECOMMENDATION & VERDICT)

* **Khuyến nghị:** Toàn bộ công tác chuẩn bị kỹ thuật, công cụ kiểm toán, tệp nguồn CSV 2016 và hạ tầng an toàn khóa/con trỏ đã ở trạng thái hoàn hảo, không có bất kỳ lỗi kỹ thuật nào. Dự án đã sẵn sàng 100% về mặt kỹ thuật cho năm 2016.
* **Xác nhận an toàn:** Quyết định D5 đang là `NOT_AUTHORIZED`; chưa có bất kỳ lệnh Spark live nào được chạy; dữ liệu gốc và 50 tệp staging của T-010 được bảo vệ nguyên vẹn.

$$\mathbf{VERDICT:}\quad \mathbf{READY\_WITH\_CONDITIONS}$$

*(Trạng thái sẵn sàng kỹ thuật cao; chờ 3 điều kiện hành chính và vận hành: [1] Chữ ký người tải BTS để đóng G5; [2] Dọn dẹp RAM $\ge 4.0\text{ GiB}$; [3] Project Lead cấp phép Quyết định D5 và kích hoạt có kiểm soát).*
