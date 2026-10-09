from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from ..constants import COLORS
from ..exports import csv_bytes
from ..metrics import snapshot_timeline, transition_metrics
from ..ui import br_int, br_pct, empty_state, kpi_card, plotly_layout, section


def render(all_snapshots: pd.DataFrame) -> None:
    if all_snapshots.empty or all_snapshots["snapshot_date"].nunique() < 2:
        empty_state(
            "Velocidade indisponível",
            "Importe um segundo snapshot com data posterior para calcular transições de venda.",
        )
        return

    timeline = snapshot_timeline(all_snapshots)
    transitions = transition_metrics(all_snapshots)
    latest = transitions.iloc[-1]
    cols = st.columns(4)
    with cols[0]:
        kpi_card("Novas vendas", br_int(latest["new_sales"]), "Último intervalo")
    with cols[1]:
        kpi_card("Reversões", br_int(latest["reversals"]), "Último intervalo", "stock")
    with cols[2]:
        kpi_card("Vendas líquidas", br_int(latest["net_sales"]), "Novas vendas menos reversões")
    with cols[3]:
        velocity = None if pd.isna(latest["monthly_velocity"]) else int(round(latest["monthly_velocity"]))
        kpi_card("Velocidade mensal", "n.d." if velocity is None else br_int(velocity), "Normalizada para 30 dias", "consumption")

    section("Evolução do consumo", "A série usa os totais de cada snapshot; adições e remoções alteram o denominador.")
    fig = go.Figure(
        go.Scatter(
            x=timeline["snapshot_date"], y=timeline["consumption"], mode="lines+markers+text",
            text=timeline["consumption"], texttemplate="%{text:.1%}", textposition="top center",
            line={"color": COLORS["green_900"], "width": 3},
            marker={"color": COLORS["green_500"], "size": 10},
            customdata=timeline[["total", "sold", "stock"]],
            hovertemplate="%{x|%d/%m/%Y}<br>Consumo %{y:.1%}<br>Total %{customdata[0]:,.0f}<br>Vendidas %{customdata[1]:,.0f}<br>Estoque %{customdata[2]:,.0f}<extra></extra>",
        )
    )
    fig.update_yaxes(title="Consumo", tickformat=".0%", range=[0, min(1.05, max(1, timeline["consumption"].max() + .08))])
    fig.update_xaxes(title="Snapshot")
    plotly_layout(fig, height=380)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    section("Transições entre snapshots")
    fig = go.Figure()
    fig.add_bar(x=transitions["snapshot_date"], y=transitions["new_sales"], name="Novas vendas", marker_color=COLORS["green_900"])
    fig.add_bar(x=transitions["snapshot_date"], y=transitions["reversals"], name="Reversões", marker_color=COLORS["error"])
    fig.add_scatter(x=transitions["snapshot_date"], y=transitions["net_sales"], name="Vendas líquidas", mode="lines+markers", line={"color": COLORS["orange"], "width": 3})
    fig.update_layout(barmode="group")
    fig.update_yaxes(title="Unidades")
    plotly_layout(fig, height=380)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    display = transitions.rename(columns={
        "previous_date": "Data anterior", "snapshot_date": "Data atual", "days": "Dias",
        "new_sales": "Novas vendas", "reversals": "Reversões", "net_sales": "Vendas líquidas",
        "monthly_velocity": "Velocidade mensal", "consumption_change_pp": "Variação do consumo (p.p.)",
        "added_units": "Unidades adicionadas", "removed_units": "Unidades removidas",
    })
    st.dataframe(display, hide_index=True, use_container_width=True)
    st.download_button("Exportar transições em CSV", csv_bytes(transitions), file_name="transicoes_snapshots.csv", mime="text/csv")

