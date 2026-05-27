# Plano Estratégico do Projeto — Dashboard Executivo de Vendas

> Documento de planejamento elaborado sob duas óticas:
> **Arquitetura de Soluções** (decisões técnicas, estrutura, integrações) +
> **Especialista de Negócio** (perguntas de negócio, insights acionáveis, indicadores).

---

## PARTE I — VISÃO DE NEGÓCIO

### 1. Contexto

Empresa de varejo multicanal (loja física + ecommerce) com:
- 215 SKUs ativos distribuídos em múltiplas categorias e marcas
- 50 clientes cadastrados em todo o Brasil
- 3.020 transações registradas
- Monitoramento competitivo em 3 marketplaces (Amazon, Mercado Livre, Shopee)

O negócio precisa migrar da gestão por intuição para **gestão orientada por dados** com clareza sobre receita, clientes, catálogo e posicionamento.

### 2. Stakeholders e suas Perguntas-Chave

| Stakeholder | Pergunta de Negócio | Decisão que toma |
|-------------|---------------------|------------------|
| **CEO** | Estamos crescendo? Em que ritmo? | Investimentos, contratações, metas |
| **Diretor Comercial** | Quais canais e produtos puxam o resultado? | Alocação de orçamento, foco de equipe |
| **Gerente de Marketing** | Onde estão e como se comportam meus clientes? | Campanhas, segmentação, mídia paga |
| **Gestor de Produto** | Quais SKUs vendem? Quais devem sair do catálogo? | Curadoria, encomendas, descontinuação |
| **Pricing Manager** | Estamos competitivos? Onde perder/ganhar margem? | Reajustes, promoções, política de margem |
| **Analista de BI** | Quero validar os números e cruzar livremente | Auditoria, relatórios customizados |

### 3. Objetivos SMART do Projeto

1. **Reduzir tempo de tomada de decisão** de >2 dias (planilhas manuais) para **<2 minutos** (dashboard).
2. **Identificar oportunidades de receita** em ≥10% do catálogo via análise competitiva.
3. **Segmentar 100% da base ativa** em perfis RFM acionáveis.
4. **Disponibilizar dashboard atualizado a cada 5 minutos** (cache TTL).
5. **Atingir adoção semanal** de 100% dos diretores em 30 dias.

### 4. Insights Acionáveis e Indicadores Derivados

Cada insight gera **(a) métrica observável + (b) ação concreta**.

#### 4.1 Insights de Receita

| # | Insight Acionável | Indicador | Ação Recomendada |
|---|-------------------|-----------|------------------|
| R1 | Receita está crescendo ou caindo? | Receita Total + % MoM/YoY | Acionar plano de contingência se ▼ >5% |
| R2 | Qual canal traz mais resultado? | Mix de Receita por Canal (%) | Reforçar verba no canal vencedor |
| R3 | Estamos mais dependentes de volume ou ticket? | Ticket Médio vs Nº Transações (variação %) | Se ticket caindo → trabalhar upsell/bundles |
| R4 | Quando vendemos mais? | Heatmap dia × hora | Concentrar campanhas / staffing em horários quentes |
| R5 | Existe sazonalidade? | Decomposição da série temporal | Antecipar estoque e marketing |

#### 4.2 Insights de Clientes

| # | Insight Acionável | Indicador | Ação Recomendada |
|---|-------------------|-----------|------------------|
| C1 | Quem são meus 20% que geram 80%? | Curva ABC + Top N | CRM dedicado, atendimento premium |
| C2 | Quantos clientes estão "Em Risco"? | Matriz RFM — bucket "Em Risco" | Campanha de reativação personalizada |
| C3 | Como está a retenção mês a mês? | Cohort retention heatmap | Ajustar onboarding/pós-venda |
| C4 | Onde geograficamente concentro receita? | Coroplético estados (R$ por UF) | Marketing regional, logística, novas praças |
| C5 | Estou adquirindo ou só retendo? | Novos vs Recorrentes (stacked monthly) | Equilibrar mídia de aquisição vs CRM |
| C6 | Qual o LTV médio por estado? | LTV = receita acumulada / cliente | Calcular CAC máximo aceitável por região |

#### 4.3 Insights de Catálogo

| # | Insight Acionável | Indicador | Ação Recomendada |
|---|-------------------|-----------|------------------|
| P1 | Quais produtos são "estrelas"? | Matriz BCG (crescimento × participação) | Foco de marketing e estoque garantido |
| P2 | Quais são "abacaxis"? | BCG quadrante inferior esquerdo | Descontinuação, liquidação |
| P3 | Quais SKUs não venderam no período? | Lista de produtos sem venda | Promoção, kit, ou removal |
| P4 | Qual a long tail? | Curva de Pareto produtos | Decidir nível de cauda longa a manter |
| P5 | Quais categorias mais lucram? | Receita e participação por categoria | Expandir mix vencedor |
| P6 | Qual marca puxa cada categoria? | Treemap categoria → marca | Negociação com fornecedores |

#### 4.4 Insights Competitivos

| # | Insight Acionável | Indicador | Ação Recomendada |
|---|-------------------|-----------|------------------|
| K1 | Estamos caros ou baratos? | % SKUs acima/abaixo/paridade vs mediana | Comunicação ("melhor preço") ou reajuste |
| K2 | Em quais categorias perdemos preço? | Heatmap gap por categoria × concorrente | Renegociar com fornecedor da categoria |
| K3 | Quais SKUs têm gap negativo >15%? | Top oportunidades de reajuste | Diminuir preço para recuperar volume |
| K4 | Quais SKUs têm gap positivo (somos mais baratos)? | Top vantagens competitivas | Destacar em campanhas e ads |
| K5 | Concorrente X muda preço com frequência? | Volatilidade de preço por concorrente | Política dinâmica de monitoramento |

### 5. Árvore de KPIs (KPI Tree)

```
                        ╔══════════════════════════╗
                        ║   RECEITA TOTAL (R$)     ║   ← North Star
                        ╚════════════╦═════════════╝
                                     │
              ┌──────────────────────┼──────────────────────┐
              │                      │                      │
       ┌──────▼──────┐       ┌───────▼───────┐      ┌──────▼──────┐
       │  Volume     │       │  Ticket Médio │      │  Mix Canal  │
       │  (# vendas) │       │   (R$/venda)  │      │   (%)       │
       └──────┬──────┘       └───────┬───────┘      └─────────────┘
              │                      │
      ┌───────┴────────┐    ┌────────┴────────┐
      │                │    │                  │
 ┌────▼────┐    ┌──────▼─┐  │             ┌────▼────────────┐
 │ Clientes│    │Vendas/ │  │             │ Itens / venda    │
 │ ativos  │    │cliente │  │             │ × Preço unitário │
 └────┬────┘    └────────┘  │             └──────────────────┘
      │                     │
 ┌────┴──────┐         Mix Produtos
 │ Novos     │         (categoria × marca)
 │ Recorr.   │
 └───────────┘

Métricas de Saúde (não derivadas, mas influenciam):
  • Retenção (% clientes recorrentes)
  • Gap Competitivo Médio
  • Cobertura de catálogo (% SKUs com venda)
```

### 6. Definição Formal dos Indicadores

| Indicador | Fórmula | Tabela | Granularidade |
|-----------|---------|--------|---------------|
| Receita Total | `SUM(quantidade × preco_unitario)` | vendas | dia, mês, ano |
| Ticket Médio | `Receita / COUNT(DISTINCT id_venda)` | vendas | período |
| Volume de Vendas | `COUNT(DISTINCT id_venda)` | vendas | período |
| Itens Vendidos | `SUM(quantidade)` | vendas | período |
| Clientes Ativos | `COUNT(DISTINCT id_cliente)` | vendas | período |
| Receita/Cliente | `Receita / Clientes Ativos` | vendas | período |
| Mix Ecommerce % | `Receita(ecommerce) / Receita Total` | vendas | período |
| % Crescimento MoM | `(R_mes − R_mes-1) / R_mes-1` | vendas | mês |
| Recência (R) | `MAX(data_venda) por cliente` | vendas | cliente |
| Frequência (F) | `COUNT(id_venda) por cliente` | vendas | cliente |
| Monetário (M) | `SUM(receita) por cliente` | vendas | cliente |
| LTV | `M acumulado por cliente` | vendas | cliente |
| Gap Competitivo | `(preco_atual − mediana_concorrentes) / mediana_concorrentes` | produtos ⨝ precos_competidores | SKU |
| Curva ABC | Pareto sobre receita ordenada desc | vendas | produto/cliente |

### 7. Personas e Jornada no Dashboard

```
CEO Roberta (45s)
└─► Página 1 (Executiva)
    └─► KPIs grandes + gráfico YoY + mapa
        └─► [se algo chama atenção] Página 2 ou 5

Diretor Comercial André (5min)
└─► Página 2 (Vendas)
    └─► filtra por canal/categoria
        └─► drill em heatmap dia×hora
            └─► insights para reunião semanal

Gerente Marketing Camila (10min)
└─► Página 3 (Clientes)
    └─► identifica "Em Risco" no RFM
        └─► exporta lista para CRM

Pricing Manager João (15min)
└─► Página 5 (Competitivo)
    └─► top oportunidades de reajuste
        └─► drill em histórico de preços
            └─► aplica decisão de pricing
```

---

## PARTE II — ARQUITETURA DE SOLUÇÕES

### 8. Visão Arquitetural

```
┌─────────────────────────────────────────────────────────────┐
│                     CAMADA DE APRESENTAÇÃO                  │
│   Streamlit (multi-page) · Plotly · st-aggrid · Inter font  │
└────────────────────────────┬────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────┐
│                  CAMADA DE APLICAÇÃO                        │
│  • Components (kpi_card, filters, theme)                    │
│  • Charts (funções puras → Plotly Figure)                   │
│  • Transformations (RFM, cohort, BCG, ABC, Pareto)          │
│  • State Manager (st.session_state para filtros globais)    │
└────────────────────────────┬────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────┐
│                  CAMADA DE DADOS                            │
│  • SupabaseClient (singleton, @st.cache_resource)           │
│  • Queries SQL parametrizadas (pré-agregadas)               │
│  • Cache (@st.cache_data ttl=300s)                          │
│  • Fallback: CSV local em /arquivos                         │
└────────────────────────────┬────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────┐
│              SUPABASE (PostgreSQL 17)                       │
│  Schema: JORNADA_DADOS_CLAUDE_CODE_PROJ_REAIS               │
│  Tables: vendas, produtos, clientes, precos_competidores    │
└─────────────────────────────────────────────────────────────┘
```

### 9. Decisões Arquiteturais (ADRs Resumidos)

| # | Decisão | Justificativa | Alternativas Rejeitadas |
|---|---------|---------------|--------------------------|
| ADR-01 | Streamlit como framework | Velocidade de entrega, Python-first, baixa curva de aprendizado | Dash, Panel, Gradio |
| ADR-02 | Plotly para gráficos | Interatividade nativa, ecossistema, exportação | Matplotlib, Altair |
| ADR-03 | Supabase como backend | Já provisionado, Postgres real, MCP integrado | DuckDB local, Firebase |
| ADR-04 | uv como gerenciador | Velocidade (10–100× pip), lock determinístico | pip + venv, Poetry |
| ADR-05 | Pré-agregação no SQL | Postgres é mais rápido que pandas em volumes >100k | Agregar tudo em pandas |
| ADR-06 | Cache em duas camadas | `@st.cache_resource` (conexão) + `@st.cache_data` (queries) | Sem cache, Redis |
| ADR-07 | Filtros globais via session_state | Coerência entre páginas, UX consistente | Query string, sem persistência |
| ADR-08 | CSVs como fallback offline | Dev sem internet, demo, testes | Apenas online |
| ADR-09 | RLS habilitado, policies depois | Segurança por padrão, restritivo até definir regras | Desabilitar RLS |

### 10. Modelo de Dados Lógico (com chaves a adicionar)

Necessário criar (via migration futura):

```sql
ALTER TABLE clientes ADD PRIMARY KEY (id_cliente);
ALTER TABLE produtos ADD PRIMARY KEY (id_produto);
ALTER TABLE vendas   ADD PRIMARY KEY (id_venda);

ALTER TABLE vendas
  ADD CONSTRAINT fk_vendas_cliente
  FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente);

ALTER TABLE vendas
  ADD CONSTRAINT fk_vendas_produto
  FOREIGN KEY (id_produto) REFERENCES produtos(id_produto);

ALTER TABLE precos_competidores
  ADD CONSTRAINT fk_pc_produto
  FOREIGN KEY (id_produto) REFERENCES produtos(id_produto);

-- Índices para performance
CREATE INDEX idx_vendas_data ON vendas(data_venda);
CREATE INDEX idx_vendas_cliente ON vendas(id_cliente);
CREATE INDEX idx_vendas_produto ON vendas(id_produto);
CREATE INDEX idx_pc_produto_data ON precos_competidores(id_produto, data_coleta);
```

### 11. Estrutura de Pastas Final

```
.
├── app.py                              # entrypoint
├── pages/                              # multi-page Streamlit
│   ├── 1_📊_Visao_Executiva.py
│   ├── 2_💰_Vendas.py
│   ├── 3_👥_Clientes.py
│   ├── 4_📦_Catalogo.py
│   ├── 5_🎯_Competitivo.py
│   └── 6_🗂️_Dados_Brutos.py
├── src/
│   ├── __init__.py
│   ├── data/
│   │   ├── connection.py               # cliente Supabase singleton
│   │   ├── queries.py                  # SQL parametrizado
│   │   ├── loaders.py                  # interface (Supabase OU CSV)
│   │   └── transformations.py          # RFM, cohort, BCG, ABC
│   ├── components/
│   │   ├── kpi_card.py                 # card padrão big number + delta + sparkline
│   │   ├── filters.py                  # filtros globais (date range, multi-select)
│   │   ├── theme.py                    # paleta, fontes, CSS injetado
│   │   └── header.py                   # cabeçalho com logo
│   ├── charts/
│   │   ├── executive.py                # YoY, gauge, mapa BR, donut canal
│   │   ├── sales.py                    # heatmap, Pareto, funil
│   │   ├── customers.py                # RFM, cohort, ABC, treemap geo
│   │   ├── catalog.py                  # BCG, treemap, sunburst
│   │   └── competitive.py              # scatter posicionamento, radar, heatmap gap
│   └── utils/
│       ├── formatters.py               # fmt_brl, fmt_pct, fmt_date_br
│       ├── colors.py                   # paleta semântica
│       └── constants.py                # SCHEMA, TABLES, etc.
├── assets/
│   ├── logo.svg
│   ├── style.css                       # overrides finos
│   └── geo/
│       └── br_states.geojson
├── .streamlit/
│   └── config.toml                     # tema base (dark)
├── arquivos/                           # CSVs (fallback offline)
├── tests/
│   ├── test_transformations.py
│   └── test_formatters.py
├── .env                                # secrets locais (gitignored)
├── .env.example
├── .gitignore
├── pyproject.toml
├── uv.lock
├── CLAUDE.md
├── database.md
└── README.md
```

### 12. Padrões de Código

- **Funções de carga retornam DataFrame** com colunas/tipos validados
- **Funções de gráfico recebem DataFrame e retornam `plotly.graph_objects.Figure`**
- **Sem lógica de negócio nas páginas** — apenas composição de componentes
- **Type hints obrigatórios** em assinaturas públicas
- **Docstrings curtas** somente quando o nome não basta
- **Testes unitários** apenas para `transformations.py` e `formatters.py` (lógica pura)

### 13. Performance — Metas e Estratégias

| Métrica | Meta | Estratégia |
|---------|------|------------|
| Carregamento inicial | < 3s (cache morno) | Cache + pré-agregação SQL |
| Mudança de filtro | < 800ms | Pré-aggregate em queries, índices |
| Memória do app | < 512MB | Não fazer `SELECT *`, usar agregados |
| Hit-rate cache | > 80% | TTL 300s, parâmetros estáveis |

---

## PARTE III — ROADMAP DE EXECUÇÃO

### 14. Fases e Sprints

#### **Sprint 0 — Fundação (Dia 1)**
- [ ] Criar PKs e FKs no banco (via `apply_migration`)
- [ ] Criar índices de performance
- [ ] Configurar tema base (`.streamlit/config.toml`)
- [ ] Implementar `connection.py`, `loaders.py` com fallback CSV
- [ ] Implementar `formatters.py`, `colors.py`, `theme.py`
- [ ] Skeleton de `app.py` com navegação multi-page

**Critério de pronto:** `streamlit run app.py` exibe 6 páginas vazias com tema aplicado.

#### **Sprint 1 — Visão Executiva (Dia 2)**
- [ ] Componente `kpi_card` com sparkline
- [ ] 8 KPIs calculados e exibidos
- [ ] Gráfico YoY (linha + área)
- [ ] Gauge de meta
- [ ] Mapa coroplético do Brasil
- [ ] Donut canal
- [ ] Top 10 produtos

**Critério de pronto:** Diretoria consegue responder "estamos crescendo?" em 10s.

#### **Sprint 2 — Vendas (Dia 3)**
- [ ] Filtros globais persistentes
- [ ] Heatmap dia × hora
- [ ] Pareto produtos
- [ ] Distribuição de ticket
- [ ] Funil
- [ ] Área empilhada de canal no tempo

**Critério de pronto:** Diretor comercial identifica top produtos e horários quentes. ✅ ENTREGUE

#### **Sprint 3 — Clientes (Dia 4)**
- [ ] Cálculo RFM (transformação)
- [ ] Matriz RFM visual
- [ ] Cohort retention heatmap
- [ ] Curva ABC clientes
- [ ] Coroplético + treemap geográfico
- [ ] Aquisição vs Retenção

**Critério de pronto:** Marketing exporta lista de clientes "Em Risco".

#### **Sprint 4 — Catálogo (Dia 5)**
- [ ] Treemap hierárquico categoria→marca→produto
- [ ] Matriz BCG
- [ ] Sunburst
- [ ] Long tail
- [ ] Produtos sem venda

**Critério de pronto:** Compras tem lista de SKUs candidatos a descontinuação.

#### **Sprint 5 — Competitivo (Dia 6)**
- [ ] Painel de posicionamento
- [ ] Scatter preço nosso × concorrentes
- [ ] Heatmap gap categoria × concorrente
- [ ] Top oportunidades de reajuste
- [ ] Histórico de preços (drill)

**Critério de pronto:** Pricing aprova ou ajusta ≥5 SKUs por dia.

#### **Sprint 6 — Dados Brutos + Polish (Dia 7)**
- [ ] st-aggrid com filtros e busca
- [ ] Exportação CSV/Excel
- [ ] Toggle dark/light
- [ ] Animações de transição
- [ ] Auditoria de formatação BR
- [ ] README final + instruções de deploy

**Critério de pronto:** Analista exporta query customizada em <30s.

### 15. Riscos e Mitigações

| Risco | Probabilidade | Impacto | Mitigação |
|-------|---------------|---------|-----------|
| RLS sem policy bloqueia leitura | Alta | Alto | Criar policies de leitura para anon antes do Sprint 1 |
| Dados sujos em `produtos_sujo` poluindo análises | Média | Médio | Ignorar tabela; documentar em CLAUDE.md |
| Performance degrada em filtros grandes | Baixa | Médio | Pré-aggregate + índices |
| Mapa do Brasil exige GeoJSON externo | Alta | Baixo | Baixar GeoJSON oficial do IBGE e versionar |
| Falta de variação YoY (poucos dados históricos) | Média | Médio | Comparar período × período anterior, não YoY |
| Volume pequeno (50 clientes) gera RFM trivial | Alta | Baixo | Ainda assim mostrar; será robusto quando escalar |

### 16. Métricas de Sucesso do Projeto

| Métrica | Como medir | Meta |
|---------|------------|------|
| Adoção semanal | Logs de acesso (Supabase Auth futuro) | ≥ 1×/semana por diretor |
| Tempo de decisão | Survey trimestral | < 2 min para responder pergunta executiva |
| Satisfação | NPS interno | ≥ 50 |
| Cobertura de KPIs | Checklist do PRD | 100% |
| Performance | Lighthouse / tempo medido | < 3s carregamento |

---

## PARTE IV — PRÓXIMOS PASSOS IMEDIATOS

1. ✅ **Aprovação deste plano** pelo product owner
2. 🔜 Aplicar PKs/FKs/índices no Supabase (`apply_migration`)
3. 🔜 Criar policies de RLS (leitura para `anon`)
4. 🔜 Iniciar Sprint 0 (fundação)
5. 🔜 Configurar pipeline de seed (caso queira repopular dados)

**Pergunta para o stakeholder antes de começar:**
- Existe meta de receita oficial para alimentar o gauge da Página 1?
- Quais concorrentes além de Amazon/ML/Shopee devem ser monitorados?
- Há restrição de exibição de dados sensíveis (nomes de clientes) entre perfis?
