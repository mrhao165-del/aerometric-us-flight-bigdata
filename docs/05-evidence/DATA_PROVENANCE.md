# DATA_PROVENANCE — Nguồn gốc và lịch sử dữ liệu

## Bằng chứng được cung cấp
- `data_inventory.md`: 9 file `flight_with_weather_YYYY.csv` ở `data/raw/tabular/{year}/`, thêm 27 file `.pt` Flight Chain.
- 9 báo cáo `schema_YYYY.json`: metadata được kiểm toán qua `pandas_chunked` ngày 23/08/2026, 34 cột và 54,674,003 rows tổng cộng.
- `canonical_schema_v1(1).md`: các field nhóm và logical dtypes.
- `canonical_schedule_datetime_representation_audit.md`: audit 48,389,162 rows processed 2016–2023 ngày 26/08/2026.
- `leakage_audit.md`: kiểm toán prediction-time dành cho pipeline Aeolus ATL cũ, không phải bằng chứng weather science cho đồ án mới.

## Chưa xác minh
- Địa chỉ public nguồn gốc đầu tiên, giấy phép sử dụng, chuẩn bảng gốc, phương pháp lựa chọn completed flights, phạm vi hãng/sân bay, ngày phiên bản dataset, join weather chi tiết và đơn vị weather.
- Việc `.pt` train/test/val có gì bên trong: không đọc và **không cần** cho scope này.
- Bản gốc dữ liệu có chứa cancelled/diverted không: nguồn Tabular nhận được không có hai cột trạng thái.
- Checksum SHA-256 raw: JSON có file_size/mtime/source_relative_path, **không có digest nội dung** theo nội dung đã đọc. Matching metadata (`METADATA_MATCH_ONLY`) không xác nhận content identity; khi mismatch chưa lý giải = `IDENTITY_UNVERIFIED` cho đến khi kiểm chứng bổ sung.

## Quy trình kiểm chứng cần làm T-001
1. Xác minh nguồn và license từ tài liệu/kho tải gốc được nhóm cung cấp.
2. So sánh schema source với 34 fields, ghi mọi tiền xử lý có trước.
3. Xác minh hoàn chỉnh flight grain, year/year coverage và lý do tất cả ARR_DELAY nonmissing.
4. Xác minh đơn vị và join time/coordinates weather; nếu không thì giữ mô tả weather ở mức dữ liệu phụ chưa diễn giải.
5. Lưu source URLs, version, content SHA256 nếu thực hiện được, license, process logs trong manifest mới do nhóm tạo; không retroactively tự ghi vào audit cũ. Nếu không có raw digest phải ghi trạng thái identity minh bạch, không tự khẳng định đã VERIFIED.
6. Kiểm chứng nguồn và units/sign/domain 7 trường delay/taxi/elapsed/air, giữ bằng chứng cho T-003/TS-018; nếu không đủ, G2 còn BLOCKED.

## Immutable evidence
Bản sao input ở `docs/05-evidence/inputs/` dùng để tái thẩm định; không sửa. Nội dung này không phải xác nhận quyền sử dụng nguồn gốc.
