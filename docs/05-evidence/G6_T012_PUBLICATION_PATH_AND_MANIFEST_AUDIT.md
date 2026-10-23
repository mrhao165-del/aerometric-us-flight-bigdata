# G6_T012_PUBLICATION_PATH_AND_MANIFEST_AUDIT.md
# Kiểm Toán Hợp Đồng Đường Dẫn Xuất Bản, Lược Đồ Manifest và Ranh Giới Kiểm Tra Parquet (Finding P06 & P07)

**Dự án:** US Flight Performance Analysis 2016–2024  
**Nhiệm vụ:** Publication Architecture & Manifest Contract Verification  
**Module phân tích:** `src/flight_pipeline/storage/publication.py` & `src/flight_pipeline/ingestion/coordinator.py`  
**Gate quản lý:** Gate G5 = IN_PROGRESS, Gate G6 = NOT_STARTED / BLOCKED  
**Tác giả:** Principal PySpark Release Engineer, Storage Reliability Specialist  
**Thời điểm lập:** 2026-10-20  

---

## 1. BỐI CẢNH VÀ ĐỐI CHIẾU MÃ NGUỒN THỰC TẾ (FINDING P06)

Trong các tài liệu kế hoạch ban đầu của Gate G6, có sự không nhất quán về đường dẫn lưu trữ, ví dụ xuất hiện các đường dẫn giả định như:
`staging/active/<year>/latest` hoặc `curated/<year>/published`.

**Đối chiếu thực tế trong mã nguồn:**
Theo cài đặt thực tế của hai lớp [`SafePublisher`](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/src/flight_pipeline/storage/publication.py#L110) và [`IngestionCoordinator`](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/src/flight_pipeline/ingestion/coordinator.py#L730), hệ thống lưu trữ được tổ chức theo cấu trúc phân cấp tương đối dựa trên một thư mục gốc cấu hình duy nhất: **`base_data_dir`**.

```
<base_data_dir>/
├── staging/                           # Thư mục staging tạm thời
│   └── <run_id>/                      # Staging độc lập của từng lượt chạy (two-phase task staging)
│       └── part-*.parquet
├── curated/                           # Thư mục xuất bản dữ liệu chuẩn
│   ├── latest_run_id.txt              # Tệp con trỏ toàn cục trỏ đến run_id mới nhất
│   └── runs/                          # Kho lưu trữ các phiên bản dữ liệu bất biến
│       └── <run_id>/                  # Thư mục phiên bản bất biến (immutable versioned run)
│           ├── part-*.parquet
│           └── run_manifest.json      # Bản sao manifest xuất bản (nếu được sao chép cùng)
├── metadata/                          # Thư mục lưu trữ siêu dữ liệu chính thức của Coordinator
│   └── <run_id>/
│       ├── run_manifest.json          # Tệp RunManifest chính thức (ghi nguyên tử)
│       └── execution_receipt.json     # Tệp ExecutionReceipt độc lập (sidecar receipt)
├── quarantine/                        # Thư mục cách ly các bản ghi lỗi DC-11
│   └── <run_id>/
│       └── quarantine_*.parquet
└── locks/                             # Thư mục quản lý khóa Single-Writer
    ├── .pipeline.lock                 # Tệp khóa nguyên tử chính (chứa LockMetadata)
    └── .pipeline.lock.coord           # Tệp điều phối vùng găng (CoordinationLock)
```

---

## 2. NGUYÊN TẮC CẤU HÌNH VÀ THAM SỐ `--base-dir` TRÊN CLI

1. **Không mặc định `base_data_dir` là gốc repository:**
   - Trong môi trường kiểm thử hoặc production, `base_data_dir` có thể được cấu hình trỏ ra ổ đĩa lưu trữ lớn riêng biệt (ví dụ `D:\Study\Code\Apache\Flight_Analyzt\data` hoặc `D:\Study\Code\Apache\Flight_Analyzt`).
   - Mọi công cụ CLI (bao gồm `tools/qa/verify_staging_pointer.py`) đều tiếp nhận tham số `--base-dir` hoặc `-b` để trỏ chính xác vào thư mục chứa `curated/` và `staging/`.
2. **Chuẩn hóa tìm kiếm `run_manifest.json` trong `verify_staging_pointer.py`:**
   - Để tương thích với cả `SafePublisher` và `IngestionCoordinator`, công cụ kiểm tra con trỏ quét tìm manifest tại 3 vị trí theo thứ tự ưu tiên:
     1. `<target_dir>/run_manifest.json` (bên trong thư mục phiên bản `curated/runs/<run_id>/`).
     2. `<base_dir>/metadata/<pointer_val>/run_manifest.json` (thư mục metadata chuẩn của `IngestionCoordinator`).
     3. `<base_dir>/curated/metadata/<pointer_val>/run_manifest.json` (vị trí sidecar dự phòng).

---

## 3. RANH GIỚI KIỂM TRA PARQUET VÀ PHƯƠNG PHÁP ĐỐI SOÁT SHA-256 (FINDING P07)

> [!IMPORTANT]
> **Đính chính quan trọng về ranh giới kiểm tra:**
> Công cụ `tools/qa/verify_staging_pointer.py` là một công cụ **kiểm tra tính hợp lệ nhanh của con trỏ (fast pointer probe)**. Công cụ này **KHÔNG tính toán lại mã băm SHA-256 của toàn bộ các tệp Parquet** khi kiểm tra con trỏ, vì việc băm lại hàng chục gigabyte Parquet sẽ làm tắc nghẽn hoạt động kiểm tra vận hành.

### 3.1. Phạm vi kiểm tra của `verify_staging_pointer.py`
- Kiểm tra 4 byte ma thuật `b'PAR1'` ở đầu tệp (offset 0..3).
- Kiểm tra 4 byte ma thuật `b'PAR1'` ở cuối tệp (offset -4..EOF).
- Đọc và phân tích siêu dữ liệu Thrift footer thông qua `pyarrow.parquet.read_metadata()` để bảo đảm tệp có cấu trúc cột hợp lệ và không bị cắt cụt (truncated).

### 3.2. Quy trình đối soát toàn vẹn SHA-256 chính thức (Deep Forensic SHA-256 Audit)
Khi cần chứng thực toàn vẹn mật mã học ở mức độ pháp y dữ liệu (forensic audit):
1. **Bước 1:** Trích xuất danh mục tệp (`outputs`) từ tệp `run_manifest.json` chính thức. Tệp manifest lưu trữ chính xác kích thước bytes và mã băm SHA-256 của từng phân vùng Parquet tại thời điểm Coordinator kết thúc ghi.
2. **Bước 2:** Chạy công cụ đối soát chuyên dụng độc lập (ví dụ `tools/qa/verify_t010_parquet_schema_attestation.py` hoặc script đối soát manifest) để đọc từng tệp Parquet trên đĩa vật lý bằng streaming buffer 64KB và so khớp bit-for-bit với mã băm trong manifest.

---

## 4. PHÂN BIỆT CON TRỎ TOÀN CỤC VỚI CƠ CHẾ TRUY XUẤT ĐỒNG THỜI 9 NĂM

1. **Vai trò của con trỏ toàn cục (`curated/latest_run_id.txt`):**
   - Chỉ phản ánh định danh của mẻ dữ liệu gần nhất được xuất bản thành công.
   - Khi hoàn thành xử lý năm 2024, con trỏ sẽ trỏ đến `run_2024` (hoặc `run_9year_final`).
2. **Cơ chế truy xuất đồng thời toàn bộ 9 năm:**
   - Để phân tích và tính toán 8 CORE KPI trên toàn bộ 54,7 triệu dòng của 9 năm, ứng dụng Spark không chỉ đọc duy nhất một thư mục con trỏ, mà thực hiện nạp dữ liệu thông qua:
     * **Đường dẫn tập hợp (Directory Wildcard):**
       `spark.read.schema(curated_schema).parquet("<base_dir>/curated/runs/run_*/")`
     * **Hoặc Sổ bộ dữ liệu đa năm (Multi-Year Dataset Registry):**
       Tệp manifest tổng hợp liên kết chính xác đường dẫn 9 phiên bản tương ứng của từng năm từ 2016 đến 2024.

---

## 5. KẾT LUẬN ĐỒNG BỘ TÀI LIỆU

Mọi tài liệu kế hoạch triển khai của Gate G6 ([`G6_T012_FULL_RUN_ENTRY_PLAN.md`](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/docs/05-evidence/G6_T012_FULL_RUN_ENTRY_PLAN.md), [`G6_T012_READINESS_CHECKLIST.md`](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/docs/05-evidence/G6_T012_READINESS_CHECKLIST.md)) đã được đồng bộ hóa hoàn toàn với cấu trúc đường dẫn và hợp đồng thực tế của `SafePublisher` và `IngestionCoordinator`.
