"""Formatadores brasileiros (R$, %, datas, números compactos)."""

from datetime import date, datetime
from typing import Union

Number = Union[int, float]

MESES_PT = [
    "jan.", "fev.", "mar.", "abr.", "mai.", "jun.",
    "jul.", "ago.", "set.", "out.", "nov.", "dez.",
]


def fmt_brl(valor: Number, casas: int = 2) -> str:
    """Formata número como Real Brasileiro: R$ 1.234.567,89"""
    if valor is None:
        return "R$ 0,00"
    s = f"{valor:,.{casas}f}"
    s = s.replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {s}"


def fmt_brl_compact(valor: Number) -> str:
    """Formata compacto: R$ 1,2M / R$ 234K"""
    if valor is None:
        return "R$ 0"
    v = float(valor)
    if abs(v) >= 1_000_000_000:
        return f"R$ {v/1_000_000_000:.1f}".replace(".", ",") + "B"
    if abs(v) >= 1_000_000:
        return f"R$ {v/1_000_000:.1f}".replace(".", ",") + "M"
    if abs(v) >= 1_000:
        return f"R$ {v/1_000:.1f}".replace(".", ",") + "K"
    return fmt_brl(v, 0)


def fmt_int(valor: Number) -> str:
    if valor is None:
        return "0"
    return f"{int(valor):,}".replace(",", ".")


def fmt_pct(valor: Number, casas: int = 1, com_sinal: bool = False) -> str:
    """0.124 -> '12,4%'"""
    if valor is None:
        return "0,0%"
    pct = valor * 100
    s = f"{pct:.{casas}f}".replace(".", ",")
    if com_sinal and pct > 0:
        s = f"+{s}"
    return f"{s}%"


def fmt_delta_arrow(valor: Number, casas: int = 1) -> str:
    """0.124 -> '▲ 12,4%' / -0.05 -> '▼ 5,0%'"""
    if valor is None or valor == 0:
        return "─ 0,0%"
    arrow = "▲" if valor > 0 else "▼"
    s = f"{abs(valor)*100:.{casas}f}".replace(".", ",")
    return f"{arrow} {s}%"


def fmt_date_br(d: Union[date, datetime, str]) -> str:
    """2026-05-26 -> '26 de mai. de 2026'"""
    if isinstance(d, str):
        d = datetime.fromisoformat(d.replace("Z", "+00:00"))
    return f"{d.day:02d} de {MESES_PT[d.month - 1]} de {d.year}"


def fmt_month_year_br(d: Union[date, datetime, str]) -> str:
    if isinstance(d, str):
        d = datetime.fromisoformat(d.replace("Z", "+00:00"))
    return f"{MESES_PT[d.month - 1]}/{d.year}"
