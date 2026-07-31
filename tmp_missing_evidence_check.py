import ai_service
from ai_service import candidate_assessment


def fake_structured_json(*args, **kwargs):
    return {
        'summary': 'ok',
        'score_breakdown': {'skills': 20, 'experience': 15, 'projects': 10, 'other': 5},
        'confidence': 60,
        'recommendation': 'needs_review',
        'strengths': ['a'],
        'gaps': ['b'],
        'interview_questions': ['c'],
    }

ai_service.generate_structured_json = fake_structured_json
result = candidate_assessment('Backend developer', 'CV mẫu', 70)
print(result['analysis_mode'], result['evidence'])
