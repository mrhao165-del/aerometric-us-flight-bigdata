# T010_FULL_SAFETY_GUARD_VERIFICATION.md — Production Policy Safety Hard Guards (G3-COND-A)

**Gate:** G5  
**Task:** T-010 — Bounded Real-Data Smoke & Resource Benchmark  
**Author:** Principal Apache Spark Engineer & Data Quality Architect  
**Execution Timestamp:** 2026-10-18T11:07:20+00:00 (2026-10-18T18:07:20+07:00)  
**Status:** PASS (CONTROLLED)  

---

## 1. Governance Policy Framework & Context

Task T-010 operates directly under canonical production safety guards established by Gate G3, Gate G4, and Project Lead directives:

1. **G3-COND-A (Provisional Flight Number Policy):**
   - In production execution, non-positive flight numbers (`OP_CARRIER_FL_NUM <= 0`) must remain **ACCEPTED** with provisional anomaly flag `PROVISIONAL_FLIGHT_NUM_NON_POSITIVE_G3_COND_A`.
   - Hard quarantine for non-positive flight numbers (`quarantine_non_positive_flight_num = True`) is an unapproved policy (OPTY-01 rejected by Project Lead) and is strictly prohibited in canonical execution.
2. **FP-DEC-017 (Weather Optionality / CONDITIONAL_NO_GO):**
   - Weather columns (`O_TEMP..D_WSPD`) are optional.
   - Nulls or missing values in weather columns must NEVER cause a record to be quarantined or rejected.
3. **DC-11 & DC-12 Strict Accounting:**
   - Strict 3-state disjoint row accounting (`N_raw == N_accepted + N_quarantined + N_rejected`) and strict metric valid accounting must be enforced at all times.
4. **Fail-Closed Simulation Guard:**
   - Any attempt to execute production code with simulation flags (`allow_unapproved_policies = True`) must fail closed immediately.

---

## 2. Hard Guard Specification: `QualityPolicyConfig`

The production configuration in [`flight_pipeline.quality.policy.QualityPolicyConfig`](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/src/flight_pipeline/quality/policy.py#L16-L65) defines and enforces these invariants:

```python
@dataclass(frozen=True)
class QualityPolicyConfig:
    # Runtime execution guards (Canonical Production Invariants)
    quarantine_non_positive_flight_num: bool = False
    allow_weather_nulls: bool = True
    strict_record_accounting: bool = True
    strict_metric_accounting: bool = True
    
    # Simulation safety gate
    allow_unapproved_policies: bool = False
```

### Fail-Closed Validation Logic:
```python
def validate(self) -> None:
    if self.quarantine_non_positive_flight_num and not self.allow_unapproved_policies:
        raise PolicyViolationError(
            "GOVERNANCE_VIOLATION: Hard quarantine for OP_CARRIER_FL_NUM <= 0 is strictly "
            "PROVISIONAL under G3-COND-A. Escalation to hard quarantine requires explicit human "
            "signoff after real BTS data validation at Gate G5. Set allow_unapproved_policies=True "
            "only for offline impact simulations."
        )
    if not self.allow_weather_nulls and not self.allow_unapproved_policies:
        raise PolicyViolationError(
            "GOVERNANCE_VIOLATION: Disallowing weather nulls violates FP-DEC-017 (CONDITIONAL_NO_GO). "
            "Weather absence must not quarantine or reject valid CORE flights."
        )
```

---

## 3. Dedicated Verification Suite: `test_t010_policy_guards.py`

A dedicated unit and regression test suite was implemented in [`tests/test_t010_policy_guards.py`](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/tests/test_t010_policy_guards.py) to prove that unapproved policies fail closed and production safety invariants are enforced.

### Test Execution Results (8/8 PASS in 28.32s):

| Test Case | Description | Result |
| :--- | :--- | :--- |
| `test_default_production_policy_guards` | Verifies default config enforces all canonical guards without mutation | **PASS** |
| `test_fail_closed_on_unapproved_quarantine_flight_num` | Setting `quarantine_non_positive_flight_num=True` raises `PolicyViolationError` (G3-COND-A) | **PASS** |
| `test_fail_closed_on_unapproved_disallow_weather_nulls` | Setting `allow_weather_nulls=False` raises `PolicyViolationError` (FP-DEC-017) | **PASS** |
| `test_production_guard_rejects_simulation_flag` | `assert_production_policy_compliance` strictly rejects `allow_unapproved_policies=True` | **PASS** |
| `test_production_guard_rejects_relaxed_accounting` | Rejecting `strict_record_accounting=False` or `strict_metric_accounting=False` | **PASS** |
| `test_canonical_production_preserves_non_positive_flight_num` | Evaluates rows with `FL_NUM <= 0.0` in Spark; verifies status remains `ACCEPTED` | **PASS** |
| `test_canonical_production_allows_weather_nulls` | Evaluates rows with null weather in Spark; verifies status remains `ACCEPTED` | **PASS** |
| `test_strict_accounting_rejects_imbalance` | Row accounting count mismatch triggers `AccountingBalanceError` (DC-11) | **PASS** |

---

## 4. Production Hard Guard Conclusion

All canonical safety guards have been proven robust and active. Attempts to activate unapproved policies fail closed with explicit governance error messages. Canonical production execution cleanly preserves non-positive flight numbers under G3-COND-A and permits weather nulls under FP-DEC-017 without compromising record validity.
