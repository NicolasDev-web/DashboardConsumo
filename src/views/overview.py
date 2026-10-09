from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from ..constants import COLORS
from ..exports import csv_bytes
from ..metrics import floor_metrics, grouped_metrics, portfolio_kpis, stock_by_status
from ..ui import br_int, br_pct, empty_state, kpi_card, plotly_layout, section


def render(frame: pd.DataFrame, snapshot_date) -> None:
    if frame.empty:
        empty_state("Nenhuma unidade no recorte", "Remova alguns filtros para voltar a visualizar o portfólio.")
        return

    kpis = portfolio_kpis(frame)
    cols = st.columns(4)
    with cols[0]:
        kpi_card("Total de unidades", br_int(kpis["total"]), "Contagem distinta no recorte")
    with cols[1]:
        kpi_card("Vendidas", br_int(kpis["sold"]), "Status oficial igual a VENDIDO")
    with cols[2]:
        kpi_card("Estoque não vendido", br_int(kpis["stock"]), "Inclui bloqueadas, reservadas e não lançadas", "stock")
    with cols[3]:
        kpi_card("Consumo", br_pct(kpis["consumption"]), "Vendidas sobre o total filtrado", "consumption")

    section("Onde o estoque está concentrado", "Os dez maiores estoques identificam concentração, não prioridade comercial automática.")
    left, right = st.columns([1.15, 0.85], gap="large")
    enterprise = grouped_metrics(frame, "enterprise_name").nlargest(10, "stock").sort_values("stock")
    with left:
        fig = px.bar(
            enterprise,
            x="stock",
            y="enterprise_name",
            orientation="h",
            text="stock",
            labels={"stock": "Estoque não vendido", "enterprise_name": ""},
            color_discrete_sequence=[COLORS["green_900"]],
        )
        fig.update_traces(texttemplate="%{text:,.0f}", textposition="outside", cliponaxis=False)
        plotly_layout(fig, height=420, margin={"l": 12, "r": 42, "t": 16, "b": 30})
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    with right:
        status = stock_by_status(frame).head(10).sort_values("units")
        status["display_units"] = status["units"].map(br_int)
        fig = px.bar(
            status,
            x="units",
            y="status_unit_normalized",
            orientation="h",
            text="display_units",
            labels={"units": "Unidades", "status_unit_normalized": ""},
            color_discrete_sequence=[COLORS["green_700"]],
        )
        fig.update_traces(texttemplate="%{text:,.0f}", textposition="outside", cliponaxis=False)
        plotly_layout(fig, height=420, margin={"l": 12, "r": 36, "t": 16, "b": 30})
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    section("Leitura por andar", "Unidades sem andar informado permanecem nos KPIs gerais e ficam fora desta comparação.")
    floors = floor_metrics(frame)
    c1, c2 = st.columns(2, gap="large")
    with c1:
        fig = go.Figure(
            go.Bar(
                x=floors["floor"], y=floors["total"],
                marker_color=COLORS["green_900"], name="Unidades",
                hovertemplate="Andar %{x:.0f}<br>%{y:,.0f} unidades<extra></extra>",
            )
        )
        fig.update_layout(title="Quantidade de unidades")
        fig.update_xaxes(title="Andar", dtick=1)
        fig.update_yaxes(title="Unidades")
        plotly_layout(fig, height=340)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    with c2:
        floor_labels = [
            f"{value:.1%} (n={br_int(total)})" if floor >= 19 else ""
            for floor, value, total in zip(floors["floor"], floors["consumption"], floors["total"])
        ]
        fig = go.Figure(
            go.Scatter(
                x=floors["floor"], y=floors["consumption"],
                mode="lines+markers+text", text=floor_labels, textposition="top center",
                line={"color": COLORS["green_700"], "width": 3},
                marker={"color": COLORS["green_500"], "size": 8, "line": {"color": COLORS["green_900"], "width": 1}},
                customdata=floors[["total", "sold", "stock"]],
                hovertemplate="Andar %{x:.0f}<br>Consumo %{y:.1%}<br>Total %{customdata[0]:,.0f}<br>Vendidas %{customdata[1]:,.0f}<br>Estoque %{customdata[2]:,.0f}<extra></extra>",
            )
        )
        fig.update_layout(title="Consumo observado")
        fig.update_xaxes(title="Andar", dtick=1)
        fig.update_yaxes(title="Consumo", tickformat=".0%", range=[0, 1.02])
        plotly_layout(fig, height=340)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    section("Resumo por empreendimento")
    summary = grouped_metrics(frame, ["city", "enterprise_name"]).sort_values(
        ["stock", "total"], ascending=False
    )
    display = summary.rename(
        columns={
            "city": "Cidade", "enterprise_name": "Empreendimento", "total": "Total",
            "sold": "Vendidas", "stock": "Estoque não vendido", "consumption": "Consumo",
        }
    )
    display["Consumo"] = display["Consumo"] * 100
    st.dataframe(
        display,
        hide_index=True,
        use_container_width=True,
        column_config={"Consumo": st.column_config.ProgressColumn(format="%.1f%%", min_value=0, max_value=100)},
    )
    export = summary.copy()
    export.insert(0, "snapshot_date", snapshot_date)
    st.download_button(
        "Exportar resumo em CSV", csv_bytes(export),
        file_name=f"resumo_empreendimentos_{snapshot_date}.csv", mime="text/csv",
    )
