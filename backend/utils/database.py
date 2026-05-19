import json
import sqlite3
from datetime import datetime, timezone

try:
    from backend.utils.preprocess import DATA_DIR
except ModuleNotFoundError:
    from utils.preprocess import DATA_DIR

DB_PATH = DATA_DIR / "failsafe.db"


def get_connection():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL UNIQUE,
                name TEXT NOT NULL,
                role TEXT NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS prediction_snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                total_students INTEGER NOT NULL,
                high_risk INTEGER NOT NULL,
                medium_risk INTEGER NOT NULL,
                low_risk INTEGER NOT NULL,
                accuracy REAL,
                precision REAL,
                recall REAL,
                f1 REAL,
                payload TEXT NOT NULL
            )
            """
        )
        conn.commit()


def save_prediction_snapshot(summary, metrics=None):
    metrics = metrics or {}
    payload = json.dumps({"summary": summary, "metrics": metrics})
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO prediction_snapshots (
                created_at, total_students, high_risk, medium_risk, low_risk,
                accuracy, precision, recall, f1, payload
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                datetime.now(timezone.utc).isoformat(),
                summary.get("students", 0),
                summary.get("high_risk", 0),
                summary.get("medium", 0),
                summary.get("safe", 0),
                metrics.get("accuracy"),
                metrics.get("precision"),
                metrics.get("recall"),
                metrics.get("f1"),
                payload,
            ),
        )
        conn.commit()


def latest_snapshots(limit=6):
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT created_at, total_students, high_risk, medium_risk, low_risk,
                   accuracy, precision, recall, f1
            FROM prediction_snapshots
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
    return [dict(row) for row in rows][::-1]
