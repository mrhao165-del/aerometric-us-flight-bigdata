# G6_T012_READINESS_CHECKLIST.md
# Danh Mục Kiểm Tra Tính Sẵn Sàng Vận Hành Toàn Diện Pipeline 9 Năm (Task T-012 / Gate G6)

**Dự án:** US Flight Performance Analysis 2016–2024  
**Nhiệm vụ:** T-012 — 9-Year Full Pipeline Execution & Multidimensional KPI Aggregation  
**Cổng quản lý:** Gate G5 = IN_PROGRESS, Gate G6 = NOT_STARTED / BLOCKED  
**Quyết định cấp phép:** Quyết định độc lập D5 — **HIỆN TẠI ĐANG PENDING**  
**Tác giả:** Principal Big Data Engineer, Release & Evidence Manager  
**Thời điểm lập:** 2026-10-20  

---

## 1. NGUYÊN TẮC BẢO VỆ VẬN HÀNH BẮT BUỘC

> [!CAUTION]
> **LỆNH CẤM THỰC THI:** Danh mục kiểm tra này được thiết lập nhằm chuẩn bị trước cho Gate G6. Tuyệt đối **KHÔNG CHẠY BẤT KỲ NĂM DỮ LIỆU NÀO** trong phiên làm việc hiện tại khi chưa có quyết định phê duyệt D5 chính thức từ Project Lead.

1. **Bảo tồn bất biến Baseline 2016:**
   - 50 tệp Parquet năm 2016 đã đạt nghiệm thu tại Task T-010 (dấu vân tay mật mã `b5805fcae8db44e9a53c0eb1dfa1c1f3d9ec2983b3922bfbe5c6454f1654b09a`) là **bất biến tuyệt đối**.
   - Pipeline G6 chỉ đọc hoặc kế thừa phân vùng 2016; nghiêm cấm chạy đè hoặc xóa bỏ baseline 2016.
2. **Thực thi phân kỳ tuần tự từng năm (Year-by-Year Staging):**
   - Không nạp hoặc xử lý đồng thời cả 9 năm (54,7 triệu dòng) trong một tác vụ Spark duy nhất để tránh OOM hoặc lỗi đĩa.
   - Thứ tự thực thi: `2017` $\rightarrow$ `2018` $\rightarrow$ `2019` $\rightarrow$ `2020` $\rightarrow$ `2021` $\rightarrow$ `2022` $\rightarrow$ `2023` $\rightarrow$ `2024`.
3. **Điều kiện dừng khẩn cấp (Fail-Stop Condition):**
   - Nếu bất kỳ năm nào vi phạm đẳng thức hạch toán dòng DC-11 ($raw \neq accepted + quarantined + rejected$), pipeline phải lập tức **dừng toàn bộ hệ thống**, không tiếp tục sang năm sau và kích hoạt rollback con trỏ về năm thành công gần nhất.

---

## 2. BẢNG KIỂM TRA ĐIỀU KIỆN TIÊN QUYẾT TRƯỚC KHỞI CHẠY (PREFLIGHT CHECKLIST)

| STT | Hạng mục kiểm tra | Tiêu chuẩn bắt buộc | Lệnh kiểm tra thực tế | Trạng thái kỹ thuật |
| :---: | :--- | :--- | :--- | :---: |
| **P-01** | Quyết định đóng Gate G5 (D1–D4) | Đã được Project Lead ký phê duyệt chính thức | Đối soát văn bản phê duyệt trong `docs/05-evidence/` | `AWAITING_LEAD` |
| **P-02** | Quyết định mở Gate G6 (D5) | Có lệnh văn bản cấp phép khởi động T-012 | Kiểm tra chỉ thị D5 từ Project Lead | `PENDING` |
| **P-03** | Tính toàn vẹn 9 tệp CSV thô | 9/9 tệp khớp SHA-256 đã audit tại Gate G2 | `python tools/qa/verify_t006_contract_consistency.py` | `VERIFIED_PASS` |
| **P-04** | Dung lượng đĩa Drive D | Khả dụng $\ge 25,0$ GiB (đo thực tế $\ge 57,0$ GiB) | `python -c "import shutil; print(shutil.disk_usage('D:'))"` | `57.90 GiB (PASS)` |
| **P-05** | Baseline 2016 Parquet Staging | 50 tệp nguyên vẹn, khớp vân tay `b5805fca...` | `python tools/qa/verify_t010_parquet_schema_attestation.py` | `VERIFIED_PASS` |
| **P-06a** | Trạng thái con trỏ xuất bản (POINTER_STATE) | Con trỏ chưa khởi tạo hoặc trỏ phiên bản hợp lệ | `python tools/qa/verify_staging_pointer.py --allow-uninitialized` | `PASS (READ_ONLY)` |
| **P-06b** | Trạng thái khóa Single-Writer (WRITER_LOCK_STATE) | Không có active writer (`PROCESS_ALIVE`), 0 tệp recovery marker (`.del_*`, `.recovery_required*`) | Kiểm tra độc lập LockMetadata, PID liveness và `get_unresolved_recovery_artifacts()` (không dùng pointer) | `PENDING_OPERATIONAL_VERIFICATION` |
| **P-07** | Thư mục cách ly lỗi (Quarantine) | Sẵn sàng tại `data/quarantine/` | Kiểm tra đường dẫn tồn tại và có quyền ghi | `READY` |
| **P-08** | Chính sách cô lập Thời tiết | Tiếp tục cô lập dữ liệu thời tiết (FP-DEC-017) | Cấu hình `enable_weather=False` trong pipeline | `ENFORCED` |

---

## 3. LỘ TRÌNH THỰC THI VẬN HÀNH PHÂN KỲ TỪNG NĂM

### Giai đoạn 1: Năm 2017 – 2018 (Ổn định tiền đại dịch)
- **Năm 2017:** 5.677.153 dòng CSV thô $\rightarrow$ Đọc, phân loại chất lượng, ghi Staging Parquet 2017 $\rightarrow$ Kiểm tra đối soát DC-11 $\rightarrow$ Cập nhật con trỏ.
- **Năm 2018:** 7.213.446 dòng CSV thô $\rightarrow$ Xử lý tương tự $\rightarrow$ Hạch toán dòng $\rightarrow$ Đối soát con trỏ qua `verify_staging_pointer.py`.

### Giai đoạn 2: Năm 2019 – 2021 (Đại dịch COVID-19 và biến động sản lượng)
- **Năm 2019:** 7.422.037 dòng CSV thô $\rightarrow$ Tháng 1 đã được đối soát 100% với BTS tại TS-018 $\rightarrow$ Xử lý toàn bộ năm $\rightarrow$ Hạch toán dòng.
- **Năm 2020:** 4.686.075 dòng CSV thô $\rightarrow$ Năm có lượng chuyến bay sụt giảm mạnh do đại dịch $\rightarrow$ Đảm bảo các chỉ số min-N không bị lỗi chia cho 0.
- **Năm 2021:** 6.311.871 dòng CSV thô $\rightarrow$ Giai đoạn phục hồi ngành hàng không.

### Giai đoạn 3: Năm 2022 – 2024 (Hậu phục hồi và kiểm soát khiếm khuyết)
- **Năm 2022:** 7.009.728 dòng CSV thô.
- **Năm 2023:** 7.182.010 dòng CSV thô.
- **Năm 2024 (Kiểm soát khiếm khuyết OR-05):**
  - Số dòng CSV thô: 3.633.696 dòng (chỉ bao gồm tháng 1, 2, 4–8; **hoàn toàn mất tháng 3/2024**).
  - Hạch toán dòng: Xác nhận $raw = accepted + quarantined + rejected$ trên 3.633.696 dòng nhận được.
  - Cảnh báo bắt buộc: Bảng manifest ghi rõ cờ `PARTIAL_COVERAGE_OR05_WARNING`.

---

## 4. BẢNG ĐỐI SOÁT 8 CORE KPI SAU KHI HOÀN TẤT INGESTION

Sau khi toàn bộ 9 năm được chuyển đổi vào Curated Parquet, động cơ `KpiCalculator` sẽ tính toán 8 CORE KPI trên 4 chiều phân tích:

| Mã KPI | Tên chỉ số hiệu suất | Định nghĩa tính toán chuẩn (`KPI_SPEC.md`) | Chiều phân tích bắt buộc |
| :---: | :--- | :--- | :--- |
| **KPI-01** | OTP-15 Rate (On-Time Performance) | Tỷ lệ chuyến bay đến trễ $\le 15$ phút trên các chuyến hợp lệ | Năm, Hãng-Năm, Sân bay-Năm, Chặng bay-Năm |
| **KPI-02** | Mean Departure Delay | Thời gian trễ khởi hành trung bình (phút) | Năm, Hãng-Năm, Sân bay-Năm, Chặng bay-Năm |
| **KPI-03** | Mean Arrival Delay | Thời gian trễ đến nơi trung bình (phút) | Năm, Hãng-Năm, Sân bay-Năm, Chặng bay-Năm |
| **KPI-04** | Severe Delay Rate ($\ge 60$ min) | Tỷ lệ chuyến bay trễ đến $\ge 60$ phút | Năm, Hãng-Năm, Sân bay-Năm, Chặng bay-Năm |
| **KPI-05** | Mean Taxi-Out Time | Thời gian lăn bánh cất cánh trung bình (phút) | Sân bay-Năm, Năm |
| **KPI-06** | Mean Taxi-In Time | Thời gian lăn bánh cập cổng trung bình (phút) | Sân bay-Năm, Năm |
| **KPI-07** | Elapsed Time Ratio (Actual / Scheduled) | Tỷ số giữa thời gian bay thực tế và dự kiến | Chặng bay-Năm, Hãng-Năm |
| **KPI-08** | Flight Volume & Cancellation Proxy | Tổng sản lượng chuyến bay đã thực hiện và chỉ số hoạt động | Toàn bộ 4 chiều phân tích |

---

## 5. QUY TRÌNH HỒI PHỤC (ROLLBACK PROTOCOL)

Khi xảy ra lỗi tại bất kỳ năm nào ($Year_K$):
1. **Con trỏ không bị hỏng:** `SafePublisher` duy trì con trỏ trỏ về $Year_{K-1}$ hợp lệ.
2. **Kiểm tra con trỏ bằng công cụ:** Chạy `python tools/qa/verify_staging_pointer.py --base-dir data/` để xác nhận con trỏ trỏ về phiên bản hợp lệ gần nhất.
3. **Cách ly dữ liệu hỏng:** Toàn bộ thư mục staging hoặc versioned của $Year_K$ bị lỗi được giữ nguyên tại `data/staging/` hoặc chuyển vào `data/quarantine/` để điều tra forensic, không xóa bỏ đột ngột.
4. **Báo cáo sự cố:** Lập báo cáo sự cố ghi nhận nguyên nhân, stacktrace và thông số tài nguyên tại thời điểm lỗi.
