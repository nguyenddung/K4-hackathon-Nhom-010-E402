"""Fast, provider-free tests for the deterministic CV RAG stages."""

from chunking import chunk_by_section
from extraction import extract_regex_fields
import retrieval
from retrieval import StoredChunk, retrieve_for_rubric
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
