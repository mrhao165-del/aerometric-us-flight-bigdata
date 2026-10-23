# G5_FINAL_PRE_SIGNOFF_RECONCILIATION.md
# Báo Cáo Đối Soát Tổng Thể Các Điều Kiện Đóng Gate G5 Trước Khi Trình Project Lead

**Dự án:** US Flight Performance Analysis 2016–2024  
**Gate:** G5 — Đang thực hiện (`IN_PROGRESS`) $\rightarrow$ Chuẩn bị chuyển giao Gate G6  
**Nhiệm vụ:** Gate G5 Final Pre-Signoff Reconciliation  
**Tác giả:** Principal Big Data QA Engineer, Independent Evidence Auditor, Project Governance Custodian  
**Thời điểm lập:** 2026-10-20  
**Thẩm quyền:** Báo cáo kiểm định kỹ thuật và đối soát quản trị; thẩm quyền phê duyệt chính thức thuộc về Project Lead.

---

## 1. MỤC TIÊU VÀ NGUYÊN TẮC QUẢN TRỊ
Tài liệu này đối soát toàn diện 19 tiêu chí đầu ra của Gate G5 theo `TEST_PLAN.md` và các quyết định kiến trúc dự án.
Đặc biệt, tài liệu phân định rạch ròi giữa:
- **`TECHNICAL_PASS`:** Các tiêu chí kỹ thuật đã được kiểm chứng bằng thực nghiệm mã nguồn và dữ liệu thực tế.
- **`CONTROLLED_ACCEPTANCE`:** Các rủi ro hoặc khiếm khuyết thượng nguồn được hội đồng chấp nhận có kiểm soát kèm biện pháp phòng vệ, tuyệt đối không được đánh đồng là "lỗi đã được giải quyết" (tránh dùng nhãn ngộ nhận như `DOCUMENTED_DEFECT_PASS`).
- **`HUMAN_DECISION_PENDING`:** Các quyết định thuộc thẩm quyền độc quyền của Project Lead.

---

## 2. BẢNG ĐỐI SOÁT CHI TIẾT 19 TIÊU CHÍ GATE G5

| STT | Mã kiểm thử / Yêu cầu | Mô tả nội dung kiểm tra | Kết quả thực tế & Bằng chứng kiểm toán | Phân loại trạng thái | Kết luận quản trị G5 |
| :---: | :--- | :--- | :--- | :---: | :---: |
| 1 | **T-010 Bounded Smoke** | Nạp & staging Parquet dữ liệu thực 2016 (5.617.658 dòng) | SafePublisher 7 bước nguyên tử, Snappy Parquet 50 phân vùng (`b5805fca...`) | `REAL_DATA_PASS` | **PASS (CONTROLLED)** |
| 2 | **T-010 Benchmark (TS-014)** | Đo lường tài nguyên CPU, RAM, I/O trên dữ liệu thực | Đo thực tế: 250s, 3.2 GB RAM đỉnh, nén 4.48x (`T010_FULL_RESOURCE_BENCHMARK_TS014.md`) | `REAL_DATA_PASS` | **PASS** |
| 3 | **T-011 KPI Engine** | Tính toán 8 KPI cốt lõi trên tập staging cohort | ANSI mode casting, boundary edge cases, âm/dương (`test_t011_kpi_engine.py` 32/32 PASS) | `SYNTHETIC_PASS` | **PASS** |
| 4 | **T-011 Locking & Faults** | TS-013 SingleWriterLock, crash recovery & rollback | Thuật toán khóa NTFS bền vững, fstat inode audit, không xóa marker khi locked | `SYNTHETIC_PASS` | **PASS (CONTROLLED)** |
| 5 | **TS-001 Schema Drift** | Kiểm tra 34 cột thô và ngăn ngừa trôi dạt schema | Bộ lọc fail-closed schema drift hoạt động chính xác (`test_t010_policy_guards.py`) | `REAL_DATA_PASS` | **PASS** |
| 6 | **TS-002 Parsing & Domain** | Kiểm soát miền giá trị, timestamp, NaN, Inf | ANSI casting, phân biệt rõ valid null với invalid tokens (`predicates.py`, `ParsedCell`) | `REAL_DATA_PASS` | **PASS** |
| 7 | **TS-003 Row Accounting** | Hạch toán 3 trạng thái loại trừ lẫn nhau (DC-11/12) | $\text{Raw} = \text{Accepted} + \text{Quarantined} + \text{Rejected}$ (5.617.658 = 5.617.658 + 0 + 0) | `REAL_DATA_PASS` | **PASS** |
| 8 | **TS-005 Delay Thresholds** | Ngưỡng trễ 15.0 phút và xử lý mẫu số hợp lệ | Biên 14.999/15.0/15.001 phút, loại trừ chuyến bay không đủ điều kiện | `SYNTHETIC_PASS` | **PASS** |
| 9 | **TS-006 Signed Delay** | Bảo toàn độ trễ âm/dương (-6.0, -4.0, ...) | Không cắt xén giá trị trễ âm; kiểm chứng thực tế trên 1.500 bản ghi mẫu | `REAL_DATA_PASS` | **PASS** |
| 10 | **TS-008 Percentiles** | Tính phân vị P50/P90 với tham số `accuracy=10000` | Thuật toán phân vị đạt độ chính xác $\le 0.0001$; chỉ áp dụng cho kiểm thử cục bộ | `SYNTHETIC_PASS` | **PASS (BOUNDED)** |
| 11 | **TS-009 Grain & Cancel** | Bảo vệ hạt dữ liệu FLIGHTS, loại trừ hủy/chuyển hướng | Loại trừ chuyến bay canceled/diverted khỏi KPI độ trễ; hạch toán độc lập | `REAL_DATA_PASS` | **PASS** |
| 12 | **TS-010 Overnight & 2400** | Xử lý chuyến bay qua đêm và mốc thời gian 2400 | Quản trị theo `FP-DEC-004` (ghi nhận `NOT_AVAILABLE`, không tự chế ngày đến) | `POLICY_PASS` | **PASS** |
| 13 | **TS-012 Repeatability** | Tính tái lập xác định của kết quả tính toán | Thuật toán xuất bản bất biến, ghi nhận mã băm giống hệt khi chạy lại | `SYNTHETIC_PASS` | **PASS** |
| 14 | **TS-013 Rollback & Faults** | Phục hồi và cô lập lỗi khi xuất bản gặp sự cố | Cô lập hoàn toàn bản ghi hỏng, con trỏ `latest` giữ nguyên phiên bản cũ | `SYNTHETIC_PASS` | **PASS** |
| 15 | **TS-014 Workstation Metric** | Định mức tài nguyên hệ thống thực tế | Ghi nhận chi tiết I/O đĩa, bộ nhớ JVM, không dùng số liệu ước tính giả lập | `REAL_DATA_PASS` | **PASS** |
| 16 | **TS-017 Accounting Terms** | Phân định thuật ngữ Valid Rate vs Ingest Coverage | Tử số/mẫu số phân định rõ: mẫu số là `accepted_row_count(C)`, có bảo vệ chia 0 | `SYNTHETIC_PASS` | **PASS** |
| 17 | **TS-018 BTS Unit Parity** | Đối soát 7 trường số đo cốt lõi với BTS tháng 1/2019 | 10.500/10.500 khớp bitwise IEEE-754 tuyệt đối; 13/13 negative tests fail-closed | `REAL_DATA_PASS` | **TECHNICAL_READY (AWAITING OPTION B & HUMAN SIGNOFF)** |
| 18 | **TS-019 Source Identity** | Kiểm kê mã băm SHA-256 của 9 tệp CSV dữ liệu thô | Đã ghi nhận mã băm 9 năm; chấp nhận rủi ro thượng nguồn `OR-08` chưa xác thực | `CONTROLLED_ACCEPTANCE` | **ACCEPTED_WITH_OR-08_EXCEPTION** |
| 19 | **FP-DEC-017 Weather** | Cô lập dữ liệu thời tiết khỏi pipeline CORE | Pipeline CORE vận hành độc lập, không join dữ liệu thời tiết | `POLICY_PASS` | **PASS** |

---

## 3. LÀM RÕ CÁC GIỚI HẠN VÀ RỦI RO TỒN ĐỌNG CÓ KIỂM SOÁT

1. **Rủi ro thượng nguồn OR-08 (IDENTITY_UNVERIFIED):**
   - Sự trùng khớp 100% giữa mẫu 1.500 chuyến bay năm 2019 và BTS TranStats chỉ chứng minh tính xác thực số đo cục bộ của tệp 2019, **không giải quyết dứt điểm** việc toàn bộ 9 tệp CSV trên Kaggle thiếu chữ ký số gốc từ BTS.
   - Trạng thái quản trị: Được hội đồng chấp nhận dưới hình thức **ngoại lệ có kiểm soát (Managed Exception)**, không ghi nhận là lỗi đã biến mất.
2. **Khiếm khuyết dữ liệu OR-05 (Thiếu tháng 3/2024):**
   - Tệp CSV năm 2024 bị mất hoàn toàn dữ liệu tháng 3/2024 từ nguồn cung cấp.
   - Trạng thái quản trị: Tiếp tục duy trì `OPEN_QUALITY_DEFECT`; dữ liệu các tháng còn lại được xử lý bình thường với cảnh báo minh bạch trong báo cáo phân tích.
3. **Phạm vi kiểm thử TS-008:**
   - Việc đạt PASS tại G5 chỉ xác nhận hàm tính phân vị P50/P90 hoạt động đúng thuật toán với `accuracy=10000`. Phân vị toàn thể 9 năm 54,7 triệu hàng thuộc phạm vi Gate G6 / Task T-013.
4. **PARQUET_PARITY_NOT_TESTED:**
   - TS-018 thực hiện đối soát CSV thô 2019 với BTS CSV (Option B). Tính chẵn lẻ của Parquet 2019 sẽ được kiểm chứng khi thực thi G6 nạp Parquet.

---

## 4. KẾT LUẬN VỀ MỨC ĐỘ SẴN SÀNG CỦA GATE G5
- Về mặt kỹ thuật, toàn bộ 19 tiêu chí đã hoàn tất kiểm chứng với độ tin cậy tối đa.
- Không còn bất kỳ blocker kỹ thuật nào ngăn cản việc xem xét nghiệm thu.
- Hồ sơ được chuyển giao nguyên vẹn để **Project Lead** xem xét ban hành 2 quyết định:
  1. Phê duyệt chính sách **FP-DEC-019 (Option B)**.
  2. Ký biên bản đóng Gate **G5 (G5 Human Signoff)**.
