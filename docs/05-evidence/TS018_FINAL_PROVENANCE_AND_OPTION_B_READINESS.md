# TS018_FINAL_PROVENANCE_AND_OPTION_B_READINESS.md
# Báo Cáo Sẵn Sàng Nghiệm Thu Option B Và Nguồn Gốc BTS Cho TS-018

**Dự án:** US Flight Performance Analysis 2016–2024  
**Nhiệm vụ:** TS-018 — Final Verifier Hardening & Controlled Signoff Readiness  
**Tác giả:** Principal Big Data QA Engineer, Independent Forensic Evidence Auditor  
**Thời điểm lập:** 2026-10-20  
**Thẩm quyền:** Báo cáo kiểm định độc lập phục vụ Project Lead; không tự ký nghiệm thu.

---

## 1. MỤC TIÊU VÀ NGUYÊN TẮC
Tài liệu này tổng hợp đối soát mức độ sẵn sàng phê duyệt của đề xuất chính sách **FP-DEC-019 (Option B)**, làm rõ bằng chứng nguồn gốc xuất xứ của tệp BTS đối chuẩn, và tách bạch nghiêm ngặt 5 quyết định phê duyệt độc lập của con người.

---

## 2. PHÂN BIỆT RÕ RÀNG NĂM QUYẾT ĐỊNH ĐỘC LẬP CỦA CON NGƯỜI
Trong quy trình quản trị dự án nghiêm ngặt, 5 quyết định sau là hoàn toàn độc lập và phải được Project Lead xem xét riêng biệt, không được gộp hoặc tự động suy diễn quyết định này từ quyết định kia:

1. **Quyết định 1 — Xác nhận nguồn BTS (BTS Provenance Attestation):**
   - *Căn cứ:* Biên bản tải về thực tế từ cổng TranStats của BTS Hoa Kỳ, nhật ký hash SHA-256 (`342de99f65561fb856b524c704f2ad3851f8015f52251668ece346dff1350ae6`), dung lượng 29.975.383 bytes và xác nhận bằng văn bản của người thực hiện tải tệp.
   - *Trạng thái:* **SẴN SÀNG TRÌNH DUYỆT (READY FOR HUMAN ATTESTATION)**.
2. **Quyết định 2 — Phê duyệt chính sách FP-DEC-019 (Option B Approval):**
   - *Nội dung:* Chấp thuận sử dụng đối soát trực tiếp giữa tệp CSV thô năm 2019 (`flight_with_weather_2019.csv`) và tệp BTS chính thức tháng 1/2019 để thỏa mãn yêu cầu kiểm chứng đơn vị (unit verification) của TS-018 trong phạm vi Gate G5.
   - *Trạng thái:* **ĐỀ XUẤT CHÍNH THỨC (PROPOSED — AWAITING PROJECT LEAD DECISION)**.
3. **Quyết định 3 — Nghiệm thu kỹ thuật TS-018 (TS-018 Human Technical Acceptance):**
   - *Nội dung:* Công nhận kết quả kiểm chứng kỹ thuật số đo 7 trường trên 1.500 bản ghi mẫu đạt 100% khớp bitwise IEEE-754 với mức dung sai nghiêm ngặt (`TOLERANCE = 0.0`), zero mismatch, zero duplicate keys.
   - *Trạng thái:* **SẴN SÀNG NGHIỆM THU (READY FOR TECHNICAL ACCEPTANCE)**.
4. **Quyết định 4 — Ký đóng Gate G5 (G5 Human Gate Signoff):**
   - *Nội dung:* Đánh giá tổng thể 19 tiêu chí hoàn thành của G5, bao gồm T-010 (PASS CONTROLLED), T-011 (SIGNED_OFF), TS-018, các rủi ro tồn đọng có kiểm soát và ngoại lệ active `G2-EXC-001`.
   - *Trạng thái:* **CHỜ KÝ ĐÓNG THEO ĐIỀU KIỆN (PENDING G5 CLOSEOUT REVIEW)**.
5. **Quyết định 5 — Cấp phép khởi động Gate G6 (G6 Entry Authorization):**
   - *Nội dung:* Quyết định cấp phép chạy pipeline 9 năm T-012 sau khi đã đóng G5, kiểm tra năng lực đĩa và chuẩn bị quy trình rollback. Việc đóng G5 **không** tự động đồng nghĩa với việc G6 được tự động kích hoạt.
   - *Trạng thái:* **CHƯA MỞ / BỊ CHẶN (NOT_STARTED / BLOCKED)**.

---

## 3. PHẠM VI CHÍNH SÁCH FP-DEC-019 (OPTION B) VÀ CĂN CỨ KỸ THUẬT
- **Bối cảnh:** Tại Gate G5, chỉ có dữ liệu năm 2016 được nạp vào Staging Parquet (theo phạm vi T-010). Dữ liệu 8 năm còn lại (2017–2024) chưa được nạp vào Staging Parquet cho đến khi Gate G6 thực thi. Do đó, việc đối soát năm 2019 giữa Staging Parquet và BTS là bất khả thi về mặt vật lý tại G5 mà không vi phạm ranh giới gate.
- **Nội dung Option B:** Thực hiện đối soát trực tiếp 7 trường số đo cốt lõi giữa **CSV dữ liệu thô dự án năm 2019** (`data/raw/tabular/2019/flight_with_weather_2019.csv`) và **tệp tham chiếu BTS gốc** (`T_ONTIME_REPORTING_20261019_112232.zip`).
- **Nhãn kỹ thuật chuẩn tắc:** Bằng chứng được định danh chính xác là:
  `2019_RAW_SOURCE_VS_BTS` (tuyệt đối không dùng nhãn `2019_PARQUET_PARITY`).
- **Kết quả đối soát thực nghiệm:** 1.500 chuyến bay phân tầng ngẫu nhiên được kiểm tra, toàn bộ 10.500 so sánh đạt trùng khớp bitwise IEEE-754 tuyệt đối (`diff == 0.000000`), không có sai lệch dung sai (`tol_only == 0`), không có signed zero (`+0.0` vs `-0.0`), không có lỗi null-null hay token không hợp lệ.

---

## 4. GIỚI HẠN VÀ KHUYẾN CÁO VỀ NGUỒN GỐC DỮ LIỆU (PROVENANCE LIMITATIONS)
Để đảm bảo tính trung thực khoa học, nhóm kỹ sư tuyên bố rõ các ranh giới:
1. **Không khái quát hóa quá mức:** Việc 1.500 chuyến bay tháng 1/2019 trong CSV thô khớp chính xác 100% với BTS TranStats chứng minh tính xác thực số đo cục bộ của tập dữ liệu năm 2019, nhưng **không cấu thành bằng chứng toán học hay pháp lý** rằng toàn bộ 54,7 triệu hàng trên Kaggle (2016–2024) có chuỗi cung ứng chính thức từ BTS.
2. **PARQUET_PARITY_NOT_TESTED:** Tính toàn vẹn của mã hóa Parquet cho năm 2019 chưa được kiểm thử (do dữ liệu 2019 chưa nạp Parquet).
3. **OR-08 giữ nguyên trạng thái:** Rủi ro `OR-08` (nguồn gốc dữ liệu Kaggle thượng nguồn chưa được nhà cung cấp xác thực chuỗi bàn giao) duy trì ở mức `IDENTITY_UNVERIFIED`.
4. **OR-05 giữ nguyên khiếm khuyết:** Tệp thô năm 2024 bị khuyết dữ liệu tháng 3/2024 (`OPEN_QUALITY_DEFECT`).
5. **Thời tiết FP-DEC-017:** Dữ liệu thời tiết duy trì trạng thái `CONDITIONAL_NO_GO`.

---

## 5. KẾT LUẬN VÀ KHUYẾN NGHỊ
Hồ sơ kỹ thuật cho TS-018 đã hoàn thiện ở mức tối đa, loại bỏ hoàn toàn các rủi ro bỏ sót lỗi (false-PASS). Hồ sơ sẵn sàng để **Project Lead** xem xét và phê duyệt:
- Đề xuất: Project Lead xem xét phê duyệt **FP-DEC-019 (Option B)** và ký biên bản nghiệm thu kỹ thuật **TS-018**.
