"""Página 1 — Visão Executiva."""

from pathlib import Path
import streamlit as st

from src.components.theme import apply_theme
from src.components.kpi_card import kpi_card
from src.data.loaders import load_vendas, load_clientes, load_produtos
from src.data.transformations import (
    kpis_com_delta, receita_yoy, receita_por_estado, receita_por_canal,
    top_produtos, meta_e_realizado, periodo_default, filter_periodo,
)
from src.charts.executive import grafico_yoy, gauge_meta, donut_canal, top_produtos_bar, mapa_brasil
from src.utils.formatters import fmt_brl_compact, fmt_int, fmt_pct, fmt_brl
from src.utils.constants import META_CRESCIMENTO_DEFAULT

st.set_page_config(page_title="Visão Executiva", page_icon="📊", layout="wide")
apply_theme()

# ---------- HEADER ----------
st.title("📊 Visão Executiva")
st.caption("Saúde do negócio em 10 segundos — CEO e Diretoria")

# ---------- DADOS ----------
vendas = load_vendas()
clientes = load_clientes()
produtos = load_produtos()

# ---------- FILTROS ----------
inicio_def, fim_def = periodo_default(vendas)

with st.sidebar:
    st.markdown("### 🎛️ Filtros")
    periodo = st.date_input(
        "Período",
        value=(inicio_def.date(), fim_def.date()),
        min_value=vendas["data_venda"].min().date() if not vendas.empty else None,
        max_value=vendas["data_venda"].max().date() if not vendas.empty else None,
    )
    if isinstance(periodo, tuple) and len(periodo) == 2:
        inicio, fim = periodo
    else:
        inicio, fim = inicio_def.date(), fim_def.date()

    canais = sorted(vendas["canal_venda"].dropna().unique().tolist())
    sel_canais = st.multiselect("Canal", canais, default=canais)

    meta_growth = st.slider("Meta de crescimento %", min_value=-20, max_value=50, value=int(META_CRESCIMENTO_DEFAULT * 100), step=5) / 100
    st.caption(f"Fonte: `{vendas.attrs.get('source', '?')}`")

# Filtrar
import pandas as pd
inicio_dt = pd.Timestamp(inicio, tz="UTC")
fim_dt = pd.Timestamp(fim, tz="UTC") + pd.Timedelta(days=1) - pd.Timedelta(microseconds=1)

vendas_f = vendas[vendas["canal_venda"].isin(sel_canais)]
vendas_periodo = filter_periodo(vendas_f, "data_venda", inicio_dt, fim_dt)

# ---------- KPIs ----------
st.markdown("### Indicadores Principais")

kpis = kpis_com_delta(vendas_f, inicio_dt, fim_dt)

c1, c2, c3, c4 = st.columns(4)
with c1:
    kpi_card("Receita Total", kpis["receita"]["valor"], fmt_brl_compact, kpis["receita"]["delta"])
with c2:
    kpi_card("Ticket Médio", kpis["ticket_medio"]["valor"], fmt_brl, kpis["ticket_medio"]["delta"])
with c3:
    kpi_card("Volume de Vendas", kpis["n_vendas"]["valor"], fmt_int, kpis["n_vendas"]["delta"])
with c4:
    kpi_card("Itens Vendidos", kpis["itens"]["valor"], fmt_int, kpis["itens"]["delta"])

c5, c6, c7, c8 = st.columns(4)
with c5:
    kpi_card("Clientes Ativos", kpis["clientes_ativos"]["valor"], fmt_int, kpis["clientes_ativos"]["delta"])
with c6:
    kpi_card("Receita / Cliente", kpis["receita_por_cliente"]["valor"], fmt_brl, kpis["receita_por_cliente"]["delta"])
with c7:
    kpi_card("Mix Ecommerce", kpis["mix_ecommerce"]["valor"], fmt_pct, kpis["mix_ecommerce"]["delta"])
with c8:
    duracao = fim_dt - inicio_dt
    inicio_ant = inicio_dt - duracao
    vendas_ant = filter_periodo(vendas_f, "data_venda", inicio_ant, inicio_dt)
    realizado, meta, pct = meta_e_realizado(vendas_periodo, vendas_ant, growth=meta_growth)
    delta_meta = (realizado - meta) / meta if meta else None
    kpi_card("Meta Atingida", pct, fmt_pct, delta_meta)

st.markdown("---")

# ---------- LINHA 1 — YoY + Meta ----------
col1, col2 = st.columns([2, 1])
with col1:
    st.plotly_chart(grafico_yoy(receita_yoy(vendas_f)), use_container_width=True)
with col2:
    st.plotly_chart(gauge_meta(realizado, meta, pct), use_container_width=True)

# ---------- LINHA 2 — Top Produtos + Mapa ----------
col3, col4 = st.columns([1, 1])
with col3:
    st.plotly_chart(top_produtos_bar(top_produtos(vendas_periodo, produtos, n=10)), use_container_width=True)
with col4:
    geojson_path = Path(__file__).resolve().parents[1] / "assets" / "geo" / "br_states.geojson"
    st.plotly_chart(mapa_brasil(receita_por_estado(vendas_periodo, clientes), geojson_path), use_container_width=True)

# ---------- LINHA 3 — Donut canal ----------
col5, col6 = st.columns([1, 2])
with col5:
    st.plotly_chart(donut_canal(receita_por_canal(vendas_periodo)), use_container_width=True)
with col6:
    st.markdown("### 💡 Resumo do Período")
    if kpis["receita"]["delta"] is not None:
        sentido = "crescimento" if kpis["receita"]["delta"] > 0 else "queda"
        cor = "🟢" if kpis["receita"]["delta"] > 0 else "🔴"
        st.markdown(f"""
        - {cor} Receita em **{sentido}** de **{fmt_pct(abs(kpis['receita']['delta']))}** vs período anterior
        - 💰 Ticket médio: **{fmt_brl(kpis['ticket_medio']['valor'])}**
        - 👥 **{fmt_int(kpis['clientes_ativos']['valor'])}** clientes ativos no período
        - 🎯 Meta: **{fmt_pct(pct)}** atingida ({fmt_brl_compact(realizado)} de {fmt_brl_compact(meta)})
        - 📊 Canal ecommerce representa **{fmt_pct(kpis['mix_ecommerce']['valor'])}** da receita
        """)
    else:
        st.info("Selecione um período com dados comparáveis para ver o resumo.")
