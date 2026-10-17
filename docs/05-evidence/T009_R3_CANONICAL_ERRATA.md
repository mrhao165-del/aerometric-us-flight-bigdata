# T009-R3: CANONICAL CONTRACT ERRATA & DEFINITION RECONCILIATION

**Task ID:** `T-009` (Remediation R3)  
**Gate:** `G4`  
**Auditor:** Repository Governance Engineer & Lead QA Auditor  
**Execution Mode:** `CONTROLLED TARGETED REMEDIATION`  
**Date:** 2026-10-17  
**Status:** `ERRATA_OFFICIALLY_RECORDED`  

---

## 1. Bảng Đính Chính Định Nghĩa & Phân Định Ranh Giới Chuẩn Tắc

Bảng dưới đây đính chính chính thức các sai lệch trong các văn bản presignoff trước đó so với tài liệu chuẩn tắc được phê duyệt:

| Mã Chuẩn Tắc | Định Nghĩa Sai Trong Văn Bản Cũ | Định Nghĩa Chuẩn Tắc Bắt Buộc | Tài Liệu Nguồn Căn Cứ |
|:---:|---|---|---|
| **TS-009** | Bị nhầm là kiểm tra cấu hình Spark môi trường | **Kiểm tra ranh giới schema nạp liệu (Schema Boundary Guard):** bảo vệ 34 cột thô, cấm cột chế tạo (FLIGHTS), cấm bộ lọc CANCELLED/DIVERTED, và coi thời tiết là tùy chọn. Nghiệm thu tại T-007 (Gate G4). | [`TEST_PLAN.md`](../03-quality/TEST_PLAN.md#L65-L80) |
| **TS-013** | Báo cáo là đã PASS chính thức tại G4 | **Kiểm tra mô phỏng sự cố & phục hồi (Fault Injection & Recovery):** Chỉ mới kiểm thử mô phỏng cấp độ đơn vị (unit simulation); nghiệm thu vận hành chính thức trên toàn bộ dữ liệu thuộc Gate G5. | [`TEST_PLAN.md`](../03-quality/TEST_PLAN.md#L95-L110) |
| **TS-014** | Bị nhầm là kiểm tra lũy đẳng đơn thuần | **Kiểm tra tài nguyên & kiểm chuẩn hiệu năng (Resource & Benchmark):** Giám sát bộ nhớ driver $\le 4\text{GB}$ và thời gian thực thi trên toàn bộ 54.7M hàng. Thuộc Gate G5/G6. | [`TEST_PLAN.md`](../03-quality/TEST_PLAN.md#L115-L130) |
| **TS-018** | Bị nhầm là kiểm tra độ chính xác của unit test | **Kiểm tra xác thực đơn vị, dấu và miền của 7 thước đo liên tục CORE trên 54.7M dòng:** Đã được hoãn lại (deferred) có bảo lưu sang Gate G5 theo phê duyệt G2/G3; cấm tự ý công bố PASS tại G4. | [`TEST_PLAN.md`](../03-quality/TEST_PLAN.md#L145-L160) |
| **FP-DEC-017**| Bị mô tả chung chung là quyết định dữ liệu | **Quyết định thời tiết tùy chọn (Weather Conditional No-Go):** Dữ liệu thời tiết là tùy chọn; không được chặn tiến độ của pipeline CORE chuyến bay vì nhánh thời tiết chưa GO. | [`DECISIONS.md`](../02-design/DECISIONS.md#L120-L140) |
| **Git Revert** | `git revert --no-commit cda19fb..HEAD` | **Cú pháp chuẩn xác hoàn nguyên về baseline `be1b81e`:** `git revert --no-commit be1b81e..HEAD` (hoặc `cda19fb^..HEAD`), vì dải `A..B` loại trừ commit A. | Git Revision Syntax Specification |

---

## 2. Cam Kết Bảo Lưu Quản Trị Cốt Lõi

1. **Bảo tồn nguyên trạng dữ liệu và lịch sử:** Tuyệt đối không xóa dữ liệu thô, không sửa đổi các báo cáo kiểm toán lịch sử mà chỉ ban hành phụ lục đính chính mới.
2. **Không tự ý mở rộng phạm vi:** Mọi quyết định thiết kế ngoài phạm vi T-009 phải được trình Project Lead phê duyệt trước khi lập trình.
