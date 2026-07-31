"""Fast, provider-free tests for the deterministic CV RAG stages."""

from chunking import chunk_by_section
from extraction import extract_regex_fields
import retrieval
from retrieval import StoredChunk, retrieve_for_rubric
from ai_service import candidate_assessment
from llm_client import parse_json_object
from schemas import RubricCriterion


def test_regex_and_section_chunking() -> None:
    text = """NGUYEN VAN AN
nguyen@example.com | +84 912 345 678

KINH NGHIỆM
Công ty A
- Xây dựng FastAPI production trong 4 năm.
- Tối ưu PostgreSQL.

DỰ ÁN
Hệ thống tuyển dụng
- Thiết kế REST API và monitoring.
"""
    fields = extract_regex_fields(text)
    chunks = chunk_by_section(text, max_words=30)

    assert fields["email"] == "nguyen@example.com"
    assert fields["years_experience_claimed"] == 4
    assert {chunk.section for chunk in chunks} >= {"profile", "experience", "projects"}
    assert all(chunk.text.strip() for chunk in chunks)


def test_retrieval_returns_top_chunk_per_rubric(monkeypatch) -> None:
    monkeypatch.setattr(retrieval, "embed_texts", lambda _: [[1.0, 0.0]])
    chunks = [
        StoredChunk("cv:chunk-001", "skills", "Python FastAPI", [1.0, 0.0]),
        StoredChunk("cv:chunk-002", "education", "Business degree", [0.0, 1.0]),
    ]
    rubric = [
        RubricCriterion(
            id="backend",
            name="Backend",
            description="Python và FastAPI",
            weight=1,
        )
    ]

    result = retrieve_for_rubric(chunks, rubric, top_k=1)

    assert [chunk.id for chunk in result.chunks] == ["cv:chunk-001"]
    assert result.matches[0].criterion_id == "backend"
    assert result.matches[0].similarity == 1.0


def test_parse_json_object_handles_code_fences_and_leading_text() -> None:
    payload = 'Đây là kết quả:\n```json\n{"ok": true, "value": 2}\n```'

    assert parse_json_object(payload) == {"ok": True, "value": 2}


def test_parse_json_object_handles_trailing_commas() -> None:
    payload = '```json\n{"ok": true, "value": 2,}\n```'

    assert parse_json_object(payload) == {"ok": True, "value": 2}


def test_candidate_assessment_reports_underlying_error(monkeypatch) -> None:
    def boom(*args, **kwargs):
        raise ValueError("gemini schema mismatch")

    monkeypatch.setattr("ai_service.generate_structured_json", boom)

    result = candidate_assessment("Backend developer", "CV mẫu", 70)

    assert result["analysis_mode"] == "fallback"
    assert "gemini schema mismatch" in result["fallback_reason"]


def test_candidate_assessment_accepts_missing_evidence(monkeypatch) -> None:
    def fake_structured_json(*args, **kwargs):
        return {
            "summary": "Không có bằng chứng rõ ràng.",
            "score_breakdown": {"skills": 20, "experience": 15, "projects": 10, "other": 5},
            "confidence": 60,
            "recommendation": "needs_review",
            "strengths": ["Có nền tảng cơ bản"],
            "gaps": ["Cần xác minh thêm"],
            "interview_questions": ["Bạn đã làm việc với hệ thống nào?"],
        }

    monkeypatch.setattr("ai_service.generate_structured_json", fake_structured_json)

    result = candidate_assessment("Backend developer", "CV mẫu", 70)

    assert result["analysis_mode"] == "gemini" or result["analysis_mode"] == "openai"
    assert result["evidence"] == []


def test_database_migration_creates_cv_rag_tables(tmp_path, monkeypatch) -> None:
    import database

    monkeypatch.setattr(database, "DB_PATH", str(tmp_path / "rag-test.db"))
    database.init_db()
    connection = database.get_conn()
    tables = {
        row["name"]
        for row in connection.execute("SELECT name FROM sqlite_master WHERE type='table'")
    }
    connection.close()

    assert {"cv_documents", "cv_chunks"} <= tables
