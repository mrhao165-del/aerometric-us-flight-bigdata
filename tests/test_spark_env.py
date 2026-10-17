"""
Unit tests for Spark runtime environment and SparkSession bootstrap.
Conforms to ARCHITECTURE.md Section 3 and T-009 requirements.
"""

import sys
import unittest
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parents[1] / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from flight_pipeline.config.spark_config import SparkConfig, get_spark_session, stop_spark_session


class TestSparkEnv(unittest.TestCase):
    def test_spark_session_creation_and_config(self):
        """Verify SparkSession factory instantiates session with proper configuration."""
        cfg = SparkConfig(master="local[2]", driver_memory="2g", shuffle_partitions=4)
        spark = get_spark_session(cfg)
        try:
            self.assertIsNotNone(spark)
            # Verify Spark master
            self.assertEqual(spark.conf.get("spark.master"), "local[2]")
            # Verify shuffle partitions
            self.assertEqual(spark.conf.get("spark.sql.shuffle.partitions"), "4")
            # Verify basic distributed operation
            rdd = spark.sparkContext.parallelize(range(100), 4)
            self.assertEqual(rdd.sum(), 4950)
            # Verify DataFrame operation
            df = spark.createDataFrame([(1, "a"), (2, "b")], ["num", "letter"])
            self.assertEqual(df.count(), 2)
        finally:
            stop_spark_session(spark)


if __name__ == "__main__":
    unittest.main()
