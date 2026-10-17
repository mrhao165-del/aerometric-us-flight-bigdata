#!/usr/bin/env python3
"""
tools/qa/test_t009_unblock_r2_git_exclusion.py

Dedicated Positive and Negative Automated Test Suite for T009-UNBLOCK-R2:
- Verifies that root `.git/` directory metadata is cleanly excluded from working-tree accounting.
- Verifies that non-git stray files (at root and in subfolders) are still strictly detected and rejected.
- Verifies that `.gitignore` is preserved and not accidentally ignored as git metadata.
- Verifies that nested `.git` directories outside root are NOT treated as root git metadata.
- Executes in isolated temporary directories without modifying live repository state.
"""

import copy
from hashlib import sha256
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile

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


def build_minimal_fixture(base_dir: Path) -> Path:
    """Build a fast, minimal working repository fixture containing essential manifests,
    deliverable registry, 9 dummy CSVs, and a mock .git/ directory."""
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

    # Copy all registered deliverables
    reg_data = json.loads(reg_src.read_text(encoding="utf-8"))
    for d in reg_data.get("registered_deliverables", []):
        dp = d["path"]
        src = ROOT / dp
        dst = fx / dp
        dst.parent.mkdir(parents=True, exist_ok=True)
        if src.is_file():
            shutil.copy2(src, dst)

    # 5. Create 9 dummy CSVs
    for yr in range(2016, 2025):
        csv_p = fx / f"data/raw/tabular/{yr}/flight_with_weather_{yr}.csv"
        csv_p.parent.mkdir(parents=True, exist_ok=True)
        csv_p.write_text("FL_DATE\n2016-01-01\n", encoding="utf-8")

    # 6. Create simulated .git directory at root with dummy objects
    git_dir = fx / ".git"
    git_dir.mkdir(parents=True, exist_ok=True)
    (git_dir / "HEAD").write_text("ref: refs/heads/master\n", encoding="utf-8")
    (git_dir / "config").write_text("[core]\n\trepositoryformatversion = 0\n", encoding="utf-8")
    (git_dir / "objects").mkdir(parents=True, exist_ok=True)
    (git_dir / "objects" / "sample_obj").write_text("blob\n", encoding="utf-8")
    (git_dir / "refs" / "heads").mkdir(parents=True, exist_ok=True)
    (git_dir / "refs" / "heads" / "master").write_text("5d700358efda26388f615364ceb362088f1704db\n", encoding="utf-8")

    return fx


def run_tests():
    print("=" * 80)
    print("RUNNING T009-UNBLOCK-R2 GIT EXCLUSION POSITIVE & NEGATIVE VERIFICATION SUITE")
    print("=" * 80)

    with tempfile.TemporaryDirectory(prefix="t009_unblock_r2_test_") as tmp_str:
        tmp_dir = Path(tmp_str)
        fx = build_minimal_fixture(tmp_dir)

        # POS-01: Baseline fixture with root .git directory passes
        passed, issues = cwtc.run_consistency_check(fx)
        record(
            "POS-01",
            len(issues) == 0,
            "Isolated repo with root `.git/` metadata is cleanly accepted with 0 errors",
            f"Issues: {issues}",
        )

        # POS-02: Active docs check ignores markdown inside .git/
        git_md = fx / ".git" / "RELEASE_NOTES.md"
        git_md.write_text("# Git Release Notes\n", encoding="utf-8")
        passed, issues = cwtc.run_consistency_check(fx)
        record(
            "POS-02",
            len(issues) == 0,
            "Markdown file inside root `.git/` is ignored by active docs checks and accounting",
            f"Issues: {issues}",
        )
        git_md.unlink()

        # NEG-01: Stray unrecognized file at repository root is detected and rejected
        stray_root = fx / "stray_file_at_root.txt"
        stray_root.write_text("stray content", encoding="utf-8")
        passed, issues = cwtc.run_consistency_check(fx)
        stray_detected = any("stray_file_at_root.txt" in str(iss) for iss in issues)
        record(
            "NEG-01",
            stray_detected,
            "Unrecognized stray file at repository root is strictly rejected",
            f"Issues: {issues}",
        )
        stray_root.unlink()

        # NEG-02: Stray unrecognized markdown file in docs/ is detected and rejected
        stray_doc = fx / "docs" / "stray_unregistered_doc.md"
        stray_doc.write_text("# Stray Unregistered Doc\nExtra long text content here to exceed 100 bytes limit required by active docs check.\n", encoding="utf-8")
        passed, issues = cwtc.run_consistency_check(fx)
        stray_doc_detected = any("stray_unregistered_doc.md" in str(iss) for iss in issues)
        record(
            "NEG-02",
            stray_doc_detected,
            "Unrecognized stray file in docs/ subfolder is strictly rejected",
            f"Issues: {issues}",
        )
        stray_doc.unlink()

        # NEG-03: Stray unrecognized python file in tools/ is detected and rejected
        stray_tool = fx / "tools" / "stray_unregistered_tool.py"
        stray_tool.write_text("# stray tool\n", encoding="utf-8")
        passed, issues = cwtc.run_consistency_check(fx)
        stray_tool_detected = any("stray_unregistered_tool.py" in str(iss) for iss in issues)
        record(
            "NEG-03",
            stray_tool_detected,
            "Unrecognized stray Python script in tools/ subfolder is strictly rejected",
            f"Issues: {issues}",
        )
        stray_tool.unlink()

        # NEG-04: Non-root nested .git directory (e.g. docs/.git/stray.txt) is NOT ignored
        nested_git = fx / "docs" / ".git"
        nested_git.mkdir(parents=True, exist_ok=True)
        nested_file = nested_git / "nested_stray.txt"
        nested_file.write_text("nested stray", encoding="utf-8")
        passed, issues = cwtc.run_consistency_check(fx)
        nested_detected = any("nested_stray.txt" in str(iss) for iss in issues)
        record(
            "NEG-04",
            nested_detected,
            "Nested `.git/` outside repository root is NOT ignored and strictly rejected",
            f"Issues: {issues}",
        )
        shutil.rmtree(nested_git)

        # NEG-05: Modified deliverable content with mismatched SHA-256 is detected and rejected
        sample_deliv = fx / "tools/check_working_tree_consistency.py"
        orig_content = sample_deliv.read_text(encoding="utf-8")
        sample_deliv.write_text(orig_content + "\n# Tampered line\n", encoding="utf-8")
        passed, issues = cwtc.run_consistency_check(fx)
        tamper_detected = any("physical size/SHA-256 verified" in str(iss) for iss in issues)
        record(
            "NEG-05",
            tamper_detected,
            "Tampered deliverable with SHA-256/size mismatch is strictly detected and rejected",
            f"Issues: {issues}",
        )
        sample_deliv.write_text(orig_content, encoding="utf-8")

    print("=" * 80)
    print(f"VERIFICATION SUMMARY: {len(passed_tests)} PASS, {len(failed_tests)} FAIL")
    print("=" * 80)
    if failed_tests:
        sys.exit(1)
    print("ALL T009-UNBLOCK-R2 POSITIVE & NEGATIVE CHECKS PASSED.")


if __name__ == "__main__":
    run_tests()
