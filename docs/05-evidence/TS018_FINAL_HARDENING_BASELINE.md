# TS018_FINAL_HARDENING_BASELINE.md
# Báo Cáo Đối Soát Đường Cơ Sở Trước Khắc Phục Điểm Yếu Công Cụ TS-018

**Dự án:** US Flight Performance Analysis 2016–2024  
**Nhiệm vụ:** TS-018 — Final Verifier Hardening & Controlled Signoff Readiness  
**Tác giả:** Principal Big Data QA Engineer, Independent Evidence Auditor  
**Thời điểm lập:** 2026-10-20  
**Thẩm quyền:** Báo cáo kỹ thuật độc lập; không thay thế quyết định của Project Lead.

---

## 1. MỤC TIÊU VÀ PHẠM VI
Tài liệu này xác lập đường cơ sở (baseline) kỹ thuật và mật mã học trước khi tiến hành khép 5 điểm yếu cuối cùng (H01–H05) của công cụ đối soát hai nguồn TS-018, bảo đảm mọi bằng chứng được tạo ra đều có thể truy vết và kiểm toán độc lập.

---

## 2. ĐƯỜNG CƠ SỞ ĐÃ ĐƯỢC XÁC MINH ĐỘC LẬP (ESTABLISHED BASELINE)

### 2.1. Gói nén kiểm toán tiền nhiệm (T011 R1 Package)
- **Tên gói nén:** `TS018_G5_FINAL_R1_CORRECTED_REVIEW_PACKAGE.zip`
- **Mã băm SHA-256:** `6e84004716f269bf43b2e1f3bcf4c8befdc9a71d6be3f73dd4dbd3b841354c75`
- **Số lượng thành viên:** `749` tệp, toàn vẹn cấu trúc ZIP CRC: **`PASS`**.
- **Đánh giá của Independent Reviewer:** Reviewer đã xác minh trực tiếp 1.500/1.500 khóa trong ZIP BTS thật và 10.500/10.500 giá trị BTS trùng khớp tệp witness ở mức IEEE-754.

### 2.2. Dấu vân tay mật mã học của các nguồn dữ liệu vật lý
1. **Tệp tham chiếu BTS TranStats chính thức tháng 1/2019:**
   - Đường dẫn: `data/reference/bts_transtats/original/T_ONTIME_REPORTING_20261019_112232.zip`
   - Dung lượng: `29.975.383` bytes
   - **Mã băm SHA-256:** `342de99f65561fb856b524c704f2ad3851f8015f52251668ece346dff1350ae6`
   - Tính toàn vẹn bên trong: Tệp `T_ONTIME_REPORTING.csv` có CRC hợp lệ.
2. **Tệp CSV dữ liệu thô dự án năm 2019:**
   - Đường dẫn: `data/raw/tabular/2019/flight_with_weather_2019.csv`
   - Dung lượng: `1.990.370.667` bytes
   - **Mã băm SHA-256:** `eec50211a1a63f37b840977be5ab2e99a008a8d5234c2a12df8eb50862f93b4a`
3. **Tệp mẫu chứng thực hai nguồn đã niêm phong (Sealed Witness):**
   - Đường dẫn: `docs/05-evidence/TS018_201901_MATCHED_SAMPLE_WITNESS.csv`
   - Dung lượng: `294.436` bytes (1.500 dòng dữ liệu + 1 dòng header)
   - **Mã băm SHA-256:** `942c476994c414378a541d5c84fcbdad35c6aeace1c98891044a085d55c3a9a1`
   - Trạng thái: Bất biến (Immutable), không chỉnh sửa.

---

## 3. PHẠM VI 7 TRƯỜNG SỐ ĐO CỐT LÕI
Theo quyết định `FP-DEC-012`, `DATA_CONTRACT.md` và ngoại lệ `G2-EXC-001`, đúng 7 trường số đo cốt lõi được đối soát bao gồm:
1. `ARR_DELAY`
2. `DEP_DELAY`
3. `TAXI_OUT`
4. `TAXI_IN`
5. `AIR_TIME`
6. `ACTUAL_ELAPSED_TIME`
7. `CRS_ELAPSED_TIME`

Nhãn kỹ thuật chính thức của bằng chứng là: `2019_RAW_SOURCE_VS_BTS` (tuyệt đối không gọi là `2019_PARQUET_PARITY` do năm 2019 chưa được nạp vào Staging Parquet).

---

## 4. MA TRẬN TRẠNG THÁI QUẢN TRỊ DUY TRÌ
- Gate G2, G3: **PASS**
- Gate G4: **PASS (CONTROLLED)**
- Task T-010: **PASS (CONTROLLED)**
- Task T-011 Technical Signoff: **PASS / SIGNED_OFF (CONTROLLED)**
- Task T-011 Contractual Closeout: **PENDING_TS018**
- TS-018: **OPEN**
- Ngoại lệ G2-EXC-001: **ACTIVE**
- Chính sách Option B: **FP-DEC-PROP-019 (PROPOSED)**
- Gate G5: **IN_PROGRESS**
- Gate G6: **NOT_STARTED / BLOCKED**
- Khiếm khuyết OR-05 (thiếu tháng 3/2024): **OPEN_QUALITY_DEFECT**
- Nguồn gốc Kaggle OR-08: **IDENTITY_UNVERIFIED**
- Thời tiết FP-DEC-017: **CONDITIONAL_NO_GO**
