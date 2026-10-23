# BIÊN BẢN KÝ DUYỆT CHÍNH THỨC CÓ KIỂM SOÁT NHIỆM VỤ T-016
## Cổng kiểm soát G7: Báo cáo Học thuật, Bộ Trình chiếu & Hướng dẫn Tái lập

- **Dự án:** Phân tích hiệu suất khai thác chuyến bay nội địa Hoa Kỳ giai đoạn 2016–2024 bằng Apache Spark/PySpark.
- **Cổng kiểm soát:** Gate G7 (G7 = IN_PROGRESS).
- **Nhiệm vụ:** T-016 (Báo cáo học thuật, Slide, Hướng dẫn chạy/Tái lập).
- **Căn cứ ủy quyền:** Chỉ thị trực tiếp của Project Lead (`T-016 — FINAL ONE-LINE ERRATUM & OFFICIAL CONTROLLED SIGNOFF`).
- **Phán quyết nghiệm thu chính thức:** `T016_OFFICIAL_CONTROLLED_SIGNOFF_PASS`.
- **Trạng thái phê duyệt:** `T-016 = PASS / COMPLETED (CONTROLLED)`.
- **Trạng thái cổng kiểm soát:** `G7 = IN_PROGRESS`.
- **Nhiệm vụ kế tiếp:** `T-017 = NOT_STARTED / ELIGIBLE_FOR_SEPARATE_AUTHORIZATION`.
- **Ngày ban hành:** 2026-10-22.

---

## 1. TUYÊN BỐ PHÊ DUYỆT CỦA PROJECT LEAD

Căn cứ vào thẩm quyền và chỉ thị kiểm soát chất lượng khoa học:
1. Xác nhận gói sản phẩm ký duyệt `T-016` đã vượt qua 100% các phép kiểm toán vật lý, kiểm tra tính toàn vẹn gói nén ZIP và mã băm manifest ngoại vi.
2. Xác nhận điểm không nhất quán khoa học cuối cùng tại Mục 2.5 của Báo cáo học thuật đã được đính chính hoàn toàn: công thức sai số thứ hạng tương đối của thuật toán Spark Greenwald-Khanna GK-sketch với tham số `accuracy=10000` theo quyết định kiến trúc `FP-DEC-015` được chuẩn hóa thành:
   $$\epsilon_{\text{rank}} \le \frac{1}{\text{accuracy}} = \frac{1}{10000} = 0.0001 \quad (0.01\%)$$
   thống nhất tuyệt đối giữa Mục 2.5, Mục 3.8 và quyết định đã duyệt `FP-DEC-015`.
3. Xác nhận toàn bộ 4 nội dung hiệu chỉnh vi mô trước đó được bảo toàn nguyên vẹn:
   - Slide 5: Giải thích định tính về Parquet Column Projection & Predicate Pushdown; xác định rõ 510.7s là benchmark của T-013 CORE KPI.
   - Slide 7: Quy tắc phân tầng cỡ mẫu FP-DEC-016 dựa trên mẫu số hợp lệ riêng $N_{\text{valid}}$ cho từng chỉ số và 3 cấp độ (SUPPRESSED, LOW_SAMPLE_CAUTION, SUFFICIENT).
   - Slide 2 & Báo cáo: Lý do khoa học lựa chọn nền tảng PySpark khả mở cho 54.7M dòng dữ liệu trên phần cứng thực tế (Windows 11, OpenJDK 21 LTS, Python 3.10), loại bỏ các tuyên bố chủ quan về Pandas OOM.
   - Báo cáo Nghiệm thu: Đối chiếu thực tế 9 cấu trúc bảng trong Word (7 bảng số liệu đa cột thực tế + 2 hộp phương pháp luận 1x1).
4. Chính thức ghi nhận:
   - **`T-016 = PASS / COMPLETED (CONTROLLED)`**
   - **`G7 = IN_PROGRESS`**
   - **`T-017 = NOT_STARTED / ELIGIBLE_FOR_SEPARATE_AUTHORIZATION`**
5. Bảo lưu nguyên vẹn:
   - `G6 = PASS / CLOSED (CONTROLLED)`
   - `D5 = NOT_AUTHORIZED / FAIL-CLOSED`
   - `T-015 = CONDITIONAL_NO_GO`

---

## 2. DANH MỤC SẢN PHẨM NIÊM PHONG CHÍNH THỨC TẠI `signoff_official/`

Thư mục lưu trữ chính thức: `D:\Flight_Audit_Exports\G7_T016_FINAL_DELIVERABLES\signoff_official\`

| STT | Tên tệp sản phẩm | Định dạng | Kích thước (bytes) | SHA-256 | CRC-32 |
|:---:|:---|:---:|:---:|:---:|:---:|
| 1 | `T016_FINAL_ACADEMIC_REPORT.docx` | DOCX | 3,214,033 | `b40675bf1040c8a33a78124b58c27736c5807e9f19d80934f99695d7287ddd0d` | `68c9f6e7` |
| 2 | `T016_FINAL_ACADEMIC_REPORT.md` | MD | 99,505 | `59e9d696961094b3a04f305b05f2f515407b799422978e3d9b06ac4e9a86ff72` | `3eb0b8f2` |
| 3 | `T016_FINAL_PRESENTATION.pptx` | PPTX | 1,240,546 | `f5f06dc08eb135a3d05f0217290ef82815020c453c878fc7c9b224ffc1203d4c` | `1d290783` |
| 4 | `T016_REPRODUCIBILITY_AND_DEMO_GUIDE.md` | MD | 9,444 | `9e28cecd0816e15918e48926221107e735aff8ecd0a5be689b25e2daa9734f05` | `2f12b001` |
| 5 | `T016_CLAIM_TO_EVIDENCE_INDEX.csv` | CSV | 5,928 | `5016bbd8246ebcdcfd164b85fb11dbb81aed89cb0f9d008bf603cb1093eef313` | `3d91167a` |
| 6 | `T016_TECHNICAL_COMPLETION_REPORT.md` | MD | 9,082 | `7b3b8676e8e7ee470ffc2f2696847f09c6ed73ce88670b953da62250ae91266d` | `a1c6c8b3` |
| **7** | **Gói nén niêm phong:** `T016_OFFICIAL_SIGNOFF_REVIEW.zip` | ZIP | **4,480,255** | `7d9d046df7f2156fd9a50a84b38d23308f67186c33cbc6cc20f740dc59770b55` | `5785dfc6` |
| **8** | **Manifest kiểm toán ngoại vi:** `T016_OFFICIAL_SIGNOFF_REVIEW_MANIFEST.json` | JSON | 2,008 | `2da5405bbe1bd4714baa84c216022cb0f08240f2a62a7dadd055f669d2911d6b` | — |

*(Bản sao đồng nhất `T016_FINAL_SIGNOFF_REVIEW.zip` và `T016_FINAL_SIGNOFF_REVIEW_MANIFEST.json` được duy trì song song tại thư mục trên để bảo đảm tính tương thích tối đa).*

---

## 3. BẢO TỒN NGUYÊN VẸN CÁC GÓI LƯU TRỮ LỊCH SỬ

Các gói lưu trữ trước đây được bảo tồn bất biến:
1. `D:\Flight_Audit_Exports\G7_T016_FINAL_DELIVERABLES\corrected\T016_CORRECTED_REVIEW.zip`:
   - SHA-256: `9df74b5029abe3a7cb6a585f5fe2ee436a9f37d7de3161eca57570e0f905f6a0` (Xác nhận nguyên vẹn).
2. `D:\Flight_Audit_Exports\G7_T016_FINAL_DELIVERABLES\signoff_final\T016_FINAL_SIGNOFF_REVIEW.zip`:
   - SHA-256: `412d978f01d8c3d8992181b74c7577e8bec13e53ed4b8bd1df0ee6b6fa268ac2` (Xác nhận nguyên vẹn).

---

## 4. RANH GIỚI QUẢN TRỊ & BÀN GIAO TIẾP THEO

- Nhiệm vụ T-016 chính thức đóng lại với kết quả nghiệm thu thành công có kiểm soát (`PASS / COMPLETED (CONTROLLED)`).
- Gate G7 tiếp tục giữ trạng thái `IN_PROGRESS`.
- Nhiệm vụ T-017 ở trạng thái `NOT_STARTED / ELIGIBLE_FOR_SEPARATE_AUTHORIZATION` và chỉ được triển khai khi có chỉ thị phê duyệt riêng từ Project Lead.
- Dừng mọi hoạt động kỹ thuật theo đúng yêu cầu sau quyết định này.
