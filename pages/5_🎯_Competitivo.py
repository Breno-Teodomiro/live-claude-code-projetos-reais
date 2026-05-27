"""Página 5 — Inteligência Competitiva."""

import streamlit as st

from src.components.theme import apply_theme
from src.components.filters import render_sidebar_filters, apply_filters
from src.components.kpi_card import kpi_card
from src.data.loaders import load_vendas, load_produtos, load_precos_competidores
from src.data.transformations import (
    gap_competitivo, resumo_posicionamento, gap_por_categoria_concorrente,
    oportunidades_reajuste, vantagens_competitivas, historico_preco,
)
from src.charts import competitive as ch
from src.utils.formatters import fmt_brl, fmt_pct, fmt_int

st.set_page_config(page_title="Inteligência Competitiva", page_icon="🎯", layout="wide")
apply_theme()

st.title("🎯 Inteligência Competitiva")
st.caption("Posicionamento de preço vs Amazon, Mercado Livre e Shopee")

# ---------- DADOS ----------
vendas = load_vendas()
produtos = load_produtos()
precos = load_precos_competidores()

filtros = render_sidebar_filters(vendas, mostrar_canal=True)
v = apply_filters(vendas, filtros)

# ---------- CÁLCULOS ----------
df_gap = gap_competitivo(produtos, precos, tol=0.02)
resumo = resumo_posicionamento(df_gap)
pivot_gap = gap_por_categoria_concorrente(produtos, precos)
df_oport = oportunidades_reajuste(df_gap, v, n=10)
df_vant = vantagens_competitivas(df_gap, v, n=10)

# ---------- KPIs ----------
st.markdown("### Indicadores Competitivos")
total = resumo["total"] or 1
pct_barato = resumo["mais_barato"] / total
pct_paridade = resumo["paridade"] / total
pct_caro = resumo["mais_caro"] / total

c1, c2, c3, c4 = st.columns(4)
with c1: kpi_card("SKUs Monitorados", resumo["total"], fmt_int)
with c2: kpi_card("🟢 Mais Baratos", resumo["mais_barato"], fmt_int, help_text=fmt_pct(pct_barato))
with c3: kpi_card("⚪ Paridade", resumo["paridade"], fmt_int, help_text=fmt_pct(pct_paridade))
with c4: kpi_card("🔴 Mais Caros", resumo["mais_caro"], fmt_int, delta_positivo_bom=False, help_text=fmt_pct(pct_caro))

c5, c6, c7, c8 = st.columns(4)
with c5: kpi_card("Gap Médio", resumo["gap_medio"], lambda x: fmt_pct(x, com_sinal=True), delta_positivo_bom=False, help_text="Negativo = somos mais baratos que mediana")
with c6: kpi_card("Concorrentes Monitorados", precos["nome_concorrente"].nunique() if not precos.empty else 0, fmt_int)
with c7: kpi_card("Coletas no Total", len(precos), fmt_int)
with c8: kpi_card("Oportunidades de Reajuste", len(df_oport), fmt_int, delta_positivo_bom=False, help_text="SKUs onde estamos >5% mais caros")

st.markdown("---")

# ---------- LINHA 1: Painel posicionamento + Scatter ----------
col1, col2 = st.columns([1, 2])
with col1:
    st.plotly_chart(ch.cards_posicionamento(resumo), use_container_width=True)
with col2:
    st.plotly_chart(ch.scatter_posicionamento(df_gap), use_container_width=True)

# ---------- LINHA 2: Heatmap gap ----------
st.plotly_chart(ch.heatmap_gap(pivot_gap), use_container_width=True)

# ---------- LINHA 3: Tabelas oportunidades + vantagens ----------
col3, col4 = st.columns(2)
with col3:
    st.markdown(f"### 🚨 Top {len(df_oport)} Oportunidades de Reajuste")
    st.caption("Estamos mais caros que o mercado — considere reduzir")
    if not df_oport.empty:
        tabela = df_oport[["nome_produto", "categoria", "preco_atual", "preco_mediana_concorrentes", "gap", "preco_sugerido", "receita_periodo"]].rename(
            columns={
                "nome_produto": "Produto", "categoria": "Categoria",
                "preco_atual": "Nosso", "preco_mediana_concorrentes": "Mediana",
                "gap": "Gap", "preco_sugerido": "Sugerido", "receita_periodo": "Receita"
            }
        )
        st.dataframe(
            tabela, use_container_width=True, hide_index=True,
            column_config={
                "Nosso": st.column_config.NumberColumn(format="R$ %.2f"),
                "Mediana": st.column_config.NumberColumn(format="R$ %.2f"),
                "Sugerido": st.column_config.NumberColumn(format="R$ %.2f"),
                "Gap": st.column_config.NumberColumn(format="%.1f%%"),
                "Receita": st.column_config.NumberColumn(format="R$ %.0f"),
            },
        )
        st.download_button("⬇️ Exportar oportunidades", df_oport.to_csv(index=False).encode("utf-8"),
                           "oportunidades_reajuste.csv", mime="text/csv")
    else:
        st.success("Nenhum produto significativamente mais caro 🎉")

with col4:
    st.markdown(f"### 🏆 Top {len(df_vant)} Vantagens Competitivas")
    st.caption("Somos mais baratos — destaque em ads e campanhas")
    if not df_vant.empty:
        tabela = df_vant[["nome_produto", "categoria", "preco_atual", "preco_mediana_concorrentes", "gap", "receita_periodo"]].rename(
            columns={
                "nome_produto": "Produto", "categoria": "Categoria",
                "preco_atual": "Nosso", "preco_mediana_concorrentes": "Mediana",
                "gap": "Gap", "receita_periodo": "Receita"
            }
        )
        st.dataframe(
            tabela, use_container_width=True, hide_index=True,
            column_config={
                "Nosso": st.column_config.NumberColumn(format="R$ %.2f"),
                "Mediana": st.column_config.NumberColumn(format="R$ %.2f"),
                "Gap": st.column_config.NumberColumn(format="%.1f%%"),
                "Receita": st.column_config.NumberColumn(format="R$ %.0f"),
            },
        )
    else:
        st.info("Sem vantagens claras no momento")

# ---------- LINHA 4: Histórico de preço (drill-down) ----------
st.markdown("---")
st.markdown("### 📈 Drill-down: Histórico de Preços")
nomes = produtos[["id_produto", "nome_produto"]].dropna().drop_duplicates()
opcoes = {f"{r['nome_produto']} ({r['id_produto']})": r["id_produto"] for _, r in nomes.iterrows()}
opt = st.selectbox("Selecione um produto", list(opcoes.keys()))
id_sel = opcoes[opt]
hist = historico_preco(precos, produtos, id_sel)
st.plotly_chart(ch.historico_preco_chart(hist, opt.split(" (")[0]), use_container_width=True)

# ---------- INSIGHTS ----------
st.markdown("---")
st.markdown("### 💡 Insights Competitivos")

if resumo["total"] > 0:
    posicao_majoritaria = "mais baratos que o mercado" if pct_barato > 0.5 else (
        "mais caros que o mercado" if pct_caro > 0.5 else "em paridade com o mercado"
    )
    receita_oport = float(df_oport["receita_periodo"].sum()) if not df_oport.empty else 0
    st.markdown(f"""
    - 📊 Em **{resumo['total']}** SKUs monitorados, estamos majoritariamente **{posicao_majoritaria}**
    - 🟢 **{fmt_pct(pct_barato)}** dos produtos estão mais baratos que a mediana — força competitiva
    - 🔴 **{fmt_pct(pct_caro)}** estão mais caros — risco de perder volume
    - 🎯 **Gap médio:** {fmt_pct(resumo['gap_medio'], com_sinal=True)} ({'somos mais baratos' if resumo['gap_medio'] < 0 else 'somos mais caros'} na média)
    - 🚨 **{len(df_oport)} oportunidades** de reajuste representam **{fmt_brl(receita_oport)}** de receita no período — priorizar revisão
    - 🏆 **{len(df_vant)} vantagens** competitivas claras — material pronto para marketing
    """)
else:
    st.info("Sem dados competitivos para o período.")
