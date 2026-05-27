# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Idioma

Sempre se comunicar com o usuário em **português brasileiro (pt-BR)**, independentemente do idioma da pergunta.

## Project Status

**✅ MVP completo e deployado em produção.**

- 🌐 **App ao vivo:** https://insightsjobsia-dashboard.streamlit.app
- 📦 **Repositório:** https://github.com/Breno-Teodomiro/live-claude-code-projetos-reais
- ✅ **7 sprints concluídas** (0 a 6) — fundação, 5 páginas analíticas, dados brutos
- 🎯 Filtros globais persistentes via `st.session_state`
- 💾 Fallback automático para CSV em `arquivos/` quando Supabase indisponível
- 🔑 Secrets via `st.secrets` (Streamlit Cloud) OU `.env` (local) — auto-detect em `src/data/connection.py`

Para evoluir o projeto, consulte `.llm/planning.md` (sprints e decisões arquiteturais) e `.llm/prd.md` (spec do produto). Padrões visuais consolidados na skill local `.claude/skills/premium-dashboard-patterns/SKILL.md`.

## What's Being Built

A **premium executive dashboard** for an e-commerce/retail business with 6 pages:

1. Executive Overview (CEO/Diretoria)
2. Sales & Performance (Comercial)
3. Customers & Geography (Marketing — RFM, cohorts, choropleth)
4. Catalog & Products (BCG matrix, treemaps, long tail)
5. Competitive Intelligence (price vs Amazon, Mercado Livre, Shopee)
6. Raw Data (audit & export)

**Stack:** Python · Streamlit · Plotly · Pandas · Supabase (PostgreSQL).

## Data Backend

The project connects to a Supabase project at `https://iinfocxymnnyhghsmulg.supabase.co`.

- **Schema:** `JORNADA_DADOS_CLAUDE_CODE_PROJ_REAIS` (note: NOT `public` — must quote in SQL)
- **Tables:** `vendas` (3.020), `produtos` (215), `clientes` (50), `precos_competidores` (728), `produtos_sujo` (39, staging — ignore)
- **No primary keys, no foreign keys** — relationships are logical only:
  - `vendas.id_cliente → clientes.id_cliente`
  - `vendas.id_produto → produtos.id_produto`
  - `precos_competidores.id_produto → produtos.id_produto`
- **RLS is enabled on all tables but no policies exist** — API access via anon key will return zero rows until policies are added. See `database.md` for full schema details.
- The `produtos_sujo` table contains dirty/raw staging data (text-typed numbers, mixed date formats) — do not use it as a source for the dashboard.

The CSVs in `arquivos/` are an exact mirror of the Supabase tables and can be used for local development without hitting the API.

## MCP & Skills

- **Supabase MCP server** is preconfigured in `.mcp.json`. Use its tools (`mcp__supabase__list_tables`, `execute_sql`, `apply_migration`, etc.) for any DB inspection or DDL work — prefer this over manual SQL files.
- **Installed skills** (auto-invoked when relevant):
  - `supabase` — for any Supabase task
  - `supabase-postgres-best-practices` — for Postgres optimization
  - `data-analyst` — for SQL/pandas/statistical analysis

## Working Conventions

- **Brazilian formatting throughout the UI:** `R$ 1.234.567,89`, dates as `26 de mai. de 2026`, percentages with comma decimal.
- **Color semantics:** verde (positivo/meta atingida), vermelho (negativo), neutro azul/ciano for informational. See palette block in `.llm/prd.md` §11.
- **Cache strategy:** all data queries should use `@st.cache_data(ttl=300)`; Supabase client should be `@st.cache_resource`.
- **Pre-aggregate in SQL, not Python** — push heavy work to Postgres.

## Commands

There is no `requirements.txt`, `package.json`, or build tooling yet — these will be created when implementation begins. Per the PRD, expected commands once scaffolded will be:

```bash
pip install -r requirements.txt
streamlit run app.py
```

Credentials will live in a `.env` file (`SUPABASE_URL`, `SUPABASE_KEY`).
