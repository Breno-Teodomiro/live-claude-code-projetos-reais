"""Entrypoint do Dashboard Executivo de Vendas."""

import streamlit as st

from src.components.theme import apply_theme
from src.data.loaders import load_vendas, load_clientes, load_produtos
from src.utils.formatters import fmt_brl_compact, fmt_int

st.set_page_config(
    page_title="Dashboard Executivo de Vendas",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_theme()

st.title("📊 Dashboard Executivo de Vendas")
st.caption("Visão consolidada de vendas, clientes, catálogo e inteligência competitiva")

with st.sidebar:
    st.markdown("### Navegação")
    st.markdown(
        """
        - 📊 **Visão Executiva**
        - 💰 **Vendas & Performance**
        - 👥 **Clientes & Geografia**
        - 📦 **Catálogo & Produtos**
        - 🎯 **Inteligência Competitiva**
        - 🗂️ **Dados Brutos**
        """
    )
    st.markdown("---")
    st.caption("Use o menu de páginas no topo da sidebar para navegar.")

st.markdown("## Bem-vindo")
st.markdown(
    """
    Esta é a página inicial do dashboard. Use a navegação lateral para acessar
    cada módulo analítico. Os dados são atualizados a cada 5 minutos.
    """
)

st.markdown("### Status de Dados")

try:
    vendas = load_vendas()
    clientes = load_clientes()
    produtos = load_produtos()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Vendas", fmt_int(len(vendas)))
    c2.metric("Clientes", fmt_int(len(clientes)))
    c3.metric("Produtos", fmt_int(len(produtos)))
    c4.metric("Receita total", fmt_brl_compact(vendas["receita"].sum()))

    st.caption(f"Fonte dos dados: `{vendas.attrs.get('source', 'desconhecido')}`")
except Exception as e:
    st.error(f"Erro ao carregar dados: {e}")
