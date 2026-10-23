# G6_R05_RECURSIVE_PARQUET_INVENTORY_AUDIT.md
## Technical Audit and Forensic Resolution of Finding R05 (Non-Recursive Parquet Discovery)

**Project:** US Flight Performance Analysis 2016–2024  
**Date:** 2026-10-21  
**Gate Status:** G5 = IN_PROGRESS (TECHNICALLY READY) | G6 = NOT_STARTED / BLOCKED  
**Auditor:** Principal Big Data QA Engineer & PySpark Release Reliability Engineer  
**Component:** `tools/qa/verify_multiyear_snapshot.py`  
**Finding Classification:** R05 (Physical Parquet Discovery Incompleteness / Silent File Bypass Vulnerability)

---

## 1. Executive Summary & Defect Description

During independent verification of review package `G6_RELEASE_VALIDATOR_STRICT_FINAL_REVIEW.zip` (SHA-256 `060800bc51c22d0ca8db3277594a23e16610794efad898a5ee236f20258daeed`), the Independent Evidence Auditor identified a fundamental structural asymmetry between how `IngestionCoordinator` records physical Parquet files and how `verify_multiyear_snapshot.py` discovers them on disk.

### Writer Implementation vs. Validator Implementation (Pre-Fix)

- **Production Writer (`src/flight_pipeline/ingestion/coordinator.py`):**
  When registering published artifacts in `RunManifest.outputs`, the coordinator executes a full recursive traversal across the published directory:
  ```python
  # coordinator.py lines ~940-960
  parquet_files = sorted(list(published_dir.rglob("*.parquet")))
  ```
  This naturally captures hierarchical, partitioned structures such as `year=2019/month=1/part-00000.parquet`, `date=2019-01-01/part-00001.parquet`, or arbitrary multi-level subdirectories.

- **Pre-Fix Validator (`tools/qa/verify_multiyear_snapshot.py`):**
  The multi-year dataset validator attempted to discover physical Parquet files using a non-recursive or single-fallback approach:
  ```python
  # Old logic in verify_multiyear_snapshot.py:
  parquet_files = sorted(list(physical_dir.glob("*.parquet")))
  if not parquet_files:
      parquet_files = sorted(list(physical_dir.glob("*/*.parquet")))
  ```

### Vulnerability Analysis & Counterexamples

1. **Mixed Root and Nested Partitions:** If a run directory contains a top-level Parquet file (`physical_dir/part-000.parquet`) alongside nested partition directories (`physical_dir/month=1/part-001.parquet`), `physical_dir.glob("*.parquet")` returned a non-empty list containing only `part-000.parquet`. The validator never entered the fallback branch `*/*.parquet`, silently omitting nested partition files from checksum validation, row count aggregation, and schema inspection.
2. **Deep Partition Hierarchies (>= 2 Levels):** In partitioned datasets organized into two or more levels of directory hierarchy (e.g., `physical_dir/year=2019/month=1/part-000.parquet`), the fallback `*/*.parquet` only inspected one level deep (`physical_dir/*/`), completely missing files located 2 or more levels below `physical_dir`.
3. **Silent Accounting Inconsistency:** Because unlisted files located in deep directories were completely ignored by `glob()`, malicious or corrupted data could reside inside the physical run directory without triggering `UNLISTED_PHYSICAL_PARQUET_DETECTED`.

---

## 2. Architectural Remediation: `discover_physical_parquet_files`

To achieve strict 1:1 parity with the production writer while maintaining fail-closed security invariants, `tools/qa/verify_multiyear_snapshot.py` was refactored with a dedicated discovery engine: `discover_physical_parquet_files(physical_dir)`.

### Core Invariants Enforced

1. **Deep Recursive Traversal (`os.walk`):** Traverses the entire directory subtree under `physical_dir` to arbitrary depth, collecting every file whose extension matches `.parquet` (case-insensitive).
2. **Fail-Closed Symlink, Junction & Reparse Point Guard:**
   - Evaluates `is_symlink_or_reparse(physical_dir)` before starting.
   - For every directory (`root`), child directory (`sub_d`), and candidate file (`f_p`), verifies that no symlink, junction, or NTFS reparse point exists.
   - If any symlink or reparse point is encountered anywhere in the directory hierarchy, discovery immediately fails closed with `UNSAFE_SYMLINK_DETECTED`.
3. **Strict Path Confinement:** Every discovered Parquet file must resolve strictly inside `physical_dir.resolve()` via `Path.resolve().relative_to(physical_dir.resolve())`. Any path traversal or junction escape fails closed.
4. **Canonical POSIX Path Sorting:** Discovered files are deterministically sorted by their canonical POSIX relative path from `physical_dir`:
   ```python
   parquet_files_sorted = sorted(
       parquet_files,
       key=lambda p: p.resolve().relative_to(physical_dir_resolved).as_posix()
   )
   ```
   This guarantees identical ordering across Windows NTFS, Linux ext4, and macOS APFS, eliminating basename collisions across distinct subfolders.
5. **Fail-Closed on Empty Run:** If `parquet_files` is empty, returns `EMPTY_RUN_DIRECTORY_OR_NO_PARQUET`.

### Implementation Code (`tools/qa/verify_multiyear_snapshot.py`)

```python
def discover_physical_parquet_files(
    physical_dir: Path,
) -> Tuple[Optional[List[Path]], Optional[str], Optional[str]]:
    """
    Recursively discover all Parquet files within physical_dir (Finding R05).
    Enforces fail-closed detection of symlinks, junctions, and reparse points.
    Returns (parquet_files_sorted, error_status, error_message).
    """
    if is_symlink_or_reparse(physical_dir):
        return None, "UNSAFE_SYMLINK_DETECTED", f"Curated directory itself is a symlink or reparse point: {physical_dir}"

    parquet_files: List[Path] = []
    physical_dir_resolved = physical_dir.resolve()

    for root, dirs, files in os.walk(str(physical_dir)):
        root_p = Path(root)
        if is_symlink_or_reparse(root_p):
            return None, "UNSAFE_SYMLINK_DETECTED", f"Curated subdirectory is a symlink or reparse point: {root_p}"

        for d in dirs:
            sub_d = root_p / d
            if is_symlink_or_reparse(sub_d):
                return None, "UNSAFE_SYMLINK_DETECTED", f"Curated child directory is a symlink or reparse point: {sub_d}"

        for f in files:
            f_p = root_p / f
            if is_symlink_or_reparse(f_p):
                return None, "UNSAFE_SYMLINK_DETECTED", f"File is a symlink or reparse point: {f_p}"

            if f.lower().endswith(".parquet"):
                try:
                    f_p.resolve().relative_to(physical_dir_resolved)
                except (ValueError, RuntimeError):
                    return None, "UNSAFE_SYMLINK_DETECTED", f"Parquet file {f_p} resolves outside {physical_dir_resolved}"
                parquet_files.append(f_p)

    if not parquet_files:
        return None, "EMPTY_RUN_DIRECTORY_OR_NO_PARQUET", f"Directory {physical_dir} contains no .parquet files"

    parquet_files_sorted = sorted(
        parquet_files,
        key=lambda p: p.resolve().relative_to(physical_dir_resolved).as_posix()
    )
    return parquet_files_sorted, None, None
```

---

## 3. Integration with Multi-Year & Single-Run Invariants

The recursive discovery function is integrated at two critical inspection points:
1. **Multi-Year Dataset Registry Validation (`validate_multiyear_snapshot_registry`):** Replaces legacy `glob` checks in Invariant 6 and Invariant 10, ensuring all files at all depths are matched 1:1 against `RunManifest.outputs`.
2. **Single Annual Run Validation (`validate_single_annual_run`):** Ensures that standalone annual execution runs verify every physical file across all partition folders before validating `ExecutionReceipt`.

---

## 4. Verification and Audit Verdict

- **Vulnerability Closed:** Incomplete discovery via non-recursive `glob` has been eliminated.
- **Fail-Closed Protection:** Any unlisted Parquet file at any depth triggers `UNLISTED_PHYSICAL_PARQUET_DETECTED`.
- **Status:** **R05_FULLY_REMEDIATED_AND_VERIFIED**.
