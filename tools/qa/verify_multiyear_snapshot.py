"""
tools/qa/verify_multiyear_snapshot.py

Multi-Year Dataset Registry Validator and Snapshot Path Resolver.
Enforces Findings G6-C03, S01, S02, S03, and Production Manifest Contract Compatibility (M01, M02, M03).
Conforms to ARCHITECTURE.md, DATA_CONTRACT.md (DC-11, DC-12), and G6_C03_MULTIYEAR_SNAPSHOT_AND_VERSION_POLICY.md.

Fail-Closed Invariants:
1. All 9 survey years (2016–2024) must be present.
2. Every path must resolve strictly inside `<base_data_dir>/curated/runs/`.
3. Absolute paths, path traversal ('..'), and root-escaping symlinks/reparse points are strictly rejected.
4. selected_run_id must conform to SafePublisher validation and match directory basename.
5. Curated run directories must NOT be empty and MUST contain valid Parquet files.
6. A valid published run_manifest.json must exist, match selected_run_id, and declare coverage for the audited year in configuration.years.
7. Publication status in manifest must strictly equal 'PUBLISHED' (rejecting 'FAILED', 'ABORTED', 'IN_PROGRESS', or unknown status).
8. All outputs declared in manifest must exist on disk, be strictly confined inside run directory, have mandatory non-negative bytes and 64-char hex sha256 (no placeholders), and match exact bytes and SHA-256 (R02, R03).
9. Manifest output paths preserve full relative path and directory structure without basename collision; cross-run outputs or duplicate entries fail closed (R02).
10. No physical Parquet files may contribute to the snapshot that are unlisted in manifest outputs (M02).
11. Physical Parquet Thrift metadata is inspected: magic bytes, Thrift footers, column definitions, and exact row counts.
12. Parquet schema must conform to DATA_CONTRACT.md: must contain 7 core delay/time measures, core flight identifiers, and NO forbidden columns.
13. Physical Parquet row count must match certified accepted_row_count across manifest and registry (physical == manifest_accepted == registry_accepted).
14. Row accounting under DC-11 must balance for every year: raw_row_count == accepted + quarantined + rejected with valid non-negative integer types.
15. Manifest row accounting must reconcile 1:1 with registry row accounting.
16. ExecutionReceipt is mandatory by default for production verification (R01). Receipt must be strictly validated against ExecutionReceipt.to_dict(): run_id, task_id, published_path, manifest_path, manifest_bytes, manifest_sha256, row_accounting, and pipeline_state/publication_status == 'PUBLISHED' (R04).
17. Multi-year runs must have verified partition boundaries per year or fail closed.
18. raw_row_count for each year must match canonical audited source inventory; sum of RAW == 54,674,003 (accepted is dynamically aggregated).
19. Year 2024 must declare source_coverage_status = 'PARTIAL' (OR-05).
"""

import argparse
from dataclasses import asdict, dataclass, field
import hashlib
import json
import os
from pathlib import Path
import re
import sys
from typing import Any, Dict, List, Optional, Sequence, Set, Tuple, Union

import pyarrow.parquet as pq

ROOT_DIR = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT_DIR / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from flight_pipeline.ingestion.schema import (
    CANONICAL_COLUMN_NAMES,
    FORBIDDEN_COLUMNS,
    SEVEN_CORE_MEASURES,
)
from flight_pipeline.ingestion.source_validator import (
    AUDITED_SOURCE_INVENTORY,
    TOTAL_AUDITED_ROWS,
    is_symlink_or_reparse,
)
from flight_pipeline.storage.publication import (
    RUN_ID_REGEX,
    compute_file_sha256,
    is_valid_parquet_file,
    validate_run_id,
)

CANONICAL_YEARS: Tuple[int, ...] = tuple(range(2016, 2025))


@dataclass(frozen=True)
class AnnualSnapshotDetail:
    year: int
    selected_run_id: str
    physical_path: str
    parquet_files_count: int
    raw_row_count: int
    accepted_row_count: int
    quarantined_row_count: int
    rejected_row_count: int
    source_coverage_status: str
    manifest_path: str
    schema_fingerprint: Optional[str] = None
    receipt_path: Optional[str] = None
    physical_parquet_rows: Optional[int] = None


@dataclass(frozen=True)
class SnapshotValidationResult:
    valid: bool
    status: str
    error_message: Optional[str] = None
    selected_paths: Optional[List[str]] = None
    total_raw_rows: Optional[int] = None
    total_accepted_rows: Optional[int] = None
    total_quarantined_rows: Optional[int] = None
    total_rejected_rows: Optional[int] = None
    annual_details: Optional[Dict[int, Dict[str, Any]]] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _is_safe_path_confinement(target_path: Path, parent_root: Path) -> bool:
    """Check that target_path resolves strictly inside parent_root without escape."""
    try:
        resolved_target = target_path.resolve()
        resolved_root = parent_root.resolve()
        resolved_target.relative_to(resolved_root)
        return resolved_target != resolved_root
    except (ValueError, RuntimeError):
        return False


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


def validate_multiyear_snapshot_registry(
    registry_path: Optional[Union[str, Path]] = None,
    base_data_dir: Union[str, Path] = "data",
    expected_years: Tuple[int, ...] = CANONICAL_YEARS,
    verify_parquet_metadata: bool = True,
    verify_file_checksums: bool = True,
    verify_physical_row_counts: bool = True,
    verify_parquet_schema: bool = True,
    require_execution_receipt: bool = True,
    registry_data: Optional[Dict[str, Any]] = None,
) -> SnapshotValidationResult:
    """
    Perform deep fail-closed validation of multi_year_dataset_registry.json.
    Integrates production RunManifest, ExecutionReceipt, Parquet Thrift metadata,
    and DC-11/12 row accounting.
    """
    base_dir = Path(base_data_dir).resolve()
    curated_runs_root = (base_dir / "curated" / "runs").resolve()

    if registry_data is not None:
        data = registry_data
        reg_p = Path(registry_path).resolve() if registry_path else None
    elif isinstance(registry_path, dict):
        data = registry_path
        reg_p = None
    elif registry_path is not None:
        reg_p = Path(registry_path).resolve()
        if not reg_p.is_file():
            return SnapshotValidationResult(
                valid=False,
                status="MISSING_REGISTRY_FILE",
                error_message=f"Registry file does not exist: {reg_p}",
            )
        try:
            data = json.loads(reg_p.read_text(encoding="utf-8"))
        except Exception as exc:
            return SnapshotValidationResult(
                valid=False,
                status="CORRUPT_REGISTRY_JSON",
                error_message=f"Registry JSON is corrupt or unparseable: {exc}",
            )
    else:
        return SnapshotValidationResult(
            valid=False,
            status="MISSING_REGISTRY_INPUT",
            error_message="Neither registry_path nor registry_data provided",
        )

    if not isinstance(data, dict):
        return SnapshotValidationResult(
            valid=False,
            status="INVALID_REGISTRY_STRUCTURE",
            error_message="Registry root must be a JSON object",
        )

    years_dict = data.get("years")
    if not isinstance(years_dict, dict):
        return SnapshotValidationResult(
            valid=False,
            status="MISSING_YEARS_MAPPING",
            error_message="Registry missing required 'years' object mapping",
        )

    try:
        present_years = sorted([int(k) for k in years_dict.keys()])
    except ValueError:
        return SnapshotValidationResult(
            valid=False,
            status="INVALID_YEAR_KEY",
            error_message="All year keys in 'years' must be convertible to integers",
        )

    # Invariant 1: Completeness of expected survey years
    if present_years != list(expected_years):
        missing = sorted(list(set(expected_years) - set(present_years)))
        extra = sorted(list(set(present_years) - set(expected_years)))
        return SnapshotValidationResult(
            valid=False,
            status="YEARS_COMPLETENESS_ERROR",
            error_message=f"Registry years mismatch: missing={missing}, extra={extra}",
        )

    seen_physical_dirs: Set[str] = set()
    selected_paths: List[str] = []
    annual_details: Dict[int, Dict[str, Any]] = {}

    tot_raw = 0
    tot_accepted = 0
    tot_quarantined = 0
    tot_rejected = 0

    for year in expected_years:
        entry = years_dict.get(str(year))
        if not isinstance(entry, dict):
            return SnapshotValidationResult(
                valid=False,
                status="INVALID_YEAR_ENTRY",
                error_message=f"Year {year} entry is not a dictionary",
            )

        # Invariant 2: Validate selected_run_id format
        run_id = entry.get("selected_run_id")
        if not isinstance(run_id, str) or not run_id.strip():
            return SnapshotValidationResult(
                valid=False,
                status="MISSING_RUN_ID",
                error_message=f"Year {year} missing valid selected_run_id string",
            )
        run_id = run_id.strip()

        if not RUN_ID_REGEX.match(run_id) or any(c in run_id for c in ("..", "/", "\\", ":")):
            return SnapshotValidationResult(
                valid=False,
                status="INVALID_RUN_ID_FORMAT",
                error_message=f"Year {year} selected_run_id {run_id!r} violates run_id naming rules",
            )

        # Invariant 3: Path containment & security check
        rel_curated_path = entry.get("relative_curated_path")
        if not isinstance(rel_curated_path, str) or not rel_curated_path.strip():
            return SnapshotValidationResult(
                valid=False,
                status="MISSING_CURATED_PATH",
                error_message=f"Year {year} missing relative_curated_path",
            )
        rel_curated_path = rel_curated_path.strip()

        # Reject absolute paths or traversal sequences
        if Path(rel_curated_path).is_absolute() or ".." in Path(rel_curated_path).parts:
            return SnapshotValidationResult(
                valid=False,
                status="PATH_TRAVERSAL_DETECTED",
                error_message=f"Year {year} path contains traversal or is absolute: {rel_curated_path!r}",
            )

        physical_dir = (base_dir / rel_curated_path).resolve()
        if not _is_safe_path_confinement(physical_dir, curated_runs_root):
            return SnapshotValidationResult(
                valid=False,
                status="PATH_CONFINEMENT_ESCAPE",
                error_message=f"Year {year} path escapes curated runs root: {rel_curated_path!r}",
            )

        # Invariant 4: Directory name must match selected_run_id
        if physical_dir.name != run_id:
            return SnapshotValidationResult(
                valid=False,
                status="RUN_ID_DIRECTORY_MISMATCH",
                error_message=(
                    f"Year {year} selected_run_id {run_id!r} does not match directory basename {physical_dir.name!r}"
                ),
            )

        # Check symlink escaping
        if is_symlink_or_reparse(physical_dir):
            target_link = physical_dir.resolve()
            if not _is_safe_path_confinement(target_link, curated_runs_root):
                return SnapshotValidationResult(
                    valid=False,
                    status="SYMLINK_ESCAPE_DETECTED",
                    error_message=f"Year {year} path is a symlink/reparse point escaping root: {physical_dir}",
                )

        # Invariant 5: Physical directory existence and non-empty check
        if not physical_dir.is_dir():
            return SnapshotValidationResult(
                valid=False,
                status="PHYSICAL_DIR_NOT_FOUND",
                error_message=f"Year {year} curated run directory not found: {physical_dir}",
            )

        # Invariant 6: Deep Recursive Parquet discovery & Reparse/Symlink security audit (Finding R05)
        parquet_files, err_status, err_msg = discover_physical_parquet_files(physical_dir)
        if err_status is not None:
            return SnapshotValidationResult(
                valid=False,
                status=err_status,
                error_message=f"Year {year} {err_msg}",
            )

        # Invariant 7: Disjoint physical paths check
        norm_dir_str = str(physical_dir.as_posix())
        if norm_dir_str in seen_physical_dirs:
            return SnapshotValidationResult(
                valid=False,
                status="DUPLICATE_PHYSICAL_PATH",
                error_message=f"Year {year} physical path {norm_dir_str} is already assigned to another year",
            )
        seen_physical_dirs.add(norm_dir_str)
        selected_paths.append(norm_dir_str)

        # Invariant 8: Run Manifest discovery and validation (Finding M01, M02)
        candidate_manifests = [
            physical_dir / "run_manifest.json",
            base_dir / "metadata" / run_id / "run_manifest.json",
            base_dir / "curated" / "metadata" / run_id / "run_manifest.json",
        ]
        manifest_p = next((p for p in candidate_manifests if p.is_file()), None)

        if manifest_p is None:
            return SnapshotValidationResult(
                valid=False,
                status="MISSING_RUN_MANIFEST",
                error_message=f"Year {year} run {run_id} has no run_manifest.json in candidate locations",
            )

        try:
            m_data = json.loads(manifest_p.read_text(encoding="utf-8"))
        except Exception as exc:
            return SnapshotValidationResult(
                valid=False,
                status="CORRUPT_RUN_MANIFEST",
                error_message=f"Year {year} run_manifest.json is corrupt: {exc}",
            )

        if not isinstance(m_data, dict):
            return SnapshotValidationResult(
                valid=False,
                status="CORRUPT_RUN_MANIFEST",
                error_message=f"Year {year} run_manifest.json root is not a dictionary",
            )

        # Validate manifest run_id
        m_run_id = m_data.get("run_id")
        if m_run_id != run_id:
            return SnapshotValidationResult(
                valid=False,
                status="MANIFEST_RUN_ID_MISMATCH",
                error_message=f"Year {year} manifest run_id {m_run_id!r} != selected_run_id {run_id!r}",
            )

        # Validate publication state (Finding M01, M02)
        # Strict whitelist: status must be PUBLISHED (rejecting FAILED, ABORTED, None, etc.)
        m_status = m_data.get("status") or m_data.get("publication_status") or m_data.get("pipeline_state")
        if m_status != "PUBLISHED":
            return SnapshotValidationResult(
                valid=False,
                status="MANIFEST_STATUS_NOT_PUBLISHED",
                error_message=f"Year {year} manifest status is not PUBLISHED (got {m_status!r})",
            )

        # Validate configuration.years structure (Finding M01)
        cfg_years = None
        if "configuration" in m_data and isinstance(m_data["configuration"], dict):
            cfg_years = m_data["configuration"].get("years")
        if cfg_years is None:
            # Fallback to root alias if present
            cfg_years = m_data.get("years") or ([m_data["year"]] if "year" in m_data else None)

        if cfg_years is None or not isinstance(cfg_years, list) or not cfg_years:
            return SnapshotValidationResult(
                valid=False,
                status="MANIFEST_YEARS_STRUCTURE_INVALID",
                error_message=f"Year {year} manifest missing or invalid years configuration: {cfg_years!r}",
            )

        if not all(isinstance(y, int) and not isinstance(y, bool) for y in cfg_years):
            return SnapshotValidationResult(
                valid=False,
                status="MANIFEST_YEARS_STRUCTURE_INVALID",
                error_message=f"Year {year} manifest years contains non-integer elements: {cfg_years!r}",
            )

        if year not in cfg_years:
            return SnapshotValidationResult(
                valid=False,
                status="MANIFEST_YEAR_MISMATCH",
                error_message=f"Year {year} manifest does not declare coverage for year {year} (years={cfg_years})",
            )

        # Multi-year run partition verification
        if len(cfg_years) > 1:
            # If multiple years declared in a single run, verify partition directory exists
            sub_year_matches = [p for p in physical_dir.iterdir() if p.is_dir() and f"{year}" in p.name]
            if not sub_year_matches:
                return SnapshotValidationResult(
                    valid=False,
                    status="UNVERIFIED_MULTIYEAR_PARTITION",
                    error_message=f"Multi-year run {run_id} declares years {cfg_years} but lacks verified partition boundaries for year {year}",
                )

        # Invariant 9: Manifest Outputs and File Checksums verification (Findings M01, M02, R02, R03)
        raw_outputs = m_data.get("outputs")
        if raw_outputs is None:
            raw_outputs = m_data.get("files") or m_data.get("published_files")

        if not raw_outputs:
            return SnapshotValidationResult(
                valid=False,
                status="MISSING_MANIFEST_OUTPUTS",
                error_message=f"Year {year} manifest declares no outputs or files inventory",
            )

        outputs_inventory: Dict[str, Dict[str, Any]] = {}
        if isinstance(raw_outputs, list):
            for out_item in raw_outputs:
                if not isinstance(out_item, dict):
                    return SnapshotValidationResult(
                        valid=False,
                        status="INVALID_OUTPUT_ENTRY",
                        error_message=f"Year {year} manifest output item is not a dictionary: {out_item!r}",
                    )
                out_path_str = out_item.get("path")
                if not out_path_str or not isinstance(out_path_str, str):
                    return SnapshotValidationResult(
                        valid=False,
                        status="INVALID_OUTPUT_ENTRY",
                        error_message=f"Year {year} manifest output item missing 'path'",
                    )
                out_p = Path(out_path_str)
                if out_p.is_absolute() or ".." in out_p.parts:
                    return SnapshotValidationResult(
                        valid=False,
                        status="OUTPUT_PATH_TRAVERSAL_DETECTED",
                        error_message=f"Year {year} manifest output path traversal or absolute: {out_path_str!r}",
                    )

                # R02: Output Path Identity & Confinement
                norm_out_str = out_path_str.replace("\\", "/")
                if norm_out_str.startswith("curated/") or norm_out_str.startswith("staging/") or norm_out_str.startswith("runs/"):
                    target_file = (base_dir / norm_out_str).resolve()
                else:
                    target_file = (physical_dir / norm_out_str).resolve()

                try:
                    rel_to_physical = target_file.relative_to(physical_dir.resolve())
                    if target_file == physical_dir.resolve():
                        return SnapshotValidationResult(
                            valid=False,
                            status="OUTPUT_PATH_IS_DIRECTORY",
                            error_message=f"Year {year} manifest output path points to directory itself: {out_path_str!r}",
                        )
                except (ValueError, RuntimeError):
                    return SnapshotValidationResult(
                        valid=False,
                        status="OUTPUT_PATH_RUN_MISMATCH",
                        error_message=(
                            f"Year {year} manifest output path {out_path_str!r} resolves to {target_file} "
                            f"which is outside authorized physical_dir {physical_dir.resolve()}"
                        ),
                    )

                canon_rel = rel_to_physical.as_posix()
                if canon_rel in outputs_inventory:
                    return SnapshotValidationResult(
                        valid=False,
                        status="DUPLICATE_OUTPUT_ENTRY",
                        error_message=f"Year {year} manifest contains duplicate output entry for {canon_rel!r}",
                    )

                # R03: Output bytes check (required non-negative int, not bool)
                if "bytes" not in out_item or out_item.get("bytes") is None:
                    return SnapshotValidationResult(
                        valid=False,
                        status="MISSING_OUTPUT_BYTES",
                        error_message=f"Year {year} manifest output {canon_rel!r} missing required 'bytes'",
                    )
                exp_bytes = out_item["bytes"]
                if not isinstance(exp_bytes, int) or isinstance(exp_bytes, bool) or exp_bytes < 0:
                    return SnapshotValidationResult(
                        valid=False,
                        status="INVALID_OUTPUT_BYTES_METADATA",
                        error_message=f"Year {year} manifest output {canon_rel!r} has invalid 'bytes': {exp_bytes!r}",
                    )

                # R03: Output sha256 check (required 64 hex chars, no placeholders)
                if "sha256" not in out_item or out_item.get("sha256") is None:
                    return SnapshotValidationResult(
                        valid=False,
                        status="MISSING_OUTPUT_SHA256",
                        error_message=f"Year {year} manifest output {canon_rel!r} missing required 'sha256'",
                    )
                exp_sha = out_item["sha256"]
                if not isinstance(exp_sha, str):
                    return SnapshotValidationResult(
                        valid=False,
                        status="INVALID_OUTPUT_SHA256_METADATA",
                        error_message=f"Year {year} manifest output {canon_rel!r} 'sha256' must be str, got {type(exp_sha).__name__}",
                    )
                exp_sha_stripped = exp_sha.strip()
                if exp_sha_stripped in ("PENDING", "UNVERIFIED", ""):
                    return SnapshotValidationResult(
                        valid=False,
                        status="INVALID_OUTPUT_SHA256_METADATA",
                        error_message=f"Year {year} manifest output {canon_rel!r} has placeholder 'sha256': {exp_sha!r}",
                    )
                if not re.fullmatch(r"^[0-9a-fA-F]{64}$", exp_sha_stripped):
                    return SnapshotValidationResult(
                        valid=False,
                        status="INVALID_OUTPUT_SHA256_METADATA",
                        error_message=f"Year {year} manifest output {canon_rel!r} has invalid 64-char hex SHA-256: {exp_sha!r}",
                    )

                outputs_inventory[canon_rel] = {
                    "path": canon_rel,
                    "target_file": target_file,
                    "bytes": exp_bytes,
                    "sha256": exp_sha_stripped,
                }
        elif isinstance(raw_outputs, dict):
            for rel_k, v in raw_outputs.items():
                k_p = Path(rel_k)
                if k_p.is_absolute() or ".." in k_p.parts:
                    return SnapshotValidationResult(
                        valid=False,
                        status="OUTPUT_PATH_TRAVERSAL_DETECTED",
                        error_message=f"Year {year} manifest output path traversal or absolute: {rel_k!r}",
                    )
                norm_out_str = rel_k.replace("\\", "/")
                if norm_out_str.startswith("curated/") or norm_out_str.startswith("staging/") or norm_out_str.startswith("runs/"):
                    target_file = (base_dir / norm_out_str).resolve()
                else:
                    target_file = (physical_dir / norm_out_str).resolve()

                try:
                    rel_to_physical = target_file.relative_to(physical_dir.resolve())
                    if target_file == physical_dir.resolve():
                        return SnapshotValidationResult(
                            valid=False,
                            status="OUTPUT_PATH_IS_DIRECTORY",
                            error_message=f"Year {year} manifest output path points to directory itself: {rel_k!r}",
                        )
                except (ValueError, RuntimeError):
                    return SnapshotValidationResult(
                        valid=False,
                        status="OUTPUT_PATH_RUN_MISMATCH",
                        error_message=(
                            f"Year {year} manifest output path {rel_k!r} resolves to {target_file} "
                            f"which is outside authorized physical_dir {physical_dir.resolve()}"
                        ),
                    )

                canon_rel = rel_to_physical.as_posix()
                if canon_rel in outputs_inventory:
                    return SnapshotValidationResult(
                        valid=False,
                        status="DUPLICATE_OUTPUT_ENTRY",
                        error_message=f"Year {year} manifest contains duplicate output entry for {canon_rel!r}",
                    )

                if not isinstance(v, dict):
                    return SnapshotValidationResult(
                        valid=False,
                        status="INVALID_OUTPUT_ENTRY",
                        error_message=f"Year {year} manifest output {rel_k!r} metadata must be a dict",
                    )

                if "bytes" not in v or v.get("bytes") is None:
                    return SnapshotValidationResult(
                        valid=False,
                        status="MISSING_OUTPUT_BYTES",
                        error_message=f"Year {year} manifest output {canon_rel!r} missing required 'bytes'",
                    )
                exp_bytes = v["bytes"]
                if not isinstance(exp_bytes, int) or isinstance(exp_bytes, bool) or exp_bytes < 0:
                    return SnapshotValidationResult(
                        valid=False,
                        status="INVALID_OUTPUT_BYTES_METADATA",
                        error_message=f"Year {year} manifest output {canon_rel!r} has invalid 'bytes': {exp_bytes!r}",
                    )

                if "sha256" not in v or v.get("sha256") is None:
                    return SnapshotValidationResult(
                        valid=False,
                        status="MISSING_OUTPUT_SHA256",
                        error_message=f"Year {year} manifest output {canon_rel!r} missing required 'sha256'",
                    )
                exp_sha = v["sha256"]
                if not isinstance(exp_sha, str):
                    return SnapshotValidationResult(
                        valid=False,
                        status="INVALID_OUTPUT_SHA256_METADATA",
                        error_message=f"Year {year} manifest output {canon_rel!r} 'sha256' must be str, got {type(exp_sha).__name__}",
                    )
                exp_sha_stripped = exp_sha.strip()
                if exp_sha_stripped in ("PENDING", "UNVERIFIED", ""):
                    return SnapshotValidationResult(
                        valid=False,
                        status="INVALID_OUTPUT_SHA256_METADATA",
                        error_message=f"Year {year} manifest output {canon_rel!r} has placeholder 'sha256': {exp_sha!r}",
                    )
                if not re.fullmatch(r"^[0-9a-fA-F]{64}$", exp_sha_stripped):
                    return SnapshotValidationResult(
                        valid=False,
                        status="INVALID_OUTPUT_SHA256_METADATA",
                        error_message=f"Year {year} manifest output {canon_rel!r} has invalid 64-char hex SHA-256: {exp_sha!r}",
                    )

                outputs_inventory[canon_rel] = {
                    "path": canon_rel,
                    "target_file": target_file,
                    "bytes": exp_bytes,
                    "sha256": exp_sha_stripped,
                }
        else:
            return SnapshotValidationResult(
                valid=False,
                status="INVALID_OUTPUT_STRUCTURE",
                error_message=f"Year {year} manifest outputs must be a list or dict",
            )

        # Check for unlisted physical Parquet files (Finding M02, R02)
        physical_parquet_map = {
            pf.resolve().relative_to(physical_dir.resolve()).as_posix(): pf
            for pf in parquet_files
        }
        physical_parquet_rels = set(physical_parquet_map.keys())
        declared_rels = set(outputs_inventory.keys())

        unlisted = physical_parquet_rels - declared_rels
        if unlisted:
            return SnapshotValidationResult(
                valid=False,
                status="UNLISTED_PHYSICAL_PARQUET_DETECTED",
                error_message=f"Year {year} physical Parquet files not declared in manifest outputs: {sorted(unlisted)}",
            )

        missing_from_disk = declared_rels - physical_parquet_rels
        if missing_from_disk:
            return SnapshotValidationResult(
                valid=False,
                status="MANIFEST_FILE_NOT_FOUND",
                error_message=f"Year {year} declared output file missing from disk: {sorted(missing_from_disk)}",
            )

        # Verify physical file size and SHA-256 (Finding R03)
        if verify_file_checksums:
            for canon_rel, expected_meta in outputs_inventory.items():
                target_file = physical_parquet_map[canon_rel]
                if not target_file.is_file():
                    return SnapshotValidationResult(
                        valid=False,
                        status="MANIFEST_FILE_NOT_FOUND",
                        error_message=f"Year {year} declared output file {canon_rel} missing from disk at {target_file}",
                    )

                actual_bytes = target_file.stat().st_size
                exp_bytes = expected_meta["bytes"]
                if actual_bytes != exp_bytes:
                    return SnapshotValidationResult(
                        valid=False,
                        status="MANIFEST_FILE_SIZE_MISMATCH",
                        error_message=f"Year {year} file {canon_rel} size mismatch: expected {exp_bytes}, got {actual_bytes}",
                    )

                actual_sha = compute_file_sha256(target_file)
                exp_sha = expected_meta["sha256"]
                if actual_sha.lower() != exp_sha.lower():
                    return SnapshotValidationResult(
                        valid=False,
                        status="MANIFEST_FILE_HASH_MISMATCH",
                        error_message=f"Year {year} file {canon_rel} SHA-256 mismatch against manifest: expected {exp_sha}, got {actual_sha}",
                    )

        # Invariant 10: Strict DC-11/DC-12 Row Accounting verification
        acct = entry.get("accounting")
        if not isinstance(acct, dict):
            return SnapshotValidationResult(
                valid=False,
                status="MISSING_ROW_ACCOUNTING",
                error_message=f"Year {year} missing 'accounting' dictionary",
            )

        raw_c = acct.get("raw_row_count")
        acc_c = acct.get("accepted_row_count")
        q_c = acct.get("quarantined_row_count")
        rej_c = acct.get("rejected_row_count")

        # Strict non-negative integer type checks (reject bool, float, str, None)
        for field_name, val in [
            ("raw_row_count", raw_c),
            ("accepted_row_count", acc_c),
            ("quarantined_row_count", q_c),
            ("rejected_row_count", rej_c),
        ]:
            if not isinstance(val, int) or isinstance(val, bool) or val < 0:
                return SnapshotValidationResult(
                    valid=False,
                    status="INVALID_NUMERIC_ACCOUNTING",
                    error_message=f"Year {year} {field_name} must be non-negative integer, got {val!r} ({type(val).__name__})",
                )

        # DC-11 conservation equation: raw == accepted + quarantined + rejected
        if raw_c != (acc_c + q_c + rej_c):
            return SnapshotValidationResult(
                valid=False,
                status="UNBALANCED_ROW_ACCOUNTING",
                error_message=(
                    f"Year {year} row accounting unbalance: raw({raw_c}) != "
                    f"accepted({acc_c}) + quarantined({q_c}) + rejected({rej_c})"
                ),
            )

        # Invariant 11: Manifest-to-Registry Accounting Reconciliation (Finding M02)
        m_acct = m_data.get("row_accounting")
        if not isinstance(m_acct, dict):
            return SnapshotValidationResult(
                valid=False,
                status="MISSING_MANIFEST_ROW_ACCOUNTING",
                error_message=f"Year {year} manifest missing row_accounting dictionary",
            )

        m_raw = m_acct.get("raw_row_count")
        m_acc = m_acct.get("accepted_row_count")
        m_quar = m_acct.get("quarantined_row_count")
        m_rej = m_acct.get("rejected_row_count")

        for m_name, m_val in [
            ("raw_row_count", m_raw),
            ("accepted_row_count", m_acc),
            ("quarantined_row_count", m_quar),
            ("rejected_row_count", m_rej),
        ]:
            if not isinstance(m_val, int) or isinstance(m_val, bool) or m_val < 0:
                return SnapshotValidationResult(
                    valid=False,
                    status="INVALID_MANIFEST_ACCOUNTING_TYPES",
                    error_message=f"Year {year} manifest {m_name} must be non-negative integer, got {m_val!r}",
                )

        if m_raw != (m_acc + m_quar + m_rej):
            return SnapshotValidationResult(
                valid=False,
                status="MANIFEST_ROW_ACCOUNTING_UNBALANCED",
                error_message=f"Year {year} manifest accounting is unbalanced: {m_raw} != {m_acc} + {m_quar} + {m_rej}",
            )

        if m_raw != raw_c or m_acc != acc_c or m_quar != q_c or m_rej != rej_c:
            return SnapshotValidationResult(
                valid=False,
                status="MANIFEST_REGISTRY_ACCOUNTING_MISMATCH",
                error_message=(
                    f"Year {year} accounting mismatch: manifest (raw={m_raw}, acc={m_acc}, quar={m_quar}, rej={m_rej}) "
                    f"!= registry (raw={raw_c}, acc={acc_c}, quar={q_c}, rej={rej_c})"
                ),
            )

        # Invariant 12: Parquet Physical Row Counts and Schema verification (Finding M02, M03)
        total_physical_parquet_rows = 0
        for pf in parquet_files:
            if not is_valid_parquet_file(pf):
                return SnapshotValidationResult(
                    valid=False,
                    status="CORRUPT_OR_FAKE_PARQUET_DETECTED",
                    error_message=f"Year {year} file {pf.name} is corrupt or not a valid Parquet file",
                )

            if verify_parquet_metadata:
                try:
                    meta = pq.read_metadata(str(pf))
                except Exception as exc:
                    return SnapshotValidationResult(
                        valid=False,
                        status="INVALID_PARQUET_METADATA",
                        error_message=f"Year {year} file {pf.name} Thrift metadata parse failure: {exc}",
                    )

                if meta.num_columns < 1 or meta.num_rows < 0:
                    return SnapshotValidationResult(
                        valid=False,
                        status="INVALID_PARQUET_METADATA",
                        error_message=f"Year {year} file {pf.name} invalid metadata dimensions",
                    )

                total_physical_parquet_rows += meta.num_rows

                if verify_parquet_schema:
                    try:
                        arrow_schema = meta.schema.to_arrow_schema()
                        col_names = set(arrow_schema.names)
                    except Exception as exc:
                        return SnapshotValidationResult(
                            valid=False,
                            status="INVALID_PARQUET_SCHEMA",
                            error_message=f"Year {year} file {pf.name} schema extraction error: {exc}",
                        )

                    # Check forbidden columns per DATA_CONTRACT.md
                    forbidden_present = [col for col in FORBIDDEN_COLUMNS if col in col_names]
                    if forbidden_present:
                        return SnapshotValidationResult(
                            valid=False,
                            status="FORBIDDEN_COLUMNS_IN_PARQUET_SCHEMA",
                            error_message=f"Year {year} file {pf.name} contains forbidden columns: {sorted(forbidden_present)}",
                        )

                    # Check 7 core measures
                    missing_measures = [m for m in SEVEN_CORE_MEASURES if m not in col_names]
                    if missing_measures:
                        return SnapshotValidationResult(
                            valid=False,
                            status="MISSING_CORE_MEASURES_IN_PARQUET_SCHEMA",
                            error_message=f"Year {year} file {pf.name} missing mandatory core measures: {sorted(missing_measures)}",
                        )

        # Invariant 13: Physical Parquet Row Count must match certified accepted rows (Finding M03)
        if verify_physical_row_counts:
            if total_physical_parquet_rows != acc_c:
                return SnapshotValidationResult(
                    valid=False,
                    status="PARQUET_PHYSICAL_ROW_COUNT_MISMATCH",
                    error_message=(
                        f"Year {year} physical Parquet row count {total_physical_parquet_rows:,} "
                        f"!= declared accepted_row_count {acc_c:,}"
                    ),
                )

        # Invariant 14: ExecutionReceipt Verification (Findings M01, M02, R01, R04)
        candidate_receipts = [
            physical_dir / "execution_receipt.json",
            base_dir / "metadata" / run_id / "execution_receipt.json",
            base_dir / "curated" / "metadata" / run_id / "execution_receipt.json",
        ]
        receipt_p = next((p for p in candidate_receipts if p.is_file()), None)

        if require_execution_receipt and receipt_p is None:
            return SnapshotValidationResult(
                valid=False,
                status="MISSING_EXECUTION_RECEIPT",
                error_message=f"Year {year} execution_receipt.json missing in candidate locations",
            )

        if receipt_p is not None:
            try:
                r_data = json.loads(receipt_p.read_text(encoding="utf-8"))
            except Exception as exc:
                return SnapshotValidationResult(
                    valid=False,
                    status="CORRUPT_EXECUTION_RECEIPT",
                    error_message=f"Year {year} execution receipt is corrupt: {exc}",
                )

            if not isinstance(r_data, dict):
                return SnapshotValidationResult(
                    valid=False,
                    status="CORRUPT_EXECUTION_RECEIPT",
                    error_message=f"Year {year} execution receipt root must be a JSON object",
                )

            # R04.1: run_id
            r_run_id = r_data.get("run_id")
            if not r_run_id or not isinstance(r_run_id, str):
                return SnapshotValidationResult(
                    valid=False,
                    status="RECEIPT_FIELD_MISSING",
                    error_message=f"Year {year} receipt missing mandatory 'run_id'",
                )
            if r_run_id != run_id:
                return SnapshotValidationResult(
                    valid=False,
                    status="RECEIPT_RUN_ID_MISMATCH",
                    error_message=f"Year {year} receipt run_id {r_run_id!r} != selected_run_id {run_id!r}",
                )

            # R04.2: task_id
            r_task_id = r_data.get("task_id")
            if not r_task_id or not isinstance(r_task_id, str) or not r_task_id.strip():
                return SnapshotValidationResult(
                    valid=False,
                    status="RECEIPT_FIELD_MISSING",
                    error_message=f"Year {year} receipt missing mandatory 'task_id'",
                )

            # R04.3: pipeline_state & publication_status
            r_pipe_state = r_data.get("pipeline_state")
            r_pub_status = r_data.get("publication_status")
            if not r_pipe_state or not r_pub_status:
                return SnapshotValidationResult(
                    valid=False,
                    status="RECEIPT_FIELD_MISSING",
                    error_message=f"Year {year} receipt missing 'pipeline_state' or 'publication_status'",
                )
            if r_pipe_state != "PUBLISHED" or r_pub_status != "PUBLISHED":
                return SnapshotValidationResult(
                    valid=False,
                    status="RECEIPT_STATUS_NOT_PUBLISHED",
                    error_message=(
                        f"Year {year} receipt publication status is not PUBLISHED "
                        f"(pipeline_state={r_pipe_state!r}, publication_status={r_pub_status!r})"
                    ),
                )

            # R04.4: published_path
            r_pub_path = r_data.get("published_path")
            if not r_pub_path or not isinstance(r_pub_path, str):
                return SnapshotValidationResult(
                    valid=False,
                    status="RECEIPT_FIELD_MISSING",
                    error_message=f"Year {year} receipt missing mandatory 'published_path'",
                )
            norm_r_pub = r_pub_path.replace("\\", "/")
            if Path(norm_r_pub).is_absolute():
                r_pub_resolved = Path(norm_r_pub).resolve()
            else:
                if norm_r_pub.startswith("data/"):
                    cand = (base_dir / norm_r_pub[5:]).resolve()
                    if cand == physical_dir.resolve():
                        r_pub_resolved = cand
                    else:
                        r_pub_resolved = (base_dir / norm_r_pub).resolve()
                else:
                    r_pub_resolved = (base_dir / norm_r_pub).resolve()

            if r_pub_resolved != physical_dir.resolve():
                return SnapshotValidationResult(
                    valid=False,
                    status="RECEIPT_PUBLISHED_PATH_MISMATCH",
                    error_message=(
                        f"Year {year} receipt published_path {r_pub_path!r} resolves to "
                        f"{r_pub_resolved} != physical_dir {physical_dir.resolve()}"
                    ),
                )

            # R04.5: manifest_path
            r_m_path = r_data.get("manifest_path")
            if not r_m_path or not isinstance(r_m_path, str):
                return SnapshotValidationResult(
                    valid=False,
                    status="RECEIPT_FIELD_MISSING",
                    error_message=f"Year {year} receipt missing mandatory 'manifest_path'",
                )
            norm_r_m = r_m_path.replace("\\", "/")
            if Path(norm_r_m).is_absolute():
                r_m_resolved = Path(norm_r_m).resolve()
            else:
                if norm_r_m.startswith("data/"):
                    cand = (base_dir / norm_r_m[5:]).resolve()
                    if cand == manifest_p.resolve():
                        r_m_resolved = cand
                    else:
                        r_m_resolved = (base_dir / norm_r_m).resolve()
                else:
                    r_m_resolved = (base_dir / norm_r_m).resolve()

            if r_m_resolved != manifest_p.resolve():
                return SnapshotValidationResult(
                    valid=False,
                    status="RECEIPT_MANIFEST_PATH_MISMATCH",
                    error_message=(
                        f"Year {year} receipt manifest_path {r_m_path!r} resolves to "
                        f"{r_m_resolved} != actual manifest {manifest_p.resolve()}"
                    ),
                )

            # R04.6: manifest_bytes
            r_m_bytes = r_data.get("manifest_bytes")
            if r_m_bytes is None or not isinstance(r_m_bytes, int) or isinstance(r_m_bytes, bool) or r_m_bytes < 0:
                return SnapshotValidationResult(
                    valid=False,
                    status="RECEIPT_FIELD_MISSING",
                    error_message=f"Year {year} receipt missing or invalid 'manifest_bytes': {r_m_bytes!r}",
                )
            actual_m_bytes = manifest_p.stat().st_size
            if r_m_bytes != actual_m_bytes:
                return SnapshotValidationResult(
                    valid=False,
                    status="RECEIPT_MANIFEST_BYTES_MISMATCH",
                    error_message=f"Year {year} receipt manifest_bytes {r_m_bytes} != actual {actual_m_bytes}",
                )

            # R04.7: manifest_sha256
            r_m_sha = r_data.get("manifest_sha256")
            if not r_m_sha or not isinstance(r_m_sha, str) or not re.fullmatch(r"^[0-9a-fA-F]{64}$", r_m_sha.strip()):
                return SnapshotValidationResult(
                    valid=False,
                    status="RECEIPT_FIELD_MISSING",
                    error_message=f"Year {year} receipt missing or invalid 'manifest_sha256': {r_m_sha!r}",
                )
            actual_m_sha = compute_file_sha256(manifest_p)
            if r_m_sha.strip().lower() != actual_m_sha.lower():
                return SnapshotValidationResult(
                    valid=False,
                    status="RECEIPT_MANIFEST_SHA256_MISMATCH",
                    error_message=f"Year {year} receipt manifest_sha256 mismatch against disk manifest",
                )

            # R04.8: row_accounting
            r_acct = r_data.get("row_accounting")
            if not isinstance(r_acct, dict):
                return SnapshotValidationResult(
                    valid=False,
                    status="RECEIPT_FIELD_MISSING",
                    error_message=f"Year {year} receipt missing 'row_accounting' dictionary",
                )
            for fld in ("raw_row_count", "accepted_row_count", "quarantined_row_count", "rejected_row_count"):
                v = r_acct.get(fld)
                if v is None or not isinstance(v, int) or isinstance(v, bool) or v < 0:
                    return SnapshotValidationResult(
                        valid=False,
                        status="RECEIPT_FIELD_MISSING",
                        error_message=f"Year {year} receipt row_accounting field {fld} invalid or missing: {v!r}",
                    )
            if r_acct["raw_row_count"] != (r_acct["accepted_row_count"] + r_acct["quarantined_row_count"] + r_acct["rejected_row_count"]):
                return SnapshotValidationResult(
                    valid=False,
                    status="RECEIPT_ROW_ACCOUNTING_UNBALANCED",
                    error_message=f"Year {year} receipt row_accounting is unbalanced",
                )
            if (
                r_acct["raw_row_count"] != raw_c
                or r_acct["accepted_row_count"] != acc_c
                or r_acct["quarantined_row_count"] != q_c
                or r_acct["rejected_row_count"] != rej_c
            ):
                return SnapshotValidationResult(
                    valid=False,
                    status="RECEIPT_ROW_ACCOUNTING_MISMATCH",
                    error_message=f"Year {year} receipt row_accounting does not match manifest and registry",
                )

        # Contrast raw_row_count against canonical source inventory
        canonical_entry = AUDITED_SOURCE_INVENTORY.get(year)
        if canonical_entry is not None:
            if raw_c != canonical_entry.audited_row_count:
                return SnapshotValidationResult(
                    valid=False,
                    status="CANONICAL_RAW_COUNT_MISMATCH",
                    error_message=(
                        f"Year {year} raw_row_count {raw_c:,} does not match canonical audited inventory {canonical_entry.audited_row_count:,}"
                    ),
                )

        # Invariant 15: Governed source_coverage_status verification
        cov_status = entry.get("source_coverage_status")
        if year == 2024 and cov_status != "PARTIAL":
            return SnapshotValidationResult(
                valid=False,
                status="OR05_COVERAGE_STATUS_VIOLATION",
                error_message="Year 2024 must declare source_coverage_status = 'PARTIAL' (preserving OR-05 missing March)",
            )
        elif year != 2024 and cov_status not in ("VERIFIED_WITH_SCOPE", "UNKNOWN"):
            return SnapshotValidationResult(
                valid=False,
                status="INVALID_COVERAGE_STATUS",
                error_message=f"Year {year} source_coverage_status {cov_status!r} invalid",
            )

        tot_raw += raw_c
        tot_accepted += acc_c
        tot_quarantined += q_c
        tot_rejected += rej_c

        annual_details[year] = asdict(AnnualSnapshotDetail(
            year=year,
            selected_run_id=run_id,
            physical_path=norm_dir_str,
            parquet_files_count=len(parquet_files),
            raw_row_count=raw_c,
            accepted_row_count=acc_c,
            quarantined_row_count=q_c,
            rejected_row_count=rej_c,
            source_coverage_status=cov_status,
            manifest_path=str(manifest_p.as_posix()),
            schema_fingerprint=m_data.get("schema_fingerprint"),
            receipt_path=str(receipt_p.as_posix()) if receipt_p else None,
            physical_parquet_rows=total_physical_parquet_rows,
        ))

    # Invariant 16: Total 9-year RAW rows must equal 54,674,003
    if tot_raw != TOTAL_AUDITED_ROWS:
        return SnapshotValidationResult(
            valid=False,
            status="TOTAL_RAW_ROWS_MISMATCH",
            error_message=f"Sum of 9-year raw_row_count {tot_raw:,} != canonical baseline {TOTAL_AUDITED_ROWS:,}",
        )

    # Guard against non-production diagnostic mode yielding production acceptance
    if not require_execution_receipt:
        return SnapshotValidationResult(
            valid=False,
            status="DIAGNOSTIC_PASS_RECEIPT_OMITTED_NOT_FOR_PRODUCTION",
            error_message="Registry passed structural checks, but execution receipts were not required/verified. This non-production diagnostic result cannot be certified for production release.",
            selected_paths=selected_paths,
            total_raw_rows=tot_raw,
            total_accepted_rows=tot_accepted,
            total_quarantined_rows=tot_quarantined,
            total_rejected_rows=tot_rejected,
            annual_details=annual_details,
        )

    if not verify_file_checksums:
        return SnapshotValidationResult(
            valid=False,
            status="NON_PRODUCTION_CHECKSUM_SKIPPED",
            error_message="Checksum verification was skipped; cannot certify snapshot for production release.",
            selected_paths=selected_paths,
            total_raw_rows=tot_raw,
            total_accepted_rows=tot_accepted,
            total_quarantined_rows=tot_quarantined,
            total_rejected_rows=tot_rejected,
            annual_details=annual_details,
        )

    if not (verify_parquet_metadata and verify_physical_row_counts and verify_parquet_schema):
        return SnapshotValidationResult(
            valid=False,
            status="NON_PRODUCTION_VERIFICATION_INCOMPLETE",
            error_message="One or more Parquet verification checks were disabled; cannot certify snapshot for production release.",
            selected_paths=selected_paths,
            total_raw_rows=tot_raw,
            total_accepted_rows=tot_accepted,
            total_quarantined_rows=tot_quarantined,
            total_rejected_rows=tot_rejected,
            annual_details=annual_details,
        )

    return SnapshotValidationResult(
        valid=True,
        status="VALID_SNAPSHOT_REGISTRY",
        selected_paths=selected_paths,
        total_raw_rows=tot_raw,
        total_accepted_rows=tot_accepted,
        total_quarantined_rows=tot_quarantined,
        total_rejected_rows=tot_rejected,
        annual_details=annual_details,
    )


def validate_single_annual_run(
    year: int,
    run_id: str,
    base_data_dir: Union[str, Path] = "data",
    verify_parquet_metadata: bool = True,
    verify_file_checksums: bool = True,
    verify_physical_row_counts: bool = True,
    verify_parquet_schema: bool = True,
    require_execution_receipt: bool = True,
) -> SnapshotValidationResult:
    """
    Validate a single annual execution batch at run level (Findings E02, R05).
    Evaluates:
    - Run ID format and containment
    - Deep recursive physical Parquet discovery (Finding R05)
    - Run manifest presence, status == 'PUBLISHED', coverage for year
    - Outputs inventory 1:1 match with physical files (bytes, SHA-256)
    - DC-11 balanced row accounting reconciled against canonical source inventory
    - Physical Parquet Thrift metadata, schema, 7 core measures, forbidden columns
    - Physical row count conservation (physical == accepted)
    - ExecutionReceipt full contract validation (Finding R01, R04)
    - Source coverage status (e.g. PARTIAL for 2024 per OR-05)
    """
    base_dir = Path(base_data_dir).resolve()
    curated_runs_root = (base_dir / "curated" / "runs").resolve()

    if year not in CANONICAL_YEARS:
        return SnapshotValidationResult(
            valid=False,
            status="INVALID_SURVEY_YEAR",
            error_message=f"Year {year} is not in canonical survey years {CANONICAL_YEARS}",
        )

    try:
        physical_dir = validate_run_id(run_id, curated_runs_root)
    except ValueError as exc:
        return SnapshotValidationResult(
            valid=False,
            status="INVALID_RUN_ID",
            error_message=f"Year {year} run_id {run_id!r} failed validation: {exc}",
        )

    if not physical_dir.is_dir():
        return SnapshotValidationResult(
            valid=False,
            status="MISSING_PHYSICAL_DIR",
            error_message=f"Year {year} curated run directory not found: {physical_dir}",
        )

    # Invariant 6: Deep Recursive Parquet discovery (Finding R05)
    parquet_files, err_status, err_msg = discover_physical_parquet_files(physical_dir)
    if err_status is not None:
        return SnapshotValidationResult(
            valid=False,
            status=err_status,
            error_message=f"Year {year} {err_msg}",
        )

    # Run Manifest discovery and validation
    candidate_manifests = [
        physical_dir / "run_manifest.json",
        base_dir / "metadata" / run_id / "run_manifest.json",
        base_dir / "curated" / "metadata" / run_id / "run_manifest.json",
    ]
    manifest_p = next((p for p in candidate_manifests if p.is_file()), None)

    if manifest_p is None:
        return SnapshotValidationResult(
            valid=False,
            status="MISSING_RUN_MANIFEST",
            error_message=f"Year {year} run {run_id} has no run_manifest.json in candidate locations",
        )

    try:
        m_data = json.loads(manifest_p.read_text(encoding="utf-8"))
    except Exception as exc:
        return SnapshotValidationResult(
            valid=False,
            status="CORRUPT_RUN_MANIFEST",
            error_message=f"Year {year} run_manifest.json is corrupt: {exc}",
        )

    if not isinstance(m_data, dict):
        return SnapshotValidationResult(
            valid=False,
            status="CORRUPT_RUN_MANIFEST",
            error_message=f"Year {year} run_manifest.json root is not a dictionary",
        )

    m_run_id = m_data.get("run_id")
    if m_run_id != run_id:
        return SnapshotValidationResult(
            valid=False,
            status="MANIFEST_RUN_ID_MISMATCH",
            error_message=f"Year {year} manifest run_id {m_run_id!r} != selected_run_id {run_id!r}",
        )

    m_status = m_data.get("status")
    if m_status != "PUBLISHED":
        return SnapshotValidationResult(
            valid=False,
            status="MANIFEST_STATUS_NOT_PUBLISHED",
            error_message=f"Year {year} manifest status is {m_status!r}, must strictly equal 'PUBLISHED'",
        )

    m_cfg = m_data.get("configuration")
    if not isinstance(m_cfg, dict):
        return SnapshotValidationResult(
            valid=False,
            status="MANIFEST_CONFIGURATION_MISSING",
            error_message=f"Year {year} manifest missing configuration object",
        )

    cfg_years = m_cfg.get("years")
    if not isinstance(cfg_years, list) or not all(isinstance(y, int) for y in cfg_years):
        return SnapshotValidationResult(
            valid=False,
            status="MANIFEST_YEARS_STRUCTURE_INVALID",
            error_message=f"Year {year} manifest configuration.years must be a list of integers",
        )

    if year not in cfg_years:
        return SnapshotValidationResult(
            valid=False,
            status="MANIFEST_YEAR_MISMATCH",
            error_message=f"Year {year} manifest does not declare coverage for year {year} (years={cfg_years})",
        )

    # Manifest outputs verification (Findings R02, R03, R05)
    raw_outputs = m_data.get("outputs")
    if raw_outputs is None:
        raw_outputs = m_data.get("files") or m_data.get("published_files")

    if not raw_outputs:
        return SnapshotValidationResult(
            valid=False,
            status="MISSING_MANIFEST_OUTPUTS",
            error_message=f"Year {year} manifest declares no outputs or files inventory",
        )

    outputs_inventory: Dict[str, Dict[str, Any]] = {}
    if isinstance(raw_outputs, list):
        for out_item in raw_outputs:
            if not isinstance(out_item, dict):
                return SnapshotValidationResult(
                    valid=False,
                    status="INVALID_OUTPUT_ENTRY",
                    error_message=f"Year {year} manifest output item is not a dictionary: {out_item!r}",
                )
            out_path_str = out_item.get("path")
            if not out_path_str or not isinstance(out_path_str, str):
                return SnapshotValidationResult(
                    valid=False,
                    status="INVALID_OUTPUT_ENTRY",
                    error_message=f"Year {year} manifest output item missing 'path'",
                )
            out_p = Path(out_path_str)
            if out_p.is_absolute() or ".." in out_p.parts:
                return SnapshotValidationResult(
                    valid=False,
                    status="OUTPUT_PATH_TRAVERSAL_DETECTED",
                    error_message=f"Year {year} manifest output path traversal or absolute: {out_path_str!r}",
                )

            norm_out_str = out_path_str.replace("\\", "/")
            if norm_out_str.startswith("curated/") or norm_out_str.startswith("staging/") or norm_out_str.startswith("runs/"):
                target_file = (base_dir / norm_out_str).resolve()
            else:
                target_file = (physical_dir / norm_out_str).resolve()

            try:
                rel_to_physical = target_file.relative_to(physical_dir.resolve())
                if target_file == physical_dir.resolve():
                    return SnapshotValidationResult(
                        valid=False,
                        status="OUTPUT_PATH_IS_DIRECTORY",
                        error_message=f"Year {year} manifest output path points to directory itself: {out_path_str!r}",
                    )
            except (ValueError, RuntimeError):
                return SnapshotValidationResult(
                    valid=False,
                    status="OUTPUT_PATH_RUN_MISMATCH",
                    error_message=(
                        f"Year {year} manifest output path {out_path_str!r} resolves to {target_file} "
                        f"which is outside authorized physical_dir {physical_dir.resolve()}"
                    ),
                )

            canon_rel = rel_to_physical.as_posix()
            if canon_rel in outputs_inventory:
                return SnapshotValidationResult(
                    valid=False,
                    status="DUPLICATE_OUTPUT_ENTRY",
                    error_message=f"Year {year} manifest contains duplicate output entry for {canon_rel!r}",
                )

            if "bytes" not in out_item or out_item.get("bytes") is None:
                return SnapshotValidationResult(
                    valid=False,
                    status="MISSING_OUTPUT_BYTES",
                    error_message=f"Year {year} manifest output {canon_rel!r} missing required 'bytes'",
                )
            exp_bytes = out_item["bytes"]
            if not isinstance(exp_bytes, int) or isinstance(exp_bytes, bool) or exp_bytes < 0:
                return SnapshotValidationResult(
                    valid=False,
                    status="INVALID_OUTPUT_BYTES_METADATA",
                    error_message=f"Year {year} manifest output {canon_rel!r} has invalid 'bytes': {exp_bytes!r}",
                )

            if "sha256" not in out_item or out_item.get("sha256") is None:
                return SnapshotValidationResult(
                    valid=False,
                    status="MISSING_OUTPUT_SHA256",
                    error_message=f"Year {year} manifest output {canon_rel!r} missing required 'sha256'",
                )
            exp_sha = out_item["sha256"]
            if not isinstance(exp_sha, str):
                return SnapshotValidationResult(
                    valid=False,
                    status="INVALID_OUTPUT_SHA256_METADATA",
                    error_message=f"Year {year} manifest output {canon_rel!r} 'sha256' must be str, got {type(exp_sha).__name__}",
                )
            exp_sha_stripped = exp_sha.strip()
            if exp_sha_stripped in ("PENDING", "UNVERIFIED", ""):
                return SnapshotValidationResult(
                    valid=False,
                    status="INVALID_OUTPUT_SHA256_METADATA",
                    error_message=f"Year {year} manifest output {canon_rel!r} has placeholder 'sha256': {exp_sha!r}",
                )
            if not re.fullmatch(r"^[0-9a-fA-F]{64}$", exp_sha_stripped):
                return SnapshotValidationResult(
                    valid=False,
                    status="INVALID_OUTPUT_SHA256_METADATA",
                    error_message=f"Year {year} manifest output {canon_rel!r} has invalid 64-char hex SHA-256: {exp_sha!r}",
                )

            outputs_inventory[canon_rel] = {
                "path": canon_rel,
                "target_file": target_file,
                "bytes": exp_bytes,
                "sha256": exp_sha_stripped,
            }
    elif isinstance(raw_outputs, dict):
        for rel_k, v in raw_outputs.items():
            k_p = Path(rel_k)
            if k_p.is_absolute() or ".." in k_p.parts:
                return SnapshotValidationResult(
                    valid=False,
                    status="OUTPUT_PATH_TRAVERSAL_DETECTED",
                    error_message=f"Year {year} manifest output path traversal or absolute: {rel_k!r}",
                )
            norm_out_str = rel_k.replace("\\", "/")
            if norm_out_str.startswith("curated/") or norm_out_str.startswith("staging/") or norm_out_str.startswith("runs/"):
                target_file = (base_dir / norm_out_str).resolve()
            else:
                target_file = (physical_dir / norm_out_str).resolve()

            try:
                rel_to_physical = target_file.relative_to(physical_dir.resolve())
                if target_file == physical_dir.resolve():
                    return SnapshotValidationResult(
                        valid=False,
                        status="OUTPUT_PATH_IS_DIRECTORY",
                        error_message=f"Year {year} manifest output path points to directory itself: {rel_k!r}",
                    )
            except (ValueError, RuntimeError):
                return SnapshotValidationResult(
                    valid=False,
                    status="OUTPUT_PATH_RUN_MISMATCH",
                    error_message=(
                        f"Year {year} manifest output path {rel_k!r} resolves to {target_file} "
                        f"which is outside authorized physical_dir {physical_dir.resolve()}"
                    ),
                )

            canon_rel = rel_to_physical.as_posix()
            if canon_rel in outputs_inventory:
                return SnapshotValidationResult(
                    valid=False,
                    status="DUPLICATE_OUTPUT_ENTRY",
                    error_message=f"Year {year} manifest contains duplicate output entry for {canon_rel!r}",
                )

            if not isinstance(v, dict):
                return SnapshotValidationResult(
                    valid=False,
                    status="INVALID_OUTPUT_ENTRY",
                    error_message=f"Year {year} manifest output {rel_k!r} metadata must be a dict",
                )

            if "bytes" not in v or v.get("bytes") is None:
                return SnapshotValidationResult(
                    valid=False,
                    status="MISSING_OUTPUT_BYTES",
                    error_message=f"Year {year} manifest output {canon_rel!r} missing required 'bytes'",
                )
            exp_bytes = v["bytes"]
            if not isinstance(exp_bytes, int) or isinstance(exp_bytes, bool) or exp_bytes < 0:
                return SnapshotValidationResult(
                    valid=False,
                    status="INVALID_OUTPUT_BYTES_METADATA",
                    error_message=f"Year {year} manifest output {canon_rel!r} has invalid 'bytes': {exp_bytes!r}",
                )

            if "sha256" not in v or v.get("sha256") is None:
                return SnapshotValidationResult(
                    valid=False,
                    status="MISSING_OUTPUT_SHA256",
                    error_message=f"Year {year} manifest output {canon_rel!r} missing required 'sha256'",
                )
            exp_sha = v["sha256"]
            if not isinstance(exp_sha, str):
                return SnapshotValidationResult(
                    valid=False,
                    status="INVALID_OUTPUT_SHA256_METADATA",
                    error_message=f"Year {year} manifest output {canon_rel!r} 'sha256' must be str, got {type(exp_sha).__name__}",
                )
            exp_sha_stripped = exp_sha.strip()
            if exp_sha_stripped in ("PENDING", "UNVERIFIED", ""):
                return SnapshotValidationResult(
                    valid=False,
                    status="INVALID_OUTPUT_SHA256_METADATA",
                    error_message=f"Year {year} manifest output {canon_rel!r} has placeholder 'sha256': {exp_sha!r}",
                )
            if not re.fullmatch(r"^[0-9a-fA-F]{64}$", exp_sha_stripped):
                return SnapshotValidationResult(
                    valid=False,
                    status="INVALID_OUTPUT_SHA256_METADATA",
                    error_message=f"Year {year} manifest output {canon_rel!r} has invalid 64-char hex SHA-256: {exp_sha!r}",
                )

            outputs_inventory[canon_rel] = {
                "path": canon_rel,
                "target_file": target_file,
                "bytes": exp_bytes,
                "sha256": exp_sha_stripped,
            }
    else:
        return SnapshotValidationResult(
            valid=False,
            status="INVALID_OUTPUT_STRUCTURE",
            error_message=f"Year {year} manifest outputs must be a list or dict",
        )

    physical_parquet_map = {
        pf.resolve().relative_to(physical_dir.resolve()).as_posix(): pf
        for pf in parquet_files
    }
    physical_parquet_rels = set(physical_parquet_map.keys())
    declared_rels = set(outputs_inventory.keys())

    unlisted = physical_parquet_rels - declared_rels
    if unlisted:
        return SnapshotValidationResult(
            valid=False,
            status="UNLISTED_PHYSICAL_PARQUET_DETECTED",
            error_message=f"Year {year} physical Parquet files not declared in manifest outputs: {sorted(unlisted)}",
        )

    missing_from_disk = declared_rels - physical_parquet_rels
    if missing_from_disk:
        return SnapshotValidationResult(
            valid=False,
            status="MANIFEST_FILE_NOT_FOUND",
            error_message=f"Year {year} declared output file missing from disk: {sorted(missing_from_disk)}",
        )

    if verify_file_checksums:
        for canon_rel, expected_meta in outputs_inventory.items():
            target_file = physical_parquet_map[canon_rel]
            if not target_file.is_file():
                return SnapshotValidationResult(
                    valid=False,
                    status="MANIFEST_FILE_NOT_FOUND",
                    error_message=f"Year {year} declared output file {canon_rel} missing from disk at {target_file}",
                )

            actual_bytes = target_file.stat().st_size
            exp_bytes = expected_meta["bytes"]
            if actual_bytes != exp_bytes:
                return SnapshotValidationResult(
                    valid=False,
                    status="MANIFEST_FILE_SIZE_MISMATCH",
                    error_message=f"Year {year} file {canon_rel} size mismatch: expected {exp_bytes}, got {actual_bytes}",
                )

            actual_sha = compute_file_sha256(target_file)
            exp_sha = expected_meta["sha256"]
            if actual_sha.lower() != exp_sha.lower():
                return SnapshotValidationResult(
                    valid=False,
                    status="MANIFEST_FILE_HASH_MISMATCH",
                    error_message=f"Year {year} file {canon_rel} SHA-256 mismatch against manifest: expected {exp_sha}, got {actual_sha}",
                )

    # Manifest row accounting verification (DC-11)
    m_acct = m_data.get("row_accounting")
    if not isinstance(m_acct, dict):
        return SnapshotValidationResult(
            valid=False,
            status="MISSING_MANIFEST_ROW_ACCOUNTING",
            error_message=f"Year {year} manifest missing row_accounting dictionary",
        )

    m_raw = m_acct.get("raw_row_count")
    m_acc = m_acct.get("accepted_row_count")
    m_quar = m_acct.get("quarantined_row_count")
    m_rej = m_acct.get("rejected_row_count")

    for m_name, m_val in [
        ("raw_row_count", m_raw),
        ("accepted_row_count", m_acc),
        ("quarantined_row_count", m_quar),
        ("rejected_row_count", m_rej),
    ]:
        if not isinstance(m_val, int) or isinstance(m_val, bool) or m_val < 0:
            return SnapshotValidationResult(
                valid=False,
                status="INVALID_MANIFEST_ACCOUNTING_TYPES",
                error_message=f"Year {year} manifest {m_name} must be non-negative integer, got {m_val!r}",
            )

    if m_raw != (m_acc + m_quar + m_rej):
        return SnapshotValidationResult(
            valid=False,
            status="MANIFEST_ROW_ACCOUNTING_UNBALANCED",
            error_message=f"Year {year} manifest accounting is unbalanced: {m_raw} != {m_acc} + {m_quar} + {m_rej}",
        )

    # Reconcile against canonical source inventory
    canonical_entry = AUDITED_SOURCE_INVENTORY.get(year)
    if canonical_entry is not None:
        if m_raw != canonical_entry.audited_row_count:
            return SnapshotValidationResult(
                valid=False,
                status="CANONICAL_RAW_COUNT_MISMATCH",
                error_message=(
                    f"Year {year} raw_row_count {m_raw:,} does not match canonical audited inventory {canonical_entry.audited_row_count:,}"
                ),
            )

    # Parquet Physical Row Counts and Schema verification
    total_physical_parquet_rows = 0
    for pf in parquet_files:
        if not is_valid_parquet_file(pf):
            return SnapshotValidationResult(
                valid=False,
                status="CORRUPT_OR_FAKE_PARQUET_DETECTED",
                error_message=f"Year {year} file {pf.name} is corrupt or not a valid Parquet file",
            )

        if verify_parquet_metadata:
            try:
                meta = pq.read_metadata(str(pf))
            except Exception as exc:
                return SnapshotValidationResult(
                    valid=False,
                    status="INVALID_PARQUET_METADATA",
                    error_message=f"Year {year} file {pf.name} Thrift metadata parse failure: {exc}",
                )

            if meta.num_columns < 1 or meta.num_rows < 0:
                return SnapshotValidationResult(
                    valid=False,
                    status="INVALID_PARQUET_METADATA",
                    error_message=f"Year {year} file {pf.name} invalid metadata dimensions",
                )

            total_physical_parquet_rows += meta.num_rows

            if verify_parquet_schema:
                try:
                    arrow_schema = meta.schema.to_arrow_schema()
                    col_names = set(arrow_schema.names)
                except Exception as exc:
                    return SnapshotValidationResult(
                        valid=False,
                        status="INVALID_PARQUET_SCHEMA",
                        error_message=f"Year {year} file {pf.name} schema extraction error: {exc}",
                    )

                forbidden_present = [col for col in FORBIDDEN_COLUMNS if col in col_names]
                if forbidden_present:
                    return SnapshotValidationResult(
                        valid=False,
                        status="FORBIDDEN_COLUMNS_IN_PARQUET_SCHEMA",
                        error_message=f"Year {year} file {pf.name} contains forbidden columns: {sorted(forbidden_present)}",
                    )

                missing_measures = [m for m in SEVEN_CORE_MEASURES if m not in col_names]
                if missing_measures:
                    return SnapshotValidationResult(
                        valid=False,
                        status="MISSING_CORE_MEASURES_IN_PARQUET_SCHEMA",
                        error_message=f"Year {year} file {pf.name} missing mandatory core measures: {sorted(missing_measures)}",
                    )

    if verify_physical_row_counts:
        if total_physical_parquet_rows != m_acc:
            return SnapshotValidationResult(
                valid=False,
                status="PARQUET_PHYSICAL_ROW_COUNT_MISMATCH",
                error_message=(
                    f"Year {year} physical Parquet row count {total_physical_parquet_rows:,} "
                    f"!= declared accepted_row_count {m_acc:,}"
                ),
            )

    # ExecutionReceipt Verification
    candidate_receipts = [
        physical_dir / "execution_receipt.json",
        base_dir / "metadata" / run_id / "execution_receipt.json",
        base_dir / "curated" / "metadata" / run_id / "execution_receipt.json",
    ]
    receipt_p = next((p for p in candidate_receipts if p.is_file()), None)

    if require_execution_receipt and receipt_p is None:
        return SnapshotValidationResult(
            valid=False,
            status="MISSING_EXECUTION_RECEIPT",
            error_message=f"Year {year} execution_receipt.json missing in candidate locations",
        )

    if receipt_p is not None:
        try:
            r_data = json.loads(receipt_p.read_text(encoding="utf-8"))
        except Exception as exc:
            return SnapshotValidationResult(
                valid=False,
                status="CORRUPT_EXECUTION_RECEIPT",
                error_message=f"Year {year} execution receipt is corrupt: {exc}",
            )

        if not isinstance(r_data, dict):
            return SnapshotValidationResult(
                valid=False,
                status="CORRUPT_EXECUTION_RECEIPT",
                error_message=f"Year {year} execution receipt root must be a JSON object",
            )

        r_run_id = r_data.get("run_id")
        if not r_run_id or not isinstance(r_run_id, str):
            return SnapshotValidationResult(
                valid=False,
                status="RECEIPT_FIELD_MISSING",
                error_message=f"Year {year} receipt missing mandatory 'run_id'",
            )
        if r_run_id != run_id:
            return SnapshotValidationResult(
                valid=False,
                status="RECEIPT_RUN_ID_MISMATCH",
                error_message=f"Year {year} receipt run_id {r_run_id!r} != selected_run_id {run_id!r}",
            )

        r_task_id = r_data.get("task_id")
        if not r_task_id or not isinstance(r_task_id, str) or not r_task_id.strip():
            return SnapshotValidationResult(
                valid=False,
                status="RECEIPT_FIELD_MISSING",
                error_message=f"Year {year} receipt missing mandatory 'task_id'",
            )

        r_pipe_state = r_data.get("pipeline_state")
        r_pub_status = r_data.get("publication_status")
        if not r_pipe_state or not r_pub_status:
            return SnapshotValidationResult(
                valid=False,
                status="RECEIPT_FIELD_MISSING",
                error_message=f"Year {year} receipt missing 'pipeline_state' or 'publication_status'",
            )
        if r_pipe_state != "PUBLISHED" or r_pub_status != "PUBLISHED":
            return SnapshotValidationResult(
                valid=False,
                status="RECEIPT_STATUS_NOT_PUBLISHED",
                error_message=(
                    f"Year {year} receipt publication status is not PUBLISHED "
                    f"(pipeline_state={r_pipe_state!r}, publication_status={r_pub_status!r})"
                ),
            )

        r_pub_path = r_data.get("published_path")
        if not r_pub_path or not isinstance(r_pub_path, str):
            return SnapshotValidationResult(
                valid=False,
                status="RECEIPT_FIELD_MISSING",
                error_message=f"Year {year} receipt missing mandatory 'published_path'",
            )
        norm_r_pub = r_pub_path.replace("\\", "/")
        if Path(norm_r_pub).is_absolute():
            r_pub_resolved = Path(norm_r_pub).resolve()
        else:
            if norm_r_pub.startswith("data/"):
                cand = (base_dir / norm_r_pub[5:]).resolve()
                if cand == physical_dir.resolve():
                    r_pub_resolved = cand
                else:
                    r_pub_resolved = (base_dir / norm_r_pub).resolve()
            else:
                r_pub_resolved = (base_dir / norm_r_pub).resolve()

        if r_pub_resolved != physical_dir.resolve():
            return SnapshotValidationResult(
                valid=False,
                status="RECEIPT_PUBLISHED_PATH_MISMATCH",
                error_message=(
                    f"Year {year} receipt published_path {r_pub_path!r} resolves to "
                    f"{r_pub_resolved} != physical_dir {physical_dir.resolve()}"
                ),
            )

        r_m_path = r_data.get("manifest_path")
        if not r_m_path or not isinstance(r_m_path, str):
            return SnapshotValidationResult(
                valid=False,
                status="RECEIPT_FIELD_MISSING",
                error_message=f"Year {year} receipt missing mandatory 'manifest_path'",
            )
        norm_r_m = r_m_path.replace("\\", "/")
        if Path(norm_r_m).is_absolute():
            r_m_resolved = Path(norm_r_m).resolve()
        else:
            if norm_r_m.startswith("data/"):
                cand = (base_dir / norm_r_m[5:]).resolve()
                if cand == manifest_p.resolve():
                    r_m_resolved = cand
                else:
                    r_m_resolved = (base_dir / norm_r_m).resolve()
            else:
                r_m_resolved = (base_dir / norm_r_m).resolve()

        if r_m_resolved != manifest_p.resolve():
            return SnapshotValidationResult(
                valid=False,
                status="RECEIPT_MANIFEST_PATH_MISMATCH",
                error_message=(
                    f"Year {year} receipt manifest_path {r_m_path!r} resolves to "
                    f"{r_m_resolved} != actual manifest {manifest_p.resolve()}"
                ),
            )

        r_m_bytes = r_data.get("manifest_bytes")
        if r_m_bytes is None or not isinstance(r_m_bytes, int) or isinstance(r_m_bytes, bool) or r_m_bytes < 0:
            return SnapshotValidationResult(
                valid=False,
                status="RECEIPT_FIELD_MISSING",
                error_message=f"Year {year} receipt missing or invalid 'manifest_bytes': {r_m_bytes!r}",
            )
        actual_m_bytes = manifest_p.stat().st_size
        if r_m_bytes != actual_m_bytes:
            return SnapshotValidationResult(
                valid=False,
                status="RECEIPT_MANIFEST_BYTES_MISMATCH",
                error_message=f"Year {year} receipt manifest_bytes {r_m_bytes} != actual {actual_m_bytes}",
            )

        r_m_sha = r_data.get("manifest_sha256")
        if not r_m_sha or not isinstance(r_m_sha, str) or not re.fullmatch(r"^[0-9a-fA-F]{64}$", r_m_sha.strip()):
            return SnapshotValidationResult(
                valid=False,
                status="RECEIPT_FIELD_MISSING",
                error_message=f"Year {year} receipt missing or invalid 'manifest_sha256': {r_m_sha!r}",
            )
        actual_m_sha = compute_file_sha256(manifest_p)
        if r_m_sha.strip().lower() != actual_m_sha.lower():
            return SnapshotValidationResult(
                valid=False,
                status="RECEIPT_MANIFEST_SHA256_MISMATCH",
                error_message=f"Year {year} receipt manifest_sha256 mismatch against disk manifest",
            )

        r_acct = r_data.get("row_accounting")
        if not isinstance(r_acct, dict):
            return SnapshotValidationResult(
                valid=False,
                status="RECEIPT_FIELD_MISSING",
                error_message=f"Year {year} receipt missing 'row_accounting' dictionary",
            )
        for fld in ("raw_row_count", "accepted_row_count", "quarantined_row_count", "rejected_row_count"):
            v = r_acct.get(fld)
            if v is None or not isinstance(v, int) or isinstance(v, bool) or v < 0:
                return SnapshotValidationResult(
                    valid=False,
                    status="RECEIPT_FIELD_MISSING",
                    error_message=f"Year {year} receipt row_accounting field {fld} invalid or missing: {v!r}",
                )
        if r_acct["raw_row_count"] != (r_acct["accepted_row_count"] + r_acct["quarantined_row_count"] + r_acct["rejected_row_count"]):
            return SnapshotValidationResult(
                valid=False,
                status="RECEIPT_ROW_ACCOUNTING_UNBALANCED",
                error_message=f"Year {year} receipt row_accounting is unbalanced",
            )
        if (
            r_acct["raw_row_count"] != m_raw
            or r_acct["accepted_row_count"] != m_acc
            or r_acct["quarantined_row_count"] != m_quar
            or r_acct["rejected_row_count"] != m_rej
        ):
            return SnapshotValidationResult(
                valid=False,
                status="RECEIPT_ROW_ACCOUNTING_MISMATCH",
                error_message=f"Year {year} receipt row_accounting does not match manifest",
            )

    # 2024 OR-05 check
    if year == 2024:
        cov_status = m_cfg.get("source_coverage_status")
        if cov_status != "PARTIAL":
            return SnapshotValidationResult(
                valid=False,
                status="OR05_COVERAGE_STATUS_VIOLATION",
                error_message="Year 2024 must declare source_coverage_status = 'PARTIAL' (preserving OR-05 missing March)",
            )

    if not require_execution_receipt:
        return SnapshotValidationResult(
            valid=False,
            status="DIAGNOSTIC_PASS_RECEIPT_OMITTED_NOT_FOR_PRODUCTION",
            error_message="Run passed structural checks, but execution receipts were not required/verified. This non-production diagnostic result cannot be certified for production release.",
            selected_paths=[str(physical_dir.as_posix())],
            total_raw_rows=m_raw,
            total_accepted_rows=m_acc,
            total_quarantined_rows=m_quar,
            total_rejected_rows=m_rej,
        )

    if not verify_file_checksums:
        return SnapshotValidationResult(
            valid=False,
            status="NON_PRODUCTION_CHECKSUM_SKIPPED",
            error_message="Checksum verification was skipped; cannot certify run for production release.",
            selected_paths=[str(physical_dir.as_posix())],
            total_raw_rows=m_raw,
            total_accepted_rows=m_acc,
            total_quarantined_rows=m_quar,
            total_rejected_rows=m_rej,
        )

    if not (verify_parquet_metadata and verify_physical_row_counts and verify_parquet_schema):
        return SnapshotValidationResult(
            valid=False,
            status="NON_PRODUCTION_VERIFICATION_INCOMPLETE",
            error_message="One or more Parquet verification checks were disabled; cannot certify run for production release.",
            selected_paths=[str(physical_dir.as_posix())],
            total_raw_rows=m_raw,
            total_accepted_rows=m_acc,
            total_quarantined_rows=m_quar,
            total_rejected_rows=m_rej,
        )

    return SnapshotValidationResult(
        valid=True,
        status="VALID_SINGLE_RUN_ANNUAL_BATCH",
        selected_paths=[str(physical_dir.as_posix())],
        total_raw_rows=m_raw,
        total_accepted_rows=m_acc,
        total_quarantined_rows=m_quar,
        total_rejected_rows=m_rej,
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify multi-year snapshot registry or single annual execution batch."
    )
    parser.add_argument(
        "--registry-path",
        type=Path,
        default=None,
        help="Path to snapshot_registry.json (default: data/curated/snapshot_registry.json)",
    )
    parser.add_argument(
        "--single-run-year",
        type=int,
        default=None,
        help="Validate a single annual run instead of multi-year registry (e.g. --single-run-year 2016 --run-id run_2016_v1)",
    )
    parser.add_argument(
        "--run-id",
        type=str,
        default=None,
        help="Run ID for single annual run validation (e.g. run_2016_v1)",
    )
    parser.add_argument(
        "--base-dir",
        type=Path,
        default=Path("data"),
        help="Base data directory (default: data)",
    )
    parser.add_argument(
        "--skip-parquet-check",
        action="store_true",
        help="Skip PyArrow Parquet Thrift metadata inspection",
    )
    parser.add_argument(
        "--require-receipt",
        action="store_true",
        default=True,
        help="Require execution_receipt.json to be present (default: True)",
    )
    parser.add_argument(
        "--allow-missing-receipt-diagnostic-only",
        action="store_true",
        help="Allow missing execution receipts for offline diagnostic inspection only (will not yield production PASS)",
    )
    args = parser.parse_args()

    require_receipt = not args.allow_missing_receipt_diagnostic_only

    # Dispatch to single annual run mode if --single-run-year is specified
    if args.single_run_year is not None:
        if not args.run_id:
            print("Error: --run-id is required when --single-run-year is specified")
            return 1

        res = validate_single_annual_run(
            year=args.single_run_year,
            run_id=args.run_id,
            base_data_dir=args.base_dir,
            verify_parquet_metadata=not args.skip_parquet_check,
            require_execution_receipt=require_receipt,
        )

        print("=" * 80)
        print(f"SINGLE ANNUAL RUN AUDIT: [{'PASS' if res.valid else 'FAIL'}] {res.status}")
        print("=" * 80)
        print(f"Survey Year:         {args.single_run_year}")
        print(f"Run ID:              {args.run_id}")
        print(f"Base Directory:      {args.base_dir.resolve()}")
        print(f"Validation Status:   {res.status}")
        print(f"Valid:               {res.valid}")
        if res.error_message:
            print(f"Error Message:       {res.error_message}")
        print(f"Total Raw Rows:      {res.total_raw_rows:,}" if res.total_raw_rows is not None else "Total Raw Rows: N/A")
        print(f"Total Accepted Rows: {res.total_accepted_rows:,}" if res.total_accepted_rows is not None else "Total Accepted Rows: N/A")
        print(f"Total Quarantined:   {res.total_quarantined_rows:,}" if res.total_quarantined_rows is not None else "Total Quarantined: N/A")
        print(f"Total Rejected Rows: {res.total_rejected_rows:,}" if res.total_rejected_rows is not None else "Total Rejected Rows: N/A")
        print("=" * 80)
        return 0 if res.valid else 1

    # Otherwise validate multi-year registry
    reg_path = args.registry_path or Path("data/curated/snapshot_registry.json")
    if not reg_path.exists():
        print(f"Error: Snapshot registry file not found: {reg_path}")
        return 1

    try:
        registry_data = json.loads(reg_path.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"Error: Failed to parse snapshot registry JSON: {exc}")
        return 2

    res = validate_multiyear_snapshot_registry(
        registry_data=registry_data,
        base_data_dir=args.base_dir,
        verify_parquet_metadata=not args.skip_parquet_check,
        require_execution_receipt=require_receipt,
    )

    print("=" * 80)
    print(f"MULTI-YEAR SNAPSHOT REGISTRY AUDIT: [{'PASS' if res.valid else 'FAIL'}] {res.status}")
    print("=" * 80)
    print(f"Registry Path:       {reg_path.resolve()}")
    print(f"Base Directory:      {args.base_dir.resolve()}")
    print(f"Validation Status:   {res.status}")
    print(f"Valid:               {res.valid}")
    if res.error_message:
        print(f"Error Message:       {res.error_message}")
    print(f"Total Raw Rows:      {res.total_raw_rows:,}" if res.total_raw_rows is not None else "Total Raw Rows: N/A")
    print(f"Total Accepted Rows: {res.total_accepted_rows:,}" if res.total_accepted_rows is not None else "Total Accepted Rows: N/A")
    print(f"Total Quarantined:   {res.total_quarantined_rows:,}" if res.total_quarantined_rows is not None else "Total Quarantined: N/A")
    print(f"Total Rejected Rows: {res.total_rejected_rows:,}" if res.total_rejected_rows is not None else "Total Rejected Rows: N/A")
    print(f"Selected Paths:      {len(res.selected_paths) if res.selected_paths else 0} paths validated")
    print("=" * 80)

    return 0 if res.valid else 1


if __name__ == "__main__":
    sys.exit(main())
