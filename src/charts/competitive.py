"""Gráficos da página Inteligência Competitiva."""

import pandas as pd
import plotly.graph_objects as go

from src.utils.colors import COLORS, COMPETITOR_COLORS, DIVERGING_RDYLGN
from src.utils.formatters import fmt_brl

PLOTLY_LAYOUT = dict(
    paper_bgcolor=COLORS["bg_secondary"],
    plot_bgcolor=COLORS["bg_secondary"],
    font=dict(family="Inter, sans-serif", color=COLORS["text_primary"], size=12),
    margin=dict(l=40, r=20, t=60, b=40),
    hoverlabel=dict(bgcolor=COLORS["bg_tertiary"], font=dict(color=COLORS["text_primary"])),
)
AXIS = dict(gridcolor="rgba(255,255,255,0.05)", linecolor="rgba(255,255,255,0.1)")

POS_COLORS = {
    "Mais barato": COLORS["success"],
    "Paridade":    COLORS["text_muted"],
    "Mais caro":   COLORS["danger"],
}


def _empty(title: str) -> go.Figure:
    return go.Figure().update_layout(title=title, height=320, **PLOTLY_LAYOUT)


def scatter_posicionamento(df_gap: pd.DataFrame) -> go.Figure:
    if df_gap.empty:
        return _empty("Sem dados competitivos")
    fig = go.Figure()
    max_v = max(df_gap["preco_atual"].max(), df_gap["preco_mediana_concorrentes"].max()) * 1.05

    # Linha de paridade
    fig.add_trace(go.Scatter(
        x=[0, max_v], y=[0, max_v],
        mode="lines", line=dict(color=COLORS["text_muted"], dash="dash", width=1),
        name="Paridade",
        hoverinfo="skip",
    ))
    for pos, sub in df_gap.groupby("posicao"):
        fig.add_trace(go.Scatter(
            x=sub["preco_mediana_concorrentes"], y=sub["preco_atual"],
            mode="markers",
            name=pos,
            marker=dict(
                size=10,
                color=POS_COLORS.get(pos, COLORS["accent"]),
                line=dict(color=COLORS["bg_primary"], width=1),
                opacity=0.85,
            ),
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>"
                "Categoria: %{customdata[1]}<br>"
                "Nosso preço: R$ %{y:,.2f}<br>"
                "Mediana concorrentes: R$ %{x:,.2f}<br>"
                "Gap: %{customdata[2]:.1%}<extra></extra>"
            ),
            customdata=sub[["nome_produto", "categoria", "gap"]].values,
        ))
    fig.update_layout(
        title=dict(text="🎯 Posicionamento de Preço — Nós × Mercado", font=dict(size=16)),
        xaxis=dict(**AXIS, title="Mediana concorrentes (R$)", tickprefix="R$ ", tickformat=",.0f"),
        yaxis=dict(**AXIS, title="Nosso preço (R$)", tickprefix="R$ ", tickformat=",.0f"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=480,
        **PLOTLY_LAYOUT,
    )
    return fig


def cards_posicionamento(resumo: dict) -> go.Figure:
    """3 indicadores horizontais com % de produtos em cada posição."""
    total = resumo["total"] or 1
    fig = go.Figure()
    valores = [resumo["mais_barato"], resumo["paridade"], resumo["mais_caro"]]
    labels = ["Mais Baratos", "Paridade", "Mais Caros"]
    cores = [COLORS["success"], COLORS["text_muted"], COLORS["danger"]]
    icones = ["🟢", "⚪", "🔴"]
    for i, (lbl, val, cor, ic) in enumerate(zip(labels, valores, cores, icones)):
        fig.add_trace(go.Bar(
            x=[val / total * 100], y=[lbl],
            orientation="h", marker_color=cor,
            text=[f"{ic} <b>{val}</b> ({val/total*100:.0f}%)"],
            textposition="inside", insidetextanchor="start",
            textfont=dict(color="white", size=14),
            hovertemplate=f"<b>{lbl}</b>: {val} produtos<extra></extra>",
            showlegend=False,
        ))
    fig.update_layout(
        title=dict(text="📊 Onde Estamos no Mercado", font=dict(size=16)),
        xaxis=dict(showgrid=False, showticklabels=False, range=[0, 100], visible=False),
        yaxis=dict(**AXIS, autorange="reversed"),
        height=260,
        bargap=0.4,
        **PLOTLY_LAYOUT,
    )
    return fig


def heatmap_gap(pivot: pd.DataFrame) -> go.Figure:
    if pivot.empty:
        return _empty("Sem dados")
    fig = go.Figure(go.Heatmap(
        z=pivot.values * 100,
        x=pivot.columns,
        y=pivot.index,
        colorscale="RdYlGn_r",
        zmid=0,
        hovertemplate="<b>%{y}</b> × <b>%{x}</b><br>Gap médio: %{z:.1f}%<extra></extra>",
        text=[[f"{v*100:+.0f}%" if not pd.isna(v) else "" for v in row] for row in pivot.values],
        texttemplate="%{text}",
        textfont=dict(size=11, color="white"),
        colorbar=dict(title="Gap %", thickness=10, tickfont=dict(color=COLORS["text_muted"]), ticksuffix="%"),
    ))
    fig.update_layout(
        title=dict(text="🌡️ Gap Médio por Categoria × Concorrente (verde = mais barato)", font=dict(size=16)),
        xaxis=dict(**AXIS, title=""),
        yaxis=dict(**AXIS, title="", autorange="reversed"),
        height=420,
        **PLOTLY_LAYOUT,
    )
    return fig


def historico_preco_chart(df: pd.DataFrame, nome_produto: str) -> go.Figure:
    if df.empty:
        return _empty("Selecione um produto com histórico")
    fig = go.Figure()
    for concorrente, sub in df.groupby("nome_concorrente"):
        cor = COMPETITOR_COLORS.get(concorrente, COLORS["accent"])
        fig.add_trace(go.Scatter(
            x=sub["data_coleta"], y=sub["preco_concorrente"],
            mode="lines+markers", name=concorrente,
            line=dict(color=cor, width=2),
            marker=dict(size=6),
            hovertemplate=f"<b>{concorrente}</b><br>%{{x|%d %b %Y}}: R$ %{{y:,.2f}}<extra></extra>",
        ))
    nosso = df.attrs.get("nosso_preco")
    if nosso:
        fig.add_hline(y=nosso, line=dict(color=COLORS["accent"], dash="dash", width=2),
                      annotation_text=f"Nosso preço: {fmt_brl(nosso)}",
                      annotation_font=dict(color=COLORS["accent"]),
                      annotation_position="top right")
    fig.update_layout(
        title=dict(text=f"📈 Histórico de Preços — {nome_produto}", font=dict(size=16)),
        xaxis=dict(**AXIS, title=""),
        yaxis=dict(**AXIS, title="Preço (R$)", tickprefix="R$ ", tickformat=",.2f"),
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=380,
        **PLOTLY_LAYOUT,
    )
    return fig
