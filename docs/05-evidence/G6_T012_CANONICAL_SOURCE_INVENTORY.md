# G6_T012_CANONICAL_SOURCE_INVENTORY.md
# Danh Mục Nguồn Dữ Liệu Thô 9 Năm Chuẩn Hóa và Bảng Băm Mật Mã Học (Canonical Source Inventory)

**Dự án:** US Flight Performance Analysis 2016–2024  
**Nhiệm vụ:** T-012 — Nine-Year Pipeline Ingestion & Production Readiness  
**Gate quản trị:** Gate G5 = IN_PROGRESS, Gate G6 = NOT_STARTED / BLOCKED  
**Tác giả:** Principal Big Data Architect, Senior PySpark Engineer, Independent Data Quality Auditor  
**Thời điểm lập:** 2026-10-20 (Đã đồng bộ hóa theo `G6_C01_ANNUAL_ROW_COUNT_RECONCILIATION.md`)  

---

## 1. MỤC ĐÍCH VÀ NGUYÊN TẮC BẢO TOÀN DỮ LIỆU

Tài liệu này xác lập danh mục chuẩn hóa duy nhất (Single Source of Truth) cho toàn bộ 9 tệp dữ liệu thô dạng CSV giai đoạn 2016–2024 được lưu trữ tại `data/raw/tabular/`.

**Nguyên tắc bảo vệ dữ liệu bất biến:**
1. **Tuyệt đối không sửa đổi `data/raw/`:** Không ghi đè, xóa, đổi tên hoặc sửa bất kỳ byte dữ liệu nào trong cây thư mục `data/raw/`.
2. **Đối soát vật lý thực tế:** Toàn bộ các mã băm và số dòng trong danh mục này được đối soát trực tiếp bằng chương trình đọc luồng có giới hạn bộ nhớ (bounded streaming reader) trên tệp vật lý, khớp 100% với `inputs/schema_YYYY.json`, `T004_FINAL_QA_RECONCILIATION.md`, `T008_ENTRY_SOURCE_INVENTORY_RECONCILIATION.md`, và `AUDITED_SOURCE_INVENTORY` trong mã nguồn sản xuất `src/flight_pipeline/ingestion/source_validator.py`.

---

## 2. BẢNG DANH MỤC NGUỒN DỮ LIỆU THÔ 9 NĂM CHUẨN HÓA

| Năm khảo sát | Đường dẫn tệp vật lý | Kích thước tệp (Bytes) | Dung lượng (GiB) | Dung lượng (GB) | Số dòng dữ liệu (Data Rows) | Mã băm SHA-256 Canonical (Local Snapshot) | Trạng thái nguồn |
| :---: | :--- | :---: | :---: | :---: | :---: | :--- | :---: |
| **2016** | `data/raw/tabular/2016/flight_with_weather_2016.csv` | `1,538,427,452` | 1.43 GiB | 1.54 GB | 5,537,987 | `4ed92ed732721a38ae28325135fad63436347613674ad96c1b273eb9d44cef34` | `CANONICAL_AUDITED` |
| **2017** | `data/raw/tabular/2017/flight_with_weather_2017.csv` | `1,549,837,485` | 1.44 GiB | 1.55 GB | 5,575,872 | `67b8dbd6678576b1a2229ef2dbeec065e0f64d31d688ab8a2ca59c88d2a656f9` | `CANONICAL_AUDITED` |
| **2018** | `data/raw/tabular/2018/flight_with_weather_2018.csv` | `1,941,406,432` | 1.81 GiB | 1.94 GB | 6,986,842 | `0398bab8f1b79a5f3bea628b707e18c3af628f37a1daa52de6849fb8bdfc71a3` | `CANONICAL_AUDITED` |
| **2019** | `data/raw/tabular/2019/flight_with_weather_2019.csv` | `1,990,370,667` | 1.85 GiB | 1.99 GB | 7,161,827 | `eec50211a1a63f37b840977be5ab2e99a008a8d5234c2a12df8eb50862f93b4a` | `CANONICAL_AUDITED` |
| **2020** | `data/raw/tabular/2020/flight_with_weather_2020.csv` | `1,197,858,795` | 1.12 GiB | 1.20 GB | 4,312,091 | `787981046c9fe0f4884ac207a3d28ea6a7fae98e89535cb9f8a37debb5c7fa5d` | `CANONICAL_AUDITED` |
| **2021** | `data/raw/tabular/2021/flight_with_weather_2021.csv` | `1,600,032,487` | 1.49 GiB | 1.60 GB | 5,755,666 | `5b7cc4801a6ff5cf432137632209ebd7aecd3d4a0f83e8920e3525116e88defc` | `CANONICAL_AUDITED` |
| **2022** | `data/raw/tabular/2022/flight_with_weather_2022.csv` | `1,782,648,882` | 1.66 GiB | 1.78 GB | 6,413,416 | `45eb45e801d6eeeb16167306fc69a8449177191cfff29bfb5d22285827f53140` | `CANONICAL_AUDITED` |
| **2023** | `data/raw/tabular/2023/flight_with_weather_2023.csv` | `1,847,433,387` | 1.72 GiB | 1.85 GB | 6,645,461 | `9c9e20f55d3dd10a127bcdd28680df6547a01a82ad71999b794aff3e1075d7bd` | `CANONICAL_AUDITED` |
| **2024** | `data/raw/tabular/2024/flight_with_weather_2024.csv` | `1,748,350,586` | 1.63 GiB | 1.75 GB | 6,284,841 | `f938ade95a031088467ab5e75abea2021e541eaf4a4288e564066e100541d5f7` | `CANONICAL_AUDITED` |
| **TỔNG CỘNG** | **Toàn bộ 9 năm khảo sát** | **`15,196,366,173`** | **`14.15 GiB`** | **`15.20 GB`** | **`54,674,003`** | **Khớp 100% kiểm toán vật lý** | `VERIFIED_PASS` |

---

## 3. LƯU Ý ĐẶC THÙ VỀ NĂM 2016 VÀ 2024

1. **Đính chính mã băm 2016 (Finding P03):**
   - Mã băm lịch sử `632d43e5898b1eb798363a02fa023eec7fa6d38e0ba8f368e7ec8396aa700540` trong các tài liệu sơ khai trước Gate G5 là kết quả tính toán sai hoặc không hoàn tất.
   - Văn bản [`G5_T010_ENTRY_BASELINE_ERRATA.md`](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/docs/05-evidence/G5_T010_ENTRY_BASELINE_ERRATA.md) đã chính thức bác bỏ giá trị này và niêm phong giá trị canonical: **`4ed92ed732721a38ae28325135fad63436347613674ad96c1b273eb9d44cef34`**.
2. **Khiếm khuyết dữ liệu năm 2024 (Rủi ro OR-05):**
   - Tệp dữ liệu thô năm 2024 có đúng **6.284.841 dòng dữ liệu** (335 ngày, khuyết thiếu toàn bộ 31 ngày của Tháng 3/2024).
   - Tuyệt đối không nội suy dữ liệu giả. Pipeline T-012 ghi nhận cờ cảnh báo `OR-05: OPEN_QUALITY_DEFECT` và nhãn `source_coverage_status = PARTIAL`.
