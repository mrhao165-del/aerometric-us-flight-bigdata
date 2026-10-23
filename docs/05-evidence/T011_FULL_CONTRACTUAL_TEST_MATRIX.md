# T011_FULL_CONTRACTUAL_TEST_MATRIX — MA TRẬN KIỂM THỬ HỢP ĐỒNG GATE G5

- **Mã nhiệm vụ:** `T-011` (Gate G5: KPI Sample Smoke, BTS Parity, TS-008, TS-013 & Review Packaging)
- **Gate:** `G5` (IN_PROGRESS)
- **Thời điểm kiểm toán:** 2026-10-18T21:04:00+07:00
- **Tiêu chuẩn tuân thủ:** [`AGENTS.md`](../../AGENTS.md), [`TEST_PLAN.md`](../03-quality/TEST_PLAN.md), [`BACKLOG.md`](../01-planning/BACKLOG.md).
- **Trạng thái:** **VERIFIED**

---

## 1. MA TRẬN ĐỐI CHIẾU 20 BÀI KIỂM THỬ QUY CHUẨN (TS-001..TS-020)

| Mã test | Tên bài kiểm thử quy chuẩn | Gate quy định | Tình trạng thực thi tại T-011 | Kết luận & Ranh giới bằng chứng |
|:---:|---|:---:|:---:|---|
| **TS-001** | Raw CSV schema & byte-level integrity | G4 / G5 / G6 | **PASS** | 9 CSV nguồn 2016–2024 bất biến 100%, không bị sửa đổi hay ghi đè. |
| **TS-002** | Safe type casting & ANSI mode compliance | G4 / G5 | **PASS** | 100% predicates trong `predicates.py` và `aggregators.py` dùng try_cast và finite numeric filter. |
| **TS-003** | DC-11 3-state disjoint row accounting | G4 / G5 / G6 | **PASS** | Hạch toán `raw == accepted + quarantined + rejected` rời nhau và đầy đủ; F04 kiểm chứng abort khi mất cân bằng. |
| **TS-004** | Full 9-year ETL reconciliation | G6 | **PENDING_G6** | Chỉ chạy ở Gate G6 sau khi TS-018 đạt PASS; cấm chạy sớm. |
| **TS-005** | ARR_DELAY late rate >= 15 & signed mean | G2 / G5 | **PASS** | Điểm biên đúng 15.0; bảo toàn dấu âm chuyến bay sớm (`test_t011_kpi_engine.py`). |
| **TS-006** | DEP_DELAY late rate >= 15 & signed mean | G2 / G5 | **PASS** | Điểm biên đúng 15.0; bảo toàn dấu âm (`test_t011_kpi_engine.py`). |
| **TS-007** | Pipeline integration & CSV reader | G4 / G5 | **PASS** | Kế thừa từ T-007; đọc an toàn với kiểu chuỗi nguyên bản. |
| **TS-008** | P50/P90 GK-sketch & min-N thresholds | G2 / G5 / G6 | **PASS** | Sai số thứ hạng $\le 0.015$ trên phân phối lệch; kiểm chứng ngưỡng 1000/365/100 (`test_t011_ts008_repeatability.py`). |
| **TS-009** | Cấm dùng FLIGHTS làm trọng số đếm | G2 / G5 / G7 | **PASS** | `KPI-01` dùng `count_records`; không cộng dồn `FLIGHTS` (`FP-DEC-010`). |
| **TS-010** | Derived schedule time policy | CONDITIONAL | **PASS** | Tuân thủ chính sách CONDITIONAL; không suy diễn ngày đến. |
| **TS-011** | Weather CONDITIONAL_NO_GO compliance | G2 / G6 | **PASS** | Tuân thủ FP-DEC-017: Không tính KPI-10, không loại chuyến bay CORE vì thiếu thời tiết. |
| **TS-012** | Deterministic aggregation repeatability | G5 / G6 | **PASS** | Kết quả số học đồng nhất 100% trên nhiều lần chạy độc lập (`test_t011_ts008_repeatability.py`). |
| **TS-013** | Safe publication & non-destructive rollback | G5 | **PASS** | 8/8 kịch bản lỗi F01..F08 đạt 100% PASS trong sandbox cô lập (`test_t011_fault_injection.py`). |
| **TS-014** | Production resource & memory benchmark | G5 | **PASS** | Kế thừa từ T-010 (Run 1: 49.22s, Run 2: 64.35s, RSS 2.16 GiB, Heap 1.05 GiB). |
| **TS-015** | Weather correlation non-causal protocol | G7 | **PENDING_G7** | Thuộc phạm vi báo cáo phân tích cuối cùng. |
| **TS-016** | Panel consistency & missing March 2024 | G6 / G7 | **PASS (Design/Smoke)** | Năm 2024 tự động mang nhãn `source_coverage_status = PARTIAL` (`OR-05`). |
| **TS-017** | DC-12 metrics denominator dictionary | G4 / G5 | **PASS** | Mẫu số độc lập cho từng submetric; xử lý mẫu số 0 ra null và mã `ZERO_METRIC_DENOMINATOR`. |
| **TS-018** | Seven CORE measure units parity vs BTS | G5 | **BLOCKED_BEFORE_G6** | Reconciler hoàn thành và kiểm chứng thuật toán 100%; dữ liệu thật BTS chưa có $\implies$ Chặn Gate G6. |
| **TS-019** | Streaming SHA-256 hash tracking | G4 / G5 | **PASS** | Kế thừa từ T-009/T-007; băm luồng SHA-256 xác thực bất biến. |
| **TS-020** | Row identifier & accounting stability | G4 / G6 | **PASS** | Không deduplicate tùy tiện; bảo tồn cặp trùng khóa `YX 3624` (`OR-02`). |

---

## 2. TỔNG KẾT TRẠNG THÁI KIỂM THỬ

- **Số bài kiểm thử đạt PASS tại phạm vi T-011:** 17/20 bài.
- **Số bài kiểm thử PENDING theo đúng lộ trình kế hoạch:** 2 bài (`TS-004` tại Gate G6, `TS-015` tại Gate G7).
- **Số bài kiểm thử BỊ CHẶN BỞI DỮ LIỆU NGUỒN NGOÀI:** 1 bài (**`TS-018`** đối soát thực tế với BTS TranStats, khóa cổng trước Gate G6).
