"""Internal identity-to-workspace mapping, ready for server authentication.

Only trusted server code may call provision/set_enabled. resolve() must receive
the identity verified by the future session layer, never a browser user_id.
This module does not implement authentication or expose an HTTP endpoint.
"""
from contextlib import closing
from dataclasses import dataclass
from pathlib import Path
import re
import sqlite3
import uuid


class WorkspaceDenied(PermissionError):
    pass


@dataclass(frozen=True)
class Workspace:
    user_id: str
    workspace_id: str
    directory: Path
    quota_bytes: int

    @property
    def database_path(self):
        return self.directory / "data" / "calculator.sqlite3"


class WorkspaceRegistry:
    def __init__(self, root):
        self.root = Path(root).resolve()
        self.root.mkdir(parents=True, exist_ok=True)
        self.path = self.root / "accounts.sqlite3"
        with self._db() as db:
            db.execute("""CREATE TABLE IF NOT EXISTS workspaces (
                user_id TEXT PRIMARY KEY,
                workspace_id TEXT NOT NULL UNIQUE,
                enabled INTEGER NOT NULL CHECK(enabled IN (0,1)),
                quota_bytes INTEGER NOT NULL CHECK(quota_bytes > 0))""")

    def _db(self):
        return closing(sqlite3.connect(self.path, timeout=10))

    def provision(self, trusted_user_id, *, quota_bytes):
        if not isinstance(trusted_user_id, str) or not trusted_user_id.strip():
            raise ValueError("A verified account identity is required")
        if len(trusted_user_id) > 255:
            raise ValueError("Account identity is too long")
        if type(quota_bytes) is not int or quota_bytes <= 0:
            raise ValueError("Storage allowance must be a positive integer")
        key = uuid.uuid4().hex
        with self._db() as db, db:
            db.execute("INSERT INTO workspaces VALUES (?, ?, 1, ?)",
                       (trusted_user_id, key, quota_bytes))
        return self.resolve(trusted_user_id)

    def resolve(self, verified_user_id):
        with self._db() as db:
            row = db.execute("SELECT workspace_id, enabled, quota_bytes FROM workspaces WHERE user_id = ?",
                             (verified_user_id,)).fetchone()
        if not row or not row[1]:
            raise WorkspaceDenied("Account is unavailable")
        key, _, quota = row
        # Identity/email/client paths are never used as filesystem names.
        if not re.fullmatch(r"[a-f0-9]{32}", key):
            raise WorkspaceDenied("Invalid workspace mapping")
        tenants = self.root / "workspaces"
        if tenants.is_symlink():
            raise WorkspaceDenied("Invalid workspace root")
        expected = tenants / key
        if expected.is_symlink() or expected.resolve() != expected:
            raise WorkspaceDenied("Invalid workspace directory")
        expected.mkdir(parents=True, exist_ok=True)
        return Workspace(verified_user_id, key, expected, quota)

    def set_enabled(self, trusted_user_id, enabled):
        if type(enabled) is not bool:
            raise ValueError("Enabled must be true or false")
        with self._db() as db, db:
            changed = db.execute("UPDATE workspaces SET enabled = ? WHERE user_id = ?",
                                 (int(enabled), trusted_user_id)).rowcount
            if not changed:
                raise WorkspaceDenied("Account is unavailable")
