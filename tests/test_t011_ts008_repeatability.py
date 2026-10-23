"""
Contractual test suite for TS-008 (percentile_approx accuracy, min-N thresholds)
and TS-012 (deterministic aggregation repeatability).
Conforms to Master Execution Prompt T-011 Phase 2, FP-DEC-015, and FP-DEC-016.
"""

import math
from pathlib import Path
import random
import sys
import unittest
from typing import List, Dict, Any

SRC_DIR = Path(__file__).resolve().parents[1] / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))
ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from pyspark.sql import functions as F
from pyspark.sql.types import StructType, StructField, StringType, DoubleType

from flight_pipeline.config.spark_config import (
    SparkConfig,
    get_spark_session,
    stop_spark_session,
    setup_pyspark_env,
)
from flight_pipeline.kpi.calculator import KpiCalculator
from flight_pipeline.kpi.catalog import (
    PERCENTILE_APPROX_ACCURACY,
    MIN_N_STATUS_SUPPRESSED,
    MIN_N_STATUS_LOW_SAMPLE_CAUTION,
    MIN_N_STATUS_SUFFICIENT,
)


class TestTs008AndRepeatability(unittest.TestCase):
    """Test suite validating TS-008 GK-sketch rank error and TS-012 deterministic repeatability."""

    @classmethod
    def setUpClass(cls):
        setup_pyspark_env()
        config = SparkConfig(
            app_name="TestTs008Repeatability",
            master="local[2]",
            shuffle_partitions=2,
            driver_memory="2g",
            memory_overhead="512m",
        )
        cls.spark = get_spark_session(config)
        cls.calc = KpiCalculator(run_id="test_run_ts008")

    @classmethod
    def tearDownClass(cls):
        stop_spark_session()

    def _create_df(self, records: List[Dict[str, Any]]):
        schema = StructType([
            StructField("FL_DATE", StringType(), True),
            StructField("OP_CARRIER", StringType(), True),
            StructField("OP_CARRIER_FL_NUM", DoubleType(), True),
            StructField("ORIGIN", StringType(), True),
            StructField("DEST", StringType(), True),
            StructField("ARR_DELAY", DoubleType(), True),
            StructField("DEP_DELAY", DoubleType(), True),
            StructField("TAXI_OUT", DoubleType(), True),
            StructField("TAXI_IN", DoubleType(), True),
            StructField("AIR_TIME", DoubleType(), True),
            StructField("ACTUAL_ELAPSED_TIME", DoubleType(), True),
            StructField("CRS_ELAPSED_TIME", DoubleType(), True),
        ])
        return self.spark.createDataFrame(records, schema=schema)

    def test_01_gk_sketch_rank_error_on_skewed_distribution(self):
        """
        TS-008 & FP-DEC-015:
        Verify that percentile_approx(ARR_DELAY, [0.5, 0.9], accuracy=10000)
        guarantees relative rank error epsilon_rank <= 0.01% (0.0001) on a controlled sample (N >= 20000).
        Evaluates P50 and P90 using rank interval [R_low/N, R_high/N].
        """
        random.seed(42)
        n = 25000  # 1/N = 0.00004 < 0.0001
        # Continuous skewed distribution with distinct values to minimize discrete ties
        delays = []
        for i in range(n):
            u = random.random()
            if u < 0.60:
                delays.append(random.uniform(-40.0, 14.9))
            elif u < 0.90:
                delays.append(random.uniform(15.0, 120.0))
            else:
                delays.append(random.expovariate(1.0 / 200.0) + 120.0)

        # Add explicit historical extrema: min -238.0 and max +4405.0
        delays[0] = -238.0
        delays[1] = 4405.0

        records = [
            {
                "FL_DATE": "2016-01-01", "OP_CARRIER": "AA", "OP_CARRIER_FL_NUM": float(i),
                "ORIGIN": "JFK", "DEST": "LAX", "ARR_DELAY": delays[i], "DEP_DELAY": 0.0,
                "TAXI_OUT": 15.0, "TAXI_IN": 5.0, "AIR_TIME": 100.0,
                "ACTUAL_ELAPSED_TIME": 120.0, "CRS_ELAPSED_TIME": 120.0,
            }
            for i in range(n)
        ]

        df = self._create_df(records)
        res = self.calc.compute_kpis_for_cohort(df, source_year="2016").collect()

        p50_row = [r for r in res if r["kpi_id"] == "KPI-06" and r["submetric"] == "P50"][0]
        p90_row = [r for r in res if r["kpi_id"] == "KPI-06" and r["submetric"] == "P90"][0]

        p50_spark = p50_row["value"]
        p90_spark = p90_row["value"]

        self.assertIsNotNone(p50_spark)
        self.assertIsNotNone(p90_spark)

        # Theoretical GK bound with accuracy=10000 is epsilon <= 1/10000 = 0.0001
        epsilon = 1.0 / PERCENTILE_APPROX_ACCURACY  # 0.0001
        sorted_delays = sorted(delays)

        # Check P50 rank interval
        r_low_p50 = sum(1 for x in sorted_delays if x < p50_spark)
        r_high_p50 = sum(1 for x in sorted_delays if x <= p50_spark)
        rel_low_p50 = r_low_p50 / n
        rel_high_p50 = r_high_p50 / n
        dist_p50 = max(0.0, rel_low_p50 - 0.5, 0.5 - rel_high_p50)
        self.assertLessEqual(
            dist_p50,
            epsilon + (1.0 / n),
            f"P50 rank distance {dist_p50} exceeds GK accuracy bound {epsilon}",
        )

        # Check P90 rank interval
        r_low_p90 = sum(1 for x in sorted_delays if x < p90_spark)
        r_high_p90 = sum(1 for x in sorted_delays if x <= p90_spark)
        rel_low_p90 = r_low_p90 / n
        rel_high_p90 = r_high_p90 / n
        dist_p90 = max(0.0, rel_low_p90 - 0.9, 0.9 - rel_high_p90)
        self.assertLessEqual(
            dist_p90,
            epsilon + (1.0 / n),
            f"P90 rank distance {dist_p90} exceeds GK accuracy bound {epsilon}",
        )

    def test_02_ts012_deterministic_repeatability(self):
        """
        TS-012: Running KPI computation on the same input multiple times
        must yield mathematically identical numeric results across all columns.
        """
        records = [
            {"FL_DATE": "2016-01-01", "OP_CARRIER": "AA", "OP_CARRIER_FL_NUM": float(i),
             "ORIGIN": "ORD", "DEST": "DFW", "ARR_DELAY": float(i % 50 - 15), "DEP_DELAY": float(i % 40 - 10),
             "TAXI_OUT": 12.0 + (i % 5), "TAXI_IN": 6.0 + (i % 3), "AIR_TIME": 90.0 + (i % 10),
             "ACTUAL_ELAPSED_TIME": 108.0 + (i % 18), "CRS_ELAPSED_TIME": 110.0}
            for i in range(100)
        ]

        df1 = self._create_df(records)
        df2 = self._create_df(records)

        calc1 = KpiCalculator(run_id="run_repeat_01")
        calc2 = KpiCalculator(run_id="run_repeat_02")

        res1 = calc1.compute_kpis_for_cohort(df1, source_year="2016").collect()
        res2 = calc2.compute_kpis_for_cohort(df2, source_year="2016").collect()

        self.assertEqual(len(res1), len(res2))

        # Map by (kpi_id, submetric)
        map1 = {f"{r['kpi_id']}:{r['submetric']}": r for r in res1}
        map2 = {f"{r['kpi_id']}:{r['submetric']}": r for r in res2}

        self.assertEqual(set(map1.keys()), set(map2.keys()))

        for k in map1:
            r1 = map1[k]
            r2 = map2[k]

            # Invariant: Business and statistical values are strictly identical
            self.assertEqual(r1["count_records"], r2["count_records"])
            self.assertEqual(r1["count_metric_valid"], r2["count_metric_valid"])
            self.assertEqual(r1["excluded_count"], r2["excluded_count"])
            self.assertEqual(r1["metric_valid_rate"], r2["metric_valid_rate"])
            self.assertEqual(r1["unit_status"], r2["unit_status"])
            self.assertEqual(r1["min_n_status"], r2["min_n_status"])

            if r1["value"] is None:
                self.assertIsNone(r2["value"])
            else:
                self.assertEqual(r1["value"], r2["value"])

    def test_03_tied_values_and_extreme_outliers(self):
        """TS-008: Verify behavior on tied values and extreme outliers."""
        records = [
            # 50 records with identical delay 15.0
            {"FL_DATE": "2016-01-01", "OP_CARRIER": "AA", "OP_CARRIER_FL_NUM": float(i),
             "ORIGIN": "A", "DEST": "B", "ARR_DELAY": 15.0, "DEP_DELAY": 15.0,
             "TAXI_OUT": 10.0, "TAXI_IN": 5.0, "AIR_TIME": 50.0,
             "ACTUAL_ELAPSED_TIME": 65.0, "CRS_ELAPSED_TIME": 65.0}
            for i in range(50)
        ] + [
            # 1 extreme outlier: 4405.0 min
            {"FL_DATE": "2016-01-01", "OP_CARRIER": "AA", "OP_CARRIER_FL_NUM": 999.0,
             "ORIGIN": "A", "DEST": "B", "ARR_DELAY": 4405.0, "DEP_DELAY": 4400.0,
             "TAXI_OUT": 10.0, "TAXI_IN": 5.0, "AIR_TIME": 50.0,
             "ACTUAL_ELAPSED_TIME": 65.0, "CRS_ELAPSED_TIME": 65.0}
        ]

        df = self._create_df(records)
        res = self.calc.compute_kpis_for_cohort(df, source_year="2016").collect()

        # Median of 51 records (50 of which are 15.0) must be 15.0
        p50 = [r for r in res if r["kpi_id"] == "KPI-06" and r["submetric"] == "P50"][0]
        self.assertAlmostEqual(p50["value"], 15.0, places=2)

    def test_04_null_and_nan_inf_exclusion_from_quantiles(self):
        """TS-008: Non-finite values (null, NaN, Inf) must be cleanly excluded from quantiles."""
        records = [
            {"FL_DATE": "2016-01-01", "OP_CARRIER": "AA", "OP_CARRIER_FL_NUM": 1.0,
             "ORIGIN": "A", "DEST": "B", "ARR_DELAY": 10.0, "DEP_DELAY": 10.0,
             "TAXI_OUT": 10.0, "TAXI_IN": 5.0, "AIR_TIME": 50.0,
             "ACTUAL_ELAPSED_TIME": 65.0, "CRS_ELAPSED_TIME": 65.0},
            {"FL_DATE": "2016-01-01", "OP_CARRIER": "AA", "OP_CARRIER_FL_NUM": 2.0,
             "ORIGIN": "A", "DEST": "B", "ARR_DELAY": float("nan"), "DEP_DELAY": 10.0,
             "TAXI_OUT": 10.0, "TAXI_IN": 5.0, "AIR_TIME": 50.0,
             "ACTUAL_ELAPSED_TIME": 65.0, "CRS_ELAPSED_TIME": 65.0},
            {"FL_DATE": "2016-01-01", "OP_CARRIER": "AA", "OP_CARRIER_FL_NUM": 3.0,
             "ORIGIN": "A", "DEST": "B", "ARR_DELAY": float("inf"), "DEP_DELAY": 10.0,
             "TAXI_OUT": 10.0, "TAXI_IN": 5.0, "AIR_TIME": 50.0,
             "ACTUAL_ELAPSED_TIME": 65.0, "CRS_ELAPSED_TIME": 65.0},
            {"FL_DATE": "2016-01-01", "OP_CARRIER": "AA", "OP_CARRIER_FL_NUM": 4.0,
             "ORIGIN": "A", "DEST": "B", "ARR_DELAY": None, "DEP_DELAY": 10.0,
             "TAXI_OUT": 10.0, "TAXI_IN": 5.0, "AIR_TIME": 50.0,
             "ACTUAL_ELAPSED_TIME": 65.0, "CRS_ELAPSED_TIME": 65.0},
            {"FL_DATE": "2016-01-01", "OP_CARRIER": "AA", "OP_CARRIER_FL_NUM": 5.0,
             "ORIGIN": "A", "DEST": "B", "ARR_DELAY": 20.0, "DEP_DELAY": 10.0,
             "TAXI_OUT": 10.0, "TAXI_IN": 5.0, "AIR_TIME": 50.0,
             "ACTUAL_ELAPSED_TIME": 65.0, "CRS_ELAPSED_TIME": 65.0},
        ]
        df = self._create_df(records)
        res = self.calc.compute_kpis_for_cohort(df, source_year="2016").collect()

        p50 = [r for r in res if r["kpi_id"] == "KPI-06" and r["submetric"] == "P50"][0]
        # Valid records are exactly 2 (10.0 and 20.0) -> P50 is between 10.0 and 20.0
        self.assertEqual(p50["count_metric_valid"], 2)
        self.assertEqual(p50["excluded_count"], 3)
        self.assertTrue(10.0 <= p50["value"] <= 20.0)


if __name__ == "__main__":
    unittest.main()
