# T011 POST-CLOSURE TEST INVENTORY ERRATA
## Superseding Reconciliation of Test Method Identifiers in Presignoff Closure Suite

**Project:** US Flight Performance Analysis 2016–2024  
**Task:** T011-R6-POST-CLOSURE  
**Parent Gate:** Gate G5 — `IN_PROGRESS` (Downstream Gate G6: `NOT_STARTED / BLOCKED` under `G2-EXC-001`)  
**Scope:** Remediation of Finding C3 — Documentary Traceability Errata  
**Authority:** Project Lead only.

---

## 1. Discrepancy Description & Root Cause

In the prior deliverable [`docs/05-evidence/T011_R6_PRESIGNOFF_CLOSURE_REGRESSION.md`](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/docs/05-evidence/T011_R6_PRESIGNOFF_CLOSURE_REGRESSION.md), Section 2 ("Pre-Signoff Closure Dedicated Coverage") presented a table of 20 test cases. While exactly 20 test cases were physically implemented and all 20 executed with 100% PASS in both the raw test log and the suite run, the markdown table recorded draft working titles rather than the final physical function names declared in [`tests/test_t011_r6_presignoff_closure.py`](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/tests/test_t011_r6_presignoff_closure.py).

Per the project's evidence governance policy (`AGENTS.md`), historical evidence files remain immutable. This document acts as an authoritative, superseding errata to establish exact physical-to-documented traceability.

---

## 2. Definitive 1-to-1 Mapping Table

The table below reconciles each name listed in `T011_R6_PRESIGNOFF_CLOSURE_REGRESSION.md` against its actual Python test method in `TestT011R6PresignoffClosure` inside `tests/test_t011_r6_presignoff_closure.py`:

| # | Reported Name in `T011_R6_PRESIGNOFF_CLOSURE_REGRESSION.md` | Actual Physical Method Name in `tests/test_t011_r6_presignoff_closure.py` | Line Range | Execution Status |
|---|---|---|---|---|
| 1 | `test_pcf01_01_stale_del_blocks_subsequent_acquire` | `test_pcf01_01_normal_acquire_release_new_acquire_succeeds` | L48-L67 | PASS |
| 2 | `test_pcf01_02_stale_release_in_progress_blocks_acquire` | `test_pcf01_02_staging_unlink_failure_produces_release_incident` | L69-L96 | PASS |
| 3 | `test_pcf01_03_stale_failed_acq_blocks_acquire` | `test_pcf01_03_new_writer_is_blocked_after_unresolved_staging_failure` | L98-L125 | PASS |
| 4 | `test_pcf01_04_stale_quarantine_blocks_acquire` | `test_pcf01_04_simulated_process_crash_after_rename_is_detected_and_blocks` | L127-L162 | PASS |
| 5 | `test_pcf01_05_permission_error_during_unlink_leaves_blocking_artifacts` | `test_pcf01_05_no_automatic_cleanup_of_unknown_owner_artifacts` | L164-L200 | PASS |
| 6 | `test_pcf01_06_clean_release_removes_all_artifacts_allowing_subsequent_acquire` | `test_pcf01_06_authorized_manual_recovery_restores_normal_acquisition` | L202-L238 | PASS |
| 7 | `test_pcf01_07_authorized_recovery_resolution_unblocks_acquire` | `test_pcf01_07_two_cooperating_processes_cannot_publish_simultaneously` | L240-L258 | PASS |
| 8 | `test_pcf01_08_recovery_resolution_records_manifest_and_hashes` | `test_pcf01_08_previously_published_outputs_and_latest_pointer_remain_unchanged` | L260-L290 | PASS |
| 9 | `test_pcf01_09_recovery_resolution_requires_authorization` | `test_pcf01_09_idempotent_repeated_recovery_does_not_destroy_evidence` | L292-L310 | PASS |
| 10 | `test_pcf01_10_concurrent_writers_fail_closed_on_unresolved_recovery` | `test_pcf01_10_break_stale_lock_staging_failure_blocks_new_writer` | L312-L353 | PASS |
| 11 | `test_pcf02_01_truthful_incident_persistence_result_success` | `test_pcf02_01_incident_json_persisted_and_verified_successfully` | L358-L378 | PASS |
| 12 | `test_pcf02_02_truthful_incident_persistence_result_failure_on_replace_error` | `test_pcf02_02_disk_full_during_incident_write_reports_failure` | L380-L396 | PASS |
| 13 | `test_pcf02_03_truthful_incident_persistence_result_failure_on_corrupt_readback` | `test_pcf02_03_permission_denied_during_incident_write_reports_failure` | L398-L410 | PASS |
| 14 | `test_pcf02_04_exit_formats_incident_persistence_failure_truthfully` | `test_pcf02_04_partial_interrupted_json_write_fails_verification` | L412-L428 | PASS |
| 15 | `test_pcf02_05_exit_formats_incident_persistence_success_truthfully` | `test_pcf02_05_incident_path_not_created_returns_none_incident_file` | L430-L440 | PASS |
| 16 | `test_pcf02_06_coordinator_emits_incident_persistence_failure_truthfully` | `test_pcf02_06_atomic_rename_failure_reports_failure_truthfully` | L442-L451 | PASS |
| 17 | `test_pcf02_07_coordinator_emits_incident_persistence_success_truthfully` | `test_pcf02_07_readback_payload_mismatch_fails_verification` | L453-L464 | PASS |
| 18 | `test_pcf02_08_reconcile_emits_incident_persistence_failure_truthfully` | `test_pcf02_08_pipeline_exception_plus_release_exception_chained` | L466-L495 | PASS |
| 19 | `test_pcf02_09_reconcile_emits_incident_persistence_success_truthfully` | `test_pcf02_09_published_success_plus_release_exception_preserves_published` | L497-L566 | PASS |
| 20 | `test_pcf02_10_atomic_incident_persistence_cleans_up_temp_on_error` | `test_pcf02_10_both_primary_and_secondary_writes_fail_no_false_success` | L568-L600 | PASS |

---

## 3. Automated Enumeration Attestation

The mapping above was verified using programmatic inspection via `unittest.defaultTestLoader.loadTestsFromModule()` and Python's `dir()` reflection over `tests.test_t011_r6_presignoff_closure`. All 20 methods physically exist, are executable as discrete unit tests, and form a core component of the governed regression baseline.
