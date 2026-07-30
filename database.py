"""SQLite setup and audit logging."""

import datetime
import sqlite3
import uuid

from config import DB_PATH


def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conn()
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS jobs (
            id TEXT PRIMARY KEY,
            title TEXT,
            description TEXT,
            embedding TEXT,
            created_at TEXT
        );
        CREATE TABLE IF NOT EXISTS candidates (
            id TEXT PRIMARY KEY,
            job_id TEXT,
            name TEXT,
            cv_text TEXT,
            embedding TEXT,
            score REAL,
            reasoning TEXT,
            created_at TEXT
        );
        CREATE TABLE IF NOT EXISTS decisions (
            id TEXT PRIMARY KEY,
            candidate_id TEXT,
            decision TEXT,
            note TEXT,
            created_at TEXT
        );
        CREATE TABLE IF NOT EXISTS audit_log (
            id TEXT PRIMARY KEY,
            entity_id TEXT,
            action TEXT,
            detail TEXT,
            created_at TEXT
        );
        """
    )
    conn.commit()
    conn.close()


def log_audit(entity_id: str, action: str, detail: str):
    conn = get_conn()
    conn.execute(
        "INSERT INTO audit_log (id, entity_id, action, detail, created_at) VALUES (?,?,?,?,?)",
        (str(uuid.uuid4()), entity_id, action, detail, datetime.datetime.utcnow().isoformat()),
    )
    conn.commit()
    conn.close()