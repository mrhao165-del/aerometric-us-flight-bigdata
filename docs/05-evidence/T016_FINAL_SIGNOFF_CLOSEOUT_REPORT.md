# BÁO CÁO NGHIỆM THU KỸ THUẬT CHÍNH THỨC NHIỆM VỤ T-016
## G7 — Academic Report, Presentation & Reproducibility Handoff

- **Dự án:** Phân tích hiệu suất khai thác chuyến bay Hoa Kỳ 2016–2024 bằng Apache Spark/PySpark.
- **Cổng kiểm soát:** Gate G7 (G7 = IN_PROGRESS).
- **Mã nhiệm vụ:** T-016 (Báo cáo, Slide, Hướng dẫn chạy/Tái lập).
- **Phán quyết kỹ thuật chính thức:** `T016_OFFICIAL_CONTROLLED_SIGNOFF_PASS`.
- **Trạng thái phê duyệt:** `T-016 = PASS / COMPLETED (CONTROLLED)` (Đã được Project Lead ủy quyền ký duyệt có kiểm soát).
- **Nhiệm vụ kế tiếp:** `T-017 = NOT_STARTED / ELIGIBLE_FOR_SEPARATE_AUTHORIZATION`.
- **Thư mục xuất bản chính thức:** `D:\Flight_Audit_Exports\G7_T016_FINAL_DELIVERABLES\signoff_official`

---

## 1. TỔNG HỢP CÁC NỘI DUNG HIỆU CHỈNH & ĐÍNH CHÍNH KHOA HỌC CUỐI CÙNG

Toàn bộ các điểm hiệu chỉnh vi mô và đính chính khoa học đã được thực hiện và kiểm toán nghiêm ngặt:

1. **Hiệu chỉnh Slide 5 PowerPoint (Kiến trúc Big Data & Parquet):**
   - Loại bỏ hoàn toàn nhận định không có bằng chứng đo đạc thực nghiệm về việc Column Projection / Predicate Pushdown giảm 85% disk I/O.
   - Thay thế bằng giải thích định tính chuẩn xác về mặt kỹ thuật: cơ chế chiếu cột (column projection) chỉ nạp các cột cần thiết cho mỗi phép tính KPI và đẩy điều kiện lọc (predicate pushdown) xuống tầng lưu trữ Parquet, giảm thiểu đáng kể chi phí quét đĩa vật lý. Không đưa ra bất kỳ tỷ lệ phần trăm nào chưa qua đo đạc benchmark thực tế.
   - Xác định rõ ràng mốc thời gian 510.7 giây là benchmark hiệu năng đã được phê duyệt riêng cho tác vụ tính toán 8 CORE KPIs (T-013), không đại diện cho tổng thời gian toàn bộ quy trình đầu cuối.

2. **Hiệu chỉnh Slide 7 PowerPoint (Khung KPI & FP-DEC-016):**
   - Làm rõ quy tắc phân tầng cỡ mẫu theo quyết định `FP-DEC-016` dựa trên mẫu số hợp lệ riêng `N_valid` của từng chỉ số so với ngưỡng tối thiểu đã duyệt:
     * Cấp độ phân loại:
       - `SUPPRESSED`: khi `N_valid < N_min` (ẩn chỉ số để tránh suy diễn sai lầm).
       - `LOW_SAMPLE_CAUTION`: khi `N_min <= N_valid < 3 * N_min` (gắn nhãn cảnh báo cỡ mẫu nhỏ).
       - `SUFFICIENT`: khi `N_valid >= 3 * N_min` (độ tin cậy thống kê đầy đủ).
     * Ngưỡng tối thiểu phê duyệt chính thức: Hãng bay theo năm (`carrier-year` = 1,000 chuyến), Sân bay theo năm (`airport-year` = 365 chuyến), Tuyến bay có hướng theo năm (`directed route-year` = 100 chuyến).

3. **Hiệu chỉnh Báo cáo Học thuật (MD/DOCX) & Slide 2 PowerPoint (Động lực & Nền tảng PySpark):**
   - Loại bỏ các nhận định chủ quan cho rằng thư viện đơn nút như Pandas là hoàn toàn bất khả thi hoặc bắt buộc gặp lỗi tràn bộ nhớ (OOM).
   - Mô tả căn cứ khoa học chính xác vì sao Apache Spark / PySpark được lựa chọn: quy mô 54.7 triệu bản ghi chi tiết (34.5 GB CSV thô) đòi hỏi kiến trúc xử lý khả mở (scalable), cơ chế phân vùng dữ liệu tối ưu, lazy evaluation và quản lý bộ nhớ ngoài heap (off-heap) để đảm bảo độ tin cậy và ổn định cao trên môi trường thực tế của đồ án (Windows 11 Enterprise 64-bit, OpenJDK 21 LTS, Python 3.10).
   - Tuyệt đối không tạo dựng các con số so sánh giả định (comparative benchmark).

4. **Đối chiếu và Phân định Cấu trúc Bảng trong Báo cáo Word (DOCX Structural Reconciliation):**
   - **Thực tế cấu trúc văn bản trong tệp Word (`doc.tables`):** Gồm đúng **9 phần tử bảng**, được phân định thành 2 nhóm cấu trúc rõ ràng:
     * **7 bảng số liệu đa cột thực tế (Real Multi-Column Data Tables):** Bảng 5.1 (Sản lượng 9 năm), Bảng 5.2 (Trễ đến & phân vị), Bảng 5.3 (Hãng bay lớn), Bảng 5.4 (Đại dịch & phục hồi), Bảng 5.5 (Lăn bánh Taxi & hành trình), Phụ lục A (Sổ đăng ký 20 RES), Phụ lục B (Danh mục 16 Biểu đồ).
     * **2 hộp phương pháp luận (Methodological Callout Boxes):** Định dạng khung bảng đơn ô (1x1 table) viền trái đậm màu Navy và nền sáng.
   - **Giải trình nguồn gốc con số 16:** Phát sinh do kiểm kê cơ học ký tự `|` trong Markdown giữa 7 bảng dữ liệu và 9 dòng viền ASCII luồng xử lý 4 giai đoạn, hoặc phân biệt với 16 biểu đồ / 12 bảng phân tích T-014.

5. **Đính chính Tính nhất quán Tham số Sai số Phân vị Greenwald-Khanna (Mục 2.5):**
   - Sửa đổi phát biểu tại Mục 2.5 trong cả hai bản Markdown và DOCX: từ $\epsilon_{\text{rank}} \le 0.01$ (1%) thành công thức chuẩn tắc đồng bộ 100% với Mục 3.8 và quyết định kiến trúc `FP-DEC-015`:
     $$\epsilon_{\text{rank}} \le \frac{1}{\text{accuracy}} = \frac{1}{10000} = 0.0001 \quad (0.01\%)$$
   - Thống nhất tuyệt đối cơ sở lý thuyết sai số thứ hạng tương đối trên toàn bộ tài liệu nghiên cứu.

---

## 2. DANH MỤC CÁC SẢN PHẨM HOÀN TẤT TẠI THƯ MỤC XUẤT KHẨU
Thư mục lưu trữ: `D:\Flight_Audit_Exports\G7_T016_FINAL_DELIVERABLES\signoff_official`

| STT | Tên tệp sản phẩm | Định dạng | Kích thước / Vai trò |
|:---:|:---|:---:|:---|
| 1 | `T016_FINAL_ACADEMIC_REPORT.docx` | DOCX | Báo cáo học thuật hoàn chỉnh (Microsoft Word) đủ 80 đề mục, 7 bảng dữ liệu đa cột, 2 hộp phương pháp luận và 15 biểu đồ 300 DPI (đã đính chính Mục 2.5) |
| 2 | `T016_FINAL_ACADEMIC_REPORT.md` | MD | Nguồn văn bản Markdown chuẩn tắc đồng bộ của báo cáo học thuật (80 đề mục, ~82k ký tự, đã đính chính Mục 2.5) |
| 3 | `T016_FINAL_PRESENTATION.pptx` | PPTX | Bộ trình chiếu 16 slide khoa học (PowerPoint) đã hoàn tất micro-corrections và speaker notes |
| 4 | `T016_REPRODUCIBILITY_AND_DEMO_GUIDE.md` | MD | Hướng dẫn môi trường, lệnh tái lập và kịch bản demo 8 bước |
| 5 | `T016_CLAIM_TO_EVIDENCE_INDEX.csv` | CSV | Chỉ mục đối chiếu truy vết 20 phát hiện định lượng |
| 6 | `T016_TECHNICAL_COMPLETION_REPORT.md` | MD | Báo cáo nghiệm thu kỹ thuật và đối chiếu cấu trúc tài liệu |
| 7 | `T016_OFFICIAL_SIGNOFF_REVIEW.zip` | ZIP | Gói nén niêm phong toàn bộ 6 sản phẩm T-016 |
| 8 | `T016_OFFICIAL_SIGNOFF_REVIEW_MANIFEST.json` | JSON | Hồ sơ kiểm toán ngoại vi ghi nhận kích thước, SHA-256, CRC-32 |

---

## 3. KẾT QUẢ KIỂM TOÁN CHẤT LƯỢNG (VALIDATION CHECKS)

1. **Kiểm tra đính chính khoa học Mục 2.5:** Đã xác nhận công thức $\epsilon_{\text{rank}} \le 1/10000 = 0.0001 = 0.01\%$ khớp chính xác giữa Mục 2.5, Mục 3.8 và quyết định `FP-DEC-015` trong cả Markdown và Word DOCX.
2. **Kiểm tra 4 điểm hiệu chỉnh vi mô trước:** Cả 4 điểm về Slide 5, Slide 7, Slide 2/Báo cáo và cấu trúc bảng DOCX được bảo toàn hoàn hảo.
3. **Kiểm tra tính nhất quán giữa DOCX và Markdown:** Đủ 80/80 đề mục (Heading 0..3), 437 khối văn bản, 15 biểu đồ 300 DPI, nội dung các đoạn văn bản sửa đổi hoàn toàn đồng nhất.
4. **Kiểm tra kết xuất bộ trình chiếu PowerPoint:** Slides 2, 5 và 7 hiển thị chuẩn mực; tổng số slide duy trì chính xác **16 slides**.
5. **Kiểm tra khả năng mở và đọc của 6 tệp bàn giao:** Toàn bộ 6 tệp thành viên được kiểm tra mở và đọc thành công, cấu trúc định dạng nguyên vẹn.
6. **Kiểm tra gói nén và mã băm SHA-256 / CRC-32:** Tệp nén giải nén thử nghiệm thành công 6/6 tệp, mã băm khớp chính xác 100% với manifest kiểm toán ngoại vi.
7. **Bảo tồn bất biến dữ liệu sản xuất & các gói lưu trữ trước:** Các gói lưu trữ tại thư mục cha, `corrected/`, và `signoff_final/` được bảo tồn nguyên vẹn không can thiệp.

---

## 4. KẾT LUẬN & GHI NHẬN TRẠNG THÁI QUẢN TRỊ
- Nhiệm vụ T-016 đã hoàn tất toàn diện mọi yêu cầu kỹ thuật và hiệu chỉnh tài liệu khoa học.
- Ghi nhận chính thức theo ủy quyền của Project Lead:
  * `T-016 = PASS / COMPLETED (CONTROLLED)`
  * `G7 = IN_PROGRESS`
  * `T-017 = NOT_STARTED / ELIGIBLE_FOR_SEPARATE_AUTHORIZATION`
  * `G6 = PASS / CLOSED (CONTROLLED)` *(Bảo tồn)*
  * `D5 = NOT_AUTHORIZED / FAIL-CLOSED` *(Bảo tồn)*
  * `T-015 = CONDITIONAL_NO_GO` *(Bảo tồn)*