export default function CreateJobModal({ onClose, onSubmit, creatingJob, createJobError }) {
  return (
    <div className="fixed inset-0 z-30 bg-[#132a246b] backdrop-blur-[2px] grid place-items-center p-[20px]">
      <div className="relative w-[min(580px,100%)] rounded-[10px] bg-paper p-[28px] shadow-[0_24px_70px_#152d2440]">
        <button className="absolute right-[16px] top-[12px] border-0 bg-transparent text-[#7a8480] text-[22px]" onClick={onClose}>×</button>
        <p className="text-xs uppercase tracking-widest text-slate-500 m-[0_0_8px]">NEW PIPELINE</p>
        <h2 className="font-serif text-2xl font-semibold m-[0_0_8px]">Tạo Job mới</h2>
        <p className="text-sm text-slate-700 leading-6 m-0 mb-[18px]">Job mới sẽ được thêm vào Pipeline để bắt đầu nhận và đánh giá hồ sơ.</p>
        <form onSubmit={onSubmit}>
          <div className="grid grid-cols-2 max-[650px]:grid-cols-1 gap-[12px]">
            <label className="grid gap-[6px] text-sm font-semibold text-[#4c5753]">Tên vị trí (Title)
              <input className="w-full border border-[#cfd4cf] rounded-[6px] bg-white p-[10px] text-ink outline-forest text-sm" name="title" required placeholder="Ví dụ: Backend Developer"/>
            </label>
            <label className="grid gap-[6px] text-sm font-semibold text-[#4c5753]">Phòng ban (Department)
              <input className="w-full border border-[#cfd4cf] rounded-[6px] bg-white p-[10px] text-ink outline-forest text-sm" name="department" required placeholder="Ví dụ: Engineering"/>
            </label>
            <label className="grid gap-[6px] text-sm font-semibold text-[#4c5753] col-span-full">Mô tả công việc & Yêu cầu (JD)
              <textarea className="w-full resize-y border border-[#cfd4cf] rounded-[6px] bg-white p-[11px] text-ink outline-forest text-sm leading-[1.55]" name="description" rows="5" required placeholder="Nhập mô tả chi tiết, kỹ năng bắt buộc, ngôn ngữ lập trình, hệ thống... AI sẽ dùng thông tin này để đánh giá ứng viên."/>
            </label>
          </div>
          {createJobError && <div className="mt-[12px] p-[9px_10px] rounded-[5px] bg-[#f8e8e4] text-[#9d4035] text-sm font-medium">{createJobError}</div>}
          <div className="flex justify-end gap-[8px] mt-[18px]">
            <button className="border border-[#c9cfca] bg-paper text-[#48534f] rounded-[6px] p-[10px_14px] text-sm font-medium" type="button" onClick={onClose} disabled={creatingJob}>Hủy</button>
            <button className="border-0 bg-forest text-white rounded-[6px] p-[11px_15px] text-sm font-medium shadow-[0_1px_2px_#123d3525] disabled:opacity-65 disabled:cursor-wait" type="submit" disabled={creatingJob}>{creatingJob ? 'Đang lưu...' : 'Tạo Job'}</button>
          </div>
        </form>
      </div>
    </div>
  )
}
