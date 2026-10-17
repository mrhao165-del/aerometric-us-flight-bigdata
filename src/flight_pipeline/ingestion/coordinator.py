"""
End-to-End Ingestion Coordinator and Pipeline Lifecycle Engine (T007-05).
Integrates:
- Canonical Schema (T007-01: schema.py)
- Source Validator (T007-02: source_validator.py)
- Raw CSV Reader & Classifier (T007-03: reader.py)
- Single-Writer Lock (T007-04: locking.py)
- SparkConfig, RunManifest, RowAccounting, SafePublisher (T-009)

Governance Invariants:
- 8-state deterministic lifecycle: RUN_STARTED -> SOURCE_VERIFICATION -> INGESTION_IN_PROGRESS ->
  INGESTION_COMPLETED -> STAGING_VERIFIED -> PUBLICATION_PENDING -> PUBLISHED | TERMINAL_FAILURE.
- Sidecar ExecutionReceipt resolves manifest self-reference without mutating immutable published payload.
- Diagnostic and manifest files are stored in metadata directory outside Parquet staging/published directories.
- Preserves OR-05 (2024 partial coverage warning), OR-08 (IDENTITY_UNVERIFIED), FP-DEC-017 (Weather CONDITIONAL_NO_GO),
  and G2-EXC-001 (Provisional units).
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from hashlib import sha256
import json
import os
from pathlib import Path
from typing import Any, Callable, Dict, List, Mapping, Optional, Sequence, Tuple, Union

from pyspark.sql import DataFrame, SparkSession, functions as F

from flight_pipeline.config.spark_config import SparkConfig, get_spark_session
from flight_pipeline.ingestion.reader import (
    CsvReadOptions,
    IngestionRecordClassifier,
    IngestionTransformer,
    RawCsvReader,
    RecordStatus,
    REASON_COLUMN,
    STATUS_COLUMN,
    compute_row_accounting,
)
from flight_pipeline.ingestion.schema import (
    CANONICAL_COLUMN_NAMES,
    CORRUPT_RECORD_COLUMN,
    get_curated_parquet_schema,
)
from flight_pipeline.ingestion.source_validator import (
    BatchVerificationResult,
    SourceEntry,
    SourceValidator,
    UPSTREAM_IDENTITY_STATUS_UNVERIFIED,
    VerificationState,
)
from flight_pipeline.storage.locking import (
    LockError,
    SingleWriterLock,
)
from flight_pipeline.storage.publication import (
    PublicationResult,
    SafePublisher,
    compute_file_sha256,
    validate_run_id,
)
from flight_pipeline.utils.run_manifest import RowAccounting, RunManifest


class PipelineState(str, Enum):
    """Canonical lifecycle states for T-007 Ingestion Coordinator."""
    RUN_STARTED = "RUN_STARTED"
    SOURCE_VERIFICATION = "SOURCE_VERIFICATION"
    INGESTION_IN_PROGRESS = "INGESTION_IN_PROGRESS"
    INGESTION_COMPLETED = "INGESTION_COMPLETED"
    STAGING_VERIFIED = "STAGING_VERIFIED"
    PUBLICATION_PENDING = "PUBLICATION_PENDING"
    PUBLISHED = "PUBLISHED"
    TERMINAL_FAILURE = "TERMINAL_FAILURE"


@dataclass
class ExecutionReceipt:
    """
    Independent sidecar receipt written outside the immutable versioned Parquet payload.
    Resolves the manifest self-reference paradox by recording the finalized manifest's
    exact disk size and SHA-256 alongside the publication outcome.
    """
    run_id: str
    task_id: str
    pipeline_state: str
    publication_status: str
    published_path: Optional[str]
    pointer_value: Optional[str]
    previous_pointer: Optional[str]
    manifest_path: str
    manifest_bytes: int
    manifest_sha256: str
    row_accounting: Dict[str, Any]
    upstream_identity_status: str = UPSTREAM_IDENTITY_STATUS_UNVERIFIED
    weather_branch_status: str = "CONDITIONAL_NO_GO"
    core_measures_unit_status: str = "G2-EXC-001_PROVISIONAL"
    or05_coverage_warning: Optional[str] = None
    completed_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class PipelineRunOutcome:
    """Comprehensive return object from an IngestionCoordinator run."""
    success: bool
    run_id: str
    final_state: PipelineState
    state_history: List[PipelineState]
    row_accounting: Optional[RowAccounting] = None
    publication_result: Optional[PublicationResult] = None
    manifest_path: Optional[Path] = None
    receipt_path: Optional[Path] = None
    receipt: Optional[ExecutionReceipt] = None
    source_verification: Optional[BatchVerificationResult] = None
    anomaly_summary: Dict[str, int] = field(default_factory=dict)
    governance_warnings: List[str] = field(default_factory=list)
    error_message: Optional[str] = None


def write_json_atomic(target_path: Path, data: Dict[str, Any]) -> Tuple[int, str]:
    """
    Atomically write dictionary as JSON to target_path using a temporary file and os.replace.
    Returns (byte_size, sha256_hex) of the written file.
    """
    target_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = target_path.with_suffix(target_path.suffix + f".tmp.{os.getpid()}")
    payload = (json.dumps(data, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    try:
        with open(tmp_path, "wb") as f:
            f.write(payload)
            f.flush()
            os.fsync(f.fileno())
        os.replace(str(tmp_path), str(target_path))
    except Exception:
        if tmp_path.exists():
            try:
                tmp_path.unlink()
            except Exception:
                pass
        raise

    actual_bytes = target_path.stat().st_size
    actual_sha256 = compute_file_sha256(target_path)
    return actual_bytes, actual_sha256


def write_dataframe_parquet_safe(
    df: DataFrame,
    staging_dir: Path,
    compression: str = "snappy",
) -> List[Path]:
    """
    Write a PySpark DataFrame to Parquet files in staging_dir using streaming Arrow batches
    (`mapInArrow` + `pyarrow.parquet.ParquetWriter`).
    
    Why this is used on Windows local environments:
    - Standard `df.write.parquet()` invokes Hadoop's `Shell.getQualifiedBin("winutils.exe")`,
      which fails with FileNotFoundException on Windows hosts when HADOOP_HOME is unset.
    - `mapInArrow` executes distributed across Spark workers/partitions in streaming O(1) memory
      chunks (never collecting data to driver RAM) and writes standard Apache Parquet files
      with Snappy compression that are 100% readable by both Spark and PyArrow.
    """
    import uuid
    import pyarrow as pa
    import pyarrow.parquet as pq
    from pyspark import TaskContext
    from pyspark.sql.pandas.types import to_arrow_schema
    from pyspark.sql.types import LongType, StringType as SparkStringType, StructField, StructType

    staging_dir.mkdir(parents=True, exist_ok=True)
    arrow_schema = to_arrow_schema(df.schema)
    out_dir_str = str(staging_dir.resolve())

    def _write_partition_arrow(batch_iter):
        ctx = TaskContext.get()
        part_id = ctx.partitionId() if ctx is not None else 0
        uid = uuid.uuid4().hex[:8]
        part_file = Path(out_dir_str) / f"part-{part_id:05d}-{uid}.parquet"

        writer = None
        rows_written = 0
        try:
            for batch in batch_iter:
                if batch.num_rows > 0:
                    if writer is None:
                        writer = pq.ParquetWriter(
                            str(part_file),
                            arrow_schema,
                            compression=compression,
                        )
                    # Ensure batch matches target arrow_schema
                    tbl = pa.Table.from_batches([batch], schema=arrow_schema)
                    writer.write_table(tbl)
                    rows_written += batch.num_rows
        finally:
            if writer is not None:
                writer.close()

        result_batch = pa.RecordBatch.from_pydict(
            {
                "file_path": [str(part_file) if rows_written > 0 else ""],
                "rows_written": [rows_written],
            },
            schema=pa.schema([
                pa.field("file_path", pa.string()),
                pa.field("rows_written", pa.int64()),
            ]),
        )
        yield result_batch

    result_schema = StructType([
        StructField("file_path", SparkStringType(), True),
        StructField("rows_written", LongType(), True),
    ])

    summary_rows = df.mapInArrow(_write_partition_arrow, result_schema).collect()
    written_files = [Path(r["file_path"]) for r in summary_rows if r["file_path"]]

    # If DataFrame had 0 rows (e.g., header-only CSV), write a single valid empty Parquet file
    if not written_files:
        empty_file = staging_dir / "part-00000-empty.parquet"
        empty_arrays = [pa.array([], type=field.type) for field in arrow_schema]
        empty_table = pa.Table.from_arrays(empty_arrays, schema=arrow_schema)
        pq.write_table(empty_table, str(empty_file), compression=compression)
        written_files.append(empty_file)

    return sorted(written_files)


def read_parquet_safe(
    spark: SparkSession,
    parquet_dir_or_file: Union[str, Path],
) -> DataFrame:
    """
    Read Parquet files from a directory or file path into a PySpark DataFrame safely on Windows.
    Passing explicit `.parquet` file paths avoids Hadoop's `RawLocalFileSystem.listStatus`
    -> `FileUtil.canRead` -> `NativeIO$Windows.access0` UnsatisfiedLinkError when `hadoop.dll`
    is absent on Windows.
    """
    target = Path(parquet_dir_or_file).resolve()
    if target.is_dir():
        parquet_files = sorted(str(p) for p in target.rglob("*.parquet") if p.is_file())
        if not parquet_files:
            raise FileNotFoundError(f"No .parquet files found in directory: {target}")
        return spark.read.parquet(*parquet_files)
    return spark.read.parquet(str(target))


class IngestionCoordinator:
    """
    Orchestrates end-to-end raw CSV ingestion into curated Parquet storage.
    Enforces single-writer locking, fail-closed source validation, DC-11 row accounting,
    7-step Windows NTFS atomic publication, and sidecar receipt generation.
    """

    def __init__(
        self,
        spark: SparkSession,
        base_data_dir: Union[str, Path],
        source_validator: SourceValidator,
        csv_options: Optional[CsvReadOptions] = None,
        task_id: str = "T-007",
    ):
        if spark is None:
            raise ValueError("SparkSession cannot be None")
        self.spark = spark
        self.base_data_dir = Path(base_data_dir).resolve()
        self.source_validator = source_validator
        self.csv_options = csv_options or CsvReadOptions()
        self.task_id = task_id

        self.staging_root = self.base_data_dir / "staging"
        self.curated_root = self.base_data_dir / "curated"
        self.metadata_root = self.base_data_dir / "metadata"
        self.lock_dir = self.base_data_dir / "locks"

        self.publisher = SafePublisher(str(self.base_data_dir))
        self.reader = RawCsvReader(self.spark, options=self.csv_options)

    def run_ingestion(
        self,
        run_id: str,
        years: Optional[Sequence[int]] = None,
        require_verified_hashes: bool = True,
        allow_candidate_hashes: bool = False,
        fault_injector: Optional[Callable[[str], None]] = None,
    ) -> PipelineRunOutcome:
        """
        Execute the full ingestion lifecycle for the specified years.
        
        Args:
            run_id: Unique identifier for this execution run.
            years: Subset of years to ingest (defaults to all years in validator inventory).
            require_verified_hashes: If True, requires LOCAL_HASH_VERIFIED unless allow_candidate_hashes=True.
            allow_candidate_hashes: If True, permits LOCAL_HASH_COMPUTED_UNAPPROVED candidate hashes.
            fault_injector: Optional hook called at lifecycle transitions for negative testing.
            
        Returns:
            PipelineRunOutcome with full state trace, accounting, and artifact paths.
        """
        state_history: List[PipelineState] = []

        def transition(new_state: PipelineState) -> None:
            state_history.append(new_state)
            if fault_injector is not None:
                fault_injector(new_state.value)

        # Validate run_id format early using SafePublisher's canonical validator
        try:
            validate_run_id(run_id, self.staging_root)
        except ValueError as e:
            state_history.append(PipelineState.TERMINAL_FAILURE)
            return PipelineRunOutcome(
                success=False,
                run_id=run_id,
                final_state=PipelineState.TERMINAL_FAILURE,
                state_history=state_history,
                error_message=f"Invalid run_id: {e}",
            )

        run_meta_dir = self.metadata_root / run_id
        manifest_path = run_meta_dir / "run_manifest.json"
        receipt_path = run_meta_dir / "execution_receipt.json"
        staging_run_dir = self.staging_root / run_id

        manifest = RunManifest(
            run_id=run_id,
            task_id=self.task_id,
            configuration={
                "base_data_dir": str(self.base_data_dir),
                "years": list(years) if years is not None else sorted(self.source_validator.inventory.keys()),
                "require_verified_hashes": require_verified_hashes,
                "allow_candidate_hashes": allow_candidate_hashes,
                "upstream_identity_status": UPSTREAM_IDENTITY_STATUS_UNVERIFIED,
                "weather_status": "CONDITIONAL_NO_GO",
                "core_units_status": "G2-EXC-001_PROVISIONAL",
            },
        )

        governance_warnings: List[str] = [
            "OR-08: Raw source upstream identity is IDENTITY_UNVERIFIED (local SHA-256 proves snapshot integrity only).",
            "FP-DEC-017: Weather columns are CONDITIONAL_NO_GO and optional for CORE.",
            "G2-EXC-001: 7 CORE delay/time measures carry provisional minute units pending G5 TS-018 verification.",
        ]

        target_years = sorted(years) if years is not None else sorted(self.source_validator.inventory.keys())
        if 2024 in target_years:
            governance_warnings.append(
                "OR-05: OPEN_QUALITY_DEFECT — Year 2024 has partial coverage (335/366 days; March 2024 missing)."
            )

        lock = SingleWriterLock(self.lock_dir, run_id=run_id)
        try:
            # Acquire single-writer lock before any critical state
            lock.acquire()
            transition(PipelineState.RUN_STARTED)

            # Check if run_id already published or staged to prevent duplicate run_id collision
            if (self.publisher.runs_root / run_id).exists() or staging_run_dir.exists():
                raise ValueError(f"Duplicate or pre-existing run_id directory detected for '{run_id}'")

            # -----------------------------------------------------------------
            # STEP 1: SOURCE VERIFICATION
            # -----------------------------------------------------------------
            transition(PipelineState.SOURCE_VERIFICATION)

            batch_res = self._verify_target_sources(
                target_years=target_years,
                require_verified_hashes=require_verified_hashes,
                allow_candidate_hashes=allow_candidate_hashes,
            )

            # Save source verification diagnostic report in metadata directory
            write_json_atomic(run_meta_dir / "source_verification.json", batch_res.to_dict())

            # Record verified/candidate inputs into RunManifest
            for yr in target_years:
                r = batch_res.results[yr]
                manifest.record_input(
                    path=r.path,
                    bytes_count=r.actual_byte_size or 0,
                    sha256_hash=r.computed_sha256,
                )

            # -----------------------------------------------------------------
            # STEP 2: INGESTION IN PROGRESS (READ, CLASSIFY, ACCOUNT, WRITE STAGING)
            # -----------------------------------------------------------------
            transition(PipelineState.INGESTION_IN_PROGRESS)

            combined_raw_df: Optional[DataFrame] = None
            for yr in target_years:
                src_path = self.source_validator.get_source_path(yr)
                yr_df = self.reader.read_raw(src_path)
                if combined_raw_df is None:
                    combined_raw_df = yr_df
                else:
                    combined_raw_df = combined_raw_df.unionByName(yr_df)

            if combined_raw_df is None:
                raise ValueError("No source DataFrames loaded for target years")

            classified_df = IngestionRecordClassifier.classify(combined_raw_df)
            accounting = compute_row_accounting(classified_df)
            manifest.row_accounting = accounting

            # Collect anomaly breakdown for forensic metadata
            anomaly_rows = (
                classified_df
                .filter(F.col(STATUS_COLUMN) != RecordStatus.ACCEPTED.value)
                .groupBy(STATUS_COLUMN, REASON_COLUMN)
                .agg(F.count(F.lit(1)).alias("count"))
                .collect()
            )
            anomaly_summary = {
                f"{row[STATUS_COLUMN]}:{row[REASON_COLUMN]}": row["count"]
                for row in anomaly_rows
            }
            write_json_atomic(
                run_meta_dir / "anomaly_summary.json",
                {
                    "run_id": run_id,
                    "row_accounting": accounting.to_dict(),
                    "anomaly_breakdown": anomaly_summary,
                },
            )

            # Transform accepted records to curated schema and write Parquet to staging
            curated_df = IngestionTransformer.to_curated(classified_df, filter_accepted=True)
            staging_run_dir.mkdir(parents=True, exist_ok=True)
            write_dataframe_parquet_safe(curated_df, staging_run_dir)

            transition(PipelineState.INGESTION_COMPLETED)

            # -----------------------------------------------------------------
            # STEP 3: STAGING VERIFIED
            # -----------------------------------------------------------------
            # Clean up Spark _SUCCESS and .crc metadata files from staging if needed,
            # though SafePublisher ignores _SUCCESS and .crc files automatically.
            parquet_files = sorted(staging_run_dir.rglob("*.parquet"))
            if not parquet_files:
                raise RuntimeError(f"No .parquet files produced in staging directory {staging_run_dir}")

            transition(PipelineState.STAGING_VERIFIED)

            # -----------------------------------------------------------------
            # STEP 4: PUBLICATION PENDING & SAFE PUBLISHER EXECUTION
            # -----------------------------------------------------------------
            transition(PipelineState.PUBLICATION_PENDING)

            pub_result = self.publisher.publish(
                run_id=run_id,
                staging_dir=staging_run_dir,
                accounting=accounting,
            )

            if not pub_result.success or pub_result.status != "PUBLISHED":
                raise RuntimeError(
                    f"SafePublisher failed at step {pub_result.aborted_step} with status "
                    f"{pub_result.status}: {pub_result.error_message}"
                )

            # Record published Parquet files in RunManifest
            published_dir = Path(pub_result.published_path)
            for pf in sorted(published_dir.rglob("*.parquet")):
                manifest.record_output(
                    path=pf.relative_to(self.base_data_dir).as_posix(),
                    bytes_count=pf.stat().st_size,
                    sha256_hash=compute_file_sha256(pf),
                )

            # Close and persist RunManifest atomically in metadata directory (outside published_dir)
            manifest.close(status="PUBLISHED")
            manifest_bytes, manifest_sha256 = write_json_atomic(manifest_path, manifest.to_dict())

            # Write independent sidecar ExecutionReceipt atomically
            or05_warn = next((w for w in governance_warnings if "OR-05" in w), None)
            receipt = ExecutionReceipt(
                run_id=run_id,
                task_id=self.task_id,
                pipeline_state=PipelineState.PUBLISHED.value,
                publication_status=pub_result.status,
                published_path=pub_result.published_path,
                pointer_value=pub_result.pointer_value,
                previous_pointer=pub_result.previous_pointer,
                manifest_path=str(manifest_path),
                manifest_bytes=manifest_bytes,
                manifest_sha256=manifest_sha256,
                row_accounting=accounting.to_dict(),
                upstream_identity_status=UPSTREAM_IDENTITY_STATUS_UNVERIFIED,
                or05_coverage_warning=or05_warn,
            )
            write_json_atomic(receipt_path, receipt.to_dict())

            transition(PipelineState.PUBLISHED)

            return PipelineRunOutcome(
                success=True,
                run_id=run_id,
                final_state=PipelineState.PUBLISHED,
                state_history=state_history,
                row_accounting=accounting,
                publication_result=pub_result,
                manifest_path=manifest_path,
                receipt_path=receipt_path,
                receipt=receipt,
                source_verification=batch_res,
                anomaly_summary=anomaly_summary,
                governance_warnings=governance_warnings,
            )

        except Exception as exc:
            state_history.append(PipelineState.TERMINAL_FAILURE)
            err_msg = str(exc)
            try:
                manifest.close(status="FAILED", error=err_msg)
                write_json_atomic(manifest_path, manifest.to_dict())
            except Exception:
                pass

            return PipelineRunOutcome(
                success=False,
                run_id=run_id,
                final_state=PipelineState.TERMINAL_FAILURE,
                state_history=state_history,
                row_accounting=manifest.row_accounting,
                manifest_path=manifest_path if manifest_path.exists() else None,
                governance_warnings=governance_warnings,
                error_message=err_msg,
            )
        finally:
            if lock.is_acquired:
                try:
                    lock.release()
                except Exception:
                    pass

    def _verify_target_sources(
        self,
        target_years: Sequence[int],
        require_verified_hashes: bool,
        allow_candidate_hashes: bool,
    ) -> BatchVerificationResult:
        """Verify all target years fail-closed."""
        results = {}
        total_bytes = 0
        all_present = True
        all_sizes = True
        all_verified = True
        has_candidates = False

        for yr in target_years:
            res = self.source_validator.verify_source(yr, compute_hash=True, fail_fast=True)
            results[yr] = res
            if res.actual_byte_size is not None:
                total_bytes += res.actual_byte_size

            if res.state == VerificationState.LOCAL_HASH_VERIFIED:
                pass
            elif res.state == VerificationState.LOCAL_HASH_COMPUTED_UNAPPROVED:
                has_candidates = True
                all_verified = False
                if require_verified_hashes and not allow_candidate_hashes:
                    raise RuntimeError(
                        f"Source for year {yr} has unapproved candidate hash ({res.computed_sha256}), "
                        "but require_verified_hashes=True and allow_candidate_hashes=False."
                    )
            else:
                all_verified = False
                raise RuntimeError(
                    f"Source verification failed for year {yr}: state={res.state.value}, error={res.error_message}"
                )

        return BatchVerificationResult(
            results=results,
            all_present=all_present,
            all_sizes_match=all_sizes,
            all_hashes_verified=all_verified,
            total_actual_bytes=total_bytes,
            upstream_identity_status=UPSTREAM_IDENTITY_STATUS_UNVERIFIED,
            has_unapproved_candidate_hashes=has_candidates,
        )
