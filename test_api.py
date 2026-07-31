import json
from ai_service import candidate_assessment

assessment = candidate_assessment(
    "Tuyển Backend Developer. Yêu cầu: Python, FastAPI, Docker, CI/CD. Cần có kinh nghiệm tối ưu hệ thống.",
    "Tôi là lập trình viên Backend có kinh nghiệm 4 năm. Tôi sử dụng Python, Django và Flask. Tôi đã làm việc với Docker. Tôi biết tối ưu database.",
    0.7
)
print(json.dumps(assessment, indent=2, ensure_ascii=False))
