# G6 Final Row Accounting Reconciliation & Conservation Audit

**Document ID:** `DOC-G6-ROW-ACC-001`  
**Classification:** DATA CONTRACT COMPLIANCE & ACCOUNTING RECONCILIATION  
**Task Reference:** TS-018 / Gate G6 Operational Readiness  
**Governing Standard:** DATA_CONTRACT.md (DC-11, DC-12), KPI_SPEC.md  
**Date:** 2026-10-20  
**Status:** RECONCILED & GOVERNANCE COMPLIANT  

---

## 1. Executive Accounting Principles

Data Contract rules **DC-11** (Three-way partition of input records) and **DC-12** (No unclassified records) establish the fundamental conservation law for all flight data ingestion in the US Flight Performance Analysis repository:
$$\forall y \in [2016 \dots 2024]: \quad \text{raw}_y = \text{accepted}_y + \text{quarantined}_y + \text{rejected}_y$$

Where:
- $\text{accepted}_y$: Chuyến bay đạt toàn bộ schema, range checks, và validation rules; được ghi vào production Parquet curated dataset và dùng cho tính toán 8 CORE KPI.
- $\text{quarantined}_y$: Chuyến bay có dữ liệu bất thường hoặc xung đột logic (ví dụ: thời gian bay âm, arrival time trước departure time mà không giải thích được bởi múi giờ, thiếu trường bắt buộc của chuyến bay đã hoàn thành), được cô lập vào quarantine store.
- $\text{rejected}_y$: Bản ghi hỏng nặng cấu trúc, trùng lặp hoàn toàn (duplicate key), hoặc vi phạm contract không thể phân tích.

Các tập hợp $\text{accepted}$, $\text{quarantined}$, và $\text{rejected}$ là **rời nhau hoàn toàn (mutually exclusive)** và **vét cạn (collectively exhaustive)** trên toàn bộ tập nguồn raw.

---

## 2. Canonical Source Inventory Across 9 Years (2016–2024)

Dữ liệu nguồn thô đã được niêm phong và đối chiếu qua các Gate G0–G5 ghi nhận chính xác **54.674.003 hàng** trên 9 năm:

| Năm (Year) | Canonical Raw Rows | Coverage Status | Quản trị / Ghi chú |
| :---: | :---: | :---: | :--- |
| **2016** | 5,617,658 | FULL | Baseline T-010 benchmark (Option B quy định tái nhập) |
| **2017** | 5,677,990 | FULL | TranStats on-time reporting |
| **2018** | 7,213,446 | FULL | Mở rộng danh sách hãng hàng không báo cáo |
| **2019** | 7,422,037 | FULL | Khớp 100% chứng từ TS-018 vật lý (7.422.037 hàng CSV) |
| **2020** | 4,688,354 | FULL | Giai đoạn đại dịch COVID-19 (suy giảm sản lượng bay) |
| **2021** | 6,311,871 | FULL | Phục hồi sau COVID-19 |
| **2022** | 7,004,628 | FULL | Sản lượng phục hồi cao |
| **2023** | 6,942,654 | FULL | Tăng trưởng ổn định |
| **2024** | 3,795,365 | **PARTIAL** | **Thiếu tháng 03/2024 (quản trị theo OR-05)** |
| **TỔNG CỘNG** | **54,674,003** | — | **TỔNG SỐ HÀNG RAW ĐÃ AUDIT** |

> [!IMPORTANT]
> Theo quy tắc quản trị `AGENTS.md`: Con số 54.674.003 là **"số hàng trong dataset đã audit"**, KHÔNG được gọi là "tổng chuyến bay thực tế của Mỹ" vì năm 2024 chỉ có dữ liệu bán phần (thiếu tháng 3 do gián đoạn nguồn phát hành, OR-05).

---

## 3. Khắc phục Sai lệch Kế toán Cũ (Flaw S02)

### 3.1 Sai lệch của bản dự thảo cũ
Trong bản dự thảo kiểm toán trước đây, validator quy định:
$$\sum_{y=2016}^{2024} accepted_y == 54,674,003$$

Quy tắc này sai nghiêm trọng về mặt toán học và vi phạm hợp đồng dữ liệu DC-11/12 vì:
1. Nó đồng nhất tổng số hàng thô ($raw$) với tổng số hàng hợp lệ ($accepted$).
2. Nếu pipeline thực tế phát hiện 10.000 bản ghi lỗi và đưa vào quarantine ($\text{quarantined} = 10,000$), thì $\text{accepted} = 54,664,003 < 54,674,003$. Khi đó, validator cũ sẽ báo lỗi **FAIL**, từ chối một đợt chạy ETL hoàn toàn chuẩn mực và tuân thủ hợp đồng!
3. Ngược lại, nếu một đợt chạy ghi nhận $\text{raw} = 100$, nhưng gán $\text{accepted} = 100$, $\text{quarantined} = 20$, validator cũ không phát hiện được sự phá vỡ định luật bảo toàn $100 \neq 120$.

### 3.2 Quy tắc Kế toán Mới Được Chuẩn hóa
Trong module `tools/qa/verify_multiyear_snapshot.py`, quy tắc kế toán đã được tái cấu trúc triệt để:
1. **Bảo toàn cấp năm (Per-Year Conservation):**
   $$\forall y: \quad raw\_rows_y == accepted\_rows_y + quarantined\_rows_y + rejected\_rows_y$$
2. **Khớp số liệu nguồn thô chính thức (Canonical Raw Match):**
   $$\forall y: \quad raw\_rows_y == \text{CANONICAL\_SOURCE\_ROW\_COUNTS}[y]$$
   $$\sum_{y=2016}^{2024} raw\_rows_y == 54,674,003$$
3. **Tổng hợp động Accepted (Dynamic Aggregation):**
   $$total\_accepted = \sum_{y=2016}^{2024} accepted\_rows_y \le 54,674,003$$
   Tổng số accepted được tính toán động và báo cáo trong manifest, không bị ép buộc bằng hằng số giả định.
4. **Kiểm tra kiểu dữ liệu nghiêm ngặt:**
   Tất cả 4 trường kế toán phải là số nguyên không âm (`int`, không chấp nhận kiểu `bool`, `float`, `str`, hoặc giá trị âm).

---

## 4. Minh chứng Kế toán Thực nghiệm

Hai kịch bản kế toán đã được kiểm chứng tự động trong `tests/test_multiyear_snapshot_policy.py`:

### Kịch bản A: Ideal Zero-Quarantine Run
- $raw = 54,674,003$
- $accepted = 54,674,003$
- $quarantined = 0$
- $rejected = 0$
- **Kết quả:** `PASS` (Cả 9 năm bảo toàn, tổng raw = 54.674.003).

### Kịch bản B: Realistic Production Run với Quarantine & Rejects
- Năm 2019: $raw = 7,422,037$, $accepted = 7,420,000$, $quarantined = 2,000$, $rejected = 37$.
- Các năm khác: $quarantined = 0, rejected = 0$.
- Tổng $raw = 54,674,003$; Tổng $accepted = 54,671,966$.
- **Kết quả:** `PASS` (Validator chấp nhận đợt chạy hợp lệ, ghi nhận đúng tỷ lệ hợp lệ $accepted / raw = 99.996\%$).

### Kịch bản C: Gian lận Kế toán (Unbalanced Accounting)
- Năm 2019: $raw = 7,422,037$, $accepted = 7,422,037$, $quarantined = 5,000$, $rejected = 0$ ($7,422,037 \neq 7,427,037$).
- **Kết quả:** `FAIL (UNBALANCED_ROW_ACCOUNTING)` (Validator lập tức fail-closed chặn đợt chạy).

---

## 5. Kết luận

Hệ thống kế toán số hàng cho Gate G6 hiện tại đã đạt độ chính xác toán học tuyệt đối, bảo vệ tính toàn vẹn của hợp đồng dữ liệu DC-11/12, ghi nhận trung thực rủi ro dữ liệu bán phần 2024 (OR-05), và sẵn sàng phục vụ việc kiểm toán sản phẩm production khi Project Lead cấp phép T-012.
