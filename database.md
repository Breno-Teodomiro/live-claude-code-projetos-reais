# Documentação Técnica do Banco de Dados

## Visão Geral

| Item | Valor |
|------|-------|
| **Plataforma** | Supabase (PostgreSQL) |
| **URL do Projeto** | `https://iinfocxymnnyhghsmulg.supabase.co` |
| **Schema Principal** | `JORNADA_DADOS_CLAUDE_CODE_PROJ_REAIS` |
| **Total de Tabelas** | 5 |
| **Migrações Registradas** | 0 |

---

## Schema: `JORNADA_DADOS_CLAUDE_CODE_PROJ_REAIS`

### Diagrama de Relacionamentos

```
┌─────────────┐        ┌──────────────┐        ┌────────────────────┐
│   clientes  │        │    vendas    │        │      produtos      │
│─────────────│        │──────────────│        │────────────────────│
│ id_cliente  │◄───────│ id_cliente   │───────►│ id_produto         │
│ nome_cliente│        │ id_venda     │        │ nome_produto       │
│ estado      │        │ data_venda   │        │ categoria          │
│ pais        │        │ id_produto   │        │ marca              │
│ data_cadastro        │ canal_venda  │        │ preco_atual        │
└─────────────┘        │ quantidade   │        │ data_criacao       │
                       │ preco_unit.. │        └────────────────────┘
                       └──────────────┘                 ▲
                                                        │
                                          ┌─────────────────────────┐
                                          │   precos_competidores   │
                                          │─────────────────────────│
                                          │ id_produto              │
                                          │ nome_concorrente        │
                                          │ preco_concorrente       │
                                          │ data_coleta             │
                                          └─────────────────────────┘

┌─────────────────────────────────────────────────┐
│  produtos_sujo  (tabela de staging / dados brutos)│
└─────────────────────────────────────────────────┘
```

> **Nota:** Os relacionamentos são lógicos. Não há foreign keys ou primary keys definidas no banco de dados.

---

## Tabelas

### `clientes`

Cadastro de clientes da empresa.

| Propriedade | Valor |
|-------------|-------|
| Linhas | 50 |
| RLS | Habilitado |
| Primary Key | Nenhuma |

| Coluna | Tipo | Nulo | Descrição |
|--------|------|------|-----------|
| `id_cliente` | `text` | sim | Identificador único do cliente (ex: `cus_71308b76151a`) |
| `nome_cliente` | `text` | sim | Nome completo do cliente |
| `estado` | `text` | sim | Sigla do estado brasileiro (ex: `SP`, `MS`, `MT`) |
| `pais` | `text` | sim | País do cliente (ex: `Brasil`) |
| `data_cadastro` | `timestamptz` | sim | Data e hora do cadastro com fuso horário |

**Exemplo de registro:**
```json
{
  "id_cliente": "cus_71308b76151a",
  "nome_cliente": "Srta. Amanda Sousa",
  "estado": "MS",
  "pais": "Brasil",
  "data_cadastro": "2023-10-03 13:49:51+00"
}
```

---

### `produtos`

Catálogo de produtos comercializados.

| Propriedade | Valor |
|-------------|-------|
| Linhas | 215 |
| RLS | Habilitado |
| Primary Key | Nenhuma |

| Coluna | Tipo | Nulo | Descrição |
|--------|------|------|-----------|
| `id_produto` | `text` | sim | Identificador único do produto (ex: `prd_2293732b7542`) |
| `nome_produto` | `text` | sim | Nome do produto |
| `categoria` | `text` | sim | Categoria do produto (ex: `Casa`, `Eletrônicos`) |
| `marca` | `text` | sim | Marca do produto |
| `preco_atual` | `float8` | sim | Preço atual de venda em reais |
| `data_criacao` | `timestamptz` | sim | Data de criação do produto no catálogo |

**Exemplo de registro:**
```json
{
  "id_produto": "prd_2293732b7542",
  "nome_produto": "Cortina Blackout",
  "categoria": "Casa",
  "marca": "Xiaomi",
  "preco_atual": 68.9,
  "data_criacao": "2022-12-13 17:49:51+00"
}
```

---

### `vendas`

Registro de todas as transações de venda.

| Propriedade | Valor |
|-------------|-------|
| Linhas | 3.020 |
| RLS | Habilitado |
| Primary Key | Nenhuma |

| Coluna | Tipo | Nulo | Descrição |
|--------|------|------|-----------|
| `id_venda` | `text` | sim | Identificador único da venda (ex: `sal_adff6978b0c6`) |
| `data_venda` | `timestamptz` | sim | Data e hora da venda com fuso horário |
| `id_cliente` | `text` | sim | Referência ao `id_cliente` da tabela `clientes` |
| `id_produto` | `text` | sim | Referência ao `id_produto` da tabela `produtos` |
| `canal_venda` | `text` | sim | Canal de venda (ex: `loja_fisica`, `ecommerce`) |
| `quantidade` | `int8` | sim | Quantidade de itens vendidos |
| `preco_unitario` | `float8` | sim | Preço unitário cobrado na venda em reais |

**Exemplo de registro:**
```json
{
  "id_venda": "sal_adff6978b0c6",
  "data_venda": "2025-12-13 17:38:09+00",
  "id_cliente": "cus_508a15ccf0fa",
  "id_produto": "prd_96fbc500aec1",
  "canal_venda": "loja_fisica",
  "quantidade": 2,
  "preco_unitario": 64.79
}
```

**Canais de venda identificados:**
- `loja_fisica`
- `ecommerce`

---

### `precos_competidores`

Monitoramento de preços praticados por concorrentes para os produtos do catálogo.

| Propriedade | Valor |
|-------------|-------|
| Linhas | 728 |
| RLS | Habilitado |
| Primary Key | Nenhuma |

| Coluna | Tipo | Nulo | Descrição |
|--------|------|------|-----------|
| `id_produto` | `text` | sim | Referência ao `id_produto` da tabela `produtos` |
| `nome_concorrente` | `text` | sim | Nome do concorrente/marketplace (ex: `Amazon`, `Shopee`) |
| `preco_concorrente` | `float8` | sim | Preço praticado pelo concorrente em reais |
| `data_coleta` | `timestamptz` | sim | Data e hora em que o preço foi coletado |

**Exemplo de registro:**
```json
{
  "id_produto": "prd_2293732b7542",
  "nome_concorrente": "Mercado Livre",
  "preco_concorrente": 65.45,
  "data_coleta": "2026-01-11 17:35:52+00"
}
```

**Concorrentes monitorados (exemplos identificados):**
- Amazon
- Mercado Livre
- Shopee

---

### `produtos_sujo`

Tabela de staging com dados brutos/não tratados de produtos. Utilizada como fonte de dados antes da limpeza e carga na tabela `produtos`.

| Propriedade | Valor |
|-------------|-------|
| Linhas | 39 |
| RLS | Habilitado |
| Primary Key | Nenhuma |

| Coluna | Tipo | Nulo | Descrição |
|--------|------|------|-----------|
| `id_produto` | `text` | sim | Identificador do produto |
| `Nome_Produto` | `text` | sim | Nome do produto (nomenclatura inconsistente com PascalCase) |
| `CATEGORIA` | `text` | sim | Categoria (nomenclatura em MAIÚSCULAS, valores inconsistentes) |
| `marca` | `text` | sim | Marca do produto |
| `preco_atual` | `text` | sim | Preço armazenado como texto (sem tipagem numérica) |
| `Data_Criacao` | `text` | sim | Data armazenada como texto com formatos mistos |

**Problemas de qualidade identificados:**
- Nomenclatura de colunas inconsistente (`Nome_Produto`, `CATEGORIA`, `Data_Criacao`)
- Campo `preco_atual` armazenado como `text` em vez de numérico
- Campo `Data_Criacao` em texto com formatos de data mistos:
  - `13/12/2022` (DD/MM/YYYY)
  - `08-19-2022` (MM-DD-YYYY)
  - `2023-06-28 17:49:51` (ISO 8601)
- Valores de `CATEGORIA` com capitalização inconsistente (ex: `Casa` vs `eletronicos`)

---

## Extensions Instaladas

| Extension | Schema | Versão | Descrição |
|-----------|--------|--------|-----------|
| `plpgsql` | `pg_catalog` | 1.0 | Linguagem procedural PL/pgSQL |
| `pgcrypto` | `extensions` | 1.3 | Funções criptográficas |
| `uuid-ossp` | `extensions` | 1.1 | Geração de UUIDs |
| `pg_stat_statements` | `extensions` | 1.11 | Rastreamento de estatísticas de queries SQL |
| `supabase_vault` | `vault` | 0.3.1 | Gerenciamento seguro de secrets |

**Extensions disponíveis (não instaladas) — destaques:**
- `vector` (0.8.0) — Suporte a embeddings e busca vetorial
- `pg_cron` (1.6.4) — Agendador de jobs no banco
- `pg_trgm` (1.6) — Busca por similaridade de texto com trigramas
- `postgis` (3.3.7) — Suporte a dados geoespaciais
- `pg_graphql` (1.5.11) — API GraphQL diretamente no Postgres

---

## Avisos e Recomendações

### Segurança

> **RLS sem Policies** — Todas as 5 tabelas têm Row Level Security (RLS) habilitado, porém **nenhuma policy foi definida**. Isso significa que nenhuma linha será retornada para clientes da API (anon/authenticated) enquanto não houver policies configuradas.
>
> Referência: [Supabase Docs — RLS Enabled No Policy](https://supabase.com/docs/guides/database/database-linter?lint=0008_rls_enabled_no_policy)

**Tabelas afetadas:** `clientes`, `produtos`, `vendas`, `precos_competidores`, `produtos_sujo`

### Performance

> **Ausência de Primary Keys** — Nenhuma das 5 tabelas possui chave primária definida. Tabelas sem PK são menos eficientes em operações de UPDATE, DELETE e replicação, e impossibilitam relacionamentos formais via foreign keys.
>
> Referência: [Supabase Docs — No Primary Key](https://supabase.com/docs/guides/database/database-linter?lint=0004_no_primary_key)

**Sugestão de PKs:**

| Tabela | Coluna sugerida para PK |
|--------|------------------------|
| `clientes` | `id_cliente` |
| `produtos` | `id_produto` |
| `vendas` | `id_venda` |
| `precos_competidores` | Chave composta: `(id_produto, nome_concorrente, data_coleta)` |
| `produtos_sujo` | `id_produto` (após limpeza) |

### Qualidade de Dados

- A tabela `produtos_sujo` requer pipeline de limpeza antes de integrar dados à tabela `produtos`
- Considerar adicionar constraints de NOT NULL para colunas identificadoras (`id_cliente`, `id_produto`, `id_venda`)
- Considerar adicionar foreign keys entre `vendas.id_cliente → clientes.id_cliente` e `vendas.id_produto → produtos.id_produto`

---

## Estatísticas Gerais

| Tabela | Linhas |
|--------|--------|
| `clientes` | 50 |
| `produtos` | 215 |
| `vendas` | 3.020 |
| `precos_competidores` | 728 |
| `produtos_sujo` | 39 |
| **Total** | **4.052** |
