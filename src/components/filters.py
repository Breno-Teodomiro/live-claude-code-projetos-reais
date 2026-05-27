"""Filtros globais persistentes via st.session_state."""

from datetime import date
from typing import Iterable
import pandas as pd
import streamlit as st


def init_filters(vendas: pd.DataFrame) -> None:
    """Inicializa filtros globais no session_state se ainda não existirem."""
    if vendas.empty:
        return
    if "filtro_periodo" not in st.session_state:
        fim = vendas["data_venda"].max().date()
        inicio = (vendas["data_venda"].max() - pd.Timedelta(days=90)).date()
        st.session_state["filtro_periodo"] = (inicio, fim)
    if "filtro_canais" not in st.session_state:
        st.session_state["filtro_canais"] = sorted(vendas["canal_venda"].dropna().unique().tolist())


def render_sidebar_filters(vendas: pd.DataFrame, mostrar_canal: bool = True, mostrar_meta: bool = False) -> dict:
    """Renderiza filtros na sidebar e retorna dict com valores selecionados."""
    init_filters(vendas)
    with st.sidebar:
        st.markdown("### 🎛️ Filtros Globais")

        min_date = vendas["data_venda"].min().date() if not vendas.empty else None
        max_date = vendas["data_venda"].max().date() if not vendas.empty else None

        # Presets
        preset = st.radio("Período rápido", ["Custom", "7d", "30d", "90d", "YTD", "Tudo"], horizontal=True, index=0, key="preset_periodo")
        if preset != "Custom" and not vendas.empty:
            fim = max_date
            if preset == "7d":
                inicio = fim - pd.Timedelta(days=7).to_pytimedelta()
            elif preset == "30d":
                inicio = fim - pd.Timedelta(days=30).to_pytimedelta()
            elif preset == "90d":
                inicio = fim - pd.Timedelta(days=90).to_pytimedelta()
            elif preset == "YTD":
                inicio = date(fim.year, 1, 1)
            else:
                inicio = min_date
            st.session_state["filtro_periodo"] = (inicio, fim)

        periodo = st.date_input(
            "Período",
            value=st.session_state["filtro_periodo"],
            min_value=min_date, max_value=max_date,
            key="date_range_input",
        )
        if isinstance(periodo, tuple) and len(periodo) == 2:
            st.session_state["filtro_periodo"] = periodo

        if mostrar_canal:
            canais_disponiveis = sorted(vendas["canal_venda"].dropna().unique().tolist())
            sel_canais = st.multiselect(
                "Canal de venda",
                canais_disponiveis,
                default=st.session_state["filtro_canais"],
                key="canais_input",
            )
            st.session_state["filtro_canais"] = sel_canais or canais_disponiveis

        meta_growth = None
        if mostrar_meta:
            meta_growth = st.slider("Meta de crescimento %", -20, 50, 10, 5, key="meta_growth_input") / 100

        st.markdown("---")
        st.caption(f"Fonte: `{vendas.attrs.get('source', '?')}`")

    inicio, fim = st.session_state["filtro_periodo"]
    return {
        "inicio": pd.Timestamp(inicio, tz="UTC"),
        "fim": pd.Timestamp(fim, tz="UTC") + pd.Timedelta(days=1) - pd.Timedelta(microseconds=1),
        "canais": st.session_state["filtro_canais"],
        "meta_growth": meta_growth,
    }


def apply_filters(vendas: pd.DataFrame, filtros: dict) -> pd.DataFrame:
    """Aplica filtros a um DataFrame de vendas."""
    if vendas.empty:
        return vendas
    df = vendas[vendas["canal_venda"].isin(filtros["canais"])]
    df = df[(df["data_venda"] >= filtros["inicio"]) & (df["data_venda"] <= filtros["fim"])]
    return df
