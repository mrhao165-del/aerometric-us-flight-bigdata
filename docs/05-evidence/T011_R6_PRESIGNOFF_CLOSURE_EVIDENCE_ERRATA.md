# T011-R6 PRESIGNOFF CLOSURE EVIDENCE ERRATA
## Factual Errata & Assertion Count Reconciliation (Finding PC-F03)

**Project:** US Flight Performance Analysis 2016–2024  
**Task:** T-011 R6 Pre-Signoff Closure  
**Parent Gate:** G5 (IN_PROGRESS)  
**Date:** 2026-10-19  
**Technical Role:** Evidence Governance Auditor & Technical Reviewer

---

## 1. Context & Independent Review Finding

The independent technical review of the `T011_R6_PRESIGNOFF_REVIEW_PACKAGE.zip` baseline verified:
1. **ZIP Member Integrity:** 674/674 files passed CRC and SHA-256 verification.
2. **ZIP SHA-256 Digest:** `1260106839a0f0c1a5f0b653a72ac034950066b755033f97d8e0d80b07e6fadf` verified exact.
3. **Raw Unittest Execution:** Exactly 326 tests across 23 test modules executed in 411.634s with status `OK` (0 FAIL).
4. **Document Attestation Table:** Exactly 27/27 canonical Markdown documents verified on disk with exact byte counts and SHA-256 hashes.
5. **Raw QA Log Consistency Assertion Count:** In the execution log `T011_R6_PRESIGNOFF_RAW_QA_LOG.txt`, script #12 reported: `Working-Tree PASS assertions: 1359; FAIL: 0`.
6. **Discrepancy Noted (PC-F03):** The previous assistant summary report stated that the QA verification suite executed 1,361 assertions.

---

## 2. Root Cause Analysis & Factual Reconciliation

The discrepancy of 2 assertions between 1,359 and 1,361 was caused by a sequential timing distinction in the deliverable registration lifecycle:

1. **Step 1 (Raw QA Suite Execution):**
   - When `run_presignoff_qa.py` executed the 12 QA scripts, `T011_R6_PRESIGNOFF_RAW_QA_LOG.txt` had not yet been written to `docs/05-evidence/`.
   - Script #12 (`tools/check_working_tree_consistency.py`) ran against all registered deliverables existing at that moment.
   - It verified exactly **1,359 assertions with 0 FAIL**.
   - `run_presignoff_qa.py` completed and flushed the raw execution output to `docs/05-evidence/T011_R6_PRESIGNOFF_RAW_QA_LOG.txt`.

2. **Step 2 (Post-QA Registration & Final Verification):**
   - The newly generated log `T011_R6_PRESIGNOFF_RAW_QA_LOG.txt` was added to `EVIDENCE_DELIVERABLE_REGISTER.json`.
   - Adding this registered deliverable increased the assertion perimeter of `tools/check_working_tree_consistency.py` by exactly 2 checks:
     - Check 1: Registered deliverable metadata & security rules valid for `T011_R6_PRESIGNOFF_RAW_QA_LOG.txt`.
     - Check 2: Physical size and SHA-256 checksum verified for `T011_R6_PRESIGNOFF_RAW_QA_LOG.txt`.
   - Executing `tools/check_working_tree_consistency.py` on the final tree produced: `Working-Tree PASS assertions: 1361; FAIL: 0`.

3. **Reporting Ambiguity:**
   - The assistant report cited the post-registration total of 1,361 assertions as the result of the QA suite run, whereas the raw QA log file itself records 1,359 assertions.
   - Both assertions were 100% PASS with 0 FAIL, but referring to the post-registration count without clarifying the sequence caused a documentary ambiguity.

---

## 3. Authoritative Corrected Record

This errata formally and supersedingly establishes the factual numbers:

| Verification Phase | Target Scope | Actual Assertions PASS | FAIL | Log Reference |
|:---|:---|:---:|:---:|:---|
| **Raw QA Suite Execution** | 12 QA scripts including pre-log tree verification | **1,359** | 0 | `docs/05-evidence/T011_R6_PRESIGNOFF_RAW_QA_LOG.txt` |
| **Post-Registration Seal** | Final tree including QA log entry in registry | **1,361** | 0 | Interactive verification via `tools/check_working_tree_consistency.py` |

---

## 4. Preservation of Historical Evidence

In strict compliance with repository governance rules:
- No historical reports, sealed evidence, or audit manifests have been retroactively edited or rewritten.
- This document stands as the factual, authoritative errata reconciling the audit trail.
