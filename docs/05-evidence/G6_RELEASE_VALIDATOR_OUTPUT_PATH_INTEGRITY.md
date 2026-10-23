# G6_RELEASE_VALIDATOR_OUTPUT_PATH_INTEGRITY.md
## Architectural Audit of Output Path Confinement, Namespace Isolation, and Parquet Discovery

**Project:** US Flight Performance Analysis 2016–2024  
**Date:** 2026-10-21  
**Gate Status:** Gate G5 = IN_PROGRESS (TECHNICALLY READY), Gate G6 = NOT_STARTED / BLOCKED  
**Author:** Production Data Release Architect & Principal Big Data Engineer  
**Scope:** Output path resolution in `tools/qa/verify_multiyear_snapshot.py` vs `src/flight_pipeline/ingestion/coordinator.py`

---

## 1. Context & Production Writer Contract

In the production PySpark ingestion pipeline (`src/flight_pipeline/ingestion/coordinator.py`, lines 990–996), upon successful atomic pointer switch, published Parquet files are recorded into the `RunManifest` via:

```python
published_dir = Path(pub_result.published_path)
for pf in sorted(published_dir.rglob("*.parquet")):
    manifest.record_output(
        path=pf.relative_to(self.base_data_dir).as_posix(),
        bytes_count=pf.stat().st_size,
        sha256_hash=compute_file_sha256(pf),
    )
```

The canonical storage convention produces paths formatted relative to `base_data_dir`, e.g.:
`curated/runs/run_2019_v1/part-00000-2019.parquet` or `curated/runs/run_2019_v1/quarter=1/part-0.parquet`.

---

## 2. Forensic Analysis of Finding R02

### 2.1 The Vulnerability of Basename Indexing
The legacy snapshot validator extracted the file basename via `Path(out_path_str).name` and indexed outputs as:
```python
outputs_inventory[out_p.name] = out_item
```
This design introduced two severe failure modes:
1. **Cross-Run Substitution:** An output declared as `curated/runs/run_2020_v1/part-2019.parquet` was stored under key `"part-2019.parquet"`. When checking physical presence, the validator checked `physical_dir / fname` (i.e. `run_2019_v1/part-2019.parquet`). If a file with the same basename existed in `run_2019_v1`, the cross-run reference in the manifest was ignored, yielding a false-positive release certification.
2. **Namespace Collision in Partitioned Datasets:** When Spark writes partitioned outputs (e.g., `quarter=1/part-0.parquet` and `quarter=2/part-0.parquet`), both files share the basename `"part-0.parquet"`. The dictionary key collision overwrote one entry with another, leading to unlisted file failures or loss of cryptographic audit trails.

---

## 3. The Strict Path Resolution & Confinement Engine

To guarantee mathematical proof of path identity and prevent escape, `tools/qa/verify_multiyear_snapshot.py` was refactored with the following invariant rules:

### Rule 1: Multi-Root Resolution
Every declared path `out_path_str` is normalized and resolved:
```python
norm_out_str = out_path_str.replace("\\", "/")
if norm_out_str.startswith("curated/") or norm_out_str.startswith("staging/") or norm_out_str.startswith("runs/"):
    target_file = (base_dir / norm_out_str).resolve()
else:
    target_file = (physical_dir / norm_out_str).resolve()
```

### Rule 2: Strict Physical Run Confinement
The resolved path must be strictly contained within `physical_dir.resolve()`:
```python
try:
    rel_to_physical = target_file.relative_to(physical_dir.resolve())
    if target_file == physical_dir.resolve():
        return SnapshotValidationResult(valid=False, status="OUTPUT_PATH_IS_DIRECTORY", ...)
except (ValueError, RuntimeError):
    return SnapshotValidationResult(
        valid=False,
        status="OUTPUT_PATH_RUN_MISMATCH",
        error_message=f"Year {year} manifest output path {out_path_str!r} resolves to {target_file} outside physical_dir {physical_dir.resolve()}",
    )
```
If an output references any path outside the verified run directory (such as another run, another year, or a parent directory), it fails closed immediately with `OUTPUT_PATH_RUN_MISMATCH`.

### Rule 3: Canonical Relative Path Indexing
The inventory key is the canonical POSIX path relative to the physical run directory:
```python
canon_rel = rel_to_physical.as_posix()
```
For `curated/runs/run_2019_v1/quarter=1/part-0.parquet`, `canon_rel` is `"quarter=1/part-0.parquet"`.
For `curated/runs/run_2019_v1/quarter=2/part-0.parquet`, `canon_rel` is `"quarter=2/part-0.parquet"`.
Both entries coexist without collision.

### Rule 4: Duplicate Entry Prevention
If `canon_rel` is already present in `outputs_inventory`, the validator immediately fails closed with `DUPLICATE_OUTPUT_ENTRY`.

### Rule 5: Bi-Directional 1:1 Parquet Reconciliation
All physical Parquet files discovered via recursive scan `physical_dir.rglob("*.parquet")` are mapped by their canonical relative path:
```python
physical_parquet_map = {
    pf.resolve().relative_to(physical_dir.resolve()).as_posix(): pf
    for pf in parquet_files
}
physical_parquet_rels = set(physical_parquet_map.keys())
declared_rels = set(outputs_inventory.keys())
```
The validator enforces two strict disjoint set checks:
1. `unlisted = physical_parquet_rels - declared_rels`: If non-empty, fails closed with `UNLISTED_PHYSICAL_PARQUET_DETECTED`.
2. `missing = declared_rels - physical_parquet_rels`: If non-empty, fails closed with `MANIFEST_FILE_NOT_FOUND`.

---

## 4. Verification & Negative Test Evidence

The path confinement engine was verified against dedicated positive and negative test cases in `tests/test_multiyear_snapshot_policy.py`:

1. **Cross-Run Attack (`test_neg_r02a_cross_run_output_path_fails_closed`):**
   - Injected `curated/runs/run_2020_v1/part-00000-2019.parquet` into year 2019 manifest.
   - Result: Failed closed with `OUTPUT_PATH_RUN_MISMATCH`.
2. **Duplicate Entry Attack (`test_neg_r02b_duplicate_output_entry_fails_closed`):**
   - Declared identical output entry twice.
   - Result: Failed closed with `DUPLICATE_OUTPUT_ENTRY`.
3. **Partitioned Hierarchy Preservation (`test_pos_r02c_subpartition_distinct_basenames_passes`):**
   - Created `quarter=1/part-0.parquet` and `quarter=2/part-0.parquet`.
   - Result: Successfully validated both partitions with status `VALID_SNAPSHOT_REGISTRY`.
4. **Subpartition Path Mismatch (`test_neg_r02d_subpartition_path_mismatch_fails_closed`):**
   - Manifest declared `quarter=2/part-0.parquet` while physical file was at `quarter=1/part-0.parquet`.
   - Result: Failed closed with `UNLISTED_PHYSICAL_PARQUET_DETECTED`.

---

## 5. Architectural Verdict

The output path validation engine now enforces strict mathematical namespace confinement, eliminating cross-run injection, duplicate output evasion, and subpartition collision vulnerabilities.
