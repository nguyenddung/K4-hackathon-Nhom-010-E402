import { useState } from 'react'

export default function PipelineView({ jobs, candidates, onCreateJob, onUpload, onOpenCandidate }) {
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
  const decisions = JSON.parse(localStorage.getItem('talentscreen-decisions') || '{}')

  return <div className="max-w-auto m-auto p-[40px_34px_55px] max-[650px]:p-[28px_16px_40px]">
    <section className="flex justify-between items-end gap-[20px] mb-[25px] max-[650px]:items-start">
      <div>
        <p className="text-xs uppercase tracking-widest text-slate-500 m-[0_0_8px]">RECRUITING PIPELINE</p>
        <h1 className="font-serif text-3xl font-semibold tracking-tight leading-tight m-[0_0_7px]">Phòng ban & Job đang tuyển</h1>
        <p className="text-sm text-slate-700 leading-6 m-0">Xem nhanh ứng viên theo từng vị trí, so sánh độ khớp trước khi đi vào đánh giá chi tiết.</p>
      </div>
      <button className="border-0 rounded-[6px] bg-forest text-white p-[11px_15px] text-sm font-medium shadow-[0_1px_2px_#123d3525] flex items-center gap-[8px]" onClick={onCreateJob}>＋ Tạo Job mới</button>
    </section>

    <div className="grid grid-cols-3 max-[650px]:grid-cols-1 gap-[12px] mb-[18px]">
      <article className="flex items-center gap-[14px] border border-line rounded-[7px] bg-paper p-[17px_18px]">
        <span className="min-w-[48px] text-forest font-serif text-3xl font-bold">{jobs.length}</span>
        <div className="grid gap-[4px] pl-[14px] border-l border-line"><b className="text-sm font-medium">Job đang tuyển</b><small className="text-xs text-slate-500">Trên {departments.length - 1} phòng ban</small></div>
      </article>
      <article className="flex items-center gap-[14px] border border-line rounded-[7px] bg-paper p-[17px_18px]">
        <span className="min-w-[48px] text-forest font-serif text-3xl font-bold">{candidates.length}</span>
        <div className="grid gap-[4px] pl-[14px] border-l border-line"><b className="text-sm font-medium">Ứng viên đã sàng lọc</b><small className="text-xs text-slate-500">{candidates.filter(item => item.score >= 80).length} hồ sơ phù hợp cao</small></div>
      </article>
      <article className="flex items-center gap-[14px] border border-line rounded-[7px] bg-paper p-[17px_18px]">
        <span className="min-w-[48px] text-forest font-serif text-3xl font-bold">{Math.round(candidates.reduce((sum, item) => sum + item.score, 0) / Math.max(1, candidates.length))}</span>
        <div className="grid gap-[4px] pl-[14px] border-l border-line"><b className="text-sm font-medium">Điểm khớp trung bình</b><small className="text-xs text-slate-500">Trên thang điểm 100</small></div>
      </article>
    </div>

    <section className="border border-line rounded-[8px] bg-paper shadow-[0_4px_18px_#24342d08] p-[20px]">
      <div className="flex items-center justify-between">
        <div><p className="text-xs uppercase tracking-widest text-slate-500 m-[0_0_8px]">DEPARTMENTS</p><h2 className="m-0 font-serif text-2xl font-semibold">Chọn phòng ban</h2></div>
        <span className="text-[#577169] bg-[#e8f0eb] p-[5px_8px] rounded-[12px] text-xs font-medium">{visibleJobs.length} Job đang mở</span>
      </div>
      <div className="flex gap-[7px] my-[15px] overflow-auto">
        {departments.map(item => (
          <button key={item} className={`border border-[#d3d7d2] rounded-[18px] p-[7px_10px] bg-white whitespace-nowrap text-sm font-medium ${department === item ? '!bg-forest !border-forest !text-white' : 'text-[#6b7571]'}`} onClick={() => { setDepartment(item); setSelectedJobId('all') }}>
            {item}<span className="ml-[6px] opacity-65">{item === 'Tất cả phòng ban' ? jobs.length : jobs.filter(job => job.department === item).length}</span>
          </button>
        ))}
      </div>
      <div className="grid grid-cols-3 gap-[10px] max-[960px]:grid-cols-2 max-[650px]:grid-cols-1">
        {visibleJobs.map(job => {
          const jobCandidates = candidates.filter(item => item.jobId === job.id)
          const average = jobCandidates.length ? Math.round(jobCandidates.reduce((sum, item) => sum + item.score, 0) / jobCandidates.length) : 0
          return <article key={job.id} className={`border border-line rounded-[7px] p-[14px] cursor-pointer transition-[.18s] hover:border-[#76988d] hover:shadow-[0_5px_15px_#163e3410] hover:-translate-y-[1px] ${selectedJobId === job.id ? '!border-[#76988d] !shadow-[0_5px_15px_#163e3410] !-translate-y-[1px]' : ''}`} onClick={() => setSelectedJobId(job.id)}>
            <div className="flex justify-between items-center"><span className="text-slate-500 font-mono font-semibold text-xs">{job.code}</span><i className="text-[#3d805d] text-xs font-medium not-italic">● Đang tuyển</i></div>
            <h3 className="m-[13px_0_4px] font-serif text-xl font-semibold">{job.title}</h3><p className="m-0 text-slate-500 text-sm">{job.department}</p>
            <div className="grid grid-cols-3 m-[14px_0_12px] p-[11px_0] border-y border-line">
              <div className="grid gap-[3px] text-center border-r border-line"><b className="font-mono text-sm font-semibold text-forest">{jobCandidates.length}</b><small className="text-slate-500 text-sm">Ứng viên</small></div>
              <div className="grid gap-[3px] text-center border-r border-line"><b className="font-mono text-sm font-semibold text-forest">{average || '—'}</b><small className="text-slate-500 text-sm">Điểm TB</small></div>
              <div className="grid gap-[3px] text-center"><b className="font-mono text-sm font-semibold text-forest">{jobCandidates.filter(item => item.score >= 80).length}</b><small className="text-slate-500 text-sm">Khớp cao</small></div>
            </div>
            <button className="w-full border-0 bg-transparent text-forest text-sm font-medium" onClick={event => { event.stopPropagation(); onUpload(job.id) }}>＋ Thêm CV</button>
          </article>
        })}
      </div>
    </section>

    <section className="border border-line rounded-[8px] bg-paper shadow-[0_4px_18px_#24342d08] mt-[16px] overflow-hidden">
      <div className="flex items-center justify-between p-[19px_20px] max-[650px]:items-start max-[650px]:flex-col max-[650px]:gap-[12px]">
        <div>
          <p className="text-xs uppercase tracking-widest text-slate-500 m-[0_0_8px]">CANDIDATE MATCHING</p>
          <h2 className="m-0 font-serif text-2xl font-semibold">{selectedJob ? selectedJob.title : department === 'Tất cả phòng ban' ? 'Tất cả ứng viên' : department}</h2>
          <p className="text-xs text-slate-500 m-[5px_0_0]">{visibleCandidates.length} ứng viên · Sắp xếp theo điểm phù hợp cao nhất</p>
        </div>
        <div className="flex items-center gap-[7px] border border-[#cfd4ce] rounded-[6px] p-[0_9px] text-slate-500 w-[210px] max-[650px]:w-full">
          <span>⌕</span>
          <input className="w-full border-0 outline-0 bg-transparent h-[35px] text-sm placeholder:text-slate-400" value={query} onChange={event => setQuery(event.target.value)} placeholder="Tìm ứng viên..." />
        </div>
      </div>
      <div className="overflow-auto"><table className="min-w-[850px] w-full text-left border-collapse">
        <thead><tr className="border-b border-line">
          <th className="p-[10px_18px] text-xs uppercase tracking-wide font-semibold text-slate-500">ỨNG VIÊN</th>
          <th className="p-[10px_18px] text-xs uppercase tracking-wide font-semibold text-slate-500">JOB ỨNG TUYỂN</th>
          <th className="p-[10px_18px] text-xs uppercase tracking-wide font-semibold text-slate-500">MATCH SCORE</th>
          <th className="p-[10px_18px] text-xs uppercase tracking-wide font-semibold text-slate-500">CONFIDENCE</th>
          <th className="p-[10px_18px] text-xs uppercase tracking-wide font-semibold text-slate-500">TRẠNG THÁI HR</th>
          <th className="p-[10px_18px]"></th>
        </tr></thead>
        <tbody>{visibleCandidates.map(item => {
          const job = jobs.find(entry => entry.id === item.jobId)
          const saved = decisions[item.id]
          return <tr key={item.id} className="cursor-pointer hover:bg-[#fafaf7] transition-[.1s] border-b border-line last:border-0" onClick={() => onOpenCandidate(item, job)}>
            <td className="p-[12px_18px]">
              <div className="flex items-center gap-[9px]">
                <span className="w-[31px] h-[31px] flex-none rounded-full grid place-items-center bg-[#dce9e2] text-forest text-xs font-bold">{item.initials}</span>
                <div className="grid gap-[3px]"><b className="text-[#35413d] text-sm font-semibold">{item.name}</b><small className="block text-slate-500 text-sm">{item.role}</small></div>
              </div>
            </td>
            <td className="p-[12px_18px]"><b className="text-[#35413d] text-sm font-semibold">{job?.title}</b><small className="block text-slate-500 text-sm mt-[3px]">{job?.code}</small></td>
            <td className="p-[12px_18px]">
              <div className="flex items-center gap-[8px]">
                <strong className={`w-[32px] h-[32px] grid place-items-center rounded-full font-mono text-xs font-bold ${item.score >= 80 ? 'text-[#246746] bg-[#dff0e6]' : item.score >= 70 ? 'text-[#8e5f1f] bg-[#f4ead7]' : 'text-[#9b4038] bg-[#f5e3df]'}`}>{item.score}</strong>
                <i className="w-[52px] h-[4px] rounded-[4px] overflow-hidden bg-[#e3e6e1]"><em className="block h-full bg-forest" style={{ width: `${item.score}%` }} /></i>
              </div>
            </td>
            <td className="p-[12px_18px]"><span className="rounded-[12px] p-[5px_7px] text-xs font-medium whitespace-nowrap bg-[#edf0ec] text-[#59645f]">{item.confidence}%</span></td>
            <td className="p-[12px_18px]">
              <span className={`rounded-[12px] p-[5px_7px] text-xs font-medium whitespace-nowrap ${saved ? saved.type === 'advance' ? 'bg-[#e1f0e7] text-[#2e7150]' : 'bg-[#f5e6dd] text-[#986044]' : 'bg-[#eff0ed] text-[#747d79]'}`}>
                {saved ? saved.type === 'advance' ? 'Đề xuất vòng tiếp' : 'Chưa đề xuất' : 'Chờ HR xem'}
              </span>
            </td>
            <td className="p-[12px_18px] text-right"><button className="border-0 bg-transparent text-forest whitespace-nowrap text-sm font-medium">Xem chi tiết →</button></td>
          </tr>
        })}</tbody>
      </table></div>
      {!visibleCandidates.length && <div className="p-[45px_20px] grid place-items-center text-center border-t border-line">
        <span className="text-3xl text-slate-400">○</span>
        <h3 className="m-[8px_0_4px] font-serif text-lg font-semibold">Chưa có ứng viên</h3>
        <p className="text-sm text-slate-500 m-[0_0_13px]">Upload CV đầu tiên để bắt đầu sàng lọc cho vị trí này.</p>
        {selectedJob && <button className="border-0 rounded-[6px] bg-forest text-white p-[11px_15px] text-sm font-medium shadow-[0_1px_2px_#123d3525]" onClick={() => onUpload(selectedJob.id)}>↑ Upload CV</button>}
      </div>}
    </section>
  </div>
}
