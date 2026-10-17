# PRD — Đặc tả yêu cầu đồ án

- **Phiên bản:** 1.0; **trạng thái:** Baseline theo mục tiêu người dùng; phương pháp và công nghệ vẫn PROPOSED.
- **Tên đề tài:** Phân tích hiệu suất các chuyến bay tại Hoa Kỳ (2016–2024).
- **Mục tiêu sản phẩm:** Xây dựng quy trình dữ liệu lớn có khả năng chuẩn hóa, kiểm toán và tổng hợp bộ dữ liệu tabular 9 năm, sau đó tạo kết quả thống kê/biểu đồ có thể tái lập để mô tả hiệu suất khai thác bay.
- **Người dùng đầu ra:** giảng viên đánh giá môn Big Data, nhóm sinh viên, người đọc báo cáo phân tích.

## Câu hỏi nghiên cứu
| ID | Câu hỏi | Kết quả dự kiến | Điều kiện |
|---|---|---|---|
| RQ-01 | Quy mô dữ liệu quan sát và phân phối theo năm/tháng thay đổi thế nào? | Bảng/biểu đồ số hàng và độ phủ | Giải thích không phải tổng quốc gia; xác minh flight grain |
| RQ-02 | Đúng giờ/chậm đến và chậm đi thay đổi theo thời gian ra sao? | % >=15 phút, trung bình và phân vị | Theo `KPI_SPEC` và phạm vi observed |
| RQ-03 | Khác biệt theo hãng, sân bay, tuyến bay? | Nhóm và so sánh có N, coverage | Ngưỡng cỡ mẫu, so sánh không gây hiểu lầm |
| RQ-04 | Năm 2020 khác giai đoạn xung quanh như thế nào? | Phân tích giai đoạn, tránh kết luận nhân quả | Thành phần mẫu thay đổi phải được công bố |
| RQ-05 | Chỉ số taxi và thời gian hành trình phản ánh hiệu suất ra sao? | Phân phối và xu hướng | Chỉ số đo trực tiếp; loại giá trị lỗi được log |
| RQ-06 (conditional) | Các nhóm thời tiết có liên hệ thế nào với chậm chuyến? | So sánh mô tả, không kết luận nhân quả | Đơn vị, provenance và join đã xác minh |

## Phạm vi IN
- 9 CSV Tabular 2016–2024; sơ đồ 34 cột do audit cung cấp.
- Kiểm toán cấu trúc/dữ liệu, phân tích KPI và các yếu tố thống kê quan sát; sử dụng công cụ Big Data (đề xuất PySpark/Spark SQL).
- Hệ thống báo cáo tĩnh hoặc dashboard chỉ khi đủ thời gian; có khả năng tái lập.
- Năm 2024 được phép tham gia phân tích mô tả; số liệu 2024 trong schema audit là bằng chứng khám phá dữ liệu, không phải kiểm chứng pipeline mới.

## Phạm vi OUT
- Dự đoán chậm chuyến, feature engineering/temporal holdout cho ML, ATL-only prediction, Flight Chain `.pt`, graph flight network.
- Khẳng định nguyên nhân chậm chuyến do thời tiết hoặc bất kỳ yếu tố nào từ dữ liệu quan sát.
- Tỷ lệ chuyến hủy/chuyển hướng từ CSV hiện tại (thiếu cột tương ứng).
- Tuyên bố đại diện tất cả chuyến bay tại Mỹ trước khi xác nhận định nghĩa, lọc và nguồn gốc bộ dữ liệu.
- API/web application production là tùy chọn, không phải deliverable mặc định.

## Yêu cầu chức năng
| ID | Yêu cầu | Ưu tiên | Bằng chứng nghiệm thu |
|---|---|---|---|
| REQ-01 | Đọc/kiểm tra dữ liệu 9 năm theo manifest, không sửa raw | Must | DATA/QC manifests, test |
| REQ-02 | Chuẩn hóa schema và dữ liệu vào Parquet có version | Must | schema diff, row-accounting |
| REQ-03 | Tổng hợp KPI theo năm, tháng, hãng, sân bay và tuyến | Must | Kết quả Spark và đối chiếu độc lập |
| REQ-04 | Kiểm tra và công bố denominator/coverage | Must | KPI output metadata |
| REQ-05 | Biểu đồ và báo cáo các RQ-01..RQ-05 | Must | Results Register và báo cáo |
| REQ-06 | Phân tích thời tiết (chỉ khi qua gate) | Should/conditional | units/provenance/stratification |
| REQ-07 | Re-run có cùng input và KPI version cho cùng kết quả | Must | run manifest, reproducibility test |
| REQ-08 | Trang dashboard tương tác | Could | Nghiệm thu riêng nếu kích hoạt |

## Yêu cầu phi chức năng
- Không load toàn bộ CSV (~15.2GB) vào Pandas đơn tiến trình làm đường chạy chính.
- Thực thi theo phân vùng năm, có batch/smoke, kiểm tra tài nguyên thực tế trước full run.
- Có log nguồn, phiên bản code/contract, số hàng qua từng bước, lỗi và kết quả kiểm thử.
- Tách clean/curated và raw; có rollback an toàn.
- Đảm bảo không nhầm `n hàng` với `n chuyến`, và không ngầm chuyển đổi thời gian/lượng thời tiết.

## Đầu ra bàn giao
1. Mã nguồn kiểm thử được, môi trường và hướng dẫn chạy.
2. Bảng processed/curated có manifest hoặc báo cáo nếu không thể lưu toàn bộ.
3. Các bảng KPI + trực quan hóa + giải thích giới hạn dữ liệu.
4. Báo cáo đồ án và slide/demo (format phụ thuộc đề bài giảng viên chưa được gửi).
5. Bộ docs A/B/C + tài liệu chuyên ngành và evidence.

## Điều kiện ra khỏi phạm vi
Mọi bổ sung ML, Chain, hủy chuyến, phần mềm API phải có ADR mới, đánh giá công sức và cập nhật KPI/test trước khi coding.
