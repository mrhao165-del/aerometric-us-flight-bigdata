"""
Automated positive and negative security and compatibility test suite for T-009 validator extension.
Tests authorized path categories:
- src/flight_pipeline/**/*.py
- tests/**/*.py
- requirements.txt
- .github/workflows/*.yml
And verifies strict rejection of unauthorized files, extensions, and tampered contents.
"""

import copy
from hashlib import sha256
import json
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


def build_test_fixture(base_dir: Path) -> Path:
    """Build a fast, minimal working repository fixture."""
    fx = base_dir / "fixture_repo"
    fx.mkdir(parents=True, exist_ok=True)

    # Copy PACKAGE_MANIFEST.json
    shutil.copy2(ROOT / "PACKAGE_MANIFEST.json", fx / "PACKAGE_MANIFEST.json")

    # Copy files from PACKAGE_MANIFEST.json
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

    # Copy SOURCE_MANIFEST.json
    src_man = ROOT / "docs/05-evidence/inputs/SOURCE_MANIFEST.json"
    if src_man.is_file():
        dst_man = fx / "docs/05-evidence/inputs/SOURCE_MANIFEST.json"
        dst_man.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src_man, dst_man)

    # Copy EVIDENCE_DELIVERABLE_REGISTER.json
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

    # 9 dummy CSVs
    for yr in range(2016, 2025):
        csv_p = fx / f"data/raw/tabular/{yr}/flight_with_weather_{yr}.csv"
        csv_p.parent.mkdir(parents=True, exist_ok=True)
        csv_p.write_text("FL_DATE\n2016-01-01\n", encoding="utf-8")

    # Root .git metadata
    git_dir = fx / ".git"
    git_dir.mkdir(parents=True, exist_ok=True)
    (git_dir / "HEAD").write_text("ref: refs/heads/master\n", encoding="utf-8")
    (git_dir / "config").write_text("[core]\n\trepositoryformatversion = 0\n", encoding="utf-8")

    return fx


def run_tests():
    print("=" * 80)
    print("RUNNING T009-R1 VALIDATOR POLICY EXTENSION SECURITY & COMPATIBILITY SUITE")
    print("=" * 80)

    with tempfile.TemporaryDirectory(prefix="t009_val_ext_test_") as tmp_str:
        tmp_dir = Path(tmp_str)
        fx = build_test_fixture(tmp_dir)

        # Baseline check
        passed, issues = cwtc.run_consistency_check(fx)
        record("BASE-01", len(issues) == 0, "Base fixture satisfies all checks", f"Issues: {issues}")

        # NEG-01: Unregistered .py file in src/flight_pipeline/ is rejected
        stray_src = fx / "src/flight_pipeline/stray_module.py"
        stray_src.parent.mkdir(parents=True, exist_ok=True)
        stray_src.write_text("# stray src\n", encoding="utf-8")
        passed, issues = cwtc.run_consistency_check(fx)
        record("NEG-01", any("stray_module.py" in str(i) for i in issues), "Unregistered .py in src/ is rejected", f"Issues: {issues}")
        stray_src.unlink()

        # NEG-02: Unregistered .py file in tests/ is rejected
        stray_test = fx / "tests/test_stray.py"
        stray_test.parent.mkdir(parents=True, exist_ok=True)
        stray_test.write_text("# stray test\n", encoding="utf-8")
        passed, issues = cwtc.run_consistency_check(fx)
        record("NEG-02", any("test_stray.py" in str(i) for i in issues), "Unregistered .py in tests/ is rejected", f"Issues: {issues}")
        stray_test.unlink()

        # NEG-03: Unauthorized extension in src/ (e.g. .sh) is rejected even if registered
        reg_p = fx / "docs/05-evidence/EVIDENCE_DELIVERABLE_REGISTER.json"
        reg = json.loads(reg_p.read_text(encoding="utf-8"))
        bad_src = fx / "src/flight_pipeline/bad.sh"
        bad_src.write_text("#!/bin/sh\n", encoding="utf-8")
        reg_tamper = copy.deepcopy(reg)
        reg_tamper["registered_deliverables"].append({
            "path": "src/flight_pipeline/bad.sh",
            "task_id": "T-009",
            "artifact_type": "SOURCE_CODE",
            "bytes": bad_src.stat().st_size,
            "sha256": sha256(bad_src.read_bytes()).hexdigest(),
            "authorization_ref": "test",
        })
        reg_p.write_text(json.dumps(reg_tamper, indent=2), encoding="utf-8")
        passed, issues = cwtc.run_consistency_check(fx)
        record("NEG-03", any("bad.sh" in str(i) for i in issues), "Non-.py extension in src/ is strictly rejected", f"Issues: {issues}")
        bad_src.unlink()
        reg_p.write_text(json.dumps(reg, indent=2), encoding="utf-8")

        # NEG-04: Unauthorized root file (.env) is rejected
        env_file = fx / ".env"
        env_file.write_text("SECRET=12345\n", encoding="utf-8")
        passed, issues = cwtc.run_consistency_check(fx)
        record("NEG-04", any(".env" in str(i) for i in issues), "Unauthorized root .env file is strictly rejected", f"Issues: {issues}")
        env_file.unlink()

        # POS-01: Valid registered source file in src/flight_pipeline/ is accepted
        valid_src = fx / "src/flight_pipeline/valid_module.py"
        valid_src.write_text("# valid module\n", encoding="utf-8")
        reg_pos = copy.deepcopy(reg)
        reg_pos["registered_deliverables"].append({
            "path": "src/flight_pipeline/valid_module.py",
            "task_id": "T-009",
            "artifact_type": "SOURCE_CODE",
            "bytes": valid_src.stat().st_size,
            "sha256": sha256(valid_src.read_bytes()).hexdigest(),
            "authorization_ref": "Project Lead T-009 instruction",
        })
        reg_p.write_text(json.dumps(reg_pos, indent=2), encoding="utf-8")
        passed, issues = cwtc.run_consistency_check(fx)
        record("POS-01", len(issues) == 0, "Registered .py in src/flight_pipeline/ is accepted", f"Issues: {issues}")
        valid_src.unlink()
        reg_p.write_text(json.dumps(reg, indent=2), encoding="utf-8")

        # POS-02: Valid registered requirements.txt is accepted
        req_orig_content = (fx / "requirements.txt").read_bytes() if (fx / "requirements.txt").is_file() else None
        req_file = fx / "requirements.txt"
        req_file.write_text("pyspark==4.0.1\n", encoding="utf-8")
        reg_pos2 = copy.deepcopy(reg)
        reg_pos2["registered_deliverables"] = [x for x in reg_pos2["registered_deliverables"] if x["path"] != "requirements.txt"]
        reg_pos2["registered_deliverables"].append({
            "path": "requirements.txt",
            "task_id": "T-009",
            "artifact_type": "DEPENDENCY_SPEC",
            "bytes": req_file.stat().st_size,
            "sha256": sha256(req_file.read_bytes()).hexdigest(),
            "authorization_ref": "Project Lead T-009 instruction",
        })
        reg_p.write_text(json.dumps(reg_pos2, indent=2), encoding="utf-8")
        passed, issues = cwtc.run_consistency_check(fx)
        record("POS-02", len(issues) == 0, "Registered requirements.txt at root is accepted", f"Issues: {issues}")
        if req_orig_content is not None:
            req_file.write_bytes(req_orig_content)
        else:
            req_file.unlink()
        reg_p.write_text(json.dumps(reg, indent=2), encoding="utf-8")

        # POS-03: Valid registered CI workflow in .github/workflows/ is accepted
        ci_file = fx / ".github/workflows/test_workflow.yml"
        ci_file.parent.mkdir(parents=True, exist_ok=True)
        ci_file.write_text("name: Test CI\n", encoding="utf-8")
        reg_pos3 = copy.deepcopy(reg)
        reg_pos3["registered_deliverables"] = [x for x in reg_pos3["registered_deliverables"] if x["path"] != ".github/workflows/test_workflow.yml"]
        reg_pos3["registered_deliverables"].append({
            "path": ".github/workflows/test_workflow.yml",
            "task_id": "T-009",
            "artifact_type": "CI_CONFIG",
            "bytes": ci_file.stat().st_size,
            "sha256": sha256(ci_file.read_bytes()).hexdigest(),
            "authorization_ref": "Project Lead T-009 instruction",
        })
        reg_p.write_text(json.dumps(reg_pos3, indent=2), encoding="utf-8")
        passed, issues = cwtc.run_consistency_check(fx)
        record("POS-03", len(issues) == 0, "Registered .github/workflows/*.yml is accepted", f"Issues: {issues}")
        ci_file.unlink()
        reg_p.write_text(json.dumps(reg, indent=2), encoding="utf-8")

    print("=" * 80)
    print(f"VERIFICATION SUMMARY: {len(passed_tests)} PASS, {len(failed_tests)} FAIL")
    print("=" * 80)
    if failed_tests:
        sys.exit(1)
    print("ALL T009-R1 VALIDATOR EXTENSION TESTS PASSED.")


if __name__ == "__main__":
    run_tests()
