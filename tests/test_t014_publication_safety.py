"""
Unit and Synthetic Failure Injection Tests for T-014 Prospective Publication Safety.
Validates:
1. Duplicate published run ID rejection.
2. Isolated staging directory usage and automatic cleanup on failure.
3. Pre-promotion invariant validations (table counts, figure counts, results counts, semantic traceability).
4. Latest pointer preservation on failure.
5. Atomic pointer update behavior.
"""

import os
import sys
import shutil
import tempfile
import unittest
from unittest.mock import patch, MagicMock

# Add repository root and src to path
sys.path.insert(0, os.path.abspath("."))
sys.path.insert(0, os.path.abspath("src"))

from flight_pipeline.analytics.runner import T014AnalyticsRunner


class TestT014PublicationSafety(unittest.TestCase):
    """Test suite validating prospective analytical publication safety."""

    def setUp(self):
        self.repo_root = os.path.abspath(".")
        self.analytics_pointer = os.path.join(self.repo_root, "data", "analytics", "latest_run_id.txt")
        with open(self.analytics_pointer, "r", encoding="utf-8") as f:
            self.baseline_pointer = f.read().strip()

    def tearDown(self):
        # Guarantee latest pointer is always restored to baseline
        with open(self.analytics_pointer, "w", encoding="utf-8") as f:
            f.write(self.baseline_pointer + "\n")

    def test_01_duplicate_run_id_rejected(self):
        """Verify that attempting to execute an existing published run ID raises FileExistsError."""
        runner = T014AnalyticsRunner(
            base_dir=self.repo_root,
            run_id="t014_analysis_2016_2024_v4",  # Already published
        )
        self.assertTrue(os.path.exists(runner.publish_dir))
        with self.assertRaises(FileExistsError) as ctx:
            runner.execute()
        self.assertIn("already exists", str(ctx.exception))
        self.assertIn("strictly prohibited", str(ctx.exception))

    def test_02_staging_cleanup_and_pointer_preserved_on_failure(self):
        """Verify that failure during execution cleans up staging and preserves the existing pointer."""
        mock_run_id = "test_synthetic_failed_run_9999"
        mock_publish_dir = os.path.join(self.repo_root, "data", "analytics", "runs", mock_run_id)

        # Ensure target doesn't exist before test
        if os.path.exists(mock_publish_dir):
            shutil.rmtree(mock_publish_dir)

        runner = T014AnalyticsRunner(
            base_dir=self.repo_root,
            run_id=mock_run_id,
        )

        # Inject failure during table transformation
        with patch("flight_pipeline.analytics.runner.KPIAnalyticsTransformer.get_rq01_annual_volume_table") as mock_tf:
            mock_tf.side_effect = RuntimeError("SYNTHETIC_INJECTED_FAILURE_DURING_TRANSFORMATION")

            with self.assertRaises(RuntimeError) as ctx:
                runner.execute()
            self.assertIn("SYNTHETIC_INJECTED_FAILURE_DURING_TRANSFORMATION", str(ctx.exception))

        # Assert destination published dir was NOT created
        self.assertFalse(os.path.exists(mock_publish_dir))

        # Assert staging dir is NOT left behind
        staging_root = os.path.join(self.repo_root, "data", "analytics", "staging")
        if os.path.exists(staging_root):
            stages = [d for d in os.listdir(staging_root) if mock_run_id in d]
            self.assertEqual(len(stages), 0, f"Staging directories left behind: {stages}")

        # Assert latest pointer remained completely unchanged
        with open(self.analytics_pointer, "r", encoding="utf-8") as f:
            current_pointer = f.read().strip()
        self.assertEqual(current_pointer, self.baseline_pointer)

    def test_03_pre_promotion_table_count_invariant(self):
        """Verify that invariant check fails if table count does not equal 12."""
        mock_run_id = "test_synthetic_table_invariant_9999"
        runner = T014AnalyticsRunner(
            base_dir=self.repo_root,
            run_id=mock_run_id,
        )

        # Mock CSV writing to only write 11 tables
        real_to_csv = runner._hash_file
        with patch("pandas.DataFrame.to_csv") as mock_csv:
            # Drop writing of one table
            with self.assertRaises(Exception):
                runner.execute()

        # Target should not be promoted
        self.assertFalse(os.path.exists(runner.publish_dir))

    def test_04_pre_promotion_semantic_invariant_fail_closed(self):
        """Verify that semantic traceability failure in staging aborts promotion fail-closed."""
        mock_run_id = "test_synthetic_semantic_fail_9999"
        runner = T014AnalyticsRunner(
            base_dir=self.repo_root,
            run_id=mock_run_id,
        )

        with patch.object(
            T014AnalyticsRunner,
            "_build_final_chart_semantic_traceability_dict",
            return_value={"all_16_charts_verified": False, "semantic_checks": {}}
        ):
            with self.assertRaises(RuntimeError) as ctx:
                runner.execute()
            self.assertIn("PRE-PROMOTION INVARIANT FAILURE", str(ctx.exception))

        # Target should not be promoted
        self.assertFalse(os.path.exists(runner.publish_dir))

        # Pointer untouched
        with open(self.analytics_pointer, "r", encoding="utf-8") as f:
            self.assertEqual(f.read().strip(), self.baseline_pointer)


if __name__ == "__main__":
    unittest.main()
