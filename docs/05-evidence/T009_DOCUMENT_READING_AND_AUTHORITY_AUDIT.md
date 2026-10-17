# T-009 DOCUMENT READING AND AUTHORITY AUDIT

**Task ID:** `T-009`  
**Gate:** `G4`  
**Auditor:** Senior Big Data Software Architect & Governance Engineer  
**Audit Timestamp:** 2026-10-17T08:00:00+07:00  
**Normalized Placement:** `docs/05-evidence/T009_DOCUMENT_READING_AND_AUTHORITY_AUDIT.md` (Flat Canonical Layout per Project Lead T009-UNBLOCK-R1 Directive)  
**Status:** `AUDIT_COMPLETE / PRECONDITIONS_CHECKED`  

---

## 1. Mục Đích & Nguyên Tắc Đọc Tài Liệu Bắt Buộc

Căn cứ theo yêu cầu nghiêm ngặt của chỉ thị triển khai Task `T-009` (Gate G4), toàn bộ 27 tài liệu chuẩn tắc thuộc Live Repository và Báo cáo tiền khả thi đã được mở trực tiếp, đọc toàn văn và tính mã băm mật mã học SHA-256.

### Quy tắc kiểm tra:
1. `READ_COMPLETE` chỉ được ghi nhận khi đã thực sự mở đọc nội dung chi tiết trong Live Repository.
2. Không khai báo bất kỳ tệp nào không tồn tại.
3. Phân định rõ thứ bậc thẩm quyền pháp lý/kỹ thuật của từng nhóm tài liệu.
4. Xác định các điểm xung đột tiềm tàng và áp dụng đúng quy tắc giải quyết xung đột đã được phê duyệt.

---

## 2. Bảng Kiểm Tra & Đối Chiếu Thẩm Quyền Toàn Diện (27 Tài Liệu)

| File | Exists | Read status | SHA-256 | Relevant sections | Authority |
|---|:---:|:---:|:---:|---|:---:|
| `AGENTS.md` | YES | `READ_COMPLETE` | `4b97c977133acff8e3ad2ecba3c062de00cefda79316b7c6eaa0b33d5c0165d1` | Scope đồ án docs-v1.1; quy trình bắt buộc trước mọi task; những điều cấm (cấm sửa raw CSV, cấm SQL/Spark overwrite, cấm fake PASS, cấm tự đổi KPI); thứ tự G4 T-009 trước T-007/008; DoD. | **Chính sách Tối cao cho AI Agent** |
| `README.md` | YES | `READ_COMPLETE` | `3c5032ea72b4f3221cf30b703a846265b514d3e6cec8d2e3c4a973acddf32837` | Trọng tâm phân tích mô tả 2016–2024; 54.674.003 hàng audit; không có CANCELLED/DIVERTED; chưa có mã nguồn pipeline trong docs package; quy ước trạng thái; nguyên tắc tái lập. | **Điểm Khởi Đầu Hồ Sơ Đồ Án** |
| `START_HERE.md` | YES | `READ_COMPLETE` | `7b46e77572cdd89ed6717cfd9d8c9139eb2fec5647af7ecbda1fd035c561cda0` | Phân loại 18 file ABC + 8 tài liệu điều phối + 13 báo cáo source; trình tự đọc 1–5; hướng dẫn phân công AI từng bước (không giao cả ETL một lần). | **Tài Liệu Định Hướng Ban Đầu** |
| `docs/04-execution/PROJECT_STATE.md` | YES | `READ_COMPLETE` | `77a9d87248715cfa9b768dfe5909ef7c6d0743edf6b91b613555144cc2a80708` | Snapshot Gate G0–G7; G2=PASS (2026-10-16); G3=PASS & T-006=PASS/COMPLETED (2026-10-17); T-009_ENTRY_GATE=READY; G4 T-009/007/008=NOT_STARTED; Fact baseline 54.674.003 hàng $\times$ 34 cột; nghĩa vụ bảo lưu G2-EXC-001, OR-05, OR-08, FP-DEC-017, G3-COND-A/B/C. | **Sổ Quản Trị Trạng Thái Sống (`governed_living_docs`)** |
| `docs/04-execution/AI_HANDOFF.md` | YES | `READ_COMPLETE` | `c1d7ae6469570f3da4f36df7a92ada07f594159753781b3e8b05ceb5bd6a06bb` | Bất biến bàn giao AI; phân biệt audit lịch sử vs hiện thực; cấm ML/Aeolus; cấm suy diễn nhân quả thời tiết; thẩm quyền duy nhất của DATA_DICTIONARY 34 cột. | **Bàn Giao Bối Cảnh AI (`governed_living_docs`)** |
| `docs/04-execution/TASK_TEMPLATE.md` | YES | `READ_COMPLETE` | `a0d0ae0059350a653ec17ce5b32400983f18f63687d1ffd43017b2abbb5faf91` | Mẫu khung nhiệm vụ chuẩn; bắt buộc tạo file vật lý trong `docs/05-evidence/`; cấm chat-only pass; tệp cấm sửa (data/raw/, inputs/, PACKAGE_MANIFEST); bảng lệnh kiểm thử thực thi. | **Quy Chuẩn Nhiệm Vụ (`governed_living_docs`)** |
| `docs/01-planning/PRD.md` | YES | `READ_COMPLETE` | `f0290800a354a94e1adb6424e9942caa83ec215bde03a795bfe91ece2ab10414` | Câu hỏi nghiên cứu RQ-01..05 (& conditional RQ-06); phạm vi IN (9 CSV, PySpark, Parquet, thống kê mô tả); phạm vi OUT (ML, prediction, causal weather, cancelled/diverted); yêu cầu REQ-01..08. | **Đặc Tả Yêu Cầu Sản Phẩm** |
| `docs/01-planning/ROADMAP.md` | YES | `READ_COMPLETE` | `d46dbb64d73340a22830db66ba617ae256e000c44db294375fc30e6cbd6e9c72` | Lộ trình Gate G0..G7; phụ thuộc DAG; thứ tự bắt buộc Gate G4: T-009 setup trước T-007 ingestion và T-008 quality; điều kiện ra khỏi gate. | **Lộ Trình Cột Mốc Đồ Án** |
| `docs/01-planning/BACKLOG.md` | YES | `READ_COMPLETE` | `68770e5d88fd5cb7d70dcb3afb6a0eda66772f8f045976c29b9caffe2076ef43` | Định nghĩa Done cho T-009: khởi tạo project Python/Spark, test runner, lint, CI skeleton, run manifest; phụ thuộc T-006; ma trận chuyển giao downstream obligations G2->G3..G7. | **Backlog Nhiệm Vụ Chuẩn Tắc (`governed_living_docs`)** |
| `docs/02-design/ARCHITECTURE.md` | YES | `READ_COMPLETE` | `14cf55d04468149886bec7d6102228240f98bdb07305b7282073bd71608fa6a6` | Sơ đồ 6 tầng; ngân sách tài nguyên đo lường thực tế (16GB RAM, D: 64GB free); stack: PySpark 4.0.1, Java 21 LTS, Python 3.10; layout Parquet phân vùng theo YEAR; hạch toán dòng DC-11; lineage TS-020; thứ tự ưu tiên chuẩn tắc. | **Kiến Trúc Hệ Thống Chuẩn Tắc (`governed_living_docs`)** |
| `docs/02-design/DECISIONS.md` | YES | `READ_COMPLETE` | `bede7f51e95a832bd24dd6ceb51e4eb72a0fb6d9d3efc5a97fc4bc7642d0e66d` | Toàn bộ quyết định đã duyệt FP-DEC-001..017: FP-DEC-004 raw immutable, FP-DEC-005 PySpark+Parquet, FP-DEC-007 temporal safety, FP-DEC-008 threshold >=15, FP-DEC-010 denominator count_records, FP-DEC-011 DC-11/12, FP-DEC-012 8 CORE KPIs, FP-DEC-015 percentile_approx accuracy 10000, FP-DEC-016 min-N 1000/365/100, FP-DEC-017 Weather CONDITIONAL_NO_GO. | **Sổ Bộ Quyết Định Kiến Trúc (`governed_living_docs`)** |
| `docs/02-design/DATA_CONTRACT.md` | YES | `READ_COMPLETE` | `2f831cbd71f177f9cf18ec101be781f2a5a372ea2b3395aef6fe9bde1a04d6f4` | Hợp đồng dữ liệu DC-01..12: DC-01 raw immutable, DC-02 explicit schema, DC-03 provisional units, DC-06 count_records, DC-07 weather retained in raw, DC-11 disjoint accounting (raw = accepted + quarantined + rejected), DC-12 metric invalidity. | **Hợp Đồng Dữ Liệu Tối Cao** |
| `docs/02-design/DATA_DICTIONARY.md` | YES | `READ_COMPLETE` | `c4e729f40db803719f7f66fef92225a703db6a15a5de4a3d4cece095fb5f9642` | Thẩm quyền duy nhất cho 34 cột CSV thô: tên cột, thứ tự vật lý, kiểu dữ liệu logic; loại bỏ hoàn toàn 9 cột giả định; MONTH/DAY_OF_MONTH/DAY_OF_WEEK nullable; 6 cột weather O_TEMP..D_WSPD. | **Từ Điển Dữ Liệu Tối Cao** |
| `docs/02-design/KPI_SPEC.md` | YES | `READ_COMPLETE` | `bf4a663485c6416a790e1ca1d721f1da808fa9da61dc1e377b52b4ef04121d9c` | Đặc tả toán học 8 CORE KPIs (KPI-01..08); KPI-02/04 late rate >=15.0; KPI-03/05 signed mean delay (giữ số âm); KPI-06 P50/P90 accuracy 10000; KPI-07 taxi mẫu số độc lập; KPI-08 duration decomposition; min-N 1000/365/100. | **Đặc Tả Chỉ Số CORE KPI (`governed_living_docs`)** |
| `docs/02-design/ANALYSIS_PROTOCOL.md` | YES | `READ_COMPLETE` | `873fb4bf568b3adf5b96bbe0612b5f918e9caa072be4d819c6b8b1742c3b6925` | Giao thức phân tích mô tả hồi cứu; cấm kết luận nhân quả từ quan sát; nguyên tắc so sánh hãng/sân bay có N; xử lý dị biệt năm 2020 và khuyết Tháng 3/2024. | **Giao Thức Nghiên Cứu & Phân Tích** |
| `docs/03-quality/TEST_PLAN.md` | YES | `READ_COMPLETE` | `bc77f3d9d82b75af5ad2407b1523a7e010e1429bdba984bf22c7a869a2f9efde` | Ma trận 20 bài kiểm thử TS-001..TS-020; phân định giai đoạn thực thi (G4 synthetic tests: TS-001, TS-002, TS-003, TS-017, TS-019, TS-020); fixtures tối thiểu; PASS/FAIL rules. | **Kế Hoạch Kiểm Thử Chuẩn Tắc** |
| `docs/03-quality/RISK_REGISTER.md` | YES | `READ_COMPLETE` | `55c5a46d682cfd5b0ec45d9d3f4d65c9adf4f513ad12a8dc0eae88af01fd2d85` | Ánh xạ chuẩn tắc OR-01..OR-08 sang R-01..R-17; OR-01 FLIGHTS==1; OR-02 cặp YX 3624; OR-03 đơn vị 7 trường đo provisional; OR-05 năm 2024 thiếu Tháng 3 (OPEN_QUALITY_DEFECT); OR-08 danh tính thô IDENTITY_UNVERIFIED. | **Sổ Bộ Quản Trị Rủi Ro (`governed_living_docs`)** |
| `docs/03-quality/ROLLBACK_PLAN.md` | YES | `READ_COMPLETE` | `a27227da7b8db7ff619b962dd80acf03009410b58052e7f9eaf0fd8f1f4860b2` | Quy trình phục hồi khả nghịch; cấm sửa raw data; lưu git status/commit/branch; không overwrite bản đã publish; rollback pointer file an toàn. | **Kế Hoạch Hoàn Nguyên & Phục Hồi** |
| `docs/03-quality/SECURITY.md` | YES | `READ_COMPLETE` | `24d4696701ec3c03774fbee9313fc1959a5e22ac4311e81cf7b8e4af008b91c8` | An ninh dữ liệu và bí mật; cấm đưa credentials/tokens vào Git; bảo vệ raw CSV chỉ đọc; cấm tự ý chạy `torch.load` trên tệp `.pt` ngoài luồng. | **Chính Sách An Toàn & Bảo Mật** |
| `docs/03-quality/CHANGELOG.md` | YES | `READ_COMPLETE` | `4a10f400651bf335cfc322aae1cf38565bb495c13dcba40b43a4f74b04c10f31` | Nhật ký thay đổi hồ sơ qua các phiên bản docs-v1.0 -> v1.1; ghi nhận G2 PASS (2026-10-16); ghi nhận G3 PASS & T-006 PASS (2026-10-17). | **Nhật Ký Quản Trị Thay Đổi (`governed_living_docs`)** |
| `docs/05-evidence/G2_OFFICIAL_SIGNOFF_HUMAN_ACCEPTANCE_RECORD.md` | YES | `READ_COMPLETE` | `42c6131345069eac540337b6ca9cc0359219a051a8199f35fc29e158d58b95fc` | Biên bản nghiệm thu chính thức Gate G2 của Project Lead; bảo lưu G2-EXC-001 (7 trường số provisional, TS-018 G5 hard stop), OR-05 (2024 thiếu Tháng 3), OR-08 (IDENTITY_UNVERIFIED), FP-DEC-017 (Weather CONDITIONAL_NO_GO). | **Biên Bản Nghiệm Thu Chính Thức Gate G2** |
| `docs/05-evidence/G3_OFFICIAL_SIGNOFF_HUMAN_ACCEPTANCE_RECORD.md` | YES | `READ_COMPLETE` | `f83825f1b12ce84fe6e01bbf760a87598d2ffbaa1c9b6ae83a9aeedaa955ba8c` | Biên bản nghiệm thu chính thức Gate G3 & T-006 của Project Lead; xác lập 3 điều kiện chuyển giao bắt buộc G3-COND-A (quarantine provisional), G3-COND-B (runtime is_finite_numeric test), G3-COND-C (Windows NTFS 7-step publication); T-009_ENTRY_GATE = READY; T-009/T-007/T-008 = NOT_STARTED. | **Biên Bản Nghiệm Thu Chính Thức Gate G3** |
| `docs/05-evidence/T006_R1_CANONICAL_SCHEMA_RECONCILIATION.md` | YES | `READ_COMPLETE` | `3cd842e2e240e6ce01a6e6a13ade5bfc7e43852775911e0f3d280fb138a0aa87` | Bảng đối soát chuẩn tắc 34 cột raw; loại bỏ 9 cột tự chế; kiểu dữ liệu tương thích schema_YYYY.json; trường lịch nullable; regex kiểm tra ngày có neo. | **Báo Cáo Đối Soát Schema Chuẩn Tắc** |
| `docs/05-evidence/T006_R1_KPI_AND_TEST_RECONCILIATION.md` | YES | `READ_COMPLETE` | `25eded92a5bfad3fc691d62adeca4da3871d3236be906bf0ad470c583faa9e1d` | Đối soát toán học 8 CORE KPIs; loại bỏ bộ lọc cancel/divert; percentile_approx accuracy 10000; min-N 1000/365/100; ma trận kiểm thử TS-001..TS-020. | **Báo Cáo Đối Soát KPI & Kiểm Thử** |
| `docs/05-evidence/T006_R1_ARCHITECTURE_RISK_CORRECTIONS.md` | YES | `READ_COMPLETE` | `524d49229d1c5a620b585ca2ceac672a2cbc2ff685bbef5ba1346307401e5c33` | Hiệu chỉnh rủi ro kiến trúc: ngân sách RAM 6–8GB là ESTIMATED, partitioning Parquet theo YEAR, định danh dòng ổn định TS-020, an toàn xuất bản NTFS. | **Báo Cáo Hiệu Chỉnh Rủi Ro Kiến Trúc** |
| `docs/05-evidence/T006_FINAL_CORRECTIONS_ADDENDUM.md` | YES | `READ_COMPLETE` | `9966159e5d8aecc2f3bc786faacd22c72d02568e37b4b80e40c5faaa14c87304` | Phụ lục an toàn triển khai tối cao: chuẩn hóa DC-11/12 (metric invalidity không cách ly chuyến bay); vị từ số thực hữu hạn đầy đủ is_finite_numeric; quy trình xuất bản an toàn 7 bước; hủy bỏ lệnh rollback xóa file Remove-Item; regex ngày neo chặt. | **Phụ Lục An Toàn Triển Khai Chuẩn Tắc G3** |
| `../T009_PREFLIGHT_AUDIT_REPORT.md` | YES | `READ_COMPLETE` | `6d217b563a613581fe643aadbee57927ccada0f0254816e75ea529aca75cd2ac` | Báo cáo tiền khả thi độc lập: xác minh Python 3.10.11, Java 21 LTS, PySpark 4.0.1; phát hiện biến môi trường PYSPARK_PYTHON trỏ sai; kiểm chứng thực nghiệm thành công G3-COND-B & G3-COND-C trên synthetic; xác định ổ D trống 64.3GB; cảnh báo thiếu Git baseline. | **Báo Cáo Kiểm Toán Tiền Khả Thi Độc Lập** |

---

## 3. Thứ Tự Ưu Tiên Thẩm Quyền Chuẩn Tắc (Precedence & Conflict Resolution)

Căn cứ Mục 8 của `docs/02-design/ARCHITECTURE.md` và `docs/05-evidence/G3_OFFICIAL_SIGNOFF_HUMAN_ACCEPTANCE_RECORD.md`:

$$\mathbf{DATA\_DICTIONARY.md} \equiv \mathbf{KPI\_SPEC.md} \equiv \mathbf{DATA\_CONTRACT.md}$$
$$> \mathbf{T006\_FINAL\_CORRECTIONS\_ADDENDUM.md} > \mathbf{T006\_R1\_*} > \mathbf{ARCHITECTURE.md} > \mathbf{T006\_(Initial)}$$

### Các điểm mâu thuẫn đã được nhận diện & xử lý triệt để:
1. **Xung đột danh mục cột raw:**
   - Các tài liệu sơ khai từng chứa các cột giả định (`CANCELLED`, `DIVERTED`, `DISTANCE`, 5 cột `*_DELAY` của BTS, `weather_code`).
   - **Xử lý:** Ưu tiên tuyệt đối `DATA_DICTIONARY.md` và `T006_R1_CANONICAL_SCHEMA_RECONCILIATION.md` — chính xác 34 cột vật lý, gồm 6 cột thời tiết `O_TEMP, O_PRCP, O_WSPD, D_TEMP, D_PRCP, D_WSPD`.
2. **Xung đột hạch toán dòng (Record vs Metric Validity):**
   - Tài liệu thiết kế cũ từng đề xuất cách ly toàn bộ dòng khi `AIR_TIME <= 0` hoặc taxi âm.
   - **Xử lý:** Ưu tiên `T006_FINAL_CORRECTIONS_ADDENDUM.md` và `DATA_CONTRACT.md` (DC-11/12) — vi phạm số đo chỉ loại khỏi mẫu số hợp lệ $N_{valid}$ của chính số đo đó, bản ghi vẫn là `ACCEPTED` đóng góp vào `KPI-01` (`count_records`).
3. **Xung đột hướng dẫn hoàn nguyên:**
   - `T006_R1_EXECUTION_MANIFEST.md` chứa lệnh xóa `Remove-Item` trên file Markdown và thư mục backup.
   - **Xử lý:** Đã bị hủy bỏ hoàn toàn bởi Mục 5 của `T006_FINAL_CORRECTIONS_ADDENDUM.md`. Cấm tuyệt đối xóa bằng chứng lịch sử.
4. **Xung đột đường dẫn giao phẩm bằng chứng:**
   - Prompt T-009 ban đầu từng đề xuất gốc bằng chứng tại `docs/05-evidence/T009/`.
   - Script kiểm tra tính nhất quán hiện hành `tools/check_working_tree_consistency.py` (Mục 13, dòng 495) chỉ cho phép file trực tiếp dưới `docs/05-evidence/` khớp biểu thức `EVIDENCE_FILENAME_RE` (ví dụ `T009_*.md`), không cho phép thư mục con ngoài các thư mục `*_BACKUPS`.
   - **Xử lý:** Theo chỉ thị `T009-UNBLOCK-R1` của Project Lead, toàn bộ bằng chứng T-009 được chuẩn hóa về quy ước phẳng trực tiếp dưới `docs/05-evidence/T009_*.md`.

---

## 4. Kết Luận Kiểm Toán Đọc Tài Liệu

- **Tổng số tài liệu bắt buộc:** 27 / 27 tài liệu tồn tại thực tế và đã được đọc hiểu đầy đủ.
- **Không có tài liệu giả mạo hoặc hư cấu.**
- **Toàn bộ các điều kiện tiên quyết và bất biến nghiệp vụ đã được nắm vững.**
- **Báo cáo này được lập hợp lệ trước khi thực hiện bất kỳ thao tác mã nguồn nào.**
