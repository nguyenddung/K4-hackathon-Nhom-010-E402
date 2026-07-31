import { useEffect, useMemo, useState } from 'react'
import './App.css'

const _seedJobs = [
  {
    id: 'backend-senior',
    title: 'Senior Backend Developer',
    code: 'ENG-042',
    department: 'Platform Engineering',
    requirements: ['Python', 'FastAPI', 'PostgreSQL', 'Docker', 'Kubernetes', 'System design'],
  },
  {
    id: 'backend-mid',
    title: 'Backend Developer',
    code: 'ENG-038',
    department: 'Product Engineering',
    requirements: ['Python', 'REST API', 'PostgreSQL', 'Docker', 'Redis'],
  },
]

const _seedCandidates = [
  {
    id: 'an',
    jobId: 'backend-senior',
    name: 'Nguyễn Hoàng An',
    initials: 'NA',
    role: 'Backend Engineer · 4 năm KN',
    file: 'Nguyen_Hoang_An_CV.pdf',
    updated: '2 phút trước',
    score: 82,
    confidence: 87,
    summary: 'Ứng viên đáp ứng tốt nền tảng backend với Python, FastAPI và PostgreSQL. Kinh nghiệm triển khai production được mô tả rõ, nhưng chưa có bằng chứng trực tiếp về Kubernetes.',
    breakdown: [
      ['Kỹ năng', 35, 40],
      ['Kinh nghiệm', 20, 25],
      ['Dự án', 17, 20],
      ['Yếu tố khác', 10, 15],
    ],
    evidence: [
      { skill: 'Python', status: 'found', source: 'CV · Kỹ năng', quote: 'Sử dụng Python 3.10 xây dựng các dịch vụ backend trong 4 năm.' },
      { skill: 'FastAPI', status: 'found', source: 'CV · Dự án FinHub', quote: 'Thiết kế 12 REST API bằng FastAPI, xử lý trung bình 2M request/tháng.' },
      { skill: 'PostgreSQL', status: 'found', source: 'CV · Kinh nghiệm', quote: 'Tối ưu truy vấn PostgreSQL, giảm p95 latency từ 480ms xuống 190ms.' },
      { skill: 'Docker', status: 'found', source: 'CV · Kỹ năng', quote: 'Đóng gói và triển khai dịch vụ bằng Docker, GitHub Actions.' },
      { skill: 'Kubernetes', status: 'missing', source: 'Không tìm thấy trong CV', quote: 'Không đủ bằng chứng để đánh giá kinh nghiệm Kubernetes.' },
      { skill: 'System design', status: 'partial', source: 'CV · Dự án FinHub', quote: 'Có mô tả event-driven architecture nhưng chưa nêu quy mô và trade-off.' },
    ],
    gaps: [
      { title: 'Kubernetes', severity: 'Cần xác minh', text: 'JD yêu cầu kinh nghiệm vận hành Kubernetes; CV không đề cập công nghệ này.' },
      { title: 'System design ở quy mô lớn', severity: 'Thiếu bằng chứng', text: 'Có kiến trúc event-driven nhưng chưa mô tả tải, độ tin cậy hoặc quyết định đánh đổi.' },
    ],
    questions: [
      'Bạn đã từng triển khai ứng dụng bằng Kubernetes trong dự án thực tế chưa? Vai trò cụ thể của bạn là gì?',
      'Với hệ thống xử lý 10.000 request/giây, bạn sẽ thiết kế API và tầng dữ liệu như thế nào?',
      'Hãy kể về một sự cố production gần đây: bạn phát hiện, xử lý và ngăn tái diễn ra sao?',
    ],
  },
  {
    id: 'minh',
    jobId: 'backend-senior',
    name: 'Trần Đức Minh',
    initials: 'TM',
    role: 'Software Engineer · 3 năm KN',
    file: 'Tran_Duc_Minh_CV.pdf',
    updated: '18 phút trước',
    score: 71,
    confidence: 74,
    summary: 'Ứng viên có nền tảng Python và API phù hợp. CV thiếu số liệu về quy mô hệ thống, PostgreSQL và kinh nghiệm ownership ở production.',
    breakdown: [['Kỹ năng', 31, 40], ['Kinh nghiệm', 16, 25], ['Dự án', 15, 20], ['Yếu tố khác', 9, 15]],
    evidence: [
      { skill: 'Python', status: 'found', source: 'CV · Kỹ năng', quote: 'Python, Django, Celery.' },
      { skill: 'REST API', status: 'found', source: 'CV · Kinh nghiệm', quote: 'Phát triển API cho nền tảng thương mại điện tử.' },
      { skill: 'PostgreSQL', status: 'partial', source: 'CV · Kỹ năng', quote: 'Có liệt kê PostgreSQL nhưng không nêu thời gian hoặc phạm vi sử dụng.' },
      { skill: 'Kubernetes', status: 'missing', source: 'Không tìm thấy trong CV', quote: 'Không đủ bằng chứng để đánh giá.' },
    ],
    gaps: [
      { title: 'Vận hành production', severity: 'Cần xác minh', text: 'Chưa rõ mức độ ownership và kinh nghiệm xử lý sự cố.' },
      { title: 'Kubernetes', severity: 'Thiếu bằng chứng', text: 'Không tìm thấy bằng chứng trong CV.' },
    ],
    questions: [
      'Bạn chịu trách nhiệm đến đâu trong việc vận hành dịch vụ sau khi release?',
      'Bạn đã tối ưu PostgreSQL trong trường hợp thực tế nào?',
      'Bạn có kinh nghiệm với Kubernetes hoặc một nền tảng orchestration tương đương không?',
    ],
  },
  {
    id: 'linh',
    jobId: 'backend-senior',
    name: 'Lê Thuỳ Linh',
    initials: 'LL',
    role: 'Backend Developer · 5 năm KN',
    file: 'Le_Thuy_Linh_CV.pdf',
    updated: '1 giờ trước',
    score: 89,
    confidence: 92,
    summary: 'Hồ sơ có bằng chứng mạnh về Python, distributed systems và vận hành Kubernetes. Phù hợp cao với yêu cầu kỹ thuật của vị trí.',
    breakdown: [['Kỹ năng', 37, 40], ['Kinh nghiệm', 23, 25], ['Dự án', 18, 20], ['Yếu tố khác', 11, 15]],
    evidence: [
      { skill: 'Python & FastAPI', status: 'found', source: 'CV · Kinh nghiệm', quote: 'Tech lead nhóm 4 người phát triển microservices bằng Python, FastAPI.' },
      { skill: 'Kubernetes', status: 'found', source: 'CV · Dự án PayFlow', quote: 'Vận hành 18 services trên EKS, thiết lập autoscaling và observability.' },
      { skill: 'PostgreSQL', status: 'found', source: 'CV · Dự án PayFlow', quote: 'Thiết kế partitioning cho bảng giao dịch 800M records.' },
      { skill: 'Mentoring', status: 'partial', source: 'CV · Kinh nghiệm', quote: 'Có vai trò tech lead nhưng chưa mô tả hoạt động coaching.' },
    ],
    gaps: [{ title: 'Mentoring', severity: 'Cần xác minh', text: 'JD ưu tiên khả năng nâng tầm đội ngũ; CV mới nêu vai trò tech lead.' }],
    questions: [
      'Bạn đã giúp một thành viên trong nhóm phát triển năng lực như thế nào?',
      'Quyết định system design khó nhất ở PayFlow là gì và trade-off bạn chấp nhận?',
    ],
  },
  {
    id: 'phuong',
    jobId: 'backend-mid',
    name: 'Phạm Minh Phương',
    initials: 'PP',
    role: 'Backend Developer · 2 năm KN',
    file: 'Pham_Minh_Phuong_CV.pdf',
    updated: 'Hôm qua',
    score: 76,
    confidence: 81,
    summary: 'Ứng viên có nền tảng Python, REST API và PostgreSQL phù hợp cấp độ Middle. Cần xác minh thêm về Redis, monitoring và khả năng xử lý sự cố production.',
    breakdown: [['Kỹ năng', 33, 40], ['Kinh nghiệm', 18, 25], ['Dự án', 16, 20], ['Yếu tố khác', 9, 15]],
    evidence: [
      { skill: 'Python', status: 'found', source: 'CV · Kinh nghiệm', quote: 'Phát triển backend bằng Python, Django và FastAPI trong 2 năm.' },
      { skill: 'PostgreSQL', status: 'found', source: 'CV · Dự án Ecom', quote: 'Thiết kế schema và tối ưu index cho PostgreSQL.' },
      { skill: 'Docker', status: 'found', source: 'CV · Kỹ năng', quote: 'Docker, Docker Compose, CI/CD.' },
      { skill: 'Redis', status: 'missing', source: 'Không tìm thấy trong CV', quote: 'Không đủ bằng chứng để đánh giá kinh nghiệm Redis.' },
    ],
    gaps: [
      { title: 'Redis', severity: 'Thiếu bằng chứng', text: 'JD yêu cầu Redis nhưng CV không đề cập.' },
      { title: 'Production monitoring', severity: 'Cần xác minh', text: 'Chưa có bằng chứng về logging, metrics hoặc alerting.' },
    ],
    questions: [
      'Bạn đã dùng Redis cho bài toán nào và lựa chọn cấu trúc dữ liệu ra sao?',
      'Bạn theo dõi sức khoẻ một API trên production bằng những chỉ số nào?',
    ],
  },
]

const _initialAudit = [
  { id: 1, time: '10:32 · Hôm nay', actor: 'TalentScreen AI', action: 'Hoàn tất phân tích', detail: 'Nguyễn Hoàng An · 82/100 · Confidence 87%' },
  { id: 2, time: '10:31 · Hôm nay', actor: 'Hệ thống', action: 'Ẩn danh dữ liệu CV', detail: 'Đã loại bỏ 4 trường PII trước khi gửi tới AI' },
  { id: 3, time: '09:14 · Hôm nay', actor: 'Mai Anh (HR)', action: 'Tải lên hồ sơ', detail: 'Nguyễn Hoàng An · Senior Backend Developer' },
]

const backendJd = `Tuyển Backend Developer. Yêu cầu: Python, FastAPI, REST API, PostgreSQL, Docker, Kubernetes, system design, tối ưu hiệu năng và vận hành production. Ứng viên cần mô tả rõ vai trò, thời gian sử dụng công nghệ, quy mô dự án và kết quả đo lường được.`

async function readApiPayload(response) {
  const body = await response.text()
  if (!body) return {}
  try {
    return JSON.parse(body)
  } catch {
    return { detail: response.ok ? 'API trả về dữ liệu không hợp lệ.' : body.startsWith('Internal Server Error') ? 'Backend gặp lỗi khi xử lý yêu cầu. Vui lòng thử lại hoặc kiểm tra terminal backend.' : body.slice(0, 240) }
  }
}

function candidateFromApi(result, localJobId = result.job_id, fileName = result.cv_filename) {
  const assessment = result.assessment || {}
  const parts = assessment.score_breakdown || {}
  const breakdown = [
    ['Kỹ năng', Number(parts.skills || 0), 40],
    ['Kinh nghiệm', Number(parts.experience || 0), 25],
    ['Dự án', Number(parts.projects || 0), 20],
    ['Yếu tố khác', Number(parts.other || 0), 15],
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
    role: result.job_title || 'Ứng viên đã sàng lọc',
    file: fileName || 'CV đã mã hoá',
    updated: result.updated_at ? 'đã cập nhật' : 'đã phân tích',
    score,
    confidence: Number(assessment.confidence || 0),
    summary: assessment.summary || 'Không đủ bằng chứng để đánh giá.',
    breakdown,
    evidence: evidence.length ? evidence : [{ skill: 'Thông tin CV', status: 'missing', source: 'CV đã tải lên', quote: 'Không đủ bằng chứng để đánh giá.' }],
    gaps: gaps.length ? gaps : [{ title: 'Thông tin cần xác minh', severity: 'Cần xác minh', text: 'Không đủ bằng chứng để đánh giá toàn bộ yêu cầu của JD.' }],
    questions: assessment.interview_questions?.length ? assessment.interview_questions : ['Bạn có thể mô tả dự án backend gần nhất, vai trò và các quyết định kỹ thuật của mình không?'],
    analysisMode: assessment.analysis_mode || 'fallback',
    aiProvider: assessment.provider || 'Không xác định',
    aiModel: assessment.model || 'Không xác định',
    fallbackReason: assessment.fallback_reason || '',
    recommendation: assessment.recommendation || 'needs_review',
    hrDecision: result.decision || null,
    decisionNote: result.note || '',
    overrideScore: result.override_score,
  }
}

const icons = {
  pipeline: <><rect x="3" y="6" width="18" height="14" rx="2"/><path d="M8 6V4h8v2M3 11h18M9 11v2h6v-2"/></>,
  screen: <><path d="M4 5h16v14H4z"/><path d="M8 9h8M8 13h5"/></>,
  audit: <><path d="M12 3a9 9 0 1 0 9 9"/><path d="M12 7v5l3 2M16 3h5v5"/></>,
  shield: <><path d="M12 3 5 6v5c0 4.4 2.8 8 7 10 4.2-2 7-5.6 7-10V6z"/><path d="m9 12 2 2 4-4"/></>,
  chevron: <path d="m9 18 6-6-6-6"/>,
}

function Icon({ name, size = 18 }) {
  return <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">{icons[name]}</svg>
}

function AuthScreen({ onAuthenticated }) {
  const [mode, setMode] = useState('login')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const submit = async event => {
    event.preventDefault()
    setLoading(true)
    setError('')
    const data = Object.fromEntries(new FormData(event.currentTarget))
    try {
      const response = await fetch(`/api/auth/${mode === 'login' ? 'login' : 'register'}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(mode === 'login' ? { email: data.email, password: data.password } : { name: data.name, email: data.email, password: data.password, role: data.role }),
      })
      const payload = await readApiPayload(response)
      if (!response.ok) throw new Error(payload.detail || 'Không thể xác thực tài khoản.')
      localStorage.setItem('talentscreen-session', JSON.stringify(payload))
      onAuthenticated(payload)
    } catch (submitError) {
      setError(`${submitError.message} Hãy kiểm tra backend đang chạy ở cổng 8000.`)
    } finally {
      setLoading(false)
    }
  }
  return <div className="auth-shell">
    <section className="auth-story">
      <div className="logo auth-logo"><span className="logo-symbol">T</span><span>TalentScreen <b>AI</b></span></div>
      <div className="auth-copy"><p className="eyebrow">EVIDENCE-BASED HIRING</p><h1>Tuyển đúng người.<br/><em>Hiểu rõ lý do.</em></h1><p>Trợ lý AI giúp HR sàng lọc Backend Developer nhất quán, có bằng chứng và luôn giữ con người ở vị trí quyết định.</p></div>
      <div className="auth-principles"><span>01 <b>Grounded evidence</b></span><span>02 <b>Human decision</b></span><span>03 <b>Audit-ready</b></span></div>
    </section>
    <section className="auth-form-side"><form className="auth-card" onSubmit={submit}>
      <p className="eyebrow">{mode === 'login' ? 'WELCOME BACK' : 'CREATE WORKSPACE'}</p>
      <h2>{mode === 'login' ? 'Đăng nhập vào TalentScreen' : 'Tạo tài khoản HR'}</h2>
      <p>{mode === 'login' ? 'Tiếp tục quản lý pipeline tuyển dụng của bạn.' : 'Bắt đầu workspace sàng lọc minh bạch cho đội ngũ.'}</p>
      {mode === 'register' && <><label>Họ và tên<input name="name" required minLength="2" placeholder="Nguyễn Minh Anh"/></label><label>Vai trò<select name="role"><option>HR Manager</option><option>Recruiter</option></select></label></>}
      <label>Email<input name="email" type="email" required defaultValue={mode === 'login' ? 'demo@vairecruiter.local' : ''} placeholder="hr@company.com"/></label>
      <label>Mật khẩu<input name="password" type="password" required minLength="8" defaultValue={mode === 'login' ? 'Demo@123' : ''} placeholder="Tối thiểu 8 ký tự"/></label>
      {error && <div className="auth-error">{error}</div>}
      <button className="auth-submit" disabled={loading}>{loading ? 'Đang xử lý...' : mode === 'login' ? 'Đăng nhập →' : 'Tạo tài khoản →'}</button>
      <div className="auth-switch">{mode === 'login' ? 'Chưa có tài khoản?' : 'Đã có tài khoản?'} <button type="button" onClick={() => { setMode(mode === 'login' ? 'register' : 'login'); setError('') }}>{mode === 'login' ? 'Đăng ký ngay' : 'Đăng nhập'}</button></div>
    </form></section>
  </div>
}

function App() {
  const [session, setSession] = useState(() => JSON.parse(localStorage.getItem('talentscreen-session') || 'null'))
  if (!session) return <AuthScreen onAuthenticated={setSession}/>
  return <WorkspaceApp session={session} onLogout={() => { localStorage.removeItem('talentscreen-session'); setSession(null) }}/>
}

function WorkspaceApp({ session, onLogout }) {
  const [view, setView] = useState('pipeline')
  const [jobList, setJobList] = useState([])
  const [jobId, setJobId] = useState('')
  const [candidateList, setCandidateList] = useState([])
  const available = useMemo(() => candidateList.filter(item => item.jobId === jobId), [candidateList, jobId])
  const [candidateId, setCandidateId] = useState('')
  const candidate = available.find(item => item.id === candidateId) || available[0]
  const [tab, setTab] = useState('overview')
  const [isRunning, setIsRunning] = useState(false)
  const [fresh, setFresh] = useState(false)
  const [decision, setDecision] = useState(null)
  const [audit, setAudit] = useState([])
  const [dialog, setDialog] = useState(null)
  const [override, setOverride] = useState(false)
  const [overrideScore, setOverrideScore] = useState(0)
  const [toast, setToast] = useState('')
  const [uploadOpen, setUploadOpen] = useState(false)
  const [uploadJobId, setUploadJobId] = useState('')
  const [uploading, setUploading] = useState(false)
  const [uploadError, setUploadError] = useState('')
  const [createJobOpen, setCreateJobOpen] = useState(false)
  const [creatingJob, setCreatingJob] = useState(false)
  const [createJobError, setCreateJobError] = useState('')
  const [workspaceLoading, setWorkspaceLoading] = useState(true)
  const [workspaceError, setWorkspaceError] = useState('')

  useEffect(() => {
    let active = true
    const loadWorkspace = async () => {
      setWorkspaceLoading(true)
      setWorkspaceError('')
      try {
        const headers = { Authorization: `Bearer ${session.access_token}` }
        const [jobsResponse, candidatesResponse, auditResponse] = await Promise.all([
          fetch('/api/jobs', { headers }),
          fetch('/api/candidates?limit=100', { headers }),
          fetch('/api/audit?limit=100', { headers }),
        ])
        if ([jobsResponse, candidatesResponse, auditResponse].some(response => response.status === 401)) {
          onLogout()
          return
        }
        if (!jobsResponse.ok || !candidatesResponse.ok || !auditResponse.ok) throw new Error('Không thể tải dữ liệu workspace.')
        const [apiJobs, candidatePage, apiAudit] = await Promise.all([readApiPayload(jobsResponse), readApiPayload(candidatesResponse), readApiPayload(auditResponse)])
        if (!active) return
        const mappedJobs = apiJobs.map(job => ({ ...job, department: job.department || 'Engineering', code: job.code || `JOB-${job.id.slice(0, 6).toUpperCase()}` }))
        const mappedCandidates = candidatePage.items.map(item => candidateFromApi(item))
        setJobList(mappedJobs)
        setCandidateList(mappedCandidates)
        setAudit(apiAudit.map(item => ({ id: item.id, time: new Date(item.created_at).toLocaleString('vi-VN'), actor: item.actor_id === session.user.id ? session.user.name : 'Hệ thống', action: item.action, detail: item.detail })))
        if (mappedCandidates.length) {
          setJobId(mappedCandidates[0].jobId)
          setCandidateId(mappedCandidates[0].id)
          setOverrideScore(mappedCandidates[0].score)
          setDecision(mappedCandidates[0].hrDecision ? { type: mappedCandidates[0].hrDecision === 'Pass' ? 'advance' : 'hold', note: mappedCandidates[0].decisionNote, score: mappedCandidates[0].overrideScore ?? mappedCandidates[0].score, overridden: mappedCandidates[0].overrideScore != null } : null)
        } else if (mappedJobs.length) {
          setJobId(mappedJobs[0].id)
          setUploadJobId(mappedJobs[0].id)
        }
      } catch (error) {
        if (active) setWorkspaceError(error.message)
      } finally {
        if (active) setWorkspaceLoading(false)
      }
    }
    loadWorkspace()
    return () => { active = false }
  }, [session.access_token, session.user.id, session.user.name, onLogout])

  const selectCandidate = id => {
    setCandidateId(id)
    setTab('overview')
    setFresh(false)
    setOverride(false)
    const next = candidateList.find(item => item.id === id)
    setOverrideScore(next?.score || 0)
    setDecision(next?.hrDecision ? { type: next.hrDecision === 'Pass' ? 'advance' : 'hold', note: next.decisionNote, score: next.overrideScore ?? next.score, overridden: next.overrideScore != null } : null)
  }

  const uploadCv = async event => {
    event.preventDefault()
    setUploadError('')
    const data = new FormData(event.currentTarget)
    const file = data.get('cv')
    if (!file?.name) return setUploadError('Vui lòng chọn CV.')
    const extension = file.name.split('.').pop()?.toLowerCase()
    if (!['pdf', 'docx'].includes(extension)) return setUploadError('Chỉ hỗ trợ PDF hoặc DOCX.')
    if (file.size > 10 * 1024 * 1024) return setUploadError('CV phải nhỏ hơn 10 MB.')
    setUploading(true)
    try {
      const headers = { Authorization: `Bearer ${session.access_token}` }
      const jobsResponse = await fetch('/api/jobs', { headers })
      if (!jobsResponse.ok) throw new Error('Không thể tải danh sách vị trí từ API.')
      const apiJobs = await readApiPayload(jobsResponse)
      const localJob = jobList.find(item => item.id === data.get('jobId'))
      let apiJob = apiJobs.find(item => item.id === localJob.id) || apiJobs.find(item => item.title.toLowerCase() === localJob.title.toLowerCase())
      if (!apiJob) {
        const createResponse = await fetch('/api/jobs', {
          method: 'POST',
          headers: { ...headers, 'Content-Type': 'application/json' },
          body: JSON.stringify({ title: localJob.title, description: localJob.description || backendJd, department: localJob.department, code: localJob.code }),
        })
        if (!createResponse.ok) throw new Error('Không thể tạo vị trí trên API.')
        apiJob = await readApiPayload(createResponse)
      }
      const uploadData = new FormData()
      uploadData.append('job_id', apiJob.id)
      uploadData.append('name', data.get('name'))
      uploadData.append('email', data.get('email'))
      uploadData.append('cv', file)
      const response = await fetch('/api/candidates/upload', { method: 'POST', headers, body: uploadData })
      const payload = await readApiPayload(response)
      if (!response.ok) throw new Error(payload.detail || 'Không thể phân tích CV.')
      const newCandidate = candidateFromApi(payload, localJob.id, file.name)
      setCandidateList(items => [newCandidate, ...items])
      setJobId(localJob.id)
      setCandidateId(newCandidate.id)
      setDecision(null)
      setTab('overview')
      setUploadOpen(false)
      const eventItem = { id: Date.now(), time: 'Vừa xong', actor: 'TalentScreen AI', action: 'Upload & phân tích CV', detail: `${newCandidate.name} · ${newCandidate.score}/100 · ${file.name}` }
      const nextAudit = [eventItem, ...audit]
      setAudit(nextAudit)
      setToast(`Đã phân tích CV của ${newCandidate.name}.`)
    } catch (error) {
      setUploadError(`${error.message} Hãy kiểm tra backend đang chạy ở cổng 8000.`)
    } finally {
      setUploading(false)
    }
  }

  const createJob = async event => {
    event.preventDefault()
    setCreateJobError('')
    setCreatingJob(true)
    const data = new FormData(event.currentTarget)
    try {
      const response = await fetch('/api/jobs', {
        method: 'POST',
        headers: { Authorization: `Bearer ${session.access_token}`, 'Content-Type': 'application/json' },
        body: JSON.stringify({ title: data.get('title'), description: data.get('description'), department: data.get('department'), code: data.get('code') || null }),
      })
      const payload = await readApiPayload(response)
      if (!response.ok) throw new Error(payload.detail || 'Không thể tạo Job.')
      const newJob = {
        id: payload.id,
        title: payload.title,
        code: payload.code,
        department: payload.department,
        description: payload.description,
        requirements: [],
      }
      setJobList(items => [newJob, ...items])
      setCreateJobOpen(false)
      setUploadJobId(newJob.id)
      setUploadError('')
      setUploadOpen(true)
      setToast(`Đã tạo ${newJob.title}. Hãy upload CV đầu tiên cho vị trí này.`)
    } catch (error) {
      setCreateJobError(`${error.message} Hãy kiểm tra backend đang chạy ở cổng 8000.`)
    } finally {
      setCreatingJob(false)
    }
  }

  const runScreening = async () => {
    if (!candidate) return
    setIsRunning(true)
    setFresh(false)
    try {
      const response = await fetch(`/api/candidates/${candidate.id}/rescreen`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${session.access_token}` },
      })
      const payload = await readApiPayload(response)
      if (!response.ok) throw new Error(payload.detail || 'Không thể phân tích lại CV.')
      const updated = candidateFromApi(payload)
      setCandidateList(items => items.map(item => item.id === updated.id ? updated : item))
      setOverrideScore(updated.score)
      setIsRunning(false)
      setFresh(true)
      setAudit(items => [{ id: Date.now(), time: 'Vừa xong', actor: 'TalentScreen AI', action: 'Phân tích lại hồ sơ', detail: `${updated.name} · ${updated.score}/100 · Grounded on CV + JD` }, ...items])
      setToast('Phân tích hoàn tất — mọi kết luận đều có nguồn bằng chứng.')
    } catch (error) {
      setToast(error.message)
    } finally {
      setIsRunning(false)
    }
  }

  const saveDecision = async event => {
    event.preventDefault()
    const data = new FormData(event.currentTarget)
    const chosen = dialog
    const score = override ? Number(overrideScore) : candidate.score
    try {
      const response = await fetch(`/api/candidates/${candidate.id}/decision`, {
        method: 'PUT',
        headers: { Authorization: `Bearer ${session.access_token}`, 'Content-Type': 'application/json' },
        body: JSON.stringify({ decision: chosen === 'advance' ? 'Pass' : 'Hold', note: data.get('note'), override_score: override ? score : null }),
      })
      const payload = await readApiPayload(response)
      if (!response.ok) throw new Error(payload.detail || 'Không thể lưu quyết định.')
      const savedDecision = { type: chosen, note: payload.note, score, overridden: override, at: 'Vừa xong' }
      setDecision(savedDecision)
      setCandidateList(items => items.map(item => item.id === candidate.id ? { ...item, hrDecision: payload.decision, decisionNote: payload.note, overrideScore: payload.override_score } : item))
      const label = chosen === 'advance' ? 'Đề xuất vào vòng tiếp' : 'Chưa đề xuất'
      setAudit(items => [{ id: Date.now(), time: 'Vừa xong', actor: session.user.name, action: label, detail: `${candidate.name}${override ? ` · Override ${candidate.score} → ${score}` : ' · Giữ nguyên điểm AI'}` }, ...items])
      setDialog(null)
      setToast(`Đã lưu quyết định HR cho ${candidate.name} vào database.`)
    } catch (error) {
      setToast(error.message)
    }
  }

  return <div className="app-shell">
    <aside className="sidebar">
      <div className="logo"><span className="logo-symbol">T</span><span>TalentScreen <b>AI</b></span></div>
      <p className="workspace-label">WORKSPACE</p>
      <nav>
        <button className={view === 'pipeline' ? 'active' : ''} onClick={() => setView('pipeline')}><Icon name="pipeline"/>Phòng ban & Job</button>
        <button className={view === 'screen' ? 'active' : ''} onClick={() => setView(candidate ? 'screen' : 'pipeline')}><Icon name="screen"/>Chi tiết đánh giá</button>
        <button className={view === 'audit' ? 'active' : ''} onClick={() => setView('audit')}><Icon name="audit"/>Nhật ký đánh giá</button>
      </nav>
      <div className="sidebar-note"><Icon name="shield"/><div><b>Human-in-the-loop</b><p>AI chỉ đề xuất. Bạn luôn là người quyết định cuối cùng.</p></div></div>
      <div className="profile"><span>{session.user.name.split(/\s+/).map(part => part[0]).slice(-2).join('').toUpperCase()}</span><div><b>{session.user.name}</b><small>{session.user.role}</small></div><button onClick={onLogout} title="Đăng xuất" aria-label="Đăng xuất">↪</button></div>
    </aside>

    <main>
      <header className="topbar">
        <div className="crumb"><span>TalentScreen</span><Icon name="chevron" size={14}/><b>{view === 'audit' ? 'Nhật ký đánh giá' : view === 'pipeline' ? 'Phòng ban & Job' : 'Sàng lọc ứng viên'}</b></div>
        <div className="top-actions"><span className="privacy"><span/>Dữ liệu đã được bảo vệ</span><button className="avatar">{session.user.name.split(/\s+/).map(part => part[0]).slice(-2).join('').toUpperCase()}</button></div>
      </header>

      {toast && <div className="toast">{toast}<button onClick={() => setToast('')}>×</button></div>}

      {workspaceLoading ? <WorkspaceState title="Đang tải workspace..." text="TalentScreen đang đồng bộ Job, ứng viên và quyết định từ database."/> : workspaceError ? <WorkspaceState title="Không thể tải dữ liệu" text={workspaceError} action="Thử lại" onAction={() => window.location.reload()}/> : view === 'audit' ? <AuditView audit={audit}/> : view === 'pipeline' ? <PipelineView jobs={jobList} candidates={candidateList} onCreateJob={() => { setCreateJobError(''); setCreateJobOpen(true) }} onUpload={selectedJobId => { setUploadJobId(selectedJobId); setUploadError(''); setUploadOpen(true) }} onOpenCandidate={(item, selectedJob) => { setJobId(selectedJob.id); selectCandidate(item.id); setView('screen') }}/> : !candidate ? <WorkspaceState title="Chưa có ứng viên để đánh giá" text="Hãy tạo Job và upload CV đầu tiên. TalentScreen sẽ phân tích hồ sơ ngay sau khi tải lên." action="Về danh sách Job" onAction={() => setView('pipeline')}/> : <div className="workspace">
        <section className="page-heading">
          <div><button className="back-link" onClick={() => setView('pipeline')}>← Quay lại danh sách</button><h1>{candidate.name}</h1><p>{jobList.find(job => job.id === candidate.jobId)?.title} · Đánh giá dựa trên CV và JD</p></div>
          <div className="heading-actions"><button className="create-job-button" onClick={() => { setCreateJobError(''); setCreateJobOpen(true) }}>＋ Tạo Job</button><button className="upload-button" onClick={() => { setUploadJobId(jobId); setUploadError(''); setUploadOpen(true) }}>↑ Upload CV</button><button className="run-button" onClick={runScreening} disabled={isRunning}><span className={isRunning ? 'spinner' : ''}>{isRunning ? '' : '✦'}</span>{isRunning ? 'Đang phân tích...' : 'Phân tích lại'}</button></div>
        </section>

        <section className="selection-card">
          <div className="select-step"><span>01</span><label>VỊ TRÍ TUYỂN DỤNG<select value={jobId} onChange={e => { const nextCandidate = candidateList.find(item => item.jobId === e.target.value); if (nextCandidate) { setJobId(e.target.value); selectCandidate(nextCandidate.id) } else { setUploadJobId(e.target.value); setUploadOpen(true); setToast('Job này chưa có ứng viên — hãy upload CV đầu tiên.') } }}>{jobList.map(job => <option key={job.id} value={job.id}>{job.title} · {job.code}</option>)}</select><small>{jobList.find(job => job.id === jobId)?.department}</small></label></div>
          <div className="step-arrow">→</div>
          <div className="select-step"><span>02</span><label>ỨNG VIÊN<select value={candidate.id} onChange={e => selectCandidate(e.target.value)}>{available.map(item => <option key={item.id} value={item.id}>{item.name}</option>)}</select><small>{candidate.role}</small></label></div>
          <div className="file-chip"><span>PDF</span><div><b>{candidate.file}</b><small>Cập nhật {candidate.updated}</small></div></div>
        </section>

        {fresh && <div className="fresh-banner"><span>✓</span><div><b>Phân tích vừa được cập nhật</b><p>Kết quả được grounded trên CV, JD và competency framework.</p></div><button onClick={() => setFresh(false)}>×</button></div>}

        <div className="results-grid">
          <section className="score-panel card">
            <div className="card-title"><div><p className="eyebrow">MATCH SCORE</p><h2>Mức độ phù hợp</h2></div><span className={`ai-badge ${candidate.analysisMode === 'openai' || candidate.analysisMode === 'gemini' ? 'openai' : 'fallback'}`}>{candidate.analysisMode === 'openai' || candidate.analysisMode === 'gemini' ? `✦ ${candidate.aiProvider || (candidate.analysisMode === 'gemini' ? 'Google Gemini' : 'OpenAI')} · ${candidate.aiModel || 'unknown'}` : '⚙ Local fallback'}</span></div>
            {candidate.analysisMode !== 'openai' && candidate.analysisMode !== 'gemini' && <div className="fallback-alert"><b>Kết quả này chưa được tạo bởi AI</b><span>{candidate.fallbackReason || 'Đây là assessment cũ hoặc mô hình AI chưa khả dụng khi hồ sơ được phân tích.'}</span><button onClick={runScreening} disabled={isRunning}>{isRunning ? 'Đang gọi AI...' : 'Phân tích lại bằng AI'}</button></div>}
            <div className="score-hero">
              <div className="score-ring" style={{ '--score': `${candidate.score * 3.6}deg` }}><div><strong>{candidate.score}</strong><span>/100</span></div></div>
              <div className="score-copy"><b>{candidate.score >= 80 ? 'Phù hợp cao' : candidate.score >= 65 ? 'Cần HR xem thêm' : 'Phù hợp thấp'}</b><p>{candidate.score >= 80 ? 'Ứng viên đáp ứng phần lớn yêu cầu quan trọng.' : 'Hãy xem bằng chứng và khoảng trống trước khi quyết định.'}</p><div className="confidence"><span>Độ tin cậy</span><strong>{candidate.confidence}%</strong><i><em style={{ width: `${candidate.confidence}%` }}/></i></div></div>
            </div>
            <div className="breakdown">{candidate.breakdown.map(([name, value, max]) => <div key={name}><span>{name}</span><i><em style={{ width: `${value / max * 100}%` }}/></i><b>{value}<small>/{max}</small></b></div>)}</div>
            <div className="grounded-note"><Icon name="shield"/><p><b>Chỉ dùng bằng chứng có trong hồ sơ</b><br/>Thông tin thiếu được đánh dấu để HR xác minh.</p></div>
          </section>

          <section className="analysis-panel card">
            <div className="tabs">
              <button className={tab === 'overview' ? 'active' : ''} onClick={() => setTab('overview')}>Tổng quan</button>
              <button className={tab === 'evidence' ? 'active' : ''} onClick={() => setTab('evidence')}>Bằng chứng <span>{candidate.evidence.length}</span></button>
              <button className={tab === 'questions' ? 'active' : ''} onClick={() => setTab('questions')}>Câu hỏi PV <span>{candidate.questions.length}</span></button>
            </div>

            {tab === 'overview' && <div className="tab-content">
              <div className="analysis-heading"><span>✦</span><div><p className="eyebrow">{candidate.analysisMode === 'openai' || candidate.analysisMode === 'gemini' ? `AI EXPLANATION · ${candidate.aiModel || (candidate.analysisMode === 'gemini' ? 'Google Gemini' : 'OpenAI')}` : 'RULE-BASED EXPLANATION'}</p><h2>Tại sao ứng viên được {candidate.score} điểm?</h2></div></div>
              <p className="summary">{candidate.summary}</p>
              <h3>Bằng chứng nổi bật</h3>
              <div className="evidence-compact">{candidate.evidence.slice(0, 4).map(item => <div key={item.skill}><span className={`status-icon ${item.status}`}>{item.status === 'found' ? '✓' : item.status === 'partial' ? '~' : '!'}</span><div><b>{item.skill}</b><p>{item.quote}</p><small>{item.source}</small></div></div>)}</div>
              <button className="text-link" onClick={() => setTab('evidence')}>Xem toàn bộ bằng chứng <span>→</span></button>
              <div className="gap-header"><div><p className="eyebrow">GAP DETECTION</p><h3>Khoảng trống cần xác minh</h3></div><span>{candidate.gaps.length} điểm</span></div>
              <div className="gap-list">{candidate.gaps.map(gap => <article key={gap.title}><span>!</span><div><b>{gap.title}</b><p>{gap.text}</p></div><small>{gap.severity}</small></article>)}</div>
              <div className="question-preview-head"><div><p className="eyebrow">INTERVIEW QUESTIONS</p><h3>Câu hỏi phỏng vấn gợi ý</h3></div><button onClick={() => setTab('questions')}>Xem tất cả {candidate.questions.length} câu →</button></div>
              <div className="question-preview">{candidate.questions.slice(0, 2).map((question, index) => <article key={question}><span>{index + 1}</span><p>{question}</p></article>)}</div>
            </div>}

            {tab === 'evidence' && <div className="tab-content">
              <div className="analysis-heading"><span>⌕</span><div><p className="eyebrow">GROUNDED EVIDENCE</p><h2>Đối chiếu yêu cầu và CV</h2></div></div>
              <p className="summary">Mỗi kết luận dưới đây đều trỏ về một đoạn cụ thể trong CV. “Thiếu” không đồng nghĩa ứng viên không có kỹ năng — chỉ là chưa đủ bằng chứng.</p>
              <div className="evidence-full">{candidate.evidence.map(item => <article key={item.skill}><div className="evidence-title"><span className={`status-icon ${item.status}`}>{item.status === 'found' ? '✓' : item.status === 'partial' ? '~' : '?'}</span><b>{item.skill}</b><small className={item.status}>{item.status === 'found' ? 'Đã xác thực' : item.status === 'partial' ? 'Một phần' : 'Thiếu bằng chứng'}</small></div><blockquote>“{item.quote}”</blockquote><p>{item.source}</p></article>)}</div>
            </div>}

            {tab === 'questions' && <div className="tab-content">
              <div className="analysis-heading"><span>?</span><div><p className="eyebrow">INTERVIEW COPILOT</p><h2>Câu hỏi xác minh đề xuất</h2></div></div>
              <p className="summary">Các câu hỏi được tạo từ khoảng trống trong CV, giúp HR xác minh thay vì để AI tự suy đoán.</p>
              <div className="question-list">{candidate.questions.map((question, index) => <article key={question}><span>{String(index + 1).padStart(2, '0')}</span><p>{question}</p><button onClick={() => { navigator.clipboard?.writeText(question); setToast('Đã sao chép câu hỏi.') }}>Sao chép</button></article>)}</div>
            </div>}
          </section>
        </div>

        <section className="decision-bar">
          <div><p className="eyebrow">HUMAN DECISION</p><h2>Quyết định của HR</h2><p>AI không tự động tuyển hoặc loại ứng viên.</p></div>
          {decision && <div className={`saved-decision ${decision.type}`}><span>✓</span><div><b>{decision.type === 'advance' ? 'Đã đề xuất vào vòng tiếp' : 'Đã chọn chưa đề xuất'}</b><small>{decision.overridden ? `HR override: ${decision.score}/100` : 'Giữ nguyên đánh giá AI'}</small></div></div>}
          <div className="decision-actions"><button className="secondary" onClick={() => setDialog('hold')}>Chưa đề xuất</button><button className="primary" onClick={() => setDialog('advance')}>Đề xuất vào vòng tiếp <span>→</span></button></div>
        </section>
      </div>}
    </main>

    {dialog && <div className="modal-backdrop" onMouseDown={e => e.target === e.currentTarget && setDialog(null)}>
      <form className="modal" onSubmit={saveDecision}>
        <button type="button" className="modal-close" onClick={() => setDialog(null)}>×</button>
        <p className="eyebrow">HUMAN-IN-THE-LOOP</p>
        <h2>{dialog === 'advance' ? 'Đề xuất ứng viên vào vòng tiếp?' : 'Chưa đề xuất ứng viên?'}</h2>
        <p>Quyết định này thuộc về HR và sẽ được lưu vào audit log cùng đánh giá của AI.</p>
        <div className="decision-summary"><span>{candidate.initials}</span><div><b>{candidate.name}</b><small>AI Score {candidate.score}/100 · Confidence {candidate.confidence}%</small></div></div>
        <label className="override-toggle"><input type="checkbox" checked={override} onChange={e => setOverride(e.target.checked)}/><span/><div><b>Điều chỉnh điểm AI</b><small>Dùng khi đánh giá chuyên môn của HR khác với AI.</small></div></label>
        {override && <label className="range-label">Điểm điều chỉnh <b>{overrideScore}/100</b><input type="range" min="0" max="100" value={overrideScore} onChange={e => setOverrideScore(e.target.value)}/></label>}
        <label className="note-label">Nhận xét của HR<textarea name="note" rows="4" required placeholder="Ghi rõ lý do cho quyết định để đảm bảo audit minh bạch..."/></label>
        <div className="modal-actions"><button type="button" className="secondary" onClick={() => setDialog(null)}>Huỷ</button><button className={dialog === 'advance' ? 'primary' : 'danger'}>Xác nhận & lưu nhật ký</button></div>
      </form>
    </div>}

    {uploadOpen && <div className="modal-backdrop" onMouseDown={e => e.target === e.currentTarget && !uploading && setUploadOpen(false)}>
      <form className="modal upload-modal" onSubmit={uploadCv}>
        <button type="button" className="modal-close" disabled={uploading} onClick={() => setUploadOpen(false)}>×</button>
        <p className="eyebrow">CV SCREENING</p>
        <h2>Upload và phân tích CV</h2>
        <p>CV được ẩn danh trước khi gửi đến AI. Hệ thống chỉ dùng CV, JD và competency framework để đánh giá.</p>
        <div className="upload-fields">
          <label>Họ và tên<input name="name" required minLength="2" placeholder="VD: Nguyễn Minh Anh"/></label>
          <label>Email<input name="email" type="email" placeholder="email@domain.com"/></label>
          <label className="full-field">Vị trí ứng tuyển<select name="jobId" defaultValue={uploadJobId}>{jobList.map(job => <option key={job.id} value={job.id}>{job.title}</option>)}</select></label>
          <label className="file-drop full-field"><input name="cv" type="file" accept=".pdf,.docx,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document" required/><span>↑</span><b>Chọn CV từ máy tính</b><small>PDF hoặc DOCX · tối đa 10 MB</small></label>
        </div>
        {uploadError && <div className="upload-error">{uploadError}</div>}
        <div className="upload-security"><Icon name="shield"/><span>PII được mã hoá khi lưu trữ và loại bỏ trước khi AI phân tích.</span></div>
        <div className="modal-actions"><button type="button" className="secondary" disabled={uploading} onClick={() => setUploadOpen(false)}>Huỷ</button><button className="primary" disabled={uploading}>{uploading ? <><span className="spinner"/>Đang đọc & phân tích...</> : <>✦ Phân tích CV</>}</button></div>
      </form>
    </div>}

    {createJobOpen && <div className="modal-backdrop" onMouseDown={e => e.target === e.currentTarget && !creatingJob && setCreateJobOpen(false)}>
      <form className="modal create-job-modal" onSubmit={createJob}>
        <button type="button" className="modal-close" disabled={creatingJob} onClick={() => setCreateJobOpen(false)}>×</button>
        <p className="eyebrow">JOB SETUP</p>
        <h2>Tạo vị trí tuyển dụng</h2>
        <p>JD là nguồn chuẩn để AI đối chiếu CV. Viết rõ yêu cầu bắt buộc, mức kinh nghiệm và tiêu chí dự án.</p>
        <div className="upload-fields">
          <label>Chức danh<input name="title" required minLength="2" placeholder="VD: Senior Backend Developer"/></label>
          <label>Mã Job<input name="code" placeholder="VD: ENG-052"/></label>
          <label className="full-field">Phòng ban<input name="department" required placeholder="VD: Engineering · Platform"/></label>
          <label className="full-field">Job Description<textarea name="description" rows="8" required minLength="20" placeholder={'Mô tả trách nhiệm và yêu cầu...\n\nBắt buộc:\n- Python, FastAPI\n- PostgreSQL, Docker\n- 3+ năm kinh nghiệm\n\nƯu tiên:\n- Kubernetes, system design'}/></label>
        </div>
        {createJobError && <div className="upload-error">{createJobError}</div>}
        <div className="upload-security"><Icon name="shield"/><span>JD được dùng làm nguồn đánh giá; AI không sử dụng thuộc tính nhạy cảm để chấm điểm.</span></div>
        <div className="modal-actions"><button type="button" className="secondary" disabled={creatingJob} onClick={() => setCreateJobOpen(false)}>Huỷ</button><button className="primary" disabled={creatingJob}>{creatingJob ? <><span className="spinner"/>Đang tạo...</> : <>＋ Tạo Job & thêm CV</>}</button></div>
      </form>
    </div>}
  </div>
}

function WorkspaceState({ title, text, action, onAction }) {
  return <div className="workspace-state"><span className="workspace-state-mark">T</span><h2>{title}</h2><p>{text}</p>{action && <button className="primary" onClick={onAction}>{action}</button>}</div>
}

function PipelineView({ jobs, candidates, onCreateJob, onUpload, onOpenCandidate }) {
  const departments = ['Tất cả phòng ban', ...new Set(jobs.map(job => job.department))]
  const [department, setDepartment] = useState('Tất cả phòng ban')
  const [selectedJobId, setSelectedJobId] = useState('all')
  const [query, setQuery] = useState('')
  const visibleJobs = jobs.filter(job => department === 'Tất cả phòng ban' || job.department === department)
  const visibleCandidates = candidates
    .filter(item => selectedJobId === 'all' ? visibleJobs.some(job => job.id === item.jobId) : item.jobId === selectedJobId)
    .filter(item => `${item.name} ${item.role}`.toLowerCase().includes(query.toLowerCase()))
    .sort((a, b) => b.score - a.score)
  const selectedJob = jobs.find(job => job.id === selectedJobId)

  return <div className="workspace pipeline-page">
    <section className="page-heading">
      <div><p className="eyebrow">RECRUITING PIPELINE</p><h1>Phòng ban & Job đang tuyển</h1><p>Xem nhanh ứng viên theo từng vị trí, so sánh độ khớp trước khi đi vào đánh giá chi tiết.</p></div>
      <button className="run-button" onClick={onCreateJob}>＋ Tạo Job mới</button>
    </section>

    <div className="pipeline-metrics">
      <article><span>{jobs.length}</span><div><b>Job đang tuyển</b><small>Trên {departments.length - 1} phòng ban</small></div></article>
      <article><span>{candidates.length}</span><div><b>Ứng viên đã sàng lọc</b><small>{candidates.filter(item => item.score >= 80).length} hồ sơ phù hợp cao</small></div></article>
      <article><span>{Math.round(candidates.reduce((sum, item) => sum + item.score, 0) / Math.max(1, candidates.length))}</span><div><b>Điểm khớp trung bình</b><small>Trên thang điểm 100</small></div></article>
    </div>

    <section className="department-section">
      <div className="section-heading"><div><p className="eyebrow">DEPARTMENTS</p><h2>Chọn phòng ban</h2></div><span>{visibleJobs.length} Job đang mở</span></div>
      <div className="department-tabs">{departments.map(item => <button key={item} className={department === item ? 'active' : ''} onClick={() => { setDepartment(item); setSelectedJobId('all') }}>{item}<span>{item === 'Tất cả phòng ban' ? jobs.length : jobs.filter(job => job.department === item).length}</span></button>)}</div>
      <div className="pipeline-job-grid">
        {visibleJobs.map(job => {
          const jobCandidates = candidates.filter(item => item.jobId === job.id)
          const average = jobCandidates.length ? Math.round(jobCandidates.reduce((sum, item) => sum + item.score, 0) / jobCandidates.length) : 0
          return <article key={job.id} className={selectedJobId === job.id ? 'active' : ''} onClick={() => setSelectedJobId(job.id)}>
            <div className="job-card-top"><span>{job.code}</span><i>● Đang tuyển</i></div>
            <h3>{job.title}</h3><p>{job.department}</p>
            <div className="job-card-stats"><div><b>{jobCandidates.length}</b><small>Ứng viên</small></div><div><b>{average || '—'}</b><small>Điểm TB</small></div><div><b>{jobCandidates.filter(item => item.score >= 80).length}</b><small>Khớp cao</small></div></div>
            <button onClick={event => { event.stopPropagation(); onUpload(job.id) }}>＋ Thêm CV</button>
          </article>
        })}
      </div>
    </section>

    <section className="candidate-pipeline-card">
      <div className="candidate-pipeline-head">
        <div><p className="eyebrow">CANDIDATE MATCHING</p><h2>{selectedJob ? selectedJob.title : department === 'Tất cả phòng ban' ? 'Tất cả ứng viên' : department}</h2><p>{visibleCandidates.length} ứng viên · Sắp xếp theo điểm phù hợp cao nhất</p></div>
        <div className="pipeline-search"><span>⌕</span><input value={query} onChange={event => setQuery(event.target.value)} placeholder="Tìm ứng viên..."/></div>
      </div>
      <div className="pipeline-table-wrap"><table className="pipeline-table">
        <thead><tr><th>ỨNG VIÊN</th><th>JOB ỨNG TUYỂN</th><th>MATCH SCORE</th><th>CONFIDENCE</th><th>TRẠNG THÁI HR</th><th></th></tr></thead>
        <tbody>{visibleCandidates.map(item => {
          const job = jobs.find(entry => entry.id === item.jobId)
          const saved = item.hrDecision
          return <tr key={item.id} onClick={() => onOpenCandidate(item, job)}>
            <td><div className="pipeline-person"><span>{item.initials}</span><div><b>{item.name}</b><small>{item.role}</small></div></div></td>
            <td><b className="job-name">{job?.title}</b><small className="job-code">{job?.code}</small></td>
            <td><div className="quick-score"><strong className={item.score >= 80 ? 'high' : item.score >= 70 ? 'medium' : 'low'}>{item.score}</strong><i><em style={{ width: `${item.score}%` }}/></i></div></td>
            <td><span className="confidence-chip">{item.confidence}%</span></td>
            <td><span className={`decision-chip ${saved === 'Pass' ? 'advance' : saved ? 'hold' : 'pending'}`}>{saved ? saved === 'Pass' ? 'Đề xuất vòng tiếp' : saved === 'Reject' ? 'Không đề xuất' : 'Cần xem thêm' : 'Chờ HR xem'}</span></td>
            <td><button className="detail-link">Xem chi tiết →</button></td>
          </tr>
        })}</tbody>
      </table></div>
      {!visibleCandidates.length && <div className="pipeline-empty"><span>○</span><h3>Chưa có ứng viên</h3><p>Upload CV đầu tiên để bắt đầu sàng lọc cho vị trí này.</p>{selectedJob && <button className="primary" onClick={() => onUpload(selectedJob.id)}>↑ Upload CV</button>}</div>}
    </section>
  </div>
}

function AuditView({ audit }) {
  return <div className="workspace audit-page">
    <section className="page-heading"><div><p className="eyebrow">AUDIT & GOVERNANCE</p><h1>Nhật ký đánh giá</h1><p>Theo dõi toàn bộ chuỗi AI đề xuất → HR quyết định → HR override.</p></div><button className="export-button" onClick={() => window.print()}>↓ Xuất báo cáo</button></section>
    <div className="audit-stats"><article><span>24</span><p>Hồ sơ đã phân tích</p></article><article><span>7</span><p>Quyết định của HR</p></article><article><span>2</span><p>Lần HR override</p></article><article><span>100%</span><p>Đánh giá có bằng chứng</p></article></div>
    <section className="audit-card">
      <div className="audit-card-head"><div><h2>Lịch sử hoạt động</h2><p>Dữ liệu được ghi lại tự động và không thể chỉnh sửa.</p></div><span>● Live</span></div>
      <div className="audit-table">
        <div className="audit-row audit-head"><span>THỜI GIAN</span><span>NGƯỜI THỰC HIỆN</span><span>HOẠT ĐỘNG</span><span>CHI TIẾT</span></div>
        {audit.map(item => <div className="audit-row" key={item.id}><span>{item.time}</span><span><i>{item.actor.startsWith('Talent') ? 'AI' : item.actor.startsWith('Hệ') ? 'HT' : 'MA'}</i>{item.actor}</span><b>{item.action}</b><span>{item.detail}</span></div>)}
      </div>
    </section>
  </div>
}

export default App
