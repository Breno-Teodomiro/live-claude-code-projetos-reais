"""Gráficos da página Vendas & Performance."""

import pandas as pd
import plotly.graph_objects as go

from src.utils.colors import COLORS, CHANNEL_COLORS
from src.utils.formatters import fmt_brl, fmt_brl_compact

PLOTLY_LAYOUT = dict(
    paper_bgcolor=COLORS["bg_secondary"],
    plot_bgcolor=COLORS["bg_secondary"],
    font=dict(family="Inter, sans-serif", color=COLORS["text_primary"], size=12),
    margin=dict(l=40, r=20, t=60, b=40),
    hoverlabel=dict(bgcolor=COLORS["bg_tertiary"], font=dict(color=COLORS["text_primary"])),
)
AXIS = dict(gridcolor="rgba(255,255,255,0.05)", linecolor="rgba(255,255,255,0.1)", zerolinecolor="rgba(255,255,255,0.05)")


def _empty(title: str) -> go.Figure:
    fig = go.Figure()
    fig.update_layout(title=title, height=320, **PLOTLY_LAYOUT)
    return fig


def heatmap_dia_hora(df: pd.DataFrame) -> go.Figure:
    if df.empty:
        return _empty("Sem dados")
    fig = go.Figure(go.Heatmap(
        z=df.values,
        x=[f"{h:02d}h" for h in df.columns],
        y=df.index,
        colorscale=[[0, COLORS["bg_tertiary"]], [0.3, "#1E3A5F"], [0.6, "#3B82F6"], [1, "#60A5FA"]],
        hovertemplate="<b>%{y} %{x}</b><br>Receita: R$ %{z:,.0f}<extra></extra>",
        colorbar=dict(title="R$", thickness=10, tickfont=dict(color=COLORS["text_muted"])),
    ))
    fig.update_layout(
        title=dict(text="🔥 Receita por Dia da Semana × Hora", font=dict(size=16)),
        xaxis=dict(**AXIS, title=""),
        yaxis=dict(**AXIS, title="", autorange="reversed"),
        height=380,
        **PLOTLY_LAYOUT,
    )
    return fig


def pareto_produtos(df: pd.DataFrame) -> go.Figure:
    if df.empty:
        return _empty("Sem dados")
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df["nome_produto"], y=df["receita"], name="Receita",
        marker=dict(color=df["receita"], colorscale=[[0, "#1E3A5F"], [1, "#3B82F6"]]),
        hovertemplate="<b>%{x}</b><br>Receita: R$ %{y:,.0f}<extra></extra>",
        yaxis="y",
    ))
    fig.add_trace(go.Scatter(
        x=df["nome_produto"], y=df["pct_acumulado"] * 100, name="% Acumulado",
        mode="lines+markers",
        line=dict(color=COLORS["warning"], width=3),
        marker=dict(size=6, color=COLORS["warning"]),
        hovertemplate="<b>%{x}</b><br>Acumulado: %{y:.1f}%<extra></extra>",
        yaxis="y2",
    ))
    fig.add_hline(y=80, line=dict(color=COLORS["danger"], dash="dash", width=1.5), yref="y2",
                  annotation_text="80%", annotation_font=dict(color=COLORS["danger"]))
    fig.update_layout(
        title=dict(text="📊 Pareto 80/20 — Produtos por Receita", font=dict(size=16)),
        xaxis=dict(**AXIS, title="", tickangle=-45, tickfont=dict(size=10)),
        yaxis=dict(**AXIS, title="Receita (R$)", tickprefix="R$ ", tickformat=",.0f"),
        yaxis2=dict(title="% Acumulado", overlaying="y", side="right",
                    range=[0, 105], ticksuffix="%", gridcolor="rgba(0,0,0,0)"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=420,
        **PLOTLY_LAYOUT,
    )
    return fig


def evolucao_canal(df: pd.DataFrame) -> go.Figure:
    if df.empty:
        return _empty("Sem dados")
    fig = go.Figure()
    canais = sorted(df["canal_venda"].unique())
    for canal in canais:
        sub = df[df["canal_venda"] == canal]
        cor = CHANNEL_COLORS.get(canal, COLORS["accent"])
        fig.add_trace(go.Scatter(
            x=sub["periodo"], y=sub["receita"],
            mode="lines", name=canal.replace("_", " ").title(),
            stackgroup="one",
            line=dict(width=0.5, color=cor),
            fillcolor=cor,
            hovertemplate="<b>%{x|%d %b %Y}</b><br>" + canal + ": R$ %{y:,.0f}<extra></extra>",
        ))
    fig.update_layout(
        title=dict(text="🌊 Evolução de Receita por Canal", font=dict(size=16)),
        xaxis=dict(**AXIS, title=""),
        yaxis=dict(**AXIS, title="Receita (R$)", tickprefix="R$ ", tickformat=",.0f"),
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=380,
        **PLOTLY_LAYOUT,
    )
    return fig


def distribuicao_ticket(tickets: pd.Series) -> go.Figure:
    if tickets.empty:
        return _empty("Sem dados")
    fig = go.Figure()
    fig.add_trace(go.Histogram(
        x=tickets, nbinsx=40,
        marker=dict(color=COLORS["accent"], line=dict(color=COLORS["bg_primary"], width=1)),
        opacity=0.85,
        hovertemplate="Ticket: R$ %{x:,.0f}<br>Frequência: %{y}<extra></extra>",
        name="Frequência",
    ))
    mediana = tickets.median()
    media = tickets.mean()
    fig.add_vline(x=mediana, line=dict(color=COLORS["success"], dash="dash", width=2),
                  annotation_text=f"Mediana: {fmt_brl(mediana)}", annotation_font=dict(color=COLORS["success"]))
    fig.add_vline(x=media, line=dict(color=COLORS["warning"], dash="dot", width=2),
                  annotation_text=f"Média: {fmt_brl(media)}", annotation_font=dict(color=COLORS["warning"]),
                  annotation_position="bottom right")
    fig.update_layout(
        title=dict(text="📐 Distribuição de Ticket por Venda", font=dict(size=16)),
        xaxis=dict(**AXIS, title="Ticket (R$)", tickprefix="R$ ", tickformat=",.0f"),
        yaxis=dict(**AXIS, title="Frequência"),
        showlegend=False,
        bargap=0.05,
        height=380,
        **PLOTLY_LAYOUT,
    )
    return fig


def funil_vendas(df: pd.DataFrame) -> go.Figure:
    if df.empty:
        return _empty("Sem dados")
    cores = ["#3B82F6", "#06B6D4", "#10B981", "#F59E0B"]
    fig = go.Figure(go.Funnel(
        y=df["etapa"], x=df["valor"],
        textinfo="value+percent initial",
        textfont=dict(size=14, color="white"),
        marker=dict(color=cores[: len(df)], line=dict(color=COLORS["bg_primary"], width=2)),
        connector=dict(line=dict(color=COLORS["border"], width=1)),
        hovertemplate="<b>%{y}</b><br>Valor: %{x:,}<br>Conversão inicial: %{percentInitial}<extra></extra>",
    ))
    fig.update_layout(
        title=dict(text="⚡ Funil de Conversão", font=dict(size=16)),
        height=380,
        **PLOTLY_LAYOUT,
    )
    return fig


def sazonalidade_mensal(df: pd.DataFrame) -> go.Figure:
    if df.empty:
        return _empty("Sem dados")
    meses_pt = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
    fig = go.Figure(go.Heatmap(
        z=df.values,
        x=[meses_pt[m - 1] for m in df.columns],
        y=[str(a) for a in df.index],
        colorscale=[[0, COLORS["bg_tertiary"]], [0.5, "#3B82F6"], [1, "#10B981"]],
        hovertemplate="<b>%{x}/%{y}</b><br>Receita: R$ %{z:,.0f}<extra></extra>",
        colorbar=dict(title="R$", thickness=10, tickfont=dict(color=COLORS["text_muted"])),
        text=[[fmt_brl_compact(v) if v > 0 else "" for v in row] for row in df.values],
        texttemplate="%{text}", textfont=dict(size=10, color=COLORS["text_primary"]),
    ))
    fig.update_layout(
        title=dict(text="📅 Sazonalidade Mensal (heatmap calendário)", font=dict(size=16)),
        xaxis=dict(**AXIS, title=""),
        yaxis=dict(**AXIS, title="", autorange="reversed"),
        height=320,
        **PLOTLY_LAYOUT,
    )
    return fig


def evolucao_diaria_mm(df: pd.DataFrame) -> go.Figure:
    """Receita diária + média móvel 7d."""
    if df.empty:
        return _empty("Sem dados")
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["periodo"], y=df["receita"], mode="lines", name="Diário",
        line=dict(color=COLORS["text_muted"], width=1),
        fill="tozeroy", fillcolor="rgba(59,130,246,0.08)",
        hovertemplate="<b>%{x|%d %b %Y}</b><br>Receita: R$ %{y:,.0f}<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=df["periodo"], y=df["media_movel"], mode="lines", name="Média móvel 7d",
        line=dict(color=COLORS["accent"], width=3),
        hovertemplate="MM7d: R$ %{y:,.0f}<extra></extra>",
    ))
    fig.update_layout(
        title=dict(text="📈 Evolução Diária com Média Móvel 7d", font=dict(size=16)),
        xaxis=dict(**AXIS, title=""),
        yaxis=dict(**AXIS, title="Receita (R$)", tickprefix="R$ ", tickformat=",.0f"),
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=380,
        **PLOTLY_LAYOUT,
    )
    return fig
