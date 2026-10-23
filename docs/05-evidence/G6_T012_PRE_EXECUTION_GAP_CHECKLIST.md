# G6_T012_PRE_EXECUTION_GAP_CHECKLIST.md
# Danh Mục Kiểm Tra Khoảng Cách Và Sẵn Sàng Vận Hành Gate G6 / Task T-012

**Dự án:** US Flight Performance Analysis 2016–2024  
**Nhiệm vụ:** Gate G6 Pre-Execution Gap Audit & Safety Checklist  
**Tác giả:** Principal Big Data Engineer, Systems Concurrency & Windows NTFS Storage Specialist  
**Thời điểm lập:** 2026-10-20  
**Thẩm quyền:** Báo cáo kiểm định kỹ thuật độc lập; **TUYỆT ĐỐI KHÔNG CHẠY T-012 TRONG GIAI ĐOẠN NÀY**.

---

## 1. MỤC TIÊU VÀ NGUYÊN TẮC
Tài liệu này xác minh các điều kiện tiên quyết về tài nguyên hạ tầng, sự toàn vẹn của dữ liệu và các khoảng cách vận hành (operational gaps) cần xử lý trước khi kích hoạt Task T-012 (nạp toàn bộ 9 năm 2016–2024 vào Staging Parquet).
Mọi phát biểu về tài nguyên đều được đo lường thực tế tại thời điểm lập báo cáo, không sử dụng số liệu giả lập hay snapshot cũ.

---

## 2. BẢNG KIỂM TRA ĐIỀU KIỆN TIÊN QUYẾT HẠ TẦNG & DỮ LIỆU

| Hạng mục kiểm tra | Hiện trạng thực tế đo lường (2026-10-20) | Ngưỡng an toàn tối thiểu | Đánh giá kỹ thuật |
| :--- | :--- | :--- | :---: |
| **Tính toàn vẹn 9 tệp RAW CSV** | Cả 9 tệp CSV (2016–2024) tồn tại đầy đủ tại `data/raw/tabular/`, kích thước từ 1.19 GB đến 1.99 GB, tổng dung lượng: $\approx 15.2$ GB. Mã băm SHA-256 khớp danh mục. | 9 tệp CSV bất biến | **PASS (VERIFIED)** |
| **50 tệp Parquet Staging 2016** | 50 tệp Parquet tại `D:\Study\Code\Apache\Flight_Analyzt\staging\` (thuộc 2 lần chạy T-010) còn nguyên vẹn, mã băm khớp manifest niêm phong. | Không bị sửa đổi / xóa | **PASS (VERIFIED)** |
| **Dung lượng đĩa Drive D:** | **59,44 GiB khả dụng** ($63.821.283.328$ bytes). Tổng dung lượng ổ: 300.00 GiB. | Tối thiểu 30 GB khả dụng | **PASS (MARGIN = 3.28x)** |
| **Cấu hình Spark & RAM** | Spark 3.5.x, Driver RAM 4GB, Executor RAM 4GB, ANSI mode ON. Tiêu thụ thực tế đo tại T-010: đỉnh 3.2 GB RAM JVM. | Workstation 16GB+ RAM | **PASS** |
| **Cơ chế khóa & phục hồi** | `SingleWriterLock` tuân thủ `FP-DEC-018`: kiểm soát quyền sở hữu qua PID/Timestamp/fstat, chống ghi đè khi tiến trình còn sống. | Tuân thủ FP-DEC-018 | **PASS** |
| **Tính bất biến của baseline 2016** | Toàn bộ output của G6 sẽ được ghi vào các thư mục phân vùng mới có run-id hoặc partition riêng, không tác động vào thư mục baseline T-010. | Zero mutation baseline | **PASS** |

---

## 3. RÀ SOÁT KHOẢNG CÁCH VẬN HÀNH (OPERATIONAL GAPS) VÀ BIỆN PHÁP XỬ LÝ

| Mã Gap | Nội dung khoảng cách | Mô tả chi tiết | Biện pháp xử lý bắt buộc trước khi chạy G6 |
| :---: | :--- | :--- | :--- |
| **GAP-01** | `tools/qa/verify_staging_pointer.py` chưa triển khai độc lập | Tài liệu vận hành có đề cập script kiểm tra con trỏ staging độc lập, nhưng thực tế file này chưa được tạo riêng rẽ; logic hiện nằm trong `SingleWriterLock` và `test_t010_policy_guards.py`. | **Xử lý trước G6:** Kỹ sư vận hành sẽ tạo công cụ độc lập `verify_staging_pointer.py` hoặc sử dụng hàm kiểm tra programmatic tích hợp sẵn trong `SingleWriterLock.verify_pointer_integrity()` trước khi chuyển giao. |
| **GAP-02** | Xóa temp & recovery marker khi có sự cố | Hướng dẫn sơ khởi có đoạn đề xuất xóa folder tạm `.tmp_*` thủ công. Điều này vi phạm `FP-DEC-018` nếu writer khác đang giữ khóa. | **Quy tắc an toàn tuyệt đối:** Cấm xóa marker hoặc dọn dẹp `.tmp` thủ công nếu chưa kiểm chứng `is_locked() == False` và quyền sở hữu tiến trình đã hết hạn. |
| **GAP-03** | Cam kết thời gian chạy 9 năm | Ước tính trước đây ghi 49.5–60 phút là phép ngoại suy tuyến tính từ 1 năm 2016 (5.5 phút/năm), chưa tính độ trễ tích lũy I/O và Garbage Collection JVM khi xử lý 9 năm liên tục. | **Điều chỉnh ước tính:** Thời gian thực tế dự kiến dao động trong khoảng **75 – 120 phút**. Không cam kết mốc 60 phút. |
| **GAP-04** | Điểm dừng (STOP) và điều kiện Rollback từng năm | Full-run 9 năm không được chạy dạng batch một lượt không kiểm soát. | **Thiết kế từng năm (Per-Year Execution):** Chạy tuần tự từng năm ($2016 \rightarrow 2024$). Sau mỗi năm, tiến hành kiểm tra row count, DC-11/12 hạch toán 3 trạng thái. Nếu 1 năm thất bại, rollback năm đó về trạng thái trước và **DỪNG TOÀN BỘ (FAIL-STOP)**. |

---

## 4. BẢNG DỰ TOÁN NGÂN SÁCH DUNG LƯỢNG ĐĨA CHO T-012 FULL-RUN

- Dung lượng đĩa trống Drive D đo thực tế: **59,44 GiB** ($63,82$ GB).
- Dự toán tiêu thụ tối đa cho full 9 năm:
  1. Parquet Staging (54,7 triệu dòng nén Snappy, tỷ lệ nén đo tại T-010 là 4.48x): $\approx 3,16$ GB.
  2. Bảng KPI xuất bản Parquet: $\approx 0,80$ GB.
  3. Bảng chất lượng & logs witness: $\approx 0,50$ GB.
  4. Shuffle spill buffer & temporary workdir: $\approx 10,00$ GB.
  5. Dự phòng versioning & rollback buffer: $\approx 5,00$ GB.
- **Tổng ngân sách đĩa tối đa:** $\approx \mathbf{19,46\text{ GB}}$.
- **Dung lượng đĩa an toàn còn lại sau chạy:** $\approx 44,36\text{ GB}$.
- **Hệ số an toàn (Safety Margin):** **$3,28\times$** ngân sách tối đa.

---

## 5. KẾT LUẬN VỀ TRẠNG THÁI GATE G6
1. Hạ tầng đĩa và bộ nhớ hoàn toàn sẵn sàng cho Task T-012.
2. Các khoảng cách vận hành (GAP-01 đến GAP-04) đã được nhận diện minh bạch và có phương án kiểm soát chặt chẽ.
3. **Cổng Gate G6 vẫn giữ nguyên trạng thái `NOT_STARTED / BLOCKED`** cho đến khi Project Lead hoàn tất phê duyệt Option B, nghiệm thu TS-018 và ký đóng Gate G5.
