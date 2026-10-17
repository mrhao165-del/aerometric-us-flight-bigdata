# ROLLBACK_PLAN — Kế hoạch phục hồi

**Status: thiết kế, chưa chứng minh trên repository thật.** Không bao giờ phục hồi bằng cách chỉnh raw.

## Trước khi thực thi task
- Lưu `git status`, current branch, commit hash; làm việc trên branch riêng.
- Ghi `run_id`, input signatures, output paths, code commit, config version.
- Lưu kết quả đã nghiệm thu trong folder versioned, không `overwrite` bản đã publish.
- Có bản sao/backup được kiểm chứng nếu có thay đổi phá hủy; không coi Git là backup của data lớn.

## Rollback mã nguồn
1. Dừng job đang chạy, ghi run-id và log.
2. Bảo toàn diff chưa commit; không `git reset --hard` khi chưa bảo vệ công việc.
3. Tạo branch khôi phục hoặc revert commit lỗi (`git revert <sha>` sau khi kiểm tra quan hệ commit).
4. Chạy unit/integration/reconciliation test; chỉ merge revert nếu PASS.

## Rollback processed/curated
1. Đánh dấu manifest của run lỗi `INVALID`/`QUARANTINED`, không xóa trước.
2. Chuyển con trỏ bản đang phục vụ sang bản run đã nghiệm thu gần nhất (atomic nếu môi trường hỗ trợ).
3. Kiểm tra schema, số hàng, KPI checksum, plots và report có cùng version.
4. Nếu không có artifact tốt trước đó, dừng publish, chạy lại từ immutable raw theo run-id mới.

## Các tình huống không được 'tự sửa'
- Chênh lệch số bản ghi, timezone/overnight, thiếu provenance thời tiết, định nghĩa KPI thay đổi: dừng sử dụng output và mở issue/ADR; không tự thêm/bớt giờ hay drop hàng.

## Diễn tập tối thiểu
G5 tạo một run cố ý lỗi ở output staging, xác nhận không được publish; phục hồi con trỏ run đã tốt; lưu **TS-013** logs.
