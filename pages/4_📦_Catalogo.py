import streamlit as st
from src.components.theme import apply_theme

st.set_page_config(page_title="Catálogo & Produtos", page_icon="📦", layout="wide")
apply_theme()

st.title("📦 Catálogo & Produtos")
st.caption("Curadoria de portfólio: estrelas, vacas leiteiras, abacaxis")
st.info("🚧 Sprint 4 — em construção")
