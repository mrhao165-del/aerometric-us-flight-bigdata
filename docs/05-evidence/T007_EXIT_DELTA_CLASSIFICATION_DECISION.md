# T007 EXIT DELTA - CLASSIFICATION & PROVISIONAL QUARANTINE DECISION TABLE

**Document ID:** `DOC-T007-EXIT-DELTA-02-CLASSIFICATION-DECISION`  
**Task ID:** `T-007` (Raw CSV Ingestion Pipeline)  
**Gate:** `G4` (`PLANNED / NOT_COMPLETED`)  
**Design Authority:** Lead PySpark Architect & Data Contract Auditor  
**Binding Standards:** `DATA_CONTRACT.md` (DC-11/12), `G3_OFFICIAL_SIGNOFF_HUMAN_ACCEPTANCE_RECORD.md` (G3-COND-A/B/C)  

---

## 1. FOUR-LAYER CLASSIFICATION TAXONOMY

To guarantee mutual exclusivity and mathematical completeness under DC-11 without violating metric-level independence (DC-12), T-007 enforces a strict **Four-Layer Evaluation Hierarchy**:

```
[Raw Physical Input Stream]
           │
           ▼
[LAYER 1: Parser-Level Unrecoverable Corruption] ───(Malformed Syntax/Token Count)───► REJECTED DATASET
           │ (Clean CSV Syntax)
           ▼
[LAYER 2: Recoverable Field Parse Anomaly] ────────(Non-numeric Metric / Cast Failure)──► FIELD NULL / STAGING
           │
           ▼
[LAYER 3: Record-Level Identity & Core Anchors] ───(Missing Date/Carrier/Airport)────► QUARANTINED (or Flagged)
           │ (Valid Core Anchors)
           ▼
[LAYER 4: Metric-Specific Evaluation (DC-12)] ────(Delay / AirTime / Taxi Validation)──► ACCEPTED CURATED
                                                                                         (Metrics Valid / Invalid)
```

---

## 2. CANONICAL CLASSIFICATION DECISION TABLE (11 SITUATIONS)

| Sit. ID | Case Situation | Raw Token Example | Parsed Value | Record Classification | Metric Validity | Reason Code | Canonical Authority | Policy Status | Test / Evidence ID |
| :---: | :--- | :--- | :--- | :---: | :---: | :--- | :--- | :---: | :---: |
| **S-01** | **Null Flight Number** | `""` or `\s+` | `NULL` | **QUARANTINED** | `N/A` | `MISSING_CORE_ANCHOR_FL_NUM` | `DATA_CONTRACT.md` (DC-01) | `CANONICAL_ENFORCED` | `TS-003-ANCHOR-01` |
| **S-02** | **Zero / Negative Flight Number** | `"0"` or `"-100"` | `0` or `-100` | **ACCEPTED** *(with anomaly tag)* | Evaluated per metric | `ANOMALY_NON_POSITIVE_FL_NUM` | `G3-COND-A` (Provisional Rule) | `POLICY_DECISION_PENDING` *(Awaiting T-008 Survey)* | `TS-003-ANCHOR-02` |
| **S-03** | **Non-Numeric Flight Number** | `"UA123"` or `"FL_A"` | `NULL` | **QUARANTINED** | `N/A` | `INVALID_FL_NUM_FORMAT` | `DATA_CONTRACT.md` (DC-01) | `CANONICAL_ENFORCED` | `TS-003-ANCHOR-03` |
| **S-04** | **Fractional Flight Number** | `"100.5"` | `NULL` *(via regex cast)* | **QUARANTINED** | `N/A` | `NON_INTEGER_FL_NUM` | `DATA_CONTRACT.md` (DC-01) | `CANONICAL_ENFORCED` | `TS-003-ANCHOR-04` |
| **S-05** | **Missing Core Anchors** | `FL_DATE=""` or `ORIGIN=""` | `NULL` | **QUARANTINED** | `N/A` | `MISSING_IDENTITY_ANCHOR` | `DATA_CONTRACT.md` (DC-01) | `CANONICAL_ENFORCED` | `TS-003-ANCHOR-05` |
| **S-06** | **Invalid FL_DATE Format** | `"01/01/2016"` or `"2016-02-30"` | `NULL` | **QUARANTINED** | `N/A` | `INVALID_DATE_FORMAT` | `DATA_CONTRACT.md` (DC-01) | `CANONICAL_ENFORCED` | `TS-004-DATE-01` |
| **S-07** | **Invalid DEP/ARR Delay** | `"NA"` or `"99999.0"` or `NaN` | `NULL` | **ACCEPTED** | `INVALID` | `METRIC_PARSE_FAILURE` | `DATA_CONTRACT.md` (DC-12) & `G3-COND-B` | `CANONICAL_ENFORCED` | `TS-003-METRIC-01` |
| **S-08** | **Negative Valid Delay** | `"-15.0"` | `-15.0` | **ACCEPTED** | `VALID` | `NORMAL_EARLY_FLIGHT` | `KPI_SPEC.md` (KPI-03 Signed Mean) | `CANONICAL_ENFORCED` | `TS-003-METRIC-02` |
| **S-09** | **Invalid Taxi / Air Time** | `"-5.0"` or `"NaN"` | `NULL` | **ACCEPTED** | `INVALID` | `NEGATIVE_ELAPSED_OR_TAXI` | `G3-COND-B` & `TEST_PLAN.md` (TS-012) | `CANONICAL_ENFORCED` | `TS-012-METRIC-03` |
| **S-10** | **Malformed CSV Token Count** | `< 34` or `> 34` tokens | Raw String in `_corrupt_record` | **REJECTED** | `N/A` | `CSV_PARSER_TOKEN_MISMATCH` | `DATA_CONTRACT.md` (DC-11) | `CANONICAL_ENFORCED` | `TS-003-REJECT-01` |
| **S-11** | **Missing Weather Data** | `O_TEMP=""` or `D_WSPD=""` | `NULL` | **ACCEPTED** | Flight valid, weather pending | `WEATHER_OPTIONAL_ABSENT` | `DECISIONS.md` (FP-DEC-017) | `CANONICAL_ENFORCED` *(Weather Conditional No-Go)* | `TS-003-WX-01` |

---

## 3. RESOLUTION OF BLOCKER CSV-02: DC-11 & DC-12 ALIGNMENT

### 3.1. Strict Distinction: Parser Corruption vs Field Metric Invalidation
- **Parser Corruption (`rejected/`):** Triggered strictly when a line fails basic CSV framing (unbalanced quotes, invalid delimiters, physical token count $\ne 34$). These rows cannot be safely projected into 34 columns.
- **Metric Invalidation (Curated In-Place `NULL`):** When a row has exactly 34 tokens and valid identity anchors (`FL_DATE`, `OP_CARRIER`, `FL_NUM > 0`, `ORIGIN`, `DEST`), but a measure column like `DEP_DELAY` contains `"NA"`, the record is **NOT REJECTED**.
  - The record is accepted into Curated Parquet.
  - The column `DEP_DELAY` is cast to `NULL`.
  - In KPI calculation, DC-12 denominator accounting applies:
    $$\text{count\_records} = 1, \quad \text{count\_metric\_valid} = 0, \quad \text{excluded\_count} = 1$$
  - The valid flight is preserved for volume, route, and operational carrier reporting.

### 3.2. Preservation of G3-COND-A on `OP_CARRIER_FL_NUM <= 0`
- Under **G3-COND-A**, the proposal to hard-quarantine flights with `OP_CARRIER_FL_NUM <= 0` was explicitly approved as **PROVISIONAL**.
- T-007 design conforms to this constraint:
  - Non-positive flight numbers (`FL_NUM <= 0`) are **NOT hard-quarantined** in T-007.
  - They are ingested into Curated Staging with an explicit diagnostic boolean flag: `ANOMALY_NON_POSITIVE_FL_NUM = true`.
  - Task T-008 will run an empirical frequency survey across all 54.7M rows to determine whether `FL_NUM <= 0` represents military, test, or ferry operations before Project Lead makes a final quarantine decision.

### 3.3. Mathematical Proof of Mutual Exclusivity (DC-11)
Every logical raw record $r \in \mathcal{R}_{\text{raw}}$ is partitioned by deterministic, non-overlapping predicates:
$$\mathcal{R}_{\text{rejected}} = \{r \in \mathcal{R}_{\text{raw}} \mid r.\text{\_corrupt\_record} \neq \text{NULL}\}$$
$$\mathcal{R}_{\text{quarantined}} = \{r \in \mathcal{R}_{\text{raw}} \setminus \mathcal{R}_{\text{rejected}} \mid \text{MissingIdentity}(r) \lor \text{MalformedAnchor}(r)\}$$
$$\mathcal{R}_{\text{accepted}} = \mathcal{R}_{\text{raw}} \setminus (\mathcal{R}_{\text{rejected}} \cup \mathcal{R}_{\text{quarantined}})$$

Therefore:
$$\mathcal{R}_{\text{accepted}} \cap \mathcal{R}_{\text{quarantined}} = \emptyset, \quad \mathcal{R}_{\text{accepted}} \cap \mathcal{R}_{\text{rejected}} = \emptyset, \quad \mathcal{R}_{\text{quarantined}} \cap \mathcal{R}_{\text{rejected}} = \emptyset$$
$$\mathcal{R}_{\text{accepted}} \cup \mathcal{R}_{\text{quarantined}} \cup \mathcal{R}_{\text{rejected}} = \mathcal{R}_{\text{raw}}$$
$$N_{\text{raw}} = N_{\text{accepted}} + N_{\text{quarantined}} + N_{\text{rejected}}$$
Non-negative domain check: $N_{\text{raw}} \ge 0, N_{\text{accepted}} \ge 0, N_{\text{quarantined}} \ge 0, N_{\text{rejected}} \ge 0$.
If this balance fails by even 1 record, `SafePublisher` aborts with `status="ACCOUNTING_UNVERIFIED"`.
