# G6_PROJECT_LEAD_D1_D4_SIGNOFF_STATUS.md
## Official Governance Decision Register & Human Signoff Handoff

**Project:** US Flight Performance Analysis 2016–2024  
**Date:** 2026-10-21  
**Current Gate:** Gate G5 = IN_PROGRESS (TECHNICALLY READY, AWAITING HUMAN DECISION)  
**Next Gate:** Gate G6 = NOT_STARTED / BLOCKED  
**Author:** Project Governance, Release & Evidence Manager  
**Scope:** Canonical mapping of Decisions D1–D5 and Architectural Choice G6-ARCH-2016

---

## 1. Strict Separation of Agent vs. Project Lead Authority

Per `AGENTS.md` and repository governance policies:
- The AI Agent acts as an engineering auditor, implementer, and technical evidence compiler.
- The AI Agent **HAS NO AUTHORITY** to self-approve governance decisions, self-sign gates, or self-authorize pipeline executions.
- The existence or provision of an agent prompt does **NOT** constitute project signoff.
- All decisions remain in their governed pending status until Project Lead provides explicit human signature in writing.

---

## 2. Master Decision Register (D1–D5)

| Decision ID | Topic | Current Governed Status | Agent Recommendation | Human Approval Action Required |
|---|---|---|---|---|
| **D1** | BTS TranStats Source Provenance Attestation | **AWAITING_PROJECT_LEAD_DECISION** (PENDING) | Attestation of physical BTS ZIP download receipt by operator. | Project Lead review of BTS ZIP SHA-256 (`342de99f65561fb856b524c704f2ad3851f8015f52251668ece346dff1350ae6`) and witness CSV intake. |
| **D2** | FP-DEC-019 / Option B (Unit Verification Scope) | **PROPOSED / PENDING** | Approve Option B: RAW CSV 2019 vs BTS Jan 2019 unit verification for exact 7 CORE measures. | Project Lead formal ratification of Option B, preserving `PARQUET_PARITY_NOT_TESTED`. |
| **D3** | TS-018 Technical Signoff & G2-EXC-001 Closure | **HUMAN_SIGNOFF_PENDING** | Technical evidence (E01–E05, 1,500 flight witness, 14 negative tests) is complete and reproducible. | Project Lead formal signature resolving G2-EXC-001 as `RESOLVED_BY_OPTION_B`. |
| **D4** | Gate G5 Human Gate Signoff | **IN_PROGRESS (TECHNICALLY READY)** | All 19 G5 exit criteria satisfied technically. Residual risks documented. | Project Lead formal signature transitioning Gate G5 from `IN_PROGRESS` to `PASS (CONTROLLED)`. |
| **D5** | Gate G6 / T-012 Full Run Execution Authorization | **NOT_AUTHORIZED / BLOCKED** | Keep strictly BLOCKED until D1–D4 are signed and 2016 preflight is verified. | Project Lead authorization to commence annual batch execution. |

---

## 3. Independent Architectural Decision: G6-ARCH-2016

To determine how the 2016 baseline dataset is integrated into the multi-year curated catalog, two distinct options are presented:

- **Option A (Promote Baseline T-010):**
  - Promote the existing 50 Parquet files generated during T-010 benchmark to `curated/runs/run_2016_v1/`.
  - Generates retroactive `run_manifest.json` and `execution_receipt.json`.
  - *Risks:* T-010 Parquet files were created under benchmark harness and lack inline production `RunManifest` cryptographic lineage.
- **Option B (Recommended — Versioned Production Rerun):**
  - Preserve the 50 T-010 Parquet files in `data/curated/` as read-only historical benchmark evidence.
  - Execute a clean, versioned production run for Year 2016 into `data/curated/runs/run_2016_v1/` using the hardened `IngestionCoordinator` and `SafePublisher`.
  - Produces authentic, tamper-evident `run_manifest.json` and `execution_receipt.json`.
  - *Current Status:* **RECOMMENDED BY TECHNICAL TEAM — AWAITING PROJECT LEAD RATIFICATION**.

---

## 4. Preserved Governance Invariants (Active Constraints)

The following governance invariants remain strictly active and unaltered:
1. **OR-08 (IDENTITY_UNVERIFIED):** Upstream RAW data files in `data/raw/` retain `source_signature` based on size and mtime, but raw content provenance remains uncertified against BTS digital signatures.
2. **OR-05 (PARTIAL Coverage 2024):** Year 2024 is strictly governed as `PARTIAL` coverage due to the audited missing March dataset.
3. **FP-DEC-017 (Weather Branch Status):** Weather correlation pipeline remains `CONDITIONAL_NO_GO`. It is decoupled from CORE pipeline execution.
4. **PARQUET_PARITY_NOT_TESTED:** Parquet parity against BTS reference Parquet files remains unverified; only RAW CSV vs BTS Jan 2019 was tested under Option B.
5. **G2-EXC-001:** Remains `ACTIVE` until Project Lead formally executes Decision D3.

---

## 5. Summary Handoff Verdict

The engineering team has completed all preflight hardening and verifier remediation. The project is in state:
```
READY_FOR_PROJECT_LEAD_SIGNOFF_AND_G6_PREEXECUTION
```
**No pipeline execution or state modification will occur without Project Lead signature.**
