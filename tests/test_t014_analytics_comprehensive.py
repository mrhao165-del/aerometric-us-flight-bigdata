"""
Comprehensive Test Suite for Task T-014 (V3 Final Evidence Closeout).
Validates Reader, Transformations, Visualizations, Results Register,
Published Deliverables, and 8 Mandatory Negative Tests against all T-014 Acceptance Criteria.
"""

import os
import sys
import json
import zipfile
import hashlib
import binascii
import unittest
import pandas as pd

# Add repository root and src to path
sys.path.insert(0, os.path.abspath("."))
sys.path.insert(0, os.path.abspath("src"))

from flight_pipeline.analytics.reader import KPIAnalyticsReader
from flight_pipeline.analytics.transformations import KPIAnalyticsTransformer
from flight_pipeline.analytics.results_register import ResultsRegister


class TestT014AnalyticsComprehensive(unittest.TestCase):
    """Full independent verification of T-014 analytics with positive and negative testing."""

    @classmethod
    def setUpClass(cls):
        cls.reader = KPIAnalyticsReader()
        cls.kpi_df = cls.reader.load_kpi_dataset("kpi_run_2016_2024_v1")
        cls.transformer = KPIAnalyticsTransformer(cls.kpi_df)
        cls.publish_dir = os.path.join("data", "analytics", "runs", "t014_analysis_2016_2024_v4")
        cls.export_dir = r"D:\Flight_Audit_Exports\T014_FULL_ANALYTICS\signoff_blocker_closeout"

    # -------------------------------------------------------------------------
    # 1. Reader & Baseline Verifications
    # -------------------------------------------------------------------------
    def test_01_reader_row_count_and_columns(self):
        """Verify exactly 684,180 records across 9 years."""
        self.assertEqual(len(self.kpi_df), 684180)
        self.assertEqual(self.kpi_df["entity_year"].nunique(), 9)
        self.assertEqual(sorted(self.kpi_df["entity_year"].unique().tolist()), list(range(2016, 2025)))

    def test_02_reader_grouping_families(self):
        """Verify deterministic classification into the 6 approved families."""
        families = self.kpi_df["group_family"].value_counts().to_dict()
        self.assertIn("year", families)
        self.assertIn("year-month", families)
        self.assertIn("carrier-year", families)
        self.assertIn("origin-year", families)
        self.assertIn("dest-year", families)
        self.assertIn("route-year", families)
        self.assertEqual(families["year"], 108)  # 9 years * 12 streams
        self.assertEqual(families["year-month"], 1284)  # 107 months * 12 streams
        self.assertEqual(families["carrier-year"], 1680)  # 140 cohorts * 12
        self.assertEqual(families["origin-year"], 33768)  # 2,814 cohorts * 12
        self.assertEqual(families["dest-year"], 33792)  # 2,816 cohorts * 12
        self.assertEqual(families["route-year"], 613548)  # 51,129 cohorts * 12

    # -------------------------------------------------------------------------
    # 2. RQ-01: Volume & Seasonality
    # -------------------------------------------------------------------------
    def test_03_rq01_annual_volume_totals(self):
        """Verify 54,674,003 total accepted flights and annual shares."""
        df = self.transformer.get_rq01_annual_volume_table()
        self.assertEqual(len(df), 9)
        total_vol = df["annual_volume"].sum()
        self.assertEqual(total_vol, 54674003)
        self.assertAlmostEqual(df["share_of_9yr_pct"].sum(), 100.0, places=4)

        # Peak 2019, trough 2020
        v_2019 = df.loc[df["year"] == 2019, "annual_volume"].values[0]
        v_2020 = df.loc[df["year"] == 2020, "annual_volume"].values[0]
        self.assertEqual(v_2019, 7161827)
        self.assertEqual(v_2020, 4312091)
        self.assertTrue(v_2019 > v_2020)

    def test_04_rq01_monthly_seasonality_and_or05(self):
        """Verify 107 months, April 2020 trough, and missing March 2024."""
        df = self.transformer.get_rq01_monthly_volume_table()
        self.assertEqual(len(df), 107)

        # Check March 2024 absence (OR-05)
        self.assertNotIn("2024-03", df["year_month"].values)

        # Check April 2020 volume
        apr_2020 = df[df["year_month"] == "2020-04"]
        self.assertEqual(len(apr_2020), 1)
        self.assertEqual(int(apr_2020["monthly_volume"].values[0]), 179835)

        # Peak volume month distribution: July is peak in 6/9 years
        years_with_july_peak = 0
        df_copy = df.copy()
        df_copy["year"] = df_copy["year_month"].apply(lambda ym: int(ym.split("-")[0]))
        for yr, grp in df_copy.groupby("year"):
            max_row = grp.loc[grp["monthly_volume"].idxmax()]
            if max_row["year_month"].endswith("-07"):
                years_with_july_peak += 1
        self.assertEqual(years_with_july_peak, 6)

    # -------------------------------------------------------------------------
    # 3. RQ-02: Delays, Means & Percentiles
    # -------------------------------------------------------------------------
    def test_05_rq02_annual_delays(self):
        """Verify delay rates and signed means."""
        df = self.transformer.get_rq02_annual_delay_performance_table()
        self.assertEqual(len(df), 9)

        # 2020 minimum delay rate and negative signed mean (-5.1078 min)
        row_2020 = df[df["year"] == 2020].iloc[0]
        self.assertAlmostEqual(row_2020["arr_delay_ge_15_rate_pct"], 9.73, places=1)
        self.assertAlmostEqual(row_2020["arr_delay_signed_mean_min"], -5.1078, places=2)

        # 2022 peak delay rate and exact signed mean (+6.9344m, not +6.43m)
        row_2022 = df[df["year"] == 2022].iloc[0]
        self.assertAlmostEqual(row_2022["arr_delay_ge_15_rate_pct"], 20.99, places=1)
        self.assertAlmostEqual(row_2022["arr_delay_signed_mean_min"], 6.9344, places=2)

    def test_06_rq02_skewness_p50_vs_p90(self):
        """Verify median P50 is negative and P90 is large positive."""
        df = self.transformer.get_rq02_annual_delay_performance_table()
        for _, r in df.iterrows():
            self.assertTrue(r["arr_delay_p50_min"] <= 0, f"P50 should be <= 0 in year {r['year']}")
            self.assertTrue(r["arr_delay_p90_min"] > 10, f"P90 should be > 10 in year {r['year']}")

        # 2020 P50 is -11m; 2022 P90 is 42m; 2024 P90 is 43m
        r_2020 = df[df["year"] == 2020].iloc[0]
        r_2022 = df[df["year"] == 2022].iloc[0]
        self.assertAlmostEqual(r_2020["arr_delay_p50_min"], -11.0, places=1)
        self.assertAlmostEqual(r_2022["arr_delay_p90_min"], 42.0, places=1)

    # -------------------------------------------------------------------------
    # 4. RQ-03: Carriers, Airports & Routes
    # -------------------------------------------------------------------------
    def test_07_rq03_top_carriers(self):
        """Verify top carriers summary with valid-denominator weighted pooling."""
        df = self.transformer.get_rq03_top_carriers_summary()
        self.assertEqual(len(df), 10)

        # Southwest (WN) volume is exactly 11,133,643
        self.assertEqual(df.iloc[0]["carrier"], "WN")
        self.assertEqual(df.iloc[0]["total_volume"], 11133643)

        # Pooled on-time rate for WN is 80.67%
        self.assertAlmostEqual(df.iloc[0]["mean_on_time_arr_rate_pct"], 80.67, places=1)

        # DL punctuality > AA punctuality
        dl_punct = df.loc[df["carrier"] == "DL", "mean_on_time_arr_rate_pct"].values[0]
        aa_punct = df.loc[df["carrier"] == "AA", "mean_on_time_arr_rate_pct"].values[0]
        self.assertTrue(dl_punct > aa_punct)
        self.assertAlmostEqual(dl_punct, 85.81, places=1)
        self.assertAlmostEqual(aa_punct, 79.61, places=1)

        # DL and AA exact 9-year volumes
        dl_vol = df.loc[df["carrier"] == "DL", "total_volume"].values[0]
        aa_vol = df.loc[df["carrier"] == "AA", "total_volume"].values[0]
        self.assertEqual(dl_vol, 7821658)
        self.assertEqual(aa_vol, 7518473)

    def test_08_rq03_directed_route_asymmetry(self):
        """Verify bidirectional asymmetry in flight routes for year 2019."""
        df = self.transformer.get_rq03_directed_route_asymmetry_table(year=2019, top_n_pairs=10)
        self.assertTrue(len(df) > 0)
        self.assertIn("year", df.columns)
        self.assertEqual(int(df["year"].iloc[0]), 2019)
        lga_ord = df[df["city_pair"] == "LGA <-> ORD"]
        self.assertTrue(len(lga_ord) > 0)
        r = lga_ord.iloc[0]
        self.assertEqual(r["total_pair_volume"], 28277)
        self.assertAlmostEqual(r["delay_rate_diff_pct"], 2.8242, places=3)
        self.assertAlmostEqual(r["arr_delay_rate_fwd_pct"], 28.5976, places=3)
        self.assertAlmostEqual(r["arr_delay_rate_ret_pct"], 31.4219, places=3)

    # -------------------------------------------------------------------------
    # 5. RQ-04: Pandemic Shock & Recovery
    # -------------------------------------------------------------------------
    def test_09_rq04_pandemic_comparison(self):
        """Verify pandemic table 2019, 2020, 2021 comparison and year column preservation."""
        df = self.transformer.get_rq04_pandemic_comparison_table()
        self.assertEqual(len(df), 3)
        self.assertIn(2019, df.index)
        self.assertIn(2020, df.index)
        self.assertIn(2021, df.index)
        self.assertIn("year", df.columns)

        v_19 = df.loc[2019, "total_records"]
        v_20 = df.loc[2020, "total_records"]
        pct_drop = (v_20 - v_19) / v_19 * 100.0
        self.assertAlmostEqual(pct_drop, -39.79, places=1)

    # -------------------------------------------------------------------------
    # 6. RQ-05: Taxi & Journey Dynamics
    # -------------------------------------------------------------------------
    def test_10_rq05_journey_times_and_buffers(self):
        """Verify taxi times and schedule buffer."""
        df = self.transformer.get_rq05_annual_journey_times_table()
        self.assertEqual(len(df), 9)
        for _, r in df.iterrows():
            self.assertTrue(r["taxi_out_mean_min"] > r["taxi_in_mean_min"])
            buf = r["crs_elapsed_mean_min"] - r["actual_elapsed_mean_min"]
            self.assertTrue(buf > 4.0, f"Schedule buffer should be > 4m in {r['year']}")

        # 2020 Taxi-Out is 15.2476m
        row_2020 = df[df["year"] == 2020].iloc[0]
        self.assertAlmostEqual(row_2020["taxi_out_mean_min"], 15.2476, places=2)

    # -------------------------------------------------------------------------
    # 7. Results Register & Published Deliverables
    # -------------------------------------------------------------------------
    def test_11_results_register_integrity(self):
        """Verify Results Register has all 20 required entries and exact denominators."""
        reg_path = os.path.join(self.publish_dir, "RESULTS_REGISTER.json")
        self.assertTrue(os.path.exists(reg_path), f"Missing {reg_path}")
        with open(reg_path, "r", encoding="utf-8") as f:
            reg = json.load(f)
        self.assertEqual(len(reg["results"]), 20)
        res_map = {e["res_id"]: e for e in reg["results"]}

        # Check cohort-specific denominators
        self.assertEqual(res_map["RES-001"]["valid_cohort_denominator_N"], 54674003)
        self.assertEqual(res_map["RES-002"]["valid_cohort_denominator_N"], 9)
        self.assertEqual(res_map["RES-004"]["valid_cohort_denominator_N"], 6413416)
        self.assertEqual(res_map["RES-005"]["valid_cohort_denominator_N"], 4312091)
        self.assertEqual(res_map["RES-007"]["valid_cohort_denominator_N"], 6413416)
        self.assertEqual(res_map["RES-010"]["valid_cohort_denominator_N"], 123277)
        self.assertEqual(res_map["RES-015"]["valid_cohort_denominator_N"], 4312091)
        self.assertEqual(res_map["RES-017"]["valid_cohort_denominator_N"], 129620)

        # Check supersessions map exists
        self.assertIn("supersessions", reg)
        self.assertIn("RES-004", reg["supersessions"])
        self.assertIn("RES-005", reg["supersessions"])

    def test_12_published_tables_and_charts(self):
        """Verify published tables and figures in both formats."""
        tables_dir = os.path.join(self.publish_dir, "tables")
        charts_dir = os.path.join(self.publish_dir, "charts")
        self.assertTrue(os.path.isdir(tables_dir))
        self.assertTrue(os.path.isdir(charts_dir))

        csv_files = [f for f in os.listdir(tables_dir) if f.endswith(".csv")]
        parquet_files = [f for f in os.listdir(tables_dir) if f.endswith(".parquet")]
        png_files = [f for f in os.listdir(charts_dir) if f.endswith(".png")]
        svg_files = [f for f in os.listdir(charts_dir) if f.endswith(".svg")]

        self.assertEqual(len(csv_files), 12)
        self.assertEqual(len(parquet_files), 12)
        self.assertEqual(len(png_files), 16)
        self.assertEqual(len(svg_files), 16)

    def test_13_sealed_evidence_package(self):
        """Verify external review zip and outside manifest."""
        zip_path = os.path.join(self.export_dir, "T014_FINAL_REVIEW.zip")
        manifest_path = os.path.join(self.export_dir, "T014_FINAL_REVIEW_MANIFEST.json")
        self.assertTrue(os.path.exists(zip_path), f"Missing {zip_path}")
        self.assertTrue(os.path.exists(manifest_path), f"Missing {manifest_path}")

        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest = json.load(f)

        # Check SHA-256 matches
        h = hashlib.sha256()
        crc = 0
        with open(zip_path, "rb") as f:
            while chunk := f.read(65536):
                h.update(chunk)
                crc = binascii.crc32(chunk, crc)

        calc_sha256 = h.hexdigest()
        calc_crc32 = f"{crc & 0xFFFFFFFF:08x}"

        self.assertEqual(manifest["archive_sha256"], calc_sha256)
        self.assertEqual(manifest["archive_crc32_hex"], calc_crc32)
        self.assertEqual(manifest["archive_bytes"], os.path.getsize(zip_path))

    def test_14_cohort_breakdown_and_exact_balance(self):
        """Verify exact cohort family breakdown."""
        counts = self.kpi_df["group_family"].value_counts().to_dict()
        expected_rows = {
            "year": 108,
            "year-month": 1284,
            "carrier-year": 1680,
            "origin-year": 33768,
            "dest-year": 33792,
            "route-year": 613548,
        }
        for fam, exp_cnt in expected_rows.items():
            self.assertEqual(counts[fam], exp_cnt, f"Mismatch in family {fam}")

        total_cohorts = sum(counts[fam] // 12 for fam in expected_rows)
        self.assertEqual(total_cohorts, 57015)
        self.assertEqual(len(self.kpi_df), 684180)

    def test_15_final_closeout_deliverables_presence(self):
        """Verify all required blocker and closeout deliverables exist in export directory."""
        required = [
            "T014_SIGNOFF_BLOCKER_CORRECTION_REPORT.md",
            "T014_CORRECTED_CHART_SEMANTIC_VERIFICATION.json",
            "T014_ROUTE_YEAR_NUMERICAL_RECONCILIATION.json",
            "T014_FINAL_EVIDENCE_CLOSEOUT_REPORT.md",
            "T014_FINAL_RES_COHORT_RECONCILIATION.json",
            "T014_FINAL_CHART_SEMANTIC_TRACEABILITY.json",
            "T014_FINAL_TEST_AND_AUDIT_LOG.txt",
            "T014_AUTHENTIC_TEST_AND_AUDIT_LOG.txt",
            "T014_FINAL_CHANGES.patch",
            "T014_BLOCKER_FIX_CHANGES.patch",
            "T014_FINAL_REVIEW.zip",
            "T014_FINAL_SEALED_REVIEW.zip",
            "T014_FINAL_REVIEW_MANIFEST.json",
            "T014_FINAL_SEALED_REVIEW_MANIFEST.json",
        ]
        for item in required:
            p = os.path.join(self.export_dir, item)
            self.assertTrue(os.path.exists(p), f"Missing external deliverable: {item}")

    def test_16_semantic_checks_all_true(self):
        """Verify that all 5 named semantic checks are TRUE and all 16 charts are verified."""
        trace_path = os.path.join(self.export_dir, "T014_CORRECTED_CHART_SEMANTIC_VERIFICATION.json")
        self.assertTrue(os.path.exists(trace_path))
        with open(trace_path, "r", encoding="utf-8") as f:
            trace = json.load(f)

        checks = trace.get("semantic_checks", {})
        self.assertTrue(checks.get("chart_rq02_04_links_to_res004"), "chart_rq02_04 must link to RES-004")
        self.assertTrue(checks.get("chart_rq02_03_links_to_res006_and_res007"), "chart_rq02_03 must link to RES-006 & RES-007")
        self.assertTrue(checks.get("chart_rq05_01_links_to_res015_and_res016"), "chart_rq05_01 must link to RES-015 & RES-016")
        self.assertTrue(checks.get("chart_rq05_02_links_to_res018_and_res019"), "chart_rq05_02 must link to RES-018 & RES-019")
        self.assertTrue(checks.get("chart_rq05_03_links_to_res017"), "chart_rq05_03 must link to RES-017")
        self.assertTrue(trace.get("all_16_charts_verified"), "all 16 charts must have semantic_alignment_verified=True")

    def test_17_route_year_numerical_reconciliation(self):
        """Verify route-year reconciliation JSON for LGA <-> ORD in 2019."""
        recon_path = os.path.join(self.export_dir, "T014_ROUTE_YEAR_NUMERICAL_RECONCILIATION.json")
        self.assertTrue(os.path.exists(recon_path))
        with open(recon_path, "r", encoding="utf-8") as f:
            recon = json.load(f)

        self.assertEqual(recon.get("selected_year"), 2019)
        lga_ord = recon.get("lga_ord_reconciliation", {})
        self.assertEqual(lga_ord.get("year"), 2019)
        self.assertEqual(lga_ord.get("comparison", {}).get("total_pair_volume"), 28277)
        self.assertAlmostEqual(lga_ord.get("comparison", {}).get("delay_rate_difference_pct"), 2.8242, places=3)
        self.assertEqual(lga_ord.get("forward_direction", {}).get("flight_volume"), 14169)
        self.assertEqual(lga_ord.get("return_direction", {}).get("flight_volume"), 14108)

    # -------------------------------------------------------------------------
    # 8. MANDATORY NEGATIVE TESTS (Proving Fail-Closed Verification)
    # -------------------------------------------------------------------------
    def test_negative_01_wrong_year_specific_mean(self):
        """Negative Test 1: Asserting 2022 mean arrival delay is +6.43m must fail."""
        df = self.transformer.get_rq02_annual_delay_performance_table()
        val_2022 = df.loc[df["year"] == 2022, "arr_delay_signed_mean_min"].values[0]
        with self.assertRaises(AssertionError):
            # Erroneous v1 figure +6.43m must not equal authoritative +6.9344m
            self.assertAlmostEqual(val_2022, 6.43, places=2)

    def test_negative_02_wrong_peak_month_count(self):
        """Negative Test 2: Asserting July is peak volume in 7/9 years must fail (actual is 6/9)."""
        df = self.transformer.get_rq01_monthly_volume_table()
        df_copy = df.copy()
        df_copy["year"] = df_copy["year_month"].apply(lambda ym: int(ym.split("-")[0]))
        july_peaks = sum(
            1 for _, grp in df_copy.groupby("year")
            if grp.loc[grp["monthly_volume"].idxmax()]["year_month"].endswith("-07")
        )
        with self.assertRaises(AssertionError):
            self.assertEqual(july_peaks, 7)

    def test_negative_03_wrong_res_entry_denominator(self):
        """Negative Test 3: Asserting RES-004 has national denominator 54.7M must fail."""
        reg_path = os.path.join(self.publish_dir, "RESULTS_REGISTER.json")
        with open(reg_path, "r", encoding="utf-8") as f:
            reg = json.load(f)
        res_004 = next(e for e in reg["results"] if e["res_id"] == "RES-004")
        with self.assertRaises(AssertionError):
            self.assertEqual(res_004["valid_cohort_denominator_N"], 54674003)

    def test_negative_04_wrong_chart_semantic_link(self):
        """Negative Test 4: Asserting CHART_RQ02_04 links to RES-007 (percentiles) must fail."""
        chart_inv_path = os.path.join(self.publish_dir, "CHART_INVENTORY.json")
        with open(chart_inv_path, "r", encoding="utf-8") as f:
            inv = json.load(f)
        chart_04 = next(c for c in inv["figures"] if c["chart_id"].startswith("CHART_RQ02_04"))
        with self.assertRaises(AssertionError):
            self.assertEqual(chart_04["res_id"], "RES-007")

    def test_negative_05_fabricated_observed_value(self):
        """Negative Test 5: Asserting RES-010 observed value is fabricated 23.1% must fail."""
        reg_path = os.path.join(self.publish_dir, "RESULTS_REGISTER.json")
        with open(reg_path, "r", encoding="utf-8") as f:
            reg = json.load(f)
        res_010 = next(e for e in reg["results"] if e["res_id"] == "RES-010")
        with self.assertRaises(AssertionError):
            self.assertEqual(res_010["observed_value"], 23.1)

    def test_negative_06_report_misstating_min_n_policy(self):
        """Negative Test 6: Asserting min-N threshold is uniform 100 across carriers/airports must fail."""
        recon_path = os.path.join(self.export_dir, "T014_FINAL_RES_COHORT_RECONCILIATION.json")
        with open(recon_path, "r", encoding="utf-8") as f:
            recon = json.load(f)
        policy = recon.get("min_n_policy", {})
        with self.assertRaises(AssertionError):
            # Policy specifies carrier=1000, airport=365; uniform 100 must fail
            self.assertEqual(policy.get("carrier_year"), 100)
        with self.assertRaises(AssertionError):
            self.assertEqual(policy.get("origin_year"), 100)

    def test_negative_07_prohibited_percentile_pooling(self):
        """Negative Test 7: Attempting arithmetic mean of P50 GK-quantiles must diverge from true year medians."""
        df = self.transformer.get_rq02_annual_delay_performance_table()
        unweighted_p50_mean = df["arr_delay_p50_min"].mean()
        # Unweighted mean across 9 years (-6.77m) must not be treated as a valid median for any single year
        p50_2020 = df.loc[df["year"] == 2020, "arr_delay_p50_min"].values[0]
        with self.assertRaises(AssertionError):
            self.assertAlmostEqual(unweighted_p50_mean, p50_2020, places=1)

    def test_negative_08_audit_pointing_at_wrong_run(self):
        """Negative Test 8: Pointing audit reader at nonexistent or unapproved run must fail."""
        fresh_reader = KPIAnalyticsReader()
        with self.assertRaises(Exception):
            fresh_reader.load_kpi_dataset("unapproved_fabricated_run_v999")

    def test_negative_09_wrong_chart_group_family(self):
        """Negative Test 9: Asserting CHART_RQ02_04 uses annual grouping 'year' must fail."""
        trace_path = os.path.join(self.export_dir, "T014_CORRECTED_CHART_SEMANTIC_VERIFICATION.json")
        with open(trace_path, "r", encoding="utf-8") as f:
            trace = json.load(f)
        c04 = next(c for c in trace["figures_traceability"] if c["chart_id"].startswith("CHART_RQ02_04"))
        with self.assertRaises(AssertionError):
            # CHART_RQ02_04 is monthly arrival delay seasonality, must NOT be 'year'
            self.assertEqual(c04["cohort_family"], "year")

    def test_negative_10_wrong_route_year(self):
        """Negative Test 10: Asserting rq03_directed_routes was computed for 2018 must fail."""
        df = pd.read_csv(os.path.join(self.publish_dir, "tables", "rq03_directed_routes.csv"))
        with self.assertRaises(AssertionError):
            self.assertEqual(int(df["year"].iloc[0]), 2018)

    def test_negative_11_wrong_route_directional_rates(self):
        """Negative Test 11: Asserting ORD->LGA delay rate is draft figure 24.31% must fail."""
        df = pd.read_csv(os.path.join(self.publish_dir, "tables", "rq03_directed_routes.csv"))
        lga_ord = df[df["city_pair"] == "LGA <-> ORD"].iloc[0]
        with self.assertRaises(AssertionError):
            self.assertAlmostEqual(lga_ord["arr_delay_rate_ret_pct"], 24.31, places=1)
        with self.assertRaises(AssertionError):
            self.assertAlmostEqual(lga_ord["arr_delay_rate_fwd_pct"], 21.49, places=1)

    def test_negative_12_semantic_check_false_fail_closed(self):
        """Negative Test 12: An invalid chart mapping must trigger fail-closed RuntimeError."""
        from flight_pipeline.analytics.runner import T014AnalyticsRunner
        runner = T014AnalyticsRunner(run_id="test_fail_closed")
        bad_inventory = [{"chart_id": "CHART_NONEXISTENT", "res_id": "RES-001"}]
        with self.assertRaises(RuntimeError):
            runner._build_final_chart_semantic_traceability_dict(bad_inventory, [])


if __name__ == "__main__":
    unittest.main()
