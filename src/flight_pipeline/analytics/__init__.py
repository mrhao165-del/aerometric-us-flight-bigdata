"""
Analytics package for Task T-014.
Transforms accepted T-013 CORE KPI outputs into reproducible analytical tables,
publication-quality visualizations, research registers, and findings reports.
"""

from .reader import KPIAnalyticsReader
from .transformations import KPIAnalyticsTransformer
from .visualizations import KPIVisualizer
from .results_register import ResultsRegister
from .report_generator import FindingsReportGenerator
from .runner import T014AnalyticsRunner

__all__ = [
    "KPIAnalyticsReader",
    "KPIAnalyticsTransformer",
    "KPIVisualizer",
    "ResultsRegister",
    "FindingsReportGenerator",
    "T014AnalyticsRunner",
]
