"""
tests/test_g6_kpi_contract_consistency.py

Regression test for Finding G6-C02:
Verifies that the 8 CORE KPIs in documentation and production code match
the authoritative contracts approved in KPI_SPEC.md, FP-DEC-008, FP-DEC-011,
FP-DEC-012, FP-DEC-015, and FP-DEC-016.
"""

from pathlib import Path
import sys
import unittest

ROOT_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT_DIR / "src"
DOCS_DIR = ROOT_DIR / "docs"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from flight_pipeline.kpi.catalog import (
    CORE_KPI_DEFINITIONS,
    KPI_OUTPUT_COLUMNS,
    PERCENTILE_APPROX_ACCURACY,
    UNIT_STATUS_ZERO_DENOMINATOR,
    MIN_N_CARRIER_YEAR,
    MIN_N_AIRPORT_YEAR,
    MIN_N_ROUTE_YEAR,
)


class TestG6KpiContractConsistency(unittest.TestCase):
    def test_01_core_kpi_ids_and_counts(self):
        """The core KPI catalog must contain exactly KPI-01 through KPI-08."""
        kpi_ids = sorted(list(set(k.kpi_id for k in CORE_KPI_DEFINITIONS)))
        self.assertEqual(kpi_ids, [
            "KPI-01", "KPI-02", "KPI-03", "KPI-04",
            "KPI-05", "KPI-06", "KPI-07", "KPI-08"
        ])

    def test_02_submetrics_structure(self):
        """KPI-06 has 2 submetrics (P50, P90); KPI-07 has 2; KPI-08 has 3."""
        kpi_06_subs = [k.submetric for k in CORE_KPI_DEFINITIONS if k.kpi_id == "KPI-06"]
        self.assertEqual(kpi_06_subs, ["P50", "P90"])

        kpi_07_subs = [k.submetric for k in CORE_KPI_DEFINITIONS if k.kpi_id == "KPI-07"]
        self.assertEqual(kpi_07_subs, ["TAXI_OUT", "TAXI_IN"])

        kpi_08_subs = [k.submetric for k in CORE_KPI_DEFINITIONS if k.kpi_id == "KPI-08"]
        self.assertEqual(kpi_08_subs, ["AIR_TIME", "ACTUAL_ELAPSED_TIME", "CRS_ELAPSED_TIME"])

    def test_03_percentile_approx_accuracy(self):
        """FP-DEC-015 requires percentile_approx accuracy=10000."""
        self.assertEqual(PERCENTILE_APPROX_ACCURACY, 10000)

    def test_04_zero_denominator_label(self):
        """FP-DEC-011 requires ZERO_METRIC_DENOMINATOR label when N_valid=0."""
        self.assertEqual(UNIT_STATUS_ZERO_DENOMINATOR, "ZERO_METRIC_DENOMINATOR")

    def test_05_min_n_thresholds(self):
        """FP-DEC-016 requires specific sample size thresholds."""
        self.assertEqual(MIN_N_CARRIER_YEAR, 1000)
        self.assertEqual(MIN_N_AIRPORT_YEAR, 365)
        self.assertEqual(MIN_N_ROUTE_YEAR, 100)

    def test_06_canonical_17_columns(self):
        """Every KPI output row must have exactly the 17 canonical columns under DC-11/12."""
        self.assertEqual(len(KPI_OUTPUT_COLUMNS), 17)
        expected_cols = [
            "kpi_id", "submetric", "run_id", "kpi_version", "source_year",
            "group_dimensions", "filter_definition", "count_records",
            "count_metric_valid", "excluded_count", "metric_valid_rate",
            "source_coverage_status", "value", "unit_status", "min_n_status",
            "quality_version", "provenance_reference",
        ]
        self.assertEqual(KPI_OUTPUT_COLUMNS, expected_cols)

    def test_07_checklist_v2_section4_consistency(self):
        """G6_T012_FINAL_EXECUTION_CHECKLIST_V2.md Section 4 must reflect approved 8 CORE KPIs."""
        chk_path = DOCS_DIR / "05-evidence" / "G6_T012_FINAL_EXECUTION_CHECKLIST_V2.md"
        self.assertTrue(chk_path.exists())
        content = chk_path.read_text(encoding="utf-8")

        # Must describe approved KPIs
        self.assertIn("KPI-01:", content)
        self.assertIn("KPI-02:", content)
        self.assertIn("KPI-03:", content)
        self.assertIn("KPI-04:", content)
        self.assertIn("KPI-05:", content)
        self.assertIn("KPI-06:", content)
        self.assertIn("KPI-07:", content)
        self.assertIn("KPI-08:", content)
        self.assertIn("percentile_approx", content)
        self.assertIn("accuracy=10000", content)
        self.assertIn("TAXI_OUT", content)
        self.assertIn("TAXI_IN", content)
        self.assertIn("AIR_TIME", content)
        self.assertIn("ACTUAL_ELAPSED_TIME", content)
        self.assertIn("CRS_ELAPSED_TIME", content)

        # Must explicitly reject forbidden proxies
        self.assertNotIn("Severe Delay Rate (\\ge 60 min)", content)
        self.assertNotIn("Elapsed Time Ratio (Actual / Scheduled)", content)
        self.assertNotIn("Flight Volume & Cancellation Proxy", content)


if __name__ == "__main__":
    unittest.main()
