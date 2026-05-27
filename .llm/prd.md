# PRD — Dashboard Executivo de Vendas & Inteligência Competitiva

> **Produto:** Plataforma analítica para o e-commerce / varejo, com visão consolidada de vendas, clientes, catálogo e posicionamento competitivo.
> **Audiência:** CEO, Diretores Comerciais, Gerentes de Marketing, Gestores de Produto, Analistas de BI.
> **Stack:** Python · Streamlit · Plotly · Pandas · Supabase (PostgreSQL).

---

## 1. Visão Geral

Construir um **dashboard executivo de classe premium**, com identidade visual sóbria e foco em decisão, que conecta-se ao banco Supabase (schema `JORNADA_DADOS_CLAUDE_CODE_PROJ_REAIS`) e entrega:

1. **Visão 360º das vendas** — receita, volume, ticket médio, mix de canais e produtos.
2. **Inteligência de clientes** — segmentação geográfica, recência, frequência, ticket médio.
3. **Inteligência competitiva** — comparação de preços com Amazon, Mercado Livre, Shopee.
4. **Gestão de catálogo** — performance por categoria, marca e produto.
5. **Tabela transacional auditável** — drill-down completo dos dados.

O produto deve transmitir **confiança, sofisticação e clareza** — padrão "Stripe / Linear / Notion / Vercel".

---

## 2. Fontes de Dados (Supabase)

Schema: `JORNADA_DADOS_CLAUDE_CODE_PROJ_REAIS`

| Tabela | Volume | Uso |
|--------|--------|-----|
| `vendas` | 3.020 | Fato central — transações |
| `clientes` | 50 | Dimensão cliente |
| `produtos` | 215 | Dimensão produto |
| `precos_competidores` | 728 | Inteligência competitiva |
| `produtos_sujo` | 39 | Staging (não usar no dashboard) |

**Relacionamentos lógicos:**
- `vendas.id_cliente → clientes.id_cliente`
- `vendas.id_produto → produtos.id_produto`
- `precos_competidores.id_produto → produtos.id_produto`

---

## 3. Arquitetura de Páginas

O dashboard terá **5 páginas** organizadas em sidebar com ícones (`streamlit-option-menu` ou `st.navigation`):

| # | Página | Ícone | Audiência primária |
|---|--------|-------|--------------------|
| 1 | **Visão Executiva** | 📊 | CEO / Diretoria |
| 2 | **Vendas & Performance** | 💰 | Comercial |
| 3 | **Clientes & Geografia** | 👥 | Marketing |
| 4 | **Catálogo & Produtos** | 📦 | Produto / Compras |
| 5 | **Inteligência Competitiva** | 🎯 | Pricing |
| 6 | **Dados Brutos** | 🗂️ | Analistas |

---

## 4. KPIs Principais (Cards Superiores em Todas as Páginas)

Cada KPI deve seguir o padrão **"big number + delta + sparkline"**:

```
┌─────────────────────────────┐
│  RECEITA TOTAL              │
│  R$ 1.247.890               │
│  ▲ 12,4% vs período anterior│
│  ▁▂▃▅▆▇▆▅▃▂▁  (sparkline)   │
└─────────────────────────────┘
```

### 4.1 KPIs Executivos

| KPI | Cálculo | Cor por Cenário |
|-----|---------|-----------------|
| **Receita Total** | `Σ (quantidade × preco_unitario)` | Verde se ▲, Vermelho se ▼ |
| **Ticket Médio** | Receita / nº vendas | Verde / Vermelho |
| **Volume de Vendas** | `COUNT(id_venda)` | Verde / Vermelho |
| **Itens Vendidos** | `Σ quantidade` | Verde / Vermelho |
| **Clientes Ativos** | `COUNT(DISTINCT id_cliente)` no período | Verde / Vermelho |
| **Receita por Cliente** | Receita / Clientes Ativos | Verde / Vermelho |
| **Mix Ecommerce %** | Receita ecommerce / Receita total | Neutro (azul) |
| **Gap Competitivo Médio** | `(preço_atual − média_concorrentes) / média_concorrentes` | Verde se mais barato, Vermelho se mais caro |

---

## 5. Página 1 — Visão Executiva

**Objetivo:** Em ≤10 segundos, executivo entende a saúde do negócio.

### Layout

```
┌──────────────────────────────────────────────────────────────────┐
│  [filtros: período, canal, estado, categoria]    [exportar PDF]  │
├──────────────────────────────────────────────────────────────────┤
│  [KPI 1]    [KPI 2]    [KPI 3]    [KPI 4]    [KPI 5]    [KPI 6] │
├──────────────────────────────────────────────────────────────────┤
│  📈 Receita Mensal (linha + área)    │  🎯 Meta vs Realizado    │
│  Comparativo Year-over-Year          │  (gauge)                  │
├──────────────────────────────────────────────────────────────────┤
│  🥇 Top 10 Produtos (barras horiz.)  │  🗺️ Mapa do Brasil       │
│                                       │  (receita por estado)    │
├──────────────────────────────────────────────────────────────────┤
│  📊 Mix de Canal (donut animado)     │  ⚡ Pulse: últimas 24h   │
└──────────────────────────────────────────────────────────────────┘
```

### Gráficos Específicos

1. **Receita Mensal YoY** — `plotly.graph_objects.Scatter` com `fill='tozeroy'`, duas séries (ano atual / anterior), hover unificado.
2. **Gauge de Meta** — `go.Indicator(mode="gauge+number+delta")` com steps coloridos (vermelho < 70%, amarelo 70-95%, verde ≥ 95%).
3. **Top 10 Produtos** — barras horizontais com `text_auto='.2s'`, ordenadas, com gradiente de cor por valor.
4. **Mapa Coroplético do Brasil** — `px.choropleth` com GeoJSON dos estados; escala de cores `Blues` ou `Viridis`; hover com receita, nº vendas, ticket médio.
5. **Donut de Canal** — `px.pie(hole=0.6)` com cores `loja_fisica` (#1f4e79) e `ecommerce` (#06b6d4).

---

## 6. Página 2 — Vendas & Performance

**Objetivo:** Diagnóstico granular da operação comercial.

### Análises e Gráficos

| # | Análise | Tipo de Gráfico | Insight Esperado |
|---|---------|-----------------|------------------|
| 1 | **Evolução Diária com Média Móvel 7d** | Linha + área | Identificar tendência e sazonalidade |
| 2 | **Heatmap Dia da Semana × Hora** | `px.imshow` | Picos de vendas para staffing/campanhas |
| 3 | **Receita por Canal ao Longo do Tempo** | Área empilhada | Migração ecommerce vs loja física |
| 4 | **Distribuição de Ticket** | Histograma + boxplot lateral | Identificar outliers e segmentos |
| 5 | **Funil: Cliente → Venda → Item** | `go.Funnel` | Conversão por etapa |
| 6 | **Pareto 80/20 (produtos)** | Barras + linha cumulativa | Quais produtos representam 80% da receita |
| 7 | **Sazonalidade Mensal** | Heatmap calendário | Padrões cíclicos |

### Filtros (sidebar)

- Período (date range com presets: 7d / 30d / 90d / YTD / Custom)
- Canal de venda (multiselect)
- Categoria (multiselect)
- Marca (multiselect)
- Estado (multiselect)

---

## 7. Página 3 — Clientes & Geografia

**Objetivo:** Entender base de clientes, distribuição e oportunidades regionais.

### Análises

1. **Matriz RFM** (Recência × Frequência × Valor Monetário)
   - Scatter 3D ou heatmap 2D + bubble size
   - Segmentos: Campeões, Leais, Em Risco, Hibernando, Perdidos
   - Tabela com contagem e % por segmento

2. **Mapa do Brasil — Densidade de Clientes**
   - Coroplético + bolhas proporcionais
   - Tooltip: nº clientes, receita, ticket médio, % crescimento

3. **Cohort de Retenção**
   - Heatmap `mês de cadastro × mês de atividade`
   - % de clientes ativos em cada cohort

4. **Top 20 Clientes (Curva ABC)**
   - Barras com rótulo de receita acumulada %
   - Marcação visual das classes A (80%), B (15%), C (5%)

5. **Distribuição Geográfica**
   - Tabela treemap por estado/país
   - `px.treemap` com hierarquia `pais → estado`

6. **Aquisição vs Retenção**
   - Stacked bar: novos clientes / clientes recorrentes por mês

---

## 8. Página 4 — Catálogo & Produtos

**Objetivo:** Curadoria de portfólio — o que vender mais, o que descontinuar.

### Análises

1. **Treemap Hierárquico** `Categoria → Marca → Produto`
   - Tamanho = receita; cor = ticket médio ou crescimento
   - `px.treemap` com `color_continuous_scale='RdYlGn'`

2. **Matriz BCG-like** (Crescimento × Participação)
   - Scatter quadrants
   - Eixos: crescimento de receita (vs período anterior) × participação no total
   - Quadrantes rotulados: ⭐ Estrelas / 🐄 Vacas Leiteiras / ❓ Pontos de Interrogação / 🐕 Abacaxis

3. **Sunburst Categoria → Marca**
   - Drill-down interativo

4. **Performance por Categoria**
   - Barras múltiplas: receita, qtd vendida, ticket médio, gap competitivo

5. **Long Tail Analysis**
   - Curva ordenada decrescente de produtos por receita
   - Marcadores das classes A/B/C

6. **Produtos Sem Venda no Período** (alerta)
   - Tabela com produtos do catálogo que não venderam → candidatos a descontinuação ou ação de marketing

---

## 9. Página 5 — Inteligência Competitiva

**Objetivo:** Posicionamento de preço vs Amazon, Mercado Livre, Shopee.

### Análises

1. **Painel "Onde Estamos no Mercado"**
   - 3 cards: % produtos mais baratos / em paridade (±2%) / mais caros
   - Cores: verde / cinza / vermelho

2. **Gráfico de Posicionamento** (scatter)
   - Eixo X: preço médio dos concorrentes
   - Eixo Y: nosso preço
   - Linha de paridade (45°)
   - Cor = categoria; tamanho = receita do produto
   - Pontos acima da linha = mais caros que mercado

3. **Comparativo por Concorrente** (radar / barras agrupadas)
   - Para cada concorrente: gap médio %, nº produtos monitorados, frequência de coleta

4. **Heatmap de Gap por Categoria × Concorrente**
   - Diverging colorscale (verde-branco-vermelho)
   - Centro = 0% (paridade)

5. **Top 10 Oportunidades de Reajuste**
   - Tabela rankeada de produtos com maior gap negativo (estamos muito mais caros) e sua receita
   - Recomendação automática: "Reduzir em X% para alinhar à mediana"

6. **Histórico de Preços por Produto** (drill-down)
   - Seletor de produto → linha temporal do nosso preço vs cada concorrente

---

## 10. Página 6 — Dados Brutos

**Objetivo:** Auditoria e exportação livre.

- Selector de tabela (`vendas` / `clientes` / `produtos` / `precos_competidores`)
- Filtros dinâmicos por coluna (use `st-aggrid` ou `streamlit-extras.dataframe_explorer`)
- Busca textual global
- Botão **"Exportar CSV"** e **"Exportar Excel"**
- Paginação server-side se >10k linhas

---

## 11. Identidade Visual — Padrão Premium

### Paleta de Cores

```python
COLORS = {
    "bg_primary":   "#0B0F19",   # fundo escuro principal
    "bg_secondary": "#111827",   # cards
    "bg_tertiary":  "#1F2937",   # hover
    "text_primary": "#F9FAFB",   # texto principal
    "text_muted":   "#9CA3AF",   # texto secundário
    "accent":       "#3B82F6",   # azul Stripe-like
    "success":      "#10B981",   # verde
    "warning":      "#F59E0B",   # amarelo
    "danger":       "#EF4444",   # vermelho
    "info":         "#06B6D4",   # ciano
}
```

> **Modo claro alternativo** disponível via toggle no topo da sidebar.

### Tipografia

- **Fonte principal:** `Inter` (Google Fonts, peso 400/500/600/700)
- **Fonte monospace** para números: `JetBrains Mono`
- **Hierarquia:** títulos h1=32px / h2=24px / h3=18px / corpo=14px / labels=12px

### Componentes

- **Cards de KPI:** background `bg_secondary`, border-radius 12px, padding 24px, sombra sutil `0 1px 3px rgba(0,0,0,0.12)`.
- **Gráficos:** `template='plotly_dark'` (ou custom), grid sutil `rgba(255,255,255,0.05)`, sem bordas, hover com fundo escuro translúcido.
- **Tabelas:** `st-aggrid` com tema `balham-dark`, zebra striping, headers stickies.
- **Botões:** estilo flat com hover.
- **Spinners:** `st.spinner` customizado durante carregamento.

### Regras Estéticas Obrigatórias

| Regra | Aplicação |
|-------|-----------|
| Formatação numérica BR | `R$ 1.234.567,89` (não US format) |
| Datas em pt-BR | `26 de mai. de 2026` |
| Variações % com sinal | `▲ 12,4%` / `▼ 5,3%` em verde/vermelho |
| Sem 3D pizza/donut | Apenas 2D |
| Espaçamento generoso | Margens `padding: 1.5rem` mínimas |
| Hover unificado | `hovermode='x unified'` em séries temporais |
| Sem legenda redundante | Se um eixo já rotula, ocultar legenda |

---

## 12. Arquitetura Técnica

### Estrutura de Pastas

```
.
├── app.py                          # entrypoint Streamlit
├── pages/
│   ├── 1_📊_Visao_Executiva.py
│   ├── 2_💰_Vendas.py
│   ├── 3_👥_Clientes.py
│   ├── 4_📦_Catalogo.py
│   ├── 5_🎯_Competitivo.py
│   └── 6_🗂️_Dados_Brutos.py
├── src/
│   ├── data/
│   │   ├── connection.py           # cliente Supabase
│   │   ├── queries.py              # SQL parametrizado
│   │   └── transformations.py      # cálculos (RFM, cohort, etc)
│   ├── components/
│   │   ├── kpi_card.py
│   │   ├── filters.py
│   │   └── theme.py
│   ├── charts/
│   │   ├── executive.py
│   │   ├── sales.py
│   │   ├── customers.py
│   │   ├── catalog.py
│   │   └── competitive.py
│   └── utils/
│       ├── formatters.py           # R$, %, datas
│       └── colors.py
├── assets/
│   ├── logo.svg
│   └── style.css
├── .streamlit/
│   └── config.toml                 # tema customizado
├── .env.example                    # SUPABASE_URL, SUPABASE_KEY
├── requirements.txt
└── README.md
```

### Dependências Mínimas

```txt
streamlit>=1.36
plotly>=5.22
pandas>=2.2
supabase>=2.5
python-dotenv>=1.0
streamlit-option-menu>=0.3.13
streamlit-aggrid>=0.3.5
streamlit-extras>=0.4.7
numpy>=1.26
```

### Performance & Cache

- Toda função de query deve usar `@st.cache_data(ttl=300)` (5 min).
- Conexão Supabase singleton via `@st.cache_resource`.
- Pré-agregações pesadas em SQL (não em Python), aproveitando o Postgres.

### Segurança

- Credenciais via `.env` (nunca hardcoded).
- Cliente usa `anon key` apenas — após implementar policies de RLS adequadas.
- Validação de input dos filtros antes de injetar em queries.

---

## 13. Interatividade — Padrão Plotly Profissional

| Recurso | Implementação |
|---------|---------------|
| Hover refinado | `hovertemplate` customizado com `<b>`, valores formatados |
| Cross-filtering | Selecionar barra → filtra outros gráficos via `st.session_state` |
| Zoom & pan | `config={'displaylogo': False, 'modeBarButtonsToRemove': ['lasso2d']}` |
| Animação de transição | `transition_duration=500` em mudanças de filtro |
| Tooltip rich | Multilinhas com KPIs adicionais |
| Drill-down | Click em treemap/sunburst expande nível |
| Highlights | Hover em série deixa outras com `opacity=0.3` |

---

## 14. Critérios de Aceite

- [ ] Conecta ao Supabase com credenciais em `.env`
- [ ] 6 páginas implementadas e navegáveis
- [ ] Todos os KPIs calculados corretamente (validar amostras)
- [ ] Filtros globais persistem entre páginas via `st.session_state`
- [ ] Carregamento inicial < 3s com cache morno
- [ ] Layout responsivo (desktop full HD e tablets)
- [ ] Exportação CSV/Excel funcional na página de dados
- [ ] Modo escuro padrão e toggle para claro
- [ ] Formatação BR em todos os números, percentuais e datas
- [ ] Zero erros no console / `st.error`
- [ ] README com instruções de setup (`pip install`, `.env`, `streamlit run`)

---

## 15. Roadmap Futuro (V2)

- Forecast de vendas (Prophet ou statsmodels)
- Alertas via e-mail quando KPI cai abaixo de threshold
- A/B test de pricing simulator (slider "se baixarmos preço em X% → projeção")
- Integração com WhatsApp / Slack para resumo diário automatizado
- Login multi-usuário com perfis (Supabase Auth) e RLS por estado/categoria
- Versão mobile-first com PWA
