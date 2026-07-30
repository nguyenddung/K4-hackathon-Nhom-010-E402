"""Versioned, non-destructive SQLite migrations."""

from __future__ import annotations

import datetime
import sqlite3
import uuid


LATEST_SCHEMA_VERSION = 4


def utc_now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def _columns(conn: sqlite3.Connection, table: str) -> set[str]:
    return {row[1] for row in conn.execute(f'PRAGMA table_info("{table}")')}


def _table_exists(conn: sqlite3.Connection, table: str) -> bool:
    return conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (table,)
    ).fetchone() is not None


def _add_columns(conn: sqlite3.Connection, table: str, definitions: dict[str, str]) -> None:
    existing = _columns(conn, table)
    for name, definition in definitions.items():
        if name not in existing:
            conn.execute(f'ALTER TABLE "{table}" ADD COLUMN "{name}" {definition}')


def _base_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS schema_migrations (
            version INTEGER PRIMARY KEY,
            applied_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            username TEXT UNIQUE,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'CANDIDATE',
            full_name TEXT NOT NULL,
            created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS jobs (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            embedding TEXT,
            created_at TEXT NOT NULL
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
            entity_id TEXT NOT NULL,
            action TEXT NOT NULL,
            detail TEXT,
            created_at TEXT NOT NULL
        );
        """
    )


def _migration_1_expand_legacy_schema(conn: sqlite3.Connection) -> None:
    _add_columns(
        conn,
        "jobs",
        {
            "level": "TEXT DEFAULT 'Middle'",
            "mandatory_skills": "TEXT DEFAULT ''",
            "preferred_skills": "TEXT DEFAULT ''",
            "salary": "TEXT DEFAULT 'Thỏa thuận'",
            "timeline": "TEXT DEFAULT '30 ngày'",
            "rubric_json": "TEXT DEFAULT '[]'",
            "vague_warnings_json": "TEXT DEFAULT '[]'",
            "status": "TEXT DEFAULT 'JOB_PUBLISHED'",
            "updated_at": "TEXT",
        },
    )
    _add_columns(
        conn,
        "candidates",
        {
            "email": "TEXT",
            "portfolio_link": "TEXT",
            "mandatory_flags": "TEXT DEFAULT '[]'",
            "evidence_json": "TEXT DEFAULT '[]'",
            "missing_gaps_json": "TEXT DEFAULT '[]'",
            "parser_confidence": "REAL DEFAULT 0.9",
            "routing_recommendation": "TEXT DEFAULT 'HUMAN_REVIEW'",
            "hr_score": "REAL",
            "hr_override_reason": "TEXT",
            "feedback_json": "TEXT",
            "interview_slots_json": "TEXT",
            "interview_questions_json": "TEXT",
            "interview_scorecard_json": "TEXT",
            "stage_status": "TEXT DEFAULT 'CV_QUEUED'",
        },
    )
    _add_columns(
        conn,
        "decisions",
        {"hr_score": "REAL", "agent_score": "REAL", "application_id": "TEXT"},
    )
    _add_columns(
        conn,
        "audit_log",
        {
            "entity_type": "TEXT DEFAULT 'UNKNOWN'",
            "actor_user_id": "TEXT",
            "actor_role": "TEXT",
            "from_status": "TEXT",
            "to_status": "TEXT",
            "metadata_json": "TEXT DEFAULT '{}'",
        },
    )
    conn.execute("UPDATE jobs SET status='JOB_PUBLISHED' WHERE status IS NULL OR status='PUBLISHED'")


def _migration_2_profiles_and_applications(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS candidate_profiles (
            id TEXT PRIMARY KEY,
            user_id TEXT,
            full_name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS applications (
            id TEXT PRIMARY KEY,
            candidate_profile_id TEXT NOT NULL,
            job_id TEXT NOT NULL,
            revision_of_id TEXT,
            revision_number INTEGER NOT NULL DEFAULT 1,
            cv_text TEXT,
            cv_file_path TEXT,
            cv_file_name TEXT,
            cv_mime_type TEXT,
            cv_sha256 TEXT,
            cv_size_bytes INTEGER,
            portfolio_link TEXT,
            embedding TEXT,
            score REAL NOT NULL DEFAULT 0,
            mandatory_flags TEXT NOT NULL DEFAULT '[]',
            evidence_json TEXT NOT NULL DEFAULT '[]',
            missing_gaps_json TEXT NOT NULL DEFAULT '[]',
            parser_confidence REAL NOT NULL DEFAULT 0.9,
            routing_recommendation TEXT NOT NULL DEFAULT 'HUMAN_REVIEW',
            hr_score REAL,
            hr_override_reason TEXT,
            feedback_json TEXT,
            feedback_status TEXT NOT NULL DEFAULT 'NONE',
            interview_slots_json TEXT,
            interview_questions_json TEXT,
            interview_scorecard_json TEXT,
            stage_status TEXT NOT NULL DEFAULT 'APPLICATION_SUBMITTED',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY (candidate_profile_id) REFERENCES candidate_profiles(id),
            FOREIGN KEY (job_id) REFERENCES jobs(id),
            FOREIGN KEY (revision_of_id) REFERENCES applications(id)
        );

        CREATE INDEX IF NOT EXISTS idx_jobs_status ON jobs(status);
        CREATE INDEX IF NOT EXISTS idx_applications_job ON applications(job_id);
        CREATE INDEX IF NOT EXISTS idx_applications_profile ON applications(candidate_profile_id);
        CREATE INDEX IF NOT EXISTS idx_applications_stage ON applications(stage_status);
        CREATE INDEX IF NOT EXISTS idx_audit_entity ON audit_log(entity_id, created_at);
        """
    )

    if not _table_exists(conn, "candidates"):
        return
    columns = _columns(conn, "candidates")
    legacy_rows = conn.execute("SELECT * FROM candidates").fetchall()
    for row in legacy_rows:
        record = dict(row)
        application_id = record.get("id") or str(uuid.uuid4())
        if conn.execute("SELECT 1 FROM applications WHERE id=?", (application_id,)).fetchone():
            continue
        email = record.get("email") or f"legacy-{application_id}@local.invalid"
        full_name = record.get("name") or "Ứng viên chưa rõ tên"
        profile = conn.execute("SELECT id FROM candidate_profiles WHERE email=?", (email,)).fetchone()
        profile_id = profile[0] if profile else str(uuid.uuid4())
        now = record.get("created_at") or utc_now()
        if not profile:
            conn.execute(
                "INSERT INTO candidate_profiles (id, full_name, email, created_at, updated_at) VALUES (?,?,?,?,?)",
                (profile_id, full_name, email, now, now),
            )
        stage = record.get("stage_status") or "CV_QUEUED"
        if stage == "REJECTED":
            stage = "NOT_PROCEEDING"
        conn.execute(
            """
            INSERT INTO applications (
                id, candidate_profile_id, job_id, cv_text, portfolio_link, embedding, score,
                mandatory_flags, evidence_json, missing_gaps_json, parser_confidence,
                routing_recommendation, hr_score, hr_override_reason, feedback_json,
                interview_slots_json, interview_questions_json, interview_scorecard_json,
                stage_status, created_at, updated_at
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """,
            (
                application_id,
                profile_id,
                record.get("job_id"),
                record.get("cv_text"),
                record.get("portfolio_link") if "portfolio_link" in columns else None,
                record.get("embedding"),
                record.get("score") or 0,
                record.get("mandatory_flags") or "[]",
                record.get("evidence_json") or "[]",
                record.get("missing_gaps_json") or "[]",
                record.get("parser_confidence") or 0.9,
                record.get("routing_recommendation") or "HUMAN_REVIEW",
                record.get("hr_score"),
                record.get("hr_override_reason"),
                record.get("feedback_json"),
                record.get("interview_slots_json"),
                record.get("interview_questions_json"),
                record.get("interview_scorecard_json"),
                stage,
                now,
                now,
            ),
        )


def _migration_3_job_pdf_and_queue(conn: sqlite3.Connection) -> None:
    _add_columns(
        conn,
        "jobs",
        {
            "responsibilities": "TEXT DEFAULT ''",
            "experience_years": "REAL DEFAULT 0",
            "location": "TEXT DEFAULT ''",
            "work_mode": "TEXT DEFAULT 'Onsite'",
            "interview_process": "TEXT DEFAULT ''",
            "deadline": "TEXT",
            "headcount": "INTEGER DEFAULT 1",
            "salary_public": "INTEGER DEFAULT 0",
            "rubric_version": "INTEGER DEFAULT 1",
            "rubric_approved_by": "TEXT",
            "rubric_approved_at": "TEXT",
        },
    )
    _add_columns(
        conn,
        "applications",
        {
            "parse_status": "TEXT DEFAULT 'PENDING'",
            "parse_error": "TEXT",
            "page_count": "INTEGER",
            "submitted_answers_json": "TEXT DEFAULT '{}'",
            "start_availability": "TEXT",
            "work_preference": "TEXT",
        },
    )
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS processing_jobs (
            id TEXT PRIMARY KEY,
            application_id TEXT NOT NULL UNIQUE,
            status TEXT NOT NULL DEFAULT 'QUEUED',
            priority INTEGER NOT NULL DEFAULT 100,
            retry_count INTEGER NOT NULL DEFAULT 0,
            locked_at TEXT,
            last_error TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY (application_id) REFERENCES applications(id)
        );
        CREATE INDEX IF NOT EXISTS idx_processing_queue
            ON processing_jobs(status, priority, created_at);
        """
    )


def _migration_4_review_feedback_interview_offer(conn: sqlite3.Connection) -> None:
    _add_columns(
        conn,
        "applications",
        {
            "talent_pool_consent": "INTEGER DEFAULT 0",
            "selected_interview_slot_id": "TEXT",
        },
    )
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS decision_scores (
            id TEXT PRIMARY KEY,
            decision_id TEXT NOT NULL,
            application_id TEXT NOT NULL,
            criterion TEXT NOT NULL,
            agent_score REAL,
            hr_score REAL NOT NULL,
            evidence TEXT,
            hr_reason TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY (application_id) REFERENCES applications(id)
        );

        CREATE TABLE IF NOT EXISTS interview_slots (
            id TEXT PRIMARY KEY,
            application_id TEXT NOT NULL,
            starts_at TEXT NOT NULL,
            format TEXT NOT NULL,
            interviewer TEXT NOT NULL,
            meeting_link TEXT,
            selected_at TEXT,
            created_at TEXT NOT NULL,
            UNIQUE (interviewer, starts_at),
            FOREIGN KEY (application_id) REFERENCES applications(id)
        );

        CREATE TABLE IF NOT EXISTS offers (
            id TEXT PRIMARY KEY,
            application_id TEXT NOT NULL UNIQUE,
            salary TEXT NOT NULL,
            conditions TEXT,
            status TEXT NOT NULL DEFAULT 'OFFER_PENDING',
            expires_at TEXT,
            created_by TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY (application_id) REFERENCES applications(id)
        );

        CREATE INDEX IF NOT EXISTS idx_decision_scores_application
            ON decision_scores(application_id, created_at);
        CREATE INDEX IF NOT EXISTS idx_interview_slots_application
            ON interview_slots(application_id, starts_at);
        """
    )
MIGRATIONS = {
    1: _migration_1_expand_legacy_schema,
    2: _migration_2_profiles_and_applications,
    3: _migration_3_job_pdf_and_queue,
    4: _migration_4_review_feedback_interview_offer,
}


def run_migrations(conn: sqlite3.Connection) -> int:
    """Apply every pending migration in one transaction and return the version."""
    _base_schema(conn)
    applied = {row[0] for row in conn.execute("SELECT version FROM schema_migrations")}
    for version in range(1, LATEST_SCHEMA_VERSION + 1):
        if version in applied:
            continue
        MIGRATIONS[version](conn)
        conn.execute(
            "INSERT INTO schema_migrations (version, applied_at) VALUES (?,?)",
            (version, utc_now()),
        )
    return LATEST_SCHEMA_VERSION
