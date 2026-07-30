import { useEffect, useEffectEvent, useState } from 'react'
import './App.css'

const API_URL = import.meta.env.VITE_API_URL || '/api'
const DECISIONS = ['Pass', 'Hold', 'Reject']

async function request(path, { token, ...options } = {}) {
  const response = await fetch(`${API_URL}${path}`, {
    ...options,
    headers: { 'Content-Type': 'application/json', ...(token ? { Authorization: `Bearer ${token}` } : {}), ...options.headers },
  })
  const payload = await response.json().catch(() => ({}))
  if (!response.ok) throw new Error(payload.detail || 'Không thể kết nối đến máy chủ.')
  return payload
}

function formatDate(value) {
  return new Intl.DateTimeFormat('vi-VN', { dateStyle: 'medium', timeStyle: 'short' }).format(new Date(value))
}

function Assessment({ assessment }) {
  if (!assessment) return null
  return <div className="assessment">
    <p className="assessment-summary">{assessment.summary}</p>
    <div className="assessment-grid">
      <section><h4>Điểm phù hợp</h4><ul>{assessment.strengths.map((item) => <li key={item}>{item}</li>)}</ul></section>
      <section><h4>Cần xác minh</h4><ul>{assessment.gaps.map((item) => <li key={item}>{item}</li>)}</ul></section>
    </div>
    <section><h4>Câu hỏi phỏng vấn gợi ý</h4><ol>{assessment.interview_questions.map((item) => <li key={item}>{item}</li>)}</ol></section>
  </div>
}

function Login({ onLogin }) {
  const [email, setEmail] = useState('demo@vairecruiter.local')
  const [password, setPassword] = useState('Demo@123')
  const [error, setError] = useState('')
  const [pending, setPending] = useState(false)
  async function submit(event) {
    event.preventDefault(); setPending(true); setError('')
    try { onLogin(await request('/auth/login', { method: 'POST', body: JSON.stringify({ email, password }) })) } catch (loginError) { setError(loginError.message) } finally { setPending(false) }
  }
  return <main className="login-page"><section className="login-intro"><p className="eyebrow">V-AI RECRUITER</p><h1>Tuyển đúng người.<br />Rõ từng quyết định.</h1><p>Không gian làm việc tập trung để tạo vị trí, đánh giá CV và lưu lại quyết định của đội tuyển dụng.</p><div className="principles"><span>Đánh giá có căn cứ</span><span>Quyết định do con người</span><span>Audit minh bạch</span></div></section><form className="login-form" onSubmit={submit}><p className="eyebrow">ĐĂNG NHẬP WORKSPACE</p><h2>Chào mừng trở lại</h2><label>Email<input type="email" value={email} onChange={(event) => setEmail(event.target.value)} required /></label><label>Mật khẩu<input type="password" value={password} onChange={(event) => setPassword(event.target.value)} required /></label>{error && <p className="form-error" role="alert">{error}</p>}<button className="button primary" disabled={pending}>{pending ? 'Đang đăng nhập...' : 'Vào workspace'}</button><p className="hint">Tài khoản demo đã được điền sẵn.</p></form></main>
}

function App() {
  const [session, setSession] = useState(() => JSON.parse(localStorage.getItem('vai-session') || 'null'))
  const [tab, setTab] = useState('overview')
  const [data, setData] = useState({ jobs: [], candidates: [], dashboard: null, analytics: null, audit: [] })
  const [loading, setLoading] = useState(Boolean(session))
  const [error, setError] = useState('')
  const [notice, setNotice] = useState('')
  const [selectedCandidate, setSelectedCandidate] = useState(null)
  async function refresh() {
    if (!session) return
    setLoading(true); setError('')
    try {
      const [dashboard, jobs, candidates, analytics, audit] = await Promise.all(['/dashboard', '/jobs', '/candidates', '/analytics', '/audit'].map((path) => request(path, { token: session.access_token })))
      setData({ dashboard, jobs, candidates, analytics, audit })
    } catch (loadError) { setError(loadError.message) } finally { setLoading(false) }
  }
  const loadWorkspace = useEffectEvent(() => { void refresh() })
  useEffect(() => { loadWorkspace() }, [session])
  function login(nextSession) { localStorage.setItem('vai-session', JSON.stringify(nextSession)); setSession(nextSession) }
  function logout() { localStorage.removeItem('vai-session'); setSession(null); setData({ jobs: [], candidates: [], dashboard: null, analytics: null, audit: [] }) }
  async function createJob(event) {
    event.preventDefault()
    const form = event.currentTarget
    const formData = new FormData(form)
    try {
      await request('/jobs', { token: session.access_token, method: 'POST', body: JSON.stringify({ title: formData.get('title'), description: formData.get('description') }) })
      form.reset()
      setNotice('Đã tạo job mới.')
      await refresh()
    } catch (actionError) {
      setError(actionError.message)
    }
  }
  async function screenCandidate(event) {
    event.preventDefault()
    const form = event.currentTarget
    const formData = new FormData(form)
    try {
      const candidate = await request('/candidates', { token: session.access_token, method: 'POST', body: JSON.stringify({ job_id: formData.get('job_id'), name: formData.get('name'), cv_text: formData.get('cv_text') }) })
      form.reset()
      setSelectedCandidate(candidate)
      setNotice('Đã chấm CV và lưu kết quả.')
      await refresh()
    } catch (actionError) {
      setError(actionError.message)
    }
  }
  async function saveDecision(event) {
    event.preventDefault(); const form = new FormData(event.currentTarget)
    try { await request(`/candidates/${form.get('candidate_id')}/decision`, { token: session.access_token, method: 'PUT', body: JSON.stringify({ decision: form.get('decision'), note: form.get('note') }) }); setNotice('Đã lưu quyết định tuyển dụng.'); await refresh() } catch (actionError) { setError(actionError.message) }
  }
  if (!session) return <Login onLogin={login} />
  const metrics = data.dashboard?.metrics
  const activeCandidate = selectedCandidate || data.candidates[0]
  const tabs = [['overview', 'Tổng quan'], ['jobs', 'Job'], ['screen', 'Sàng lọc'], ['decisions', 'Quyết định'], ['audit', 'Phân tích']]
  return <div className="app-shell"><header className="topbar"><div className="brand"><img src="/logo.png" alt="V-AI Recruiter logo" className="brand-logo" /><div><strong>V-AI Recruiter</strong><small>Talent screening workspace</small></div></div><div className="account"><span>{session.user.name}</span><button className="text-button" onClick={logout}>Đăng xuất</button></div></header><nav className="nav" aria-label="Điều hướng workspace">{tabs.map(([id, label]) => <button key={id} className={tab === id ? 'active' : ''} onClick={() => setTab(id)}>{label}</button>)}</nav><main className="workspace">{notice && <div className="notice">{notice}<button onClick={() => setNotice('')} aria-label="Đóng thông báo">x</button></div>}{error && <div className="form-error banner">{error}<button onClick={() => setError('')} aria-label="Đóng lỗi">x</button></div>}{loading ? <p className="loading">Đang đồng bộ workspace...</p> : <>
    {tab === 'overview' && <section><div className="page-heading"><div><p className="eyebrow">TỔNG QUAN</p><h1>Ngày làm việc của {session.user.name.split(' ').at(-1)}</h1></div><button className="button primary" onClick={() => setTab('jobs')}>Tạo job mới</button></div><div className="metrics"><article><span>Job đang mở</span><strong>{metrics?.open_jobs || 0}</strong></article><article><span>CV đã chấm</span><strong>{metrics?.screened_candidates || 0}</strong></article><article><span>Đã Pass</span><strong>{metrics?.decisions?.Pass || 0}</strong></article><article><span>Đang Hold</span><strong>{metrics?.decisions?.Hold || 0}</strong></article></div><section className="panel"><div className="panel-header"><h2>Ứng viên mới nhất</h2><button className="text-button" onClick={() => setTab('decisions')}>Xem quyết định</button></div>{data.candidates.length ? <div className="candidate-list">{data.candidates.slice(0, 5).map((candidate) => <button className="candidate-row" key={candidate.id} onClick={() => { setSelectedCandidate(candidate); setTab('decisions') }}><div><strong>{candidate.name}</strong><span>{candidate.job_title}</span></div><b>{candidate.score.toFixed(3)}</b><em className={candidate.decision ? candidate.decision.toLowerCase() : ''}>{candidate.decision || 'Chưa quyết định'}</em></button>)}</div> : <p className="empty">Chưa có ứng viên. Hãy tạo job và chấm CV đầu tiên.</p>}</section></section>}
    {tab === 'jobs' && <section className="two-column"><form className="panel form-panel" onSubmit={createJob}><p className="eyebrow">01 / JOB MỚI</p><h1>Tạo vị trí tuyển dụng</h1><label>Tên vị trí<input name="title" placeholder="Backend Developer (Python)" required /></label><label>Mô tả công việc<textarea name="description" rows="11" placeholder="Nêu rõ kỹ năng, kinh nghiệm và trách nhiệm của vị trí..." required /></label><button className="button primary">Tạo job</button></form><section className="panel"><div className="panel-header"><h2>Job đang mở</h2><span className="count">{data.jobs.length}</span></div>{data.jobs.length ? <div className="job-list">{data.jobs.map((job) => <article key={job.id}><div><h3>{job.title}</h3><p>{job.description}</p></div><footer><span>{job.candidate_count} ứng viên</span><time>{formatDate(job.created_at)}</time></footer></article>)}</div> : <p className="empty">Chưa có job nào.</p>}</section></section>}
    {tab === 'screen' && <section className="two-column"><form className="panel form-panel" onSubmit={screenCandidate}><p className="eyebrow">02 / SÀNG LỌC</p><h1>Đánh giá một hồ sơ</h1>{data.jobs.length ? <><label>Job<select name="job_id" required>{data.jobs.map((job) => <option key={job.id} value={job.id}>{job.title}</option>)}</select></label><label>Tên ứng viên<input name="name" placeholder="Nguyen Van A" required /></label><label>Nội dung CV<textarea name="cv_text" rows="10" placeholder="Dán nội dung CV dạng văn bản..." required /></label><button className="button primary">Chấm điểm CV</button></> : <p className="empty">Hãy tạo một job trước khi sàng lọc CV.</p>}</form><section className="panel result-panel"><p className="eyebrow">KẾT QUẢ GẦN NHẤT</p>{activeCandidate ? <><div className="candidate-title"><div><h2>{activeCandidate.name}</h2><p>{activeCandidate.job_title}</p></div><strong className="score">{activeCandidate.score.toFixed(3)}</strong></div><Assessment assessment={activeCandidate.assessment} /></> : <p className="empty">Kết quả đánh giá sẽ xuất hiện tại đây.</p>}</section></section>}
    {tab === 'decisions' && <section className="two-column decision-layout"><section className="panel"><div className="panel-header"><h2>Ứng viên đã chấm</h2><span className="count">{data.candidates.length}</span></div>{data.candidates.length ? <div className="candidate-list">{data.candidates.map((candidate) => <button className={`candidate-row ${activeCandidate?.id === candidate.id ? 'selected' : ''}`} key={candidate.id} onClick={() => setSelectedCandidate(candidate)}><div><strong>{candidate.name}</strong><span>{candidate.job_title}</span></div><b>{candidate.score.toFixed(3)}</b><em className={candidate.decision ? candidate.decision.toLowerCase() : ''}>{candidate.decision || 'Mới'}</em></button>)}</div> : <p className="empty">Chưa có ứng viên để quyết định.</p>}</section><section className="panel result-panel">{activeCandidate ? <><div className="candidate-title"><div><p className="eyebrow">03 / QUYẾT ĐỊNH</p><h2>{activeCandidate.name}</h2><p>{activeCandidate.job_title}</p></div><strong className="score">{activeCandidate.score.toFixed(3)}</strong></div><Assessment assessment={activeCandidate.assessment} /><form className="decision-form" key={activeCandidate.id} onSubmit={saveDecision}><input type="hidden" name="candidate_id" value={activeCandidate.id} /><fieldset><legend>Quyết định của HR</legend>{DECISIONS.map((decision) => <label className="choice" key={decision}><input type="radio" name="decision" value={decision} defaultChecked={(activeCandidate.decision || 'Pass') === decision} />{decision}</label>)}</fieldset><label>Ghi chú<textarea name="note" rows="3" defaultValue={activeCandidate.note || ''} placeholder="Bối cảnh hoặc việc cần theo dõi..." /></label><button className="button primary">Lưu quyết định</button></form></> : <p className="empty">Chọn ứng viên để xem xét.</p>}</section></section>}
    {tab === 'audit' && <section><div className="page-heading"><div><p className="eyebrow">04 / PHÂN TÍCH</p><h1>Dữ liệu và kiểm toán</h1></div></div><div className="metrics">{[['Ứng viên đã chấm', data.analytics?.candidate_count], ['Điểm trung bình', data.analytics?.average_score?.toFixed(3) || '-'], ['Điểm cao nhất', data.analytics?.highest_score?.toFixed(3) || '-'], ['Điểm thấp nhất', data.analytics?.lowest_score?.toFixed(3) || '-']].map(([label, value]) => <article key={label}><span>{label}</span><strong>{value}</strong></article>)}</div><section className="panel audit-panel"><div className="panel-header"><h2>Nhật ký kiểm toán</h2><p>100 thao tác gần nhất</p></div>{data.audit.length ? <div className="audit-list">{data.audit.map((item) => <article key={item.id}><span>{item.action.replaceAll('_', ' ')}</span><p>{item.detail}</p><time>{formatDate(item.created_at)}</time></article>)}</div> : <p className="empty">Chưa có thao tác nào được ghi lại.</p>}</section></section>}
  </>}</main></div>
}

export default App