# T011-R5 Checksum Format and Provenance Validation Audit

**Project:** US Flight Performance Analysis 2016–2024  
**Task:** T-011 R5 — Lock Safety Closure and Evidence Reconciliation  
**Parent Gate:** G5 — `IN_PROGRESS`  
**Finding Reference:** `R5-F02` (BTS Candidate SHA-256 Hexadecimal Validation)  
**Date:** 2026-10-19  

---

## 1. Description of Finding R5-F02

In T011-R4, `BtsProvenanceValidator` validated that the declared and actual SHA-256 hashes had a length of 64 characters (`len(hash.strip()) == 64`), but did not enforce strict hexadecimal encoding (`[0-9a-fA-F]{64}`).

When tested with:
```python
sha256_hash = "z" * 64
actual_sha256 = "z" * 64
```
The validator returned:
```python
(True, "CANDIDATE_CHECKSUM_MATCHED")
```
Because `"z"` is not a valid hexadecimal character, a non-hex digest string was improperly accepted as a matching candidate checksum.

---

## 2. Pre-Fix Execution Log

Executing the unpatched R4 validator directly verified the issue:
```text
R5-F02 reproduction on unpatched code: ok = True msg = CANDIDATE_CHECKSUM_MATCHED
```

---

## 3. Required Remediation

1. Implement `is_valid_sha256_hex(val: Any) -> bool`:
   - Must be a non-empty string.
   - Reject leading or trailing whitespace (`val == val.strip()`).
   - Match regex `^[0-9a-fA-F]{64}$`.
2. Update `BtsProvenanceValidator.validate_metadata_format`:
   - Strictly require declared `sha256_hash` to satisfy `is_valid_sha256_hex`.
   - Reject non-hex with `PROVENANCE_MALFORMED_HASH`.
3. Update `BtsProvenanceValidator.validate_candidate_checksum`:
   - Strictly require actual `actual_sha256` to satisfy `is_valid_sha256_hex`.
   - Reject non-hex with `PROVENANCE_ACTUAL_CHECKSUM_MALFORMED`.
4. Preserve Governance Invariants:
   - `source_provenance_verified = False` unconditionally for locally described candidates.
   - `human_accepted = False` unconditionally until genuine Project Lead signoff.
   - BTS unit status remains `OFFICIAL_MINUTES_EMPIRICALLY_CONSISTENT_PROVISIONAL`.
   - TS-018 authentic parity remains `PENDING`.
