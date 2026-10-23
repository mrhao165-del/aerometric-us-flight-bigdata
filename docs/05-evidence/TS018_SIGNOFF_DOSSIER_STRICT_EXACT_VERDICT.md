# TS018_SIGNOFF_DOSSIER_STRICT_EXACT_VERDICT.md
# Phán Quyết Kỹ Thuật: Tính Chẵn Lẻ Bitwise Tuyệt Đối 100% Của Hai Nguồn Vật Lý

**Dự án:** US Flight Performance Analysis 2016–2024  
**Nhiệm vụ:** TS-018 Final Signoff Dossier Reconciliation (Finding E04)  
**Tác giả:** Independent Forensic Evidence Auditor, Principal Big Data QA Engineer  
**Thời điểm lập:** 2026-10-20  
**Thẩm quyền:** Báo cáo kiểm định độc lập phục vụ Project Lead; không tự ký nghiệm thu.

---

## 1. MỤC TIÊU VÀ TIÊU CHÍ NGHIỆM THU NGHIÊM NGẶT (STRICT EXACT SPECIFICATION)

Để bảo đảm tính trung thực khoa học tuyệt đối và loại bỏ hoàn toàn khả năng ngộ nhận (false-PASS), công cụ đối soát hai nguồn [`verify_ts018_two_source_sample_witness.py`](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/tools/qa/verify_ts018_two_source_sample_witness.py) đã được nâng cấp với các điều kiện ràng buộc toán học và mật mã học nghiêm ngặt:

1. **Điều kiện nghiệm thu bitwise bắt buộc:**  
   Tổng số phép so sánh đạt chuẩn bitwise nhị phân IEEE-754 phải đạt chính xác:
   $$\text{total\_exact\_bitwise} == N_{\text{records}} \times N_{\text{fields}} = 1.500 \times 7 = 10.500$$
2. **Quy tắc loại trừ tuyệt đối:**
   - Số phép so sánh chỉ đạt dung sai (`TOLERANCE_ONLY_MATCH`): **phải bằng $0$**.
   - Số phép so sánh có sai lệch dấu số 0 (`NUMERIC_EQUAL_SIGNED_ZERO_DIFF`, tức `+0.0` vs `-0.0`): **phải bằng $0$**.
   - Số phép so sánh có giá trị Null (`NULL_NULL_AGREEMENT`): **phải bằng $0$** trong tập mẫu nghiệm thu bitwise.
   - Số phép so sánh sai lệch (`MISMATCH`): **phải bằng $0$**.
   - Số token không hợp lệ hoặc không hữu hạn (`NONFINITE_OR_INVALID_TOKEN`, như `NaN`, `Inf`): **phải bằng $0$**.
3. **Bảo vệ tiêu đề kết quả (Anti-False-Pass Banner Guard):**  
   Thông điệp `VERIFICATION RESULT: 100% REPRODUCIBLE STRICT EXACT TWO-SOURCE PARITY PASS` **chỉ được phép in ra** khi và chỉ khi toàn bộ $10.500$ phép so sánh đều là `EXACT_BITWISE_MATCH` và mọi loại sai lệch bằng $0$. Bất kỳ trường hợp nào có `null_null > 0` hoặc `exact < 10.500` đều bị chặn hoặc chuyển sang tiêu đề không nghiêm ngặt (`NON-STRICT`).

---

## 2. BẢNG PHÂN TÍCH CHI TIẾT THEO TỪNG TRƯỜNG SỐ ĐO (FIELD-BY-FIELD BREAKDOWN)

Kết quả chạy lại thực tế trên hai nguồn vật lý (`flight_with_weather_2019.csv` và `T_ONTIME_REPORTING_20261019_112232.zip`):

| Trường số đo CORE | Tổng số bản ghi | Trùng khớp Bitwise IEEE-754 | Lệch dấu số 0 (+0 vs -0) | Khớp nhờ dung sai ($>0$) | Null-Null | Sai lệch (Mismatch) | Sai lệch tuyệt đối lớn nhất ($\max \|\Delta\|$) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `ARR_DELAY` | 1.500 | **1.500** | 0 | 0 | 0 | 0 | `0.000000` |
| `DEP_DELAY` | 1.500 | **1.500** | 0 | 0 | 0 | 0 | `0.000000` |
| `TAXI_OUT` | 1.500 | **1.500** | 0 | 0 | 0 | 0 | `0.000000` |
| `TAXI_IN` | 1.500 | **1.500** | 0 | 0 | 0 | 0 | `0.000000` |
| `AIR_TIME` | 1.500 | **1.500** | 0 | 0 | 0 | 0 | `0.000000` |
| `ACTUAL_ELAPSED_TIME` | 1.500 | **1.500** | 0 | 0 | 0 | 0 | `0.000000` |
| `CRS_ELAPSED_TIME` | 1.500 | **1.500** | 0 | 0 | 0 | 0 | `0.000000` |
| **TỔNG CỘNG** | **10.500** | **10.500** | **0** | **0** | **0** | **0** | **`0.000000`** |

---

## 3. TỔNG KẾT VÀ PHÁN QUYẾT KỸ THUẬT

1. **Tỷ lệ trùng khớp bitwise thực tế:** **`100.00%`** ($10.500 / 10.500$ phép so sánh).
2. **Khóa đối soát:** Đúng $1.500$ khóa composite độc nhất được phân tầng đại diện; $0$ va chạm trùng khóa trong CSV thô và $0$ va chạm trùng khóa trong BTS ZIP.
3. **Bảo toàn ngữ nghĩa:**
   - Độ trễ âm (đến sớm) được bảo toàn nguyên vẹn (ví dụ: `-6.0`, `-4.0`).
   - Mốc thời gian không trễ được biểu diễn dưới dạng số thực dương chuẩn (`+0.0`).
   - Các trường thời gian bay và lăn bánh khớp tuyệt đối với báo cáo chính thức của Cục Thống kê Giao thông Vận tải Hoa Kỳ.
4. **Phán quyết:** Tiêu chí kỹ thuật TS-018 dưới phương án **FP-DEC-019 (Option B)** hoàn toàn thỏa mãn ở cấp độ cao nhất.
