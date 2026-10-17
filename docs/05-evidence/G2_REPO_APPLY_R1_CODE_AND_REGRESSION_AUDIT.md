# G2_REPO_APPLY_R1_CODE_AND_REGRESSION_AUDIT — Báo cáo Kiểm toán Mã nguồn Công cụ & Kiểm thử Hồi quy Độc lập

**Mã tài liệu:** `G2_REPO_APPLY_R1_CODE_AND_REGRESSION_AUDIT`  
**Nhiệm vụ:** `G2-REPO-APPLY-R1` (Targeted Semantic Regression Repair & Independent Code Verification)  
**Ngày thực hiện:** 2026-10-16  
**Vai trò:** Kỹ sư Dữ liệu Lớn Độc lập, Kiểm toán viên Quản trị Kho mã & Chuyên viên Tự động hóa Kiểm thử  
**Trạng thái nghiệm thu kỹ thuật:** **HOÀN TOÀN ĐẠT CHUẨN (`PASS`)** trên tất cả các bộ kiểm thử mã nguồn và bất biến ngữ nghĩa.  
**Trạng thái Gate G2 chính thức:** **`IN_PROGRESS / NOT_PASSED`** (`AWAITING_FINAL_HUMAN_GATE_SIGNOFF`).

---

## 1. Mục tiêu và Phương pháp Kiểm toán Mã nguồn

Kiểm toán viên độc lập đã tiến hành thẩm tra trực tiếp mã nguồn thực thi, cấu trúc dữ liệu sổ đăng ký, các cơ chế kiểm tra phòng vệ và bộ kiểm thử tự động, thay vì chỉ đọc báo cáo Markdown.

Phạm vi thẩm tra mã nguồn bao gồm:
1. Công cụ kiểm tra toàn vẹn cây làm việc: [`tools/check_working_tree_consistency.py`](../../tools/check_working_tree_consistency.py).
2. Sổ đăng ký kiểm soát phân phối và tài liệu sống: [`docs/05-evidence/EVIDENCE_DELIVERABLE_REGISTER.json`](EVIDENCE_DELIVERABLE_REGISTER.json).
3. Bộ kiểm thử hồi quy đăng ký: [`tools/qa/test_working_tree_registry_regression.py`](../../tools/qa/test_working_tree_registry_regression.py).
4. Bộ kiểm thử bất biến ngữ nghĩa và đột biến có kiểm soát mới tạo: [`tools/qa/verify_g2_repo_apply_r1_semantic_invariants.py`](../../tools/qa/verify_g2_repo_apply_r1_semantic_invariants.py).

---

## 2. Kết quả Rà soát Ranh giới Tin cậy và Các Điểm Tăng cường Bảo vệ (Phase C Findings)

### 2.1. Đánh giá 9 Tiêu chí Ranh giới Tin cậy của Sổ Đăng ký
1. **Ranh giới tin cậy rõ ràng (`Explicit Trust Boundary`):** Sổ đăng ký phân định tuyệt đối giữa:
   - Các tệp kiểm toán lịch sử bất biến (`docs/05-evidence/inputs/`, 13 tệp trong `SOURCE_MANIFEST.json`).
   - Các tệp phát hành gói chuẩn `docs-v1.1` (47 tệp trong `PACKAGE_MANIFEST.json`).
   - Danh sách 7 tài liệu sống được ủy quyền chỉnh sửa (`ALLOWED_GOVERNED_LIVING_DOCS`).
   - Các tệp bằng chứng và công cụ kiểm tra được cấp phép (`registered_deliverables`).
2. **Phân biệt tệp bất biến vs. tài liệu sống được phép sửa:** Mọi sửa đổi trên tài liệu sống đều bắt buộc phải có bản sao lưu trước khi sửa (`.pre_g2_repo_apply.bak`) đối khớp chính xác byte và SHA-256 với v1.1 ban đầu trong `PACKAGE_MANIFEST.json`.
3. **Từ chối tệp không đăng ký (`Rejection of Unregistered Files`):** Bất kỳ tệp mới nào xuất hiện trong kho mà không nằm trong manifest gốc, không phải 9 CSV thô, không phải sổ đăng ký và không được đăng ký trong `registered_deliverables` đều bị chặn hoàn toàn với lỗi `No unrecognized stray files in working-tree`.
4. **Từ chối nội dung đăng ký bị sửa đổi:** Bất kỳ sự thay đổi dù chỉ 1 byte hoặc thay đổi SHA-256 đều làm thất bại kiểm tra `Registered deliverable physical size/SHA-256 verified`.
5. **Từ chối liên kết mềm (`Symlink`) và duyệt đường dẫn (`Path Traversal`):**
   - Đã tăng cường `_is_safe_rel_path`: Từ chối tuyệt đối bất kỳ thành phần đường dẫn nào là symbolic link (`cur.is_symlink() -> False`).
   - Đã bổ sung kiểm tra quét toàn diện cây làm việc ở Mục 14: Phát hiện và chặn đứng bất kỳ symbolic link nào tồn tại trong repository.
6. **Từ chối bản ghi thiếu, trùng lặp hoặc sai định dạng:** Xác thực cấu trúc JSON nghiêm ngặt, từ chối bản ghi trùng lặp (`seen_living`, `seen_deliv`), kiểm tra regex mã băm 64 ký tự hex (`HEX64_RE`), kiểm tra kích thước dương (> 0).
7. **Không thể bỏ qua manifest lịch sử:** Đã tăng cường ghim cứng mã băm và kích thước byte của chính hai tệp manifest nền tảng:
   - `PACKAGE_MANIFEST.json`: Pinned Bytes = `8,354`, Pinned SHA-256 = `7c457207a6fefd2a45ad56a4c8ee8e3fb6194b8462f6ee24985f4e9534d61df1`.
   - `docs/05-evidence/inputs/SOURCE_MANIFEST.json`: Pinned Bytes = `2,479`, Pinned SHA-256 = `5e11e619790e475260b19c70630d8faef9a902c9d55d2ca641320163c87447fc`.
   Mọi hành vi sửa đổi trực tiếp vào hai tệp manifest này đều bị phát hiện ngay lập tức.
8. **Xử lý toàn vẹn tự thân không phụ thuộc băm vòng tròn (`No Circular Hashing`):** Sổ đăng ký `EVIDENCE_DELIVERABLE_REGISTER.json` tự loại trừ chính đường dẫn của nó khỏi danh sách băm nội dung (`dp != reg_rel`), tránh lỗi băm vòng tròn.
9. **Ghi nhận trung thực giới hạn tính xác thực mật mã học:**
   > [!IMPORTANT]
   > **Tuyên bố Giới hạn Tin cậy Trung thực:** Sổ đăng ký kiểm soát toàn vẹn nội bộ repository thông qua mã băm SHA-256 cục bộ. Nó **không** tương đương với một mỏ neo tin cậy chữ ký số công cộng PKI bên ngoài độc lập (external cryptographic PKI anchor). Bằng chứng kiểm toán cho thấy kho dữ liệu CSV thô vẫn giữ trạng thái danh tính `IDENTITY_UNVERIFIED` (`OR-08`) đối với nguồn BTS TranStats gốc bên ngoài cho đến khi có mã băm đối chiếu chính thức từ phía cơ quan xuất bản.

---

## 3. Danh mục Ca Kiểm thử Hồi quy Sổ Đăng ký (`POS-01..02`, `NEG-01..10`)

Bộ kiểm thử [`tools/qa/test_working_tree_registry_regression.py`](../../tools/qa/test_working_tree_registry_regression.py) được thực thi trong môi trường cô lập tạm thời (`isolated fixture`), không chạm vào `data/raw/`:

| Mã Test | Loại | Mục tiêu kiểm thử | Kết quả Thực tế | Exit Code | Ghi chú Chi tiết |
|:---:|:---:|---|:---:|:---:|---|
| **POS-01** | Dương tính | Tệp bằng chứng mới được đăng ký hợp lệ, đúng kích thước và SHA-256 được chấp thuận | **PASS** | `0` | Thử nghiệm tạo artifact hợp lệ, kiểm tra vượt qua toàn bộ assertions |
| **POS-02** | Dương tính | Toàn bộ chứng tích lịch sử bất biến và baseline hiện hành được chấp thuận 0 lỗi | **PASS** | `0` | Kiểm tra toàn bộ 26 tài liệu cốt lõi, 13 tệp `SOURCE_MANIFEST.json` và 47 tệp package |
| **NEG-01** | Âm tính | Tệp Markdown bất kỳ không đăng ký xuất hiện trong kho bị từ chối | **PASS** | `0` | Phát hiện lỗi stray file không được phép |
| **NEG-02** | Âm tính | Tệp có tiền tố hợp lệ (`T005_...`, `G2_...`) nhưng không đăng ký bị từ chối | **PASS** | `0` | Ngăn chặn hành vi giả mạo tiền tố nhiệm vụ |
| **NEG-03** | Âm tính | Tệp đã đăng ký nhưng nội dung bị sửa đổi hoặc SHA-256 sai bị từ chối | **PASS** | `0` | Phát hiện sai khác mã băm mật mã học |
| **NEG-04** | Âm tính | Tệp đã đăng ký nhưng bị xóa hoặc sai lệch kích thước byte bị từ chối | **PASS** | `0` | Phát hiện thiếu tệp vật lý hoặc sai kích thước |
| **NEG-05** | Âm tính | Tệp đăng ký JSON bị hỏng cú pháp hoặc chứa bản ghi trùng lặp bị từ chối | **PASS** | `0` | Bảo vệ cấu trúc và tính duy nhất của registry |
| **NEG-06** | Âm tính | Đường dẫn vượt ranh giới (`../`) hoặc đường dẫn nguy hiểm bị từ chối | **PASS** | `0` | Ngăn chặn path traversal |
| **NEG-07** | Âm tính | Phần mở rộng nguy hiểm (`.pt`, `.exe`, `.py` dưới evidence) hoặc Task ID giả (`T-999`) bị từ chối | **PASS** | `0` | Ngăn chặn nạp mã thực thi hoặc mô hình ML ngoài luồng |
| **NEG-08** | Âm tính | Không thể dùng sổ đăng ký mới để vượt mặt `SOURCE_MANIFEST.json` hoặc sửa `PACKAGE_MANIFEST.json` không phép | **PASS** | `0` | Chặn đứng hành vi ghi đè file đầu vào kiểm toán |
| **NEG-09** | Âm tính | Sửa đổi trực tiếp `PACKAGE_MANIFEST.json` / `SOURCE_MANIFEST.json` hoặc đăng ký doc sống ngoài danh sách bị từ chối | **PASS** | `0` | Xác nhận cơ chế ghim cứng mã băm manifest và `ALLOWED_GOVERNED_LIVING_DOCS` |
| **NEG-10** | Âm tính | Đăng ký `artifact_type` không trong danh mục cho phép hoặc chèn symlink bị từ chối | **PASS** | `0` | Xác nhận `ALLOWED_ARTIFACT_TYPES` và chính sách cấm symlink |

---

## 4. Danh mục Ca Kiểm thử Đột biến Bất biến Ngữ nghĩa (`MUT-01..MUT-08`)

Bộ kiểm thử [`tools/qa/verify_g2_repo_apply_r1_semantic_invariants.py`](../../tools/qa/verify_g2_repo_apply_r1_semantic_invariants.py) kiểm chứng 14 bất biến ngữ nghĩa trên cây tài liệu sống và thực thi 8 ca kiểm thử đột biến cô lập:

| Mã Test | Đột biến Được Tiêm vào Fixture Cô lập | Kết quả Kỳ vọng | Kết quả Thực tế | Bắt lỗi Thành công |
|:---:|---|---|:---:|:---:|
| **MUT-01** | Tiêm tái định nghĩa `FP-DEC-002` thành *"Ưu tiên lộ trình 8 CORE KPIs"* vào `DECISIONS.md` | Bị bắt lỗi và chặn ngay | **PASS** | `Caught FP-DEC-002 corruption` |
| **MUT-02** | Tiêm cột thời tiết tự chế `weather_code` vào `DATA_DICTIONARY.md` | Bị bắt lỗi và chặn ngay | **PASS** | `Caught weather_code fabrication` |
| **MUT-03** | Tiêm ánh xạ xáo trộn `OR-01 -> R-02` vào `RISK_REGISTER.md` | Bị bắt lỗi và chặn ngay | **PASS** | `Caught OR-01 scrambled mapping` |
| **MUT-04** | Tiêm định nghĩa sai lệch `TS-003` thành *"Kiểm thử overnight temporal"* vào `TEST_PLAN.md` | Bị bắt lỗi và chặn ngay | **PASS** | `Caught TS-003 definition corruption` |
| **MUT-05** | Tiêm khẳng định trái phép `Gate G2 = PASS` vào `PROJECT_STATE.md` | Bị bắt lỗi và chặn ngay | **PASS** | `Caught unauthorized G2 PASS` |
| **MUT-06** | Tiêm kích hoạt trái phép `T-006 = IN_PROGRESS` vào `PROJECT_STATE.md` | Bị bắt lỗi và chặn ngay | **PASS** | `Caught unauthorized T-006 start` |
| **MUT-07** | Tiêm sửa ngưỡng `min-N` từ `1000` thành `500` vào `DECISIONS.md` | Bị bắt lỗi và chặn ngay | **PASS** | `Caught min-N threshold corruption` |
| **MUT-08** | Tiêm khẳng định đơn vị đo 7 trường CORE đã `VERIFIED` (bỏ `PROVISIONAL`) vào `DECISIONS.md` | Bị bắt lỗi và chặn ngay | **PASS** | `Caught premature VERIFIED units claim` |

---

## 5. Tổng hợp Bằng chứng Thực thi Toàn diện

```
================================================================================
BẢNG TỔNG HỢP KIỂM CHỨNG TỰ ĐỘNG G2-REPO-APPLY-R1
================================================================================
1. verify_t003_contract_consistency.py      : PASS (96 checks, 0 fail, Exit 0)
2. verify_t004_time_representation.py        : PASS (90 checks, 0 fail, Exit 0)
3. verify_g2_repo_apply_r1_semantic_invariants: PASS (14 invariants, 8 mutation tests PASS, Exit 0)
4. check_working_tree_consistency.py        : PASS (0 fail, Exit 0)
5. test_working_tree_registry_regression.py : PASS (12 regression tests: POS-01..02, NEG-01..10, Exit 0)
================================================================================
TẤT CẢ CÁC BỘ KIỂM THỬ ĐẠT CHUẨN PASS TUYỆT ĐỐI.
```
