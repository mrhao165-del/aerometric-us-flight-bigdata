# G6_C04_2016_BASELINE_OPTION_REVIEW.md
# Đánh Giá Phương Án Tích Hợp Baseline 2016 (T-010) Vào Vận Hành 9 Năm (Gate G6)

**Mã tài liệu:** `G6_C04_2016_BASELINE_OPTION_REVIEW`  
**Dự án:** US Flight Performance Analysis 2016–2024  
**Nhiệm vụ:** T-012 — Nine-Year Pipeline Ingestion & Production Readiness  
**Gate quản trị:** Gate G5 = IN_PROGRESS, Gate G6 = NOT_STARTED / BLOCKED  
**Vai trò:** Principal Big Data Architect, PySpark Release Engineer, Independent Auditor  
**Ngày lập:** 2026-10-20  

---

## 1. KHẢO SÁT VẬT LÝ BASELINE 2016 (T-010) TRÊN ĐĨA

Khảo sát vật lý tại đường dẫn lưu trữ staging ngoài repository (`D:\Study\Code\Apache\Flight_Analyzt\staging`):
- **Tổng số tệp Parquet T-010 hiện hữu:** Đúng **50 tệp Parquet** còn nguyên vẹn 100%, khớp hoàn toàn với bản kê khai mật mã học [`T010_SIGNOFF_CLOSURE_PARQUET_ARTIFACT_HASH_MANIFEST.json`](./T010_SIGNOFF_CLOSURE_PARQUET_ARTIFACT_HASH_MANIFEST.json):
  * `smoke_2016_20261018_110720` (Full year 2016, 5.537.987 dòng, 332.018.057 bytes): 12 tệp.
  * `smoke_2016_20261018_122236` (Repeatability run, 5.537.987 dòng, 332.018.057 bytes): 12 tệp.
  * `smoke_2016_jan_20261018_110720` (January smoke): 12 tệp.
  * `smoke_2016_jan_20261018_122236` (January smoke replay): 12 tệp.
  * `smoke_2016_micro_20261018_110720` (Micro smoke): 1 tệp.
  * `smoke_2016_micro_20261018_122236` (Micro smoke replay): 1 tệp.
  * **Tổng cộng: 50/50 tệp Parquet nguyên vẹn, CRC và magic bytes `PAR1` hợp lệ.**
- **Mã vân tay schema vật lý:** `b5805fcae8db44e9a53c0eb1dfa1c1f3d9ec2983b3922bfbe5c6454f1654b09a` (34 cột chuẩn).

---

## 2. PHÂN TÍCH HAI PHƯƠNG ÁN TÍCH HỢP CHO GATE G6

> [!NOTE]
> Hai phương án này hoàn toàn độc lập với chính sách `FP-DEC-019 Option B` của TS-018 (đối chiếu BTS). Đây là quyết định kỹ thuật về mặt xuất bản tập dữ liệu Curated Storage cho riêng năm 2016.

### 2.1. Phương án A: Thăng hạng trực tiếp Baseline T-010 (`G6-2016-OPTION-A`)
- **Cơ chế:** Sử dụng thư mục staging `smoke_2016_20261018_110720`, đóng gói đối tượng `RowAccounting(5537987, 5537987, 0, 0)`, và gọi `SafePublisher.publish()` để thăng hạng vào `curated/runs/run_2016_promoted_t010/`.
- **Ưu điểm:**
  * Tiết kiệm thời gian xử lý Spark (không phải đọc và ghi lại 1.54 GB dữ liệu thô năm 2016).
  * Giữ nguyên vẹn mã băm từng tệp Parquet đã được nghiệm thu tại Gate G5 (`T010_HUMAN_SIGNOFF_20261018.md`).
- **Nhược điểm & Rào cản kỹ thuật:**
  * Thư mục `smoke_2016_*` được tạo bởi kịch bản smoke runner độc lập, thiếu tệp receipt sidecar hiện đại (`ExecutionReceipt`) và cấu trúc metadata chuẩn mà `IngestionCoordinator` thế hệ T-011 tạo ra. Cần viết một adapter chuyển đổi metadata để tương thích với `multi_year_dataset_registry.json`.

### 2.2. Phương án B: Chạy lại năm 2016 thành Versioned Production Run (`G6-2016-OPTION-B`)
- **Cơ chế:** Cho phép `IngestionCoordinator.run_ingestion(run_id="run_2016_prod_v1", years=[2016])` xử lý tệp CSV thô `data/raw/tabular/2016/flight_with_weather_2016.csv`.
- **Ưu điểm:**
  * **Tính đồng nhất kiến trúc tuyệt đối (Architectural Uniformity):** Cả 9 năm (2016–2024) đều được xử lý bởi cùng một phiên bản coordinator, cùng cấu trúc manifest, cùng sidecar receipt, cùng cơ chế forensic quarantine (`data/quarantine/<run_id>/`).
  * **Bảo vệ tuyệt đối baseline T-010:** Dữ liệu T-010 trong `D:\Study\Code\Apache\Flight_Analyzt\staging` hoàn toàn không bị chạm vào, được lưu giữ vĩnh viễn làm bằng chứng đối chứng lịch sử.
  * Chi phí tài nguyên rất nhỏ: Năm 2016 chỉ mất khoảng ~1.8 giây đọc luồng và ~15-20 giây ghi Parquet trên Spark.
- **Nhược điểm:**
  * Tốn thêm khoảng 332 MB dung lượng đĩa cho lần chạy mới (hoàn toàn nằm trong ngân sách đĩa 18.5 GiB).

---

## 3. BẢNG SO SÁNH KỸ THUẬT TOÀN DIỆN

| Tiêu chí đánh giá | Phương án A (Promote T-010) | Phương án B (Unified Production Re-run) |
| :--- | :--- | :--- |
| **Tính đồng nhất Receipt & Manifest** | Thấp (cần adapter metadata riêng) | **Tuyệt đối (Cùng cấu trúc với 2017–2024)** |
| **Tính toàn vẹn của Baseline T-010** | Nguyên vẹn (được thăng hạng) | **Nguyên vẹn 100% (Giữ làm benchmark độc lập)** |
| **Khả năng rollback khi lỗi** | Phức tạp do phụ thuộc staging cũ | **Đơn giản qua atomic version pointer / registry** |
| **Thời gian thực thi** | Tức thì (~0.5s copy) | Rất nhanh (~20s Spark execution) |
| **Khả năng tương thích Snapshot 9 năm** | Cần xử lý ngoại lệ cấu trúc thư mục | **Tương thích tự nhiên 100%** |
| **Rủi ro sai khác mã băm CSV thô** | Đã được xác thực tại Gate G5 | **Đã xác thực hash `4ed92ed7...` (Errata G5-T010)** |

---

## 4. ĐỀ XUẤT CỦA ĐỘI NGŨ KỸ THUẬT

1. **Khuyến nghị kỹ thuật:**
   - Đội ngũ kỹ thuật **khuyến nghị lựa chọn `G6-2016-OPTION-B` (Unified Production Re-run)** để đảm bảo toàn bộ 9 năm 2016–2024 có chung một vòng đời nạp dữ liệu chuẩn tắc, sinh đầy đủ ExecutionReceipt, RunManifest và tích hợp mượt mà vào `multi_year_dataset_registry.json`.
   - Toàn bộ 50 tệp Parquet của T-010 tiếp tục được niêm phong bất biến tại thư mục `staging/` ngoài repository làm bằng chứng đối chứng.
2. **Quyền quyết định con người:**
   - Khuyến nghị này được trình lên Project Lead xem xét trước khi phê duyệt quyết định vận hành D5. Không tự ý thực thi chạy lại hoặc thăng hạng khi chưa có phê duyệt chính thức.
