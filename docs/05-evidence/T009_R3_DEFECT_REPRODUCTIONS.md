# T009-R3: FORENSIC DEFECT REPRODUCTIONS & ROOT CAUSE ANALYSIS

**Task ID:** `T-009` (Remediation R3)  
**Gate:** `G4`  
**Auditor:** Senior PySpark & Storage Systems Engineer  
**Execution Mode:** `CONTROLLED TARGETED REMEDIATION`  
**Date:** 2026-10-17  
**Status:** `ALL_5_DEFECTS_REPRODUCED_AND_VERIFIED`  

---

## 1. Tổng Quan Tái Hiện Thực Nghiệm (Reproduction Summary)

Thực hiện nguyên tắc *Failing Tests First*, toàn bộ 5 khiếm khuyết (F-01 đến F-05) đã được kiểm chứng độc lập bằng bộ kiểm thử tự động [`tests/test_t009_r3_defect_reproductions.py`](../../tests/test_t009_r3_defect_reproductions.py) trên mã nguồn gốc R2 trước khi áp dụng bất kỳ bản vá nào.

- **Kết quả chạy trước khi sửa:** `FAILED (failures=5 / 5 tests)`.
- **Nhật ký thực thi thô (Raw Log):** [`T009_R3_LOG_REPRODUCTIONS_PRE_FIX.txt`](T009_R3_LOG_REPRODUCTIONS_PRE_FIX.txt).

---

## 2. Chi Tiết Từng Khiếm Khuyết & Nguyên Nhân Gốc Rễ

### 2.1. Defect F-01: Sai lệch mã băm RunManifest SHA-256 (`src/flight_pipeline/utils/run_manifest.py`)
- **Triệu chứng:** Giá trị trả về từ `RunManifest.save()` khác mã băm SHA-256 thực tế của tệp ghi trên đĩa:
  `AssertionError: 'ff9d2a40...' != '8e13a8c0...'`
- **Nguyên nhân gốc rễ:**
  ```python
  # Code cũ:
  content = self.to_json()
  p.write_text(content + "\n", encoding="utf-8")
  return sha256(content.encode("utf-8")).hexdigest()  # Băm content KHÔNG CÓ '\n'
  ```
  Hàm ghi tệp ghi `content + "
"`, nhưng hàm băm lại băm `content` không có ký tự xuống dòng `
`.
- **Hậu quả:** Bất kỳ quy trình kiểm toán nào kiểm tra tệp `manifest.json` trên đĩa đều thấy hash bị lệch so với hash mà hàm `save()` công bố.

### 2.2. Defect F-02: Lỗ hổng kiểm tra nội dung Staging & Thăng cấp Parquet (`src/flight_pipeline/storage/publication.py`)
- **Triệu chứng:** Một tệp văn bản thô chứa chuỗi `"THIS IS NOT PARQUET DATA!"` đặt tên là `part-000.parquet` vẫn được chấp nhận và nhận trạng thái `PUBLISHED` thành công:
  `AssertionError: True is not false : F-02 Defect: Fake parquet was erroneously accepted`
- **Nguyên nhân gốc rễ:**
  - Bước 1 chỉ kiểm tra thư mục có tệp hay không (`staging_data_files`).
  - Bước 4 chỉ so sánh số lượng tệp (`len(promoted_files) == len(staging_data_files)`).
  - Không có bước kiểm tra magic bytes của định dạng Parquet (`PAR1`), cũng không so sánh kích thước byte hay mã băm SHA-256 giữa tệp staging và tệp promoted.
- **Hậu quả:** Dữ liệu hỏng hoặc tệp giả mạo có thể lọt vào vùng dữ liệu chuẩn `curated/runs/`.

### 2.3. Defect F-03: Nguy cơ thoát thư mục qua Path Traversal trong `run_id` (`src/flight_pipeline/storage/publication.py`)
- **Triệu chứng:** Khi truyền `run_id = "../../escaped"`, hệ thống chấp nhận và tạo thư mục bên ngoài `curated/runs/`:
  `AssertionError: True is not false : F-03 Defect: Malicious run_id '../../escaped' was not rejected`
- **Nguyên nhân gốc rễ:**
  ```python
  # Code cũ:
  versioned_target = self.runs_root / run_id
  ```
  Toán tử nối đường dẫn `/` của `pathlib.Path` cho phép các ký tự `..`, `/`, `\` điều hướng ra ngoài thư mục cha mà không có bộ lọc kiểm soát phạm vi (path confinement).
- **Hậu quả:** Rủi ro ghi đè hoặc tạo tệp trái phép vào các thư mục hệ thống hoặc dữ liệu khác.

### 2.4. Defect F-04: Thiếu ràng buộc miền giá trị không âm cho DC-11/DC-12 (`src/flight_pipeline/utils/run_manifest.py`)
- **Triệu chứng:**
  - `RowAccounting(-1, -1, 0, 0).is_balanced()` trả về `True` (vì `-1 == -1 + 0 + 0`).
  - `MetricAccounting("ARR_DELAY", 100, 120).calculate_metric_valid_rate()` trả về `1.2` (lớn hơn 100%).
- **Nguyên nhân gốc rễ:**
  - `RowAccounting` không kiểm tra số nguyên không âm (`>= 0`) cho các trường số dòng.
  - `MetricAccounting` không chặn trường hợp `count_metric_valid > count_records` và không kiểm tra miền tỷ lệ $[0.0, 1.0]$.
- **Hậu quả:** Vi phạm nghiêm trọng logic toán học của hợp đồng dữ liệu chuẩn tắc DC-11 và DC-12.

### 2.5. Defect F-05: Hoàn nguyên con trỏ không nguyên tử tại Bước 6 (`src/flight_pipeline/storage/publication.py`)
- **Triệu chứng:** Tại Bước 5, việc cập nhật con trỏ tiến hành nguyên tử bằng `os.replace`. Nhưng tại Bước 6, nếu đọc lại con trỏ thấy sai lệch và cần rollback, mã nguồn lại gọi:
  ```python
  self.pointer_file.write_text(previous_pointer + "\n", encoding="utf-8")
  ```
- **Nguyên nhân gốc rễ:** Thao tác ghi trực tiếp `write_text` trên Windows NTFS không có tính nguyên tử, có thể bị lỗi file locking nếu có tiến trình khác đang mở đọc, dẫn đến tệp con trỏ bị rỗng hoặc hỏng dở dang trong quá trình rollback.
- **Hậu quả:** Rủi ro hỏng con trỏ `latest_run_id.txt` trong kịch bản xử lý sự cố.
