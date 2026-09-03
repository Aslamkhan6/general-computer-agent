import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .models import Memory, MemorySource, MemoryType


class MemoryStorage:
    """SQLite persistence layer for long-term agent memories."""

    def __init__(self, db_path: str = "./workspace/memory/memories.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path.resolve()))
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS memories (
                    id TEXT PRIMARY KEY,
                    content TEXT NOT NULL,
                    type TEXT NOT NULL,
                    source TEXT NOT NULL,
                    importance REAL NOT NULL,
                    timestamp TEXT NOT NULL,
                    last_accessed TEXT NOT NULL,
                    access_count INTEGER NOT NULL,
                    metadata_json TEXT NOT NULL,
                    expiration TEXT,
                    persistent INTEGER NOT NULL
                )
            """)
            conn.commit()

    def save(self, memory: Memory) -> None:
        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO memories (
                    id, content, type, source, importance, timestamp,
                    last_accessed, access_count, metadata_json, expiration, persistent
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    memory.id,
                    memory.content,
                    memory.type.value,
                    memory.source.value,
                    memory.importance,
                    memory.timestamp.isoformat(),
                    memory.last_accessed.isoformat(),
                    memory.access_count,
                    json.dumps(memory.metadata),
                    memory.expiration.isoformat() if memory.expiration else None,
                    1 if memory.persistent else 0,
                ),
            )
            conn.commit()

    def get(self, memory_id: str) -> Memory | None:
        with self._get_connection() as conn:
            cur = conn.execute("SELECT * FROM memories WHERE id = ?", (memory_id,))
            row = cur.fetchone()
            if row:
                return self._row_to_memory(row)
        return None

    def load_all(self) -> list[Memory]:
        with self._get_connection() as conn:
            cur = conn.execute("SELECT * FROM memories")
            rows = cur.fetchall()
            return [self._row_to_memory(r) for r in rows]

    def delete(self, memory_id: str) -> bool:
        with self._get_connection() as conn:
            cur = conn.execute("DELETE FROM memories WHERE id = ?", (memory_id,))
            conn.commit()
            return cur.rowcount > 0

    def _row_to_memory(self, row: sqlite3.Row) -> Memory:
        return Memory(
            id=row["id"],
            content=row["content"],
            type=MemoryType(row["type"]),
            source=MemorySource(row["source"]),
            importance=row["importance"],
            timestamp=datetime.fromisoformat(row["timestamp"]),
            last_accessed=datetime.fromisoformat(row["last_accessed"]),
            access_count=row["access_count"],
            metadata=json.loads(row["metadata_json"]),
            expiration=datetime.fromisoformat(row["expiration"]) if row["expiration"] else None,
            persistent=bool(row["persistent"]),
        )
