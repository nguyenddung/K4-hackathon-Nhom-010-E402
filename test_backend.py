"""Isolated backend, migration, RBAC, state-machine, and UI smoke tests."""

from __future__ import annotations

import atexit
import io
import json
import os
import sqlite3
import tempfile
import uuid
from pathlib import Path


# Configure an isolated database before importing application modules.
_TEST_DIR = tempfile.TemporaryDirectory(prefix="talentscreen-tests-")
atexit.register(_TEST_DIR.cleanup)
TEST_DB_PATH = str(Path(_TEST_DIR.name) / "talentscreen_test.db")
TEST_CV_PATH = str(Path(_TEST_DIR.name) / "cv-storage")
os.environ["TALENTSCREEN_DB_PATH"] = TEST_DB_PATH
os.environ["TALENTSCREEN_CV_STORAGE"] = TEST_CV_PATH
os.environ["AI_PROVIDER"] = "mock"
os.environ["EMBEDDING_PROVIDER"] = "local"
os.environ["OPENAI_API_KEY"] = ""
os.environ["GEMINI_API_KEY"] = ""
os.environ["GROQ_API_KEY"] = ""

from ai_service import (  # noqa: E402
    analyze_jd_and_create_rubric,
    embed_text,
    generate_interview_questions_and_scorecard,
    parse_and_evaluate_cv_with_evidence,
)
from application_service import submit_pdf_application  # noqa: E402
from cv_service import PDF_MIME_TYPE, PdfValidationError, validate_and_parse_pdf  # noqa: E402
from database import (  # noqa: E402
    approve_candidate_feedback,
    create_offer,
    create_job,
    create_user,
    get_audit_logs,
    get_candidates_by_email,
    get_conn,
    get_interview_slots,
    get_job_by_id,
    init_db,
    respond_to_offer,
    save_candidate_application,
    save_candidate_feedback,
    save_interview_data,
    save_interview_scorecard,
    select_interview_slot,
    send_candidate_feedback,
    set_talent_pool_consent,
    transition_application_status,
    update_hr_decision,
    update_job_status,
    verify_user_login,
)
from domain import (  # noqa: E402
    ApplicationStatus,
    AuthorizationError,
    InvalidTransitionError,
    JobStatus,
    Role,
)


def _create_legacy_schema() -> None:
    conn = sqlite3.connect(TEST_DB_PATH)
    conn.executescript(
        """
        CREATE TABLE jobs (
            id TEXT PRIMARY KEY,
            title TEXT,
            description TEXT,
            embedding TEXT,
            created_at TEXT
        );
        CREATE TABLE candidates (
            id TEXT PRIMARY KEY,
            job_id TEXT,
            name TEXT,
            cv_text TEXT,
            embedding TEXT,
            score REAL,
            reasoning TEXT,
            created_at TEXT
        );
        CREATE TABLE decisions (
            id TEXT PRIMARY KEY,
            candidate_id TEXT,
            decision TEXT,
            note TEXT,
            created_at TEXT
        );
        CREATE TABLE audit_log (
            id TEXT PRIMARY KEY,
            entity_id TEXT,
            action TEXT,
            detail TEXT,
            created_at TEXT
        );
        """
    )
    conn.execute(
        "INSERT INTO jobs VALUES (?,?,?,?,?)",
        ("legacy_job", "Legacy Backend Job", "Legacy JD", "[]", "2026-01-01T00:00:00Z"),
    )
    conn.execute(
        "INSERT INTO candidates VALUES (?,?,?,?,?,?,?,?)",
        (
            "legacy_application",
            "legacy_job",
            "Legacy Candidate",
            "Legacy CV",
            "[]",
            0.5,
            "{}",
            "2026-01-02T00:00:00Z",
        ),
    )
    conn.commit()
    conn.close()


def run_backend_tests() -> None:
    print("=" * 58)
    print("STARTING ISOLATED BACKEND, RBAC & STATE-MACHINE TESTS")
    print("=" * 58)

    print("[1/7] Migrating legacy database without data loss...")
    _create_legacy_schema()
    init_db()
    conn = get_conn()
    assert conn.execute("SELECT MAX(version) FROM schema_migrations").fetchone()[0] == 4
    assert conn.execute("SELECT title FROM jobs WHERE id='legacy_job'").fetchone()[0] == "Legacy Backend Job"
    assert conn.execute("SELECT id FROM applications WHERE id='legacy_application'").fetchone()[0] == "legacy_application"
    job_columns = {row[1] for row in conn.execute("PRAGMA table_info(jobs)")}
    assert {"status", "rubric_json", "mandatory_skills"}.issubset(job_columns)
    conn.close()
    print("  OK - schema v4, legacy Job and application preserved.")

    print("[2/7] Authenticating defaults and upgrading legacy-safe hashes...")
    hr_user = verify_user_login("hr@topiklearn.com", "123456")
    candidate_user = verify_user_login("candidate@example.com", "123456")
    assert hr_user and hr_user["role"] == Role.HR.value
    assert candidate_user and candidate_user["role"] == Role.CANDIDATE.value
    assert verify_user_login("candidate@example.com", "wrong") is None
    print("  OK - HR/Candidate authentication and invalid password handling.")

    print("[3/7] Enforcing safe self-registration RBAC...")
    suffix = uuid.uuid4().hex[:10]
    email = f"candidate-{suffix}@example.com"
    assert create_user(email, "pass123", Role.CANDIDATE.value, "Ứng viên Test")
    assert not create_user(f"hr-{suffix}@example.com", "pass123", Role.HR.value, "Fake HR")
    registered = verify_user_login(email, "pass123")
    assert registered and registered["role"] == Role.CANDIDATE.value
    print("  OK - public registration cannot create an HR account.")

    print("[4/7] Creating Job through every guarded state...")
    job_id = f"job-{suffix}"
    title = "Backend Developer (Python/FastAPI)"
    jd_text = "Yêu cầu Python, REST API, SQL và hai năm kinh nghiệm."
    rubric = analyze_jd_and_create_rubric(title, jd_text)["rubric"]
    create_job(
        job_id,
        title,
        jd_text,
        "Middle",
        "Python, REST API, SQL",
        "Docker",
        "Thỏa thuận",
        "30 ngày",
        json.dumps(embed_text(jd_text)),
        json.dumps(rubric, ensure_ascii=False),
        "[]",
        JobStatus.DRAFT.value,
        actor_user_id=hr_user["id"],
        actor_role=Role.HR.value,
    )
    for status in (JobStatus.RUBRIC_REVIEW, JobStatus.APPROVED, JobStatus.PUBLISHED):
        update_job_status(
            job_id,
            status.value,
            actor_user_id=hr_user["id"],
            actor_role=Role.HR.value,
            reason=f"Test transition to {status.value}",
        )
    try:
        update_job_status(
            job_id,
            JobStatus.APPROVED.value,
            actor_user_id=candidate_user["id"],
            actor_role=Role.CANDIDATE.value,
        )
        raise AssertionError("Candidate unexpectedly changed a Job status")
    except AuthorizationError:
        pass
    print("  OK - DRAFT -> REVIEW -> APPROVED -> PUBLISHED; Candidate denied.")

    print("[5/7] Submitting and processing one application...")
    cv_text = "4 năm Python, FastAPI, REST API, SQL và Docker."
    evaluation = parse_and_evaluate_cv_with_evidence(title, jd_text, rubric, cv_text, 0.8)
    application_id = f"application-{suffix}"
    save_candidate_application(
        application_id,
        job_id,
        registered["full_name"],
        registered["email"],
        cv_text,
        "https://github.com/example",
        json.dumps(embed_text(cv_text)),
        evaluation["score"],
        evaluation.get("mandatory_flags", []),
        evaluation.get("evidence_scorecard", []),
        evaluation.get("gaps", []),
        evaluation.get("parser_confidence", 0.95),
        evaluation.get("routing_recommendation", "HUMAN_REVIEW"),
        ApplicationStatus.SUBMITTED.value,
        actor_user_id=registered["id"],
        actor_role=Role.CANDIDATE.value,
    )
    for status in (
        ApplicationStatus.QUEUED,
        ApplicationStatus.PROCESSING,
        ApplicationStatus.ANALYZED,
        ApplicationStatus.HR_REVIEW_PENDING,
    ):
        transition_application_status(
            application_id,
            status.value,
            actor_user_id=None,
            actor_role=Role.AGENT.value,
            reason=f"Test transition to {status.value}",
        )
    own_applications = get_candidates_by_email(email)
    assert len(own_applications) == 1
    assert own_applications[0]["stage_status"] == ApplicationStatus.HR_REVIEW_PENDING.value
    try:
        transition_application_status(
            application_id,
            ApplicationStatus.HIRED.value,
            actor_user_id=registered["id"],
            actor_role=Role.CANDIDATE.value,
            reason="Illegal jump",
        )
        raise AssertionError("Illegal application transition unexpectedly succeeded")
    except (AuthorizationError, InvalidTransitionError):
        pass
    print("  OK - Candidate scope, processing states, and illegal jump guard.")

    print("[6/10] Completing happy path through interview, offer, and hire...")
    update_hr_decision(
        application_id,
        ApplicationStatus.SHORTLISTED.value,
        evaluation["score"],
        evaluation["score"],
        "Đủ bằng chứng để phỏng vấn",
        ApplicationStatus.SHORTLISTED.value,
        actor_user_id=hr_user["id"],
        actor_role=Role.HR.value,
    )
    question_data = generate_interview_questions_and_scorecard(title, jd_text, cv_text, evaluation)
    save_interview_data(
        application_id,
        question_data,
        [{"date": "2026-08-01", "time": "10:00", "format": "Online", "interviewer": "Tech Lead"}],
        actor_user_id=hr_user["id"],
        actor_role=Role.HR.value,
    )
    slots = get_interview_slots(application_id, available_only=True)
    assert len(slots) == 1
    select_interview_slot(application_id, slots[0]["id"], candidate_email=email)
    for status, role in (
        (ApplicationStatus.INTERVIEW_COMPLETED, Role.HR),
        (ApplicationStatus.SCORECARD_PENDING, Role.HR),
    ):
        transition_application_status(
            application_id,
            status.value,
            actor_user_id=hr_user["id"] if role is Role.HR else registered["id"],
            actor_role=role.value,
            reason=f"Test transition to {status.value}",
        )
    save_interview_scorecard(
        application_id,
        {"average_score": 3.8},
        ApplicationStatus.INTERVIEWER_SUBMITTED.value,
        actor_user_id=hr_user["id"],
        actor_role=Role.HR.value,
    )
    transition_application_status(
        application_id,
        ApplicationStatus.AGENT_SUMMARIZED.value,
        actor_user_id=None,
        actor_role=Role.AGENT.value,
        reason="Agent summarized scorecard",
    )
    create_offer(
        application_id,
        "3,000 USD",
        "Thử việc 2 tháng",
        None,
        actor_user_id=hr_user["id"],
        actor_role=Role.HR.value,
    )
    respond_to_offer(application_id, ApplicationStatus.OFFER_ACCEPTED.value, candidate_email=email)
    for status in (ApplicationStatus.HIRED, ApplicationStatus.ONBOARDING, ApplicationStatus.CLOSED):
        transition_application_status(
            application_id,
            status.value,
            actor_user_id=hr_user["id"],
            actor_role=Role.HR.value,
            reason=f"Happy path to {status.value}",
        )
    logs = get_audit_logs(application_id)
    assert logs and all(log["entity_type"] == "APPLICATION" for log in logs)
    assert any(log["from_status"] and log["to_status"] for log in logs)
    print("  OK - interview selection, scorecard, offer acceptance, hire, and audit.")

    print("[7/10] Testing feedback approval and PDF revision flow...")
    feedback_application_id = f"feedback-{suffix}"
    save_candidate_application(
        feedback_application_id,
        job_id,
        registered["full_name"],
        email,
        "CV cần bổ sung bằng chứng",
        "",
        "[]",
        55,
        [],
        [],
        ["Thiếu bằng chứng"],
        0.9,
        "NEED_MORE_EVIDENCE",
        ApplicationStatus.SUBMITTED.value,
        actor_user_id=registered["id"],
        actor_role=Role.CANDIDATE.value,
    )
    for status in (
        ApplicationStatus.QUEUED,
        ApplicationStatus.PROCESSING,
        ApplicationStatus.ANALYZED,
        ApplicationStatus.HR_REVIEW_PENDING,
    ):
        transition_application_status(
            feedback_application_id,
            status.value,
            actor_user_id=None,
            actor_role=Role.AGENT.value,
            reason="Prepare feedback flow",
        )
    update_hr_decision(
        feedback_application_id,
        ApplicationStatus.NEED_MORE_INFORMATION.value,
        55,
        55,
        "Cần bổ sung bằng chứng dự án",
        ApplicationStatus.NEED_MORE_INFORMATION.value,
        actor_user_id=hr_user["id"],
        actor_role=Role.HR.value,
    )
    feedback = {
        "matched_points": ["Có Python"],
        "missing_points": ["Thiếu số liệu dự án"],
        "improvement_advice": "Bổ sung phạm vi và kết quả.",
        "before_example": "Tham gia dự án.",
        "after_example": "Xây 3 API, giảm 20% lỗi.",
    }
    save_candidate_feedback(
        feedback_application_id,
        feedback,
        actor_user_id=hr_user["id"],
        actor_role=Role.HR.value,
    )
    approve_candidate_feedback(
        feedback_application_id,
        feedback,
        actor_user_id=hr_user["id"],
        actor_role=Role.HR.value,
    )
    send_candidate_feedback(
        feedback_application_id,
        actor_user_id=hr_user["id"],
        actor_role=Role.HR.value,
    )
    from pypdf import PdfWriter

    pdf_buffer = io.BytesIO()
    writer = PdfWriter()
    writer.add_blank_page(width=612, height=792)
    writer.write(pdf_buffer)
    pdf_bytes = pdf_buffer.getvalue()
    parsed_pdf = validate_and_parse_pdf("revised-cv.pdf", PDF_MIME_TYPE, pdf_bytes)
    assert parsed_pdf.parse_status == "LOW_CONFIDENCE"
    revised_id = submit_pdf_application(
        user=dict(registered),
        job=get_job_by_id(job_id),
        candidate_name=registered["full_name"],
        filename="revised-cv.pdf",
        mime_type=PDF_MIME_TYPE,
        content=pdf_bytes,
        revision_of_id=feedback_application_id,
    )
    revised = next(item for item in get_candidates_by_email(email) if item["id"] == revised_id)
    assert revised["revision_number"] == 2
    assert revised["routing_recommendation"] == "HUMAN_REVIEW"
    print("  OK - generated -> approved -> sent feedback and PDF revision #2.")

    print("[8/10] Testing Talent Pool consent guard...")
    talent_id = f"talent-{suffix}"
    save_candidate_application(
        talent_id, job_id, registered["full_name"], email, "CV talent", "", "[]", 65,
        [], [], [], 0.9, "HUMAN_REVIEW", ApplicationStatus.SUBMITTED.value,
        actor_user_id=registered["id"], actor_role=Role.CANDIDATE.value,
    )
    for status in (ApplicationStatus.QUEUED, ApplicationStatus.PROCESSING, ApplicationStatus.ANALYZED, ApplicationStatus.HR_REVIEW_PENDING):
        transition_application_status(talent_id, status.value, actor_user_id=None, actor_role=Role.AGENT.value, reason="Prepare talent pool")
    set_talent_pool_consent(talent_id, True, candidate_email=email)
    update_hr_decision(
        talent_id, ApplicationStatus.TALENT_POOL.value, 65, 65, "Phù hợp vị trí khác",
        ApplicationStatus.TALENT_POOL.value, actor_user_id=hr_user["id"], actor_role=Role.HR.value,
    )
    print("  OK - Candidate consent recorded before Talent Pool decision.")

    print("[9/10] Rejecting fake PDF content...")
    try:
        validate_and_parse_pdf("fake.pdf", PDF_MIME_TYPE, b"not-a-real-pdf")
        raise AssertionError("Fake PDF unexpectedly passed validation")
    except PdfValidationError:
        pass
    print("  OK - extension alone cannot bypass PDF signature validation.")

    print("[10/10] Running Streamlit smoke tests for auth, HR, and Candidate...")
    from streamlit.testing.v1 import AppTest

    app = AppTest.from_file("app.py", default_timeout=15).run()
    assert not app.exception, [item.value for item in app.exception]
    app.session_state["current_user"] = dict(hr_user)
    app.run()
    assert not app.exception, [item.value for item in app.exception]
    assert len(app.tabs) == 5
    app.session_state["current_user"] = dict(candidate_user)
    app.run()
    assert not app.exception, [item.value for item in app.exception]
    assert len(app.tabs) == 3
    print("  OK - all three UI entry states render without exception.")

    print("=" * 58)
    print("ALL P0-P9 BACKEND AND UI SMOKE TESTS PASSED")
    print(f"Isolated DB: {TEST_DB_PATH}")
    print("=" * 58)


if __name__ == "__main__":
    run_backend_tests()
    select_interview_slot,
    send_candidate_feedback,
    set_talent_pool_consent,
