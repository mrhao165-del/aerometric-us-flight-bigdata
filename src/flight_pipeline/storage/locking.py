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
import json
import os
from pathlib import Path
import platform
import time
from typing import Any, Dict, Optional, Union
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


@dataclass
class LockMetadata:
    """Metadata recorded in lock file for provenance and forensic audit."""
    owner_token: str
    run_id: str
    pid: int
    hostname: str
    created_at: str
    platform: str = field(default_factory=platform.platform)

    def to_json(self) -> str:
        return json.dumps(asdict(self), indent=2)

    @classmethod
    def from_json(cls, json_str: str) -> "LockMetadata":
        data = json.loads(json_str)
        return cls(**data)


def is_pid_alive(pid: int) -> bool:
    """
    Check if a process with given PID is currently active on local host.
    
    CRITICAL WINDOWS NOTE:
    Never use `os.kill(pid, 0)` on Windows! On Windows, signal 0 is `CTRL_C_EVENT` (0),
    which invokes `GenerateConsoleCtrlEvent(CTRL_C_EVENT, pid)` and sends a Ctrl+C signal
    to the console process group, terminating the parent CLI / runner!
    Instead, on Windows we use Win32 `OpenProcess` + `GetExitCodeProcess` via `ctypes`.
    """
    if not isinstance(pid, int) or pid <= 0:
        return False

    if os.name == "nt":
        import ctypes
        from ctypes import wintypes

        PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
        ERROR_ACCESS_DENIED = 5
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
                return True
            return False

        try:
            exit_code = wintypes.DWORD()
            if kernel32.GetExitCodeProcess(handle, ctypes.byref(exit_code)):
                return exit_code.value == STILL_ACTIVE
            return True
        finally:
            kernel32.CloseHandle(handle)
    else:
        try:
            os.kill(pid, 0)
            return True
        except PermissionError:
            return True
        except (ProcessLookupError, OSError):
            return False


class SingleWriterLock:
    """
    Single-writer filesystem lock ensuring mutually exclusive access to pipeline execution.
    Uses atomic OS-level file creation (O_CREAT | O_EXCL) and cryptographic owner tokens.
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

        # Generate unique owner token for this lock instance
        self.owner_token: str = str(uuid.uuid4())
        self._is_acquired: bool = False
        self._fd: Optional[int] = None

    @property
    def is_acquired(self) -> bool:
        """Return True iff lock is currently held by this instance."""
        return self._is_acquired

    def acquire(self) -> "SingleWriterLock":
        """
        Atomically acquire the lock file.
        
        Raises:
            LockContentionError: If lock is already held.
            DuplicateRunIdError: If active lock is for the same run_id.
            OSError: On filesystem permission or I/O failure.
        """
        if self._is_acquired:
            return self

        self.lock_dir.mkdir(parents=True, exist_ok=True)

        meta = LockMetadata(
            owner_token=self.owner_token,
            run_id=self.run_id,
            pid=os.getpid(),
            hostname=platform.node(),
            created_at=datetime.now(timezone.utc).isoformat(),
        )
        meta_json = meta.to_json().encode("utf-8")

        # Atomic file creation using O_CREAT | O_EXCL
        flags = os.O_CREAT | os.O_EXCL | os.O_WRONLY | getattr(os, "O_BINARY", 0)
        try:
            fd = os.open(str(self.lock_file_path), flags, 0o600)
        except FileExistsError:
            # Lock file already exists. Inspect existing lock for diagnostics.
            existing_meta = self._read_existing_metadata()
            if existing_meta:
                if existing_meta.run_id == self.run_id:
                    raise DuplicateRunIdError(
                        f"Active lock already exists for run_id '{self.run_id}' "
                        f"(PID: {existing_meta.pid}, Host: {existing_meta.hostname})"
                    )
                alive = is_pid_alive(existing_meta.pid) if existing_meta.hostname == platform.node() else True
                if alive:
                    raise LockContentionError(
                        f"Lock contention: locked by active process PID {existing_meta.pid} "
                        f"(run_id: '{existing_meta.run_id}', token: {existing_meta.owner_token})"
                    )
                else:
                    # PID is dead on local host, but fail-closed policy requires explicit/manual recovery
                    raise LockContentionError(
                        f"Lock held by terminated process PID {existing_meta.pid} "
                        f"(run_id: '{existing_meta.run_id}'). Automatic stealing prohibited: "
                        "FAIL_CLOSED — MANUAL_RECOVERY_REQUIRED"
                    )
            raise LockContentionError(
                f"Lock file exists but could not be parsed: {self.lock_file_path}. "
                "FAIL_CLOSED — MANUAL_RECOVERY_REQUIRED"
            )
        except OSError as e:
            raise LockError(f"Failed to create lock file {self.lock_file_path}: {e}") from e

        # Write metadata and flush immediately
        try:
            os.write(fd, meta_json)
            os.close(fd)
        except Exception as e:
            try:
                os.close(fd)
            except Exception:
                pass
            try:
                self.lock_file_path.unlink(missing_ok=True)
            except Exception:
                pass
            raise LockError(f"Failed to write lock metadata: {e}") from e

        self._is_acquired = True
        return self

    def release(self) -> None:
        """
        Release the lock file if owned by this instance.
        Verifies owner token in lock file before removal to prevent race deletions.
        """
        if not self._is_acquired:
            return

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

        try:
            self.lock_file_path.unlink()
        except OSError as e:
            raise LockError(f"Failed to delete lock file {self.lock_file_path}: {e}") from e
        finally:
            self._is_acquired = False

    def break_stale_lock(self, force: bool = False) -> bool:
        """
        Governed recovery method to break a verified stale lock (PID dead on local machine).
        Requires explicit force=True flag.
        """
        if not force:
            raise LockError("Breaking a stale lock requires explicit force=True authorization.")

        if not self.lock_file_path.exists():
            return True

        existing_meta = self._read_existing_metadata()
        if existing_meta is None:
            self.lock_file_path.unlink()
            return True

        if existing_meta.hostname != platform.node():
            raise LockError(
                f"Cannot break lock owned by different host: {existing_meta.hostname} vs {platform.node()}"
            )

        if is_pid_alive(existing_meta.pid):
            raise LockContentionError(
                f"Refusing to break lock: process PID {existing_meta.pid} is still actively running."
            )

        # PID is confirmed dead on local host
        self.lock_file_path.unlink()
        return True

    def _read_existing_metadata(self) -> Optional[LockMetadata]:
        """Safely read metadata from existing lock file."""
        try:
            content = self.lock_file_path.read_text(encoding="utf-8")
            return LockMetadata.from_json(content)
        except Exception:
            return None

    def __enter__(self) -> "SingleWriterLock":
        return self.acquire()

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._is_acquired:
            try:
                self.release()
            except Exception:
                pass
