"""Grounded AI screening helpers. The model can recommend; HR decides."""

import hashlib
import json
import os
import re
from typing import Any

import numpy as np

from config import CHAT_MODEL, EMBED_MODEL, MAX_OUTPUT_TOKENS


def get_client():
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
    if not np.linalg.norm(left) or not np.linalg.norm(right):
        return 0.0
    return float(np.dot(left, right) / (np.linalg.norm(left) * np.linalg.norm(right)))


def _items(value: Any) -> list[str]:
    return [str(item).strip() for item in value if str(item).strip()] if isinstance(value, list) else []


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


def _has(text: str, aliases: tuple[str, ...]) -> bool:
    lowered = text.casefold()
    return any(alias in lowered for alias in aliases)


def _evidence_line(cv_text: str, aliases: tuple[str, ...]) -> str:
    lines = [line.strip() for line in re.split(r"[\n.!?]+", cv_text) if line.strip()]
    return next((line[:240] for line in lines if _has(line, aliases)), "Có đề cập trong CV.")


def _fallback(_: float, job_text: str, cv_text: str) -> dict[str, Any]:
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
        "summary": f"CV cung cấp bằng chứng cho {len(found)}/{len(required)} yêu cầu kỹ thuật được nhận diện từ JD. Các nội dung còn thiếu được đánh dấu để HR xác minh, không được AI tự suy diễn.",
        "score_breakdown": {"skills": skills, "experience": experience, "projects": projects, "other": max(0, total - skills - experience - projects)},
        "confidence": min(92, max(45, 55 + len(cv_text) // 180 + round(ratio * 20))),
        "recommendation": "advance" if total >= 70 else "needs_review",
        "strengths": [f"Có bằng chứng về {name}." for name, _ in found[:3]],
        "evidence": evidence,
        "gaps": gaps or ["Không có gap kỹ thuật rõ ràng từ CV; HR vẫn cần xác minh chiều sâu khi phỏng vấn."],
        "interview_questions": questions[:3],
    }


def candidate_assessment(job_text: str, cv_text: str, score: float) -> dict[str, Any]:
    client = get_client()
    if client is None:
        return _fallback(score, job_text, cv_text)
    prompt = f"""You are TalentScreen AI, an evidence-grounded recruiting assistant for a Backend Developer role.
Only use the job description and redacted CV below. Never infer missing facts. If evidence is absent, say exactly that it is insufficient and add a verification question. Do not recommend hiring/rejection; HR makes the decision.

JOB DESCRIPTION:
{job_text}

REDACTED CV:
{cv_text}

Return valid JSON in Vietnamese with: summary, score_breakdown (skills max 40, experience max 25, projects max 20, other max 15), confidence (0-100), recommendation (advance|needs_review), strengths (max 3), evidence (array of {{requirement,evidence,status}}; status found|missing), gaps (max 4), interview_questions (2-3)."""
    try:
        response = client.chat.completions.create(model=CHAT_MODEL, messages=[{"role": "user", "content": prompt}], temperature=0.2, max_tokens=MAX_OUTPUT_TOKENS, response_format={"type": "json_object"})
        return normalize_assessment(json.loads(response.choices[0].message.content or "{}"))
    except Exception:
        return _fallback(score, job_text, cv_text)


def load_assessment(reasoning: str) -> dict[str, Any]:
    try:
        return normalize_assessment(json.loads(reasoning))
    except (TypeError, json.JSONDecodeError):
        return normalize_assessment({"summary": reasoning})


def normalize_assessment(assessment: Any) -> dict[str, Any]:
    if not isinstance(assessment, dict): assessment = {}
    breakdown = assessment.get("score_breakdown") if isinstance(assessment.get("score_breakdown"), dict) else {}
    evidence = assessment.get("evidence") if isinstance(assessment.get("evidence"), list) else []
    return {
        "summary": str(assessment.get("summary", "Không đủ bằng chứng để đánh giá.")).strip(),
        "strengths": _items(assessment.get("strengths")), "gaps": _items(assessment.get("gaps")), "interview_questions": _items(assessment.get("interview_questions")),
        "score_breakdown": {key: max(0, min(cap, int(breakdown.get(key, 0) or 0))) for key, cap in {"skills": 40, "experience": 25, "projects": 20, "other": 15}.items()},
        "confidence": max(0, min(100, int(assessment.get("confidence", 0) or 0))),
        "recommendation": "advance" if assessment.get("recommendation") == "advance" else "needs_review",
        "evidence": [{"requirement": str(item.get("requirement", "Yêu cầu")), "evidence": str(item.get("evidence", "Không đủ bằng chứng để đánh giá.")), "status": "found" if item.get("status") == "found" else "missing"} for item in evidence if isinstance(item, dict)][:8],
    }
