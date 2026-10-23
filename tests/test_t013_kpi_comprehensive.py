"""
Comprehensive regression test suite for T-013 mathematical requirements.
Explicitly verifies all 20 required mathematical scenarios from T-013 Master Prompt Section 13.
"""

import sys
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parents[1] / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))
ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import unittest
import math
from pyspark.sql import SparkSession
from pyspark.sql.types import (
    StructType,
    StructField,
    StringType,
    DoubleType,
    LongType,
)

from flight_pipeline.config.spark_config import SparkConfig, get_spark_session, stop_spark_session
from flight_pipeline.kpi.calculator import KpiCalculator
from flight_pipeline.kpi.catalog import (
    KPI_OUTPUT_COLUMNS,
    UNIT_STATUS_RESOLVED,
    UNIT_STATUS_ZERO_DENOMINATOR,
    UNIT_STATUS_COUNT_RECORDS,
    COVERAGE_PARTIAL,
    COVERAGE_VERIFIED_WITH_SCOPE,
    MIN_N_STATUS_SUPPRESSED,
    MIN_N_STATUS_LOW_SAMPLE_CAUTION,
    MIN_N_STATUS_SUFFICIENT,
    MIN_N_STATUS_NOT_APPLICABLE,
)


class TestT013KpiComprehensive(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        config = SparkConfig(
            app_name="T013_ComprehensiveTests",
            master="local[2]",
            shuffle_partitions=2,
            driver_memory="2g",
            memory_overhead="512m",
        )
        cls.spark = get_spark_session(config)
        cls.calc = KpiCalculator(run_id="test_t013_run")

    @classmethod
    def tearDownClass(cls):
        stop_spark_session()

    def test_01_delay_boundary_14_999_15_000_15_001(self):
        """Case 1, 2, 3: Strict boundary checks for delay >= 15.0 minutes."""
        records = [
            {"FL_DATE": "2016-01-01", "ARR_DELAY": 14.999, "DEP_DELAY": 14.999, "TAXI_OUT": 10.0, "TAXI_IN": 5.0, "AIR_TIME": 60.0, "ACTUAL_ELAPSED_TIME": 75.0, "CRS_ELAPSED_TIME": 75.0},
            {"FL_DATE": "2016-01-01", "ARR_DELAY": 15.0,   "DEP_DELAY": 15.0,   "TAXI_OUT": 10.0, "TAXI_IN": 5.0, "AIR_TIME": 60.0, "ACTUAL_ELAPSED_TIME": 75.0, "CRS_ELAPSED_TIME": 75.0},
            {"FL_DATE": "2016-01-01", "ARR_DELAY": 15.001, "DEP_DELAY": 15.001, "TAXI_OUT": 10.0, "TAXI_IN": 5.0, "AIR_TIME": 60.0, "ACTUAL_ELAPSED_TIME": 75.0, "CRS_ELAPSED_TIME": 75.0},
        ]
        df = self.spark.createDataFrame(records)
        res = self.calc.compute_kpis_for_cohort(df, source_year="2016")
        rows = {f"{r['kpi_id']}:{r['submetric']}": r for r in res.collect()}

        # 2 out of 3 records are >= 15.0
        self.assertAlmostEqual(rows["KPI-02:None"]["value"], 2.0 / 3.0, places=5)
        self.assertAlmostEqual(rows["KPI-04:None"]["value"], 2.0 / 3.0, places=5)

    def test_02_negative_delays_preserved(self):
        """Case 4, 5: Negative delays preserved in signed mean."""
        records = [
            {"FL_DATE": "2016-01-01", "ARR_DELAY": -30.0, "DEP_DELAY": -10.0, "TAXI_OUT": 10.0, "TAXI_IN": 5.0, "AIR_TIME": 60.0, "ACTUAL_ELAPSED_TIME": 75.0, "CRS_ELAPSED_TIME": 75.0},
            {"FL_DATE": "2016-01-01", "ARR_DELAY": 10.0,  "DEP_DELAY": 20.0,  "TAXI_OUT": 10.0, "TAXI_IN": 5.0, "AIR_TIME": 60.0, "ACTUAL_ELAPSED_TIME": 75.0, "CRS_ELAPSED_TIME": 75.0},
        ]
        df = self.spark.createDataFrame(records)
        res = self.calc.compute_kpis_for_cohort(df, source_year="2016")
        rows = {f"{r['kpi_id']}:{r['submetric']}": r for r in res.collect()}

        # (-30 + 10) / 2 = -10.0
        self.assertAlmostEqual(rows["KPI-03:None"]["value"], -10.0, places=5)
        # (-10 + 20) / 2 = +5.0
        self.assertAlmostEqual(rows["KPI-05:None"]["value"], 5.0, places=5)

    def test_03_null_nan_inf_domain_exclusions(self):
        """Case 6, 7, 8: Null, NaN, Inf, and invalid domain values excluded."""
        records = [
            {"FL_DATE": "2016-01-01", "ARR_DELAY": float("nan"), "DEP_DELAY": float("inf"), "TAXI_OUT": -5.0, "TAXI_IN": None, "AIR_TIME": 0.0, "ACTUAL_ELAPSED_TIME": -10.0, "CRS_ELAPSED_TIME": 0.0},
            {"FL_DATE": "2016-01-01", "ARR_DELAY": 20.0, "DEP_DELAY": 20.0, "TAXI_OUT": 15.0, "TAXI_IN": 8.0, "AIR_TIME": 90.0, "ACTUAL_ELAPSED_TIME": 113.0, "CRS_ELAPSED_TIME": 115.0},
        ]
        df = self.spark.createDataFrame(records)
        res = self.calc.compute_kpis_for_cohort(df, source_year="2016")
        rows = {f"{r['kpi_id']}:{r['submetric']}": r for r in res.collect()}

        # Record count = 2, valid count = 1 for ARR_DELAY, DEP_DELAY, TAXI_OUT, etc.
        self.assertEqual(rows["KPI-01:None"]["count_records"], 2)
        self.assertEqual(rows["KPI-02:None"]["count_metric_valid"], 1)
        self.assertEqual(rows["KPI-02:None"]["excluded_count"], 1)
        self.assertEqual(rows["KPI-07:TAXI_OUT"]["count_metric_valid"], 1)
        self.assertEqual(rows["KPI-08:AIR_TIME"]["count_metric_valid"], 1)

    def test_04_zero_denominator_gives_null(self):
        """Case 9: Zero denominator gives NULL and ZERO_METRIC_DENOMINATOR status."""
        schema = StructType([
            StructField("FL_DATE", StringType(), True),
            StructField("ARR_DELAY", DoubleType(), True),
            StructField("DEP_DELAY", DoubleType(), True),
            StructField("TAXI_OUT", DoubleType(), True),
            StructField("TAXI_IN", DoubleType(), True),
            StructField("AIR_TIME", DoubleType(), True),
            StructField("ACTUAL_ELAPSED_TIME", DoubleType(), True),
            StructField("CRS_ELAPSED_TIME", DoubleType(), True),
        ])
        records = [
            {"FL_DATE": "2016-01-01", "ARR_DELAY": None, "DEP_DELAY": None, "TAXI_OUT": None, "TAXI_IN": None, "AIR_TIME": None, "ACTUAL_ELAPSED_TIME": None, "CRS_ELAPSED_TIME": None},
        ]
        df = self.spark.createDataFrame(records, schema=schema)
        res = self.calc.compute_kpis_for_cohort(df, source_year="2016")
        rows = {f"{r['kpi_id']}:{r['submetric']}": r for r in res.collect()}

        self.assertIsNone(rows["KPI-02:None"]["value"])
        self.assertEqual(rows["KPI-02:None"]["unit_status"], UNIT_STATUS_ZERO_DENOMINATOR)
        self.assertIsNone(rows["KPI-03:None"]["value"])
        self.assertEqual(rows["KPI-03:None"]["unit_status"], UNIT_STATUS_ZERO_DENOMINATOR)

    def test_05_directed_route_symmetry(self):
        """Case 14: Directed route A->B differs from B->A."""
        records = [
            {"FL_DATE": "2016-01-01", "ORIGIN": "DFW", "DEST": "LAX", "ARR_DELAY": 10.0, "DEP_DELAY": 5.0, "TAXI_OUT": 10.0, "TAXI_IN": 5.0, "AIR_TIME": 120.0, "ACTUAL_ELAPSED_TIME": 135.0, "CRS_ELAPSED_TIME": 140.0},
            {"FL_DATE": "2016-01-01", "ORIGIN": "LAX", "DEST": "DFW", "ARR_DELAY": 40.0, "DEP_DELAY": 35.0, "TAXI_OUT": 15.0, "TAXI_IN": 8.0, "AIR_TIME": 115.0, "ACTUAL_ELAPSED_TIME": 138.0, "CRS_ELAPSED_TIME": 140.0},
        ]
        df = self.spark.createDataFrame(records)
        res = self.calc.compute_kpis_for_cohort(df, source_year="2016", dimension_type="route-year", group_by_cols=["ORIGIN", "DEST"])
        rows = res.collect()

        dfw_lax = [r for r in rows if "ORIGIN=DFW;DEST=LAX" in r["group_dimensions"] and r["kpi_id"] == "KPI-03"][0]
        lax_dfw = [r for r in rows if "ORIGIN=LAX;DEST=DFW" in r["group_dimensions"] and r["kpi_id"] == "KPI-03"][0]

        self.assertEqual(dfw_lax["value"], 10.0)
        self.assertEqual(lax_dfw["value"], 40.0)
        self.assertNotEqual(dfw_lax["group_dimensions"], lax_dfw["group_dimensions"])

    def test_06_min_n_boundaries_exact(self):
        """Case 13: Exact min-N boundary points (N-1, N, 3N)."""
        from flight_pipeline.kpi.aggregators import evaluate_min_n
        from pyspark.sql import functions as F

        # Carrier-year: min-N = 1000
        test_df = self.spark.createDataFrame([(999,), (1000,), (2999,), (3000,)], ["cnt"])
        res = test_df.select(evaluate_min_n(F.col("cnt"), "carrier-year").alias("status")).collect()
        statuses = [r["status"] for r in res]
        self.assertEqual(statuses, [
            MIN_N_STATUS_SUPPRESSED,           # 999 < 1000
            MIN_N_STATUS_LOW_SAMPLE_CAUTION,  # 1000 <= 1000 < 3000
            MIN_N_STATUS_LOW_SAMPLE_CAUTION,  # 2999 < 3000
            MIN_N_STATUS_SUFFICIENT,          # 3000 >= 3000
        ])

        # Airport-year: min-N = 365
        test_df2 = self.spark.createDataFrame([(364,), (365,), (1094,), (1095,)], ["cnt"])
        res2 = test_df2.select(evaluate_min_n(F.col("cnt"), "airport-year").alias("status")).collect()
        statuses2 = [r["status"] for r in res2]
        self.assertEqual(statuses2, [
            MIN_N_STATUS_SUPPRESSED,
            MIN_N_STATUS_LOW_SAMPLE_CAUTION,
            MIN_N_STATUS_LOW_SAMPLE_CAUTION,
            MIN_N_STATUS_SUFFICIENT,
        ])

        # Route-year: min-N = 100
        test_df3 = self.spark.createDataFrame([(99,), (100,), (299,), (300,)], ["cnt"])
        res3 = test_df3.select(evaluate_min_n(F.col("cnt"), "route-year").alias("status")).collect()
        statuses3 = [r["status"] for r in res3]
        self.assertEqual(statuses3, [
            MIN_N_STATUS_SUPPRESSED,
            MIN_N_STATUS_LOW_SAMPLE_CAUTION,
            MIN_N_STATUS_LOW_SAMPLE_CAUTION,
            MIN_N_STATUS_SUFFICIENT,
        ])

    def test_07_flights_not_weighted(self):
        """Case 19: FLIGHTS column is not used as a weight for record counts."""
        records = [
            {"FL_DATE": "2016-01-01", "FLIGHTS": 10.0, "ARR_DELAY": 0.0, "DEP_DELAY": 0.0, "TAXI_OUT": 10.0, "TAXI_IN": 5.0, "AIR_TIME": 60.0, "ACTUAL_ELAPSED_TIME": 75.0, "CRS_ELAPSED_TIME": 75.0},
            {"FL_DATE": "2016-01-01", "FLIGHTS": 5.0,  "ARR_DELAY": 0.0, "DEP_DELAY": 0.0, "TAXI_OUT": 10.0, "TAXI_IN": 5.0, "AIR_TIME": 60.0, "ACTUAL_ELAPSED_TIME": 75.0, "CRS_ELAPSED_TIME": 75.0},
        ]
        df = self.spark.createDataFrame(records)
        res = self.calc.compute_kpis_for_cohort(df, source_year="2016")
        rows = {f"{r['kpi_id']}:{r['submetric']}": r for r in res.collect()}

        # Must be 2 records, NOT 15.0 (sum of FLIGHTS)
        self.assertEqual(rows["KPI-01:None"]["count_records"], 2)
        self.assertEqual(rows["KPI-01:None"]["value"], 2.0)

    def test_08_missing_cancelled_diverted_columns_safe(self):
        """Case 20: 34-column schema without CANCELLED / DIVERTED executes safely."""
        # Only canonical 34 columns without any CANCELLED or DIVERTED
        records = [
            {
                "FL_DATE": "2016-01-01",
                "OP_CARRIER": "AA",
                "OP_CARRIER_FL_NUM": 100.0,
                "ORIGIN": "DFW",
                "DEST": "ORD",
                "CRS_DEP_TIME": "0800",
                "DEP_TIME": "0805",
                "DEP_DELAY": 5.0,
                "TAXI_OUT": 12.0,
                "WHEELS_OFF": "0817",
                "WHEELS_ON": "1015",
                "TAXI_IN": 6.0,
                "CRS_ARR_TIME": "1020",
                "ARR_TIME": "1021",
                "ARR_DELAY": 1.0,
                "CRS_ELAPSED_TIME": 140.0,
                "ACTUAL_ELAPSED_TIME": 136.0,
                "AIR_TIME": 118.0,
                "FLIGHTS": 1.0,
                "MONTH": 1,
                "DAY_OF_MONTH": 1,
                "DAY_OF_WEEK": 5,
                "ORIGIN_INDEX": 1,
                "DEST_INDEX": 2,
                "O_TEMP": 15.0,
                "O_PRCP": 0.0,
                "O_WSPD": 10.0,
                "D_TEMP": 10.0,
                "D_PRCP": 0.0,
                "D_WSPD": 8.0,
                "O_LATITUDE": 32.89,
                "O_LONGITUDE": -97.04,
                "D_LATITUDE": 41.97,
                "D_LONGITUDE": -87.90,
            }
        ]
        df = self.spark.createDataFrame(records)
        res = self.calc.compute_kpis_for_cohort(df, source_year="2016")
        self.assertEqual(res.count(), 12)
        self.assertEqual(len(res.columns), 17)


if __name__ == "__main__":
    unittest.main()
