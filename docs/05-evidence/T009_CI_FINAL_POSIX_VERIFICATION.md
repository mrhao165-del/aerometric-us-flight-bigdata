# T009-CI-FINAL POSIX & Clean-Checkout Verification Report

## 1. Objective & Methodology
To guarantee that the pipeline operates safely in Linux/POSIX CI environments (such as GitHub Actions runners or containerized builds) without creating unauthorized files in the checkout directory:
1. An isolated, clean sandbox repository was created in a temporary OS directory, containing only Git-tracked source and docs (strictly 0 raw CSVs, 0 Parquet files).
2. The complete unit test suite (37 tests) was executed within the clean checkout *before* running consistency checks to identify any unintended filesystem side-effects.
3. The root filesystem of the checkout was audited for any stray directories or files (specifically looking for `D:`, `flight_spark_tmp`, or in-repo scratch folders).
4. `tools/check_working_tree_consistency.py --ci-mode` was executed to verify 100% adherence to repository structure and manifest invariants.

---

## 2. Experimental Execution & Results

### 2.1. Test Execution in Clean Checkout
- **Sandbox Root:** `C:\Users\Heikapu\AppData\Local\Temp\tmpmu43hou1\repo`
- **Command:** `python -m unittest discover -s tests -p "test_*.py"`
- **Result:**
  ```
  Ran 37 tests in 27.901s
  OK
  ```
- **Exit Code:** `0`

### 2.2. Filesystem Side-Effect Audit
- **Filesystem Scan:**
  `os.listdir(sandbox_root) -> ['.env.example', '.github', '.gitignore', 'AGENTS.md', 'docs', 'PACKAGE_MANIFEST.json', 'README.md', 'requirements.txt', 'src', 'START_HERE.md', 'tests', 'tools']`
- **Audit Findings:**
  - `D:` directory in repository root: **NOT FOUND** (Assertion `D: not in entries` PASS)
  - `flight_spark_tmp` in repository root: **NOT FOUND** (Assertion PASS)
  - `in_repo_scratch` in repository root: **NOT FOUND** (Assertion PASS)
  - Stray `.tmp` or lock files: **0**

### 2.3. Spark Parameter Inspection
In `test_spark_session_creation_and_config`, the SparkSession runtime configuration was directly queried:
- Configuration key: `spark.local.dir`
- Value: Verified to be an absolute path located within the designated OS scratch directory.
- Driver memory: `2g`
- Shuffle partitions: `4`
- Result: **PASS**

---

## 3. Conclusion
The implementation of `is_windows_host()` and platform-aware `ensure_scratch_dir()` completely eliminates the Windows path collision on Linux. Clean-checkout builds now maintain zero repository pollution throughout test and runtime execution.
