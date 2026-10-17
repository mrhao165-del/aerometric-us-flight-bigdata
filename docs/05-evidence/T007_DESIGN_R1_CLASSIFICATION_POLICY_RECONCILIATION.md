# T007 DESIGN R1 CLASSIFICATION POLICY RECONCILIATION — G3-COND-A & ROW ACCOUNTING

**Document ID:** `DOC-T007-DESIGN-R1-03-CLASSIFICATION-RECONCILIATION`  
**Task ID:** `T-007` (Raw CSV Ingestion Pipeline)  
**Phase:** `DESIGN REMEDIATION (R1)`  
**Gate:** `G4` (`PLANNED / NOT_COMPLETED`)  
**Design Authority:** Senior Big Data Architect & Data Contract Auditor  
**Binding Standards:** [`G3_OFFICIAL_SIGNOFF_HUMAN_ACCEPTANCE_RECORD.md`](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/docs/05-evidence/G3_OFFICIAL_SIGNOFF_HUMAN_ACCEPTANCE_RECORD.md) §3.1 (`G3-COND-A`), `DATA_CONTRACT.md` (DC-11, DC-12)  

---

## 1. OFFICIAL G3-COND-A TEXT & GOVERNANCE MANDATE

In the initial T-007 design, `OP_CARRIER_FL_NUM <= 0` was erroneously represented as a hard, approved quarantine rule. To restore absolute compliance with the Project Lead's binding gate conditions, the verbatim text of **`G3-COND-A`** is cited directly from [`docs/05-evidence/G3_OFFICIAL_SIGNOFF_HUMAN_ACCEPTANCE_RECORD.md`](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/docs/05-evidence/G3_OFFICIAL_SIGNOFF_HUMAN_ACCEPTANCE_RECORD.md) §3.1:

> ### 3.1. `G3-COND-A` — Chính sách Cách ly Bản ghi Không Phê duyệt Cứng (`Record-level Quarantine Policy is PROVISIONAL`)
> 1. **Bản chất chính sách:** Chính sách cách ly toàn bộ dòng bản ghi (`record-level quarantine`) ở tầng nạp hiện chỉ là **đề xuất kỹ thuật sơ bộ của Gate G3**, chưa được phê duyệt thành quy tắc cứng bắt buộc cho toàn bộ pipeline.
> 2. **Bảo vệ định danh chuyến bay:** Ràng buộc `OP_CARRIER_FL_NUM <= 0` **tuyệt đối không được tự động trở thành quy tắc cách ly cứng toàn bộ dòng** khi chưa thực hiện khảo sát và kiểm chứng thực nghiệm trên dữ liệu thô tại `G4/T-008`.
> 3. **Bảo toàn nguyên tắc phân định `DC-11 / DC-12`:**
>    - Chỉ có các vi phạm mỏ neo bản ghi cốt lõi (*Core Record-level Anchor Violations*: `INVALID_FL_DATE_CORE_ANCHOR`, `MISSING_CARRIER_CORE_ANCHOR`, `MISSING_AIRPORT_CORE_ANCHOR`, `INVALID_FLIGHT_NUM_CORE_ANCHOR`) mới đưa dòng vào `quarantined_row_count`.
>    - Các trường hợp vi phạm tính hợp lệ của số đo chuyên biệt (*Metric-Level Invalidity*, e.g., `TAXI_OUT < 0.0`, `TAXI_IN < 0.0`, `AIR_TIME <= 0.0`) **vẫn phải được phân loại là `accepted_row_count`**, vẫn được tính vào mẫu số của `KPI-01` (`count_records`) và chỉ bị loại khỏi mẫu số hợp lệ `count_metric_valid` của chính số đo đó.

---

## 2. POLICY TAXONOMY & STATUS DISAMBIGUATION

To eliminate ambiguity, all data quality and quarantine rules in the ingestion design are categorized under a tri-state governance taxonomy:

```
+---------------------------------------------------------------------------------------------------+
| 1. APPROVED (Hard Ingestion Rules)                                                                |
|    - Structural parse failure -> REJECTED                                                         |
|    - Missing Core Anchor (FL_DATE unparseable, null OP_CARRIER, null ORIGIN/DEST) -> QUARANTINED      |
+---------------------------------------------------------------------------------------------------+
                                                  |
+---------------------------------------------------------------------------------------------------+
| 2. PROVISIONAL (Candidate Rules - Non-Blocking in T-007)                                         |
|    - OP_CARRIER_FL_NUM <= 0 flagged with candidate code; NOT hard-quarantined without survey     |
+---------------------------------------------------------------------------------------------------+
                                                  |
+---------------------------------------------------------------------------------------------------+
| 3. PENDING_DATA_VALIDATION (Deferred to G4/T-008)                                                 |
|    - Empirical distribution survey of flight number values (zeros, negatives, decimals) across    |
|      the 54.7M rows conducted in T-008 before converting provisional rules to hard rules         |
+---------------------------------------------------------------------------------------------------+
```

---

## 3. DECONSTRUCTION OF `OP_CARRIER_FL_NUM` SCENARIOS

The handling of flight number values in the ingestion pipeline is designed with precise granularity:

| Value / Scenario | Data Type & Example | Provisional Status | Ingestion Handling in T-007 | Downstream Action in G4/T-008 |
|---|---|---|---|---|
| **Null Flight Number** | Null / Missing | `PROVISIONAL_ANCHOR_DEFECT` | Routed to quarantine candidate set (`QUARANTINE_NULL_FL_NUM`) as an incomplete identity anchor. | Reconciled in T-008 count audit. |
| **Zero (`FL_NUM == 0`)** | Integer `0` | `PROVISIONAL_ANOMALY` | **NOT automatically dropped or quarantined.** Ingested with `fl_num_zero_flag = True` into provisional accepted set. | T-008 surveys prevalence and decides whether to formally quarantine. |
| **Negative (`FL_NUM < 0`)** | Integer `-105` | `PROVISIONAL_ANOMALY` | **NOT automatically dropped or quarantined.** Ingested with `fl_num_negative_flag = True` into provisional accepted set. | T-008 surveys prevalence across all carriers and years. |
| **Float Literal (`x.0`)** | Double `1234.0` | `APPROVED_VALID_FORMAT` | Cast cleanly to Integer `1234`. Fully `ACCEPTED`. | Standard ingestion processing. |
| **Fractional Decimal** | Double `1234.5` | `PROVISIONAL_SYNTAX_ERROR` | Non-zero decimal indicates data token corruption. Flagged with `fl_num_fractional_flag`. | Examined in T-008 data quality profiling. |
| **Non-Numeric Token** | String `"DL102"` | `PROVISIONAL_ANCHOR_DEFECT` | Cast to integer returns `null`; treated as null flight number. | Examined in T-008 data quality profiling. |

> [!IMPORTANT]
> **Open Dependency on T-008:** In strict adherence to `G3-COND-A`, the final decision on whether `OP_CARRIER_FL_NUM <= 0` constitutes a hard quarantine rule is formally **deferred to Task T-008**. The T-007 pipeline design provides the structural measurement hooks without executing T-008 ahead of its DAG order.

---

## 4. APPROVED CORE RECORD ANCHORS VS. METRIC INVALIDITY

The distinction between **Record-Level Acceptance** and **Metric-Level Validity** is formally reaffirmed under `DC-11` and `DC-12`:

### 4.1. The Three Approved Core Record Anchors for Quarantine
A flight record enters `quarantined_row_count` if and only if it has valid 34-column CSV syntax but violates one of the following three essential identity anchors:
1. `INVALID_FL_DATE_CORE_ANCHOR`: `FL_DATE` is missing, null, or fails regex `^(?:\d{4}-\d{2}-\d{2}|\d{4}-\d{2}-\d{2} 00:00:00)$`.
2. `MISSING_CARRIER_CORE_ANCHOR`: `OP_CARRIER` is null or zero-length string.
3. `MISSING_AIRPORT_CORE_ANCHOR`: `ORIGIN` or `DEST` is null, zero-length, or fails length check ($\neq 3$).

### 4.2. Metric-Level Invalidity Never Quarantines Whole Records
Under `DATA_CONTRACT.md` DC-12 and `G3-COND-A`:
- Invalid, negative, or non-finite values in individual measure columns (`TAXI_OUT < 0.0`, `TAXI_IN < 0.0`, `AIR_TIME <= 0.0`, `ACTUAL_ELAPSED_TIME <= 0.0`, `DEP_DELAY = NaN`, `ARR_DELAY = Inf`) **MUST REMAIN CLASSIFIED AS `ACCEPTED`**.
- Such records are retained in the master dataset and contribute to `count_records` (the denominator of `KPI-01`).
- Such records are excluded **only** from the numerator and denominator of `count_metric_valid` for that specific submetric via `is_finite_numeric`.
- Auxiliary weather nulls (`O_TEMP`, `D_WSPD` are null) have **zero impact** on record acceptance per `FP-DEC-017` (`CONDITIONAL_NO_GO`).

---

## 5. MATHEMATICAL ROW INVARIANTS (DC-11 / DC-12)

The fundamental accounting invariants are preserved unconditionally:
$$N_{\text{raw}} = N_{\text{accepted}} + N_{\text{quarantined}} + N_{\text{rejected}}$$
$$\text{ACCEPTED} \cap \text{QUARANTINED} = \emptyset, \quad \text{ACCEPTED} \cap \text{REJECTED} = \emptyset, \quad \text{QUARANTINED} \cap \text{REJECTED} = \emptyset$$
$$\text{IAR} = \dfrac{N_{\text{accepted}}}{N_{\text{raw}}} \quad (N_{\text{raw}} > 0), \qquad \text{MVR}_m = \dfrac{N_{\text{valid}, m}}{N_{\text{accepted}}} \quad (N_{\text{accepted}} > 0)$$

---

## 6. CLASSIFICATION POLICY VERDICT

The row classification and quarantine architecture has been fully reconciled with `G3-COND-A`, preventing unauthorized hard quarantine while maintaining complete mathematical accounting rigor.

**CLASSIFICATION RECONCILIATION VERDICT: 100% COMPLIANT WITH G3-COND-A.**
