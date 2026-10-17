"""Configuration subpackage for flight pipeline."""

from flight_pipeline.config.spark_config import get_spark_session, stop_spark_session, SparkConfig

__all__ = ["get_spark_session", "stop_spark_session", "SparkConfig"]
