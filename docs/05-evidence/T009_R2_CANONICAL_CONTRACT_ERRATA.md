# T009-R2: CANONICAL CONTRACT & TEST ID RECONCILIATION ERRATA

**Task ID:** `T-009` (Remediation & Independent Corrective Audit R2)  
**Gate:** `G4`  
**Auditor:** Senior Big Data Architect & Data Quality Engineer  
**Date:** 2026-10-17  
**Status:** `ERRATA_FORMALIZED_AND_APPLIED`  

---

## 1. Bảng Đối Soát Chuẩn Tắc Mã Kiểm Thử (Canonical Test ID Reconciliation Table)

Trong báo cáo R1 ([`T009_R1_TEST_RESULTS.md`](T009_R1_TEST_RESULTS.md)), một số mã kiểm thử từ [`TEST_PLAN.md`](../03-quality/TEST_PLAN.md) đã bị gán nhãn sai lệch so với định nghĩa chính thức. Bảng dưới đây đối soát, đính chính và xác định trạng thái thực thi thực tế:

| Canonical Test ID | Định Nghĩa Chính Thức ([`TEST_PLAN.md`](../03-quality/TEST_PLAN.md)) | Cách Sử Dụng Trong R1 | Bản Chất Xung Đột | Hiệu Chỉnh Kỹ Thuật Chuẩn Tắc | Trạng Thái Thực Thi Thực Tế |
|:---:|---|---|---|---|:---:|
| **TS-009** | **Guard FLIGHTS, cancel/divert, weather optional** (REQ-04, T-002/011, G2 design/G5/G7). Không xuất count không có grain; weather không tự coi là mandatory. | Gọi nhầm là *"Environment & Toolchain Bootstrap Test"*. | TS-009 là rào chắn nghiệp vụ FLIGHTS/Weather, không phải bài test khởi tạo Spark. | Tách biệt kiểm thử đơn vị Spark bootstrap ([`test_spark_env.py`](../../tests/test_spark_env.py)) khỏi TS-009. TS-009 giữ nguyên phạm vi G5/G7. | **TS-009 CHƯA CHẠY** (Đúng kế hoạch; Unit test Spark PASS) |
| **TS-013** | **Fault injection, rollback pointer, invalid partial output** (REQ-07, T-011, G5 execution). Không publish run lỗi; bằng chứng rollback trên pipeline thực. | Tuyên bố TS-013 đã *"PASS"* hoàn toàn trong T-009. | T-009 mới chỉ mô phỏng hook bơm lỗi trong unit test ở mức module lưu trữ, chưa chạy trên pipeline dữ liệu thực tế của G5. | Đính chính: Bài test [`test_publication_safety.py`](../../tests/test_publication_safety.py) là kiểm thử đơn vị mô phỏng (unit simulation); kiểm thử vận hành TS-013 chính thức được bảo lưu tại G5/T-011. | **TS-013 BẢO LƯU CHO G5** (Unit simulation PASS) |
| **TS-014** | **Resource/benchmark:** CPU/RAM/disk/time logs đo thật trên pipeline (REQ-07, T-006/010/012, G5/G6). Không ước lượng PASS. | Gọi nhầm là *"Audit Manifest & Lineage Completeness Test"*. | TS-014 là đo lường tải tài nguyên vật lý khi xử lý dữ liệu lớn, không phải kiểm tra tuần tự hóa RunManifest. | Kiểm tra RunManifest là unit test của T-009 ([`test_manifest.py`](../../tests/test_manifest.py)). TS-014 chính thức đo lường tài nguyên sẽ thực hiện ở G5 và G6. | **TS-014 CHƯA CHẠY** (Đúng kế hoạch; Unit test Manifest PASS) |
| **TS-018** | **Verify seven CORE measure units/sign/domain từ source:** Citation/source/protocol cho cả 7 trường hoặc G2 BLOCKED (REQ-03/05, T-003, G2 doc / G5 exec). | Tuyên bố TS-018 đã *"PASS"* vì đã viết xong vị từ số thực hữu hạn. | TS-018 là điều kiện chặn cứng (mandatory hard stop) yêu cầu bằng chứng đơn vị đo, dấu và miền giá trị trên 54.7M hàng thực tế trước khi qua G6. Viết hàm `is_finite_numeric` chỉ là unit test chuẩn bị, không thay thế TS-018. | Đính chính: Kiểm tra vị từ trên DataFrame giả lập ([`test_numeric_predicates.py`](../../tests/test_numeric_predicates.py)) là thỏa mãn điều kiện `G3-COND-B`; nghĩa vụ kiểm chứng nguồn thực tế của TS-018 được bảo lưu nguyên vẹn tại G5 trước khi mở G6. | **TS-018 BẢO LƯU CHO G5** (Unit predicate PASS) |

---

## 2. Đính Chính Hợp Đồng Dữ Liệu DC-11 & DC-12 (Data Contract Errata)

Căn cứ văn bản chuẩn tắc [`DATA_CONTRACT.md`](../02-design/DATA_CONTRACT.md):

### 2.1. Hạch toán dòng ba trạng thái (DC-11)
- Bất biến bắt buộc:
  $$\text{raw\_row\_count} \equiv \text{accepted\_row\_count} + \text{quarantined\_row\_count} + \text{rejected\_row\_count}$$
- Không có trạng thái thứ tư.
- **Tỷ lệ tiếp nhận nạp liệu (Ingest Acceptance Rate):**
  $$\text{ingest\_acceptance\_rate} = \frac{\text{accepted\_row\_count}}{\text{raw\_row\_count}} \quad (\text{khi } \text{raw\_row\_count} > 0)$$
  Nếu `raw_row_count == 0` $\implies$ trả về `None` (quy tắc `ZERO_DENOMINATOR`, tuyệt đối không xuất 0.0%).

### 2.2. Mẫu số và tỷ lệ hợp lệ của thước đo (DC-12)
- Được tính toán trên một nhóm thuần tập (cohort) $C$ thuộc tập các bản ghi đã được tiếp nhận (`accepted`):
  - `count_records`: Số bản ghi accepted trong cohort $C$.
  - `count_metric_valid`: Số bản ghi trong $C$ thỏa mãn điều kiện miền giá trị và tính hữu hạn của riêng submetric $m$.
  - `excluded_count`: Số bản ghi bị loại trừ riêng cho $m$:
    $$\text{excluded\_count} = \text{count\_records} - \text{count\_metric\_valid}$$
  - **Tỷ lệ hợp lệ của thước đo (Metric Valid Rate):**
    $$\text{metric\_valid\_rate} = \frac{\text{count\_metric\_valid}}{\text{count\_records}} \quad (\text{khi } \text{count\_records} > 0)$$
    Nếu `count_records == 0` $\implies$ trả về `None` kèm cờ `ZERO_DENOMINATOR`.

### 2.3. Đính chính sai sót trong báo cáo R1
- Trong [`T009_R1_IMPLEMENTATION_REPORT.md`](T009_R1_IMPLEMENTATION_REPORT.md), Mục 2.3 đã ghi sai công thức: `calculate_valid_rate(): accepted / (accepted + quarantined)`. Công thức này hoàn toàn sai lệch và vi phạm DC-12 vì nhầm lẫn giữa tỷ lệ tiếp nhận nạp liệu ở cấp bản ghi với tỷ lệ hợp lệ của từng thước đo độc lập.
- **Khắc phục:** Đã bổ sung trong [`src/flight_pipeline/utils/run_manifest.py`](../../src/flight_pipeline/utils/run_manifest.py) hai mô hình phân định rành mạch:
  1. `RowAccounting.calculate_ingest_acceptance_rate()`: Tính toán chuẩn tắc theo DC-11/12 cấp độ ingest.
  2. `MetricAccounting.calculate_metric_valid_rate()`: Tính toán chuẩn tắc theo DC-12 cấp độ submetric, với xử lý `ZERO_DENOMINATOR` trả về `None`.

---

## 3. Đính Chính Các Điều Kiện Chuyển Giao Gate G3 (G3 Conditions Errata)

Áp dụng chính xác biên bản [`G3_OFFICIAL_SIGNOFF_HUMAN_ACCEPTANCE_RECORD.md`](G3_OFFICIAL_SIGNOFF_HUMAN_ACCEPTANCE_RECORD.md):
1. **`G3-COND-A` (Record Quarantine Policy is PROVISIONAL):**
   - Ràng buộc G2-EXC-001 tiếp tục là tạm thời (provisional).
   - Tuyệt đối không tự ý hard-code điều kiện `OP_CARRIER_FL_NUM <= 0` thành cách ly toàn dòng (`quarantined`); phân biệt rõ ràng giữa tính không hợp lệ của bản ghi (record validity) và tính không hợp lệ của từng trường đo (metric validity).
2. **`G3-COND-B` (Unit verification for `is_finite_numeric`):**
   - Đã kiểm chứng thành công trên DataFrame PySpark giả lập đối với các trường hợp `NULL`, `NaN`, $+\infty$, $-\infty$, số 0, số âm và số dương hữu hạn.
   - Kiểm thử này hoàn toàn không thay thế bài kiểm thử thống kê TS-008 trên dữ liệu 9 năm tại G5/G6.
3. **`G3-COND-C` (Windows NTFS Staged Publication Engine):**
   - Đã hiện thực hóa cơ chế an toàn 7 bước chống rách dữ liệu và kiểm tra con trỏ atomically trên Windows NTFS.
   - Thử nghiệm này ở mức unit test và không thay thế việc kiểm thử vận hành TS-013 trên toàn bộ pipeline ở Gate G5.

---

## 4. Đính Chính Số Lượng Dòng Dữ Liệu Audited (Source Row Count Errata)

- **Số liệu ghi trong báo cáo R1:** `54,670,361 dòng`.
- **Số liệu chuẩn tắc đã được kiểm toán:** `54,674,003 dòng`.
- **Sai lệch:** `3,642 dòng`.
- **Kết luận:** Đây là lỗi đánh máy đơn lẻ trong văn bản Markdown tổng kết R1. Toàn bộ 9 tệp CSV thô (2016–2024) có tổng số dòng chính xác tuyệt đối là **54,674,003 dòng**, được bảo toàn nguyên vẹn 100%.
