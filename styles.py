"""Visual theme for the Streamlit application."""

import streamlit as st


def apply_theme():
    st.markdown(
        """
        <style>
            @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Outfit:wght@500;600;700&display=swap');
            :root { --ink: #18333d; --muted: #687b80; --teal: #087f78; --teal-dark: #05635e; --canvas: #f4f7f5; --line: #dbe6e1; }
            .stApp { background: linear-gradient(135deg, rgba(188,230,221,.38), transparent 34%), linear-gradient(315deg, rgba(255,221,204,.42), transparent 28%), var(--canvas); color: var(--ink); font-family: 'DM Sans', sans-serif; }
            [data-testid="stAppViewContainer"] .main .block-container { max-width: 1180px; padding-top: 2.4rem; padding-bottom: 3.5rem; }
            [data-testid="stSidebar"] { background: #103f45; }
            [data-testid="stSidebar"] * { color: #f5fbfa; }
            [data-testid="stSidebar"] [data-testid="stAlert"] { border-radius: 8px; border: 1px solid rgba(255,255,255,.25); background: rgba(255,255,255,.12); }
            .brand-kicker { color: var(--teal); font-size: .78rem; font-weight: 700; letter-spacing: .12em; text-transform: uppercase; margin-bottom: .55rem; }
            .brand-title { font-family: 'Outfit', sans-serif; color: var(--ink); font-size: clamp(2.1rem, 5vw, 3.55rem); font-weight: 700; line-height: 1.03; margin: 0; }
            .brand-copy { color: var(--muted); font-size: 1rem; line-height: 1.6; margin: .8rem 0 1.8rem; max-width: 720px; }
            h2, h3, [data-testid="stMarkdownContainer"] h2 { font-family: 'Outfit', sans-serif; color: var(--ink); letter-spacing: 0; }
            h3, [data-testid="stMarkdownContainer"] h3 { font-size: 1.45rem; margin-top: .45rem; }
            [data-testid="stTabs"] [role="tablist"] { gap: .45rem; border-bottom: 1px solid var(--line); }
            [data-testid="stTabs"] [role="tab"] { background: transparent; border-radius: 6px 6px 0 0; color: var(--muted); font-weight: 600; padding: .75rem 1rem; }
            [data-testid="stTabs"] [role="tab"][aria-selected="true"] { color: var(--teal-dark); background: rgba(255,255,255,.78); }
            [data-testid="stForm"] { background: rgba(255,255,255,.9); border: 1px solid var(--line); border-radius: 8px; padding: 1.2rem 1.25rem .5rem; box-shadow: 0 10px 28px rgba(24,51,61,.06); }
            [data-testid="stTextInput"] input, [data-testid="stTextArea"] textarea, [data-testid="stSelectbox"] div[data-baseweb="select"] > div { background: #fbfdfc; border-color: #cbdad4; border-radius: 6px; }
            [data-testid="stTextInput"] input:focus, [data-testid="stTextArea"] textarea:focus { border-color: var(--teal); box-shadow: 0 0 0 2px rgba(8,127,120,.14); }
            .stButton > button, [data-testid="stFormSubmitButton"] > button { background: var(--teal); border: 1px solid var(--teal); border-radius: 6px; color: white; font-weight: 700; padding: .55rem 1.15rem; }
            .stButton > button:hover, [data-testid="stFormSubmitButton"] > button:hover { background: var(--teal-dark); border-color: var(--teal-dark); color: white; }
            [data-testid="stMetric"] { background: rgba(255,255,255,.88); border: 1px solid var(--line); border-radius: 8px; padding: 1rem; }
            [data-testid="stDataFrame"] { border: 1px solid var(--line); border-radius: 8px; overflow: hidden; }
            [data-testid="stAlert"] { border-radius: 8px; }
            hr { border-color: var(--line); margin: 2rem 0; }
            @media (max-width: 700px) { [data-testid="stAppViewContainer"] .main .block-container { padding: 1.5rem 1rem 2.5rem; } [data-testid="stTabs"] [role="tab"] { padding: .65rem .55rem; font-size: .84rem; } }
        </style>
        """,
        unsafe_allow_html=True,
    )