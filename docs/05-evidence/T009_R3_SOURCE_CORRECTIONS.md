# T009-R3: SOURCE CODE CORRECTIONS & TECHNICAL IMPLEMENTATION

**Task ID:** `T-009` (Remediation R3)  
**Gate:** `G4`  
**Auditor:** Senior PySpark & Storage Systems Engineer  
**Execution Mode:** `CONTROLLED TARGETED REMEDIATION`  
**Date:** 2026-10-17  
**Status:** `ALL_CORRECTIONS_APPLIED_AND_VERIFIED`  

---

## 1. Chi Tiết Sửa Đổi Trong [`src/flight_pipeline/utils/run_manifest.py`](../../src/flight_pipeline/utils/run_manifest.py)

### 1.1. Khắc Phục F-01: Đồng Bộ Tuyệt Đối Mã Băm RunManifest
Định nghĩa hàm chuẩn tắc `to_bytes()` để thống nhất định dạng byte trên đĩa và hàm tính mã băm:
```python
def to_bytes(self) -> bytes:
    """Canonical byte representation of the manifest."""
    return (self.to_json() + "\n").encode("utf-8")

def calculate_sha256(self) -> str:
    """Calculate SHA-256 hash of the canonical manifest bytes."""
    return sha256(self.to_bytes()).hexdigest()

def save(self, target_path: str) -> str:
    """Save manifest JSON to file and return its exact disk SHA-256 hash."""
    p = Path(target_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    data = self.to_bytes()
    p.write_bytes(data)
    return sha256(data).hexdigest()
```
- **Kết quả:** `manifest.save(path) == sha256(Path(path).read_bytes()).hexdigest()` đạt sự đồng nhất 100%.

### 1.2. Khắc Phục F-04: Ràng Buộc Miền Giá Trị Số Nguyên Không Âm DC-11/DC-12
1. **Trong `RowAccounting`:**
   - Bổ sung `__post_init__` kiểm tra kiểu số nguyên (`int`) và giá trị không âm (`>= 0`). Nếu âm, ném ngoại lệ `ValueError`.
   - Trong `is_balanced()`, bổ sung kiểm tra an toàn: nếu bất kỳ số dòng nào $< 0$, trả về `False`.
   - Trong `calculate_ingest_acceptance_rate()`, kiểm tra $0 \le accepted \le raw$. Nếu ngoài miền, trả về `None`.
2. **Trong `MetricAccounting`:**
   - Bổ sung `__post_init__` kiểm tra kiểu số nguyên, giá trị không âm, và khẳng định $count\_metric\_valid \le count\_records$. Nếu vượt quá, ném `ValueError`.
   - Trong `calculate_metric_valid_rate()`, kiểm tra $0 \le count\_metric\_valid \le count\_records$. Khi $count\_records = 0$, trả về `None` (ZERO_DENOMINATOR). Tỷ lệ trả về luôn nằm trong khoảng $[0.0, 1.0]$.

---

## 2. Chi Tiết Sửa Đổi Trong [`src/flight_pipeline/storage/publication.py`](../../src/flight_pipeline/storage/publication.py)

### 2.1. Khắc Phục F-03: Kiểm Soát Phân Vùng Tuyệt Đối (`validate_run_id`)
Bổ sung hàm kiểm tra đường dẫn độc lập:
```python
RUN_ID_REGEX = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9_\-\.]*$")

def validate_run_id(run_id: str, runs_root: Path) -> Path:
    if not isinstance(run_id, str) or not run_id.strip():
        raise ValueError("run_id must be a non-empty string")
    run_id = run_id.strip()
    if not RUN_ID_REGEX.match(run_id):
        raise ValueError(f"Invalid run_id format: {run_id!r}")
    if any(p in run_id for p in ("..", "/", "\\", ":")):
        raise ValueError(f"Path traversal or separator detected in run_id: {run_id!r}")
    target = (runs_root / run_id).resolve()
    runs_root_resolved = runs_root.resolve()
    try:
        target.relative_to(runs_root_resolved)
    except ValueError:
        raise ValueError(f"run_id {run_id!r} escapes authorized runs_root {runs_root_resolved}")
    if target == runs_root_resolved or target.parent != runs_root_resolved:
        raise ValueError(f"run_id {run_id!r} resolves outside target directory")
    return target
```
- Ngăn chặn hoàn toàn mọi dạng payload traversal: `../`, `../../`, `/absolute`, `C:\`, chuỗi rỗng.

### 2.2. Khắc Phục F-02: Kiểm Tra Nội Dung Parquet & Đối Soát Băm Thăng Cấp
1. **Kiểm tra Magic Bytes Parquet:**
   Hàm `is_valid_parquet_file(p: Path)` kiểm tra tệp có kích thước $\ge 12$ bytes, 4 byte đầu bắt buộc là `b'PAR1'` và 4 byte cuối bắt buộc là `b'PAR1'`.
2. **Kiểm tra Bước 1:**
   - Mọi tệp có đuôi `.parquet` trong staging bắt buộc phải vượt qua `is_valid_parquet_file`. Nếu không, từ chối với trạng thái `FAILED_STAGING_CONTENT_INVALID`.
   - Ghi nhận `staging_inventory` gồm kích thước và mã băm SHA-256 của từng tệp.
3. **Kiểm tra Bước 4:**
   - Đối chiếu từng tệp thăng cấp trong `curated/runs/{run_id}` với `staging_inventory`.
   - Khẳng định 100% khớp tên, khớp kích thước byte và khớp mã băm SHA-256. Nếu sai lệch, từ chối với trạng thái `FAILED_COMPLETENESS`.

### 2.3. Khắc Phục F-05: Hoàn Nguyên Con Trỏ Nguyên Tử Tại Bước 6
Bổ sung hàm trợ giúp `_atomic_write_pointer(pointer_val, tmp_prefix)`:
- Sử dụng tệp tạm thời `.latest_run_id_*.tmp` và gọi `os.replace` nguyên tử trên NTFS với cơ chế thử lại (exponential backoff).
- Áp dụng phương thức nguyên tử này cho cả:
  1. Thao tác chuyển tiếp con trỏ (Step 5).
  2. Thao tác hoàn nguyên con trỏ khi hậu kiểm Step 6 thất bại.
