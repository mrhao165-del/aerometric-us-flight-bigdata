# TS018_SIGNOFF_DOSSIER_NEGATIVE_TEST_VERDICT.md
# Phán Quyết Kỹ Thuật: Bộ Kiểm Thử Tiêu Cực Chống False-PASS (NEG-W01 Đến NEG-W14)

**Dự án:** US Flight Performance Analysis 2016–2024  
**Nhiệm vụ:** TS-018 Final Signoff Dossier Reconciliation (Finding E05)  
**Tác giả:** Independent Forensic Evidence Auditor, Principal Big Data QA Engineer  
**Thời điểm lập:** 2026-10-20  
**Thẩm quyền:** Báo cáo kiểm định độc lập phục vụ Project Lead; không tự ký nghiệm thu.

---

## 1. MỤC TIÊU VÀ NGUYÊN TẮC THIẾT KẾ (TEST SUITE ARCHITECTURE)

Bộ kiểm thử tiêu cực [`test_ts018_negative_witness_verification.py`](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/tools/qa/test_ts018_negative_witness_verification.py) được xây dựng nhằm chứng minh công cụ kiểm chứng TS-018 có khả năng phát hiện lỗi và từ chối các dữ liệu sai lệch (fail-closed), tuyệt đối không để lọt bất kỳ lỗi ngụy trang (false-PASS) nào.

### Nguyên tắc kiểm định nghiêm ngặt:
1. **Phân loại rạch ròi loại hình kiểm thử:** Tách biệt rõ kiểm thử mức tiến trình (Process-level mutation) và kiểm thử mức đơn vị (Component unit checks).
2. **Độ đặc hiệu của chẩn đoán (Diagnostic Specificity):** Mỗi ca kiểm thử bắt buộc phải kích hoạt đúng thông báo chẩn đoán mục tiêu. Tuyệt đối không chấp nhận lỗi cú pháp (`SyntaxError`), lỗi truy cập từ điển (`KeyError`) hay sự cố môi trường (`Unhandled Traceback`) làm bằng chứng PASS âm tính.
3. **Đặc trị Finding E05 (NEG-W09):** Ca kiểm thử tiêm token `NaN` bắt buộc phải kiểm tra thông báo chứa chính xác `NONFINITE_OR_INVALID_TOKEN`, loại bỏ hoàn toàn các chuỗi so khớp lỏng lẻo chung chung (như `"mismatches"`).

---

## 2. BẢNG PHÂN LOẠI VÀ KẾT QUẢ 14 CA KIỂM THỬ TIÊU CỰC

| Mã kiểm thử | Nhóm kiểm thử | Dạng lỗi / Vector tiêm vào | Thông báo chẩn đoán mục tiêu được xác minh | Mã thoát / Kết quả phân loại | Phán quyết kỹ thuật |
| :---: | :---: | :--- | :--- | :---: | :---: |
| **NEG-W01** | **Category A** (Process Mutation) | Sai lệch giá trị số đo trong witness (`-999.0` vs `-6.0`) | `discrepancies detected between raw CSV and witness (includes MISMATCH)` | `exit=1` | **PASS (Fail-Closed)** |
| **NEG-W02** | **Category A** (Process Mutation) | Chuyến bay không tồn tại (`2019-01-01|ZZ|9999|XYZ|ZZZ`) | `witness keys missing from raw CSV` | `exit=1` | **PASS (Fail-Closed)** |
| **NEG-W03** | **Category A** (Process Mutation) | Sửa đổi nội dung làm sai lệch SHA-256 tệp witness | `Sealed witness checksum mismatch` | `exit=1` | **PASS (Fail-Closed)** |
| **NEG-W04** | **Category A** (Process Mutation) | Lật dấu độ trễ (slipped sign: `-6.0` $\rightarrow$ `+6.0`) | `discrepancies detected between raw CSV and witness` | `exit=1` | **PASS (Fail-Closed)** |
| **NEG-W05** | **Category A** (Process Mutation) | Tiêm khóa composite trùng lặp trong tệp witness | `Duplicate composite key detected in witness` | `exit=1` | **PASS (Fail-Closed)** |
| **NEG-W06** | **Category A** (Process Mutation) | Thay thế số đo khác không bằng `0.0` (`TAXI_OUT 13.0 -> 0.0`) | `discrepancies detected between raw CSV and witness` | `exit=1` | **PASS (Fail-Closed)** |
| **NEG-W07** | **Category A** (Process Mutation) | Độ lệch nhỏ trong dung sai (`+0.00005`) dưới chế độ strict | `Strict exact mode violation: 1 tolerance-only matches detected` | `exit=1` | **PASS (Fail-Closed)** |
| **NEG-W08** | **Category A** (Process Mutation) | Bất đồng Null thực sự (chuỗi rỗng `""` vs `98.0`) | `discrepancies detected between raw CSV and witness` | `exit=1` | **PASS (Fail-Closed)** |
| **NEG-W09** | **Category A** (Process Mutation) | Tiêm token phi hữu hạn (`"NaN"` trong `CRS_ELAPSED_TIME`) | `includes NONFINITE_OR_INVALID_TOKEN` (Khẳng định đặc hiệu Finding E05) | `exit=1` | **PASS (Fail-Closed)** |
| **NEG-W10** | **Category A** (Process Mutation) | Sai lệch ngày bay thực tế (`2019-01-10` $\rightarrow$ `2019-01-20`) | `witness keys missing from raw CSV` | `exit=1` | **PASS (Fail-Closed)** |
| **NEG-W11** | **Category B** (Component Unit) | Cả hai nguồn cùng chứa token `"NaN"` | Phân loại là `NONFINITE_OR_INVALID_TOKEN`, loại trừ `NULL_NULL_AGREEMENT` | `category=NONFINITE` | **PASS (Anti-False-Pass)** |
| **NEG-W12** | **Category B** (Component Unit) | Sai lệch dấu ở số 0 (`+0.0` vs `-0.0`) | Phân loại là `NUMERIC_EQUAL_SIGNED_ZERO_DIFF`, loại trừ `EXACT_BITWISE_MATCH` | `category=SIGNED_ZERO` | **PASS (Strict Bitwise)** |
| **NEG-W13** | **Category B** (Component Unit) | Parser kiểm tra các token văn bản hỏng (`"Infinity"`, `"12.34.56"`) | Toàn bộ bị phân loại là `NONFINITE_OR_INVALID_TOKEN`, không bị biến thành `VALID_NULL` | `kinds=INVALID_TOKEN` | **PASS (Domain Guard)** |
| **NEG-W14** | **Category C** (Strict Policy) | Cả hai nguồn cùng mang giá trị Null (`""` vs `""`) | Phân loại là `NULL_NULL_AGREEMENT`, loại trừ `EXACT_BITWISE_MATCH` (Finding E04) | `category=NULL_NULL` | **PASS (Strict Policy Guard)** |

---

## 3. KẾT LUẬN VỀ CHẤT LƯỢNG BỘ KIỂM THỬ TIÊU CỰC
- Toàn bộ **14/14 ca kiểm thử tiêu cực đều đạt PASS** với hành vi fail-closed xác định.
- Tỷ lệ phát hiện lỗi đạt **100%**. Không có ngoại lệ nào gây crash tiến trình ngoài mong muốn.
- Khép triệt để **Finding E05** và **Finding E04**.
