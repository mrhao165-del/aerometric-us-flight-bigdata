"""
Unit tests for finite numeric predicates and metric validity filters.
Conforms to T006_FINAL_CORRECTIONS_ADDENDUM.md Section 3 (FIX-02) test matrix.
"""

import math
import sys
import unittest
from pathlib import Path

# Add src to sys.path
SRC_DIR = Path(__file__).resolve().parents[1] / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from flight_pipeline.config.spark_config import get_spark_session, stop_spark_session
from flight_pipeline.quality.predicates import (
    is_finite_numeric,
    is_valid_arr_delay,
    is_valid_dep_delay,
    is_valid_taxi_out,
    is_valid_taxi_in,
    is_valid_air_time,
    is_valid_actual_elapsed_time,
    is_valid_crs_elapsed_time,
)


class TestNumericPredicates(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.spark = get_spark_session()

    @classmethod
    def tearDownClass(cls):
        stop_spark_session(cls.spark)

    def test_is_finite_numeric_matrix(self):
        """Test is_finite_numeric against None, NaN, +inf, -inf, 0, negative and positive numbers."""
        test_data = [
            (1, None),
            (2, float("nan")),
            (3, float("inf")),
            (4, float("-inf")),
            (5, 0.0),
            (6, -15.5),
            (7, 42.0),
        ]
        df = self.spark.createDataFrame(test_data, ["id", "val"])
        res = df.withColumn("is_finite", is_finite_numeric("val")).collect()
        res_map = {row["id"]: row["is_finite"] for row in res}

        self.assertFalse(res_map[1], "None must NOT be finite")
        self.assertFalse(res_map[2], "NaN must NOT be finite")
        self.assertFalse(res_map[3], "+Inf must NOT be finite")
        self.assertFalse(res_map[4], "-Inf must NOT be finite")
        self.assertTrue(res_map[5], "0.0 must be finite")
        self.assertTrue(res_map[6], "-15.5 must be finite")
        self.assertTrue(res_map[7], "42.0 must be finite")

    def test_delay_predicates_preserve_signed_negative(self):
        """Test that ARR_DELAY and DEP_DELAY preserve signed negative values."""
        test_data = [
            ("r1", -25.0, -10.0),   # Early arrival and departure
            ("r2", 0.0, 0.0),       # On-time
            ("r3", 15.0, 30.0),     # Late
            ("r4", None, float("nan")), # Invalid
        ]
        df = self.spark.createDataFrame(test_data, ["id", "ARR_DELAY", "DEP_DELAY"])
        eval_df = df.withColumn("arr_valid", is_valid_arr_delay()).withColumn("dep_valid", is_valid_dep_delay())
        rows = {r["id"]: r for r in eval_df.collect()}

        self.assertTrue(rows["r1"]["arr_valid"], "Negative arrival delay must be VALID (signed preservation)")
        self.assertTrue(rows["r1"]["dep_valid"], "Negative departure delay must be VALID (signed preservation)")
        self.assertTrue(rows["r2"]["arr_valid"])
        self.assertTrue(rows["r3"]["arr_valid"])
        self.assertFalse(rows["r4"]["arr_valid"])
        self.assertFalse(rows["r4"]["dep_valid"])

    def test_taxi_predicates_require_non_negative(self):
        """Test TAXI_OUT and TAXI_IN domain constraints (>= 0.0)."""
        test_data = [
            ("t1", 0.0, 5.0),
            ("t2", -1.0, 10.0),
            ("t3", 15.0, -0.5),
            ("t4", float("nan"), None),
        ]
        df = self.spark.createDataFrame(test_data, ["id", "TAXI_OUT", "TAXI_IN"])
        eval_df = df.withColumn("out_valid", is_valid_taxi_out()).withColumn("in_valid", is_valid_taxi_in())
        rows = {r["id"]: r for r in eval_df.collect()}

        self.assertTrue(rows["t1"]["out_valid"])
        self.assertTrue(rows["t1"]["in_valid"])
        self.assertFalse(rows["t2"]["out_valid"], "Negative TAXI_OUT must be invalid")
        self.assertTrue(rows["t2"]["in_valid"], "Positive TAXI_IN must be valid independently")
        self.assertTrue(rows["t3"]["out_valid"])
        self.assertFalse(rows["t3"]["in_valid"], "Negative TAXI_IN must be invalid")
        self.assertFalse(rows["t4"]["out_valid"])
        self.assertFalse(rows["t4"]["in_valid"])

    def test_duration_predicates_require_strictly_positive(self):
        """Test AIR_TIME, ACTUAL_ELAPSED_TIME, CRS_ELAPSED_TIME domain constraints (> 0.0)."""
        test_data = [
            ("d1", 60.0, 80.0, 75.0),
            ("d2", 0.0, 0.0, 0.0),      # Non-positive duration is invalid
            ("d3", -10.0, -20.0, -15.0), # Negative duration is invalid
            ("d4", None, float("inf"), float("nan")),
        ]
        df = self.spark.createDataFrame(test_data, ["id", "AIR_TIME", "ACTUAL_ELAPSED_TIME", "CRS_ELAPSED_TIME"])
        eval_df = (
            df.withColumn("air_valid", is_valid_air_time())
            .withColumn("act_valid", is_valid_actual_elapsed_time())
            .withColumn("crs_valid", is_valid_crs_elapsed_time())
        )
        rows = {r["id"]: r for r in eval_df.collect()}

        self.assertTrue(rows["d1"]["air_valid"])
        self.assertTrue(rows["d1"]["act_valid"])
        self.assertTrue(rows["d1"]["crs_valid"])
        self.assertFalse(rows["d2"]["air_valid"], "0.0 AIR_TIME must be invalid (flight must take > 0 min)")
        self.assertFalse(rows["d2"]["act_valid"])
        self.assertFalse(rows["d3"]["air_valid"])
        self.assertFalse(rows["d4"]["air_valid"])
        self.assertFalse(rows["d4"]["act_valid"])


if __name__ == "__main__":
    unittest.main()
