# G6_T012_FINAL_R1_OPERATIONAL_GAP_REVIEW.md
# Đánh Giá Khoảng Cách Vận Hành Kế Hoạch Triển Khai Gate G6 / Task T-012

**Dự án:** US Flight Performance Analysis 2016–2024  
**Nhiệm vụ:** Gate G6 Operational Readiness Gap Analysis (TS-018 R1 Correction)  
**Tác giả:** Principal Big Data Engineer, Systems Concurrency & Storage Specialist  
**Ngày lập:** 2026-10-20  
**Phạm vi:** Rà soát kỹ thuật trước khi chuyển giao kế hoạch vận hành cho Project Lead; **KHÔNG THỰC THI G6**.

---

## 1. MỤC TIÊU VÀ NGUYÊN TẮC
Kế hoạch vận hành Task T-012 (xử lý toàn bộ 9 năm dữ liệu 2016–2024) được thiết lập tại Gate G5 nhằm chuẩn bị trước cho Gate G6. Tài liệu này đánh giá tính khả thi và khoảng cách (gap) giữa thiết kế kế hoạch và mã nguồn hiện thực tế, bảo đảm không gây ngộ nhận về mức độ sẵn sàng khi bước vào G6.

---

## 2. BẢNG ĐỐI SOÁT KHOẢNG CÁCH TRIỂN KHAI (IMPLEMENTATION VS EXECUTION GAP MATRIX)

| Hạng mục vận hành | Mô tả trong tài liệu kế hoạch G6 | Hiện trạng mã nguồn thực tế | Đánh giá khoảng cách (Gap) | Biện pháp kiểm soát bắt buộc |
| :--- | :--- | :--- | :---: | :--- |
| **Công cụ kiểm tra con trỏ Staging** | Tham chiếu `tools/qa/verify_staging_pointer.py` | Tệp chưa được triển khai độc lập; logic hiện nằm trong `SingleWriterLock` và `run_t010_real_data_smoke.py`. | **GAP — UNIMPLEMENTED_TOOL** | Đánh dấu rõ là công cụ dự kiến; dùng hàm kiểm tra có sẵn trong module `locking.py` và `test_t010_policy_guards.py`. |
| **Quy trình dọn dẹp thư mục tạm & xóa marker recovery** | Xóa thư mục `.tmp_*` và gỡ bỏ recovery marker khi có sự cố | Yêu cầu phải kiểm chứng không còn writer hoạt động (`is_locked() == False`) theo `FP-DEC-018`. | **CRITICAL_SAFETY_CONSTRAINT** | Cấm xóa marker thủ công nếu chưa chạy kiểm tra quyền sở hữu tiến trình khóa. |
| **Ước tính thời gian chạy 9 năm** | Dự báo 49,5 – 60 phút | Ngoại suy từ 1 năm dữ liệu 2016 tại T-010 (mỗi năm ~5,5 phút); chưa tính độ trễ I/O GC dồn tích trên 9 năm. | **ESTIMATION_LIMITATION** | Không cam kết hoàn tất trong 60 phút; thời gian thực tế có thể dao động 75–120 phút trên máy trạm cục bộ. |
| **Đo lường dung lượng đĩa Drive D:** | Ghi nhận 59,47 GB | Đo thực tế tại phiên R1 (2026-10-20): **59,46 GiB** ($63.848.439.808$ bytes). | **VERIFIED_CURRENT** | Đo lường lại ngay trước khi bấm nút khởi chạy từng năm trong G6. |
| **Xử lý phân vùng năm 2016** | Tái sử dụng Staging 2016 có sẵn | 50 tệp Parquet 2016 hiện tại là baseline kiểm thử khép kín của T-010 (dấu vân tay `b5805fca...`). | **GOVERNANCE_SEPARATION** | Phân biệt rõ baseline T-010 bất biến với phân vùng xuất bản chính thức của G6. Không ghi đè baseline 2016. |

---

## 3. TÍNH TOÁN NGÂN SÁCH TÀI NGUYÊN (RESOURCE BUDGET)

- **Dung lượng đĩa Drive D hiện có:** **59,46 GiB** ($63,85$ GB khả dụng).
- **Phân bổ ngân sách dự kiến cho T-012 full-run:**
  1. *Parquet Staging (nén Snappy, tỷ lệ thực tế đo tại T-010 là 4,48x):* $\approx 3,16$ GB.
  2. *Bảng KPI xuất bản chính thức (Parquet):* $\approx 0,80$ GB.
  3. *Tệp chất lượng & nhật ký QA witness:* $\approx 0,50$ GB.
  4. *Bộ đệm xáo trộn (Shuffle buffer) và phân vùng tạm thời tối đa:* $\approx 10,00$ GB.
  5. *Dự phòng lưu giữ phiên bản (Version retention buffer):* $\approx 5,00$ GB.
- **Tổng ngân sách đĩa cần thiết tối đa:** $\approx \mathbf{19,46\text{ GB}}$.
- **Dung lượng an toàn còn lại sau full-run:** $\approx 44,39\text{ GB}$.
- **Hệ số an toàn (Safety Margin):** **$3,28\times$** ngân sách tối đa; đáp ứng vượt trội quy tắc an toàn lưu trữ trên hệ thống tệp Windows NTFS.

---

## 4. ĐIỀU KIỆN RÀNG BUỘC TRƯỚC KHI KHỞI CHẠY G6
Tuyệt đối không được kích hoạt pipeline T-012 chín năm khi chưa hội đủ các điều kiện sau:
1. Project Lead đã hoàn tất ký nghiệm thu TS-018 và ký đóng Gate G5.
2. Quyết định mở Gate G6 đã được ban hành chính thức.
3. Kỹ sư vận hành đã rà soát bảng danh mục kiểm tra an toàn [G6_T012_EXECUTION_CHECKLIST.md](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/docs/05-evidence/G6_T012_EXECUTION_CHECKLIST.md).
4. Các công cụ chưa triển khai (như `verify_staging_pointer.py`) phải được thay thế bằng lệnh kiểm tra programmatic trực tiếp từ `SingleWriterLock`.
