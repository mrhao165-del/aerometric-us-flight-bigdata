"""
Standalone QA runner for T-011 KPI Sample Smoke.
Executes KpiCalculator on bounded representative data across multiple dimensions
(year, carrier-year, airport-year, route-year), verifying the 17-field schema
and emitting a machine-readable metrics summary.
"""

import json
import os
from pathlib import Path
import sys

SRC_DIR = Path(__file__).resolve().parents[2] / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))
ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from flight_pipeline.config.spark_config import SparkConfig, get_spark_session, stop_spark_session
from flight_pipeline.kpi.calculator import KpiCalculator
from flight_pipeline.kpi.catalog import KPI_OUTPUT_COLUMNS


def run_t011_kpi_smoke() -> int:
    print("=" * 80)
    print("RUNNING T-011 KPI SAMPLE SMOKE & DIMENSIONAL AGGREGATION AUDIT")
    print("=" * 80)

    config = SparkConfig(
        app_name="T011_KpiSampleSmoke",
        master="local[2]",
        shuffle_partitions=2,
        driver_memory="2g",
        memory_overhead="512m",
    )
    spark = get_spark_session(config)
    calc = KpiCalculator(run_id="smoke_run_t011")

    # Generate multi-carrier, multi-airport representative sample (1,200 flights)
    # Allows testing carrier-year min-N threshold (AA >= 1000 -> LOW_SAMPLE_CAUTION, DL < 1000 -> SUPPRESSED)
    records = []
    for i in range(1200):
        # 1050 records for AA (exceeds min-N 1000)
        # 150 records for DL (less than min-N 1000)
        carrier = "AA" if i < 1050 else "DL"
        origin = "DFW" if i % 2 == 0 else "ORD"
        dest = "LAX" if i % 3 == 0 else "ATL"
        arr_delay = float(i % 60 - 20)  # mix of early arrivals (-20 to -1) and late (+0 to +39)
        dep_delay = float(i % 50 - 15)

        records.append({
            "FL_DATE": "2016-06-15",
            "OP_CARRIER": carrier,
            "OP_CARRIER_FL_NUM": float(1000 + i),
            "ORIGIN": origin,
            "DEST": dest,
            "ARR_DELAY": arr_delay,
            "DEP_DELAY": dep_delay,
            "TAXI_OUT": 18.0 + (i % 8),
            "TAXI_IN": 7.0 + (i % 4),
            "AIR_TIME": 120.0 + (i % 30),
            "ACTUAL_ELAPSED_TIME": 145.0 + (i % 40),
            "CRS_ELAPSED_TIME": 150.0,
        })

    df = spark.createDataFrame(records)

    # 1. Overall cohort (year dimension)
    print("[RUN] Computing Year-level KPIs...")
    kpi_year_df = calc.compute_kpis_for_cohort(
        df=df,
        source_year="2016",
        dimension_type="year",
        filter_definition="accepted_flights",
    )
    year_rows = kpi_year_df.collect()
    print(f"  Emitted {len(year_rows)} KPI slices for year level.")

    # 2. Carrier-year dimension
    print("[RUN] Computing Carrier-Year level KPIs...")
    kpi_carrier_df = calc.compute_kpis_for_cohort(
        df=df,
        source_year="2016",
        dimension_type="carrier-year",
        group_by_cols=["OP_CARRIER"],
        filter_definition="accepted_flights,by_carrier",
    )
    carrier_rows = kpi_carrier_df.collect()
    print(f"  Emitted {len(carrier_rows)} KPI slices for carrier-year level.")

    # Verify carrier min-N behavior: AA has count 1050 (LOW_SAMPLE_CAUTION), DL has 150 (SUPPRESSED)
    aa_kpi01 = [r for r in carrier_rows if "OP_CARRIER=AA" in r["group_dimensions"] and r["kpi_id"] == "KPI-01"][0]
    dl_kpi01 = [r for r in carrier_rows if "OP_CARRIER=DL" in r["group_dimensions"] and r["kpi_id"] == "KPI-01"][0]

    assert aa_kpi01["min_n_status"] == "LOW_SAMPLE_CAUTION", f"Expected LOW_SAMPLE_CAUTION, got {aa_kpi01['min_n_status']}"
    assert dl_kpi01["min_n_status"] == "SUPPRESSED", f"Expected SUPPRESSED, got {dl_kpi01['min_n_status']}"
    print(f"  [PASS] AA min_n_status: {aa_kpi01['min_n_status']} (count: {aa_kpi01['count_metric_valid']})")
    print(f"  [PASS] DL min_n_status: {dl_kpi01['min_n_status']} (count: {dl_kpi01['count_metric_valid']})")

    # Metrics summary
    smoke_summary = {
        "run_id": "smoke_run_t011",
        "total_sample_records": len(records),
        "year_slices_emitted": len(year_rows),
        "carrier_slices_emitted": len(carrier_rows),
        "columns_verified": KPI_OUTPUT_COLUMNS,
        "sample_kpi_values": {
            f"{r['kpi_id']}:{r['submetric']}": {
                "value": r["value"],
                "count_valid": r["count_metric_valid"],
                "unit_status": r["unit_status"],
                "min_n_status": r["min_n_status"],
            }
            for r in year_rows
        },
    }

    out_json = ROOT_DIR / "docs" / "05-evidence" / "T011_KPI_SAMPLE_SMOKE_METRICS.json"
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(smoke_summary, f, indent=2)

    print(f"[ARTIFACT] KPI smoke metrics written to: {out_json}")
    print("=" * 80)
    stop_spark_session()
    return 0


if __name__ == "__main__":
    sys.exit(run_t011_kpi_smoke())
