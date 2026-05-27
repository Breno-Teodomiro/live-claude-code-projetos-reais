"""Carregadores de dados com fallback CSV.

Estratégia:
- Tenta Supabase primeiro.
- Em caso de erro (sem rede, RLS bloqueando, etc.) cai para os CSVs em /arquivos.
"""

from pathlib import Path
import pandas as pd
import streamlit as st

from src.data.connection import get_supabase_client
from src.utils.constants import SCHEMA

CSV_DIR = Path(__file__).resolve().parents[2] / "arquivos"

CSV_MAP = {
    "vendas":              "vendas.csv",
    "clientes":            "clientes.csv",
    "produtos":            "produtos.csv",
    "precos_competidores": "preco_competidores.csv",
}


def _load_from_supabase(table: str) -> pd.DataFrame:
    client = get_supabase_client()
    res = client.schema(SCHEMA).table(table).select("*").execute()
    return pd.DataFrame(res.data)


def _load_from_csv(table: str) -> pd.DataFrame:
    path = CSV_DIR / CSV_MAP[table]
    return pd.read_csv(path)


@st.cache_data(ttl=300, show_spinner="Carregando dados...")
def load_table(table: str) -> pd.DataFrame:
    """Carrega uma tabela com fallback automático para CSV."""
    try:
        df = _load_from_supabase(table)
        if df.empty:
            raise ValueError("Supabase retornou vazio (provável bloqueio de RLS).")
        source = "supabase"
    except Exception as e:
        df = _load_from_csv(table)
        source = f"csv (fallback: {type(e).__name__})"
    df.attrs["source"] = source
    df.attrs["table"] = table
    return df


def load_vendas() -> pd.DataFrame:
    df = load_table("vendas").copy()
    df["data_venda"] = pd.to_datetime(df["data_venda"], utc=True, errors="coerce")
    df["receita"] = df["quantidade"] * df["preco_unitario"]
    return df


def load_clientes() -> pd.DataFrame:
    df = load_table("clientes").copy()
    df["data_cadastro"] = pd.to_datetime(df["data_cadastro"], utc=True, errors="coerce")
    return df


def load_produtos() -> pd.DataFrame:
    return load_table("produtos").copy()


def load_precos_competidores() -> pd.DataFrame:
    df = load_table("precos_competidores").copy()
    df["data_coleta"] = pd.to_datetime(df["data_coleta"], utc=True, errors="coerce")
    return df
