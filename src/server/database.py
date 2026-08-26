import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

import attr

_SCHEMA = """
CREATE TABLE IF NOT EXISTS settings (
    key   TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
"""


@attr.s(auto_attribs=True, frozen=True)
class Database:
    path: Path

    def initialize(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as connection:
            connection.executescript(_SCHEMA)

    @contextmanager
    def _connect(self) -> Iterator[sqlite3.Connection]:
        connection = sqlite3.connect(self.path, isolation_level=None)
        try:
            connection.execute("PRAGMA journal_mode = WAL")
            connection.execute("PRAGMA foreign_keys = ON")
            with connection:
                yield connection
        finally:
            connection.close()

    def get(self, key: str) -> str | None:
        with self._connect() as connection:
            row = connection.execute("SELECT value FROM settings WHERE key = ?", (key,)).fetchone()
        if row is None:
            return None
        value = row[0]
        if not isinstance(value, str):
            raise RuntimeError(f"settings.{key} is stored as {type(value).__name__}, expected str")
        return value

    def set(self, key: str, value: str) -> None:
        with self._connect() as connection:
            connection.execute(
                "INSERT INTO settings (key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value = excluded.value",
                (key, value),
            )

    def delete(self, key: str) -> None:
        with self._connect() as connection:
            connection.execute("DELETE FROM settings WHERE key = ?", (key,))
