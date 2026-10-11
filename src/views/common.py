from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from ..constants import COLORS, STATUS_GROUP_HELP
from ..metrics import stock_by_group, stock_by_status
from ..ui import br_int, plotly_layout, share_bars


GROUP_COLORS = {
    "Em comercialização": COLORS["green_900"],
    "Reservadas": COLORS["green_500"],
    "Fora de venda": COLORS["stock"],
    "Outros status": COLORS["orange"],
}


def stock_composition(frame: pd.DataFrame) -> pd.DataFrame:
    """Mostra o que é o estoque em três grupos e deixa o status bruto em detalhes."""

    groups = stock_by_group(frame)
    share_bars(
        [
            {
                "label": row.group,
                "value": row.units,
                "share": row.share,
                "color": GROUP_COLORS[row.group],
                "help": STATUS_GROUP_HELP[row.group],
            }
            for row in groups.itertuples()
        ]
    )
    with st.expander("Ver estoque por status oficial"):
        status = stock_by_status(frame).sort_values("units")
        status["label"] = status["units"].map(br_int)
        fig = px.bar(
            status,
            x="units",
            y="status_unit_normalized",
            orientation="h",
            text="label",
            labels={"units": "Unidades", "status_unit_normalized": ""},
            color_discrete_sequence=[COLORS["green_700"]],
        )
        fig.update_traces(textposition="outside", cliponaxis=False, hovertemplate="%{y}<br>%{x:,.0f} unidades<extra></extra>")
        plotly_layout(fig, height=max(240, len(status) * 36 + 70), margin={"l": 12, "r": 48, "t": 8, "b": 24})
        fig.update_xaxes(visible=False)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    return groups


def enterprise_picker(options: list[str], key: str, allow_empty: bool = False) -> str | None:
    """Seletor de empreendimento que lembra a escolha entre as telas."""

    current = st.session_state.get("current_enterprise")
    kwargs: dict = {}
    if key not in st.session_state and current in options:
        st.session_state[key] = current
    elif key not in st.session_state:
        kwargs["index"] = None if allow_empty else 0
    choice = st.selectbox(
        "Empreendimento",
        options,
        placeholder="Digite para buscar um empreendimento",
        key=key,
        **kwargs,
    )
    if choice:
        st.session_state["current_enterprise"] = choice
    return choice
