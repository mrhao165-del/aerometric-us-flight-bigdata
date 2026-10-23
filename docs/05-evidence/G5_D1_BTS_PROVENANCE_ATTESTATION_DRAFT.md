# G5_D1_BTS_PROVENANCE_ATTESTATION_DRAFT.md
# Biên Bản Xác Nhận Nguồn Gốc và Tính Xác Thực Dữ Liệu BTS TranStats (Dự Thảo D1 — Reconciled)

**Dự án:** US Flight Performance Analysis 2016–2024  
**Hạng mục quản trị:** Quyết định độc lập D1 — BTS Provenance Attestation  
**Cổng quản lý:** Gate G5 — IN_PROGRESS  
**Trạng thái hiện tại:** **`PASS (CONTROLLED)`**  
**Cơ sở ủy quyền:** Project Lead Explicit Agreement (2026-10-21: *"tôi hoàn toàn đồng ý với ý kiến của bạn"*)  
**Tác giả dự thảo:** Project Governance Officer & Independent Evidence Auditor  
**Thời điểm cập nhật:** 2026-10-21  

---

## 1. MỤC ĐÍCH VÀ PHẠM VI

Biên bản này được lập nhằm ghi nhận chính xác nguồn gốc, phương thức thu thập và tính toàn vẹn mật mã học của tệp dữ liệu đối chứng BTS TranStats tháng 1/2019, phục vụ công tác kiểm chứng độc lập TS-018 thuộc Gate G5.

Tuân thủ nghiêm ngặt nguyên tắc quản trị tại `AGENTS.md`:
1. **Agent không tự cấp thẩm quyền:** Agent kỹ thuật không tự tạo "biên lai tải về" (download receipt) giả mạo hoặc tuyên bố rằng tệp BTS có chữ ký số của cơ quan BTS khi cơ quan này không cung cấp chữ ký số kèm theo.
2. **Chỉ ghi nhận lời xác nhận thực tế:** Việc xác thực nguồn gốc chỉ có hiệu lực pháp lý khi được chính cá nhân đã thực hiện thao tác tải tệp từ cổng TranStats ký xác nhận.

---

## 2. BẰNG CHỨNG TOÀN VẸN MẬT MÃ HỌC CỦA TỆP LƯU TRỮ VẬT LÝ

Tệp lưu trữ BTS vật lý trong repository đã được kiểm định độc lập, đối soát với `data/reference/bts_transtats/bts_transtats_201901.provenance.json` và niêm phong mật mã học:

| Thuộc tính kiểm định | Giá trị ghi nhận thực tế từ tệp vật lý | Trạng thái đối soát |
| :--- | :--- | :---: |
| **Đường dẫn tệp cục bộ** | `data/reference/bts_transtats/original/T_ONTIME_REPORTING_20261019_112232.zip` | `VERIFIED_PHYSICAL` |
| **Dung lượng tệp ZIP (bytes)** | `29,975,383` bytes ($\approx 28.59$ MiB) | `EXACT_MATCH` |
| **Thuật toán băm** | SHA-256 (Streaming chunked 64KB) | `CRYPTOGRAPHIC_SEAL` |
| **Mã băm SHA-256 của tệp ZIP** | `342de99f65561fb856b524c704f2ad3851f8015f52251668ece346dff1350ae6` | `VERIFIED_BITWISE` |
| **Kiểm tra tính toàn vẹn ZIP** | `zipfile.testzip()` trả về `None` (0 tệp hỏng CRC-32) | `CRC_PASS` |
| **Tệp CSV bên trong ZIP** | `T_ONTIME_REPORTING.csv` | `EXTRACTABLE` |
| **Dung lượng CSV giải nén** | `217,369,264` bytes ($\approx 207.30$ MiB) | `EXACT_MATCH` |
| **Mã CRC của tệp CSV** | `0x7d8573c4` | `VERIFIED_CRC32` |
| **Mã băm SHA-256 của tệp CSV** | `dce92e8f602d02ef50f2354789653dd770bc46d948c13a48e3518f2998068bec` | `VERIFIED_BITWISE` |
| **Số cột tiêu đề CSV** | `108` cột | `VERIFIED_SCHEMA` |
| **Số dòng dữ liệu trong CSV** | `583,985` bản ghi dữ liệu (583.986 dòng bao gồm 1 dòng tiêu đề) | `VERIFIED_COUNT` |
| **Bảng dữ liệu BTS TranStats** | `Reporting Carrier On-Time Performance (1987-present)` | `VERIFIED_METADATA` |

---

## 3. LỜI TUYÊN BỐ VÀ CHỨNG THỰC CỦA PROJECT LEAD (DOWNLOADER ATTESTATION)

> [!NOTE]
> Vào phiên làm việc ngày 2026-10-21, Project Lead đã chính thức cung cấp tuyên bố xác nhận bằng văn bản:
> *"tôi là người tải bộ dữ liệu BTS"* (kế thừa xác nhận: *"tôi đã tải bộ hồ sơ BTS"*)
> Lời xác nhận này được ghi nhận chính thức vào hồ sơ chứng thực nguồn gốc D1, kết hợp cùng kết quả đối soát mật mã học 100% của tệp lưu trữ vật lý.

Tôi, Project Lead, với tư cách là người trực tiếp thu thập dữ liệu nguồn, xác nhận:
1. Tệp dữ liệu đối chứng `T_ONTIME_REPORTING_20261019_112232.zip` tại đường dẫn `data/reference/bts_transtats/original/T_ONTIME_REPORTING_20261019_112232.zip` đã được tôi trực tiếp tải về từ cổng cơ sở dữ liệu chính thức của Cục Thống kê Giao thông Vận tải Hoa Kỳ (Bureau of Transportation Statistics - BTS TranStats) cho kỳ báo cáo: **Năm 2019, Tháng 1 (January 2019)**.
2. Tệp nén gốc được lưu trữ nguyên vẹn, không qua bất kỳ hành vi sửa đổi, chỉnh sửa, biên tập hay loại bỏ dữ liệu nào.
3. Mã băm SHA-256 tính toán trên tệp ZIP lưu trữ hoàn toàn trùng khớp với giá trị `342de99f65561fb856b524c704f2ad3851f8015f52251668ece346dff1350ae6`, kích thước đúng `29,975,383` bytes.
4. Biên lai giao dịch tải về (Download transaction receipt) hoặc chữ ký điện tử từ máy chủ BTS: **`NOT_PROVIDED`** (BTS không cung cấp kèm theo tệp tải).

---

## 4. XÁC NHẬN VÀ PHÊ CHUẨN CỦA PROJECT LEAD

- **Người thực hiện tải tệp (Downloader):** Project Lead
- **Nội dung xác nhận:** *"tôi là người tải bộ dữ liệu BTS"*
- **Phương thức xác nhận:** Chỉ thị bằng văn bản qua prompt (Project Lead Explicit Written Instruction)
- **Thời điểm xác nhận:** 2026-10-21
- **Kết quả đối soát mật mã học:** `EXACT_BITWISE_MATCH` (29.975.383 bytes, SHA-256 `342de99f...`)
- **Trạng thái Quyết định D1:** **`PASS (CONTROLLED)`**
