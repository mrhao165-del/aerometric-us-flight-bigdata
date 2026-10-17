# T009-UNBLOCK-R2: ROOT CAUSE ANALYSIS REPORT

**Task ID:** `T009-UNBLOCK-R2` (Targeted Git Metadata Exclusion & Validator Reconciliation)  
**Gate:** `G4`  
**Auditor:** Senior Software Engineer, Repository Governance Engineer & Independent QA Engineer  
**Timestamp:** 2026-10-17T08:38:30+07:00  
**Status:** `ROOT_CAUSE_CONFIRMED`  

---

## 1. Tái Hiện Lỗi Khách Quan (Failure Reproduction in Live Repository)

### 1.1. Lệnh thực thi & Thông số môi trường:
- **Lệnh thực thi:** `python tools/check_working_tree_consistency.py`
- **Môi trường:** `Python 3.10.11`, `Windows 10`
- **Git HEAD tại thời điểm tái hiện:** `5d70035863a343d5f5866d9300b90d0c5fce22f8` (Branch: `master`)
- **Trạng thái Working Tree:** `clean` (`nothing to commit, working tree clean`)
- **Exit Code thực tế:** **`1`** (FAIL)
- **Số lượng Assertions:** **`383 PASS, 2 FAIL`** (trên tổng số 385 assertions của kịch bản).

### 1.2. Nhật ký lỗi chi tiết trích xuất:
```text
FAIL: No unrecognized stray files in working-tree: ['.git/COMMIT_EDITMSG', '.git/HEAD', '.git/config', '.git/description', '.git/hooks/applypatch-msg.sample', ... (227 files)]
FAIL: All extra working-tree files cleanly accounted for
```

---

## 2. Phân Tích & Phân Loại Danh Sách Tệp Bị Báo Lỗi (File Inventory Breakdown)

Thực hiện kiểm kê lập trình toàn bộ 227 tệp bị báo lỗi `unrecognized`:

| Tiêu Chí Phân Loại | Số Lượng Tệp | Tỷ Lệ | Danh Sách Chi Tiết |
|---|:---:|:---:|---|
| **Tệp nằm trong thư mục `.git/`** | **227** | **100.0%** | `.git/HEAD`, `.git/config`, `.git/index`, `.git/COMMIT_EDITMSG`, 209 tệp đối tượng Git trong `.git/objects/**`, 14 tệp mẫu trong `.git/hooks/**`, các tệp con trỏ nhánh trong `.git/refs/**`. |
| **Tệp KHÔNG thuộc thư mục `.git/`** | **0** | **0.0%** | Không có bất kỳ tệp lạ nào ngoài Git trong toàn bộ cây làm việc của repository. |

---

## 3. Phân Tích Cơ Chế Mã Nguồn Gây Lỗi (Code-Level Root Cause)

### 3.1. Điểm khuyết tật tại `tools/check_working_tree_consistency.py`:
Tại dòng 550–557 của kịch bản kiểm toán:
```python
# Đoạn mã gốc gây lỗi:
actual_files = {
    f.relative_to(root).as_posix()
    for f in root.rglob("*")
    if (f.is_file() or f.is_symlink())
    and f.name != "PACKAGE_MANIFEST.json"
    and "__pycache__" not in f.parts
    and not f.name.endswith(".pyc")
}
```

### 3.2. Cơ chế kích hoạt lỗi:
1. **Trước khi có Git (Giai đoạn G0–G3 và trước Phase D của T009-UNBLOCK-R1):**
   - Thư mục `.git/` hoàn toàn chưa tồn tại trên đĩa.
   - Hàm `root.rglob("*")` chỉ quét qua các tệp tài liệu, kịch bản QA, tệp bằng chứng và dữ liệu thô.
   - Toàn bộ các tệp này đều thuộc `manifest_paths`, `raw_data_files`, `registry_self`, hoặc `verified_deliv_paths`.
   - Kết quả: `unrecognized = set()` $\implies$ `385 PASS, 0 FAIL` (Exit Code 0).
2. **Sau khi thực hiện `git init` (Phase D của T009-UNBLOCK-R1):**
   - Lệnh `git init` tạo ra thư mục siêu dữ liệu `.git/` tại thư mục gốc repository để quản lý phiên bản.
   - Hàm `root.rglob("*")` duyệt đệ quy toàn bộ thư mục con bao gồm `.git/`.
   - Điều kiện lọc chỉ loại trừ bytecode Python (`__pycache__` và `.pyc`) mà **không có điều kiện loại trừ siêu dữ liệu Git `.git/`**.
   - Do `.git/` không nằm trong bản kê phát hành tĩnh `PACKAGE_MANIFEST.json`, không phải CSV thô trong `data/raw/`, và không nằm trong sổ đăng ký `EVIDENCE_DELIVERABLE_REGISTER.json`, validator đã tự động xếp toàn bộ 227 tệp nội bộ của Git vào danh sách `unrecognized stray files`.
   - Do đó, cả hai assertions tại dòng 583 (`len(unrecognized) == 0`) và dòng 588 (`len(extra_files) == ...`) đều bị đánh trượt.

---

## 4. Tại Sao Lỗi Không Được Tự Sửa Trong T009-UNBLOCK-R1?

Trong phiên làm việc `T009-UNBLOCK-R1`, Mục 4 của chỉ thị Project Lead quy định:
> *"Nếu validator tiếp tục FAIL, không được tự chỉnh validator để làm cho PASS. Phân tích nguyên nhân, lưu bằng chứng, STOP."*

AI Agent đã nghiêm chỉnh tuân thủ nguyên tắc an toàn này: bảo lưu nguyên vẹn kịch bản validator, không tự ý sửa đổi khi chưa có sự phê duyệt, lưu trữ nhật ký lỗi trung thực và báo cáo lên Project Lead với phán quyết `READY_WITH_OPEN_CONDITIONS`. 

Việc phê duyệt chính thức tại nhiệm vụ `T009-UNBLOCK-R2` cung cấp cơ sở thẩm quyền đầy đủ để giải quyết dứt điểm điểm nghẽn kỹ thuật này.
