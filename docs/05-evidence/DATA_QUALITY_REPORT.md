# DATA_QUALITY_REPORT — Tổng hợp G1 từ báo cáo audit

**Trạng thái:** evidence synthesis (không đọc lại toàn bộ CSV). Nguồn: 9 `schema_YYYY.json` v0.1.0, canonical/schema-time audit.

| Năm | Records | ARR_DELAY >=15 | Tỷ lệ trong finite ARR_DELAY | ARR_DELAY signed mean | Số mã hãng |
|---|---:|---:|---:|---:|---:|
| 2016 | 5,537,987 | 964,216 | 17.41% | 3.52 | 12 |
| 2017 | 5,575,872 | 1,028,626 | 18.45% | 4.32 | 12 |
| 2018 | 6,986,842 | 1,333,849 | 19.09% | 5.00 | 18 |
| 2019 | 7,161,827 | 1,368,348 | 19.11% | 5.38 | 17 |
| 2020 | 4,312,091 | 419,429 | 9.73% | -5.11 | 17 |
| 2021 | 5,755,666 | 983,228 | 17.08% | 2.95 | 17 |
| 2022 | 6,413,416 | 1,346,386 | 20.99% | 6.93 | 17 |
| 2023 | 6,645,461 | 1,365,190 | 20.54% | 6.57 | 15 |
| 2024 | 6,284,841 | 1,307,644 | 20.81% | 7.11 | 15 |
| **Tổng/tổng hợp** | **54,674,003** | **10,116,916** | **18.5041%** | **4.4771** | — |

Lưu ý: số liệu tổng hợp là phép tính thứ cấp trên JSON, không phải Spark KPI official. Mean toàn kỳ là trung bình gia quyền bằng số bản ghi của mean từng năm (vì năm có finite ARR_DELAY bằng row count theo audit).

## Schema & integrity
- 9/9 JSON đánh dấu `is_complete: true`, `column_count: 34`; mỗi năm cùng trường dữ liệu theo canonical v1.
- Kiểm toán full-row duplicate báo `0` trong từng năm bằng dual 64-bit hash: **không** chứng minh unique flight event business key hoặc loại trừ collision.
- `ARR_DELAY` missing=0, invalid/nonfinite=0 trong tất cả năm audit; không suy ra tất cả records thực tế (gồm cancellations) đều có ARR_DELAY.
- Weather: O_TEMP/O_PRCP/O_WSPD có cùng missing counts mỗi năm, tổng **13,474** / 54,674,003 (0.0246%); D_TEMP/D_PRCP/D_WSPD tổng **15,046** (0.0275%). Không fill zero.
- Cardinality hãng thay đổi (12→18→17→15 qua các giai đoạn); cần kiểm chứng company identity/coverage.

## Time audit
- 2016–2023 processed: 48,389,162 rows được audit, string timestamps thống nhất. `FL_DATE` 00:00; scheduled departure date components trùng service date; scheduled arrival date cũng trùng dù clock có thể thấp hơn departure.
- Kết luận explicit `AMENDMENT_REQUIRES_REVIEW`, `2400_SEMANTICS_NOT_PROVEN`.
- 2024 **không thuộc phạm vi** full schedule representation audit đó; schema JSON 2024 chỉ xác nhận riêng structural/date-year audit.

## Vấn đề đang chặn claim
1. Không có `CANCELLED`/`DIVERTED`; không tính tỷ lệ của chúng.
2. Không xác nhận số hàng = số chuyến có lịch; không xác nhận denominator toàn ngành.
3. Đơn vị/time join Weather chưa xác nhận; chỉ có missing/float quan sát.
4. Không dùng date component để dựng arrival-datetime xuyên ngày.
5. Chưa đánh giá logic thresholds/domain cho tất cả numeric columns hay temporal join ngoài các audit sẵn có.

## Ranh giới sử dụng ở docs-v1.1
- Tỷ lệ audit `ARR_DELAY>=15` chỉ dùng để đối chiếu run với cùng cohort; con số trong báo cáo này **không có `metric_valid_rate` hoặc `source_coverage_status` của pipeline mới**.
- Units của 7 trường delay/taxi/elapsed/air còn chờ T-003/TS-018; không nâng lên `VERIFIED` qua thống kê JSON.
- `source_signature` size/mtime không phải content checksum raw.

## Gate verdict
**G1 = PARTIAL** (đã có structural baseline, nhưng chưa đủ semantic/quality evidence cho tất cả KPI). Đóng mở riêng: KPI cơ bản có thể được thiết kế với metadata và test; Weather/overnight/cancellations vẫn bị gác hoặc blocked.
