# T008 FULL PROVISIONAL POLICY IMPACT REVIEW (G3-COND-A)

**Document ID:** `T008_FULL_PROVISIONAL_POLICY_IMPACT_REVIEW`  
**Parent Task:** `T-008 — Data Quality, Disjoint Row Accounting & Quarantine Engine`  
**Parent Gate:** `G4`  
**Classification:** `PROVISIONAL_POLICY_ANALYSIS_AND_GOVERNANCE_REVIEW`  
**Date:** 2026-10-18  

---

## 1. PURPOSE & GOVERNANCE CONTEXT

Under Gate G3 condition `G3-COND-A`, the rule regarding non-positive flight numbers (`OP_CARRIER_FL_NUM <= 0`) was classified as strictly **`PROVISIONAL`**.
- In the initial planning stages, non-positive flight numbers were proposed for quarantine.
- However, during the Gate G3 human review, it was recognized that BTS raw records occasionally contain flight numbers of `0` or negative integers representing non-scheduled, ferry, or test operations.
- The Project Lead directed that non-positive flight numbers must **NOT** be hard-quarantined without empirical evidence of their real-world BTS distribution.
- Therefore, in canonical production configuration, `OP_CARRIER_FL_NUM <= 0` remains **`ACCEPTED`** (flagged as `PROVISIONAL_FLIGHT_NUM_NON_POSITIVE_G3_COND_A`).

---

## 2. SYNTHETIC IMPACT SIMULATION & PROFILER

The `ProvisionalPolicyProfiler` was implemented in `flight_pipeline.quality.policy` to quantify the impact of this policy without mutating records.

### 2.1. Profiler Capabilities
- Measures total records, non-positive count, zero count, and negative count.
- Groups affected flights by carrier code (`OP_CARRIER`).
- Simulates comparative outcomes:
  - **Canonical Policy (G3-COND-A):** All records with valid identity anchors remain `ACCEPTED`.
  - **Alternative Hard Policy:** Non-positive flight numbers are diverted to `QUARANTINED`.

### 2.2. Synthetic Benchmark Results (from `test_pol_04`)
- Evaluated on a 5-record synthetic cohort containing 1 zero (`0.0`), 1 negative (`-5.0`), and 3 positive flights across carriers AA, DL, and UA:
  - Total records: `5`
  - Non-positive count: `2` (Rate: `40.0%`)
  - Zero count: `1`
  - Negative count: `1`
  - Carrier breakdown: `{"AA": 1, "DL": 1}`
  - Simulated accepted under Canonical Policy: `5`
  - Simulated quarantined under Hard Policy: `2`

---

## 3. STRICT REAL DATA BOUNDARY & G5 OBLIGATION

1. **No Fake Distribution Claims:** The Agent has NOT read the 54.7M raw CSV rows to compute a real distribution. Any claim of having surveyed real 9-year flight number distribution in G4 is strictly forbidden.
2. **Current Governance Status:**
   ```
   status = PROVISIONAL_POLICY_PENDING_REAL_DATA_VALIDATION
   ```
3. **Gate G5 Real-Data Obligation:**
   - In Gate G5 (`T-010` / `T-011`), the bounded real-data smoke run on 2016 data will profile real-world frequency of `OP_CARRIER_FL_NUM <= 0`.
   - The results will be submitted to the Project Lead for an official binding policy decision before Gate G6 full execution.
