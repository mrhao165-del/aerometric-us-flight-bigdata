# G6_C03_MULTIYEAR_SNAPSHOT_AND_VERSION_POLICY.md
# Chính Sách Quản Lý Snapshot 9 Năm Và Ngăn Chặn Đọc Trùng Phiên Bản Dữ Liệu

**Mã tài liệu:** `G6_C03_MULTIYEAR_SNAPSHOT_AND_VERSION_POLICY`  
**Dự án:** US Flight Performance Analysis 2016–2024  
**Nhiệm vụ:** T-012 / T-013 — Nine-Year Pipeline Ingestion, Multi-Year Publication & Storage  
**Gate quản trị:** Gate G5 = IN_PROGRESS, Gate G6 = NOT_STARTED / BLOCKED  
**Vai trò:** Principal Big Data Architect, Senior PySpark Engineer, Storage Reliability Reviewer  
**Ngày lập:** 2026-10-20  

---

## 1. NGUYÊN NHÂN VÀ PHÂN TÍCH RỦI RO ĐỌC TRÙNG (WILDCARD DUPLICATION RISK)

### 1.1. Kiến trúc lưu trữ hiện tại của mã nguồn sản xuất:
Mã nguồn sản xuất hiện lưu trữ dữ liệu nạp theo từng lần chạy độc lập:
```
<base_data_dir>/curated/runs/<run_id>/
```
và duy trì một con trỏ duy nhất:
```
<base_data_dir>/curated/latest_run_id.txt
```
Thao tác xuất bản qua `SafePublisher.publish()` đảm bảo tính bất biến (*immutable versioned directory*) của từng `run_id` và cập nhật nguyên tử con trỏ `latest_run_id.txt`.

### 1.2. Rủi ro của việc đọc wildcard `runs/run_*/`:
Trong một số tài liệu hướng dẫn sơ khai, có gợi ý đọc toàn bộ tập dữ liệu 9 năm bằng cú pháp:
```python
spark.read.schema(curated_schema).parquet("<base_dir>/curated/runs/run_*/")
```
**Đây là một khiếm khuyết thiết kế nghiêm trọng vì:**
1. **Nguy cơ nhân đôi bản ghi khi chạy lại (Re-run duplication):**
   Nếu Năm $Y$ (ví dụ 2017) bị lỗi và cần chạy lại thành `run_2017_v2`, thì thư mục `curated/runs/` sẽ chứa cả `run_2017_v1` (được bảo tồn bất biến để kiểm toán) và `run_2017_v2`. Lệnh đọc wildcard `run_*` sẽ tự động nạp cả hai phiên bản, làm nhân đôi dữ liệu năm 2017 lên **11.151.744 dòng** thay vì 5.575.872 dòng.
2. **Nguy cơ nạp lẫn dữ liệu thử nghiệm:**
   Các thư mục chạy thử như `smoke_2016_*` hoặc `probe_*` nếu nằm chung trong `runs/` sẽ bị wildcard đọc vào tập phân tích chính thức.
3. **Giới hạn của con trỏ đơn `latest_run_id.txt`:**
   Con trỏ `latest_run_id.txt` chỉ lưu một chuỗi duy nhất của lần chạy gần nhất. Nếu quy trình chạy phân kỳ 9 năm theo từng mẻ (hoặc từng năm độc lập), con trỏ này chỉ trỏ về năm 2024, hoàn toàn không đại diện cho toàn bộ 9 năm (2016–2024).

---

## 2. THIẾT KẾ SỔ ĐĂNG KÝ BẢN SNAPSHOT 9 NĂM (`multi_year_dataset_registry.json`)

Để giải quyết triệt để rủi ro trên mà không làm phá vỡ logic xuất bản bất biến của T-011, dự án thiết lập quy tắc quản lý phiên bản thông qua **Sổ đăng ký bản snapshot 9 năm bất biến** (`multi_year_dataset_registry.json`) đặt tại:
```
<base_data_dir>/curated/multi_year_dataset_registry.json
```

### 2.1. Cấu trúc Schema của Sổ Đăng Ký Snapshot:
```json
{
  "registry_version": "1.0",
  "dataset_id": "US_FLIGHT_PERFORMANCE_2016_2024_CANONICAL",
  "snapshot_timestamp_utc": "2026-10-20T18:00:00Z",
  "governance_status": "PENDING_PROJECT_LEAD_ACCEPTANCE",
  "total_years_count": 9,
  "total_accepted_rows": 54674003,
  "years": {
    "2016": {
      "year": 2016,
      "selected_run_id": "run_2016_prod_v1",
      "relative_curated_path": "curated/runs/run_2016_prod_v1",
      "accounting": {
        "raw_row_count": 5537987,
        "accepted_row_count": 5537987,
        "quarantined_row_count": 0,
        "rejected_row_count": 0
      },
      "schema_fingerprint": "b5805fcae8db44e9a53c0eb1dfa1c1f3d9ec2983b3922bfbe5c6454f1654b09a",
      "source_coverage_status": "VERIFIED_WITH_SCOPE",
      "publication_status": "PUBLISHED",
      "manifest_ref": "metadata/run_2016_prod_v1/run_manifest.json"
    },
    "... (tương tự cho 2017 đến 2023) ...": {},
    "2024": {
      "year": 2024,
      "selected_run_id": "run_2024_prod_v1",
      "relative_curated_path": "curated/runs/run_2024_prod_v1",
      "accounting": {
        "raw_row_count": 6284841,
        "accepted_row_count": 6284841,
        "quarantined_row_count": 0,
        "rejected_row_count": 0
      },
      "schema_fingerprint": "b5805fcae8db44e9a53c0eb1dfa1c1f3d9ec2983b3922bfbe5c6454f1654b09a",
      "source_coverage_status": "PARTIAL",
      "publication_status": "PUBLISHED",
      "manifest_ref": "metadata/run_2024_prod_v1/run_manifest.json"
    }
  }
}
```

---

## 3. CÁC QUY TẮC KIỂM TRA BẢO VỆ CHẶN LỖI (VALIDATION INVARIANTS)

Trước khi bất kỳ tác vụ đọc dữ liệu phục vụ báo cáo hoặc tính KPI T-013 được thực thi, bộ kiểm tra tính toàn vẹn snapshot phải kiểm chứng 7 điều kiện bất biến (Fail-Closed):

1. **Tính đầy đủ 9 năm (Completeness Invariant):**
   Bắt buộc phải có đầy đủ 9 năm $2016 \dots 2024$. Thiếu bất kỳ năm nào sẽ lập tức chặn thực thi (`ERROR_INCOMPLETE_YEARS`).
2. **Tính đơn nhất theo năm (Uniqueness Invariant):**
   Mỗi năm chỉ được phép có đúng một `selected_run_id` được kích hoạt. Không cho phép tồn tại đa phiên bản hoạt động đồng thời cho cùng một năm.
3. **Tính tồn tại của Run ID và Đường dẫn (Liveness Invariant):**
   Từng `selected_run_id` phải tồn tại trong thư mục `curated/runs/<run_id>/` và có đầy đủ các tệp `.parquet` hợp lệ (header/footer `PAR1`).
4. **Đối chiếu Run Manifest (Manifest Alignment Invariant):**
   Run Manifest tương ứng của `run_id` phải ghi nhận chính xác năm $Y$ trong danh sách `years`.
5. **Không trùng lặp đường dẫn vật lý (Path Disjoint Invariant):**
   Không có hai năm khác nhau trỏ vào cùng một đường dẫn thư mục vật lý.
6. **Bảo toàn hạch toán dòng DC-11:**
   Tổng số dòng của 9 năm trong registry phải khớp chính xác:
   $$\sum_{Y=2016}^{2024} \text{raw\_row\_count}(Y) \equiv 54,674,003$$
7. **Bảo vệ con trỏ đơn lẻ (Pointer Decoupling Invariant):**
   Việc con trỏ `latest_run_id.txt` thay đổi không tự động làm thay đổi bản snapshot 9 năm nếu chưa có thao tác cập nhật registry có thẩm quyền.

---

## 4. PHƯƠNG PHÁP ĐỌC DỮ LIỆU ĐƯỢC PHÊ DUYỆT TRONG T-013

Cấm tuyệt đối việc sử dụng wildcard `spark.read.parquet("runs/run_*/")`.

Thay vào đó, hàm nạp dữ liệu chuẩn tắc `load_canonical_multiyear_dataset(spark, registry_path)` sẽ:
1. Đọc và thẩm định tính toàn vẹn của `multi_year_dataset_registry.json`.
2. Trích xuất danh sách 9 đường dẫn thư mục cụ thể của từng năm:
   `paths = [registry["years"][str(y)]["relative_curated_path"] for y in range(2016, 2025)]`
3. Thực hiện đọc danh sách đường dẫn tường minh:
   ```python
   df = spark.read.schema(curated_parquet_schema).parquet(*paths)
   ```
Phương pháp này bảo đảm: Dù trong `curated/runs/` có 20 hay 50 lần chạy cũ/chạy lại, câu truy vấn 9 năm luôn luôn chỉ đọc đúng 9 thư mục đã được phê duyệt, loại bỏ 100% rủi ro đọc trùng bản ghi.
