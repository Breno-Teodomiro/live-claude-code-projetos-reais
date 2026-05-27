---
name: premium-dashboard-patterns
description: Padrões visuais e de interação para o Dashboard Executivo de Vendas (Streamlit + Plotly). Use SEMPRE que criar/modificar gráfico, página, componente de UI, KPI card, ou layout. Garante consistência premium (Stripe/Linear/Vercel) em paleta, tipografia, microinterações, hover, animações, formatação BR.
---

# Premium Dashboard Patterns

Skill local que codifica o padrão visual e de interação do projeto. Aplique TODOS os pontos abaixo em qualquer artefato visual.

## 1. Paleta — sempre usar `src/utils/colors.py`

| Token | Hex | Uso |
|-------|-----|-----|
| `bg_primary` | `#0B0F19` | Fundo principal |
| `bg_secondary` | `#111827` | Cards e plot bg |
| `bg_tertiary` | `#1F2937` | Hover, tooltip bg |
| `text_primary` | `#F9FAFB` | Texto principal |
| `text_muted` | `#9CA3AF` | Labels, eixos |
| `accent` | `#3B82F6` | Série principal |
| `success` | `#10B981` | Verde (positivo) |
| `warning` | `#F59E0B` | Amarelo (atenção) |
| `danger` | `#EF4444` | Vermelho (negativo) |
| `info` | `#06B6D4` | Ciano (info neutra) |

**Cores semânticas obrigatórias:**
- Delta positivo (quando bom) → `success`
- Delta negativo (quando bom) → `danger`
- Cenário neutro → `text_muted` ou `info`
- Canal `loja_fisica` → `#1F4E79` · `ecommerce` → `#06B6D4`
- Concorrentes: Amazon `#FF9900` · ML `#FFE600` · Shopee `#EE4D2D`

**Escalas:**
- Sequencial azul → `SEQUENTIAL_BLUE`
- Diverging (gap, performance) → `DIVERGING_RDYLGN` centrado em 0

## 2. Layout Padrão Plotly

Use SEMPRE o dicionário `PLOTLY_LAYOUT` (já em `src/charts/executive.py`). Replicar em novos chart modules:

```python
PLOTLY_LAYOUT = dict(
    paper_bgcolor="#111827",
    plot_bgcolor="#111827",
    font=dict(family="Inter, sans-serif", color="#F9FAFB", size=12),
    margin=dict(l=40, r=20, t=50, b=40),
    xaxis=dict(gridcolor="rgba(255,255,255,0.05)", linecolor="rgba(255,255,255,0.1)"),
    yaxis=dict(gridcolor="rgba(255,255,255,0.05)", linecolor="rgba(255,255,255,0.1)"),
    hoverlabel=dict(bgcolor="#1F2937", font=dict(color="#F9FAFB")),
)
```

**Regras invioláveis:**
- ❌ Nunca usar `template='plotly'` (light) ou `plotly_dark` puro
- ❌ Nunca usar 3D pizza/donut
- ✅ Sempre `hovermode='x unified'` em séries temporais
- ✅ Sempre ocultar legenda redundante (se eixo já rotula)
- ✅ Sempre `font-family: Inter` em todos os charts
- ✅ Grid sutil `rgba(255,255,255,0.05)` — quase invisível
- ✅ Border zero em barras (sem `marker_line`)

## 3. Tipografia

- **Fonte UI:** `Inter` (400/500/600/700/800)
- **Fonte números (KPI, eixos):** `JetBrains Mono` (apenas valores)
- **Hierarquia:**
  - H1 = 2rem (32px), peso 700, letter-spacing -0.02em
  - H2 = 1.5rem (24px), peso 700
  - H3 = 1.125rem (18px), peso 600
  - body = 14px
  - labels/captions = 12px, peso 500, `text-transform: uppercase`, `letter-spacing: 0.05em`, cor `text_muted`

## 4. KPI Card

**Sempre via** `src/components/kpi_card.py`. Estrutura:

```
┌─────────────────────────────┐
│ LABEL UPPERCASE (12px)      │  ← text_muted
│ R$ 1.247.890 (JetBrains)    │  ← text_primary, 28px, bold
│ ▲ 12,4% vs período anterior │  ← success ou danger
└─────────────────────────────┘
```

- Background `bg_secondary` · border `1px solid #1F2937` · radius 12px · padding 1.25rem 1.5rem
- Hover: `transform: translateY(-2px); border-color: accent`
- Transição: `.15s ease`
- Sombra sutil: `0 1px 3px rgba(0,0,0,0.12)`

**delta_positivo_bom:**
- `True` para receita, vendas, clientes, ticket
- `False` para churn, gap negativo, custo

## 5. Microinterações e Hover

| Interação | Implementação |
|-----------|---------------|
| Hover refinado | `hovertemplate` customizado com `<b>`, valores formatados em pt-BR |
| Hover unificado | `hovermode="x unified"` em todas séries temporais |
| Cross-highlight | Hover em série → outras com `opacity=0.3` |
| Cross-filter | Click em barra/treemap → filtra outros gráficos via `st.session_state` |
| Drill-down | Click em treemap/sunburst expande nível |
| Animação | `transition_duration=500` em mudança de filtro |
| Zoom/pan | `config={'displaylogo': False, 'modeBarButtonsToRemove': ['lasso2d']}` |

## 6. Formatação Brasileira — SEMPRE

Use `src/utils/formatters.py`:

| Função | Saída |
|--------|-------|
| `fmt_brl(1234567.89)` | `R$ 1.234.567,89` |
| `fmt_brl_compact(1234567)` | `R$ 1,2M` |
| `fmt_int(1234)` | `1.234` |
| `fmt_pct(0.124)` | `12,4%` |
| `fmt_delta_arrow(0.124)` | `▲ 12,4%` |
| `fmt_date_br(date)` | `26 de mai. de 2026` |

❌ Nunca `$1,234.56` (formato US) · ❌ Nunca `1234.56` puro

## 7. Estrutura de Página Padrão

```python
import streamlit as st
from src.components.theme import apply_theme

st.set_page_config(page_title="...", page_icon="...", layout="wide")
apply_theme()  # CSS injection — OBRIGATÓRIO

st.title("📊 ...")           # H1 com emoji
st.caption("...")             # Subtítulo descritivo

# --- DADOS ---
# --- FILTROS (sidebar) ---
# --- KPIs (linha de cards) ---
st.markdown("---")            # Divisor entre seções
# --- GRÁFICOS (grid de colunas) ---
# --- RESUMO/INSIGHTS ---
```

## 8. Hierarquia de Importância Visual

1. **KPIs no topo** — informação mais densa, decisão imediata
2. **Gráfico principal grande** (2/3 da largura)
3. **Gráficos de apoio** (1/3 ou 1/2)
4. **Tabela/detalhes** ao final
5. **Resumo em linguagem natural** — interpretação para executivo

## 9. Acessibilidade Mínima

- Contraste mínimo 4.5:1 (paleta atual passa em texto sobre `bg_secondary`)
- Não depender APENAS de cor (sempre incluir ícone/seta para delta: `▲ ▼`)
- Tooltip com texto completo para abreviações (R$ 1,2M → "R$ 1.234.567")
- Tamanhos de fonte ≥ 12px

## 10. Performance Visual

- Carregamento inicial < 3s (cache morno)
- Gráficos > 1000 pontos: usar `Scattergl` (WebGL) em vez de `Scatter`
- Treemap/Sunburst: máximo 200 nós no nível visível
- Mapa coroplético: GeoJSON simplificado se > 5MB

## 11. Checklist antes de marcar gráfico como pronto

- [ ] Aplicou `PLOTLY_LAYOUT` ou equivalente dark?
- [ ] Hovertemplate em pt-BR com valores formatados?
- [ ] Cores semânticas (verde/vermelho/neutro conforme contexto)?
- [ ] Margens generosas (≥ 40px)?
- [ ] Título com emoji 📊/💰/🎯 e tamanho 16px+?
- [ ] Sem legenda redundante?
- [ ] Hover unificado (se série temporal)?
- [ ] Funciona com DataFrame vazio (retorna figura placeholder)?

## 12. Anti-padrões — NUNCA fazer

- 🚫 Cores aleatórias sem semântica
- 🚫 Pie/donut 3D
- 🚫 Mais de 7 cores em legenda
- 🚫 Eixos sem unidade ("100" sem saber se é R$, %, qtd)
- 🚫 Datas em formato ISO na UI (sempre fmt_date_br)
- 🚫 Lógica de cálculo dentro de função de gráfico (separar em transformations.py)
- 🚫 Largura fixa em pixels (usar `use_container_width=True`)
- 🚫 Emojis decorativos sem propósito (usar só para hierarquia/categoria)

## Quando esta skill é acionada

Use ESTA skill SEMPRE que:
- Criar novo gráfico (em `src/charts/*.py`)
- Adicionar nova página (em `pages/`)
- Criar novo componente (em `src/components/`)
- Revisar/refatorar layout existente
- Validar consistência visual entre sprints
