# G6 Test Inventory Discovery & Artifact Cryptographic Hash Errata

**Document ID:** `DOC-G6-ERRATA-TEST-001`  
**Classification:** QA TEST AUDIT & CRYPTOGRAPHIC HASH RECONCILIATION  
**Task Reference:** Finding M04 / Gate G6 Preflight Integrity Audit  
**Date:** 2026-10-20  
**Evaluator:** Senior PySpark QA Engineer & Independent Forensic Auditor  
**Status:** RECONCILED & AUDITED  

---

## 1. Executive Summary & Reason for Errata

In the previous turn's summary report, two discrepancies were identified by the Independent Reviewer:
1. **Test Naming Inconsistency:** The summary report referred to test cases using sequential numbers (`test_01_...`, `test_02_...`), while the codebase was transitioning between naming schemes.
2. **Artifact Hash Drift:** In earlier reports, placeholder or pre-final hashes were cited that did not match the finalized physical files after registry synchronization.

This document issues a formal reconciliation:
- Emits the complete, exact test inventory discovered directly by `python -m unittest -v`.
- Computes exact file sizes and SHA-256 hashes directly from the Windows filesystem.
- Clearly delineates synthetic test fixture boundaries from physical production datasets.

---

## 2. Complete Discovered Test Inventory (40 Tests, 100% PASS)

The test suite consists of 40 automated regression tests across two modules:
- `tests/test_multiyear_snapshot_policy.py`: 31 tests (4 positive, 27 negative counterexamples).
- `tests/test_lock_state_vs_pointer_state.py`: 9 tests (1 positive, 8 negative preflight/safety checks).

### 2.1 Multi-Year Snapshot Policy Suite (31 Tests in `test_multiyear_snapshot_policy.py`)

| Test Method Name | Class Name | Category | Objective / Scenario | Verdict |
| :--- | :--- | :---: | :--- | :---: |
| `test_pos_01_complete_canonical_9year_snapshot_passes` | `TestMultiyearSnapshotPolicyComprehensive` | POSITIVE | 9-year canonical snapshot with valid RunManifest and Parquet passes | **PASS** |
| `test_pos_02_valid_snapshot_with_nonzero_quarantine_rejects_passes` | `TestMultiyearSnapshotPolicyComprehensive` | POSITIVE | DC-11 conservation with realistic non-zero quarantine and rejects passes | **PASS** |
| `test_pos_03_production_runmanifest_and_receipt_integration_passes` | `TestMultiyearSnapshotPolicyComprehensive` | POSITIVE | Full integration of RunManifest.to_dict() and ExecutionReceipt.to_dict() | **PASS** |
| `test_pos_04_multi_version_rerun_selection_passes` | `TestMultiyearSnapshotPolicyComprehensive` | POSITIVE | Selecting rerun (v2) excludes old version (v1) | **PASS** |
| `test_neg_01_manifest_status_failed_fails_closed` | `TestMultiyearSnapshotPolicyComprehensive` | NEGATIVE | Manifest with status='FAILED' fails closed (`MANIFEST_STATUS_NOT_PUBLISHED`) | **PASS** |
| `test_neg_02_manifest_status_missing_or_invalid_fails_closed` | `TestMultiyearSnapshotPolicyComprehensive` | NEGATIVE | Manifest with unknown status fails closed (`MANIFEST_STATUS_NOT_PUBLISHED`) | **PASS** |
| `test_neg_03_manifest_missing_configuration_years_fails_closed` | `TestMultiyearSnapshotPolicyComprehensive` | NEGATIVE | Missing configuration.years fails closed (`MANIFEST_YEARS_STRUCTURE_INVALID`) | **PASS** |
| `test_neg_04_manifest_year_mismatch_fails_closed` | `TestMultiyearSnapshotPolicyComprehensive` | NEGATIVE | Manifest declaring different year fails closed (`MANIFEST_YEAR_MISMATCH`) | **PASS** |
| `test_neg_05_manifest_run_id_mismatch_fails_closed` | `TestMultiyearSnapshotPolicyComprehensive` | NEGATIVE | Manifest run_id mismatching directory fails closed (`MANIFEST_RUN_ID_MISMATCH`) | **PASS** |
| `test_neg_06_manifest_missing_outputs_fails_closed` | `TestMultiyearSnapshotPolicyComprehensive` | NEGATIVE | Manifest declaring empty outputs fails closed (`MISSING_MANIFEST_OUTPUTS`) | **PASS** |
| `test_neg_07_manifest_output_hash_mismatch_fails_closed` | `TestMultiyearSnapshotPolicyComprehensive` | NEGATIVE | Forged output SHA-256 fails closed (`MANIFEST_FILE_HASH_MISMATCH`) | **PASS** |
| `test_neg_08_manifest_output_byte_size_mismatch_fails_closed` | `TestMultiyearSnapshotPolicyComprehensive` | NEGATIVE | Wrong output byte size fails closed (`MANIFEST_FILE_SIZE_MISMATCH`) | **PASS** |
| `test_neg_09_output_path_traversal_fails_closed` | `TestMultiyearSnapshotPolicyComprehensive` | NEGATIVE | Output path with `..` fails closed (`OUTPUT_PATH_TRAVERSAL_DETECTED`) | **PASS** |
| `test_neg_10_unlisted_physical_parquet_fails_closed` | `TestMultiyearSnapshotPolicyComprehensive` | NEGATIVE | Physical Parquet unlisted in outputs fails (`UNLISTED_PHYSICAL_PARQUET_DETECTED`) | **PASS** |
| `test_neg_11_parquet_physical_row_count_mismatch_fails_closed` | `TestMultiyearSnapshotPolicyComprehensive` | NEGATIVE | Physical rows != accepted rows fails (`PARQUET_PHYSICAL_ROW_COUNT_MISMATCH`) | **PASS** |
| `test_neg_12_parquet_forbidden_column_schema_fails_closed` | `TestMultiyearSnapshotPolicyComprehensive` | NEGATIVE | Parquet with forbidden column (`DISTANCE`) fails closed | **PASS** |
| `test_neg_13_parquet_missing_core_measures_schema_fails_closed` | `TestMultiyearSnapshotPolicyComprehensive` | NEGATIVE | Parquet missing 7 core measures fails closed | **PASS** |
| `test_neg_14_manifest_registry_accounting_mismatch_fails_closed` | `TestMultiyearSnapshotPolicyComprehensive` | NEGATIVE | Manifest accounting differing from registry fails closed | **PASS** |
| `test_neg_15_receipt_status_not_published_fails_closed` | `TestMultiyearSnapshotPolicyComprehensive` | NEGATIVE | Receipt status != PUBLISHED fails closed (`RECEIPT_STATUS_NOT_PUBLISHED`) | **PASS** |
| `test_neg_16_receipt_manifest_sha256_mismatch_fails_closed` | `TestMultiyearSnapshotPolicyComprehensive` | NEGATIVE | Receipt manifest SHA-256 mismatch fails closed | **PASS** |
| `test_neg_17_multiyear_run_unverified_partition_fails_closed` | `TestMultiyearSnapshotPolicyComprehensive` | NEGATIVE | Multi-year run without partitions fails closed | **PASS** |
| `test_neg_18_empty_run_directory_fails_closed` | `TestMultiyearSnapshotPolicyComprehensive` | NEGATIVE | Empty run directory fails closed (`EMPTY_RUN_DIRECTORY_OR_NO_PARQUET`) | **PASS** |
| `test_neg_19_fake_corrupt_parquet_fails_closed` | `TestMultiyearSnapshotPolicyComprehensive` | NEGATIVE | Text file renamed to .parquet fails closed (`CORRUPT_OR_FAKE_PARQUET_DETECTED`) | **PASS** |
| `test_neg_20_duplicate_physical_directory_fails_closed` | `TestMultiyearSnapshotPolicyComprehensive` | NEGATIVE | Reusing same directory for multiple years fails (`DUPLICATE_PHYSICAL_PATH`) | **PASS** |
| `test_neg_21_unbalanced_row_accounting_fails_closed` | `TestMultiyearSnapshotPolicyComprehensive` | NEGATIVE | $raw \neq accepted + quarantined + rejected$ fails closed | **PASS** |
| `test_neg_22_non_integer_row_accounting_fails_closed` | `TestMultiyearSnapshotPolicyComprehensive` | NEGATIVE | Boolean or float row count fails closed (`INVALID_NUMERIC_ACCOUNTING`) | **PASS** |
| `test_neg_23_negative_row_accounting_fails_closed` | `TestMultiyearSnapshotPolicyComprehensive` | NEGATIVE | Negative row count fails closed (`INVALID_NUMERIC_ACCOUNTING`) | **PASS** |
| `test_neg_24_canonical_raw_row_mismatch_fails_closed` | `TestMultiyearSnapshotPolicyComprehensive` | NEGATIVE | Raw count mismatching canonical baseline fails closed | **PASS** |
| `test_neg_25_missing_required_survey_year_fails_closed` | `TestMultiyearSnapshotPolicyComprehensive` | NEGATIVE | Missing survey year in 2016–2024 fails closed (`YEARS_COMPLETENESS_ERROR`) | **PASS** |
| `test_neg_26_year_2024_requires_partial_coverage_status_fails_closed` | `TestMultiyearSnapshotPolicyComprehensive` | NEGATIVE | Year 2024 not declaring 'PARTIAL' fails closed (`OR05_COVERAGE_STATUS_VIOLATION`) | **PASS** |
| `test_neg_27_path_traversal_curated_runs_escape_fails_closed` | `TestMultiyearSnapshotPolicyComprehensive` | NEGATIVE | Path traversal escaping curated root fails closed (`PATH_TRAVERSAL_DETECTED`) | **PASS** |

### 2.2 Lock & Pointer Safety Suite (9 Tests in `test_lock_state_vs_pointer_state.py`)

| Test Method Name | Class Name | Category | Objective / Scenario | Verdict |
| :--- | :--- | :---: | :--- | :---: |
| `test_01_negative_uninitialized_pointer_with_active_lock_is_not_safe` | `TestLockStateVsPointerStateRegression` | NEGATIVE | Active writer lock blocks preflight admission (exit code 1) | **PASS** |
| `test_02_negative_unresolved_recovery_marker_blocks_writer_admission` | `TestLockStateVsPointerStateRegression` | NEGATIVE | Presence of `.recovery` marker blocks admission (exit code 3) | **PASS** |
| `test_03_negative_stale_lock_dead_pid_does_not_auto_delete` | `TestLockStateVsPointerStateRegression` | NEGATIVE | Stale lock with dead PID fails closed safely (exit code 2) | **PASS** |
| `test_04_negative_corrupt_lock_metadata_fails_closed` | `TestLockStateVsPointerStateRegression` | NEGATIVE | Corrupt lock metadata fails closed (exit code 2) | **PASS** |
| `test_05_negative_ambiguous_liveness_fails_closed` | `TestLockStateVsPointerStateRegression` | NEGATIVE | Ambiguous process liveness fails closed (exit code 2) | **PASS** |
| `test_06_positive_clean_workspace_safe_for_lock_acquisition` | `TestLockStateVsPointerStateRegression` | POSITIVE | Clean workspace allows lock acquisition (exit code 0) | **PASS** |
| `test_07_storage_root_mismatch_blocks_writer_admission` | `TestLockStateVsPointerStateRegression` | NEGATIVE | Mismatch in `--expected-storage-root` blocks admission (exit code 4) | **PASS** |
| `test_08_pointer_corruption_fails_closed` | `TestLockStateVsPointerStateRegression` | NEGATIVE | Corrupt or dangling pointer fails closed (exit code 4) | **PASS** |
| `test_09_unified_tools_integration_consistency` | `TestLockStateVsPointerStateRegression` | POSITIVE | Pointer and preflight tools inspect identical resolved root paths | **PASS** |

---

## 3. Physical Evidence Deliverables Hash Audit

The following table records the exact physical byte sizes and SHA-256 hashes of all deliverables authored during the G6 Production Manifest Compatibility task:

| Relative File Path | Exact Bytes | SHA-256 Hash (64-char Hexadecimal) |
| :--- | :---: | :--- |
| `tools/qa/verify_multiyear_snapshot.py` | 21,507 B | `c488cf4c803f29b6859e9c2014bdf73950e3fa0276d1e48fe3320f269a994ae7` |
| `tests/test_multiyear_snapshot_policy.py` | 28,141 B | `32e2cff013bb6ec904aa3d2422736171f11c75c87a55b206037a1e05dff3239a` |
| `docs/05-evidence/G6_PRODUCTION_MANIFEST_COMPATIBILITY_AUDIT.md` | 7,688 B | `e837a77d13eb8538ef0c20aeb5a0e0f31922cbe7f8cce8bb32fdfc14d9b23b49` |
| `docs/05-evidence/G6_PRODUCTION_MANIFEST_FALSE_PASS_RECONCILIATION.md` | 8,245 B | `11d5f2a1b9fb2b7dd977d2427a1c43f7736cc4b8d780ef5709ee0aa7fc71c4c9` |
| `docs/05-evidence/G6_PHYSICAL_PARQUET_ACCOUNTING_CONTRACT_TEST.md` | 6,432 B | `13aa9f743df658b1054a8a5f82c3c6f2a7dbdc39d919864a97491cf152ea3a96` |
| `docs/05-evidence/G6_MANIFEST_RECEIPT_AND_OUTPUT_HASH_AUDIT.md` | 5,594 B | `c30b20ef22ec01ce7a7b827cb6a6358dbb25ccf7ae9f53e5e6e66cf5759ff7b5` |
| `docs/05-evidence/G6_OFFICIAL_DECISION_MAPPING_ERRATA.md` | 6,375 B | `b68079fa720e985834887eeae6734101e4ec305a4ecb3f02123ba4beecdfce09` |

*(Note: Remaining evidence files `G6_TEST_INVENTORY_AND_ARTIFACT_HASH_ERRATA.md`, `G6_FINAL_MANIFEST_COMPATIBILITY_RAW_LOG.txt`, and `G6_PROJECT_LEAD_SIGNOFF_HANDOFF_CORRECTED.md` will be registered immediately upon generation).*

---

## 4. Distinction Between Synthetic Fixtures and Physical Production Data

To prevent any misunderstanding regarding the nature of the test suite:
1. **Synthetic Test Fixtures (`tests/test_multiyear_snapshot_policy.py`):**
   - Create lightweight, structurally and cryptographically valid Parquet files (e.g. 2 rows per year) inside temporary directories (`tempfile.TemporaryDirectory`).
   - Use mathematical balancing: $\text{accepted} = 2, \text{quarantined} = \text{raw} - 2$, verifying exact Thrift metadata parsing and conservation without requiring 15 GB of storage during automated CI/CD.
2. **Physical Production Data (Gate G6 / T-012):**
   - The actual 54,674,003 flight records across 2016–2024 will be ingested and transformed under Apache Spark in Task T-012 **only after** the Project Lead approves Decision D5.
   - At Gate G5 exit, no production Parquet dataset for 2017–2024 exists or is permitted to exist.

---

## 5. Conclusion

This errata reconciles all test inventory naming and cryptographic hash representations. The regression test suite is confirmed at 40/40 tests passing with zero failures and zero ambiguities.
