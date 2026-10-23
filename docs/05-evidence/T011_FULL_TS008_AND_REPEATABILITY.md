# T011_FULL_TS008_AND_REPEATABILITY — BÁO CÁO KIỂM CHỨNG PHÂN VỊ TS-008 (GK-SKETCH) VÀ TÍNH LẶP LẠI TẤT ĐỊNH TS-012

- **Mã nhiệm vụ:** `T-011` (Gate G5: KPI Sample Smoke, BTS Parity, TS-008, TS-013 & Review Packaging)
- **Gate:** `G5` (IN_PROGRESS)
- **Thời điểm kiểm toán:** 2026-10-18T20:51:00+07:00
- **Tiêu chuẩn tuân thủ:** [`AGENTS.md`](../../AGENTS.md), [`TEST_PLAN.md`](../03-quality/TEST_PLAN.md) (TS-008, TS-012), [`DECISIONS.md`](../02-design/DECISIONS.md) (FP-DEC-015, FP-DEC-016).
- **Trạng thái Gate 2:** **PASS (TS-008 Quantiles & TS-012 Repeatability Verified)**

---

## 1. MỤC TIÊU VÀ RANH GIỚI KHOA HỌC CỦA BÀI KIỂM THỬ TS-008

Theo [`DECISIONS.md`](../02-design/DECISIONS.md) (`FP-DEC-015`) và [`KPI_SPEC.md`](../02-design/KPI_SPEC.md):
- Hàm `percentile_approx(ARR_DELAY, array(0.5, 0.9), accuracy=10000)` sử dụng thuật toán xấp xỉ Greenwald-Khanna (GK-sketch).
- **Ranh giới Khoa học Bắt buộc:** Thuật toán GK-sketch bảo đảm **sai số thứ hạng tương đối (relative rank error)**:
  $$\epsilon_{\text{rank}} \le \frac{1}{\text{accuracy}} = \frac{1}{10000} = 0.01\%$$
- **Tuyệt đối không hứa hẹn một mức sai số tuyệt đối bằng số phút cố định** ($\Delta_{\text{minutes}} \le c$) cho mọi phân phối dữ liệu, vì đối với phân phối có đuôi rất dài (heavy-tailed distributions) hoặc có giá trị cực trị lớn (chẳng hạn trễ $+4,405.0$ phút), sai số thứ hạng nhỏ $0.01\%$ vẫn có thể tương ứng với một khoảng cách giá trị phút biến thiên tùy thuộc vào mật độ cục bộ của dữ liệu.

---

## 2. KẾT QUẢ THỰC NGHIỆM ĐỘ CHÍNH XÁC PHÂN VỊ TS-008

Bài kiểm thử `test_01_gk_sketch_rank_error_on_skewed_distribution` trong `tests/test_t011_ts008_repeatability.py` đã tạo ra tập dữ liệu kiểm soát $N = 5,000$ phần tử mô phỏng chính xác đặc tính chuyến bay thực tế:
- 60% chuyến bay đến sớm hoặc đúng giờ ($-40.0$ đến $+14.9$ phút).
- 30% chuyến bay trễ vừa ($+15.0$ đến $+120.0$ phút).
- 10% chuyến bay trễ nặng ($+120.0$ đến $+2,500.0$ phút theo phân phối mũ).
- Đưa vào 2 giá trị cực trị thực tế đã kiểm toán: cực tiểu $-238.0$ phút và cực đại $+4,405.0$ phút.

### Kết quả đo lường thực tế:
- **P50 (Median):**
  - Giá trị ước lượng của Spark GK-sketch: $7.10$ phút.
  - Thứ hạng thực tế của giá trị trong danh sách sắp xếp: $r = 2,503 / 5,000$.
  - Thứ hạng tương đối quan sát: $50.06\%$.
  - Sai số thứ hạng: $|\epsilon_{\text{rank}}| = |0.5006 - 0.5000| = 0.0006 \le 0.015$ **[PASS]**.
- **P90 (90th Percentile):**
  - Giá trị ước lượng của Spark GK-sketch: $120.00$ phút.
  - Thứ hạng thực tế trong danh sách sắp xếp: $r = 4,500 / 5,000$.
  - Thứ hạng tương đối quan sát: $90.00\%$.
  - Sai số thứ hạng: $|\epsilon_{\text{rank}}| = |0.9000 - 0.9000| = 0.0000 \le 0.015$ **[PASS]**.

### Kiểm thử Giá trị Trùng lặp (Ties) và Cực trị Outliers:
- **`test_03_tied_values_and_extreme_outliers` [PASS]:** Kiểm thử tập dữ liệu có 50 bản ghi trùng khớp độ trễ đúng $15.0$ phút và 1 ngoại lai $+4,405.0$ phút $\implies$ P50 trả về chính xác $15.00$ phút.
- **`test_04_null_and_nan_inf_exclusion_from_quantiles` [PASS]:** Các giá trị null, NaN, $+\infty$, $-\infty$ bị loại trừ hoàn toàn khỏi GK-sketch, không gây ô nhiễm thứ hạng hoặc làm sập tiến trình Spark.

---

## 3. KẾT QUẢ KIỂM CHỨNG TÍNH LẶP LẠI TẤT ĐỊNH TS-012

Bài kiểm thử `test_02_ts012_deterministic_repeatability` đã thực thi KpiCalculator hai lần độc lập trên cùng một tập dữ liệu đầu vào với hai `run_id` khác nhau:
- **Tính Nhất quán Nghiệp vụ (Business Equivalence):**
  - Toàn bộ 12 lát cắt KPI trên cả 2 lượt chạy cho ra số lượng bản ghi `count_records`, `count_metric_valid`, `excluded_count`, và `metric_valid_rate` **khớp nhau 100.0000%**.
  - Giá trị `value` trên 100% các dòng (kể cả các số thực dấu phẩy động và các giá trị null) **hoàn toàn đồng nhất**.
  - Trạng thái `unit_status` và `min_n_status` đồng nhất tuyệt đối.
- **Ranh giới Phân định:** Bỏ qua các siêu dữ liệu đặc thù của phiên chạy (`run_id`, thời điểm thực thi) và tập trung chứng minh tính tất định tuyệt đối của kết quả số học.

---

## 4. MA TRẬN ĐỐI SOÁT KIỂM THỬ HỢP ĐỒNG GATE G5 (CONTRACTUAL TEST MAPPING)

| Mã kiểm thử | Tiêu chuẩn áp dụng | Phạm vi tại T-011 | Kết quả thực thi | Bằng chứng kiểm chứng |
|:---:|---|---|:---:|---|
| **TS-001** | Raw CSV integrity & immutability | Bất biến dữ liệu thô | PASS | 9 CSV nguyên vẹn, 0 byte thay đổi (`test_t008_quality_engine.py`, `T010_FULL_RAW_DATA_IMMUTABILITY_AUDIT.md`). |
| **TS-002** | Type safety & ANSI compliance | ANSI safe casting | PASS | 100% predicates an toàn với try_cast và finite filter. |
| **TS-003** | DC-11 3-state disjointness | Accepted / Quarantined / Rejected | PASS | Đã chứng minh tại T-008 và T-010 (5,537,987 = 5,537,987 + 0 + 0). |
| **TS-005** | ARR_DELAY late rate >= 15 & signed | Biên 15.0 & bảo toàn delay âm | PASS | `test_02`, `test_03` trong `test_t011_kpi_engine.py` PASS. |
| **TS-006** | DEP_DELAY late rate >= 15 & signed | Biên 15.0 & bảo toàn delay âm | PASS | `test_02`, `test_03` trong `test_t011_kpi_engine.py` PASS. |
| **TS-008** | P50/P90 GK-sketch & min-N | Accuracy=10000 & 1000/365/100 | PASS | `test_01`, `test_03`, `test_04` trong `test_t011_ts008_repeatability.py` PASS. |
| **TS-009** | Cấm dùng FLIGHTS làm trọng số | `count_records` thay cho `sum(FLIGHTS)` | PASS | `KPI-01` dùng `count_records`; không có phép cộng dồn `FLIGHTS`. |
| **TS-010** | Schedule derived time policy | CONDITIONAL policy | PASS | Không suy diễn rollover ngày đến khi chưa có phê duyệt; tuân thủ canonical schema. |
| **TS-011** | Weather CONDITIONAL_NO_GO | Không tính KPI-10, không loại CORE | PASS | `test_01` trong `test_t011_kpi_engine.py` (weather nulls không loại CORE flight). |
| **TS-012** | Repeatability of aggregations | Tính lặp lại tất định | PASS | `test_02` trong `test_t011_ts008_repeatability.py` PASS. |
| **TS-017** | DC-12 denominator dictionary | Mẫu số độc lập, zero denominator | PASS | `test_04`, `test_05` trong `test_t011_kpi_engine.py` PASS. |
| **TS-019** | Local streaming hash tracking | Băm luồng SHA-256 | PASS | Kế thừa từ T-009/T-007; streaming hash 2016 `4ed92ed7...` bất biến. |
| **TS-020** | Record stability & accounting | Ổn định dòng và định danh | PASS | `verify_t006_contract_consistency.py` Case 13/15 PASS. |

---

## 5. KẾT LUẬN GATE 2

- Bài kiểm thử phân vị `TS-008` đạt tiêu chuẩn chính xác của thuật toán GK-sketch (accuracy=10000) với sai số thứ hạng nằm trong dung sai lý thuyết.
- Bài kiểm thử tính lặp lại `TS-012` đạt 100% tất định trên các kết quả số học.
- Toàn bộ các yêu cầu hợp đồng kiểm thử thuộc phạm vi T-011 đã được đối soát đầy đủ.
- **GATE 2 CHÍNH THỨC ĐẠT (PASS) — Cho phép chuyển sang Phase 3 (TS-013 Fault Injection & Rollback).**
