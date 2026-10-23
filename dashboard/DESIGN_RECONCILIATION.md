# Đối chiếu thiết kế Stitch với implementation

Input: 7 cặp `code.html` / `screen.png` và `aerometric_research_console/DESIGN.md` trong `stitch_us_flight_performance_dashboard_2016_2024/`. Đã đọc HTML và xem các ảnh thiết kế. Giữ sidebar AeroMetric, canvas sáng, primary xanh, accent teal/cam, thẻ KPI, bố cục 2 biểu đồ, bảng và phần ghi chú nghiên cứu. CSS dùng chung thay cho Tailwind CDN; Inter và JetBrains Mono đóng gói local theo OFL.

| Thành phần mockup | Implementation và lý do |
|---|---|
| Số liệu/đường SVG minh họa | Plotly dùng giá trị T-014 và metadata T-013. Không dùng số liệu giả của mockup. |
| Sản lượng 2020 khoảng 4,69M, delay 11,2%, P90 28 trong thiết kế | Giá trị artifact: 4.312.091 bản ghi, arrival delay rate 9,72681235%, P90 14 phút. Nguồn `rq04_pandemic_comparison.parquet` và year KPI-01/02/06. |
| “Tổng chuyến bay Hoa Kỳ” | Gọi đúng “bản ghi accepted trong dataset”; tổng 54.674.003 không chứng minh market coverage. |
| Bộ lọc nhiều chiều và route toàn kỳ | Carrier-year, airport-role-year riêng; route giới hạn 10 cặp năm 2019 đã công bố. Không giả lập giao filter không có cohort. |
| Gộp KPI theo khoảng thời gian | Khoảng năm chỉ chọn các hàng/điểm gốc. Có SUM count trên các năm rời nhau; không tạo pooled rate/mean/quantile mới. |
| Mean/P90 đẹp nhưng không rõ mẫu | Tooltip/thẻ/bảng thể hiện N_valid của stream; âm vẫn âm; P50/P90 theo từng năm. |
| CI/bootstrap/p-value hoặc so sánh stable panel | Loại bỏ các yếu tố chưa có bằng chứng đã xuất bản; giữ thống kê mô tả. |
| Spark 3.5.1/32 executors/live processing | Dùng nhãn kết quả PySpark 4.0.1 theo bằng chứng môi trường; không có Spark chạy trên website. |
| Canceled/diverted/weather | Không có KPI hay filter; thiếu trường hoặc ngoài CORE đã duyệt. |
| 2024 nhìn như năm đầy đủ | Cảnh báo toàn ứng dụng; đánh dấu năm/cột/điểm; ô/đường tháng 3 trống. |
| “Schedule buffer” được hiểu như hành vi | Ghi “CRS − Actual: hiệu hai trung bình”; N CRS2020=4.312.090, N Actual2020=4.312.091. Không paired inference. |
| Nút export, biểu đồ nguồn | CSV thực của bảng hiển thị; tải bảng Parquet gốc; gallery 16 ảnh nguyên bản có PNG/SVG. |

Mọi chỉnh sửa trên chỉ ở tầng trình bày. Không chỉnh sửa register/chart/table hoặc evidence gốc. Bundle giữ bản tải xuống nguyên trạng của T-014, với hash đối chiếu nguồn.

Một số narrative phụ của register/chart không được tái diễn thành kết luận mới: RES-003 ghi nhận T4/2020, nhưng bảng tháng có đáy T5/2020; RES-017 chỉ hiển thị primary observation JFK2023, không sao chép thứ hạng phụ chưa khớp số; RES-018 không dùng context denominator trong register làm mẫu số chung của hiệu hai means. RES-010 và ảnh nguồn được trình bày với cohort gốc để người xem không hiểu ảnh là một chart được lọc theo RES. Các lưu ý đã được ghi tại giao diện; hồ sơ nghiệm thu giữ nguyên.

Các thành phần mới: UI, điều hướng, bộ lọc, tooltip, sắp xếp/xuất bảng, adapter và static server chỉ đọc. Chưa có đăng nhập, database, API dữ liệu động, dự đoán, thời tiết hoặc deployment public. Không thay đổi task/gate đã nghiệm thu.

Mức xác minh: dữ liệu/manifest được đọc và đối chiếu bằng adapter; module/render/event được test tự động. Visual fidelity trên trình duyệt thật **chưa xác minh** vì không có browser trong công cụ phiên này.

## Hiệu chỉnh biểu đồ thời gian trong stitch_v2

- Tổng quan: hai chart chuyển sang tháng của năm chọn; 4 thẻ vẫn là thống kê cả năm. Trục tháng có đủ T1–T12; T3/2024 trống và không nối đường qua khoảng thiếu. Không tạo tổng hợp quý mới.
- Taxi sân bay và xu hướng hãng: trục X tuyến tính 2016–2024, phạm vi cố định 2015,5–2024,5; shape năm và dữ liệu cùng tọa độ số. Năm chọn có marker lớn và nhãn giá trị. Năm không có cohort giữ null.
- Nguyên nhân lỗi cũ: shape nhận số năm trên trục category, có thể bị hiểu là ordinal index và làm giãn trục. Kiểm thử mới từ chối numeric year shape trên category axis, kiểm tra range và đủ tick.
- Giữ nguyên tất cả bảng/RES/ảnh và sản phẩm dữ liệu. Build v2 chỉ đối chiếu thêm số liệu tháng với stream KPI tương ứng; không tính lại KPI. Gói v1 giữ nguyên làm rollback target.
- Browser QA v2 vẫn chưa thể thực hiện: công cụ CUA không liệt kê trình duyệt khả dụng; chưa có screenshot nghiệm thu 1366/1440.

## Hiệu chỉnh heatmap mùa vụ trong stitch_v3

V2 đặt annotation “Thiếu” tại `y: '2024'` trên trục category. Plotly xử lý chuỗi số này như vị trí 2024 trong phạm vi trục, thay vì hàng 8 (toàn kỳ) hoặc 2 (2022–2024), làm heatmap bị ép gần như vô hình. Hai khoảng không chứa 2024 không có annotation này nên không gặp lỗi.

V3 dùng tọa độ ô số nguyên cho cả heatmap và annotation; trục X cố định [-0,5; 11,5], trục Y cố định [số_năm−0,5; −0,5]. Tick vẫn là T1–T12 và năm theo thứ tự từ trên xuống. Tooltip lấy năm/tháng/coverage qua customdata, không hiển thị chỉ số ô. Giữ nguyên bảng màu, số liệu và null tại T3/2024; không nội suy hay thay bằng 0.

Kiểm thử bao gồm đủ 4 khoảng, 107/48/24/35 ô quan sát, so khớp từng giá trị với bảng nguồn, annotation nằm trong phạm vi và chuyển bộ lọc qua lại. Dữ liệu JSON giữ nguyên so với v2, gói v2 giữ nguyên để rollback. Công cụ vẫn trả `listBrowsers=[]`; xác minh trực quan 1366/1440 chưa thực hiện.
