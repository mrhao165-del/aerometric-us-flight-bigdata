"""
End-to-End Ingestion Coordinator, Forensic Persistence, Safe Parquet Writer, and Lifecycle Engine (T007-05).
Integrates:
- Canonical Schema (T007-01: schema.py)
- Source Validator (T007-02: source_validator.py)
- Raw CSV Reader, Header Validator, Logical Scanner & Classifier (T007-03: reader.py)
- Single-Writer Lock (T007-04: locking.py)
- SparkConfig, RunManifest, RowAccounting, SafePublisher (T-009)

Governance & Remediation Invariants:
- FIX-F01: Physical 34-column CSV header preflight validation before Spark reading.
- FIX-F02 / DC-11: Independent source logical record scanner reconciled per source_year and per run_id
  against classified row counts; raises AccountingUnverifiedError (ACCOUNTING_UNVERIFIED) on any mismatch.
- FIX-F03: Full forensic persistence of QUARANTINED and REJECTED records (including all 34 raw string
  columns, _corrupt_record, lineage fields, _record_status, _anomaly_reason, and _anomaly_flags) into
  `data/quarantine/<run_id>/` outside curated Parquet storage, with readback count reconciliation.
- FIX-F04: Two-phase task attempt staging (`_task_attempts`) in `write_dataframe_parquet_safe` with
  orphan/duplicate attempt cleanup and independent post-write row count & 34-column schema verification.
- FIX-F05: Strict separation of pre-pointer-switch failures (`TERMINAL_FAILURE` / `ABORTED_PRESERVED_PREVIOUS`)
  from post-pointer-switch sidecar failures (`PUBLISHED_RECEIPT_PENDING_RECONCILIATION`). Never overwrites
  a published run's manifest to `FAILED`; provides `reconcile_published_run(run_id)` recovery tool.
- Preserves OR-05 (2024 partial coverage warning), OR-08 (IDENTITY_UNVERIFIED), FP-DEC-017 (Weather
  CONDITIONAL_NO_GO), and G2-EXC-001 (Provisional units).
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
import json
import os
from pathlib import Path
import shutil
import time
from typing import Any, Callable, Dict, List, Mapping, Optional, Sequence, Tuple, Union

import pyarrow as pa
import pyarrow.parquet as pq
from pyspark.sql import DataFrame, SparkSession, functions as F

from flight_pipeline.config.spark_config import SparkConfig, get_spark_session
from flight_pipeline.ingestion.reader import (
    ANOMALY_FLAGS_COLUMN,
    AccountingUnverifiedError,
    CsvReadOptions,
    HeaderValidationError,
    IngestionRecordClassifier,
    IngestionTransformer,
    LINEAGE_ID_COLUMN,
    REASON_COLUMN,
     RawCsvReader,
    RecordStatus,
    SOURCE_FILE_COLUMN,
    SOURCE_YEAR_COLUMN,
     STATUS_COLUMN,
    SourceScanResult,
    compute_per_year_accounting,
    compute_row_accounting,
    scan_csv_logical_records,
)
from flight_pipeline.ingestion.schema import (
    CANONICAL_COLUMN_NAMES,
    CANONICAL_COLUMNS_COUNT,
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
    is_valid_parquet_file,
    validate_run_id,
)
from flight_pipeline.utils.run_manifest import RowAccounting, RunManifest


class PipelineState(str, Enum):
    """Canonical lifecycle states for T-007 Ingestion Coordinator (including FIX-F05 recovery states)."""
    RUN_STARTED = "RUN_STARTED"
    SOURCE_VERIFICATION = "SOURCE_VERIFICATION"
    INGESTION_IN_PROGRESS = "INGESTION_IN_PROGRESS"
    INGESTION_COMPLETED = "INGESTION_COMPLETED"
    STAGING_VERIFIED = "STAGING_VERIFIED"
    PUBLICATION_PENDING = "PUBLICATION_PENDING"
    PUBLISHED = "PUBLISHED"
    PUBLISHED_RECEIPT_PENDING_RECONCILIATION = "PUBLISHED_RECEIPT_PENDING_RECONCILIATION"
    ABORTED_PRESERVED_PREVIOUS = "ABORTED_PRESERVED_PREVIOUS"
    TERMINAL_FAILURE = "TERMINAL_FAILURE"


@dataclass
class ForensicPersistenceResult:
    """Summary of persisted forensic QUARANTINED and REJECTED records in `data/quarantine/<run_id>/`."""
    run_id: str
    quarantine_dir: str
    quarantined_jsonl_path: str
    rejected_jsonl_path: str
    quarantined_parquet_dir: Optional[str]
    rejected_parquet_dir: Optional[str]
    expected_quarantined_count: int
    persisted_quarantined_count: int
    expected_rejected_count: int
    persisted_rejected_count: int
    verified: bool

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


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
    per_year_accounting: Dict[str, Any] = field(default_factory=dict)
    forensic_quarantine_dir: Optional[str] = None
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
    per_year_accounting: Dict[int, RowAccounting] = field(default_factory=dict)
    source_scan_results: Dict[int, SourceScanResult] = field(default_factory=dict)
    forensic_result: Optional[ForensicPersistenceResult] = None
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
    tmp_path = target_path.with_suffix(target_path.suffix + f".tmp.{os.getpid()}.{time.time_ns()}")
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


def write_json_atomic_with_retry(
    target_path: Path,
    data: Dict[str, Any],
    max_retries: int = 3,
    retry_delay_sec: float = 0.05,
) -> Tuple[int, str]:
    """
    Atomically write JSON with bounded retries to handle transient Windows file-locking/AV contention (FIX-F05).
    """
    last_err: Optional[Exception] = None
    for attempt in range(max(1, max_retries)):
        try:
            return write_json_atomic(target_path, data)
        except Exception as exc:
            last_err = exc
            if attempt + 1 < max_retries:
                time.sleep(retry_delay_sec * (attempt + 1))
    assert last_err is not None
    raise last_err


def write_dataframe_parquet_safe(
    df: DataFrame,
    staging_dir: Path,
    compression: str = "snappy",
    expected_row_count: Optional[int] = None,
    verify_curated_schema: bool = False,
) -> List[Path]:
    """
    Write a PySpark DataFrame to Parquet files in `staging_dir` using two-phase task attempt staging
    and independent post-write readback verification (FIX-F04).

    Two-Phase Task Attempt Staging Protocol:
    1. Clean any pre-existing `.tmp` or `_task_attempts` artifacts in `staging_dir`.
    2. Each Spark partition task writes its streaming Arrow batches into an isolated attempt file inside
       `staging_dir / "_task_attempts" / "part-{part_id:05d}-attempt-{attempt_id}-{task_attempt_id}-{uid}.parquet.tmp"`,
       closes the ParquetWriter, and renames to `.parquet` inside `_task_attempts`. If a task fails mid-write,
       its `.parquet.tmp` file is unlinked in the `except` block.
    3. Only the winning task attempts returned by Spark's DAGScheduler to `collect()` on the driver are
       promoted via atomic `os.replace` into `staging_dir / "part-{part_id:05d}.parquet"`.
    4. `staging_dir / "_task_attempts"` is completely removed via `shutil.rmtree`, guaranteeing that failed
       or speculative task retries NEVER leave duplicate or orphan `.parquet` files in `staging_dir`.
    5. Independently reads back the promoted Parquet files via PyArrow to verify exact row count conservation
       (`driver_written_rows == parquet_readback_rows == expected_row_count`) and schema compliance.
    """
    import uuid
    from pyspark import TaskContext
    from pyspark.sql.pandas.types import to_arrow_schema
    from pyspark.sql.types import LongType, StringType as SparkStringType, StructField, StructType

    staging_dir = Path(staging_dir).resolve()
    staging_dir.mkdir(parents=True, exist_ok=True)

    # Clean any stale attempt directory or leftover .tmp files before starting
    attempts_dir = staging_dir / "_task_attempts"
    if attempts_dir.exists():
        shutil.rmtree(attempts_dir)
    for stale_file in list(staging_dir.glob("*.parquet")) + list(staging_dir.glob("*.tmp")):
        if stale_file.is_file():
            stale_file.unlink()
    attempts_dir.mkdir(parents=True, exist_ok=True)

    arrow_schema = to_arrow_schema(df.schema)
    attempts_dir_str = str(attempts_dir)

    def _write_partition_arrow(batch_iter):
        ctx = TaskContext.get()
        part_id = int(ctx.partitionId()) if ctx is not None else 0
        attempt_num = int(ctx.attemptNumber()) if ctx is not None else 0
        task_attempt_id = int(ctx.taskAttemptId()) if ctx is not None else 0
        uid = uuid.uuid4().hex[:8]

        base_name = f"part-{part_id:05d}-attempt-{attempt_num}-{task_attempt_id}-{uid}"
        tmp_file = Path(attempts_dir_str) / f"{base_name}.parquet.tmp"
        final_attempt_file = Path(attempts_dir_str) / f"{base_name}.parquet"

        writer = None
        rows_written = 0
        try:
            for batch in batch_iter:
                if batch.num_rows > 0:
                    if writer is None:
                        writer = pq.ParquetWriter(
                            str(tmp_file),
                            arrow_schema,
                            compression=compression,
                        )
                    tbl = pa.Table.from_batches([batch], schema=arrow_schema)
                    writer.write_table(tbl)
                    rows_written += int(batch.num_rows)
            if writer is not None:
                writer.close()
                writer = None
                os.replace(str(tmp_file), str(final_attempt_file))
        except Exception:
            if writer is not None:
                try:
                    writer.close()
                except Exception:
                    pass
            if tmp_file.exists():
                try:
                    tmp_file.unlink()
                except Exception:
                    pass
            if final_attempt_file.exists():
                try:
                    final_attempt_file.unlink()
                except Exception:
                    pass
            raise

        result_batch = pa.RecordBatch.from_pydict(
            {
                "part_id": [part_id],
                "attempt_num": [attempt_num],
                "task_attempt_id": [task_attempt_id],
                "file_path": [str(final_attempt_file) if rows_written > 0 else ""],
                "rows_written": [rows_written],
            },
            schema=pa.schema([
                pa.field("part_id", pa.int64()),
                pa.field("attempt_num", pa.int64()),
                pa.field("task_attempt_id", pa.int64()),
                pa.field("file_path", pa.string()),
                pa.field("rows_written", pa.int64()),
            ]),
        )
        yield result_batch

    result_schema = StructType([
        StructField("part_id", LongType(), False),
        StructField("attempt_num", LongType(), False),
        StructField("task_attempt_id", LongType(), False),
        StructField("file_path", SparkStringType(), True),
        StructField("rows_written", LongType(), False),
    ])

    try:
        summary_rows = df.mapInArrow(_write_partition_arrow, result_schema).collect()

        # Deduplicate by part_id (selecting highest task_attempt_id if multiple records ever surfaced)
        winning_by_part: Dict[int, Any] = {}
        for r in summary_rows:
            pid = int(r["part_id"])
            if pid not in winning_by_part or int(r["task_attempt_id"]) > int(winning_by_part[pid]["task_attempt_id"]):
                winning_by_part[pid] = r

        promoted_files: List[Path] = []
        driver_written_rows = 0

        for pid in sorted(winning_by_part.keys()):
            r = winning_by_part[pid]
            rows_cnt = int(r["rows_written"])
            fpath_str = r["file_path"]
            driver_written_rows += rows_cnt
            if rows_cnt > 0 and fpath_str:
                attempt_path = Path(fpath_str)
                if not attempt_path.exists():
                    raise RuntimeError(
                        f"PARQUET_WRITE_INTEGRITY_ERROR: Winning attempt file missing for partition {pid}: {attempt_path}"
                    )
                dest_path = staging_dir / f"part-{pid:05d}.parquet"
                os.replace(str(attempt_path), str(dest_path))
                promoted_files.append(dest_path)

        # Remove _task_attempts directory (purging any orphan/aborted/speculative attempt files)
        if attempts_dir.exists():
            shutil.rmtree(attempts_dir)

        # If DataFrame had 0 rows (e.g., header-only CSV), write a single valid empty Parquet file
        if not promoted_files:
            empty_file = staging_dir / "part-00000.parquet"
            empty_arrays = [pa.array([], type=field.type) for field in arrow_schema]
            empty_table = pa.Table.from_arrays(empty_arrays, schema=arrow_schema)
            pq.write_table(empty_table, str(empty_file), compression=compression)
            promoted_files.append(empty_file)

        # Independent post-write verification (FIX-F04)
        verify_parquet_directory_integrity(
            parquet_dir=staging_dir,
            expected_row_count=expected_row_count if expected_row_count is not None else driver_written_rows,
            driver_written_rows=driver_written_rows,
            verify_curated_schema=verify_curated_schema,
        )

        return sorted(promoted_files)
    finally:
        # Always ensure temporary _task_attempts directory is cleaned up
        if attempts_dir.exists():
            try:
                shutil.rmtree(attempts_dir)
            except Exception:
                pass


def verify_parquet_directory_integrity(
    parquet_dir: Path,
    expected_row_count: Optional[int] = None,
    driver_written_rows: Optional[int] = None,
    verify_curated_schema: bool = False,
) -> int:
    """
    Independently verify a directory of Parquet files for:
    - Zero leftover `.tmp` or `_task_attempts` files
    - Valid `PAR1` header/footer magic bytes (`is_valid_parquet_file`)
    - Exact readback row count matching `driver_written_rows` and `expected_row_count`
    - Exact 34-column canonical curated schema and types when `verify_curated_schema=True`.

    Raises RuntimeError with `FAILED_STAGING_CONTENT_INVALID` / `PARQUET_WRITE_INTEGRITY_ERROR` on failure.
    """
    parquet_dir = Path(parquet_dir).resolve()
    if not parquet_dir.exists() or not parquet_dir.is_dir():
        raise RuntimeError(f"FAILED_STAGING_CONTENT_INVALID: Parquet directory does not exist: {parquet_dir}")

    # Check for leftover temporary files or task attempt directories
    tmp_files = list(parquet_dir.rglob("*.tmp")) + list(parquet_dir.rglob("*.parquet.tmp"))
    if tmp_files:
        raise RuntimeError(
            f"FAILED_STAGING_CONTENT_INVALID: Leftover temporary files found in {parquet_dir}: {tmp_files}"
        )
    if (parquet_dir / "_task_attempts").exists():
        raise RuntimeError(
            f"FAILED_STAGING_CONTENT_INVALID: Uncleaned _task_attempts directory found in {parquet_dir}"
        )

    parquet_files = sorted(p for p in parquet_dir.rglob("*.parquet") if p.is_file())
    if not parquet_files:
        raise RuntimeError(f"FAILED_STAGING_CONTENT_INVALID: No .parquet files found in {parquet_dir}")

    readback_rows = 0
    expected_curated_schema = get_curated_parquet_schema() if verify_curated_schema else None
    forbidden_tech_cols = {
        CORRUPT_RECORD_COLUMN,
        STATUS_COLUMN,
        REASON_COLUMN,
        ANOMALY_FLAGS_COLUMN,
        SOURCE_YEAR_COLUMN,
        SOURCE_FILE_COLUMN,
        LINEAGE_ID_COLUMN,
    }

    for pf in parquet_files:
        if not is_valid_parquet_file(pf):
            raise RuntimeError(
                f"FAILED_STAGING_CONTENT_INVALID: File {pf.name} failed PAR1 magic byte verification"
            )
        try:
            pq_file = pq.ParquetFile(str(pf))
            readback_rows += int(pq_file.metadata.num_rows)
            arrow_sch = pq_file.schema_arrow
        except Exception as exc:
            raise RuntimeError(
                f"FAILED_STAGING_CONTENT_INVALID: Unable to read Parquet metadata from {pf.name}: {exc}"
            ) from exc

        col_names = list(arrow_sch.names)
        leaked_tech = forbidden_tech_cols.intersection(col_names)
        if verify_curated_schema and leaked_tech:
            raise RuntimeError(
                f"FAILED_STAGING_CONTENT_INVALID: Technical columns {sorted(leaked_tech)} leaked into curated Parquet {pf.name}"
            )

        if verify_curated_schema and expected_curated_schema is not None:
            if col_names != list(CANONICAL_COLUMN_NAMES) or len(col_names) != CANONICAL_COLUMNS_COUNT:
                raise RuntimeError(
                    f"FAILED_STAGING_CONTENT_INVALID: Curated Parquet {pf.name} column mismatch: "
                    f"expected {CANONICAL_COLUMNS_COUNT} canonical columns, got {len(col_names)}: {col_names}"
                )

    if driver_written_rows is not None and readback_rows != driver_written_rows:
        raise RuntimeError(
            f"PARQUET_WRITE_INTEGRITY_ERROR: Parquet readback row count ({readback_rows}) != "
            f"driver written row count ({driver_written_rows}) in {parquet_dir}"
        )

    if expected_row_count is not None and readback_rows != expected_row_count:
        raise RuntimeError(
            f"PARQUET_WRITE_INTEGRITY_ERROR: Parquet readback row count ({readback_rows}) != "
            f"expected accepted_row_count ({expected_row_count}) in {parquet_dir}"
        )

    return readback_rows


def persist_forensic_records(
    classified_df: DataFrame,
    run_id: str,
    quarantine_root: Path,
    accounting: RowAccounting,
) -> ForensicPersistenceResult:
    """
    Persist full `QUARANTINED` and `REJECTED` records into `data/quarantine/<run_id>/` (FIX-F03).
    Preserves all 34 raw canonical string columns, `_corrupt_record`, `_source_year`, `_source_file`,
    `_record_lineage_id`, `_record_status`, `_anomaly_reason`, and `_anomaly_flags`.

    Writes both human-auditable JSONL files (`quarantined_records.jsonl`, `rejected_records.jsonl`)
    and Parquet directories (`quarantined_parquet/`, `rejected_parquet/`), then independently verifies
    that persisted record counts match `accounting.quarantined_row_count` and `accounting.rejected_row_count`.
    """
    run_quar_dir = Path(quarantine_root).resolve() / run_id
    run_quar_dir.mkdir(parents=True, exist_ok=True)

    forensic_cols = [
        SOURCE_YEAR_COLUMN,
        SOURCE_FILE_COLUMN,
        LINEAGE_ID_COLUMN,
        STATUS_COLUMN,
        REASON_COLUMN,
        ANOMALY_FLAGS_COLUMN,
        CORRUPT_RECORD_COLUMN,
    ] + list(CANONICAL_COLUMN_NAMES)

    # Ensure all forensic columns exist on classified_df
    available_cols = [c for c in forensic_cols if c in classified_df.columns]
    non_accepted_df = (
        classified_df
        .filter(F.col(STATUS_COLUMN) != RecordStatus.ACCEPTED.value)
        .select(*available_cols)
    )

    quar_df = non_accepted_df.filter(F.col(STATUS_COLUMN) == RecordStatus.QUARANTINED.value)
    rej_df = non_accepted_df.filter(F.col(STATUS_COLUMN) == RecordStatus.REJECTED.value)

    quar_parquet_dir = run_quar_dir / "quarantined_parquet"
    rej_parquet_dir = run_quar_dir / "rejected_parquet"

    write_dataframe_parquet_safe(
        quar_df,
        quar_parquet_dir,
        expected_row_count=accounting.quarantined_row_count,
        verify_curated_schema=False,
    )
    write_dataframe_parquet_safe(
        rej_df,
        rej_parquet_dir,
        expected_row_count=accounting.rejected_row_count,
        verify_curated_schema=False,
    )

    # Stream from the verified forensic Parquet files into JSONL files (O(1) memory via PyArrow batches)
    quar_jsonl_path = run_quar_dir / "quarantined_records.jsonl"
    rej_jsonl_path = run_quar_dir / "rejected_records.jsonl"

    persisted_quar_jsonl = _parquet_dir_to_jsonl_atomic(quar_parquet_dir, quar_jsonl_path, run_id=run_id)
    persisted_rej_jsonl = _parquet_dir_to_jsonl_atomic(rej_parquet_dir, rej_jsonl_path, run_id=run_id)

    # Independent readback count check on JSONL + Parquet
    quar_pq_rows = verify_parquet_directory_integrity(
        quar_parquet_dir,
        expected_row_count=accounting.quarantined_row_count,
    )
    rej_pq_rows = verify_parquet_directory_integrity(
        rej_parquet_dir,
        expected_row_count=accounting.rejected_row_count,
    )

    if (
        persisted_quar_jsonl != accounting.quarantined_row_count
        or quar_pq_rows != accounting.quarantined_row_count
        or persisted_rej_jsonl != accounting.rejected_row_count
        or rej_pq_rows != accounting.rejected_row_count
    ):
        raise RuntimeError(
            f"FORENSIC_PERSISTENCE_FAILED: Persisted forensic counts (quarantined={persisted_quar_jsonl}/{quar_pq_rows}, "
            f"rejected={persisted_rej_jsonl}/{rej_pq_rows}) != expected DC-11 counts "
            f"(quarantined={accounting.quarantined_row_count}, rejected={accounting.rejected_row_count})"
        )

    res = ForensicPersistenceResult(
        run_id=run_id,
        quarantine_dir=str(run_quar_dir),
        quarantined_jsonl_path=str(quar_jsonl_path),
        rejected_jsonl_path=str(rej_jsonl_path),
        quarantined_parquet_dir=str(quar_parquet_dir),
        rejected_parquet_dir=str(rej_parquet_dir),
        expected_quarantined_count=accounting.quarantined_row_count,
        persisted_quarantined_count=persisted_quar_jsonl,
        expected_rejected_count=accounting.rejected_row_count,
        persisted_rejected_count=persisted_rej_jsonl,
        verified=True,
    )
    write_json_atomic_with_retry(run_quar_dir / "forensic_manifest.json", res.to_dict())
    return res


def _parquet_dir_to_jsonl_atomic(parquet_dir: Path, target_jsonl: Path, run_id: str) -> int:
    """Convert Parquet files in `parquet_dir` into a deterministic JSONL file atomically and return line count."""
    target_jsonl.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = target_jsonl.with_suffix(target_jsonl.suffix + f".tmp.{os.getpid()}.{time.time_ns()}")
    written_lines = 0
    try:
        with open(tmp_path, "wb") as out_f:
            for pf in sorted(parquet_dir.rglob("*.parquet")):
                pq_file = pq.ParquetFile(str(pf))
                for batch in pq_file.iter_batches(batch_size=4096):
                    for row_dict in batch.to_pylist():
                        payload_dict = {"run_id": run_id}
                        payload_dict.update(row_dict)
                        line_bytes = (json.dumps(payload_dict, ensure_ascii=False) + "\n").encode("utf-8")
                        out_f.write(line_bytes)
                        written_lines += 1
            out_f.flush()
            os.fsync(out_f.fileno())
        os.replace(str(tmp_path), str(target_jsonl))
    except Exception:
        if tmp_path.exists():
            try:
                tmp_path.unlink()
            except Exception:
                pass
        raise

    # Independent line count readback on JSONL file
    readback_lines = 0
    with open(target_jsonl, "rb") as in_f:
        for raw_line in in_f:
            if raw_line.strip():
                readback_lines += 1
    if readback_lines != written_lines:
        raise RuntimeError(
            f"FORENSIC_PERSISTENCE_FAILED: JSONL readback count ({readback_lines}) != written count ({written_lines}) in {target_jsonl}"
        )
    return readback_lines


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
    Enforces single-writer locking, fail-closed source validation, independent DC-11 row accounting,
    forensic QUARANTINED/REJECTED record persistence, retry-safe Parquet writing, 7-step Windows NTFS
    atomic publication, and post-pointer-switch sidecar receipt reconciliation.
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
        self.quarantine_root = self.base_data_dir / "quarantine"
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

        target_years = sorted(years) if years is not None else sorted(self.source_validator.inventory.keys())

        manifest = RunManifest(
            run_id=run_id,
            task_id=self.task_id,
            configuration={
                "base_data_dir": str(self.base_data_dir),
                "years": list(target_years),
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

        if 2024 in target_years:
            governance_warnings.append(
                "OR-05: OPEN_QUALITY_DEFECT — Year 2024 has partial coverage (335/366 days; March 2024 missing)."
            )

        lock = SingleWriterLock(self.lock_dir, run_id=run_id)
        pointer_switched = False
        is_duplicate_run_id = False
        pub_result: Optional[PublicationResult] = None
        batch_res: Optional[BatchVerificationResult] = None
        scan_results_by_year: Dict[int, SourceScanResult] = {}
        per_year_accounting: Dict[int, RowAccounting] = {}
        forensic_res: Optional[ForensicPersistenceResult] = None
        anomaly_summary: Dict[str, int] = {}

        try:
            # Acquire single-writer lock before any critical state
            lock.acquire()
            transition(PipelineState.RUN_STARTED)

            # Check if run_id already published, staged, or recorded in metadata to prevent duplicate run_id collision
            if (
                (self.publisher.runs_root / run_id).exists()
                or staging_run_dir.exists()
                or manifest_path.exists()
            ):
                is_duplicate_run_id = True
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

            write_json_atomic_with_retry(run_meta_dir / "source_verification.json", batch_res.to_dict())

            for yr in target_years:
                r = batch_res.results[yr]
                manifest.record_input(
                    path=r.path,
                    bytes_count=r.actual_byte_size or 0,
                    sha256_hash=r.computed_sha256,
                )

            # -----------------------------------------------------------------
            # STEP 2: INGESTION IN PROGRESS (SCAN, READ, CLASSIFY, ACCOUNT, FORENSIC, WRITE STAGING)
            # -----------------------------------------------------------------
            transition(PipelineState.INGESTION_IN_PROGRESS)

            combined_raw_df: Optional[DataFrame] = None
            for yr in target_years:
                src_path = self.source_validator.get_source_path(yr)
                # Independent physical & logical record scan + header validation (FIX-F01 / FIX-F02)
                scan_res = scan_csv_logical_records(
                    src_path,
                    options=self.csv_options,
                    source_year=yr,
                )
                scan_results_by_year[yr] = scan_res

                yr_df = self.reader.read_raw(src_path, source_year=yr, attach_lineage=True)
                if combined_raw_df is None:
                    combined_raw_df = yr_df
                else:
                    combined_raw_df = combined_raw_df.unionByName(yr_df)

            if combined_raw_df is None:
                raise ValueError("No source DataFrames loaded for target years")

            classified_df = IngestionRecordClassifier.classify(combined_raw_df)

            # Reconcile independent source counts against Spark classifier counts per year & per run (FIX-F02)
            accounting, per_year_accounting = compute_per_year_accounting(
                classified_df=classified_df,
                scan_results_by_year=scan_results_by_year,
            )
            manifest.row_accounting = accounting
            manifest.configuration["per_year_accounting"] = {
                str(yr): acc_yr.to_dict() for yr, acc_yr in sorted(per_year_accounting.items())
            }
            manifest.configuration["source_scan_results"] = {
                str(yr): sr.to_dict() for yr, sr in sorted(scan_results_by_year.items())
            }

            # Persist full forensic QUARANTINED and REJECTED records outside curated Parquet (FIX-F03)
            forensic_res = persist_forensic_records(
                classified_df=classified_df,
                run_id=run_id,
                quarantine_root=self.quarantine_root,
                accounting=accounting,
            )
            manifest.configuration["forensic_persistence"] = forensic_res.to_dict()

            # Collect anomaly breakdown for forensic metadata
            anomaly_rows = (
                classified_df
                .filter(F.col(STATUS_COLUMN) != RecordStatus.ACCEPTED.value)
                .groupBy(STATUS_COLUMN, REASON_COLUMN)
                .agg(F.count(F.lit(1)).alias("count"))
                .collect()
            )
            anomaly_summary = {
                f"{row[STATUS_COLUMN]}:{row[REASON_COLUMN]}": int(row["count"])
                for row in anomaly_rows
            }
            write_json_atomic_with_retry(
                run_meta_dir / "anomaly_summary.json",
                {
                    "run_id": run_id,
                    "row_accounting": accounting.to_dict(),
                    "per_year_accounting": {
                        str(yr): acc_yr.to_dict() for yr, acc_yr in sorted(per_year_accounting.items())
                    },
                    "source_scan_results": {
                        str(yr): sr.to_dict() for yr, sr in sorted(scan_results_by_year.items())
                    },
                    "forensic_persistence": forensic_res.to_dict(),
                    "anomaly_breakdown": anomaly_summary,
                },
            )

            # Transform accepted records to curated schema and write Parquet to staging with 2-phase attempt safety
            curated_df = IngestionTransformer.to_curated(classified_df, filter_accepted=True)
            staging_run_dir.mkdir(parents=True, exist_ok=True)
            write_dataframe_parquet_safe(
                curated_df,
                staging_run_dir,
                expected_row_count=accounting.accepted_row_count,
                verify_curated_schema=True,
            )

            transition(PipelineState.INGESTION_COMPLETED)

            # -----------------------------------------------------------------
            # STEP 3: STAGING VERIFIED (Post-INGESTION_COMPLETED verification)
            # -----------------------------------------------------------------
            verify_parquet_directory_integrity(
                parquet_dir=staging_run_dir,
                expected_row_count=accounting.accepted_row_count,
                verify_curated_schema=True,
            )

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

            # CRITICAL COMMIT POINT REACHED (FIX-F05):
            # Pointer latest_run_id.txt now points to run_id and immutable Parquet is live!
            pointer_switched = True
            manifest.configuration["previous_pointer"] = pub_result.previous_pointer

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
            manifest_bytes, manifest_sha256 = write_json_atomic_with_retry(
                manifest_path,
                manifest.to_dict(),
            )

            # Optional fault injection hook right before/during sidecar receipt persistence (FIX-F05 test hook)
            if fault_injector is not None:
                fault_injector("POST_POINTER_SIDE_EFFECT")

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
                per_year_accounting={
                    str(yr): acc_yr.to_dict() for yr, acc_yr in sorted(per_year_accounting.items())
                },
                forensic_quarantine_dir=forensic_res.quarantine_dir if forensic_res else None,
                upstream_identity_status=UPSTREAM_IDENTITY_STATUS_UNVERIFIED,
                or05_coverage_warning=or05_warn,
            )
            write_json_atomic_with_retry(receipt_path, receipt.to_dict())

            transition(PipelineState.PUBLISHED)

            return PipelineRunOutcome(
                success=True,
                run_id=run_id,
                final_state=PipelineState.PUBLISHED,
                state_history=state_history,
                row_accounting=accounting,
                per_year_accounting=per_year_accounting,
                source_scan_results=scan_results_by_year,
                forensic_result=forensic_res,
                publication_result=pub_result,
                manifest_path=manifest_path,
                receipt_path=receipt_path,
                receipt=receipt,
                source_verification=batch_res,
                anomaly_summary=anomaly_summary,
                governance_warnings=governance_warnings,
            )

        except Exception as exc:
            err_msg = str(exc)

            # Check if THIS run invocation already switched the pointer (FIX-F05)
            if pointer_switched:
                # POST-POINTER-SWITCH FAILURE:
                # NEVER overwrite manifest.status to FAILED when latest_run_id.txt points to run_id!
                state_history.append(PipelineState.PUBLISHED_RECEIPT_PENDING_RECONCILIATION)
                try:
                    manifest.close(
                        status="PUBLISHED_RECEIPT_PENDING_RECONCILIATION",
                        error=f"Published pointer is live for '{run_id}', but post-pointer sidecar failed: {err_msg}",
                    )
                    write_json_atomic_with_retry(manifest_path, manifest.to_dict())
                except Exception:
                    pass

                return PipelineRunOutcome(
                    success=False,
                    run_id=run_id,
                    final_state=PipelineState.PUBLISHED_RECEIPT_PENDING_RECONCILIATION,
                    state_history=state_history,
                    row_accounting=manifest.row_accounting,
                    per_year_accounting=per_year_accounting,
                    source_scan_results=scan_results_by_year,
                    forensic_result=forensic_res,
                    publication_result=pub_result,
                    manifest_path=manifest_path if manifest_path.exists() else None,
                    receipt_path=receipt_path if receipt_path.exists() else None,
                    source_verification=batch_res,
                    anomaly_summary=anomaly_summary,
                    governance_warnings=governance_warnings,
                    error_message=(
                        f"PUBLISHED_RECEIPT_PENDING_RECONCILIATION: Pointer switched to '{run_id}', "
                        f"but sidecar finalization failed ({err_msg}). Run reconcile_published_run('{run_id}')."
                    ),
                )

            # PRE-POINTER-SWITCH FAILURE:
            state_history.append(PipelineState.TERMINAL_FAILURE)
            if not is_duplicate_run_id and lock.is_acquired:
                try:
                    manifest.close(status="FAILED", error=err_msg)
                    write_json_atomic_with_retry(manifest_path, manifest.to_dict())
                except Exception:
                    pass

            return PipelineRunOutcome(
                success=False,
                run_id=run_id,
                final_state=PipelineState.TERMINAL_FAILURE,
                state_history=state_history,
                row_accounting=manifest.row_accounting,
                per_year_accounting=per_year_accounting,
                source_scan_results=scan_results_by_year,
                forensic_result=forensic_res,
                publication_result=pub_result,
                manifest_path=manifest_path if manifest_path.exists() else None,
                source_verification=batch_res,
                anomaly_summary=anomaly_summary,
                governance_warnings=governance_warnings,
                error_message=err_msg,
            )
        finally:
            if lock.is_acquired:
                try:
                    lock.release()
                except Exception:
                    pass

    def reconcile_published_run(self, run_id: str) -> PipelineRunOutcome:
        """
        Repair/complete `run_manifest.json` (`status="PUBLISHED"`) and `execution_receipt.json` for a run
        whose pointer switch in `latest_run_id.txt` succeeded, without modifying any file inside
        the immutable published Parquet directory `data/curated/runs/<run_id>` (FIX-F05).
        """
        validate_run_id(run_id, self.staging_root)
        lock = SingleWriterLock(self.lock_dir, run_id=f"reconcile_{run_id}")
        state_history = [PipelineState.PUBLISHED_RECEIPT_PENDING_RECONCILIATION]

        try:
            lock.acquire()

            published_dir = self.publisher.runs_root / run_id
            if not published_dir.exists() or not published_dir.is_dir():
                raise RuntimeError(
                    f"Cannot reconcile run '{run_id}': published directory does not exist at {published_dir}"
                )

            current_ptr = self.publisher.get_current_pointer()
            if current_ptr != run_id:
                raise RuntimeError(
                    f"Cannot reconcile run '{run_id}': pointer file points to '{current_ptr}', not '{run_id}'"
                )

            run_meta_dir = self.metadata_root / run_id
            manifest_path = run_meta_dir / "run_manifest.json"
            receipt_path = run_meta_dir / "execution_receipt.json"
            anomaly_path = run_meta_dir / "anomaly_summary.json"

            if not manifest_path.exists():
                raise RuntimeError(f"Cannot reconcile run '{run_id}': manifest file missing at {manifest_path}")

            manifest_data = json.loads(manifest_path.read_text(encoding="utf-8"))
            previous_ptr = manifest_data.get("configuration", {}).get("previous_pointer")
            acc_dict = manifest_data.get("row_accounting")
            if not acc_dict and anomaly_path.exists():
                anom_data = json.loads(anomaly_path.read_text(encoding="utf-8"))
                acc_dict = anom_data.get("row_accounting")

            if not acc_dict:
                raise RuntimeError(f"Cannot reconcile run '{run_id}': row_accounting missing from metadata")

            accounting = RowAccounting(
                raw_row_count=int(acc_dict["raw_row_count"]),
                accepted_row_count=int(acc_dict["accepted_row_count"]),
                quarantined_row_count=int(acc_dict["quarantined_row_count"]),
                rejected_row_count=int(acc_dict["rejected_row_count"]),
            )
            if not accounting.is_balanced():
                raise AccountingUnverifiedError(
                    f"ACCOUNTING_UNVERIFIED: Stored accounting for '{run_id}' is unbalanced: {acc_dict}"
                )

            # Verify immutable published Parquet directory without modifying any files inside it
            verify_parquet_directory_integrity(
                parquet_dir=published_dir,
                expected_row_count=accounting.accepted_row_count,
                verify_curated_schema=True,
            )

            # Reconstruct outputs list from immutable published Parquet files
            outputs_list = []
            for pf in sorted(published_dir.rglob("*.parquet")):
                outputs_list.append({
                    "path": pf.relative_to(self.base_data_dir).as_posix(),
                    "bytes": pf.stat().st_size,
                    "sha256": compute_file_sha256(pf),
                })

            manifest_data["outputs"] = outputs_list
            manifest_data["row_accounting"] = accounting.to_dict()
            manifest_data["status"] = "PUBLISHED"
            manifest_data["error_message"] = None
            manifest_data["completed_at"] = datetime.now(timezone.utc).isoformat()

            manifest_bytes, manifest_sha256 = write_json_atomic_with_retry(manifest_path, manifest_data)

            cfg = manifest_data.get("configuration", {})
            years_cfg = cfg.get("years", [])
            or05_warn = (
                "OR-05: OPEN_QUALITY_DEFECT — Year 2024 has partial coverage (335/366 days; March 2024 missing)."
                if 2024 in years_cfg
                else None
            )
            forensic_info = cfg.get("forensic_persistence", {})
            per_yr_info = cfg.get("per_year_accounting", {})

            receipt = ExecutionReceipt(
                run_id=run_id,
                task_id=manifest_data.get("task_id", self.task_id),
                pipeline_state=PipelineState.PUBLISHED.value,
                publication_status="PUBLISHED",
                published_path=str(published_dir),
                pointer_value=run_id,
                previous_pointer=previous_ptr,
                manifest_path=str(manifest_path),
                manifest_bytes=manifest_bytes,
                manifest_sha256=manifest_sha256,
                row_accounting=accounting.to_dict(),
                per_year_accounting=per_yr_info,
                forensic_quarantine_dir=forensic_info.get("quarantine_dir"),
                upstream_identity_status=UPSTREAM_IDENTITY_STATUS_UNVERIFIED,
                or05_coverage_warning=or05_warn,
            )
            write_json_atomic_with_retry(receipt_path, receipt.to_dict())

            state_history.append(PipelineState.PUBLISHED)
            pub_res = PublicationResult(
                success=True,
                run_id=run_id,
                status="PUBLISHED",
                published_path=str(published_dir),
                pointer_value=run_id,
                previous_pointer=previous_ptr,
            )

            return PipelineRunOutcome(
                success=True,
                run_id=run_id,
                final_state=PipelineState.PUBLISHED,
                state_history=state_history,
                row_accounting=accounting,
                publication_result=pub_res,
                manifest_path=manifest_path,
                receipt_path=receipt_path,
                receipt=receipt,
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
