"""Página 2 — Vendas & Performance."""

import streamlit as st

from src.components.theme import apply_theme
from src.components.filters import render_sidebar_filters, apply_filters
from src.components.kpi_card import kpi_card
from src.data.loaders import load_vendas, load_produtos, load_clientes
from src.data.transformations import (
    kpis_periodo, serie_temporal_receita, media_movel,
    heatmap_dia_hora, pareto_produtos, evolucao_canal,
    distribuicao_ticket, funil_vendas, sazonalidade_mensal,
)
from src.charts import sales as ch
from src.utils.formatters import fmt_brl, fmt_brl_compact, fmt_int, fmt_pct

st.set_page_config(page_title="Vendas & Performance", page_icon="💰", layout="wide")
apply_theme()

st.title("💰 Vendas & Performance")
st.caption("Diagnóstico granular da operação comercial — picos, sazonalidade, conversão e mix")

# ---------- DADOS ----------
vendas = load_vendas()
produtos = load_produtos()
clientes = load_clientes()

# ---------- FILTROS GLOBAIS ----------
filtros = render_sidebar_filters(vendas, mostrar_canal=True, mostrar_meta=False)
v = apply_filters(vendas, filtros)

# ---------- KPIs ----------
st.markdown("### Indicadores do Período")
k = kpis_periodo(v)
tickets = distribuicao_ticket(v)
ticket_mediana = float(tickets.median()) if not tickets.empty else 0.0
ticket_p90 = float(tickets.quantile(0.9)) if not tickets.empty else 0.0

c1, c2, c3, c4 = st.columns(4)
with c1: kpi_card("Receita", k["receita"], fmt_brl_compact)
with c2: kpi_card("Ticket Médio", k["ticket_medio"], fmt_brl)
with c3: kpi_card("Ticket Mediano", ticket_mediana, fmt_brl, help_text="50% das vendas ficam abaixo deste valor")
with c4: kpi_card("Ticket P90", ticket_p90, fmt_brl, help_text="90% das vendas ficam abaixo deste valor")

c5, c6, c7, c8 = st.columns(4)
with c5: kpi_card("Transações", k["n_vendas"], fmt_int)
with c6: kpi_card("Itens Vendidos", k["itens"], fmt_int)
with c7: kpi_card("Itens / Venda", k["itens"] / k["n_vendas"] if k["n_vendas"] else 0, lambda x: f"{x:.2f}".replace(".", ","))
with c8: kpi_card("Mix Ecom", k["mix_ecommerce"], fmt_pct)

st.markdown("---")

# ---------- LINHA 1: Série temporal com MM7 ----------
serie = media_movel(serie_temporal_receita(v, freq="D"), janela=7)
st.plotly_chart(ch.evolucao_diaria_mm(serie), use_container_width=True)

# ---------- LINHA 2: Heatmap dia x hora + Distribuição ticket ----------
col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(ch.heatmap_dia_hora(heatmap_dia_hora(v)), use_container_width=True)
with col2:
    st.plotly_chart(ch.distribuicao_ticket(tickets), use_container_width=True)

# ---------- LINHA 3: Pareto produtos ----------
st.plotly_chart(ch.pareto_produtos(pareto_produtos(v, produtos, top_n=30)), use_container_width=True)

# ---------- LINHA 4: Evolução canal + Funil ----------
col3, col4 = st.columns([2, 1])
with col3:
    st.plotly_chart(ch.evolucao_canal(evolucao_canal(v, freq="W")), use_container_width=True)
with col4:
    st.plotly_chart(ch.funil_vendas(funil_vendas(v, clientes, produtos)), use_container_width=True)

# ---------- LINHA 5: Sazonalidade (usa TODAS as vendas, ignora período) ----------
st.markdown("### Visão Macro (todos os dados)")
st.plotly_chart(ch.sazonalidade_mensal(sazonalidade_mensal(vendas)), use_container_width=True)

# ---------- INSIGHTS ----------
st.markdown("---")
st.markdown("### 💡 Insights do Período")

if not v.empty:
    hm = heatmap_dia_hora(v)
    par = pareto_produtos(v, produtos, top_n=50)

    # melhor dia/hora
    melhor_dia, melhor_hora = "—", "—"
    if not hm.empty:
        idx = hm.stack().idxmax()
        melhor_dia, melhor_hora = idx[0], f"{idx[1]:02d}h"

    # produtos pra atingir 80%
    n80 = int((par["pct_acumulado"] <= 0.80).sum()) + 1 if not par.empty else 0
    pct_top10 = float(par.head(10)["receita"].sum() / par["receita"].sum()) if not par.empty else 0

    st.markdown(f"""
    - 🔥 **Pico de vendas:** {melhor_dia} às {melhor_hora}
    - 📊 **Concentração Pareto:** apenas **{n80}** produtos respondem por **80%** da receita
    - 🏆 **Top 10 produtos** representam **{fmt_pct(pct_top10)}** da receita
    - 💰 **Ticket mediano** (R$ {fmt_brl(ticket_mediana).replace('R$ ', '')}) está
      **{fmt_pct((k['ticket_medio'] - ticket_mediana) / ticket_mediana) if ticket_mediana else '0%'}**
      abaixo do ticket médio — sinal de **outliers altos** puxando a média
    - 🌊 Canal **{'ecommerce' if k['mix_ecommerce'] > 0.5 else 'loja física'}** lidera o mix
      com {fmt_pct(max(k['mix_ecommerce'], 1 - k['mix_ecommerce']))}
    """)
else:
    st.info("Selecione um período com dados para ver os insights.")
