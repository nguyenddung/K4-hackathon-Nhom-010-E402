import Icon from '../components/Icon'

export default function AuditView({ audit }) {
  const overrides = audit.filter(log => log.overridden)
  const holds = audit.filter(log => log.decision === 'hold')
  const advances = audit.filter(log => log.decision === 'advance')

  return (
    <div className="max-w m-auto p-[40px_34px_55px] max-[650px]:p-[28px_16px_40px]">
      <section className="flex justify-between items-end gap-[20px] mb-[25px] max-[650px]:items-start max-[650px]:flex-col">
        <div>
          <p className="text-xs uppercase tracking-widest text-slate-500 m-[0_0_8px]">SYSTEM LOGS</p>
          <h1 className="font-serif text-3xl font-semibold tracking-tight leading-tight m-[0_0_7px]">Nhật ký đánh giá</h1>
          <p className="text-sm text-slate-700 leading-6 m-0">Ghi nhận mọi quyết định của HR và AI, cung cấp bằng chứng giải trình khi cần.</p>
        </div>
        <button className="border border-[#c9cfca] bg-paper rounded-[6px] p-[10px_13px] text-sm font-medium whitespace-nowrap" onClick={() => alert('Demo: Tính năng trích xuất (Excel/CSV) chưa khả dụng.')}>↓ Trích xuất báo cáo</button>
      </section>

      <div className="grid grid-cols-4 max-[650px]:grid-cols-2 gap-[12px] mb-[17px]">
        <article className="border border-line bg-paper rounded-[7px] p-[18px]">
          <span className="font-serif text-3xl font-bold text-forest">{audit.length}</span>
          <p className="m-[5px_0_0] text-sm font-medium text-slate-500">Tổng quyết định được lưu</p>
        </article>
        <article className="border border-line bg-paper rounded-[7px] p-[18px]">
          <span className="font-serif text-3xl font-bold text-forest">{overrides.length}</span>
          <p className="m-[5px_0_0] text-sm font-medium text-slate-500">Quyết định can thiệp bởi HR (Override)</p>
        </article>
        <article className="border border-line bg-paper rounded-[7px] p-[18px]">
          <span className="font-serif text-3xl font-bold text-forest">{advances.length}</span>
          <p className="m-[5px_0_0] text-sm font-medium text-slate-500">Đề xuất đi tiếp</p>
        </article>
        <article className="border border-line bg-paper rounded-[7px] p-[18px]">
          <span className="font-serif text-3xl font-bold text-forest">{holds.length}</span>
          <p className="m-[5px_0_0] text-sm font-medium text-slate-500">Từ chối/Giữ lại</p>
        </article>
      </div>

      <div className="bg-paper border border-line rounded-[8px] overflow-hidden max-[650px]:overflow-auto">
        <div className="p-[20px] flex justify-between items-center min-w-[750px]">
          <div><h2 className="font-serif text-lg font-semibold m-0">Lịch sử đánh giá (Audit Trail)</h2><p className="text-xs text-slate-500 m-[5px_0_0]">Cập nhật theo thời gian thực</p></div>
          <span className="text-[#3f8a62] bg-[#e5f1e9] rounded-[12px] p-[5px_8px] text-xs font-medium">{audit.length} bản ghi</span>
        </div>
        <div className="grid grid-cols-[135px_180px_180px_1fr] items-center min-w-[750px] p-[13px_20px] border-t border-line bg-[#f4f4ef] text-xs uppercase tracking-wide font-semibold text-slate-500">
          <span>THỜI GIAN</span><span>ỨNG VIÊN & JOB</span><span>QUYẾT ĐỊNH (HR)</span><span>BẰNG CHỨNG GHI NHẬN (LÝ DO)</span>
        </div>
        {audit.map((log, index) => <div key={index} className="grid grid-cols-[135px_180px_180px_1fr] items-center min-w-[750px] p-[13px_20px] border-t border-line text-sm text-slate-700">
          <span>{log.time}</span>
          <span className="flex items-center gap-[8px] text-[#3d4844]"><i className="w-[23px] h-[23px] rounded-full bg-[#e1ebe5] text-forest grid place-items-center not-italic text-xs font-bold">{log.initials}</i> <b className="font-semibold">{log.candidateName}</b></span>
          <span className="flex items-center gap-[5px] whitespace-nowrap">
            <span className={`rounded-[12px] p-[5px_7px] text-xs font-medium ${log.decision === 'advance' ? 'bg-[#e1f0e7] text-[#2e7150]' : 'bg-[#f5e6dd] text-[#986044]'}`}>{log.decision === 'advance' ? 'Đề xuất vòng tiếp' : 'Từ chối/Hold'}</span>
            {log.overridden && <span className="rounded-[12px] p-[5px_7px] text-xs font-medium bg-[#edf0ec] text-[#59645f]">Override</span>}
          </span>
          <span className="whitespace-nowrap overflow-hidden text-ellipsis">{log.note}</span>
        </div>)}
        {!audit.length && <div className="p-[30px] text-center border-t border-line text-sm text-slate-500">Chưa có quyết định nào được lưu trong hệ thống.</div>}
      </div>
    </div>
  )
}
