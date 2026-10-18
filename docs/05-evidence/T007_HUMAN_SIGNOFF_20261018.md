# T-007 — HUMAN SIGNOFF & CONTROLLED ACCEPTANCE RECORD

**Project:** US Flight Performance Analysis 2016–2024  
**Task ID:** `T-007` — Raw CSV Ingestion Pipeline  
**Parent Gate:** `G4` (`PLANNED / NOT_COMPLETED`)  
**Record ID:** `T007-HUMAN-SIGNOFF-20261018`  
**Date:** 2026-10-18  
**Human Approval Authority:** Project Lead (`APPROVED_BY_PROJECT_LEAD_EXPLICIT_INSTRUCTION`)  
**Recording Agent:** AI Pair Programming Agent (Senior Data Engineer & Provenance Auditor)  
**Formal Authentication Status:** `HUMAN_APPROVAL_RECEIVED — FORMAL_AUTHENTICATION_PENDING`  
**Overall Status:** **`PASS / COMPLETED (CONTROLLED)`**

---

## 1. Tuyên bố Thẩm quyền & Quyết định Nghiệm thu

Project Lead đã trực tiếp ban hành quyết định phê duyệt có kiểm soát đối với Nhiệm vụ `T-007` (Raw CSV Ingestion Pipeline):

> **"T-007 — Raw CSV Ingestion Pipeline = PASS / COMPLETED (CONTROLLED)"**

Biên bản này được lập bởi AI Agent nhằm ghi nhận chính thức quyết định của con người vào hệ thống quản trị dự án, tuân thủ các quy tắc bất biến tại `AGENTS.md` và `PROJECT_STATE.md`. Quyết định này là sự phê duyệt của Project Lead đối với các bằng chứng kỹ thuật đã được kiểm chứng độc lập trong gói kiểm toán `MASTER-T007-SIGNOFF-EXIT`.

### Phạm vi Được Phê duyệt
- **Mã nguồn sản xuất:** Toàn bộ tầng nạp dữ liệu PySpark, bao gồm Canonical Schema (`T007-01`), Source Inventory & Local Streaming SHA-256 Verifier (`T007-02A/02B`), Header/Delimiter/Record Scanner & Lineage Attachment (`T007-03`), Single Writer Concurrency Lock (`T007-04`), Quản lý vòng đời Ingestion Coordinator, cơ chế ghi Parquet 2 pha và phục hồi hậu-pointer (`T007-05..07`).
- **Phạm vi kiểm thử:** Kiểm chứng tự động toàn diện trên dữ liệu synthetic, bao gồm 135 unit/integration/fault-injection tests đạt `PASS` tuyệt đối, cùng 6 bộ kiểm toán QA bảo vệ cấu trúc repository.

---

## 2. Baseline Kỹ thuật & Mã băm Kiểm toán

- **Approved Git Commit Baseline:** `499921e0b06b165fd741b5486441cb27e13f3eff`
- **Active Git Branch:** `master`
- **Working Tree State:** Clean (`0` modified / `0` untracked files tại thời điểm nghiệm thu)
- **Môi trường Thực thi:** Windows 11 / Python 3.10 / Apache Spark 4.0.1 / PySpark Local Mode

### 2.1. Mã băm Mô-đun Mã nguồn Sản xuất T-007

| Đường dẫn Mô-đun Sản xuất | Kích thước (Bytes) | SHA-256 Checksum | Trạng thái Nghiệm thu |
| :--- | ---: | :--- | :---: |
| `src/flight_pipeline/ingestion/schema.py` | `14,686` | `56f09f848da2f501f98a6f75101500c1e7fd952524c28f7ebfb0bf35c0495395` | `PASS` (T007-01) |
| `src/flight_pipeline/ingestion/source_validator.py` | `20,762` | `d1e2b8f64be8e943e9ccdd1a6c27ba469092dd99c4d199b0382463d5195e75be` | `PASS` (T007-02A) |
| `src/flight_pipeline/storage/locking.py` | `10,601` | `c1cb562291167c5c94fd10dc141f277c5aaad6d9006b34866a7852db47d64607` | `PASS` (T007-04) |
| `src/flight_pipeline/ingestion/reader.py` | `44,077` | `2f3df94170d954d9fde299590cc1b7d4928cf24737b794f159c5fbf101a88067` | `PASS` (T007-03) |
| `src/flight_pipeline/ingestion/coordinator.py` | `71,897` | `2577275651b8f60e23af38725c8d8f01792e969a42ad471e238e320257652d06` | `PASS` (T007-05..07) |
| `src/flight_pipeline/ingestion/__init__.py` | `4,470` | `19f5d466a5e3fec2c46cedfc4adf0358d7f825aa3bd100b950975b6d0bc50b52` | `PASS` (Export) |

### 2.2. Mã băm Bộ Kiểm thử Tích hợp và Đơn vị

| Đường dẫn Bộ Kiểm thử | Kích thước (Bytes) | SHA-256 Checksum | Số lượng Tests |
| :--- | ---: | :--- | :---: |
| `tests/test_t007_schema.py` | `14,642` | `463b7e7a57a552bfef3234d6ca32cbcae0ef6b7be30058e1467ea55b9eb64ff1` | 22 PASS |
| `tests/test_t007_source_validator.py` | `27,247` | `ba363f82e5ee81c9ba257bc5ea9a650d885fe8ba8043690d5bc0c5717ef9a584` | 38 PASS |
| `tests/test_t007_reader.py` | `38,395` | `98335e73c8cdda709634c970100615e0defd85edd25bfdd352965d212bfb0403` | 17 PASS |
| `tests/test_t007_locking.py` | `11,732` | `374bc7b9937fc1c0a00632a6136d85eb56e897e937d530263f25ee22467b7381` | 8 PASS |
| `tests/test_t007_pipeline_integration.py` | `50,178` | `ec1b6293ffc01dd7fef9bba3707e613a95bf88ad9ec7608761063fd61c30ac10` | 13 PASS |
| *Cụm kiểm thử T-009 đã nghiệm thu* | -- | *(5 tệp kiểm thử T-009 được bảo tồn nguyên vẹn)* | 37 PASS |
| **Tổng số bài kiểm thử tự động** | -- | **T007_SIGNOFF_EXIT_LOG_UNITTEST_SUITE.txt** | **`135 PASS`** |

---

## 3. Bằng chứng Thực thi Kiểm chứng Độc lập

Toàn bộ các bằng chứng thực thi đã được xác nhận khớp với các tệp nhật ký thô được lưu trữ trong `docs/05-evidence/`:

1. **Bộ kiểm thử toàn diện `tests/`:** Đạt **`135/135 PASS (0 FAIL, 0 SKIP)`** trong `96.670s` ([`T007_SIGNOFF_EXIT_LOG_UNITTEST_SUITE.txt`](T007_SIGNOFF_EXIT_LOG_UNITTEST_SUITE.txt)).
2. **Kiểm tra Hợp đồng T-006:** `tools/qa/verify_t006_contract_consistency.py` đạt **`17/17 Invariants PASS`** và **`16/16 Mutations PASS`** ([`T007_SIGNOFF_EXIT_LOG_QA_VERIFIERS.txt`](T007_SIGNOFF_EXIT_LOG_QA_VERIFIERS.txt)).
3. **Kiểm tra Bất biến Ngữ nghĩa Gate G2:** `tools/qa/verify_g2_repo_apply_r1_semantic_invariants.py` đạt **`15/15 Invariants PASS`** và **`14/14 Mutations PASS`**.
4. **Kiểm tra Mở rộng Validator T-009:** `tools/qa/test_t009_r1_validator_extension.py` đạt **`8/8 PASS`**.
5. **Kiểm tra Loại trừ Git T-009:** `tools/qa/test_t009_unblock_r2_git_exclusion.py` đạt **`7/7 PASS`**.
6. **Kiểm tra Hồi quy Registry:** `tools/qa/test_working_tree_registry_regression.py` đạt **`16/16 PASS`**.
7. **Kiểm tra Tính nhất quán Working Tree:** `tools/check_working_tree_consistency.py` đạt **`989/989 PASS`**.

---

## 4. Các Giới hạn Được Chấp nhận & Ràng buộc Bảo lưu (Non-blocking Limitations)

Project Lead phê duyệt nghiệm thu có kiểm soát `T-007` đi kèm với việc bảo lưu nghiêm ngặt các giới hạn kỹ thuật và pháp lý sau:

1. **`L-T007-01` — Synthetic Execution Only / Chưa chạy Spark trên 54.7M Dòng Thật:**
   - Trong khuôn khổ Gate G4, Spark chỉ được thực thi trên các bộ dữ liệu synthetic (bao gồm các ca kiểm thử multi-line, 34 cột, lỗi footer Parquet, v.v.).
   - 9 tệp CSV thô thật sự chỉ được đọc dạng streaming byte-level tuần tự để tính mã băm SHA-256 ứng viên (`T007-02B`), hoàn toàn chưa được nạp hoặc biến đổi bởi Spark DataFrame API.
   - Nghiêm cấm tuyên bố rằng T-007 đã xử lý thành công 54.7 triệu dòng dữ liệu thực tế của Mỹ.
2. **`L-T007-02` — Candidate SHA-256 Baseline Remains Pending Acceptance:**
   - Tập mã băm sinh ra tại [`docs/05-evidence/T007_LOCAL_RAW_SHA256_CANDIDATE.json`](T007_LOCAL_RAW_SHA256_CANDIDATE.json) tiếp tục giữ trạng thái **`CANDIDATE_PENDING_HUMAN_ACCEPTANCE`**.
   - Trạng thái định danh thượng nguồn của dữ liệu BTS tiếp tục giữ nguyên **`IDENTITY_UNVERIFIED`** (`OR-08` / `TS-019`).
   - Tệp gốc `SOURCE_MANIFEST.json` và 9 tệp CSV thô được bảo toàn nguyên vẹn, không bị sửa đổi.
3. **`L-T007-03` — Lineage Identifier Semantics:**
   - Cột kỹ thuật `_record_lineage_id` là mã băm xác định nội dung kèm thứ tự xuất hiện nội bộ phân vùng, không đại diện cho chỉ số dòng vật lý trong tệp CSV nguồn (xem [`T007_FINAL_SIGNOFF_DOCUMENTATION_ERRATA.md`](T007_FINAL_SIGNOFF_DOCUMENTATION_ERRATA.md)).
4. **`L-T007-04` — Provisional Quarantine Rules Awaiting T-008 (`G3-COND-A`):**
   - Tiêu chí cách ly bản ghi `OP_CARRIER_FL_NUM <= 0` tiếp tục giữ trạng thái tạm thời, bắt buộc phải qua thẩm tra phân bố tại `T-008` trước khi chạy smoke Gate G5.
5. **Bảo lưu Toàn vẹn các Ràng buộc Quản trị Cốt lõi:**
   - **`G2-EXC-001 / TS-018`:** 7 trường số đo liên tục CORE (`ARR_DELAY`, `DEP_DELAY`, `TAXI_OUT`, `TAXI_IN`, `AIR_TIME`, `ACTUAL_ELAPSED_TIME`, `CRS_ELAPSED_TIME`) tiếp tục giữ nhãn `PROVISIONAL`. Bắt buộc thực hiện `TS-018` đối chiếu bản ghi BTS có thẩm quyền tại Gate G5; nếu FAIL thì CHẶN hoàn toàn Gate G6.
   - **`OR-05`:** Khuyết tật chất lượng mở năm 2024 chỉ có `335/366` ngày (thiếu toàn bộ Tháng 3/2024) tiếp tục được theo dõi, cấm tạo dữ liệu giả hoặc nội suy.
   - **`FP-DEC-017`:** Trạng thái `CONDITIONAL_NO_GO` của thời tiết được duy trì nghiêm ngặt. 6 cột thời tiết có mặt trong schema nhưng không được sử dụng để loại bỏ dòng CORE hợp lệ.
   - **`G3-COND-B` & `G3-COND-C`:** Kiểm thử vị từ số học tại runtime và xuất bản an toàn Windows NTFS tiếp tục là nghĩa vụ kiểm chứng tại G5.

---

## 5. Nghĩa vụ Chuyển giao Bắt buộc Sang T-008, G5 và G6

| Nhiệm vụ / Gate Đích | Nghĩa vụ Chuyển giao Cụ thể | Điều kiện Nghiệm thu |
| :--- | :--- | :--- |
| **`G4 / T-008`** | Triển khai Quality Engine, phân loại 3 trạng thái độc lập (`DC-11`), tính toán mẫu số hợp đồng (`DC-12`), kiểm tra sớm độ phủ lịch 2024 (`OR-05`), thẩm tra chính sách cách ly `OP_CARRIER_FL_NUM <= 0`. | Synthetic Quality Tests PASS; không đụng đến mã nguồn T-007 hay dữ liệu thật. |
| **`G5 / T-010`** | Chạy smoke thực tế PySpark trên duy nhất 1 năm (2016) vào staging Parquet; đo lường benchmark tài nguyên CPU/RAM/thời gian (`TS-014`). | RunManifest 2016 hợp lệ; raw CSV bất biến; benchmark trong ngân sách. |
| **`G5 / T-011`** | Triển khai tính toán KPI mẫu trên năm 2016; kiểm thử tiêm lỗi rollback (`TS-013`); **bắt buộc chạy `TS-018` đối chiếu 7 trường số CORE với BTS**. | **`TS-018` PASS (Hard Stop trước G6)**; KPI mẫu khớp với oracle. |
| **`G6 / T-012..015`** | Chạy toàn diện 9 năm dữ liệu (2016–2024) sau khi `TS-018` đạt PASS; xác thực độ phủ khuyết Tháng 3/2024 (`TS-004`); tính toán 8 CORE KPIs (`T-013`, `T-014`). | 9 RunManifests; xuất bản Parquet hoàn tất; tuân thủ `FP-DEC-017` (`T-015 = CONDITIONAL_NO_GO`). |

---

## 6. Kết luận & Trạng thái Quản trị Repository

Căn cứ vào quyết định phê duyệt của Project Lead và kết quả kiểm chứng tự động:
- **`T-007 — Raw CSV Ingestion Pipeline`** chính thức ghi nhận trạng thái: **`PASS / COMPLETED (CONTROLLED)`**.
- Các hạng mục con `T007-01` đến `T007-07` được ghi nhận hoàn thành đồng bộ.
- Nhiệm vụ **`T-008`** tiếp tục giữ nghiêm ngặt trạng thái: **`NOT_STARTED`**.
- Gate **`G4`** tiếp tục giữ trạng thái: **`PLANNED / NOT_COMPLETED`** (chờ hoàn thành và nghiệm thu `T-008`).

Tài liệu này được công bố chính thức và lưu trữ bất biến tại [`docs/05-evidence/T007_HUMAN_SIGNOFF_20261018.md`](T007_HUMAN_SIGNOFF_20261018.md).
