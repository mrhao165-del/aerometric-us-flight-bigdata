# T011_FULL_RISK_AND_LIMITATION_REGISTER — SỔ ĐĂNG KÝ RỦI RO VÀ GIỚI HẠN KỸ THUẬT T-011

- **Mã nhiệm vụ:** `T-011` (Gate G5: KPI Sample Smoke, BTS Parity, TS-008, TS-013 & Review Packaging)
- **Gate:** `G5` (IN_PROGRESS)
- **Thời điểm kiểm toán:** 2026-10-18T21:04:50+07:00
- **Tiêu chuẩn tuân thủ:** [`AGENTS.md`](../../AGENTS.md), [`RISK_REGISTER.md`](../03-quality/RISK_REGISTER.md), [`TEST_PLAN.md`](../03-quality/TEST_PLAN.md).
- **Trạng thái:** **ACTIVE GOVERNANCE REGISTER**

---

## 1. DANH MỤC CÁC ĐIỂM NGHẼN VÀ RỦI RO HOẠT ĐỘNG (ACTIVE BLOCKERS & RISKS)

| Mã rủi ro | Phân loại | Tên rủi ro / Điểm nghẽn | Trạng thái hiện tại | Biện pháp kiểm soát & Tác động quản trị |
|:---:|---|---|:---:|---|
| **TS-018 / G2-EXC-001** | **MANDATORY HARD BLOCKER** | Thiếu dữ liệu mẫu BTS TranStats chính thức bên ngoài để xác minh đơn vị 7 trường đo CORE | **OPEN BLOCKER (Khóa cổng Gate G6)** | Reconciler đã hoàn thành; giữ 7 trường đo ở trạng thái `OFFICIAL_MINUTES_EMPIRICALLY_CONSISTENT_PROVISIONAL`; **cấm chạy full-run Gate G6** cho đến khi có dữ liệu thật. |
| **OR-05** | **QUALITY DEFECT** | Năm 2024 khuyết thiếu toàn bộ 31 ngày Tháng 3 (335/366 ngày quan sát) | **OPEN_QUALITY_DEFECT** | Tự động gán nhãn `source_coverage_status = PARTIAL` cho mọi nhóm dữ liệu 2024; cấm nội suy hoặc bù đắp giả mạo. |
| **OR-08** | **PROVENANCE LIMITATION** | Danh tính nguồn ngoài của 9 tệp raw CSV chưa được xác minh từ BTS | **IDENTITY_UNVERIFIED** | Giữ mã băm cục bộ ở trạng thái `CANDIDATE_PENDING_HUMAN_ACCEPTANCE`; không coi hash cục bộ là chứng thực nguồn ngoài. |
| **FP-DEC-017** | **SCOPE EXCLUSION** | Nhánh phân tích thời tiết tùy chọn (RQ-06 / KPI-10) chưa đủ điều kiện GO | **CONDITIONAL_NO_GO** | Giữ 6 cột thời tiết `O_TEMP..D_WSPD` là nullable; cấm loại bỏ chuyến bay CORE vì thiếu thời tiết; không tính KPI-10. |
| **FP-DEC-015** | **MATHEMATICAL LIMITATION** | Phân vị P50/P90 sử dụng xấp xỉ GK-sketch (accuracy=10000) | **RANK_ERROR_BOUNDED** | Đảm bảo sai số thứ hạng $\epsilon_{\text{rank}} \le 0.01\%$; không cam kết sai số tuyệt đối bằng số phút cố định cho mọi phân phối lệch. |
| **FP-DEC-016** | **STATISTICAL SUPPRESSION** | Cỡ mẫu nhỏ không đủ độ tin cậy để xếp hạng chính thức | **MIN_N_ENFORCED** | Áp dụng ngưỡng 1000 (hãng), 365 (sân bay), 100 (tuyến bay); gán nhãn `SUPPRESSED` khi $< \text{min-N}$ để loại khỏi xếp hạng. |
| **G3-COND-A** | **PROVISIONAL POLICY** | Chính sách cách ly chuyến bay có số hiệu không dương (`FL_NUM <= 0`) | **POLICY_GUARD_ACTIVE** | Duy trì `quarantine_non_positive_flight_num=False` trong sản xuất; mọi thử nghiệm phải thực hiện ngoài production. |
| **G3-COND-C** | **STORAGE CONCURRENCY** | Hệ thống tệp NTFS đơn máy chủ không hỗ trợ multi-writer phân tán | **SINGLE_WRITER_ENFORCED** | Sử dụng `SingleWriterLock` chặn tranh chấp ghi đồng thời; fail-closed khi có xung đột. |

---

## 2. KẾT LUẬN QUẢN TRỊ RỦI RO

Không có rủi ro mới nào phát sinh đe dọa tính toàn vẹn của dữ liệu hoặc tính đúng đắn của pipeline. Toàn bộ các rủi ro đã biết đều được kiểm soát và ghi nhận minh bạch theo đúng thẩm quyền tài phán.
