# T007 DESIGN R1 CANONICAL CONFLICT REGISTER — INDEPENDENT DEFECT LOG & REMEDIATION MATRIX

**Document ID:** `DOC-T007-DESIGN-R1-01-CONFLICT-REGISTER`  
**Task ID:** `T-007` (Raw CSV Ingestion Pipeline)  
**Phase:** `DESIGN REMEDIATION (R1)`  
**Gate:** `G4` (`PLANNED / NOT_COMPLETED`)  
**Audit Timestamp:** 2026-10-17T15:15:00+07:00  
**Auditor:** Senior Big Data Architect & Independent QA Reviewer  
**Execution Mode:** `TARGETED DESIGN REMEDIATION — NO PRODUCTION CODE`  

---

## 1. PURPOSE & AUDIT CONTEXT

During the independent technical audit of the initial T-007 design package (`T007_DESIGN_PACKAGE.zip`), several architectural, semantic, and interface discrepancies with canonical contracts were identified. In strict accordance with repository governance policy ([`AGENTS.md`](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/AGENTS.md)), this document establishes the formal register of all detected defects (`DEF-01` through `DEF-08`), cross-references binding authorities, and specifies the remediation strategy implemented across the `T007_DESIGN_R1_*` deliverables.

---

## 2. DEFECT LOG & CANONICAL CONFLICT REGISTER

| Defect ID | Severity | Defect Description in Initial T-007 Design | Canonical Standard / Binding Standard | Remediation Specification in R1 |
|---|---|---|---|---|
| **DEF-01** | **CRITICAL** | Described `OP_CARRIER_FL_NUM <= 0 => QUARANTINED` as a hard, approved quarantine rule across matrices and decision tables. | [`G3_OFFICIAL_SIGNOFF_HUMAN_ACCEPTANCE_RECORD.md`](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/docs/05-evidence/G3_OFFICIAL_SIGNOFF_HUMAN_ACCEPTANCE_RECORD.md) §3.1 (`G3-COND-A`). | Reclassified `OP_CARRIER_FL_NUM <= 0` as `PROVISIONAL / PENDING_DATA_VALIDATION`. Forbidden from automatic hard quarantine in T-007 without empirical distribution survey in `G4/T-008`. Core record anchors restricted to approved identity violations. |
| **DEF-02** | **HIGH** | Claimed `SOURCE_MANIFEST.json` contains raw CSV SHA-256 hashes for source verification. | `docs/05-evidence/inputs/SOURCE_MANIFEST.json` line 3: *"SHA-256 verifies snapshots of user-provided audit documents; NOT raw CSV files."* | Analyzed actual `SOURCE_MANIFEST.json` schema. Separated audit document hashes from local raw CSV hashes. Designed dedicated Ingestion Manifest tracking local raw CSV SHA-256 hashes while preserving `OR-08 = IDENTITY_UNVERIFIED` for BTS origin. |
| **DEF-03** | **HIGH** | Described non-existent `SafePublisher.publish_run()` method and asserted atomic rename promotion. | Live production source in [`src/flight_pipeline/storage/publication.py`](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/src/flight_pipeline/storage/publication.py) lines 110–350 (`SafePublisher.publish`). | Aligned design with live API: `SafePublisher.publish(run_id, staging_dir, accounting, fault_injection_step5=False)`. Clarified that Step 3 executes `shutil.copytree` followed by byte-by-byte and SHA-256 audit. Separated curated Parquet from diagnostic quarantine text. |
| **DEF-04** | **HIGH** | Assumed `PERMISSIVE` mode with `_corrupt_record` automatically catches all 34-column physical mismatches. | PySpark 4.0.1 CSV parser specifications, Catalyst column pruning behavior, and `DATA_CONTRACT.md` DC-11. | Analyzed PySpark 4.0.1 CSV parsing nuances (token count mismatch vs numeric nulling vs unclosed quotes). Added explicit projection to prevent Catalyst column pruning. Formulated fail-closed `ACCOUNTING_UNVERIFIED` protocol. |
| **DEF-05** | **MEDIUM** | Applied zero-padding to time strings without checking raw formats; regex pipe `\|` confused with Markdown table delimiters; imprecise double-to-integer cast. | `DATA_DICTIONARY.md`, `T-004` audit, [`FP-DEC-007`](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/docs/02-design/DECISIONS.md), and `G2-EXC-001`. | Clarified anchored date regex `^(?:\d{4}-\d{2}-\d{2}\|\d{4}-\d{2}-\d{2} 00:00:00)$`. Prohibited date rollover or timezone fabrication (`FP-DEC-007`). Preserved 7 CORE measures units as `PROVISIONAL` under `G2-EXC-001`. Defined safe numeric casting. |
| **DEF-06** | **HIGH** | Single-writer lock design permitted automatic stale lock revocation after 2 hours or if Windows PID query failed. | Storage reliability and NTFS file locking concurrency safety. | Enforced fail-closed locking: if lock owner liveness cannot be disproven (e.g. Windows `OpenProcess` Access Denied), the pipeline aborts with `PublicationContentionError`. Lock is never stolen without definitive proof of owner death. |
| **DEF-07** | **HIGH** | Misassigned `TS-009` to pointer publication; recreated `OR-01..OR-08` with shadow meanings colliding with canonical risk register. | [`TEST_PLAN.md`](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/docs/03-quality/TEST_PLAN.md) and [`RISK_REGISTER.md`](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/docs/03-quality/RISK_REGISTER.md). | Restored canonical test mapping (`TS-001` schema, `TS-002` types, `TS-003` DC-11, `TS-009` FLIGHTS/weather, `TS-013` fault injection, `TS-018` units, `TS-019` identity, `TS-020` lineage). Restored canonical `OR-01..OR-08` risk definitions. Introduced separate `OPR-` prefix for operational execution risks. |
| **DEF-08** | **MEDIUM** | Implementation DAG had minor subtask numbering inconsistencies (7 subtasks vs 6 in text), lacked formal checkpoint gates, and suggested invalid `git revert -m`. | `ROADMAP.md`, `BACKLOG.md`, and `ROLLBACK_PLAN.md`. | Standardized implementation DAG into 7 structured subtasks (`T007-01` to `T007-07`). Formulated 3 distinct Human Signoff Checkpoints. Corrected rollback procedures to standard non-destructive Git commands. |

---

## 3. REMEDIATION DOCUMENTATION STRUCTURE

To preserve immutable historical audit records while delivering complete, verified corrections, the remediation is published under the `T007_DESIGN_R1_` prefix:

1. `T007_DESIGN_R1_CANONICAL_CONFLICT_REGISTER.md` (Current Document): Defect registry and resolution matrix.
2. `T007_DESIGN_R1_SOURCE_SCHEMA_CORRECTIONS.md`: Exact 34-column schema, data types, and date/time fidelity.
3. `T007_DESIGN_R1_CLASSIFICATION_POLICY_RECONCILIATION.md`: Full reconciliation with `G3-COND-A`, provisional policies, and DC-11/DC-12.
4. `T007_DESIGN_R1_CSV_RECORD_ACCOUNTING_REVIEW.md`: PySpark 4.0.1 CSV parser behavior, column pruning prevention, and accounting proofs.
5. `T007_DESIGN_R1_T009_PUBLICATION_INTERFACE_REVIEW.md`: Exact integration with live `SafePublisher.publish()` and `RunManifest`.
6. `T007_DESIGN_R1_SINGLE_WRITER_AND_ROLLBACK_REVIEW.md`: Fail-closed single-writer locking and non-destructive rollback.
7. `T007_DESIGN_R1_TEST_TRACEABILITY_CORRECTIONS.md`: Canonical alignment with `TEST_PLAN.md` and `RISK_REGISTER.md`.
8. `T007_DESIGN_R1_IMPLEMENTATION_DAG_REVISED.md`: Revised 7-subtask DAG with 3 human review checkpoints.
9. `T007_DESIGN_R1_FINAL_INDEPENDENT_VERDICT.md`: Comprehensive audit synthesis and readiness recommendation.

---

## 4. CONFLICT REGISTER VERDICT

All 8 identified defects have been formally cataloged with binding authorities and concrete technical remediation specifications.

**CONFLICT REGISTER STATUS: FULLY LOGGED & REMEDIATION SPECIFIED.**
