"""Grounded AI screening helpers. The model can recommend; HR decides."""

import hashlib
import json
import os
import re
from typing import Any

import numpy as np

from config import AI_PROVIDER, EMBED_MODEL
from llm_client import (
    active_model_name,
    active_provider_name,
    generate_structured_json,
)


def get_client():
    if AI_PROVIDER != "openai":
        return None
    key = os.environ.get("OPENAI_API_KEY", "").strip()
    if len(key) < 20 or key.casefold() in {"key", "your-key", "sk-...", "replace-me"}:
        return None
    from openai import OpenAI
    return OpenAI(api_key=key)


def _local_embedding(text: str) -> list[float]:
    # Deterministic hashed bag-of-words keeps the no-key demo meaningful:
    # related JD/CV terms land in the same dimensions instead of random vectors.
    vector = np.zeros(384)
    for token in re.findall(r"[\w+#.-]{2,}", text.casefold()):
        digest = hashlib.sha256(token.encode("utf-8")).digest()
        vector[int.from_bytes(digest[:2], "big") % len(vector)] += 1
    return vector.tolist()


def embed_text(text: str) -> list[float]:
    client = get_client()
    if client is None:
        return _local_embedding(text)
    try:
        return client.embeddings.create(model=EMBED_MODEL, input=text[:8000]).data[0].embedding
    except Exception:
        return _local_embedding(text)


def cosine_sim(first: list[float], second: list[float]) -> float:
    left, right = np.array(first), np.array(second)
    if left.shape != right.shape:
        return 0.0
    if not np.linalg.norm(left) or not np.linalg.norm(right):
        return 0.0
    return float(np.dot(left, right) / (np.linalg.norm(left) * np.linalg.norm(right)))


def _items(value: Any) -> list[str]:
    return [str(item).strip() for item in value if str(item).strip()] if isinstance(value, list) else []


def _validate_assessment_payload(assessment: Any) -> dict[str, Any]:
    """Reject incomplete provider output before it can be presented as AI analysis."""
    if not isinstance(assessment, dict):
        raise ValueError("AI assessment must be a JSON object")

    required = {
        "summary",
        "score_breakdown",
        "confidence",
        "recommendation",
        "strengths",
        "evidence",
        "gaps",
        "interview_questions",
    }
    missing = sorted(required - assessment.keys())
    if missing:
        raise ValueError(f"AI assessment is missing fields: {', '.join(missing)}")

    evidence = assessment.get("evidence")
    if not isinstance(evidence, list) or not evidence:
        raise ValueError("AI assessment returned no grounded evidence")
    for index, item in enumerate(evidence, start=1):
        if not isinstance(item, dict):
            raise ValueError(f"AI evidence item {index} must be an object")
        if not str(item.get("requirement", "")).strip():
            raise ValueError(f"AI evidence item {index} has no requirement")
        if not str(item.get("evidence", "")).strip():
            raise ValueError(f"AI evidence item {index} has no quote or explanation")
        if item.get("status") not in {"found", "missing"}:
            raise ValueError(f"AI evidence item {index} has an invalid status")

    questions = assessment.get("interview_questions")
    if not isinstance(questions, list) or len(questions) < 2:
        raise ValueError("AI assessment must return at least two interview questions")
    if not isinstance(assessment.get("score_breakdown"), dict):
        raise ValueError("AI assessment score_breakdown must be an object")
    return assessment


SKILLS = {
    "Python": ("python",),
    "FastAPI": ("fastapi",),
    "REST API": ("rest api", "restful",),
    "PostgreSQL": ("postgresql", "postgres",),
    "Docker": ("docker",),
    "Kubernetes": ("kubernetes", "k8s", "eks", "gke",),
    "Redis": ("redis",),
    "System design": ("system design", "kiến trúc", "architecture", "microservice",),
    "Production": ("production", "vận hành", "monitoring", "observability",),
}

ASSESSMENT_SCHEMA = {
    "name": "talent_screen_assessment",
    "strict": True,
    "schema": {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "summary": {"type": "string"},
            "score_breakdown": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "skills": {
                        "type": "object",
                        "properties": {"score": {"type": "integer"}, "reason": {"type": "string"}},
                        "required": ["score", "reason"]
                    },
                    "experience": {
                        "type": "object",
                        "properties": {"score": {"type": "integer"}, "reason": {"type": "string"}},
                        "required": ["score", "reason"]
                    },
                    "projects": {
                        "type": "object",
                        "properties": {"score": {"type": "integer"}, "reason": {"type": "string"}},
                        "required": ["score", "reason"]
                    },
                    "other": {
                        "type": "object",
                        "properties": {"score": {"type": "integer"}, "reason": {"type": "string"}},
                        "required": ["score", "reason"]
                    },
                },
                "required": ["skills", "experience", "projects", "other"],
            },
            "confidence": {"type": "integer"},
            "recommendation": {"type": "string", "enum": ["advance", "needs_review"]},
            "strengths": {"type": "array", "items": {"type": "string"}, "maxItems": 3},
            "evidence": {
                "type": "array",
                "minItems": 1,
                "maxItems": 8,
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "requirement": {"type": "string"},
                        "evidence": {"type": "string"},
                        "status": {"type": "string", "enum": ["found", "missing"]},
                    },
                    "required": ["requirement", "evidence", "status"],
                },
            },
            "gaps": {"type": "array", "items": {"type": "string"}, "maxItems": 4},
            "interview_questions": {"type": "array", "items": {"type": "string"}, "minItems": 2, "maxItems": 3},
        },
        "required": ["summary", "score_breakdown", "confidence", "recommendation", "strengths", "evidence", "gaps", "interview_questions"],
    },
}


def _has(text: str, aliases: tuple[str, ...]) -> bool:
    lowered = text.casefold()
    return any(alias in lowered for alias in aliases)


def _evidence_line(cv_text: str, aliases: tuple[str, ...]) -> str:
    lines = [line.strip() for line in re.split(r"[\n.!?]+", cv_text) if line.strip()]
    return next((line[:240] for line in lines if _has(line, aliases)), "Có đề cập trong CV.")


def _fallback(_: float, job_text: str, cv_text: str, reason: str = "OpenAI API is not configured") -> dict[str, Any]:
    required = [(name, aliases) for name, aliases in SKILLS.items() if _has(job_text, aliases)]
    required = required or list(SKILLS.items())[:6]
    found = [(name, aliases) for name, aliases in required if _has(cv_text, aliases)]
    missing = [(name, aliases) for name, aliases in required if not _has(cv_text, aliases)]
    ratio = len(found) / len(required)
    year_match = re.search(r"(\d{1,2})\s*(?:\+?\s*n.m|years?)", cv_text, re.I)
    years = min(10, int(year_match.group(1))) if year_match else 0
    skills = round(40 * ratio)
    experience = min(25, 10 + years * 3) if years else (12 if re.search(r"kinh nghiệm|experience", cv_text, re.I) else 7)
    projects = 17 if re.search(r"dự án|project|microservice|architecture|kiến trúc", cv_text, re.I) else 9
    other = 11 if re.search(r"tối ưu|latency|performance|lead|team|ci/cd|github actions", cv_text, re.I) else 7
    total = min(100, skills + experience + projects + other)
    evidence = [
        {"requirement": name, "evidence": _evidence_line(cv_text, aliases), "status": "found"}
        for name, aliases in found
    ] + [
        {"requirement": name, "evidence": "Không đủ bằng chứng để đánh giá.", "status": "missing"}
        for name, _ in missing
    ]
    gaps = [f"{name}: chưa tìm thấy bằng chứng trong CV; HR cần xác minh trực tiếp." for name, _ in missing[:4]]
    question_map = {
        "Kubernetes": "Bạn đã từng triển khai ứng dụng bằng Kubernetes trong dự án thực tế chưa? Vai trò cụ thể của bạn là gì?",
        "Redis": "Bạn đã dùng Redis cho bài toán nào và lựa chọn cấu trúc dữ liệu ra sao?",
        "System design": "Bạn sẽ thiết kế một API chịu tải lớn như thế nào và đánh đổi điều gì?",
        "Production": "Hãy kể về một sự cố production: bạn phát hiện, xử lý và ngăn tái diễn ra sao?",
        "PostgreSQL": "Bạn đã tối ưu PostgreSQL trong trường hợp thực tế nào và đo kết quả ra sao?",
    }
    questions = [question_map.get(name, f"Bạn đã sử dụng {name} trong dự án thực tế nào?") for name, _ in missing[:3]]
    if len(questions) < 2:
        questions.append("Quyết định kỹ thuật khó nhất trong dự án backend gần đây của bạn là gì?")
    return {
        "analysis_mode": "fallback",
        "provider": "local",
        "model": "grounded-rules-v1",
        "fallback_reason": reason,
        "summary": f"CV cung cấp bằng chứng cho {len(found)}/{len(required)} yêu cầu kỹ thuật được nhận diện từ JD. Các nội dung còn thiếu được đánh dấu để HR xác minh, không được AI tự suy diễn.",
        "score_breakdown": {
            "skills": {"score": skills, "reason": f"Đạt {len(found)}/{len(required)} kỹ năng."},
            "experience": {"score": experience, "reason": "Đánh giá dựa trên số năm kinh nghiệm."},
            "projects": {"score": projects, "reason": "Đánh giá qua quy mô dự án và kiến trúc."},
            "other": {"score": max(0, total - skills - experience - projects), "reason": "Điểm cộng từ kỹ năng tối ưu, vận hành hệ thống."}
        },
        "confidence": min(92, max(45, 55 + len(cv_text) // 180 + round(ratio * 20))),
        "recommendation": "advance" if total >= 70 else "needs_review",
        "strengths": [f"Có bằng chứng về {name}." for name, _ in found[:3]],
        "evidence": evidence,
        "gaps": gaps or ["Không có gap kỹ thuật rõ ràng từ CV; HR vẫn cần xác minh chiều sâu khi phỏng vấn."],
        "interview_questions": questions[:3],
    }


def candidate_assessment(job_text: str, cv_text: str, score: float) -> dict[str, Any]:
    prompt = f"""Bạn là TalentScreen AI, trợ lý sàng lọc ứng viên Backend Developer cho HR.

NGUYÊN TẮC BẮT BUỘC:
- Chỉ sử dụng thông tin trong JD và CV đã ẩn danh bên dưới.
- Không suy diễn kỹ năng, số năm kinh nghiệm, vai trò hay kết quả nếu CV không nêu rõ.
- Mỗi bằng chứng phải trích lại một đoạn ngắn, cụ thể từ CV; không viết nhận xét chung chung.
- Với yêu cầu thiếu bằng chứng, ghi status="missing", giải thích chính xác điều chưa biết và tạo câu hỏi phỏng vấn để xác minh.
- AI chỉ đề xuất "advance" hoặc "needs_review"; không tự quyết định tuyển hoặc loại.
- Tổng điểm phải bằng tổng skills + experience + projects + other.

JOB DESCRIPTION:
{job_text}

REDACTED CV:
{cv_text}

Trả về JSON hợp lệ bằng tiếng Việt với:
- summary: 2-3 câu giải thích vì sao đạt mức điểm này
- score_breakdown: object chứa 4 tiêu chí (skills tối đa 40, experience tối đa 25, projects tối đa 20, other tối đa 15). Mỗi tiêu chí phải là một object gồm 'score' (điểm) và 'reason' (lý do cụ thể vì sao trừ điểm hoặc cho điểm, ghi rất ngắn gọn).
- confidence: 0-100, phản ánh mức đầy đủ của bằng chứng chứ không phải mức phù hợp
- recommendation: advance hoặc needs_review
- strengths: tối đa 3 điểm mạnh có bằng chứng
- evidence: mảng {{requirement,evidence,status}}, status found hoặc missing
- gaps: tối đa 4 khoảng trống cụ thể
- interview_questions: 2-3 câu hỏi trực tiếp từ gaps."""
    last_error: Exception | None = None
    for _ in range(2):
        try:
            assessment = normalize_assessment(
                _validate_assessment_payload(
                    generate_structured_json(
                        prompt,
                        ASSESSMENT_SCHEMA["schema"],
                        ASSESSMENT_SCHEMA["name"],
                        temperature=0.2,
                    )
                )
            )
            assessment.update(
                {
                    "analysis_mode": AI_PROVIDER,
                    "provider": active_provider_name(),
                    "model": active_model_name(),
                    "fallback_reason": "",
                }
            )
            return assessment
        except Exception as exc:
            last_error = exc
    error_text = f"{type(last_error).__name__}: {last_error}" if last_error else f"{active_provider_name()} request failed after 2 attempts"
    return _fallback(
        score,
        job_text,
        cv_text,
        error_text,
    )


def load_assessment(reasoning: str) -> dict[str, Any]:
    try:
        return normalize_assessment(json.loads(reasoning))
    except (TypeError, json.JSONDecodeError):
        return normalize_assessment({"summary": reasoning})


def normalize_assessment(assessment: Any) -> dict[str, Any]:
    if not isinstance(assessment, dict): assessment = {}
    breakdown = assessment.get("score_breakdown") if isinstance(assessment.get("score_breakdown"), dict) else {}
    evidence = assessment.get("evidence") if isinstance(assessment.get("evidence"), list) else []
    def _parse_metric(val, cap):
        if isinstance(val, dict):
            return {"score": max(0, min(cap, int(val.get("score") or 0))), "reason": str(val.get("reason") or "").strip()}
        return {"score": max(0, min(cap, int(val or 0))), "reason": ""}

    return {
        "analysis_mode": assessment.get("analysis_mode") if assessment.get("analysis_mode") in {"openai", "gemini", "groq"} else "fallback",
        "provider": str(assessment.get("provider", "unknown")),
        "model": str(assessment.get("model", "unknown")),
        "fallback_reason": str(assessment.get("fallback_reason", "")),
        "summary": str(assessment.get("summary", "Không đủ bằng chứng để đánh giá.")).strip(),
        "strengths": _items(assessment.get("strengths")), "gaps": _items(assessment.get("gaps")), "interview_questions": _items(assessment.get("interview_questions")),
        "score_breakdown": {
            "skills": _parse_metric(breakdown.get("skills"), 40),
            "experience": _parse_metric(breakdown.get("experience"), 25),
            "projects": _parse_metric(breakdown.get("projects"), 20),
            "other": _parse_metric(breakdown.get("other"), 15),
        },
        "confidence": max(0, min(100, int(assessment.get("confidence", 0) or 0))),
        "recommendation": "advance" if assessment.get("recommendation") == "advance" else "needs_review",
        "evidence": [{"requirement": str(item.get("requirement", "Yêu cầu")), "evidence": str(item.get("evidence", "Không đủ bằng chứng để đánh giá.")), "status": "found" if item.get("status") == "found" else "missing"} for item in evidence if isinstance(item, dict)][:8],
    }
