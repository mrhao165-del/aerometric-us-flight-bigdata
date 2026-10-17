#!/usr/bin/env python3
"""
tools/qa/verify_t004_time_representation.py
Authoritative QA script verifying T-004 Safe Time Representation Audit,
2024 Calendar Coverage, Overnight Counterexamples, Annual Row Counts,
and Test Fixture Specifications.

Updated for T-004 FINAL QA & Evidence Sign-Off (QA-01..QA-04).
Exit code 0 on PASS, 1 on any failure.
"""

import sys
import re
import csv
import json
from pathlib import Path
from zoneinfo import ZoneInfo
from datetime import datetime

ROOT = Path(__file__).resolve().parent.parent.parent

passed_assertions = []
failed_assertions = []


def check(condition: bool, name: str, details: str = ""):
    if condition:
        passed_assertions.append(name)
        print(f"[PASS] {name}")
    else:
        msg = f"{name} -> {details}" if details else name
        failed_assertions.append(msg)
        print(f"[FAIL] {msg}")


def run_checks() -> int:
    print("=" * 80)
    print("RUNNING T-004 FINAL QA: SOURCE COUNT RECONCILIATION & TEMPORAL AUDIT")
    print("=" * 80)

    # -------------------------------------------------------------------------
    # 1. Verify Existence of all T-004 Evidence Artifacts & Fixtures
    # -------------------------------------------------------------------------
    expected_docs = [
        "docs/05-evidence/T004_TIME_REPRESENTATION_AUDIT.md",
        "docs/05-evidence/T004_2024_DATE_COVERAGE_AUDIT.md",
        "docs/05-evidence/T004_OVERNIGHT_COUNTEREXAMPLES.md",
        "docs/05-evidence/T004_SAFE_FIELDS_DECISION.md",
        "docs/05-evidence/T004_TEST_FIXTURE_SPEC.md",
        "docs/05-evidence/T004_FINAL_REVIEW.md",
        "docs/05-evidence/T004_TF09_temporal_fixture.csv",
        "docs/05-evidence/T004_TF09_full_schema_fixture.csv",
        "docs/05-evidence/T004_TF09_temporal_fixture.json",
        "docs/05-evidence/T004_R1_INDEPENDENT_RECONCILIATION.md",
        "docs/05-evidence/T004_FINAL_QA_RECONCILIATION.md",
    ]

    for rel_path in expected_docs:
        fpath = ROOT / rel_path
        check(fpath.exists(), f"Artifact exists: {rel_path}", str(fpath))
        if fpath.exists():
            check(fpath.stat().st_size > 100, f"Artifact non-empty: {rel_path}")

    # -------------------------------------------------------------------------
    # 2. QA-01: Reconcile Annual Row Counts Across Schema Audits & Docs
    # -------------------------------------------------------------------------
    authoritative_row_counts = {
        2016: 5537987,
        2017: 5575872,
        2018: 6986842,
        2019: 7161827,
        2020: 4312091,
        2021: 5755666,
        2022: 6413416,
        2023: 6645461,
        2024: 6284841,
    }

    schema_dir = ROOT / "docs/05-evidence/inputs"
    total_schema_rows = 0
    for y, expected_cnt in authoritative_row_counts.items():
        sf = schema_dir / f"schema_{y}.json"
        check(sf.exists(), f"Schema file exists: schema_{y}.json")
        if sf.exists():
            sd = json.loads(sf.read_text(encoding="utf-8"))
            rc = sd.get("row_count")
            check(rc == expected_cnt, f"schema_{y}.json row_count matches authoritative ({rc} == {expected_cnt})")
            total_schema_rows += rc

    check(total_schema_rows == 54674003, f"Sum of 9 schema row counts is exactly 54,674,003 ({total_schema_rows})")

    # Verify row counts in T004_R1_INDEPENDENT_RECONCILIATION.md
    r1_path = ROOT / "docs/05-evidence/T004_R1_INDEPENDENT_RECONCILIATION.md"
    if r1_path.exists():
        r1_text = r1_path.read_text(encoding="utf-8")
        for y, expected_cnt in authoritative_row_counts.items():
            cnt_str = f"{expected_cnt:,}".replace(",", ".")
            cnt_raw_str = f"{expected_cnt:,}"
            found = cnt_raw_str in r1_text or cnt_str in r1_text or str(expected_cnt) in r1_text
            check(found, f"T004_R1 multi-year table contains authoritative count for {y} ({expected_cnt})")

    # Verify row counts in T004_FINAL_QA_RECONCILIATION.md
    qa_path = ROOT / "docs/05-evidence/T004_FINAL_QA_RECONCILIATION.md"
    if qa_path.exists():
        qa_text = qa_path.read_text(encoding="utf-8")
        for y, expected_cnt in authoritative_row_counts.items():
            cnt_str = f"{expected_cnt:,}".replace(",", ".")
            cnt_raw_str = f"{expected_cnt:,}"
            found = cnt_raw_str in qa_text or cnt_str in qa_text or str(expected_cnt) in qa_text
            check(found, f"T004_FINAL_QA table contains authoritative count for {y} ({expected_cnt})")

    # -------------------------------------------------------------------------
    # 3. QA-02: Preserve Original YX 3624 Records
    # -------------------------------------------------------------------------
    overnight_path = ROOT / "docs/05-evidence/T004_OVERNIGHT_COUNTEREXAMPLES.md"
    if overnight_path.exists():
        on_text = overnight_path.read_text(encoding="utf-8")
        check("6,384,132" in on_text and "6,384,133" in on_text, "Physical line numbers for YX 3624 cited")
        check("877.0" in on_text and "20.0" in on_text, "DEP_DELAY values (+877.0 and +20.0) verified")
        check("941.0" in on_text and "4.0" in on_text, "ARR_DELAY values (+941.0 and +4.0) verified")
        check("13.0" in on_text and "83.0" in on_text and "6.0" in on_text and "102.0" in on_text,
              "Row B taxi and air values (13.0 / 83.0 / 6.0 / 102.0) preserved in overnight audit")
        check("VERIFIED" in on_text and "INFERRED" in on_text and "UNKNOWN" in on_text,
              "Section 2.3 strict 3-tier boundary (VERIFIED / INFERRED / UNKNOWN) implemented")
        check("PHYSICAL_EVENT_IDENTITY_UNKNOWN" in on_text or "PHYSICAL_ENTITY_IDENTITY_UNKNOWN" in on_text,
              "Physical entity identity classified as UNKNOWN (lack of TAIL_NUM)")
        check("UPSTREAM_CODE_UNKNOWN" in on_text, "Upstream ETL code classified as UPSTREAM_CODE_UNKNOWN")
        check("CẤM TUYỆT ĐỐI" in on_text, "Mandatory prohibitions on timestamp subtraction documented")

    if r1_path.exists():
        check("13.0" in r1_text and "83.0" in r1_text and "6.0" in r1_text,
              "Row B raw values (13.0 / 83.0 / 6.0) verified in T004_R1 Section 3.1")

    if qa_path.exists():
        check("13.0" in qa_text and "83.0" in qa_text and "6.0" in qa_text and "102.0" in qa_text,
              "Row B raw values (13.0 / 83.0 / 6.0 / 102.0) verified in T004_FINAL_QA Section 3")

    # -------------------------------------------------------------------------
    # 4. QA-03: Fixture & Timezone Contract
    # -------------------------------------------------------------------------
    # 4a. 18-column Temporal Test Projection CSV
    csv_18_path = ROOT / "docs/05-evidence/T004_TF09_temporal_fixture.csv"
    if csv_18_path.exists():
        raw_csv_lines = [l for l in csv_18_path.read_text(encoding="utf-8").splitlines() if l.strip()]
        check(len(raw_csv_lines) == 10, f"Temporal fixture CSV has exactly 10 lines, got {len(raw_csv_lines)}")
        check(all(not l.startswith("#") for l in raw_csv_lines), "Temporal fixture CSV contains no '#' comments")
        with open(csv_18_path, "r", encoding="utf-8") as f:
            reader_18 = list(csv.DictReader(f))
            check(len(reader_18) == 9, f"Temporal CSV parsed exactly 9 rows, got {len(reader_18)}")
            check(len(reader_18[0]) == 18, f"Temporal CSV has exactly 18 columns, got {len(reader_18[0])}")

    # 4b. 34-column Full Schema Ingestion CSV
    csv_34_path = ROOT / "docs/05-evidence/T004_TF09_full_schema_fixture.csv"
    if csv_34_path.exists():
        raw_34_lines = [l for l in csv_34_path.read_text(encoding="utf-8").splitlines() if l.strip()]
        check(len(raw_34_lines) == 10, f"Full schema CSV has exactly 10 lines, got {len(raw_34_lines)}")
        check(all(not l.startswith("#") for l in raw_34_lines), "Full schema CSV contains no '#' comments")
        with open(csv_34_path, "r", encoding="utf-8") as f:
            reader_34 = list(csv.DictReader(f))
            check(len(reader_34) == 9, f"Full schema CSV parsed exactly 9 rows, got {len(reader_34)}")
            check(len(reader_34[0]) == 34, f"Full schema CSV has exactly 34 columns, got {len(reader_34[0])}")

    # 4c. JSON Oracle & Invariants
    json_path = ROOT / "docs/05-evidence/T004_TF09_temporal_fixture.json"
    if json_path.exists():
        with open(json_path, "r", encoding="utf-8") as f:
            fixture_json = json.load(f)
        fixtures = fixture_json.get("fixtures", [])
        check(len(fixtures) == 9, f"JSON oracle contains 9 fixture objects, got {len(fixtures)}")

        all_delay_bal = True
        all_decomp = True
        for fx in fixtures:
            fid = fx["fixture_id"]
            inp = fx["inputs"]
            arr_delay = inp["ARR_DELAY"]
            dep_delay = inp["DEP_DELAY"]
            crs_elap = inp["CRS_ELAPSED_TIME"]
            act_elap = inp["ACTUAL_ELAPSED_TIME"]
            tax_out = inp["TAXI_OUT"]
            air = inp["AIR_TIME"]
            tax_in = inp["TAXI_IN"]

            if arr_delay != dep_delay + (act_elap - crs_elap):
                all_delay_bal = False
            if act_elap != tax_out + air + tax_in:
                all_decomp = False

        check(all_delay_bal, "Delay balance invariant holds on all 9 fixtures")
        check(all_decomp, "Elapsed time decomposition invariant holds on all 9 fixtures")

        # 4d. Historical Timezone IANA Verification
        expected_tz = {
            "TF-01": {"orig": "America/Chicago", "dest": "America/Chicago", "offset": 0, "orig_name": "CDT", "dest_name": "CDT"},
            "TF-02": {"orig": "America/Los_Angeles", "dest": "America/New_York", "offset": 3, "orig_name": "PDT", "dest_name": "EDT"},
            "TF-03": {"orig": "America/New_York", "dest": "America/New_York", "offset": 0, "orig_name": "EDT", "dest_name": "EDT"},
            "TF-04": {"orig": "America/New_York", "dest": "America/New_York", "offset": 0, "orig_name": "EDT", "dest_name": "EDT"},
            "TF-05": {"orig": "America/New_York", "dest": "America/New_York", "offset": 0, "orig_name": "EDT", "dest_name": "EDT"},
            "TF-06": {"orig": "America/Los_Angeles", "dest": "America/Phoenix", "offset": 1, "orig_name": "PST", "dest_name": "MST"},
            "TF-07": {"orig": "America/Los_Angeles", "dest": "America/Anchorage", "offset": -1, "orig_name": "PST", "dest_name": "AKST"},
            "TF-08": {"orig": "America/Denver", "dest": "America/Chicago", "offset": 1, "orig_name": "MDT", "dest_name": "CDT"},
            "TF-09": {"orig": "America/Los_Angeles", "dest": "America/New_York", "offset": 3, "orig_name": "PDT", "dest_name": "EDT"},
        }

        all_tz_ok = True
        for fx in fixtures:
            fid = fx["fixture_id"]
            ref = expected_tz[fid]
            if fx.get("iana_origin_tz") != ref["orig"] or fx.get("iana_dest_tz") != ref["dest"]:
                all_tz_ok = False
            if fx.get("tz_offset_hours") != ref["offset"]:
                all_tz_ok = False
            if ref["orig_name"] not in fx.get("origin_tz", "") or ref["dest_name"] not in fx.get("dest_tz", ""):
                all_tz_ok = False

        check(all_tz_ok, "Historical IANA timezones and DST abbreviations verified across all 9 fixtures")

        # TF-08 counterexample check
        tf08 = next(fx for fx in fixtures if fx["fixture_id"] == "TF-08")
        check("2018-06-21" in tf08["inputs"]["CRS_DEP_TIME"] and "2018-06-21" in tf08["inputs"]["DEP_TIME"],
              "TF-08 date component preserved as counterexample without fabricating absolute recovery date")

    # -------------------------------------------------------------------------
    # 5. QA-04: Reproducible QA and Evidence Boundaries
    # -------------------------------------------------------------------------
    risk_path = ROOT / "docs/03-quality/RISK_REGISTER.md"
    if risk_path.exists():
        risk_text = risk_path.read_text(encoding="utf-8")
        check("R-01" in risk_text and "R-17" in risk_text,
              "Canonical R-01..R-17 present in RISK_REGISTER.md")

    rev_path = ROOT / "docs/05-evidence/T004_FINAL_REVIEW.md"
    if rev_path.exists():
        rev_text = rev_path.read_text(encoding="utf-8")
        check("OR-01" in rev_text and "OR-08" in rev_text,
              "Open risks OR-01..OR-08 present in T004_FINAL_REVIEW.md")
        check("OPEN_QUALITY_DEFECT" in rev_text, "OR-05 recorded as OPEN_QUALITY_DEFECT in T004_FINAL_REVIEW.md")
        check("IN_PROGRESS / NOT_PASSED" in rev_text, "Gate G2 is NOT passed in T004_FINAL_REVIEW.md")

    # Governance: Gate G2 Status Check (Guarded)
    state_path = ROOT / "docs/04-execution/PROJECT_STATE.md"
    if state_path.exists():
        st_text = state_path.read_text(encoding="utf-8")
        acc_rec = ROOT / "docs/05-evidence/G2_OFFICIAL_SIGNOFF_HUMAN_ACCEPTANCE_RECORD.md"
        if acc_rec.exists() and "APPROVED_BY_PROJECT_LEAD_EXPLICIT_INSTRUCTION" in acc_rec.read_text(encoding="utf-8"):
            check("G2 | PASS" in st_text, "Gate G2 is PASS in PROJECT_STATE.md (Official Signoff)")
        else:
            check("G2 | IN_PROGRESS / NOT_PASSED" in st_text, "Gate G2 is IN_PROGRESS / NOT_PASSED in PROJECT_STATE.md")

    cov_path = ROOT / "docs/05-evidence/T004_2024_DATE_COVERAGE_AUDIT.md"
    if cov_path.exists():
        cov_text = cov_path.read_text(encoding="utf-8")
        check("OPEN_QUALITY_DEFECT" in cov_text, "OR-05 explicitly retained as OPEN_QUALITY_DEFECT in date coverage audit")
        check("DATA_ABSENT_IN_CURRENT_CSV" in cov_text, "Status DATA_ABSENT_IN_CURRENT_CSV documented")
        check("UPSTREAM_ROOT_CAUSE_UNKNOWN" in cov_text, "Boundary UPSTREAM_ROOT_CAUSE_UNKNOWN documented")

    # -------------------------------------------------------------------------
    # Summary
    # -------------------------------------------------------------------------
    print("=" * 80)
    print(f"VERIFICATION SUMMARY: {len(passed_assertions)} PASS, {len(failed_assertions)} FAIL")
    print("=" * 80)

    if failed_assertions:
        print("\nFAILED ASSERTIONS:")
        for fa in failed_assertions:
            print(f"  - {fa}")
        return 1
    else:
        print(f"\nALL {len(passed_assertions)} T-004 FINAL QA CHECKS PASSED.")
        return 0


if __name__ == "__main__":
    sys.exit(run_checks())
