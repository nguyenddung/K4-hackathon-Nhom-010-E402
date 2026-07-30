"""Streamlit UI views with authentication, role-based dashboards (HR Admin vs Candidate), and TOPIKLearn editorial design system."""

import datetime
import html
import json
import uuid

import streamlit as st

from application_service import submit_pdf_application
from ai_service import (
    analyze_jd_and_create_rubric,
    cosine_sim,
    embed_text,
    generate_candidate_feedback,
    generate_interview_questions_and_scorecard,
    parse_and_evaluate_cv_with_evidence,
    pre_screen_candidate_qa,
)
from database import (
    approve_candidate_feedback,
    create_offer,
    create_job,
    create_user,
    enqueue_application,
    get_all_candidates,
    get_all_jobs,
    get_audit_logs,
    get_candidates_by_email,
    get_conn,
    get_job_by_id,
    get_interview_slots,
    get_offer_for_application,
    get_processing_jobs,
    init_db,
    log_audit,
    save_candidate_application,
    save_application_analysis,
    save_candidate_feedback,
    save_interview_data,
    save_interview_scorecard,
    respond_to_offer,
    select_interview_slot,
    send_candidate_feedback,
    set_talent_pool_consent,
    transition_application_status,
    update_job_rubric,
    update_processing_job,
    update_hr_decision,
    update_job_status,
    verify_user_login,
)
from cv_service import PDF_MIME_TYPE, PdfValidationError, persist_pdf, validate_and_parse_pdf
from domain import ApplicationStatus, JobStatus, Role
from job_service import RubricValidationError, validate_rubric
from styles import apply_theme


def render_user_nav_header(user):
    role = user.get("role", "CANDIDATE")
    role_badge_html = f"<span class='role-badge-hr'>🏢 HR ADMIN</span>" if role == "HR" else f"<span class='role-badge-cand'>👤 ỨNG VIÊN</span>"
    safe_name = html.escape(str(user.get("full_name", "")))
    safe_email = html.escape(str(user.get("email", "")))
    nav_items = (
        "Job & Rubric · Hàng đợi CV · HR Review · Feedback · Phỏng vấn"
        if role == Role.HR.value
        else "Việc làm · Hồ sơ của tôi · Feedback · Lịch phỏng vấn"
    )

    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(
            f"""
            <div class="editorial-header" style="border-bottom: none; margin-bottom: 0;">
                <div class="brand-box">
                    <div class="logo-icon">TOPIK</div>
                    <div>
                        <h1 class="brand-title-text">TOPIKLearn <span>TalentScreen AI</span> <span class="korean-sub">토픽학습</span></h1>
                    </div>
                </div>
                <div class="role-nav">{nav_items}</div>
                <div class="user-nav-bar">
                    {role_badge_html}
                    <strong>{safe_name}</strong> ({safe_email})
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col2:
        if st.button("🚪 Đăng xuất", type="secondary"):
            del st.session_state["current_user"]
            st.rerun()
    st.divider()


def render_auth_screen():
    st.markdown(
        """
        <div style="text-align: center; margin-bottom: 2rem;">
            <div class="hero-kicker">※ HELLO TOPIKLEARN · TALENTSCREEN AI V-RECRUITER</div>
            <h1 class="hero-title">Đăng Nhập Nền Tảng <span class="serif-red-italic">Tuyển Dụng AI</span></h1>
            <p class="hero-lead">Vui lòng đăng nhập hoặc đăng ký tài khoản theo đúng Vai trò (HR / Admin hoặc Ứng viên) để trải nghiệm giao diện tương ứng.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown("<div class='wongonji-header'>※ ĐĂNG NHẬP / REGISTRATION</div>", unsafe_allow_html=True)

        mode = st.radio("Thao tác", ["Đăng nhập", "Đăng ký tài khoản mới"], horizontal=True)

        if mode == "Đăng nhập":
            with st.form("login_form"):
                email = st.text_input("Email", placeholder="vd: hr@topiklearn.com hoặc candidate@example.com")
                password = st.text_input("Mật khẩu", type="password", placeholder="Nhập mật khẩu...")
                btn_login = st.form_submit_button("Đăng Nhập", type="primary")

            if btn_login:
                if not email or not password:
                    st.error("Vui lòng nhập đủ Email và Mật khẩu.")
                else:
                    user = verify_user_login(email, password)
                    if user:
                        st.session_state["current_user"] = dict(user)
                        st.success(f"Chào mừng {user['full_name']} ({user['role']})!")
                        st.rerun()
                    else:
                        st.error("Email hoặc mật khẩu không đúng!")

        else:
            with st.form("register_form"):
                r_name = st.text_input("Họ và tên đầy đủ", placeholder="VD: Nguyễn Văn A")
                r_email = st.text_input("Email đăng ký", placeholder="vd: nguyenvana@email.com")
                r_password = st.text_input("Mật khẩu", type="password", placeholder="Nhập mật khẩu...")
                st.caption("Tài khoản tự đăng ký luôn có vai trò Ứng viên. Tài khoản HR do quản trị viên cấp.")
                btn_register = st.form_submit_button("Tạo Tài Khoản Mới", type="primary")

            if btn_register:
                if not r_name or not r_email or not r_password:
                    st.error("Vui lòng điền đủ thông tin đăng ký.")
                else:
                    ok = create_user(r_email, r_password, Role.CANDIDATE.value, r_name)
                    if ok:
                        st.success("🎉 Đăng ký thành công! Hãy chuyển sang tab Đăng nhập để sử dụng tài khoản mới.")
                    else:
                        st.error("Email đã tồn tại trong hệ thống.")

    with col2:
        st.markdown("<div class='wongonji-header'>💡 TÀI KHOẢN DÙNG THỬ CÓ SẴN</div>", unsafe_allow_html=True)

        st.markdown("#### 🏢 HR / Admin (Quản trị viên)")
        st.info("**Email:** `hr@topiklearn.com` | **Mật khẩu:** `123456`\n\n*Quyền hạn: Tạo Job, Duyệt Rubric AI, Chấm CV bằng chứng, Ghi đè điểm HR, Soạn feedback & Khởi tạo bộ câu hỏi phỏng vấn.*")

        st.markdown("#### 👤 Ứng Viên (Candidate / User)")
        st.success("**Email:** `candidate@example.com` | **Mật khẩu:** `123456`\n\n*Quyền hạn: Tìm việc, Hỏi trợ lý AI tư vấn, Nộp CV, Theo dõi tiến độ hồ sơ cá nhân & Xem thư góp ý chỉnh sửa CV.*")



def render_hr_dashboard():
    st.markdown(
        """
        <div style="margin-bottom: 1.5rem;">
            <div class="hero-kicker">※ HR MANAGEMENT WORKSPACE · BẢNG ĐIỀU HÀNH NHÂN SỰ</div>
            <h1 class="hero-title">Quản Lý Tuyển Dụng <span class="serif-red-italic">AI Recruiter</span></h1>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Overview Metrics
    jobs = get_all_jobs()
    candidates = get_all_candidates()

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("Vị Trí Đang Đăng", f"{len(jobs)}")
    with m2:
        st.metric("Tổng Hồ Sơ Nộp", f"{len(candidates)}")
    with m3:
        shortlist_count = len([c for c in candidates if c['stage_status'] in ['SHORTLISTED', 'INTERVIEW_SCHEDULED', 'OFFER_PENDING']])
        st.metric("Ứng Viên Shortlist", f"{shortlist_count}")
    with m4:
        avg_score = sum([c['score'] for c in candidates]) / len(candidates) if candidates else 0
        st.metric("Điểm AI Trung Bình", f"{avg_score:.0f}/100")

    st.divider()

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🏛️ 1. Tạo Job & Rubric",
        "🔍 2. Hàng Đợi & Bằng Chứng",
        "⚖️ 3. HR Review & Audit",
        "✉️ 4. Phản Hồi Cải Thiện CV",
        "🎙️ 5. Lịch Phỏng Vấn & Scorecard"
    ])

    with tab1:
        render_jobs_tab()
    with tab2:
        render_screening_queue_tab()
    with tab3:
        render_hr_review_tab()
    with tab4:
        render_feedback_tab()
    with tab5:
        render_interview_tab()


def render_candidate_dashboard(user):
    safe_name = html.escape(str(user["full_name"]))
    st.markdown(
        f"""
        <div style="margin-bottom: 1.5rem;">
            <div class="hero-kicker">※ CANDIDATE PORTAL · CỔNG THÔNG TIN ỨNG VIÊN</div>
            <h1 class="hero-title">Chào mừng, <span class="serif-red-italic">{safe_name}!</span></h1>
            <p class="hero-lead">Tìm kiếm cơ hội nghề nghiệp phù hợp, hỏi trợ lý AI tư vấn và theo dõi trực tiếp tiến độ hồ sơ ứng tuyển của bạn.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    my_cands = get_candidates_by_email(user["email"])

    st.markdown("### 📋 Hồ Sơ Đã Nộp Của Tôi (My Applications)")
    if my_cands:
        for idx, c in enumerate(my_cands, start=1):
            safe_job_title = html.escape(str(c["job_title"] or "Vị trí không xác định"))
            safe_stage = html.escape(str(c["stage_status"]))
            st.markdown(
                f"""
                <div class="step-card">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <span class="step-num">0{idx}</span>
                            <span class="step-title">{safe_job_title}</span>
                        </div>
                        <div>
                            <span class="stamp-badge">{safe_stage}</span>
                        </div>
                    </div>
                    <p style="color: var(--muted); margin-top: 8px; font-size: 0.9rem;">
                        <strong>Ngày nộp:</strong> {c['created_at'][:10]} | Hồ sơ đang được xử lý theo quy trình tuyển dụng.
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )
            consent_key = f"talent_consent_{c['id']}"
            consent = st.checkbox(
                "Cho phép lưu hồ sơ vào Talent Pool nếu chưa phù hợp Job này",
                value=bool(c["talent_pool_consent"]),
                key=consent_key,
            )
            if consent != bool(c["talent_pool_consent"]):
                set_talent_pool_consent(c["id"], consent, candidate_email=user["email"])
                st.rerun()
            if c["stage_status"] == ApplicationStatus.OFFER_PENDING.value:
                offer = get_offer_for_application(c["id"])
                if offer:
                    st.info(f"**Offer:** {offer['salary']}\n\n{offer['conditions'] or ''}")
                    accept_col, decline_col = st.columns(2)
                    with accept_col:
                        if st.button("Chấp Nhận Offer", key=f"accept_offer_{c['id']}", type="primary"):
                            respond_to_offer(c["id"], ApplicationStatus.OFFER_ACCEPTED.value, candidate_email=user["email"])
                            st.rerun()
                    with decline_col:
                        if st.button("Từ Chối Offer", key=f"decline_offer_{c['id']}", type="secondary"):
                            respond_to_offer(c["id"], ApplicationStatus.OFFER_DECLINED.value, candidate_email=user["email"])
                            st.rerun()
    else:
        st.info("Bạn chưa nộp hồ sơ vào vị trí tuyển dụng nào. Hãy tham khảo các vị trí bên dưới và nộp CV ngay!")

    st.divider()

    c_tab1, c_tab2, c_tab3 = st.tabs([
        "💼 1. Tìm Việc & Nộp CV",
        "✉️ 2. Xem Thư Góp Ý Cải Thiện CV",
        "🎙️ 3. Lịch Phỏng Vấn Của Tôi"
    ])

    with c_tab1:
        render_candidate_portal_tab_for_user(user)

    with c_tab2:
        render_candidate_feedback_view(user, my_cands)

    with c_tab3:
        render_candidate_interview_view(user, my_cands)


def render_candidate_portal_tab_for_user(user):
    jobs = get_all_jobs(published_only=True)
    if not jobs:
        st.info("Hiện chưa có vị trí tuyển dụng nào mở.")
        return

    job_options = {f"{j['title']} ({j['level']})": j["id"] for j in jobs}
    selected_name = st.selectbox("Chọn vị trí công việc muốn ứng tuyển", list(job_options.keys()))
    job_id = job_options[selected_name]
    job = get_job_by_id(job_id)

    safe_job_title = html.escape(str(job["title"]))
    st.markdown(f"### {safe_job_title} <span class='stamp-badge'>TUYỂN DỤNG</span>", unsafe_allow_html=True)
    salary_text = job["salary"] if job["salary_public"] else "Trao đổi khi phỏng vấn"
    st.write(f"**Cấp bậc:** {job['level']} | **Mức lương:** {salary_text} | **Hạn nộp:** {job['deadline'] or job['timeline']}")
    st.write(f"**Địa điểm:** {job['location'] or 'Trao đổi'} | **Hình thức:** {job['work_mode']} | **Kinh nghiệm:** {job['experience_years']} năm")
    st.write(f"**Kỹ năng bắt buộc:** `{job['mandatory_skills']}`")
    st.write(f"**Kỹ năng ưu tiên:** `{job['preferred_skills']}`")
    st.markdown("**Mô tả vị trí:**")
    st.write(job["description"])
    if job["responsibilities"]:
        st.markdown("**Trách nhiệm chính:**")
        st.write(job["responsibilities"])
    if job["interview_process"]:
        st.markdown("**Quy trình phỏng vấn:**")
        st.write(job["interview_process"])

    st.markdown("#### 🤖 Hỏi Trợ Lý AI: 'Tôi có phù hợp với vị trí này không?'")
    qa_col1, qa_col2 = st.columns([3, 1])
    with qa_col1:
        cand_question = st.text_input("Nhập thắc mắc...", placeholder="Ví dụ: Vị trí này yêu cầu số năm kinh nghiệm tối thiểu là bao nhiêu?")
    with qa_col2:
        btn_qa = st.button("Hỏi AI Recruiter")

    if btn_qa and cand_question:
        with st.spinner("AI đang tư vấn dựa trên JD..."):
            ans = pre_screen_candidate_qa(job["title"], job["description"], cand_question)
            st.info(f"**Trả lời từ AI Recruiter:**\n\n{ans}")

    st.divider()
    st.markdown("#### 📄 Form Nộp CV Ứng Tuyển")
    with st.form("cand_cv_submission_form"):
        c_name = st.text_input("Họ và tên ứng viên", value=user["full_name"])
        c_email = st.text_input("Email liên hệ", value=user["email"], disabled=True)
        c_portfolio = st.text_input("Portfolio / GitHub / LinkedIn Link", placeholder="https://github.com/username")
        uploaded_cv = st.file_uploader(
            "CV dạng PDF",
            type=["pdf"],
            help="Chỉ nhận PDF không mật khẩu, tối đa 8 MB và 20 trang.",
        )
        c_start = st.text_input("Thời gian có thể bắt đầu", placeholder="VD: Sau 30 ngày")
        c_work_preference = st.selectbox("Mong muốn làm việc", ["Theo mô tả Job", "Onsite", "Hybrid", "Remote"])
        c_screening_answer = st.text_area(
            "Thông tin bổ sung cho HR",
            placeholder="Nêu ngắn gọn lý do phù hợp hoặc câu trả lời sàng lọc.",
            height=100,
        )

        btn_submit_cv = st.form_submit_button("Nộp CV PDF", type="primary")

    if btn_submit_cv:
        if uploaded_cv is None:
            st.error("Vui lòng chọn một file CV PDF.")
        else:
            try:
                pdf_bytes = uploaded_cv.getvalue()
                parsed = validate_and_parse_pdf(uploaded_cv.name, uploaded_cv.type, pdf_bytes)
                cand_id = str(uuid.uuid4())
                stored_path = persist_pdf(cand_id, uploaded_cv.name, pdf_bytes)
                save_candidate_application(
                    candidate_id=cand_id,
                    job_id=job_id,
                    name=c_name,
                    email=user["email"],
                    cv_text=parsed.text,
                    portfolio_link=c_portfolio,
                    embedding="[]",
                    score=0,
                    mandatory_flags=[],
                    evidence_json=[],
                    missing_gaps_json=[],
                    parser_confidence=parsed.parser_confidence,
                    routing_recommendation="HUMAN_REVIEW",
                    stage_status=ApplicationStatus.SUBMITTED.value,
                    cv_file_path=stored_path,
                    cv_file_name=uploaded_cv.name,
                    cv_mime_type=PDF_MIME_TYPE,
                    cv_sha256=parsed.sha256,
                    cv_size_bytes=parsed.size_bytes,
                    parse_status=parsed.parse_status,
                    page_count=parsed.page_count,
                    submitted_answers={"candidate_note": c_screening_answer},
                    start_availability=c_start,
                    work_preference=c_work_preference,
                    actor_user_id=user.get("id"),
                    actor_role=Role.CANDIDATE.value,
                )
                enqueue_application(cand_id)
                transition_application_status(
                    cand_id,
                    ApplicationStatus.QUEUED.value,
                    actor_user_id=None,
                    actor_role=Role.AGENT.value,
                    reason="CV PDF hợp lệ đã vào hàng đợi",
                )
                update_processing_job(cand_id, "PROCESSING")
                transition_application_status(
                    cand_id,
                    ApplicationStatus.PROCESSING.value,
                    actor_user_id=None,
                    actor_role=Role.AGENT.value,
                    reason="Agent bắt đầu phân tích CV PDF",
                )

                if parsed.parse_status == "PARSED":
                    job_emb = json.loads(job["embedding"]) if job["embedding"] else embed_text(job["description"])
                    cv_emb = embed_text(parsed.text)
                    sim = cosine_sim(job_emb, cv_emb)
                    rubric = json.loads(job["rubric_json"]) if job["rubric_json"] else []
                    eval_res = parse_and_evaluate_cv_with_evidence(
                        job["title"], job["description"], rubric, parsed.text, sim
                    )
                    save_application_analysis(
                        cand_id,
                        embedding=json.dumps(cv_emb),
                        score=eval_res.get("score", 0),
                        mandatory_flags=eval_res.get("mandatory_flags", []),
                        evidence=eval_res.get("evidence_scorecard", []),
                        gaps=eval_res.get("gaps", []),
                        parser_confidence=parsed.parser_confidence,
                        routing_recommendation=eval_res.get("routing_recommendation", "HUMAN_REVIEW"),
                    )
                    queue_result = "COMPLETED"
                else:
                    save_application_analysis(
                        cand_id,
                        embedding="[]",
                        score=0,
                        mandatory_flags=["PARSER_CONFIDENCE_LOW"],
                        evidence=[],
                        gaps=["PDF có thể là bản scan; cần HR kiểm tra thủ công hoặc yêu cầu tải lại."],
                        parser_confidence=parsed.parser_confidence,
                        routing_recommendation="HUMAN_REVIEW",
                    )
                    queue_result = "MANUAL_REVIEW"

                for next_status in (ApplicationStatus.ANALYZED, ApplicationStatus.HR_REVIEW_PENDING):
                    transition_application_status(
                        cand_id,
                        next_status.value,
                        actor_user_id=None,
                        actor_role=Role.AGENT.value,
                        reason="Hoàn tất bước phân tích; chuyển HR kiểm tra",
                    )
                update_processing_job(cand_id, queue_result)
                st.success("✅ CV PDF đã được tiếp nhận. HR sẽ kiểm tra hồ sơ và phản hồi theo trạng thái hiển thị.")
                st.balloons()
                st.rerun()
            except PdfValidationError as exc:
                st.error(str(exc))
            except Exception as exc:
                if "cand_id" in locals():
                    try:
                        update_processing_job(cand_id, "FAILED", error=str(exc))
                    except Exception:
                        pass
                st.error(f"Không thể xử lý CV lúc này: {exc}")


def render_candidate_feedback_view(user, my_cands):
    st.markdown("### ✉️ Thư Phản Hồi Góp Ý Cải Thiện CV")
    if not my_cands:
        st.info("Chưa có thông tin phản hồi.")
        return

    c_with_fb = [
        c for c in my_cands
        if c["feedback_json"] and c["feedback_status"] == "FEEDBACK_SENT"
    ]
    if not c_with_fb:
        st.info("Hiện tại chưa có thư nhận xét góp ý mới cho hồ sơ của bạn.")
        return

    for c in c_with_fb:
        fb = json.loads(c["feedback_json"])
        st.markdown(f"### ✉️ Nhận Xét Góp Ý CV — Vị Trí: {c['job_title']}", unsafe_allow_html=True)

        st.markdown("**1. Điểm bạn đã đáp ứng tốt:**")
        for m in fb.get("matched_points", []):
            st.write(f"- ✓ {m}")

        st.markdown("**2. Điểm cần làm rõ / nâng cấp:**")
        for g in fb.get("missing_points", []):
            st.write(f"- ⚠️ {g}")

        st.info(f"**Lời khuyên từ Chuyên Gia Tuyển Dụng:**\n\n{fb.get('improvement_advice')}")

        st.markdown("#### 💡 Gợi Ý Chỉnh Sửa CV (Trước vs Sau):")
        col_b, col_a = st.columns(2)
        with col_b:
            st.error(f"**Trước khi sửa:**\n\n*{fb.get('before_example')}*")
        with col_a:
            st.success(f"**Sau khi sửa (Chuẩn ăn điểm):**\n\n*{fb.get('after_example')}*")

        if c["stage_status"] == ApplicationStatus.NEED_MORE_INFORMATION.value:
            st.markdown("#### Nộp lại CV PDF sau khi cải thiện")
            revised_pdf = st.file_uploader(
                "Chọn CV PDF phiên bản mới",
                type=["pdf"],
                key=f"revision_pdf_{c['id']}",
            )
            if st.button("Nộp Lại CV PDF", key=f"submit_revision_{c['id']}", type="primary"):
                if revised_pdf is None:
                    st.error("Vui lòng chọn file PDF phiên bản mới.")
                else:
                    try:
                        job = get_job_by_id(c["job_id"])
                        submit_pdf_application(
                            user=user,
                            job=job,
                            candidate_name=user["full_name"],
                            filename=revised_pdf.name,
                            mime_type=revised_pdf.type,
                            content=revised_pdf.getvalue(),
                            portfolio_link=c["portfolio_link"] or "",
                            start_availability=c["start_availability"] or "",
                            work_preference=c["work_preference"] or "Theo mô tả Job",
                            revision_of_id=c["id"],
                        )
                        st.success("Đã nộp CV PDF phiên bản mới để Agent đánh giá lại.")
                        st.rerun()
                    except (PdfValidationError, ValueError, PermissionError) as exc:
                        st.error(str(exc))



def render_candidate_interview_view(user, my_cands):
    st.markdown("### 🎙️ Lịch Phỏng Vấn Của Tôi")
    c_inv = [c for c in my_cands if c["interview_slots_json"]]

    if not c_inv:
        st.info("Chưa có lịch phỏng vấn nào được xếp.")
        return

    for c in c_inv:
        slots = get_interview_slots(c["id"])
        st.markdown(f"### 📅 Thư Mời Phỏng Vấn — Vị Trí: {c['job_title']} <span class='stamp-badge'>SHORTLISTED</span>", unsafe_allow_html=True)
        for s in slots:
            st.write(f"**Thời gian:** `{s['starts_at']}` | **Hình thức:** {s['format']} | **Interviewer:** {s['interviewer']}")
        if c["stage_status"] == ApplicationStatus.INTERVIEW_INVITED.value:
            available = [s for s in slots if not s["selected_at"]]
            if available:
                slot_map = {
                    f"{s['starts_at']} · {s['format']} · {s['interviewer']}": s["id"]
                    for s in available
                }
                chosen = st.selectbox("Chọn khung giờ", list(slot_map), key=f"slot_{c['id']}")
                if st.button("Xác Nhận Lịch Phỏng Vấn", key=f"choose_slot_{c['id']}", type="primary"):
                    try:
                        select_interview_slot(c["id"], slot_map[chosen], candidate_email=user["email"])
                        st.success("Đã xác nhận lịch phỏng vấn.")
                        st.rerun()
                    except (ValueError, PermissionError) as exc:
                        st.error(str(exc))
        elif c["selected_interview_slot_id"]:
            st.success("Bạn đã xác nhận lịch phỏng vấn này.")


# Keep remaining admin tab render functions intact
def render_jobs_tab():
    st.markdown("### 🏛️ Tab 1: Tạo Vị Trí Tuyển Dụng & Duyệt Rubric AI")
    st.caption("Khởi tạo JD, phát hiện các cụm từ mơ hồ và phê duyệt Rubric đánh giá có trọng số trước khi đăng tuyển.")

    with st.form("job_create_form"):
        col1, col2 = st.columns(2)
        with col1:
            title = st.text_input("Tên vị trí tuyển dụng", placeholder="VD: Senior Backend Engineer (Python/FastAPI)")
            level = st.selectbox("Cấp bậc", ["Fresher/Junior", "Middle", "Senior", "Lead/Manager"])
            experience_years = st.number_input("Số năm kinh nghiệm", min_value=0.0, max_value=30.0, step=0.5)
            location = st.text_input("Địa điểm", placeholder="VD: Hà Nội")
            work_mode = st.selectbox("Hình thức làm việc", ["Onsite", "Hybrid", "Remote"])
            salary = st.text_input("Mức lương", value="Thỏa thuận (Up to 3,000 USD)")
            salary_public = st.checkbox("Công khai mức lương")
        with col2:
            mandatory_skills = st.text_input("Kỹ năng bắt buộc (cách nhau bởi phẩy)", placeholder="VD: Python, REST API, SQL")
            preferred_skills = st.text_input("Kỹ năng ưu tiên", placeholder="VD: Docker, Kubernetes, AWS")
            timeline = st.text_input("Hạn nộp & Thời gian tuyển", value="30 ngày")
            deadline = st.date_input("Ngày hết hạn")
            headcount = st.number_input("Số lượng cần tuyển", min_value=1, max_value=100, value=1)

        description = st.text_area("Mô tả công việc (JD đầy đủ)", height=180, placeholder="Dán nội dung JD công việc vào đây...")
        responsibilities = st.text_area("Trách nhiệm chính", height=100)
        interview_process = st.text_area("Quy trình phỏng vấn", height=100, placeholder="VD: HR Screening → Technical → Final")

        btn_analyze = st.form_submit_button("1. Phân Tích JD & Tạo Rubric AI", type="primary")

    if btn_analyze:
        if not title or not description:
            st.error("Vui lòng điền đủ Tên vị trí và Mô tả công việc.")
        else:
            with st.spinner("AI đang phân tích JD & phát hiện tiêu chí mơ hồ..."):
                analysis = analyze_jd_and_create_rubric(title, description)
                actor = st.session_state.get("current_user", {})
                job_id = str(uuid.uuid4())
                create_job(
                    job_id=job_id,
                    title=title,
                    description=description,
                    level=level,
                    mandatory_skills=mandatory_skills,
                    preferred_skills=preferred_skills,
                    salary=salary,
                    timeline=timeline,
                    embedding=json.dumps(embed_text(description)),
                    rubric_json=json.dumps(analysis.get("rubric", []), ensure_ascii=False),
                    vague_warnings_json=json.dumps(analysis.get("vague_warnings", []), ensure_ascii=False),
                    status=JobStatus.DRAFT.value,
                    responsibilities=responsibilities,
                    experience_years=experience_years,
                    location=location,
                    work_mode=work_mode,
                    interview_process=interview_process,
                    deadline=str(deadline),
                    headcount=int(headcount),
                    salary_public=salary_public,
                    actor_user_id=actor.get("id"),
                    actor_role=actor.get("role", Role.HR.value),
                )
                st.session_state["draft_analysis"] = analysis
                st.session_state["draft_job_id"] = job_id
                st.rerun()

    if "draft_analysis" in st.session_state and "draft_job_id" in st.session_state:
        analysis = st.session_state["draft_analysis"]
        draft_job = get_job_by_id(st.session_state["draft_job_id"])

        st.markdown("<div class='wongonji-header'>※ PHÂN TÍCH JD & CẢNH BÁO TIÊU CHÍ MƠ HỒ (VAGUE WARNINGS)</div>", unsafe_allow_html=True)

        vague_list = analysis.get("vague_warnings", [])
        if vague_list:
            for v in vague_list:
                st.warning(f"**Cảnh báo mơ hồ:** {v.get('vague_phrase')} \n👉 **Gợi ý đo lường được:** {v.get('suggestion')}")
        else:
            st.success("✓ JD có cấu trúc rõ ràng, không phát hiện tiêu chí mơ hồ gây nhiễu!")

        st.markdown("#### 📊 Rubric Đánh Giá CV (7 Phần Có Trọng Số)")
        rubric_data = analysis.get("rubric", [])
        edited = st.data_editor(rubric_data, width="stretch", num_rows="dynamic", key="rubric_editor")
        edited_records = edited.to_dict("records") if hasattr(edited, "to_dict") else edited
        st.caption(f"Trạng thái hiện tại: {draft_job['status']}")
        actor = st.session_state.get("current_user", {})
        try:
            if draft_job["status"] == JobStatus.DRAFT.value:
                if st.button("2. Lưu Rubric & Chuyển Sang Review", type="primary"):
                    clean_rubric = validate_rubric(edited_records)
                    update_job_rubric(draft_job["id"], clean_rubric, actor_user_id=actor.get("id"), actor_role=actor.get("role", Role.HR.value))
                    update_job_status(draft_job["id"], JobStatus.RUBRIC_REVIEW.value, actor_user_id=actor.get("id"), actor_role=actor.get("role", Role.HR.value), reason="HR gửi rubric sang bước review")
                    st.session_state["draft_analysis"]["rubric"] = clean_rubric
                    st.rerun()
            elif draft_job["status"] == JobStatus.RUBRIC_REVIEW.value:
                if st.button("3. Phê Duyệt Rubric", type="primary"):
                    clean_rubric = validate_rubric(edited_records)
                    update_job_rubric(draft_job["id"], clean_rubric, actor_user_id=actor.get("id"), actor_role=actor.get("role", Role.HR.value))
                    update_job_status(draft_job["id"], JobStatus.APPROVED.value, actor_user_id=actor.get("id"), actor_role=actor.get("role", Role.HR.value), reason="HR phê duyệt rubric tổng trọng số 100%")
                    st.rerun()
            elif draft_job["status"] == JobStatus.APPROVED.value:
                if st.button("4. Đăng Tuyển", type="primary"):
                    update_job_status(draft_job["id"], JobStatus.PUBLISHED.value, actor_user_id=actor.get("id"), actor_role=actor.get("role", Role.HR.value), reason="HR đăng tuyển Job đã duyệt")
                    st.success(f"🎉 Đã đăng tuyển vị trí {draft_job['title']}.")
                    del st.session_state["draft_analysis"]
                    del st.session_state["draft_job_id"]
                    st.rerun()
        except (RubricValidationError, ValueError) as exc:
            st.error(str(exc))


    st.divider()
    st.markdown("### 📋 Danh Sách Vị Trí Tuyển Dụng Đã Đăng")
    jobs = get_all_jobs()
    if jobs:
        for idx, job in enumerate(jobs, start=1):
            safe_title = html.escape(str(job["title"] or "Chưa đặt tên"))
            safe_level = html.escape(str(job["level"] or "Chưa xác định"))
            safe_salary = html.escape(str(job["salary"] or "Thỏa thuận"))
            safe_status = html.escape(str(job["status"] or "UNKNOWN"))
            safe_skills = html.escape(str(job["mandatory_skills"] or "Chưa cập nhật"))
            st.markdown(
                f"""
                <div class="step-card">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <span class="step-num">0{idx}</span>
                            <span class="step-title">{safe_title}</span>
                            <span class="mono-chip" style="margin-left: 10px;">{safe_level}</span>
                            <span class="mono-chip">{safe_salary}</span>
                        </div>
                        <div>
                            <span class="stamp-badge">{safe_status}</span>
                        </div>
                    </div>
                    <p style="color: var(--muted); margin-top: 8px; font-size: 0.9rem;">
                        <strong>Kỹ năng cốt lõi:</strong> {safe_skills} |
                        <strong>Ngày đăng:</strong> {job['created_at'][:10]}
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )

            with st.expander(f"🔎 Xem chi tiết — {job['title']}"):
                detail_col1, detail_col2, detail_col3 = st.columns(3)
                detail_col1.write(f"**Cấp bậc:** {job['level'] or 'Chưa cập nhật'}")
                detail_col1.write(f"**Kinh nghiệm:** {job['experience_years'] or 0} năm")
                detail_col1.write(f"**Số lượng:** {job['headcount'] or 1}")
                detail_col2.write(f"**Địa điểm:** {job['location'] or 'Chưa cập nhật'}")
                detail_col2.write(f"**Hình thức:** {job['work_mode'] or 'Chưa cập nhật'}")
                detail_col2.write(f"**Hạn nộp:** {job['deadline'] or job['timeline'] or 'Chưa cập nhật'}")
                detail_col3.write(f"**Mức lương:** {job['salary'] or 'Thỏa thuận'}")
                detail_col3.write(f"**Công khai lương:** {'Có' if job['salary_public'] else 'Không'}")
                detail_col3.write(f"**Trạng thái:** {job['status']}")

                st.markdown("#### Mô tả công việc")
                st.write(job["description"] or "Chưa có mô tả.")
                st.markdown("#### Trách nhiệm chính")
                st.write(job["responsibilities"] or "Chưa cập nhật.")
                st.write(f"**Kỹ năng bắt buộc:** {job['mandatory_skills'] or 'Chưa cập nhật'}")
                st.write(f"**Kỹ năng ưu tiên:** {job['preferred_skills'] or 'Chưa cập nhật'}")
                st.write(f"**Quy trình phỏng vấn:** {job['interview_process'] or 'Chưa cập nhật'}")

                try:
                    rubric = json.loads(job["rubric_json"] or "[]")
                except (TypeError, json.JSONDecodeError):
                    rubric = []
                st.markdown("#### Rubric đánh giá")
                if rubric:
                    st.dataframe(rubric, width="stretch", hide_index=True)
                else:
                    st.info("Job này chưa có rubric đánh giá.")


def render_screening_queue_tab():
    st.markdown("### 🔍 Tab 2: Hàng Đợi Xử Lý CV & Evidence Scorecard")
    st.caption("Xem đánh giá 2 lớp của Agent: Kiểm tra yêu cầu bắt buộc (Layer 1) & Chấm điểm trích dẫn BẰNG CHỨNG THỰC TẾ (Layer 2).")

    queue = get_processing_jobs()
    if queue:
        st.dataframe(
            [
                {
                    "Ứng viên": item["candidate_name"],
                    "Job": item["job_title"],
                    "Queue": item["status"],
                    "Hồ sơ": item["stage_status"],
                    "Parser": f"{item['parser_confidence'] * 100:.0f}%",
                    "Routing": item["routing_recommendation"],
                    "Retry": item["retry_count"],
                }
                for item in queue
            ],
            width="stretch",
            hide_index=True,
        )
    candidates = get_all_candidates()
    if not candidates:
        st.info("Chưa có CV nào được nộp vào hàng đợi.")
        return

    c_map = {f"{c['name']} - Job: {c['job_title']} (Điểm: {c['score']:.0f}/100)" : c["id"] for c in candidates}
    selected_c_key = st.selectbox("Chọn hồ sơ ứng viên trong hàng đợi", list(c_map.keys()))
    cand_id = c_map[selected_c_key]
    cand = next(c for c in candidates if c["id"] == cand_id)

    st.markdown(f"## Ứng Viên: {cand['name']} <span class='stamp-badge'>{cand['stage_status']}</span>", unsafe_allow_html=True)
    st.write(f"**Email:** {cand['email'] or 'N/A'} | **Portfolio:** {cand['portfolio_link'] or 'N/A'}")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Điểm Phù Hợp AI", f"{cand['score']:.0f} / 100")
    with col2:
        st.metric("Độ Tin Cậy Parser", f"{cand['parser_confidence']*100:.0f}%")
    with col3:
        st.markdown(f"**Đề Xuất Routing:**\n<span class='stamp-badge'>{cand['routing_recommendation']}</span>", unsafe_allow_html=True)

    mandatory_flags = json.loads(cand["mandatory_flags"]) if cand["mandatory_flags"] else []
    st.markdown("#### 🚩 Layer 1: Kiểm Tra Điều Kiện Bắt Buộc")
    if mandatory_flags:
        for flag in mandatory_flags:
            st.error(f"⚠️ {flag}")
    else:
        st.success("✓ Đạt toàn bộ các điều kiện công việc bắt buộc cốt lõi.")

    st.markdown("#### 📜 Layer 2: Trích Dẫn Bằng Chứng Thực Tế Từ CV (Evidence Scorecard)")
    evidence_list = json.loads(cand["evidence_json"]) if cand["evidence_json"] else []
    if evidence_list:
        for item in evidence_list:
            st.markdown(
                f"""
                <div style="background: #FFFFFF; border: 1px solid var(--line); border-left: 4px solid var(--red); padding: 12px; margin-bottom: 10px; border-radius: 4px;">
                    <div style="display: flex; justify-content: space-between;">
                        <strong>{item.get('criterion')}</strong>
                        <span class="mono-chip">Điểm: {item.get('score')}/{item.get('max_score', 5)} (Độ tin cậy: {int(item.get('confidence', 0.9)*100)}%)</span>
                    </div>
                    <p style="margin: 6px 0; color: var(--ink);">
                        <strong>Bằng chứng CV:</strong> <span class="wavy-underline">"{item.get('evidence_quote')}"</span>
                    </p>
                    <p style="margin: 0; color: var(--red); font-size: 0.85rem;">
                        <strong>Điểm thiếu sót:</strong> {item.get('missing_gap')}
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )



def render_hr_review_tab():
    st.markdown("### ⚖️ Tab 3: HR Review & Nhật Ký Phê Duyệt (Human-in-the-Loop)")
    candidates = get_all_candidates()
    if not candidates:
        st.info("Chưa có ứng viên nào để đánh giá.")
        return

    c_map = {f"{c['name']} - {c['job_title']} (Trạng thái: {c['stage_status']})" : c["id"] for c in candidates}
    selected_key = st.selectbox("Chọn ứng viên phê duyệt", list(c_map.keys()))
    cand_id = c_map[selected_key]
    cand = next(c for c in candidates if c["id"] == cand_id)

    col_cv, col_eval = st.columns(2)
    with col_cv:
        st.markdown("### 📄 CV Gốc Của Ứng Viên")
        st.text_area("Nội dung CV", value=cand["cv_text"], height=400, disabled=True)

    with col_eval:
        st.markdown("### ⚖️ Quyết Định Của HR")
        st.write(f"**Điểm gợi ý từ Agent:** `{cand['score']:.0f} / 100`")

        evidence = json.loads(cand["evidence_json"]) if cand["evidence_json"] else []
        criterion_rows = [
            {
                "criterion": item.get("criterion", "Tiêu chí"),
                "agent_score": float(item.get("score", 0)),
                "hr_score": float(item.get("score", 0)),
                "evidence": item.get("evidence_quote", ""),
                "hr_reason": "",
            }
            for item in evidence
        ]
        edited_scores = st.data_editor(
            criterion_rows,
            width="stretch",
            disabled=["criterion", "agent_score", "evidence"],
            key=f"criterion_scores_{cand_id}",
        )
        score_records = edited_scores.to_dict("records") if hasattr(edited_scores, "to_dict") else edited_scores

        with st.form("hr_decision_form"):
            hr_score = st.slider("Điểm HR đánh giá lại (0 - 100)", min_value=0, max_value=100, value=int(cand['score']))
            decision = st.selectbox(
                "Quyết định tuyển dụng HR",
                ["SHORTLISTED (Duyệt phỏng vấn)", "NEED_MORE_INFORMATION (Yêu cầu bổ sung)", "TALENT_POOL (Lưu kho tiềm năng)", "NOT_PROCEEDING (Từ chối)"]
            )
            hr_note = st.text_area("Lý do HR đánh giá / Ghi chú kiểm toán", placeholder="Nhập lý do điều chỉnh...")
            st.caption(
                "Nếu thay đổi điểm Agent hoặc chọn Từ chối, hãy nhập lý do rồi bấm "
                "“Lưu Quyết Định & Ghi Log”. Việc nhập nội dung chưa tự động gửi form."
            )
            btn_save_hr = st.form_submit_button("Lưu Quyết Định & Ghi Log", type="primary")

        if btn_save_hr:
            dec_clean = decision.split(" ")[0]
            actor = st.session_state.get("current_user", {})
            try:
                update_hr_decision(
                    cand_id,
                    dec_clean,
                    hr_score,
                    cand['score'],
                    hr_note,
                    dec_clean,
                    criterion_scores=score_records,
                    actor_user_id=actor.get("id"),
                    actor_role=actor.get("role", Role.HR.value),
                )
                st.success("✅ Đã lưu quyết định HR thành công!")
                st.rerun()
            except ValueError as exc:
                st.error(str(exc))


    logs = get_audit_logs(cand_id, limit=50)
    if logs:
        st.markdown("#### Nhật ký trạng thái và quyết định")
        st.dataframe(
            [
                {
                    "Thời gian": log["created_at"],
                    "Actor": log["actor_role"] or "SYSTEM",
                    "Hành động": log["action"],
                    "Từ": log["from_status"],
                    "Sang": log["to_status"],
                    "Chi tiết": log["detail"],
                }
                for log in logs
            ],
            width="stretch",
            hide_index=True,
        )


def render_feedback_tab():
    st.markdown("### ✉️ Tab 4: Phản Hồi Cải Thiện CV Cho Ứng Viên")
    candidates = get_all_candidates()
    if not candidates:
        st.info("Chưa có dữ liệu ứng viên.")
        return

    c_map = {f"{c['name']} - Job: {c['job_title']}" : c["id"] for c in candidates}
    selected_key = st.selectbox("Chọn ứng viên gửi phản hồi", list(c_map.keys()))
    cand_id = c_map[selected_key]
    cand = next(c for c in candidates if c["id"] == cand_id)
    job = get_job_by_id(cand["job_id"])

    if st.button("✨ Soạn Thư Phản Hồi Góp Ý CV Bằng AI", type="primary"):
        with st.spinner("AI đang soạn thư góp ý..."):
            eval_dict = {"strengths": json.loads(cand["evidence_json"]) if cand["evidence_json"] else [], "gaps": json.loads(cand["missing_gaps_json"]) if cand["missing_gaps_json"] else []}
            fb = generate_candidate_feedback(job["title"], job["description"], cand["cv_text"], eval_dict)
            actor = st.session_state.get("current_user", {})
            save_candidate_feedback(
                cand_id,
                fb,
                actor_user_id=actor.get("id"),
                actor_role=actor.get("role", Role.HR.value),
            )
            st.success("Đã tạo thư phản hồi góp ý!")
            st.rerun()

    if cand["feedback_json"]:
        fb = json.loads(cand["feedback_json"])
        st.markdown(f"### ✉️ Mẫu Thư Phản Hồi Góp Ý - Ứng Viên: {cand['name']}", unsafe_allow_html=True)
        st.caption(f"Trạng thái: {cand['feedback_status']}")
        if cand["feedback_status"] == "FEEDBACK_GENERATED":
            with st.form(f"approve_feedback_{cand_id}"):
                matched_text = st.text_area("Điểm đã đáp ứng", value="\n".join(fb.get("matched_points", [])))
                missing_text = st.text_area("Điểm còn thiếu", value="\n".join(fb.get("missing_points", [])))
                advice = st.text_area("Lời khuyên", value=fb.get("improvement_advice", ""))
                before = st.text_area("Ví dụ trước", value=fb.get("before_example", ""))
                after = st.text_area("Ví dụ sau", value=fb.get("after_example", ""))
                approve = st.form_submit_button("HR Duyệt Feedback", type="primary")
            if approve:
                actor = st.session_state.get("current_user", {})
                approved_fb = {
                    "matched_points": [x.strip() for x in matched_text.splitlines() if x.strip()],
                    "missing_points": [x.strip() for x in missing_text.splitlines() if x.strip()],
                    "improvement_advice": advice.strip(),
                    "before_example": before.strip(),
                    "after_example": after.strip(),
                }
                approve_candidate_feedback(cand_id, approved_fb, actor_user_id=actor.get("id"), actor_role=actor.get("role", Role.HR.value))
                st.rerun()
        elif cand["feedback_status"] == "HR_APPROVED_FEEDBACK":
            st.info(f"**Lời khuyên đã duyệt:** {fb.get('improvement_advice')}")
            if st.button("Gửi Feedback Cho Ứng Viên", key=f"send_feedback_{cand_id}", type="primary"):
                actor = st.session_state.get("current_user", {})
                send_candidate_feedback(cand_id, actor_user_id=actor.get("id"), actor_role=actor.get("role", Role.HR.value))
                st.rerun()
        else:
            st.success("Feedback đã gửi cho ứng viên.")
            st.info(f"**Lời khuyên:** {fb.get('improvement_advice')}")


def render_interview_tab():
    st.markdown("### 🎙️ Tab 5: Lịch Phỏng Vấn & Bộ Câu Hỏi 5 Cấp Độ")
    candidates = get_all_candidates()
    interview_stages = {
        ApplicationStatus.SHORTLISTED.value,
        ApplicationStatus.INTERVIEW_INVITED.value,
        ApplicationStatus.INTERVIEW_SCHEDULED.value,
        ApplicationStatus.INTERVIEW_COMPLETED.value,
        ApplicationStatus.SCORECARD_PENDING.value,
        ApplicationStatus.INTERVIEWER_SUBMITTED.value,
        ApplicationStatus.AGENT_SUMMARIZED.value,
        ApplicationStatus.NEXT_ROUND.value,
        ApplicationStatus.ASSESSMENT_REQUIRED.value,
        ApplicationStatus.OFFER_PENDING.value,
    }
    shortlisted = [c for c in candidates if c["stage_status"] in interview_stages]
    if not shortlisted:
        st.info("Chưa có ứng viên Shortlist.")
        return

    c_map = {f"{c['name']} - {c['job_title']}" : c["id"] for c in shortlisted}
    selected_key = st.selectbox("Chọn ứng viên phỏng vấn", list(c_map.keys()))
    cand_id = c_map[selected_key]
    cand = next(c for c in shortlisted if c["id"] == cand_id)
    job = get_job_by_id(cand["job_id"])

    if cand["stage_status"] in {
        ApplicationStatus.SHORTLISTED.value,
        ApplicationStatus.NEXT_ROUND.value,
    }:
        with st.form(f"interview_setup_{cand_id}"):
            interview_date = st.date_input("Ngày phỏng vấn", key=f"date_{cand_id}")
            interview_time = st.time_input("Giờ phỏng vấn", key=f"time_{cand_id}")
            interview_format = st.selectbox("Hình thức", ["Online", "Offline"], key=f"format_{cand_id}")
            interviewer = st.text_input("Interviewer", value="Tech Lead", key=f"interviewer_{cand_id}")
            meeting_link = st.text_input("Meeting link / địa chỉ", key=f"meeting_{cand_id}")
            create_interview = st.form_submit_button("Tạo Câu Hỏi & Gửi Lời Mời", type="primary")
        if create_interview:
            with st.spinner("AI đang tạo bộ câu hỏi..."):
                eval_dict = {"gaps": json.loads(cand["missing_gaps_json"]) if cand["missing_gaps_json"] else []}
                q_data = generate_interview_questions_and_scorecard(job["title"], job["description"], cand["cv_text"], eval_dict)
                slots = [{
                    "starts_at": f"{interview_date}T{interview_time.isoformat()}",
                    "format": interview_format,
                    "interviewer": interviewer,
                    "meeting_link": meeting_link,
                }]
                actor = st.session_state.get("current_user", {})
                save_interview_data(cand_id, q_data, slots, actor_user_id=actor.get("id"), actor_role=actor.get("role", Role.HR.value))
                st.success("Đã gửi lời mời phỏng vấn.")
                st.rerun()

    if cand["interview_questions_json"]:
        questions = json.loads(cand["interview_questions_json"])
        st.markdown("#### Bộ câu hỏi theo JD, Rubric và CV")
        all_questions = []
        for level_key, items in questions.items():
            if not level_key.startswith("level_") or not isinstance(items, list):
                continue
            st.markdown(f"**{level_key.replace('_', ' ').title()}**")
            for item in items:
                st.write(f"- {item.get('question')} — *{item.get('target')}*")
                all_questions.append(item)

        if cand["stage_status"] == ApplicationStatus.INTERVIEW_SCHEDULED.value and all_questions:
            with st.form(f"scorecard_{cand_id}"):
                scorecard_items = []
                for index, item in enumerate(all_questions):
                    score = st.slider(item.get("question", f"Câu {index + 1}"), 0, 4, 2, key=f"qscore_{cand_id}_{index}")
                    note = st.text_input("Ghi chú", key=f"qnote_{cand_id}_{index}")
                    scorecard_items.append({"question": item.get("question"), "score": score, "note": note})
                submit_scorecard = st.form_submit_button("Hoàn Tất Scorecard", type="primary")
            if submit_scorecard:
                actor = st.session_state.get("current_user", {})
                for status in (ApplicationStatus.INTERVIEW_COMPLETED, ApplicationStatus.SCORECARD_PENDING):
                    transition_application_status(cand_id, status.value, actor_user_id=actor.get("id"), actor_role=Role.HR.value, reason="HR hoàn tất buổi phỏng vấn")
                save_interview_scorecard(cand_id, {"items": scorecard_items}, ApplicationStatus.INTERVIEWER_SUBMITTED.value, actor_user_id=actor.get("id"), actor_role=Role.HR.value)
                transition_application_status(cand_id, ApplicationStatus.AGENT_SUMMARIZED.value, actor_user_id=None, actor_role=Role.AGENT.value, reason="Agent tổng hợp scorecard")
                st.rerun()

    if cand["stage_status"] in {
        ApplicationStatus.AGENT_SUMMARIZED.value,
        ApplicationStatus.ASSESSMENT_REQUIRED.value,
    }:
        st.markdown("#### Quyết định sau phỏng vấn")
        outcome_options = (
            ["OFFER_PENDING", "NEXT_ROUND", "NOT_PROCEEDING"]
            if cand["stage_status"] == ApplicationStatus.ASSESSMENT_REQUIRED.value
            else ["NEXT_ROUND", "ASSESSMENT_REQUIRED", "OFFER_PENDING", "TALENT_POOL", "NOT_PROCEEDING"]
        )
        outcome = st.selectbox("Kết quả", outcome_options, key=f"outcome_{cand_id}")
        if outcome == "OFFER_PENDING":
            offer_salary = st.text_input("Mức lương offer", key=f"offer_salary_{cand_id}")
            offer_conditions = st.text_area("Điều kiện offer", key=f"offer_conditions_{cand_id}")
            if st.button("Tạo Offer", key=f"create_offer_{cand_id}", type="primary"):
                actor = st.session_state.get("current_user", {})
                create_offer(cand_id, offer_salary, offer_conditions, None, actor_user_id=actor.get("id"), actor_role=actor.get("role", Role.HR.value))
                st.rerun()
        elif st.button("Lưu Kết Quả Sau Phỏng Vấn", key=f"save_outcome_{cand_id}", type="primary"):
            actor = st.session_state.get("current_user", {})
            transition_application_status(cand_id, outcome, actor_user_id=actor.get("id"), actor_role=Role.HR.value, reason="HR quyết định sau phỏng vấn")
            st.rerun()


def render_footer():
    st.markdown(
        """
        <div class="dark-footer">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
                <div>
                    <h3>TOPIKLearn TalentScreen AI</h3>
                    <p>Nền tảng tuyển dụng thông minh ứng dụng AI — phân quyền HR/Admin & Ứng viên.<br>
                    Sinh ra cho đội ngũ HR & Hiring Manager Việt Nam.</p>
                </div>
                <div>
                    <span class="stamp-badge stamp-badge-green">작성 - 한국어 / TOPIKLearn</span>
                </div>
            </div>
            <hr style="border-color: #333; margin: 1.5rem 0 1rem 0;">
            <div style="display: flex; justify-content: space-between; font-size: 0.8rem; color: #999;">
                <span>© 2026 TOPIKLearn · TalentScreen AI Mini Hackathon</span>
                <span>Làm bằng cả lòng nhiệt huyết — 정성으로 만들었습니다</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# EOF
