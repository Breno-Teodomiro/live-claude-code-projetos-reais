# Dashboard Executivo de Vendas

Dashboard analítico premium para varejo / e-commerce com visão consolidada de
**vendas, clientes, catálogo e inteligência competitiva**.
Construído com **Python · Streamlit · Plotly · Pandas · Supabase**.

### 🌐 Demo online

**👉 [https://insightsjobsia-dashboard.streamlit.app](https://insightsjobsia-dashboard.streamlit.app)**

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://insightsjobsia-dashboard.streamlit.app)
![Stack](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.57-FF4B4B?logo=streamlit&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-Premium-3F4F75?logo=plotly&logoColor=white)
![Supabase](https://img.shields.io/badge/Supabase-Postgres-3FCF8E?logo=supabase&logoColor=white)

---

## 🎯 O que entrega

Seis páginas com 30+ análises acionáveis:

| Página | Para quem | Análises principais |
|--------|-----------|---------------------|
| 📊 **Visão Executiva** | CEO, Diretoria | 8 KPIs, YoY, gauge de meta, mapa BR, top produtos |
| 💰 **Vendas & Performance** | Comercial | Heatmap dia × hora, Pareto, funil, sazonalidade |
| 👥 **Clientes & Geografia** | Marketing | RFM (10 segmentos), cohort, curva ABC, mapa BR |
| 📦 **Catálogo & Produtos** | Compras / Produto | BCG, treemap, sunburst, long tail, sem venda |
| 🎯 **Inteligência Competitiva** | Pricing | Posicionamento vs Amazon/ML/Shopee/Magalu |
| 🗂️ **Dados Brutos** | Analistas | Filtros dinâmicos, exportação CSV/Excel |

Todas as páginas têm **filtros globais persistentes** (período, canal), **insights automáticos
em linguagem natural** e formatação brasileira (R$, %, datas em pt-BR).

---

## ⚡ Setup Rápido

### Pré-requisitos
- Python 3.12+
- [`uv`](https://docs.astral.sh/uv/) (gerenciador de pacotes recomendado)

### Instalação

```bash
# Clonar o repositório
git clone git@github.com:Breno-Teodomiro/live-claude-code-projetos-reais.git
cd live-claude-code-projetos-reais

# Criar virtualenv e instalar dependências
uv sync

# Copiar template de env
cp .env.example .env
# Editar .env com suas credenciais Supabase
```

### Rodar

```bash
uv run streamlit run app.py
```

Abrir em `http://localhost:8501`.

> 💡 **Modo offline:** Se o Supabase estiver indisponível ou com RLS bloqueando,
> o app cai automaticamente para os **CSVs em `arquivos/`** — funciona 100%
> sem internet.

---

## 🗂️ Estrutura

```
.
├── app.py                          # entrypoint Streamlit
├── pages/                          # multi-page (1 a 6)
├── src/
│   ├── data/
│   │   ├── connection.py           # cliente Supabase singleton
│   │   ├── loaders.py              # carga com fallback CSV
│   │   └── transformations.py      # KPIs, RFM, BCG, Pareto, etc.
│   ├── components/
│   │   ├── theme.py                # CSS premium injetado
│   │   ├── kpi_card.py             # card de KPI padrão
│   │   └── filters.py              # filtros globais persistentes
│   ├── charts/                     # funções de gráfico (Plotly)
│   │   ├── executive.py
│   │   ├── sales.py
│   │   ├── customers.py
│   │   ├── catalog.py
│   │   └── competitive.py
│   └── utils/
│       ├── colors.py               # paleta semântica
│       ├── formatters.py           # formatação BR (R$, %, datas)
│       └── constants.py
├── assets/
│   └── geo/br_states.geojson       # mapa do Brasil
├── arquivos/                       # CSVs (fallback)
├── .llm/                           # PRD e planejamento
└── .claude/                        # skills e settings do Claude Code
```

---

## 🧮 Dados

| Tabela | Volume | Descrição |
|--------|--------|-----------|
| `vendas` | 3.020 | Transações (data, cliente, produto, canal, qtd, preço) |
| `produtos` | 215 | Catálogo (categoria, marca, preço) |
| `clientes` | 50 | Cadastro (estado, país, data de cadastro) |
| `precos_competidores` | 728 | Coletas de preço de **Amazon, Magalu, Mercado Livre, Shopee** |

Detalhes técnicos completos em [`database.md`](./database.md).
Documento de planejamento estratégico em [`.llm/planning.md`](./.llm/planning.md).

---

## 🎨 Padrão Visual Premium

- **Tema dark** estilo Stripe/Linear/Vercel (paleta semântica em `src/utils/colors.py`)
- Tipografia: **Inter** (UI) + **JetBrains Mono** (números)
- Plotly com paper/plot bg consistentes, hover unificado em séries temporais,
  formatação BR em todos os tooltips
- KPI cards com hover lift e delta colorido (verde/vermelho conforme contexto)
- Filtros globais persistem entre páginas via `st.session_state`

Padrões consolidados na skill local [`.claude/skills/premium-dashboard-patterns`](./.claude/skills/premium-dashboard-patterns/SKILL.md).

---

## 🛠️ Stack Técnica

| Camada | Tecnologia |
|--------|-----------|
| UI | Streamlit 1.57, st-aggrid, streamlit-extras |
| Visualização | Plotly 5+ (graph_objects, express) |
| Dados | Pandas 2.2, NumPy |
| Backend | Supabase (PostgreSQL 17) |
| Auth backend | python-dotenv |
| Export | openpyxl (xlsx) |
| Gerenciador | uv (lockfile reprodutível) |

---

## 📈 Roadmap

- [x] **Sprint 0** — Fundação (tema, conexão, fallback, skeleton)
- [x] **Sprint 1** — Visão Executiva (8 KPIs, YoY, gauge, mapa, top produtos)
- [x] **Sprint 2** — Vendas (heatmap, Pareto, funil, sazonalidade, canal)
- [x] **Sprint 3** — Clientes (RFM, cohort, ABC, geo, aquisição vs retenção)
- [x] **Sprint 4** — Catálogo (BCG, treemap, sunburst, long tail, sem venda)
- [x] **Sprint 5** — Competitivo (posicionamento, gap categoria, reajustes, histórico)
- [x] **Sprint 6** — Dados Brutos + Polish (filtros, export CSV/Excel)

**Próximos (V2):**
- Forecast de vendas (Prophet)
- Alertas via e-mail/Slack quando KPI cai abaixo de threshold
- Simulador de pricing ("se baixarmos preço em X% → projeção")
- Login multi-usuário com Supabase Auth + RLS por perfil
- Versão mobile-first PWA

---

## 🤝 Contribuindo

O projeto é mantido com auxílio do **Claude Code** seguindo padrões consolidados
em [`CLAUDE.md`](./CLAUDE.md). Sugestões e PRs bem-vindos.

---

## 👤 Autor

**Breno Teodomiro**

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Breno%20Teodomiro-0A66C2?logo=linkedin&logoColor=white)](https://www.linkedin.com/in/breno-teodomiro-power-bi)

---

## 📄 Licença

Uso educacional / demonstração.
Stack open source, dados sintéticos.
