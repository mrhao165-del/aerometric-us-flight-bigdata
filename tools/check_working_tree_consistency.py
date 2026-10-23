#!/usr/bin/env python3
"""Working-tree consistency verifier for flight docs repository.
Checks documentary integrity, manifest preservation, and working-tree additions.
Designed for active workspace where raw data and task evidence reports are present.
Can be imported as a module (`run_consistency_check(root_dir)`) for isolated regression testing.
"""
from pathlib import Path
from hashlib import sha256
import json, re, sys

ALLOWED_TASK_GATE_IDS = (
    {f"T-{i:03d}" for i in range(1, 18)}
    | {f"G{i}" for i in range(0, 8)}
    | {
        "G2-FINAL-REVIEW",
        "G2-R1",
        "G2-SIGNOFF-PREP",
        "G2-SIGNOFF-PRECHECK",
        "G2-SIGNOFF-HANDOFF-FIX",
        "G2-REPO-APPLY",
        "G2-REPO-APPLY-R1",
        "G2-FINAL-FIX",
        "G2-FINAL-CLOSEOUT",
        "G2-OFFICIAL-SIGNOFF",
        "G3-T006",
        "G3-T006-R1",
        "T-006-R1",
        "G3-OFFICIAL-SIGNOFF",
    }
)

ALLOWED_GOVERNED_LIVING_DOCS = {
    "docs/01-planning/BACKLOG.md",
    "docs/02-design/ARCHITECTURE.md",
    "docs/02-design/DECISIONS.md",
    "docs/02-design/KPI_SPEC.md",
    "docs/03-quality/CHANGELOG.md",
    "docs/03-quality/RISK_REGISTER.md",
    "docs/04-execution/AI_HANDOFF.md",
    "docs/04-execution/TASK_TEMPLATE.md",
}

ALLOWED_ARTIFACT_TYPES = {
    "AUDIT_REPORT",
    "PRE_CHANGE_BACKUP",
    "GOVERNANCE_PACKAGE",
    "TEST_FIXTURE",
    "AUDIT_SCRIPT",
    "QA_SCRIPT",
    "SYNTHETIC_TEST_REPORT",
    "CODE_AND_REGRESSION_AUDIT",
    "ERRATA_REPORT",
    "AUTOMATED_VERIFICATION_SCRIPT",
    "TEST_SUITE",
    "EXECUTION_MANIFEST",
    "SOURCE_CODE",
    "TEST_MODULE",
    "DEPENDENCY_SPEC",
    "CI_CONFIG",
}

ALLOWED_DELIVERABLE_EXTENSIONS = {
    ".md",
    ".csv",
    ".json",
    ".py",
    ".bak",
    ".txt",
    ".yml",
    ".yaml",
}
ALLOWED_LIVING_DOC_EXTENSIONS = {".md"}
HEX64_RE = re.compile(r"^[0-9a-f]{64}$")
EVIDENCE_FILENAME_RE = re.compile(
    r"^(?:T0(?:0[1-9]|1[0-7])|G[0-7]|FP|TS018)_[A-Za-z0-9_.\-]+\.(?:md|csv|json|txt)$"
)
BACKUP_FILENAME_RE = re.compile(
    r"^[A-Za-z0-9_.\-]+\.pre_g2_repo_apply\.bak$"
)
FINAL_FIX_BACKUP_FILENAME_RE = re.compile(
    r"^[A-Za-z0-9_.\-]+\.pre_g2_final_fix\.bak$"
)
OFFICIAL_SIGNOFF_BACKUP_FILENAME_RE = re.compile(
    r"^[A-Za-z0-9_.\-]+\.pre_g2_official_signoff\.bak$"
)
T006_BACKUP_FILENAME_RE = re.compile(
    r"^[A-Za-z0-9_.\-]+\.pre_t006\.bak$"
)
T006_R1_BACKUP_FILENAME_RE = re.compile(
    r"^[A-Za-z0-9_.\-]+\.pre_t006_r1\.bak$"
)
TS018_BACKUP_FILENAME_RE = re.compile(
    r"^[A-Za-z0-9_.\-]+\.pre_ts018\.bak$"
)

PINNED_SOURCE_MANIFEST_BYTES = 2479
PINNED_SOURCE_MANIFEST_SHA256 = (
    "5e11e619790e475260b19c70630d8faef9a902c9d55d2ca641320163c87447fc"
)
PINNED_PACKAGE_MANIFEST_BYTES = 8354
PINNED_PACKAGE_MANIFEST_SHA256 = (
    "7c457207a6fefd2a45ad56a4c8ee8e3fb6194b8462f6ee24985f4e9534d61df1"
)


def _is_safe_rel_path(rel_path: str, root: Path) -> bool:
    if not isinstance(rel_path, str) or not rel_path:
        return False
    if "\\" in rel_path or rel_path.startswith("/") or ":" in rel_path:
        return False
    parts = rel_path.split("/")
    if any(p in ("", ".", "..") for p in parts):
        return False
    candidate = root / rel_path
    try:
        resolved_root = root.resolve()
        # Strictly reject any symlinks along the path
        cur = root
        for part in parts:
            cur = cur / part
            if cur.is_symlink():
                return False
        if candidate.exists():
            candidate.resolve().relative_to(resolved_root)
    except Exception:
        return False
    return True


def run_consistency_check(root_dir: Path, ci_mode: bool = False):
    root = Path(root_dir).resolve()
    issues = []
    passed = []

    def require(v, msg):
        if v:
            passed.append(msg)
        else:
            issues.append(msg)

    def load(rel):
        return (root / rel).read_text(encoding="utf-8")

    # 1. Core documentary structure (18 ABC + 8 supplementary)
    core_paths = {
        "A": [
            "README.md",
            "AGENTS.md",
            "docs/01-planning/PRD.md",
            "docs/01-planning/ROADMAP.md",
            "docs/01-planning/BACKLOG.md",
            "docs/02-design/ARCHITECTURE.md",
        ],
        "B": [
            "docs/03-quality/TEST_PLAN.md",
            "docs/03-quality/RISK_REGISTER.md",
            "docs/02-design/DECISIONS.md",
            "docs/03-quality/CHANGELOG.md",
            "docs/03-quality/ROLLBACK_PLAN.md",
            "docs/03-quality/SECURITY.md",
        ],
        "C": [
            "docs/04-execution/PROJECT_STATE.md",
            "docs/04-execution/AI_HANDOFF.md",
            "docs/04-execution/TASK_TEMPLATE.md",
            "docs/02-design/API_CONTRACTS.md",
            "docs/02-design/DATA_DICTIONARY.md",
            "docs/04-execution/DEPLOYMENT.md",
        ],
        "supplementary": [
            "docs/02-design/DATA_CONTRACT.md",
            "docs/02-design/KPI_SPEC.md",
            "docs/02-design/ANALYSIS_PROTOCOL.md",
            "docs/05-evidence/DATA_PROVENANCE.md",
            "docs/05-evidence/DATA_QUALITY_REPORT.md",
            "docs/05-evidence/RESULTS_REGISTER.md",
            "docs/03-quality/G0_G1_REVIEW.md",
            "docs/00-governance/DOCUMENT_REGISTER.md",
        ],
    }
    paths = sum(core_paths.values(), [])
    require(
        all((root / p).is_file() for p in paths),
        "18 A/B/C + 8 supplementary paths exist",
    )
    require(
        len(set(paths)) == 26
        and all(len(v) == 6 for k, v in core_paths.items() if k != "supplementary")
        and len(core_paths["supplementary"]) == 8,
        "Doc group counts and unique roles",
    )

    active = [
        f
        for f in root.rglob("*.md")
        if "inputs" not in f.parts and f.relative_to(root).parts[0] != ".git"
    ]
    require(all(f.stat().st_size > 100 for f in active), "Active docs are nonempty")

    # 2. Markdown reference integrity (no broken docs/... paths)
    path_pat = re.compile(
        r"(?<![A-Za-z0-9_./])(?:docs/(?:[A-Za-z0-9_.()\-]+/)+[A-Za-z0-9_.()\-]+\.(?:md|json))(?![A-Za-z0-9_.\-])"
    )
    refbad = []
    for f in active:
        for n, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
            for x in path_pat.findall(line):
                if not (root / x).is_file():
                    refbad.append(f"{f.relative_to(root)}:{n}:{x}")
    require(
        not refbad,
        "All explicitly written docs/... MD/JSON paths resolve"
        + (": " + repr(refbad[:12]) if refbad else ""),
    )

    # 3. Relative link resolution in all markdown files
    link_pat = re.compile(r"\[([^\]]+)\]\((?:<([^>]+)>|([^)]+))\)")
    broken_links = []
    for f in active:
        content = f.read_text(encoding="utf-8")
        for match in link_pat.finditer(content):
            text, u1, u2 = match.groups()
            url = u1 or u2
            if not url or url.startswith(
                ("http://", "https://", "#", "mailto:", "conversation://", "file:///")
            ):
                continue
            clean_url = url.split("#")[0]
            if clean_url and not (f.parent / clean_url).resolve().exists():
                broken_links.append(f"{f.relative_to(root)} -> {url}")
    require(
        not broken_links,
        "All relative markdown links resolve correctly"
        + (": " + repr(broken_links[:10]) if broken_links else ""),
    )

    # 4. No stale tokens
    for bad in ("`HANDOFF.md`", "TEST-013 logs", "Khóa 5 KPI lõi"):
        require(
            not any(
                bad in f.read_text(encoding="utf-8")
                for f in active
                if f.name
                not in (
                    "CHANGELOG.md",
                    "V1_0_CONSISTENCY_AUDIT.md",
                    "DOCS_CONSISTENCY_AUDIT_v1.1.md",
                )
            ),
            "No stale actionable token " + bad,
        )

    # 5. Core glossary and definitions
    dc = load("docs/02-design/DATA_CONTRACT.md")
    kpi = load("docs/02-design/KPI_SPEC.md")
    for s in (
        "raw_row_count = accepted_row_count + quarantined_row_count + rejected_row_count",
        "count_metric_valid",
        "metric_valid_rate",
        "source_coverage_status",
        "IDENTITY_UNVERIFIED",
        "METADATA_MATCH_ONLY",
    ):
        require(s in dc, "DC owns " + s)
    require(
        "accepted_row_count(C)" in dc and "ZERO_DENOMINATOR" in dc,
        "Group denominator and zero guard",
    )
    require(
        "KPI-01..08" in load("docs/01-planning/ROADMAP.md")
        and "KPI-01..08" in load("docs/01-planning/BACKLOG.md"),
        "8 CORE KPIs in roadmap and backlog",
    )

    # 6. KPI catalog ordering and CORE_DRAFT
    rows = re.findall(r"^\|\s*(KPI-\d\d)\s*\|.*$", kpi, re.M)
    require(
        rows == [f"KPI-{i:02d}" for i in range(1, 13)],
        "KPI catalog exactly 01..12 ordered",
    )
    require(
        sum(
            bool(re.search(r"^\|\s*KPI-(?:0[1-8])\s*\|.*CORE_DRAFT", l))
            for l in kpi.splitlines()
        )
        == 8,
        "8 CORE_DRAFT rows",
    )

    # 7. Task DAG and acyclicity
    backlog = load("docs/01-planning/BACKLOG.md")
    tasks = {}
    deps = {}
    for line in backlog.splitlines():
        m = re.match(
            r"^\|\s*(T-\d{3})\s*\|\s*(G\d)\s*\|(.+?)\|(.+?)\|(.+?)\|(.+?)\|\s*$", line
        )
        if m:
            task, gate, descr, dependency, accept, status = m.groups()
            tasks[task] = gate
            deps[task] = re.findall(r"T-\d{3}", dependency)
    require(set(tasks) == {f"T-{i:03d}" for i in range(1, 18)}, "Exactly T-001..017")
    require(
        deps.get("T-007") == ["T-009"]
        and deps.get("T-008") == ["T-007"]
        and deps.get("T-009") == ["T-006"],
        "T-009->T-007->T-008 dependency",
    )
    visited = set()
    path = set()

    def dfs(k):
        if k in path:
            return False
        if k in visited:
            return True
        path.add(k)
        if not all(dfs(d) for d in deps[k]):
            return False
        path.remove(k)
        visited.add(k)
        return True

    require(all(dfs(k) for k in tasks), "Task dependencies acyclic")

    # 8. Test catalog TS-001..TS-020
    testtext = load("docs/03-quality/TEST_PLAN.md")
    defined_tests = re.findall(r"^\|\s*(TS-\d{3})\s*\|", testtext, re.M)
    require(
        defined_tests == [f"TS-{i:03d}" for i in range(1, 21)],
        "Test catalog exactly TS-001..020 ordered",
    )

    # 9. Results Register slots
    results = load("docs/05-evidence/RESULTS_REGISTER.md")
    res_ids = re.findall(r"^\|\s*(RES-\d{3})\s*\|", results, re.M)
    require(
        res_ids == [f"RES-{i:03d}" for i in range(1, 13)],
        "RES-001..012 planned exactly once",
    )
    require(
        "NO_PRODUCTION_RESULTS" in results
        and not re.search(r"\|\s*PASS\s*\|$", results, re.M),
        "No fabricated production results",
    )

    # 10. Immutable source manifest
    source_manifest_path = root / "docs/05-evidence/inputs/SOURCE_MANIFEST.json"
    require(
        source_manifest_path.is_file()
        and source_manifest_path.stat().st_size == PINNED_SOURCE_MANIFEST_BYTES
        and sha256(source_manifest_path.read_bytes()).hexdigest()
        == PINNED_SOURCE_MANIFEST_SHA256,
        "SOURCE_MANIFEST.json pinned hash and size verified",
    )
    source = json.loads(source_manifest_path.read_text(encoding="utf-8"))
    for x in source["sources"]:
        f = root / x["path"]
        require(
            f.is_file()
            and len(f.read_bytes()) == x["bytes"]
            and sha256(f.read_bytes()).hexdigest() == x["sha256"],
            "Input immutable " + x["path"],
        )

    # 11. Load and validate EVIDENCE_DELIVERABLE_REGISTER.json (fail-closed)
    reg_rel = "docs/05-evidence/EVIDENCE_DELIVERABLE_REGISTER.json"
    reg_path = root / reg_rel
    require(reg_path.is_file(), "EVIDENCE_DELIVERABLE_REGISTER.json exists")

    reg_data = None
    living_overrides = {}
    registered_deliverables = {}

    if reg_path.is_file():
        try:
            reg_data = json.loads(reg_path.read_text(encoding="utf-8"))
            require(
                isinstance(reg_data, dict)
                and reg_data.get("registry_version") == "1.0"
                and isinstance(reg_data.get("governed_living_docs"), list)
                and isinstance(reg_data.get("registered_deliverables"), list),
                "EVIDENCE_DELIVERABLE_REGISTER.json schema structure valid",
            )
        except Exception as exc:
            require(
                False, f"EVIDENCE_DELIVERABLE_REGISTER.json valid JSON: {exc}"
            )
            reg_data = None

    # 12. Release package manifest verification + governed living docs verification
    pm_path = root / "PACKAGE_MANIFEST.json"
    require(
        pm_path.is_file()
        and pm_path.stat().st_size == PINNED_PACKAGE_MANIFEST_BYTES
        and sha256(pm_path.read_bytes()).hexdigest()
        == PINNED_PACKAGE_MANIFEST_SHA256,
        "PACKAGE_MANIFEST.json pinned hash and size verified",
    )
    if pm_path.exists():
        pm = json.loads(pm_path.read_text(encoding="utf-8"))
        pm_by_path = {obj["path"]: obj for obj in pm["generated_files"]}
        manifest_paths = set(pm_by_path.keys())

        if reg_data and isinstance(reg_data.get("governed_living_docs"), list):
            seen_living = set()
            for entry in reg_data["governed_living_docs"]:
                p = entry.get("path", "")
                valid_entry = (
                    isinstance(entry, dict)
                    and p not in seen_living
                    and _is_safe_rel_path(p, root)
                    and Path(p).suffix in ALLOWED_LIVING_DOC_EXTENSIONS
                    and p in ALLOWED_GOVERNED_LIVING_DOCS
                    and p in pm_by_path
                    and not p.startswith("docs/05-evidence/inputs/")
                    and p not in ("PACKAGE_MANIFEST.json", "tools/check_docs_consistency.py")
                    and entry.get("original_v1_1_bytes") == pm_by_path[p]["bytes"]
                    and entry.get("original_v1_1_sha256") == pm_by_path[p]["sha256"]
                    and isinstance(entry.get("current_bytes"), int)
                    and entry.get("current_bytes", 0) > 0
                    and bool(HEX64_RE.match(str(entry.get("current_sha256", ""))))
                    and isinstance(entry.get("backup_path"), str)
                    and _is_safe_rel_path(entry.get("backup_path", ""), root)
                    and isinstance(entry.get("authorization_ref"), str)
                    and len(entry.get("authorization_ref", "")) > 0
                )
                require(
                    valid_entry,
                    f"Governed living doc entry valid and preserves v1.1 baseline metadata: {p}",
                )
                if valid_entry:
                    seen_living.add(p)
                    bfile = root / entry["backup_path"]
                    backup_ok = (
                        bfile.is_file()
                        and bfile.stat().st_size == entry["original_v1_1_bytes"]
                        and sha256(bfile.read_bytes()).hexdigest()
                        == entry["original_v1_1_sha256"]
                    )
                    require(
                        backup_ok,
                        f"Governed living doc pre-change backup verified against v1.1 hash: {p}",
                    )
                    living_overrides[p] = entry

        for obj in pm["generated_files"]:
            name = obj["path"]
            ff = root / name
            if name in living_overrides:
                ov = living_overrides[name]
                require(
                    ff.is_file()
                    and ff.stat().st_size == ov["current_bytes"]
                    and sha256(ff.read_bytes()).hexdigest() == ov["current_sha256"],
                    "Governed living doc verified: " + name,
                )
            elif name == "docs/04-execution/PROJECT_STATE.md":
                st_txt = ff.read_text(encoding="utf-8")
                if "| G2 | PASS |" in st_txt:
                    acc_rec = root / "docs/05-evidence/G2_OFFICIAL_SIGNOFF_HUMAN_ACCEPTANCE_RECORD.md"
                    require(
                        acc_rec.is_file() and "APPROVED_BY_PROJECT_LEAD_EXPLICIT_INSTRUCTION" in acc_rec.read_text(encoding="utf-8"),
                        "Official G2 acceptance record verified when G2 is PASS",
                    )
                if "| G3 | PASS |" in st_txt:
                    acc_rec_g3 = root / "docs/05-evidence/G3_OFFICIAL_SIGNOFF_HUMAN_ACCEPTANCE_RECORD.md"
                    require(
                        acc_rec_g3.is_file()
                        and "APPROVED_BY_PROJECT_LEAD_EXPLICIT_INSTRUCTION" in acc_rec_g3.read_text(encoding="utf-8")
                        and "G3-COND-A" in acc_rec_g3.read_text(encoding="utf-8")
                        and "G3-COND-B" in acc_rec_g3.read_text(encoding="utf-8")
                        and "G3-COND-C" in acc_rec_g3.read_text(encoding="utf-8"),
                        "Official G3 acceptance record verified when G3 is PASS",
                    )
                require(
                    ff.exists()
                    and ff.stat().st_size > 500
                    and "T-001" in st_txt,
                    "Living project state verified: " + name,
                )
            elif name == ".gitignore":
                gitign_txt = ff.read_text(encoding="utf-8")
                require(
                    ff.is_file()
                    and "data/raw/" in gitign_txt
                    and "/data/reference/" in gitign_txt,
                    "Governed .gitignore verified: " + name,
                )
            else:
                require(
                    ff.exists()
                    and ff.stat().st_size == obj["bytes"]
                    and sha256(ff.read_bytes()).hexdigest() == obj["sha256"],
                    "Package manifest verified: " + name,
                )

        # 13. Validate registered deliverables in EVIDENCE_DELIVERABLE_REGISTER.json
        if reg_data and isinstance(reg_data.get("registered_deliverables"), list):
            seen_deliv = set()
            for item in reg_data["registered_deliverables"]:
                dp = item.get("path", "")
                tid = item.get("task_id", "")
                atype = item.get("artifact_type", "")
                ebytes = item.get("bytes")
                esha = str(item.get("sha256", ""))
                aref = item.get("authorization_ref", "")

                # Allowed location and naming rules
                ext = Path(dp).suffix
                fname = Path(dp).name
                loc_ok = False
                if dp.startswith("docs/05-evidence/G2_REPO_APPLY_BACKUPS/"):
                    loc_ok = bool(BACKUP_FILENAME_RE.match(fname))
                elif dp.startswith("docs/05-evidence/G2_FINAL_FIX_BACKUPS/"):
                    loc_ok = bool(FINAL_FIX_BACKUP_FILENAME_RE.match(fname))
                elif dp.startswith("docs/05-evidence/G2_OFFICIAL_SIGNOFF_BACKUPS/"):
                    loc_ok = bool(OFFICIAL_SIGNOFF_BACKUP_FILENAME_RE.match(fname))
                elif dp.startswith("docs/05-evidence/T006_BACKUPS/"):
                    loc_ok = bool(T006_BACKUP_FILENAME_RE.match(fname))
                elif dp.startswith("docs/05-evidence/T006_R1_BACKUPS/"):
                    loc_ok = bool(T006_R1_BACKUP_FILENAME_RE.match(fname))
                elif dp.startswith("docs/05-evidence/TS018_BACKUPS/"):
                    loc_ok = bool(TS018_BACKUP_FILENAME_RE.match(fname))
                elif dp.startswith("docs/05-evidence/") and "/" not in dp[len("docs/05-evidence/"):]:
                    loc_ok = bool(EVIDENCE_FILENAME_RE.match(fname))
                elif dp == "tools/check_working_tree_consistency.py":
                    loc_ok = True
                elif dp.startswith("tools/audit/") or dp.startswith("tools/qa/"):
                    loc_ok = ext in (".py", ".json") and "/" not in dp.split("/", 2)[2]
                elif dp.startswith("src/flight_pipeline/"):
                    loc_ok = ext == ".py"
                elif dp.startswith("tests/"):
                    loc_ok = ext == ".py"
                elif dp == "requirements.txt":
                    loc_ok = True
                elif dp.startswith(".github/workflows/"):
                    loc_ok = ext in (".yml", ".yaml")

                meta_ok = (
                    isinstance(item, dict)
                    and dp not in seen_deliv
                    and dp != reg_rel
                    and dp not in manifest_paths
                    and _is_safe_rel_path(dp, root)
                    and ext in ALLOWED_DELIVERABLE_EXTENSIONS
                    and loc_ok
                    and tid in ALLOWED_TASK_GATE_IDS
                    and atype in ALLOWED_ARTIFACT_TYPES
                    and isinstance(ebytes, int)
                    and ebytes > 0
                    and bool(HEX64_RE.match(esha))
                    and isinstance(aref, str)
                    and len(aref) > 0
                )
                require(
                    meta_ok,
                    f"Registered deliverable metadata & security rules valid: {dp}",
                )
                if meta_ok:
                    seen_deliv.add(dp)
                    df = root / dp
                    content_ok = (
                        df.is_file()
                        and df.stat().st_size == ebytes
                        and sha256(df.read_bytes()).hexdigest() == esha
                    )
                    require(
                        content_ok,
                        f"Registered deliverable physical size/SHA-256 verified: {dp}",
                    )
                    if content_ok:
                        registered_deliverables[dp] = item

        # 14. Working-tree accounting: All files in repo are either manifest release files, raw data, the registry itself, or verified registered deliverables
        # Check that no symlinks exist anywhere in the working-tree (excluding root .git)
        symlinks_in_repo = [
            f.relative_to(root).as_posix()
            for f in root.rglob("*")
            if f.is_symlink() and f.relative_to(root).parts[0] != ".git"
        ]
        require(
            len(symlinks_in_repo) == 0,
            "No symbolic links in working-tree"
            + (": " + repr(symlinks_in_repo[:5]) if symlinks_in_repo else ""),
        )
        # Ignore transient Python bytecode cache files (__pycache__ / .pyc) and root .git metadata
        actual_files = {
            f.relative_to(root).as_posix()
            for f in root.rglob("*")
            if (f.is_file() or f.is_symlink())
            and f.name != "PACKAGE_MANIFEST.json"
            and "__pycache__" not in f.parts
            and not f.name.endswith(".pyc")
            and f.relative_to(root).parts[0] != ".git"
        }
        extra_files = actual_files - manifest_paths

        raw_data_files = {
            f
            for f in extra_files
            if f.startswith("data/raw/tabular/") and f.endswith(".csv")
        }
        # Governed reference data policy (TS-018):
        # 1. Allowed reference subtree: strictly data/reference/bts_transtats/
        # 2. Every reference file must match an entry in TS018_201901_ORIGINAL_AND_DERIVED_HASH_MANIFEST.json
        ref_manifest_path = root / "docs/05-evidence/TS018_201901_ORIGINAL_AND_DERIVED_HASH_MANIFEST.json"
        known_ref_artifacts = {}
        if ref_manifest_path.is_file():
            try:
                ref_man_data = json.loads(ref_manifest_path.read_text(encoding="utf-8"))
                for art in ref_man_data.get("artifacts", []):
                    known_ref_artifacts[art["path"]] = art
            except Exception:
                pass

        reference_data_files = set()
        for f in extra_files:
            if f.startswith("data/reference/"):
                in_allowed_subtree = f.startswith("data/reference/bts_transtats/")
                require(
                    in_allowed_subtree,
                    f"Reference file within allowed subtree (data/reference/bts_transtats/): {f}",
                )
                if f in known_ref_artifacts:
                    expected_ref = known_ref_artifacts[f]
                    rf_p = root / f
                    hash_matches = (
                        rf_p.is_file()
                        and rf_p.stat().st_size == expected_ref["bytes"]
                        and sha256(rf_p.read_bytes()).hexdigest() == expected_ref["sha256"]
                    )
                    require(
                        hash_matches,
                        f"Reference file physical hash and size match manifest: {f}",
                    )
                    if in_allowed_subtree and hash_matches:
                        reference_data_files.add(f)
                else:
                    require(
                        False,
                        f"Reference data file registered in TS018 reference manifest: {f}",
                    )
        registry_self = {reg_rel} if reg_path.is_file() else set()
        verified_deliv_paths = set(registered_deliverables.keys())

        unrecognized = (
            extra_files - raw_data_files - reference_data_files - registry_self - verified_deliv_paths
        )
        missing_registered = verified_deliv_paths - extra_files

        if ci_mode:
            require(
                len(raw_data_files) == 0,
                "CI clean-checkout mode: raw data files excluded from Git tracking as required by repository policy",
            )
        else:
            require(
                len(raw_data_files) == 9,
                "Working-tree contains exactly 9 raw CSV files (2016-2024)",
            )
        require(
            len(missing_registered) == 0,
            "All registered deliverables present in working-tree"
            + (": " + repr(sorted(missing_registered)) if missing_registered else ""),
        )
        require(
            len(unrecognized) == 0,
            "No unrecognized stray files in working-tree"
            + (": " + repr(sorted(unrecognized)) if unrecognized else ""),
        )
        require(
            len(extra_files)
            == len(raw_data_files) + len(reference_data_files) + len(registry_self) + len(verified_deliv_paths),
            "All extra working-tree files cleanly accounted for",
        )

    return passed, issues


def main():
    root = Path(__file__).resolve().parents[1]
    ci_mode = "--ci-mode" in sys.argv or "--repo-only" in sys.argv
    passed, issues = run_consistency_check(root, ci_mode=ci_mode)
    print(f"Working-Tree PASS assertions: {len(passed)}; FAIL: {len(issues)}")
    for i in issues:
        print("FAIL:", i)
    if issues:
        sys.exit(1)
    print("ALL WORKING-TREE CHECKS PASSED.")


if __name__ == "__main__":
    main()
