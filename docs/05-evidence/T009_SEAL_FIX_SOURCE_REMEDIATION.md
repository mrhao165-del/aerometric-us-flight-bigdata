# T009-SEAL-FIX Source Remediation Report

## 1. Scope of Remediation
In accordance with `TARGETED FIX — FAILING TESTS FIRST — NO UNRELATED REFACTORING`, modifications were strictly restricted to the four files identified in the audit:
1. `src/flight_pipeline/storage/publication.py`
2. `tests/test_publication_safety.py`
3. `tools/check_working_tree_consistency.py`
4. `.github/workflows/ci.yml`

---

## 2. Technical Modifications

### 2.1 Streaming SHA-256 (`src/flight_pipeline/storage/publication.py`)
- **Added Function:**
  ```python
  def compute_file_sha256(p: Path, chunk_size: int = 65536) -> str:
      """
      Compute SHA-256 hash of a file using streaming fixed-size blocks (default 64KB).
      Avoids reading large Parquet files completely into RAM.
      """
      if not p.is_file():
          raise FileNotFoundError(f"Cannot compute hash for non-existent file: {p}")
      h = sha256()
      with open(p, "rb") as f:
          while True:
              chunk = f.read(chunk_size)
              if not chunk:
                  break
              h.update(chunk)
      return h.hexdigest()
  ```
- **Replaced Lines:** Replaced `sha256(f.read_bytes()).hexdigest()` in staging inventory (Line 254) and promoted verification (Line 316) with `compute_file_sha256()`.

### 2.2 Pointer Read Exception Safety & Retry (`publication.py`)
- **`get_current_pointer()`:** Enhanced with a 3-attempt retry loop with linear backoff (50ms base) to absorb transient Windows NTFS file lock contention. Explicitly raises `OSError` if persistent IO errors occur.
- **Step 6 Exception Handling:**
  - Wrapped `current_pointer = self.get_current_pointer()` in `try-except OSError as exc`.
  - If `read_err is not None` or `current_pointer != run_id`:
    1. Executes atomic rollback via `_atomic_write_pointer(previous_pointer, ...)`.
    2. Reads back the pointer to verify rollback success on disk.
    3. If rollback restored `previous_pointer`: returns `status="FAILED_POINTER_READ_VERIFICATION"` (if read failed) or `status="FAILED_POINTER_VERIFICATION"` (if value mismatched).
    4. If rollback failed or could not be verified: returns `status="FAILED_POINTER_VERIFICATION_ROLLBACK_ERROR"`.
    5. Returns `success=False`, `aborted_step=6`.
    6. Preserves staging and versioned targets intact for forensic inspection.

### 2.3 CI Clean-Checkout Support (`tools/check_working_tree_consistency.py`)
- Updated `run_consistency_check(root_dir: Path, ci_mode: bool = False)` and `main()` to accept `--ci-mode` / `--repo-only`.
- In `ci_mode`: Asserts `len(raw_data_files) == 0`, explicitly validating that raw CSV files are not checked into Git.
- In default mode: Asserts `len(raw_data_files) == 9`, validating local workstation data completeness.

### 2.4 CI Workflow Update (`.github/workflows/ci.yml`)
- Updated consistency step:
  ```yaml
  - name: Run working-tree consistency verifier (CI clean-checkout mode)
    run: |
      python tools/check_working_tree_consistency.py --ci-mode
  ```
