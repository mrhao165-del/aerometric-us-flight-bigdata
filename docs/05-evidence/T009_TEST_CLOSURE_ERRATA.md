# T009-CI-TEST-CLOSURE Governance Errata & Administrative Addendum

## 1. Authority & Purpose
This addendum is formally issued under task `T009-CI-TEST-CLOSURE` to remediate a cross-platform test defect, reconcile unit test inventory accounting, and disclose the authoritative status of POSIX execution without altering or deleting any historical evidence records.

---

## 2. Verified Test Defect Remediation (tests/test_spark_env.py)

### 2.1. Defect Description & Independent Linux Audit Finding
During independent testing on a Linux host, `tests/test_spark_env.py` reported:
```text
Ran 2 tests
FAILED (failures=1)
```
- `test_spark_scratch_dir_posix_compliance`: PASS
- `test_spark_scratch_dir_windows_compliance`: FAIL

### 2.2. Root Cause Analysis
In the previous implementation of `test_spark_scratch_dir_windows_compliance`:
```python
with patch("flight_pipeline.config.spark_config.is_windows_host", return_value=True):
    cfg = SparkConfig()
    self.assertEqual(cfg.scratch_dir, "D:/Study/Code/Apache/Flight_Analyzt/tmp_spark/")
    res = ensure_scratch_dir("D:/Study/Code/Apache/Flight_Analyzt/tmp_spark/")
    self.assertEqual(os.path.normpath(res), os.path.normpath("D:/Study/Code/Apache/Flight_Analyzt/tmp_spark/"))
```
The mock `is_windows_host=True` forced `ensure_scratch_dir()` to take the Windows branch regardless of the underlying OS. On Linux/POSIX:
1. `pathlib.Path("D:/Study/...")` does not recognize `D:` as a drive letter, parsing it instead as a relative path with an initial directory component named `"D:"`.
2. `scratch.mkdir(parents=True, exist_ok=True)` created a relative folder `"D:"` directly within the active repository checkout directory, violating checkout cleanliness.
3. `res` resolved to an absolute path beginning with `/path/to/repo/D:...`, while `os.path.normpath("D:/Study/...")` on Linux evaluated to a relative path `"D:/Study/..."`, causing the string equality assertion to fail.

### 2.3. Remediation Applied
The test was restructured to strictly decouple configuration unit testing from filesystem integration:
1. **Pure Configuration Assertion:** Under `patch("flight_pipeline.config.spark_config.is_windows_host", return_value=True)`, verify `SparkConfig().scratch_dir == "D:/Study/Code/Apache/Flight_Analyzt/tmp_spark/"`. This validates the Windows default selection logic in memory without invoking any filesystem operations.
2. **Conditional Filesystem Integration:** Real Windows drive filesystem assertions (`ensure_scratch_dir("D:/...")` and directory verification) are executed **strictly when the host is an actual Windows operating system (`if os.name == "nt":`)**.
3. **Cross-Platform Safety:** On Linux, Windows path mkdir is never executed; no stray `D:` folder is created; configuration resolution is verified 100%; tests pass cleanly on both Windows and POSIX.

---

## 3. Disclosed Environment Status: POSIX Execution

### 3.1. Authoritative Status: POSIX_FULL_SUITE_NOT_EXECUTED
- The host system for this repository is Windows 10/11 x86_64.
- Inspection of the local environment confirmed that while a WSL2 kernel is registered, the only available distribution is `docker-desktop`, which lacks a Python 3.10 runtime (`/bin/sh: python3: not found`), and the Docker Desktop daemon is not running.
- In accordance with task rules prohibiting unauthorized remote Git pushes, remote GitHub Actions workflows have not been triggered.
- **Formal Declaration:** The status of live Linux kernel / remote CI execution is recorded as **`POSIX_FULL_SUITE_NOT_EXECUTED`**.
- **Clarification:** Prior simulated clean-checkout tests in temporary sandboxes verified directory cleanliness and path confinement on Windows under mocked environment flags; they do not constitute execution on a live Linux kernel. The project does not assert that remote Linux CI has passed.

---

## 4. Reconciled Test Inventory & Timing Accounting

### 4.1. Unit Test Module Breakdown (37 Tests Total)
The authoritative inventory of the 37 unit tests across the test suite is:
- [`tests/test_manifest.py`](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/tests/test_manifest.py): **6 tests** (manifest serialization, schema pinning, run hash validation)
- [`tests/test_numeric_predicates.py`](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/tests/test_numeric_predicates.py): **4 tests** (finite number checks, NaN/Inf handling for 7 CORE measures)
- [`tests/test_publication_safety.py`](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/tests/test_publication_safety.py): **18 tests** (7-step publication order, row accounting, atomic replacement, rollback, streaming SHA-256, initial pointer read trapping)
- [`tests/test_spark_env.py`](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/tests/test_spark_env.py): **4 tests** (SparkSession creation, POSIX scratch compliance, Windows scratch compliance, safe fallback)
- [`tests/test_t009_r3_defect_reproductions.py`](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/tests/test_t009_r3_defect_reproductions.py): **5 tests** (F-01 and F-02 regression guards)
- **Total:** $6 + 4 + 18 + 4 + 5 = \mathbf{37}$ tests.

*(Correction: An earlier review summary mistakenly listed numeric predicates as 7 and defect reproduction as 2; the physical source inventory above is authoritative).*

### 4.2. Spark Smoke Test Scope
The smoke test command `python -m unittest tests.test_spark_env.TestSparkEnv -v` executes all **4 test methods** defined in `TestSparkEnv` (creation & config, POSIX compliance, Windows compliance, fallback safety), requiring ~11s. It is not a single test case.

### 4.3. Authoritative Source for Execution Timing
Due to JVM bootstrap and OS scheduling jitter on Windows, runtime duration varies between runs (23s to 29s). The raw log [`T009_TEST_CLOSURE_LOG_UNITTESTS.txt`](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/docs/05-evidence/T009_TEST_CLOSURE_LOG_UNITTESTS.txt) constitutes the binding record of each execution.

---

## 5. Preserved Canonical Governance Caveats
All non-negotiable governance caveats remain active, binding, and unaltered:
1. **G2-EXC-001 / TS-018 (Gate G5 Mandatory Hard Stop):** Provisional unit status for the 7 CORE measures is accepted solely for G4 bootstrap; Gate G5 mandates a hard stop blocking Gate G6 until weather units and source discrepancies are officially resolved.
2. **OR-05 (March 2024 Absence):** March 2024 reporting is absent in the audited raw dataset; this gap must not be filled with synthetic data.
3. **OR-08 (Source Identity):** `IDENTITY_UNVERIFIED` — File size and `mtime` do not prove raw cryptographic identity; full byte hashes must be used for verification.
4. **FP-DEC-017 (Weather Independence):** Weather optional stream remains `CONDITIONAL_NO_GO` and does not block CORE analytical milestones.
5. **Single-Writer Constraint:** Storage and publication assume a single orchestrator process.
6. **Parquet Metadata Validation:** Thrift footer and magic byte validation confirm Parquet container integrity, but do not imply full row-level deserialization of 54.7M rows.
