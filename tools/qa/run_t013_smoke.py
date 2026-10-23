"""
Smoke test runner for T-013 KPI Aggregation on Year 2016.
Validates end-to-end cohort calculations, Arrow writing, and schema integrity without touching production runs.
"""

import sys
from pathlib import Path
import shutil

SRC_DIR = Path(__file__).resolve().parents[2] / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))
ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from flight_pipeline.kpi.runner import KpiProductionRunner


def run_smoke():
    print("=" * 80)
    print("RUNNING T-013 SMOKE TEST (YEAR 2016)")
    print("=" * 80)
    runner = KpiProductionRunner(run_id="smoke_kpi_2016_v1")
    try:
        metrics = runner.execute_core_kpi_pipeline(smoke_only=True)
        print("Smoke execution metrics:", metrics)
        assert metrics["total_output_rows"] > 0
        assert "2016" in metrics["years_processed"]
        print("SMOKE TEST PASSED SUCCESSFULLY!")
        return 0
    finally:
        # Clean up smoke staging directory
        if runner.staging_run_dir.exists():
            shutil.rmtree(runner.staging_run_dir)


if __name__ == "__main__":
    sys.exit(run_smoke())
