# DATA_CONTRACT — Hợp đồng chất lượng dữ liệu và mẫu số

**Version:** docs-v1.1 / DESIGN_PROPOSED. Là owner duy nhất của thuật ngữ accounting; công thức của từng KPI thuộc `KPI_SPEC.md`. Không thay thế canonical storage schema v1. Phải phê duyệt qua T-001/002/003 và chạy test trước khi coi là vận hành.

## Ingestion & source identity
- Đầu vào: `data/raw/tabular/{year}/flight_with_weather_{year}.csv` (2016–2024) chỉ đọc; 9 CSV chưa nằm trong ZIP này.
- `source_signature` của JSON chỉ gồm **đường dẫn tương đối, size và modified_time**; đây là phép so metadata để cảnh báo drift, **không phải bằng chứng identity nội dung**. Copy file có thể đổi mtime hoặc content có thể thay đổi mà metadata tương tự.
- Nếu metadata khác: ghi `METADATA_MISMATCH`, yêu cầu kiểm tra chứng cứ nội dung / checksum có nguồn tin cậy; chưa đủ thì `IDENTITY_UNVERIFIED`, dừng publish; **không** sửa audit JSON. Nếu metadata trùng nhưng không có checksum: `METADATA_MATCH_ONLY`, không gọi `CONTENT_VERIFIED`.
- Khi có SHA-256 raw từ nguồn/kiểm toán được duyệt, so hash để xác định content identity. Hash của bản sao MD/JSON trong `SOURCE_MANIFEST.json` **không** xác thực raw.
- Schema 34 cột và layout từ `DATA_DICTIONARY.md` và 9 JSON; drift cấu trúc → fail trước publish. `source_year` metadata đáng tin từ file được xác minh. Không tự coi `source_row_number` Spark phân tán là ổn định; chỉ sử dụng nếu chứng minh reproducible physical row offset hoặc cơ chế ID khác được duyệt.

## Rule catalog
| ID | Field | Quy tắc | Invalid / chưa rõ |
|---|---|---|---|
| DC-01 | `FL_DATE` | Lưu raw text; parse service date theo format được kiểm tra và đối chiếu năm | Gắn flag; chưa nhận chuẩn nếu thiếu date |
| DC-02 | `CRS_DEP_TIME`, `CRS_ARR_TIME`, actual time | Giữ nguyên text; không dựng overnight/zone timestamp trước T-004 | Derived timestamp = NULL/NOT_AVAILABLE |
| DC-03 | `ARR_DELAY`, `DEP_DELAY` | Numeric finite, giữ dấu; unknown/nonfinite không làm 0 | Metric-specific exclusion, không tự loại khỏi tất cả KPI |
| DC-04 | `TAXI_OUT`, `TAXI_IN`, `AIR_TIME`, `ACTUAL_ELAPSED_TIME`, `CRS_ELAPSED_TIME` | Units và domain (không âm, nếu được nguồn xác nhận), finite và outlier flags | Gắn flag; chính sách valid/exclude cần duyệt T-003 |
| DC-05 | `OP_CARRIER`, `ORIGIN`, `DEST` | Trim và normalize có trace; chưa rõ mapping hãng theo năm không tự gộp | Unmapped/invalid flag; group unknown policy được duyệt |
| DC-06 | `FLIGHTS` | Giữ dữ liệu, không sum/weight trước T-002 | KPI-12 BLOCKED |
| DC-07 | 6 Weather fields | Giữ raw + null flags; không gán units, valid time hoặc bin từ tên cột | RQ-06 CONDITIONAL_NO_GO nếu thiếu provenance |
| DC-08 | `MONTH`, `DAY_OF_MONTH`, `DAY_OF_WEEK` | Kiểm chứng so với service date và quy tắc thứ | Không overwrite nguồn khi mismatch |
| DC-09 | Airport indices/coordinates | Kiểm chứng mapping nếu dùng; index không phải metric liên tục | Không dùng khi thiếu map |
| DC-10 | Duplicates | Exact row hash ≠ flight event identity; ghi cả 2 mức | Không deduplicate business records tự động |

## Row accounting — nguồn định nghĩa duy nhất (DC-11)
Trong **mỗi `source_year` và `run_id`**, toàn bộ input data records (không tính header) được phân loại đúng **một** trạng thái, loại trừ lẫn nhau:
- `raw_row_count`: tổng records đầu vào mà reader xác định (kể cả invalid); record hỏng nặng phải được đếm/recovery từ nguồn hoặc đánh `ACCOUNTING_UNVERIFIED` và không publish.
- `accepted_row_count`: records đáp ứng **quy tắc hợp lệ cốt lõi đã phê duyệt**; có thể thiếu riêng `ARR_DELAY` hay Weather mà vẫn accepted nếu core-record policy cho phép. Không đánh đồng accepted với mọi metric valid.
- `quarantined_row_count`: records đọc được nhưng bị giữ riêng vì vi phạm core-record rules hoặc trường không thể diễn giải; có reason codes, không thuộc accepted.
- `rejected_row_count`: records không parse/recover được theo schema CSV; giữ count và diagnostics; không thuộc accepted/quarantine.
- Invariant **`raw_row_count = accepted_row_count + quarantined_row_count + rejected_row_count`**, không có trạng thái thứ tư. Mọi điều kiện để phân loại ba nhóm phải được duyệt ở T-002/003; hiện là thiết kế, không phải số đã chạy.
- Accounting raw/quarantine/reject được công bố ở **cấp năm nguồn**; không ép records không parse ra carrier/month/route giả. Các bảng group KPI được tính **chỉ từ accepted rows**. Nếu nhóm có missing category, dùng explicit `UNKNOWN` hoặc cô lập theo policy G2, không mất hàng im lặng.

## Metric-specific metadata — cùng một nghĩa trên tất cả KPI (DC-12)
Với một cohort `C` của accepted records sau **bộ lọc/group được công bố**, và một submetric `m`:
- `count_records` = `accepted_row_count(C)`, số hàng accepted thuộc cohort/group.
- `count_metric_valid` = `metric_eligible_count(m,C)`, số hàng accepted **đủ điều kiện cho chính submetric** sau numeric finite/domain và exclusion đã định nghĩa.
- `excluded_count` = `metric_excluded_count(m,C)` = `count_records - count_metric_valid` (có reason summary); không bao gồm raw quarantined/rejected trong cohort.
- `metric_valid_rate` = `count_metric_valid / count_records` **khi** `count_records>0`; nếu `count_records=0` → `null` kèm `ZERO_DENOMINATOR`, không xuất 0%.
- `ingest_acceptance_rate` = `accepted_row_count/raw_row_count` (cấp source_year, khi `raw_row_count>0`); **khác** `metric_valid_rate`.
- `source_coverage_status` = `UNKNOWN/PARTIAL/VERIFIED_WITH_SCOPE` + provenance; **không phải** tỷ lệ số chuyến của Mỹ khi không có known external population denominator.
- Cấm nhãn mơ hồ `coverage_rate` không có hậu tố. Đối với KPI-07/08 có nhiều measure, **mỗi submetric một denominator và valid rate**, không copy denominator của measure khác.
- KPI-01 count records được coi có `count_metric_valid=count_records`, `excluded_count=0`, `metric_valid_rate=1` nếu N>0; nhóm trống là null rate. KPI dựa vào `FLIGHTS` vẫn bị chặn đến khi T-002.

## GO/NO-GO
- RQ-01..05: chỉ cho phép xuất bản khi provenance/cohort/units/denominator của 8 CORE KPIs được T-001..003 chứng minh và review; năm 2024 nằm trong phạm vi mô tả.
- Cancelled/diverted: `NOT_COMPUTABLE` từ 34 cột hiện hữu. Weather: GO có evidence hoặc `CONDITIONAL_NO_GO`. Derived cross-midnight: `NOT_AVAILABLE` trừ khi T-004 GO. Các blockers chuyên biệt không làm vô hiệu KPI dùng trực tiếp `ARR_DELAY` sau validation.
- Không drop extreme/outlier bằng default; chỉ flag, cung cấp sensitivity riêng theo protocol.
