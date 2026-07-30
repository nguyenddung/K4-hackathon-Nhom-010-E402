import React, { useState, useEffect, useRef } from "react";
import {
  Shield, Lock, Search, Sparkles, ScanLine, MessageSquareText,
  Check, ChevronDown, Menu, X, ArrowRight, Star, Cpu, Database,
  Server, Boxes, Layers, EyeOff, KeyRound, Bug
} from "lucide-react";

const BRAND = {
  ink: "#0B1220",
  navy: "#101B33",
  paper: "#F5F7FA",
  teal: "#0FB88A",
  tealDark: "#0A8F6A",
  amber: "#F5A623",
  line: "#E3E7EE",
  muted: "#5B6472",
};

const NAV_LINKS = [
  { href: "home", label: "Trang chủ" },
  { href: "features", label: "Tính năng" },
  { href: "security", label: "Bảo mật" },
  { href: "pricing", label: "Bảng giá" },
  { href: "faq", label: "Tài nguyên" },
];

/* ---------- Candidate demo data for the animated scan card ---------- */
const CANDIDATES = [
  { initials: "AN", name: "Nguyễn Văn An", role: "Frontend Developer · 3 năm KN", tags: ["React", "TypeScript", "Node.js", "GraphQL"], overall: 92, tech: 92, exp: 78, edu: 85 },
  { initials: "TL", name: "Trần Thanh Lâm", role: "Backend Developer · 4 năm KN", tags: ["Python", "FastAPI", "PostgreSQL", "Redis"], overall: 88, tech: 90, exp: 84, edu: 80 },
  { initials: "MH", name: "Lê Minh Hà", role: "Data Analyst · 2 năm KN", tags: ["SQL", "Power BI", "Python", "ETL"], overall: 81, tech: 76, exp: 70, edu: 90 },
];

const QUEUE = [
  { initials: "PD", name: "Phạm T. Dung", role: "Marketing Mgr" },
  { initials: "NB", name: "Nguyễn Bảo", role: "Sales Lead" },
  { initials: "VT", name: "Võ Thành", role: "Data Analyst" },
];

/* ---------- Anti-bias pipeline demo content ---------- */
const RAW_CV_LINE = "Nguyễn Văn An · Nam · 24 tuổi · Tốt nghiệp ĐH Bách Khoa Hà Nội · Quê quán Nam Định";
const MASKED_CV_LINE = "Ứng viên #A7F3 · Ứng viên · [ẨN] tuổi · Tốt nghiệp [ẨN] · [ẨN]";

const PIPELINE_STEPS = [
  {
    icon: Layers,
    title: "1. Nhận hồ sơ",
    body: "CV gốc (PDF/DOCX) được tiếp nhận, bao gồm cả các trường thông tin cá nhân không liên quan đến năng lực.",
  },
  {
    icon: EyeOff,
    title: "2. Ẩn định kiến",
    body: "Hệ thống tự động phát hiện và làm mờ giới tính, độ tuổi, quốc tịch, vùng miền, tên trường học trước khi dữ liệu rời khỏi vùng an toàn.",
  },
  {
    icon: Sparkles,
    title: "3. Phân tích LLM",
    body: "Chỉ dữ liệu năng lực thuần túy (kỹ năng, kinh nghiệm, dự án) được gửi tới mô hình ngôn ngữ để chấm điểm — loại trừ khả năng thiên vị vô thức.",
  },
];

/* ---------- Core feature + security cards ---------- */
const CORE_FEATURES = [
  { icon: ScanLine, tag: "01 / MATCHING", title: "Sàng lọc & Chấm điểm tương thích", body: "Phân tích CV dạng PDF/DOCX, đối chiếu chi tiết với JD và trả về Matching Score trực quan cùng bảng phân tích kỹ năng mạnh / yếu.", pill: "Tiết kiệm 80% thời gian" },
  { icon: MessageSquareText, tag: "05 / INTERVIEW", title: "Gợi ý bộ câu hỏi phỏng vấn", body: "Tự động phát hiện lỗ hổng kỹ năng hoặc thông tin mâu thuẫn trong CV, sinh câu hỏi phỏng vấn sâu, cá nhân hóa cho từng ứng viên.", pill: "Weakness Probing" },
];

const SECURITY_FEATURES = [
  { icon: EyeOff, title: "Quy trình 3 lớp giảm thiểu thiên vị", body: "Loại bỏ giới tính, tuổi, quốc tịch, vùng miền, tên trường trước khi đưa vào LLM — đánh giá thuần túy dựa trên năng lực.", meta: "Anti-Bias Pipeline" },
  { icon: Lock, title: "Mã hóa PII & Blind Indexing", body: "Tên, email, SĐT, địa chỉ được mã hóa trước khi lưu trữ hay truyền ra cloud. Tìm kiếm hoạt động trực tiếp trên dữ liệu đã mã hóa.", meta: "PII Encryption" },
  { icon: Bug, title: "Hàng rào chống Prompt Injection", body: "Phát hiện và lọc bỏ các lệnh ẩn ứng viên cố tình chèn vào CV nhằm đánh lừa AI nâng điểm số đánh giá.", meta: "AI Security Gate" },
];

const TECH_STACK = {
  Frontend: { icon: Layers, items: ["Next.js 15", "Tailwind CSS", "TypeScript"], body: "Giao diện hiện đại, tối ưu SEO, hỗ trợ Responsive & Dark/Light mode." },
  Backend: { icon: Server, items: ["FastAPI", "Python", "SQLAlchemy ORM"], body: "Đảm bảo hiệu năng xử lý API cực nhanh cho khối lượng CV lớn." },
  "Database & Queue": { icon: Database, items: ["PostgreSQL", "Redis", "RQ Workers"], body: "Xử lý hàng đợi phân tích CV bất đồng bộ để tránh nghẽn luồng." },
  "AI Engine": { icon: Cpu, items: ["Gemini API", "OpenAI API", "LangChain"], body: "Tích hợp linh hoạt nhiều mô hình ngôn ngữ lớn qua LangChain." },
  Deployment: { icon: Boxes, items: ["Docker", "Docker Compose"], body: "Đóng gói và triển khai nhất quán trên mọi môi trường." },
};

const PLANS = [
  {
    name: "Cơ bản", sub: "Phù hợp cho doanh nghiệp nhỏ", monthly: 0, yearly: 0,
    features: ["Đăng tin tuyển dụng không giới hạn", "100 credit AI/tháng", "Quản lý ứng viên cơ bản", "Hỗ trợ email"], cta: "Dùng thử miễn phí",
  },
  {
    name: "Chuyên nghiệp", sub: "Phù hợp cho doanh nghiệp vừa", monthly: 199000, yearly: 159000, popular: true,
    features: ["Đăng tin tuyển dụng không giới hạn", "2.000 credit AI/tháng", "Đánh giá CV 2 credit/lượt, tác vụ khác 1 credit", "Hỗ trợ ưu tiên"], cta: "Bắt đầu ngay",
  },
  {
    name: "Max", sub: "Dành cho agency & doanh nghiệp lớn", monthly: 499000, yearly: 399000,
    features: ["Đăng tin tuyển dụng không giới hạn", "5.500 credit AI/tháng", "Đánh giá CV 2 credit/lượt, tác vụ khác 1 credit", "Hỗ trợ ưu tiên 24/7"], cta: "Nâng gói Max",
  },
];

const TESTIMONIALS = [
  { quote: "V-AI Recruiter giúp chúng tôi tiết kiệm hơn 80% thời gian sàng lọc hồ sơ. AI rất chính xác!", name: "Nguyễn Thị Hương", role: "HR Manager - FPT Software", initials: "NH" },
  { quote: "Giao diện dễ dùng, tính năng mạnh mẽ và tiết kiệm chi phí. Rất đáng để đầu tư!", name: "Trần Văn Minh", role: "CEO - Miss JSC", initials: "TM" },
  { quote: "Tự động hóa lịch phỏng vấn và báo cáo rất hữu ích cho đội ngũ HR của chúng tôi.", name: "Phạm Quang Hiệp", role: "HR Director - Viettel Telecom", initials: "PH" },
];

const FAQS = [
  { q: "V-AI Recruiter có miễn phí không?", a: "Có, gói Cơ bản miễn phí vĩnh viễn với 100 credit AI mỗi tháng, phù hợp cho doanh nghiệp nhỏ mới bắt đầu." },
  { q: "AI sàng lọc hồ sơ dựa trên tiêu chí nào?", a: "AI đánh giá dựa trên kỹ năng kỹ thuật, kinh nghiệm làm việc, học vấn và mức độ phù hợp với mô tả công việc — sau khi đã ẩn các thông tin gây thiên vị." },
  { q: "Dữ liệu ứng viên có được bảo mật không?", a: "Toàn bộ PII được mã hóa trước khi lưu trữ hoặc truyền tải, tìm kiếm hoạt động trên dữ liệu đã mã hóa (Blind Indexing)." },
  { q: "Hệ thống xử lý thế nào nếu ứng viên gian lận bằng Prompt Injection?", a: "AI Security Gate kiểm tra cấu trúc ngữ nghĩa của CV, tự động phát hiện và lọc bỏ các lệnh ẩn trước khi đưa vào quy trình chấm điểm." },
];

function fmtVND(n) {
  if (n === 0) return "0đ";
  return n.toLocaleString("vi-VN") + "đ";
}

export default function VAIRecruiterLanding() {
  const [menuOpen, setMenuOpen] = useState(false);
  const [activeSection, setActiveSection] = useState("home");
  const [candidateIdx, setCandidateIdx] = useState(0);
  const [progress, setProgress] = useState(40);
  const [pipelineStep, setPipelineStep] = useState(1);
  const [techTab, setTechTab] = useState("Frontend");
  const [billing, setBilling] = useState("monthly");
  const [openFaq, setOpenFaq] = useState(0);
  const [testiIdx, setTestiIdx] = useState(0);

  const sectionRefs = useRef({});

  // Animate the CV scan progress bar and cycle candidates
  useEffect(() => {
    const tick = setInterval(() => {
      setProgress((p) => {
        if (p >= 100) {
          setCandidateIdx((i) => (i + 1) % CANDIDATES.length);
          return 30;
        }
        return p + 4;
      });
    }, 250);
    return () => clearInterval(tick);
  }, []);

  // Auto-advance testimonials
  useEffect(() => {
    const t = setInterval(() => setTestiIdx((i) => (i + 1) % TESTIMONIALS.length), 5000);
    return () => clearInterval(t);
  }, []);

  // Scroll-spy for nav active state
  useEffect(() => {
    const handler = () => {
      let current = "home";
      Object.entries(sectionRefs.current).forEach(([id, el]) => {
        if (el && el.getBoundingClientRect().top <= 140) current = id;
      });
      setActiveSection(current);
    };
    window.addEventListener("scroll", handler);
    return () => window.removeEventListener("scroll", handler);
  }, []);

  const scrollTo = (id) => {
    setMenuOpen(false);
    sectionRefs.current[id]?.scrollIntoView({ behavior: "smooth", block: "start" });
  };

  const candidate = CANDIDATES[candidateIdx];

  return (
    <div style={{ background: BRAND.paper, color: BRAND.ink, fontFamily: "Inter, sans-serif" }} className="min-h-screen">
      <style>{`
        @keyframes pulseDot { 0%,100%{opacity:1} 50%{opacity:.25} }
        @keyframes scan { 0%{transform:translateY(0);opacity:0} 8%{opacity:1} 92%{opacity:1} 100%{transform:translateY(220px);opacity:0} }
        .font-display { font-family: 'Space Grotesk', sans-serif; letter-spacing: -0.02em; }
        .font-mono { font-family: 'JetBrains Mono', monospace; }
      `}</style>
      <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet" />

      {/* NAV */}
      <header className="sticky top-0 z-50 backdrop-blur border-b" style={{ background: "rgba(245,247,250,0.85)", borderColor: BRAND.line }}>
        <div className="max-w-6xl mx-auto px-6 flex items-center justify-between py-4">
          <button onClick={() => scrollTo("home")} className="flex items-center gap-2 font-bold text-lg font-display">
            <span className="w-8 h-8 rounded-lg flex items-center justify-center" style={{ background: BRAND.ink }}>
              <Sparkles size={15} color={BRAND.teal} />
            </span>
            V-AIRECRUITER
          </button>

          <nav className="hidden md:flex gap-8 text-sm font-medium" style={{ color: BRAND.muted }}>
            {NAV_LINKS.map((l) => (
              <button
                key={l.href}
                onClick={() => scrollTo(l.href)}
                className="transition-colors"
                style={{ color: activeSection === l.href ? BRAND.ink : BRAND.muted, fontWeight: activeSection === l.href ? 700 : 500 }}
              >
                {l.label}
              </button>
            ))}
          </nav>

          <div className="hidden md:flex items-center gap-3">
            <button className="text-sm font-semibold px-2" style={{ color: BRAND.muted }}>Đăng nhập</button>
            <button
              className="text-sm font-semibold px-5 py-2.5 rounded-lg text-white transition-colors"
              style={{ background: BRAND.ink }}
              onMouseEnter={(e) => (e.currentTarget.style.background = BRAND.tealDark)}
              onMouseLeave={(e) => (e.currentTarget.style.background = BRAND.ink)}
            >
              Dùng thử miễn phí
            </button>
          </div>

          <button className="md:hidden" onClick={() => setMenuOpen((v) => !v)}>
            {menuOpen ? <X size={22} /> : <Menu size={22} />}
          </button>
        </div>

        {menuOpen && (
          <div className="md:hidden px-6 pb-5 flex flex-col gap-4 border-t" style={{ borderColor: BRAND.line }}>
            {NAV_LINKS.map((l) => (
              <button key={l.href} onClick={() => scrollTo(l.href)} className="text-left text-sm font-medium pt-3">
                {l.label}
              </button>
            ))}
            <button className="text-sm font-semibold px-5 py-2.5 rounded-lg text-white mt-2" style={{ background: BRAND.ink }}>
              Dùng thử miễn phí
            </button>
          </div>
        )}
      </header>

      {/* HERO */}
      <section ref={(el) => (sectionRefs.current.home = el)} className="pt-16 pb-10 px-6">
        <div className="max-w-6xl mx-auto grid md:grid-cols-2 gap-14 items-center">
          <div>
            <div className="inline-flex items-center gap-2 bg-white border rounded-full px-3.5 py-1.5 text-xs font-semibold mb-5" style={{ borderColor: BRAND.line, color: BRAND.tealDark }}>
              <span className="w-1.5 h-1.5 rounded-full" style={{ background: BRAND.teal }} />
              AI hỗ trợ tuyển dụng thông minh
            </div>
            <h1 className="font-display font-bold text-4xl md:text-5xl leading-tight mb-5">
              Tuyển đúng người,<br />
              <span style={{ color: BRAND.tealDark }}>hiệu quả vượt trội</span>
            </h1>
            <p className="mb-8 max-w-md leading-relaxed" style={{ color: BRAND.muted, fontSize: 17 }}>
              Nền tảng AI Full-stack giúp doanh nghiệp tự động hóa sàng lọc CV, đối chiếu JD và đánh giá ứng viên — an toàn dữ liệu và khách quan là gốc rễ thiết kế.
            </p>
            <div className="flex gap-3 mb-11">
              <button className="flex items-center gap-2 text-white font-semibold px-6 py-3.5 rounded-lg" style={{ background: BRAND.ink }}>
                Dùng thử miễn phí <ArrowRight size={16} />
              </button>
              <button onClick={() => scrollTo("security")} className="font-semibold px-6 py-3.5 rounded-lg border bg-white" style={{ borderColor: BRAND.line }}>
                Xem cách hoạt động
              </button>
            </div>
            <div className="flex gap-9">
              {[["80%", "Tiết kiệm thời gian"], ["92%", "Độ chính xác AI"], ["24/7", "Sàng lọc tự động"]].map(([n, l]) => (
                <div key={l} className="border-l-2 pl-3.5" style={{ borderColor: BRAND.line }}>
                  <b className="block font-display text-xl">{n}</b>
                  <span className="text-xs" style={{ color: BRAND.muted }}>{l}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Animated scan card */}
          <div className="rounded-2xl p-5 text-white relative overflow-hidden" style={{ background: BRAND.navy, boxShadow: "0 24px 60px -20px rgba(16,27,51,0.5)" }}>
            <div className="absolute left-0 right-0 h-0.5 pointer-events-none" style={{ background: `linear-gradient(90deg, transparent, ${BRAND.teal}, transparent)`, animation: "scan 3s linear infinite", boxShadow: `0 0 16px 2px ${BRAND.teal}` }} />
            <div className="flex justify-between items-start mb-4">
              <div>
                <h4 className="font-semibold text-sm">AI Phân tích CV</h4>
                <p className="text-xs" style={{ color: "#9AA5B8" }}>Senior Frontend Developer · 12 ứng viên</p>
              </div>
              <div className="flex items-center gap-1.5 text-xs font-semibold px-2.5 py-1 rounded-full" style={{ background: "rgba(15,184,138,0.15)", color: BRAND.teal }}>
                <span className="w-1.5 h-1.5 rounded-full" style={{ background: BRAND.teal, animation: "pulseDot 1.4s infinite" }} />
                Đang xử lý
              </div>
            </div>

            <div className="flex justify-between text-xs mb-1.5" style={{ color: "#9AA5B8" }}>
              <span>Tiến trình phân tích</span><span>{Math.min(progress, 100)}%</span>
            </div>
            <div className="h-1.5 rounded-full mb-5 overflow-hidden" style={{ background: "rgba(255,255,255,0.08)" }}>
              <div className="h-full rounded-full transition-all duration-200" style={{ width: `${Math.min(progress, 100)}%`, background: `linear-gradient(90deg, ${BRAND.teal}, #5EEAC0)` }} />
            </div>

            <div className="rounded-xl p-4 mb-3.5 border" style={{ background: "rgba(255,255,255,0.04)", borderColor: "rgba(255,255,255,0.08)" }}>
              <div className="flex gap-3 items-center mb-3">
                <div className="w-10 h-10 rounded-lg flex items-center justify-center font-bold text-xs" style={{ background: `linear-gradient(135deg, ${BRAND.teal}, #1C4E8C)` }}>
                  {candidate.initials}
                </div>
                <div>
                  <h5 className="text-sm font-semibold">{candidate.name}</h5>
                  <p className="text-xs" style={{ color: "#9AA5B8" }}>{candidate.role}</p>
                </div>
              </div>
              <div className="flex gap-1.5 flex-wrap mb-3.5">
                {candidate.tags.map((t) => (
                  <span key={t} className="text-xs px-2 py-1 rounded-md font-mono" style={{ background: "rgba(255,255,255,0.06)", color: "#C7CEDA" }}>{t}</span>
                ))}
              </div>
              <div className="flex items-center justify-between mb-2.5">
                <span className="text-xs" style={{ color: "#9AA5B8" }}>Điểm tổng thể — Ưu tiên cao</span>
                <div
                  className="w-12 h-12 rounded-full flex items-center justify-center font-display font-bold text-xs"
                  style={{ background: `conic-gradient(${BRAND.teal} 0deg ${candidate.overall * 3.6}deg, rgba(255,255,255,0.08) ${candidate.overall * 3.6}deg 360deg)` }}
                >
                  <div className="w-[42px] h-[42px] rounded-full flex items-center justify-center" style={{ background: BRAND.navy }}>{candidate.overall}%</div>
                </div>
              </div>
              <div className="grid grid-cols-3 gap-2 text-xs" style={{ color: "#9AA5B8" }}>
                <div>Kỹ thuật<b className="block font-display text-white text-sm">{candidate.tech}%</b></div>
                <div>Kinh nghiệm<b className="block font-display text-white text-sm">{candidate.exp}%</b></div>
                <div>Học vấn<b className="block font-display text-white text-sm">{candidate.edu}%</b></div>
              </div>
            </div>

            <div className="flex gap-2.5">
              {QUEUE.map((q) => (
                <div key={q.initials} className="flex-1 text-center rounded-lg p-2.5 border" style={{ background: "rgba(255,255,255,0.04)", borderColor: "rgba(255,255,255,0.07)" }}>
                  <div className="w-7 h-7 mx-auto mb-1.5 rounded-lg flex items-center justify-center text-[11px] font-bold" style={{ background: `linear-gradient(135deg, ${BRAND.teal}, #1C4E8C)` }}>{q.initials}</div>
                  <p className="text-xs font-semibold">{q.name}</p>
                  <span className="text-[10px]" style={{ color: "#9AA5B8" }}>{q.role}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="max-w-6xl mx-auto flex gap-7 flex-wrap py-6 mt-10 border-t border-b text-sm font-medium" style={{ borderColor: BRAND.line, color: BRAND.muted }}>
          {["Bảo mật dữ liệu tuyệt đối", "Giao diện dễ sử dụng", "Hỗ trợ 24/7"].map((s) => (
            <span key={s} className="flex items-center gap-2"><Check size={15} color={BRAND.tealDark} />{s}</span>
          ))}
        </div>
      </section>

      {/* FEATURES */}
      <section ref={(el) => (sectionRefs.current.features = el)} className="py-20 px-6">
        <div className="max-w-6xl mx-auto">
          <SectionHead eyebrow="Tính năng nổi bật" title="Tuyển dụng thông minh, hiệu quả vượt trội" desc="Bộ công cụ đầy đủ giúp bạn tối ưu quy trình tuyển dụng và tìm được ứng viên phù hợp nhanh hơn." />
          <div className="grid md:grid-cols-2 gap-5">
            {CORE_FEATURES.map((f) => (
              <div key={f.title} className="bg-white border rounded-2xl p-7 transition-all hover:-translate-y-1" style={{ borderColor: BRAND.line }}>
                <f.icon size={22} color={BRAND.tealDark} className="mb-4" />
                <h3 className="font-semibold text-lg mb-2.5">{f.title}</h3>
                <p className="text-sm leading-relaxed mb-4" style={{ color: BRAND.muted }}>{f.body}</p>
                <span className="text-xs font-semibold" style={{ color: BRAND.tealDark }}>{f.pill}</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* SECURITY / ANTI-BIAS */}
      <section ref={(el) => (sectionRefs.current.security = el)} className="py-20 px-6 text-white" style={{ background: BRAND.navy }}>
        <div className="max-w-6xl mx-auto">
          <SectionHead
            dark
            eyebrow="Công nghệ cốt lõi"
            title="An toàn dữ liệu và khách quan là gốc rễ"
            desc="Mỗi hồ sơ đi qua V-AI Recruiter được xử lý qua các lớp bảo mật và chống thiên vị độc quyền — trước khi chạm tới bất kỳ mô hình ngôn ngữ nào."
          />

          {/* Interactive anti-bias pipeline demo */}
          <div className="rounded-2xl border p-6 mb-8" style={{ borderColor: "rgba(255,255,255,0.1)", background: "rgba(255,255,255,0.03)" }}>
            <div className="flex flex-wrap gap-3 mb-6">
              {PIPELINE_STEPS.map((s, i) => (
                <button
                  key={s.title}
                  onClick={() => setPipelineStep(i)}
                  className="flex items-center gap-2 text-xs font-semibold px-3.5 py-2 rounded-full border transition-colors"
                  style={{
                    borderColor: pipelineStep === i ? BRAND.teal : "rgba(255,255,255,0.15)",
                    background: pipelineStep === i ? "rgba(15,184,138,0.15)" : "transparent",
                    color: pipelineStep === i ? BRAND.teal : "#AEB7C6",
                  }}
                >
                  <s.icon size={13} /> {s.title}
                </button>
              ))}
            </div>
            <p className="text-sm leading-relaxed mb-5" style={{ color: "#C7CEDA", maxWidth: 620 }}>
              {PIPELINE_STEPS[pipelineStep].body}
            </p>
            <div className="grid md:grid-cols-2 gap-4">
              <div className="rounded-xl p-4 border" style={{ borderColor: "rgba(255,255,255,0.1)", background: "rgba(255,255,255,0.03)" }}>
                <div className="text-[11px] font-mono mb-2" style={{ color: "#8993A6" }}>DỮ LIỆU GỐC</div>
                <div className="font-mono text-xs leading-relaxed" style={{ color: pipelineStep >= 1 ? "#5C6577" : "#fff", textDecoration: pipelineStep >= 1 ? "line-through" : "none" }}>
                  {RAW_CV_LINE}
                </div>
              </div>
              <div className="rounded-xl p-4 border" style={{ borderColor: pipelineStep >= 1 ? "rgba(15,184,138,0.4)" : "rgba(255,255,255,0.1)", background: "rgba(255,255,255,0.03)" }}>
                <div className="text-[11px] font-mono mb-2" style={{ color: "#8993A6" }}>SAU KHI ẨN ĐỊNH KIẾN</div>
                <div className="font-mono text-xs leading-relaxed" style={{ color: pipelineStep >= 1 ? BRAND.teal : "#5C6577" }}>
                  {pipelineStep >= 1 ? MASKED_CV_LINE : "— chờ xử lý —"}
                </div>
              </div>
            </div>
          </div>

          <div className="grid md:grid-cols-3 gap-5">
            {SECURITY_FEATURES.map((f) => (
              <div key={f.title} className="rounded-2xl p-6 border transition-colors" style={{ borderColor: "rgba(255,255,255,0.09)", background: "rgba(255,255,255,0.04)" }}>
                <f.icon size={20} color={BRAND.teal} className="mb-3.5" />
                <h3 className="font-semibold text-base mb-2.5">{f.title}</h3>
                <p className="text-sm leading-relaxed mb-4" style={{ color: "#B7C0D1" }}>{f.body}</p>
                <div className="text-xs font-mono pt-3 border-t" style={{ borderColor: "rgba(255,255,255,0.08)", color: "#8993A6" }}>{f.meta}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* TECH STACK — interactive tabs */}
      <section className="py-20 px-6">
        <div className="max-w-6xl mx-auto">
          <SectionHead eyebrow="Tech Stack" title="Nền tảng kỹ thuật đứng sau V-AI Recruiter" desc="Kiến trúc full-stack hiện đại, xử lý bất đồng bộ để CV lớn không làm nghẽn hệ thống." />
          <div className="flex flex-wrap gap-2 mb-6">
            {Object.keys(TECH_STACK).map((k) => (
              <button
                key={k}
                onClick={() => setTechTab(k)}
                className="text-sm font-semibold px-4 py-2 rounded-lg border transition-colors"
                style={{
                  borderColor: techTab === k ? BRAND.ink : BRAND.line,
                  background: techTab === k ? BRAND.ink : "white",
                  color: techTab === k ? "white" : BRAND.ink,
                }}
              >
                {k}
              </button>
            ))}
          </div>
          <div className="bg-white border rounded-2xl p-8 flex items-start gap-6" style={{ borderColor: BRAND.line }}>
            <div className="w-12 h-12 rounded-xl flex items-center justify-center flex-shrink-0" style={{ background: BRAND.paper }}>
              {React.createElement(TECH_STACK[techTab].icon, { size: 22, color: BRAND.tealDark })}
            </div>
            <div>
              <div className="flex flex-wrap gap-2 mb-3">
                {TECH_STACK[techTab].items.map((it) => (
                  <span key={it} className="text-xs font-semibold px-2.5 py-1 rounded-md border" style={{ borderColor: BRAND.line, background: BRAND.paper }}>{it}</span>
                ))}
              </div>
              <p className="text-sm" style={{ color: BRAND.muted }}>{TECH_STACK[techTab].body}</p>
            </div>
          </div>
        </div>
      </section>

      {/* PRICING — monthly/yearly toggle */}
      <section ref={(el) => (sectionRefs.current.pricing = el)} className="py-20 px-6" style={{ background: "white", borderTop: `1px solid ${BRAND.line}`, borderBottom: `1px solid ${BRAND.line}` }}>
        <div className="max-w-6xl mx-auto">
          <SectionHead eyebrow="Bảng giá" title="Linh hoạt gói dịch vụ phù hợp với mọi quy mô" desc="Chọn gói phù hợp với quy mô doanh nghiệp của bạn, nâng cấp bất cứ lúc nào." />

          <div className="flex items-center gap-3 mb-9">
            <button
              onClick={() => setBilling("monthly")}
              className="text-sm font-semibold px-4 py-2 rounded-lg border"
              style={{ borderColor: billing === "monthly" ? BRAND.ink : BRAND.line, background: billing === "monthly" ? BRAND.ink : "white", color: billing === "monthly" ? "white" : BRAND.ink }}
            >
              Theo tháng
            </button>
            <button
              onClick={() => setBilling("yearly")}
              className="text-sm font-semibold px-4 py-2 rounded-lg border flex items-center gap-2"
              style={{ borderColor: billing === "yearly" ? BRAND.ink : BRAND.line, background: billing === "yearly" ? BRAND.ink : "white", color: billing === "yearly" ? "white" : BRAND.ink }}
            >
              Theo năm <span className="text-xs px-1.5 py-0.5 rounded-full" style={{ background: BRAND.teal, color: "white" }}>-20%</span>
            </button>
          </div>

          <div className="grid md:grid-cols-3 gap-5">
            {PLANS.map((p) => (
              <div
                key={p.name}
                className="relative bg-white rounded-2xl p-8 flex flex-col"
                style={{ border: p.popular ? `2px solid ${BRAND.ink}` : `1px solid ${BRAND.line}` }}
              >
                {p.popular && (
                  <span className="absolute -top-3 left-8 text-xs font-bold px-3 py-1 rounded-full text-white" style={{ background: BRAND.teal }}>Phổ biến</span>
                )}
                <h3 className="text-lg font-semibold mb-1">{p.name}</h3>
                <p className="text-sm mb-5" style={{ color: BRAND.muted }}>{p.sub}</p>
                <div className="font-display font-bold text-3xl mb-6">
                  {fmtVND(billing === "monthly" ? p.monthly : p.yearly)}
                  <span className="text-sm font-normal ml-1" style={{ color: BRAND.muted }}>/ tháng</span>
                </div>
                <ul className="flex-1 mb-7">
                  {p.features.map((f, i) => (
                    <li key={f} className="flex gap-2.5 text-sm py-2.5" style={{ borderTop: i === 0 ? "none" : `1px solid ${BRAND.line}` }}>
                      <Check size={15} color={BRAND.tealDark} className="flex-shrink-0 mt-0.5" /> {f}
                    </li>
                  ))}
                </ul>
                <button
                  className="w-full text-sm font-semibold py-3 rounded-lg"
                  style={p.popular ? { background: BRAND.ink, color: "white" } : { border: `1px solid ${BRAND.line}`, background: "white" }}
                >
                  {p.cta}
                </button>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* TESTIMONIALS carousel */}
      <section className="py-20 px-6">
        <div className="max-w-3xl mx-auto text-center">
          <SectionHead center eyebrow="Đánh giá" title="Khách hàng nói gì về chúng tôi" />
          <div className="bg-white border rounded-2xl p-9" style={{ borderColor: BRAND.line }}>
            <div className="flex justify-center gap-0.5 mb-5" style={{ color: BRAND.amber }}>
              {Array.from({ length: 5 }).map((_, i) => <Star key={i} size={16} fill={BRAND.amber} strokeWidth={0} />)}
            </div>
            <p className="text-base leading-relaxed mb-6">"{TESTIMONIALS[testiIdx].quote}"</p>
            <div className="flex items-center justify-center gap-3">
              <div className="w-9 h-9 rounded-lg flex items-center justify-center text-xs font-bold text-white" style={{ background: `linear-gradient(135deg, #1C4E8C, ${BRAND.teal})` }}>
                {TESTIMONIALS[testiIdx].initials}
              </div>
              <div className="text-left">
                <b className="block text-sm">{TESTIMONIALS[testiIdx].name}</b>
                <span className="text-xs" style={{ color: BRAND.muted }}>{TESTIMONIALS[testiIdx].role}</span>
              </div>
            </div>
          </div>
          <div className="flex justify-center gap-2 mt-5">
            {TESTIMONIALS.map((_, i) => (
              <button key={i} onClick={() => setTestiIdx(i)} className="w-2 h-2 rounded-full" style={{ background: i === testiIdx ? BRAND.ink : BRAND.line }} />
            ))}
          </div>
        </div>
      </section>

      {/* FAQ accordion */}
      <section ref={(el) => (sectionRefs.current.faq = el)} className="py-20 px-6">
        <div className="max-w-2xl mx-auto">
          <SectionHead center eyebrow="Câu hỏi thường gặp" title="Bạn cần biết thêm điều gì?" />
          <div>
            {FAQS.map((f, i) => (
              <div key={f.q} className="border-b" style={{ borderColor: BRAND.line }}>
                <button onClick={() => setOpenFaq(openFaq === i ? -1 : i)} className="w-full flex justify-between items-center py-5 text-left font-semibold text-[15px]">
                  {f.q}
                  <ChevronDown size={18} style={{ color: BRAND.muted, transform: openFaq === i ? "rotate(180deg)" : "none", transition: "transform .2s" }} />
                </button>
                {openFaq === i && <p className="text-sm pb-5 leading-relaxed max-w-lg" style={{ color: BRAND.muted }}>{f.a}</p>}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="px-6 pb-20">
        <div className="max-w-6xl mx-auto rounded-3xl p-14 text-center text-white relative overflow-hidden" style={{ background: BRAND.navy }}>
          <div className="absolute w-96 h-96 rounded-full opacity-20" style={{ background: BRAND.teal, filter: "blur(60px)", top: -150, right: -100 }} />
          <h2 className="font-display font-bold text-3xl mb-3 relative">Sẵn sàng nâng cấp quy trình tuyển dụng?</h2>
          <p className="mb-7 relative" style={{ color: "#B7C0D1" }}>Dùng thử V-AI Recruiter miễn phí 14 ngày, không cần thẻ tín dụng.</p>
          <button className="relative font-semibold px-7 py-3.5 rounded-lg" style={{ background: BRAND.teal, color: "white" }}>
            Dùng thử miễn phí ngay
          </button>
        </div>
      </section>

      {/* FOOTER */}
      <footer className="px-6 py-10 border-t text-sm" style={{ borderColor: BRAND.line, color: BRAND.muted }}>
        <div className="max-w-6xl mx-auto flex flex-wrap justify-between gap-4">
          <span>© 2024 V-AI Recruiter. All rights reserved.</span>
          <span>contact@vairecruiter.ai · Hotline: 1900 1234</span>
        </div>
      </footer>
    </div>
  );
}

function SectionHead({ eyebrow, title, desc, dark, center }) {
  return (
    <div className={`mb-12 max-w-xl ${center ? "mx-auto text-center" : ""}`}>
      <div
        className="inline-flex items-center gap-2 rounded-full px-3.5 py-1.5 text-xs font-semibold mb-4"
        style={dark ? { background: "rgba(255,255,255,0.06)", border: "1px solid rgba(255,255,255,0.12)", color: BRAND.teal } : { background: "white", border: `1px solid ${BRAND.line}`, color: BRAND.tealDark }}
      >
        <span className="w-1.5 h-1.5 rounded-full" style={{ background: BRAND.teal }} />
        {eyebrow}
      </div>
      <h2 className="font-display font-bold text-3xl mb-3" style={{ color: dark ? "white" : BRAND.ink }}>{title}</h2>
      {desc && <p className="text-base leading-relaxed" style={{ color: dark ? "#AEB7C6" : BRAND.muted }}>{desc}</p>}
    </div>
  );
}
