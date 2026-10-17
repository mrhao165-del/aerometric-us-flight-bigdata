# T009-UNBLOCK-R2: CODE CHANGE REVIEW & TECHNICAL SPECIFICATION

**Task ID:** `T009-UNBLOCK-R2` (Targeted Git Metadata Exclusion & Validator Reconciliation)  
**Gate:** `G4`  
**Auditor:** Senior Software Engineer, Repository Governance Engineer & Independent QA Engineer  
**Timestamp:** 2026-10-17T08:39:00+07:00  
**Status:** `CHANGE_REVIEWED_AND_APPLIED`  

---

## 1. Mục Tiêu & Ranh Giới Kỹ Thuật Của Thay Đổi (Technical Scope)

Thay đổi được áp dụng duy nhất cho tệp:
[`tools/check_working_tree_consistency.py`](../../tools/check_working_tree_consistency.py)

Tuân thủ nghiêm ngặt 8 yêu cầu kỹ thuật tại Mục 4 của chỉ thị Project Lead:
1. **Chỉ bỏ qua Git metadata nội bộ:** Sử dụng điều kiện neo chặt đường dẫn tương đối tại gốc repository: `f.relative_to(root).parts[0] != ".git"`.
2. **Không bỏ qua toàn bộ hidden files:** Các tệp chấm như `.gitignore`, `.github/` (nếu có sau này), `.gitattributes` không bị ảnh hưởng vì `parts[0]` của chúng khác `".git"`.
3. **Không vô hiệu hóa kiểm tra unrecognized files:** Logic hạch toán cây làm việc `unrecognized = extra_files - ...` được bảo toàn nguyên vẹn 100%.
4. **Không sửa quy tắc canonical evidence filename:** Các biểu thức chính quy `EVIDENCE_FILENAME_RE`, `BACKUP_FILENAME_RE` giữ nguyên.
5. **Không vô hiệu hóa kiểm chứng SHA-256:** Quy trình đối chiếu byte và băm SHA-256 đối với mọi deliverable giữ nguyên.
6. **Không làm giảm các kiểm soát dataset/schema/KPI:** Toàn bộ 383 assertions khác của bộ kiểm tra hoạt động bình thường.
7. **Không tự bỏ qua mọi thư mục trong `.gitignore`:** Không đọc tệp `.gitignore` để tự động bỏ qua thư mục; chỉ bỏ qua duy nhất siêu dữ liệu `.git/`.
8. **Không sửa kết quả test hoặc giảm tiêu chí PASS:** Không dùng fallback nhân tạo (`or True`) hay giảm số lượng assertion.

---

## 2. Baseline Kiểm Toán Trước & Sau Thay Đổi (Cryptographic Baselines)

| Thuộc Tính Kiểm Toán | Baseline Trước Sửa Đổi (Pre-Change) | Trạng Thái Sau Sửa Đổi (Post-Change) |
|---|---|---|
| **Đường dẫn tệp** | `tools/check_working_tree_consistency.py` | `tools/check_working_tree_consistency.py` |
| **Kích thước byte** | `23,426 bytes` | `23,642 bytes` |
| **Mã băm SHA-256** | `4f53a91458a3fabe896edb63b38198c0280d11d15638e6bef0c6f44164d013c9` | `8ed88ff6c3b0bffc4130732a4f4a346106b9860eece25a351a1044d30822b894` |
| **Git Baseline Commit** | `5d70035863a343d5f5866d9300b90d0c5fce22f8` | `5d70035863a343d5f5866d9300b90d0c5fce22f8` (Working Tree Modified) |
| **Ảnh hưởng `PACKAGE_MANIFEST.json`** | Không thuộc manifest (0% ảnh hưởng) | Không thuộc manifest (0% ảnh hưởng, manifest ghim cứng) |
| **Ảnh hưởng `SOURCE_MANIFEST.json`** | Không thuộc manifest (0% ảnh hưởng) | Không thuộc manifest (0% ảnh hưởng, manifest ghim cứng) |
| **Trạng thái Sổ đăng ký Bằng chứng** | Được đăng ký tại `EVIDENCE_DELIVERABLE_REGISTER.json` | Cập nhật hash và bytes mới tương ứng trong cùng nhiệm vụ |

---

## 3. Bản Ghi Chi Tiết Thay Đổi Mã Nguồn (Detailed Git Diff)

```diff
diff --git a/tools/check_working_tree_consistency.py b/tools/check_working_tree_consistency.py
index 214dfcc..8de8346 100644
--- a/tools/check_working_tree_consistency.py
+++ b/tools/check_working_tree_consistency.py
@@ -174,7 +174,11 @@ def run_consistency_check(root_dir: Path):
         "Doc group counts and unique roles",
     )
 
-    active = [f for f in root.rglob("*.md") if "inputs" not in f.parts]
+    active = [
+        f
+        for f in root.rglob("*.md")
+        if "inputs" not in f.parts and f.relative_to(root).parts[0] != ".git"
+    ]
     require(all(f.stat().st_size > 100 for f in active), "Active docs are nonempty")
 
     # 2. Markdown reference integrity (no broken docs/... paths)
@@ -535,18 +539,18 @@ def run_consistency_check(root_dir: Path):
                         registered_deliverables[dp] = item
 
         # 14. Working-tree accounting: All files in repo are either manifest release files, raw data, the registry itself, or verified registered deliverables
-        # Check that no symlinks exist anywhere in the working-tree
+        # Check that no symlinks exist anywhere in the working-tree (excluding root .git)
         symlinks_in_repo = [
             f.relative_to(root).as_posix()
             for f in root.rglob("*")
-            if f.is_symlink()
+            if f.is_symlink() and f.relative_to(root).parts[0] != ".git"
         ]
         require(
             len(symlinks_in_repo) == 0,
             "No symbolic links in working-tree"
             + (": " + repr(symlinks_in_repo[:5]) if symlinks_in_repo else ""),
         )
-        # Ignore transient Python bytecode cache files (__pycache__ / .pyc)
+        # Ignore transient Python bytecode cache files (__pycache__ / .pyc) and root .git metadata
         actual_files = {
             f.relative_to(root).as_posix()
             for f in root.rglob("*")
@@ -554,6 +558,7 @@ def run_consistency_check(root_dir: Path):
             and f.name != "PACKAGE_MANIFEST.json"
             and "__pycache__" not in f.parts
             and not f.name.endswith(".pyc")
+            and f.relative_to(root).parts[0] != ".git"
         }
         extra_files = actual_files - manifest_paths
```

---

## 4. Lý Giải Kỹ Thuật Về Biểu Thức Lựa Chọn (Technical Rationale)

1. **Tại sao sử dụng `f.relative_to(root).parts[0] != ".git"` thay vì `".git" not in f.parts`?**
   - Biểu thức `".git" not in f.parts` sẽ loại trừ bất kỳ thư mục con nào có tên `.git` ở bất kỳ đâu trong repository (ví dụ `subfolder/.git/`). Điều này có thể che giấu các cấu trúc Git lồng nhau không hợp lệ hoặc các tệp lạ cố ý đặt tên trong thư mục con `.git`.
   - Ngược lại, `f.relative_to(root).parts[0] != ".git"` chỉ kiểm tra phần tử đầu tiên của đường dẫn tương đối tính từ gốc repository. Do đó, nó **chỉ loại trừ duy nhất thư mục Git ở gốc dự án**, hoàn toàn không ảnh hưởng đến bất kỳ vị trí nào khác.
2. **Xử lý an toàn đường dẫn:**
   - Trong `root.rglob("*")`, biến `f` luôn đại diện cho một hậu duệ thực sự của `root` (không bao gồm chính `root`). Do đó `len(f.relative_to(root).parts) >= 1` luôn được bảo đảm, không bao giờ gây ra lỗi ngoại lệ `IndexError`.
