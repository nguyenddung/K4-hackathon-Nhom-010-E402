export function candidateFromApi(result, localJobId, fileName) {
  const assessment = result.assessment || {}
  const parts = assessment.score_breakdown || {}
  const breakdown = [
    ['Kỹ năng', Number(parts.skills?.score ?? parts.skills ?? 0), 40, parts.skills?.reason || ''],
    ['Kinh nghiệm', Number(parts.experience?.score ?? parts.experience ?? 0), 25, parts.experience?.reason || ''],
    ['Dự án', Number(parts.projects?.score ?? parts.projects ?? 0), 20, parts.projects?.reason || ''],
    ['Yếu tố khác', Number(parts.other?.score ?? parts.other ?? 0), 15, parts.other?.reason || ''],
  ]
  const breakdownTotal = breakdown.reduce((sum, item) => sum + item[1], 0)
  const score = breakdownTotal || Math.round(Number(result.score || 0) * 100)
  const evidence = (assessment.evidence || []).map(item => ({
    skill: item.requirement,
    status: item.status === 'found' ? 'found' : 'missing',
    source: item.status === 'found' ? 'CV đã tải lên' : 'Không tìm thấy trong CV',
    quote: item.evidence,
  }))
  const gaps = (assessment.gaps || []).map((text, index) => ({
    title: evidence.filter(item => item.status === 'missing')[index]?.skill || `Khoảng trống ${index + 1}`,
    severity: 'Cần xác minh',
    text,
  }))
  return {
    id: result.id,
    jobId: localJobId,
    name: result.name,
    initials: result.name.split(/\s+/).map(part => part[0]).slice(-2).join('').toUpperCase(),
    role: 'Ứng viên mới · Vừa phân tích',
    file: fileName,
    updated: 'vừa xong',
    score,
    confidence: Number(assessment.confidence || 0),
    summary: assessment.summary || 'Không đủ bằng chứng để đánh giá.',
    breakdown,
    evidence: evidence.length ? evidence : [{ skill: 'Thông tin CV', status: 'missing', source: 'CV đã tải lên', quote: 'Không đủ bằng chứng để đánh giá.' }],
    gaps: gaps.length ? gaps : [{ title: 'Thông tin cần xác minh', severity: 'Cần xác minh', text: 'Không đủ bằng chứng để đánh giá toàn bộ yêu cầu của JD.' }],
    questions: assessment.interview_questions?.length ? assessment.interview_questions : ['Bạn có thể mô tả dự án backend gần nhất, vai trò và các quyết định kỹ thuật của mình không?'],
  }
}
