"""Application workflow orchestration shared by initial and revised PDF submissions."""

from __future__ import annotations

import json
import uuid
from typing import Any

from ai_service import cosine_sim, embed_text, parse_and_evaluate_cv_with_evidence
from cv_service import PDF_MIME_TYPE, persist_pdf, validate_and_parse_pdf
from database import (
    enqueue_application,
    save_application_analysis,
    save_candidate_application,
    transition_application_status,
    update_processing_job,
)
from domain import ApplicationStatus, Role


def submit_pdf_application(
    *,
    user: dict[str, Any],
    job,
    candidate_name: str,
    filename: str,
    mime_type: str | None,
    content: bytes,
    portfolio_link: str = "",
    start_availability: str = "",
    work_preference: str = "Theo mô tả Job",
    submitted_answers: dict[str, Any] | None = None,
    revision_of_id: str | None = None,
) -> str:
    parsed = validate_and_parse_pdf(filename, mime_type, content)
    application_id = str(uuid.uuid4())
    stored_path = persist_pdf(application_id, filename, content)
    save_candidate_application(
        candidate_id=application_id,
        job_id=job["id"],
        name=candidate_name,
        email=user["email"],
        cv_text=parsed.text,
        portfolio_link=portfolio_link,
        embedding="[]",
        score=0,
        mandatory_flags=[],
        evidence_json=[],
        missing_gaps_json=[],
        parser_confidence=parsed.parser_confidence,
        routing_recommendation="HUMAN_REVIEW",
        stage_status=ApplicationStatus.SUBMITTED.value,
        revision_of_id=revision_of_id,
        cv_file_path=stored_path,
        cv_file_name=filename,
        cv_mime_type=PDF_MIME_TYPE,
        cv_sha256=parsed.sha256,
        cv_size_bytes=parsed.size_bytes,
        parse_status=parsed.parse_status,
        page_count=parsed.page_count,
        submitted_answers=submitted_answers,
        start_availability=start_availability,
        work_preference=work_preference,
        actor_user_id=user.get("id"),
        actor_role=Role.CANDIDATE.value,
    )

    try:
        enqueue_application(application_id)
        transition_application_status(
            application_id,
            ApplicationStatus.QUEUED.value,
            actor_user_id=None,
            actor_role=Role.AGENT.value,
            reason="CV PDF hợp lệ đã vào hàng đợi",
        )
        update_processing_job(application_id, "PROCESSING")
        transition_application_status(
            application_id,
            ApplicationStatus.PROCESSING.value,
            actor_user_id=None,
            actor_role=Role.AGENT.value,
            reason="Agent bắt đầu phân tích CV PDF",
        )
        if parsed.parse_status == "PARSED":
            job_embedding = json.loads(job["embedding"]) if job["embedding"] else embed_text(job["description"])
            cv_embedding = embed_text(parsed.text)
            similarity = cosine_sim(job_embedding, cv_embedding)
            rubric = json.loads(job["rubric_json"]) if job["rubric_json"] else []
            result = parse_and_evaluate_cv_with_evidence(
                job["title"], job["description"], rubric, parsed.text, similarity
            )
            save_application_analysis(
                application_id,
                embedding=json.dumps(cv_embedding),
                score=result.get("score", 0),
                mandatory_flags=result.get("mandatory_flags", []),
                evidence=result.get("evidence_scorecard", []),
                gaps=result.get("gaps", []),
                parser_confidence=parsed.parser_confidence,
                routing_recommendation=result.get("routing_recommendation", "HUMAN_REVIEW"),
            )
            queue_result = "COMPLETED"
        else:
            save_application_analysis(
                application_id,
                embedding="[]",
                score=0,
                mandatory_flags=["PARSER_CONFIDENCE_LOW"],
                evidence=[],
                gaps=["PDF có thể là bản scan; cần HR kiểm tra thủ công hoặc yêu cầu tải lại."],
                parser_confidence=parsed.parser_confidence,
                routing_recommendation="HUMAN_REVIEW",
            )
            queue_result = "MANUAL_REVIEW"
        for status in (ApplicationStatus.ANALYZED, ApplicationStatus.HR_REVIEW_PENDING):
            transition_application_status(
                application_id,
                status.value,
                actor_user_id=None,
                actor_role=Role.AGENT.value,
                reason="Hoàn tất bước phân tích; chuyển HR kiểm tra",
            )
        update_processing_job(application_id, queue_result)
        return application_id
    except Exception as exc:
        try:
            update_processing_job(application_id, "FAILED", error=str(exc))
        except Exception:
            pass
        raise
