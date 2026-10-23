# T011_FULL_DOC_READING_ATTESTATION — BIÊN BẢN KIỂM TOÁN VÀ ĐỐI SOÁT ĐỌC TOÀN BỘ TÀI LIỆU QUY CHUẨN

- **Mã nhiệm vụ:** `T-011` (Gate G5: KPI Sample Smoke, BTS Parity, TS-008, TS-013 & Review Packaging)
- **Gate:** `G5` (IN_PROGRESS)
- **Thời điểm kiểm toán:** 2026-10-18T20:41:00+07:00
- **Tiêu chuẩn tuân thủ:** [`AGENTS.md`](../../AGENTS.md), Master Execution Prompt T-011 Mục 2.
- **Trạng thái Gate 0A:** **PASS (100% Mandatory Documents Completely Read & Crosswalked)**

---

## 1. TỔNG QUAN DANH MỤC TÀI LIỆU KIỂM TOÁN BẮT BUỘC

Kiểm toán độc lập đã đọc đầy đủ từng ký tự (100% complete content reading, không đọc lướt, không bỏ sót phân đoạn bị cắt xén) toàn bộ **50 tài liệu quy chuẩn**:
- **3 tài liệu gốc (Root Documents):** `AGENTS.md`, `README.md`, `START_HERE.md`.
- **24 tài liệu quy hoạch, thiết kế, chất lượng và thực thi:** thuộc `docs/00-governance/`, `docs/01-planning/`, `docs/02-design/`, `docs/03-quality/`, `docs/04-execution/`.
- **23 tài liệu bằng chứng, biên bản nghiệm thu và errata:** thuộc `docs/05-evidence/`.

---

## 2. BẢNG CHI TIẾT TỪNG TÀI LIỆU, CHỮ KÝ SHA-256 VÀ TRÍCH XUẤT QUY CHUẨN

| STT | Đường dẫn tương đối | Kích thước (Bytes) | Chữ ký SHA-256 | Trạng thái đọc | Các yêu cầu, quyết định & ràng buộc cốt lõi áp dụng cho T-011 |
|:---:|---|---:|---|:---:|---|
| 1 | `AGENTS.md` | 4,178 | `4b97c977133acff8e3ad2ecba3c062de00cefda79316b7c6eaa0b33d5c0165d1` | 100% READ | Quy định tối cao: Cấm sửa raw CSV; cấm giả mạo đọc 54.7M dòng; cấm tự gán đơn vị; tuân thủ DC-11/12; G2-EXC-001/TS-018 là hard stop; Weather CONDITIONAL_NO_GO; không dùng lệnh xóa phá hủy. |
| 2 | `README.md` | 3,946 | `3c5032ea72b4f3221cf30b703a846265b514d3e6cec8d2e3c4a973acddf32837` | 100% READ | Tổng quan dự án phân tích hiệu suất bay Hoa Kỳ 2016–2024; phân tích mô tả dữ liệu lớn bằng PySpark; kiến trúc 3 vùng raw/staging/curated. |
| 3 | `START_HERE.md` | 2,396 | `7b46e77572cdd89ed6717cfd9d8c9139eb2fec5647af7ecbda1fd035c561cda0` | 100% READ | Hướng dẫn onboarding, luồng kiểm tra tính nhất quán working tree và quy trình làm việc có kiểm soát. |
| 4 | `docs/00-governance/BUILD_QA_REPORT.md` | 2,063 | `583229e19bd7346ef2857013691d25bae8090882a24c7f1fb69641f7bb32e3f4` | 100% READ | Quy chuẩn báo cáo QA; xác minh toàn vẹn cấu trúc và tài liệu tham chiếu. |
| 5 | `docs/00-governance/DOCS_CONSISTENCY_AUDIT_v1.1.md` | 4,179 | `878184396cb1160a419de1fe251334b8e800aa2796a1e7455b7a37c5986d40ca` | 100% READ | Kiểm toán tính nhất quán v1.1: Đồng bộ hóa thuật ngữ DC-11/12, các mã rủi ro OR-01..08 và quyết định FP-DEC-001..017. |
| 6 | `docs/00-governance/DOCUMENT_REGISTER.md` | 5,376 | `996754a0cd3b19fd50a386b41ec0b2854180b9c24468bb9e4900f4e1af271f28` | 100% READ | Sổ đăng ký tài liệu tài phán; phân loại tài liệu living, authoritative, immutable và contract. |
| 7 | `docs/00-governance/V1_0_CONSISTENCY_AUDIT.md` | 16,126 | `6fe4b6fcfc56a6dbcb79b66764c19c4ef9cb05a6b4ab89d9607547d381ee1f36` | 100% READ | Hồ sơ lịch sử kiểm toán nhất quán phiên bản v1.0, ghi nhận các sai lệch đã được khắc phục ở v1.1. |
| 8 | `docs/01-planning/BACKLOG.md` | 12,660 | `e2020622d3735f2679d45d755e0ebd4f43e1ec23c88fba26fb55c7cdd94c4447` | 100% READ | Định vị T-011 tại Gate G5: Workstream A (KPI), B (TS-008), C (TS-018 blocker), D (TS-013), E (Contractual regression). |
| 9 | `docs/01-planning/PRD.md` | 5,249 | `f0290800a354a94e1adb6424e9942caa83ec215bde03a795bfe91ece2ab10414` | 100% READ | Yêu cầu sản phẩm: 5 câu hỏi nghiên cứu RQ-01..05 phục vụ 8 CORE KPIs; loại trừ RQ-06 (thời tiết). |
| 10 | `docs/01-planning/ROADMAP.md` | 3,865 | `d46dbb64d73340a22830db66ba617ae256e000c44db294375fc30e6cbd6e9c72` | 100% READ | Lộ trình các Gate G0..G7; Gate G5 là smoke & benchmark; Gate G6 là full 9-year ETL; TS-018 là điều kiện tiên quyết mở G6. |
| 11 | `docs/02-design/ANALYSIS_PROTOCOL.md` | 3,452 | `873fb4bf568b3adf5b96bbe0612b5f918e9caa072be4d819c6b8b1742c3b6925` | 100% READ | Giao thức phân tích mô tả: Cấm suy diễn nhân quả; phân biệt quan sát với quy luật; không nội suy dữ liệu khuyết. |
| 12 | `docs/02-design/API_CONTRACTS.md` | 769 | `ba9ae2838372add9208737572a7986774c3f96e5c0c3d6253c1d5b0f7fdaaf8b` | 100% READ | Giao diện API nội bộ cho các pipeline modules; quy định interface đầu vào/đầu ra chuẩn. |
| 13 | `docs/02-design/ARCHITECTURE.md` | 21,056 | `14cf55d04468149886bec7d6102228240f98bdb07305b7282073bd71608fa6a6` | 100% READ | Kiến trúc tổng thể: Pipeline Spark, 2-phase SafePublisher, locking, lineage surrogate, schema 34 cột. |
| 14 | `docs/02-design/DATA_CONTRACT.md` | 7,238 | `2f831cbd71f177f9cf18ec101be781f2a5a372ea2b3395aef6fe9bde1a04d6f4` | 100% READ | Hợp đồng dữ liệu chuẩn: DC-01..DC-12. DC-11 (raw = accepted + quarantined + rejected), DC-12 (record vs metric validity). |
| 15 | `docs/02-design/DATA_DICTIONARY.md` | 6,081 | `c4e729f40db803719f7f66fef92225a703db6a15a5de4a3d4cece095fb5f9642` | 100% READ | Từ điển 34 cột raw: 10 String, 19 Double, 5 Long. 6 cột thời tiết O_TEMP..D_WSPD. Không có cột cancelled/diverted. |
| 16 | `docs/02-design/DECISIONS.md` | 21,647 | `bede7f51e95a832bd24dd6ceb51e4eb72a0fb6d9d3efc5a97fc4bc7642d0e66d` | 100% READ | Toàn bộ quyết định chuẩn tắc FP-DEC-001..017; FP-DEC-012 (G2-EXC-001), FP-DEC-015 (GK-sketch), FP-DEC-016 (min-N), FP-DEC-017 (Weather NO-GO). |
| 17 | `docs/02-design/KPI_SPEC.md` | 9,949 | `bf4a663485c6416a790e1ca1d721f1da808fa9da61dc1e377b52b4ef04121d9c` | 100% READ | Đặc tả chi tiết 8 CORE KPIs; công thức toán học; bảo toàn delay âm; ngưỡng 15.0; mẫu số độc lập; schema 17 trường chuẩn. |
| 18 | `docs/03-quality/CHANGELOG.md` | 17,417 | `5698f13a832458bfcf5a535108a48b3a7ec3c479d2c7e4ba77f4c57d0a25aebe` | 100% READ | Nhật ký thay đổi chuẩn tắc qua các mốc G0, G1, G2, G3, T-009, T-007, T-008, G4, T-010. |
| 19 | `docs/03-quality/G0_G1_REVIEW.md` | 3,926 | `ca325a846bc6890d25c0b03d7e521bdbde15faa7de6fe59b8c6e4972587bf731` | 100% READ | Đánh giá độc lập G0/G1; kiểm toán dữ liệu thô 54,674,003 dòng và 9 tệp CSV nguồn. |
| 20 | `docs/03-quality/RISK_REGISTER.md` | 11,376 | `55c5a46d682cfd5b0ec45d9d3f4d65c9adf4f513ad12a8dc0eae88af01fd2d85` | 100% READ | Danh mục rủi ro: OR-01..OR-08; OR-03 (đơn vị provisional -> R-15), OR-05 (thiếu tháng 3/2024 -> R-03), OR-08 (identity unverified -> R-16). |
| 21 | `docs/03-quality/ROLLBACK_PLAN.md` | 1,850 | `a27227da7b8db7ff619b962dd80acf03009410b58052e7f9eaf0fd8f1f4860b2` | 100% READ | Kế hoạch rollback an toàn: Phục hồi con trỏ, không xóa phá hủy, lưu giữ forensic logs khi gặp sự cố. |
| 22 | `docs/03-quality/SECURITY.md` | 1,748 | `24d4696701ec3c03774fbee9313fc1959a5e22ac4311e81cf7b8e4af008b91c8` | 100% READ | An toàn bảo mật: Cấm đưa secrets, token, tệp nhị phân lớn hoặc raw CSV vào git tracking. |
| 23 | `docs/03-quality/TEST_PLAN.md` | 6,346 | `bc77f3d9d82b75af5ad2407b1523a7e010e1429bdba984bf22c7a869a2f9efde` | 100% READ | Kế hoạch kiểm thử: Danh mục bài kiểm thử TS-001..TS-020; TS-008 (quantiles/min-N), TS-013 (fault injection), TS-018 (BTS parity). |
| 24 | `docs/04-execution/AI_HANDOFF.md` | 17,329 | `c1d7ae6469570f3da4f36df7a92ada07f594159753781b3e8b05ceb5bd6a06bb` | 100% READ | Giao thức bàn giao giữa AI Agents: Phân định vai trò, truyền tải ngữ cảnh và kiểm soát bằng chứng. |
| 25 | `docs/04-execution/DEPLOYMENT.md` | 1,923 | `21a408adc186637e21b45abafb721f933778260a69f25f5ca9465090a328209c` | 100% READ | Hướng dẫn triển khai môi trường Spark, cấu hình tài nguyên và các tham số thực thi. |
| 26 | `docs/04-execution/PROJECT_STATE.md` | 34,777 | `eaa820165ddb562fdcc7a7c5e62cd02ab7501e82b7a91f3bd3ecda9f794bc792` | 100% READ | Trạng thái dự án living: G2, G3, G4 = PASS; T-010 = PASS; G5 = IN_PROGRESS; T-011 = NOT_STARTED. |
| 27 | `docs/04-execution/TASK_TEMPLATE.md` | 8,445 | `a0d0ae0059350a653ec17ce5b32400983f18f63687d1ffd43017b2abbb5faf91` | 100% READ | Mẫu đặc tả nhiệm vụ chuẩn tắc của đồ án. |
| 28 | `docs/05-evidence/G2_OFFICIAL_SIGNOFF_HUMAN_ACCEPTANCE_RECORD.md` | 12,478 | `42c6131345069eac540337b6ca9cc0359219a051a8199f35fc29e158d58b95fc` | 100% READ | Biên bản ký duyệt Gate G2: Phê duyệt 8 CORE KPIs với ngoại lệ G2-EXC-001; TS-018 là điều kiện bắt buộc chặn G6. |
| 29 | `docs/05-evidence/G3_OFFICIAL_SIGNOFF_HUMAN_ACCEPTANCE_RECORD.md` | 14,451 | `f83825f1b12ce84fe6e01bbf760a87598d2ffbaa1c9b6ae83a9aeedaa955ba8c` | 100% READ | Biên bản ký duyệt Gate G3: Nghiệm thu thiết kế kiến trúc T-006; xác lập 3 điều kiện G3-COND-A/B/C. |
| 30 | `docs/05-evidence/G4_OFFICIAL_HUMAN_SIGNOFF_20261018.md` | 6,740 | `5cf4017f751443d567d5f4b82ae2d3efcc9c85fa36d84ba0181204a456c31d25` | 100% READ | Biên bản ký duyệt Gate G4 & T-008: Nghiệm thu Quality Engine trên synthetic integration data. |
| 31 | `docs/05-evidence/G4_SIGNOFF_TEST_EVIDENCE_ERRATA.md` | 6,585 | `93dd0236da4967a9a1a3ac309c8da7c8b667240284f0e3c35fd2f16e7f069eab` | 100% READ | Phụ lục đính chính bằng chứng kiểm thử G4. |
| 32 | `docs/05-evidence/G5_ENTRY_HANDOFF.md` | 10,151 | `39a88e8a2a8016424669128aae7e1eaac7e48001501055dea47b9972b2a6495c` | 100% READ | Đặc tả bàn giao đầu vào Gate G5: Phân chia phạm vi T-010 (smoke 2016) và T-011 (KPI, TS-008, TS-013, TS-018). |
| 33 | `docs/05-evidence/T007_HUMAN_SIGNOFF_20261018.md` | 11,293 | `c479046bcc76431f7df34a37339ef8e153f93bf91853759178702467094d3b88` | 100% READ | Biên bản ký duyệt Task T-007 (Raw Ingestion Pipeline). |
| 34 | `docs/05-evidence/T008_HUMAN_SIGNOFF_20261018.md` | 7,341 | `cdb90cb20844a93037693f5023794cd80c677d5ada63f0804ca9ee6baef82f20` | 100% READ | Biên bản ký duyệt Task T-008 (Quality Engine & Disjoint Accounting). |
| 35 | `docs/05-evidence/T010_HUMAN_SIGNOFF_20261018.md` | 9,413 | `62bedf399c1b5143f03814b484d6bb2ee289abf777c72d544ec3bed56cd2fafe` | 100% READ | Biên bản ký duyệt Task T-010 (2016 Real-data Smoke & Benchmark): Nghiệm thu 5,537,987 dòng, 100% metric valid. |
| 36 | `docs/05-evidence/T010_OFFICIAL_SIGNOFF_SCHEMA_AND_PROVENANCE_ERRATA.md` | 10,799 | `3243a4c7fdd14f5225a0132db3da5bfbfcfaf423efa3f817a7b0622a9cfe54dd` | 100% READ | Phụ lục đính chính schema Parquet: 10 String, 19 Double, 5 Long. OP_CARRIER_FL_NUM là DoubleType. |
| 37 | `docs/05-evidence/T010_SIGNOFF_CLOSURE_FINAL_VERDICT.md` | 8,214 | `5e0d8145f0ae3da9d6f0b45888e0c2f4ee39d4d8c5e7f8ae0794021a42e5e884` | 100% READ | Kết luận kiểm toán đóng 7 điểm hở của T-010. |
| 38 | `docs/05-evidence/T010_SIGNOFF_CLOSURE_PARQUET_SCHEMA_ERRATA.md` | 7,535 | `6ddaf00c9f127918fb359a404c40034cbc3b7b78e21bac6c66c246b2a5de8848` | 100% READ | Đính chính cấu trúc Parquet staging và fingerprint schema. |
| 39 | `docs/05-evidence/T010_FULL_FINAL_INDEPENDENT_VERDICT.md` | 7,643 | `e756b86921ad31bc61010ce3913846de2f2f528b4094daf0de1fdbb294628848` | 100% READ | Phán quyết độc lập của T-010 trước khi ký duyệt. |
| 40 | `docs/05-evidence/T003_UNIT_VERIFICATION.md` | 17,419 | `e2fdc8a6b2e634370a7ee37676a88f935b2b7824435e43bef0f0db7826b3eaba` | 100% READ | Kiểm chứng đơn vị T-003: Phân tầng bằng chứng 4 cấp; chứng minh đẳng thức tuyến tính; xác lập trạng thái PROVISIONAL. |
| 41 | `docs/05-evidence/T003_PERCENTILE_AND_MIN_N_DECISIONS.md` | 15,745 | `3793203b5524dad9ab21156323ad3faba5cefaa22c0c9658bebf6c325b8bf428` | 100% READ | Cơ sở toán học cho GK-sketch (accuracy=10000) và chính sách phân loại min-N. |
| 42 | `docs/05-evidence/T003_SIGNOFF_RECORD.md` | 9,456 | `590fa69047583811e8d68ed96a38d48a7f615791af626c11beb8a9e7542e49a2` | 100% READ | Hồ sơ nghiệm thu T-003: PASS_WITH_OPEN_RISKS (G2-EXC-001). |
| 43 | `docs/05-evidence/T010_FULL_DC11_DC12_ACCOUNTING_REPORT.md` | 4,338 | `845cf504f29e0e2a3c51015e324ab2b6532f64ef2c066a3b010f35527cfbcc27` | 100% READ | Báo cáo hạch toán DC-11/12 trên dữ liệu 2016: 5,537,987 accepted + 0 + 0. |
| 44 | `docs/05-evidence/T010_FULL_RESOURCE_BENCHMARK_TS014.md` | 6,588 | `f48b47614b5e5f23adc9a931944c13a9f9d69da8579092e8436b4693fb586b02` | 100% READ | Benchmark tài nguyên thực tế TS-014 năm 2016: 49.22s - 64.35s; 2.16 GiB RSS; 1.05 GiB JVM heap. |
| 45 | `docs/05-evidence/T010_FULL_SAFETY_GUARD_VERIFICATION.md` | 5,179 | `73261c32fb4afa0a15938d55b236d23bf436e5b5b3a422f6d19e4cb26d0b56d3` | 100% READ | Kiểm chứng các chốt chặn an toàn sản xuất (production guards). |
| 46 | `docs/05-evidence/T010_FULL_PARQUET_STAGING_VERIFICATION.md` | 4,390 | `89b3594c03b5464f8cf58a48d12a46308a984f682f43aa3bee472a817a8972f6` | 100% READ | Xác minh 50 tệp Parquet staging trong vùng cô lập. |
| 47 | `docs/05-evidence/T010_SIGNOFF_CLOSURE_METRIC_VALIDITY_INDEPENDENT_REVIEW.md` | 5,472 | `4e74a0919b570874100a4e126555e29ed77fd55719d31e934b674567ebdcb9c9` | 100% READ | PyArrow audit độc lập 5.53M dòng: 100% valid trên 7 trường đo CORE. |
| 48 | `docs/05-evidence/T010_SIGNOFF_CLOSURE_PRODUCTION_POLICY_GUARD.md` | 5,491 | `a0efbaf7ab77e47ed12f7fe01e9827c4689e50a0344596063fae775d39019fa3` | 100% READ | Chốt chặn chính sách flight number và weather nulls. |
| 49 | `docs/05-evidence/T010_SIGNOFF_CLOSURE_SOURCE_AND_RUN_PROVENANCE.md` | 5,541 | `ece551406af8a2fdd6177285363846aa8ee95f05e595acbfd5f9bc0dffa9268d` | 100% READ | Bằng chứng provenance của Run 1 và Run 2 năm 2016. |
| 50 | `docs/05-evidence/EVIDENCE_DELIVERABLE_REGISTER.json` | 201,579 | `23cbce795469afe9b3b1461f2587ed2341ff41cf8fdf00b8e4f4524a8ea7d5a0` | 100% READ | Sổ đăng ký bằng chứng chuẩn tắc: Hiện lưu trữ chính xác 512 registered deliverables. |

---

## 3. PHÁT HIỆN SAI LỆCH LỊCH SỬ & GIẢI QUYẾT CHUẨN TẮC (DISCREPANCIES & RESOLUTIONS)

1. **Số lượng trường đầu ra của KPI Engine (16 vs 17 trường):**
   - *Phát hiện:* Một số ghi chú lịch sử tóm tắt ghi "16 cột output". Tuy nhiên, theo danh sách chính thức tại `KPI_SPEC.md` và Master Prompt Mục 6.2, danh mục chuẩn tắc gồm đúng **17 trường**:
     `1. kpi_id, 2. submetric, 3. run_id, 4. kpi_version, 5. source_year, 6. group_dimensions, 7. filter_definition, 8. count_records, 9. count_metric_valid, 10. excluded_count, 11. metric_valid_rate, 12. source_coverage_status, 13. value, 14. unit_status, 15. min_n_status, 16. quality_version, 17. provenance_reference`.
   - *Nghị quyết chuẩn tắc:* KPI Engine tại T-011 triển khai đầy đủ **17 trường** theo đúng hợp đồng `KPI_SPEC.md`, tuyệt đối không lược bỏ bất kỳ trường nào.
2. **Kiểu dữ liệu cột `OP_CARRIER_FL_NUM` (LongType vs DoubleType):**
   - *Phát hiện:* Một số mô tả thiết kế ban đầu giả định `OP_CARRIER_FL_NUM` là LongType/Int64.
   - *Nghị quyết chuẩn tắc:* Biên bản nghiệm thu chính thức `T010_OFFICIAL_SIGNOFF_SCHEMA_AND_PROVENANCE_ERRATA.md` đã đính chính và xác lập: Schema Parquet sản xuất chuẩn tắc có `OP_CARRIER_FL_NUM` là **DoubleType** (Arrow float64). Cấu trúc 34 cột chính thức là **10 String, 19 Double, 5 Long**.
3. **Số lượng deliverables đã đăng ký (511 vs 512):**
   - *Phát hiện:* Báo cáo Agent T-010 trước đây từng đề cập 511 deliverables.
   - *Nghị quyết chuẩn tắc:* Đã kiểm toán nhị phân trực tiếp trên `EVIDENCE_DELIVERABLE_REGISTER.json`: Số lượng mục đăng ký thực tế là **512**. Bộ kiểm tra working tree `tools/check_working_tree_consistency.py` xác nhận 1,135 assertions PASS hoàn toàn với con số 512.
4. **Tính sẵn sàng của dữ liệu BTS TranStats bên ngoài cho `TS-018`:**
   - *Phát hiện:* Kho lưu trữ hiện tại không chứa bất kỳ tệp dữ liệu mẫu tải về từ cổng BTS TranStats bên ngoài nào (trong `docs/05-evidence/inputs/` chỉ có các tệp JSON/MD audit nội bộ).
   - *Nghị quyết chuẩn tắc:* Tuân thủ quy định tối cao của `AGENTS.md` (không bịa kết quả, không dùng dữ liệu giả lập để tuyên bố BTS parity PASS). Agent sẽ xây dựng hoàn chỉnh reconciler framework, kiểm chứng bằng synthetic fixtures, và nếu chưa có dữ liệu BTS thật từ Project Lead, bắt buộc phân loại `TS-018_REAL_DATA = PENDING_EXTERNAL_BTS_SOURCE / BLOCKED_BEFORE_G6`, bảo lưu điều kiện chặn trước Gate G6.

---

## 4. MA TRẬN ĐỐI SOÁT YÊU CẦU ĐẾN NGUỒN TÀI LIỆU (REQUIREMENT-TO-SOURCE CROSSWALK)

| Yêu cầu nhiệm vụ T-011 | Nguồn quy chuẩn | Ràng buộc kỹ thuật & Logic bắt buộc |
|---|---|---|
| **KPI-01** (Accepted record count) | `KPI_SPEC.md`, `DATA_CONTRACT.md` (DC-11) | Dùng `count_records`, cấm dùng `sum(FLIGHTS)`. |
| **KPI-02 & KPI-04** (Delay rate >= 15 min) | `KPI_SPEC.md`, `DECISIONS.md` (FP-DEC-008, FP-DEC-012) | Lấy biên đúng $15.0$ phút; mẫu số là $N_{\text{valid}}$ của chính trường đo đó. |
| **KPI-03 & KPI-05** (Signed delay mean) | `KPI_SPEC.md`, `DECISIONS.md` (FP-DEC-008) | Giữ nguyên độ trễ âm (chuyến bay đến/đi sớm); cấm gán âm về 0. |
| **KPI-06** (P50/P90 delay quantiles) | `KPI_SPEC.md`, `DECISIONS.md` (FP-DEC-015), `TEST_PLAN.md` (TS-008) | Dùng PySpark `percentile_approx(ARR_DELAY, array(0.5, 0.9), 10000)` trên cohort metric-valid; kiểm chứng sai số thứ hạng $\le 0.01\%$. |
| **KPI-07** (Mean Taxi-out & Taxi-in) | `KPI_SPEC.md`, `DATA_CONTRACT.md` (DC-12) | Hai submetrics có mẫu số độc lập $N_{\text{valid}}(\text{TAXI\_OUT})$ và $N_{\text{valid}}(\text{TAXI\_IN})$. |
| **KPI-08** (Mean Air, Actual & CRS Elapsed) | `KPI_SPEC.md`, `DATA_CONTRACT.md` (DC-12) | Ba submetrics có mẫu số độc lập tương ứng. |
| **Mẫu số 0 (Zero Denominator)** | `KPI_SPEC.md`, `DECISIONS.md` (FP-DEC-011), `TEST_PLAN.md` (TS-017) | Khi $N_{\text{valid}} == 0 \implies \text{value} = \text{null}$, mã `ZERO_METRIC_DENOMINATOR`. Cấm chia cho 0 hoặc trả về 0.0. |
| **Ngưỡng min-N** | `KPI_SPEC.md`, `DECISIONS.md` (FP-DEC-016), `TEST_PLAN.md` (TS-008) | Carrier-year (1000), Airport-year (365), Route-year (100). Gán nhãn `SUPPRESSED`, `LOW_SAMPLE_CAUTION`, `SUFFICIENT`. |
| **Fault Injection & Rollback** | `ARCHITECTURE.md`, `ROLLBACK_PLAN.md`, `TEST_PLAN.md` (TS-013) | Thực thi 100% trong synthetic sandbox; không phá hủy; không chuyển con trỏ `latest` khi gặp sự cố. |
| **BTS TranStats Parity** | `TEST_PLAN.md` (TS-018), `G2_OFFICIAL_SIGNOFF_HUMAN_ACCEPTANCE_RECORD.md` (G2-EXC-001) | Đối chiếu 7 trường đo CORE trên khóa `FL_DATE + OP_CARRIER + OP_CARRIER_FL_NUM + ORIGIN + DEST`. Điều kiện tiên quyết mở G6. |

---

## 5. KẾT LUẬN GATE 0A

- **Toàn bộ 50/50 tài liệu quy chuẩn và bằng chứng bắt buộc đã được đọc trọn vẹn 100%.**
- Không có tài liệu bắt buộc nào bị thiếu hoặc hỏng hóc.
- Mọi mâu thuẫn lịch sử đã được đối soát và giải quyết theo đúng thẩm quyền tài phán.
- **GATE 0A CHÍNH THỨC ĐẠT (PASS) — Cho phép chuyển sang Phase 0 (Preflight & Baseline Audit).**
