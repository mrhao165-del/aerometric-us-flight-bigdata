# T009-R2: INDEPENDENT BASELINE & SOURCE INTEGRITY AUDIT

**Task ID:** `T-009` (Remediation & Independent Corrective Audit R2)  
**Gate:** `G4`  
**Auditor:** Senior Big Data Architect & Repository Governance Engineer  
**Date:** 2026-10-17  
**Status:** `BASELINE_AUDITED_AND_VERIFIED`  

---

## 1. Xác Minh Git Baseline & Trạng Thái Repository (Git Baseline Verification)

Kiểm toán độc lập thực hiện trực tiếp trên hệ thống tệp và lịch sử Git cục bộ:

- **Git HEAD Full SHA:** `cda19fbde9b931f59339bfa4828ea9ad288683c5`
- **Current Branch:** `master`
- **Baseline Revert Target SHA:** `be1b81e676dde78767c05a0cd2420ec171ba960f` (Mốc hoàn thành `T009-UNBLOCK-R2`)
- **Phạm vi thay đổi từ baseline đến HEAD:**
  - Tổng số tệp thay đổi: 39 tệp (37 tệp tạo mới, 2 tệp sửa đổi quản trị).
  - Tệp sửa đổi: [`tools/check_working_tree_consistency.py`](../../tools/check_working_tree_consistency.py), [`docs/05-evidence/EVIDENCE_DELIVERABLE_REGISTER.json`](EVIDENCE_DELIVERABLE_REGISTER.json).
  - Tệp tạo mới: 10 mô-đun Python trong `src/flight_pipeline/`, 5 tệp kiểm thử trong `tests/`, `requirements.txt`, `.github/workflows/ci.yml`, 1 tool QA `tools/qa/test_t009_r1_validator_extension.py`, 12 tệp Markdown/JSON và 7 tệp log trong `docs/05-evidence/`.

---

## 2. Kiểm Toán Toàn Vẹn Dữ Liệu Nguồn (Raw Data Integrity Audit)

Kiểm tra trực tiếp 9 tệp dữ liệu bảng thô đặt tại `data/raw/tabular/`:

| Năm | Đường Dẫn Tệp CSV Thô | Kích Thước Vật Lý (Bytes) | Trạng Thái Git | Số Dòng Audited (schema_YYYY.json) |
|:---:|---|:---:|:---:|:---:|
| **2016** | `data/raw/tabular/2016/flight_with_weather_2016.csv` | 1,538,427,452 | Untracked (Ignored) | 5,537,987 |
| **2017** | `data/raw/tabular/2017/flight_with_weather_2017.csv` | 1,549,837,485 | Untracked (Ignored) | 5,575,872 |
| **2018** | `data/raw/tabular/2018/flight_with_weather_2018.csv` | 1,941,406,432 | Untracked (Ignored) | 6,986,842 |
| **2019** | `data/raw/tabular/2019/flight_with_weather_2019.csv` | 1,990,370,667 | Untracked (Ignored) | 7,161,827 |
| **2020** | `data/raw/tabular/2020/flight_with_weather_2020.csv` | 1,197,858,795 | Untracked (Ignored) | 4,312,091 |
| **2021** | `data/raw/tabular/2021/flight_with_weather_2021.csv` | 1,600,032,487 | Untracked (Ignored) | 5,755,666 |
| **2022** | `data/raw/tabular/2022/flight_with_weather_2022.csv` | 1,782,648,882 | Untracked (Ignored) | 6,413,416 |
| **2023** | `data/raw/tabular/2023/flight_with_weather_2023.csv` | 1,847,433,387 | Untracked (Ignored) | 6,645,461 |
| **2024** | `data/raw/tabular/2024/flight_with_weather_2024.csv` | 1,748,350,586 | Untracked (Ignored) | 6,284,841 |
| **TỔNG**| **9 Tệp CSV Thô (2016–2024)** | **15,196,366,173** | **Hoàn Toàn Không Bị Sửa** | **54,674,003** |

### Đối soát số liệu dòng 54,674,003 vs 54,670,361:
- Toàn bộ hồ sơ nguồn chuẩn tắc ([`README.md`](../../README.md), [`ARCHITECTURE.md`](../02-design/ARCHITECTURE.md), [`DECISIONS.md`](../02-design/DECISIONS.md), [`KPI_SPEC.md`](../02-design/KPI_SPEC.md), [`data_inventory.md`](inputs/data_inventory.md), và 9 manifest `schema_YYYY.json`) đều thống nhất tuyệt đối con số **54,674,003** dòng dữ liệu thô.
- Trong báo cáo tổng kết R1 ([`T009_R1_FINAL_TECHNICAL_REVIEW.md`](T009_R1_FINAL_TECHNICAL_REVIEW.md)), tác giả đã ghi nhầm con số `54,670,361` (lệch chính xác 3,642 dòng).
- Nguyên nhân sai lệch: Đây là lỗi đánh máy (clerical error) đơn lẻ trong phần tóm tắt văn bản Markdown của R1. Không có bất kỳ tệp dữ liệu thô nào bị thay đổi hay mất mát.
- **Khẳng định chuẩn tắc:** Tổng số dòng dữ liệu thô trong dataset đã audit là **54,674,003 dòng**.

---

## 3. Bảo Vệ Các Manifest Chuẩn Tắc (Manifest Preservation)

1. **`PACKAGE_MANIFEST.json`:**
   - Kích thước: `8,354 bytes`
   - SHA-256: `7c457207a6fefd2a45ad56a4c8ee8e3fb6194b8462f6ee24985f4e9534d61df1`
   - Trạng thái: Khớp tuyệt đối với hằng số ghim cứng `PINNED_PACKAGE_MANIFEST_SHA256`.
2. **`SOURCE_MANIFEST.json`:**
   - Kích thước: `2,479 bytes`
   - SHA-256: `5e11e619790e475260b19c70630d8faef9a902c9d55d2ca641320163c87447fc`
   - Trạng thái: Khớp tuyệt đối với hằng số ghim cứng `PINNED_SOURCE_MANIFEST_SHA256`.
3. **Historical Evidence:**
   - Toàn bộ các báo cáo, addendum và tệp log lịch sử thuộc các đợt G2, G3, T-006, T009-UNBLOCK-R1, T009-UNBLOCK-R2, và T009-R1 đều được bảo toàn nguyên trạng, không bị xóa hay ghi đè.

---

## 4. Kết Luận Kiểm Toán Baseline (Baseline Verdict)

Hệ thống lưu trữ, commit history và dữ liệu nguồn hoàn toàn nguyên vẹn. Môi trường kiểm toán đạt chuẩn cao nhất để tiến hành sửa đổi kỹ thuật có mục tiêu trong `T009-R2`.
