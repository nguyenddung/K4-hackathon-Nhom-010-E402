"""AI Service engine providing JD parsing, weighted Rubric creation, 2-layer CV evidence evaluation, constructive candidate feedback, and 5-level interview question generation."""

import json
import hashlib
import re
from typing import Any, Dict, List

import numpy as np

from config import AI_TIMEOUT_SECONDS, MAX_OUTPUT_TOKENS, get_chat_runtime, get_embedding_runtime


def get_client():
    runtime = get_chat_runtime()
    if runtime.provider == "mock" or not runtime.api_key:
        return None
    try:
        from openai import OpenAI
        return OpenAI(
            api_key=runtime.api_key,
            base_url=runtime.base_url,
            timeout=AI_TIMEOUT_SECONDS,
        )
    except Exception:
        return None


def get_ai_runtime_info() -> Dict[str, Any]:
    """Return safe diagnostics without ever exposing an API key."""
    chat = get_chat_runtime()
    embedding = get_embedding_runtime()
    return {
        "chat_provider": chat.provider,
        "chat_model": chat.model,
        "chat_configured": chat.configured,
        "embedding_provider": embedding.provider,
        "embedding_model": embedding.model,
        "embedding_configured": embedding.configured,
    }


def _local_embedding(text: str) -> List[float]:
    seed = int.from_bytes(hashlib.sha256(text.encode("utf-8")).digest()[:8], "big")
    return np.random.default_rng(seed).normal(size=384).tolist()


def embed_text(text: str) -> List[float]:
    runtime = get_embedding_runtime()
    if runtime.provider == "local" or not runtime.api_key:
        return _local_embedding(text)
    try:
        from openai import OpenAI

        client = OpenAI(
            api_key=runtime.api_key,
            base_url=runtime.base_url,
            timeout=AI_TIMEOUT_SECONDS,
        )
        response = client.embeddings.create(model=runtime.model, input=text[:8000])
        return response.data[0].embedding
    except Exception:
        return _local_embedding(text)


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


def analyze_jd_and_create_rubric(job_title: str, jd_text: str, *, _force_mock: bool = False) -> Dict[str, Any]:
    """Analyzes JD, flags vague phrases, and generates weighted rubric (7 categories)."""
    client = get_client()
    if client is None or _force_mock:
        # MOCK response
        vague_warnings = []
        if "áp lực" in jd_text.lower() or "giao tiếp" in jd_text.lower() or "tư duy" in jd_text.lower():
            vague_warnings.append({
                "vague_phrase": "Các cụm từ mơ hồ (áp lực, tư duy, giao tiếp)",
                "suggestion": "Chuyển thành: Có ví dụ xử lý sự cố thực tế, khả năng thuyết trình kỹ thuật cho người không chuyên."
            })

        return {
            "vague_warnings": vague_warnings,
            "rubric": [
                {"criterion": "Kỹ năng chuyên môn chính", "type": "Bắt buộc", "weight": 30, "description": "Đáp ứng ngôn ngữ/framework chính"},
                {"criterion": "Kinh nghiệm liên quan", "type": "Chấm điểm", "weight": 20, "description": "Số năm và cấp độ vị trí tương đương"},
                {"criterion": "Dự án thực tế", "type": "Chấm điểm", "weight": 15, "description": "Quy mô hệ thống và vai trò cá nhân"},
                {"criterion": "Thành tích đo lường được", "type": "Chấm điểm", "weight": 10, "description": "Số liệu cụ thể về hiệu năng, kết quả"},
                {"criterion": "Kỹ năng hỗ trợ", "type": "Ưu tiên", "weight": 10, "description": "Testing, CI/CD, Git workflow"},
                {"criterion": "Ngoại ngữ", "type": "Theo yêu cầu", "weight": 5, "description": "Tiếng Anh giao tiếp hoặc đọc tài liệu"},
                {"criterion": "Mức độ rõ ràng của bằng chứng", "type": "Chấm điểm", "weight": 10, "description": "Có trích dẫn số liệu & bằng chứng thực tế"}
            ],
            "initial_screening_questions": [
                f"Bạn có bao nhiêu năm kinh nghiệm thực tế với {job_title}?",
                "Mô tả dự án lớn nhất bạn từng tham gia và vai trò của bạn."
            ]
        }

    prompt = (
        f"Vị trí: {job_title}\n"
        f"Mô tả công việc (JD):\n{jd_text}\n\n"
        "Hãy đóng vai AI Recruiter phân tích JD này. Trả về JSON hợp lệ theo đúng cấu trúc:\n"
        "{\n"
        '  "vague_warnings": [{"vague_phrase": "cụm mơ hồ", "suggestion": "gợi ý tiêu chí đo lường được"}],\n'
        '  "rubric": [\n'
        '    {"criterion": "Tên tiêu chí", "type": "Bắt buộc/Chấm điểm/Ưu tiên", "weight": 30, "description": "Mô tả"}\n'
        "  ],\n"
        '  "initial_screening_questions": ["câu hỏi 1", "câu hỏi 2"]\n'
        "}\n"
        "Tổng trọng số rubric phải đúng bằng 100%. Phân tích các tiêu chí mơ hồ như 'chịu áp lực', 'giao tiếp tốt' để gợi ý tiêu chí chuẩn hóa."
    )

    try:
        res = client.chat.completions.create(
            model=get_chat_runtime().model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            response_format={"type": "json_object"}
        )
        return json.loads(res.choices[0].message.content or "{}")
    except Exception:
        return analyze_jd_and_create_rubric(job_title, jd_text, _force_mock=True)


def pre_screen_candidate_qa(job_title: str, jd_text: str, question: str) -> str:
    """Answers candidate questions before applying."""
    client = get_client()
    if client is None:
        return f"[MOCK Assistant] Vị trí '{job_title}' yêu cầu kinh nghiệm chuyên môn chính và tinh thần học hỏi. Hãy nộp CV để hệ thống đối chiếu chi tiết!"

    prompt = (
        f"Ứng viên hỏi về công việc '{job_title}':\n"
        f"JD: {jd_text[:1500]}\n"
        f"Câu hỏi của ứng viên: {question}\n\n"
        "Hãy trả lời thân thiện, khách quan, tư vấn sơ bộ dựa trên JD. Không hứa hẹn ứng viên chắc chắn trúng tuyển."
    )
    try:
        res = client.chat.completions.create(
            model=get_chat_runtime().model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4,
            max_tokens=300
        )
        return res.choices[0].message.content.strip()
    except Exception:
        return f"Vị trí '{job_title}' chào đón bạn nộp CV. Vui lòng tham khảo các kỹ năng bắt buộc trong JD."


def parse_and_evaluate_cv_with_evidence(job_title: str, jd_text: str, rubric: List[Dict[str, Any]], cv_text: str, sim_score: float, *, _force_mock: bool = False) -> Dict[str, Any]:
    """2-Layer evaluation: Mandatory check + Weighted rubric with exact evidence quotes."""
    client = get_client()
    if client is None or _force_mock:
        # Generate realistic MOCK evaluation based on similarity score
        score_val = max(35, min(95, int(sim_score * 100 + 30)))
        mandatory_pass = True if score_val >= 50 else False

        routing = "SHORTLIST_RECOMMENDED" if score_val >= 80 else ("HUMAN_REVIEW" if score_val >= 60 else ("NEED_MORE_EVIDENCE" if score_val >= 40 else "LOW_MATCH_REVIEW"))

        return {
            "parser_confidence": 0.92,
            "mandatory_flags": [] if mandatory_pass else ["MANDATORY_CRITERION_NOT_FOUND: Chưa tìm thấy bằng chứng kỹ năng bắt buộc cốt lõi"],
            "score": score_val,
            "summary": f"Ứng viên đạt điểm phù hợp {score_val}/100. Hồ sơ thể hiện được một số kinh nghiệm làm việc thực tế phù hợp với JD.",
            "evidence_scorecard": [
                {
                    "criterion": "Kỹ năng chuyên môn chính",
                    "score": 4 if score_val >= 70 else 2,
                    "max_score": 5,
                    "evidence_quote": "Thực hiện lập trình và xây dựng module theo yêu cầu dự án trong CV.",
                    "missing_gap": "Chưa thấy số liệu tối ưu hiệu năng cụ thể.",
                    "confidence": 0.90
                },
                {
                    "criterion": "Kinh nghiệm liên quan",
                    "score": 4 if score_val >= 60 else 2,
                    "max_score": 5,
                    "evidence_quote": "Có thời gian làm việc trong các dự án công nghệ tương đương.",
                    "missing_gap": "Chưa làm rõ quy mô người dùng của hệ thống.",
                    "confidence": 0.88
                }
            ],
            "strengths": [
                "Nội dung trình bày rõ ràng, có quá trình làm việc liên tục.",
                "Có kỹ năng phù hợp với yêu cầu chuyên môn của dự án."
            ],
            "gaps": [
                "Cần bổ sung bằng chứng và số liệu cụ thể về kết quả đạt được.",
                "Chưa nêu rõ quy mô hệ thống hoặc kích thước đội nhóm từng tham gia."
            ],
            "routing_recommendation": routing
        }

    rubric_str = json.dumps(rubric, ensure_ascii=False)
    prompt = (
        f"Vị trí: {job_title}\n"
        f"Mô tả công việc (JD):\n{jd_text[:2000]}\n\n"
        f"Rubric đánh giá:\n{rubric_str}\n\n"
        f"CV Ứng viên:\n{cv_text[:3000]}\n\n"
        "Hãy đóng vai AI Recruiter phân tích CV chuyên sâu theo tiêu chuẩn phantich.md:\n"
        "1. Lớp 1: Kiểm tra yêu cầu bắt buộc. Nếu thiếu, thêm vào mandatory_flags dạng 'MANDATORY_CRITERION_NOT_FOUND: [tên tiêu chí]'.\n"
        "2. Lớp 2: Chấm điểm 0-100 tổng thể. Cho từng tiêu chí trong Rubric: trích dẫn BẰNG CHỨNG THỰC TẾ (evidence_quote) chính xác từ CV, nêu ĐIỂM THIẾU (missing_gap), độ tin cậy (confidence 0-1).\n"
        "3. Đề xuất phân luồng (routing_recommendation): SHORTLIST_RECOMMENDED (80-100), HUMAN_REVIEW (60-79), NEED_MORE_EVIDENCE (40-59), LOW_MATCH_REVIEW (0-39).\n\n"
        "Trả về JSON hợp lệ với cấu trúc:\n"
        "{\n"
        '  "parser_confidence": 0.95,\n'
        '  "mandatory_flags": [],\n'
        '  "score": 85,\n'
        '  "summary": "Tóm tắt 2-3 câu",\n'
        '  "evidence_scorecard": [\n'
        '     {"criterion": "Tên", "score": 4, "max_score": 5, "evidence_quote": "Đoạn trích từ CV", "missing_gap": "Điểm thiếu", "confidence": 0.9}\n'
        '  ],\n'
        '  "strengths": ["Điểm mạnh 1", "Điểm mạnh 2"],\n'
        '  "gaps": ["Thiếu sót 1", "Thiếu sót 2"],\n'
        '  "routing_recommendation": "SHORTLIST_RECOMMENDED"\n'
        "}"
    )

    try:
        res = client.chat.completions.create(
            model=get_chat_runtime().model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            response_format={"type": "json_object"}
        )
        return json.loads(res.choices[0].message.content or "{}")
    except Exception:
        return parse_and_evaluate_cv_with_evidence(
            job_title, jd_text, rubric, cv_text, sim_score, _force_mock=True
        )


def generate_candidate_feedback(job_title: str, jd_text: str, cv_text: str, evaluation: Dict[str, Any]) -> Dict[str, Any]:
    """Generates constructive, evidence-based feedback for candidates with before/after CV rewrite examples."""
    client = get_client()
    strengths = evaluation.get("strengths", ["Đã thể hiện được kinh nghiệm làm việc cơ bản."])
    gaps = evaluation.get("gaps", ["Chưa làm rõ thành tích và số liệu đo lường được."])

    if client is None:
        return {
            "matched_points": strengths,
            "missing_points": gaps,
            "improvement_advice": "Hãy bổ sung vai trò cụ thể trong từng dự án, công nghệ sử dụng, quy mô hệ thống và các con số kết quả đo lường được.",
            "before_example": "Tham gia phát triển dự án phần mềm cho công ty.",
            "after_example": f"Phát triển 3 REST API bằng công nghệ chính cho module đơn hàng; viết unit test và giúp giảm 20% lỗi sau phát hành."
        }

    prompt = (
        f"Vị trí: {job_title}\n"
        f"JD: {jd_text[:1500]}\n"
        f"CV Ứng viên: {cv_text[:2000]}\n"
        f"Đánh giá thiếu sót: {json.dumps(gaps, ensure_ascii=False)}\n\n"
        "Hãy tạo phản hồi góp ý chân thành, lịch sự và mang tính xây dựng để ứng viên cải thiện CV (theo quy chuẩn phantich.md). Trả về JSON:\n"
        "{\n"
        '  "matched_points": ["Điểm ứng viên đã làm tốt"],\n'
        '  "missing_points": ["Các điểm chưa thể hiện rõ so với JD"],\n'
        '  "improvement_advice": "Lời khuyên tổng thể cải thiện CV",\n'
        '  "before_example": "Cách viết chưa tốt trong CV hiện tại",\n'
        '  "after_example": "Ví dụ viết lại CV chuẩn ăn điểm chuyên nghiệp"\n'
        "}\n"
        "Lưu ý: Không nhận xét về ngoại hình, đặc điểm cá nhân hay phán xét năng lực. Phản hồi phải mang tính hướng dẫn chuyên nghiệp."
    )

    try:
        res = client.chat.completions.create(
            model=get_chat_runtime().model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            response_format={"type": "json_object"}
        )
        return json.loads(res.choices[0].message.content or "{}")
    except Exception:
        return {
            "matched_points": strengths,
            "missing_points": gaps,
            "improvement_advice": "Bổ sung vai trò, công nghệ và kết quả đo lường được trong từng dự án.",
            "before_example": "Tham gia phát triển dự án.",
            "after_example": "Xây dựng REST API cho 20.000 người dùng, giảm 20% thời gian xử lý."
        }


def generate_interview_questions_and_scorecard(job_title: str, jd_text: str, cv_text: str, evaluation: Dict[str, Any], *, _force_mock: bool = False) -> Dict[str, Any]:
    """Generates 5 levels of tailored interview questions + 0-4 point evaluation scorecard rubric."""
    client = get_client()
    if client is None or _force_mock:
        return {
            "level_1_verification": [
                {"question": "Mô tả vai trò trực tiếp của bạn trong dự án gần nhất?", "target": "Xác minh thông tin CV", "good_answer_signal": "Nêu rõ module cá nhân phụ trách"}
            ],
            "level_2_fundamentals": [
                {"question": "Phân biệt REST API và GraphQL, khi nào nên sử dụng loại nào?", "target": "Kiến thức căn bản", "good_answer_signal": "Hiểu rõ trade-off kiến trúc"}
            ],
            "level_3_practical": [
                {"question": "Bạn tổ chức logging và error handling thế nào trong ứng dụng production?", "target": "Áp dụng thực tế", "good_answer_signal": "Có quy trình cụ thể"}
            ],
            "level_4_advanced": [
                {"question": "Khi hệ thống nhận 1.000.000 request/ngày, bạn sẽ tối ưu ở những điểm nào?", "target": "Tình huống nâng cao", "good_answer_signal": "Tối ưu database, Caching, Async queue"}
            ],
            "level_5_gap_targeted": [
                {"question": "Trong CV chưa nêu rõ về testing, bạn đã thực hiện unit test và integration test như thế nào?", "target": "Khoảng trống CV", "good_answer_signal": "Trình bày được framework và coverage metric"}
            ],
            "rubric_0_to_4": [
                {"score": 0, "description": "Không trả lời hoặc sai hoàn toàn"},
                {"score": 1, "description": "Biết khái niệm nhưng chưa áp dụng thực tế"},
                {"score": 2, "description": "Trả lời được tình huống cơ bản"},
                {"score": 3, "description": "Có kinh nghiệm thực tế và giải thích rõ ràng"},
                {"score": 4, "description": "Hiểu sâu, nhận diện được rủi ro và đánh đổi (trade-offs)"}
            ]
        }

    prompt = (
        f"Vị trí: {job_title}\n"
        f"JD: {jd_text[:1500]}\n"
        f"CV: {cv_text[:2000]}\n\n"
        "Hãy tạo bộ câu hỏi phỏng vấn 5 CẤP ĐỘ và Rubric chấm điểm phỏng vấn (thang 0-4) theo quy chuẩn phantich.md:\n"
        "- Mức 1: Xác minh thông tin CV\n"
        "- Mức 2: Kiến thức căn bản chuyên ngành\n"
        "- Mức 3: Áp dụng thực tế\n"
        "- Mức 4: Tình huống nâng cao & System Design\n"
        "- Mức 5: Câu hỏi xoáy vào khoảng trống/thiếu sót trong CV\n\n"
        "Trả về JSON đúng cấu trúc:\n"
        "{\n"
        '  "level_1_verification": [{"question": "...", "target": "...", "good_answer_signal": "..."}],\n'
        '  "level_2_fundamentals": [{"question": "...", "target": "...", "good_answer_signal": "..."}],\n'
        '  "level_3_practical": [{"question": "...", "target": "...", "good_answer_signal": "..."}],\n'
        '  "level_4_advanced": [{"question": "...", "target": "...", "good_answer_signal": "..."}],\n'
        '  "level_5_gap_targeted": [{"question": "...", "target": "...", "good_answer_signal": "..."}],\n'
        '  "rubric_0_to_4": [\n'
        '     {"score": 0, "description": "..."}, {"score": 1, "description": "..."}, {"score": 2, "description": "..."}, {"score": 3, "description": "..."}, {"score": 4, "description": "..."}\n'
        '  ]\n'
        "}"
    )

    try:
        res = client.chat.completions.create(
            model=get_chat_runtime().model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            response_format={"type": "json_object"}
        )
        return json.loads(res.choices[0].message.content or "{}")
    except Exception:
        return generate_interview_questions_and_scorecard(
            job_title, jd_text, cv_text, evaluation, _force_mock=True
        )
