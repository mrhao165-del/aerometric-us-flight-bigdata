# T008-FINAL-EXIT: Quality Policy Configuration Safety & Runtime Contract Clarity

**Deliverable ID:** `T008-DELIV-EXIT-03`  
**Task:** `MASTER-T008-FINAL-EXIT`  
**Parent Task:** `T-008 — Data Quality, Disjoint Row Accounting & Quarantine Engine`  
**Gate:** `G4`  
**Timestamp:** `2026-10-18T15:52:00+07:00`  
**Status:** `VERIFIED_PASS`  
**Authority:** `G3-COND-A`, `FP-DEC-017`, `DATA_CONTRACT.md` (DC-11, DC-12)

---

## 1. Executive Summary

During governance and architectural review of T-008, the demarcation between **Runtime Execution Guards** (canonical production invariants) and **Simulation Parameters** (offline what-if policy exploration) required formal codification and integration. Specifically:
1. `G3-COND-A` mandates that non-positive flight numbers (`OP_CARRIER_FL_NUM <= 0`) must **never** be hard-quarantined in canonical production mode; they must remain `ACCEPTED` with an anomaly flag pending real BTS validation at Gate G5.
2. `FP-DEC-017` mandates that missing weather data must **never** quarantine valid CORE flights.
3. Offline policy simulation must be strictly segregated behind the explicit safety flag `allow_unapproved_policies=True`.

This document records the design, implementation, and verification of **FIX-03**:
1. Formal demarcation in `src/flight_pipeline/quality/policy.py`.
2. Safe wiring of simulation reclassification in `src/flight_pipeline/quality/engine.py`.
3. Maintenance of exact DC-11 row accounting balance under both production and simulation modes.
4. Comprehensive test verification (`test_pol_01` through `test_pol_06`).

---

## 2. Policy Configuration Demarcation

```python
@dataclass(frozen=True)
class QualityPolicyConfig:
    """
    Configuration controlling quality validation behavior and governance invariants.
    
    RUNTIME EXECUTION GUARDS (Canonical Production Invariants):
    - quarantine_non_positive_flight_num (default False): Under G3-COND-A, non-positive flight numbers
      (OP_CARRIER_FL_NUM <= 0) must remain ACCEPTED with an anomaly flag. Escalating to hard quarantine
      is strictly provisional pending real BTS data validation at Gate G5.
    - allow_weather_nulls (default True): Under FP-DEC-017 (CONDITIONAL_NO_GO), weather column nulls or
      absence must never quarantine or reject valid CORE flights.
    - strict_record_accounting (default True): Enforces DC-11 3-state disjoint row accounting balance.
    - strict_metric_accounting (default True): Enforces DC-12 metric valid bound and zero-denominator safety.
    
    SIMULATION PARAMETER:
    - allow_unapproved_policies (default False): Safety gate required to run offline what-if policy
      simulations (e.g. simulating the volume impact of hard quarantining non-positive flight numbers).
      Must NEVER be enabled in canonical production execution.
    """
    # Runtime execution guards
    quarantine_non_positive_flight_num: bool = False
    allow_weather_nulls: bool = True
    strict_record_accounting: bool = True
    strict_metric_accounting: bool = True
    
    # Simulation safety gate
    allow_unapproved_policies: bool = False

    def __post_init__(self):
        self.validate()

    def validate(self) -> None:
        """Validate configuration against canonical governance invariants."""
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

## 3. Engine Simulation Integration

In `src/flight_pipeline/quality/engine.py`, simulation reclassification is integrated directly into the evaluation flow:

```python
        # 1b. Offline policy simulation: if quarantine_non_positive_flight_num is activated
        # (Only permitted when allow_unapproved_policies=True per G3-COND-A)
        if self.policy.quarantine_non_positive_flight_num:
            fl_num_col = "OP_CARRIER_FL_NUM"
            if fl_num_col in working_df.columns:
                fl_num_d = F.expr(f"try_cast(trim({fl_num_col}) AS double)")
                is_non_pos = (
                    fl_num_d.isNotNull()
                    & ~F.isnan(fl_num_d)
                    & ~fl_num_d.isin(float("inf"), float("-inf"))
                    & (fl_num_d <= 0.0)
                )
                working_df = (
                    working_df.withColumn(
                        REASON_COLUMN,
                        F.when(
                            (F.col(STATUS_COLUMN) == RecordStatus.ACCEPTED.value) & is_non_pos,
                            F.lit("PROVISIONAL_FLIGHT_NUM_NON_POSITIVE"),
                        ).otherwise(F.col(REASON_COLUMN)),
                    )
                    .withColumn(
                        STATUS_COLUMN,
                        F.when(
                            (F.col(STATUS_COLUMN) == RecordStatus.ACCEPTED.value) & is_non_pos,
                            F.lit(RecordStatus.QUARANTINED.value),
                        ).otherwise(F.col(STATUS_COLUMN)),
                    )
                )
```

### Key Safety Guarantees:
1. In canonical production mode (`quarantine_non_positive_flight_num=False`), the simulation block is a strict no-op, preserving 100% adherence to G3-COND-A.
2. In simulation mode (`allow_unapproved_policies=True`), non-positive flight numbers are safely quarantined, and the resulting `RowAccounting` maintains exact disjoint balance (`raw == accepted + quarantined + rejected`).

---

## 4. Test Verification Evidence

| Test Method | Focus | Result |
|---|---|:---:|
| `test_pol_01_default_policy_conforms_to_g3_cond_a` | Default policy enforces canonical invariants | PASS |
| `test_pol_02_enabling_hard_quarantine_without_override_raises_error` | Fail-closed governance protection against unauthorized escalation | PASS |
| `test_pol_03_disallowing_weather_nulls_raises_error` | Fail-closed protection of FP-DEC-017 | PASS |
| `test_pol_04_provisional_policy_profiling_simulation` | Accurate profiling of flight number zero/negative distribution | PASS |
| `test_pol_05_offline_policy_simulation_quarantines_non_positive_flight_nums` | Simulation reclassification and exact DC-11 row balance | PASS |
| `test_pol_06_canonical_production_never_hard_quarantines_non_positive` | Production mode preserves non-positive flight records as ACCEPTED | PASS |

---

## 5. Verdict

**STATUS: PASS.** FIX-03 establishes complete contract clarity, guarantees strict fail-closed governance protection against unauthorized escalation of provisional rules, and enables controlled offline policy impact simulations.
