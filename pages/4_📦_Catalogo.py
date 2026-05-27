"""Página 4 — Catálogo & Produtos."""

import streamlit as st

from src.components.theme import apply_theme
from src.components.filters import render_sidebar_filters, apply_filters
from src.components.kpi_card import kpi_card
from src.data.loaders import load_vendas, load_produtos
from src.data.transformations import (
    hierarquia_catalogo, matriz_bcg, long_tail,
    produtos_sem_venda, performance_categoria,
)
from src.charts import catalog as ch
from src.utils.formatters import fmt_brl_compact, fmt_brl, fmt_int, fmt_pct

st.set_page_config(page_title="Catálogo & Produtos", page_icon="📦", layout="wide")
apply_theme()

st.title("📦 Catálogo & Produtos")
st.caption("Curadoria de portfólio: estrelas, vacas leiteiras, abacaxis e long tail")

# ---------- DADOS ----------
vendas = load_vendas()
produtos = load_produtos()

filtros = render_sidebar_filters(vendas, mostrar_canal=True)
v = apply_filters(vendas, filtros)

# ---------- CALCULOS ----------
df_long = long_tail(v, produtos)
df_bcg = matriz_bcg(v, produtos, periodo_dias=30)
df_sem = produtos_sem_venda(v, produtos)
df_cat = performance_categoria(v, produtos)
df_hier = hierarquia_catalogo(v, produtos)

# ---------- KPIs ----------
st.markdown("### Indicadores de Catálogo")
total_skus = len(produtos)
skus_vendidos = v["id_produto"].nunique() if not v.empty else 0
n_classe_a = int((df_long["classe"] == "A").sum()) if not df_long.empty else 0
n_estrelas = int((df_bcg["quadrante"] == "⭐ Estrela").sum()) if not df_bcg.empty else 0
n_abacaxis = int((df_bcg["quadrante"] == "🐄 Vaca Leiteira").sum()) if not df_bcg.empty else 0  # placeholder
n_vacas = int((df_bcg["quadrante"] == "🐄 Vaca Leiteira").sum()) if not df_bcg.empty else 0
n_pineapples = int((df_bcg["quadrante"] == "🐕 Abacaxi").sum()) if not df_bcg.empty else 0
n_categorias = produtos["categoria"].nunique()
n_marcas = produtos["marca"].nunique()

c1, c2, c3, c4 = st.columns(4)
with c1: kpi_card("SKUs no Catálogo", total_skus, fmt_int)
with c2: kpi_card("SKUs Vendidos no Período", skus_vendidos, fmt_int, help_text=f"{fmt_pct(skus_vendidos/total_skus) if total_skus else '0%'} de cobertura")
with c3: kpi_card("Categorias", n_categorias, fmt_int)
with c4: kpi_card("Marcas", n_marcas, fmt_int)

c5, c6, c7, c8 = st.columns(4)
with c5: kpi_card("Classe A (80% receita)", n_classe_a, fmt_int, help_text="SKUs que concentram 80% da receita")
with c6: kpi_card("⭐ Estrelas BCG", n_estrelas, fmt_int)
with c7: kpi_card("🐄 Vacas Leiteiras", n_vacas, fmt_int)
with c8: kpi_card("🐕 Abacaxis", n_pineapples, fmt_int, delta_positivo_bom=False)

st.markdown("---")

# ---------- LINHA 1: Treemap hierárquico ----------
st.plotly_chart(ch.treemap_hierarquico(df_hier), use_container_width=True)

# ---------- LINHA 2: BCG + Sunburst ----------
col1, col2 = st.columns([3, 2])
with col1:
    st.plotly_chart(ch.matriz_bcg(df_bcg), use_container_width=True)
with col2:
    st.plotly_chart(ch.sunburst_catalogo(df_hier), use_container_width=True)

# ---------- LINHA 3: Long tail ----------
st.plotly_chart(ch.long_tail_chart(df_long), use_container_width=True)

# ---------- LINHA 4: Performance por categoria ----------
st.plotly_chart(ch.performance_categoria_chart(df_cat), use_container_width=True)

# ---------- TABELAS ----------
st.markdown("---")

col3, col4 = st.columns(2)
with col3:
    st.markdown(f"### 🐕 Abacaxis — Candidatos a Descontinuação ({n_pineapples})")
    if not df_bcg.empty:
        abacaxis = df_bcg[df_bcg["quadrante"] == "🐕 Abacaxi"].sort_values("receita_atual", ascending=True).head(20)
        if not abacaxis.empty:
            st.dataframe(
                abacaxis[["nome_produto", "categoria", "receita_atual", "crescimento", "participacao"]]
                .rename(columns={"receita_atual": "Receita", "crescimento": "Crescimento", "participacao": "Participação"}),
                use_container_width=True, hide_index=True,
                column_config={
                    "Receita": st.column_config.NumberColumn(format="R$ %.0f"),
                    "Crescimento": st.column_config.NumberColumn(format="%.1f%%"),
                    "Participação": st.column_config.NumberColumn(format="%.2f%%"),
                },
            )
        else:
            st.success("Nenhum abacaxi identificado 🎉")

with col4:
    st.markdown(f"### 🚫 SKUs sem Venda no Período ({len(df_sem)})")
    if not df_sem.empty:
        st.dataframe(
            df_sem[["nome_produto", "categoria", "marca", "preco_atual"]].head(20),
            use_container_width=True, hide_index=True,
            column_config={"preco_atual": st.column_config.NumberColumn(format="R$ %.2f")},
        )
        st.download_button(
            "⬇️ Exportar todos sem venda",
            df_sem.to_csv(index=False).encode("utf-8"),
            "produtos_sem_venda.csv",
            mime="text/csv",
        )
    else:
        st.success("Todos os SKUs venderam no período 🎉")

# ---------- INSIGHTS ----------
st.markdown("---")
st.markdown("### 💡 Insights de Curadoria")

if not df_long.empty and not df_bcg.empty:
    pct_concentracao = n_classe_a / len(df_long) if len(df_long) else 0
    cobertura = skus_vendidos / total_skus if total_skus else 0

    top_categoria = df_cat.iloc[0] if not df_cat.empty else None

    st.markdown(f"""
    - 📊 **Cobertura do catálogo:** {fmt_pct(cobertura)} dos SKUs venderam no período
      ({skus_vendidos} de {total_skus})
    - 🎯 **Concentração:** apenas **{n_classe_a} SKUs** ({fmt_pct(pct_concentracao)} do mix vendido)
      respondem por **80% da receita**
    - ⭐ **{n_estrelas} produtos Estrela** — alta participação e alto crescimento, **foco máximo**
    - 🐄 **{n_vacas} Vacas Leiteiras** — sustentam o caixa, **mantenha estoque garantido**
    - 🐕 **{n_pineapples} Abacaxis** — baixo crescimento e baixa participação,
      **candidatos a descontinuação ou liquidação**
    - 🏆 **Categoria líder em receita:** {top_categoria['categoria'] if top_categoria is not None else '—'}
      ({fmt_brl_compact(top_categoria['receita']) if top_categoria is not None else '—'})
    - 🚫 **{len(df_sem)} SKUs** não venderam no período — avaliar promoção, kit ou removal
    """)
else:
    st.info("Selecione um período com dados para ver os insights.")
