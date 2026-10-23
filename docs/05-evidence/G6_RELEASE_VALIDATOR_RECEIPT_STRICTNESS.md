# G6_RELEASE_VALIDATOR_RECEIPT_STRICTNESS.md
## Technical Specification and Verification Audit for ExecutionReceipt Strictness

**Project:** US Flight Performance Analysis 2016–2024  
**Date:** 2026-10-21  
**Gate Status:** Gate G5 = IN_PROGRESS (TECHNICALLY READY), Gate G6 = NOT_STARTED / BLOCKED  
**Author:** Senior PySpark Reliability Engineer & Independent QA Auditor  
**Scope:** `ExecutionReceipt` contract enforcement in `tools/qa/verify_multiyear_snapshot.py`

---

## 1. Governance & Contract Background

Under `ARCHITECTURE.md` Section 2 and `T006_FINAL_CORRECTIONS_ADDENDUM.md` Section 4, the `ExecutionReceipt` is an independent sidecar artifact written outside the immutable versioned Parquet payload. It resolves the manifest self-reference paradox by recording the finalized manifest's exact disk size and SHA-256 hash alongside the publication outcome.

Prior to this hardening, `verify_multiyear_snapshot.py` tolerated receipts missing critical fields (Finding R04) or allowed omitting receipts altogether by defaulting `require_execution_receipt=False` (Finding R01).

---

## 2. Canonical Contract Specification

In `src/flight_pipeline/ingestion/coordinator.py`, the dataclass `ExecutionReceipt` is defined as:

```python
@dataclass
class ExecutionReceipt:
    run_id: str
    task_id: str
    pipeline_state: str
    publication_status: str
    published_path: Optional[str]
    pointer_value: Optional[str]
    previous_pointer: Optional[str]
    manifest_path: str
    manifest_bytes: int
    manifest_sha256: str
    row_accounting: Dict[str, Any]
    per_year_accounting: Dict[str, Any] = field(default_factory=dict)
    forensic_quarantine_dir: Optional[str] = None
    upstream_identity_status: str = UPSTREAM_IDENTITY_STATUS_UNVERIFIED
    weather_branch_status: str = "CONDITIONAL_NO_GO"
    core_measures_unit_status: str = "G2-EXC-001_PROVISIONAL"
    or05_coverage_warning: Optional[str] = None
    completed_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
```

---

## 3. Strict Verification Engine Implementation (R01 & R04)

`tools/qa/verify_multiyear_snapshot.py` now enforces deep schema and cryptographic reconciliation across all 8 core receipt fields:

### Field 1: `run_id`
- Must be a non-empty string.
- Must exactly match `selected_run_id` for that survey year.
- Violation triggers `RECEIPT_FIELD_MISSING` or `RECEIPT_RUN_ID_MISMATCH`.

### Field 2: `task_id`
- Must be a non-empty string (e.g. `"T-012"`).
- Missing, empty, or non-string values trigger `RECEIPT_FIELD_MISSING`.

### Field 3: `pipeline_state` & `publication_status`
- Both fields must be present and strictly equal `"PUBLISHED"`.
- Any other status (e.g., `"FAILED"`, `"ABORTED"`, `"IN_PROGRESS"`) triggers `RECEIPT_STATUS_NOT_PUBLISHED`. Missing fields trigger `RECEIPT_FIELD_MISSING`.

### Field 4: `published_path`
- Must be a valid string resolving 1:1 to `physical_dir.resolve()`.
- Supports canonical absolute paths or paths formatted relative to `base_data_dir`.
- Mismatch triggers `RECEIPT_PUBLISHED_PATH_MISMATCH`.

### Field 5: `manifest_path`
- Must be a valid string resolving 1:1 to `manifest_p.resolve()`.
- Mismatch triggers `RECEIPT_MANIFEST_PATH_MISMATCH`.

### Field 6: `manifest_bytes`
- Must be a non-negative integer (`isinstance(v, int) and not isinstance(v, bool) and v >= 0`).
- Must exactly equal the disk size of `run_manifest.json` (`manifest_p.stat().st_size`).
- Omission triggers `RECEIPT_FIELD_MISSING`; numeric discrepancy triggers `RECEIPT_MANIFEST_BYTES_MISMATCH`.

### Field 7: `manifest_sha256`
- Must be a valid 64-character hexadecimal string (`^[0-9a-fA-F]{64}$`). Placeholders (`"PENDING"`, `"UNVERIFIED"`, `""`) are rejected.
- Must exactly equal the streaming SHA-256 hash computed from `run_manifest.json`.
- Omission triggers `RECEIPT_FIELD_MISSING`; hash mismatch triggers `RECEIPT_MANIFEST_SHA256_MISMATCH`.

### Field 8: `row_accounting`
- Must be a valid dictionary containing `raw_row_count`, `accepted_row_count`, `quarantined_row_count`, and `rejected_row_count` as non-negative integers.
- Must satisfy the DC-11 conservation equation: `raw == accepted + quarantined + rejected`.
- Must match 1:1 with both manifest `row_accounting` and registry `accounting`.
- Omission triggers `RECEIPT_FIELD_MISSING`; unbalance triggers `RECEIPT_ROW_ACCOUNTING_UNBALANCED`; divergence triggers `RECEIPT_ROW_ACCOUNTING_MISMATCH`.

---

## 4. Production Release Gating (R01 Default Enforcement)

To ensure that receipts can never be bypassed during production signoff:
1. `validate_multiyear_snapshot_registry(require_execution_receipt=True)` is the system default.
2. If `require_execution_receipt=False` is passed (via diagnostic mode), the function completes structural inspection but explicitly terminates with:
   ```python
   return SnapshotValidationResult(
       valid=False,
       status="DIAGNOSTIC_PASS_RECEIPT_OMITTED_NOT_FOR_PRODUCTION",
       error_message="Registry passed structural checks, but execution receipts were not required/verified. This non-production diagnostic result cannot be certified for production release.",
       ...
   )
   ```
   This guarantees that an inadvertent or malicious setting cannot produce `VALID_SNAPSHOT_REGISTRY`.

---

## 5. Verification Test Evidence

The hardened receipt rules are verified in `tests/test_multiyear_snapshot_policy.py`:
- `test_neg_r01a_missing_execution_receipt_fails_closed`: PASS (`MISSING_EXECUTION_RECEIPT`)
- `test_neg_r01b_diagnostic_mode_missing_receipt_never_yields_production_pass`: PASS (`DIAGNOSTIC_PASS_RECEIPT_OMITTED_NOT_FOR_PRODUCTION`)
- `test_neg_r04a_receipt_missing_task_id_fails_closed`: PASS (`RECEIPT_FIELD_MISSING`)
- `test_neg_r04b_receipt_missing_manifest_bytes_fails_closed`: PASS (`RECEIPT_FIELD_MISSING`)
- `test_neg_r04c_receipt_missing_manifest_sha256_fails_closed`: PASS (`RECEIPT_FIELD_MISSING`)
- `test_neg_r04d_receipt_published_path_mismatch_fails_closed`: PASS (`RECEIPT_PUBLISHED_PATH_MISMATCH`)
- `test_neg_r04e_receipt_manifest_path_mismatch_fails_closed`: PASS (`RECEIPT_MANIFEST_PATH_MISMATCH`)
- `test_neg_r04f_receipt_row_accounting_missing_or_mismatch_fails_closed`: PASS (`RECEIPT_FIELD_MISSING` and `RECEIPT_ROW_ACCOUNTING_MISMATCH`)

---

## 6. Audit Verdict

`ExecutionReceipt` validation is now strictly closed against field omission, placeholder hash substitution, path forgery, and accounting divergence. Finding R04 and Finding R01 are fully remediated.
