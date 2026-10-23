# FP-DEC-018 — Official Project Lead Approval

**Project:** US Flight Performance Analysis 2016–2024  
**Date:** 2026-10-19 (Asia/Ho_Chi_Minh)  
**Previous proposal:** `FP-DEC-PROP-018: Treatment of Post-Publication Lock Release Incidents`  
**Approved ID:** `FP-DEC-018`  
**Decision status:** `APPROVED_WITH_CONDITIONS`  
**Authority:** Project Lead, via explicit acceptance communicated in the current ChatGPT conversation on 2026-10-19.  
**Scope:** Post-publication lock-release incidents and manual recovery in the T-011 implementation. This is NOT an approval of TS-018 or Gate G5/G6.

## 1. Binding decision

The Project Lead approves the **non-destructive preservation / fail-closed** option in `T011_R6_PRESIGNOFF_CLOSURE_FP_DEC_018_REVIEW.md`, with the independently reviewed Post-Closure corrections included:

1. If publication has *actually committed, and the published payload/receipt are verified* before lock-release failure, the immutable published dataset remains valid and readable; do **not** roll back correctly committed Parquet or the already committed latest pointer merely because local cleanup fails.
2. `PipelineRunOutcome.success=True` may describe **publication success only**. It must not misrepresent operational readiness: report `recovery_required=True`, `MANUAL_RECOVERY_REQUIRED`, explicit `release_error`, and validated incident-persistence status separately. A higher-level scheduler/operator must treat recovery-required as an outstanding incident, not unconditional readiness to start another write.
3. All cooperating writers MUST be denied admission until unresolved `.del_*`, `.failed_acq_*`, quarantine, `.release_in_progress_*`, `.recovery_in_progress_*`, and `.recovery_required_*` artifacts have been handled under the approved protocol. Explicit fail-closed evidence is required for disk/record-write failures and interrupted recovery.
4. Manual recovery requires a **separately authorized operator** who has verified **quiescence / no active writer**. `authorized=True` and caller-provided `operator` name are *not* proof of identity or authorization. Preserve incident and resolution audit trails, verified SHA-256, and operator reason; remove blocking markers only after resolution record is committed and verified.
5. Incident persistence must never be reported successful when write, fsync, atomic promotion or readback fails. Propagate `INCIDENT_PERSISTENCE_FAILED`, preserving release error and original processing error as applicable.
6. Safety guarantee is limited to the **cooperating-writer model using the approved coordination protocol** and documented Windows NTFS tests. It does not claim protection against arbitrary actors with unmanaged direct filesystem modification privileges, process crashes/power-loss beyond tested guarantees, or unauthorized administrator actions.

## 2. Supporting evidence and independent review

- Baseline package: `T011_POST_CLOSURE_REVIEW_PACKAGE.zip` (also submitted again unchanged as `(1)`); **2,379,324 bytes**, SHA-256 `959bcdbf2ca8cc3fb123b4c3c311c5d1dd0df5f444d9966593dfff50ccc8244c`.
- Package manifest and CRC: **694/694** PASS, no duplicate paths, mismatches or missing members.
- Raw Windows unit-test log: `Ran 364 tests in 384.634s`, `OK`, 25 test modules (source is agent-supplied execution log, not independently rerun end-to-end on Windows).
- Raw QA logs: **12/12 scripts exit 0**; working-tree checker **1,399 assertions PASS** in raw log; agent's post-registration assertion claim 1,401 not directly supported by that same log.
- Independent targeted execution: **18/18 Post-Closure tests PASS** on Linux/Python environment; targeted recovery-admission and release-incident negative counterexamples PASS.
- Independent audit artifact: `T011_POST_CLOSURE_INDEPENDENT_AUDIT_20261019.md` (provided in the conversation).
- Evidence limitations: raw source CSV and physical staging not included in this ZIP, so this approval does not independently re-attest their actual bytes or establish upstream BTS source identity.

## 3. Explicit boundaries / NON-approvals

- `TS-018 = AUTHENTIC_BTS_PARITY_PENDING`: no official BTS sample, numerical source verification, or independent provenance signoff has been accepted in this decision.
- The seven CORE fields `ARR_DELAY`, `DEP_DELAY`, `TAXI_OUT`, `TAXI_IN`, `AIR_TIME`, `ACTUAL_ELAPSED_TIME`, `CRS_ELAPSED_TIME` remain `OFFICIAL_MINUTES_EMPIRICALLY_CONSISTENT_PROVISIONAL` until authentic BTS evidence is independently reviewed and approved.
- `G2-EXC-001 = ACTIVE`; `G5 = IN_PROGRESS`; `G6 = NOT_STARTED / BLOCKED`. No full-run or final KPI publication.
- `OR-05 = OPEN_QUALITY_DEFECT` (missing March 2024); `OR-08 = IDENTITY_UNVERIFIED`; weather excluded from CORE (`FP-DEC-017 CONDITIONAL_NO_GO`); `G3-COND-A/B/C`, `DC-11/DC-12`, `FP-DEC-012`, `FP-DEC-015`, `FP-DEC-016` remain unchanged.
- No new policy or automatic clearance mechanism is authorized beyond the specifically reviewed implementation.

## 4. Recording requirement

The Agent may **transcribe this explicit human decision** into the actual repository `docs/02-design/DECISIONS.md`, `docs/04-execution/PROJECT_STATE.md`, `docs/01-planning/BACKLOG.md`, `docs/03-quality/CHANGELOG.md`, `docs/04-execution/AI_HANDOFF.md`, and relevant evidence registry, *without re-deciding or expanding it*. Preserve the original proposal and independent audit unmodified. Verify the recorded changes and emit a dedicated official signoff package.

**Decision basis:** explicit acceptance by the Project Lead in ChatGPT on 2026-10-19, following presentation of FP-DEC-PROP-018 and controlled T-011 technical acceptance. No handwritten/digital cryptographic signature is asserted by this text.
