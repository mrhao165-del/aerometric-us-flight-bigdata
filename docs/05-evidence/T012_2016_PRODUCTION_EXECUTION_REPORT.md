# Báo cáo Thực thi Nạp Dữ liệu Sản xuất Năm 2016 (T-012 Production Ingestion Report)

**Mã tài liệu:** `T012_2016_PRODUCTION_EXECUTION_REPORT`  
**Ngày thực hiện:** 2026-10-21  
**Dự án:** US Flight Performance Analysis 2016–2024  
**Nhiệm vụ:** `T-012 — Controlled Annual Ingestion, Year 2016`  
**Vai trò:** Senior PySpark Engineer & Production Data Pipeline Operator  
**Căn cứ Ủy quyền:** Project Lead Decision D5 Official Approval (2026-10-21)  
**Phán quyết Chung cuộc:** **`T012_2016_PASS_CONTROLLED`**

---

## 1. Căn cứ Ủy quyền Decision D5 của Project Lead (Authorization Reference)

Vào ngày 2026-10-21, Project Lead đã ban hành văn bản phê duyệt chính thức cấp phép Decision D5 với phạm vi được giới hạn có kiểm soát:

> *"Tôi, với vai trò Project Lead của dự án US Flight Performance Analysis 2016–2024, **chính thức phê duyệt Decision D5 — PASS (CONTROLLED)**, giới hạn cho lần thực thi T-012 đầu tiên đối với dữ liệu năm 2016, sử dụng `run_2016_v1` theo FP-DEC-020 Option B.*  
> *Việc thực thi chỉ được tiến hành khi kiểm tra prestart tại thời điểm chạy đạt PASS, RAM khả dụng tối thiểu 4 GiB, nguồn RAW được xác minh và các điều kiện lock, pointer, recovery đều an toàn.*  
> *Tôi không cấp phép thực thi các năm 2017–2024, không cho phép tự động bỏ qua điều kiện an toàn, tự xử lý sự cố publication hoặc ghi đè dữ liệu đã tồn tại.*  
> *Sau lần chạy năm 2016, Agent phải dừng và cung cấp bằng chứng nghiệm thu để tôi xem xét trước khi tiếp tục."*

---

## 2. Kết quả Thẩm định Tiền Khởi động (Phase A — Final Preflight)

Trước khi kích hoạt lệnh sản xuất, toàn bộ 10 tiêu chí tiền điều kiện an toàn đã được thẩm định tự động và xác nhận đạt chuẩn 100%:

| Tiêu chí Kiểm tra | Giá trị Thực tế Xác minh | Ngưỡng Quy chuẩn | Trạng thái |
|---|---|---|:---:|
| **Gate G5** | `PASS (CONTROLLED)` (Project Lead phê duyệt 2026-10-21) | Bắt buộc PASS | **`PASS`** |
| **Quyết định D5** | Ủy quyền rõ ràng cho năm 2016, `run_2016_v1` | Bắt buộc có văn bản Project Lead | **`PASS`** |
| **Tính Hợp lệ Run ID** | `run_2016_v1` hợp lệ, chưa từng xuất hiện trên đĩa | Unused & Valid format | **`PASS`** |
| **Nguồn RAW CSV 2016** | `1,538,427,452` bytes, SHA-256 `4ed92ed7...` | Khớp 100% danh mục kiểm toán | **`PASS`** |
| **Dung lượng Ổ đĩa D:** | **58.41 GiB** trống | $\ge 25.0\text{ GiB}$ | **`PASS`** |
| **RAM Khả dụng:** | **5.82 GiB** khả dụng (tại thời điểm chạy) | $\ge 4.0\text{ GiB}$ | **`PASS`** |
| **Khóa Ghi Đơn (Lock):** | 0 khóa hoạt động trong `data/locks/` | Clean Mutex | **`CLEAN`** |
| **Cờ Khôi phục Sự cố:** | 0 tệp phục hồi dở dang trong `data/` | Không có lỗi tồn đọng | **`PASS`** |
| **Con trỏ Xuất bản:** | `latest_run_id.txt` chưa khởi tạo | Hợp lệ cho đợt chạy đầu tiên | **`PASS`** |
| **Preflight Dry-Run:** | `--dry-run-preflight --verify-hashes` exit code 0 | Khớp preflight inspection | **`PASS`** |

---

## 3. Bản vá Kích hoạt D5 Có Kiểm soát (Phase B — Controlled D5 Activation)

Tuân thủ nghiêm ngặt chỉ thị không dùng cờ `True` toàn cục tự do, bản vá kích hoạt hẹp được áp dụng trong [`src/flight_pipeline/ingestion/coordinator.py`](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/src/flight_pipeline/ingestion/coordinator.py):

```python
    # Controlled D5 Authorization by Project Lead (Approved 2026-10-21):
    # Strictly authorized for Year 2016 only and run_id 'run_2016_v1' under FP-DEC-020 Option B.
    # Rejects any year or run_id outside this specific authorization scope.
    D5_AUTHORIZED_FOR_2016_RUN1: bool = (
        args.years == [2016] and args.run_id == "run_2016_v1"
    )

    if not D5_AUTHORIZED_FOR_2016_RUN1:
        print("\n[GOVERNANCE HOLD] Live ingestion execution is BLOCKED.")
        print("Decision D5 is strictly authorized ONLY for year 2016 and run_id 'run_2016_v1'.")
        print("Status: UNAUTHORIZED_SCOPE_OR_PENDING_D5")
        print("Execution of any other year (2017-2024) or unapproved run_id is forbidden.")
        return 1
```

*Kiểm thử phủ định trước khi chạy:*
- Lệnh thử với `--years 2017`: Bị chặn lập tức với `UNAUTHORIZED_SCOPE_OR_PENDING_D5` (Exit code: 1).
- Lệnh thử với `--run-id run_2016_v2`: Bị chặn lập tức với `UNAUTHORIZED_SCOPE_OR_PENDING_D5` (Exit code: 1).

---

## 4. Nhật ký Thực thi Lệnh Sản xuất Năm 2016 (Phase C — Production Execution)

- **Lệnh thực thi chính thức:**
  ```powershell
  $env:PYTHONPATH='src'; python -m flight_pipeline.ingestion.coordinator --years 2016 --run-id run_2016_v1 --base-data-dir data --verify-hashes
  ```
- **Mã thoát (`Exit Code`):** **`0`**
- **Thông điệp kết thúc:** `[INGESTION SUCCESS] Run run_2016_v1 published successfully.`
- **Tiến trình PySpark:** Hoàn thành đầy đủ toàn bộ các Stage từ `Stage 0` đến `Stage 10`.
- **Nhật ký thô:** Được lưu trữ đầy đủ tại [`docs/05-evidence/T012_2016_PRODUCTION_EXECUTION_LOG.txt`](T012_2016_PRODUCTION_EXECUTION_LOG.txt).

---

## 5. Thẩm định Vật lý Sản phẩm Đầu ra (Phase D — Physical Verification)

### 5.1 Kiểm toán Con trỏ Xuất bản (`SafePublisher`)
- **Tệp con trỏ:** `data/curated/latest_run_id.txt`
- **Giá trị con trỏ nguyên tử:** `run_2016_v1` (Khớp 100%)
- **Trạng thái con trỏ:** `VALID_POINTER`

### 5.2 Kiểm toán Tệp Dữ liệu Parquet Sản xuất
- **Thư mục lưu trữ:** `data/curated/runs/run_2016_v1/`
- **Số lượng phân vùng Parquet:** **12 tệp** (`part-00000.parquet` đến `part-00011.parquet`).
- **Tổng dung lượng Parquet:** **332,018,057 bytes** (khoảng `316.64 MB`, nén Snappy).
- **Tổng số dòng đọc qua PyArrow Metadata:** **5,537,987 dòng** (khớp chính xác 100% số dòng dự kiến của năm 2016).
- **Số cột:** **34 cột**, bảo toàn thứ tự và kiểu dữ liệu chuẩn tắc.
- **7 trường đo CORE:** `ARR_DELAY`, `DEP_DELAY`, `TAXI_OUT`, `TAXI_IN`, `AIR_TIME`, `ACTUAL_ELAPSED_TIME`, `CRS_ELAPSED_TIME` đều hiện diện đầy đủ, không null bất thường.
- **Cột bị cấm:** Hoàn toàn **KHÔNG** chứa `CANCELLED`, `DIVERTED`, `CANCELLATION_CODE` hay `ELAPSED_DIFF`.

### 5.3 Danh mục Tệp Parquet Chi tiết
| Tệp Phân vùng Parquet | Kích thước (Bytes) | Mã băm SHA-256 |
|---|---|---|
| `part-00000.parquet` | 28,414,121 | `6349e23a90d7291a42b12a0e29b3c44d8bda9e705a98306dd9156a268251e5dc` |
| `part-00001.parquet` | 28,603,245 | `c8f6ed6d879a1284621ac245134aa46995d38ce837b4a596526507e94d6d970c` |
| `part-00002.parquet` | 28,637,691 | `e45f2573fc64969778559c43556c9c9d4bf476e839e48d07a7b1422530e94579` |
| `part-00003.parquet` | 28,540,494 | `c74b4837c44b1a8eb9ae9549f5e7bc6cd041848da72c777a5d9c8cfe61bb9fa3` |
| `part-00004.parquet` | 29,314,492 | `06a43a9025eb28c5f878d488951e12d31a66ecbc2b31a8e18ab34050e25991a7` |
| `part-00005.parquet` | 28,892,448 | `89304e6d890eed377ff12abd7d59fd2a2517eca275d48b6e4dea3ff9fc4e3124` |
| `part-00006.parquet` | 28,688,181 | `e614d23011b0204d1841ed33999e9beb6a69e6492d2532bf85c3871d0886fed0` |
| `part-00007.parquet` | 29,227,574 | `68e0509f524235d4efaf7ea16f027c3a12079897d1c33191cad160e5c348c6ae` |
| `part-00008.parquet` | 29,156,297 | `3f6806512c75beb08d78fe42e93e308a7f4a1ce3d6b2db0f692f3cd7564df102` |
| `part-00009.parquet` | 29,369,525 | `882b743ba4db29ff83991c01cd3e5ce95b4a9d1aa056191e419ccb9920e433e1` |
| `part-00010.parquet` | 29,439,506 | `6c07dbcd391eac97488ce73ee6998815159c9a2a221929a81e71b9949f530a23` |
| `part-00011.parquet` | 13,734,483 | `e677d6505f89b9c758e70cb4aefd76182291cfbd1ec2888e49d8d085f2e4eb2f` |

### 5.4 Hạch toán Dòng Cân bằng theo DC-11 / DC-12
Phương trình hạch toán dòng được chứng minh cân bằng tuyệt đối:
$$\text{raw\_row\_count } (5,537,987) = \text{accepted } (5,537,987) + \text{quarantined } (0) + \text{rejected } (0)$$
- **Tỷ lệ chấp thuận (`ingest_acceptance_rate`):** `1.0` (`100.0%`).
- **Trạng thái cân bằng (`is_balanced`):** `True`.

### 5.5 Kiểm toán Siêu dữ liệu Độc lập (`RunManifest` & `ExecutionReceipt`)
- **Tệp RunManifest:** `data/metadata/run_2016_v1/run_manifest.json`
  - Trạng thái: `PUBLISHED`
  - SHA-256: `636c9b7fbb7df81be751fbd0220e8a8a209409a471c31e71de269f94bd7bf340`
  - Kích thước: `5,401` bytes
- **Tệp ExecutionReceipt:** `data/metadata/run_2016_v1/execution_receipt.json`
  - Khớp 1:1 mã băm của `run_manifest.json` (`636c9b7f...`).
  - Trạng thái xuất bản: `PUBLISHED`.
  - Thời điểm hoàn tất: `2026-10-21T11:12:55.367874+00:00`.

### 5.6 Kết quả Chạy Bộ Thẩm định Single-Run Chuẩn
Lệnh thực thi bộ thẩm tra:
```powershell
python tools/qa/verify_multiyear_snapshot.py --single-run-year 2016 --run-id run_2016_v1 --base-dir data
```
**Kết quả:**
```
================================================================================
SINGLE ANNUAL RUN AUDIT: [PASS] VALID_SINGLE_RUN_ANNUAL_BATCH
================================================================================
Survey Year:         2016
Run ID:              run_2016_v1
Base Directory:      D:\Study\Code\Apache\Flight_Analyzt\US_FLIGHT_PERFORMANCE_DOCS_V1\data
Validation Status:   VALID_SINGLE_RUN_ANNUAL_BATCH
Valid:               True
Total Raw Rows:      5,537,987
Total Accepted Rows: 5,537,987
Total Quarantined:   0
Total Rejected Rows: 0
================================================================================
```
Exit Code: `0` (`PASS`).

---

## 6. Đóng Khung Cửa Sổ Ủy quyền D5 (Phase E — End Authorization)

Ngay sau khi quá trình thẩm định hoàn tất, hệ thống đã lập tức được đưa trở lại trạng thái phong tỏa mặc định (`fail-closed`) trong [`src/flight_pipeline/ingestion/coordinator.py`](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/src/flight_pipeline/ingestion/coordinator.py):

```python
    # Strict fail-closed governance: D5 authorization window closed post-2016 run_2016_v1 completion
    D5_AUTHORIZED_BY_PROJECT_LEAD: bool = False

    if not D5_AUTHORIZED_BY_PROJECT_LEAD:
        print("\n[GOVERNANCE HOLD] Live ingestion execution is BLOCKED.")
        print("Decision D5 (Gate G6 Annual Ingestion Authorization) has NOT been approved by Project Lead.")
        print("Status: PENDING_D5")
        print("Per AGENTS.md, autonomous AI agents cannot authorize production data execution.")
        print("To execute live ingestion, Project Lead must explicitly approve Decision D5.")
        return 1
```

*Kiểm chứng khóa cổng sau thực thi:*
- Mọi lệnh gọi coordinator nạp dữ liệu sống mà không có ủy quyền mới đều bị chặn lập tức với thông báo `[GOVERNANCE HOLD] Live ingestion execution is BLOCKED.`
- Lệnh gọi lại chính `run_2016_v1` bị từ chối với lỗi trùng lặp `[PREFLIGHT FAIL] Duplicate run_id...` để bảo vệ tính bất biến của bộ dữ liệu đã xuất bản.

---

## 7. Giới hạn Còn tồn tại Được Bảo lưu Nghiêm ngặt (Residual Scope)

1. **Phạm vi Duy nhất 2016:** Đây là đợt nạp sản xuất duy nhất cho năm 2016; **các năm 2017–2024 hoàn toàn CHƯA ĐƯỢC CẤP PHÉP**.
2. **Gate G6 Chưa Hoàn tất:** Gate G6 giữ trạng thái `IN_PROGRESS (2016_VERIFIED)` và chưa được đóng.
3. **`OR-05`:** Năm 2024 thiếu Tháng 3/2024 tiếp tục được theo dõi riêng.
4. **`OR-08`:** Nguồn gốc Kaggle giữ nguyên `IDENTITY_UNVERIFIED`.
5. **`FP-DEC-017`:** Thời tiết tiếp tục giữ nguyên phán quyết `CONDITIONAL_NO_GO`.
6. **Bảo tồn T-010 Staging:** 50 tệp Parquet staging T-010 được giữ nguyên vẹn trên đĩa như bằng chứng lịch sử bất biến.

---

## 8. Phán quyết Chung cuộc (Final Verdict)

# **`T012_2016_PASS_CONTROLLED`**

Đợt nạp dữ liệu sản xuất đầu tiên cho năm 2016 (`run_2016_v1`) đã hoàn thành xuất sắc, được kiểm chứng vật lý toàn diện, hạch toán dòng DC-11 cân bằng tuyệt đối, và chốt chặn quản trị D5 đã được đóng lại an toàn.  
Hệ thống dừng hoàn toàn để chờ Project Lead xem xét và chỉ đạo cho các bước tiếp theo.
