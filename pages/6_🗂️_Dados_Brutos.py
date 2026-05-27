"""Página 6 — Dados Brutos (auditoria e exportação)."""

import io
import pandas as pd
import streamlit as st

from src.components.theme import apply_theme
from src.data.loaders import load_vendas, load_clientes, load_produtos, load_precos_competidores

st.set_page_config(page_title="Dados Brutos", page_icon="🗂️", layout="wide")
apply_theme()

st.title("🗂️ Dados Brutos")
st.caption("Auditoria livre, filtros dinâmicos e exportação CSV / Excel")

# ---------- SELETOR DE TABELA ----------
TABELAS = {
    "💰 Vendas":              ("vendas", load_vendas),
    "👥 Clientes":            ("clientes", load_clientes),
    "📦 Produtos":            ("produtos", load_produtos),
    "🎯 Preços Competidores": ("precos_competidores", load_precos_competidores),
}

st.markdown("### Selecione a Tabela")
nome_tab = st.radio("", list(TABELAS.keys()), horizontal=True, label_visibility="collapsed")
nome_arquivo, fn = TABELAS[nome_tab]
df = fn()

# ---------- METADADOS ----------
c1, c2, c3, c4 = st.columns(4)
c1.metric("Linhas", f"{len(df):,}".replace(",", "."))
c2.metric("Colunas", len(df.columns))
c3.metric("Fonte", df.attrs.get("source", "?"))
c4.metric("Memória", f"{df.memory_usage(deep=True).sum() / 1024:.1f} KB")

st.markdown("---")

# ---------- FILTROS DINÂMICOS ----------
st.markdown("### 🔎 Filtros")
filtros_col = st.columns(3)
df_filt = df.copy()

# Busca global texto
with filtros_col[0]:
    busca = st.text_input("🔍 Busca global (texto em qualquer coluna)")
    if busca:
        mask = pd.Series(False, index=df_filt.index)
        for col in df_filt.columns:
            mask = mask | df_filt[col].astype(str).str.contains(busca, case=False, na=False, regex=False)
        df_filt = df_filt[mask]

# Filtro por coluna específica (categórica)
with filtros_col[1]:
    colunas_cat = [c for c in df_filt.columns if df_filt[c].dtype == "object" and df_filt[c].nunique() < 30]
    if colunas_cat:
        col_sel = st.selectbox("Coluna categórica para filtrar", ["(nenhuma)"] + colunas_cat)
        if col_sel != "(nenhuma)":
            valores = sorted(df_filt[col_sel].dropna().unique().tolist())
            sel = st.multiselect(f"Valores de '{col_sel}'", valores, default=valores)
            df_filt = df_filt[df_filt[col_sel].isin(sel)]

# Filtro por período (se houver coluna de data)
with filtros_col[2]:
    colunas_data = [c for c in df_filt.columns if "data" in c.lower() and pd.api.types.is_datetime64_any_dtype(df_filt[c])]
    if colunas_data:
        col_data = st.selectbox("Coluna de data", colunas_data)
        min_d = df_filt[col_data].min().date() if not df_filt.empty else None
        max_d = df_filt[col_data].max().date() if not df_filt.empty else None
        if min_d and max_d:
            periodo = st.date_input("Período", value=(min_d, max_d), min_value=min_d, max_value=max_d)
            if isinstance(periodo, tuple) and len(periodo) == 2:
                ini = pd.Timestamp(periodo[0], tz="UTC")
                fim = pd.Timestamp(periodo[1], tz="UTC") + pd.Timedelta(days=1) - pd.Timedelta(microseconds=1)
                df_filt = df_filt[(df_filt[col_data] >= ini) & (df_filt[col_data] <= fim)]

st.caption(f"Mostrando **{len(df_filt):,}** de **{len(df):,}** linhas".replace(",", "."))

# ---------- TABELA ----------
st.markdown("### 📋 Dados")
try:
    from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
    gob = GridOptionsBuilder.from_dataframe(df_filt)
    gob.configure_default_column(filterable=True, sortable=True, resizable=True, wrapText=True)
    gob.configure_pagination(paginationAutoPageSize=False, paginationPageSize=25)
    gob.configure_side_bar()
    AgGrid(
        df_filt, gridOptions=gob.build(),
        theme="balham-dark", height=520, fit_columns_on_grid_load=True,
        update_mode=GridUpdateMode.NO_UPDATE, allow_unsafe_jscode=True,
    )
except Exception:
    st.dataframe(df_filt, use_container_width=True, height=520, hide_index=True)

# ---------- EXPORTAÇÃO ----------
st.markdown("---")
st.markdown("### ⬇️ Exportar Dados Filtrados")
exp_col1, exp_col2 = st.columns(2)
with exp_col1:
    st.download_button(
        "⬇️ CSV (UTF-8)",
        df_filt.to_csv(index=False).encode("utf-8"),
        f"{nome_arquivo}_filtrado.csv",
        mime="text/csv",
        use_container_width=True,
    )
with exp_col2:
    try:
        buf = io.BytesIO()
        with pd.ExcelWriter(buf, engine="openpyxl") as writer:
            df_filt.to_excel(writer, index=False, sheet_name=nome_arquivo[:31])
        st.download_button(
            "⬇️ Excel (.xlsx)",
            buf.getvalue(),
            f"{nome_arquivo}_filtrado.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )
    except ModuleNotFoundError:
        st.button("⬇️ Excel (instalar openpyxl)", disabled=True, use_container_width=True)

# ---------- ESTATÍSTICAS RÁPIDAS ----------
with st.expander("📊 Estatísticas descritivas das colunas numéricas"):
    numericas = df_filt.select_dtypes(include="number")
    if not numericas.empty:
        st.dataframe(numericas.describe().T, use_container_width=True)
    else:
        st.info("Nenhuma coluna numérica nesta tabela.")
