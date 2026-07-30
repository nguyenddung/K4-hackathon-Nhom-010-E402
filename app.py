"""TalentScreen AI application entry point with authentication & role-based access control."""

import streamlit as st

from database import init_db
from styles import apply_theme
from ui import (
    render_auth_screen,
    render_candidate_dashboard,
    render_footer,
    render_hr_dashboard,
    render_user_nav_header,
)


def main():
    st.set_page_config(
        page_title="TOPIKLearn TalentScreen AI - RBAC Portal",
        page_icon="📜",
        layout="wide",
        initial_sidebar_state="collapsed",
    )

    init_db()
    apply_theme()

    if "current_user" not in st.session_state:
        render_auth_screen()
        render_footer()
    else:
        user = st.session_state["current_user"]
        render_user_nav_header(user)

        if user.get("role") == "HR":
            render_hr_dashboard()
        else:
            render_candidate_dashboard(user)

        render_footer()


if __name__ == "__main__":
    main()
