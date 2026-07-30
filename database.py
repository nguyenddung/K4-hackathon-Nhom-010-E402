"""SQLite persistence, migrations, authentication, RBAC, and audited transitions."""

from __future__ import annotations

import base64
import datetime
import hashlib
import hmac
import json
import os
import sqlite3
import uuid
from pathlib import Path
from typing import Any

from config import DB_PATH
from config import MAX_CV_REVISIONS
from domain import (
    ApplicationStatus,
    FeedbackStatus,
    JobStatus,
    Role,
    normalize_application_status,
    normalize_job_status,
    require_role,
    validate_application_transition,
    validate_job_transition,
)
from migrations import run_migrations


PBKDF2_ITERATIONS = 390_000


def utc_now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def get_conn() -> sqlite3.Connection:
    db_path = Path(DB_PATH)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    conn.execute("PRAGMA busy_timeout=5000")
    return conn


def hash_password(password: str) -> str:
    """Hash a password with PBKDF2-HMAC-SHA256 and a per-password salt."""
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, PBKDF2_ITERATIONS)
    return "pbkdf2_sha256${}${}${}".format(
        PBKDF2_ITERATIONS,
        base64.urlsafe_b64encode(salt).decode("ascii"),
        base64.urlsafe_b64encode(digest).decode("ascii"),
    )


def _verify_password(password: str, stored_hash: str) -> tuple[bool, bool]:
    """Return (valid, needs_upgrade), supporting the legacy unsalted SHA-256 hash."""
    if stored_hash.startswith("pbkdf2_sha256$"):
        try:
            _, iterations, encoded_salt, encoded_digest = stored_hash.split("$", 3)
            salt = base64.urlsafe_b64decode(encoded_salt.encode("ascii"))
            expected = base64.urlsafe_b64decode(encoded_digest.encode("ascii"))
            actual = hashlib.pbkdf2_hmac(
                "sha256", password.encode("utf-8"), salt, int(iterations)
            )
            return hmac.compare_digest(actual, expected), False
        except (ValueError, TypeError):
            return False, False

    legacy = hashlib.sha256(password.encode("utf-8")).hexdigest()
    valid = hmac.compare_digest(legacy, stored_hash)
    return valid, valid


def _insert_audit(
    conn: sqlite3.Connection,
    entity_id: str,
    action: str,
    detail: str,
    *,
    entity_type: str = "UNKNOWN",
    actor_user_id: str | None = None,
    actor_role: str | None = None,
    from_status: str | None = None,
    to_status: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> None:
    conn.execute(
        """
        INSERT INTO audit_log (
            id, entity_id, action, detail, created_at, entity_type,
            actor_user_id, actor_role, from_status, to_status, metadata_json
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?)
        """,
        (
            str(uuid.uuid4()),
            entity_id,
            action,
            detail,
            utc_now(),
            entity_type,
            actor_user_id,
            actor_role,
            from_status,
            to_status,
            json.dumps(metadata or {}, ensure_ascii=False),
        ),
    )


def init_db() -> None:
    conn = get_conn()
    try:
        with conn:
            run_migrations(conn)
            defaults = (
                ("hr_admin", "hr@topiklearn.com", "HR", "HR Manager (Admin)"),
                ("candidate1", "candidate@example.com", "CANDIDATE", "Nguyễn Văn Ứng Viên"),
            )
            for username, email, role, full_name in defaults:
                if not conn.execute("SELECT 1 FROM users WHERE email=?", (email,)).fetchone():
                    conn.execute(
                        """
                        INSERT INTO users (id, username, email, password_hash, role, full_name, created_at)
                        VALUES (?,?,?,?,?,?,?)
                        """,
                        (
                            str(uuid.uuid4()),
                            username,
                            email,
                            hash_password("123456"),
                            role,
                            full_name,
                            utc_now(),
                        ),
                    )
    finally:
        conn.close()


def log_audit(
    entity_id: str,
    action: str,
    detail: str,
    *,
    entity_type: str = "UNKNOWN",
    actor_user_id: str | None = None,
    actor_role: str | None = None,
    from_status: str | None = None,
    to_status: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> None:
    conn = get_conn()
    try:
        with conn:
            _insert_audit(
                conn,
                entity_id,
                action,
                detail,
                entity_type=entity_type,
                actor_user_id=actor_user_id,
                actor_role=actor_role,
                from_status=from_status,
                to_status=to_status,
                metadata=metadata,
            )
    finally:
        conn.close()


def create_user(email: str, password: str, role: str, full_name: str) -> bool:
    normalized_email = email.strip().lower()
    normalized_role = Role(role)
    if normalized_role is not Role.CANDIDATE:
        return False
    conn = get_conn()
    user_id = str(uuid.uuid4())
    try:
        with conn:
            conn.execute(
                """
                INSERT INTO users (id, username, email, password_hash, role, full_name, created_at)
                VALUES (?,?,?,?,?,?,?)
                """,
                (
                    user_id,
                    normalized_email,
                    normalized_email,
                    hash_password(password),
                    normalized_role.value,
                    full_name.strip(),
                    utc_now(),
                ),
            )
            _insert_audit(
                conn,
                user_id,
                "USER_REGISTER",
                f"Đăng ký tài khoản ứng viên: {normalized_email}",
                entity_type="USER",
                actor_user_id=user_id,
                actor_role=normalized_role.value,
            )
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def verify_user_login(email: str, password: str):
    normalized_email = email.strip().lower()
    conn = get_conn()
    try:
        user = conn.execute("SELECT * FROM users WHERE email=?", (normalized_email,)).fetchone()
        if not user:
            return None
        valid, needs_upgrade = _verify_password(password, user["password_hash"])
        if not valid:
            return None
        with conn:
            if needs_upgrade:
                conn.execute(
                    "UPDATE users SET password_hash=? WHERE id=?",
                    (hash_password(password), user["id"]),
                )
            _insert_audit(
                conn,
                user["id"],
                "USER_LOGIN",
                f"Đăng nhập thành công: {user['full_name']} ({user['role']})",
                entity_type="USER",
                actor_user_id=user["id"],
                actor_role=user["role"],
            )
        return conn.execute("SELECT * FROM users WHERE id=?", (user["id"],)).fetchone()
    finally:
        conn.close()


def get_all_jobs(*, published_only: bool = False):
    conn = get_conn()
    try:
        if published_only:
            return conn.execute(
                "SELECT * FROM jobs WHERE status=? ORDER BY created_at DESC",
                (JobStatus.PUBLISHED.value,),
            ).fetchall()
        return conn.execute("SELECT * FROM jobs ORDER BY created_at DESC").fetchall()
    finally:
        conn.close()


def get_job_by_id(job_id: str):
    conn = get_conn()
    try:
        return conn.execute("SELECT * FROM jobs WHERE id=?", (job_id,)).fetchone()
    finally:
        conn.close()


def create_job(
    job_id,
    title,
    description,
    level="Middle",
    mandatory_skills="",
    preferred_skills="",
    salary="Thỏa thuận",
    timeline="30 ngày",
    embedding="[]",
    rubric_json="[]",
    vague_warnings_json="[]",
    status=JobStatus.DRAFT.value,
    *,
    responsibilities: str = "",
    experience_years: float = 0,
    location: str = "",
    work_mode: str = "Onsite",
    interview_process: str = "",
    deadline: str | None = None,
    headcount: int = 1,
    salary_public: bool = False,
    actor_user_id: str | None = None,
    actor_role: str = Role.HR.value,
):
    require_role(actor_role, {Role.HR})
    normalized_status = normalize_job_status(status)
    now = utc_now()
    conn = get_conn()
    try:
        with conn:
            conn.execute(
                """
                INSERT INTO jobs (
                    id, title, description, level, mandatory_skills, preferred_skills,
                    salary, timeline, embedding, rubric_json, vague_warnings_json,
                    status, created_at, updated_at, responsibilities, experience_years,
                    location, work_mode, interview_process, deadline, headcount, salary_public
                ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                """,
                (
                    job_id,
                    title,
                    description,
                    level,
                    mandatory_skills,
                    preferred_skills,
                    salary,
                    timeline,
                    embedding,
                    rubric_json,
                    vague_warnings_json,
                    normalized_status.value,
                    now,
                    now,
                    responsibilities,
                    experience_years,
                    location,
                    work_mode,
                    interview_process,
                    deadline,
                    headcount,
                    1 if salary_public else 0,
                ),
            )
            _insert_audit(
                conn,
                job_id,
                "CREATE_JOB",
                f"Tạo Job: {title}",
                entity_type="JOB",
                actor_user_id=actor_user_id,
                actor_role=actor_role,
                to_status=normalized_status.value,
            )
    finally:
        conn.close()


def update_job_status(
    job_id: str,
    status: str,
    rubric_json: str | None = None,
    *,
    actor_user_id: str | None = None,
    actor_role: str = Role.HR.value,
    reason: str = "",
):
    require_role(actor_role, {Role.HR})
    conn = get_conn()
    try:
        with conn:
            job = conn.execute("SELECT status FROM jobs WHERE id=?", (job_id,)).fetchone()
            if not job:
                raise ValueError("Không tìm thấy Job.")
            current, target = validate_job_transition(job["status"], status)
            if rubric_json is not None:
                conn.execute(
                    "UPDATE jobs SET status=?, rubric_json=?, updated_at=? WHERE id=?",
                    (target.value, rubric_json, utc_now(), job_id),
                )
            else:
                conn.execute(
                    "UPDATE jobs SET status=?, updated_at=? WHERE id=?",
                    (target.value, utc_now(), job_id),
                )
            if target is JobStatus.APPROVED:
                conn.execute(
                    "UPDATE jobs SET rubric_approved_by=?, rubric_approved_at=? WHERE id=?",
                    (actor_user_id, utc_now(), job_id),
                )
            _insert_audit(
                conn,
                job_id,
                "UPDATE_JOB_STATUS",
                reason or f"Chuyển trạng thái Job sang {target.value}",
                entity_type="JOB",
                actor_user_id=actor_user_id,
                actor_role=actor_role,
                from_status=current.value,
                to_status=target.value,
            )
    finally:
        conn.close()


def update_job_rubric(
    job_id: str,
    rubric: list[dict[str, Any]],
    *,
    actor_user_id: str | None,
    actor_role: str = Role.HR.value,
) -> None:
    require_role(actor_role, {Role.HR})
    conn = get_conn()
    try:
        with conn:
            job = conn.execute("SELECT status, rubric_version FROM jobs WHERE id=?", (job_id,)).fetchone()
            if not job:
                raise ValueError("Không tìm thấy Job.")
            status = normalize_job_status(job["status"])
            if status not in {JobStatus.DRAFT, JobStatus.RUBRIC_REVIEW}:
                raise ValueError("Chỉ được sửa rubric khi Job đang Draft hoặc Rubric Review.")
            version = int(job["rubric_version"] or 0) + 1
            conn.execute(
                "UPDATE jobs SET rubric_json=?, rubric_version=?, updated_at=? WHERE id=?",
                (json.dumps(rubric, ensure_ascii=False), version, utc_now(), job_id),
            )
            _insert_audit(
                conn,
                job_id,
                "UPDATE_RUBRIC",
                f"HR cập nhật rubric phiên bản {version}",
                entity_type="JOB",
                actor_user_id=actor_user_id,
                actor_role=actor_role,
                metadata={"rubric_version": version, "criteria_count": len(rubric)},
            )
    finally:
        conn.close()


def _get_or_create_profile(
    conn: sqlite3.Connection,
    *,
    name: str,
    email: str,
) -> str:
    normalized_email = email.strip().lower()
    profile = conn.execute(
        "SELECT id FROM candidate_profiles WHERE email=?", (normalized_email,)
    ).fetchone()
    now = utc_now()
    if profile:
        conn.execute(
            "UPDATE candidate_profiles SET full_name=?, updated_at=? WHERE id=?",
            (name.strip(), now, profile["id"]),
        )
        return profile["id"]
    user = conn.execute("SELECT id FROM users WHERE email=?", (normalized_email,)).fetchone()
    profile_id = str(uuid.uuid4())
    conn.execute(
        """
        INSERT INTO candidate_profiles (id, user_id, full_name, email, created_at, updated_at)
        VALUES (?,?,?,?,?,?)
        """,
        (profile_id, user["id"] if user else None, name.strip(), normalized_email, now, now),
    )
    return profile_id


def save_candidate_application(
    candidate_id,
    job_id,
    name,
    email,
    cv_text,
    portfolio_link,
    embedding,
    score,
    mandatory_flags,
    evidence_json,
    missing_gaps_json,
    parser_confidence,
    routing_recommendation,
    stage_status=ApplicationStatus.SUBMITTED.value,
    *,
    revision_of_id: str | None = None,
    cv_file_path: str | None = None,
    cv_file_name: str | None = None,
    cv_mime_type: str | None = None,
    cv_sha256: str | None = None,
    cv_size_bytes: int | None = None,
    parse_status: str = "PENDING",
    parse_error: str | None = None,
    page_count: int | None = None,
    submitted_answers: dict[str, Any] | None = None,
    start_availability: str | None = None,
    work_preference: str | None = None,
    actor_user_id: str | None = None,
    actor_role: str = Role.CANDIDATE.value,
):
    require_role(actor_role, {Role.CANDIDATE})
    normalized_status = normalize_application_status(stage_status)
    now = utc_now()
    conn = get_conn()
    try:
        with conn:
            if not conn.execute(
                "SELECT 1 FROM jobs WHERE id=? AND status=?",
                (job_id, JobStatus.PUBLISHED.value),
            ).fetchone():
                raise ValueError("Chỉ có thể nộp hồ sơ vào Job đã được đăng.")
            profile_id = _get_or_create_profile(conn, name=name, email=email)
            revision_number = 1
            revision_root = None
            if revision_of_id:
                base = conn.execute(
                    "SELECT * FROM applications WHERE id=?", (revision_of_id,)
                ).fetchone()
                if not base or base["candidate_profile_id"] != profile_id or base["job_id"] != job_id:
                    raise PermissionError("Không có quyền cập nhật hồ sơ này.")
                if base["stage_status"] != ApplicationStatus.NEED_MORE_INFORMATION.value:
                    raise ValueError("Chỉ được nộp lại khi HR yêu cầu bổ sung thông tin.")
                if base["feedback_status"] != FeedbackStatus.SENT.value:
                    raise ValueError("HR phải gửi feedback trước khi ứng viên nộp lại CV.")
                revision_root = base["revision_of_id"] or base["id"]
                latest = conn.execute(
                    """
                    SELECT MAX(revision_number) FROM applications
                    WHERE id=? OR revision_of_id=?
                    """,
                    (revision_root, revision_root),
                ).fetchone()[0] or 1
                if latest >= MAX_CV_REVISIONS + 1:
                    raise ValueError(f"Hồ sơ đã đạt giới hạn {MAX_CV_REVISIONS} lần cập nhật.")
                revision_number = int(latest) + 1
            conn.execute(
                """
                INSERT INTO applications (
                    id, candidate_profile_id, job_id, revision_of_id, revision_number,
                    cv_text, portfolio_link, embedding,
                    score, mandatory_flags, evidence_json, missing_gaps_json,
                    parser_confidence, routing_recommendation, stage_status, created_at, updated_at,
                    cv_file_path, cv_file_name, cv_mime_type, cv_sha256, cv_size_bytes,
                    parse_status, parse_error, page_count, submitted_answers_json,
                    start_availability, work_preference
                ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                """,
                (
                    candidate_id,
                    profile_id,
                    job_id,
                    revision_root,
                    revision_number,
                    cv_text,
                    portfolio_link,
                    embedding,
                    score,
                    json.dumps(mandatory_flags, ensure_ascii=False),
                    json.dumps(evidence_json, ensure_ascii=False),
                    json.dumps(missing_gaps_json, ensure_ascii=False),
                    parser_confidence,
                    routing_recommendation,
                    normalized_status.value,
                    now,
                    now,
                    cv_file_path,
                    cv_file_name,
                    cv_mime_type,
                    cv_sha256,
                    cv_size_bytes,
                    parse_status,
                    parse_error,
                    page_count,
                    json.dumps(submitted_answers or {}, ensure_ascii=False),
                    start_availability,
                    work_preference,
                ),
            )
            _insert_audit(
                conn,
                candidate_id,
                "SUBMIT_CV",
                f"Ứng viên {name} nộp hồ sơ cho Job {job_id}",
                entity_type="APPLICATION",
                actor_user_id=actor_user_id,
                actor_role=actor_role,
                to_status=normalized_status.value,
                metadata={"revision_of_id": revision_root, "revision_number": revision_number},
            )
    finally:
        conn.close()


def enqueue_application(application_id: str, *, priority: int = 100) -> str:
    queue_id = str(uuid.uuid4())
    now = utc_now()
    conn = get_conn()
    try:
        with conn:
            conn.execute(
                """
                INSERT INTO processing_jobs (id, application_id, status, priority, created_at, updated_at)
                VALUES (?,?,?,?,?,?)
                ON CONFLICT(application_id) DO UPDATE SET
                    status='QUEUED', priority=excluded.priority, updated_at=excluded.updated_at
                """,
                (queue_id, application_id, "QUEUED", priority, now, now),
            )
            _insert_audit(
                conn,
                application_id,
                "ENQUEUE_CV",
                "Đưa CV vào hàng đợi xử lý",
                entity_type="APPLICATION",
                actor_role=Role.AGENT.value,
                metadata={"priority": priority},
            )
        return queue_id
    finally:
        conn.close()


def update_processing_job(
    application_id: str,
    status: str,
    *,
    error: str | None = None,
) -> None:
    allowed = {"QUEUED", "PROCESSING", "COMPLETED", "FAILED", "MANUAL_REVIEW"}
    if status not in allowed:
        raise ValueError("Trạng thái hàng đợi không hợp lệ.")
    conn = get_conn()
    try:
        with conn:
            row = conn.execute(
                "SELECT retry_count FROM processing_jobs WHERE application_id=?", (application_id,)
            ).fetchone()
            if not row:
                raise ValueError("Hồ sơ chưa có trong hàng đợi.")
            retry_count = int(row["retry_count"] or 0) + (1 if status == "FAILED" else 0)
            conn.execute(
                """
                UPDATE processing_jobs
                SET status=?, retry_count=?, last_error=?, locked_at=?, updated_at=?
                WHERE application_id=?
                """,
                (
                    status,
                    retry_count,
                    error,
                    utc_now() if status == "PROCESSING" else None,
                    utc_now(),
                    application_id,
                ),
            )
    finally:
        conn.close()


def save_application_analysis(
    application_id: str,
    *,
    embedding: str,
    score: float,
    mandatory_flags: list,
    evidence: list,
    gaps: list,
    parser_confidence: float,
    routing_recommendation: str,
) -> None:
    if not 0 <= float(score) <= 100:
        raise ValueError("Điểm Agent phải nằm trong khoảng 0–100.")
    if not 0 <= float(parser_confidence) <= 1:
        raise ValueError("Parser confidence phải nằm trong khoảng 0–1.")
    if float(score) > 0 and not evidence:
        raise ValueError("Kết quả có điểm phải kèm scorecard bằng chứng.")
    for index, item in enumerate(evidence, start=1):
        if not str(item.get("criterion", "")).strip():
            raise ValueError(f"Bằng chứng số {index} thiếu tiêu chí.")
        if not str(item.get("evidence_quote", "")).strip():
            raise ValueError(f"Bằng chứng số {index} thiếu trích dẫn CV.")
        confidence = float(item.get("confidence", 0))
        if not 0 <= confidence <= 1:
            raise ValueError(f"Confidence của bằng chứng số {index} không hợp lệ.")

    if parser_confidence < 0.65 or mandatory_flags:
        safe_routing = "HUMAN_REVIEW"
    elif score >= 80:
        safe_routing = "SHORTLIST_RECOMMENDED"
    elif score >= 60:
        safe_routing = "HUMAN_REVIEW"
    elif score >= 40:
        safe_routing = "NEED_MORE_EVIDENCE"
    else:
        safe_routing = "LOW_MATCH_REVIEW"
    if routing_recommendation not in {
        "SHORTLIST_RECOMMENDED", "HUMAN_REVIEW", "NEED_MORE_EVIDENCE", "LOW_MATCH_REVIEW"
    }:
        routing_recommendation = safe_routing
    elif routing_recommendation != safe_routing:
        routing_recommendation = safe_routing
    conn = get_conn()
    try:
        with conn:
            if not conn.execute("SELECT 1 FROM applications WHERE id=?", (application_id,)).fetchone():
                raise ValueError("Không tìm thấy hồ sơ ứng tuyển.")
            conn.execute(
                """
                UPDATE applications
                SET embedding=?, score=?, mandatory_flags=?, evidence_json=?, missing_gaps_json=?,
                    parser_confidence=?, routing_recommendation=?, updated_at=?
                WHERE id=?
                """,
                (
                    embedding,
                    score,
                    json.dumps(mandatory_flags, ensure_ascii=False),
                    json.dumps(evidence, ensure_ascii=False),
                    json.dumps(gaps, ensure_ascii=False),
                    parser_confidence,
                    routing_recommendation,
                    utc_now(),
                    application_id,
                ),
            )
            _insert_audit(
                conn,
                application_id,
                "SAVE_AGENT_ANALYSIS",
                "Lưu kết quả phân tích CV có bằng chứng",
                entity_type="APPLICATION",
                actor_role=Role.AGENT.value,
                metadata={"score": score, "routing": routing_recommendation},
            )
    finally:
        conn.close()


def get_processing_jobs():
    conn = get_conn()
    try:
        return conn.execute(
            """
            SELECT q.*, p.full_name AS candidate_name, j.title AS job_title,
                   a.stage_status, a.parser_confidence, a.routing_recommendation
            FROM processing_jobs q
            JOIN applications a ON a.id=q.application_id
            JOIN candidate_profiles p ON p.id=a.candidate_profile_id
            JOIN jobs j ON j.id=a.job_id
            ORDER BY q.priority ASC, q.created_at ASC
            """
        ).fetchall()
    finally:
        conn.close()


APPLICATION_SELECT = """
    SELECT
        a.*,
        p.full_name AS name,
        p.email AS email,
        j.title AS job_title
    FROM applications a
    JOIN candidate_profiles p ON p.id=a.candidate_profile_id
    LEFT JOIN jobs j ON j.id=a.job_id
"""


def get_candidates_by_job(job_id: str):
    conn = get_conn()
    try:
        return conn.execute(
            APPLICATION_SELECT + " WHERE a.job_id=? ORDER BY a.created_at DESC", (job_id,)
        ).fetchall()
    finally:
        conn.close()


def get_candidates_by_email(email: str):
    conn = get_conn()
    try:
        return conn.execute(
            APPLICATION_SELECT + " WHERE p.email=? ORDER BY a.created_at DESC",
            (email.strip().lower(),),
        ).fetchall()
    finally:
        conn.close()


def get_all_candidates():
    conn = get_conn()
    try:
        return conn.execute(APPLICATION_SELECT + " ORDER BY a.created_at DESC").fetchall()
    finally:
        conn.close()


def transition_application_status(
    application_id: str,
    target_status: str,
    *,
    actor_user_id: str | None,
    actor_role: str,
    reason: str,
) -> None:
    role = Role(actor_role)
    target = normalize_application_status(target_status)
    if target in {
        ApplicationStatus.SHORTLISTED,
        ApplicationStatus.TALENT_POOL,
        ApplicationStatus.NOT_PROCEEDING,
        ApplicationStatus.OFFER_PENDING,
        ApplicationStatus.HIRED,
    }:
        require_role(role, {Role.HR})
    conn = get_conn()
    try:
        with conn:
            row = conn.execute(
                "SELECT stage_status, talent_pool_consent FROM applications WHERE id=?", (application_id,)
            ).fetchone()
            if not row:
                raise ValueError("Không tìm thấy hồ sơ ứng tuyển.")
            if target is ApplicationStatus.TALENT_POOL and not row["talent_pool_consent"]:
                raise ValueError("Ứng viên chưa đồng ý lưu hồ sơ vào Talent Pool.")
            current, target = validate_application_transition(row["stage_status"], target)
            conn.execute(
                "UPDATE applications SET stage_status=?, updated_at=? WHERE id=?",
                (target.value, utc_now(), application_id),
            )
            _insert_audit(
                conn,
                application_id,
                "APPLICATION_STATUS_CHANGED",
                reason,
                entity_type="APPLICATION",
                actor_user_id=actor_user_id,
                actor_role=role.value,
                from_status=current.value,
                to_status=target.value,
            )
    finally:
        conn.close()


def update_hr_decision(
    candidate_id: str,
    decision: str,
    hr_score: float,
    agent_score: float,
    note: str,
    new_stage: str,
    *,
    criterion_scores: list[dict[str, Any]] | None = None,
    actor_user_id: str | None = None,
    actor_role: str = Role.HR.value,
):
    require_role(actor_role, {Role.HR})
    target = normalize_application_status(new_stage)
    allowed_decisions = {
        ApplicationStatus.NEED_MORE_INFORMATION,
        ApplicationStatus.SHORTLISTED,
        ApplicationStatus.TALENT_POOL,
        ApplicationStatus.NOT_PROCEEDING,
    }
    if target not in allowed_decisions:
        raise ValueError("Quyết định HR không hợp lệ ở bước review CV.")
    if target is ApplicationStatus.NOT_PROCEEDING and not note.strip():
        raise ValueError("Bạn đang chọn Từ chối ứng viên. Vui lòng nhập lý do trước khi lưu.")
    if abs(float(hr_score) - float(agent_score)) > 1e-9 and not note.strip():
        raise ValueError(
            f"Điểm HR ({hr_score:g}) khác điểm Agent ({agent_score:g}). "
            "Vui lòng nhập lý do điều chỉnh trước khi lưu; ứng viên chưa bị từ chối."
        )

    conn = get_conn()
    try:
        with conn:
            row = conn.execute(
                "SELECT stage_status, talent_pool_consent FROM applications WHERE id=?", (candidate_id,)
            ).fetchone()
            if not row:
                raise ValueError("Không tìm thấy hồ sơ ứng tuyển.")
            current = normalize_application_status(row["stage_status"])
            if target is ApplicationStatus.TALENT_POOL and not row["talent_pool_consent"]:
                raise ValueError("Ứng viên chưa đồng ý lưu hồ sơ vào Talent Pool.")
            if current is ApplicationStatus.ANALYZED:
                conn.execute(
                    "UPDATE applications SET stage_status=? WHERE id=?",
                    (ApplicationStatus.HR_REVIEW_PENDING.value, candidate_id),
                )
                _insert_audit(
                    conn,
                    candidate_id,
                    "APPLICATION_STATUS_CHANGED",
                    "Hồ sơ đã phân tích, chuyển sang hàng đợi HR",
                    entity_type="APPLICATION",
                    actor_role=Role.AGENT.value,
                    from_status=current.value,
                    to_status=ApplicationStatus.HR_REVIEW_PENDING.value,
                )
                current = ApplicationStatus.HR_REVIEW_PENDING
            current, target = validate_application_transition(current, target)
            decision_id = str(uuid.uuid4())
            conn.execute(
                """
                INSERT INTO decisions (
                    id, candidate_id, application_id, decision, hr_score, agent_score, note, created_at
                ) VALUES (?,?,?,?,?,?,?,?)
                """,
                (
                    decision_id,
                    candidate_id,
                    candidate_id,
                    decision,
                    hr_score,
                    agent_score,
                    note.strip(),
                    utc_now(),
                ),
            )
            for item in criterion_scores or []:
                conn.execute(
                    """
                    INSERT INTO decision_scores (
                        id, decision_id, application_id, criterion, agent_score,
                        hr_score, evidence, hr_reason, created_at
                    ) VALUES (?,?,?,?,?,?,?,?,?)
                    """,
                    (
                        str(uuid.uuid4()),
                        decision_id,
                        candidate_id,
                        str(item.get("criterion", "Tiêu chí")),
                        item.get("agent_score"),
                        float(item.get("hr_score", 0)),
                        str(item.get("evidence", "")),
                        str(item.get("hr_reason", "")),
                        utc_now(),
                    ),
                )
            conn.execute(
                """
                UPDATE applications
                SET hr_score=?, hr_override_reason=?, stage_status=?, updated_at=?
                WHERE id=?
                """,
                (hr_score, note.strip(), target.value, utc_now(), candidate_id),
            )
            _insert_audit(
                conn,
                candidate_id,
                "HR_DECISION",
                note.strip() or f"HR chọn {decision}",
                entity_type="APPLICATION",
                actor_user_id=actor_user_id,
                actor_role=actor_role,
                from_status=current.value,
                to_status=target.value,
                metadata={"decision": decision, "agent_score": agent_score, "hr_score": hr_score},
            )
    finally:
        conn.close()


def get_decision_scores(application_id: str):
    conn = get_conn()
    try:
        return conn.execute(
            "SELECT * FROM decision_scores WHERE application_id=? ORDER BY created_at DESC",
            (application_id,),
        ).fetchall()
    finally:
        conn.close()


def save_candidate_feedback(
    candidate_id: str,
    feedback_json: dict,
    *,
    actor_user_id: str | None = None,
    actor_role: str = Role.HR.value,
):
    require_role(actor_role, {Role.HR})
    conn = get_conn()
    try:
        with conn:
            if not conn.execute("SELECT 1 FROM applications WHERE id=?", (candidate_id,)).fetchone():
                raise ValueError("Không tìm thấy hồ sơ ứng tuyển.")
            conn.execute(
                """
                UPDATE applications
                SET feedback_json=?, feedback_status=?, updated_at=? WHERE id=?
                """,
                (
                    json.dumps(feedback_json, ensure_ascii=False),
                    FeedbackStatus.GENERATED.value,
                    utc_now(),
                    candidate_id,
                ),
            )
            _insert_audit(
                conn,
                candidate_id,
                "GENERATE_FEEDBACK",
                "Tạo bản nháp feedback; chưa công khai cho ứng viên",
                entity_type="APPLICATION",
                actor_user_id=actor_user_id,
                actor_role=actor_role,
                to_status=FeedbackStatus.GENERATED.value,
            )
    finally:
        conn.close()


def approve_candidate_feedback(
    application_id: str,
    feedback_json: dict,
    *,
    actor_user_id: str | None,
    actor_role: str = Role.HR.value,
) -> None:
    require_role(actor_role, {Role.HR})
    conn = get_conn()
    try:
        with conn:
            row = conn.execute(
                "SELECT feedback_status FROM applications WHERE id=?", (application_id,)
            ).fetchone()
            if not row or row["feedback_status"] != FeedbackStatus.GENERATED.value:
                raise ValueError("Feedback phải ở trạng thái đã tạo nháp trước khi HR duyệt.")
            conn.execute(
                """
                UPDATE applications
                SET feedback_json=?, feedback_status=?, updated_at=? WHERE id=?
                """,
                (
                    json.dumps(feedback_json, ensure_ascii=False),
                    FeedbackStatus.HR_APPROVED.value,
                    utc_now(),
                    application_id,
                ),
            )
            _insert_audit(
                conn,
                application_id,
                "APPROVE_FEEDBACK",
                "HR duyệt nội dung feedback",
                entity_type="APPLICATION",
                actor_user_id=actor_user_id,
                actor_role=actor_role,
                from_status=FeedbackStatus.GENERATED.value,
                to_status=FeedbackStatus.HR_APPROVED.value,
            )
    finally:
        conn.close()


def send_candidate_feedback(
    application_id: str,
    *,
    actor_user_id: str | None,
    actor_role: str = Role.HR.value,
) -> None:
    require_role(actor_role, {Role.HR})
    conn = get_conn()
    try:
        with conn:
            row = conn.execute(
                "SELECT feedback_status FROM applications WHERE id=?", (application_id,)
            ).fetchone()
            if not row or row["feedback_status"] != FeedbackStatus.HR_APPROVED.value:
                raise ValueError("Feedback phải được HR duyệt trước khi gửi.")
            conn.execute(
                "UPDATE applications SET feedback_status=?, updated_at=? WHERE id=?",
                (FeedbackStatus.SENT.value, utc_now(), application_id),
            )
            _insert_audit(
                conn,
                application_id,
                "SEND_FEEDBACK",
                "Công khai feedback đã duyệt cho ứng viên",
                entity_type="APPLICATION",
                actor_user_id=actor_user_id,
                actor_role=actor_role,
                from_status=FeedbackStatus.HR_APPROVED.value,
                to_status=FeedbackStatus.SENT.value,
            )
    finally:
        conn.close()


def set_talent_pool_consent(
    application_id: str,
    consent: bool,
    *,
    candidate_email: str,
) -> None:
    conn = get_conn()
    try:
        with conn:
            row = conn.execute(
                """
                SELECT a.id, p.user_id FROM applications a
                JOIN candidate_profiles p ON p.id=a.candidate_profile_id
                WHERE a.id=? AND p.email=?
                """,
                (application_id, candidate_email.strip().lower()),
            ).fetchone()
            if not row:
                raise PermissionError("Không có quyền cập nhật hồ sơ này.")
            conn.execute(
                "UPDATE applications SET talent_pool_consent=?, updated_at=? WHERE id=?",
                (1 if consent else 0, utc_now(), application_id),
            )
            _insert_audit(
                conn,
                application_id,
                "TALENT_POOL_CONSENT",
                "Ứng viên đồng ý lưu Talent Pool" if consent else "Ứng viên rút consent Talent Pool",
                entity_type="APPLICATION",
                actor_user_id=row["user_id"],
                actor_role=Role.CANDIDATE.value,
                metadata={"consent": consent},
            )
    finally:
        conn.close()


def save_interview_data(
    candidate_id: str,
    interview_questions_json: dict,
    interview_slots_json: list,
    *,
    actor_user_id: str | None = None,
    actor_role: str = Role.HR.value,
):
    require_role(actor_role, {Role.HR})
    conn = get_conn()
    try:
        with conn:
            row = conn.execute(
                "SELECT stage_status FROM applications WHERE id=?", (candidate_id,)
            ).fetchone()
            if not row:
                raise ValueError("Không tìm thấy hồ sơ ứng tuyển.")
            current = normalize_application_status(row["stage_status"])
            target = current
            if current in {ApplicationStatus.SHORTLISTED, ApplicationStatus.NEXT_ROUND}:
                _, target = validate_application_transition(current, ApplicationStatus.INTERVIEW_INVITED)
            conn.execute(
                """
                UPDATE applications
                SET interview_questions_json=?, interview_slots_json=?, stage_status=?, updated_at=?
                WHERE id=?
                """,
                (
                    json.dumps(interview_questions_json, ensure_ascii=False),
                    json.dumps(interview_slots_json, ensure_ascii=False),
                    target.value,
                    utc_now(),
                    candidate_id,
                ),
            )
            for slot in interview_slots_json:
                starts_at = slot.get("starts_at") or f"{slot.get('date')}T{slot.get('time')}:00"
                conn.execute(
                    """
                    INSERT OR IGNORE INTO interview_slots (
                        id, application_id, starts_at, format, interviewer, meeting_link, created_at
                    ) VALUES (?,?,?,?,?,?,?)
                    """,
                    (
                        str(uuid.uuid4()),
                        candidate_id,
                        starts_at,
                        slot.get("format", "Online"),
                        slot.get("interviewer", "HR"),
                        slot.get("meeting_link", ""),
                        utc_now(),
                    ),
                )
            _insert_audit(
                conn,
                candidate_id,
                "CREATE_INTERVIEW",
                "Tạo lời mời, lịch đề xuất và bộ câu hỏi phỏng vấn",
                entity_type="APPLICATION",
                actor_user_id=actor_user_id,
                actor_role=actor_role,
                from_status=current.value,
                to_status=target.value,
            )
    finally:
        conn.close()


def get_interview_slots(application_id: str, *, available_only: bool = False):
    conn = get_conn()
    try:
        sql = "SELECT * FROM interview_slots WHERE application_id=?"
        if available_only:
            sql += " AND selected_at IS NULL"
        sql += " ORDER BY starts_at"
        return conn.execute(sql, (application_id,)).fetchall()
    finally:
        conn.close()


def select_interview_slot(
    application_id: str,
    slot_id: str,
    *,
    candidate_email: str,
) -> None:
    conn = get_conn()
    try:
        with conn:
            application = conn.execute(
                """
                SELECT a.stage_status, p.user_id FROM applications a
                JOIN candidate_profiles p ON p.id=a.candidate_profile_id
                WHERE a.id=? AND p.email=?
                """,
                (application_id, candidate_email.strip().lower()),
            ).fetchone()
            if not application:
                raise PermissionError("Không có quyền chọn lịch cho hồ sơ này.")
            current, target = validate_application_transition(
                application["stage_status"], ApplicationStatus.INTERVIEW_SCHEDULED
            )
            slot = conn.execute(
                """
                SELECT * FROM interview_slots
                WHERE id=? AND application_id=? AND selected_at IS NULL
                """,
                (slot_id, application_id),
            ).fetchone()
            if not slot:
                raise ValueError("Khung giờ không còn khả dụng.")
            now = utc_now()
            conn.execute("UPDATE interview_slots SET selected_at=? WHERE id=?", (now, slot_id))
            conn.execute(
                """
                UPDATE applications SET selected_interview_slot_id=?, stage_status=?, updated_at=?
                WHERE id=?
                """,
                (slot_id, target.value, now, application_id),
            )
            _insert_audit(
                conn,
                application_id,
                "SELECT_INTERVIEW_SLOT",
                f"Ứng viên chọn lịch {slot['starts_at']}",
                entity_type="APPLICATION",
                actor_user_id=application["user_id"],
                actor_role=Role.CANDIDATE.value,
                from_status=current.value,
                to_status=target.value,
                metadata={"slot_id": slot_id, "starts_at": slot["starts_at"]},
            )
    finally:
        conn.close()


def create_offer(
    application_id: str,
    salary: str,
    conditions: str,
    expires_at: str | None,
    *,
    actor_user_id: str | None,
    actor_role: str = Role.HR.value,
) -> str:
    require_role(actor_role, {Role.HR})
    conn = get_conn()
    offer_id = str(uuid.uuid4())
    try:
        with conn:
            row = conn.execute("SELECT stage_status FROM applications WHERE id=?", (application_id,)).fetchone()
            if not row:
                raise ValueError("Không tìm thấy hồ sơ.")
            current = normalize_application_status(row["stage_status"])
            if current is not ApplicationStatus.OFFER_PENDING:
                _, target = validate_application_transition(current, ApplicationStatus.OFFER_PENDING)
                conn.execute(
                    "UPDATE applications SET stage_status=?, updated_at=? WHERE id=?",
                    (target.value, utc_now(), application_id),
                )
            now = utc_now()
            conn.execute(
                """
                INSERT INTO offers (id, application_id, salary, conditions, status, expires_at, created_by, created_at, updated_at)
                VALUES (?,?,?,?,?,?,?,?,?)
                """,
                (offer_id, application_id, salary, conditions, ApplicationStatus.OFFER_PENDING.value, expires_at, actor_user_id, now, now),
            )
            _insert_audit(
                conn,
                application_id,
                "CREATE_OFFER",
                "HR tạo offer",
                entity_type="APPLICATION",
                actor_user_id=actor_user_id,
                actor_role=actor_role,
                from_status=current.value,
                to_status=ApplicationStatus.OFFER_PENDING.value,
            )
        return offer_id
    finally:
        conn.close()


def get_offer_for_application(application_id: str):
    conn = get_conn()
    try:
        return conn.execute("SELECT * FROM offers WHERE application_id=?", (application_id,)).fetchone()
    finally:
        conn.close()


def respond_to_offer(
    application_id: str,
    response: str,
    *,
    candidate_email: str,
) -> None:
    if response not in {ApplicationStatus.OFFER_ACCEPTED.value, ApplicationStatus.OFFER_DECLINED.value}:
        raise ValueError("Phản hồi offer không hợp lệ.")
    conn = get_conn()
    try:
        with conn:
            row = conn.execute(
                """
                SELECT a.stage_status, p.user_id FROM applications a
                JOIN candidate_profiles p ON p.id=a.candidate_profile_id
                WHERE a.id=? AND p.email=?
                """,
                (application_id, candidate_email.strip().lower()),
            ).fetchone()
            offer = conn.execute("SELECT id FROM offers WHERE application_id=?", (application_id,)).fetchone()
            if not row or not offer:
                raise PermissionError("Không có quyền phản hồi offer này.")
            current, target = validate_application_transition(row["stage_status"], response)
            now = utc_now()
            conn.execute(
                "UPDATE applications SET stage_status=?, updated_at=? WHERE id=?",
                (target.value, now, application_id),
            )
            conn.execute(
                "UPDATE offers SET status=?, updated_at=? WHERE id=?",
                (target.value, now, offer["id"]),
            )
            _insert_audit(
                conn,
                application_id,
                "RESPOND_TO_OFFER",
                "Ứng viên chấp nhận offer" if target is ApplicationStatus.OFFER_ACCEPTED else "Ứng viên từ chối offer",
                entity_type="APPLICATION",
                actor_user_id=row["user_id"],
                actor_role=Role.CANDIDATE.value,
                from_status=current.value,
                to_status=target.value,
            )
    finally:
        conn.close()


def save_interview_scorecard(
    candidate_id: str,
    scorecard_json: dict,
    final_stage: str,
    *,
    actor_user_id: str | None = None,
    actor_role: str = Role.HR.value,
):
    require_role(actor_role, {Role.HR, Role.INTERVIEWER})
    conn = get_conn()
    try:
        with conn:
            row = conn.execute(
                "SELECT stage_status FROM applications WHERE id=?", (candidate_id,)
            ).fetchone()
            if not row:
                raise ValueError("Không tìm thấy hồ sơ ứng tuyển.")
            current, target = validate_application_transition(row["stage_status"], final_stage)
            conn.execute(
                """
                UPDATE applications
                SET interview_scorecard_json=?, stage_status=?, updated_at=? WHERE id=?
                """,
                (json.dumps(scorecard_json, ensure_ascii=False), target.value, utc_now(), candidate_id),
            )
            _insert_audit(
                conn,
                candidate_id,
                "SCORECARD_COMPLETED",
                "Lưu scorecard phỏng vấn",
                entity_type="APPLICATION",
                actor_user_id=actor_user_id,
                actor_role=actor_role,
                from_status=current.value,
                to_status=target.value,
            )
    finally:
        conn.close()


def get_audit_logs(entity_id: str | None = None, limit: int = 100):
    conn = get_conn()
    try:
        if entity_id:
            return conn.execute(
                "SELECT * FROM audit_log WHERE entity_id=? ORDER BY created_at DESC LIMIT ?",
                (entity_id, limit),
            ).fetchall()
        return conn.execute(
            "SELECT * FROM audit_log ORDER BY created_at DESC LIMIT ?", (limit,)
        ).fetchall()
    finally:
        conn.close()
