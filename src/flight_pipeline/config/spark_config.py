"""
Spark configuration and SparkSession factory for US Flight Performance Analysis.
Enforces deterministic runtime parameters, memory budgeting, and safe temporary storage.
"""

from dataclasses import dataclass
import os
from pathlib import Path
import sys
from typing import Optional

from pyspark.sql import SparkSession


@dataclass
class SparkConfig:
    """SparkSession configuration parameters conforming to ARCHITECTURE.md specifications."""
    app_name: str = "US_Flight_Performance_Analysis"
    master: str = "local[4]"
    driver_memory: str = "4g"
    memory_overhead: str = "1g"
    shuffle_partitions: int = 16
    scratch_dir: str = "D:/Study/Code/Apache/Flight_Analyzt/tmp_spark/"
    parquet_compression: str = "snappy"
    timezone: str = "UTC"


def setup_pyspark_env() -> None:
    """Set in-process environment variables so Spark workers and driver use the current Python interpreter."""
    current_python = sys.executable
    os.environ["PYSPARK_PYTHON"] = current_python
    os.environ["PYSPARK_DRIVER_PYTHON"] = current_python


def ensure_scratch_dir(path_str: str) -> str:
    """Ensure scratch directory exists and is writable on drive D, falling back safely if needed."""
    scratch = Path(path_str)
    try:
        scratch.mkdir(parents=True, exist_ok=True)
        # Test writability
        test_file = scratch / ".write_test"
        test_file.write_text("ok", encoding="utf-8")
        test_file.unlink()
        return str(scratch.resolve().as_posix())
    except Exception:
        # Fallback to local user temp directory if path is not writable
        fallback = Path(os.environ.get("TEMP", ".")) / "flight_spark_tmp"
        fallback.mkdir(parents=True, exist_ok=True)
        return str(fallback.resolve().as_posix())


def get_spark_session(config: Optional[SparkConfig] = None) -> SparkSession:
    """
    Create or retrieve a SparkSession configured per project architecture standards.
    Configures memory budget, scratch directory, and deterministic serialization.
    """
    if config is None:
        config = SparkConfig()

    setup_pyspark_env()
    scratch_path = ensure_scratch_dir(config.scratch_dir)

    builder = (
        SparkSession.builder.appName(config.app_name)
        .master(config.master)
        .config("spark.driver.memory", config.driver_memory)
        .config("spark.driver.memoryOverhead", config.memory_overhead)
        .config("spark.sql.shuffle.partitions", str(config.shuffle_partitions))
        .config("spark.local.dir", scratch_path)
        .config("spark.sql.parquet.compression.codec", config.parquet_compression)
        .config("spark.sql.session.timeZone", config.timezone)
        .config("spark.ui.enabled", "false")
        .config("spark.sql.execution.arrow.pyspark.enabled", "true")
    )

    spark = builder.getOrCreate()
    # Set log level to WARN to reduce console clutter
    spark.sparkContext.setLogLevel("WARN")
    return spark


def stop_spark_session(spark: Optional[SparkSession] = None) -> None:
    """Safely stop an active SparkSession."""
    if spark is not None:
        spark.stop()
    else:
        active = SparkSession.getActiveSession()
        if active is not None:
            active.stop()
