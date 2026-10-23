# T011_FULL_BASELINE_AND_PREFLIGHT — BÁO CÁO KIỂM TOÁN MÔI TRƯỜNG, HẠ TẦNG VÀ BASELINE TRƯỚC THỰC THI T-011

- **Mã nhiệm vụ:** `T-011` (Gate G5: KPI Sample Smoke, BTS Parity, TS-008, TS-013 & Review Packaging)
- **Gate:** `G5` (IN_PROGRESS)
- **Thời điểm kiểm toán:** 2026-10-18T20:41:30+07:00
- **Tiêu chuẩn tuân thủ:** [`AGENTS.md`](../../AGENTS.md), Master Execution Prompt T-011 Mục 5.
- **Trạng thái Gate 0:** **PASS (Preflight & Baseline Verified)**

---

## 1. THÔNG SỐ MÔI TRƯỜNG VÀ HẠ TẦNG RUNTIME THỰC TẾ

| Thành phần kiểm toán | Giá trị ghi nhận thực tế | Trạng thái thẩm định |
|---|---|:---:|
| **Repository Root** | `D:\Study\Code\Apache\Flight_Analyzt\US_FLIGHT_PERFORMANCE_DOCS_V1` | HỢP LỆ |
| **Git Current Branch** | `master` | HỢP LỆ |
| **Git HEAD Hash** | `bc4f03fb8ccd6c0b2455af3fcb2b1b98fa39d632` | HỢP LỆ |
| **Working Tree Status** | 76 thay đổi đã ghi nhận từ G4/T-010 Human Signoff và hồ sơ evidence (không có file rác không xác định) | HỢP LỆ |
| **Hệ điều hành (OS)** | Windows 10 (Build 10.0.19045-SP0, 64-bit) | HỢP LỆ |
| **Python Runtime** | `Python 3.10.11 (tags/v3.10.11:7d4cc5a, Apr 5 2023, 00:38:17) [MSC v.1929 64 bit (AMD64)]` | HỢP LỆ |
| **Apache Spark / PySpark** | `PySpark 4.0.1` | HỢP LỆ |
| **Java Virtual Machine (JVM)** | `openjdk version "21.0.12.1" 2026-08-18 LTS` | HỢP LỆ |
| **Không gian đĩa cứng (Disk Space)** | Total: 300.00 GB, Used: 237.64 GB, **Free: 62.36 GB** | HỢP LỆ |
| **Dữ liệu thô Canonical (`data/raw/`)** | 9 tệp CSV (2016–2024), 54,674,003 dòng, 15,196,366,173 bytes | BẤT BIẾN / READ-ONLY |
| **Vùng xuất bản sản xuất (`data/curated/latest`)** | Không bị thay đổi, giữ nguyên con trỏ an toàn | HỢP LỆ |

---

## 2. KẾT QUẢ KIỂM CHUẨN BASELINE QA VÀ TEST SUITE

Trước khi thực hiện bất kỳ thay đổi nào vào mã nguồn sản xuất, toàn bộ bộ kiểm thử hiện có đã được chạy và xác thực:

### 2.1. Bộ Unittest Toàn diện (`tests/test_*.py`)
- **Lệnh thực thi:** `python -m unittest discover -s tests -p "test_*.py"`
- **Thời gian chạy:** 147.566 giây
- **Mã thoát (Exit Code):** `0`
- **Kết quả:** **181 tests executed, 181 PASS, 0 FAIL, 0 ERROR, 0 SKIP (100% PASS)**

### 2.2. Kiểm tra Tính Nhất quán Working Tree (`tools/check_working_tree_consistency.py`)
- **Lệnh thực thi:** `python tools/check_working_tree_consistency.py`
- **Mã thoát (Exit Code):** `0`
- **Kết quả:** **1,135 PASS assertions, 0 FAIL** trên 512 registered deliverables.

### 2.3. Kiểm chứng Bất biến Ngữ nghĩa G2 (`tools/qa/verify_g2_repo_apply_r1_semantic_invariants.py`)
- **Lệnh thực thi:** `python tools/qa/verify_g2_repo_apply_r1_semantic_invariants.py`
- **Mã thoát (Exit Code):** `0`
- **Kết quả:** **15 Semantic Invariants PASS + 15 Isolated Mutation Tests PASS (0 FAIL)**

### 2.4. Kiểm chứng Hợp đồng T-006 (`tools/qa/verify_t006_contract_consistency.py`)
- **Lệnh thực thi:** `python tools/qa/verify_t006_contract_consistency.py`
- **Mã thoát (Exit Code):** `0`
- **Kết quả:** **17 Invariants PASS + 16 Isolated Mutation Tests PASS (0 FAIL)**

### 2.5. Xác thực Schema Parquet T-010 (`tools/qa/verify_t010_parquet_schema_attestation.py`)
- **Lệnh thực thi:** `python tools/qa/verify_t010_parquet_schema_attestation.py`
- **Mã thoát (Exit Code):** `0`
- **Kết quả:** **50/50 tệp Parquet staging thực tế đạt 100% khớp schema 34 cột (10 String, 19 Double, 5 Long), mã băm `b5805fcae8db44e9a53c0eb1dfa1c1f3d9ec2983b3922bfbe5c6454f1654b09a`**.

---

## 3. KIỂM TOÁN TƯƠNG THÍCH MÃ NGUỒN HIỆN HÀNH (IMPLEMENTATION COMPATIBILITY AUDIT)

Kiểm toán đã rà soát trực tiếp các API sản xuất đã được nghiệm thu để tái sử dụng trong T-011:
1. **Module Ingestion (`src/flight_pipeline/ingestion/`):**
   - `reader.py`: `RawCsvReader` cung cấp cơ chế đọc CSV an toàn với kiểu chuỗi nguyên bản và streaming hash.
   - `schema.py`: `CANONICAL_SOURCE_COLUMNS` và `CANONICAL_SOURCE_SCHEMA` (34 cột).
   - `source_validator.py`: Kiểm toán cấu trúc tệp nguồn không can thiệp nội dung.
2. **Module Quality (`src/flight_pipeline/quality/`):**
   - `predicates.py`: Cung cấp các hàm kiểm tra hợp lệ số `is_finite_numeric()`, `is_valid_delay()`, `is_valid_elapsed()`, `is_valid_taxi()` an toàn trong Spark ANSI mode.
   - `accounting.py`: Triển khai hạch toán 3 trạng thái rời nhau `DC-11` (`accepted`, `quarantined`, `rejected`).
   - `policy.py`: `ProductionQualityPolicyGuard` duy trì các chốt chặn an toàn: `allow_weather_nulls=True`, `quarantine_non_positive_flight_num=False`.
3. **Module Storage (`src/flight_pipeline/storage/`):**
   - `locking.py`: `SingleWriterLock` trên Windows NTFS.
   - `publication.py`: `SafePublisher` quy trình 7 bước xuất bản hai pha.
4. **Hiện trạng Module KPI (`src/flight_pipeline/kpi/`):**
   - Chưa tồn tại mã nguồn nào trong thư mục này. Sẽ được thiết kế và xây dựng mới hoàn toàn trong Phase 1 của T-011 theo đúng hợp đồng `KPI_SPEC.md`.

---

## 4. KẾT LUẬN GATE 0

- Hạ tầng runtime, phiên bản phần mềm, không gian đĩa và bộ nhớ hoàn toàn đáp ứng yêu cầu thực thi T-011.
- Toàn bộ 181 baseline unittests và 1,135 working-tree checks đạt 100% PASS, tạo nền tảng vững chắc không có sai lệch hồi quy.
- Phạm vi thay đổi tệp được giới hạn nghiêm ngặt theo đúng chỉ thị ủy quyền.
- **GATE 0 CHÍNH THỨC ĐẠT (PASS) — Cho phép chuyển sang Phase 1 (Implement CORE KPI Engine).**
