# G6_T012_FINAL_EXECUTION_CHECKLIST_V2.md
# Danh Mục Kiểm Tra Vận Hành T-012 Toàn Diện 9 Năm (Phiên Bản V2 — Đã Đối Soát Khắc Phục P01–P07)

**Dự án:** US Flight Performance Analysis 2016–2024  
**Nhiệm vụ:** T-012 — Nine-Year Pipeline Ingestion & Multidimensional KPI Aggregation  
**Cổng quản lý hiện tại:** Gate G5 = IN_PROGRESS, Gate G6 = NOT_STARTED / BLOCKED  
**Quyết định cấp phép D5:** **PENDING — CHƯA ĐƯỢC PHÊ DUYỆT**  
**Tác giả:** Principal Big Data Engineer, Release & Evidence Manager  
**Thời điểm lập:** 2026-10-20  

---

## 1. NGUYÊN TẮC AN TOÀN VẬN HÀNH BẮT BUỘC (CARDINAL RULES)

> [!CAUTION]
> **LỆNH CẤM THỰC THI (STRICT EXECUTION HOLD):**
> Danh mục kiểm tra này được thiết lập để chuẩn bị kỹ thuật cho Gate G6. Tuyệt đối **KHÔNG CHẠY BẤT KỲ NĂM DỮ LIỆU NÀO** trong phiên hiện tại. Gate G6 chỉ được mở khi Project Lead đã ký chính thức quyết định D5.

1. **Bảo tồn bất biến Baseline 2016:**
   - 50 tệp Parquet staging 2016 của T-010 (dấu vân tay `b5805fca...`) là bất biến.
   - Quá trình xử lý năm 2016 trong G6 tuân thủ quyết định kiến trúc tại [`G6_T012_2016_BASELINE_INTEGRATION_DECISION_DRAFT.md`](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/docs/05-evidence/G6_T012_2016_BASELINE_INTEGRATION_DECISION_DRAFT.md), không ghi đè lên các tệp staging T-010 có sẵn.
2. **Thực thi phân kỳ tuần tự từng năm (Year-by-Year Sequential Execution — Điều kiện G6-ARCH-2016):**
   - **Trường hợp Quyết định G6-ARCH-2016 phê duyệt Option B (Khuyến nghị):**
     * Xử lý tuần tự: $\mathbf{2016} \rightarrow 2017 \rightarrow 2018 \rightarrow 2019 \rightarrow 2020 \rightarrow 2021 \rightarrow 2022 \rightarrow 2023 \rightarrow 2024$.
     * Năm 2016 được chạy lại như một production run chính thức (`run_2016_v1`) vào `data/curated/runs/` để thống nhất RunManifest/ExecutionReceipt toàn bộ 9 năm.
     * Toàn bộ 50 tệp Parquet staging 2016 của T-010 được bảo tồn nguyên vẹn làm Golden Benchmark đối chứng.
   - **Trường hợp Quyết định G6-ARCH-2016 phê duyệt Option A:**
     * Thăng hạng 50 tệp Parquet staging T-010 cho năm 2016; pipeline thực thi tuần tự từ $2017 \rightarrow 2018 \rightarrow \dots \rightarrow 2024$.
   - Kiểm tra đối soát hạch toán dòng DC-11 ($raw = accepted + quarantined + rejected$) sau mỗi năm trước khi chuyển sang năm kế tiếp.
3. **Cơ chế dừng khẩn cấp (Fail-Stop & Atomic Rollback):**
   - Nếu bất kỳ năm nào vi phạm hạch toán dòng, lỗi phân vùng hoặc lỗi ghi Parquet, pipeline dừng ngay lập tức.
   - Con trỏ `curated/latest_run_id.txt` duy trì nguyên vẹn ở năm thành công trước đó thông qua quy trình rollback nguyên tử của `SafePublisher`.

---

## 2. BẢNG KIỂM TRA ĐIỀU KIỆN TIÊN QUYẾT TRƯỚC KHỞI CHẠY (PRE-EXECUTION CHECKLIST)

| Mã kiểm tra | Hạng mục kiểm tra | Tiêu chuẩn bắt buộc | Lệnh hoặc tài liệu đối soát | Trạng thái kỹ thuật |
| :---: | :--- | :--- | :--- | :---: |
| **PRE-01** | Quyết định đóng Gate G5 (D1–D4) | Đã được Project Lead ký phê duyệt chính thức | Đối soát văn bản phê duyệt trong `docs/05-evidence/` | `AWAITING_LEAD` |
| **PRE-02** | Quyết định mở Gate G6 (D5) | Project Lead ban hành lệnh bằng văn bản riêng | Chỉ thị văn bản D5 từ Project Lead | `PENDING` |
| **PRE-03** | Tính toàn vẹn 9 tệp CSV thô | Khớp 100% kích thước và mã băm canonical candidate | [`G6_T012_CANONICAL_SOURCE_INVENTORY.md`](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/docs/05-evidence/G6_T012_CANONICAL_SOURCE_INVENTORY.md) | `VERIFIED_PASS` |
| **PRE-04** | Dung lượng đĩa Drive D | Khả dụng $\ge 25.0$ GiB (đo thực tế $\ge 57.0$ GiB) | `python -c "import shutil; print(shutil.disk_usage('D:'))"` | `57.90 GiB (PASS)` |
| **PRE-05** | Baseline 2016 Parquet Staging | 50 tệp nguyên vẹn, khớp vân tay `b5805fca...` | `python tools/qa/verify_t010_parquet_schema_attestation.py` | `VERIFIED_PASS` |
| **PRE-06a**| Trạng thái con trỏ xuất bản (POINTER_STATE) | Con trỏ chưa khởi tạo hoặc trỏ phiên bản hợp lệ | `python tools/qa/verify_staging_pointer.py --allow-uninitialized --base-dir data` | `PASS (READ_ONLY)` |
| **PRE-06b**| Trạng thái khóa Single-Writer (WRITER_LOCK_STATE) | Không có active writer (`PROCESS_ALIVE`), 0 tệp recovery marker (`.del_*`, `.recovery_required*`) | `tests/test_lock_state_vs_pointer_state.py` chứng minh quy tắc đánh giá kép | `PENDING_AT_LAUNCH` |
| **PRE-07** | Thư mục cách ly lỗi (Quarantine) | Sẵn sàng tại `<base_data_dir>/quarantine/` | Kiểm tra quyền ghi và thư mục rỗng | `READY` |
| **PRE-08** | Chính sách cô lập Thời tiết | Tiếp tục cô lập dữ liệu thời tiết (FP-DEC-017) | Cấu hình `enable_weather=False` trong Coordinator | `ENFORCED` |

---

## 3. LỘ TRÌNH THỰC THI PHÂN KỲ TỪNG NĂM TRONG GATE G6

### Mẻ 0: Năm 2016 (Áp dụng khi phê duyệt G6-ARCH-2016 Option B)
- **Năm 2016:** 5.537.987 dòng CSV thô $\rightarrow$ Xử lý qua `IngestionCoordinator` (`run_2016_v1`) $\rightarrow$ Hạch toán dòng DC-11 ($5.537.987 = accepted + quarantined + rejected$) $\rightarrow$ Kiểm tra Parquet $\rightarrow$ Hoán đổi con trỏ qua `SafePublisher` $\rightarrow$ Đối chiếu song song với 50 Parquet T-010.

### Mẻ 1: Năm 2017 – 2018 (Giai đoạn ổn định trước đại dịch)
- **Năm 2017:** 5.575.872 dòng CSV thô $\rightarrow$ Xử lý qua `IngestionCoordinator` $\rightarrow$ Hạch toán dòng DC-11 $\rightarrow$ Kiểm tra Parquet $\rightarrow$ Hoán đổi con trỏ qua `SafePublisher`.
- **Năm 2018:** 6.986.842 dòng CSV thô $\rightarrow$ Thực hiện tương tự $\rightarrow$ Đối soát con trỏ bằng `verify_staging_pointer.py`.

### Mẻ 2: Năm 2019 – 2021 (Đại dịch COVID-19 và biến động sản lượng)
- **Năm 2019:** 7.161.827 dòng CSV thô $\rightarrow$ Tháng 1 đã được đối soát 100% bitwise exact với BTS tại TS-018 $\rightarrow$ Xử lý toàn bộ năm $\rightarrow$ Hạch toán dòng.
- **Năm 2020:** 4.312.091 dòng CSV thô $\rightarrow$ Năm có lượng chuyến bay sụt giảm mạnh do đại dịch $\rightarrow$ Bảo đảm các chỉ số min-N không bị lỗi chia cho 0 (`ZERO_DENOMINATOR`).
- **Năm 2021:** 5.755.666 dòng CSV thô $\rightarrow$ Giai đoạn phục hồi ngành hàng không.

### Mẻ 3: Năm 2022 – 2024 (Hậu phục hồi và kiểm soát khiếm khuyết OR-05)
- **Năm 2022:** 6.413.416 dòng CSV thô.
- **Năm 2023:** 6.645.461 dòng CSV thô.
- **Năm 2024 (Kiểm soát khiếm khuyết OR-05):**
  * Số dòng CSV thô: 6.284.841 dòng (335/366 ngày; **thiếu hoàn toàn tháng 3/2024**).
  * Hạch toán dòng: Xác nhận $raw = accepted + quarantined + rejected$ trên 6.284.841 dòng thực nhận.
  * Cảnh báo bắt buộc: Bảng manifest và receipt ghi nhận cờ `OR-05: OPEN_QUALITY_DEFECT` và `source_coverage_status = PARTIAL`.

---

## 4. TÍNH TOÁN 8 CORE KPI SAU HOÀN TẤT INGESTION 9 NĂM (CHUẨN HÓA THEO KPI_SPEC.md)

Sau khi dữ liệu 9 năm hoàn tất nạp vào Curated Storage, động cơ `KpiCalculator` sẽ tính toán 8 CORE KPI trên các chiều phân tích (`year`, `year-month`, `carrier-year`, `origin-year`, `dest-year`, `route-year`) tuân thủ tuyệt đối hợp đồng [`KPI_SPEC.md`](../02-design/KPI_SPEC.md) và `src/flight_pipeline/kpi/catalog.py`:

1. **KPI-01:** Tổng bản ghi accepted (`count_records(C)`).
2. **KPI-02:** Tỷ lệ trễ đến $\ge 15$ phút ($\sum_{valid} 1[\text{ARR\_DELAY} \ge 15] / N_{\text{valid}}(\text{ARR\_DELAY}, C)$).
3. **KPI-03:** Trễ đến trung bình có dấu ($\sum_{valid} \text{ARR\_DELAY} / N_{\text{valid}}(\text{ARR\_DELAY}, C)$, giữ nguyên giá trị âm của chuyến bay đến sớm).
4. **KPI-04:** Tỷ lệ trễ đi $\ge 15$ phút ($\sum_{valid} 1[\text{DEP\_DELAY} \ge 15] / N_{\text{valid}}(\text{DEP\_DELAY}, C)$).
5. **KPI-05:** Trễ đi trung bình có dấu ($\sum_{valid} \text{DEP\_DELAY} / N_{\text{valid}}(\text{DEP\_DELAY}, C)$, giữ nguyên giá trị âm của chuyến bay cất cánh sớm).
6. **KPI-06:** Phân vị P50 và P90 của độ trễ đến (tính bằng hàm `percentile_approx(ARR_DELAY, [0.5, 0.9], accuracy=10000)` theo FP-DEC-015).
7. **KPI-07:** Thời gian lăn bánh trung bình — gồm **hai submetrics** riêng biệt:
   * Submetric `TAXI_OUT`: Trung bình thời gian lăn bánh ra sân đỗ trên mẫu số $N_{\text{valid}}(\text{TAXI\_OUT}, C)$.
   * Submetric `TAXI_IN`: Trung bình thời gian lăn bánh vào cổng trên mẫu số $N_{\text{valid}}(\text{TAXI\_IN}, C)$.
8. **KPI-08:** Thời gian bay và hành trình trung bình — gồm **ba submetrics** riêng biệt:
   * Submetric `AIR_TIME`: Trung bình thời gian trên không trên mẫu số $N_{\text{valid}}(\text{AIR\_TIME}, C)$.
   * Submetric `ACTUAL_ELAPSED_TIME`: Trung bình tổng thời gian thực tế trên mẫu số $N_{\text{valid}}(\text{ACTUAL\_ELAPSED\_TIME}, C)$.
   * Submetric `CRS_ELAPSED_TIME`: Trung bình tổng thời gian lịch trình trên mẫu số $N_{\text{valid}}(\text{CRS\_ELAPSED\_TIME}, C)$.

*Ghi chú quản trị:* Nghiêm cấm đưa các đại lượng ngoài hợp đồng (như OTP-15 định nghĩa sai, Severe Delay $\ge 60$, Elapsed Time Ratio, hay Cancellation Proxy vốn bị chặn bởi FP-DEC-006 và OR-04) vào thay thế 8 CORE KPI. Mọi dòng output KPI phải có đủ 17 cột canonical theo DC-11/12. Nếu $N_{\text{valid}}=0$, trả về `null` kèm nhãn `ZERO_METRIC_DENOMINATOR` (FP-DEC-011). Áp dụng ngưỡng min-N theo FP-DEC-016.

---

## 5. KẾT LUẬN VẬN HÀNH

Tài liệu này thay thế hoàn toàn phiên bản sơ khai trước đó, loại bỏ mọi sai lệch về con trỏ, mã băm và cơ chế khóa. Danh mục sẵn sàng được kích hoạt ngay khi Project Lead ban hành quyết định D5.
