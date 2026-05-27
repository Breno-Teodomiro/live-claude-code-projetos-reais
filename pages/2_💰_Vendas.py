import streamlit as st
from src.components.theme import apply_theme

st.set_page_config(page_title="Vendas & Performance", page_icon="💰", layout="wide")
apply_theme()

st.title("💰 Vendas & Performance")
st.caption("Diagnóstico granular da operação comercial")
st.info("🚧 Sprint 2 — em construção")
