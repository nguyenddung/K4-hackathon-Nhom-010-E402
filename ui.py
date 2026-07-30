"""Streamlit views and interaction handlers."""

import datetime
import json
import uuid

import numpy as np
import streamlit as st

from ai_service import candidate_assessment, cosine_sim, embed_text, get_client, load_assessment
from config import DB_PATH
from database import get_conn, init_db, log_audit
from styles import apply_theme


def render_assessment(assessment: dict):
    st.info(assessment["summary"])
    strengths_col, gaps_col = st.columns(2)
    with strengths_col:
        st.markdown("##### Điểm phù hợp")
        st.markdown("\n".join(f"- {item}" for item in assessment["strengths"]) or "Chưa có điểm phù hợp cụ thể để hiển thị.")
    with gaps_col:
        st.markdown("##### Thiếu sót cần xác minh")
        st.markdown("\n".join(f"- {item}" for item in assessment["gaps"]) or "CV đã thể hiện các yêu cầu chính hoặc cần xem lại JD.")
    st.markdown("##### Câu hỏi phỏng vấn gợi ý")
    questions = assessment["interview_questions"]
    st.markdown("\n".join(f"{index}. {question}" for index, question in enumerate(questions, start=1)) or "Chưa có câu hỏi gợi ý.")


def render_header():
    st.markdown(
        """
        <div class="brand-kicker">AI recruitment workspace</div>
        <h1 class="brand-title">TalentScreen AI</h1>
        <p class="brand-copy">Tạo job, sàng lọc hồ sơ và lưu quyết định tuyển dụng trong một không gian làm việc tập trung.</p>
        """,
        unsafe_allow_html=True,
    )
    with st.sidebar:
        st.header("TalentScreen AI")
        st.caption("Recruitment command center")
        st.divider()
        st.subheader("Trạng thái hệ thống")
        if get_client() is None:
            st.warning("Chưa có API key trong file .env → đang chạy ở MOCK mode (embedding giả lập).")
        else:
            st.success("Đã nạp OpenAI API key từ file .env.")
        st.divider()
        st.caption(f"DB file: `{DB_PATH}`")


def render_jobs_tab():
    st.subheader("Tạo job mới")
    st.caption("Xác định rõ yêu cầu để AI đánh giá hồ sơ nhất quán hơn.")
    with st.form("job_form"):
        title = st.text_input("Tên vị trí", placeholder="VD: Backend Developer (Python)")
        description = st.text_area("Mô tả công việc (JD)", height=200, placeholder="Yêu cầu kỹ năng, kinh nghiệm, trách nhiệm công việc...")
        submitted = st.form_submit_button("Tạo Job", type="primary")
    if submitted:
        if not title or not description:
            st.error("Vui lòng nhập đủ tên vị trí và mô tả.")
        else:
            job_id = str(uuid.uuid4())
            conn = get_conn()
            conn.execute(
                "INSERT INTO jobs (id, title, description, embedding, created_at) VALUES (?,?,?,?,?)",
                (job_id, title, description, json.dumps(embed_text(description)), datetime.datetime.utcnow().isoformat()),
            )
            conn.commit()
            conn.close()
            log_audit(job_id, "create_job", f"Tạo job '{title}'")
            st.success(f"Đã tạo job **{title}** (id: `{job_id[:8]}...`)")
    st.divider()
    st.subheader("Job đang mở")
    conn = get_conn()
    jobs = conn.execute("SELECT id, title, created_at FROM jobs ORDER BY created_at DESC").fetchall()
    conn.close()
    if jobs:
        st.dataframe([{"ID": job["id"][:8], "Tên": job["title"], "Tạo lúc": job["created_at"]} for job in jobs], use_container_width=True)
    else:
        st.info("Chưa có job nào.")


def render_screening_tab():
    st.subheader("Sàng lọc ứng viên")
    st.caption("Đối chiếu nội dung CV với yêu cầu của job đã chọn.")
    conn = get_conn()
    jobs = conn.execute("SELECT id, title FROM jobs ORDER BY created_at DESC").fetchall()
    conn.close()
    if not jobs:
        st.info("Hãy tạo ít nhất 1 job ở tab 1 trước.")
        return
    job_map = {f"{job['title']} ({job['id'][:8]})": job["id"] for job in jobs}
    job_id = job_map[st.selectbox("Chọn Job", list(job_map.keys()))]
    with st.form("cv_form"):
        candidate_name = st.text_input("Tên ứng viên")
        cv_text = st.text_area("Nội dung CV (paste text)", height=200)
        submitted = st.form_submit_button("Chấm điểm CV", type="primary")
    if submitted:
        if not candidate_name or not cv_text:
            st.error("Vui lòng nhập tên và nội dung CV.")
        else:
            conn = get_conn()
            job = conn.execute("SELECT description, embedding FROM jobs WHERE id=?", (job_id,)).fetchone()
            candidate_embedding = embed_text(cv_text)
            score = cosine_sim(json.loads(job["embedding"]), candidate_embedding)
            assessment = candidate_assessment(job["description"], cv_text, score)
            candidate_id = str(uuid.uuid4())
            conn.execute(
                """INSERT INTO candidates (id, job_id, name, cv_text, embedding, score, reasoning, created_at)
                   VALUES (?,?,?,?,?,?,?,?)""",
                (candidate_id, job_id, candidate_name, cv_text, json.dumps(candidate_embedding), score, json.dumps(assessment, ensure_ascii=False), datetime.datetime.utcnow().isoformat()),
            )
            conn.commit()
            conn.close()
            log_audit(candidate_id, "screen_cv", f"Chấm CV '{candidate_name}' cho job {job_id[:8]} — score={score:.3f}")
            st.metric("Điểm khớp (cosine similarity)", f"{score:.3f}")
            st.markdown("#### Phân tích hồ sơ bằng AI")
            render_assessment(assessment)
    st.divider()
    st.subheader("Ứng viên đã chấm")
    conn = get_conn()
    candidates = conn.execute("SELECT id, name, score, created_at FROM candidates WHERE job_id=? ORDER BY score DESC", (job_id,)).fetchall()
    conn.close()
    if candidates:
        st.dataframe([{"ID": candidate["id"][:8], "Tên": candidate["name"], "Điểm": round(candidate["score"], 3), "Lúc": candidate["created_at"]} for candidate in candidates], use_container_width=True)
    else:
        st.info("Chưa có ứng viên nào được chấm cho job này.")


def render_decisions_tab():
    st.subheader("Đưa ra quyết định")
    st.caption("Kết hợp nhận xét AI với đánh giá chuyên môn của đội tuyển dụng.")
    conn = get_conn()
    candidates = conn.execute("""SELECT c.id, c.name, c.score, c.reasoning, j.title as job_title FROM candidates c JOIN jobs j ON c.job_id = j.id ORDER BY c.created_at DESC""").fetchall()
    conn.close()
    if candidates:
        candidate_map = {f"{candidate['name']} — {candidate['job_title']} (score {candidate['score']:.2f})": candidate["id"] for candidate in candidates}
        candidate_id = candidate_map[st.selectbox("Chọn ứng viên", list(candidate_map.keys()))]
        candidate = next(item for item in candidates if item["id"] == candidate_id)
        st.markdown("#### Phân tích hồ sơ bằng AI")
        render_assessment(load_assessment(candidate["reasoning"]))
        conn = get_conn()
        latest = conn.execute("SELECT id, decision, note, created_at FROM decisions WHERE candidate_id=? ORDER BY created_at DESC LIMIT 1", (candidate_id,)).fetchone()
        conn.close()
        options = ["Pass — mời phỏng vấn", "Hold — xem xét thêm", "Reject — từ chối"]
        if latest:
            st.caption(f"Đang chỉnh sửa quyết định gần nhất từ {latest['created_at']}.")
        decision = st.radio("Quyết định", options, index=options.index(latest["decision"]) if latest and latest["decision"] in options else 0, horizontal=True, key=f"decision_{candidate_id}")
        note = st.text_input("Ghi chú thêm (tuỳ chọn)", value=latest["note"] if latest else "", key=f"decision_note_{candidate_id}")
        button_label = "Cập nhật quyết định" if latest else "Lưu quyết định"
        if st.button(button_label, type="primary"):
            saved_at = datetime.datetime.utcnow().isoformat()
            conn = get_conn()
            if latest:
                conn.execute("UPDATE decisions SET decision=?, note=?, created_at=? WHERE id=?", (decision, note, saved_at, latest["id"]))
                audit_action, audit_detail = "update_hr_decision", f"Sửa quyết định từ '{latest['decision']}' thành '{decision}' — {note}"
            else:
                conn.execute("INSERT INTO decisions (id, candidate_id, decision, note, created_at) VALUES (?,?,?,?,?)", (str(uuid.uuid4()), candidate_id, decision, note, saved_at))
                audit_action, audit_detail = "hr_decision", f"{decision} — {note}"
            conn.commit()
            conn.close()
            log_audit(candidate_id, audit_action, audit_detail)
            st.success(f"Đã {button_label.lower()}: **{decision}**")
    else:
        st.info("Chưa có ứng viên nào để quyết định. Hãy screen CV ở tab 2.")
    st.divider()
    st.subheader("Lịch sử quyết định")
    conn = get_conn()
    decisions = conn.execute("SELECT d.decision, d.note, d.created_at, c.name FROM decisions d JOIN candidates c ON d.candidate_id = c.id ORDER BY d.created_at DESC").fetchall()
    conn.close()
    if decisions:
        st.dataframe([{"Ứng viên": item["name"], "Quyết định": item["decision"], "Ghi chú": item["note"], "Lúc": item["created_at"]} for item in decisions], use_container_width=True)
    else:
        st.info("Chưa có quyết định nào.")


def render_audit_tab():
    st.subheader("Phân tích và kiểm toán")
    st.caption("Theo dõi độ phân tán điểm số và lịch sử thao tác trên hệ thống.")
    conn = get_conn()
    candidates = conn.execute("""SELECT c.name, c.score, j.title as job_title, d.decision FROM candidates c JOIN jobs j ON c.job_id = j.id LEFT JOIN decisions d ON d.candidate_id = c.id""").fetchall()
    conn.close()
    if candidates:
        first_col, second_col = st.columns(2)
        scores = [candidate["score"] for candidate in candidates]
        with first_col:
            st.metric("Số ứng viên đã chấm", len(candidates))
            st.metric("Điểm trung bình", f"{np.mean(scores):.3f}")
        with second_col:
            st.metric("Điểm cao nhất", f"{max(scores):.3f}")
            st.metric("Điểm thấp nhất", f"{min(scores):.3f}")
        counts = {}
        for candidate in candidates:
            decision = candidate["decision"] or "Chưa quyết định"
            counts[decision] = counts.get(decision, 0) + 1
        st.markdown("**Phân bố quyết định**")
        st.bar_chart(counts)
        st.caption("Lưu ý fairness cho demo: cần xem lại thủ công nếu điểm số hoặc quyết định không nhất quán.")
    else:
        st.info("Chưa có dữ liệu để phân tích.")
    st.divider()
    st.subheader("Nhật ký kiểm toán")
    conn = get_conn()
    logs = conn.execute("SELECT action, detail, created_at FROM audit_log ORDER BY created_at DESC LIMIT 100").fetchall()
    conn.close()
    if logs:
        st.dataframe([{"Hành động": log["action"], "Chi tiết": log["detail"], "Lúc": log["created_at"]} for log in logs], use_container_width=True)
    else:
        st.info("Chưa có log nào.")


def main():
    st.set_page_config(page_title="TalentScreen AI — Hackathon Mode", layout="wide")
    apply_theme()
    init_db()
    render_header()
    jobs_tab, screening_tab, decisions_tab, audit_tab = st.tabs(["01  Tạo job", "02  Sàng lọc CV", "03  Quyết định", "04  Phân tích"])
    with jobs_tab:
        render_jobs_tab()
    with screening_tab:
        render_screening_tab()
    with decisions_tab:
        render_decisions_tab()
    with audit_tab:
        render_audit_tab()