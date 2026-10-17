# T009-R3-EXIT Registry Failure Forensic Reconciliation Report

## 1. Context & Identified Blocker
During the initial review of T-009 R3 evidence, log file `docs/05-evidence/T009_R3_LOG_REGISTRY_REGRESSION.txt` was found to contain failure records for test cases POS-01 and POS-02:
```text
[FAIL] POS-02: Historical immutable evidence and registered baseline accepted with 0 failures
[FAIL] POS-01: Correctly registered new evidence artifact with matching size and SHA-256 is accepted
REGRESSION SUITE SUMMARY: 14 PASS, 2 FAIL, 0 SKIP
```
This failure represented a critical governance concern that blocked final human signoff of Task T-009.

---

## 2. Root Cause Forensic Analysis
A thorough execution trace of the T-009 R3 run was conducted:
1. **Timing of Execution:** In T009-R3, the test file `tests/test_t009_r3_defect_reproductions.py` was created on disk during defect test authoring.
2. **Intermediate Fixture Generation:** Immediately following file creation, background task `task-1153` executed `python tools/qa/test_working_tree_registry_regression.py`.
3. **Fixture Isolation Mechanism:** The test suite uses `build_isolated_fixture()`, which traverses `ROOT.rglob('*')` and replicates all tracked files into a temporary sandbox along with `EVIDENCE_DELIVERABLE_REGISTER.json`.
4. **The Transient Anomaly:** At that specific point in time, `tests/test_t009_r3_defect_reproductions.py` physically existed in the repository tree, but had not yet been registered in `EVIDENCE_DELIVERABLE_REGISTER.json` (as register update was scheduled as the subsequent consolidation step).
5. **Detection:** When `check_working_tree_consistency.py` ran inside the temporary fixture, it correctly identified `tests/test_t009_r3_defect_reproductions.py` as an unrecognized stray file, appropriately failing POS-02 and POS-01.
6. **Premature Artifact Capture:** The stdout of `task-1153` was captured directly to `T009_R3_LOG_REGISTRY_REGRESSION.txt` before the registration step completed, immortalizing an intermediate uncommitted state in the evidence log.

---

## 3. Definitive Proof of Resolution
To verify that the working tree and registry are in complete alignment:
1. The repository working tree was verified with `tests/test_t009_r3_defect_reproductions.py` fully registered in `EVIDENCE_DELIVERABLE_REGISTER.json`.
2. `tools/qa/test_working_tree_registry_regression.py` was executed directly against the synchronized state.
3. **Result:**
   ```text
   [PASS] POS-02: Historical immutable evidence (`SOURCE_MANIFEST.json`, `PACKAGE_MANIFEST.json`) and registered baseline accepted with 0 failures
   [PASS] POS-01: Correctly registered new evidence artifact with matching size and SHA-256 is accepted
   [PASS] NEG-01: Unregistered arbitrary Markdown file is rejected
   [PASS] NEG-02: File with valid-looking `T005_` prefix but absent from registry is rejected
   [PASS] NEG-03: Registered artifact with modified content or incorrect SHA-256 is rejected
   [PASS] NEG-04: Registered artifact with missing file or size mismatch is rejected
   [PASS] NEG-05: Malformed registry JSON and duplicate registry entries are both rejected
   [PASS] NEG-06: Path traversal (`../`) or unsafe path in registry is rejected
   [PASS] NEG-07: Unexpected `.pt` extension in evidence directory and forged task identifier (`T-999`) are both rejected
   [PASS] NEG-08: Tampering with `SOURCE_MANIFEST.json` inputs or unapproved `PACKAGE_MANIFEST.json` files cannot be bypassed via the registry
   [PASS] NEG-09: Tampering with pinned PACKAGE_MANIFEST/SOURCE_MANIFEST or registering unapproved living doc is rejected
   [PASS] NEG-10A: Unapproved artifact_type is strictly rejected
   [PASS] NEG-10B: Symlink injection into working tree is strictly rejected by checker and path validator
   [PASS] MUT-NEG10-01: Mutation test proves unconditional false-PASS fallback ('or True') is identified and rejected
   [PASS] MUT-NEG10-02: Path helper _is_safe_rel_path strictly rejects traversal (../), absolute, backslash, and empty paths
   [PASS] MUT-NEG10-03: Unauthorized artifact_type allowlist strictly enforces approved enum members
   REGRESSION SUITE SUMMARY: 16 PASS, 0 FAIL, 0 SKIP
   ALL POSITIVE AND NEGATIVE REGISTRY REGRESSION TESTS PASSED.
   ```
4. Exit code: `0`.
5. Official verified log: `docs/05-evidence/T009_EXIT_LOG_REGISTRY_REGRESSION.txt`.

---

## 4. Conclusion
The failure in `T009_R3_LOG_REGISTRY_REGRESSION.txt` was purely an artifact capture sequencing issue during R3 execution. The underlying mechanism operated exactly as designed, proving that the governance engine strictly detects unregistered files. With the repository in a fully synchronized state, all 16 positive, negative, and mutation test cases pass without error.
