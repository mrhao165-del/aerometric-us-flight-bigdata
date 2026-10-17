# G0/G1 REVIEW — Đánh giá tài liệu được cung cấp

**Ngày review:** 2026-10-13. Scope người dùng yêu cầu: hiệu suất bay Hoa Kỳ 2016–2024. Đây là kiểm tra logic và tổng hợp *các tài liệu*; raw CSV 15GB không được tải vào phiên này.

## Evidence matrix
| Nguồn | Nội dung được chứng minh | Không chứng minh |
|---|---|---|
| `data_inventory.md` | 9 CSV Tabular + 27 `.pt`, paths, byte sizes, records audit update | Nội dung tensor, nguồn công bố gốc, representativeness |
| `canonical_schema_v1(1).md` | 34 field families và dtypes canonical | Đơn vị tất cả cột, semantic validity |
| 9 × `schema_YYYY.json` | 54,674,003 records, 34 columns, audit completeness, descriptive ARR_DELAY stats, missing per-column | Scheduled cancellations/diversions, flight grain, causal claims |
| `canonical_schedule_datetime_representation_audit.md` | 2016–2023 processed timestamp-like, service date equivalence FL_DATE, date clock issue | 2400 normalization, 2024 complete time audit |
| `leakage_audit.md` | Historical ATL T-2h prediction feature safety; raw weather provenance issue | Quy tắc cấm dùng operations trong phân tích mô tả |

## Kiểm tra nhất quán
- Năm 2016–2024 đủ, mỗi năm có cùng 34 cột; tổng records JSON bằng inventory.
- JSON có `ARR_DELAY` available/finite_count = row_count trên cả chín năm; compatible với nghiên cứu on observed records.
- Audit xử lý DATE chỉ full 2016–2023: không nâng kết luận sang 2024 mà chưa có check.
- Source `leakage_audit` nói `DEST=ATL` **trong core inbound partitions cũ**; không được suy thành toàn bộ CSV Tabular chỉ ATL. Cột `DEST` schema đầy đủ khác hẳn subset dự báo.
- `canonical_schema_v1` chứa V4 ML target wording; **không quyết định scope** đồ án mới.
- `Flight Chain`: inventory từ thời điểm trước mô tả OPTIONAL, audit thời gian ghi raw `.pt` đã `FINAL—NO_GO` trong nhánh lịch sử; scope mới loại hẳn nên không có xung đột vận hành.

## Vấn đề blocker
- **B01:** Định nghĩa dữ liệu nguồn/coverage thiếu; tác động RQ-01/03/04, cách gọi số chuyến và hãng hàng không.
- **B02:** `FLIGHTS` chưa rõ; tránh tính weighted total.
- **B03:** Không có flags cancelled/diverted; bỏ KPI tương ứng.
- **B04:** Date rollover/2400 không chứng minh; khóa derived arrival/depart timestamp differences.
- **B05:** Weather units/valid-time/merge logic thiếu; không dùng cho kết luận causal hoặc bins mang nhãn đơn vị.
- **B06:** Chưa có pipeline Spark và log chạy thực; không khẳng định các tài liệu này là sản phẩm code hoàn tất.
- **B07:** Chưa có rubric giảng viên và môi trường thực thi chốt.
- **B08 (docs-v1.1 addendum):** Nguồn chưa chứng minh units/sign/domain cho 7 measures CORE; T-003/TS-018 phải xử lý trước G2 PASS.
- **B09 (docs-v1.1 addendum):** JSON `source_signature` chỉ có size/mtime, không có raw content checksum; source identity vẫn chưa xác minh.

## Gate verdict
- **G0: DESIGN_BASELINE** — người dùng đã xác nhận analysis-first. Những quyết định kỹ thuật vẫn `PROPOSED`.
- **G1: PARTIAL** — đủ structural audit, thiếu evidence các blocker trên. Có thể khởi tạo docs và thiết kế core KPIs; chưa nghiệm thu dataset ready-to-publish.
- **G2+: NOT_EXECUTED** — đặc tả đã soạn, chưa thực nghiệm.

## Hành động cần ưu tiên
T-001 nguồn/selection/coverage, T-002 grain & `FLIGHTS`, T-003 khóa **8 CORE KPI và kiểm chứng units/sign/domain của 7 measures**, T-004 thời gian, T-005 weather conditional. G2 chưa PASS trước khi có bằng chứng thực tế. Nếu không có nguồn thứ cấp, khóa RQ-06 NO-GO và tập trung RQ-01–05.
