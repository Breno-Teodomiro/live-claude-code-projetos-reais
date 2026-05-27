"""Gráficos da página Visão Executiva."""

import json
from pathlib import Path
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

from src.utils.colors import COLORS, CHANNEL_COLORS, SEQUENTIAL_BLUE
from src.utils.formatters import fmt_brl, fmt_brl_compact, fmt_int

PLOTLY_LAYOUT = dict(
    paper_bgcolor=COLORS["bg_secondary"],
    plot_bgcolor=COLORS["bg_secondary"],
    font=dict(family="Inter, sans-serif", color=COLORS["text_primary"], size=12),
    margin=dict(l=40, r=20, t=50, b=40),
    xaxis=dict(gridcolor="rgba(255,255,255,0.05)", linecolor="rgba(255,255,255,0.1)"),
    yaxis=dict(gridcolor="rgba(255,255,255,0.05)", linecolor="rgba(255,255,255,0.1)"),
    hoverlabel=dict(bgcolor=COLORS["bg_tertiary"], font=dict(color=COLORS["text_primary"])),
)


def grafico_yoy(df_yoy: pd.DataFrame) -> go.Figure:
    """Linha + área comparando últimos 2 anos por mês."""
    fig = go.Figure()
    if df_yoy.empty:
        fig.update_layout(title="Sem dados para comparativo YoY", **PLOTLY_LAYOUT)
        return fig

    anos = sorted(df_yoy["ano"].unique())
    cores = {anos[-1]: COLORS["accent"], anos[0]: COLORS["text_muted"]} if len(anos) > 1 else {anos[0]: COLORS["accent"]}

    meses_pt = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]

    for ano in anos:
        sub = df_yoy[df_yoy["ano"] == ano]
        é_atual = ano == anos[-1]
        fig.add_trace(go.Scatter(
            x=[meses_pt[m - 1] for m in sub["mes"]],
            y=sub["receita"],
            name=str(ano),
            mode="lines+markers",
            line=dict(color=cores[ano], width=3 if é_atual else 2, dash="solid" if é_atual else "dot"),
            marker=dict(size=8 if é_atual else 5),
            fill="tozeroy" if é_atual else None,
            fillcolor=f"rgba(59,130,246,0.12)" if é_atual else None,
            hovertemplate=f"<b>{ano}</b><br>%{{x}}: <b>R$ %{{y:,.0f}}</b><extra></extra>",
        ))

    fig.update_layout(
        title=dict(text="📈 Receita Mensal — Comparativo Year-over-Year", font=dict(size=16)),
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=380,
        **{k: v for k, v in PLOTLY_LAYOUT.items() if k not in ("xaxis", "yaxis")},
    )
    fig.update_xaxes(**PLOTLY_LAYOUT["xaxis"])
    fig.update_yaxes(**PLOTLY_LAYOUT["yaxis"], tickprefix="R$ ", tickformat=",.0f")
    return fig


def gauge_meta(realizado: float, meta: float, pct: float) -> go.Figure:
    cor = COLORS["danger"] if pct < 0.70 else COLORS["warning"] if pct < 0.95 else COLORS["success"]
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=realizado,
        number=dict(prefix="R$ ", valueformat=",.0f", font=dict(size=28, color=COLORS["text_primary"])),
        delta=dict(reference=meta, relative=False, valueformat=",.0f", increasing=dict(color=COLORS["success"]), decreasing=dict(color=COLORS["danger"])),
        gauge=dict(
            axis=dict(range=[0, max(meta, realizado) * 1.1], tickcolor=COLORS["text_muted"], tickfont=dict(color=COLORS["text_muted"], size=10)),
            bar=dict(color=cor, thickness=0.7),
            bgcolor=COLORS["bg_tertiary"],
            borderwidth=0,
            steps=[
                dict(range=[0, meta * 0.70], color="rgba(239,68,68,0.15)"),
                dict(range=[meta * 0.70, meta * 0.95], color="rgba(245,158,11,0.15)"),
                dict(range=[meta * 0.95, meta], color="rgba(16,185,129,0.15)"),
            ],
            threshold=dict(line=dict(color=COLORS["text_primary"], width=3), thickness=0.9, value=meta),
        ),
    ))
    fig.update_layout(
        title=dict(text=f"🎯 Meta vs Realizado ({pct*100:.1f}%)", font=dict(size=16)),
        height=380,
        paper_bgcolor=COLORS["bg_secondary"],
        font=dict(color=COLORS["text_primary"], family="Inter, sans-serif"),
        margin=dict(l=20, r=20, t=60, b=20),
    )
    return fig


def donut_canal(df_canal: pd.DataFrame) -> go.Figure:
    if df_canal.empty:
        return go.Figure().update_layout(title="Sem dados de canal", **PLOTLY_LAYOUT)
    cores = [CHANNEL_COLORS.get(c, COLORS["accent"]) for c in df_canal["canal_venda"]]
    fig = go.Figure(go.Pie(
        labels=[c.replace("_", " ").title() for c in df_canal["canal_venda"]],
        values=df_canal["receita"],
        hole=0.65,
        marker=dict(colors=cores, line=dict(color=COLORS["bg_primary"], width=2)),
        textinfo="label+percent",
        textfont=dict(size=13, color=COLORS["text_primary"]),
        hovertemplate="<b>%{label}</b><br>Receita: R$ %{value:,.0f}<br>Mix: %{percent}<extra></extra>",
    ))
    total = df_canal["receita"].sum()
    fig.add_annotation(text=f"<b>{fmt_brl_compact(total)}</b><br><span style='font-size:11px;color:#9CA3AF'>Receita total</span>",
                       showarrow=False, font=dict(size=18, color=COLORS["text_primary"]))
    fig.update_layout(
        title=dict(text="📊 Mix de Canal", font=dict(size=16)),
        showlegend=False,
        height=360,
        paper_bgcolor=COLORS["bg_secondary"],
        font=dict(color=COLORS["text_primary"], family="Inter, sans-serif"),
        margin=dict(l=20, r=20, t=60, b=20),
    )
    return fig


def top_produtos_bar(df_top: pd.DataFrame) -> go.Figure:
    if df_top.empty:
        return go.Figure().update_layout(title="Sem dados", **PLOTLY_LAYOUT)
    df_top = df_top.sort_values("receita")
    fig = go.Figure(go.Bar(
        x=df_top["receita"],
        y=df_top["nome_produto"],
        orientation="h",
        marker=dict(
            color=df_top["receita"],
            colorscale=[[0, "#1E3A5F"], [1, "#3B82F6"]],
            line=dict(color=COLORS["accent"], width=0),
        ),
        text=[fmt_brl_compact(v) for v in df_top["receita"]],
        textposition="outside",
        textfont=dict(color=COLORS["text_primary"], size=11),
        hovertemplate="<b>%{y}</b><br>Receita: R$ %{x:,.0f}<br>Categoria: %{customdata}<extra></extra>",
        customdata=df_top["categoria"],
    ))
    fig.update_layout(
        title=dict(text="🥇 Top 10 Produtos por Receita", font=dict(size=16)),
        height=440,
        showlegend=False,
        **{k: v for k, v in PLOTLY_LAYOUT.items() if k not in ("xaxis", "yaxis")},
    )
    fig.update_xaxes(**PLOTLY_LAYOUT["xaxis"], tickprefix="R$ ", tickformat=",.0f", title="")
    fig.update_yaxes(**PLOTLY_LAYOUT["yaxis"], title="")
    return fig


def mapa_brasil(df_estados: pd.DataFrame, geojson_path: Path) -> go.Figure:
    if df_estados.empty or not geojson_path.exists():
        fig = go.Figure()
        fig.update_layout(title="Mapa indisponível", **PLOTLY_LAYOUT, height=440)
        return fig
    with open(geojson_path, "r", encoding="utf-8") as f:
        geo = json.load(f)

    fig = px.choropleth(
        df_estados,
        geojson=geo,
        locations="estado",
        featureidkey="properties.sigla",
        color="receita",
        color_continuous_scale=SEQUENTIAL_BLUE,
        hover_data={"estado": True, "receita": ":,.0f", "n_vendas": True, "clientes": True},
    )
    fig.update_geos(
        fitbounds="locations",
        visible=False,
        bgcolor=COLORS["bg_secondary"],
    )
    fig.update_layout(
        title=dict(text="🗺️ Receita por Estado", font=dict(size=16)),
        height=440,
        paper_bgcolor=COLORS["bg_secondary"],
        plot_bgcolor=COLORS["bg_secondary"],
        font=dict(family="Inter, sans-serif", color=COLORS["text_primary"]),
        margin=dict(l=0, r=0, t=60, b=0),
        coloraxis_colorbar=dict(
            title="Receita",
            tickprefix="R$ ",
            tickformat=",.0f",
            thickness=10,
            len=0.7,
            tickfont=dict(color=COLORS["text_muted"]),
        ),
    )
    return fig
