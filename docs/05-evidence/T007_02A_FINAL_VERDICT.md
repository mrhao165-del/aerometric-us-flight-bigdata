# T007-02A Final Verdict & Readiness Record

**Document ID:** `T007_02A_FINAL_VERDICT.md`  
**Date:** 2026-10-17  
**Task:** `T007-02A` (Source Inventory & Local Hash Verifier Implementation)  
**Parent Task:** `T-007` (Raw CSV Ingestion Pipeline)  
**Parent Gate:** `G4` (`PLANNED / NOT_COMPLETED`)  
**Verdict:** **`T007_02A_READY_FOR_HUMAN_REVIEW`**  
**Auditor / Reviewer:** Senior Big Data Architect & Independent Technical Reviewer  

---

## 1. Kết luận Chính thức (Official Verdict)

Subtask **`T007-02A` (Source Inventory & Local Hash Verifier Implementation)** đã hoàn thành toàn diện toàn bộ mục tiêu kỹ thuật, kiểm thử và tài liệu hóa theo đúng ủy quyền có kiểm soát của Project Lead con người.

Trạng thái chính thức đề xuất:
$$\mathbf{T007\_02A = READY\_FOR\_HUMAN\_REVIEW}$$

Toàn bộ các điều kiện nghiệm thu (Definition of Done) đã được thỏa mãn tuyệt đối:
- [x] **Source Inventory Baseline:** Định nghĩa chính xác 9 tệp CSV nguồn hàng không 2016–2024, tổng cộng 54,674,003 dòng và 15,196,366,173 bytes.
- [x] **Streaming SHA-256 Hasher:** Triển khai thuật toán băm theo khối 1 MiB, bảo đảm bộ nhớ RAM $O(1)$ (< 2 MB) và cơ chế kiểm tra kép `stat_before`/`stat_after` phát hiện xung đột ghi tệp (`SourceChangedDuringReadError`).
- [x] **Filesystem Safety:** Chặn hoàn toàn path traversal (`..`), symlinks/reparse points và root directory escapes.
- [x] **State Disjointness:** Tách biệt rõ ràng giữa candidate hash chưa duyệt (`LOCAL_HASH_COMPUTED_UNAPPROVED`) và hash đã duyệt (`LOCAL_HASH_VERIFIED`). Tuyệt đối không tự động nâng cấp trạng thái khi chưa có approved baseline.
- [x] **Strict Raw Data Isolation:** Không đọc, không mở stream và không tính hash bất kỳ byte nào từ 15.2 GB CSV thật trong `data/raw/tabular/`. 100% kiểm thử thực thi trên synthetic fixtures trong thư mục tạm.
- [x] **Governance Invariants:**
  - `OR-08` / `TS-019`: Cố định `upstream_identity_status = "IDENTITY_UNVERIFIED"`.
  - `DOC-F01`: Xác định rõ `SOURCE_MANIFEST.json` quản lý 13 tài liệu audit, không quản lý raw CSV hashes.
  - `DOC-F02`: Tích hợp chính xác với `RunManifest.record_input(path, bytes_count, sha256_hash)`.
- [x] **Downstream Tasks & Gates Preserved:**
  - Subtask `T007-02B` chưa thực thi (chờ phê duyệt riêng).
  - Subtasks `T007-03` đến `T007-07` giữ nguyên trạng thái `LOCKED`.
  - Task `T-008` nghiêm ngặt giữ trạng thái `NOT_STARTED`.
  - Gate `G4` nghiêm ngặt giữ trạng thái `PLANNED / NOT_COMPLETED`.

---

## 2. Đề xuất Kế hoạch Thực thi Tiếp theo: Subtask `T007-02B`

Nhằm hoàn thiện mục tiêu `TS-019` (Local Content Snapshot Integrity) trước khi bước sang giai đoạn phân tích cấu trúc dữ liệu thô, kính trình Project Lead xem xét ủy quyền riêng cho **Subtask `T007-02B`**:

### Kế hoạch Triển khai Subtask `T007-02B`:
1. **Chế độ thực thi:** `READ_ONLY_RAW_DATA_SNAPSHOT_HASHING`.
2. **Quy trình thực hiện:**
   - Cấp quyền đọc chỉ đọc (read-only stream) cho module `SourceValidator` trên 9 tệp CSV trong `data/raw/tabular/{year}/flight_with_weather_{year}.csv`.
   - Tính toán streaming SHA-256 cho toàn bộ 15,196,366,173 bytes bằng thuật toán khối 1 MiB đã được kiểm chứng ở `T007-02A`.
   - Lập bảng kết quả ứng viên (Candidate Baseline SHA-256 Table) kèm đối chiếu kích thước byte và mtime thực tế.
   - Trình bảng kết quả lên Project Lead phê duyệt chính thức để đóng băng thành Reference Baseline cho toàn bộ các gate tiếp theo.
3. **Cam kết:** Không ghi đè, không sửa đổi dữ liệu thô; không bắt đầu `T007-03..07` hoặc `T-008` khi chưa có lệnh tiếp theo.
