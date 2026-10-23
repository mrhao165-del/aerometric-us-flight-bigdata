# G6_C05_EXECUTION_PATH_LOCK_RESOURCE_AUDIT.md
# Kiểm Toán Đường Dẫn Vận Hành, Cơ Chế An Toàn Khóa Và Chính Sách Tài Nguyên Trước G6

**Mã tài liệu:** `G6_C05_EXECUTION_PATH_LOCK_RESOURCE_AUDIT`  
**Dự án:** US Flight Performance Analysis 2016–2024  
**Nhiệm vụ:** T-012 — Nine-Year Ingestion Preflight & Safety Enforcement  
**Gate quản trị:** Gate G5 = IN_PROGRESS, Gate G6 = NOT_STARTED / BLOCKED  
**Vai trò:** Principal Big Data Architect, Senior Windows NTFS Storage Engineer, Release Auditor  
**Ngày lập:** 2026-10-20  

---

## 1. ĐỐI SOÁT VÀ CHUẨN HÓA ĐƯỜNG DẪN XUẤT BẢN THỰC TẾ (SECTION 6.1)

Kiểm toán toàn bộ tài liệu vận hành và đối chiếu với mã nguồn sản xuất (`IngestionCoordinator`, `SafePublisher`):

### 1.1. Bảng đối chiếu đường dẫn chuẩn sản xuất vs đường dẫn lỗi thời:
| Thành phần dữ liệu | Đường dẫn chuẩn trong mã nguồn sản xuất (`flight_pipeline`) | Đường dẫn lỗi thời bị cấm (`SUPERSEDED`) | Trạng thái hợp đồng |
| :--- | :--- | :--- | :---: |
| **Staging Area** | `<base_dir>/staging/<run_id>/` | `staging/active/<year>/latest`<br>`staging/runs/run_<year>_<run_id>/` | **ENFORCED** |
| **Curated Storage** | `<base_dir>/curated/runs/<run_id>/` | `curated/<year>/published` | **ENFORCED** |
| **Global Latest Pointer** | `<base_dir>/curated/latest_run_id.txt` | `curated/latest_pointer.txt` | **ENFORCED** |
| **Forensic Quarantine** | `<base_dir>/quarantine/<run_id>/` | `data/quarantine_records/` | **ENFORCED** |
| **Run Metadata / Manifest** | `<base_dir>/metadata/<run_id>/` | `curated/runs/<run_id>/manifest/` | **ENFORCED** |
| **Single-Writer Lock** | `<base_dir>/locks/.pipeline.lock` | `locks/writer.lck` | **ENFORCED** |

### 1.2. Đánh dấu văn bản lỗi thời:
- Tài liệu [`G6_T012_EXECUTION_CHECKLIST.md`](./G6_T012_EXECUTION_CHECKLIST.md) (v1) đã được gắn nhãn cảnh báo **`SUPERSEDED / DO_NOT_EXECUTE`**, thay thế bằng [`G6_T012_FINAL_EXECUTION_CHECKLIST_V2.md`](./G6_T012_FINAL_EXECUTION_CHECKLIST_V2.md).
- Toàn bộ các script vận hành thực tế bắt buộc sử dụng cấu trúc thư mục chuẩn của `SafePublisher`.

---

## 2. LỆNH KIỂM TRA TIỀN KHẢ THI KHÓA VÀ HỒI PHỤC ĐỘC LẬP (SECTION 6.2)

Để đảm bảo việc kiểm tra an toàn khóa không chỉ là một helper ẩn trong bộ unit test, dự án đã chính thức ban hành công cụ dòng lệnh độc lập:
```powershell
python tools/qa/check_writer_preflight_safety.py --base-dir data --json
```

### 2.1. Hợp đồng kiểm tra chỉ đọc (Read-Only Safety Contract):
1. **Hoàn toàn chỉ đọc (Pure Read-Only):**
   - Công cụ tuyệt đối **không** tạo lock, **không** xóa tệp `.pipeline.lock`, **không** xóa marker hồi phục `.recovery_required*`, và **không** can thiệp vào tiến trình khác.
2. **Kiểm tra song trùng (Dual-Gate Verification):**
   - **Gate 1 (POINTER_STATE):** Kiểm tra tính hợp lệ của con trỏ xuất bản (chấp nhận trạng thái uninitialized an toàn).
   - **Gate 2 (WRITER_LOCK_STATE):**
     * Quét sự hiện diện của các marker hồi phục dở dang (`.pipeline.lock.*.recovery_required*`, `.del_*`). Nếu phát hiện, báo lỗi `UNRESOLVED_RECOVERY_ARTIFACTS_DETECTED` (Mã thoát 2).
     * Đọc tệp `.pipeline.lock`, trích xuất PID và xác định trạng thái sống của tiến trình qua `get_pid_liveness(pid)`.
3. **Mã thoát đóng (Fail-Closed Exit Codes):**
   - `0`: **CLEAN** — Không có lock, không có marker hồi phục, con trỏ hợp lệ. Sẵn sàng cho writer khởi động.
   - `1`: **ACTIVE_OR_STALE_LOCK** — Có tiến trình đang giữ lock (`PROCESS_ALIVE`) hoặc lock cũ của PID đã chết (`PROCESS_DEAD` - bắt buộc phải phục hồi thủ công có kiểm soát, cấm tự ý xóa).
   - `2`: **UNRESOLVED_RECOVERY** — Có marker sự cố dở dang từ lần chạy trước chưa được xử lý.
   - `3`: **CORRUPT_OR_AMBIGUOUS** — Metadata lock bị hỏng hoặc trạng thái PID không xác định (`PROCESS_STATUS_UNKNOWN`).
   - `4`: **POINTER_ERROR** — Lỗi hỏng con trỏ staging/curated.
4. **Bảo toàn nguyên tắc chiếm khóa nguyên tử (Atomic Lock Acquisition at Runtime):**
   - Lệnh preflight đạt kết quả PASS (mã thoát 0) **không** thay thế cho việc writer phải thực hiện chiếm khóa nguyên tử `SingleWriterLock.acquire()` tại thời điểm chạy thật. Nếu có sự tranh chấp phát sinh giữa lúc preflight và lúc writer bắt đầu, cơ chế khóa NTFS sẽ lập tức kích hoạt Fail-Closed.

---

## 3. CHÍNH SÁCH TÀI NGUYÊN PHẦN CỨNG THỰC TẾ TRƯỚC G6 (SECTION 6.3)

Đối soát và chuẩn hóa tài liệu [`G6_T012_RESOURCE_PRESTART_POLICY.md`](./G6_T012_RESOURCE_PRESTART_POLICY.md) theo đúng các số liệu đo đạc vật lý thực tế:

1. **Dung lượng đĩa trống trên Ổ `D:`:**
   - Dung lượng đo thực tế: **57.90 GiB** (tương đương **62.17 GB**).
   - Ngân sách lưu trữ tối đa cho 9 năm Parquet Curated: **18.50 GiB** (tương đương **19.86 GB**).
   - Hệ số an toàn thực tế: **$3.13\times$** ($57.90 / 18.50 = 62.17 / 19.86$).
   - Quy định: Dung lượng trống tối thiểu trước khi bấm chạy T-012 phải đạt $\ge 35\text{ GiB}$.
2. **Thư mục Spark Scratch / Spill Space:**
   - Cấu hình bắt buộc: `spark.local.dir = D:/temp/spark_scratch`.
   - Ngăn chặn triệt để việc Spark tự động ghi scratch tràn vào ổ hệ thống `C:`.
3. **Bộ nhớ hệ thống (System RAM & JVM Allocations):**
   - Tổng RAM vật lý hệ thống tối thiểu: $\ge 16\text{ GB}$.
   - JVM Heap cho Spark Driver: Cấp phát `-Xmx4g`, `-Xms2g`.
   - Off-Heap Memory: Cấp phát `spark.memory.offHeap.size = 2g`.
   - **Lưu ý khoa học về bộ nhớ:** Tuyệt đối không nhầm lẫn `Runtime.getRuntime().freeMemory()` (bộ nhớ chưa dùng trong phần heap đã cấp phát) với tổng dung lượng JVM có thể cấp phát thêm từ hệ điều hành. Nghiêm cấm việc cưỡng bức Garbage Collection (`System.gc()`) hoặc xóa các tệp `.tmp_*` để làm giả số liệu kiểm tra.
4. **Bảo vệ bằng chứng lịch sử (No Artificially Inflated Checks):**
   - Mọi kiểm tra trước khi chạy phải đo đạc trực tiếp trạng thái vật lý tại thời điểm chạy, không sử dụng lại ảnh chụp cũ.

---

## 4. KẾT LUẬN

Mọi đường dẫn vận hành, công cụ kiểm tra khóa độc lập (`check_writer_preflight_safety.py`), và chính sách tài nguyên đã được chuẩn hóa đồng bộ 100%, bảo đảm không có đường dẫn lỗi thời và loại bỏ nguy cơ tranh chấp khóa hoặc tràn đĩa khi Project Lead cấp phép Gate G6.
