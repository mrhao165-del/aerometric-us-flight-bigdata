"""
Execution run manifest and row accounting model.
Conforms to DATA_CONTRACT.md (DC-11/12) and ARCHITECTURE.md specifications.
Captures cryptographic lineage, runtime environment versions, and row accounting verification.
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
import platform
import sys
from typing import Any, Dict, List, Optional


@dataclass
class RowAccounting:
    """Three-state disjoint row accounting per DATA_CONTRACT.md (DC-11)."""
    raw_row_count: int = 0
    accepted_row_count: int = 0
    quarantined_row_count: int = 0
    rejected_row_count: int = 0

    def __post_init__(self):
        for name in ("raw_row_count", "accepted_row_count", "quarantined_row_count", "rejected_row_count"):
            val = getattr(self, name)
            if not isinstance(val, int) or isinstance(val, bool):
                raise TypeError(f"{name} must be an integer, got {type(val).__name__}")
            if val < 0:
                raise ValueError(f"{name} must be non-negative, got {val}")

    def is_balanced(self) -> bool:
        """Verify the mandatory invariant: raw = accepted + quarantined + rejected with non-negative domains."""
        if (
            self.raw_row_count < 0
            or self.accepted_row_count < 0
            or self.quarantined_row_count < 0
            or self.rejected_row_count < 0
        ):
            return False
        return self.raw_row_count == (
            self.accepted_row_count + self.quarantined_row_count + self.rejected_row_count
        )

    def calculate_ingest_acceptance_rate(self) -> Optional[float]:
        """
        Calculate ingest acceptance rate = accepted_row_count / raw_row_count (DC-12).
        Returns None when raw_row_count == 0 to handle ZERO_DENOMINATOR cleanly.
        """
        if self.raw_row_count <= 0:
            return None
        if not (0 <= self.accepted_row_count <= self.raw_row_count):
            return None
        return self.accepted_row_count / self.raw_row_count

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["is_balanced"] = self.is_balanced()
        d["ingest_acceptance_rate"] = self.calculate_ingest_acceptance_rate()
        return d


@dataclass
class MetricAccounting:
    """
    Per-submetric accounting per DATA_CONTRACT.md (DC-12).
    Evaluated on accepted records for a specific submetric cohort.
    """
    metric_name: str
    count_records: int = 0
    count_metric_valid: int = 0

    def __post_init__(self):
        for name in ("count_records", "count_metric_valid"):
            val = getattr(self, name)
            if not isinstance(val, int) or isinstance(val, bool):
                raise TypeError(f"{name} must be an integer, got {type(val).__name__}")
            if val < 0:
                raise ValueError(f"{name} must be non-negative, got {val}")
        if self.count_metric_valid > self.count_records:
            raise ValueError(
                f"count_metric_valid ({self.count_metric_valid}) cannot exceed count_records ({self.count_records})"
            )

    @property
    def excluded_count(self) -> int:
        """Excluded count = count_records - count_metric_valid (DC-12)."""
        diff = self.count_records - self.count_metric_valid
        return max(0, diff) if self.count_records >= 0 else 0

    def calculate_metric_valid_rate(self) -> Optional[float]:
        """
        Calculate metric valid rate = count_metric_valid / count_records when count_records > 0 (DC-12).
        Returns None when count_records == 0 (ZERO_DENOMINATOR rule, not 0.0) or invalid.
        """
        if self.count_records <= 0:
            return None
        if not (0 <= self.count_metric_valid <= self.count_records):
            return None
        return self.count_metric_valid / self.count_records

    def to_dict(self) -> Dict[str, Any]:
        return {
            "metric_name": self.metric_name,
            "count_records": self.count_records,
            "count_metric_valid": self.count_metric_valid,
            "excluded_count": self.excluded_count,
            "metric_valid_rate": self.calculate_metric_valid_rate(),
        }


@dataclass
class RunManifest:
    """Execution run manifest capturing audit lineage, environment, and accounting."""
    run_id: str
    task_id: str
    status: str = "IN_PROGRESS"
    start_time: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    end_time: Optional[str] = None
    runtime_versions: Dict[str, str] = field(default_factory=dict)
    configuration: Dict[str, Any] = field(default_factory=dict)
    inputs: List[Dict[str, Any]] = field(default_factory=list)
    outputs: List[Dict[str, Any]] = field(default_factory=list)
    row_accounting: Optional[RowAccounting] = None
    error_info: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        if not self.runtime_versions:
            self.runtime_versions = self._detect_runtime_versions()

    @staticmethod
    def _detect_runtime_versions() -> Dict[str, str]:
        """Collect current host runtime versions accurately."""
        versions = {
            "python": sys.version.split()[0],
            "os": platform.platform(),
            "architecture": platform.machine(),
        }
        try:
            import pyspark
            versions["pyspark"] = pyspark.__version__
        except ImportError:
            versions["pyspark"] = "NOT_INSTALLED"
        try:
            import pyarrow
            versions["pyarrow"] = pyarrow.__version__
        except ImportError:
            versions["pyarrow"] = "NOT_INSTALLED"
        return versions

    def record_input(self, path: str, bytes_count: int, sha256_hash: Optional[str] = None) -> None:
        """Record an audited input source file."""
        self.inputs.append({
            "path": path,
            "bytes": bytes_count,
            "sha256": sha256_hash or "UNVERIFIED",
        })

    def record_output(self, path: str, bytes_count: int, sha256_hash: Optional[str] = None) -> None:
        """Record an output artifact."""
        self.outputs.append({
            "path": path,
            "bytes": bytes_count,
            "sha256": sha256_hash or "PENDING",
        })

    def close(self, status: str = "SUCCESS", error: Optional[str] = None) -> None:
        """Mark run completion with final status, timestamp, and optional error info."""
        self.status = status
        self.end_time = datetime.now(timezone.utc).isoformat()
        if error:
            self.error_info = {"error_message": error, "timestamp": self.end_time}

    def to_dict(self) -> Dict[str, Any]:
        data = {
            "run_id": self.run_id,
            "task_id": self.task_id,
            "status": self.status,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "runtime_versions": self.runtime_versions,
            "configuration": self.configuration,
            "inputs": self.inputs,
            "outputs": self.outputs,
            "row_accounting": self.row_accounting.to_dict() if self.row_accounting else None,
            "error_info": self.error_info,
        }
        return data

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)

    def to_bytes(self) -> bytes:
        """Canonical byte representation of the manifest."""
        return (self.to_json() + "\n").encode("utf-8")

    def calculate_sha256(self) -> str:
        """Calculate SHA-256 hash of the canonical manifest bytes."""
        return sha256(self.to_bytes()).hexdigest()

    def save(self, target_path: str) -> str:
        """Save manifest JSON to file and return its exact disk SHA-256 hash."""
        p = Path(target_path)
        p.parent.mkdir(parents=True, exist_ok=True)
        data = self.to_bytes()
        p.write_bytes(data)
        return sha256(data).hexdigest()
