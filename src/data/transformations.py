"""Transformações e cálculos de KPIs."""

from datetime import datetime, timedelta
from typing import Tuple
import pandas as pd

from src.utils.constants import META_CRESCIMENTO_DEFAULT


def filter_periodo(df: pd.DataFrame, col: str, inicio: datetime, fim: datetime) -> pd.DataFrame:
    return df[(df[col] >= inicio) & (df[col] <= fim)]


def kpis_periodo(vendas: pd.DataFrame) -> dict:
    if vendas.empty:
        return {
            "receita": 0.0, "ticket_medio": 0.0, "n_vendas": 0,
            "itens": 0, "clientes_ativos": 0, "receita_por_cliente": 0.0,
            "mix_ecommerce": 0.0,
        }
    receita = float(vendas["receita"].sum())
    n_vendas = int(vendas["id_venda"].nunique())
    itens = int(vendas["quantidade"].sum())
    clientes_ativos = int(vendas["id_cliente"].nunique())
    receita_ecom = float(vendas.loc[vendas["canal_venda"] == "ecommerce", "receita"].sum())
    return {
        "receita": receita,
        "ticket_medio": receita / n_vendas if n_vendas else 0.0,
        "n_vendas": n_vendas,
        "itens": itens,
        "clientes_ativos": clientes_ativos,
        "receita_por_cliente": receita / clientes_ativos if clientes_ativos else 0.0,
        "mix_ecommerce": receita_ecom / receita if receita else 0.0,
    }


def kpis_com_delta(vendas: pd.DataFrame, inicio: datetime, fim: datetime) -> dict:
    """Calcula KPIs do período + variação % vs período anterior de mesmo tamanho."""
    duracao = fim - inicio
    inicio_ant = inicio - duracao
    fim_ant = inicio - timedelta(microseconds=1)

    atual = filter_periodo(vendas, "data_venda", inicio, fim)
    anterior = filter_periodo(vendas, "data_venda", inicio_ant, fim_ant)

    k_atual = kpis_periodo(atual)
    k_ant = kpis_periodo(anterior)

    result = {}
    for key, val in k_atual.items():
        prev = k_ant.get(key, 0)
        delta = (val - prev) / prev if prev else None
        result[key] = {"valor": val, "anterior": prev, "delta": delta}
    return result


def serie_temporal_receita(vendas: pd.DataFrame, freq: str = "D") -> pd.DataFrame:
    if vendas.empty:
        return pd.DataFrame(columns=["periodo", "receita"])
    df = (
        vendas.set_index("data_venda")["receita"]
        .resample(freq).sum()
        .reset_index()
        .rename(columns={"data_venda": "periodo"})
    )
    return df


def receita_yoy(vendas: pd.DataFrame) -> pd.DataFrame:
    """Receita mensal com coluna de ano para comparação YoY."""
    if vendas.empty:
        return pd.DataFrame(columns=["mes", "ano", "receita"])
    df = vendas.copy()
    df["ano"] = df["data_venda"].dt.year
    df["mes"] = df["data_venda"].dt.month
    return df.groupby(["ano", "mes"], as_index=False)["receita"].sum().sort_values(["ano", "mes"])


def receita_por_estado(vendas: pd.DataFrame, clientes: pd.DataFrame) -> pd.DataFrame:
    if vendas.empty or clientes.empty:
        return pd.DataFrame(columns=["estado", "receita", "n_vendas", "clientes"])
    df = vendas.merge(clientes[["id_cliente", "estado"]], on="id_cliente", how="left")
    agg = df.groupby("estado", as_index=False).agg(
        receita=("receita", "sum"),
        n_vendas=("id_venda", "nunique"),
        clientes=("id_cliente", "nunique"),
    ).sort_values("receita", ascending=False)
    return agg


def receita_por_canal(vendas: pd.DataFrame) -> pd.DataFrame:
    if vendas.empty:
        return pd.DataFrame(columns=["canal_venda", "receita", "n_vendas"])
    return vendas.groupby("canal_venda", as_index=False).agg(
        receita=("receita", "sum"),
        n_vendas=("id_venda", "nunique"),
    ).sort_values("receita", ascending=False)


def top_produtos(vendas: pd.DataFrame, produtos: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    if vendas.empty:
        return pd.DataFrame(columns=["id_produto", "nome_produto", "receita", "quantidade"])
    df = vendas.merge(produtos[["id_produto", "nome_produto", "categoria"]], on="id_produto", how="left")
    agg = df.groupby(["id_produto", "nome_produto", "categoria"], as_index=False).agg(
        receita=("receita", "sum"),
        quantidade=("quantidade", "sum"),
    ).sort_values("receita", ascending=False).head(n)
    return agg


def meta_e_realizado(vendas_atual: pd.DataFrame, vendas_anterior: pd.DataFrame, growth: float = META_CRESCIMENTO_DEFAULT) -> Tuple[float, float, float]:
    """Retorna (realizado, meta, %atingido). Meta = receita_anterior * (1 + growth)."""
    realizado = float(vendas_atual["receita"].sum()) if not vendas_atual.empty else 0.0
    base = float(vendas_anterior["receita"].sum()) if not vendas_anterior.empty else 0.0
    meta = base * (1 + growth) if base > 0 else realizado * 1.1
    pct = realizado / meta if meta > 0 else 0.0
    return realizado, meta, pct


# ============================================================
# SPRINT 2 — Vendas & Performance
# ============================================================

DIAS_PT = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]


def heatmap_dia_hora(vendas: pd.DataFrame) -> pd.DataFrame:
    """Receita por dia da semana × hora do dia."""
    if vendas.empty:
        return pd.DataFrame()
    df = vendas.copy()
    df["dia_semana"] = df["data_venda"].dt.dayofweek
    df["hora"] = df["data_venda"].dt.hour
    pivot = df.pivot_table(values="receita", index="dia_semana", columns="hora", aggfunc="sum", fill_value=0)
    pivot.index = [DIAS_PT[i] for i in pivot.index]
    return pivot


def pareto_produtos(vendas: pd.DataFrame, produtos: pd.DataFrame, top_n: int = 30) -> pd.DataFrame:
    """Curva de Pareto: produtos ordenados por receita + % acumulado."""
    if vendas.empty:
        return pd.DataFrame(columns=["nome_produto", "receita", "pct_acumulado"])
    df = vendas.merge(produtos[["id_produto", "nome_produto"]], on="id_produto", how="left")
    agg = df.groupby("nome_produto", as_index=False)["receita"].sum().sort_values("receita", ascending=False)
    total = agg["receita"].sum()
    agg["pct_acumulado"] = agg["receita"].cumsum() / total if total else 0
    return agg.head(top_n)


def evolucao_canal(vendas: pd.DataFrame, freq: str = "W") -> pd.DataFrame:
    """Receita por canal ao longo do tempo (área empilhada)."""
    if vendas.empty:
        return pd.DataFrame(columns=["periodo", "canal_venda", "receita"])
    df = (
        vendas.groupby([pd.Grouper(key="data_venda", freq=freq), "canal_venda"], as_index=False)["receita"]
        .sum()
        .rename(columns={"data_venda": "periodo"})
    )
    return df


def distribuicao_ticket(vendas: pd.DataFrame) -> pd.Series:
    """Série de tickets (receita por venda) para histograma + boxplot."""
    if vendas.empty:
        return pd.Series(dtype=float)
    return vendas.groupby("id_venda")["receita"].sum()


def funil_vendas(vendas: pd.DataFrame, clientes: pd.DataFrame, produtos: pd.DataFrame) -> pd.DataFrame:
    """Funil: Clientes cadastrados → Clientes ativos → Vendas → Itens."""
    n_clientes_cad = len(clientes)
    n_clientes_ativos = vendas["id_cliente"].nunique() if not vendas.empty else 0
    n_vendas = vendas["id_venda"].nunique() if not vendas.empty else 0
    n_itens = int(vendas["quantidade"].sum()) if not vendas.empty else 0
    return pd.DataFrame({
        "etapa": ["Base cadastrada", "Clientes ativos", "Transações", "Itens vendidos"],
        "valor": [n_clientes_cad, n_clientes_ativos, n_vendas, n_itens],
    })


def sazonalidade_mensal(vendas: pd.DataFrame) -> pd.DataFrame:
    """Heatmap calendário: ano × mês."""
    if vendas.empty:
        return pd.DataFrame()
    df = vendas.copy()
    df["ano"] = df["data_venda"].dt.year
    df["mes"] = df["data_venda"].dt.month
    pivot = df.pivot_table(values="receita", index="ano", columns="mes", aggfunc="sum", fill_value=0)
    return pivot


def media_movel(serie_temporal: pd.DataFrame, janela: int = 7) -> pd.DataFrame:
    """Adiciona coluna de média móvel à série temporal."""
    if serie_temporal.empty:
        return serie_temporal
    df = serie_temporal.copy()
    df["media_movel"] = df["receita"].rolling(window=janela, min_periods=1).mean()
    return df


# ============================================================
# SPRINT 3 — Clientes & Geografia
# ============================================================

RFM_SEGMENTOS = {
    "Campeões":        "🏆",
    "Leais":           "💎",
    "Potenciais":      "🌱",
    "Novos":           "✨",
    "Promissores":     "🌟",
    "Atenção":         "⚠️",
    "Em Risco":        "🔥",
    "Não Posso Perder": "🆘",
    "Hibernando":      "💤",
    "Perdidos":        "👋",
}


def rfm(vendas: pd.DataFrame, ref_date: pd.Timestamp | None = None) -> pd.DataFrame:
    """Calcula RFM por cliente com segmentação clássica em buckets 1-4."""
    if vendas.empty:
        return pd.DataFrame(columns=["id_cliente", "recencia", "frequencia", "monetario", "R", "F", "M", "score", "segmento"])
    if ref_date is None:
        ref_date = vendas["data_venda"].max()
    agg = vendas.groupby("id_cliente").agg(
        recencia=("data_venda", lambda x: (ref_date - x.max()).days),
        frequencia=("id_venda", "nunique"),
        monetario=("receita", "sum"),
    ).reset_index()

    # Scores 1-4 (quartis). Recência: menor é melhor (invertemos via rank desc).
    agg["R"] = pd.qcut((-agg["recencia"]).rank(method="first"), q=4, labels=[1, 2, 3, 4]).astype(int)
    agg["F"] = pd.qcut(agg["frequencia"].rank(method="first"), q=4, labels=[1, 2, 3, 4]).astype(int)
    agg["M"] = pd.qcut(agg["monetario"].rank(method="first"), q=4, labels=[1, 2, 3, 4]).astype(int)
    agg["score"] = agg["R"] * 100 + agg["F"] * 10 + agg["M"]
    agg["segmento"] = agg.apply(_classificar_segmento, axis=1)
    return agg


def _classificar_segmento(row: pd.Series) -> str:
    r, f, m = row["R"], row["F"], row["M"]
    if r >= 4 and f >= 4 and m >= 4: return "Campeões"
    if r >= 3 and f >= 3 and m >= 3: return "Leais"
    if r >= 4 and f <= 2: return "Novos"
    if r >= 3 and f <= 2 and m <= 2: return "Promissores"
    if r >= 3 and f >= 3 and m <= 2: return "Potenciais"
    if r <= 2 and f >= 3 and m >= 3: return "Não Posso Perder"
    if r <= 2 and f >= 3: return "Em Risco"
    if r == 2 and f <= 2: return "Atenção"
    if r <= 2 and f <= 2 and m <= 2: return "Hibernando"
    return "Perdidos"


def resumo_rfm(df_rfm: pd.DataFrame) -> pd.DataFrame:
    if df_rfm.empty:
        return pd.DataFrame(columns=["segmento", "n_clientes", "pct", "monetario_total", "monetario_medio"])
    total = len(df_rfm)
    agg = df_rfm.groupby("segmento").agg(
        n_clientes=("id_cliente", "count"),
        monetario_total=("monetario", "sum"),
        monetario_medio=("monetario", "mean"),
    ).reset_index()
    agg["pct"] = agg["n_clientes"] / total
    agg["icone"] = agg["segmento"].map(RFM_SEGMENTOS).fillna("")
    return agg.sort_values("monetario_total", ascending=False)


def cohort_retencao(vendas: pd.DataFrame) -> pd.DataFrame:
    """Heatmap de retenção: mês cohort × meses desde cohort."""
    if vendas.empty:
        return pd.DataFrame()
    df = vendas.copy()
    df["mes_venda"] = df["data_venda"].dt.to_period("M")
    primeira = df.groupby("id_cliente")["mes_venda"].min().rename("mes_cohort")
    df = df.merge(primeira, on="id_cliente")
    df["meses_desde"] = (df["mes_venda"] - df["mes_cohort"]).apply(lambda x: x.n)

    cohort_size = df.groupby("mes_cohort")["id_cliente"].nunique()
    retidos = df.groupby(["mes_cohort", "meses_desde"])["id_cliente"].nunique().unstack(fill_value=0)
    pivot = retidos.divide(cohort_size, axis=0)
    pivot.index = pivot.index.astype(str)
    return pivot


def abc_clientes(vendas: pd.DataFrame, clientes: pd.DataFrame) -> pd.DataFrame:
    """Curva ABC de clientes (top 20 + classe A/B/C)."""
    if vendas.empty:
        return pd.DataFrame()
    agg = vendas.groupby("id_cliente", as_index=False)["receita"].sum().sort_values("receita", ascending=False)
    total = agg["receita"].sum()
    agg["pct_acumulado"] = agg["receita"].cumsum() / total
    agg["classe"] = agg["pct_acumulado"].apply(lambda p: "A" if p <= 0.80 else ("B" if p <= 0.95 else "C"))
    agg = agg.merge(clientes[["id_cliente", "nome_cliente", "estado"]], on="id_cliente", how="left")
    return agg


def distribuicao_geografica(vendas: pd.DataFrame, clientes: pd.DataFrame) -> pd.DataFrame:
    """Hierarquia país → estado para treemap."""
    if vendas.empty or clientes.empty:
        return pd.DataFrame()
    df = vendas.merge(clientes[["id_cliente", "estado", "pais"]], on="id_cliente", how="left")
    agg = df.groupby(["pais", "estado"], as_index=False).agg(
        receita=("receita", "sum"),
        clientes=("id_cliente", "nunique"),
    )
    return agg


def aquisicao_vs_retencao(vendas: pd.DataFrame) -> pd.DataFrame:
    """Por mês: nº de clientes novos vs recorrentes."""
    if vendas.empty:
        return pd.DataFrame()
    df = vendas.copy()
    df["mes"] = df["data_venda"].dt.to_period("M").astype(str)
    primeira = df.groupby("id_cliente")["data_venda"].min().dt.to_period("M").astype(str).rename("primeira_compra")
    df = df.merge(primeira, on="id_cliente")
    df["tipo"] = df.apply(lambda r: "Novo" if r["mes"] == r["primeira_compra"] else "Recorrente", axis=1)
    return df.groupby(["mes", "tipo"])["id_cliente"].nunique().reset_index(name="clientes")


def periodo_default(vendas: pd.DataFrame) -> Tuple[datetime, datetime]:
    """Define período padrão: últimos 90 dias a partir do dado mais recente."""
    if vendas.empty:
        hoje = datetime.now()
        return hoje - timedelta(days=90), hoje
    fim = vendas["data_venda"].max()
    inicio = fim - timedelta(days=90)
    return inicio.to_pydatetime(), fim.to_pydatetime()
