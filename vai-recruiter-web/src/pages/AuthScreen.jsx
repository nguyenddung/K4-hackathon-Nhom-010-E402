import { useState } from 'react'

export default function AuthScreen({ onAuthenticated }) {
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
      const payload = await response.json()
      if (!response.ok) throw new Error(payload.detail || 'Không thể xác thực tài khoản.')
      localStorage.setItem('talentscreen-session', JSON.stringify(payload))
      onAuthenticated(payload)
    } catch (submitError) {
      setError(`${submitError.message} Hãy kiểm tra backend đang chạy ở cổng 8000.`)
    } finally {
      setLoading(false)
    }
  }
  return <div className="min-h-screen grid grid-cols-1 md:grid-cols-[1.05fr_0.95fr] bg-paper">
    <section className="min-h-[230px] md:min-h-screen p-[28px] md:p-[42px_clamp(40px,7vw,105px)] bg-forest text-white flex flex-col relative overflow-hidden after:content-[''] after:absolute after:w-[520px] after:h-[520px] after:-right-[230px] after:-bottom-[220px] after:border after:border-[#bfe8d530] after:rounded-full after:shadow-[0_0_0_70px_#bfe8d508,0_0_0_140px_#bfe8d508]">
      <div className="logo relative z-10 text-xl font-bold"><span className="logo-symbol mr-2 inline-flex items-center justify-center w-6 h-6 bg-mint text-forest rounded">T</span><span>TalentScreen <b className="text-mint">AI</b></span></div>
      <div className="m-[45px_0_10px] md:m-[auto_0] max-w-[560px] relative z-10">
        <p className="text-xs uppercase tracking-widest text-mint mb-2">EVIDENCE-BASED HIRING</p>
        <h1 className="m-[14px_0_22px] font-serif text-3xl font-semibold tracking-tight leading-tight">Tuyển đúng người.<br/><em className="text-mint not-italic">Hiểu rõ lý do.</em></h1>
        <p className="hidden md:block max-w-[510px] text-[#b8cbc5] text-sm leading-6">Trợ lý AI giúp HR sàng lọc Backend Developer nhất quán, có bằng chứng và luôn giữ con người ở vị trí quyết định.</p>
      </div>
      <div className="hidden md:flex gap-[28px] relative z-10 text-[#739a8f] font-mono text-xs font-medium">
        <span className="grid gap-[5px]">01 <b className="text-[#d6e6e1] font-sans text-xs">Grounded evidence</b></span>
        <span className="grid gap-[5px]">02 <b className="text-[#d6e6e1] font-sans text-xs">Human decision</b></span>
        <span className="grid gap-[5px]">03 <b className="text-[#d6e6e1] font-sans text-xs">Audit-ready</b></span>
      </div>
    </section>
    <section className="p-[35px_22px] md:p-[35px] grid place-items-center"><form className="w-[min(390px,100%)]" onSubmit={submit}>
      <p className="text-xs uppercase tracking-widest text-slate-500">{mode === 'login' ? 'WELCOME BACK' : 'CREATE WORKSPACE'}</p>
      <h2 className="m-[0_0_8px] font-serif text-2xl font-semibold text-ink">{mode === 'login' ? 'Đăng nhập vào TalentScreen' : 'Tạo tài khoản HR'}</h2>
      <p className="text-sm text-slate-500 mb-[25px] leading-6">{mode === 'login' ? 'Tiếp tục quản lý pipeline tuyển dụng của bạn.' : 'Bắt đầu workspace sàng lọc minh bạch cho đội ngũ.'}</p>
      
      {mode === 'register' && <>
        <label className="grid gap-[7px] my-[14px] text-slate-700 text-sm font-medium">Họ và tên
          <input className="w-full border border-[#cfd4ce] rounded-[6px] bg-white p-[11px_12px] outline-forest text-ink text-sm placeholder:text-slate-400" name="name" required minLength="2" placeholder="Nguyễn Minh Anh"/>
        </label>
        <label className="grid gap-[7px] my-[14px] text-slate-700 text-sm font-medium">Vai trò
          <select className="w-full border border-[#cfd4ce] rounded-[6px] bg-white p-[11px_12px] outline-forest text-ink text-sm" name="role"><option>HR Manager</option><option>Recruiter</option></select>
        </label>
      </>}
      <label className="grid gap-[7px] my-[14px] text-slate-700 text-sm font-medium">Email
        <input className="w-full border border-[#cfd4ce] rounded-[6px] bg-white p-[11px_12px] outline-forest text-ink text-sm placeholder:text-slate-400" name="email" type="email" required defaultValue={mode === 'login' ? 'demo@vairecruiter.local' : ''} placeholder="hr@company.com"/>
      </label>
      <label className="grid gap-[7px] my-[14px] text-slate-700 text-sm font-medium">Mật khẩu
        <input className="w-full border border-[#cfd4ce] rounded-[6px] bg-white p-[11px_12px] outline-forest text-ink text-sm placeholder:text-slate-400" name="password" type="password" required minLength="8" defaultValue={mode === 'login' ? 'Demo@123' : ''} placeholder="Tối thiểu 8 ký tự"/>
      </label>
      {error && <div className="p-[10px] rounded-[5px] bg-[#f8e7e3] text-[#9b4338] text-sm leading-6">{error}</div>}
      <button className="w-full mt-[8px] border-0 rounded-[6px] p-[12px] bg-forest text-white text-sm font-medium disabled:opacity-[.65]" disabled={loading}>{loading ? 'Đang xử lý...' : mode === 'login' ? 'Đăng nhập →' : 'Tạo tài khoản →'}</button>
      <div className="text-center mt-[18px] text-xs text-slate-500">{mode === 'login' ? 'Chưa có tài khoản?' : 'Đã có tài khoản?'} <button className="border-0 bg-transparent text-forest font-medium text-sm ml-1" type="button" onClick={() => { setMode(mode === 'login' ? 'register' : 'login'); setError('') }}>{mode === 'login' ? 'Đăng ký ngay' : 'Đăng nhập'}</button></div>
    </form></section>
  </div>
}
