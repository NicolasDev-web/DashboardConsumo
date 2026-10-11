from __future__ import annotations

import html

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from ..constants import COLORS, STATUS_GROUP_ORDER, STATUS_GROUPS
from ..exports import csv_bytes
from ..metrics import floor_metrics, portfolio_kpis, stock_by_group
from ..ui import br_int, br_pct, br_pp, empty_state, insight, plotly_layout, section, sorted_unique, strong, summary_strip
from .common import enterprise_picker, stock_composition


def _headline(name: str, kpis: dict, baseline: float, baseline_label: str, groups: pd.Series) -> None:
    if not kpis["stock"]:
        insight(f"{strong(name)} está {strong('100% vendido')}.", tone="positive")
        return
    rate = kpis["consumption"]
    headline = f"{strong(name)} está {strong(br_pct(rate))} vendido, {html.escape(br_pp(rate - baseline))} {html.escape(baseline_label)}."
    parts = [f"{br_int(units)} {group.lower()}" for group, units in groups.items() if units]
    detail = f"Restam {html.escape(br_int(kpis['stock']))} unidades: {html.escape(', '.join(parts))}."
    tone = "attention" if rate < 0.5 else ("positive" if rate >= 0.95 else "")
    insight(headline, detail, tone)


def _floor_chart(enterprise: pd.DataFrame, display_metric: str) -> None:
    floors = floor_metrics(enterprise)
    if floors.empty:
        st.caption("As unidades deste recorte não têm andar informado.")
        return

    metric_column = {
        "Ainda não vendidas": "stock",
        "Unidades vendidas": "sold",
        "Percentual vendido": "consumption",
    }[display_metric]
    floors = floors.sort_values(
        [metric_column, "consumption", "floor"],
        ascending=[False, False, True],
    ).reset_index(drop=True)

    if metric_column == "stock":
        colors = [COLORS["orange"]] * len(floors)
        labels = [
            f"{br_int(row.stock)} não vendidas · {br_int(row.sold)} vendidas · total {br_int(row.total)} · {br_pct(row.consumption, 0)}"
            for row in floors.itertuples()
        ]
        x_values = floors["stock"]
        axis_title = "Unidades ainda não vendidas"
        x_range = [0, max(1, float(floors["stock"].max())) * 2.25]
    elif metric_column == "sold":
        colors = [COLORS["green_900"]] * len(floors)
        labels = [
            f"{br_int(row.sold)} vendidas · total {br_int(row.total)} · {br_pct(row.consumption, 0)}"
            for row in floors.itertuples()
        ]
        x_values = floors["sold"]
        axis_title = "Unidades vendidas"
        x_range = [0, max(1, float(floors["sold"].max())) * 1.75]
    else:
        colors = [COLORS["green_700"]] * len(floors)
        labels = [
            f"{br_int(row.sold)} vendidas · total {br_int(row.total)} · {br_pct(row.consumption, 0)}"
            for row in floors.itertuples()
        ]
        x_values = floors["consumption"]
        axis_title = "Percentual vendido"
        x_range = [0, 1.5]

    fig = go.Figure(
        go.Bar(
            x=x_values,
            y=[f"{int(value)}º andar" for value in floors["floor"]],
            orientation="h",
            marker_color=colors,
            text=labels,
            textposition="outside",
            cliponaxis=False,
            customdata=floors[["sold", "stock", "total", "consumption"]],
            hovertemplate=(
                "%{y}<br>%{customdata[0]:,.0f} unidades vendidas"
                "<br>%{customdata[1]:,.0f} ainda não vendidas"
                "<br>%{customdata[2]:,.0f} unidades no total"
                "<br>%{customdata[3]:.1%} vendido<extra></extra>"
            ),
        )
    )
    if metric_column == "consumption":
        fig.update_xaxes(title=axis_title, range=x_range, tickformat=".0%")
    else:
        fig.update_xaxes(title=axis_title, range=x_range, rangemode="tozero")
    fig.update_yaxes(title="", autorange="reversed", automargin=True)
    plotly_layout(
        fig,
        height=max(330, len(floors) * 42 + 80),
        margin={"l": 12, "r": 250, "t": 12, "b": 42},
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def _floor_highlights(enterprise: pd.DataFrame) -> None:
    floors = floor_metrics(enterprise)
    if floors.empty:
        return
    most_stock = floors.sort_values(["stock", "floor"], ascending=[False, True]).iloc[0]
    least_sold = floors.sort_values(["consumption", "floor"], ascending=[True, True]).iloc[0]
    stock_total = int(floors["stock"].sum())
    stock_share = most_stock["stock"] / stock_total if stock_total else 0
    st.markdown(
        "<div class='mrv-performance'>"
        "<div><h4>Mais unidades não vendidas</h4><ol><li>"
        f"<span>{int(most_stock['floor'])}º andar</span>"
        f"<strong>{br_int(most_stock['stock'])} não vendidas · {br_pct(stock_share, 0)} do estoque</strong>"
        "</li></ol></div>"
        "<div><h4>Menor percentual vendido</h4><ol><li>"
        f"<span>{int(least_sold['floor'])}º andar</span>"
        f"<strong>{br_int(least_sold['sold'])} vendidas · total {br_int(least_sold['total'])} · {br_pct(least_sold['consumption'], 0)}</strong>"
        "</li></ol></div>"
        "</div>",
        unsafe_allow_html=True,
    )


def _unit_tables(enterprise: pd.DataFrame, snapshot_date) -> None:
    columns = {
        "block_name": "Bloco", "unit_name": "Unidade", "floor": "Andar", "typology": "Tipologia",
        "status_unit_normalized": "Status",
    }
    unsold = enterprise.loc[~enterprise["is_sold"]].copy()
    if not unsold.empty:
        section("Unidades não vendidas", "Ordenadas pelas que podem ser vendidas agora.")
        unsold["Situação"] = unsold["status_unit_normalized"].map(STATUS_GROUPS).fillna(STATUS_GROUP_ORDER[-1])
        unsold["_order"] = unsold["Situação"].map({group: index for index, group in enumerate(STATUS_GROUP_ORDER)})
        unsold = unsold.sort_values(["_order", "block_name", "floor", "unit_name"])
        display = unsold[["Situação", *columns]].rename(columns=columns)
        st.dataframe(display, hide_index=True, use_container_width=True, height=min(420, 40 + len(display) * 35))

    with st.expander(f"Ver todas as unidades ({br_int(len(enterprise))}) e exportar"):
        detail = enterprise[["city", "enterprise_name", *columns, "subtypology", "is_sold"]].copy()
        display = detail[[*columns, "is_sold"]].rename(columns={**columns, "is_sold": "Vendida"})
        st.dataframe(display, hide_index=True, use_container_width=True)
        detail.insert(0, "snapshot_date", snapshot_date)
        st.download_button("Exportar unidades em CSV", csv_bytes(detail), file_name=f"unidades_{snapshot_date}.csv", mime="text/csv")


def render(frame: pd.DataFrame, snapshot_date, baseline_label: str = "média geral") -> None:
    enterprises = sorted_unique(frame["enterprise_name"])
    if not enterprises:
        empty_state("Nenhum empreendimento disponível", "Ajuste os filtros para selecionar um empreendimento.")
        return

    pick, blocks_col = st.columns([2, 1])
    with pick:
        selected = enterprise_picker(enterprises, key="enterprise_detail")
    enterprise = frame.loc[frame["enterprise_name"].eq(selected)].copy()
    with blocks_col:
        selected_blocks = st.multiselect(
            "Blocos (opcional)", sorted_unique(enterprise["block_name"]), key="enterprise_blocks", placeholder="Todos"
        )
    if selected_blocks:
        enterprise = enterprise.loc[enterprise["block_name"].isin(selected_blocks)]
    if enterprise.empty:
        empty_state("Sem unidades nesse recorte", "Remova o filtro de bloco para continuar.")
        return

    kpis = portfolio_kpis(enterprise)
    baseline = portfolio_kpis(frame)["consumption"]
    groups = stock_by_group(enterprise).set_index("group")["units"]
    _headline(selected, kpis, baseline, baseline_label, groups)

    floors = floor_metrics(enterprise)
    most_stock = floors.sort_values(["stock", "floor"], ascending=[False, True]).iloc[0] if not floors.empty else None
    least_sold = floors.sort_values(["consumption", "floor"], ascending=[True, True]).iloc[0] if not floors.empty else None
    summary_items = [
        (f"{br_int(kpis['sold'])} vendidas", f"de {br_int(kpis['total'])} unidades"),
        (f"{br_int(kpis['stock'])} não vendidas", f"{br_int(groups.get('Em comercialização', 0))} em comercialização"),
        (br_pct(kpis["consumption"]), "percentual vendido"),
    ]
    if most_stock is not None and least_sold is not None:
        summary_items.append(
            (
                f"{int(most_stock['floor'])}º andar",
                f"mais estoque · {br_int(most_stock['stock'])} unidades",
            )
        )
    summary_strip(summary_items)

    if kpis["stock"]:
        section(
            "Vendas e estoque por andar",
            "Compare números absolutos e percentual. Cada barra mostra vendidas, não vendidas e total do andar.",
        )
        display_metric = st.segmented_control(
            "Comparar por",
            ["Ainda não vendidas", "Unidades vendidas", "Percentual vendido"],
            default="Ainda não vendidas",
            key="enterprise_floor_metric",
        ) or "Ainda não vendidas"
        left, right = st.columns([0.72, 0.28], gap="large")
        with left:
            _floor_chart(enterprise, display_metric)
        with right:
            _floor_highlights(enterprise)

        with st.expander("Entender os status das unidades não vendidas"):
            stock_composition(enterprise)

    _unit_tables(enterprise, snapshot_date)
