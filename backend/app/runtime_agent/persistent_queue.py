"""Persistent SQLite-backed queue store — survives restarts.

Mirrors the ActionQueue interface for Telegram callback compatibility.
"""

import os
import sqlite3
import json
import logging
import threading
from datetime import datetime
from typing import Optional

logger = logging.getLogger("sezonski.persistent_queue")

DEFAULT_DB_PATH = os.path.abspath(os.path.join(
    os.path.dirname(__file__), "..", "..", "persistent_queue.db"
))


class PersistentQueueStore:
    """SQLite-backed queue store. Thread-safe. Survives restarts."""

    def __init__(self, db_path: str | None = None):
        self.db_path = db_path or DEFAULT_DB_PATH
        self._lock = threading.Lock()
        self._init_db()

    def _init_db(self):
        with self._lock:
            conn = sqlite3.connect(self.db_path)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS persistent_queue (
                    item_id TEXT PRIMARY KEY,
                    action_type TEXT NOT NULL DEFAULT 'request_operator_review',
                    status TEXT NOT NULL DEFAULT 'pending',
                    suggested_text TEXT DEFAULT '',
                    edited_text TEXT DEFAULT '',
                    reason TEXT DEFAULT '',
                    operator TEXT DEFAULT '',
                    operator_approval_required INTEGER DEFAULT 1,
                    lead_id TEXT DEFAULT NULL,
                    event_id TEXT DEFAULT NULL,
                    raw_json TEXT DEFAULT '{}',
                    created_at TEXT NOT NULL,
                    updated_at TEXT DEFAULT ''
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_pq_status
                ON persistent_queue(status)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_pq_created
                ON persistent_queue(created_at)
            """)
            conn.commit()
            conn.close()
            logger.info(f"Persistent queue initialized: {self.db_path}")

    # ── CRUD ─────────────────────────────────────────────────────────────

    def add(self, item: dict) -> str:
        """Store a queue item. Returns item_id."""
        item_id = item.get("item_id", "")
        if not item_id:
            import uuid
            item_id = f"q_{uuid.uuid4().hex[:12]}"

        now = datetime.utcnow().isoformat()

        with self._lock:
            conn = sqlite3.connect(self.db_path)
            conn.execute("""
                INSERT OR REPLACE INTO persistent_queue
                (item_id, action_type, status, suggested_text, edited_text, reason,
                 operator, operator_approval_required, lead_id, event_id,
                 raw_json, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                item_id,
                item.get("action_type", "request_operator_review"),
                item.get("status", "pending"),
                item.get("suggested_text", ""),
                item.get("edited_text", ""),
                item.get("reason", ""),
                item.get("operator", ""),
                1 if item.get("operator_approval_required", True) else 0,
                item.get("lead_id"),
                item.get("event_id"),
                json.dumps(item.get("raw_json", {}) or {}),
                item.get("created_at", now),
                item.get("updated_at", ""),
            ))
            conn.commit()
            conn.close()

        logger.debug(f"Persistent queue: added {item_id}")
        return item_id

    def get(self, item_id: str) -> dict | None:
        """Get a queue item by ID."""
        with self._lock:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            row = conn.execute(
                "SELECT * FROM persistent_queue WHERE item_id = ?", (item_id,)
            ).fetchone()
            conn.close()

        if not row:
            return None
        return self._row_to_dict(row)

    def update_status(self, item_id: str, new_status: str,
                      operator: str = "", reason: str = "") -> bool:
        """Update queue item status. Returns True if updated."""
        now = datetime.utcnow().isoformat()

        with self._lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.execute("""
                UPDATE persistent_queue
                SET status = ?, updated_at = ?,
                    operator = CASE WHEN ? != '' THEN ? ELSE operator END,
                    reason = CASE WHEN ? != '' THEN ? ELSE reason END
                WHERE item_id = ?
            """, (new_status, now, operator, operator, reason, reason, item_id))
            updated = cursor.rowcount > 0
            conn.commit()
            conn.close()

        if updated:
            logger.info(f"Persistent queue: {item_id} → {new_status}")
        return updated

    def update_text(self, item_id: str, new_text: str, operator: str = "") -> bool:
        """Update suggested_text or edited_text."""
        now = datetime.utcnow().isoformat()

        with self._lock:
            conn = sqlite3.connect(self.db_path)
            conn.execute("""
                UPDATE persistent_queue
                SET edited_text = ?, status = 'edited',
                    updated_at = ?, operator = ?
                WHERE item_id = ?
            """, (new_text, now, operator, item_id))
            updated = conn.execute("SELECT changes()").fetchone()[0] > 0
            conn.commit()
            conn.close()

        if updated:
            logger.info(f"Persistent queue: {item_id} text edited")
        return updated

    def get_all(self, status: str | None = None) -> list[dict]:
        """Get all items, optionally filtered by status."""
        with self._lock:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            if status:
                rows = conn.execute(
                    "SELECT * FROM persistent_queue WHERE status = ? ORDER BY created_at DESC",
                    (status,)
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM persistent_queue ORDER BY created_at DESC"
                ).fetchall()
            conn.close()

        return [self._row_to_dict(r) for r in rows]

    def get_pending_count(self) -> int:
        with self._lock:
            conn = sqlite3.connect(self.db_path)
            count = conn.execute(
                "SELECT COUNT(*) FROM persistent_queue WHERE status = 'pending'"
            ).fetchone()[0]
            conn.close()
        return count

    # ── Helpers ───────────────────────────────────────────────────────────

    def _row_to_dict(self, row) -> dict:
        return {
            "item_id": row["item_id"],
            "action_type": row["action_type"],
            "status": row["status"],
            "suggested_text": row["suggested_text"],
            "edited_text": row["edited_text"],
            "reason": row["reason"],
            "operator": row["operator"],
            "operator_approval_required": bool(row["operator_approval_required"]),
            "lead_id": row["lead_id"],
            "event_id": row["event_id"],
            "raw_json": json.loads(row["raw_json"]) if row["raw_json"] else {},
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
        }

    def close(self):
        pass  # SQLite handles this via connections


# Singleton
_persistent_store: PersistentQueueStore | None = None


def get_persistent_queue(db_path: str | None = None) -> PersistentQueueStore:
    global _persistent_store
    if _persistent_store is None:
        _persistent_store = PersistentQueueStore(db_path)
    return _persistent_store
