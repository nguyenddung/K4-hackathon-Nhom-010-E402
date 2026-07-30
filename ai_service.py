"""OpenAI integration and candidate-assessment helpers."""

import json
import os
from typing import Any, Dict, List

import numpy as np

from config import CHAT_MODEL, EMBED_MODEL, MAX_OUTPUT_TOKENS


def get_client():
    api_key = os.environ.get("OPENAI_API_KEY", "")
    if not api_key:
        return None
    from openai import OpenAI

    return OpenAI(api_key=api_key)


def embed_text(text: str) -> List[float]:
    client = get_client()
    if client is None:
        rng = np.random.default_rng(abs(hash(text)) % (2**32))
        return rng.normal(size=384).tolist()
    response = client.embeddings.create(model=EMBED_MODEL, input=text[:8000])
    return response.data[0].embedding


def cosine_sim(first: List[float], second: List[float]) -> float:
    first_array, second_array = np.array(first), np.array(second)
    if np.linalg.norm(first_array) == 0 or np.linalg.norm(second_array) == 0:
        return 0.0
    return float(
        np.dot(first_array, second_array)
        / (np.linalg.norm(first_array) * np.linalg.norm(second_array))
    )


def clean_items(value: Any) -> List[str]:
    if not isinstance(value, list):
        return []
    return [str(item).strip() for item in value if str(item).strip()]


def candidate_assessment(job_text: str, cv_text: str, score: float) -> Dict[str, Any]:
    client = get_client()
    if client is None:
        return {
            "summary": f"[MOCK] Điểm khớp {score:.2f}. Cần dùng OpenAI API để phân tích thiếu sót cụ thể.",
            "strengths": ["Có một số nội dung liên quan đến vị trí đang tuyển."],
            "gaps": ["Chưa thể phân tích đối chiếu JD và CV khi chưa có OpenAI API key."],
            "interview_questions": ["Bạn có thể mô tả kinh nghiệm phù hợp nhất với vị trí này không?"],
        }

    prompt = (
        f"Job description:\n{job_text}\n\n"
        f"CV ứng viên:\n{cv_text}\n\n"
        f"Điểm tương đồng vector: {score:.3f}\n"
        "Phân tích bằng tiếng Việt và chỉ dựa trên JD, CV. Trả về JSON hợp lệ với đúng các khóa: "
        "summary (chuỗi, tối đa 3 câu), strengths (mảng tối đa 3 ý), gaps (mảng tối đa 4 ý), "
        "interview_questions (mảng 3-5 câu hỏi). Với gaps, chỉ nêu yêu cầu của JD chưa thấy bằng chứng "
        "trong CV, không suy diễn ứng viên không có năng lực. Mỗi câu hỏi phỏng vấn phải kiểm chứng một "
        "kỹ năng, kinh nghiệm hoặc thiếu sót cụ thể. Không đánh giá hay đặt câu hỏi về tuổi, giới tính, "
        "dân tộc, tôn giáo, tình trạng hôn nhân, sức khỏe hoặc thuộc tính cá nhân nhạy cảm."
    )
    response = client.chat.completions.create(
        model=CHAT_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=MAX_OUTPUT_TOKENS,
        response_format={"type": "json_object"},
    )
    try:
        assessment = json.loads(response.choices[0].message.content or "{}")
    except json.JSONDecodeError:
        assessment = {}

    return normalize_assessment(assessment)


def load_assessment(reasoning: str) -> Dict[str, Any]:
    try:
        assessment = json.loads(reasoning)
    except (TypeError, json.JSONDecodeError):
        assessment = {"summary": reasoning}
    return normalize_assessment(assessment)


def normalize_assessment(assessment: Any) -> Dict[str, Any]:
    if not isinstance(assessment, dict):
        assessment = {}
    return {
        "summary": str(assessment.get("summary", "Chưa có nhận xét tổng quan.")).strip(),
        "strengths": clean_items(assessment.get("strengths")),
        "gaps": clean_items(assessment.get("gaps")),
        "interview_questions": clean_items(assessment.get("interview_questions")),
    }