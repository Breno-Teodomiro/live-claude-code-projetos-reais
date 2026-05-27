"""Componente de KPI Card premium."""

from typing import Callable, Optional
import streamlit as st

from src.utils.formatters import fmt_delta_arrow


def kpi_card(
    label: str,
    valor: float,
    formatter: Callable[[float], str],
    delta: Optional[float] = None,
    delta_positivo_bom: bool = True,
    help_text: Optional[str] = None,
) -> None:
    """Renderiza um card de KPI com big number e delta colorido.

    Args:
        label: rótulo (ex: "Receita Total")
        valor: número principal a formatar
        formatter: função para formatar o valor (ex: fmt_brl_compact)
        delta: variação proporcional (-0.05, 0.124...)
        delta_positivo_bom: True → verde se delta>0; False → vermelho se delta>0
    """
    if delta is None:
        delta_str = None
        delta_color = "off"
    else:
        delta_str = fmt_delta_arrow(delta)
        if delta == 0:
            delta_color = "off"
        else:
            é_positivo = delta > 0
            é_bom = é_positivo == delta_positivo_bom
            delta_color = "normal" if é_bom else "inverse"
            # streamlit: normal=verde, inverse=vermelho

    st.metric(label=label, value=formatter(valor), delta=delta_str, delta_color=delta_color, help=help_text)
