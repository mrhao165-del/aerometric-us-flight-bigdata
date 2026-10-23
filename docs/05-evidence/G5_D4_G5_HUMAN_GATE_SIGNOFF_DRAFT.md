# G5_D4_G5_HUMAN_GATE_SIGNOFF_DRAFT.md
# Biên Bản Nghiệm Thu Đóng Cổng Quản Lý Gate G5 (Quyết Định D4 — Official Gate Signoff)

**Dự án:** US Flight Performance Analysis 2016–2024  
**Hạng mục quản trị:** Quyết định độc lập D4 — G5 Human Gate Signoff  
**Cổng quản lý:** Gate G5 — **PASS (CONTROLLED)**  
**Cổng tiếp theo:** Gate G6 — **READY_FOR_PREPARATION / BLOCKED_ON_D5**  
**Trạng thái kỹ thuật:** **19/19 TIÊU CHÍ KỸ THUẬT ĐẠT CHUẨN (TECHNICALLY READY & VERIFIED)**  
**Trạng thái quản trị:** **PASS (CONTROLLED) — CHÍNH THỨC PHÊ DUYỆT BỞI PROJECT LEAD**  
**Tác giả:** Project Governance Officer & Principal Big Data Engineer  
**Thời điểm phê duyệt:** 2026-10-21  

---

## 1. MỤC ĐÍCH VÀ NGUYÊN TẮC QUẢN TRỊ

Gate G5 (Pipeline Integration, Smoke Testing, KPI Engine & Staging Readiness) là cổng kỹ thuật bản lề trước khi chuyển sang giai đoạn vận hành toàn diện quy mô lớn 9 năm (Gate G6 / Task T-012).

Theo nguyên tắc quản trị tại `AGENTS.md` và `DECISIONS.md`:
1. **Chỉ Project Lead có quyền ký đóng Gate G5.**
2. Việc ký đóng Gate G5 chỉ được thực hiện sau khi tất cả các tiêu chí thành phần (bao gồm D1, D2, D3) đã hoàn tất và các rủi ro tồn đọng được định danh, kiểm soát chặt chẽ.
3. **Quyết định D4 ký đóng Gate G5 KHÔNG tự động cấp phép khởi chạy Gate G6 (Quyết định D5).**

---

## 2. BẢNG ĐỐI SOÁT 19 TIÊU CHÍ NGHIỆM THU GATE G5 (G5 EXIT CRITERIA)

| STT | Tiêu chí nghiệm thu Gate G5 | Bằng chứng kỹ thuật thực tế | Trạng thái kỹ thuật |
| :---: | :--- | :--- | :---: |
| **1** | Bounded Smoke trên dữ liệu thật 2016 (T-010) | Báo cáo `T010_FULL_BASELINE_AND_PREFLIGHT.md`, **5.537.987** hàng xử lý thành công. | `PASS (CONTROLLED)` |
| **2** | Bất biến dữ liệu thô (Raw Data Immutability) | 9 tệp CSV thô được kiểm chứng băm SHA-256 trước và sau chạy smoke, 0 bit bị thay đổi. | `PASS` |
| **3** | Phân vùng Staging Parquet 2016 chuẩn hóa | 50 tệp Parquet staging 2016 khớp hoàn toàn lược đồ 34 cột (`b5805fca...`). | `PASS` |
| **4** | Cân bằng hạch toán dòng DC-11/DC-12 | $5.537.987 = 5.537.987 + 0 + 0$, 0 dòng sai lệch hoặc thất thoát. | `PASS` |
| **5** | Động cơ tính toán 8 CORE KPI (T-011) | `KpiCalculator` tính đúng 8 KPI trên 4 chiều phân tích, đạt kiểm thử đơn vị. | `PASS` |
| **6** | Lược đồ bảng xuất bản KPI 17 trường | Định dạng cột và kiểu dữ liệu tuân thủ nghiêm ngặt `KPI_SPEC.md`. | `PASS` |
| **7** | Cơ chế khóa Single-Writer trên Windows NTFS | `SingleWriterLock` bảo đảm loại trừ tương hỗ nguyên tử, chặn race condition. | `PASS` |
| **8** | Chống nuốt lỗi và dọn dẹp khóa khi tiến trình chết | Cơ chế kiểm tra liveness qua PID, xử lý token mismatch, fail-closed an toàn. | `PASS` |
| **9** | Đánh dấu sự cố giải phóng khóa bền vững | Bền vững hóa báo cáo incident vào thư mục khóa, ngăn writer mới chen ngang. | `PASS` |
| **10** | Quy trình xuất bản an toàn 7 bước (SafePublisher) | Hoán đổi con trỏ nguyên tử, rollback không phá hủy khi xảy ra lỗi bước 5/6. | `PASS` |
| **11** | Công cụ kiểm tra con trỏ Staging độc lập | `tools/qa/verify_staging_pointer.py` chỉ đọc, kiểm tra path traversal, 13/13 test PASS. | `PASS` |
| **12** | Khép các điểm yếu kiểm chứng TS-018 (E01–E05) | Strict verifier, phát hiện khóa trùng, phân biệt NaN/Inf với null, pinned hash. | `PASS` |
| **13** | Đối soát số học 100% bitwise exact với BTS | 10.500/10.500 giá trị trên 1.500 chuyến bay khớp mức bitwise IEEE-754. | `PASS` |
| **14** | Bộ kiểm thử tiêu cực chống False-PASS | 14/14 ca kiểm thử tiêu cực chặn lỗi đúng mục tiêu, exit code $\neq 0$. | `PASS` |
| **15** | Đạt hồi quy chính sách tham chiếu BTS | 6/6 kịch bản hồi quy chính sách tham chiếu đạt chuẩn. | `PASS` |
| **16** | Đạt kiểm tra nhất quán cây làm việc | Lịch sử TS-018: 1.545; Phiên rà soát preflight mới: **1.569/1.569** khẳng định PASS. | `PASS` |
| **17** | Đạt kiểm thử hồi quy sổ đăng ký (Registry regression) | `test_working_tree_registry_regression.py` đạt **16/16** test POS/NEG/MUT. | `PASS` |
| **18** | Đo lường dung lượng đĩa và tài nguyên trạm | Đĩa D trống **57.90 GiB** (62.17 GB), ngân sách 18.50 GiB (19.86 GB), hệ số an toàn **3.13x**. | `PASS` |
| **19** | Phân định ranh giới và tài liệu hóa rủi ro | Toàn bộ 5 rủi ro tồn đọng được định danh tường minh trong Sổ đăng ký rủi ro. | `PASS` |

---

## 3. DANH MỤC 5 RỦI RO TỒN ĐỌNG VÀ NGOẠI LỆ ĐƯỢC BẢO LƯU

Việc đóng Gate G5 được thực hiện dưới sự bảo lưu của các ngoại lệ có kiểm soát:

1. **Rủi ro thượng nguồn OR-08 (IDENTITY_UNVERIFIED):**
   - Nguồn gốc Kaggle của toàn bộ 9 năm dữ liệu chưa có chuỗi hành trình chính thức từ BTS. Chấp nhận rủi ro này ở mức độ nghiên cứu học thuật/mô tả.
2. **Khiếm khuyết dữ liệu OR-05 (Thiếu tháng 3/2024):**
   - Tháng 3/2024 bị mất hoàn toàn từ nguồn cung cấp (335/366 ngày). Trạng thái: `OPEN_QUALITY_DEFECT`. Kế hoạch G6 sẽ chạy 2024 với cảnh báo partial coverage.
3. **Chính sách dữ liệu thời tiết FP-DEC-017:**
   - Dữ liệu thời tiết duy trì `CONDITIONAL_NO_GO`. Pipeline CORE tiếp tục cách ly tuyệt đối dữ liệu thời tiết.
4. **Ngoại lệ G2-EXC-001 (Đơn vị tính sơ bộ):**
   - Duy trì `ACTIVE` tại G5, sẽ chuyển thành `RESOLVED_BY_OPTION_B` đồng thời khi Project Lead ký quyết định D3.
5. **Ranh giới kỹ thuật PARQUET_PARITY_NOT_TESTED:**
   - Option B giới hạn đối soát ở tệp RAW CSV 2019 $\leftrightarrow$ BTS CSV. Không suy rộng sang tính chẵn lẻ của tệp Parquet 2019.

---

## 4. QUYẾT ĐỊNH CỦA PROJECT LEAD (PHÊ DUYỆT CHÍNH THỨC ĐÓNG CỔNG G5)

> [!NOTE]
> Project Lead chính thức phê duyệt đóng Gate G5 vào ngày 2026-10-21 theo chỉ thị rõ ràng:
> *"D4 — APPROVED: I approve closing Gate G5 as PASS (CONTROLLED), provided D1, D2, D3 and all 19 G5 exit criteria are validly satisfied."*
> Đồng thời xác nhận đầy đủ: D1 đã được chứng thực, D2 đã được phê duyệt, D3 đã đạt chuẩn và được phê duyệt, 19/19 tiêu chí kỹ thuật đã thỏa mãn.

1. **Xác nhận tiêu chí kỹ thuật:** Toàn bộ 19/19 tiêu chí nghiệm thu kỹ thuật Gate G5 đã được kiểm chứng và đạt chuẩn.
2. **Xác nhận rủi ro có kiểm soát:** Chấp thuận và bảo lưu danh mục 5 rủi ro và ngoại lệ tại Mục 3 (`OR-08`, `OR-05`, `FP-DEC-017`, `G2-EXC-001 = RESOLVED_BY_TS018_APPROVED_OPTION_B`, `PARQUET_PARITY_NOT_TESTED`).
3. **Quyết định đóng cổng Gate G5:**
   * **`D4 = APPROVED`**
   * **`GATE G5 = PASS (CONTROLLED)`**
   * **Gate G6:** Chuyển trạng thái sang **`READY_FOR_PREPARATION / BLOCKED_ON_D5`** (Tuyệt đối KHÔNG đánh dấu PASS; sẵn sàng cho các công tác chuẩn bị trước khởi động).
4. **CẢNH BÁO QUẢN TRỊ BẮT BUỘC:** Quyết định này và việc đóng Gate G5 **TUYỆT ĐỐI KHÔNG CẤP PHÉP KHỞI ĐỘNG CHẠY DỮ LIỆU SẢN XUẤT (Quyết định D5)**. Quyết định D5 tiếp tục giữ nghiêm ngặt trạng thái **`NOT_AUTHORIZED`**; Task T-012 tiếp tục giữ trạng thái **`NOT_STARTED`**.

- **Cơ sở ủy quyền:** Project Lead Explicit Authorization (2026-10-21)
- **Trạng thái chính thức:** **`PASS (CONTROLLED)`**
- **Thời điểm phê duyệt:** 2026-10-21
