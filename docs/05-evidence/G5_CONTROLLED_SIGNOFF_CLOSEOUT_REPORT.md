# G5 Controlled Human Signoff & Governance Closeout Report

**Document ID:** `G5_CONTROLLED_SIGNOFF_CLOSEOUT_REPORT`  
**Date:** 2026-10-21  
**Project:** US Flight Performance Analysis 2016–2024  
**Task:** `G5-CONTROLLED-SIGNOFF`  
**Roles:** Project Governance Officer, Independent Evidence Reviewer, Senior Big Data Engineering Advisor  
**Authority:** Project Lead  
**Final Governance Verdict:** **`G5_PENDING_HUMAN_PREREQUISITES`**

---

## 1. D1–D4 Status Transition Matrix (Before vs. After)

| Decision ID | Subject / Scope | Status Before (Pre-Prompt) | Status After (Reconciled Closeout) | Governing Authority / Basis |
| :---: | :--- | :---: | :---: | :--- |
| **D1** | **BTS Source Provenance Attestation** | `DRAFT / PENDING_REVIEW` | **`PENDING_HUMAN_SOURCE_ATTESTATION`** | Physical bitwise identity verified (`342de99f...`, 29,975,383 bytes); awaiting first-person statement signed by physical downloader. |
| **D2** | **FP-DEC-019 Option B Formal Policy** | `DRAFT / PENDING_APPROVAL` | **`APPROVED_WITH_CONDITIONS`** (`FP-DEC-019`) | Approved by Project Lead explicit instruction (`PROJECT_LEAD_EXPLICIT_INSTRUCTION`, 2026-10-21). Bounded by `PARQUET_PARITY_NOT_TESTED`, `OR-08`, and 7 CORE measures. |
| **D3** | **TS-018 BTS Parity Human Technical Signoff** | `DRAFT / TECHNICALLY_READY` | **`CONDITIONALLY_ACCEPTED_PENDING_PREREQUISITES`** | Technical parity 100% bitwise exact (10,500/10,500 values, 14/14 negative tests PASS); conditionally accepted by Project Lead, awaiting D1 downloader attestation. |
| **D4** | **Gate G5 Human Gate Signoff** | `DRAFT / PENDING_SIGNOFF` | **`IN_PROGRESS / HUMAN_SIGNOFF_PENDING`** | All 19 G5 technical criteria verified PASS; closure formally awaiting completion of D1 and transition of D3 to official PASS. |

---

## 2. G6-ARCH-2016 Decision Status: Approved Option B

- **Decision Registered:** **`FP-DEC-020`** (registered in `docs/02-design/DECISIONS.md`).
- **Status:** **`APPROVED_BY_PROJECT_LEAD_INSTRUCTION`** (Date: 2026-10-21).
- **Approved Strategy:** **Option B — Unified Production Rerun of 2016**.
- **Architectural & Operational Commitments:**
  1. **Preserve T-010 Staging Baseline:** All 50 staging Parquet files produced during T-010 benchmark (`b5805fcae8db44e9a53c0eb1dfa1c1f3d9ec2983b3922bfbe5c6454f1654b09a`) are preserved intact and unperturbed as protected historical evidence.
  2. **Canonical RAW 2016 Re-execution:** The canonical 2016 RAW CSV (`4ed92ed732721a38ae28325135fad63436347613674ad96c1b273eb9d44cef34`, 1,538,427,452 bytes, 5,537,987 audited rows) will be processed through the unified production `IngestionCoordinator` as a new versioned production run (`run_2016_...`).
  3. **Standardized Sidecars:** Will generate standard production `run_manifest.json` and `execution_receipt.json`, ensuring schema and metadata compatibility across the entire 2016–2024 dataset.
  4. **Sequential Annual Ingestion:** Ingestion of 2016 will be validated before proceeding to subsequent years (2017 $\rightarrow$ 2024).
  5. **STRICT GOVERNANCE BOUNDARY:** Approving this architecture **DOES NOT** authorize executing the rerun. Execution remains strictly contingent upon Project Lead issuing Decision D5.

---

## 3. Human Approval Source & Authorization Boundaries

### 3.1 Traceable Human Authorization Source
On October 21, 2026, the Project Lead officially issued the explicit directive:
> *"tôi hoàn toàn đồng ý với ý kiến của bạn"*

This instruction was given in direct response to recommendations to:
1. Accept the completed targeted T-012 preflight corrections (16/16 test PASS, clean classification of PID enum states and fail-closed empty pointer).
2. Approve FP-DEC-019 Option B subject to explicit scope limitations.
3. Advance the D1 $\rightarrow$ D4 G5 signoff sequence as prerequisites are satisfied.
4. Select G6-ARCH-2016 Option B (versioned production rerun of 2016).
5. Prepare Gate G6 transition without initiating production ingestion.

### 3.2 Authorization Boundaries (What the Directive Does and Does NOT Authorize)
- **What is authorized:**
  - Technical acceptance of T-012 preflight remediation.
  - Policy approval of FP-DEC-019 Option B (`APPROVED_WITH_CONDITIONS`).
  - Architecture approval of G6-ARCH-2016 Option B (`APPROVED_BY_PROJECT_LEAD_INSTRUCTION`).
  - Conditional acceptance of TS-018 pending source attestation.
- **What is NOT authorized:**
  - This statement is **not** a first-person downloader attestation for the physical BTS file.
  - It does **not** provide a handwritten or cryptographic signature.
  - It does **not** authorize production T-012 execution.
  - It does **not** authorize Decision D5 (`NOT_AUTHORIZED`).

---

## 4. BTS Provenance Evidence & Missing Human Attestation

### 4.1 Physical File & Cryptographic Verification
Direct physical verification of the BTS reference archive confirms:
- **Canonical Path:** `data/reference/bts_transtats/original/T_ONTIME_REPORTING_20261019_112232.zip`
- **File Size:** `29,975,383` bytes (Exact Match)
- **SHA-256:** `342de99f65561fb856b524c704f2ad3851f8015f52251668ece346dff1350ae6` (Bitwise Verified)
- **ZIP File Integrity:** `zipfile.testzip()` returns `None` (0 corrupt members, CRC-32 `0x7d8573c4` verified)
- **Contained CSV Member:** `T_ONTIME_REPORTING.csv` (Uncompressed bytes: `217,369,264`, 108 columns, 583,985 data rows)
- **Table Name:** `Reporting Carrier On-Time Performance (1987-present)`, Period: January 2019

### 4.2 Exact Missing Human Downloader Attestation
Per `AGENTS.md` and repository governance, matching cryptographic hashes prove local bitwise identity against recorded baselines, but cannot substitute for attributable personal custody.

To close Decision D1 formally, the actual individual who downloaded the archive must sign the attestation statement in [`docs/05-evidence/G5_D1_BTS_PROVENANCE_ATTESTATION_DRAFT.md`](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/docs/05-evidence/G5_D1_BTS_PROVENANCE_ATTESTATION_DRAFT.md#L49-L64):

```markdown
Tôi, người ký tên dưới đây, xin chứng thực:
1. Vào ngày 19 tháng 10 năm 2026, tôi đã trực tiếp truy cập vào cổng cơ sở dữ liệu chính thức của Cục Thống kê Giao thông Vận tải Hoa Kỳ (BTS TranStats) tại địa chỉ:
   https://www.transtats.bts.gov/DL_SelectFields.aspx?QO_fu146_anzr=b0-gvzr&gnoyr_VQ=FGJ
2. Tôi đã chọn bảng dữ liệu "Reporting Carrier On-Time Performance (1987-present)" cho kỳ báo cáo: Năm 2019, Tháng 1 (January 2019).
3. Tôi đã tải về tệp nén gốc và lưu trữ nguyên vẹn vào đường dẫn data/reference/bts_transtats/original/T_ONTIME_REPORTING_20261019_112232.zip mà không thực hiện bất kỳ hành vi sửa đổi, biên tập, loại bỏ hoặc chèn thêm dữ liệu nào.
4. Mã băm SHA-256 tính toán trên tệp ZIP được lưu trữ hoàn toàn trùng khớp với giá trị 342de99f65561fb856b524c704f2ad3851f8015f52251668ece346dff1350ae6, kích thước đúng 29,975,383 bytes.
5. Biên lai giao dịch tải về hoặc chữ ký điện tử từ máy chủ BTS: NOT_PROVIDED (BTS không cấp kèm).

- Người thực hiện tải tệp (Downloader): [ĐIỀN HỌ TÊN VÀ KÝ]
- Ngày ký: [ĐIỀN NGÀY]
- Project Lead phê chuẩn quyết định D1: [KÝ DUYỆT]
```

---

## 5. TS-018 Technical Evidence Summary

The technical verification supporting TS-018 is 100% complete, reproducible, and passed:
- **Sample Design:** Controlled quota-stratified sample of 1,500 flight keys across 17 operating carriers from January 2019, generated via deterministic seed `ts018_bts_jan2019_seed_42`.
- **Duplicate Keys:** 0 duplicates in witness sample; 0 duplicates in RAW 2019 sample; 0 duplicates in BTS sample.
- **Seven Core Measures Tested:** `ARR_DELAY`, `DEP_DELAY`, `TAXI_OUT`, `TAXI_IN`, `AIR_TIME`, `ACTUAL_ELAPSED_TIME`, `CRS_ELAPSED_TIME`.
- **Numeric Comparisons:** Exactly 10,500 float64 values ($1,500 \times 7$) compared at bitwise IEEE-754 level.
- **Bitwise Exact Matches:** **10,500 / 10,500 (100.0%)**.
- **Tolerance-Only Cases:** 0.
- **Mismatches:** 0.
- **Negative Test Suite:** 14/14 fault-injection scenarios (NEG-W01 through NEG-W14) confirmed fail-closed.
- **Reference Policy Regressions:** 6/6 tests passed.

---

## 6. Status of G2-EXC-001 (Provisional Units Exception)

- **Current Status:** **`ACTIVE`**.
- **Governing Rule:** Under `AGENTS.md` and `DECISIONS.md`, exception `G2-EXC-001` permits provisional units (`OFFICIAL_MINUTES_EMPIRICALLY_CONSISTENT_PROVISIONAL`) during G2–G5, but mandates that TS-018 must achieve official `PASS` at Gate G5 before full multi-year production ingestion can run.
- **Transition Criterion:** As soon as Decision D1 receives human downloader attestation and Decision D3 is marked official `PASS`, `G2-EXC-001` will immediately transition to **`RESOLVED_BY_OPTION_B`** for the 7 CORE numeric measures.

---

## 7. Official Status of Gate G5

- **Status:** **`IN_PROGRESS / HUMAN_SIGNOFF_PENDING`**.
- **Technical Readyness:** 19/19 exit criteria satisfied (T-010 bounded smoke PASS on 5,537,987 rows, DC-11 row accounting balance, T-011 8 CORE KPIs implemented, Windows NTFS locking and SafePublisher atomic rollback verified, TS-018 exact numeric parity verified, safety disk margin 3.13x verified, T-012 preflight unblocked).
- **Closeout Prerequisite:** Awaiting completion of D1 human source attestation by the actual downloader, enabling D3 and D4 official signoffs.

---

## 8. Status of Decision D5 & Execution Confirmation

- **Decision D5 Status:** **`NOT_AUTHORIZED`** (Strictly Held).
- **Gate G6 Status:** **`NOT_STARTED / BLOCKED`**.
- **Task T-012 Status:** **`NOT_STARTED`**.
- **Execution Confirmation:**
  - Absolute confirmation: **Zero** production data was created.
  - Zero production Spark sessions were initiated.
  - Zero RAW source CSV files were modified.
  - Zero T-010 staging Parquet baseline files were touched.
  - Publication pointer `latest_run_id.txt` remains unperturbed.
  - Single-writer locks remain unreleased and untampered.

---

## 9. Summary of Changed Files & Rationale

| File Path | Nature of Change | Exact Rationale |
| :--- | :--- | :--- |
| `docs/02-design/DECISIONS.md` | Registered `FP-DEC-019` and `FP-DEC-020` | Formally record Project Lead's approval of Option B for TS-018 and Option B for G6-ARCH-2016 baseline integration. |
| `docs/04-execution/PROJECT_STATE.md` | Updated Gate snapshot, Section 1, 2, 3 | Align project governance status with 2026-10-21 decisions: D2 approved, G6-ARCH-2016 approved, D1 pending attestation, D3 conditionally accepted, G5 human signoff pending. |
| `docs/04-execution/AI_HANDOFF.md` | Updated Section 1 and Section 3.1 | Maintain strict context handoff for next agents regarding approved decisions, active limitations, and non-authorization of D5. |
| `docs/01-planning/BACKLOG.md` | Updated Task T-011 status line | Record FP-DEC-019 approval and D3 conditionally accepted status in the task backlog. |
| `docs/05-evidence/G5_D1_BTS_PROVENANCE_ATTESTATION_DRAFT.md` | Updated status to `PENDING_HUMAN_SOURCE_ATTESTATION` | Document physical bitwise identity verification and isolate the exact missing downloader statement. |
| `docs/05-evidence/G5_D2_FP_DEC_019_OPTION_B_APPROVAL_DRAFT.md` | Updated status to `APPROVED_WITH_CONDITIONS` | Record Project Lead approval via instruction (`APPROVED_BY_PROJECT_LEAD_INSTRUCTION`) without falsifying signatures. |
| `docs/05-evidence/G5_D3_TS018_HUMAN_TECHNICAL_SIGNOFF_DRAFT.md` | Updated status to `CONDITIONALLY_ACCEPTED_PENDING_PREREQUISITES` | Record technical completeness while preserving fail-closed hold pending D1 source attestation. |
| `docs/05-evidence/G5_D4_G5_HUMAN_GATE_SIGNOFF_DRAFT.md` | Updated status to `IN_PROGRESS / HUMAN_SIGNOFF_PENDING` | Record 19/19 technical readiness while holding gate closure until D1/D3 are effective. |
| `docs/05-evidence/G6_T012_2016_BASELINE_INTEGRATION_DECISION_DRAFT.md` | Updated status to `APPROVED_BY_PROJECT_LEAD_INSTRUCTION` | Record Project Lead selection of Option B (Unified Production Rerun 2016) while emphasizing D5 remains NOT_AUTHORIZED. |
| `docs/05-evidence/G5_CONTROLLED_SIGNOFF_CLOSEOUT_REPORT.md` | Created primary deliverable | Complete, transparent synthesis of G5 controlled closeout and governance state. |

---

## 10. Unresolved Prerequisite Requiring Project Lead Action

Only **one** concrete human action is required to achieve complete, unencumbered closure of Gate G5:

> **Action Required:** The individual who performed the download of `T_ONTIME_REPORTING_20261019_112232.zip` from BTS TranStats must fill in their name, date, and confirm the statement in [`docs/05-evidence/G5_D1_BTS_PROVENANCE_ATTESTATION_DRAFT.md`](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/docs/05-evidence/G5_D1_BTS_PROVENANCE_ATTESTATION_DRAFT.md#L49-L64) (or confirm it explicitly in chat as the downloader).

Upon completion of this single item:
1. Decision D1 $\rightarrow$ `PASS`.
2. Decision D3 $\rightarrow$ `PASS`, resolving `G2-EXC-001` to `RESOLVED_BY_OPTION_B` and closing T-011 full contract.
3. Decision D4 $\rightarrow$ `PASS`, formally closing Gate G5 (`G5 = PASS (CONTROLLED)`).
4. Project Lead may then hold the G6 operational readiness review and consider Decision D5.

---

## 11. Final Governance Verdict

$$\mathbf{VERDICT:}\quad \mathbf{G5\_PENDING\_HUMAN\_PREREQUISITES}$$

All technical requirements, tests, algorithms, and data contracts are 100% verified and PASS. Formal closure is held exclusively for the legitimate human source attestation of Decision D1, maintaining absolute fidelity to the project's governance charter.
