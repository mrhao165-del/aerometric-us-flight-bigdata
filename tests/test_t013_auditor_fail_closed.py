"""
Mandatory mutation test suite for T-013 Auditor Fail-Closed Logic.
Verifies the 5 mandatory scenarios from T013-FINAL-EVIDENCE-RECONCILIATION Section 3:
1. Valid reference values pass.
2. An intentionally incorrect rate fails.
3. An intentionally incorrect signed mean fails.
4. A materially incorrect P50/P90 does not receive PASS merely because of the previous fallback.
5. A failed invariant forces the overall verdict away from PASS.

Uses synthetic data fixtures only. Never touches real production datasets.
"""

import sys
from pathlib import Path
import unittest

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from tools.qa.run_t013_math_independent_audit import (
    evaluate_metric_stream,
    evaluate_percentile_rank_error,
    derive_overall_mathematical_verdict,
)


class TestT013AuditorFailClosed(unittest.TestCase):

    def test_01_valid_reference_values_pass(self):
        """Scenario 1: Valid reference values pass rate, mean, percentile, and overall verdict."""
        # 1. Valid rate
        comp_rate = evaluate_metric_stream(
            kid="KPI-02",
            sub=None,
            ref_val=0.163587,
            ref_valid=1000,
            ref_exc=0,
            check_type="float",
            pub_val=0.163587,
            pub_valid=1000,
            pub_exc=0,
            pub_rec=1000,
            n_records=1000,
            pub_mn="SUFFICIENT",
        )
        self.assertEqual(comp_rate["status"], "PASS")

        # 2. Valid signed mean
        comp_mean = evaluate_metric_stream(
            kid="KPI-03",
            sub=None,
            ref_val=-4.51234,
            ref_valid=1000,
            ref_exc=0,
            check_type="float",
            pub_val=-4.51234,
            pub_valid=1000,
            pub_exc=0,
            pub_rec=1000,
            n_records=1000,
            pub_mn="SUFFICIENT",
        )
        self.assertEqual(comp_mean["status"], "PASS")

        # 3. Valid percentile (GK sketch rank distance = 0)
        sorted_delays = list(range(-50, 50))  # 100 items
        rank_err, rank_dist, stat = evaluate_percentile_rank_error(
            sorted_values=sorted_delays,
            v_pub=0.0,
            phi=0.5,
            accuracy=10000,
        )
        self.assertEqual(stat, "PASS")
        self.assertEqual(rank_dist, 0.0)

        # 4. Overall verdict derive PASS
        mock_invariants = {
            "inv1": {"status": "PASS", "verified": True},
            "inv2": {"status": "NOT_APPLICABLE_IN_OBSERVED_PRODUCTION_COHORTS", "verified": True},
        }
        mock_cohorts = [{"cohort_name": "c1", "all_streams_passed": True, "metric_comparisons": [comp_rate, comp_mean]}]
        verdict, unverified, stmt = derive_overall_mathematical_verdict(mock_invariants, mock_cohorts)
        self.assertEqual(verdict, "PASS")
        self.assertEqual(len(unverified), 0)

    def test_02_incorrect_rate_fails(self):
        """Scenario 2: An intentionally incorrect rate fails and forces overall verdict to FAIL."""
        comp_rate = evaluate_metric_stream(
            kid="KPI-02",
            sub=None,
            ref_val=0.150000,
            ref_valid=1000,
            ref_exc=0,
            check_type="float",
            pub_val=0.250000,  # Intentionally perturbed rate
            pub_valid=1000,
            pub_exc=0,
            pub_rec=1000,
            n_records=1000,
            pub_mn="SUFFICIENT",
        )
        self.assertEqual(comp_rate["status"], "FAIL_DELTA_EXCEEDED")
        self.assertAlmostEqual(comp_rate["delta"], 0.10, places=5)

        mock_invariants = {"inv1": {"status": "PASS", "verified": True}}
        mock_cohorts = [{"cohort_name": "c1", "all_streams_passed": False, "metric_comparisons": [comp_rate]}]
        verdict, unverified, stmt = derive_overall_mathematical_verdict(mock_invariants, mock_cohorts)
        self.assertEqual(verdict, "FAIL")
        self.assertIn("cohort failures", stmt)

    def test_03_incorrect_signed_mean_fails(self):
        """Scenario 3: An intentionally incorrect signed mean fails and forces overall verdict to FAIL."""
        comp_mean = evaluate_metric_stream(
            kid="KPI-05",
            sub=None,
            ref_val=8.500000,
            ref_valid=1000,
            ref_exc=0,
            check_type="float",
            pub_val=-5.000000,  # Intentionally perturbed sign and value
            pub_valid=1000,
            pub_exc=0,
            pub_rec=1000,
            n_records=1000,
            pub_mn="SUFFICIENT",
        )
        self.assertEqual(comp_mean["status"], "FAIL_DELTA_EXCEEDED")
        self.assertAlmostEqual(comp_mean["delta"], 13.50, places=5)

        mock_invariants = {"inv1": {"status": "PASS", "verified": True}}
        mock_cohorts = [{"cohort_name": "c1", "all_streams_passed": False, "metric_comparisons": [comp_mean]}]
        verdict, unverified, stmt = derive_overall_mathematical_verdict(mock_invariants, mock_cohorts)
        self.assertEqual(verdict, "FAIL")

    def test_04_materially_incorrect_percentile_fails_gk_tolerance(self):
        """
        Scenario 4: A materially incorrect P50/P90 does not receive PASS merely because
        of an absolute minute threshold (e.g. delta <= 2.0).
        """
        # Create 10,000 distinct sorted values: [-5000, ..., 4999]
        # True median (P50, rank 5000) is 0.
        sorted_delays = [float(x) for x in range(-5000, 5000)]
        N = len(sorted_delays)  # 10,000

        # Suppose published P50 is 1.5.
        # Absolute minute difference is |1.5 - 0.0| = 1.5 <= 2.0.
        # Under the old defective logic (`delta <= 2.0`), this would have returned PASS!
        # But in a 10,000-flight dataset, 1.5 minutes represents a rank difference of 1500 items!
        # Empirical rank error = 1500 / 10000 = 0.15 >> epsilon (0.0001).
        rank_err, rank_dist, stat = evaluate_percentile_rank_error(
            sorted_values=sorted_delays,
            v_pub=1.5,
            phi=0.5,
            accuracy=10000,
        )

        self.assertGreater(rank_err, 0.0001)
        self.assertEqual(stat, "FAIL_GK_RANK_TOLERANCE_EXCEEDED")

        comp_p50 = evaluate_metric_stream(
            kid="KPI-06",
            sub="P50",
            ref_val=0.0,
            ref_valid=N,
            ref_exc=0,
            check_type="percentile",
            pub_val=1.5,
            pub_valid=N,
            pub_exc=0,
            pub_rec=N,
            n_records=N,
            pub_mn="SUFFICIENT",
            sorted_arr_delay=sorted_delays,
            accuracy=10000,
        )
        self.assertEqual(comp_p50["status"], "FAIL_GK_RANK_TOLERANCE_EXCEEDED")

        mock_invariants = {"inv1": {"status": "PASS", "verified": True}}
        mock_cohorts = [{"cohort_name": "c1", "all_streams_passed": False, "metric_comparisons": [comp_p50]}]
        verdict, unverified, stmt = derive_overall_mathematical_verdict(mock_invariants, mock_cohorts)
        self.assertEqual(verdict, "FAIL")

    def test_05_failed_invariant_forces_verdict_away_from_pass(self):
        """Scenario 5: A broken invariant forces overall verdict to FAIL even if cohorts pass."""
        mock_invariants = {
            "dc12_denominator_conservation": {"status": "FAIL", "violations": 1, "verified": True},
            "rate_bounds": {"status": "PASS", "verified": True},
        }
        mock_cohorts = [{"cohort_name": "c1", "all_streams_passed": True, "metric_comparisons": []}]
        verdict, unverified, stmt = derive_overall_mathematical_verdict(mock_invariants, mock_cohorts)
        self.assertEqual(verdict, "FAIL")
        self.assertIn("invariant failures", stmt)


if __name__ == "__main__":
    unittest.main()
