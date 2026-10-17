# T007 DESIGN CLASSIFICATION AND ACCOUNTING — MATHEMATICAL INVARIANTS & DECISION TABLE

**Document ID:** `DOC-T007-DESIGN-04-CLASSIFICATION-ACCOUNTING`  
**Task ID:** `T-007` (Raw CSV Ingestion Pipeline)  
**Phase:** `DESIGN ONLY`  
**Gate:** `G4` (`PLANNED / NOT_COMPLETED`)  
**Design Authority:** Senior Big Data Architect, Data Contract Auditor & QA Reviewer  
**Binding Contracts:** `DATA_CONTRACT.md` (DC-11, DC-12), `G3-COND-A`, `FP-DEC-010`, `FP-DEC-017`  

---

## 1. MATHEMATICAL INVARIANTS (DC-11 & DC-12)

The canonical contracts establish strict mathematical accounting rules that must be preserved unconditionally throughout ingestion:

### 1.1. Invariant 1: Row Partition Conservation (DC-11)
For any ingestion run $R$ processing raw source dataset $S$:
$$N_{\text{raw}} = N_{\text{accepted}} + N_{\text{quarantined}} + N_{\text{rejected}}$$
Where:
- $N_{\text{raw}}$: Total physical data lines parsed from source CSV files (excluding the header line).
- $N_{\text{accepted}}$: Rows passing structural and core identity anchor validation.
- $N_{\text{quarantined}}$: Rows with valid 34-column CSV structure but failing identity anchor validation.
- $N_{\text{rejected}}$: Unparseable physical lines (malformed CSV syntax, token count mismatch, byte corruption).

### 1.2. Invariant 2: Mutual Exclusivity
Every input row $r \in S$ must be mapped to exactly one classification state:
$$\text{Class}(r) \in \{\text{ACCEPTED}, \text{QUARANTINED}, \text{REJECTED}\}$$
$$\text{ACCEPTED} \cap \text{QUARANTINED} = \emptyset, \quad \text{ACCEPTED} \cap \text{REJECTED} = \emptyset, \quad \text{QUARANTINED} \cap \text{REJECTED} = \emptyset$$

### 1.3. Invariant 3: Ingestion Acceptance Rate (IAR) (DC-12)
$$\text{IAR} = \begin{cases} 
\dfrac{N_{\text{accepted}}}{N_{\text{raw}}} & \text{if } N_{\text{raw}} > 0 \\ 
\text{ZERO\_DENOMINATOR} & \text{if } N_{\text{raw}} = 0 
\end{cases}$$

### 1.4. Invariant 4: Metric Valid Rate (MVR) Decoupling (DC-12)
For any metric $m \in \{\text{DEP\_DELAY}, \text{ARR\_DELAY}, \text{TAXI\_OUT}, \text{TAXI\_IN}, \text{AIR\_TIME}, \text{CRS\_ELAPSED\_TIME}, \text{ACTUAL\_ELAPSED\_TIME}\}$:
$$\text{MVR}_m = \begin{cases} 
\dfrac{N_{\text{valid}, m}}{N_{\text{accepted}}} & \text{if } N_{\text{accepted}} > 0 \\ 
\text{ZERO\_DENOMINATOR} & \text{if } N_{\text{accepted}} = 0 
\end{cases}$$
> [!IMPORTANT]
> **Record Validity vs. Metric Validity:** A flight record is `ACCEPTED` as long as its physical structure and flight identity anchors are sound. An invalid, non-finite, or null value in a specific metric column (e.g. `AIR_TIME = -5.0` or `TAXI_OUT = NaN`) **DOES NOT** quarantine the entire record. The record remains `ACCEPTED` and contributes to `count_records` (KPI-01), but is excluded from the numerator and denominator of the specific metric subcalculation.

---

## 2. CANONICAL 12-SCENARIO DECISION TABLE

The following decision table governs the exact classification, metric impact, and error handling for all potential source data anomalies:

| Scenario # | Data Scenario Description | Record Status | Metric Validity Impact | Canonical Authority | Test Fixture ID | Ingestion Action |
|---|---|---|---|---|---|---|
| **SC-01** | **Missing Required Structural Column** (e.g., CSV has only 33 columns; missing `ORIGIN`) | **INGESTION_ABORT** (Job Failure) | N/A (Run aborted) | `DATA_CONTRACT.md` §3 | `FIX-06` | Abort preflight validation with `SchemaMismatchError`. No Parquet written. |
| **SC-02** | **Unexpected Extra Column** (e.g., CSV has 35 columns) | **INGESTION_ABORT** (Job Failure) | N/A (Run aborted) | `DATA_CONTRACT.md` §3 | `FIX-07` | Abort preflight validation with `SchemaMismatchError`. Strict 34-column schema enforcement. |
| **SC-03** | **Malformed Date Token** (e.g., `FL_DATE = "2018-02-31"`, `"INVALID"`, or null) | **QUARANTINED** | Excluded from curated Parquet | `DATA_CONTRACT.md` DC-11 | `FIX-03` | Route to quarantine dataset with reason `QUARANTINE_MALFORMED_DATE`. |
| **SC-04** | **Nullable Non-Core Field is Null** (e.g., `TAXI_IN` is null, but all anchors valid) | **ACCEPTED** | Excluded from `TAXI_IN` denominator; included in all other metrics | `DATA_DICTIONARY.md` | `FIX-01` | Ingest into curated Parquet. `TAXI_IN` remains null. |
| **SC-05** | **Invalid Non-Finite Numeric** (e.g., `DEP_DELAY = "NaN"` or `"Infinity"`) | **ACCEPTED** | Excluded from `DEP_DELAY` denominator via `is_finite_numeric` | `src/flight_pipeline/quality/predicates.py` | `FIX-09` | Ingest into curated Parquet. Field stored as null. Record retained in `count_records`. |
| **SC-06** | **Negative Signed Delay** (e.g., `DEP_DELAY = -15.0`, `ARR_DELAY = -22.0`) | **ACCEPTED** | **VALID METRIC VALUE**; fully included in delay distributions | `KPI_SPEC.md` §2.1 | `FIX-08` | Ingest as valid early departure/arrival. Delay preserved exactly. |
| **SC-07** | **Invalid Single KPI Measure** (e.g., `AIR_TIME <= 0.0` or `ACTUAL_ELAPSED_TIME <= 0.0`) | **ACCEPTED** | Excluded from `AIR_TIME` valid count per `is_valid_air_time` | `src/flight_pipeline/quality/predicates.py` | `FIX-09` | Ingest into curated Parquet. Excluded from KPI-05 average air time. |
| **SC-08** | **Invalid Flight Number** (`OP_CARRIER_FL_NUM <= 0` or null) | **QUARANTINED** | Excluded from curated Parquet | `G3-COND-A` (Provisional Rule) | `FIX-05` | Route to quarantine dataset with reason `QUARANTINE_INVALID_FL_NUM`. |
| **SC-09** | **Missing Auxiliary Weather** (e.g., `O_TEMP`, `D_WSPD` are null) | **ACCEPTED** | Zero impact on CORE metrics (`DEP_DELAY`, `ARR_DELAY`, etc.) | `FP-DEC-017` (CONDITIONAL_NO_GO) | `FIX-10` | Ingest into curated Parquet. Weather fields stored as null. Core metrics unaffected. |
| **SC-10** | **Malformed CSV Text Line** (unclosed quotes, mismatched commas, byte corruption) | **REJECTED** | Never enters structured DataFrame | `DATA_CONTRACT.md` DC-11 | `FIX-02` | Captured via `_corrupt_record` or parser error. Routed to `rejected/` raw text store. |
| **SC-11** | **Duplicate Row / Identity Ambiguity** (two identical rows in raw CSV) | **ACCEPTED** (with Lineage) | Included in all valid metrics per raw instance | `FP-DEC-008`, `ANALYSIS_PROTOCOL.md` | `FIX-01` | Ingested as reported. Deduplication is strictly out-of-scope for raw bronze ingestion. |
| **SC-12** | **Missing Calendar Month in Source Coverage** (Year 2024 missing March) | **ACCEPTED** (for available days) | Ingestion continues for available 335 days | `OR-05` (OPEN_QUALITY_DEFECT) | `FIX-01` | Ingest available data. Explicitly log `OR-05` defect and date gap in `RunManifest`. |

---

## 3. QUARANTINE & REJECTION REASON CODE SPECIFICATION

To ensure full audit traceability, every quarantined or rejected row must be annotated with a canonical reason code:

### 3.1. Quarantine Reason Codes
1. `QUARANTINE_MALFORMED_DATE`: `FL_DATE` is null, unparseable, or fails regex `^(?:\d{4}-\d{2}-\d{2}|\d{4}-\d{2}-\d{2} 00:00:00)$`.
2. `QUARANTINE_NULL_CARRIER`: `OP_CARRIER` is null or zero-length string.
3. `QUARANTINE_NULL_ORIGIN_DEST`: `ORIGIN` or `DEST` is null, zero-length, or invalid length ($\neq 3$).
4. `QUARANTINE_INVALID_FL_NUM`: `OP_CARRIER_FL_NUM` is null, non-numeric, or $\le 0$ (enforcing provisional rule `G3-COND-A`).

### 3.2. Rejection Reason Codes
1. `REJECTED_PARSE_ERROR`: PySpark CSV parser failed to tokenize physical line due to malformed quotes, delimiter corruptions, or encoding errors.
2. `REJECTED_TOKEN_COUNT_MISMATCH`: Line produced fewer or more tokens than the 34 required canonical fields.

---

## 4. OUTPUT RECONCILIATION & ACCOUNTING AUDIT

During pre-publication verification, the `RunManifest` automatically evaluates the following assertion:
```python
assert raw_rows == (accepted_rows + quarantined_rows + rejected_rows), (
    f"DC-11 Accounting Violation: raw={raw_rows} != "
    f"accepted({accepted_rows}) + quarantined({quarantined_rows}) + rejected({rejected_rows})"
)
```
If this assertion fails, the publication process triggers an immediate fail-fast abort, preventing corrupt or unaccounted data from reaching `data/curated/`.

---

## 5. CLASSIFICATION DESIGN VERDICT

The classification and accounting design strictly adheres to DC-11, DC-12, G3-COND-A, FP-DEC-010, and FP-DEC-017.

**CLASSIFICATION DESIGN VERDICT: CANONICALLY COMPLIANT & APPROVED.**
