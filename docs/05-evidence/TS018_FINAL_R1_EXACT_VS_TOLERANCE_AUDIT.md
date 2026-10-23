# TS018_FINAL_R1_EXACT_VS_TOLERANCE_AUDIT.md
# Báo Cáo Kiểm Toán Độ Chính Xác Số Học: Exact Match vs Tolerance Audit

**Dự án:** US Flight Performance Analysis 2016–2024  
**Nhiệm vụ:** TS-018 Final Evidence Integrity Review (R1 Correction)  
**Tác giả:** Principal Big Data Engineer, Numerical Precision Auditor  
**Ngày lập:** 2026-10-20  
**Tình trạng:** Kết quả tính toán tự động bằng máy trên toàn bộ 10.500 so sánh số học.

---

## 1. NGUYÊN TẮC PHÂN LOẠI TOÁN HỌC CHUẨN MỰC
Để loại bỏ hoàn toàn khả năng gán nhầm giá trị sai lệch trong phạm vi dung sai (tolerance) thành giá trị bằng nhau tuyệt đối (exact match), hệ thống kiểm chứng đã thiết lập cơ chế phân loại 5 trạng thái độc quyền hỗ tương (Mutually Exclusive):

1. **`EXACT_NUMERIC_MATCH`**: Giá trị hữu hạn và bằng nhau chính xác cả về giá trị số học và biểu diễn nhị phân IEEE-754 64-bit (`diff == 0.0`, cấu trúc bit đồng nhất tuyệt đối).
2. **`TOLERANCE_ONLY_MATCH`**: Giá trị hữu hạn có sai lệch nhỏ nằm trong ngưỡng dung sai được duyệt ($0 < |a - b| \le 10^{-4}$). Nhóm này **tuyệt đối không được tính vào Exact Match**.
3. **`NULL_NULL_AGREEMENT`**: Cả hai nguồn đều mang giá trị null/None hợp lệ theo quy tắc hợp đồng dữ liệu.
4. **`MISMATCH`**: Sai lệch vượt ngưỡng dung sai ($|a - b| > 10^{-4}$) hoặc có sự bất đồng một bên có giá trị còn một bên mang giá trị null.
5. **`NONFINITE_OR_PARSE_ERROR`**: Xuất hiện giá trị không hữu hạn (`NaN`, `+Inf`, `-Inf`) hoặc lỗi định dạng chuỗi không thể phân tích số học.

---

## 2. KẾT QUẢ KIỂM TOÁN CHI TIẾT TỪNG TRƯỜNG (10.500 PHÉP SO SÁNH)

Dữ liệu được trích xuất và tính toán trực tiếp từ công cụ [verify_ts018_two_source_sample_witness.py](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/tools/qa/verify_ts018_two_source_sample_witness.py):

| Tên trường CORE | Tổng số so sánh | EXACT_NUMERIC_MATCH | TOLERANCE_ONLY_MATCH | NULL_NULL_AGREEMENT | MISMATCH | NONFINITE / PARSE | Max Abs Diff ($\Delta_{\max}$) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `ARR_DELAY` | 1.500 | **1.500** | 0 | 0 | 0 | 0 | `0.000000` |
| `DEP_DELAY` | 1.500 | **1.500** | 0 | 0 | 0 | 0 | `0.000000` |
| `TAXI_OUT` | 1.500 | **1.500** | 0 | 0 | 0 | 0 | `0.000000` |
| `TAXI_IN` | 1.500 | **1.500** | 0 | 0 | 0 | 0 | `0.000000` |
| `AIR_TIME` | 1.500 | **1.500** | 0 | 0 | 0 | 0 | `0.000000` |
| `ACTUAL_ELAPSED_TIME` | 1.500 | **1.500** | 0 | 0 | 0 | 0 | `0.000000` |
| `CRS_ELAPSED_TIME` | 1.500 | **1.500** | 0 | 0 | 0 | 0 | `0.000000` |
| **TỔNG CỘNG** | **10.500** | **10.500 (100,00%)** | **0** | **0** | **0** | **0** | **`0.000000`** |

---

## 3. KIỂM CHỨNG BIỂU DIỄN NHỊ PHÂN IEEE-754 VÀ SIGNED ZERO
- **Biểu diễn nhị phân IEEE-754 64-bit:** Toàn bộ 10.500 cặp giá trị số thực dấu phẩy động đều được trích xuất qua `struct.pack('>d', val).hex()`. Kết quả cho thấy 10.500/10.500 cặp đều có chuỗi hex nhị phân trùng khớp 100%.
- **Kiểm tra Signed Zero (`+0.0` vs `-0.0`):**
  - Số lượng cặp giá trị có dấu zero khác nhau (`0x0000000000000000` vs `0x8000000000000000`): **0 cặp**.
  - Không xuất hiện hiện tượng `-0.0` trong bất kỳ trường đo lường nào của cả hai nguồn.

---

## 4. BẰNG CHỨNG PHÒNG VỆ CHỐNG GÁN NHẦM TOLERANCE (NEGATIVE TEST NEG-W07)
Để chứng minh hệ thống không bao giờ gán nhầm một giá trị lệch trong ngưỡng tolerance thành exact match:
- Kịch bản `NEG-W07` trong [test_ts018_negative_witness_verification.py](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/tools/qa/test_ts018_negative_witness_verification.py) đã cố tình bơm một sai khác $\Delta = +0.00005$ vào bản ghi đầu tiên (`RAW_DATASET_ARR_DELAY = -5.99995` trong khi giá trị thực là `-6.0`).
- Sai khác $0,00005$ nằm hoàn toàn dưới ngưỡng dung sai $10^{-4}$ ($0.00010$).
- **Hành vi của hệ thống:**
  - Hàm `classify_comparison` lập tức ghi nhận bản ghi này vào hạng mục `TOLERANCE_ONLY_MATCH` và không tính vào `EXACT_NUMERIC_MATCH`.
  - Chế độ kiểm tra nghiêm ngặt `REQUIRE_STRICT_EXACT` phát hiện `total_tol_only > 0` và kích hoạt ngắt an toàn fail-closed với mã thoát 1 (`exit=1`), in rõ cảnh báo: `Strict exact mode violation: 1 tolerance-only matches detected!`.
- **Kết luận:** Hệ thống bảo đảm tính chính xác tuyệt đối, không có bất kỳ giá trị xấp xỉ nào bị báo cáo sai lệch là Exact Match.
