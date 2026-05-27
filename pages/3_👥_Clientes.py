import streamlit as st
from src.components.theme import apply_theme

st.set_page_config(page_title="Clientes & Geografia", page_icon="👥", layout="wide")
apply_theme()

st.title("👥 Clientes & Geografia")
st.caption("RFM, cohorts e distribuição geográfica")
st.info("🚧 Sprint 3 — em construção")
