# DATA_DICTIONARY — 34 trường Canonical v1

- Evidence: `canonical_schema_v1(1).md`, 9 `schema_YYYY.json` (audit 0.1.0).
- Không thêm bớt field schema; các giải thích ý nghĩa là diễn giải theo tên và báo cáo lịch sử, chỉ được coi **đã xác minh chính thức** khi nguồn provenance xác nhận.
- `KPI_SPEC.md` KPI-01..08 hiện CORE_DRAFT; các đơn vị của **7 trường đo delay/taxi/elapsed/air** chưa được chứng minh từ nguồn upstream, phải được T-003 + TS-018 xác minh trước G2 PASS. Không gắn nhãn phút đã VERIFIED chỉ từ thông lệ đặt tên.
- Logical canonical `string` có thể được lưu Arrow `large_string`; numeric float64, integer nullable Int64.

| Field | Logical dtype | Nhóm | Ý nghĩa mô tả | Lưu ý |
|---|---|---|---|---|
| `FL_DATE` | string | Lịch | Ngày phục vụ chuyến bay; raw schema string; processed 2016–2023 timestamp-like | Không diễn giải múi giờ; audit full 2016–2023 processed |
| `OP_CARRIER` | string | Danh mục | Mã hãng khai thác | So sánh hãng qua năm cần mapping lịch sử |
| `OP_CARRIER_FL_NUM` | float64 | Định danh | Số hiệu chuyến bay, lưu float64 | Không làm duy nhất business key khi chưa kiểm tra |
| `ORIGIN` | string | Danh mục | Sân bay khởi hành (mã) | Code/mapping cần xác minh |
| `DEST` | string | Danh mục | Sân bay đến (mã) | Code/mapping cần xác minh |
| `CRS_DEP_TIME` | string | Giờ dự kiến | Giờ khởi hành kế hoạch, string | Timestamp-like; không chứng minh 2400 |
| `DEP_TIME` | string | Giờ thực tế | Giờ khởi hành thực tế, string | Cross-midnight/timezone cần kiểm chứng |
| `DEP_DELAY` | float64 | Hiệu suất | Độ trễ khởi hành (signed), float64 | Đơn vị phút là cách hiểu từ trường lịch sử, xác minh source |
| `TAXI_OUT` | float64 | Hiệu suất | Thời gian taxi ra, float64 | Xác minh domain và đơn vị |
| `WHEELS_OFF` | string | Giờ thực tế | Thời điểm cất cánh, string | Timestamp parse/rollover guard |
| `WHEELS_ON` | string | Giờ thực tế | Thời điểm chạm đất, string | Timestamp parse/rollover guard |
| `TAXI_IN` | float64 | Hiệu suất | Thời gian taxi vào, float64 | Xác minh domain và đơn vị |
| `CRS_ARR_TIME` | string | Giờ dự kiến | Giờ đến kế hoạch, string | **Date component không chứng minh ngày đến thực** |
| `ARR_TIME` | string | Giờ thực tế | Giờ đến thực tế, string | Cross-midnight/timezone cần kiểm chứng |
| `ARR_DELAY` | float64 | Hiệu suất | Độ trễ đến (signed), float64 | KPI >=15 theo draft; finite_count audit 100% |
| `CRS_ELAPSED_TIME` | float64 | Hiệu suất | Thời lượng hành trình dự kiến, float64 | Không tự suy ra từ timestamp |
| `ACTUAL_ELAPSED_TIME` | float64 | Hiệu suất | Thời lượng hành trình thực tế, float64 | Domain/units validate |
| `AIR_TIME` | float64 | Hiệu suất | Thời gian trên không, float64 | Domain/units validate |
| `FLIGHTS` | float64 | Chưa rõ | Chỉ số lượng được lưu float64 | **BLOCKED** weight/grain chưa chứng minh |
| `MONTH` | Int64 nullable | Lịch | Tháng, nullable Int64 | Cross-check FL_DATE |
| `DAY_OF_MONTH` | Int64 nullable | Lịch | Ngày trong tháng, nullable Int64 | Cross-check FL_DATE |
| `DAY_OF_WEEK` | Int64 nullable | Lịch | Thứ trong tuần, nullable Int64 | Hệ đánh số phải xác minh |
| `ORIGIN_INDEX` | Int64 nullable | Index | Mã index sân bay đi, nullable Int64 | Không coi continuous metric |
| `DEST_INDEX` | Int64 nullable | Index | Mã index sân bay đến, nullable Int64 | Không coi continuous metric |
| `O_TEMP` | float64 | Thời tiết | Nhiệt độ nơi đi, float64 | **BLOCKED** đơn vị/provenance/time join |
| `O_PRCP` | float64 | Thời tiết | Lượng mưa nơi đi, float64 | **BLOCKED** đơn vị/provenance/time join |
| `O_WSPD` | float64 | Thời tiết | Tốc độ gió nơi đi, float64 | **BLOCKED** đơn vị/provenance/time join |
| `D_TEMP` | float64 | Thời tiết | Nhiệt độ nơi đến, float64 | **BLOCKED** đơn vị/provenance/time join |
| `D_PRCP` | float64 | Thời tiết | Lượng mưa nơi đến, float64 | **BLOCKED** đơn vị/provenance/time join |
| `D_WSPD` | float64 | Thời tiết | Tốc độ gió nơi đến, float64 | **BLOCKED** đơn vị/provenance/time join |
| `O_LATITUDE` | float64 | Vị trí | Vĩ độ sân bay đi, float64 | Verify entity mapping |
| `O_LONGITUDE` | float64 | Vị trí | Kinh độ sân bay đi, float64 | Verify entity mapping |
| `D_LATITUDE` | float64 | Vị trí | Vĩ độ sân bay đến, float64 | Verify entity mapping |
| `D_LONGITUDE` | float64 | Vị trí | Kinh độ sân bay đến, float64 | Verify entity mapping |

## Metadata không thuộc 34 cột raw
`source_year`, `source_row_number`, `flight_key` được đề cập trong audit canonical processed của dự án trước, nhưng không có trong 34 fields CSV schema. Nếu pipeline mới cần các cột này thì **phải tái tạo/nhập theo quy tắc versioned, ghi rõ nguồn**, không được tuyên bố đã có trong raw.

## Domain review bắt buộc
- Delay signed âm nghĩa đến/đi sớm theo quy ước dự kiến; chưa xác nhận đơn vị nguồn trực tiếp từ documentation gốc.
- Numeric extreme có `ARR_DELAY` tối đa hàng nghìn theo audit; không tự cắt/winsorize.
- `DAY_OF_WEEK` hệ đánh số phải đối chiếu với ngày.
- Các trục Airport/Carrier thay đổi cardinality qua năm; dùng mã hợp lệ và chú giải coverage.
- `FLIGHTS`: chưa biết mỗi hàng một flight event hay weighted count; denominator theo `DATA_CONTRACT.md` chỉ là accepted `count_records` (row-based), không phải `FLIGHTS` sum; raw/quarantine/reject báo cáo riêng.
- Không có `CANCELLED`, `DIVERTED`, `DISTANCE`, aircraft id, weather valid-time; không tự bổ sung.
