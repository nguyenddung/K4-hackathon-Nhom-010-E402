"""Pydantic contracts for upload, rubric retrieval, and grounded analysis."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class ParsedFields(StrictModel):
    name: str | None = None
    email: str | None = None
    phone: str | None = None
    linkedin: str | None = None
    github: str | None = None
    years_experience_claimed: int | None = None


class CVUploadResponse(StrictModel):
    id: str
    filename: str
    fields: ParsedFields
    chunk_count: int
    embedding_model: str


class RubricCriterion(StrictModel):
    id: str = Field(min_length=1, max_length=80)
    name: str = Field(min_length=2, max_length=160)
    description: str = Field(min_length=2, max_length=1_000)
    weight: float = Field(default=1, gt=0, le=100)


def default_rubric() -> list[RubricCriterion]:
    return [
        RubricCriterion(id="skills", name="Kỹ năng", description="Kỹ năng kỹ thuật phù hợp vai trò", weight=40),
        RubricCriterion(id="experience", name="Kinh nghiệm", description="Mức độ và tính liên quan của kinh nghiệm", weight=30),
        RubricCriterion(id="projects", name="Dự án", description="Dự án, trách nhiệm và kết quả có bằng chứng", weight=20),
        RubricCriterion(id="education", name="Học vấn/chứng chỉ", description="Học vấn hoặc chứng chỉ liên quan", weight=10),
    ]


class AnalyzeRequest(StrictModel):
    rubric: list[RubricCriterion] = Field(default_factory=default_rubric, min_length=1, max_length=20)
    top_k: int = Field(default=3, ge=1, le=8)

    @model_validator(mode="after")
    def unique_criterion_ids(self) -> "AnalyzeRequest":
        ids = [item.id for item in self.rubric]
        if len(ids) != len(set(ids)):
            raise ValueError("rubric criterion ids must be unique")
        return self


class EvidenceQuote(StrictModel):
    chunk_id: str
    section: str
    quote: str = Field(max_length=500)


class CriterionAssessment(StrictModel):
    criterion_id: str
    verdict: Literal["met", "partial", "not_met", "unknown"]
    score: int = Field(ge=0, le=100)
    rationale: str
    evidence: list[EvidenceQuote] = Field(max_length=5)


class CVAnalysisCore(StrictModel):
    summary: str
    overall_score: int = Field(ge=0, le=100)
    recommendation: Literal["advance", "needs_review"]
    criteria: list[CriterionAssessment]
    gaps: list[str] = Field(max_length=10)
    interview_questions: list[str] = Field(max_length=10)


class CVAnalysisResponse(CVAnalysisCore):
    cv_id: str
    provider: Literal["OpenAI", "Google Gemini"]
    model: str
    retrieved_chunk_count: int
