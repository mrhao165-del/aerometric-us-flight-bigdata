# AeroMetric — Dashboard demo theo thiết kế Stitch

Website local gồm 7 trang, sử dụng HTML/CSS/JavaScript và Plotly.js được đóng gói offline. Không có Flask/FastAPI, database hoặc Spark runtime. Python chỉ đóng gói artifact và phục vụ file tĩnh trên loopback.

## Chạy bản đã đóng gói

Tại thư mục gốc repository, chạy:

```powershell
python -B dashboard/demo.py serve
```

Mở **http://127.0.0.1:8000/** bằng Chrome hoặc Edge. Giữ terminal mở; nhấn `Ctrl+C` để dừng. Nếu cổng bận, thêm `--port 8001` rồi mở cổng tương ứng. Không mở `index.html` bằng double-click vì trình duyệt cần HTTP để đọc module và JSON.

Bundle mặc định: `D:\Flight_Audit_Exports\DASHBOARD_DEMO\stitch_v3`. Bản này đã chứa JavaScript biểu đồ, font, dữ liệu và ảnh gốc; chạy demo không cần internet, PyArrow, Node hoặc npm. Cần Python 3.10 trở lên cho static server. Nếu server v1/v2 đang chạy, dừng bằng `Ctrl+C`, chạy lại lệnh trên rồi tải lại trang bằng `Ctrl+F5`.

```powershell
python -B dashboard/demo.py verify
```

`serve` cũng kiểm tra SHA-256 bundle trước khi mở cổng. Đây là kiểm tra tính toàn vẹn của gói local; không phải chứng thực danh tính upstream hoặc chữ ký nghiệm thu mới.

## Các trang và thao tác demo

| Trang | Nội dung và thao tác thực tế |
|---|---|
| Tổng quan | 4 KPI của cả năm chọn; biểu đồ sản lượng và tỷ lệ ARR/DEP theo 12 tháng của chính năm đó. Chọn chip năm để đổi đồng thời thẻ và biểu đồ. Tháng 3/2024 để trống. |
| Sản lượng | Khoảng năm; tổng bản ghi, cực đại/cực tiểu tháng, mean tháng quan sát; cột năm, đường tháng, heatmap 9×12. Bật/tắt đường mean và mốc chú thích. |
| Độ trễ | Tỷ lệ ARR/DEP, signed means, P50/P90 từng năm; chọn năm cho thẻ, chọn khoảng cho biểu đồ; bật/tắt chuỗi và baseline. |
| So sánh hiệu suất | Tab hãng, sân bay Origin/DEST, 10 cặp tuyến đối ứng 2019; chọn entity từ dropdown, thanh hoặc bảng. Xu hướng hãng/taxi giữ 9 năm, dùng trục năm tuyến tính và nhãn tại năm chọn. Ranking dùng tập đủ mẫu được công bố. |
| Giai đoạn 2020 | 2019–2021; sản lượng tuyệt đối hoặc % so với 2019; tỷ lệ ARR/DEP và dòng thời gian tháng; bật/tắt chú thích tháng 4/5. |
| Taxi & hành trình | Taxi-out/in, Air Time, Actual/CRS và hiệu 2 means; bảng N_valid riêng từng measure. |
| Dữ liệu & phương pháp | 4 giới hạn nghiên cứu; tìm 20 RES, lọc RQ, mở ảnh SVG gốc của 16 chart và tải PNG/SVG/register. |

Các bảng có sắp xếp và xuất CSV của **những hàng đang hiển thị**. Link “Parquet nguồn” tải **toàn bảng gốc**, không áp dụng bộ lọc giao diện. Các ảnh chính thức giữ nguyên cohort gốc; chọn năm ở trang khác không thay đổi ảnh.

Gợi ý trình diễn: chọn 2019/2020 tại Tổng quan → Sản lượng, xem ô thiếu T3/2024 → Độ trễ, chọn 2020 và đối chiếu P50/P90 → So sánh hãng/sân bay/tuyến → Giai đoạn 2020, đổi chế độ % → Taxi, chọn 2020 để thấy N CRS khác N Actual → tìm RES-018 và mở ảnh nguồn.

## Dữ liệu và ranh giới thống kê

- Run cố định: `t014_analysis_2016_2024_v4`, `kpi_run_2016_2024_v1`.
- 12 bảng T-014, 16 PNG + 16 SVG, 20 RES; 17.575 dòng KPI tổng hợp được chọn từ T-013 để cung cấp giá trị/metadata đúng cohort. Đây không phải một KPI run mới.
- 54.674.003 là số bản ghi accepted trong dataset đã audit, không phải tổng chuyến bay thực tế của Mỹ.
- 2024 `PARTIAL`: thiếu toàn tháng 3; 335/366 ngày. Đường tháng để khoảng trống, không điền 0/nội suy. Các trang đều hiện cảnh báo.
- Giữ dấu âm/dương, N_valid riêng từng measure; không trung bình cộng tỷ lệ hoặc phân vị. Chọn khoảng năm chỉ chọn các điểm đã công bố.
- Carrier-year, Origin-year, DEST-year và directed route-year là các family riêng. Không có filter giao Carrier × Airport × Route. Tuyến chỉ có 10 cặp năm 2019 trong MVP.
- FP-DEC-016: N_min carrier=1.000, airport=365, route=100; SUFFICIENT từ 3×N_min. Không gọi ngưỡng này là kiểm định ý nghĩa thống kê.
- OR-03: units được kiểm chứng mẫu TS-018 Option B, không xác thực toàn bộ 9 năm. OR-08 vẫn `IDENTITY_UNVERIFIED / ACCEPTED_NON_BLOCKING`; Weather ngoài CORE; D5 không được cấp quyền.
- CRS−Actual là **hiệu hai trung bình biên**, không phải mean hiệu từng chuyến, cũng không chứng minh hành vi đệm lịch trình.

## Tạo bundle mới khi sửa giao diện

Chỉ bước build cần môi trường PyArrow đã có trong dự án và internet để tải Plotly/font từ nguồn chính thức. Không cài thêm thư viện. Ví dụ:

```powershell
python -B dashboard/demo.py build --bundle D:/Flight_Audit_Exports/DASHBOARD_DEMO/stitch_v4
python -B dashboard/demo.py serve --bundle D:/Flight_Audit_Exports/DASHBOARD_DEMO/stitch_v4
```

Build từ chối đường dẫn nằm trong repository hoặc output đã tồn tại. Dữ liệu được hash/đối chiếu manifest trước khi chọn các hàng tổng hợp; tạo staging ngoài repo rồi rename thành bundle mới. Không sửa bundle đã xuất bản. Nếu mất mạng, bản đã build vẫn chạy được.

Không đọc raw/Curated trong build hoặc serve; không import pipeline, chạy Spark, tính lại CORE KPI, đổi con trỏ latest hoặc sửa evidence G6/G7. `bundle_manifest.json` ghi source paths/hashes và vendor URLs/hashes. Source ứng dụng nằm duy nhất trong `dashboard/`; không có commit được tạo.

## Kiểm tra

```powershell
python -B -m unittest discover -s dashboard/tests -p "test_*.py" -v
node --test dashboard/tests/core.test.mjs dashboard/tests/app.test.mjs
```

Để test bundle khác: đặt `$env:AEROMETRIC_TEST_BUNDLE='D:/.../stitch_v4'` trước lệnh. Python tests kiểm tra artifact, N_valid, khoảng thiếu, immutable output, HTTP MIME/CSP và bề mặt chỉ đọc. Node tests kiểm tra biến đổi an toàn và render/event của cả 7 trang bằng DOM/Plotly test doubles, gồm các lựa chọn năm/entity đã xuất bản, 12 ô tháng cho mỗi năm, tọa độ shape trên trục tuyến tính và marker/nhãn của năm chọn. Heatmap được kiểm tra đủ 4 khoảng lọc, giá trị từng ô, vị trí chú thích thiếu, giới hạn trục và tooltip năm/tháng sau nhiều lần đổi bộ lọc.

`stitch_v1` được giữ nguyên để quay lại khi cần: `python -B dashboard/demo.py serve --bundle D:/Flight_Audit_Exports/DASHBOARD_DEMO/stitch_v1`. Thay đổi v2 chỉ ở hiển thị và kiểm tra đối chiếu monthly KPI; dữ liệu JSON cung cấp cho website giữ nguyên nội dung. Taxi sân bay vẫn theo năm vì chưa có cohort sân bay–tháng đã xuất bản.

V3 sửa heatmap mùa vụ: cả hai trục dùng chỉ số ô với tick là năm/tháng thực; chú thích thiếu nằm tại cột 2, hàng của năm 2024, không còn kéo giãn trục. Ma trận có 107/48/24/35 ô quan sát tương ứng Toàn kỳ / 2016–2019 / 2020–2021 / 2022–2024. Tháng 3/2024 vẫn là null. Dữ liệu JSON giữ nguyên từng byte so với v2; không tính lại KPI. Rollback gần nhất: `python -B dashboard/demo.py serve --bundle D:/Flight_Audit_Exports/DASHBOARD_DEMO/stitch_v2`.

**Giới hạn xác minh:** phiên triển khai không có trình duyệt khả dụng trong công cụ CUA (`listBrowsers=[]`). Chưa thực hiện screenshot/visual QA hoặc xác minh Plotly trên trình duyệt thật. Các bài kiểm tra DOM double không thay thế bước này. Trước buổi bảo vệ nên mở trên laptop, kiểm tra 7 trang ở độ rộng 1366/1440 và thử hover, lọc, xuất CSV, modal SVG khi ngắt internet.

Xem [DESIGN_RECONCILIATION.md](DESIGN_RECONCILIATION.md) để biết cách chuyển mockup sang dữ liệu thực. Log kiểm tra và snapshot bảo vệ project nằm ngoài repo tại `D:\Flight_Audit_Exports\DASHBOARD_DEMO\qa_v3\` cho bản sửa heatmap; các log cũ vẫn ở `qa\` và `qa_v2\`.
