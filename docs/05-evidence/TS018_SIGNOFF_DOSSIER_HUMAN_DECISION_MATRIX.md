# TS018_SIGNOFF_DOSSIER_HUMAN_DECISION_MATRIX.md
# Ma Trận Năm Quyết Định Độc Lập Trình Project Lead Phê Duyệt

**Dự án:** US Flight Performance Analysis 2016–2024  
**Nhiệm vụ:** TS-018 Final Signoff Dossier Reconciliation (Phase D)  
**Tác giả:** Project Governance Release Reviewer, Independent Evidence Auditor  
**Thời điểm lập:** 2026-10-20  
**Thẩm quyền:** Báo cáo kiểm định độc lập phục vụ Project Lead; **thẩm quyền ký phê duyệt thuộc độc quyền của Project Lead**.

---

## 1. NGUYÊN TẮC TÁCH BẠCH QUẢN TRỊ
Để tuân thủ nghiêm ngặt chính sách `AGENTS.md` và ngăn chặn việc ngộ nhận hoặc gộp quyền, năm quyết định sau đây là hoàn toàn độc lập. Việc phê duyệt một quyết định **không đồng nghĩa và không tự động kéo theo** việc các quyết định khác được thông qua đồng thời.

---

## 2. MA TRẬN NĂM QUYẾT ĐỊNH ĐỘC LẬP (DECISION MATRIX D1 – D5)

| Mã Quyết Định | Tên quyết định | Căn cứ thẩm định & Bằng chứng kỹ thuật | Trạng thái kỹ thuật đề xuất | Thẩm quyền phê duyệt | Ranh giới & Ràng buộc bảo lưu |
| :---: | :--- | :--- | :---: | :---: | :--- |
| **D1** | **Xác Nhận Nguồn Gốc BTS (BTS Provenance Attestation)** | Tệp `T_ONTIME_REPORTING_20261019_112232.zip` (SHA-256: `342de99...`), biên bản tải về từ cổng TranStats của BTS Hoa Kỳ và chứng thực của người thực hiện tải tệp. | **READY_FOR_ATTESTATION** | **Project Lead / Người thực hiện tải** | Agent không tự chứng thực thay người tải; chỉ xác nhận tính toàn vẹn mật mã học của tệp lưu trữ. |
| **D2** | **Phê Duyệt Chính Sách FP-DEC-019 (Option B Approval)** | Báo cáo kiểm chứng kỹ thuật: Staging Parquet 2019 chưa nạp tại G5 (tuân thủ ranh giới T-010); đối soát trực tiếp CSV thô 2019 $\leftrightarrow$ BTS đạt $100\%$ bitwise exact. | **PROPOSED_FOR_APPROVAL** | **Project Lead** | Giữ nguyên ranh giới **`PARQUET_PARITY_NOT_TESTED`**; không mở rộng ra tính chẵn lẻ của Parquet 2019. |
| **D3** | **Nghiệm Thu Kỹ Thuật TS-018 (TS-018 Technical Signoff)** | Bằng chứng 10.500/10.500 phép so sánh bitwise exact trên 1.500 bản ghi phân tầng, $0$ duplicate keys, $14/14$ negative tests fail-closed, khép các điểm yếu E01–E05. | **RECOMMENDED_FOR_SIGNOFF** | **Project Lead** | Nhãn kỹ thuật duy nhất: `2019_RAW_SOURCE_VS_BTS`. Ngoại lệ `G2-EXC-001` chuyển từ `ACTIVE` sang `RESOLVED_BY_OPTION_B` khi được ký. |
| **D4** | **Ký Đóng Gate G5 (G5 Human Gate Signoff)** | Hoàn tất 19/19 tiêu chí kỹ thuật G5 (T-010 Bounded Smoke, T-011 KPI Engine, SingleWriterLock crash recovery, TS-018 Option B candidate). | **READY_FOR_G5_CLOSEOUT_REVIEW** | **Project Lead** | Phân định rõ `TECHNICAL_PASS` với chấp nhận rủi ro có kiểm soát (`OR-08`, `OR-05`). Không tự động mở Gate G6. |
| **D5** | **Cấp Phép Khởi Động Gate G6 (G6 / T-012 Authorization)** | Báo cáo sẵn sàng tài nguyên: Đĩa Drive D trống **59,44 GiB** (hệ số an toàn $3,28\times$), kế hoạch phân vùng từng năm, cơ chế khóa FP-DEC-018, quy trình rollback. | **BLOCKED — AWAITING EXPLICIT ORDER** | **Project Lead** | Cổng G6 duy trì trạng thái **`BLOCKED`** cho đến khi có lệnh bằng văn bản riêng biệt từ Project Lead. Tuyệt đối không chạy T-012. |

---

## 3. CÁC RỦI RO TỒN ĐỌNG VÀ NGOẠI LỆ ĐƯỢC BẢO LƯU

1. **Rủi ro thượng nguồn OR-08 (IDENTITY_UNVERIFIED):**
   - Sự trùng khớp số đo của mẫu 1.500 chuyến bay năm 2019 chứng minh tính chính xác nội dung của tệp CSV 2019, nhưng **không chứng minh toàn bộ 9 năm trên Kaggle có chuỗi bàn giao chính thức từ BTS**. Rủi ro này tiếp tục được duy trì dưới dạng ngoại lệ có kiểm soát.
2. **Khiếm khuyết dữ liệu OR-05 (Thiếu tháng 3/2024):**
   - Tệp dữ liệu thô năm 2024 bị mất hoàn toàn tháng 3/2024 từ nhà cung cấp. Trạng thái: `OPEN_QUALITY_DEFECT`.
3. **Chính sách thời tiết FP-DEC-017:**
   - Dữ liệu thời tiết duy trì trạng thái `CONDITIONAL_NO_GO`; pipeline CORE tiếp tục cô lập hoàn toàn không join thời tiết.
4. **Ngoại lệ G2-EXC-001:**
   - Tiếp tục duy trì `ACTIVE` cho đến thời điểm Project Lead chính thức ký văn bản phê duyệt D2 và D3.
5. **Tính bất biến của T-011:**
   - Toàn bộ việc triển khai kỹ thuật của T-011 (KPI Engine, cơ chế khóa SafePublisher, SingleWriterLock) đã được nghiệm thu tại phiên signoff kiểm soát ngày 2026-10-19 và được giữ nguyên vẹn, không mở lại.
