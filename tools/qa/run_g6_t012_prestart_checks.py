#!/usr/bin/env python3
"""
tools/qa/run_g6_t012_prestart_checks.py

Operational Prestart Verification Runner for 2016 Annual Ingestion (Task: G6-T012-2016-PRESTART).
Executes read-only safety, source integrity, resource audit, and governance hold checks.
Outputs raw log to docs/05-evidence/G6_T012_2016_PRESTART_RAW_LOG.txt.

Safety Guarantees:
- Fail-Closed: Any mandatory check failure results in nonzero overall exit code (1).
- Non-Invasive: Never invokes live coordinator against production data directories.
- Safe Governance Check: Uses static code inspection and synthetic unit testing to verify D5 hold.
"""

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
from typing import List, Optional

import psutil

ROOT_DIR = Path(__file__).resolve().parents[2]
LOG_PATH = ROOT_DIR / "docs" / "05-evidence" / "G6_T012_2016_PRESTART_RAW_LOG.txt"


def evaluate_source_integrity(
    raw_path: Path,
    expected_size: int = 1538427452,
    expected_sha256: str = "4ed92ed732721a38ae28325135fad63436347613674ad96c1b273eb9d44cef34"
) -> dict:
    """Evaluate source file existence, byte size, and SHA-256 fail-closed."""
    exists = raw_path.exists()
    byte_size = raw_path.stat().st_size if exists else 0
    hasher = hashlib.sha256()
    if exists:
        with open(raw_path, "rb") as f:
            while chunk := f.read(1024 * 1024):
                hasher.update(chunk)
    sha256_hex = hasher.hexdigest() if exists else ""

    source_exists_match = exists
    source_size_match = (byte_size == expected_size)
    source_sha_match = (sha256_hex == expected_sha256)
    source_integrity_pass = source_exists_match and source_size_match and source_sha_match

    return {
        "exists": exists,
        "byte_size": byte_size,
        "expected_size": expected_size,
        "size_match": source_size_match,
        "sha256": sha256_hex,
        "expected_sha256": expected_sha256,
        "sha_match": source_sha_match,
        "valid": source_integrity_pass
    }


def run_checks(
    raw_path_override: Optional[Path] = None,
    allow_resource_hold: bool = False,
    output_log_path: Optional[Path] = None
) -> int:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT_DIR / "src")

    target_log_path = output_log_path or LOG_PATH

    overall_pass = True
    failure_reasons = []

    log_lines = []
    log_lines.append("=" * 80)
    log_lines.append("US FLIGHT PERFORMANCE ANALYSIS 2016-2024")
    log_lines.append("TASK: G6-T012-2016-PRESTART — RAW COMMAND EXECUTION LOG")
    log_lines.append(f"Timestamp (UTC): {datetime.now(timezone.utc).isoformat()}")
    log_lines.append("=" * 80 + "\n")

    def record_step(title: str, cmd_str: str, returncode: int, output: str) -> None:
        log_lines.append(f">>> STEP: {title}")
        log_lines.append(f"Command: {cmd_str}")
        log_lines.append(f"Exit Code: {returncode}")
        log_lines.append("--- Output ---")
        log_lines.append(output.rstrip())
        log_lines.append("-" * 80 + "\n")

    # 1. Git Status
    cmd = ["git", "status", "--short"]
    p = subprocess.run(cmd, cwd=ROOT_DIR, capture_output=True, text=True, env=env)
    record_step("Git Working Tree Status", " ".join(cmd), p.returncode, p.stdout + p.stderr)
    if p.returncode != 0:
        overall_pass = False
        failure_reasons.append("Git status check failed")

    # 2. Canonical RAW 2016 File Inspection (Strict Evaluation)
    raw_path = raw_path_override or (ROOT_DIR / "data" / "raw" / "tabular" / "2016" / "flight_with_weather_2016.csv")
    src_res = evaluate_source_integrity(raw_path)
    source_step_exit_code = 0 if src_res["valid"] else 1

    if not src_res["valid"]:
        overall_pass = False
        reasons = []
        if not src_res["exists"]:
            reasons.append("source file missing")
        if not src_res["size_match"]:
            reasons.append(f"size mismatch ({src_res['byte_size']} != {src_res['expected_size']})")
        if not src_res["sha_match"]:
            reasons.append(f"sha256 mismatch ({src_res['sha256']} != {src_res['expected_sha256']})")
        failure_reasons.append(f"Canonical 2016 RAW file integrity check failed: {', '.join(reasons)}")

    raw_output = (
        f"File: {raw_path}\n"
        f"Exists: {src_res['exists']}\n"
        f"Byte Size: {src_res['byte_size']} (Expected: {src_res['expected_size']}, Match: {src_res['size_match']})\n"
        f"SHA-256:   {src_res['sha256']}\n"
        f"Expected:  {src_res['expected_sha256']}\n"
        f"Hash Match: {src_res['sha_match']}\n"
        f"Source Integrity Verdict: {'PASS' if src_res['valid'] else 'FAIL'}\n"
        f"Audited Expected Rows: 5,537,987 (from schema_2016.json metadata catalog)"
    )
    record_step("Canonical 2016 RAW File Inspection", "internal_hash_check", source_step_exit_code, raw_output)

    # 3. Workstation Resources
    disk_c = shutil.disk_usage("C:")
    disk_d = shutil.disk_usage("D:")
    mem = psutil.virtual_memory()
    lock_dir = ROOT_DIR / "data" / "locks"
    locks_count = len(os.listdir(lock_dir)) if lock_dir.exists() else 0

    d_free_gib = disk_d.free / (1024**3)
    ram_avail_gib = mem.available / (1024**3)

    disk_pass = (d_free_gib >= 25.0)
    ram_hard_pass = (ram_avail_gib >= 3.0)

    # If allow_resource_hold is True, RAM < 3.0 GiB triggers RESOURCE_HOLD warning without hard fail
    if not disk_pass:
        overall_pass = False
        failure_reasons.append(f"Drive D: free space insufficient ({d_free_gib:.2f} GiB < 25.0 GiB policy threshold)")

    if not ram_hard_pass:
        if not allow_resource_hold:
            overall_pass = False
            failure_reasons.append(f"RAM available below operational hard minimum ({ram_avail_gib:.2f} GiB < 3.0 GiB)")

    resource_step_pass = disk_pass and (ram_hard_pass or allow_resource_hold)
    resource_exit_code = 0 if resource_step_pass else 1

    res_dict = {
        "c_drive_total_gib": round(disk_c.total / (1024**3), 2),
        "c_drive_free_gib": round(disk_c.free / (1024**3), 2),
        "d_drive_total_gib": round(disk_d.total / (1024**3), 2),
        "d_drive_free_gib": round(d_free_gib, 2),
        "ram_total_gib": round(mem.total / (1024**3), 2),
        "ram_available_gib": round(ram_avail_gib, 2),
        "ram_used_percent": mem.percent,
        "active_locks_count": locks_count,
        "resource_policy_evaluation": {
            "d_drive_threshold_policy_min_gib": 25.0,
            "d_drive_status": "PASS" if disk_pass else "FAIL",
            "ram_hard_operational_min_gib": 3.0,
            "ram_hard_status": "PASS" if ram_hard_pass else ("RESOURCE_HOLD" if allow_resource_hold else "FAIL"),
            "ram_recommended_headroom_gib": 4.0,
            "ram_recommended_status": "MEETS_RECOMMENDATION" if ram_avail_gib >= 4.0 else "BELOW_RECOMMENDATION_OPERATOR_CLEANUP_ADVISED"
        }
    }
    record_step("Workstation Resource Audit", "internal_psutil_shutil", resource_exit_code, json.dumps(res_dict, indent=2))

    # 4. Standalone Lock & Pointer Safety Preflight
    cmd = [sys.executable, "tools/qa/check_writer_preflight_safety.py", "--base-dir", "data", "--run-id", "run_2016_v1", "--json"]
    p = subprocess.run(cmd, cwd=ROOT_DIR, capture_output=True, text=True, env=env)
    record_step("Standalone Lock & Pointer Safety Preflight", " ".join(cmd), p.returncode, p.stdout + p.stderr)
    if p.returncode != 0:
        overall_pass = False
        failure_reasons.append("Standalone lock & pointer safety preflight failed")

    # 5. Staging Pointer Audit
    cmd = [sys.executable, "tools/qa/verify_staging_pointer.py", "--base-dir", "data", "--allow-uninitialized", "--json"]
    p = subprocess.run(cmd, cwd=ROOT_DIR, capture_output=True, text=True, env=env)
    record_step("Staging Pointer Audit (verify_staging_pointer.py)", " ".join(cmd), p.returncode, p.stdout + p.stderr)
    if p.returncode != 0:
        overall_pass = False
        failure_reasons.append("Staging pointer audit failed")

    # 6. Ingestion Coordinator Dry-Run Preflight (Safe Dry-Run)
    cmd = [
        sys.executable, "src/flight_pipeline/ingestion/coordinator.py",
        "--years", "2016",
        "--run-id", "run_2016_v1",
        "--base-data-dir", "data",
        "--dry-run-preflight",
        "--verify-hashes"
    ]
    p = subprocess.run(cmd, cwd=ROOT_DIR, capture_output=True, text=True, env=env)
    record_step("Ingestion Coordinator Safe Dry-Run Preflight", " ".join(cmd), p.returncode, p.stdout + p.stderr)
    if p.returncode != 0:
        overall_pass = False
        failure_reasons.append("Ingestion coordinator safe dry-run preflight failed")

    # 7. Safe Governance Hold Verification (Static Inspection + Synthetic Unit Test)
    # Never invoke live coordinator against production data directories.
    coord_file = ROOT_DIR / "src" / "flight_pipeline" / "ingestion" / "coordinator.py"
    coord_source = coord_file.read_text(encoding="utf-8") if coord_file.exists() else ""
    d5_hold_match = re.search(r"D5_AUTHORIZED_BY_PROJECT_LEAD\s*:\s*bool\s*=\s*(False|True)", coord_source)
    is_d5_blocked = bool(d5_hold_match and d5_hold_match.group(1) == "False")

    unit_test_cmd = [
        sys.executable, "-m", "unittest",
        "tests.test_coordinator_preflight_unblock.TestCoordinatorPreflightUnblock.test_09_unauthorized_live_execution_blocked"
    ]
    p_unit = subprocess.run(unit_test_cmd, cwd=ROOT_DIR, capture_output=True, text=True, env=env)

    gov_step_pass = is_d5_blocked and (p_unit.returncode == 0)
    gov_exit_code = 0 if gov_step_pass else 1

    if not gov_step_pass:
        overall_pass = False
        if not is_d5_blocked:
            failure_reasons.append("D5_AUTHORIZED_BY_PROJECT_LEAD is not False in coordinator.py")
        if p_unit.returncode != 0:
            failure_reasons.append("Synthetic unit test test_09_unauthorized_live_execution_blocked failed")

    gov_output = (
        f"Static Code Inspection: D5_AUTHORIZED_BY_PROJECT_LEAD = {d5_hold_match.group(1) if d5_hold_match else 'NOT_FOUND'}\n"
        f"Governance Hold Active: {is_d5_blocked}\n"
        f"Synthetic Unit Test Command: {' '.join(unit_test_cmd)}\n"
        f"Synthetic Unit Test Exit Code: {p_unit.returncode}\n"
        f"Synthetic Unit Test Output:\n{p_unit.stdout.strip()}\n{p_unit.stderr.strip()}\n"
        f"Safety Guarantee: No live execution invoked against production paths."
    )
    record_step("Safe Governance Hold Verification (Static + Synthetic Unit Test)", "static_and_unit_test", gov_exit_code, gov_output)

    # 8. Single-Run Validator Interface Verification
    cmd = [sys.executable, "tools/qa/verify_multiyear_snapshot.py", "--help"]
    p = subprocess.run(cmd, cwd=ROOT_DIR, capture_output=True, text=True, env=env)
    record_step("Single-Run Validator Interface Verification", " ".join(cmd), p.returncode, p.stdout + p.stderr)
    if p.returncode != 0:
        overall_pass = False
        failure_reasons.append("Single-run validator interface verification failed")

    # Summary
    log_lines.append("=" * 80)
    log_lines.append(f"PRESTART OVERALL VERDICT: {'PASS' if overall_pass else 'FAIL'}")
    if not overall_pass:
        log_lines.append(f"Failure Reasons: {'; '.join(failure_reasons)}")
    log_lines.append("=" * 80 + "\n")

    target_log_path.parent.mkdir(parents=True, exist_ok=True)
    with open(target_log_path, "w", encoding="utf-8") as f:
        f.write("\n".join(log_lines))

    print(f"Logged prestart checks to {target_log_path}")
    if overall_pass:
        print("[PRESTART CHECKS PASS] All mandatory prestart safety checks succeeded.")
        return 0
    else:
        print(f"[PRESTART CHECKS FAIL] {len(failure_reasons)} check(s) failed:")
        for r in failure_reasons:
            print(f"  - {r}")
        return 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Operational Prestart Safety Verification Runner (Task G6-T012-2016-PRESTART)")
    parser.add_argument("--allow-resource-hold", action="store_true", help="Report RESOURCE_HOLD for RAM < 3.0 GiB instead of hard failure")
    parser.add_argument("--raw-path", type=Path, default=None, help="Override path to 2016 raw source CSV for testing")
    parser.add_argument("--log-path", type=Path, default=None, help="Override output log path")
    args = parser.parse_args()

    return run_checks(
        raw_path_override=args.raw_path,
        allow_resource_hold=args.allow_resource_hold,
        output_log_path=args.log_path
    )


if __name__ == "__main__":
    sys.exit(main())
