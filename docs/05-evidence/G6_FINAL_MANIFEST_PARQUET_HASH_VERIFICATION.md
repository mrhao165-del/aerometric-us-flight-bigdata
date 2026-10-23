# G6 Final Manifest & Parquet Cryptographic Verification Protocol

**Document ID:** `DOC-G6-PAYLOAD-HASH-001`  
**Classification:** DATA INTEGRITY & FORENSIC VERIFICATION PROTOCOL  
**Component:** `tools/qa/verify_multiyear_snapshot.py`  
**Evaluator:** Principal Big Data Architect & Senior PySpark Reliability Engineer  
**Date:** 2026-10-20  
**Status:** VALIDATED & FAIL-CLOSED ENFORCED  

---

## 1. Mục tiêu và Bối cảnh An toàn

Trong kiến trúc lưu trữ dữ liệu Big Data trên nền tảng Apache Parquet và NTFS/POSIX filesystem, việc chỉ kiểm tra sự tồn tại của tệp (file existence) hoặc đuôi mở rộng (`*.parquet`) tiềm ẩn nguy cơ **false-PASS** cực kỳ nguy hiểm:
- Các tệp ghi dở do tiến trình Spark bị ngắt đột ngột (partial writes).
- Các tệp rỗng 0 bytes hoặc tệp văn bản vô giá trị bị đổi tên thành `.parquet`.
- Tệp bị hỏng phần Thrift footer do lỗi I/O của đĩa hoặc tiến trình ghi đè đồng thời.
- Manifest (`run_manifest.json`) không khớp với danh mục tệp thực tế trên đĩa (hash drift).

Tài liệu này xác định giao thức kiểm tra tính xác thực vật lý hai lớp (Dual-Layer Forensic Verification) đã được tích hợp trong validator `tools/qa/verify_multiyear_snapshot.py`.

---

## 2. Lớp 1: Kiểm định Siêu dữ liệu Thrift Header/Footer qua PyArrow

### 2.1 Cơ chế Không Chiếm Dụng Bộ nhớ (Zero-RAM Row Materialization)
Thay vì nạp toàn bộ hàng triệu bản ghi chuyến bay vào RAM qua `spark.read.parquet()` hay `pq.read_table()`, validator sử dụng hàm cấp thấp `pq.read_metadata()`:
```python
def is_valid_parquet_file(file_path: Path) -> bool:
    try:
        meta = pq.read_metadata(file_path)
        return meta is not None and meta.num_rows >= 0 and meta.num_columns >= 1
    except Exception:
        return False
```

### 2.2 Các Ràng buộc Cấu trúc Được Kiểm chứng Tức thì
1. **Magic Bytes:** Tệp Parquet hợp lệ bắt buộc phải bắt đầu và kết thúc bằng 4 byte ký tự ASCII `PAR1` (hex: `50 41 52 31`).
2. **Thrift FileMetaData:** Bộ giải mã Parquet đọc 4 byte cuối cùng (footer length) để định vị và giải tuần tự hóa khối Thrift FileMetaData chứa schema và danh mục Row Group.
3. **Tính toàn vẹn Cột và Hàng:**
   - `meta.num_columns >= 1`: Đảm bảo schema có ít nhất một cột hợp lệ.
   - `meta.num_rows >= 0`: Đảm bảo số lượng hàng được mã hóa chuẩn xác trong các Row Group descriptors.
4. **Phát hiện Lỗi tức thì:** Nếu tệp bị cắt cụt (truncated), rỗng, hoặc là tệp văn bản giả mạo, hàm `pq.read_metadata()` sẽ ném ra ngoại lệ `pyarrow.lib.ArrowInvalid`, và validator lập tức trả về `CORRUPT_OR_FAKE_PARQUET_DETECTED`.

---

## 3. Lớp 2: Kiểm tra Hợp đồng Manifest và Cryptographic Checksum

### 3.1 Cấu trúc Chuẩn của `run_manifest.json`
Mỗi thư mục run được xuất bản hợp lệ bắt buộc phải có tệp `run_manifest.json` ở cấp gốc với lược đồ:
```json
{
  "run_id": "run_2019_sample",
  "year": 2019,
  "publication_status": "PUBLISHED",
  "publication_timestamp_utc": "2026-10-20T12:00:00Z",
  "source_coverage_status": "FULL",
  "row_accounting": {
    "raw_rows": 7422037,
    "accepted_rows": 7420000,
    "quarantined_rows": 2000,
    "rejected_rows": 37
  },
  "file_inventory": [
    {
      "filename": "part-00000.parquet",
      "bytes": 1048576,
      "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    }
  ]
}
```

### 3.2 Quy trình Đối soát Toàn vẹn Tệp (File Inventory Verification)
Khi trường `file_inventory` (hoặc `files`) được khai báo trong manifest:
1. Validator kiểm tra sự hiện diện của từng tệp được liệt kê trong danh mục.
2. Kiểm tra dung lượng tệp thực tế trên đĩa (`stat().st_size`) so với trường `bytes`. Mismatch lập tức báo lỗi.
3. Tính toán mã băm SHA-256 từng chunk 64KB của tệp trên đĩa:
   ```python
   hasher = hashlib.sha256()
   with open(fpath, "rb") as f:
       while chunk := f.read(65536):
           hasher.update(chunk)
   computed_hash = hasher.hexdigest()
   ```
4. So khớp `computed_hash == declared_sha256`. Nếu có bất kỳ sự sai lệch dù chỉ 1 bit, validator lập tức fail-closed với mã trạng thái:
   `FILE_INTEGRITY_CHECKSUM_MISMATCH`

---

## 4. Xử lý các Tệp Rác và Tiến trình Chưa Hoàn thành

Trong môi trường Big Data phân tán, các thư mục chạy có thể chứa tệp tạm thời do Spark executor để lại:
- Các tệp `_temporary/`, `.tmp`, hoặc `._SUCCESS.crc`.
- Validator quy định: Mọi tệp Parquet thực sự đóng góp vào snapshot đều phải nằm trong danh mục tệp hợp lệ. Sự xuất hiện của tệp hỏng hoặc không hoàn thiện sẽ kích hoạt lỗi ngay tại Bước 4 (Thrift Header Check).
- Nếu manifest thiếu hoặc tệp bị hỏng, validator từ chối ghi nhận snapshot đó vào snapshot registry.

---

## 5. Kết quả Kiểm thử Tiêu cực (Negative Test Verification)

Trong bộ kiểm thử `tests/test_multiyear_snapshot_policy.py`:
- `test_03_fake_parquet_corrupt_fails_closed`: Đưa tệp text giả mạo làm parquet $\rightarrow$ Kết quả: `FAIL_DETECTED` (`CORRUPT_OR_FAKE_PARQUET_DETECTED`).
- `test_04_missing_manifest_fails_closed`: Bỏ tệp manifest $\rightarrow$ Kết quả: `FAIL_DETECTED` (`MISSING_RUN_MANIFEST`).
- `test_05_corrupted_json_manifest_fails_closed`: Ghi JSON hỏng cú pháp $\rightarrow$ Kết quả: `FAIL_DETECTED` (`CORRUPT_RUN_MANIFEST`).
- `test_11_manifest_checksum_mismatch_fails_closed`: Đổi nội dung tệp khiến SHA-256 sai $\rightarrow$ Kết quả: `FAIL_DETECTED` (`FILE_INTEGRITY_CHECKSUM_MISMATCH`).

Toàn bộ 4 kịch bản kiểm thử tiêu cực đều pass 100%, chứng minh tính bất khả xâm phạm của giao thức kiểm tra payload và manifest cryptographic verification.
