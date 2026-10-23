"""
Single-Writer Coordination and Filesystem Lock module.
Conforms to ARCHITECTURE.md, T007-04 specifications, and Windows NTFS safety invariants.

Governance Invariants:
- Atomic lock acquisition using os.open with O_CREAT | O_EXCL.
- Owner token verification before release (prevents releasing another writer's lock).
- Fail-closed: No arbitrary timeout-based lock theft.
- Ambiguous liveness requires manual recovery (FAIL_CLOSED — MANUAL_RECOVERY_REQUIRED).
- Preserves forensic lock metadata on failure.
"""

from dataclasses import dataclass, asdict, field
from datetime import datetime, timezone
from enum import Enum
from hashlib import sha256
import json
import os
from pathlib import Path
import platform
import threading
import time
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
import uuid


class LockError(Exception):
    """Base exception for filesystem locking errors."""
    pass


class LockContentionError(LockError):
    """Raised when lock acquisition fails because lock is held by another active or unverified process."""
    pass


class DuplicateRunIdError(LockError):
    """Raised when run_id is already locked or conflicting."""
    pass


class LockOwnerMismatchError(LockError):
    """Raised when release is attempted by a process not owning the lock token."""
    pass


class LockSecurityError(LockError, ValueError):
    """Raised when lock path escapes allowed root or contains traversal."""
    pass


class LockReleaseFailureError(LockError):
    """Raised when lock release fails or cleanup could not be safely completed (PS-01)."""
    pass


class LockOwnerReleaseFailureError(LockOwnerMismatchError, LockReleaseFailureError):
    """Raised when lock release fails specifically due to owner mismatch (C2)."""
    pass


class IncidentPersistenceError(LockError):
    """Raised when an incident report cannot be durably persisted to disk (PC-F02)."""
    pass


class UnresolvedRecoveryStateError(LockContentionError):
    """Raised when active unresolved recovery artifacts exist in lock directory (PC-F01)."""
    pass


@dataclass
class IncidentPersistenceResult:
    """Result of attempting to persist an auditable lock release incident (PC-F02)."""
    success: bool
    incident_file: Optional[Path] = None
    bytes_written: int = 0
    verified: bool = False
    error: Optional[str] = None
    secondary_incident_file: Optional[Path] = None


class PidLivenessStatus(str, Enum):
    """Liveness classification for process IDs, adhering to fail-closed semantics."""
    PROCESS_ALIVE = "PROCESS_ALIVE"
    PROCESS_DEAD = "PROCESS_DEAD"
    INVALID_PID = "INVALID_PID"
    PROCESS_STATUS_UNKNOWN = "PROCESS_STATUS_UNKNOWN"


@dataclass
class LockMetadata:
    """Metadata recorded in lock file for provenance and forensic audit."""
    owner_token: str
    run_id: str
    pid: int
    hostname: str
    created_at: str
    platform: str = field(default_factory=platform.platform)

    def __post_init__(self):
        if isinstance(self.pid, bool) or not isinstance(self.pid, int) or self.pid <= 0:
            raise ValueError(f"Invalid PID: {self.pid!r}. Must be a positive non-boolean integer.")
        if not self.owner_token or not isinstance(self.owner_token, str):
            raise ValueError("owner_token must be a non-empty string.")
        if not self.run_id or not isinstance(self.run_id, str):
            raise ValueError("run_id must be a non-empty string.")
        if not self.hostname or not isinstance(self.hostname, str):
            raise ValueError("hostname must be a non-empty string.")

    def to_json(self) -> str:
        return json.dumps(asdict(self), indent=2)

    @classmethod
    def from_json(cls, json_str: str) -> "LockMetadata":
        data = json.loads(json_str)
        return cls(**data)


def get_pid_liveness(pid: Any) -> PidLivenessStatus:
    """
    Classify process liveness for a given PID with strict fail-closed safety.
    
    Returns:
        - PidLivenessStatus.PROCESS_ALIVE if process exists and is active.
        - PidLivenessStatus.PROCESS_DEAD if process is confirmed non-existent.
        - PidLivenessStatus.INVALID_PID if pid is not a positive non-boolean integer.
        - PidLivenessStatus.PROCESS_STATUS_UNKNOWN if liveness cannot be safely determined.
        
    CRITICAL WINDOWS SAFETY:
    Never use `os.kill(pid, 0)` on Windows! Signal 0 sends CTRL_C_EVENT to the process group,
    terminating the runner. Win32 OpenProcess with PROCESS_QUERY_LIMITED_INFORMATION is used instead.
    """
    if isinstance(pid, bool) or not isinstance(pid, int) or pid <= 0:
        return PidLivenessStatus.INVALID_PID

    if os.name == "nt":
        import ctypes
        from ctypes import wintypes

        PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
        ERROR_ACCESS_DENIED = 5
        ERROR_INVALID_PARAMETER = 87
        STILL_ACTIVE = 259

        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel32.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
        kernel32.OpenProcess.restype = wintypes.HANDLE
        kernel32.GetExitCodeProcess.argtypes = [wintypes.HANDLE, ctypes.POINTER(wintypes.DWORD)]
        kernel32.GetExitCodeProcess.restype = wintypes.BOOL
        kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
        kernel32.CloseHandle.restype = wintypes.BOOL

        handle = kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
        if not handle:
            err = ctypes.get_last_error()
            if err == ERROR_ACCESS_DENIED:
                # Access denied indicates process exists under different user / elevated context
                return PidLivenessStatus.PROCESS_ALIVE
            elif err == ERROR_INVALID_PARAMETER:
                # Invalid parameter indicates PID does not exist in system table
                return PidLivenessStatus.PROCESS_DEAD
            else:
                return PidLivenessStatus.PROCESS_STATUS_UNKNOWN

        try:
            exit_code = wintypes.DWORD()
            if kernel32.GetExitCodeProcess(handle, ctypes.byref(exit_code)):
                if exit_code.value == STILL_ACTIVE:
                    return PidLivenessStatus.PROCESS_ALIVE
                return PidLivenessStatus.PROCESS_DEAD
            return PidLivenessStatus.PROCESS_STATUS_UNKNOWN
        except Exception:
            return PidLivenessStatus.PROCESS_STATUS_UNKNOWN
        finally:
            kernel32.CloseHandle(handle)
    else:
        try:
            os.kill(pid, 0)
            return PidLivenessStatus.PROCESS_ALIVE
        except PermissionError:
            return PidLivenessStatus.PROCESS_ALIVE
        except ProcessLookupError:
            return PidLivenessStatus.PROCESS_DEAD
        except OSError:
            return PidLivenessStatus.PROCESS_STATUS_UNKNOWN
        except Exception:
            return PidLivenessStatus.PROCESS_STATUS_UNKNOWN


def is_pid_alive(pid: Any) -> bool:
    """
    Check if a process with given PID is currently active on local host.
    Delegates to get_pid_liveness() and returns True ONLY if status is PROCESS_ALIVE.
    """
    return get_pid_liveness(pid) == PidLivenessStatus.PROCESS_ALIVE


class CoordinationLock:
    """
    OS-level and in-process coordination lock serializing critical sections
    (acquire, release, break_stale_lock) across cooperative pipeline processes.
    Uses Win32/MSVCRT byte locking on Windows and fcntl.flock on POSIX.
    """
    _process_local_lock = threading.RLock()

    def __init__(self, coord_path: Path):
        self.coord_path = coord_path
        self._fd: Optional[int] = None

    def __enter__(self) -> "CoordinationLock":
        self._process_local_lock.acquire()
        try:
            self.coord_path.parent.mkdir(parents=True, exist_ok=True)
            flags = os.O_CREAT | os.O_RDWR | getattr(os, "O_BINARY", 0)
            self._fd = os.open(str(self.coord_path), flags, 0o600)
            if os.name == "nt":
                import msvcrt
                # Lock byte 0 exclusively in blocking mode
                msvcrt.locking(self._fd, msvcrt.LK_LOCK, 1)
            else:
                import fcntl
                fcntl.flock(self._fd, fcntl.LOCK_EX)
            return self
        except Exception:
            if self._fd is not None:
                try:
                    os.close(self._fd)
                except Exception:
                    pass
                self._fd = None
            self._process_local_lock.release()
            raise

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            if self._fd is not None:
                try:
                    if os.name == "nt":
                        import msvcrt
                        try:
                            os.lseek(self._fd, 0, os.SEEK_SET)
                            msvcrt.locking(self._fd, msvcrt.LK_UNLCK, 1)
                        except Exception:
                            pass
                    else:
                        import fcntl
                        try:
                            fcntl.flock(self._fd, fcntl.LOCK_UN)
                        except Exception:
                            pass
                    os.close(self._fd)
                except Exception:
                    pass
                finally:
                    self._fd = None
        finally:
            self._process_local_lock.release()


class SingleWriterLock:
    """
    Single-writer filesystem lock ensuring mutually exclusive access to pipeline execution.
    Uses atomic OS-level file creation (O_CREAT | O_EXCL), cryptographic owner tokens,
    and OS-level CoordinationLock with atomic isolated file removal (R5-F01).
    """

    def __init__(
        self,
        lock_dir: Union[str, Path],
        run_id: str,
        lock_filename: str = ".pipeline.lock",
    ):
        if not run_id or not isinstance(run_id, str):
            raise ValueError("run_id must be a non-empty string")
        self.run_id = run_id.strip()
        self.lock_dir = Path(lock_dir).resolve()
        self.lock_filename = lock_filename
        self.lock_file_path = self.lock_dir / self.lock_filename
        self.coord_file_path = self.lock_dir / f"{self.lock_filename}.coord"
        self._coord_lock = CoordinationLock(self.coord_file_path)

        # Generate unique owner token for this lock instance
        self.owner_token: str = str(uuid.uuid4())
        self._is_acquired: bool = False
        self._fd: Optional[int] = None
        self._current_open_fd: Optional[int] = None
        self._pre_unlink_hook: Optional[Callable[[], None]] = None
        self._post_rename_hook: Optional[Callable[[], None]] = None
        self._pre_write_hook: Optional[Callable[[], None]] = None
        self._pre_cleanup_hook: Optional[Callable[[], None]] = None

    @property
    def is_acquired(self) -> bool:
        """Return True iff lock is currently held by this instance."""
        return self._is_acquired

    def get_unresolved_recovery_artifacts(self) -> List[Path]:
        """
        Scan lock directory under CoordinationLock for unresolved lock lifecycle artifacts (PC-F01):
        - Staging deletion files (.del_*) from incomplete or failed release / break_stale_lock
        - Failed acquisition files (.failed_acq_*) from failed metadata writes
        - Quarantined lock files (.quarantine_*) from ownership collision / tampering
        - Release-in-progress markers (.release_in_progress_*)
        - Durable recovery markers (.recovery_required*)
        """
        artifacts: List[Path] = []
        if not self.lock_dir.exists():
            return artifacts

        prefix_pattern = self.lock_filename.lstrip(".")
        patterns = [
            f"*{prefix_pattern}*.del_*",
            f"*{prefix_pattern}*.failed_acq_*",
            f"*{prefix_pattern}*.quarantine_*",
            f"*{prefix_pattern}*.release_in_progress_*",
            f"*{prefix_pattern}*.recovery_in_progress_*",
            f"*{prefix_pattern}*.recovery_required*",
        ]
        seen = set()
        for pat in patterns:
            for p in self.lock_dir.glob(pat):
                if p.is_file() and p not in seen:
                    seen.add(p)
                    artifacts.append(p)
        return sorted(artifacts)

    def acquire(self) -> "SingleWriterLock":
        """
        Atomically acquire the lock file inside CoordinationLock critical section.
        
        Raises:
            UnresolvedRecoveryStateError: If unrecovered staging/quarantine/marker files exist.
            LockContentionError: If lock is already held.
            DuplicateRunIdError: If active lock is for the same run_id.
            OSError: On filesystem permission or I/O failure.
        """
        if self._is_acquired:
            return self

        self.lock_dir.mkdir(parents=True, exist_ok=True)

        with self._coord_lock:
            # Check for unresolved recovery artifacts before attempting acquisition (PC-F01)
            unresolved = self.get_unresolved_recovery_artifacts()
            if unresolved:
                artifact_names = [p.name for p in unresolved]
                raise UnresolvedRecoveryStateError(
                    f"Cannot acquire lock: unresolved recovery artifacts detected in lock directory "
                    f"{self.lock_dir}: {artifact_names}. Incomplete lock release, crash during removal, "
                    f"or quarantined collision state requires authorized operator recovery before new writers "
                    f"may acquire the lock. FAIL_CLOSED — MANUAL_RECOVERY_REQUIRED"
                )

            # Check if lock file already exists
            if self.lock_file_path.exists():
                existing_meta = self._read_existing_metadata()
                if existing_meta:
                    if existing_meta.run_id == self.run_id:
                        raise DuplicateRunIdError(
                            f"Active lock already exists for run_id '{self.run_id}' "
                            f"(PID: {existing_meta.pid}, Host: {existing_meta.hostname})"
                        )
                    liveness = get_pid_liveness(existing_meta.pid) if existing_meta.hostname == platform.node() else PidLivenessStatus.PROCESS_ALIVE
                    if liveness == PidLivenessStatus.PROCESS_ALIVE:
                        raise LockContentionError(
                            f"Lock contention: locked by active process PID {existing_meta.pid} "
                            f"(run_id: '{existing_meta.run_id}', token: {existing_meta.owner_token})"
                        )
                    else:
                        # PID is dead or unverified on local host, fail-closed policy requires manual recovery
                        raise LockContentionError(
                            f"Lock held by terminated or unverified process PID {existing_meta.pid} "
                            f"(run_id: '{existing_meta.run_id}'). Automatic stealing prohibited: "
                            "FAIL_CLOSED — MANUAL_RECOVERY_REQUIRED"
                        )
                raise LockContentionError(
                    f"Lock file exists but could not be parsed: {self.lock_file_path}. "
                    "FAIL_CLOSED — MANUAL_RECOVERY_REQUIRED"
                )

            meta = LockMetadata(
                owner_token=self.owner_token,
                run_id=self.run_id,
                pid=os.getpid(),
                hostname=platform.node(),
                created_at=datetime.now(timezone.utc).isoformat(),
            )
            meta_json = meta.to_json().encode("utf-8")

            # Atomic file creation using O_CREAT | O_EXCL | O_RDWR
            flags = os.O_CREAT | os.O_EXCL | os.O_RDWR | getattr(os, "O_BINARY", 0)
            try:
                fd = os.open(str(self.lock_file_path), flags, 0o600)
            except FileExistsError:
                raise LockContentionError(f"Lock contention: lock file created concurrently at {self.lock_file_path}")
            except OSError as e:
                raise LockError(f"Failed to create lock file {self.lock_file_path}: {e}") from e

            self._current_open_fd = fd

            # Record file stats from fd to identify the exact file created
            try:
                st_orig = os.fstat(fd)
            except OSError as e:
                try:
                    os.close(fd)
                except Exception:
                    pass
                self._current_open_fd = None
                raise LockError(
                    f"Failed to stat newly created lock file ({self.lock_file_path}): {e}. "
                    f"FAIL_CLOSED — MANUAL_RECOVERY_REQUIRED: Canonical lock file was created at fd={fd} "
                    f"but file stats could not be captured for identity tracking. Incomplete lock file remains "
                    f"on disk to prevent unsafe unlinking of an unverified path. Manual operator recovery is required."
                ) from e

            # Hook for testing race condition between file creation and metadata writing
            if self._pre_write_hook:
                self._pre_write_hook()

            # Write metadata and flush immediately
            try:
                bytes_written = os.write(fd, meta_json)
                if bytes_written < len(meta_json):
                    raise OSError(f"Short metadata write: wrote {bytes_written} of {len(meta_json)} bytes")
                os.fsync(fd)
                # Retain fd open while lock is acquired (OS-authoritative held lock preventing NTFS mutation)
                self._fd = fd
                self._current_open_fd = None
            except Exception as e:
                if self._pre_cleanup_hook:
                    self._pre_cleanup_hook()

                try:
                    os.close(fd)
                except Exception:
                    pass
                self._fd = None
                self._current_open_fd = None

                # SAFE IDENTITY-AWARE CLEANUP (R6-F01):
                # Verify that self.lock_file_path still refers to the exact file created by fd (same st_ino and st_dev).
                # If an out-of-band actor replaced self.lock_file_path, WE MUST NOT DELETE IT!
                try:
                    if self.lock_file_path.exists():
                        st_cur = self.lock_file_path.stat()
                        if (st_cur.st_ino, st_cur.st_dev) != (st_orig.st_ino, st_orig.st_dev):
                            # The canonical lock file was replaced by another owner or external actor!
                            # PRESERVE THE REPLACEMENT LOCK INTACT!
                            raise LockError(
                                f"Failed to complete lock acquisition: {e}. In addition, canonical lock file "
                                f"{self.lock_file_path} was concurrently replaced by an unexpected file "
                                f"(orig inode {st_orig.st_ino} vs current inode {st_cur.st_ino}). "
                                "Replacement lock file preserved intact; FAIL_CLOSED — MANUAL_RECOVERY_REQUIRED"
                            ) from e

                        # The file at self.lock_file_path is indeed our own failed/incomplete file.
                        # To eliminate check-then-unlink race, atomically rename to staging and verify again.
                        staging_fail = self.lock_dir / f".{self.lock_filename}.failed_acq_{uuid.uuid4().hex}"
                        try:
                            os.rename(str(self.lock_file_path), str(staging_fail))
                            st_staging = staging_fail.stat()
                            if (st_staging.st_ino, st_staging.st_dev) == (st_orig.st_ino, st_orig.st_dev):
                                staging_fail.unlink(missing_ok=True)
                            else:
                                # Swapped right before rename: restore it!
                                if not self.lock_file_path.exists():
                                    try:
                                        os.replace(str(staging_fail), str(self.lock_file_path))
                                    except Exception:
                                        pass
                        except Exception:
                            pass
                except LockError:
                    raise
                except Exception:
                    pass

                raise LockError(f"Failed to write lock metadata: {e}") from e

            self._is_acquired = True
            return self

    def release(self) -> None:
        """
        Release the lock file if owned by this instance.
        Verifies owner token in lock file before removal to prevent race deletions.
        Uses atomic isolated removal (os.rename to staging) to eliminate TOCTOU races (R5-F01).
        """
        if not self._is_acquired:
            return

        with self._coord_lock:
            # Release OS file handle if held
            if self._fd is not None:
                try:
                    os.close(self._fd)
                except Exception:
                    pass
                self._fd = None

            if not self.lock_file_path.exists():
                self._is_acquired = False
                return

            existing_meta = self._read_existing_metadata()
            if existing_meta is None:
                raise LockOwnerMismatchError(
                    f"Cannot release lock: lock file {self.lock_file_path} is missing or corrupted."
                )

            if existing_meta.owner_token != self.owner_token:
                raise LockOwnerMismatchError(
                    f"Lock owner mismatch! Cannot release lock owned by {existing_meta.owner_token} "
                    f"using token {self.owner_token}."
                )

            # Hook for simulating race condition between check and unlink in testing
            if self._pre_unlink_hook:
                self._pre_unlink_hook()

            # Establish durable release-in-progress marker before entering destructive transition (PC-F01)
            marker_path = self.lock_dir / f".{self.lock_filename}.release_in_progress_{self.owner_token}"
            marker_tmp = self.lock_dir / f".{marker_path.name}.tmp_{uuid.uuid4().hex[:8]}"
            try:
                marker_tmp.write_text(
                    json.dumps({
                        "event": "RELEASE_IN_PROGRESS",
                        "owner_token": self.owner_token,
                        "run_id": self.run_id,
                        "pid": os.getpid(),
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                    }),
                    encoding="utf-8",
                )
                os.replace(str(marker_tmp), str(marker_path))
            except Exception as e:
                try:
                    marker_tmp.unlink(missing_ok=True)
                except Exception:
                    pass
                raise LockError(f"Failed to establish durable release marker: {e}") from e

            # Atomic isolated removal protocol (R5-F01):
            # Rather than calling Path.unlink() directly on self.lock_file_path,
            # atomically rename to a private staging file, verify its token, and unlink the staging file.
            staging_del = self.lock_dir / f".{self.lock_filename}.del_{uuid.uuid4().hex}"
            try:
                os.rename(str(self.lock_file_path), str(staging_del))
            except FileNotFoundError:
                # Concurrently deleted
                marker_path.unlink(missing_ok=True)
                self._is_acquired = False
                return
            except OSError as e:
                marker_path.unlink(missing_ok=True)
                raise LockError(f"Failed to isolate lock file for deletion: {e}") from e

            # Hook for testing race condition immediately after rename (R6-F02)
            if self._post_rename_hook:
                self._post_rename_hook()

            staging_meta = self._read_metadata_from_path(staging_del)
            if staging_meta is None or staging_meta.owner_token != self.owner_token:
                # File was concurrently replaced or corrupted right before the rename!
                # Restore it back so the replacement lock is preserved!
                marker_path.unlink(missing_ok=True)
                if not self.lock_file_path.exists():
                    try:
                        os.replace(str(staging_del), str(self.lock_file_path))
                    except Exception:
                        pass
                    raise LockOwnerMismatchError(
                        f"Lock owner mismatch! Lock file was concurrently replaced prior to release "
                        f"(expected token {self.owner_token}). Replacement lock restored to canonical path."
                    )
                else:
                    # Both staging_del and canonical lock file exist: quarantine staging and fail closed (R6-F02)
                    quarantine_path = self.lock_dir / f".{self.lock_filename}.quarantine_{uuid.uuid4().hex}"
                    try:
                        os.rename(str(staging_del), str(quarantine_path))
                    except Exception:
                        pass
                    raise LockOwnerMismatchError(
                        f"CRITICAL: Lock authority compromised! Lock file was concurrently replaced prior to release "
                        f"(expected token {self.owner_token}, found {staging_meta.owner_token if staging_meta else 'unparseable'}) "
                        f"and canonical path was re-occupied. Staged replacement quarantined for forensics. "
                        "FAIL_CLOSED — MANUAL_RECOVERY_REQUIRED"
                    )

            # Verified owner token on isolated file: unlink staging
            try:
                staging_del.unlink(missing_ok=True)
            except OSError as e:
                # Staging unlink failed: DO NOT clear marker or staging_del!
                # Preserving both files ensures subsequent writers detect unresolved recovery state (PC-F01)
                raise LockError(f"Failed to delete isolated lock file {staging_del}: {e}") from e

            # Clean exit: unlink marker
            try:
                marker_path.unlink(missing_ok=True)
            except Exception:
                pass
            finally:
                self._is_acquired = False

    def break_stale_lock(self, force: bool = False) -> bool:
        """
        Governed recovery method to break a verified stale lock (PID dead on local machine).
        Requires explicit force=True flag.
        
        Hardened under R3-F03, R4-F02, R4-F03, and R5-F01:
        - If metadata cannot be parsed, is incomplete, or ownership is ambiguous:
          FAILS CLOSED and raises LockContentionError with FAIL_CLOSED — MANUAL_RECOVERY_REQUIRED.
        - Strictly refuses to delete active, unknown, or invalid PID locks.
        - Verifies process termination on local host via Win32 process handles (nt) or signal 0 (posix).
        - Executes inside CoordinationLock critical section.
        - Uses atomic isolated removal protocol to eliminate check-to-unlink TOCTOU races.
        """
        if not force:
            raise LockError("Breaking a stale lock requires explicit force=True authorization.")

        if not self.lock_file_path.exists():
            return True

        with self._coord_lock:
            if not self.lock_file_path.exists():
                return True

            existing_meta = self._read_existing_metadata()
            if existing_meta is None:
                raise LockContentionError(
                    f"Cannot automatically break unparseable or corrupted lock file {self.lock_file_path}: "
                    "ownership, host, and process liveness cannot be safely established. "
                    "FAIL_CLOSED — MANUAL_RECOVERY_REQUIRED"
                )

            if not existing_meta.owner_token or not existing_meta.pid or not existing_meta.hostname:
                raise LockContentionError(
                    f"Cannot break incomplete lock file {self.lock_file_path}: missing required metadata fields. "
                    "FAIL_CLOSED — MANUAL_RECOVERY_REQUIRED"
                )

            if existing_meta.hostname != platform.node():
                raise LockError(
                    f"Cannot break lock owned by different host: {existing_meta.hostname} vs {platform.node()}. "
                    "FAIL_CLOSED — MANUAL_RECOVERY_REQUIRED"
                )

            liveness = get_pid_liveness(existing_meta.pid)
            if liveness == PidLivenessStatus.INVALID_PID:
                raise LockContentionError(
                    f"Lock contains invalid PID {existing_meta.pid!r}: liveness cannot be safely established. "
                    "FAIL_CLOSED — MANUAL_RECOVERY_REQUIRED"
                )
            elif liveness == PidLivenessStatus.PROCESS_STATUS_UNKNOWN:
                raise LockContentionError(
                    f"Process status for PID {existing_meta.pid} could not be determined. "
                    "FAIL_CLOSED — MANUAL_RECOVERY_REQUIRED"
                )
            elif liveness == PidLivenessStatus.PROCESS_ALIVE:
                raise LockContentionError(
                    f"Refusing to break lock: process PID {existing_meta.pid} on host {existing_meta.hostname} is still actively running."
                )
            elif liveness != PidLivenessStatus.PROCESS_DEAD:
                raise LockContentionError(
                    f"Refusing to break lock: unhandled liveness status {liveness.name}. "
                    "FAIL_CLOSED — MANUAL_RECOVERY_REQUIRED"
                )

            # Hook for simulating race condition between check and unlink in testing
            if self._pre_unlink_hook:
                self._pre_unlink_hook()

            # Atomic isolated removal protocol (R5-F01):
            staging_del = self.lock_dir / f".{self.lock_filename}.del_{uuid.uuid4().hex}"
            try:
                os.rename(str(self.lock_file_path), str(staging_del))
            except FileNotFoundError:
                return True
            except OSError as e:
                raise LockError(f"Failed to isolate stale lock file for deletion: {e}") from e

            staging_meta = self._read_metadata_from_path(staging_del)
            if staging_meta is None:
                if not self.lock_file_path.exists():
                    try:
                        os.replace(str(staging_del), str(self.lock_file_path))
                    except Exception:
                        pass
                else:
                    quarantine_path = self.lock_dir / f".{self.lock_filename}.quarantine_{uuid.uuid4().hex}"
                    try:
                        os.rename(str(staging_del), str(quarantine_path))
                    except Exception:
                        pass
                raise LockContentionError(
                    "Lock file became unparseable concurrently between verification and removal. "
                    "FAIL_CLOSED — MANUAL_RECOVERY_REQUIRED"
                )

            if (
                staging_meta.owner_token != existing_meta.owner_token
                or staging_meta.pid != existing_meta.pid
            ):
                # Stale lock was concurrently modified or replaced! Restore it!
                if not self.lock_file_path.exists():
                    try:
                        os.replace(str(staging_del), str(self.lock_file_path))
                    except Exception:
                        pass
                else:
                    quarantine_path = self.lock_dir / f".{self.lock_filename}.quarantine_{uuid.uuid4().hex}"
                    try:
                        os.rename(str(staging_del), str(quarantine_path))
                    except Exception:
                        pass
                raise LockContentionError(
                    "Lock file changed concurrently between verification and removal "
                    f"(expected token {existing_meta.owner_token}, found {staging_meta.owner_token}). "
                    "FAIL_CLOSED — MANUAL_RECOVERY_REQUIRED"
                )

            try:
                staging_del.unlink(missing_ok=True)
            except OSError as e:
                raise LockError(f"Failed to delete verified stale lock file {staging_del}: {e}") from e

            return True

    def _read_metadata_from_path(self, path: Path) -> Optional[LockMetadata]:
        """Safely read metadata from a specific path."""
        try:
            content = path.read_text(encoding="utf-8")
            return LockMetadata.from_json(content)
        except Exception:
            return None

    def _read_existing_metadata(self) -> Optional[LockMetadata]:
        """Safely read metadata from existing lock file."""
        return self._read_metadata_from_path(self.lock_file_path)

    def resolve_recovery_state(
        self,
        authorized: bool = False,
        operator: str = "",
        reason: str = "",
        archive_dir: Optional[Path] = None,
    ) -> Dict[str, Any]:
        """
        Authorized operator manual recovery protocol (PC-F01).
        
        Requires explicit authorization (`authorized=True`), operator identifier, and reason.
        Under CoordinationLock:
        1. Scans for any unresolved recovery artifacts (.del_*, .failed_acq_*, .quarantine_*, release markers).
        2. Idempotent: If none exist, returns success without modifying anything.
        3. For each unresolved artifact, moves it to an isolated recovery archive directory
           with forensic preservation (timestamp, sha256), NEVER silently deleting unknown files.
        4. Writes an auditable recovery resolution record (JSON).
        5. Returns a structured summary of the resolved artifacts.
        """
        if not authorized:
            raise LockError("Manual recovery requires explicit authorized=True confirmation.")
        if not operator or not isinstance(operator, str) or not operator.strip():
            raise ValueError("Manual recovery requires non-empty operator identifier.")
        if not reason or not isinstance(reason, str) or not reason.strip():
            raise ValueError("Manual recovery requires non-empty justification reason.")

        with self._coord_lock:
            unresolved = self.get_unresolved_recovery_artifacts()
            target_archive = archive_dir or (self.lock_dir / "recovery_archive")
            target_archive.mkdir(parents=True, exist_ok=True)

            if not unresolved:
                return {
                    "resolved": True,
                    "count": 0,
                    "archived_artifacts": [],
                    "archive_dir": str(target_archive),
                    "operator": operator.strip(),
                    "reason": reason.strip(),
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }

            archived_info = []
            resolution_id = uuid.uuid4().hex[:12]
            ts = datetime.now(timezone.utc).isoformat()

            # 1. Establish durable hold marker BEFORE relocating artifacts (C1)
            hold_name = f".{self.lock_filename}.recovery_in_progress_{resolution_id}"
            hold_file = self.lock_dir / hold_name
            hold_tmp = self.lock_dir / f".tmp_{hold_name}_{uuid.uuid4().hex}"
            hold_data = json.dumps({
                "event": "RECOVERY_IN_PROGRESS",
                "resolution_id": resolution_id,
                "operator": operator.strip(),
                "reason": reason.strip(),
                "unresolved_artifacts": [p.name for p in unresolved],
                "timestamp": ts,
                "pid": os.getpid(),
            }, indent=2).encode("utf-8")

            fd_hold = os.open(str(hold_tmp), os.O_CREAT | os.O_WRONLY | os.O_EXCL | getattr(os, "O_BINARY", 0), 0o600)
            try:
                os.write(fd_hold, hold_data)
                os.fsync(fd_hold)
            finally:
                os.close(fd_hold)
            os.replace(str(hold_tmp), str(hold_file))

            # 2. Archive artifacts to target_archive with forensic preservation
            for art in unresolved:
                if art == hold_file:
                    continue
                try:
                    data = art.read_bytes()
                    art_sha = sha256(data).hexdigest()
                    art_size = len(data)
                except Exception:
                    art_sha = "unreadable"
                    art_size = -1

                archived_name = f"archived_{art.name}_{resolution_id}"
                archived_path = target_archive / archived_name
                try:
                    os.replace(str(art), str(archived_path))
                    archived_info.append({
                        "original_path": str(art),
                        "archived_path": str(archived_path),
                        "bytes": art_size,
                        "sha256": art_sha,
                    })
                except Exception as e:
                    # Partial archival failure: hold_file remains on disk, blocking admission
                    raise LockError(
                        f"Failed to archive recovery artifact {art}: {e}. "
                        f"Recovery hold marker preserved ({hold_file.name}). FAIL_CLOSED — MANUAL_RECOVERY_REQUIRED"
                    ) from e

            # 3. Write and verify resolution audit record
            resolution_record = {
                "resolution_id": resolution_id,
                "timestamp_utc": ts,
                "operator": operator.strip(),
                "reason": reason.strip(),
                "lock_dir": str(self.lock_dir),
                "resolved_count": len(archived_info),
                "archived_artifacts": archived_info,
            }
            record_bytes = json.dumps(resolution_record, indent=2).encode("utf-8")
            res_file = target_archive / f"recovery_resolution_{resolution_id}.json"
            res_tmp = target_archive / f".tmp_recovery_resolution_{resolution_id}_{uuid.uuid4().hex}"

            try:
                fd_res = os.open(str(res_tmp), os.O_CREAT | os.O_WRONLY | os.O_EXCL | getattr(os, "O_BINARY", 0), 0o600)
                try:
                    w = os.write(fd_res, record_bytes)
                    if w < len(record_bytes):
                        raise OSError(f"Short write on recovery resolution: wrote {w} of {len(record_bytes)}")
                    os.fsync(fd_res)
                finally:
                    os.close(fd_res)

                os.replace(str(res_tmp), str(res_file))

                # Byte-level readback verification
                readback = res_file.read_bytes()
                if readback != record_bytes:
                    raise OSError(f"Corrupted recovery resolution readback: expected {len(record_bytes)} bytes, got {len(readback)}")
            except Exception as e:
                # Clean up temp file
                try:
                    res_tmp.unlink(missing_ok=True)
                except Exception:
                    pass
                # CRITICAL: Preserve admission block via durable recovery_required marker
                perm_marker = self.lock_dir / f".{self.lock_filename}.recovery_required_{resolution_id}"
                try:
                    os.replace(str(hold_file), str(perm_marker))
                except Exception:
                    pass
                raise LockError(
                    f"Failed to commit recovery resolution audit record: {e}. "
                    f"Admission guard preserved via {perm_marker.name}. FAIL_CLOSED — MANUAL_RECOVERY_REQUIRED"
                ) from e

            # 4. Verified commit: clear hold marker
            try:
                hold_file.unlink(missing_ok=True)
            except Exception as e:
                raise LockError(
                    f"Recovery resolution committed but failed to remove hold file {hold_file}: {e}. "
                    "FAIL_CLOSED — MANUAL_RECOVERY_REQUIRED"
                ) from e

            return {
                "resolved": True,
                "resolution_id": resolution_id,
                "count": len(archived_info),
                "archived_artifacts": archived_info,
                "resolution_record_file": str(res_file),
                "archive_dir": str(target_archive),
                "operator": operator.strip(),
                "reason": reason.strip(),
                "timestamp": ts,
            }

    def persist_release_incident(
        self,
        release_err: Exception,
        pipeline_err: Optional[Exception] = None,
        secondary_dir: Optional[Path] = None,
        raise_on_failure: bool = False,
    ) -> IncidentPersistenceResult:
        """
        Persist an auditable, non-destructive lock release failure incident report (PS-01 / PC-F02).
        Uses atomic file replacement, fsync, and readback verification.
        Never suppresses write failures while reporting false success.
        """
        incident_id = uuid.uuid4().hex[:12]
        timestamp = datetime.now(timezone.utc).isoformat()
        incident_file = self.lock_dir / f"lock_release_incident_{self.owner_token}_{incident_id}.json"

        lock_file_exists = self.lock_file_path.exists()
        lock_metadata = None
        if lock_file_exists:
            try:
                m = self._read_existing_metadata()
                if m:
                    lock_metadata = asdict(m)
            except Exception:
                pass

        payload = {
            "incident_id": incident_id,
            "timestamp_utc": timestamp,
            "event": "LOCK_RELEASE_FAILURE",
            "lock_file_path": str(self.lock_file_path),
            "lock_file_exists": lock_file_exists,
            "canonical_metadata": lock_metadata,
            "owner_token": self.owner_token,
            "run_id": self.run_id,
            "pid": os.getpid(),
            "hostname": platform.node(),
            "release_error_type": type(release_err).__name__,
            "release_error_message": str(release_err),
            "pipeline_error_type": type(pipeline_err).__name__ if pipeline_err else None,
            "pipeline_error_message": str(pipeline_err) if pipeline_err else None,
            "recovery_status": "MANUAL_RECOVERY_REQUIRED",
            "action_required": (
                "Investigate lock directory and release error. If pipeline outputs were published, "
                "preserve published immutable outputs and perform authorized operator recovery "
                "after verifying no concurrent writer is active."
            ),
        }
        content = json.dumps(payload, indent=2).encode("utf-8")

        def _try_atomic_write(target_dir: Path, fname: str) -> Tuple[bool, Optional[Path], int, Optional[str]]:
            try:
                target_dir.mkdir(parents=True, exist_ok=True)
                dest = target_dir / fname
                tmp = target_dir / f".{fname}.tmp_{uuid.uuid4().hex[:8]}"

                flags = os.O_CREAT | os.O_WRONLY | os.O_TRUNC | getattr(os, "O_BINARY", 0)
                fd = os.open(str(tmp), flags, 0o600)
                try:
                    bytes_written = os.write(fd, content)
                    if bytes_written < len(content):
                        raise OSError(f"Short write: wrote {bytes_written} of {len(content)} bytes")
                    os.fsync(fd)
                finally:
                    os.close(fd)

                os.replace(str(tmp), str(dest))

                # Readback verification
                read_data = dest.read_bytes()
                if read_data != content:
                    raise OSError("Readback verification failed: written bytes do not match expected payload")
                parsed = json.loads(read_data.decode("utf-8"))
                if parsed.get("incident_id") != incident_id:
                    raise ValueError(f"Readback incident_id mismatch: {parsed.get('incident_id')} != {incident_id}")

                return True, dest, len(read_data), None
            except Exception as exc:
                return False, None, 0, f"{type(exc).__name__}: {exc}"

        # Attempt primary persistence in lock_dir
        primary_ok, primary_path, primary_bytes, primary_err = _try_atomic_write(
            self.lock_dir, incident_file.name
        )

        if primary_ok:
            return IncidentPersistenceResult(
                success=True,
                incident_file=primary_path,
                bytes_written=primary_bytes,
                verified=True,
                error=None,
            )

        # Primary persistence failed. Attempt secondary backup if secondary_dir provided
        secondary_ok = False
        secondary_path = None
        secondary_err = None
        if secondary_dir:
            secondary_ok, secondary_path, sec_bytes, secondary_err = _try_atomic_write(
                secondary_dir, f"backup_{incident_file.name}"
            )
            if secondary_ok:
                return IncidentPersistenceResult(
                    success=True,
                    incident_file=secondary_path,
                    bytes_written=sec_bytes,
                    verified=True,
                    error=f"Primary write failed ({primary_err}); saved to secondary backup",
                    secondary_incident_file=secondary_path,
                )

        total_err = f"Primary persistence failed ({primary_err})"
        if secondary_dir:
            total_err += f"; Secondary persistence failed ({secondary_err})"

        if raise_on_failure:
            raise IncidentPersistenceError(total_err)

        return IncidentPersistenceResult(
            success=False,
            incident_file=None,
            bytes_written=0,
            verified=False,
            error=total_err,
        )

    def __enter__(self) -> "SingleWriterLock":
        return self.acquire()

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._is_acquired:
            rel_err = None
            try:
                self.release()
            except Exception as e:
                rel_err = e

            if rel_err is not None:
                inc_res = self.persist_release_incident(release_err=rel_err, pipeline_err=exc_val)
                if inc_res.success and inc_res.verified:
                    incident_diag = f"Incident persisted at {inc_res.incident_file}"
                else:
                    incident_diag = f"INCIDENT_PERSISTENCE_FAILED ({inc_res.error})"

                if exc_val is None:
                    # Normal block execution, but release failed: surface release failure with incident status (C2)
                    msg = (
                        f"Lock release failed ({type(rel_err).__name__}: {rel_err}). "
                        f"{incident_diag}. FAIL_CLOSED — MANUAL_RECOVERY_REQUIRED"
                    )
                    if isinstance(rel_err, LockOwnerMismatchError):
                        err = LockOwnerReleaseFailureError(msg)
                    else:
                        err = LockReleaseFailureError(msg)
                    err.release_error = rel_err
                    err.incident_result = inc_res
                    raise err from rel_err
                else:
                    # Block exception occurred AND release failed: chain release error from block exception
                    msg = (
                        f"Lock release failed after block exception ({type(rel_err).__name__}: {rel_err}). "
                        f"{incident_diag}. FAIL_CLOSED — MANUAL_RECOVERY_REQUIRED"
                    )
                    if isinstance(rel_err, LockOwnerMismatchError):
                        err = LockOwnerReleaseFailureError(msg)
                    else:
                        err = LockReleaseFailureError(msg)
                    err.release_error = rel_err
                    err.incident_result = inc_res
                    raise err from exc_val
