# T007-02A T-009 API Compatibility & Integration Verification

**Document ID:** `T007_02A_T009_API_COMPATIBILITY.md`  
**Date:** 2026-10-17  
**Task:** `T007-02A` (Source Inventory & Local Hash Verifier Implementation)  
**Parent Task:** `T-007` (Raw CSV Ingestion Pipeline)  
**Status:** `VERIFIED_PASS`  
**Engineer:** Big Data Integration Engineer & Independent API Auditor  

---

## 1. Mục tiêu Kiểm toán Tương thích

Kiểm chứng tính tương thích giao diện (API Compatibility) giữa module mới phát triển `src/flight_pipeline/ingestion/source_validator.py` và các module nền tảng của Task `T-009` (đã được nghiệm thu chính thức), đặc biệt là mô hình quản lý nhật ký thực thi `RunManifest`.

---

## 2. Chi tiết Chữ ký API và Hiệu chỉnh DOC-F02

### 2.1. Kiểm tra Phương thức `RunManifest.record_input`
Tại tệp `src/flight_pipeline/utils/run_manifest.py` (dòng 155–161):
```python
def record_input(self, path: str, bytes_count: int, sha256_hash: Optional[str] = None) -> None:
    """Record an audited input source file."""
    self.inputs.append({
        "path": path,
        "bytes": bytes_count,
        "sha256": sha256_hash or "UNVERIFIED",
    })
```

- **Kết quả kiểm toán đối chiếu:**
  1. Không tồn tại phương thức `add_input()` trong `RunManifest`.
  2. Phương thức chuẩn là `record_input(path, bytes_count, sha256_hash)`.
  3. Khi `sha256_hash` nhận giá trị `None` hoặc chuỗi rỗng, `RunManifest` gán mặc định nhãn `"UNVERIFIED"`.

### 2.2. Triển khai Adapter Tương thích trong `SourceValidator`
Trong `source_validator.py`:
```python
def record_into_run_manifest(
    self,
    manifest: Any,
    batch_result: BatchVerificationResult,
    record_only_verified_hashes: bool = True,
) -> None:
    if not hasattr(manifest, "record_input"):
        raise SourceConfigurationError(
            "Supplied manifest object does not implement record_input(path, bytes_count, sha256_hash) per DOC-F02"
        )

    for year in sorted(batch_result.results.keys()):
        res = batch_result.results[year]
        path_str = res.path
        bytes_count = res.actual_byte_size if res.actual_byte_size is not None else 0

        if res.is_verified and res.computed_sha256:
            hash_to_record = res.computed_sha256
        elif not record_only_verified_hashes and res.computed_sha256:
            hash_to_record = res.computed_sha256
        else:
            hash_to_record = None

        manifest.record_input(path=path_str, bytes_count=bytes_count, sha256_hash=hash_to_record)
```

- **Quy tắc an toàn:**
  - Nếu nguồn đã được kiểm chứng khớp baseline (`is_verified = True`), mã băm SHA-256 được chuyển giao cho `RunManifest`.
  - Nếu nguồn mới chỉ có candidate hash chưa được duyệt (`LOCAL_HASH_COMPUTED_UNAPPROVED`), `hash_to_record` là `None`, và `RunManifest` sẽ tự động ghi nhận là `"UNVERIFIED"`.

---

## 3. Ranh giới với SafePublisher (T-009 Storage)

- Module `src/flight_pipeline/storage/publication.py` (`SafePublisher`) không bị sửa đổi.
- Module `source_validator.py` không thực hiện bất kỳ lời gọi nào tới `SafePublisher.publish()` hoặc `publish_dataset()`.
- Việc xuất bản dữ liệu Parquet thuộc trách nhiệm của các subtask sau (`T007-06`/`T007-07`) sau khi toàn bộ chu trình nạp, làm sạch và xác thực hoàn tất.

---

## 4. Bằng chứng Kiểm thử (Ca kiểm thử API-01)

Bài kiểm thử `test_api_01_run_manifest_record_input_compatibility` tại `tests/test_t007_source_validator.py` đã xác nhận:
1. Ghi nhận thành công các tệp nguồn vào danh sách `manifest.inputs`.
2. Định dạng kiểu dữ liệu đầu vào: `path` (chuỗi), `bytes` (số nguyên), `sha256` (chuỗi hash 64 ký tự hoặc `"UNVERIFIED"`).
3. Không làm biến dạng cấu trúc JSON canonical của `RunManifest`.
4. Trạng thái kiểm thử: **`PASS`**.
