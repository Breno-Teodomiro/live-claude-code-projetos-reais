"""Aplicação do tema premium via CSS injetado."""

import streamlit as st

CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

.stApp {
    background: linear-gradient(180deg, #0B0F19 0%, #0F1422 100%);
}

h1, h2, h3, h4 { font-weight: 700; letter-spacing: -0.02em; }
h1 { font-size: 2rem !important; }
h2 { font-size: 1.5rem !important; color: #F9FAFB; }
h3 { font-size: 1.125rem !important; color: #E5E7EB; }

[data-testid="stSidebar"] {
    background: #0B0F19;
    border-right: 1px solid #1F2937;
}

[data-testid="stMetric"] {
    background: #111827;
    border: 1px solid #1F2937;
    border-radius: 12px;
    padding: 1.25rem 1.5rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.12);
    transition: transform .15s ease, border-color .15s ease;
}
[data-testid="stMetric"]:hover { transform: translateY(-2px); border-color: #3B82F6; }
[data-testid="stMetricLabel"] { color: #9CA3AF; font-size: 0.75rem; font-weight: 500; text-transform: uppercase; letter-spacing: 0.05em; }
[data-testid="stMetricValue"] { font-family: 'JetBrains Mono', monospace; font-weight: 700; font-size: 1.75rem; color: #F9FAFB; }
[data-testid="stMetricDelta"] { font-size: 0.85rem; font-weight: 500; }

div[data-testid="column"] { padding: 0 0.5rem; }

.stButton > button {
    background: #1F2937;
    color: #F9FAFB;
    border: 1px solid #374151;
    border-radius: 8px;
    font-weight: 500;
    transition: all .15s ease;
}
.stButton > button:hover { background: #3B82F6; border-color: #3B82F6; }

hr { border-color: #1F2937; margin: 1.5rem 0; }

#MainMenu, footer { visibility: hidden; }
header[data-testid="stHeader"] { background: transparent; }
</style>
"""


def apply_theme() -> None:
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
