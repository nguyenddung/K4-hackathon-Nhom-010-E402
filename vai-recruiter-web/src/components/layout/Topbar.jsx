import Icon from '../Icon'

export default function Topbar({ view, session }) {
  return (
    <header className="h-[65px] px-[34px] border-b border-line flex justify-between items-center bg-[#f8f6ef] max-[650px]:hidden">
      <div className="flex items-center gap-[8px] text-sm font-medium text-[#8a918e]">
        <span>TalentScreen</span>
        <Icon name="chevron" size={14}/>
        <b className="text-[#46514d]">{view === 'audit' ? 'Nhật ký đánh giá' : view === 'pipeline' ? 'Phòng ban & Job' : 'Sàng lọc ứng viên'}</b>
      </div>
      <div className="flex items-center gap-[8px]">
        <span className="flex items-center gap-[8px] border border-[#d7ded8] bg-[#f9fcf9] rounded-[20px] p-[7px_11px] text-xs font-medium text-[#557067]">
          <span className="w-[6px] h-[6px] rounded-full bg-[#55a275] shadow-[0_0_0_3px_#55a27520]"/>
          Dữ liệu đã được bảo vệ
        </span>
        <button className="w-[31px] h-[31px] rounded-full grid place-items-center bg-forest text-white text-sm font-bold border-0">
          {session.user.name.split(/\s+/).map(part => part[0]).slice(-2).join('').toUpperCase()}
        </button>
      </div>
    </header>
  )
}
