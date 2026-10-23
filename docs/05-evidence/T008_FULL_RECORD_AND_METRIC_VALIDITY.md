# T008 FULL RECORD VALIDITY VS METRIC VALIDITY SPECIFICATION

**Document ID:** `T008_FULL_RECORD_AND_METRIC_VALIDITY`  
**Parent Task:** `T-008 — Data Quality, Disjoint Row Accounting & Quarantine Engine`  
**Parent Gate:** `G4`  
**Classification:** `DATA_CONTRACT_AND_ACCOUNTING_ARCHITECTURE`  
**Date:** 2026-10-18  

---

## 1. THE DC-11 AND DC-12 ARCHITECTURAL SEPARATION

A foundational invariant of the US Flight Performance Analysis pipeline is the strict boundary between:
1. **Record-Level Validity (`DC-11`):** Governs whether a row in the raw CSV constitutes an accepted flight event, a quarantined malformed record, or an unrecoverable parser rejection.
2. **Metric-Level Validity (`DC-12`):** Governs whether a specific numeric performance measure (e.g., `ARR_DELAY`, `DEP_DELAY`, `TAXI_OUT`) within an accepted flight record is valid for aggregation in a given KPI denominator.

```
                         +-----------------------------------+
                         |          RAW CSV RECORD           |
                         +-----------------------------------+
                                           |
                                [Parser Syntax Check]
                                 /               \
                       Corrupt  /                 \ Syntax Valid
                               v                   v
                    +--------------+      [Core Identity Anchors]
                    |   REJECTED   |       /                   \
                    +--------------+  Missing/Invalid       Anchors Valid
                                             v                   v
                                    +-----------------+  +-----------------+
                                    |   QUARANTINED   |  |    ACCEPTED     |
                                    +-----------------+  +-----------------+
                                                                  |
                                                       [DC-12 Submetric Checks]
                                                       /                      \
                                            Metric Valid                  Metric Invalid / NULL
                                                 v                                  v
                                       (Included in KPI Denom)            (Excluded from KPI Denom)
```

---

## 2. RECORD VALIDITY DISPOSITION (DC-11)

Every physical row $i \in \{1, \dots, N_{raw}\}$ is assigned to exactly one state:
- **`REJECTED`:** Parser-level syntax corruption (e.g., short row, unclosed quotes, token count mismatch). Captured in `_corrupt_record`.
- **`QUARANTINED`:** 34-column syntactically valid rows that fail mandatory core entity identity anchors:
  - Missing `OP_CARRIER` (`MISSING_CARRIER_CORE_ANCHOR`)
  - Missing `ORIGIN` or `DEST` (`MISSING_AIRPORT_CORE_ANCHOR`)
  - Malformed or impossible `FL_DATE` (`INVALID_FL_DATE_CORE_ANCHOR`)
  - Mismatch between `FL_DATE` year and `_source_year` (`SOURCE_YEAR_DATE_MISMATCH`)
  - Missing or non-numeric `OP_CARRIER_FL_NUM` (`INVALID_FLIGHT_NUM_CORE_ANCHOR`)
- **`ACCEPTED`:** Valid flight events satisfying all core identity anchors.

---

## 3. METRIC VALIDITY DISPOSITION (DC-12)

Within the set of `ACCEPTED` records, individual measures may be missing (`null`), non-numeric (`"NA"`), or outside valid domains without invalidating the record:
- **Preservation of Flight Event:** If `DEP_DELAY` is null or invalid, the flight is **NOT** quarantined. It remains an accepted flight event.
- **KPI Denominator Safety:** For any KPI analyzing departure delays (e.g., KPI-04, KPI-05), only records where `is_valid_dep_delay == True` enter the denominator cohort.
- **Signed Negative Delays:** Early departures and early arrivals have negative delay values (e.g., `-15.0`). These are strictly preserved and validated as finite numeric measures.
- **Weather Columns:** Absence or null values in the 6 weather columns (`O_TEMP..D_WSPD`) never quarantine or reject a valid flight event (conforming to `FP-DEC-017` CONDITIONAL_NO_GO).

---

## 4. MATHEMATICAL PROPERTIES & TESTS

1. **Disjointness:** $N_{raw} = N_{acc} + N_{quar} + N_{rej}$ and $Acc \cap Quar = \emptyset, Acc \cap Rej = \emptyset, Quar \cap Rej = \emptyset$.
2. **Metric Subsetting:** For each metric $M$, $\{r \in Acc \mid \text{valid}(r.M)\} \subseteq Acc$, therefore:
   $$\text{count\_metric\_valid}_M \le \text{count\_records}_{Acc}$$
3. **Verified by Unit Tests:**
   - `test_qual_08_metric_invalidity_preserves_accepted_record`
   - `test_qual_09_signed_negative_delay_preserved`
   - `test_qual_10_duration_metrics_domain_boundaries`
   - `test_acct_04_metric_valid_bound_enforced`
   - `test_acct_05_zero_denominator_handled_cleanly`
