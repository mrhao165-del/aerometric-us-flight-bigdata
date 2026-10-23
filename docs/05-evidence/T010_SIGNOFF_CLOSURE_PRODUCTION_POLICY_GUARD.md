# T010 SIGNOFF CLOSURE: PRODUCTION POLICY HARD GUARD AT ENTRYPOINT

**Document ID:** `T010_SIGNOFF_CLOSURE_PRODUCTION_POLICY_GUARD`  
**Parent Task:** `MASTER-T010-SIGNOFF-CLOSURE`  
**Parent Gate:** `G5 — Bounded Real-Data Smoke & Resource Benchmark`  
**Role:** Principal Big Data Architect, Production Safety Engineer & QA Reviewer  
**Audit Date:** 2026-10-18  

---

## 1. Governance Mandate & Defect Remediation (FIX-04)

Under Gate G3 / G4 governance decisions:
- **`G3-COND-A`:** Non-positive flight numbers (`OP_CARRIER_FL_NUM <= 0`) are classified as `ACCEPTED` with an anomaly flag. Escalating this rule to hard record quarantine is strictly a provisional proposal requiring empirical validation at Gate G5.
- **`FP-DEC-017`:** Weather analysis is designated `CONDITIONAL_NO_GO`. Weather column nulls or absence must never quarantine or reject valid flight events.
- **`DC-11 / DC-12`:** Disjoint row accounting and metric validity bound enforcement must remain active at all times.

### Defect Identified
Previously, `assert_production_policy_compliance()` was defined exclusively within the test suite `tests/test_t010_policy_guards.py`. The real-data runner did not actively enforce this guard at the process entrypoint prior to reading CSV data.

### Remediation Implemented
1. **Production Code Relocation:** Migrated `assert_production_policy_compliance()` directly into `src/flight_pipeline/quality/policy.py` and exported it via `src/flight_pipeline/quality/__init__.py`.
2. **Runner Entrypoint Invocation:** In `tools/qa/run_t010_real_data_smoke.py`, Phase 0 executes `assert_production_policy_compliance(production_policy)` before reading any CSV file, initializing Spark, or creating staging output paths.
3. **Simulation Isolation:** Any configuration with `allow_unapproved_policies=True` or `quarantine_non_positive_flight_num=True` immediately triggers `PolicyViolationError` and halts execution.

---

## 2. Technical Implementation Architecture

### 2.1. Production Guard Implementation (`policy.py`)
```python
def assert_production_policy_compliance(policy: QualityPolicyConfig) -> None:
    """
    Production Safety Hard Guard (G3-COND-A, FP-DEC-017).
    Enforces that canonical production and bounded real-data smoke execution strictly
    reject simulation parameters and unapproved policy deviations at the entrypoint.
    """
    if policy.allow_unapproved_policies:
        raise PolicyViolationError(
            "PRODUCTION_GUARD_VIOLATION: allow_unapproved_policies=True is strictly prohibited in "
            "canonical production and real-data execution. It is reserved solely for offline simulations."
        )
    if policy.quarantine_non_positive_flight_num:
        raise PolicyViolationError(
            "PRODUCTION_GUARD_VIOLATION: Hard quarantine for OP_CARRIER_FL_NUM <= 0 is prohibited "
            "under G3-COND-A in production mode."
        )
    if not policy.allow_weather_nulls:
        raise PolicyViolationError(
            "PRODUCTION_GUARD_VIOLATION: Disallowing weather nulls violates FP-DEC-017."
        )
    if not policy.strict_record_accounting:
        raise PolicyViolationError(
            "PRODUCTION_GUARD_VIOLATION: strict_record_accounting must be True under DC-11."
        )
    if not policy.strict_metric_accounting:
        raise PolicyViolationError(
            "PRODUCTION_GUARD_VIOLATION: strict_metric_accounting must be True under DC-12."
        )
```

### 2.2. Runner Entrypoint Execution Flow
In `tools/qa/run_t010_real_data_smoke.py`:
```python
def main():
    ...
    # --- PHASE 0: PRODUCTION POLICY HARD GUARDS AT ENTRYPOINT (G3-COND-A) ---
    production_policy = QualityPolicyConfig()
    assert_production_policy_compliance(production_policy)
    ...
```
If any parameter violates canonical invariants, execution aborts with exit code 1 before any filesystem read or Spark initialization occurs.

---

## 3. Test Coverage & Fail-Closed Verification

The test suite `tests/test_t010_policy_guards.py` validates fail-closed behavior across all five configuration dimensions:

| Test Case | Invariant Tested | Injected Configuration | Expected & Observed Result |
| :--- | :--- | :--- | :---: |
| `test_default_production_policy_guards` | Canonical Production | All default parameters | **PASS (Compliant)** |
| `test_fail_closed_on_unapproved_quarantine_flight_num` | `G3-COND-A` Guard | `quarantine_non_positive_flight_num=True` without simulation gate | **RAISES `PolicyViolationError`** |
| `test_fail_closed_on_unapproved_disallow_weather_nulls` | `FP-DEC-017` Guard | `allow_weather_nulls=False` without simulation gate | **RAISES `PolicyViolationError`** |
| `test_production_guard_rejects_simulation_flag` | Simulation Flag | `allow_unapproved_policies=True` | **RAISES `PolicyViolationError`** |
| `test_production_guard_rejects_relaxed_accounting` | `DC-11` Accounting | `strict_record_accounting=False` | **RAISES `PolicyViolationError`** |
| `test_production_guard_rejects_all_individual_violations` | Exhaustive Isolation | Each of the 5 flags flipped individually | **5/5 RAISE `PolicyViolationError`** |
| `test_canonical_production_preserves_non_positive_flight_num` | `G3-COND-A` Acceptance | Flight num = 0.0, -10.0 | **ACCEPTED (0 Quarantined)** |
| `test_canonical_production_allows_weather_nulls` | `FP-DEC-017` Acceptance | All 6 weather fields = `None` | **ACCEPTED (0 Quarantined)** |

All tests execute cleanly and pass 100% in `tests/test_t010_policy_guards.py`.
