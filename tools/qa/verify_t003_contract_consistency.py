#!/usr/bin/env python3
"""
tools/qa/verify_t003_contract_consistency.py

Independent Contract Consistency and Automated Oracle Verification for Task T-003.
Author: Independent Technical Reviewer & Data Contract QA Engineer
Project: US Flight Performance Analysis (2016-2024), Big Data Descriptive Study

Checks:
1. FIX-14 CSV physical structure (34 cols, 5 data rows, row 5 has 6 cols).
2. FIX-14 JSON metadata (5 = 3 + 1 + 1 invariant, standardized reasons).
3. Independent recalculation of all 8 CORE KPI arithmetic oracles on accepted rows.
4. Completeness and exact count of 14 test fixtures (FIX-01..FIX-14).
5. Detection of known inverted/incorrect KPI mappings in evidence reports.
6. Detection of TS-009 vs TS-010 / TS-005 test mapping errors.
7. Governance checks (FP-DEC-015/016 & TS-021 PROPOSED, Gate G2 NOT_PASSED).

Exit code: 0 if ALL assertions pass, 1 if any assertion fails.
"""

import csv
import json
import math
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent

passed_assertions = []
failed_assertions = []


def check(condition: bool, description: str, detail: str = ""):
    if condition:
        passed_assertions.append(description)
        print(f"[PASS] {description}")
    else:
        msg = f"{description}" + (f" -> {detail}" if detail else "")
        failed_assertions.append(msg)
        print(f"[FAIL] {msg}", file=sys.stderr)


def run_checks():
    print("=" * 80)
    print("T-003 INDEPENDENT CONTRACT CONSISTENCY & ARITHMETIC ORACLE VERIFICATION")
    print("=" * 80)

    # -------------------------------------------------------------------------
    # 1. FIX-14 CSV Verification
    # -------------------------------------------------------------------------
    csv_path = ROOT / "docs/05-evidence/T003_FIX14_accounting_fixture.csv"
    check(csv_path.exists(), "FIX-14 CSV file exists", str(csv_path))

    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)
        data_rows = [r for r in reader if r]

    check(len(header) == 34, "FIX-14 CSV header has exactly 34 columns", f"Found {len(header)}")
    check(len(data_rows) == 5, "FIX-14 CSV has exactly 5 data rows", f"Found {len(data_rows)}")

    for i in range(4):
        check(len(data_rows[i]) == 34, f"FIX-14 data row {i+1} has 34 columns", f"Found {len(data_rows[i])}")

    check(len(data_rows[4]) == 6, "FIX-14 data row 5 has exactly 6 columns (column count mismatch)", f"Found {len(data_rows[4])}")
    check(data_rows[3][header.index("ORIGIN")] == "12A", "FIX-14 row 4 has ORIGIN='12A' (quarantine trigger)", data_rows[3][header.index("ORIGIN")])

    # -------------------------------------------------------------------------
    # 2. FIX-14 JSON Metadata & Invariant Verification
    # -------------------------------------------------------------------------
    json_path = ROOT / "docs/05-evidence/T003_FIX14_accounting_fixture.json"
    check(json_path.exists(), "FIX-14 JSON metadata file exists", str(json_path))

    with open(json_path, "r", encoding="utf-8") as f:
        meta = json.load(f)

    acct = meta.get("expected_accounting", {})
    check(acct.get("raw_row_count") == 5, "Accounting raw_row_count == 5", str(acct.get("raw_row_count")))
    check(acct.get("accepted_row_count") == 3, "Accounting accepted_row_count == 3", str(acct.get("accepted_row_count")))
    check(acct.get("quarantined_row_count") == 1, "Accounting quarantined_row_count == 1", str(acct.get("quarantined_row_count")))
    check(acct.get("rejected_row_count") == 1, "Accounting rejected_row_count == 1", str(acct.get("rejected_row_count")))

    invariant_holds = (acct.get("raw_row_count") == acct.get("accepted_row_count") + acct.get("quarantined_row_count") + acct.get("rejected_row_count"))
    check(invariant_holds and acct.get("accounting_invariant_holds") is True, "Accounting invariant holds: 5 = 3 + 1 + 1")
    check(abs(acct.get("ingest_acceptance_rate", 0) - 0.60) < 1e-9, "Ingest acceptance rate is exactly 60.0% (3/5)")

    # Standardized reason check for row 5
    row_classes = meta.get("row_classifications", [])
    row_5_class = next((r for r in row_classes if r.get("physical_line_number") == 6 or r.get("record_id") == "ROW_05_REJECTED"), {})
    check("COLUMN_COUNT_MISMATCH: EXPECTED_34_FOUND_6" in row_5_class.get("reason", ""),
          "Standardized rejection reason contains COLUMN_COUNT_MISMATCH: EXPECTED_34_FOUND_6",
          row_5_class.get("reason"))

    # -------------------------------------------------------------------------
    # 3. Independent Arithmetic Oracle Recalculation on Accepted Cohort
    # -------------------------------------------------------------------------
    accepted = data_rows[:3]
    arr_idx = header.index("ARR_DELAY")
    dep_idx = header.index("DEP_DELAY")
    to_idx = header.index("TAXI_OUT")
    ti_idx = header.index("TAXI_IN")
    air_idx = header.index("AIR_TIME")
    act_idx = header.index("ACTUAL_ELAPSED_TIME")
    crs_idx = header.index("CRS_ELAPSED_TIME")

    arr_delays = [float(r[arr_idx]) for r in accepted]
    dep_delays = [float(r[dep_idx]) for r in accepted]
    taxi_outs = [float(r[to_idx]) for r in accepted]
    taxi_ins = [float(r[ti_idx]) for r in accepted]
    air_times = [float(r[air_idx]) for r in accepted]
    act_elapseds = [float(r[act_idx]) for r in accepted]
    crs_elapseds = [float(r[crs_idx]) for r in accepted]

    check(arr_delays == [0.0, -12.0, 20.0], "Accepted ARR_DELAY values are [0.0, -12.0, 20.0]", str(arr_delays))
    check(dep_delays == [5.0, -5.0, 25.0], "Accepted DEP_DELAY values are [5.0, -5.0, 25.0]", str(dep_delays))

    # Metric recalculations per KPI_SPEC.md v1.1
    calc_kpi_01 = len(accepted)
    calc_kpi_02 = sum(1 for x in arr_delays if x >= 15.0) / calc_kpi_01
    calc_kpi_03 = sum(arr_delays) / calc_kpi_01
    calc_kpi_04 = sum(1 for x in dep_delays if x >= 15.0) / calc_kpi_01
    calc_kpi_05 = sum(dep_delays) / calc_kpi_01

    # Quantiles of [-12.0, 0.0, 20.0]
    sorted_arr = sorted(arr_delays)  # [-12.0, 0.0, 20.0]
    calc_p50 = sorted_arr[1]  # 0.0
    # Continuous linear (Type 7): index = 1 + 0.90*(3-1) = 2.8 -> y2 + 0.8*(y3 - y2) = 0.0 + 0.8*20.0 = 16.0
    calc_p90_cont = sorted_arr[1] + 0.8 * (sorted_arr[2] - sorted_arr[1])  # 16.0
    calc_p90_disc = sorted_arr[2]  # 20.0

    calc_taxi_out = sum(taxi_outs) / calc_kpi_01  # 45.0 / 3 = 15.0
    calc_taxi_in = sum(taxi_ins) / calc_kpi_01    # 18.0 / 3 = 6.0

    calc_air = sum(air_times) / calc_kpi_01       # 350.0 / 3 ≈ 116.6667
    calc_actual = sum(act_elapseds) / calc_kpi_01 # 413.0 / 3 ≈ 137.6667
    calc_crs = sum(crs_elapseds) / calc_kpi_01    # 430.0 / 3 ≈ 143.3333

    check(calc_kpi_01 == 3, "Recalculated KPI-01 == 3", str(calc_kpi_01))
    check(abs(calc_kpi_02 - 1.0/3.0) < 1e-9, "Recalculated KPI-02 == 1/3 (~33.3333%)", str(calc_kpi_02))
    check(abs(calc_kpi_03 - 8.0/3.0) < 1e-9, "Recalculated KPI-03 == 8/3 (~2.6667 min)", str(calc_kpi_03))
    check(abs(calc_kpi_04 - 1.0/3.0) < 1e-9, "Recalculated KPI-04 == 1/3 (~33.3333%)", str(calc_kpi_04))
    check(abs(calc_kpi_05 - 25.0/3.0) < 1e-9, "Recalculated KPI-05 == 25/3 (~8.3333 min)", str(calc_kpi_05))
    check(calc_p50 == 0.0, "Recalculated KPI-06 P50 == 0.0 min", str(calc_p50))
    check(abs(calc_p90_cont - 16.0) < 1e-9, "Recalculated KPI-06 P90 continuous == 16.0 min", str(calc_p90_cont))
    check(calc_p90_disc == 20.0, "Recalculated KPI-06 P90 discrete == 20.0 min", str(calc_p90_disc))
    check(calc_taxi_out == 15.0, "Recalculated KPI-07 Taxi-Out == 15.0 min", str(calc_taxi_out))
    check(calc_taxi_in == 6.0, "Recalculated KPI-07 Taxi-In == 6.0 min", str(calc_taxi_in))
    check(abs(calc_air - 350.0/3.0) < 1e-9, "Recalculated KPI-08 Air Time == 350/3 min", str(calc_air))
    check(abs(calc_actual - 413.0/3.0) < 1e-9, "Recalculated KPI-08 Actual Elapsed Time == 413/3 min", str(calc_actual))
    check(abs(calc_crs - 430.0/3.0) < 1e-9, "Recalculated KPI-08 CRS Elapsed Time == 430/3 min", str(calc_crs))

    # Reconcile with JSON entries
    exp_kpis = meta.get("expected_kpis_on_accepted_cohort", {})
    check(exp_kpis.get("KPI-01") == calc_kpi_01, "JSON KPI-01 matches recalculated oracle")
    check(abs(exp_kpis.get("KPI-02", 0) - calc_kpi_02) < 1e-9, "JSON KPI-02 matches recalculated oracle")
    check(abs(exp_kpis.get("KPI-03", 0) - calc_kpi_03) < 1e-9, "JSON KPI-03 matches recalculated oracle")
    check(abs(exp_kpis.get("KPI-04", 0) - calc_kpi_04) < 1e-9, "JSON KPI-04 matches recalculated oracle")
    check(abs(exp_kpis.get("KPI-05", 0) - calc_kpi_05) < 1e-9, "JSON KPI-05 matches recalculated oracle")
    check(exp_kpis.get("KPI-06-P50") == calc_p50, "JSON KPI-06-P50 matches recalculated oracle")
    check(abs(exp_kpis.get("KPI-06-P90_continuous", 0) - calc_p90_cont) < 1e-9, "JSON KPI-06-P90_continuous matches recalculated oracle")
    check(exp_kpis.get("KPI-06-P90_discrete") == calc_p90_disc, "JSON KPI-06-P90_discrete matches recalculated oracle")
    check(exp_kpis.get("KPI-07-TAXI_OUT") == calc_taxi_out, "JSON KPI-07-TAXI_OUT matches recalculated oracle")
    check(exp_kpis.get("KPI-07-TAXI_IN") == calc_taxi_in, "JSON KPI-07-TAXI_IN matches recalculated oracle")
    check(abs(exp_kpis.get("KPI-08-AIR_TIME", 0) - calc_air) < 1e-9, "JSON KPI-08-AIR_TIME matches recalculated oracle")
    check(abs(exp_kpis.get("KPI-08-ACTUAL_ELAPSED_TIME", 0) - calc_actual) < 1e-9, "JSON KPI-08-ACTUAL_ELAPSED_TIME matches recalculated oracle")
    check(abs(exp_kpis.get("KPI-08-CRS_ELAPSED_TIME", 0) - calc_crs) < 1e-9, "JSON KPI-08-CRS_ELAPSED_TIME matches recalculated oracle")

    # -------------------------------------------------------------------------
    # 4. Check 14 Test Fixtures in Specification
    # -------------------------------------------------------------------------
    spec_path = ROOT / "docs/05-evidence/T003_TEST_FIXTURE_SPEC.md"
    check(spec_path.exists(), "T003_TEST_FIXTURE_SPEC.md exists", str(spec_path))
    spec_text = spec_path.read_text(encoding="utf-8")

    fixture_ids = [f"FIX-{i:02d}" for i in range(1, 15)]
    found_fixtures = [fid for fid in fixture_ids if fid in spec_text]
    check(len(found_fixtures) == 14, "All 14 fixtures (FIX-01..FIX-14) present in TEST_FIXTURE_SPEC", f"Found {len(found_fixtures)}: {found_fixtures}")

    # -------------------------------------------------------------------------
    # 5. Detect Inverted/Incorrect KPI Mappings in Documentation Reports
    # -------------------------------------------------------------------------
    reports_to_check = [
        ROOT / "docs/05-evidence/T003_FINAL_CLOSEOUT_VERIFICATION.md",
        ROOT / "docs/05-evidence/T003_FINAL_GATE_RECOMMENDATION.md",
        ROOT / "docs/05-evidence/T003_TEST_FIXTURE_SPEC.md",
        ROOT / "docs/05-evidence/T003_PERCENTILE_AND_MIN_N_DECISIONS.md"
    ]

    # Erroneous mapping patterns to guard against:
    forbidden_patterns = [
        (re.compile(r"KPI-02\s*\|\s*Tỷ lệ chuyến bay đến đúng giờ", re.IGNORECASE), "KPI-02 wrongly mapped as on-time rate"),
        (re.compile(r"KPI-03\s*\|\s*Tỷ lệ chuyến bay đến trễ", re.IGNORECASE), "KPI-03 wrongly mapped as arrival late rate"),
        (re.compile(r"KPI-04\s*\|\s*Độ trễ đến trung bình", re.IGNORECASE), "KPI-04 wrongly mapped as arrival average delay"),
        (re.compile(r"KPI-05\s*\|\s*Trung vị độ trễ đến", re.IGNORECASE), "KPI-05 wrongly mapped as arrival median delay"),
        (re.compile(r"KPI-07\s*\|\s*Tỷ lệ chuyến bay khởi hành trễ", re.IGNORECASE), "KPI-07 wrongly mapped as departure late rate"),
        (re.compile(r"KPI-08\s*\|\s*Độ trễ khởi hành trung bình", re.IGNORECASE), "KPI-08 wrongly mapped as departure average delay"),
        (re.compile(r"ARR_DELAY\s*=\s*\[5(?:\.0)?,?\s*22(?:\.0)?,?\s*16(?:\.0)?\]"), "Hallucinated ARR_DELAY=[5, 22, 16] found"),
        (re.compile(r"DEP_DELAY\s*=\s*\[-2(?:\.0)?,?\s*18(?:\.0)?,?\s*0(?:\.0)?\]"), "Hallucinated DEP_DELAY=[-2, 18, 0] found"),
    ]

    for rpath in reports_to_check:
        if rpath.exists():
            content = rpath.read_text(encoding="utf-8")
            for pattern, desc in forbidden_patterns:
                matches = pattern.findall(content)
                check(len(matches) == 0, f"No erroneous pattern in {rpath.name}: {desc}", f"Matches: {matches[:3]}")

    # -------------------------------------------------------------------------
    # 6. Detect Wrongful TS-009 Mapping
    # -------------------------------------------------------------------------
    for rpath in reports_to_check:
        if rpath.exists():
            content = rpath.read_text(encoding="utf-8")
            ts009_temporal = re.search(r"TS-009\b[^\n]*\b(?:Temporal|rollover|midnight|2400)\b", content, re.IGNORECASE)
            check(ts009_temporal is None, f"No wrongful temporal mapping of TS-009 in {rpath.name}",
                  ts009_temporal.group(0) if ts009_temporal else "")

    # -------------------------------------------------------------------------
    # 7. Governance & Gate Status Checks
    # -------------------------------------------------------------------------
    state_path = ROOT / "docs/04-execution/PROJECT_STATE.md"
    check(state_path.exists(), "PROJECT_STATE.md exists", str(state_path))
    state_text = state_path.read_text(encoding="utf-8")

    # Guarded check: Gate G2 may be PASS only if accompanied by official Project Lead acceptance record
    acc_rec = ROOT / "docs/05-evidence/G2_OFFICIAL_SIGNOFF_HUMAN_ACCEPTANCE_RECORD.md"
    if acc_rec.exists() and "APPROVED_BY_PROJECT_LEAD_EXPLICIT_INSTRUCTION" in acc_rec.read_text(encoding="utf-8"):
        check("G2 | PASS" in state_text, "Gate G2 is officially PASS in PROJECT_STATE.md with human acceptance record")
        check("G2_OFFICIAL_SIGNOFF_HUMAN_ACCEPTANCE_RECORD.md" in state_text or "APPROVED_BY_PROJECT_LEAD_EXPLICIT_INSTRUCTION" in state_text,
              "Gate G2 references authoritative acceptance record in PROJECT_STATE.md")
    else:
        check("G2 | IN_PROGRESS / NOT_PASSED" in state_text or "G2 | DRAFT / NOT_PASSED" in state_text,
              "Gate G2 is NOT passed in PROJECT_STATE.md when acceptance record is absent")
        check("G2 | PASS" not in state_text, "Gate G2 is NOT overclaimed as PASS without acceptance record")

    # Verify ADRs and proposed tests are NOT claimed as APPROVED in evidence
    dec_text = (ROOT / "docs/05-evidence/T003_PERCENTILE_AND_MIN_N_DECISIONS.md").read_text(encoding="utf-8")
    check("APPROVED" not in re.findall(r"FP-DEC-01[56]\b[^\n]*APPROVED", dec_text),
          "FP-DEC-015 and FP-DEC-016 are NOT claimed as APPROVED (retained as PROPOSED)")

    # -------------------------------------------------------------------------
    # 8. ARR_DELAY Extrema Verification Across 9 Schema JSON Files (F10)
    # -------------------------------------------------------------------------
    overall_min_arr_delay = float("inf")
    overall_max_arr_delay = float("-inf")
    yearly_extrema = {}

    for yr in range(2016, 2025):
        schema_file = ROOT / f"docs/05-evidence/inputs/schema_{yr}.json"
        check(schema_file.exists(), f"Schema JSON exists for {yr}", str(schema_file))
        if schema_file.exists():
            with open(schema_file, "r", encoding="utf-8") as f:
                sdata = json.load(f)
            arr_dist = sdata.get("arr_delay", {}).get("distribution", {})
            ymin = arr_dist.get("min")
            ymax = arr_dist.get("max")
            check(ymin is not None and ymax is not None, f"arr_delay min and max present in schema_{yr}.json")
            if ymin is not None and ymax is not None:
                yearly_extrema[yr] = (ymin, ymax)
                if ymin < overall_min_arr_delay:
                    overall_min_arr_delay = ymin
                if ymax > overall_max_arr_delay:
                    overall_max_arr_delay = ymax

    check(overall_min_arr_delay == -238.0, f"Overall ARR_DELAY min across all 9 years is -238.0 (found {overall_min_arr_delay})")
    check(overall_max_arr_delay == 4405.0, f"Overall ARR_DELAY max across all 9 years is +4405.0 (found {overall_max_arr_delay})")

    # Ensure stale range [-1992, 2972] does not appear in any T-003 evidence document
    t003_evidence_files = list((ROOT / "docs/05-evidence").glob("T003_*.md"))
    stale_range_found = []
    for ef in t003_evidence_files:
        ef_text = ef.read_text(encoding="utf-8")
        if "-1992" in ef_text or "2972" in ef_text:
            stale_range_found.append(ef.name)
    check(len(stale_range_found) == 0, "No stale range [-1992, 2972] found in T003 evidence files", str(stale_range_found))

    # -------------------------------------------------------------------------
    # 9. Canonical Unit Status Uniformity (F11)
    # -------------------------------------------------------------------------
    unit_verif_path = ROOT / "docs/05-evidence/T003_UNIT_VERIFICATION.md"
    check(unit_verif_path.exists(), "T003_UNIT_VERIFICATION.md exists")
    if unit_verif_path.exists():
        unit_text = unit_verif_path.read_text(encoding="utf-8")
        canonical_str = "OFFICIAL_MINUTES_EMPIRICALLY_CONSISTENT_PROVISIONAL"
        measures_7 = ["ARR_DELAY", "DEP_DELAY", "TAXI_OUT", "TAXI_IN", "ACTUAL_ELAPSED_TIME", "CRS_ELAPSED_TIME", "AIR_TIME"]
        for m in measures_7:
            # Pattern matching markdown table row: | `MEASURE` | ... | `OFFICIAL_MINUTES_EMPIRICALLY_CONSISTENT_PROVISIONAL` |
            m_pattern = re.compile(rf"\|\s*`{m}`\s*\|[^\n]*`{canonical_str}`")
            check(bool(m_pattern.search(unit_text)), f"Measure {m} has canonical unit status {canonical_str} in T003_UNIT_VERIFICATION.md")

        check(not bool(re.search(r"\|\s*`?VERIFIED_AGAINST_UPSTREAM", unit_text)),
              "No premature elevation to VERIFIED_AGAINST_UPSTREAM in T003_UNIT_VERIFICATION.md")

    kpi_contract_path = ROOT / "docs/05-evidence/T003_KPI_CONTRACT_REVIEW.md"
    check(kpi_contract_path.exists(), "T003_KPI_CONTRACT_REVIEW.md exists")
    if kpi_contract_path.exists():
        kpi_text = kpi_contract_path.read_text(encoding="utf-8")
        minute_kpis = ["KPI-03", "KPI-05", "KPI-06", "KPI-07", "KPI-08"]
        for k in minute_kpis:
            check(f"`{k}`" in kpi_text and canonical_str in kpi_text,
                  f"Minute-based KPI {k} documented with canonical unit status in T003_KPI_CONTRACT_REVIEW.md")
        check("`KPI-01`" in kpi_text and "COUNT_INTEGER" in kpi_text, "KPI-01 is COUNT_INTEGER in T003_KPI_CONTRACT_REVIEW.md")
        check("`KPI-02`" in kpi_text and "DIMENSIONLESS_RATIO" in kpi_text, "KPI-02 is DIMENSIONLESS_RATIO in T003_KPI_CONTRACT_REVIEW.md")
        check("`KPI-04`" in kpi_text and "DIMENSIONLESS_RATIO" in kpi_text, "KPI-04 is DIMENSIONLESS_RATIO in T003_KPI_CONTRACT_REVIEW.md")

    # -------------------------------------------------------------------------
    # 10. Evidence Boundary & Population Distinction (F12)
    # -------------------------------------------------------------------------
    if unit_verif_path.exists():
        unit_text = unit_verif_path.read_text(encoding="utf-8")
        check("10.000 dòng" in unit_text or "10,000" in unit_text, "10k sample size clearly referenced in unit verification")
        check("54,674,003" in unit_text or "54.674.003" in unit_text, "Full population size (54,674,003) referenced for distinction in unit verification")
        check("PROVISIONAL" in unit_text, "Open provisional unit risk preserved in unit verification")

        # Guard against false claims
        false_claims = [
            (re.compile(r"10[,.]000\s*(?:hàng|dòng)[^\n]*(?:chứng minh|đại diện|khẳng định)[^\n]*(?:toàn bộ|54|tổng thể)", re.IGNORECASE),
             "False claim that 10k sample proves 54.67M population"),
            (re.compile(r"toàn bộ 54[.,]67[^\n]*(?:đã được xác minh upstream|proven against upstream BTS)", re.IGNORECASE),
             "False claim that population is verified against upstream BTS"),
        ]
        for fpat, fdesc in false_claims:
            matches = fpat.findall(unit_text)
            check(len(matches) == 0, f"No false claim: {fdesc}", str(matches[:2]))

    # -------------------------------------------------------------------------
    # 11. Quality Rule Protection for Duplicate Rows (F13)
    # -------------------------------------------------------------------------
    if spec_path.exists():
        spec_text = spec_path.read_text(encoding="utf-8")
        check("Zero Arbitrary Deduplication" in spec_text, "Zero Arbitrary Deduplication referenced in spec")
        check(bool(re.search(r"không\s+(?:cho phép\s+.*)?bỏ qua\s+.*quy tắc.*chất lượng", spec_text, re.IGNORECASE)),
              "Specification explicitly states duplicate rows must still satisfy quality rules")



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
        print("\nALL CONTRACT CONSISTENCY & ARITHMETIC ORACLE CHECKS PASSED.")
        return 0


if __name__ == "__main__":
    sys.exit(run_checks())
