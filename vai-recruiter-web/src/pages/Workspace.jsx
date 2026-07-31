import { useMemo, useState } from 'react'
import { seedJobs, seedCandidates, initialAudit, backendJd } from '../data/mockData'
import { candidateFromApi } from '../utils/candidate'
import Sidebar from '../components/layout/Sidebar'
import Topbar from '../components/layout/Topbar'
import UploadModal from '../components/modals/UploadModal'
import CreateJobModal from '../components/modals/CreateJobModal'
import DecisionModal from '../components/modals/DecisionModal'
import PipelineView from './PipelineView'
import ScreeningView from './ScreeningView'
import AuditView from './AuditView'

export default function Workspace({ session, onLogout }) {
  const [view, setView] = useState('pipeline')
  const [jobList, setJobList] = useState(seedJobs)
  const [jobId, setJobId] = useState(seedJobs[0].id)
  const [candidateList, setCandidateList] = useState(seedCandidates)
  const available = useMemo(() => candidateList.filter(item => item.jobId === jobId), [candidateList, jobId])
  const [candidateId, setCandidateId] = useState(seedCandidates[0].id)
  const candidate = available.find(item => item.id === candidateId) || available[0]
  const [tab, setTab] = useState('overview')
  const [isRunning, setIsRunning] = useState(false)
  const [fresh, setFresh] = useState(false)
  const [decision, setDecision] = useState(() => (JSON.parse(localStorage.getItem('talentscreen-decisions') || '{}'))[seedCandidates[0].id] || null)
  const [audit, setAudit] = useState(() => JSON.parse(localStorage.getItem('talentscreen-audit') || 'null') || initialAudit)
  const [dialog, setDialog] = useState(null)
  const [override, setOverride] = useState(false)
  const [overrideScore, setOverrideScore] = useState(candidate?.score || 0)
  const [toast, setToast] = useState('')
  const [uploadOpen, setUploadOpen] = useState(false)
  const [uploadJobId, setUploadJobId] = useState(seedJobs[0].id)
  const [uploading, setUploading] = useState(false)
  const [uploadError, setUploadError] = useState('')
  const [createJobOpen, setCreateJobOpen] = useState(false)
  const [creatingJob, setCreatingJob] = useState(false)
  const [createJobError, setCreateJobError] = useState('')
  const [dragActive, setDragActive] = useState(false)
  const [selectedFile, setSelectedFile] = useState(null)

  const selectCandidate = id => {
    setCandidateId(id)
    setTab('overview')
    setFresh(false)
    setOverride(false)
    const next = candidateList.find(item => item.id === id)
    setOverrideScore(next?.score || 0)
    const saved = JSON.parse(localStorage.getItem('talentscreen-decisions') || '{}')
    setDecision(saved[id] || null)
  }

  const handleDrag = e => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true)
    } else if (e.type === 'dragleave') {
      setDragActive(false)
    }
  }

  const handleDrop = e => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0]
      const extension = file.name.split('.').pop()?.toLowerCase()
      if (!['pdf', 'docx'].includes(extension)) return setUploadError('Chỉ hỗ trợ PDF hoặc DOCX.')
      if (file.size > 10 * 1024 * 1024) return setUploadError('CV phải nhỏ hơn 10 MB.')
      setSelectedFile(file)
      setUploadError('')
    }
  }

  const uploadCv = async (event, mode) => {
    event.preventDefault()
    setUploadError('')
    const data = new FormData(event.currentTarget)
    
    let file = null
    let cvText = ''
    
    if (mode === 'file') {
      file = selectedFile || data.get('cv')
      if (!file?.name) return setUploadError('Vui lòng chọn CV.')
      const extension = file.name.split('.').pop()?.toLowerCase()
      if (!['pdf', 'docx'].includes(extension)) return setUploadError('Chỉ hỗ trợ PDF hoặc DOCX.')
      if (file.size > 10 * 1024 * 1024) return setUploadError('CV phải nhỏ hơn 10 MB.')
    } else {
      cvText = data.get('cv_text')
      if (!cvText || cvText.length < 30) return setUploadError('Vui lòng nhập ít nhất 30 ký tự nội dung CV.')
    }

    setUploading(true)
    try {
      const headers = { Authorization: `Bearer ${session.access_token}` }
      const jobsResponse = await fetch('/api/jobs', { headers })
      if (!jobsResponse.ok) throw new Error('Không thể tải danh sách vị trí từ API.')
      const apiJobs = await jobsResponse.json()
      const localJob = jobList.find(item => item.id === data.get('jobId'))
      let apiJob = localJob.apiId ? apiJobs.find(item => item.id === localJob.apiId) : apiJobs.find(item => item.title.toLowerCase() === localJob.title.toLowerCase())
      if (!apiJob) {
        const createResponse = await fetch('/api/jobs', {
          method: 'POST',
          headers: { ...headers, 'Content-Type': 'application/json' },
          body: JSON.stringify({ title: localJob.title, description: localJob.description || backendJd }),
        })
        if (!createResponse.ok) throw new Error('Không thể tạo vị trí trên API.')
        apiJob = await createResponse.json()
      }

      let payload
      let fileName

      if (mode === 'file') {
        const uploadData = new FormData()
        uploadData.append('job_id', apiJob.id)
        uploadData.append('name', data.get('name'))
        if (data.get('email')) uploadData.append('email', data.get('email'))
        uploadData.append('cv', file)
        
        const response = await fetch('/api/candidates/upload', { method: 'POST', headers, body: uploadData })
        payload = await response.json()
        if (!response.ok) throw new Error(payload.detail || 'Không thể phân tích CV.')
        fileName = file.name
      } else {
        const textPayload = {
          job_id: apiJob.id,
          name: data.get('name'),
          cv_text: cvText
        }
        if (data.get('email')) textPayload.email = data.get('email')

        const response = await fetch('/api/candidates', { 
          method: 'POST', 
          headers: { ...headers, 'Content-Type': 'application/json' },
          body: JSON.stringify(textPayload) 
        })
        payload = await response.json()
        if (!response.ok) throw new Error(payload.detail || 'Không thể phân tích CV.')
        fileName = 'Nhập văn bản'
      }

      const newCandidate = candidateFromApi(payload, localJob.id, fileName)
      setCandidateList(items => [newCandidate, ...items])
      setJobId(localJob.id)
      setCandidateId(newCandidate.id)
      setDecision(null)
      setTab('overview')
      setUploadOpen(false)
      setSelectedFile(null)
      const eventItem = { id: Date.now(), time: 'Vừa xong', actor: 'TalentScreen AI', action: 'Upload & phân tích CV', detail: `${newCandidate.name} · ${newCandidate.score}/100 · ${fileName}` }
      const nextAudit = [eventItem, ...audit]
      setAudit(nextAudit)
      localStorage.setItem('talentscreen-audit', JSON.stringify(nextAudit))
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
        body: JSON.stringify({ title: data.get('title'), description: data.get('description') }),
      })
      const payload = await response.json()
      if (!response.ok) throw new Error(payload.detail || 'Không thể tạo Job.')
      const newJob = {
        id: `local-${payload.id}`,
        apiId: payload.id,
        title: payload.title,
        code: data.get('code') || `ENG-${String(jobList.length + 40).padStart(3, '0')}`,
        department: data.get('department'),
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

  const runScreening = () => {
    setIsRunning(true)
    setFresh(false)
    window.setTimeout(() => {
      setIsRunning(false)
      setFresh(true)
      const event = { id: Date.now(), time: 'Vừa xong', actor: 'TalentScreen AI', action: 'Phân tích lại hồ sơ', detail: `${candidate.name} · ${candidate.score}/100 · Grounded on CV + JD` }
      const next = [event, ...audit]
      setAudit(next)
      localStorage.setItem('talentscreen-audit', JSON.stringify(next))
      setToast('Phân tích hoàn tất — mọi kết luận đều có nguồn bằng chứng.')
    }, 900)
  }

  const saveDecision = event => {
    event.preventDefault()
    const data = new FormData(event.currentTarget)
    const chosen = dialog
    const score = override ? Number(overrideScore) : candidate.score
    const savedDecision = { type: chosen, note: data.get('note'), score, overridden: override, at: 'Vừa xong' }
    const all = JSON.parse(localStorage.getItem('talentscreen-decisions') || '{}')
    if (candidate) {
      all[candidate.id] = savedDecision
    }
    localStorage.setItem('talentscreen-decisions', JSON.stringify(all))
    setDecision(savedDecision)
    const label = chosen === 'advance' ? 'Đề xuất vào vòng tiếp' : 'Chưa đề xuất'
    const eventItem = { id: Date.now(), time: 'Vừa xong', actor: 'Mai Anh (HR)', action: label, detail: `${candidate ? candidate.name : ''}${override ? ` · Override ${candidate.score} → ${score}` : ' · Giữ nguyên điểm AI'}` }
    const next = [eventItem, ...audit]
    setAudit(next)
    localStorage.setItem('talentscreen-audit', JSON.stringify(next))
    setDialog(null)
    setToast(`Đã lưu quyết định HR cho ${candidate ? candidate.name : ''}.`)
  }

  return (
    <div className="min-h-screen bg-cream text-ink">
      <Sidebar view={view} setView={setView} session={session} onLogout={onLogout} />

      <main className="ml-[248px] max-[960px]:ml-[74px] max-[650px]:ml-0 min-w-0">
        <Topbar view={view} session={session} />

        {toast && <div className="fixed right-[24px] top-[78px] z-20 p-[12px_14px] border border-[#b9d6c6] rounded-[7px] bg-[#f2fbf6] text-[#255e45] shadow-[0_12px_35px_#20372d22] text-[10px]">{toast}<button className="border-0 bg-transparent text-inherit ml-[18px]" onClick={() => setToast('')}>×</button></div>}

        {view === 'audit' ? (
          <AuditView audit={audit} />
        ) : view === 'pipeline' ? (
          <PipelineView 
            jobs={jobList} 
            candidates={candidateList} 
            onCreateJob={() => { setCreateJobError(''); setCreateJobOpen(true) }} 
            onUpload={selectedJobId => { setUploadJobId(selectedJobId); setUploadError(''); setUploadOpen(true) }} 
            onOpenCandidate={(item, selectedJob) => { setJobId(selectedJob.id); selectCandidate(item.id); setView('screen') }} 
          />
        ) : (
          <ScreeningView 
            jobList={jobList} 
            jobId={jobId} 
            setJobId={setJobId} 
            selectCandidate={selectCandidate} 
            candidateList={candidateList} 
            setUploadJobId={setUploadJobId} 
            setUploadOpen={setUploadOpen} 
            setToast={setToast}
            candidate={candidate} 
            available={available} 
            runScreening={runScreening} 
            isRunning={isRunning} 
            fresh={fresh} 
            setFresh={setFresh} 
            tab={tab} 
            setTab={setTab} 
            decision={decision} 
            setDialog={setDialog} 
            onCreateJob={() => { setCreateJobError(''); setCreateJobOpen(true) }}
          />
        )}
      </main>

      {dialog && <DecisionModal 
        type={dialog} 
        onClose={() => setDialog(null)} 
        onSubmit={saveDecision} 
        candidate={candidate} 
        override={override} 
        setOverride={setOverride} 
        overrideScore={overrideScore} 
        setOverrideScore={setOverrideScore} 
      />}

      {uploadOpen && <UploadModal 
        isOpen={uploadOpen} 
        onClose={() => { setUploadOpen(false); setSelectedFile(null); }} 
        onSubmit={uploadCv} 
        uploading={uploading} 
        uploadError={uploadError} 
        jobList={jobList} 
        uploadJobId={uploadJobId} 
        dragActive={dragActive} 
        handleDrag={handleDrag} 
        handleDrop={handleDrop} 
        selectedFile={selectedFile} 
        setSelectedFile={setSelectedFile} 
      />}

      {createJobOpen && <CreateJobModal 
        isOpen={createJobOpen} 
        onClose={() => setCreateJobOpen(false)} 
        onSubmit={createJob} 
        creatingJob={creatingJob} 
        createJobError={createJobError} 
      />}
    </div>
  )
}
