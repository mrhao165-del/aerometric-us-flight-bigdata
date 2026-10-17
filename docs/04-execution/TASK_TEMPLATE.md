# TASK_TEMPLATE — Mẫu Yêu cầu và Báo cáo Nghiệm thu Nhiệm vụ AI Agent

**Version:** `docs-v1.1` (cập nhật đồng bộ quản trị `G2-REPO-APPLY` & đính chính ngữ nghĩa `G2-REPO-APPLY-R1` tại [`G2_REPO_APPLY_R1_SEMANTIC_ERRATA.md`](../05-evidence/G2_REPO_APPLY_R1_SEMANTIC_ERRATA.md), 2026-10-16).  
**Quy tắc bắt buộc:** Mọi nhiệm vụ của AI Agent phải tạo ra **tệp bằng chứng vật lý thực tế dưới `docs/05-evidence/`** và đăng ký đầy đủ vào [`docs/05-evidence/EVIDENCE_DELIVERABLE_REGISTER.json`](../05-evidence/EVIDENCE_DELIVERABLE_REGISTER.json). **Chỉ phản hồi trong khung chat (chat response alone) tuyệt đối KHÔNG được chấp nhận là bằng chứng hoàn thành nhiệm vụ.**

---

## Mẫu Khung Nhiệm vụ và Báo cáo Nghiệm thu Chuẩn (`Standard Task Contract & Evidence Template`)

```markdown
# TASK: <TASK-ID> — <Tên nhiệm vụ>

## 1. Gate Áp dụng, Phụ thuộc & Trạng thái Khởi đầu (`Applicable Gate & Dependencies`)
- **Đề tài:** Phân tích hiệu suất chuyến bay Hoa Kỳ 2016–2024 bằng Apache Spark / PySpark (nghiên cứu mô tả hồi cứu; loại trừ ML, dự báo T-2h riêng sân bay ATL, và tệp đồ thị `.pt`).
- **Gate áp dụng:** `<G#>` | **Trạng thái Gate hiện tại:** `<IN_PROGRESS / NOT_PASSED / PLANNED / ...>`
- **Phụ thuộc bắt buộc (`Dependencies`):** `<Liệt kê Task/Gate phải hoàn tất trước theo ROADMAP.md và BACKLOG.md; lưu ý ở G4: T-009 phải hoàn tất trước T-007 và T-008>`
- **Tài liệu bắt buộc đọc trước khi thực thi:** `AGENTS.md`, `docs/04-execution/PROJECT_STATE.md`, `docs/04-execution/AI_HANDOFF.md`, `docs/02-design/DECISIONS.md`, `docs/02-design/DATA_CONTRACT.md`, `docs/02-design/KPI_SPEC.md`, `docs/03-quality/TEST_PLAN.md`, `docs/03-quality/RISK_REGISTER.md`, `docs/05-evidence/G2_REPO_APPLY_R1_SEMANTIC_ERRATA.md`.

## 2. Các Quyết định Kiến trúc & Ngoại lệ Đã Phê duyệt Áp dụng (`Current Approved Decision IDs`)
- **Các mã quyết định áp dụng:** `<Liệt kê chính xác từ FP-DEC-001 đến FP-DEC-017 trong docs/02-design/DECISIONS.md; trạng thái phê duyệt: APPROVED_BY_PROJECT_LEAD_INSTRUCTION (không dùng SIGNED_BY_PROJECT_LEAD_INSTRUCTION)>`
- **Ngoại lệ áp dụng (nếu có):** `<Ví dụ: G2-EXC-001 cho đúng 7 trường số đo CORE trong CSV nguồn (không gồm ELAPSED_DIFF) — giữ unit_status = OFFICIAL_MINUTES_EMPIRICALLY_CONSISTENT_PROVISIONAL, bắt buộc TS-018 PASS ở Gate G5 trước khi chạy G6>`
- **Yêu cầu / Câu hỏi nghiên cứu / KPI liên quan:** `<REQ-##, RQ-##, KPI-01..08 (CORE), KPI-09 (OPTIONAL_DRAFT), KPI-10 (CONDITIONAL_NO_GO), KPI-11 (NOT_COMPUTABLE từ 34 cột hiện tại), KPI-12 (BLOCKED)>`

## 3. Phạm vi Tệp Được Phép Sửa & Bị Cấm Sửa (`Allowed & Forbidden Files`)
- **Tệp được phép sửa đổi (`Allowed files to modify`):** `<Liệt kê đường dẫn chính xác>`
- **Tệp được phép tạo mới (`Allowed files to create`):** `<Liệt kê đường dẫn dưới docs/05-evidence/ hoặc thư mục được giao>`
- **Tệp/Thư mục bị CẤM sửa đổi (`Forbidden files to modify`):**
  - `data/raw/tabular/{year}/flight_with_weather_{year}.csv` (`2016..2024` — 9 tệp CSV nguồn ~15.2 GB tuyệt đối chỉ đọc; gồm 6 cột thời tiết `O_TEMP, O_PRCP, O_WSPD, D_TEMP, D_PRCP, D_WSPD`).
  - `docs/05-evidence/inputs/` và `docs/05-evidence/inputs/SOURCE_MANIFEST.json` (13 tệp kiểm toán lịch sử bất biến).
  - `PACKAGE_MANIFEST.json` (bản kê 47 tệp gốc của gói `docs-v1.1`).
  - Các báo cáo bằng chứng lịch sử đã xuất (`T001_..T005_`, `G2_FINAL_*`, `G2_R1_*`, `G2_SIGNOFF_*`, `G2_REPO_APPLY_*.md`, và `docs/05-evidence/G2_REPO_APPLY_BACKUPS/`) — chỉ đính chính bằng tệp addendum/errata mới có phiên bản.
  - Cấm nạp `.pt` qua `torch.load`, cấm tự ý thay đổi công thức KPI hoặc định nghĩa `DC-11`/`DC-12`.

## 4. Giả định Danh tính Dữ liệu Nguồn & Baseline Trước Khi Sửa (`Source Data Identity & Pre-Change Baseline`)
- **Trạng thái danh tính dữ liệu nguồn (`Source Data Identity Assumptions`):**
  - `OR-08 = IDENTITY_UNVERIFIED` (`R-16`; `METADATA_MATCH_ONLY` qua `size/mtime` cho đến khi tính SHA-256 cục bộ tại `G4/T-007` và `G5` theo `TS-019`; không tuyên bố trùng khớp bit-level với BTS gốc nếu chưa có mã băm đối chiếu từ nguồn ngoài).
  - `OR-05 = OPEN_QUALITY_DEFECT` (`R-10`; Năm 2024 chỉ có `335/366` ngày, thiếu 31 ngày Tháng 3/2024; `source_coverage_status = PARTIAL`).
  - `OR-03` (`R-15`; Đơn vị 7 trường đo CORE là `OFFICIAL_MINUTES_EMPIRICALLY_CONSISTENT_PROVISIONAL` theo `G2-EXC-001`).
- **Baseline trước khi sửa đổi (`Pre-Change Baseline`):**
  - Ghi rõ kích thước byte, mã băm SHA-256 và vị trí bản sao lưu (backup/Git) của mọi tệp hiện hữu trước khi chỉnh sửa.

## 5. Lệnh Kiểm thử, Kết quả Kỳ vọng & Kết quả Thực tế (`Test Commands, Expected & Actual Results`)
- **Phân biệt bắt buộc:** Ghi rõ bài kiểm thử là `SPECIFIED / NOT_RUN` (mới thiết kế đặc tả) hay `EXECUTED_PASS / EXECUTED_FAIL` (đã chạy lệnh thực tế).
- **Bảng thực thi lệnh kiểm thử:**
  | Lệnh thực thi (`Command`) | Thư mục chạy (`Cwd`) | Kết quả kỳ vọng (`Expected`) | Exit Code thực tế | Số lượng `PASS / FAIL / SKIP` | Ghi chú / Log |
  |---|---|---|---:|---|---|
  | `<python ...>` | `<...>` | `Exit Code 0` | `<0/1>` | `<...>` | `<...>` |

## 6. Danh mục Tệp Bằng chứng Đầu ra, Kích thước & SHA-256 (`Evidence Outputs & Cryptographic Hashes`)
- Mọi tệp bằng chứng xuất ra dưới `docs/05-evidence/` phải được đọc lại kiểm tra UTF-8, kiểm tra liên kết tương đối, ghi nhận kích thước byte, tính mã băm SHA-256 và đăng ký vào `docs/05-evidence/EVIDENCE_DELIVERABLE_REGISTER.json`:
  | Đường dẫn tệp bằng chứng (`docs/05-evidence/...`) | Vai trò Artifact | Kích thước (Bytes) | Mã băm SHA-256 | Trạng thái đăng ký `EVIDENCE_DELIVERABLE_REGISTER.json` |
  |---|---|---:|---|---|
  | `<docs/05-evidence/...>` | `<...>` | `<...>` | `<64-hex>` | `REGISTERED & VERIFIED` |

## 7. Quy trình Phục hồi (`Rollback Procedures`)
- Nêu rõ cách khôi phục từng tệp đã sửa về trạng thái byte-for-byte ban đầu (từ Git hoặc từ thư mục backup đã đăng ký) và cách gỡ bỏ các tệp mới tạo nếu phát hiện lỗi hồi quy mà không chạm vào `data/raw/`.

## 8. Rủi ro Chưa Giải quyết, Yêu cầu Phê duyệt của Con người & Điều kiện Dừng (`Risks, Human Approvals & Stop Conditions`)
- **Rủi ro còn mở (`Known Unresolved Risks`):** `<Đối chiếu chính xác OR-01..OR-08 và R-01..R-17 theo docs/03-quality/RISK_REGISTER.md; không tự ý gán lại ý nghĩa mã rủi ro>`
- **Yêu cầu phê duyệt của con người (`Human Approval Requirements`):** `<Liệt kê các quyết định hoặc cổng kiểm soát cần Project Lead ký duyệt>`
- **Điều kiện dừng tường minh (`Explicit Stop Conditions`):**
  - Dừng ngay lập tức nếu phát hiện mâu thuẫn hợp đồng, hỏng mã băm của `SOURCE_MANIFEST.json`, hoặc thất bại kiểm thử bảo mật/toàn vẹn.
  - Không tự ý chuyển Gate sang `PASS` hoặc khởi động nhiệm vụ của Gate tiếp theo khi chưa có ủy quyền.

## 9. Trạng thái Kết thúc Nhiệm vụ (`Final Task Status`)
- **Final Status:** `<PASS / FAIL / BLOCKED / NOT_RUN / CONDITIONAL>` *(Đối với nhánh tùy chọn hoặc tài liệu: ghi rõ `CONDITIONAL_PENDING`, `CONDITIONAL_NO_GO`, hoặc `design/documentation only`)*
```

---

## Quy tắc Thực thi Bắt buộc
1. Không gộp nhiều Gate phụ thuộc vào cùng một lần thực thi nếu chưa có phê duyệt chuyển cổng của Project Lead.
2. Mọi thay đổi đối với tài liệu sống hoặc tệp bằng chứng đều phải chạy lại `python tools/check_working_tree_consistency.py` và `python tools/qa/verify_g2_repo_apply_r1_semantic_invariants.py` và đạt `Exit Code 0` trước khi kết thúc nhiệm vụ.
