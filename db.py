# db.py
from __future__ import annotations

import os
import json
import sqlite3
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

# Always store DB next to this file (project root)
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "runs.db")

def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with get_conn() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                config_json TEXT NOT NULL,
                summary_json TEXT NOT NULL,
                csv_text TEXT NOT NULL
            )
            """
        )
        conn.execute("CREATE INDEX IF NOT EXISTS idx_runs_created_at ON runs(created_at)")
        conn.commit()


def save_run(cfg: Dict[str, Any], summary: Dict[str, Any], csv_text: str) -> int:
    created_at = datetime.now(timezone.utc).isoformat()
    with get_conn() as conn:
        cur = conn.execute(
            """
            INSERT INTO runs (created_at, config_json, summary_json, csv_text)
            VALUES (?, ?, ?, ?)
            """,
            (created_at, json.dumps(cfg), json.dumps(summary), csv_text),
        )
        conn.commit()
        return int(cur.lastrowid)


def list_runs(limit: int = 50) -> List[Dict[str, Any]]:
    with get_conn() as conn:
        rows = conn.execute(
            """
            SELECT id, created_at, summary_json
            FROM runs
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()

    out: List[Dict[str, Any]] = []
    for r in rows:
        summ = json.loads(r["summary_json"])
        out.append(
            {
                "id": r["id"],
                "created_at": r["created_at"],
                "completed_rate": summ.get("completed_rate"),
                "avg_touchpoints": summ.get("avg_touchpoints"),
                "avg_total_time": summ.get("avg_total_time"),
            }
        )
    return out


def get_run(run_id: int) -> Optional[Dict[str, Any]]:
    with get_conn() as conn:
        row = conn.execute(
            """
            SELECT id, created_at, config_json, summary_json, csv_text
            FROM runs
            WHERE id = ?
            """,
            (run_id,),
        ).fetchone()

    if not row:
        return None

    return {
        "id": row["id"],
        "created_at": row["created_at"],
        "config": json.loads(row["config_json"]),
        "summary": json.loads(row["summary_json"]),
        "csv_text": row["csv_text"],
    }
