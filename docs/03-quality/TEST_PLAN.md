# TEST_PLAN — Kiểm thử và điều kiện nghiệm thu

**Version:** docs-v1.1; `SPECIFIED/NOT_RUN`. Test ID `TS-###` là duy nhất; viết fixture trên giấy **không** phải test PASS. Phải có bằng chứng lệnh thực thi, run/log/commit khi nghiệm thu code.

| Test | Requirements / Task | Nội dung | Giai đoạn thực thi | PASS condition |
|---|---|---|---|---|
| TS-001 | REQ-01, T-007 | Đủ 9 nguồn và 34 cột mỗi năm | G4 synthetic/G5 real/G6 full | Dữ liệu nguồn thực tế được kiểm tra, drift fail-closed |
| TS-002 | REQ-02, T-007/008 | Parse date/numeric, null, NaN, inf, domain & flags | G4/G5 | Lỗi không bị silent cast/drop; outcome có reason |
| TS-003 | REQ-02/04, T-008/010/012 | Ba trạng thái row accounting | G4 synthetic/G5/G6 | `raw=accepted+quarantined+rejected`, disjoint; corrupted input có count hoặc ACCOUNTING_UNVERIFIED chặn publish |
| TS-004 | REQ-01/02, T-012 | Year/FL_DATE/schema, kiểm riêng 2024 | G6 | Full 9 năm được reconcile, date extraction bằng chứng riêng |
| TS-005 | REQ-03/04, T-003/011 | `ARR_DELAY` threshold, eligibility và metadata denominator | G2 fixture design/G5 execution | Boundary 14.999/15/15.001, null, negative, N=0, rate null nếu denominator 0 |
| TS-006 | REQ-03, T-003/011 | Mean signed vs positive, units, submetric nulls | G2 design/G5 | Không clip signed; finite domain và mean đúng; unit_status rõ |
| TS-007 | REQ-03, T-013 | Year/month/carrier/origin/dest/route aggregate | G6 | 6 group dims đầy đủ; reconcile tổng **riêng** từng dimension, no double count khi cộng origin+dest |
| TS-008 | REQ-03, T-003/011/013 | P50/P90, extreme, min-N & per-submetric denominator | G2 design/G5 synthetic/G6 full | Quantile algorithm/tolerance/min-N đã duyệt; 2 taxi và 3 elapsed mẫu số độc lập; không ranking khi min-N chưa duyệt |
| TS-009 | REQ-04, T-002/011 | Guard FLIGHTS, cancel/divert, weather optional | G2 design/G5/G7 | Không xuất count không có grain/cancel rate; weather không được tự coi mandatory |
| TS-010 | REQ-02, T-004/012 | Timezone/overnight/2400 + 2024 boundary | G2 design/G5/G6 conditional | Không suy timestamp không có evidence; derived date metrics `NOT_AVAILABLE` nếu NO_GO |
| TS-011 | REQ-06, T-005/015 | Weather units, join, missing, stratification | Conditional G2/G6 | GO verified hoặc documented CONDITIONAL_NO_GO; không sinh chart nếu chưa GO |
| TS-012 | REQ-07, T-010/011 | Repeatability, keys, sample run determinism | G5 | Hai runs cùng input/contract cho output logic tương đương; không dựa source_row_number Spark không ổn định |
| TS-013 | REQ-07, T-011 | Fault injection, rollback pointer, invalid partial output | G5 | Không publish run lỗi; bằng chứng rollback |
| TS-014 | REQ-07, T-006/010/012 | Resource/benchmark | G5/G6 | CPU/RAM/disk/time logs đo thật, không ước lượng PASS |
| TS-015 | REQ-05, T-014/017 | Figure/result provenance | G6/G7 | Mỗi RQ-01..05 có ít nhất RES-ID kết quả validated, query/run/KPI, chart hoặc bảng và caveats |
| TS-016 | REQ-03/04/05, T-013/014 | Panel coverage, 2020, stable cohort, ranking guards | G6/G7 | Thống kê N, coverage, sensitivity và chặn ranking chưa chứng thực |
| TS-017 | REQ-02/04, T-002/003/008 | Accounting/coverage glossary + zero denominators | G4 synthetic/G5 | count_records=accepted group; eligible+excluded=accepted; valid_rate N/A nếu N=0; ingest rate khác metric rate; source_coverage_status không phải market % |
| TS-018 | REQ-03/05, T-003 | Verify seven CORE measure units/sign/domain từ source | G2 document gate | Citation/source/protocol cho cả 7 trường hoặc G2 BLOCKED; không gán phút theo tên khi chưa kiểm chứng |
| TS-019 | REQ-07, T-001/007 | Raw identity và metadata drift | G4 synthetic/G5 | size/mtime không coi là content identity; mismatch → IDENTITY_UNVERIFIED; raw hash verified nếu có |
| TS-020 | REQ-02/07, T-007/012 | Stable lineage / row identifier | G4/G6 | Traceability reproducible trên repeated distributed reads hoặc lineage surrogate được duyệt, không đoán Spark offsets |

## Synthetic fixtures tối thiểu
- `ARR_DELAY = [-5,0,14.999,15,31,null]`; thử group no records và group all-null, `metric_valid_rate=null` khi denominator 0.
- Input có 5 records: 3 accepted, 1 quarantined (parseable nhưng core-rule invalid), 1 rejected (malformed, counted); với accepted, 1 null metric => `metric_valid_rate=2/3`, `ingest_acceptance_rate=3/5`; không tự cộng rejected vào KPI cohort.
- KPI-07/08 với null khác nhau ở mỗi submetric; min-N ranking phải có suppression/caution.
- Hai hàng identical nhưng chưa rõ event identity: không xóa theo hash; năm khác code/map khác.
- `FL_DATE='2016-06-01 00:00:00'`, `CRS_DEP_TIME='2016-06-01 22:25:00'`, `CRS_ARR_TIME='2016-06-01 00:00:00'`; không đoán next-day.
- 2024 timestamp có kiểm toán riêng; Weather missing/unknown units; invalid `FLIGHTS` không ảnh hưởng KPI-01 record count.
- Metadata source path/size giống, mtime khác; hoặc mtime giống nhưng content hash khác: state `IDENTITY_UNVERIFIED` chứ không PASS.

## Gate-to-test mapping
- **G2:** TS-005/006/008 (spec review), TS-009/010/011 (conditional policies), **TS-018 + definitions TS-017** review; phải có evidence T-001..003, không coi test fixture đã chạy.
- **G3:** test plan và fixtures đã review, không đòi TS-001 code PASS.
- **G4:** TS-001/002/003/017/019/020 synthetic phù hợp, CI runner PASS.
- **G5:** TS-001/002/003/005/006/**008**/009/012/013/014/017/019 PASS cho phạm vi smoke; TS-008 ở G5 là synthetic/limited KPI-06..08 validation, KHÔNG đồng nghĩa đã có đầy đủ kết quả nhóm 9 năm; TS-010 chỉ nếu derived time GO.
- **G6:** TS-003/004/007/008/014/016/020 PASS full run; TS-011 chỉ nếu Weather GO; TS-010 nếu derived time GO.
- **G7:** TS-015/016 + result/traceability/reproducibility review PASS.

## Lưu bằng chứng
`artifacts/runs/<run_id>/{manifest.json,test_results.json,row_accounting.csv,quality_summary.csv}`, commands, exit codes, code commit, Spark version; chỉ output thực mới có `PASS`. Gate CORE không bị chặn bởi Weather có `CONDITIONAL_NO_GO` được duyệt.
