"""
Unit and Regression Test Suite for T-010 Production Policy Safety Guards (G3-COND-A).
Verifies that canonical production execution enforces:
- allow_unapproved_policies = False
- quarantine_non_positive_flight_num = False (OPTY-01 rejected per G3-COND-A)
- allow_weather_nulls = True (FP-DEC-017 Weather optional)
- strict_record_accounting = True (DC-11 row accounting)
- strict_metric_accounting = True (DC-12 metric accounting)
- Fail-closed behavior on unapproved simulation policies
"""

from pathlib import Path
import sys
import unittest

SRC_DIR = Path(__file__).resolve().parents[1] / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from pyspark.sql import SparkSession
from pyspark.sql.types import (
    DoubleType,
    LongType,
    StringType,
    StructField,
    StructType,
)

from flight_pipeline.config.spark_config import SparkConfig, get_spark_session, stop_spark_session
from flight_pipeline.ingestion.reader import (
    RecordStatus,
    STATUS_COLUMN,
    REASON_COLUMN,
)
from flight_pipeline.ingestion.schema import get_raw_parser_schema
from flight_pipeline.quality.accounting import (
    QualityAccountingEngine,
    AccountingBalanceError,
)
from flight_pipeline.quality.engine import QualityEngine
from flight_pipeline.quality.policy import (
    QualityPolicyConfig,
    PolicyViolationError,
    ProvisionalPolicyProfiler,
    assert_production_policy_compliance,
)


class TestT010PolicyGuards(unittest.TestCase):
    """Test suite verifying production policy hard guards and fail-closed safety."""

    @classmethod
    def setUpClass(cls):
        cfg = SparkConfig(
            app_name="TestT010PolicyGuards",
            master="local[2]",
            driver_memory="1g",
            shuffle_partitions=2,
        )
        cls.spark = get_spark_session(cfg)

    @classmethod
    def tearDownClass(cls):
        if cls.spark:
            try:
                cls.spark.stop()
            except Exception:
                pass

    def test_default_production_policy_guards(self):
        """Default QualityPolicyConfig matches canonical production invariants."""
        cfg = QualityPolicyConfig()
        self.assertFalse(cfg.quarantine_non_positive_flight_num)
        self.assertTrue(cfg.allow_weather_nulls)
        self.assertTrue(cfg.strict_record_accounting)
        self.assertTrue(cfg.strict_metric_accounting)
        self.assertFalse(cfg.allow_unapproved_policies)

        # Passes production compliance guard
        assert_production_policy_compliance(cfg)

    def test_fail_closed_on_unapproved_quarantine_flight_num(self):
        """Enabling quarantine_non_positive_flight_num without allow_unapproved_policies fails closed."""
        with self.assertRaises(PolicyViolationError) as ctx:
            QualityPolicyConfig(quarantine_non_positive_flight_num=True)
        self.assertIn("GOVERNANCE_VIOLATION", str(ctx.exception))
        self.assertIn("G3-COND-A", str(ctx.exception))

    def test_fail_closed_on_unapproved_disallow_weather_nulls(self):
        """Disallowing weather nulls without allow_unapproved_policies fails closed."""
        with self.assertRaises(PolicyViolationError) as ctx:
            QualityPolicyConfig(allow_weather_nulls=False)
        self.assertIn("GOVERNANCE_VIOLATION", str(ctx.exception))
        self.assertIn("FP-DEC-017", str(ctx.exception))

    def test_production_guard_rejects_simulation_flag(self):
        """assert_production_policy_compliance strictly rejects simulation policy."""
        sim_policy = QualityPolicyConfig(
            quarantine_non_positive_flight_num=True,
            allow_unapproved_policies=True,
        )
        with self.assertRaises(PolicyViolationError) as ctx:
            assert_production_policy_compliance(sim_policy)
        self.assertIn("PRODUCTION_GUARD_VIOLATION", str(ctx.exception))
        self.assertIn("allow_unapproved_policies=True is strictly prohibited", str(ctx.exception))

    def test_production_guard_rejects_relaxed_accounting(self):
        """assert_production_policy_compliance strictly rejects disabled record or metric accounting."""
        lax_record_policy = QualityPolicyConfig(
            strict_record_accounting=False,
            allow_unapproved_policies=True,
        )
        with self.assertRaises(PolicyViolationError) as ctx:
            assert_production_policy_compliance(lax_record_policy)
        self.assertIn("PRODUCTION_GUARD_VIOLATION", str(ctx.exception))

    def test_canonical_production_preserves_non_positive_flight_num(self):
        """In canonical production, non-positive flight numbers remain ACCEPTED per G3-COND-A."""
        schema = get_raw_parser_schema()

        rows = [
            ("2016-01-01", "AA", "100.0", "JFK", "LAX", "0800", "0805", "5.0", "15.0", "0820", "1110", "5.0", "1120", "1115", "-5.0", "380.0", "370.0", "350.0", "1.0", "1", "1", "5", "2475.0", "12892", "5.0", "0.0", "10.0", "18.0", "0.0", "5.0", "40.64", "-73.78", "33.94", "-118.41", None),
            ("2016-01-01", "AA", "0.0", "JFK", "LAX", "0800", "0805", "5.0", "15.0", "0820", "1110", "5.0", "1120", "1115", "-5.0", "380.0", "370.0", "350.0", "1.0", "1", "1", "5", "2475.0", "12892", "5.0", "0.0", "10.0", "18.0", "0.0", "5.0", "40.64", "-73.78", "33.94", "-118.41", None),
            ("2016-01-01", "AA", "-10.0", "JFK", "LAX", "0800", "0805", "5.0", "15.0", "0820", "1110", "5.0", "1120", "1115", "-5.0", "380.0", "370.0", "350.0", "1.0", "1", "1", "5", "2475.0", "12892", "5.0", "0.0", "10.0", "18.0", "0.0", "5.0", "40.64", "-73.78", "33.94", "-118.41", None),
        ]

        df = self.spark.createDataFrame(rows, schema=schema)
        engine = QualityEngine()  # Canonical production policy
        augmented_df, result = engine.evaluate(df, independent_raw_count=3, source_year=2016)

        self.assertEqual(result.accepted_count, 3)
        self.assertEqual(result.quarantined_count, 0)
        self.assertEqual(result.rejected_count, 0)
        self.assertTrue(result.row_accounting.is_balanced())

        # Provisional profiler detects anomalies without mutating status
        prof = result.provisional_policy_profile
        self.assertIsNotNone(prof)
        self.assertEqual(prof.total_records, 3)
        self.assertEqual(prof.non_positive_count, 2)
        self.assertEqual(prof.zero_count, 1)
        self.assertEqual(prof.negative_count, 1)

    def test_canonical_production_allows_weather_nulls(self):
        """In canonical production, null weather columns do NOT quarantine records per FP-DEC-017."""
        schema = get_raw_parser_schema()

        # All 6 weather fields are None
        rows = [
            ("2016-01-01", "AA", "100.0", "JFK", "LAX", "0800", "0805", "5.0", "15.0", "0820", "1110", "5.0", "1120", "1115", "-5.0", "380.0", "370.0", "350.0", "1.0", "1", "1", "5", "2475.0", "12892", None, None, None, None, None, None, "40.64", "-73.78", "33.94", "-118.41", None),
        ]

        df = self.spark.createDataFrame(rows, schema=schema)
        engine = QualityEngine()
        augmented_df, result = engine.evaluate(df, independent_raw_count=1, source_year=2016)

        self.assertEqual(result.accepted_count, 1)
        self.assertEqual(result.quarantined_count, 0)
        self.assertEqual(result.rejected_count, 0)
        self.assertTrue(result.row_accounting.is_balanced())

    def test_strict_accounting_rejects_imbalance(self):
        """DC-11 row accounting imbalance raises AccountingBalanceError."""
        schema = get_raw_parser_schema()

        rows = [
            ("2016-01-01", "AA", "100.0", "JFK", "LAX", "0800", "0805", "5.0", "15.0", "0820", "1110", "5.0", "1120", "1115", "-5.0", "380.0", "370.0", "350.0", "1.0", "1", "1", "5", "2475.0", "12892", "5.0", "0.0", "10.0", "18.0", "0.0", "5.0", "40.64", "-73.78", "33.94", "-118.41", None),
        ]

        df = self.spark.createDataFrame(rows, schema=schema)
        engine = QualityEngine()

        # Claim independent count is 100 while df only has 1 record
        with self.assertRaises(AccountingBalanceError) as ctx:
            engine.evaluate(df, independent_raw_count=100, source_year=2016)
        self.assertIn("ACCOUNTING_UNVERIFIED", str(ctx.exception))

    def test_production_guard_rejects_all_individual_violations(self):
        """assert_production_policy_compliance tests fail-closed on every single disallowed config."""
        # 1. allow_unapproved_policies True
        with self.assertRaises(PolicyViolationError):
            assert_production_policy_compliance(QualityPolicyConfig(allow_unapproved_policies=True))
        
        # 2. quarantine_non_positive_flight_num True
        with self.assertRaises(PolicyViolationError):
            assert_production_policy_compliance(QualityPolicyConfig(quarantine_non_positive_flight_num=True, allow_unapproved_policies=True))

        # 3. allow_weather_nulls False
        with self.assertRaises(PolicyViolationError):
            assert_production_policy_compliance(QualityPolicyConfig(allow_weather_nulls=False, allow_unapproved_policies=True))

        # 4. strict_record_accounting False
        with self.assertRaises(PolicyViolationError):
            assert_production_policy_compliance(QualityPolicyConfig(strict_record_accounting=False, allow_unapproved_policies=True))

        # 5. strict_metric_accounting False
        with self.assertRaises(PolicyViolationError):
            assert_production_policy_compliance(QualityPolicyConfig(strict_metric_accounting=False, allow_unapproved_policies=True))

    def test_negative_input_parser_discrepancy_caught(self):
        """Mutation test: When independent raw count != parsed records, system fails closed."""
        schema = get_raw_parser_schema()
        rows = [
            ("2016-01-01", "AA", "100.0", "JFK", "LAX", "0800", "0805", "5.0", "15.0", "0820", "1110", "5.0", "1120", "1115", "-5.0", "380.0", "370.0", "350.0", "1.0", "1", "1", "5", "2475.0", "12892", "5.0", "0.0", "10.0", "18.0", "0.0", "5.0", "40.64", "-73.78", "33.94", "-118.41", None),
            ("2016-01-02", "DL", "200.0", "ATL", "ORD", "0900", "0905", "5.0", "15.0", "0920", "1110", "5.0", "1120", "1115", "-5.0", "120.0", "110.0", "90.0", "1.0", "1", "2", "6", "10397.0", "13930", "8.0", "0.0", "5.0", "2.0", "0.0", "8.0", "33.64", "-84.43", "41.97", "-87.90", None),
        ]
        df = self.spark.createDataFrame(rows, schema=schema)
        engine = QualityEngine()

        # Injected discrepancy: independent count = 3 but df has 2
        with self.assertRaises(AccountingBalanceError):
            engine.evaluate(df, independent_raw_count=3, source_year=2016)

        # Injected discrepancy: independent count = 1 but df has 2
        with self.assertRaises(AccountingBalanceError):
            engine.evaluate(df, independent_raw_count=1, source_year=2016)


if __name__ == "__main__":
    unittest.main()

