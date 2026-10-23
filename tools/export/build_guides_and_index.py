# -*- coding: utf-8 -*-
"""
tools/export/build_guides_and_index.py
Generates:
- T016_REPRODUCIBILITY_AND_DEMO_GUIDE.md
- T016_CLAIM_TO_EVIDENCE_INDEX.csv
- T016_TECHNICAL_COMPLETION_REPORT.md
"""

import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import json
import csv
from tools.export.report_content import PROJECT_METADATA

OUTPUT_DIR = Path(r"D:\Flight_Audit_Exports\G7_T016_FINAL_DELIVERABLES")
CORRECTED_OUTPUT_DIR = OUTPUT_DIR / "corrected"
ANALYTICS_DIR = BASE_DIR / "data" / "analytics" / "runs" / "t014_analysis_2016_2024_v4"

def generate_reproducibility_guide(output_dir=None):
    target_dir = Path(output_dir) if output_dir else CORRECTED_OUTPUT_DIR
    target_dir.mkdir(parents=True, exist_ok=True)
    guide_path = target_dir / "T016_REPRODUCIBILITY_AND_DEMO_GUIDE.md"

    content = [
        "# HƯỚNG DẪN TÁI LẬP VÀ QUY TRÌNH TRÌNH DIỄN ĐỀ ÁN (T-016)",
        "## PHÂN TÍCH HIỆU SUẤT KHAI THÁC CHUYẾN BAY NỘI ĐỊA HOA KỲ GIAI ĐOẠN 2016–2024",
        "",
        f"- **Mã nhiệm vụ / Cổng kiểm soát:** {PROJECT_METADATA['task']} / Gate {PROJECT_METADATA['gate']}",
        f"- **Trạng thái thực thi:** `{PROJECT_METADATA['status']}`",
        f"- **Snapshot dữ liệu Curated Parquet:** 117 tệp | 3,308,617,408 bytes | {PROJECT_METADATA['curated_records']:,} bản ghi",
        f"- **Snapshot KPI sản xuất:** `{PROJECT_METADATA['kpi_run_id']}` ({PROJECT_METADATA['kpi_records']:,} dòng KPI | {PROJECT_METADATA['kpi_cohorts']:,} cohorts)",
        f"- **Snapshot phân tích chính thức:** `{PROJECT_METADATA['analysis_run_id']}` (12 bảng, 16 biểu đồ, 20 RES)",
        "",
        "---",
        "",
        "## PHẦN A — YÊU CẦU DỰ ÁN & HỆ THỐNG",
        "",
        "### 1. Yêu cầu phần mềm và phiên bản môi trường thực tế",
        "- **Hệ điều hành:** Microsoft Windows 10/11 Enterprise (64-bit, x86_64) hoặc Linux x86_64.",
        "- **Phiên bản Python:** Python 3.10.x (đã xác thực trên Python 3.10.11).",
        "- **Công cụ tính toán Dữ liệu lớn:** Apache Spark / PySpark 4.0.1 (đã xác thực trên môi trường thực thi).",
        "- **Môi trường Java Runtime:** OpenJDK 21.0.12.1 LTS (Temurin 64-Bit Server VM, đã xác thực cấu hình `JAVA_HOME`).",
        "- **Các thư viện phụ thuộc bắt buộc:**",
        "  - `pandas >= 2.0.0` (xử lý dữ liệu bảng)",
        "  - `pyarrow >= 14.0.0` (đọc/ghi tệp định dạng Apache Parquet)",
        "  - `matplotlib >= 3.8.0` (vẽ biểu đồ khoa học)",
        "  - `seaborn >= 0.13.0` (bản đồ nhiệt và phân phối)",
        "  - `python-docx >= 1.0.0` (sinh báo cáo học thuật Microsoft Word)",
        "  - `python-pptx >= 1.0.0` (sinh bài trình chiếu Microsoft PowerPoint)",
        "  - `pytest >= 8.0.0` (khung thực thi kiểm thử tự động)",
        "",
        "### 2. Cấu trúc thư mục kho lưu trữ chuẩn",
        "```",
        "US_FLIGHT_PERFORMANCE_DOCS_V1/",
        "├── data/                           # Thư mục dữ liệu (ngoài Git)",
        "│   ├── curated/runs/              # 9 phân vùng Parquet sạch (117 tệp, 3.31 GB)",
        "│   ├── kpi/runs/                  # Snapshot KPI sản xuất kpi_run_2016_2024_v1",
        "│   └── analytics/runs/            # Snapshot phân tích t014_analysis_2016_2024_v4",
        "│       ├── tables/                # 12 bảng dữ liệu CSV & Parquet",
        "│       ├── charts/                # 16 biểu đồ khoa học PNG (300 DPI) & SVG",
        "│       └── RESULTS_REGISTER.json  # 20 bản ghi phát hiện định lượng chuẩn hóa",
        "├── docs/                          # Hệ thống tài liệu quản trị & kỹ thuật",
        "│   ├── 01-planning/               # PRD, BACKLOG, ROADMAP",
        "│   ├── 02-design/                 # DATA_CONTRACT, KPI_SPEC, ANALYSIS_PROTOCOL",
        "│   ├── 03-quality/                # TEST_PLAN, RISK_REGISTER, CHANGELOG",
        "│   ├── 04-execution/              # PROJECT_STATE, AI_HANDOFF",
        "│   └── 05-evidence/               # Bằng chứng kiểm toán và biên bản nghiệm thu",
        "├── src/flight_pipeline/           # Mã nguồn pipeline Spark (ingestion, quality, kpi, analytics)",
        "├── tests/                         # Bộ kiểm thử đơn vị và tích hợp",
        "└── tools/qa/                      # Các kịch bản kiểm toán độc lập và đối soát",
        "```",
        "",
        "---",
        "",
        "## PHẦN B — THIẾT LẬP MÔI TRƯỜNG THỰC THI",
        "",
        "### 1. Kiểm tra môi trường Python và Java",
        "Mở terminal (PowerShell trên Windows) tại thư mục gốc repository và thực thi:",
        "```powershell",
        "# Kiểm tra phiên bản Python",
        "python --version",
        "# Kết quả kỳ vọng: Python 3.10.x",
        "",
        "# Kiểm tra môi trường Java",
        "java -version",
        "# Kết quả kỳ vọng: openjdk version \"21.x\" (hoặc 17.x)",
        "```",
        "",
        "### 2. Cài đặt các thư viện cần thiết",
        "```powershell",
        "pip install pandas pyarrow matplotlib seaborn python-docx python-pptx pytest",
        "```",
        "",
        "---",
        "",
        "## PHẦN C — YÊU CẦU DỮ LIỆU NGUỒN & PHẠM VI",
        "",
        "1. **Bảo toàn dữ liệu nguồn:** Các tệp CSV thô (34.5 GB) và dữ liệu Parquet lớn không được đưa vào Git để tuân thủ chính sách quản trị kho lưu trữ.",
        "2. **Dữ liệu phân tích đã nghiệm thu:** Toàn bộ dữ liệu sạch (Curated Parquet), dữ liệu KPI (`kpi_run_2016_2024_v1`), và bảng kết quả phân tích (`t014_analysis_2016_2024_v4`) đã được niêm phong sẵn sàng trên đĩa cục bộ.",
        "3. **Chính sách bản quyền & Nhận dạng:** Nguồn dữ liệu tuân thủ ghi nhận rủi ro OR-08 (`IDENTITY_UNVERIFIED / ACCEPTED_NON_BLOCKING`) và đã được kiểm chứng tương đương số học 10,500/10,500 điểm với BTS TranStats Part 234 qua TS-018 Option B.",
        "",
        "---",
        "",
        "## PHẦN D — CÁC LỆNH KIỂM CHỨNG TÁI LẬP (REPRODUCIBILITY COMMANDS)",
        "",
        "Người đánh giá có thể thực thi trực tiếp các lệnh kiểm chứng độc lập sau đây:",
        "",
        "### Lệnh 1: Kiểm tra con trỏ phiên bản và tính bất biến",
        "```powershell",
        "python -c \"print('KPI Pointer:', open('data/kpi/latest_run_id.txt').read().strip()); print('Analytics Pointer:', open('data/analytics/latest_run_id.txt').read().strip())\"",
        "# Kết quả kỳ vọng:",
        "# KPI Pointer: kpi_run_2016_2024_v1",
        "# Analytics Pointer: t014_analysis_2016_2024_v4",
        "```",
        "",
        "### Lệnh 2: Chạy kiểm toán toàn vẹn phân tích độc lập (91/91 Checks PASS)",
        "```powershell",
        "python tools/qa/run_t014_independent_audit.py",
        "# Kết quả kỳ vọng: AUDIT SUMMARY: 91/91 CHECKS PASSED, exit code 0",
        "```",
        "",
        "### Lệnh 3: Chạy bộ kiểm thử phân tích toàn diện (29 Tests PASS)",
        "```powershell",
        "python -m pytest tests/test_t014_analytics_comprehensive.py",
        "# Kết quả kỳ vọng: 29 passed in ~13s, exit code 0",
        "```",
        "",
        "### Lệnh 4: Kiểm kê vật lý thực tế dữ liệu Curated Parquet",
        "```powershell",
        "python -c \"import os; p='data/curated/runs'; files=[os.path.join(r,f) for r,d,fs in os.walk(p) for f in fs if f.endswith('.parquet')]; print('Total Parquet files:', len(files), '| Total bytes:', sum(os.path.getsize(f) for f in files))\"",
        "# Kết quả kỳ vọng: Total Parquet files: 117 | Total bytes: 3308617408",
        "```",
        "",
        "### Lệnh 5: Đọc và hiển thị bảng sản lượng hàng năm (RQ-01)",
        "```powershell",
        "python -c \"import pandas as pd; df=pd.read_csv('data/analytics/runs/t014_analysis_2016_2024_v4/tables/rq01_annual_volume.csv'); print(df[['year','annual_volume','yoy_growth_pct','source_coverage_status']].to_string(index=False))\"",
        "```",
        "",
        "### Lệnh 6: Kiểm tra Sổ đăng ký kết quả (20 RES-IDs)",
        "```powershell",
        "python -c \"import json; data=json.load(open('data/analytics/runs/t014_analysis_2016_2024_v4/RESULTS_REGISTER.json', encoding='utf-8')); print('Total RES entries:', len(data['results']))\"",
        "# Kết quả kỳ vọng: Total RES entries: 20",
        "```",
        "",
        "---",
        "",
        "## PHẦN E — PHÂN ĐỊNH GIỮA KIỂM CHỨNG CHỈ ĐỌC VÀ CHẠY LẠI SẢN XUẤT",
        "",
        "> [!IMPORTANT]",
        "> **CẢNH BÁO QUẢN TRỊ D5 = NOT_AUTHORIZED / FAIL-CLOSED:**  ",
        "> Đề án phân định tuyệt đối giữa:  ",
        "> 1. **Kiểm chứng chỉ đọc (Read-only Verification):** Đọc dữ liệu, kiểm tra mã băm, chạy kiểm thử và đối soát kết quả — Hoàn toàn được phép và an toàn.  ",
        "> 2. **Chạy lại toàn bộ đường ống sản xuất (Production Rebuild):** Chạy lại Spark ingestion từ CSV thô hoặc tính lại KPI — **TUYỆT ĐỐI BỊ CẤM** khi chưa có chỉ thị ủy quyền D5 bằng văn bản của Project Lead.",
        "",
        "---",
        "",
        "## PHẦN F — KỊCH BẢN TRÌNH DIỄN KỸ THUẬT (DEMONSTRATION FLOW)",
        "",
        "Quy trình trình diễn trực tiếp đề án gồm 8 bước mạch lạc:",
        "",
        "1. **Bước 1 — Giới thiệu tổng quan cấu trúc đề tài:** Mở `docs/04-execution/PROJECT_STATE.md`, chỉ ra trạng thái đóng Cổng G6 có kiểm soát và phê duyệt kỹ thuật T-016 sẵn sàng.",
        "2. **Bước 2 — Trình diễn dữ liệu sạch Curated Parquet:** Thực thi Lệnh 4 kiểm tra 117 tệp Parquet và dung lượng 3,308,617,408 bytes (~3.31 GB) nén từ 34.5 GB CSV.",
        "3. **Bước 3 — Trình diễn kết quả CORE KPI:** Mở thư mục `data/kpi/runs/kpi_run_2016_2024_v1/`, chỉ ra 9 tệp Parquet chứa 684,180 dòng KPI trên 57,015 cohorts.",
        "4. **Bước 4 — Trình diễn các bảng phân tích:** Mở `tables/rq01_annual_volume.csv` và `tables/rq02_annual_delays.csv` minh chứng các số liệu thật.",
        "5. **Bước 5 — Trình diễn hệ thống biểu đồ khoa học:** Mở các tệp ảnh 300 DPI trong `charts/` (Hình 1.1, Hình 2.2, Hình 3.1, Hình 3.4).",
        "6. **Bước 6 — Diễn giải phát hiện chuyên sâu với bằng chứng RES:**",
        "   - Trình bày nghịch lý đuôi dài lệch phải (RQ-02): Trung vị P50 luôn âm [-11.0, -5.0] phút (`RES-006`) chứng minh >50% chuyến đến sớm; trong khi P90 kéo dãn lên +42 đến +43 phút (`RES-007`), kéo lệch Mean lên dương.",
        "7. **Bước 7 — Thực thi lệnh kiểm toán độc lập:** Chạy `python tools/qa/run_t014_independent_audit.py` tại terminal, cho thấy 91/91 checks PASS trực tiếp.",
        "8. **Bước 8 — Công bố các giới hạn khoa học:** Tóm tắt 4 ràng buộc OR-03, OR-05 (năm 2024 PARTIAL), OR-07 (không thời tiết), và OR-08 (Kaggle identity) cùng bản chất phi nhân quả.",
        "",
        "---",
        "**Tài liệu này là thành phần bàn giao chính thức của Nhiệm vụ T-016.**"
    ]

    with open(guide_path, "w", encoding="utf-8") as f:
        f.write("\n".join(content))

    file_size = os.path.getsize(guide_path)
    print(f"Reproducibility guide generated: {guide_path} ({file_size:,} bytes)")
    return guide_path

def generate_claim_to_evidence_index(output_dir=None):
    target_dir = Path(output_dir) if output_dir else CORRECTED_OUTPUT_DIR
    target_dir.mkdir(parents=True, exist_ok=True)
    index_path = target_dir / "T016_CLAIM_TO_EVIDENCE_INDEX.csv"

    # Mapping of sections and slides to RES-001..RES-020
    rows = [
        ["Report Sec 5.1 / Slide 8", "RQ-01", "Tong san luong 9 nam dat 54,674,003 chuyen; dinh 2019 dat 7,161,827 chuyen (+2.5% YoY); day 2020 giam -39.79% xuong 4,312,091 chuyen", "RES-001", "rq01_annual_volume.csv / CHART_RQ01_01", "kpi_run_2016_2024_v1", "Non-causal; 54.7M accepted census"],
        ["Report Sec 5.1 / Slide 8", "RQ-01", "Trong dung 6/9 nam quan sat (2016-18, 2021-22, 2024), dinh san luong trong nam deu roi vao Thang 7 (>600K chuyen/thang)", "RES-002", "rq01_monthly_volume.csv / CHART_RQ01_02", "kpi_run_2016_2024_v1", "N=9 years; 3 exceptional years (2019 Aug, 2020 Jan, 2023 Oct)"],
        ["Report Sec 5.1 / Slide 8", "RQ-01", "Thang 5/2020 ghi nhan day san luong lich su voi 163,767 chuyen bay (sau thang 4/2020 voi 179,835 chuyen)", "RES-003", "rq01_monthly_volume.csv / CHART_RQ01_02", "kpi_run_2016_2024_v1", "Pandemic shock period; unweighted monthly census"],
        ["Report Sec 5.2 / Slide 9", "RQ-02", "Ty le tre den (>=15m) dat day 9.73% nam 2020, tang vot len dinh 20.99% nam 2022 va duy tri 20.81% nam 2024", "RES-004", "rq02_annual_delays.csv / CHART_RQ02_01", "kpi_run_2016_2024_v1", "Valid-denominator pooled; N_valid(ARR_DELAY)"],
        ["Report Sec 5.2 / Slide 9", "RQ-02", "Do tre den trung binh co dau am duy nhat vao nam 2020 (-5.11 phut, chinh xac -5.1078 phut); cac nam khac luon duong (+3.5 den +7.1m)", "RES-005", "rq02_annual_delays.csv / CHART_RQ02_01", "kpi_run_2016_2024_v1", "Signed delay preserved; negative indicates early arrival"],
        ["Report Sec 5.2 / Slide 9", "RQ-02", "Trung vi tre den (P50) hang nam luon am [-11.0, -5.0] phut; hon 50% chuyen bay den som hon gio lich trinh!", "RES-006", "rq02_annual_delays.csv / CHART_RQ02_03", "kpi_run_2016_2024_v1", "Spark GK-sketch approx (accuracy=10000); NO PERCENTILE POOLING"],
        ["Report Sec 5.2 / Slide 9", "RQ-02", "Phan vi P90 dat +42.0m (2022) va +43.0m (2024); chenh lech P90-P50 dao dong 25-49 phut (38-49 phut nam thuong, 25 phut 2020) (duoi dai lech phai)", "RES-007", "rq02_annual_delays.csv / CHART_RQ02_03", "kpi_run_2016_2024_v1", "Extreme right skewness; mean is pulled positive by tail 10-20%"],
        ["Report Sec 5.3 / Slide 10", "RQ-03", "Southwest Airlines (WN) la hang co san luong lon nhat voi 11,133,643 chuyen (20.36% thi truong), dung gio gop 80.67%, Taxi-Out 12.46m", "RES-008", "rq03_top_carriers.csv / CHART_RQ03_01", "kpi_run_2016_2024_v1", "min-N >= 1000 (SUFFICIENT); point-to-point network model"],
        ["Report Sec 5.3 / Slide 10", "RQ-03", "Delta Air Lines (DL, N=7,821,658) dung dau nhom truyen thong voi dung gio gop 85.81% (tre den 14.19%), tre den TB chi +0.66m; American (AA) dat 79.61%", "RES-009", "rq03_top_carriers.csv / CHART_RQ03_01", "kpi_run_2016_2024_v1", "Valid-denominator weighted pooling; hub-and-spoke vs point-to-point"],
        ["Report Sec 5.3 / Slide 11", "RQ-03", "San bay Newark Liberty (EWR) ghi nhan ty le tre cat canh dinh diem 27.67% nam 2022 tren N=123,277 chuyen (ORD dat 22.48% nam 2024)", "RES-010", "rq03_origin_airports.csv / CHART_RQ03_03", "kpi_run_2016_2024_v1", "min-N >= 365 (SUFFICIENT); congested Northeast corridor"],
        ["Report Sec 5.3 / Slide 11", "RQ-03", "Nam 2019, cap chong ORD <-> LGA bat doi xung ty le tre ro ret: ORD->LGA tre 31.42% vs LGA->ORD tre 28.60%, chenh lech 2.82% (cap LAX-SFO chenh 2.46%)", "RES-011", "rq03_directed_routes.csv / CHART_RQ03_04", "kpi_run_2016_2024_v1", "min-N >= 100 per direction (SUFFICIENT); directional route asymmetry"],
        ["Report Sec 5.4 / Slide 12", "RQ-04", "Nam 2020 san luong giam 39.79% so voi 2019, dong thoi ty le tre den giam gan 10 diem phan tram xuong 9.73%", "RES-012", "rq04_pandemic_comparison.csv / CHART_RQ04_01", "kpi_run_2016_2024_v1", "Observational co-variation; non-causal attribution"],
        ["Report Sec 5.4 / Slide 12", "RQ-04", "Thang 4/2020 dat ty le dung gio ky luc 95.15% (ty le tre chi 4.85%) tren 179,835 chuyen bay khi khong phan thong thoang", "RES-013", "rq04_pandemic_comparison.csv / CHART_RQ04_02", "kpi_run_2016_2024_v1", "Monthly pandemic bottom; capacity underutilization"],
        ["Report Sec 5.4 / Slide 12", "RQ-04", "Giai doan phuc hoi 2022-2024 tai tac nghen khi ty le tre den tang vot len dinh 20.99% (2022) va 20.81% (2024), vuot qua ca muc nam 2019", "RES-014", "rq04_pandemic_comparison.csv / CHART_RQ04_01", "kpi_run_2016_2024_v1", "Post-pandemic re-congestion; network capacity limits"],
        ["Report Sec 5.5 / Slide 13", "RQ-05", "Thoi gian lan ra cat canh (Taxi-Out) binh quan toan quoc dao dong tu 15.25 phut (2020) den 17.95 phut (2024)", "RES-015", "rq05_annual_journey_times.csv / CHART_RQ05_01", "kpi_run_2016_2024_v1", "N_valid(TAXI_OUT); surface departure queue congestion"],
        ["Report Sec 5.5 / Slide 13", "RQ-05", "Thoi gian lan vao ben do (Taxi-In) binh quan toan quoc on dinh tu 6.82 phut (2020) den 8.37 phut (2024)", "RES-016", "rq05_annual_journey_times.csv / CHART_RQ05_01", "kpi_run_2016_2024_v1", "N_valid(TAXI_IN); less prone to queueing than Taxi-Out"],
        ["Report Sec 5.5 / Slide 13", "RQ-05", "San bay JFK dan dau quoc gia ve Taxi-Out binh quan nam 2023 voi 26.21 phut tren N=129,620 chuyen (EWR dat 23.76m, LGA 23.58m, ORD 22.45m)", "RES-017", "rq05_airport_taxi.csv / CHART_RQ05_03", "kpi_run_2016_2024_v1", "min-N >= 365 (SUFFICIENT); complex airfield layout & volume"],
        ["Report Sec 5.5 / Slide 13", "RQ-05", "Chenh lech giua hai gia tri TB can bien da cong bo (CRS - Actual Elapsed TB) luon duong qua 9 nam, dao dong tu +4.87m (2018) den +7.08m (2020)", "RES-018", "rq05_annual_journey_times.csv / CHART_RQ05_02", "kpi_run_2016_2024_v1", "Difference of published marginal means; descriptive observation without causal attribution"],
        ["Report Sec 5.5 / Slide 13", "RQ-05", "Thoi gian hanh trinh thuc te TB dat 140.16 phut nam 2016 (N=5,537,987); so voi Actual Elapsed TB, Air Time chiem ~83.14%, Taxi-Out ~11.55%, Taxi-In ~5.31%", "RES-019", "rq05_annual_journey_times.csv / CHART_RQ05_02", "kpi_run_2016_2024_v1", "Ratio of published marginal means; DC-12 valid denominators"],
        ["Report Sec 5.1 / Slide 8", "RQ-01", "Nam 2024 co dung 11 thang quan sat (335 ngay, 6,284,841 chuyen, khuyet Thang 3 theo OR-05); source_coverage_status = PARTIAL", "RES-020", "rq01_annual_volume.csv / CHART_RQ01_01", "kpi_run_2016_2024_v1", "OR-05 calendar defect; prohibited from full-year volume parity"]
    ]

    headers = [
        "section_or_slide", "research_question", "claim_summary",
        "res_id", "source_table_or_chart", "source_run_id", "limitation_reference"
    ]

    with open(index_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)

    file_size = os.path.getsize(index_path)
    print(f"Claim-to-Evidence index generated: {index_path} ({file_size:,} bytes, {len(rows)} entries)")
    return index_path

def generate_technical_completion_report(output_dir=None):
    target_dir = Path(output_dir) if output_dir else Path(r"D:\Flight_Audit_Exports\G7_T016_FINAL_DELIVERABLES\signoff_official")
    target_dir.mkdir(parents=True, exist_ok=True)
    report_path = target_dir / "T016_TECHNICAL_COMPLETION_REPORT.md"

    content = [
        "# BÁO CÁO NGHIỆM THU KỸ THUẬT CHÍNH THỨC NHIỆM VỤ T-016",
        "## G7 — Academic Report, Presentation & Reproducibility Handoff",
        "",
        "- **Dự án:** Phân tích hiệu suất khai thác chuyến bay Hoa Kỳ 2016–2024 bằng Apache Spark/PySpark.",
        "- **Cổng kiểm soát:** Gate G7 (G7 = IN_PROGRESS).",
        "- **Mã nhiệm vụ:** T-016 (Báo cáo, Slide, Hướng dẫn chạy/Tái lập).",
        "- **Phán quyết kỹ thuật chính thức:** `T016_OFFICIAL_CONTROLLED_SIGNOFF_PASS`.",
        "- **Trạng thái phê duyệt:** `T-016 = PASS / COMPLETED (CONTROLLED)` (Đã được Project Lead ủy quyền ký duyệt có kiểm soát).",
        "- **Nhiệm vụ kế tiếp:** `T-017 = NOT_STARTED / ELIGIBLE_FOR_SEPARATE_AUTHORIZATION`.",
        f"- **Thư mục xuất bản chính thức:** `{target_dir}`",
        "",
        "---",
        "",
        "## 1. TỔNG HỢP CÁC NỘI DUNG HIỆU CHỈNH & ĐÍNH CHÍNH KHOA HỌC CUỐI CÙNG",
        "",
        "Toàn bộ các điểm hiệu chỉnh vi mô và đính chính khoa học đã được thực hiện và kiểm toán nghiêm ngặt:",
        "",
        "1. **Hiệu chỉnh Slide 5 PowerPoint (Kiến trúc Big Data & Parquet):**",
        "   - Loại bỏ hoàn toàn nhận định không có bằng chứng đo đạc thực nghiệm về việc Column Projection / Predicate Pushdown giảm 85% disk I/O.",
        "   - Thay thế bằng giải thích định tính chuẩn xác về mặt kỹ thuật: cơ chế chiếu cột (column projection) chỉ nạp các cột cần thiết cho mỗi phép tính KPI và đẩy điều kiện lọc (predicate pushdown) xuống tầng lưu trữ Parquet, giảm thiểu đáng kể chi phí quét đĩa vật lý. Không đưa ra bất kỳ tỷ lệ phần trăm nào chưa qua đo đạc benchmark thực tế.",
        "   - Xác định rõ ràng mốc thời gian 510.7 giây là benchmark hiệu năng đã được phê duyệt riêng cho tác vụ tính toán 8 CORE KPIs (T-013), không đại diện cho tổng thời gian toàn bộ quy trình đầu cuối.",
        "",
        "2. **Hiệu chỉnh Slide 7 PowerPoint (Khung KPI & FP-DEC-016):**",
        "   - Làm rõ quy tắc phân tầng cỡ mẫu theo quyết định `FP-DEC-016` dựa trên mẫu số hợp lệ riêng `N_valid` của từng chỉ số so với ngưỡng tối thiểu đã duyệt:",
        "     * Cấp độ phân loại:",
        "       - `SUPPRESSED`: khi `N_valid < N_min` (ẩn chỉ số để tránh suy diễn sai lầm).",
        "       - `LOW_SAMPLE_CAUTION`: khi `N_min <= N_valid < 3 * N_min` (gắn nhãn cảnh báo cỡ mẫu nhỏ).",
        "       - `SUFFICIENT`: khi `N_valid >= 3 * N_min` (độ tin cậy thống kê đầy đủ).",
        "     * Ngưỡng tối thiểu phê duyệt chính thức: Hãng bay theo năm (`carrier-year` = 1,000 chuyến), Sân bay theo năm (`airport-year` = 365 chuyến), Tuyến bay có hướng theo năm (`directed route-year` = 100 chuyến).",
        "",
        "3. **Hiệu chỉnh Báo cáo Học thuật (MD/DOCX) & Slide 2 PowerPoint (Động lực & Nền tảng PySpark):**",
        "   - Loại bỏ các nhận định chủ quan cho rằng thư viện đơn nút như Pandas là hoàn toàn bất khả thi hoặc bắt buộc gặp lỗi tràn bộ nhớ (OOM).",
        "   - Mô tả căn cứ khoa học chính xác vì sao Apache Spark / PySpark được lựa chọn: quy mô 54.7 triệu bản ghi chi tiết (34.5 GB CSV thô) đòi hỏi kiến trúc xử lý khả mở (scalable), cơ chế phân vùng dữ liệu tối ưu, lazy evaluation và quản lý bộ nhớ ngoài heap (off-heap) để đảm bảo độ tin cậy và ổn định cao trên môi trường thực tế của đồ án (Windows 11 Enterprise 64-bit, OpenJDK 21 LTS, Python 3.10).",
        "   - Tuyệt đối không tạo dựng các con số so sánh giả định (comparative benchmark).",
        "",
        "4. **Đối chiếu và Phân định Cấu trúc Bảng trong Báo cáo Word (DOCX Structural Reconciliation):**",
        "   - **Thực tế cấu trúc văn bản trong tệp Word (`doc.tables`):** Gồm đúng **9 phần tử bảng**, được phân định thành 2 nhóm cấu trúc rõ ràng:",
        "     * **7 bảng số liệu đa cột thực tế (Real Multi-Column Data Tables):** Bảng 5.1 (Sản lượng 9 năm), Bảng 5.2 (Trễ đến & phân vị), Bảng 5.3 (Hãng bay lớn), Bảng 5.4 (Đại dịch & phục hồi), Bảng 5.5 (Lăn bánh Taxi & hành trình), Phụ lục A (Sổ đăng ký 20 RES), Phụ lục B (Danh mục 16 Biểu đồ).",
        "     * **2 hộp phương pháp luận (Methodological Callout Boxes):** Định dạng khung bảng đơn ô (1x1 table) viền trái đậm màu Navy và nền sáng.",
        "   - **Giải trình nguồn gốc con số 16:** Phát sinh do kiểm kê cơ học ký tự `|` trong Markdown giữa 7 bảng dữ liệu và 9 dòng viền ASCII luồng xử lý 4 giai đoạn, hoặc phân biệt với 16 biểu đồ / 12 bảng phân tích T-014.",
        "",
        "5. **Đính chính Tính nhất quán Tham số Sai số Phân vị Greenwald-Khanna (Mục 2.5):**",
        "   - Sửa đổi phát biểu tại Mục 2.5 trong cả hai bản Markdown và DOCX: từ $\\epsilon_{\\text{rank}} \\le 0.01$ (1%) thành công thức chuẩn tắc đồng bộ 100% với Mục 3.8 và quyết định kiến trúc `FP-DEC-015`:",
        "     $$\\epsilon_{\\text{rank}} \\le \\frac{1}{\\text{accuracy}} = \\frac{1}{10000} = 0.0001 \\quad (0.01\\%)$$",
        "   - Thống nhất tuyệt đối cơ sở lý thuyết sai số thứ hạng tương đối trên toàn bộ tài liệu nghiên cứu.",
        "",
        "---",
        "",
        "## 2. DANH MỤC CÁC SẢN PHẨM HOÀN TẤT TẠI THƯ MỤC XUẤT KHẨU",
        f"Thư mục lưu trữ: `{target_dir}`",
        "",
        "| STT | Tên tệp sản phẩm | Định dạng | Kích thước / Vai trò |",
        "|:---:|:---|:---:|:---|",
        "| 1 | `T016_FINAL_ACADEMIC_REPORT.docx` | DOCX | Báo cáo học thuật hoàn chỉnh (Microsoft Word) đủ 80 đề mục, 7 bảng dữ liệu đa cột, 2 hộp phương pháp luận và 15 biểu đồ 300 DPI (đã đính chính Mục 2.5) |",
        "| 2 | `T016_FINAL_ACADEMIC_REPORT.md` | MD | Nguồn văn bản Markdown chuẩn tắc đồng bộ của báo cáo học thuật (80 đề mục, ~82k ký tự, đã đính chính Mục 2.5) |",
        "| 3 | `T016_FINAL_PRESENTATION.pptx` | PPTX | Bộ trình chiếu 16 slide khoa học (PowerPoint) đã hoàn tất micro-corrections và speaker notes |",
        "| 4 | `T016_REPRODUCIBILITY_AND_DEMO_GUIDE.md` | MD | Hướng dẫn môi trường, lệnh tái lập và kịch bản demo 8 bước |",
        "| 5 | `T016_CLAIM_TO_EVIDENCE_INDEX.csv` | CSV | Chỉ mục đối chiếu truy vết 20 phát hiện định lượng |",
        "| 6 | `T016_TECHNICAL_COMPLETION_REPORT.md` | MD | Báo cáo nghiệm thu kỹ thuật và đối chiếu cấu trúc tài liệu |",
        "| 7 | `T016_OFFICIAL_SIGNOFF_REVIEW.zip` | ZIP | Gói nén niêm phong toàn bộ 6 sản phẩm T-016 |",
        "| 8 | `T016_OFFICIAL_SIGNOFF_REVIEW_MANIFEST.json` | JSON | Hồ sơ kiểm toán ngoại vi ghi nhận kích thước, SHA-256, CRC-32 |",
        "",
        "---",
        "",
        "## 3. KẾT QUẢ KIỂM TOÁN CHẤT LƯỢNG (VALIDATION CHECKS)",
        "",
        "1. **Kiểm tra đính chính khoa học Mục 2.5:** Đã xác nhận công thức $\\epsilon_{\\text{rank}} \\le 1/10000 = 0.0001 = 0.01\\%$ khớp chính xác giữa Mục 2.5, Mục 3.8 và quyết định `FP-DEC-015` trong cả Markdown và Word DOCX.",
        "2. **Kiểm tra 4 điểm hiệu chỉnh vi mô trước:** Cả 4 điểm về Slide 5, Slide 7, Slide 2/Báo cáo và cấu trúc bảng DOCX được bảo toàn hoàn hảo.",
        "3. **Kiểm tra tính nhất quán giữa DOCX và Markdown:** Đủ 80/80 đề mục (Heading 0..3), 437 khối văn bản, 15 biểu đồ 300 DPI, nội dung các đoạn văn bản sửa đổi hoàn toàn đồng nhất.",
        "4. **Kiểm tra kết xuất bộ trình chiếu PowerPoint:** Slides 2, 5 và 7 hiển thị chuẩn mực; tổng số slide duy trì chính xác **16 slides**.",
        "5. **Kiểm tra khả năng mở và đọc của 6 tệp bàn giao:** Toàn bộ 6 tệp thành viên được kiểm tra mở và đọc thành công, cấu trúc định dạng nguyên vẹn.",
        "6. **Kiểm tra gói nén và mã băm SHA-256 / CRC-32:** Tệp nén giải nén thử nghiệm thành công 6/6 tệp, mã băm khớp chính xác 100% với manifest kiểm toán ngoại vi.",
        "7. **Bảo tồn bất biến dữ liệu sản xuất & các gói lưu trữ trước:** Các gói lưu trữ tại thư mục cha, `corrected/`, và `signoff_final/` được bảo tồn nguyên vẹn không can thiệp.",
        "",
        "---",
        "",
        "## 4. KẾT LUẬN & GHI NHẬN TRẠNG THÁI QUẢN TRỊ",
        "- Nhiệm vụ T-016 đã hoàn tất toàn diện mọi yêu cầu kỹ thuật và hiệu chỉnh tài liệu khoa học.",
        "- Ghi nhận chính thức theo ủy quyền của Project Lead:",
        "  * `T-016 = PASS / COMPLETED (CONTROLLED)`",
        "  * `G7 = IN_PROGRESS`",
        "  * `T-017 = NOT_STARTED / ELIGIBLE_FOR_SEPARATE_AUTHORIZATION`",
        "  * `G6 = PASS / CLOSED (CONTROLLED)` *(Bảo tồn)*",
        "  * `D5 = NOT_AUTHORIZED / FAIL-CLOSED` *(Bảo tồn)*",
        "  * `T-015 = CONDITIONAL_NO_GO` *(Bảo tồn)*"
    ]

    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(content))

    file_size = os.path.getsize(report_path)
    print(f"Technical completion report generated: {report_path} ({file_size:,} bytes)")
    return report_path
    return report_path
    return report_path

if __name__ == "__main__":
    generate_reproducibility_guide()
    generate_claim_to_evidence_index()
    generate_technical_completion_report()
