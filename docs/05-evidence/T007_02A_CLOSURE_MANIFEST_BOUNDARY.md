# T007-02A Final Closure RunManifest Publication Boundary Audit

**Document ID:** `T007_02A_CLOSURE_MANIFEST_BOUNDARY.md`  
**Date:** 2026-10-17  
**Task:** `T007-02A-FINAL-CLOSURE` (Fail-Closed Source Integrity Correction)  
**Parent Task:** `T-007` (Raw CSV Ingestion Pipeline)  
**Parent Gate:** `G4` (`PLANNED / NOT_COMPLETED`)  
**Status:** `AUDITED_AND_VERIFIED`  
**Engineer:** Senior Python Data Engineer & Data Provenance Auditor  

---

## 1. Ranh giới Tích hợp với Hợp đồng T-009 (RunManifest Boundary)

Trong kiến trúc tổng thể của dự án, `RunManifest` (được chuẩn hóa trong nhiệm vụ T-009) đóng vai trò là chứng thư ghi vết thực thi (provenance ledger). Danh sách `manifest.inputs` lưu trữ siêu dữ liệu của toàn bộ các tệp đầu vào phục vụ cho việc đối soát tính toàn vẹn và khả năng tái lập (reproducibility).

### 1.1. Khuyết tật Trước Sửa đổi (FIX-A04 Defect)
Trước đợt đóng này, hàm `record_into_run_manifest()` ghi nhận mọi tệp trong batch vào `manifest.inputs`, bao gồm cả những tệp không tồn tại (`SOURCE_MISSING`) hoặc lỗi đọc/cấu trúc (`SOURCE_READ_ERROR`), với giá trị giả định:
```python
manifest.add_input(path=item.relative_path, bytes=0, sha256="UNVERIFIED")
```
Hành vi này dẫn tới hai hệ lụy nghiêm trọng:
1. **Làm suy giảm tính xác thực của Ledger:** Downstream pipeline và auditor khi đọc `manifest.inputs` bị đánh lừa rằng các tệp trên đã được tiếp nhận và xử lý, trong khi thực tế dữ liệu không hề được đọc.
2. **Vi phạm nguyên tắc Fail-Closed:** Thay vì dừng pipeline ngay tại ranh giới xác thực, hệ thống cho phép dữ liệu khiếm khuyết thâm nhập vào quy trình xuất bản.

---

## 2. Thiết kế Ranh giới An toàn Mới (Safe Publication Boundary)

Hàm `record_into_run_manifest()` được tái cấu trúc triệt để với hai cơ chế phòng vệ nghiêm ngặt:

```python
def record_into_run_manifest(
    self,
    manifest: Any,
    batch_result: SourceBatchVerificationResult,
    allow_partial: bool = False,
) -> dict[str, Any]:
```

### 2.1. Chế độ Mặc định Fail-Closed (`allow_partial=False`)
- **Nguyên tắc:** Nếu batch xác thực chứa **dù chỉ một nguồn lỗi**, việc ghi nhận vào `manifest` bị từ chối lập tức.
- **Xác định Nguồn Lỗi:** Bất kỳ nguồn nào có trạng thái thuộc:
  - `SOURCE_MISSING`
  - `SOURCE_READ_ERROR`
  - `SOURCE_CHANGED_DURING_READ`
  - Hoặc `HASH_MISMATCH` (khi kiểm tra hash)
- **Hành vi:** Ném ngay ngoại lệ:
  ```python
  raise SourceIntegrityError(
      f"Cannot record batch into RunManifest: {len(failed_items)} sources failed verification. "
      f"Failed sources: {failed_items}"
  )
  ```
- **Hệ quả:** `manifest.inputs` được giữ nguyên vẹn 100%, không bị ô nhiễm bởi bất kỳ bản ghi lỗi nào.

### 2.2. Chế độ Phân đoạn Có Kiểm soát (`allow_partial=True`)
- **Mục đích:** Hỗ trợ kịch bản xử lý từng phần (partial ingestion) được cấu hình có chủ đích, hoặc phục vụ kiểm thử phân đoạn.
- **Quy tắc Tiếp nhận:** Chỉ các nguồn có trạng thái hợp lệ đã được kiểm chứng cấu trúc:
  - `SOURCE_PRESENT_METADATA_MATCH`
  - `LOCAL_HASH_COMPUTED_UNAPPROVED`
  - `LOCAL_HASH_VERIFIED`
  mới được phép ghi vào `manifest.inputs`.
- **Loại trừ Tuyệt đối Nguồn Lỗi:** Các nguồn lỗi hoàn toàn **bị loại bỏ** khỏi `manifest.inputs`.
- **Cơ chế Báo cáo Kiểm toán:** Hàm trả về từ điển kết quả chi tiết:
  ```python
  return {
      "recorded_count": int,
      "rejected_count": int,
      "rejected_details": list[dict],
  }
  ```
  cho phép caller kiểm toán chính xác những tệp nào đã bị từ chối và lý do tương ứng.

---

## 3. Bằng chứng Kiểm thử Tự động (Unit Test Evidence)

Các ca kiểm thử trong `tests/test_t007_source_validator.py` đã xác nhận hành vi bảo vệ ranh giới:

### 3.1. Từ chối Ghi Khi Batch Có Lỗi (`test_closure_fix_a04_run_manifest_rejects_failed_batch`)
- Thiết lập batch kiểm tra trong đó một tệp bình thường và một tệp bị lỗi đọc (thư mục giả danh tệp CSV).
- Gọi `record_into_run_manifest(manifest, batch, allow_partial=False)`.
- Kết quả: Ném `SourceIntegrityError`, `manifest.inputs` có độ dài 0 (không bị ghi đè bất kỳ bản ghi nào).

### 3.2. Chế độ Partial Cách ly Tuyệt đối Nguồn Lỗi (`test_closure_fix_a04_run_manifest_partial_mode_rejects_failed_sources`)
- Gọi với `allow_partial=True` trên batch chứa cả nguồn hợp lệ và nguồn lỗi.
- Kết quả:
  - `manifest.inputs` chỉ chứa duy nhất nguồn hợp lệ với đầy đủ kích thước byte và mã băm thật.
  - Báo cáo trả về: `recorded_count = 1, rejected_count = 1`.
  - Trường `rejected_details` chỉ rõ tệp lỗi và trạng thái `SOURCE_READ_ERROR`.

Kết luận: Ranh giới tích hợp giữa `SourceValidator` và `RunManifest` bảo đảm tuyệt đối tính toàn vẹn và fail-closed của hồ sơ provenance.
