"""Visual theme for TalentScreen AI - Editorial Warm Paper & Red Stamp Design System."""

import streamlit as st


def apply_theme():
    st.markdown(
        """
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,600;0,700;0,900;1,400;1,700&family=Space+Mono:ital,wght@0,400;0,700;1,400&family=Inter:wght@300;400;500;600;700&family=Noto+Serif+KR:wght@400;700&display=swap');

            :root {
                --paper: #F7F4EB;
                --paper-card: #FAF7F0;
                --paper-white: #FFFFFF;
                --ink: #221F1E;
                --muted: #6E685F;
                --red: #C83827;
                --red-dark: #A32718;
                --red-bg: rgba(200, 56, 39, 0.08);
                --line: #D9D2C5;
                --line-strong: #221F1E;
                --dark-banner: #1C1A19;
            }

            .stApp {
                background-color: var(--paper) !important;
                color: var(--ink);
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            }

            [data-testid="stAppViewContainer"] .main .block-container {
                max-width: 1140px;
                padding-top: 1.5rem;
                padding-bottom: 4rem;
            }

            [data-testid="stMainBlockContainer"] {
                max-width: 1140px !important;
                padding-top: 1.25rem !important;
                padding-bottom: 4rem !important;
            }

            [data-testid="stHeader"] {
                background: transparent;
                border: 0;
                height: 0;
            }

            [data-testid="stToolbar"], [data-testid="stDecoration"], #MainMenu {
                display: none !important;
            }

            [data-testid="stSidebar"], [data-testid="stSidebarCollapsedControl"] {
                display: none;
            }

            /* Brand & Editorial Navigation Header */
            .editorial-header {
                display: flex;
                align-items: center;
                justify-content: space-between;
                padding-bottom: 1.2rem;
                border-bottom: 2px solid var(--ink);
                margin-bottom: 1.5rem;
                position: relative;
                gap: 1.25rem;
            }

            .editorial-header::after {
                content: '';
                position: absolute;
                left: 0;
                right: 0;
                bottom: -6px;
                border-bottom: 1px solid var(--ink);
            }

            .brand-box {
                display: flex;
                align-items: center;
                gap: 0.8rem;
            }

            .logo-icon {
                background: var(--red);
                color: #FFFFFF;
                font-family: 'Space Mono', monospace;
                font-weight: 700;
                font-size: 0.75rem;
                padding: 6px 10px;
                border-radius: 3px;
                letter-spacing: 0.05em;
                box-shadow: 2px 2px 0px var(--ink);
            }

            .brand-title-text {
                font-family: 'Playfair Display', serif;
                font-size: 1.35rem !important;
                font-weight: 900;
                line-height: 1.05 !important;
                color: var(--ink);
                margin: 0;
                letter-spacing: -0.01em;
            }

            .brand-title-text span {
                color: var(--red);
            }

            .korean-sub {
                font-family: 'Noto Serif KR', serif;
                font-size: 0.75rem;
                color: var(--muted);
                margin-left: 6px;
            }

            .user-nav-bar {
                display: flex;
                align-items: center;
                gap: 10px;
                margin-left: auto;
                font-size: 0.78rem;
                white-space: nowrap;
            }

            .role-nav {
                color: var(--muted);
                font-family: 'Space Mono', monospace;
                font-size: 0.69rem;
                letter-spacing: 0.03em;
                line-height: 1.6;
                text-align: center;
            }

            .role-badge-hr {
                background: var(--red);
                color: #FFFFFF;
                font-family: 'Space Mono', monospace;
                font-size: 0.75rem;
                padding: 4px 10px;
                border-radius: 3px;
                font-weight: 700;
            }

            .role-badge-cand {
                background: #2D7D46;
                color: #FFFFFF;
                font-family: 'Space Mono', monospace;
                font-size: 0.75rem;
                padding: 4px 10px;
                border-radius: 3px;
                font-weight: 700;
            }

            /* Editorial Hero Typography */
            .hero-kicker {
                font-family: 'Space Mono', monospace;
                font-size: 0.75rem;
                letter-spacing: 0.12em;
                text-transform: uppercase;
                color: var(--red);
                margin-bottom: 0.5rem;
                font-weight: 700;
            }

            .hero-title {
                font-family: 'Playfair Display', serif;
                font-size: clamp(2.2rem, 4.5vw, 3.4rem);
                font-weight: 900;
                line-height: 1.12;
                color: var(--ink);
                margin: 0 0 1rem 0;
            }

            .serif-red-italic {
                font-family: 'Playfair Display', serif;
                font-style: italic;
                color: var(--red);
                font-weight: 700;
            }

            .hero-lead {
                font-size: 1.05rem;
                color: var(--muted);
                line-height: 1.65;
                max-width: 780px;
                margin-bottom: 1.8rem;
            }

            h1, h2, h3, h4,
            [data-testid="stMarkdownContainer"] h1,
            [data-testid="stMarkdownContainer"] h2,
            [data-testid="stMarkdownContainer"] h3 {
                font-family: 'Playfair Display', serif !important;
                color: var(--ink);
                letter-spacing: -0.01em;
            }

            /* Red Ink Stamp Badge */
            .stamp-badge {
                display: inline-block;
                border: 2px solid var(--red);
                color: var(--red);
                background: var(--red-bg);
                font-family: 'Space Mono', monospace;
                font-weight: 700;
                font-size: 0.78rem;
                padding: 4px 10px;
                border-radius: 4px;
                letter-spacing: 0.06em;
                text-transform: uppercase;
                transform: rotate(-3deg);
                box-shadow: 1px 1px 0px rgba(200, 56, 39, 0.3);
                margin: 2px 4px;
            }

            .stamp-badge-green {
                border-color: #2D7D46;
                color: #2D7D46;
                background: rgba(45, 125, 70, 0.08);
                transform: rotate(-2deg);
            }

            .stamp-badge-dark {
                border-color: var(--ink);
                color: var(--ink);
                background: rgba(34, 31, 30, 0.06);
                transform: rotate(1deg);
            }

            /* Wavy Red Underline Effect */
            .wavy-underline {
                text-decoration: underline wavy var(--red);
                text-underline-offset: 4px;
                text-decoration-thickness: 1.5px;
            }

            /* Wongonji / Manuscript Grid Box */
            .wongonji-box {
                background: var(--paper-card);
                border: 2px solid var(--ink);
                border-radius: 4px;
                padding: 1.4rem;
                box-shadow: 4px 4px 0px var(--ink);
                margin-bottom: 1.5rem;
            }

            .wongonji-header {
                font-family: 'Space Mono', monospace;
                font-size: 0.75rem;
                letter-spacing: 0.1em;
                text-transform: uppercase;
                color: var(--red);
                border-bottom: 1px dashed var(--line);
                padding-bottom: 8px;
                margin-bottom: 12px;
                font-weight: 700;
            }

            /* Step Cards (01, 02, 03) */
            .step-card {
                background: var(--paper-card);
                border: 1px solid var(--line);
                border-radius: 4px;
                padding: 1.25rem;
                margin-bottom: 1rem;
                transition: all 0.2s ease;
            }

            .step-card:hover {
                border-color: var(--ink);
                box-shadow: 3px 3px 0px var(--ink);
            }

            .step-num {
                font-family: 'Playfair Display', serif;
                font-size: 1.5rem;
                font-weight: 900;
                color: var(--red);
                margin-right: 0.8rem;
            }

            .step-title {
                font-family: 'Playfair Display', serif;
                font-size: 1.15rem;
                font-weight: 700;
                color: var(--ink);
            }

            code, .mono-chip {
                font-family: 'Space Mono', monospace !important;
                background: var(--paper-card);
                border: 1px solid var(--line);
                color: var(--ink);
                padding: 2px 6px;
                border-radius: 3px;
                font-size: 0.82rem;
            }

            /* Tabs Styling */
            [data-testid="stTabs"] [role="tablist"] {
                gap: 0.4rem;
                border-bottom: 2px solid var(--ink);
            }

            [data-testid="stTabs"] [role="tab"] {
                background: transparent;
                border-radius: 4px 4px 0 0;
                color: var(--muted);
                font-family: 'Inter', sans-serif;
                font-size: 0.88rem;
                font-weight: 600;
                padding: 0.65rem 1.1rem;
            }

            [data-testid="stTabs"] [role="tab"][aria-selected="true"] {
                background: var(--paper-card);
                border: 2px solid var(--ink);
                border-bottom: 2px solid var(--paper-card);
                color: var(--red);
                font-weight: 700;
                margin-bottom: -2px;
            }

            /* Forms & Inputs */
            [data-testid="stForm"] {
                background: var(--paper-card);
                border: 2px solid var(--ink);
                border-radius: 4px;
                box-shadow: 4px 4px 0px var(--ink);
                padding: 1.5rem;
            }

            [data-testid="stTextInput"] input,
            [data-testid="stTextArea"] textarea,
            [data-testid="stSelectbox"] div[data-baseweb="select"] > div {
                background: var(--paper-white) !important;
                border: 1px solid var(--line) !important;
                border-radius: 4px !important;
                color: var(--ink) !important;
                font-family: 'Inter', sans-serif !important;
            }

            .stButton > button, [data-testid="stFormSubmitButton"] > button {
                background: var(--ink) !important;
                border: 2px solid var(--ink) !important;
                border-radius: 4px !important;
                color: #FFFFFF !important;
                font-weight: 700 !important;
                padding: 0.6rem 1.4rem !important;
                box-shadow: 2px 2px 0px var(--red);
                transition: all 0.15s ease;
            }

            .stButton > button:hover, [data-testid="stFormSubmitButton"] > button:hover {
                background: var(--red) !important;
                border-color: var(--red) !important;
                color: #FFFFFF !important;
                box-shadow: 3px 3px 0px var(--ink);
            }

            .stButton > button:focus-visible,
            [data-testid="stFormSubmitButton"] > button:focus-visible,
            input:focus-visible,
            textarea:focus-visible,
            [role="tab"]:focus-visible {
                outline: 3px solid rgba(200, 56, 39, 0.35) !important;
                outline-offset: 3px !important;
            }

            [data-testid="stMetric"] {
                background: var(--paper-card);
                border: 1px solid var(--line);
                border-radius: 4px;
                padding: 1rem;
                box-shadow: 2px 2px 0px var(--line-strong);
            }

            [data-testid="stMetricValue"] {
                color: var(--red) !important;
                font-family: 'Playfair Display', serif !important;
                font-weight: 900;
            }

            .dark-footer {
                background: var(--dark-banner);
                color: #FAF7F0;
                padding: 2.5rem 2rem;
                border-radius: 4px;
                margin-top: 3.5rem;
                border-top: 3px solid var(--red);
            }

            @media (max-width: 900px) {
                [data-testid="stAppViewContainer"] .main .block-container {
                    padding-left: 1.1rem;
                    padding-right: 1.1rem;
                    padding-top: 1rem;
                }

                [data-testid="stMainBlockContainer"] {
                    padding: 0.75rem 1.1rem 3rem !important;
                }

                .editorial-header {
                    align-items: flex-start;
                    flex-wrap: wrap;
                }

                .role-nav {
                    order: 3;
                    text-align: left;
                    width: 100%;
                }

                [data-testid="stTabs"] [role="tablist"] {
                    overflow-x: auto;
                    scrollbar-width: thin;
                }

                [data-testid="stTabs"] [role="tab"] {
                    flex: 0 0 auto;
                    white-space: nowrap;
                }
            }

            @media (max-width: 640px) {
                .hero-title {
                    font-size: 2.05rem !important;
                    line-height: 1.08;
                }

                .hero-lead {
                    font-size: 0.95rem;
                }

                .brand-title-text {
                    font-size: 1.05rem;
                }

                .korean-sub,
                .user-nav-bar strong,
                .user-nav-bar:not(.role-badge-hr):not(.role-badge-cand) {
                    font-size: 0.7rem;
                }

                .wongonji-box,
                [data-testid="stForm"] {
                    box-shadow: 2px 2px 0 var(--ink);
                    padding: 1rem;
                }

                [data-testid="stHorizontalBlock"] {
                    flex-wrap: wrap;
                }

                [data-testid="stHorizontalBlock"] > div {
                    min-width: min(100%, 280px) !important;
                    flex: 1 1 100% !important;
                }

                .dark-footer {
                    margin-left: -0.25rem;
                    margin-right: -0.25rem;
                    padding: 1.5rem 1rem;
                }
            }
        </style>
        """,
        unsafe_allow_html=True,
    )
