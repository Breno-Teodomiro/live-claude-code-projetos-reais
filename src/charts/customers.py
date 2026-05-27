"""Gráficos da página Clientes & Geografia."""

import json
from pathlib import Path
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

from src.utils.colors import COLORS, SEQUENTIAL_BLUE, DIVERGING_RDYLGN
from src.utils.formatters import fmt_brl_compact

PLOTLY_LAYOUT = dict(
    paper_bgcolor=COLORS["bg_secondary"],
    plot_bgcolor=COLORS["bg_secondary"],
    font=dict(family="Inter, sans-serif", color=COLORS["text_primary"], size=12),
    margin=dict(l=40, r=20, t=60, b=40),
    hoverlabel=dict(bgcolor=COLORS["bg_tertiary"], font=dict(color=COLORS["text_primary"])),
)
AXIS = dict(gridcolor="rgba(255,255,255,0.05)", linecolor="rgba(255,255,255,0.1)")

SEG_COLORS = {
    "Campeões": "#10B981",
    "Leais": "#06B6D4",
    "Potenciais": "#3B82F6",
    "Novos": "#8B5CF6",
    "Promissores": "#A78BFA",
    "Atenção": "#F59E0B",
    "Em Risco": "#F97316",
    "Não Posso Perder": "#EF4444",
    "Hibernando": "#6B7280",
    "Perdidos": "#374151",
}


def _empty(title: str) -> go.Figure:
    return go.Figure().update_layout(title=title, height=320, **PLOTLY_LAYOUT)


def matriz_rfm(df_rfm: pd.DataFrame) -> go.Figure:
    if df_rfm.empty:
        return _empty("Sem dados RFM")
    fig = go.Figure()
    for seg, sub in df_rfm.groupby("segmento"):
        fig.add_trace(go.Scatter(
            x=sub["recencia"], y=sub["frequencia"],
            mode="markers",
            name=seg,
            marker=dict(
                size=sub["monetario"] / max(df_rfm["monetario"].max() / 40, 1),
                sizemin=8,
                color=SEG_COLORS.get(seg, COLORS["accent"]),
                line=dict(color=COLORS["bg_primary"], width=1),
                opacity=0.85,
            ),
            hovertemplate=(
                "<b>" + seg + "</b><br>"
                "Recência: %{x} dias<br>"
                "Frequência: %{y} vendas<br>"
                "Monetário: R$ %{marker.size:,.0f}<extra></extra>"
            ),
            customdata=sub["monetario"],
        ))
    fig.update_layout(
        title=dict(text="🎯 Matriz RFM (tamanho = valor monetário)", font=dict(size=16)),
        xaxis=dict(**AXIS, title="Recência (dias desde última compra)", autorange="reversed"),
        yaxis=dict(**AXIS, title="Frequência (nº de vendas)"),
        height=440,
        legend=dict(orientation="v", yanchor="top", y=1, xanchor="left", x=1.02, bgcolor="rgba(0,0,0,0)"),
        **PLOTLY_LAYOUT,
    )
    return fig


def barras_segmentos(df_resumo: pd.DataFrame) -> go.Figure:
    if df_resumo.empty:
        return _empty("Sem dados")
    df_resumo = df_resumo.sort_values("n_clientes", ascending=True)
    cores = [SEG_COLORS.get(s, COLORS["accent"]) for s in df_resumo["segmento"]]
    fig = go.Figure(go.Bar(
        y=[f"{r['icone']} {r['segmento']}" for _, r in df_resumo.iterrows()],
        x=df_resumo["n_clientes"],
        orientation="h",
        marker=dict(color=cores),
        text=[f"{int(n)} ({p*100:.0f}%)" for n, p in zip(df_resumo["n_clientes"], df_resumo["pct"])],
        textposition="outside",
        textfont=dict(color=COLORS["text_primary"]),
        hovertemplate=(
            "<b>%{y}</b><br>"
            "Clientes: %{x}<br>"
            "Receita total: R$ %{customdata:,.0f}<extra></extra>"
        ),
        customdata=df_resumo["monetario_total"],
    ))
    fig.update_layout(
        title=dict(text="📊 Clientes por Segmento RFM", font=dict(size=16)),
        xaxis=dict(**AXIS, title="Nº de clientes"),
        yaxis=dict(**AXIS, title=""),
        showlegend=False,
        height=440,
        **PLOTLY_LAYOUT,
    )
    return fig


def cohort_heatmap(pivot: pd.DataFrame) -> go.Figure:
    if pivot.empty:
        return _empty("Sem dados de cohort")
    fig = go.Figure(go.Heatmap(
        z=pivot.values * 100,
        x=[f"M+{c}" for c in pivot.columns],
        y=pivot.index,
        colorscale=[[0, COLORS["bg_tertiary"]], [0.4, "#1E3A5F"], [0.7, "#3B82F6"], [1, "#10B981"]],
        zmin=0, zmax=100,
        hovertemplate="Cohort %{y}<br>%{x}: %{z:.0f}% retidos<extra></extra>",
        text=[[f"{v*100:.0f}%" if v > 0 else "" for v in row] for row in pivot.values],
        texttemplate="%{text}",
        textfont=dict(size=10, color=COLORS["text_primary"]),
        colorbar=dict(title="% retenção", thickness=10, tickfont=dict(color=COLORS["text_muted"]), ticksuffix="%"),
    ))
    fig.update_layout(
        title=dict(text="🔄 Cohort de Retenção (%)", font=dict(size=16)),
        xaxis=dict(**AXIS, title="Meses desde primeiro contato"),
        yaxis=dict(**AXIS, title="Mês cohort", autorange="reversed"),
        height=420,
        **PLOTLY_LAYOUT,
    )
    return fig


def curva_abc(df_abc: pd.DataFrame, top: int = 20) -> go.Figure:
    if df_abc.empty:
        return _empty("Sem dados ABC")
    df = df_abc.head(top).copy()
    cores_classe = {"A": COLORS["success"], "B": COLORS["warning"], "C": COLORS["danger"]}
    fig = go.Figure(go.Bar(
        x=df["receita"],
        y=df["nome_cliente"].fillna(df["id_cliente"]),
        orientation="h",
        marker=dict(color=[cores_classe[c] for c in df["classe"]]),
        text=[f"{c} · {p*100:.0f}%" for c, p in zip(df["classe"], df["pct_acumulado"])],
        textposition="outside",
        textfont=dict(color=COLORS["text_primary"], size=10),
        hovertemplate="<b>%{y}</b><br>Receita: R$ %{x:,.0f}<br>Classe: %{customdata}<extra></extra>",
        customdata=df["classe"],
    ))
    fig.update_layout(
        title=dict(text=f"🏆 Top {top} Clientes — Curva ABC", font=dict(size=16)),
        xaxis=dict(**AXIS, title="Receita (R$)", tickprefix="R$ ", tickformat=",.0f"),
        yaxis=dict(**AXIS, title="", autorange="reversed"),
        height=460,
        **PLOTLY_LAYOUT,
    )
    return fig


def treemap_geo(df_geo: pd.DataFrame) -> go.Figure:
    if df_geo.empty:
        return _empty("Sem dados geográficos")
    fig = px.treemap(
        df_geo, path=["pais", "estado"], values="receita",
        color="receita", color_continuous_scale=SEQUENTIAL_BLUE,
        custom_data=["clientes"],
    )
    fig.update_traces(
        hovertemplate="<b>%{label}</b><br>Receita: R$ %{value:,.0f}<br>Clientes: %{customdata[0]}<extra></extra>",
        marker=dict(line=dict(color=COLORS["bg_primary"], width=2)),
    )
    fig.update_layout(
        title=dict(text="🗺️ Treemap Geográfico (País → Estado)", font=dict(size=16)),
        height=420,
        paper_bgcolor=COLORS["bg_secondary"],
        font=dict(family="Inter, sans-serif", color=COLORS["text_primary"]),
        margin=dict(l=10, r=10, t=60, b=10),
        coloraxis_showscale=False,
    )
    return fig


def mapa_clientes(df_estados: pd.DataFrame, geojson_path: Path) -> go.Figure:
    """Mapa coroplético de clientes por estado."""
    if df_estados.empty or not geojson_path.exists():
        return _empty("Mapa indisponível")
    with open(geojson_path, "r", encoding="utf-8") as f:
        geo = json.load(f)
    fig = px.choropleth(
        df_estados, geojson=geo, locations="estado",
        featureidkey="properties.sigla",
        color="clientes",
        color_continuous_scale=[[0, "#1E3A5F"], [1, "#10B981"]],
        hover_data={"clientes": True, "receita": ":,.0f", "estado": True},
    )
    fig.update_geos(fitbounds="locations", visible=False, bgcolor=COLORS["bg_secondary"])
    fig.update_layout(
        title=dict(text="📍 Densidade de Clientes por Estado", font=dict(size=16)),
        height=420,
        paper_bgcolor=COLORS["bg_secondary"],
        font=dict(family="Inter, sans-serif", color=COLORS["text_primary"]),
        margin=dict(l=0, r=0, t=60, b=0),
        coloraxis_colorbar=dict(title="Clientes", thickness=10, len=0.7, tickfont=dict(color=COLORS["text_muted"])),
    )
    return fig


def aquisicao_retencao(df: pd.DataFrame) -> go.Figure:
    if df.empty:
        return _empty("Sem dados")
    pivot = df.pivot(index="mes", columns="tipo", values="clientes").fillna(0)
    fig = go.Figure()
    if "Recorrente" in pivot.columns:
        fig.add_trace(go.Bar(x=pivot.index, y=pivot["Recorrente"], name="Recorrentes",
                             marker_color=COLORS["accent"],
                             hovertemplate="<b>%{x}</b><br>Recorrentes: %{y}<extra></extra>"))
    if "Novo" in pivot.columns:
        fig.add_trace(go.Bar(x=pivot.index, y=pivot["Novo"], name="Novos",
                             marker_color=COLORS["success"],
                             hovertemplate="<b>%{x}</b><br>Novos: %{y}<extra></extra>"))
    fig.update_layout(
        title=dict(text="🌱 Aquisição vs Retenção (por mês)", font=dict(size=16)),
        xaxis=dict(**AXIS, title=""),
        yaxis=dict(**AXIS, title="Clientes únicos"),
        barmode="stack",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=380,
        **PLOTLY_LAYOUT,
    )
    return fig
