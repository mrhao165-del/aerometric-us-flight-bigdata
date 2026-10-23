# G5_D1_D4_CORRECTED_DRAFT_RECONCILIATION.md
# Báo Cáo Đối Soát và Khắc Phục Sai Lệch Bốn Hồ Sơ Dự Thảo Nghiệm Thu G5 (P01 – P07)

**Dự án:** US Flight Performance Analysis 2016–2024  
**Hạng mục:** Targeted Governance & Operational Contract Reconciliation  
**Gate quản lý:** Gate G5 = IN_PROGRESS, Gate G6 = NOT_STARTED / BLOCKED  
**Tác giả:** Principal Big Data Engineer, Independent Forensic Auditor, PySpark Release Engineer  
**Thời điểm lập:** 2026-10-20  

---

## 1. MỤC ĐÍCH VÀ NGUYÊN TẮC QUẢN TRỊ

Báo cáo này tổng hợp kết quả điều tra độc lập, tái hiện và khắc phục triệt để bảy nhóm phát hiện (Findings P01 – P07) do Independent Reviewer xác định trong bốn dự thảo nghiệm thu Gate G5 (`G5_D1` đến `G5_D4`) và các tài liệu kế hoạch vận hành Gate G6 / Task T-012.

**Nguyên tắc thẩm quyền bắt buộc:**
- Hoạt động này là **hiệu chỉnh kỹ thuật có mục tiêu (targeted technical correction)** trên các bản DRAFT, tuyệt đối không tạo thêm vòng kiểm toán lại TS-018 khi bằng chứng cũ còn nguyên vẹn.
- Không tự ý phê duyệt các quyết định D1, D2, D3, D4 hoặc D5.
- Không chạy bất kỳ năm dữ liệu nào của pipeline T-012, không ghi Parquet mới, không thay đổi con trỏ xuất bản hay tệp đánh dấu phục hồi.

---

## 2. BẢNG TỔNG HỢP KHẮC PHỤC BẢY NHÓM PHÁT HIỆN (P01 – P07)

| Mã phát hiện | Hạng mục bị ảnh hưởng | Nguyên nhân sai lệch | Biện pháp kỹ thuật đã khắc phục | Trạng thái kỹ thuật |
| :---: | :--- | :--- | :--- | :---: |
| **P01** | `G5_D1` BTS Provenance Attestation | Ghi nhầm dung lượng ZIP (18,8 MB thay vì 29,97 MB), dung lượng CSV (233 MB thay vì 217 MB), và nhầm tên bảng `Marketing Carrier` | Đối soát trực tiếp tệp vật lý và `bts_transtats_201901.provenance.json`: Cập nhật đúng ZIP bytes = **29,975,383**, CSV uncompressed = **217,369,264**, bảng = **`Reporting Carrier On-Time Performance (1987-present)`**, 583.985 bản ghi, CRC = `0x7d8573c4`. Ghi nhận biên lai/chữ ký BTS = `NOT_PROVIDED`. | `RECONCILED_PASS` |
| **P02** | `G6_T012_READINESS_CHECKLIST.md` (P-06) | Sử dụng lệnh kiểm tra con trỏ `--allow-uninitialized` để suy luận hệ thống không có active writer | Tách bạch hoàn toàn `POINTER_STATE` và `WRITER_LOCK_STATE`. Bổ sung kiểm thử hồi quy tiêu cực chứng minh con trỏ chưa khởi tạo nhưng có lock/marker thì tuyệt đối không an toàn để khởi chạy writer. | `RECONCILED_PASS` |
| **P03** | `G6_T012_FULL_RUN_ENTRY_PLAN.md` | Sử dụng mã băm 2016 cũ (`632d43e5...`) đã bị bác bỏ bởi `G5_T010_ENTRY_BASELINE_ERRATA.md` | Cập nhật chính xác mã băm canonical candidate 2016: **`4ed92ed732721a38ae28325135fad63436347613674ad96c1b273eb9d44cef34`** (1.538.427.452 bytes, 5.537.987 hàng). | `RECONCILED_PASS` |
| **P04** | Chiến lược Baseline 2016 và 9 năm dữ liệu | Tài liệu chưa thống nhất giữa việc chạy full 9 năm hay chạy 8 năm kế thừa 2016 | Xác nhận 50 Parquet staging 2016 của T-010 là bất biến. Lập đề xuất kiến trúc (Phương án A: Thăng hạng Parquet 2016 vs Phương án B: Chạy thống nhất 2016 mới) trình Project Lead quyết định. | `RECONCILED_PASS` |
| **P05** | `G5_D4` G5 Human Gate Signoff | Trộn lẫn đơn vị tính GB và GiB (viết 57,90 GiB / 19,86 GB = 2,91x); chưa cập nhật số lượng assertion 1.569 | Thống nhất đơn vị đo lường: Dung lượng trống = **57.90 GiB** (62.17 GB), Ngân sách = **18.50 GiB** (19.86 GB), Hệ số an toàn chuẩn = **3.13x**. Cập nhật số assertion mới = 1.569; định danh rõ 5 rủi ro tồn đọng. | `RECONCILED_PASS` |
| **P06** | Hợp đồng đường dẫn `SafePublisher` | Tài liệu G6 mô tả đường dẫn không khớp với mã nguồn (như `staging/active/<year>/latest`) | Chuẩn hóa toàn bộ đường dẫn theo mã nguồn: `staging/<run_id>`, `curated/runs/<run_id>`, `curated/latest_run_id.txt`, `metadata/<run_id>/run_manifest.json`. | `RECONCILED_PASS` |
| **P07** | Ranh giới kiểm tra Parquet SHA-256 | Tuyên bố quá mức rằng pointer verifier kiểm tra SHA-256 của toàn bộ Parquet | Đính chính: `verify_staging_pointer.py` chỉ kiểm tra Parquet magic bytes `b'PAR1'` và parse Thrift metadata. Việc đối soát SHA-256 toàn bộ thuộc về công cụ chuyên dụng đối soát manifest. | `RECONCILED_PASS` |

---

## 3. CHI TIẾT TỪNG PHÁT HIỆN VÀ BIỆN PHÁP KHẮC PHỤC

### 3.1. Finding P01 — Chuẩn hóa thông tin vật lý tệp BTS trong Dự thảo D1
- **Tệp nguồn vật lý:** `data/reference/bts_transtats/original/T_ONTIME_REPORTING_20261019_112232.zip`
- **Kết quả đo lường trực tiếp:**
  * Kích thước ZIP: **29,975,383 bytes** (khớp chính xác thuộc tính hệ thống và băm SHA-256 `342de99f65561fb856b524c704f2ad3851f8015f52251668ece346dff1350ae6`).
  * Tệp CSV bên trong: `T_ONTIME_REPORTING.csv`.
  * Kích thước giải nén: **217,369,264 bytes**.
  * Mã CRC-32: `0x7d8573c4`.
  * Số dòng dữ liệu: **583,985** dòng dữ liệu (+ 1 dòng tiêu đề = 583.986 dòng).
  * Tên bảng chính thức: **`Reporting Carrier On-Time Performance (1987-present)`** (được đối soát theo `bts_transtats_201901.provenance.json`).
- **Nghiêm cấm:** Không tự bịa đặt biên lai tải về hay chữ ký số của BTS khi nguồn dữ liệu công khai của chính phủ không cấp kèm các thành phần này.

### 3.2. Finding P02 — Tách bạch độc lập trạng thái con trỏ và trạng thái khóa
- **Nguyên lý:** Tệp con trỏ `latest_run_id.txt` thuộc phạm vi quản lý của `SafePublisher` (phục vụ người đọc và chỉ dẫn phiên bản xuất bản mới nhất). Tệp khóa `.pipeline.lock` thuộc phạm vi quản lý của `SingleWriterLock` (phục vụ an toàn loại trừ tương hỗ giữa các tiến trình ghi).
- **Hành động:**
  1. Trong [`G6_T012_READINESS_CHECKLIST.md`](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/docs/05-evidence/G6_T012_READINESS_CHECKLIST.md), tách tiêu chí P-06 thành:
     * **P-06a:** `POINTER_STATE` — kiểm tra con trỏ chỉ đọc.
     * **P-06b:** `WRITER_LOCK_STATE` — kiểm tra độc lập trạng thái khóa qua siêu dữ liệu `LockMetadata`, trạng thái sống còn PID (`get_pid_liveness`), và quét các artifact phục hồi (`get_unresolved_recovery_artifacts`).
  2. Bổ sung bộ kiểm thử hồi quy độc lập [`tests/test_lock_state_vs_pointer_state.py`](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/tests/test_lock_state_vs_pointer_state.py) gồm 3 ca kiểm thử:
     * `test_p02_negative_uninitialized_pointer_with_active_lock_is_not_safe`: Chặn False-PASS khi con trỏ rỗng nhưng có tiến trình sống giữ khóa.
     * `test_p02_negative_uninitialized_pointer_with_recovery_artifact_is_not_safe`: Chặn khởi chạy khi có tệp phục hồi dở dang (`UnresolvedRecoveryStateError`).
     * `test_p02_dead_pid_does_not_authorize_auto_deletion`: Khẳng định việc phát hiện PID chết không cho phép tự động xóa khóa nếu thiếu quy trình phục hồi có kiểm soát.

### 3.3. Finding P03 — Đính chính mã băm 2016 Canonical Candidate
- **Căn cứ lịch sử:** Văn bản [`G5_T010_ENTRY_BASELINE_ERRATA.md`](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/docs/05-evidence/G5_T010_ENTRY_BASELINE_ERRATA.md) đã chính thức bác bỏ mã băm cũ `632d43e5...` và thiết lập mã băm streaming canonical candidate cho tệp `data/raw/tabular/2016/flight_with_weather_2016.csv`.
- **Hành động:** Đã cập nhật dòng 33 tệp [`G6_T012_FULL_RUN_ENTRY_PLAN.md`](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/docs/05-evidence/G6_T012_FULL_RUN_ENTRY_PLAN.md) thành:
  * Kích thước: `1,538,427,452` bytes.
  * SHA-256: `4ed92ed732721a38ae28325135fad63436347613674ad96c1b273eb9d44cef34`.
  * Không sửa đổi các hồ sơ niêm phong lịch sử.

### 3.4. Finding P04 — Thống nhất chiến lược tích hợp Baseline 2016
- **Thực trạng:** T-010 đã xử lý trọn vẹn năm 2016 trên dữ liệu thật (5.537.987 hàng, đạt cân bằng DC-11 và dấu vân tay lược đồ `b5805fca...`). 50 tệp Parquet staging hiện được lưu giữ tại `D:\Study\Code\Apache\Flight_Analyzt\staging\`.
- **Giải pháp:** Thiết lập báo cáo đề xuất kiến trúc [`G6_T012_2016_BASELINE_INTEGRATION_DECISION_DRAFT.md`](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/docs/05-evidence/G6_T012_2016_BASELINE_INTEGRATION_DECISION_DRAFT.md) trình Project Lead xem xét, bảo đảm dữ liệu của toàn bộ 9 năm (2016–2024) đều có thể được truy vấn đồng thời trong Curated Storage mà không phá vỡ tính bất biến của baseline T-010.

### 3.5. Finding P05 — Nhất quán số liệu và đơn vị đo lường trong Dự thảo D4
- **Đính chính số học:**
  * Dung lượng đĩa Drive D trống đo thực tế: `62,174,007,296` bytes.
    - Đơn vị nhị phân: **`57.90 GiB`**.
    - Đơn vị thập phân: **`62.17 GB`**.
  * Ngân sách đĩa tối đa cho T-012:
    - Đơn vị nhị phân: **`18.50 GiB`**.
    - Đơn vị thập phân: **`19.86 GB`**.
  * Hệ số an toàn (Safety Multiplier) nhất quán:
    - Nhị phân: $57.90\text{ GiB} / 18.50\text{ GiB} = \mathbf{3.13\times}$.
    - Thập phân: $62.17\text{ GB} / 19.86\text{ GB} = \mathbf{3.13\times}$.
  * Số lượng khẳng định nhất quán: TS-018 lịch sử = 1.545; Phiên rà soát vận hành G6 mới = **1.569/1.569**.
  * Danh mục rủi ro tồn đọng: Định danh rõ ràng 5 rủi ro và giới hạn phạm vi: `OR-08`, `OR-05`, `FP-DEC-017`, `G2-EXC-001`, và `PARQUET_PARITY_NOT_TESTED`.

### 3.6. Finding P06/P07 — Chuẩn hóa hợp đồng đường dẫn xuất bản và ranh giới kiểm tra Parquet
- **Đường dẫn chuẩn hóa:**
  * `base_data_dir`: Thư mục gốc do cấu hình chỉ định (ví dụ `D:/Study/Code/Apache/Flight_Analyzt/data` hoặc thư mục làm việc).
  * Staging: `<base_data_dir>/staging/<run_id>`.
  * Curated Runs: `<base_data_dir>/curated/runs/<run_id>`.
  * Pointer file: `<base_data_dir>/curated/latest_run_id.txt`.
  * Metadata & Manifest: `<base_data_dir>/metadata/<run_id>/run_manifest.json`.
- **Ranh giới công cụ:** Công cụ `tools/qa/verify_staging_pointer.py` được xác định rõ là công cụ kiểm tra con trỏ và tính hợp lệ cú pháp Parquet (magic bytes và metadata footer), không thay thế cho công cụ đối soát toàn bộ SHA-256 từng dòng dữ liệu.

---

## 4. KẾT LUẬN VÀ TRẠNG THÁI HIỆN THỜI

Tất cả bảy nhóm phát hiện P01 – P07 đã được xử lý triệt để, bảo đảm tính trung thực tuyệt đối giữa mã nguồn, dữ liệu vật lý và hồ sơ quản trị. 

Các dự thảo `G5_D1`, `G5_D2`, `G5_D3`, `G5_D4` đã được chuẩn hóa và sẵn sàng chuyển giao cho Project Lead xem xét độc lập.
