# TS018 REFERENCE POLICY & SOURCE INVENTORY ERRATA
## Narrowly Scoped Errata & Hardening Record for TS-018 Reference Data Governance

**Project:** US Flight Performance Analysis 2016–2024  
**Date:** 2026-10-20 (Asia/Ho_Chi_Minh)  
**Parent Task:** Task T-011 / TS-018  
**Parent Gate:** Gate G5 (`IN_PROGRESS`)  
**Scope:** Controlled documentation errata and reference policy hardening record.

---

## 1. Erratum TS018-ERR-01: BTS CSV Physical Header Column Count

- **Historical Reference:** [`TS018_BTS_ACQUISITION_READINESS_20261019.md`](TS018_BTS_ACQUISITION_READINESS_20261019.md#L83) (Section 5, Item 83) stated:
  > *"Contained File: `T_ONTIME_REPORTING.csv` (217,369,264 bytes uncompressed, 109 columns, covering January 2019)."*
- **Forensic Verification:** An automated streaming reader directly read the first row of `T_ONTIME_REPORTING.csv` decompressed from `T_ONTIME_REPORTING_20261019_112232.zip`.
- **Observed Physical Value:** The header line contains exactly **108 columns** (from `YEAR` to `DIV5_TAIL_NUM`), comma-delimited, without a trailing empty delimiter.
- **Root Cause of Prior Claim:** In certain BTS TranStats web exports, an unselected trailing comma produces a 109th empty header token (`""`). In this specific official download, the export cleanly ends on `DIV5_TAIL_NUM` with no trailing comma, yielding exactly 108 columns.
- **Superseding Action:** Historical document [`TS018_BTS_ACQUISITION_READINESS_20261019.md`](TS018_BTS_ACQUISITION_READINESS_20261019.md) is preserved immutable. This erratum supersedes the column count to **108 columns**.

---

## 2. Erratum TS018-ERR-02: Bounded Reference Data Policy Hardening

### Background
In the signoff snapshot of `tools/check_working_tree_consistency.py`, reference files were accounted for via:
```python
reference_data_files = {
    f for f in extra_files if f.startswith("data/reference/")
}
```
This broad rule was identified during independent review as overly permissive, potentially masking arbitrary unrecognized files placed anywhere inside `data/reference/`.

### Hardened Bounded Policy (Implemented under TS-018 Phase S1)
The policy was hardened with strict, multi-layered governance:
1. **Strict Subtree Whitelist:** All reference files must reside strictly within `data/reference/bts_transtats/`. Any file in `data/reference/` root or unapproved subtrees is immediately rejected.
2. **Explicit Inventory Manifest:** Every accepted reference file must be registered in [`TS018_201901_ORIGINAL_AND_DERIVED_HASH_MANIFEST.json`](TS018_201901_ORIGINAL_AND_DERIVED_HASH_MANIFEST.json) with exact byte size and SHA-256 hash.
3. **Cryptographic Verification:** Every physical file is checked against its manifest digest; any mismatch or tampered file fails consistency checks.
4. **Denial of Stray Artifacts:** Any unregistered file inside `data/reference/` is flagged as an unrecognized stray file and fails the repository check (no unrestricted auto-pass).
5. **Path Traversal Protection:** Relative traversal sequences (`../`), backslashes, and symlinks are strictly rejected.

### Git Ignore Hardening
- Anchored `/data/reference/` was added to `.gitignore` to prevent large binary reference archives (such as the 29.9 MB ZIP and 217 MB CSV) from being tracked in Git.
- Verified via `git check-ignore -v` that reference archives and working files are ignored, while all evidence markdown documents in `docs/05-evidence/` remain tracked.

---

## 3. Rollback & Pre-Change Backups

Prior to applying the patch, verified byte-exact backups were created and registered in [`EVIDENCE_DELIVERABLE_REGISTER.json`](EVIDENCE_DELIVERABLE_REGISTER.json):

| Original File | Pre-Change Backup Location | Original Size | Original SHA-256 |
|---|---|---|---|
| `.gitignore` | `docs/05-evidence/TS018_BACKUPS/.gitignore.pre_ts018.bak` | 315 bytes | `cf71bf4e52ec4d214129bf215c182937b71fb43f0cbcc62ef49e100772b55459` |
| `tools/check_working_tree_consistency.py` | `docs/05-evidence/TS018_BACKUPS/tools__check_working_tree_consistency.py.pre_ts018.bak` | 24,704 bytes | `334d1d2474ca79fa5beae31876cfa04d4971db88ddc9710b26bb602ec4e200f8` |

---

## 4. Verification & QA Suite

A dedicated regression test suite was created at [`tools/qa/test_ts018_reference_policy_regression.py`](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/tools/qa/test_ts018_reference_policy_regression.py):
- **POS-01:** Legitimate known reference ZIP and companion matching manifest accepted (PASS).
- **NEG-01:** Unregistered file in reference directory rejected as stray (PASS).
- **NEG-02:** Tampered reference file failing SHA-256 match rejected (PASS).
- **NEG-03:** Unauthorized file outside allowed reference subtree rejected (PASS).
- **NEG-04:** Path traversal attempt (`../`) rejected (PASS).
- **NEG-05:** Ghost / corrupted artifact rejected (PASS).
- **Suite Result:** **6 PASS, 0 FAIL** (100% pass rate).
