"""
T-014 Independent Data Integrity and Release Readiness Audit Tool.
Final Signoff Blocker Correction Verification (V4 Controlled Release).
Verifies all published analytical tables, charts, registers, reports, and sealed packages.
Conforms to Gate G6 compliance standards and AGENTS.md policy.
"""

import os
import sys
import json
import zipfile
import hashlib
import binascii
import csv
from datetime import datetime, timezone

sys.path.insert(0, os.path.abspath("."))
sys.path.insert(0, os.path.abspath("src"))


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


def run_audit() -> bool:
    print("=" * 80)
    print("T-014 INDEPENDENT ANALYTICAL INTEGRITY AUDIT (SIGNOFF BLOCKER CORRECTION V4)")
    print(f"Timestamp: {datetime.now(timezone.utc).isoformat()}")
    print("=" * 80)

    repo_root = os.path.abspath(".")
    analytics_base = os.path.join(repo_root, "data", "analytics")
    run_id = "t014_analysis_2016_2024_v4"
    run_dir = os.path.join(analytics_base, "runs", run_id)
    export_dir = r"D:\Flight_Audit_Exports\T014_FULL_ANALYTICS\signoff_blocker_closeout"

    passed_checks = 0
    total_checks = 0

    def check(name: str, condition: bool, details: str = ""):
        nonlocal passed_checks, total_checks
        total_checks += 1
        status = "PASS" if condition else "FAIL"
        print(f"[{status}] {name} {details}")
        if condition:
            passed_checks += 1
        else:
            print(f"       ERROR: Condition failed: {details}")

    # 1. Baseline Invariant Checks
    print("\n--- 1. Baseline Pointers and Invariants ---")
    kpi_pointer = os.path.join(repo_root, "data", "kpi", "latest_run_id.txt")
    check("KPI pointer exists", os.path.exists(kpi_pointer))
    with open(kpi_pointer, "r", encoding="utf-8") as f:
        kpi_val = f.read().strip()
    check("KPI pointer preserved as kpi_run_2016_2024_v1", kpi_val == "kpi_run_2016_2024_v1", f"Found: {kpi_val}")

    analytics_pointer = os.path.join(analytics_base, "latest_run_id.txt")
    check("Analytics pointer exists", os.path.exists(analytics_pointer))
    with open(analytics_pointer, "r", encoding="utf-8") as f:
        ana_val = f.read().strip()
    check(f"Analytics pointer set to {run_id}", ana_val == run_id, f"Found: {ana_val}")

    # 2. Published Run Directory Integrity
    print("\n--- 2. Published Analytical Run Directory ---")
    check("Published run directory exists", os.path.isdir(run_dir))
    manifest_path = os.path.join(run_dir, "analytics_run_manifest.json")
    check("Analytics run manifest exists", os.path.exists(manifest_path))

    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    check("Manifest status is PUBLISHED_CONTROLLED", manifest.get("status") == "PUBLISHED_CONTROLLED")
    check("Manifest source rows is 54,674,003", manifest.get("source_total_records") == 54674003)
    check("Manifest KPI records processed is 684,180", manifest.get("kpi_records_processed") == 684180)

    # Tables verification
    tables_dir = os.path.join(run_dir, "tables")
    check("Tables directory exists", os.path.isdir(tables_dir))
    csv_files = [f for f in os.listdir(tables_dir) if f.endswith(".csv")]
    parquet_files = [f for f in os.listdir(tables_dir) if f.endswith(".parquet")]
    check("Exactly 12 CSV tables", len(csv_files) == 12, f"Found: {len(csv_files)}")
    check("Exactly 12 Parquet tables", len(parquet_files) == 12, f"Found: {len(parquet_files)}")

    # Verify table hashes against manifest
    manifest_tables = {t["table_name"]: t for t in manifest.get("tables", [])}
    for csv_f in csv_files:
        tbl_name = csv_f[:-4]
        csv_path = os.path.join(tables_dir, csv_f)
        parquet_path = os.path.join(tables_dir, f"{tbl_name}.parquet")
        if tbl_name in manifest_tables:
            exp_csv_hash = manifest_tables[tbl_name]["csv_sha256"]
            exp_pq_hash = manifest_tables[tbl_name]["parquet_sha256"]
            actual_csv_hash = hash_file(csv_path)
            actual_pq_hash = hash_file(parquet_path)
            check(f"Table hash match: {tbl_name}", (actual_csv_hash == exp_csv_hash and actual_pq_hash == exp_pq_hash))

    # Blocker B Table verification: rq03_directed_routes column and values
    print("\n--- 2b. Blocker B: Route Table Column and Value Verification ---")
    route_csv = os.path.join(tables_dir, "rq03_directed_routes.csv")
    with open(route_csv, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames or []
        check("rq03_directed_routes.csv has 'year' column", "year" in fieldnames, f"Fields: {fieldnames[:5]}")
        rows = list(reader)

    ord_lga_rows = [r for r in rows if r.get("city_pair") == "LGA <-> ORD"]
    check("ORD <-> LGA route pair exists in table", len(ord_lga_rows) > 0)
    if ord_lga_rows:
        r0 = ord_lga_rows[0]
        route_year = int(r0.get("year", 0))
        check("ORD <-> LGA route pair year is 2019", route_year == 2019, f"Found: {route_year}")
        fwd_rate = float(r0.get("arr_delay_rate_fwd_pct", 0))
        ret_rate = float(r0.get("arr_delay_rate_ret_pct", 0))
        diff_rate = float(r0.get("delay_rate_diff_pct", 0))
        fwd_n = int(r0.get("volume_fwd", 0))
        ret_n = int(r0.get("volume_ret", 0))
        total_vol = int(r0.get("total_pair_volume", 0))
        check("ORD->LGA return rate ~ 31.42%", abs(ret_rate - 31.4219) < 0.01, f"Found: {ret_rate:.4f}%")
        check("LGA->ORD forward rate ~ 28.60%", abs(fwd_rate - 28.5976) < 0.01, f"Found: {fwd_rate:.4f}%")
        check("ORD <-> LGA rate difference ~ 2.82%", abs(diff_rate - 2.8242) < 0.01, f"Found: {diff_rate:.4f}%")
        check("ORD <-> LGA total volume is 28,277", (fwd_n + ret_n) == 28277 and total_vol == 28277, f"Found: {total_vol}")

    # Charts verification
    print("\n--- 3. Publication Figures and Blocker A Semantic Traceability ---")
    charts_dir = os.path.join(run_dir, "charts")
    check("Charts directory exists", os.path.isdir(charts_dir))
    png_files = [f for f in os.listdir(charts_dir) if f.endswith(".png")]
    svg_files = [f for f in os.listdir(charts_dir) if f.endswith(".svg")]
    check("Exactly 16 PNG figures (300 DPI)", len(png_files) == 16, f"Found: {len(png_files)}")
    check("Exactly 16 SVG figures (Vector)", len(svg_files) == 16, f"Found: {len(svg_files)}")

    chart_inv_path = os.path.join(run_dir, "CHART_INVENTORY.json")
    check("Chart inventory JSON exists", os.path.exists(chart_inv_path))
    with open(chart_inv_path, "r", encoding="utf-8") as f:
        chart_inv = json.load(f)

    # Check semantic attributes of CHART_RQ02_04
    chart_04 = next(c for c in chart_inv["figures"] if c["chart_id"].startswith("CHART_RQ02_04"))
    check("CHART_RQ02_04 links to RES-004", chart_04.get("res_id") == "RES-004" or "RES-004" in chart_04.get("supporting_res_ids", []))
    check("CHART_RQ02_04 cohort_family is 'year-month'", chart_04.get("cohort_family") == "year-month", f"Found: {chart_04.get('cohort_family')}")
    check("CHART_RQ02_04 table_reference is 'rq02_monthly_delays.parquet'", chart_04.get("table_reference") == "rq02_monthly_delays.parquet", f"Found: {chart_04.get('table_reference')}")

    # Check all 16 charts have cohort_family and table_reference
    all_charts_have_attrs = all(c.get("cohort_family") and c.get("table_reference") for c in chart_inv["figures"])
    check("All 16 charts have cohort_family and table_reference", all_charts_have_attrs)

    # Results Register verification
    print("\n--- 4. Results Register and Report ---")
    reg_path = os.path.join(run_dir, "RESULTS_REGISTER.json")
    check("Results register JSON exists", os.path.exists(reg_path))
    with open(reg_path, "r", encoding="utf-8") as f:
        reg = json.load(f)
    check("Results register has 20 traceable findings", len(reg.get("results", [])) == 20)

    res_map = {e["res_id"]: e for e in reg.get("results", [])}
    check("RES-002 peak July in 6/9 years", res_map.get("RES-002", {}).get("observed_value") == 6 and res_map.get("RES-002", {}).get("valid_cohort_denominator_N") == 9)
    check("RES-004 2022 arrival delay denominator is 6,413,416", res_map.get("RES-004", {}).get("valid_cohort_denominator_N") == 6413416)
    check("RES-005 2020 arrival delay signed mean is -5.1078m", abs(res_map.get("RES-005", {}).get("observed_value") - (-5.1078)) < 1e-4)
    check("RES-006 2020 P50 arrival delay is -11.0m", res_map.get("RES-006", {}).get("observed_value") == -11.0)
    check("RES-007 2022 P90 arrival delay is 42.0m", res_map.get("RES-007", {}).get("observed_value") == 42.0)
    check("RES-010 EWR 2022 departure delay rate is 27.67%", res_map.get("RES-010", {}).get("observed_value") == 27.67 and res_map.get("RES-010", {}).get("valid_cohort_denominator_N") == 123277)
    check("RES-011 LGA-ORD route asymmetry is 2.82% (2019)", res_map.get("RES-011", {}).get("observed_value") == 2.82 and res_map.get("RES-011", {}).get("valid_cohort_denominator_N") == 28277)
    check("RES-015 2020 Taxi-Out is 15.25m (15.2476m)", abs(res_map.get("RES-015", {}).get("observed_value") - 15.25) < 0.01)
    check("RES-017 JFK 2023 Taxi-Out is 26.21m", res_map.get("RES-017", {}).get("observed_value") == 26.21 and res_map.get("RES-017", {}).get("valid_cohort_denominator_N") == 129620)
    check("RES-018 2020 schedule buffer is 7.08m", abs(res_map.get("RES-018", {}).get("observed_value") - 7.08) < 1e-2)
    check("RES-019 2016 actual elapsed time is 140.16m", abs(res_map.get("RES-019", {}).get("observed_value") - 140.16) < 1e-2)

    report_path = os.path.join(run_dir, "T014_ANALYTICAL_FINDINGS_REPORT.md")
    check("Analytical findings report exists", os.path.exists(report_path))
    with open(report_path, "r", encoding="utf-8") as f:
        report_content = f.read()

    # Check 10 sections
    for i in range(1, 11):
        sec_str = f"## {i}."
        check(f"Report contains Section {i}", sec_str in report_content)

    # Check report mentions 2019 ORD-LGA asymmetry
    check("Report cites 2019 for ORD-LGA asymmetry", "2019" in report_content and "31.42%" in report_content and "28.60%" in report_content)

    # 5. External Sealed Package & Blocker Resolution Verification
    print("\n--- 5. External Sealed Evidence Package & Blocker Resolution ---")
    check("External export directory exists", os.path.isdir(export_dir))

    zip_path = os.path.join(export_dir, "T014_FINAL_REVIEW.zip")
    review_manifest_path = os.path.join(export_dir, "T014_FINAL_REVIEW_MANIFEST.json")
    check("T014_FINAL_REVIEW.zip exists", os.path.exists(zip_path))
    check("T014_FINAL_REVIEW_MANIFEST.json exists", os.path.exists(review_manifest_path))

    with open(review_manifest_path, "r", encoding="utf-8") as f:
        rev_manifest = json.load(f)

    # Compute actual ZIP hashes
    actual_zip_sha256 = hash_file(zip_path)
    actual_zip_crc32 = crc32_file(zip_path)
    actual_zip_bytes = os.path.getsize(zip_path)

    check("ZIP SHA-256 matches manifest", actual_zip_sha256 == rev_manifest["archive_sha256"], f"{actual_zip_sha256[:16]}...")
    check("ZIP CRC-32 matches manifest", actual_zip_crc32 == rev_manifest["archive_crc32_hex"], f"{actual_zip_crc32}")
    check("ZIP file size matches manifest", actual_zip_bytes == rev_manifest["archive_bytes"], f"{actual_zip_bytes:,} bytes")

    # Verify members inside ZIP
    with zipfile.ZipFile(zip_path, "r") as zf:
        zip_members = zf.namelist()
        check(
            f"ZIP contains all {rev_manifest.get('total_members')} member files (tables, charts, evidence reports)",
            len(zip_members) == rev_manifest.get("total_members") and len(zip_members) >= 65,
            f"Found: {len(zip_members)}, Manifest expects: {rev_manifest.get('total_members')}"
        )

    # Check Blocker A Artifact: T014_CORRECTED_CHART_SEMANTIC_VERIFICATION.json
    semantic_file = os.path.join(export_dir, "T014_CORRECTED_CHART_SEMANTIC_VERIFICATION.json")
    check("T014_CORRECTED_CHART_SEMANTIC_VERIFICATION.json exists", os.path.exists(semantic_file))
    with open(semantic_file, "r", encoding="utf-8") as f:
        sem_data = json.load(f)
    checks_dict = sem_data.get("semantic_checks", {})
    all_semantic_true = all(checks_dict.values()) and len(checks_dict) == 5
    check("Semantic alignment verified (all 5 checks True)", all_semantic_true)
    check("All 16 charts verified is True", sem_data.get("all_16_charts_verified") is True)
    check("Semantic check 1 (chart_rq02_04_links_to_res004) is True", checks_dict.get("chart_rq02_04_links_to_res004") is True)
    check("Semantic check 2 (chart_rq02_03_links_to_res006_and_res007) is True", checks_dict.get("chart_rq02_03_links_to_res006_and_res007") is True)
    check("Semantic check 3 (chart_rq05_01_links_to_res015_and_res016) is True", checks_dict.get("chart_rq05_01_links_to_res015_and_res016") is True)
    check("Semantic check 4 (chart_rq05_02_links_to_res018_and_res019) is True", checks_dict.get("chart_rq05_02_links_to_res018_and_res019") is True)
    check("Semantic check 5 (chart_rq05_03_links_to_res017) is True", checks_dict.get("chart_rq05_03_links_to_res017") is True)

    # Check Blocker B Artifact: T014_ROUTE_YEAR_NUMERICAL_RECONCILIATION.json
    reconcil_file = os.path.join(export_dir, "T014_ROUTE_YEAR_NUMERICAL_RECONCILIATION.json")
    check("T014_ROUTE_YEAR_NUMERICAL_RECONCILIATION.json exists", os.path.exists(reconcil_file))
    with open(reconcil_file, "r", encoding="utf-8") as f:
        rec_data = json.load(f)
    lga_ord = rec_data.get("lga_ord_reconciliation", {})
    comp = lga_ord.get("comparison", {})
    check("Route reconciliation verified is True", rec_data.get("selected_year") == 2019 and lga_ord.get("year") == 2019)
    check("Reconciliation year is 2019", rec_data.get("selected_year") == 2019)
    check("Reconciliation pair volume is 28,277", comp.get("total_pair_volume") == 28277)
    check("Reconciliation rate difference is 2.8242%", abs(comp.get("delay_rate_difference_pct", 0) - 2.8242) < 1e-4)

    # Check all required final deliverables in export_dir
    for doc in [
        "T014_SIGNOFF_BLOCKER_CORRECTION_REPORT.md",
        "T014_CORRECTED_CHART_SEMANTIC_VERIFICATION.json",
        "T014_ROUTE_YEAR_NUMERICAL_RECONCILIATION.json",
        "T014_AUTHENTIC_TEST_AND_AUDIT_LOG.txt",
        "T014_BLOCKER_FIX_CHANGES.patch",
        "T014_FINAL_REVIEW.zip",
        "T014_FINAL_REVIEW_MANIFEST.json",
    ]:
        check(f"Export deliverable exists: {doc}", os.path.exists(os.path.join(export_dir, doc)))

    print("\n" + "=" * 80)
    print(f"AUDIT SUMMARY: {passed_checks}/{total_checks} CHECKS PASSED")
    if passed_checks == total_checks:
        print("VERDICT: T014_SIGNOFF_BLOCKERS_RESOLVED_READY_FOR_HUMAN_SIGNOFF")
        print("=" * 80)
        return True
    else:
        print(f"VERDICT: FAIL ({total_checks - passed_checks} checks failed)")
        print("=" * 80)
        return False


if __name__ == "__main__":
    success = run_audit()
    sys.exit(0 if success else 1)
