import streamlit as st
from src.components.theme import apply_theme

st.set_page_config(page_title="Dados Brutos", page_icon="🗂️", layout="wide")
apply_theme()

st.title("🗂️ Dados Brutos")
st.caption("Auditoria e exportação livre")
st.info("🚧 Sprint 6 — em construção")
