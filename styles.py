"""Visual theme for the Streamlit application."""

import streamlit as st


def apply_theme():
    st.markdown(
        """
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&family=Space+Grotesk:wght@400;500;600;700&display=swap');
            :root { --ink: #0b1220; --navy: #101b33; --paper: #f5f7fa; --card: #ffffff; --teal: #0fb88a; --teal-dark: #0a8f6a; --line: #e3e7ee; --muted: #5b6472; }
            .stApp { background: var(--paper); color: var(--ink); font-family: 'Inter', sans-serif; }
            [data-testid="stAppViewContainer"] .main .block-container { max-width: 1180px; padding-top: 2rem; padding-bottom: 3.75rem; }
            [data-testid="stHeader"] { background: rgba(245, 247, 250, .88); border-bottom: 1px solid var(--line); }
            [data-testid="stToolbar"] { right: 1rem; }
            .workspace-header { align-items: center; border-bottom: 1px solid var(--line); display: flex; justify-content: space-between; margin-bottom: 2rem; padding-bottom: 1.25rem; }
            .brand-lockup { align-items: center; display: flex; gap: .75rem; }
            .logo-mark { align-items: center; background: var(--ink); border-radius: 8px; color: white; display: flex; font-family: 'Space Grotesk', sans-serif; font-size: .75rem; font-weight: 700; height: 34px; justify-content: center; letter-spacing: .04em; position: relative; overflow: hidden; width: 34px; }
            .logo-mark::after { background: linear-gradient(135deg, var(--teal), transparent 65%); content: ''; inset: 0; opacity: .9; position: absolute; }
            .logo-mark span { position: relative; z-index: 1; }
            .brand-name { color: var(--ink); font-family: 'Space Grotesk', sans-serif; font-size: 1rem; font-weight: 700; letter-spacing: .04em; margin: 0; }
            .brand-context { color: var(--muted); font-size: .78rem; margin: .1rem 0 0; }
            .system-chip { align-items: center; background: var(--card); border: 1px solid var(--line); border-radius: 999px; color: var(--teal-dark); display: flex; font-size: .74rem; font-weight: 600; gap: .4rem; padding: .42rem .7rem; }
            .system-dot { background: var(--teal); border-radius: 50%; display: inline-block; height: .4rem; width: .4rem; }
            .brand-kicker { color: var(--teal-dark); font-family: 'JetBrains Mono', monospace; font-size: .71rem; font-weight: 500; letter-spacing: .06em; margin-bottom: .55rem; text-transform: uppercase; }
            .brand-title { color: var(--ink); font-family: 'Space Grotesk', sans-serif; font-size: clamp(2rem, 5vw, 3.25rem); font-weight: 700; letter-spacing: 0; line-height: 1.04; margin: 0; }
            .brand-copy { color: var(--muted); font-size: 1rem; line-height: 1.6; margin: .8rem 0 1.9rem; max-width: 700px; }
            h1, h2, h3, h4, [data-testid="stMarkdownContainer"] h2, [data-testid="stMarkdownContainer"] h3 { color: var(--ink); font-family: 'Space Grotesk', sans-serif; letter-spacing: 0; }
            h2, [data-testid="stMarkdownContainer"] h2 { font-size: 1.85rem; }
            h3, [data-testid="stMarkdownContainer"] h3 { font-size: 1.35rem; margin-top: .5rem; }
            [data-testid="stSidebar"], [data-testid="stSidebarCollapsedControl"] { display: none; }
            [data-testid="stTabs"] [role="tablist"] { gap: .25rem; border-bottom: 1px solid var(--line); }
            [data-testid="stTabs"] [role="tab"] { background: transparent; border-radius: 0; color: var(--muted); font-family: 'Inter', sans-serif; font-size: .87rem; font-weight: 600; padding: .85rem .9rem; }
            [data-testid="stTabs"] [role="tab"][aria-selected="true"] { background: var(--card); border-bottom: 2px solid var(--teal); color: var(--ink); }
            [data-testid="stForm"] { background: var(--card); border: 1px solid var(--line); border-radius: 8px; box-shadow: 0 14px 32px -24px rgba(16,27,51,.4); padding: 1.3rem 1.35rem .55rem; }
            [data-testid="stTextInput"] input, [data-testid="stTextArea"] textarea, [data-testid="stSelectbox"] div[data-baseweb="select"] > div { background: #fff; border-color: #cfd6df; border-radius: 6px; color: var(--ink); }
            [data-testid="stTextInput"] input:focus, [data-testid="stTextArea"] textarea:focus { border-color: var(--teal); box-shadow: 0 0 0 2px rgba(15,184,138,.14); }
            [data-testid="stTextInput"] label, [data-testid="stTextArea"] label, [data-testid="stSelectbox"] label, [data-testid="stRadio"] label { color: var(--ink); font-weight: 600; }
            .stButton > button, [data-testid="stFormSubmitButton"] > button { background: var(--ink); border: 1px solid var(--ink); border-radius: 7px; color: white; font-weight: 700; padding: .58rem 1.15rem; }
            .stButton > button:hover, [data-testid="stFormSubmitButton"] > button:hover { background: var(--teal-dark); border-color: var(--teal-dark); color: white; }
            [data-testid="stMetric"] { background: var(--card); border: 1px solid var(--line); border-radius: 8px; padding: 1rem; }
            [data-testid="stMetricValue"] { color: var(--teal-dark); font-family: 'Space Grotesk', sans-serif; }
            [data-testid="stDataFrame"] { background: var(--card); border: 1px solid var(--line); border-radius: 8px; overflow: hidden; }
            [data-testid="stAlert"] { border-radius: 8px; }
            [data-testid="stInfo"] { background: #edf9f5; border-color: #bdebdc; color: var(--ink); }
            hr { border-color: var(--line); margin: 2rem 0; }
            @media (max-width: 700px) { [data-testid="stAppViewContainer"] .main .block-container { padding: 1.25rem 1rem 2.5rem; } .workspace-header { align-items: flex-start; gap: .75rem; } .system-chip { font-size: .68rem; } [data-testid="stTabs"] [role="tab"] { font-size: .78rem; padding: .7rem .5rem; } }
        </style>
        """,
        unsafe_allow_html=True,
    )