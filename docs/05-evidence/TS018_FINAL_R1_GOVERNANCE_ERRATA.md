# TS018_FINAL_R1_GOVERNANCE_ERRATA.md
# Văn Bản Đính Chính Quản Trị Và Chuẩn Hóa Ngoại Lệ G2-EXC-001

**Dự án:** US Flight Performance Analysis 2016–2024  
**Nhiệm vụ:** TS-018 Final Evidence Integrity Review (R1 Correction)  
**Tác giả:** Project Governance, Release & Evidence Manager  
**Ngày phát hành:** 2026-10-20  
**Tình trạng pháp lý:** Đính chính quản trị có hiệu lực thi hành đối với toàn bộ hồ sơ Gate G5.

---

## 1. MỤC ĐÍCH VĂN BẢN
Đính chính định nghĩa và phạm vi áp dụng của ngoại lệ quản trị `G2-EXC-001` bị ghi chép sai lệch trong các văn bản tổng kết gần đây của AI Agent, đồng thời tái lập ma trận trạng thái quản trị chuẩn xác của toàn bộ dự án trước khi chuyển giao hồ sơ cho Project Lead.

---

## 2. NỘI DUNG ĐÍNH CHÍNH NGOẠI LỆ G2-EXC-001

### 2.1. Định nghĩa chuẩn xác của G2-EXC-001
Căn cứ quyết định `FP-DEC-012` tại [docs/02-design/DECISIONS.md](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/docs/02-design/DECISIONS.md):
- **Tên ngoại lệ:** `G2-EXC-001` (Ngoại lệ kỹ thuật có kiểm soát đối soát đơn vị đo lường 7 trường số cốt lõi).
- **Nội dung:** Cho phép thông qua cổng Gate G2 có điều kiện và **hoãn việc đối chiếu đơn vị đo lường với nguồn BTS TranStats chính thức đến Gate G5 (thông qua nhiệm vụ kiểm chứng TS-018)**.
- **Phạm vi áp dụng:** Áp dụng cho đúng 7 trường số đo nguyên bản: `ARR_DELAY`, `DEP_DELAY`, `TAXI_OUT`, `TAXI_IN`, `AIR_TIME`, `ACTUAL_ELAPSED_TIME`, `CRS_ELAPSED_TIME`.
- **Ràng buộc tiên quyết:** Bắt buộc nhiệm vụ `TS-018` phải đạt `PASS` tại Gate G5 trước khi được phép kích hoạt Gate G6 (chạy đường ống dữ liệu lớn 9 năm).
- **Trạng thái hiện tại:** **`ACTIVE`** (Đang duy trì có kiểm soát).

### 2.2. Đính chính sự nhầm lẫn với "Midnight Rollover"
- Trong báo cáo tổng kết trước đó, `G2-EXC-001` đã bị gán nhãn nhầm là ngoại lệ "Midnight Rollover".
- **Làm rõ:** 
  - Vấn đề chuyển tiếp ngày qua nửa đêm (Midnight Rollover) được điều chỉnh bởi Hợp đồng dữ liệu `DATA_CONTRACT.md` (các quy tắc `DC-08`, `DC-09`, `DC-10`) và quy định cấm tại `AGENTS.md`: *"Không suy ra ngày đến thực tế chỉ từ date component của CRS_ARR_TIME; không tự động cộng 24h để sửa rollover"*.
  - `G2-EXC-001` **không phải** là ngoại lệ Midnight Rollover. Mọi tài liệu gọi G2-EXC-001 là Midnight Rollover đều là lỗi biên soạn văn bản và được đính chính vô hiệu lực bởi tài liệu này.

---

## 3. BẢNG TỔNG HỢP TRẠNG THÁI QUẢN TRỊ CHÍNH THỨC TOÀN DỰ ÁN

| Thực thể / Cổng kiểm soát | Trạng thái kỹ thuật đạt được | Trạng thái quản trị chính thức | Thẩm quyền quyết định | Điều kiện ràng buộc |
| :--- | :---: | :---: | :---: | :--- |
| **Gate G2** | PASS | **PASS** | Project Lead (Đã duyệt) | Thông qua với ngoại lệ `G2-EXC-001`. |
| **Gate G3** | PASS | **PASS** | Project Lead (Đã duyệt) | Kiến trúc thiết kế đã chốt. |
| **Gate G4** | PASS | **PASS (CONTROLLED)** | Project Lead (Đã duyệt) | Nghiệm thu trên phân vùng Staging 2016. |
| **Task T-010** | PASS | **PASS (CONTROLLED)** | Project Lead (Đã duyệt) | Smoke test 2016 hoàn tất. |
| **Task T-011 (Technical)** | PASS | **PASS / SIGNED_OFF** | Project Lead (Đã duyệt) | Khóa ghi NTFS và KPI Engine đã hoàn tất. |
| **Task T-011 (Closeout)** | READY | **PENDING_TS018** | Project Lead | Khép hợp đồng T-011 phụ thuộc vào nghiệm thu TS-018. |
| **Ngoại lệ G2-EXC-001** | ACTIVE | **ACTIVE** | Project Lead | Giữ nguyên cho đến khi TS-018 và G5 được ký đóng. |
| **Nhiệm vụ TS-018** | READY_FOR_REVIEW | **OPEN** | **Project Lead (Chờ ký)** | 1.500 bản ghi, 10.500 so sánh khớp 100% diff == 0.0. |
| **Chính sách Option B** | PROPOSED | **FP-DEC-PROP-019** | **Project Lead (Chờ duyệt)** | Phê duyệt đối soát cấp bản ghi CSV 2019 $\leftrightarrow$ BTS. |
| **Chứng thực BTS ZIP** | VERIFIED_PHYSICALLY | **PENDING_ATTESTATION** | **Project Lead (Chờ ký)** | Xác nhận nguồn gốc tải từ BTS TranStats. |
| **Gate G5** | READY_FOR_SIGNOFF | **IN_PROGRESS** | **Project Lead (Chờ ký)** | Toàn bộ 19 nghĩa vụ kiểm thử đã đạt. |
| **Gate G6** | NOT_STARTED | **NOT_STARTED / BLOCKED** | **Project Lead (Chặn cứng)** | Tuyệt đối không mở trước khi G5 được ký đóng. |
| **Khiếm khuyết OR-05** | OPEN | **OPEN_QUALITY_DEFECT** | Project Lead | Thiếu hụt tháng 3/2024 trong tập dữ liệu thô. |
| **Khiếm khuyết OR-08** | IDENTITY_UNVERIFIED | **IDENTITY_UNVERIFIED** | Project Lead | Nhận dạng nguồn dữ liệu thượng nguồn Kaggle. |
| **Thời tiết FP-DEC-017** | CONDITIONAL_NO_GO | **CONDITIONAL_NO_GO** | Project Lead | Nhánh thời tiết không chặn tiến trình CORE. |

---

## 4. KẾT LUẬN
Bảng trạng thái trên là nguồn sự thật duy nhất về mặt quản trị của dự án tại thời điểm hiện tại. Mọi thành viên và Agent bắt buộc tuân thủ nguyên tắc không được tự ý nâng cấp trạng thái quản trị khi chưa có chữ ký chính thức của Project Lead.
