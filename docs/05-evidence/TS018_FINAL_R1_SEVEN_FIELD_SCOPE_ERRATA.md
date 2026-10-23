# TS018_FINAL_R1_SEVEN_FIELD_SCOPE_ERRATA.md
# Văn Bản Đính Chính Phạm Vi Bảy Trường Đo Số Cốt Lõi TS-018

**Dự án:** US Flight Performance Analysis 2016–2024  
**Nhiệm vụ:** TS-018 Final Evidence Integrity Review (R1 Correction)  
**Quyết định liên quan:** `FP-DEC-012` / Ngoại lệ `G2-EXC-001`  
**Ngày phát hành:** 2026-10-20  
**Tình trạng pháp lý:** Tài liệu kỹ thuật đính chính chính thức; niêm phong bổ sung hồ sơ quản trị.

---

## 1. MỤC ĐÍCH VĂN BẢN
Văn bản này đính chính triệt để sai sót trong các báo cáo văn bản và bản thảo gần đây của AI Agent khi mô tả sai tập 7 trường số cốt lõi thuộc phạm vi đối soát cấp bản ghi TS-018 giữa tập dữ liệu đồ án và BTS TranStats.

---

## 2. NGUYÊN TẮC QUẢN TRỊ BẤT KHẢ XÂM PHẠM
1. **Hợp đồng dữ liệu là tối thượng:** Theo `docs/02-design/DATA_CONTRACT.md`, `docs/02-design/DECISIONS.md` (`FP-DEC-012`) và `G2-EXC-001`, tập 7 trường số cốt lõi của đồ án chỉ bao gồm:
   - `ARR_DELAY`
   - `DEP_DELAY`
   - `TAXI_OUT`
   - `TAXI_IN`
   - `AIR_TIME`
   - `ACTUAL_ELAPSED_TIME`
   - `CRS_ELAPSED_TIME`
2. **Cấm hoán đổi cột nguyên nhân trễ:** Các cột nguyên nhân phân rã độ trễ (`CARRIER_DELAY`, `WEATHER_DELAY`, `NAS_DELAY`, `SECURITY_DELAY`, `LATE_AIRCRAFT_DELAY`) tuyệt đối **không phải** là 7 trường số đo nguyên bản của TS-018 và không được phép dùng để thay thế cho các trường thời gian lăn bánh (`TAXI_OUT`, `TAXI_IN`) hay thời gian bay / hành trình (`AIR_TIME`, `ACTUAL_ELAPSED_TIME`, `CRS_ELAPSED_TIME`).
3. **Bảo tồn tính toàn vẹn của mã nguồn:** Mã nguồn thực tế tại `src/flight_pipeline/kpi/bts_reconciler.py`, `tools/qa/run_ts018_bts_adapter.py`, `tools/qa/verify_ts018_two_source_sample_witness.py` và tệp vật lý `TS018_201901_MATCHED_SAMPLE_WITNESS.csv` **luôn luôn sử dụng đúng 7 trường CORE này**. Lỗi hoàn toàn nằm ở khâu tổng hợp văn bản của Agent.

---

## 3. BẢNG ĐỐI CHIẾU DANH MỤC TRƯỜNG (FIELD-BY-FIELD MAPPING)

| STT | Trường chính thức được phê duyệt (`FP-DEC-012` / `G2-EXC-001`) | Kiểu dữ liệu | Ý nghĩa đo lường trong đồ án | Mô tả sai trong báo cáo Agent cũ | Đánh giá sai lệch |
| :---: | :--- | :---: | :--- | :--- | :--- |
| **1** | `ARR_DELAY` | Float (Phút) | Độ lệch giờ đến thực tế so với lịch trình | `ARR_DELAY` | Khớp đúng |
| **2** | `DEP_DELAY` | Float (Phút) | Độ lệch giờ khởi hành thực tế so với lịch trình | `DEP_DELAY` | Khớp đúng |
| **3** | `TAXI_OUT` | Float (Phút) | Thời gian lăn bánh từ cửa ra đến khi cất cánh | `CARRIER_DELAY` *(Sai)* | **SAI LỆCH NGHIÊM TRỌNG** |
| **4** | `TAXI_IN` | Float (Phút) | Thời gian lăn bánh từ khi hạ cánh đến cửa vào | `WEATHER_DELAY` *(Sai)* | **SAI LỆCH NGHIÊM TRỌNG** |
| **5** | `AIR_TIME` | Float (Phút) | Thời gian bay thực tế trên không | `NAS_DELAY` *(Sai)* | **SAI LỆCH NGHIÊM TRỌNG** |
| **6** | `ACTUAL_ELAPSED_TIME` | Float (Phút) | Tổng thời gian hành trình thực tế (Gate-to-Gate) | `SECURITY_DELAY` *(Sai)* | **SAI LỆCH NGHIÊM TRỌNG** |
| **7** | `CRS_ELAPSED_TIME` | Float (Phút) | Tổng thời gian hành trình theo lịch trình công bố | `LATE_AIRCRAFT_DELAY` *(Sai)* | **SAI LỆCH NGHIÊM TRỌNG** |

---

## 4. DANH SÁCH TÀI LIỆU ẢNH HƯỞNG VÀ HÀNH ĐỘNG KHẮC PHỤC

| Tài liệu bị ảnh hưởng | Vị trí sai | Mức độ ảnh hưởng | Hành động khắc phục |
| :--- | :--- | :---: | :--- |
| Báo cáo tổng kết Agent phiên trước | Phần A.1, Phần A.2, Phần D.2 | Cao (Gây hiểu nhầm phạm vi) | Phát hành báo cáo tổng kết mới R1 thay thế toàn diện; trích xuất số liệu từ mã nguồn thực tế. |
| `docs/05-evidence/TS018_FINAL_SAMPLE_DISTRIBUTION_AUDIT.md` | Bảng phân tầng và tên trường | Trung bình (Tài liệu diễn giải) | Thay thế bằng tài liệu kiểm toán phân tầng R1 mới [TS018_FINAL_R1_SAMPLING_FORENSIC_AUDIT.md](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/docs/05-evidence/TS018_FINAL_R1_SAMPLING_FORENSIC_AUDIT.md). |
| `docs/05-evidence/TS018_FINAL_INDEPENDENT_REPLAY_REPORT.md` | Phần giới thiệu liệt kê cột | Thấp (Dữ liệu bảng và mã nguồn đúng) | Giữ nguyên tệp bằng chứng lịch sử; bổ sung văn bản đính chính này làm phụ lục có hiệu lực pháp lý cao hơn. |

---

## 5. KẾT LUẬN VÀ CAM KẾT KIỂM TOÁN
Toàn bộ hồ sơ nghiệm thu chính thức hiện hành của Gate G5 và nhiệm vụ TS-018 chỉ công nhận **đúng bảy trường số nguyên bản**: `ARR_DELAY`, `DEP_DELAY`, `TAXI_OUT`, `TAXI_IN`, `AIR_TIME`, `ACTUAL_ELAPSED_TIME`, `CRS_ELAPSED_TIME`. Mọi tuyên bố kỹ thuật trong giai đoạn này chỉ có giá trị pháp lý khi dựa trên đúng bảy trường này.
