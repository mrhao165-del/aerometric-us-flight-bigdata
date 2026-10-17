# DEPLOYMENT — Quy trình tái lập/triển khai (chưa chạy)

**Status: NOT_READY / DOCUMENTATION ONLY.** Chưa có source code pipeline/môi trường runtime trong gói tài liệu; không cung cấp lệnh chạy giả.

## Điều kiện trước khi chạy
- Chọn môi trường (Antigravity local/Google Colab/cluster Spark), Python/Java/Spark versions có hỗ trợ lẫn nhau; ghi thực tế vào environment manifest.
- Đặt raw theo cấu trúc `data/raw/tabular/{year}/flight_with_weather_{year}.csv`, kiểm tra dung lượng/metadata drift; chỉ ghi CONTENT_VERIFIED nếu thực sự đối chiếu SHA-256 raw đáng tin cậy, không gán confidence từ mtime.
- Xác nhận tài nguyên RAM/CPU/disk và quota; output không nằm trên raw folder.
- Cài dependencies bằng lockfile đã được kiểm tra; không dùng secret chung repo.
- Có test runner, kịch bản dry-run/smoke, versioned outputs và rollback. Theo thứ tự G3 design review → G4 T-009 bootstrap/T-007 ingest/T-008 quality → G5 smoke, **không** skip G2 CORE units/KPI approval.

## Quy trình tương lai
`environment verification` → `source validation` → `bounded smoke` → `quality reconciliation` → `full year batch` → `all-year summary` → `KPI tests` → `charts/report publish`. Mỗi bước phát hành manifest. Không có kết quả PASS khi chưa có logs.

## Phát hành
Chỉ công bố bảng và biểu đồ từ curated run đã nghiệm thu. Đính kèm output snapshot/run-id, contract version, kiểm thử, ngày thực thi. Nếu phải chạy trên Colab: lưu output vào Drive theo folder versioned, kiểm soát giới hạn phiên chạy và tránh giả định có dung lượng/bộ nhớ cố định.

## Khôi phục
Tham chiếu `docs/03-quality/ROLLBACK_PLAN.md`. Dashboard/server (nếu có) thuộc scope phụ và cần quyết định triển khai riêng.
