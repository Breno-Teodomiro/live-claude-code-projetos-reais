"""Gráficos da página Catálogo & Produtos."""

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

from src.utils.colors import COLORS
from src.utils.formatters import fmt_brl_compact

PLOTLY_LAYOUT = dict(
    paper_bgcolor=COLORS["bg_secondary"],
    plot_bgcolor=COLORS["bg_secondary"],
    font=dict(family="Inter, sans-serif", color=COLORS["text_primary"], size=12),
    margin=dict(l=40, r=20, t=60, b=40),
    hoverlabel=dict(bgcolor=COLORS["bg_tertiary"], font=dict(color=COLORS["text_primary"])),
)
AXIS = dict(gridcolor="rgba(255,255,255,0.05)", linecolor="rgba(255,255,255,0.1)")

BCG_COLORS = {
    "⭐ Estrela": COLORS["success"],
    "🐄 Vaca Leiteira": COLORS["accent"],
    "❓ Interrogação": COLORS["warning"],
    "🐕 Abacaxi": COLORS["danger"],
}


def _empty(title: str) -> go.Figure:
    return go.Figure().update_layout(title=title, height=320, **PLOTLY_LAYOUT)


def treemap_hierarquico(df: pd.DataFrame) -> go.Figure:
    if df.empty:
        return _empty("Sem dados de catálogo")
    fig = px.treemap(
        df, path=["categoria", "marca", "nome_produto"], values="receita",
        color="receita", color_continuous_scale=[[0, "#1E3A5F"], [1, "#10B981"]],
        custom_data=["quantidade"],
    )
    fig.update_traces(
        hovertemplate="<b>%{label}</b><br>Receita: R$ %{value:,.0f}<br>Qtd: %{customdata[0]}<extra></extra>",
        marker=dict(line=dict(color=COLORS["bg_primary"], width=2)),
    )
    fig.update_layout(
        title=dict(text="🌳 Treemap Hierárquico — Categoria → Marca → Produto", font=dict(size=16)),
        height=520,
        paper_bgcolor=COLORS["bg_secondary"],
        font=dict(family="Inter, sans-serif", color=COLORS["text_primary"]),
        margin=dict(l=10, r=10, t=60, b=10),
        coloraxis_showscale=False,
    )
    return fig


def sunburst_catalogo(df: pd.DataFrame) -> go.Figure:
    if df.empty:
        return _empty("Sem dados")
    fig = px.sunburst(
        df, path=["categoria", "marca"], values="receita",
        color="receita", color_continuous_scale=[[0, "#1E3A5F"], [1, "#3B82F6"]],
    )
    fig.update_traces(
        hovertemplate="<b>%{label}</b><br>Receita: R$ %{value:,.0f}<extra></extra>",
        marker=dict(line=dict(color=COLORS["bg_primary"], width=2)),
    )
    fig.update_layout(
        title=dict(text="☀️ Sunburst — Categoria & Marca", font=dict(size=16)),
        height=460,
        paper_bgcolor=COLORS["bg_secondary"],
        font=dict(family="Inter, sans-serif", color=COLORS["text_primary"]),
        margin=dict(l=10, r=10, t=60, b=10),
        coloraxis_showscale=False,
    )
    return fig


def matriz_bcg(df: pd.DataFrame) -> go.Figure:
    if df.empty:
        return _empty("Sem dados BCG")
    df = df[df["receita_atual"] > 0].copy()
    fig = go.Figure()

    med_part = df["participacao"].median()
    max_part = df["participacao"].max()
    max_cresc = max(df["crescimento"].max(), 1)
    min_cresc = min(df["crescimento"].min(), -1)

    for q, sub in df.groupby("quadrante"):
        fig.add_trace(go.Scatter(
            x=sub["participacao"], y=sub["crescimento"],
            mode="markers",
            name=q,
            marker=dict(
                size=sub["receita_atual"].pow(0.5) / max(df["receita_atual"].pow(0.5).max() / 50, 1),
                sizemin=8,
                color=BCG_COLORS.get(q, COLORS["accent"]),
                line=dict(color=COLORS["bg_primary"], width=1),
                opacity=0.85,
            ),
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>"
                "Categoria: %{customdata[1]}<br>"
                "Participação: %{x:.2%}<br>"
                "Crescimento: %{y:.1%}<br>"
                "Receita atual: R$ %{customdata[2]:,.0f}<extra></extra>"
            ),
            customdata=sub[["nome_produto", "categoria", "receita_atual"]].values,
        ))

    fig.add_vline(x=med_part, line=dict(color=COLORS["text_muted"], dash="dash", width=1))
    fig.add_hline(y=0, line=dict(color=COLORS["text_muted"], dash="dash", width=1))

    # Anotações dos quadrantes
    anots = [
        ("⭐ Estrelas", max_part * 0.85, max_cresc * 0.85, COLORS["success"]),
        ("🐄 Vacas Leiteiras", max_part * 0.85, min_cresc * 0.85, COLORS["accent"]),
        ("❓ Interrogações", med_part * 0.3, max_cresc * 0.85, COLORS["warning"]),
        ("🐕 Abacaxis", med_part * 0.3, min_cresc * 0.85, COLORS["danger"]),
    ]
    for txt, x, y, cor in anots:
        fig.add_annotation(x=x, y=y, text=f"<b>{txt}</b>", showarrow=False,
                           font=dict(size=13, color=cor), opacity=0.6)

    fig.update_layout(
        title=dict(text="📐 Matriz BCG — Crescimento × Participação", font=dict(size=16)),
        xaxis=dict(**AXIS, title="Participação no mix", tickformat=".1%"),
        yaxis=dict(**AXIS, title="Crescimento vs período anterior", tickformat=".0%"),
        height=520,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        **PLOTLY_LAYOUT,
    )
    return fig


def long_tail_chart(df: pd.DataFrame) -> go.Figure:
    if df.empty:
        return _empty("Sem dados")
    cores_classe = {"A": COLORS["success"], "B": COLORS["warning"], "C": COLORS["danger"]}
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df["posicao"], y=df["receita"],
        marker=dict(color=[cores_classe[c] for c in df["classe"]]),
        hovertemplate="<b>%{customdata[0]}</b><br>Posição: %{x}<br>Receita: R$ %{y:,.0f}<br>Classe: %{customdata[1]}<extra></extra>",
        customdata=df[["nome_produto", "classe"]].values,
        name="Receita",
    ))
    fig.add_trace(go.Scatter(
        x=df["posicao"], y=df["pct_acumulado"] * 100,
        mode="lines", name="% acumulado",
        line=dict(color=COLORS["info"], width=2),
        yaxis="y2",
        hovertemplate="Acumulado: %{y:.1f}%<extra></extra>",
    ))
    n_classe_a = (df["classe"] == "A").sum()
    fig.add_vline(x=n_classe_a + 0.5, line=dict(color=COLORS["text_muted"], dash="dot", width=1),
                  annotation_text=f"{n_classe_a} SKUs classe A", annotation_font=dict(color=COLORS["success"]))

    fig.update_layout(
        title=dict(text="📉 Long Tail do Catálogo (cor = classe ABC)", font=dict(size=16)),
        xaxis=dict(**AXIS, title="Posição (ordenado por receita)"),
        yaxis=dict(**AXIS, title="Receita (R$)", tickprefix="R$ ", tickformat=",.0f"),
        yaxis2=dict(title="% acumulado", overlaying="y", side="right", range=[0, 105], ticksuffix="%", gridcolor="rgba(0,0,0,0)"),
        showlegend=False,
        height=420,
        **PLOTLY_LAYOUT,
    )
    return fig


def performance_categoria_chart(df: pd.DataFrame) -> go.Figure:
    if df.empty:
        return _empty("Sem dados")
    df = df.sort_values("receita", ascending=True)
    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=df["categoria"], x=df["receita"],
        orientation="h", name="Receita",
        marker=dict(color=df["receita"], colorscale=[[0, "#1E3A5F"], [1, "#3B82F6"]]),
        text=[fmt_brl_compact(v) for v in df["receita"]],
        textposition="outside",
        textfont=dict(color=COLORS["text_primary"], size=11),
        hovertemplate=(
            "<b>%{y}</b><br>"
            "Receita: R$ %{x:,.0f}<br>"
            "Qtd: %{customdata[0]}<br>"
            "Vendas: %{customdata[1]}<br>"
            "Ticket médio: R$ %{customdata[2]:,.0f}<extra></extra>"
        ),
        customdata=df[["quantidade", "n_vendas", "ticket_medio"]].values,
    ))
    fig.update_layout(
        title=dict(text="📦 Performance por Categoria", font=dict(size=16)),
        xaxis=dict(**AXIS, title="Receita (R$)", tickprefix="R$ ", tickformat=",.0f"),
        yaxis=dict(**AXIS, title=""),
        showlegend=False,
        height=400,
        **PLOTLY_LAYOUT,
    )
    return fig
