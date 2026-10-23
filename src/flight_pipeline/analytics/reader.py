"""
KPI Analytics Reader for Task T-014.
Loads and indexes the approved T-013 CORE KPI dataset read-only.
"""

import os
import re
import glob
import json
import logging
from typing import Dict, Any, List, Optional
import pyarrow.parquet as pq
import pandas as pd

logger = logging.getLogger("flight_pipeline.analytics.reader")

EXPECTED_COLUMNS = [
    "kpi_id",
    "submetric",
    "run_id",
    "kpi_version",
    "source_year",
    "group_dimensions",
    "filter_definition",
    "count_records",
    "count_metric_valid",
    "excluded_count",
    "metric_valid_rate",
    "source_coverage_status",
    "value",
    "unit_status",
    "min_n_status",
    "quality_version",
    "provenance_reference",
]


class KPIAnalyticsReader:
    """Read-only loader and indexer for published CORE KPI datasets."""

    def __init__(self, base_dir: str = "."):
        self.base_dir = os.path.abspath(base_dir)
        self.kpi_root = os.path.join(self.base_dir, "data", "kpi")
        self.metadata_root = os.path.join(self.base_dir, "data", "metadata", "kpi")
        self._cached_df: Optional[pd.DataFrame] = None
        self._run_id: Optional[str] = None
        self._manifest_data: Optional[Dict[str, Any]] = None

    def get_latest_run_id(self) -> str:
        pointer_path = os.path.join(self.kpi_root, "latest_run_id.txt")
        if not os.path.exists(pointer_path):
            raise FileNotFoundError(f"KPI latest pointer not found: {pointer_path}")
        with open(pointer_path, "r", encoding="utf-8") as f:
            run_id = f.read().strip()
        if not run_id:
            raise ValueError(f"KPI latest pointer is empty: {pointer_path}")
        return run_id

    def verify_input_baseline(self, run_id: Optional[str] = None) -> Dict[str, Any]:
        """Verify RunManifest, ExecutionReceipt, file counts, and schema before loading."""
        if run_id is None:
            run_id = self.get_latest_run_id()
        self._run_id = run_id

        run_dir = os.path.join(self.kpi_root, "runs", run_id)
        if not os.path.exists(run_dir):
            raise FileNotFoundError(f"KPI run directory does not exist: {run_dir}")

        manifest_path = os.path.join(self.metadata_root, run_id, "run_manifest.json")
        receipt_path = os.path.join(self.metadata_root, run_id, "execution_receipt.json")

        if not os.path.exists(manifest_path):
            raise FileNotFoundError(f"RunManifest missing: {manifest_path}")
        if not os.path.exists(receipt_path):
            raise FileNotFoundError(f"ExecutionReceipt missing: {receipt_path}")

        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest = json.load(f)
        with open(receipt_path, "r", encoding="utf-8") as f:
            receipt = json.load(f)

        self._manifest_data = manifest

        pattern = os.path.join(run_dir, "data", "*", "*.parquet")
        files = sorted(glob.glob(pattern))
        if len(files) != 9:
            raise ValueError(f"Expected 9 Parquet partitions, found {len(files)} in {run_dir}")

        total_bytes = sum(os.path.getsize(f) for f in files)
        logger.info("Verified KPI input: %s (%d files, %d bytes)", run_id, len(files), total_bytes)

        return {
            "run_id": run_id,
            "manifest_status": receipt.get("status"),
            "manifest_total_rows": manifest.get("output_total_rows"),
            "manifest_total_bytes": manifest.get("total_bytes"),
            "input_total_records": manifest.get("input_total_rows"),
            "file_count": len(files),
            "files": files,
            "total_bytes": total_bytes,
        }

    @staticmethod
    def classify_dimension_family(group_dimensions: str) -> str:
        """Deterministically classify cohort into one of the 6 approved grouping families."""
        if "ORIGIN=" in group_dimensions and "DEST=" in group_dimensions:
            return "route-year"
        elif "ORIGIN=" in group_dimensions:
            return "origin-year"
        elif "DEST=" in group_dimensions:
            return "dest-year"
        elif "OP_UNIQUE_CARRIER=" in group_dimensions or "OP_CARRIER=" in group_dimensions:
            return "carrier-year"
        elif "YEAR_MONTH=" in group_dimensions:
            return "year-month"
        elif "cohort=all" in group_dimensions:
            return "year"
        return "unknown"

    def load_kpi_dataset(self, run_id: Optional[str] = None) -> pd.DataFrame:
        """Load all 9 KPI Parquet partitions into memory and enrich with parsed dimension fields."""
        if self._cached_df is not None:
            return self._cached_df

        baseline = self.verify_input_baseline(run_id)
        files = baseline["files"]

        tables = []
        for file_path in files:
            table = pq.read_table(file_path)
            # Verify columns
            if table.column_names != EXPECTED_COLUMNS:
                raise ValueError(
                    f"Parquet schema mismatch in {file_path}. Expected {EXPECTED_COLUMNS}, got {table.column_names}"
                )
            tables.append(table.to_pandas())

        full_df = pd.concat(tables, ignore_index=True)
        if len(full_df) != 684180:
            raise ValueError(f"Expected 684,180 KPI records, got {len(full_df)}")

        # Enrich with dimension family
        full_df["group_family"] = full_df["group_dimensions"].apply(self.classify_dimension_family)

        # Extract parsed entity fields
        full_df["entity_year"] = full_df["source_year"].astype(int)
        full_df["entity_month"] = full_df["group_dimensions"].str.extract(r"YEAR_MONTH=[0-9]{4}-([0-9]{2})")
        full_df["entity_year_month"] = full_df["group_dimensions"].str.extract(r"YEAR_MONTH=([0-9]{4}-[0-9]{2})")
        full_df["entity_carrier"] = full_df["group_dimensions"].str.extract(r"OP_(?:UNIQUE_)?CARRIER=([A-Z0-9]+)")
        full_df["entity_origin"] = full_df["group_dimensions"].str.extract(r"ORIGIN=([A-Z0-9]+)")
        full_df["entity_dest"] = full_df["group_dimensions"].str.extract(r"DEST=([A-Z0-9]+)")

        self._cached_df = full_df
        logger.info("Successfully loaded %d KPI rows across 6 grouping families", len(full_df))
        return self._cached_df

    @property
    def manifest(self) -> Dict[str, Any]:
        return self._manifest_data or {}
