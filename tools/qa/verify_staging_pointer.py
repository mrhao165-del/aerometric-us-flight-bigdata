#!/usr/bin/env python3
"""
tools/qa/verify_staging_pointer.py

Windows NTFS-safe read-only pointer verification utility.
Conforms to ARCHITECTURE.md, T006_FINAL_CORRECTIONS_ADDENDUM.md, and Gate G6 Operational Standards.

Verifies:
1. SafePublisher pointer read resolution via get_current_pointer().
2. Confinement and format validation of published run_id against directory traversal.
3. Existence and directory validity of target curated run directory (dangling pointer check).
4. Physical Parquet file integrity within the published target run directory.
5. Optional run_manifest.json integrity, JSON parseability, and run_id alignment.

CRITICAL SAFETY INVARIANT:
This tool operates strictly in READ-ONLY mode. It NEVER modifies, touches, moves,
creates, or deletes the pointer file, staging directory, curated runs, or manifests.
"""

from dataclasses import dataclass, asdict, field
import json
import os
from pathlib import Path
import sys
from typing import Any, Dict, List, Optional, Union

ROOT_DIR = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from flight_pipeline.storage.publication import (
    SafePublisher,
    is_valid_parquet_file,
    validate_run_id,
    RUN_ID_REGEX,
)


@dataclass
class PointerVerificationResult:
    """Immutable result of read-only pointer verification."""
    success: bool
    status: str
    base_dir: str
    pointer_file: str
    pointer_value: Optional[str] = None
    target_dir: Optional[str] = None
    parquet_files_found: int = 0
    valid_parquet_files: int = 0
    manifest_found: bool = False
    manifest_path: Optional[str] = None
    manifest_run_id: Optional[str] = None
    error_message: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)


def verify_staging_pointer(
    base_data_dir: Union[str, Path],
    require_manifest: bool = False,
    require_parquet: bool = True,
    allow_uninitialized: bool = False,
) -> PointerVerificationResult:
    """
    Perform comprehensive read-only verification of the staging/curated publication pointer.

    Args:
        base_data_dir: Base directory containing curated/ and staging/
        require_manifest: Whether run_manifest.json is strictly required
        require_parquet: Whether at least one valid .parquet file is required in target
        allow_uninitialized: If True, a non-existent pointer file is considered valid uninitialized state

    Returns:
        PointerVerificationResult detailing verification outcome.
    """
    base_dir = Path(base_data_dir).resolve()
    publisher = SafePublisher(str(base_dir))
    pointer_path = publisher.pointer_file
    runs_root = publisher.runs_root

    details: Dict[str, Any] = {
        "pointer_file_path": str(pointer_path),
        "runs_root_path": str(runs_root),
        "read_only_mode": True,
    }

    # 1. Check pointer file existence and initial resolution
    if not pointer_path.exists():
        if allow_uninitialized:
            return PointerVerificationResult(
                success=True,
                status="UNINITIALIZED_POINTER_ALLOWED",
                base_dir=str(base_dir),
                pointer_file=str(pointer_path),
                details=details,
                error_message=None,
            )
        return PointerVerificationResult(
            success=False,
            status="MISSING_POINTER_FILE",
            base_dir=str(base_dir),
            pointer_file=str(pointer_path),
            details=details,
            error_message=f"Pointer file does not exist: {pointer_path}",
        )

    if not pointer_path.is_file():
        return PointerVerificationResult(
            success=False,
            status="POINTER_NOT_A_FILE",
            base_dir=str(base_dir),
            pointer_file=str(pointer_path),
            details=details,
            error_message=f"Pointer path exists but is not a regular file: {pointer_path}",
        )

    # 2. Read pointer using SafePublisher get_current_pointer()
    try:
        raw_pointer = publisher.get_current_pointer()
    except OSError as exc:
        return PointerVerificationResult(
            success=False,
            status="POINTER_READ_IO_ERROR",
            base_dir=str(base_dir),
            pointer_file=str(pointer_path),
            details=details,
            error_message=f"Failed to read pointer file due to I/O or file lock error: {exc}",
        )

    if raw_pointer is None or not raw_pointer.strip():
        return PointerVerificationResult(
            success=False,
            status="EMPTY_POINTER_FILE",
            base_dir=str(base_dir),
            pointer_file=str(pointer_path),
            pointer_value=raw_pointer,
            details=details,
            error_message="Pointer file is empty or contains only whitespace.",
        )

    pointer_val = raw_pointer.strip()
    details["raw_pointer_value"] = pointer_val

    # 3. Path confinement and run_id format validation (Anti-Traversal)
    try:
        target_dir = validate_run_id(pointer_val, runs_root)
    except ValueError as exc:
        status = "PATH_TRAVERSAL_DETECTED" if any(p in pointer_val for p in ("..", "/", "\\", ":")) else "INVALID_RUN_ID_FORMAT"
        return PointerVerificationResult(
            success=False,
            status=status,
            base_dir=str(base_dir),
            pointer_file=str(pointer_path),
            pointer_value=pointer_val,
            details=details,
            error_message=f"Pointer value validation failed: {exc}",
        )

    details["resolved_target_dir"] = str(target_dir)

    # 4. Target directory existence (Dangling pointer check)
    if not target_dir.exists():
        return PointerVerificationResult(
            success=False,
            status="DANGLING_POINTER_TARGET_MISSING",
            base_dir=str(base_dir),
            pointer_file=str(pointer_path),
            pointer_value=pointer_val,
            target_dir=str(target_dir),
            details=details,
            error_message=f"Dangling pointer detected: target run directory does not exist: {target_dir}",
        )

    if not target_dir.is_dir():
        return PointerVerificationResult(
            success=False,
            status="TARGET_NOT_A_DIRECTORY",
            base_dir=str(base_dir),
            pointer_file=str(pointer_path),
            pointer_value=pointer_val,
            target_dir=str(target_dir),
            details=details,
            error_message=f"Target path exists but is not a directory: {target_dir}",
        )

    # 5. Parquet file verification
    parquet_files = [f for f in target_dir.rglob("*.parquet") if f.is_file()]
    details["total_parquet_files_found"] = len(parquet_files)
    valid_parquet_count = 0
    corrupt_parquet_files: List[str] = []

    for pf in parquet_files:
        if is_valid_parquet_file(pf):
            valid_parquet_count += 1
        else:
            corrupt_parquet_files.append(str(pf.relative_to(target_dir)))

    details["corrupt_parquet_files"] = corrupt_parquet_files

    if corrupt_parquet_files:
        return PointerVerificationResult(
            success=False,
            status="CORRUPT_PARQUET_DETECTED",
            base_dir=str(base_dir),
            pointer_file=str(pointer_path),
            pointer_value=pointer_val,
            target_dir=str(target_dir),
            parquet_files_found=len(parquet_files),
            valid_parquet_files=valid_parquet_count,
            details=details,
            error_message=f"Detected {len(corrupt_parquet_files)} corrupted or invalid Parquet file(s) in target.",
        )

    if require_parquet and valid_parquet_count == 0:
        return PointerVerificationResult(
            success=False,
            status="NO_PARQUET_FILES_FOUND",
            base_dir=str(base_dir),
            pointer_file=str(pointer_path),
            pointer_value=pointer_val,
            target_dir=str(target_dir),
            parquet_files_found=0,
            valid_parquet_files=0,
            details=details,
            error_message=f"Target directory contains no valid Parquet files: {target_dir}",
        )

    # 6. Run Manifest verification (if present or required)
    # Search locations per IngestionCoordinator and SafePublisher architectures:
    # 1. target_dir / "run_manifest.json" (inside versioned curated run)
    # 2. base_dir / "metadata" / pointer_val / "run_manifest.json" (canonical IngestionCoordinator metadata root)
    # 3. base_dir / "curated" / "metadata" / pointer_val / "run_manifest.json" (curated metadata sidecar fallback)
    manifest_candidates = [
        target_dir / "run_manifest.json",
        base_dir / "metadata" / pointer_val / "run_manifest.json",
        base_dir / "curated" / "metadata" / pointer_val / "run_manifest.json",
    ]
    found_manifest: Optional[Path] = None
    for cand in manifest_candidates:
        if cand.is_file():
            found_manifest = cand
            break

    if require_manifest and found_manifest is None:
        return PointerVerificationResult(
            success=False,
            status="MISSING_RUN_MANIFEST",
            base_dir=str(base_dir),
            pointer_file=str(pointer_path),
            pointer_value=pointer_val,
            target_dir=str(target_dir),
            parquet_files_found=len(parquet_files),
            valid_parquet_files=valid_parquet_count,
            manifest_found=False,
            details=details,
            error_message=f"run_manifest.json is required but not found in {manifest_candidates}",
        )

    manifest_run_id: Optional[str] = None
    if found_manifest is not None:
        try:
            m_text = found_manifest.read_text(encoding="utf-8")
            m_data = json.loads(m_text)
            if not isinstance(m_data, dict):
                return PointerVerificationResult(
                    success=False,
                    status="INVALID_MANIFEST_JSON",
                    base_dir=str(base_dir),
                    pointer_file=str(pointer_path),
                    pointer_value=pointer_val,
                    target_dir=str(target_dir),
                    parquet_files_found=len(parquet_files),
                    valid_parquet_files=valid_parquet_count,
                    manifest_found=True,
                    manifest_path=str(found_manifest),
                    details=details,
                    error_message=f"Manifest content is not a JSON object: {found_manifest}",
                )
            manifest_run_id = m_data.get("run_id")
            details["manifest_data_status"] = m_data.get("status")
            details["manifest_row_accounting"] = m_data.get("row_accounting")
        except Exception as exc:
            return PointerVerificationResult(
                success=False,
                status="CORRUPT_MANIFEST_FILE",
                base_dir=str(base_dir),
                pointer_file=str(pointer_path),
                pointer_value=pointer_val,
                target_dir=str(target_dir),
                parquet_files_found=len(parquet_files),
                valid_parquet_files=valid_parquet_count,
                manifest_found=True,
                manifest_path=str(found_manifest),
                details=details,
                error_message=f"Could not parse run manifest JSON: {exc}",
            )

        if manifest_run_id != pointer_val:
            return PointerVerificationResult(
                success=False,
                status="MANIFEST_RUN_ID_MISMATCH",
                base_dir=str(base_dir),
                pointer_file=str(pointer_path),
                pointer_value=pointer_val,
                target_dir=str(target_dir),
                parquet_files_found=len(parquet_files),
                valid_parquet_files=valid_parquet_count,
                manifest_found=True,
                manifest_path=str(found_manifest),
                manifest_run_id=manifest_run_id,
                details=details,
                error_message=f"Manifest run_id mismatch: pointer has {pointer_val!r}, manifest has {manifest_run_id!r}",
            )

    return PointerVerificationResult(
        success=True,
        status="VALID_POINTER",
        base_dir=str(base_dir),
        pointer_file=str(pointer_path),
        pointer_value=pointer_val,
        target_dir=str(target_dir),
        parquet_files_found=len(parquet_files),
        valid_parquet_files=valid_parquet_count,
        manifest_found=(found_manifest is not None),
        manifest_path=str(found_manifest) if found_manifest else None,
        manifest_run_id=manifest_run_id,
        details=details,
        error_message=None,
    )


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(
        description="Verify Staging/Curated Publication Pointer in Read-Only Mode."
    )
    parser.add_argument(
        "--base-dir",
        "-b",
        default="data",
        help="Base data directory containing curated/ and staging/ (default: data)",
    )
    parser.add_argument(
        "--require-manifest",
        action="store_true",
        help="Require that a valid run_manifest.json exists and matches run_id",
    )
    parser.add_argument(
        "--no-parquet-check",
        action="store_true",
        help="Skip checking for valid Parquet files in the published target directory",
    )
    parser.add_argument(
        "--allow-uninitialized",
        action="store_true",
        help="Allow absence of pointer file (returns exit code 0 for clean uninitialized state)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output machine-readable JSON result",
    )

    args = parser.parse_args()

    res = verify_staging_pointer(
        base_data_dir=args.base_dir,
        require_manifest=args.require_manifest,
        require_parquet=not args.no_parquet_check,
        allow_uninitialized=args.allow_uninitialized,
    )

    if args.json:
        print(res.to_json())
    else:
        status_symbol = "[PASS]" if res.success else "[FAIL]"
        print("=" * 80)
        print(f"STAGING / CURATED POINTER AUDIT: {status_symbol} {res.status}")
        print("=" * 80)
        print(f"Base Directory:       {res.base_dir}")
        print(f"Pointer File:         {res.pointer_file}")
        print(f"Pointer Value:        {res.pointer_value}")
        print(f"Target Directory:     {res.target_dir}")
        print(f"Parquet Files Found:  {res.parquet_files_found} (Valid: {res.valid_parquet_files})")
        print(f"Manifest Verified:    {res.manifest_found} (Run ID: {res.manifest_run_id})")
        if res.error_message:
            print(f"Error Diagnostic:     {res.error_message}")
        print("=" * 80)

    return 0 if res.success else 1


if __name__ == "__main__":
    sys.exit(main())
