"""
Spark configuration and SparkSession factory for US Flight Performance Analysis.
Enforces deterministic runtime parameters, memory budgeting, and safe temporary storage.
"""

from dataclasses import dataclass, field
import os
from pathlib import Path
import re
import sys
import tempfile
from typing import Optional

from pyspark.sql import SparkSession


def is_windows_host() -> bool:
    """Return True if running on a Windows operating system."""
    return sys.platform.startswith("win") or os.name == "nt"


def get_default_scratch_dir() -> str:
    """
    Return approved default scratch directory based on host OS.
    On Windows: D:/Study/Code/Apache/Flight_Analyzt/tmp_spark/ per approved ARCHITECTURE.md.
    On POSIX (Linux/macOS): Standard OS temporary directory outside repository checkout.
    """
    if is_windows_host():
        return "D:/Study/Code/Apache/Flight_Analyzt/tmp_spark/"
    return str(Path(tempfile.gettempdir()) / "flight_spark_tmp")


@dataclass
class SparkConfig:
    """SparkSession configuration parameters conforming to ARCHITECTURE.md specifications."""
    app_name: str = "US_Flight_Performance_Analysis"
    master: str = "local[4]"
    driver_memory: str = "4g"
    memory_overhead: str = "1g"
    shuffle_partitions: int = 16
    scratch_dir: str = field(default_factory=get_default_scratch_dir)
    parquet_compression: str = "snappy"
    timezone: str = "UTC"


def setup_pyspark_env() -> None:
    """Set in-process environment variables so Spark workers and driver use the current Python interpreter."""
    current_python = sys.executable
    os.environ["PYSPARK_PYTHON"] = current_python
    os.environ["PYSPARK_DRIVER_PYTHON"] = current_python


def ensure_scratch_dir(path_str: Optional[str] = None) -> str:
    """
    Ensure scratch directory exists and is writable, falling back safely if needed.
    On Windows (nt): Uses path_str (defaulting to D:/Study/Code/Apache/Flight_Analyzt/tmp_spark/).
    On POSIX (Linux/macOS): Never treats Windows drive-letter paths as relative directories.
    Always uses OS temp directory outside repository checkout.
    Fallback never uses '.' or workspace paths.
    """
    if path_str is None:
        path_str = get_default_scratch_dir()

    is_win = is_windows_host()
    has_windows_drive = bool(re.match(r"^[a-zA-Z]:", path_str))

    if not is_win and has_windows_drive:
        # On Linux/macOS, Windows drive-letter paths would be treated as relative, creating
        # a 'D:' directory in the repo working tree. Redirect to standard OS temp directory.
        scratch = Path(tempfile.gettempdir()) / "flight_spark_tmp"
    else:
        scratch = Path(path_str)
        # On POSIX, reject relative paths to prevent creating scratch dirs in checkout
        if not is_win and not scratch.is_absolute():
            scratch = Path(tempfile.gettempdir()) / "flight_spark_tmp"

    try:
        scratch.mkdir(parents=True, exist_ok=True)
        # Test writability
        test_file = scratch / f".write_test_{os.getpid()}"
        test_file.write_text("ok", encoding="utf-8")
        test_file.unlink()
        return os.path.normpath(str(scratch.resolve()))
    except Exception:
        # Fallback to standard OS temp directory (never '.' or in-repo checkout)
        fallback = Path(tempfile.gettempdir()) / "flight_spark_tmp"
        try:
            fallback.mkdir(parents=True, exist_ok=True)
        except Exception:
            pass
        return os.path.normpath(str(fallback.resolve()))


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
