"""
Unit test suite for KPI Engine (KPI-01..08) with independent Python Oracle verification.
Conforms to Master Execution Prompt T-011 Phase 1, KPI_SPEC.md, and DECISIONS.md.
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
from typing import List, Dict, Any, Optional
from pyspark.sql import SparkSession
from pyspark.sql.types import (
    StructType,
    StructField,
    StringType,
    DoubleType,
    LongType,
)

from flight_pipeline.kpi.catalog import (
    KPI_OUTPUT_COLUMNS,
    UNIT_STATUS_PROVISIONAL,
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
from flight_pipeline.config.spark_config import SparkConfig, get_spark_session, stop_spark_session
from flight_pipeline.kpi.calculator import KpiCalculator


def _is_valid_float(val: Any) -> bool:
    if val is None:
        return False
    try:
        f = float(val)
        return not (math.isnan(f) or math.isinf(f))
    except (ValueError, TypeError):
        return False


def _compute_python_oracle(records: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """
    Independent pure-Python Oracle computing expected KPI values.
    Does NOT use PySpark or shared production helper functions.
    """
    total_records = len(records)

    # Valid ARR_DELAY
    arr_delays = [float(r["ARR_DELAY"]) for r in records if _is_valid_float(r.get("ARR_DELAY"))]
    valid_arr_count = len(arr_delays)
    arr_gte_15 = [x for x in arr_delays if x >= 15.0]

    # Valid DEP_DELAY
    dep_delays = [float(r["DEP_DELAY"]) for r in records if _is_valid_float(r.get("DEP_DELAY"))]
    valid_dep_count = len(dep_delays)
    dep_gte_15 = [x for x in dep_delays if x >= 15.0]

    # Valid TAXI_OUT (>= 0.0)
    taxi_outs = [float(r["TAXI_OUT"]) for r in records if _is_valid_float(r.get("TAXI_OUT")) and float(r["TAXI_OUT"]) >= 0.0]
    valid_taxi_out_count = len(taxi_outs)

    # Valid TAXI_IN (>= 0.0)
    taxi_ins = [float(r["TAXI_IN"]) for r in records if _is_valid_float(r.get("TAXI_IN")) and float(r["TAXI_IN"]) >= 0.0]
    valid_taxi_in_count = len(taxi_ins)

    # Valid AIR_TIME (> 0.0)
    air_times = [float(r["AIR_TIME"]) for r in records if _is_valid_float(r.get("AIR_TIME")) and float(r["AIR_TIME"]) > 0.0]
    valid_air_time_count = len(air_times)

    # Valid ACTUAL_ELAPSED_TIME (> 0.0)
    act_elapseds = [float(r["ACTUAL_ELAPSED_TIME"]) for r in records if _is_valid_float(r.get("ACTUAL_ELAPSED_TIME")) and float(r["ACTUAL_ELAPSED_TIME"]) > 0.0]
    valid_act_elapsed_count = len(act_elapseds)

    # Valid CRS_ELAPSED_TIME (> 0.0)
    crs_elapseds = [float(r["CRS_ELAPSED_TIME"]) for r in records if _is_valid_float(r.get("CRS_ELAPSED_TIME")) and float(r["CRS_ELAPSED_TIME"]) > 0.0]
    valid_crs_elapsed_count = len(crs_elapseds)

    oracle: Dict[str, Dict[str, Any]] = {}

    # KPI-01
    oracle["KPI-01:None"] = {
        "count_records": total_records,
        "count_metric_valid": total_records,
        "excluded_count": 0,
        "value": float(total_records),
        "unit_status": UNIT_STATUS_COUNT_RECORDS,
    }

    # KPI-02
    oracle["KPI-02:None"] = {
        "count_records": total_records,
        "count_metric_valid": valid_arr_count,
        "excluded_count": total_records - valid_arr_count,
        "value": (len(arr_gte_15) / valid_arr_count) if valid_arr_count > 0 else None,
        "unit_status": UNIT_STATUS_ZERO_DENOMINATOR if valid_arr_count == 0 else UNIT_STATUS_RESOLVED,
    }

    # KPI-03
    oracle["KPI-03:None"] = {
        "count_records": total_records,
        "count_metric_valid": valid_arr_count,
        "excluded_count": total_records - valid_arr_count,
        "value": (sum(arr_delays) / valid_arr_count) if valid_arr_count > 0 else None,
        "unit_status": UNIT_STATUS_ZERO_DENOMINATOR if valid_arr_count == 0 else UNIT_STATUS_RESOLVED,
    }

    # KPI-04
    oracle["KPI-04:None"] = {
        "count_records": total_records,
        "count_metric_valid": valid_dep_count,
        "excluded_count": total_records - valid_dep_count,
        "value": (len(dep_gte_15) / valid_dep_count) if valid_dep_count > 0 else None,
        "unit_status": UNIT_STATUS_ZERO_DENOMINATOR if valid_dep_count == 0 else UNIT_STATUS_RESOLVED,
    }

    # KPI-05
    oracle["KPI-05:None"] = {
        "count_records": total_records,
        "count_metric_valid": valid_dep_count,
        "excluded_count": total_records - valid_dep_count,
        "value": (sum(dep_delays) / valid_dep_count) if valid_dep_count > 0 else None,
        "unit_status": UNIT_STATUS_ZERO_DENOMINATOR if valid_dep_count == 0 else UNIT_STATUS_RESOLVED,
    }

    # KPI-06 P50 / P90
    oracle["KPI-06:P50"] = {
        "count_records": total_records,
        "count_metric_valid": valid_arr_count,
        "excluded_count": total_records - valid_arr_count,
        "unit_status": UNIT_STATUS_ZERO_DENOMINATOR if valid_arr_count == 0 else UNIT_STATUS_RESOLVED,
    }
    oracle["KPI-06:P90"] = {
        "count_records": total_records,
        "count_metric_valid": valid_arr_count,
        "excluded_count": total_records - valid_arr_count,
        "unit_status": UNIT_STATUS_ZERO_DENOMINATOR if valid_arr_count == 0 else UNIT_STATUS_RESOLVED,
    }

    # KPI-07
    oracle["KPI-07:TAXI_OUT"] = {
        "count_records": total_records,
        "count_metric_valid": valid_taxi_out_count,
        "excluded_count": total_records - valid_taxi_out_count,
        "value": (sum(taxi_outs) / valid_taxi_out_count) if valid_taxi_out_count > 0 else None,
        "unit_status": UNIT_STATUS_ZERO_DENOMINATOR if valid_taxi_out_count == 0 else UNIT_STATUS_RESOLVED,
    }
    oracle["KPI-07:TAXI_IN"] = {
        "count_records": total_records,
        "count_metric_valid": valid_taxi_in_count,
        "excluded_count": total_records - valid_taxi_in_count,
        "value": (sum(taxi_ins) / valid_taxi_in_count) if valid_taxi_in_count > 0 else None,
        "unit_status": UNIT_STATUS_ZERO_DENOMINATOR if valid_taxi_in_count == 0 else UNIT_STATUS_RESOLVED,
    }

    # KPI-08
    oracle["KPI-08:AIR_TIME"] = {
        "count_records": total_records,
        "count_metric_valid": valid_air_time_count,
        "excluded_count": total_records - valid_air_time_count,
        "value": (sum(air_times) / valid_air_time_count) if valid_air_time_count > 0 else None,
        "unit_status": UNIT_STATUS_ZERO_DENOMINATOR if valid_air_time_count == 0 else UNIT_STATUS_RESOLVED,
    }
    oracle["KPI-08:ACTUAL_ELAPSED_TIME"] = {
        "count_records": total_records,
        "count_metric_valid": valid_act_elapsed_count,
        "excluded_count": total_records - valid_act_elapsed_count,
        "value": (sum(act_elapseds) / valid_act_elapsed_count) if valid_act_elapsed_count > 0 else None,
        "unit_status": UNIT_STATUS_ZERO_DENOMINATOR if valid_act_elapsed_count == 0 else UNIT_STATUS_RESOLVED,
    }
    oracle["KPI-08:CRS_ELAPSED_TIME"] = {
        "count_records": total_records,
        "count_metric_valid": valid_crs_elapsed_count,
        "excluded_count": total_records - valid_crs_elapsed_count,
        "value": (sum(crs_elapseds) / valid_crs_elapsed_count) if valid_crs_elapsed_count > 0 else None,
        "unit_status": UNIT_STATUS_ZERO_DENOMINATOR if valid_crs_elapsed_count == 0 else UNIT_STATUS_RESOLVED,
    }

    return oracle


class TestKpiEngine(unittest.TestCase):
    """Test suite validating KpiCalculator against independent Oracle and contract invariants."""

    @classmethod
    def setUpClass(cls):
        config = SparkConfig(
            app_name="TestKpiEngine",
            master="local[2]",
            shuffle_partitions=2,
            driver_memory="2g",
            memory_overhead="512m",
        )
        cls.spark = get_spark_session(config)
        cls.calc = KpiCalculator(run_id="test_run_t011")

    @classmethod
    def tearDownClass(cls):
        stop_spark_session()

    def _create_df(self, records: List[Dict[str, Any]]):
        """Helper to create a Spark DataFrame from dictionary records with explicit schema."""
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
            StructField("O_TEMP", DoubleType(), True),
            StructField("D_TEMP", DoubleType(), True),
        ])
        return self.spark.createDataFrame(records, schema=schema)

    def test_01_synthetic_oracle_parity_clean_data(self):
        """Test KPI-01..08 values against Python Oracle on clean synthetic data with signed delays."""
        records = [
            # Record 1: Early arrival (-12.0), early departure (-5.0), taxi/air times positive
            {
                "FL_DATE": "2016-01-01", "OP_CARRIER": "AA", "OP_CARRIER_FL_NUM": 101.0,
                "ORIGIN": "JFK", "DEST": "LAX", "ARR_DELAY": -12.0, "DEP_DELAY": -5.0,
                "TAXI_OUT": 20.0, "TAXI_IN": 8.0, "AIR_TIME": 330.0,
                "ACTUAL_ELAPSED_TIME": 358.0, "CRS_ELAPSED_TIME": 365.0,
                "O_TEMP": 5.0, "D_TEMP": 18.0,
            },
            # Record 2: Exactly 15.0 arrival delay (boundary case), on-time dep (0.0)
            {
                "FL_DATE": "2016-01-01", "OP_CARRIER": "AA", "OP_CARRIER_FL_NUM": 102.0,
                "ORIGIN": "JFK", "DEST": "LAX", "ARR_DELAY": 15.0, "DEP_DELAY": 0.0,
                "TAXI_OUT": 25.0, "TAXI_IN": 10.0, "AIR_TIME": 340.0,
                "ACTUAL_ELAPSED_TIME": 375.0, "CRS_ELAPSED_TIME": 360.0,
                "O_TEMP": 4.0, "D_TEMP": 17.0,
            },
            # Record 3: Heavy delay (+120.0 arr, +110.0 dep)
            {
                "FL_DATE": "2016-01-01", "OP_CARRIER": "DL", "OP_CARRIER_FL_NUM": 201.0,
                "ORIGIN": "ATL", "DEST": "ORD", "ARR_DELAY": 120.0, "DEP_DELAY": 110.0,
                "TAXI_OUT": 18.0, "TAXI_IN": 7.0, "AIR_TIME": 105.0,
                "ACTUAL_ELAPSED_TIME": 130.0, "CRS_ELAPSED_TIME": 120.0,
                "O_TEMP": None, "D_TEMP": None,  # Weather nulls should not affect CORE
            },
            # Record 4: Delay directly below 15 (14.9 arr), late dep (+15.0 boundary)
            {
                "FL_DATE": "2016-01-01", "OP_CARRIER": "DL", "OP_CARRIER_FL_NUM": 202.0,
                "ORIGIN": "ATL", "DEST": "ORD", "ARR_DELAY": 14.9, "DEP_DELAY": 15.0,
                "TAXI_OUT": 15.0, "TAXI_IN": 6.0, "AIR_TIME": 110.0,
                "ACTUAL_ELAPSED_TIME": 131.0, "CRS_ELAPSED_TIME": 131.1,
                "O_TEMP": 8.0, "D_TEMP": 2.0,
            },
        ]

        df = self._create_df(records)
        oracle = _compute_python_oracle(records)

        result_df = self.calc.compute_kpis_for_cohort(
            df=df,
            source_year="2016",
            dimension_type="year",
        )

        rows = result_df.collect()
        self.assertEqual(len(rows), 12, "Must emit exactly 12 KPI rows for 8 CORE KPIs")

        # Verify columns contract
        self.assertEqual(result_df.columns, KPI_OUTPUT_COLUMNS)

        for row in rows:
            key = f"{row['kpi_id']}:{row['submetric']}"
            self.assertIn(key, oracle, f"Unexpected KPI key: {key}")
            exp = oracle[key]

            # Verify exact count invariants
            self.assertEqual(row["count_records"], exp["count_records"])
            self.assertEqual(row["count_metric_valid"], exp["count_metric_valid"])
            self.assertEqual(row["excluded_count"], exp["excluded_count"])
            self.assertEqual(row["unit_status"], exp["unit_status"])

            # Verify numerical values (except percentile approx which is tested in TS-008)
            if "value" in exp and exp["value"] is not None:
                self.assertIsNotNone(row["value"])
                self.assertAlmostEqual(row["value"], exp["value"], places=5)
            elif "value" in exp and exp["value"] is None:
                self.assertIsNone(row["value"])

    def test_02_negative_delays_preserved_in_signed_means(self):
        """FP-DEC-008: Negative delays must be preserved in signed mean, not truncated to 0."""
        records = [
            {"FL_DATE": "2016-01-01", "OP_CARRIER": "AA", "OP_CARRIER_FL_NUM": 1.0, "ORIGIN": "A", "DEST": "B",
             "ARR_DELAY": -30.0, "DEP_DELAY": -10.0, "TAXI_OUT": 10.0, "TAXI_IN": 5.0, "AIR_TIME": 50.0,
             "ACTUAL_ELAPSED_TIME": 65.0, "CRS_ELAPSED_TIME": 85.0, "O_TEMP": 1.0, "D_TEMP": 1.0},
            {"FL_DATE": "2016-01-01", "OP_CARRIER": "AA", "OP_CARRIER_FL_NUM": 2.0, "ORIGIN": "A", "DEST": "B",
             "ARR_DELAY": 10.0, "DEP_DELAY": 0.0, "TAXI_OUT": 10.0, "TAXI_IN": 5.0, "AIR_TIME": 50.0,
             "ACTUAL_ELAPSED_TIME": 65.0, "CRS_ELAPSED_TIME": 65.0, "O_TEMP": 1.0, "D_TEMP": 1.0},
        ]
        df = self._create_df(records)
        res = self.calc.compute_kpis_for_cohort(df, source_year="2016").collect()

        # Mean ARR_DELAY = (-30 + 10) / 2 = -10.0
        kpi03 = [r for r in res if r["kpi_id"] == "KPI-03"][0]
        self.assertAlmostEqual(kpi03["value"], -10.0, places=5)

        # Mean DEP_DELAY = (-10 + 0) / 2 = -5.0
        kpi05 = [r for r in res if r["kpi_id"] == "KPI-05"][0]
        self.assertAlmostEqual(kpi05["value"], -5.0, places=5)

    def test_03_exact_15_minute_boundary(self):
        """FP-DEC-008: Rate >= 15 must include exact 15.0; 14.999 is NOT >= 15.0."""
        records = [
            {"FL_DATE": "2016-01-01", "OP_CARRIER": "AA", "OP_CARRIER_FL_NUM": 1.0, "ORIGIN": "A", "DEST": "B",
             "ARR_DELAY": 14.999, "DEP_DELAY": 14.999, "TAXI_OUT": 10.0, "TAXI_IN": 5.0, "AIR_TIME": 50.0,
             "ACTUAL_ELAPSED_TIME": 65.0, "CRS_ELAPSED_TIME": 65.0, "O_TEMP": 1.0, "D_TEMP": 1.0},
            {"FL_DATE": "2016-01-01", "OP_CARRIER": "AA", "OP_CARRIER_FL_NUM": 2.0, "ORIGIN": "A", "DEST": "B",
             "ARR_DELAY": 15.000, "DEP_DELAY": 15.000, "TAXI_OUT": 10.0, "TAXI_IN": 5.0, "AIR_TIME": 50.0,
             "ACTUAL_ELAPSED_TIME": 65.0, "CRS_ELAPSED_TIME": 65.0, "O_TEMP": 1.0, "D_TEMP": 1.0},
        ]
        df = self._create_df(records)
        res = self.calc.compute_kpis_for_cohort(df, source_year="2016").collect()

        # Rate should be exactly 1 / 2 = 0.5
        kpi02 = [r for r in res if r["kpi_id"] == "KPI-02"][0]
        self.assertAlmostEqual(kpi02["value"], 0.5, places=5)
        kpi04 = [r for r in res if r["kpi_id"] == "KPI-04"][0]
        self.assertAlmostEqual(kpi04["value"], 0.5, places=5)

    def test_04_zero_metric_denominator_safety(self):
        """FP-DEC-011: When count_metric_valid == 0, value must be null and status ZERO_METRIC_DENOMINATOR."""
        records = [
            # All metrics null or invalid
            {"FL_DATE": "2016-01-01", "OP_CARRIER": "AA", "OP_CARRIER_FL_NUM": 1.0, "ORIGIN": "A", "DEST": "B",
             "ARR_DELAY": None, "DEP_DELAY": None, "TAXI_OUT": -5.0, "TAXI_IN": None, "AIR_TIME": 0.0,
             "ACTUAL_ELAPSED_TIME": None, "CRS_ELAPSED_TIME": -10.0, "O_TEMP": 1.0, "D_TEMP": 1.0},
        ]
        df = self._create_df(records)
        res = self.calc.compute_kpis_for_cohort(df, source_year="2016").collect()

        # KPI-01 count_records is 1
        kpi01 = [r for r in res if r["kpi_id"] == "KPI-01"][0]
        self.assertEqual(kpi01["value"], 1.0)
        self.assertEqual(kpi01["unit_status"], UNIT_STATUS_COUNT_RECORDS)

        # Other KPIs must have value = None, count_metric_valid = 0, unit_status = ZERO_METRIC_DENOMINATOR
        for row in res:
            if row["kpi_id"] != "KPI-01":
                self.assertIsNone(row["value"], f"{row['kpi_id']} value must be None")
                self.assertEqual(row["count_metric_valid"], 0)
                self.assertEqual(row["excluded_count"], 1)
                self.assertEqual(row["unit_status"], UNIT_STATUS_ZERO_DENOMINATOR)

    def test_05_independent_denominators_kpi07_and_kpi08(self):
        """DC-12: Submetrics of KPI-07 and KPI-08 must use independent valid denominators."""
        records = [
            # Flight 1: TAXI_OUT valid, TAXI_IN null, AIR_TIME valid, ACTUAL_ELAPSED null
            {"FL_DATE": "2016-01-01", "OP_CARRIER": "AA", "OP_CARRIER_FL_NUM": 1.0, "ORIGIN": "A", "DEST": "B",
             "ARR_DELAY": 0.0, "DEP_DELAY": 0.0, "TAXI_OUT": 20.0, "TAXI_IN": None, "AIR_TIME": 100.0,
             "ACTUAL_ELAPSED_TIME": None, "CRS_ELAPSED_TIME": 130.0, "O_TEMP": 1.0, "D_TEMP": 1.0},
            # Flight 2: TAXI_OUT null, TAXI_IN valid, AIR_TIME null, ACTUAL_ELAPSED valid
            {"FL_DATE": "2016-01-01", "OP_CARRIER": "AA", "OP_CARRIER_FL_NUM": 2.0, "ORIGIN": "A", "DEST": "B",
             "ARR_DELAY": 0.0, "DEP_DELAY": 0.0, "TAXI_OUT": None, "TAXI_IN": 10.0, "AIR_TIME": None,
             "ACTUAL_ELAPSED_TIME": 135.0, "CRS_ELAPSED_TIME": 130.0, "O_TEMP": 1.0, "D_TEMP": 1.0},
        ]
        df = self._create_df(records)
        res = self.calc.compute_kpis_for_cohort(df, source_year="2016").collect()

        # TAXI_OUT: valid=1, mean=20.0
        taxi_out = [r for r in res if r["kpi_id"] == "KPI-07" and r["submetric"] == "TAXI_OUT"][0]
        self.assertEqual(taxi_out["count_metric_valid"], 1)
        self.assertAlmostEqual(taxi_out["value"], 20.0, places=5)

        # TAXI_IN: valid=1, mean=10.0
        taxi_in = [r for r in res if r["kpi_id"] == "KPI-07" and r["submetric"] == "TAXI_IN"][0]
        self.assertEqual(taxi_in["count_metric_valid"], 1)
        self.assertAlmostEqual(taxi_in["value"], 10.0, places=5)

        # AIR_TIME: valid=1, mean=100.0
        air_time = [r for r in res if r["kpi_id"] == "KPI-08" and r["submetric"] == "AIR_TIME"][0]
        self.assertEqual(air_time["count_metric_valid"], 1)
        self.assertAlmostEqual(air_time["value"], 100.0, places=5)

        # ACTUAL_ELAPSED_TIME: valid=1, mean=135.0
        act_elapsed = [r for r in res if r["kpi_id"] == "KPI-08" and r["submetric"] == "ACTUAL_ELAPSED_TIME"][0]
        self.assertEqual(act_elapsed["count_metric_valid"], 1)
        self.assertAlmostEqual(act_elapsed["value"], 135.0, places=5)

        # CRS_ELAPSED_TIME: valid=2, mean=130.0
        crs_elapsed = [r for r in res if r["kpi_id"] == "KPI-08" and r["submetric"] == "CRS_ELAPSED_TIME"][0]
        self.assertEqual(crs_elapsed["count_metric_valid"], 2)
        self.assertAlmostEqual(crs_elapsed["value"], 130.0, places=5)

    def test_06_min_n_threshold_boundaries(self):
        """FP-DEC-016: Test exact min-N boundary conditions on carrier-year, airport-year, route-year, and aliases."""
        from pyspark.sql import functions as F
        from flight_pipeline.kpi.aggregators import evaluate_min_n

        test_cases = [
            # Carrier-year (1000 / 3000)
            (999, "carrier-year", MIN_N_STATUS_SUPPRESSED),
            (1000, "carrier-year", MIN_N_STATUS_LOW_SAMPLE_CAUTION),
            (2999, "carrier-year", MIN_N_STATUS_LOW_SAMPLE_CAUTION),
            (3000, "carrier-year", MIN_N_STATUS_SUFFICIENT),
            # Airport-year (365 / 1095)
            (364, "airport-year", MIN_N_STATUS_SUPPRESSED),
            (365, "airport-year", MIN_N_STATUS_LOW_SAMPLE_CAUTION),
            (1094, "airport-year", MIN_N_STATUS_LOW_SAMPLE_CAUTION),
            (1095, "airport-year", MIN_N_STATUS_SUFFICIENT),
            # Airport aliases
            (364, "destination-year", MIN_N_STATUS_SUPPRESSED),
            (365, "destination-year", MIN_N_STATUS_LOW_SAMPLE_CAUTION),
            (1095, "origin-year", MIN_N_STATUS_SUFFICIENT),
            (1095, "dest_year", MIN_N_STATUS_SUFFICIENT),
            # Route-year (100 / 300)
            (99, "route-year", MIN_N_STATUS_SUPPRESSED),
            (100, "route-year", MIN_N_STATUS_LOW_SAMPLE_CAUTION),
            (299, "route-year", MIN_N_STATUS_LOW_SAMPLE_CAUTION),
            (300, "route-year", MIN_N_STATUS_SUFFICIENT),
            (300, "pair_year", MIN_N_STATUS_SUFFICIENT),
            # Null count handling
            (None, "carrier-year", MIN_N_STATUS_SUPPRESSED),
            (None, "airport-year", MIN_N_STATUS_SUPPRESSED),
            (None, "route-year", MIN_N_STATUS_SUPPRESSED),
            # Other dimensions
            (500, "year", MIN_N_STATUS_NOT_APPLICABLE),
        ]

        for cnt, dim, expected in test_cases:
            df = self.spark.createDataFrame([(cnt,)], "cnt: long")
            status = df.select(evaluate_min_n(F.col("cnt"), dim).alias("status")).collect()[0]["status"]
            self.assertEqual(status, expected, f"Failed for cnt={cnt}, dim={dim}: expected {expected}, got {status}")

    def test_07_year_2024_partial_coverage_metadata(self):
        """OR-05: Year 2024 must emit source_coverage_status = PARTIAL even if caller attempts override."""
        records = [
            {"FL_DATE": "2024-01-01", "OP_CARRIER": "AA", "OP_CARRIER_FL_NUM": 1.0, "ORIGIN": "A", "DEST": "B",
             "ARR_DELAY": 0.0, "DEP_DELAY": 0.0, "TAXI_OUT": 10.0, "TAXI_IN": 5.0, "AIR_TIME": 50.0,
             "ACTUAL_ELAPSED_TIME": 65.0, "CRS_ELAPSED_TIME": 65.0, "O_TEMP": 1.0, "D_TEMP": 1.0},
        ]
        df = self._create_df(records)
        # Attempt to pass VERIFIED_WITH_SCOPE for 2024
        res = self.calc.compute_kpis_for_cohort(
            df,
            source_year="2024",
            source_coverage_status=COVERAGE_VERIFIED_WITH_SCOPE,
        ).collect()

        for row in res:
            self.assertEqual(row["source_coverage_status"], COVERAGE_PARTIAL)
            self.assertEqual(row["source_year"], "2024")

    def test_08_empty_cohort_kpi_computation(self):
        """R1-F04: Empty cohort DataFrame must compute non-null counts (0) and ZERO_METRIC_DENOMINATOR unit status."""
        empty_df = self._create_df([])
        res = self.calc.compute_kpis_for_cohort(empty_df, source_year="2016").collect()
        self.assertEqual(len(res), 12)

        for row in res:
            self.assertEqual(row["count_records"], 0)
            self.assertEqual(row["count_metric_valid"], 0)
            self.assertEqual(row["excluded_count"], 0)
            self.assertIsNone(row["metric_valid_rate"])
            self.assertEqual(row["min_n_status"], MIN_N_STATUS_NOT_APPLICABLE)

            if row["kpi_id"] == "KPI-01":
                self.assertEqual(row["unit_status"], UNIT_STATUS_COUNT_RECORDS)
                self.assertEqual(row["value"], 0.0)
            else:
                self.assertEqual(row["unit_status"], UNIT_STATUS_ZERO_DENOMINATOR)
                self.assertIsNone(row["value"])

    def test_09_cohort_fl_date_year_validation(self):
        """R1-F06: Cohort FL_DATE must strictly match source_year, rejecting mismatches."""
        records = [
            {"FL_DATE": "2017-05-15", "OP_CARRIER": "AA", "OP_CARRIER_FL_NUM": 1.0, "ORIGIN": "A", "DEST": "B",
             "ARR_DELAY": 0.0, "DEP_DELAY": 0.0, "TAXI_OUT": 10.0, "TAXI_IN": 5.0, "AIR_TIME": 50.0,
             "ACTUAL_ELAPSED_TIME": 65.0, "CRS_ELAPSED_TIME": 65.0},
        ]
        df = self._create_df(records)
        with self.assertRaises(ValueError) as ctx:
            self.calc.compute_kpis_for_cohort(df, source_year="2016")
        self.assertIn("Cohort integrity violation", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
