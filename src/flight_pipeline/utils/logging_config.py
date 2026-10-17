"""
Logging configuration for flight pipeline execution.
Provides structured, consistent logging format across all modules and tasks.
"""

import logging
import sys
from typing import Optional


def setup_logging(
    level: int = logging.INFO,
    run_id: Optional[str] = None,
    log_file: Optional[str] = None,
) -> logging.Logger:
    """
    Configure and return a structured logger for pipeline execution.
    Includes run_id in the formatting when provided.
    """
    logger = logging.getLogger("flight_pipeline")
    logger.setLevel(level)

    # Avoid duplicate handlers if setup_logging is called multiple times
    if logger.handlers:
        return logger

    fmt_prefix = f"[{run_id}] " if run_id else ""
    formatter = logging.Formatter(
        f"%(asctime)s | %(levelname)-7s | {fmt_prefix}%(name)s:%(funcName)s:%(lineno)d | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    if log_file:
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger
