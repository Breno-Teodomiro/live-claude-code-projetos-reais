"""Página 3 — Clientes & Geografia."""

from pathlib import Path
import pandas as pd
import streamlit as st

from src.components.theme import apply_theme
from src.components.filters import render_sidebar_filters, apply_filters
from src.components.kpi_card import kpi_card
from src.data.loaders import load_vendas, load_clientes
from src.data.transformations import (
    rfm, resumo_rfm, cohort_retencao, abc_clientes,
    distribuicao_geografica, aquisicao_vs_retencao, receita_por_estado,
)
from src.charts import customers as ch
from src.utils.formatters import fmt_brl, fmt_brl_compact, fmt_int, fmt_pct

st.set_page_config(page_title="Clientes & Geografia", page_icon="👥", layout="wide")
apply_theme()

st.title("👥 Clientes & Geografia")
st.caption("Segmentação RFM, retenção, curva ABC e distribuição geográfica")

# ---------- DADOS ----------
vendas = load_vendas()
clientes = load_clientes()

filtros = render_sidebar_filters(vendas, mostrar_canal=True)
v = apply_filters(vendas, filtros)

# ---------- RFM ----------
df_rfm = rfm(v)
df_resumo = resumo_rfm(df_rfm)

# ---------- KPIs ----------
st.markdown("### Indicadores de Clientes")
total_clientes = len(clientes)
ativos = df_rfm["id_cliente"].nunique() if not df_rfm.empty else 0
em_risco = int(df_resumo.loc[df_resumo["segmento"].isin(["Em Risco", "Não Posso Perder"]), "n_clientes"].sum()) if not df_resumo.empty else 0
campeoes = int(df_resumo.loc[df_resumo["segmento"] == "Campeões", "n_clientes"].sum()) if not df_resumo.empty else 0
ltv_medio = float(df_rfm["monetario"].mean()) if not df_rfm.empty else 0
recencia_mediana = float(df_rfm["recencia"].median()) if not df_rfm.empty else 0
freq_mediana = float(df_rfm["frequencia"].median()) if not df_rfm.empty else 0

c1, c2, c3, c4 = st.columns(4)
with c1: kpi_card("Base Total", total_clientes, fmt_int)
with c2: kpi_card("Ativos no Período", ativos, fmt_int)
with c3: kpi_card("🏆 Campeões", campeoes, fmt_int, help_text="R≥4 e F≥4 e M≥4")
with c4: kpi_card("🆘 Em Risco / Não Posso Perder", em_risco, fmt_int, delta_positivo_bom=False, help_text="Clientes valiosos com queda de recência")

c5, c6, c7, c8 = st.columns(4)
with c5: kpi_card("LTV Médio", ltv_medio, fmt_brl)
with c6: kpi_card("Recência Mediana", recencia_mediana, lambda x: f"{int(x)} dias")
with c7: kpi_card("Frequência Mediana", freq_mediana, lambda x: f"{x:.1f}".replace(".", ","))
with c8: kpi_card("% Ativação", ativos / total_clientes if total_clientes else 0, fmt_pct)

st.markdown("---")

# ---------- LINHA 1: RFM Scatter + Barras segmentos ----------
col1, col2 = st.columns([3, 2])
with col1:
    st.plotly_chart(ch.matriz_rfm(df_rfm), use_container_width=True)
with col2:
    st.plotly_chart(ch.barras_segmentos(df_resumo), use_container_width=True)

# ---------- LINHA 2: Cohort ----------
st.plotly_chart(ch.cohort_heatmap(cohort_retencao(v)), use_container_width=True)

# ---------- LINHA 3: ABC ----------
st.plotly_chart(ch.curva_abc(abc_clientes(v, clientes), top=20), use_container_width=True)

# ---------- LINHA 4: Mapa + Treemap geo ----------
col3, col4 = st.columns(2)
with col3:
    df_estados = receita_por_estado(v, clientes)
    geojson_path = Path(__file__).resolve().parents[1] / "assets" / "geo" / "br_states.geojson"
    st.plotly_chart(ch.mapa_clientes(df_estados, geojson_path), use_container_width=True)
with col4:
    st.plotly_chart(ch.treemap_geo(distribuicao_geografica(v, clientes)), use_container_width=True)

# ---------- LINHA 5: Aquisição vs Retenção ----------
st.plotly_chart(ch.aquisicao_retencao(aquisicao_vs_retencao(v)), use_container_width=True)

# ---------- TABELA EXPORTÁVEL ----------
with st.expander("📋 Lista de clientes 'Em Risco' (exportável)"):
    if not df_rfm.empty:
        em_risco_df = df_rfm[df_rfm["segmento"].isin(["Em Risco", "Não Posso Perder", "Atenção"])].merge(
            clientes[["id_cliente", "nome_cliente", "estado"]], on="id_cliente", how="left"
        ).sort_values("monetario", ascending=False)
        st.dataframe(
            em_risco_df[["nome_cliente", "estado", "segmento", "recencia", "frequencia", "monetario"]],
            use_container_width=True, hide_index=True,
        )
        st.download_button(
            "⬇️ Exportar CSV",
            em_risco_df.to_csv(index=False).encode("utf-8"),
            "clientes_em_risco.csv",
            mime="text/csv",
        )
    else:
        st.info("Sem dados no período selecionado.")

# ---------- INSIGHTS ----------
st.markdown("---")
st.markdown("### 💡 Insights")

if not df_rfm.empty and not df_resumo.empty:
    top_seg = df_resumo.iloc[0]
    pct_em_risco = em_risco / ativos if ativos else 0
    pct_campeoes = campeoes / ativos if ativos else 0
    pct_ativos = ativos / total_clientes if total_clientes else 0

    st.markdown(f"""
    - 👥 **{fmt_pct(pct_ativos)}** da base está ativa no período ({ativos} de {total_clientes})
    - 🏆 **{fmt_pct(pct_campeoes)}** dos ativos são **Campeões** ({campeoes} clientes)
    - 🚨 **{fmt_pct(pct_em_risco)}** dos ativos estão em **risco** — ação imediata recomendada
    - 💰 **LTV médio** por cliente ativo: **{fmt_brl(ltv_medio)}**
    - 📌 Maior segmento por receita: **{top_seg['icone']} {top_seg['segmento']}**
      ({int(top_seg['n_clientes'])} clientes, {fmt_brl_compact(top_seg['monetario_total'])} de receita)
    - ⏱️ **{int(recencia_mediana)} dias** é a mediana de recência — quanto menor, mais saudável a base
    """)
else:
    st.info("Selecione um período com dados para ver os insights.")
