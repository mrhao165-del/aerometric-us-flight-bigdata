"""
Calendar Date Coverage and OR-05 Annual Defect Analyzer (T-008).
Conforms to DATA_CONTRACT.md, ARCHITECTURE.md, and Gate G2 / G3 decisions (FP-DEC-002, OR-05, TS-004).
"""

from calendar import isleap
from dataclasses import dataclass, asdict
from datetime import date, timedelta
from typing import Any, Dict, List, Optional, Set
from pyspark.sql import DataFrame, functions as F


@dataclass(frozen=True)
class CoverageReport:
    """
    Structured report of calendar date coverage for a specific survey year.
    Captures leap-year semantics, missing date counts, and OR-05 2024 March anomaly.
    """
    year: int
    is_leap: bool
    expected_days: int
    observed_days: int
    missing_days_count: int
    missing_dates: List[str]
    out_of_year_count: int
    out_of_year_dates: List[str]
    source_coverage_status: str  # "COMPLETE" or "PARTIAL"
    coverage_ratio: Optional[float]
    has_march_2024_defect: bool
    is_march_missing: bool = False
    is_exact_or05_pattern: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert report to dictionary."""
        return asdict(self)


class DateCoverageAnalyzer:
    """
    Evaluates calendar date coverage across survey cohorts.
    Detects leap-year anomalies, missing calendar days, and flags OR-05 March 2024 absence.
    Does NOT interpolate or fabricate synthetic flight records to fill missing days.
    """

    @staticmethod
    def get_expected_dates_for_year(year: int) -> List[str]:
        """Generate all canonical calendar dates (YYYY-MM-DD) for a given calendar year."""
        start_date = date(year, 1, 1)
        total_days = 366 if isleap(year) else 365
        return [(start_date + timedelta(days=i)).isoformat() for i in range(total_days)]

    @classmethod
    def analyze(cls, df: DataFrame, target_year: int, date_col: str = "FL_DATE") -> CoverageReport:
        """
        Analyze date coverage for a target year against a PySpark DataFrame.
        Evaluates distinct dates from the `FL_DATE` column (extracting YYYY-MM-DD).
        """
        if date_col not in df.columns:
            raise ValueError(f"DataFrame missing date column: {date_col}")

        # Extract normalized YYYY-MM-DD substring and collect distinct values
        date_expr = F.substring(F.trim(F.col(date_col)), 1, 10)
        distinct_rows = (
            df.select(date_expr.alias("clean_date"))
            .filter(F.col("clean_date").isNotNull() & (F.col("clean_date") != ""))
            .distinct()
            .collect()
        )

        observed_set: Set[str] = {r["clean_date"] for r in distinct_rows if r["clean_date"] is not None}
        expected_list = cls.get_expected_dates_for_year(target_year)
        expected_set = set(expected_list)

        missing_dates = sorted(list(expected_set - observed_set))
        out_of_year_dates = sorted([d for d in observed_set if not d.startswith(f"{target_year}-")])
        in_year_observed = observed_set.intersection(expected_set)

        expected_count = len(expected_list)
        observed_count = len(in_year_observed)
        missing_count = len(missing_dates)
        out_count = len(out_of_year_dates)

        ratio = (observed_count / expected_count) if expected_count > 0 else None
        status = "COMPLETE" if (missing_count == 0 and expected_count > 0) else "PARTIAL"

        # Check for OR-05 specific pattern: 2024 missing all 31 days of March.
        # Disambiguate March missing vs exact OR-05 pattern (335 observed days, exactly 31 days of March missing).
        # An empty cohort (observed_count == 0) must NOT trigger the OR-05 defect flag.
        has_march_2024_defect = False
        is_march_missing = False
        is_exact_or05_pattern = False
        if target_year == 2024 and observed_count > 0:
            march_days = [f"2024-03-{d:02d}" for d in range(1, 32)]
            is_march_missing = all(m in missing_dates for m in march_days)
            has_march_2024_defect = is_march_missing
            is_exact_or05_pattern = (observed_count == 335 and missing_count == 31 and is_march_missing)

        return CoverageReport(
            year=target_year,
            is_leap=isleap(target_year),
            expected_days=expected_count,
            observed_days=observed_count,
            missing_days_count=missing_count,
            missing_dates=missing_dates,
            out_of_year_count=out_count,
            out_of_year_dates=out_of_year_dates,
            source_coverage_status=status,
            coverage_ratio=ratio,
            has_march_2024_defect=has_march_2024_defect,
            is_march_missing=is_march_missing,
            is_exact_or05_pattern=is_exact_or05_pattern,
        )
