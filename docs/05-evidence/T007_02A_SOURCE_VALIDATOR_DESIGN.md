# T007-02A Source Validator Architecture & Design Specification

**Document ID:** `T007_02A_SOURCE_VALIDATOR_DESIGN.md`  
**Date:** 2026-10-17  
**Task:** `T007-02A` (Source Inventory & Local Hash Verifier Implementation)  
**Parent Task:** `T-007` (Raw CSV Ingestion Pipeline)  
**Status:** `IMPLEMENTED_AND_VERIFIED`  
**Engineer:** Senior Big Data Architect & Lead Python Data Engineer  

---

## 1. Mục tiêu và Kiến trúc Tổng quan

Module `src/flight_pipeline/ingestion/source_validator.py` đóng vai trò là chốt chặn an toàn đầu vào (integrity gate) cho toàn bộ pipeline nạp dữ liệu. Trước khi bất kỳ thao tác đọc hoặc phân tích CSV nào được thực thi, module bảo đảm xác thực tính sẵn sàng, tính toàn vẹn và cấu trúc của 9 tệp CSV nguồn hàng không giai đoạn 2016–2024.

```
+-------------------------------------------------------------------------+
|                           SourceValidator                               |
|                                                                         |
|  1. Inventory Check       2. Path Safety Check    3. Streaming SHA-256  |
|  +---------------------+  +--------------------+  +------------------+  |
|  | 9 Audited Years     |  | Reject '..'        |  | Chunk: 1 MiB     |  |
|  | Expected Rows/Bytes |  | Reject Symlinks    |  | Memory: O(1)     |  |
|  | 34 Columns Canonical|  | Root Containment   |  | Pre/Post Stat    |  |
|  +---------------------+  +--------------------+  +------------------+  |
|                               |                             |           |
|                               v                             v           |
|  4. State Assignment & Baseline Comparison                              |
|  +-------------------------------------------------------------------+  |
|  | - SOURCE_MISSING / SIZE_MISMATCH / SOURCE_CHANGED_DURING_READ     |  |
|  | - LOCAL_HASH_COMPUTED_UNAPPROVED (Candidate, Pending Approval)   |  |
|  | - LOCAL_HASH_VERIFIED (Strict match with approved baseline)       |  |
|  +-------------------------------------------------------------------+  |
|                               |                                         |
|                               v                                         |
|  5. Governance Preservation & Lineage Recording                         |
|  +-------------------------------------------------------------------+  |
|  | - Upstream Identity: IDENTITY_UNVERIFIED (OR-08 / TS-019)         |  |
|  | - RunManifest Integration: record_input(path, bytes, sha256)      |  |
|  +-------------------------------------------------------------------+  |
+-------------------------------------------------------------------------+
```

---

## 2. Bảng Baseline 9 Tệp Nguồn Đã Kiểm Toán (G1 Metadata)

Module định nghĩa cấu trúc dữ liệu bất biến `SourceEntry` và từ điển `AUDITED_SOURCE_INVENTORY` tương ứng 9 năm:

| Năm | Đường dẫn Tương đối Chuẩn tắc | Số Dòng Kiểm toán | Kích thước Byte Kiểm toán | Số Cột |
| :---: | :---| :---: | :---: | :---: |
| **2016** | `data/raw/tabular/2016/flight_with_weather_2016.csv` | 5,617,658 | 1,563,303,803 | 34 |
| **2017** | `data/raw/tabular/2017/flight_with_weather_2017.csv` | 5,674,621 | 1,577,414,136 | 34 |
| **2018** | `data/raw/tabular/2018/flight_with_weather_2018.csv` | 7,213,446 | 2,005,622,763 | 34 |
| **2019** | `data/raw/tabular/2019/flight_with_weather_2019.csv` | 7,422,037 | 2,060,544,985 | 34 |
| **2020** | `data/raw/tabular/2020/flight_with_weather_2020.csv` | 4,688,354 | 1,303,942,668 | 34 |
| **2021** | `data/raw/tabular/2021/flight_with_weather_2021.csv` | 5,992,543 | 1,666,039,833 | 34 |
| **2022** | `data/raw/tabular/2022/flight_with_weather_2022.csv` | 6,703,047 | 1,863,280,094 | 34 |
| **2023** | `data/raw/tabular/2023/flight_with_weather_2023.csv` | 6,787,093 | 1,885,823,248 | 34 |
| **2024** | `data/raw/tabular/2024/flight_with_weather_2024.csv` | 4,575,204 | 1,270,394,643 | 34 |
| **TỔNG** | **9 tệp CSV nguồn** | **54,674,003** | **15,196,366,173** | **34** |

---

## 3. Hệ Thống Trạng thái Xác thực (Verification State Machine)

Lớp `VerificationState(str, Enum)` phân định rõ ràng 9 trạng thái loại trừ lẫn nhau:
1. `SOURCE_PRESENT_METADATA_MATCH`: Tệp tồn tại, là regular file, kích thước byte khớp baseline nhưng chưa tính mã băm.
2. `LOCAL_HASH_COMPUTED_UNAPPROVED`: Đã tính xong mã băm streaming SHA-256 nhưng chưa có baseline được Project Lead phê duyệt đối chiếu (Candidate hash). Trạng thái này có `is_verified = False`.
3. `LOCAL_HASH_VERIFIED`: Mã băm tính toán khớp 100% với baseline SHA-256 đã được phê duyệt. Trạng thái duy nhất có `is_verified = True`.
4. `SOURCE_MISSING`: Tệp không tồn tại tại đường dẫn chỉ định.
5. `SIZE_MISMATCH`: Kích thước tệp trên đĩa khác với kích thước kiểm toán.
6. `HASH_MISMATCH`: Mã băm tính toán khác với mã băm trong baseline được phê duyệt.
7. `SOURCE_READ_ERROR`: Lỗi phân quyền (PermissionError) hoặc lỗi I/O hệ thống.
8. `SOURCE_CHANGED_DURING_READ`: Tệp bị thay đổi kích thước hoặc mtime trong lúc đang đọc stream.
9. `BASELINE_PENDING_APPROVAL`: Baseline đang chờ phê duyệt từ cấp thẩm quyền.

### Quy tắc Bất biến:
Tuyệt đối **không bao giờ** tự động chuyển trạng thái từ `LOCAL_HASH_COMPUTED_UNAPPROVED` sang `LOCAL_HASH_VERIFIED` khi chưa có baseline đối chiếu.

---

## 4. Cơ chế Tính Mã Băm Streaming SHA-256 An toàn Bộ nhớ

Để xử lý các tệp kích thước lớn (lên tới 2.06 GB cho năm 2019) trên máy trạm thông thường mà không gây tràn bộ nhớ (OOM):
- Kích thước khối đệm đọc chuẩn: `DEFAULT_HASH_CHUNK_SIZE = 1,048,576` bytes (1 MiB).
- Thuật toán băm: Chuẩn NIST `hashlib.sha256()`.
- Mức tiêu thụ bộ nhớ RAM: Cố định $O(1)$ (< 2 MB) bất kể kích thước tệp nguồn.
- **Phát hiện sửa đổi tệp khi đang đọc (Race Condition Detection):**
  - Thực hiện lệnh `stat_before = os.stat(path_obj)` trước khi mở tệp.
  - Đọc và băm tuần tự theo từng chunk 1 MiB.
  - Thực hiện lệnh `stat_after = os.stat(path_obj)` ngay sau khi kết thúc luồng đọc.
  - Nếu `stat_after.st_size != stat_before.st_size` hoặc `stat_after.st_mtime != stat_before.st_mtime` hoặc tổng số bytes đọc khác `stat_before.st_size`: ngay lập tức phát sinh lỗi `SourceChangedDuringReadError` (fail-closed).

---

## 5. Ranh giới Bảo vệ An toàn Hệ thống Tệp (Path Safety)

Hàm `validate_path_safety(file_path, base_dir)` kiểm tra:
1. **Chống Path Traversal:** Từ chối mọi chuỗi đường dẫn chứa thành phần `..`.
2. **Chống Symlink/Reparse Point Escape:** Kiểm tra cả `path.is_symlink()` và `os.path.islink()` trên đường dẫn ban đầu và đường dẫn đã resolve. Mọi symbolic link đều bị từ chối với `SourcePathSecurityError`.
3. **Giới hạn Thư mục Gốc:** Khi truyền `base_dir`, bắt buộc đường dẫn tệp sau khi resolve phải là con của `base_dir` (`resolved_path.relative_to(resolved_base)`).
4. **Regular File Only:** Chỉ chấp nhận tệp định dạng thông thường, từ chối thư mục, socket, FIFO hoặc thiết bị.

---

## 6. Tích hợp Với `RunManifest` (T-009) Theo `DOC-F02`

Phương thức `record_into_run_manifest(manifest, batch_result, record_only_verified_hashes=True)`:
- Kiểm tra tính tương thích của đối tượng `manifest`, gọi đúng phương thức sản xuất:
  ```python
  manifest.record_input(path=path_str, bytes_count=bytes_count, sha256_hash=hash_to_record)
  ```
- Khi `record_only_verified_hashes=True`:
  - Nguồn đạt `LOCAL_HASH_VERIFIED` $\implies$ ghi nhận mã SHA-256 thực tế.
  - Nguồn chỉ đạt `LOCAL_HASH_COMPUTED_UNAPPROVED` $\implies$ truyền `sha256_hash=None`, `RunManifest` sẽ tự động ghi nhận nhãn an toàn `"UNVERIFIED"`.

---

## 7. Bảo lưu Bất biến Quản trị OR-08 & TS-019

Thuộc tính `upstream_identity_status` của cả `SourceVerificationResult` và `BatchVerificationResult` được cố định là:
```python
UPSTREAM_IDENTITY_STATUS_UNVERIFIED = "IDENTITY_UNVERIFIED"
```
Bất kể mã băm cục bộ có khớp tuyệt đối hay không, module không bao giờ tuyên bố dữ liệu đã được chứng minh xuất xứ từ máy chủ BTS TranStats hoặc NOAA.
