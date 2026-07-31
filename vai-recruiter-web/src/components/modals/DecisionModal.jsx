export default function DecisionModal({ type, candidate, onClose, onSubmit, override, setOverride, overrideScore, setOverrideScore }) {
  return (
    <div className="fixed inset-0 z-30 bg-[#132a246b] backdrop-blur-[2px] grid place-items-center p-[20px]">
      <div className="relative w-[min(470px,100%)] rounded-[10px] bg-paper p-[28px] shadow-[0_24px_70px_#152d2440]">
        <button className="absolute right-[16px] top-[12px] border-0 bg-transparent text-[#7a8480] text-[22px]" onClick={onClose}>×</button>
        <p className="text-xs uppercase tracking-widest text-slate-500 m-[0_0_8px]">FINAL REVIEW</p>
        <h2 className="font-serif text-2xl font-semibold m-[0_0_8px]">{type === 'advance' ? 'Đề xuất vào vòng phỏng vấn' : 'Không đề xuất ứng viên này'}</h2>
        <p className="text-sm text-slate-700 leading-6 m-0">Hệ thống sẽ lưu quyết định này vào Audit Log với tên của bạn để đảm bảo tính minh bạch.</p>
        
        <div className="flex items-center gap-[10px] m-[18px_0] p-[12px] bg-[#f0f2ec] rounded-[7px]">
          <span className="w-[33px] h-[33px] rounded-full bg-[#d5e5dc] text-forest grid place-items-center text-sm font-bold">{candidate?.initials}</span>
          <div className="grid gap-[4px]"><b className="text-sm font-semibold">{candidate?.name}</b><small className="text-xs text-slate-500">AI Match Score: {candidate?.score}/100</small></div>
        </div>
        
        <form onSubmit={onSubmit}>
          <label className="grid grid-cols-[auto_auto_1fr] gap-[9px] items-center m-[16px_0] cursor-pointer">
            <input className="hidden peer" type="checkbox" checked={override} onChange={e => setOverride(e.target.checked)} />
            <span className="w-[30px] h-[17px] rounded-[12px] bg-[#cfd4cf] relative transition-[.2s] peer-checked:bg-forest after:content-[''] after:absolute after:w-[13px] after:h-[13px] after:left-[2px] after:top-[2px] after:bg-white after:rounded-full after:transition-[.2s] peer-checked:after:translate-x-[13px]" />
            <div className="grid gap-[3px]"><b className="text-sm font-semibold">Ghi đè điểm AI (Override)</b><small className="text-xs text-slate-500">Dùng khi bạn thấy AI chấm quá khắt khe hoặc bỏ sót ngữ cảnh.</small></div>
          </label>
          
          {override && <label className="grid grid-cols-[1fr_auto] gap-[8px] mb-[16px] text-sm font-semibold">
            Điểm đánh giá lại của HR: <b>{overrideScore}</b>
            <input className="col-span-full accent-forest" type="range" min="0" max="100" value={overrideScore} onChange={e => setOverrideScore(e.target.value)} />
          </label>}
          
          <label className="block text-sm font-semibold">Lý do quyết định (Bắt buộc)
            <textarea className="w-full resize-y mt-[7px] border border-[#cfd3ce] rounded-[6px] p-[10px] outline-forest text-sm leading-6" name="note" rows="3" required placeholder={type === 'advance' ? 'Ví dụ: Ứng viên có exp làm system design tốt dù thiếu vài tool phụ...' : 'Ví dụ: Đòi hỏi mức lương vượt khung ngân sách, kinh nghiệm chưa sâu...'} />
          </label>
          
          <div className="flex justify-end gap-[8px] mt-[18px]">
            <button className="border border-[#c9cfca] bg-paper text-[#48534f] rounded-[6px] p-[10px_14px] text-sm font-medium" type="button" onClick={onClose}>Hủy</button>
            <button className={`border-0 rounded-[6px] p-[11px_15px] text-sm font-medium shadow-[0_1px_2px_#123d3525] text-white ${type === 'advance' ? 'bg-forest' : 'bg-[#a84f43]'}`} type="submit">Lưu quyết định & Ghi log</button>
          </div>
        </form>
      </div>
    </div>
  )
}
