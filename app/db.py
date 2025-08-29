import os
import sqlite3
from datetime import datetime

DB_DIR = "data"
DB_PATH = os.path.join(DB_DIR, "submissions.db")

def _conn():
    # One connection per call; check_same_thread=False so FastAPI thread can use it.
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def ensure_db():
    os.makedirs(DB_DIR, exist_ok=True)
    conn = _conn()
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS submissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name_enc TEXT NOT NULL,
                instagram_enc TEXT NOT NULL,
                entry_enc TEXT NOT NULL,
                gender_enc TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.commit()
    finally:
        conn.close()

def insert_submission(name_enc: str, instagram_enc: str, entry_enc: str, gender_enc: str):
    conn = _conn()
    try:
        conn.execute(
            "INSERT INTO submissions(name_enc, instagram_enc, entry_enc, gender_enc, created_at) VALUES (?, ?, ?, ?, ?)",
            (name_enc, instagram_enc, entry_enc, gender_enc, datetime.utcnow().isoformat(timespec="seconds")+"Z"),
        )
        conn.commit()
    finally:
        conn.close()

def fetch_all_count() -> int:
    conn = _conn()
    try:
        cur = conn.execute("SELECT COUNT(*) FROM submissions")
        (count,) = cur.fetchone()
        return int(count)
    finally:
        conn.close()

def fetch_all_rows():
    conn = _conn()
    conn.row_factory = sqlite3.Row
    try:
        cur = conn.execute(
            "SELECT id, name_enc, instagram_enc, entry_enc, gender_enc, created_at FROM submissions ORDER BY id ASC"
        )
        return cur.fetchall()
    finally:
        conn.close()
