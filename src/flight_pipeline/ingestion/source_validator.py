"""
Source inventory and streaming SHA-256 hash verifier module for raw CSV flight datasets.
Conforms to DATA_CONTRACT.md, ARCHITECTURE.md, T007-02 specifications, and T007_02A_HANDOFF_ERRATA.md.

Governance Invariants:
- OR-08 / TS-019: Upstream identity status is strictly IDENTITY_UNVERIFIED. Local hash verifies snapshot
  integrity only and does not prove BTS TranStats or NOAA provenance.
- DOC-F01: SOURCE_MANIFEST.json tracks audit documentation, NOT raw CSV checksums.
- DOC-F02: Integration with RunManifest uses record_input(path, bytes_count, sha256_hash).
- FP-DEC-014: Size and modification timestamps do not prove content identity; streaming SHA-256 is required.
"""

from dataclasses import dataclass, field, asdict
from enum import Enum
import hashlib
import os
from pathlib import Path
import stat
from typing import Any, Dict, List, Mapping, Optional, Set, Tuple, Union

# Upstream identity invariant (OR-08 / TS-019)
UPSTREAM_IDENTITY_STATUS_UNVERIFIED: str = "IDENTITY_UNVERIFIED"

# Default streaming buffer chunk size: 1 MiB (1,048,576 bytes)
DEFAULT_HASH_CHUNK_SIZE: int = 1024 * 1024


class VerificationState(str, Enum):
    """
    Mutually exclusive verification states for raw source files.
    Distinguishes metadata matching, unapproved candidate hashes, and verified hashes.
    """
    SOURCE_PRESENT_METADATA_MATCH = "SOURCE_PRESENT_METADATA_MATCH"
    LOCAL_HASH_COMPUTED_UNAPPROVED = "LOCAL_HASH_COMPUTED_UNAPPROVED"
    LOCAL_HASH_VERIFIED = "LOCAL_HASH_VERIFIED"
    SOURCE_MISSING = "SOURCE_MISSING"
    SIZE_MISMATCH = "SIZE_MISMATCH"
    HASH_MISMATCH = "HASH_MISMATCH"
    SOURCE_READ_ERROR = "SOURCE_READ_ERROR"
    SOURCE_CHANGED_DURING_READ = "SOURCE_CHANGED_DURING_READ"
    BASELINE_PENDING_APPROVAL = "BASELINE_PENDING_APPROVAL"


class SourceValidatorError(Exception):
    """Base exception for source validation errors."""
    pass


class SourceNotFoundError(SourceValidatorError, FileNotFoundError):
    """Raised when an expected raw source file is missing."""
    pass


class SourceIntegrityError(SourceValidatorError):
    """Base exception for integrity violations (size, hash, race conditions)."""
    pass


class SourceSizeMismatchError(SourceIntegrityError):
    """Raised when disk file size does not match audited inventory baseline."""
    pass


class SourceHashMismatchError(SourceIntegrityError):
    """Raised when computed SHA-256 does not match approved baseline hash."""
    pass


class SourceChangedDuringReadError(SourceIntegrityError):
    """Raised when file modification or size change is detected during streaming hash read."""
    pass


class SourcePathSecurityError(SourceValidatorError, ValueError):
    """Raised when path traversal (..), symlink/reparse point, or root escape is detected."""
    pass


class SourcePermissionError(SourceValidatorError, PermissionError):
    """Raised when file read permission is denied."""
    pass


class SourceConfigurationError(SourceValidatorError, ValueError):
    """Raised when inventory configuration or baseline hash format is corrupt or invalid."""
    pass


@dataclass(frozen=True)
class SourceEntry:
    """Audited source file inventory entry."""
    year: int
    relative_path: str
    audited_row_count: int
    audited_byte_size: int
    audited_column_count: int = 34

    def __post_init__(self):
        if not isinstance(self.year, int) or isinstance(self.year, bool):
            raise TypeError(f"year must be an integer, got {type(self.year).__name__}")
        if self.year < 2016 or self.year > 2024:
            raise ValueError(f"year must be within 2016-2024, got {self.year}")
        if not self.relative_path or not isinstance(self.relative_path, str):
            raise ValueError("relative_path must be a non-empty string")
        if not isinstance(self.audited_row_count, int) or self.audited_row_count <= 0:
            raise ValueError(f"audited_row_count must be positive integer, got {self.audited_row_count}")
        if not isinstance(self.audited_byte_size, int) or self.audited_byte_size <= 0:
            raise ValueError(f"audited_byte_size must be positive integer, got {self.audited_byte_size}")
        if self.audited_column_count != 34:
            raise ValueError(f"audited_column_count must be exactly 34, got {self.audited_column_count}")


# Audited 9-year raw CSV inventory baseline per G1 metadata and T007-02 specifications
AUDITED_SOURCE_INVENTORY: Dict[int, SourceEntry] = {
    2016: SourceEntry(
        year=2016,
        relative_path="data/raw/tabular/2016/flight_with_weather_2016.csv",
        audited_row_count=5537987,
        audited_byte_size=1538427452,
        audited_column_count=34,
    ),
    2017: SourceEntry(
        year=2017,
        relative_path="data/raw/tabular/2017/flight_with_weather_2017.csv",
        audited_row_count=5575872,
        audited_byte_size=1549837485,
        audited_column_count=34,
    ),
    2018: SourceEntry(
        year=2018,
        relative_path="data/raw/tabular/2018/flight_with_weather_2018.csv",
        audited_row_count=6986842,
        audited_byte_size=1941406432,
        audited_column_count=34,
    ),
    2019: SourceEntry(
        year=2019,
        relative_path="data/raw/tabular/2019/flight_with_weather_2019.csv",
        audited_row_count=7161827,
        audited_byte_size=1990370667,
        audited_column_count=34,
    ),
    2020: SourceEntry(
        year=2020,
        relative_path="data/raw/tabular/2020/flight_with_weather_2020.csv",
        audited_row_count=4312091,
        audited_byte_size=1197858795,
        audited_column_count=34,
    ),
    2021: SourceEntry(
        year=2021,
        relative_path="data/raw/tabular/2021/flight_with_weather_2021.csv",
        audited_row_count=5755666,
        audited_byte_size=1600032487,
        audited_column_count=34,
    ),
    2022: SourceEntry(
        year=2022,
        relative_path="data/raw/tabular/2022/flight_with_weather_2022.csv",
        audited_row_count=6413416,
        audited_byte_size=1782648882,
        audited_column_count=34,
    ),
    2023: SourceEntry(
        year=2023,
        relative_path="data/raw/tabular/2023/flight_with_weather_2023.csv",
        audited_row_count=6645461,
        audited_byte_size=1847433387,
        audited_column_count=34,
    ),
    2024: SourceEntry(
        year=2024,
        relative_path="data/raw/tabular/2024/flight_with_weather_2024.csv",
        audited_row_count=6284841,
        audited_byte_size=1748350586,
        audited_column_count=34,
    ),
}

# Grand totals of audited baseline
TOTAL_AUDITED_ROWS: int = 54674003
TOTAL_AUDITED_BYTES: int = 15196366173
EXPECTED_ANNUAL_SOURCES_COUNT: int = 9


def is_symlink_or_reparse(path_obj: Union[str, Path]) -> bool:
    """
    Check if a path component is a symbolic link or Windows reparse point (NTFS junction).
    Handles POSIX symlinks, Windows symlinks, and Windows directory junctions.

    Fail-closed policy:
    If path inspection fails due to PermissionError, EIO, or other unexpected OSError,
    it raises SourcePathSecurityError so that uninspectable paths are never assumed safe.
    Only FileNotFoundError (indicating the path genuinely does not exist) returns False.
    """
    p = Path(path_obj)
    try:
        if p.is_symlink() or os.path.islink(p):
            return True
    except PermissionError as e:
        raise SourcePathSecurityError(f"Permission denied inspecting symlink status: {p}") from e
    except OSError as e:
        if not isinstance(e, FileNotFoundError):
            raise SourcePathSecurityError(f"I/O error inspecting symlink status: {p}") from e
        return False

    try:
        st = os.lstat(p)
        attrs = getattr(st, "st_file_attributes", 0)
        reparse_flag = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x0400)
        if attrs & reparse_flag:
            return True
    except FileNotFoundError:
        return False
    except PermissionError as e:
        raise SourcePathSecurityError(f"Permission denied inspecting path attributes: {p}") from e
    except (OSError, ValueError) as e:
        raise SourcePathSecurityError(f"Failed to inspect path attributes for security verification: {p} ({e})") from e

    return False


def validate_path_safety(
    file_path: Union[str, Path],
    base_dir: Optional[Union[str, Path]] = None,
) -> Path:
    """
    Enforce filesystem security boundaries:
    1. Reject path traversal sequences ('..').
    2. Reject symlinks and reparse points (NTFS junctions) across all path components.
    3. If base_dir is supplied, enforce that the resolved path is contained within base_dir.
    4. Must refer to a regular file if it exists.
    """
    raw_str = str(file_path).replace("\\", "/")
    parts = raw_str.split("/")
    if ".." in parts:
        raise SourcePathSecurityError(f"Path traversal sequence '..' detected in path: {file_path}")

    path_obj = Path(file_path)

    # Check the leaf path component
    if is_symlink_or_reparse(path_obj):
        raise SourcePathSecurityError(f"Symlinks and reparse points are forbidden: {file_path}")

    base_obj = Path(base_dir).resolve() if base_dir is not None else None

    # Check ancestors of path_obj before resolution
    curr = path_obj.parent
    while curr != curr.parent:
        if is_symlink_or_reparse(curr):
            raise SourcePathSecurityError(f"Symlink or reparse point detected in ancestor path: {curr}")
        if base_obj is not None:
            try:
                if curr.resolve() == base_obj:
                    break
            except (OSError, ValueError):
                pass
        curr = curr.parent

    try:
        resolved_path = path_obj.resolve()
    except (OSError, ValueError) as e:
        raise SourcePathSecurityError(f"Failed to resolve path: {path_obj} ({e})") from e

    # Double-check resolved path and its ancestors
    if is_symlink_or_reparse(resolved_path):
        raise SourcePathSecurityError(f"Symlinks and reparse points are forbidden: {resolved_path}")

    curr_res = resolved_path.parent
    while curr_res != curr_res.parent:
        if is_symlink_or_reparse(curr_res):
            raise SourcePathSecurityError(f"Symlink or reparse point detected in resolved ancestor: {curr_res}")
        if base_obj is not None and curr_res == base_obj:
            break
        curr_res = curr_res.parent

    if base_dir is not None:
        try:
            resolved_path.relative_to(base_obj)
        except ValueError:
            raise SourcePathSecurityError(
                f"Path {resolved_path} escapes the allowed base directory {base_obj}"
            )

    return path_obj


@dataclass
class SourceVerificationResult:
    """Structured verification result for a single source file."""
    year: int
    path: str
    state: VerificationState
    actual_byte_size: Optional[int] = None
    expected_byte_size: Optional[int] = None
    computed_sha256: Optional[str] = None
    approved_sha256: Optional[str] = None
    upstream_identity_status: str = UPSTREAM_IDENTITY_STATUS_UNVERIFIED
    error_message: Optional[str] = None
    is_verified: bool = False

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["state"] = self.state.value if isinstance(self.state, VerificationState) else str(self.state)
        return d


@dataclass
class BatchVerificationResult:
    """Aggregated verification result for a set of source files."""
    results: Dict[int, SourceVerificationResult] = field(default_factory=dict)
    all_present: bool = False
    all_sizes_match: bool = False
    all_hashes_verified: bool = False
    total_actual_bytes: int = 0
    upstream_identity_status: str = UPSTREAM_IDENTITY_STATUS_UNVERIFIED
    has_unapproved_candidate_hashes: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "all_present": self.all_present,
            "all_sizes_match": self.all_sizes_match,
            "all_hashes_verified": self.all_hashes_verified,
            "total_actual_bytes": self.total_actual_bytes,
            "upstream_identity_status": self.upstream_identity_status,
            "has_unapproved_candidate_hashes": self.has_unapproved_candidate_hashes,
            "results": {year: res.to_dict() for year, res in self.results.items()},
        }


class SourceValidator:
    """
    Source inventory validator and streaming SHA-256 verifier.
    Supports dependency-injected base directory, inventory definitions, and approved baseline hashes.
    """

    def __init__(
        self,
        base_dir: Optional[Union[str, Path]] = None,
        inventory: Optional[Mapping[int, SourceEntry]] = None,
        approved_baseline_hashes: Optional[Mapping[int, str]] = None,
        chunk_size: int = DEFAULT_HASH_CHUNK_SIZE,
        enforce_production_inventory: bool = False,
    ):
        self.base_dir = Path(base_dir).resolve() if base_dir is not None else Path.cwd().resolve()

        if inventory is not None:
            if len(inventory) == 0:
                raise SourceConfigurationError("Configured inventory cannot be empty")
            self.inventory: Dict[int, SourceEntry] = dict(inventory)
        else:
            self.inventory = dict(AUDITED_SOURCE_INVENTORY)

        self.enforce_production_inventory = enforce_production_inventory
        if self.enforce_production_inventory:
            expected_years = set(range(2016, 2025))
            actual_years = set(self.inventory.keys())
            if actual_years != expected_years:
                missing = sorted(expected_years - actual_years)
                extra = sorted(actual_years - expected_years)
                raise SourceConfigurationError(
                    f"Production inventory must contain exactly all 9 annual sources (2016-2024). "
                    f"Missing years: {missing}, extra years: {extra}"
                )

        self.approved_baseline_hashes: Optional[Dict[int, str]] = (
            dict(approved_baseline_hashes) if approved_baseline_hashes is not None else None
        )
        if chunk_size <= 0:
            raise SourceConfigurationError(f"chunk_size must be positive integer, got {chunk_size}")
        self.chunk_size = chunk_size

        self._validate_inventory_consistency()
        self._validate_baseline_hashes_format()

    def _validate_inventory_consistency(self) -> None:
        """Validate internal inventory data structures."""
        seen_paths: Set[str] = set()
        for year, entry in self.inventory.items():
            if entry.year != year:
                raise SourceConfigurationError(f"Inventory key {year} does not match entry year {entry.year}")
            norm_path = entry.relative_path.replace("\\", "/").strip().lower()
            if norm_path in seen_paths:
                raise SourceConfigurationError(f"Duplicate relative path detected in inventory: {entry.relative_path}")
            seen_paths.add(norm_path)

    def _validate_baseline_hashes_format(self) -> None:
        """Validate formatting of approved baseline hashes if supplied."""
        if self.approved_baseline_hashes is None:
            return

        for year, hash_val in self.approved_baseline_hashes.items():
            if not isinstance(year, int) or year not in self.inventory:
                raise SourceConfigurationError(f"Baseline hash key {year} not found in inventory years")
            if not isinstance(hash_val, str) or len(hash_val) != 64:
                raise SourceConfigurationError(
                    f"Approved baseline hash for year {year} is invalid length or type: {hash_val!r}"
                )
            try:
                int(hash_val, 16)
            except ValueError:
                raise SourceConfigurationError(
                    f"Approved baseline hash for year {year} is not valid hexadecimal: {hash_val!r}"
                )

    def get_source_path(self, year: int) -> Path:
        """Resolve and validate the filesystem path for a given inventory year."""
        if year not in self.inventory:
            raise KeyError(f"Year {year} not found in configured inventory")
        entry = self.inventory[year]
        target_path = self.base_dir / entry.relative_path
        validate_path_safety(target_path, base_dir=self.base_dir)
        return target_path

    def compute_file_hash(
        self,
        file_path: Union[str, Path],
        fail_on_change: bool = True,
    ) -> Tuple[str, int]:
        """
        Compute SHA-256 hash using streaming block reads with pre/post stat checks to detect modification.
        Memory consumption is strictly bounded by chunk_size (O(1)).

        Returns:
            Tuple[str, int]: (sha256_hex_digest, actual_file_byte_size)
        """
        path_obj = validate_path_safety(file_path, base_dir=self.base_dir)

        try:
            stat_before = os.stat(path_obj)
        except FileNotFoundError as e:
            raise SourceNotFoundError(f"Source file not found: {file_path}") from e
        except PermissionError as e:
            raise SourcePermissionError(f"Permission denied reading file stats: {file_path}") from e
        except OSError as e:
            raise SourceIntegrityError(f"I/O error reading file stats: {file_path}") from e

        st_mode = getattr(stat_before, "st_mode", None)
        if isinstance(st_mode, int) and not stat.S_ISREG(st_mode):
            raise SourceIntegrityError(f"Source path is not a regular file: {file_path}")
        elif not isinstance(st_mode, int) and not path_obj.is_file():
            raise SourceIntegrityError(f"Source path is not a regular file: {file_path}")

        hasher = hashlib.sha256()
        bytes_read = 0

        try:
            with open(path_obj, "rb") as f:
                while True:
                    chunk = f.read(self.chunk_size)
                    if not chunk:
                        break
                    hasher.update(chunk)
                    bytes_read += len(chunk)
        except PermissionError as e:
            raise SourcePermissionError(f"Permission denied reading file content: {file_path}") from e
        except OSError as e:
            raise SourceIntegrityError(f"I/O error reading file content: {file_path}") from e

        # Post-read stat check to detect concurrent modification during reading
        try:
            stat_after = os.stat(path_obj)
        except OSError as e:
            raise SourceChangedDuringReadError(
                f"File became inaccessible or was removed during hashing: {file_path}"
            ) from e

        if fail_on_change:
            if stat_after.st_size != stat_before.st_size or stat_after.st_mtime != stat_before.st_mtime:
                raise SourceChangedDuringReadError(
                    f"File modified during hashing: {file_path} (size {stat_before.st_size} -> {stat_after.st_size}, "
                    f"mtime {stat_before.st_mtime} -> {stat_after.st_mtime})"
                )
            if bytes_read != stat_before.st_size:
                raise SourceChangedDuringReadError(
                    f"Bytes read ({bytes_read}) does not match stat size ({stat_before.st_size}): {file_path}"
                )

        return hasher.hexdigest().lower(), bytes_read

    def verify_source(
        self,
        year: int,
        compute_hash: bool = False,
        fail_fast: bool = False,
    ) -> SourceVerificationResult:
        """
        Verify single annual source against inventory metadata and optionally compute/verify hash.
        """
        if year not in self.inventory:
            err = f"Year {year} is not in inventory"
            if fail_fast:
                raise SourceConfigurationError(err)
            return SourceVerificationResult(
                year=year,
                path="UNKNOWN",
                state=VerificationState.SOURCE_MISSING,
                error_message=err,
            )

        entry = self.inventory[year]
        try:
            path_obj = self.get_source_path(year)
        except SourcePathSecurityError as e:
            if fail_fast:
                raise
            return SourceVerificationResult(
                year=year,
                path=entry.relative_path,
                state=VerificationState.SOURCE_READ_ERROR,
                expected_byte_size=entry.audited_byte_size,
                error_message=str(e),
            )

        try:
            st = os.stat(path_obj)
        except FileNotFoundError:
            err = f"Source file does not exist: {path_obj}"
            if fail_fast:
                raise SourceNotFoundError(err)
            return SourceVerificationResult(
                year=year,
                path=str(path_obj),
                state=VerificationState.SOURCE_MISSING,
                expected_byte_size=entry.audited_byte_size,
                error_message=err,
            )
        except PermissionError as e:
            if fail_fast:
                raise SourcePermissionError(str(e)) from e
            return SourceVerificationResult(
                year=year,
                path=str(path_obj),
                state=VerificationState.SOURCE_READ_ERROR,
                expected_byte_size=entry.audited_byte_size,
                error_message=str(e),
            )
        except OSError as e:
            err = f"I/O error reading metadata for {path_obj}: {e}"
            if fail_fast:
                raise SourceIntegrityError(err) from e
            return SourceVerificationResult(
                year=year,
                path=str(path_obj),
                state=VerificationState.SOURCE_READ_ERROR,
                expected_byte_size=entry.audited_byte_size,
                error_message=err,
            )

        st_mode = getattr(st, "st_mode", None)
        is_regular = stat.S_ISREG(st_mode) if isinstance(st_mode, int) else path_obj.is_file()
        if not is_regular:
            err = f"Source path is not a regular file: {path_obj}"
            if fail_fast:
                raise SourceIntegrityError(err)
            return SourceVerificationResult(
                year=year,
                path=str(path_obj),
                state=VerificationState.SOURCE_READ_ERROR,
                expected_byte_size=entry.audited_byte_size,
                error_message=err,
            )

        actual_size = st.st_size

        if actual_size != entry.audited_byte_size:
            err = (
                f"Source size mismatch for year {year}: disk size {actual_size} bytes, "
                f"expected {entry.audited_byte_size} bytes"
            )
            if fail_fast:
                raise SourceSizeMismatchError(err)
            return SourceVerificationResult(
                year=year,
                path=str(path_obj),
                state=VerificationState.SIZE_MISMATCH,
                actual_byte_size=actual_size,
                expected_byte_size=entry.audited_byte_size,
                error_message=err,
            )

        # File exists and size matches
        if not compute_hash:
            return SourceVerificationResult(
                year=year,
                path=str(path_obj),
                state=VerificationState.SOURCE_PRESENT_METADATA_MATCH,
                actual_byte_size=actual_size,
                expected_byte_size=entry.audited_byte_size,
                is_verified=False,
            )

        # Compute streaming hash
        try:
            computed_hash, hashed_bytes = self.compute_file_hash(path_obj, fail_on_change=True)
        except SourceChangedDuringReadError as e:
            if fail_fast:
                raise
            return SourceVerificationResult(
                year=year,
                path=str(path_obj),
                state=VerificationState.SOURCE_CHANGED_DURING_READ,
                actual_byte_size=actual_size,
                expected_byte_size=entry.audited_byte_size,
                error_message=str(e),
            )
        except SourcePermissionError as e:
            if fail_fast:
                raise
            return SourceVerificationResult(
                year=year,
                path=str(path_obj),
                state=VerificationState.SOURCE_READ_ERROR,
                actual_byte_size=actual_size,
                expected_byte_size=entry.audited_byte_size,
                error_message=str(e),
            )
        except SourceIntegrityError as e:
            if fail_fast:
                raise
            return SourceVerificationResult(
                year=year,
                path=str(path_obj),
                state=VerificationState.SOURCE_READ_ERROR,
                actual_byte_size=actual_size,
                expected_byte_size=entry.audited_byte_size,
                error_message=str(e),
            )

        # Baseline evaluation
        approved_hash = (
            self.approved_baseline_hashes.get(year)
            if self.approved_baseline_hashes is not None
            else None
        )

        if approved_hash is None:
            # Candidate hash computed, but no approved baseline exists.
            # Never promote unapproved hash to LOCAL_HASH_VERIFIED!
            return SourceVerificationResult(
                year=year,
                path=str(path_obj),
                state=VerificationState.LOCAL_HASH_COMPUTED_UNAPPROVED,
                actual_byte_size=hashed_bytes,
                expected_byte_size=entry.audited_byte_size,
                computed_sha256=computed_hash,
                approved_sha256=None,
                upstream_identity_status=UPSTREAM_IDENTITY_STATUS_UNVERIFIED,
                is_verified=False,
            )

        norm_approved = approved_hash.strip().lower()
        if computed_hash == norm_approved:
            return SourceVerificationResult(
                year=year,
                path=str(path_obj),
                state=VerificationState.LOCAL_HASH_VERIFIED,
                actual_byte_size=hashed_bytes,
                expected_byte_size=entry.audited_byte_size,
                computed_sha256=computed_hash,
                approved_sha256=norm_approved,
                upstream_identity_status=UPSTREAM_IDENTITY_STATUS_UNVERIFIED,
                is_verified=True,
            )
        else:
            err = (
                f"Hash mismatch for year {year}: computed {computed_hash}, "
                f"approved baseline {norm_approved}"
            )
            if fail_fast:
                raise SourceHashMismatchError(err)
            return SourceVerificationResult(
                year=year,
                path=str(path_obj),
                state=VerificationState.HASH_MISMATCH,
                actual_byte_size=hashed_bytes,
                expected_byte_size=entry.audited_byte_size,
                computed_sha256=computed_hash,
                approved_sha256=norm_approved,
                upstream_identity_status=UPSTREAM_IDENTITY_STATUS_UNVERIFIED,
                error_message=err,
                is_verified=False,
            )

    def verify_all_sources(
        self,
        compute_hash: bool = False,
        fail_fast: bool = False,
    ) -> BatchVerificationResult:
        """
        Verify all configured inventory sources with fail-closed batch semantics.
        """
        if len(self.inventory) == 0:
            return BatchVerificationResult(
                results={},
                all_present=False,
                all_sizes_match=False,
                all_hashes_verified=False,
                total_actual_bytes=0,
                upstream_identity_status=UPSTREAM_IDENTITY_STATUS_UNVERIFIED,
                has_unapproved_candidate_hashes=False,
            )

        results: Dict[int, SourceVerificationResult] = {}
        all_present = True
        all_sizes_match = True
        all_hashes_verified = True
        has_unapproved = False
        total_actual_bytes = 0

        for year in sorted(self.inventory.keys()):
            res = self.verify_source(year, compute_hash=compute_hash, fail_fast=fail_fast)
            results[year] = res

            # Check presence: file must exist as a verified regular file without read/stability/security errors
            if res.state in (
                VerificationState.SOURCE_MISSING,
                VerificationState.SOURCE_READ_ERROR,
                VerificationState.SOURCE_CHANGED_DURING_READ,
            ):
                all_present = False
                all_sizes_match = False
                all_hashes_verified = False
            elif res.state == VerificationState.SIZE_MISMATCH:
                all_sizes_match = False
                all_hashes_verified = False
            elif res.state == VerificationState.LOCAL_HASH_COMPUTED_UNAPPROVED:
                has_unapproved = True
                all_hashes_verified = False
            elif res.state == VerificationState.LOCAL_HASH_VERIFIED:
                pass
            elif res.state == VerificationState.HASH_MISMATCH:
                all_hashes_verified = False
            elif res.state == VerificationState.SOURCE_PRESENT_METADATA_MATCH:
                all_hashes_verified = False
            else:
                all_hashes_verified = False

            if res.actual_byte_size is not None:
                total_actual_bytes += res.actual_byte_size

        if not compute_hash:
            all_hashes_verified = False

        return BatchVerificationResult(
            results=results,
            all_present=all_present,
            all_sizes_match=all_sizes_match,
            all_hashes_verified=all_hashes_verified,
            total_actual_bytes=total_actual_bytes,
            upstream_identity_status=UPSTREAM_IDENTITY_STATUS_UNVERIFIED,
            has_unapproved_candidate_hashes=has_unapproved,
        )

    def record_into_run_manifest(
        self,
        manifest: Any,
        batch_result: BatchVerificationResult,
        record_only_verified_hashes: bool = True,
        allow_partial: bool = False,
    ) -> Dict[str, Any]:
        """
        Record verified sources into a RunManifest instance per DOC-F02:
        Calls manifest.record_input(path=..., bytes_count=..., sha256_hash=...).

        By default (allow_partial=False), if any source in the batch failed validation
        (not all_present or not all_sizes_match), raises SourceIntegrityError (fail-closed).

        If allow_partial=True is explicitly set, records only the sources that passed
        structural validation (state in SOURCE_PRESENT_METADATA_MATCH, LOCAL_HASH_COMPUTED_UNAPPROVED,
        LOCAL_HASH_VERIFIED), excludes failed sources, and returns a structured audit report.
        """
        if not hasattr(manifest, "record_input"):
            raise SourceConfigurationError(
                "Supplied manifest object does not implement record_input(path, bytes_count, sha256_hash) "
                "per DOC-F02"
            )

        if len(batch_result.results) == 0:
            raise SourceIntegrityError("Cannot record empty verification batch into RunManifest")

        valid_states = {
            VerificationState.SOURCE_PRESENT_METADATA_MATCH,
            VerificationState.LOCAL_HASH_COMPUTED_UNAPPROVED,
            VerificationState.LOCAL_HASH_VERIFIED,
        }

        recorded = []
        rejected = []

        for year in sorted(batch_result.results.keys()):
            res = batch_result.results[year]
            if res.state not in valid_states:
                rejected.append({
                    "year": year,
                    "path": res.path,
                    "state": res.state.value if isinstance(res.state, VerificationState) else str(res.state),
                    "error_message": res.error_message or "Integrity validation failed",
                })
            else:
                recorded.append(res)

        if rejected and not allow_partial:
            rej_summary = "; ".join([f"Year {r['year']}: {r['state']} ({r['error_message']})" for r in rejected])
            raise SourceIntegrityError(
                f"Cannot record failed verification batch into RunManifest (allow_partial=False): {rej_summary}"
            )

        for res in recorded:
            path_str = res.path
            bytes_count = res.actual_byte_size if res.actual_byte_size is not None else 0

            if res.is_verified and res.computed_sha256:
                hash_to_record = res.computed_sha256
            elif not record_only_verified_hashes and res.computed_sha256:
                hash_to_record = res.computed_sha256
            else:
                hash_to_record = None

            manifest.record_input(path=path_str, bytes_count=bytes_count, sha256_hash=hash_to_record)

        return {
            "recorded_count": len(recorded),
            "rejected_count": len(rejected),
            "all_verified": batch_result.all_hashes_verified,
            "recorded_paths": [r.path for r in recorded],
            "rejected_details": rejected,
        }
