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


def periodo_default(vendas: pd.DataFrame) -> Tuple[datetime, datetime]:
    """Define período padrão: últimos 90 dias a partir do dado mais recente."""
    if vendas.empty:
        hoje = datetime.now()
        return hoje - timedelta(days=90), hoje
    fim = vendas["data_venda"].max()
    inicio = fim - timedelta(days=90)
    return inicio.to_pydatetime(), fim.to_pydatetime()
