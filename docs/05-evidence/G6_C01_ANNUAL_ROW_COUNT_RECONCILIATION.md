# G6_C01_ANNUAL_ROW_COUNT_RECONCILIATION.md
# Báo Cáo Kiểm Toán Và Đối Chiếu Số Hàng Hàng Năm 9 Năm (2016–2024)

**Mã tài liệu:** `G6_C01_ANNUAL_ROW_COUNT_RECONCILIATION`  
**Dự án:** US Flight Performance Analysis 2016–2024  
**Nhiệm vụ:** T-012 — Nine-Year Pipeline Ingestion & Production Readiness  
**Gate quản trị:** Gate G5 = IN_PROGRESS, Gate G6 = NOT_STARTED / BLOCKED  
**Vai trò:** Principal Big Data Architect, Senior PySpark Engineer, Independent Data Quality Auditor  
**Ngày lập:** 2026-10-20  

---

## 1. NGUYÊN NHÂN GỐC RỄ CỦA SAI LỆCH PHÂN BỔ HÀNG (ROOT CAUSE ANALYSIS)

Independent Reviewer phát hiện danh mục `G6_T012_CANONICAL_SOURCE_INVENTORY.md` trước đây có sự sai lệch phân bổ số dòng từng năm giai đoạn 2017–2024 so với báo cáo kiểm chuẩn `T004_FINAL_QA_RECONCILIATION.md`, mặc dù tổng số dòng 9 năm đều bằng đúng **54.674.003 dòng**.

### Phân tích điều tra:
1. **Nguồn gốc số liệu lỗi:**
   - Trong giai đoạn lập kế hoạch T-007 (`T007_02_ENTRY_PREPARATION.md`), một bảng ước tính trước nạp (*pre-ingestion planning estimate*) đã phân bổ số dòng tạm thời giữa các năm 2017–2024 (ví dụ 2024 ước tính 3.633.696 dòng, 2017 ước tính 5.677.153 dòng...).
   - Bảng ước tính này từng bị sao chép nhầm vào `T007_FINAL_SIGNOFF_DOCUMENTATION_ERRATA.md`, sau đó đã được đính chính dứt điểm bởi văn bản quản trị [`T008_ENTRY_SOURCE_INVENTORY_RECONCILIATION.md`](./T008_ENTRY_SOURCE_INVENTORY_RECONCILIATION.md).
   - Khi soạn thảo `G6_T012_CANONICAL_SOURCE_INVENTORY.md`, bảng số dòng lỗi thời này lại vô tình được đưa vào, dẫn đến sự phân bổ sai lệch giữa các năm 2017–2024.
2. **Kiểm tra tổng (Aggregate Check Blindness):**
   - Do tổng của 9 số ước tính cũ vẫn bằng chính xác $54,674,003$ dòng và tổng dung lượng vẫn bằng chính xác $15,196,366,173$ bytes, các lệnh kiểm tra mức tổng quát (`sum(rows) == 54674003`) đã không phát hiện được sự lệch pha từng năm.
3. **Bằng chứng vật lý độc lập:**
   - Quá trình kiểm toán streaming bounded-memory thực tế trên toàn bộ 9 tệp CSV thô tại `data/raw/tabular/` khẳng định tuyệt đối: **Các tệp CSV thô vật lý hoàn toàn nguyên vẹn, khớp 100% với `inputs/schema_YYYY.json`, `AUDITED_SOURCE_INVENTORY` trong `source_validator.py`, và `T004_FINAL_QA_RECONCILIATION.md`**.

---

## 2. KẾT QUẢ KIỂM TOÁN VẬT LÝ STREAMING BOUNDED-MEMORY (100% VERIFIED)

Kiểm toán trực tiếp từng byte nhị phân của 9 tệp dữ liệu thô bằng thuật toán đọc đệm giới hạn 1 MiB (không nạp toàn bộ vào RAM), đếm ký tự ngắt dòng `\n` và tính mã băm SHA-256:

| Năm | Đường dẫn tệp vật lý | Dung lượng byte thực tế | Số dòng vật lý (Lines) | Header | Số dòng dữ liệu (Data Rows) | Mã băm SHA-256 vật lý thực tế | Thời gian đọc luồng |
| :---: | :--- | :---: | :---: | :---: | :---: | :--- | :---: |
| **2016** | `data/raw/tabular/2016/flight_with_weather_2016.csv` | `1,538,427,452` | $5,537,988$ | 1 | **$5,537,987$** | `4ed92ed732721a38ae28325135fad63436347613674ad96c1b273eb9d44cef34` | 1.8s |
| **2017** | `data/raw/tabular/2017/flight_with_weather_2017.csv` | `1,549,837,485` | $5,575,873$ | 1 | **$5,575,872$** | `67b8dbd6678576b1a2229ef2dbeec065e0f64d31d688ab8a2ca59c88d2a656f9` | 1.8s |
| **2018** | `data/raw/tabular/2018/flight_with_weather_2018.csv` | `1,941,406,432` | $6,986,843$ | 1 | **$6,986,842$** | `0398bab8f1b79a5f3bea628b707e18c3af628f37a1daa52de6849fb8bdfc71a3` | 2.3s |
| **2019** | `data/raw/tabular/2019/flight_with_weather_2019.csv` | `1,990,370,667` | $7,161,828$ | 1 | **$7,161,827$** | `eec50211a1a63f37b840977be5ab2e99a008a8d5234c2a12df8eb50862f93b4a` | 2.3s |
| **2020** | `data/raw/tabular/2020/flight_with_weather_2020.csv` | `1,197,858,795` | $4,312,092$ | 1 | **$4,312,091$** | `787981046c9fe0f4884ac207a3d28ea6a7fae98e89535cb9f8a37debb5c7fa5d` | 1.4s |
| **2021** | `data/raw/tabular/2021/flight_with_weather_2021.csv` | `1,600,032,487` | $5,755,667$ | 1 | **$5,755,666$** | `5b7cc4801a6ff5cf432137632209ebd7aecd3d4a0f83e8920e3525116e88defc` | 1.9s |
| **2022** | `data/raw/tabular/2022/flight_with_weather_2022.csv` | `1,782,648,882` | $6,413,417$ | 1 | **$6,413,416$** | `45eb45e801d6eeeb16167306fc69a8449177191cfff29bfb5d22285827f53140` | 2.3s |
| **2023** | `data/raw/tabular/2023/flight_with_weather_2023.csv` | `1,847,433,387` | $6,645,462$ | 1 | **$6,645,461$** | `9c9e20f55d3dd10a127bcdd28680df6547a01a82ad71999b794aff3e1075d7bd` | 2.1s |
| **2024** | `data/raw/tabular/2024/flight_with_weather_2024.csv` | `1,748,350,586` | $6,284,842$ | 1 | **$6,284,841$** | `f938ade95a031088467ab5e75abea2021e541eaf4a4288e564066e100541d5f7` | 2.0s |
| **TỔNG** | **Toàn bộ 9 năm khảo sát** | **`15,196,366,173`** | **$54,674,012$** | **9** | **$54,674,003$** | **Khớp 100% với baseline T-004 & T-008** | **17.9s** |

---

## 3. ĐỐI CHIẾU THỰC TẾ NĂM 2024 VÀ RỦI RO OR-05

1. **Số lượng dòng thực tế năm 2024:**
   - Năm 2024 có đúng **$6,284,841$ dòng dữ liệu** (không phải 3.633.696 dòng như ước tính sơ khai).
   - Tệp CSV năm 2024 gồm $1,748,350,586$ bytes và SHA-256: `f938ade95a031088467ab5e75abea2021e541eaf4a4288e564066e100541d5f7`.
2. **Hiện trạng độ bao phủ ngày lịch (Calendar Coverage):**
   - Như đã kiểm toán tại [`T004_2024_DATE_COVERAGE_AUDIT.md`](./T004_2024_DATE_COVERAGE_AUDIT.md), năm 2024 chứa dữ liệu của **11 tháng với đúng 335 ngày phân biệt**.
   - **Tháng 3/2024 hoàn toàn vắng mặt** ($0$ chuyến bay từ `2024-03-01` đến `2024-03-31`).
   - Có đầy đủ ngày nhuận `2024-02-29` với $18,642$ chuyến bay.
3. **Chính sách quản trị:**
   - Giữ nguyên rủi ro **`OR-05: OPEN_QUALITY_DEFECT`**.
   - Tuyệt đối **không nội suy hoặc chế tạo bản ghi giả** cho tháng 3/2024.
   - Gắn nhãn `source_coverage_status = PARTIAL` cho mọi tổng hợp của năm 2024.

---

## 4. KẾT LUẬN VÀ QUYẾT ĐỊNH ĐỒNG BỘ HÓA

- **Đồng bộ hóa toàn diện:** Danh mục `G6_T012_CANONICAL_SOURCE_INVENTORY.md`, kế hoạch `G6_T012_FULL_RUN_ENTRY_PLAN.md`, và danh mục kiểm tra `G6_T012_FINAL_EXECUTION_CHECKLIST_V2.md` được điều chỉnh theo đúng số liệu vật lý tại Bảng ở Mục 2.
- **Quy tắc kiểm thử hồi quy:** Mọi bài kiểm tra tự động phải xác thực từng năm độc lập, cấm chỉ kiểm tra tổng số dòng cộng dồn.
