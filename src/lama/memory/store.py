from __future__ import annotations

from pathlib import Path
import sqlite3
from datetime import datetime


class MemoryStore:
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS task_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    created_at TEXT NOT NULL,
                    kind TEXT NOT NULL,
                    status TEXT NOT NULL,
                    summary TEXT NOT NULL
                )
                """
            )

    def add_task_event(self, kind: str, status: str, summary: str) -> None:
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO task_log(created_at, kind, status, summary) VALUES(?, ?, ?, ?)",
                (datetime.now().isoformat(timespec="seconds"), kind, status, summary),
            )

    def completed_today(self) -> int:
        prefix = datetime.now().date().isoformat() + "%"
        with self._connect() as conn:
            row = conn.execute(
                "SELECT COUNT(*) FROM task_log WHERE status='done' AND created_at LIKE ?",
                (prefix,),
            ).fetchone()
        return int(row[0] if row else 0)
