"""
tools/qa/check_writer_preflight_safety.py

Standalone Read-Only Operational Preflight Command for Windows NTFS Concurrency & Recovery Safety.
Enforces Findings G6-C05 and S04:
Evaluates both POINTER_STATE and WRITER_LOCK_STATE prior to writer execution.
Guarantees unified storage root alignment with SafePublisher and IngestionCoordinator.

Exit Codes (Fail-Closed):
  0: CLEAN - Safe for writer to proceed with atomic lock acquisition
  1: ACTIVE_OR_STALE_LOCK - Active writer lock held or stale lock requiring governed recovery
  2: UNRESOLVED_RECOVERY - Recovery markers or artifacts present (.del_*, .recovery_required*)
  3: CORRUPT_OR_AMBIGUOUS - Corrupt lock metadata or indeterminate process liveness
  4: POINTER_OR_ROOT_ERROR - Invalid/corrupted staging pointer or storage root mismatch
"""

import argparse
from dataclasses import asdict, dataclass
import json
import os
from pathlib import Path
import sys
from typing import Any, Dict, List, Optional, Union

ROOT_DIR = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT_DIR / "src"
TOOLS_DIR = Path(__file__).resolve().parent

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

from flight_pipeline.storage.locking import (
    LockMetadata,
    PidLivenessStatus,
    SingleWriterLock,
    get_pid_liveness,
)
from verify_staging_pointer import verify_staging_pointer


@dataclass(frozen=True)
class PreflightSafetyReport:
    safe_to_start_writer: bool
    exit_code: int
    summary_verdict: str
    base_data_dir: str
    pointer_status: str
    pointer_error: Optional[str]
    pointer_file: str
    lock_state: str
    lock_dir: str
    lock_file_path: Optional[str]
    active_pid: Optional[int]
    liveness_status: Optional[str]
    recovery_artifacts_count: int
    recovery_artifacts: List[str]
    curated_dir: str
    storage_root_matched: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def evaluate_writer_safety_policy(
    base_dir: Union[str, Path],
    run_id: str = "operational_preflight_probe",
    expected_storage_root: Optional[Union[str, Path]] = None,
) -> PreflightSafetyReport:
    """
    Independent dual-gate operational evaluator strictly verifying both:
    1. POINTER_STATE (via read-only pointer verification)
    2. WRITER_LOCK_STATE (via read-only LockMetadata and recovery artifact inspection)
    3. STORAGE_ROOT_ALIGNMENT (against planned ingestion storage root)

    Read-Only Contract:
    Never mutates locks, never unlinks markers, never writes to disk.
    """
    resolved_base = Path(base_dir).resolve()
    curated_dir = resolved_base / "curated"
    lock_dir = resolved_base / "locks"
    lock_file = lock_dir / ".pipeline.lock"
    pointer_file = curated_dir / "latest_run_id.txt"

    exit_code = 0
    storage_root_matched = True
    summary_verdict = "SAFE_TO_PROCEED_TO_LOCK_ACQUISITION"

    # Gate 0: Storage Root Alignment Check
    if expected_storage_root is not None:
        resolved_expected = Path(expected_storage_root).resolve()
        if resolved_base != resolved_expected:
            storage_root_matched = False
            exit_code = 4
            summary_verdict = (
                f"BLOCKED_STORAGE_ROOT_MISMATCH: preflight={resolved_base} != planned={resolved_expected}"
            )

    # Gate 1: Pointer verification (read-only)
    pointer_res = verify_staging_pointer(resolved_base, allow_uninitialized=True)

    # Gate 2: Writer lock inspection (read-only)
    lock_obj = SingleWriterLock(lock_dir, run_id=run_id)
    recovery_artifacts = [p.name for p in lock_obj.get_unresolved_recovery_artifacts()]

    lock_state = "CLEAN"
    active_pid: Optional[int] = None
    liveness_val: Optional[str] = None

    if recovery_artifacts:
        lock_state = "UNRESOLVED_RECOVERY_ARTIFACTS_DETECTED"
        if exit_code == 0:
            exit_code = 2
            summary_verdict = "BLOCKED_UNRESOLVED_RECOVERY_ARTIFACTS"
    elif lock_file.is_file():
        try:
            raw_text = lock_file.read_text(encoding="utf-8")
            meta = LockMetadata.from_json(raw_text)
            active_pid = meta.pid
            liveness = get_pid_liveness(active_pid)
            liveness_val = liveness.value

            if liveness == PidLivenessStatus.PROCESS_ALIVE:
                lock_state = "ACTIVE_WRITER_LOCK_HELD"
                if exit_code == 0:
                    exit_code = 1
                    summary_verdict = "BLOCKED_CONCURRENT_WRITER_RUNNING"
            elif liveness == PidLivenessStatus.PROCESS_DEAD:
                lock_state = "STALE_LOCK_MANUAL_RECOVERY_REQUIRED"
                if exit_code == 0:
                    exit_code = 1
                    summary_verdict = "BLOCKED_STALE_LOCK_DEAD_PID_RECOVERY_REQUIRED"
            else:
                lock_state = "AMBIGUOUS_LOCK_LIVENESS_FAIL_CLOSED"
                if exit_code == 0:
                    exit_code = 3
                    summary_verdict = "BLOCKED_AMBIGUOUS_PID_LIVENESS"
        except Exception as exc:
            lock_state = f"CORRUPT_LOCK_METADATA_FAIL_CLOSED: {exc}"
            if exit_code == 0:
                exit_code = 3
                summary_verdict = "BLOCKED_CORRUPT_LOCK_METADATA"

    # Check pointer errors if no higher-priority error triggered
    if not pointer_res.success and exit_code == 0:
        exit_code = 4
        summary_verdict = f"BLOCKED_POINTER_VERIFICATION_FAILED: {pointer_res.status}"

    safe_to_start = (
        exit_code == 0
        and storage_root_matched
        and pointer_res.success
        and lock_state == "CLEAN"
        and len(recovery_artifacts) == 0
    )

    return PreflightSafetyReport(
        safe_to_start_writer=safe_to_start,
        exit_code=exit_code,
        summary_verdict=summary_verdict,
        base_data_dir=str(resolved_base.as_posix()),
        pointer_status=pointer_res.status,
        pointer_error=pointer_res.error_message,
        pointer_file=str(pointer_file.as_posix()),
        lock_state=lock_state,
        lock_dir=str(lock_dir.as_posix()),
        lock_file_path=str(lock_file.as_posix()) if lock_file.exists() else None,
        active_pid=active_pid,
        liveness_status=liveness_val,
        recovery_artifacts_count=len(recovery_artifacts),
        recovery_artifacts=recovery_artifacts,
        curated_dir=str(curated_dir.as_posix()),
        storage_root_matched=storage_root_matched,
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Standalone Read-Only Operational Preflight Check for Lock and Pointer Safety."
    )
    parser.add_argument(
        "--base-dir",
        type=Path,
        default=Path("data"),
        help="Base data directory containing curated/ and locks/ (default: data)",
    )
    parser.add_argument(
        "--expected-storage-root",
        type=Path,
        default=None,
        help="Expected storage root for planned ingestion to prevent root mismatch",
    )
    parser.add_argument(
        "--run-id",
        type=str,
        default="preflight_probe",
        help="Probe run_id for inspection context (default: preflight_probe)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output machine-readable JSON report",
    )
    args = parser.parse_args()

    report = evaluate_writer_safety_policy(
        base_dir=args.base_dir,
        run_id=args.run_id,
        expected_storage_root=args.expected_storage_root,
    )

    if args.json:
        print(json.dumps(report.to_dict(), indent=2))
    else:
        print("=================================================================")
        print("  G6 OPERATIONAL WRITER PREFLIGHT SAFETY CHECK (READ-ONLY)       ")
        print("=================================================================")
        print(f"Base Data Directory:  {report.base_data_dir}")
        print(f"Curated Directory:    {report.curated_dir}")
        print(f"Pointer File:         {report.pointer_file}")
        print(f"Lock Directory:       {report.lock_dir}")
        print(f"Lock File:            {report.lock_file_path}")
        print(f"Pointer Status:       {report.pointer_status}")
        print(f"Lock State:           {report.lock_state}")
        print(f"Active PID:           {report.active_pid} ({report.liveness_status})")
        print(f"Recovery Artifacts:   {report.recovery_artifacts_count}")
        print(f"Storage Root Matched: {report.storage_root_matched}")
        print(f"Safe To Start Writer: {report.safe_to_start_writer}")
        print(f"Summary Verdict:      {report.summary_verdict}")
        print(f"Exit Code:            {report.exit_code}")
        print("=================================================================")

    return report.exit_code


if __name__ == "__main__":
    sys.exit(main())
