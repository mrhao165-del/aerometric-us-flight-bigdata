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
            # Verify scratch directory configuration is passed to SparkSession (CI-01 requirement 9)
            spark_local_dir = spark.conf.get("spark.local.dir")
            self.assertIsNotNone(spark_local_dir)
            self.assertTrue(Path(spark_local_dir).is_absolute())
            # Verify basic distributed operation
            rdd = spark.sparkContext.parallelize(range(100), 4)
            self.assertEqual(rdd.sum(), 4950)
            # Verify DataFrame operation
            df = spark.createDataFrame([(1, "a"), (2, "b")], ["num", "letter"])
            self.assertEqual(df.count(), 2)
        finally:
            stop_spark_session(spark)

    def test_spark_scratch_dir_posix_compliance(self):
        """CI-01: On POSIX environments, scratch directory must be absolute, outside checkout, and never create 'D:'."""
        from flight_pipeline.config.spark_config import ensure_scratch_dir, SparkConfig
        import tempfile
        import os
        from unittest.mock import patch

        temp_dir = os.path.normpath(tempfile.gettempdir())

        # 1. Test ensure_scratch_dir with Windows-like path on simulated POSIX
        with patch("flight_pipeline.config.spark_config.is_windows_host", return_value=False):
            res_path = ensure_scratch_dir("D:/Study/Code/Apache/Flight_Analyzt/tmp_spark/")
            # Must be an absolute path
            self.assertTrue(os.path.isabs(res_path), f"Path {res_path} is not absolute")
            # Must not contain or create a relative 'D:' folder in current directory
            self.assertNotIn("D:", os.listdir("."), "A relative 'D:' folder was created in the current working directory!")
            # Must reside in OS temp directory
            self.assertTrue(res_path.startswith(temp_dir), f"Expected {res_path} to start with {temp_dir}")

            # 2. Test relative path redirection on POSIX
            res_rel = ensure_scratch_dir("in_repo_scratch")
            self.assertTrue(os.path.isabs(res_rel))
            self.assertNotIn("in_repo_scratch", os.listdir("."), "Relative scratch folder was created in repo!")
            self.assertTrue(res_rel.startswith(temp_dir))

            # 3. Test default config on POSIX
            cfg = SparkConfig()
            self.assertTrue(os.path.isabs(cfg.scratch_dir), f"Default config on POSIX must be absolute: {cfg.scratch_dir}")
            self.assertFalse(cfg.scratch_dir.startswith("D:"), f"Default config on POSIX must not start with 'D:': {cfg.scratch_dir}")
            self.assertTrue(cfg.scratch_dir.startswith(temp_dir))

    def test_spark_scratch_dir_windows_compliance(self):
        """CI-01: On Windows environments, approved D: drive path is preserved."""
        from flight_pipeline.config.spark_config import ensure_scratch_dir, SparkConfig
        import os
        from unittest.mock import patch

        windows_approved_scratch_path = "D:/Study/Code/Apache/Flight_Analyzt/tmp_spark/"

        # 1. Pure configuration assertion: Verify default scratch_dir on Windows host
        with patch("flight_pipeline.config.spark_config.is_windows_host", return_value=True):
            cfg = SparkConfig()
            self.assertEqual(cfg.scratch_dir, windows_approved_scratch_path)

        # 2. Filesystem integration test: ONLY execute on actual Windows host (os.name == 'nt')
        # Running Windows drive path mkdir on POSIX hosts treats 'D:' as a relative folder,
        # polluting the repository checkout and failing cross-platform assertions.
        if os.name == "nt":
            res = ensure_scratch_dir(windows_approved_scratch_path)
            self.assertEqual(os.path.normpath(res), os.path.normpath(windows_approved_scratch_path))
            self.assertTrue(os.path.isabs(res))

    def test_spark_scratch_dir_fallback_never_uses_repo(self):
        """CI-01: If scratch path creation fails, fallback uses OS temp directory and NEVER '.' or workspace."""
        from flight_pipeline.config.spark_config import ensure_scratch_dir
        import tempfile
        import os
        from unittest.mock import patch

        temp_dir = os.path.normpath(tempfile.gettempdir())

        with patch("pathlib.Path.mkdir", side_effect=OSError("Simulated read-only disk")):
            fallback_res = ensure_scratch_dir("unusable_path")
            self.assertTrue(os.path.isabs(fallback_res))
            self.assertTrue(fallback_res.startswith(temp_dir))
            self.assertNotIn("flight_spark_tmp", os.listdir("."), "Fallback created folder in repository root!")


if __name__ == "__main__":
    unittest.main()


