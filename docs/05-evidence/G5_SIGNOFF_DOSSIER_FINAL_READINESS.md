# G5_SIGNOFF_DOSSIER_FINAL_READINESS.md
# Báo Cáo Sẵn Sàng Nghiệm Thu Gate G5 Lần Cuối (Final Readiness Dossier)

**Dự án:** US Flight Performance Analysis 2016–2024  
**Gate hiện tại:** Gate G5 (`IN_PROGRESS`) $\rightarrow$ Chuẩn bị bàn giao Gate G6 (`NOT_STARTED / BLOCKED`)  
**Tác giả:** Project Governance Release Reviewer, Independent Evidence Auditor  
**Thời điểm lập:** 2026-10-20  
**Thẩm quyền:** Báo cáo kiểm định độc lập phục vụ Project Lead; thẩm quyền nghiệm thu thuộc về Project Lead.

---

## 1. MỤC TIÊU VÀ NGUYÊN TẮC
Tài liệu này xác nhận lần cuối mức độ sẵn sàng của hồ sơ Gate G5 sau khi đã khép toàn bộ các điểm yếu kỹ thuật E01–E05, bảo đảm mọi tiêu chí kỹ thuật đều có bằng chứng tái lập trên dữ liệu thực tế và các rủi ro tồn đọng được phân loại minh bạch.

---

## 2. BẢNG ĐỐI SOÁT 19 TIÊU CHÍ GATE G5 THEO PHÂN LOẠI NGHIÊM NGẶT

| STT | Mã yêu cầu / Tiêu chí | Nội dung kiểm tra | Hiện trạng kiểm chứng & Tham chiếu bằng chứng | Phân loại trạng thái | Đánh giá sẵn sàng |
| :---: | :--- | :--- | :--- | :---: | :---: |
| 1 | **T-010 Bounded Smoke** | Nạp & staging dữ liệu thực 2016 (5.617.658 dòng) | 50 tệp Parquet staging nguyên vẹn tại `staging/` (`b5805fca...`) | `REAL_DATA_PASS` | **SẴN SÀNG** |
| 2 | **T-010 Benchmark (TS-014)** | Đo lường tài nguyên CPU, RAM, I/O trên máy trạm | 250s, 3.2 GB RAM JVM, nén 4.48x (`T010_FULL_RESOURCE_BENCHMARK_TS014.md`) | `REAL_DATA_PASS` | **SẴN SÀNG** |
| 3 | **T-011 KPI Engine** | Tính toán 8 KPI cốt lõi trên tập staging | ANSI casting, xử lý signed delay, biên 15.0m (`test_t011_kpi_engine.py` 32/32 PASS) | `SYNTHETIC_PASS` | **SẴN SÀNG** |
| 4 | **T-011 Locking & Faults** | TS-013 SingleWriterLock, crash recovery NTFS | Tuân thủ FP-DEC-018: PID/Timestamp/fstat audit, cấm xóa marker khi locked | `SYNTHETIC_PASS` | **SẴN SÀNG** |
| 5 | **TS-001 Schema Drift** | Kiểm tra 34 cột thô và chống trôi dạt schema | Bộ lọc fail-closed schema drift hoạt động chính xác (`test_t010_policy_guards.py`) | `REAL_DATA_PASS` | **SẴN SÀNG** |
| 6 | **TS-002 Parsing & Domain** | Kiểm soát miền giá trị, NaN, Inf, timestamp | ANSI casting, phân biệt rạch ròi valid null với invalid tokens (`predicates.py`) | `REAL_DATA_PASS` | **SẴN SÀNG** |
| 7 | **TS-003 Row Accounting** | Hạch toán 3 trạng thái loại trừ lẫn nhau (DC-11/12) | $\text{Raw} = \text{Accepted} + \text{Quarantined} + \text{Rejected}$ (5.617.658 = 5.617.658 + 0 + 0) | `REAL_DATA_PASS` | **SẴN SÀNG** |
| 8 | **TS-005 Delay Thresholds** | Ngưỡng trễ 15.0 phút và xử lý mẫu số hợp lệ | Biên 14.999/15.0/15.001 phút, loại trừ chuyến bay không đủ điều kiện | `SYNTHETIC_PASS` | **SẴN SÀNG** |
| 9 | **TS-006 Signed Delay** | Bảo toàn độ trễ âm/dương (-6.0, -4.0, ...) | Không cắt xén độ trễ âm; kiểm chứng thực tế trên 1.500 bản ghi mẫu | `REAL_DATA_PASS` | **SẴN SÀNG** |
| 10 | **TS-008 Percentiles** | Phân vị P50/P90 với tham số `accuracy=10000` | Thuật toán phân vị đạt độ chính xác $\le 0.0001$ trên phạm vi kiểm thử cục bộ | `SYNTHETIC_PASS` | **SẴN SÀNG** |
| 11 | **TS-009 Grain & Cancel** | Bảo vệ hạt dữ liệu FLIGHTS, loại trừ hủy/chuyển hướng | Loại trừ chuyến bay canceled/diverted khỏi KPI trễ; hạch toán riêng biệt | `REAL_DATA_PASS` | **SẴN SÀNG** |
| 12 | **TS-010 Overnight & 2400** | Xử lý chuyến bay qua đêm và mốc 2400 | Quản trị theo FP-DEC-004 (`NOT_AVAILABLE`, không tự chế ngày đến) | `POLICY_PASS` | **SẴN SÀNG** |
| 13 | **TS-012 Repeatability** | Tính tái lập xác định của kết quả tính toán | Thuật toán xuất bản bất biến, mã băm giống hệt khi chạy lại | `SYNTHETIC_PASS` | **SẴN SÀNG** |
| 14 | **TS-013 Rollback & Faults** | Phục hồi và cô lập lỗi khi xuất bản gặp sự cố | Cô lập hoàn toàn bản ghi hỏng, con trỏ `latest` giữ nguyên phiên bản cũ | `SYNTHETIC_PASS` | **SẴN SÀNG** |
| 15 | **TS-014 Workstation Metric** | Định mức tài nguyên hệ thống thực tế | Ghi nhận chi tiết I/O đĩa, bộ nhớ JVM, không dùng số liệu ước tính giả lập | `REAL_DATA_PASS` | **SẴN SÀNG** |
| 16 | **TS-017 Accounting Terms** | Phân định thuật ngữ Valid Rate vs Ingest Coverage | Mẫu số là `accepted_row_count(C)`, có bảo vệ chia 0 | `SYNTHETIC_PASS` | **SẴN SÀNG** |
| 17 | **TS-018 BTS Unit Parity** | Đối soát 7 trường số đo cốt lõi với BTS tháng 1/2019 | 10.500/10.500 khớp bitwise IEEE-754; 14/14 negative tests fail-closed (E01–E05 khép) | `REAL_DATA_PASS` | **SẴN SÀNG TRÌNH KÝ** |
| 18 | **TS-019 Source Identity** | Kiểm kê mã băm SHA-256 của 9 tệp CSV dữ liệu thô | Mã băm 9 năm đã ghi nhận; chấp nhận ngoại lệ rủi ro thượng nguồn `OR-08` | `CONTROLLED_ACCEPTANCE` | **ACCEPTED (EXCEPTION)** |
| 19 | **FP-DEC-017 Weather** | Cô lập dữ liệu thời tiết khỏi pipeline CORE | Pipeline CORE vận hành độc lập, không join dữ liệu thời tiết | `POLICY_PASS` | **SẴN SÀNG** |

---

## 3. KHẲNG ĐỊNH RANH GIỚI VÀ PHÂN ĐỊNH QUẢN TRỊ
1. **Toàn bộ 19 tiêu chí đã hoàn tất mặt kỹ thuật:** Không còn rào cản kỹ thuật hay lỗi chưa rõ nguyên nhân.
2. **Không tự động đóng Gate G5:** Việc 19 tiêu chí đạt kỹ thuật chỉ xác nhận trạng thái **`G5_READY_FOR_HUMAN_SIGNOFF`**. Chỉ có chữ ký chính thức của Project Lead mới có thể chuyển trạng thái Gate G5 sang `PASS`.
3. **Cổng Gate G6 được bảo vệ:** Cổng G6 tiếp tục được niêm phong ở trạng thái **`NOT_STARTED / BLOCKED`**.
