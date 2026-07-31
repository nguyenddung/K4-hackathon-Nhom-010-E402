import Icon from '../Icon'

export default function Sidebar({ view, setView, session, onLogout }) {
  return (
    <aside className="fixed inset-[0_auto_0_0] w-[248px] p-[28px_18px_20px] bg-forest text-white flex flex-col z-5 max-[960px]:w-[74px] max-[960px]:p-[26px_12px] max-[650px]:static max-[650px]:w-full max-[650px]:min-h-[58px] max-[650px]:h-[58px] max-[650px]:flex-row max-[650px]:items-center max-[650px]:p-[10px_16px]">
      <div className="flex items-center gap-[11px] text-lg font-semibold tracking-[-.35px] max-[960px]:justify-center">
        <span className="w-[31px] h-[31px] grid place-items-center text-forest bg-mint rounded-[50%_50%_50%_10%] font-serif font-bold text-lg">T</span>
        <span className="max-[960px]:text-[0px] max-[650px]:inline max-[650px]:text-[15px]">TalentScreen <b className="text-mint font-[650]">AI</b></span>
      </div>
      
      <p className="m-[48px_12px_12px] text-[#91afa7] text-xs uppercase tracking-widest font-bold max-[960px]:text-[0px]">WORKSPACE</p>
      
      <nav className="grid gap-[5px] max-[650px]:ml-auto max-[650px]:flex">
        <button 
          className={`border-0 rounded-[7px] p-[11px_12px] bg-transparent text-[#b9cbc6] flex items-center gap-[11px] text-left text-sm font-medium max-[960px]:justify-center max-[960px]:p-[12px] max-[960px]:text-[0px] max-[650px]:hidden ${view === 'pipeline' ? 'bg-[#ffffff15] text-white [&>svg]:text-mint max-[650px]:!flex max-[650px]:text-[0px]' : ''}`} 
          onClick={() => setView('pipeline')}
        >
          <div className="max-[960px]:w-[20px] max-[960px]:h-[20px] flex items-center justify-center"><Icon name="pipeline"/></div>
          Phòng ban & Job
        </button>
        <button 
          className={`border-0 rounded-[7px] p-[11px_12px] bg-transparent text-[#b9cbc6] flex items-center gap-[11px] text-left text-sm font-medium max-[960px]:justify-center max-[960px]:p-[12px] max-[960px]:text-[0px] max-[650px]:hidden ${view === 'screen' ? 'bg-[#ffffff15] text-white [&>svg]:text-mint max-[650px]:!flex max-[650px]:text-[0px]' : ''}`} 
          onClick={() => setView('screen')}
        >
          <div className="max-[960px]:w-[20px] max-[960px]:h-[20px] flex items-center justify-center"><Icon name="screen"/></div>
          Sàng lọc ứng viên
        </button>
        <button 
          className={`border-0 rounded-[7px] p-[11px_12px] bg-transparent text-[#b9cbc6] flex items-center gap-[11px] text-left text-sm font-medium max-[960px]:justify-center max-[960px]:p-[12px] max-[960px]:text-[0px] max-[650px]:hidden ${view === 'audit' ? 'bg-[#ffffff15] text-white [&>svg]:text-mint max-[650px]:!flex max-[650px]:text-[0px]' : ''}`} 
          onClick={() => setView('audit')}
        >
          <div className="max-[960px]:w-[20px] max-[960px]:h-[20px] flex items-center justify-center"><Icon name="audit"/></div>
          Nhật ký đánh giá
        </button>
      </nav>
      
      <div className="mt-auto p-[15px_13px] flex items-start gap-[10px] border border-[#ffffff16] bg-[#ffffff0a] rounded-[9px] text-mint max-[960px]:hidden">
        <div className="flex-none mt-[2px]"><Icon name="shield"/></div>
        <div><b className="text-sm font-semibold text-white">Human-in-the-loop</b><p className="text-[#9ebbb3] m-[4px_0_0] text-xs leading-5">AI chỉ đề xuất. Bạn luôn là người quyết định cuối cùng.</p></div>
      </div>
      
      <div className="border-t border-[#ffffff16] p-[18px_5px_0] mt-[18px] flex items-center gap-[9px] max-[960px]:justify-center max-[960px]:mt-auto max-[650px]:hidden">
        <span className="w-[31px] h-[31px] rounded-full grid place-items-center bg-[#d8c5a3] text-[#604c2c] text-sm font-bold border-0">{session.user.name.split(/\s+/).map(part => part[0]).slice(-2).join('').toUpperCase()}</span>
        <div className="grid max-[960px]:hidden"><b className="text-sm font-semibold">{session.user.name}</b><small className="text-[#91afa7] text-xs mt-[3px]">{session.user.role}</small></div>
        <button className="ml-auto border-0 bg-transparent text-[#91afa7] max-[960px]:hidden" onClick={onLogout} title="Đăng xuất" aria-label="Đăng xuất">↪</button>
      </div>
    </aside>
  )
}
