# T007-02A Final Closure Batch Verification Invariants & State Matrix

**Document ID:** `T007_02A_CLOSURE_BATCH_INVARIANTS.md`  
**Date:** 2026-10-17  
**Task:** `T007-02A-FINAL-CLOSURE` (Fail-Closed Source Integrity Correction)  
**Parent Task:** `T-007` (Raw CSV Ingestion Pipeline)  
**Parent Gate:** `G4` (`PLANNED / NOT_COMPLETED`)  
**Status:** `AUDITED_AND_VERIFIED`  
**Engineer:** Senior Python Data Engineer & Independent QA Reviewer  

---

## 1. Tổng quan và Nguyên tắc Bất biến Toán học (Mathematical Invariants)

Trong các hệ thống phân tán và pipeline xử lý dữ liệu lớn, việc tổng hợp trạng thái của một tập hợp các nguồn (batch verification) tiềm ẩn nguy cơ xuất hiện ngụy biện chân lý rỗng (vacuous truth) hoặc bỏ sót các lỗi ngoại lệ (fail-open leak) nếu quan hệ logic giữa trạng thái từng bản ghi và cờ tổng hợp của batch không được ràng buộc chặt chẽ.

Nhiệm vụ `T007-02A-FINAL-CLOSURE` thiết lập và chứng minh bốn nguyên tắc bất biến fail-closed tuyệt đối trong `src/flight_pipeline/ingestion/source_validator.py`:

1. **Bất biến Không Rỗng (Non-Empty Invariant - FIX-A01):**
   $$\text{Batch}(\emptyset) \implies \text{all\_present} = \text{False} \land \text{all\_sizes\_match} = \text{False} \land \text{all\_hashes\_verified} = \text{False}$$
   Một tập kiểm tra rỗng không bao giờ được phép mang giá trị chân lý `True`. `SourceValidator.__init__` từ chối khởi tạo với `SourceConfigurationError` nếu inventory rỗng.

2. **Bất biến Hiện diện Tệp Hợp lệ (Presence Invariant - FIX-A02):**
   $$\text{all\_present} \iff \forall s \in S: \left(\text{state}(s) \notin \{\text{SOURCE\_MISSING}, \text{SOURCE\_READ\_ERROR}, \text{SOURCE\_CHANGED\_DURING\_READ}\}\right)$$
   Nếu một nguồn không tồn tại, hoặc trỏ tới thư mục/reparse point, hoặc bị lỗi I/O, hoặc thay đổi kích thước trong quá trình đọc, thì `all_present` bắt buộc phải là `False`.

3. **Bất biến Khớp Dung lượng (Size Match Invariant - FIX-A02):**
   $$\text{all\_sizes\_match} \iff \text{all\_present} \land \forall s \in S: \left(\text{state}(s) \neq \text{SIZE\_MISMATCH}\right)$$
   Điều kiện tiên quyết để `all_sizes_match = True` là `all_present` phải bằng `True` và mọi nguồn phải có kích thước byte khớp chính xác với manifest chuẩn.

4. **Bất biến Kiểm thực Mã băm (Hash Verification Invariant - FIX-A01, FIX-A02):**
   $$\text{all\_hashes\_verified} \iff \text{compute\_hash} \land \text{all\_present} \land \text{all\_sizes\_match} \land \forall s \in S: \left(\text{state}(s) = \text{LOCAL\_HASH\_VERIFIED}\right)$$
   Một batch chỉ được coi là xác thực mã băm thành công khi và chỉ khi 100% các nguồn cấu thành đều đạt trạng thái `LOCAL_HASH_VERIFIED`.

---

## 2. Ma trận Trạng thái Chi tiết (State Transition & Batch Flag Matrix)

Bảng dưới đây quy định hành vi tất định của `verify_all_sources()` khi một nguồn cá thể $s_i$ rơi vào từng trạng thái trong tập $S$:

| Trạng thái Cá thể của Nguồn ($s_i$) | Ý nghĩa Kỹ thuật | `all_present` | `all_sizes_match` | `all_hashes_verified` | `has_unapproved_candidate_hashes` |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **`SOURCE_MISSING`** | Tệp không tồn tại trên filesystem | **`False`** | **`False`** | **`False`** | Không đổi |
| **`SOURCE_READ_ERROR`** | Là thư mục, symlink, junction, hoặc lỗi I/O | **`False`** | **`False`** | **`False`** | Không đổi |
| **`SOURCE_CHANGED_DURING_READ`** | Mtime hoặc byte size thay đổi khi đang băm | **`False`** | **`False`** | **`False`** | Không đổi |
| **`SIZE_MISMATCH`** | Tệp tồn tại nhưng sai số byte kích thước | `True`* | **`False`** | **`False`** | Không đổi |
| **`SOURCE_PRESENT_METADATA_MATCH`** | Dung lượng khớp, chưa kích hoạt tính hash | `True`* | `True`* | **`False`** | Không đổi |
| **`HASH_MISMATCH`** | Dung lượng khớp, mã băm tính được sai khác | `True`* | `True`* | **`False`** | Không đổi |
| **`BASELINE_PENDING_APPROVAL`** | Nguồn chưa có baseline hash đã phê duyệt | `True`* | `True`* | **`False`** | **`True`** |
| **`LOCAL_HASH_COMPUTED_UNAPPROVED`** | Đã băm xong nhưng baseline chưa phê duyệt | `True`* | `True`* | **`False`** | **`True`** |
| **`LOCAL_HASH_VERIFIED`** | Kích thước và mã băm khớp baseline phê duyệt | `True`* | `True`* | `True`** | Không đổi |

*\* Ghi chú:* Các cờ đánh dấu `*` chỉ đạt giá trị `True` nếu **tất cả** các nguồn khác trong batch cũng thỏa mãn điều kiện tương ứng. Nếu dù chỉ một nguồn rơi vào nhóm lỗi (`SOURCE_MISSING`, `SOURCE_READ_ERROR`, `SOURCE_CHANGED_DURING_READ`), toàn bộ các cờ `all_present`, `all_sizes_match`, `all_hashes_verified` bị ép về `False`.  
*\*\* Ghi chú:* `all_hashes_verified` chỉ đạt `True` khi cờ cấu hình `compute_hash=True` và **100%** các nguồn trong batch đều là `LOCAL_HASH_VERIFIED`.

---

## 3. Cơ chế Bảo vệ Inventory Sản xuất (`enforce_production_inventory`)

Để ngăn chặn việc downstream pipeline chạy trên một tập con không đầy đủ của bộ dữ liệu lịch sử hàng không 2016–2024 (ví dụ chỉ cấu hình 1 năm thay vì trọn vẹn 9 năm), `SourceValidator` cung cấp cờ:

```python
enforce_production_inventory: bool = False
```

Khi cờ này được bật:
1. Tập năm trong `inventory.keys()` bắt buộc phải trùng khớp chính xác với tập hằng số:
   $$\text{REQUIRED\_PRODUCTION\_YEARS} = \{2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024\}$$
2. Nếu thiếu bất kỳ năm nào (ví dụ inventory chỉ có 8 năm), ném ngay ngoại lệ:
   ```python
   SourceConfigurationError: Production inventory must contain all 9 years (2016-2024). Missing years: ...
   ```
3. Nếu thừa hoặc sai lệch năm, ném ngay ngoại lệ:
   ```python
   SourceConfigurationError: Production inventory contains unexpected years: ...
   ```

---

## 4. Chứng minh Thực nghiệm qua Unit Tests

Các trường hợp kiểm thử tự động đã được lập trình và vượt qua 100% trong `tests/test_t007_source_validator.py`:

1. `test_closure_fix_a01_empty_inventory_rejected_in_init`: Khởi tạo với `{}` ném ngay `SourceConfigurationError`.
2. `test_closure_fix_a01_production_completeness_guard`: Cung cấp 8 năm thay vì 9 năm bị ném `SourceConfigurationError` chỉ rõ năm bị thiếu. Cung cấp đủ 9 năm vượt qua hợp lệ.
3. `test_closure_fix_a02_directory_source_read_error_batch_fail_closed`: Một nguồn trỏ vào thư mục sinh `SOURCE_READ_ERROR`; toàn bộ `all_present`, `all_sizes_match`, `all_hashes_verified` đều là `False`.
4. `test_closure_fix_a02_all_verification_states_fail_closed_matrix`: Chạy qua toàn bộ ma trận trạng thái để kiểm chứng mọi tổ hợp lỗi đều ép cờ batch về `False`.

Kết luận: Thiết kế ma trận trạng thái và bất biến batch bảo đảm hoàn toàn tính an toàn fail-closed cho hệ thống.
