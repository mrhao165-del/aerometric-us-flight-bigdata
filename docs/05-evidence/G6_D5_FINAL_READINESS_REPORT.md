# Báo cáo Đối chiếu Hậu Nghiệm thu Gate G5 & Thẩm định Sẵn sàng Kích hoạt D5 (G6 D5 Final Readiness Report)

**Mã tài liệu:** `G6_D5_FINAL_READINESS_REPORT`  
**Ngày thực hiện:** 2026-10-21  
**Dự án:** US Flight Performance Analysis 2016–2024  
**Nhiệm vụ:** `G5-POST-SIGNOFF-RECONCILIATION-AND-D5-READINESS`  
**Vai trò:** Senior Big Data Engineer & Project Governance Reviewer  
**Thẩm quyền phê duyệt:** Project Lead  
**Phán quyết Kỹ thuật Chung cuộc:** **`READY_FOR_D5_HUMAN_AUTHORIZATION`**

---

## 1. Kết quả Đối chiếu Lịch sử CHANGELOG (Task A)

### 1.1 Hiện tượng Bất đồng
Kiểm toán độc lập phát hiện tệp `docs/03-quality/CHANGELOG.md` trong gói nghiệm thu G5 gần nhất chỉ có kích thước 10.843 bytes, thiếu 12 đề mục lịch sử quan trọng bao gồm Gate G4, Task T-010 và Task T-011 so với bản chụp kho lưu trữ G6 trước đó (37.480 bytes, SHA-256 `323e613c1fd812b7c926476e1f2fa6fc630006d3e1b21886520f5f7c9e010483`).

### 1.2 Nguyên nhân Kỹ thuật
Tệp `CHANGELOG.md` trong working-tree trước đó xuất phát từ baseline cũ chỉ ghi nhận đến Gate G3 (10.843 bytes). Trong khi đó, toàn bộ 12 đề mục kiểm toán lịch sử của G4, T-010 và T-011 đã được kiểm chứng đầy đủ và lưu trữ trong các gói lưu trữ độc lập đã được thẩm tra (điển hình là `G6_RELEASE_VALIDATOR_STRICT_FINAL_REVIEW.zip` và `G5_SIGNOFF_G6_EXECUTION_CONTRACT_FINAL_REVIEW.zip`).

### 1.3 Phương án Xử lý Thực hiện
1. Trích xuất nguyên vẹn 100% nội dung 37.480 bytes chuẩn tắc từ `G6_RELEASE_VALIDATOR_STRICT_FINAL_REVIEW.zip`.
2. Khôi phục đầy đủ 12 đề mục lịch sử đã được kiểm chứng:
   - `docs-v1.1-g5-t011-official-controlled-signoff — 2026-10-19`
   - `docs-v1.1-g5-t011-r6-remediation — 2026-10-19`
   - `docs-v1.1-g5-t011-r5-remediation — 2026-10-19`
   - `docs-v1.1-g5-t011-r4-remediation — 2026-10-19`
   - `docs-v1.1-g5-t011-r3-remediation — 2026-10-19`
   - `docs-v1.1-g5-t011-r2-remediation — 2026-10-19`
   - `docs-v1.1-g5-t011-r1-remediation — 2026-10-19`
   - `docs-v1.1-g5-t011-kpi-implementation-and-parity-harness — 2026-10-18`
   - `docs-v1.1-g5-t010-official-signoff — 2026-10-18`
   - `docs-v1.1-g5-t010-closure — 2026-10-18`
   - `docs-v1.1-g5-t010-smoke — 2026-10-18`
   - `docs-v1.1-g4-official-signoff — 2026-10-18`
3. Bảo tồn chính xác đề mục nghiệm thu chính thức Gate G5 của Project Lead ở đầu tệp:
   - `docs-v1.1-g5-official-human-signoff — 2026-10-21`
4. Kích thước tệp `CHANGELOG.md` sau hòa giải: **39.170 bytes**, tổng cộng **21 đề mục chuẩn tắc**, không tự chế bất kỳ bản ghi nào và sử dụng bản vá diff tối thiểu.

---

## 2. Hiệu chỉnh Làm rõ Trạng thái Lịch sử G2 trong DECISIONS.md (Task B)

### 2.1 Hiện tượng Cần Làm rõ
Tại Mục 2 của `docs/02-design/DECISIONS.md`, phần mô tả ngoại lệ `G2-EXC-001` (dòng 47) vẫn chứa câu chữ dễ gây hiểu nhầm:
> *"Trạng thái chính thức của Gate G2 vẫn là `IN_PROGRESS / NOT_PASSED` (`AWAITING_FINAL_HUMAN_GATE_SIGNOFF`)."*

### 2.2 Nội dung Hiệu chỉnh
Câu chữ trên đã được hiệu chỉnh chính xác để phân định rõ ràng giữa **ngữ cảnh lịch sử thời điểm ban hành ngoại lệ** và **trạng thái chính thức hiện hành**:

- **Ngữ cảnh lịch sử (2026-10-16):** Khi phê duyệt ngoại lệ `G2-EXC-001` tại bước `G2-REPO-APPLY`, quyết định đó chỉ giải tỏa điều kiện chặn thiết kế đối với `FP-DEC-012`, không tự động cho phép đóng Gate G2 mà giữ Gate G2 ở trạng thái chờ duyệt `IN_PROGRESS / NOT_PASSED`.
- **Trạng thái chính thức hiện hành:**
  - **Gate G2:** Đã được Project Lead chính thức phê duyệt nghiệm thu đạt **`PASS`** ngày 2026-10-16 (`G2_OFFICIAL_SIGNOFF_HUMAN_ACCEPTANCE_RECORD.md`).
  - **TS-018:** Đã đạt **`PASS (CONTROLLED)`** ngày 2026-10-21 theo `FP-DEC-019 Option B`.
  - **Ngoại lệ G2-EXC-001:** Đã chính thức được giải quyết thành **`RESOLVED_BY_TS018_APPROVED_OPTION_B`**.

Toàn bộ nguyên tắc thiết kế ban đầu, bối cảnh giải thích, các quyết định `FP-DEC-019`, `FP-DEC-020` và định nghĩa KPI được bảo toàn nguyên vẹn.

---

## 3. Trạng thái Git HEAD & Cây Làm việc Thực tế (Working-Tree State)

- **Nhánh Git hiện tại:** `master`
- **Git Commit HEAD:** `bc4f03fb8ccd6c0b2455af3fcb2b1b98fa39d632`
- **Tình trạng Cây làm việc:**
  - Không có bất kỳ thay đổi nào tác động lên 9 tệp RAW CSV nguồn (`15.196.366.173 bytes`) hoặc 50 tệp Parquet staging T-010 (`332 MB Snappy`, fingerprint `b5805fca...`).
  - Toàn bộ các tệp tài liệu quản trị sống (`BACKLOG.md`, `DECISIONS.md`, `CHANGELOG.md`, `AI_HANDOFF.md`, `PROJECT_STATE.md`) đã được đồng bộ hóa hoàn toàn và vượt qua bộ kiểm thử `tools/qa/verify_g2_repo_apply_r1_semantic_invariants.py` (15 Invariants PASS, 15 Mutation Tests PASS).

---

## 4. Đo đạc Tài nguyên Trạm Làm việc Thực tế (Workstation Resources)

Kết quả đo đạc từ lệnh thực thi `tools/qa/run_g6_t012_prestart_checks.py`:

| Thành phần Tài nguyên | Giá trị Thực tế Đo được | Ngưỡng Chính sách Bắt buộc | Đánh giá Trạng thái |
|---|---|---|---|
| **Dung lượng Trống Ổ D:** | **58.41 GiB** (trên tổng 300.00 GiB) | $\ge 25.0\text{ GiB}$ | **`PASS`** |
| **Dung lượng Trống Ổ C:** | **20.51 GiB** (trên tổng 154.86 GiB) | N/A (tham khảo hệ điều hành) | **`PASS`** |
| **Tổng Bộ nhớ RAM Vật lý:** | **15.71 GiB** | N/A (phần cứng máy trạm) | **`PASS`** |
| **Bộ nhớ RAM Khả dụng:** | **6.31 GiB** (tỷ lệ sử dụng 59.9%) | Tối thiểu $\ge 3.0\text{ GiB}$; Khuyến nghị $\ge 4.0\text{ GiB}$ | **`MEETS_RECOMMENDATION`** |
| **Số lượng Khóa Ghi Hoạt động:** | **0 active locks** trong `data/locks/` | $= 0$ (trạng thái tĩnh lặng) | **`CLEAN`** |
| **Trạng thái Con trỏ Xuất bản:** | `data/curated/latest_run_id.txt` | Cho phép chưa khởi tạo ở đợt đầu | **`UNINITIALIZED (VALID)`** |

> [!NOTE]
> Bộ nhớ RAM khả dụng đo được là **6.31 GiB**, vượt ngưỡng khuyến nghị tối ưu $\ge 4.0\text{ GiB}$ của dự án mà không cần kích hoạt cờ `--allow-resource-hold`. Máy trạm hoàn toàn sẵn sàng về mặt tài nguyên cho JVM Spark thực thi năm 2016.

---

## 5. Lệnh Kiểm tra Tiền Khởi động & Mã Thoát (Prestart Execution Log)

Runner tiền khởi động an toàn [`tools/qa/run_g6_t012_prestart_checks.py`](../../tools/qa/run_g6_t012_prestart_checks.py) đã thực thi toàn bộ 8 bước kiểm tra kiểm toán độc lập:

| STT | Bước Kiểm tra Tiền Khởi động | Lệnh Thực thi | Mã Thoát (`Exit Code`) | Kết quả |
| :---: | :--- | :--- | :---: | :---: |
| 1 | Trạng thái Git Working Tree | `git status --short` | `0` | **`PASS`** |
| 2 | Kiểm tra Tệp RAW 2016 Chuẩn | Hàm kiểm tra băm nội bộ (`evaluate_source_integrity`) | `0` | **`PASS`** |
| 3 | Kiểm toán Tài nguyên Máy trạm | Kiểm toán nội bộ `psutil` / `shutil` | `0` | **`PASS`** |
| 4 | Kiểm tra Khóa & Con trỏ Độc lập | `python tools/qa/check_writer_preflight_safety.py --base-dir data --run-id run_2016_v1 --json` | `0` | **`PASS`** |
| 5 | Kiểm toán Con trỏ Staging | `python tools/qa/verify_staging_pointer.py --base-dir data --allow-uninitialized --json` | `0` | **`PASS`** |
| 6 | Preflight Điều phối viên An toàn | `python src/flight_pipeline/ingestion/coordinator.py --years 2016 --run-id run_2016_v1 --base-data-dir data --dry-run-preflight --verify-hashes` | `0` | **`PASS`** |
| 7 | Xác minh Chốt chặn Quản trị D5 | Kiểm tra mã nguồn tĩnh + Unit Test `test_09_unauthorized_live_execution_blocked` | `0` | **`PASS`** |
| 8 | Giao diện Bộ Thẩm tra Single-Run | `python tools/qa/verify_multiyear_snapshot.py --help` | `0` | **`PASS`** |

**Phán quyết Tổng thể Runner Tiền Khởi động:** **`PRESTART OVERALL VERDICT: PASS`** (Exit Code: `0`).  
Nhật ký chi tiết được lưu trữ tại: [`docs/05-evidence/G6_T012_2016_PRESTART_RAW_LOG.txt`](G6_T012_2016_PRESTART_RAW_LOG.txt).

---

## 6. Xác minh Tính Toàn vẹn Nguồn & Ranh giới An toàn (Source & Safety)

### 6.1 Thuộc tính Tệp Nguồn RAW 2016 Chuẩn
- **Đường dẫn chuẩn:** `data/raw/tabular/2016/flight_with_weather_2016.csv`
- **Kích thước tệp vật lý:** `1,538,427,452` bytes (Khớp 100%)
- **Mã băm SHA-256 dòng chảy:** `4ed92ed732721a38ae28325135fad63436347613674ad96c1b273eb9d44cef34` (Khớp 100%)
- **Số dòng dự kiến theo danh mục kiểm toán:** `5,537,987` dòng (trích xuất từ `schema_2016.json`).
- *Ranh giới hạch toán dòng:* Số dòng trên là số dòng dự kiến được kiểm toán; số lượng dòng thực tế sẽ được kiểm chứng và hạch toán độc lập theo 3 trạng thái loại trừ lẫn nhau `accepted`, `quarantined`, `rejected` theo chuẩn `DC-11`/`DC-12` trong quá trình nạp dữ liệu.

### 6.2 An toàn Khóa & Con trỏ
- Thư mục khóa `data/locks/` hoàn toàn sạch, không có tệp `.pipeline.lock` tồn đọng.
- Thư mục dàn dựng `data/staging/run_2016_v1` chưa tồn tại (sạch sẽ, sẵn sàng cấp phát).
- Không có cờ phục hồi sự cố hoặc tệp đánh dấu lỗi dở dang.

---

## 7. Phụ thuộc Kích hoạt Quản trị D5 (D5 Governance Hold)

### 7.1 Hiện trạng Chốt chặn
Chốt chặn quản trị D5 trong [`src/flight_pipeline/ingestion/coordinator.py`](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/src/flight_pipeline/ingestion/coordinator.py) (dòng 231) đang ở trạng thái bảo vệ nghiêm ngặt:
```python
# Decision D5 is currently NOT_AUTHORIZED by Project Lead
D5_AUTHORIZED_BY_PROJECT_LEAD: bool = False
```
Khi thực thi lệnh trực tiếp không kèm cờ `--dry-run-preflight`, hệ thống kích hoạt chốt chặn fail-closed ngay lập tức:
```
[GOVERNANCE HOLD] Live ingestion execution is BLOCKED.
Decision D5 (Gate G6 Annual Ingestion Authorization) has NOT been approved by Project Lead.
Status: PENDING_D5
Per AGENTS.md, autonomous AI agents cannot authorize production data execution.
To execute live ingestion, Project Lead must explicitly approve Decision D5.
```

### 7.2 Quy trình Kích hoạt Được Kiểm soát Khi Project Lead Phê duyệt D5
Khi và chỉ khi Project Lead ban hành văn bản chính thức cấp phép Decision D5, bản vá 1 dòng duy nhất sẽ được áp dụng:
```python
# Chuyển đổi dưới sự kiểm soát:
D5_AUTHORIZED_BY_PROJECT_LEAD: bool = True
```
Ngoài dòng này, không tạo thêm bất kỳ framework hay runner trung gian nào.

---

## 8. Quy trình Thực thi & Thẩm định Hậu Thực thi Năm 2016 (Execution & Post-Run Runbook)

### 8.1 Lệnh Thực thi Sản xuất Năm 2016 (Sau khi có D5)
```powershell
python -m flight_pipeline.ingestion.coordinator --years 2016 --run-id run_2016_v1 --base-data-dir data
```

### 8.2 Ghi nhận Siêu dữ liệu Bất biến (Sidecars)
Sau khi hoàn tất, hệ thống sẽ tự động sinh:
1. `data/curated/runs/run_2016_v1/run_manifest.json`: Lưu trữ phiên bản mã nguồn Git, danh sách tệp Parquet đầu ra kèm mã băm SHA-256 và kích thước byte.
2. `data/curated/runs/run_2016_v1/execution_receipt.json`: Biên lai thực thi bảo chứng tính toàn vẹn của đợt chạy.
3. Cập nhật con trỏ `data/curated/latest_run_id.txt` trỏ tới `run_2016_v1` thông qua cơ chế xuất bản an toàn nguyên tử `SafePublisher`.

### 8.3 Quy trình Thẩm định Hậu Thực thi (Single-Run Validator)
Chạy bộ thẩm tra độc lập cho đợt chạy năm 2016:
```powershell
python tools/qa/verify_multiyear_snapshot.py --single-run-year 2016 --run-id run_2016_v1 --base-dir data
```
Bộ thẩm tra sẽ kiểm chứng 5 bất biến:
1. Quét đệ quy toàn bộ phân vùng Parquet (`discover_physical_parquet_files()`).
2. Khớp 1:1 danh mục tệp đầu ra trong manifest với tệp thực tế trên đĩa (đường dẫn, kích thước, SHA-256).
3. Hạch toán dòng `DC-11`: Khớp chính xác 5.537.987 dòng thô với tổng `accepted + quarantined + rejected`.
4. Tuân thủ Schema: Có đủ 7 trường đo CORE và không chứa các cột bị cấm.
5. Khớp biên lai thực thi với mã băm mật mã học của `run_manifest.json`.

### 8.4 Xử lý Khi Có Sự cố
- Nếu PySpark thất bại trong Pha 1 (Staging): Toàn bộ thư mục `data/staging/run_2016_v1` bị xóa sạch; con trỏ xuất bản không bị thay đổi.
- Nếu xảy ra sự cố giải phóng khóa sau xuất bản (Pha 2): Áp dụng chính sách `FP-DEC-018` — dữ liệu Parquet đã xuất bản giữ nguyên tính toàn vẹn, đánh dấu cờ `recovery_required = True` và chặn các writer tiếp theo cho đến khi hoàn tất khôi phục thủ công.

---

## 9. Đánh giá Tồn đọng & Phán quyết Quản trị Chung cuộc

- **Tồn đọng Kỹ thuật:** **KHÔNG CÒN (ZERO technical blockers).** Mọi điều kiện tiên quyết kỹ thuật, kiểm thử an toàn, kiểm tra tài nguyên và tính toàn vẹn nguồn đều đạt chuẩn 100%.
- **Hành động Duy nhất Còn lại:** Project Lead xem xét và ban hành quyết định phê duyệt chính thức **Decision D5**.

---

### PHÁN QUYẾT QUẢN TRỊ TỔNG THỂ

**Phán quyết:** **`READY_FOR_D5_HUMAN_AUTHORIZATION`**

- **Gate G6:** `READY_FOR_PREPARATION / BLOCKED_ON_D5`
- **Decision D5:** **`NOT_AUTHORIZED`**
- **Nhiệm vụ T-012:** **`NOT_STARTED`**
- **Dữ liệu Sản xuất Thực thi:** **`NO` (Zero production data written)**
