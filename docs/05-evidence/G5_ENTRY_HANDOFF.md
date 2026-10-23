# G5-ENTRY-HANDOFF: Quy định Bàn giao, Điều kiện Tiên quyết & Kế hoạch Khởi động Gate G5 (T-010 & T-011)

**Mã tài liệu:** `G5-HANDOFF-20261018`  
**Dự án:** US Flight Performance Analysis 2016–2024  
**Cổng xuất phát:** `Gate G4 — PASS (CONTROLLED)`  
**Cổng đích:** `Gate G5 — Bounded Real Data Smoke, Resource Benchmark & BTS Unit Reconciliation`  
**Ngày lập:** `2026-10-18`  
**Trạng thái Cổng G5:** **`NOT_STARTED / ENTRY PREPARATION`**  
**Quyền hạn phê duyệt:** `Project Lead`  
**Cơ sở thẩm quyền:** `AGENTS.md`, `DATA_CONTRACT.md` (DC-11, DC-12), `DECISIONS.md`, `TEST_PLAN.md` (TS-014, TS-018), `G2-EXC-001`, `G3-COND-A/B/C`, `FP-DEC-017`

---

## 1. Mục tiêu và Phạm vi Cổng G5

Gate G5 đại diện cho bước chuyển đổi mang tính quyết định từ **kiểm thử synthetic tích hợp** sang **thực thi có kiểm soát trên dữ liệu thực tế** của một năm khảo sát đơn lẻ (năm 2016), nhằm đo lường khả năng chịu tải của hệ thống, kiểm chứng tính đúng đắn của hạch toán dòng trên dữ liệu thật, và hoàn thành nghĩa vụ đối chiếu đơn vị đo bắt buộc trước khi được phép chạy 9 năm tại Gate G6.

Gate G5 bao gồm hai nhiệm vụ cốt lõi:
1. **Nhiệm vụ `T-010` (Bounded Real-Data Smoke & Benchmark):**
   - Nạp dữ liệu thực tế năm 2016 (`data/raw/tabular/2016/flight_with_weather_2016.csv`, `5,617,658` dòng, `1,556,608,989` bytes).
   - Chạy pipeline Ingestion (`T-007`) và Quality Engine (`T-008`).
   - Xuất bản dữ liệu staging Parquet năm 2016 theo quy trình 7 bước an toàn của `SafePublisher`.
   - Thu thập và lập báo cáo benchmark tài nguyên thực tế (`TS-014`): thời gian chạy, đỉnh RAM driver/executor, CPU utilization, dung lượng đĩa và tỉ lệ nén Snappy.
2. **Nhiệm vụ `T-011` (KPI Sample, BTS Unit Parity & Fault Injection / Rollback):**
   - Tính toán thử nghiệm 8 CORE KPIs trên dữ liệu mẫu năm 2016 (`TS-008`, `TS-016`).
   - **Thực hiện nghĩa vụ bắt buộc `TS-018` theo ngoại lệ `G2-EXC-001`:** Đối chiếu trực tiếp bản ghi mẫu của 7 trường số đo CORE (`ARR_DELAY`, `DEP_DELAY`, `TAXI_OUT`, `TAXI_IN`, `AIR_TIME`, `ACTUAL_ELAPSED_TIME`, `CRS_ELAPSED_TIME`) với dữ liệu gốc BTS TranStats. **Nếu đối chiếu không khớp hoặc sai khác không giải thích được $\implies$ CHẶN TOÀN BỘ (`BLOCKED`) Gate G6 và cấm xuất bản**.
   - Diễn tập tiêm lỗi đĩa/mạng và kiểm chứng quy trình rollback tự động (`TS-013`).

---

## 2. Các Ràng buộc Quản trị Bắt buộc Phải Duy trì Tuyệt đối

Theo chính sách của dự án và các quyết định đã được Project Lead phê duyệt:

### 2.1 Rào chắn Sản xuất Bắt buộc (Production Hard Guard theo `G3-COND-A`)
Trước và trong suốt quá trình chạy `T-010`:
1. **Tuyệt đối không kích hoạt `allow_unapproved_policies=True`** trong cấu hình pipeline chạy dữ liệu thật. Cờ này chỉ dành riêng cho các kịch bản mô phỏng offline.
2. **Tuyệt đối không kích hoạt `quarantine_non_positive_flight_num=True`**.
3. Các chuyến bay có số hiệu không dương (`OP_CARRIER_FL_NUM <= 0`) **phải được giữ nguyên trạng thái `ACCEPTED`** kèm cờ cảnh báo `PROVISIONAL_FLIGHT_NUM_NON_POSITIVE_G3_COND_A`.
4. Nếu phát hiện DataFrame xuất phát từ chế độ mô phỏng bị chuyển sang luồng xuất bản sản xuất, hệ thống phải lập tức kích hoạt cơ chế `fail-closed`, từ chối cập nhật con trỏ `latest/` và hủy bỏ run.
5. Kiểm chứng các rào chắn này bằng kiểm thử tự động tại bước Preflight của G5.

### 2.2 Bảo tồn Rủi ro Mở và Trạng thái Quản trị Hiện hành
1. **`OR-05 = OPEN_QUALITY_DEFECT`:** Giữ nguyên trạng thái khuyết 31 ngày Tháng 3/2024 (`335/366` ngày, `source_coverage_status = PARTIAL`). Không tự tiện bù khuyết hoặc giả mạo dữ liệu. Nghiệm thu chính thức `TS-004` được bảo lưu tại Gate G6.
2. **`OR-08 = IDENTITY_UNVERIFIED`:** Các mã băm candidate SHA-256 trên 9 CSV nguồn giữ nguyên nhãn `CANDIDATE_PENDING_HUMAN_ACCEPTANCE`. Nghiệm thu `TS-019` tại Gate G5.
3. **`FP-DEC-017 = CONDITIONAL_NO_GO`:** Dữ liệu thời tiết tiếp tục bị loại khỏi phạm vi phân tích sản xuất. Thiếu thời tiết không được làm rơi dòng CORE.
4. **Hạch toán dòng `DC-11`:** Bắt buộc nghiệm thu cân bằng hạch toán chính xác tuyệt đối trên 5,617,658 dòng của năm 2016:
   $$\text{Raw Count } (5,617,658) = \text{Accepted} + \text{Quarantined} + \text{Rejected}$$

---

## 3. Ngân sách Tài nguyên trên Môi trường Windows Local (`Resource Budget`)

Hạ tầng PySpark thực thi trên máy trạm Windows local phải tuân thủ nghiêm ngặt cấu hình đã được phê duyệt tại `ARCHITECTURE.md` và `src/flight_pipeline/config/spark_config.py`:

| Tham số Cấu hình | Giá trị Chuẩn tắc | Mục đích và Giới hạn An toàn |
|---|---|---|
| `spark.master` | `local[4]` | Giới hạn 4 worker threads, tránh nghẽn I/O trên đĩa SSD/HDD Windows |
| `spark.driver.memory` | `4g` | Ngân sách bộ nhớ an toàn cho Driver PySpark |
| `spark.driver.memoryOverhead` | `1g` | Bộ đệm cho bộ nhớ JVM off-heap và Py4J serialization |
| `spark.sql.shuffle.partitions` | `16` | Giảm kích thước mỗi partition khi tính toán xáo trộn, tránh OOM |
| `spark.local.dir` | `D:/Study/Code/Apache/Flight_Analyzt/tmp_spark/` | Thư mục scratch tạm an toàn nằm ngoài repository checkout |
| `spark.sql.parquet.compression.codec` | `snappy` | Nén Snappy tiêu chuẩn, tối ưu hóa tốc độ giải nén và dung lượng |
| `spark.sql.session.timeZone` | `UTC` | Đơn định hóa múi giờ xử lý, tránh phụ thuộc múi giờ hệ điều hành |
| `spark.sql.execution.arrow.pyspark.enabled` | `true` | Tối ưu hóa chuyển đổi dữ liệu JVM-Python bằng Apache Arrow |
| Không gian đĩa khả dụng yêu cầu | $\ge 30\text{ GB}$ | Kiểm tra không gian trống trên ổ `D:` trước khi khởi động pipeline |

---

## 4. Kế hoạch Thực thi Bounded Smoke Năm 2016 (`T-010`)

Quá trình chạy `T-010` phải được thực hiện theo nguyên tắc tiệm tiến an toàn, có điểm dừng kiểm chứng độc lập ở từng pha:

```
[Pha 1: Preflight & Candidate Check]
               │
               ▼
[Pha 2: Micro-Smoke 1,000 dòng] ──(Verify Schema, Null Handling, Predicates)
               │
               ▼
[Pha 3: Month-Smoke Tháng 1/2016 (~445k dòng)] ──(Verify Memory, SafePublisher)
               │
               ▼
[Pha 4: Full-Year 2016 Run (5,617,658 dòng)] ──(Verify DC-11/12 Accounting & Benchmark)
               │
               ▼
[Pha 5: Resource Benchmark Report (TS-014)]
```

### Chi tiết các Pha Thực thi:
1. **Pha 1 (Preflight):**
   - Kiểm tra mã SHA-256 candidate của tệp nguồn năm 2016: `632d43e5898b1eb798363a02fa023eec7fa6d38e0ba8f368e7ec8396aa700540`.
   - Xác minh kích thước file: đúng `1,556,608,989` bytes.
   - Kiểm tra thư mục tạm `tmp_spark/` và quyền ghi.
2. **Pha 2 (Micro-Smoke 1,000 dòng):**
   - Đọc 1,000 dòng đầu tiên bằng `RawCsvReader`.
   - Kiểm chứng không phát sinh lỗi parse, StructType không bị biến dạng, các cột metric cast an toàn dưới ANSI mode.
3. **Pha 3 (Month-Smoke Tháng 1/2016):**
   - Lọc dữ liệu `FL_DATE` trong Tháng 1/2016 (~445,000 bản ghi).
   - Ghi Parquet vào staging bằng `SafePublisher`, kiểm chứng cơ chế atomic rename trên Windows NTFS.
4. **Pha 4 (Full-Year 2016 Run):**
   - Chạy toàn bộ 5,617,658 dòng năm 2016.
   - Kiểm chứng hạch toán 3 trạng thái DC-11 và 7 metric DC-12.
   - Kiểm tra con trỏ `latest/` và tính toàn vẹn của `RunManifest`.
5. **Pha 5 (Báo cáo Benchmark `TS-014`):**
   - Lập tài liệu báo cáo `T010_REAL_DATA_SMOKE_AND_BENCHMARK_REPORT.md` ghi nhận đầy đủ chỉ số tài nguyên.

---

## 5. Danh mục các Bước Cần Human Approval Riêng của Project Lead

Mỗi bước chuyển giao quan trọng trong Gate G5 bắt buộc phải có chỉ thị phê duyệt riêng bằng văn bản từ Project Lead trước khi thực hiện:

| Bước phê duyệt | Nội dung quyết định cần phê duyệt | Điều kiện tiên quyết |
|:---:|---|---|
| **Duyệt 1** | **Chỉ thị khởi động Gate G5 và cấp phép đọc tệp thật 2016** | Nghiệm thu Gate G4 đã ký; Preflight tài nguyên đĩa $\ge 30\text{ GB}$ |
| **Duyệt 2** | **Phê duyệt kết quả Micro-Smoke & Month-Smoke năm 2016** | Micro-smoke đạt 100% không lỗi; log bộ nhớ ổn định |
| **Duyệt 3** | **Phê duyệt kết quả chạy toàn bộ năm 2016 & Benchmark `TS-014` (`T-010`)** | Hạch toán DC-11 cân bằng tuyệt đối; RunManifest được niêm phong |
| **Duyệt 4** | **Phê duyệt kết quả đối chiếu mẫu BTS TranStats `TS-018` (`T-011`)** | 7 trường số đo CORE khớp chính xác với BTS; nếu không khớp thì dừng dự án |
| **Duyệt 5** | **Nghiệm thu chính thức Gate G5 và cho phép mở Gate G6** | T-010 và T-011 hoàn tất, không có bất kỳ rủi ro chưa giải quyết |

---

## 6. Cam kết Nghiêm ngặt (Strict Non-Execution Commitment)

Trong phiên thực thi hiện tại:
- **TUYỆT ĐỐI KHÔNG KHỞI ĐỘNG HOẶC TRIỂN KHAI NHIỆM VỤ T-010.**
- **TUYỆT ĐỐI KHÔNG DÙNG SPARK ĐỌC FULL TỆP CSV NĂM 2016.**
- Không tự ý chuyển trạng thái Gate G5 thành `IN_PROGRESS` hoặc `PASS`.
- Toàn bộ workspace được bảo toàn ở trạng thái chuẩn bị bàn giao sạch sẽ, ổn định và chờ chỉ thị tiếp theo từ Project Lead.
