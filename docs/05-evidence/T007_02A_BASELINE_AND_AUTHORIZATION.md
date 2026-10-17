# T007-02A Baseline & Project Lead Authorization Record

**Document ID:** `T007_02A_BASELINE_AND_AUTHORIZATION.md`  
**Date:** 2026-10-17  
**Parent Task:** `T-007` (Raw CSV Ingestion Pipeline)  
**Subtask:** `T007-02A` (Source Inventory & Local Hash Verifier Implementation)  
**Parent Gate:** `G4` (`PLANNED / NOT_COMPLETED`)  
**Status:** `OFFICIALLY_RECORDED`  
**Engineer:** Senior Python Data Engineer & Independent QA Reviewer  

---

## 1. Cơ sở Ủy quyền từ Project Lead

Nhiệm vụ `T007-02A` được khởi động theo chỉ thị ủy quyền tường minh và trực tiếp từ Project Lead con người:

> "Bạn là Senior Python Data Engineer, Data Provenance Auditor, Secure Filesystem Engineer và Independent QA Reviewer... Project Lead trực tiếp gửi prompt này để ủy quyền triển khai T007-02A, với giới hạn không đọc dữ liệu CSV thật."

### Ranh giới Ủy quyền Tuyệt đối:
1. **Phạm vi được ủy quyền:**
   - Triển khai module `src/flight_pipeline/ingestion/source_validator.py`.
   - Cập nhật exports tại `src/flight_pipeline/ingestion/__init__.py`.
   - Triển khai bộ kiểm thử tổng hợp `tests/test_t007_source_validator.py`.
   - Ban hành phụ lục đính chính `docs/05-evidence/T007_02A_HANDOFF_ERRATA.md`.
   - Lập hồ sơ bằng chứng `T007_02A_*.md` và nhật ký kiểm toán.
2. **Phạm vi nghiêm cấm (Strictly Forbidden):**
   - Không đọc, mở stream, hoặc băm 9 tệp CSV thật (15.2 GB) trong `data/raw/tabular/`.
   - Không thực hiện Subtask `T007-02B` (tạo candidate SHA-256 từ dữ liệu thật).
   - Không thực hiện các subtask tiếp theo `T007-03` đến `T007-07`.
   - Không khởi động nhiệm vụ chất lượng `T-008`.
   - Không tự ý nghiệm thu Gate `G4` (`G4` tiếp tục giữ trạng thái `PLANNED / NOT_COMPLETED`).

---

## 2. Kiểm toán Trạng thái Entry Baseline

Trước khi triển khai, trạng thái kho lưu trữ đã được kiểm chứng độc lập trên cây làm việc sạch:

| Hạng mục Kiểm toán | Trạng thái Thực tế | Ghi chú & Căn cứ Pháp lý |
|---|:---:|---|
| **Git Working Tree** | Clean (`porcelain` rỗng) | Không có tệp uncommitted hoặc untracked trước task |
| **Git Commit HEAD** | `f6da09b4d4ba880772ec3c963588ad0594f8e198` | Sau commit `T007-01-HUMAN-SIGNOFF` |
| **Branch** | `master` | Nhánh phát triển chính |
| **Gate G2** | `PASS` | Đã ký nghiệm thu con người (`G2_OFFICIAL_SIGNOFF_HUMAN_ACCEPTANCE_RECORD.md`) |
| **Gate G3** | `PASS` | Đã ký nghiệm thu con người (`G3_OFFICIAL_SIGNOFF_HUMAN_ACCEPTANCE_RECORD.md`) |
| **Task T-006** | `PASS / COMPLETED` | Hoàn tất thiết kế kiến trúc PySpark |
| **Task T-009** | `PASS / COMPLETED` *(Controlled)* | Đã ký nghiệm thu con người (`T009_HUMAN_SIGNOFF_20261017.md`) |
| **Subtask T007-01** | `PASS / COMPLETED` *(Controlled)* | Đã ký nghiệm thu con người (`T007_01_HUMAN_SIGNOFF_20261017.md`) |
| **Task T-007 Tổng thể** | `IN_PROGRESS` *(Controlled)* | Đang tiến hành theo từng checkpoint ủy quyền |
| **Subtask T007-02** | `IN_PROGRESS (Checkpoint 2A)` | Mở có kiểm soát cho Checkpoint 2A |
| **Subtask T007-03..07** | `LOCKED` | Khóa nghiêm ngặt |
| **Task T-008** | `NOT_STARTED` | Khóa nghiêm ngặt |
| **Gate G4** | `PLANNED / NOT_COMPLETED` | Không thay đổi |

---

## 3. Baseline Kiểm thử Trước Triển khai

Tại thời điểm baseline, toàn bộ các bộ kiểm toán và kiểm thử đã đạt kết quả tuyệt đối:
- Unit test suite: **59 tests PASS, 0 FAIL** (trong 26.014s).
- `verify_t006_contract_consistency.py`: **17 Invariants PASS, 16 Mutations PASS, 0 FAIL**.
- `verify_g2_repo_apply_r1_semantic_invariants.py`: **15 Invariants PASS, 14 Mutations PASS, 0 FAIL**.
- `test_working_tree_registry_regression.py`: **16 PASS, 0 FAIL, 0 SKIP**.
- `check_working_tree_consistency.py`: **843 PASS, 0 FAIL** tại $N = 366$ deliverables.
