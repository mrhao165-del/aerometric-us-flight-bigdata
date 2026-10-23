"""
Captures authentic raw test and audit output from pytest and the QA independent audit script.
Updates T014_AUTHENTIC_TEST_AND_AUDIT_LOG.txt in both the run directory and the export directory.
Re-seals the review ZIP archive and updates manifests to preserve strict cryptographic integrity.
"""

import os
import sys
import json
import time
import subprocess
import zipfile
import hashlib
import binascii
from datetime import datetime, timezone


def hash_file(filepath: str) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def crc32_file(filepath: str) -> str:
    crc = 0
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            crc = binascii.crc32(chunk, crc)
    return f"{crc & 0xFFFFFFFF:08x}"


def run_command_capture(cmd_list, description):
    start_time = time.time()
    start_iso = datetime.now(timezone.utc).isoformat()
    print(f"Executing: {' '.join(cmd_list)}")
    proc = subprocess.run(cmd_list, capture_output=True, text=True, encoding="utf-8", errors="replace")
    end_time = time.time()
    end_iso = datetime.now(timezone.utc).isoformat()
    duration = end_time - start_time

    log_section = []
    log_section.append("=" * 80)
    log_section.append(f"COMMAND: {' '.join(cmd_list)}")
    log_section.append(f"DESCRIPTION: {description}")
    log_section.append(f"START TIME (UTC): {start_iso}")
    log_section.append(f"END TIME (UTC): {end_iso}")
    log_section.append(f"EXECUTION DURATION: {duration:.2f} seconds")
    log_section.append(f"EXIT CODE: {proc.returncode}")
    log_section.append("-" * 80)
    log_section.append("STDOUT:")
    log_section.append(proc.stdout if proc.stdout else "(empty)")
    if proc.stderr:
        log_section.append("-" * 80)
        log_section.append("STDERR:")
        log_section.append(proc.stderr)
    log_section.append("=" * 80)
    log_section.append("")

    return proc.returncode, "\n".join(log_section)


def main():
    repo_root = os.path.abspath(".")
    export_dir = r"D:\Flight_Audit_Exports\T014_FULL_ANALYTICS\signoff_blocker_closeout"
    run_dir = os.path.join(repo_root, "data", "analytics", "runs", "t014_analysis_2016_2024_v4")

    overall_header = []
    overall_header.append("=" * 80)
    overall_header.append("T-014 AUTHENTIC RAW TEST AND AUDIT EXECUTION LOG")
    overall_header.append("TASK: T014-FINAL-SIGNOFF-BLOCKER-CORRECTION")
    overall_header.append("RUN ID: t014_analysis_2016_2024_v4")
    overall_header.append(f"TIMESTAMP: {datetime.now(timezone.utc).isoformat()}")
    overall_header.append(f"HOST OS: Windows (win32)")
    overall_header.append(f"PYTHON EXECUTABLE: {sys.executable}")
    overall_header.append(f"PYTHON VERSION: {sys.version}")
    overall_header.append("UPSTREAM INPUT RUN: kpi_run_2016_2024_v1 (54,674,003 accepted flights, 684,180 KPI rows)")
    overall_header.append("=" * 80)
    overall_header.append("")

    # 1. Run pytest
    py_exec = sys.executable
    cmd_pytest = [py_exec, "-m", "pytest", "tests/test_t014_analytics_comprehensive.py", "-v"]
    rc_pytest, log_pytest = run_command_capture(cmd_pytest, "Pytest Comprehensive Test Suite (29 tests)")

    # 2. Run QA Independent Audit
    cmd_audit = [py_exec, "tools/qa/run_t014_independent_audit.py"]
    rc_audit, log_audit = run_command_capture(cmd_audit, "QA Independent Data Integrity and Release Audit (91 checks)")

    summary = []
    summary.append("=" * 80)
    summary.append("TEST AND AUDIT EXECUTION SUMMARY")
    summary.append(f"Pytest Exit Code: {rc_pytest} ({'PASS' if rc_pytest == 0 else 'FAIL'})")
    summary.append(f"QA Audit Exit Code: {rc_audit} ({'PASS' if rc_audit == 0 else 'FAIL'})")
    overall_pass = (rc_pytest == 0 and rc_audit == 0)
    summary.append(f"Overall Status: {'PASS' if overall_pass else 'FAIL'}")
    summary.append(f"Verdict: {'T014_SIGNOFF_BLOCKERS_RESOLVED_READY_FOR_HUMAN_SIGNOFF' if overall_pass else 'T014_BLOCKED'}")
    summary.append("=" * 80)

    full_log_text = "\n".join(overall_header) + log_pytest + "\n" + log_audit + "\n" + "\n".join(summary)

    # Write to files
    log_dest_export = os.path.join(export_dir, "T014_AUTHENTIC_TEST_AND_AUDIT_LOG.txt")
    log_dest_run = os.path.join(run_dir, "T014_AUTHENTIC_TEST_AND_AUDIT_LOG.txt")
    log_dest_final = os.path.join(export_dir, "T014_FINAL_TEST_AND_AUDIT_LOG.txt")
    log_dest_run_final = os.path.join(run_dir, "T014_FINAL_TEST_AND_AUDIT_LOG.txt")

    for p in [log_dest_export, log_dest_run, log_dest_final, log_dest_run_final]:
        with open(p, "w", encoding="utf-8") as f:
            f.write(full_log_text)
    print(f"Wrote authentic log to: {log_dest_export}")

    # Re-package ZIP archives cleanly with mode 'w' to preserve exactly 70 members
    zip_pairs = [
        ("T014_FINAL_REVIEW.zip", "T014_FINAL_REVIEW_MANIFEST.json"),
        ("T014_FINAL_SEALED_REVIEW.zip", "T014_FINAL_SEALED_REVIEW_MANIFEST.json"),
    ]

    for zn, mn in zip_pairs:
        zip_path = os.path.join(export_dir, zn)
        member_hashes = {}
        with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            # 1. Tables (12 CSV + 12 Parquet = 24)
            tables_dir = os.path.join(run_dir, "tables")
            for tbl_file in sorted(os.listdir(tables_dir)):
                p = os.path.join(tables_dir, tbl_file)
                arcname = f"tables/{tbl_file}"
                zf.write(p, arcname)
                member_hashes[arcname] = hash_file(p)

            # 2. Charts (16 PNG + 16 SVG = 32)
            charts_dir = os.path.join(run_dir, "charts")
            for chart_file in sorted(os.listdir(charts_dir)):
                p = os.path.join(charts_dir, chart_file)
                arcname = f"charts/{chart_file}"
                zf.write(p, arcname)
                member_hashes[arcname] = hash_file(p)

            # 3. Documents & Manifests (14 files)
            doc_entries = [
                ("T014_ANALYTICAL_FINDINGS_REPORT.md", os.path.join(run_dir, "T014_ANALYTICAL_FINDINGS_REPORT.md")),
                ("RESULTS_REGISTER.json", os.path.join(run_dir, "RESULTS_REGISTER.json")),
                ("CHART_INVENTORY.json", os.path.join(run_dir, "CHART_INVENTORY.json")),
                ("analytics_run_manifest.json", os.path.join(run_dir, "analytics_run_manifest.json")),
                ("T014_FINAL_EVIDENCE_CLOSEOUT_REPORT.md", os.path.join(export_dir, "T014_FINAL_EVIDENCE_CLOSEOUT_REPORT.md")),
                ("T014_SIGNOFF_BLOCKER_CORRECTION_REPORT.md", os.path.join(export_dir, "T014_SIGNOFF_BLOCKER_CORRECTION_REPORT.md")),
                ("T014_FINAL_RES_COHORT_RECONCILIATION.json", os.path.join(export_dir, "T014_FINAL_RES_COHORT_RECONCILIATION.json")),
                ("T014_FINAL_CHART_SEMANTIC_TRACEABILITY.json", os.path.join(export_dir, "T014_FINAL_CHART_SEMANTIC_TRACEABILITY.json")),
                ("T014_CORRECTED_CHART_SEMANTIC_VERIFICATION.json", os.path.join(export_dir, "T014_CORRECTED_CHART_SEMANTIC_VERIFICATION.json")),
                ("T014_ROUTE_YEAR_NUMERICAL_RECONCILIATION.json", os.path.join(export_dir, "T014_ROUTE_YEAR_NUMERICAL_RECONCILIATION.json")),
                ("T014_FINAL_TEST_AND_AUDIT_LOG.txt", log_dest_final),
                ("T014_AUTHENTIC_TEST_AND_AUDIT_LOG.txt", log_dest_export),
                ("T014_FINAL_CHANGES.patch", os.path.join(export_dir, "T014_FINAL_CHANGES.patch")),
                ("T014_BLOCKER_FIX_CHANGES.patch", os.path.join(export_dir, "T014_BLOCKER_FIX_CHANGES.patch")),
            ]
            for doc_arc, doc_file in doc_entries:
                zf.write(doc_file, doc_arc)
                member_hashes[doc_arc] = hash_file(doc_file)

        zip_sha = hash_file(zip_path)
        zip_crc = crc32_file(zip_path)
        zip_bytes = os.path.getsize(zip_path)

        manifest_path = os.path.join(export_dir, mn)
        review_manifest = {
            "archive_filename": zn,
            "archive_sha256": zip_sha,
            "archive_crc32_hex": zip_crc,
            "archive_bytes": zip_bytes,
            "created_at_utc": datetime.now(timezone.utc).isoformat(),
            "total_members": len(member_hashes),
            "member_hashes": member_hashes,
        }
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(review_manifest, f, indent=2)
        print(f"Re-sealed {zn} ({zip_bytes:,d} bytes, SHA-256: {zip_sha[:16]}..., members: {len(member_hashes)})")

    print("\nRe-running independent audit on updated sealed package...")
    final_audit = subprocess.run([py_exec, "tools/qa/run_t014_independent_audit.py"], capture_output=True, text=True, encoding="utf-8")
    print(final_audit.stdout)
    if final_audit.returncode != 0:
        print("ERROR in final audit:\n", final_audit.stderr)
        sys.exit(1)

    print("Authentic log capture and sealed package verification COMPLETE.")


if __name__ == "__main__":
    main()
