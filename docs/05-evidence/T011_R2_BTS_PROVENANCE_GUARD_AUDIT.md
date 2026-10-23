# T011-R2 BTS Provenance Guard & Governance State Audit

**Project:** US Flight Performance Analysis 2016–2024  
**Task:** T-011 R2 — Targeted Parity Hardening and Evidence Correction  
**Parent Gate:** G5 — IN_PROGRESS  
**Component:** BTS TranStats Reconciler (`src/flight_pipeline/kpi/bts_reconciler.py`, `tools/qa/run_ts018_bts_parity.py`)  
**Audit Finding Addressed:** R2-F01 (Local unverified CSV falsely establishing authentic parity)  
**Date:** 2026-10-19  
**Status:** COMPLETE / FAIL-CLOSED INVARIANT ENFORCED  

---

## 1. Executive Summary & Defect Remediation

During independent audit review of T011-R1, finding **R2-F01** revealed that `BtsTranStatsReconciler` accepted a caller-supplied boolean argument (`is_authentic_bts_data: bool = False`). If a caller passed `is_authentic_bts_data=True`, the reconciler awarded `TS018_PASS_AUTHENTIC_PARITY_ESTABLISHED` even if the candidate file was merely a local synthetic stub (`bts_transtats_sample.csv`) with zero cryptographic or institutional provenance.

This violated the core project governance invariant (as stated in `AGENTS.md` and `PROJECT_STATE.md`):
> **Authenticity cannot be conferred by caller assertion or local file hashes alone.** Authentic external reference data requires verifiable provenance approved by the Project Lead.

In T011-R2, this vulnerability has been eliminated through the introduction of strict cryptographic provenance validation (`BtsProvenanceValidator`) and formal separation into 5 distinct lifecycle states.

---

## 2. The 5 Formal Governance States

To prevent conflation of physical presence, schema adherence, mathematical parity, and institutional authenticity, T011-R2 establishes 5 strictly segregated governance states:

| State | Scope | Verification Mechanism | Status for Local Sample |
| :--- | :--- | :--- | :--- |
| **1. `file_present`** | Physical file existence | `os.path.isfile(path)` | **TRUE** (file exists on disk) |
| **2. `schema_valid`** | Column completeness & naming | Verifies presence of all 7 CORE measure mappings without omission | **TRUE** (headers align) |
| **3. `source_provenance_verified`** | External institutional authenticity | `BtsProvenanceValidator.validate()` requiring Project Lead approval | **FALSE (PENDING)** (synthetic fixture) |
| **4. `numerical_parity_verified`** | Mathematical alignment | Exact / rounding agreement within tolerance across all 7 measures | **TRUE** (on golden records) |
| **5. `human_accepted`** | Official gate signoff | Explicit human signoff recorded in `docs/04-execution/` | **NOT_STARTED** |

---

## 3. Architecture of `BtsProvenanceValidator`

### 3.1 Metadata Contract (`BtsProvenanceMetadata`)

```python
@dataclass(frozen=True)
class BtsProvenanceMetadata:
    provenance_version: str
    source_url_or_system: str
    extraction_timestamp: str
    certified_by: str
    project_lead_approval_status: str  # Must be "APPROVED_BY_PROJECT_LEAD"
    is_external_reference: bool       # Must be True (cannot be local synthetic fixture)
    sha256_hash: str                  # Cryptographic identity of external download
    notes: Optional[str] = None
```

### 3.2 Fail-Closed Validation Rules

The validator implements three non-negotiable checks:
1. **Metadata Existence:** If `provenance_metadata is None`, `source_provenance_verified` is forced to `False`. A caller passing `is_authentic_bts_data=True` cannot bypass this rule.
2. **Project Lead Authorization:** `project_lead_approval_status` must equal `"APPROVED_BY_PROJECT_LEAD"`. Any other value (`"PENDING"`, `"DRAFT"`, `"REJECTED"`, or missing) fails validation.
3. **External Flag:** `is_external_reference` must be strictly `True`. If `is_external_reference is False` (marking a local fixture, stub, or synthetic test data), provenance validation fails.

When provenance is not verified:
- If mathematical parity passes against synthetic data, the reconciler emits:
  `reconciliation_verdict = "SYNTHETIC_RECONCILER_VERIFIED_AUTHENTIC_BTS_PENDING"`
- Under no circumstances is `TS018_PASS_AUTHENTIC_PARITY_ESTABLISHED` emitted.

---

## 4. QA Tool Integration (`tools/qa/run_ts018_bts_parity.py`)

`tools/qa/run_ts018_bts_parity.py` was updated to look for a certified companion provenance manifest (`.provenance.json` or `BTS_PROVENANCE_MANIFEST.json`).
When executing against the existing local fixture:
- It discovers that no Project Lead provenance manifest exists.
- It logs: `[PROVENANCE] Candidate file has NO approved external BTS provenance manifest.`
- It evaluates the reconciler algorithm using `provenance_meta = None, is_authentic_bts_data=False`.
- Output verdict: `SYNTHETIC_RECONCILER_VERIFIED_AUTHENTIC_BTS_PENDING` (Exit Code 0 for QA harness verification, while blocking authentic claim).

---

## 5. Verification Evidence

1. **Defect Reproduction (`tests/test_t011_r2_counterexamples.py`):**
   - Pre-fix: caller boolean granted authentic pass on local fake data (`R2-F01`).
   - Post-fix: `test_guard_r2_f01_local_file_without_provenance_fails_closed` proves that passing `is_authentic_bts_data=True` without provenance yields `SYNTHETIC_RECONCILER_VERIFIED_AUTHENTIC_BTS_PENDING`.
2. **Exhaustive Unit Tests (`tests/test_t011_ts018_bts_parity.py`):**
   - `test_14_provenance_metadata_gating_rejects_unapproved`: validates that unapproved provenance, synthetic flags, and missing metadata all fail closed.
   - `test_09_synthetic_fixture_verification_pending_bts`: validates the canonical synthetic verification path.

---

## 6. Conclusion

Finding **R2-F01** is **CLOSED / RESOLVED**. The project guarantees that TS-018 authentic BTS parity cannot be fraudulently or accidentally claimed on local synthetic data.
