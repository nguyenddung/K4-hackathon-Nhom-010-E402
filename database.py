"""SQLite persistence layer, schema migrations, and transaction helpers."""

import sqlite3
import uuid
from contextlib import contextmanager
from datetime import UTC, datetime
from typing import Iterator

from config import DB_PATH
from security_service import blind_index, encrypt


def now() -> str:
    return datetime.now(UTC).isoformat()


def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    conn.execute("PRAGMA busy_timeout = 5000")
    return conn


@contextmanager
def transaction() -> Iterator[sqlite3.Connection]:
    conn = get_conn()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db() -> None:
    with transaction() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                email TEXT NOT NULL UNIQUE COLLATE NOCASE,
                password_hash TEXT NOT NULL,
                name TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'Recruiter',
                created_at TEXT NOT NULL,
                updated_at TEXT
            );
            CREATE TABLE IF NOT EXISTS jobs (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                department TEXT NOT NULL DEFAULT 'Engineering',
                code TEXT,
                embedding TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT,
                status TEXT NOT NULL DEFAULT 'open' CHECK(status IN ('open', 'closed'))
            );
            CREATE TABLE IF NOT EXISTS candidates (
                id TEXT PRIMARY KEY,
                job_id TEXT NOT NULL REFERENCES jobs(id) ON DELETE RESTRICT,
                name TEXT NOT NULL,
                email TEXT,
                cv_text TEXT NOT NULL,
                embedding TEXT NOT NULL,
                score REAL NOT NULL CHECK(score >= 0 AND score <= 1),
                reasoning TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT
                ,encrypted_name TEXT
                ,encrypted_email TEXT
                ,name_blind_index TEXT
                ,email_blind_index TEXT
                ,encrypted_cv_text TEXT
                ,encrypted_cv_filename TEXT
                ,security_status TEXT NOT NULL DEFAULT 'protected'
                ,redaction_count INTEGER NOT NULL DEFAULT 0
            );
            CREATE TABLE IF NOT EXISTS decisions (
                id TEXT PRIMARY KEY,
                candidate_id TEXT NOT NULL UNIQUE REFERENCES candidates(id) ON DELETE CASCADE,
                decision TEXT NOT NULL CHECK(decision IN ('Pass', 'Hold', 'Reject')),
                note TEXT NOT NULL DEFAULT '',
                override_score INTEGER,
                ai_score INTEGER,
                created_at TEXT NOT NULL,
                updated_at TEXT
            );
            CREATE TABLE IF NOT EXISTS audit_log (
                id TEXT PRIMARY KEY,
                entity_id TEXT NOT NULL,
                action TEXT NOT NULL,
                detail TEXT NOT NULL,
                actor_id TEXT,
                created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS cv_documents (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                encrypted_filename TEXT NOT NULL,
                encrypted_text TEXT NOT NULL,
                encrypted_fields TEXT NOT NULL,
                embedding_model TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS cv_chunks (
                id TEXT PRIMARY KEY,
                document_id TEXT NOT NULL REFERENCES cv_documents(id) ON DELETE CASCADE,
                position INTEGER NOT NULL,
                section TEXT NOT NULL,
                encrypted_text TEXT NOT NULL,
                embedding TEXT NOT NULL,
                UNIQUE(document_id, position)
            );
            CREATE INDEX IF NOT EXISTS idx_candidates_job_created ON candidates(job_id, created_at DESC);
            CREATE INDEX IF NOT EXISTS idx_candidates_name ON candidates(name COLLATE NOCASE);
            CREATE INDEX IF NOT EXISTS idx_audit_entity_created ON audit_log(entity_id, created_at DESC);
            CREATE INDEX IF NOT EXISTS idx_cv_documents_user_created ON cv_documents(user_id, created_at DESC);
            CREATE INDEX IF NOT EXISTS idx_cv_chunks_document_position ON cv_chunks(document_id, position);
        """)
        # Safely extend databases created by earlier project versions.
        for table, column, definition in (
            ("users", "updated_at", "TEXT"), ("jobs", "updated_at", "TEXT"),
            ("jobs", "status", "TEXT NOT NULL DEFAULT 'open'"),
            ("jobs", "department", "TEXT NOT NULL DEFAULT 'Engineering'"), ("jobs", "code", "TEXT"),
            ("candidates", "email", "TEXT"), ("candidates", "updated_at", "TEXT"),
            ("candidates", "encrypted_name", "TEXT"), ("candidates", "encrypted_email", "TEXT"),
            ("candidates", "name_blind_index", "TEXT"), ("candidates", "email_blind_index", "TEXT"),
            ("candidates", "encrypted_cv_text", "TEXT"), ("candidates", "encrypted_cv_filename", "TEXT"),
            ("candidates", "security_status", "TEXT NOT NULL DEFAULT 'protected'"), ("candidates", "redaction_count", "INTEGER NOT NULL DEFAULT 0"),
            ("decisions", "updated_at", "TEXT"), ("decisions", "override_score", "INTEGER"),
            ("decisions", "ai_score", "INTEGER"), ("audit_log", "actor_id", "TEXT"),
        ):
            columns = {row["name"] for row in conn.execute(f"PRAGMA table_info({table})")}
            if column not in columns:
                conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")
        # Upgrade legacy local records: preserve data in encrypted columns and remove plaintext PII.
        legacy = conn.execute("SELECT id,name,email,cv_text FROM candidates WHERE encrypted_name IS NULL").fetchall()
        for row in legacy:
            name, email, cv_text = row["name"] or "Candidate", row["email"], row["cv_text"] or ""
            conn.execute(
                """UPDATE candidates SET name=?,email=NULL,cv_text='[ENCRYPTED]',encrypted_name=?,encrypted_email=?,
                   encrypted_cv_text=?,name_blind_index=?,email_blind_index=?,security_status='protected' WHERE id=?""",
                (f"Candidate {row['id'][:8]}", encrypt(name), encrypt(email) if email else None, encrypt(cv_text), blind_index(name), blind_index(email) if email else None, row["id"]),
            )
        conn.execute("CREATE INDEX IF NOT EXISTS idx_candidates_name_blind ON candidates(name_blind_index)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_candidates_email_blind ON candidates(email_blind_index)")


def log_audit(conn: sqlite3.Connection, entity_id: str, action: str, detail: str, actor_id: str | None) -> None:
    conn.execute(
        "INSERT INTO audit_log (id, entity_id, action, detail, actor_id, created_at) VALUES (?,?,?,?,?,?)",
        (str(uuid.uuid4()), entity_id, action, detail, actor_id, now()),
    )
