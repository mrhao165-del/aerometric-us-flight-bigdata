# G5_D3_TS018_HUMAN_TECHNICAL_SIGNOFF_DRAFT.md
# Biên Bản Nghiệm Thu Kỹ Thuật Chính Thức Nhiệm Vụ TS-018 (Quyết Định D3 — Official Controlled Signoff)

**Dự án:** US Flight Performance Analysis 2016–2024  
**Hạng mục quản trị:** Quyết định độc lập D3 — TS-018 Human Technical Signoff  
**Cổng quản lý:** Gate G5 — IN_PROGRESS  
**Nhiệm vụ kiểm thử:** TS-018 (Authentic BTS TranStats Parity Verification)  
**Trạng thái hiện tại:** **`PASS (CONTROLLED)`**  
**Cơ sở ủy quyền:** Project Lead Explicit Authorization (2026-10-21: *"D3 — APPROVED: I approve the official controlled technical signoff of TS-018, based on the previously reviewed evidence of 1,500 matched flight keys and 10,500 exact numeric comparisons across seven CORE fields, within the scope of FP-DEC-019 Option B."*)  
**Điều kiện chặn:** `NONE` (Toàn bộ điều kiện tiên quyết D1, D2 đã thỏa mãn hợp lệ)  
**Tác giả:** Principal Big Data QA Engineer & Independent Evidence Auditor  
**Thời điểm phê duyệt:** 2026-10-21  

---

## 1. MỤC TIÊU VÀ ĐIỀU KIỆN TIÊN QUYẾT

Nhiệm vụ TS-018 có mục tiêu đối soát dữ liệu của tập dữ liệu bay Hoa Kỳ với nguồn dữ liệu nguyên bản BTS TranStats nhằm bảo đảm dữ liệu đầu vào không bị làm sai lệch về mặt số học.

**Các điều kiện tiên quyết bắt buộc để quyết định D3 có hiệu lực:**
1. Quyết định **D1** (Xác nhận nguồn gốc BTS) đã được người tải (Project Lead: *"tôi là người tải bộ dữ liệu BTS"*) và kiểm định mã băm tệp ZIP đạt `PASS (CONTROLLED)`.
2. Quyết định **D2** (Phê duyệt chính sách FP-DEC-019 Option B) đã được Project Lead phê duyệt chính thức.
3. Bằng chứng kiểm chứng số học nghiêm ngặt (Strict Parity Replay) trên 1.500 chuyến bay phân tầng hạn ngạch $\times$ 7 trường giữ vững kết quả 10.500/10.500 bitwise exact.
4. Toàn bộ 14 ca kiểm thử tiêu cực (Negative tests) đạt kết quả fail-closed và công cụ kiểm chứng hoạt động ở chế độ nghiêm ngặt (`REQUIRE_STRICT_EXACT = True`).

---

## 2. TỔNG HỢP KẾT QUẢ KIỂM CHỨNG KỸ THUẬT

| Hạng mục kiểm định | Bằng chứng kỹ thuật | Kết quả | Ghi chú |
| :--- | :--- | :---: | :--- |
| **Công cụ đối soát chính thức** | `tools/qa/verify_ts018_two_source_sample_witness.py` | `PASS` | Đã khóa cứng mã băm witness chuẩn; `REQUIRE_STRICT_EXACT = True`. |
| **Đặc tính tập mẫu** | Mẫu phân tầng hạn ngạch 17 hãng theo seed `ts018_bts_jan2019_seed_42` | `CONTROLLED_SAMPLE` | Không gán tính đại diện i.i.d. cho toàn bộ tổng thể. |
| **Kiểm tra khóa trùng lặp** | Phát hiện duplicate keys trong witness, raw và BTS | `PASS` | 0 duplicate keys trên toàn bộ 1.500 bản ghi. |
| **Phân loại số học chuẩn xác** | Nhận diện tường minh `NULL`, `NaN`, `Inf`, `-0.0` | `PASS` | Không chuyển đổi ngầm token không hợp lệ thành 0 hay None. |
| **Tỷ lệ trùng khớp số học** | 10.500 giá trị float64 so sánh mức bitwise IEEE-754 | `PASS` | **10.500 / 10.500 (100.0%) trùng khớp tuyệt đối**. |
| **Dung sai số học (Tolerance-only)** | Trường hợp chỉ khớp trong khoảng dung sai $10^{-4}$ | `PASS` | **0 trường hợp**. |
| **Bộ kiểm thử tiêu cực chống False-PASS** | 14 kịch bản bơm dữ liệu lỗi độc lập (NEG-W01 đến NEG-W14) | `PASS` | 14/14 kịch bản bị chặn bắt chính xác với mã lỗi đặc thù. |
| **Hồi quy chính sách tham chiếu BTS** | 6 kịch bản kiểm tra chính sách BTS | `PASS` | 6/6 kịch bản đạt chuẩn. |

---

## 3. RANH GIỚI BẢO LƯU VÀ TÁC ĐỘNG QUẢN TRỊ KHI ĐƯỢC PHÊ DUYỆT

1. **Ranh giới bắt buộc `PARQUET_PARITY_NOT_TESTED`:**
   - Nghiệm thu này được giới hạn nghiêm ngặt ở mức kiểm thử đơn vị: đối soát giữa tệp **RAW CSV 2019** và **BTS CSV tháng 1/2019**.
   - Quyết định này **KHÔNG CHỨNG NHẬN** tính chẵn lẻ của tệp Parquet năm 2019 (vì Parquet 2019 chưa được tạo ra tại Gate G5).
2. **Ngoại lệ G2-EXC-001 (Đơn vị tính sơ bộ):**
   - Hiện tại duy trì trạng thái **`ACTIVE`** cho đến khi Project Lead chính thức ký phê duyệt văn bản này.
   - Ngay khi văn bản này được ký chính thức, ngoại lệ `G2-EXC-001` chuyển trạng thái sang **`RESOLVED_BY_OPTION_B`** cho đúng 7 trường CORE: `ARR_DELAY`, `DEP_DELAY`, `TAXI_OUT`, `TAXI_IN`, `AIR_TIME`, `ACTUAL_ELAPSED_TIME`, `CRS_ELAPSED_TIME`.
3. **Khép hợp đồng kỹ thuật Task T-011:**
   - Hợp đồng của Task T-011 chuyển trạng thái từ `PENDING_TS018` sang **`CLOSED / FULL_CONTRACT_PASS`**.
4. **Các rủi ro tồn đọng tiếp tục duy trì:**
   - `OR-05` (Thiếu tháng 3/2024): Tiếp tục duy trì `OPEN_QUALITY_DEFECT`.
   - `OR-08` (Tính xác thực thượng nguồn Kaggle 9 năm): Tiếp tục duy trì `IDENTITY_UNVERIFIED`.
   - `FP-DEC-017` (Thời tiết): Tiếp tục duy trì `CONDITIONAL_NO_GO`.

---

## 4. QUYẾT ĐỊNH CỦA PROJECT LEAD (PHÊ DUYỆT CHÍNH THỨC CÓ KIỂM SOÁT)

> [!NOTE]
> Project Lead chính thức phê duyệt nghiệm thu kỹ thuật TS-018 ngày 2026-10-21 theo chỉ thị rõ ràng:
> *"D3 — APPROVED: I approve the official controlled technical signoff of TS-018, based on the previously reviewed evidence of 1,500 matched flight keys and 10,500 exact numeric comparisons across seven CORE fields, within the scope of FP-DEC-019 Option B."*

1. **Xác nhận kết quả kỹ thuật:** Toàn bộ 10.500 giá trị kiểm toán trên 1.500 chuyến bay đã đạt 100% bitwise exact, 14/14 negative tests PASS, công cụ hoạt động nghiêm ngặt ở chế độ `REQUIRE_STRICT_EXACT = True`.
2. **Xác nhận chính sách:** Quyết định D2 (FP-DEC-019 Option B) đã được phê duyệt chính thức.
3. **Xác nhận nguồn gốc D1:** Project Lead đã chứng thực là người tải bộ dữ liệu BTS; tệp ZIP đạt kiểm định SHA-256 tuyệt đối.
4. **Hiệu lực chuyển trạng thái chính thức:**
   * **`D3 = PASS (CONTROLLED)`**
   * **`TS-018 = PASS (CONTROLLED)`**
   * **`G2-EXC-001 = RESOLVED_BY_TS018_APPROVED_OPTION_B`** (Ngoại lệ đơn vị đo của 7 trường CORE chính thức khép lại).
   * **`T-011 FULL_CONTRACT_CLOSEOUT = PASS (CONTROLLED)`** (Hợp đồng nhiệm vụ T-011 chính thức khép lại).

- **Cơ sở ủy quyền:** Project Lead Explicit Authorization (2026-10-21)
- **Trạng thái chính thức:** **`PASS (CONTROLLED)`**
- **Ngày phê duyệt:** 2026-10-21
