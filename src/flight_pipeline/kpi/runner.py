"""
T-013 Full CORE KPI Production Ingestion & Aggregation Runner.
Orchestrates end-to-end execution of all 8 CORE KPIs across 6 dimensional cohorts
for the 9-year curated snapshot (2016-2024, 54,674,003 accepted records).
Enforces DC-11/DC-12 row accounting, FP-DEC-015/016 min-N and GK-sketch rules,
OR-05 2024 PARTIAL date coverage, atomic publication, and independent post-run validation.
"""

import hashlib
import json
import logging
import os
from pathlib import Path
import shutil
import sys
import time
from typing import Any, Dict, List, Optional, Tuple

import psutil
import pyarrow.parquet as pq
from pyspark.sql import DataFrame, functions as F

try:
    from flight_pipeline.config.spark_config import SparkConfig, get_spark_session, stop_spark_session
    from flight_pipeline.ingestion.coordinator import read_parquet_safe, write_dataframe_parquet_safe
    from flight_pipeline.kpi.calculator import KpiCalculator
    from flight_pipeline.kpi.catalog import (
        CORE_KPI_DEFINITIONS,
        COVERAGE_PARTIAL,
        COVERAGE_VERIFIED_WITH_SCOPE,
        KPI_OUTPUT_COLUMNS,
        KPI_VERSION,
        QUALITY_VERSION,
        UNIT_STATUS_COUNT_RECORDS,
        UNIT_STATUS_RESOLVED,
        UNIT_STATUS_ZERO_DENOMINATOR,
        MIN_N_STATUS_NOT_APPLICABLE,
        MIN_N_STATUS_SUFFICIENT,
        MIN_N_STATUS_LOW_SAMPLE_CAUTION,
        MIN_N_STATUS_SUPPRESSED,
    )
    from flight_pipeline.kpi.schema import KPI_OUTPUT_SCHEMA
except ModuleNotFoundError:
    from src.flight_pipeline.config.spark_config import SparkConfig, get_spark_session, stop_spark_session
    from src.flight_pipeline.ingestion.coordinator import read_parquet_safe, write_dataframe_parquet_safe
    from src.flight_pipeline.kpi.calculator import KpiCalculator
    from src.flight_pipeline.kpi.catalog import (
        CORE_KPI_DEFINITIONS,
        COVERAGE_PARTIAL,
        COVERAGE_VERIFIED_WITH_SCOPE,
        KPI_OUTPUT_COLUMNS,
        KPI_VERSION,
        QUALITY_VERSION,
        UNIT_STATUS_COUNT_RECORDS,
        UNIT_STATUS_RESOLVED,
        UNIT_STATUS_ZERO_DENOMINATOR,
        MIN_N_STATUS_NOT_APPLICABLE,
        MIN_N_STATUS_SUFFICIENT,
        MIN_N_STATUS_LOW_SAMPLE_CAUTION,
        MIN_N_STATUS_SUPPRESSED,
    )
    from src.flight_pipeline.kpi.schema import KPI_OUTPUT_SCHEMA


def compute_file_sha256(path: Path) -> str:
    """Compute SHA-256 hash of a file."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(1024 * 1024):
            h.update(chunk)
    return h.hexdigest()


class KpiProductionRunner:
    """Production executor for T-013 Full CORE KPI Aggregation."""

    def __init__(
        self,
        run_id: str = "kpi_run_2016_2024_v1",
        repo_root: Optional[Path] = None,
        external_audit_dir: Optional[Path] = None,
    ):
        self.run_id = run_id
        self.repo_root = repo_root or Path(__file__).resolve().parents[3]
        self.external_audit_dir = external_audit_dir or Path("D:/Flight_Audit_Exports/T013_FULL_CORE_KPI")
        self.snapshot_registry_path = self.repo_root / "data" / "curated" / "snapshot_registry.json"
        self.staging_run_dir = self.repo_root / "data" / "staging" / "kpi" / self.run_id
        self.published_run_dir = self.repo_root / "data" / "kpi" / "runs" / self.run_id
        self.metadata_run_dir = self.repo_root / "data" / "metadata" / "kpi" / self.run_id
        self.latest_pointer_path = self.repo_root / "data" / "kpi" / "latest_run_id.txt"

        # Setup logging
        self.log_file = self.external_audit_dir / "execution" / "T013_FULL_EXECUTION_LOG.txt"
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger("T013KpiRunner")
        self.logger.setLevel(logging.INFO)
        for h in list(self.logger.handlers):
            h.close()
            self.logger.removeHandler(h)

        c_handler = logging.StreamHandler(sys.stdout)
        f_handler = logging.FileHandler(str(self.log_file), mode="w", encoding="utf-8")
        formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s")
        c_handler.setFormatter(formatter)
        f_handler.setFormatter(formatter)
        self.logger.addHandler(c_handler)
        self.logger.addHandler(f_handler)

    def close(self) -> None:
        """Close log handlers to safely release file locks, especially on Windows."""
        for h in list(self.logger.handlers):
            h.close()
            self.logger.removeHandler(h)

    def log(self, msg: str, level: int = logging.INFO) -> None:
        self.logger.log(level, msg)

    def run_prestart_checks(self) -> Dict[str, Any]:
        """Perform strict preflight checks on system resources, locks, and input snapshot."""
        self.log("=" * 80)
        self.log("STAGE 1: PRESTART SYSTEM, RESOURCE, AND INPUT SNAPSHOT CHECKS")
        self.log("=" * 80)

        # 1. Check RAM
        mem = psutil.virtual_memory()
        free_ram_gb = mem.available / (1024**3)
        self.log(f"Host Total RAM: {mem.total / (1024**3):.2f} GiB | Available RAM: {free_ram_gb:.2f} GiB")
        if free_ram_gb < 3.5:  # Bounded threshold
            raise RuntimeError(f"PRESTART_FAIL: Insufficient available RAM ({free_ram_gb:.2f} GiB < 3.5 GiB).")

        # 2. Check Disk Space
        disk = psutil.disk_usage(str(self.repo_root))
        free_disk_gb = disk.free / (1024**3)
        self.log(f"Workspace Drive Free Disk: {free_disk_gb:.2f} GiB")
        if free_disk_gb < 20.0:
            raise RuntimeError(f"PRESTART_FAIL: Insufficient disk space ({free_disk_gb:.2f} GiB < 20.0 GiB).")

        # 3. Check Lock Directory
        lock_dir = self.repo_root / "data" / "locks"
        active_locks = []
        if lock_dir.exists():
            for p in lock_dir.glob("*"):
                if p.is_file() and not p.name.startswith(".gitkeep") and not p.name.endswith(".coord"):
                    active_locks.append(p.name)
        if active_locks:
            raise RuntimeError(f"PRESTART_FAIL: Active locks detected in {lock_dir}: {active_locks}")
        self.log("Locks check: CLEAN (0 active locks).")

        # 4. Check Snapshot Registry
        if not self.snapshot_registry_path.is_file():
            raise FileNotFoundError(f"PRESTART_FAIL: snapshot_registry.json not found at {self.snapshot_registry_path}")

        reg_bytes = self.snapshot_registry_path.read_bytes()
        reg_hash = hashlib.sha256(reg_bytes).hexdigest()
        reg_data = json.loads(reg_bytes.decode("utf-8"))

        expected_years = [str(y) for y in range(2016, 2025)]
        years_in_reg = sorted(reg_data.get("years", {}).keys())
        if years_in_reg != expected_years:
            raise RuntimeError(f"PRESTART_FAIL: snapshot_registry years {years_in_reg} != expected {expected_years}")

        total_input_rows = 0
        annual_inventory = {}
        for y in expected_years:
            y_info = reg_data["years"][y]
            acc = y_info["accounting"]["accepted_row_count"]
            total_input_rows += acc
            rel_path = y_info["relative_curated_path"]
            abs_path = self.repo_root / "data" / rel_path
            if not abs_path.exists():
                raise FileNotFoundError(f"PRESTART_FAIL: Curated path missing for {y}: {abs_path}")
            p_files = list(abs_path.glob("*.parquet"))
            if not p_files:
                raise FileNotFoundError(f"PRESTART_FAIL: No parquet files in {abs_path}")
            annual_inventory[y] = {
                "run_id": y_info["selected_run_id"],
                "accepted_rows": acc,
                "path": str(abs_path),
                "parquet_files": len(p_files),
                "coverage_status": y_info.get("source_coverage_status", "VERIFIED_WITH_SCOPE"),
            }

        if total_input_rows != 54674003:
            raise RuntimeError(f"PRESTART_FAIL: Snapshot total rows {total_input_rows} != expected 54,674,003")

        self.log(f"Snapshot Registry verified: 9 years, {total_input_rows:,} total records, SHA-256: {reg_hash}")
        self.log("PRESTART VERDICT: PASS")

        return {
            "snapshot_sha256": reg_hash,
            "total_input_rows": total_input_rows,
            "annual_inventory": annual_inventory,
        }

    def execute_core_kpi_pipeline(self, smoke_only: bool = False) -> Dict[str, Any]:
        """Execute the full T-013 KPI calculation across all 9 years and 6 dimensions."""
        prestart_info = self.run_prestart_checks()
        annual_inventory = prestart_info["annual_inventory"]

        self.log("=" * 80)
        self.log(f"STAGE 2: INITIALIZING SPARK SESSION & KPI CALCULATOR (smoke_only={smoke_only})")
        self.log("=" * 80)

        spark_cfg = SparkConfig(
            app_name=f"T013_FullCoreKpi_{self.run_id}",
            master="local[4]",
            driver_memory="3g",
            memory_overhead="1g",
            shuffle_partitions=8,
        )
        spark = get_spark_session(spark_cfg)
        calc = KpiCalculator(run_id=self.run_id, kpi_version=KPI_VERSION, quality_version=QUALITY_VERSION)

        # Prepare clean staging directory
        if self.staging_run_dir.exists():
            shutil.rmtree(self.staging_run_dir)
        staging_data_dir = self.staging_run_dir / "data"
        staging_data_dir.mkdir(parents=True, exist_ok=True)

        execution_metrics: Dict[str, Any] = {
            "run_id": self.run_id,
            "start_time": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "years_processed": {},
            "total_output_rows": 0,
            "dimensions_computed": [
                "year",
                "year-month",
                "carrier-year",
                "origin-year",
                "dest-year",
                "route-year",
            ],
        }

        years_to_process = ["2016"] if smoke_only else [str(y) for y in range(2016, 2025)]
        total_kpi_rows_written = 0

        self.log("=" * 80)
        self.log(f"STAGE 3: COMPUTING 8 CORE KPIS ACROSS 6 DIMENSIONS FOR {len(years_to_process)} YEARS")
        self.log("=" * 80)

        start_time_all = time.time()

        for year_str in years_to_process:
            year_start = time.time()
            y_meta = annual_inventory[year_str]
            expected_cnt = y_meta["accepted_rows"]
            curated_path = Path(y_meta["path"])
            coverage_status = y_meta["coverage_status"]

            self.log(f"--- Processing Year {year_str} (Run: {y_meta['run_id']}, Expected Rows: {expected_cnt:,}) ---")

            # 1. Read input dataset safely
            df = read_parquet_safe(spark, curated_path)

            # 2. Add derived canonical YEAR_MONTH
            df_with_ym = df.withColumn("YEAR_MONTH", F.substring(F.trim(F.col("FL_DATE")), 1, 7))

            # 3. Compute 6 dimensional cohorts
            self.log(f"[{year_str}] Aggregating Dimension 1: year...")
            res_year = calc.compute_kpis_for_cohort(
                df,
                source_year=year_str,
                dimension_type="year",
                group_by_cols=None,
                source_coverage_status=coverage_status,
            )

            self.log(f"[{year_str}] Aggregating Dimension 2: year-month...")
            res_ym = calc.compute_kpis_for_cohort(
                df_with_ym,
                source_year=year_str,
                dimension_type="year-month",
                group_by_cols=["YEAR_MONTH"],
                source_coverage_status=coverage_status,
            )

            self.log(f"[{year_str}] Aggregating Dimension 3: carrier-year...")
            res_carrier = calc.compute_kpis_for_cohort(
                df,
                source_year=year_str,
                dimension_type="carrier-year",
                group_by_cols=["OP_CARRIER"],
                source_coverage_status=coverage_status,
            )

            self.log(f"[{year_str}] Aggregating Dimension 4: origin airport-year...")
            res_origin = calc.compute_kpis_for_cohort(
                df,
                source_year=year_str,
                dimension_type="origin-year",
                group_by_cols=["ORIGIN"],
                source_coverage_status=coverage_status,
            )

            self.log(f"[{year_str}] Aggregating Dimension 5: destination airport-year...")
            res_dest = calc.compute_kpis_for_cohort(
                df,
                source_year=year_str,
                dimension_type="dest-year",
                group_by_cols=["DEST"],
                source_coverage_status=coverage_status,
            )

            self.log(f"[{year_str}] Aggregating Dimension 6: directed route-year...")
            res_route = calc.compute_kpis_for_cohort(
                df,
                source_year=year_str,
                dimension_type="route-year",
                group_by_cols=["ORIGIN", "DEST"],
                source_coverage_status=coverage_status,
            )

            # 4. Union all 6 dimensional datasets for this year
            annual_kpi_df = (
                res_year.unionByName(res_ym)
                .unionByName(res_carrier)
                .unionByName(res_origin)
                .unionByName(res_dest)
                .unionByName(res_route)
            )

            # 5. Write to staging year subfolder safely via Arrow streaming
            year_staging_dir = staging_data_dir / f"year_{year_str}"
            self.log(f"[{year_str}] Writing annual KPI Parquet to staging: {year_staging_dir}...")
            promoted_files = write_dataframe_parquet_safe(
                annual_kpi_df.coalesce(1),
                year_staging_dir,
                verify_curated_schema=False,
            )

            # Count rows written
            year_kpi_rows = sum(pq.ParquetFile(str(f)).metadata.num_rows for f in promoted_files)
            year_duration = time.time() - year_start
            total_kpi_rows_written += year_kpi_rows

            self.log(
                f"[{year_str}] Done in {year_duration:.1f}s: {year_kpi_rows:,} KPI rows produced "
                f"({len(promoted_files)} file(s))."
            )

            execution_metrics["years_processed"][year_str] = {
                "input_rows": expected_cnt,
                "kpi_rows": year_kpi_rows,
                "duration_seconds": round(year_duration, 2),
                "files": [p.name for p in promoted_files],
            }

        total_duration = time.time() - start_time_all
        execution_metrics["total_output_rows"] = total_kpi_rows_written
        execution_metrics["end_time"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        execution_metrics["total_duration_seconds"] = round(total_duration, 2)

        self.log(f"All processing complete in {total_duration:.1f}s. Total KPI rows written: {total_kpi_rows_written:,}")

        # Stop Spark Session before atomic promotion and independent verification
        stop_spark_session(spark)

        return execution_metrics

    def publish_and_validate(self, execution_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate staged analytical data as a prerequisite, then atomically promote
        to production, write metadata sidecars, and update the latest KPI pointer.
        Fails closed on validation error, preserving staging and leaving previous pointer intact.
        """
        self.log("=" * 80)
        self.log("STAGE 4: STAGING VALIDATION, ATOMIC PUBLICATION & METADATA SIDECAR GENERATION")
        self.log("=" * 80)

        # 1. Fail-closed check: Published target must NOT exist (no silent overwrites)
        if self.published_run_dir.exists():
            raise RuntimeError(f"PUBLISH_FAIL: Published run directory already exists: {self.published_run_dir}")

        # 2. Check staging directory exists and contains parquet data
        if not self.staging_run_dir.exists():
            raise RuntimeError(f"PUBLISH_FAIL: Staging directory does not exist: {self.staging_run_dir}")

        staged_files = sorted(self.staging_run_dir.rglob("*.parquet"))
        if not staged_files:
            raise RuntimeError(f"PUBLISH_FAIL: No Parquet files found in staging directory: {self.staging_run_dir}")

        # 3. Inventory physical staged parquet files
        total_bytes = 0
        file_inventory_staging = []
        for sf in staged_files:
            meta = pq.ParquetFile(str(sf)).metadata
            sz = sf.stat().st_size
            total_bytes += sz
            file_hash = compute_file_sha256(sf)
            rel_p = str(sf.relative_to(self.staging_run_dir)).replace("\\", "/")
            file_inventory_staging.append({
                "relative_path": rel_p,
                "file_name": sf.name,
                "num_rows": meta.num_rows,
                "file_bytes": sz,
                "sha256": file_hash,
            })

        self.log(f"Staged Parquet files: {len(staged_files)}, Total bytes: {total_bytes:,}")

        # 4. PREREQUISITE: Perform independent mathematical & contract validation on STAGED data BEFORE publishing
        self.log("=" * 80)
        self.log("STAGE 5: PRE-PUBLICATION STAGING VALIDATION & CONTRACT AUDIT")
        self.log("=" * 80)
        self.log("Executing pre-publication mathematical validation on staged analytical outputs...")
        try:
            validation_report = self._perform_independent_validation(staged_files)
        except Exception as e:
            self.log(
                f"PRE-PUBLICATION VALIDATION FAILED: {e}. Staging directory preserved at {self.staging_run_dir}. Latest pointer UNCHANGED.",
                level=logging.ERROR,
            )
            raise

        if validation_report.get("verdict") != "PASS":
            raise RuntimeError(f"PRE-PUBLICATION VALIDATION DID NOT PASS: {validation_report}. Publication aborted.")

        self.log("Pre-publication staging validation PASSED. Proceeding to atomic directory promotion...")

        # 5. Atomically promote staging to published directory
        self.published_run_dir.parent.mkdir(parents=True, exist_ok=True)
        self.log(f"Promoting {self.staging_run_dir} -> {self.published_run_dir}...")
        os.replace(str(self.staging_run_dir), str(self.published_run_dir))
        self.log("Promotion successful.")

        # Re-resolve published files inventory with canonical relative paths
        file_inventory = []
        published_files = sorted(self.published_run_dir.rglob("*.parquet"))
        for pf in published_files:
            meta = pq.ParquetFile(str(pf)).metadata
            sz = pf.stat().st_size
            file_hash = compute_file_sha256(pf)
            rel_p = str(pf.relative_to(self.published_run_dir)).replace("\\", "/")
            file_inventory.append({
                "relative_path": rel_p,
                "file_name": pf.name,
                "num_rows": meta.num_rows,
                "file_bytes": sz,
                "sha256": file_hash,
            })

        # 6. Write RunManifest and ExecutionReceipt in metadata_run_dir
        self.metadata_run_dir.mkdir(parents=True, exist_ok=True)
        registry_rel = (
            str(self.snapshot_registry_path.relative_to(self.repo_root)).replace("\\", "/")
            if self.snapshot_registry_path.is_relative_to(self.repo_root)
            else str(self.snapshot_registry_path)
        )
        registry_sha = compute_file_sha256(self.snapshot_registry_path) if self.snapshot_registry_path.exists() else "SYNTHETIC_REGISTRY_SHA256"

        manifest_data = {
            "run_id": self.run_id,
            "kpi_version": KPI_VERSION,
            "quality_version": QUALITY_VERSION,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "snapshot_registry_path": registry_rel,
            "snapshot_registry_sha256": registry_sha,
            "input_total_rows": 54674003,
            "output_total_rows": execution_metrics["total_output_rows"],
            "total_bytes": total_bytes,
            "file_count": len(published_files),
            "files": file_inventory,
            "execution_metrics": execution_metrics,
        }
        manifest_path = self.metadata_run_dir / "run_manifest.json"
        manifest_path.write_text(json.dumps(manifest_data, indent=2), encoding="utf-8")
        manifest_sha = compute_file_sha256(manifest_path)
        self.log(f"RunManifest written to {manifest_path} (SHA-256: {manifest_sha})")

        receipt_data = {
            "run_id": self.run_id,
            "status": "SUCCESS",
            "published_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "manifest_path": (
                str(manifest_path.relative_to(self.repo_root)).replace("\\", "/")
                if manifest_path.is_relative_to(self.repo_root)
                else str(manifest_path)
            ),
            "manifest_sha256": manifest_sha,
            "total_records_processed": 54674003,
            "kpi_rows_emitted": execution_metrics["total_output_rows"],
            "output_directory": (
                str(self.published_run_dir.relative_to(self.repo_root)).replace("\\", "/")
                if self.published_run_dir.is_relative_to(self.repo_root)
                else str(self.published_run_dir)
            ),
        }
        receipt_path = self.metadata_run_dir / "execution_receipt.json"
        receipt_path.write_text(json.dumps(receipt_data, indent=2), encoding="utf-8")
        receipt_sha = compute_file_sha256(receipt_path)
        self.log(f"ExecutionReceipt written to {receipt_path} (SHA-256: {receipt_sha})")

        # 7. Update latest pointer ONLY AFTER successful validation, directory promotion, and metadata creation
        self.log(f"Updating latest KPI pointer at {self.latest_pointer_path}...")
        self.latest_pointer_path.parent.mkdir(parents=True, exist_ok=True)
        tmp_pointer = self.latest_pointer_path.parent / f".latest_kpi_ptr_{os.getpid()}"
        tmp_pointer.write_text(f"{self.run_id}\n", encoding="utf-8")
        os.replace(str(tmp_pointer), str(self.latest_pointer_path))
        self.log(f"Pointer points to: {self.run_id}")

        # 8. Write External Review Deliverables in final/
        final_dir = self.external_audit_dir / "final"
        final_dir.mkdir(parents=True, exist_ok=True)

        val_res_path = final_dir / "T013_KPI_VALIDATION_RESULTS.json"
        val_res_path.write_text(json.dumps(validation_report, indent=2), encoding="utf-8")
        self.log(f"Validation results written to {val_res_path}")

        inv_path = final_dir / "T013_KPI_OUTPUT_INVENTORY.json"
        inv_data = {
            "run_id": self.run_id,
            "published_directory": str(self.published_run_dir.resolve()),
            "total_files": len(published_files),
            "total_bytes": total_bytes,
            "total_rows": execution_metrics["total_output_rows"],
            "files": file_inventory,
        }
        inv_path.write_text(json.dumps(inv_data, indent=2), encoding="utf-8")
        self.log(f"Output inventory written to {inv_path}")

        return {
            "manifest_data": manifest_data,
            "manifest_sha256": manifest_sha,
            "receipt_data": receipt_data,
            "receipt_sha256": receipt_sha,
            "validation_report": validation_report,
            "file_inventory": file_inventory,
        }

    def _perform_independent_validation(
        self,
        files_to_validate: List[Path],
        manifest_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Perform deep mathematical checks directly via PyArrow on physical Parquet files."""
        self.log("Reading Parquet dataset directly with PyArrow for independent verification...")
        
        # Combine all files into a single Arrow Table
        tables = [pq.read_table(str(f)) for f in files_to_validate]
        full_table = pyarrow_concat_tables(tables)
        total_rows = full_table.num_rows

        self.log(f"Loaded {total_rows:,} rows across {len(files_to_validate)} Parquet files.")

        # Check Schema
        actual_cols = full_table.column_names
        if actual_cols != KPI_OUTPUT_COLUMNS:
            raise AssertionError(f"SCHEMA MISMATCH: Got {actual_cols}, expected {KPI_OUTPUT_COLUMNS}")
        self.log(f"Schema check: PASS (17 canonical columns matched in exact order).")

        # Extract columns as Python lists for deep mathematical assertions
        kpi_ids = full_table["kpi_id"].to_pylist()
        submetrics = full_table["submetric"].to_pylist()
        years = full_table["source_year"].to_pylist()
        dim_str = full_table["group_dimensions"].to_pylist()
        cnt_records = full_table["count_records"].to_pylist()
        cnt_valids = full_table["count_metric_valid"].to_pylist()
        cnt_excluded = full_table["excluded_count"].to_pylist()
        valid_rates = full_table["metric_valid_rate"].to_pylist()
        cov_statuses = full_table["source_coverage_status"].to_pylist()
        values = full_table["value"].to_pylist()
        unit_statuses = full_table["unit_status"].to_pylist()
        min_n_statuses = full_table["min_n_status"].to_pylist()

        # Invariant 1: DC-12 denominator conservation for ALL rows
        dc12_errors = 0
        rate_range_errors = 0
        min_n_errors = 0
        or05_errors = 0
        signed_delays_preserved = False
        zero_denom_tested = False
        asymmetric_routes_found = 0

        # Route asymmetry tracking: Origin-Dest -> ARR_DELAY mean
        route_means: Dict[str, float] = {}

        for i in range(total_rows):
            rec = cnt_records[i]
            val = cnt_valids[i]
            exc = cnt_excluded[i]
            rate = valid_rates[i]
            kid = kpi_ids[i]
            v = values[i]
            yr = years[i]
            cov = cov_statuses[i]
            us = unit_statuses[i]
            mn = min_n_statuses[i]
            dims = dim_str[i]

            # Invariant 1: rec == val + exc
            if rec != val + exc:
                dc12_errors += 1

            # Invariant 2: Rates in [0, 1]
            if kid in ("KPI-02", "KPI-04"):
                if v is not None and not (0.0 <= v <= 1.0):
                    rate_range_errors += 1

            # Invariant 3: Negative signed delay preservation
            if kid in ("KPI-03", "KPI-05") and v is not None and v < 0:
                signed_delays_preserved = True

            # Invariant 4: Zero denominator handling
            if val == 0:
                zero_denom_tested = True
                if kid != "KPI-01":
                    if v is not None or us != UNIT_STATUS_ZERO_DENOMINATOR:
                        dc12_errors += 1

            # Invariant 5: OR-05 for 2024
            if yr == "2024":
                if cov != COVERAGE_PARTIAL:
                    or05_errors += 1
                if "YEAR_MONTH=2024-03" in dims:
                    or05_errors += 1
            else:
                if cov != COVERAGE_VERIFIED_WITH_SCOPE:
                    or05_errors += 1

            # Route pairs tracking for asymmetry check
            if kid == "KPI-03" and "ORIGIN=" in dims and "DEST=" in dims and v is not None:
                # Format: ORIGIN=XXX;DEST=YYY;source_year=ZZZZ
                parts = dict(p.split("=") for p in dims.split(";"))
                orig = parts.get("ORIGIN")
                dst = parts.get("DEST")
                yr_p = parts.get("source_year")
                if orig and dst and yr_p:
                    route_means[f"{yr_p}:{orig}->{dst}"] = v

        # Route asymmetry verification: find A->B vs B->A pairs
        checked_pairs = set()
        for k, v_ab in route_means.items():
            yr_p, pair = k.split(":")
            orig, dst = pair.split("->")
            rev_k = f"{yr_p}:{dst}->{orig}"
            pair_key = tuple(sorted([orig, dst])) + (yr_p,)
            if pair_key in checked_pairs:
                continue
            checked_pairs.add(pair_key)
            if rev_k in route_means:
                v_ba = route_means[rev_k]
                if abs(v_ab - v_ba) > 1e-4:
                    asymmetric_routes_found += 1

        self.log(f"DC-12 Denominator Accounting: Checked {total_rows:,} rows -> {dc12_errors} errors.")
        self.log(f"Rate Bounds [0, 1]: {rate_range_errors} violations.")
        self.log(f"Signed delay preservation: Negative means preserved = {signed_delays_preserved}.")
        self.log(f"OR-05 2024 Partial Date Coverage: {or05_errors} violations (March 2024 absent).")
        self.log(f"Directed Route Asymmetry: Found {asymmetric_routes_found:,} asymmetric route pairs.")

        if dc12_errors > 0 or rate_range_errors > 0 or or05_errors > 0:
            raise AssertionError("INDEPENDENT MATHEMATICAL VALIDATION FAILED!")

        validation_summary = {
            "verdict": "PASS",
            "total_kpi_records": total_rows,
            "dc12_reconciled_rows": total_rows,
            "dc12_errors": dc12_errors,
            "rate_range_errors": rate_range_errors,
            "signed_delays_preserved": signed_delays_preserved,
            "or05_violations": or05_errors,
            "asymmetric_route_pairs_verified": asymmetric_routes_found,
            "zero_denominator_tested": zero_denom_tested,
        }

        return validation_summary


def pyarrow_concat_tables(tables: List[Any]) -> Any:
    """Concatenate PyArrow tables safely."""
    import pyarrow as pa
    return pa.concat_tables(tables)


def main():
    runner = KpiProductionRunner()
    metrics = runner.execute_core_kpi_pipeline(smoke_only=False)
    results = runner.publish_and_validate(metrics)
    print("\n" + "=" * 80)
    print("T-013 FULL CORE KPI PRODUCTION PIPELINE COMPLETED SUCCESSFULLY!")
    print("=" * 80)


if __name__ == "__main__":
    main()
