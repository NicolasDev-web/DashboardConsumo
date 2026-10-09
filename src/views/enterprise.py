from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from ..constants import COLORS
from ..exports import csv_bytes
from ..metrics import floor_metrics, portfolio_kpis, stock_by_status
from ..ui import br_int, br_pct, empty_state, kpi_card, plotly_layout, section, sorted_unique


def render(frame: pd.DataFrame, snapshot_date) -> None:
    enterprises = sorted_unique(frame["enterprise_name"])
    if not enterprises:
        empty_state("Nenhum empreendimento disponível", "Ajuste os filtros globais para selecionar um empreendimento.")
        return

    selected = st.selectbox("Empreendimento", enterprises, key="enterprise_detail")
    enterprise = frame.loc[frame["enterprise_name"].eq(selected)].copy()
    blocks = sorted_unique(enterprise["block_name"])
    selected_blocks = st.multiselect("Bloco (opcional)", blocks, key="enterprise_blocks", placeholder="Selecione")
    if selected_blocks:
        enterprise = enterprise.loc[enterprise["block_name"].isin(selected_blocks)]

    if enterprise.empty:
        empty_state("Sem unidades nesse recorte", "Remova o filtro de bloco para continuar.")
        return

    kpis = portfolio_kpis(enterprise)
    cols = st.columns(4)
    with cols[0]:
        kpi_card("Unidades", br_int(kpis["total"]), selected)
    with cols[1]:
        kpi_card("Vendidas", br_int(kpis["sold"]), "Status oficial")
    with cols[2]:
        kpi_card("Estoque não vendido", br_int(kpis["stock"]), "Todos os demais status", "stock")
    with cols[3]:
        kpi_card("Consumo", br_pct(kpis["consumption"]), "Vendidas sobre total", "consumption")

    floors = floor_metrics(enterprise)
    section("Distribuição por andar", "Volume e taxa de consumo aparecem em gráficos separados para evitar eixo duplo.")
    c1, c2 = st.columns(2, gap="large")
    with c1:
        fig = go.Figure()
        fig.add_bar(x=floors["floor"], y=floors["sold"], name="Vendidas", marker_color=COLORS["green_900"])
        fig.add_bar(x=floors["floor"], y=floors["stock"], name="Não vendidas", marker_color=COLORS["stock"])
        fig.update_layout(barmode="stack", title="Unidades por andar")
        fig.update_xaxes(title="Andar", dtick=1)
        fig.update_yaxes(title="Unidades")
        plotly_layout(fig, height=360)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    with c2:
        fig = go.Figure(
            go.Bar(
                x=floors["floor"], y=floors["consumption"], marker_color=COLORS["green_700"],
                text=floors["consumption"], texttemplate="%{text:.1%}", textposition="outside",
                customdata=floors["total"],
                hovertemplate="Andar %{x:.0f}<br>Consumo %{y:.1%}<br>Amostra %{customdata:,.0f}<extra></extra>",
            )
        )
        fig.update_layout(title="Consumo por andar")
        fig.update_xaxes(title="Andar", dtick=1)
        fig.update_yaxes(title="Consumo", tickformat=".0%", range=[0, 1.08])
        plotly_layout(fig, height=360)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    section("Composição do estoque")
    status = stock_by_status(enterprise)
    if status.empty:
        st.success("Todas as unidades do recorte estão vendidas.")
    else:
        fig = px.bar(
            status.sort_values("units"), x="units", y="status_unit_normalized", orientation="h",
            text="units", color_discrete_sequence=[COLORS["green_700"]],
            labels={"units": "Unidades", "status_unit_normalized": ""},
        )
        fig.update_traces(textposition="outside", cliponaxis=False)
        plotly_layout(fig, height=max(280, len(status) * 42 + 90), margin={"l": 12, "r": 34, "t": 16, "b": 30})
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    section("Unidades do recorte")
    detail = enterprise[[
        "city", "enterprise_name", "block_name", "unit_name", "floor", "typology",
        "subtypology", "status_unit_normalized", "is_sold",
    ]].copy()
    display = detail.rename(columns={
        "city": "Cidade", "enterprise_name": "Empreendimento", "block_name": "Bloco",
        "unit_name": "Unidade", "floor": "Andar", "typology": "Tipologia",
        "subtypology": "Subtipologia", "status_unit_normalized": "Status", "is_sold": "Vendida",
    })
    st.dataframe(display, hide_index=True, use_container_width=True)
    detail.insert(0, "snapshot_date", snapshot_date)
    st.download_button("Exportar unidades em CSV", csv_bytes(detail), file_name=f"unidades_{snapshot_date}.csv", mime="text/csv")
