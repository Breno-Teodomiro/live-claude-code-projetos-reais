"""Filtros globais persistentes via st.session_state."""

from datetime import date
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


def _clamp_date(d: date, min_d: date, max_d: date) -> date:
    if d < min_d: return min_d
    if d > max_d: return max_d
    return d


def render_sidebar_filters(vendas: pd.DataFrame, mostrar_canal: bool = True, mostrar_meta: bool = False) -> dict:
    """Renderiza filtros na sidebar e retorna dict com valores selecionados."""
    init_filters(vendas)

    if vendas.empty:
        return {"inicio": pd.Timestamp.now(tz="UTC"), "fim": pd.Timestamp.now(tz="UTC"),
                "canais": [], "meta_growth": None}

    min_date = vendas["data_venda"].min().date()
    max_date = vendas["data_venda"].max().date()

    # Garantir que o filtro persistido está dentro dos limites
    fp = st.session_state["filtro_periodo"]
    fp = (_clamp_date(fp[0], min_date, max_date), _clamp_date(fp[1], min_date, max_date))
    st.session_state["filtro_periodo"] = fp

    # Sincronizar widget state com filtro state (somente na primeira renderização)
    if "date_range_input" not in st.session_state:
        st.session_state["date_range_input"] = fp

    with st.sidebar:
        st.markdown("### 🎛️ Filtros Globais")

        # Presets
        preset = st.radio("Período rápido", ["Custom", "7d", "30d", "90d", "YTD", "Tudo"],
                          horizontal=True, index=0, key="preset_periodo")
        if preset != "Custom":
            fim = max_date
            if preset == "7d":
                inicio = fim - pd.Timedelta(days=7).to_pytimedelta()
            elif preset == "30d":
                inicio = fim - pd.Timedelta(days=30).to_pytimedelta()
            elif preset == "90d":
                inicio = fim - pd.Timedelta(days=90).to_pytimedelta()
            elif preset == "YTD":
                inicio = date(fim.year, 1, 1)
            else:  # Tudo
                inicio = min_date
            inicio = _clamp_date(inicio, min_date, max_date)
            novo = (inicio, fim)
            if st.session_state.get("date_range_input") != novo:
                st.session_state["date_range_input"] = novo
                st.session_state["filtro_periodo"] = novo

        # Date picker — sem 'value=' porque usamos key para state
        periodo = st.date_input(
            "Período",
            min_value=min_date, max_value=max_date,
            key="date_range_input",
        )
        if isinstance(periodo, tuple) and len(periodo) == 2:
            st.session_state["filtro_periodo"] = periodo

        # Canais
        if mostrar_canal:
            canais_disponiveis = sorted(vendas["canal_venda"].dropna().unique().tolist())
            if "canais_input" not in st.session_state:
                st.session_state["canais_input"] = st.session_state["filtro_canais"]
            sel_canais = st.multiselect("Canal de venda", canais_disponiveis, key="canais_input")
            st.session_state["filtro_canais"] = sel_canais or canais_disponiveis

        # Meta growth
        meta_growth = None
        if mostrar_meta:
            meta_growth = st.slider("Meta de crescimento %", -20, 50, 10, 5, key="meta_growth_input") / 100

        st.markdown("---")
        st.caption(f"Fonte: `{vendas.attrs.get('source', '?')}`")

    inicio_dt, fim_dt = st.session_state["filtro_periodo"]
    return {
        "inicio": pd.Timestamp(inicio_dt, tz="UTC"),
        "fim": pd.Timestamp(fim_dt, tz="UTC") + pd.Timedelta(days=1) - pd.Timedelta(microseconds=1),
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
