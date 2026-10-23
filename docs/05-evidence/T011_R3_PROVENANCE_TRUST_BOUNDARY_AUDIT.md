# T011-R3 Provenance Trust Boundary & Anti-Self-Approval Audit

**Project:** US Flight Performance Analysis 2016–2024  
**Task:** T-011 R3 — Provenance Trust Boundary, Numeric Integrity, Lock Recovery & Evidence Correction  
**Parent Gate:** G5 — IN_PROGRESS  
**Component:** BTS TranStats Reconciler (`src/flight_pipeline/kpi/bts_reconciler.py`, `tools/qa/run_ts018_bts_parity.py`)  
**Audit Finding Addressed:** R3-F01 (CRITICAL — False authentic BTS PASS through self-approved metadata / hash overwrite)  
**Date:** 2026-10-19  
**Status:** COMPLETE / FAIL-CLOSED IMMUTABILITY & TRUST BOUNDARY ENFORCED  

---

## 1. Executive Summary & Defect Remediation

During the independent technical audit of package `T011_R2_REVIEW_PACKAGE.zip`, finding **R3-F01** uncovered a critical security and governance vulnerability in the BTS parity verification subsystem:

1. **Hash Overwrite Vulnerability:** In `tools/qa/run_ts018_bts_parity.py` (line 124 of R2), the execution harness contained:
   ```python
   prov_meta.sha256_hash = bts_sha256
   ```
   This silently overwrote the declared cryptographic identity from the provenance record with the actual hash of whatever candidate CSV was provided. Consequently, any fabricated CSV paired with an unverified JSON metadata file would compare its own hash against itself, defeating the entire purpose of SHA-256 verification.
2. **Self-Approved Provenance Escalation:** If a local companion metadata file asserted `project_lead_approval_status = "APPROVED_BY_PROJECT_LEAD"`, the reconciler automatically conferred `TS018_PASS_AUTHENTIC_PARITY_ESTABLISHED`. This allowed automated code or local JSON fixtures to bypass the Project Lead's exclusive human authority, violating the non-delegable signoff governance principle of `AGENTS.md`.

In T011-R3, this defect has been completely eliminated. Declared SHA-256 hashes are immutable, actual hashes are strictly verified against declared hashes, and automated execution is architecturally prohibited from awarding official human acceptance.

---

## 2. Segregation of the 5 Governance Dimensions

To ensure absolute clarity and prevent conflation between physical existence, cryptographic integrity, metadata validity, numerical parity, and governance authority, R3 enforces five strictly segregated dimensions:

| Dimension | Scope | Verification Rule | Invariant / Governance Role |
| :--- | :--- | :--- | :--- |
| **1. File Presence (`file_present`)** | Physical filesystem existence | `os.path.isfile(csv_path)` | Binary check; does not imply validity or authenticity. |
| **2. Checksum Match (`checksum_match`)** | Cryptographic integrity | `declared_sha256.lower() == actual_sha256.lower()` | Overwrite strictly prohibited; both hashes must be 64-char hex. |
| **3. Provenance Verification (`source_provenance_verified`)** | Institutional source attestation | `BtsProvenanceValidator.validate_provenance()` | Requires external flag, declared SHA match, and valid approval record reference. |
| **4. Numerical Parity (`numerical_parity_verified`)** | Mathematical alignment | Exact / rounding agreement across all 7 CORE measures | Requires 0 mismatches, 0 unmatched records, 0 ambiguous keys, 0 invalid keys, and positive samples for all 7 measures. |
| **5. Human Signoff (`human_accepted`)** | Official human authority | Project Lead signature in `docs/04-execution/` | **NEVER** automated. Set to `False` in all runtime code. |

---

## 3. Production Source Hardening

### 3.1 Elimination of Hash Overwrite (`tools/qa/run_ts018_bts_parity.py`)

The hash mutation statement was removed. The harness now preserves the declared metadata hash unmodified and passes the independently computed `bts_sha256` directly to `reconciler.reconcile()`:

```python
# R3 Hardened Invariant: Never mutate declared SHA-256 hash.
summary, results = reconciler.reconcile(
    dataset_records=target_records,
    bts_records=bts_records,
    provenance_metadata=prov_meta,
    actual_bts_sha256=bts_sha256,
    is_authentic_bts_data=(prov_meta is not None),
)
```

### 3.2 Immutability and Strict Hash Validation (`src/flight_pipeline/kpi/bts_reconciler.py`)

In `BtsProvenanceValidator`:
- Rejects empty, whitespace, or malformed hashes (must be exactly 64 characters hex).
- Strictly compares `provenance.sha256_hash.strip().lower() != actual_sha256.strip().lower()`.
- Validates that `approval_record_ref` is non-empty and non-whitespace.

### 3.3 Candidate Parity vs. Official Human Acceptance

In `BtsTranStatsReconciler.reconcile()`:
- `summary.human_accepted` is hardcoded to `False` in automated execution.
- If verified provenance format and complete numerical parity are achieved against an external candidate file, the reconciler emits:
  `summary.reconciliation_verdict = "TS018_CANDIDATE_PARITY_VERIFIED_HUMAN_APPROVAL_PENDING"`
- The verdict `TS018_PASS_AUTHENTIC_PARITY_ESTABLISHED` is reserved exclusively for post-human-signoff record-keeping and is **never** emitted by autonomous scripts.

---

## 4. Verification Evidence & Counterexample Guards

Permanent regression suite `tests/test_t011_r3_counterexamples.py` (`TestT011R3ProvenanceTrustBoundary`) proves that 12 unapproved scenarios fail closed and cannot obtain authentic status:

1. `test_r3_f01_scenario_01_no_provenance_with_authentic_flag`: PASS (verdict remains synthetic pending).
2. `test_r3_f01_scenario_02_not_external_reference`: PASS (`PROVENANCE_NOT_EXTERNAL`).
3. `test_r3_f01_scenario_03_empty_sha256`: PASS (`PROVENANCE_MALFORMED_HASH`).
4. `test_r3_f01_scenario_04_short_sha256`: PASS (`PROVENANCE_MALFORMED_HASH`).
5. `test_r3_f01_scenario_05_hash_mismatch_with_actual`: PASS (`PROVENANCE_HASH_MISMATCH`).
6. `test_r3_f01_scenario_06_unapproved_status_pending`: PASS (`PROVENANCE_UNAPPROVED`).
7. `test_r3_f01_scenario_07_unapproved_status_self_approved`: PASS (`PROVENANCE_UNAPPROVED`).
8. `test_r3_f01_scenario_08_unapproved_status_agent_approved`: PASS (`PROVENANCE_UNAPPROVED`).
9. `test_r3_f01_scenario_09_missing_approval_record_ref_empty`: PASS (`PROVENANCE_MISSING_APPROVAL_REF`).
10. `test_r3_f01_scenario_10_missing_approval_record_ref_whitespace`: PASS (`PROVENANCE_MISSING_APPROVAL_REF`).
11. `test_r3_f01_scenario_11_candidate_parity_requires_human_signoff`: PASS (`TS018_CANDIDATE_PARITY_VERIFIED_HUMAN_APPROVAL_PENDING`, `human_accepted=False`).
12. `test_r3_f01_scenario_12_no_hash_overwrite_in_validator`: PASS (declared hash remains unmodified).

---

## 5. Conclusion

Finding **R3-F01** is **RESOLVED / CLOSED**. The cryptographic identity of external datasets cannot be overwritten or self-certified, and TS-018 authentic BTS parity remains strictly `PENDING` until explicit human signoff by the Project Lead.
