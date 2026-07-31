import Icon from '../components/Icon'

export default function ScreeningView({
  jobList, jobId, setJobId, selectCandidate, candidateList, setUploadJobId, setUploadOpen, setToast,
  candidate, available, runScreening, isRunning, fresh, setFresh, tab, setTab, decision, setDialog, onCreateJob
}) {
  return (
    <div className="max-w m-auto p-[40px_34px_55px] max-[650px]:p-[28px_16px_40px]">
      <section className="flex justify-between items-end gap-[20px] mb-[25px] max-[650px]:items-start">
        <div>
          <p className="text-xs uppercase tracking-widest text-slate-500 m-[0_0_8px]">AI SCREENING WORKSPACE</p>
          <h1 className="font-serif text-3xl font-semibold tracking-tight leading-tight m-[0_0_7px]">Đánh giá ứng viên</h1>
          <p className="text-sm text-slate-700 leading-6 m-0">Đối chiếu CV với yêu cầu công việc — minh bạch, có bằng chứng và không suy diễn.</p>
        </div>
        <div className="flex gap-[8px] max-[650px]:flex-col">
          <button className="border border-[#c8cec9] rounded-[6px] bg-transparent text-[#4d5b56] p-[10px_14px] text-sm font-medium" onClick={onCreateJob}>＋ Tạo Job</button>
          <button className="border border-[#9ab4a9] rounded-[6px] bg-paper text-forest p-[10px_15px] text-sm font-medium" onClick={() => { setUploadJobId(jobId); setUploadOpen(true) }}>↑ Upload CV</button>
          <button className="border-0 rounded-[6px] bg-forest text-white p-[11px_15px] text-sm font-medium shadow-[0_1px_2px_#123d3525] flex items-center gap-[8px] disabled:opacity-70 disabled:cursor-wait" onClick={runScreening} disabled={isRunning}>
            <span className={isRunning ? 'w-[12px] h-[12px] border-2 border-[#ffffff60] border-t-white rounded-full animate-spin' : 'text-mint'}>{isRunning ? '' : '✦'}</span>
            {isRunning ? 'Đang phân tích...' : 'Phân tích lại'}
          </button>
        </div>
      </section>

      <section className="border border-line rounded-[8px] bg-paper min-h-[91px] p-[15px_18px] grid grid-cols-[1fr_28px_1fr_auto] items-center gap-[14px] shadow-[0_4px_18px_#24342d08] max-[960px]:grid-cols-[1fr_20px_1fr] max-[650px]:grid-cols-1 max-[650px]:gap-[16px]">
        <div className="flex items-start gap-[12px] min-w-0 max-[650px]:pt-[14px] max-[650px]:border-t max-[650px]:border-line max-[650px]:first:border-0 max-[650px]:first:pt-0">
          <span className="w-[22px] h-[22px] flex-none rounded-full grid place-items-center bg-[#e5eee9] text-forest font-mono text-xs font-bold mt-[2px]">01</span>
          <label className="text-slate-500 font-mono text-xs uppercase tracking-widest font-semibold grid w-full">VỊ TRÍ TUYỂN DỤNG
            <select className="appearance-none w-full border-0 bg-transparent outline-0 text-ink font-sans text-sm font-semibold m-[4px_0_2px] cursor-pointer" value={jobId} onChange={e => { const nextCandidate = candidateList.find(item => item.jobId === e.target.value); if (nextCandidate) { setJobId(e.target.value); selectCandidate(nextCandidate.id) } else { setUploadJobId(e.target.value); setUploadOpen(true); setToast('Job này chưa có ứng viên — hãy upload CV đầu tiên.') } }}>
              {jobList.map(job => <option key={job.id} value={job.id}>{job.title} · {job.code}</option>)}
            </select>
            <small className="text-slate-500 font-sans text-xs">{jobList.find(job => job.id === jobId)?.department}</small>
          </label>
        </div>
        <div className="text-slate-400 text-sm max-[650px]:hidden">→</div>
        <div className="flex items-start gap-[12px] min-w-0 max-[650px]:pt-[14px] max-[650px]:border-t max-[650px]:border-line">
          <span className="w-[22px] h-[22px] flex-none rounded-full grid place-items-center bg-[#e5eee9] text-forest font-mono text-xs font-bold mt-[2px]">02</span>
          <label className="text-slate-500 font-mono text-xs uppercase tracking-widest font-semibold grid w-full">ỨNG VIÊN
            <select className="appearance-none w-full border-0 bg-transparent outline-0 text-ink font-sans text-sm font-semibold m-[4px_0_2px] cursor-pointer" value={candidate.id} onChange={e => selectCandidate(e.target.value)}>
              {available.map(item => <option key={item.id} value={item.id}>{item.name}</option>)}
            </select>
            <small className="text-slate-500 font-sans text-xs">{candidate.role}</small>
          </label>
        </div>
        <div className="border-l border-line pl-[18px] flex items-center gap-[9px] max-[960px]:hidden">
          <span className="bg-[#f3e8e2] text-[#a95543] font-mono font-bold text-xs p-[9px_6px] rounded-[4px]">PDF</span>
          <div className="grid gap-[4px]"><b className="max-w-[145px] overflow-hidden text-ellipsis whitespace-nowrap text-sm font-medium">{candidate.file}</b><small className="text-slate-500 font-sans text-xs">Cập nhật {candidate.updated}</small></div>
        </div>
      </section>

      {fresh && <div className="flex items-center gap-[9px] bg-[#e6f2eb] border border-[#bdd9c9] rounded-[7px] p-[9px_12px] mt-[13px] text-[#2e704f]">
        <span className="w-[19px] h-[19px] bg-[#bfe2ce] rounded-full grid place-items-center text-xs">✓</span>
        <div><b className="text-sm font-medium">Phân tích vừa được cập nhật</b><p className="text-xs text-[#678073] m-[2px_0_0]">Kết quả được grounded trên CV, JD và competency framework.</p></div>
        <button className="ml-auto border-0 bg-transparent text-[#638071]" onClick={() => setFresh(false)}>×</button>
      </div>}

      <div className="mt-[17px] grid grid-cols-[minmax(310px,.78fr)_minmax(480px,1.42fr)] gap-[17px] items-start max-[960px]:grid-cols-1">
        <section className="bg-paper border border-line rounded-[8px] shadow-[0_4px_18px_#24342d08] p-[22px] max-[960px]:grid max-[960px]:grid-cols-2 max-[960px]:gap-[20px] max-[650px]:block">
          <div className="flex justify-between items-start max-[960px]:col-span-2">
            <div><p className="text-xs uppercase tracking-widest text-slate-500 m-[0_0_8px]">MATCH SCORE</p><h2 className="font-serif text-lg font-semibold m-0">Mức độ phù hợp</h2></div>
            <span className="text-forest bg-[#e6f0ea] rounded-[20px] p-[6px_9px] text-xs font-medium">✦ AI đề xuất</span>
          </div>
          <div className="flex items-center gap-[24px] p-[25px_4px_24px] border-b border-line max-[960px]:border-b-0 max-[650px]:border-b max-[650px]:border-line">
            <div className="w-[122px] h-[122px] flex-none rounded-full grid place-items-center relative before:content-[''] before:absolute before:inset-[8px] before:bg-paper before:rounded-full" style={{ background: `conic-gradient(var(--forest) ${candidate.score * 3.6}deg, #e3e5df 0)` }}>
              <div className="relative flex items-baseline"><strong className="font-serif text-3xl font-bold text-forest">{candidate.score}</strong><span className="text-[#8b9591] text-xs">/100</span></div>
            </div>
            <div>
              <b className="font-serif text-lg font-semibold text-forest">Phù hợp cao</b>
              <p className="text-sm leading-6 text-slate-500 m-[6px_0_14px]">Ứng viên đáp ứng phần lớn yêu cầu quan trọng của vị trí.</p>
              <div className="grid grid-cols-[1fr_auto] gap-[5px] items-center">
                <span className="text-xs text-slate-500">Độ tin cậy</span><strong className="text-sm font-medium text-forest">{candidate.confidence}%</strong>
                <i className="col-span-full h-[4px] rounded-[5px] bg-[#e0e5e1] overflow-hidden"><em className="block h-full bg-[#6da28e] rounded-[5px]" style={{ width: `${candidate.confidence}%` }} /></i>
              </div>
            </div>
          </div>
          <div className="p-[20px_0_9px] grid gap-[13px]">
            {candidate.breakdown.map(([name, value, max, reason]) => <div key={name} className="grid gap-[4px]">
              <div className="grid grid-cols-[100px_1fr_38px] items-center gap-[10px]">
                <span className="text-slate-700 text-sm font-medium">{name}</span>
                <i className="h-[5px] rounded-[5px] bg-[#e0e5e1] overflow-hidden"><em className="block h-full bg-forest rounded-[5px]" style={{ width: `${value / max * 100}%` }} /></i>
                <b className="text-right font-mono text-sm font-semibold">{value}<small className="text-slate-400 text-xs">/{max}</small></b>
              </div>
              {reason && <p className="text-xs text-slate-500 m-[0_0_2px_110px] leading-5">{reason}</p>}
            </div>)}
          </div>
          <div className="mt-[13px] p-[11px] flex items-start gap-[9px] rounded-[6px] bg-[#eff4f0] text-forest max-[960px]:col-span-2">
            <div className="flex-none"><Icon name="shield" /></div>
            <p className="text-xs leading-5 m-0 text-slate-500"><b className="text-forest font-medium">Chỉ dùng bằng chứng có trong hồ sơ</b><br />Thông tin thiếu được đánh dấu để HR xác minh.</p>
          </div>
        </section>

        <section className="bg-paper border border-line rounded-[8px] shadow-[0_4px_18px_#24342d08] min-h-[531px] overflow-hidden">
          <div className="h-[53px] px-[22px] border-b border-line flex gap-[25px] max-[650px]:gap-[16px] max-[650px]:overflow-auto">
            <button className={`border-0 border-b-2 bg-transparent text-sm p-[2px_0_0] whitespace-nowrap ${tab === 'overview' ? 'text-forest border-forest font-medium' : 'border-transparent text-slate-500 font-medium'}`} onClick={() => setTab('overview')}>Tổng quan</button>
            <button className={`border-0 border-b-2 bg-transparent text-sm p-[2px_0_0] whitespace-nowrap ${tab === 'evidence' ? 'text-forest border-forest font-medium' : 'border-transparent text-slate-500 font-medium'}`} onClick={() => setTab('evidence')}>Bằng chứng <span className="bg-[#e9ebe6] p-[2px_5px] rounded-[9px] ml-[4px] text-xs font-normal">{candidate.evidence.length}</span></button>
            <button className={`border-0 border-b-2 bg-transparent text-sm p-[2px_0_0] whitespace-nowrap ${tab === 'questions' ? 'text-forest border-forest font-medium' : 'border-transparent text-slate-500 font-medium'}`} onClick={() => setTab('questions')}>Câu hỏi PV <span className="bg-[#e9ebe6] p-[2px_5px] rounded-[9px] ml-[4px] text-xs font-normal">{candidate.questions.length}</span></button>
          </div>

          {tab === 'overview' && <div className="p-[22px]">
            <div className="flex gap-[10px] items-center"><span className="w-[28px] h-[28px] rounded-full grid place-items-center bg-[#e4eee9] text-forest font-bold text-sm">✦</span><div><p className="text-xs uppercase tracking-widest text-slate-500 mb-[4px]">AI EXPLANATION</p><h2 className="font-serif text-lg font-semibold m-0">Tại sao ứng viên được {candidate.score} điểm?</h2></div></div>
            <p className="pb-[18px] m-[13px_0_18px] border-b border-line text-sm text-slate-700 leading-6">{candidate.summary}</p>
            <h3 className="text-sm font-medium m-[0_0_12px]">Bằng chứng nổi bật</h3>
            <div className="grid grid-cols-2 gap-[9px] max-[650px]:grid-cols-1">
              {candidate.evidence.slice(0, 4).map(item => <div key={item.skill} className="border border-line rounded-[6px] p-[10px] flex items-start gap-[8px] min-w-0">
                <span className={`w-[17px] h-[17px] flex-none grid place-items-center rounded-full text-xs font-bold ${item.status === 'found' ? 'text-[#287353] bg-[#dff1e7]' : item.status === 'partial' ? 'text-[#98631c] bg-[#f5ead4]' : 'text-[#a74a3e] bg-[#f4e1dd]'}`}>{item.status === 'found' ? '✓' : item.status === 'partial' ? '~' : '!'}</span>
                <div><b className="text-xs font-semibold">{item.skill}</b><p className="whitespace-nowrap overflow-hidden text-ellipsis max-w-[190px] text-xs text-slate-500 m-[4px_0]">{item.quote}</p><small className="text-xs text-slate-400">{item.source}</small></div>
              </div>)}
            </div>
            <button className="border-0 bg-transparent text-forest p-[13px_0_18px] text-sm font-medium" onClick={() => setTab('evidence')}>Xem toàn bộ bằng chứng <span className="ml-[4px]">→</span></button>
            <div className="pt-[16px] border-t border-line flex justify-between items-center"><div><p className="text-xs uppercase tracking-widest text-[#9a6722] mb-[4px]">GAP DETECTION</p><h3 className="text-sm font-medium m-0">Khoảng trống cần xác minh</h3></div><span className="bg-[#f4e6ce] text-[#93631f] p-[4px_7px] rounded-[10px] text-xs font-medium">{candidate.gaps.length} điểm</span></div>
            <div className="grid gap-[7px] mt-[11px]">
              {candidate.gaps.map(gap => <article key={gap.title} className="grid grid-cols-[19px_1fr_auto] gap-[8px] items-start p-[9px_10px] bg-[#fcf8ef] border-l-2 border-[#d39337] rounded-[3px]">
                <span className="w-[17px] h-[17px] grid place-items-center bg-[#f2dfbe] text-[#93631f] rounded-full text-xs font-bold">!</span>
                <div><b className="text-sm font-medium">{gap.title}</b><p className="text-xs text-slate-500 m-[3px_0_0] leading-5">{gap.text}</p></div>
                <small className="text-[#a36c21] text-xs font-medium whitespace-nowrap">{gap.severity}</small>
              </article>)}
            </div>
            <div className="flex justify-between items-center pt-[17px] mt-[16px] border-t border-line"><div><p className="text-xs uppercase tracking-widest text-slate-500 mb-[4px]">INTERVIEW QUESTIONS</p><h3 className="text-sm font-medium m-0">Câu hỏi phỏng vấn gợi ý</h3></div><button className="border-0 bg-transparent text-forest text-sm font-medium" onClick={() => setTab('questions')}>Xem tất cả {candidate.questions.length} câu →</button></div>
            <div className="grid gap-[7px] mt-[10px]">
              {candidate.questions.slice(0, 2).map((question, index) => <article key={question} className="flex items-start gap-[9px] p-[9px_11px] border border-[#d8ded9] rounded-[5px] bg-[#f8faf7]">
                <span className="w-[17px] h-[17px] flex-none rounded-full grid place-items-center bg-[#dfece5] text-forest text-xs font-bold">{index + 1}</span>
                <p className="m-[1px_0_0] text-sm text-slate-700 leading-6">{question}</p>
              </article>)}
            </div>
          </div>}

          {tab === 'evidence' && <div className="p-[22px]">
            <div className="flex gap-[10px] items-center"><span className="w-[28px] h-[28px] rounded-full grid place-items-center bg-[#e4eee9] text-forest font-bold text-sm">⌕</span><div><p className="text-xs uppercase tracking-widest text-slate-500 mb-[4px]">GROUNDED EVIDENCE</p><h2 className="font-serif text-lg font-semibold m-0">Đối chiếu yêu cầu và CV</h2></div></div>
            <p className="pb-[18px] m-[13px_0_18px] border-b border-line text-sm text-slate-700 leading-6">Mỗi kết luận dưới đây đều trỏ về một đoạn cụ thể trong CV. “Thiếu” không đồng nghĩa ứng viên không có kỹ năng — chỉ là chưa đủ bằng chứng.</p>
            <div className="grid gap-[9px] max-h-[355px] overflow-auto pr-[4px]">
              {candidate.evidence.map(item => <article key={item.skill} className="border border-line rounded-[6px] p-[11px]">
                <div className="flex items-center gap-[7px]">
                  <span className={`w-[17px] h-[17px] flex-none grid place-items-center rounded-full text-xs font-bold ${item.status === 'found' ? 'text-[#287353] bg-[#dff1e7]' : item.status === 'partial' ? 'text-[#98631c] bg-[#f5ead4]' : 'text-[#a74a3e] bg-[#f4e1dd]'}`}>{item.status === 'found' ? '✓' : item.status === 'partial' ? '~' : '?'}</span>
                  <b className="text-sm font-medium">{item.skill}</b>
                  <small className={`ml-auto text-xs font-medium rounded-[10px] p-[4px_7px] ${item.status === 'found' ? 'text-[#287353] bg-[#e3f1e9]' : item.status === 'partial' ? 'text-[#98631c] bg-[#f5ead4]' : 'text-[#a74a3e] bg-[#f4e1dd]'}`}>{item.status === 'found' ? 'Đã xác thực' : item.status === 'partial' ? 'Một phần' : 'Thiếu bằng chứng'}</small>
                </div>
                <blockquote className="m-[10px_0_7px_25px] text-sm text-slate-500 leading-6">“{item.quote}”</blockquote>
                <p className="m-[0_0_0_25px] text-xs text-slate-400">{item.source}</p>
              </article>)}
            </div>
          </div>}

          {tab === 'questions' && <div className="p-[22px]">
            <div className="flex gap-[10px] items-center"><span className="w-[28px] h-[28px] rounded-full grid place-items-center bg-[#e4eee9] text-forest font-bold text-sm">?</span><div><p className="text-xs uppercase tracking-widest text-slate-500 mb-[4px]">INTERVIEW COPILOT</p><h2 className="font-serif text-lg font-semibold m-0">Câu hỏi xác minh đề xuất</h2></div></div>
            <p className="pb-[18px] m-[13px_0_18px] border-b border-line text-sm text-slate-700 leading-6">Các câu hỏi được tạo từ khoảng trống trong CV, giúp HR xác minh thay vì để AI tự suy đoán.</p>
            <div className="grid gap-[10px]">
              {candidate.questions.map((question, index) => <article key={question} className="grid grid-cols-[25px_1fr_auto] items-center gap-[12px] p-[14px] border border-line rounded-[6px]">
                <span className="font-serif font-medium text-sm text-[#66857c]">{String(index + 1).padStart(2, '0')}</span>
                <p className="m-0 text-sm text-slate-700 leading-6">{question}</p>
                <button className="border-0 bg-transparent text-forest text-sm font-medium" onClick={() => { navigator.clipboard?.writeText(question); setToast('Đã sao chép câu hỏi.') }}>Sao chép</button>
              </article>)}
            </div>
          </div>}
        </section>
      </div>

      <section className="mt-[17px] min-h-[98px] border border-[#b9c9c1] rounded-[8px] bg-[#edf2ee] p-[18px_20px] flex items-center gap-[20px] max-[650px]:items-start max-[650px]:flex-col">
        <div>
          <p className="text-xs uppercase tracking-widest text-slate-500 mb-[3px]">HUMAN DECISION</p>
          <h2 className="font-serif text-lg font-semibold m-0">Quyết định của HR</h2>
          <p className="text-xs text-slate-500 m-[4px_0_0]">AI không tự động tuyển hoặc loại ứng viên.</p>
        </div>
        {decision && <div className={`ml-auto flex items-center gap-[8px] text-[#357457] max-[650px]:ml-0 max-[650px]:w-full ${decision.type === 'hold' ? '!text-[#985c34]' : ''}`}>
          <span className="w-[23px] h-[23px] rounded-full bg-[#d6eadf] grid place-items-center">✓</span>
          <div className="grid"><b className="text-sm font-medium">{decision.type === 'advance' ? 'Đã đề xuất vào vòng tiếp' : 'Đã chọn chưa đề xuất'}</b><small className="text-slate-500 mt-[3px] text-xs">{decision.overridden ? `HR override: ${decision.score}/100` : 'Giữ nguyên đánh giá AI'}</small></div>
        </div>}
        <div className="flex gap-[8px] ml-auto max-[650px]:ml-0 max-[650px]:w-full [&>button]:max-[650px]:flex-1 [&>button]:max-[650px]:justify-center">
          <button className="border border-[#c9cfca] bg-paper text-[#48534f] rounded-[6px] p-[10px_14px] text-sm font-medium" onClick={() => setDialog('hold')}>Chưa đề xuất</button>
          <button className="border-0 bg-forest text-white rounded-[6px] p-[11px_15px] text-sm font-medium shadow-[0_1px_2px_#123d3525] flex items-center gap-[8px]" onClick={() => setDialog('advance')}>Đề xuất vào vòng tiếp <span>→</span></button>
        </div>
      </section>
    </div>
  )
}
