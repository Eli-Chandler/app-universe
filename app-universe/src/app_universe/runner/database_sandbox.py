import os
import sqlite3
import tempfile
from contextlib import contextmanager
from typing import Iterator


class DatabaseSandbox:
    def __init__(self, base_db_paths: dict[str, str]):
        self._base_db_paths = base_db_paths
        self.paths: dict[str, str] = {}
        self.conns: dict[str, sqlite3.Connection] = {}

    def _clone(self, temp_dir: str) -> None:
        for name, src_path in self._base_db_paths.items():
            dst = os.path.join(temp_dir, f"{name}.db")
            # Backup using a single connection, then close it
            src = sqlite3.connect(src_path)
            dst_conn = sqlite3.connect(dst)
            try:
                src.backup(dst_conn)
            finally:
                src.close()
                dst_conn.close()
            self.paths[name] = dst

    @contextmanager
    def session(self) -> Iterator["DatabaseSandbox"]:
        with tempfile.TemporaryDirectory() as d:
            self._clone(d)
            # open working connections
            self.conns = {n: sqlite3.connect(p) for n, p in self.paths.items()}
            try:
                yield self
            finally:
                # close in reverse order just in case
                for conn in self.conns.values():
                    conn.close()
                self.conns.clear()
