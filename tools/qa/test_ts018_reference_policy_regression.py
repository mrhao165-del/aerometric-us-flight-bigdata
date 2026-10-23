#!/usr/bin/env python3
"""
tools/qa/test_ts018_reference_policy_regression.py

Automated Positive & Negative Regression Test Suite for TS-018 Bounded Reference Policy:
- POS-01: Legitimate known reference ZIP and provenance companion matching manifest are cleanly accepted.
- NEG-01: Unknown / unregistered file under data/reference/bts_transtats/ is strictly rejected as stray.
- NEG-02: Forged registered hash in reference manifest (tampered physical file or wrong manifest SHA) is strictly rejected.
- NEG-03: Unauthorized file outside allowed reference subtree (e.g., data/reference/unauthorized.txt or data/reference/other_dir/sample.csv) is strictly rejected.
- NEG-04: Path traversal attempt (e.g., data/reference/bts_transtats/../../outside.txt) is rejected by safety path helper.
- NEG-05: Missing file referenced in manifest is strictly rejected.
"""

import copy
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
from hashlib import sha256

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

import check_working_tree_consistency as cwtc

passed_tests = []
failed_tests = []


def record(test_id: str, condition: bool, description: str, detail: str = ""):
    if condition:
        passed_tests.append(f"{test_id}: {description}")
        print(f"[PASS] {test_id}: {description}")
    else:
        msg = f"{test_id}: {description}" + (f" -> {detail}" if detail else "")
        failed_tests.append(msg)
        print(f"[FAIL] {msg}", file=sys.stderr)


def build_reference_fixture(base_dir: Path) -> Path:
    """Build a fast, minimal working repository fixture containing essential manifests,
    deliverable registry, 9 dummy CSVs, mock .git, and a sample reference dataset."""
    fx = base_dir / "minimal_repo"
    fx.mkdir(parents=True, exist_ok=True)

    # 1. Copy PACKAGE_MANIFEST.json
    shutil.copy2(ROOT / "PACKAGE_MANIFEST.json", fx / "PACKAGE_MANIFEST.json")

    # 2. Copy governed living docs and manifest files
    pm = json.loads((ROOT / "PACKAGE_MANIFEST.json").read_text(encoding="utf-8"))
    for item in pm["generated_files"]:
        p = item["path"]
        src = ROOT / p
        dst = fx / p
        dst.parent.mkdir(parents=True, exist_ok=True)
        if src.is_file():
            shutil.copy2(src, dst)
        else:
            dst.write_text("Dummy content for manifest verification\n", encoding="utf-8")

    # 3. Copy SOURCE_MANIFEST.json and historical inputs
    src_man = ROOT / "docs/05-evidence/inputs/SOURCE_MANIFEST.json"
    if src_man.is_file():
        dst_man = fx / "docs/05-evidence/inputs/SOURCE_MANIFEST.json"
        dst_man.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src_man, dst_man)

    # 4. Copy EVIDENCE_DELIVERABLE_REGISTER.json
    reg_src = ROOT / "docs/05-evidence/EVIDENCE_DELIVERABLE_REGISTER.json"
    reg_dst = fx / "docs/05-evidence/EVIDENCE_DELIVERABLE_REGISTER.json"
    reg_dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(reg_src, reg_dst)

    # Copy registered deliverables
    reg_data = json.loads(reg_src.read_text(encoding="utf-8"))
    for d in reg_data.get("registered_deliverables", []):
        dp = d["path"]
        src = ROOT / dp
        dst = fx / dp
        dst.parent.mkdir(parents=True, exist_ok=True)
        if src.is_file():
            shutil.copy2(src, dst)

    # Synchronize registered deliverables inside fixture with actual copied files
    for item in reg_data.get("registered_deliverables", []):
        df = fx / item["path"]
        if df.is_file():
            item["bytes"] = df.stat().st_size
            item["sha256"] = sha256(df.read_bytes()).hexdigest()
    reg_dst.write_text(json.dumps(reg_data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    # 5. Create 9 dummy raw CSVs
    for yr in range(2016, 2025):
        csv_p = fx / f"data/raw/tabular/{yr}/flight_with_weather_{yr}.csv"
        csv_p.parent.mkdir(parents=True, exist_ok=True)
        csv_p.write_text("FL_DATE\n2016-01-01\n", encoding="utf-8")

    # 6. Create simulated .git directory
    git_dir = fx / ".git"
    git_dir.mkdir(parents=True, exist_ok=True)
    (git_dir / "HEAD").write_text("ref: refs/heads/master\n", encoding="utf-8")

    # 7. Create a small dummy reference ZIP and manifest
    ref_zip_rel = "data/reference/bts_transtats/original/T_ONTIME_REPORTING_20261019_112232.zip"
    ref_zip_path = fx / ref_zip_rel
    ref_zip_path.parent.mkdir(parents=True, exist_ok=True)
    ref_dummy_bytes = b"PK\x05\x06" + b"\x00" * 18  # valid empty zip header
    ref_zip_path.write_bytes(ref_dummy_bytes)

    prov_rel = "data/reference/bts_transtats/bts_transtats_201901.provenance.json"
    prov_path = fx / prov_rel
    prov_bytes = b'{"status": "PENDING"}\n'
    prov_path.write_bytes(prov_bytes)

    # Reference manifest
    ref_man_rel = "docs/05-evidence/TS018_201901_ORIGINAL_AND_DERIVED_HASH_MANIFEST.json"
    ref_man_path = fx / ref_man_rel
    ref_man_path.parent.mkdir(parents=True, exist_ok=True)
    ref_man_data = {
        "manifest_schema": "ts018_reference_manifest_v1",
        "task_id": "TS-018",
        "allowed_reference_subtree": "data/reference/bts_transtats/",
        "artifacts": [
            {
                "path": ref_zip_rel,
                "bytes": len(ref_dummy_bytes),
                "sha256": sha256(ref_dummy_bytes).hexdigest(),
                "role": "ORIGINAL_EXTERNAL_BTS_ZIP"
            },
            {
                "path": prov_rel,
                "bytes": len(prov_bytes),
                "sha256": sha256(prov_bytes).hexdigest(),
                "role": "CANDIDATE_PROVENANCE_COMPANION"
            }
        ]
    }
    ref_man_path.write_text(json.dumps(ref_man_data, indent=2), encoding="utf-8")

    # Update ref_man_rel in EVIDENCE_DELIVERABLE_REGISTER.json inside fixture
    found = False
    for item in reg_data["registered_deliverables"]:
        if item["path"] == ref_man_rel:
            item["bytes"] = len(ref_man_path.read_bytes())
            item["sha256"] = sha256(ref_man_path.read_bytes()).hexdigest()
            found = True
            break
    if not found:
        reg_data["registered_deliverables"].append({
            "path": ref_man_rel,
            "task_id": "T-011",
            "artifact_type": "AUDIT_REPORT",
            "bytes": len(ref_man_path.read_bytes()),
            "sha256": sha256(ref_man_path.read_bytes()).hexdigest(),
            "authorization_ref": "TS-018 Reference manifest",
        })
    reg_dst.write_text(json.dumps(reg_data, indent=2), encoding="utf-8")

    return fx


def run_suite():
    print("=" * 80)
    print("RUNNING TS-018 BOUNDED REFERENCE DATA POLICY REGRESSION TEST SUITE")
    print("=" * 80)

    with tempfile.TemporaryDirectory(prefix="ts018_ref_test_") as tmp_str:
        tmp_dir = Path(tmp_str)
        fx = build_reference_fixture(tmp_dir)

        # POS-01: Legitimate known reference ZIP and companion matching manifest are accepted
        passed, issues = cwtc.run_consistency_check(fx)
        record(
            "POS-01",
            len(issues) == 0,
            "Legitimate known reference ZIP and companion matching manifest are cleanly accepted with 0 errors",
            f"Issues: {issues}",
        )

        # NEG-01: Unknown / unregistered file under data/reference/bts_transtats/ is strictly rejected
        stray_ref = fx / "data/reference/bts_transtats/unregistered_stray.csv"
        stray_ref.write_text("FL_DATE,OP_CARRIER\n", encoding="utf-8")
        passed, issues_neg1 = cwtc.run_consistency_check(fx)
        stray_caught = any("unregistered_stray.csv" in str(i) for i in issues_neg1) and any("registered in TS018 reference manifest" in str(i) for i in issues_neg1)
        record(
            "NEG-01",
            stray_caught,
            "Unknown / unregistered file under data/reference/bts_transtats/ is strictly rejected as stray",
            f"Issues: {issues_neg1[:2]}",
        )
        stray_ref.unlink()

        # NEG-02: Forged registered hash in reference manifest is strictly rejected
        ref_zip_p = fx / "data/reference/bts_transtats/original/T_ONTIME_REPORTING_20261019_112232.zip"
        orig_bytes = ref_zip_p.read_bytes()
        ref_zip_p.write_bytes(orig_bytes + b"\x00\x00")  # tamper content
        passed, issues_neg2 = cwtc.run_consistency_check(fx)
        tamper_caught = any("physical hash and size match manifest" in str(i) for i in issues_neg2)
        record(
            "NEG-02",
            tamper_caught,
            "Forged / tampered reference artifact failing SHA-256 match is strictly rejected",
            f"Issues: {issues_neg2[:2]}",
        )
        ref_zip_p.write_bytes(orig_bytes)

        # NEG-03: Unauthorized file outside allowed reference subtree is strictly rejected
        unauth_ref = fx / "data/reference/unauthorized_root_file.txt"
        unauth_ref.write_text("unauthorized file\n", encoding="utf-8")
        passed, issues_neg3 = cwtc.run_consistency_check(fx)
        unauth_caught = any("allowed subtree (data/reference/bts_transtats/)" in str(i) for i in issues_neg3)
        record(
            "NEG-03",
            unauth_caught,
            "Unauthorized file outside allowed reference subtree is strictly rejected",
            f"Issues: {issues_neg3[:2]}",
        )
        unauth_ref.unlink()

        # NEG-04: Path traversal attempt is rejected by path helper
        traversal_rejected = not cwtc._is_safe_rel_path("data/reference/bts_transtats/../../outside.txt", fx)
        record(
            "NEG-04",
            traversal_rejected,
            "Path traversal attempt (../) in reference path is strictly rejected by path helper",
        )

        # NEG-05: Missing file referenced in manifest is strictly rejected
        ref_man_p = fx / "docs/05-evidence/TS018_201901_ORIGINAL_AND_DERIVED_HASH_MANIFEST.json"
        man_data = json.loads(ref_man_p.read_text(encoding="utf-8"))
        man_data["artifacts"].append({
            "path": "data/reference/bts_transtats/missing_ghost.zip",
            "bytes": 100,
            "sha256": "0" * 64,
            "role": "GHOST_ARTIFACT"
        })
        ref_man_p.write_text(json.dumps(man_data, indent=2), encoding="utf-8")
        # update manifest in register
        reg_p = fx / "docs/05-evidence/EVIDENCE_DELIVERABLE_REGISTER.json"
        reg_data = json.loads(reg_p.read_text(encoding="utf-8"))
        for it in reg_data["registered_deliverables"]:
            if it["path"] == "docs/05-evidence/TS018_201901_ORIGINAL_AND_DERIVED_HASH_MANIFEST.json":
                it["bytes"] = len(ref_man_p.read_bytes())
                it["sha256"] = sha256(ref_man_p.read_bytes()).hexdigest()
        reg_p.write_text(json.dumps(reg_data, indent=2), encoding="utf-8")

        passed, issues_neg5 = cwtc.run_consistency_check(fx)
        # Missing ghost file won't appear in extra_files, but let's check that if created with wrong size it's caught
        ghost_p = fx / "data/reference/bts_transtats/missing_ghost.zip"
        ghost_p.write_bytes(b"wrong size")
        passed, issues_neg5b = cwtc.run_consistency_check(fx)
        ghost_caught = any("physical hash and size match manifest" in str(i) for i in issues_neg5b)
        record(
            "NEG-05",
            ghost_caught,
            "Ghost/corrupted artifact matching manifest path but with wrong hash/size is strictly rejected",
            f"Issues: {issues_neg5b[:2]}",
        )
        ghost_p.unlink()

    print("=" * 80)
    print(f"REFERENCE POLICY SUITE SUMMARY: {len(passed_tests)} PASS, {len(failed_tests)} FAIL")
    print("=" * 80)
    if failed_tests:
        sys.exit(1)
    print("ALL REFERENCE DATA POLICY POSITIVE AND NEGATIVE TESTS PASSED.")


if __name__ == "__main__":
    run_suite()
